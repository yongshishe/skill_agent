#!/usr/bin/env python3
"""competitor-data-collector 数据质量自检脚本。

读取 data/manifest.json 指向的 chunk JSONL，执行字段完整性 / 去重 / 异常值 / 样本量检查，
输出 JSON 自检报告，并把发现的问题追加写入 feedback/self-review.jsonl。
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SKILL_DIR / "data"
FEEDBACK_DIR = SKILL_DIR / "feedback"
SKILL_VERSION = "0.1.0"

REQUIRED = ["sku_id", "product_name", "platform", "collected_at", "data_version"]


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_manifest():
    p = DATA_DIR / "manifest.json"
    return json.loads(p.read_text(encoding="utf-8"))


def load_all(manifest):
    records, load_errors = [], []
    for c in manifest.get("chunks", []):
        fp = DATA_DIR / c["file"]
        if not fp.exists():
            load_errors.append({"type": "missing_file", "file": str(fp)})
            continue
        with fp.open(encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    load_errors.append(
                        {"type": "bad_json", "file": str(fp), "line": i, "error": str(e)}
                    )
    return records, load_errors


def run_checks(records, manifest):
    issues = []
    n = len(records)

    if n < 5:
        issues.append({
            "summary": f"样本量仅 {n}，低于阈值 5，结论置信度低",
            "severity": "medium", "status": "pending",
        })

    # 必填字段缺失
    for f in REQUIRED:
        missing = sum(1 for r in records if r.get(f) is None)
        if missing:
            issues.append({
                "summary": f"必填字段 {f} 缺失 {missing} 条",
                "severity": "high", "status": "needs-developer",
            })

    # 重复
    sku_ids = [r.get("sku_id") for r in records]
    dup_sku = sorted({s for s in sku_ids if sku_ids.count(s) > 1})
    if dup_sku:
        issues.append({
            "summary": f"sku_id 重复: {dup_sku}",
            "severity": "high", "status": "auto-fixable",
        })
    # 同篇测评覆盖多品是正常的，只有「同名产品 + 同一来源」重复才算真重复
    pairs = [(r.get("product_name"), r.get("source_url"))
             for r in records if r.get("source_url")]
    dup_pairs = sorted({p for p in pairs if pairs.count(p) > 1})
    if dup_pairs:
        issues.append({
            "summary": f"同名产品同一来源重复 {len(dup_pairs)} 条",
            "severity": "medium", "status": "auto-fixable",
        })

    # 数值字段：缺失 + 越界
    for f, (lo, hi) in {
        "price_usd": (0, None),
        "rating": (0, 5),
        "review_count": (0, None),
    }.items():
        vals = [r.get(f) for r in records if r.get(f) is not None]
        null_cnt = n - len(vals)
        if null_cnt:
            issues.append({
                "summary": f"{f} 缺失 {null_cnt}/{n} 条",
                "severity": "medium", "status": "pending",
            })
        bad = [v for v in vals if (lo is not None and v < lo) or (hi is not None and v > hi)]
        if bad:
            issues.append({
                "summary": f"{f} 越界值: {bad}",
                "severity": "high", "status": "auto-fixable",
            })

    # 关键业务字段全空 → needs-developer
    for f in ("listing_time", "sales_estimate"):
        if n and all(r.get(f) is None for r in records):
            issues.append({
                "summary": f"{f} 全量缺失，公开渠道不可得，需真实爬虫/API 补齐",
                "severity": "medium", "status": "needs-developer",
            })

    # manifest record_count 一致性
    declared = sum(c.get("record_count", 0) for c in manifest.get("chunks", []))
    if declared != n:
        issues.append({
            "summary": f"manifest 声明 {declared} 条，实际 {n} 条，不一致",
            "severity": "high", "status": "auto-fixable",
        })

    return issues


def main():
    manifest = load_manifest()
    records, load_errors = load_all(manifest)
    issues = run_checks(records, manifest)

    ts = now_iso()
    date_stamp = datetime.now(timezone.utc).strftime("%Y%m%d")

    report = {
        "checked_at": ts,
        "skill_version": SKILL_VERSION,
        "data_version": manifest.get("data_version"),
        "record_count": len(records),
        "load_errors": load_errors,
        "issue_count": len(issues),
        "issues": issues,
    }

    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    sr_file = FEEDBACK_DIR / "self-review.jsonl"
    with sr_file.open("a", encoding="utf-8") as f:
        for idx, it in enumerate(issues, 1):
            rec = {
                "issue_id": f"AI-{date_stamp}-{idx:03d}",
                "source": "data_validation",
                "module": "competitor-data-collector",
                "skill_version": SKILL_VERSION,
                "severity": it["severity"],
                "summary": it["summary"],
                "status": it["status"],
                "created_at": ts,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
