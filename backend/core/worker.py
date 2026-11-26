from pathlib import Path
from traceback import print_exc
import json

from redis.exceptions import WatchError

from core.db import transaction
from core.queueing import QUEUE, broker
from domain.completion_service import finalize
from domain.learning import calculate

pulse = Path('/tmp/compute-heartbeat')


def store(token, payload):
    """只有当前仍是排队中的任务才写入终态，避免覆盖并发写入的失效标记。"""
    key = f'compute:{token}'
    encoded = json.dumps(payload, allow_nan=False)
    while True:
        try:
            with broker.pipeline() as pipe:
                pipe.watch(key)
                raw = pipe.get(key)
                if raw is not None and json.loads(raw).get('status') == 'stale':
                    pipe.unwatch()
                    return False
                pipe.multi()
                pipe.set(key, encoded, ex=86400)
                pipe.execute()
                return True
        except WatchError:
            continue


def process(job):
    try:
        model = calculate(job['input'])
        with transaction() as conn:
            evidence, stale = finalize(conn, job['input'], model)
    except ValueError as exc:
        return {'status': 'rejected', 'detail': str(exc)}
    except Exception:
        print_exc()
        return {'status': 'rejected', 'detail': '计算失败，请检查输入和 worker 日志'}
    if stale:
        return {'status': 'stale', 'detail': stale}
    return {'status': 'ready', 'result': evidence}


def serve():
    while True:
        broker.ping()
        pulse.touch()
        item = broker.blmove(QUEUE, f'{QUEUE}:processing', timeout=2, src='LEFT', dest='RIGHT')
        if item is None:
            continue
        job = json.loads(item)
        status = {'owner': job['owner'], 'input': job['input']}
        status.update(process(job))
        store(job['token'], status)
        with broker.pipeline() as pipe:
            pipe.lrem(f'{QUEUE}:processing', 1, item)
            pipe.execute()
        pulse.touch()

if __name__ == '__main__':
    for raw in broker.lrange(f'{QUEUE}:processing', 0, -1):
        with broker.pipeline() as pipe:
            pipe.lpush(QUEUE, raw)
            pipe.lrem(f'{QUEUE}:processing', 1, raw)
            pipe.execute()
    serve()
