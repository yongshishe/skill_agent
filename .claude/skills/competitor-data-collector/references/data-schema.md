# 竞品 SKU 数据 Schema

版本：`competitor_sku v1.1`（类目字段泛化：类目专属字段下沉到 `attributes`）

每条 SKU 一个 JSON 对象，写入 `data/<data_version>/chunk-*.jsonl`（每行一条，无顶层数组）。

## 通用字段（所有类目共用，顶层）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sku_id` | string | 是 | 内部唯一 ID，格式 `SKU-<platform>-<seq>` |
| `product_name` | string | 是 | 产品名 |
| `brand` | string | 否 | 品牌，未知 null |
| `platform` | string | 是 | 枚举：`amazon_us` / `amazon_au` / `1688` / `tiktok` / `other` |
| `source_url` | string | 否 | 原始来源链接，无则 null |
| `price_usd` | number | 否 | 归一化美元价，缺失 null |
| `currency` | string | 否 | 原始币种，如 `USD` / `AUD` / `CNY` |
| `rating` | number | 否 | 亚马逊星级 0–5，缺失 null |
| `review_count` | integer | 否 | 评论数，缺失 null |
| `amazon_choice` | boolean | 否 | 是否 Amazon's Choice，未知 false |
| `filters` | string[] | 否 | 过滤/功能点列表 |
| `listing_time` | string | 否 | 上架时间 ISO 日期，缺失 null |
| `sales_estimate` | integer | 否 | 销量估计，缺失 null |
| `collected_at` | string | 是 | 采集时间 ISO 8601 |
| `data_version` | string | 是 | 所属数据版本，与 manifest 一致 |
| `attributes` | object | 否 | 类目专属字段，见下 |

## 类目专属字段（放 attributes）

不同类目的规格字段不同，统一放进 `attributes`，不在顶层堆类目专属字段。

### 旅行包 / 箱包（travel-bag）

| 字段 | 类型 | 说明 |
|---|---|---|
| `capacity_l` | number | 容量（升） |
| `material_fabric` | string | 面料（如 nylon / polyester / 1000D TPU-coated nylon） |
| `waterproof` | boolean | 是否防水 |
| `editorial_score` | number | 编辑评分 0–100（测评站口径，非亚马逊星级） |
| `rating_source` | string | 评分来源标识 |
| `price_note` | string | 价格备注（如 under $100 / not listed） |

### 宠物饮水机（pet-water-fountain，历史种子类目）

| 字段 | 类型 | 说明 |
|---|---|---|
| `capacity_ml` | number | 容量（毫升） |
| `material` | string | 材质：`stainless_steel` / `ceramic` / `plastic` / `mixed` |
| `power` | string | 供电：`wired` / `cordless` / `wireless_pump` |
| `noise_db` | number | 噪音（分贝） |

### 保温杯 / 保温杯（thermos / insulated-tumbler）

| 字段 | 类型 | 说明 |
|---|---|---|
| `capacity_ml` | number | 容量（毫升），由 oz 换算（1 oz ≈ 29.57 ml） |
| `material` | string | 材质：`stainless_steel` / `ceramic_coated` / `titanium` / `glass` / `plastic` / `mixed` |
| `insulation_type` | string | 保温结构：`vacuum_double_wall` / `vacuum` / `foam` / `none` |
| `hot_retention_hours` | number | 保温时长（热饮，小时），公开测评口径，缺失 null |
| `cold_retention_hours` | number | 保冷时长（冷饮，小时），缺失 null |
| `lid_type` | string | 杯盖类型：`straw` / `flip` / `screw` / `press` / `autoseal` / `magslider` |
| `leak_proof` | boolean | 是否防漏 |
| `dishwasher_safe` | boolean | 是否可洗碗机，未知 null |

## 约束

- 数值字段统一归一化（币种→USD；容量按类目单位进 `attributes`）。
- `rating` 取值范围 [0,5]；`editorial_score` 取值范围 [0,100]（类目专属，放 `attributes`）。
- 不允许用 `0` 或空字符串表示「未知」，未知一律 `null`。
- 同一条记录 `collected_at` / `data_version` 必须一致。

## 示例（旅行包）

```json
{"sku_id":"SKU-amazon_us-001","product_name":"Osprey Farpoint 40 Travel Backpack","brand":"Osprey","platform":"amazon_us","source_url":"https://...","price_usd":185.0,"currency":"USD","rating":4.7,"review_count":561,"amazon_choice":false,"filters":["LightWire frame","16-inch laptop sleeve"],"listing_time":null,"sales_estimate":null,"collected_at":"2026-09-10T10:00:00Z","data_version":"travel-bag-snapshot-2026w37","attributes":{"capacity_l":40,"material_fabric":"nylon","waterproof":false,"rating_source":"amazon.ae ASIN B09KQ262GM"}}
```
