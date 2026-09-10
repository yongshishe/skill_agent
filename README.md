# 选品 Skill 工厂

把一套电商选品 SOP 变成可自检、可追溯、延迟修复的模块化 Skill。每次改动都落 git 分支并同步 GitHub，开发者可直接沿用户分支对齐、减少沟通成本。

## 一、怎么调用（自然语言意图触发）

这套 Skill 不靠命令，靠 `SKILL.md` 的 `description` 做自然语言意图路由。

| 想做什么 | 直接说（示例） | 触发 |
|---|---|---|
| 采集竞品数据 | 「采集宠物饮水机的竞品 SKU、价格、评分」 | `competitor-data-collector` |
| 监控趋势 | 「监控价格带迁移、功能词热度、品类热度」 | `market-trend-monitor` |
| 生成选品机会 | 「汇总周度选品机会清单、竞争度分析、找空白价格带」 | `product-opportunity-ranking` |
| 生成 / 拆分 Skill | 「根据这份 SOP 生成选品 Skill」 | `business-skill-factory` |
| 修复 / 优化 | 「修复问题」「处理反馈」「统一优化」 | `business-skill-factory` |

## 二、调用顺利流程（happy path）

以「采集」为例：

1. 说「采集宠物饮水机的竞品数据」。
2. collector 读 `references/data-schema.md` 标准化字段，写 `data/<版本>/chunk-*.jsonl` + `data/manifest.json`。
3. collector 自动跑 `scripts/validate.py` 数据自检，结果追加进 `feedback/self-review.jsonl`。
4. 无阻断问题 → 产出标准化数据集，交给下游（聚类 / 趋势 / 机会评分）。
5. 说「监控价格带迁移、功能词热度、品类热度」→ `market-trend-monitor` 跑 `scripts/analyze_trends.py`，产出《趋势预警》。
6. 说「汇总周度选品机会清单」→ `product-opportunity-ranking` 跑 `scripts/rank_opportunities.py`，产出四要素机会清单。

已跑通：采集（旅行包 15 条 SKU）→ 趋势 → 机会 三段链路。

## 三、出错 → 记录 → 修复 → 发版 流程

核心：**记录优先、不即时改**。

1. 出错（用户反馈 or AI 自检）→ `record_issue.py` 记录到中央 `issues/`，自动带分支 + commit。
2. 只有用户说「修复问题」才启动修复。
3. 问题先分类再改（见 `issue-taxonomy.md`）：数据 / 规则 / 提示词 / 脚本 / 测试各走各的改法；爬虫 / API / 口径未定义 → `needs-developer`。
4. 改完回归 → `release.py` 提交 + 生成 release-manifest + 更新 CHANGELOG。

## 四、保存到 GitHub 流程

1. 仓库已在项目根 `git init`，remote = `origin`（`https://github.com/yongshishe/skill_agent.git`）。
2. 每次改动：`release.py`（默认 push）→ 自动开 `user/*` 分支 → commit → push。
3. 开发者 `git fetch` + `git diff main...user/<分支>` 即可看到改动全貌，读 manifest + issues 对齐。

## 五、命令速查

```bash
# 记录一条问题（不修改；会自动开 user/<日期>-<问题> 分支，分支名标注问题）
python .claude/skills/business-skill-factory/scripts/record_issue.py \
  --module competitor-data-collector --summary "价格带错了" \
  --source user_feedback --severity medium --slug price-band-wrong [--status needs-developer]

# 数据自检
python .claude/skills/competitor-data-collector/scripts/validate.py

# 趋势分析（读采集数据 →《趋势预警》）
python .claude/skills/market-trend-monitor/scripts/analyze_trends.py

# 机会评分（读采集数据 →《周度选品机会清单》）
python .claude/skills/product-opportunity-ranking/scripts/rank_opportunities.py

# 发版 + 推送 GitHub（默认 push，--no-push 跳过）
python .claude/skills/business-skill-factory/scripts/release.py \
  --message "fix: ..." --issues AI-xxx
```

## 六、目录结构

```
.claude/skills/
├── business-skill-factory/          # 元 Skill：生成/迭代 + 问题记录 + 发版
│   ├── SKILL.md
│   ├── references/                  # skill-template / chunking-rules / issue-taxonomy / git-release-workflow
│   └── scripts/                     # record_issue.py / release.py
├── competitor-data-collector/       # 领域 Skill：采集
│   ├── SKILL.md
│   ├── references/                  # data-schema / source-map / business-rules / exceptions
│   ├── scripts/validate.py          # 数据质量自检
│   ├── data/                        # JSONL + manifest
│   └── feedback/                    # 自检/反馈记录
├── market-trend-monitor/            # 领域 Skill：趋势（价格带/功能词/品类热度）
│   ├── SKILL.md
│   ├── references/                  # business-rules / report-template / exceptions
│   ├── scripts/analyze_trends.py    # 趋势分析 →《趋势预警》
│   └── data/  feedback/
└── product-opportunity-ranking/     # 领域 Skill：机会（四要素选品机会清单）
    ├── SKILL.md
    ├── references/                  # business-rules / scoring-rules / report-template / exceptions
    ├── scripts/rank_opportunities.py # 机会评分 →《周度选品机会清单》
    └── data/  feedback/

issues/                              # 中央问题库（pending/needs-business/needs-developer/resolved）
releases/<version>/release-manifest.json
CHANGELOG.md
```

## 七、问题状态机

```
pending → auto-fixable / needs-business / needs-developer → resolved
```

- `auto-fixable`：改规则/脚本/测试能解决。
- `needs-developer`：爬虫/API/数据库/权限等，AI 不自动改，转开发者工单。
- `needs-business`：评分口径/字段含义未定义，待业务确认。
