#!/usr/bin/env python3
"""product-opportunity-ranking 机会评分脚本。

读取 competitor-data-collector 的 manifest + chunk JSONL，基于价格带密度识别机会：
  1. 真空带（计数 0）/ 稀疏带（计数 1）→ 补位机会。
  2. 竞争度 = 目标价格带 SKU 密度（低/中/高）。
  3. 可解释场景 = 价格带位置启发式推导（口径待业务确认）。
  4. 创新分、契合现有货号 = 需业务口径/货号表 → needs_business 占位，不编造。

输出 JSON 机会清单到 data/，并写 data/manifest.json 索引。
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
COLLECTOR_DATA = SKILL_DIR.parent / "competitor-data-collector" / "data"
DATA_DIR = SKILL_DIR / "data"
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


def competition(count):
    if count <= 1:
        return "低"
    if count == 2:
        return "中"
    return "高"


def scenario_for(start, lo, hi):
    if start <= lo:
        return "入门性价比（价格带下沿）"
    if start + PRICE_BAND >= hi:
        return "高端差异化（价格带上沿）"
    return "主流补位（价格带中段）"


def main():
    manifest_path = COLLECTOR_DATA / "manifest.json"
    if not manifest_path.exists():
        print(json.dumps(
            {"error": f"collector manifest 不存在: {manifest_path}"}, ensure_ascii=False, indent=2))
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records, load_errors = load_records(manifest)

    prices = sorted(r["price_usd"] for r in records if r.get("price_usd") is not None)
    opportunities = []
    red_ocean = []
    if prices:
        band_lo = int(min(prices) // PRICE_BAND) * PRICE_BAND
        band_hi = int(max(prices) // PRICE_BAND + 1) * PRICE_BAND
        bands = []
        for start in range(band_lo, band_hi, PRICE_BAND):
            cnt = sum(1 for p in prices if start <= p < start + PRICE_BAND)
            bands.append((start, cnt))
            if cnt >= 3:
                red_ocean.append(f"${start}-{start + PRICE_BAND} ({cnt} 条)")
        for start, cnt in bands:
            if cnt <= 1:
                opportunities.append({
                    "target_price_band": f"${start}-{start + PRICE_BAND}",
                    "incumbent_count": cnt,
                    "创新分": {"value": None, "needs_business": True,
                               "reason": "创新分评分口径未定义，待业务确认"},
                    "竞争度": competition(cnt),
                    "可解释场景": scenario_for(start, band_lo, band_hi),
                    "契合现有货号": {"value": None, "needs_business": True,
                                     "reason": "缺少现有货号目录，无法比对"},
                })

    report = {
        "generated_at": now_iso(),
        "skill_version": SKILL_VERSION,
        "input_data_version": manifest.get("data_version"),
        "category": manifest.get("category"),
        "record_count": len(records),
        "priced_count": len(prices),
        "load_errors": load_errors,
        "opportunities": opportunities,
        "red_ocean_bands": red_ocean,
    }

    dv = manifest.get("data_version", "unknown")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = DATA_DIR / f"opportunity-list-{dv}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DATA_DIR / "manifest.json").write_text(
        json.dumps({"skill": "product-opportunity-ranking", "latest_input": dv, "outputs": [out.name]},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
