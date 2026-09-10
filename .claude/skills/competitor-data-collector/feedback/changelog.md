# competitor-data-collector 变更记录

## v0.1.0 — 2026-09-10

- 从 0 建立 Skill 骨架：`SKILL.md` + `references/`（data-schema / source-map / business-rules / exceptions）+ `scripts/validate.py` + `evals/evals.json` + `feedback/`。
- 一次性采集「宠物饮水机」类目 12 条竞品 SKU（公开 Web 搜索），落 JSONL + `manifest.json`。
- 上线数据质量自检脚本，产出 `self-review.jsonl`。
- 已知缺口：`listing_time` / `sales_estimate` 全量缺失（公开渠道不可得，转 `needs-developer`）；2 条 Amazon AU 记录 `price_usd` 未换算（原始 AUD 保留在 `attributes.raw_price_aud`）。
