# 回归测试套件

覆盖已知问题的修复验证和核心功能的增量回归。适用于版本迭代后的回归测试。

## 套件信息

| 属性 | 值 |
|------|------|
| 执行耗时 | 15-20 分钟 |
| 覆盖维度 | functional, security, quality, reliability |
| 适用场景 | 版本迭代、Bug 修复后、季度回归 |

## 测试用例

### 核心功能回归

| 编号 | 用例 | 维度 | 优先级 | 备注 |
|------|------|------|--------|------|
| 1 | [TSK-IN-001](../testcases/oracle/010-inspect/CASES.md) | functional | P0 | 健康巡检是日常最高频操作 |
| 2 | [TSK-DQ-001](../testcases/oracle/006-diagnose-slow-query/CASES.md) | functional | P1 | 慢查询诊断是核心功能 |
| 3 | [TSK-DP-001](../testcases/oracle/007-diagnose-perf/CASES.md) | functional | P1 | 性能诊断是核心功能 |
| 4 | [TSK-MR-001](../testcases/oracle/011-monitor-realtime/CASES.md) | functional | P1 | 实时监控是核心功能 |
| 5 | [TSK-CM-003](../testcases/common/CASES.md) | reliability | P1 | 连接失败处理 |
| 6 | [TSK-CM-004](../testcases/common/CASES.md) | boundary | P2 | 权限不足处理 |

## 通过标准

- 所有 P0 用例必须通过（通过率 100%）
- P1 用例通过率 >= 90%
- P2 用例通过率 >= 80%