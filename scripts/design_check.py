#!/usr/bin/env python3
"""设计产出自检：交付前把明显的坑先挑出来。

用法：
    py -3 design_check.py check <路径> [<路径> ...] [--json]

只看文件，不联网、不改文件。退出码 1 表示有阻断项，0 表示没有。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# 本机绝对目录的形态。片段拆开拼接，是为了这份脚本自己不被误判成含个人目录。
LOCAL_PATH_PATTERNS = (
    re.compile("[A-Za-z]:[\\\\/]+Use" + "rs[\\\\/]+[A-Za-z0-9._ -]+[\\\\/]+"),
    re.compile("/Use" + "rs/(?!Shared(?:/|$))[A-Za-z0-9._-]+/"),
    re.compile("/hom" + "e/[A-Za-z0-9._-]+/"),
    re.compile("/ro" + "ot(?:/|$)"),
)

PLACEHOLDER_PATTERNS = (
    (re.compile(r"lorem ipsum", re.IGNORECASE), "还留着 Lorem ipsum 假文字"),
    (re.compile(r"\bTODO\b"), "还留着 TODO 标记"),
    (re.compile(r"\bplaceholder\b", re.IGNORECASE), "还留着 placeholder 字样"),
    (re.compile(r"待补充|此处填写|请填写|点击这里编辑|示例文本"), "还留着没人替换的占位文案"),
    (re.compile(r"\bxxx+\b", re.IGNORECASE), "还留着 xxx 占位"),
)

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
}

WEB_SUFFIXES = {".html", ".htm"}
SVG_SUFFIXES = {".svg"}
PNG_SUFFIXES = {".png"}
TEXT_SUFFIXES = {
    ".html",
    ".htm",
    ".css",
    ".js",
    ".mjs",
    ".json",
    ".md",
    ".svg",
    ".txt",
    ".xml",
}

ASSET_ATTR_RE = re.compile(
    r"""(?:src|href|poster)\s*=\s*["']([^"']+)["']""", re.IGNORECASE
)
CSS_URL_RE = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""", re.IGNORECASE)
META_VIEWPORT_RE = re.compile(
    r"""<meta[^>]+name\s*=\s*["']viewport["']""", re.IGNORECASE
)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)

REMOTE_RE = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//)")
SKIP_ASSET_RE = re.compile(r"^(?:data:|mailto:|tel:|#|javascript:)", re.IGNORECASE)


def iter_files(target: Path):
    if target.is_file():
        yield target
        return
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(target).parts[:-1]):
            continue
        yield path


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def add(findings: list, level: str, code: str, path: Path, message: str, line: int = 0):
    findings.append(
        {
            "level": level,
            "code": code,
            "file": str(path),
            "line": line,
            "message": message,
        }
    )


def check_common_text(path: Path, text: str, findings: list) -> None:
    for pattern, message in PLACEHOLDER_PATTERNS:
        match = pattern.search(text)
        if match:
            add(findings, "error", "content.placeholder", path, message, line_of(text, match.start()))
    for pattern in LOCAL_PATH_PATTERNS:
        match = pattern.search(text)
        if match:
            add(
                findings,
                "error",
                "path.local-absolute",
                path,
                f"写死了本机绝对目录：{match.group(0)}；改成相对路径",
                line_of(text, match.start()),
            )


def check_html(path: Path, text: str, findings: list) -> None:
    title = TITLE_RE.search(text)
    if not title:
        add(findings, "error", "content.html-title", path, "HTML 没有 <title>，浏览器标签页会是空白的")
    elif not title.group(1).strip():
        add(findings, "error", "content.html-title", path, "<title> 是空的，写一句这东西是什么")
    if not META_VIEWPORT_RE.search(text):
        add(
            findings,
            "error",
            "content.viewport",
            path,
            "缺 <meta name=\"viewport\">，手机上会按桌面宽度缩放",
        )
    refs = [(m.group(1), m.start()) for m in ASSET_ATTR_RE.finditer(text)]
    refs += [(m.group(1), m.start()) for m in CSS_URL_RE.finditer(text)]
    for ref, index in refs:
        value = ref.strip()
        if not value or SKIP_ASSET_RE.match(value):
            continue
        if REMOTE_RE.match(value):
            add(
                findings,
                "info",
                "asset.remote",
                path,
                f"引用了外部资源 {value[:80]}；离线打开会缺失",
                line_of(text, index),
            )
            continue
        target = (path.parent / value.split("?")[0].split("#")[0]).resolve()
        if not target.exists():
            add(
                findings,
                "error",
                "asset.missing",
                path,
                f"引用的本地文件不存在：{value}",
                line_of(text, index),
            )


def check_svg(path: Path, text: str, findings: list) -> None:
    try:
        ET.fromstring(text)
    except ET.ParseError as exc:
        add(findings, "error", "svg.parse", path, f"SVG 解析不了：{exc}")
        return
    for match in re.finditer(r"""(?:href|xlink:href)\s*=\s*["']([^"']+)["']""", text, re.IGNORECASE):
        value = match.group(1).strip()
        if value.startswith("file:"):
            add(
                findings,
                "error",
                "svg.local-reference",
                path,
                f"SVG 里引用了本机文件 {value[:80]}；换成本机相对路径或内联",
                line_of(text, match.start()),
            )
        elif REMOTE_RE.match(value) and not value.startswith("#"):
            add(
                findings,
                "info",
                "asset.remote",
                path,
                f"SVG 引用了外部资源 {value[:80]}；离线打开会缺失",
                line_of(text, match.start()),
            )


def check_png(path: Path, findings: list) -> None:
    try:
        data = path.read_bytes()[:33]
    except OSError:
        add(findings, "error", "image.unreadable", path, "PNG 读不出来")
        return
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 26 or data[12:16] != b"IHDR":
        add(findings, "error", "image.signature", path, "文件头不是合法 PNG")
        return
    color_type = data[25]
    if color_type not in (4, 6):
        add(
            findings,
            "error",
            "image.no-alpha",
            path,
            "这张 PNG 没有透明通道；要当透明素材用就得重新导出带 alpha 的版本",
        )


def check_target(target: Path) -> list:
    findings: list = []
    if not target.exists():
        add(findings, "error", "target.missing", target, "路径不存在")
        return findings
    found_any = False
    for path in iter_files(target):
        suffix = path.suffix.lower()
        if suffix not in TEXT_SUFFIXES and suffix not in PNG_SUFFIXES:
            continue
        found_any = True
        if suffix in PNG_SUFFIXES:
            check_png(path, findings)
            continue
        text = read_text(path)
        if text is None:
            continue
        check_common_text(path, text, findings)
        if suffix in WEB_SUFFIXES:
            check_html(path, text, findings)
        elif suffix in SVG_SUFFIXES:
            check_svg(path, text, findings)
    if not found_any:
        add(
            findings,
            "info",
            "target.empty",
            target,
            "这里没有可检查的 HTML / CSS / JS / SVG / PNG 文件",
        )
    return findings


def cmd_check(args) -> int:
    findings: list = []
    for raw in args.paths:
        findings.extend(check_target(Path(raw)))
    errors = [item for item in findings if item["level"] == "error"]
    infos = [item for item in findings if item["level"] == "info"]
    if args.json:
        print(
            json.dumps(
                {"errors": len(errors), "notes": len(infos), "findings": findings},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1 if errors else 0
    if not findings:
        print("没有发现问题。")
        return 0
    for item in findings:
        where = f"{item['file']}:{item['line']}" if item["line"] else item["file"]
        mark = "阻断" if item["level"] == "error" else "提示"
        print(f"[{mark}] {where}\n    {item['message']}（{item['code']}）")
    print(f"\n阻断 {len(errors)} 项，提示 {len(infos)} 项。")
    if errors:
        print("有阻断项就先改再交付。")
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="design_check.py", description="设计产出自检")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="检查产物文件或目录")
    check.add_argument("paths", nargs="+", help="要检查的文件或目录")
    check.add_argument("--json", action="store_true", help="输出 JSON")
    check.set_defaults(func=cmd_check)
    return parser


def main(argv: list | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
