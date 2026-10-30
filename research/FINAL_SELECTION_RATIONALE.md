# Final 30-figure selection and last web review

## Decision

The final report retains the question **What do averages and snapshots hide about inequality, relationships and change over time?** It selects 30 numbered figure sets, including required multi-panel experiments. The final PDF is 26 pages, including references, with a question, encoding explanation, detailed interpretation, limitations and boxed main takeaway for every figure. Full rationale and evidence fields also remain in the companion gallery and editable Markdown.

Relative to the 25-page, 29-figure version:

- **Add Figure 11:** annual absolute/relative inequality and within/between-region variance. It adds a substantive qualification to the digital-divide conclusion and exposes the 2013 turning point.
- **Upgrade Figure 12:** preserve the regional dumbbell endpoints and add individual-country gain rainclouds in the same figure. It distinguishes changes in regional medians from medians of matched changes.
- **Upgrade Figure 23:** preserve monthly rainfall totals and add within-month five-day concentration maps. It adds temporal evidence without discarding absolute rainfall.
- Keep Figure 10's quantile comparison: decile-specific changes and individual gains are different information from a scalar inequality index.
- Keep the SPLOM and country-change scatterplots. Replacing all raw data with correlation coefficients would conceal shape and outliers.
- Keep all required network-layout, JavaScript PCP/treemap, horizon/ridgeline, scalar, contour and vector experiments.

Regional correlation contrasts, milestone curves and event-sequence rasters remain research companions. They are useful, but their incremental value is smaller than the selected upgrades within the page budget. Original standalone dumbbells, rainfall maps and all other original images remain available in the workspace; no original graph is deleted.

## Last web and Medium pass

The following pages were opened during the final pass:

1. Pierre DeBois, **How to Create Raincloud Plots with ggrain for R Programming**, Medium/CodeX, February 7, 2026: https://medium.com/codex/how-to-create-raincloud-plots-with-ggrain-for-r-programming-0c7760821f6b . Only the public introduction was accessible; it is marked member-only. It was used to survey presentation ideas, not as methodological authority or implementation evidence. No inaccessible content was assumed.
2. Dario Weitz, **Scatter Plots, Why & How**, Medium/Analytics Vidhya, February 20, 2020: https://medium.com/analytics-vidhya/scatter-plots-why-how-3de6e1e32645 . Considered for presentation context. Its blanket correlation cutoffs and broad restrictions on scatterplot use are not adopted. The final design retains raw observations and contextual interpretation.

Statistical and algorithmic statements in the report are grounded in primary or official sources, rather than those Medium articles:

- Allen et al., **Raincloud plots: a multi-platform tool for robust data visualization**, Wellcome Open Research 4:63: https://doi.org/10.12688/wellcomeopenres.15191.1 . Our adaptation combines raw gains, density shape and descriptive intervals, with a separate paired endpoint panel. It does not claim confidence intervals.
- Rousselet, Pernet and Wilcox, **Beyond differences in means**, 2017: https://doi.org/10.1111/ejn.13610 . Our quantile plot is descriptive and uses linear empirical quantiles; it does not claim the paper's inferential procedure.
- World Bank Gini metadata: https://databank.worldbank.org/metadataglossary/environment-social-and-governance-%28esg%29-data/series/SI.POV.GINI . Relative inequality is distinguished from absolute gaps. Here the units are country adoption percentages, not household income.
- NIST, **One-way ANOVA overview**: https://www.itl.nist.gov/div898/handbook/prc/section4/prc431.htm . The sums-of-squares identity supports the descriptive variance decomposition. No ANOVA significance test is performed.
- Climdex, **Indices**: https://www.climdex.org/learn/indices/ . The maximum consecutive five-day precipitation concept motivates the concentration view. Our within-month ratio and 10-mm display mask are explicitly analyst-defined; they are not a full climatological Rx5day implementation.

## Interpretation commitments

The final narrative states that relative adoption inequality declines while absolute gaps remain above 2000 levels, with absolute dispersion narrowing after 2013. It does not assert that every inequality measure worsens. Regional comparisons distinguish typical individual gains from changes in regional summaries. Rainfall concentration retains the absolute totals, minimum-total mask, differing eligible areas and within-month window rule. Associations, partitions and selected weather thresholds remain descriptive.

The report also states the source wind height (10 m), explains the seasonal analytical rationale for the supplied interval and equal temporal sampling, and identifies Marching Squares-family contour tracing and its regular-grid rationale. The task-contribution split remains unassigned per the user's instruction to treat the current work as one contributor. JavaScript syntax/assets are checked; live browser interaction remains a documented manual check.
