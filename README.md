# wf-design

![wf-design 工作流示意:选择参考,确认样板,再完整制作](assets/readme/hero.svg)

不懂设计也能参与设计：先明确任务与设计契约，再确认关键样板，复杂项目按切片制作和审查。工作流负责组织技能、交接和确认点，具体方法留在各技能本体。

## 怎么走

共同流程是:明确任务 → 核验事实与参考 → 设计契约 → 方向样板 → 制作与验收。复杂项目增加真实垂直切片、逐片审查与集成验收；小改、已有参考或已有设计体系时不重复走全程。全新视觉方向按需比较候选，不固定数量。

## 内置 SOP

笔记整理沿用独立 SOP 和分档，不走视觉参考流程。视觉设计按产物组织技能，具体场景 SOP 只补真正需要偏离底座的部分。

- [SOP 索引](references/sops/index.md)
- [笔记整理](references/sops/note-organization.md)

## 按产物组织

- **办公文档**:Word、PDF、PPT 与在线协作文档。
- **进阶应用**:网页、移动 App、桌面应用。
- **细节模块**:界面模块、图片、交互与交互动画。
- **视频**:连续镜头和 AI 视频，与交互动画分开。

**先取舍再动手**:不是每个技能每趟都用。简单任务只报当前环节、状态和下一步；复杂任务再展示阶段产物与子 Agent 分工。

## 交付前自检

```bash
py -3 scripts/design_check.py check <路径>
```

查漏掉的标题、残留的占位文字、指不到的图片、写死的本机路径、打不开的 SVG、不带透明通道的 PNG。笔记另有 `note_check.py`。两个脚本都以一行「结论」收尾:退出码 1(命中)就是有阻断项,先改再交。

## 安装

```bash
npx skills add hayou2002/wf-design
```

## 依赖

技能按需安装,一个不装也能走底座(只是产出靠通用能力)。生图优先走 MCP 的生图通道,需要脚本入口时才用 `image-gen`,也可自配。

笔记整理写入思源时,需要本机思源正在运行。端口从 `~/.config/siyuan/port.json` 读取,访问码从工作区 `conf/conf.json` 的 `accessAuthCode` 读取;也可以用 `SIYUAN_PORT`、`SIYUAN_TOKEN` 覆盖。脚本不会打印访问码。

## 同系列

- [wf-maker](https://github.com/hayou2002/wf-maker):把流程做成工作流 Skill
- [wf-github-ops](https://github.com/hayou2002/wf-github-ops):本地 Git 整理与 GitHub 上传
- [wf-vibecode](https://github.com/hayou2002/wf-vibecode):日常 Vibe Coding

## 许可

MIT
