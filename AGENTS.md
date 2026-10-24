# llm-rag-lab 仓库约定

面向在本仓库工作的编码代理与协作者。目标：一套 RAG 课程，中英两个版本，一个 uv 环境。

## 1. 双语原则（最高优先级）

- **中文是母本（master）**，位于仓库根目录（`00_夯实基础/`、`02_综合实战/`、`03_范式拓展/`、根级 notebook）。
- **英文是镜像（mirror）**，位于 `english/`，只能由中文母本**单向派生**。任何内容修正先改中文，再同步英文。
- 语言规则单向：`english/` 下凡学习者会读或写的地方必须纯英文（正文、标题、图表文案、Notebook 输出、文件名）。中文母本可自由中英混排。
- 一课一对应：母本每一篇课程文档都必须能在映射表中找到英文对应项，**已翻译**的必须真实存在，**未翻译**的必须登记原因。
- 根目录 `README.md` 是英文入口，`README.zh-CN.md` 是中文入口。

## 2. 已记录的偏离（不要"顺手修正"）

deep-learning-lab 的同类课程要求**两侧目录与文件名都是 ASCII**。本仓库**有意不重命名中文母本**：

- 原因：中文目录名已被外部教程、链接与讲义引用，重命名属于破坏性改动，收益只是路径整洁。
- 结果：中文母本保留中文目录与文件名；`english/` 侧全部使用 ASCII 名字；两侧对应关系由 `scripts/course_map.py` 里的显式映射表维护，**不靠同名推断**。
- 英文侧引用母本资源（图片、语料、母本正文）时，使用**百分号编码的相对链接**，这样文件内容仍是纯 ASCII，链接又能解析。

## 3. 映射与校验

- `scripts/course_map.py`：母本 ↔ 镜像的**唯一**映射来源，另含 `NON_COURSE`（不翻译、不配对的内容及原因）。
- `scripts/check_parity.py`：在仓库根执行 `python3 scripts/check_parity.py`，检查
  1. `english/` 下目录名与文件名为 ASCII；
  2. `english/` 下所有文本（`.md` / `.ipynb` / `.py` / `.sh` / `.ps1` / `.json`）不含中日韩字符；
  3. 母本每篇课程文档都在映射表内，`english/` 每篇文档都能反查到母本（无孤儿）；
  4. 已翻译镜像带 `<!-- derived-from: <百分号编码路径> -->`，且解码后目标存在；
  5. 已配对的 Markdown 标题数与图片数一致、Notebook 单元格数一致；
  6. 待译项必须带原因。
- 校验必须**全绿**才能提交。翻译了新的一篇，就把映射表里的状态从 `pending` 改成英文路径，不要新增绕过开关。

## 4. 环境：默认 uv

- **一个 uv 工程：仓库根**（`pyproject.toml` + `uv.lock` + `.python-version`）。中英两侧共用根 `.venv`，`uv sync` 一次装齐。
- 默认启动：`uv sync` → `uv run jupyter lab`；或 `./start-notebooks.sh --language zh-CN|en --module foundations|capstone|frontiers`（Windows 用 `start-notebooks.ps1 -Language ... -Module ...`）。
- `requirement.txt` 是 Conda 路线的遗留清单，**只读对照**，不要往里加新依赖。
- 文档中的命令必须注明工作目录；除特别说明外都在仓库根执行。

## 5. 数据与第三方内容

- `knowledge_md/`、`knowledge_path/`：知识库语料，属**数据**，不翻译、不改名、不删除。
- `assets/`、各模块 `images/`：图片资源，中英共用。
- `00_夯实基础/C03_索引构建/code/visual_bge/`：vendored 第三方库，原样保留，不翻译、不重构。
- `00_夯实基础/C01_解锁RAG/data/`：示例语料，不翻译。
- `.ipynb_checkpoints/`、`.venv/`、`__pycache__/` 属生成物，不配对、不提交。
- `.env` 含真实密钥且历史上已被 Git 跟踪：**不要读取后输出内容、不要提交新密钥、不要扩大跟踪范围**。若要停止跟踪，先通知协作者并确认（`git rm --cached .env` 会在他人拉取时删除其本地文件），并轮换入库密钥。

## 6. 翻译一篇课件的标准流程

1. `git status --short` 确认工作区，保留他人/既有改动。
2. 在 `scripts/course_map.py` 找到母本条目，确认其英文路径与目录（不存在就创建目录）。
3. 新建英文文件，首行放 provenance：
   `<!-- derived-from: <百分号编码的相对路径> -->`，紧随一行英文提示，链接文本用英文。
4. 逐段翻译，保留原有标题层级、表格、脚注与公式；图片链接改为指向母本 `images/` 的百分号编码相对路径。
5. 全文自查无 CJK 字符（含图注、表格、alt 文本）。
6. 把映射表状态改为英文路径，跑 `python3 scripts/check_parity.py`，同步 `README.md` / `english/README.md` 的课程地图与进度。

## 7. 提交与推送

- 只提交与任务相关的文件；提交信息用简洁祈使句。
- 上游是 Gitee 镜像仓库，**未经用户明确同意不要 `git push`**。
