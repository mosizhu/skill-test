---
test_id: TSK-DQ-001
skill: db-oracle-diagnose-slow-query
dimension: functional
priority: P1
risk_level: low
---

## 测试目标
验证慢查询诊断 TOP N 功能的正确性和输出质量。

## 前置条件
- 目标实例正在运行，有活跃查询
- 存在 AWR 快照或 v$ 视图可访问

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-diagnose-slow-query skill
2. 传入 `top_n: 5`（取 TOP 5 慢 SQL）
3. 传入 `instance_host`（目标实例）
4. 等待诊断完成

## 预期结果
通过标准：
- 正确识别 TOP N 慢 SQL（按 elapsed time 排序）
- 每条慢 SQL 包含：SQL_ID、执行次数、平均耗时、SQL 文本（脱敏）
- 包含执行计划分析（访问路径、连接方式）
- 给出优化建议（索引、SQL 改写、统计信息）
- 输出结构化报告，非纯文本描述

## 备注
- 诊断类只读操作，风险低
- 如果目标实例无慢查询，应返回空结果集而非报错
- AWR 快照需存在，无快照时尝试从 v$ 视图采集