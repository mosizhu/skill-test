---
test_id: TSK-PB-001
skill: db-oracle-plan-backup
dimension: functional
priority: P2
risk_level: low
---

## 测试目标
验证 RMAN 备份策略设计功能的正确性。

## 前置条件
- 目标实例信息可获取（数据量、表空间等）

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-plan-backup skill
2. 传入 `instance_host`（目标实例）
3. 传入 `rpo_hours: 4`（恢复点目标，小时）
4. 传入 `rto_minutes: 30`（恢复时间目标，分钟）
5. 等待方案设计

## 预期结果
通过标准：
- 根据 RPO/RTO 自动选择备份类型和频率
- 输出完整的备份策略（全量/增量/归档日志备份计划）
- 包含备份保留策略（Retention Policy）
- 备份目标配置建议（FRA/磁盘/磁带）
- 包含备份校验和恢复测试建议
- 输出结构化方案报告

## 备注
- 备份策略设计是只读的
- 策略应基于实际数据库规模调整（小库和大库策略不同）
- 建议包含 RMAN CONFIGURE 命令示例