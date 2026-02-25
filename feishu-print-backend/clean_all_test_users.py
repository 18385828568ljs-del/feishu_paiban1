"""
清理所有测试用户脚本
删除所有明显的测试用户，只保留真实的飞书用户
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User

def clean_all_test_users():
    """清理所有测试用户"""
    print("=" * 60)
    print("清理所有测试用户")
    print("=" * 60)
    print()
    print("⚠️  此脚本将删除以下特征的用户：")
    print("  - feishu_user_id 不是以 'ou_' 开头")
    print("  - feishu_user_id 包含 'test'")
    print("  - feishu_user_id 包含 'user_00'")
    print("  - 昵称包含 '测试'、'张三'、'李四'、'王五'")
    print()
    
    try:
        # 创建数据库连接
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # 查找所有用户
        all_users = db.query(User).all()
        
        print(f"数据库中共有 {len(all_users)} 个用户")
        print()
        
        # 识别测试用户
        test_users = []
        real_users = []
        
        for user in all_users:
            is_test = False
            reason = []
            
            # 检查 feishu_user_id
            if not user.feishu_user_id.startswith('ou_'):
                is_test = True
                reason.append("不是ou_开头")
            elif 'test' in user.feishu_user_id.lower():
                is_test = True
                reason.append("包含test")
            elif 'user_00' in user.feishu_user_id:
                is_test = True
                reason.append("包含user_00")
            
            # 检查昵称
            if user.nickname:
                test_names = ['测试', '张三', '李四', '王五']
                if any(name in user.nickname for name in test_names):
                    is_test = True
                    reason.append(f"昵称包含测试名称")
            
            if is_test:
                test_users.append((user, reason))
            else:
                real_users.append(user)
        
        print(f"识别出 {len(test_users)} 个测试用户：")
        for user, reason in test_users:
            print(f"  - ID: {user.id}, 飞书ID: {user.feishu_user_id}, 昵称: {user.nickname}, 原因: {', '.join(reason)}")
        print()
        
        print(f"识别出 {len(real_users)} 个真实用户：")
        for user in real_users:
            print(f"  - ID: {user.id}, 飞书ID: {user.feishu_user_id}, 昵称: {user.nickname}")
        print()
        
        if not test_users:
            print("✓ 没有找到测试用户")
            db.close()
            return
        
        # 确认操作
        confirm = input(f"确认删除这 {len(test_users)} 个测试用户？(输入 'yes' 继续): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            db.close()
            return
        
        print()
        print("开始清理...")
        print()
        
        # 获取测试用户的ID和飞书ID
        test_user_ids = [user.id for user, _ in test_users]
        test_feishu_ids = [user.feishu_user_id for user, _ in test_users]
        
        # 1. 删除用户活动记录
        if test_feishu_ids:
            placeholders = ','.join([f"'{fid}'" for fid in test_feishu_ids])
            result = db.execute(
                text(f"DELETE FROM user_activities WHERE feishu_user_id IN ({placeholders})")
            )
            print(f"✓ 删除了 {result.rowcount} 条用户活动记录")
        
        # 2. 删除用户创建的模板（如果字段存在）
        if test_user_ids:
            try:
                placeholders = ','.join(map(str, test_user_ids))
                result = db.execute(
                    text(f"DELETE FROM templates WHERE user_id IN ({placeholders})")
                )
                print(f"✓ 删除了 {result.rowcount} 个用户模板")
            except Exception as e:
                print(f"  跳过模板清理（user_id字段可能不存在）")
        
        # 3. 删除订单记录（如果存在）
        if test_user_ids:
            try:
                placeholders = ','.join(map(str, test_user_ids))
                result = db.execute(
                    text(f"DELETE FROM orders WHERE user_id IN ({placeholders})")
                )
                print(f"✓ 删除了 {result.rowcount} 条订单记录")
            except Exception as e:
                print(f"  跳过订单表（可能不存在）")
        
        # 4. 删除会员信息
        if test_user_ids:
            placeholders = ','.join(map(str, test_user_ids))
            result = db.execute(
                text(f"DELETE FROM memberships WHERE user_id IN ({placeholders})")
            )
            print(f"✓ 删除了 {result.rowcount} 条会员记录")
        
        # 5. 删除用户记录
        if test_feishu_ids:
            placeholders = ','.join([f"'{fid}'" for fid in test_feishu_ids])
            result = db.execute(
                text(f"DELETE FROM users WHERE feishu_user_id IN ({placeholders})")
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
        
        print("当前数据库状态：")
        print(f"  - 剩余用户数: {remaining_users}")
        print()
        
        if remaining_users > 0:
            print("剩余用户列表：")
            remaining_user_list = db.query(User).all()
            for user in remaining_user_list:
                print(f"  - ID: {user.id}, 飞书ID: {user.feishu_user_id}, 昵称: {user.nickname}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 清理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    clean_all_test_users()
