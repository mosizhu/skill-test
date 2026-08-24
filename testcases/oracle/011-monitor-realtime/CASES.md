# Oracle 实时监控 (db-oracle-monitor-realtime) 测试用例集

> 验证实时监控能力的准确性、及时性和告警触发能力。覆盖 CPU、内存、会话、等待事件、表空间等核心指标。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 风险 |
|------|------|------|--------|------|
| TSK-MR-001 | 基础数据采集 | 正例 | P0 | 低 |
| TSK-MR-002 | 数据准确性验证 | 正例 | P0 | 低 |
| TSK-MR-003 | 告警阈值触发 | 正例 | P0 | 低 |
| TSK-MR-004 | 非法参数拒绝 | 反例 | P1 | 低 |
| TSK-MR-005 | 断线重连 | 反例 | P1 | 低 |
| TSK-MR-006 | 高阈值覆盖 | 边界 | P1 | 低 |
| TSK-MR-007 | 多指标同时告警 | 边界 | P1 | 低 |
| TSK-MR-008 | 快照时间精度 | 边界 | P2 | 低 |
| TSK-MR-009 | 输出格式规范 | 边界 | P2 | 低 |

---

test_id: TSK-MR-001
type: positive
skill: db-oracle-monitor-realtime
dimension: functional
priority: P0
risk_level: low

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