"""
数据库迁移脚本：创建 membership_plans 表并写入默认会员计划
"""
import sys
import io
from sqlalchemy import text
from app.database import engine
from app.config import settings

# 设置标准输出编码为 UTF-8（Windows 兼容）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


DEFAULT_PLANS = [
    {"id": "pro", "name": "专业版", "price": 2900, "original_price": 5900, "duration_days": 30},
    {"id": "team", "name": "团队版", "price": 9900, "original_price": 19900, "duration_days": 30},
]


def run_migration() -> bool:
    print("=" * 60)
    print("开始执行数据库迁移：创建 membership_plans 表")
    print("=" * 60)
    print(
        f"数据库连接: {settings.database_url.split('@')[-1] if '@' in settings.database_url else '已配置'}"
    )
    print()

    try:
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # 创建表（如果不存在）
                print("正在创建 membership_plans 表（如果不存在）...")
                connection.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS membership_plans (
                          id VARCHAR(32) PRIMARY KEY,
                          name VARCHAR(50) NOT NULL,
                          price INT NOT NULL,
                          original_price INT NULL,
                          duration_days INT NOT NULL DEFAULT 30,
                          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                        """
                    )
                )
                print("[成功] 表检查/创建完成")
                print()

                # 写入默认数据（upsert）
                print("正在写入/更新默认会员计划...")
                for p in DEFAULT_PLANS:
                    connection.execute(
                        text(
                            """
                            INSERT INTO membership_plans (id, name, price, original_price, duration_days)
                            VALUES (:id, :name, :price, :original_price, :duration_days)
                            ON DUPLICATE KEY UPDATE
                              name = VALUES(name),
                              price = VALUES(price),
                              original_price = VALUES(original_price),
                              duration_days = VALUES(duration_days);
                            """
                        ),
                        p,
                    )
                print("[成功] 默认数据写入完成")
                print()

                # 验证
                result = connection.execute(text("SELECT id, name, price, original_price, duration_days FROM membership_plans ORDER BY id"))
                rows = result.fetchall()
                print("当前 membership_plans 数据：")
                for r in rows:
                    print(f"  - {r[0]}: {r[1]} price={r[2]} original={r[3]} days={r[4]}")
                print()

                trans.commit()
                return True
            except Exception as e:
                print(f"[错误] 迁移过程中发生错误: {str(e)}")
                import traceback

                traceback.print_exc()
                trans.rollback()
                return False
    except Exception as e:
        print(f"[错误] 数据库连接失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    ok = run_migration()
    print()
    print("=" * 60)
    if ok:
        print("迁移完成！")
        sys.exit(0)
    print("迁移失败！")
    sys.exit(1)








