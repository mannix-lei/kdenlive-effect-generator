#!/usr/bin/env python3
"""
Web Server for Effect Preview
Web界面预览生成的特效
"""

import os
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, send_file, request
from typing import Dict, List, Any


class EffectPreviewServer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.app = Flask(__name__, 
                        template_folder=str(self.project_root / "web" / "templates"),
                        static_folder=str(self.project_root / "web" / "static"))
        
        # 设置Flask配置
        self.app.config['SECRET_KEY'] = 'kdenlive-effect-generator-secret'
        self.app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用缓存
        
        self.setup_routes()
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.route('/')
        def index():
            """主页"""
            return render_template('index.html')
        
        @self.app.route('/api/styles')
        def get_styles():
            """获取所有风格"""
            effects_dir = self.project_root / "effects"
            styles = []
            
            if effects_dir.exists():
                for style_dir in effects_dir.iterdir():
                    if style_dir.is_dir():
                        effect_count = len(list(style_dir.glob("*.xml")))
                        preview_dir = self.project_root / "previews" / style_dir.name
                        preview_count = len(list(preview_dir.glob("*.mp4"))) if preview_dir.exists() else 0
                        
                        styles.append({
                            "name": style_dir.name,
                            "effect_count": effect_count,
                            "preview_count": preview_count
                        })
            
            return jsonify(styles)
        
        @self.app.route('/api/effects/<style>')
        def get_effects_by_style(style):
            """获取指定风格的特效列表"""
            effects_dir = self.project_root / "effects" / style
            previews_dir = self.project_root / "previews" / style
            
            effects = []
            
            if effects_dir.exists():
                for effect_file in effects_dir.glob("*.xml"):
                    preview_file = previews_dir / f"{effect_file.stem}_preview.mp4"
                    
                    # 读取特效信息
                    effect_info = self._parse_effect_info(effect_file)
                    
                    effects.append({
                        "id": effect_file.stem,
                        "name": effect_info.get("name", effect_file.stem),
                        "description": effect_info.get("description", ""),
                        "author": effect_info.get("author", ""),
                        "effect_file": f"effects/{style}/{effect_file.name}",
                        "preview_file": f"previews/{style}/{preview_file.name}" if preview_file.exists() else None,
                        "has_preview": preview_file.exists()
                    })
            
            return jsonify(effects)
        
        @self.app.route('/api/effect/<style>/<effect_id>')
        def get_effect_details(style, effect_id):
            """获取特效详细信息"""
            effect_file = self.project_root / "effects" / style / f"{effect_id}.xml"
            
            if not effect_file.exists():
                return jsonify({"error": "Effect not found"}), 404
            
            # 读取XML内容
            with open(effect_file, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            effect_info = self._parse_effect_info(effect_file)
            effect_info["xml_content"] = xml_content
            
            return jsonify(effect_info)
        
        @self.app.route('/preview/<path:filename>')
        def serve_preview(filename):
            """提供预览视频文件"""
            file_path = self.project_root / "previews" / filename
            if file_path.exists() and file_path.is_file():
                try:
                    return send_file(str(file_path), mimetype='video/mp4')
                except Exception as e:
                    return f"Error serving file: {e}", 500
            else:
                return "File not found", 404
        
        @self.app.route('/effect/<path:filename>')
        def serve_effect(filename):
            """提供特效XML文件"""
            file_path = self.project_root / "effects" / filename
            if file_path.exists() and file_path.is_file():
                try:
                    return send_file(str(file_path), as_attachment=True, 
                                   mimetype='application/xml')
                except Exception as e:
                    return f"Error serving file: {e}", 500
            else:
                return "File not found", 404
        
        @self.app.route('/api/generate', methods=['POST'])
        def generate_effects():
            """生成新特效"""
            data = request.json
            style = data.get('style')
            count = data.get('count', 5)
            
            if not style:
                return jsonify({"error": "Style is required"}), 400
            
            try:
                # 这里应该调用特效生成器
                from src.effect_generator import EffectGenerator
                generator = EffectGenerator(str(self.project_root))
                generated_files = generator.generate_effects(style, count)
                
                return jsonify({
                    "success": True,
                    "generated_count": len(generated_files),
                    "files": [str(Path(f).relative_to(self.project_root)) for f in generated_files]
                })
            
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/generate_preview', methods=['POST'])
        def generate_preview():
            """生成预览视频"""
            data = request.json
            style = data.get('style')
            effect_id = data.get('effect_id')
            
            if not style or not effect_id:
                return jsonify({"error": "Style and effect_id are required"}), 400
            
            try:
                from src.preview_generator import PreviewGenerator
                generator = PreviewGenerator(str(self.project_root))
                
                effect_file = self.project_root / "effects" / style / f"{effect_id}.xml"
                output_file = self.project_root / "previews" / style / f"{effect_id}_preview.mp4"
                
                # 确保目录存在
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 渲染预览视频，同时保存到demos目录
                success = generator.render_preview(effect_file, output_file, save_demo=True)
                
                return jsonify({
                    "success": success,
                    "preview_file": f"previews/{style}/{effect_id}_preview.mp4" if success else None,
                    "demo_file": f"demos/{style}_{effect_id}_demo.mp4" if success else None
                })
            
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/generate_batch_preview', methods=['POST'])
        def generate_batch_preview():
            """批量生成预览视频"""
            data = request.json
            style = data.get('style')
            
            if not style:
                return jsonify({"error": "Style is required"}), 400
            
            try:
                from src.preview_generator import PreviewGenerator
                generator = PreviewGenerator(str(self.project_root))
                
                # 生成该风格的所有预览
                generated_count = generator.generate_previews_for_style(style)
                
                # 统计总特效数
                effects_dir = self.project_root / "effects" / style
                total_effects = len(list(effects_dir.glob("*.xml"))) if effects_dir.exists() else 0
                
                return jsonify({
                    "success": True,
                    "generated_count": generated_count,
                    "total_effects": total_effects,
                    "demos_saved_to": str(self.project_root / "demos")
                })
            
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/demos')
        def get_demos():
            """获取所有demo视频列表"""
            demos_dir = self.project_root / "demos"
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

        @self.app.route('/demos/<path:filename>')
        def serve_demo(filename):
            """提供demo视频文件"""
            demos_dir = self.project_root / "demos"
            return send_file(demos_dir / filename)

        # ...existing code...
    
    def _parse_effect_info(self, effect_file: Path) -> Dict[str, Any]:
        """解析特效XML文件获取基本信息"""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(effect_file)
            root = tree.getroot()
            
            info = {
                "id": root.get("id", ""),
                "name": "",
                "description": "",
                "author": ""
            }
            
            # 提取名称
            name_elem = root.find("n")
            if name_elem is not None:
                info["name"] = name_elem.text or ""
            
            # 提取描述
            desc_elem = root.find("description")
            if desc_elem is not None:
                info["description"] = desc_elem.text or ""
            
            # 提取作者
            author_elem = root.find("author")
            if author_elem is not None:
                info["author"] = author_elem.text or ""
            
            return info
        
        except Exception as e:
            return {
                "id": effect_file.stem,
                "name": effect_file.stem,
                "description": f"Error parsing XML: {e}",
                "author": "Unknown"
            }
    
    def run(self, host='localhost', port=5000, debug=True):
        """启动服务器"""
        print(f"Starting Effect Preview Server at http://{host}:{port}")
        print(f"Project root: {self.project_root}")
        
        # 确保目录存在
        (self.project_root / "previews").mkdir(exist_ok=True)
        (self.project_root / "effects").mkdir(exist_ok=True)
        
        # 添加CORS支持和错误处理
        @self.app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        @self.app.errorhandler(403)
        def forbidden(error):
            return jsonify({"error": "Forbidden", "message": str(error)}), 403
            
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Not Found", "message": str(error)}), 404
            
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({"error": "Internal Server Error", "message": str(error)}), 500
        
        self.app.run(host=host, port=port, debug=debug, threaded=True)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Effect Preview Web Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    server = EffectPreviewServer(args.project_root)
    server.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
