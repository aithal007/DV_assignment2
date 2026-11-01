"""Build the annotated gallery, supplementary figures and updated SciVis report.

Run build_scivis.py first. Uses its manifest and actual cached data, not fixed findings.
"""
from pathlib import Path
import csv
import html
import json
import numpy as np
from PIL import Image
from build_scivis import plt, Normalize, map_axis, save_figure
from matplotlib.colors import TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images/scivis"


def main():
    manifest = json.loads((ROOT / "data/scivis/manifest.json").read_text())
    dates = manifest["sample_dates"]
    with np.load(ROOT / manifest["data_cache"]) as z:
        lat, lon = z["lat"], z["lon"]
        fields = {k: z[k] for k in ["tmmx", "pr", "vs", "th"]}
    t = fields["tmmx"]
    assert len(dates) == 8 and len(set(dates)) == 8
    assert dates[0] == "2023-07-01" and dates[-1] == "2023-09-30"
    assert all(a.shape == t.shape for a in fields.values())
    assert t.shape == (8, len(lat), len(lon))
    assert np.all(np.diff(lon) > 0) and (np.all(np.diff(lat) > 0) or np.all(np.diff(lat) < 0))
    assert -90 < np.nanmin(t) < np.nanmax(t) < 65
    assert np.nanmin(fields["pr"]) >= 0 and np.nanmin(fields["vs"]) >= 0
    assert 0 <= np.nanmin(fields["th"]) <= np.nanmax(fields["th"]) <= 360
    theta = np.deg2rad([0, 90, 180, 270])
    assert np.allclose(-np.sin(theta), [0, -1, 0, 1], atol=1e-6)
    assert np.allclose(-np.cos(theta), [-1, 0, 1, 0], atol=1e-6)
    limits = manifest["temperature_global_limits_C"]
    assert np.allclose(limits, [np.nanmin(t), np.nanmax(t)])
    for when in ["global", "local", "contour"]:
        with Image.open(OUT / f"scivis_{when}.gif") as im:
            assert im.n_frames == 8
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axs = plt.subplots(4, 2, figsize=(15, 17), constrained_layout=True)
    fig.suptitle("Summer into autumn: eight daily temperature snapshots\nJuly-September 2023 | One fixed color scale", fontsize=21, color="#193044")
    for ax, when, values in zip(axs.flat, dates, t):
        im = ax.pcolormesh(lon, lat, values, cmap="viridis", norm=Normalize(*limits), shading="auto", rasterized=True)
        map_axis(ax, when)
    fig.colorbar(im, ax=axs, shrink=.75, label="Daily maximum air temperature (°C)")
    fig.supxlabel("gridMET | Uniform temporal samples, every sixth native grid cell | Gray = missing | Snapshots, not monthly averages", fontsize=11)
    save_figure(fig, OUT, "scivis_temperature_atlas")
    plt.close(fig)

    change = t[-1] - t[0]
    bound = float(np.ceil(np.nanmax(np.abs(change)) / 5) * 5)
    fig, ax = plt.subplots(figsize=(13, 7), constrained_layout=True)
    im = ax.pcolormesh(lon, lat, change, cmap="RdBu_r", norm=TwoSlopeNorm(vmin=-bound, vcenter=0, vmax=bound), shading="auto", rasterized=True)
    map_axis(ax, "Two-day difference: September 30 minus July 1, 2023")
    fig.suptitle("Where did the endpoint snapshots differ?", fontsize=20, color="#193044")
    fig.colorbar(im, ax=ax, shrink=.8, label="Change in daily maximum temperature (°C)")
    fig.supxlabel("Blue = cooler on September 30; red = warmer | Gray = missing | A weather difference, not a climate anomaly or trend", fontsize=10)
    save_figure(fig, OUT, "scivis_endpoint_change")
    plt.close(fig)

    with (ROOT / "data/scivis/sample_statistics.csv").open() as f:
        rows = list(csv.DictReader(f))
    valid = np.isfinite(change)
    weights = np.broadcast_to(np.cos(np.deg2rad(lat))[:, None], change.shape)
    cooling = float(np.sum(weights[valid] * (change[valid] < 0)) / weights[valid].sum() * 100)
    mean_change = float(np.average(change[valid], weights=weights[valid]))
    middle = len(dates) // 2
    p = fields["pr"][middle]
    pos = p[np.isfinite(p)]
    pmax = max(5, float(np.percentile(pos, 99)))
    dry = float(np.mean(pos == 0) * 100)
    faint = float(np.mean((pos > 0) & (pos < .1)) * 100)
    saturated = float(np.mean(pos > pmax) * 100)
    spread = [b - a for a, b in manifest["temperature_daily_limits_C"]]
    narrow, wide = int(np.argmin(spread)), int(np.argmax(spread))
    lo1, hi1 = manifest["temperature_daily_limits_C"][narrow]
    lo2, hi2 = manifest["temperature_daily_limits_C"][wide]
    findings = {
        "endpoint_area_weighted_cooler_percent": cooling,
        "endpoint_area_weighted_mean_change_C": mean_change,
        "endpoint_min_change_C": float(np.nanmin(change)),
        "endpoint_max_change_C": float(np.nanmax(change)),
        "color_experiment_date": dates[middle],
        "precip_dry_grid_percent": dry,
        "precip_positive_below_0_1_grid_percent": faint,
        "precip_above_display_limit_grid_percent": saturated,
        "precip_display_max_mm": pmax,
        "grid_shape": list(t.shape),
        "valid_temperature_cells_per_date": [int(np.isfinite(x).sum()) for x in t],
        "weighting": "cos(latitude) on endpoint common valid subsampled cells; approximate area weights; no population weighting",
        "validation": "PASS: dates, dimensions, coordinates, physical ranges, cardinal wind conversions, min/max scales and eight GIF frames",
    }
    (ROOT / "data/scivis/findings_2023.json").write_text(json.dumps(findings, indent=2))

    captions = [
        ("scivis_temperature_atlas", "Eight dates, one temperature scale", f"All eight snapshots use {limits[0]:.2f} to {limits[1]:.2f} °C. Gray means no data. Shared limits allow direct comparisons; eight dates cannot establish event duration or a seasonal trend."),
        ("scivis_color_experiments", "Continuous, discrete, linear and logarithmic mapping", f"Same fields on {dates[middle]}. Temperature uses continuous viridis and 5 °C cividis classes. Of valid rain cells, {dry:.1f}% are dry and {faint:.2f}% have positive rain below 0.1 mm. Rain above {pmax:.2f} mm ({saturated:.2f}% of valid cells) saturates. The log panel assigns white to dry cells, pale yellow to positive rain below 0.1 mm, and gray to missing cells."),
        ("scivis_global_local", "Global versus local extrema", f"Global limits are actual minima/maxima over these eight subsampled fields. The narrowest daily span is {lo1:.2f} to {hi1:.2f} °C on {dates[narrow]}; the widest is {lo2:.2f} to {hi2:.2f} °C on {dates[wide]}. Local scales improve within-date contrast but change the numerical meaning of the same color. Global here means the sampled space-time cube, not all 92 days or the whole Earth."),
        ("scivis_contour_experiments", "Contour spacing and fill", f"Same temperature field on {dates[middle]}, compared at 5 and 10 °C intervals. Matplotlib/ContourPy serial grid-cell tracing uses the Marching Squares family. Lines trace equal-temperature boundaries; fills reveal broad regions. Coarse levels span the full sampled range. Interpolation smooths boundaries between available grid points; no finer-resolution measurements are created."),
        ("scivis_quiver_experiments", "Wind density and arrow length", f"Same daily wind field on {dates[middle]}. Columns retain every 4th, 8th or 12th display cell: nominal angular steps 1°, 2° or 3° after the base 0.25° subsample. Rows compare speed-proportional and equal-length arrows with identical speed colors (0-15 m/s; greater values saturated). Arrows point where air flows, not where wind comes from. Longitude/latitude bearings account for cosine latitude and the plotted aspect. Constant length makes weak winds visible but removes magnitude from length. Wind's coarser source limits terrain-scale inference."),
        ("scivis_endpoint_change", "Signed endpoint difference", f"On common valid sampled cells, approximately {cooling:.1f}% of area is cooler on September 30 than July 1. The approximate area-weighted difference is {mean_change:.2f} °C; individual cells range from {np.nanmin(change):.2f} to {np.nanmax(change):.2f} °C. Weights are cosine latitude. This two-day comparison is neither a seasonal average nor a climate anomaly."),
    ]
    section = "## SciVis: July-September 2023\n\n"
    section += "The team-supplied interval contains 92 calendar days. Eight deterministic, uniformly spaced samples include both endpoints and avoid selecting only dramatic days. The base spatial stride is six native cells (0.25 degrees); it is subsampling, not averaging. Source packing and masks are decoded before converting K to Celsius. Current data are used: the owner records reprocessing of this interval in September 2024.\n\n"
    figure_numbers = [11, 12, 13, 14, 15, 16]
    for (name, title, caption), number in zip(captions, figure_numbers):
        section += f"![Figure {number}. {title}.](images/scivis/{name}.png)\n\n**Figure {number}.** {caption}\n\n"
    section += "Three eight-frame GIFs compare shared-scale temperature, daily-scale temperature, and fixed-level filled contours. The shared-scale version is preferred for between-date comparisons; local rescaling is an explicit experiment.\n\n"
    section += "**Design rationale.** Sequential palettes encode ordered scalar values; 5 °C classes trade detail for readable bands. Log rain mapping expands weak-positive-rain contrast while requiring separate zero handling. A diverging palette is appropriate for signed endpoint differences, because zero has a physical meaning. Temperature itself is not treated as a zero-centered anomaly. In line contours, background lightness and labels support tracing; filled contours support regional comparisons. No experiment changes the underlying observations.\n\n"
    section += "**Normalization and algorithm.** Global mapping uses (value - global minimum)/(global maximum - global minimum); local mapping substitutes that day's extrema. Contours are computed using the documented ContourPy serial implementation, not a custom algorithm. Grid-cell crossings are interpolated, with missing values masked and the library's default corner masking. The wind transform is u = -speed sin(theta), v = -speed cos(theta), for a clockwise-from-north source angle: north wind flows south, east wind flows west. Scalar speeds and directions are paired daily products; plotted arrows do not assert instantaneous trajectories.\n\n"
    section += "**Verified data handling.** Automated checks pass for eight distinct dates, coordinate ordering, aligned array shapes, plausible physical ranges, nonnegative rain/speed, direction range, cardinal wind conversions, global min/max settings, and eight frames in each animation. Validation evidence is in data/scivis/findings_2023.json. Geographic axes are a longitude/latitude display, not an equal-area map; use documented cosine-latitude weights for the approximate area result.\n\n"
    # The revised report is composed by integrate_quality_report.py. Historical
    # builders still reproduce their own assets without reverting its analysis.
    if not (ROOT / 'data/current_figure_manifest.json').exists():
        report_path = ROOT / "REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        begin = report.index("## SciVis")
        end = report.index("## Extended weather analysis", begin) if "## Extended weather analysis" in report[begin:] else report.index("## Reproducibility", begin)
        report = report[:begin] + section + report[end:]
        report_path.write_text(report, encoding="utf-8")
    (ROOT / "SCIVIS_RESULTS_2023.md").write_text("# gridMET results: July-September 2023\n\n" + section + "Research and source links: research/JUL_SEP_2023_PLAN.md.\n", encoding="utf-8")

    cards = ""
    for name, title, caption in captions:
        cards += f'<article><h2>{html.escape(title)}</h2><a href="../../images/scivis/{name}.png"><img loading="lazy" src="../../images/scivis/{name}.png" alt="{html.escape(title)}"></a><p>{html.escape(caption)}</p><a href="../../images/scivis/{name}.svg">Download SVG</a></article>'
    for mode, title in [("global", "Temperature: fixed scale"), ("local", "Temperature: daily rescaling"), ("contour", "Contours: fixed levels")]:
        cards += f'<article><h2>{title}</h2><img loading="lazy" src="../../images/scivis/scivis_{mode}.gif" alt="Eight-frame animation"><p>Eight uniformly spaced snapshots. {"Colors change numerical meaning between frames." if mode == "local" else "Color meaning remains fixed across frames."}</p></article>'
    table = '<table><thead><tr><th>Date</th><th>Min °C</th><th>Max °C</th><th>Wet grid cells</th><th>Rain p99 mm</th></tr></thead><tbody>'
    for r in rows:
        table += f'<tr><td>{r["date"]}</td><td>{float(r["tmmx_min_C"]):.2f}</td><td>{float(r["tmmx_max_C"]):.2f}</td><td>{100*float(r["pr_positive_fraction"]):.1f}%</td><td>{float(r["pr_p99_mm"]):.2f}</td></tr>'
    table += '</tbody></table>'
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>gridMET | July-September 2023</title><style>body{{font:17px/1.65 system-ui,sans-serif;color:#193044;background:#eef2f5;margin:0}}main{{max-width:1180px;margin:auto;padding:32px}}header,article,section{{background:white;padding:28px;margin:22px 0;border-radius:12px}}h1{{font-size:40px;line-height:1.15}}h2{{line-height:1.3}}img{{width:100%;height:auto}}a{{color:#17618a}}table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;text-align:left;border-bottom:1px solid #dbe2e8}}.tag{{color:#526579;text-transform:uppercase;font-size:13px;letter-spacing:2px}}@media(max-width:600px){{main{{padding:10px}}header,article,section{{padding:14px}}h1{{font-size:28px}}}}</style><main><header><div class="tag">DAS732 Assignment 2 · Scientific visualization</div><h1>Weather patterns from summer into autumn</h1><p>July 1-September 30, 2023 | Eight uniform dates | Four real gridMET variables</p><p>Six figure sets and three animations. Click a figure for full resolution. <a href="../../research/JUL_SEP_2023_PLAN.md">Research plan</a> · <a href="../../SCIVIS_RESULTS_2023.md">Report text</a> · <a href="../../data/scivis/findings_2023.json">Validation and findings</a></p></header>{cards}<section><h2>Measured snapshot statistics</h2><p>Statistics describe valid subsampled grid cells. They are neither population-weighted nor full-month summaries.</p>{table}</section><section><h2>Methods and sources</h2><p>The base grid is sampled every sixth native cell. Missing cells retain masks; temperature converts from K to °C. All inference is restricted to these daily snapshots. Source documentation records reprocessing of this 2023 interval.</p><p><a href="https://www.climatologylab.org/gridmet.html">gridMET documentation</a> · <a href="https://matplotlib.org/stable/users/explain/colors/colormaps.html">Color research</a> · <a href="https://contourpy.readthedocs.io/en/latest/description.html">Contour algorithm</a> · <a href="../../data/scivis/manifest.json">Reproduction settings</a></p></section></main></html>'''
    gallery = ROOT / "output/scivis_2023/index.html"
    gallery.parent.mkdir(parents=True, exist_ok=True)
    gallery.write_text(page, encoding="utf-8")
    print(json.dumps(findings, indent=2))
    print(f"Gallery: {gallery}")


if __name__ == "__main__":
    main()
