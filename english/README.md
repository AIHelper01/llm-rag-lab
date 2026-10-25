# LLM RAG Lab - English mirror

English mirror · [Chinese course (master)](../README.zh-CN.md) · [repository README](../README.md)

Every lesson here is derived from a Chinese master lesson at the repository root. Chinese is the source of truth: fix the master first, then update this side. Nothing under `english/` may contain CJK characters, file names and notebook outputs included - `scripts/check_parity.py` enforces it.

## What is available

| Lesson | English | Master | Status |
| --- | --- | --- | --- |
| C01 Unlock RAG - 01 RAG overview | [01_rag-overview.md](00-foundations/C01-unlock-rag/01_rag-overview.md) | lesson 1 of C01 | Translated (reference sample) |
| C01 Unlock RAG - 02 Preparation | pending | lesson 2 of C01 | Pending |
| C01 Unlock RAG - 03 Get started with RAG | pending | lesson 3 of C01 | Pending |
| C02 Data preparation | pending | 2 lessons | Pending |
| C03 Index building | pending | 6 lessons | Pending |
| C04 Retrieval optimisation | pending | 5 lessons | Pending |
| C05 Generation | pending | 1 lesson | Pending |
| C06 Evaluation | pending | 2 lessons | Pending |
| 02 Capstone | [02-capstone/README.md](02-capstone/README.md) | 2 notebooks, 1 PDF-cleaning notebook, 1 RAGFlow chapter | Done |
| 03 Paradigm extensions | pending | 1 chapter | Pending |

Full pairing table and reasons for every gap: `python3 scripts/course_map.py` (run from the repository root). Live check: `python3 scripts/check_parity.py`.

## Running the English edition

The uv project lives in the repository root and both language editions share its `.venv`:

```bash
cd ..                        # the repository root
uv sync
uv run jupyter lab           # or ./start-notebooks.ps1 -Language en -Module capstone on Windows
```

The Chinese course directory names stay Chinese on purpose (documented deviation, see `AGENTS.md`); this side uses ASCII names, and `scripts/course_map.py` is the single source of truth for the pairing. Images and corpora are shared with the masters through percent-encoded relative links, so nothing is duplicated.

## Translating a lesson

1. Find the master entry in `scripts/course_map.py` and note the target path here.
2. Create the file with the provenance comment on the first line: `<!-- derived-from: <percent-encoded relative path> -->`.
3. Translate section by section, keeping heading levels, tables, footnotes, and the same number of images.
4. Point image links at the master `images/` directory using percent-encoded relative paths.
5. Check for stray CJK characters, then run `python3 scripts/check_parity.py` and update the tables in this file and `README.md`.
