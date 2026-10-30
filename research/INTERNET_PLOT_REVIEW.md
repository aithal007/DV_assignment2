# Internet-specific research trials

Main question: **What do averages and snapshots hide about inequality, relationships and change over time?**

Three new figures were calculated and rendered from the existing internet datasets. Open `../output/internet_research/index.html`. The previous regional gain raincloud is also relevant and is linked from that gallery. These are research previews; the 25-page report has not yet been expanded.

## Priority 1: absolute versus relative inequality, with regional decomposition

The existing quantile plot establishes widening absolute P90-P10 gaps between 2000 and 2020. The new figure adds two essential distinctions: relative inequality can move in the opposite direction, and endpoint comparisons hide reversals during the interval.

On the identical 159-country complete annual panel:

- The mean absolute pairwise adoption gap rises from **11.43 to 28.78 percentage points** between 2000 and 2020.
- It peaks at **32.86 points in 2013**, then falls. Thus the full-period increase is not a continuous worsening.
- The Gini of country adoption rates falls from **0.708 to 0.222**. Mean adoption grows faster than the absolute pairwise differences.

Let x_i be country adoption, n the number of countries, and mu the equal-country mean. The mean pairwise gap is sum over all ordered pairs of |x_i-x_j| divided by n squared (self-pairs included). The Gini is that gap divided by 2*mu. This is an application to national adoption percentages, not an income Gini or a population-weighted measure of people's internet access. The two panels deliberately have different units and no shared vertical scale.

The third panel applies the exact identity Var(X) = sum_g p_g Var(X|g) + sum_g p_g (mu_g-mu)^2, with p_g equal to each region's country share. On the 158 classified countries, **53.04% of 2020 variance is between regional means and 46.96% is within regions**. Regional averages therefore omit nearly half the variation on this measure. This is a descriptive partition, not the causal proportion explained by geography. The unclassified country is retained in the first two panels and excluded from the regional partition only.

Research basis: [World Bank Gini metadata](https://databank.worldbank.org/metadataglossary/environment-social-and-governance-%28esg%29-data/series/SI.POV.GINI) distinguishes relative from absolute inequality. [NIST's sums-of-squares decomposition](https://www.itl.nist.gov/div898/handbook/prc/section4/prc431.htm) supports the exact within/between partition. No ANOVA hypothesis test is performed.

**Report use:** highest priority. Expand or redesign Figure 10 with absolute/relative trajectories alongside the quantile comparison, and place the decomposition in a companion panel if legible. The conclusion should say: *Relative inequality declined, while absolute gaps remained wider than in 2000; absolute dispersion nevertheless narrowed after its 2013 peak.* This is more precise than saying simply that inequality increased or decreased. Preserve the figure showing individual gains, since neither Gini nor variance identifies who gained.

## Priority 2: pooled versus regional infrastructure associations

The new contrast plot compares Spearman correlations of 2020 levels with correlations of 2015-2020 matched-country changes, separately for broadband and mobile subscription intensity. All rows use subsets of the same 175-country matched panel; they do not use the larger 179-country graph cohort.

The pooled broadband association changes from **0.831 for levels to 0.054 for changes**, already established in the report. The new information is its regional structure. Europe's mobile/adoption level correlation is only **0.056**. North America's broadband coefficient is **0.536 for levels and -0.375 for changes**. Neither result establishes a causal technology effect or a statistically reliable reversal; regional sample size and range restriction matter. Raw points, available in the exported table and existing scatterplots, are needed to check shapes and influential countries. Three unclassified countries and eight Oceanian countries are explicitly flagged as very small groups.

Research basis: [Kievit et al., Simpson's paradox in psychological science: a practical guide](https://pmc.ncbi.nlm.nih.gov/articles/PMC3740239/) motivates examining associations at different aggregation levels. This figure does **not** claim a demonstrated Simpson's paradox: comparing levels with changes or seeing heterogeneous coefficients is not enough to establish one.

**Report use:** a compact companion to Figures 6-7. It strengthens the infrastructure story beyond a single pooled coefficient. Keep the scatterplot matrix or a raw-point view; replacing every scatterplot with correlations would lose nonlinearity and outlier information. Circle-to-diamond connectors are comparisons, not time trajectories or confidence intervals.

## Priority 3: adoption milestone timelines

Each regional curve gives the fraction of its fixed panel ever observed at or above 50% or 75% adoption by a given year. It answers timing and coverage questions that a regional median cannot answer.

By 2020, the 75% milestone had been reached by **32/37 European countries (86.49%)**, **23/37 Asian countries (62.16%)**, and **1/45 African countries (2.22%)** in the classified complete annual panel. The chart includes the other three regions as well. These denominators are fixed across years and differ from the matched 175-country panel.

The curve is an empirical cumulative attainment summary, inspired by the [empirical distribution function](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/ecdfplot.htm). All countries remain in the denominator; those not observed to reach the milestone by 2020 are not silently discarded. It is not a Kaplan-Meier estimate, hazard model or forecast. Countries already above a threshold in 2000 may have crossed earlier; annual values do not identify exact dates. Once counted, a country remains counted even if its adoption later falls. Thus 'ever reached' is different from 'currently above' or 'sustainably above'.

**Report use:** lower priority because required horizons already provide temporal evidence. Use it when the narrative asks how long countries took to reach widespread adoption. Keep it as companion material if adding it would exceed 27 pages.

## Combined recommendation for the internet section

1. Prioritize the absolute/relative inequality comparison: it materially improves the answer to the main question.
2. Retain the regional gain raincloud trial to reveal individual experiences behind the restored dumbbells.
3. Add the regional association contrast only with enough room for raw-data evidence.
4. Keep milestone curves as a useful optional companion. Avoid adding all trials merely to increase the chart count.

Required network layouts, JavaScript PCP and treemaps, two horizons and two ridgelines remain required evidence. New research plots should complement or consolidate analytical extensions rather than displace these experiments.

## Verification and artifacts

The generator independently checks the pairwise Gini against its sorted-value formula, verifies within + between = total variance for every year, checks Spearman values against correlations of ranks, and checks monotonicity of every cumulative attainment curve. CSVs export annual inequality values, exact cohorts and correlations, milestone shares and country-level first-observed years. All three figures were visually inspected. Rebuild with `python -X utf8 ass2/scripts/research_internet_candidates.py`; the original country JSON and CSV files remain workspace inputs.
