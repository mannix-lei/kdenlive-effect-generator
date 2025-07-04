#!/usr/bin/env python3
"""
简化的Web服务器启动脚本 - 用于调试403错误
"""

import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import tempfile
import shutil

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

@app.route('/api/generate', methods=['POST'])
def generate_effects():
    """生成特效"""
    data = request.get_json()
    style = data.get('style')
    count = data.get('count', 5)
    
    print(f"🎨 Generate effects request: style={style}, count={count}")
    
    if not style:
        return jsonify({"error": "Style is required"}), 400
    
    # 验证风格是否有效
    valid_styles = ["shake", "zoom", "blur", "transition", "glitch", "color"]
    if style not in valid_styles:
        return jsonify({"error": f"Invalid style. Must be one of: {valid_styles}"}), 400
    
    try:
        # 导入特效生成器
        from src.effect_generator import EffectGenerator
        
        # 创建生成器实例
        generator = EffectGenerator(str(Path(__file__).parent))
        
        # 生成特效
        generated_files = generator.generate_effects(style, count)
        
        print(f"✅ Generated {len(generated_files)} effects for style: {style}")
        
        return jsonify({
            "success": True,
            "generated_count": len(generated_files),
            "style": style,
            "files": [str(f) for f in generated_files]
        })
    
    except Exception as e:
        print(f"❌ Effect generation failed: {e}")
        return jsonify({"error": str(e)}), 500

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
        
        effect_file = Path("effects") / style / f"{effect_id}.xml"
        preview_file = preview_style_dir / f"{effect_id}_preview.mp4"
        
        if not effect_file.exists():
            return jsonify({"error": f"Effect file not found: {effect_file}"}), 404
        
        # 生成预览视频
        print(f"📹 Creating preview: {preview_file}")
        create_placeholder_video(preview_file, style, effect_id)
        
        return jsonify({
            "success": True,
            "preview_file": f"previews/{style}/{effect_id}_preview.mp4"
        })
    
    except Exception as e:
        print(f"❌ Preview generation failed: {e}")
        return jsonify({"error": str(e)}), 500

def create_placeholder_video(output_file, style, effect_id):
    """创建预览视频，动态替换特效到kdenlive模板中"""
    try:
        import subprocess
        
        # 读取特效XML文件
        effect_file = Path("effects") / style / f"{effect_id}.xml"
        if not effect_file.exists():
            print(f"❌ Effect file not found: {effect_file}")
            output_file.touch()
            return
        
        # 读取特效XML内容
        with open(effect_file, 'r', encoding='utf-8') as f:
            effect_xml_content = f.read()
        
        # 解析特效XML
        try:
            effect_root = ET.fromstring(effect_xml_content)
        except ET.ParseError as e:
            print(f"❌ Invalid effect XML: {e}")
            output_file.touch()
            return
        
        # 读取kdenlive模板文件
        template_file = Path("assets/effect-demo-simple.kdenlive")
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 解析模板XML
        try:
            template_root = ET.fromstring(template_content)
        except ET.ParseError as e:
            print(f"❌ Invalid template XML: {e}")
            output_file.touch()
            return
        
        # 替换模板中的特效
        modified_template = replace_effect_in_template(template_root, effect_root, style, effect_id)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.kdenlive', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(ET.tostring(modified_template, encoding='unicode'))
            temp_kdenlive_path = temp_file.name
        
        try:
            # 使用melt命令渲染视频
            cmd = ['/Applications/kdenlive.app/Contents/MacOS/melt', temp_kdenlive_path, '-consumer', f'avformat:{output_file}', 'ab=160k', 'acodec=aac', 'channels=2', 'crf=23', 'f=mp4', 'g=15', 'movflags=+faststart', 'preset=veryfast', 'real_time=-1', 'threads=0', 'vcodec=libx264']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Preview video created with {style} effect: {output_file}")
            else:
                print(f"❌ Melt rendering failed: {result.stderr}")
                print(f"❌ Melt stdout: {result.stdout}")
                # 如果melt失败，创建一个空文件作为占位
                output_file.touch()
                
        finally:
            # 清理临时文件
            try:
                Path(temp_kdenlive_path).unlink()
            except:
                pass
            
    except Exception as e:
        print(f"⚠️  Could not create video: {e}")
        # 创建空文件作为占位
        output_file.touch()

def replace_effect_in_template(template_root, effect_root, style, effect_id):
    """将特效插入到kdenlive模板中"""
    # 找到playlist_main中的第一个entry（包含特效的entry）
    playlist_main = None
    for playlist in template_root.iter('playlist'):
        if playlist.get('id') == 'playlist_main':
            playlist_main = playlist
            break
    
    if playlist_main is not None:
        # 找到第一个entry
        first_entry = playlist_main.find('entry')
        if first_entry is not None:
            # 删除现有的所有filter（除了基础的缩放filter）
            filters_to_remove = []
            for filter_elem in first_entry.iter('filter'):
                if filter_elem.get('id') != 'filter_scale':  # 保留基础缩放filter
                    filters_to_remove.append(filter_elem)
            
            for filter_elem in filters_to_remove:
                first_entry.remove(filter_elem)
            
            # 根据特效类型转换并添加新特效
            if effect_root.tag == 'effect':
                # 单个特效
                new_filter = convert_effect_to_filter(effect_root, style, effect_id)
                if new_filter is not None:
                    first_entry.append(new_filter)
                    print(f"✅ Added single effect: {effect_root.get('id', 'unknown')}")
            elif effect_root.tag == 'effectgroup':
                # 特效组
                for effect in effect_root.iter('effect'):
                    new_filter = convert_effect_to_filter(effect, style, effect_id)
                    if new_filter is not None:
                        first_entry.append(new_filter)
                        print(f"✅ Added effect from group: {effect.get('id', 'unknown')}")
        else:
            print("❌ No entry found in playlist_main")
    else:
        print("❌ playlist_main not found")
    
    return template_root

def convert_effect_to_filter(effect_root, style, effect_id):
    """将特效XML转换为kdenlive filter格式"""
    # 创建新的filter元素
    new_filter = ET.Element('filter')
    new_filter.set('id', f'filter_generated_{effect_id}')
    
    # 根据特效类型设置不同的属性
    if effect_root.tag == 'effect':
        # 单个特效
        effect_id_attr = effect_root.get('id', 'unknown')
        mlt_service = effect_root.get('tag', effect_id_attr)
        
        # 设置mlt_service
        service_prop = ET.SubElement(new_filter, 'property')
        service_prop.set('name', 'mlt_service')
        service_prop.text = mlt_service
        
        # 设置kdenlive_id
        kdenlive_id_prop = ET.SubElement(new_filter, 'property')
        kdenlive_id_prop.set('name', 'kdenlive_id')
        kdenlive_id_prop.text = effect_id_attr
        
        # 复制特效的参数 (parameter元素)
        for param in effect_root.iter('parameter'):
            param_name = param.get('name')
            param_value = param.get('value', param.get('default', ''))
            
            if param_name and param_value:
                prop = ET.SubElement(new_filter, 'property')
                prop.set('name', param_name)
                prop.text = param_value
        
        # 复制特效的属性 (property元素)
        for prop in effect_root.iter('property'):
            prop_name = prop.get('name')
            if prop_name and prop.text:
                new_prop = ET.SubElement(new_filter, 'property')
                new_prop.set('name', prop_name)
                new_prop.text = prop.text
    
    elif effect_root.tag == 'effectgroup':
        # 特效组 - 使用第一个特效
        first_effect = effect_root.find('effect')
        if first_effect is not None:
            effect_id_attr = first_effect.get('id', 'unknown')
            
            # 设置mlt_service
            service_prop = ET.SubElement(new_filter, 'property')
            service_prop.set('name', 'mlt_service')
            service_prop.text = effect_id_attr
            
            # 设置kdenlive_id
            kdenlive_id_prop = ET.SubElement(new_filter, 'property')
            kdenlive_id_prop.set('name', 'kdenlive_id')
            kdenlive_id_prop.text = effect_id_attr
            
            # 复制特效的属性
            for prop in first_effect.iter('property'):
                prop_name = prop.get('name')
                if prop_name and prop.text:
                    new_prop = ET.SubElement(new_filter, 'property')
                    new_prop.set('name', prop_name)
                    new_prop.text = prop.text
    
    # 添加一些默认属性
    collapsed_prop = ET.SubElement(new_filter, 'property')
    collapsed_prop.set('name', 'kdenlive:collapsed')
    collapsed_prop.text = '0'
    
    return new_filter

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
        
        # 确保预览目录存在
        preview_style_dir = Path("previews") / style
        preview_style_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取所有特效文件
        effect_files = list(effects_dir.glob("*.xml"))
        generated_count = 0
        
        for effect_file in effect_files:
            effect_id = effect_file.stem
            preview_file = preview_style_dir / f"{effect_id}_preview.mp4"
            
            # 如果预览文件不存在，则生成
            if not preview_file.exists():
                create_placeholder_video(preview_file, style, effect_id)
                generated_count += 1
                print(f"📹 Generated preview for: {effect_id}")
        
        return jsonify({
            "success": True,
            "generated_count": generated_count,
            "total_effects": len(effect_files)
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

@app.route('/api/regenerate_preview', methods=['POST'])
def regenerate_preview():
    """重新生成预览视频"""
    data = request.get_json()
    style = data.get('style')
    effect_id = data.get('effect_id')
    
    print(f"🔄 Regenerate preview request: style={style}, effect_id={effect_id}")
    
    if not style or not effect_id:
        return jsonify({"error": "Style and effect_id are required"}), 400
    
    try:
        # 确保预览目录存在
        preview_style_dir = Path("previews") / style
        preview_style_dir.mkdir(parents=True, exist_ok=True)
        
        effect_file = Path("effects") / style / f"{effect_id}.xml"
        preview_file = preview_style_dir / f"{effect_id}_preview.mp4"
        
        if not effect_file.exists():
            return jsonify({"error": f"Effect file not found: {effect_file}"}), 404
        
        # 删除现有的预览视频（如果存在）
        if preview_file.exists():
            try:
                preview_file.unlink()
                print(f"🗑️  Deleted existing preview: {preview_file}")
            except Exception as e:
                print(f"⚠️  Could not delete existing preview: {e}")
        
        # 重新生成预览视频
        print(f"📹 Regenerating preview: {preview_file}")
        create_placeholder_video(preview_file, style, effect_id)
        
        return jsonify({
            "success": True,
            "preview_file": f"previews/{style}/{effect_id}_preview.mp4",
            "message": "Preview regenerated successfully"
        })
    
    except Exception as e:
        print(f"❌ Preview regeneration failed: {e}")
        return jsonify({"error": str(e)}), 500

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
