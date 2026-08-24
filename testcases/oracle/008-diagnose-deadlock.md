---
test_id: TSK-DQ-003
skill: db-oracle-diagnose-deadlock
dimension: functional
priority: P2
risk_level: low
---

## 测试目标
验证 Oracle 死锁分析功能的正确性。

## 前置条件
- 目标实例可访问
- 存在 v$LOCK、v$SESSION 视图权限
- （可选）存在正在发生的死锁

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-diagnose-deadlock skill
2. 传入 `instance_host`（目标实例）
3. 等待诊断完成

## 预期结果
通过标准：
- 能识别当前活跃的死锁（如果存在）
- 输出死锁会话详情：会话ID、进程ID、锁定对象、等待对象
- 输出死锁 trace 文件位置和内容摘要
- 给出解决建议（哪个会话应被终止）
- 若无死锁，返回空结果并明确说明（而非报错）

## 备注
- 死锁诊断是只读的，但建议可能涉及 kill session
- 无死锁时的空结果也是有效结果
- 应检查 alert log 中的 ORA-00060