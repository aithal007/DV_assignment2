"""Export complete country-year profiles from A2 preprocessing outputs."""

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREPARED_DATA = ROOT / "data" / "processed"
OUT = ROOT / "data" / "infovis_countries.json"
FIELDS = (
    "internet_users_share_pct",
    "telephone_lines_per100",
    "broadband_subs_per100",
    "mobile_subs_per100",
)
YEARS = (2015, 2020)


def main() -> None:
    with (PREPARED_DATA / "region_lookup.csv").open(newline="", encoding="utf-8-sig") as handle:
        regions = {row["code"]: row["region"] for row in csv.DictReader(handle)}

    records = []
    exclusions = Counter()
    with (PREPARED_DATA / "master_dataset_countries_only.csv").open(
        newline="", encoding="utf-8-sig"
    ) as handle:
        for row in csv.DictReader(handle):
            year = int(row["year"])
            if year not in YEARS:
                continue
            if row["is_aggregate"].lower() == "true":
                exclusions["aggregate"] += 1
                continue
            if not row["code"]:
                exclusions["missing country code"] += 1
                continue
            if any(not row[field] for field in FIELDS):
                exclusions["incomplete profile"] += 1
                continue
            records.append(
                {
                    "country": row["entity"],
                    "code": row["code"],
                    "year": year,
                    "region": regions.get(row["code"], "Unclassified"),
                    **{field: float(row[field]) for field in FIELDS},
                }
            )

    records.sort(key=lambda r: (r["year"], r["country"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} rows to {OUT}")
    print("Retained by year:", dict(sorted(Counter(r["year"] for r in records).items())))
    print("Excluded:", dict(exclusions))


if __name__ == "__main__":
    main()
