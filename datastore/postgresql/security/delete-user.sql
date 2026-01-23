-- ====================================================================
-- PostgreSQL 角色删除脚本
-- ====================================================================
-- 用途：安全删除 PostgreSQL 角色/用户，清理所有依赖和权限
-- 使用场景：当 DROP ROLE 因权限或所有权问题而失败时
--
-- 重要提示：
-- 1. 此脚本必须在每一个包含该角色依赖的数据库中执行
-- 2. 角色的权限和所有权是数据库级别的，不是实例级别的
-- 3. 执行前请确保修改下面的三个参数
-- ====================================================================

DO $$
DECLARE
    -- ======= 配置区域：只需要修改这三个参数 =======
    v_old_user    TEXT := 'your-role-to-delete';  -- 要删除的角色名
    v_target_user TEXT := 'postgres';              -- 接收资产的角色（建议用 postgres 或其他管理员账号）
    v_me          TEXT := current_user;            -- 当前执行脚本的用户（自动获取）
    -- ===============================================

    v_db_name TEXT;
BEGIN
    v_db_name := current_database();

    RAISE NOTICE '================================================';
    RAISE NOTICE '开始清理角色: %', v_old_user;
    RAISE NOTICE '当前数据库: %', v_db_name;
    RAISE NOTICE '================================================';

    -- 第一步：身份继承（解决权限不足）
    -- 管理员需要临时获得该角色的身份，才能处理它的资产
    -- 这是最关键的一步，否则后续操作会因权限不足而失败
    EXECUTE format('GRANT %I TO %I', v_old_user, v_me);
    EXECUTE format('GRANT %I TO %I', v_target_user, v_me);
    RAISE NOTICE '✓ 已获取角色身份权限';

    -- 第二步：资产转移（REASSIGN OWNED）
    -- 将该角色拥有的所有表、视图、序列的所有权批量转移给接收角色
    -- 注意：这只会处理当前数据库中的对象
    EXECUTE format('REASSIGN OWNED BY %I TO %I', v_old_user, v_target_user);
    RAISE NOTICE '✓ 已转移当前数据库中的所有资产';

    -- 第三步：依赖抹除（DROP OWNED）
    -- 这是最关键的一步，会做两件事：
    -- 1. 撤销该角色在所有对象上的显式权限（SELECT, UPDATE 等）
    -- 2. 清理默认权限记录（Default ACLs）——这是最隐形的依赖点
    EXECUTE format('DROP OWNED BY %I', v_old_user);
    RAISE NOTICE '✓ 已抹除当前数据库中的所有权限依赖';

    -- 第四步：尝试物理删除角色
    -- 如果该角色在其他数据库还有依赖，这一步会失败
    -- 这是正常的，需要在其他数据库中重复执行此脚本
    BEGIN
        EXECUTE format('DROP ROLE %I', v_old_user);
        RAISE NOTICE '================================================';
        RAISE NOTICE '✓✓✓ 角色 % 已被彻底删除！', v_old_user;
        RAISE NOTICE '================================================';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '================================================';
        RAISE NOTICE '⚠ 当前数据库 % 已清理完成', v_db_name;
        RAISE NOTICE '⚠ 角色 % 在其他数据库仍有依赖', v_old_user;
        RAISE NOTICE '⚠ 请切换到其他数据库并重新执行此脚本';
        RAISE NOTICE '================================================';
    END;

    -- 第五步：清理身份继承关系
    -- 无论删除是否成功，都要清理临时授予的权限
    EXECUTE format('REVOKE %I FROM %I', v_old_user, v_me);
    EXECUTE format('REVOKE %I FROM %I', v_target_user, v_me);
    RAISE NOTICE '✓ 已清理临时身份继承关系';

END $$;

-- ====================================================================
-- 使用说明
-- ====================================================================
--
-- 1. 修改脚本顶部的三个参数：
--    - v_old_user: 要删除的角色名
--    - v_target_user: 接收资产的角色（通常是 postgres 或其他管理员账号）
--
-- 2. 在每个数据库中执行此脚本：
--    \c database1
--    \i delete-user.sql
--
--    \c database2
--    \i delete-user.sql
--
--    \c postgres  -- 不要忘记 postgres 数据库
--    \i delete-user.sql
--
-- 3. 如何查找包含依赖的数据库：
--    SELECT db.datname
--    FROM pg_shdepend s
--    LEFT JOIN pg_database db ON s.dbid = db.oid
--    WHERE refobjid = (SELECT oid FROM pg_roles WHERE rolname = 'your-role-name');
--
-- 4. 常见错误处理：
--    - "must be owner of relation xxx": 使用 REASSIGN OWNED 转移所有权
--    - "permission denied for table xxx": 确保执行 GRANT 步骤获取了身份
--    - "role is being used by current user": 重新连接数据库
--    - "cannot drop table xxx because other objects depend on it": CASCADE 删除
--
-- ====================================================================
