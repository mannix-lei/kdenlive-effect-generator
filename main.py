#!/usr/bin/env python3
"""
Main Script - 项目主入口
"""

import os
import sys
import argparse
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def main():
    parser = argparse.ArgumentParser(description="Kdenlive Effect Generator")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # 生成特效命令
    generate_parser = subparsers.add_parser('generate', help='Generate effects')
    generate_parser.add_argument('--style', required=True, 
                               choices=['shake', 'zoom', 'blur', 'transition', 'glitch', 'color'],
                               help='Effect style')
    generate_parser.add_argument('--count', type=int, default=10, help='Number of effects')
    
    # 生成预览命令
    preview_parser = subparsers.add_parser('preview', help='Generate previews')
    preview_parser.add_argument('--style', help='Style to generate previews for')
    preview_parser.add_argument('--effect-file', help='Specific effect file')
    preview_parser.add_argument('--create-samples', action='store_true', help='Create sample assets')
    
    # Web服务器命令
    web_parser = subparsers.add_parser('web', help='Start web server')
    web_parser.add_argument('--host', default='localhost', help='Host to bind to')
    web_parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # 批量处理命令
    batch_parser = subparsers.add_parser('batch', help='Batch operations')
    batch_parser.add_argument('--generate-all', action='store_true', help='Generate all styles')
    batch_parser.add_argument('--preview-all', action='store_true', help='Generate all previews')
    batch_parser.add_argument('--count', type=int, default=5, help='Effects per style')
    
    # 预览管理命令
    manage_parser = subparsers.add_parser('manage', help='Manage preview files')
    manage_parser.add_argument('--organize', action='store_true', help='Organize previews to demos folder')
    manage_parser.add_argument('--index', action='store_true', help='Create demo index')
    manage_parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Cleanup old previews')
    manage_parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'generate':
            from effect_generator import EffectGenerator
            generator = EffectGenerator(str(project_root))
            files = generator.generate_effects(args.style, args.count)
            print(f"Generated {len(files)} effects for {args.style}")
        
        elif args.command == 'preview':
            from preview_generator import PreviewGenerator
            generator = PreviewGenerator(str(project_root))
            
            if args.create_samples:
                generator.create_sample_assets()
            elif args.effect_file:
                effect_file = Path(args.effect_file)
                output_file = project_root / "previews" / f"{effect_file.stem}_preview.mp4"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                if generator.render_preview(effect_file, output_file):
                    print(f"Preview generated: {output_file}")
            elif args.style:
                count = generator.generate_previews_for_style(args.style)
                print(f"Generated {count} previews for {args.style}")
            else:
                results = generator.generate_all_previews()
                total = sum(results.values())
                print(f"Generated {total} previews total")
        
        elif args.command == 'web':
            from web_server import EffectPreviewServer
            server = EffectPreviewServer(str(project_root))
            server.run(host=args.host, port=args.port, debug=args.debug)
        
        elif args.command == 'batch':
            if args.generate_all:
                from effect_generator import EffectGenerator
                generator = EffectGenerator(str(project_root))
                styles = ['shake', 'zoom', 'blur', 'transition', 'glitch', 'color']
                
                for style in styles:
                    files = generator.generate_effects(style, args.count)
                    print(f"Generated {len(files)} {style} effects")
                
                print(f"Batch generation complete: {len(styles) * args.count} total effects")
            
            if args.preview_all:
                from preview_generator import PreviewGenerator
                generator = PreviewGenerator(str(project_root))
                results = generator.generate_all_previews()
                total = sum(results.values())
                print(f"Batch preview generation complete: {total} total previews")
        
        elif args.command == 'manage':
            from preview_manager import PreviewManager
            manager = PreviewManager(str(project_root))
            
            if args.organize:
                manager.organize_previews()
            
            if args.index:
                index = manager.create_demo_index()
                print(f"Created demo index with {index['total_demos']} videos")
            
            if args.cleanup:
                manager.cleanup_old_previews(args.cleanup)
            
            if args.stats:
                stats = manager.get_stats()
                print(f"Total storage: {stats['total_size_mb']:.2f} MB")
            
            if not any([args.organize, args.index, args.cleanup, args.stats]):
                # 默认执行整理和索引
                manager.organize_previews()
                manager.create_demo_index()
    
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
