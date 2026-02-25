"""
清理测试数据脚本
删除所有测试用户及其相关数据，只保留真实的飞书用户
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User, Membership
from app.models.admin import Admin
from app.database import get_db

def clean_test_data():
    """清理所有测试数据"""
    print("=" * 60)
    print("清理测试数据")
    print("=" * 60)
    print()
    print("⚠️  警告：此操作将删除以下数据：")
    print("  - 所有测试用户（feishu_user_id 不是以 'ou_' 开头的用户）")
    print("  - 用户的会员信息")
    print("  - 用户的活动记录")
    print("  - 用户创建的模板")
    print("  - 用户的订单记录")
    print()
    print("✓ 保留的数据：")
    print("  - 真实飞书用户（feishu_user_id 以 'ou_' 开头）")
    print("  - 系统模板（user_id 为 NULL 的模板）")
    print("  - 管理员账号")
    print()
    
    # 确认操作
    confirm = input("确认清理测试数据？(输入 'yes' 继续): ")
    if confirm.lower() != 'yes':
        print("❌ 操作已取消")
        return
    
    print()
    print("开始清理...")
    print()
    
    try:
        # 创建数据库连接
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # 1. 查找所有测试用户（不是以 'ou_' 开头的用户）
        test_users = db.query(User).filter(
            ~User.feishu_user_id.like('ou_%')
        ).all()
        
        if not test_users:
            print("✓ 没有找到测试用户")
            db.close()
            return
        
        print(f"找到 {len(test_users)} 个测试用户：")
        for user in test_users:
            print(f"  - ID: {user.id}, 飞书ID: {user.feishu_user_id}, 昵称: {user.nickname}")
        print()
        
        # 获取测试用户的ID列表
        test_user_ids = [user.id for user in test_users]
        
        # 2. 删除用户活动记录
        result = db.execute(
            text("DELETE FROM user_activities WHERE feishu_user_id NOT LIKE 'ou_%'")
        )
        print(f"✓ 删除了 {result.rowcount} 条用户活动记录")
        
        # 3. 删除用户创建的模板（检查字段是否存在）
        try:
            result = db.execute(
                text(f"DELETE FROM templates WHERE user_id IN ({','.join(map(str, test_user_ids))})")
            ) if test_user_ids else None
            if result:
                print(f"✓ 删除了 {result.rowcount} 个用户模板")
        except Exception as e:
            print(f"  跳过模板清理（user_id字段可能不存在）: {e}")
        
        # 4. 删除订单记录（如果存在）
        try:
            result = db.execute(
                text(f"DELETE FROM orders WHERE user_id IN ({','.join(map(str, test_user_ids))})")
            ) if test_user_ids else None
            if result:
                print(f"✓ 删除了 {result.rowcount} 条订单记录")
        except Exception as e:
            print(f"  跳过订单表（可能不存在）: {e}")
        
        # 5. 删除会员信息
        result = db.execute(
            text(f"DELETE FROM memberships WHERE user_id IN ({','.join(map(str, test_user_ids))})")
        ) if test_user_ids else None
        if result:
            print(f"✓ 删除了 {result.rowcount} 条会员记录")
        
        # 6. 删除用户记录
        result = db.execute(
            text("DELETE FROM users WHERE feishu_user_id NOT LIKE 'ou_%'")
        )
        print(f"✓ 删除了 {result.rowcount} 个测试用户")
        
        # 提交事务
        db.commit()
        
        print()
        print("=" * 60)
        print("✓ 清理完成！")
        print("=" * 60)
        print()
        
        # 显示剩余用户统计
        remaining_users = db.query(User).count()
        real_users = db.query(User).filter(User.feishu_user_id.like('ou_%')).count()
        
        print("当前数据库状态：")
        print(f"  - 总用户数: {remaining_users}")
        print(f"  - 真实飞书用户: {real_users}")
        print()
        
        if real_users > 0:
            print("真实用户列表：")
            real_user_list = db.query(User).filter(User.feishu_user_id.like('ou_%')).all()
            for user in real_user_list:
                print(f"  - ID: {user.id}, 飞书ID: {user.feishu_user_id}, 昵称: {user.nickname}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 清理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    clean_test_data()
