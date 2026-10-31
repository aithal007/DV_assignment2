# Beyond Averages and Snapshots

Connectivity Profiles and Daily Weather | Team Plot Twist | DAS732 Assignment 2

[Live dashboard](https://aithal007.github.io/DV_assignment2/)

## Abstract

What do averages and snapshots hide about inequality, relationships and change over time? We study country internet indicators and daily US weather separately. Network, multivariable, temporal and spatial views connect each question to measured evidence. Broadband and internet use correlate strongly across country levels (0.831), but weakly across their changes (0.054). About 47% of measured adoption variation lies within regions. Hot-dry conditions occupy 16.27% of weighted grid-cell days, yet local runs reach 67 days. These contrasts show why group summaries, endpoints and separate frequencies need individual values, histories and shared timing for interpretation.

## Introduction

A national adoption rate hides infrastructure differences; a regional mean hides its member countries; a monthly weather summary hides daily events. We use linked comparisons to recover that missing detail.

**Central question: What do averages and snapshots hide about inequality, relationships and change over time?**

We ask: (1) Do similar internet-use levels conceal different telecom profiles? (2) Does overall progress imply catch-up among the same countries? (3) What do weather averages and selected dates omit about location, event timing and duration? Country data answer the first two questions; the separate weather investigation answers the third. Each result is interpreted as a descriptive pattern in the included data, with its scope stated.

## Data and preparation

**Country inputs and cleaning.** Three A1 OWID/ITU CSV extracts [2] provide internet-user counts, internet-use percentages and telecom subscriptions. `scripts/preprocess_data.py` renames columns, checks source-key uniqueness and numeric types, then outer-joins the files on entity, country code and year with one-to-one validation. The join has 13,387 rows; removing 823 explicitly listed aggregate rows leaves 12,564 country-year records. Missing values remain missing: they are neither replaced with zero nor imputed. A separate code-based lookup supplies regions; unmapped entries remain Unclassified.

**Comparable cohorts and transformations.** Each task declares its complete cases: 179 countries with all four 2020 profile indicators for the network; the same 175 countries in both 2015 and 2020 for paired changes; 159 countries with all 21 annual adoption values for 2000-2020; and 184 countries with user counts and adoption for treemaps. A change is computed within country before summarizing. Internet use is a percentage of people; landline, broadband and mobile values are subscriptions per 100 people and may exceed 100. These units are retained in profiles and changes.

**Professor's guidance and network construction.** Following Prof. Jaya Sreevalsan Nair's advice, we score every country pair, inspect the similarity distribution and filter highly similar pairs. Four indicators are z-scored separately across the 179 countries: subtract the indicator's country mean and divide by its standard deviation. Euclidean distance d gives similarity s=1/(1+d). Our team chooses the 95th percentile, P95=0.569763, as the sparse default: 797 of 15,931 pairs remain, with all 179 nodes retained. The professor suggested distribution-based thresholding and mentioned perturbation as an option; she did not prescribe P95. Figure 1 explains that choice and its sensitivity.

**Weather period and sampling rationale.** gridMET [1] supplies `tmmx` (daily maximum temperature), `pr` (rain), `vs` (wind speed at 10 m) and `th` (wind FROM-direction at 10 m). July-September spans peak summer into early autumn, allowing heat persistence, cooling and rain timing to be compared in one contiguous interval. The selected 2023 year includes independently documented Southwest July heat [9], making persistence substantively relevant; it is a case study, not a representative climate year. Uniform eight-date sampling, 13 days apart with both endpoints, gives reproducible seasonal coverage without the uneven gaps possible in a small random sample. It cannot ensure capture of short extremes; all 92 days support monthly/event inferences.

**Weather preparation.** Decode NetCDF packing/masks before converting source Kelvin to Celsius; supplied caches are already Celsius. Read every sixth grid cell (subsampling, not averaging), align coordinates/dates and retain the same 13,416 cells valid for all variables on all days. Cosine-latitude weights approximate area. Rain stays mm/day, speed m/s and direction degrees FROM north; quiver components point toward flow. The audit records hashes, missing counts, cohorts and sampled-to-daily checks.

### Tools, interaction and evidence

NetworkX [3] computes three layouts; Gephi [5] is the assignment-permitted alternative and is not used here. D3 [4] provides the threshold slider, layout selection, region/isolate node filters, PCP interactions and treemap zoom/hierarchy/partition controls. These are the required working node-link interactions, not merely static layout images. Report diagrams are chart exports; complete uncropped browser captures with controls are linked through the [UI evidence gallery](https://aithal007.github.io/DV_assignment2/interactions.html). Use the dashboard or `python run_visualizations.py`; the README gives full reproduction commands.

## Country relationships and paths

We establish how links are constructed, compare country histories and inspect relationships hidden inside a community.

### Figure 1. Complete pair similarities, threshold selection and three layouts.

![Figure 1](output/network_revision/network_threshold_layouts.png)

**Question.** How can a dense complete similarity network be filtered transparently before comparing layouts?

**Encoding.** The histogram counts all unique country pairs. The second panel sweeps percentile cutoffs from P80 to P99 and counts countries in the largest connected component and countries with no retained edge. The vertical lines mark P95. The lower panels draw the same 797 retained edges with Spring, Spectral and Circular positions; India and its twelve links are highlighted.

**Why this chart.** The full similarity distribution makes the filtering decision visible instead of silently imposing nearest neighbors. Three layouts then test representation effects on one fixed threshold graph. A shared threshold treats every country pair by the same rule.

**What it shows.** Following Prof. Jaya Sreevalsan Nair's guidance, we inspect every pair score before filtering. The histogram describes the complete 15,931-pair universe; panel B shows how the cutoff changes connectedness. This makes the filtering decision inspectable.

Our team selects P95 as an exploratory sparse default: the 95th percentile of all pair scores is 0.569763. Scores at or above it retain 797 pairs, approximately the strongest 5%. P95 is neither similarity 0.95, a confidence level nor a percentage of connected countries. The professor did not prescribe this percentile.

All three layouts preserve the 797 edges and India's twelve neighbors. Spring/Spectral position the 167-country connected core and pack the twelve degree-zero countries into a boxed row. Those dots are measured nodes, not a dotted baseline, missing data or a plotting error. They have scores to every other country and may gain links below P95. Circular distributes all 179 countries around its circumference.

P90 retains 1,594 edges and 5 isolates; P92.5 retains 1,195 and 9; P95 retains 797 and 12; P97.5 retains 399 and 22. Stricter filtering removes weaker pairs but can fragment the core. Keeping every country connected requires 11,526 edges. P95 balances this display trade-off without claiming a unique optimum.

The professor mentioned perturbation as one possible selector. Our 30 seeded trials test robustness after choosing P95: Gaussian noise with SD 0.02 in standardized coordinates gives edge Jaccard 0.905-0.941 (mean 0.922). This is neither calibrated measurement error nor a specified published selector. Scaling/feature changes give overlaps 0.801 (median/IQR), 0.460 (ranks) and 0.338-0.512 (one feature omitted). The online method review supplies tables, the continuous matrix and sources. Stable drawings or small-noise checks cannot establish natural country groups.

**Takeaway.** Filtering makes the complete pair network readable, but also changes connectedness. P95 keeps 797 edges and 12 isolates; the three layouts preserve those relationships. Infer similarity from scores and edges, while treating layout proximity and isolated placement as display choices.

[View live demonstration](https://aithal007.github.io/DV_assignment2/web/network.html) | [Full UI screenshot](https://aithal007.github.io/DV_assignment2/interactions.html#network)


### Figure 2. Different country paths to higher internet use.

![Figure 2](output/internet_review_20261024/adoption_broadband_paths.png)

**Question.** Can internet use rise without a similar rise in fixed broadband?

**Encoding.** Each panel follows one country from 2010 to 2020. Open dots mark 2010 and dark dots mark 2020. Small dots show the intervening years. All panels use the same axes.

**Why this chart.** The network compares countries in one year. Small multiples add the history it leaves out. Each country gets its own panel, so its annual path can be followed without crossing five other paths. Shared axes make the size and direction of the changes comparable across countries.

**What it shows.** The six panels do not follow one shared adoption-broadband path. South Africa gains 48.1 percentage points in internet use with only 0.7 additional fixed-broadband subscriptions per 100 people, whereas China gains 35.8 points with 24.6 additional subscriptions. India similarly gains 35.9 points with a broadband increase of 0.8. The vertical separation of their start/end markers and different horizontal displacements are the visible evidence.

This answers the history part of the main question: an endpoint or even a similar adoption gain cannot identify the associated infrastructure trajectory. Germany's smaller adoption gain also begins from an already high 82% level, so raw gains need starting-level context. These six stated examples illustrate heterogeneity; they do not establish whether mobile access, investment or another mechanism caused it.

**Takeaway.** Similar adoption progress can accompany different infrastructure histories. The contrasting country paths show that a 2020 endpoint cannot establish how a country reached it; annual paired observations are needed to distinguish those histories.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig2)


### Figure 3. NodeTrix: links and gaps after threshold filtering.

![Figure 3](output/network_revision/nodetrix_threshold_detail.png)

**Question.** Which individual relationships are hidden by the grouped threshold graph?

**Encoding.** The overview replaces each non-singleton modularity group with an adjacency matrix and retains cross-group lines. The right view enlarges group 5, with 15 countries. Teal means similarity meets the global threshold; white means it does not. Gray diagonal self-pairs are excluded. Row labels show within-group degree.

**Why this chart.** Matrix cells make exact retained pairs and gaps checkable without relying on crowded lines. The detail group is selected reproducibly as the smallest group with at least five countries that is not a clique. Isolates are explicitly reported rather than silently dropped.

**What it shows.** The overview has 699 links within six non-singleton modularity communities and 98 between them. Those communities subdivide one 167-country connected component; the twelve isolates are separately shown. The enlarged 15-country community contains 93 of 105 possible pairs. Its uneven rows and white gaps show that members are not interchangeable [8].

Afghanistan meets the cutoff with all 14 other members, whereas Angola meets it with seven. This is evidence about the pattern of pair similarities, not a ranking of development or internet quality. A common group label therefore conceals different relationships. White cells are measured similarities below P95, not absent observations or physical disconnections. Lowering the cutoff may fill them and alter the grouping; the inference applies to the declared metric and threshold.

**Takeaway.** A community label hides unequal relationships among its members. The enlarged matrix contains 93 of 105 possible links, with uneven row degrees and real gaps. Inspect those pairs before treating a network community as one uniform telecom profile.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig3)


## Profiles, changes and hierarchies

We connect paired changes and endpoint profiles, directly test almost equal adoption, then compare associations and user-count hierarchies.

### Figure 4. Similar internet gains, different infrastructure changes.

![Figure 4](output/pcp_changes/pcp_changes.png)

**Question.** Do countries with similar gains in internet use also have similar changes in their telecom indicators?

**Encoding.** Each line connects one country's four changes from 2015 to 2020. At every axis, change is calculated as the 2020 value minus its 2015 value. Internet use changes in percentage points; the other axes show changes in subscriptions per 100 people. All 175 matched countries remain visible. Blue highlights the 39 countries that gained 20-30 percentage points in internet use; gray retains the other 136. Three selected examples are named and colored separately. The dashed horizontal line aligns zero on all four axes: above it means an increase and below it a decrease. Each axis has its own stated range.

**Why this chart.** The annual paths in Figure 2 compare internet use and broadband for six examples. This parallel-coordinate view connects all four changes for the full matched sample, so one country can be followed across several measures. Brushing a common range of internet gains asks what else changed among countries making broadly similar progress. Thin background lines retain the full sample, while three named records make the selected pattern easier to trace. The browser supports brushing, axis reordering, hover values and a straight-versus-gently-bundled comparison.

**What it shows.** Brushing adoption gains of 20-30 percentage points selects 39 of the same 175 matched countries. Their selected lines still span broadband changes from about -0.3 to +16.6, landlines from -14.8 to +7.1 and mobile from -80.2 to +34.5 subscriptions per 100 people. The spread across the remaining axes is the evidence that one adoption-gain band does not identify a common infrastructure transition.

Georgia and Brunei both gain about 25 adoption points and around eight broadband subscriptions per 100. Yet Georgia's landline/mobile changes are -14.8/-12.0, while Brunei's are +5.2/+10.2. Their lines cross the common zero reference in different directions. Paired four-measure records expose that contrast; a summary gain cannot. The 20-30 band is an analyst-defined comparison, not a discovered country class. Axis intersections remain measured values under bundling [10]; five-year differences omit annual timing and do not establish which change caused adoption growth.

**Takeaway.** Similar internet-use gains conceal different combinations of infrastructure change. Even the selected 20-30-point gain group contains opposing landline and mobile movements. Follow each country across all four change axes before assigning one explanation to its progress.

[View live demonstration](https://aithal007.github.io/DV_assignment2/output/pcp_changes/index.html) | [Full UI screenshot](https://aithal007.github.io/DV_assignment2/interactions.html#changes)


### Figure 5. Gentle bundles reveal different country profiles.

![Figure 5](output/internet_revision/pcp_gentle_bundles.png)

**Question.** Do countries with high internet use share the same infrastructure profile?

**Encoding.** Each curve is one of the same 175 countries in 2020. The four vertical axes retain their original units and full matched-country ranges. Orange means below 40% internet use, blue means 40-below-70%, and green means at least 70%. Within each chosen band, curves bend gently toward the average profile between neighboring axes. The 35% setting preserves every measured axis intersection and keeps each bend between its two endpoint values. These bands are chosen comparison groups, not discovered country types.

**Why this chart.** Parallel coordinates keep four measurements connected for each country. Thin curves and three consistent colors make the full set easier to follow without replacing records with filled ribbons. Figure 4 compares five-year changes; this figure compares the country profiles at the 2020 endpoint. The two PCPs therefore ask different questions using the same matched countries. The browser lets the reader compare straight and bundled paths, brush ranges, reorder axes and inspect country values.

**What it shows.** The high-adoption curves fan out strongly on fixed broadband. Kuwait has about 99.1% internet use with 1.7 broadband subscriptions per 100 people; Kyrgyzstan has 72.0% with 4.3. Mobile values also overlap across the three adoption bands instead of separating them cleanly. These are visible exceptions to the idea that one headline adoption category has one infrastructure profile.

Read values where each curve meets an axis. Gentle bundling uses the declared adoption bands to help trace records [10], while the joins between axes are drawing aids. This plot addresses endpoint composition; the preceding change plot addresses transition. Together they distinguish a similar present state from a similar history. The data do not measure all alternative access technologies or identify a causal route to connectivity.

**Takeaway.** High adoption describes several infrastructure profiles rather than one common model. Overlapping mobile values and widely differing broadband values within the same adoption band show why the headline rate must be read alongside the other indicators.

[View live demonstration](https://aithal007.github.io/DV_assignment2/web/index.html) | [Full UI screenshot](https://aithal007.github.io/DV_assignment2/interactions.html#pcp)


### Figure 6. Similar adoption can hide different infrastructure.

![Figure 6](output/additional_evidence/similar_adoption_infrastructure.png)

**Question.** How much can infrastructure differ when internet-use rates almost match?

**Encoding.** Panel A counts pairs within one percentage point in internet use. Panel B shows three pairs selected by minimum, middle-ranked and maximum infrastructure distance. Labels give absolute subscription gaps per 100 people; colour gives standardized gaps.

**Why this chart.** This links an almost equal headline rate to the infrastructure detail it conceals. The histogram retains all eligible pairs, while the examples make the gaps tangible.

**What it shows.** Among 454 country pairs whose adoption rates differ by at most one percentage point, only 71 (15.6%) meet the full-profile P95 cutoff. The remaining 383 nearly match on the headline percentage but not on the combined definition. The histogram retains all eligible pairs rather than only memorable cases.

The displayed examples are selected by minimum, middle-ranked and maximum infrastructure distance. Bhutan/Turkey differ by 0.82 adoption points but 19.0 broadband subscriptions per 100; Kuwait/Monaco show a much larger multi-indicator contrast despite a 0.54-point adoption gap. Cell labels show raw gaps and colors standardized gaps, keeping size and relative unusualness distinct. This directly answers the profiles subquestion. Pairs share countries and the selection is illustrative, so the counts do not form an independent sample or establish significance.

**Takeaway.** Almost equal adoption rates can conceal substantially different infrastructure. Only 71 of 454 eligible pairs meet the full-profile cutoff. The headline percentage therefore cannot substitute for a country profile, even when two values nearly match.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig6)


### Figure 7. Four telecom measures: associations and exceptions.

![Figure 7](images/quality/telecom_scatterplot_matrix.png)

**Question.** What does the complete set of pairwise relationships reveal?

**Encoding.** The four variables occupy the same row and column order: internet use, landlines, fixed broadband and mobile. Diagonal cells are country-count histograms. Below the diagonal, each dot is one country, with the column variable on the horizontal axis and the row variable on the vertical axis. Color shows region. Above the diagonal, the matching pair has its Spearman rank-correlation value. All cells use the same 175 countries in 2020.

**Why this chart.** The two adoption scatterplots in A1 already compared broadband and mobile. Restoring the full scatterplot matrix adds the four other pairs, the individual distributions and a common sample. Each relationship can be checked in its own scatter cell rather than inferred from a single correlation number. This also gives a position-based check on the four-variable parallel-coordinate profiles.

**What it shows.** The lower scatter cells show tighter upward ordering for broadband versus adoption (Spearman 0.83) than for mobile versus adoption (0.53). Landlines and broadband have the strongest displayed pairwise rank association, about 0.87. The clouds and outlying countries qualify those coefficients: high adoption still occurs at low fixed-broadband values, and mobile subscriptions overlap widely.

All cells use the same 175 countries, so different sample membership does not explain the contrast. Diagonal distributions also show why a subscription count can exceed 100 per 100 people without being an adoption percentage. This tests the profiles seen in parallel coordinates using ordinary position axes. It supports an association between 2020 country levels, while leaving causal explanations and country-specific change unresolved.

**Takeaway.** A correlation summarizes an association while hiding its exceptions and shape. The scatter cells show stronger adoption association with broadband than mobile, yet substantial variation remains. These endpoint associations do not identify the drivers of country progress.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig7)


### Figure 8. Country levels and country gains tell different stories.

![Figure 8](output/proposals_20261026/recommended_fig7_association_audit.png)

**Question.** Does a strong relationship between country levels also hold for gains within the same countries?

**Encoding.** The left panel compares Spearman rank correlations with internet use for fixed broadband, landlines and mobile. Blue dots use 2020 country levels; orange dots use each country's 2020-minus-2015 gains. Each gray line joins the two correlations for one measure. The right panel shows the actual broadband and adoption gains, with one dot per country. Both comparisons use the same 175 complete country pairs. Correlation describes how consistently two variables increase together across countries.

**Why this chart.** Figure 7 shows relationships between country levels. Repeating the comparison after calculating each country's gain tests whether that snapshot relationship carries over to progress. The paired-dot chart compares all three measures without repeating six scatterplots. The broadband-gain scatterplot keeps the underlying observations visible, so the coefficients can be checked against the shape of the data.

**What it shows.** The strongest endpoint association weakens sharply when each country is paired across time: broadband-adoption rank correlation falls from about 0.83 in 2020 levels to 0.054 in 2015-2020 gains. The gain scatter at right lacks the clear upward ordering implied by the endpoint coefficient. Landline and mobile associations likewise weaken, from about 0.79 to 0.29 and 0.53 to 0.07.

Because the same 175 countries supply both calculations, this is a change of analytical question rather than a sample-composition effect. Countries that already have more infrastructure differ from countries adding more within the interval. The figure therefore blocks a tempting inference from the snapshot: the endpoint association cannot explain who progressed faster. Weak gain correlation is not proof that infrastructure is irrelevant; timing, omitted factors and measurement changes remain unresolved.

**Takeaway.** Countries that have more broadband tend to have higher adoption, but countries gaining more broadband do not show the same ordering of adoption gains. The fall from 0.83 to 0.05 exposes why a cross-country snapshot cannot substitute for paired change.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig8)


### Figure 9. Internet users grouped by region.

![Figure 9](output/internet_revision/treemap_root_region.png)

**Question.** Where are the included internet users concentrated?

**Encoding.** Large rectangles are regions; smaller country rectangles sit inside them. Area shows the number of internet users. Country color shows the percentage of people online. Group headers show each region’s share of the included total.

**Why this chart.** A country with a high internet-use rate can still have fewer users than a large country with a lower rate. The nested treemap separates these two quantities: area shows the count and color shows the rate. Region-first grouping answers where the included users live, while keeping countries inside their regions.

**What it shows.** Asia occupies about 56.9% of the included internet-user total, compared with 14.0% in Europe. China and India are large country rectangles because user counts are large; their colors can differ because adoption percentages measure a separate quantity. The total denominator is the same 184-country, 4,521,767,530-user sample, not an estimate covering every missing country.

This answers where included users are concentrated while showing why a large user population does not imply near-universal access. Zooming into Asia reveals country counts and rates hidden by its regional area. The live spatial-partition control also compares squarified rectangles with slice-and-dice strips; values and hierarchy remain fixed while geometry changes. Compare encoded values, not a country's apparent visual prominence alone.

**Takeaway.** A large internet-user count can coexist with incomplete population access. Asia holds 56.9% of included users, but rectangle size alone says nothing about adoption percentage. Read count area and country color together to distinguish scale from access.

[View live demonstration](https://aithal007.github.io/DV_assignment2/web/treemap.html) | [Full UI screenshot](https://aithal007.github.io/DV_assignment2/interactions.html#treemap)


### Figure 10. The same users grouped by adoption band.

![Figure 10](output/internet_revision/treemap_root_adoption.png)

**Question.** Does changing the hierarchy change the comparison?

**Encoding.** This treemap uses the same 184 countries and total as Figure 9. It first groups countries by internet-use band, then by region. Area still shows user count and country color still shows internet use.

**Why this chart.** The first treemap makes regional size prominent. Reversing the hierarchy asks which adoption levels contain those users. Keeping the country data, total area and color scale fixed isolates the effect of grouping. The two trees therefore answer different questions with the same records.

**What it shows.** Moving adoption band to the top exposes a different composition of the same user total: the 50-below-75% band contains about 39.7% of included users, slightly more than the 38.1% in the 75-100% band. Thus a large share of online people live in countries where a substantial part of the population remains offline.

No country values change when the hierarchy switches. The difference from the region-first view comes from which grouping is made visually prominent. This is evidence that aggregation design changes the question a summary answers. A rectangle represents online users, not offline population, so the plot does not directly count the access shortfall. The live partitioning comparison changes shapes only; zooming changes the displayed denominator, which is stated in the status and breadcrumb.

**Takeaway.** The distribution of users across adoption levels becomes visible when the hierarchy changes. The 50-below-75% band contains 39.7% of included users, so many online users live where substantial access gaps remain. Grouping changes the question answered by the same values.

[View live demonstration](https://aithal007.github.io/DV_assignment2/web/treemap.html) | [Full UI screenshot](https://aithal007.github.io/DV_assignment2/interactions.html#treemap)


## Progress, inequality and timing

Fixed country identities distinguish progress from catch-up; distributions and trajectories retain the differences behind regional summaries.

### Figure 11. Did countries that started behind catch up?

![Figure 11](output/proposals_20261026/recommended_fig10_fixed_cohorts.png)

**Question.** Did the countries with the lowest initial internet use catch up as overall adoption rose?

**Encoding.** The 159 countries with complete 2000-2020 records are ranked once by their internet use in 2000 and divided into three groups of 53. Orange is the lowest starting third, blue the middle third and purple the highest third. Membership stays fixed in every year. The left panel follows each group's yearly median. The right panel shows every country's 2020 value; the thick bar spans the middle half and the white circle marks the median. Small vertical offsets separate overlapping country dots and have no data meaning.

**Why this chart.** Yearly distributions can improve even when the countries that started behind remain behind. Keeping the same initial groups follows those countries instead of replacing them with whichever countries occupy a percentile later. The median paths show the group contrast over time; the individual dots prevent a group summary from hiding exceptions. This complements the later ridgelines, which compare overall and regional distributions.

**What it shows.** All three cohorts move upward, but the lowest-starting group reaches a 2020 median of 36.1% while the highest reaches 89.9%. Their absolute median gap widens from 16.2 to 53.8 percentage points. Membership is assigned once from 2000 adoption, so the widening cannot be attributed to countries moving between cohort labels.

The endpoint dots overlap: some low-start countries finish above members of a higher-start group. Group-level persistence therefore coexists with individual exceptions. This separates broad progress from absolute catch-up and answers the inequality subquestion. Country rates have equal weight; these medians are not population-weighted access estimates. Four- and five-cohort checks preserve the widening endpoint pattern, but no claim is made that every relative inequality measure rises.

**Takeaway.** Broad progress does not imply absolute catch-up. All fixed starting groups improve, yet their low-to-high median gap widens from 16.2 to 53.8 points. Fixed membership establishes that this contrast is not created by moving countries between groups.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig11)


### Figure 12. Country differences inside each region.

![Figure 12](output/simple_revision/within_regions.png)

**Question.** How much country variation does a regional average leave hidden?

**Encoding.** Each dot shows one country’s 2020 internet-use rate. A dark tick marks the regional average. The bar on the right divides the total spread into differences within regions and differences between regional averages.

**Why this chart.** A regional mean is one mark, even when its countries are far apart. Showing every country beside that mark reveals the spread directly. The variance split then gives a single numerical answer to how much of the total country variation sits inside regions. This extends the regional comparison without repeating A1's absolute-gap and ratio plots.

**What it shows.** The country dots spread widely around several regional averages. Variance decomposition assigns about 47% of measured adoption variation to differences within regions and 53% to differences between their means. This calculation uses the 158 region-classified members of the balanced country panel; the unclassified member is not silently assigned to a region.

The bars quantify what the dots make visible: a regional mean leaves nearly half of this measured country-level variation unresolved. Region therefore provides context without identifying the situation of each member. The decomposition weights regional mean contributions by country count and treats countries equally. It neither attributes 53% of outcomes causally to region nor describes the share of people who have access. This is why regional progress must be interpreted alongside individual values.

**Takeaway.** Regional averages leave substantial country inequality unresolved. The 47% within-region variance share and the individual dots show that a regional label cannot stand in for its members. Preserve country-level spread when interpreting an improving regional summary.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig12)


### Figure 13. Regional change and individual country gains.

![Figure 13](output/final_research/regional_endpoints_gains.png)

**Question.** Does the change in a regional median describe a typical country’s gain?

**Encoding.** The left panel shows 2015 and 2020 regional medians. The right panel shows each country’s own gain. A thick line marks the middle half of gains; the open circle is the median gain. The black tick repeats the shift in the regional median.

**Why this chart.** Subtracting two regional medians sounds like the typical country's gain, but the middle country can change between years. The paired endpoint view shows the regional summaries, and the gain view calculates change for each country first. Putting the two calculations together exposes the difference instead of asking the reader to infer it from separate tables.

**What it shows.** Asia's endpoint median shifts by 26.55 adoption points, but the median of its individual country gains is 19.75. South America reverses the relative comparison: its endpoint-median shift is 16.54 while its median country gain is 21.76. The visible separation between the black shift tick and open gain marker exposes the difference between these calculations.

The same countries are matched across 2015/2020. Subtracting two separately computed medians need not track one country's experience because the countries defining the middle may change. The gain dots additionally preserve Asia's wide range, about -0.84 to +49.94 points. This answers what a regional trend hides: both the distribution of progress and the distinction between summary movement and a typical paired change. Neither operation identifies causes.

**Takeaway.** A shift in a regional median is a different quantity from a typical country gain. Asia gives 26.55 versus 19.75 points. Calculate paired changes first when the question concerns individual progress; summarizing first can change the answer.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig13)


### Figure 14. Country horizon plots.

![Figure 14](images/horizon_countries.png)

**Question.** Which countries reach majority internet use early or late?

**Encoding.** Each row follows one selected country from 2000 to 2020. Red means below 50% internet use and blue means above it. Darker bands mean a larger distance from 50%. Right labels show the 2020 value and first observed 50% year.

**Why this chart.** Many full-size time-series panels would take more space. Horizon rows fold values around a meaningful 50% reference, keeping all 21 years in a compact display. Sorting by first crossing makes early and late arrivals easy to scan. The numerical endpoint labels help read values that are harder to recover from folded bands.

**What it shows.** The ordered rows show different first observed majority-use years: Singapore reaches 50% in 2003, Ireland in 2006, China in 2015, Peru in 2017 and Namibia in 2020; Tanzania and Micronesia have no observed crossing by the endpoint. Those differences remain visible even where eventual adoption rates might look comparable.

Red/blue encodes position below/above the fixed 50% reference; darkness distinguishes 25-point folded bands. A red row can still be rising rapidly. Annual sampling identifies the first recorded crossing year, not the precise date within that year. Two countries per classified region are selected by a stated endpoint-quartile rule. These examples recover timing hidden by a snapshot without pretending to represent every country or to measure growth directly from hue.

**Takeaway.** The same final adoption level can hide different arrival times. Horizon rows preserve early, late and absent crossings of the 50% milestone. Their colors describe position relative to that reference; they do not by themselves indicate growth or decline.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig14)


### Figure 15. Regional median horizon plots.

![Figure 15](images/horizon_regions.png)

**Question.** Do regional medians reach majority use at similar times?

**Encoding.** Each row shows the yearly median internet-use rate for one region. The 50% reference and band colors match Figure 14. The same countries are used in every year.

**Why this chart.** Repeating the horizon design for regional medians tests how much the story changes after aggregation. The same reference and colors allow a direct comparison with Figure 14. One compact row per region makes broad timing clear, while the preceding country plots show what each regional row leaves out.

**What it shows.** Europe's regional median crosses 50% earlier and ends at 86.86%, while Africa ends at 31.89%. The shared reference makes both timing and the roughly 55-point endpoint difference visible in a small vertical space. This is stronger evidence of different regional histories than a single pooled final value.

Each row is nevertheless one median per year. It cannot identify the country crossing times or spreads shown in the preceding views. The same classified balanced-country membership is retained across all years, preventing changing coverage from creating the apparent trajectories. Read the regional horizon as an organizing summary, then use the country horizons and within-region dots to establish how far that summary can be generalized.

**Takeaway.** Regional trajectories make broad timing differences clear while compressing member histories. The large Europe-Africa median gap does not describe every country in either region. Read these summaries with country horizons and within-region spread before generalizing.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig15)


### Figure 16. How the country distribution changed.

![Figure 16](images/ridgeline_years.png)

**Question.** Did all countries move toward similar internet use?

**Encoding.** Each ridge shows the distribution of internet use across the same 159 countries in one year. All ridges share the 0–100% scale. Small ticks show countries, and right labels give the median.

**Why this chart.** A rising median could mean that countries moved together or that some moved much faster than others. Ridgelines retain the whole distribution at several dates. A common horizontal scale shows the shift, while country ticks help check the smooth shapes against the actual observations.

**What it shows.** The ridges shift right as the country median rises from 2.2% in 2000 to 71.4% in 2020. Yet the 2020 middle half still spans about 37.5 percentage points. The horizontal width and country ticks show that broad progress has not produced a narrow common adoption level.

All five distributions use the same 159 countries and the same 0-100% axis, so the comparison is not driven by membership changes. Ridge heights are independently normalized; a taller peak does not mean more countries. Smoothing estimates shape between observations, whereas the ticks retain actual values. This supports the main question directly: a much larger median can coexist with substantial remaining dispersion. The fixed-cohort plot is needed for the separate question of who caught up.

**Takeaway.** A rising country median does not mean adoption has become uniform. Despite the rise from 2.2% to 71.4%, the 2020 middle half spans 37.5 points. Distribution width qualifies the progress visible in the central value.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig16)


### Figure 17. How distributions changed within regions.

![Figure 17](images/ridgeline_regions.png)

**Question.** Which regional differences are hidden by the whole-panel distribution?

**Encoding.** Each panel repeats the ridgeline view within one region for 2000, 2005, 2010, 2015 and 2020. All panels use the same internet-use scale. Country ticks and median labels help check the smooth curves.

**Why this chart.** The global distribution mixes countries from different regions. Small multiples repeat the ridgeline comparison within each region, so a broad global shape can be traced to different regional paths. Shared horizontal scales keep low and high adoption in the same position across all panels.

**What it shows.** Europe's ridges move toward high adoption earlier, while later African ridges still occupy low and middle values. Asia's distributions remain broad during its movement to the right. These distinct positions and widths explain how the global progress pattern combines different regional histories rather than one common shift.

The shared horizontal scale and unchanged country membership support temporal comparison inside each region. The small Oceania sample contains only eight included countries, making its individual ticks more reliable evidence than a smooth bump alone. Peak height is normalized within each ridge and should not be compared as a population count. These panels recover both between-region timing and internal spread that a single regional median horizon compresses.

**Takeaway.** Global progress combines different regional histories and changing internal spreads. A single global ridge therefore cannot represent one shared journey. Country marks are essential when small groups make a smooth density shape look more certain than the observations support.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig17)


## Scalar fields and visual encodings

Controlled experiments hold measured weather fields fixed while varying palette, temporal normalization and contour representation.

### Figure 18. How color choices change the view.

![Figure 18](images/scivis/scivis_color_experiments.png)

**Question.** What changes when the same field uses a different color mapping?

**Encoding.** The panels keep the weather field and date fixed. All four palettes are sequential colormaps: their colors progress from lower to higher values. Temperature uses continuous viridis and cividis split into 5°C bands. Rain uses Blues with a linear scale and magma with a logarithmic scale. Palette choice and scale normalization are separate choices. Read each color bar before comparing the maps.

**Why this chart.** A palette or scale can make a feature stand out even when the measurements do not change. These panels hold the field fixed and change only its mapping to color. Sequential colormaps suit these ordered magnitudes because no middle value needs special emphasis. Temperature tests palette choice; rainfall tests how the scale reveals smaller values alongside heavy rain.

**What it shows.** The temperature panels hold one field fixed while continuous viridis and 5-degree cividis bands emphasize different levels of detail. The rainfall panels also hold values fixed: linear Blues allocates most contrast to large amounts, while logarithmic magma separates small positive amounts that appear almost uniform under the linear mapping. Zero rain is excluded from the logarithm rather than treated as missing source data.

Absolute temperature/rain fields have ordered magnitudes, so sequential palettes are appropriate. Figure 22 instead subtracts July from September: zero separates cooling from warming, so a diverging RdBu_r palette with symmetric bounds is appropriate [7]. Palette and normalization are separate choices. The experimental contrast is a change in visual emphasis, not additional rainfall or evidence of a stronger event.

**Takeaway.** Color mapping controls which measured differences receive visual emphasis. Linear rain color prioritizes absolute amounts, while logarithmic color separates small positive amounts. Interpret a feature through its legend and normalization before calling it a stronger weather event.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig18)


### Figure 19. Fixed and daily color scales.

![Figure 19](images/scivis/scivis_global_local.png)

**Question.** Can the same color mean a different temperature?

**Encoding.** The left column uses one temperature range across the eight sampled dates. The right column rescales each date to its own minimum and maximum. Both columns show the same fields.

**Why this chart.** An animation can look equally warm on every date if each frame is rescaled separately. The two columns test this with identical daily fields. One scale preserves comparisons between dates; the other spends its full color range on the variation within each date. Neither choice can be understood without checking the color bars.

**What it shows.** The paired columns map identical daily fields using two parameter rules. Global normalization uses u=(T-min)/(max-min) with bounds fixed over the eight frames; daily normalization recomputes those bounds for each date. Consequently, the same warm hue may mark different temperatures in the daily column even when both frames use their full palette.

The fixed eight-date range is -1.85 to 49.65 C. It supports between-frame comparison without claiming to cover extremes on every unsampled day. Daily scaling is useful for within-date contrasts but cannot support reading repeated color as repeated absolute temperature. The GIFs make this issue explicit over time. This explains a visual inference failure that can occur before any statistical aggregation: inconsistent encodings can conceal the change the animation is meant to reveal.

**Takeaway.** Consistent colors are necessary for comparing temperature across dates. Daily rescaling can assign the same bright color to different temperatures, concealing absolute change. Use fixed bounds for temporal comparison and daily bounds for within-date contrast.

[View fixed-scale animation](https://aithal007.github.io/DV_assignment2/images/scivis/scivis_global.gif) | [View daily-scale animation](https://aithal007.github.io/DV_assignment2/images/scivis/scivis_local.gif)


### Figure 20. Contour intervals and filled contours.

![Figure 20](output/internet_revision/contours_worked.png)

**Question.** How much boundary detail does the contour interval show?

**Encoding.** The same August 22 temperature field is drawn with 5°C and 10°C intervals, using lines and filled bands. Levels and color bars show the thresholds used.

**Why this chart.** Contours turn a continuous field into visible boundaries. Using the same date with two intervals separates the effect of boundary spacing from actual weather differences. Lines make threshold crossings explicit, while filled bands make broad areas easier to compare. The four panels test both choices on the same grid.

**What it shows.** The four panels use the same August 22 temperature grid. Five-degree levels produce more boundaries than ten-degree levels; filled bands organize broad areas, while labeled lines identify individual thresholds. The worked grid cell shows temperatures on both sides of 35 C and the interpolated edge crossings used to draw that boundary.

The regular two-dimensional scalar grid fits ContourPy's serial Marching Squares/sweep method [6]: classify four corner values, interpolate crossings on cell edges, and trace segments between neighboring cells. This local method respects the grid/mask and avoids treating missing cells as measurements. Filled contour polygons expose connected temperature ranges; line contours make precise threshold location easier to inspect. Finer level spacing changes displayed boundaries, not source resolution or certainty about the field between grid points.

**Takeaway.** More contour lines increase display detail without increasing data resolution. Five-degree spacing reveals more threshold crossings; filled bands emphasize broad regions. Select the representation for the reading task and infer boundaries only at the stated levels.

[View contour animation](https://aithal007.github.io/DV_assignment2/images/scivis/scivis_contour.gif)


## Weather across complete months and days

We restore all 92 dates to compare cooling, spatial spread, rainfall concentration, repeated heat and episode timing.

### Figure 21. Monthly temperature maps.

![Figure 21](images/extensions/monthly_tmax_maps.png)

**Question.** How does the average daily maximum temperature change across the three months?

**Encoding.** Each map averages daily maximum temperature over one month. All maps use the same Celsius scale and the same 25°C and 35°C contour levels.

**Why this chart.** After testing color and contours, we use fixed choices to compare complete months. Shared colors let a temperature be recognized across all three maps, and common contour levels give reference boundaries. Using every day avoids choosing one unusually hot or cool date to represent a month.

**What it shows.** The same color and 25/35 C contours make monthly temperatures comparable. Mean daily maximum temperature falls from 31.19 C in July to 26.55 C in September over the weighted common footprint, while southern warm areas remain visible. The maps establish both the broad decline and its nonuniform spatial pattern.

Each month uses every daily maximum, so one unusually hot or cool day is not made its representative. The mapped quantity is an average of daily maxima, not a monthly extreme or an average of hourly temperatures. Monthly averaging still removes short spells and the order of days. The following difference map tests the spatial extent of cooling, and daily/frequency views recover the event information needed to interpret that seasonal summary.

**Takeaway.** The monthly maps establish broad cooling while retaining its spatial pattern. The mean daily maximum falls by 4.64 degrees, but a monthly average cannot count heat episodes or their duration. Daily and frequency views supply those missing dimensions.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig21)


### Figure 22. Monthly change versus two selected dates.

![Figure 22](images/quality/monthly_temperature_change.png)

**Question.** Can two daily snapshots describe a whole month’s change?

**Encoding.** The map subtracts July’s mean daily maximum temperature from September’s. It uses the diverging colormap RdBu_r, with equal negative and positive limits centered on zero. Blue means cooling, red means warming, and the pale center means no change. The curves summarize changes across three longitude bands.

**Why this chart.** Three maps show overall cooling but make small spatial differences difficult to compare. A diverging colormap suits a difference map because zero is a meaningful reference: it separates cooling from warming. Symmetric color limits show the sign and size of change around that neutral center. The cumulative curves show how widespread each change is within longitude bands, rather than reducing each band to one mean.

**What it shows.** September-minus-July monthly means are negative over 99.66% of the weighted study area, with an overall change of -4.64 C. The area-wide cooling claim is therefore supported by the spatial distribution, not only by one negative mean. The sector cumulative curves show how cooling magnitudes vary across longitude bands.

Using September 30 minus July 1 gives the opposite change sign over 18.26% of the area. Those two weather states are poor substitutes for the complete months when the question concerns seasonal change. RdBu_r uses equal positive/negative limits around zero: blue is cooling, red warming and the pale midpoint no change [7]. This encoding makes both direction and size explicit. The result is a three-month weather comparison, not a long-term climate trend.

**Takeaway.** Two endpoint days can misrepresent change across the full interval. Their change sign disagrees with the complete-month comparison over 18.26% of the study area. Use all days when the claim concerns monthly conditions rather than two weather states.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig22)


### Figure 23. Daily temperature and its spatial spread.

![Figure 23](images/extensions/daily_temperature_ribbons.png)

**Question.** What does a daily average hide about different places?

**Encoding.** Each longitude-sector panel retains all 92 days. The solid colored line is the area-weighted spatial median, the dashed dark line the area-weighted mean, and the shaded ribbon the spatial 10th-90th percentiles. All panels use the same Celsius scale.

**Why this chart.** Monthly averages hide both short episodes and differences between places. A daily line restores timing, while the ribbons retain the range of temperatures across locations. Separate longitude panels keep the regional patterns readable without overlaying six shaded bands on one set of axes.

**What it shows.** On July 27 the western sector has a weighted mean maximum temperature of 31.19 C, while its spatial 10th-90th percentile range is 23.75-39.25 C. The central sector mean is 35.36 C with a narrower 31.39-38.35 C range. Thus similar-looking summary trajectories can conceal quite different simultaneous temperature spreads.

In these actual panels, the solid colored line is the spatial median, the dashed dark line is the area-weighted mean, and the shaded ribbon is p10-p90. The same 4,910 western, 4,828 central and 3,678 eastern cells contribute on every date. Temporary peaks and dips remain visible inside each month. Ribbons describe variation across places, not confidence intervals around a mean. Their role in the main question is to recover both daily episodes and the geography compressed by one sector value.

**Takeaway.** A smooth area mean can conceal both daily episodes and simultaneous differences between places. The ribbons recover that spatial spread around the daily mean. Their width describes variation across cells, rather than statistical uncertainty about the mean.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig23)


### Figure 24. Monthly rain totals and five-day bursts.

![Figure 24](output/research_candidates/rainfall_concentration.png)

**Question.** Can similar monthly totals come from different rainfall timing?

**Encoding.** The top row shows monthly rain totals on one scale. The bottom row shows the share of each month’s rain that falls in its wettest five consecutive days. Cells with less than 10 mm monthly rain are masked in the bottom row.

**Why this chart.** A monthly rainfall total cannot distinguish steady rain from a short burst. The second row adds the share falling in the wettest five consecutive days. Keeping total and concentration separate avoids calling a very small rain amount a major event simply because all of it fell at once.

**What it shows.** July and August have close weighted totals, 75.26 and 75.82 mm, but their five-day concentration patterns differ. Among cells receiving at least 10 mm in the month, 43.8% of eligible area in July receives at least half its rain within one five-day window; August reaches 67.5% and September 77.6%. September's lower total, 57.08 mm, therefore coexists with more concentrated timing.

The ratio maps deliberately mask nearly dry cells, where tiny totals can create misleadingly large percentages. Eligible footprint shares differ between months (74.75%, 92.32%, 94.09%), so these conditional percentages must not be treated as measurements of identical subsets. Windows stay inside each month. The result distinguishes amount from arrival pattern; daily gridded rain alone does not establish hourly intensity, runoff or flooding.

**Takeaway.** Monthly rainfall amount cannot identify how rain arrived. Similar July-August totals conceal different five-day concentration, and September has the largest concentration share despite a lower total. Compare amount with timing, using the explicitly eligible area for each month.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig24)


### Figure 25. Where hot days are frequent.

![Figure 25](images/extensions/hot_day_frequency_maps.png)

**Question.** Where do daily maximum temperatures often reach 35°C?

**Encoding.** Each map shows the percentage of days in a month with daily maximum temperature at least 35°C. The three maps share one 0–100% scale.

**Why this chart.** A monthly mean temperature does not count how often a chosen hot threshold was exceeded. Frequency maps use all days and preserve location, making repeated heat distinguishable from one selected hot day. The fixed percentage scale lets July, August and September be compared directly.

**What it shows.** The weighted mean frequency of Tmax >=35 C falls from 22.8% of July days to 8.9% of September days. The spatial colors show where repeated threshold exceedance remains concentrated, providing evidence that is absent from the monthly mean temperature alone.

The denominator is each month's number of days, so 31 versus 30 days does not mechanically create the contrast. A 50% cell crosses the chosen threshold on half its days, but its warm days may be consecutive or scattered. Thus these maps establish repetition and location, while the persistence map/calendar establish sequence and duration. The 35 C threshold is a declared descriptive definition rather than a universal heat-risk criterion; the final sensitivity panel checks how that choice affects the counts.

**Takeaway.** Hot-day frequency reveals repeated heat that a monthly mean or one selected date cannot count. Its decline from July to September measures occurrence, while the maps retain location. Frequency still leaves the ordering of those days unresolved.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig25)


### Figure 26. Daily weather across longitude.

![Figure 26](images/quality/weather_hovmoller.png)

**Question.** When and where do warm and rainy periods occur?

**Encoding.** Time runs vertically and longitude horizontally. The top panel shows an area-weighted fixed-threshold heat summary. The other panels show temperature and rain averaged across latitude, retaining every day.

**Why this chart.** Maps preserve location but require many frames to show all 92 days. A time-longitude diagram keeps every date visible in one view. Averaging across latitude makes room for that time axis, so episodes can be compared by their dates and east-west extent rather than remembered across an animation.

**What it shows.** The 92-day time-longitude panels retain short warm episodes and brief rain periods that monthly maps smooth away. Rain is more localized in both time and longitude, whereas some warm bands extend across larger east-west ranges. Their date alignment permits comparison without remembering separate animation frames.

Each longitude column averages the stated latitude band, so cells from different north-south locations are combined. A diagonal streak is a pattern in these aggregates, not proof of a tracked storm moving through the domain. This trade-off adds continuous timing while sacrificing one spatial dimension. Use the diagram to identify when and over which longitudes an episode occurs, then return to maps for exact spatial interpretation. It complements the daily spatial ribbons rather than replacing their spread information.

**Takeaway.** Retaining every date exposes episodes smoothed away by monthly maps. The time-longitude view locates their timing and east-west extent, but latitude averaging removes north-south detail. Return to maps before interpreting a band as a specific event location or track.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig26)


## Wind direction and magnitude

Quiver maps locate the flow; monthly direction distributions describe how often different winds occur.

### Figure 27. Wind-arrow density and length.

![Figure 27](images/scivis/scivis_quiver_experiments.png)

**Question.** How do sampling and arrow length affect readability?

**Encoding.** The panels show the same western-US wind field with different sampling gaps. The top row scales arrow length by speed; the bottom row uses equal lengths. Color gives speed in both rows. Arrows point toward the flow direction.

**Why this chart.** An arrow map can become unreadable before it becomes informative. Holding the wind field fixed while varying spacing shows how much local detail is traded for legibility. Comparing speed-scaled and equal-length arrows also separates the tasks of reading direction and reading magnitude.

**What it shows.** All six panels use the same western-US field and the required NetCDF variables `vs` (10 m speed) and `th` (10 m source direction). Sampling every 4th, 8th or 12th point of the already subsampled grid progressively reduces arrow overlap. Speed-proportional arrows show direction and magnitude together; equal-length arrows make direction easier to compare, but their length ceases to encode speed.

Source direction is converted to flow-to components, u=-vs*sin(th) and v=-vs*cos(th), with bearing correction for longitude scale and map aspect. The 5 m/s key and shared speed color retain units. Near-calm vectors are omitted because their direction is not informative. These comparisons justify a readable display density; they do not imply finer wind resolution or reveal trajectories, gusts or terrain effects absent from the source [1].

**Takeaway.** Arrow spacing and length determine which wind questions are readable. Sparse sampling clarifies directions while omitting locations; equal lengths emphasize direction and speed-scaled lengths add magnitude. Interpret the vector convention and speed colors with the chosen design.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig27)


### Figure 28. Monthly wind-direction distributions.

![Figure 28](output/lecture_previews/monthly_wind_roses.png)

**Question.** Does one pooled wind summary hide monthly differences?

**Encoding.** Each rose groups a month’s grid-cell days by wind source direction. Stacked colors show speed ranges. The same radial scale gives the percentage of each month’s weighted grid-cell days.

**Why this chart.** Quiver maps show where wind points, but not how often each source direction occurs across a month. Wind roses collect those directions into sectors and divide each sector by speed. Separate monthly panels and a common radial scale reveal changes that one pooled seasonal rose would hide.

**What it shows.** The largest source-direction sector is southwest in July, then south in August and September. Because every rose has the same 14% radial maximum, that directional-frequency change can be compared directly. Stacked 0-2, 2-4, 4-6, 6-8 and >=8 m/s bands show which speed classes contribute to each direction.

This is a distribution over weighted grid-cell days, rather than a mean vector or a count of storm tracks. The source-direction convention is opposite to the flow-pointing quiver arrows; the apparent difference is intentional. A pooled seasonal rose could hide the monthly redistribution, while each monthly rose still loses location. Use it for how often particular winds occur and the quiver map for where directions are observed.

**Takeaway.** Wind direction and strength distributions change within the three-month interval. Monthly roses expose a source-direction shift that a pooled seasonal summary could hide. Their common radial scale supports frequency comparison, while maps remain necessary to locate the winds.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig28)


## Coincidence, frequency and persistence

Aligned fields identify joint conditions, full-period counts establish occurrence, and the daily calendar explains why equal frequencies can have unequal run lengths.

### Figure 29. Temperature, rain and wind on the same dates.

![Figure 29](images/quality/weather_four_fields.png)

**Question.** Can separate weather summaries hide where conditions occur together?

**Encoding.** Both maps combine temperature color, rain contours and wind arrows. They show July 27 and September 30 on shared scales so the fields can be read at the same locations.

**Why this chart.** Separate temperature, rainfall and wind maps make it hard to check whether conditions occur at the same locations. The overlay aligns the three fields on one map. Two contrasting dates show what that alignment adds, while common visual scales keep the comparison meaningful.

**What it shows.** The objectively selected dates contrast hot-dry area coverage of 34.56% on July 27 and 1.75% on September 30. Common temperature colors, 5/20/50 mm rain contours and the same arrow positions permit spatial comparison. The overlay reveals where the fields coincide; three separate area means would not establish that.

The dates are deliberately contrasting examples, so they do not show how frequent either state is. The next full-period calculation evaluates all cells and dates. Moreover, daily maximum temperature, accumulated rain and daily wind summaries need not occur at the same hour: the overlay establishes cell-day alignment, not instantaneous physical simultaneity. This qualification preserves the spatial inference without turning co-location into an explanation of a weather mechanism.

**Takeaway.** Separate field summaries cannot establish that conditions coincide at the same place. The overlay aligns heat, rain and wind to reveal spatial coincidence on selected dates. Those examples motivate the complete-period overlap calculation rather than establish its frequency.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig29)


### Figure 30. Separate frequencies and shared occurrence.

![Figure 30](output/simple_revision/weather_overlap_simple.png)

**Question.** How often do hot, dry and windy conditions occur together?

**Encoding.** The first three bars count hot, dry and windy grid-cell days separately. The orange bar requires all three conditions in the same grid cell on the same day. All bars use the same weighted percentage scale.

**Why this chart.** With three conditions and a question about their joint occurrence, four bars give a direct answer. The first three establish how common each condition is; the fourth requires all three together. An intersection matrix would add symbols and combinations that are unnecessary for this comparison.

**What it shows.** The separate bars give about 18.06% hot, 76.65% dry and 11.65% windy weighted cell-days. Their intersection is 2.57%, calculated only when all three flags are true at the same cell and date. A very common dry condition therefore does not make the three-condition event equally common.

The bars overlap and must not be added. Multiplying the three marginal percentages would give about 1.61% under an independence assumption, rather than the measured 2.57%; separate frequencies do not recover the joint distribution. This answers the coincidence part of the main question with an explicit joint calculation. It is not a significance test, causal attribution or official hazard index, and neighboring cells/days are not independent samples.

**Takeaway.** Common individual conditions need not produce common joint events. Although dry days occupy 76.65% of weighted cell-days, only 2.57% meet all three conditions together. Compute overlap at the same cell and date; separate marginal percentages cannot recover it.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig30)


### Figure 31. How often conditions occur and how long they last.

![Figure 31](images/quality/compound_frequency_persistence.png)

**Question.** Does the event count describe uninterrupted duration?

**Encoding.** The maps compare hot-dry day frequency and the longest hot-dry run at each cell. The daily curve shows area coverage. The final panel repeats the calculation under alternative thresholds.

**Why this chart.** The shared-condition bars count occurrences but do not show whether they form long uninterrupted spells. Frequency and longest-run maps separate these two ideas. The daily coverage curve restores timing, and the threshold panel checks how the numerical result changes when the event definition changes.

**What it shows.** Hot-dry conditions occupy 16.27% of weighted grid-cell days, while the maximum local uninterrupted run reaches 67 days. These quantities have different denominators: one summarizes area and time together; the other records the longest sequence at one location. The daily coverage curve adds whether a local persistent pattern also affects a large fraction of the footprint at once.

The final panel repeats frequencies at 33, 35 and 37 C with rain cutoffs of 0.1 and 1 mm/day, showing definition sensitivity. Runs touching the first/last observation may continue outside the window. The daily calendar that follows supplies a direct explanation of the frequency-persistence distinction: equal counts can be arranged into very different spells. Report occurrence, duration, coverage and threshold together before characterizing the event pattern.

**Takeaway.** Occurrence, uninterrupted duration and affected area describe different event properties. The 16.27% hot-dry frequency and 67-day local maximum cannot substitute for each other. Combine their maps, daily coverage and threshold sensitivity before characterizing the seasonal pattern.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig31)


### Figure 32. Daily event order separates frequency from persistence.

![Figure 32](output/additional_evidence/daily_event_calendar.png)

**Question.** Can equal event frequencies hide different uninterrupted spells?

**Encoding.** Rows are named grid cells; columns are all 92 days. Orange marks hot-dry conditions and gray their absence. Row labels give event-day counts and longest runs; vertical lines separate months.

**Why this chart.** Maps show where frequency and persistence occur. The calendar reveals the daily ordering that creates their difference.

**What it shows.** Both selected cells have 75 qualifying days out of 92 (81.5%), yet the orange sequences form longest runs of 17 and 67 days. The interrupted first row and long continuous block in the second supply the visual mechanism behind that difference. A count discards the ordering that determines persistence.

Selection searches the common 13,416-cell footprint for the largest run-length contrast among equal positive day counts, with a declared tie rule. These are deliberately diagnostic examples, not typical cells. The maximum 67-day run is included. Fixed coordinates and the complete daily series avoid changing locations or omitting non-event days between panels. Boundary-touching spells may extend beyond the study window. This is the temporal detail needed to interpret the preceding frequency and run-length maps.

**Takeaway.** Equal event counts can hide very different persistence. Two cells each have 75 hot-dry days, yet longest spells of 17 and 67 days. Preserving daily order is necessary to distinguish scattered occurrences from sustained conditions.

[View figure and interpretation online](https://aithal007.github.io/DV_assignment2/figures.html#fig32)


## Discussion

The country evidence answers why an improving summary cannot describe every country. Network layouts rearrange the same relationships; threshold and matrix checks reveal what a grouped picture hides. Figure 6 makes the headline problem explicit: only 71 of 454 pairs with almost equal adoption meet the full-profile cutoff. Paired paths and change PCPs recover different histories behind progress. The level-versus-gain comparison weakens the broadband association from 0.83 to 0.05, so a snapshot relationship cannot explain the ordering of gains. Fixed cohorts retain a widening absolute gap, and 47% of measured adoption variance lies within regions. Country identities and paired observations are necessary for these inferences.

Weather evidence similarly separates level, timing and coincidence. Two selected days disagree in change sign with complete months over 18.26% of the area. Rainfall concentration exposes timing concealed by monthly totals. Hot-dry frequency, longest runs and daily coverage describe different event properties; the calendar shows equal 75-day counts with 17- versus 67-day longest spells. Separate hot, dry and windy frequencies cannot recover their 2.57% joint occurrence.

Together the comparisons recover within-group differences, histories and daily order hidden by aggregation. These descriptive results concern the stated countries, grid and period; they do not establish causes, universal country types or a climate trend.

## Code and supporting files

The repository README documents exact commands for setup, preprocessing, rebuilding supplied figures into the report, regenerating results from raw country extracts and weather caches, running checks, and refreshing the live site. Source CSVs, cache metadata, preprocessing audit, figure exports and editable LaTeX are included. Use the README at the same repository revision as this report; it identifies required software, inputs, outputs and optional downloads.

## Author contributions and task allocation

The following table lists each member’s assigned work. 

| Member | Contribution allocation |
|---|---|
| Parikshith Aithal K V (BT2024249), Person A | Network construction, three layouts, interaction and country trajectory/profile interpretation; scalar color mapping, normalization, global/local scales and GIFs. Figs. 1-3, 6, 18-19, 21-24, 26. Coordination of shared preprocessing, Introduction/Dataset text, and video opening and weather-scale explanation. |
| Sindhoor Ganapathi Hegde (BT2024014), Person B | Both horizon and both ridgeline variations; contour tracing, intervals, fills and contour GIF. Figs. 11-17, 20, 25, 31-32. Inequality, regional gains and persistence interpretation, numerical-check coordination, and corresponding report/video explanations. |
| Varshith M Gowda (BT2024227), Person C | JavaScript bundled parallel coordinates with brushing/reordering and zoomable treemap with two hierarchies; quiver sampling and length encoding. Figs. 4-5, 7-10, 27-30. Browser-demo coordination, relationship/intersection interpretation, Discussion, README/package integration and video conclusion. |

Each member is responsible for the design, implementation, interpretation, report explanation and presentation of their assigned methods. Composite figures reuse other members' outputs with the original task ownership retained.


## Conclusion

Similar internet-use levels can come with different infrastructure histories. Regional progress can leave countries far apart. Similar monthly rain totals can arrive steadily or in a burst, and frequent events need not form long runs.

Each stage adds the detail missing from the previous summary: links and values, annual paths and distributions, daily timing and shared conditions.

## References

1. J. T. Abatzoglou, "Development of gridded surface meteorological data for ecological applications and modelling," International Journal of Climatology, vol. 33, pp. 121-131, 2013. gridMET product and documentation. [Online source](https://www.climatologylab.org/gridmet.html).

2. Our World in Data, "Internet" and underlying ITU/World Bank indicator metadata. The report uses the preserved A1 extracts, not a newly downloaded release. [Online source](https://ourworldindata.org/internet).

3. A. A. Hagberg, D. A. Schult and P. J. Swart, "Exploring network structure, dynamics, and function using NetworkX," Proceedings of the 7th Python in Science Conference, pp. 11-15, 2008. [Online source](https://aric.hagberg.org/papers/hagberg-2008-exploring.pdf).

4. D3 contributors, "What is D3?" and hierarchy/treemap documentation. JavaScript library used for the browser visualizations. [Online source](https://d3js.org/what-is-d3).

5. M. Bastian, S. Heymann and M. Jacomy, "Gephi: An Open Source Software for Exploring and Manipulating Networks," ICWSM, 2009. Assignment-permitted alternative; not used in this implementation. [Online source](https://doi.org/10.1609/icwsm.v3i1.13937).

6. ContourPy contributors, "Algorithm description," serial marching-squares/sweep contour generation and interpolation documentation. [Online source](https://contourpy.readthedocs.io/en/stable/description.html).

7. Matplotlib contributors, "Choosing Colormaps in Matplotlib," sequential and diverging palette guidance. [Online source](https://matplotlib.org/stable/users/explain/colors/colormaps.html).

8. N. Henry, J.-D. Fekete and M. J. McGuffin, "NodeTrix: A Hybrid Visualization of Social Networks," IEEE TVCG, vol. 13, no. 6, pp. 1302-1309, 2007. [Online source](https://www.dgp.toronto.edu/~mjmcguff/research/nodetrix/nodetrix.pdf).

9. NOAA National Centers for Environmental Information, "Assessing the U.S. Climate in July 2023," 2023. Independent context for the Southwest heat episode in the selected year. [Online source](https://www.ncei.noaa.gov/news/national-climate-202307).

10. J. Heinrich et al., "Evaluation of a Bundling Technique for Parallel Coordinates," 2011. Inspiration for the explicit-group, axis-preserving browser curves. [Online source](https://arxiv.org/abs/1109.6073).