#!/usr/bin/env python3
"""
Preview Manager - 管理预览视频文件
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json


class PreviewManager:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.previews_dir = self.project_root / "previews"
        self.demos_dir = self.project_root / "demos"  # 固定的demo视频文件夹
        
        # 创建必要的目录
        self.previews_dir.mkdir(exist_ok=True)
        self.demos_dir.mkdir(exist_ok=True)
    
    def organize_previews(self):
        """整理预览文件到demos文件夹"""
        print("📁 开始整理预览文件...")
        
        # 按风格整理
        for style_dir in self.previews_dir.iterdir():
            if style_dir.is_dir():
                style_name = style_dir.name
                target_dir = self.demos_dir / style_name
                target_dir.mkdir(exist_ok=True)
                
                # 复制所有预览视频
                preview_files = list(style_dir.glob("*.mp4"))
                copied_count = 0
                
                for preview_file in preview_files:
                    target_file = target_dir / preview_file.name
                    
                    # 如果目标文件不存在或源文件更新，则复制
                    if not target_file.exists() or preview_file.stat().st_mtime > target_file.stat().st_mtime:
                        shutil.copy2(preview_file, target_file)
                        copied_count += 1
                
                print(f"  {style_name}: 复制了 {copied_count}/{len(preview_files)} 个预览文件")
        
        print("✅ 预览文件整理完成")
    
    def create_demo_index(self):
        """创建demo视频索引"""
        index = {
            "created_at": datetime.now().isoformat(),
            "total_demos": 0,
            "styles": {}
        }
        
        total_count = 0
        
        for style_dir in self.demos_dir.iterdir():
            if style_dir.is_dir():
                style_name = style_dir.name
                demo_files = list(style_dir.glob("*.mp4"))
                
                demos = []
                for demo_file in demo_files:
                    effect_id = demo_file.stem.replace("_preview", "")
                    stat = demo_file.stat()
                    
                    demos.append({
                        "effect_id": effect_id,
                        "filename": demo_file.name,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "path": str(demo_file.relative_to(self.demos_dir))
                    })
                
                index["styles"][style_name] = {
                    "count": len(demos),
                    "demos": sorted(demos, key=lambda x: x["created_at"], reverse=True)
                }
                
                total_count += len(demos)
        
        index["total_demos"] = total_count
        
        # 保存索引文件
        index_file = self.demos_dir / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        print(f"📋 创建了demo索引: {total_count} 个视频")
        return index
    
    def cleanup_old_previews(self, keep_days=7):
        """清理旧的预览文件"""
        print(f"🧹 清理 {keep_days} 天前的预览文件...")
        
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(days=keep_days)
        
        removed_count = 0
        
        for preview_file in self.previews_dir.rglob("*.mp4"):
            if preview_file.is_file():
                file_time = datetime.fromtimestamp(preview_file.stat().st_mtime)
                if file_time < cutoff_time:
                    preview_file.unlink()
                    removed_count += 1
                    print(f"  删除: {preview_file.relative_to(self.previews_dir)}")
        
        print(f"✅ 清理完成，删除了 {removed_count} 个旧文件")
    
    def get_stats(self):
        """获取统计信息"""
        stats = {
            "previews": {},
            "demos": {},
            "total_size_mb": 0
        }
        
        # 统计预览文件
        for style_dir in self.previews_dir.iterdir():
            if style_dir.is_dir():
                files = list(style_dir.glob("*.mp4"))
                size = sum(f.stat().st_size for f in files)
                stats["previews"][style_dir.name] = {
                    "count": len(files),
                    "size_mb": round(size / (1024 * 1024), 2)
                }
                stats["total_size_mb"] += size / (1024 * 1024)
        
        # 统计demo文件
        for style_dir in self.demos_dir.iterdir():
            if style_dir.is_dir():
                files = list(style_dir.glob("*.mp4"))
                size = sum(f.stat().st_size for f in files)
                stats["demos"][style_dir.name] = {
                    "count": len(files),
                    "size_mb": round(size / (1024 * 1024), 2)
                }
                stats["total_size_mb"] += size / (1024 * 1024)
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        return stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Preview Manager")
    parser.add_argument("--organize", action="store_true", help="整理预览文件到demos文件夹")
    parser.add_argument("--index", action="store_true", help="创建demo索引")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="清理N天前的预览文件")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    
    args = parser.parse_args()
    
    manager = PreviewManager(args.project_root)
    
    if args.organize:
        manager.organize_previews()
    
    if args.index:
        index = manager.create_demo_index()
        print(f"\n📊 Demo统计:")
        for style, data in index["styles"].items():
            print(f"  {style}: {data['count']} 个视频")
    
    if args.cleanup:
        manager.cleanup_old_previews(args.cleanup)
    
    if args.stats:
        stats = manager.get_stats()
        print(f"\n📊 存储统计:")
        print(f"总大小: {stats['total_size_mb']:.2f} MB")
        
        if stats["previews"]:
            print("\n预览文件:")
            for style, data in stats["previews"].items():
                print(f"  {style}: {data['count']} 个文件, {data['size_mb']:.2f} MB")
        
        if stats["demos"]:
            print("\nDemo文件:")
            for style, data in stats["demos"].items():
                print(f"  {style}: {data['count']} 个文件, {data['size_mb']:.2f} MB")
    
    if not any([args.organize, args.index, args.cleanup, args.stats]):
        # 默认执行所有操作
        manager.organize_previews()
        manager.create_demo_index()
        stats = manager.get_stats()
        print(f"\n📊 总共管理了 {stats['total_size_mb']:.2f} MB 的视频文件")


if __name__ == "__main__":
    main()
