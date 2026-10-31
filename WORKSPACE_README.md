# DAS732 Assignment 2 - Team Plot Twist

**Main question:** What do averages and snapshots hide about inequality, relationships and change over time?

**[Live dashboard](https://aithal007.github.io/DV_assignment2/)** | [Report](output/pdf/DAS732_A2_Report_IEEE.pdf) | [32 explained figures](https://aithal007.github.io/DV_assignment2/figures.html)

The report has **27 pages and 32 figure sets**. Figures 1-17 study country internet data; Figures 18-32 study daily US weather separately. The PDF links below figures open working UIs, animations or static figure readings. The site is published from `docs/` in this same repository.

## 1. Get the project and open the visualizations

```powershell
git clone https://github.com/aithal007/DV_assignment2.git
cd DV_assignment2
python run_visualizations.py
```

Open `http://127.0.0.1:8765/web/home.html` if the browser does not open automatically. Keep the server running; Ctrl+C stops it. Windows users may double-click `START_VISUALIZATIONS.cmd`. Running the supplied apps needs Python's standard library and a modern browser, without pip dependencies or an external CDN. D3/JSON files are local. Use the server rather than opening HTML as `file://`, which can block JSON loading.

| View | Local page | Try this |
|---|---|---|
| Similarity network | `web/network.html` | Switch Spring/Spectral/Circular, select India, change threshold, pan/zoom, then Reset. |
| Country profiles | `web/index.html` | Change year/region, adjust bundling, brush, reorder axes and inspect a country. |
| Paired changes | `output/pcp_changes/index.html` | Brush gains, rotate axes and compare straight/bundled lines. |
| Zoomable treemap | `web/treemap.html` | Switch hierarchy, zoom into Asia, hover countries and go Back. |

GIFs: `images/scivis/scivis_global.gif`, `scivis_local.gif`, `scivis_contour.gif`. Each has eight dates; full-period analyses use all 92 days. Assessment images are `images/report/Fig1.png` through `Fig32.png`.

## 2. Install the regeneration dependencies

Use Python 3.11+, packages in `requirements.txt`, Node.js for the JavaScript syntax checks, and MiKTeX/TeX Live with `pdflatex` on PATH for PDF generation. This revision was checked with Python 3.14 and MiKTeX. LaTeX packages are listed in `report_latex/design_reference_preamble.tex`, including IEEEtran. Run from the repository root:

```powershell
python --version
python -m pip install -r requirements.txt
node --version
pdflatex --version
```

Optional isolated environment: run `python -m venv .venv` first. Then replace `python` in every pip/script command with `.\.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS/Linux. Activation is unnecessary. Install packages and run scripts with the same interpreter. Internet access is needed for missing dependencies; supplied extracts and caches support the cached numerical route afterward.

## 3. Preprocess before visualizing

```powershell
python -X utf8 scripts/preprocess_data.py
```

`preprocess_data.py` prepares/audits inputs without drawing plots.

### Country inputs and transformations

1. Read three A1 OWID/ITU extracts in `data/raw/`: `number-of-internet-users.csv`, `share-of-individuals-using-the-internet.csv`, and `ict-adoption-per-100-people.csv`. `region_lookup.csv` is supplied code-based metadata.
2. Rename indicator columns, enforce numeric types, reject duplicate `(entity, code, year)` keys, and outer-join the extracts with one-to-one validation. Outer joining preserves rows with an absent indicator.
3. The join has **13,387 rows**. Remove **823 explicitly listed aggregate rows**, leaving **12,564 country-year records**. Missing observations remain missing; do not impute, interpolate or replace them with zero. Attach regions by code; downstream views retain unmapped entries as Unclassified.
4. Apply explicit complete-case rules: **179** complete 2020 network profiles; the same **175** multivariable countries in both 2015/2020; **159** adoption countries with all 21 years from 2000-2020; and **184** treemap countries with count/share values, totaling **4,521,767,530** included users.
5. Calculate each country's paired change before summarizing gains. Figure 11 fixes starting cohorts using 2000 adoption, keeping members unchanged. National adoption rates use equal country weights; treemap area uses user counts. Subscriptions per 100 people can exceed 100 and do not count unique people.

Outputs: `data/processed/master_dataset_countries_only.csv`, `region_lookup.csv`, and `preprocessing_audit.json`. The audit retains raw row counts, join/exclusion counts, missing values, cohort sizes, steps and SHA-256 hashes. Source extracts remain available.

### Weather inputs and transformations

1. Our selected gridMET interval, **July 1-September 30, 2023**, spans summer into early autumn, allowing comparisons of cooling, rainfall timing and persistent conditions. Inputs are daily maximum temperature (`tmmx`), rain (`pr`), 10 m wind speed (`vs`) and wind FROM-direction (`th`).
2. Acquisition decodes NetCDF missing values/packing before converting source temperature from Kelvin to Celsius. Supplied NPZ caches are already Celsius: preprocessing validates them without converting twice. Rain stays mm/day, speed m/s and direction degrees FROM clockwise from north.
3. Read every sixth native grid point, approximately 0.25-degree sampling. This is subsampling, not averaging or new source resolution. Validate matching coordinates and consecutive dates. Retain **13,416 cells valid for all four variables on all 92 days**; cosine-latitude weights approximate area.
4. Eight evenly spaced dates, 13 days apart and including both endpoints, meet the assignment's 5-10 scalar time instances. Check every sampled field against the corresponding full-cache day. Monthly/event analyses use all 92 days.
5. Monthly temperature averages daily maxima; monthly rain sums daily rain. Quiver flow components use `u=-speed*sin(direction)` and `v=-speed*cos(direction)`. Descriptive event cutoffs are Tmax >=35 C, rain <1 mm/day and speed >=5 m/s. Longest runs are computed within each cell.

The full cache is `data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz`; the sampled cache ends in `_n8_s6.npz`. `data/processed/weather_support.npz` stores the common mask, weights, coordinates and dates. Cache hashes, units and sample checks are in the preprocessing audit; acquisition metadata are in `data/scivis/`.

If a cache is missing, use network access to retrieve it:

```powershell
python -X utf8 scripts/preprocess_data.py --download-weather
```

Source: [gridMET](https://www.climatologylab.org/gridmet.html). The default cached route does not download full annual NetCDF files again.

## 4. Professor's threshold suggestion and our chosen P95 rule

Following the professor's advice, we use derived similarities and inspect their distribution before filtering highly similar pairs. She mentioned perturbation as one possible semi-automated approach. **P95 is our team's display choice; the professor did not prescribe that percentile.**

Z-score each of four indicators across the 179 complete countries: subtract its mean and divide by its population standard deviation (`ddof=0`). Compute Euclidean distance between country profiles, then similarity `s=1/(1+d)`. All **15,931 unique pairs** are retained in `data/network_all_pair_similarities.csv` and JSON `all_edges`.

The score distribution's **95th percentile is 0.5697629885414606**. Keeping `s >= cutoff` retains **797 edges**, about the strongest 5%, with **12 isolates** and one **167-country connected core**. P95 is neither similarity 0.95 nor a confidence level. It is a transparent sparse default, not a significance/optimality claim.

Figure 1 compares connectivity across 77 cutoffs. Boxed rows in Spring/Spectral deliberately place the default isolates. Those are measured countries with no qualifying pair, not an erroneous dotted baseline. Circular places the same countries around its circumference. Positions remain fixed when filtering, so default isolates can gain links at lower cutoffs.

Thirty seeded small-noise trials at the fixed cutoff give mean edge Jaccard 0.922. This is an illustrative robustness check, not a named threshold selector or calibrated error model. Metric/feature changes also affect links. Exact scores, sweep/noise/scaling tables, continuous similarity matrix and primary references are in the [method review](https://aithal007.github.io/DV_assignment2/output/network_revision/index.html).

Rebuild/check only the network:

```powershell
python -X utf8 scripts/build_infovis_data.py
python -X utf8 scripts/network_threshold_revision.py
python -X utf8 scripts/verify_network_threshold.py
```

## 5. Rebuild the report using supplied figures

For report text/layout changes, run:

```powershell
python -X utf8 scripts/build_a1_style_report.py
python -X utf8 scripts/sync_report_delivery.py
python -X utf8 scripts/verify_story_report.py
python -X utf8 scripts/verify_report_editorial.py
python -X utf8 scripts/package_selected_report.py
```

The active builder reads the design preamble, current manifest and selected figure exports, compiles with pdfLaTeX twice, and updates `REPORT.md`, explanations, manifests, the PDF and LaTeX source ZIP. `report_editorial_revision.py` supplies final preprocessing copy, professor attribution, link destinations and takeaways. Figures 6 and 32 have declared pair/cell selection rules and CSV evidence in `output/additional_evidence/`.

Direct LaTeX compilation is also possible:

```powershell
cd report_latex
pdflatex -interaction=nonstopmode -halt-on-error DAS732_A2_Report.tex
pdflatex -interaction=nonstopmode -halt-on-error DAS732_A2_Report.tex
cd ..
```

That updates `report_latex/DAS732_A2_Report.pdf`; the Python builder also copies the deliverable to `output/pdf/DAS732_A2_Report_IEEE.pdf`. The source ZIP includes the preamble and all 32 figure PNGs, without needing an external A1 folder.

## 6. Regenerate numerical inputs, figures and report

Run the stages in order, using raw country extracts and supplied weather caches:

```powershell
python -X utf8 scripts/reproduce_results.py --stage data
python -X utf8 scripts/reproduce_results.py --stage figures
python -X utf8 scripts/reproduce_results.py --stage report
```

Or run `python -X utf8 scripts/reproduce_results.py --stage all`. Add `--download-weather` if weather caches need retrieval. The pipeline prints stage/script names and stops on the first failed command. Keep the full repository structure: current selections use supplied archived manifests and comparison material. Regeneration overwrites derived outputs, so preserve a Git commit before experiments. Fixed seeds support default layouts/noise checks; dependency versions can cause small numeric/rendering differences. Checked exports are included.

| Result | Location |
|---|---|
| Report | `output/pdf/DAS732_A2_Report_IEEE.pdf` |
| Editable source | `report_latex/` |
| Numbered PNGs | `images/report/Fig1.png` ... `Fig32.png` |
| Input provenance | `data/processed/preprocessing_audit.json` |
| Pair scores/default graph | `data/network_all_pair_similarities.csv`, `data/country_network_2020.json` |
| Change/cohort evidence | `output/pcp_changes/`, `output/proposals_20261026/` |
| Pair/calendar additions | `output/additional_evidence/` |
| Portable deliverables | `output/DAS732_A2_Report_and_JavaScript.zip`, `output/DAS732_A2_LaTeX_Source.zip` |

## 7. Check the results

```powershell
python -X utf8 scripts/verify_network_threshold.py
python -X utf8 scripts/verify_additional_evidence.py
python -X utf8 scripts/verify_final_research.py
python -X utf8 scripts/verify_story_report.py
python -X utf8 scripts/verify_report_editorial.py
```

Checks cover pair scores/edges, 454 near-equal-adoption pairs, calendar day counts/runs, paired regional gains, rainfall windows, all 32 source figures, contribution IDs, three eight-frame GIFs, PDF/page/link integrity and JavaScript syntax. `python scripts/render_story_report.py` renders pages for visual inspection; text extraction alone does not establish legibility.

Optional browser automation needs Node.js, Playwright and Edge. Adjust the local runtime/browser paths in `scripts/audit_github_pages.mjs` on another machine. `node scripts/audit_github_pages.mjs` tests local `docs/`; pass the live URL to test deployment. The apps do not require this audit environment.

## 8. Refresh the same-repository Pages site

After rebuilding and syncing images/report:

```powershell
python scripts/refresh_pages_assets.py
git add docs README.md scripts data images output/pdf report_latex
git commit -m "Refresh report and visualizations"
git push origin main
```

Pages publishes `docs/` on `main`. `docs/.nojekyll` preserves static paths. Refresh copies the current PDF, 32 figure PNGs/readings, browser JS/JSON, threshold evidence and GIFs. There is no application backend. Both project and site are public in this one repository; the former separate Pages repository was deleted.

## 9. Interpretation, contributions and references

Each interpretation connects its question, visible evidence, inference and scope. Aggregate country indicators describe associations, not causes of access; subscriptions are not unique people. Three months of weather do not establish a climate trend. Calendar examples use explicit selection rules rather than claiming a representative sample.

The report allocates a distinct Infovis and SciVis task to each member; only preprocessing may be shared. The table records responsibility, not certification of another person's implementation/review. The team supplies its truthful disclosure statements.

Method provenance: [NodeTrix](https://www.dgp.toronto.edu/~mjmcguff/research/nodetrix/nodetrix.pdf), [PCP bundling](https://arxiv.org/abs/1109.6073), [threshold/percolation study](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00441/full), [fixed-cohort principle](https://documents.worldbank.org/curated/en/914431468162277879/pdf/WPS6719.pdf). Adaptations and their limits are stated in the report/method review.

The team's requested video materials are in `output/video_presentation/`. Numerical/report regeneration does not rebuild that deck or record human narration. This revision strengthens report explanations; video recording follows its separate guide.

## Sources and interaction evidence

The report contains ten cited references, including gridMET, OWID, NetworkX, D3, ContourPy/Marching Squares and Gephi (a permitted alternative, not the tool used). July-September covers summer heat into autumn cooling; 2023 provides a documented Southwest heat episode (NOAA reference in the report). Eight uniformly spaced dates give reproducible, balanced temporal coverage, while all 92 days are used for frequency and persistence; eight snapshots alone cannot establish either.

[Complete uncropped browser screenshots](https://aithal007.github.io/DV_assignment2/interactions.html) show the working UI controls. The network supports threshold, layout, region and isolate filtering; the treemap compares squarified and slice-and-dice partitioning without changing values. Run `node scripts/audit_github_pages.mjs` after refreshing Pages to exercise controls and refresh those screenshots.
