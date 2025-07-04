# Kdenlive Effect Generator - 使用指南

## 📁 项目结构

```
kdenlive-effect-generator/
├── simple_server.py          # 简化Web服务器（推荐使用）
├── main.py                   # 主入口脚本
├── setup.py                 # 安装和配置脚本
├── requirements.txt         # Python依赖包
├── .env.example            # 环境变量配置示例
├── README.md               # 项目介绍
├── USAGE.md               # 使用指南（本文件）
├── assets/                # 素材文件夹
│   ├── sample_image.jpg   # 示例图片素材
│   ├── sample_video.mp4   # 示例视频素材
│   └── test_image.jpg     # 测试图片
├── effects/               # 生成的特效XML文件
│   ├── shake/             # 抖动特效
│   ├── zoom/              # 缩放特效
│   ├── blur/              # 模糊特效
│   ├── transition/        # 转场特效
│   ├── glitch/            # 故障艺术特效
│   └── color/             # 色彩调节特效
├── previews/              # 预览视频（临时，按风格分类）
├── demos/                 # 演示视频（永久保存）
├── src/                   # 核心源代码
│   ├── effect_generator.py      # 特效XML生成器
│   ├── preview_generator.py     # 预览视频生成器
│   ├── preview_manager.py       # 预览管理器
│   ├── web_server.py           # 完整Web服务器
│   └── create_test_assets.py    # 测试素材创建工具
└── web/                   # Web界面资源
    ├── templates/         # HTML模板
    │   └── index.html     # 主页面模板
    └── static/            # 静态资源
        ├── style.css      # 样式文件
        └── app.js         # 前端交互逻辑
```

## 🚀 快速开始

### 方法一：一键启动（推荐）

```bash
# 直接启动Web服务器
python simple_server.py
```

访问 http://localhost:5000 即可使用完整的Web界面。

### 方法二：使用主入口脚本

```bash
# 启动Web界面
python main.py web

# 生成特效
python main.py generate --style shake --count 5

# 生成预览
python main.py preview --style shake
```

### 方法三：手动安装配置

1. **安装Python依赖**：
```bash
pip install -r requirements.txt
```

2. **创建环境配置**（可选）：
```bash
cp .env.example .env
# 编辑.env文件设置API密钥等配置
```

3. **准备素材文件**：
```bash
# 将图片和视频文件放入assets目录
# 或使用工具创建测试素材
python src/create_test_assets.py
```

4. **启动服务**：
```bash
python simple_server.py
```

## 💻 命令行使用

### 🎬 生成特效

```bash
# 生成指定风格和数量的特效
python src/effect_generator.py --style shake --count 10

# 生成所有风格的特效
python src/effect_generator.py --style all --count 5

# 使用主入口脚本
python main.py generate --style shake --count 10
```

### 🎥 生成预览视频

```bash
# 为特定风格生成预览
python src/preview_generator.py --style shake

# 为所有特效生成预览
python src/preview_generator.py

# 为特定特效文件生成预览
python src/preview_generator.py --effect-file effects/shake/shake_1234.xml

# 使用主入口脚本
python main.py preview --style shake
```

### 🌐 启动Web服务

```bash
# 使用简化服务器（推荐）
python simple_server.py

# 使用完整服务器
python src/web_server.py

# 使用主入口脚本
python main.py web

# 自定义端口
python simple_server.py --port 8080
```

### 🛠️ 工具命令

```bash
# 创建测试素材
python src/create_test_assets.py

# 检查系统环境
python setup.py --check

# 清理临时文件
python setup.py --clean
```

## 🌐 Web界面使用指南

### 主要功能区域

1. **导航栏**
   - 项目标题和主要操作按钮
   - 浏览Demos、生成特效、刷新数据

2. **风格列表（左侧）**
   - 显示所有可用的特效风格
   - 实时显示每个风格的特效数量和预览数量
   - 点击风格名称查看该风格下的所有特效

3. **特效展示区（右侧）**
   - 以卡片形式展示特效
   - 鼠标悬停自动播放预览视频
   - 显示特效名称、描述和操作按钮

4. **生成特效面板（左下）**
   - 选择风格和生成数量
   - 一键生成新特效

### 🎮 交互操作

#### 浏览和预览
- **选择风格**: 点击左侧风格列表中的任意风格
- **查看特效**: 右侧会显示该风格下的所有特效
- **快速预览**: 鼠标悬停在特效卡片上，预览视频会自动播放
- **停止预览**: 鼠标移开，预览视频会自动暂停并重置

#### 详细查看
- **特效详情**: 点击特效卡片打开详情模态框
- **XML代码**: 在详情模态框中查看完整的特效XML代码
- **复制代码**: 点击复制按钮将XML代码复制到剪贴板
- **下载特效**: 点击下载按钮保存特效XML文件

#### 生成操作
- **生成特效**: 在左下角面板选择风格和数量，点击生成
- **生成预览**: 点击特效卡片上的"预览"按钮为单个特效生成预览
- **批量预览**: 点击"批量预览"按钮为整个风格生成预览视频

#### Demo管理
- **浏览Demos**: 点击导航栏的"浏览Demos"查看所有演示视频
- **搜索过滤**: 在Demos页面可以搜索和过滤视频
- **播放下载**: 可以播放、下载或删除Demo视频

### 🎨 界面特性

#### 响应式设计
- **桌面端**: 完整的多栏布局
- **平板端**: 自适应的布局调整
- **手机端**: 优化的单栏显示

#### 视觉反馈
- **加载状态**: 智能的加载遮罩和进度提示
- **操作反馈**: 成功、警告、错误的消息提示
- **悬停效果**: 丰富的鼠标悬停交互效果

#### 用户体验
- **快速响应**: 优化的前端性能
- **错误处理**: 友好的错误提示和恢复建议
- **状态保持**: 保持用户的浏览状态和选择

## 🎨 特效风格详解

### Shake（抖动特效）
- **用途**: 模仿手持相机的抖动效果，增加紧张感和真实感
- **参数**: 抖动强度、频率、方向等
- **适用场景**: 动作场面、紧张气氛、真实感渲染
- **效果示例**: 随机位置偏移、旋转抖动、缩放抖动

### Zoom（缩放特效）
- **用途**: 创建推拉镜头效果，强调重点内容
- **参数**: 缩放比例、缩放中心、缩放速度等
- **适用场景**: 重点强调、视觉冲击、戏剧效果
- **效果示例**: 逐渐放大、快速缩小、弹性缩放

### Blur（模糊特效）
- **用途**: 创建各种模糊效果，营造梦幻或失焦感
- **参数**: 模糊半径、模糊类型、动画曲线等
- **适用场景**: 梦幻效果、焦点转移、艺术渲染
- **效果示例**: 高斯模糊、运动模糊、径向模糊

### Transition（转场特效）
- **用途**: 在场景切换时提供平滑的过渡效果
- **参数**: 过渡时间、过渡方向、过渡样式等
- **适用场景**: 场景切换、时间跳跃、故事转折
- **效果示例**: 淡入淡出、滑动切换、旋转过渡

### Glitch（故障特效）
- **用途**: 模拟数字信号干扰和故障艺术效果
- **参数**: 故障强度、颜色偏移、噪声类型等
- **适用场景**: 科技感、电子音乐、艺术表达
- **效果示例**: RGB分离、数字噪声、信号失真

### Color（色彩特效）
- **用途**: 调整和增强视频的色彩表现
- **参数**: 色相、饱和度、亮度、对比度等
- **适用场景**: 情绪渲染、风格化、色彩校正
- **效果示例**: 复古滤镜、冷暖色调、高对比度

## ⚙️ 配置选项

### 环境变量配置

在项目根目录创建 `.env` 文件进行个性化配置：

```bash
# OpenAI API配置（用于AI生成特效参数）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# 视频处理工具路径（可选，系统会自动检测）
MELT_PATH=/Applications/kdenlive.app/Contents/MacOS/melt
FFMPEG_PATH=/Applications/kdenlive.app/Contents/MacOS/ffmpeg

# 预览视频参数
PREVIEW_WIDTH=720          # 预览视频宽度
PREVIEW_HEIGHT=1280        # 预览视频高度（9:16竖屏）
PREVIEW_DURATION=5         # 预览视频时长（秒）
PREVIEW_FPS=25            # 预览视频帧率

# Web服务器配置
WEB_HOST=localhost         # 服务器主机地址
WEB_PORT=5000             # 服务器端口
WEB_DEBUG=False           # 调试模式

# 文件路径配置
ASSETS_DIR=assets          # 素材文件目录
EFFECTS_DIR=effects        # 特效文件目录
PREVIEWS_DIR=previews      # 预览视频目录
DEMOS_DIR=demos           # 演示视频目录
```

### 高级配置

#### 特效生成参数
```bash
# 特效生成的默认参数范围
EFFECT_PARAM_MIN=0.1       # 参数最小值
EFFECT_PARAM_MAX=2.0       # 参数最大值
EFFECT_DURATION_MIN=1      # 特效最短时长
EFFECT_DURATION_MAX=10     # 特效最长时长
```

#### 性能优化配置
```bash
# 并发处理数量
MAX_CONCURRENT_RENDERS=2   # 同时渲染的视频数量
RENDER_TIMEOUT=300        # 渲染超时时间（秒）

# 缓存配置
ENABLE_CACHE=True         # 启用预览缓存
CACHE_MAX_SIZE=1000       # 缓存最大数量
```

## 📋 素材管理

### 素材要求

将图片和视频素材放在 `assets/` 文件夹下，系统支持以下格式：

#### 视频格式
- **MP4** (.mp4) - 推荐，兼容性最好
- **MOV** (.mov) - 高质量，适合macOS
- **AVI** (.avi) - 传统格式
- **MKV** (.mkv) - 开源格式
- **WebM** (.webm) - 网络优化格式

#### 图片格式
- **JPEG** (.jpg, .jpeg) - 压缩格式，文件小
- **PNG** (.png) - 无损格式，支持透明
- **BMP** (.bmp) - 位图格式
- **TIFF** (.tiff) - 高质量格式

### 素材建议

#### 分辨率建议
- **推荐分辨率**: 720x1280 (9:16 竖屏)
- **最低分辨率**: 480x854
- **最高分辨率**: 1080x1920 (更高分辨率会被自动缩放)

#### 时长建议
- **视频素材**: 建议10秒以上，提供足够的素材内容
- **图片素材**: 会被转换为5秒的静态视频

#### 质量建议
- **视频码率**: 建议2-8 Mbps
- **图片质量**: 建议中等到高质量，避免过度压缩
- **色彩空间**: 推荐使用sRGB色彩空间

### 素材组织

```
assets/
├── videos/              # 视频素材（可选子目录）
│   ├── sample_video.mp4
│   └── test_video.mov
├── images/              # 图片素材（可选子目录）
│   ├── sample_image.jpg
│   └── test_image.png
├── sample_video.mp4     # 直接放在根目录也可以
└── sample_image.jpg
```

### 创建测试素材

如果没有合适的素材，可以使用工具创建：

```bash
# 创建测试素材
python src/create_test_assets.py

# 手动创建简单测试文件
echo "Test video content" > assets/test_video.mp4
echo "Test image content" > assets/test_image.jpg
```

## 🚨 注意事项

### 重要提醒

1. **工具依赖**: 系统会自动检测MLT和FFmpeg，无需手动安装
2. **首次使用**: 第一次生成预览需要较长时间，请耐心等待
3. **文件兼容**: 生成的XML文件完全兼容kdenlive和其他支持MLT的软件
4. **浏览器兼容**: 推荐使用现代浏览器（Chrome 80+, Firefox 75+, Safari 13+）
5. **存储空间**: 预览视频会占用存储空间，可定期清理

### 性能优化

1. **素材优化**: 使用适当分辨率的素材，避免过大文件
2. **批量限制**: 避免同时生成过多预览视频
3. **内存管理**: 关闭不需要的特效详情窗口
4. **存储清理**: 定期清理 `previews/` 目录中的临时文件

### 安全建议

1. **API密钥**: 不要将 `.env` 文件提交到版本控制
2. **文件权限**: 确保 `assets/` 目录有读写权限
3. **网络访问**: Web界面默认只在本地访问，生产环境需要额外配置

## 🔧 故障排除

### 常见问题解决

#### Web服务无法启动
```bash
# 检查端口占用
lsof -i :5000

# 使用其他端口
python simple_server.py --port 8080

# 检查防火墙设置
```

#### 预览生成失败
```bash
# 检查素材文件
ls -la assets/

# 检查FFmpeg
ffmpeg -version

# 查看详细错误日志
python simple_server.py --debug
```

#### 特效无法加载
```bash
# 检查effects目录
ls -la effects/

# 重新生成特效
python src/effect_generator.py --style shake --count 1

# 检查XML文件格式
```

#### 依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 检查Python版本
python --version  # 推荐3.8+

# 虚拟环境问题
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

## 🚀 高级使用

### 自定义特效模板

1. **创建模板文件**: 在 `templates/` 目录下创建新的Jinja2模板
2. **定义参数**: 使用模板变量定义可配置的特效参数
3. **注册特效**: 在 `effect_generator.py` 中添加新的特效类型
4. **测试验证**: 生成测试特效并在kdenlive中验证

### API接口扩展

当前提供的API接口：
- `GET /api/styles` - 获取所有风格列表
- `GET /api/effects/{style}` - 获取指定风格的特效列表
- `GET /api/effect/{style}/{effect_id}` - 获取特效详情
- `POST /api/generate` - 生成新特效
- `POST /api/generate_preview` - 生成单个预览
- `POST /api/generate_batch_preview` - 批量生成预览

### 部署到生产环境

```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 simple_server:app

# 使用Docker部署
# 创建Dockerfile并构建镜像

# 使用Nginx反向代理
# 配置Nginx转发到Flask应用
```

## 📚 开发文档

### 代码结构说明

- **simple_server.py**: 轻量级Web服务器，包含所有必要的API接口
- **src/effect_generator.py**: 核心特效生成逻辑
- **src/preview_generator.py**: 预览视频生成和渲染
- **web/**: 前端界面资源，使用Bootstrap 5和原生JavaScript

### 扩展开发

添加新特效风格的步骤：
1. 在 `templates/` 下创建新的XML模板
2. 在 `effect_generator.py` 中添加生成逻辑
3. 在 `web/static/app.js` 中更新风格图标和显示名称
4. 测试新特效的生成和预览功能

## 📄 许可证和贡献

### 开源许可
本项目使用 MIT License，允许自由使用、修改和分发。

### 贡献指南
欢迎提交 Issue 和 Pull Request！贡献前请阅读项目的贡献指南。

### 技术支持
- GitHub Issues: 报告Bug和功能请求
- 文档更新: 帮助完善使用文档
- 代码贡献: 提交新功能和性能优化
