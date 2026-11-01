# Approved replacements — selected for Figures 7 and 10

The assignment rubric allocates 4/30 to completeness, 8/30 to correctness, 8/30 to quality of inferences, and 10/30 to data handling. These supporting figures do not replace any required visualization type. No mark increase is guaranteed.

Figure 7: Association audit. Both cohorts contain exactly the same 175 countries. Country changes are computed after joining on country code. Three level correlations are compared with three change correlations, and the broadband-change scatter shows the underlying observations. Spearman coefficients measure monotone association, not causal effects. The level correlations already appear in Figure 6; this figure's new contribution is the controlled comparison with changes for all three infrastructure measures.

Figure 10: Fixed initial cohorts. The same 159 countries with complete 2000–2020 records are split into thirds only once using 2000 adoption. Each cohort has 53 countries and no boundary ties. Country identities stay fixed. Median paths and 2020 individual values show between-group persistence and within-group exceptions. This complements Figures 15–16, which regroup distributions by year or region. Countries have equal weight; results are not a population-weighted measure of global access. Initial cohorts are descriptive, not natural types or a causal treatment. A larger absolute gap alone does not establish greater relative inequality. The wider median gap also appears with four and five initial groups.

Research: Lakner and Milanovic, World Bank WPS6719, explains why tracking fixed observations adds information beyond comparing anonymous distributions. Our cohort summary is an adaptation of this identity-preserving principle, not a reproduction of an income growth-incidence estimator.
https://documents.worldbank.org/curated/en/914431468162277879/pdf/WPS6719.pdf

Reproduce: python -X utf8 scripts/preview_rubric_replacements.py
The script asserts matching identities, cohort counts, boundary ties, complete data, sensitivity direction, and unchanged report hashes. CSV tables and SVG/PNG previews are alongside this file.
