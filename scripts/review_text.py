"""Concise, figure-specific interpretation corrections from the external review."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PDF_CAPTIONS={
1:'P95 keeps 797 edges and 12 isolates. Layouts preserve neighbors while changing separation and crossing costs; boxed rows deliberately place isolates.',
2:'Similar adoption gains accompany different annual infrastructure paths.',
3:'A shared community label conceals unequal internal degrees and measured gaps.',
4:'One adoption-gain band contains opposing landline and mobile changes.',
5:'High-adoption countries retain different four-indicator profiles.',
6:'Pairwise associations coexist with substantial profile exceptions.',
7:'Strong endpoint association does not describe paired gains.',
8:'Large online-user populations can coexist with incomplete adoption.',
9:'Hierarchy remodeling changes which composition is prominent, preserving the total.',
10:'Broad progress coexists with a widening absolute gap between fixed cohorts.',
11:'Regional averages leave 47% of measured country variation within regions.',
12:'A regional median shift can differ from the median individual gain.',
13:'Country horizons reveal different majority-use crossing times.',
14:'Regional trajectories differ; Oceania ends at 53.7%.',
15:'A rising median coexists with a broad 2020 distribution.',
16:'Regional distribution histories differ behind the global shift.',
17:'Identical values change appearance; zero-centered departures require a different encoding.',
18:'Daily rescaling changes the numerical meaning of the same color.',
19:'Custom lines match ContourPy at four thresholds; filled bands trade boundary detail for regional readability.',
20:'Complete-month means cool while retaining geographic differences.',
21:'Endpoint and complete-month differences have opposite signs over 18.26% of area.',
22:'Daily means conceal different simultaneous spatial spreads.',
23:'Similar monthly rain totals conceal different five-day concentration.',
24:'Repeated hot days remain spatially concentrated despite seasonal cooling.',
25:'Longitude-centered departures reveal timing; coastal rain extremes can have sparse spatial support.',
26:'Thinning removes locations; equal arrow lengths remove magnitude encoding.',
27:'Common-scale roses expose a monthly shift in source direction.',
28:'Aligned fields reveal spatial coincidence on two selected dates.',
29:'Frequent separate conditions have only 2.57% joint occurrence.',
30:'Frequency, uninterrupted duration and daily affected area describe different event properties.',
31:'Nearly equal adoption, differing infrastructure. Histogram distance uses three infrastructure indicators; color tests the full four-indicator P95 rule.',
32:'Equal 75-day counts conceal longest spells of 17 versus 67 days.'}
PDF_GUIDES={
1:'n=179 complete 2020 profiles. Top: pair scores and cutoff sensitivity. Bottom: region-colored, degree-sized nodes; orange edges highlight India.',
2:'Six country panels retain annual 2010-2020 pairs on shared axes. Open/filled endpoints mark 2010/2020; intermediate dots preserve timing.',
3:'Left: aggregate community nodes and between-group edge counts. Right: degree-ordered individual pairs; teal meets P95, white does not, gray excludes self-pairs.',
4:'n=175 matched 2015/2020 countries. Axes show within-country changes; zero is aligned. The brush highlights 20-30-point adoption gains; three examples are named.',
5:'n=175 matched countries, shown in 2020. Adoption-band colors/bundles organize four measured axes. Read at intercepts; the browser retains brushes and ordering controls.',
6:'n=175 matched countries. Diagonals show distributions; lower cells plot pairs, upper cells Spearman rank associations. Region colors identify context.',
7:'n=175 matched countries. Left compares adoption associations for levels and paired gains; right plots actual broadband/adoption gains, preserving exceptions.',
8:'n=184 countries. Region-first rectangles sum included users; country colors show adoption share. Zoom changes the displayed subset, not the underlying values.',
9:'The same 184 leaves and user total are regrouped by adoption band, then region. Area remains online-user count; color remains adoption share.',
10:'The same 159 countries remain in three cohorts fixed by 2000 adoption. Curves are yearly medians; endpoint dots and middle-half bars expose spread.',
11:'Each dot is one classified country; black ticks are regional averages. The variance bar partitions country-level variation within and between regions.',
12:'Paired 2015/2020 country gains appear beside regional endpoint medians. Black ticks mark median shifts; open markers mark median individual gains.',
13:'Rows retain annual country adoption around a 50% reference. Red/blue shows below/above; darkness folds 25-point bands. Dots mark first observed crossings.',
14:'Regional median histories use the same reference and bands. Right labels give 2020 adoption and first observed crossing; fixed regional memberships remain unchanged.',
15:'Ridges compare five yearly distributions of the same 159 countries on 0-100%. Rugs retain observations and right labels medians; peak heights are normalized.',
16:'Six regional panels repeat the five-year ridgeline comparison with fixed memberships. Shared horizontal scales support timing and spread comparisons; rug marks retain countries.',
17:'A/B/F hold absolute Tmax fixed; C/D hold rainfall fixed. E changes to a zero-centered within-period temperature departure, requiring a diverging scale.',
18:'Identical temperature fields use fixed eight-date extrema at left and each date\'s extrema at right. Read the separate colorbars before comparing colors.',
19:'A: custom 16-case tracing. B: 35 C overlay against ContourPy. C/D: five-/ten-degree filled bands. Bottom diagrams show the corner configurations.',
20:'Three monthly maps average all daily maxima on the common footprint. Shared color and 25/35 C contours allow spatial comparison.',
21:'A/B compare monthly and endpoint differences with shared limits. C marks opposite signs; D shows area-weighted monthly-change distributions.',
22:'Solid lines are spatial medians, dashed lines weighted means, ribbons spatial p10-p90. Fixed west/central/east cell sets retain every date.',
23:'Top: monthly rain totals. Bottom: wettest five-day share, restricted to cells with at least 10 mm monthly rain. Masks change eligible footprints.',
24:'Each month maps the percentage of its days at or above 35 C. Shared colors compare repetition; zero is a measured frequency.',
25:'A locates 30-45 N. B/C place date horizontally and longitude vertically; colors show period-mean Tmax departures and rain. D reports land-cell support.',
26:'Columns sample every fourth/twelfth display cell. Upper arrow lengths encode speed; lower lengths are equal. Colors encode speed throughout; keys identify 5 m/s.',
27:'Each rose bins FROM-direction; stacked colors bin speed. Ring frequencies and the 14% radial maximum are common across all three months.',
28:'Two objectively selected dates share temperature colors, rain thresholds, arrow positions and speed keys. Layers reveal spatial coincidence on each date.',
29:'Bars are weighted cell-day frequencies. The first three overlap; the fourth counts their exact intersection at the same cell and date.',
30:'Maps show frequency and longest run; the timeline gives daily affected area. The threshold panel repeats the calculation under six definitions.',
31:'n=179 complete 2020 profiles. Histogram distance uses three infrastructure indicators; pass/fail color uses four-indicator P95. Example cells label raw subscription gaps.',
32:'Rows are fixed grid cells, columns all 92 dates. Orange marks hot-dry days; gray marks absence. Row labels state counts and longest runs.'}
PDF_ACTIONS={
1:'Compare exact neighbors across layouts before interpreting visual separation.',2:'Use annual paths to distinguish countries with similar endpoint gains.',3:'Inspect individual pairs before generalizing from a community label.',4:'Trace all four country changes before assigning one transition story.',5:'Read the full profile before treating an adoption band as an infrastructure model.',6:'Check scatter shapes and exceptions alongside correlation coefficients.',7:'Evaluate paired gains directly; endpoint association cannot substitute for change analysis.',8:'Read count and adoption share together when discussing access.',9:'Keep the denominator fixed when comparing alternative hierarchies.',10:'Distinguish absolute catch-up from broad progress and from relative inequality.',11:'Retain country-level spread when interpreting regional summaries.',12:'Calculate individual gains before interpreting a shift in regional medians.',13:'Use first-crossing years to recover timing hidden by endpoints.',14:'Compare regional trajectories, then inspect the country spread they compress.',15:'Read distribution width alongside the rise in the median.',16:'Inspect regional histories before treating global progress as a shared trajectory.',17:'Choose a color center only when it has a meaningful data reference.',18:'Use fixed scales to compare dates; use local scales to inspect within-date detail.',19:'Use traced thresholds for boundaries and filled bands for regional comparison.',20:'Follow monthly means with daily views to recover timing.',21:'Check whether endpoint dates reverse the complete-month direction.',22:'Read daily spatial spread alongside each sector summary.',23:'Separate monthly amount, wet-day count and concentration of timing.',24:'Use persistence views to distinguish scattered hot days from continuous spells.',25:'Check baseline and spatial support before interpreting time-longitude streaks.',26:'Choose arrow density and length encoding together to preserve readable direction.',27:'Compare pooled direction frequencies, then return to maps for location.',28:'Inspect aligned fields before computing complete-period overlap.',29:'Calculate joint conditions explicitly rather than multiplying marginal frequencies.',30:'Report frequency, duration and affected area as separate event properties.',31:'Compare the full profile even when headline adoption rates nearly match.',32:'Preserve daily order when duration matters.'}
SCOPE='''**Scope and limits.** Country aggregates support descriptive comparisons, not causal attribution. Complete-case cohorts exclude missing observations; counts, shares and subscription rates use different denominators. Weather results concern one three-month interval and a fixed subsampled footprint, with approximate area weights and dependent cells/days. Daily fields need not coincide hourly; runs may extend beyond the window. Event cutoffs are descriptive, and period departures are not climate normals. Stride six reduces processing volume and display overlap; no native-resolution equivalence is claimed.'''

DETAIL={
1:'''The distribution defines the complete 15,931-pair universe. P95=0.569763 retains 797 edges and all 179 countries, including 12 isolates. This is the team's sparse default; P90/P92.5/P97.5 retain 1,594/1,195/399 pairs and 5/9/22 isolates. The labeled rows deliberately place degree-zero countries.

All layouts preserve India's twelve links. Spring separates the connected core with relatively short edges; Spectral compresses some neighborhoods and can overlap nodes; Circular preserves a uniform node order but creates long, crossing chords. Proper straight-edge crossings are 3,042/3,371/98,598 for Spring/Spectral/Circular. These display-specific counts exclude shared endpoints and collinear overlaps; they are readability measures, not evidence that one graph is truer. Region color and degree size expose composition and connectivity. The package's `output/network_revision/` contains the threshold sweep and metric-sensitivity tables; `output/review_revision/layout_comparison.csv` defines the layout comparison.''',
3:'''The left graph aggregates six communities, making their 98 between-group links readable; the 699 internal links remain inside the groups. The right matrix resolves the selected 15-country group, with 93 of 105 possible links. Rows and columns are now ordered by internal degree, so dense members and gaps are visible without decoding miniature overview matrices.

Afghanistan has 14 internal neighbors and Angola seven: a shared group label conceals different pair relationships. White cells are measured scores below P95; the diagonal is excluded. This node-link/matrix hybrid is inspired by NodeTrix [8], while community nodes in the overview are aggregates. The exact matrix supplies the individual evidence that the grouped picture omits.''',
4:'''The gain brush selects 39 of the same 175 matched countries. Within this 20-30-point adoption band, broadband changes span about -0.3 to +16.6, landlines -14.8 to +7.1 and mobile -80.2 to +34.5 subscriptions per 100. One adoption-gain interval therefore conceals several infrastructure transitions.

Georgia and Brunei both gain about 25 adoption points and eight broadband subscriptions, yet their landline/mobile changes are -14.8/-12.0 versus +5.2/+10.2. Uzbekistan gains 28.3 adoption points, 10.0 broadband, 7.1 landline and 28.6 mobile subscriptions. Its positive movement on all four axes contrasts with the other named cases. Read at axis intercepts; bundled joins are tracing aids [10].''',
7:'''Across the same 175 countries, broadband-adoption rank association falls from 0.83 in 2020 levels to 0.054 in paired 2015-2020 gains. The gain scatter lacks the ordered upward pattern suggested by the endpoint coefficient. Landline and mobile associations similarly weaken, from 0.79 to 0.29 and 0.53 to 0.07.

This changes the analytical question, not the cohort: countries already at high infrastructure levels differ from those adding most within five years. Adoption is bounded at 100%, so high-baseline countries also have less possible gain; saturation and diffusion timing can affect these contrasts. The figure supports separating levels from gains, not concluding that infrastructure is unimportant.''',
10:'''All fixed cohorts progress, but the lowest-start group ends at a median 36.1% adoption and the highest at 89.9%. Their absolute median gap rises from 16.2 to 53.8 percentage points. Fixed 2000 membership rules out changing cohort labels as the source of widening; overlapping endpoint dots retain individual exceptions.

This is an absolute percentage-point comparison. Bounded adoption and different positions on an S-shaped diffusion path can widen absolute gaps during a transition even while relative measures fall. High-start countries have less remaining headroom. The chart establishes broad progress without absolute median catch-up over this interval; it does not establish that every definition of inequality worsens.''',
14:'''Europe's regional median ends at 86.86%, Africa's at 31.89%, and Oceania's at 53.71% (53.7% rounded, matching the 2020 median in Figure 16). The fixed 50% reference makes crossing time and endpoint level comparable; red means below majority access, not decline.

Each row is one regional median, so the roughly 55-point Europe-Africa endpoint gap compresses the variation among their countries. Fixed classified-country membership prevents changing coverage from creating the trajectories. Enlarging the regional horizon makes the endpoint labels readable; the regional ridgelines then recover the spread around each median.''',
17:'''A/B/F encode the same August 22 absolute temperatures: continuous viridis, 5-degree cividis bands and a turbo baseline change visual emphasis without changing values. C/D similarly compare linear and logarithmic rainfall; zero rain is masked only for the logarithm. Ordered absolute magnitudes suit sequential palettes [7].

E deliberately changes the quantity to each cell's daily Tmax minus its own July-September mean. Zero now separates warmer/cooler departures, justifying symmetric RdBu_r. It is a within-period reference, not a climate normal. Keeping the quantity and normalization explicit prevents reading palette-induced contrast as additional physical structure; turbo hues have no extra measurement meaning.''',
19:'''The submitted code now includes an independent 16-case Marching Squares implementation: four corner bits classify each fully valid quad; linear interpolation locates edge crossings; saddle cases use the corner-mean center. Exact-level values count as below. The bottom diagrams expose all cases, including the ambiguous patterns [6].

The custom lines match ContourPy serial at 25, 30, 35 and 40 C to 1e-8 degrees on the actual August 22 grid; 32 synthetic case/center checks also pass. The overlay shows agreement. Custom line tracing supports exact threshold inspection; ContourPy fills organize broad temperature bands and masked boundaries. Five- versus ten-degree bands change display detail, not source resolution. The code and machine-readable comparison are supplied.''',
21:'''A/B use the same symmetric color limits for complete-month and endpoint changes. Monthly September-minus-July means cool over 99.66% of weighted area, with mean change -4.64 C. C directly marks the 18.26% where September 30 minus July 1 has the opposite sign. D shows how monthly cooling varies across longitude sectors.

Thus the endpoint discrepancy is now visible rather than only stated. Two selected weather states can misrepresent the direction of complete-month change at a location. Comparing matched footprints and a zero-centered diverging scale separates this sampling effect from a color-scale change; the cumulative curves prevent one area mean from concealing spatial variation.''',
22:'''On July 27, the western sector's weighted Tmax mean is 31.193 C and its spatial p10-p90 range is 23.75-39.25 C. The central mean is 35.36 C with range 31.39-38.35 C. The western daily value is distinct from July's all-area mean, 31.192 C: both round to 31.19, a numerical coincidence verified from the cache.

Solid lines show spatial medians, dashed lines weighted means, and ribbons spatial p10-p90. Fixed sector memberships are 4,910/4,828/3,678 cells. Their different ribbon widths show why similar summary trajectories need not imply similar conditions across places. The ribbons describe spatial spread, not uncertainty around a mean.''',
23:'''July and August have similar weighted rain totals, 75.26 and 75.82 mm, but different timing. Among cells with monthly total at least 10 mm, 43.8% of eligible July area gets at least half its rain in one five-day window, versus 67.5% in August and 77.6% in September. September's total is lower, 57.08 mm.

The minimum-total mask avoids ratios dominated by tiny denominators; eligible footprints differ (74.75%, 92.32%, 94.09%). Concentration also depends on wet-day count: a cell with few rain days can have a large five-day share without a sustained episode. Read the ratio with totals and daily timing, rather than interpreting it directly as event duration or hazard.''',
25:'''This Hovmoller-style display retains daily time-longitude structure [11]. Time is horizontal and longitude vertical; A locates the 30-45 N averaging band. B subtracts each longitude's own 92-day mean Tmax, removing the fixed east-west baseline so within-period warm/cool departures are visible. The reference is not a long-term climate normal.

C's largest latitude-weighted rain mean is 95.20 mm/day on September 16 at 67.27 W. It averages only two valid coastal cells, with 94.10 and 96.30 mm/day; the units are verified, not square-root millimeters. Only color spacing is square-root transformed. D exposes longitude support (1-60 cells). Sparse support can preserve local extremes; these aggregate streaks do not track individual storms.''',
26:'''Two readable sampling densities now compare every fourth and twelfth display cell on the same August 22 western-US field. Larger speed-proportional arrows retain a 5 m/s key; equal-length arrows prioritize direction while color still encodes speed. Dense sampling can overlap; sparse sampling removes locations rather than smoothing the field.

The required variables are `vs` (10 m speed) and `th` (10 m FROM-direction). After angle conversion to radians, u=-vs*sin(th), v=-vs*cos(th) gives flow-TO components. Display bearings account for longitude scale and map aspect. The comparison isolates symbol density and length encoding; it cannot reveal finer wind resolution or trajectories absent from the data [1].''',
27:'''July's largest source-direction sector is southwest, shifting toward south in August/September. All roses use the same 14% outer limit; ring values are stated outside the bars so labels no longer cover measurements. Stacked colors show how speed classes contribute to each directional frequency.

Each percentage uses weighted grid-cell days in that month, not just days at one station. Equal radial scales make the seasonal shift comparable, while the common legend prevents color reinterpretation. This pooled direction distribution complements the quiver maps: it reveals frequency changes but deliberately gives up exact location.''',
31:'''Among 454 pairs whose adoption differs by at most one percentage point, only 71 (15.6%) meet the full-profile P95 cutoff. The histogram's horizontal distance uses only standardized landline, broadband and mobile gaps; the pass/fail color uses the network's four-indicator similarity, including adoption. The definitions differ deliberately because the question conditions on nearly equal adoption.

The three examples span minimum, middle-ranked and maximum infrastructure distance. Bhutan/Turkey differ by 0.82 adoption points but 19.0 broadband subscriptions per 100; Kuwait/Monaco show much larger infrastructure gaps despite a 0.54-point adoption gap. Raw gap labels and standardized colors separate absolute size from relative unusualness. Similar headline rates therefore do not establish similar full profiles.'''
}

def apply(figures):
    for f in figures:
        aid=f['analysis_id']
        if aid in DETAIL:f['detailed_interpretation']=DETAIL[aid]
        # Keep the complete source reading guide, but centralize routine caveats
        # in the PDF Scope paragraph rather than repeating them in each block.
        if aid in {4,5,6,7}:f['explanation'][1]='Cohort: the same 175 countries complete in both 2015 and 2020; four other 2020-complete countries lack complete 2015 profiles. '+f['explanation'][1]
        if aid in {1,31}:f['explanation'][1]='Cohort: 179 complete four-indicator profiles in 2020; no 2015 completeness is required. '+f['explanation'][1]
        if aid==3:f['explanation'][1]='Left: six aggregate community nodes, sized by country count, with between-community edge counts. Right: the selected 15-country adjacency matrix, ordered by descending internal degree. Teal means above cutoff, white below, gray self-pair.'
        if aid==19:f['explanation'][1]='A: independent line tracing. B: custom/ContourPy 35 C overlay. C/D: five-/ten-degree filled bands. Bottom: all 16 corner cases; orange corners are above threshold. The same fully valid quads and linear interpolation support the comparison.'
        if aid==21:f['explanation'][1]='A: complete-month difference; B: September 30 minus July 1, with the same zero-centered limits. C: orange marks opposite signs. D: area-weighted cumulative distributions of monthly changes by longitude sector.'
        if aid==25:f['explanation'][1]='A identifies the fixed 30-45 N band. In B/C, horizontal position is date and vertical position longitude. B shows departure from each longitude\'s own period mean; C shows actual rain with square-root color spacing. D gives the contributing-cell count.'
        if aid==26:f['explanation'][1]='Columns sample every fourth/twelfth point of the already stride-six cache. Upper arrows have speed-proportional lengths; lower arrows have equal lengths. Color shows speed in both rows; keys identify the upper physical scale.'
        if aid==31:f['caption']='Nearly equal adoption, differing infrastructure. Histogram distance uses three infrastructure indicators; color tests the full four-indicator P95 rule.'
        if aid==19:f['caption']='Custom Marching Squares, ContourPy agreement and filled-band comparison on the same grid.'
        if aid==25:f['title']='Hovmoller diagrams: daily departures and rain across longitude.'
        if aid==3:f['title']='Community links and degree-ordered pair detail.'
        if aid==26:f['title']='Quiver: readable sampling and arrow-length comparisons.'
        # Figure references here use stable analysis IDs and are remapped later.
    return figures

def configure(editorial,content):
    content.DATA=content.DATA.replace('Perturbation was mentioned as an option; P95 is our team\'s choice.','P95 is our team\'s choice.')
    content.JS='''NetworkX [3] computes the three layouts; D3 [4] implements layout/threshold selection, node filters, PCP bundling/brushing/reordering and treemap zoom/hierarchy/partition controls. Gephi [5] is an allowed alternative, not a required additional tool. The first-page dashboard link opens the working browser UIs; `images/gui/` and the interaction receipt provide local evidence. Open `web/home.html` through `python run_visualizations.py` to exercise the controls locally. The README documents setup, reproduction and browser checks.'''
    editorial.REPRO='''The submission README documents software, source inputs, preprocessing and staged commands. `python scripts/submission_workflow.py --stage all` rebuilds numerical inputs, Python plots and the report using the supplied browser exports. The optional Playwright route recaptures the treemaps. Raw country extracts, weather-cache acquisition code/metadata, numerical tables, custom contour source/tests, numbered images and editable LaTeX are included. No GitHub publishing is needed.'''
    editorial.DISCUSSION=editorial.DISCUSSION.replace('Together the comparisons recover within-group differences, histories and daily order hidden by aggregation. These descriptive results concern the stated countries, grid and period; they do not establish causes, universal country types or a climate trend.','Feature sensitivity limits the country grouping: omitting one indicator gives edge Jaccard overlap only 0.338-0.512, despite much higher small-noise stability. The selected metric is an explicit descriptive definition, not a unique set of natural country groups. Together the comparisons recover within-group differences, histories and daily order hidden by aggregation.')

    editorial.DISCUSSION="""Country averages conceal profile differences (71 of 454 nearly equal-adoption pairs meet P95), different paired paths, and the 47% within-region variation. Broadband association weakens from 0.83 for levels to 0.05 for gains, with ceiling/diffusion effects limiting interpretation. Layouts preserve edges while changing crossing costs; omitting one indicator gives Jaccard 0.338-0.512, exposing feature sensitivity despite small-noise stability.

Weather comparisons recover different omitted details: endpoint signs disagree with monthly means over 18.26% of area; totals conceal concentrated rainfall; equal 75-day event counts produce 17- versus 67-day runs. Separate field frequencies also fail to recover the 2.57% joint occurrence. These findings answer the main question through profiles, matched change and daily order."""
    editorial.REPRO="""The README supplies setup and staged reproduction commands. Source country extracts, weather caches/acquisition metadata, custom contour code/tests, numbered images and editable LaTeX are included. The local launcher opens the UIs; optional Playwright commands regenerate browser exports and complete captures."""
