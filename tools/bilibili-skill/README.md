# B 站检索工具

`justinzm/bilibili_skill` 的安全改造版，供 `wf-design` 在确实需要视频经验时调用，不是独立 Skill。

## 登录

```bash
py -3 tools/bilibili-skill/bili.py login --json
py -3 tools/bilibili-skill/bili.py auth-status --json
```

二维码自动打开；扫码确认后，Cookie 与刷新令牌仅存入 Windows 凭据管理器 `codex/bilibili-research/session`。不要手动复制 Cookie，也不要将 Cookie 写入本项目。

二维码依赖已放在 `.vendor/qrcode`，保留其 BSD 许可证；图像由本机 Pillow 生成，未使用第三方账号服务。

## 检索与字幕

```bash
py -3 tools/bilibili-skill/bili.py search "Vibe Coding 复杂项目" --limit 5 --json
py -3 tools/bilibili-skill/bili.py search "Vibe Coding" --uploader-mid 13030183 --json
py -3 tools/bilibili-skill/bili.py info "BV19DySz4EQF" --json
py -3 tools/bilibili-skill/bili.py subtitles "BV19DySz4EQF" --json
```

- 搜索支持 UP 主名称或 MID 筛选，不能只看播放量决定相关性。
- 多 P 视频用 `--part N`，字幕按对应 CID 获取。
- 人工字幕优先；`subtitle.kind=ai` 时必须向用户标明是 AI 字幕。
- 字幕缓存位于 `%LOCALAPPDATA%\codex\wf-design\tools\bilibili-skill\subtitles`，不含 Cookie。
- 无字幕、登录失效、权限受限和网络错误分别报告；不根据标题补写视频内容。
- 不自动下载音视频、不转写、不绕过付费墙或访问限制。

`logout` 仅删除本工具保存的 Windows 凭据。

## 与上游的区别

上游仓库：`https://github.com/justinzm/bilibili_skill`，核对提交 `70933b0635f5143833fb6cf8d2c882205d0f2392`。

这里只借鉴其“需求 → 视频搜索 → 字幕 → AI 筛选”的思路，未复制其要求把 Cookie 写入 `config.py` 的方式。补充了扫码登录、Windows 凭据、超时重试、UP 主筛选、多 P 支持和真实缓存。

工具自身的 `LICENSE` 为 MIT；上游许可证声明与实际 LICENSE 文件需继续核对，不能据此批量再分发上游代码。
