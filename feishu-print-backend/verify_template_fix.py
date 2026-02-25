"""
验证模板修复
"""
from sqlalchemy import create_engine, text
from app.config import settings

def verify_fix():
    """验证修复"""
    print("=" * 60)
    print("验证模板表修复")
    print("=" * 60)
    print()
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 1. 检查表结构
            result = conn.execute(text("SHOW COLUMNS FROM templates LIKE 'owner_id'"))
            has_owner_id = result.fetchone() is not None
            
            result = conn.execute(text("SHOW COLUMNS FROM templates LIKE 'user_id'"))
            has_user_id = result.fetchone() is not None
            
            print("表结构检查：")
            print(f"  owner_id 字段: {'✓ 存在' if has_owner_id else '❌ 不存在'}")
            print(f"  user_id 字段: {'✓ 存在' if has_user_id else '❌ 不存在（正常）'}")
            print()
            
            # 2. 检查模板数量
            result = conn.execute(text("SELECT COUNT(*) FROM templates"))
            total = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) FROM templates WHERE is_system = 1"))
            system_count = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) FROM templates WHERE owner_id IS NOT NULL"))
            user_count = result.fetchone()[0]
            
            print("模板统计：")
            print(f"  总模板数: {total}")
            print(f"  系统模板: {system_count}")
            print(f"  用户模板: {user_count}")
            print()
            
            if has_owner_id:
                print("✓ 修复成功！")
                print()
                print("下一步：重启后端服务")
                print("  方法1: 运行 restart-server.bat")
                print("  方法2: 手动停止并重新运行 run_server.py")
            else:
                print("❌ owner_id 字段不存在")
                print("需要检查数据库表结构")
            
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_fix()
