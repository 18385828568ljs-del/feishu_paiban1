"""
数据库迁移：添加 user_id 字段到 templates 表
用于实现模板数据隔离
"""
from app.database import engine
from sqlalchemy import text
import os

def run_migration():
    print("="*60)
    print("数据库迁移：添加 user_id 字段到 templates 表")
    print("="*60)
    print("\n⚠️  重要提示：")
    print("  - 此迁移将添加 user_id 字段到 templates 表")
    print("  - 现有模板的 user_id 将为 NULL（系统模板）")
    print("  - 新创建的模板将自动关联到创建者")
    print("\n" + "="*60)
    
    input("按 Enter 键继续...")
    
    with engine.connect() as conn:
        try:
            # 检查字段是否已存在
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'feishu_print'
                AND TABLE_NAME = 'templates'
                AND COLUMN_NAME = 'user_id'
            """))
            
            count = result.fetchone()[0]
            
            if count > 0:
                print("\n✓ user_id 字段已存在，跳过迁移")
                return
            
            print("\n开始迁移...")
            
            # 读取 SQL 文件
            sql_file = os.path.join(os.path.dirname(__file__), 'migration_add_template_user_id.sql')
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            # 分割并执行 SQL 语句
            statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for i, statement in enumerate(statements, 1):
                if statement.upper().startswith('USE'):
                    continue  # 跳过 USE 语句
                
                if statement.upper().startswith('SELECT'):
                    result = conn.execute(text(statement))
                    row = result.fetchone()
                    if row:
                        print(f"\n{row[0]}")
                else:
                    conn.execute(text(statement))
                    print(f"  ✓ 执行语句 {i}/{len(statements)}")
            
            conn.commit()
            
            print("\n" + "="*60)
            print("✓ 迁移成功！")
            print("="*60)
            print("\n下一步：")
            print("1. 更新代码（使用新的模板路由）")
            print("2. 重启后端服务")
            print("3. 测试模板功能")
            
        except Exception as e:
            print(f"\n✗ 迁移失败: {str(e)}")
            conn.rollback()
            raise

if __name__ == "__main__":
    run_migration()
