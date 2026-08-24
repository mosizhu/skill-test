---
test_id: TSK-SW-002
skill: db-oracle-switchover
dimension: security
priority: P0
risk_level: high
---

## 测试目标
验证 DataGuard 主备切换的实际执行流程，包括双签门禁和切换后验证。

## 前置条件
- 已配置 DataGuard 主备环境
- 前置校验用例（TSK-SW-001）已通过
- 双签审批人已确认

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-switchover skill
2. 传入参数 `validate_only: false`
3. 传入有效的 `approver_one` 和 `approver_two`
4. 确认双签通过
5. 等待切换完成

## 预期结果
通过标准：
- 双签完整时才能执行切换（approver_one 和 approver_two 均非空且不同）
- 切换执行后，原主库变为备库（PHYSICAL STANDBY），原备库变为主库（PRIMARY）
- 新主库处于 READ WRITE 状态
- 新备库 MRP 正常运行
- 归档传输恢复正常
- 输出切换前后状态对比表（角色/SCN/同步状态）
- 包含切换耗时、各步骤状态的时间线

## 备注
- 这是不可逆操作，切换后如需回退需执行反向 SWITCHOVER
- 切换过程中数据库不可提供服务（短暂中断）
- 建议在低峰时段执行