#!/usr/bin/env bash
# 同步 uv 环境并打开指定语言/模块的 JupyterLab（macOS / Linux）。
# 用法：./start-notebooks.sh --language zh-CN|en --module foundations|capstone|frontiers [--dry-run]
set -euo pipefail

language="zh-CN"
module="foundations"
dry_run=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --language) language="$2"; shift 2 ;;
    --module) module="$2"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) sed -n '1,4p' "$0"; exit 0 ;;
    *) echo "未知参数：$1" >&2; exit 2 ;;
  esac
done

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$root"

if [[ "$language" != "zh-CN" && "$language" != "en" ]]; then
  echo "--language 只能是 zh-CN 或 en" >&2; exit 2
fi

uv_command() {
  if command -v uv >/dev/null 2>&1; then uv "$@"; else python3 -m uv "$@"; fi
}

if ! target="$(python3 scripts/course_map.py --module-dir "$language" "$module" 2>/dev/null)"; then
  echo "无法解析模块 $module（可选：foundations / capstone / frontiers）" >&2
  python3 scripts/course_map.py --modules >&2
  exit 2
fi

if [[ ! -d "$target" ]]; then
  echo "目录不存在：$target（该模块的英文镜像可能尚未翻译）" >&2; exit 1
fi
if [[ ! -f uv.lock ]]; then
  echo "缺少 uv.lock，请先 git checkout 恢复，见 README" >&2; exit 1
fi

if [[ "$dry_run" -eq 1 ]]; then
  echo "language=$language module=$module project=$root notebook_dir=$target"
  exit 0
fi

uv_command sync --locked
uv_command run --locked jupyter lab --notebook-dir "$target"
