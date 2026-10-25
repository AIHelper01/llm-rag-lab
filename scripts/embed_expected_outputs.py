#!/usr/bin/env python3
"""把已执行 notebook 的真实输出内嵌回课件本体（清空 outputs 后仍然看得见）。

规则（与 AGENTS.md 的课程约定一致）：
- 文字输出 -> `**预期输出：**` + ```text 逐字摘录；超过 MAX_CHARS 的单元按字符截断，
  并在块内如实标注省略了多少；
- 图片输出 -> 导出到 `assets/`（中英两侧共用），命名 `<课件主干>-<序号>.png`，markdown 用相对路径引用；
- 生成的 markdown 单元带 `course-expected-output` 标签，可重复执行（先删后建），内容不变则单元 id 不变；
- 只处理中文母本。英文镜像不内嵌：输出内容本身是中文语料，进 `english/` 会破坏「镜像无中日韩文字」的硬规则，
  镜像只保留「在真实环境执行后查看输出」的提示；
- 内嵌完成后清空代码单元的原生 outputs（`--keep-outputs` 可保留）：原生输出里带 venv 与 ipykernel 临时目录等
  机器路径，不适合进 git，课件靠「预期输出」块自证。没有实跑输出时脚本拒绝覆盖已有的「预期输出」块。

用法（仓库根目录）：
    uv run python scripts/execute_notebooks.py                       # 先真实执行
    uv run python scripts/embed_expected_outputs.py                  # 再内嵌全部课件
    uv run python scripts/embed_expected_outputs.py --only 02_综合实战-LangChain-进阶版.ipynb
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import re
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
TAG = "course-expected-output"
MAX_CHARS = 3000

FENCE_SAFE = re.compile(r"\n```")
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
REPO_PATH = re.compile(r"/Users/[^\s'\"`]+?(?=llm-rag-lab)")
HOME_PATH = re.compile(r"/Users/[^/\s'\"`]+")
IPYKERNEL_PATH = re.compile(r"(?:/private)?/(?:var/folders/[^\s'\"`]+?|tmp)/ipykernel_\d+/")

LABELS = {
    "text": "**预期输出：**",
    "image": "**预期输出（图片）：**",
    "path_note": "（输出里的 `…` 代表运行本 notebook 那台机器上的仓库绝对路径前缀，你在自己机器上执行会看到自己的路径。）",
    "home_note": "（输出里的 `~` 代表运行机器上的用户主目录，每台机器不同。）",
    "kernel_path_note": "（输出里的 `…` 是 Jupyter 内核本次运行的临时目录，每台机器、每次运行都不同；告警本身可以忽略。）",
    "figure": "第 {n} 张输出图",
    "truncated": "（本次输出共 {total} 个字符，这里摘录前 {kept} 个；完整内容请在真实环境执行本单元查看。）",
}

ASSETS = ROOT / "assets"

# prefix: 图片命名主干；assets_rel: 从课件所在目录看 assets 的相对路径；intro: 实跑说明（人工撰写，数字来自实跑）。
JOBS = [
    {
        "notebook": "模型统一配置说明.ipynb",
        "prefix": "model-configuration",
        "assets_rel": "assets",
        "intro": """> **本课件的实跑记录**：9 个代码单元在 `env_rag_uv` 内核真实执行，全程约 12 秒，8 个单元有输出，0 报错。
> 实测口径：Embedding 维度 `1024`；Reranker 给相关句 `1.0`、无关句 `9e-05`；Milvus 服务端 `3.0.3`（`http://localhost:19530`）；
> 演示 collection `rag_lab_demo` 写入 6 行，向量检索 top-4 相似度 `0.845 / 0.611 / 0.474 / 0.426`；
> LangChain 自定义 compressor 精排后剩两条，得分 `1.0` 与 `0.126953`。
> 前置服务：vLLM（`my_qwen3.8_flash_next`）、Xinference（embedding / reranker）、Milvus，缺哪个对应单元就报错。
> 大模型两次的回答措辞每次都会变，下面摘录的模型文本只是样例，不是断言。
> 想刷新这些输出：`make run` 真实执行 → `make outputs` 重新内嵌。""",
    },
    {
        "notebook": "02_综合实战/PDF数据清洗脚本示例.ipynb",
        "prefix": "pdf-cleaning-example",
        "assets_rel": "../assets",
        "intro": """> **本课件的实跑记录**：两个单元在 `env_rag_uv` 内核真实执行，合计约 37 秒（Unstructured 13 秒 / PyMuPDF 22 秒），0 报错。
> Unstructured 的 fast 策略在 5 份 PDF 上分别切出 `1037 / 741 / 1040 / 782 / 1013` 个 Element；
> PyMuPDF 路线 5 份全部成功；两条路线的 Markdown 都写到 `../tmp/pdf-cleaning-demo/VMAX-S`（合计约 4 300 行）。
> 前置：`cd ~/env_rag_uv && uv sync --extra pdf`（会拉 torch/timm/transformers/opencv，约 1.5 GB），
> 并且 preshed 必须 `<3.0.14`——否则 spaCy 加载失败被 Unstructured 吞掉，Element 数量会全部是 `0`。""",
    },
    {
        "notebook": "02_综合实战/01_综合实战-LangChain-基础版.ipynb",
        "prefix": "langchain-baseline",
        "assets_rel": "../assets",
        "intro": """> **本课件的实跑记录**：77 个代码单元在 `env_rag_uv` 内核真实执行，耗时 277.7 秒，56 个单元有输出，0 报错。
> 语料口径：5 份 PDF 共 188 页 → 章节感知切分 451 个 chunk / 101 457 字符；写入 Milvus 集合 `ZXVMAXS`（dense）与
> `ZXVMAXS_HYBRID`（dense + sparse，BM25 文档数 451），各 16 批导入完成，两个集合都是 `drop_old=True` 重建，重复执行安全。
> 检索口径：weighted 混合检索首选命中「上网日志业务」第 13 页的「4 功能」章；关键词型问题动态权重 dense `0.4` / BM25 `0.6`；RRF、Xinference Rerank 见对应单元。
> LLM-as-Judge 平均分：RAG `3.45`（忠实度 5.0 / 相关性 3.00 / 完整性 2.33）对比基线无 RAG `1.66`（1.0 / 2.67 / 1.33）。
> 前置服务：Milvus（`localhost:19530`）、vLLM、Xinference。模型生成的中文每次都会变，下面摘录的回答与评分是**一次真实运行**的样本。""",
    },
    {
        "notebook": "02_综合实战/02_综合实战-LangChain-进阶版.ipynb",
        "prefix": "langchain-advanced",
        "assets_rel": "../assets",
        "intro": """> **本课件的实跑记录**：92 个代码单元在 `env_rag_uv` 内核真实执行，耗时 381.1 秒，67 个单元有输出，0 报错。
> 预处理口径：单份 PDF 29 页 → 101 个标题分段 → 二次切分 121 个 chunk；Unstructured 路线 75 个章节块 → 88 个 chunk；两条路线的质量检查都通过。
> 本课件的 Markdown 预处理章节就是 `knowledge_md/` 的生成器，重跑之后 `git status --short knowledge_md` 仍然为空，说明语料可复现。
> 检索层评估（3 条）：Hit@5 `0.667`、MRR `0.667`，未命中的是「数据可靠性包括哪些层？」。
> LLM-as-Judge 平均分：RAG `3.22` 对比基线无 RAG `2.00`；其中第 1 题 RAG 只答了「我不知道」，被压到 `1.33` 对 `3.33`——这正是评估环节要暴露的问题，不是脚本故障。
> 前置服务：Milvus（`localhost:19530`）、vLLM、Xinference。LLM 文本与评分每次都会变，摘录只是**一次真实运行**的样本。""",
    },
]


def fold_paths(text: str) -> tuple[str, bool, bool, bool]:
    """折叠机器相关绝对路径，返回 (文本, 含仓库路径, 含主目录, 含内核临时目录)。"""
    saw_repo = bool(REPO_PATH.search(text))
    saw_home = bool(HOME_PATH.search(text))
    saw_kernel = bool(IPYKERNEL_PATH.search(text))
    text = IPYKERNEL_PATH.sub("…/", text)
    text = REPO_PATH.sub("…/", text)
    if not saw_repo:
        text = HOME_PATH.sub("~", text)
    return text, saw_repo, saw_home and not saw_repo, saw_kernel


def heading_caption(cells, index: int, figure_number: int) -> str:
    """向上找最近的 markdown 标题作为图注，找不到就用序号兜底。"""
    fallback = LABELS["figure"].format(n=figure_number)
    for cell in reversed(cells[:index]):
        if cell.cell_type != "markdown":
            continue
        lines = [line.strip() for line in cell.source.splitlines() if line.strip()]
        if not lines:
            continue
        title = lines[0].lstrip("#").strip()
        title = re.sub(r"^\d+[\.、]\s*", "", title)
        if title:
            return title
    return fallback


def clean_text(value: str) -> str:
    value = ANSI_ESCAPE.sub("", value)
    if FENCE_SAFE.search(value):
        value = value.replace("```", "'''")
    return value


def quote_text(raw: str) -> str:
    """逐字摘录，超长时截断并如实标注。"""
    if len(raw) <= MAX_CHARS:
        return clean_text(raw)
    head = clean_text(raw[:MAX_CHARS].rstrip())
    return head + "\n\n" + LABELS["truncated"].format(total=len(raw), kept=MAX_CHARS)


def build_blocks(nb, job):
    lang_cells = nb.cells
    blocks: dict[int, str] = {}
    figure = 0
    used_images: list[Path] = []
    for index, cell in enumerate(lang_cells):
        if cell.cell_type != "code" or not cell.outputs:
            continue
        text_parts: list[str] = []
        image_parts: list[str] = []
        notes = set()
        for output in cell.outputs:
            kind = output.output_type
            if kind in ("stream", "error"):
                raw = "".join(output.text) if kind == "stream" else "\n".join(output.get("traceback", []))
            elif kind == "execute_result":
                raw = "".join(output.get("data", {}).get("text/plain", ""))
            else:
                raw = ""
            if raw.strip():
                folded, saw_repo, saw_home, saw_kernel = fold_paths(raw.rstrip())
                text_parts.append(folded)
                if saw_repo:
                    notes.add("path_note")
                if saw_home:
                    notes.add("home_note")
                if saw_kernel:
                    notes.add("kernel_path_note")
            png = output.get("data", {}).get("image/png") if kind in ("display_data", "execute_result") else None
            if png:
                figure += 1
                name = f"{job['prefix']}-{figure}.png"
                target = ASSETS / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(base64.b64decode(png))
                caption = heading_caption(lang_cells, index, figure)
                image_parts.append(f"![{caption}]({job['assets_rel']}/{name})\n\n*{caption}*")
                used_images.append(target)
        body: list[str] = []
        if text_parts:
            body.append(LABELS["text"] + "\n\n```text\n" + quote_text("\n".join(text_parts)) + "\n```")
            for key in ("path_note", "home_note", "kernel_path_note"):
                if key in notes:
                    body.append(LABELS[key])
        for part in image_parts:
            body.append(LABELS["image"] + "\n\n" + part)
        if body:
            blocks[index] = "\n\n".join(body)
    return blocks, figure, used_images


def block_id(job, key, content: str) -> str:
    """内容不变则单元 id 不变：重复内嵌不会在 git diff 里留下只换 id 的噪音。"""
    prefix = re.sub(r"[^A-Za-z0-9_-]", "-", job["prefix"])
    digest = hashlib.sha1(content.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-expected-{key}-{digest}"[:64]


def apply_job(job, keep_outputs: bool = False) -> str:
    path = ROOT / job["notebook"]
    if not path.is_file():
        return f"跳过（缺少文件）：{path}"
    nb = nbformat.read(path, as_version=4)
    had_tag = any(TAG in c.get("metadata", {}).get("tags", []) for c in nb.cells)
    nb.cells = [c for c in nb.cells if TAG not in c.get("metadata", {}).get("tags", [])]
    executed = any(c.cell_type == "code" and c.get("outputs") for c in nb.cells)
    if not executed:
        # 没有实跑输出还内嵌，会把已有的「预期输出」块清空——必须先 make run，别拿空壳覆盖课件
        return f"跳过（没有实跑输出，先执行 make run）：{job['notebook']}" if had_tag \
            else f"跳过（没有实跑输出）：{job['notebook']}"
    blocks, figures, _ = build_blocks(nb, job)
    rebuilt = []
    for index, cell in enumerate(nb.cells):
        rebuilt.append(cell)
        if index in blocks:
            rebuilt.append(nbformat.v4.new_markdown_cell(
                blocks[index], metadata={"tags": [TAG]}, id=block_id(job, index, blocks[index])))
    nb.cells = rebuilt
    if job.get("intro"):
        nb.cells.insert(1, nbformat.v4.new_markdown_cell(
            job["intro"], metadata={"tags": [TAG]}, id=block_id(job, "intro", job["intro"])))
    nb.cells = [c for c in nb.cells if not (c.cell_type == "markdown" and "outputs" in c)]
    cleared = 0
    if not keep_outputs:
        # 原生 outputs 里全是机器相关路径（venv、ipykernel 临时目录），只留「预期输出」块：
        # 内容与深学仓一致，git diff 也只反映课件内容本身。
        for cell in nb.cells:
            if cell.cell_type == "code" and (cell.get("outputs") or cell.get("execution_count") is not None):
                cleared += bool(cell.get("outputs"))
                cell.outputs = []
                cell.execution_count = None
    nbformat.write(nb, path)
    tail = "（已清空原生 outputs）" if not keep_outputs else ""
    return f"{job['notebook']}：内嵌 {len(blocks)} 处文字块、{figures} 张图，清理 {cleared} 个单元的原生输出{tail}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", help="只处理指定课件文件名，可重复")
    parser.add_argument("--keep-outputs", action="store_true",
                        help="内嵌后保留 notebook 原生 outputs（默认清空，机器路径不进 git）")
    args = parser.parse_args()
    jobs = [j for j in JOBS if not args.only or Path(j["notebook"]).name in args.only]
    for job in jobs:
        print(apply_job(job, keep_outputs=args.keep_outputs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
