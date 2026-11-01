"""sindhoor — horizon and ridgeline plots (infovis iii) and contours (scivis)."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

root = Path(__file__).resolve().parents[1]
scripts_dir = root / "scripts"


# helper to run child scripts
def _run(name: str) -> None:
    p = scripts_dir / name
    if not p.exists():
        print(f"[skip] {name} not found"); return
    print(f"  -> {name}", flush=True)
    subprocess.run([sys.executable, str(p)], cwd=root, check=True)


# load 159-country balanced panel
def _load_panel() -> tuple[pd.DataFrame, dict]:
    processed = root / "data/processed"
    master = pd.read_csv(processed / "master_dataset_countries_only.csv")
    region_map = {r["code"]: r["region"]
                  for _, r in pd.read_csv(processed / "region_lookup.csv").iterrows()}
    annual = master.loc[master.year.between(2000, 2020)].copy()
    annual["region"] = annual["code"].map(region_map).fillna("Unclassified")
    panel = (annual.dropna(subset=["code", "internet_users_share_pct"])
             .groupby("code").filter(lambda g: g.year.nunique() == 21))
    return panel, region_map


# draw single folded horizon row
def _draw_horizon_row(ax: plt.Axes, years: list, values: list,
                      ref: float = 50.0, band: float = 25.0, label: str = "") -> None:
    vals = np.array(values, dtype=float)
    diff = vals - ref
    pos = np.where(diff > 0, diff, 0.0)
    neg = np.where(diff < 0, -diff, 0.0)
    n_bands = max(2, int(np.ceil(max(np.nanmax(pos), np.nanmax(neg)) / band)))
    blues = plt.cm.Blues(np.linspace(0.35, 0.85, n_bands))
    reds  = plt.cm.Reds(np.linspace(0.35, 0.85, n_bands))
    for b in range(n_bands):
        lo, hi = b * band, (b + 1) * band
        ax.fill_between(years, 0, np.clip(pos - lo, 0, band), color=blues[b], step="post")
        ax.fill_between(years, 0, np.clip(neg - lo, 0, band), color=reds[b],  step="post")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_yticks([])
    ax.set_ylabel(label, fontsize=7, rotation=0, ha="right", va="center", labelpad=4)


# build horizon rows and ridgeline distributions
def build_horizon() -> None:
    panel, region_map = _load_panel()
    out_img = root / "output/member_figures"; out_img.mkdir(parents=True, exist_ok=True)
    years = list(range(2000, 2021))

    # fig 13: selected country horizon rows
    classified = panel.loc[panel.region.ne("Unclassified")]
    selections: list[str] = []
    for region, grp in classified.groupby("region"):
        v20 = grp.loc[grp.year == 2020].set_index("code")["internet_users_share_pct"]
        q25, q75 = v20.quantile([0.25, 0.75])
        low  = v20[v20 <= q25]; high = v20[v20 >= q75]
        if len(low):  selections.append(low.idxmin())
        if len(high): selections.append(high.idxmax())

    fig, axes = plt.subplots(len(selections), 1,
                             figsize=(12, len(selections) * 0.55),
                             sharex=True, gridspec_kw={"hspace": 0.05})
    if len(selections) == 1: axes = [axes]
    for ax, code in zip(axes, selections):
        row  = panel.loc[panel.code == code].set_index("year")
        name = row["entity"].iloc[0]
        vals = [row.loc[y, "internet_users_share_pct"] if y in row.index else float("nan")
                for y in years]
        v20  = row.loc[2020, "internet_users_share_pct"] if 2020 in row.index else float("nan")
        _draw_horizon_row(ax, years, vals, label=f"{name} ({v20:.1f}%)")
    axes[-1].set_xticks(years[::5])
    axes[-1].set_xticklabels([str(y) for y in years[::5]], fontsize=7)
    fig.suptitle("Fig 14. Selected country horizon (ref=50%, band=25pp)",
                 fontsize=11, fontweight="bold")
    fig.savefig(out_img / "Fig14.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"Fig14 saved ({len(selections)} rows)")

    # fig 14: regional median horizon rows
    regions_ordered = sorted(panel.loc[panel.region.ne("Unclassified"), "region"].unique())
    fig, axes = plt.subplots(len(regions_ordered), 1,
                             figsize=(12, len(regions_ordered) * 0.7),
                             sharex=True, gridspec_kw={"hspace": 0.05})
    if len(regions_ordered) == 1: axes = [axes]
    for ax, region in zip(axes, regions_ordered):
        grp = panel.loc[panel.region == region]
        meds = [grp.loc[grp.year == y, "internet_users_share_pct"].median() for y in years]
        m20  = grp.loc[grp.year == 2020, "internet_users_share_pct"].median()
        _draw_horizon_row(ax, years, meds, label=f"{region} ({m20:.2f}%)")
    axes[-1].set_xticks(years[::5])
    axes[-1].set_xticklabels([str(y) for y in years[::5]], fontsize=7)
    fig.suptitle("Fig 15. Regional median horizon (ref=50%)",
                 fontsize=11, fontweight="bold")
    fig.savefig(out_img / "Fig17_bandwidth_sensitivity.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print("Fig17_bandwidth_sensitivity saved")

    # fig 15: global ridgeline across 5 years
    slice_years = [2000, 2005, 2010, 2015, 2020]
    x_grid  = np.linspace(0, 100, 500)
    palette = plt.cm.plasma(np.linspace(0.2, 0.85, len(slice_years)))

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, yr in enumerate(reversed(slice_years)):
        vals = panel.loc[panel.year == yr, "internet_users_share_pct"].dropna().values
        if len(vals) < 5: continue
        kde  = gaussian_kde(np.concatenate([vals, -vals, 200 - vals]), bw_method=6/100)
        dens = kde(x_grid) * 3
        med  = float(np.median(vals))
        ax.fill_between(x_grid, i * 0.6, i * 0.6 + dens, color=palette[i], alpha=0.7)
        ax.axvline(med, ymin=i*0.6/(len(slice_years)*0.7),
                   ymax=(i*0.6+dens.max())/(len(slice_years)*0.7),
                   color="k", lw=1.2, ls="--")
        ax.text(med + 1, i * 0.6 + 0.02, f"{yr}  med {med:.1f}%", fontsize=7, va="bottom")
    ax.set_xlabel("Internet use (%)"); ax.set_yticks([]); ax.set_xlim(0, 100)
    ax.set_title("Fig 15. Global ridgeline: 159-country adoption distribution",
                 fontsize=11, fontweight="bold")
    fig.savefig(out_img / "Fig17_bandwidth_sensitivity.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print("Fig17_bandwidth_sensitivity saved")

    # fig 16: regional ridgelines faceted
    ncols = 3
    nrows = int(np.ceil(len(regions_ordered) / ncols))
    fig, axes_grid = plt.subplots(nrows, ncols, figsize=(15, nrows * 3), sharex=True)
    axes_flat = axes_grid.flatten()
    for ax, region in zip(axes_flat, regions_ordered):
        n_ctry = panel.loc[panel.region == region, "code"].nunique()
        for i, yr in enumerate(reversed(slice_years)):
            vals = panel.loc[(panel.region == region) & (panel.year == yr),
                             "internet_users_share_pct"].dropna().values
            if len(vals) < 3: continue
            kde  = gaussian_kde(np.concatenate([vals, -vals, 200 - vals]), bw_method=6/100)
            dens = kde(x_grid) * 3
            ax.fill_between(x_grid, i * 0.6, i * 0.6 + dens, color=palette[i], alpha=0.7)
            ax.text(101, i * 0.6 + 0.02, str(yr), fontsize=6)
        ax.set_title(f"{region} (n={n_ctry})", fontsize=8)
        ax.set_xlim(0, 100); ax.set_yticks([])
    for ax in axes_flat[len(regions_ordered):]: ax.set_visible(False)
    fig.suptitle("Fig 17. Regional ridgelines: adoption distribution by region",
                 fontsize=11, fontweight="bold")
    fig.supxlabel("Internet use (%)", fontsize=9)
    fig.savefig(out_img / "Fig17_bandwidth_sensitivity.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print("Fig17_bandwidth_sensitivity saved")

    # fig 17: bandwidth sensitivity comparison
    vals_2020 = panel.loc[panel.year == 2020, "internet_users_share_pct"].dropna().values
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(12, 4))
    for bw, col in [(3, "#1f77b4"), (6, "#ff7f0e"), (12, "#2ca02c")]:
        kde = gaussian_kde(np.concatenate([vals_2020, -vals_2020, 200 - vals_2020]),
                           bw_method=bw/100)
        ax_l.plot(x_grid, kde(x_grid) * 3, label=f"bw={bw}", color=col)
    ax_l.set_title("KDE sensitivity (2020, bw 3/6/12 pp)"); ax_l.set_xlabel("Internet use (%)")
    ax_l.legend(fontsize=8)
    sv = np.sort(vals_2020)
    ax_r.step(sv, np.arange(1, len(sv)+1)/len(sv), color="k", label="ECDF")
    ax_r.axvline(np.median(sv), color="orange", ls="--", label=f"Median {np.median(sv):.1f}%")
    ax_r.set_xlabel("Internet use (%)"); ax_r.set_ylabel("Cumulative fraction")
    ax_r.set_title("ECDF (2020)"); ax_r.legend(fontsize=8)
    fig.suptitle("Supplement: Ridgeline sensitivity: bandwidth comparison + ECDF",
                 fontsize=11, fontweight="bold")
    fig.savefig(out_img / "Fig17_bandwidth_sensitivity.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print("Fig17_bandwidth_sensitivity saved")


# build marching squares contours and monthly maps
def build_contours() -> None:
    for script in [
        "build_scivis.py",
        "build_extended_figures.py",
        "build_quality_figures.py",
    ]:
        _run(script)
    print("contour and monthly map figures complete")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--horizon",  action="store_true")
    ap.add_argument("--contours", action="store_true")
    args = ap.parse_args()
    run_all = not (args.horizon or args.contours)
    if args.horizon  or run_all: build_horizon()
    if args.contours or run_all: build_contours()


if __name__ == "__main__":
    main()
