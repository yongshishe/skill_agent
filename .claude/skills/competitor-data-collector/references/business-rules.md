# 采集业务规则

## 清洗与标准化

- 币种统一换算成 `price_usd`，原始币种保留 `currency`。
- 容量统一为 `capacity_ml`：1 oz ≈ 29.5735 ml，1 L = 1000 ml。
- 材质归一到枚举：全不锈钢→`stainless_steel`，陶瓷→`ceramic`，塑料→`plastic`，多材质混合→`mixed`。
- 供电归一到枚举：插电→`wired`，内置电池→`cordless`，无线水泵（线不入水）→`wireless_pump`。

## 数据版本

- 每次采集产出一个 `data_version`（如 `competitor-snapshot-2026w37`），写入 manifest 与每条记录。
- 切块文件名 `chunk-001.jsonl`、`chunk-002.jsonl`，顺序编号。
- manifest 的 `record_count` 必须等于各 chunk 行数之和。

## 边界

- 采集数量相对历史异常下降（本次为首次，无基线）→ 在自检中记录，暂不阻断。
- 价格、评分、评论数出现明显异常值 → 标记，不静默删除。
- 同类目样本量不足（例如 < 5）→ 自检记录「样本不足，结论置信度低」。
