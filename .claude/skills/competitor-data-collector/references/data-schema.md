# 竞品 SKU 数据 Schema

版本：`competitor_sku v1.0`

每条 SKU 一个 JSON 对象，写入 `data/<data_version>/chunk-*.jsonl`（每行一条，无顶层数组）。

## 字段定义

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sku_id` | string | 是 | 内部唯一 ID，格式 `SKU-<platform>-<seq>` |
| `product_name` | string | 是 | 产品名 |
| `brand` | string | 否 | 品牌，未知为 null |
| `platform` | string | 是 | 枚举：`amazon_us` / `amazon_au` / `1688` / `tiktok` / `other` |
| `source_url` | string | 否 | 原始来源链接，无则 null |
| `price_usd` | number | 否 | 归一化美元价，缺失为 null |
| `currency` | string | 否 | 原始币种，如 `USD` / `AUD` / `CNY` |
| `capacity_ml` | number | 否 | 容量归一化为毫升，缺失为 null |
| `material` | string | 否 | 枚举：`stainless_steel` / `ceramic` / `plastic` / `mixed`，未知 null |
| `power` | string | 否 | 枚举：`wired` / `cordless` / `wireless_pump`，未知 null |
| `noise_db` | number | 否 | 噪音分贝，缺失 null |
| `rating` | number | 否 | 评分 0–5，缺失 null |
| `review_count` | integer | 否 | 评论数，缺失 null |
| `amazon_choice` | boolean | 否 | 是否 Amazon's Choice，未知 false |
| `filters` | string[] | 否 | 过滤/功能点列表 |
| `listing_time` | string | 否 | 上架时间 ISO 日期，缺失 null |
| `sales_estimate` | integer | 否 | 销量估计，缺失 null |
| `collected_at` | string | 是 | 采集时间 ISO 8601 |
| `data_version` | string | 是 | 所属数据版本，与 manifest 一致 |
| `attributes` | object | 否 | 扩展属性（供聚类使用），默认 `{}` |

## 约束

- 价格、容量、噪音等数值字段统一归一化（币种→USD、oz→ml）。
- `rating` 取值范围 [0,5]；`review_count` ≥ 0。
- 不允许用 `0` 或空字符串表示「未知」，未知一律 `null`。
- 同一条记录 `collected_at` / `data_version` 必须一致。

## 示例

```json
{"sku_id":"SKU-amazon_us-001","product_name":"Petkit Eversweet Solo SE","brand":"Petkit","platform":"amazon_us","source_url":"https://...","price_usd":25.99,"currency":"USD","capacity_ml":1850,"material":"plastic","power":"wireless_pump","noise_db":25,"rating":null,"review_count":13507,"amazon_choice":true,"filters":["5-stage filtration","wireless pump"],"listing_time":null,"sales_estimate":null,"collected_at":"2026-09-10T00:00:00Z","data_version":"competitor-snapshot-2026w37","attributes":{}}
```
