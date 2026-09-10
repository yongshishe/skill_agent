# 异常处理

| 异常 | 处理 |
|---|---|
| collector manifest 不存在 | 报错退出，提示先跑采集 |
| chunk 文件缺失 / 坏 JSON | 计入 load_errors，继续处理其余记录 |
| 全量 price_usd 为 null | 无法计算价格带，机会列表置空并说明 |
| 无真空带 / 稀疏带 | 输出空机会列表 + 红海提示，不硬造机会 |
| 创新分无口径 | 置 needs_business，不编造公式 |
| 无现有货号目录 | 「契合现有货号」置 needs_business |
