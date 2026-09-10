# 数据源字段映射

记录各平台「哪些字段从哪取」。初版为公开搜索采集，真实爬虫字段路径待开发者补齐。

## 平台字段映射

| 字段 | amazon_us | amazon_au | 1688 | 海外社媒(tiktok) |
|---|---|---|---|---|
| `product_name` | 商品标题 | 商品标题 | 货品标题 | 视频标题/挂车商品名 |
| `brand` | Brand 字段 | Brand 字段 | 品牌/厂牌 | 品牌标签 |
| `price` | price 块 | price 块 | 批发价/阶梯价 | 挂车价格 |
| `rating` | acrCustomerReviewText | 同左 | 无（1688 无评分体系） | 无 |
| `review_count` | 评分旁计数 | 同左 | 成交数/评价数 | 点赞/销量标签 |
| `listing_time` | 商品详情上架时间 | 同左 | 上架/更新时间 | 发布时间 |
| `sales_estimate` | 需第三方估算 | 需第三方估算 | 30 天成交 | 需第三方估算 |

## 本初版的真实来源

- 数据来自 2026-09-10 的公开 Web 搜索（测评文章、Consumer Reports、Amazon AU 比价页等）。
- `price_usd` / `capacity_ml` 已按来源归一化；不同站点的原始币种保留在 `currency`。
- `listing_time`、`sales_estimate` 公开渠道不可得，全部置 `null`，由自检标 `needs-developer`。

## 待开发者补齐（needs-developer）

- Amazon 商品页 DOM 字段选择器（价格、评分、评论数、上架时间）。
- 1688 的接口字段与登录态。
- 反爬 / 频率限制策略。
- 销量估算口径。
