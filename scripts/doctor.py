#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""环境体检：uv、Python 版本、uv.lock、.env 键位、关键依赖导入。

用法（仓库根目录）：

    python3 scripts/doctor.py      # 未装依赖也能跑，会提示改用 uv run
    uv run python scripts/doctor.py

只检查、不修改；`.env` 只报告键名与是否为空，绝不打印值。
退出码：0 = 可用；1 = 存在阻塞问题（输出里标 FAIL 的条目）。
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_KEYS = ["vLLM_QWEN_BASE_URL", "vLLM_QWEN_API_KEY", "vLLM_QWEN_MODEL_ID",
               "XINFERENCE_OPENAI_BASE_URL", "XINFERENCE_API_KEY",
               "XINFERENCE_EMBEDDING_MODEL_ID", "XINFERENCE_RERANKER_MODEL_ID"]
OPTIONAL_KEYS = ["XINFERENCE_BASE_URL"]
KEY_IMPORTS = {
    "langchain": "langchain",
    "langchain-openai": "langchain_openai",
    "langchain-milvus": "langchain_milvus",
    "xinference-client": "xinference_client",
    "jupyter": "jupyter_server",
}
results: list = []


def record(level: str, label: str, detail: str) -> None:
    results.append((level, label, detail))


def read_env(path: Path) -> dict:
    """解析 .env，兼容 `KEY = value`、注释行与 CRLF。"""
    values: dict = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main() -> int:
    uv = shutil.which("uv")
    record("pass" if uv else "warn", "uv",
           uv if uv else "未找到 uv（默认启动路径依赖它）：https://docs.astral.sh/uv/getting-started/installation/")

    version = ".".join(str(part) for part in sys.version_info[:3])
    level = "pass" if sys.version_info >= (3, 12) else "warn"
    record(level, "Python", f"当前解释器 {sys.executable} / {version}"
           + ("" if level == "pass" else "（项目要求 3.12，请用 `uv run python scripts/doctor.py`）"))

    lock = ROOT / "uv.lock"
    record("pass" if lock.exists() else "fail", "uv.lock",
           "存在，`uv sync --locked` 可复现环境" if lock.exists() else "缺失，请 git checkout uv.lock")

    env = read_env(ROOT / ".env")
    if not env:
        record("fail", ".env", "仓库根未找到 .env，密钥类 Notebook 会失败")
    else:
        missing = [key for key in REQUIRED_KEYS if not env.get(key)]
        detail = f"共 {len(env)} 个键；必填缺失：{missing or '无'}；可选未设：" + \
                 (", ".join(key for key in OPTIONAL_KEYS if not env.get(key)) or "无")
        record("fail" if missing else "pass", ".env", detail)
        if list(ROOT.glob(".env")) and (ROOT / ".git").exists():
            tracked = subprocess.run(["git", "ls-files", "--error-unmatch", ".env"], cwd=ROOT,
                                     capture_output=True, text=True).returncode == 0
            if tracked:
                record("warn", ".env 已被 Git 跟踪", "历史遗留：轮换入库密钥，通知协作者后再 git rm --cached .env")

    for package, module in KEY_IMPORTS.items():
        try:
            installed = importlib.util.find_spec(module) is not None
        except (ImportError, ValueError):
            installed = False
        record("pass" if installed else "warn", package,
               "可导入" if installed else "当前解释器未安装（用 uv 环境或 ~/env_rag_uv，见 README）")

    for level, label, detail in results:
        print(f"[{level.upper():4}] {label}: {detail}")
    failures = [item for item in results if item[0] == "fail"]
    print(f"\n{'✗ 存在 ' + str(len(failures)) + ' 个阻塞问题' if failures else '✓ 环境检查通过（warn 项按需处理）'}")
    return 1 if failures else 0


if __name__ == "__main__":
    os.chdir(ROOT)
    raise SystemExit(main())
