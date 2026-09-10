# 问题分类与状态机

## 状态机

```
pending          已记录，待统一处理
auto-fixable     AI 判断可通过规则/文档/测试/脚本修改解决
needs-business   需要业务确认（评分口径不清、字段含义未定义等）
needs-developer  需要开发者介入（爬虫失效、API 故障、数据库问题等）
resolved         已修复并通过回归测试
```

## 来源

| 来源 | 含义 |
|---|---|
| `user_feedback` | 用户发现 |
| `self_review` | AI 自检发现 |
| `data_validation` | 数据质量校验发现 |
| `test_failure` | 测试发现 |

## 问题不直接变规则：先归类再处理

| 问题类型 | 处理方式 |
|---|---|
| 数据缺失或脏数据 | 修复采集、清洗或数据校验 |
| 原 SOP 规则遗漏 | 补充对应参考资料或 Skill 路由 |
| Skill 理解错误 | 精准修改指令或决策规则 |
| 切块导致上下文丢失 | 调整文档块边界和关联索引 |
| 测试覆盖不足 | 新增回归测试，不一定改业务规则 |
| 原文档未定义 | 标记待业务确认，不擅自编造 |
| 用户新增要求 | 作为需求变更，单独确认后纳入 |
| 模型推断不可靠 | 增加证据要求、置信度和禁止推断规则 |

## AI 自动修改的边界

**允许**（低风险、有明确依据）：补充遗漏的 SOP 规则、修正参考文件路由、增加输入校验、补齐测试用例。

**禁止**（转 `needs-developer` 或 `needs-business`）：

- 爬虫、API、账号、网络、反爬或页面结构问题。
- 数据库、权限、部署、定时任务失败。
- 需要修改真实代码、基础设施或第三方服务配置。
- 业务规则、评分口径、字段含义未定义或互相冲突。
- 无法证明某个结论是数据问题还是市场事实。
- 多次修复仍复现，或修改可能影响多个模块。

## developer 工单最小字段

```json
{
  "issue_id": "DEV-20260910-001",
  "source": "self_review | user_feedback | test_failure",
  "module": "competitor-data-collector",
  "skill_version": "0.3.0",
  "severity": "high",
  "summary": "一句话描述",
  "reproduction_input": "站点、类目、SKU 或 URL",
  "expected_behavior": "期望行为",
  "actual_behavior": "实际行为",
  "evidence": "原始响应、日志、截图或错误信息路径",
  "ai_diagnosis": "疑似根因",
  "attempted_actions": ["已尝试动作"],
  "recommended_owner": "crawler-developer",
  "status": "needs-developer"
}
```
