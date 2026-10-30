# DAS732 Programming Assignment 2

**Main question:** What do averages and snapshots hide about inequality, relationships and change over time?

[Open the live interactive visualizations](https://aithal007.github.io/DV_assignment2/). The full assignment project and Pages site are maintained together in `aithal007/DV_assignment2`.

[Current report](output/pdf/DAS732_A2_Report_IEEE.pdf): 27 pages, 32 numbered figure sets (all original 30 plus two added plots). [Full-resolution gallery](output/quality_figures/index.html). Numbered assessment images are in `images/report/Fig1.png` through `Fig32.png`; complete browser screenshots are in `images/gui/`.

The report uses the existing IEEE design and simple-English reading guides, interpretation and takeaways. Figure 4 compares paired 2015–2020 changes, with a shared zero reference and a selected 20–30-point gain range. Figure 5 uses gentle curve bundles and stated adoption bands. Figure 7 contrasts level and gain correlations for the same 175 countries. Figure 10 follows three fixed groups of 53 countries from 2000 to 2020. Figure 6 retains the full scatterplot matrix. The report has no formal bibliography by team preference; source provenance and method links remain with the code. The team will provide its own truthful AI disclosures.

## Update the GitHub Pages site

The public site is published from `docs/` on the `main` branch of this repository. After rebuilding the report and figures, run `python scripts/refresh_pages_assets.py`, commit the updated files including `docs/`, and push `main`.

## Run the interactive visualizations

Run `python run_visualizations.py` from the submitted folder, or double-click `START_VISUALIZATIONS.cmd`. Open http://127.0.0.1:8765/web/home.html and keep the server running. The local apps require Python's standard library and supplied JavaScript/JSON assets; no CDN is needed.

- Network: `web/network.html`; NetworkX spring, spectral and circular layouts, country search, selected neighbors and edge filtering.
- Parallel coordinates: `web/index.html`; 175 matched countries, year and region filters, fixed axes, axis brushing, axis reordering, hover values and straight/gently bundled paths. Color and bundles use explicit adoption bands below 40%, 40–below 70%, and at least 70%. These are descriptive comparison bands, not discovered country types. Bundling changes only paths between axes; midpoint clamping prevents artificial peaks. `web/pcp-curves.js` contains the curve function.
- Changes PCP (Figure 4): `output/pcp_changes/index.html`; paired 2015–2020 changes for all 175 countries, a gain-range brush, reordered axes, exact hover values and straight/gently bundled paths. `paired_changes.csv` records all four differences; `validation.json` and `browser_validation.json` provide checks.
- Treemap: `web/treemap.html`; region-first versus adoption-band-first hierarchy, zoom, back and country values. The same 184 countries and total user count are preserved.

Full browser controls are explained in [web/README.md](web/README.md). Automated browser checks in `scripts/audit_infovis_interactions.mjs` exercise all three network layouts, search/filtering, PCP path changes without changing measured values, hover, pointer brushing, axis reordering, treemap zoom/back and both hierarchies. Results are in `output/infovis_audit_20261026/interactions.json`; screenshots are complete GUI captures, not cropped controls.

## Added evidence plots

Figure 31 compares all 454 country pairs within one percentage point of internet use; Figure 32 shows daily hot-dry ordering at selected grid cells. Both have detailed explanations and takeaways on the final report page. Source: `scripts/build_additional_evidence.py`; exact pairs, daily records, selection rules and facts: `output/additional_evidence/`. To regenerate, run `python -X utf8 scripts/build_additional_evidence.py` before rebuilding the report. Existing Figures 1-30 are retained.

## Rebuild the current selected report

From `ass2` (the submitted folder), with requirements installed and pdfLaTeX on PATH:

```powershell
python -X utf8 scripts/build_change_pcp.py
python -X utf8 scripts/build_gentle_pcp.py
python -X utf8 scripts/preview_rubric_replacements.py
python -X utf8 scripts/build_a1_style_report.py
python -X utf8 scripts/sync_report_delivery.py
python -X utf8 scripts/verify_story_report.py
python -X utf8 scripts/package_selected_report.py
```

These commands use supplied figures and cached data. `build_a1_style_report.py` is the active report builder; `approved_report_replacements.py` supplies the approved Figure 4/5/7/10 text. `build_story_report.py` delegates to the current builder. Compile `report_latex/DAS732_A2_Report.tex` twice to rebuild directly from LaTeX. The design preamble and all numbered PNGs are included in the source ZIP and combined package.

For complete data/figure regeneration, install `requirements.txt`, then run `python -X utf8 scripts/reproduce_results.py`. Stages are `data`, `figures`, and `report`; missing weather downloads can be requested with `--download-weather`. Supplied browser screenshots are artifacts; recapture with the browser audit when Playwright and Edge are installed. The audit's runtime location can be adjusted for another machine. It is optional for running the apps.

## Data processing and numerical evidence

Country extracts are retained in `data/raw/`; processing outputs and hashes are in `data/processed/`. Processing standardizes names and years, outer-merges indicators by country code and year, removes aggregate entities, checks duplicate keys, and retains missing values without imputation. Each analysis uses its explicitly stated complete cohort: 179 network nodes, 175 paired multivariable countries, 159 balanced annual countries or 184 treemap countries. Region lookup is supplied metadata. Treemap area uses user counts; color uses adoption percentage.

The approved supporting figures join years by country code before differencing. Figure 10 assigns its initial groups once; members stay fixed. `fig7_association_values.csv`, `fig10_country_cohorts.csv`, `fig10_cohort_summary.csv`, and `rubric_preview_validation.json` in `output/proposals_20261026/` record the calculations and sensitivity checks. Changing the initial split to four or five groups also yields a wider absolute median gap. Countries have equal weight in these analyses; they are not population-weighted global-access estimates.

Weather caches contain sampled and daily gridMET data for July–September 2023. Temperature is Celsius, rain mm/day, speed m/s, and direction degrees FROM clockwise from north. Flow components use `u=-s*sin(theta)`, `v=-s*cos(theta)`. Spatial sampling is not block averaging. Monthly Tmax averages daily maxima; monthly rain sums daily rain. Source and decoding metadata remain in `data/scivis/`. Eight uniformly spaced dates support the three GIFs; complete daily records support monthly and persistence analyses. Contours use the Marching Squares family through the plotting library's serial algorithm; the worked cell uses actual cached temperatures.

## Method provenance and allocation

Curve bundling is informed by Heinrich et al., *Evaluation of a Bundling Technique for Parallel Coordinates*: https://arxiv.org/abs/1109.6073 . Our curves use explicit adoption groups and constrained midpoints. They are not the filled density ribbons in the September 22 lecture.

Fixed-cohort analysis adapts the principle of tracking identities rather than replacing percentile members: https://documents.worldbank.org/curated/en/914431468162277879/pdf/WPS6719.pdf . It does not reproduce an income estimator or establish causation.

The report records one distinct Infovis and one SciVis task per member. Only cleaning and processing may be shared. The allocation does not certify actual implementation or individual review on anyone's behalf.

The team is preparing the required video per its latest instructions. Use the current recording package; network scenes are revised after the instructor clarification. Human voices and the live demonstration still need recording.

## Network revision following instructor clarification (29 October 2026)

The network now begins with all 15,931 unique pairs among 179 complete 2020 country profiles. Similarity is `1/(1 + Euclidean distance)` after z-scoring four indicators. `data/network_all_pair_similarities.csv` and the `all_edges` field in `data/country_network_2020.json` retain the complete pair universe. The JSON `edges` field is the default filtered graph, not the source universe.

The default threshold is the 95th percentile, **0.5697629885414606**, retaining **797 edges** (about 5% of pairs). All 179 nodes remain, including **12 isolates**. This is a declared sparse starting view, not a statistically optimal cutoff. The report shows the score histogram and connectivity across 77 percentile cutoffs. Nearby thresholds and 30 seeded small-input perturbations quantify sensitivity. The perturbation experiment is not claimed to implement a named threshold-selection method.

The 30 October research review adds median/IQR scaling, rank scaling and four leave-one-indicator-out checks, each with its own P95 cutoff. Edge Jaccard is 0.801 for IQR, 0.460 for ranks and 0.338-0.512 for feature omission. The highest cutoff preserving full connectivity retains 11,526 edges, so it is not adopted as the default. The [method review](output/network_revision/index.html) explains the alternatives, primary sources and two supporting plots (metric sensitivity and the continuous all-pair matrix). Figure 1 replaces the old retention curve with connectivity sensitivity; Figure 3 now draws all isolates. Run `python scripts/network_threshold_revision.py` to recreate these checks, then rebuild and sync the report. The baseline graph and video numerical claims remain unchanged.

The browser slider filters all pair scores, not a nearest-neighbor subset. Set it to zero for the complete graph; Reset restores the exact default. Layout coordinates stay fixed while filtering. Spring and Spectral lay out the 167-node connected core and place the 12 isolates on a separate bottom row; Circular includes all nodes. NodeTrix has six non-singleton groups plus 12 isolates; group 5 has 93 of 105 possible pairs. Groups and white matrix cells must be interpreted relative to the displayed threshold.

Rebuild from `ass2`:

```powershell
python scripts/build_infovis_data.py
python scripts/preview_lecture_extensions.py
python scripts/network_threshold_revision.py
python scripts/verify_network_threshold.py
python scripts/build_a1_style_report.py
python scripts/sync_report_delivery.py
python scripts/verify_story_report.py
python scripts/package_selected_report.py
```

Evidence: `data/network_threshold_audit.json`, `output/network_revision/threshold_sensitivity.csv`, `input_perturbations.csv`, `facts.json`, and the [diagnostic gallery](output/network_revision/index.html). Browser controls were tested with the all-pair source. Earlier archived reports and screenshots describe superseded network rules.
