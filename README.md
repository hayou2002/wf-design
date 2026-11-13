# wf-design

把「想要好看」变成能交付的东西:先问清给谁看、在哪用,再挑一条车道,一路做到能看、能改、能交。

不懂设计的人做设计,卡的从来不是「不会画」,而是三件事:说不清自己要什么、不知道哪个工具干哪件事、做完不知道好不好。这条流程就解决这三件事。

## 怎么走

**底座(每趟都走)**:问清用途 → 定方向 → 做第一版 → 看一眼再改 → 交付自检

**车道(选一条)**:

| 车道 | 什么时候走 | 大概用到 |
| --- | --- | --- |
| 1 网页与界面 | 网站、落地页、App 界面、后台、组件,含交互与动效 | citycraft、oil-ui-pro、oil-frontend、oil-motion、web-design-guidelines |
| 2 HTML 文档与演示 | 给人看的 HTML 分享文档、16:9 幻灯片 | oil-html、oil-ppt、oil-tone |
| 3 图片、图标与插画 | 配图、解释图、透明插画、成套图标、徽章 | oil-visual、oil-icon、image-gen、beautify-github-readme |
| 4 正式文件 | Word、PDF、表格、要交给别人的演示文件 | 由插件提供的文档与演示能力 |

**先取舍再动手**:不是每条车道的每个技能每趟都用。开工先说清这次用哪几个、为什么不用其余几个。

## 交付前自检

```bash
py -3 scripts/design_check.py check <路径>
```

查漏掉的标题、残留的占位文字、指不到的图片、写死的本机路径、打不开的 SVG、不带透明通道的 PNG。退出码 1 = 有阻断项。

## 安装

```bash
npx skills add hayou2002/wf-design
```

## 依赖

车道里的技能按需安装,一个不装也能走底座(只是产出靠通用能力)。生图优先走 MCP 的生图通道,需要脚本入口时才用 `image-gen`,也可自配。

## 同系列

- [wf-maker](https://github.com/hayou2002/wf-maker):把流程做成工作流 Skill
- [wf-github-ops](https://github.com/hayou2002/wf-github-ops):本地 Git 整理与 GitHub 上传
- [wf-vibecode](https://github.com/hayou2002/wf-vibecode):日常 Vibe Coding

## 许可

MIT
