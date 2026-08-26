#!/usr/bin/env python3
"""Transform CASES.json: replace trivial `SELECT 1 FROM dual` assertions with
content checks on a per-case SKILL_OUTPUT_<CASE> capture table, and add an
evidence-capture requirement so Run A persists the skill's real output.

Design:
- setup: create SKILL_OUTPUT_<CASE> (output_text CLOB) for the executor to
  insert the skill's actual output into.
- rollback: drop that table.
- evidence: instruction telling Run A to capture the skill's real output into
  the table AND write it to the ticket comment (transparency / item 3).
- assertions: each trivial dual check becomes
  SELECT COUNT(*) FROM SKILL_OUTPUT_<CASE> WHERE INSTR(output_text,'<marker>')>0
  expected c >= 1  (validates the real output contains the expected marker).
"""

import json, glob, re, sys

# Map each unique `expected` description to a marker keyword that the skill's
# real output is expected to contain. Markers are chosen from the SKILL.md
# output-format sections so they are stable across the skill's report.
MARKER = {
    "pass_criteria_met: 风险等级明确": "风险等级",
    "pass_criteria_met: 所有建议可执行": "建议",
    "pass_criteria_met: 有明确的操作步骤": "步骤",
    "pass_criteria_met: 高风险操作有标注": "高风险",
    "pass_criteria_met: 双签信息完整展示": "双签",
    "pass_criteria_met: 未执行任何恢复命令": "未执行",
    "pass_criteria_met: 错误信息包含具体原因": "原因",
    "pass_criteria_met: 非法参数被拒绝": "非法",
    "pass_criteria_met: 给出清晰的错误说明": "错误",
    "pass_criteria_met: 优化建议有效": "优化建议",
    "pass_criteria_met: 未执行任何切换命令": "未执行",
    "pass_criteria_met: 有摘要/结论段落": "结论",
    "pass_criteria_met: 返回明确的连接失败错误提示": "连接失败",
    "pass_criteria_met: 不暴露底层异常栈": "异常",
    "pass_criteria_met: 数据库可达": "可达",
    "pass_criteria_met: 连接失败并提示主机不可达": "不可达",
    "pass_criteria_met: 未生成备份策略": "备份策略",
    "pass_criteria_met: 有检测时间戳": "时间戳",
    "pass_criteria_met: 有检测范围说明": "范围",
    "pass_criteria_met: 错误信息包含合法值列表": "合法",
    "pass_criteria_met: 无 SQL 执行": "未执行",
    "pass_criteria_met: 嵌套结构正确识别": "嵌套",
    "pass_criteria_met: 每层有统计信息": "统计",
    "pass_criteria_met: 未生成迁移方案": "迁移方案",
    "pass_criteria_met: 不产出审核报告": "审核",
    "pass_criteria_met: 明确提示 approver_one 缺失，需双人审批": "approver_one",
    "pass_criteria_met: 明确提示 instance_host 不可达，连接失败": "不可达",
    "pass_criteria_met: 所有五个维度均有输出": "维度",
    "pass_criteria_met: 等待事件至少列出 TOP 5": "等待事件",
    "pass_criteria_met: 有明确的问题清单": "问题",
    "pass_criteria_met: 所有数值指标与直接查询误差 <= 0.01%": "误差",
    "pass_criteria_met: Skill 拒绝执行": "拒绝",
    "pass_criteria_met: 错误信息包含具体原因和可用实例列表": "原因",
    "pass_criteria_met: 可获取维度正常输出": "维度",
    "pass_criteria_met: 不可获取维度标注\"暂无数据\"": "暂无数据",
    "pass_criteria_met: 权限缺失不中断巡检": "权限",
    "pass_criteria_met: 降级行为清晰标注": "降级",
    "pass_criteria_met: > 90% 标注警告": "警告",
    "pass_criteria_met: 有处理建议": "建议",
    "pass_criteria_met: 警告项排在问题清单前部": "警告",
    "pass_criteria_met: 排序正确": "排序",
    "pass_criteria_met: 系统空闲等待不干扰业务分析": "空闲",
    "pass_criteria_met: 有明确的 TOP N 限制": "TOP",
    "pass_criteria_met: 有快照时间标注": "快照",
    "pass_criteria_met: 单个失败不导致整体中断": "失败",
    "pass_criteria_met: 缺失数据有明确标注": "缺失",
    "pass_criteria_met: 无原始 SQL 输出": "SQL",
    "pass_criteria_met: 异常标注清晰": "异常",
    "pass_criteria_met: 输出账号状态审计结果": "账号",
    "pass_criteria_met: 识别锁定/过期账号状态": "锁定",
    "pass_criteria_met: 检测默认密码账号": "默认密码",
    "pass_criteria_met: 输出系统权限审计结果": "系统权限",
    "pass_criteria_met: 筛查出 ALTER SYSTEM 等高危权限": "ALTER SYSTEM",
    "pass_criteria_met: 识别 ANY 类权限": "ANY",
    "pass_criteria_met: 输出口令策略审计结果": "口令策略",
    "pass_criteria_met: 检查 FAILED_LOGIN_ATTEMPTS 等密码策略参数": "FAILED_LOGIN_ATTEMPTS",
    "pass_criteria_met: 检查 PASSWORD_VERIFY_FUNCTION 复杂度": "PASSWORD_VERIFY_FUNCTION",
    "pass_criteria_met: 返回账号不存在的明确提示": "不存在",
    "pass_criteria_met: 不产出审计报告": "审计",
    "pass_criteria_met: account 范围仅输出账号状态审计": "账号",
    "pass_criteria_met: privilege 范围仅输出权限审计": "权限",
    "pass_criteria_met: policy 范围仅输出口令策略审计": "口令策略",
    "pass_criteria_met: 审计范围包含系统账号": "系统账号",
    "pass_criteria_met: 输出系统账号状态与权限": "系统账号",
    "pass_criteria_met: 数据库可达，监控指标可采集": "可达",
    "pass_criteria_met: 未超过阈值的指标不产生误报": "阈值",
    "pass_criteria_met: 高阈值覆盖场景监控正常": "阈值",
    "pass_criteria_met: 多指标告警按严重程度排序": "严重程度",
    "pass_criteria_met: 快照时间戳精确到秒、时间顺序正确": "时间戳",
    "pass_criteria_met: 监控输出格式规范、有总结段落": "总结",
    "pass_criteria_met: 输出备份状态汇总与最近备份时间": "备份",
    "pass_criteria_met: 输出备份校验结果与可恢复性结论": "校验",
    "pass_criteria_met: 输出备份执行摘要与备份集详情": "备份集",
    "pass_criteria_met: 拒绝非法 backup_type 并提示合法取值": "backup_type",
    "pass_criteria_met: 拒绝非法 backup_dest 并提示合法取值": "backup_dest",
    "pass_criteria_met: 通道数与压缩算法边界被正确处理": "通道",
    "pass_criteria_met: 备份窗口超时自动中断并提示": "超时",
    "pass_criteria_met: 备份类型选型明确（全量+归档）": "全量",
    "pass_criteria_met: 备份频率与保留策略明确": "保留",
    "pass_criteria_met: 备份目标与性能优化（并行/压缩）明确": "并行",
    "pass_criteria_met: 校验与恢复演练方案明确": "校验",
    "pass_criteria_met: 增量备份频率与变更评估明确": "增量",
    "pass_criteria_met: 磁盘+磁带两级备份目标明确": "磁带",
    "pass_criteria_met: 异地容灾与加密策略明确": "容灾",
    "pass_criteria_met: 归档日志备份频率与保留明确": "归档",
    "pass_criteria_met: 磁带备份目标配置明确": "磁带",
    "pass_criteria_met: 与 RPO 目标匹配的归档策略明确": "RPO",
    "pass_criteria_met: 实例不可达被识别并拒绝": "不可达",
    "pass_criteria_met: 非法 backup_scope 被拒绝": "backup_scope",
    "pass_criteria_met: 错误信息提示合法取值": "合法",
    "pass_criteria_met: RPO>RTO 关系被识别并给出提示": "RPO",
    "pass_criteria_met: retention_days=1 边界被处理": "retention_days",
    "pass_criteria_met: daily_change_pct=0 边界被处理": "daily_change_pct",
    "pass_criteria_met: cloud 备份目标被正确识别": "cloud",
    "pass_criteria_met: custom 范围被正确识别": "custom",
    "pass_criteria_met: 超长保留期 retention_days=365 被处理": "retention_days",
    "pass_criteria_met: 超大库 data_size_gb=10000 被处理": "data_size_gb",
    "pass_criteria_met: 所有已知异常均被检测": "异常",
    "pass_criteria_met: 异常等级正确（CRITICAL/WARNING/INFO）": "CRITICAL",
    "pass_criteria_met: 异常有唯一 ID": "ID",
    "pass_criteria_met: 每条异常有建议措施": "建议",
    "pass_criteria_met: 异常按严重程度排序": "严重程度",
    "pass_criteria_met: 正常状态下不产生误报": "误报",
    "pass_criteria_met: 误报率为 0": "误报",
    "pass_criteria_met: 正常指标不产生异常": "异常",
    "pass_criteria_met: 边界值处理正确": "边界",
    "pass_criteria_met: 无边界错误": "边界",
    "pass_criteria_met: 多异常独立列出": "异常",
    "pass_criteria_met: 按严重程度排序": "严重程度",
    "pass_criteria_met: 不互相干扰": "异常",
    "pass_criteria_met: 执行计划至少包含行号、操作、对象、成本": "执行计划",
    "pass_criteria_met: 至少 1 条优化建议": "优化建议",
    "pass_criteria_met: 全表扫描被正确识别并标注": "全表扫描",
    "pass_criteria_met: 高耗时 SQL 不遗漏": "耗时",
    "pass_criteria_met: 所有非法输入均被拒绝": "非法",
    "pass_criteria_met: 错误信息明确说明原因": "原因",
    "pass_criteria_met: 不产生误导性诊断结果": "诊断",
    "pass_criteria_met: 超长 SQL 正常处理": "SQL",
    "pass_criteria_met: 绑定变量正确识别": "绑定变量",
    "pass_criteria_met: 诊断结果不受绑定变量名干扰": "绑定变量",
    "pass_criteria_met: 每个查询独立诊断": "诊断",
    "pass_criteria_met: 优化状态标注正确": "优化",
    "pass_criteria_met: 按执行时间排序": "执行时间",
    "pass_criteria_met: 瓶颈分析有具体发现和影响说明": "瓶颈",
    "pass_criteria_met: 优化建议按优先级排序": "优先级",
    "pass_criteria_met: 关键参数有当前值与建议值对比": "参数",
    "pass_criteria_met: 至少列出前 3 大瓶颈": "瓶颈",
    "pass_criteria_met: 每个瓶颈有量化数据支撑": "瓶颈",
    "pass_criteria_met: 并发场景瓶颈不遗漏": "并发",
    "pass_criteria_met: 不同性能表正确区分": "性能",
    "pass_criteria_met: 优化建议有优先级": "优先级",
    "pass_criteria_met: 迁移范围评估完整（版本/平台/数据量/对象清单）": "迁移",
    "pass_criteria_met: 迁移方式选型有主方案与备选方案及理由": "迁移方式",
    "pass_criteria_met: 前置检查清单覆盖源端/目标端/网络存储": "前置检查",
    "pass_criteria_met: 一致性校验与回滚割接步骤明确": "回滚",
    "pass_criteria_met: 方案针对指定 schema 且含在线同步方式": "schema",
    "pass_criteria_met: 有分批策略与并行通道配置": "并行",
    "pass_criteria_met: 有割接时间线与回滚方案": "回滚",
    "pass_criteria_met: 方案针对表空间范围且含跨平台处理": "表空间",
    "pass_criteria_met: 混合模式含全量+增量同步步骤": "增量",
    "pass_criteria_met: 有字节序/字符集兼容性说明": "字符集",
    "pass_criteria_met: 源端实例不可达被识别并拒绝": "不可达",
    "pass_criteria_met: schema 范围缺少 schema_name 被拒绝": "schema_name",
    "pass_criteria_met: 错误信息提示需提供 schema_name": "schema_name",
    "pass_criteria_met: table 范围被正确识别并生成方案": "table",
    "pass_criteria_met: parallel_degree=1 边界被接受": "parallel_degree",
    "pass_criteria_met: downtime_hours=0 边界被处理": "downtime_hours",
    "pass_criteria_met: 高并行度 parallel_degree=32 被接受": "parallel_degree",
    "pass_criteria_met: 大停机窗口 downtime_hours=24 被处理": "downtime_hours",
    "pass_criteria_met: 在线模式与停机窗口评估一致": "停机",
    "pass_criteria_met: Load Profile 包含所有关键指标": "Load Profile",
    "pass_criteria_met: Top 5 时间模型按总时间排序": "时间模型",
    "pass_criteria_met: Top 10 等待事件包含总等待时间和平均等待": "等待事件",
    "pass_criteria_met: Top 10 SQL 包含执行次数、时间、逻辑读": "SQL",
    "pass_criteria_met: 趋势分析正确": "趋势",
    "pass_criteria_met: 波峰/波谷有明确时间点": "波峰",
    "pass_criteria_met: 峰值时间段被正确识别": "峰值",
    "pass_criteria_met: 峰值原因有推测": "峰值",
    "pass_criteria_met: SQL 统计变化正确": "统计",
    "pass_criteria_met: 分段分析正确": "分段",
    "pass_criteria_met: 模式被识别": "模式",
    "pass_criteria_met: 趋势线正确": "趋势",
    "pass_criteria_met: 如有死锁，至少列出 2 个会话的 SID 和用户": "死锁",
    "pass_criteria_met: 根因分析有明确的触发条件说明": "根因",
    "pass_criteria_met: 处理建议分紧急程度": "紧急",
    "pass_criteria_met: 涉及对象有具体说明": "对象",
    "pass_criteria_met: 等待时间精确": "等待",
    "pass_criteria_met: 历史死锁正确归类": "死锁",
    "pass_criteria_met: 重复模式被识别": "重复",
    "pass_criteria_met: 每个环路深度有说明": "环路",
    "pass_criteria_met: 处理建议有效": "建议",
    "pass_criteria_met: 识别出 SELECT * 问题并建议列显式化": "SELECT *",
    "pass_criteria_met: 识别出全表扫描风险并给出索引建议": "全表扫描",
    "pass_criteria_met: 优化建议有具体 SQL 语句": "SQL",
    "pass_criteria_met: 识别出 DELETE 无 WHERE 高风险": "DELETE",
    "pass_criteria_met: 建议补充 WHERE 条件或事务控制": "WHERE",
    "pass_criteria_met: 识别出密码明文存储风险": "密码",
    "pass_criteria_met: 识别出敏感数据暴露风险": "敏感",
    "pass_criteria_met: 给出安全整改建议": "安全",
    "pass_criteria_met: 返回明确的参数缺失错误提示": "参数",
    "pass_criteria_met: 返回明确的 SQL 解析错误提示": "解析",
    "pass_criteria_met: standard 范围仅输出规范性审核": "规范",
    "pass_criteria_met: performance 范围仅输出性能审核": "性能",
    "pass_criteria_met: security 范围仅输出安全审核": "安全",
    "pass_criteria_met: 超长 SQL 正常完成审核": "SQL",
    "pass_criteria_met: 识别出绑定变量使用为良好实践": "绑定变量",
    "pass_criteria_met: 恢复计划包含恢复类型/范围/备份集清单/归档日志范围": "恢复计划",
    "pass_criteria_met: 明确标注 dry_run=true 未实际执行恢复": "dry_run",
    "pass_criteria_met: 校验结果包含备份可用性与归档日志连续性结论": "校验",
    "pass_criteria_met: 明确标注 validate 模式未实际恢复": "validate",
    "pass_criteria_met: 恢复计划包含全量恢复步骤与影响范围": "恢复计划",
    "pass_criteria_met: 明确提示 dry_run=true 未执行恢复，需设 false 并双签后执行": "dry_run",
    "pass_criteria_met: 明确提示 restore_type 非法，列出支持的恢复类型": "restore_type",
    "pass_criteria_met: 明确提示 until_time 与 until_scn 二选一冲突": "until_time",
    "pass_criteria_met: 明确处理 parallelism=0 边界（提示非法或回退默认）": "parallelism",
    "pass_criteria_met: 恢复计划仍完整输出": "恢复计划",
    "pass_criteria_met: 问题识别有具体行号和原因": "行号",
    "pass_criteria_met: 优化建议有 SQL 语句": "SQL",
    "pass_criteria_met: 有预估的性能改善": "性能",
    "pass_criteria_met: 预估改善合理": "改善",
    "pass_criteria_met: 有置信度说明": "置信度",
    "pass_criteria_met: SQL 注入被识别": "注入",
    "pass_criteria_met: 不执行任何查询": "未执行",
    "pass_criteria_met: 错误信息说明原因": "原因",
    "pass_criteria_met: 输出包含受影响行数与回滚命令": "受影响行数",
    "pass_criteria_met: 输出 Dry Run 报告且包含回滚方案": "Dry Run",
    "pass_criteria_met: 输出受影响行数与回滚命令": "受影响行数",
    "pass_criteria_met: 拒绝空 SQL 并提示 sql_text 必填": "sql_text",
    "pass_criteria_met: 拒绝非法 SQL 并返回 ORA 错误码": "ORA",
    "pass_criteria_met: 输出批次信息且总行数正确": "批次",
    "pass_criteria_met: 超时自动回滚并终止，提示已处理行数": "超时",
    "pass_criteria_met: 校验报告包含双签审批记录（approver_one 与 approver_two）": "双签",
    "pass_criteria_met: 校验报告逐项列出 DG 配置/同步延迟/归档连续性/SRL/FRA/数据文件状态": "DG",
    "pass_criteria_met: 明确标注未执行实际切换（validate_only=true）": "validate_only",
    "pass_criteria_met: 校验报告包含主库角色/switchover_status/归档传输/GAP 状态": "switchover_status",
    "pass_criteria_met: 明确提示 validate_only=true 未执行实际切换，需设 false 并双签后执行": "validate_only",
    "pass_criteria_met: 双签信息在报告中展示": "双签",
    "pass_criteria_met: 校验报告包含 Broker 配置状态与主备库角色": "Broker",
    "pass_criteria_met: 明确标注 dg_broker 模式未执行 SWITCHOVER": "dg_broker",
    "pass_criteria_met: 明确提示 approver_two 缺失，需双人审批": "approver_two",
    "pass_criteria_met: 校验报告包含同步延迟与 max_lag_seconds/max_lag_mb 阈值对比": "max_lag",
    "pass_criteria_met: 阈值边界处理明确（零容忍或提示扩大阈值）": "阈值",
    "pass_criteria_met: 明确标注 skip_checks=true 跳过前置校验": "skip_checks",
    "pass_criteria_met: 输出跳过校验的高风险提示": "跳过",
}

def marker_for(expected):
    """Return the marker keyword for an expected description, or None."""
    if expected in MARKER:
        return MARKER[expected]
    # fallback: strip prefix and take a distinctive token
    m = re.match(r"pass_criteria_met:\s*(.*)", expected)
    if m:
        desc = m.group(1)
        # try to find an ASCII token (param name / keyword) in the description
        ascii_tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", desc)
        if ascii_tokens:
            return ascii_tokens[0]
    return None

def transform(path):
    data = json.load(open(path, encoding="utf-8"))
    changed = 0
    for case in data:
        cid = case["case_id"]
        # case_id like "RS-001" contains a hyphen, invalid in an Oracle
        # identifier; sanitize to an underscore for the table name.
        out_table = "SKILL_OUTPUT_" + cid.replace("-", "_")
        setup = case.get("data", {}).get("setup", "")
        rollback = case.get("data", {}).get("rollback", "")
        # 1. setup: create output capture table
        if out_table not in setup:
            setup = setup.rstrip() + f"\nCREATE TABLE {out_table} (output_text CLOB);\n"
            case["data"]["setup"] = setup
        # 2. rollback: drop output capture table
        if f"DROP TABLE {out_table}" not in rollback:
            rollback = rollback.rstrip() + f"\nDROP TABLE {out_table};"
            case["data"]["rollback"] = rollback
        # 3. evidence instruction (item 3)
        case["evidence"] = (
            f"Run A 必须将 db-oracle 技能对用例 {cid} 的**实际输出**（原始文本）完整写入 "
            f"{out_table} 表（INSERT INTO {out_table} VALUES (:output_text)），"
            f"并在工单评论中留存该原始输出供人工核对。禁止用占位/模拟数据替代真实输出。"
        )
        # 4. replace trivial dual assertions with content checks
        new_assertions = []
        for a in case.get("assertions", []):
            if "SELECT 1 as check_result FROM dual WHERE 1=1" in a.get("sql", ""):
                marker = marker_for(a.get("expected", ""))
                if marker is None:
                    print(f"WARN: no marker for {cid}: {a.get('expected')}", file=sys.stderr)
                    new_assertions.append(a)
                    continue
                new_assertions.append({
                    "sql": f"SELECT COUNT(*) as c FROM {out_table} WHERE INSTR(output_text, '{marker}') > 0",
                    "expected": "c >= 1",
                    "note": f"校验 skill 真实输出包含标记: {marker}",
                })
                changed += 1
            else:
                new_assertions.append(a)
        case["assertions"] = new_assertions
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return changed

total = 0
for f in sorted(glob.glob("testcases/oracle/*/CASES.json")):
    c = transform(f)
    total += c
    print(f"{c}\t{f}")
print("TOTAL converted:", total)
