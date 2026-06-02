# 论文自动生成工具 (Thesis Generator)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Claude API](https://img.shields.io/badge/Claude-API-0071e3?logo=anthropic)](https://www.anthropic.com/)

用 AI 重新定义学位论文创作：一行命令，自动生成格式规范的完整论文初稿。

## 什么是 Thesis Generator？

**Thesis Generator** 是一个全栈 AI 论文生成系统，旨在加速中文学术写作。上传开题报告 + 研究数据（Excel/CSV/PDF），系统自动调用 Claude API 经过 8 个阶段生成完整、格式化的 Word 论文：

1. **文件解析** — 智能提取开题报告、数据文件和参考文献
2. **数据分析** — 自动生成描述性统计、相关性矩阵、分布图表  
3. **大纲生成** — 基于提案和数据生成论文结构
4. **文献综述** — AI 撰写理论背景和研究现状（带学术引用格式）
5. **研究方法** — 描述数据采集、处理和分析方法论
6. **结果分析** — 结合生成的图表和统计结果编写发现章节
7. **结论与摘要** — 生成学术摘要和总结讨论
8. **Word 输出** — 组装为符合学术规范的 .docx 文档（宋体、行距、页眉等）

## 核心亮点

✨ **8 阶段 AI 管道** — Claude API 多阶段链式调用，每阶段输入上文信息，确保逻辑连贯  
📊 **智能数据分析** — 自动生成 matplotlib 图表（相关性热力图、分布直方图），嵌入最终文档  
📝 **学术格式输出** — python-docx 生成符合中文学位论文规范的 Word 文档（标题、目录、字体、行距）  
🔄 **容错机制** — 内置 3 次重试逻辑，应对 API 超时  
🚀 **实时进度流** — 前端 Server-Sent Events（SSE）显示 8 个阶段的实时生成进度  
📦 **多格式支持** — 接收 DOCX/PDF/TXT/MD（开题报告）+ CSV/XLSX（数据文件）  
🌐 **零配置部署** — Zeabur 配置已内置（Python 3.12 + Uvicorn）

## 架构

```
┌─────────────┐
│   Upload    │  用户上传开题报告 + 数据文件（DOCX/PDF/CSV/XLSX）
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────────────────┐
│  Backend (FastAPI + Uvicorn)                        │
├─────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐  │
│  │ File Parser (file_parser.py)                 │  │
│  │ - parse_docx() → 提取开题报告文本           │  │
│  │ - parse_pdf() → 提取参考文献                │  │
│  │ - parse_data_file() → 读取数据为 DataFrame │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │ Data Analyzer (data_analyzer.py)             │  │
│  │ - 描述性统计、缺失值检测                    │  │
│  │ - 相关性矩阵、分布直方图（matplotlib）     │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │ Thesis Generator (thesis_generator.py)       │  │
│  │ - 6 个 generate_*() 方法                    │  │
│  │ - 每个调用 Claude API（带 3 次重试）       │  │
│  │ - 使用优化的 prompts.py 模板               │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │ DOCX Builder (docx_builder.py)               │  │
│  │ - markdown_to_docx() 将 Markdown 转为格式化文本│
│  │ - set_chinese_font() 应用中文字体样式      │  │
│  │ - 插入图表、设置样式、生成最终 .docx      │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │ API Endpoints (app.py)                       │  │
│  │ - POST /api/generate → SSE 流式响应        │  │
│  │ - GET /download/{filename} → 下载文档      │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────────────────────┐
│  External APIs                                       │
├──────────────────────────────────────────────────────┤
│  - Anthropic Claude API (claude-sonnet-4-20250514)   │
│  - 调用流：大纲 → 文献 → 方法 → 结果 → 结论/摘要  │
└──────────────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│  Output      │  论文.docx（output/）+ 图表（output/charts/）
└──────────────┘
```

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **后端框架** | FastAPI 0.115.0 | 现代异步 Web 框架 + 自动 OpenAPI 文档 |
| **服务器** | Uvicorn 0.30.0 | ASGI 服务器，支持异步 I/O |
| **AI 核心** | Anthropic Claude SDK (≥0.40.0) | Claude Sonnet 4 模型，支持 8K token 输出 |
| **文档生成** | python-docx 1.1.0 | 编程方式创建 .docx 文档，支持样式和格式 |
| **数据分析** | pandas 2.2.0 | DataFrame 操作、统计分析 |
| **可视化** | matplotlib 3.9.0 | 生成相关性矩阵热力图、直方图 |
| **文件解析** | pdfplumber 0.11.0 | PDF 文本提取 |
| **Excel 支持** | openpyxl 3.1.2 | .xlsx 文件读取 |
| **前端** | Vanilla JavaScript + CSS3 | 无依赖，轻量级交互 UI（拖放、进度显示） |
| **部署** | Zeabur | 一键部署（包含 Python 3.12 环境配置） |

## 快速开始

### 前置要求

- **Python 3.12+**（[下载](https://www.python.org/downloads/)）
- **ANTHROPIC_API_KEY** — Claude API 密钥（[申请](https://console.anthropic.com/)）
- **pip** 或 **uv** 包管理器

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/thesis-generator.git
cd thesis-generator

# 创建虚拟环境（推荐）
python3.12 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

在项目根目录创建 `.env` 文件：

```env
# .env
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
PORT=8000
```

> ⚠️ **安全提示**：永远不要将 `.env` 提交到版本控制系统。`.gitignore` 已配置自动忽略。

或直接设置环境变量：

```bash
export ANTHROPIC_API_KEY=sk-ant-...your-key-here...
python app.py
```

### 3. 运行

```bash
python app.py
```

输出：
```
论文自动生成工具启动中... http://localhost:8000
INFO:     Uvicorn running on http://0.0.0.0:8000
```

打开浏览器访问 **http://localhost:8000**，看到如下界面：

```
┌─────────────────────────────────────────┐
│     论文自动生成工具                    │
│  上传开题报告和数据文件，自动生成完整论文│
├─────────────────────────────────────────┤
│ 1. 上传文件                              │
│    [拖拽文件或点击选择]                  │
│    ✓ proposal.pdf (245 KB)              │
│    ✓ data.xlsx (102 KB)                 │
├─────────────────────────────────────────┤
│ 2. 论文信息                              │
│    标题: [输入]    学位: [本科/硕士/博士]│
│    作者: [输入]    学校: [输入]          │
├─────────────────────────────────────────┤
│              [开始生成论文]               │
└─────────────────────────────────────────┘
```

### 4. 使用示例

#### 场景：生成教育学论文

**输入文件结构：**
```
uploads/abc123de/
├── proposal.pdf          # 开题报告（5 页）
├── survey_data.xlsx      # 问卷调查数据（500 行 × 12 列）
└── reference.txt         # 参考文献列表（可选）
```

**表单输入：**
```
论文标题:  中学生学习压力与心理健康的关系研究
学科方向:  教育学
学位层次:  硕士
作者:     王小明
学校:     北京师范大学
```

**生成流程（实时进度）：**
```
1. 解析文件 ............................ [完成] ✓
   → 提取开题报告：3200 字
   → 读取数据：500 行 × 12 列

2. 数据分析 ........................... [完成] ✓
   → 生成相关性矩阵热力图
   → 生成 5 个变量分布直方图

3. 生成大纲 ........................... [完成] ✓
   → 预览: 论文完整标题、关键词、章节结构...

4. 撰写文献综述 ....................... [完成] ✓
   → 预览: ## 理论基础、## 核心概念界定...

5. 撰写研究方法 ....................... [完成] ✓
6. 撰写数据分析与结果 ................ [完成] ✓
   → 附加 7 张生成的图表

7. 撰写结论与摘要 ..................... [完成] ✓
8. 组装 Word 文档 ..................... [完成] ✓

✓ 论文生成完成！
  [下载 Word 文档]
```

**输出：**
```
output/
├── 中学生学习压力与心理健康的关系研究.docx
└── charts/
    ├── survey_data_corr.png
    ├── survey_data_Q1_dist.png
    └── ... (7 张更多图表)
```

## 目录结构

```
thesis-generator/
├── app.py                          # FastAPI 主应用 + 路由
│   ├── @app.post("/api/generate")  # SSE 生成端点，8 阶段流程
│   └── @app.get("/download/{filename}")  # 文件下载
├── config.py                       # 全局配置（API 密钥、模型、目录）
├── requirements.txt                # Python 依赖清单
├── zeabur.json                     # Zeabur 部署配置
├── .env.example                    # 环境变量模板（复制后重命名为 .env）
├── .gitignore                      # Git 忽略规则
│
├── core/
│   ├── __init__.py
│   ├── file_parser.py              # 文件解析模块
│   │   ├── parse_docx()            # Word 文本提取
│   │   ├── parse_pdf()             # PDF 文本提取
│   │   └── parse_data_file()       # CSV/XLSX 数据读取
│   │
│   ├── data_analyzer.py            # 数据分析模块
│   │   ├── analyze_dataframe()     # 单文件统计 + 图表生成
│   │   └── analyze_all()           # 批量分析
│   │
│   ├── thesis_generator.py         # Claude API 集成核心
│   │   ├── ThesisGenerator.__init__()
│   │   ├── generate_outline()      # 第 3 阶段
│   │   ├── generate_literature()   # 第 4 阶段
│   │   ├── generate_methodology()  # 第 5 阶段
│   │   ├── generate_results()      # 第 6 阶段
│   │   ├── generate_conclusion()   # 第 7 阶段（结论）
│   │   └── generate_abstract()     # 第 7 阶段（摘要）
│   │
│   ├── prompts.py                  # 各阶段的 Claude Prompt 模板
│   │   ├── SYSTEM_PROMPT           # 系统级角色设定
│   │   ├── OUTLINE_PROMPT
│   │   ├── LITERATURE_PROMPT
│   │   ├── METHODOLOGY_PROMPT
│   │   ├── RESULTS_PROMPT
│   │   ├── CONCLUSION_PROMPT
│   │   └── ABSTRACT_PROMPT
│   │
│   └── docx_builder.py             # Word 文档生成模块
│       ├── set_chinese_font()      # 应用中文字体和样式
│       ├── add_cover()             # 生成封面页
│       ├── markdown_to_docx()      # Markdown 转 Word 格式
│       └── build_thesis()          # 主入口，组装完整文档
│
├── static/
│   └── index.html                  # 前端单页应用（HTML/CSS/JS）
│       ├── 文件上传（拖放 + 点击）
│       ├── 表单输入（论文信息）
│       ├── SSE 进度显示（8 个阶段）
│       └── 文件下载链接
│
├── uploads/                        # 临时上传目录（生成后自动删除）
├── output/                         # 输出目录
│   ├── *.docx                      # 生成的论文
│   └── charts/                     # 分析图表（PNG 格式）
│
└── .claude/                        # Claude Code 项目配置（如有）
```

## API 参考

### 生成论文

**请求**
```http
POST /api/generate HTTP/1.1
Content-Type: multipart/form-data

files=<file1>,<file2>...
title=论文标题
subject=学科方向
degree=硕士
author=作者姓名
school=学校名称
```

**响应（Server-Sent Events 流式）**
```
data: {"stage":"parsing","status":"active"}
data: {"stage":"parsing","status":"done"}
data: {"stage":"analyzing","status":"active"}
data: {"stage":"analyzing","status":"done"}
data: {"stage":"outline","status":"active"}
data: {"stage":"outline","status":"done","preview":"## 论文大纲..."}
...
data: {"stage":"docx","status":"done","download_url":"/download/论文标题.docx"}
```

### 下载文档

**请求**
```http
GET /download/论文标题.docx HTTP/1.1
```

**响应**
```http
HTTP/1.1 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="论文标题.docx"

<binary docx data>
```

## 关键设计细节

### 1. Claude API 集成与容错

```python
# thesis_generator.py - 3 次重试机制
def _call(self, system: str, user: str, max_tokens: int = None) -> str:
    for attempt in range(3):  # 最多 3 次重试
        try:
            resp = self.client.messages.create(
                model=config.MODEL,  # claude-sonnet-4-20250514
                max_tokens=max_tokens or config.MAX_TOKENS,  # 8192 tokens
                system=system,       # 角色设定 Prompt
                messages=[{"role": "user", "content": user}],
            )
            return resp.content[0].text
        except Exception as e:
            if attempt == 2:
                raise  # 第 3 次仍失败则抛出异常
            continue  # 否则重试
```

### 2. 数据分析图表嵌入

```python
# data_analyzer.py - 生成学术级图表
fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)  # 相关性热力图
ax.set_title("相关性矩阵")
fig.savefig(chart_path, bbox_inches="tight", dpi=150)  # 150 DPI 高清输出
```

### 3. 中文 Word 文档格式

```python
# docx_builder.py - 字体设置
def set_chinese_font(run, font_name="宋体", size=Pt(12)):
    run.font.name = "Times New Roman"  # 英文字体
    r = run._element
    r.rPr.rFonts.set(qn("w:eastAsia"), font_name)  # 中文字体
    # 标题用黑体 16pt、正文用宋体 12pt、行距 1.5 倍
```

### 4. Server-Sent Events 流式进度

```javascript
// static/index.html - 实时进度显示
const reader = resp.body.getReader();
const decoder = new TextDecoder();
while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const event = JSON.parse(line.slice(6));  // 解析 SSE 消息
    updateProgress(event);  // 更新 UI 进度条
}
```

## 部署

### 本地部署

见 [快速开始](#快速开始) 部分。

### Zeabur 部署（推荐）

项目已包含 `zeabur.json`，一键部署流程：

1. **连接 GitHub 仓库** → Zeabur 自动识别 `zeabur.json`
2. **设置环境变量**
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
3. **自动构建 & 部署** → 获得公网 URL

```bash
# 手动部署命令（如需）
zeabur deploy --token <YOUR_TOKEN>
```

### Docker 部署

```dockerfile
# Dockerfile（如需自建镜像）
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
ENV PORT=8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t thesis-generator .
docker run -e ANTHROPIC_API_KEY=sk-ant-... -p 8000:8000 thesis-generator
```

## 常见问题

### Q: 生成的论文质量如何保证？
**A:** 系统使用 Claude Sonnet 4 模型，并通过 prompts.py 中的详细提示词引导生成学术级内容。建议用户审阅生成结果并进行必要修改。

### Q: 是否支持英文论文？
**A:** 当前为中文优化。英文支持需修改 prompts.py 中的 SYSTEM_PROMPT 和各阶段模板。

### Q: 如何处理 API 超时？
**A:** 内置 3 次重试机制。若仍失败，检查网络连接和 API 配额限制。

### Q: 数据文件大小有限制吗？
**A:** 无硬性限制，但 CSV/XLSX 超过 50MB 时分析速度会明显下降。建议预处理数据。

### Q: 能否自定义生成的论文结构？
**A:** 可以修改 prompts.py 中的章节顺序和内容模板，或在 docx_builder.py 中调整 chapter_order。

## 安全与隐私

- ✅ **无密钥硬编码** — API 密钥仅通过 `.env` 环境变量传递（`.gitignore` 保护）
- ✅ **本地处理** — 所有文件上传和临时处理在本地完成，生成后立即删除（app.py 第 105 行）
- ✅ **仅提示词交互** — 用户数据仅在 Claude API 调用中作为输入，不被存储
- ✅ **开源透明** — 完整代码开放，可自行审计

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8

# 代码格式化
black core/ app.py

# 代码检查
flake8 core/ app.py --max-line-length=100

# 运行测试（如有）
pytest
```

## 许可证

本项目采用 **MIT License** — 详见 [LICENSE](LICENSE) 文件。

## 致谢

- [Anthropic](https://www.anthropic.com/) — Claude API 提供者
- [FastAPI](https://fastapi.tiangolo.com/) — 现代 Python Web 框架
- [python-docx](https://github.com/python-openxml/python-docx) — Word 文档生成
- [Zeabur](https://zeabur.com/) — 云部署平台

## 联系方式

有问题或建议？欢迎提交 [GitHub Issues](https://github.com/yourusername/thesis-generator/issues)。

---

**最后更新**：2025 年 3 月  
**项目状态**：✅ 核心功能完成  
**下一步计划**：英文支持、批量生成、自定义模板、GitHub Actions CI/CD
