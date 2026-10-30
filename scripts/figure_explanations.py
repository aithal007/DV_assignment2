"""Figure-specific reading guides for the IEEE report; findings come from REPORT.md."""

# Each tuple is: analytical question, encodings, design rationale, reading guidance,
# and main takeaway. Numeric findings remain in the audited report captions.
EXPLANATIONS = {
1: (
"How much of a country similarity graph's apparent structure comes from its layout?",
"Each point is one country with complete 2020 values for four connectivity indicators. Color gives its supplied region; a link joins countries selected by the standardized five-nearest-neighbor rule. The three panels use identical nodes and edges, but spring, spectral and circular algorithms assign different drawing positions.",
"Holding the graph fixed makes layout the controlled variable. Spring placement emphasizes local neighborhoods, spectral placement provides an ordering from graph structure, and the circle supplies a deliberately constrained baseline. Agreement across layouts is stronger evidence than proximity in only one drawing.",
"Trace a country and its links across all three panels before calling an apparent group meaningful. A node's coordinates have no geographic or indicator units. Crossings in the circular view reflect placement; they are not additional connections. Regional colors permit comparison with supplied labels rather than proving discovered communities.",
"Layout changes readability and apparent neighborhoods while the measured graph remains unchanged."),
2: (
"Can an apparent country neighborhood be inspected rather than inferred from a crowded picture?",
"The screenshot records one state of the interactive explorer. Nodes and regional colors have the same meanings as Figure 1. Layout controls, similarity filtering, search, selection and neighbor highlighting change the view of the stored graph. Edge filtering removes displayed links, not the underlying observations.",
"Overview alone cannot resolve overlapping links. Interaction supports an overview-to-detail sequence: locate a country, select it, then inspect its connected neighbors and values. A threshold filter is useful for isolating stronger similarities, provided the reader knows the visible graph is now a subset.",
"Use the screenshot as evidence of the implemented controls, not as a substitute for exercising them. Verify a neighborhood against the underlying edge list. Changing the threshold can make a country look isolated even though it remains connected in the original graph. The PDF cannot reproduce hover, panning or a sequence of filter states.",
"Selection and filtering make similarity links inspectable; a static screenshot captures only one interaction state."),
3: (
"Which combinations of connectivity measures occur in the same countries?",
"Each polyline represents one of the 175 matched countries. Its intersections with the four vertical axes give internet adoption, fixed telephones, broadband and mobile subscriptions in their labeled units. Region determines color. The domains are fixed across the matched 2015 and 2020 comparison, rather than being stretched independently for each year.",
"Parallel coordinates retain four measured dimensions without reducing them to a composite score. Straight segments provide the baseline against which bundling can be judged. Fixed axes prevent a year-specific scale from making an unchanged value appear to move, and the matched panel prevents membership changes from creating apparent trends.",
"Read values at axis intersections, then follow the same line between neighboring axes. Slopes between axes with different units are not numerical rates of change. Crossings summarize relative ordering, but dense crossings can hide individual countries; brushing or selection is needed for a precise profile comparison.",
"Mobile subscription intensity and internet adoption can differ substantially within the same country."),
4: (
"Does moderate bundling help readers follow supplied regional groups?",
"The countries, indicator axes, domains and regional colors are identical to Figure 3. A 50% bundling setting bends the intermediate line segments toward a regional centroid. All measured intersections with the axes are preserved; intermediate curves are constructed drawing paths rather than extra observations.",
"The pair with Figure 3 is a controlled readability experiment. Bundling reduces visual disorder between axes and makes regional trajectories easier to follow, while the straight version provides a check on individual profiles. Moderate bundling balances group visibility against the risk that dense bundles hide within-group variation.",
"Compare the two plots at the axis intercepts to confirm that the measurements did not change. A shared curve between axes should not be read as evidence that countries have identical values. Because grouping uses existing region labels, bundle separation cannot be presented as an independently discovered clustering result.",
"Bundling clarifies supplied groups, but exact country measurements remain at the axis intercepts."),
5: (
"Where are included internet users concentrated within Asia?",
"A rectangle is a country leaf inside the World-to-region-to-country hierarchy. Rectangle area is proportional to the number of internet users, whereas sequential color represents the percentage of that country's population using the internet. The screenshot is zoomed into Asia; the breadcrumb records the current branch.",
"A treemap uses space efficiently to compare part-to-whole counts within a hierarchy. Area and color answer different questions: a populous country can contain many users without having the highest adoption share. Zooming makes smaller leaves inspectable and retains the parent context needed to understand what the areas sum to.",
"Read the parent total first, then inspect both size and color for a country. Large China and India rectangles describe user counts, not land area or universal access. The screenshot's regional total is a subset of the included-country total; neither should be silently substituted for a complete global estimate.",
"China and India dominate Asia's included user count, while adoption percentage remains a separate color measure."),
6: (
"What is Asia's composition inside the high-adoption group?",
"The remodeled hierarchy is World-to-adoption-band-to-region-to-country. Leaves still use internet-user counts for area and adoption share for color. The displayed branch is Asia within the analyst-defined 75-100% band; countries outside that band remain elsewhere in the hierarchy rather than being assigned new values.",
"Changing the parent structure changes the analytical question without changing leaf measurements. Compared with Figure 5's geographic view, the adoption-first view asks which regions and countries account for users inside a specified access group. The same leaf values make the comparison a hierarchy experiment rather than a different dataset.",
"Check the breadcrumb and parent total before comparing rectangle sizes. A country may be prominent in Asia's overall user count yet absent from this high-adoption branch. Percentile-like visual groupings should not be inferred: the four adoption bands are fixed percentage thresholds, not equal-sized country groups.",
"Hierarchy remodeling changes the question from regional totals to the composition of an adoption band."),
7: (
"How do selected countries approach or exceed majority internet use over time?",
"Each row follows one selected country's annual adoption from 2000 to 2020. The plotted quantity is adoption minus 50 percentage points. Two 25-point bands per side are mirrored and folded: red denotes below the reference and blue above it, with darker bands indicating greater distance. Time runs left to right.",
"Horizon layering compresses several time series into comparable rows while retaining timing and baseline crossings. The reproducible low/high quantile rule within each region makes the selection transparent. It illustrates contrasting trajectories rather than choosing only visually striking cases or claiming coverage of every country.",
"Read hue as the sign relative to 50%, saturation as distance, and changing shape as temporal movement. A red row can represent rising adoption that remains below 50%; red does not mean decline. For precise adoption values, return to the annual table or the unfurled construction in Figure 27.",
"Selected countries follow contrasting paths; horizon hue identifies baseline position, not the direction of change."),
8: (
"Do regional median trajectories cross the majority-use milestone at similar times?",
"Each row shows an annual median over a fixed set of countries in one classified region. Every included country has equal weight. The sign, two 25-point bands and 50% baseline match Figure 7, so a blue interval indicates that the regional country median exceeds majority use.",
"Aggregation removes individual line clutter and exposes differences in typical-country timing. Fixed regional membership keeps the same countries in each year's median. Pairing the regional view with selected-country rows reveals the tradeoff: medians are easier to compare, but they conceal spread and exceptional country paths.",
"Compare the timing of color changes, then inspect the reported 2020 medians. The regional statistic is not the share of all regional people who are online: large and small countries receive equal weight. A median below 50% also does not mean every included country in the region is below that threshold.",
"Europe's median crosses 50% earlier; Africa's included-country median remains below 50% in 2020."),
9: (
"How does the whole fixed panel's adoption distribution shift between selected years?",
"Horizontal position is adoption percentage on the common 0-100% scale. Each ridge estimates the distribution across the same 159 countries in one year using a reflected Gaussian kernel with bandwidth 6 percentage points. Ridge heights are separately normalized; ticks mark raw medians and year labels identify the slices.",
"A distribution view tests whether a rising central value is accompanied by narrowing or persistent spread. Boundary reflection reduces smoothing leakage beyond the meaningful percentage range. Fixed membership and shared horizontal limits make distribution shifts interpretable; the median ticks anchor the smoothed shapes to an unsmoothed statistic.",
"Compare where density is concentrated and how broadly each ridge extends, rather than comparing peak heights as counts. A higher median can coexist with countries at both ends of the scale. Small density bumps depend on smoothing and should be checked using Figure 28 before being described as distinct adoption groups.",
"The median rises sharply, but the broad 2020 distribution shows that progress is uneven across countries."),
10: (
"Which regional distribution shifts are hidden by the global ridgeline?",
"Each facet is a classified region, and each ridge is one of the same five annual slices. The adoption axis, kernel bandwidth, boundary treatment and median ticks match Figure 9. Country counts are fixed within region; ridge height remains independently normalized rather than representing the size of the region.",
"Faceting separates regional mixtures that can overlap in a pooled distribution. Keeping the same visual conventions permits a regional-to-global comparison without changing the smoothing method. Displayed sample sizes are essential because a visually complex ridge from a small panel can be driven by only a few countries.",
"Compare horizontal shifts within each facet and differences between regional medians. Do not compare filled area as regional population or numbers of users. Oceania and South America have particularly small country panels, so peaks there are fragile descriptive shapes; regional membership and missing-country coverage also limit generalization.",
"Regional facets reveal unequal adoption shifts that the pooled distribution can conceal."),
11: (
"How do eight temperature snapshots compare when one color scale is held fixed?",
"Each map is one selected daily maximum-temperature field; longitude and latitude locate the sampled cells. All eight panels share the same Celsius limits and sequential palette. Gray marks missing cells. Dates identify the eight uniformly selected snapshots, including both interval endpoints, rather than eight daily consecutive fields.",
"Small multiples preserve a stable spatial reference and allow direct visual comparison without waiting for an animation frame. A shared scale means a given color denotes the same temperature on every date. Uniform date selection avoids choosing only exceptional days, while the calendar in Figure 17 makes the remaining temporal gaps explicit.",
"Track the same location across dated panels and read its color against the common bar. The atlas can show broad spatial contrasts at the selected times, but it cannot establish how long an event lasted between snapshots. For monthly behavior, use the complete daily fields summarized in Figures 18-21.",
"Shared scales support date-to-date comparison; eight snapshots do not describe all 92 days."),
12: (
"How do palette classes and normalization alter the visibility of the same scalar fields?",
"The temperature pair compares a continuous sequential palette with fixed 5-degree classes. The rain pair compares linear and logarithmic positive-rain mapping for the same date. Gray is missing, white is dry, and the stated low-positive-rain category is distinct from zero. Color bars define units and limits, including saturation.",
"Separating palette and normalization experiments shows that visual contrast is a design choice. Continuous color retains gradual variation; classes simplify boundaries at the cost of within-class detail. A logarithmic rain scale expands small positive values that are compressed by a linear scale dominated by heavy-rain cells.",
"Compare identical locations within each variable's pair, not temperature colors against rainfall colors. Saturated rain cells cannot be ranked precisely from their shared endpoint color. The log experiment must not treat zero as a small positive amount; the separately encoded dry fraction prevents that mathematical and interpretive error.",
"Normalization changes which rainfall values are visible; discrete classes trade fine detail for simpler categories."),
13: (
"Is stronger within-day contrast compatible with reliable between-day color comparison?",
"The two columns compare one shared scale against a scale fitted to each displayed day's actual minimum and maximum. Each row uses the same date and field in both columns. The local color bars change by day; the shared limits are computed over the original eight-field sampled cube, not over the full 92-day cache.",
"This experiment isolates rescaling from the weather measurements. Global limits provide one numerical meaning for color, while local limits allocate the full palette to a smaller within-day range. Showing bars for every local panel makes the rescaling explicit rather than allowing a visually vivid image to imply hotter weather.",
"Compare spatial structure within a row, then inspect the bars before comparing colors between rows. A yellow local cell on a cooler date may have a lower temperature than a green cell on a warmer date. Changes in apparent intensity therefore cannot be used alone to establish warming or cooling.",
"Local scales improve within-date contrast but sacrifice a constant color meaning between dates."),
14: (
"How do contour interval and filling change the readability of temperature boundaries?",
"All four panels use the same daily maximum-temperature field. Columns change the contour interval from 5 to 10 degrees; rows change line contours to filled intervals. Geographic axes remain fixed. A contour line traces interpolated locations of equal temperature, while a filled band marks values between neighboring levels.",
"The controlled grid separates level spacing from line-versus-area encoding. Fine spacing exposes more structure but increases clutter; coarse spacing emphasizes broad zones and suppresses smaller changes. Filled contours support regional pattern reading, whereas lines preserve background context and make individual boundaries more prominent.",
"Read a boundary through its level or adjacent color intervals, rather than assuming every line represents an independent observation. The Marching Squares family traces transitions between available samples; smooth-looking boundaries do not recover omitted native cells. Identical sampling and extent make differences between panels drawing effects.",
"Fine contours expose detail; coarse filled bands make broad temperature regions easier to read."),
15: (
"Which arrow density and length encoding best reveal daily wind direction and magnitude?",
"Columns retain every fourth, eighth or twelfth display-grid cell; rows compare speed-proportional length with unit-length direction arrows. All panels share the same western extent and speed-color limits. Arrows show flow-to direction after conversion from the source's meteorological from-direction. Colors still show speed when lengths are equal.",
"A density-by-length grid makes two visual decisions independently testable. Dense arrows preserve more locations but can overlap; sparse arrows clarify orientation while omitting local detail. Equal lengths make weak-wind directions visible, and proportional lengths retain magnitude directly in the arrow geometry.",
"Compare density within a row and length convention within a column. A large equal-length arrow need not indicate strong wind; its color carries that information. Longitude/latitude display corrections address direction distortion, but the output grid's fine spacing does not overcome gridMET's coarser wind input resolution.",
"Arrow spacing controls clutter; equal lengths clarify direction and transfer magnitude reading to color."),
16: (
"Where do the two endpoint daily maximum-temperature fields differ?",
"Each valid cell shows September 30 minus July 1 temperature in degrees Celsius. A zero-centered diverging scale separates negative blue differences from positive red differences. Gray marks cells outside common valid coverage. The area summary uses cosine-latitude weights rather than counting every displayed cell as equal area.",
"A signed map answers a different question from two independent temperature maps: it directly locates increases and decreases. Centering at zero gives the palette a meaningful midpoint. Common coverage prevents missing cells on one endpoint from entering the comparison as artificial zero values.",
"Start with the sign of a difference, then its magnitude and geographic extent. The reported area fraction and weighted mean describe the sampled footprint. They compare two weather days separated by three months; they do not measure a climatological anomaly, the mean of the season, or the trend within intervening days.",
"Most common sampled area is cooler on the later endpoint, but this is a two-day weather comparison."),
17: (
"Are sparse animation dates the dataset's actual temporal resolution?",
"A calendar cell represents one date in July, August or September 2023. Blue fill denotes an available daily field; orange outlines mark the eight dates chosen for the original animations. Month titles state the 31, 31 and 30-day counts. Availability was checked separately for all four variable time axes and daily fields.",
"The calendar distinguishes data availability from presentation sampling using familiar month structure. Marking the sample dates on top of complete daily coverage explains why a reader of the GIF might notice only a few dates. This is a coverage audit rather than a plot of temperature or precipitation magnitude.",
"Count consecutive filled cells, then inspect the regular outline spacing. A filled cell means valid grid values exist that day, not that every geographic cell has data. The eight outlined dates are 13 days apart; the underlying 92 fields are daily. Missing geographic cells remain masked in subsequent weather figures.",
"The interval has 92 consecutive daily dates; eight animation samples are a presentation choice."),
18: (
"How much daily temperature variation and within-sector spatial spread do snapshots omit?",
"Time gives all 92 dates. Each facet is a declared longitude sector, with a shared temperature axis. The mean and median summarize daily maximum temperatures using approximate area weights; the ribbon spans the spatial 10th-90th percentiles within the same fixed valid footprint. The sectors are analyst-defined longitude bands.",
"Lines recover intervening daily fluctuations that the eight-date atlas cannot display. The ribbon adds spatial heterogeneity without plotting thousands of cell trajectories. A fixed footprint and cosine-latitude weighting reduce changes caused by coverage and unequal regular-grid cell areas; common axes preserve inter-sector comparability.",
"Read a daily central value together with its ribbon width. A broad ribbon indicates varied temperatures across that sector that day, not uncertainty in an estimated mean or a confidence interval. Mean-median separation can indicate asymmetry, but the chart alone cannot attribute weather changes to a particular physical mechanism.",
"Full daily trajectories reveal variation between snapshots, while ribbons show spatial spread rather than confidence."),
19: (
"How does each month's mean daily maximum temperature vary across the sampled area?",
"Each map averages every available daily maximum-temperature field at a cell within that month: 31, 31 or 30 daily values. All maps share one Celsius scale and the same 25- and 35-degree contour levels. Gray denotes missing coverage. These are monthly averages of daily maxima, not averages of all hourly temperatures.",
"Complete-month aggregation answers a sustained-pattern question rather than selecting one representative weather day. Shared color limits make the three averages comparable, while fixed isolines add numerical anchors independent of palette shade. The area summaries use approximate cell weights and are separate from the geographic display.",
"Compare the same locations and the extent of the fixed isotherms between months. A high monthly mean maximum does not specify how many individual days crossed a threshold; Figure 21 answers that frequency question. Without a multiyear normal, these maps also do not establish whether the months were unusually hot.",
"Monthly mean daily maxima decrease across this interval, with persistent spatial differences under a shared scale."),
20: (
"Where does total accumulated rainfall differ between the three complete months?",
"Each cell is the sum of its daily precipitation accumulations for all dates of that month. The common sequential scale is in millimeters and uses the actual monthly maximum without clipping. Any cell lacking complete monthly coverage is masked, rather than treating a missing daily value as zero rainfall.",
"Summing all daily fields matches the physical meaning of accumulated rainfall. Small multiples permit geographic comparison and preserve location, whereas a single regional mean would hide concentrated rainfall. One shared scale prevents independently stretched maps from making a drier month look as wet as a wetter month.",
"Read both the magnitude and distribution of totals. A monthly sum cannot show whether rainfall came from many light days or a few heavy days; Figure 23 examines the daily amount distribution. These are actual month totals, so September's 30-day duration should be considered when comparing it with the 31-day months.",
"Complete daily sums show lower area-mean accumulation in September; rainfall totals cannot be estimated from eight snapshots."),
21: (
"How often does daily maximum temperature reach the declared 35-degree threshold?",
"At each complete-coverage cell, qualifying days are counted and divided by that month's 31, 31 or 30 days. Maps share a 0-100% sequential frequency scale. Approximate area-day percentages summarize the footprint separately. The threshold is a descriptive analytical choice, not an official heatwave or exposure classification.",
"Frequency complements Figure 19's mean: the same average can arise from different daily patterns. Dividing by month length enables a fairer fraction comparison than raw counts. The bounded common color scale gives the same meaning to each shade and makes a zero-frequency cell different from missing coverage.",
"Interpret 50% as half the included days crossing the threshold at that cell, not half its population experiencing heat. The plot does not encode consecutive hot-day runs or nighttime conditions. Neither temporal persistence nor health risk can be inferred from this one daily-maximum threshold alone.",
"Hot-day frequency falls substantially in September, complementing the decline in monthly mean daily maxima."),
22: (
"Can compact horizon rows preserve the timing of daily temperature departures from 30 degrees?",
"Rows use the same 92-day sector mean series as Figure 18, centered by subtracting 30 degrees Celsius. Four 5-degree bands per side are mirrored and folded. Blue denotes above the reference, red below it; greater saturation gives larger departure. The baseline is declared for this descriptive comparison.",
"This weather variation applies the lecture's temporal compression method to daily rather than annual data. Folding keeps all three sector series compact and makes sign changes easy to scan. Figure 18 remains the unfurled numerical reference, allowing the compact representation to be checked against actual values and spatial spread.",
"Follow each row through time and compare the timing of sign changes. A darker red patch means farther below 30 degrees, not a negative absolute temperature or automatically a decreasing day-to-day trend. Horizon rows suppress exact vertical values, so narrow fluctuations should be checked in the ribbon chart.",
"Horizon rows compactly reveal when sector means sit above or below the declared temperature reference."),
23: (
"How do positive daily rainfall distributions compare, and how much dry-day information is excluded?",
"Horizontal position gives positive daily grid-cell precipitation in millimeters on a logarithmic scale. Vertical position gives the fraction of positive grid-day values at or below that amount. Month colors identify three unsmoothed ECDFs. Each legend reports the separately excluded fraction of valid grid-day values with zero rain.",
"An ECDF uses observed ranks directly and avoids choosing a density bandwidth or histogram bins. The log axis spreads the long rainfall range so light and heavy amounts can be inspected together. Conditioning on positive rain handles logarithmically invalid zeros explicitly, while the dry fractions restore information that conditioning removes.",
"At a chosen amount, the higher curve has a larger proportion of its positive observations below that amount. This says nothing by itself about total monthly rain or geographic location. Grid-day values have equal weight and are spatially dependent, so the curves are descriptive distributions rather than independent-sample statistical tests.",
"Rainfall ECDFs expose positive-amount distributions; the dry fractions are essential to interpret the conditioning."),
24: (
"From which directions do daily western-US winds most often originate?",
"Each polar sector is one of sixteen meteorological from-direction bins, with north at the top and clockwise angle. Stacked colors classify daily speed in meters per second. Total radial height is approximate area-day frequency among noncalm valid grid-day summaries; the three months share the same radial limits.",
"The rose preserves circular direction and jointly displays speed classes without treating 359 and 1 degrees as far apart. Fixed radial limits make month-to-month frequency comparisons possible. This view intentionally uses source from-directions, complementing Figure 15's flow-to arrows rather than silently reversing their interpretation.",
"Read angle as the direction of origin and radial height as frequency. Polar wedge area is not linearly proportional to that frequency. The box and noncalm denominator define the scope; daily gridded summaries cannot count hourly wind occurrences, and the chart is not a station-level observation rose.",
"Wind roses summarize monthly direction-and-speed patterns; direction of origin differs from quiver flow direction."),
25: (
"Can graph connections be verified without node-link crossings?",
"Both matrix axes list the same 179 countries in supplied-region then alphabetical order. A dark cell denotes a similarity edge; a light cell denotes no edge. Block boundaries mark region groups. Undirected edges appear symmetrically on both sides of the empty diagonal, so 590 edges produce 1,180 dark entries.",
"A matrix trades visible geometric neighborhoods for explicit pairwise lookup. Unlike a node-link view, it has no edge crossings; however, tracing multi-step paths is less immediate. Region ordering makes within- and between-region links inspectable, and the saved row/column order supports precise country lookup rather than guessing from blocks.",
"Check symmetry and the diagonal before interpreting group structure. Dark blocks arise partly from the chosen ordering, which uses supplied region labels. They are not discovered communities or significance tests. The within-region share describes edges in the similarity graph, not international network traffic or geographic infrastructure.",
"The adjacency matrix verifies actual edge structure and complements the three node-link layouts."),
26: (
"How much do regional adoption medians change on exactly the same country panel?",
"Each row is a fixed regional group from the 175 countries complete in both 2015 and 2020. Horizontal position gives median internet adoption percentage. Blue and orange endpoints identify the two years; the connecting segment and annotation give their difference in percentage points. Labels state country counts.",
"Paired endpoints make two-year shifts easier to compare than separate regional bar charts. Matched membership prevents missing or newly available countries from manufacturing a shift. The 0-100% axis keeps the percentage context visible, while explicit counts distinguish broad regional panels from small or unclassified groups.",
"Compare each row's endpoints, then inspect the labeled difference. The statistic is the difference of two group medians, not the median of paired individual-country changes. Unclassified groups retain missing region labels without pretending they form a geographical region. Equal-country weighting does not estimate population-weighted regional adoption.",
"All displayed medians rise; Asia has the largest shift among the classified regions on this matched panel."),
27: (
"How is a horizon plot constructed, and why can rising adoption still appear red?",
"Three vertically aligned panels use Kenya's same 21 annual observations. The first shows adoption percentage with a 50% reference; the second subtracts that reference and retains negative values; the third mirrors and folds two 25-percentage-point bands. Shared time alignment allows each stage to be checked against the original series.",
"A worked example exposes a transformation that can be difficult to infer from compressed rows alone. Using actual country values avoids a fabricated demonstration. Keeping the intermediate signed-deviation stage explains why hue retains the sign even after negative areas are mirrored upward and layered into one row.",
"Follow a year through the panels: subtract 50 from the measured adoption, determine its sign and band, then read the folded color. Kenya remains below 50% throughout this series, so a rising original line can remain red while the darker negative band shrinks. Folded height should not be read as absolute adoption.",
"Horizon red means below the reference, even when the original adoption series is rising."),
28: (
"Which apparent distribution features persist when the smoothing bandwidth changes?",
"The left panel smooths the same 159 adoption values for 2020 using reflected Gaussian bandwidths of 3, 6 and 12 percentage points. Density uses its actual units without peak normalization. The right panel plots the unsmoothed ECDF and the raw median on the same adoption domain.",
"A sensitivity comparison tests a key interpretive assumption behind the ridgelines. A narrow kernel can expose small bumps; a broad one suppresses them. The empirical curve and median provide references unaffected by bandwidth, separating changes in the drawing estimator from changes in measured country adoption.",
"Compare which bumps merge or disappear as bandwidth increases, then check the empirical cumulative curve. A feature visible only under one kernel setting is weak evidence for a stable group. These are country-weighted distributions; none of the curves estimates how the world's people are distributed across adoption levels.",
"Minor KDE peaks depend on smoothing; the empirical distribution and raw median provide stable references."),
}

assert set(EXPLANATIONS) == set(range(1,29))

# Current numbering follows the reviewed report manifest, not the historical 28.
from pathlib import Path
import json
_current = Path(__file__).resolve().parents[1] / 'data/current_figure_manifest.json'
if _current.exists():
    EXPLANATIONS = {f['figure']: tuple(f['explanation']) for f in json.loads(_current.read_text(encoding='utf-8'))}
