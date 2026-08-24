---
test_id: TSK-BK-001
skill: db-oracle-backup
dimension: functional
priority: P0
risk_level: low
---

## 测试目标
验证 RMAN 全量备份执行流程的正确性。

## 前置条件
- 数据库处于归档模式
- FRA 空间充足（> 80%）
- 目标实例可达

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-backup skill
2. 传入参数 `backup_type: full`、`backup_level: 0`
3. 传入 `instance_host`（目标实例）
4. 等待备份完成

## 预期结果
通过标准：
- RMAN 备份执行成功（FULL LEVEL 0）
- 输出备份集信息（handle、size、creation time）
- 备份校验通过（backup verify）
- 报告包含备份耗时、数据量
- 备份集在 v$backup_set 中可查
- 未执行 DDL/DML（仅备份操作）

## 备注
- 全量备份通常耗时较长（取决于数据量）
- 备份过程中不影响数据库正常使用
- 建议定期执行全量备份 + 增量备份策略