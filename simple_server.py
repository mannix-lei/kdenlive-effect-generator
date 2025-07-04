#!/usr/bin/env python3
"""
简化的Web服务器启动脚本 - 用于调试403错误
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from flask import Flask, render_template, jsonify, send_file, send_from_directory, request
import json

app = Flask(__name__, 
           template_folder='web/templates',
           static_folder='web/static')

app.config['SECRET_KEY'] = 'kdenlive-effect-generator'

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/test')
def test():
    """测试页面"""
    return render_template('test.html')

@app.route('/api/styles')
def get_styles():
    """获取所有风格"""
    print("🔍 API called: /api/styles")
    
    effects_dir = Path("effects")
    styles = []
    
    print(f"📁 Effects directory: {effects_dir.absolute()}")
    print(f"📁 Effects directory exists: {effects_dir.exists()}")
    
    if effects_dir.exists():
        style_dirs = [d for d in effects_dir.iterdir() if d.is_dir()]
        print(f"📂 Found {len(style_dirs)} style directories")
        
        for style_dir in style_dirs:
            effect_count = len(list(style_dir.glob("*.xml")))
            preview_dir = Path("previews") / style_dir.name
            preview_count = len(list(preview_dir.glob("*.mp4"))) if preview_dir.exists() else 0
            
            style_data = {
                "name": style_dir.name,
                "effect_count": effect_count,
                "preview_count": preview_count
            }
            
            styles.append(style_data)
            print(f"  ➕ Style: {style_dir.name} ({effect_count} effects, {preview_count} previews)")
    
    print(f"🎨 Returning {len(styles)} styles")
    return jsonify(styles)

@app.route('/api/effects/<style>')
def get_effects_by_style(style):
    """获取指定风格的特效列表"""
    print(f"🔍 API called: /api/effects/{style}")
    
    effects_dir = Path("effects") / style
    previews_dir = Path("previews") / style
    
    print(f"📁 Effects dir: {effects_dir.absolute()}")
    print(f"📁 Effects dir exists: {effects_dir.exists()}")
    
    effects = []
    
    if effects_dir.exists():
        xml_files = list(effects_dir.glob("*.xml"))
        print(f"📄 Found {len(xml_files)} XML files")
        
        for effect_file in xml_files:
            preview_file = previews_dir / f"{effect_file.stem}_preview.mp4"
            
            effect_data = {
                "id": effect_file.stem,
                "name": effect_file.stem,
                "description": f"{style.title()} effect",
                "author": "AI Generator",
                "effect_file": f"effects/{style}/{effect_file.name}",
                "preview_file": f"previews/{style}/{preview_file.name}" if preview_file.exists() else None,
                "has_preview": preview_file.exists()
            }
            
            effects.append(effect_data)
            print(f"  ➕ Added effect: {effect_file.stem}")
    
    print(f"🎬 Returning {len(effects)} effects")
    return jsonify(effects)

@app.route('/api/generate_preview', methods=['POST'])
def generate_preview():
    """生成预览视频"""
    data = request.get_json()
    style = data.get('style')
    effect_id = data.get('effect_id')
    
    print(f"🎬 Generate preview request: style={style}, effect_id={effect_id}")
    
    if not style or not effect_id:
        return jsonify({"error": "Style and effect_id are required"}), 400
    
    try:
        # 确保预览目录存在
        preview_style_dir = Path("previews") / style
        preview_style_dir.mkdir(parents=True, exist_ok=True)
        
        # 确保固定demos目录存在
        demos_dir = Path("demos")
        demos_dir.mkdir(parents=True, exist_ok=True)
        
        effect_file = Path("effects") / style / f"{effect_id}.xml"
        preview_file = preview_style_dir / f"{effect_id}_preview.mp4"
        demo_file = demos_dir / f"{style}_{effect_id}_demo.mp4"
        
        if not effect_file.exists():
            return jsonify({"error": f"Effect file not found: {effect_file}"}), 404
        
        # 这里应该调用预览生成器，现在先创建一个占位文件
        print(f"📹 Creating preview: {preview_file}")
        print(f"📹 Creating demo: {demo_file}")
        
        # 创建预览文件和demo文件
        create_placeholder_video(preview_file, style, effect_id)
        create_placeholder_video(demo_file, style, effect_id, is_demo=True)
        
        return jsonify({
            "success": True,
            "preview_file": f"previews/{style}/{effect_id}_preview.mp4",
            "demo_file": f"demos/{style}_{effect_id}_demo.mp4"
        })
    
    except Exception as e:
        print(f"❌ Preview generation failed: {e}")
        return jsonify({"error": str(e)}), 500

def create_placeholder_video(output_file, style, effect_id, is_demo=False):
    """创建占位预览视频（实际项目中会用MLT渲染真实预览）"""
    try:
        import subprocess
        
        # 为demo视频添加不同的颜色和标识
        if is_demo:
            color = 'red'
            text_content = f"DEMO: {style}_{effect_id}"
        else:
            color = 'blue'
            text_content = f"PREVIEW: {effect_id}"
        
        # 使用ffmpeg创建一个简单的测试视频，带有文字标识
        cmd = [
            '/Applications/kdenlive.app/Contents/MacOS/ffmpeg', '-f', 'lavfi', '-i', 
            f'color=c={color}:size=720x1280:duration=5',
            '-vf', f'drawtext=text="{text_content}":fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2',
            '-f', 'lavfi', '-i', 
            f'sine=frequency=1000:duration=5',
            '-c:v', 'libx264', '-c:a', 'aac',
            '-y', str(output_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            video_type = "demo" if is_demo else "preview"
            print(f"✅ {video_type.capitalize()} video created: {output_file}")
        else:
            print(f"⚠️  FFmpeg not available, creating empty file")
            # 如果ffmpeg不可用，创建一个空文件作为占位
            output_file.touch()
            
    except Exception as e:
        print(f"⚠️  Could not create video: {e}")
        # 创建空文件作为占位
        output_file.touch()

@app.route('/previews/<path:filename>')
def serve_preview(filename):
    """提供预览视频文件"""
    try:
        return send_from_directory('previews', filename)
    except Exception as e:
        return f"Error: {e}", 404

@app.route('/api/generate_batch_preview', methods=['POST'])
def generate_batch_preview():
    """批量生成预览视频"""
    data = request.get_json()
    style = data.get('style')
    
    print(f"🎬 Batch preview request for style: {style}")
    
    if not style:
        return jsonify({"error": "Style is required"}), 400
    
    try:
        effects_dir = Path("effects") / style
        if not effects_dir.exists():
            return jsonify({"error": f"Style directory not found: {style}"}), 404
        
        # 确保预览目录存在（原有的previews目录）
        preview_style_dir = Path("previews") / style
        preview_style_dir.mkdir(parents=True, exist_ok=True)
        
        # 确保固定demos目录存在
        demos_dir = Path("demos")
        demos_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取所有特效文件
        effect_files = list(effects_dir.glob("*.xml"))
        generated_count = 0
        
        for effect_file in effect_files:
            effect_id = effect_file.stem
            # 同时生成到两个位置：原有的previews目录和固定的demos目录
            preview_file = preview_style_dir / f"{effect_id}_preview.mp4"
            demo_file = demos_dir / f"{style}_{effect_id}_demo.mp4"
            
            # 如果预览文件不存在，则生成到两个位置
            if not preview_file.exists():
                create_placeholder_video(preview_file, style, effect_id)
                # 也保存一份到固定的demos目录
                create_placeholder_video(demo_file, style, effect_id, is_demo=True)
                generated_count += 1
                print(f"📹 Generated preview for: {effect_id} (saved to both previews and demos)")
        
        return jsonify({
            "success": True,
            "generated_count": generated_count,
            "total_effects": len(effect_files),
            "demos_saved_to": str(demos_dir.absolute())
        })
    
    except Exception as e:
        print(f"❌ Batch preview generation failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/effect/<path:filename>')
def serve_effect(filename):
    """提供特效XML文件"""
    try:
        return send_from_directory('effects', filename, as_attachment=True)
    except Exception as e:
        return f"Error: {e}", 404

@app.route('/api/demos')
def get_demos():
    """获取所有demo视频列表"""
    demos_dir = Path("demos")
    demos = []
    
    if demos_dir.exists():
        for demo_file in demos_dir.glob("*.mp4"):
            # 解析文件名格式: {style}_{effect_id}_demo.mp4
            name_parts = demo_file.stem.replace("_demo", "").split("_", 1)
            if len(name_parts) >= 2:
                style = name_parts[0]
                effect_id = name_parts[1]
            else:
                style = "unknown"
                effect_id = demo_file.stem
            
            demos.append({
                "filename": demo_file.name,
                "style": style,
                "effect_id": effect_id,
                "path": f"demos/{demo_file.name}",
                "size": demo_file.stat().st_size if demo_file.exists() else 0,
                "created": demo_file.stat().st_mtime if demo_file.exists() else 0
            })
    
    # 按创建时间排序
    demos.sort(key=lambda x: x["created"], reverse=True)
    return jsonify(demos)

@app.route('/demos/<path:filename>')
def serve_demo(filename):
    """提供demo视频文件"""
    try:
        return send_from_directory('demos', filename)
    except Exception as e:
        return f"Error: {e}", 404

@app.route('/api/effect/<style>/<effect_id>')
def get_effect_details(style, effect_id):
    """获取特效详细信息"""
    print(f"🔍 API called: /api/effect/{style}/{effect_id}")
    
    effect_file = Path("effects") / style / f"{effect_id}.xml"
    
    if not effect_file.exists():
        print(f"❌ Effect file not found: {effect_file}")
        return jsonify({"error": "Effect not found"}), 404
    
    try:
        # 读取XML内容
        with open(effect_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        effect_info = {
            "id": effect_id,
            "name": effect_id,
            "description": f"{style.title()} effect",
            "author": "AI Generator",
            "xml_content": xml_content
        }
        
        print(f"✅ Effect details loaded: {effect_id}")
        return jsonify(effect_info)
        
    except Exception as e:
        print(f"❌ Error loading effect details: {e}")
        return jsonify({"error": str(e)}), 500

# 添加CORS支持
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    print("🌐 Starting Simple Web Server...")
    print("📁 Project directory:", os.getcwd())
    print("📂 Templates directory:", Path('web/templates').absolute())
    print("📂 Static directory:", Path('web/static').absolute())
    print("📂 Effects directory:", Path('effects').absolute())
    
    # 检查必要文件
    required_paths = [
        Path('web/templates/index.html'),
        Path('web/static/style.css'),
        Path('web/static/app.js'),
        Path('effects')
    ]
    
    for path in required_paths:
        if path.exists():
            print(f"✅ {path}")
        else:
            print(f"❌ {path} - NOT FOUND")
    
    print("\n🚀 Server starting at http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
