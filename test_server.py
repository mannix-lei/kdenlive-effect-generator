#!/usr/bin/env python3
"""
测试Web服务器
"""

import sys
import requests
import time
import subprocess
from pathlib import Path


def test_server():
    """测试服务器是否正常运行"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing web server...")
    
    # 测试主页
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Home page accessible")
        else:
            print(f"❌ Home page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach server: {e}")
        return False
    
    # 测试API
    try:
        response = requests.get(f"{base_url}/api/styles", timeout=5)
        if response.status_code == 200:
            styles = response.json()
            print(f"✅ API working, found {len(styles)} styles")
        else:
            print(f"❌ API error: {response.status_code}")
    except Exception as e:
        print(f"❌ API error: {e}")
    
    return True


def check_files():
    """检查必要的文件是否存在"""
    print("📁 Checking project files...")
    
    required_files = [
        "web/templates/index.html",
        "web/static/style.css", 
        "web/static/app.js",
        "src/web_server.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files present")
        return True


def main():
    print("🔧 Web Server Diagnostics")
    print("=" * 30)
    
    # 检查文件
    if not check_files():
        print("\n❌ Please ensure all project files are in place")
        return
    
    # 生成一些测试数据
    print("\n📊 Creating test data...")
    try:
        from src.effect_generator import EffectGenerator
        generator = EffectGenerator(".")
        files = generator.generate_effects("shake", 2)
        print(f"✅ Generated {len(files)} test effects")
    except Exception as e:
        print(f"⚠️  Could not generate test effects: {e}")
    
    print("\n🌐 Server should now be accessible at http://localhost:5000")
    print("💡 If you see 403 errors, try:")
    print("   1. Check file permissions: chmod -R 755 web/")
    print("   2. Restart the server")
    print("   3. Try a different port: python3 main.py web --port 8080")


if __name__ == "__main__":
    main()
