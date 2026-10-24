#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中英课程校验：配对完整性、英文侧纯英文、镜像溯源与结构对齐。

用法（仓库根目录）：

    uv run python scripts/check_parity.py        # 全绿退出码 0，否则 1
    python3 scripts/check_parity.py --json        # 附带 JSON 摘要（供工具消费）

检查项（规则来源见 AGENTS.md）：
1. 每篇中文母本课程文档都在 `course_map.COURSE_DOCS` 里，或登记在 `NON_COURSE`（数据/资源/vendored）。
2. 映射表里的母本必须真实存在；镜像未落地时必须写明原因（待译是有意安排，不是遗漏）。
3. `english/` 下每篇文档都能反查到母本（不允许孤儿镜像）。
4. `english/` 下目录名与文件名必须是 ASCII。
5. `english/` 下所有文本（含 Notebook 输出、文件名）不得出现中日韩字符。
6. 已落地的 Markdown 镜像必须带 `<!-- derived-from: <百分号编码相对路径> -->`，且解码后指向映射表中的母本。
7. 已配对的 Markdown：标题数量与图片引用数量一致；镜像里的相对链接与图片必须可解析。
8. 已配对的 Notebook：单元格数量一致。
9. 双语入口：`README.zh-CN.md`（中文母本入口）与 `README.md`（英文入口）互相链接，`english/README.md` 存在。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import course_map as cm  # noqa: E402

ROOT = cm.ROOT
EN = ROOT / cm.ENGLISH_DIR
CJK = re.compile(r"[\u3000-\u303f\u3400-\u9fff\uf900-\ufaff\uff01-\uff60]")
ASCII_ONLY = re.compile(r"^[\x20-\x7e]+$")
DERIVED = re.compile(r"<!--\s*derived-from:\s*(\S+?)\s*-->")
MD_LINK = re.compile(r"!?\[[^\]]*\]\(<?([^)>\s]+)>?\)")
HTML_IMG = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE)
SKIP_DIRS = {".git", ".venv", "__pycache__", ".ipynb_checkpoints", "node_modules", ".pytest_cache"}
TEXT_SUFFIXES = {".md", ".ipynb", ".py", ".sh", ".ps1", ".json", ".toml", ".txt"}
PROVENANCE_HEAD_LINES = 6


def walk_masters():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        parts = rel.split("/")
        if any(part in SKIP_DIRS for part in parts[:-1]):
            continue
        if parts[0] == cm.ENGLISH_DIR:
            continue
        yield rel, path


def walk_english():
    if not EN.exists():
        return
    for path in sorted(EN.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        parts = rel.split("/")
        if any(part in SKIP_DIRS for part in parts[:-1]):
            continue
        yield rel, path


def english_rel(rel: str) -> str:
    return Path(rel).relative_to(cm.ENGLISH_DIR).as_posix()


def md_stats(path: Path) -> tuple:
    text = path.read_text(encoding="utf-8", errors="replace")
    headings = sum(1 for line in text.splitlines() if line.startswith("#"))
    images = len(HTML_IMG.findall(text)) + len(re.findall(r"!\[[^\]]*\]\(", text))
    return headings, images, text


def notebook_cells(path: Path):
    try:
        notebook = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None
    cells = notebook.get("cells")
    if not isinstance(cells, list):
        return None
    markdown = sum(1 for cell in cells if cell.get("cell_type") == "markdown")
    return len(cells), markdown


def check(failures: list, rel: str, message: str) -> None:
    failures.append(f"{rel}: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="中英课程校验")
    parser.add_argument("--json", action="store_true", help="额外打印 JSON 摘要")
    args = parser.parse_args()

    failures: list = []
    warnings: list = []
    seen_masters: set = set()

    # 1/3. 母本侧覆盖：磁盘上的课程文档必须登记（映射表或非课程）
    for rel, path in walk_masters():
        if path.suffix.lower() not in {".md", ".ipynb"}:
            continue
        if rel in cm.COURSE_DOCS or cm.is_non_course(rel):
            seen_masters.add(rel)
            continue
        check(failures, rel, "未登记：加入 course_map.COURSE_DOCS（要翻译）或 NON_COURSE（数据/资源，附原因）")

    for rel in cm.NON_COURSE:
        if rel not in seen_masters and not (ROOT / rel).exists() and (ROOT / rel).suffix == "":
            warnings.append(f"NON_COURSE 前缀已失效（磁盘上找不到 {rel}*）")

    # 2. 映射表：母本存在；镜像未落地必须带原因
    translated, pending_docs = [], []
    for master, english in cm.COURSE_DOCS.items():
        if not (ROOT / master).exists():
            check(failures, master, "映射表里的母本在磁盘上不存在，请修正 course_map.py")
            continue
        if (EN / english).exists():
            translated.append((master, english))
        elif master in cm.PENDING_REASONS:
            pending_docs.append((master, english))
        else:
            check(failures, master, f"镜像 {cm.ENGLISH_DIR}/{english} 未落地，且 PENDING_REASONS 未登记原因")

    for master in cm.PENDING_REASONS:
        if master not in cm.COURSE_DOCS:
            warnings.append(f"PENDING_REASONS 有孤儿条目：{master}")
        elif (EN / cm.COURSE_DOCS[master]).exists():
            check(failures, master, "镜像已落地，应从 PENDING_REASONS 移除")

    # 3/4/5. 镜像侧：无孤儿、ASCII 名字、纯英文内容
    mirrored = set(cm.COURSE_DOCS.values())
    for rel, path in walk_english():
        e_rel = english_rel(rel)
        if path.suffix.lower() in {".md", ".ipynb"} and e_rel not in cm.ENGLISH_ONLY and e_rel not in mirrored:
            check(failures, rel, "孤儿镜像：在 course_map.COURSE_DOCS 里找不到对应母本")
        for part in path.relative_to(EN).parts:
            if not ASCII_ONLY.match(part):
                check(failures, rel, f"english/ 下必须使用 ASCII 名字：{part}")
        if path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="replace")
            hit = CJK.search(text)
            if hit:
                line = text[:hit.start()].count("\n") + 1
                check(failures, rel, f"english/ 不得出现中日韩字符（第 {line} 行：{hit.group()!r}）")

    # 6/7/8. 已配对内容：溯源 + 结构对齐 + 链接可解析
    for master, english in translated:
        mirror = EN / english
        master_file = ROOT / master
        if mirror.suffix.lower() == ".ipynb":
            master_cells, mirror_cells = notebook_cells(master_file), notebook_cells(mirror)
            if master_cells and mirror_cells and master_cells[0] != mirror_cells[0]:
                check(failures, mirror.relative_to(ROOT).as_posix(),
                      f"Notebook 单元格数与母本不一致：英文 {mirror_cells[0]} vs 中文 {master_cells[0]}")
            continue

        text = mirror.read_text(encoding="utf-8", errors="replace")
        head = "\n".join(text.splitlines()[:PROVENANCE_HEAD_LINES])
        match = DERIVED.search(head)
        if not match:
            check(failures, mirror.relative_to(ROOT).as_posix(),
                  f"缺少溯源注释：前 {PROVENANCE_HEAD_LINES} 行内需要 <!-- derived-from: <百分号编码路径> -->")
        else:
            target = (mirror.parent / unquote(match.group(1))).resolve()
            if target != (ROOT / master).resolve():
                check(failures, mirror.relative_to(ROOT).as_posix(),
                      f"溯源指向 {target.name}，但映射表母本是 {Path(master).name}")
        if not (mirror.parent / unquote(cm.english_link(master, english))).exists():
            check(failures, mirror.relative_to(ROOT).as_posix(),
                  f"指向母本的百分号编码链接无法解析：{cm.english_link(master, english)}")

        master_heads, master_imgs, _ = md_stats(master_file)
        mirror_heads, mirror_imgs, mirror_text = md_stats(mirror)
        if mirror_heads != master_heads:
            check(failures, mirror.relative_to(ROOT).as_posix(),
                  f"标题数量与母本不一致：英文 {mirror_heads} vs 中文 {master_heads}")
        if mirror_imgs != master_imgs:
            check(failures, mirror.relative_to(ROOT).as_posix(),
                  f"图片引用数量与母本不一致：英文 {mirror_imgs} vs 中文 {master_imgs}")
        for link in MD_LINK.findall(mirror_text) + HTML_IMG.findall(mirror_text):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not (mirror.parent / unquote(link)).exists():
                check(failures, mirror.relative_to(ROOT).as_posix(), f"相对链接无法解析：{link}")

    # 9. 双语入口
    zh_entry, en_entry = ROOT / "README.zh-CN.md", ROOT / "README.md"
    for entry in (zh_entry, en_entry):
        if not entry.exists():
            check(failures, entry.name, "缺少双语入口文件")
    if zh_entry.exists() and "README.md" not in zh_entry.read_text(encoding="utf-8"):
        check(failures, "README.zh-CN.md", "入口需链接到英文入口 README.md")
    if en_entry.exists() and "README.zh-CN.md" not in en_entry.read_text(encoding="utf-8"):
        check(failures, "README.md", "英文入口需链接回中文母本入口 README.zh-CN.md")
    if not (EN / "README.md").exists():
        check(failures, f"{cm.ENGLISH_DIR}/README.md", "缺少英文课程入口")

    stats = cm.progress()
    print(f"课程文档 {stats['total']} 篇：已翻译 {stats['translated']}，待翻译 {stats['pending']}")
    for master, english in sorted(pending_docs):
        print(f"  [待译] {master} -> {cm.ENGLISH_DIR}/{english}")
    for note in warnings:
        print(f"  [提示] {note}")
    if failures:
        print(f"\n发现 {len(failures)} 个问题：")
        for failure in failures:
            print(f"  ✗ {failure}")
    else:
        print("\n✓ 中英对齐检查通过（english/ 纯英文、配对完整、溯源与结构一致）")

    if args.json:
        print(json.dumps({"stats": stats, "failures": failures, "warnings": warnings}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
