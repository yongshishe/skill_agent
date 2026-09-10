# Git 分支工作流与开发者对齐

目标：每次 Skill 修改都落在一条 `user/*` 分支并提交；当用户遇到无法自行修复的问题，开发者能直接拉取这条分支，看到用户改了哪些文件、关联了哪些 issue、跑了哪些测试，从而减少开发者工作量、保证对齐。

## 分支模型（branch-per-change）

- `main`：稳定 / 已发布版本，开发者合并目标。
- `user/<日期>-<问题标识>`：用户的每一次修改/问题开一条分支，**分支名直接标注问题**。
  - 记录问题时 `record_issue.py` 自动创建（从 `--summary`/`--slug` 提取简短标识，如 `trend-hardcode-fields`）。
  - 发版时 `release.py` 若仍在 main 也会用 message 派生 slug 建分支。
- 每条 commit message 关联 issue 编号（如 `fix FB-001`）。
- push 后开发者 `git fetch` + `git diff main...user/<branch>` 即可看到用户改动全貌，分支名直接告诉开发者「大概是什么问题」。
- **记录新问题前先 `git checkout main`**，让 `record_issue.py` 为每个问题开一条干净、带标注的分支。

## 问题记录（记录优先、不即时改）

- 中央问题库 `issues/`：`pending.jsonl` / `needs-business.jsonl` / `needs-developer.jsonl` / `resolved.jsonl`。
- 每条 issue：`issue_id`、`source`、`module`、`skill_version`、`severity`、`summary`、`status`、`branch`、`git_commit`、`created_at`。
- `scripts/record_issue.py` 记录问题并自动关联当前分支与 commit。
- Skill 本地 `feedback/*.jsonl` 是 AI 运行日志；`issues/` 是面向开发者的规范库（canonical）。

## 发布与追溯

- `scripts/release.py` 提交改动 → 生成 `releases/<version>/release-manifest.json`（含 `git_commit`、`branch`、`resolved_issues`）→ 更新 CHANGELOG。
- 能回答：某次改动在哪个 commit、哪个分支、改了哪些 issue、是否已 push。

## 硬规则（每次修复必走）

- **每次修复 / 发版默认 push**：`release.py` 默认 `push -u origin <branch>`，除非显式 `--no-push`。
- **用户问题必须先落库**：用户反馈 → `record_issue.py` 存进 `issues/`（带分支 + commit），再决定是否修复；不落库不修。
- **改动只进 `user/*` 分支，不自动合并 `main`**：`release.py` 只推 user/* 分支；遇到用户不可修的问题，开发者拉分支定位 → 修改 → 再合并 main。AI 不直接改 / 合 main。

## 开发者协作流

1. 用户 push `user/*` 分支到 GitHub。
2. 开发者 pull 分支，读 release-manifest + 关联 issue 了解意图与上下文。
3. 开发者审阅 / 修改 / 合并到 `main`。
4. 无法自动修复的 issue（`needs-developer`）自带复现输入、证据、AI 诊断、已尝试动作，开发者直接接手。

## push 前置条件

- 先配置远程：`git remote add origin <你的 GitHub 仓库 URL>`。
- 首次推送：`git push -u origin main`，之后 `release.py`（默认 push）推送 user 分支。
- 本机未装 `gh` CLI，GitHub 操作走 git + 远端 URL（HTTPS + token 或 SSH）。
