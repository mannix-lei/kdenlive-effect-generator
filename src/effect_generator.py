#!/usr/bin/env python3
"""
Kdenlive Effect Generator
自动生成kdenlive特效XML文件的工具
"""

import os
import json
import random
import argparse
from typing import Dict, List, Any
from pathlib import Path
from jinja2 import Template
import xml.etree.ElementTree as ET


class EffectGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / "templates"
        self.effects_dir = self.project_root / "effects"
        
        # 特效风格配置
        self.styles = {
            "shake": {
                "description": "相机抖动、震动效果",
                "effects": ["qtblend", "rotation", "rect_animation"]
            },
            "zoom": {
                "description": "缩放、推拉镜头效果", 
                "effects": ["qtblend", "lenscorrection", "rect_scale"]
            },
            "blur": {
                "description": "各种模糊效果",
                "effects": ["dblur", "gblur", "lenscorrection"]
            },
            "transition": {
                "description": "转场过渡效果",
                "effects": ["qtblend", "opacity", "compositing"]
            },
            "glitch": {
                "description": "故障艺术、数字噪声",
                "effects": ["dblur", "exposure", "color_shift"]
            },
            "color": {
                "description": "色彩调节、滤镜",
                "effects": ["exposure", "color_correction", "saturation"]
            }
        }
    
    def generate_effect_params(self, style: str) -> Dict[str, Any]:
        """根据风格生成特效参数"""
        params = {
            "id": f"{style}_{random.randint(1000, 9999)}",
            "name": f"{style.title()} Effect",
            "description": self.styles[style]["description"],
            "author": "AI Effect Generator"
        }
        
        if style == "shake":
            params.update(self._generate_shake_params())
        elif style == "zoom":
            params.update(self._generate_zoom_params())
        elif style == "blur":
            params.update(self._generate_blur_params())
        elif style == "transition":
            params.update(self._generate_transition_params())
        elif style == "glitch":
            params.update(self._generate_glitch_params())
        elif style == "color":
            params.update(self._generate_color_params())
        
        return params
    
    def _generate_shake_params(self) -> Dict[str, Any]:
        """生成抖动特效参数"""
        intensity = random.uniform(0.5, 3.0)
        duration = random.randint(60, 300)  # 帧数
        
        # 生成抖动动画关键帧
        keyframes = []
        for i in range(0, duration, 15):  # 每15帧一个关键帧
            x_offset = random.randint(-int(50*intensity), int(50*intensity))
            y_offset = random.randint(-int(50*intensity), int(50*intensity))
            rotation = random.uniform(-intensity, intensity)
            keyframes.append({
                "frame": i,
                "x": x_offset,
                "y": y_offset,
                "rotation": rotation
            })
        
        return {
            "intensity": intensity,
            "duration": duration,
            "keyframes": keyframes,
            "rect_animation": self._build_rect_animation(keyframes),
            "rotation_animation": self._build_rotation_animation(keyframes)
        }
    
    def _generate_zoom_params(self) -> Dict[str, Any]:
        """生成缩放特效参数"""
        zoom_type = random.choice(["zoom_in", "zoom_out", "zoom_pulse"])
        start_scale = random.uniform(0.8, 1.5)
        end_scale = random.uniform(0.8, 1.5)
        duration = random.randint(60, 180)
        
        return {
            "zoom_type": zoom_type,
            "start_scale": start_scale,
            "end_scale": end_scale,
            "duration": duration,
            "lens_correction": random.uniform(0.1, 0.5),
            "brightness": random.uniform(0, 0.3),
            "rect_scale": self._build_zoom_animation(start_scale, end_scale, duration)
        }
    
    def _generate_blur_params(self) -> Dict[str, Any]:
        """生成模糊特效参数"""
        blur_type = random.choice(["motion", "gaussian", "radial"])
        intensity = random.uniform(0, 150)
        angle = random.uniform(0, 360)
        duration = random.randint(30, 120)
        
        return {
            "blur_type": blur_type,
            "intensity": intensity,
            "angle": angle,
            "duration": duration,
            "radius_animation": self._build_blur_animation(intensity, duration),
            "angle_animation": self._build_angle_animation(angle, duration)
        }
    
    def _generate_transition_params(self) -> Dict[str, Any]:
        """生成转场特效参数"""
        transition_type = random.choice(["fade", "slide", "scale", "rotate"])
        duration = random.randint(30, 90)
        
        return {
            "transition_type": transition_type,
            "duration": duration,
            "opacity_animation": self._build_opacity_animation(duration),
            "compositing_mode": random.choice([0, 11, 12, 13])  # 不同混合模式
        }
    
    def _generate_glitch_params(self) -> Dict[str, Any]:
        """生成故障特效参数"""
        glitch_intensity = random.uniform(0.5, 2.0)
        frequency = random.randint(5, 20)  # 故障频率
        duration = random.randint(60, 180)
        
        return {
            "glitch_intensity": glitch_intensity,
            "frequency": frequency,
            "duration": duration,
            "exposure_shift": random.uniform(-0.5, 0.5),
            "color_shift": random.uniform(0, 50),
            "blur_pulses": self._build_glitch_animation(glitch_intensity, frequency, duration)
        }
    
    def _generate_color_params(self) -> Dict[str, Any]:
        """生成色彩特效参数"""
        color_style = random.choice(["vintage", "neon", "warm", "cool", "dramatic"])
        
        # 根据风格设置色彩参数
        if color_style == "vintage":
            exposure = random.uniform(-0.3, 0.1)
            saturation = random.uniform(0.7, 0.9)
        elif color_style == "neon":
            exposure = random.uniform(0.2, 0.8)
            saturation = random.uniform(1.2, 1.8)
        elif color_style == "warm":
            exposure = random.uniform(0, 0.3)
            saturation = random.uniform(1.0, 1.3)
        elif color_style == "cool":
            exposure = random.uniform(-0.2, 0.2)
            saturation = random.uniform(0.8, 1.2)
        else:  # dramatic
            exposure = random.uniform(0.3, 0.7)
            saturation = random.uniform(1.1, 1.5)
        
        return {
            "color_style": color_style,
            "exposure": exposure,
            "saturation": saturation,
            "contrast": random.uniform(0.9, 1.3),
            "brightness": random.uniform(-0.1, 0.2)
        }
    
    def _build_rect_animation(self, keyframes: List[Dict]) -> str:
        """构建矩形动画字符串"""
        animations = []
        for kf in keyframes:
            x = kf["x"]
            y = kf["y"]
            animations.append(f"{kf['frame']}={x} {y} 1080 1920 1.000000")
        return ";".join(animations)
    
    def _build_rotation_animation(self, keyframes: List[Dict]) -> str:
        """构建旋转动画字符串"""
        animations = []
        for kf in keyframes:
            animations.append(f"{kf['frame']}={kf['rotation']}")
        return ";".join(animations)
    
    def _build_zoom_animation(self, start_scale: float, end_scale: float, duration: int) -> str:
        """构建缩放动画字符串"""
        start_w = int(1080 * start_scale)
        start_h = int(1920 * start_scale)
        end_w = int(1080 * end_scale)
        end_h = int(1920 * end_scale)
        
        start_x = int((1080 - start_w) / 2)
        start_y = int((1920 - start_h) / 2)
        end_x = int((1080 - end_w) / 2)
        end_y = int((1920 - end_h) / 2)
        
        return f"0={start_x} {start_y} {start_w} {start_h} 1.000000;{duration}={end_x} {end_y} {end_w} {end_h} 1.000000"
    
    def _build_blur_animation(self, intensity: float, duration: int) -> str:
        """构建模糊动画字符串"""
        mid_frame = duration // 2
        return f"0=0;{mid_frame}={int(intensity)};{duration}=0"
    
    def _build_angle_animation(self, angle: float, duration: int) -> str:
        """构建角度动画字符串"""
        return f"0={angle};{duration}={angle}"
    
    def _build_opacity_animation(self, duration: int) -> str:
        """构建透明度动画字符串"""
        return f"0=0;{duration//2}=1;{duration}=0"
    
    def _build_glitch_animation(self, intensity: float, frequency: int, duration: int) -> str:
        """构建故障动画字符串"""
        animations = []
        for i in range(0, duration, frequency):
            if random.random() < 0.7:  # 70%概率出现故障
                blur_value = int(intensity * random.uniform(50, 200))
            else:
                blur_value = 0
            animations.append(f"{i}={blur_value}")
        return ";".join(animations)
    
    def generate_xml(self, style: str, params: Dict[str, Any]) -> str:
        """生成XML字符串"""
        if style == "shake":
            return self._generate_shake_xml(params)
        elif style == "zoom":
            return self._generate_zoom_xml(params)
        elif style == "blur":
            return self._generate_blur_xml(params)
        elif style == "transition":
            return self._generate_transition_xml(params)
        elif style == "glitch":
            return self._generate_glitch_xml(params)
        elif style == "color":
            return self._generate_color_xml(params)
        else:
            raise ValueError(f"Unknown style: {style}")
    
    def _generate_shake_xml(self, params: Dict[str, Any]) -> str:
        """生成抖动特效XML"""
        template = '''<effect id="{{ id }}" tag="qtblend" type="customVideo" version="2">
 <n>{{ name }}</n>
 <description>{{ description }}</description>
 <author>{{ author }}</author>
 <parameter default="0 0 %width %height 1" name="rect" type="animatedrect" value="{{ rect_animation }}">
  <n>Rectangle</n>
 </parameter>
 <parameter compact="1" decimals="2" default="0" max="360" min="-360" name="rotation" notintimeline="1" suffix="°" type="animated" value="{{ rotation_animation }}">
  <n>Rotation</n>
 </parameter>
 <parameter default="0" name="compositing" paramlist="0;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27;28;29;6;8" type="list" value="0">
  <paramlistdisplay>Alpha blend,Xor,Plus,Multiply,Screen,Overlay,Darken,Lighten,Color dodge,Color burn,Hard light,Soft light,Difference,Exclusion,Bitwise or,Bitwise and,Bitwise xor,Bitwise nor,Bitwise nand,Bitwise not xor,Destination in,Destination out</paramlistdisplay>
  <n>Compositing</n>
 </parameter>
 <parameter default="0" max="1" min="0" name="distort" type="bool" value="0">
  <n>Distort</n>
 </parameter>
 <parameter default="1" max="1" min="0" name="rotate_center" type="bool" value="1">
  <n>Rotate from center</n>
 </parameter>
</effect>'''
        
        t = Template(template)
        return t.render(**params)
    
    def _generate_zoom_xml(self, params: Dict[str, Any]) -> str:
        """生成缩放特效XML"""
        template = '''<effectgroup description="{{ description }}" id="{{ id }}" parentIn="0">
 <description>{{ description }}</description>
 <effect id="qtblend">
  <property name="rotation">0=0;{{ duration }}=0</property>
  <property name="rect">{{ rect_scale }}</property>
  <property name="rotate_center">1</property>
  <property name="distort">0</property>
  <property name="compositing">0</property>
 </effect>
 <effect id="frei0r.lenscorrection">
  <property name="correctionnearcenter">0=0.5;{{ duration }}={{ lens_correction }}</property>
  <property name="brightness">0=0;{{ duration }}={{ brightness }}</property>
  <property name="correctionnearedges">0=0.5;{{ duration }}={{ lens_correction }}</property>
  <property name="ycenter">0=0.5;{{ duration }}=0.5</property>
  <property name="xcenter">0=0.5;{{ duration }}=0.5</property>
 </effect>
</effectgroup>'''
        
        t = Template(template)
        return t.render(**params)
    
    def _generate_blur_xml(self, params: Dict[str, Any]) -> str:
        """生成模糊特效XML"""
        template = '''<effectgroup description="{{ description }}" id="{{ id }}" parentIn="0">
 <description>{{ description }}</description>
 <effect id="avfilter.dblur">
  <property name="av.planes">15</property>
  <property name="av.radius">{{ radius_animation }}</property>
  <property name="av.angle">{{ angle_animation }}</property>
 </effect>
</effectgroup>'''
        
        t = Template(template)
        return t.render(**params)
    
    def _generate_transition_xml(self, params: Dict[str, Any]) -> str:
        """生成转场特效XML"""
        template = '''<effect id="{{ id }}" tag="qtblend" type="customVideo" version="2">
 <n>{{ name }}</n>
 <description>{{ description }}</description>
 <author>{{ author }}</author>
 <parameter default="0 0 %width %height 1" name="rect" type="animatedrect" value="0=0 0 1080 1920 1.000000;{{ duration }}=0 0 1080 1920 1.000000">
  <n>Rectangle</n>
 </parameter>
 <parameter default="0" name="compositing" paramlist="0;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27;28;29;6;8" type="list" value="{{ compositing_mode }}">
  <paramlistdisplay>Alpha blend,Xor,Plus,Multiply,Screen,Overlay,Darken,Lighten,Color dodge,Color burn,Hard light,Soft light,Difference,Exclusion,Bitwise or,Bitwise and,Bitwise xor,Bitwise nor,Bitwise nand,Bitwise not xor,Destination in,Destination out</paramlistdisplay>
  <n>Compositing</n>
 </parameter>
 <parameter default="1" max="1" min="0" name="opacity" type="animated" value="{{ opacity_animation }}">
  <n>Opacity</n>
 </parameter>
</effect>'''
        
        t = Template(template)
        return t.render(**params)
    
    def _generate_glitch_xml(self, params: Dict[str, Any]) -> str:
        """生成故障特效XML"""
        template = '''<effectgroup description="{{ description }}" id="{{ id }}" parentIn="0">
 <description>{{ description }}</description>
 <effect id="avfilter.dblur">
  <property name="av.planes">15</property>
  <property name="av.radius">{{ blur_pulses }}</property>
  <property name="av.angle">0={{ glitch_intensity * 90 }};{{ duration }}={{ glitch_intensity * 180 }}</property>
 </effect>
 <effect id="avfilter.exposure">
  <property name="av.exposure">0={{ exposure_shift }};{{ duration }}={{ exposure_shift * -1 }}</property>
  <property name="av.black">0=0;{{ duration }}=0</property>
 </effect>
</effectgroup>'''
        
        t = Template(template)
        return t.render(**params)
    
    def _generate_color_xml(self, params: Dict[str, Any]) -> str:
        """生成色彩特效XML"""
        template = '''<effectgroup description="{{ description }}" id="{{ id }}" parentIn="0">
 <description>{{ description }} - {{ color_style }}</description>
 <effect id="avfilter.exposure">
  <property name="av.exposure">{{ exposure }}</property>
  <property name="av.black">0</property>
 </effect>
 <effect id="frei0r.saturat0r">
  <property name="saturation">{{ saturation }}</property>
 </effect>
 <effect id="frei0r.brightness">
  <property name="brightness">{{ brightness }}</property>
 </effect>
</effectgroup>'''
        
        t = Template(template)
        return t.render(**params)
    
    def generate_effects(self, style: str, count: int = 10) -> List[str]:
        """批量生成特效文件"""
        generated_files = []
        style_dir = self.effects_dir / style
        style_dir.mkdir(exist_ok=True)
        
        for i in range(count):
            params = self.generate_effect_params(style)
            xml_content = self.generate_xml(style, params)
            
            filename = f"{params['id']}.xml"
            file_path = style_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            generated_files.append(str(file_path))
            print(f"Generated: {filename}")
        
        return generated_files


def main():
    parser = argparse.ArgumentParser(description="Generate kdenlive effects")
    parser.add_argument("--style", required=True, 
                      choices=["shake", "zoom", "blur", "transition", "glitch", "color"],
                      help="Effect style to generate")
    parser.add_argument("--count", type=int, default=10,
                      help="Number of effects to generate")
    parser.add_argument("--project-root", default=".",
                      help="Project root directory")
    
    args = parser.parse_args()
    
    generator = EffectGenerator(args.project_root)
    generated_files = generator.generate_effects(args.style, args.count)
    
    print(f"\nGenerated {len(generated_files)} {args.style} effects:")
    for file_path in generated_files:
        print(f"  {file_path}")


if __name__ == "__main__":
    main()
