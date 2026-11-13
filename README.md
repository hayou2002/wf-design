# wf-design

![wf-design 工作流示意:四条车道,一次只走一条](assets/readme/hero.svg)

不懂设计也能做出像样的东西。这条流程只干三件事:**问清给谁看、选对工具、做完能自己判断好不好。**

## 怎么走

先走五步共同流程,再按要做的东西挑一条车道。五步是:问用途 → 定方向 → 做第一版 → 看着真实效果改 → 交付前自检。不铺开,先把最关键的一屏或一张做出来,检查过再继续。

## 四条车道,一次只走一条

- **网页与界面**:网站、落地页、界面、后台、组件,连交互和动效。整页要风格的用 citycraft 起步,界面与组件归 oil-ui-pro,交互落地归 oil-frontend,连续画面动效才动 oil-motion,最后按 web-design-guidelines 过一遍。
- **HTML 文档与演示**:给人看的分享文档、16:9 幻灯片。分享文档那套风格用户点名才用,幻灯片走 oil-ppt,文案交给 oil-tone。
- **图片、图标与插画**:配图、解释图、透明插画、成套图标、徽章。解释图与插画归 oil-visual,成套图标归 oil-icon,生图走 image-gen 或自配通道,仓库门面素材归 beautify-github-readme。
- **正式文件**:Word、PDF、表格、要交给别人的演示文件,用文档与演示插件。

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
