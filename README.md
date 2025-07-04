# Kdenlive Effect Generator

自动生成kdenlive特效的工具，支持批量生成和Web预览功能，模仿TikTok和CapCut等流行特效。

## ✨ 功能特点

- 🎬 自动生成符合kdenlive规范的effect XML文件
- 🎨 支持多种风格：抖动、缩放、模糊、转场、故障、色彩等
- 👀 智能预览视频生成（1080x1920, 9:16 竖屏）
- 📁 按风格分类存储和管理特效文件
- 🌐 现代化Web界面，支持在线预览和管理
- 🤖 AI驱动的参数生成和优化
- 📱 响应式设计，支持移动端和桌面端
- ⚡ 快速预览：鼠标悬停即可播放预览视频

## 📁 目录结构

```
kdenlive-effect-generator/
├── simple_server.py          # 简化的Web服务器（推荐）
├── main.py                   # 主入口脚本
├── setup.py                 # 安装设置脚本
├── requirements.txt         # Python依赖
├── .env.example            # 环境变量示例
├── assets/                 # 素材文件夹（图片、视频）
│   ├── sample_image.jpg   # 示例图片
│   ├── sample_video.mp4   # 示例视频
│   └── test_image.jpg     # 测试图片
├── effects/                # 生成的特效文件
│   ├── shake/             # 抖动特效
│   ├── zoom/              # 缩放特效
│   ├── blur/              # 模糊特效
│   ├── transition/        # 转场特效
│   ├── glitch/            # 故障特效
│   └── color/             # 色彩特效
├── previews/              # 预览视频（按风格分类）
├── demos/                 # 演示视频（永久保存）
├── src/                   # 源代码
│   ├── effect_generator.py      # 特效生成器
│   ├── preview_generator.py     # 预览生成器
│   ├── preview_manager.py       # 预览管理器
│   └── web_server.py           # 完整Web服务器
└── web/                   # Web界面
    ├── templates/
    │   └── index.html
    └── static/
        ├── style.css
        └── app.js
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动Web服务器（推荐）

```bash
python simple_server.py
```

然后打开浏览器访问 http://localhost:5000

### 3. 使用Web界面

1. **浏览特效风格**：左侧显示所有可用的特效风格
2. **查看特效列表**：点击风格查看该风格下的所有特效
3. **预览特效**：鼠标悬停在特效卡片上自动播放预览
4. **查看详情**：点击特效卡片查看XML代码和完整预览
5. **生成新特效**：使用"生成特效"按钮创建新的特效
6. **批量预览**：为整个风格批量生成预览视频

## 💻 命令行使用

### 生成特效

```bash
# 生成指定风格的特效
python src/effect_generator.py --style shake --count 10

# 生成所有风格的特效
python src/effect_generator.py --style all --count 5
```

### 生成预览视频

```bash
# 为特定风格生成预览
python src/preview_generator.py --style shake

# 为所有特效生成预览
python src/preview_generator.py
```

### 启动完整Web服务器

```bash
python main.py web
# 或者
python src/web_server.py
```

## ⚙️ 配置

在项目根目录创建 `.env` 文件：

```bash
# OpenAI API密钥（用于AI生成特效参数）
OPENAI_API_KEY=your_openai_api_key_here

# MLT Framework路径（可选，会自动检测）
MELT_PATH=/Applications/kdenlive.app/Contents/MacOS/melt

# FFmpeg路径（可选，会自动检测）
FFMPEG_PATH=/Applications/kdenlive.app/Contents/MacOS/ffmpeg

# 预览视频配置
PREVIEW_WIDTH=1080
PREVIEW_HEIGHT=1920
PREVIEW_DURATION=5
PREVIEW_FPS=25

# Web服务器配置
WEB_HOST=localhost
WEB_PORT=5000
```

## 🎨 特效风格说明

| 风格 | 描述 | 适用场景 |
|-----|------|---------|
| **shake** | 相机抖动、震动效果 | 紧张刺激、动感场景 |
| **zoom** | 缩放、推拉镜头效果 | 强调重点、视觉冲击 |
| **blur** | 各种模糊效果 | 梦幻效果、焦点转移 |
| **transition** | 转场过渡效果 | 场景切换、时间跳跃 |
| **glitch** | 故障艺术、数字噪声 | 科技感、电子音乐 |
| **color** | 色彩调节、滤镜效果 | 情绪渲染、风格化 |

## 📋 素材要求

将图片和视频素材放在 `assets/` 文件夹下：

- **支持的视频格式**: mp4, mov, avi, mkv, webm
- **支持的图片格式**: jpg, jpeg, png, bmp, tiff
- **推荐分辨率**: 1080x1920 (9:16 竖屏) 或更高
- **建议时长**: 视频素材建议10秒以上

## 🌐 Web界面功能

### 主要功能
- **风格浏览**: 左侧显示所有特效风格，包括特效数量和预览数量统计
- **特效展示**: 以卡片形式展示特效，支持鼠标悬停自动播放预览
- **详情查看**: 点击特效查看XML代码、详细信息和完整预览视频
- **在线生成**: 支持在线生成新特效和预览视频
- **批量操作**: 支持批量生成特效和预览视频
- **文件管理**: 可下载特效XML文件和预览视频

### 交互特性
- **响应式设计**: 适配不同屏幕尺寸
- **实时预览**: 鼠标悬停即可播放预览视频
- **智能加载**: 优化的加载提示和错误处理
- **现代UI**: 使用Bootstrap 5和Font Awesome图标

## 🔧 技术特性

### 预览视频生成
- **智能回退**: 优先使用MLT渲染，FFmpeg作为备选方案
- **多格式支持**: 自动处理图片和视频素材
- **质量优化**: 自动调整分辨率和编码参数
- **错误恢复**: 在工具不可用时创建有效的占位视频

### Web服务架构
- **Flask后端**: 轻量级Web框架
- **RESTful API**: 标准化的API接口
- **静态文件服务**: 高效的文件传输
- **错误处理**: 完善的异常捕获和用户提示

## 🚨 注意事项

1. **依赖检查**: 系统会自动检测MLT和FFmpeg，无需手动配置
2. **预览生成**: 首次生成预览需要一定时间，请耐心等待
3. **文件兼容**: 生成的特效XML文件完全兼容kdenlive
4. **浏览器支持**: 推荐使用现代浏览器（Chrome, Firefox, Safari等）
5. **存储空间**: 预览视频会占用一定存储空间，可定期清理

## 🐛 故障排除

### 🔧 常见问题

#### Web服务器无法启动
```bash
# 检查端口是否被占用
lsof -i :5000

# 使用不同端口启动
python simple_server.py --port 8080
```

#### 预览视频生成失败
```bash
# 检查FFmpeg是否可用
ffmpeg -version

# 检查assets目录是否有素材文件
ls -la assets/

# 手动创建测试素材
python src/create_test_assets.py
```

#### MLT相关错误
```bash
# macOS安装MLT
brew install mlt

# Ubuntu/Debian安装MLT
sudo apt-get install melt

# 检查MLT版本
melt --version
```

#### 依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 检查Python版本（推荐3.8+）
python --version
```

### 🏃‍♂️ 性能优化

- **素材优化**: 使用适当分辨率的素材文件
- **批量操作**: 避免同时生成大量预览视频
- **存储清理**: 定期清理不需要的预览文件
- **内存管理**: 关闭不需要的特效详情窗口

## 🚀 开发说明

### 项目架构
- **模块化设计**: 每个功能模块独立开发和测试
- **API驱动**: 前后端分离，便于扩展
- **错误处理**: 完善的异常捕获和用户友好的错误提示

### 特效模板
- 使用Jinja2模板引擎生成XML文件
- 支持参数化配置和随机值生成
- 兼容kdenlive的effect格式规范

### 扩展开发
```bash
# 添加新的特效风格
# 1. 在templates/目录下创建新的模板文件
# 2. 在effect_generator.py中添加对应的生成逻辑
# 3. 更新Web界面的风格列表
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 贡献指南
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/your-repo/kdenlive-effect-generator/issues)

## 🙏 致谢

感谢以下开源项目：
- [Kdenlive](https://kdenlive.org/) - 专业的视频编辑软件
- [MLT Framework](https://www.mltframework.org/) - 多媒体处理框架
- [FFmpeg](https://ffmpeg.org/) - 强大的音视频处理库
- [Flask](https://flask.palletsprojects.com/) - 轻量级Web框架
- [Bootstrap](https://getbootstrap.com/) - 现代化UI框架
