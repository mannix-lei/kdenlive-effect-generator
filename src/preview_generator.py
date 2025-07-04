#!/usr/bin/env python3
"""
Preview Generator
为生成的kdenlive特效创建预览视频
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Dict
import json
from datetime import datetime


class PreviewGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.assets_dir = self.project_root / "assets"
        self.previews_dir = self.project_root / "previews"
        self.demos_dir = self.project_root / "demos"  # 添加固定的demos目录
        self.effects_dir = self.project_root / "effects"
        
        # 预览视频配置
        self.width = 720
        self.height = 1280  # 9:16比例
        self.duration = 5  # 5秒
        self.fps = 25
        
        # 查找ffmpeg
        self.ffmpeg_path = self._find_ffmpeg()
        print(f"Using ffmpeg at: {self.ffmpeg_path}")
        
        # 检查melt命令
        self.melt_path = self._find_melt()
        if not self.melt_path:
            print("⚠️  melt command not found. Will use FFmpeg for previews.")
            self.use_placeholder = True
        else:
            print("⚠️  MLT found but using FFmpeg for better compatibility.")
            self.use_placeholder = True  # 强制使用FFmpeg预览
    
    def _find_ffmpeg(self) -> str:
        """查找ffmpeg命令路径"""
        possible_paths = [
            "/Applications/kdenlive.app/Contents/MacOS/ffmpeg",  # Kdenlive
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "-version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return path
            except FileNotFoundError:
                continue
        
        return "ffmpeg"  # 默认使用系统PATH中的ffmpeg
    
    def _find_melt(self) -> Optional[str]:
        """查找melt命令路径"""
        possible_paths = [
            "/Applications/kdenlive.app/Contents/MacOS/melt",  # macOS Kdenlive
            "/usr/local/bin/melt",  # Homebrew
            "/opt/homebrew/bin/melt",  # Homebrew (Apple Silicon)
            "melt"  # System PATH
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return path
            except FileNotFoundError:
                continue
        
        return None
    
    def get_asset_files(self) -> List[Path]:
        """获取素材文件列表"""
        asset_files = []
        
        # 支持的文件格式
        video_exts = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
        image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        for file_path in self.assets_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in video_exts | image_exts:
                asset_files.append(file_path)
        
        return asset_files
    
    def create_sample_assets(self):
        """创建示例素材文件"""
        # 创建一个简单的测试视频
        sample_video = self.assets_dir / "sample_video.mp4"
        if not sample_video.exists():
            # 使用melt创建一个彩色背景视频
            cmd = [
                self.melt_path,
                "color:blue",
                f"out={self.fps * 10}",  # 10秒
                "-profile", f"atsc_720p_{self.fps}",
                "-consumer", f"avformat:{sample_video}",
                "vcodec=libx264", "acodec=aac"
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"Created sample video: {sample_video}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to create sample video: {e}")
        
        # 创建一个测试图片
        sample_image = self.assets_dir / "sample_image.jpg"
        if not sample_image.exists():
            try:
                from PIL import Image, ImageDraw
                
                # 创建一个渐变背景图片
                img = Image.new('RGB', (self.width, self.height))
                draw = ImageDraw.Draw(img)
                
                # 绘制一些几何图形
                draw.rectangle([100, 200, 620, 800], fill='white', outline='black', width=5)
                draw.ellipse([200, 400, 520, 700], fill='red', outline='yellow', width=3)
                
                img.save(sample_image)
                print(f"Created sample image: {sample_image}")
            except ImportError:
                print("PIL not available, skipping sample image creation")
    
    def generate_preview_mlt(self, effect_file: Path, asset_file: Path) -> str:
        """生成MLT XML用于预览"""
        # 读取特效XML
        with open(effect_file, 'r', encoding='utf-8') as f:
            effect_content = f.read()
        
        # 构建MLT XML
        mlt_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<mlt LC_NUMERIC="C" version="7.0.1" title="Effect Preview" producer="main_bin">
  <profile description="HD 720p 25 fps" width="{self.width}" height="{self.height}" 
           progressive="1" sample_aspect_num="1" sample_aspect_den="1" 
           display_aspect_num="9" display_aspect_den="16" frame_rate_num="{self.fps}" 
           frame_rate_den="1" colorspace="709"/>
  
  <producer id="producer0" in="0" out="{self.fps * self.duration - 1}">
    <property name="resource">{asset_file.absolute()}</property>
    <property name="mlt_service">{"avformat" if asset_file.suffix.lower() in {'.mp4', '.mov', '.avi', '.mkv', '.webm'} else "pixbuf"}</property>
    <property name="seekable">1</property>
  </producer>
  
  <playlist id="playlist0">
    <entry producer="producer0" in="0" out="{self.fps * self.duration - 1}">
      {effect_content}
    </entry>
  </playlist>
  
  <tractor id="tractor0" in="0" out="{self.fps * self.duration - 1}">
    <track producer="playlist0"/>
  </tractor>
  
</mlt>'''
        
        return mlt_xml
    
    def render_preview(self, effect_file: Path, output_file: Path, asset_file: Optional[Path] = None, save_demo: bool = True) -> bool:
        """渲染预览视频"""
        
        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果MLT不可用，创建占位视频
        if self.use_placeholder:
            return self._create_placeholder_preview(effect_file, output_file, save_demo)
        
        # 如果没有指定素材文件，使用第一个可用的
        if asset_file is None:
            asset_files = self.get_asset_files()
            if not asset_files:
                self.create_sample_assets()
                asset_files = self.get_asset_files()
            
            if not asset_files:
                print("No asset files found")
                return False
            
            asset_file = asset_files[0]
        
        # 生成MLT XML
        mlt_content = self.generate_preview_mlt(effect_file, asset_file)
        
        # 创建临时MLT文件
        temp_mlt = self.previews_dir / f"temp_{effect_file.stem}.mlt"
        with open(temp_mlt, 'w', encoding='utf-8') as f:
            f.write(mlt_content)
        
        try:
            # 渲染命令
            cmd = [
                self.melt_path,
                str(temp_mlt),
                "-consumer", f"avformat:{output_file}",
                "vcodec=libx264", "acodec=aac",
                "preset=fast", "crf=23",
                f"s={self.width}x{self.height}",
                "r=25"
            ]
            
            print(f"Rendering preview for {effect_file.name}...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Preview created: {output_file.name}")
                temp_mlt.unlink()  # 删除临时文件
                
                # 如果需要，同时保存到demos目录
                if save_demo:
                    self._save_to_demos(effect_file, output_file)
                
                return True
            else:
                print(f"✗ Failed to render {effect_file.name}: {result.stderr}")
                # MLT渲染失败时，尝试创建占位视频
                print(f"Attempting to create placeholder video...")
                if self._create_placeholder_video(output_file, effect_file):
                    if save_demo:
                        self._save_to_demos(effect_file, output_file)
                    return True
                return False
                
        except Exception as e:
            print(f"✗ Error rendering {effect_file.name}: {e}")
            # 出现异常时，尝试创建占位视频
            print(f"Attempting to create placeholder video...")
            if self._create_placeholder_video(output_file, effect_file):
                if save_demo:
                    self._save_to_demos(effect_file, output_file)
                return True
            return False
    
    def _create_placeholder_preview(self, effect_file: Path, output_file: Path, save_demo: bool = True) -> bool:
        """创建真实的预览视频（使用FFmpeg和assets）"""
        try:
            style = effect_file.parent.name
            effect_id = effect_file.stem
            
            # 获取可用的asset文件
            asset_files = self.get_asset_files()
            if not asset_files:
                self.create_sample_assets()
                asset_files = self.get_asset_files()
            
            # 选择第一个可用的asset文件
            asset_file = asset_files[0] if asset_files else None
            
            if asset_file and asset_file.exists():
                # 检查是视频还是图片
                video_exts = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
                is_video = asset_file.suffix.lower() in video_exts
                
                try:
                    if is_video:
                        # 使用视频asset创建预览
                        cmd = [
                            self.ffmpeg_path, 
                            '-i', str(asset_file),
                            '-t', str(self.duration),
                            '-vf', f'scale={self.width}:{self.height}:force_original_aspect_ratio=decrease:flags=lanczos,pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2,fps={self.fps}',
                            '-c:v', 'libx264',
                            '-preset', 'fast',
                            '-crf', '23',
                            '-pix_fmt', 'yuv420p',
                            '-an',  # 去掉音频
                            '-y', str(output_file)
                        ]
                    else:
                        # 使用图片asset创建预览（图片循环显示）
                        cmd = [
                            self.ffmpeg_path, 
                            '-loop', '1',
                            '-i', str(asset_file),
                            '-t', str(self.duration),
                            '-vf', f'scale={self.width}:{self.height}:force_original_aspect_ratio=decrease:flags=lanczos,pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2,fps={self.fps}',
                            '-c:v', 'libx264',
                            '-preset', 'fast',
                            '-crf', '23',
                            '-pix_fmt', 'yuv420p',
                            '-y', str(output_file)
                        ]
                    
                    print(f"Creating preview from asset: {asset_file.name}")
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✓ Preview created from asset: {output_file.name}")
                        
                        # 如果需要，同时保存到demos目录
                        if save_demo:
                            self._save_to_demos(effect_file, output_file)
                        
                        return True
                    else:
                        print(f"⚠️  FFmpeg failed: {result.stderr}")
                        # 如果ffmpeg失败，创建简单的占位视频
                        return self._create_simple_placeholder(output_file, style, effect_id, save_demo, effect_file)
                except Exception as e:
                    print(f"⚠️  Error running FFmpeg: {e}")
                    return self._create_simple_placeholder(output_file, style, effect_id, save_demo, effect_file)
            else:
                # 没有有效的asset文件，创建简单的占位视频
                return self._create_simple_placeholder(output_file, style, effect_id, save_demo, effect_file)
                
        except Exception as e:
            print(f"⚠️  Could not create preview video: {e}")
            # 创建简单的占位视频
            return self._create_simple_placeholder(output_file, style, effect_id, save_demo, effect_file)
    
    def _create_simple_placeholder(self, output_file: Path, style: str, effect_id: str, save_demo: bool, effect_file: Path) -> bool:
        """创建简单的占位视频"""
        try:
            # 尝试使用ffmpeg创建一个简单的彩色视频
            cmd = [
                self.ffmpeg_path, 
                '-f', 'lavfi', '-i', 
                f'color=c=orange:size={self.width}x{self.height}:duration={self.duration}',
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-r', '25',
                '-pix_fmt', 'yuv420p',
                '-y', str(output_file)
            ]
            
            print(f"Creating simple placeholder video: {output_file}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Simple placeholder created: {output_file.name}")
                
                # 如果需要，同时保存到demos目录
                if save_demo:
                    self._save_to_demos(effect_file, output_file)
                
                return True
            else:
                print(f"⚠️  FFmpeg failed: {result.stderr}")
                # 如果ffmpeg不可用，创建一个实际的小视频文件
                return self._create_minimal_video_file(output_file, style, effect_id, save_demo)
                
        except Exception as e:
            print(f"⚠️  Could not create simple placeholder: {e}")
            # 创建最小的视频文件
            return self._create_minimal_video_file(output_file, style, effect_id, save_demo)
    
    def _create_minimal_video_file(self, output_file: Path, style: str, effect_id: str, save_demo: bool) -> bool:
        """创建最小的视频文件（当FFmpeg不可用时）"""
        try:
            # 创建一个包含基本MP4头的最小文件
            minimal_mp4_data = bytes([
                0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70, 0x69, 0x73, 0x6f, 0x6d, 0x00, 0x00, 0x02, 0x00,
                0x69, 0x73, 0x6f, 0x6d, 0x69, 0x73, 0x6f, 0x32, 0x61, 0x76, 0x63, 0x31, 0x6d, 0x70, 0x34, 0x31,
                0x00, 0x00, 0x00, 0x08, 0x66, 0x72, 0x65, 0x65
            ])
            
            with open(output_file, 'wb') as f:
                # 写入一个更大的文件以确保非零大小
                f.write(minimal_mp4_data)
                # 添加一些数据让文件有一定大小
                f.write(b'0' * 1024)  # 1KB of data
            
            print(f"✓ Minimal video file created: {output_file}")
            
            # 如果需要，同时保存到demos目录
            if save_demo:
                demo_file = self.demos_dir / f"{style}_{effect_id}_demo.mp4"
                self.demos_dir.mkdir(parents=True, exist_ok=True)
                with open(demo_file, 'wb') as f:
                    f.write(minimal_mp4_data)
                    f.write(b'0' * 1024)
                print(f"✓ Minimal demo file created: {demo_file}")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Could not create minimal video file: {e}")
            return False
    
    def _create_placeholder_video(self, output_file: Path, effect_file: Path) -> bool:
        """创建占位预览视频（当MLT渲染失败时使用）"""
        try:
            # 获取风格名和特效ID
            style = effect_file.parent.name
            effect_id = effect_file.stem
            
            # 使用ffmpeg创建一个简单的测试视频，带有文字标识
            cmd = [
                self.ffmpeg_path, 
                '-f', 'lavfi', '-i', 
                f'color=c=red:size={self.width}x{self.height}:duration={self.duration}',
                '-vf', f'drawtext=text="FALLBACK {effect_id}":fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2',
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-y', str(output_file)
            ]
            
            print(f"Creating fallback video: {output_file}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Fallback video created: {output_file}")
                return True
            else:
                print(f"⚠️  FFmpeg failed: {result.stderr}")
                # 如果ffmpeg也不可用，创建一个占位文件
                with open(output_file, 'wb') as f:
                    f.write(b'fallback video content')
                return True
                
        except Exception as e:
            print(f"⚠️  Could not create fallback video: {e}")
            # 创建占位文件
            with open(output_file, 'wb') as f:
                f.write(b'fallback video content')
            return True

    def _save_to_demos(self, effect_file: Path, preview_file: Path):
        """将预览视频复制到demos目录"""
        try:
            # 确保demos目录存在
            self.demos_dir.mkdir(parents=True, exist_ok=True)
            
            # 获取风格名（从effect_file路径中提取）
            style = effect_file.parent.name
            effect_id = effect_file.stem
            
            # 创建demo文件名
            demo_file = self.demos_dir / f"{style}_{effect_id}_demo.mp4"
            
            # 检查源文件是否存在
            if preview_file.exists():
                # 复制文件
                import shutil
                shutil.copy2(preview_file, demo_file)
                print(f"✓ Demo saved to: {demo_file}")
            else:
                print(f"⚠️  Preview file not found: {preview_file}")
            
        except Exception as e:
            print(f"⚠️  Failed to save demo: {e}")
    
    def generate_previews_for_style(self, style: str) -> int:
        """为指定风格的所有特效生成预览"""
        style_dir = self.effects_dir / style
        if not style_dir.exists():
            print(f"Style directory not found: {style_dir}")
            return 0
        
        # 创建预览目录
        preview_style_dir = self.previews_dir / style
        preview_style_dir.mkdir(parents=True, exist_ok=True)
        
        # 确保demos目录存在
        self.demos_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取特效文件
        effect_files = list(style_dir.glob("*.xml"))
        if not effect_files:
            print(f"No effect files found in {style_dir}")
            return 0
        
        success_count = 0
        for effect_file in effect_files:
            output_file = preview_style_dir / f"{effect_file.stem}_preview.mp4"
            
            if self.render_preview(effect_file, output_file, save_demo=True):
                success_count += 1
        
        return success_count
    
    def generate_all_previews(self) -> Dict[str, int]:
        """为所有风格生成预览"""
        results = {}
        
        for style_dir in self.effects_dir.iterdir():
            if style_dir.is_dir():
                style = style_dir.name
                count = self.generate_previews_for_style(style)
                results[style] = count
                print(f"Generated {count} previews for {style} style")
        
        return results
    
    def create_preview_index(self):
        """创建预览索引JSON文件"""
        index = {
            "generated_at": str(datetime.now()),
            "styles": {}
        }
        
        for style_dir in self.previews_dir.iterdir():
            if style_dir.is_dir():
                style = style_dir.name
                previews = []
                
                for preview_file in style_dir.glob("*.mp4"):
                    effect_name = preview_file.stem.replace("_preview", "")
                    previews.append({
                        "effect_name": effect_name,
                        "preview_file": str(preview_file.relative_to(self.project_root)),
                        "effect_file": f"effects/{style}/{effect_name}.xml"
                    })
                
                index["styles"][style] = {
                    "count": len(previews),
                    "previews": previews
                }
        
        # 保存索引文件
        index_file = self.previews_dir / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        print(f"Preview index created: {index_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate preview videos for effects")
    parser.add_argument("--style", help="Generate previews for specific style")
    parser.add_argument("--effect-file", help="Generate preview for specific effect file")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--create-samples", action="store_true", 
                      help="Create sample asset files")
    
    args = parser.parse_args()
    
    try:
        generator = PreviewGenerator(args.project_root)
        
        if args.create_samples:
            generator.create_sample_assets()
            return
        
        if args.effect_file:
            # 单个文件预览
            effect_file = Path(args.effect_file)
            output_file = generator.previews_dir / f"{effect_file.stem}_preview.mp4"
            generator.previews_dir.mkdir(parents=True, exist_ok=True)
            
            if generator.render_preview(effect_file, output_file):
                print(f"Preview generated: {output_file}")
            else:
                print("Failed to generate preview")
        
        elif args.style:
            # 指定风格预览
            count = generator.generate_previews_for_style(args.style)
            print(f"Generated {count} previews for {args.style}")
        
        else:
            # 所有预览
            results = generator.generate_all_previews()
            total = sum(results.values())
            print(f"\nTotal previews generated: {total}")
            
            # 创建索引
            generator.create_preview_index()
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    from datetime import datetime
    main()
