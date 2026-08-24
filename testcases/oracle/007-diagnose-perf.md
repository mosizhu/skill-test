---
test_id: TSK-DQ-002
skill: db-oracle-diagnose-perf
dimension: functional
priority: P1
risk_level: low
---

## 测试目标
验证 Oracle 综合性能诊断（CPU/IO/锁）的完整性和输出质量。

## 前置条件
- 目标实例运行中
- 可访问 v$ 视图和 AWR 历史数据

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-diagnose-perf skill
2. 传入 `instance_host`（目标实例）
3. 等待诊断完成

## 预期结果
通过标准：
- 包含三个维度：CPU 诊断、IO 诊断、锁诊断
- CPU 诊断：实例 CPU 使用率、DB CPU 时间占比、TOP CPU SQL
- IO 诊断：物理读/写命中率、temp 文件使用、ioseek 指标
- 锁诊断：当前阻塞会话数、长时间持有锁的会话、锁等待链
- 输出性能基线评估（与历史对比）
- 给出优化建议

## 备注
- 诊断类只读操作，风险低
- 输出应结构化，便于下游消费
- 诊断超时 10 分钟应标记为超时