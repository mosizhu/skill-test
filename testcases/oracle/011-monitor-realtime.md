---
test_id: TSK-MN-001
skill: db-oracle-monitor-realtime
dimension: functional
priority: P1
risk_level: low
---

## 测试目标
验证 Oracle 实时指标监控的准确性和时效性。

## 前置条件
- 目标实例运行中
- 可访问 v$ 动态视图

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-monitor-realtime skill
2. 传入 `instance_host`（目标实例）
3. 传入 `metrics: cpu,connections,session,sql_count`
4. 等待采集完成

## 预期结果
通过标准：
- CPU 监控：OS 级 CPU 使用率、DB CPU 占比准确
- 连接数监控：当前会话数、各状态会话分布
- 慢查询数：当前活跃查询数、等待事件分布
- 输出包含实时数值 + 阈值告警（如有）
- 响应时间在合理范围（秒级）
- 数据格式结构化（JSON 或表格）

## 备注
- 实时监控类 skill 响应应快于其他诊断类
- 如果指标超过阈值，应给出告警级别标注
- 多次连续采集应能输出趋势对比