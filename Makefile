# llm-rag-lab 一键入口（macOS / Linux）。Windows 用 start-notebooks.ps1。
.PHONY: help sync env env-pdf kernel lab lab-en run outputs check doctor map

help:
	@echo "make sync     - uv sync，装齐中英两侧共用依赖"
	@echo "make env      - 同步课堂内核环境 ~/env_rag_uv 并注册内核 env_rag_uv"
	@echo "make env-pdf  - 给课堂内核补 PDF 课件的 Unstructured 解析栈（约 1.5 GB）"
	@echo "make kernel   - 给仓库 .venv 注册 Jupyter 内核 env_rag（可选）"
	@echo "make lab      - 打开中文模块（默认 foundations）：make lab MODULE=capstone"
	@echo "make lab-en   - 打开英文镜像：make lab-en MODULE=capstone"
	@echo "make run      - 用 env_rag_uv 内核真实执行课件（写回 outputs）"
	@echo "make outputs  - 把实跑输出内嵌成 **预期输出：** 块（先 make run）"
	@echo "make check    - 中英对齐与英文侧纯英文检查"
	@echo "make doctor   - 环境体检：uv / Python / .env / 关键依赖"
	@echo "make map      - 打印中英映射表与翻译进度"

MODULE ?= foundations
# 课件执行与内嵌都使用课堂内核环境，避免污染仓库 .venv
PY ?= $(HOME)/env_rag_uv/.venv/bin/python

sync:
	uv sync --locked

ENV_DIR ?= $(HOME)/env_rag_uv

env:
	cd $(ENV_DIR) && uv sync
	cd $(ENV_DIR) && .venv/bin/python -m ipykernel install --user --name env_rag_uv --display-name "Python (env_rag_uv)"
	@echo "内核 env_rag_uv 就绪：make doctor 可用 $(ENV_DIR)/.venv/bin/python 复核"
	@echo "PDF 课件另需重型解析栈：make env-pdf（普通 uv sync 会把它裁掉）"

env-pdf:
	cd $(ENV_DIR) && uv sync --extra pdf

kernel:
	uv run python -m ipykernel install --user --name env_rag --display-name "Python 3.12 (llm-rag-lab)"

lab:
	./start-notebooks.sh --language zh-CN --module $(MODULE)

lab-en:
	./start-notebooks.sh --language en --module $(MODULE)

run:
	$(PY) scripts/execute_notebooks.py

outputs:
	$(PY) scripts/embed_expected_outputs.py

check:
	@python3 scripts/check_parity.py

doctor:
	@python3 scripts/doctor.py

map:
	@python3 scripts/course_map.py
