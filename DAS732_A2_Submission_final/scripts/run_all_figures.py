"""master runner to reproduce and verify submission outputs."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
scripts_dir = root / "scripts"

# pipeline stages by contributor
stages = {
    "data":       ["shared_data_prep.py"],
    "parikshith": ["parikshith_network_pcp.py"],
    "sindhoor":   ["sindhoor_horizon_contours.py"],
    "varshith":   ["varshith_treemap_quiver.py"],
    "verify":     ["verify_all.py"],
}


# run individual script stage
def run_script(name: str, extra: list[str] | None = None) -> None:
    p = scripts_dir / name
    if not p.exists():
        print(f"[skip] {name} - not found")
        return
    cmd = [sys.executable, "-X", "utf8", str(p)] + (extra or [])
    print(f"\n>> {name}", flush=True)
    subprocess.run(cmd, cwd=root, check=True)
    print(f"ok {name}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--stage",
        choices=["all", *stages.keys()],
        default="all",
        help="pipeline stage to execute",
    )
    ap.add_argument(
        "--download-weather",
        action="store_true",
        help="download missing weather caches if needed",
    )
    args = ap.parse_args()

    stages_to_run = list(stages.keys()) if args.stage == "all" else [args.stage]

    for stage in stages_to_run:
        for script in stages[stage]:
            extra: list[str] = []
            if script == "shared_data_prep.py" and args.download_weather:
                extra = ["--all"]
            run_script(script, extra if extra else None)

    print("\nall requested stages completed.")


if __name__ == "__main__":
    main()
