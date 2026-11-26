        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "封袋签收",
  "module": "饰件签收",
  "caption": "饰件签收",
  "detail": "封签和饰件一一对应，维修承诺票在最后一站生成。",
  "path": "/pieces",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "description",
      "label": "封袋明细"
    },
    {
      "name": "mass_g",
      "label": "总重（g）"
    },
    {
      "name": "stone_count",
      "label": "贵重石数"
    },
    {
      "name": "seal",
      "label": "收件封签"
    },
    {
      "name": "arrived",
      "label": "签收日"
    }
  ],
  "layout": "split",
  "view": "stack",
  "actions": [
    {
      "name": "receive",
      "label": "签收新饰件",
      "path": "/pieces/receive",
      "fields": [
        {
          "name": "code",
          "label": "饰件编号",
          "kind": "text",
          "initial": "JW-011"
        },
        {
          "name": "description",
          "label": "封袋明细",
          "kind": "text",
          "initial": "14K 耳饰扣 · 偏斜"
        },
        {
          "name": "mass_g",
          "label": "饰件总重（克）",
          "kind": "float",
          "initial": 7.4
        },
        {
          "name": "stone_count",
          "label": "贵重石数量",
          "kind": "int",
          "initial": 0
        },
        {
          "name": "seal",
          "label": "新封签",
          "kind": "text",
          "initial": "BAG-914J"
        },
        {
          "name": "arrived",
          "label": "签收日期",
          "kind": "text",
          "initial": "2026-11-24"
        }
      ],
      "help": "记录客户实物入袋和贵重石数量。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "pieces";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
