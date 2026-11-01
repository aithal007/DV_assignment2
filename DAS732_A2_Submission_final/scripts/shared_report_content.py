"""shared report content: interpretations, explanations, and plain copy."""
from __future__ import annotations

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]

# extended analytical detail keyed by figure number
detail: dict[int, str] = {
    2: (
        "The six panels do not follow one shared adoption-broadband path. South Africa "
        "gains 48.1 percentage points in internet use with only 0.7 additional "
        "fixed-broadband subscriptions per 100 people, whereas China gains 35.8 points "
        "with 24.6 additional subscriptions. India similarly gains 35.9 points with a "
        "broadband increase of 0.8. The vertical separation of their start/end markers "
        "and different horizontal displacements are the visible evidence.\n\n"
        "This answers the history part of the main question: an endpoint cannot identify "
        "the associated infrastructure trajectory."
    ),
    3: (
        "The overview has 699 links within six non-singleton modularity communities and "
        "98 between them. Afghanistan meets the cutoff with all 14 other members, whereas "
        "Angola meets it with seven. White cells are measured similarities below P95, "
        "not absent observations."
    ),
    4: (
        "Brushing adoption gains of 20-30 percentage points selects 39 of the 175 matched "
        "countries. Their lines span broadband changes from about -0.3 to +16.6, landlines "
        "from -14.8 to +7.1 and mobile from -80.2 to +34.5 subscriptions per 100 people. "
        "Georgia and Brunei both gain about 25 adoption points and around eight broadband "
        "subscriptions per 100. Yet Georgia's landline/mobile changes are -14.8/-12.0, "
        "while Brunei's are +5.2/+10.2."
    ),
    5: (
        "The high-adoption curves fan out strongly on fixed broadband. Kuwait has about "
        "99.1% internet use with 1.7 broadband subscriptions per 100 people; Kyrgyzstan "
        "has 72.0% with 4.3. Mobile values also overlap across the three adoption bands."
    ),
    6: (
        "The lower scatter cells show tighter upward ordering for broadband versus adoption "
        "(Spearman 0.83) than for mobile versus adoption (0.53). Landlines and broadband "
        "have the strongest displayed pairwise rank association, about 0.87."
    ),
    7: (
        "The strongest endpoint association weakens sharply when each country is paired "
        "across time: broadband-adoption rank correlation falls from about 0.83 in 2020 "
        "levels to 0.054 in 2015-2020 gains. Landline and mobile associations likewise "
        "weaken, from about 0.79 to 0.29 and 0.53 to 0.07."
    ),
    8: (
        "Asia occupies about 56.9% of the included internet-user total, compared with "
        "14.0% in Europe. China and India are large country rectangles because user counts "
        "are large; their colors differ because adoption percentages measure a separate "
        "quantity."
    ),
    9: (
        "The 50-below-75% band contains about 39.7% of included users, slightly more than "
        "the 38.1% in the 75-100% band. Thus a large share of online people live in "
        "countries where a substantial part of the population remains offline."
    ),
    10: (
        "All three cohorts move upward, but the lowest-starting group reaches a 2020 "
        "median of 36.1% while the highest reaches 89.9%. Their absolute median gap widens "
        "from 16.2 to 53.8 percentage points."
    ),
    11: (
        "Variance decomposition assigns about 47% of measured adoption variation to "
        "differences within regions and 53% to differences between their means."
    ),
    12: (
        "Asia's endpoint median shifts by 26.55 adoption points, but the median of its "
        "individual country gains is 19.75. South America reverses the comparison: its "
        "endpoint-median shift is 16.54 while its median country gain is 21.76."
    ),
    13: (
        "Singapore reaches 50% in 2003, Ireland in 2006, China in 2015, Peru in 2017 "
        "and Namibia in 2020; Tanzania and Micronesia have no observed crossing."
    ),
    14: (
        "Europe's regional median crosses 50% earlier and ends at 86.86%, while Africa "
        "ends at 31.89%."
    ),
    15: (
        "The median rises from 2.2% in 2000 to 71.4% in 2020. The 2020 middle half still "
        "spans about 37.5 percentage points."
    ),
    16: (
        "Europe's ridges move toward high adoption earlier, while later African ridges "
        "still occupy low and middle values. Asia's distributions remain broad."
    ),
    17: (
        "The temperature panels hold one field fixed while continuous viridis and 5-degree "
        "cividis bands emphasize different levels of detail. The rainfall panels hold values "
        "fixed: linear Blues allocates most contrast to large amounts, while logarithmic "
        "magma separates small positive amounts."
    ),
    18: (
        "The paired columns map identical daily fields using two parameter rules. Global "
        "normalization uses fixed bounds over eight frames; daily normalization recomputes "
        "bounds for each date. The fixed eight-date range is -1.85 to 49.65 C."
    ),
    19: (
        "The four panels use the same August 22 temperature grid. Five-degree levels "
        "produce more boundaries than ten-degree levels."
    ),
    20: (
        "Mean daily maximum temperature falls from 31.19 C in July to 26.55 C in September "
        "over the weighted common footprint."
    ),
    21: (
        "September-minus-July monthly means are negative over 99.66% of the weighted study "
        "area, with an overall change of -4.64 C."
    ),
    22: (
        "On July 27 the western sector has a weighted mean maximum temperature of 31.19 C, "
        "while its spatial 10th-90th percentile range is 23.75-39.25 C. The central sector "
        "mean is 35.36 C with a narrower 31.39-38.35 C range."
    ),
    23: (
        "July and August have close weighted totals, 75.26 and 75.82 mm, but their five-day "
        "concentration patterns differ. Among cells receiving at least 10 mm in the month, "
        "43.8% of eligible area in July receives at least half its rain within one five-day "
        "window; August reaches 67.5% and September 77.6%."
    ),
    24: (
        "The weighted mean frequency of Tmax >=35 C falls from 22.8% of July days to 8.9% "
        "of September days."
    ),
    25: (
        "The 92-day time-longitude panels retain short warm episodes and brief rain periods "
        "that monthly maps smooth away."
    ),
    26: (
        "All six panels use the same western-US field. vs maps to wind_speed and th to "
        "wind_from_direction. Source direction converts to flow-to components: "
        "u=-vs*sin(th) and v=-vs*cos(th)."
    ),
    27: (
        "The largest source-direction sector is southwest in July, then south in August "
        "and September."
    ),
    28: (
        "The objectively selected dates contrast hot-dry area coverage of 34.56% on July 27 "
        "and 1.75% on September 30."
    ),
    29: (
        "The separate bars give about 18.06% hot, 76.65% dry and 11.65% windy weighted "
        "cell-days. Their intersection is 2.57%."
    ),
    30: (
        "Hot-dry conditions occupy 16.27% of weighted grid-cell days, while the maximum "
        "local uninterrupted run reaches 67 days."
    ),
    31: (
        "Among 454 country pairs whose adoption rates differ by at most one percentage "
        "point, only 71 (15.6%) meet the full-profile P95 cutoff."
    ),
    32: (
        "Both selected cells have 75 qualifying days out of 92 (81.5%), yet the orange "
        "sequences form longest runs of 17 and 67 days."
    ),
}

DETAIL = detail

# reading guides
explanations: dict[int, tuple] = {}
_current = root / "data/current_figure_manifest.json"
if _current.exists():
    explanations = {
        f["figure"]: tuple(f["explanation"])
        for f in json.loads(_current.read_text(encoding="utf-8"))
    }
EXPLANATIONS = explanations

# plain copy
intro = (
    "**Main question: What do averages and snapshots hide about inequality, "
    "relationships and change over time?**\n\n"
    "We study internet use across countries and, separately, daily weather in the "
    "United States. An average can hide large differences between countries or places. "
    "A single date can hide how those differences developed. We use several views of "
    "the same data to show what each summary leaves out. The internet and weather "
    "datasets are not joined."
)
INTRO = intro

data_text = (
    "**Internet data.** We reuse the A1 OWID/ITU country data. We check duplicate "
    "country-year rows, join the indicators by country code and year, remove regional "
    "and world totals, and keep missing values as missing. The network uses 179 "
    "countries with all four 2020 indicators, standardized and joined to the five "
    "closest matches (590 undirected links). The 2015-2020 comparisons use 175 "
    "countries; the treemaps use 184; the 2000-2020 views use 159.\n\n"
    "**Weather data.** gridMET daily maximum temperature, rain, wind speed and "
    "direction from July 1 to September 30, 2023. Every sixth grid cell is read; "
    "source temperatures convert from Kelvin to Celsius once. Eight dates, spaced "
    "13 days apart, are used for GIFs. Full-period summaries use all 92 days and "
    "the same 13,416 valid cells."
)
DATA = data_text

js_text = (
    "The browser pages provide the required interactions. Parallel coordinates use "
    "JavaScript for bundling, brushing and axis reordering. D3 provides treemap "
    "zooming and the network controls; NetworkX supplies three network layouts. "
    "Run `python run_visualizations.py` from the submitted folder to open the launcher."
)
JS = js_text

discussion = (
    "**What the internet views add.** Figure 1 shows why distance in a network "
    "drawing can mislead: the links stay the same as the layout changes. In 126 of "
    "175 countries, internet use rose while landline subscriptions fell.\n\n"
    "**What averages hide.** Countries within one region can have very different "
    "levels. About 47% of the measured 2020 country spread lies within regions. "
    "For Asia, the regional-median shift (26.55pp) and median individual country "
    "gain (19.75pp) differ.\n\n"
    "**What weather summaries hide.** For September, 77.6% of eligible area received "
    "at least half its rain in five consecutive days. Hot-dry conditions covered "
    "16.27% of weighted grid-cell days; the longest local run was 67 days. Adding "
    "wind reduces joint occurrence to 2.57%."
)
DISCUSSION = discussion

conclusion = (
    "Averages hide differences within groups. Snapshots hide the paths and short "
    "events behind the final values. Separate measures can hide how often conditions "
    "occur together. Using several clear views of the same data helps answer these "
    "questions without treating a visual pattern as proof of a cause."
)
CONCLUSION = conclusion

# per-figure short descriptions
copy_data: dict[int, tuple] = {
    1: (
        "Same links, different network layouts",
        "Do the neighbors change when the layout changes?",
        "Trace a country and its links across all three panels before calling an apparent group meaningful.",
        "Layout changes readability and apparent neighborhoods while the measured graph remains unchanged.",
        "Line length in these layouts has no indicator unit.",
        "Check the connecting lines, not the distance between points.",
    ),
    2: (
        "Different country paths to higher internet use",
        "Can internet use rise without a similar rise in fixed broadband?",
        "Each panel follows one country from 2010 to 2020. All panels use the same axes.",
        "South Africa's internet use rose by 48.1pp while fixed broadband rose by 0.7 per 100.",
        "These six examples illustrate different paths, not all countries.",
        "A final value does not show the path a country took.",
    ),
    7: (
        "Internet use rose while landlines fell",
        "How common is this combination of changes?",
        "A bar counts countries where internet use increased and landlines decreased 2015-2020.",
        "This combination occurs in 126 of 175 matched countries (72%).",
        "Bars count directions of change, not their size.",
        "More internet use does not always come with more landline subscriptions.",
    ),
    11: (
        "Country differences inside each region",
        "How much country variation does a regional average leave hidden?",
        "Each dot shows one country's 2020 internet-use rate; dark tick marks the regional average.",
        "About 47% of measured country spread lies within regions.",
        "The split uses variance for 158 countries; each has equal weight.",
        "A regional label leaves nearly half the measured country differences hidden.",
    ),
    29: (
        "Separate frequencies and shared occurrence",
        "How often do hot, dry and windy conditions occur together?",
        "The first three bars count hot, dry and windy grid-cell days separately.",
        "All three conditions occur together in only 2.57% of weighted grid-cell days.",
        "The first three bars overlap and must not be added.",
        "Common separate conditions can have a much smaller shared occurrence.",
    ),
}
COPY = copy_data
