# Mopheus Skill Test Suite

Oracle 出厂预置 Skill 的测试用例仓库。所有测试在真实 Oracle 环境中执行，覆盖功能性、输出质量、安全边界、可靠性等维度。

## 测试维度

| 维度 | 说明 | 优先级 |
|------|------|--------|
| 功能性 | Skill 能否按设计正确执行核心流程 | P0 |
| 安全边界 | 高危操作是否正确触发审批、拦截越权行为 | P0 |
| 输出质量 | 返回结果的准确性、完整性、结构化程度 | P1 |
| 可靠性 | 断连/超时/异常输入时的容错表现 | P1 |
| 人机协作 | 高危操作的双签/确认流程质量 | P2 |
| 边界场景 | 空参数/空结果/无权限/环境歧义等异常 | P2 |
| 可追溯性 | 操作记录、时间戳、前后状态对比 | P3 |
| 响应时效 | 是否在超时阈值内返回 | P3 |
| 资源效率 | 查询效率、数据库负载影响 | P3 |

## 仓库结构

```
testcases/
├── oracle/          # Oracle 功能测试用例（按 skill 分组）
└── common/          # 通用异常/边界测试用例（跨 skill）
suites/              # 测试套件定义（冒烟/全量/回归）
results/             # 测试结果归档
```

## 测试用例格式

每个 `.md` 文件包含一个测试用例，标准结构：

```markdown
---
test_id: TSK-XXX
skill: db-oracle-xxx
dimension: functional | security | quality | reliability
priority: P0 | P1 | P2 | P3
risk_level: low | medium | high (dangerous ops)
---

## 测试目标
...

## 前置条件
...

## 执行步骤
...

## 预期结果
通过标准：
- ...

## 备注
...
```

## 执行流程

1. 从 suites 中选择要运行的测试套件
2. 按顺序执行测试用例（高危用例需人工确认）
3. 将执行结果回填到对应工单
4. 通过 `mopheus ticket comment add` 更新测试状态

## 当前范围

- Oracle 出厂预置 Skill：16 个
- Kingbase Skill：20+ 个（后续接入）
- 通用 Skill：grillme / prometheus / database-diagnosis-verification 等（后续接入）