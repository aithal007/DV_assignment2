# Research beyond the lecture slides

Main question: **What do averages and snapshots hide about inequality, relationships and change over time?**

Three candidates were implemented on the actual project data. Open `../output/research_candidates/index.html` for full-size figures, interpretations, caveats and sources. The current 25-page report is unchanged during this research trial.

## 1. Rainfall total and concentration maps: strongest direct replacement

**Research basis.** Climdex defines maximum consecutive five-day precipitation, Rx5day: https://www.climdex.org/learn/indices/ . This candidate adapts the rolling-window idea to a within-month concentration ratio. It does not claim to implement a full climatological index.

**Calculation.** For each common valid grid cell and month, sum all daily rain, find the maximum sum of five consecutive days wholly inside that month, and divide that maximum by the monthly total. The top row preserves the existing three monthly-total maps; the second row shows the new ratios on a shared 0-100% scale. Ratios are displayed only where the monthly total is at least 10 mm, avoiding large percentages driven by almost no rain.

**Evidence.** Among eligible cells, 43.8% of weighted area in July, 67.5% in August and 77.6% in September received at least half its monthly rain within one five-day window. The eligible areas themselves differ: 74.75%, 92.32% and 94.09% of the common footprint. Thus these conditional percentages do not compare identical subsets. A separate sensitivity table varies the minimum total through 1, 10, 25 and 50 mm.

**Added meaning.** Monthly totals cannot distinguish a short concentrated episode from rain spread across many days. The new row directly exposes that lost temporal structure while preserving the original totals. It does not establish floods, runoff, hourly intensity, an anomalous season, or climate change. Cross-month episodes are excluded by the explicit within-month definition.

**Decision.** Replace current Figure 22 with this six-panel comparison. It is a stronger use of one figure slot, although its greater height requires a fresh PDF layout check against the 27-page maximum.

## 2. Regional gain raincloud: strongest country-summary enhancement

**Research basis.** Allen et al., *Raincloud plots: a multi-platform tool for robust data visualization*, Wellcome Open Research: https://pmc.ncbi.nlm.nih.gov/articles/PMC6480976/ . Rainclouds combine a distribution shape with individual observations and summary information.

**Calculation.** Retain the 175-country complete matched panel, subtract each country's 2015 adoption from its 2020 adoption, and display every gain by region. A circle and interval show the median and middle 50% of individual gains. A black tick separately shows the difference between the 2020 and 2015 regional medians. KDE shape is supplied only for regions with at least 10 countries; jitter is cosmetic and deterministic. Density height is normalized separately by region and density is truncated at the observed range.

**Evidence.** Asia's difference of regional medians is 26.55 percentage points, while its median individual country gain is 19.75. Its 41 individual gains range from -0.84 to 49.94, and the middle half spans 9.86 to 28.25. South America's median individual gain is 21.76 versus a 16.54-point difference of regional medians. Rankings can therefore depend on which question is being answered.

**Added meaning.** This distinguishes the change of a regional summary from the typical matched country's change and exposes within-region heterogeneity. The restored dumbbell is useful for absolute endpoints, but cannot show this distribution by itself. Intervals are not confidence intervals; no causal effect is estimated. Country gains are descriptive changes in the supplied series, which may also reflect revisions or measurement differences.

**Decision.** Enhance Figure 11 with the raincloud, retaining an endpoint panel or endpoint table. Do not remove the required horizon or ridgeline variations. This adds more information than another smooth distribution without individual observations.

## 3. Event-sequence raster plus run exceedance: strongest explanation of hidden timing

**Research basis.** Swihart et al. (2010), *Lasagna plots: a saucy alternative to spaghetti plots*: https://pmc.ncbi.nlm.nih.gov/articles/PMC2937254/ . A heatmap row for each repeated-measure unit preserves temporal order without crossing trajectories. The candidate adapts that approach to binary daily conditions.

**Calculation.** Hot/dry means daily maximum temperature at least 35 C and daily precipitation below 1 mm. The raster holds total frequency exactly constant across its rows. Among exact-count groups with at least 20 cells and at least 10 event days, select the group with the largest range of longest runs, then prefer larger groups if tied. This deliberately selects an explanatory contrast, not a representative sample. The resulting group has 21 cells, all displayed. The separate run-exceedance curve uses all 13,416 common cells and cosine-latitude area weights.

**Evidence.** All 21 example cells have 75 hot/dry days, but their longest runs span 17-67 days. Across the full sampled footprint, 5.15% of area has a run of at least 30 days; only 0.117% has a run of at least 60 days. This contextualizes the existing headline maximum of 67 days: it is a local extreme, not typical domain behavior.

**Added meaning.** A frequency map cannot reconstruct sequences. A maximum-run map cannot show all interruptions or how common long runs are across the domain. The paired raster and exceedance curve show both an explicit same-count contrast and its domain-wide context.

**Decision.** Use as a companion to Figure 29, or redesign that figure while retaining its location maps and threshold sensitivity. It is useful but less straightforward to replace an existing figure without losing other information. It does not define an official heatwave/drought index. Boundary runs may extend outside the observed window; daily fields do not establish hourly simultaneity. Cells are spatially dependent, and selected rows are not area-weighted.

## Selection and verification

Prioritize the rainfall replacement, then the regional gain enhancement. Keep the event sequence as an optional explanatory companion if the page budget permits. Preserve required assignment experiments and the new quantile comparison: these candidates answer different questions and do not supersede the full assignment coverage.

Other approaches considered include Gardner-Altman estimation plots (https://acclab.github.io/DABEST-python/tutorials/02-two_group.html). They emphasize effect estimates and uncertainty. For this descriptive complete-case country panel, raw matched gains add clear information without introducing an unjustified population-sampling interpretation. No bootstrap confidence intervals are claimed.

The script checks the 175-country cohort and common 13,416-cell weather footprint; recomputes all rolling maxima independently with cumulative sums; checks selected run lengths independently with grouped binary sequences; and verifies the domain-wide exceedance curve is monotone. PNGs were visually reviewed. CSVs retain raw country gains, regional summaries, cell-level rainfall results, mask sensitivity, selected cell coordinates, full displayed sequences and the run-exceedance series. Run `python -X utf8 ass2/scripts/research_plot_candidates.py` to regenerate from existing workspace inputs. The preview archive includes analysis outputs and the script; original cached weather inputs are workspace dependencies.
