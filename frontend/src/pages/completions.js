        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "实际完工与分档校准",
  "module": "完工校准",
  "caption": "完工记录",
  "detail": "柜台补录实际完工日后，按签票时的排队档重新校准上限；只认每件饰件最后一张票。",
  "path": "/completions",
  "columns": [
    {
      "name": "code",
      "label": "记录编号"
    },
    {
      "name": "piece",
      "label": "饰件编号"
    },
    {
      "name": "ticket",
      "label": "承诺票"
    },
    {
      "name": "completed_day",
      "label": "实际完工日"
    },
    {
      "name": "recorded_at",
      "label": "落账时间"
    }
  ],
  "layout": "stack",
  "view": "table",
  "actions": [
    {
      "name": "record_completion",
      "label": "补录或更正完工日",
      "path": "/completions/record",
      "fields": [
        {
          "name": "code",
          "label": "记录编号（留空自动）",
          "kind": "text",
          "initial": ""
        },
        {
          "name": "piece",
          "label": "饰件编号",
          "kind": "text",
          "initial": "JW-001"
        },
        {
          "name": "ticket",
          "label": "承诺票（留空取最后一张）",
          "kind": "text",
          "initial": ""
        },
        {
          "name": "completed_day",
          "label": "实际完工日",
          "kind": "text",
          "initial": "2026-12-02"
        }
      ],
      "help": "同编号再次提交即为更正；补录与更正都会作废本档排队中的估算，并重算本档未签估算。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已落账"
    }
  ]
};

        export const {title} = page;
        export const key = "completions";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
