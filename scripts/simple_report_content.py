"""Short, plain-English report copy and compact figure descriptions."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

INTRO='''**Main question: What do averages and snapshots hide about inequality, relationships and change over time?**

We study internet use across countries and, separately, daily weather in the United States. An average can hide large differences between countries or places. A single date can hide how those differences developed. We use several views of the same data to show what each summary leaves out. The internet and weather datasets are not joined.'''

DATA='''**Internet data.** We reuse the A1 OWID/ITU country data. We check duplicate country-year rows, join the indicators by country code and year, remove regional and world totals, and keep missing values as missing. Internet use is a percentage of people. Phone and broadband values count subscriptions per 100 people. They do not count unique users. The network uses 179 countries with all four 2020 indicators. We standardize the indicators and join each country to its five closest matches, giving 590 undirected links. NodeTrix groups the graph using weighted greedy modularity, which favors more links inside groups and fewer between groups. The 2015–2020 comparisons use the same 175 countries; the treemaps use 184 countries. The 2000–2020 views use 159 countries with a value in every year.

**Weather data.** We use gridMET daily maximum temperature, rain, wind speed and wind direction from July 1 to September 30, 2023. We read every sixth grid cell, mask missing values and convert source temperatures from Kelvin to Celsius. Eight dates, spaced 13 days apart, cover the interval evenly for the required GIFs. Full-period summaries use all 92 days and the same 13,416 valid cells. Area summaries use latitude weights. Hot means at least 35°C; dry means less than 1 mm of rain per day; windy means at least 5 m/s. Rain totals add daily rain. Wind arrows point toward the direction of flow.'''

JS='''The browser pages provide the required interactions. Parallel coordinates use JavaScript for bundling, brushing and axis reordering. D3 provides treemap zooming and the network controls; NetworkX supplies three network layouts. Run `python run_visualizations.py` from the submitted folder to open the launcher. Figure 1 compares the network layouts, Figures 4-5 show parallel coordinates, Figures 8-9 show the treemap hierarchies, Figures 13-14 show horizon plots, and Figures 15-16 show ridgelines. The README gives the browser controls and file paths.'''

DISCUSSION='''**What the internet views add.** Figure 1 shows why distance in a network drawing can mislead: the links stay the same as the layout changes. NodeTrix makes individual links inside a group visible. The six-country parallel-coordinate view is easier to trace than the full overview. In 126 of 175 countries, internet use rose while landline subscriptions fell. This shows that these measures can move in different directions; it does not explain why.

**What averages hide.** Countries within one region can have very different levels of internet use. About 47% of the measured 2020 country spread lies within regions. Also, a change in a regional median is not the same as the median of the countries’ own changes. For Asia, these are 26.55 and 19.75 percentage points. The yearly paths, horizons and ridgelines show who improved early, late or unevenly.

**What weather summaries hide.** Monthly maps show the broad seasonal change, but daily views show short events. For September, 77.6% of eligible area received at least half its monthly rain within five consecutive days. Hot and dry conditions covered 16.27% of weighted grid-cell days, while the longest local hot-dry run lasted 67 days. Adding the wind condition reduces the shared occurrence to 2.57%. Frequency, timing and uninterrupted duration answer different questions.

These findings describe the countries, places and dates included here. National data cannot prove causes. Three months of weather cannot establish a long-term climate trend.'''

REPRO='''The README lists the steps to rebuild the results, run the browser pages and compile the report. The submission includes source data, scripts, full-resolution figures, interactive pages and three eight-frame GIFs. A separate recording guide gives the video narration and screen actions. Each member’s assigned work is listed below.'''

CONCLUSION='''Averages hide differences within groups. Snapshots hide the paths and short events behind the final values. Separate measures can hide how often conditions occur together. Using several clear views of the same data helps answer these questions without treating a visual pattern as proof of a cause.'''

# title, question, reading guide, finding, short qualification, takeaway
COPY={
1:('Same links, different network layouts','Do the neighbors change when the layout changes?',
'India is dark blue. Each colored line joins it to one of the same six countries. Gray points and lines show the rest of the network. Match a line’s color across the three layouts.',
'India keeps the same six linked countries in Spring, Spectral and Circular layouts. The circular layout stretches some lines and places linked countries farther apart. This changes the drawing, not the list of neighbors. Here, “neighbor” means directly joined by an edge; it does not mean nearest on the page.',
'Line length in these layouts has no indicator unit. The links show similar country measurements, not physical cables.',
'Check the connecting lines, not the distance between points.'),
2:('Different country paths to higher internet use','Can internet use rise without a similar rise in fixed broadband?',
'Each panel follows one country from 2010 to 2020. Open dots mark 2010 and dark dots mark 2020. Small dots show the intervening years. All panels use the same axes.',
'South Africa’s internet use rose by 48.1 percentage points while fixed broadband rose by 0.7 subscriptions per 100 people. China gained 35.8 points in internet use and 24.6 broadband subscriptions per 100. A single 2020 value would hide these different paths.',
'These six examples illustrate different paths. They do not represent every country or prove what caused the change.',
'A final value does not show the path a country took.'),
3:('NodeTrix: look inside a country group','Which links are hidden inside a crowded group?',
'The left view replaces each country group with a small matrix. Gray lines join different groups. The right view enlarges group 7: a teal cell means the row country is linked to the column country. White means no link. The gray diagonal compares each country with itself.',
'The graph has 525 links inside its seven groups and 65 between groups. Group 7 contains eight countries and 18 of the 28 possible internal links. Filled rows show which countries connect to many others inside this group. Gaps show the pairs that are not linked. The mirrored pattern appears because each undirected link is shown twice.',
'Groups come from the chosen similarity rule. A dense block does not prove a natural or causal country category.',
'Matrix cells make individual links and missing links visible.'),
4:('Six selected countries: straight parallel coordinates','Which country measurements are hidden by the full overview?',
'Only six countries are shown. Follow a country’s named line across four axes. The dots give its internet-use rate and landline, broadband and mobile subscriptions per 100 people. Each axis has its own units and range.',
'All six countries have at least 70% internet use but no more than five fixed broadband subscriptions per 100 people in 2020. Their landline and mobile values still differ. Showing this small selection makes the individual values easier to follow than 175 overlapping lines.',
'The full 175-country view remains in the browser. The report uses ranges suited to this six-country selection.',
'A small, named selection makes the four measurements easier to compare.'),
5:('The same six countries with bundled lines','What does bundling change?',
'The countries, dots, colors and axis ranges are identical to Figure 4. The lines now bend partway toward the regional centers of the selected countries, using 50% bundling. The browser uses this rule for the same selection.',
'The connecting curves change, but all measured dots stay in the same places. Bundling can help follow a regional pattern. It can also bring lines together between axes even when the countries have different values. Read the dots for exact measurements.',
'A curve between two axes is drawing geometry, not a new observation or a change through time.',
'Bundling changes the paths between measured values; it does not change the values.'),
6:('Internet use, fixed broadband and mobile subscriptions','Which measurements tend to be high in the same countries?',
'The left panel compares internet use with fixed broadband; the right compares it with mobile subscriptions. The same 175 countries appear in both. Each dot is a country. Three examples are named. The internet-use axis is shared; both horizontal axes count subscriptions per 100 people.',
'Countries with more fixed broadband usually also have higher internet use. The rank-correlation score is 0.831 for broadband and 0.531 for mobile; a score closer to 1 means a stronger upward pattern. Some countries still differ from this pattern. This one-year comparison cannot show whether adding broadband raised internet use.',
'These are national comparisons for one year. The next figure examines changes between two years.',
'An overall relationship can hide individual country exceptions.'),
7:('Internet use rose while landlines fell','How common is this combination of changes?',
'A bar counts countries where internet use increased and landline subscriptions per 100 people decreased between 2015 and 2020. Labels show the count, group size and percentage. All bars use the same percentage scale.',
'This combination occurs in 126 of the 175 matched countries, or 72%. The regional counts are 30/46 in Africa, 27/41 in Asia, 35/43 in Europe, 15/23 in North America, 10/11 in South America and 7/8 in Oceania. The regional bars show that the pattern is widespread, while the exact share differs between groups.',
'The bars count directions of change, not their size. They do not show that one technology replaced another.',
'More internet use does not always come with more landline subscriptions.'),
8:('Internet users grouped by region','Where are the included internet users concentrated?',
'Large rectangles are regions; smaller country rectangles sit inside them. Area shows the number of internet users. Country color shows the percentage of people online. Group headers show each region’s share of the included total.',
'Asia accounts for about 56.9% of the 4.52 billion included internet users, compared with 14.0% in Europe. China and India occupy large areas because they have many internet users. Their different colors show that large user counts do not necessarily mean the same adoption rate.',
'The total covers 184 countries with both required values. It is not a complete count for every country in the world.',
'User counts and the percentage online answer different questions.'),
9:('The same users grouped by adoption band','Does changing the hierarchy change the comparison?',
'This treemap uses the same 184 countries and total as Figure 8. It first groups countries by internet-use band, then by region. Area still shows user count and country color still shows internet use.',
'Countries in the 50–below-75% band contain about 39.7% of included users. Countries in the 75–100% band contain about 38.1%. A large share of online users therefore lives in countries where many people are still offline. Changing the grouping makes this visible without changing any country measurement.',
'Adoption bands are chosen categories. The browser lets the reader zoom in and inspect exact country values.',
'Changing the grouping reveals a different feature of the same data.'),
10:('When countries first reach 50% and 75% internet use','Do countries reach the same milestones at the same time?',
'Each panel follows the same set of countries within one region. A step rises when a country is first observed at or above 50% internet use, or at or above 75%. The two colors show these two thresholds.',
'By 2020, 86.5% of the included European countries had reached 75% internet use, compared with 2.2% of the African countries. The steps show early and late progress that one regional average would hide. This uses 158 countries with known regions and complete annual values.',
'A country stays counted after its first crossing, even if use later falls. The threshold may have been crossed before 2000 or after 2020.',
'A shared average can hide very different times of arrival.'),
11:('Country differences inside each region','How much country variation does a regional average leave hidden?',
'Each dot shows one country’s 2020 internet-use rate. A dark tick marks the regional average. The bar on the right divides the total spread into differences within regions and differences between regional averages.',
'About 47% of the measured country spread lies within regions; about 53% lies between regional averages. Countries in Asia, Africa and North America cover wide ranges. Knowing a country’s region therefore gives only part of the picture. The dots show the countries that an average would hide.',
'The split uses variance, a measure of spread, for 158 countries with known regions. Each country has equal weight.',
'A regional label leaves nearly half of the measured country differences hidden.'),
12:('Regional change and individual country gains','Does the change in a regional median describe a typical country’s gain?',
'The left panel shows 2015 and 2020 regional medians. The right panel shows each country’s own gain. A thick line marks the middle half of gains; the open circle is the median gain. The black tick repeats the shift in the regional median.',
'Asia’s regional median rises by 26.55 percentage points, but its median individual country gain is 19.75 points. South America’s regional-median shift is 16.54 points, while its median country gain is 21.76 points. These are different calculations and can even give different regional rankings.',
'The spread lines describe variation between country gains. They are not confidence intervals.',
'A change in a regional summary is not the same as the typical country’s change.'),
13:('Country horizon plots','Which countries reach majority internet use early or late?',
'Each row follows one selected country from 2000 to 2020. Red means below 50% internet use and blue means above it. Darker bands mean a larger distance from 50%. Right labels show the 2020 value and first observed 50% year.',
'Singapore first reaches 50% in 2003, China in 2015, and Namibia in 2020. Tanzania remains below 50% at the end. The rows show timing that would be lost in a 2020 snapshot. Two countries are chosen from each classified region using its 2020 lower and upper quartiles.',
'Red means below the reference level, not falling internet use. A first crossing need not be permanent.',
'Countries can end with higher internet use after very different journeys.'),
14:('Regional median horizon plots','Do regional medians reach majority use at similar times?',
'Each row shows the yearly median internet-use rate for one region. The 50% reference and band colors match Figure 13. The same countries are used in every year.',
'Europe reaches majority use earlier than the other regional medians. Its 2020 median is 86.86%, while Africa’s is 31.89%. Asia’s row shows a later crossing. These compact rows make the broad timing easy to compare, while Figure 11 shows the country differences hidden by each row.',
'A regional median gives every included country equal weight; it does not describe every person in that region.',
'Regional progress differs in both timing and final level.'),
15:('How the country distribution changed','Did all countries move toward similar internet use?',
'Each ridge shows the distribution of internet use across the same 159 countries in one year. All ridges share the 0–100% scale. Small ticks show countries, and right labels give the median.',
'The median rises from 2.2% in 2000 to 71.4% in 2020. Early values sit near zero; later values cover much of the scale. The rightward shift shows broad progress, but the wide 2020 distribution shows that countries have not all reached similar levels.',
'Curves use a reflected Gaussian density with a six-percentage-point bandwidth. Each ridge is scaled separately for shape.',
'Internet use increased widely, while large country differences remained.'),
16:('How distributions changed within regions','Which regional differences are hidden by the whole-panel distribution?',
'Each panel repeats the ridgeline view within one region for 2000, 2005, 2010, 2015 and 2020. All panels use the same internet-use scale. Country ticks and median labels help check the smooth curves.',
'Europe’s ridges move toward high internet use earlier. Africa’s later ridges still cover low and middle values. Asia has a broad spread before moving farther right. Oceania has only eight included countries, so the individual ticks are especially useful there.',
'Small groups can produce bumps that are not stable patterns. Curve height is not a country count.',
'The global shift contains different regional paths and spreads.'),
17:('How color choices change the view','What changes when the same field uses a different color mapping?',
'The panels keep the weather field and date fixed. All four palettes are sequential colormaps: their colors progress from lower to higher values. Temperature uses continuous viridis and cividis split into 5°C bands. Rain uses Blues with a linear scale and magma with a logarithmic scale. Palette choice and scale normalization are separate choices. Read each color bar before comparing the maps.',
'Most rain values are small and a few are large. A linear scale gives the large values most of the visible contrast. A logarithmic scale makes lighter rain easier to see. Changing a temperature palette also changes which boundaries stand out. The underlying measurements stay the same.',
'Zero rain is masked for logarithmic mapping. Color contrast by itself is not a change in the data.',
'The scale should match the question the map needs to answer.'),
18:('Fixed and daily color scales','Can the same color mean a different temperature?',
'The left column uses one temperature range across the eight sampled dates. The right column rescales each date to its own minimum and maximum. Both columns show the same fields.',
'Daily scaling makes local differences easier to see, but a bright color can represent different temperatures on different dates. A fixed scale supports comparisons across dates. Daily scaling supports comparison within one date. The GIFs repeat this comparison over all eight sampled fields.',
'The fixed limits come from the eight samples, not from all 92 days or a long-term climate record.',
'Use a fixed color scale when comparing temperature between dates.'),
19:('Contour intervals and filled contours','How much boundary detail does the contour interval show?',
'The same August 22 temperature field is drawn with 5°C and 10°C intervals, using lines and filled bands. Levels and color bars show the thresholds used.',
'Five-degree intervals show more boundaries than ten-degree intervals. Filled bands help compare larger warm and cool areas; line contours expose individual thresholds. Matplotlib/ContourPy traces the regular grid using the Marching Squares family of algorithms. This fits the two-dimensional grid and keeps missing cells masked.',
'More contour lines mean more displayed detail, not more observations or a changed field.',
'Contour spacing controls how much boundary detail the reader sees.'),
20:('Monthly temperature maps','How does the average daily maximum temperature change across the three months?',
'Each map averages daily maximum temperature over one month. All maps use the same Celsius scale and the same 25°C and 35°C contour levels.',
'The mean of daily maximum temperature falls from 31.19°C in July to 26.55°C in September over the weighted study area. Warm conditions remain visible in parts of the south. The fixed colors allow direct comparison, while the contours show where the stated temperature levels occur.',
'These are monthly averages of daily maxima, not monthly extremes or averages of every hourly temperature.',
'The fixed-scale maps show both the broad cooling and where warmth remains.'),
21:('Monthly change versus two selected dates','Can two daily snapshots describe a whole month’s change?',
'The map subtracts July’s mean daily maximum temperature from September’s. It uses the diverging colormap RdBu_r, with equal negative and positive limits centered on zero. Blue means cooling, red means warming, and the pale center means no change. The curves summarize changes across three longitude bands.',
'The area-weighted mean change is −4.64°C, and 99.66% of the study area is cooler. A comparison using only the first and last sampled days disagrees with this monthly result in sign over 18.26% of the area. Two dates can therefore give a different impression of the season.',
'The result describes this 2023 interval and sampled area; it is not a long-term climate trend.',
'Use complete months to compare months, rather than relying on two daily snapshots.'),
22:('Daily temperature and its spatial spread','What does a daily average hide about different places?',
'Each panel shows one longitude band across all 92 days. The dark line is its area-weighted mean daily maximum temperature. Nested ribbons show the middle half and the middle 80% of grid-cell temperatures.',
'The ribbons remain wide even when the average changes smoothly. Places within a band can therefore experience quite different temperatures on the same day. Warm and cool episodes are also visible within each month. A single monthly mean would hide both the daily timing and this spatial spread.',
'Ribbons describe differences across grid cells, not uncertainty around the mean.',
'A daily mean hides differences between places; a monthly mean also hides timing.'),
23:('Monthly rain totals and five-day bursts','Can similar monthly totals come from different rainfall timing?',
'The top row shows monthly rain totals on one scale. The bottom row shows the share of each month’s rain that falls in its wettest five consecutive days. Cells with less than 10 mm monthly rain are masked in the bottom row.',
'July and August have similar weighted mean totals, about 75 mm. The five-day comparison shows different timing. In September, 77.6% of eligible weighted area receives at least half its monthly rain in one five-day window, compared with 43.8% in July. A monthly total alone cannot show this concentration.',
'Windows stay inside each month. The eligible area differs by month, and this measure does not establish flooding.',
'The same monthly amount can arrive gradually or in a short burst.'),
24:('Where hot days are frequent','Where do daily maximum temperatures often reach 35°C?',
'Each map shows the percentage of days in a month with daily maximum temperature at least 35°C. The three maps share one 0–100% scale.',
'The weighted mean hot-day frequency falls from 22.8% in July to 8.9% in September. The maps show where frequent heat remains concentrated. Unlike one hot-day snapshot, this view counts every day in each month and separates repeated heat from a single selected event.',
'The 35°C threshold is a chosen study definition. Frequency alone does not show whether hot days form one continuous run.',
'Counting all days reveals where heat repeats.'),
25:('Daily weather across longitude','When and where do warm and rainy periods occur?',
'Time runs vertically and longitude horizontally. The top panel shows an area-weighted fixed-threshold heat summary. The other panels show temperature and rain averaged across latitude, retaining every day.',
'The diagrams reveal warm episodes and short rainy periods that monthly maps smooth over. Some temperature features extend across several longitudes, while rain is often more concentrated in time and location. The full-period view makes it easier to compare the timing of these patterns.',
'Averaging across latitude hides north–south differences. Reading across columns does not by itself track a moving storm.',
'Keeping all days exposes events hidden by monthly summaries.'),
26:('Wind-arrow density and length','How do sampling and arrow length affect readability?',
'The panels show the same western-US wind field with different sampling gaps. The top row scales arrow length by speed; the bottom row uses equal lengths. Color gives speed in both rows. Arrows point toward the flow direction.',
'Dense arrows retain more locations but can overlap. Wider sampling gaps make direction easier to read while omitting detail. Proportional lengths show speed as well as direction. Equal lengths make weak-wind directions more visible, so the color bar is needed to read speed.',
'These are daily wind values at 10 m, not gusts or paths followed by air parcels.',
'Arrow density and length should be chosen for the comparison the reader needs.'),
27:('Monthly wind-direction distributions','Does one pooled wind summary hide monthly differences?',
'Each rose groups a month’s grid-cell days by wind source direction. Stacked colors show speed ranges. The same radial scale gives the percentage of each month’s weighted grid-cell days.',
'The largest direction sector is southwest in July and south in August and September. The dominant source direction therefore changes across the interval. Speed colors add information that would be hidden by direction alone. The rose complements the quiver map: one summarizes frequency, while the other shows locations and directions.',
'Read radial height as frequency. Near-calm directions carry little physical meaning.',
'Separate monthly roses reveal changes hidden by one pooled wind distribution.'),
28:('Temperature, rain and wind on the same dates','Can separate weather summaries hide where conditions occur together?',
'Both maps combine temperature color, rain contours and wind arrows. They show July 27 and September 30 on shared scales so the fields can be read at the same locations.',
'These dates contrast high and low hot-dry coverage: 34.56% and 1.75% of the study area. Combining the fields shows where warm areas, rainfall boundaries and wind directions lie together. Separate area averages would not identify those locations.',
'The dates were selected for this contrast. Co-location in a daily map does not prove a causal link or hourly coincidence.',
'Aligned fields preserve location information that separate averages hide.'),
29:('Separate frequencies and shared occurrence','How often do hot, dry and windy conditions occur together?',
'The first three bars count hot, dry and windy grid-cell days separately. The orange bar requires all three conditions in the same grid cell on the same day. All bars use the same weighted percentage scale.',
'Dry conditions are common, but all three conditions occur together in only 2.57% of weighted grid-cell days. The shared frequency cannot be read from any single condition’s bar. Checking the conditions together adds information that their separate frequencies leave out.',
'The first three bars overlap and must not be added. These percentages describe weighted grid-cell days, not people.',
'Common separate conditions can have a much smaller shared occurrence.'),
30:('How often conditions occur and how long they last','Does the event count describe uninterrupted duration?',
'The maps compare hot-dry day frequency and the longest hot-dry run at each cell. The daily curve shows area coverage. The final panel repeats the calculation under alternative thresholds.',
'Hot-dry conditions cover 16.27% of weighted grid-cell days, but the longest local run reaches 67 consecutive days. The frequency and run-length maps therefore answer different questions. The threshold comparison shows that the chosen definition also changes the measured amount of overlap.',
'A run may start before or end after the study window. These daily thresholds do not diagnose drought or a heatwave.',
'A count says how often; a run length says how long without a break.'),
}

def apply(figures):
    metrics=json.loads((ROOT/'output/simple_revision/metrics.json').read_text())
    paths={1:'network_explained',3:'nodetrix_detail',4:'pcp_six_straight',5:'pcp_six_bundled',6:'pairwise_simple',7:'country_changes_simple',11:'within_regions',29:'weather_overlap_simple'}
    for f in figures:
        n=f['figure'];title,q,read,result,note,take=COPY[n]
        f.update(title=title+'.',caption=result,explanation=[q,read,'This view answers the stated question using the same measured data.',note,take],detailed_interpretation=result)
        if n in paths:f.update(path=f'output/simple_revision/{paths[n]}.png',chart_export=True)
        if n==3:f['extension_key']='nodetrix_detail'
        if n==11:f['extension_key']='within_regions'
        if n==29:f['extension_key']='weather_overlap_simple'
    return figures

def configure(module):
    module.INTRO=INTRO;module.DATA=DATA;module.JS=JS;module.DISCUSSION=DISCUSSION;module.REPRO=REPRO;module.CONCLUSION=CONCLUSION
    titles=['Country links and country paths','Internet measurements and changes','Timing and differences between countries','Color and contour choices','Weather over the full three months','Wind direction and speed','Shared conditions and long runs','Companion figures']
    leads=['We first compare the country network, individual paths and the links inside one group.',
      'We first compare changes across four measures, then inspect endpoint profiles, associations and two ways to group internet users.',
      'Fixed starting groups and yearly views show who progresses and what country and regional summaries leave hidden.',
      'These experiments keep the data fixed while changing the way it is drawn.',
      'Complete daily records reveal changes and short events hidden by selected dates or monthly totals.',
      'Maps show wind at specific locations; monthly roses summarize direction and speed across the area.',
      'We compare individual conditions, their shared occurrence and uninterrupted duration.',
      'The companion gallery contains the full country overview, group profiles, earlier inequality analysis and other supporting checks.']
    module.SECTIONS=[(('Appendix: '+title) if i==7 else title,ids,leads[i]) for i,(title,(_,ids,_)) in enumerate(zip(titles,module.SECTIONS))]
    module.REFERENCES=[]
