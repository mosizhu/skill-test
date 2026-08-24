# Oracle 健康巡检 (db-oracle-inspect) 测试用例集

> 验证 Oracle 数据库健康巡检的完整性、准确性和输出质量。覆盖实例信息、主机健康、空间资源、性能分析、备份容灾五大维度。
>
> **环境隔离策略**: 所有测试数据隔离在 TEST002 表空间。需要构造数据的用例，在 TEST002 中创建/填充/清理测试数据。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 环境需求 |
|------|------|------|--------|----------|
| TSK-IN-001 | 完整巡检执行 | 正例 | P0 | 无需构造，直接执行 |
| TSK-IN-002 | 数值准确性 | 正例 | P0 | 无需构造，直接执行 |
| TSK-IN-003 | 非法参数拒绝 | 反例 | P1 | 无需构造，直接执行 |
| TSK-IN-004 | 空结果处理 | 反例 | P1 | 无需构造，直接执行 |
| TSK-IN-005 | 权限降级 | 反例 | P1 | 无需构造，直接执行 |
| TSK-IN-006 | 表空间接近满 | 边界 | P1 | TEST002 填充至 90%+ |
| TSK-IN-007 | 等待事件分析 | 边界 | P1 | 无需构造，直接执行 |
| TSK-IN-008 | 会话数超限 | 边界 | P2 | 无需构造，直接执行 |
| TSK-IN-009 | 数据字典缺失 | 边界 | P2 | 无需构造，直接执行 |
| TSK-IN-010 | 输出格式规范 | 边界 | P2 | 无需构造，直接执行 |

## 隔离环境说明

- **隔离表空间**: `TEST002`（~35MB，支持自动扩展至 ~196GB）
- **隔离前缀**: 所有测试对象以 `TEST_TS_` 为前缀
- **清理策略**: 每个需要构造数据的用例末尾 `DROP TABLE` + 验证空间释放
- **不可清理场景**: 无（所有构造数据均可清理）

---

test_id: TSK-IN-001
type: positive
skill: db-oracle-inspect
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证健康巡检在正常环境下覆盖所有维度的完整执行。

## 前置条件

- 目标实例运行正常（oracle-rac_node01）
- 有各维度查询所需权限

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-inspect` skill
2. 传入参数: `instance_host` = `oracle-rac_node01`
3. 等待巡检完成（预期 30-60 秒）
4. 收集巡检输出

## 预期结果

### 实例信息维度（必须）
- 包含实例名称、主机名、版本、状态、启动时间
- 包含归档模式、最大归档模式
- 输出格式:

```
## 实例信息
| 属性 | 值 |
|------|------|
| 实例名称 | testdb1 |
| 主机 | node01 |
| 版本 | Oracle 19.0.0.0.0 |
| 状态 | OPEN |
| 启动时间 | 2026-08-17 04:12:04 |
| 归档模式 | ARCHIVELOG |
```

### 主机健康维度（必须）
- CPU 使用率（数值 + 百分比）
- 内存使用率（已用/总量/百分比）
- 磁盘使用率（各挂载点）

### 空间资源维度（必须）
- 所有数据文件表空间的总容量、已用、剩余、使用率
- 自动扩展配置信息
- 离线/只读表空间标注

### 性能分析维度（必须）
- 活跃会话数统计（ACTIVE/INACTIVE/OTHERS）
- 等待事件 TOP 10（事件名、会话数、总等待秒数）
- 性能基线评分（如有）

### 备份容灾维度（必须）
- 最近一次备份的时间、类型、状态
- 归档日志配置
- DG 同步状态（如有）

### 综合评估（必须）
- 整体健康评分或评级（如 A/B/C/D 或 90/100）
- 发现的问题清单（按严重程度排序）
- 处理建议

### 输出格式
- 使用 Markdown 格式
- 各维度有明确的二级标题（##）
- 数据使用表格展示
- 异常项使用 ⚠️ 或红色标注
- 正常项使用 ✅ 标注
- 有摘要/结论段落

## 通过标准

- 所有五个维度均有输出
- 实例信息完整无缺失
- 表空间使用率精确到小数点后 2 位
- 等待事件至少列出 TOP 5
- 有整体健康评分
- 有明确的问题清单

---

test_id: TSK-IN-002
type: positive
skill: db-oracle-inspect
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证巡检数值准确性和与数据库实际状态一致。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-inspect` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 手动验证关键指标:
   a) 表空间使用率:
   ```sql
   SELECT df.tablespace_name,
          ROUND((1 - df.free_mb/tf.total_mb)*100, 2) as usage_pct
   FROM (SELECT tablespace_name, SUM(bytes)/1024/1024 as free_mb FROM dba_free_space GROUP BY tablespace_name) df,
        (SELECT tablespace_name, SUM(bytes)/1024/1024 as total_mb FROM dba_data_files GROUP BY tablespace_name) tf
   WHERE df.tablespace_name = tf.tablespace_name;
   ```
   b) 会话数:
   ```sql
   SELECT status, COUNT(*) FROM v$session GROUP BY status;
   ```

## 预期结果

- 表空间使用率误差 <= 0.01%
- 会话数统计完全一致
- 百分比格式统一（如 "78.50%"）

## 通过标准

- 所有数值指标与直接查询误差 <= 0.01%
- 百分比格式统一无歧义

---

test_id: TSK-IN-003
type: negative
skill: db-oracle-inspect
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证非法参数输入时的拒绝行为。

## 前置条件

- 无特殊要求

## 执行步骤

1. 触发 `db-oracle-inspect` skill
2. 传入 `instance_host` = `nonexistent-host-99999`
3. 观察行为

## 预期结果

- Skill 在连接建立前即拒绝
- 错误信息包含具体原因和可用实例列表
- 不执行任何无效查询

## 通过标准

- Skill 拒绝执行
- 错误信息包含具体原因和可用实例列表

---

test_id: TSK-IN-004
type: negative
skill: db-oracle-inspect
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证空查询结果的优雅处理。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 触发 `db-oracle-inspect` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 观察空结果集处理

## 预期结果

- 空结果不导致 skill 崩溃
- 标注"暂无数据"而非留空
- 不影响其他维度输出

## 通过标准

- 可获取维度正常输出
- 不可获取维度标注"暂无数据"

---

test_id: TSK-IN-005
type: negative
skill: db-oracle-inspect
dimension: functional
priority: P1
risk_level: low
isolation: none

## 测试目标

验证权限受限账户下的降级行为。

## 前置条件

- test 账户无法访问 v$database.VERSION 等视图

## 执行步骤

1. 触发 `db-oracle-inspect` skill
2. 传入 `instance_host` = `oracle-rac_node01`（test 账户）
3. 观察部分视图查询失败的处理

## 预期结果

- 可查询维度正常输出
- 不可查询维度标注"权限不足，跳过"
- 不因部分查询失败而中断
- 整体健康评分仅基于可获取维度

## 通过标准

- 权限缺失不中断巡检
- 降级行为清晰标注

---

test_id: TSK-IN-006
type: boundary
skill: db-oracle-inspect
dimension: functional
priority: P1
risk_level: low
isolation: test002_fill
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_TS_HIGH_USAGE CHECK CONSTRAINTS CASCADE"
  - "验证 TEST002 空间释放"

## 测试目标

验证发现表空间接近满时的告警行为。

## 前置条件

- 需要在 TEST002 表空间填充数据至接近满（> 90%）

## 执行步骤

1. **构造高使用率环境**:
   ```sql
   -- 在 TEST002 创建测试表并填充数据
   CREATE TABLE TEST_TS_HIGH_USAGE (id NUMBER, data VARCHAR2(4000)) TABLESPACE TEST002;
   INSERT /*+ APPEND */ INTO TEST_TS_HIGH_USAGE SELECT ROWNUM, RPAD('X', 4000, 'X') FROM dual CONNECT BY LEVEL <= 10000;
   COMMIT;
   ```
2. 确认表空间使用率:
   ```sql
   SELECT tablespace_name, (1 - free_mb/total_mb)*100 as usage_pct FROM ...;
   ```
   目标: TEST002 使用率 >= 90%
3. 触发 `db-oracle-inspect` skill
4. 传入 `instance_host` = `oracle-rac_node01`
5. 验证对高使用率表空间的标注:
   a) 检查 TEST002 表空间是否被标记
   b) 验证标注等级是否正确

## 预期结果

- TEST002 使用率 > 90% 被标注为"警告"或"warning"
- 有明确的扩容建议
- SYSTEM/USERS 表空间（生产环境已有高使用率）的告警正确

## 通过标准

- > 90% 标注警告
- 有处理建议
- 警告项排在问题清单前部

## 清理

```sql
DROP TABLE TEST_TS_HIGH_USAGE;
```

---

test_id: TSK-IN-007
type: boundary
skill: db-oracle-inspect
dimension: functional
priority: P1
risk_level: low
isolation: none

## 测试目标

验证等待事件分析的准确性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 触发 `db-oracle-inspect` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 验证:
   a) 等待事件按累计等待时间排序
   b) 区分系统空闲等待和业务等待
   c) TOP 3 业务相关等待有说明

## 预期结果

- 按累计等待时间降序排列
- 系统空闲等待放末尾
- 业务等待有简要说明

## 通过标准

- 排序正确
- 系统空闲等待不干扰业务分析
- 有明确的 TOP N 限制

---

test_id: TSK-IN-008
type: boundary
skill: db-oracle-inspect
dimension: functional
priority: P2
risk_level: low
isolation: none

## 测试目标

验证高并发场景下的会话统计准确性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 触发 `db-oracle-inspect` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 对比:
   ```sql
   SELECT status, COUNT(*) FROM v$session GROUP BY status;
   ```

## 预期结果

- 会话数与 v$session 一致
- 有快照时间点标注
- 接近 processes 参数限制时告警（512）

## 通过标准

- 数值与 v$session 一致
- 有快照时间标注

---

test_id: TSK-IN-009
type: boundary
skill: db-oracle-inspect
dimension: functional
priority: P2
risk_level: low
isolation: none

## 测试目标

验证数据字典查询失败时的容错。

## 前置条件

- test 账户对某些数据字典视图无权限

## 执行步骤

1. 触发 `db-oracle-inspect` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 观察: dba_segments 空返回、dba_tablespaces 权限错误

## 预期结果

- 单个数据字典失败不影响其他维度
- 不可访问标注"无权限"
- 整体报告不中断

## 通过标准

- 单个失败不导致整体中断
- 缺失数据有明确标注
- 报告完整性 > 80%

---

test_id: TSK-IN-010
type: boundary
skill: db-oracle-inspect
dimension: quality
priority: P2
risk_level: low
isolation: none

## 测试目标

验证巡检输出的可读性和格式规范。

## 前置条件

- 正常执行巡检

## 执行步骤

1. 触发 `db-oracle-inspect` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 逐项检查:
   a) 各维度有明确标题分隔
   b) 表格数据对齐
   c) 无原始 SQL 暴露
   d) 有摘要/结论段落
   e) 数值精度统一
   f) 异常项有标注

## 预期结果

- ✅ 各维度有二级标题（##）
- ✅ 数据使用 Markdown 表格
- ❌ 无原始 SQL 输出
- ✅ 有摘要段落
- ✅ 数值格式统一
- ✅ 异常项使用 ⚠️ 标注

## 通过标准

- Markdown 格式规范
- 无原始 SQL 输出
- 有摘要/结论段落
- 异常标注清晰