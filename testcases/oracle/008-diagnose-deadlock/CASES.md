# Oracle 死锁诊断 (db-oracle-diagnose-deadlock) 测试用例集

> 验证死锁检测的及时性、根因分析的准确性和恢复建议的有效性。
>
> **环境隔离策略**: 构造死锁数据隔离在 TEST002 表空间。由于死锁是并发操作，构造时需使用独立表。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 环境需求 |
|------|------|------|--------|----------|
| TSK-DL-001 | 死锁检测 | 正例 | P0 | 无需构造，直接执行 |
| TSK-DL-002 | 根因分析 | 正例 | P0 | TEST002 构造死锁环境 |
| TSK-DL-003 | 恢复建议 | 正例 | P0 | TEST002 构造死锁环境 |
| TSK-DL-004 | 无死锁场景 | 反例 | P1 | 无需构造 |
| TSK-DL-005 | 历史死锁 | 边界 | P1 | TEST002 构造死锁环境 |
| TSK-DL-006 | 循环死锁 | 边界 | P1 | TEST002 构造死锁环境 |

## 隔离环境说明

- **隔离表空间**: `TEST002`
- **隔离前缀**: 所有测试对象以 `TEST_DL_` 为前缀
- **清理策略**: `DROP TABLE` + 验证空间释放

---

test_id: TSK-DL-001
type: positive
skill: db-oracle-diagnose-deadlock
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证死锁检测的及时性和准确性。

## 前置条件

- oracle-rac_node01 实例运行正常
- 存在活跃事务

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-diagnose-deadlock` skill
2. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `check_mode` = `realtime`（实时检测）
   - `check_interval` = `5`（每 5 秒检查一次）
3. 观察 skill 对当前死锁状态的分析

## 预期结果

### 输出格式

```
## 死锁诊断报告
### 检测结果
| 属性 | 值 |
|------|------|
| 检测时间 | 2026-08-24 10:00:00 |
| 死锁状态 | 存在 / 不存在 |
| 活跃事务数 | N |
| 阻塞会话数 | M |

### 详细信息（存在死锁时）
| 会话 | SID | 用户 | 阻塞对象 | 等待事件 |
|------|-----|------|----------|----------|
| SID1 | 123 | user1 | table_A | enq: TX - row lock contention |

### 根因分析
- **触发条件**: 两个会话互相锁定对方需要的资源
- **触发时间**: 时间
- **影响范围**: 受影响的业务系统

### 处理建议
1. [紧急] 终止阻塞会话
2. [高] 优化应用逻辑
```

## 通过标准

- 检测结果准确（存在死锁则报告，不存在则说明）
- 如有死锁，至少列出 2 个会话的 SID 和用户
- 根因分析有明确的触发条件说明
- 处理建议分紧急程度

---

test_id: TSK-DL-002
type: positive
skill: db-oracle-diagnose-deadlock
dimension: functional
priority: P0
risk_level: low
isolation: test002_deadlock
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DL_DEADLOCK CHECK CONSTRAINTS CASCADE"

## 测试目标

验证死锁根因分析的深度和准确性。

## 前置条件

- 需要在 TEST002 中构造死锁环境

## 执行步骤

1. **构造死锁环境** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DL_DEADLOCK (
     id NUMBER PRIMARY KEY,
     name VARCHAR2(100),
     status VARCHAR2(20),
     value NUMBER
   ) TABLESPACE TEST002;
   
   INSERT INTO TEST_DL_DEADLOCK VALUES (1, 'A', 'X', 100);
   INSERT INTO TEST_DL_DEADLOCK VALUES (2, 'B', 'Y', 200);
   COMMIT;
   ```

2. 触发 `db-oracle-diagnose-deadlock` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 验证根因分析:
   a) 是否识别出阻塞链（谁阻塞谁）
   b) 是否列出涉及的表和操作
   c) 是否分析锁等待时间
   d) 是否分析锁等待队列长度

## 预期结果

- 阻塞链描述清晰（A 阻塞 B，B 阻塞 A）
- 涉及的表和操作有具体说明
- 锁等待时间精确到秒
- 锁等待队列长度

## 通过标准

- 阻塞链完整描述
- 涉及对象有具体说明
- 等待时间精确

## 清理

```sql
DROP TABLE TEST_DL_DEADLOCK;
```

---

test_id: TSK-DL-003
type: positive
skill: db-oracle-diagnose-deadlock
dimension: functional
priority: P0
risk_level: low
isolation: test002_deadlock
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DL_RECOVERY CHECK CONSTRAINTS CASCADE"

## 测试目标

验证恢复建议的有效性。

## 前置条件

- 需要在 TEST002 中构造死锁环境

## 执行步骤

1. **构造死锁环境** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DL_RECOVERY (
     id NUMBER PRIMARY KEY,
     name VARCHAR2(100),
     status VARCHAR2(20)
   ) TABLESPACE TEST002;
   
   INSERT INTO TEST_DL_RECOVERY VALUES (1, 'A', 'X');
   INSERT INTO TEST_DL_RECOVERY VALUES (2, 'B', 'Y');
   COMMIT;
   ```

2. 触发 `db-oracle-diagnose-deadlock` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 验证恢复建议:
   a) 建议是否具体可操作
   b) 建议的风险评估是否合理
   c) 建议的执行步骤是否完整

## 预期结果

- 每条建议有明确的操作步骤
- 高风险操作标注"需维护窗口"
- 每条建议有预估的收益

## 通过标准

- 所有建议可执行
- 有明确的操作步骤
- 高风险操作有标注

## 清理

```sql
DROP TABLE TEST_DL_RECOVERY;
```

---

test_id: TSK-DL-004
type: negative
skill: db-oracle-diagnose-deadlock
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证无死锁场景的诊断准确性。

## 前置条件

- oracle-rac_node01 实例运行正常，当前无死锁

## 执行步骤

1. 触发 `db-oracle-diagnose-deadlock` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 观察输出

## 预期结果

- 无死锁时输出:

```
## 死锁诊断报告
### 检测结果
| 属性 | 值 |
|------|------|
| 检测时间 | 2026-08-24 10:00:00 |
| 死锁状态 | 不存在 |
| 活跃事务数 | N |
| 阻塞会话数 | 0 |

无死锁检测。
```

## 通过标准

- 无死锁时正确输出"无死锁"
- 有检测时间戳
- 有检测范围说明

---

test_id: TSK-DL-005
type: boundary
skill: db-oracle-diagnose-deadlock
dimension: boundary
priority: P1
risk_level: low
isolation: test002_deadlock
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DL_HIST CHECK CONSTRAINTS CASCADE"

## 测试目标

验证历史死锁记录的分析。

## 前置条件

- 需要在 TEST002 中构造历史死锁

## 执行步骤

1. **构造历史死锁数据** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DL_HIST (
     id NUMBER,
     event_time TIMESTAMP,
     session_id NUMBER,
     blocked_by NUMBER,
     operation VARCHAR2(50)
   ) TABLESPACE TEST002;
   
   INSERT INTO TEST_DL_HIST VALUES (1, SYSDATE-1, 101, 202, 'UPDATE', '2026-08-23 14:00:00');
   INSERT INTO TEST_DL_HIST VALUES (2, SYSDATE-1, 202, 101, 'UPDATE', '2026-08-23 14:00:01');
   INSERT INTO TEST_DL_HIST VALUES (3, SYSDATE-1, 303, 404, 'INSERT', '2026-08-23 15:00:00');
   COMMIT;
   ```

2. 触发 `db-oracle-diagnose-deadlock` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 验证历史死锁的分析

## 预期结果

- 历史死锁被正确归类
- 重复模式被识别（如多个相同模式的死锁）
- 趋势分析（频率、时间段）

## 通过标准

- 历史死锁正确归类
- 重复模式被识别
- 趋势分析准确

## 清理

```sql
DROP TABLE TEST_DL_HIST;
```

---

test_id: TSK-DL-006
type: boundary
skill: db-oracle-diagnose-deadlock
dimension: boundary
priority: P1
risk_level: low
isolation: test002_deadlock
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DL_CYCLE CHECK CONSTRAINTS CASCADE"

## 测试目标

验证循环死锁的检测（3+ 会话循环阻塞）。

## 前置条件

- 需要在 TEST002 中构造循环死锁

## 执行步骤

1. **构造循环死锁环境** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DL_CYCLE_A (id NUMBER PRIMARY KEY, name VARCHAR2(50)) TABLESPACE TEST002;
   CREATE TABLE TEST_DL_CYCLE_B (id NUMBER PRIMARY KEY, name VARCHAR2(50)) TABLESPACE TEST002;
   CREATE TABLE TEST_DL_CYCLE_C (id NUMBER PRIMARY KEY, name VARCHAR2(50)) TABLESPACE TEST002;
   
   INSERT INTO TEST_DL_CYCLE_A VALUES (1, 'A');
   INSERT INTO TEST_DL_CYCLE_B VALUES (1, 'B');
   INSERT INTO TEST_DL_CYCLE_C VALUES (1, 'C');
   COMMIT;
   ```

2. 触发 `db-oracle-diagnose-deadlock` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 验证循环死锁的检测（A 锁 B，B 锁 C，C 锁 A）

## 预期结果

- 循环链完整描述（A → B → C → A）
- 每个环路的深度有说明
- 处理建议针对循环结构

## 通过标准

- 循环链完整描述
- 每个环路深度有说明
- 处理建议有效

## 清理

```sql
DROP TABLE TEST_DL_CYCLE_A;
DROP TABLE TEST_DL_CYCLE_B;
DROP TABLE TEST_DL_CYCLE_C;
```