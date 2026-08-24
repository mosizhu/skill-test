# Oracle 异常监控 (db-oracle-monitor-anomaly) 测试用例集

> 验证异常检测的灵敏度、准确率和误报率控制。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 风险 |
|------|------|------|--------|------|
| TSK-MA-001 | 已知异常检测 | 正例 | P0 | 低 |
| TSK-MA-002 | 无异常确认 | 正例 | P0 | 低 |
| TSK-MA-003 | 误报控制 | 正例 | P0 | 低 |
| TSK-MA-004 | 异常参数 | 反例 | P1 | 低 |
| TSK-MA-005 | 阈值自适应 | 边界 | P1 | 低 |
| TSK-MA-006 | 多异常同时 | 边界 | P1 | 低 |

---

test_id: TSK-MA-001
type: positive
skill: db-oracle-monitor-anomaly
dimension: functional
priority: P0
risk_level: low

## 测试目标

验证对已知异常的准确检测。

## 前置条件

- oracle-rac_node01 实例运行正常
- 存在可检测的异常条件

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-monitor-anomaly` skill
2. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `anomaly_types` = `all`（检测所有类型异常）
   - `sensitivity` = `standard`
3. 等待检测完成

## 预期结果

### 输出格式

```
## 异常检测报告
### 检测概览
| 属性 | 值 |
|------|------|
| 检测时间 | 2026-08-24 10:00:00 |
| 检测范围 | CPU, 内存, 会话, 等待事件, 表空间, IO |
| 异常总数 | N |

### 异常详情
#### 异常 #1
- **ID**: ANOMALY-001
- **类型**: 表空间
- **等级**: CRITICAL
- **描述**: SYSTEM 表空间使用率 99.94%
- **影响**: 可能导致数据库不可用
- **检测时间**: 2026-08-24 10:00:00
- **持续时间**: 已持续 24 小时
- **建议**: 立即扩容 SYSTEM 表空间

#### 异常 #2
- **ID**: ANOMALY-002
- **类型**: 会话
- **等级**: WARNING
- **描述**: 活跃会话数 91，接近上限
- **影响**: 可能影响新用户连接
- **检测时间**: 2026-08-24 10:00:00
- **建议**: 优化长会话，考虑增加 sessions 参数
```

## 通过标准

- 所有已知异常均被检测
- 异常等级正确（CRITICAL/WARNING/INFO）
- 异常有唯一 ID
- 每条异常有建议措施
- 异常按严重程度排序

---

test_id: TSK-MA-002
type: positive
skill: db-oracle-monitor-anomaly
dimension: functional
priority: P0
risk_level: low

## 测试目标

验证正常状态下不误报。

## 前置条件

- oracle-rac_node01 实例运行正常，各项指标正常

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-monitor-anomaly` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 观察检测输出

## 预期结果

- 无异常时输出:
```
## 异常检测报告
### 检测结果
| 属性 | 值 |
|------|------|
| 检测时间 | 2026-08-24 10:00:00 |
| 异常总数 | 0 |
| 检测状态 | 正常 |

无异常检测。
```

## 通过标准

- 正常状态下不产生误报
- 输出明确说明"无异常"
- 有检测时间戳
- 有检测范围说明

---

test_id: TSK-MA-003
type: positive
skill: db-oracle-monitor-anomaly
dimension: quality
priority: P0
risk_level: low

## 测试目标

验证异常检测的误报率控制。

## 前置条件

- oracle-rac_node01 实例运行正常
- 各项指标在正常范围内（CPU < 80%, 会话数 < 50% 上限）

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-monitor-anomaly` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 检查各项指标:
   a) CPU 使用率 < 80%（正常）
   b) 会话数 < 50% 上限（正常）
   c) 表空间空闲率 > 10%（正常）
   d) 等待事件无异常
4. 观察是否误报

## 预期结果

- 正常指标不产生异常
- 仅在真正异常时报告
- 不将正常波动标记为异常

## 通过标准

- 误报率为 0
- 正常指标不产生异常
- 异常检测准确（仅在真正异常时报告）

---

test_id: TSK-MA-004
type: negative
skill: db-oracle-monitor-anomaly
dimension: boundary
priority: P1
risk_level: low

## 测试目标

验证非法参数输入的处理。

## 前置条件

- 无特殊要求

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-monitor-anomaly` skill
2. 传入非法参数:
   - 情况 A: `anomaly_types` = `invalid_type`
   - 情况 B: `sensitivity` = `invalid_level`
3. 观察 skill 行为

## 预期结果

- 非法参数被拒绝
- 错误信息包含合法的参数值列表
- 不执行任何查询

## 通过标准

- 非法参数被拒绝
- 错误信息包含合法值列表