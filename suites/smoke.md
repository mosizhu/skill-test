# 冒烟测试套件

快速验证核心功能是否正常，约 5-10 分钟可完成。适用于每次 skill 变更后的快速回归。

## 套件信息

| 属性 | 值 |
|------|------|
| 执行耗时 | 5-10 分钟 |
| 覆盖维度 | functional, security |
| 适用场景 | skill 变更后、CI/CD 流水线 |

## 测试用例

| 编号 | 用例 | 维度 | 优先级 |
|------|------|------|--------|
| 1 | [TSK-IN-001](../testcases/oracle/010-inspect.md) | 健康巡检 | P0 |
| 2 | [TSK-SW-001](../testcases/oracle/001-switchover-validate.md) | 切换前置校验 | P0 |
| 3 | [TSK-BK-001](../testcases/oracle/004-backup-full.md) | 全量备份 | P0 |
| 4 | [TSK-EX-001](../testcases/oracle/005-ddl-execute.md) | DDL/DML 执行 | P0 |
| 5 | [TSK-MN-001](../testcases/oracle/011-monitor-realtime.md) | 实时监控 | P1 |
| 6 | [TSK-DQ-001](../testcases/oracle/006-diagnose-slow-query.md) | 慢查询诊断 | P1 |
| 7 | [TSK-CM-003](../testcases/common/003-unreachable-db.md) | 不可达数据库 | P1 |

## 通过标准

- 所有 P0 用例必须通过
- P1 用例最多允许 1 个因环境原因 skip
- 总通过率 >= 80%