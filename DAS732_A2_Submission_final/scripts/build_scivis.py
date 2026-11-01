"""Fetch sampled gridMET fields and produce the A2 SciVis comparisons.

The default period is the team's supplied July-September 2023 interval.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, LogNorm, Normalize
from netCDF4 import Dataset, date2num
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://thredds.northwestknowledge.net/thredds/dodsC/MET"
VARIABLES = {
    "tmmx": ("air_temperature", "Daily maximum air temperature", "°C"),
    "pr": ("precipitation_amount", "Daily precipitation", "mm"),
    "vs": ("wind_speed", "Wind speed at 10 m", "m/s"),
    "th": ("wind_from_direction", "Wind from-direction", "degrees clockwise from north"),
}
EXTENT = (-125, -66, 24, 50)


def dates_between(start: date, end: date, count: int) -> list[date]:
    span = (end - start).days
    if span < count - 1:
        raise ValueError("Period is too short for distinct samples")
    return [start + timedelta(days=round(i * span / (count - 1))) for i in range(count)]


def read_remote(variable: str, when: date, stride: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    url = f"{BASE}/{variable}/{variable}_{when.year}.nc"
    with Dataset(url) as nc:
        days = nc.variables["day"]
        index = int(round(date2num(datetime.combine(when, datetime.min.time()), days.units, days.calendar if hasattr(days, "calendar") else "standard")))
        day_values = np.asarray(days[:], dtype=float)
        matches = np.flatnonzero(np.isclose(day_values, index))
        if len(matches) != 1:
            raise ValueError(f"{when} missing in {url}")
        lat = np.asarray(nc.variables["lat"][::stride], dtype=float)
        lon = np.asarray(nc.variables["lon"][::stride], dtype=float)
        raw = nc.variables[VARIABLES[variable][0]]
        values = np.ma.filled(raw[int(matches[0]), ::stride, ::stride], np.nan).astype("float32")
        metadata = {"url": url, "variable": VARIABLES[variable][0], "units": getattr(raw, "units", ""), "long_name": getattr(raw, "long_name", ""), "sample_index": int(matches[0]), "scale_factor": str(getattr(raw, "scale_factor", "none")), "add_offset": str(getattr(raw, "add_offset", "none"))}
    if variable == "tmmx":
        values -= 273.15
    return lat, lon, values, metadata


def get_fields(start: date, end: date, count: int, stride: int, refresh: bool):
    dates = dates_between(start, end, count)
    path = ROOT / "data" / "scivis" / f"gridmet_{start}_{end}_n{count}_s{stride}.npz"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not refresh:
        with np.load(path) as data:
            return dates, data["lat"], data["lon"], {v: data[v] for v in VARIABLES}, path
    fields = {v: [] for v in VARIABLES}
    sources = []
    lat0 = lon0 = None
    for when in dates:
        print(f"Fetching {when} from gridMET", flush=True)
        for variable in VARIABLES:
            lat, lon, field, metadata = read_remote(variable, when, stride)
            if lat0 is None:
                lat0, lon0 = lat, lon
            elif not (np.array_equal(lat0, lat) and np.array_equal(lon0, lon)):
                raise ValueError("Coordinate mismatch among gridMET variables")
            fields[variable].append(field)
            sources.append({"date": when.isoformat(), "retrieved_utc": datetime.now(timezone.utc).isoformat(), **metadata})
    arrays = {v: np.stack(fields[v]) for v in VARIABLES}
    np.savez_compressed(path, lat=lat0, lon=lon0, **arrays)
    path.with_suffix(".sources.json").write_text(json.dumps(sources, indent=2), encoding="utf-8")
    return dates, lat0, lon0, arrays, path


def map_axis(ax, title: str, extent=EXTENT):
    ax.set_title(title, fontsize=10)
    ax.set_xlim(extent[:2])
    ax.set_ylim(extent[2:])
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.grid(color="#888", alpha=.25, linewidth=.4)
    ax.set_aspect(1.3)
    ax.set_facecolor("#d9dde3")


def save_figure(fig, out, name):
    fig.savefig(out / f"{name}.png", dpi=240)
    fig.savefig(out / f"{name}.svg")


def color_experiments(dates, lat, lon, fields, out):
    i = len(dates) // 2
    t = fields["tmmx"][i]
    p = fields["pr"][i]
    valid_p = p[np.isfinite(p)]
    pmax = max(5, float(np.nanpercentile(valid_p, 99)))
    fig, axs = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    fig.suptitle(f"Color mapping: identical fields, different encodings | {dates[i]}", fontsize=15)
    panels = [
        (t, "viridis", Normalize(-10, 45), "Temperature: continuous viridis", "°C"),
        (t, "cividis", BoundaryNorm(np.arange(-10, 50, 5), 256, clip=True), "Temperature: 5°C discrete cividis", "°C"),
        (p, "Blues", Normalize(0, pmax), "Rain: linear (above p99 saturated)", "mm/day"),
        (np.ma.masked_where(p <= 0, p), "magma", LogNorm(.1, pmax), "Rain: log (dry cells shown in white)", "mm/day"),
    ]
    for ax, (arr, cmap, norm, title, unit) in zip(axs.flat, panels):
        ax.set_facecolor("#d9dde3")
        if isinstance(norm, LogNorm):
            dry = np.ma.masked_where(~np.isfinite(p) | (p > 0), np.zeros_like(p))
            ax.pcolormesh(lon, lat, dry, cmap=matplotlib.colors.ListedColormap(["#ffffff"]), shading="auto")
            cmap = plt.get_cmap(cmap).copy()
            cmap.set_under("#fff2cc")
        im = ax.pcolormesh(lon, lat, arr, cmap=cmap, norm=norm, shading="auto", rasterized=True)
        map_axis(ax, title)
        fig.colorbar(im, ax=ax, shrink=.7, label=unit, extend="both" if isinstance(norm, LogNorm) else "max")
    fig.supxlabel("Gray = missing | Log rain: white = dry; pale yellow = 0 < rain < 0.1 mm | Above scale maximum = saturated", fontsize=9)
    save_figure(fig, out, "scivis_color_experiments")
    plt.close(fig)


def global_local(dates, lat, lon, t, out):
    valid = t[np.isfinite(t)]
    global_limits = (float(np.min(valid)), float(np.max(valid)))
    ranges = [(float(np.nanmin(x)), float(np.nanmax(x))) for x in t]
    spread = [hi - lo for lo, hi in ranges]
    indices = [int(np.argmin(spread)), int(np.argmax(spread))]
    if indices[0] == indices[1]:
        indices = [0, len(dates)-1]
    fig, axs = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    fig.suptitle("Same color, different meaning? Global versus daily min/max", fontsize=15)
    for row, i in enumerate(indices):
        for col, norm in enumerate([Normalize(*global_limits), Normalize(*ranges[i])]):
            ax = axs[row, col]
            im = ax.pcolormesh(lon, lat, t[i], cmap="viridis", norm=norm, shading="auto", rasterized=True)
            map_axis(ax, f"{dates[i]} · {'shared' if col == 0 else 'day-specific'} limits")
            fig.colorbar(im, ax=ax, shrink=.74, label="Maximum temperature (°C)")
    save_figure(fig, out, "scivis_global_local")
    plt.close(fig)
    return global_limits, ranges


def contour_experiments(dates, lat, lon, t, out):
    i = len(dates) // 2
    values = t[i]
    lo, hi = np.nanmin(t), np.nanmax(t)
    fine = np.arange(np.floor(lo / 5) * 5, np.ceil(hi / 5) * 5 + 5, 5)
    coarse = np.arange(np.floor(lo / 10) * 10, np.ceil(hi / 10) * 10 + 10, 10)
    fig, axs = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    fig.suptitle(f"Contour mapping: boundary detail versus readability | {dates[i]}", fontsize=15)
    for ax, levels, filled, title in [
        (axs[0, 0], fine, False, "Line contours · 5°C interval"),
        (axs[0, 1], coarse, False, "Line contours · 10°C interval"),
        (axs[1, 0], fine, True, "Filled contours · 5°C interval"),
        (axs[1, 1], coarse, True, "Filled contours · 10°C interval"),
    ]:
        if filled:
            plot = ax.contourf(lon, lat, values, levels=levels, cmap="viridis", vmin=fine[0], vmax=fine[-1], extend="both", algorithm="serial")
            fig.colorbar(plot, ax=ax, shrink=.74, label="Maximum temperature (°C)")
        else:
            ax.pcolormesh(lon, lat, values, cmap="Greys", alpha=.32, shading="auto", rasterized=True)
            plot = ax.contour(lon, lat, values, levels=levels, colors="#17283a", linewidths=.65, algorithm="serial")
            ax.clabel(plot, inline=True, fontsize=7, fmt="%g°C")
        map_axis(ax, title)
    save_figure(fig, out, "scivis_contour_experiments")
    plt.close(fig)
    return fine


def quiver_experiments(dates, lat, lon, speed, direction, out):
    i = len(dates) // 2
    theta = np.deg2rad(direction[i])
    u = -speed[i] * np.sin(theta)
    v = -speed[i] * np.cos(theta)
    # The selected western-US box keeps the density experiment legible.
    ys = (lat >= 30) & (lat <= 49)
    xs = (lon >= -125) & (lon <= -100)
    X, Y = np.meshgrid(lon[xs], lat[ys])
    U, V, S = u[np.ix_(ys, xs)], v[np.ix_(ys, xs)], speed[i][np.ix_(ys, xs)]
    fig, axs = plt.subplots(2, 3, figsize=(16, 10), constrained_layout=True)
    fig.suptitle(f"Wind: sampling density and vector length | {dates[i]} | Western US", fontsize=15)
    for col, step in enumerate([4, 8, 12]):
        for row in range(2):
            ax = axs[row, col]
            footprint = np.ma.masked_where(~np.isfinite(S), np.zeros_like(S))
            ax.pcolormesh(lon[xs], lat[ys], footprint, cmap=matplotlib.colors.ListedColormap(["#f8fafc"]), shading="auto")
            sl = (slice(None, None, step), slice(None, None, step))
            xx, yy, uu, vv, ss = X[sl], Y[sl], U[sl], V[sl], S[sl]
            good = np.isfinite(ss) & (ss > .1) & np.isfinite(uu) & np.isfinite(vv)
            if row == 1:
                uu, vv = np.divide(uu, ss, out=np.zeros_like(uu), where=good), np.divide(vv, ss, out=np.zeros_like(vv), where=good)
            uu, vv = np.where(good, uu, np.nan), np.where(good, vv, np.nan)
            # Eastward velocity spans more longitude degrees at higher latitudes.
            # Explicit displayed bearings preserve physical vector length and map direction.
            angles = np.rad2deg(np.arctan2(vv * 1.3, uu / np.cos(np.deg2rad(yy))))
            q = ax.quiver(xx, yy, uu, vv, ss, cmap="viridis", clim=(0, 15), scale=65 if row == 0 else 12, scale_units="inches", angles=angles, pivot="mid", width=.0034)
            map_axis(ax, f"{'Speed-proportional' if row == 0 else 'Equal-length'} · every {step}th cell", (-125, -100, 30, 49))
            if row == 0 and col == 0:
                key = ax.quiverkey(q, .72, .94, 5, "5 m/s", labelpos="E", coordinates="axes")
                key.text.set_bbox({"facecolor": "white", "edgecolor": "none", "alpha": .85, "pad": 2})
    fig.colorbar(q, ax=axs, shrink=.75, label="Wind speed (m/s)", extend="max")
    fig.supxlabel("Arrows show flow TO | Native grid read every 6th cell, then arrow thinning above | Gray = missing; calm winds omitted", fontsize=9)
    save_figure(fig, out, "scivis_quiver_experiments")
    plt.close(fig)


def gif_frames(dates, lat, lon, t, limits, ranges, levels, out):
    for mode in ["global", "local", "contour"]:
        frames = []
        for i, when in enumerate(dates):
            fig, ax = plt.subplots(figsize=(9, 5.3), layout="constrained")
            if mode == "contour":
                im = ax.contourf(lon, lat, t[i], levels=levels, cmap="viridis", extend="both")
                ax.contour(lon, lat, t[i], levels=levels[::2], colors="#17283a", linewidths=.3)
            else:
                im = ax.pcolormesh(lon, lat, t[i], cmap="viridis", norm=Normalize(*(limits if mode == "global" else ranges[i])), shading="auto", rasterized=True)
            map_axis(ax, f"gridMET maximum temperature · {when} · {mode} limits")
            fig.colorbar(im, ax=ax, shrink=.83, label="°C")
            fig.canvas.draw()
            frames.append(Image.frombytes("RGB", fig.canvas.get_width_height(), fig.canvas.tostring_rgb()) if hasattr(fig.canvas, "tostring_rgb") else Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy().astype("uint8")).convert("RGB"))
            plt.close(fig)
        frames[0].save(out / f"scivis_{mode}.gif", save_all=True, append_images=frames[1:], duration=800, loop=0, optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", default="2023-07-01", help="First day of assigned period")
    ap.add_argument("--end", default="2023-09-30", help="Last day of assigned period")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--stride", type=int, default=6, help="Spatial read stride from 1/24 degree native grid")
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    if not 5 <= args.samples <= 10:
        ap.error("Assignment requires 5–10 time samples")
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    if end < start:
        ap.error("End must be after start")
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    dates, lat, lon, fields, cache = get_fields(start, end, args.samples, args.stride, args.refresh)
    out = ROOT / "images" / "scivis"
    out.mkdir(parents=True, exist_ok=True)
    color_experiments(dates, lat, lon, fields, out)
    limits, ranges = global_local(dates, lat, lon, fields["tmmx"], out)
    levels = contour_experiments(dates, lat, lon, fields["tmmx"], out)
    quiver_experiments(dates, lat, lon, fields["vs"], fields["th"], out)
    gif_frames(dates, lat, lon, fields["tmmx"], limits, ranges, levels, out)
    with (ROOT / "data" / "scivis" / "sample_statistics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "tmmx_min_C", "tmmx_max_C", "tmmx_p02_C", "tmmx_p98_C", "pr_positive_fraction", "pr_p99_mm", "vs_mean_m_s"])
        writer.writeheader()
        for i, when in enumerate(dates):
            t, p, s = (fields[k][i] for k in ["tmmx", "pr", "vs"])
            writer.writerow({"date": when, "tmmx_min_C": float(np.nanmin(t)), "tmmx_max_C": float(np.nanmax(t)), "tmmx_p02_C": float(np.nanpercentile(t, 2)), "tmmx_p98_C": float(np.nanpercentile(t, 98)), "pr_positive_fraction": float(np.mean(p[np.isfinite(p)] > 0)), "pr_p99_mm": float(np.nanpercentile(p, 99)), "vs_mean_m_s": float(np.nanmean(s))})
    manifest = {"status": "Team-supplied interval", "start": str(start), "end": str(end), "sample_dates": [str(x) for x in dates], "native_resolution_degrees": 1/24, "spatial_stride": args.stride, "data_cache": str(cache.relative_to(ROOT)), "temperature_global_limits_C": limits, "temperature_daily_limits_C": ranges, "longitude_extent": EXTENT[:2], "latitude_extent": EXTENT[2:], "wind_direction_convention": "from, clockwise from north", "wind_vector_formula": "u=-speed*sin(theta); v=-speed*cos(theta)"}
    manifest.update({"cache_sha256": hashlib.sha256(cache.read_bytes()).hexdigest(), "cache_file_modified_utc": datetime.fromtimestamp(cache.stat().st_mtime, timezone.utc).isoformat(), "figure_built_utc": datetime.now(timezone.utc).isoformat(), "contour_algorithm": "ContourPy serial", "contour_corner_mask": True, "display_subsample_degrees": args.stride / 24, "global_scale_scope": "all valid cells in eight sampled fields, not all days in interval"})
    (ROOT / "data" / "scivis" / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote SciVis figures and GIFs to {out}")


if __name__ == "__main__":
    main()
