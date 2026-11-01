"""shared data preparation utilities for a2."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]

# indicator profile and raw source mappings
profile = [
    "internet_users_share_pct",
    "telephone_lines_per100",
    "broadband_subs_per100",
    "mobile_subs_per100",
]
sources = {
    "number-of-internet-users.csv": {
        "it_net_user_zs_number": "internet_users_count"
    },
    "share-of-individuals-using-the-internet.csv": {
        "it_net_user_zs": "internet_users_share_pct"
    },
    "ict-adoption-per-100-people.csv": {
        "it_mlt_main_p2": "telephone_lines_per100",
        "it_net_bbnd_p2": "broadband_subs_per100",
        "it_cel_sets_p2": "mobile_subs_per100",
    },
}
aggregates = {
    "World", "High-income countries", "Low-income countries",
    "Lower-middle-income countries", "Upper-middle-income countries",
    "Africa (UN)", "Asia (UN)", "Europe (UN)", "Northern America (UN)",
    "Central and Southern Asia (UN SDG)", "East Asia and Pacific (WB)",
    "Eastern and South-Eastern Asia (UN SDG)", "Europe and Central Asia (WB)",
    "Europe and Northern America (UN SDG)", "European Union (27)",
    "Latin America and Caribbean (WB)",
    "Latin America and the Caribbean (UN SDG)",
    "Latin America and the Caribbean (UN)",
    "Middle East, North Africa, Afghanistan and Pakistan (WB)",
    "North America (WB)", "Northern Africa and Western Asia (UN SDG)",
    "Small Island Developing States (SIDS)", "South Asia (WB)",
    "Sub-Saharan Africa (UN SDG)", "Sub-Saharan Africa (WB)",
}
infovis_years = (2015, 2020)
infovis_fields = (
    "internet_users_share_pct",
    "telephone_lines_per100",
    "broadband_subs_per100",
    "mobile_subs_per100",
)


# compute sha256 checksum
def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# preprocess country data and weather support
def preprocess(download_weather: bool = False) -> None:
    raw = root / "data/raw"
    out = root / "data/processed"
    out.mkdir(parents=True, exist_ok=True)

    evidence: dict = {"input_files": {}, "raw_rows": {}, "steps": []}
    merged = None
    for name, rename in sources.items():
        path = raw / name
        if not path.exists():
            raise FileNotFoundError(f"missing raw input {path}")
        df = pd.read_csv(path).rename(
            columns={"Entity": "entity", "Code": "code", "Year": "year", **rename}
        )
        df = df[["entity", "code", "year", *rename.values()]].copy()
        if df.duplicated(["entity", "code", "year"]).any():
            raise ValueError(f"duplicate keys in {name}")
        for col in rename.values():
            df[col] = pd.to_numeric(df[col], errors="raise")
        evidence["input_files"][name] = _checksum(path)
        evidence["raw_rows"][name] = len(df)
        merged = (
            df
            if merged is None
            else merged.merge(
                df, on=["entity", "code", "year"], how="outer", validate="one_to_one"
            )
        )

    # filter country rows and write master csv
    merged["is_aggregate"] = merged.entity.isin(aggregates)
    countries = (
        merged.loc[~merged.is_aggregate]
        .sort_values(["entity", "year"])
        .reset_index(drop=True)
    )
    evidence["join_counts"] = {
        "merged_rows": len(merged),
        "aggregate_rows_removed": int(merged.is_aggregate.sum()),
        "country_rows_retained": len(countries),
        "duplicate_join_keys": 0,
    }
    countries.to_csv(out / "master_dataset_countries_only.csv", index=False)

    # region lookup
    regions = pd.read_csv(raw / "region_lookup.csv")
    if regions.code.duplicated().any():
        raise ValueError("duplicate region lookup code")
    regions.to_csv(out / "region_lookup.csv", index=False)
    evidence["input_files"]["region_lookup.csv"] = _checksum(raw / "region_lookup.csv")

    # verify cohorts
    complete = countries.dropna(subset=["code", *profile])
    old = set(complete.loc[complete.year.eq(2015), "code"])
    latest = set(complete.loc[complete.year.eq(2020), "code"])
    annual = countries.loc[countries.year.between(2000, 2020)].dropna(
        subset=["code", profile[0]]
    )
    panel = annual.groupby("code").year.nunique().eq(21)
    tree = countries.loc[countries.year.eq(2020)].dropna(
        subset=["code", "internet_users_count", profile[0]]
    )
    tree = tree.loc[tree.internet_users_count.ge(0)]
    evidence["country_cohorts"] = {
        "graph_2020": len(latest),
        "matched_2015_2020": len(old & latest),
        "annual_complete_2000_2020": int(panel.sum()),
        "treemap_2020": len(tree),
        "treemap_users": int(tree.internet_users_count.round().sum()),
    }
    assert evidence["country_cohorts"] == dict(
        graph_2020=179,
        matched_2015_2020=175,
        annual_complete_2000_2020=159,
        treemap_2020=184,
        treemap_users=4521767530,
    )
    evidence["country_missing_values"] = (
        countries[profile + ["internet_users_count"]].isna().sum().to_dict()
    )

    # verify weather caches
    sampled = root / "data/scivis/gridmet_2023-07-01_2023-09-30_n8_s6.npz"
    daily = root / "data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz"
    if download_weather:
        from build_scivis import get_fields  # noqa: PLC0415
        get_fields(date(2023, 7, 1), date(2023, 9, 30), 8, 6, False)
        subprocess.run(
            [sys.executable, str(root / "scripts/shared_data_prep.py"), "--fetch-daily"],
            check=True,
        )
    if not sampled.exists() or not daily.exists():
        raise FileNotFoundError("weather caches missing in data/scivis")

    with np.load(daily) as z, np.load(sampled) as a:
        dates = z["dates"].astype("datetime64[D]")
        assert len(dates) == 92 and np.all(np.diff(dates) == np.timedelta64(1, "D"))
        assert str(dates[0]) == "2023-07-01" and str(dates[-1]) == "2023-09-30"
        assert np.array_equal(z["lat"], a["lat"]) and np.array_equal(z["lon"], a["lon"])
        mask = np.logical_and.reduce(
            [np.isfinite(z[k]).all(axis=0) for k in ["tmmx", "pr", "vs", "th"]]
        )
        assert int(mask.sum()) == 13416
        weights = np.broadcast_to(
            np.cos(np.deg2rad(z["lat"]))[:, None], mask.shape
        )
        np.savez_compressed(
            out / "weather_support.npz",
            valid_mask=mask,
            area_weights=np.where(mask, weights, 0),
            lat=z["lat"],
            lon=z["lon"],
            dates=z["dates"],
        )
        sample_dates = json.loads(
            (root / "data/scivis/manifest.json").read_text()
        )["sample_dates"]
        for i, d in enumerate(sample_dates):
            j = int(np.flatnonzero(dates == np.datetime64(d))[0])
            for k in ["tmmx", "pr", "vs", "th"]:
                np.testing.assert_allclose(a[k][i], z[k][j], equal_nan=True)
        assert -90 < float(np.nanmin(z["tmmx"])) < float(np.nanmax(z["tmmx"])) < 65
        assert np.nanmin(z["pr"]) >= 0 and np.nanmin(z["vs"]) >= 0
        assert 0 <= np.nanmin(z["th"]) <= np.nanmax(z["th"]) <= 360
        evidence["weather"] = {
            "daily_dates": 92,
            "sample_dates": sample_dates,
            "common_cells": int(mask.sum()),
            "units": {
                "tmmx": "Celsius",
                "pr": "mm/day",
                "vs": "m/s",
                "th": "degrees clockwise from north (source direction)",
            },
            "caches": {p.name: _checksum(p) for p in [sampled, daily]},
        }

    evidence["outputs"] = {
        p.name: _checksum(p)
        for p in [
            out / "master_dataset_countries_only.csv",
            out / "region_lookup.csv",
            out / "weather_support.npz",
        ]
    }
    (out / "preprocessing_audit.json").write_text(
        json.dumps(evidence, indent=2), encoding="utf8"
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "cohorts": evidence["country_cohorts"],
                "weather_cells": 13416,
                "audit": str(out / "preprocessing_audit.json"),
            },
            indent=2,
        )
    )


# export country profiles for pcp and network browser apps
def export_infovis() -> None:
    prepared = root / "data/processed"
    out_path = root / "data/infovis_countries.json"

    with (prepared / "region_lookup.csv").open(newline="", encoding="utf-8-sig") as fh:
        regions = {row["code"]: row["region"] for row in csv.DictReader(fh)}

    records: list[dict] = []
    exclusions: Counter = Counter()
    with (prepared / "master_dataset_countries_only.csv").open(
        newline="", encoding="utf-8-sig"
    ) as fh:
        for row in csv.DictReader(fh):
            year = int(row["year"])
            if year not in infovis_years:
                continue
            if row["is_aggregate"].lower() == "true":
                exclusions["aggregate"] += 1
                continue
            if not row["code"]:
                exclusions["missing country code"] += 1
                continue
            if any(not row[field] for field in infovis_fields):
                exclusions["incomplete profile"] += 1
                continue
            records.append(
                {
                    "country": row["entity"],
                    "code": row["code"],
                    "year": year,
                    "region": regions.get(row["code"], "Unclassified"),
                    **{field: float(row[field]) for field in infovis_fields},
                }
            )

    records.sort(key=lambda r: (r["year"], r["country"]))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(records)} rows to {out_path}")


# cache all 92 daily fields if requested
def fetch_weather() -> None:
    from datetime import datetime, timezone
    from netCDF4 import Dataset, num2date  # type: ignore
    from build_scivis import BASE, VARIABLES  # noqa: PLC0415

    data_dir = root / "data/scivis"
    cache_path = data_dir / "gridmet_2023-07-01_2023-09-30_daily_s6.npz"

    if cache_path.exists() and (data_dir / "daily_manifest.json").exists():
        print("reusing verified 92-day cache", flush=True)
        return

    arrays: dict = {}
    sources_meta: list = []
    lat0 = lon0 = dates0 = None
    for key, (name, _, _) in VARIABLES.items():
        url = f"{BASE}/{key}/{key}_2023.nc"
        print(f"auditing coordinates: {key}", flush=True)
        with Dataset(url) as nc:
            day = nc.variables["day"]
            time = np.asarray(day[:])
            annual_dates = [
                d.strftime("%Y-%m-%d")
                for d in num2date(
                    time, day.units, getattr(day, "calendar", "standard")
                )
            ]
            selected = [
                i
                for i, d in enumerate(annual_dates)
                if "2023-07-01" <= d <= "2023-09-30"
            ]
            dates = [annual_dates[i] for i in selected]
            assert (
                len(annual_dates) == 365
                and len(dates) == 92
                and len(set(dates)) == 92
            )
            assert np.all(np.diff(time[selected]) == 1)
            lat = np.asarray(nc.variables["lat"][::6])
            lon = np.asarray(nc.variables["lon"][::6])
            if lat0 is None:
                lat0, lon0, dates0 = lat, lon, dates
            else:
                assert (
                    dates == dates0
                    and np.array_equal(lat, lat0)
                    and np.array_equal(lon, lon0)
                )
            raw = nc.variables[name]
            pieces = []
            for month in ("07", "08", "09"):
                indices = [i for i in selected if annual_dates[i][5:7] == month]
                path = data_dir / f"daily_{key}_2023_{month}_s6.npy"
                if path.exists():
                    arr = np.load(path)
                else:
                    arr = np.ma.filled(
                        raw[indices[0]: indices[-1] + 1, ::6, ::6], np.nan
                    ).astype("float32")
                    if key == "tmmx":
                        arr -= 273.15
                    np.save(path, arr)
                assert arr.shape == (len(indices), len(lat), len(lon))
                pieces.append(arr)
            arrays[key] = np.concatenate(pieces)
            counts = [int(np.isfinite(a).sum()) for a in arrays[key]]
            assert all(c > 0 for c in counts)
            sources_meta.append(
                {
                    "key": key,
                    "url": url,
                    "variable": name,
                    "units": getattr(raw, "units", ""),
                    "selected_date_count": 92,
                    "valid_cell_counts_by_day": counts,
                    "checked_utc": datetime.now(timezone.utc).isoformat(),
                }
            )

    np.savez_compressed(
        cache_path, lat=lat0, lon=lon0, dates=np.array(dates0), **arrays
    )
    manifest = {
        "start": dates0[0],
        "end": dates0[-1],
        "date_count": 92,
        "dates": dates0,
        "spatial_stride": 6,
        "cache": str(cache_path.relative_to(root)).replace("\\", "/"),
        "sha256": _checksum(cache_path),
        "sources": sources_meta,
    }
    (data_dir / "daily_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"saved 92 daily fields: {cache_path}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--all",
        action="store_true",
        help="run full prep including weather fetch",
    )
    ap.add_argument(
        "--download-weather",
        action="store_true",
        help="fetch weather caches if missing",
    )
    ap.add_argument(
        "--fetch-daily",
        action="store_true",
        help="run daily fetch only",
    )
    args = ap.parse_args()

    if args.fetch_daily:
        fetch_weather()
        return

    preprocess(download_weather=args.download_weather or args.all)
    export_infovis()
    if args.all:
        fetch_weather()


if __name__ == "__main__":
    main()
