---
test_id: TSK-CM-001
skill: all
dimension: boundary
priority: P2
risk_level: low
---

## 测试目标
验证所有 skill 对无效参数的处理。

## 前置条件
- 目标实例可达

## 执行步骤
对以下 skill 分别执行：
1. db-oracle-switchover：不传 approver_one/approver_two，不传 validate_only
2. db-oracle-backup：不传 backup_type
3. db-oracle-execute：传入空 SQL 文本
4. db-oracle-inspect：不传 instance_host
5. db-oracle-monitor-realtime：传入 metrics: invalid_metric_name

## 预期结果
通过标准：
- 所有 skill 拒绝执行并给出明确的错误提示
- 错误提示说明缺少或错误的具体参数
- 不执行任何数据库操作
- 不崩溃、不产生脏输出

## 备注
- 边界测试用例，不涉及真实数据库操作
- 验证 skill 的参数校验层是否健壮