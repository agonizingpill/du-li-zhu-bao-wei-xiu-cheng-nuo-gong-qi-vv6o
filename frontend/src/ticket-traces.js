import {request} from './api.js';
import {el, display} from './dom.js';

const metric = value => value === null || value === undefined ? '—' : (Number(value) * 100).toFixed(1) + '%';

export async function ticketTraces(root) {
  const traces = await request('/promise_tickets/traces');
  if (!traces.length) return;
  const section = el('section', {class:'ticket-traces', 'aria-label':'承诺票签发依据'},
    el('h2', {}, '签发时的样本与上限'));
  for (const trace of traces) {
    const rows = (trace.samples || []).map(sample => el('tr', {},
      el('td', {}, sample.piece), el('td', {}, sample.ticket), el('td', {}, sample.completed_day),
      el('td', {}, sample.duration + ' 天'), el('td', {}, sample.raw_upper_days + ' 天'),
      el('td', {}, sample.use === 'calibration' ? '校准' : sample.use === 'validation' ? '比较' : '未用')));
    section.append(el('article', {class:'trace' + (trace.state === '现行' ? ' active' : '')},
      el('h3', {}, `${trace.ticket} · ${trace.piece} · ${trace.bench}`),
      el('p', {class:'trace-meta'}, `${trace.state} · 开工 ${trace.start_day} · 承诺最晚 ${trace.end_day}`),
      el('p', {}, `分档 ${trace.bucket} · 原上限 ${trace.raw_upper_days} 天 · 校准 ${trace.delta_days >= 0 ? '+' : ''}${trace.delta_days} 天 · 采用 ${trace.upper_days} 天`),
      el('p', {class:'trace-verdict'}, `样本 ${trace.sample_count} 条（校准 ${trace.calibration_rows} / 比较 ${trace.validation_rows}）· ${trace.reason}`),
      el('p', {}, `比较段超期率 ${metric(trace.old_overrun)} → ${metric(trace.new_overrun)}，P80 分位损失 ${display(trace.old_pinball)} → ${display(trace.new_pinball)}`),
      rows.length ? el('div', {class:'scroll'}, el('table', {},
        el('thead', {}, el('tr', {}, ['饰件', '票', '完工日', '实际', '原上限', '用途'].map(x => el('th', {scope:'col'}, x)))),
        el('tbody', {}, rows))) : el('p', {class:'trace-empty'}, '本档暂无完工样本，沿用原估算。')));
  }
  root.querySelector('.title').after(section);
}
