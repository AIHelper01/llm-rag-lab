# llm-rag-lab 一键入口（macOS / Linux）。Windows 用 start-notebooks.ps1。
.PHONY: help sync kernel lab lab-en check doctor map

help:
	@echo "make sync     - uv sync，装齐中英两侧共用依赖"
	@echo "make kernel   - 注册 Jupyter 内核 env_rag"
	@echo "make lab      - 打开中文模块（默认 foundations）：make lab MODULE=capstone"
	@echo "make lab-en   - 打开英文镜像：make lab-en MODULE=capstone"
	@echo "make check    - 中英对齐与英文侧纯英文检查"
	@echo "make doctor   - 环境体检：uv / Python / .env / 关键依赖"
	@echo "make map      - 打印中英映射表与翻译进度"

MODULE ?= foundations

sync:
	uv sync --locked

kernel:
	uv run python -m ipykernel install --user --name env_rag --display-name "Python 3.12 (llm-rag-lab)"

lab:
	./start-notebooks.sh --language zh-CN --module $(MODULE)

lab-en:
	./start-notebooks.sh --language en --module $(MODULE)

check:
	@python3 scripts/check_parity.py

doctor:
	@python3 scripts/doctor.py

map:
	@python3 scripts/course_map.py
