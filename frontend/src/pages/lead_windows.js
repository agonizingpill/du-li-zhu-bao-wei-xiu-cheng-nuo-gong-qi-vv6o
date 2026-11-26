import {latestWindow} from '../range-ribbon.js';
        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "工期分位与留出证据",
  "module": "工期区间",
  "caption": "工期区间",
  "detail": "保存 P20 与 P80 承诺区间，并把估算绑定到当前工序快照。",
  "path": "/lead_windows",
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
      "name": "backlog",
      "label": "当前排队单数"
    },
    {
      "name": "signature",
      "label": "工序快照"
    },
    {
      "name": "lower_days",
      "label": "P20 日数"
    },
    {
      "name": "upper_days",
      "label": "P80 日数"
    },
    {
      "name": "coverage",
      "label": "留出覆盖"
    },
    {
      "name": "evidence",
      "label": "模型计算"
    }
  ],
  "layout": "stack",
  "view": "table",
  "actions": [
    {
      "name": "fit_window",
      "label": "按当前工序估算",
      "path": "/lead_windows/fit-window",
      "fields": [
        {
          "name": "piece",
          "label": "饰件编号",
          "kind": "text",
          "initial": "JW-001"
        },
        {
          "name": "backlog",
          "label": "当前排队单数",
          "kind": "int",
          "initial": 6
        }
      ],
      "help": "估算使用已有工序，不会签出承诺。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "save_window",
      "label": "归档工期区间",
      "path": "/lead_windows/save-window",
      "fields": [
        {
          "name": "code",
          "label": "估算编号",
          "kind": "text",
          "initial": "EST-001"
        },
        {
          "name": "token",
          "label": "回归任务编号",
          "kind": "token",
          "initial": ""
        }
      ],
      "help": "填写计算令牌，留出证据会随区间归档。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "lead_windows";
        export async function render(root, role) {
          await workspace(root, role, page);
  await latestWindow(root);

        }
