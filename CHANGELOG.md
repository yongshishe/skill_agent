# 选品 Skill 工厂 变更记录

## v0.1.0 — 2026-09-10

- 初始化：`business-skill-factory`（元）+ `competitor-data-collector`（采集）两个 Skill。
- 采集「宠物饮水机」12 条竞品 SKU，JSONL + manifest 存储。
- 数据质量自检脚本 `validate.py` 跑通。
- 引入 git 分支工作流：`record_issue.py` 记录问题、`release.py` 提交 + 发版。

## v0.1.1 — 2026-09-10
- feat: 问题记录与发版脚本
- branch: `user/2026-09-10-record` · commit: `86e1fb5731679003ede037ff935ec7743bde4277`
- 关联 issues: AI-20260910-001, AI-20260910-002, AI-20260910-003
