#!/usr/bin/env python3
"""完整测试模板查询流程"""
import sys
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import json

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
API_BASE = 'http://localhost:8000'

print("=" * 80)
print("完整流程测试")
print("=" * 80)

try:
    # 1. 检查数据库
    print("\n1. 检查数据库中的 AI 模板")
    print("-" * 80)
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, name, template_type, is_system, owner_id 
            FROM templates 
            WHERE template_type = 'ai'
            ORDER BY id DESC
        """))
        templates = result.fetchall()
        print(f"数据库中有 {len(templates)} 个 AI 模板")
        for t in templates[:5]:
            print(f"  ID: {t[0]}, 名称: {t[1]}, 所有者: {t[4]}")
    
    # 2. 测试未登录请求
    print("\n2. 测试未登录请求 (无 token)")
    print("-" * 80)
    response = requests.get(f"{API_BASE}/api/templates/", params={'template_type': 'ai'})
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"返回 {len(data)} 个模板")
        for t in data[:3]:
            print(f"  ID: {t['id']}, 名称: {t['name']}")
    else:
        print(f"错误: {response.text}")
    
    # 3. 模拟用户登录并获取 token
    print("\n3. 模拟用户登录")
    print("-" * 80)
    feishu_user_id = 'ou_b31756a18c7f43f29734f9e7bd79e8e3'
    response = requests.post(
        f"{API_BASE}/api/user/init",
        json={
            'feishu_user_id': feishu_user_id,
            'tenant_key': '145b59171ac65740'
        }
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        session_token = data.get('session_token')
        if session_token:
            print(f"✅ 获取到 session_token: {session_token[:50]}...")
            
            # 4. 使用 token 请求模板
            print("\n4. 使用 token 请求 AI 模板")
            print("-" * 80)
            headers = {'Authorization': f'Bearer {session_token}'}
            response = requests.get(
                f"{API_BASE}/api/templates/",
                params={'template_type': 'ai'},
                headers=headers
            )
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 返回 {len(data)} 个 AI 模板")
                for t in data[:5]:
                    print(f"  ID: {t['id']}, 名称: {t['name']}, 所有者: {t.get('owner_id')}")
            else:
                print(f"❌ 错误: {response.text}")
        else:
            print("❌ 未获取到 session_token")
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ 登录失败: {response.text}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
