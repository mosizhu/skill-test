# Oracle 实时监控 (db-oracle-monitor-realtime) 测试用例集

> 验证实时监控能力的准确性、及时性和告警触发能力。覆盖 CPU、内存、会话、等待事件、表空间等核心指标。
>
> **环境隔离策略**: 构造负载数据的用例隔离在 TEST002 表空间，测试后清理。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 环境需求 |
|------|------|------|--------|----------|
| TSK-MR-001 | 基础数据采集 | 正例 | P0 | 无需构造，直接执行 |
| TSK-MR-002 | 数据准确性验证 | 正例 | P0 | 无需构造，直接执行 |
| TSK-MR-003 | 告警阈值触发 | 正例 | P0 | TEST002 填充测试数据 |
| TSK-MR-004 | 非法参数拒绝 | 反例 | P1 | 无需构造 |
| TSK-MR-005 | 断线重连 | 反例 | P1 | 无需构造 |
| TSK-MR-006 | 高阈值覆盖 | 边界 | P1 | TEST002 构造高负载 |
| TSK-MR-007 | 多指标同时告警 | 边界 | P1 | TEST002 构造多指标触发 |
| TSK-MR-008 | 快照时间精度 | 边界 | P2 | 无需构造 |
| TSK-MR-009 | 输出格式规范 | 边界 | P2 | 无需构造 |

## 隔离环境说明

- **隔离表空间**: `TEST002`（~35MB，支持自动扩展至 ~196GB）
- **隔离前缀**: 所有测试对象以 `TEST_MR_` 为前缀
- **清理策略**: 每个构造数据的用例末尾 `DROP TABLE` + 验证空间释放

---

test_id: TSK-MR-001
type: positive
skill: db-oracle-monitor-realtime
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证实时监控能采集核心指标的完整性和及时性。

## 前置条件

- oracle-rac_node01 实例运行正常
- 存在活跃会话和等待事件

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-monitor-realtime` skill
2. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `monitor_duration` = `30`（采集 30 秒）
   - `snapshot_interval` = `5`（每 5 秒采集一次）
3. 等待监控完成

## 预期结果

### 必须采集的指标

| 指标类别 | 子指标 | 采集频率 |
|----------|--------|----------|
| CPU | 使用率 (%) | 每 5 秒 |
| 内存 | SGA/PGA 使用率 (%) | 每 5 秒 |
| 会话 | 总数/活跃/空闲/等待 | 每 5 秒 |
| 等待事件 | 主要等待事件 TOP 5 | 每 5 秒 |
| 表空间 | 增长速率 (MB/秒) | 每 5 秒 |

### 输出要求

- 每个指标有采集时间戳
- 输出包含时间序列数据（至少 6 个时间点）
- 有最终统计值（平均、最大、最小）
- 异常值单独标注

## 通过标准

- 所有指标类别均有数据
- 时间序列数据点 >= 5
- 时间戳精度到秒
- 最终统计包含平均、最大、最小值

---

test_id: TSK-MR-002
type: positive
skill: db-oracle-monitor-realtime
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证采集数据的准确性，与直接查询结果对比。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-monitor-realtime` skill
2. 传入 `instance_host` = `oracle-rac_node01`，`monitor_duration` = `10`
3. 监控同时执行以下查询作为对照:

   a) 实时会话数:
   ```sql
   SELECT COUNT(*) as total,
          SUM(CASE WHEN status='ACTIVE' THEN 1 ELSE 0 END) as active,
          SUM(CASE WHEN status='INACTIVE' THEN 1 ELSE 0 END) as inactive
   FROM v$session;
   ```
   b) 实时 CPU 使用率:
   ```sql
   SELECT ROUND(100*(1-s.user_io/total),2) as cpu_idle_pct
   FROM (SELECT value user_io FROM v$sysstat WHERE stat_name='CPU used by this session') s,
        (SELECT value total FROM v$sysstat WHERE stat_name='stat ...') t;
   ```

4. 对比监控报告中的会话数和 CPU 使用率

## 预期结果

- 会话数误差 <= 1（允许 +/-1 的时间窗口差异）
- CPU 使用率误差 <= 0.1%
- 采集时间戳与实际执行时间吻合

## 通过标准

- 核心指标误差在允许范围内
- 时间戳与执行时间一致
- 不遗漏任何活跃会话

---

test_id: TSK-MR-003
type: positive
skill: db-oracle-monitor-realtime
dimension: functional
priority: P0
risk_level: low
isolation: test002_fill
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_MR_LOAD CHECK CONSTRAINTS CASCADE"

## 测试目标

验证告警阈值的正确触发。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. **构造负载数据** (在 TEST002):
   ```sql
   CREATE TABLE TEST_MR_LOAD (id NUMBER, data VARCHAR2(4000)) TABLESPACE TEST002;
   
   -- 填充数据触发表空间告警
   INSERT /*+ APPEND */ INTO TEST_MR_LOAD SELECT ROWNUM, RPAD('X', 4000, 'X')
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 5000);
   COMMIT;
   
   -- 触发会话数告警: 创建 50 个会话
   ```

2. 触发 `db-oracle-monitor-realtime` skill
3. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `monitor_duration` = `30`
   - `alert_thresholds`:
     - `cpu_usage` = `80`（CPU 使用率超过 80% 告警）
     - `session_count` = `100`（会话数超过 100 告警）
     - `tablespace_usage` = `90`（表空间使用率超过 90% 告警）
     - `waitevent_count` = `10`（单事件等待会话超过 10 告警）

## 预期结果

- CPU 使用率 > 80% 时触发 CPU 告警
- 会话数 > 100 时触发会话数告警
- 表空间使用率 > 90% 时触发告警
- 单个等待事件等待会话 > 10 时触发告警

### 告警格式要求

每条告警必须包含:
```
### 告警 #N
- **等级**: WARNING / CRITICAL
- **指标**: 指标名称
- **阈值**: 触发阈值
- **当前值**: 实际值
- **时间**: 触发时间
- **建议**: 处理建议
```

## 通过标准

- 超过阈值的指标正确触发告警
- 未超过阈值的指标不产生误报
- 告警格式统一，包含所有必要字段
- 告警按严重程度排序

## 清理

```sql
DROP TABLE TEST_MR_LOAD;
```

---

test_id: TSK-MR-004
type: negative
skill: db-oracle-monitor-realtime
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证非法参数输入的处理。

## 前置条件

- 无特殊要求

## 执行步骤

1. 触发 `db-oracle-monitor-realtime` skill
2. 传入非法参数:
   - 情况 A: `monitor_duration` = -5（负数）
   - 情况 B: `snapshot_interval` = 0
   - 情况 C: `monitor_duration` = "abc"（非数字）
3. 观察 skill 行为

## 预期结果

- 所有非法输入被拒绝
- 错误信息包含具体原因
- 不执行任何查询

## 通过标准

- 非法参数被拒绝
- 错误信息包含具体原因

---

test_id: TSK-MR-005
type: negative
skill: db-oracle-monitor-realtime
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证断线重连的能力。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 触发 `db-oracle-monitor-realtime` skill
2. 传入 `instance_host` = `oracle-rac_node01`，`monitor_duration` = `60`（长时监控）
3. 观察 skill 在网络断开后的处理

## 预期结果

- 网络断开后有明确的错误提示
- 网络恢复后能自动重连
- 重连后的数据点不遗漏

## 通过标准

- 网络断开有明确提示
- 自动重连能力
- 数据点不遗漏

---

test_id: TSK-MR-006
type: boundary
skill: db-oracle-monitor-realtime
dimension: boundary
priority: P1
risk_level: low
isolation: test002_load
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_MR_HIGH_LOAD CHECK CONSTRAINTS CASCADE"

## 测试目标

验证高阈值覆盖场景的监控准确性。

## 前置条件

- 需要在 TEST002 中构造高负载

## 执行步骤

1. **构造高负载环境** (在 TEST002):
   ```sql
   CREATE TABLE TEST_MR_HIGH_LOAD (id NUMBER, data VARCHAR2(4000)) TABLESPACE TEST002;
   
   INSERT /*+ APPEND */ INTO TEST_MR_HIGH_LOAD SELECT ROWNUM, RPAD('X', 4000, 'X')
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 100000);
   COMMIT;
   ```

2. 触发 `db-oracle-monitor-realtime` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 验证监控输出

## 预期结果

- 高负载场景下监控数据完整
- 不产生数据丢失
- 告警正确触发

## 通过标准

- 监控数据完整
- 告警正确触发

## 清理

```sql
DROP TABLE TEST_MR_HIGH_LOAD;
```

---

test_id: TSK-MR-007
type: boundary
skill: db-oracle-monitor-realtime
dimension: boundary
priority: P1
risk_level: low
isolation: test002_multi
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_MR_MULTI CHECK CONSTRAINTS CASCADE"

## 测试目标

验证多指标同时告警时的处理能力。

## 前置条件

- 需要在 TEST002 中构造多指标触发场景

## 执行步骤

1. **构造多指标触发环境** (在 TEST002):
   ```sql
   CREATE TABLE TEST_MR_MULTI (
     id NUMBER,
     status VARCHAR2(20),
     value NUMBER,
     created_date DATE
   ) TABLESPACE TEST002;
   
   INSERT INTO TEST_MR_MULTI SELECT ROWNUM,
     CASE MOD(ROWNUM, 3) WHEN 0 THEN 'ACTIVE' WHEN 1 THEN 'INACTIVE' ELSE 'PENDING' END,
     ROWNUM, SYSDATE - ROWNUM/1000
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 50000);
   COMMIT;
   ```

2. 触发 `db-oracle-monitor-realtime` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 验证多指标同时告警的处理

## 预期结果

- 多指标告警独立列出
- 不互相干扰
- 按严重程度排序

## 通过标准

- 多指标告警独立列出
- 按严重程度排序

## 清理

```sql
DROP TABLE TEST_MR_MULTI;
```

---

test_id: TSK-MR-008
type: boundary
skill: db-oracle-monitor-realtime
dimension: boundary
priority: P2
risk_level: low
isolation: none

## 测试目标

验证快照时间精度。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 触发 `db-oracle-monitor-realtime` skill
2. 传入 `instance_host` = `oracle-rac_node01`，`monitor_duration` = `10`，`snapshot_interval` = `2`
3. 检查时间戳精度:
   a) 时间戳是否精确到秒
   b) 时间间隔是否一致
   c) 时间顺序是否正确

## 预期结果

- 时间戳精确到秒
- 时间间隔一致（误差 <= 1 秒）
- 时间顺序正确

## 通过标准

- 时间戳精确到秒
- 时间间隔一致
- 时间顺序正确

---

test_id: TSK-MR-009
type: boundary
skill: db-oracle-monitor-realtime
dimension: quality
priority: P2
risk_level: low
isolation: none

## 测试目标

验证监控输出的可读性和格式规范。

## 前置条件

- 正常执行监控

## 执行步骤

1. 触发 `db-oracle-monitor-realtime` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 逐项检查:
   a) 各指标有明确标题
   b) 时间序列数据格式统一
   c) 告警有颜色/符号标注
   d) 有总结段落

## 预期结果

- ✅ 各指标有明确标题
- ✅ 时间序列数据格式统一
- ✅ 告警使用 ⚠️ 标注
- ✅ 有总结段落

## 通过标准

- 格式规范
- 数据格式统一
- 告警清晰可见
- 有总结段落