---
test_id: TSK-PM-001
skill: db-oracle-plan-migration
dimension: functional
priority: P2
risk_level: low
---

## 测试目标
验证数据库迁移方案设计功能的完整性。

## 前置条件
- 源端和目标端实例信息可获取
- 目标环境已准备（可选，skill 可基于假设生成方案）

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-plan-migration skill
2. 传入 `source_host`（源库）、`target_host`（目标库，可选）
3. 传入 `migration_type: cross_version` 或 `cross_platform`
4. 传入 `tablespace_list`（指定迁移范围，可选）
5. 等待方案生成

## 预期结果
通过标准：
- 自动发现源库对象清单（表、索引、视图、存储过程等）
- 数据量统计（按表空间、按 schema）
- 迁移方式选型（Data Pump、GoldenGate、DB Links、RMAN）
- 迁移步骤的时序规划
- 风险评估和回退方案
- 停机时间预估
- 输出结构化方案报告

## 备注
- 迁移方案设计是只读的，不执行实际迁移
- 如果目标端不可访问，基于假设生成方案并标注
- 方案应覆盖所有迁移类型：同版本/跨版本/同平台/跨平台