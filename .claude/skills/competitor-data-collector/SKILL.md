---
name: competitor-data-collector
description: >-
  竞品数据采集 Skill。当用户想要采集亚马逊 / 1688 / 海外社媒等平台的竞品 SKU、价格、销量、
  评分、上架时间，并把原始数据标准化成结构化 SKU 数据集（JSONL + manifest 索引，支持切块）时使用。
  触发意图示例：采集某个类目的竞品数据、爬取 SKU、抓取竞品价格和评分、把竞品数据标准化、
  采集并切块保存。
---

# competitor-data-collector

把各平台原始竞品数据，标准化成下游（聚类 / 趋势 / 机会评分）可直接消费的 SKU 数据集。

## 触发与路由

靠自然语言意图判定。当用户表达「采集 / 爬取 / 抓取 / 标准化竞品数据」时进入本 Skill。

执行顺序按需加载 reference：

1. 明确平台与类目 → 读 [source-map.md](references/source-map.md) 定位字段来源。
2. 采集原始数据 → 按 [data-schema.md](references/data-schema.md) 标准化字段。
3. 应用 [business-rules.md](references/business-rules.md) 的清洗与约束。
4. 遇到异常按 [exceptions.md](references/exceptions.md) 处理。
5. 写 JSONL（大则切块）+ 更新 `data/manifest.json`。
6. 跑 `scripts/validate.py` 做数据质量自检，结果进 `feedback/self-review.jsonl`。

## 输入

- 平台（amazon_us / amazon_au / 1688 / tiktok 等）
- 类目 / 关键词 / 时间范围
- 数据源访问方式（公开搜索、已有接口、爬虫授权）

## 输出

- 标准化 SKU 数据集：`data/<data_version>/chunk-*.jsonl`
- 数据版本索引：`data/manifest.json`
- 自检报告 + `feedback/self-review.jsonl` 追加记录

## 流程约束

- 每个字段要么有值、要么显式 `null`，不省略、不猜测。
- 原始来源 URL 必须保留，保证可追溯。
- 上架时间、销量等公开渠道拿不到的字段置 `null`，由自检脚本标 `needs-developer`，不编造。
- 切块后 manifest 的 `record_count` 必须与实际行数一致。

## 硬约束

- 不接入或编写真实爬虫代码（本初版为一次性采集）。需要真实爬虫 → 转 `needs-developer`。
- 反爬、登录失效、页面结构变化 → 停止重试，记录并转 `needs-developer`。
- 脏数据（价格为空、销量格式异常）标记后不进入评分，不删除、不补造。
