#!/usr/bin/env python3
"""记录一条问题到中央 issues/ 库，并自动关联当前 git 分支与 commit。

用法:
  python record_issue.py --module competitor-data-collector \
      --summary "listing_time 全量缺失，需真实爬虫补齐" \
      --source data_validation --severity medium --status needs-developer

source: user_feedback | self_review | data_validation | test_failure
status: pending | auto-fixable | needs-business | needs-developer | resolved
"""
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = repo_root = None  # placeholder, replaced below


def _repo_root():
    try:
        out = subprocess.run(
            ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
        ).stdout.strip()
        return Path(out)
    except Exception:
        return Path(__file__).resolve().parents[4]


REPO_ROOT = _repo_root()
ISSUES_DIR = REPO_ROOT / "issues"

SOURCE_PREFIX = {
    "user_feedback": "FB",
    "self_review": "AI",
    "data_validation": "AI",
    "test_failure": "TEST",
}

STATUS_FILE = {
    "pending": "pending.jsonl",
    "auto-fixable": "pending.jsonl",
    "needs-business": "needs-business.jsonl",
    "needs-developer": "needs-developer.jsonl",
    "resolved": "resolved.jsonl",
}


def git(cmd):
    try:
        return subprocess.run(
            ["git", "-C", str(REPO_ROOT)] + cmd,
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
        ).stdout.strip()
    except Exception:
        return ""


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def next_id(prefix, date):
    n = 0
    for f in ISSUES_DIR.glob("*.jsonl"):
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            iid = rec.get("issue_id", "")
            if iid.startswith(f"{prefix}-{date}-"):
                try:
                    n = max(n, int(iid.rsplit("-", 1)[-1]))
                except ValueError:
                    pass
    return f"{prefix}-{date}-{n + 1:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--source", required=True, choices=list(SOURCE_PREFIX))
    ap.add_argument("--severity", default="medium", choices=["low", "medium", "high", "critical"])
    ap.add_argument("--status", default="pending", choices=list(STATUS_FILE))
    ap.add_argument("--skill-version", default="0.1.0")
    ap.add_argument("--detail", default="{}")
    args = ap.parse_args()

    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    prefix = SOURCE_PREFIX[args.source]
    issue_id = next_id(prefix, date)
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    commit = git(["rev-parse", "HEAD"]) or None

    try:
        detail = json.loads(args.detail)
    except json.JSONDecodeError:
        detail = {"raw": args.detail}

    rec = {
        "issue_id": issue_id,
        "source": args.source,
        "module": args.module,
        "skill_version": args.skill_version,
        "severity": args.severity,
        "summary": args.summary,
        "status": args.status,
        "detail": detail,
        "branch": branch,
        "git_commit": commit,
        "created_at": now_iso(),
        "resolved_at": None,
    }

    ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    out = ISSUES_DIR / STATUS_FILE[args.status]
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(json.dumps(rec, ensure_ascii=False, indent=2))
    print(f"已记录到 {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
