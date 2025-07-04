#!/usr/bin/env python3
"""
Installation and Setup Helper
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} found")
    return True


def install_dependencies():
    """安装Python依赖"""
    try:
        print("📦 Installing Python dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_mlt():
    """检查MLT Framework"""
    mlt_paths = [
        "/Applications/kdenlive.app/Contents/MacOS/melt",
    ]
    
    for path in mlt_paths:
        if os.path.exists(path):
            print(f"✅ MLT found at {path}")
            return path
    
    # 检查系统PATH
    try:
        result = subprocess.run(["melt", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MLT found in system PATH")
            return "melt"
    except FileNotFoundError:
        pass
    
    print("❌ MLT Framework not found")
    print("   Please install MLT:")
    print("   - macOS: brew install mlt")
    print("   - Ubuntu: sudo apt-get install melt")
    print("   - Or download from: https://www.mltframework.org/")
    return None


def create_directories():
    """创建必要的目录"""
    directories = [
        "assets",
        "effects/shake",
        "effects/zoom", 
        "effects/blur",
        "effects/transition",
        "effects/glitch",
        "effects/color",
        "previews",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")


def create_sample_assets():
    """创建示例素材"""
    try:
        from src.preview_generator import PreviewGenerator
        generator = PreviewGenerator(".")
        generator.create_sample_assets()
        print("✅ Sample assets created")
    except Exception as e:
        print(f"⚠️  Could not create sample assets: {e}")


def generate_sample_effects():
    """生成示例特效"""
    try:
        from src.effect_generator import EffectGenerator
        generator = EffectGenerator(".")
        
        styles = ['shake', 'zoom', 'blur', 'transition', 'glitch', 'color']
        total = 0
        
        for style in styles:
            files = generator.generate_effects(style, 2)  # 每种风格生成2个示例
            total += len(files)
            print(f"  Generated {len(files)} {style} effects")
        
        print(f"✅ Generated {total} sample effects")
        
    except Exception as e:
        print(f"⚠️  Could not generate sample effects: {e}")


def create_env_file():
    """创建环境配置文件"""
    env_file = Path(".env")
    if not env_file.exists():
        mlt_path = check_mlt()
        if mlt_path:
            content = f"""# Kdenlive Effect Generator Configuration
MELT_PATH={mlt_path}
PROJECT_NAME=Kdenlive Effect Generator
DEBUG=true
PREVIEW_WIDTH=720
PREVIEW_HEIGHT=1280
PREVIEW_DURATION=5
PREVIEW_FPS=25
WEB_HOST=localhost
WEB_PORT=5000
"""
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Environment file created")


def main():
    print("🎬 Kdenlive Effect Generator Setup")
    print("=" * 40)
    
    # 检查Python版本
    if not check_python():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 检查MLT
    mlt_path = check_mlt()
    
    # 创建目录
    create_directories()
    
    # 创建环境文件
    create_env_file()
    
    # 创建示例素材
    create_sample_assets()
    
    # 生成示例特效
    generate_sample_effects()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Generate effects: python3 main.py generate --style shake --count 5")
    print("2. Generate previews: python3 main.py preview --style shake")
    print("3. Start web server: python3 main.py web")
    print("4. Open browser: http://localhost:5000")
    
    # 询问是否启动Web服务器
    try:
        response = input("\n🌐 Start web server now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("🌐 Starting web server...")
            from src.web_server import EffectPreviewServer
            server = EffectPreviewServer(".")
            server.run()
    except KeyboardInterrupt:
        print("\n👋 Setup complete. You can start the web server later with: python3 main.py web")


if __name__ == "__main__":
    main()
