# 业务 Skill 统一骨架模板

每个业务 Skill 用同一套目录结构。`SKILL.md` 只放触发/路由/输入输出/流程约束，业务细节全部下沉到 `references/`，执行到哪一步才加载哪个文件，避免一次塞满上下文。

```
.agents/skills/<skill-name>/          # 注：本项目落地在 .claude/skills/
├── SKILL.md                 # 触发条件 + 路由 + 输入输出 + 流程约束（不含业务细节）
├── references/
│   ├── data-schema.md       # 输入/输出字段定义、类型、必填、枚举
│   ├── business-rules.md    # 该模块的业务规则、边界、判定条件
│   ├── scoring-rules.md     # 评分公式（仅评分类模块需要）
│   ├── source-map.md        # 数据源 → 字段映射、平台差异
│   ├── exceptions.md        # 异常/脏数据/失败处理
│   └── report-template.md   # 输出报告模板（趋势预警/机会清单等）
├── scripts/                 # 确定性数据处理、校验、报告生成（不进提示词）
├── evals/
│   └── evals.json           # 可执行测试用例
├── data/                    # JSONL 数据 + manifest 索引（支持切块）
└── feedback/
    ├── pending.jsonl        # 待处理问题
    ├── resolved.jsonl       # 已修复问题
    ├── self-review.jsonl    # AI/脚本自检发现
    └── changelog.md         # 版本变更记录
```

## SKILL.md 应包含的段落

1. `description`（frontmatter）：自然语言触发意图，写清楚「什么时候用、覆盖哪些意图」。
2. 触发与路由：如何判断进入本 Skill。
3. 输入：需要什么材料，缺什么先问。
4. 输出：产出什么、什么格式、写到哪。
5. 流程约束：按什么顺序执行、哪些步骤必须校验。
6. 硬约束：禁止做什么、什么情况转 `needs-developer` / `needs-business`。

## 生成规则

- 每个模块只负责一件事；跨模块依赖写清，不复制规则。
- `references/` 只写「何时读取哪个文件」的路由，不在 SKILL.md 里堆业务规则。
- 脚本处理一切可确定的部分（校验、清洗、格式转换、报告生成），模型只做需要判断的部分。
- 每个 Skill 生成后立即配 `evals/evals.json`，含正常/边界/异常/数据质量四类场景。
