"""
数据库迁移脚本：为 templates 表添加 is_system 字段
"""
import sys
import io
from sqlalchemy import text
from app.database import engine
from app.config import settings

# 设置标准输出编码为 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_migration():
    """执行数据库迁移"""
    print("=" * 60)
    print("开始执行数据库迁移：添加 is_system 字段")
    print("=" * 60)
    print(f"数据库连接: {settings.database_url.split('@')[-1] if '@' in settings.database_url else '已配置'}")
    print()
    
    try:
        with engine.connect() as connection:
            # 开始事务
            trans = connection.begin()
            
            try:
                # 检查表是否存在
                check_table = text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'templates'
                """)
                result = connection.execute(check_table)
                table_exists = result.fetchone()[0] > 0
                
                if not table_exists:
                    print("[错误] templates 表不存在！")
                    print("请先确保数据库表已创建。")
                    trans.rollback()
                    return False
                
                # 检查字段是否已存在
                check_column = text("""
                    SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'templates'
                    AND COLUMN_NAME = 'is_system'
                """)
                result = connection.execute(check_column)
                column_info = result.fetchone()
                
                if column_info:
                    print("[提示] is_system 字段已存在，跳过添加字段步骤")
                    print(f"  - 字段类型: {column_info[1]}")
                    print(f"  - 是否可空: {column_info[2]}")
                    print(f"  - 默认值: {column_info[3] or '(无)'}")
                    print()
                else:
                    # 执行迁移：添加字段
                    print("正在添加 is_system 字段...")
                    alter_sql = text("""
                        ALTER TABLE templates 
                        ADD COLUMN is_system BOOLEAN DEFAULT FALSE NOT NULL 
                        AFTER template_type
                    """)
                    connection.execute(alter_sql)
                    print("[成功] 字段添加成功！")
                    print()
                
                # 为现有数据设置默认值（确保所有现有模版都是非系统模版）
                print("正在更新现有数据的 is_system 值...")
                update_sql = text("""
                    UPDATE templates 
                    SET is_system = FALSE 
                    WHERE is_system IS NULL
                """)
                result = connection.execute(update_sql)
                updated_rows = result.rowcount
                print(f"[成功] 已更新 {updated_rows} 条记录的 is_system 值")
                print()
                
                # 验证迁移结果
                result = connection.execute(check_column)
                column_info = result.fetchone()
                
                if column_info:
                    print("[成功] 迁移成功！")
                    print()
                    print("验证结果:")
                    print(f"  - 字段名称: {column_info[0]}")
                    print(f"  - 字段类型: {column_info[1]}")
                    print(f"  - 是否可空: {column_info[2]}")
                    print(f"  - 默认值: {column_info[3] or '(无)'}")
                    
                    # 统计系统模版和用户模版数量
                    count_sql = text("""
                        SELECT is_system, COUNT(*) as count
                        FROM templates
                        GROUP BY is_system
                    """)
                    result = connection.execute(count_sql)
                    counts = result.fetchall()
                    print()
                    print("模版类型统计:")
                    for row in counts:
                        template_type = "系统模版" if row[0] else "用户模版"
                        print(f"  - {template_type}: {row[1]} 个")
                    
                    # 提交事务
                    trans.commit()
                    return True
                else:
                    print("[错误] 迁移后验证失败！")
                    trans.rollback()
                    return False
                    
            except Exception as e:
                print(f"[错误] 迁移过程中发生错误: {str(e)}")
                import traceback
                traceback.print_exc()
                trans.rollback()
                return False
                
    except Exception as e:
        print(f"[错误] 数据库连接失败: {str(e)}")
        print()
        print("请检查:")
        print("  1. 数据库服务是否运行")
        print("  2. .env 文件中的 DATABASE_URL 配置是否正确")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    print()
    print("=" * 60)
    if success:
        print("迁移完成！")
        sys.exit(0)
    else:
        print("迁移失败！")
        sys.exit(1)

