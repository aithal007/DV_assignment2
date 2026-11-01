# DAS732 Assignment 2 - Team Plot Twist

## Shared Storage Mirrors
- **Google Drive Mirror**: [Google Drive Folder](https://drive.google.com/drive/folders/1z1a7Zm4Zed1E_HTJYJ9jM60JMG6ReEO6?usp=drive_link)
- **Microsoft OneDrive / SharePoint Mirror**: [OneDrive / SharePoint Folder](https://iiitbac-my.sharepoint.com/:f:/g/personal/parikshith_aithal_iiitb_ac_in/IgCNp7Qd4mEWRJ3aRFu4KIv7ASgagGLXmGN8K92jPUOksxw?e=Nd7Xc1)
- **Live GitHub Pages Dashboard**: [https://aithal007.github.io/DV_assignment2/](https://aithal007.github.io/DV_assignment2/)


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
| Paired changes | `web/pcp_changes.html` | Brush, reorder axes, bundling and exact changes |
| Treemap | `web/treemap.html` | Zoom/back, two hierarchies, squarified/slice-and-dice partition |
| All figures | `figures.html` | 31 full-resolution figures with detailed interpretations |
| Full UI evidence | `interactions.html` | Complete browser screenshots with controls |

## Folder contents

- `DAS732_A2_Report.pdf`: main IEEE report (31 pages).
- `images/report/`: all 31 canonical numbered PNGs (Fig1.png - Fig31.png).
- `images/scivis/`: three eight-frame GIFs and the scalar/contour/vector exports used by the report.
- `web/`: runnable JavaScript UIs (D3 network, parallel coordinates, treemap) and vendored D3 library.
- `scripts/`: Python generation scripts, shared utilities, and verification code.
- `data/raw/`: original OWID/ITU country extracts and region lookup.
- `data/processed/`: cleaned data tables, network JSON, and preprocessing audit.
- `data/scivis/`: weather caches (gridMET summer-autumn 2023) and acquisition metadata.
- `report_latex/`: complete editable report LaTeX source (`DAS732_A2_Report.tex`), preamble, and figure assets.

## Reproduction and verification

To run all automated verification checks on the submission:

```powershell
python scripts/verify_all.py
```

To run individual member scripts:

```powershell
python scripts/parikshith_network_pcp.py
python scripts/sindhoor_horizon_contours.py
python scripts/varshith_treemap_quiver.py
```

To execute the complete end-to-end regeneration pipeline across all tasks:

```powershell
python scripts/run_all_figures.py
```

All required intermediate modules (including `network_threshold_revision.py` and weather data caches) are fully bundled. The pipeline executes `shared_data_prep.py`, individual member generation scripts, and concludes with `verify_all.py` confirming 100% verification across all network thresholds, 31 figure artifacts, weather data, and report structure.

To recompile the LaTeX report, run from `report_latex/`:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error DAS732_A2_Report.tex
pdflatex -interaction=nonstopmode -halt-on-error DAS732_A2_Report.tex
```

## Member responsibilities

Task responsibilities and figure allocations:

| Member | Figs | InfoVis task | SciVis task |
|---|---|---|---|
| Parikshith Aithal K V (BT2024249) | 1–7, 18–19, 22–23 (11 figs) | Network node-link + parallel coordinates plot | Scalar color mapping (global vs local extrema) |
| Sindhoor Ganapathi Hegde (BT2024014) | 14–17, 20–21, 24–25, 30–31 (10 figs) | Horizon plots + ridgeline plots | Marching Squares contour mapping |
| Varshith M Gowda (BT2024227) | 8–13, 26–29 (10 figs) | Treemap visualisations + cohort comparisons | Quiver plot (grid sampling + magnitude encoding) |

Total figures: 31. No two members share a task; joint ownership applies only to shared data cleaning/pre-processing (see report Section I).
