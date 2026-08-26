# Oracle Skill 测试用例设计模板（CASES.json）

本模板定义 db-oracle-* 技能测试用例的标准格式与设计规范。所有新 skill 的 CASES.json 必须遵循本模板。

## 文件位置
`testcases/oracle/<NN>-<skill-name>/CASES.json`

## 核心设计原则

1. **模拟真实用户场景**：`user_input` 必须是自然语言，模拟 DBA 真实提问方式，而非参数直填。
2. **覆盖每一种输出结果**：对 skill 的每个指标 × 每个阈值状态单独设计用例，通过用例覆盖反向暴露 skill 缺陷。
3. **环境无关**：用例定义与执行环境解耦。断言是条件逻辑判断（skill 输出 = 规则应用于实际值），而非固定状态。
4. **可构造性只是执行元数据**：`constructible_in_current_env` 只决定执行策略，不决定用例有效性。不可构造 ≠ 真实环境不存在。
5. **只提供用例，不提供环境构造**：环境构造由执行 agent 负责，用例只描述目标状态，不写 setup/rollback 构造 SQL。
6. **测试库即 Oracle**：不出现任何 OceanBase 兼容租户等非 Oracle 表述。

## 操作类型判定（自我优化）

生成前必须读取 SKILL.md 判定操作类型，据此选择设计重点：

| 操作类型 | 判定依据 | 用例设计重点 |
|---------|---------|-------------|
| query（查询/只读） | 仅 SELECT / v$ 视图，无 DML/DDL | 阈值判断逻辑、可构造 vs 不可构造状态、ground-truth 对比 |
| execute（执行/写） | 执行 DML/DDL/参数变更 | 安全拦截（危险 SQL 是否被拒）、变更是否真实生效、回滚验证、权限校验 |
| high-risk（高危变更） | switchover/restore/backup 等 DB 级操作 | 安全门禁、人工确认、变更前后状态验证、回滚 |
| audit（审计） | 审计 SQL/权限 | 权限边界、可见 vs 隐藏、安全合规 |

## 顶层结构
```json
[
  {
    "skill": "<技能标识>",
    "skill_version": "<生成时的技能版本>",
    "case_id": "<skill序号>-<序号>",
    "type": "positive|negative|boundary",
    "priority": "P0|P1|P2",
    "dimension": "<指标/功能维度>",
    "metric": "<具体指标>",
    "target_state": "<normal|warning|severe|...>",
    "judgment_rule": "<阈值判断规则>",
    "user_input": "<自然语言，模拟真实用户场景>",
    "params": { "<参数名>": "<值>" },
    "expected_output": {
      "target_judgment": "<目标判断>",
      "description": "<期望输出特征>"
    },
    "assertions": [
      {
        "name": "<断言名>",
        "ground_truth_sql": "<读取真实值的 SQL>",
        "logic": "<条件逻辑判断：skill 输出必须等于规则应用于实际值的结果>"
      }
    ],
    "constructible_in_current_env": true|false,
    "execution_note": "<执行策略说明，构造方式由执行 agent 决定>"
  }
]
```

## 用例类型与优先级
- **positive**（P0）：正常路径，验证核心功能完整执行。
- **negative**（P1）：非法输入/不可达主机/权限不足，验证拒绝与错误处理。
- **boundary**（P1/P2）：边界条件（超长、空、并发、阈值临界）。

## 参数契约
`params` 必须与 SKILL.md frontmatter 中声明的参数一致（名称、类型、必填）。`instance_host` 用 `oracle-rac_node01`（可达）或 `nonexistent-host-99999`（不可达，用于 negative 用例）。

## 断言设计
- 断言必须是**条件逻辑判断**：`ground_truth_sql` 读取真实值，`logic` 描述"skill 输出必须等于规则应用于实际值的结果"。
- **禁止** `SELECT 1 FROM dual WHERE 1=1` 假断言。
- **禁止**引用目标库不存在的视图/表（如 dba_tablespace_usage 会 ORA-00942）。
- 不可构造状态：标注 `constructible_in_current_env=false`，`execution_note` 说明"当前环境无法强制该状态，读取实际值验证判断逻辑；真实环境存在该状态时自动覆盖对应分支"。

## 环境构造
- 用例**不携带** setup/rollback 构造 SQL。
- 可构造状态（`constructible_in_current_env=true`）在 `execution_note` 中描述目标状态区间，由执行 agent 在 Run A 阶段自行构造环境。
- 高危用例（switchover/restore）必须标注 priority 并附人工确认要求。

## 示例用例
```json
{
  "skill": "db-oracle-<skill>",
  "skill_version": "v1.0.0",
  "case_id": "XX-001",
  "type": "positive",
  "priority": "P0",
  "dimension": "connection",
  "metric": "会话使用率",
  "target_state": "warning",
  "judgment_rule": "<60%→正常；60%-80%→警告；>80%→严重",
  "user_input": "查看172.20.23.95 Oracle数据库的会话使用率",
  "params": { "instance_host": "oracle-rac_node01", "metric_type": "connection" },
  "expected_output": {
    "target_judgment": "警告",
    "description": "当会话使用率处于警告状态时，skill 应输出'警告'判断"
  },
  "assertions": [
    {
      "name": "会话使用率-警告判断",
      "ground_truth_sql": "SELECT ROUND(COUNT(*)/(SELECT value FROM v$parameter WHERE name='sessions')*100,2) FROM v$session",
      "logic": "skill 报告的 judgment 必须等于 judgment_rule 应用于实际采集 value 的结果"
    }
  ],
  "constructible_in_current_env": true,
  "execution_note": "执行 agent 构造会话使会话使用率进入警告区间后验证目标分支；构造方式由执行 agent 决定。"
}
```
