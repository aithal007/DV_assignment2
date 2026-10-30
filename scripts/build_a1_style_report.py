"""Report-only revision: A1's IEEE layout and explanation style, current A2 plots.

This command does not rebuild charts, slides, narration or video materials.
"""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,zipfile
import pymupdf
from build_latex_report import inline,escape
import simple_report_content as content
import build_story_report as story
import report_review_refinements as revision
import approved_report_replacements as approved

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'report_latex'

# Explain why each form is needed, rather than repeat a generic design claim.
WHY={
1:'A network picture can suggest that nearby countries are more closely related. Keeping one country and its links highlighted across three layouts tests that reading directly. The colored links can be followed even when the circle puts their endpoints far apart. This separates a change in the drawing from a change in the country relationships.',
2:'The network compares countries in one year. Small multiples add the history it leaves out. Each country gets its own panel, so its annual path can be followed without crossing five other paths. Shared axes make the size and direction of the changes comparable across countries.',
3:'The layout experiment shows where a network drawing can mislead, but crowded links can still hide individual pairs. NodeTrix replaces links inside each group with matrix cells. The overview keeps the groups in context, while the enlarged matrix lets the reader inspect a named country row and see both links and gaps.',
4:'Four measurements cannot be read from one ordinary scatterplot. Parallel coordinates place them on four vertical axes and keep each country connected across them. The full overview has too many overlapping lines for close reading, so this report selects six named countries that share high internet use and low fixed broadband. The selection makes their remaining differences visible.',
5:'This is a controlled comparison with Figure 4: country selection, colors, axis order, ranges and measured points stay fixed. Only the line paths change. Placing straight and bundled versions next to the same explanation makes it possible to judge whether bundling helps trace a group or hides country differences.',
6:'Parallel coordinates show four values together, but crossings are a poor way to judge the strength of a pairwise relationship. Two scatterplots put both comparisons on ordinary position axes. Keeping the same countries and internet-use scale makes the broadband and mobile patterns directly comparable.',
7:'Figure 6 compares country levels in one year. This chart asks a different question: how often did two measures move in opposite directions within a country? A common percentage baseline and count labels make the answer easier to read than a page of regional scatterplots. Showing each denominator also makes the small regional groups visible.',
8:'A country with a high internet-use rate can still have fewer users than a large country with a lower rate. The nested treemap separates these two quantities: area shows the count and color shows the rate. Region-first grouping answers where the included users live, while keeping countries inside their regions.',
9:'The first treemap makes regional size prominent. Reversing the hierarchy asks which adoption levels contain those users. Keeping the country data, total area and color scale fixed isolates the effect of grouping. The two trees therefore answer different questions with the same records.',
10:'A final adoption rate does not show when a country reached it. The steps count first arrivals at two clear milestones, so early progress and late catch-up can be compared within each region. A fixed set of countries prevents changing data coverage from creating an artificial rise.',
11:'A regional mean is one mark, even when its countries are far apart. Showing every country beside that mark reveals the spread directly. The variance split then gives a single numerical answer to how much of the total country variation sits inside regions. This extends the regional comparison without repeating A1\'s absolute-gap and ratio plots.',
12:'Subtracting two regional medians sounds like the typical country\'s gain, but the middle country can change between years. The paired endpoint view shows the regional summaries, and the gain view calculates change for each country first. Putting the two calculations together exposes the difference instead of asking the reader to infer it from separate tables.',
13:'Many full-size time-series panels would take more space. Horizon rows fold values around a meaningful 50% reference, keeping all 21 years in a compact display. Sorting by first crossing makes early and late arrivals easy to scan. The numerical endpoint labels help read values that are harder to recover from folded bands.',
14:'Repeating the horizon design for regional medians tests how much the story changes after aggregation. The same reference and colors allow a direct comparison with Figure 13. One compact row per region makes broad timing clear, while the preceding country plots show what each regional row leaves out.',
15:'A rising median could mean that countries moved together or that some moved much faster than others. Ridgelines retain the whole distribution at several dates. A common horizontal scale shows the shift, while country ticks help check the smooth shapes against the actual observations.',
16:'The global distribution mixes countries from different regions. Small multiples repeat the ridgeline comparison within each region, so a broad global shape can be traced to different regional paths. Shared horizontal scales keep low and high adoption in the same position across all panels.',
17:'A palette or scale can make a feature stand out even when the measurements do not change. These panels hold the field fixed and change only its mapping to color. Sequential colormaps suit these ordered magnitudes because no middle value needs special emphasis. Temperature tests palette choice; rainfall tests how the scale reveals smaller values alongside heavy rain.',
18:'An animation can look equally warm on every date if each frame is rescaled separately. The two columns test this with identical daily fields. One scale preserves comparisons between dates; the other spends its full color range on the variation within each date. Neither choice can be understood without checking the color bars.',
19:'Contours turn a continuous field into visible boundaries. Using the same date with two intervals separates the effect of boundary spacing from actual weather differences. Lines make threshold crossings explicit, while filled bands make broad areas easier to compare. The four panels test both choices on the same grid.',
20:'After testing color and contours, we use fixed choices to compare complete months. Shared colors let a temperature be recognized across all three maps, and common contour levels give reference boundaries. Using every day avoids choosing one unusually hot or cool date to represent a month.',
21:'Three maps show overall cooling but make small spatial differences difficult to compare. A diverging colormap suits a difference map because zero is a meaningful reference: it separates cooling from warming. Symmetric color limits show the sign and size of change around that neutral center. The cumulative curves show how widespread each change is within longitude bands, rather than reducing each band to one mean.',
22:'Monthly averages hide both short episodes and differences between places. A daily line restores timing, while the ribbons retain the range of temperatures across locations. Separate longitude panels keep the regional patterns readable without overlaying six shaded bands on one set of axes.',
23:'A monthly rainfall total cannot distinguish steady rain from a short burst. The second row adds the share falling in the wettest five consecutive days. Keeping total and concentration separate avoids calling a very small rain amount a major event simply because all of it fell at once.',
24:'A monthly mean temperature does not count how often a chosen hot threshold was exceeded. Frequency maps use all days and preserve location, making repeated heat distinguishable from one selected hot day. The fixed percentage scale lets July, August and September be compared directly.',
25:'Maps preserve location but require many frames to show all 92 days. A time-longitude diagram keeps every date visible in one view. Averaging across latitude makes room for that time axis, so episodes can be compared by their dates and east-west extent rather than remembered across an animation.',
26:'An arrow map can become unreadable before it becomes informative. Holding the wind field fixed while varying spacing shows how much local detail is traded for legibility. Comparing speed-scaled and equal-length arrows also separates the tasks of reading direction and reading magnitude.',
27:'Quiver maps show where wind points, but not how often each source direction occurs across a month. Wind roses collect those directions into sectors and divide each sector by speed. Separate monthly panels and a common radial scale reveal changes that one pooled seasonal rose would hide.',
28:'Separate temperature, rainfall and wind maps make it hard to check whether conditions occur at the same locations. The overlay aligns the three fields on one map. Two contrasting dates show what that alignment adds, while common visual scales keep the comparison meaningful.',
29:'With three conditions and a question about their joint occurrence, four bars give a direct answer. The first three establish how common each condition is; the fourth requires all three together. An intersection matrix would add symbols and combinations that are unnecessary for this comparison.',
30:'The shared-condition bars count occurrences but do not show whether they form long uninterrupted spells. Frequency and longest-run maps separate these two ideas. The daily coverage curve restores timing, and the threshold panel checks how the numerical result changes when the event definition changes.'
}

MORE={
1:'Current all-pair similarities and threshold diagnostics are inserted by network_threshold_revision.apply. Every distinct country pair has a measured similarity; the declared cutoff selects the displayed edges. Drawing distance does not define a neighbor.',
2:'India provides another low-broadband path: internet use rises by 35.9 points while fixed broadband rises by 0.8 per 100. Brazil gains 40.7 points alongside 10.1 more broadband subscriptions per 100. Germany starts at 82% online and gains only 7.8 points, leaving less room for growth. The six paths show why neither a shared endpoint nor a similar gain identifies one infrastructure history.',
3:'Within the enlarged group, Cuba and Palestine each connect to six other members, while Laos connects to three. Their fuller and sparser rows make that difference visible. The white cells matter as much as the filled cells: this group is not an all-to-all clique. Across the full graph, most links lie inside the groups, but 65 still cross group boundaries. The overview keeps those connections visible instead of treating the groups as isolated boxes.',
4:'Kuwait is about 99.1% online with 1.7 broadband subscriptions per 100, whereas Kyrgyzstan is 72.0% online with 4.3. Cuba has about 59.6 mobile subscriptions per 100, compared with 165.0 in Libya. Thus, even a deliberately similar selection on internet use and broadband retains large differences on the other axes. Each axis is read in its own units; equal vertical positions on two different axes do not mean equal quantities.',
5:'A line passing near another line between axes does not add evidence that the countries have equal values. The evidence is at the axis dots. The regional centers here are calculated from the selected six countries, so they describe this selection rather than all countries in each region. The straight version remains the clearest place to check an individual value; the bundled version tests a different way to follow the same profiles.',
6:'The broadband pattern is stronger, but a high rate of internet use does not require a high fixed-broadband value in every country, as Figures 2 and 4 already showed. There is another distinction: for 2015-2020 changes, the rank correlation between broadband gain and internet-use gain is only about 0.054. A strong relationship between country levels therefore does not carry over automatically to their changes.',
7:'South America has the highest displayed share, 10 of 11 countries, but only a small denominator. Europe has 35 of 43, while Africa has 30 of 46. These counts support a broad statement about direction: internet use often grows while landline use falls. They do not establish the size of either change or identify which connection technology people used. That is why the report keeps this count separate from the four-indicator profiles.',
8:'The total is 4,521,767,530 users in the included countries. Europe has a relatively high adoption rate in many tiles but a smaller user-count area than Asia. Reading only area would confuse population scale with access; reading only color would miss where most users live. The next figure changes the first grouping to test the same distinction from another angle.',
9:'Together, the two highest bands contain about 77.8% of the included users, but the 50-below-75% band is slightly larger than the 75-100% band. The band title describes the national adoption rate, not the status of every person inside the tile. All areas still count online users. Offline people are not drawn as a second population in this treemap.',
10:'The 50% and 75% curves also distinguish reaching majority use from reaching a much higher level. A country may pass one milestone well before the other. Here, first arrival is the event being counted: once a country crosses a threshold it remains in the cumulative count. The next views return to actual country levels, so that a milestone summary is not mistaken for a complete history.',
11:'The calculation uses variance, which measures how far values lie from their mean. Total country variance is split into spread around each regional mean and spread between the regional means, weighted by the number of countries. The 47% is a share of this measured spread, not a share of internet users or a claim that region causes the remaining 53%. The visible dots provide the practical interpretation: countries within one region can still be far apart.',
12:'For Asia, individual gains range from about -0.84 to 49.94 points, and the middle half lies between 9.86 and 28.25. A single regional shift hides that range. The correct calculation depends on the question: subtract regional medians to describe movement of the regional middle, or calculate each country\'s change first to describe the typical country gain. These two operations need not give the same answer.',
13:'Ireland crosses in 2006 and Peru in 2017, while Micronesia, like Tanzania, has no observed crossing by 2020. These rows show individual crossing times behind the group summaries. The selected countries are chosen by a stated quartile rule, rather than only choosing memorable successes. Folding the bands saves space, but the color reference must be read carefully: a red row can still be rising quickly toward 50%.',
14:'The gap between the European and African medians is about 55 percentage points in 2020. Yet each row compresses many different countries into one value per year. Figure 11 shows why the regional result cannot be assigned to every member, and Figure 12 shows why its change cannot automatically be read as a typical country gain. Together the views distinguish group timing from individual progress.',
15:'The middle half of country values still spans about 37.5 percentage points in 2020. That wide spread qualifies the large median increase: broad progress does not mean all countries are close to the same level. Each curve has its own height scaling, so the horizontal location and width carry the comparison; a taller peak does not mean that the year contains more countries.',
16:'The regional panels explain why one global curve cannot describe a single common journey. Europe reaches the upper part of the scale earlier, while lower and middle values remain more prominent in Africa. Within-region spreads also change, so even the regional median horizon is only part of the story. In small panels such as Oceania, the eight country marks are stronger evidence than an attractive bump in the fitted curve.',
17:'The rainfall comparison is especially useful because a few wet cells can set the top of the linear range and leave many other cells nearly the same color. Logarithmic mapping spreads positive small values apart, but its color steps represent ratios rather than equal millimeters. The legend is therefore part of the explanation. Zero rainfall is excluded from that logarithmic mapping because its logarithm is undefined.',
18:'The fixed range is obtained from the eight sampled dates. It supports comparisons across those frames, while making no claim to cover all possible temperatures outside them. This choice is carried into the date-comparison GIFs. A viewer can then read a repeated color as a repeated temperature instead of interpreting a repeated hottest color as the same absolute heat. The normalized position is u = (T - minimum) / (maximum - minimum). Global mapping uses the minimum and maximum across all sampled dates; local mapping uses the bounds of each date. Thus a fixed temperature keeps its color only with the global bounds.',
19:'The grid is regular and two-dimensional, so the plotting library traces threshold crossings through neighboring grid cells using the Marching Squares family of methods. Missing cells stay masked. Choosing a smaller interval changes how many boundaries are drawn, rather than adding finer source measurements. The interval should therefore be selected for the required reading task, not treated as improved data resolution.',
20:'The difference is a fall of 4.64 degrees in the area-weighted mean. That is a change in the average daily maximum, rather than a count of hot days or the single hottest day. Those are separate questions. The next views subtract the months directly, then restore daily timing and hot-day frequency to show the information lost by this monthly summary.',
21:'A negative mean alone could be produced by strong cooling in a small area. The 99.66% area result shows that cooling is widespread here. The comparison with first and last sampled dates then tests the snapshot problem directly: a pair of daily weather states does not summarize all the days in their respective months. The longitude-band curves show how the size of change also varies across the study area.',
22:'The inner ribbon runs from the 25th to the 75th percentile, and the outer ribbon from the 10th to the 90th. For example, a broad ribbon means that places in the same longitude band have different daily maxima even if the average line is steady. The ribbons should not be read as statistical confidence around that line; their subject is spatial variation in the observed field.',
23:'August also has a larger concentrated-rain share than July: 67.5% of its eligible area receives at least half its monthly rain in a five-day window. September has a lower weighted mean total, about 57.1 mm, but the largest concentration share. Amount and timing therefore give different comparisons. The 10 mm screen avoids unstable percentages from nearly dry cells; the supporting calculation repeats it with other minimum totals.',
24:'The frequency denominator is the number of days in the month, so different month lengths do not create a difference merely by changing the count. A 50% cell has reached the threshold on half its days, whether those days are consecutive or scattered. That distinction leads to the final run-length analysis, where uninterrupted duration is calculated explicitly.',
25:'The daily ordering can reveal a short episode that contributes only a small part of a monthly average. However, each longitude column combines locations at different latitudes. A feature running across columns is a pattern in these summaries; it is not, by itself, the path of a particular storm. The monthly maps and daily ribbons retain complementary spatial detail.',
26:'The source wind direction states where the wind comes from. The arrow components are converted so that the plotted arrow points toward its flow destination. Keeping that convention explicit prevents a 180-degree reading error. Equal-length arrows are helpful for comparing directions, but their length no longer indicates speed; the colors carry that measurement.',
27:'The speed classes are 0-2, 2-4, 4-6, 6-8 and at least 8 m/s. All roses use the same 14% radial maximum, so equal bar heights mean equal weighted frequency across months. Here direction is the source direction, unlike the flow-pointing arrows. A wind rose summarizes the distribution over the area; it cannot show which particular location produced a sector.',
28:'The rainfall contours keep threshold boundaries visible without replacing the temperature background, and the arrows add wind direction at sampled locations. The result is useful for checking where the fields meet, but the single map can become busy if every grid arrow is drawn. The spacing chosen in the quiver experiment is therefore carried into the overlay. Complete-period counts are still needed to say how common the selected contrast is.',
29:'The separate frequencies are about 18.06% hot, 76.65% dry and 11.65% windy. They overlap, so they must not be added to obtain a total. The 2.57% joint bar is calculated by checking the three conditions in each cell on each day before averaging. This preserves coincidence that would be lost by multiplying or comparing separate spatial averages.',
30:'The longest run is calculated separately in each cell, whereas the daily curve shows how much of the full study area is affected at once. A long local spell and a large affected area are different findings. The plotted sensitivity check uses 33, 35 and 37 degrees with rain cutoffs of 0.1 and 1 mm/day. Runs touching July 1 or September 30 may continue outside the observed window.'
}

INTRO='''A country can have a high internet-use rate even with little fixed broadband. A region can improve while its countries remain far apart. A month can be cooler on average yet contain short hot spells. In each case, a summary leaves something out. This report follows those missing details through several views of the same data.

**Central question: What do averages and snapshots hide about inequality, relationships and change over time?**

We answer three subquestions:

**1. Relationships.** Can countries with similar internet use have different infrastructure profiles and network links?

**2. Inequality and change.** Does overall progress mean countries have caught up, or do regional summaries hide gaps and different paths?

**3. Daily weather.** What do averages and selected dates leave out about location, short events and long runs?

The first two questions use the country internet data from A1. The third uses daily weather in the United States. The datasets are studied separately; all three questions examine the detail hidden by a summary.'''

ABSTRACT='''An average gives a useful overview, but it can hide different paths and uneven progress. We examine this problem using country internet data and, separately, daily weather from July to September 2023. Thirty figure sets connect each comparison to a question. In the internet data, 126 of 175 countries gain internet users as a share of population while landline subscriptions fall. About 47% of measured country variation in internet use lies within regions, so a regional label leaves substantial differences hidden. In the weather data, July and August have similar average monthly rain totals, but different concentration into short bursts. Hot-dry conditions account for 16.27% of weighted grid-cell days, while one location has a 67-day uninterrupted run. Network, multivariable, time-series and spatial views show why levels, changes, frequency and duration need separate comparisons.'''

DISCUSSION='''The internet views separate three questions. The network tests which country profiles are linked, rather than which nodes happen to look close. The annual paths distinguish similar endpoints reached through different histories. Figure 4 adds four paired changes for each country: Georgia and Brunei gain about 25 points in internet use, yet their landline and mobile changes go in opposite directions. Figure 5 compares the separate question of endpoint profiles. Figure 7 shows that strong level relationships become much weaker when the same countries' gains are compared. Figure 10 follows fixed starting groups: all improve, but the lowest-starting group remains far behind in its median. The country dots and paired gains then show why a regional average cannot stand in for each member. Nearly half of measured country variation lies within regions, and a regional median shift need not equal the typical country gain.

The weather views make the same distinction between summary and detail. Monthly maps show broad cooling, daily records reveal episodes, rainfall concentration separates amount from timing, and run length separates frequency from uninterrupted duration. Fixed colors and shared axes keep those comparisons consistent.

Together these results answer the main question: averages hide differences inside groups, snapshots hide paths and timing, and separate summaries hide coincidence. The patterns describe the included countries and this three-month weather interval; they do not, on their own, identify causes.'''

CONCLUSION='''Similar internet-use levels can come with different infrastructure histories. Regional progress can leave countries far apart. Similar monthly rain totals can arrive steadily or in a burst, and frequent events need not form long runs.

Each stage adds the detail missing from the previous summary: links and values, annual paths and distributions, daily timing and shared conditions.'''

REPRO='''The supporting files contain source data, scripts, full-resolution figures, interactive pages and three eight-frame GIFs. The README explains how to rebuild the figures, run the browser views and compile this report.'''

CAPTIONS={
1:'The same threshold graph in Spring, Spectral and Circular layouts; the all-pair distribution and chosen cutoff accompany the comparison.',
2:'Annual internet-use and fixed-broadband paths for six countries, 2010-2020, on shared axes.',
3:'Seven country groups in a NodeTrix overview, with the eight-country group G7 enlarged to show its individual links.',
4:'Four 2020 indicators for six countries with at least 70% internet use and no more than five broadband subscriptions per 100 people.',
5:'The same countries, axis ranges and measured points as Figure 4, with 50% bundling toward the selected regional centers.',
6:'Internet use against fixed broadband and mobile subscriptions for the same 175 countries in 2020.',
7:'Counts and percentages of matched countries with rising internet use and falling landline subscriptions, 2015-2020.',
8:'Region-first treemap of 4.52 billion included internet users in 184 countries, 2020; area shows users and country color shows adoption.',
9:'The same users and countries as Figure 8, grouped first by national adoption band and then by region.',
10:'Cumulative shares first observed at or above 50% and 75% internet use, 2000-2020; 158 countries with known regions.',
11:'Individual country internet-use rates and regional means, 2020, alongside the within-region and between-region variance split.',
12:'Regional medians in 2015 and 2020 beside the distribution of the same countries\' individual gains.',
13:'Annual internet use for 12 selected countries, 2000-2020; horizon bands show distance above or below 50%.',
14:'Regional median internet use, 2000-2020, using the same 50% horizon reference as Figure 13.',
15:'Internet-use distributions for a fixed panel of 159 countries at five dates from 2000 to 2020.',
16:'The fixed-panel distributions separated by region, with shared adoption axes, country ticks and median labels.',
17:'Fixed weather fields shown with alternative temperature palettes and linear versus logarithmic rainfall scales.',
18:'Identical sampled temperature fields with one fixed scale versus a separate scale for each date.',
19:'The August 22 temperature field with 5- and 10-degree contour intervals, drawn as lines and filled bands.',
20:'July, August and September 2023 mean daily maximum temperature, with shared colors and contour thresholds.',
21:'September minus July mean daily maximum temperature, with area-weighted cumulative change distributions by longitude band.',
22:'Daily mean maximum temperature with spatial 25th-75th and 10th-90th percentile ribbons across all 92 days.',
23:'Monthly rainfall totals beside each month\'s wettest consecutive five-day share; concentration is shown where monthly rain is at least 10 mm.',
24:'Percentage of days reaching at least 35 degrees Celsius in each month, shown on one frequency scale.',
25:'Daily temperature and rainfall summaries across longitude, retaining all dates while averaging across latitude.',
26:'One wind field with three arrow spacings and either speed-scaled or equal arrow lengths.',
27:'Monthly wind-source direction and speed distributions, using identical sectors, speed classes and radial frequency scales.',
28:'Temperature color, rain contours and wind arrows for July 27 and September 30, with common scales.',
29:'Separate hot, dry and windy frequencies beside their all-three joint frequency, using weighted grid-cell days.',
30:'Hot-dry frequency, longest local run, daily affected area and sensitivity to the chosen temperature and rainfall thresholds.'
}

def digest(paths):
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def build():
    protected=list((ROOT/'output/video_presentation').rglob('*'))
    protected=[p for p in protected if p.is_file()]
    before=digest(protected)
    backup=ROOT/'archive/before_expanded_takeaways_20261024.zip'
    if not backup.exists():
        with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
            for p in [ROOT/'REPORT.md',ROOT/'data/current_figure_manifest.json',OUT/'DAS732_A2_Report.tex',ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf']:
                z.write(p,p.relative_to(ROOT))
    figures=[f for f in json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8')) if f['figure']<=30]
    assets=list(dict.fromkeys([ROOT/f['path'] for f in figures]+[ROOT/'output/internet_revision/pcp_focus.png',ROOT/'images/quality/telecom_scatterplot_matrix.png']))
    images_before=digest(assets)
    content.configure(story)
    for f in figures:
        n=f['figure'];title,q,enc,finding,note,take=content.COPY[n]
        # Essential context belongs with the reading, without a separate limits block.
        f.update(title=title+'.',caption=CAPTIONS[n],explanation=[q,enc,WHY[n],note,take],
                 detailed_interpretation=finding+'\n\n'+MORE[n])
        # These qualifications are already explained in the expanded prose.
        if n not in {1,3,4,5,8,10,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30}:
            f['detailed_interpretation']+=' '+note
    revision.refine(figures,WHY,MORE,CAPTIONS)
    approved.apply(figures,WHY,MORE,CAPTIONS)
    import network_threshold_revision
    network_threshold_revision.apply(figures,content)
    # Use the exact typography, title block and float spacing of ass2_1.pdf.
    # Only its design is reused; the current report supplies all body content.
    pre=(OUT/'design_reference_preamble.tex').read_text(encoding='utf-8')
    parts=[pre,r'\begin{abstract}'+escape(revision.ABSTRACT)+r'\end{abstract}',
           r'\begin{IEEEkeywords}country internet use, visual comparison, temporal change, daily weather, multivariable visualization\end{IEEEkeywords}',
           r'\section{Introduction}',story.paragraph(INTRO),r'\section{Data and preparation}',story.paragraph(content.DATA),
           r'\subsection{Tools and interactive views}',story.paragraph(content.JS)]
    md=['# Beyond Averages and Snapshots\n\nConnectivity Profiles and Daily Weather | Team Plot Twist | DAS732 Assignment 2','## Abstract\n\n'+revision.ABSTRACT,
        '## Introduction\n\n'+INTRO,'## Data and preparation\n\n'+content.DATA,'### Tools and interactive views\n\n'+content.JS]
    guide=[];pos=0
    for section,ids,lead in story.SECTIONS:
        if section.startswith('Appendix'):break
        parts += [r'\section{'+escape(section)+'}',story.paragraph(lead)]
        md += ['## '+section+'\n\n'+lead]
        for _ in ids:
            f=figures[pos];pos+=1;n=f['figure'];q,enc,why,note,take=f['explanation']
            shutil.copy2(ROOT/f['path'],OUT/'figures'/f'Fig{n}.png')
            # Match the reference: full-width main figures, two compact
            # one-column summaries, short captions and italic reading guides.
            height={1:.62,5:.49,6:.62,7:.49,10:.54,19:.58,22:.47,26:.47,28:.62}.get(n,.49)
            env='figure' if n in {14,15} else 'figure*'
            width=r'\columnwidth' if n in {14,15} else r'\textwidth'
            if n in {14,15}:height=.42
            parts += [r'\subsection{'+escape(f['title'].rstrip('.'))+'}',
                      r'\noindent\textit{Question (Fig.~\ref{fig:'+str(n)+r'}).} '+inline(q),
                      r'\begin{'+env+r'}[!tb]\centering',
                      rf'\includegraphics[width={width},height={height}\textheight,keepaspectratio]{{Fig{n}.png}}',
                      r'\caption{'+escape(f['title'])+r'}\label{fig:'+str(n)+'}',r'\end{'+env+'}',
                      r'\noindent\textit{How to read the graph.} '+inline(enc),
                      r'\noindent\textit{Why this chart.} '+inline(why),
                      r'\noindent\textit{Detailed interpretation.} '+story.paragraph(f['detailed_interpretation']),
                      r'\takeaway{'+inline(take)+'}']
            block=f'### Figure {n}. {f["title"]}\n\n![Figure {n}]({f["path"]})\n\n**Encoding.** {enc}\n\n**Why this chart.** {why}\n\n**What it shows.** {f["detailed_interpretation"]}\n\n**Takeaway.** {take}\n'
            md.append(block);guide.append(block)
        if pos==16:parts.append(r'\FloatBarrier')
    contributions=story.contributions_latex().replace('Discussion/Limitations','Discussion').replace('Figs. 1-3, 17-18, 20-23, 25.', 'Figs. 1-3, 17-18, 20-23, 25, 31.').replace('Figs. 10-16, 19, 24, 30.', 'Figs. 10-16, 19, 24, 30, 32.')
    # Keep the required allocation with its heading instead of on an empty float page.
    contributions=contributions.replace(r'\begin{table}[!ht]\centering\footnotesize',r'\par\smallskip\noindent{\footnotesize').replace(r'\end{tabularx}\end{table}',r'\end{tabularx}}\par\smallskip')
    parts += [r'\section{Discussion}',story.paragraph(DISCUSSION),r'\section{Code and supporting files}',story.paragraph(REPRO),contributions,r'\section{Conclusion}',story.paragraph(CONCLUSION)]
    import build_additional_evidence as addition
    extras=addition.entries()
    parts += [r'\clearpage',r'\onecolumn',r'\section{Additional evidence for the central question}']
    extra_md=[]
    for f in extras:
        n=f['figure'];q,enc,why,note,take=f['explanation']
        shutil.copy2(ROOT/f['path'],OUT/'figures'/f'Fig{n}.png')
        parts += [r'\begin{center}',rf'\includegraphics[width=\textwidth,height=.205\textheight,keepaspectratio]{{Fig{n}.png}}',r'\widecaption{'+escape(f['title'])+'}{fig:'+str(n)+'}',r'\end{center}',r'\noindent\textit{Question (Fig.~\ref{fig:'+str(n)+r'}).} '+inline(q),r'\noindent\textit{How to read the graph.} '+inline(enc),r'\noindent\textit{Why this chart.} '+inline(why),r'\noindent\textit{Detailed interpretation.} '+story.paragraph(f['detailed_interpretation']+' '+note),r'\takeaway{'+inline(take)+'}']
        block=f'### Figure {n}. {f["title"]}\n\n![Figure {n}]({f["path"]})\n\n**Encoding.** {enc}\n\n**Why this chart.** {why}\n\n**What it shows.** {f["detailed_interpretation"]} {note}\n\n**Takeaway.** {take}\n'
        extra_md.append(block);guide.append(block)
    figures.extend(extras)
    parts.append(r'\end{document}')
    tex='\n\n'.join(parts)
    tex=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:' '.join(r'\path{'+t+'}' for t in m[1].replace(r'\_','_').split()),tex)
    (OUT/'DAS732_A2_Report.tex').write_text(tex,encoding='utf-8')
    for i in range(2):
        result=subprocess.run([shutil.which('pdflatex'),'-interaction=nonstopmode','-halt-on-error','DAS732_A2_Report.tex'],cwd=OUT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (OUT/f'compile_pass_{i+1}.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
        if result.returncode:raise RuntimeError(result.stdout[-4000:])
    pdf=ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf';shutil.copy2(OUT/'DAS732_A2_Report.pdf',pdf)
    md += ['## Discussion\n\n'+DISCUSSION,'## Code and supporting files\n\n'+REPRO,story.contributions_markdown().replace('Discussion/Limitations','Discussion').replace('Figs. 1-3, 17-18, 20-23, 25.', 'Figs. 1-3, 17-18, 20-23, 25, 31.').replace('Figs. 10-16, 19, 24, 30.', 'Figs. 10-16, 19, 24, 30, 32.'),'## Conclusion\n\n'+CONCLUSION]
    md += ['## Additional evidence for the central question']+extra_md
    (ROOT/'REPORT.md').write_text('\n\n'.join(md),encoding='utf-8')
    (ROOT/'FIGURE_EXPLANATIONS.md').write_text('# Figure explanations\n\n'+'\n\n'.join(guide),encoding='utf-8')
    (ROOT/'data/current_figure_manifest.json').write_text(json.dumps(figures,indent=2),encoding='utf-8')
    selection_path=ROOT/'data/report_selection.json'
    selection=json.loads(selection_path.read_text(encoding='utf-8'))
    selection.update(report_style='Design restored from user reference ass2_1.pdf: original title, float spacing, short captions, italic guides and individually sized figures',report_generator='scripts/build_a1_style_report.py',design_reference='C:/Users/Parikshith/Downloads/ass2_1.pdf',revision_scope='Approved change PCP (Figure 4), association comparison (Figure 7), fixed cohorts (Figure 10), and expanded interpretations; presentation and video unchanged')
    selection_path.write_text(json.dumps(selection,indent=2),encoding='utf-8')
    (ROOT/'data/report_figure_explanations.json').write_text(json.dumps([dict(figure=f['figure'],title=f['title'],question=f['explanation'][0],encoding=f['explanation'][1],rationale=f['explanation'][2],detailed_interpretation=f['detailed_interpretation'],takeaway=f['explanation'][4]) for f in figures],indent=2),encoding='utf-8')
    pages=len(pymupdf.open(pdf))
    (OUT/'README.md').write_text(f'# A2 report source\n\n{pages} pages, 32 figure sets (all original 30 plus two additional analyses). Design follows the user-provided ass2_1.pdf: original title block, full-width figures, compact captions, italic reading guides and tight float spacing. Current content and expanded takeaways are retained. Compile DAS732_A2_Report.tex twice with pdfLaTeX.\n\nReport-only rebuild: python scripts/build_a1_style_report.py from ass2. Slides and video files are not regenerated.\n',encoding='utf-8')
    with zipfile.ZipFile(ROOT/'output/DAS732_A2_LaTeX_Source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in [OUT/'DAS732_A2_Report.tex',OUT/'design_reference_preamble.tex',OUT/'README.md',*[OUT/'figures'/f'Fig{n}.png' for n in range(1,len(figures)+1)]]:z.write(p,p.relative_to(OUT))
    assert before==digest(protected),'Presentation/video files changed'
    assert images_before==digest(assets),'Source plot assets changed'
    validation=dict(pages=pages,figures=len(figures),style_reference='C:/Users/Parikshith/Downloads/ass2_1.pdf',source_plot_assets_unchanged=True,restored_figures=[5,6],slides_video_unchanged=True,protected_files=before,reading_guide_count=tex.count(r'\textit{How to read the graph.}'),rationale_count=tex.count(r'\textit{Why this chart.}'),takeaways=tex.count(r'\takeaway{'),takeaway_word_counts=[len(f['explanation'][4].split()) for f in figures],references=len(story.REFERENCES))
    (ROOT/'data/a1_style_report_validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in validation.items() if k!='protected_files'},indent=2))

if __name__=='__main__':build()
