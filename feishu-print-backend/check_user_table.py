#!/usr/bin/env python3
"""检查用户表结构"""
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:18385828568ljs@localhost:3306/feishu_print')

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    # 检查 users 表结构
    print("=" * 80)
    print("users 表结构:")
    print("=" * 80)
    
    if 'users' in inspector.get_table_names():
        columns = inspector.get_columns('users')
        print(f"{'列名':<30} {'类型':<20} {'可空':<10} {'默认值':<20}")
        print("-" * 80)
        for col in columns:
            nullable = "YES" if col['nullable'] else "NO"
            default = str(col['default']) if col['default'] is not None else "NULL"
            print(f"{col['name']:<30} {str(col['type']):<20} {nullable:<10} {default:<20}")
    else:
        print("users 表不存在")
    
    # 查询用户数据
    with engine.connect() as conn:
        print("\n" + "=" * 80)
        print("用户数据:")
        print("=" * 80)
        result = conn.execute(text("SELECT * FROM users LIMIT 5"))
        
        rows = result.fetchall()
        if rows:
            # 获取列名
            columns = result.keys()
            print(" | ".join(columns))
            print("-" * 80)
            for row in rows:
                print(" | ".join(str(v) if v is not None else "NULL" for v in row))
        else:
            print("没有找到用户数据")
            
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
