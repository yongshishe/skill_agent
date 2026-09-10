#!/usr/bin/env python3
"""market-trend-monitor 趋势分析脚本。

读取 competitor-data-collector 的 manifest + chunk JSONL，计算三类趋势指标：
  1. 价格带迁移：$50 分桶计数，识别密集带与真空带（单期只输出现状）。
  2. 功能词热度：从 filters + attributes 提取功能点 / 面料 / 防水 / 容量段分布。
  3. 品类热度变化：按容量段计数。

输出 JSON 趋势预警报告到 data/，并把样本不足等发现追加进 feedback/self-review.jsonl。
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
COLLECTOR_DATA = SKILL_DIR.parent / "competitor-data-collector" / "data"
DATA_DIR = SKILL_DIR / "data"
FEEDBACK_DIR = SKILL_DIR / "feedback"
SKILL_VERSION = "0.1.0"
PRICE_BAND = 50


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_records(manifest):
    records, load_errors = [], []
    for c in manifest.get("chunks", []):
        fp = COLLECTOR_DATA / c["file"]
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


def price_bands(records):
    prices = [r["price_usd"] for r in records if r.get("price_usd") is not None]
    if not prices:
        return {"priced_count": 0, "bands": [], "gaps": [], "densest": [], "densest_count": 0}
    lo = int(min(prices) // PRICE_BAND) * PRICE_BAND
    hi = int(max(prices) // PRICE_BAND + 1) * PRICE_BAND
    bands = []
    for start in range(lo, hi, PRICE_BAND):
        cnt = sum(1 for p in prices if start <= p < start + PRICE_BAND)
        bands.append({"band": f"${start}-{start + PRICE_BAND}", "count": cnt})
    gaps = [b["band"] for b in bands if b["count"] == 0]
    maxcnt = max(b["count"] for b in bands)
    densest = [b["band"] for b in bands if b["count"] == maxcnt]
    return {
        "priced_count": len(prices),
        "bands": bands,
        "gaps": gaps,
        "densest": densest,
        "densest_count": maxcnt,
    }


def feature_heat(records):
    filter_counter = Counter()
    fabric_counter = Counter()
    waterproof_counter = Counter()
    capacity_counter = Counter()
    for r in records:
        for f in r.get("filters") or []:
            filter_counter[f] += 1
        a = r.get("attributes") or {}
        if a.get("material_fabric"):
            fabric_counter[a["material_fabric"]] += 1
        if "waterproof" in a:
            waterproof_counter["防水" if a["waterproof"] else "不防水"] += 1
        if a.get("capacity_l"):
            cap = a["capacity_l"]
            seg = "20-28L" if cap <= 28 else ("35-42L" if cap <= 42 else ("45L" if cap <= 45 else "60L+"))
            capacity_counter[seg] += 1
    return {
        "top_filters": filter_counter.most_common(10),
        "fabric": dict(fabric_counter.most_common()),
        "waterproof": dict(waterproof_counter),
        "capacity_segments": dict(capacity_counter.most_common()),
    }


def main():
    manifest_path = COLLECTOR_DATA / "manifest.json"
    if not manifest_path.exists():
        print(json.dumps(
            {"error": f"collector manifest 不存在: {manifest_path}"}, ensure_ascii=False, indent=2))
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records, load_errors = load_records(manifest)

    report = {
        "generated_at": now_iso(),
        "skill_version": SKILL_VERSION,
        "input_data_version": manifest.get("data_version"),
        "category": manifest.get("category"),
        "record_count": len(records),
        "load_errors": load_errors,
        "sections": {
            "价格带迁移": price_bands(records),
            "功能词热度": feature_heat(records),
        },
        "warnings": [],
    }
    if len(records) < 5:
        report["warnings"].append("样本量不足 5，趋势结论置信度低")

    dv = manifest.get("data_version", "unknown")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = DATA_DIR / f"trend-report-{dv}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DATA_DIR / "manifest.json").write_text(
        json.dumps({"skill": "market-trend-monitor", "latest_input": dv, "outputs": [out.name]},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    ts = now_iso()
    date_stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    with (FEEDBACK_DIR / "self-review.jsonl").open("a", encoding="utf-8") as f:
        for idx, w in enumerate(report["warnings"], 1):
            f.write(json.dumps({
                "issue_id": f"AI-{date_stamp}-TREND-{idx:03d}",
                "source": "self_review",
                "module": "market-trend-monitor",
                "skill_version": SKILL_VERSION,
                "severity": "low",
                "summary": w,
                "status": "pending",
                "created_at": ts,
            }, ensure_ascii=False) + "\n")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
