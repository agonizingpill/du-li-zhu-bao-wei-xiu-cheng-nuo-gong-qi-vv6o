        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "金工工序与见证",
  "module": "工序与双见证",
  "caption": "工序与双见证",
  "detail": "贵重石拆装工序需两名能登录的工作人员看同一封签，重复账号无效。",
  "path": "/bench_steps",
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
      "name": "operation",
      "label": "工序"
    },
    {
      "name": "minutes",
      "label": "工台分钟"
    },
    {
      "name": "first_witness",
      "label": "第一见证"
    },
    {
      "name": "second_witness",
      "label": "第二见证"
    }
  ],
  "layout": "flip",
  "view": "grid",
  "actions": [
    {
      "name": "add_operation",
      "label": "登记下一道工序",
      "path": "/bench_steps/add-operation",
      "fields": [
        {
          "name": "code",
          "label": "工序编号",
          "kind": "text",
          "initial": "OP-011"
        },
        {
          "name": "piece",
          "label": "饰件编号",
          "kind": "text",
          "initial": "JW-011"
        },
        {
          "name": "operation",
          "label": "工序名",
          "kind": "text",
          "initial": "整形"
        },
        {
          "name": "minutes",
          "label": "分钟",
          "kind": "int",
          "initial": 30
        }
      ],
      "help": "可登记整形、抛光或镶石拆装。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "witness_stone",
      "label": "见证贵重石拆装",
      "path": "/bench_steps/witness-stone",
      "fields": [
        {
          "name": "task",
          "label": "工序编号",
          "kind": "text",
          "initial": "OP-001"
        },
        {
          "name": "seal",
          "label": "复见收件封签",
          "kind": "text",
          "initial": "BAG-892A"
        }
      ],
      "help": "签名必须来自不同账号并使用同一收件封签。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "bench_steps";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
