# Oracle 性能诊断 (db-oracle-diagnose-perf) 测试用例集

> 验证数据库整体性能诊断的准确性和优化建议的可操作性。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 风险 |
|------|------|------|--------|------|
| TSK-DP-001 | 整体性能诊断 | 正例 | P0 | 低 |
| TSK-DP-002 | 性能瓶颈定位 | 正例 | P0 | 低 |
| TSK-DP-003 | 优化建议可执行性 | 正例 | P0 | 低 |
| TSK-DP-004 | 非法参数 | 反例 | P1 | 低 |
| TSK-DP-005 | 低负载场景 | 反例 | P1 | 低 |
| TSK-DP-006 | 高并发场景 | 边界 | P1 | 低 |
| TSK-DP-007 | 混合负载场景 | 边界 | P1 | 低 |
| TSK-DP-008 | 输出格式规范 | 边界 | P2 | 低 |

---

test_id: TSK-DP-001
type: positive
skill: db-oracle-diagnose-perf
dimension: functional
priority: P0
risk_level: low

## 测试目标

验证整体性能诊断的完整性和准确性。

## 前置条件

- oracle-rac_node01 实例运行正常
- 存在一定负载

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-diagnose-perf` skill
2. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `diagnosis_depth` = `standard`（标准深度）
   - `include_tuning_suggestions` = true
3. 等待诊断完成（预期 30-60 秒）

## 预期结果

### 诊断报告结构

```
## 性能诊断报告
### 整体评分
| 维度 | 评分 | 状态 |
|------|------|------|
| CPU | 85/100 | ✅ 正常 |
| 内存 | 90/100 | ✅ 正常 |
| I/O | 70/100 | ⚠️ 偏高 |
| 网络 | 95/100 | ✅ 正常 |
| SQL | 80/100 | ⚠️ 有慢查询 |
| **综合** | **83/100** | **良好** |

### 瓶颈分析
1. **I/O 瓶颈**（评分 70）
   - 发现: db file sequential read 等待时间偏高
   - 影响: 排序操作和索引扫描受影响
   - 建议: 考虑将热点表放入 buffer pool

2. **SQL 性能**（评分 80）
   - 发现: 3 个 SQL 执行时间超过阈值
   - 建议: 查看慢查询诊断详情

### 关键参数
| 参数 | 当前值 | 建议值 | 状态 |
|------|--------|--------|------|
| sga_target | 4G | 4G | ✅ 合理 |
| pga_aggregate_target | 1G | 1G | ✅ 合理 |
| sessions | 792 | 792 | ✅ 合理 |

### 优化建议
1. [高] 分析热点表访问模式，考虑物化视图
2. [中] 优化 3 个慢查询（详见诊断报告）
3. [低] 定期检查统计信息过期情况
```

## 通过标准

- 有综合评分（0-100 分）
- 每个维度有独立评分
- 瓶颈分析有具体发现和影响说明
- 优化建议按优先级排序
- 关键参数有当前值与建议值对比

---

test_id: TSK-DP-002
type: positive
skill: db-oracle-diagnose-perf
dimension: functional
priority: P0
risk_level: low

## 测试目标

验证性能瓶颈的准确定位。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-diagnose-perf` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 验证瓶颈定位:
   a) 检查 CPU 等待事件排名
   b) 检查 I/O 等待事件排名
   c) 检查内存使用情况
   d) 对比诊断报告中的瓶颈分析与实际等待事件

## 预期结果

- 瓶颈定位与实际等待事件排名一致
- 主要瓶颈不遗漏
- 次要瓶颈不夸大
- 每个瓶颈有量化数据支撑

## 通过标准

- 瓶颈分析与实际数据一致
- 至少列出前 3 大瓶颈
- 每个瓶颈有量化数据支撑

---

test_id: TSK-DP-003
type: positive
skill: db-oracle-diagnose-perf
dimension: functional
priority: P0
risk_level: low

## 测试目标

验证优化建议的可执行性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-diagnose-perf` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 对每条优化建议验证:
   a) 建议是否具体可操作（如 "创建索引 X" 而非 "优化索引"）
   b) 建议的风险评估是否合理
   c) 建议的执行步骤是否完整

## 预期结果

- 每条建议有明确的操作步骤
- 高风险操作标注"需维护窗口"
- 每条建议有预估的收益（如 "预计减少 30% 等待时间"）

## 通过标准

- 所有建议可执行
- 高风险操作有标注
- 有预估收益说明