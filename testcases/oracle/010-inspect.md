---
test_id: TSK-IN-001
skill: db-oracle-inspect
dimension: functional
priority: P0
risk_level: low
---

## 测试目标
验证 Oracle 数据库健康巡检的完整性和结构化输出。

## 前置条件
- 目标实例运行正常
- 有各维度查询所需权限

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-inspect skill
2. 传入 `instance_host`（目标实例，使用 test1 环境）
3. 等待巡检完成

## 预期结果
通过标准：
- 覆盖五大维度：实例信息、主机健康、空间资源、性能分析、备份容灾
- 实例信息：版本、运行时间、归档模式、字符集
- 主机健康：CPU、内存、磁盘
- 空间资源：表空间使用率、自动扩展配置、离线表空间
- 性能分析：性能基线、等待事件 TOP N
- 备份容灾：RMAN 备份状态、DG 同步
- 输出整体健康评分或评级
- 异常项有明确标注和严重程度
- 输出结构化，非纯文本

---

test_id: TSK-IN-002
skill: db-oracle-inspect
dimension: boundary
priority: P1
risk_level: low
---

## 测试目标
验证 inspect 对非法参数的处理。

## 前置条件
- 无特殊要求

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-inspect skill
2. 传入不存在的实例名或连接串

## 预期结果
通过标准：
- Skill 明确拒绝执行
- 说明实例不存在或无法连接
- 不产生任何无效查询
- 错误信息清晰可操作

---

test_id: TSK-IN-003
skill: db-oracle-inspect
dimension: functional
priority: P1
risk_level: low
---

## 测试目标
验证 inspect 在 test 账户权限受限情况下的降级行为。

## 前置条件
- test 账户无法访问 v$database.VERSION、v$parameter 等系统视图

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-inspect skill
2. 使用 test 账户访问的 profile（oracle-rac_node01）
3. 观察部分系统视图查询失败时的行为

## 预期结果
通过标准：
- 可查询的维度正常输出
- 不可查询的维度标注"权限不足，跳过"
- 不因部分查询失败而中断整个巡检
- 输出中清晰标注哪些维度因权限缺失而省略
- 整体健康评分仅基于可获取的维度

---

test_id: TSK-IN-004
skill: db-oracle-inspect
dimension: boundary
priority: P2
risk_level: low
---

## 测试目标
验证 inspect 对空结果/异常数据容错。

## 前置条件
- 目标实例中某些视图可能返回空数据

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-inspect skill
2. 使用 test1 环境正常执行巡检
3. 关注返回空结果的维度处理

## 预期结果
通过标准：
- 空结果不导致技能崩溃
- 空结果标注"暂无数据"而非留空
- 不影响其他维度的输出
- 不产生误导性空行或占位符

---

test_id: TSK-IN-005
skill: db-oracle-inspect
dimension: reliability
priority: P2
risk_level: low
---

## 测试目标
验证 inspect 输出格式的一致性和可读性。

## 前置条件
- 正常执行巡检

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-inspect skill
2. 执行一次完整巡检
3. 对比输出格式是否符合规范

## 预期结果
通过标准：
- 各维度有明确的标题分隔
- 表格数据对齐，无错位
- 关键指标（表空间使用率、会话数）有数值和百分比
- 无纯 SQL 输出直接暴露给用户
- 有摘要/结论段落
- 异常项用颜色或符号标注（如 ⚠️）