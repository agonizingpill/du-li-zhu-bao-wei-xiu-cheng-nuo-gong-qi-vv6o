import {benchCalendar} from '../bench-calendar.js';
import {ticketTraces} from '../ticket-traces.js';
        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "承诺票与工台日程",
  "module": "客户承诺票",
  "caption": "客户承诺票",
  "detail": "客户承诺票锁定独占工台日期。重排只有在新窗口合规时才替换旧票。",
  "path": "/promise_tickets",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "piece",
      "label": "饰件编号"
    },
    {
      "name": "estimate",
      "label": "换算凭证"
    },
    {
      "name": "bench",
      "label": "工台"
    },
    {
      "name": "start_day",
      "label": "开工日"
    },
    {
      "name": "end_day",
      "label": "承诺最晚日"
    },
    {
      "name": "state",
      "label": "状态"
    },
    {
      "name": "previous",
      "label": "上一张票"
    },
    {
      "name": "reason",
      "label": "修订原因"
    }
  ],
  "layout": "split",
  "view": "table",
  "actions": [
    {
      "name": "issue_ticket",
      "label": "签出首次承诺",
      "path": "/promise_tickets/issue-ticket",
      "fields": [
        {
          "name": "code",
          "label": "承诺票编号",
          "kind": "text",
          "initial": "CARD-001"
        },
        {
          "name": "estimate",
          "label": "工期区间编号",
          "kind": "text",
          "initial": "EST-001"
        },
        {
          "name": "bench",
          "label": "工台编号",
          "kind": "text",
          "initial": "BENCH-A"
        },
        {
          "name": "start_day",
          "label": "开工日",
          "kind": "text",
          "initial": "2026-11-25"
        }
      ],
      "help": "签发需确认工序双见证、工台可排和区间 freshness。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "revise_ticket",
      "label": "重排并保留旧票",
      "path": "/promise_tickets/revise-ticket",
      "fields": [
        {
          "name": "code",
          "label": "承诺票编号",
          "kind": "text",
          "initial": "CARD-001"
        },
        {
          "name": "estimate",
          "label": "工期区间编号",
          "kind": "text",
          "initial": "EST-001"
        },
        {
          "name": "bench",
          "label": "工台编号",
          "kind": "text",
          "initial": "BENCH-A"
        },
        {
          "name": "start_day",
          "label": "开工日",
          "kind": "text",
          "initial": "2026-11-25"
        },
        {
          "name": "previous",
          "label": "原现行承诺票编号",
          "kind": "text",
          "initial": "CARD-001"
        },
        {
          "name": "reason",
          "label": "重排原因",
          "kind": "text",
          "initial": "顾客将原取件日程推迟"
        }
      ],
      "help": "引用现行票和新估算凭证，同时记录重排原因。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "promise_tickets";
        export async function render(root, role) {
          await workspace(root, role, page);
  await benchCalendar(root);
  await ticketTraces(root);

        }
