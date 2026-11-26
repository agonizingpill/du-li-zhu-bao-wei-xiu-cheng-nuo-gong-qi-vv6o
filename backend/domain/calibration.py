"""完工日校准：只依赖标准库，便于在 worker 与 API 两侧复用。

校准思路
--------
1. 每件饰件只取最后一张承诺票；该票所用估算里的排队单数决定分档。
2. 同一分档内，完工记录按实际完工日排序，早期记录用来校准上限，
   后期记录用来比较新旧上限的超期率与 P80 分位损失。
3. 新上限 = 原模型上限 + 早期残差（实际天数 - 原上限）的 P80 分位，向上取整。
4. 样本不足，或超期率、分位损失任一指标变差，就沿用原估算（偏移 0 天）。
"""

from hashlib import sha256
from math import ceil, floor
import json

# 排队量分档：0–5、6–11、12–17、18–24。签票时排队量落在哪档就用哪档校准。
BANDS = ((0, 5), (6, 11), (12, 17), (18, 24))
TARGET_QUANTILE = 0.8

MIN_CALIBRATION_ROWS = 4
MIN_VALIDATION_ROWS = 3

EPSILON = 1e-9


def band_of(backlog):
    value = int(backlog)
    for low, high in BANDS:
        if low <= value <= high:
            return f'B{low}-{high}'
    return f'B{BANDS[-1][0]}-{BANDS[-1][1]}'


def quantile(values, q):
    """线性插值分位数，与 numpy.quantile 的默认口径一致。"""
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    position = q * (len(ordered) - 1)
    low, high = int(floor(position)), int(ceil(position))
    if low == high:
        return ordered[low]
    fraction = position - low
    return ordered[low] * (1 - fraction) + ordered[high] * fraction


def pinball_loss(actual, bound, q=TARGET_QUANTILE):
    """P80 分位损失：越低越好。"""
    if actual >= bound:
        return q * (actual - bound)
    return (1 - q) * (bound - actual)


def overrun(actual, bound):
    return actual > bound


def _fingerprint(bucket, samples):
    payload = [[s['piece'], s['ticket'], s['completed_day'], int(s['duration']), int(s['raw_upper_days'])]
               for s in sorted(samples, key=lambda s: (s['piece'], s['ticket']))]
    return sha256(json.dumps([bucket, payload], ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def build(bucket, samples):
    """为单一排队档生成校准快照。

    samples 每项须含 piece、ticket、completed_day、duration、raw_upper_days。
    快照会随估算归档，也用于判断排队中的计算是否已被补录/更正作废。
    """
    ordered = sorted((dict(sample) for sample in samples),
                     key=lambda s: (s['completed_day'], s['piece'], s['ticket']))
    snapshot = {
        'bucket': bucket,
        'target_quantile': TARGET_QUANTILE,
        'sample_count': len(ordered),
        'calibration_rows': 0,
        'validation_rows': 0,
        'delta_days': 0,
        'candidate_delta_days': 0,
        'applied': False,
        'reason': '样本不足，沿用原估算',
        'key': _fingerprint(bucket, ordered),
        'old_overrun': None,
        'new_overrun': None,
        'old_pinball': None,
        'new_pinball': None,
        'samples': [dict(sample, use='unused') for sample in ordered],
    }

    if len(ordered) < MIN_CALIBRATION_ROWS + MIN_VALIDATION_ROWS:
        return snapshot

    split = max(MIN_CALIBRATION_ROWS, int(ceil(len(ordered) * 0.6)))
    split = min(split, len(ordered) - MIN_VALIDATION_ROWS)
    early, later = ordered[:split], ordered[split:]

    residuals = [sample['duration'] - sample['raw_upper_days'] for sample in early]
    delta = int(ceil(round(quantile(residuals, TARGET_QUANTILE), 9)))

    old_bounds = [sample['raw_upper_days'] for sample in later]
    new_bounds = [sample['raw_upper_days'] + delta for sample in later]
    actuals = [sample['duration'] for sample in later]

    old_overrun = _mean([1.0 if overrun(a, b) else 0.0 for a, b in zip(actuals, old_bounds)])
    new_overrun = _mean([1.0 if overrun(a, b) else 0.0 for a, b in zip(actuals, new_bounds)])
    old_pinball = _mean([pinball_loss(a, b) for a, b in zip(actuals, old_bounds)])
    new_pinball = _mean([pinball_loss(a, b) for a, b in zip(actuals, new_bounds)])

    snapshot.update(
        calibration_rows=len(early),
        validation_rows=len(later),
        candidate_delta_days=delta,
        old_overrun=round(old_overrun, 4),
        new_overrun=round(new_overrun, 4),
        old_pinball=round(old_pinball, 4),
        new_pinball=round(new_pinball, 4),
        samples=[dict(sample, use='calibration') for sample in early]
                + [dict(sample, use='validation') for sample in later],
    )

    if delta == 0:
        snapshot['reason'] = '残差 P80 为 0 天，沿用原估算'
        return snapshot

    if new_overrun > old_overrun + EPSILON or new_pinball > old_pinball + EPSILON:
        snapshot['reason'] = '校准后超期率或分位损失变差，沿用原估算'
        return snapshot

    snapshot['delta_days'] = delta
    snapshot['applied'] = True
    snapshot['reason'] = '校准通过'
    return snapshot
