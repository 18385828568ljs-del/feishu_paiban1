"""
检查 templates 表结构
"""
from sqlalchemy import create_engine, text
from app.config import settings

def check_table_structure():
    """检查表结构"""
    print("=" * 60)
    print("检查 templates 表结构")
    print("=" * 60)
    print()
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 查询表结构
            result = conn.execute(text("DESCRIBE templates"))
            
            print("templates 表字段：")
            print("-" * 60)
            for row in result:
                print(f"  {row[0]:<20} {row[1]:<20} {row[2]:<10}")
            print()
            
            # 检查是否有 user_id 字段
            result = conn.execute(text("SHOW COLUMNS FROM templates LIKE 'user_id'"))
            has_user_id = result.fetchone() is not None
            
            if has_user_id:
                print("✓ user_id 字段存在")
            else:
                print("❌ user_id 字段不存在")
                print()
                print("需要运行迁移脚本：")
                print("  python run_migration_template_user_id.py")
            
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_table_structure()
