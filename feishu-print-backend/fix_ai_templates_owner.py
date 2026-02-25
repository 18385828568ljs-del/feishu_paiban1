#!/usr/bin/env python3
"""修复 AI 模板的 owner_id"""
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:18385828568ljs@localhost:3306/feishu_print')

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 获取最新的用户（假设是当前用户）
        result = conn.execute(text("SELECT id, feishu_user_id FROM users ORDER BY updated_at DESC LIMIT 1"))
        user = result.fetchone()
        
        if not user:
            print("错误: 没有找到用户")
            sys.exit(1)
        
        user_id = user[0]
        feishu_user_id = user[1]
        
        print(f"找到用户: ID={user_id}, 飞书ID={feishu_user_id}")
        
        # 查找 owner_id 为 NULL 的 AI 模板
        result = conn.execute(text("""
            SELECT id, name, template_type 
            FROM templates 
            WHERE owner_id IS NULL AND is_system = 0
            ORDER BY id DESC
        """))
        
        templates = result.fetchall()
        
        if not templates:
            print("没有找到需要修复的模板")
            sys.exit(0)
        
        print(f"\n找到 {len(templates)} 个需要修复的模板:")
        print("-" * 80)
        for t in templates:
            print(f"ID: {t[0]}, 名称: {t[1]}, 类型: {t[2]}")
        
        # 询问是否继续
        response = input(f"\n是否将这些模板的 owner_id 设置为 {user_id}? (y/n): ")
        
        if response.lower() != 'y':
            print("已取消")
            sys.exit(0)
        
        # 更新模板
        result = conn.execute(text("""
            UPDATE templates 
            SET owner_id = :user_id 
            WHERE owner_id IS NULL AND is_system = 0
        """), {"user_id": user_id})
        
        conn.commit()
        
        print(f"\n✅ 成功更新 {result.rowcount} 个模板")
        
        # 验证更新
        result = conn.execute(text("""
            SELECT id, name, template_type, owner_id 
            FROM templates 
            WHERE owner_id = :user_id
            ORDER BY id DESC
            LIMIT 10
        """), {"user_id": user_id})
        
        templates = result.fetchall()
        
        print(f"\n用户 {user_id} 的模板 (最近10条):")
        print("-" * 80)
        print(f"{'ID':<5} {'名称':<30} {'类型':<10} {'所有者':<10}")
        print("-" * 80)
        for t in templates:
            print(f"{t[0]:<5} {t[1]:<30} {t[2] or 'NULL':<10} {t[3]:<10}")
            
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
