# DAS732 Assignment 2 - Team Plot Twist

## Shared Storage Mirrors
- **Google Drive Mirror**: [Google Drive Folder](https://drive.google.com/drive/folders/1z1a7Zm4Zed1E_HTJYJ9jM60JMG6ReEO6?usp=drive_link)
- **Microsoft OneDrive / SharePoint Mirror**: [OneDrive / SharePoint Folder](https://iiitbac-my.sharepoint.com/my?id=%2Fpersonal%2Fparikshith%5Faithal%5Fiiitb%5Fac%5Fin%2FDocuments%2FPlot%5FTwist%5F2&viewid=fc99016c%2D7fb9%2D4f80%2D95c3%2D7dfc9f6dca23)
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

To regenerate individual member figures (writes to `output/member_figures/`):

```powershell
python scripts/parikshith_network_pcp.py
python scripts/sindhoor_horizon_contours.py
python scripts/varshith_treemap_quiver.py
```

> **Reproducibility note (M6/M7):** `scripts/run_all_figures.py` orchestrates the above
> member scripts. Several final-asset generators require intermediate modules
> (`network_threshold_revision`, weather overlap CSVs) that were used during development
> but are not included in this submission package. Consequently, the runner may abort
> on missing imports for the network/community figures (Figs 1, 3) and some weather
> figures (Fig 27). The canonical `images/report/Fig*.png` files are the assessed
> submission artifacts; their SHA-256 hashes and sizes are recorded in
> `submission_manifest.json`. Figures that cannot be regenerated from included source
> are explicitly listed below:
>
> | Figure(s) | Regenerable from included source? |
> |-----------|----------------------------------|
> | Figs 2, 4–8, 9–13, 14–17, 18 (panels A–D), 19–26, 28–31 | Yes, via member scripts |
> | Figs 1, 3 (network layout/community): final five-panel + NodeTrix | Partial — base network recomputed; final layout/community compositor absent |
> | Fig 18 panels E–F (departure + Turbo comparison) | Not regenerable — generator excluded from package |
> | Fig 27 (wind rose, 5-speed-class version) | Not regenerable — five-bin generator absent; four-bin builder present |
>
> The supplied PNG assets are intact and hash-verified. Run `python scripts/verify_all.py`
> to confirm figure presence and network integrity.

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
