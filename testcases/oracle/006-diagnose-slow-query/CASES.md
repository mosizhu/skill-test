# Oracle 慢查询诊断 (db-oracle-diagnose-slow-query) 测试用例集

> 验证慢查询诊断的准确性、执行计划分析和优化建议的可操作性。
>
> **环境隔离策略**: 构造慢查询数据隔离在 TEST002 表空间，诊断完成后清理。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 环境需求 |
|------|------|------|--------|----------|
| TSK-DQ-001 | 慢查询正常诊断 | 正例 | P0 | TEST002 填充测试数据 |
| TSK-DQ-002 | 诊断数据准确性 | 正例 | P0 | 无需构造 |
| TSK-DQ-003 | 优化建议可执行性 | 正例 | P0 | TEST002 填充测试数据 |
| TSK-DQ-004 | 非法 SQL 拒绝 | 反例 | P1 | 无需构造 |
| TSK-DQ-005 | 空执行计划 | 反例 | P1 | 无需构造 |
| TSK-DQ-006 | 超长 SQL | 边界 | P1 | TEST002 填充超长表 |
| TSK-DQ-007 | 递归/嵌套查询 | 边界 | P2 | TEST002 嵌套查询表 |
| TSK-DQ-008 | 绑定变量查询 | 边界 | P2 | 无需构造 |
| TSK-DQ-009 | 并发慢查询 | 边界 | P2 | TEST002 并发填充表 |

## 隔离环境说明

- **隔离表空间**: `TEST002`（~35MB，支持自动扩展至 ~196GB）
- **隔离前缀**: 所有测试对象以 `TEST_DQ_` 为前缀
- **清理策略**: 每个构造数据的用例末尾 `DROP TABLE` + 验证空间释放

---

test_id: TSK-DQ-001
type: positive
skill: db-oracle-diagnose-slow-query
dimension: functional
priority: P0
risk_level: low
isolation: test002_fill
preconditions:
  - "TEST002 表空间可用"
  - "有 CREATE TABLE / INSERT 权限"
cleanup_steps:
  - "DROP TABLE TEST_DQ_SLOW_QUERY CHECK CONSTRAINTS CASCADE"
  - "DROP INDEX TEST_DQ_IDX_SLOW CHECK CONSTRAINTS CASCADE"

## 测试目标

验证对已知慢查询的诊断完整性和准确性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. **构造慢查询环境** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DQ_SLOW_QUERY (
     id NUMBER,
     name VARCHAR2(200),
     data CLOB,
     created_date DATE
   ) TABLESPACE TEST002;
   
   -- 填充数据（约 10 万行，产生明显执行时间）
   INSERT /*+ APPEND */ INTO TEST_DQ_SLOW_QUERY
   SELECT ROWNUM,
          RPAD('NAME', 200, 'X'),
          RPAD('DATA', 4000, 'Y'),
          SYSDATE - ROWNUM/1000
   FROM (SELECT /*+ MATERIALIZE */ ROWNUM FROM dual CONNECT BY LEVEL <= 100)
   CROSS JOIN (SELECT /*+ MATERIALIZE */ ROWNUM FROM dual CONNECT BY LEVEL <= 1000);
   COMMIT;
   
   -- 创建部分索引（故意不创建全索引，产生全表扫描）
   CREATE INDEX TEST_DQ_IDX_SLOW ON TEST_DQ_SLOW_QUERY(created_date);
   -- 注意: name 列无索引，用于测试全表扫描检测
   ```

2. 触发 `db-oracle-diagnose-slow-query` skill
3. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `sql_text` = `SELECT * FROM TEST_DQ_SLOW_QUERY WHERE name LIKE '%X%'`
   - `execution_plan` = true
   - `top_n_events` = 5
4. 等待诊断完成

## 预期结果

### 诊断报告结构

```
## 慢查询诊断报告
### 基本信息
| 属性 | 值 |
|------|------|
| SQL ID | xxxxxx |
| 执行次数 | N |
| 平均耗时 | X ms |
| 最大耗时 | Y ms |

### 执行计划
| 行号 | 操作 | 对象 | 成本 | 预估行数 |
|------|------|------|------|---------|

### 性能分析
- **全表扫描**: 是 — TEST_DQ_SLOW_QUERY 表全表扫描
- **索引使用**: 部分 — created_date 列有索引但查询未使用
- **排序操作**: 1 次
- **哈希连接**: 0 次

### 优化建议
1. [高优先级] 为 name 列创建索引: CREATE INDEX idx_name ON TEST_DQ_SLOW_QUERY(name)
2. [中优先级] 查询优化: 避免使用 LIKE '%X%'（无法使用索引）
3. [低优先级] 考虑添加索引覆盖查询条件

### 风险评估
- **影响范围**: 全表扫描影响数据库整体 IO
- **风险等级**: HIGH
- **预估优化收益**: 预计提升 90%+
```

## 通过标准

- 包含完整的基本信息、执行计划、性能分析、优化建议
- 执行计划至少包含行号、操作、对象、成本
- 至少 1 条优化建议
- 风险等级明确
- 全表扫描被正确识别并标注

## 清理

```sql
DROP TABLE TEST_DQ_SLOW_QUERY;
DROP INDEX TEST_DQ_IDX_SLOW;
```

---

test_id: TSK-DQ-002
type: positive
skill: db-oracle-diagnose-slow-query
dimension: functional
priority: P0
risk_level: low
isolation: none

## 测试目标

验证诊断数据准确性，与 AWR 或 v$sql 实际数据对比。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 触发 `db-oracle-diagnose-slow-query` skill
2. 传入 `instance_host` = `oracle-rac_node01`
3. 同时执行以下查询作为对照:
   ```sql
   SELECT sql_id, sql_text, executions, elapsed_time/1000000 as elapsed_sec,
          cpu_time/1000000 as cpu_sec, buffer_gets
   FROM v$sql
   WHERE sql_text NOT LIKE '%v$sql%'
     AND sql_text NOT LIKE '%sql_text%'
   ORDER BY elapsed_time DESC
   FETCH FIRST 5 ROWS ONLY;
   ```
4. 对比诊断报告中的 SQL 信息与 v$sql 实际数据

## 预期结果

- 诊断报告中的 SQL 信息与 v$sql 一致
- 执行次数、执行时间、逻辑读等指标一致
- 不遗漏高耗时 SQL

## 通过标准

- SQL 信息完全一致
- 高耗时 SQL 不遗漏

---

test_id: TSK-DQ-003
type: positive
skill: db-oracle-diagnose-slow-query
dimension: functional
priority: P0
risk_level: low
isolation: test002_fill
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DQ_MULTI_IDX CHECK CONSTRAINTS CASCADE"
  - "DROP INDEX TEST_DQ_IDX_A CHECK CONSTRAINTS CASCADE"

## 测试目标

验证优化建议的可执行性。

## 前置条件

- 需要在 TEST002 中构造有明确优化空间的查询

## 执行步骤

1. **构造有明显优化空间的查询** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DQ_MULTI_IDX (
     id NUMBER,
     code VARCHAR2(50),
     status VARCHAR2(20),
     value NUMBER,
     created_date DATE
   ) TABLESPACE TEST002;
   
   INSERT INTO TEST_DQ_MULTI_IDX SELECT * FROM TEST_DQ_SLOW_QUERY;
   
   -- 创建部分索引（故意遗漏 status 列）
   CREATE INDEX TEST_DQ_IDX_A ON TEST_DQ_MULTI_IDX(created_date);
   -- 注意: code 和 status 列无索引
   ```

2. 触发 `db-oracle-diagnose-slow-query` skill
3. 传入 `sql_text` = `SELECT * FROM TEST_DQ_MULTI_IDX WHERE status = 'ACTIVE' AND code = 'ABC123'`
4. 验证每条优化建议:
   a) 建议是否具体可操作（如 "为 status 列创建索引" 而非 "优化索引"）
   b) 建议的风险评估是否合理
   c) 建议的执行步骤是否完整

## 预期结果

- 每条建议有明确的操作步骤（包含完整 SQL）
- 高风险操作标注"需维护窗口"
- 每条建议有预估的收益

## 通过标准

- 所有建议可执行
- 有明确的操作步骤
- 高风险操作有标注

## 清理

```sql
DROP TABLE TEST_DQ_MULTI_IDX;
DROP INDEX TEST_DQ_IDX_A;
```

---

test_id: TSK-DQ-004
type: negative
skill: db-oracle-diagnose-slow-query
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证非法 SQL 输入的处理能力。

## 前置条件

- 无特殊要求

## 执行步骤

1. 触发 `db-oracle-diagnose-slow-query` skill
2. 传入非法 SQL:
   - 情况 A: `sql_text` = `' OR 1=1 --`（SQL 注入）
   - 情况 B: `sql_text` = `hello world`（非 SQL 字符串）
   - 情况 C: `sql_text` = ``（空字符串）
3. 观察 skill 行为

## 预期结果

- 情况 A: 识别并拒绝执行，说明检测到可能的 SQL 注入
- 情况 B: 返回错误，说明非 SQL 内容无法诊断
- 情况 C: 返回错误，说明 SQL 不能为空
- 均不执行任何实际查询

## 通过标准

- 所有非法输入均被拒绝
- 错误信息明确说明原因
- 无 SQL 执行

---

test_id: TSK-DQ-005
type: negative
skill: db-oracle-diagnose-slow-query
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证对不存在 SQL 的处理（SQL ID 无效或查询已完成）。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 触发 `db-oracle-diagnose-slow-query` skill
2. 传入不存在的 SQL ID: `sql_id` = "INVALID00000"
3. 观察 skill 行为

## 预期结果

- 不在 v$sql 或 AWR 中找到该 SQL
- 标注"该 SQL 不在共享池/AWR 中"
- 不产生空诊断报告
- 建议用户检查 SQL ID 或等待查询执行后再诊断

## 通过标准

- 准确识别 SQL 不存在
- 给出清晰的错误说明
- 不产生误导性诊断结果

---

test_id: TSK-DQ-006
type: boundary
skill: db-oracle-diagnose-slow-query
dimension: boundary
priority: P1
risk_level: low
isolation: test002_long
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DQ_LONG_SQL CHECK CONSTRAINTS CASCADE"

## 测试目标

验证超长 SQL（> 4000 字符）的处理能力。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. **构造超长 SQL** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DQ_LONG_SQL (
     col1 NUMBER, col2 NUMBER, col3 NUMBER, col4 NUMBER, col5 NUMBER
   ) TABLESPACE TEST002;
   
   -- 重复 1000 次 INSERT（超过 4000 字符限制）
   INSERT INTO TEST_DQ_LONG_SQL SELECT ROWNUM, ROWNUM+1, ROWNUM+2, ROWNUM+3, ROWNUM+4 FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 100) t1, (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 100) t2;
   COMMIT;
   ```

2. 触发 `db-oracle-diagnose-slow-query` skill
3. 传入超长 SQL（拼接 50+ 表的 JOIN 或嵌套子查询超过 20 层）
4. 观察 skill 对超长 SQL 的处理

## 预期结果

- 不截断 SQL 文本（完整显示或提示过长）
- 不因为 SQL 过长而报错
- 执行计划分析正常进行
- 优化建议基于完整 SQL 分析

## 通过标准

- 超长 SQL 正常处理
- 执行计划完整
- 优化建议有效

## 清理

```sql
DROP TABLE TEST_DQ_LONG_SQL;
```

---

test_id: TSK-DQ-007
type: boundary
skill: db-oracle-diagnose-slow-query
dimension: boundary
priority: P2
risk_level: low
isolation: test002_nested
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DQ_NESTED CHECK CONSTRAINTS CASCADE"

## 测试目标

验证递归/嵌套查询的诊断准确性。

## 前置条件

- 需要在 TEST002 中构造嵌套查询

## 执行步骤

1. **构造嵌套查询数据** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DQ_NESTED (id NUMBER, parent_id NUMBER) TABLESPACE TEST002;
   INSERT INTO TEST_DQ_NESTED SELECT ROWNUM, MOD(ROWNUM, 500) FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 1000);
   COMMIT;
   ```

2. 触发 `db-oracle-diagnose-slow-query` skill
3. 传入嵌套查询 SQL（3+ 层子查询）:
   ```sql
   SELECT * FROM TEST_DQ_NESTED WHERE id IN (
     SELECT id FROM (SELECT id FROM (SELECT id FROM TEST_DQ_NESTED WHERE id > 500) WHERE id < 900)
   );
   ```

## 预期结果

- 嵌套结构正确识别
- 每层子查询的统计信息列出
- 嵌套深度有评估
- 优化建议针对嵌套结构

## 通过标准

- 嵌套结构正确识别
- 每层有统计信息
- 优化建议有效

## 清理

```sql
DROP TABLE TEST_DQ_NESTED;
```

---

test_id: TSK-DQ-008
type: boundary
skill: db-oracle-diagnose-slow-query
dimension: boundary
priority: P2
risk_level: low
isolation: test002_bind
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DQ_BIND_VAL CHECK CONSTRAINTS CASCADE"

## 测试目标

验证绑定变量查询的诊断准确性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. **构造绑定变量查询数据** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DQ_BIND_VAL (id NUMBER, name VARCHAR2(100), status VARCHAR2(20)) TABLESPACE TEST002;
   INSERT INTO TEST_DQ_BIND_VAL SELECT ROWNUM, 'NAME_' || ROWNUM, 'ACTIVE' FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 50000);
   COMMIT;
   ```

2. 触发 `db-oracle-diagnose-slow-query` skill
3. 传入带绑定变量的 SQL:
   ```sql
   SELECT * FROM TEST_DQ_BIND_VAL WHERE status = :1 AND name LIKE :2;
   ```

## 预期结果

- 绑定变量被正确识别和解释
- 诊断报告中列出绑定变量类型和范围
- 不将绑定变量名作为实际值

## 通过标准

- 绑定变量正确识别
- 诊断结果不受绑定变量名干扰

## 清理

```sql
DROP TABLE TEST_DQ_BIND_VAL;
```

---

test_id: TSK-DQ-009
type: boundary
skill: db-oracle-diagnose-slow-query
dimension: boundary
priority: P2
risk_level: low
isolation: test002_concurrent
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_DQ_CONCURRENT CHECK CONSTRAINTS CASCADE"

## 测试目标

验证并发慢查询的诊断准确性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. **构造并发查询环境** (在 TEST002):
   ```sql
   CREATE TABLE TEST_DQ_CONCURRENT (id NUMBER, status VARCHAR2(20), value NUMBER) TABLESPACE TEST002;
   INSERT INTO TEST_DQ_CONCURRENT SELECT ROWNUM, 'ACTIVE', ROWNUM FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 100000);
   COMMIT;
   
   -- 创建部分索引
   CREATE INDEX TEST_DQ_IDX_CONC ON TEST_DQ_CONCURRENT(status);
   ```

2. 触发 `db-oracle-diagnose-slow-query` skill
3. 传入多个并发查询 SQL 同时诊断:
   ```sql
   SELECT * FROM TEST_DQ_CONCURRENT WHERE status = 'ACTIVE';  -- 有索引
   SELECT * FROM TEST_DQ_CONCURRENT WHERE value > 50000;       -- 无索引，全表扫描
   ```

## 预期结果

- 每个查询独立诊断
- 有索引的查询标记为"已优化"
- 无索引的查询标记为"需优化"
- 诊断报告按执行时间排序

## 通过标准

- 每个查询独立诊断
- 优化状态标注正确
- 按执行时间排序