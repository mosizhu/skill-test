---
test_id: TSK-CM-004
skill: all
dimension: boundary
priority: P2
risk_level: low
---

## 测试目标
验证 skill 在权限不足时的错误提示。

## 前置条件
- 准备一个低权限账户（无 v$ 视图权限、无 DBA 权限）

## 执行步骤
对以下 skill 使用低权限账户：
1. db-oracle-inspect（需查询 v$ 视图）
2. db-oracle-audit-permission（需查询 dba_* 视图）
3. db-oracle-diagnose-awr（需访问 AWR 视图）
4. db-oracle-execute（需 DDL 权限）

## 预期结果
通过标准：
- 返回明确的权限不足错误
- 说明缺少哪些具体权限
- 不产生部分结果（如果关键步骤因权限失败，不应返回不完整结果）

## 备注
- 权限不足是常见场景，应提前检测并告知
- 建议 skill 在开始前先检测必要权限