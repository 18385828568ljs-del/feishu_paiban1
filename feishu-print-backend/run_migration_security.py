"""
运行安全功能迁移脚本
添加 security_level 字段和 user_activities 表
"""
import os
import sys
from dotenv import load_dotenv
import pymysql
from urllib.parse import urlparse

# 加载环境变量
load_dotenv()

def parse_database_url(url: str) -> dict:
    """解析数据库连接字符串"""
    # 移除 mysql+pymysql:// 前缀
    url = url.replace('mysql+pymysql://', 'mysql://')
    parsed = urlparse(url)
    
    return {
        'host': parsed.hostname,
        'port': parsed.port or 3306,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/')
    }

def run_migration():
    """执行迁移"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("错误：未找到 DATABASE_URL 环境变量")
        sys.exit(1)
    
    # 解析数据库连接信息
    db_config = parse_database_url(database_url)
    
    print(f"连接到数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 读取 SQL 文件
        with open('migration_add_security_features.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 分割并执行每个 SQL 语句
        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"\n执行语句 {i}/{len(statements)}:")
                print(statement[:100] + '...' if len(statement) > 100 else statement)
                try:
                    cursor.execute(statement)
                    connection.commit()
                    print("✓ 执行成功")
                except pymysql.err.OperationalError as e:
                    if 'Duplicate column name' in str(e) or 'already exists' in str(e):
                        print(f"⚠ 跳过（已存在）: {e}")
                    else:
                        raise
        
        print("\n" + "="*50)
        print("✓ 迁移完成！")
        print("="*50)
        
        # 验证迁移结果
        print("\n验证迁移结果:")
        
        # 检查 users 表的 security_level 字段
        cursor.execute("SHOW COLUMNS FROM users LIKE 'security_level'")
        if cursor.fetchone():
            print("✓ users.security_level 字段已添加")
        else:
            print("✗ users.security_level 字段未找到")
        
        # 检查 user_activities 表
        cursor.execute("SHOW TABLES LIKE 'user_activities'")
        if cursor.fetchone():
            print("✓ user_activities 表已创建")
            cursor.execute("SELECT COUNT(*) FROM user_activities")
            count = cursor.fetchone()[0]
            print(f"  当前记录数: {count}")
        else:
            print("✗ user_activities 表未找到")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    print("="*50)
    print("安全功能数据库迁移")
    print("="*50)
    run_migration()
