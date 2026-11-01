"""varshith — treemap (infovis ii-b) and quiver / wind animations (scivis)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
scripts_dir = root / "scripts"


# helper to run child scripts
def _run(name: str) -> None:
    p = scripts_dir / name
    if not p.exists():
        print(f"[skip] {name} not found"); return
    print(f"  -> {name}", flush=True)
    subprocess.run([sys.executable, str(p)], cwd=root, check=True)


# load master data and region map
def _load_data() -> tuple[pd.DataFrame, dict]:
    processed = root / "data/processed"
    master = pd.read_csv(processed / "master_dataset_countries_only.csv")
    region_map = {r["code"]: r["region"]
                  for _, r in pd.read_csv(processed / "region_lookup.csv").iterrows()}
    return master, region_map


profile = [
    "internet_users_share_pct",
    "telephone_lines_per100",
    "broadband_subs_per100",
    "mobile_subs_per100",
]


# build treemap browser data and country analysis figures
def build_treemap() -> None:
    master, region_map = _load_data()

    # export treemap json for web/treemap.js
    def adoption_band(p: float) -> str:
        return ("0-below-25%" if p < 25 else "25-below-50%" if p < 50
                else "50-below-75%" if p < 75 else "75-100%")

    tree = (master.loc[master.year == 2020]
            .dropna(subset=["code", "internet_users_count", "internet_users_share_pct"])
            .loc[lambda d: d.internet_users_count >= 0].copy())
    tree["region"] = tree["code"].map(region_map).fillna("Unclassified")
    assert len(tree) == 184, f"expected 184 treemap countries, got {len(tree)}"

    nodes = [{"country": r["entity"], "code": r["code"],
              "region": r["region"],
              "adoption_band": adoption_band(float(r["internet_users_share_pct"])),
              "internet_users": int(round(r["internet_users_count"])),
              "internet_pct": float(r["internet_users_share_pct"])}
             for _, r in tree.iterrows()]
    (root / "data/treemap_data.json").write_text(
        json.dumps({"total_users": int(round(tree.internet_users_count.sum())),
                    "country_count": len(nodes), "nodes": nodes},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"treemap_data.json: {len(nodes)} countries, "
          f"{int(tree.internet_users_count.sum()):,} total users")

    # generate country comparison figures 10-12
    _build_fixed_cohorts(master, region_map)
    _build_median_shift(master, region_map)
    _build_within_region(master, region_map)


# fig 10: fixed 2000 adoption cohorts tracked to 2020
def _build_fixed_cohorts(master: pd.DataFrame, region_map: dict) -> None:
    out_img = root / "output/member_figures"; out_img.mkdir(parents=True, exist_ok=True)
    annual = master.loc[master.year.between(2000, 2020)].copy()
    annual["region"] = annual["code"].map(region_map).fillna("Unclassified")
    panel = (annual.dropna(subset=["code", "internet_users_share_pct"])
             .groupby("code").filter(lambda g: g.year.nunique() == 21))

    vals_2000 = (panel.loc[panel.year == 2000]
                 .set_index("code")["internet_users_share_pct"].sort_values())
    n = len(vals_2000); third = n // 3
    low_codes  = set(vals_2000.index[:third])
    mid_codes  = set(vals_2000.index[third:2*third])
    high_codes = set(vals_2000.index[2*third:])

    years = list(range(2000, 2021))

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(14, 5))
    for label, codes, col in [("Low start", low_codes, "#e87c2c"),
                               ("Mid start", mid_codes, "#3a86d8"),
                               ("High start", high_codes, "#2ca02c")]:
        meds = [panel.loc[(panel.code.isin(codes)) & (panel.year == y),
                          "internet_users_share_pct"].median() for y in years]
        ax_l.plot(years, meds, color=col, lw=2, label=label)
        v20 = panel.loc[(panel.code.isin(codes)) & (panel.year == 2020),
                        "internet_users_share_pct"].values
        jitter = np.random.default_rng(42).uniform(-0.15, 0.15, len(v20))
        ax_r.scatter(jitter + (["Low start","Mid start","High start"].index(label)),
                     v20, color=col, alpha=0.5, s=18)

    ax_l.set_ylabel("Internet use (%)"); ax_l.set_xlabel("Year")
    ax_l.legend(fontsize=9); ax_l.set_ylim(0, 100)
    ax_r.set_xticks([0, 1, 2]); ax_r.set_xticklabels(["Low", "Mid", "High"])
    ax_r.set_ylabel("2020 adoption (%)"); ax_r.set_ylim(0, 100)
    fig.suptitle("Fig 10. Fixed 2000 adoption cohorts tracked to 2020",
                 fontsize=11, fontweight="bold")
    fig.savefig(out_img / "Fig10.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print("Fig10 saved")


# fig 12: regional median shift vs individual country gains
def _build_median_shift(master: pd.DataFrame, region_map: dict) -> None:
    out_img = root / "output/member_figures"; out_img.mkdir(parents=True, exist_ok=True)
    matched = _get_matched(master, region_map)
    matched["region"] = matched["code"].map(region_map).fillna("Unclassified")

    m15 = matched.loc[matched.year == 2015].set_index("code")["internet_users_share_pct"]
    m20 = matched.loc[matched.year == 2020].set_index("code")["internet_users_share_pct"]
    matched_codes = set(m15.index) & set(m20.index)
    gains = {c: float(m20[c] - m15[c]) for c in matched_codes}

    regions = sorted(r for r in matched["region"].unique() if r != "Unclassified")
    med15 = {r: matched.loc[(matched.region == r) & (matched.year == 2015),
                             "internet_users_share_pct"].median() for r in regions}
    med20 = {r: matched.loc[(matched.region == r) & (matched.year == 2020),
                             "internet_users_share_pct"].median() for r in regions}

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(14, 5))
    for i, region in enumerate(regions):
        ax_l.plot([med15[region], med20[region]], [i, i], "o-", color="#3a86d8", lw=2)
        ax_l.text(med20[region] + 0.5, i,
                  f"+{med20[region]-med15[region]:.1f}pp", fontsize=7, va="center")
        region_gains = [gains[c] for c in matched_codes
                        if matched.loc[matched.code == c, "region"].iloc[0] == region
                        and c in gains]
        if region_gains:
            q25, q75 = np.percentile(region_gains, [25, 75])
            med_g = np.median(region_gains)
            ax_r.plot([q25, q75], [i, i], lw=5, color="#3a86d8", alpha=0.4)
            ax_r.scatter([med_g], [i], color="w", s=40, zorder=5, edgecolors="#3a86d8")
            rng_jitter = np.random.default_rng(732)  # fixed seed — deterministic jitter
            ax_r.scatter(region_gains, [i + rng_jitter.uniform(-0.2, 0.2) for _ in region_gains],
                         color="#3a86d8", alpha=0.3, s=10)
            ax_r.axvline(med20[region] - med15[region], ymin=(i-0.4)/len(regions),
                         ymax=(i+0.4)/len(regions), color="k", lw=1.5, ls="--")

    ax_l.set_yticks(range(len(regions))); ax_l.set_yticklabels(regions, fontsize=8)
    ax_l.set_xlabel("Internet use (%)")
    ax_l.set_title("Regional median shift (2015→2020)", fontsize=9)
    ax_r.set_yticks(range(len(regions))); ax_r.set_yticklabels(regions, fontsize=8)
    ax_r.set_xlabel("Individual country gain (pp)")
    ax_r.set_title("Country gains within region", fontsize=9)
    fig.suptitle("Fig 12. Regional median shift vs individual country gains",
                 fontsize=11, fontweight="bold")
    fig.savefig(out_img / "Fig12.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print("Fig12 saved")


# fig 11: country-level variation within regions (2020)
def _build_within_region(master: pd.DataFrame, region_map: dict) -> None:
    out_img = root / "output/member_figures"; out_img.mkdir(parents=True, exist_ok=True)
    annual = master.loc[master.year == 2020].copy()
    annual["region"] = annual["code"].map(region_map).fillna("Unclassified")
    classified = annual.loc[annual.region.ne("Unclassified")].dropna(
        subset=["internet_users_share_pct"])

    regions = sorted(classified["region"].unique())
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, region in enumerate(regions):
        vals = classified.loc[classified.region == region, "internet_users_share_pct"].values
        jitter = np.random.default_rng(0).uniform(-0.2, 0.2, len(vals))
        ax.scatter(vals, [i + j for j in jitter], color="#3a86d8", alpha=0.5, s=20)
        ax.plot([np.mean(vals)], [i], "k|", ms=12, mew=2.5)

    ax.set_yticks(range(len(regions))); ax.set_yticklabels(regions, fontsize=9)
    ax.set_xlabel("Internet use (%)"); ax.set_xlim(0, 100)
    ax.set_title("Fig 11. Country-level variation within regions (2020)",
                 fontsize=11, fontweight="bold")
    fig.savefig(out_img / "Fig11.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print("Fig11 saved")


# filter matched 2015 and 2020 country records
def _get_matched(master: pd.DataFrame, region_map: dict) -> pd.DataFrame:
    complete = master.dropna(subset=["code"] + profile)
    old = set(complete.loc[complete.year == 2015, "code"])
    new = set(complete.loc[complete.year == 2020, "code"])
    codes = old & new
    matched = complete.loc[complete.code.isin(codes)].copy()
    matched["region"] = matched["code"].map(region_map).fillna("Unclassified")
    return matched


# build wind quiver figures and gif animations
def build_quiver() -> None:
    for script in [
        "build_scivis.py",
        "build_scivis_results.py",
    ]:
        _run(script)
    print("quiver and animation figures complete")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--treemap", action="store_true")
    ap.add_argument("--quiver",  action="store_true")
    args = ap.parse_args()
    run_all = not (args.treemap or args.quiver)
    if args.treemap or run_all: build_treemap()
    if args.quiver  or run_all: build_quiver()


if __name__ == "__main__":
    main()
