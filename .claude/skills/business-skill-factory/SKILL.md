---
name: business-skill-factory
description: >-
  元 Skill / Skill 工厂。当用户想把一份业务 SOP、业务文档或工作流程，生成、拆分、测试、
  迭代成一组可自检、可追溯、延迟修复的模块化 Skill 时使用。覆盖「收集材料 → 判断切块 →
  生成模块化 Skill → 运行 → 自检 → 记录反馈 → 按需延迟批量修复」。触发意图示例：生成选品 Skill、
  根据这份文档创建 Skill、把这个 SOP 拆成 Skill、修复问题、处理反馈、统一优化、根据测试结果更新、
  发布新版本。
---

# business-skill-factory

把一份业务 SOP 变成一组模块化业务 Skill。本 Skill 是「元层」，不执行具体业务，只负责生成与迭代下面的业务 Skill。

## 触发与路由

靠用户自然语言意图判定，两类意图：

1. **生成意图**：`生成/创建/拆分 Skill`、`根据这份 SOP/文档产出 Skill`
   → 走「收集材料 → 分析切块 → 生成 Skill」流程。
2. **迭代意图**：`修复问题`、`处理反馈`、`统一优化`、`根据测试结果更新`、`发布新版本`
   → 走「汇总问题 → 归因 → 修改 → 回归测试 → 发版」流程。

默认行为是**记录优先、不即时改**。仅当用户出现上述明确意图才启动迭代；其余情况只记录，不改动正式 Skill。

## 输入（生成时索取，缺一即先问）

- 业务 SOP / 业务文档
- 数据源说明（平台、字段、权限）
- 目标类目 / 市场 / 站点
- 评分规则与输出模板
- 现有代码 / 数据库 / 接口 / 爬虫
- 已知限制（不可抓取数据、频率限制、人工审核节点）

## 生成流程

1. 读业务文档，按 [chunking-rules.md](references/chunking-rules.md) 判断是否切块、怎么切。
2. 按 [skill-template.md](references/skill-template.md) 生成每个业务 Skill 的统一骨架。
3. 生成脚本、测试用例（`evals/evals.json`）、feedback 占位文件。
4. 运行结构测试 + 数据测试 + 业务场景测试。

## 迭代流程（延迟修复）

仅当用户明确要求修复时执行：

1. 汇总各 Skill `feedback/*.jsonl` 中的全部问题。
2. 去重、分类（见 [issue-taxonomy.md](references/issue-taxonomy.md)）。
3. 逐条归因：改数据 / 规则 / 提示词 / 脚本 / 测试。
4. 生成修改计划 → 修改 → 补回归测试 → 运行 → 产出 release-manifest 与 changelog。

## 硬约束

- 不编造业务规则。文档未定义 → 标记「待业务确认」，不擅自补全。
- 只在低风险、有明确依据时自动改 Skill；爬虫 / API / 数据库 / 口径未定义 / 多次复现 → 转 `needs-developer`。
- 编排 Skill 不重复领域业务规则，只做调度与状态传递。
- 每次生成或迭代后记录：Skill 版本、文档版本、数据 schema 版本、关联反馈/自检编号、修改文件、变更原因、新增测试、测试结果、待业务确认项。

## 版本与协作（问题记录 + GitHub 分支）

每次 Skill 修改都走 git 分支，问题统一进中央问题库。详见 [git-release-workflow.md](references/git-release-workflow.md)。

- 记录问题：`python scripts/record_issue.py --module <skill> --summary "..." --source <source> --severity <sev> [--status <status>]`
- 提交发版：`python scripts/release.py --message "..." --issues FB-001,AI-002 [--bump patch]`（默认 push，`--no-push` 跳过）

问题库在仓库根 `issues/`（pending / needs-business / needs-developer / resolved），
release-manifest 在 `releases/<version>/`，两者通过 `git_commit` 关联，保证开发者能沿用户分支定位每一次改动。
