# DAS732 Assignment 2 - Team Plot Twist

Open **DAS732_A2_Report.pdf** for the full report with 31 figure sets and complete explanations. The high-resolution assessment images are in `images/report/`, named Fig1-Fig31. The three required eight-frame scalar animations are in `images/scivis/`.

This folder is a self-contained local submission copy. It contains no Git remote and requires no external network access. All raw inputs, processed tables, gridMET caches, scripts and web assets required for this submission are included.

## Open the working visualizations

From this folder, run:

```powershell
python run_visualizations.py
```

Windows users can double-click `START_VISUALIZATIONS.cmd`. Open `http://127.0.0.1:8765/web/home.html` in your browser. These apps use only Python's standard-library HTTP server, supplied JSON, JavaScript and vendored D3; no pip packages, network connection or CDN are needed for viewing them. Stop the server with Ctrl+C.

| View | Local page | Interaction to assess |
|---|---|---|
| Network | `web/network.html` | Spring/Spectral/Circular layouts, country search, threshold filter, region/isolate filters, pan/zoom |
| Bundled profiles | `web/index.html` | Parallel coordinates bundling, vertical brushing, axis-title reorder, year/region, country details |
| Paired changes | `output/pcp_changes/index.html` | Brush, reorder axes, bundling and exact changes |
| Treemap | `web/treemap.html` | Zoom/back, two hierarchies, squarified/slice-and-dice partition |
| All figures | `figures.html` | 31 full-resolution figures with detailed interpretations |
| Full UI evidence | `interactions.html` | Complete browser screenshots with controls |

## Folder contents

- `DAS732_A2_Report.pdf`: main IEEE report (30 pages).
- `images/report/`: all 31 canonical numbered PNGs (Fig1.png - Fig31.png).
- `images/scivis/`: three eight-frame GIFs and the scalar/contour/vector exports used by the report.
- `web/`: runnable JavaScript UIs (D3 network, parallel coordinates, treemap) and vendored D3 library.
- `scripts/`: Python generation scripts, shared utilities, and verification code.
- `data/raw/`: original OWID/ITU country extracts and region lookup.
- `data/processed/`: cleaned data tables, network JSON, and preprocessing audit.
- `data/scivis/`: weather caches (gridMET summer-autumn 2023) and acquisition metadata.
- `report_latex/`: complete editable report LaTeX source (`DAS732_A2_Report.tex`), preamble, and figure assets.

## Reproduction and verification

To run all verification checks on the submission:

```powershell
python scripts/verify_all.py
```

To run individual member scripts:

```powershell
python scripts/parikshith_network_pcp.py
python scripts/sindhoor_horizon_contours.py
python scripts/varshith_treemap_quiver.py
```

To regenerate all figures:

```powershell
python scripts/run_all_figures.py
```

To recompile the LaTeX report, run from `report_latex/`:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error DAS732_A2_Report.tex
pdflatex -interaction=nonstopmode -halt-on-error DAS732_A2_Report.tex
```

## Member responsibilities

Task responsibilities and figure allocations:

- **Parikshith Aithal K V (BT2024249)**: Network and interactive parallel coordinates; scalar color mapping and global/local scales; rainfall concentration comparison. (11 figures: 1–5, 7, 13, 19–20, 22–23)
- **Sindhoor Ganapathi Hegde (BT2024014)**: Horizon/ridgeline variations; custom contour tracing, filled bands and contour GIF; weather persistence and event timing. (10 figures: 6, 14–18, 21, 25–26, 31)
- **Varshith M Gowda (BT2024227)**: Association and catch-up comparison experiments across measures, regions and cohorts; quiver sampling and length encoding with wind and multivariable context. (10 figures: 8–12, 24, 27–30)

Total figures: 31 (each member owns one InfoVis and one SciVis focus area, fully documented in the report).
