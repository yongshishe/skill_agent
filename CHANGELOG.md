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

## v0.1.2 — 2026-09-10
- fix: 去重误报修复 + 补调用方案 README
- branch: `user/2026-09-10-record` · commit: `d8954bce793d09feae9c47577bca5d2fb1c5c3e1`
- 关联 issues: AI-20260910-003

## v0.2.0 — 2026-09-10
- feat: 新增 market-trend-monitor + product-opportunity-ranking；schema v1.1 泛化旅行包格式；release 默认 push
- branch: `user/2026-09-10-record` · commit: `516498b00d8d157329638bcbf601a7de490ce82a`
- 关联 issues: AI-20260910-004

## v0.2.1 — 2026-09-10
- fix: release.py 纳入 .gitignore 白名单变更，补齐新 Skill 白名单
- branch: `user/2026-09-10-record` · commit: `7f390bfd698bee7456c8eb6acda735de521dbc31`
