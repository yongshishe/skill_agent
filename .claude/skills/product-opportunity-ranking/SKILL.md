---
name: product-opportunity-ranking
description: >-
  选品机会评分 Skill。当用户想要基于竞品数据汇总《周度选品机会清单》，给每个机会标注
  创新分、竞争度、可解释场景、契合现有货号时使用。触发意图示例：生成选品机会、周度选品清单、
  机会评分、找空白价格带、竞争度分析、选品建议。
---

# product-opportunity-ranking

基于竞品价格带与竞争密度，汇总《周度选品机会清单》。每个机会标注四要素：创新分 / 竞争度 / 可解释场景 / 契合现有货号。

## 触发与路由

自然语言意图判定。当用户表达「选品机会 / 机会清单 / 竞争度 / 空白价格带」时进入本 Skill。

执行顺序：

1. 读上游 collector 数据（价格带 → 竞争密度）。
2. 跑 `scripts/rank_opportunities.py` 识别真空带 / 稀疏带机会。
3. 按 [scoring-rules.md](references/scoring-rules.md) 给机会打四要素。
4. 按 [report-template.md](references/report-template.md) 输出清单。

## 输入

- 上游标准化 SKU 数据集。
- 可选：现有货号目录（用于「契合现有货号」比对）。

## 输出

- 机会清单：`data/opportunity-list-<data_version>.json`
- 报告索引：`data/manifest.json`

## 流程约束

- 竞争度由价格带密度可算；创新分、契合现有货号需要业务口径/货号表，缺则置 `needs_business`，不编造。
- 每个机会必须能追溯到价格带计数与具体 SKU。

## 硬约束

- 不编造创新分评分公式；口径未定义 → `needs-business`。
- 没有现有货号目录时，「契合现有货号」置空并标注，不猜测。
- 竞争度、场景若无法从数据推断 → 标注，不硬填。
