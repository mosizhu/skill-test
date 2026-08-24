---
test_id: TSK-MN-002
skill: db-oracle-monitor-anomaly
dimension: functional
priority: P2
risk_level: low
---

## 测试目标
验证 Oracle 历史指标异常检测功能的正确性。

## 前置条件
- AWR 历史快照已收集（至少近 7 天）
- 目标实例运行历史上有指标波动

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-monitor-anomaly skill
2. 传入 `instance_host`、`lookback_days: 7`
3. 传入 `metric_types: cpu,connections,sql_response_time`
4. 等待分析完成

## 预期结果
通过标准：
- 基于 AWR 历史数据（DBA_HIST_SYSMETRIC_SUMMARY）
- 使用统计方法检测异常（Z-Score / 移动平均偏离度）
- 检测出 CPU 异常、连接数异常、SQL 响应时间异常
- 每个异常标注：发生时间、指标值、偏离度、持续时长
- 异常时段与业务操作（如批量作业）关联分析
- 输出结构化异常报告

## 备注
- 异常检测算法的正确性需验证（是否漏报/误报）
- 如果近 7 天无异常，应明确说明"未发现异常"而非报错
- 不同指标可能有不同的检测阈值