# LLM RAG Lab

[Chinese course (master)](README.zh-CN.md) · English mirror

A hands-on RAG course built on the ZXVMAX-S product manuals as the knowledge base: data preparation, index building, retrieval optimisation, generation, and end-to-end evaluation with LangChain, Milvus, and local or hosted LLMs.

The Chinese lessons at the repository root are the **masters**; every lesson under `english/` is derived from its Chinese twin. Chinese is the source of truth, English is the mirror, one lesson per lesson. Rules and tooling: [AGENTS.md](AGENTS.md).

## 1. Course map

| Module | English entry | Content | Mirror status |
| --- | --- | --- | --- |
| 00 Foundations - C01 Unlock RAG | [01_rag-overview.md](english/00-foundations/C01-unlock-rag/01_rag-overview.md) | What RAG is, its evolution, when to use it, how to start | Done |
| 00 Foundations - C02 Data preparation | pending | Document loading and chunking | Pending |
| 00 Foundations - C03 Index building | pending | Embeddings, multimodal embeddings, vector stores, index tuning | Pending |
| 00 Foundations - C04 Retrieval optimisation | pending | Hybrid retrieval, query construction and rewriting, text2sql | Pending |
| 00 Foundations - C05 Generation | pending | Prompt templates and structured output | Pending |
| 00 Foundations - C06 Evaluation | pending | Retrieval and generation metrics, evaluation tools | Pending |
| 02 Capstone | pending | Baseline and advanced notebooks, RAGFlow platform | Pending |
| 03 Paradigm extensions | pending | Personal AI knowledge base | Pending |

Suggested order: C01 to C06, then the capstone (baseline notebook first, advanced second), and finally the paradigm extensions.

## 2. Quick start (uv by default)

One environment for the whole course: the **uv project lives in the repository root** (`pyproject.toml` + `uv.lock` + `.python-version`), and both language editions share the same `.venv`.

```bash
git clone https://gitee.com/coderwillyan/llm-rag-lab.git
cd llm-rag-lab
uv sync                       # installs all dependencies (first run may download Python 3.12)
uv run jupyter lab            # start JupyterLab
```

The classroom kernel follows the same naming as `~/env_agent_uv` and `~/env_dl_uv`: `~/env_rag_uv` is a standalone uv project with its own `.venv` and a Jupyter kernel.

```bash
cd ~/env_rag_uv && uv sync
.venv/bin/python -m ipykernel install --user --name env_rag_uv --display-name "Python (env_rag_uv)"
uv run --no-sync jupyter lab ../workspace/llm-rag-lab     # then pick the env_rag_uv kernel
```

To register a kernel for the repository `.venv` instead (use `env_rag_uv` for the classroom setup):

```bash
uv run python -m ipykernel install --user --name env_rag --display-name "Python 3.12 (llm-rag-lab)"
```

Sync and open one module in a single command:

```bash
./start-notebooks.sh --language en --module foundations   # macOS / Linux
./start-notebooks.sh --language en --module capstone
```

Windows PowerShell:

```powershell
.\start-notebooks.ps1 -Language en -Module foundations
.\start-notebooks.ps1 -Language en -Module capstone
```

Modules: `foundations` (00), `capstone` (02), `frontiers` (03).

`make` targets (macOS / Linux): `make sync`, `make lab`, `make check`, `make doctor`.

`requirement.txt` is the retired Conda manifest, kept only for reference; new environments use `uv sync`.

## 3. Bilingual rules

- The Chinese masters stay at the repository root; the English mirrors live in `english/` and are derived from them, never the other way round.
- No CJK characters anywhere under `english/`, file names and notebook outputs included; `scripts/check_parity.py` enforces it.
- The masters keep their original Chinese directory and file names (a deliberate, documented deviation - see the "Recorded deviations" section of [AGENTS.md](AGENTS.md)). The mirror uses ASCII names and `scripts/course_map.py` is the single source of truth for the pairing.
- Images and corpora are not duplicated: the mirror points at the master assets through percent-encoded relative links.

Translation progress:

```bash
python3 scripts/check_parity.py
```

## 4. API keys

Create `.env` in the repository root (this file is unfortunately tracked in Git for historical reasons, see section 7):

```dotenv
SILICONFLOW_API_KEY=your_siliconflow_key
DEEPSEEK_API_KEY=your_deepseek_key
```

Notebooks running from the capstone directory read `../.env`; from the repository root they read `.env`. Check where you actually are:

```python
from pathlib import Path
print(Path.cwd())
```

## 5. Models and services

The unified configuration pattern lives in the master notebook `model-configuration` (Chinese), and `.env` holds exactly this stack:

| Capability | Service | Environment variables | Model |
| --- | --- | --- | --- |
| LLM | vLLM (OpenAI-compatible `/v1`) | `vLLM_QWEN_BASE_URL` / `vLLM_QWEN_API_KEY` / `vLLM_QWEN_MODEL_ID` | `my_qwen3.8_flash_next` |
| Embedding | Xinference (`/v1/embeddings`) | `XINFERENCE_OPENAI_BASE_URL` / `XINFERENCE_API_KEY` / `XINFERENCE_EMBEDDING_MODEL_ID` | `my_qwen3_embedding_0.6b` (1024-dim) |
| Reranker | Xinference (`/v1/rerank`) | `XINFERENCE_OPENAI_BASE_URL` / `XINFERENCE_API_KEY` / `XINFERENCE_RERANKER_MODEL_ID` | `my_qwen3_reranker_0.6b` |
| Vector store | Milvus standalone | `connection_args` inside the notebooks | `http://xxx:19530` |

Embedding and the reranker share one Xinference instance: `XINFERENCE_BASE_URL` is the native REST root (for `xinference.client`), `XINFERENCE_OPENAI_BASE_URL` is its `/v1` compatibility root, and both use `XINFERENCE_API_KEY`. `make doctor` checks that these keys exist.

## 6. Layout

```text
llm-rag-lab/
├── three Chinese module directories    # the masters: 00_ foundations, 02_ capstone, 03_ paradigm extensions
│                                       # Chinese names are kept on purpose; run
│                                       #   python3 scripts/course_map.py --modules
│                                       # for the exact paths on both sides
├── english/                # English mirror, ASCII names, one lesson per lesson
├── scripts/                # course_map.py (pairing table), check_parity.py (bilingual checks)
├── knowledge_md/           # cleaned markdown corpus (data, not paired)
├── knowledge_path/         # ZXVMAX-S PDF knowledge base (data)
├── start-notebooks.sh / .ps1
├── Makefile
└── pyproject.toml / uv.lock / .python-version
```

## 7. Security notes

- Never put API keys in notebooks, the README, or logs.
- **Heads up**: `.env` was committed to this repository in the past, which contradicts the rule above. Rotate any key that entered history, and once collaborators are informed and have backups, stop tracking it with `git rm --cached .env`.
- In production, inject credentials from a secret manager and restrict network access to Milvus, Ollama, and similar services.
