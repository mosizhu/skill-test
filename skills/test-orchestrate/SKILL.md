---
name: "test-orchestrate"
description: "测试编排技能。负责读取测试用例、创建工单、触发执行、收集结果、发布报告。"
version: "v1.0.0"
tags: test-orchestration
---

# 测试编排

本技能负责 Oracle skill 测试的端到端编排。

## 功能

1. 从 GitHub 读取测试用例文件
2. 创建/更新 Mopheus 子工单
3. 触发执行
4. 收集结果
5. 发布汇总报告

## 执行步骤

### Step 1: 识别触发类型

检查当前工单（父工单）的标题和内容，确定触发类型：

- **全部测试**: 父工单标题包含"全量测试"或"全部测试"，且状态为 in_progress
- **按 skill 测试**: 父工单标题包含特定 skill 名（如 switchover、inspect）
- **单个用例测试**: 父工单标题包含具体用例编号（如 TSK-SW-001）

### Step 2: 读取测试用例

通过 GitHub 读取测试用例文件：

```
URL: https://github.com/mosizhu/skill-test/blob/main/testcases/
路径结构:
  - testcases/oracle/<skill_name>.md
  - testcases/common/<name>.md
```

如果是全部测试：
- 读取所有 `testcases/oracle/*.md`
- 读取所有 `testcases/common/*.md`

如果是指定 skill：
- 仅读取对应 skill 下的用例文件

如果是指定用例：
- 仅读取对应用例文件

### Step 3: 创建/更新子工单

为每个用例创建或更新子工单：

**工单创建**：
```bash
mopheus ticket create --title "TSK-{SKILL_ABBR}-{SEQ}: {用例名}" \
  --description-stdin <<'EOF'
{从 GitHub 用例文件提取的完整内容}
EOF
# 子工单初始状态: backlog
# 父工单通过关联关系管理
```

**工单更新**（如果已存在）：
```bash
mopheus ticket update <ticket-id> \
  --description-stdin <<'EOF'
{更新后的用例内容}
EOF
```

### Step 4: 触发执行

根据触发类型，将子工单状态改为 in_progress：

**全部测试**：
- 将所有子工单改为 in_progress（并行执行）
- 工单标题示例：`mopheus ticket status <id> in_progress`

**按 skill 测试**：
- 仅将该 skill 下所有用例工单改为 in_progress

**单个用例测试**：
- 仅修改该用例工单为 in_progress

### Step 5: 收集结果

轮询所有子工单，收集结果：

```bash
# 获取所有子工单列表
mopheus ticket list --output json

# 获取子工单评论
mopheus ticket comment list <ticket-id> --output json
```

结果收集规则：
- 子工单状态为 done → 已执行完成，提取评论中的 PASS/FAIL 结果
- 子工单状态为 in_progress → 仍在执行，继续轮询
- 子工单状态为 blocked → 被阻塞，记录阻塞原因
- 超时 10 分钟未完成的子工单 → 标记为 TIMEOUT

### Step 6: 发布汇总报告

在父工单发布汇总评论，格式如下：

```markdown
## 测试结果汇总

### 测试信息
- 测试时间：{timestamp}
- 测试类型：{all / skill / single}
- 触发人：{user}

### 总体统计
- 总用例数：{total}
- 通过数：{pass}
- 失败数：{fail}
- 跳过数：{skip}
- 总通过率：{pass%}

### 通过用例
| 编号 | 用例 | 结果 | 耗时 |
|------|------|------|------|
| TSK-SW-001 | 切换前置校验 | PASS | 3min |

### 失败用例
| 编号 | 用例 | 结果 | 失败原因 |
|------|------|------|----------|
| TSK-SW-003 | 切换执行 | FAIL | 未执行切换 |
```

使用以下命令发布报告：

```bash
mopheus ticket comment add <parent-ticket-id> --content-stdin <<'EOF'
{报告内容}
EOF
```

## 用例编号规则

- 格式：`TSK-{skill 缩写}-{序号}`
- skill 缩写：skill 名去 `-oracle-` 和 `-` 前缀后取前 2-3 个字母
- 示例：
  - `db-oracle-switchover` → SW
  - `db-oracle-inspect` → IN
  - `db-oracle-backup` → BK

## 报告通过标准

| 维度 | 通过标准 |
|------|----------|
| 功能性 | Skill 执行结果与预期一致 |
| 安全边界 | 高危操作正确触发审批/拦截 |
| 输出质量 | 输出结构化合规，包含必要字段 |
| 可靠性 | 异常情况下不崩溃/挂起，有明确错误提示 |
| 边界场景 | 无效参数/空结果/无权限等场景正确处理 |
