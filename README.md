# Codebase to Prompt

一个简单的桌面工具，将本地代码库转换为结构化提示文本，适用于大型语言模型（LLM）。帮助您选择要包含或忽略的文件，然后以可直接复制到 LLM 的格式输出，用于代码审查、分析或文档生成。

## 概述

**Codebase to Prompt** 是一个基于 Python 和 Tkinter 的桌面应用程序，扫描您选择的文件夹并构建文件树。您可以展开文件夹，查看哪些文件是文本或代码文件，并仅选择需要的文件。选定的文件随后被编译成结构化文本片段，您可以复制用于 LLM。

## 功能特性

- **交互式文件树**  
  在简单的界面中浏览和展开本地文件夹，支持展开/折叠所有节点。

- **智能文件过滤**  
  自动忽略系统或二进制文件（如 `.DS_Store`、`node_modules`、图片、视频等）。

- **复选框选择**  
  支持文件和目录的复选框选择，支持全选/取消全选，支持父子级联选择。

- **实时预览**  
  右侧面板实时显示生成的提示文本，包含文件夹结构和文件内容。

- **LLM 就绪输出**  
  生成易于粘贴到聊天机器人和其他 AI 工具的格式，包含文件夹结构和文档块。

- **Token 计数估算**  
  提供所选内容可能使用的 token 数量的粗略计算。

- **一键复制**  
  一键将生成的提示文本复制到剪贴板。

- **性能优化**  
  支持大型项目（最多 10,000 个文件），使用后台线程处理文件读取，避免界面冻结。

## 系统要求

- Python 3.6 或更高版本
- Tkinter（通常随 Python 一起安装）
- Windows、macOS 或 Linux

## 安装

### 方式一：下载预编译的可执行文件（推荐）

从 [Releases](https://github.com/turandot2017/codebase2prompt/releases) 页面下载最新版本：

- **Windows**: `codebase2prompt-windows.exe`
- **Linux**: `codebase2prompt-linux`
- **macOS**: `codebase2prompt-macos`

#### 使用说明

**Windows 用户**：
- 直接双击运行 `codebase2prompt-windows.exe`
- 如果 Windows Defender 提示未知应用，点击"更多信息" → "仍要运行"

**Linux 用户**：
```bash
# 添加执行权限
chmod +x codebase2prompt-linux

# 运行应用
./codebase2prompt-linux
```

**macOS 用户**：
```bash
# 添加执行权限
chmod +x codebase2prompt-macos

# 运行应用
./codebase2prompt-macos
```

> **注意**：macOS 可能会提示"无法打开应用"，因为应用未经签名。解决方法：
> 1. 右键点击应用 → 选择"打开"
> 2. 或在"系统偏好设置" → "安全性与隐私"中点击"仍要打开"

### 方式二：从源代码运行

1. **克隆或下载项目**
   ```bash
   git clone https://github.com/turandot2017/codebase2prompt.git
   cd codebase2prompt
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用**
   ```bash
   python main.py
   ```

### 方式三：自行编译可执行文件

使用 PyInstaller 编译为独立可执行文件：

```bash
# 安装 PyInstaller（如果尚未安装）
pip install pyinstaller

# 编译
pyinstaller main.spec

# 或直接使用命令
pyinstaller --onefile --windowed --icon=logo.ico main.py
```

编译后的可执行文件将位于 `dist/` 目录中。

## 使用方法

1. **启动应用**  
   运行 `main.py` 或双击可执行文件。

2. **选择目录**  
   点击 "Select Directory" 按钮，选择要分析的文件夹。

3. **浏览和选择文件**  
   - 展开或折叠目录树
   - 点击复选框选择或取消选择文件和目录
   - 选择目录会自动选择其所有子文件和子目录
   - 使用 "Expand All" / "Collapse All" 快速展开或折叠所有节点
   - 使用 "Select All" / "Deselect All" 快速选择或取消选择所有文件

4. **查看生成的提示**  
   右侧面板会实时显示生成的提示文本，包含：
   - 文件夹结构（ASCII 树形图）
   - 每个选定文件的完整内容（包装在 `<document>` 标签中）

5. **复制到剪贴板**  
   点击 "Copy to Clipboard" 按钮将生成的提示文本复制到剪贴板。

6. **清除选择**  
   点击 "Clear" 按钮清除当前选择并重新开始。

## 输出格式

生成的提示文本格式如下：

```
<folder-structure>
project-name
├── src
│   ├── main.py
│   └── utils.py
└── README.md
</folder-structure>

<document path="src/main.py">
...文件内容...
</document>

<document path="src/utils.py">
...文件内容...
</document>

<document path="README.md">
...文件内容...
</document>
```

## 配置

### 忽略的目录

默认忽略以下目录：
- `node_modules`
- `venv`
- `.git`
- `__pycache__`
- `.idea`
- `.vscode`

### 忽略的文件

默认忽略以下文件类型和文件名：
- 图片文件：`.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`, `.psd`, `.ai`, `.eps`, `.tiff`
- 视频文件：`.mp4`, `.mov`, `.avi`, `.mkv`, `.wmv`, `.flv`, `.3gp`
- 音频文件：`.flac`, `.m4a`, `.aac`
- 压缩文件：`.zip`, `.tar`, `.gz`, `.rar`
- 系统文件：`.DS_Store`, `Thumbs.db`, `.env`, `.pyc`
- 可执行文件：`.exe`, `.bin`, `.iso`, `.dll`
- 字体文件：`.woff`, `.woff2`, `.ttf`, `.otf`

### 修改配置

要修改忽略的目录或文件列表，请编辑 `main.py` 文件中的以下常量：

```python
IGNORED_DIRECTORIES = {'node_modules', 'venv', '.git', ...}
IGNORED_FILES = {'.DS_Store', 'Thumbs.db', ...}
LIKELY_TEXT_EXTENSIONS = {'.txt', '.md', '.py', ...}
```

## 使用场景

- 为 AI 代码审查或问答创建上下文
- 快速提取大型项目的重要部分进行分析
- 为 LLM 调试准备代码片段
- 为新开发者或文档生成参考材料
- 将整个代码库转换为单个提示文本，用于 AI 辅助开发

## 技术细节

- **GUI 框架**：Tkinter
- **文件处理**：使用后台线程异步读取文件，避免界面冻结
- **性能优化**：
  - 文件内容缓存，避免重复读取
  - 限制最大文件数量（10,000 个文件）
  - 使用路径映射优化树节点查找

## 限制

- 最大支持 10,000 个文件（超过此限制会显示错误提示）
- 仅处理文本文件（自动检测或基于扩展名）
- 大文件可能导致生成时间较长

## 故障排除

### 应用无法启动

- 确保已安装 Python 3.6 或更高版本
- 确保已安装所有依赖：`pip install -r requirements.txt`
- 检查 Tkinter 是否可用：`python -m tkinter`

### 文件读取错误

- 检查文件权限
- 确保文件不是二进制文件
- 某些特殊字符可能导致编码问题（应用使用 UTF-8 编码，错误会被忽略）

### 复制到剪贴板失败

- 如果内容过大，可能无法复制到剪贴板
- 尝试手动选择文本并复制

## 开发

### 项目结构

```
codebase2prompt_tool/
├── main.py              # 主应用程序文件
├── main.spec            # PyInstaller 配置文件
├── requirements.txt     # Python 依赖
├── logo.ico             # 应用图标
├── logo.svg             # SVG 图标
├── dist/                # 编译输出目录
├── build/               # 构建临时文件
└── refer/               # 参考实现（JavaScript 版本）
```

### 贡献

欢迎贡献！请随时提交问题报告或功能请求。对于重大更改，请先创建问题讨论。

## 许可证

MIT License

## 致谢

- 基于 [CodebaseToPrompt](https://github.com/hello-nerdo/CodebaseToPrompt) JavaScript 版本的 Python 桌面实现
- 使用 Tkinter 构建 GUI
- 使用 PyInstaller 打包为可执行文件

## 联系方式

- 在 GitHub 上提交问题以报告错误或提出建议
- 提交 Pull Request 进行直接贡献

