"""parikshith — network graph (infovis i) and parallel coordinates (infovis ii-a)."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
scripts_dir = root / "scripts"


# helper to run child scripts
def _run(name: str) -> None:
    p = scripts_dir / name
    if not p.exists():
        print(f"[skip] {name} not found"); return
    print(f"  -> {name}", flush=True)
    subprocess.run([sys.executable, str(p)], cwd=root, check=True)


# build similarity graph, three layouts (fig 1), and browser data
def build_network() -> None:
    _run("build_infovis_data.py")
    print("network data and figure 1 complete")


# build pcp and paired change figures
def build_pcp() -> None:
    for script in [
        "build_change_pcp.py",
        "build_gentle_pcp.py",
        "build_quantile_change.py",
        "build_internet_revision.py",
        "build_simple_figures.py",
        "build_approved_assets.py",
    ]:
        _run(script)
    print("pcp figures complete")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--network", action="store_true")
    ap.add_argument("--pcp", action="store_true")
    args = ap.parse_args()
    run_all = not (args.network or args.pcp)
    if args.network or run_all: build_network()
    if args.pcp or run_all: build_pcp()


if __name__ == "__main__":
    main()
