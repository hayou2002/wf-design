#!/usr/bin/env python3
"""AI-facing Bilibili search and subtitle tool with Windows credential storage."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http.cookiejar import CookieJar
from pathlib import Path

from credentials import delete_session, load_session, save_session


ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / ".vendor"
CACHE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "codex" / "wf-design" / "tools" / "bilibili-skill"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
RETRY_CODES = {-352, -412, -799}


class BiliError(RuntimeError):
    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status


def request_json(url: str, *, cookies: dict | None = None, jar: CookieJar | None = None, attempts: int = 3) -> dict:
    headers = {"User-Agent": USER_AGENT, "Referer": "https://www.bilibili.com/"}
    if cookies:
        headers["Cookie"] = "; ".join(f"{name}={value}" for name, value in cookies.items())
    handlers = [urllib.request.ProxyHandler({})]
    if jar is not None:
        handlers.append(urllib.request.HTTPCookieProcessor(jar))
    opener = urllib.request.build_opener(*handlers)
    for attempt in range(attempts):
        try:
            with opener.open(urllib.request.Request(url, headers=headers), timeout=20) as response:
                payload = json.load(response)
            if payload.get("code") in RETRY_CODES and attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
                continue
            return payload
        except (TimeoutError, urllib.error.URLError) as exc:
            if attempt + 1 >= attempts:
                raise BiliError("network_error", f"请求失败：{exc}") from exc
            time.sleep(1.5 * (attempt + 1))
    raise BiliError("network_error", "请求重试次数已用尽")


def require_ok(payload: dict) -> dict:
    if payload.get("code") != 0:
        raise BiliError("api_error", f"B 站接口返回 {payload.get('code')}：{payload.get('message', '未知错误')}")
    return payload.get("data") or {}


def current_session() -> dict:
    session = load_session()
    if not session or not session.get("cookies", {}).get("SESSDATA"):
        raise BiliError("login_required", "尚未登录，请运行 login")
    return session


def emit(payload: dict, as_json: bool) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def qr_image(content: str, path: Path) -> None:
    sys.path.insert(0, str(VENDOR))
    try:
        import qrcode
    except ImportError as exc:
        raise BiliError("dependency_missing", "缺少二维码依赖；请先运行工具安装说明") from exc
    image = qrcode.make(content, border=4, box_size=10)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def command_login(args: argparse.Namespace) -> dict:
    jar = CookieJar()
    data = require_ok(request_json("https://passport.bilibili.com/x/passport-login/web/qrcode/generate", jar=jar))
    key = data["qrcode_key"]
    image_path = CACHE / "login-qr.png"
    qr_image(data["url"], image_path)
    if args.open:
        os.startfile(str(image_path))
    print(f"请用哔哩哔哩 App 扫码并确认：{image_path}", flush=True)
    deadline = time.time() + 175
    while time.time() < deadline:
        payload = request_json(
            "https://passport.bilibili.com/x/passport-login/web/qrcode/poll?" + urllib.parse.urlencode({"qrcode_key": key}),
            jar=jar,
            attempts=4,
        )
        status = payload.get("data", {}).get("code")
        if status == 86090:
            print("已扫码，请在手机上确认。", flush=True)
        elif status == 86038:
            raise BiliError("qr_expired", "二维码已失效，请重新运行 login")
        elif status == 0:
            cookies = {cookie.name: cookie.value for cookie in jar}
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(payload["data"].get("url", "")).query)
            for name in ("SESSDATA", "bili_jct", "DedeUserID", "DedeUserID__ckMd5"):
                if name in query:
                    cookies[name] = query[name][0]
            save_session({"cookies": cookies, "refresh_token": payload["data"].get("refresh_token", "")})
            if not load_session():
                raise BiliError("credential_error", "Windows 凭据回读失败")
            return {"status": "authenticated", "credential_store": "Windows Credential Manager"}
        time.sleep(3)
    raise BiliError("qr_timeout", "等待扫码超时，请重新运行 login")


def command_auth_status() -> dict:
    session = load_session()
    if not session:
        return {"saved": False, "valid": False, "status": "login_required"}
    try:
        data = require_ok(request_json("https://api.bilibili.com/x/web-interface/nav", cookies=session["cookies"]))
    except BiliError as exc:
        return {"saved": True, "valid": False, "status": exc.status}
    return {
        "saved": True,
        "valid": bool(data.get("isLogin")),
        "status": "authenticated" if data.get("isLogin") else "session_expired",
        "user": data.get("uname") if data.get("isLogin") else None,
        "uid": data.get("mid") if data.get("isLogin") else None,
    }


def normalize_video(item: dict) -> dict:
    published = item.get("pubdate")
    return {
        "bvid": item.get("bvid"),
        "title": html.unescape(re.sub(r"<[^>]+>", "", item.get("title", ""))),
        "description": item.get("description", ""),
        "uploader": item.get("author") or item.get("owner", {}).get("name"),
        "uploader_mid": item.get("mid") or item.get("owner", {}).get("mid"),
        "duration": item.get("duration"),
        "published_at": datetime.fromtimestamp(published, timezone.utc).isoformat() if published else None,
        "views": item.get("play") or item.get("stat", {}).get("view"),
        "url": f"https://www.bilibili.com/video/{item.get('bvid')}/",
    }


def command_search(args: argparse.Namespace) -> dict:
    params = {"search_type": "video", "keyword": args.query, "page": 1, "order": args.order}
    data = require_ok(request_json("https://api.bilibili.com/x/web-interface/search/type?" + urllib.parse.urlencode(params)))
    items = [normalize_video(item) for item in data.get("result", []) if item.get("type") == "video"]
    if args.uploader_mid:
        items = [item for item in items if str(item["uploader_mid"]) == str(args.uploader_mid)]
    if args.uploader:
        needle = args.uploader.casefold()
        items = [item for item in items if needle in (item["uploader"] or "").casefold()]
    return {
        "query": args.query,
        "count": len(items[:args.limit]),
        "search_scope": "first_result_page",
        "result_note": "0 条只表示当前关键词第一页未命中；可换关键词、缩短关键词或改用 UP 主视频列表。" if not items else None,
        "uploader_filter": args.uploader_mid or args.uploader,
        "results": items[:args.limit],
    }


def parse_bvid(value: str) -> str:
    match = re.search(r"BV[0-9A-Za-z]{10}", value)
    if not match:
        raise BiliError("invalid_video", "请输入 BV 号或包含 BV 号的视频链接")
    return match.group(0)


def command_info(args: argparse.Namespace) -> dict:
    data = require_ok(request_json("https://api.bilibili.com/x/web-interface/view?" + urllib.parse.urlencode({"bvid": parse_bvid(args.video)})))
    result = normalize_video(data)
    result["pages"] = [{"page": page.get("page"), "part": page.get("part"), "cid": page.get("cid"), "duration": page.get("duration")} for page in data.get("pages", [])]
    return result


def command_subtitles(args: argparse.Namespace) -> dict:
    bvid = parse_bvid(args.video)
    info = command_info(argparse.Namespace(video=bvid))
    page = next((item for item in info["pages"] if item["page"] == args.part), None)
    if not page:
        raise BiliError("invalid_part", f"视频没有第 {args.part} P")
    cache_key = hashlib.sha256(f"{bvid}:{page['cid']}:{args.language or 'auto'}".encode()).hexdigest()[:24]
    cache_file = CACHE / "subtitles" / f"{cache_key}.json"
    if not args.refresh and cache_file.exists() and time.time() - cache_file.stat().st_mtime < 86400:
        cached = json.loads(cache_file.read_text(encoding="utf-8"))
        cached["cache"] = {"hit": True, "path": str(cache_file)}
        return cached
    session = current_session()
    player = require_ok(request_json(
        "https://api.bilibili.com/x/player/wbi/v2?" + urllib.parse.urlencode({"bvid": bvid, "cid": page["cid"]}),
        cookies=session["cookies"],
    ))
    tracks = player.get("subtitle", {}).get("subtitles", [])
    if not tracks:
        status = "login_required" if player.get("need_login_subtitle") else "no_subtitles"
        return {"status": "unavailable", "reason": status, "video": info, "part": page}
    candidates = [track for track in tracks if not args.language or args.language.casefold() in {str(track.get("lan", "")).casefold(), str(track.get("lan_doc", "")).casefold()}]
    if not candidates:
        return {"status": "unavailable", "reason": "language_unavailable", "video": info, "part": page, "available": [{"lan": track.get("lan"), "name": track.get("lan_doc")} for track in tracks]}
    track = next(
        (item for item in candidates if item.get("lan") == "zh-Hans"),
        next((item for item in candidates if not str(item.get("lan", "")).startswith("ai-") and not item.get("ai_type")), candidates[0]),
    )
    url = track.get("subtitle_url", "")
    if url.startswith("//"):
        url = "https:" + url
    subtitle = request_json(url, cookies=session["cookies"])
    body = subtitle.get("body")
    if not isinstance(body, list):
        raise BiliError("subtitle_download_failed", "字幕响应缺少 body")
    segments = [{"from": item.get("from"), "to": item.get("to"), "text": item.get("content", "")} for item in body]
    result = {
        "status": "ok",
        "video": info,
        "part": page,
        "subtitle": {"lan": track.get("lan"), "name": track.get("lan_doc"), "kind": "ai" if str(track.get("lan", "")).startswith("ai-") or track.get("ai_type") else "human_or_unmarked", "segments": len(segments)},
        "text": "\n".join(item["text"] for item in segments),
        "segments": segments,
        "cache": {"hit": False, "path": str(cache_file)},
    }
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="wf-design 的 B 站检索与字幕工具")
    parser.add_argument("--json", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)
    login = subparsers.add_parser("login")
    login.add_argument("--no-open", dest="open", action="store_false", help="不自动打开二维码图片")
    subparsers.add_parser("auth-status")
    subparsers.add_parser("logout")
    for name in ("auth-status", "logout", "login"):
        subparsers.choices[name].add_argument("--json", action="store_true")
    search = subparsers.add_parser("search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--order", choices=("totalrank", "click", "pubdate", "dm", "stow"), default="totalrank")
    search.add_argument("--uploader")
    search.add_argument("--uploader-mid", type=int)
    search.add_argument("--json", action="store_true")
    info = subparsers.add_parser("info")
    info.add_argument("video")
    info.add_argument("--json", action="store_true")
    subtitles = subparsers.add_parser("subtitles")
    subtitles.add_argument("video")
    subtitles.add_argument("--part", type=int, default=1)
    subtitles.add_argument("--language")
    subtitles.add_argument("--refresh", action="store_true")
    subtitles.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "login":
            result = command_login(args)
        elif args.command == "auth-status":
            result = command_auth_status()
        elif args.command == "logout":
            result = {"deleted": delete_session()}
        elif args.command == "search":
            if not 1 <= args.limit <= 20:
                raise BiliError("invalid_limit", "--limit 必须在 1 到 20 之间")
            result = command_search(args)
        elif args.command == "info":
            result = command_info(args)
        else:
            result = command_subtitles(args)
        emit(result, True)
        return 0
    except (BiliError, RuntimeError) as exc:
        emit({"status": getattr(exc, "status", "error"), "message": str(exc)}, True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

