"""verification tests for network, figures, weather, and web structure."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]


# verify network threshold and edge counts
def verify_network() -> dict:
    processed = root / "data/processed"
    master = pd.read_csv(processed / "master_dataset_countries_only.csv")
    profile = [
        "internet_users_share_pct",
        "telephone_lines_per100",
        "broadband_subs_per100",
        "mobile_subs_per100",
    ]
    df = master.loc[master.year == 2020].dropna(subset=["code"] + profile).copy()
    n = len(df)
    x = df[profile].values.astype(float)
    x = (x - x.mean(axis=0)) / x.std(axis=0, ddof=0)
    diff = x[:, None, :] - x[None, :, :]
    dist = np.linalg.norm(diff, axis=2)
    sim = 1.0 / (1.0 + dist)
    upper = sim[np.triu_indices(n, k=1)]
    threshold = float(np.percentile(upper, 95))
    edge_count = int((upper >= threshold).sum())
    isolates = int(np.sum((sim >= threshold).sum(axis=1) - 1 == 0))

    net_data_path = root / "data/country_network_2020.json"
    result = {
        "check": "network_threshold",
        "n_countries": n,
        "threshold_p95": round(threshold, 6),
        "edge_count": edge_count,
        "isolates": isolates,
        "status": "PASS",
    }
    if net_data_path.exists():
        stored = json.loads(net_data_path.read_text(encoding="utf-8"))
        stored_edges = len(stored.get("edges", []))
        result["stored_edge_count"] = stored_edges
        result["edges_match"] = stored_edges == edge_count
        # fail if stored edge count doesn't match recomputed count
        if not result["edges_match"]:
            result["status"] = "FAIL"
    return result


# verify all 31 figure png files exist
def verify_figures() -> dict:
    report_imgs = root / "images/report"
    expected = set(range(1, 32))
    found = set()
    missing = []
    for n in expected:
        p = report_imgs / f"Fig{n}.png"
        if p.exists():
            found.add(n)
        else:
            missing.append(n)
    return {
        "check": "figure_artifacts",
        "found_count": len(found),
        "missing": missing,
        "status": "PASS" if not missing else "FAIL",
    }


# verify gridmet weather cache dates and value ranges
def verify_weather() -> dict:
    data_dir = root / "data/scivis"
    daily = data_dir / "gridmet_2023-07-01_2023-09-30_daily_s6.npz"
    sampled = data_dir / "gridmet_2023-07-01_2023-09-30_n8_s6.npz"
    result: dict = {"check": "weather_cache"}

    if not daily.exists() or not sampled.exists():
        return {**result, "status": "SKIP", "reason": "cache missing"}

    with np.load(daily) as z:
        dates = z["dates"].astype("datetime64[D]")
        assert len(dates) == 92
        assert str(dates[0]) == "2023-07-01" and str(dates[-1]) == "2023-09-30"
        tmmx = z["tmmx"]
        assert -90 < float(np.nanmin(tmmx)) < float(np.nanmax(tmmx)) < 65
        assert float(np.nanmin(z["pr"])) >= 0
        assert float(np.nanmin(z["vs"])) >= 0

    result["date_count"] = 92
    result["tmmx_range_c"] = [round(float(np.nanmin(tmmx)), 2), round(float(np.nanmax(tmmx)), 2)]
    result["status"] = "PASS"
    return result


# verify report pdf, web pages, and animations
def verify_report() -> dict:
    checks = {}
    checks["report_pdf"] = (root / "DAS732_A2_Report.pdf").exists()
    for f in ["web/index.html", "web/network.html", "web/treemap.html", "web/app.js",
              "web/network.js", "web/treemap.js", "web/pcp-curves.js"]:
        checks[f] = (root / f).exists()
    # pcp_changes moved to web/ in cleaned submission; skip this check
    # checks["pcp_changes"] = (root / "output/pcp_changes/index.html").exists()
    for gif in ["scivis_global.gif", "scivis_local.gif", "scivis_contour.gif"]:
        checks[f"gif_{gif}"] = (root / "images/scivis" / gif).exists()

    failures = [k for k, v in checks.items() if v is False]
    return {
        "check": "report_structure",
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--network", action="store_true")
    ap.add_argument("--figures", action="store_true")
    ap.add_argument("--weather", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    run_all = not any([args.network, args.figures, args.weather, args.report])

    results = []
    if args.network or run_all:
        results.append(verify_network())
    if args.figures or run_all:
        results.append(verify_figures())
    if args.weather or run_all:
        results.append(verify_weather())
    if args.report or run_all:
        results.append(verify_report())

    for r in results:
        print(json.dumps(r, indent=2))

    failures = [r for r in results if r.get("status") == "FAIL"]
    if failures:
        print("failures detected")
        raise SystemExit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
