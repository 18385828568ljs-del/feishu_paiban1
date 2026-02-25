"""
创建管理员账号
用于初始化后台管理系统的管理员账号
"""
from app.database import SessionLocal
from app.models.admin import Admin

def create_default_admin():
    """创建默认管理员账号"""
    print("="*60)
    print("创建管理员账号")
    print("="*60)
    
    db = SessionLocal()
    try:
        # 检查是否已有管理员
        existing = db.query(Admin).filter(Admin.username == "admin").first()
        if existing:
            print("\n✓ 管理员账号已存在")
            print(f"  用户名: {existing.username}")
            print(f"  昵称: {existing.nickname}")
            print(f"  状态: {'激活' if existing.is_active else '禁用'}")
            print(f"  创建时间: {existing.created_at}")
            
            # 询问是否重置密码
            reset = input("\n是否重置密码? (y/n): ").strip().lower()
            if reset == 'y':
                new_password = input("请输入新密码（至少6位）: ").strip()
                if len(new_password) < 6:
                    print("✗ 密码长度不能少于6位")
                    return
                
                existing.set_password(new_password)
                db.commit()
                print("✓ 密码已重置")
            return
        
        # 创建新管理员
        print("\n创建新的管理员账号...")
        
        username = input("请输入用户名（默认: admin）: ").strip() or "admin"
        nickname = input("请输入昵称（默认: 系统管理员）: ").strip() or "系统管理员"
        password = input("请输入密码（默认: admin123）: ").strip() or "admin123"
        
        if len(password) < 6:
            print("✗ 密码长度不能少于6位")
            return
        
        # 检查用户名是否已存在
        existing = db.query(Admin).filter(Admin.username == username).first()
        if existing:
            print(f"✗ 用户名 '{username}' 已存在")
            return
        
        admin = Admin(
            username=username,
            nickname=nickname
        )
        admin.set_password(password)
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n" + "="*60)
        print("✓ 管理员账号创建成功！")
        print("="*60)
        print(f"  用户名: {admin.username}")
        print(f"  昵称: {admin.nickname}")
        print(f"  密码: {password}")
        print(f"  创建时间: {admin.created_at}")
        print("\n⚠️  请妥善保管账号密码！")
        print("⚠️  建议登录后立即修改密码！")
        print("\n登录地址: http://localhost:5156/admin/login")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ 创建失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


def list_admins():
    """列出所有管理员"""
    print("="*60)
    print("管理员列表")
    print("="*60)
    
    db = SessionLocal()
    try:
        admins = db.query(Admin).all()
        
        if not admins:
            print("\n暂无管理员账号")
            return
        
        print(f"\n共 {len(admins)} 个管理员账号:\n")
        for admin in admins:
            status = "✓ 激活" if admin.is_active else "✗ 禁用"
            print(f"  ID: {admin.id}")
            print(f"  用户名: {admin.username}")
            print(f"  昵称: {admin.nickname}")
            print(f"  状态: {status}")
            print(f"  创建时间: {admin.created_at}")
            print("-" * 60)
        
    except Exception as e:
        print(f"\n✗ 查询失败: {str(e)}")
    finally:
        db.close()


def main():
    """主菜单"""
    while True:
        print("\n" + "="*60)
        print("管理员账号管理")
        print("="*60)
        print("1. 创建管理员账号")
        print("2. 查看管理员列表")
        print("3. 退出")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            create_default_admin()
        elif choice == "2":
            list_admins()
        elif choice == "3":
            print("\n再见！")
            break
        else:
            print("\n✗ 无效的选择")


if __name__ == "__main__":
    main()
