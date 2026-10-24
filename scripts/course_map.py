#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""课程映射表：中文母本（仓库根）↔ 英文镜像（english/）的唯一对应关系来源。

中英对应**不靠同名推断**（母本目录与文件名保留中文，见 AGENTS.md「已记录的偏离」），
所有配对与「暂不翻译」的原因都在本文件登记，`scripts/check_parity.py` 据此校验。

用法（仓库根目录）：

    python scripts/course_map.py                      # 打印映射表与进度
    python scripts/course_map.py --modules            # 打印模块名 → 目录
    python scripts/course_map.py --module-dir en capstone   # 解析某侧模块目录
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
ENGLISH_DIR = "english"

# ---------------------------------------------------------------- 模块目录
MODULES = {
    "foundations": {"zh-CN": "00_夯实基础", "en": "00-foundations"},
    "capstone": {"zh-CN": "02_综合实战", "en": "02-capstone"},
    "frontiers": {"zh-CN": "03_范式拓展", "en": "03-paradigm-extensions"},
}

# --------------------------------------------------------- 课程文档配对表
# 键 = 中文母本相对路径；值 = 英文镜像相对 english/ 的路径（即翻译后的落地位置）。
# **是否已翻译由镜像文件是否存在决定**，不再另设状态字段，避免两处状态互相漂移。
# 镜像文件不存在时，必须在 PENDING_REASONS 里写明原因（有意为之，而非遗漏）。
COURSE_DOCS = {
    "00_夯实基础/C01_解锁RAG/01_RAG简介.md": "00-foundations/C01-unlock-rag/01_rag-overview.md",
    "00_夯实基础/C01_解锁RAG/02_preparation.md": "00-foundations/C01-unlock-rag/02_preparation.md",
    "00_夯实基础/C01_解锁RAG/03_get_start_rag.md": "00-foundations/C01-unlock-rag/03_get-start-rag.md",
    "00_夯实基础/C01_解锁RAG/virtualenv.md": "00-foundations/C01-unlock-rag/virtualenv.md",
    "00_夯实基础/C02_数据准备/01_数据加载.md": "00-foundations/C02-data-preparation/01_data-loading.md",
    "00_夯实基础/C02_数据准备/02_数据切块.md": "00-foundations/C02-data-preparation/02_text-splitting.md",
    "00_夯实基础/C03_索引构建/01_向量嵌入.md": "00-foundations/C03-index-building/01_embeddings.md",
    "00_夯实基础/C03_索引构建/02_多模态嵌入.md": "00-foundations/C03-index-building/02_multimodal-embeddings.md",
    "00_夯实基础/C03_索引构建/03_向量数据库.md": "00-foundations/C03-index-building/03_vector-databases.md",
    "00_夯实基础/C03_索引构建/04_milvus实践.md": "00-foundations/C03-index-building/04_milvus-in-practice.md",
    "00_夯实基础/C03_索引构建/05_索引优化.md": "00-foundations/C03-index-building/05_index-optimization.md",
    "00_夯实基础/C03_索引构建/补充理解：Milvus_向量检索原理_HNSW_COSINE.md":
        "00-foundations/C03-index-building/06_supplement-milvus-hnsw-cosine.md",
    "00_夯实基础/C04_检索优化/01_混合检索.md": "00-foundations/C04-retrieval-optimization/01_hybrid-retrieval.md",
    "00_夯实基础/C04_检索优化/02_查询构建.md": "00-foundations/C04-retrieval-optimization/02_query-construction.md",
    "00_夯实基础/C04_检索优化/03_text2sql.md": "00-foundations/C04-retrieval-optimization/03_text2sql.md",
    "00_夯实基础/C04_检索优化/04_查询重构与分发.md": "00-foundations/C04-retrieval-optimization/04_query-rewriting-and-routing.md",
    "00_夯实基础/C04_检索优化/05_检索进阶技术.md": "00-foundations/C04-retrieval-optimization/05_advanced-retrieval.md",
    "00_夯实基础/C05_生成集成/01_格式化生成.md": "00-foundations/C05-generation-integration/01_structured-generation.md",
    "00_夯实基础/C06_RAG系统评估/01_评估介绍.md": "00-foundations/C06-rag-evaluation/01_evaluation-overview.md",
    "00_夯实基础/C06_RAG系统评估/02_评估工具.md": "00-foundations/C06-rag-evaluation/02_evaluation-tools.md",
    "02_综合实战/README.md": "02-capstone/README.md",
    "02_综合实战/01_综合实战-LangChain-基础版.ipynb": "02-capstone/01_langchain-baseline.ipynb",
    "02_综合实战/02_综合实战-LangChain-进阶版.ipynb": "02-capstone/02_langchain-advanced.ipynb",
    "02_综合实战/PDF数据清洗脚本示例.ipynb": "02-capstone/pdf-cleaning-example.ipynb",
    "02_综合实战/03_综合实战-RAGFlow.md": "02-capstone/03_ragflow.md",
    "03_范式拓展/01_Karpathy式AI知识库搭建指南.md": "03-paradigm-extensions/01_karpathy-style-knowledge-base.md",
    "模型统一配置说明.ipynb": "model-configuration.ipynb",
}

# 镜像尚未落地的母本：原因必须写清楚，保证每处缺失都是有意安排。
PENDING_REASONS = {
    "00_夯实基础/C01_解锁RAG/02_preparation.md":
        "Translation queue: C01 lesson 1 is the reference sample, the rest of C01 follows",
    "00_夯实基础/C01_解锁RAG/03_get_start_rag.md":
        "Translation queue: C01 lesson 1 is the reference sample, the rest of C01 follows",
    "00_夯实基础/C01_解锁RAG/virtualenv.md":
        "Covers the retired Conda/venv route; rewrite around uv first, then translate",
    "00_夯实基础/C02_数据准备/01_数据加载.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C02_数据准备/02_数据切块.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C03_索引构建/01_向量嵌入.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C03_索引构建/02_多模态嵌入.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C03_索引构建/03_向量数据库.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C03_索引构建/04_milvus实践.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C03_索引构建/05_索引优化.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C03_索引构建/补充理解：Milvus_向量检索原理_HNSW_COSINE.md":
        "Translation queue: supplementary note, follows its parent module",
    "00_夯实基础/C04_检索优化/01_混合检索.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C04_检索优化/02_查询构建.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C04_检索优化/03_text2sql.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C04_检索优化/04_查询重构与分发.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C04_检索优化/05_检索进阶技术.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C05_生成集成/01_格式化生成.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C06_RAG系统评估/01_评估介绍.md": "Translation queue: modules C02-C06 translate in course order",
    "00_夯实基础/C06_RAG系统评估/02_评估工具.md": "Translation queue: modules C02-C06 translate in course order",
    "02_综合实战/README.md":
        "Capstone README translated together with the capstone notebooks so terminology stays consistent",
    "02_综合实战/01_综合实战-LangChain-基础版.ipynb":
        "Capstone notebooks need a live Milvus + embedding stack to regenerate English outputs",
    "02_综合实战/02_综合实战-LangChain-进阶版.ipynb":
        "Capstone notebooks need a live Milvus + embedding stack to regenerate English outputs",
    "02_综合实战/PDF数据清洗脚本示例.ipynb":
        "Capstone notebooks need a live Milvus + embedding stack to regenerate English outputs",
    "02_综合实战/03_综合实战-RAGFlow.md": "Translation queue: platform chapter follows the notebooks",
    "03_范式拓展/01_Karpathy式AI知识库搭建指南.md": "Translation queue: extension chapter comes after the core course",
    "模型统一配置说明.ipynb": "Needs a live model stack to regenerate English outputs; translates with the capstone",
}

# 不参与双语配对（数据 / 资源 / vendored 代码 / 单侧文档）：前缀 → 原因。
NON_COURSE = {
    "knowledge_md/": "Cleaned knowledge-base corpus: course data, never translated",
    "knowledge_path/": "Source PDF knowledge base: course data, never translated",
    "assets/": "Shared image assets, referenced by both language sides",
    "00_夯实基础/C01_解锁RAG/data/": "Sample corpus for the loading lesson, kept as-is",
    "00_夯实基础/C03_索引构建/code/visual_bge/": "Vendored third-party library, kept as-is",
    "AGENTS.md": "Repository conventions, written once in Chinese; README.md carries the English summary",
    "README.md": "English course entry (mirrors README.zh-CN.md, checked separately)",
    "README.zh-CN.md": "Chinese course entry (the master entry, checked separately)",
}

# 英文侧允许存在、且不与母本配对的自有文件（镜像入口与工程文件）。
ENGLISH_ONLY = {
    "README.md": "English course entry",
    "COURSE_ROOT": "Marker file: English mirror root",
}


def is_non_course(master_rel: str) -> bool:
    return any(master_rel.startswith(prefix) for prefix in NON_COURSE)


def master_path(english_rel: str) -> PurePosixPath:
    """镜像路径 → 母本路径（english/ 下相对路径）。"""
    for master, english in COURSE_DOCS.items():
        if english == english_rel:
            return PurePosixPath(master)
    raise KeyError(english_rel)


def english_link(master: str, from_english: str) -> str:
    """母本相对路径 → 镜像文件里可直接使用的百分号编码相对链接（纯 ASCII）。"""
    relative = os.path.relpath(str(ROOT / master), str(ROOT / ENGLISH_DIR / PurePosixPath(from_english).parent))
    return quote(relative.replace(os.sep, "/"))


def module_dir(language: str, module: str) -> Path:
    entry = MODULES[module]["en"] if language == "en" else MODULES[module]["zh-CN"]
    return ROOT / (ENGLISH_DIR if language == "en" else "") / entry


def translated() -> list:
    """镜像文件已存在的母本 = 已翻译。"""
    return sorted(m for m, e in COURSE_DOCS.items() if (ROOT / ENGLISH_DIR / e).exists())


def pending() -> list:
    """映射表里有、但镜像还没落地的母本 = 待翻译。"""
    return sorted(m for m, e in COURSE_DOCS.items() if not (ROOT / ENGLISH_DIR / e).exists())


def progress() -> dict:
    done, todo = translated(), pending()
    return {"total": len(COURSE_DOCS), "translated": len(done), "pending": len(todo),
            "done": done, "pending_docs": todo}


def main() -> int:
    parser = argparse.ArgumentParser(description="课程映射表（中文母本 ↔ 英文镜像）")
    parser.add_argument("--modules", action="store_true", help="打印模块名与目录")
    parser.add_argument("--module-dir", nargs=2, metavar=("LANGUAGE", "MODULE"),
                        help="解析某一语言侧的模块目录")
    parser.add_argument("--json", action="store_true", help="以 JSON 打印进度")
    args = parser.parse_args()

    if args.module_dir:
        language, module = args.module_dir
        print(module_dir(language, module))
        return 0
    if args.modules:
        for name, sides in MODULES.items():
            print(f"{name}\tzh-CN={sides['zh-CN']}\ten={sides['en']}")
        return 0
    if args.json:
        print(json.dumps(progress(), ensure_ascii=False, indent=2))
        return 0

    stats = progress()
    print(f"课程文档 {stats['total']} 篇：已翻译 {stats['translated']}，待翻译 {stats['pending']}\n")
    for master, english in COURSE_DOCS.items():
        mark = "done   " if (ROOT / ENGLISH_DIR / english).exists() else "pending"
        tail = english if mark == "done   " else f"{english}  <- {PENDING_REASONS.get(master, '原因未登记!')}"
        print(f"[{mark}] {master}\n          -> {tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
