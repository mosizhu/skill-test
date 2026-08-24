# Oracle 技能通用测试用例集

> 适用于所有 Oracle 技能的通用测试场景，覆盖参数校验、异常处理、边界条件等。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 风险 |
|------|------|------|--------|------|
| TSK-CM-001 | 非法参数 | 反例 | P0 | 低 |
| TSK-CM-002 | 空结果处理 | 反例 | P0 | 低 |
| TSK-CM-003 | 数据库不可达 | 反例 | P0 | 低 |
| TSK-CM-004 | 权限不足 | 反例 | P0 | 低 |
| TSK-CM-005 | 多环境歧义 | 边界 | P1 | 低 |

---

test_id: TSK-CM-001
type: negative
skill: all
dimension: boundary
priority: P0
risk_level: low

## 测试目标

验证所有 skill 对非法参数的处理能力。

## 前置条件

- 无特殊要求

## 执行步骤

对每个 skill 分别执行以下测试:

### 测试 A: 缺少必要参数
1. 触发 skill，不传任何参数
2. 观察行为

### 测试 B: 参数类型错误
1. 传入 `instance_host` = 123（数字而非字符串）
2. 传入 `instance_host` = null
3. 观察行为

### 测试 C: 参数格式错误
1. 传入 `instance_host` = "host:port"（应为实例名）
2. 观察行为

## 预期结果

- 每个非法输入均被拒绝
- 错误信息包含:
  - 缺少的参数名称
  - 参数的正确类型
  - 示例值
- 不执行任何无效查询

## 通过标准

- 所有非法输入被正确拒绝
- 错误信息包含具体参数名和类型
- 无无效查询执行

---

test_id: TSK-CM-002
type: negative
skill: all
dimension: boundary
priority: P0
risk_level: low

## 测试目标

验证所有 skill 对空结果集的处理能力。

## 前置条件

- 无特殊要求

## 执行步骤

1. 对每个 skill，传入一个已知返回空结果的参数组合
2. 例如: `instance_host` = "oracle-rac_node01"，查询一个已知为空的视图
3. 观察 skill 行为

## 预期结果

- 空结果不导致 skill 崩溃
- 标注"暂无数据"
- 不影响其他维度的输出
- 不产生空行、null、占位符

## 通过标准

- 空结果处理优雅
- 无异常或错误
- 输出中明确标注"暂无数据"

---

test_id: TSK-CM-003
type: negative
skill: all
dimension: reliability
priority: P0
risk_level: low

## 测试目标

验证数据库不可达时的处理。

## 前置条件

- 无特殊要求

## 执行步骤

1. 通过 Mopheus 工单触发任一 skill
2. 传入不存在的实例名: `instance_host` = "nonexistent-99999"
3. 观察 skill 行为

## 预期结果

- 在连接建立阶段即拒绝执行
- 错误信息包含:
  - "连接失败"或"实例不存在"
  - 可用的实例列表
  - 可能的原因（如网络故障、实例宕机）
- 不尝试执行任何查询
- 有明确的恢复建议

## 通过标准

- 连接失败在早期被发现
- 错误信息包含可用实例列表
- 有恢复建议