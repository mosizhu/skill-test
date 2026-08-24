# 全量测试套件

完整覆盖所有已实现 Oracle 技能的功能和边界测试。

## 套件信息

| 属性 | 值 |
|------|------|
| 执行耗时 | 30-60 分钟 |
| 覆盖维度 | functional, boundary, quality, reliability |
| 适用场景 | 正式发布前、重大变更回归 |

## Oracle 技能测试用例

### 健康巡检 (db-oracle-inspect)

| 编号 | 用例 | 类型 | 优先级 | 文件 |
|------|------|------|--------|------|
| TSK-IN-001 | 完整巡检执行 | 正例 | P0 | [CASES.md](../testcases/oracle/010-inspect/CASES.md) |
| TSK-IN-002 | 数值准确性 | 正例 | P0 | [CASES.md](../testcases/oracle/010-inspect/CASES.md) |
| TSK-IN-003 | 非法参数拒绝 | 反例 | P1 | [CASES.md](../testcases/oracle/010-inspect/CASES.md) |
| TSK-IN-004 | 空结果处理 | 反例 | P1 | [CASES.md](../testcases/oracle/010-inspect/CASES.md) |
| TSK-IN-005 | 权限降级 | 反例 | P1 | [CASES.md](../testcases/oracle/010-inspect/CASES.md) |
| TSK-IN-006 | 表空间接近满 | 边界 | P1 | [CASES.md](../testcases/oracle/010-inspect/CASES.md) |
| TSK-IN-007 | 等待事件分析 | 边界 | P1 | [CASES.md](../testcases/oracle/010-inspect/CASES.md) |
| TSK-IN-008 | 会话数超限 | 边界 | P2 | [CASES.md](../testcases/oracle/010-inspect/CASES.md) |
| TSK-IN-009 | 数据字典缺失 | 边界 | P2 | [CASES.md](../testcases/oracle/010-inspect/CASES.md) |
| TSK-IN-010 | 输出格式规范 | 边界 | P2 | [CASES.md](../testcases/oracle/010-inspect/CASES.md) |

### 慢查询诊断 (db-oracle-diagnose-slow-query)

| 编号 | 用例 | 类型 | 优先级 | 文件 |
|------|------|------|--------|------|
| TSK-DQ-001 | 慢查询正常诊断 | 正例 | P0 | [CASES.md](../testcases/oracle/006-diagnose-slow-query/CASES.md) |
| TSK-DQ-002 | 诊断数据准确性 | 正例 | P0 | [CASES.md](../testcases/oracle/006-diagnose-slow-query/CASES.md) |
| TSK-DQ-003 | 优化建议可执行性 | 正例 | P0 | [CASES.md](../testcases/oracle/006-diagnose-slow-query/CASES.md) |
| TSK-DQ-004 | 非法 SQL 拒绝 | 反例 | P1 | [CASES.md](../testcases/oracle/006-diagnose-slow-query/CASES.md) |
| TSK-DQ-005 | 空执行计划 | 反例 | P1 | [CASES.md](../testcases/oracle/006-diagnose-slow-query/CASES.md) |
| TSK-DQ-006 | 超长 SQL | 边界 | P1 | [CASES.md](../testcases/oracle/006-diagnose-slow-query/CASES.md) |
| TSK-DQ-007 | 递归/嵌套查询 | 边界 | P2 | [CASES.md](../testcases/oracle/006-diagnose-slow-query/CASES.md) |
| TSK-DQ-008 | 绑定变量查询 | 边界 | P2 | [CASES.md](../testcases/oracle/006-diagnose-slow-query/CASES.md) |

### 性能诊断 (db-oracle-diagnose-perf)

| 编号 | 用例 | 类型 | 优先级 | 文件 |
|------|------|------|--------|------|
| TSK-DP-001 | 整体性能诊断 | 正例 | P0 | [CASES.md](../testcases/oracle/007-diagnose-perf/CASES.md) |
| TSK-DP-002 | 性能瓶颈定位 | 正例 | P0 | [CASES.md](../testcases/oracle/007-diagnose-perf/CASES.md) |
| TSK-DP-003 | 优化建议可执行性 | 正例 | P0 | [CASES.md](../testcases/oracle/007-diagnose-perf/CASES.md) |
| TSK-DP-004 | 非法参数 | 反例 | P1 | [CASES.md](../testcases/oracle/007-diagnose-perf/CASES.md) |
| TSK-DP-005 | 低负载场景 | 反例 | P1 | [CASES.md](../testcases/oracle/007-diagnose-perf/CASES.md) |
| TSK-DP-006 | 高并发场景 | 边界 | P1 | [CASES.md](../testcases/oracle/007-diagnose-perf/CASES.md) |
| TSK-DP-007 | 混合负载场景 | 边界 | P1 | [CASES.md](../testcases/oracle/007-diagnose-perf/CASES.md) |

### 死锁诊断 (db-oracle-diagnose-deadlock)

| 编号 | 用例 | 类型 | 优先级 | 文件 |
|------|------|------|--------|------|
| TSK-DL-001 | 死锁检测 | 正例 | P0 | [CASES.md](../testcases/oracle/008-diagnose-deadlock/CASES.md) |
| TSK-DL-002 | 根因分析 | 正例 | P0 | [CASES.md](../testcases/oracle/008-diagnose-deadlock/CASES.md) |
| TSK-DL-003 | 恢复建议 | 正例 | P0 | [CASES.md](../testcases/oracle/008-diagnose-deadlock/CASES.md) |
| TSK-DL-004 | 无死锁场景 | 反例 | P1 | [CASES.md](../testcases/oracle/008-diagnose-deadlock/CASES.md) |
| TSK-DL-005 | 历史死锁 | 边界 | P1 | [CASES.md](../testcases/oracle/008-diagnose-deadlock/CASES.md) |
| TSK-DL-006 | 循环死锁 | 边界 | P2 | [CASES.md](../testcases/oracle/008-diagnose-deadlock/CASES.md) |

### AWR 诊断 (db-oracle-diagnose-awr)

| 编号 | 用例 | 类型 | 优先级 | 文件 |
|------|------|------|--------|------|
| TSK-DA-001 | AWR 报告解析 | 正例 | P0 | [CASES.md](../testcases/oracle/009-diagnose-awr/CASES.md) |
| TSK-DA-002 | 趋势分析 | 正例 | P0 | [CASES.md](../../testcases/oracle/009-diagnose-awr/CASES.md) |
| TSK-DA-003 | 优化建议可执行性 | 正例 | P0 | [CASES.md](../testcases/oracle/009-diagnose-awr/CASES.md) |
| TSK-DA-004 | AWR 数据缺失 | 反例 | P1 | [CASES.md](../testcases/oracle/009-diagnose-awr/CASES.md) |
| TSK-DA-005 | 瞬时峰值 | 反例 | P1 | [CASES.md](../testcases/oracle/009-diagnose-awr/CASES.md) |
| TSK-DA-006 | 双快照对比 | 边界 | P1 | [CASES.md](../testcases/oracle/009-diagnose-awr/CASES.md) |
| TSK-DA-007 | 长周期趋势 | 边界 | P2 | [CASES.md](../testcases/oracle/009-diagnose-awr/CASES.md) |

### 实时监控 (db-oracle-monitor-realtime)

| 编号 | 用例 | 类型 | 优先级 | 文件 |
|------|------|------|--------|------|
| TSK-MR-001 | 基础数据采集 | 正例 | P0 | [CASES.md](../testcases/oracle/011-monitor-realtime/CASES.md) |
| TSK-MR-002 | 数据准确性验证 | 正例 | P0 | [CASES.md](../testcases/oracle/011-monitor-realtime/CASES.md) |
| TSK-MR-003 | 告警阈值触发 | 正例 | P0 | [CASES.md](../testcases/oracle/011-monitor-realtime/CASES.md) |
| TSK-MR-004 | 非法参数拒绝 | 反例 | P1 | [CASES.md](../testcases/oracle/011-monitor-realtime/CASES.md) |
| TSK-MR-005 | 断线重连 | 反例 | P1 | [CASES.md](../testcases/oracle/011-monitor-realtime/CASES.md) |
| TSK-MR-006 | 高阈值覆盖 | 边界 | P1 | [CASES.md](../testcases/oracle/011-monitor-realtime/CASES.md) |
| TSK-MR-007 | 多指标同时告警 | 边界 | P1 | [CASES.md](../testcases/oracle/011-monitor-realtime/CASES.md) |
| TSK-MR-008 | 快照时间精度 | 边界 | P2 | [CASES.md](../testcases/oracle/011-monitor-realtime/CASES.md) |
| TSK-MR-009 | 输出格式规范 | 边界 | P2 | [CASES.md](../testcases/oracle/011-monitor-realtime/CASES.md) |

### 异常监控 (db-oracle-monitor-anomaly)

| 编号 | 用例 | 类型 | 优先级 | 文件 |
|------|------|------|--------|------|
| TSK-MA-001 | 已知异常检测 | 正例 | P0 | [CASES.md](../testcases/oracle/012-monitor-anomaly/CASES.md) |
| TSK-MA-002 | 无异常确认 | 正例 | P0 | [CASES.md](../testcases/oracle/012-monitor-anomaly/CASES.md) |
| TSK-MA-003 | 误报控制 | 正例 | P0 | [CASES.md](../testcases/oracle/012-monitor-anomaly/CASES.md) |
| TSK-MA-004 | 异常参数 | 反例 | P1 | [CASES.md](../testcases/oracle/012-monitor-anomaly/CASES.md) |
| TSK-MA-005 | 阈值自适应 | 边界 | P1 | [CASES.md](../testcases/oracle/012-monitor-anomaly/CASES.md) |
| TSK-MA-006 | 多异常同时 | 边界 | P1 | [CASES.md](../testcases/oracle/012-monitor-anomaly/CASES.md) |

### 执行计划调优 (db-oracle-plan-tuning)

| 编号 | 用例 | 类型 | 优先级 | 文件 |
|------|------|------|--------|------|
| TSK-PT-001 | 计划分析 | 正例 | P0 | [CASES.md](../testcases/oracle/013-plan-tuning/CASES.md) |
| TSK-PT-002 | 建议可执行性 | 正例 | P0 | [CASES.md](../testcases/oracle/013-plan-tuning/CASES.md) |
| TSK-PT-003 | 影响评估 | 正例 | P0 | [CASES.md](../testcases/oracle/013-plan-tuning/CASES.md) |
| TSK-PT-004 | 非法 SQL | 反例 | P1 | [CASES.md](../testcases/oracle/013-plan-tuning/CASES.md) |
| TSK-PT-005 | 计划不存在 | 反例 | P1 | [CASES.md](../testcases/oracle/013-plan-tuning/CASES.md) |
| TSK-PT-006 | SQL 注入 | 边界 | P1 | [CASES.md](../testcases/oracle/013-plan-tuning/CASES.md) |
| TSK-PT-007 | 复杂嵌套 | 边界 | P2 | [CASES.md](../testcases/oracle/013-plan-tuning/CASES.md) |

## 通用测试用例

| 编号 | 名称 | 类型 | 优先级 | 适用 |
|------|------|------|--------|------|
| TSK-CM-001 | 非法参数 | 反例 | P0 | 所有 skill |
| TSK-CM-002 | 空结果处理 | 反例 | P0 | 所有 skill |
| TSK-CM-003 | 数据库不可达 | 反例 | P0 | 所有 skill |
| TSK-CM-004 | 权限不足 | 反例 | P0 | 所有 skill |
| TSK-CM-005 | 多环境歧义 | 边界 | P1 | 所有 skill |

## 通过标准

- P0 用例必须 100% 通过
- P1 用例通过率 >= 90%
- P2 用例通过率 >= 80%
- 每个 skill 至少覆盖正例、反例、边界三种类型