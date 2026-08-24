# 全量测试套件

完整覆盖所有功能和维度，适用于正式发布前的全面测试。

## 套件信息

| 属性 | 值 |
|------|------|
| 执行耗时 | 30-60 分钟 |
| 覆盖维度 | functional, security, quality, reliability, boundary |
| 适用场景 | 正式发布、季度回归测试 |

## 测试用例

### Oracle 功能测试

| 编号 | 用例 | 维度 | 优先级 |
|------|------|------|--------|
| 1 | [TSK-SW-001](../testcases/oracle/001-switchover-validate.md) | security | P0 |
| 2 | [TSK-SW-002](../testcases/oracle/002-switchover-execute.md) | security | P0 |
| 3 | [TSK-RE-001](../testcases/oracle/003-restore-full.md) | security | P0 |
| 4 | [TSK-BK-001](../testcases/oracle/004-backup-full.md) | functional | P0 |
| 5 | [TSK-EX-001](../testcases/oracle/005-ddl-execute.md) | functional | P0 |
| 6 | [TSK-IN-001](../testcases/oracle/010-inspect.md) | functional | P0 |
| 7 | [TSK-DQ-001](../testcases/oracle/006-diagnose-slow-query.md) | functional | P1 |
| 8 | [TSK-DQ-002](../testcases/oracle/007-diagnose-perf.md) | functional | P1 |
| 9 | [TSK-DQ-003](../testcases/oracle/008-diagnose-deadlock.md) | functional | P2 |
| 10 | [TSK-DQ-004](../testcases/oracle/009-diagnose-awr.md) | functional | P1 |
| 11 | [TSK-MN-001](../testcases/oracle/011-monitor-realtime.md) | functional | P1 |
| 12 | [TSK-MN-002](../testcases/oracle/012-monitor-anomaly.md) | functional | P2 |
| 13 | [TSK-PT-001](../testcases/oracle/013-plan-tuning.md) | functional | P1 |
| 14 | [TSK-PM-001](../testcases/oracle/014-plan-migration.md) | functional | P2 |
| 15 | [TSK-PB-001](../testcases/oracle/015-plan-backup.md) | functional | P2 |
| 16 | [TSK-AS-001](../testcases/oracle/016-audit-sql.md) | functional | P1 |
| 17 | [TSK-AP-001](../testcases/oracle/017-audit-permission.md) | functional | P1 |

### 通用边界/异常测试

| 编号 | 用例 | 维度 | 优先级 |
|------|------|------|--------|
| 18 | [TSK-CM-001](../testcases/common/001-invalid-params.md) | boundary | P2 |
| 19 | [TSK-CM-002](../testcases/common/002-empty-result.md) | reliability | P1 |
| 20 | [TSK-CM-003](../testcases/common/003-unreachable-db.md) | reliability | P1 |
| 21 | [TSK-CM-004](../testcases/common/004-insufficient-privilege.md) | boundary | P2 |
| 22 | [TSK-CM-005](../testcases/common/005-multi-env-ambiguity.md) | boundary | P2 |

## 通过标准

- 所有 P0 用例必须通过（通过率 100%）
- P1 用例通过率 >= 90%
- P2 用例通过率 >= 80%
- 高危用例（switchover、restore）必须有完整的手动确认记录