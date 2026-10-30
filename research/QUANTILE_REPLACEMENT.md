# Replacement plot: progress versus absolute convergence

The PDF replaces the adoption alluvial with a two-panel quantile comparison. The alluvial remains useful for category transitions and is retained in the companion gallery. Its four broad bands cannot show changes within each band or directly measure absolute distributional spread.

## Research basis

Rousselet, Pernet and Wilcox (2017), *Beyond differences in means: robust graphical methods to compare two groups in neuroscience*, European Journal of Neuroscience 46, 1738-1748: https://doi.org/10.1111/ejn.13610 . The authors' implementation and explanation are at https://github.com/GRousselet/rogme . Their shift-function approach compares quantiles to expose distributional differences hidden by a mean.

This report uses a **descriptive adaptation**, not their inferential procedure: percentiles on the horizontal axis, empirical linear-interpolated quantiles, and no bootstrap intervals or significance tests. The original package uses other estimators and inferential options. Those procedures are not claimed here.

## What is computed

The same 159 countries have every annual adoption value from 2000 through 2020. Each country is weighted equally. Panel A shows the 10th through 90th adoption percentiles in 2000 and 2020. Panel B shows both Q2020(p) minus Q2000(p), and Qp(adoption2020 minus adoption2000). These are generally different because country ranks can change.

The P90-P10 absolute spread grows from **28.63 to 69.84 percentage points**. The median distributional shift is **69.16 points**, while the median individual gain is **62.09 points**. Thus adoption improves across the displayed deciles without convergence on this absolute spread measure. Relative inequality could behave differently; no claim about every inequality measure is made. Percentage-point bounds and complete-case selection matter.

The comparison adds direct evidence for the report's main question: broad progress and narrowing inequality are distinct. It does not identify causes or represent the population-weighted distribution of people.

## Reproduction

Run `python -X utf8 ass2/scripts/build_quantile_change.py`. The main report builder also runs this step. `output/lecture_previews/adoption_quantile_change.csv` contains the nine plotted rows; `adoption_quantile_country_values.csv` contains the underlying matched panel and gains. PNG, SVG and metrics JSON are supplied in the same folder. The report verifier independently recomputes the deciles with Python's inclusive order-statistic method and checks the complete panel.
