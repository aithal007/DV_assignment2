# DAS732 Assignment 2 - Team Plot Twist

Open **DAS732_A2_Report.pdf** for the full report with 32 figure sets and complete explanations. The high-resolution assessment images are in `images/report/`, named Fig1-Fig32. The three required eight-frame scalar animations are in `images/scivis/`.

This folder is a local submission copy. It contains no Git remote and requires no GitHub access. Online links in the report are convenience links to an earlier published dashboard; use the supplied local apps to assess this copy.

## Open the working visualizations

From this folder, run:

```powershell
python run_visualizations.py
```

Windows users can double-click `START_VISUALIZATIONS.cmd`. Open `http://127.0.0.1:8765/web/home.html` if necessary, and keep the server running. Stop it with Ctrl+C. Use `--port 8766` if the default port is occupied. These apps use only the Python standard-library HTTP server, supplied JSON, JavaScript and vendored D3; no pip packages, network connection or CDN are needed for viewing them. Avoid opening the HTML files directly because browser file restrictions can block JSON fetching.

| View | Local page | Interaction to assess |
|---|---|---|
| Network | `web/network.html` | Spring/Spectral/Circular, country search, threshold, region/isolate filters, pan/zoom |
| Bundled profiles | `web/index.html` | Bundling, real vertical brushing, axis-title reorder, year/region, country details |
| Paired changes | `output/pcp_changes/index.html` | Brush, reorder axes, bundling and exact changes |
| Treemap | `web/treemap.html` | Zoom/back, two hierarchies, squarified/slice-and-dice partition |
| All figures | `figures.html` | 32 full-resolution figures with detailed interpretations |
| Full UI evidence | `interactions.html` | Uncropped complete browser screenshots with controls |

## Folder contents

- `DAS732_A2_Report.pdf`: main report. The canonical build copy is also at `output/pdf/DAS732_A2_Report_IEEE.pdf`.
- `images/report/`: all 32 numbered PNGs and available matching SVGs.
- `images/scivis/`: three eight-frame GIFs and the scalar/contour/vector exports used by the report.
- `web/`, `output/pcp_changes/`: runnable JavaScript UIs and local D3.
- `scripts/`: preprocessing, numerical analysis, plot builders, report builders and verification source.
- `data/raw/`: original A1 country extracts and the code-based region lookup.
- `data/processed/`: cleaned data and preprocessing audit; `data/scivis/`: weather caches and acquisition metadata.
- `report_latex/`: editable report source, preamble and 32 figure PNGs. No old report drafts are included.
- `REQUIREMENTS_CHECKLIST.md`, `evidence/`: every assignment clause, environment details, browser-test results and validation records.
- `output/`: selected source exports and numerical tables used to derive the report findings.

The core submission excludes Git files, caches such as `__pycache__`, old report drafts, unused plot experiments, old comparison galleries, and slide/video recording materials. The supplied assignment PDF explicitly says a video demo is not required. All raw inputs and relevant numerical caches required for this submission are included.

## Install dependencies for regeneration

Python 3.11+ and the packages listed in `requirements.txt` are needed for numerical regeneration. Node.js is used by the JavaScript syntax checks. PDF regeneration additionally requires MiKTeX or TeX Live with `pdflatex` on PATH and the packages listed in `report_latex/design_reference_preamble.tex`, including IEEEtran. Checked environment versions are recorded in `evidence/environment_versions.json`.

```powershell
python -m pip install -r requirements.txt
python --version
node --version
pdflatex --version
```

An optional virtual environment can be created with `python -m venv .venv`. Use that environment's Python consistently. Missing software/packages need installation; the supplied country extracts and gridMET caches support the numerical route without downloading source data again. Plot layout may vary slightly across dependency versions; the checked exports are supplied.

## Preprocessing: what is done before plotting

```powershell
python -X utf8 scripts/preprocess_data.py
```

Country preparation reads the three original OWID/ITU CSVs, renames fields and validates source keys, numeric values and one-to-one joins on entity/code/year. The outer join has **13,387** rows. An explicit aggregate-entity list removes **823** rows, retaining **12,564** country-year records. Missing values are preserved without imputation or replacement with zero. A code-based lookup supplies region metadata; unmatched regions remain Unclassified.

Task-specific complete cases are declared: 179 four-indicator network profiles in 2020; 175 countries matched in 2015 and 2020; 159 complete annual adoption histories over 2000-2020; and 184 treemap countries. Paired changes are computed within each country before summarizing. Country adoption percentages and subscription rates retain their different units.

Following the professor's advice, the complete network stores every one of the 15,931 unique pair scores. The four indicators are z-scored with population standard deviation (`ddof=0`), then Euclidean distance is mapped to similarity `1/(1+d)`. The team's P95 default is 0.5697629885414606: 797 retained edges and 12 isolates. P95 is a sparse display choice, not similarity 0.95, a confidence level or a professor-prescribed value. Perturbation and scaling comparisons test sensitivity. All scores and threshold tables are included.

Weather preparation uses July 1-September 30, 2023: summer into autumn supports heat-persistence, cooling and rainfall-timing comparisons; independently documented Southwest heat provides context for the year. This is a case study, not a representative climate year. Eight uniformly spaced dates, 13 days apart with both endpoints, provide reproducible coverage without random gaps; all 92 daily fields support monthly and event claims.

Source extraction decodes NetCDF packing/masks before converting `tmmx` from Kelvin to Celsius. Supplied NPZ caches already contain Celsius and are not converted twice. `pr` stays mm/day, `vs` is 10 m speed in m/s, and `th` is 10 m source direction clockwise from north. Actual NetCDF names are air_temperature, precipitation_amount, wind_speed and wind_from_direction. Every sixth native spatial point is read, approximately 0.25 degrees; this is subsampling, not averaging. A common **13,416-cell** all-variable/all-date mask and cosine-latitude weights are exported. Wind converts to flow-to components using `u=-vs*sin(th)` and `v=-vs*cos(th)` after converting the angle to radians. Cache hashes, missingness, cohort sizes, transformations, units and sampled/full-cache equality checks are recorded in `data/processed/preprocessing_audit.json`.

If weather caches are absent, source retrieval is optional and needs internet:

```powershell
python -X utf8 scripts/preprocess_data.py --download-weather
```

## Reproduce results from this folder

Run stages in order:

```powershell
python -X utf8 scripts/submission_workflow.py --stage data
python -X utf8 scripts/submission_workflow.py --stage figures
python -X utf8 scripts/submission_workflow.py --stage report
python -X utf8 scripts/submission_workflow.py --stage verify
```

Or run `python -X utf8 scripts/submission_workflow.py --stage all`. Add `--download-weather` to retrieve missing weather caches. The workflow stops on the first error. It does not access GitHub, publish a website, require old reports or rebuild video materials. It overwrites derived outputs; keep a copy of this folder before experiments.

The figure stage regenerates the numerical inputs and Python country/network, horizon/ridgeline, scalar/contour/quiver, daily-weather and supporting plots from supplied source tables/caches. The two browser-rendered treemap chart exports are supplied. To recapture those from the regenerated JSON, use the optional Playwright command below with `--recapture-report`, then run the report stage. The report stage rebuilds approved PCP/cohort displays, compiles the report twice, and refreshes the numbered images and local gallery. Outputs retain the same relative paths as the supplied artifacts.

For a report-only rebuild from supplied plots:

```powershell
python -X utf8 scripts/submission_workflow.py --stage report
python -X utf8 scripts/submission_workflow.py --stage verify
```

Direct LaTeX compilation is also possible: run `pdflatex -interaction=nonstopmode -halt-on-error DAS732_A2_Report.tex` twice from `report_latex/`. The Python report builder copies the resulting PDF to the canonical output location and the workflow refreshes the root report copy.

## Validation and GUI recapture

The verification stage checks every network score/default edge, all 454 near-adoption country pairs, daily event counts and runs, matched changes, regional variation, rainfall windows, plot numbering, contribution IDs, PDF bounds/links and GIF frame counts. Results are in `output/*validation.json` and `evidence/`. Text extraction alone does not establish legibility; the report was also rendered and visually reviewed.

To recapture full UI evidence with Playwright, optionally install it with `npm install playwright` and `npx playwright install chromium`, then run:

```powershell
node scripts/audit_infovis_interactions.mjs
python -X utf8 scripts/submission_workflow.py --stage refresh
```

Set `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` if using a custom Chromium executable. On this Windows machine the audit can use installed Edge. Actual pointer brushing, axis reordering, bundling invariance, three layouts, filtering, treemap zoom/back, hierarchies and partition choices are exercised. The receipt is `output/infovis_audit_20261026/interactions.json`; its internal timestamp identifies the latest test despite the historical folder name.

To regenerate the report's two browser treemap exports as well, run `node scripts/audit_infovis_interactions.mjs --recapture-report`, then rerun `python -X utf8 scripts/submission_workflow.py --stage report` and `--stage verify`. This needs the optional browser dependencies above; it is not needed to view or rebuild the report from the supplied exports.

`submission_manifest.json` records file sizes and SHA-256 hashes for the delivered folder. The final reproduction and browser receipts are in `evidence/`.

## Ownership and source references

The report records these assigned task responsibilities: Parikshith 12 figures (network, PCP and color mapping), Sindhoor 10 (horizon/ridgeline and contours), Varshith 10 (treemap and quiver). No figure is assigned twice. The team must ensure the responsibility table matches actual independent implementation. Dataset slice registration in the TAs form also requires team confirmation.

The report contains eleven cited references for datasets, methods and libraries, including gridMET, OWID, NetworkX, D3 and ContourPy. Gephi is cited as an assignment-permitted alternative, not as a tool used here. Vendored D3 retains its copyright notice. Interpretations remain descriptive: similarity edges are not physical cables, correlations are not causal effects, and three months of weather do not establish climate trends.

## Final PDF-review corrections

The first-page dashboard link opens the working interactive UIs; full screenshots remain available in the UI evidence gallery and `images/gui/`. The PDF keeps its 32 figure explanations without extra UI appendix pages. `scripts/marching_squares.py` implements all 16 cases independently, including saddle and missing-cell handling; `scripts/review_plots.py` generates the overlay and corrected figures. `output/review_revision/` supplies exact comparison metrics and tests. The report stage runs these builders automatically. `python scripts/verify_review_revision.py` checks the real-grid contours, reviewed weather numbers, dashboard link and removal of draft/video wording.

Figures 22 and 26 now show endpoint sign disagreement and longitude-centered departures/support directly. Typography, network degree/region encoding, matrix ordering, quiver visibility, wind-rose labels and treemap legends were revised. Per-image captions state a key result, numbered takeaway boxes give a reading action, and common caveats are centralized.
