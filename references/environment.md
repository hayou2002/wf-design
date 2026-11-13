# wf-design 环境清单

> 由 wf-maker 生成，请勿手改；要改就改 `sources.json` 后重跑 `wf.py env`。

更新时间：2026-11-13

## 技能依赖

| 技能 | 关系 | 来源 | 安装方式 |
| --- | --- | --- | --- |
| beautify-github-readme | 引用 | GitHub oil-oil/beautify-github-readme › skills/beautify-github-readme | npx skills add oil-oil/beautify-github-readme --skill beautify-github-readme |
| citycraft | 引用 | GitHub oil-oil/citycraft | npx skills add oil-oil/citycraft |
| documents | 只写步骤 | 插件 documents | 安装插件 documents |
| image-gen | 引用 | 本机目录 | 随本机技能目录同步（无上游仓库） |
| kdocs | 只写步骤 | GitHub kdocs-app/kdocs-skill | npx skills add kdocs-app/kdocs-skill |
| oil-frontend | 引用 | GitHub oil-oil/oil-frontend | npx skills add oil-oil/oil-frontend |
| oil-html | 引用 | GitHub oil-oil/oil-html | npx skills add oil-oil/oil-html |
| oil-icon | 引用 | GitHub oil-oil/oil-icon | npx skills add oil-oil/oil-icon |
| oil-motion | 引用 | GitHub oil-oil/oil-motion | npx skills add oil-oil/oil-motion |
| oil-ppt | 引用 | GitHub oil-oil/oil-ppt › oil-ppt | npx skills add oil-oil/oil-ppt --skill oil-ppt |
| oil-tone | 引用 | GitHub oil-oil/oil-tone › skills/oil-tone | npx skills add oil-oil/oil-tone --skill oil-tone |
| oil-ui-pro | 引用 | 本机目录 | 随本机技能目录同步（无上游仓库） |
| oil-visual | 引用 | GitHub oil-oil/oil-visual | npx skills add oil-oil/oil-visual |
| pdf | 只写步骤 | 插件 pdf | 安装插件 pdf |
| presentations | 只写步骤 | 插件 presentations | 安装插件 presentations |
| spreadsheets | 只写步骤 | 插件 spreadsheets | 安装插件 spreadsheets |
| web-design-guidelines | 引用 | GitHub oil-oil/agent-skills › skills/web-design-guidelines | npx skills add oil-oil/agent-skills --skill web-design-guidelines |

## 凭据与配置

本清单不记录任何密钥值。需要你自行准备的项目：

- image-gen：默认无：走 MCP 的 magpie-image，不用另配 Key；也可以自己配置生图服务（自选）
- oil-icon：默认无：生图走 MCP 的 magpie-image；也可以自己配置（自选），技能自带的 Key 配置页只在通道缺失时才用
- oil-motion：ZenMux API Key（图片与视频共用）；首次生成前由本机配置页写入系统凭据库，不写在文件里

## 恢复步骤

1. 按上表逐项安装或确认技能已就位。
2. 用 `wf.py check <工作流>` 核对每个技能的版本是否和登记时一致。
3. 凭据按「凭据与配置」一节自行准备，不要写进本目录。
