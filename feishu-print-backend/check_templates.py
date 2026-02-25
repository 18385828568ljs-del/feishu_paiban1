#!/usr/bin/env python3
"""检查模板数据"""
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
        # 查询所有模板
        print("=" * 80)
        print("所有模板（最近10条）:")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT id, name, template_type, is_system, owner_id, created_at 
            FROM templates 
            ORDER BY id DESC 
            LIMIT 10
        """))
        
        rows = result.fetchall()
        if rows:
            print(f"{'ID':<5} {'名称':<30} {'类型':<10} {'系统':<6} {'所有者':<8} {'创建时间':<20}")
            print("-" * 80)
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<30} {row[2] or 'NULL':<10} {row[3]:<6} {row[4] or 'NULL':<8} {str(row[5]):<20}")
        else:
            print("没有找到任何模板")
        
        print("\n" + "=" * 80)
        print("AI 模板:")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT id, name, template_type, is_system, owner_id, created_at 
            FROM templates 
            WHERE template_type = 'ai'
            ORDER BY id DESC
        """))
        
        rows = result.fetchall()
        if rows:
            print(f"{'ID':<5} {'名称':<30} {'类型':<10} {'系统':<6} {'所有者':<8} {'创建时间':<20}")
            print("-" * 80)
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<30} {row[2] or 'NULL':<10} {row[3]:<6} {row[4] or 'NULL':<8} {str(row[5]):<20}")
        else:
            print("没有找到 AI 模板")
        
        print("\n" + "=" * 80)
        print("用户信息:")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT id, feishu_user_id, username 
            FROM users 
            ORDER BY id DESC 
            LIMIT 5
        """))
        
        rows = result.fetchall()
        if rows:
            print(f"{'ID':<5} {'飞书用户ID':<40} {'用户名':<20}")
            print("-" * 80)
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<40} {row[2] or 'NULL':<20}")
        else:
            print("没有找到用户")
        
        print("\n" + "=" * 80)
        print("模板统计:")
        print("=" * 80)
        result = conn.execute(text("""
            SELECT 
                template_type,
                COUNT(*) as count,
                SUM(CASE WHEN is_system = 1 THEN 1 ELSE 0 END) as system_count,
                SUM(CASE WHEN is_system = 0 THEN 1 ELSE 0 END) as user_count
            FROM templates
            GROUP BY template_type
        """))
        
        rows = result.fetchall()
        if rows:
            print(f"{'类型':<15} {'总数':<10} {'系统模板':<12} {'用户模板':<12}")
            print("-" * 80)
            for row in rows:
                print(f"{row[0] or 'NULL':<15} {row[1]:<10} {row[2]:<12} {row[3]:<12}")
        else:
            print("没有模板数据")
            
except Exception as e:
    print(f"错误: {e}")
    sys.exit(1)
