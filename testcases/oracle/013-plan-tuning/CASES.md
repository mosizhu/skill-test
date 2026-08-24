# Oracle 执行计划调优 (db-oracle-plan-tuning) 测试用例集

> 验证执行计划分析的准确性、优化建议的可操作性和对 SQL 修改的影响评估。
>
> **环境隔离策略**: 构造测试数据的用例隔离在 TEST002 表空间，测试后清理。

## 用例总览

| 编号 | 名称 | 类型 | 优先级 | 环境需求 |
|------|------|------|--------|----------|
| TSK-PT-001 | 计划分析 | 正例 | P0 | TEST002 填充测试数据 |
| TSK-PT-002 | 建议可执行性 | 正例 | P0 | TEST002 填充测试数据 |
| TSK-PT-003 | 影响评估 | 正例 | P0 | TEST002 填充测试数据 |
| TSK-PT-004 | 非法 SQL | 反例 | P1 | 无需构造 |
| TSK-PT-005 | 计划不存在 | 反例 | P1 | 无需构造 |
| TSK-PT-006 | SQL 注入 | 边界 | P1 | 无需构造 |
| TSK-PT-007 | 复杂嵌套 | 边界 | P2 | TEST002 嵌套查询表 |

## 隔离环境说明

- **隔离表空间**: `TEST002`（~35MB，支持自动扩展至 ~196GB）
- **隔离前缀**: 所有测试对象以 `TEST_PT_` 为前缀
- **清理策略**: 每个构造数据的用例末尾 `DROP TABLE` + 验证空间释放

---

test_id: TSK-PT-001
type: positive
skill: db-oracle-plan-tuning
dimension: functional
priority: P0
risk_level: low
isolation: test002_plan
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_PT_PLAN CHECK CONSTRAINTS CASCADE"
  - "DROP INDEX TEST_PT_IDX_PLAN CHECK CONSTRAINTS CASCADE"

## 测试目标

验证执行计划分析的完整性和准确性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. **构造测试数据** (在 TEST002):
   ```sql
   CREATE TABLE TEST_PT_PLAN (
     id NUMBER,
     name VARCHAR2(100),
     status VARCHAR2(20),
     value NUMBER,
     created_date DATE
   ) TABLESPACE TEST002;
   
   -- 创建部分索引（故意不创建全索引，产生全表扫描）
   CREATE INDEX TEST_PT_IDX_PLAN ON TEST_PT_PLAN(created_date);
   -- 注意: name 和 status 列无索引，用于测试问题识别
   
   INSERT INTO TEST_PT_PLAN SELECT ROWNUM,
     RPAD('NAME', 100, 'X'),
     CASE MOD(ROWNUM, 3) WHEN 0 THEN 'ACTIVE' WHEN 1 THEN 'INACTIVE' ELSE 'PENDING' END,
     ROWNUM, SYSDATE - ROWNUM/1000
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 50000);
   COMMIT;
   ```

2. 触发 `db-oracle-plan-tuning` skill
3. 传入参数:
   - `instance_host` = `oracle-rac_node01`
   - `sql_text` = `SELECT * FROM TEST_PT_PLAN WHERE status = 'ACTIVE' AND name LIKE '%X%'`
   - `action` = `analyze`（仅分析，不修改）
4. 等待诊断完成

## 预期结果

### 输出格式

```
## 执行计划分析报告
### SQL 基本信息
| 属性 | 值 |
|------|------|
| SQL ID | xxxxxx |
| SQL 类型 | SELECT |
| 执行计划 | 见下方 |
| 状态 | 有效 |

### 当前执行计划
| 行号 | 操作 | 对象 | 访问方式 | 成本 |
|------|------|------|----------|------|
| 0 | SELECT STATEMENT | - | - | 100 |
| 1 | NESTED LOOPS | - | - | 100 |
| 2 | INDEX RANGE SCAN | IDX_1 | 索引 | 5 |
| 3 | TABLE ACCESS FULL | TABLE_A | 全表扫描 | 95 |

### 问题识别
1. **TABLE_A 全表扫描**（行号 3）
   - 问题: 表 TABLE_A 全表扫描，成本 95
   - 原因: 缺少合适索引或统计信息过期
   - 影响: 大表扫描影响性能

### 优化建议
1. **高优先级**
   - 操作: CREATE INDEX idx_table_a_col ON table_A(column_name)
   - 预期效果: 全表扫描改为索引范围扫描，成本降低 90%
   - 风险: 低（仅添加索引，不影响业务）
   - 维护窗口: 无需维护窗口

### 影响评估
| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 执行时间 | X ms | Y ms | Z% |
| 逻辑读 | N | M | W% |
| 成本 | 100 | 10 | 90% |
```

## 通过标准

- 执行计划完整，包含行号、操作、对象、访问方式
- 问题识别有具体行号和原因
- 优化建议有 SQL 语句
- 风险等级明确
- 有预估的性能改善

## 清理

```sql
DROP TABLE TEST_PT_PLAN;
DROP INDEX TEST_PT_IDX_PLAN;
```

---

test_id: TSK-PT-002
type: positive
skill: db-oracle-plan-tuning
dimension: functional
priority: P0
risk_level: low
isolation: test002_plan
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_PT_EXEC CHECK CONSTRAINTS CASCADE"

## 测试目标

验证优化建议的可执行性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. **构造测试数据** (在 TEST002):
   ```sql
   CREATE TABLE TEST_PT_EXEC (
     id NUMBER,
     code VARCHAR2(50),
     status VARCHAR2(20),
     value NUMBER
   ) TABLESPACE TEST002;
   
   -- 只创建部分索引
   CREATE INDEX TEST_PT_IDX_EXEC ON TEST_PT_EXEC(code);
   
   INSERT INTO TEST_PT_EXEC SELECT ROWNUM, RPAD('CODE', 50, 'X'),
     CASE MOD(ROWNUM, 3) WHEN 0 THEN 'A' WHEN 1 THEN 'B' ELSE 'C' END, ROWNUM
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 50000);
   COMMIT;
   ```

2. 触发 `db-oracle-plan-tuning` skill
3. 传入 `instance_host` = `oracle-rac_node01`
   - `sql_text` = `SELECT * FROM TEST_PT_EXEC WHERE status = 'A'`
4. 验证每条优化建议:
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
DROP TABLE TEST_PT_EXEC;
DROP INDEX TEST_PT_IDX_EXEC;
```

---

test_id: TSK-PT-003
type: positive
skill: db-oracle-plan-tuning
dimension: functional
priority: P0
risk_level: low
isolation: test002_plan
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_PT_IMPACT CHECK CONSTRAINTS CASCADE"

## 测试目标

验证影响评估的准确性。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. **构造测试数据** (在 TEST002):
   ```sql
   CREATE TABLE TEST_PT_IMPACT (
     id NUMBER,
     name VARCHAR2(100),
     value NUMBER
   ) TABLESPACE TEST002;
   
   INSERT INTO TEST_PT_IMPACT SELECT ROWNUM, RPAD('NAME', 100, 'X'), ROWNUM
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 50000);
   COMMIT;
   ```

2. 触发 `db-oracle-plan-tuning` skill
3. 传入 `instance_host` = `oracle-rac_node01`
   - `sql_text` = `SELECT * FROM TEST_PT_IMPACT WHERE name LIKE '%X%'`
4. 验证影响评估:
   a) 预估改善是否合理
   b) 逻辑读减少是否准确
   c) 执行时间改善是否合理

## 预期结果

- 预估改善合理（不过分夸大）
- 逻辑读减少估算准确
- 执行时间改善估算合理

## 通过标准

- 预估改善合理
- 估算准确
- 有置信度说明

## 清理

```sql
DROP TABLE TEST_PT_IMPACT;
```

---

test_id: TSK-PT-004
type: negative
skill: db-oracle-plan-tuning
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证非法 SQL 输入的处理。

## 前置条件

- 无特殊要求

## 执行步骤

1. 触发 `db-oracle-plan-tuning` skill
2. 传入非法 SQL:
   - 情况 A: `' OR 1=1 --`（SQL 注入）
   - 情况 B: `hello world`（非 SQL）
   - 情况 C: 空字符串
3. 观察 skill 行为

## 预期结果

- 所有非法输入均被拒绝
- 错误信息明确说明原因
- 不执行任何查询

## 通过标准

- 非法参数被拒绝
- 错误信息包含具体原因
- 无 SQL 执行

---

test_id: TSK-PT-005
type: negative
skill: db-oracle-plan-tuning
dimension: boundary
priority: P1
risk_level: low
isolation: none

## 测试目标

验证 SQL 不存在时的处理。

## 前置条件

- oracle-rac_node01 实例运行正常

## 执行步骤

1. 触发 `db-oracle-plan-tuning` skill
2. 传入不存在的 SQL ID: `sql_id` = "INVALID00000"
3. 观察 skill 行为

## 预期结果

- 不在 v$sql 中找到该 SQL
- 标注"该 SQL 不在共享池中"
- 不产生空诊断报告

## 通过标准

- 准确识别 SQL 不存在
- 给出清晰的错误说明

---

test_id: TSK-PT-006
type: boundary
skill: db-oracle-plan-tuning
dimension: boundary
priority: P1
risk_level: medium
isolation: none

## 测试目标

验证 SQL 注入防护。

## 前置条件

- 无特殊要求

## 执行步骤

1. 触发 `db-oracle-plan-tuning` skill
2. 传入包含 SQL 注入的 SQL 文本:
   - `' UNION SELECT username, password, null FROM all_users --`
   - `'; DROP TABLE test --`
3. 观察 skill 行为

## 预期结果

- SQL 注入被识别并拒绝
- 不执行任何实际查询
- 错误信息说明检测到可疑字符

## 通过标准

- SQL 注入被识别
- 不执行任何查询
- 错误信息说明原因

---

test_id: TSK-PT-007
type: boundary
skill: db-oracle-plan-tuning
dimension: boundary
priority: P2
risk_level: low
isolation: test002_nested
preconditions:
  - "TEST002 表空间可用"
cleanup_steps:
  - "DROP TABLE TEST_PT_NESTED CHECK CONSTRAINTS CASCADE"

## 测试目标

验证复杂嵌套查询的诊断准确性。

## 前置条件

- 需要在 TEST002 中构造嵌套查询

## 执行步骤

1. **构造嵌套查询数据** (在 TEST002):
   ```sql
   CREATE TABLE TEST_PT_NESTED (id NUMBER, parent_id NUMBER, name VARCHAR2(100)) TABLESPACE TEST002;
   
   INSERT INTO TEST_PT_NESTED SELECT ROWNUM, MOD(ROWNUM, 500), RPAD('NAME', 100, 'X')
   FROM (SELECT ROWNUM FROM dual CONNECT BY LEVEL <= 50000);
   COMMIT;
   ```

2. 触发 `db-oracle-plan-tuning` skill
3. 传入复杂嵌套查询 SQL（3+ 层子查询）:
   ```sql
   SELECT * FROM TEST_PT_NESTED WHERE id IN (
     SELECT id FROM (SELECT id FROM (SELECT id FROM TEST_PT_NESTED WHERE id > 500) WHERE id < 900)
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
DROP TABLE TEST_PT_NESTED;
```