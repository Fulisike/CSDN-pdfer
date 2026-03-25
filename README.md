# CSDN PDFer - 博客转PDF工具

一个将CSDN博客文章转换为Markdown和PDF格式的Python工具。支持自动下载图片并生成本地化文档。

## 功能特点

- 🌐 直接输入CSDN文章URL即可转换
- 📄 生成高质量的PDF格式文档
- 🖼️ 自动下载并本地化所有图片
- 📁 使用相对路径引用图片（Markdown）
- 🎨 美观的PDF输出格式
- 💾 记住上次使用的输出路径
- 🖥️ 友好的图形界面
- 🧹 **自动清理临时文件**：转换完成后自动删除.md文件和images/文件夹，只保留PDF

## 安装步骤

### 1. 设置虚拟环境

```bash
# 运行设置脚本
setup_venv.bat
```

这会自动创建Python虚拟环境并安装所有依赖。

### 2. 安装wkhtmltopdf（仅开发环境需要）

如果你要从源码运行，需要安装wkhtmltopdf：

下载并安装 [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

- Windows: 下载并安装到默认路径
- 建议安装到: `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`

**注意**：如果你使用打包好的exe版本，不需要单独安装wkhtmltopdf，它已经包含在分发包中。

## 使用方法

### 方式一：运行GUI版本（推荐）

```bash
# 激活虚拟环境
venv\Scripts\activate.bat

# 运行GUI程序
python gui_main.py
```

在GUI中：
1. 输入CSDN文章URL
2. 选择输出PDF的保存位置
3. 点击"开始转换"按钮

### 方式二：打包为EXE（用于分发）

```bash
# 激活虚拟环境
venv\Scripts\activate.bat

# 运行打包脚本（会自动包含wkhtmltopdf）
build_exe_simple.bat
```

打包完成后，`dist` 文件夹中包含：
- `CSDN-PDFer.exe` - 主程序
- `wkhtmltopdf.exe` - PDF生成引擎
- `wkhtmltox.dll` - 必需的库文件

**分发时将这3个文件一起打包，用户无需安装任何依赖！**

## 项目结构

```
csdn-pdfer/
├── main.py              # 核心转换类
├── gui_main.py          # GUI界面
├── requirements.txt     # 依赖列表
├── setup_venv.bat       # 虚拟环境设置脚本
├── build_exe_simple.bat # 打包脚本
└── README.md           # 本文件
```

## 核心功能说明

### HtmlToMdPdfConverter 类

主要转换流程：
1. HTML解析与内容提取
2. 图片发现与下载（使用MD5命名避免冲突）
3. HTML到Markdown转换
4. Markdown到PDF转换（带样式）
5. **自动清理临时文件**（.md文件和images/文件夹）

### 图片处理

- 图片保存到: `output_dir/images/`（临时，PDF生成后删除）
- Markdown中使用相对路径引用（临时文件）
- PDF生成时转换为绝对路径
- 支持相对和绝对URL
- **最终输出**：只保留PDF文件

### 输出文件

- **最终输出**：`{output_name}.pdf` - 唯一保留的文件
- **临时文件**（自动删除）：
  - `{output_name}.md` - Markdown中间文件
  - `images/` - 下载的图片文件夹

如需保留临时文件进行调试，可在 `main.py` 中设置 `keep_temp_files=True`

## 依赖项

- requests - HTTP请求
- beautifulsoup4 - HTML解析
- markdownify - HTML转Markdown
- markdown - Markdown转HTML
- pdfkit - HTML转PDF
- pyinstaller - 打包工具
- tkinter - GUI（Python内置）

## 配置文件

用户配置保存在: `~csdn_pdfer_config.json`

记录最后一次使用的输出路径。

## 注意事项

### 开发环境运行
1. **wkhtmltopdf是必需的**：必须安装wkhtmltopdf才能生成PDF
2. **网络连接**：需要能够访问CSDN和图片服务器
3. **输出目录**：确保有写入权限
4. **中文支持**：PDF输出支持中文，使用微软雅黑字体

### 打包版本分发
1. **无需安装依赖**：打包后的exe已包含所有必需文件
2. **3个文件必须在一起**：`CSDN-PDFer.exe`、`wkhtmltopdf.exe`、`wkhtmltox.dll` 必须在同一目录
3. **直接运行**：双击 `CSDN-PDFer.exe` 即可使用

## 故障排除

### 开发环境问题

#### PDF生成失败
- 确认wkhtmltopdf已正确安装
- 检查 `gui_main.py` 中的路径是否正确

#### 图片下载失败
- 检查网络连接
- 某些图片可能需要特定的请求头

### 打包版本问题

#### EXE无法运行
- 确保3个文件都在同一目录：`CSDN-PDFer.exe`、`wkhtmltopdf.exe`、`wkhtmltox.dll`
- 检查是否被杀毒软件阻止

#### PDF生成失败
- 确认 `wkhtmltopdf.exe` 和 `wkhtmltox.dll` 存在
- 不要重命名这两个文件
- 确保它们与 `CSDN-PDFer.exe` 在同一目录

## 许可证

本项目仅供学习和个人使用。
