---
test_id: TSK-AP-001
skill: db-oracle-audit-permission
dimension: functional
priority: P1
risk_level: low
---

## 测试目标
验证账号权限审计功能的完整性和准确性。

## 前置条件
- 目标实例可访问
- 有 DBA 权限（可查询 dba_sys_privs、dba_role_privs 等）

## 执行步骤
1. 通过 Mopheus 工单触发 db-oracle-audit-permission skill
2. 传入 `instance_host`（目标实例）
3. 等待审计完成

## 预期结果
通过标准：
- 账号状态审计：完整用户列表、锁定/过期/默认密码检测
- SYSDBA/SYSOPER 特权账户盘点（独立列出）
- 系统权限审计：高危权限清单（ALTER SYSTEM、DROP ANY 等）
- 对象权限审计：对象级别权限分布
- 空账号、测试账号、过期账号的识别
- 输出合规性评分或风险评级
- 每条审计发现有明确的风险等级标注

## 备注
- 权限审计是只读操作
- 审计结果可用于等保/安全合规检查
- 应重点关注：未锁定过期账号、过度授权账号、SYSDBA 非管理员使用