---
test_id: TSK-PT-001
skill: db-oracle-plan-tuning
dimension: functional
priority: P1
risk_level: low
---

## 测试目标
验证 SQL 调优方案生成的质量。

## 前置条件
- 目标实例可访问
- 有已知慢 SQL（提供 SQL_ID）

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-plan-tuning skill
2. 传入 `sql_id`（已知慢 SQL 的 SQL_ID）
3. 传入 `instance_host`（目标实例）
4. 等待方案生成

## 预期结果
通过标准：
- 正确解析执行计划（访问路径、连接方式、过滤条件）
- 识别瓶颈：全表扫描、缺失索引、统计信息过期、不当的 Hint
- 给出至少 1 条具体优化建议（SQL 改写、索引创建、统计信息收集）
- 建议有可操作的具体 SQL（非笼统描述）
- 说明优化后的预期效果（预计提升比例）
- 输出结构化方案报告

## 备注
- 调优方案是只读的，不执行变更
- 如果 SQL 已是最优执行计划，应明确说明
- 建议应区分优先级（高/中/低）