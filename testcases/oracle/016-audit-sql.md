---
test_id: TSK-AS-001
skill: db-oracle-audit-sql
dimension: functional
priority: P1
risk_level: low
---

## 测试目标
验证 SQL 审核功能的覆盖度和准确性。

## 前置条件
- 目标实例可访问
- 有可审核的 SQL 文本（提供 SQL 列表）

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-audit-sql skill
2. 传入 `audit_scope: all`（规范性 + 性能 + 安全）
3. 传入 SQL 文本列表或 SQL_ID
4. 传入 `instance_host`（目标实例）
5. 等待审核完成

## 预期结果
通过标准：
- 规范性审核：检查命名规范、SELECT *、隐式类型转换、列上函数、缺失 WHERE、字段类型选型
- 性能审核：检查索引使用、执行计划合理性、全表扫描
- 安全审核：检查 SQL 注入风险、硬编码值、敏感字段访问
- 每条 SQL 的审核结果明确标注通过/警告/阻断
- 给出具体修复建议（非笼统描述）
- 输出结构化审核报告

## 备注
- 审核是只读操作
- 审核标准应可配置（不同团队可能有不同规范）
- 严重等级应区分：建议/警告/阻断