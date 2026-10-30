"""Sync numbered images and gallery with the current selected report."""
from pathlib import Path
import html,json,shutil
import pymupdf
R=Path(__file__).resolve().parents[1]
def main():
 figures=json.loads((R/'data/current_figure_manifest.json').read_text(encoding='utf-8'));out=R/'images/report';out.mkdir(exist_ok=True)
 cards=[]
 for f in figures:
  n=f['figure'];shutil.copy2(R/f['path'],out/f'Fig{n}.png')
  if (R/f['path']).with_suffix('.svg').exists():shutil.copy2((R/f['path']).with_suffix('.svg'),out/f'Fig{n}.svg')
  fields=[('How to read',f['explanation'][1]),('Why this chart',f['explanation'][2]),('Interpretation',f['detailed_interpretation']),('Takeaway',f['explanation'][4])]
  cards.append(f'<article id="fig{n}"><h2>Figure {n}. {html.escape(f["title"])}</h2><a href="../../{f["path"]}"><img loading="lazy" src="../../{f["path"]}"></a>'+''.join('<h3>'+a+'</h3><p>'+html.escape(b).replace('\n\n','</p><p>')+'</p>' for a,b in fields)+'</article>')
 extras=json.loads((R/'data/supplementary_figure_manifest.json').read_text(encoding='utf-8'))
 cards.append('<h2>Supplementary analyses</h2><p>These are additional analyses and older versions; the numbered figures above match the current report.</p>')
 for f in extras:
  if (R/f['path']).is_file():cards.append(f'<p><a href="../../{f["path"]}">{html.escape(f.get("title",f["path"]))}</a></p>')
 (R/'output/quality_figures/index.html').write_text('<!doctype html><meta charset="utf-8"><title>Current A2 report figures</title><style>body{font:16px Arial;max-width:1250px;margin:36px auto;color:#17384e;background:#f0f4f7}article{background:white;padding:28px;margin:25px 0}img{width:100%;height:auto}p{line-height:1.6}h3{margin-bottom:5px}</style><h1>Current A2 report: full-resolution figures</h1><p>Numbering and explanations match the selected report. Click any image to inspect its original resolution.</p>'+''.join(cards),encoding='utf-8')
 p=R/'data/report_selection.json';selection=json.loads(p.read_text(encoding='utf-8'));selection.update(date='2026-10-27',note='Approved paired-changes PCP (Figure 4), association comparison (Figure 7), fixed initial cohorts (Figure 10), gentle curve PCP (Figure 5), expanded simple-English interpretations; no formal bibliography by user preference. Indexed images and gallery match the report.');p.write_text(json.dumps(selection,indent=2),encoding='utf-8')
 pages=len(pymupdf.open(R/'output/pdf/DAS732_A2_Report_IEEE.pdf'))
 text=f'''# DAS732 Programming Assignment 2

**Main question:** What do averages and snapshots hide about inequality, relationships and change over time?

[Open the live interactive visualizations](https://aithal007.github.io/DV_assignment2_pages/). The full assignment project is maintained in the private GitHub repository `aithal007/DV_assignment2`.

[Current report](output/pdf/DAS732_A2_Report_IEEE.pdf): {pages} pages, 32 numbered figure sets (all original 30 plus two added plots). [Full-resolution gallery](output/quality_figures/index.html). Numbered assessment images are in `images/report/Fig1.png` through `Fig32.png`; complete browser screenshots are in `images/gui/`.

The report uses the existing IEEE design and simple-English reading guides, interpretation and takeaways. Figure 4 compares paired 2015?2020 changes, with a shared zero reference and a selected 20?30-point gain range. Figure 5 uses gentle curve bundles and stated adoption bands. Figure 7 contrasts level and gain correlations for the same 175 countries. Figure 10 follows three fixed groups of 53 countries from 2000 to 2020. Figure 6 retains the full scatterplot matrix. The report has no formal bibliography by team preference; source provenance and method links remain with the code. The team will provide its own truthful AI disclosures.

## Run the interactive visualizations

Run `python run_visualizations.py` from the submitted folder, or double-click `START_VISUALIZATIONS.cmd`. Open http://127.0.0.1:8765/web/home.html and keep the server running. The local apps require Python's standard library and supplied JavaScript/JSON assets; no CDN is needed.

- Network: `web/network.html`; NetworkX spring, spectral and circular layouts, country search, selected neighbors and edge filtering.
- Parallel coordinates: `web/index.html`; 175 matched countries, year and region filters, fixed axes, axis brushing, axis reordering, hover values and straight/gently bundled paths. Color and bundles use explicit adoption bands below 40%, 40–below 70%, and at least 70%. These are descriptive comparison bands, not discovered country types. Bundling changes only paths between axes; midpoint clamping prevents artificial peaks. `web/pcp-curves.js` contains the curve function.
- Changes PCP (Figure 4): `output/pcp_changes/index.html`; paired 2015?2020 changes for all 175 countries, a gain-range brush, reordered axes, exact hover values and straight/gently bundled paths. `paired_changes.csv` records all four differences; `validation.json` and `browser_validation.json` provide checks.
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

A2 requires no video. Older slides, narration and recording guides remain optional companion material in `output/video_presentation/`; they have not been updated for these report replacements.
'''
 from network_threshold_revision import readme_section
 text=text.replace('A2 requires no video. Older slides, narration and recording guides remain optional companion material in `output/video_presentation/`; they have not been updated for these report replacements.','The team is preparing the required video per its latest instructions. Use the current recording package; network scenes are revised after the instructor clarification. Human voices and the live demonstration still need recording.')
 (R/'README.md').write_text(text+readme_section(),encoding='utf-8');print(f'Synced 32 images, gallery and README; report {pages} pages')
if __name__=='__main__':main()
