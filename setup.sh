#!/bin/bash

# Kdenlive Effect Generator 快速启动脚本

echo "🎬 Kdenlive Effect Generator"
echo "=============================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.7+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# 安装依赖
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# 检查MLT
if ! command -v melt &> /dev/null; then
    echo "⚠️  MLT Framework not found."
    echo "    Please install MLT:"
    echo "    - macOS: brew install mlt"
    echo "    - Ubuntu: sudo apt-get install melt"
    echo "    - Or download from: https://www.mltframework.org/"
    echo ""
fi

# 创建示例素材
echo "🎨 Creating sample assets..."
python3 main.py preview --create-samples

# 生成示例特效
echo "✨ Generating sample effects..."
python3 main.py batch --generate-all --count 3

echo ""
echo "🚀 Setup complete! You can now:"
echo ""
echo "1. Generate effects:"
echo "   python3 main.py generate --style shake --count 5"
echo ""
echo "2. Generate previews:"
echo "   python3 main.py preview --style shake"
echo ""
echo "3. Start web server:"
echo "   python3 main.py web"
echo ""
echo "4. Open browser to: http://localhost:5000"
echo ""

# 询问是否启动Web服务器
read -p "🌐 Start web server now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 Starting web server..."
    python3 main.py web
fi
