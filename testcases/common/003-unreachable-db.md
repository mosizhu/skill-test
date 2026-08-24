---
test_id: TSK-CM-003
skill: all
dimension: reliability
priority: P1
risk_level: low
---

## 测试目标
验证 skill 在数据库不可达时的表现。

## 前置条件
- 准备一个不可达的实例地址（如错误的 host/port）

## 执行步骤
对以下 skill 传入不可达的 `instance_host`：
1. db-oracle-inspect
2. db-oracle-monitor-realtime
3. db-oracle-backup
4. db-oracle-execute
5. db-oracle-diagnose-slow-query

## 预期结果
通过标准：
- 立即或快速返回连接失败
- 错误信息说明连接失败原因（主机不可达/端口拒绝/超时）
- 不重试无限次（应有重试上限）
- 不挂起或超时过久（超时阈值内返回）

## 备注
- 连接失败是高频场景（测试/生产切换、网络抖动）
- 应区分"连接失败"和"查询无结果"