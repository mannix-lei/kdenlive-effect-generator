#!/usr/bin/env python3
"""
Create test assets for preview generation
"""

import os
import sys
from pathlib import Path

# 添加PIL支持
try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def create_test_image(output_path: Path, width: int = 1080, height: int = 1920):
    """创建测试图片"""
    if PIL_AVAILABLE:
        # 创建一个渐变背景图片
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # 绘制渐变背景
        for y in range(height):
            color = int(255 * (y / height))
            draw.line([(0, y), (width, y)], fill=(color, 100, 255-color))
        
        # 绘制一些几何图形
        draw.rectangle([100, 200, 620, 800], fill='white', outline='black', width=5)
        draw.ellipse([200, 400, 520, 700], fill='red', outline='yellow', width=3)
        
        # 添加文字
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
            draw.text((width//2-50, height//2), "TEST IMAGE", fill='blue', font=font)
        except:
            draw.text((width//2-50, height//2), "TEST IMAGE", fill='blue')
        
        img.save(output_path)
        print(f"Created test image: {output_path}")
        return True
    else:
        print("PIL not available, cannot create test image")
        return False

def create_test_video_with_python(output_path: Path, width: int = 1080, height: int = 1920, duration: int = 5, fps: int = 25):
    """使用Python创建简单的测试视频"""
    try:
        import cv2
        import numpy as np
        
        # 创建视频编写器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        total_frames = duration * fps
        
        for frame_num in range(total_frames):
            # 创建一个彩色帧
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 创建动态颜色
            color = int(255 * (frame_num / total_frames))
            frame[:, :] = [color, 128, 255 - color]
            
            # 添加一些图形
            cv2.rectangle(frame, (100, 200), (620, 800), (255, 255, 255), 5)
            cv2.circle(frame, (360, 550), 100, (0, 255, 0), -1)
            
            # 添加文字
            cv2.putText(frame, f'Frame {frame_num}', (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            out.write(frame)
        
        out.release()
        print(f"Created test video: {output_path}")
        return True
        
    except ImportError:
        print("OpenCV not available, cannot create test video")
        return False

def create_simple_test_files(assets_dir: Path):
    """创建简单的测试文件"""
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建测试图片
    test_image = assets_dir / "test_image.jpg"
    if not test_image.exists():
        if create_test_image(test_image):
            print("✓ Test image created successfully")
        else:
            # 创建一个简单的文本文件作为占位符
            with open(test_image, 'w') as f:
                f.write("Test image placeholder")
            print("Created placeholder for test image")
    
    # 创建测试视频
    test_video = assets_dir / "test_video.mp4"
    if not test_video.exists():
        if create_test_video_with_python(test_video):
            print("✓ Test video created successfully")
        else:
            # 创建一个简单的文本文件作为占位符
            with open(test_video, 'w') as f:
                f.write("Test video placeholder")
            print("Created placeholder for test video")

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    assets_dir = project_root / "assets"
    
    print("Creating test assets...")
    create_simple_test_files(assets_dir)
    print("Done!")
