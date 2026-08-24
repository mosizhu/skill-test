# Oracle AWR 诊断 (db-oracle-diagnose-awr) 测试用例集

> 验证 AWR 报告分析的深度、趋势判断的准确性和优化建议的可操作性。
>
> **环境隔离策略**: AWR 分析基于 Oracle 内置 AWR 数据，无需额外构造。但部分测试需要 AWR 快照范围包含特定时间段的负载数据。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 环境需求 |
|------|------|------|--------|----------|
| TSK-DA-001 | AWR 报告解析 | 正例 | P0 | 无需构造，直接执行 |
| TSK-DA-002 | 趋势分析 | 正例 | P0 | 无需构造，直接执行 |
| TSK-DQ-003 | 优化建议可执行性 | 正例 | P0 | 无需构造，直接执行 |
| TSK-DA-004 | AWR 数据缺失 | 反例 | P1 | 无需构造 |
| TSK-DA-005 | 瞬时峰值 | 反例 | P1 | TEST002 填充数据触发峰值 |
| TSK-DA-006 | 双快照对比 | 边界 | P1 | 无需构造 |
| TSK-DA-007 | 长周期趋势 | 边界 | P2 | 无需构造 |

## 隔离环境说明

- AWR 分析基于 Oracle 内置 AWR 数据（`WRH$*`, `WRI$` 等表）
- 构造负载数据的用例隔离在 TEST002 表空间
- **清理策略**: 每个构造数据的用例末尾 `DROP TABLE` + 验证空间释放

---

test_id: TSK-DA-001
type: positive
skill: db-oracle-diagnose-awr
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证 AWR 报告解析的完整性和准确性。

## 前置条件

- oracle-rac_node01 实例运行正常
- AWR 数据可用

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-diagnose-awr` skill
2. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `snapshot_from` = 较新的快照 ID
   - `snapshot_to` = 较新的快照 ID
   - `top_n_events` = 10
3. 等待诊断完成

## 预期结果

### AWR 报告结构

```
## AWR 诊断报告
### 快照信息
| 属性 | 值 |
|------|------|
| 快照范围 | snap_id: N -> M |
| 持续时间 | HH:MM:SS |
| 快照间隔 | N 分钟 |

### Load Profile
| 指标 | 每秒 | 每次传输 |
|------|------|---------|
| 逻辑读 | X | Y |
| 物理读 | X | Y |
| 物理写 | X | Y |
| SQL 执行 | X | Y |
| 事务 | X | Y |

### Top 5 时间模型
| 统计项 | 总时间(秒) | 占比(%) |
|--------|-----------|--------|
| SQL 执行 | X | Y% |
| PL/SQL 执行 | X | Y% |
| DB 查询 | X | Y% |

### Top 10 等待事件
| 等待事件 | 总等待时间(秒) | 平均等待(毫秒) |
|----------|---------------|---------------|

### SQL 统计 TOP 10
| SQL ID | 执行次数 | 总时间(秒) | 平均时间(秒) | 逻辑读 |
|--------|---------|-----------|-------------|--------|
```

## 通过标准

- 快照信息完整（ID、时间、间隔）
- Load Profile 包含所有关键指标
- Top 5 时间模型按总时间排序
- Top 10 等待事件包含总等待时间和平均等待
- Top 10 SQL 包含执行次数、时间、逻辑读

---

test_id: TSK-DA-002
type: positive
skill: db-oracle-diagnose-awr
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证 AWR 趋势分析的准确性。

## 前置条件

- oracle-rac_node01 实例运行正常
- 有多个 AWR 快照

## 执行步骤

1. 触发 `db-oracle-diagnose-awr` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 选择跨度较大的快照范围（如 4 小时）
4. 验证趋势分析:
   a) 时间维度对比（负载变化趋势）
   b) 关键指标变化率（如逻辑读增长率）
   c) 负载波峰/波谷识别

## 预期结果

- 趋势分析正确（上升/下降/平稳）
- 负载波动有明确的时间点标注
- 关键指标变化率准确

## 通过标准

- 趋势分析正确
- 波峰/波谷有明确时间点
- 变化率准确

---

test_id: TSK-DA-003
type: positive
skill: db-oracle-diagnose-awr
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证 AWR 诊断优化建议的可执行性。

## 前置条件

- oracle-rac_node01 实例运行正常
- AWR 中有可优化的 SQL

## 执行步骤

1. 触发 `db-oracle-diagnose-awr` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 对优化建议验证:
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

---

test_id: TSK-DA-004
type: negative
skill: db-oracle-diagnose-awr
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证 AWR 数据缺失时的处理。

## 前置条件

- 无特殊要求

## 执行步骤

1. 触发 `db-oracle-diagnose-awr` skill
2. 传入不存在的快照 ID: `snapshot_from` = 99999, `snapshot_to` = 99998
3. 观察 skill 行为

## 预期结果

- AWR 数据不可用时明确说明
- 不产生空报告
- 建议用户确认 AWR 快照是否可用

## 通过标准

- 准确识别 AWR 数据不可用
- 给出清晰的错误说明

---

test_id: TSK-DA-005
type: negative
skill: db-oracle-diagnose-awr
dimension: boundary
priority: P1
risk_level: low
isolation: test002_fill
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DA_PEAK CHECK CONSTRAINTS CASCADE"

## 测试目标

验证瞬时峰值的 AWR 分析能力。

## 前置条件

- 需要在 TEST002 中构造瞬时峰值

## 执行步骤

1. **构造瞬时峰值环境** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DA_PEAK (id NUMBER, data CLOB) TABLESPACE TEST002;
   
   -- 短时间大量插入，产生峰值
   INSERT /*+ APPEND */ INTO TEST_DA_PEAK SELECT ROWNUM, RPAD('X', 2000, 'X')
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 10000);
   COMMIT;
   
   -- 立即清理
   DELETE FROM TEST_DA_PEAK;
   COMMIT;
   ```

2. 触发 `db-oracle-diagnose-awr` skill
3. 选择包含峰值时间的快照范围
4. 观察峰值分析

## 预期结果

- 峰值时间段被正确识别
- 峰值期间的负载变化有分析
- 峰值原因有推测（如大量 DML）

## 通过标准

- 峰值时间段被正确识别
- 峰值原因有推测

## 清理

```sql
DROP TABLE TEST_DA_PEAK;
```

---

test_id: TSK-DA-006
type: boundary
skill: db-oracle-diagnose-awr
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证双快照对比分析的准确性。

## 前置条件

- oracle-rac_node01 实例运行正常
- 至少有两个 AWR 快照

## 执行步骤

1. 触发 `db-oracle-diagnose-awr` skill
2. 传入两个相邻快照的 ID
3. 验证:
   a) 两个快照之间的变化被正确计算
   b) 关键指标的变化率准确
   c) SQL 执行统计变化正确

## 预期结果

- 快照间变化正确计算
- 关键指标变化率准确
- SQL 统计变化正确

## 通过标准

- 变化计算准确
- SQL 统计变化正确

---

test_id: TSK-DA-007
type: boundary
skill: db-oracle-diagnose-awr
dimension: boundary
priority: P2
risk_level: low
isolation: none

## 测试目标

验证长周期趋势分析的准确性。

## 前置条件

- oracle-rac_node01 实例运行正常
- 有足够长的 AWR 快照范围（如 7 天）

## 执行步骤

1. 触发 `db-oracle-diagnose-awr` skill
2. 传入跨度较大的快照范围（如 7 天）
3. 观察长周期趋势分析

## 预期结果

- 趋势分析按天/周分段
- 工作日/非工作日模式被识别
- 关键指标趋势线正确

## 通过标准

- 分段分析正确
- 模式被识别
- 趋势线正确