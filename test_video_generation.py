#!/usr/bin/env python3
"""
测试生成预览视频功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_video_generation():
    """测试视频生成功能"""
    
    # 从simple_server.py导入函数
    from simple_server import create_placeholder_video
    
    print("🎬 Testing video generation functionality...")
    
    # 创建测试输出目录
    test_output_dir = Path("test_output")
    test_output_dir.mkdir(exist_ok=True)
    
    # 测试生成shake特效预览
    output_file = test_output_dir / "shake_1221_test.mp4"
    
    print(f"📹 Generating video for shake_1221...")
    create_placeholder_video(output_file, "shake", "shake_1221", is_demo=False)
    
    if output_file.exists():
        file_size = output_file.stat().st_size
        print(f"✅ Video generated successfully!")
        print(f"📁 Output file: {output_file}")
        print(f"📊 File size: {file_size} bytes")
        
        if file_size > 1000:  # 如果文件大于1KB，说明可能是真正的视频
            print(f"🎉 Video appears to be properly generated (size > 1KB)")
        else:
            print(f"⚠️  Video file is small, might be a placeholder")
    else:
        print(f"❌ Video generation failed - file not created")

if __name__ == "__main__":
    test_video_generation()
