# Oracle 死锁诊断 (db-oracle-diagnose-deadlock) 测试用例集

> 验证死锁检测的及时性、根因分析的准确性和恢复建议的有效性。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 风险 |
|------|------|------|--------|------|
| TSK-DL-001 | 死锁检测 | 正例 | P0 | 低 |
| TSK-DL-002 | 根因分析 | 正例 | P0 | 低 |
| TSK-DL-003 | 恢复建议 | 正例 | P0 | 低 |
| TSK-DL-004 | 无死锁场景 | 反例 | P1 | 低 |
| TSK-DL-005 | 历史死锁 | 边界 | P1 | 低 |
| TSK-DL-006 | 循环死锁 | 边界 | P1 | 低 |

---

test_id: TSK-DL-001
type: positive
skill: db-oracle-diagnose-deadlock
dimension: functional
priority: P0
risk_level: low

## 测试目标

验证死锁检测的及时性和准确性。

## 前置条件

- oracle-rac_node01 实例运行正常
- 存在活跃事务

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-diagnose-deadlock` skill
2. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `check_mode` = `realtime`（实时检测）
   - `check_interval` = `5`（每 5 秒检查一次）
3. 观察 skill 对当前死锁状态的分析

## 预期结果

### 输出格式

```
## 死锁诊断报告
### 检测结果
| 属性 | 值 |
|------|------|
| 检测时间 | 2026-08-24 10:00:00 |
| 死锁状态 | 存在 / 不存在 |
| 活跃事务数 | N |
| 阻塞会话数 | M |

### 详细信息（存在死锁时）
| 会话 | SID | 用户 | 阻塞对象 | 等待事件 |
|------|-----|------|----------|----------|
| SID1 | 123 | user1 | table_A | enq: TX - row lock contention |
| SID2 | 456 | user2 | table_B | enq: TX - row lock contention |

### 根因分析
- **触发条件**: 两个会话互相锁定对方需要的资源
- **触发时间**: 时间
- **影响范围**: 受影响的业务系统
- **根因类型**: 开发缺陷 / 锁争用 / 长事务

### 处理建议
1. [紧急] 终止阻塞会话 SID123 或 SID456
2. [高] 优化应用逻辑，减少并发更新
3. [中] 添加超时机制，避免无限等待
```

## 通过标准

- 检测结果准确（存在死锁则报告，不存在则说明）
- 如有死锁，至少列出 2 个会话的 SID 和用户
- 根因分析有明确的触发条件说明
- 处理建议分紧急程度

---

test_id: TSK-DL-002
type: positive
skill: db-oracle-diagnose-deadlock
dimension: functional
priority: P0
risk_level: low

## 测试目标

验证死锁根因分析的深度和准确性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-diagnose-deadlock` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 验证根因分析:
   a) 是否识别出阻塞链（谁阻塞谁）
   b) 是否列出涉及的表和操作
   c) 是否分析锁等待时间
   d) 是否分析锁等待队列长度

## 预期结果

- 阻塞链描述清晰（A 阻塞 B，B 阻塞 A）
- 涉及的表和操作有具体说明
- 锁等待时间精确到秒
- 锁等待队列长度

## 通过标准

- 阻塞链完整描述
- 涉及对象有具体说明
- 等待时间精确