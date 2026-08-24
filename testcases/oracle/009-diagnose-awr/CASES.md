# Oracle AWR 诊断 (db-oracle-diagnose-awr) 测试用例集

> 验证 AWR 报告分析的深度、趋势判断的准确性和优化建议的可操作性。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 风险 |
|------|------|------|--------|------|
| TSK-DA-001 | AWR 报告解析 | 正例 | P0 | 低 |
| TSK-DA-002 | 趋势分析 | 正例 | P0 | 低 |
| TSK-DA-003 | 优化建议可执行性 | 正例 | P0 | 低 |
| TSK-DA-004 | AWR 数据缺失 | 反例 | P1 | 低 |
| TSK-DA-005 | 瞬时峰值 | 反例 | P1 | 低 |
| TSK-DA-006 | 双快照对比 | 边界 | P1 | 低 |
| TSK-DA-007 | 长周期趋势 | 边界 | P2 | 低 |

---

test_id: TSK-DA-001
type: positive
skill: db-oracle-diagnose-awr
dimension: functional
priority: P0
risk_level: low

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