#!/usr/bin/env python3
"""把一次 Skill 修改提交到 git 分支，生成 release-manifest 并更新 CHANGELOG。

用法:
  python release.py --message "fix: price_usd 缺失" --issues FB-001,AI-002 --skill competitor-data-collector [--no-push]

行为:
  1. 若当前在 main/master，自动新建 user/<日期>-<slug> 分支。
  2. git add 本工厂的 Skill + issues + releases + CHANGELOG。
  3. 提交（无变更则跳过）。
  4. 生成 releases/<version>/release-manifest.json（含 git_commit、branch、issues）。
  5. 追加 CHANGELOG 版本条目并二次提交。
  6. 默认 push -u origin <branch>（除非 --no-push；未配置 origin 则跳过）。
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = None


def _repo_root():
    try:
        out = subprocess.run(
            ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except Exception:
        return Path(__file__).resolve().parents[4]


REPO_ROOT = _repo_root()
RELEASES_DIR = REPO_ROOT / "releases"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"


def run(cmd, check=True):
    r = subprocess.run(["git", "-C", str(REPO_ROOT)] + cmd,
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(r.returncode)
    return r.stdout.strip()


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def current_branch():
    return run(["rev-parse", "--abbrev-ref", "HEAD"])


def latest_version():
    vers = []
    if RELEASES_DIR.exists():
        for d in RELEASES_DIR.iterdir():
            m = re.match(r"^v(\d+)\.(\d+)\.(\d+)$", d.name)
            if m:
                vers.append(tuple(int(x) for x in m.groups()))
    return max(vers) if vers else (0, 1, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--message", required=True)
    ap.add_argument("--issues", default="")
    ap.add_argument("--skill", default="")
    ap.add_argument("--bump", default="patch", choices=["patch", "minor", "major"])
    ap.add_argument("--no-push", action="store_true", help="跳过 push（默认会 push）")
    args = ap.parse_args()

    if not (REPO_ROOT / ".git").exists():
        sys.exit("不是 git 仓库，先在项目根目录执行 git init")

    branch = current_branch()
    if branch in ("main", "master"):
        slug = re.sub(r"[^a-z0-9]+", "-", args.message.lower()).strip("-")[:40]
        if not slug:
            slug = "change"
        branch = f"user/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{slug}"
        run(["checkout", "-b", branch])
        print(f"新建分支: {branch}")

    v = latest_version()
    if args.bump == "major":
        v = (v[0] + 1, 0, 0)
    elif args.bump == "minor":
        v = (v[0], v[1] + 1, 0)
    else:
        v = (v[0], v[1], v[2] + 1)
    version = f"v{v[0]}.{v[1]}.{v[2]}"

    issues = [i.strip() for i in args.issues.split(",") if i.strip()]

    add_paths = [p for p in (".claude/skills", "issues", "releases", "CHANGELOG.md", "README.md", ".gitignore")
                 if (REPO_ROOT / p).exists()]
    run(["add"] + add_paths)
    commit_msg = args.message + (f" (issues: {', '.join(issues)})" if issues else "")
    if run(["diff", "--cached", "--name-only"], check=False):
        run(["commit", "-m", commit_msg])
        print(f"已提交: {commit_msg}")
    else:
        print("无待提交变更，跳过 commit")

    commit = run(["rev-parse", "HEAD"])

    rel_dir = RELEASES_DIR / version
    rel_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "release_version": version,
        "git_commit": commit,
        "branch": branch,
        "released_at": now_iso(),
        "skill": args.skill or None,
        "resolved_issues": issues,
        "message": args.message,
    }
    (rel_dir / "release-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    entry = (
        f"\n## {version} — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
        f"- {args.message}\n"
        f"- branch: `{branch}` · commit: `{commit}`\n"
    )
    if issues:
        entry += f"- 关联 issues: {', '.join(issues)}\n"
    with CHANGELOG.open("a", encoding="utf-8") as f:
        f.write(entry)

    rel_add = [p for p in ("releases", "CHANGELOG.md") if (REPO_ROOT / p).exists()]
    run(["add"] + rel_add)
    if run(["diff", "--cached", "--name-only"], check=False):
        run(["commit", "-m", f"release: {version} manifest & changelog"])

    print(json.dumps(manifest, ensure_ascii=False, indent=2))

    if not args.no_push:
        remote = run(["remote", "get-url", "origin"], check=False)
        if not remote:
            print("警告：未配置 origin 远程，跳过 push。")
        else:
            run(["push", "-u", "origin", branch])
            print(f"已 push 到 origin/{branch}")


if __name__ == "__main__":
    main()
