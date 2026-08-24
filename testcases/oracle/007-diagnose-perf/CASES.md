# Oracle 性能诊断 (db-oracle-diagnose-perf) 测试用例集

> 验证数据库整体性能诊断的准确性和优化建议的可操作性。
>
> **环境隔离策略**: 构造不同负载场景的数据隔离在 TEST002 表空间，测试后清理。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 环境需求 |
|------|------|------|--------|----------|
| TSK-DP-001 | 整体性能诊断 | 正例 | P0 | 无需构造，直接执行 |
| TSK-DP-002 | 性能瓶颈定位 | 正例 | P0 | 无需构造，直接执行 |
| TSK-DP-003 | 优化建议可执行性 | 正例 | P0 | TEST002 填充测试数据 |
| TSK-DP-004 | 非法参数 | 反例 | P1 | 无需构造 |
| TSK-DP-005 | 低负载场景 | 反例 | P1 | 无需构造 |
| TSK-DP-006 | 高并发场景 | 边界 | P1 | TEST002 并发填充表 |
| TSK-DP-007 | 混合负载场景 | 边界 | P1 | TEST002 混合表 + 慢查询 |
| TSK-DP-008 | 输出格式规范 | 边界 | P2 | 无需构造 |

## 隔离环境说明

- **隔离表空间**: `TEST002`（~35MB，支持自动扩展至 ~196GB）
- **隔离前缀**: 所有测试对象以 `TEST_DP_` 为前缀
- **清理策略**: 每个构造数据的用例末尾 `DROP TABLE` + 验证空间释放

---

test_id: TSK-DP-001
type: positive
skill: db-oracle-diagnose-perf
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证整体性能诊断的完整性和准确性。

## 前置条件

- oracle-rac_node01 实例运行正常
- 存在一定负载

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-diagnose-perf` skill
2. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `diagnosis_depth` = `standard`（标准深度）
   - `include_tuning_suggestions` = true
3. 等待诊断完成（预期 30-60 秒）

## 预期结果

### 诊断报告结构

```
## 性能诊断报告
### 整体评分
| 维度 | 评分 | 状态 |
|------|------|------|
| CPU | 85/100 | ✅ 正常 |
| 内存 | 90/100 | ✅ 正常 |
| I/O | 70/100 | ⚠️ 偏高 |
| 网络 | 95/100 | ✅ 正常 |
| SQL | 80/100 | ⚠️ 有慢查询 |
| **综合** | **83/100** | **良好** |

### 瓶颈分析
1. **I/O 瓶颈**（评分 70）
   - 发现: db file sequential read 等待时间偏高
   - 影响: 排序操作和索引扫描受影响
   - 建议: 考虑将热点表放入 buffer pool

2. **SQL 性能**（评分 80）
   - 发现: 3 个 SQL 执行时间超过阈值
   - 建议: 查看慢查询诊断详情

### 关键参数
| 参数 | 当前值 | 建议值 | 状态 |
|------|--------|--------|------|
| sga_target | 4G | 4G | ✅ 合理 |
| pga_aggregate_target | 1G | 1G | ✅ 合理 |

### 优化建议
1. [高] 分析热点表访问模式，考虑物化视图
2. [中] 优化 3 个慢查询（详见诊断报告）
3. [低] 定期检查统计信息过期情况
```

## 通过标准

- 有综合评分（0-100 分）
- 每个维度有独立评分
- 瓶颈分析有具体发现和影响说明
- 优化建议按优先级排序
- 关键参数有当前值与建议值对比

---

test_id: TSK-DP-002
type: positive
skill: db-oracle-diagnose-perf
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证性能瓶颈的准确定位。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 通过 Mopheus 工单触发 `db-oracle-diagnose-perf` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 验证瓶颈定位:
   a) 检查 CPU 等待事件排名
   b) 检查 I/O 等待事件排名
   c) 检查内存使用情况
   d) 对比诊断报告中的瓶颈分析与实际等待事件

## 预期结果

- 瓶颈定位与实际等待事件排名一致
- 主要瓶颈不遗漏
- 次要瓶颈不夸大
- 每个瓶颈有量化数据支撑

## 通过标准

- 瓶颈分析与实际数据一致
- 至少列出前 3 大瓶颈
- 每个瓶颈有量化数据支撑

---

test_id: TSK-DP-003
type: positive
skill: db-oracle-diagnose-perf
dimension: functional
priority: P0
risk_level: low
isolation: test002_fill
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DP_PERF_TEST CHECK CONSTRAINTS CASCADE"
  - "DROP INDEX TEST_DP_IDX_PERF CHECK CONSTRAINTS CASCADE"

## 测试目标

验证优化建议的可执行性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. **构造有明显优化空间的查询** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DP_PERF_TEST (
     id NUMBER,
     code VARCHAR2(50),
     status VARCHAR2(20),
     value NUMBER,
     created_date DATE
   ) TABLESPACE TEST002;
   
   INSERT INTO TEST_DP_PERF_TEST SELECT ROWNUM,
     RPAD('CODE', 50, 'X'), 'ACTIVE', ROWNUM, SYSDATE - ROWNUM/1000
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 50000);
   COMMIT;
   
   -- 创建部分索引（故意遗漏 status 列）
   CREATE INDEX TEST_DP_IDX_PERF ON TEST_DP_PERF_TEST(created_date);
   -- 注意: code 和 status 列无索引
   ```

2. 触发 `db-oracle-diagnose-perf` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 对每条优化建议验证:
   a) 建议是否具体可操作（如 "为 status 列创建索引" 而非 "优化索引"）
   b) 建议的风险评估是否合理
   c) 建议的执行步骤是否完整

## 预期结果

- 每条建议有明确的操作步骤
- 高风险操作标注"需维护窗口"
- 每条建议有预估的收益

## 通过标准

- 所有建议可执行
- 有明确的操作步骤
- 高风险操作有标注

## 清理

```sql
DROP TABLE TEST_DP_PERF_TEST;
DROP INDEX TEST_DP_IDX_PERF;
```

---

test_id: TSK-DP-004
type: negative
skill: db-oracle-diagnose-perf
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证非法参数的处理能力。

## 前置条件

- 无特殊要求

## 执行步骤

1. 触发 `db-oracle-diagnose-perf` skill
2. 传入非法参数:
   - 情况 A: `diagnosis_depth` = `invalid_level`
   - 情况 B: `include_tuning_suggestions` = "yes"（字符串而非布尔）
3. 观察 skill 行为

## 预期结果

- 非法参数被拒绝
- 错误信息包含合法参数值列表
- 不执行任何查询

## 通过标准

- 非法参数被拒绝
- 错误信息包含合法值列表

---

test_id: TSK-DP-005
type: negative
skill: db-oracle-diagnose-perf
dimension: functional
priority: P1
risk_level: low
isolation: none

## 测试目标

验证低负载场景的诊断准确性。

## 前置条件

- oracle-rac_node01 实例运行正常（低负载时）

## 执行步骤

1. 触发 `db-oracle-diagnose-perf` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 观察输出中的低负载处理

## 预期结果

- 低负载时诊断报告不产生虚假告警
- 明确指出"当前负载较低"
- 评分合理（不因为低负载而给低分）

## 通过标准

- 低负载不产生虚假告警
- 评分与负载情况匹配

---

test_id: TSK-DP-006
type: boundary
skill: db-oracle-diagnose-perf
dimension: boundary
priority: P1
risk_level: low
isolation: test002_concurrent
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DP_CONCURRENT CHECK CONSTRAINTS CASCADE"

## 测试目标

验证高并发场景下的性能诊断准确性。

## 前置条件

- 需要在 TEST002 中构造高并发场景

## 执行步骤

1. **构造高并发环境** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DP_CONCURRENT (
     id NUMBER,
     status VARCHAR2(20),
     value NUMBER,
     created_date DATE
   ) TABLESPACE TEST002;
   
   INSERT INTO TEST_DP_CONCURRENT SELECT ROWNUM,
     CASE WHEN MOD(ROWNUM, 3) = 0 THEN 'ACTIVE'
          WHEN MOD(ROWNUM, 3) = 1 THEN 'INACTIVE'
          ELSE 'PENDING' END,
     ROWNUM, SYSDATE - ROWNUM/1000
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 200000);
   COMMIT;
   ```

2. 触发 `db-oracle-diagnose-perf` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 验证并发场景的诊断

## 预期结果

- 高并发场景下诊断准确
- 会话统计、等待事件准确
- 不遗漏并发导致的性能瓶颈

## 通过标准

- 诊断准确
- 并发场景瓶颈不遗漏

## 清理

```sql
DROP TABLE TEST_DP_CONCURRENT;
```

---

test_id: TSK-DP-007
type: boundary
skill: db-oracle-diagnose-perf
dimension: boundary
priority: P1
risk_level: low
isolation: test002_mixed
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DP_MIXED_FAST CHECK CONSTRAINTS CASCADE"
  - "DROP TABLE TEST_DP_MIXED_SLOW CHECK CONSTRAINTS CASCADE"

## 测试目标

验证混合负载场景的诊断能力。

## 前置条件

- 需要在 TEST002 中构造混合负载

## 执行步骤

1. **构造混合负载环境** (在 TEST002):
   ```sql
   -- 快速查询表（有完整索引）
   CREATE TABLE TEST_DP_MIXED_FAST (id NUMBER, code VARCHAR2(50), status VARCHAR2(20), value NUMBER) TABLESPACE TEST002;
   CREATE INDEX TEST_DP_IDX_FAST_1 ON TEST_DP_MIXED_FAST(code);
   CREATE INDEX TEST_DP_IDX_FAST_2 ON TEST_DP_MIXED_FAST(status);
   
   INSERT INTO TEST_DP_MIXED_FAST SELECT ROWNUM, RPAD('CODE', 50, 'X'),
     CASE MOD(ROWNUM, 3) WHEN 0 THEN 'A' WHEN 1 THEN 'B' ELSE 'C' END, ROWNUM
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 50000);
   COMMIT;
   
   -- 慢查询表（无索引）
   CREATE TABLE TEST_DP_MIXED_SLOW (id NUMBER, name VARCHAR2(200), value NUMBER) TABLESPACE TEST002;
   INSERT INTO TEST_DP_MIXED_SLOW SELECT ROWNUM, RPAD('NAME', 200, 'X'), ROWNUM
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 100000);
   COMMIT;
   ```

2. 触发 `db-oracle-diagnose-perf` skill
3. 传入 `instance_host` = `oracle-rac_node01`
4. 验证混合负载场景的诊断

## 预期结果

- 快速查询表被正确标记为"已优化"
- 慢查询表被正确标记为"需优化"
- 综合评分反映混合场景的真实状态

## 通过标准

- 不同性能表正确区分
- 综合评分反映混合场景

## 清理

```sql
DROP TABLE TEST_DP_MIXED_FAST;
DROP TABLE TEST_DP_MIXED_SLOW;
DROP INDEX TEST_DP_IDX_FAST_1;
DROP INDEX TEST_DP_IDX_FAST_2;
```

---

test_id: TSK-DP-008
type: boundary
skill: db-oracle-diagnose-perf
dimension: quality
priority: P2
risk_level: low
isolation: none

## 测试目标

验证诊断输出的可读性和格式规范。

## 前置条件

- 正常执行诊断

## 执行步骤

1. 触发 `db-oracle-diagnose-perf` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 逐项检查:
   a) 各维度有明确标题分隔
   b) 评分有颜色/符号标注
   c) 无原始 SQL 暴露
   d) 有摘要/结论段落
   e) 优化建议有优先级标注

## 预期结果

- ✅ 各维度有二级标题（##）
- ✅ 评分使用符号标注（✅/⚠️/🔴）
- ❌ 无原始 SQL 输出
- ✅ 有摘要段落
- ✅ 优化建议有优先级（高/中/低）

## 通过标准

- Markdown 格式规范
- 评分清晰直观
- 有摘要/结论段落
- 优化建议有优先级