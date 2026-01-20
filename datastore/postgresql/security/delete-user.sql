DO $$
DECLARE
    -- ======= 只需要修改这三个参数 =======
    v_old_user    TEXT := 'abc'; -- 要删的 user
    v_target_user TEXT := 'cde';          -- 接收资产的 user
    v_me        TEXT := current_user;                         -- 您的当前账号
    -- ==================================
BEGIN
    -- 1. 获取权限 (核心：让执行者代表这两个角色)
    EXECUTE format('GRANT %I TO %I', v_old_user, v_me);
    EXECUTE format('GRANT %I TO %I', v_target_user, v_me);
    RAISE NOTICE '已获取角色身份';

    -- 2. 转移资产 (REASSIGN)
    -- 处理当前数据库中该 user 拥有的所有表、序列等
    EXECUTE format('REASSIGN OWNED BY %I TO %I', v_old_user, v_target_user);
    RAISE NOTICE '已转移当前数据库资产';

    -- 3. 抹除依赖 (DROP OWNED)
    -- 清理权限条目和默认权限规则 (Default ACLs)
    EXECUTE format('DROP OWNED BY %I', v_old_user);
    RAISE NOTICE '已抹除当前数据库权限依赖';

    -- 4. 尝试物理删除角色
    -- 如果这个 user 在其他数据库还有依赖，这一步会报错，但这没关系
    BEGIN
        EXECUTE format('DROP ROLE %I', v_old_user);
        RAISE NOTICE '>>> 角色 % 已被彻底删除！', v_old_user;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '>>> 当前库已清空。由于其他数据库仍有依赖，请切换库继续执行此脚本。';
    END;

    -- 5. 清理身份继承关系
    EXECUTE format('REVOKE %I FROM %I', v_old_user, v_me);
    EXECUTE format('REVOKE %I FROM %I', v_target_user, v_me);

END $$;
