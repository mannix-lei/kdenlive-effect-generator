#!/usr/bin/env python3
"""
测试特效替换功能
"""

import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import tempfile

# 添加src目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_effect_replacement():
    """测试特效替换功能"""
    
    # 从simple_server.py导入函数
    from simple_server import replace_effect_in_template, convert_effect_to_filter
    
    print("🧪 Testing effect replacement functionality...")
    
    # 测试shake特效
    effect_file = Path("effects/shake/shake_1221.xml")
    if not effect_file.exists():
        print(f"❌ Effect file not found: {effect_file}")
        return
    
    # 读取特效XML
    with open(effect_file, 'r', encoding='utf-8') as f:
        effect_xml = f.read()
    
    print(f"📄 Original effect XML:")
    print(effect_xml)
    print()
    
    # 解析特效XML
    try:
        effect_root = ET.fromstring(effect_xml)
        print(f"✅ Effect XML parsed successfully")
        print(f"📊 Effect tag: {effect_root.tag}")
        print(f"📊 Effect id: {effect_root.get('id')}")
        print(f"📊 Effect tag attr: {effect_root.get('tag')}")
        print()
    except ET.ParseError as e:
        print(f"❌ Error parsing effect XML: {e}")
        return
    
    # 测试转换为filter
    new_filter = convert_effect_to_filter(effect_root, "shake", "shake_1221")
    if new_filter is not None:
        print(f"✅ Effect converted to filter successfully")
        filter_xml = ET.tostring(new_filter, encoding='unicode')
        print(f"📄 Generated filter XML:")
        print(filter_xml)
        print()
    else:
        print(f"❌ Failed to convert effect to filter")
    
    # 读取模板文件
    template_file = Path("assets/effect-demo.kdenlive")
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 解析模板XML
    try:
        template_root = ET.fromstring(template_content)
        print(f"✅ Template XML parsed successfully")
    except ET.ParseError as e:
        print(f"❌ Error parsing template XML: {e}")
        return
    
    # 替换模板中的特效
    modified_template = replace_effect_in_template(template_root, effect_root, "shake", "shake_1221")
    
    # 创建临时文件并保存修改后的模板
    with tempfile.NamedTemporaryFile(mode='w', suffix='.kdenlive', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(ET.tostring(modified_template, encoding='unicode'))
        temp_path = temp_file.name
    
    print(f"✅ Modified template saved to: {temp_path}")
    print(f"📄 You can inspect the modified template at: {temp_path}")

if __name__ == "__main__":
    test_effect_replacement()
