"""Create two horizon and two ridgeline variations from A1 annual country data.

Run from ass2: python scripts/build_temporal_figures.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_dataset_countries_only.csv"
REGIONS = ROOT / "data/processed/region_lookup.csv"
DATA = ROOT / "data"
IMAGES = ROOT / "images"
START, END = 2000, 2020
REGION_ORDER = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]
REGION_COLORS = {
    "Africa": "#bd4c43", "Asia": "#6b54a3", "Europe": "#3476b6",
    "North America": "#d29328", "South America": "#399269", "Oceania": "#36a0a8",
}
BG, INK, GRID = "#ffffff", "#172434", "#e3e8ee"


def load_panel() -> pd.DataFrame:
    raw = pd.read_csv(SOURCE)
    raw = raw.loc[raw.year.between(START, END)].dropna(
        subset=["code", "internet_users_share_pct"]
    ).copy()
    counts = raw.groupby("code").year.nunique()
    valid = counts[counts.eq(END - START + 1)].index
    panel = raw.loc[raw.code.isin(valid)].copy()
    lookup = pd.read_csv(REGIONS).set_index("code").region.to_dict()
    panel["region"] = panel.code.map(lookup).fillna("Unclassified")
    assert not panel.duplicated(["code", "year"]).any()
    assert panel.groupby("code").year.nunique().eq(END - START + 1).all()
    DATA.mkdir(exist_ok=True)
    panel[["entity", "code", "year", "region", "internet_users_share_pct"]].to_csv(
        DATA / "internet_panel_2000_2020.csv", index=False
    )
    return panel


def horizon(ax, series: list[tuple[str, np.ndarray]], title: str) -> None:
    years = np.arange(START, END + 1)
    def milestone(values):
        hits=years[values>=50]
        return int(hits[0]) if len(hits) else 9999
    series=sorted(series,key=lambda item:(milestone(item[1]),item[0]))
    for i, (label, values) in enumerate(series):
        base = i + .82
        deviation = values - 50
        for band in (0, 1):
            for sign, colors in ((1, ("#a6cee3", "#2877b2")), (-1, ("#f3aaa5", "#bd4c43"))):
                level = np.clip(sign * deviation - band * 25, 0, 25) / 25
                ax.fill_between(years, base, base - .68 * level,
                                color=colors[band], linewidth=0, zorder=3+band)
        ax.hlines(base, START, END, color="#a9b7c3", lw=.55, zorder=2)
        ax.text(START-.4, base-.32, label, ha="right", va="center", color=INK, fontsize=9)
        first=milestone(values)
        stamp='by 2000' if first==2000 else str(first) if first!=9999 else 'not by 2020'
        ax.text(END+.65,base-.32,f'{values[-1]:.1f}% | {stamp}',va='center',fontsize=9,color=INK)
        if START < first <= END:
            ax.plot(first,base-.34,'o',ms=3,color=INK)
    ax.set_xlim(START-.2, END+5.2)
    ax.set_ylim(len(series)+.05, -.15)
    ax.set_yticks([])
    ax.set_xticks([2000, 2005, 2010, 2015, 2020])
    ax.set_xlabel("Year | dots mark first observed 50% attainment; right labels: 2020 value | first attainment", fontsize=9)
    ax.grid(axis="x", color=GRID, lw=.7)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_title(title, loc="left", fontsize=14, color=INK, pad=12)
    legend = [Patch(color="#a6cee3", label="0–25 pp above 50%"),
              Patch(color="#2877b2", label="25–50 pp above"),
              Patch(color="#f3aaa5", label="0–25 pp below 50%"),
              Patch(color="#bd4c43", label="25–50 pp below")]
    ax.figure.legend(handles=legend, loc="lower center", bbox_to_anchor=(.5,.065), ncol=4,
                     frameon=False, fontsize=8)


def build_horizons(panel: pd.DataFrame) -> None:
    latest = panel.loc[panel.year.eq(END)]
    selected = []
    selection_records = []
    for region in REGION_ORDER:
        group = latest.loc[latest.region.eq(region)].sort_values("internet_users_share_pct")
        if len(group) < 2: continue
        for quantile in (.25, .75):
            target = group.internet_users_share_pct.quantile(quantile)
            row = group.iloc[(group.internet_users_share_pct - target).abs().to_numpy().argmin()]
            if row.code in [s["code"] for s in selected]:
                row = group.loc[~group.code.isin([s["code"] for s in selected])].iloc[0]
            selected.append({"code":row.code,"country":row.entity,"region":region,"quantile":quantile})
            selection_records.append(selected[-1])
    country_series=[]
    for item in selected:
        values = panel.loc[panel.code.eq(item["code"])].sort_values("year").internet_users_share_pct.to_numpy()
        country_series.append((f"{item['country']}  ·  {item['region']}",values))
    fig,ax=plt.subplots(figsize=(15,10),dpi=180)
    horizon(ax,country_series,"Horizon A · Country trajectories around the 50% internet-use milestone")
    fig.text(.5,.025,"Two countries per classified region: nearest to its 2020 25th and 75th percentile; all years retained.",
             ha="center",fontsize=9,color="#526579")
    fig.tight_layout(rect=[.17,.17,1,.96])
    fig.savefig(IMAGES/"horizon_countries.png",bbox_inches="tight")
    plt.close(fig)

    medians=panel.loc[panel.region.isin(REGION_ORDER)].groupby(["region","year"]).internet_users_share_pct.median()
    region_series=[(f"{r}  ·  n={panel.loc[panel.region.eq(r),'code'].nunique()}",
                    medians.loc[r].reindex(range(START,END+1)).to_numpy()) for r in REGION_ORDER]
    fig,ax=plt.subplots(figsize=(14,6.5),dpi=180)
    horizon(ax,region_series,"Horizon B · Median country trajectory by region")
    fig.text(.5,.025,"Each regional median gives every included country equal weight; the country panel is fixed over 2000–2020.",
             ha="center",fontsize=9,color="#526579")
    fig.tight_layout(rect=[.15,.17,1,.95])
    fig.savefig(IMAGES/"horizon_regions.png",bbox_inches="tight")
    plt.close(fig)
    (DATA/"horizon_country_selection.json").write_text(
        json.dumps(selection_records,indent=2),encoding="utf-8"
    )
    medians.rename("median_internet_pct").to_csv(DATA/"region_median_internet_2000_2020.csv")


def reflected_kde(values: np.ndarray, grid: np.ndarray, bandwidth: float = 6.0) -> np.ndarray:
    """Gaussian density on [0,100] with reflections at both boundaries."""
    def kernel(points):
        z = (grid[:,None]-points[None,:])/bandwidth
        return np.exp(-.5*z*z).sum(axis=1)
    normalizer=len(values)*bandwidth*np.sqrt(2*np.pi)
    return (kernel(values)+kernel(-values)+kernel(200-values))/normalizer


def ridge_axis(ax, records: list[tuple[str,np.ndarray]], title: str, palette: list[str]) -> None:
    grid=np.linspace(0,100,401)
    for i,(label,values) in enumerate(records):
        density=reflected_kde(values,grid)
        base=i+.85
        shape=.72*density/max(density.max(),1e-12)
        ax.fill_between(grid,base,base-shape,color=palette[i%len(palette)],alpha=.84,lw=0)
        ax.plot(grid,base-shape,color=palette[i%len(palette)],lw=1)
        ax.hlines(base,0,100,color="#c9d2dc",lw=.55)
        ax.plot(values,np.full(len(values),base), '|',color=INK,alpha=.5,ms=4,mew=.65)
        med=float(np.median(values))
        ax.plot([med],[base-.72*np.interp(med,grid,density)/max(density.max(),1e-12)],
                marker="|",color=INK,ms=8)
        ax.text(-2,base-.31,f"{label}  n={len(values)}",ha="right",va="center",fontsize=8,color=INK)
        ax.text(102,base-.31,f'{med:.1f}%',va='center',fontsize=8,color=INK)
    ax.set_xlim(0,112);ax.set_ylim(len(records)+.07,-.12)
    ax.set_xticks([0,25,50,75,100]);ax.set_yticks([])
    ax.set_xlabel("People using the internet (%)",fontsize=9)
    ax.set_title(title,loc="left",fontsize=12,color=INK)
    ax.grid(axis="x",color=GRID,lw=.6)
    for s in ax.spines.values():s.set_visible(False)


def build_ridges(panel: pd.DataFrame) -> None:
    years=(2000,2005,2010,2015,2020)
    global_records=[(str(year),panel.loc[panel.year.eq(year),"internet_users_share_pct"].to_numpy())
                    for year in years]
    grid=np.linspace(0,100,401)
    regional_records={r:[(str(year),panel.loc[panel.year.eq(year)&panel.region.eq(r),
                                       "internet_users_share_pct"].to_numpy()) for year in years]
                      for r in REGION_ORDER}
    colors=["#b9d5e8","#89b9d5","#5f9bc1","#357bac","#195d8d"]
    fig,ax=plt.subplots(figsize=(13,6.7),dpi=180)
    ridge_axis(ax,global_records,"Ridgeline A · Distribution across the same countries",colors)
    fig.text(.5,.025,"159-country fixed panel · 6-point reflected KDE · heights normalized separately · baseline ticks: countries; right labels: medians.",
             ha="center",fontsize=8,color="#526579")
    fig.tight_layout(rect=[.1,.06,1,.96])
    fig.savefig(IMAGES/"ridgeline_years.png",bbox_inches="tight")
    plt.close(fig)

    fig,axes=plt.subplots(2,3,figsize=(17,10),dpi=180)
    for ax,region in zip(axes.flat,REGION_ORDER):
        ridge_axis(ax,regional_records[region],f"{region} · same 5 years",colors)
    fig.suptitle("Ridgeline B · How adoption distributions moved within each region",fontsize=16,color=INK)
    fig.text(.5,.025,"Fixed regional cohorts · baseline ticks: individual countries; right labels: medians · 6-point reflected KDE; ridge heights normalized separately. Small-sample bumps are exploratory.",
             ha="center",fontsize=9,color="#526579")
    fig.tight_layout(rect=[.05,.05,1,.94],w_pad=3,h_pad=2)
    fig.savefig(IMAGES/"ridgeline_regions.png",bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    IMAGES.mkdir(exist_ok=True)
    panel=load_panel()
    build_horizons(panel)
    build_ridges(panel)
    info={"period":[START,END],"countries":int(panel.code.nunique()),
          "rows":len(panel),"unclassified_countries":panel.loc[panel.region.eq("Unclassified"),"code"].nunique(),
          "excluded_rule":"countries missing internet share in any year 2000-2020",
          "ridgeline_bandwidth_percentage_points":6}
    (DATA/"temporal_coverage.json").write_text(json.dumps(info,indent=2),encoding="utf-8")
    print("Created four temporal figures for",info["countries"],"countries")


if __name__=="__main__":
    main()
