# 采集业务规则

## 清洗与标准化

- 币种统一换算成 `price_usd`，原始币种保留 `currency`。
- 通用字段（`price_usd` / `rating` / `review_count`）统一归一化到顶层。
- 类目专属字段统一放 `attributes`：容量按类目用升（`capacity_l`）或毫升（`capacity_ml`），材质/供电/面料按类目枚举，见 [data-schema.md](data-schema.md)。
- 编辑评分（0–100）与亚马逊星级（0–5）分开：星级放顶层 `rating`，编辑评分放 `attributes.editorial_score`，不得混用。

## 数据版本

- 每次采集产出一个 `data_version`（如 `competitor-snapshot-2026w37`），写入 manifest 与每条记录。
- 切块文件名 `chunk-001.jsonl`、`chunk-002.jsonl`，顺序编号。
- manifest 的 `record_count` 必须等于各 chunk 行数之和。

## 边界

- 采集数量相对历史异常下降（本次为首次，无基线）→ 在自检中记录，暂不阻断。
- 价格、评分、评论数出现明显异常值 → 标记，不静默删除。
- 同类目样本量不足（例如 < 5）→ 自检记录「样本不足，结论置信度低」。
