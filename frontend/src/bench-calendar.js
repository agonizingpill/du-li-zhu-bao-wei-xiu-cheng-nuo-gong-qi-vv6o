import {request} from './api.js';
import {el} from './dom.js';

function isoDates(start, end) {
  const values = [];
  let day = new Date(start + 'T12:00:00Z');
  const last = new Date(end + 'T12:00:00Z');
  while (day <= last && values.length < 31) {
    values.push(day.toISOString().slice(0,10));
    day.setUTCDate(day.getUTCDate() + 1);
  }
  return values;
}

export async function benchCalendar(root) {
  const rows = await request('/promise_tickets');
  const active = rows.filter(row => row.state === '现行').sort((a,b) => a.start_day.localeCompare(b.start_day));
  const strip = el('section',{class:'bench-calendar','aria-label':'工台占用图'},el('h2',{},'两座工台的现行占用'));
  for (const bench of ['BENCH-A','BENCH-B']) {
    const tickets = active.filter(row => row.bench === bench);
    strip.append(el('div',{class:'bench-row'},el('h3',{},bench),
      tickets.length ? tickets.map(row => {
        const dates = isoDates(row.start_day,row.end_day);
        return el('article',{class:'ticket-block'},el('strong',{},row.code + ' · '+row.piece),
          el('p',{},row.start_day+' 至 '+row.end_day),
          el('div',{class:'occupied','aria-label':dates.length+' 天占用'},dates.map(day => el('i',{title:day,'aria-hidden':'true'}))));
      }) : el('p',{},'尚无承诺票。')));
  }
  root.querySelector('.title').after(strip);
}
