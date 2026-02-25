"""\
完整迁移脚本：templates 模板归属与权限字段

目的：
- 为 templates 表增加：owner_id / team_id / is_public
- 创建必要索引
- （可选）检查脏数据并添加外键约束

特性：
- 幂等（可重复执行）：会先检查列/索引/外键是否存在
- 兼容历史数据：首次新增 is_public 时，将历史模板全部置为公开（TRUE）
- 可直接运行：python run_migration_template_ownership_full.py

注意：
- 默认【不自动添加外键】（ADD_FOREIGN_KEYS = False），避免线上存量脏数据导致失败。
- 你可以先跑一次，确认字段和索引已就位；再把 ADD_FOREIGN_KEYS 改为 True，或让我生成单独外键脚本。
"""

import io
import os
import sys

from sqlalchemy import text


# Windows 控制台 UTF-8 兼容
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ============ 可调开关 ============
ADD_FOREIGN_KEYS = False  # 是否尝试添加外键（默认关闭，避免脏数据/锁表风险）
DRY_RUN = False  # True: 只打印将执行的 SQL，不真正执行
# =================================


def _log_sql(sql: str):
    print(f"    SQL: {sql}")


def _exec(connection, sql: str, params: dict | None = None):
    if DRY_RUN:
        _log_sql(sql)
        return None
    return connection.execute(text(sql), params or {})


def _table_exists(connection, table_name: str) -> bool:
    sql = """
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_schema = DATABASE()
      AND table_name = :table_name
    """
    return connection.execute(text(sql), {"table_name": table_name}).fetchone()[0] > 0


def _column_exists(connection, table_name: str, column_name: str) -> bool:
    sql = """
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = :table_name
      AND COLUMN_NAME = :column_name
    """
    return (
        connection.execute(text(sql), {"table_name": table_name, "column_name": column_name}).fetchone()[0]
        > 0
    )


def _index_exists(connection, table_name: str, index_name: str) -> bool:
    sql = """
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = :table_name
      AND INDEX_NAME = :index_name
    """
    return (
        connection.execute(text(sql), {"table_name": table_name, "index_name": index_name}).fetchone()[0]
        > 0
    )


def _fk_exists(connection, table_name: str, fk_name: str) -> bool:
    sql = """
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = :table_name
      AND CONSTRAINT_NAME = :fk_name
      AND CONSTRAINT_TYPE = 'FOREIGN KEY'
    """
    return (
        connection.execute(text(sql), {"table_name": table_name, "fk_name": fk_name}).fetchone()[0]
        > 0
    )


def _count_invalid_fk(connection, fk_column: str, ref_table: str, ref_pk: str = "id") -> int:
    # 统计 templates.fk_column 中非空且在 ref_table 中不存在的记录数
    sql = f"""
    SELECT COUNT(*)
    FROM templates t
    LEFT JOIN {ref_table} r ON t.{fk_column} = r.{ref_pk}
    WHERE t.{fk_column} IS NOT NULL
      AND r.{ref_pk} IS NULL
    """
    return connection.execute(text(sql)).fetchone()[0]


def _load_settings():
    """加载 settings/engine。

    说明：
    - 你当前项目 app/config.py 使用 env_file='.env'
    - 因此请尽量在 feishu-print-backend 目录下运行本脚本
    """

    from app.config import settings
    from app.database import engine

    return settings, engine


def run_migration() -> bool:
    print("=" * 60)
    print("开始执行数据库迁移：templates 模板归属字段（完整版）")
    print("=" * 60)

    # 给一个运行目录提示，方便排查 .env 加载问题
    print(f"当前工作目录: {os.getcwd()}")

    settings, engine = _load_settings()

    print(
        f"数据库连接: {settings.database_url.split('@')[-1] if '@' in settings.database_url else '已配置'}"
    )
    print(f"DRY_RUN={DRY_RUN}  ADD_FOREIGN_KEYS={ADD_FOREIGN_KEYS}")
    print()

    table_name = "templates"

    try:
        with engine.connect() as connection:
            trans = connection.begin()

            try:
                if not _table_exists(connection, table_name):
                    print(f"[错误] {table_name} 表不存在！")
                    print("请先确保数据库表已创建（或先执行 database.sql）。")
                    trans.rollback()
                    return False

                # 1) 列：owner_id
                if _column_exists(connection, table_name, "owner_id"):
                    print("[跳过] 列 owner_id 已存在")
                else:
                    print("[执行] 添加列 owner_id ...")
                    _exec(connection, "ALTER TABLE templates ADD COLUMN owner_id INT NULL COMMENT '模板所有者用户ID'")

                # 2) 列：team_id
                if _column_exists(connection, table_name, "team_id"):
                    print("[跳过] 列 team_id 已存在")
                else:
                    print("[执行] 添加列 team_id ...")
                    _exec(connection, "ALTER TABLE templates ADD COLUMN team_id INT NULL COMMENT '所属团队ID'")

                # 3) 列：is_public
                is_public_newly_added = False
                if _column_exists(connection, table_name, "is_public"):
                    print("[跳过] 列 is_public 已存在")
                else:
                    print("[执行] 添加列 is_public ...")
                    _exec(
                        connection,
                        "ALTER TABLE templates ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否公开模板'",
                    )
                    is_public_newly_added = True

                # 兼容历史数据：首次新增 is_public 时，将历史模板默认置为公开
                if is_public_newly_added:
                    print("[执行] 初始化历史数据：将 templates.is_public 置为 TRUE（兼容旧版本）...")
                    _exec(connection, "UPDATE templates SET is_public = TRUE WHERE is_public = FALSE")

                # 4) 索引：idx_templates_owner_id
                if _index_exists(connection, table_name, "idx_templates_owner_id"):
                    print("[跳过] 索引 idx_templates_owner_id 已存在")
                else:
                    print("[执行] 创建索引 idx_templates_owner_id ...")
                    _exec(connection, "CREATE INDEX idx_templates_owner_id ON templates(owner_id)")

                # 5) 索引：idx_templates_team_id
                if _index_exists(connection, table_name, "idx_templates_team_id"):
                    print("[跳过] 索引 idx_templates_team_id 已存在")
                else:
                    print("[执行] 创建索引 idx_templates_team_id ...")
                    _exec(connection, "CREATE INDEX idx_templates_team_id ON templates(team_id)")

                # 6) 索引：idx_templates_owner_team_public
                if _index_exists(connection, table_name, "idx_templates_owner_team_public"):
                    print("[跳过] 索引 idx_templates_owner_team_public 已存在")
                else:
                    print("[执行] 创建索引 idx_templates_owner_team_public ...")
                    _exec(
                        connection,
                        "CREATE INDEX idx_templates_owner_team_public ON templates(owner_id, team_id, is_public)",
                    )

                # 7) 可选：外键
                if ADD_FOREIGN_KEYS:
                    print()
                    print("[步骤] 外键检查与添加（已启用）")

                    # 检查依赖表
                    if not _table_exists(connection, "users"):
                        raise RuntimeError("users 表不存在，无法添加 templates.owner_id 外键")
                    if not _table_exists(connection, "teams"):
                        raise RuntimeError("teams 表不存在，无法添加 templates.team_id 外键")

                    invalid_owner = _count_invalid_fk(connection, "owner_id", "users", "id")
                    invalid_team = _count_invalid_fk(connection, "team_id", "teams", "id")

                    print(f"外键脏数据统计: owner_id 无效={invalid_owner} 条, team_id 无效={invalid_team} 条")

                    if invalid_owner > 0 or invalid_team > 0:
                        raise RuntimeError(
                            "检测到外键脏数据（templates.owner_id/team_id 指向不存在的 users/teams）。\n"
                            "请先清理后再启用 ADD_FOREIGN_KEYS。"
                        )

                    fk_owner = "fk_templates_owner"
                    if _fk_exists(connection, table_name, fk_owner):
                        print(f"[跳过] 外键 {fk_owner} 已存在")
                    else:
                        print(f"[执行] 添加外键 {fk_owner} ...")
                        _exec(
                            connection,
                            "ALTER TABLE templates "
                            "ADD CONSTRAINT fk_templates_owner "
                            "FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL",
                        )

                    fk_team = "fk_templates_team"
                    if _fk_exists(connection, table_name, fk_team):
                        print(f"[跳过] 外键 {fk_team} 已存在")
                    else:
                        print(f"[执行] 添加外键 {fk_team} ...")
                        _exec(
                            connection,
                            "ALTER TABLE templates "
                            "ADD CONSTRAINT fk_templates_team "
                            "FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL",
                        )

                if DRY_RUN:
                    print()
                    print("[DRY_RUN] 未提交事务（仅打印 SQL）")
                    trans.rollback()
                    return True

                trans.commit()
                print()
                print("[成功] 迁移完成！")
                return True

            except Exception as e:
                print(f"[错误] 迁移过程中发生错误: {str(e)}")
                trans.rollback()
                return False

    except Exception as e:
        print(f"[错误] 数据库连接失败: {str(e)}")
        print()
        print("请检查:")
        print("  1. 数据库服务是否运行")
        print("  2. feishu-print-backend/.env 中 DATABASE_URL 配置是否正确")
        print("  3. 是否在 feishu-print-backend 目录下运行，确保 .env 能被 env_file='.env' 读取")
        return False


if __name__ == "__main__":
    ok = run_migration()
    print()
    print("=" * 60)
    if ok:
        print("迁移脚本执行成功")
        sys.exit(0)
    else:
        print("迁移脚本执行失败")
        sys.exit(1)
