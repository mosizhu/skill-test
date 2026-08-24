# 冒烟测试套件

快速验证核心功能是否正常，约 5-10 分钟可完成。适用于每次 skill 变更后的快速回归。

## 套件信息

| 属性 | 值 |
|------|------|
| 执行耗时 | 5-10 分钟 |
| 覆盖维度 | functional, security |
| 适用场景 | skill 变更后、CI/CD 流水线 |

## 测试用例

| 编号 | 用例 | 维度 | 优先级 | 说明 |
|------|------|------|--------|------|
| 1 | [TSK-IN-001](../testcases/oracle/010-inspect/CASES.md) | 功能 | P0 | 完整巡检执行 |
| 2 | [TSK-DQ-001](../testcases/oracle/006-diagnose-slow-query/CASES.md) | 功能 | P0 | 慢查询正常诊断 |
| 3 | [TSK-DP-001](../testcases/oracle/007-diagnose-perf/CASES.md) | 功能 | P0 | 整体性能诊断 |
| 4 | [TSK-CM-001](../testcases/common/CASES.md) | 边界 | P0 | 非法参数处理 |
| 5 | [TSK-CM-003](../testcases/common/CASES.md) | 可靠性 | P0 | 数据库不可达 |

## 通过标准

- 所有 P0 用例必须通过
- 总通过率 >= 90%