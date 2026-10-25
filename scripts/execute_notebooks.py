#!/usr/bin/env python3
"""在课堂内核里真实执行课件 notebook，并把输出写回 notebook 本体。

用法（仓库根目录）：
    uv run python scripts/execute_notebooks.py                    # 全部课件，按依赖顺序
    uv run python scripts/execute_notebooks.py --only 模型统一配置说明.ipynb
    uv run python scripts/execute_notebooks.py --kernel env_rag_uv

说明：
- `02_综合实战/` 下的课件从模块目录读取 `../.env`，所以执行时工作目录就是该模块目录；
  根目录课件在仓库根执行。工作目录由 JOBS 登记，不靠调用方记住。
- `allow_errors=True`：可选依赖缺失的单元照常留下错误输出，便于「预期输出」如实反映；
  脚本结束时汇总每个 notebook 的错误单元，非零退出码提示需要人工确认。
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KERNEL = "env_rag_uv"

# 执行顺序即依赖顺序：先只读的模型配置说明，再 PDF 清洗，最后重建集合的两个综合实战课件。
JOBS = [
    {"notebook": "模型统一配置说明.ipynb", "cwd": ROOT, "timeout": 1800},
    {"notebook": "02_综合实战/PDF数据清洗脚本示例.ipynb", "cwd": ROOT / "02_综合实战", "timeout": 1800},
    {"notebook": "02_综合实战/01_综合实战-LangChain-基础版.ipynb", "cwd": ROOT / "02_综合实战", "timeout": 2400},
    {"notebook": "02_综合实战/02_综合实战-LangChain-进阶版.ipynb", "cwd": ROOT / "02_综合实战", "timeout": 2400},
]


def run_job(job: dict, kernel: str) -> tuple[int, int]:
    path = ROOT / job["notebook"]
    nb = nbformat.read(path, as_version=4)
    code = [c for c in nb.cells if c.cell_type == "code"]
    print(f"\n=== {job['notebook']}：{len(code)} 个代码单元，工作目录 {job['cwd'].relative_to(ROOT) or '.'} ===",
          flush=True)
    started = time.perf_counter()
    client = NotebookClient(
        nb,
        kernel_name=kernel,
        timeout=job["timeout"],
        resources={"metadata": {"path": str(job["cwd"])}},
        allow_errors=True,
    )
    # 逐单元执行并打印进度：全量跑一个课件要十几分钟，没有进度的话无法判断是卡在哪个远程调用上。
    done = 0
    with client.setup_kernel():
        for index, cell in enumerate(nb.cells):
            if cell.cell_type != "code":
                continue
            started_at = time.perf_counter()
            client.execute_cell(cell, index)
            done += 1
            elapsed = time.perf_counter() - started_at
            label = ''.join(cell.source).strip().splitlines()[0][:48] if cell.source.strip() else "(empty)"
            print(f"    [{done:>3}/{len(code)}] 单元 {index:>3} 用时 {elapsed:>6.1f}s  {label}", flush=True)
    nbformat.write(nb, path)
    errors = [i for i, c in enumerate(nb.cells)
              if c.cell_type == "code" and any(o.output_type == "error" for o in c.get("outputs", []))]
    with_output = sum(1 for c in nb.cells if c.cell_type == "code" and c.get("outputs"))
    print(f"    耗时 {time.perf_counter() - started:.1f}s | 有输出 {with_output}/{len(code)} | 错误单元 {errors}",
          flush=True)
    return len(errors), with_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", default=DEFAULT_KERNEL, help=f"Jupyter 内核名，默认 {DEFAULT_KERNEL}")
    parser.add_argument("--only", action="append", help="只跑指定的 notebook 文件名，可重复")
    args = parser.parse_args()

    jobs = [j for j in JOBS if not args.only or Path(j["notebook"]).name in args.only]
    if not jobs:
        print(f"没有匹配的课件，可选：{[Path(j['notebook']).name for j in JOBS]}")
        return 2

    total_errors = 0
    for job in jobs:
        total_errors += run_job(job, args.kernel)[0]
    print(f"\n全部执行完成，错误单元合计 {total_errors} 个"
          + ("（多为可选依赖的跳过分支，请人工确认）" if total_errors else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
