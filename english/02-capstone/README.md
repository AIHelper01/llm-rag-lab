<!-- derived-from: ../../02_%E7%BB%BC%E5%90%88%E5%AE%9E%E6%88%98/README.md -->
> English mirror, derived from the Chinese master: [the capstone README](../../02_%E7%BB%BC%E5%90%88%E5%AE%9E%E6%88%98/README.md). The Chinese text is the source of truth; shared assets and corpora are referenced from it.

# LangChain RAG Capstone

This module uses the ZXVMAX-S product manuals as the knowledge base and shows how to build a full RAG system - from document preprocessing to evaluation - with LangChain, vLLM / Xinference model services, and Milvus.

## 1. Lesson files

| File | Role | Coverage |
| --- | --- | --- |
| [01_langchain-baseline.ipynb](./01_langchain-baseline.ipynb) | Getting started and baseline | PDF preprocessing, vector store build, dense retrieval, basic QA chain, multi-turn chat |
| [02_langchain-advanced.ipynb](./02_langchain-advanced.ipynb) | The full advanced case | Four preprocessing routes, query understanding, context optimisation, hybrid retrieval, rerank, Agentic RAG, evaluation |
| [03_ragflow.md](./03_ragflow.md) | Platform extension | Building a knowledge base and RAG workflow with RAGFlow |

Run the baseline first; move on to the advanced notebook once the minimal RAG path makes sense.

## 2. Project layout

```text
02-capstone/                     # this directory (the English mirror; repo root is the bilingual course root)
|-- README.md                    # this file
|-- 01_langchain-baseline.ipynb
|-- 02_langchain-advanced.ipynb
|-- 03_ragflow.md
|-- pdf-cleaning-example.ipynb
`-- (notebooks read ../english/../../02_... corpora through percent-encoded relative links)

../knowledge_path/VMAX-S/        # ZXVMAX-S PDF knowledge base (data)
../knowledge_md/VMAX-S/          # cleaned Markdown corpus (data)
../pyproject.toml / ../uv.lock   # the uv project at the repo root, shared by both language sides
../.env                          # API keys - contains real secrets, keep it private
```

## 3. Requirements

- Python 3.12
- Jupyter Notebook or JupyterLab
- Model services: vLLM (LLM) + Xinference (embedding / reranker)
- Milvus 3.x (client `pymilvus` 3.0.x)

Start the vector store (Docker Compose, Milvus v3.0.3):

```shell
wget https://github.com/milvus-io/milvus/releases/download/v3.0.3/milvus-standalone-docker-compose.yaml -O docker-compose.yaml
docker compose -f docker-compose.yaml up -d
docker compose ps          # milvus-etcd / milvus-minio / milvus-standalone should all be Up (healthy)
```

Optional: the Attu GUI (Attu v3 uses `MILVUS_ADDRESS`, no longer `MILVUS_URL`):

```shell
docker run -d --name attu \
  -p 9092:3000 \
  -e MILVUS_ADDRESS=host.docker.internal:19530 \
  -v attu-data:/data \
  zilliz/attu:v3.0.0
```

Open `http://localhost:9092` in a browser; the published port is whatever you started with, and `docker port attu` confirms it. On Linux also add `--add-host=host.docker.internal:host-gateway`.

Python 3.12 is recommended and **uv is the default** (run from the repo root; both language sides share one `.venv`):

```bash
uv sync
uv run jupyter lab
```

`make sync` / `make lab` are equivalent entry points; `make lab MODULE=capstone` opens this module directly. The two options below are kept only as historical reference.

### Option 1: Conda

```bash
conda create --name env_rag python=3.12 -y

conda activate env_rag

pip install ipykernel

python -m ipykernel install \
--user \
--name=env_pysci \
--display-name "Python 3.12 (env_rag)"
```

### Option 2: uv (recommended)

```bash
uv venv --python=3.12

uv sync

uv add ipykernel

uv run ipython kernel install \
--user \
--name env_rag \
--display-name "Python 3.12 (env_rag)"
```

## 4. Configure the API keys (example)

Create `.env` in the repository root (same key names as section 5, values replaced with your own endpoints and secrets):

```dotenv
vLLM_QWEN_BASE_URL = "http://your-vllm-host/v1"
vLLM_QWEN_API_KEY = "your-vllm-key"
vLLM_QWEN_MODEL_ID = "my_qwen3.8_flash_next"

XINFERENCE_BASE_URL = "http://your-xinference-host"
XINFERENCE_OPENAI_BASE_URL = "http://your-xinference-host/v1"
XINFERENCE_API_KEY = "your-xinference-key"
XINFERENCE_EMBEDDING_MODEL_ID = "my_qwen3_embedding_0.6b"
XINFERENCE_RERANKER_MODEL_ID = "my_qwen3_reranker_0.6b"

MILVUS_URI = "http://localhost:19530"
```

The notebooks live in a subdirectory, so they always look upward for the root `.env` with `find_dotenv()` instead of hard-coding a relative path:

```python
import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
```

For the same reason, data and images inside a notebook are addressed relative to that notebook's own directory, e.g. `../knowledge_path/...` and `../assets/...`.
Never write or print a real API key inside a notebook.

## 5. Models and services

The canonical configuration snippet lives in [model-configuration.ipynb](../../%E6%A8%A1%E5%9E%8B%E7%BB%9F%E4%B8%80%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E.ipynb); the root `.env` holds exactly that configuration:

| Capability | Service | Environment variables | Model |
| --- | --- | --- | --- |
| Large language model | vLLM (OpenAI-compatible `/v1`) | `vLLM_QWEN_BASE_URL` / `vLLM_QWEN_API_KEY` / `vLLM_QWEN_MODEL_ID` | `my_qwen3.8_flash_next` |
| Embedding | Xinference (`/v1/embeddings`) | `XINFERENCE_OPENAI_BASE_URL` / `XINFERENCE_API_KEY` / `XINFERENCE_EMBEDDING_MODEL_ID` | `my_qwen3_embedding_0.6b` (1024-dim) |
| Reranker | Xinference (`/v1/rerank`) | `XINFERENCE_OPENAI_BASE_URL` / `XINFERENCE_API_KEY` / `XINFERENCE_RERANKER_MODEL_ID` | `my_qwen3_reranker_0.6b` |
| Vector database | Milvus standalone (local Docker) | `MILVUS_URI` | `http://localhost:19530` |

Embedding and reranking come from the same Xinference instance: `XINFERENCE_BASE_URL` is the native REST root (for `xinference.client`) and `XINFERENCE_OPENAI_BASE_URL` is its `/v1`-compatible root (for OpenAI-style clients); both share `XINFERENCE_API_KEY`. `make doctor` checks that these keys are present.

The standard LLM configuration:

```python
import os
import httpx
from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import init_chat_model

_ = load_dotenv(find_dotenv())

my_llm = init_chat_model(
    model=os.getenv("vLLM_QWEN_MODEL_ID"),
    model_provider="openai",
    base_url=os.getenv("vLLM_QWEN_BASE_URL"),
    api_key=os.getenv("vLLM_QWEN_API_KEY"),
    http_client=httpx.Client(trust_env=False),
    temperature=0.3,
    max_tokens=4096,
)
```

## 6. Milvus collections

The lessons create or connect to two collections:

| Collection | Vector fields | Purpose |
| --- | --- | --- |
| `ZXVMAXS` | `dense` | single dense semantic retrieval |
| `ZXVMAXS_HYBRID` | `dense`, `sparse` | Milvus-native dense + BM25 hybrid retrieval |

The "teaching hybrid retrieval" in the advanced notebook reads text out of `ZXVMAXS` and builds BM25 in Python memory with `rank-bm25`. That exists to explain fusion; it does not mean `ZXVMAXS` itself carries a sparse field.

## 7. Suggested run order

### Baseline

1. Unified model configuration
2. Data preprocessing
3. Build the `ZXVMAXS` vector store
4. Build the basic retrieval + QA chain
5. Test in-corpus questions, refusal behaviour, and multi-turn chat

### Advanced

1. Compare the four preprocessing routes - simple, optimised, PDF-to-Markdown, Unstructured (`unstructured[pdf]` is optional; the route is skipped when it is not installed)
2. Build `ZXVMAXS` and `ZXVMAXS_HYBRID`
3. Run query normalisation, metadata filters, and retrieval routing
4. Run deduplication, neighbour expansion, and context budgeting
5. Compare weighted, RRF, and dynamic-weight hybrid retrieval
6. Rerank with the Xinference Qwen3 reranker
7. Build the full hybrid QA chain with conversation memory
8. Test Agentic RAG across single-retrieval, hybrid-retrieval, and no-retrieval cases
9. Evaluate the retrieval layer and the generation layer separately

Cells share variables, so on a first run prefer "Restart Kernel and Run All".

## 8. The advanced core path

```text
user question
-> multi-turn question rewrite
-> query normalisation
-> business_type detection
-> dense / hybrid routing
-> metadata filter
-> optional rerank
-> document deduplication
-> neighbour chunk expansion
-> context budgeting
-> LLM answer generation
```

Agentic RAG adds three decision paths:

- conceptual enterprise questions: call the single dense retrieval tool;
- questions naming a product, log, alert, interface, field, or code: call the hybrid retrieval tool;
- greetings, rewrites, and general-capability questions: call no retrieval tool at all.

## 9. Evaluation

The advanced notebook evaluates retrieval and generation separately:

- retrieval metrics: Hit@5, MRR, rank of the first relevant hit, page and section hits;
- generation metrics: faithfulness, relevance, completeness;
- comparison: hybrid-retrieval RAG versus a no-knowledge-base baseline;
- scoring: LLM-as-Judge.

The bundled evaluation set is for teaching. A real project needs at least 50 human-verified questions, reported per business type.

## 10. Troubleshooting

### `.env` not found

Check the Jupyter working directory. From the repository root the path is `.env`; from this module directory it is `../.env`.

```python
from pathlib import Path
print(Path.cwd())
```

### Cannot connect to Milvus

Confirm Milvus is running and check the URI in `connection_args`. The default port is `19530`.

### Embedding / reranker calls fail

Confirm the Xinference service is reachable and the models are actually launched (both models share one API key):

```bash
curl -s -H "Authorization: Bearer $XINFERENCE_API_KEY" "$XINFERENCE_BASE_URL/v1/models" | head -c 400
```

Embeddings use `/v1/embeddings`, reranking uses `/v1/rerank`; the model names must match `XINFERENCE_EMBEDDING_MODEL_ID` and `XINFERENCE_RERANKER_MODEL_ID` exactly.

### LLM calls fail

Confirm vLLM is online and has loaded the target model:

```bash
curl -s -H "Authorization: Bearer $vLLM_QWEN_API_KEY" "$vLLM_QWEN_BASE_URL/models" | head -c 400
```

### Hybrid retrieval silently falls back to dense

Check the agent tool descriptions and the system prompt. Questions naming a product, log, alert, interface, field, code, or asking to "list concrete features" should prefer `hybrid_rag_search`.

### The RAG answer says "I don't know"

Look at the printed sources, page numbers, and sections first to decide whether the failure is in retrieval or in generation:

- the right document was never retrieved: adjust the query, candidate count, metadata filter, or hybrid weights;
- the right document was retrieved but the answer is still missing: check the context budget, the prompt, and the model output limit;
- the question falls outside the five manuals in scope: add the matching document or swap the evaluation question.

### Evaluation is slow

Evaluation calls the LLM many times. Keep `max_tokens` modest, use concise prompts, and disable thinking output when the model supports it. The notebook prints retrieval, generation, scoring, and timing for every question.

## 11. Security notes

- never put API keys in notebooks, READMEs, or logs;
- never commit `.env`;
- if a key ever appeared in notebook output or version history, revoke and reissue it immediately;
- in production, inject credentials from a secret manager and restrict network access to Milvus, vLLM, Xinference, and similar services.
