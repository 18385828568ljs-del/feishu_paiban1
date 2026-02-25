#!/usr/bin/env python3
"""调试模板查询问题"""
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. 检查用户
        print("=" * 80)
        print("1. 用户信息")
        print("=" * 80)
        result = conn.execute(text("SELECT id, feishu_user_id, nickname FROM users"))
        users = result.fetchall()
        for u in users:
            print(f"ID: {u[0]}, 飞书ID: {u[1]}, 昵称: {u[2]}")
        
        # 2. 检查所有模板
        print("\n" + "=" * 80)
        print("2. 所有模板")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT id, name, template_type, is_system, owner_id 
            FROM templates 
            ORDER BY id DESC 
            LIMIT 15
        """))
        templates = result.fetchall()
        print(f"{'ID':<5} {'名称':<20} {'类型':<10} {'系统':<6} {'所有者':<8}")
        print("-" * 80)
        for t in templates:
            print(f"{t[0]:<5} {t[1]:<20} {t[2] or 'NULL':<10} {t[3]:<6} {str(t[4]) if t[4] else 'NULL':<8}")
        
        # 3. 模拟查询逻辑 - 未登录
        print("\n" + "=" * 80)
        print("3. 模拟查询 - 未登录用户")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT id, name, template_type, is_system, owner_id 
            FROM templates 
            WHERE is_system = 1
            ORDER BY id DESC
        """))
        templates = result.fetchall()
        print(f"查询到 {len(templates)} 个模板")
        
        # 4. 模拟查询逻辑 - 已登录用户 (user_id=2)
        print("\n" + "=" * 80)
        print("4. 模拟查询 - 已登录用户 (ID=2)")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT id, name, template_type, is_system, owner_id 
            FROM templates 
            WHERE is_system = 1 OR owner_id = 2 OR (owner_id IS NULL AND is_system = 0)
            ORDER BY id DESC
        """))
        templates = result.fetchall()
        print(f"查询到 {len(templates)} 个模板")
        for t in templates[:10]:
            print(f"{t[0]:<5} {t[1]:<20} {t[2] or 'NULL':<10} {t[3]:<6} {str(t[4]) if t[4] else 'NULL':<8}")
        
        # 5. 模拟查询逻辑 - 已登录用户 + AI类型过滤
        print("\n" + "=" * 80)
        print("5. 模拟查询 - 已登录用户 (ID=2) + template_type='ai'")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT id, name, template_type, is_system, owner_id 
            FROM templates 
            WHERE (is_system = 1 OR owner_id = 2 OR (owner_id IS NULL AND is_system = 0))
            AND template_type = 'ai'
            ORDER BY id DESC
        """))
        templates = result.fetchall()
        print(f"查询到 {len(templates)} 个 AI 模板")
        print(f"{'ID':<5} {'名称':<20} {'类型':<10} {'系统':<6} {'所有者':<8}")
        print("-" * 80)
        for t in templates:
            print(f"{t[0]:<5} {t[1]:<20} {t[2] or 'NULL':<10} {t[3]:<6} {str(t[4]) if t[4] else 'NULL':<8}")
        
        # 6. 检查是否有 owner_id=2 的 AI 模板
        print("\n" + "=" * 80)
        print("6. 检查 owner_id=2 的 AI 模板")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT id, name, template_type, is_system, owner_id 
            FROM templates 
            WHERE owner_id = 2 AND template_type = 'ai'
            ORDER BY id DESC
        """))
        templates = result.fetchall()
        print(f"查询到 {len(templates)} 个模板")
        for t in templates:
            print(f"{t[0]:<5} {t[1]:<20} {t[2] or 'NULL':<10} {t[3]:<6} {str(t[4]) if t[4] else 'NULL':<8}")
            
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
