#!/usr/bin/env python3
"""
Demo Script - 演示项目功能
"""

import os
import time
import subprocess
from pathlib import Path


def print_banner():
    print("""
🎬 Kdenlive Effect Generator Demo
================================

这个演示将展示如何：
1. 生成多种风格的特效
2. 创建预览视频
3. 启动Web界面查看效果

""")


def run_command(cmd, description):
    print(f"📋 {description}")
    print(f"💻 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Success!")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        print()
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        print()
        return False


def demo():
    print_banner()
    
    # 检查是否在项目目录
    if not Path("main.py").exists():
        print("❌ 请在项目根目录运行此脚本")
        return
    
    input("按Enter开始演示...")
    
    # 1. 生成抖动特效
    print("🎯 步骤 1: 生成抖动特效")
    run_command([
        "python3", "main.py", "generate", 
        "--style", "shake", "--count", "3"
    ], "生成3个抖动特效")
    
    # 2. 生成缩放特效
    print("🎯 步骤 2: 生成缩放特效")
    run_command([
        "python3", "main.py", "generate",
        "--style", "zoom", "--count", "3"
    ], "生成3个缩放特效")
    
    # 3. 生成模糊特效
    print("🎯 步骤 3: 生成模糊特效")
    run_command([
        "python3", "main.py", "generate",
        "--style", "blur", "--count", "3"
    ], "生成3个模糊特效")
    
    # 4. 创建示例素材
    print("🎯 步骤 4: 创建示例素材")
    run_command([
        "python3", "main.py", "preview", "--create-samples"
    ], "创建示例图片和视频素材")
    
    # 5. 生成预览视频
    print("🎯 步骤 5: 生成预览视频")
    print("⚠️  注意: 预览生成需要MLT Framework支持")
    
    # 检查MLT
    try:
        subprocess.run(["melt", "--version"], check=True, capture_output=True)
        print("✅ MLT Framework 已安装")
        
        # 生成抖动特效预览
        run_command([
            "python3", "main.py", "preview", "--style", "shake"
        ], "为抖动特效生成预览视频")
        
    except subprocess.CalledProcessError:
        print("❌ MLT Framework 未安装，跳过预览生成")
        print("   请安装MLT: brew install mlt (macOS) 或 sudo apt-get install melt (Ubuntu)")
    
    # 6. 展示生成的文件
    print("🎯 步骤 6: 查看生成的文件")
    
    effects_dir = Path("effects")
    if effects_dir.exists():
        print("📁 生成的特效文件:")
        for style_dir in effects_dir.iterdir():
            if style_dir.is_dir():
                xml_files = list(style_dir.glob("*.xml"))
                print(f"   {style_dir.name}: {len(xml_files)} 个特效")
                for xml_file in xml_files[:2]:  # 显示前2个
                    print(f"     - {xml_file.name}")
    
    previews_dir = Path("previews")
    if previews_dir.exists():
        print("\n🎥 生成的预览视频:")
        for style_dir in previews_dir.iterdir():
            if style_dir.is_dir():
                mp4_files = list(style_dir.glob("*.mp4"))
                print(f"   {style_dir.name}: {len(mp4_files)} 个预览")
    
    # 7. 启动Web服务器
    print("\n🎯 步骤 7: 启动Web界面")
    print("Web界面将在 http://localhost:5000 启动")
    print("您可以在浏览器中查看和管理特效")
    
    try:
        response = input("\n🌐 启动Web服务器吗? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("🌐 启动Web服务器...")
            print("💡 提示: 使用 Ctrl+C 停止服务器")
            subprocess.run([
                "python3", "main.py", "web"
            ])
    except KeyboardInterrupt:
        print("\n👋 演示结束")
    
    print("\n🎉 演示完成!")
    print("\n📖 更多用法请查看:")
    print("   - README.md: 项目概述")
    print("   - USAGE.md: 详细使用说明")


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\n👋 演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
