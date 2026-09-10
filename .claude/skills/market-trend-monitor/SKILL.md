---
name: market-trend-monitor
description: >-
  趋势监测 Skill。当用户想要监控某类目竞品的价格带迁移、功能词热度、品类热度变化，产出
  《趋势预警》报告时使用。触发意图示例：监控价格趋势、分析价格带迁移、看功能词热度、
  品类热度变化、生成趋势预警、趋势分析。
---

# market-trend-monitor

读竞品 SKU 数据集，产出三类趋势指标（价格带迁移 / 功能词热度 / 品类热度变化），生成《趋势预警》，供机会评分与选品决策消费。

## 触发与路由

靠自然语言意图判定。当用户表达「趋势 / 价格带 / 功能词 / 品类热度 / 预警」时进入本 Skill。

执行顺序：

1. 读上游 `competitor-data-collector` 的 `data/manifest.json` + chunk JSONL。
2. 跑 `scripts/analyze_trends.py` 计算三类指标。
3. 按 [report-template.md](references/report-template.md) 输出《趋势预警》。
4. 异常按 [exceptions.md](references/exceptions.md) 处理。

## 输入

- 上游标准化 SKU 数据集（collector 的 `data/manifest.json` 指向的 JSONL）。
- 可选：上一版数据（用于计算「迁移」；无基线则只输出现状，不编造历史）。

## 输出

- 趋势报告：`data/trend-report-<data_version>.json`
- 报告索引：`data/manifest.json`
- 自检发现（样本不足等）追加进 `feedback/self-review.jsonl`

## 流程约束

- 数值字段用「当前值 vs 上一版」计算迁移；没有上一版只给现状，不臆造趋势方向。
- 价格带分桶默认 $50；密集带、真空带、迁移方向必须能追溯到具体 SKU 计数。
- 样本 < 5 时结论降置信度，报告里显式标注。

## 硬约束

- 不编造历史数据或趋势方向；只有单期数据时禁止输出「上升 / 下降」结论。
- 功能词热度只统计数据里实际出现的字段（filters / attributes），缺字段标记待补，不推测。
- 指标口径未定义 → 转 `needs-business`。
