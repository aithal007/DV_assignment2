"""Audit annual time coordinates and cache all 92 daily fields, at stride 6."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from netCDF4 import Dataset, num2date
from build_scivis import BASE, VARIABLES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/scivis"
CACHE = DATA / "gridmet_2023-07-01_2023-09-30_daily_s6.npz"


def main():
    if CACHE.exists() and (DATA / "daily_manifest.json").exists():
        print("Reusing verified 92-day cache", flush=True)
        return
    arrays, sources = {}, []
    lat0 = lon0 = dates0 = None
    for key, (name, _, _) in VARIABLES.items():
        url = f"{BASE}/{key}/{key}_2023.nc"
        print(f"Auditing daily coordinates: {key}", flush=True)
        with Dataset(url) as nc:
            day = nc.variables["day"]
            time = np.asarray(day[:])
            annual_dates = [d.strftime("%Y-%m-%d") for d in num2date(time, day.units, getattr(day, "calendar", "standard"))]
            selected = [i for i, d in enumerate(annual_dates) if "2023-07-01" <= d <= "2023-09-30"]
            dates = [annual_dates[i] for i in selected]
            assert len(annual_dates) == 365 and len(dates) == 92 and len(set(dates)) == 92
            assert np.all(np.diff(time[selected]) == 1)
            lat, lon = np.asarray(nc.variables["lat"][::6]), np.asarray(nc.variables["lon"][::6])
            if lat0 is None:
                lat0, lon0, dates0 = lat, lon, dates
            else:
                assert dates == dates0 and np.array_equal(lat, lat0) and np.array_equal(lon, lon0)
            raw = nc.variables[name]
            print(f"{key}: 365 annual dates; July 31 + August 31 + September 30 = 92 daily dates; native shape {raw.shape}", flush=True)
            pieces = []
            for month in ("07", "08", "09"):
                indices = [i for i in selected if annual_dates[i][5:7] == month]
                path = DATA / f"daily_{key}_2023_{month}_s6.npy"
                if path.exists():
                    arr = np.load(path)
                else:
                    print(f"Downloading {key}: month {month} ({len(indices)} days)", flush=True)
                    arr = np.ma.filled(raw[indices[0]:indices[-1]+1, ::6, ::6], np.nan).astype("float32")
                    if key == "tmmx":
                        arr -= 273.15
                    np.save(path, arr)
                assert arr.shape == (len(indices), len(lat), len(lon))
                pieces.append(arr)
            arrays[key] = np.concatenate(pieces)
            counts = [int(np.isfinite(a).sum()) for a in arrays[key]]
            assert all(c > 0 for c in counts)
            sources.append({"key": key, "url": url, "variable": name, "units": getattr(raw, "units", ""), "packing_scale": str(getattr(raw, "scale_factor", "none")), "packing_offset": str(getattr(raw, "add_offset", "none")), "annual_date_count": len(annual_dates), "native_shape": list(raw.shape), "first_selected_index": selected[0], "last_selected_index": selected[-1], "selected_date_count": 92, "missing_calendar_dates": [], "valid_cell_counts_by_day": counts, "checked_utc": datetime.now(timezone.utc).isoformat()})
    np.savez_compressed(CACHE, lat=lat0, lon=lon0, dates=np.array(dates0), **arrays)
    manifest = {"start": dates0[0], "end": dates0[-1], "date_count": 92, "month_counts": {"July": 31, "August": 31, "September": 30}, "dates": dates0, "spatial_stride": 6, "cache": str(CACHE.relative_to(ROOT)).replace("\\", "/"), "sha256": hashlib.sha256(CACHE.read_bytes()).hexdigest(), "sources": sources, "scope": "All daily temporal fields; spatially subsampled every sixth native cell. Eight-frame animations retain their original sample dates."}
    (DATA / "daily_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Verified and saved all 92 daily fields for four variables: {CACHE}", flush=True)


if __name__ == "__main__":
    main()
