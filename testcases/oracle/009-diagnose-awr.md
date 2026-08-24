---
test_id: TSK-DQ-004
skill: db-oracle-diagnose-awr
dimension: functional
priority: P1
risk_level: low
---

## 测试目标
验证 AWR 报告分析功能的正确性和深度。

## 前置条件
- 目标实例 AWR 快照已收集（DBMS_WORKLOAD_REPOSITORY）
- 至少存在一对快照

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-diagnose-awr skill
2. 传入 `instance_host`、`snap_id_begin`、`snap_id_end`
3. 传入 `instance_host`（目标实例）
4. 等待分析完成

## 预期结果
通过标准：
- 正确解析 Load Profile（每事务/每秒的统计）
- TOP 等待事件按类别分类（User I/O、Concurrency、Configuration 等）
- TOP SQL 按多维度排序（Elapsed Time、CPU Time、Buffer Gets、Disk Reads）
- 时间模型分解（DB Time 分布）
- 效率指标评估（Buffer Hit、Library Hit、Pin Hit 等）
- 给出性能瓶颈的根因分析
- 输出结构化报告，含表格和分类

## 备注
- 如果用户不提供 snap_id，skill 应自动选择最近的快照对
- AWR 数据可能大量，需注意超时处理
- 诊断超时 8 分钟应标记为超时