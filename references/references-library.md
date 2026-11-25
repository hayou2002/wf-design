# 参考资源索引

只在阶段 2 确实需要外部参考时读取。按真实任务选来源，不全量浏览；参考检索不是每个设计任务的必经步骤。

## 四种资源不要混淆

| 类型 | 用途 | 当前边界 |
| --- | --- | --- |
| 本地能力 Skill | 提供设计方法、工程规则或专项验收 | 已安装不等于每步都用；由主流程按需调用 |
| 在线参考与接口 | 按任务搜索、选择并读取设计提示词、规范或素材 | 只读取选中条目；接口、费用和权限须先核实 |
| 本地适配器 | 为特定官方来源提供发现、索引、验证或预览 | 当前仅有 Ant Design、APG、React Bits、DESIGN.md 四个试点 |
| 仅链接来源 | 提供人工或 AI 的按需参考 | 未接入、未验证或受限，不声称已经可程序化调用 |

OpenDesign 等在线库的目标使用方式是“搜索 → 选择 → 读取/下载选中条目 → 记录来源与许可”，不是整库镜像。OpenDesign 的真实按需接口与额度尚未核实，当前不得写成已接入能力。

## AI 先检索具体问题

```bash
py -3 <design-reference-library>/scripts/search_references.py "数据表格 筛选 批量操作" --json
py -3 <design-reference-library>/scripts/search_references.py "抽屉和弹窗怎么选" --json
```

优先返回具体设计模式、选择规则、验收点和官方示例；未命中时才返回候选来源，由 AI 继续查具体内容。默认用 `--json`，只向用户呈现最相关的 1–2 条及选择理由，不转发目录、整份 JSON 或库名列表。

## 参考顺序

1. 真实项目、现有设计体系、源码、数据与组件。
2. 官方源码、官方示例和版本对应文档；技术文档可按需使用 Context7。
3. 已核实的本地适配器与参考条目。
4. Oil Book 的实战经验与原始资料导航。
5. 其他公开组件库、设计网站与本地 Oil 资源。
6. 无法取得源码时的截图与视觉推断，必须标明只是推断。

可下载源码只读分析，不自动执行第三方脚本。搜索入口与证据质量分开：优先定位官方原页，二手文章只作线索。

## 重点知识与经验

| 资源 | 适合参考 | 使用边界 |
| --- | --- | --- |
| [Oil Book：AI UI 设计](https://book.oiloil.org/articles/ai-ui-design) | 设计认知、参考筛选、真实截图评审与风格形成 | 方法参考，不代替当前项目事实 |
| [Oil Book：长期开发复杂项目](https://book.oiloil.org/articles/agent-long-project-management) | 里程碑、并行分工、规范沉淀、测试与发版治理 | 作者实战复盘，不直接当普遍规则 |
| [Oil Book：Vibe Coding 从零做网站](https://book.oiloil.org/articles/vibe-coding-website-from-scratch) | 从定位、视觉方向到真实网站上线的完整过程 | 个人网站案例，复杂业务需另做闭环 |
| [Oil Book：长周期应用 Harness](https://book.oiloil.org/articles/harness-design-long-running-apps) | 把审美与真实浏览器操作变成验收标准 | 关键技术结论回到原始出处 |
| [VibeHub](https://vibe-hub.org) | 设计、交互、开发与 Agent 术语的认知补全 | 词典不是设计系统；只链接真实匹配词条 |

## 本地优先

| 资源 | 适合参考 | 呈现方式 |
| --- | --- | --- |
| 项目现有设计体系 | 存量产品、品牌和组件 | 直接沿用，不重新找风格 |
| design-reference-library | 具体组件、交互模式、选择规则与官方示例 | AI 检索并筛选最相关结果 |
| oil-ui-pro | 后台、数据密集工作区、交互状态与规范 | 按领域读取对应入口 |
| oil-art-landing | 艺术感品牌官网、多屏落地页 | 按本地目录选择锚点 |

## 外部参考状态

| 资源 | 当前使用方式 | 未解决边界 |
| --- | --- | --- |
| Ant Design、APG、React Bits、DESIGN.md | 使用已有本地适配器与各自查询/验证入口 | APG 预览仍可能受限；DESIGN.md 无专属官方预览 |
| OpenDesign | 目标为在线按需检索与读取 | 接口、登录、额度与价格未核实，不接为事实能力 |
| Carbon、assistant-ui、Ant Design X | 调研发现官方 Skill/MCP/CLI 候选 | 尚未安装或接入；使用前重新核实费用与凭据 |
| Aceternity、Uiverse、Anime.js、Base UI、Motion、Open Props | 按任务参考官方文档、归档或公开接口 | 不把调研候选当本地能力；许可与免费/Pro 范围分开 |
| MotionSites、Showreel | 仅链接参考 | 付费、授权或 robots 限制，不缓存受限提示词、视频或帧 |

需要查看完整调研证据时，读项目工作区的候选报告，不把调研总表直接交给设计用户。

## 预览与许可

1. 优先官方已有预览并记录来源与许可。
2. 公开演示或本地页面可用确定性浏览器脚本截图。
3. 有源码无预览时，只有确实必要才在隔离环境运行。
4. 需要登录、付费、授权不明或接入成本过高的来源，及时止损，只保留链接。
5. 无可靠预览时只保留文字参考，不用 AI 伪造界面截图。

参考结构、决策依据可以学习；不复制品牌、专有素材或整页设计。`oil-art-landing` 负责视觉锚点，`oil-showcase` 只把已核实的真实素材编成展示材料。

## 参考库维护

只有用户明确要求扩充或修正参考库时才进行，不在普通设计任务中顺手抓网站。

- 优先官方 Skill、MCP、CLI、API、registry、现成索引，再考虑成熟社区工具；不默认自写爬虫。
- 新来源先确认任务分类、调用契约、费用、许可与止损条件，再决定是否接入。
- 复杂抓取、特殊页面结构和稳定截图需求不构成继续开发的理由；已有链接能满足参考时停止。
- 新增或替换来源修改参考目录的登记，不重写 `wf-design` 主流程。

## 视频经验

视频是按需参考，不是必经步骤。记录 UP 主、标题、BV 号、原始链接、与当前任务的关系、字幕来源、获取日期和是否完整阅读。

```bash
py -3 <wf-design>/tools/bilibili-skill/bili.py search "Vibe Coding" --uploader-mid 13030183 --json
py -3 <wf-design>/tools/bilibili-skill/bili.py subtitles "BV19DySz4EQF" --json
```

使用本工作流的 `tools/bilibili-skill/bili.py`，不是另建设计 Skill。人工字幕优先，AI 字幕明确标注；没有可靠字幕时保留链接与缺失原因，不根据标题补写观点。Cookie 仅从 Windows 凭据管理器读取，不写入工作流、仓库、日志或交接材料。
