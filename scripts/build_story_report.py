"""Compose the selected question-led A2 report and compile its IEEE PDF.

The archived 32-figure manifest remains the immutable input for old figures.
Lecture extensions are read from output/lecture_previews. All figure selection,
numbering, reading guides, HTML gallery and LaTeX are regenerated together.
"""
from pathlib import Path
import argparse
import copy
import html
import json
import re
import shutil
import subprocess
import zipfile
from PIL import Image
from build_latex_report import PREAMBLE, inline, escape

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/'archive/before_story_revision'
OUT = ROOT/'report_latex'
PDF = ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf'
SECTIONS = [
    ('Country structure and paths: inspect what snapshots hide', [1,'country_paths','group_profiles'],
     'We first ask whether the apparent country groups are supported by stored connections and measured profiles. '
     'The required three-layout experiment highlights the same neighborhood in each drawing. Country trajectories '
     'recover different paths behind snapshots, while group profiles expose infrastructure differences behind similar adoption. The group partition is explicitly exploratory.'),
    ('Country relationships: inspect levels, changes and hierarchies', [3,4,28,27,5,6],
     'The browser methods preserve individual measurements while supporting filtering and hierarchy exploration. '
     'The scatterplot matrix verifies pairwise relationships with position encodings. We then compare '
     'country-level associations with within-country changes and distinguish internet-user counts from adoption percentages.'),
    ('Country change: compare timing, progress and inequality', ['milestone_timing','inequality_lenses','regional_endpoints_gains',7,8,9,10],
     'A fixed 159-country panel keeps membership constant from 2000 to 2020. Milestone panels use its 158 classified countries '
     'to expose early and late attainment; annual absolute and relative measures test whether progress means convergence. The combined regional dumbbell and raincloud '
     'distinguish regional endpoints from individual-country gains. The two required horizon '
     'variations retain trajectories and the two ridgeline variations retain distributions.'),
    ('Scalar fields: compare visual choices on identical weather inputs', [12,13,14],
     'The SciVis investigation uses a separate dataset. Controlled scalar experiments first show what color '
     'mapping, temporal normalization and contour spacing change. The measured weather fields remain fixed '
     'within each comparison; apparent contrast must not be mistaken for changed temperature or rainfall.'),
    ('Weather change: replace isolated snapshots with complete daily evidence', [18,16,17,'rainfall_concentration',20,21],
     'Complete-month differences, daily spread, rainfall totals, heat frequency and time-longitude fields '
     'answer different temporal questions. All-period analyses use the 92 daily fields; animation-scale '
     'experiments still use only the eight documented sample dates. Each denominator and geographic support is stated.'),
    ('Wind: retain spatial direction and compare monthly distributions', [15,'monthly_wind_roses'],
     'The quiver experiment compares spatial sampling and length encoding on the same western-US wind field. '
     'The monthly roses summarize all valid sampled cells in the common full-domain footprint. '
     'These views have different spatial support and complementary purposes; their legends state those scopes.'),
    ('Joint conditions: distinguish overlap, location and persistence', [29,'weather_upset',30],
     'Separate variable summaries cannot establish their joint frequency. Aligned maps provide spatial context, '
     'exact set intersections quantify daily overlap, and run lengths recover the ordering of qualifying days. '
     'Thresholds are descriptive definitions, not official hazard classes, and daily aggregates do not resolve hourly simultaneity.'),
    ('Appendix: companion material', [],
     'The companion gallery retains the adjacency matrix, worked horizon construction, KDE sensitivity and adoption '
     'alluvial. Their full explanations remain available alongside this report; they are outside the PDF page budget.'),
]

INTRO = """The central question is: **What do averages and snapshots hide about inequality, relationships and change over time?**

Assignment 1 examined whether mobile leapfrogging closed the digital divide. Assignment 2 extends the country investigation with network, multivariable, hierarchical and temporal methods, and separately examines daily gridMET weather. The shared question concerns what different visual representations reveal. The country and weather tables are not joined, and no relationship between connectivity and weather is inferred.

Our answer has three parts. Similar adoption levels can accompany different infrastructure profiles; country-level associations need not describe within-country changes. Rising adoption can reduce relative inequality while leaving larger absolute gaps; annual observations reveal a turning point hidden by endpoints. In weather, spatial averages, two-date differences and single-condition summaries can conceal geographic variation, overlapping conditions and long local runs.

The report combines required method experiments with selected analytical extensions. Each figure states its question, how to read its encodings, the measured evidence, the interpretation and its limits. Required browser interactions and scalar animations are supplied separately because a static PDF cannot demonstrate them.
"""

DATA = """**Country source and preprocessing.** `scripts/preprocess_data.py` reads the three original A1 OWID/ITU CSV extracts retained in `data/raw/`. It renames indicator columns, validates unique entity/code/year keys, outer-joins the sources and removes the explicit A1 aggregate-entity list. Missing measurements remain missing; no imputation is used. It exports the country table and supplied regional lookup to `data/processed/`; visualization builders read these outputs. Eritrea, Myanmar and Palestine remain Unclassified where the lookup is missing. Adoption is percent of people; landline, broadband and mobile are subscriptions per 100 people, which can exceed 100 and do not count unique subscribers.

**Country cohorts.** The 2020 graph has 179 complete countries and 590 undirected similarity edges. Parallel coordinates, the scatterplot matrix and the 2015-2020 change comparison use 175 matched complete countries. The 2020 treemap contains 184 countries with both user counts and adoption shares, totaling 4,521,767,530 included internet users. Temporal views retain 159 countries with adoption values in every year from 2000 to 2020; the six classified regional rows contain 158 of these countries. The illustrative trajectory figure retains six named countries with all 11 annual adoption/broadband pairs in 2010-2020. Denominators differ because required variables differ, and are not interchangeable.

**Graph construction.** For each of the four indicators, subtract its 2020 complete-case country mean and divide by its population standard deviation. Compute Euclidean distances and connect each country to its five nearest neighbors; take the undirected union. Edge similarity is 1/(1+distance). This derived graph measures profile resemblance, not cables, traffic, influence or geographic proximity. Weighted greedy modularity supplies an exploratory partition for NodeTrix. Sensitivity checks change k to 3, 5 and 8 and compare five Louvain seeds at each k.

**Weather source and support.** The team-supplied interval is July 1-September 30, 2023. gridMET fields are daily maximum temperature tmmx, precipitation pr, wind speed vs and clockwise-from-north wind FROM-direction th. NetCDF packing is decoded before source Kelvin temperatures are converted to Celsius. Existing derived caches already contain Celsius. The supplied interval spans summer into early autumn, allowing comparison of heat, rainfall and wind as the season changes; this is an analytical rationale, not evidence about the team's original selection procedure. The displayed extent is 125 W-66 W, 24 N-50 N. Reading every sixth native grid cell gives approximately 0.25-degree sampled spacing; this is subsampling, not block averaging or native resolution.

**Two temporal supports.** Required scalar experiments and GIFs use July 1, July 14, July 27, August 9, August 22, September 4, September 17 and September 30, uniformly 13 days apart. Equal spacing covers the supplied interval without choosing dates based on the plotted outcomes; eight samples stay within the required 5-10 frame range. Full-period extensions use all 92 days: 31 in July, 31 in August and 30 in September. The common footprint contains 13,416 cells valid across all four fields and dates. Missing cells remain masked. Eight-date global extrema refer to the eight sampled fields, not all 92 days, the whole Earth or a climatology.

**Aggregation and thresholds.** Domain area summaries use cosine-latitude weights on the sampled regular grid. Hot means daily Tmax at least 35 C; dry means daily rainfall below 1 mm. The new three-set comparison uses daily wind speed at least 5 m/s as an analyst-selected windy threshold. Alternatives are exported. These definitions describe daily gridded summaries, not drought diagnoses, heatwave warnings, gusts or population exposure. The wind variables describe 10 m above-ground conditions; the dataset slice has no vertical profile and does not resolve within-day coincidence.

**Conventions.** Monthly temperature differences are September mean daily Tmax minus July mean daily Tmax. Monthly rainfall is the sum of daily precipitation, not an average. Wind roses retain the source FROM-direction. Quiver arrows show flow TO-direction, using u=-s sin(theta) and v=-s cos(theta); a north wind therefore points south. Arrow display bearings account for longitude scaling and the plotted aspect. Directions must not be averaged as ordinary degree values.
"""

JS = """**Where JavaScript is used.** The browser implementations are in `web/`. `web/app.js` implements parallel coordinates using native JavaScript and SVG, including region-centroid edge bundling, brushing, axis reordering, year/region controls and fixed matched-country scales. `web/treemap.js` uses vendored D3 v7 for zoomable treemaps and two table-to-tree remodelings. `web/network.js` uses D3 for the interactive node-link view; its three layout positions are computed by NetworkX and stored in JSON. Native JavaScript in the PCP satisfies the JavaScript language requirement; D3 is a library used by the other pages.

**How to run.** From the `ass2` folder, run `python run_visualizations.py`, or double-click `START_VISUALIZATIONS.cmd`. Open `http://127.0.0.1:8765/web/home.html`. The launcher links the report, gallery, three browser pages and animation files. A local HTTP server is needed because the pages fetch JSON. D3 is bundled locally, so the visualization pages need no CDN.

**Parallel-coordinate demonstration.** Open `web/index.html`. Keep matched countries and fixed axes enabled. Set bundling to 0% and then 50%; exact axis intercepts stay fixed. Click Inspect high adoption / low broadband to reproduce the six-country selection, then clear it. Drag vertically on an axis to brush a range, inspect the selected count, then clear brushes. Click an axis title to move it one position right. Switch 2015/2020 and region to inspect the same measurement semantics. Curves between axes are rendering geometry, not observations or temporal transitions.

**Treemap demonstration.** Open `web/treemap.html`. Start at the root, click a region, inspect the breadcrumb and Back button, and hover a leaf for counts and adoption. Change from region-first to adoption-band-first hierarchy and repeat from the root. Both remodelings preserve the same 184 country leaves and total user count. The two report screenshots compare the same root total; the companion Asia drilldown has its own labeled subtotal. Nested country tiles retain adoption color within neutral group headers.

**Network demonstration.** Open `web/network.html`. Switch Spring/Spectral/Circular, search for India or an ISO code, and select a country to inspect neighbors and its original profile. Change the similarity threshold, then reset; filtering hides stored edges rather than recomputing country measurements. Pan and zoom to inspect crowded neighborhoods.

**Validation status.** JavaScript syntax, local asset loading, data counts and implementation handlers were checked for this revision. Existing screenshots show implementation states. No supported live browser session was connected during the revision, so the above end-to-end interaction sequence remains a manual check before submission. Screenshots alone do not verify interactions. `web/README.md` gives the exact source-file map and demonstration checklist.

**Submission evidence.** A2 requires JavaScript implementations of interactive bundled parallel coordinates and zoomable treemaps, plus an interactive node-link comparison of at least three layouts. The team also prepares the video required by its latest instructions. Three eight-frame scalar GIFs remain separate animation artifacts.
"""

DISCUSSION = """**Answer to the main question.** Averages conceal who differs from the typical country or location, snapshots conceal temporal order, and separate variable summaries conceal joint occurrence. The selected graphs recover these distinctions while preserving the original measurements. Their value comes from the specific question each answers and the checks that keep the comparison valid.

**Connectivity.** In the exploratory network partition, groups with mean adoption near 86% have different fixed and mobile infrastructure profiles. This does not identify a causal route to adoption because the groups were constructed from those same indicators and change with graph settings. In the 175-country matched panel, 126 countries (72%) increase adoption while landline intensity falls. The pooled broadband/adoption level association (Spearman rho=0.831) contrasts with the matched-change association (rho=0.054), so the cross-country level relationship cannot simply be read as an explanation of temporal change.

**Progress and inequality.** The P90-P10 absolute adoption gap widens from 28.63 to 69.84 percentage points between 2000 and 2020. Mean pairwise gaps rise from 11.43 to 28.78 points but peak at 32.86 in 2013. Meanwhile the Gini declines from 0.708 to 0.222: relative inequality falls while absolute gaps remain wider than at baseline. Within-region variation accounts for 46.96% of 2020 classified-panel variance. Asia's regional-median shift is 26.55 points, whereas its median individual gain is 19.75; the regional summary does not describe a typical matched country's change. On the fixed 159-country panel, 69 countries reach at least 75% adoption by 2020, while 19 remain below 25%. In the classified regional panel, Europe's 2020 median is 86.86% and Africa's is 31.89%. Progress is broad but uneven; neither upward category transitions nor a global median establishes that regional inequality has disappeared. Country-weighted comparisons describe included countries, not the distribution of the world's people.

**Weather.** The September-minus-July change in mean daily Tmax is -4.64 C over the weighted sampled footprint, with 99.66% cooler. An endpoint-only difference disagrees in sign over 18.26% of area. Hot/dry conditions occupy 16.27% of area-days, but a local run can reach 67 consecutive days. Adding the stated wind threshold narrows joint overlap to 2.57% of area-days. The rainfall concentration comparison additionally shows that 77.6% of eligible September area receives at least half its monthly rainfall in one within-month five-day window (monthly total at least 10 mm). Monthly differences, concentration, overlap and persistence are distinct quantities with different denominators and cannot substitute for one another.

**Representation and robustness.** Network positions, matrix ordering, bundling, hierarchy, color limits, contour intervals, vector density and KDE bandwidth change what is easy to see. They do not create new observations. Fixed cohorts/scales, exact edge lookup, empirical summaries, threshold experiments and graph sensitivity help distinguish representation effects from measured variation. Interquartile segments and spatial quantile ribbons show heterogeneity, not confidence intervals.

**Limits.** The country indicators are observational national aggregates; omitted factors and direction of effect are unresolved. Complete-case panels exclude countries. The similarity graph depends on features, standardization and k. Weather sampling omits finer spatial detail; neighboring cells and days are dependent. Daily aggregates do not prove hourly co-occurrence, and gridded daily wind is not a gust or station record. Boundary runs may begin before or end after the observed window. A single three-month interval does not establish climate change, anomalies relative to a long-term baseline, or hazard attribution.
"""

REPRO = """**Recreate the results.** From `ass2`, install `requirements.txt`, then run `python -X utf8 scripts/reproduce_results.py`. Its data stage runs `scripts/preprocess_data.py`; figure and report stages rebuild analysis, images, the IEEE PDF and package. Use `--download-weather` to retrieve missing gridMET caches; otherwise existing Celsius caches are reused. PDF compilation needs pdfLaTeX. Exact stage commands and input locations are in `README.md`.

**Preprocessing evidence.** `data/processed/preprocessing_audit.json` records raw-file and cache SHA-256 hashes, missing-value counts, cohort sizes, units and transformations. `weather_support.npz` exports the 13,416-cell all-variable/all-date mask and cosine-latitude weights. Eight sampled fields are checked against their corresponding days in the 92-day cache. This distinguishes raw source preparation from already converted cached inputs.

**Reading and source files.** `output/pdf/DAS732_A2_Report_IEEE.pdf` contains 30 numbered figures. `report_latex/DAS732_A2_Report.tex` and `output/DAS732_A2_LaTeX_Source.zip` supply editable source and numbered PNGs. `output/quality_figures/index.html` retains full-resolution figures and extended reading guides. Three eight-frame GIFs are under `images/scivis/`. Research folders retain numerical tables, sensitivity results and unselected trials. Earlier report versions remain archived.

**Validation.** Independent checks recompute country quantiles, regional gains, variance decomposition, monthly weather means, run lengths and five-day rain maxima. Report checks cover numbering, references, assets, page bounds and animation frames. JavaScript passes syntax and asset checks; live interaction testing remains pending as documented in the implementation section.

**Contribution allocation.** The team responsibility table below assigns one distinct Infovis work package and one distinct SciVis task to each member, with ten figure sets each. It records the adopted allocation; completed implementation and personal review must match the final individual disclosures. Shared inputs and reuse in composite figures do not create joint ownership of required tasks.

"""

CONTRIBUTIONS = [
    ('Parikshith Aithal K V (BT2024249), Person A',
     'Network construction, three layouts, interaction and country trajectory/profile interpretation; scalar color mapping, normalization, global/local scales and GIFs. '
     'Figs. 1-3, 17-18, 20-23, 25. Coordination of shared preprocessing, Introduction/Dataset text, and video opening and weather-scale explanation.'),
    ('Sindhoor Ganapathi Hegde (BT2024014), Person B',
     'Both horizon and both ridgeline variations; contour tracing, intervals, fills and contour GIF. '
     'Figs. 10-16, 19, 24, 30. Inequality, regional gains and persistence interpretation, numerical-check coordination, and corresponding report/video explanations.'),
    ('Varshith M Gowda (BT2024227), Person C',
     'JavaScript bundled parallel coordinates with brushing/reordering and zoomable treemap with two hierarchies; quiver sampling and length encoding. '
     'Figs. 4-9, 26-29. Browser-demo coordination, relationship/intersection interpretation, Discussion/Limitations, README/package integration and video conclusion.'),
]

def contributions_markdown():
    return ('## Author contributions and task allocation\n\n'
            'The following table lists each member’s assigned work. '
            '\n\n'
            '| Member | Contribution allocation |\n|---|---|\n'+
            '\n'.join('| '+name+' | '+task+' |' for name,task in CONTRIBUTIONS)+'\n\n'
            'Each member is responsible for the design, implementation, interpretation, report explanation and presentation of their assigned methods. '
            'Composite figures reuse other members\' outputs with the original task ownership retained.\n')

def contributions_latex():
    rows='\n'.join(escape(name)+' & '+escape(task)+r' \\' for name,task in CONTRIBUTIONS)
    return (r'\section*{Author Contributions and Task Allocation}'+'\n'+
            'The table lists each member’s assigned work. '
            'Each member is responsible for implementation, interpretation, report text and presentation of the assigned methods.\n\n'+
            r'\begin{table}[!ht]\centering\footnotesize'+'\n'+
            r'\begin{tabularx}{\columnwidth}{@{}p{0.27\columnwidth}Y@{}}\toprule'+'\n'+
            r'\textbf{Member} & \textbf{Contribution allocation}\\\midrule'+'\n'+rows+'\n'+
            r'\bottomrule\end{tabularx}\end{table}'+'\n')

REFERENCES = [
 ('quantiles','Rousselet, Pernet and Wilcox. Beyond differences in means: robust graphical methods to compare two groups in neuroscience. European Journal of Neuroscience 46, 1738-1748, 2017. https://doi.org/10.1111/ejn.13610'),
 ('raincloud','Allen et al. Raincloud plots: a multi-platform tool for robust data visualization. Wellcome Open Research 4:63, 2019. https://doi.org/10.12688/wellcomeopenres.15191.1'),
 ('gini','World Bank. Gini index: metadata and relative-inequality interpretation. https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SI.POV.GINI'),
 ('variance','NIST/SEMATECH. One-way ANOVA overview: sums-of-squares decomposition. https://www.itl.nist.gov/div898/handbook/prc/section4/prc431.htm'),
 ('climdex','Climdex. Indices: maximum consecutive five-day precipitation (Rx5day). https://www.climdex.org/learn/indices/'),
 ('brief','DAS732. Programming Assignment 2: Familiarization with SciVis and Infovis methods. IIIT Bangalore, Term 1, 2026-27. Supplied brief.'),
 ('gridmet','Climatology Lab. gridMET data, methods and limitations. https://www.climatologylab.org/gridmet.html'),
 ('networkx','NetworkX. Graph layouts and community algorithms. https://networkx.org/documentation/stable/reference/index.html'),
 ('d3','D3. Hierarchy and treemap documentation. https://d3js.org/d3-hierarchy/treemap'),
 ('bundling','Heinrich et al. Evaluation of a bundling technique for parallel coordinates. 2011. https://arxiv.org/abs/1109.6073'),
 ('nodetrix','Henry, Fekete and McGuffin. NodeTrix: A Hybrid Visualization of Social Networks. IEEE TVCG 13(6), 2007. https://arxiv.org/abs/0705.0599'),
 ('chordlink','Angori et al. ChordLink: A New Hybrid Visualization Model. 2019. https://arxiv.org/abs/1908.08412'),
 ('horizon','Heer, Kong and Agrawala. Sizing the Horizon. CHI, 2009. https://hci.stanford.edu/publications/2009/heer-horizon-chi09.pdf'),
 ('color','Matplotlib. Choosing colormaps and colormap normalization. https://matplotlib.org/stable/users/explain/colors/colormaps.html'),
 ('contour','ContourPy. Algorithm description. https://contourpy.readthedocs.io/en/stable/description.html'),
 ('wind','NCAR Earth Observing Laboratory. Wind direction quick reference. https://www.eol.ucar.edu/content/wind-direction-quick-reference'),
 ('upset','Lex et al. UpSet: Visualization of Intersecting Sets. IEEE TVCG 20(12), 1983-1992, 2014. https://upset.app/'),
 ('hovmoller','Unidata. Hovmoller Diagram Example. https://unidata.github.io/python-gallery/examples/Hovmoller_Diagram.html'),
 ('lectures','DAS732 supplied lecture slides, August 6-October 1, 2026, including the September 3 handwritten interpolation supplement.'),
 ('owid','Our World in Data. Internet collection, based on sources including ITU; country extracts supplied with A1. https://ourworldindata.org/internet'),
]


def extension(key):
    if key in ['country_paths','milestone_timing']:
        base=json.loads((ROOT/'output/internet_revision/entries.json').read_text(encoding='utf-8'))[key]
        return dict(base,extension_key=key)
    if key in ['inequality_lenses','regional_endpoints_gains','rainfall_concentration']:
        return json.loads((ROOT/'output/final_research/entries.json').read_text(encoding='utf-8'))[key]
    if key=='adoption_quantile_change':
        from build_quantile_change import build as build_quantiles
        return build_quantiles()
    item = next(x for x in json.loads((ROOT/'output/lecture_previews/manifest.json').read_text()) if x['key']==key)
    base = dict(title=item['title']+'.',path=f'output/lecture_previews/{key}.png',
                caption=item['takeaway'],wide=True,extension_key=key)
    details = {
      'nodetrix': (
        'Which locally connected country groups and between-group connections are obscured by a node-link overview?',
        'Each colored square is a symmetric binary adjacency matrix of one exploratory group. Each row/column is a country in the same ISO-code order; a colored cell is an internal edge. Gray segments retain the 65 individual external edges and attach to their actual country row or column. Cell size is constant, and labels give group size and internal edge density. Colors identify derived groups, not regions.',
        'The hybrid representation retains global connections while replacing internal link crossings with explicit cells. The companion profile figure explains the country measurements behind the partition. Alphabetical ISO ordering is exported in community_country_order.csv; the printed overview does not expose every country label.',
        'The weighted greedy-modularity partition gives seven groups of 40, 37, 35, 32, 14, 13 and 8 countries. There are 525 internal edges and 65 between groups, compared with 3.70% overall edge density. Group internal densities range from 15.6% to 64.3%. This fits a locally denser, globally sparse display, but high internal connectivity is partly expected from the nearest-neighbor construction and modularity objective. Changing k to 3/5/8 gives 13/7/5 greedy groups; alternative Louvain seeds also change memberships.',
        'Use the figure to inspect this partition, not to claim seven natural country types. Matrix area grows with group size, so compare the density labels rather than colored area. Paths and links remain derived profile relationships. This is a static NodeTrix-style overview; the full interaction design of the original paper is not claimed.',
        'Local matrix structure is inspectable, but the number and membership of groups depend on graph and optimizer choices.'),
      'group_profiles': (
        'Can nearly equal internet-adoption means conceal different fixed and mobile infrastructure profiles?',
        'Rows are the seven exploratory network groups. Each panel uses its own raw-unit horizontal axis. A dot is the equal-country mean, while the thick translucent segment spans the 25th-75th country percentiles. These intervals show within-group heterogeneity, not confidence limits. Group colors and IDs agree with the NodeTrix overview retained in the companion gallery.',
        'Aligned position encodings make differences easier to judge than area or radar polygons. Original units prevent standardized network features being mistaken for adoption percentages. Showing spread prevents a group mean from implying identical countries.',
        'G1 and G2 average 86.1% and 86.8% adoption, yet landline intensity averages 15.3 versus 41.2 per 100, broadband 24.6 versus 37.0, and mobile 140.3 versus 119.7. The adoption mean alone therefore conceals infrastructure differences. Groups were constructed from these indicators, so those contrasts describe the chosen partition rather than independently validate a causal technology pathway. Other rows preserve the broad profile range and their overlapping country spreads.',
        'Group membership changes under k and optimizer sensitivity. Means and interquartile ranges are country-weighted. Mobile subscriptions are not unique users; 140.3 subscriptions per 100 does not imply 140.3% of people own phones. Panel scales differ and should be read separately.',
        'Similar mean adoption accompanies different infrastructure profiles in this exploratory partition; a single adoption average cannot describe the complete profile.'),
      'adoption_alluvial': (
        'How do countries move between absolute internet-adoption categories over two decades?',
        'The three columns are 2000, 2010 and 2020 for the identical 159-country complete annual panel. Blocks are below 25%, 25 to below 50%, 50 to below 75%, and at least 75%. Ribbon thickness is the number of countries making an adjacent-date transition; color follows the source category for each segment. Exact threshold values enter the higher category.',
        'Ridgelines show distributional movement but not the category transitions connecting dates. An alluvial representation adds those matched-country transitions while holding cohort size fixed. Country membership and flow tables are supplied for exact lookup.',
        'The below-25% category contracts from 140 countries in 2000 to 70 in 2010 and 19 in 2020. The at-least-75% category grows from zero to 18 and then 69. Across 2000-2020, 140 countries enter a higher band and 19 remain in the same band. This is broad progress through absolute categories, while the remaining low-adoption countries reveal uneven progress. Same-band membership can conceal large numerical increases, and movement up categories does not alone establish shrinking inequality.',
        'All countries carry equal weight, so these ribbons do not represent people or internet traffic. Band boundaries are analyst choices. Aggregated adjacent ribbons do not uniquely trace a country through the middle column; use the membership CSV for identities. The complete-case panel excludes countries lacking any annual value.',
        'The distribution moves toward higher adoption, yet 19 of the same 159 countries remain below 25% in 2020.'),
      'weather_upset': (
        'How often do hot, dry and windy daily conditions occur separately and in combination?',
        'Each column gives one exact intersection of three sets: Tmax at least 35 C, rain below 1 mm, and wind speed at least 5 m/s. Filled dots mean present and pale dots absent. Top bars are cosine-latitude-weighted area-day percentages; left bars show marginal set percentages. All eight combinations, including none, sum to 100% over the fixed 13,416-cell, 92-day support.',
        'Exact intersections distinguish the prevalence of each condition from joint overlap. Marginal set sizes provide context for the intersection sizes. A three-set Venn diagram is possible, but aligned bars make quantitative comparisons and the none category straightforward.',
        'Hot, dry and windy sets occupy 18.06%, 76.65% and 11.65% of weighted sampled area-days. Dry with neither other condition occupies 54.11%. Hot and dry with any wind occupies 16.27%, whereas all three conditions occupy 2.57%. Thus the large dry marginal does not imply the three conditions commonly occur together. Exported alternatives cover 33/35/37 C, rain cutoffs 0.5/1 mm and wind thresholds 4/5/6 m/s; overlap changes with the definition.',
        'These are descriptive daily conditions, not official hazard classes. Daily Tmax, precipitation totals and wind summaries do not prove simultaneous hourly conditions. The chart pools time and space, so it cannot locate the overlap or distinguish isolated days from long runs. Neighboring cells and dates are dependent; no significance or independence claim is made.',
        'Frequent individual conditions can have much less frequent joint overlap: adding the chosen wind threshold reduces hot/dry overlap from 16.27% to 2.57% of area-days.'),
      'monthly_wind_roses': (
        'Does a pooled wind summary conceal monthly direction and speed differences?',
        'Each rose aggregates one month over the same full-domain 13,416-cell footprint. Sixteen equally spaced sectors show source FROM-direction, clockwise from north. Stacked colors classify speed into 0 to below 2, 2 to below 4, 4 to below 6, 6 to below 8 and at least 8 m/s. Sector radial height is percentage of the month\'s weighted area-days. All panels share a 14% radial limit.',
        'The circular representation respects the wraparound between 359 and 1 degrees. Common scales enable direct monthly comparison; normalization by each month\'s own area-days accounts for 31/31/30 day counts. It complements the selected-date western quiver by summarizing full-domain daily distributions.',
        'The largest directional frequency sector is southwest (225 degrees) in July and south (180 degrees) in August and September. The pattern therefore changes across months instead of being fully described by one pooled rose. The stacked bins show the associated speed composition. These modal sectors are not circular or vector means, and a domain-wide frequency cannot identify where each direction occurred.',
        'Read radial height, not wedge area, as proportional frequency. Near-calm observations are retained in the lightest bin; their direction has little physical meaning. The domain and denominator differ from the western-box quiver. Daily summaries cannot resolve hourly wind durations, gusts or air-parcel trajectories.',
        'Shared-scale monthly roses reveal a shift in the most frequent source-direction sector while retaining speed composition.'),
    }
    question,encoding,rationale,interpretation,limits,takeaway=details[key]
    base.update(explanation=[question,encoding,rationale,limits,takeaway],detailed_interpretation=interpretation)
    return base


def compose_report():
    import sys
    from simple_report_content import configure, apply as simplify
    from build_simple_figures import build as build_simple
    configure(sys.modules[__name__])
    build_simple()
    from build_internet_revision import build as build_revision, override_figure
    build_revision()
    from final_research_figures import build as build_final_figures
    build_final_figures()
    old = {f['figure']: f for f in json.loads((ARCHIVE/'current_figure_manifest.json').read_text(encoding='utf-8'))}
    selection = [x for _,ids,_ in SECTIONS for x in ids]
    mapping = {old_id: n for n,old_id in enumerate(selection,1) if isinstance(old_id,int)}
    mapping.update({25:selection.index('regional_endpoints_gains')+1,19:selection.index('rainfall_concentration')+1})
    def remap(text):
        def sub(m):
            n=int(m[2])
            if n in mapping: return f'{m[1]} {mapping[n]}'
            return 'the supporting rainfall distribution' if n==22 else 'the documented animation samples'
        return re.sub(r'\b(Figure|Fig\.) (\d+)\b',sub,text)
    figures=[]
    for n,key in enumerate(selection,1):
        f=copy.deepcopy(old[key]) if isinstance(key,int) else extension(key)
        f=override_figure(key,f)
        f.update(figure=n,number=n,previous_review_figure=key if isinstance(key,int) else None,
                 supporting=False)
        if key=='regional_endpoints_gains':f['previous_review_figure']=25
        if key=='rainfall_concentration':f['previous_review_figure']=19
        for prop in ['caption','detailed_interpretation']:
            f[prop]=remap(f[prop])
        f['explanation']=[remap(v) for v in f['explanation']]
        if key==19:
            f['explanation']=[v.replace('the supporting rainfall distribution','the supporting rainfall distribution retained in the archive') for v in f['explanation']]
        if key==14:
            f['explanation'][1]+=' Matplotlib/ContourPy uses serial grid-cell tracing in the Marching Squares family, appropriate for this regular two-dimensional grid. Filled intervals support regional comparison; contour lines expose threshold boundaries. The same sampling and extent isolate the effect of interval and fill choices.'
        assert (ROOT/f['path']).exists(), f['path']
        figures.append(f)
    figures=simplify(figures)
    assert len(figures)==30 and all(f['explanation'] and len(f['explanation'])==5 for f in figures)
    (ROOT/'data/current_figure_manifest.json').write_text(json.dumps(figures,indent=2),encoding='utf-8')
    selection_record=dict(status='selected',date='2026-10-24',main_figures=30,supporting_figures=0,
        total_figures=30,source_manifest='archive/before_story_revision/current_figure_manifest.json',
        generator='scripts/build_story_report.py',current_authorship='three-person responsibility allocation adopted; completed work requires individual verification',
        omitted_previous_review=[2,11,22,23,24,26,31,32],
        note='Simple-English revision: NodeTrix overview and labelled group matrix in Figure 3; six-country parallel coordinates in Figures 4-5; two scatterplots in Figure 6; regional change counts in Figure 7; within-region country variation in Figure 11; simple weather overlap bars in Figure 29. Earlier dense charts and the absolute/relative inequality comparison remain companion material. The implementation checklist and temporary AI paragraph are removed. Nine key references remain.')
    (ROOT/'data/report_selection.json').write_text(json.dumps(selection_record,indent=2),encoding='utf-8')
    parts=['# Beyond Averages and Snapshots\n\n**Connectivity profiles and daily weather | DAS732 Assignment 2 | Team Plot Twist**\n\n'
           '**Selected analytical report, 24 October 2026.** 30 figures; supporting checks in the companion gallery. '
           'The team’s task allocation is listed at the end.\n',
           '## Introduction\n\n'+INTRO,'## Data and preparation\n\n'+DATA,
           '## Interactive browser views\n\n'+JS]
    guides=['# Detailed reading guides for the selected report\n\n']
    position=0
    for title,ids,lead in SECTIONS:
        if title.startswith('Appendix'):
            parts+=['## Discussion: what the evidence answers\n\n'+DISCUSSION,
                    '## Code and supporting files\n\n'+REPRO,contributions_markdown(),
                    '## Conclusion\n\n'+CONCLUSION+'\n']
        parts.append('## '+title+'\n\n'+lead+'\n')
        for _ in ids:
            f=figures[position];position+=1
            q,enc,why,limits,take=f['explanation']
            content=f'![Figure {f["figure"]}. {f["title"]}]({f["path"]})\n\n**Figure {f["figure"]}.** {f["caption"]}\n\n'
            guide=f'### Figure {f["figure"]}: {f["title"]}\n\n'
            for label,value in [('Question',q),('How to read the graph',enc),('Why this graph',why),
                                ('What it shows',f['detailed_interpretation']),('Note',limits),('Main takeaway',take)]:
                content+=f'**{label}.** {value}\n\n';guide+=f'**{label}.** {value}\n\n'
            parts.append(content); guides.append(guide)
    parts.append('## References\n\n'+'\n'.join(f'{i}. {v}' for i,(_,v) in enumerate(REFERENCES,1)))
    (ROOT/'REPORT.md').write_text('\n\n'.join(parts),encoding='utf-8')
    (ROOT/'FIGURE_EXPLANATIONS.md').write_text('\n'.join(guides),encoding='utf-8')
    (ROOT/'data/report_figure_explanations.json').write_text(json.dumps([
        dict(figure=f['figure'],title=f['title'],question=f['explanation'][0],encoding=f['explanation'][1],
             rationale=f['explanation'][2],findings=f['caption'],detailed_interpretation=f['detailed_interpretation'],
             interpretation=f['explanation'][3],takeaway=f['explanation'][4]) for f in figures],indent=2),encoding='utf-8')
    gallery=ROOT/'output/quality_figures/index.html';gallery.parent.mkdir(exist_ok=True,parents=True)
    cards=[]
    for f in figures:
        href='../../'+f['path']; esc=html.escape
        cards.append(f'<section id="figure-{f["figure"]}"><h2>Figure {f["figure"]}. {esc(f["title"])}</h2>'
            f'<p><b>Question:</b> {esc(f["explanation"][0])}</p><a href="{href}"><img src="{href}" alt="{esc(f["title"])}"></a>'
            +''.join(f'<p><b>{label}:</b> {esc(value)}</p>' for label,value in [
                ('How to read',f['explanation'][1]),('Why this graph',f['explanation'][2]),('Measured findings',f['caption']),
                ('What it shows',f['detailed_interpretation']),('Note',f['explanation'][3]),('Takeaway',f['explanation'][4])])+'</section>')
    gallery.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>A2 selected figures and reading guides</title><style>body{font:17px/1.6 system-ui;color:#193044;max-width:1180px;margin:40px auto;padding:0 24px}'
        'img{max-width:100%;height:auto}section{border-top:1px solid #cdd9e3;padding:28px 0}h1,h2{line-height:1.2}a{color:#0072b2}</style>'
        '<h1>Beyond Averages and Snapshots</h1><p>30 figures; supporting checks in the companion gallery. '
        '<a href="../../web/home.html">Interactive launcher</a> | <a href="../pdf/DAS732_A2_Report_IEEE.pdf">IEEE report</a></p>'
        +''.join(cards)+'<h1>Companion figures outside the PDF page budget</h1>'+supplementary_html(old)+'</html>',encoding='utf-8')
    home=ROOT/'web/home.html'
    if home.exists():
        links=''.join(f'<li><a href="../{p.relative_to(ROOT).as_posix()}">{html.escape(p.stem.replace("_"," ").title())}</a></li>'
                      for p in sorted((ROOT/'images/scivis').glob('*.gif')))
        home.write_text(re.sub(r'<ul id="animation-links">.*?</ul>',
            '<ul id="animation-links">'+links+'</ul>',home.read_text(encoding='utf-8'),flags=re.S),encoding='utf-8')
    return figures


def supplementary_html(old):
    extras=[old[k] for k in [24,28,31,32]]+[extension('adoption_alluvial'),extension('nodetrix'),extension('group_profiles'),extension('adoption_quantile_change'),extension('inequality_lenses'),extension('weather_upset'),old[27]]
    from build_internet_revision import entry
    extras.append(entry('Country-by-year adoption atlas.','output/internet_review_20261024/adoption_atlas.png','Which individual trajectories are hidden by regional summaries?','159 country rows and 21 annual columns; shared 0–100% color scale, ordered by region and 2020 adoption.','Country identities and annual histories are visible at full resolution.','The atlas retains all 3,339 observed country-year values in the fixed panel. It is a full-resolution companion rather than a compressed report-column figure.','Countries are equally weighted visually. Complete cases exclude countries with missing annual observations.','A regional average cannot identify each country’s timing.'))
    extras.append(entry('Asia treemap drilldown.','output/internet_revision/treemap_zoom.png','What is inside the region-first root?','Country rectangles use count area and adoption color. The displayed total is Asia only.','This drilldown demonstrates the country encoding beneath the neutral root.','Country values are unchanged when drilling into the group.','Do not compare areas with root views as if they used the same denominator.','Zoom reveals the country leaves while preserving the hierarchy.'))
    (ROOT/'data/supplementary_figure_manifest.json').write_text(json.dumps(extras,indent=2),encoding='utf-8')
    return ''.join('<section><h2>'+html.escape(f['title'])+'</h2><img src="../../'+f['path']+'"><p>'+html.escape(f['caption'])+'</p>'+''.join('<p>'+html.escape(t)+'</p>' for t in f['explanation'])+'<p>'+html.escape(f['detailed_interpretation'])+'</p></section>' for f in extras)


def paragraph(text):
    return '\n\n'.join(inline(p.replace('\n',' ')) for p in text.strip().split('\n\n'))+'\n\n'


def build():
    # The selected plots already exist. Rebuild the report without touching
    # presentation/video assets or reverting the approved report wording style.
    from build_a1_style_report import build as build_report
    build_report()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--compose-only',action='store_true');args=parser.parse_args()
    compose_report() if args.compose_only else build()
