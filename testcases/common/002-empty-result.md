---
test_id: TSK-CM-002
skill: all
dimension: reliability
priority: P1
risk_level: low
---

## 测试目标
验证 skill 在目标实例无数据时的空结果处理。

## 前置条件
- 目标实例可达

## 执行步骤
1. 对 db-oracle-diagnose-deadlock：在无死锁环境下触发
2. 对 db-oracle-diagnose-slow-query：在空闲数据库触发（无慢查询）
3. 对 db-oracle-monitor-anomaly：在无异常数据的环境中触发
4. 对 db-oracle-audit-sql：传入不存在的 SQL_ID

## 预期结果
通过标准：
- 返回空结果但明确说明"无异常/无数据"
- 不返回错误码或异常堆栈
- 不返回空字符串（应有有意义的输出）
- 不崩溃或挂起

## 备注
- 空结果是合法输出，skill 应优雅处理
- 空结果应区别于"执行失败"