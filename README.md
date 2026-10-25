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
| 02 Capstone | [02-capstone/README.md](english/02-capstone/README.md) | Baseline and advanced notebooks, RAGFlow platform | Done |
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

`make` targets (macOS / Linux): `make sync`, `make lab`, `make run`, `make outputs`, `make check`, `make doctor`.

`requirement.txt` is the retired Conda manifest, kept only for reference; new environments use `uv sync`.

### 2.1 Expected outputs in the masters

Every master code cell that produces output is followed by an "expected output" markdown cell: text is quoted verbatim from a real run (truncated at 3000 characters with the elision stated inside the block), machine-specific absolute paths are folded to `...`, and image output is exported to `assets/` and referenced by relative path. Nothing is hand-written, so the run stays visible after **Kernel -> Clear All Outputs**.

Committed masters **ship without native cell outputs** (they carry machine-specific venv and ipykernel temp paths); run `make run` locally to reproduce them. Without executed output the embed script skips a master instead of wiping the expected-output blocks it already has.

Refresh it from the repository root (execute first, then embed):

```bash
make run        # = ~/env_rag_uv/.venv/bin/python scripts/execute_notebooks.py
make outputs    # = ~/env_rag_uv/.venv/bin/python scripts/embed_expected_outputs.py
```

- Milvus (`localhost:19530`), vLLM and Xinference must be reachable. The two capstone notebooks rebuild the `ZXVMAXS` / `ZXVMAXS_HYBRID` collections with `drop_old=True`. All four masters take about 12 minutes (measured 2026-10-25: model configuration 11.7 s, PDF cleaning example 36.8 s, baseline 277.7 s, advanced 381.1 s - the advanced one is dominated by remote Agentic RAG and LLM-as-Judge calls).
- Generated cells carry the `course-expected-output` tag and the script is idempotent: tagged cells are deleted and rebuilt, and the cell id stays stable while the content is unchanged.
- **The English mirrors deliberately carry no expected-output blocks**: the quoted output is itself Chinese corpus text, which would break the no-CJK rule for `english/`. The mirrors keep the "run it to see the output" note instead, and `scripts/check_parity.py` skips tagged master cells when it compares cell counts.
- LLM wording changes on every run (so do the hit page numbers). A block is one real sample used to compare structure and magnitude, not a byte-for-byte assertion.
- The PDF cleaning example writes only to `tmp/pdf-cleaning-demo/VMAX-S` (git-ignored). `knowledge_md/` is the corpus the two capstone notebooks read, so letting the example overwrite it silently changes their retrieval results and their recorded runs; before refreshing a run make sure `git status --short knowledge_md` is clean.
- `knowledge_md/` itself is generated by the Markdown preprocessing section of the advanced capstone notebook, so after a rerun `git status --short knowledge_md` must still be empty; if it is not, that edit changes every downstream retrieval result and must be reviewed before committing.
- Unstructured uses spaCy sentence segmentation even with `strategy="fast"`. With `preshed==3.0.14` the `spacy.load()` call raises `OverflowError` and Unstructured swallows it, which shows up as an element count of `0` everywhere; the `pdf` extra pins `preshed<3.0.14`.
- The Unstructured route in the PDF cleaning example needs the heavy parsing stack: `cd ~/env_rag_uv && uv sync --extra pdf` (pulls torch / timm / transformers / opencv). Without it that cell honestly reports `ModuleNotFoundError`; the PyMuPDF route is unaffected.

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

Create `.env` in the repository root (it is ignored by `.gitignore`; copy the template):

```bash
cp .env.example .env    # then fill in your own endpoints and keys
```

```dotenv
vLLM_QWEN_BASE_URL = "http://<your-host>:3791/v1"
XINFERENCE_OPENAI_BASE_URL = "http://<your-host>:3797/v1"
XINFERENCE_API_KEY = "<your-xinference-key>"
MILVUS_URI = "http://localhost:19530"
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
| Vector store | Milvus standalone (local Docker) | `MILVUS_URI` | `http://localhost:19530` |

Embedding and the reranker share one Xinference instance: `XINFERENCE_BASE_URL` is the native REST root (for `xinference.client`), `XINFERENCE_OPENAI_BASE_URL` is its `/v1` compatibility root, and both use `XINFERENCE_API_KEY`. `make doctor` checks that these keys exist. The vector store is a Milvus standalone container on your machine (v3.0.3, started with Docker Compose — see `02_capstone/README.md` for the commands; the Attu dashboard port follows the run command, `http://localhost:9092` in the standard one, and `docker port attu` shows the live mapping), with the `pymilvus` client pinned to 3.0.x to match the server. For the recall-then-rerank pattern in LangChain, see the master notebook `model-configuration` (Chinese): LangChain has no native Xinference rerank integration, so `/v1/rerank` is wrapped in a custom `BaseDocumentCompressor`.

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
- **Heads up**: `.env` was committed to this repository in the past; it is now untracked with `git rm --cached .env` and listed in `.gitignore`. Keys that entered history still need rotating. `make doctor` only reports key names, never values.
- In production, inject credentials from a secret manager and restrict network access to Milvus, vLLM, Xinference, and similar services.
