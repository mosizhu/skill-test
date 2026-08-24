# Oracle 异常监控 (db-oracle-monitor-anomaly) 测试用例集

> 验证异常检测的灵敏度、准确率和误报率控制。
>
> **环境隔离策略**: 构造异常数据的用例隔离在 TEST002 表空间，测试后清理。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 环境需求 |
|------|------|------|--------|----------|
| TSK-MA-001 | 已知异常检测 | 正例 | P0 | 无需构造，直接执行 |
| TSK-MA-002 | 无异常确认 | 正例 | P0 | 无需构造，直接执行 |
| TSK-MA-003 | 误报控制 | 正例 | P0 | TEST002 正常数据 |
| TSK-MA-004 | 异常参数 | 反例 | P1 | 无需构造 |
| TSK-MA-005 | 阈值自适应 | 边界 | P1 | TEST002 构造边界数据 |
| TSK-MA-006 | 多异常同时 | 边界 | P1 | TEST002 构造多异常 |

## 隔离环境说明

- **隔离表空间**: `TEST002`
- **隔离前缀**: 所有测试对象以 `TEST_MA_` 为前缀
- **清理策略**: 每个构造数据的用例末尾 `DROP TABLE` + 验证空间释放

---

test_id: TSK-MA-001
type: positive
skill: db-oracle-monitor-anomaly
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证对已知异常的准确检测。

## 前置条件

- oracle-rac_node01 实例运行正常
- 存在可检测的异常条件

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-monitor-anomaly` skill
2. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `anomaly_types` = `all`（检测所有类型异常）
   - `sensitivity` = `standard`
3. 等待检测完成

## 预期结果

### 输出格式

```
## 异常检测报告
### 检测概览
| 属性 | 值 |
|------|------|
| 检测时间 | 2026-08-24 10:00:00 |
| 检测范围 | CPU, 内存, 会话, 等待事件, 表空间, IO |
| 异常总数 | N |

### 异常详情
#### 异常 #1
- **ID**: ANOMALY-001
- **类型**: 表空间
- **等级**: CRITICAL
- **描述**: SYSTEM 表空间使用率 99.94%
- **影响**: 可能导致数据库不可用
- **检测时间**: 2026-08-24 10:00:00
- **持续时间**: 已持续 24 小时
- **建议**: 立即扩容 SYSTEM 表空间
```

## 通过标准

- 所有已知异常均被检测
- 异常等级正确（CRITICAL/WARNING/INFO）
- 异常有唯一 ID
- 每条异常有建议措施
- 异常按严重程度排序

---

test_id: TSK-MA-002
type: positive
skill: db-oracle-monitor-anomaly
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证正常状态下不误报。

## 前置条件

- oracle-rac_node01 实例运行正常，各项指标正常

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-monitor-anomaly` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 观察检测输出

## 预期结果

- 无异常时输出:

```
## 异常检测报告
### 检测结果
| 属性 | 值 |
|------|------|
| 检测时间 | 2026-08-24 10:00:00 |
| 异常总数 | 0 |
| 检测状态 | 正常 |

无异常检测。
```

## 通过标准

- 正常状态下不产生误报
- 输出明确说明"无异常"
- 有检测时间戳
- 有检测范围说明

---

test_id: TSK-MA-003
type: positive
skill: db-oracle-monitor-anomaly
dimension: quality
priority: P0
risk_level: low
isolation: test002_normal
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_MA_NORMAL CHECK CONSTRAINTS CASCADE"

## 测试目标

验证异常检测的误报率控制。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. **构造正常数据** (在 TEST002):
   ```sql
   CREATE TABLE TEST_MA_NORMAL (id NUMBER, value NUMBER, status VARCHAR2(20)) TABLESPACE TEST002;
   
   -- 正常数据（不触发告警）
   INSERT INTO TEST_MA_NORMAL SELECT ROWNUM, ROWNUM,
     CASE MOD(ROWNUM, 3) WHEN 0 THEN 'A' WHEN 1 THEN 'B' ELSE 'C' END
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 1000);
   COMMIT;
   ```

2. 触发 `db-oracle-monitor-anomaly` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 观察是否将 TEST002 正常数据误报为异常

## 预期结果

- 正常数据不产生异常
- TEST002 空间使用率低（< 5%），不触发告警
- 其他正常指标也不产生异常

## 通过标准

- 误报率为 0
- 正常指标不产生异常
- 异常检测准确

## 清理

```sql
DROP TABLE TEST_MA_NORMAL;
```

---

test_id: TSK-MA-004
type: negative
skill: db-oracle-monitor-anomaly
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证非法参数输入的处理。

## 前置条件

- 无特殊要求

## 执行步骤

1. 触发 `db-oracle-monitor-anomaly` skill
2. 传入非法参数:
   - 情况 A: `anomaly_types` = `invalid_type`
   - 情况 B: `sensitivity` = `invalid_level`
3. 观察 skill 行为

## 预期结果

- 非法参数被拒绝
- 错误信息包含合法的参数值列表
- 不执行任何查询

## 通过标准

- 非法参数被拒绝
- 错误信息包含合法值列表

---

test_id: TSK-MA-005
type: boundary
skill: db-oracle-monitor-anomaly
dimension: boundary
priority: P1
risk_level: low
isolation: test002_edge
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_MA_EDGE CHECK CONSTRAINTS CASCADE"

## 测试目标

验证阈值边界处的检测准确性。

## 前置条件

- 需要在 TEST002 中构造边界数据

## 执行步骤

1. **构造边界数据** (在 TEST002):
   ```sql
   CREATE TABLE TEST_MA_EDGE (id NUMBER, value NUMBER) TABLESPACE TEST002;
   
   -- 精确卡在阈值边界（如使用率 89.99%、90.01%）
   INSERT /*+ APPEND */ INTO TEST_MA_EDGE SELECT ROWNUM, RPAD('X', 4000, 'X')
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 9000);
   COMMIT;
   ```

2. 触发 `db-oracle-monitor-anomaly` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 观察边界值处理

## 预期结果

- 阈值边界值处理正确（如 89.99% < 90% 不告警，90.01% >= 90% 告警）
- 不产生边界错误

## 通过标准

- 边界值处理正确
- 无边界错误

## 清理

```sql
DROP TABLE TEST_MA_EDGE;
```

---

test_id: TSK-MA-006
type: boundary
skill: db-oracle-monitor-anomaly
dimension: boundary
priority: P1
risk_level: low
isolation: test002_multi
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_MA_MULTI CHECK CONSTRAINTS CASCADE"

## 测试目标

验证多异常同时触发时的处理。

## 前置条件

- 需要在 TEST002 中构造多异常

## 执行步骤

1. **构造多异常环境** (在 TEST002):
   ```sql
   CREATE TABLE TEST_MA_MULTI (id NUMBER, name VARCHAR2(200), status VARCHAR2(20)) TABLESPACE TEST002;
   
   INSERT /*+ APPEND */ INTO TEST_MA_MULTI SELECT ROWNUM, RPAD('X', 200, 'X'),
     CASE MOD(ROWNUM, 2) WHEN 0 THEN 'ACTIVE' ELSE 'INACTIVE' END
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 20000);
   COMMIT;
   ```

2. 触发 `db-oracle-monitor-anomaly` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 观察多异常处理

## 预期结果

- 多异常独立列出
- 按严重程度排序
- 不互相干扰

## 通过标准

- 多异常独立列出
- 按严重程度排序
- 不互相干扰