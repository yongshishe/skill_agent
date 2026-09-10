# 异常处理

| 异常 | 处理 |
|---|---|
| collector manifest 不存在 | 报错退出，提示先跑采集 |
| chunk 文件缺失 / 坏 JSON | 计入 load_errors，继续处理其余记录 |
| 全量 price_usd 为 null | 价格带迁移置空，报告中说明 |
| 样本 < 5 | 降置信度，warnings 标注，不阻断 |
| 无上一期数据 | 只输出现状，不输出迁移方向 |
| 多类目数据混在一份 manifest | 按 category 拆分后分别分析（当前为单类目，遇此转 needs-business） |
