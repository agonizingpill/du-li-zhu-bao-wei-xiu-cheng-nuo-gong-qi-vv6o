# 独立珠宝维修的承诺工期

拾琢金工维修部把收件、镶石见证、取件范围和旧票重排留在同一条珠宝维修链里。

## 现场工作与联系人

模拟客户为拾琢金工维修部。饰件来料签收、镶石与抛光工艺、工期区间、客户承诺票；贵重石拆装缺双见证禁止出承诺。

- 饰件签收 `pieces`，字段为 `description`（封袋明细）、`mass_g`（总重（g））、`stone_count`（贵重石数）、`seal`（收件封签）、`arrived`（签收日）。模型约束位于 `backend/domain/pieces_model.py`，规则位于 `pieces_service.py`。
- 工序与双见证 `bench_steps`，字段为 `piece`（饰件编号）、`operation`（工序）、`minutes`（工台分钟）、`first_witness`（第一见证）、`second_witness`（第二见证）。模型约束位于 `backend/domain/bench_steps_model.py`，规则位于 `bench_steps_service.py`。
- 工期区间 `lead_windows`，字段为 `piece`（饰件编号）、`backlog`（当前排队单数）、`signature`（工序快照）、`lower_days`（P20 日数）、`upper_days`（P80 日数）、`coverage`（留出覆盖）、`evidence`（模型计算）。模型约束位于 `backend/domain/lead_windows_model.py`，规则位于 `lead_windows_service.py`。
- 客户承诺票 `promise_tickets`，字段为 `piece`（饰件编号）、`estimate`（换算凭证）、`bench`（工台）、`start_day`（开工日）、`end_day`（承诺最晚日）、`state`（状态）、`previous`（上一张票）、`reason`（修订原因）。模型约束位于 `backend/domain/promise_tickets_model.py`，规则位于 `promise_tickets_service.py`。
- 实际完工 `completions`，字段为 `code`（记录编号）、`piece`（饰件编号）、`ticket`（承诺票）、`completed_day`（实际完工日）、`recorded_at`（落账时间）。同一承诺票只留一条记录，再次提交同一编号即为更正。模型位于 `backend/domain/completion_model.py`，规则位于 `completion_service.py`，校准算式位于 `calibration.py`。

团队为模拟的7 人维修部，为门店收进的戒托等饰件安排工作台。

店员过去用纸签抄工序和预交日期。工艺复杂度靠口头转述，缺双见证时难辨能否答复，单点工期容易在返修时失效。

来料签收和同类工艺历史进入时窗估计，下游柜台用签认承诺票答复客户。

### 一天的业务操作

1. 08:45 以 BAG-892A 签收入库 5.6 克、1 颗贵重石的 JW-001。
2. 09:00 登记 85 分钟镶石拆装和 30 分钟抛光。
3. 09:30 按排队 6 单计算 P20/P80 并归档 EST-001。
4. 10:15 封签见证尚不齐备，班长无法签发第一张票。
5. 10:45 两名不同员工使用同一封签签字，班长签出 BENCH-A 的 CARD-001。
6. 11:10 尝试把素银细镯排在同工台同日期，被拒后转 BENCH-B。
7. 14:05 客户推迟取件，重算 EST-003，12 月 3 日重排成功。旧票归档，保留修订原因。

## 启动

```sh
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

打开 `http://127.0.0.1:18312`。FastAPI OpenAPI 在 `http://127.0.0.1:19312/docs`。
Compose 运行 Nginx、Python FastAPI、独立 Redis 消费进程、SQL 数据库和 Redis，SQL 与 Redis 使用命名卷。
本机开发时，在 Python 3.11 环境安装 `backend/requirements.txt` 后从 backend 目录运行 `uvicorn core.app:app`。须提供 `DATABASE_URL`、`REDIS_URL`、`JWT_SECRET`，`SEED_DEMO` 控制演示初始化。

| 演示账号 | 权限 |
|---|---|
| operator@demo.test | 提交领域记录和计算请求 |
| reviewer@demo.test | 提交记录并执行有业务约束的复核操作 |
| viewer@demo.test | 浏览业务台账 |

三个本地演示账号均使用 `DemoC0de!2026`。角色在 `backend/core/roles.py` 和 `frontend/src/store.js` 中声明。计算状态在 worker、queueing、API 和同一前端 store 中使用。

## 页面与接口

| 业务任务 | FastAPI 路由 | 页面 |
|---|---|---|
| 饰件签收 | `/pieces` /pieces/receive | `frontend/src/pages/pieces.js` |
| 工序与双见证 | `/bench_steps` /bench_steps/add-operation，/bench_steps/witness-stone | `frontend/src/pages/bench_steps.js` |
| 工期区间 | `/lead_windows` /lead_windows/fit-window，/lead_windows/save-window | `frontend/src/pages/lead_windows.js` |
| 客户承诺票 | `/promise_tickets` /promise_tickets/issue-ticket，/promise_tickets/revise-ticket，/promise_tickets/traces | `frontend/src/pages/promise_tickets.js` |
| 实际完工校准 | `/completions` /completions/record | `frontend/src/pages/completions.js` |

SQL 实体与约束在 `backend/domain` 下维护。前端使用原生 ES modules。核心算子为 QuantileRegressor。两个线性 QuantileRegressor 分别拟合 0.2 和 0.8。110 条训练、末 30 条留出；分别报告损失和区间覆盖，另记预测顺序交叉次数。

工期计算使用可复现的模拟完工单。日数按日历日，工台日为独占，当前不连接支付、客户通知或贵重物运输。

[MIT](LICENSE)

### 工台占用规则

工台 A/B 每个日历日仅接受一张现行票。签发区间从开工日开始，用 P80 日数折成闭区间。模型采用小店历史中的总工台分钟、饰件总重、贵重石数、排队单数，签发前复核工序快照和贵重石见证。日期重叠或重复签发返回明确原因。重排保留前序票编号、修订理由和原窗口，只有新窗口满足全部规则后同时更新状态。日期占用条和分位范围条直接读取后端记录。

### 完工日校准

柜台补录实际完工日后，用早期完工记录校准 P80 上限，再用后期记录比较新旧上限。规则集中在 `backend/domain/calibration.py`：

1. 每件饰件只认最后一张票（修订链末端）；票上用估算的 `backlog` 决定分档（0–5、6–11、12–17、18–24）。
2. 同档完工记录按实际完工日排序，前 60%（至少 4 条）用来校准，其余（至少 3 条）用来比较；总量不足 7 条直接沿用原估算。
3. 新上限 = 模型原上限 + 早期残差（实际天数 − 原上限）的 P80 分位，向上取整，且不低于 P20。
4. 若新上限在比较段的超期率或 P80 分位损失任一项变差，就退回原估算；校准的偏移、样本、指标和原因随 `evidence.calibration` 归档。
5. 补录或更正完工日后，本档排队中的计算作废、本档已归档但未签票的估算就地重算；其他档照常。签票、更正与归档共用同一事务锁，并发时先落账的一方算数。
6. 承诺票页面读取 `/promise_tickets/traces`，显示每张票签发时用的分档、样本、超期率与上限；已签日期不回改。

演示文案不含个人姓名、地址、付款或实物运输信息。三个角色状态映射分别见 `backend/core/roles.py` 与 `frontend/src/store.js`；市面实际工期以诊断和双方约定为准。
