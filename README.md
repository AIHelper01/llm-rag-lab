# LangChain RAG 综合实战

本目录以 ZXVMAX-S 产品说明书为知识库，演示如何使用 LangChain、Ollama 和 Milvus 构建一套从文档预处理到效果评估的 RAG 系统。

## 1. 教程文件

| 文件 | 定位 | 主要内容 |
| --- | --- | --- |
| [01_综合实战-LangChain-基础版.ipynb](./01_综合实战-LangChain-基础版.ipynb) | 入门与基线 | PDF 预处理、向量库构建、Dense 检索、基础问答链和多轮对话 |
| [02_综合实战-LangChain-进阶版.ipynb](./02_综合实战-LangChain-进阶版.ipynb) | 完整进阶案例 | 四种预处理、查询理解、上下文优化、混合检索、Rerank、Agentic RAG 和效果评估 |
| [03_综合实战-RAGFlow.md](./03_综合实战-RAGFlow.md) | 平台化拓展 | 使用 RAGFlow 搭建知识库与 RAG 工作流 |

推荐先运行基础版，理解最小 RAG 链路后再学习进阶版。

## 2. 项目结构

```text
llm-rag/
├── 00_夯实基础/                 # RAG 原理与分主题教程
├── 02_综合实战/
│   ├── 01_综合实战-LangChain-基础版.ipynb
│   ├── 02_综合实战-LangChain-进阶版.ipynb
│   ├── 03_综合实战-RAGFlow.md
│   └── README.md
├── knowledge_path/VMAX-S/      # ZXVMAX-S PDF 知识库
├── requirement.txt
├── pyproject.toml
└── .env                        # API Key，不应提交到版本库
```

## 3. 环境要求

- Python 3.12
- Jupyter Notebook 或 JupyterLab
- vLLM/Ollama Embedding/Reranker 服务
- Milvus 2.6.x

推荐使用 Python 3.12，并为项目创建独立虚拟环境。以下两种方式任选其一。

```bash
git clone https://gitee.com/coderwillyan/llm-rag-lab.git
cd env_rag
```

### 方式一：Conda

```bash
conda create --name env_rag python=3.12 -y

conda activate env_rag

pip install ipykernel

python -m ipykernel install \
--user \
--name=env_pysci \
--display-name "Python 3.12 (env_rag)"
```

### 方式二：uv （推荐）

```bash
uv venv --python=3.12

uv sync

uv add ipykernel

uv run ipython kernel install \
--user \
--name env_rag \
--display-name "Python 3.12 (env_rag)"
```

## 4. 配置 API Key (示例)

在仓库根目录创建 `.env`：

```dotenv
SILICONFLOW_API_KEY=你的_SiliconFlow_API_Key
DEEPSEEK_API_KEY=你的_DeepSeek_API_Key
```

Notebook 位于 `02_综合实战` 子目录，因此配置代码使用：

```python
env_path = "../.env"
load_dotenv(env_path)
```

不要在 Notebook 中直接写入或输出真实 API Key。

## 5. 模型与服务

默认配置如下，请按实际环境修改地址：

| 能力 | 默认配置 |
| --- | --- |
| 大语言模型 | 本地墨模型/SiliconFlow/DeepSeek |
| Embedding | Ollama `qwen3-embedding:0.6b` |
| Reranker | Ollama `dengcao/Qwen3-Reranker-0.6B:Q8_0` |
| Milvus | `http://xxx:19530` |
| Ollama | `http://xxx:11434` |

推荐使用本地QWEN模型：

```python
import os
import httpx
from dotenv import load_dotenv,find_dotenv
from langchain.chat_models import init_chat_model

# ── 1. 大语言模型配置 ─────────────────────────────
# env_path = "../.env"
_ = load_dotenv(find_dotenv())

my_llm = init_chat_model(
    model=os.getenv("vLLM_QWEN122B_MODEL_ID"),
    model_provider="openai",
    base_url=os.getenv("vLLM_QWEN122B_BASE_URL"),
    api_key=os.getenv("vLLM_QWEN122B_API_KEY"),
    http_client=httpx.Client(trust_env=False),
    temperature=0.3,
    max_tokens=10000,
)

```

## 6. Milvus Collection

教程会创建或连接两个 collection：

| Collection | 向量字段 | 用途 |
| --- | --- | --- |
| `ZXVMAXS` | `dense` | 单一语义向量检索 |
| `ZXVMAXS_HYBRID` | `dense`、`sparse` | Milvus 原生 Dense + BM25 混合检索 |

进阶版中的“教学版混合检索”会从 `ZXVMAXS` 读取文本，并在 Python 内存中使用 `rank-bm25` 构建 BM25。这是为了讲解融合原理，不代表 `ZXVMAXS` 自身包含 sparse 字段。

## 7. 建议运行顺序

### 基础版

1. 统一模型配置
2. 数据预处理
3. 构建 `ZXVMAXS` 向量库
4. 构建基础检索问答链
5. 测试知识库内问题、拒答能力和多轮对话

### 进阶版

1. 比较简单、优化、PDF 转 Markdown、Unstructured 四种预处理路线
2. 构建 `ZXVMAXS` 与 `ZXVMAXS_HYBRID`
3. 执行查询规范化、Metadata Filter 和检索路由
4. 执行去重、邻接扩展和上下文预算控制
5. 对比 Weighted、RRF 和动态权重混合检索
6. 使用本地 Qwen3 Reranker 精排
7. 构建带记忆的完整混合检索问答链
8. 测试 Agentic RAG 的单一检索、混合检索和不检索场景
9. 分别评估检索层与生成层效果

Notebook 单元之间存在变量依赖，首次运行时建议使用“Restart Kernel and Run All”。

## 8. 进阶版核心链路

```text
用户问题
→ 多轮问题改写
→ 查询规范化
→ business_type 识别
→ Dense / Hybrid 路由
→ Metadata Filter
→ 可选 Rerank
→ 文档去重
→ 邻接块扩展
→ 上下文预算控制
→ LLM 生成答案
```

Agentic RAG 进一步提供三种决策路径：

- 语义解释类企业问题：调用单一 Dense 检索；
- 产品名、日志、告警、接口、字段或编号类问题：调用混合检索；
- 问候、改写和通用能力问题：不调用知识库检索工具。

## 9. 效果评估

进阶版将检索层和生成层分开评估：

- 检索指标：Hit@5、MRR、首个相关结果排名、页码和章节命中；
- 生成指标：忠实度、相关性、完整性；
- 对照方案：混合检索 RAG 与无知识库基线；
- 评分方式：LLM-as-Judge。

当前评测集用于教学演示。真实项目应准备至少 50 条经过人工校验的问题，并按业务类型分别统计指标。

## 10. 常见问题

### 找不到 `.env`

确认 Jupyter 的当前工作目录。如果从仓库根目录运行，路径应为 `.env`；如果从 `02_综合实战` 目录运行，路径应为 `../.env`。

```python
from pathlib import Path
print(Path.cwd())
```

### Milvus 连接失败

确认 Milvus 已启动，并检查 `connection_args` 中的 URI。默认端口为 `19530`。

### Ollama 连接失败

确认 Ollama 服务可访问，并检查模型是否存在：

```bash
ollama list
```

### 混合检索误走单一检索

检查 Agent 工具描述和系统提示词。包含产品名、日志、告警、接口、字段、编号或“列举具体功能”的问题应优先调用 `hybrid_rag_search`。

### RAG 回答“我不知道”

先查看打印出的来源、页码和章节，判断问题来自检索还是生成：

- 没有召回正确文档：调整 query、候选数量、Metadata Filter 或混合权重；
- 正确文档已召回但答案缺失：检查上下文预算、Prompt 和模型输出限制；
- 问题不属于当前五份产品说明书：补充对应文档或更换评测题。

### 评估运行较慢

评估会多次调用 LLM。建议限制 `max_tokens`，使用简洁 Prompt，并在支持的模型中关闭思考输出。Notebook 已逐题打印检索、生成、评分和耗时信息。

## 11. 安全提醒

- 不要把 API Key 写进 Notebook、README 或日志；
- 不要提交 `.env`；
- 如果密钥曾出现在 Notebook 输出或版本记录中，应立即撤销并重新生成；
- 生产环境应通过密钥管理服务注入凭据，并限制 Milvus、Ollama 等服务的网络访问范围。

