# LLM RAG 实战教程（中文课程）

中文课程（母本） · [English mirror](README.md)

以 ZXVMAX-S 产品说明书为知识库，用 LangChain + Milvus + 本地/云端 LLM 走完「数据准备 → 索引构建 → 检索优化 → 生成集成 → 系统评估」的完整 RAG 链路。

**根目录的中文课件是母本**，`english/` 下的英文课件由母本逐篇派生：中文为标准，英文为镜像，一课一对应。派生与校验规则见 [AGENTS.md](AGENTS.md)。

## 1. 课程地图

| 模块 | 中文入口 | 内容 | 英文镜像 |
| --- | --- | --- | --- |
| 00 夯实基础 · C01 解锁 RAG | [01_RAG简介.md](<00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C01_%E8%A7%A3%E9%94%81RAG/01_RAG%E7%AE%80%E4%BB%8B.md>) | RAG 定义、演进、选型与上手路线 | [01_rag-overview.md](english/00-foundations/C01-unlock-rag/01_rag-overview.md) |
| 00 夯实基础 · C02 数据准备 | [01_数据加载.md](<00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C02_%E6%95%B0%E6%8D%AE%E5%87%86%E5%A4%87/01_%E6%95%B0%E6%8D%AE%E5%8A%A0%E8%BD%BD.md>) | 多源文档加载与切块 | 待翻译 |
| 00 夯实基础 · C03 索引构建 | [01_向量嵌入.md](<00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C03_%E7%B4%A2%E5%BC%95%E6%9E%84%E5%BB%BA/01_%E5%90%91%E9%87%8F%E5%B5%8C%E5%85%A5.md>) | 嵌入、多模态嵌入、向量数据库与索引优化 | 待翻译 |
| 00 夯实基础 · C04 检索优化 | [01_混合检索.md](<00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C04_%E6%A3%80%E7%B4%A2%E4%BC%98%E5%8C%96/01_%E6%B7%B7%E5%90%88%E6%A3%80%E7%B4%A2.md>) | 混合检索、查询构建与重构、text2sql | 待翻译 |
| 00 夯实基础 · C05 生成集成 | [01_格式化生成.md](<00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C05_%E7%94%9F%E6%88%90%E9%9B%86%E6%88%90/01_%E6%A0%BC%E5%BC%8F%E5%8C%96%E7%94%9F%E6%88%90.md>) | Prompt 模板与结构化输出 | 待翻译 |
| 00 夯实基础 · C06 RAG 系统评估 | [01_评估介绍.md](<00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C06_RAG%E7%B3%BB%E7%BB%9F%E8%AF%84%E4%BC%B0/01_%E8%AF%84%E4%BC%B0%E4%BB%8B%E7%BB%8D.md>) | 检索层与生成层评估、评估工具 | 待翻译 |
| 02 综合实战 | [README.md](<02_%E7%BB%BC%E5%90%88%E5%AE%9E%E6%88%98/README.md>) | 基础版 / 进阶版 Notebook、RAGFlow 平台化 | 待翻译 |
| 03 范式拓展 | [01_Karpathy式AI知识库搭建指南.md](<03_%E8%8C%83%E5%BC%8F%E6%8B%93%E5%B1%95/01_Karpathy%E5%BC%8FAI%E7%9F%A5%E8%AF%86%E5%BA%93%E6%90%AD%E5%BB%BA%E6%8C%87%E5%8D%97.md>) | 个人 AI 知识库范式 | 待翻译 |

学习顺序建议：C01 → C06 逐章打基础，再进 `02_综合实战`（先基础版、后进阶版），最后看 `03_范式拓展`。

## 2. 快速开始（默认用 uv）

全课只有一个环境：**uv 工程就在仓库根**（`pyproject.toml` + `uv.lock` + `.python-version`），中英两侧共用同一个 `.venv`。

```bash
git clone https://gitee.com/coderwillyan/llm-rag-lab.git
cd llm-rag-lab
uv sync                       # 装齐依赖（首次会下载 Python 3.12 与依赖包）
uv run jupyter lab            # 启动 JupyterLab
```

注册内核（Notebook 需要选择内核时）：

```bash
uv run python -m ipykernel install --user --name env_rag --display-name "Python 3.12 (llm-rag-lab)"
```

一条命令同步环境并打开指定模块：

```bash
./start-notebooks.sh --language zh-CN --module foundations   # macOS / Linux
./start-notebooks.sh --language en    --module capstone
```

Windows PowerShell：

```powershell
.\start-notebooks.ps1 -Language zh-CN -Module foundations
.\start-notebooks.ps1 -Language en -Module capstone
```

`--module` / `-Module` 取值：`foundations`（00 夯实基础）、`capstone`（02 综合实战）、`frontiers`（03 范式拓展）。

`make` 入口（macOS / Linux）：

```bash
make sync     # uv sync
make lab      # uv run jupyter lab
make check    # 中英对齐与英文侧语言检查
make doctor   # 环境体检：uv、Python、.env、依赖导入
```

`requirement.txt` 是历史 Conda 路线的遗留清单，保留仅供对照，新环境一律走 `uv sync`。

## 3. 中英双语约定

- 中文在根目录，是**母本**；英文在 `english/`，是**镜像**，一律由母本派生，不反向修改中文。
- `english/` 下不得出现中日韩文字（含文件名与 Notebook 输出），由 `scripts/check_parity.py` 强制。
- 中文母本保留原有中文目录与文件名（**有意偏离**，见 [AGENTS.md](AGENTS.md) 的「已记录的偏离」），英文侧使用 ASCII 名字，两侧对应关系由 `scripts/course_map.py` 单一维护。
- 图片与语料共用母本目录，英文侧用百分号编码的相对链接引用，不复制副本。

翻译进度与逐篇状态：

```bash
python3 scripts/check_parity.py
```

## 4. 配置密钥

在仓库根目录准备 `.env`（该文件当前已被 Git 跟踪，属于历史遗留，见第 7 节安全提醒）：

```dotenv
SILICONFLOW_API_KEY=你的_SiliconFlow_API_Key
DEEPSEEK_API_KEY=你的_DeepSeek_API_Key
```

Notebook 若在 `02_综合实战` 子目录下运行，读取路径为 `../.env`；从仓库根运行则为 `.env`。用 `uv run jupyter lab` / 启动脚本时工作目录即模块目录，可用下列代码确认：

```python
from pathlib import Path
print(Path.cwd())
```

## 5. 模型与服务

统一配置写法见 [模型统一配置说明.ipynb](<%E6%A8%A1%E5%9E%8B%E7%BB%9F%E4%B8%80%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E.ipynb>)，默认值如下，请按实际环境修改：

| 能力 | 默认配置 |
| --- | --- |
| 大语言模型 | 本地 Qwen / SiliconFlow / DeepSeek |
| Embedding | Ollama `qwen3-embedding:0.6b` |
| Reranker | Ollama `dengcao/Qwen3-Reranker-0.6B:Q8_0` |
| Milvus | `http://xxx:19530` |
| Ollama | `http://xxx:11434` |

综合实战的 Collection、运行顺序、评测指标与常见问题，见 [02_综合实战/README.md](<02_%E7%BB%BC%E5%90%88%E5%AE%9E%E6%88%98/README.md>)。

## 6. 目录结构

```text
llm-rag-lab/
├── 00_夯实基础/            # C01–C06 分主题教程（中文母本，含 code/ 与 images/）
├── 02_综合实战/            # 基础版/进阶版 Notebook + RAGFlow（中文母本）
├── 03_范式拓展/            # 范式拓展（中文母本）
├── english/                # 英文镜像（ASCII 目录名，一课一对应）
├── scripts/                # course_map.py（映射表）、check_parity.py（双语校验）
├── knowledge_md/           # 已清洗的 Markdown 语料（数据，不参与双语配对）
├── knowledge_path/         # ZXVMAX-S PDF 知识库（数据）
├── assets/                 # 通用图片资源
├── start-notebooks.sh / .ps1
├── Makefile
├── pyproject.toml / uv.lock / .python-version
└── requirement.txt         # 遗留清单，仅作对照
```

## 7. 安全提醒

- 不要把 API Key 写进 Notebook、README 或日志；提交前检查 `.env` 未被加入差异。
- **注意**：本仓库历史上把 `.env` 提交进了版本库（README 自身的约定与之冲突）。请轮换曾入库的密钥，并在确认后执行 `git rm --cached .env` 停止跟踪（该操作会让他人拉取时删除本地 `.env`，请先通知协作者并备份）。
- 生产环境通过密钥管理服务注入凭据，并限制 Milvus、Ollama 等服务的网络访问范围。
