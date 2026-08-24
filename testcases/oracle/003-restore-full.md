---
test_id: TSK-RE-001
skill: db-oracle-restore
dimension: security
priority: P0
risk_level: high
---

## 测试目标
验证 RMAN 全量恢复的前置校验和双签门禁。

## 前置条件
- 数据库处于归档模式
- 存在可用的 RMAN 备份集
- 备库可访问备份目标

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-restore skill
2. 传入参数 `restore_type: full`、`validate_only: true`
3. 传入有效的 `approver_one` 和 `approver_two`
4. 传入目标实例的 `instance_host`

## 预期结果
通过标准：
- 前置校验检查备份集可用性、备份时间、备份一致性
- 双签信息在报告中正确展示
- 未执行任何恢复操作（仅校验模式）
- 报告包含备份集时间线、可恢复到的最新时间点
- 明确指出恢复后可能的数据丢失范围

## 备注
- RMAN 恢复是高危不可逆操作
- 校验模式下不实际执行 restore/recover
- 实际执行需 `validate_only: false` 且双签通过