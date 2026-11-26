import {request} from './api.js';
import {el} from './dom.js';

export async function latestWindow(root) {
  const estimates = await request('/lead_windows');
  if (!estimates.length) return;
  const row = estimates.at(-1);
  const result = row.evidence;
  root.querySelector('.title').after(el('section',{class:'range-ribbon','aria-label':'最近的工期分位区间'},
    el('h2',{},row.code+' · '+row.piece),
    el('div',{class:'range-track'},el('span',{},'P20 '+row.lower_days+' 天'),el('i',{'aria-hidden':'true'}),
       el('span',{},'P80 '+row.upper_days+' 天')),
    el('p',{},`留出 ${result.held_rows} 票，覆盖 ${(row.coverage*100).toFixed(1)}%，P20/P80 损失 ${result.p20_pinball} / ${result.p80_pinball} 天`)));
}
