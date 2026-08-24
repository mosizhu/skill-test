---
test_id: TSK-EX-001
skill: db-oracle-execute
dimension: functional
priority: P0
risk_level: medium
---

## 测试目标
验证 DDL/DML 执行流程的正确性和自动回滚能力。

## 前置条件
- 目标实例可达
- 测试用表空间可用

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-execute skill
2. 传入 `execute_type: ddl`，SQL 为 `CREATE TABLE test_skill (id NUMBER, name VARCHAR2(100))`
3. 传入 `instance_host`（目标实例）
4. 等待执行完成
5. 再次触发，传入 `execute_type: dml`，SQL 为 `INSERT INTO test_skill VALUES (1, 'test')`
6. 触发 `rollback: true`，执行回滚

## 预期结果
通过标准：
- DDL 执行成功，表创建完成
- DML 执行成功，数据插入
- 回滚执行成功，数据被清除
- 输出执行前后的状态对比
- 每条 SQL 的执行结果可追溯
- 包含执行耗时、影响行数

## 备注
- 自动回滚仅对可回滚的操作有效（DML）
- DDL（如 DROP TABLE）不可回滚，需提前确认
- 高危 DDL（DROP TABLESPACE、ALTER SYSTEM）需要额外确认