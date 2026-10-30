# Full lecture review: better graphs from the data we already have

Reviewed 17 October 2026. Scope: all 15 supplied slide PDFs, 486 pages, including the eight-page handwritten OpenBoard supplement. Read the text-bearing slides and visually scanned every page using contact sheets; inspected the handwritten supplement visually. The main hybrid examples were also inspected at larger size. This is a design review and exploratory analysis, not a revision of the submitted report.

## Recommendation

Keep the organizing question:

> What do averages and snapshots hide about inequality, relationships and change over time?

Use the lectures to improve how we investigate the data. A chart earns a place when it answers a distinct question, makes an existing answer easier to verify, or demonstrates a required controlled experiment.

The best immediate extensions are:

1. **Country adoption transitions:** an alluvial diagram on a fixed country panel. Shows which adoption bands gain or lose countries across dates.
2. **Weather set intersections:** an UpSet-style view with exact intersections and marginal set sizes. Distinguishes a common individual condition from less frequent combinations.
3. **Monthly wind roses:** shared-scale small multiples of direction and speed. Adds time to the existing pooled wind summary.
4. **NodeTrix plus group profiles:** an exploratory network overview followed by measurements that explain its groups. Group sensitivity must accompany the interpretation.

The next interaction improvement should link country selection across the existing network, matrix, PCP and country details. This is likely more useful than adding several additional standalone graph styles.

Open the [five preview figures](../output/lecture_previews/index.html). They have PNG/SVG exports, reading guides and numerical CSVs. The report, current gallery and 32 figure IDs have not been altered. These static previews do not claim to implement the papers' complete interactive systems.

## Every supplied lecture and its application

Page numbers below are PDF page numbers. The PDFs are the source of the lecture ideas; the proposed applications and priority judgments are our design assessment.

| Source | Pages | Useful ideas | Application to our data and current work |
|---|---:|---|---|
| [August 6](lecture_slides/DAS732-lecture_2026-08-06.pdf) | 39 | Composition, Minard, Anscombe, Datasaurus | Give every figure a question and a supported takeaway. Inspect distributions and exceptions alongside averages/correlations. Existing SPLOM already puts this into practice. |
| [August 11](lecture_slides/DAS732-lecture_2026-08-11.pdf) | 28 | Marks/channels, containment versus connection, overview/zoom/details | Use position for quantitative comparison; color for region or group identity. Select a country in one view and retain it across related views. A treemap hierarchy and a similarity edge express different relationships. |
| [August 18](lecture_slides/DAS732-lecture_2026-08-18.pdf) | 30 | Data types, sampled fields, perceptual color maps, palette versus mapping | Use ordered palettes for weather magnitude, zero-centered diverging maps for signed differences, categorical palettes for country groups. Keep zero precipitation distinct from missing data. Improve current figures rather than add another palette gallery. |
| [August 20](lecture_slides/DAS732_lecture-2026-08-20.pdf) | 34 | Channel effectiveness, combining channels, sampling/reconstruction | Supplement bubble encodings with aligned profile dots. Test arrow sampling while retaining actual values. Do not imply interpolation creates new observations. Current subsampled weather footprint needs explicit scope. |
| [August 27](lecture_slides/DAS732-lecture_2026-08-27.pdf) | 39 | Scalar fields, normalization, interpolation, elevation, Marching Squares and contour fill | Add a labeled 35 C isotherm to selected temperature maps to inspect a chosen boundary. Keep the existing contour-interval experiment. A 3D temperature surface is lower priority than a readable 2D map plus contours. |
| [September 1](lecture_slides/DAS732-lecture_2026-09-01.pdf) | 30 | Quiver glyphs, equal length plus magnitude color, overlays, global scales, 3D isosurfaces | Refine the quiver comparison and combine a scalar layer with sparse wind arrows when both stay legible. A monthly wind rose complements spatial arrows. The current data contains surface daily fields, not a physical atmospheric volume. |
| [September 3](lecture_slides/DAS732-lecture_2026-09-03.pdf) | 13 | Slicing, resampling, Marching Triangles, bivariate mapping derivations | Use fixed geographic transects or latitude-band time views to examine change. The existing Hovmoller diagrams are band averages, not literal single-plane slices. A bivariate hot/dry map is a possible later extension with a clear legend. |
| [September 3 OpenBoard](lecture_slides/DAS732-lecture_2026-09-03_OpenBoard.pdf) | 8 | Handwritten linear/bilinear interpolation, rectangle/trapezium parameters, scalar-to-color mapping | Strengthen the methods explanation with one real grid cell and its contour crossing. A bilinear bivariate legend is an option, but a discrete 3x3 legend will often be easier to read. This supplement introduces no new observations. |
| [September 10](lecture_slides/DAS732-lecture_2026-09-10.pdf) | 29 | Node-link, adjacency matrices, hierarchy, treemap/sunburst | Improve the existing adjacency view with ordering choices. Keep the same leaves and counts when comparing treemap hierarchies. A sunburst is an optional hierarchy comparison with limited additional analytical value here. |
| [September 15](lecture_slides/DAS732-lecture_2026-09-15.pdf) | 43 | Tidy trees, radial trees, force layouts, Fruchterman-Reingold, Kamada-Kawai, layered layouts | Retain the three required layouts on the identical graph. Use neighbor lookup to verify a visual impression. Extra tree layouts fit our constructed hierarchy, while layered dependency layouts need a meaningful direction absent from the current similarity network. |
| [September 17](lecture_slides/DAS732-lecture_2026-09-17.pdf) | 42 | Arc/chord diagrams, MatLink, NodeTrix, ChordLink, synchronized views, edge bundling, seriation/VAT | Strong extension: NodeTrix with country profiles. Also compare region versus community matrix order. ChordLink is a candidate local representation switch on the same selected group. Region-level chords need explicit aggregation and possible-pair normalization for affinity comparisons. |
| [September 22](lecture_slides/DAS732-lecture_2026-09-22.pdf) | 39 | Dumbbells, violins, wind roses, alluvial/Sankey, bubbles, PCP distributions, SPLOM/GPLOM | Strong new candidates: adoption alluvial and monthly wind roses. Add marginal distributions to PCP. Use dumbbells for a small named country set when endpoints matter. Existing scatter/SPLOM can gain linked selection; a full GPLOM is unnecessary for only four numeric measures and region. |
| [September 24](lecture_slides/DAS732-lecture_2026-09-24.pdf) | 43 | Brushing/cross-filtering, remodeling, choropleths, glyphs, cartograms, KDE and bandwidth | Highest interaction priority: linked country selection. Consider a map of adoption change with details on demand if geographic context helps. Preserve actual weather field values instead of treating a field as point-event density. Existing KDE sensitivity addresses a real distribution-design issue. |
| [September 29](lecture_slides/DAS732-lecture_2026-09-29.pdf) | 37 | Horizons, ridgelines, braided graphs, small multiples, calendars, space-time diagrams, dynamic networks | Keep required horizon/ridgeline variants. Use shared scales for monthly wind roses and map panels. A calendar of actual daily hot/dry area could show runs; a calendar of complete data availability adds little. Dynamic networks require fixed country membership/scaling and stable layout. |
| [October 1](lecture_slides/DAS732-lecture_2026-10-01.pdf) | 32 | Venn/Euler, Bubble Sets, radial sets, UpSet, Karnaugh maps, parallel sets, membership tasks | Strong new candidate: weather intersections. Parallel sets can relate region, adoption band and broadband band, but uses analyst-selected categories; PCP preserves continuous values. Bubble Sets may highlight chosen memberships on a stable network layout; do not confuse those overlays with discovered communities. |

## What the actual data permits

### Country indicators

- Existing graph: **179 countries, 590 undirected edges, 2020**, built from four z-scored indicators using the union of five-nearest-neighbor choices.
- Four features: internet adoption percentage; landline, broadband and mobile subscriptions per 100 people. Subscription counts can exceed 100 and do not measure unique users.
- Existing temporal panel: **159 countries, all 21 annual observations from 2000 through 2020**. The preview uses 2000, 2010 and 2020 from that same panel.
- Existing matched 2015/2020 browser records serve a different complete-case sample; do not silently use its denominator for the 159-country temporal panel or the 179-country graph.
- The table contains no measured country-to-country traffic or physical cable adjacency. All network edges are derived similarities.

### Weather

- Existing full daily cache: **July 1 to September 30, 2023; 92 days**.
- Fields: daily maximum temperature, daily precipitation, wind speed, wind FROM-direction. The cached temperature is already Celsius; do not convert it a second time.
- Fixed complete footprint across all four fields/dates: **13,416 sampled cells**, every sixth native cell.
- Approximate area weights: cosine of latitude on this regular latitude/longitude sample. Results describe the sampled footprint, not population exposure.
- Within-day coincidence and wind gusts cannot be inferred from daily summaries. Wind direction is circular; use vectors or circular summaries rather than an arithmetic degree mean.

## Preview 1: NodeTrix and profiles

**Question:** Which countries have similar multivariable profiles, and can similar adoption accompany different infrastructure?

[NodeTrix PNG](../output/lecture_previews/nodetrix.png) and [profile PNG](../output/lecture_previews/group_profiles.png).

The static NodeTrix preview represents internal group edges as symmetric binary matrices. Each external edge connects to its actual country's row or column. Both matrix axes use the same alphabetical ISO-code order. Country lookup is exported as a CSV. Matrix cell size is constant, so larger groups occupy larger squares; compare numerical density labels rather than total colored area.

Using weighted greedy modularity on the existing graph gives seven groups: 40, 37, 35, 32, 14, 13 and 8 countries. Of 590 edges, 525 fall inside those groups and 65 connect groups. The overall graph density is 3.70%; group densities range from 15.6% to 64.3%.

The companion profile chart uses dots for group means and thick intervals for country interquartile ranges, separately for each raw-unit indicator. G1 and G2 have mean adoption of 86.1% and 86.8%, but broadband intensities of 24.6 and 37.0 per 100, and landlines of 15.3 and 41.2 per 100.

**Interpretation:** these are useful descriptive profiles in this partition. The grouping used the same indicators, so separation is not independent confirmation of natural country types or a causal mechanism.

**Sensitivity result:** the greedy optimizer yields 13 groups at k=3, seven at k=5, and five at k=8. Louvain with five seeds at each k also changes membership and group counts. The best Jaccard matches to G1/G2 vary substantially. Report this dependence; do not promise seven stable global digital communities. High within-group connectivity is partly expected because modularity explicitly favors it and nearest-neighbor graph construction favors local connections.

**Better interactive version:** hover a matrix cell for both countries and their original indicators; click a country to highlight external edges and show its profile; switch a selected group between node-link, matrix and ChordLink-style local representations; allow region/community matrix ordering. Keep group colors separate from region colors and provide a region breakdown in details.

## Preview 2: adoption-band alluvial

**Question:** How do countries move between adoption bands while overall adoption rises?

[Alluvial PNG](../output/lecture_previews/adoption_alluvial.png).

Use three columns: 2000, 2010, 2020. Bands: below 25%, 25 to below 50%, 50 to below 75%, and 75% or above. Exact threshold values enter the higher band. Ribbon thickness is the number of countries making each adjacent-date transition.

| Adoption band | 2000 | 2010 | 2020 |
|---|---:|---:|---:|
| Below 25% | 140 | 70 | 19 |
| 25 to <50% | 17 | 42 | 22 |
| 50 to <75% | 2 | 29 | 49 |
| At least 75% | 0 | 18 | 69 |
| Total matched countries | 159 | 159 | 159 |

Over the full interval, 140 countries enter a higher band and 19 remain in the same band. Same-band membership can hide substantial numerical growth. This figure shows movement into absolute adoption categories; it does not by itself establish convergence or reduced inequality.

**Value relative to ridgelines:** ridgelines show how distributions change; ribbons show adjacent-date membership transitions on the same cohort. The static aggregation cannot trace identities continuously through the middle column. The exported country membership CSV can support search/highlighting in a later interactive version.

Use equal country weights for a country comparison. A population-weighted view would answer a different question and require consistent population data. Repeat with different band boundaries before presenting those boundaries as meaningful country categories.

## Preview 3: weather intersections

**Question:** How often do the conditions occur separately and together?

[Intersection PNG](../output/lecture_previews/weather_upset.png).

The preview defines three descriptive sets over cell-days:

- Hot: daily maximum temperature at least 35 C.
- Dry: daily precipitation below 1 mm.
- Windy: daily speed at least 5 m/s.

The term dry here is a daily rainfall threshold, not a drought diagnosis. Windy is an analyst choice, not an official warning category. The figure shows all eight exact combinations, including none, along with marginal set sizes. Approximate area weights are used, and all 92 days have equal temporal weight.

Measured results:

- Hot: **18.06%** of weighted sampled area-days.
- Dry: **76.65%**.
- Windy: **11.65%**.
- Hot and dry, regardless of wind: **16.27%**.
- Hot, dry and windy together: **2.57%**.
- Dry with neither hot nor windy: **54.11%**.

**Value relative to separate maps:** a frequent condition need not coincide with the others. The exact intersections avoid adding overlapping set totals as if they were disjoint.

This pooled view loses geography and persistence. Pair it with the existing frequency and longest-run maps. Daily Tmax, precipitation totals and daily wind summaries do not prove all conditions occurred at the same hour.

**Sensitivity:** exported calculations use 33/35/37 C, rainfall cutoffs 0.5/1 mm and speed cutoffs 4/5/6 m/s (18 combinations). Do not interpret the base 2.57% as threshold-independent. At only three sets a labeled Venn diagram is also feasible; the bar-and-matrix view is chosen for quantitative comparison and easy extension, not because three sets demand UpSet.

## Preview 4: monthly wind roses

**Question:** Does a pooled wind summary hide monthly changes in speed and direction?

[Wind-rose PNG](../output/lecture_previews/monthly_wind_roses.png).

Use July, August and September small multiples with identical radial limits, 16 direction sectors and five fixed speed bins: 0 to below 2, 2 to below 4, 4 to below 6, 6 to below 8 and at least 8 m/s. Sector directions are meteorological FROM-directions, clockwise from north.

Each month sums to 100% of that month's weighted area-days, so the 31/31/30 day counts do not inflate longer months. The common radial limit is 14%. The modal direction sector is southwest (225 degrees) in July and south (180 degrees) in August and September. This is the largest frequency sector, not a vector mean.

**Value relative to quiver:** a quiver map shows where vectors point on a chosen date; roses summarize the distribution across all sampled cells and all days within each month. A future west/central/east comparison could test how much pooling hides spatial differences.

Directions associated with near-calm winds are weakly meaningful. The lightest bin retains these observations rather than deleting them. Do not describe the rose as a wind trajectory, gust record or duration of continuous wind from one direction.

## Other ideas: where they help and where they add little

| Candidate | Useful application | Priority / decision |
|---|---|---|
| Community-reordered adjacency matrix | Compare the same graph ordered by region and by derived group; optionally degree order inside groups | High-value improvement to existing Figure 24. Same row/column permutation; ordering does not change edges. |
| Linked network + matrix + PCP | Select one country/group and inspect the same IDs everywhere | Highest interaction improvement. Country membership differs across source views; show unmatched IDs explicitly. |
| PCP marginal distributions | Histograms or densities along each axis expose concentration masked by overlapping paths | High-value refinement. Keep units, axes and country cohort fixed when comparing bundling. |
| ChordLink | Switch a selected local group between matrix and chord representations | Optional comparison after NodeTrix; evaluate exact-edge lookup versus overview. Do not call an aggregate region chord chart ChordLink. |
| Region chord diagram | Summarize similarity edge counts within/between regions | Optional overview. For affinity, report observed edges / possible pairs: within n(n-1)/2, between n_i*n_j. Internal edges count once in statistics even if a plotting matrix needs mirrored entries. |
| Arc diagram / MatLink | Inspect a small selected neighborhood or paths alongside adjacency | Low priority at 179 nodes without selection. A graph path means a chain of similarity links, not physical routing. |
| Network edge bundling | Reduce clutter while keeping searchable individual edges | Optional. Bundles can obscure exact endpoints and look like stronger relationships than the source supports. This differs from required PCP bundling. |
| VAT/dissimilarity matrix | Inspect the continuous standardized distances before thresholding into k-neighbor edges | Useful robustness extension: checks whether a graph partition reflects a continuum. Call it VAT only if the specified algorithm is actually implemented. |
| Temporal network panels | Compare similarity neighborhoods across years | Later extension. Fix complete country cohort, feature order and scaling reference; hold positions fixed or align layouts. Distinguish changed profiles from changed graph thresholds and layout motion. |
| Dumbbells / slopegraphs | Compare 2015 and 2020 for a small explicit set of countries | Clear supporting figure when country endpoints matter; duplicates existing change plots if applied indiscriminately to everyone. |
| Parallel sets | Region -> adoption band -> broadband band | Useful categorical exploration with explicit thresholds and counts. Continuous PCP already preserves more detail; do not substitute parallel sets for required PCP. |
| Telecom UpSet | Overlap of low adoption, low broadband and high mobile intensity | Possible, but needs justified thresholds and coverage. Weather is the stronger initial set application because the existing hot/dry investigation provides continuity. |
| Bivariate weather color map | Encode temperature and rainfall classes in one geographic panel, with sparse wind overlay only if readable | Optional alternative to a four-field composite. Use a labeled 3x3 legend, fixed cutoffs and a missing-data color. Avoid making temperature hard to read by mixing three quantities into hue. |
| Threshold contours | Follow a specified temperature boundary across dates | High-value refinement of current contours. Keep the same threshold/date selection rule; report sampled area above it. A contour threshold is not automatically an official hazard boundary. |
| Daily calendar of joint-condition area | Color each actual date by its weighted hot/dry area fraction | Useful supporting time view for runs and dates. Compare with the existing line plot; retain whichever makes the temporal question clearer. |
| Small multiples of event maps | Contrast typical/peak dates or all three monthly summaries | Good when date selection is explicit and common scales are used. Event-selected dates illustrate events, not seasonal averages. |
| Transects and space-time fields | Inspect temperature/rain along a fixed line or average within a stated band | Existing Hovmoller is already a strong application. State whether each cell is an actual transect sample or an average across many latitudes. |
| Streamlines | Explore instantaneous direction structure on a selected field | Optional; use a suitable coordinate transform and explain seeding. Daily wind fields do not define air-parcel trajectories over multiple days. |
| Geographic choropleth | Map country adoption rates or changes | Useful geographic context; requires country geometry. Map rates, with counts supplied separately to avoid land area implying population exposure. |
| Cartogram / proportional symbols | Contrast adoption rates with internet-user counts | Lower priority because treemap already addresses counts. Cartogram distortion makes precise geographic comparison harder. |
| Sunburst / tidy tree | Alternative view of our constructed country hierarchy | Methods comparison only. Keep the same leaves, measure and hierarchy when comparing layout; changing hierarchy answers a different question. |
| KDE hotspot map | Density of genuine point events if such events are supplied | Current weather is an existing sampled field. Smoothing the regular grid as point-event density would change the measured quantity. Existing country KDE sensitivity is more relevant. |
| 2.5D elevation surface | Temperature as artificial height above longitude/latitude | Possible illustration, but occlusion and perspective make quantitative comparison harder; current 2D fields/contours are clearer. |
| 3D isosurface / volume rendering | Physical volumetric measurements if later supplied; alternatively a clearly labeled space-time cube | Current cache has no atmospheric height/depth dimension. A longitude-latitude-time cube is a valid space-time construction but is not a 3D atmospheric measurement. Low priority for this report. |
| Waterfall / variwide / streamgraph | Additive contributions or meaningful widths with correct units | No strong unmet question in this dataset. Four subscription/adoption measures are not additive components of a common total. |
| Radar charts | Small selected normalized country profiles | Aligned dot profiles/PCP make values easier to compare and avoid polygon-area effects from axis order. Low priority. |
| Isochrones / isodistance | Travel or network cost data | No appropriate travel-time or physical routing measurements are present. Similarity distance should not be presented as geographic travel time. |

## How the story would read

1. **The average conceals different country experiences.** Open with the fixed-panel distribution, then use adoption transitions to show membership movement. Use required horizons/ridgelines for the detailed temporal evidence.
2. **Similar adoption does not imply identical infrastructure.** Inspect profiles through PCP/scatter plots; use NodeTrix to explore neighborhoods and explain grouping sensitivity. The group profile example illustrates the distinction without claiming causation.
3. **Separate weather summaries conceal overlap.** Use scalar/contour maps to establish where values occur, then the set-intersection view to quantify joint daily conditions.
4. **A frequency conceals timing and persistence.** Keep daily trajectories, Hovmoller and longest-run maps. Monthly wind roses show what an all-period directional summary hides.
5. **Representation can change our impression.** Use the required controlled comparisons of graph layouts, bundling, hierarchy, scales, contour intervals and vector density. Make the numerical observation explicit and preserve the data/support for each comparison.

The telecom and weather examples answer a shared methodological question. They do not establish a measured relationship between internet adoption and weather.

## Suggested integration order

1. Review the preview gallery for readability and analytical value.
2. Prioritize adoption transitions and weather intersections for substantive additions. Monthly wind roses can refine/replace the pooled wind summary after selection.
3. Retain NodeTrix as exploratory evidence with profiles and sensitivity. Add interactive details before relying on country-level edge lookup in it.
4. Improve the existing PCP/matrix interactions and shared scales; do not expand the report with all optional methods.
5. Only after choosing the final figures, update captions, report order, ownership and numbering. Required experiments remain required even when an optional figure is more attractive.

These priorities are recommendations. No figures have been cut or renumbered. New previews stay in their own output folder.

## Reproduce and validate

Run from the workspace root:

```powershell
python -X utf8 ass2/scripts/preview_lecture_extensions.py
```

Outputs: `ass2/output/lecture_previews/`. The script checks country-panel totals, ribbon margins, graph adjacency symmetry counts, complete weather support, physical ranges, exact-intersection totals and wind-rose normalization. The hot/dry area-day total agrees with the existing quality analysis (16.27447592706034%). The preview PNGs were visually inspected; the final alluvial and wind-rose label refinements were rendered again for review.

Numerical files include group profiles/country ordering, 18 network sensitivity configurations, adoption flows/country memberships, all-period and monthly weather intersections, 18 weather threshold configurations and monthly wind-rose bins. Group sensitivity compares k=3/5/8 and weighted greedy modularity plus five Louvain seeds per k. Results are descriptive; no independence assumptions, confidence intervals or significance claims are added.

## Source data and primary method references

- [Existing country graph](../data/country_network_2020.json) and [construction code](../scripts/build_infovis_data.py).
- [Annual adoption panel](../data/internet_panel_2000_2020.csv).
- [Full daily weather cache](../data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz) and [manifest](../data/scivis/daily_manifest.json).
- [Existing interpretation and figure-selection review](../FIGURE_SELECTION_REVIEW.md).
- Henry, Fekete and McGuffin, [NodeTrix](https://arxiv.org/abs/0705.0599): matrices for selected local subgraphs within a global node-link representation.
- Angori et al., [ChordLink](https://arxiv.org/abs/1908.08412): local chord diagrams embedded within a global node-link representation.
- Lex et al., [UpSet project and original-paper reference](https://upset.app/): exact intersections, marginal set sizes and quantitative interpretation. With three sets, the motivation here is readable quantities, not set-count scalability.

Any future report integration should accurately record the actual analysis, code generation and writing assistance used in this review in the course's existing individual disclosure process.
