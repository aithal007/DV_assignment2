"""Capture reproducible screenshots of the interactive Infovis pages with Chrome."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import subprocess
import threading

ROOT = Path(__file__).resolve().parents[1]
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PAGES = {
    "parallel_coordinates_2020.png": "web/index.html?year=2020&bundle=50&matched=1&fixed=1",
    "parallel_coordinates_straight_2020.png": "web/index.html?year=2020&bundle=0&matched=1&fixed=1",
    "parallel_coordinates_2015.png": "web/index.html?year=2015&bundle=50&matched=1&fixed=1",
    "network_interactive.png": "web/network.html",
    "treemap_region.png": "web/treemap.html?zoom=Asia",
    "treemap_adoption.png": "web/treemap.html?hierarchy=adoption&zoom=75%E2%80%93100%25/Asia",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=list(PAGES), help="Capture one named screenshot")
    args = parser.parse_args()
    if not CHROME.exists():
        raise FileNotFoundError(f"Chrome missing: {CHROME}")
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for filename, path in PAGES.items():
            if args.only and filename != args.only:
                continue
            output = ROOT / "images" / filename
            command = [str(CHROME), "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars", "--window-size=1600,1200", "--virtual-time-budget=5000", f"--screenshot={output}", f"http://127.0.0.1:{server.server_port}/{path}"]
            result = subprocess.run(command, capture_output=True, text=True, timeout=40)
            if result.returncode or not output.exists():
                raise RuntimeError(f"Chrome failed for {path}: {result.stderr[-1000:]}")
            print(f"Saved {output.relative_to(ROOT)}")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
