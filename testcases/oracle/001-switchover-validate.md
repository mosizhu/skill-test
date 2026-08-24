---
test_id: TSK-SW-001
skill: db-oracle-switchover
dimension: security
priority: P0
risk_level: high
---

## 测试目标
验证 DataGuard 主备切换的前置校验门禁是否正常触发，校验链是否完整。

## 前置条件
- 已配置 DataGuard 主备环境（主库 + 1 个物理备库）
- 备库处于 MRP 应用状态
- 网络可达，swissql 连接配置正确

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-switchover skill
2. 传入参数 `validate_only: true`、`switchover_type: validate`
3. 传入有效的 `approver_one` 和 `approver_two`（非空且不同）
4. 传入有效的 `instance_host`（主库）和 `standby_host`（备库）

## 预期结果
通过标准：
- Skill 执行完整的前置校验链：DG 配置状态、同步延迟、归档连续性、SRL 配置、FRA 空间、数据文件一致性、监听可达性
- 所有检查项均有明确的 PASS/FAIL/WARN 标注
- 校验报告包含具体数值（SCN 差距、延迟秒数、使用率百分比等）
- 未执行任何切换操作（仅校验模式）
- 双签信息在报告中正确展示
- 校验结果中至少包含 8 项子检查

## 备注
- 此用例不执行实际切换，仅验证校验逻辑
- 校验通过后输出结构化报告即视为通过