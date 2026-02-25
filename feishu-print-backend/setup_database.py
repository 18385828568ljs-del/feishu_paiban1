"""
数据库配置向导
帮助用户配置正确的数据库连接
"""
import os
import sys
from pathlib import Path

def setup_database():
    print("="*60)
    print("数据库配置向导")
    print("="*60)
    
    # 读取当前 .env 文件
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("✗ .env 文件不存在")
        return
    
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    print("\n当前数据库配置:")
    for line in env_content.split('\n'):
        if line.startswith('DATABASE_URL'):
            print(f"  {line}")
            break
    
    print("\n" + "="*60)
    print("请选择配置方式:")
    print("="*60)
    print("1. 使用 MySQL root 用户（无密码）")
    print("2. 使用 MySQL root 用户（有密码）")
    print("3. 手动输入完整的数据库连接字符串")
    print("4. 退出")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == "1":
        # root 无密码
        new_url = "mysql+pymysql://root@localhost:3306/feishu_print"
        print(f"\n将使用: {new_url}")
        
    elif choice == "2":
        # root 有密码
        password = input("\n请输入 MySQL root 密码: ").strip()
        new_url = f"mysql+pymysql://root:{password}@localhost:3306/feishu_print"
        print(f"\n将使用: mysql+pymysql://root:***@localhost:3306/feishu_print")
        
    elif choice == "3":
        # 手动输入
        print("\n格式: mysql+pymysql://用户名:密码@主机:端口/数据库名")
        print("示例: mysql+pymysql://root:123456@localhost:3306/feishu_print")
        new_url = input("\n请输入完整连接字符串: ").strip()
        
    elif choice == "4":
        print("\n已退出")
        return
    else:
        print("\n✗ 无效的选择")
        return
    
    # 更新 .env 文件
    print("\n正在更新 .env 文件...")
    
    new_content = []
    for line in env_content.split('\n'):
        if line.startswith('DATABASE_URL'):
            new_content.append(f"DATABASE_URL={new_url}")
        else:
            new_content.append(line)
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_content))
    
    print("✓ .env 文件已更新")
    
    # 测试连接
    print("\n正在测试数据库连接...")
    
    try:
        # 临时设置环境变量
        os.environ['DATABASE_URL'] = new_url
        
        from sqlalchemy import create_engine
        engine = create_engine(new_url)
        
        # 尝试连接
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✓ 数据库连接成功！")
        
        # 检查数据库是否存在
        with engine.connect() as conn:
            result = conn.execute(text("SHOW DATABASES LIKE 'feishu_print'"))
            if result.fetchone():
                print("✓ 数据库 feishu_print 已存在")
            else:
                print("✗ 数据库 feishu_print 不存在")
                create_db = input("\n是否创建数据库? (y/n): ").strip().lower()
                if create_db == 'y':
                    # 连接到 mysql 数据库创建新数据库
                    base_url = new_url.rsplit('/', 1)[0]
                    admin_engine = create_engine(base_url + '/mysql')
                    with admin_engine.connect() as conn:
                        conn.execute(text("CREATE DATABASE feishu_print CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                        conn.commit()
                    print("✓ 数据库已创建")
        
        print("\n" + "="*60)
        print("配置完成！")
        print("="*60)
        print("\n下一步:")
        print("1. 运行数据库迁移: python run_migration_security.py")
        print("2. 启动后端服务: python run_server.py")
        print("3. 运行测试脚本: python test_user_simple.py")
        
    except Exception as e:
        print(f"✗ 数据库连接失败: {str(e)}")
        print("\n请检查:")
        print("1. MySQL 服务是否正在运行")
        print("2. 用户名和密码是否正确")
        print("3. 数据库是否存在")
        print("\n可以重新运行此脚本进行配置")

if __name__ == "__main__":
    setup_database()
