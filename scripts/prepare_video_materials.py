"""Prepare evidence images and one authoritative slide/script storyboard."""
from pathlib import Path
import json, re, html
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from PIL import Image, ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/video_presentation'
ASSETS=OUT/'assets'
ASSETS.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':16,'axes.spines.top':False,
 'axes.spines.right':False,'axes.labelcolor':'#173047','text.color':'#173047',
 'xtick.color':'#173047','ytick.color':'#173047','svg.fonttype':'none'})

def asset(name,number,box=None):
    src=ROOT/manifest[number-1]['path']
    im=Image.open(src).convert('RGB')
    if box:
        w,h=im.size;im=im.crop(tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(box)))
    im.save(ASSETS/(name+'.png'))
    return name+'.png'

def finish(fig,name):
    fig.savefig(ASSETS/(name+'.png'),dpi=180,bbox_inches='tight',facecolor='white')
    fig.savefig(ASSETS/(name+'.svg'),bbox_inches='tight',facecolor='white')
    plt.close(fig)

# Faithful excerpts from report figures. Full originals remain in the report/gallery.
asset('network',1)
asset('regional',12)
asset('horizon',13)
asset('ridgeline',15)
asset('colour',18,(0,.035,1,.975))
asset('rainfall',23)
asset('contours',19,(0,.035,1,.975))
asset('quiver',26,(0,.035,1,.98))
asset('intersections',29)
asset('within_regions',11)
from PIL import Image
_matrix=Image.open(ROOT/manifest[2]['path']);_w,_h=_matrix.size
_matrix.crop((round(_w*.42),round(_h*.06),_w,round(_h*.94))).save(ASSETS/'nodetrix_zoom.png')
asset('persistence',30,(0,.055,1,.565))
# Same chart-only crops as the final report.
asset('pcp',5)
asset('treemap',8)

# Larger presentation versions of existing report analyses, using the same data.
profiles=pd.read_csv(ROOT/'output/lecture_previews/community_profiles.csv').iloc[:2]
fig,axs=plt.subplots(1,3,figsize=(12.7,4.3),layout='constrained')
for ax,key,label,upper in zip(axs,['internet_pct','landlines_per100','broadband_per100'],
 ['Internet adoption (%)','Landlines per 100 people','Broadband per 100 people'],[100,50,45]):
    for y,row in profiles.iterrows():
        color=['#087E8B','#D66A2C'][y]
        ax.barh(1-y,row[key],height=.36,color=color)
        ax.text(row[key]+1,1-y,f'{row[key]:.1f}',va='center',fontsize=18,weight='bold')
    ax.set(yticks=[1,0],yticklabels=['G1 (40 countries)','G2 (37 countries)'] if ax==axs[0] else ['', ''],
           xlim=(0,upper),ylim=(-.6,1.6),xlabel=label)
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
finish(fig,'profiles')

annual=pd.read_csv(ROOT/'output/internet_research/inequality_annual.csv')
fig,axs=plt.subplots(1,2,figsize=(12.6,4.9),layout='constrained')
for ax,key,color,ylabel,ylim in zip(axs,['mean_pairwise_gap','gini'],['#D66A2C','#087E8B'],
 ['Mean absolute gap (percentage points)','Relative inequality (Gini)'],[(0,40),(0,1)]):
    ax.plot(annual.year,annual[key],lw=3.5,color=color)
    ax.set(xlabel='Year',ylabel=ylabel,ylim=ylim,xticks=[2000,2005,2010,2015,2020])
    ax.grid(alpha=.17)
    for idx in [0,len(annual)-1]:
        r=annual.iloc[idx];ax.scatter(r.year,r[key],s=45,color=color)
        ax.annotate(f'{r[key]:.2f}',(r.year,r[key]),xytext=(0,12),textcoords='offset points',ha='center',weight='bold')
peak=annual.loc[annual.mean_pairwise_gap.idxmax()]
axs[0].annotate('Peak in 2013',(peak.year,peak.mean_pairwise_gap),xytext=(2004,37),fontsize=16,
 arrowprops={'arrowstyle':'-','color':'#173047'})
finish(fig,'inequality')

rows=pd.read_json(ROOT/'data/infovis_countries.json')
a=rows[rows.year==2015].set_index('code');b=rows[rows.year==2020].set_index('code')
codes=a.index.intersection(b.index);a=a.loc[codes];b=b.loc[codes]
assert len(codes)==175
field='internet_users_share_pct';bb='broadband_subs_per100'
rho_level=float(spearmanr(b[bb],b[field]).statistic)
rho_change=float(spearmanr(b[bb]-a[bb],b[field]-a[field]).statistic)
assert abs(rho_level-.8313809)<1e-6 and abs(rho_change-.053867)<1e-6
fig,axs=plt.subplots(1,2,figsize=(12.7,4.9),layout='constrained')
for ax,x,y,title in [(axs[0],b[bb],b[field],f'2020 levels: Spearman {rho_level:.2f}'),
 (axs[1],b[bb]-a[bb],b[field]-a[field],f'2015–2020 changes: Spearman {rho_change:.2f}')]:
    ax.scatter(x,y,s=34,color='#087E8B',alpha=.65,edgecolors='white',linewidths=.4)
    ax.set_title(title,fontsize=19,weight='bold',pad=15);ax.grid(alpha=.15);ax.set_axisbelow(True)
axs[0].set(xlabel='Broadband subscriptions per 100',ylabel='Internet adoption (%)')
axs[1].set(xlabel='Broadband change per 100',ylabel='Adoption change (percentage points)')
axs[1].axhline(0,color='#8996A0',lw=1);axs[1].axvline(0,color='#8996A0',lw=1)
finish(fig,'levels_changes')
pd.DataFrame({'code':codes,'broadband_2020':b[bb],'adoption_2020':b[field],
 'broadband_change':b[bb]-a[bb],'adoption_change':b[field]-a[field]}).to_csv(ASSETS/'levels_changes_evidence.csv',index=False)

SLIDES=[]
def add(title,speaker,start,end,layout,images,headline,takeaway,source,say,screen,actions=''):
    SLIDES.append(dict(number=len(SLIDES)+1,title=title,speaker=speaker,start=start,end=end,
      duration=end-start,layout=layout,images=images,headline=headline,takeaway=takeaway,
      source=source,say=say,screen=screen,actions=actions))

add('What do averages and snapshots hide?','Parikshith',0,15,'cover',['profiles.png','rainfall.png'],
 'Inequality, relationships and change over time', '', 'A2 report: central question; A1 country indicators and gridMET daily weather.',
 'An average can show progress while hiding who benefited and how change happened. We ask what averages and snapshots conceal, using country internet indicators and a separate daily-weather investigation.',
 'Opening slide: main question on the left, two clearly labeled evidence previews on the right. Names in the footer. No extra title-only slide.',
 'Begin immediately. Indicate country and weather previews once. These are separate datasets, with no inferred link between them.')
add('The same network can look different','Parikshith',15,38,'network',['network.png','nodetrix.png'],
 '179 countries. 590 similarity edges.', 'Check stored connections and measured profiles before interpreting a group.',
 'Report Figs. 1–2. NetworkX five-nearest-neighbor union on four standardized indicators.',
 'We start with a country similarity network. These three layouts contain exactly the same countries and edges, although their appearance changes. Links represent similar measured profiles. NodeTrix then exposes internal connections more clearly. We check the measurements behind these groups before interpreting them.',
 'Three layouts take most of the width. A smaller NodeTrix inset retains its group structure. Show one sentence below explaining the implication.',
 'Point once across spring, spectral and circular layouts. Move to the NodeTrix inset when naming it. Avoid tracing tiny individual nodes.')
add('Similar adoption conceals different infrastructure','Parikshith',38,65,'profiles',['profiles.png'],
 '86.1% and 86.8% adoption', 'Adoption averages alone do not describe the infrastructure profile.',
 'Report Fig. 3, G1/G2 excerpt; output/lecture_previews/community_profiles.csv. Equal country weights; exploratory groups.',
 'Two groups average about 86 percent adoption, yet broadband levels are approximately 25 and 37 subscriptions per hundred people. Their landline levels differ substantially too. Similar adoption therefore coexists with different infrastructure. These groups describe the selected indicators rather than establish a causal pathway. But as adoption increased, did the gap between countries narrow?',
 'Large presentation redraw of Figure 3 G1/G2 means. Keep all three unit labels. Teal identifies G1 and orange identifies G2. Highlight the broadband difference.',
 'Pause over the two adoption bars, then point to broadband. End with the question leading into Sindhoor’s section.')
add('Progress depends on the inequality measure','Sindhoor',65,97,'inequality',['inequality.png'],
 'Relative inequality falls. Absolute gaps remain wider than in 2000.',
 'Progress is real, while convergence depends on the measure.',
 'Report Fig. 11 A–B; output/internet_research/inequality_annual.csv. Fixed 159-country panel, 2000–2020.',
 'The answer depends on the measure. In a fixed country panel, relative inequality falls: the Gini drops from about 0.71 to 0.22. But the mean absolute difference rises from roughly 11 to 29 percentage points, after peaking in 2013. Adoption improved while absolute gaps remained larger than in 2000. Each country receives equal weight, so this measures differences between national rates, not inequality between individual people.',
 'Two large line charts, with the peak and endpoint values labeled. Preserve separate units and scales. The slide title and bottom inference connect both measures.',
 'Explain the teal relative measure first, then the orange absolute measure. Hold briefly on the 2013 peak and 2020 endpoint.')
add('Regional progress differs from individual gains','Sindhoor',97,120,'regional',['regional.png'],
 'Asia: 26.55 pp regional shift; 19.75 pp typical country gain',
 'A regional median shift is different from the median of individual changes.',
 'Report Fig. 12; 175 matched countries, including 41 in Asia, 2015–2020. Country-weighted statistics.',
 'Regional summaries hide another distinction. Asia’s median adoption shifts by 26.55 percentage points, while the median individual country gain is 19.75 points. The country dots show the spread behind that difference. A regional improvement should therefore not be described as every country’s improvement. How did these different experiences unfold over time?',
 'Figure 12 with two explicitly named numerical callouts. The left panel shows endpoints and the right panel shows individual gains. Emphasize the Asia row without hiding the other regions.',
 'Point to the Asia endpoint row, then its gain distribution. Say “percentage points”, not “percent growth”.')
add('Trajectories retain timing and spread','Sindhoor',120,130,'temporal',['horizon.png','ridgeline.png'],
 'Horizon: trajectories. Ridgeline: distributions.', 'The same overall progress contains different paths and distributions.',
 'Report Figs. 13 and 16. Companion variations: Figs. 14–15. Fixed 159-country annual panel.',
 'Horizon plots retain trajectories; ridgelines reveal distributions. Both expose uneven progress. We next inspect relationships behind the country profiles.',
 'Two method examples only. These are supporting demonstrations. Avoid explaining every row. Retain the horizon baseline/legend and ridgeline axes.',
 'Name each method and its analytical purpose. Detailed baseline and bandwidth explanations remain in the report.')
add('JavaScript reveals the selected country profiles','Varshith',130,155,'pcp',['pcp.png'],
 'Bundle paths, brush a range, reorder axes', 'Interaction turns a dense overview into a checkable subset.',
 'Report Figs. 4–5. web/app.js and web/index.html. 175 matched countries, fixed axes.',
 'Our JavaScript view makes this investigation interactive. Each parallel-coordinate line is a country. Bundling organizes the paths, brushing selects a range, and reordering places different measurements beside one another. These actions help us inspect the country profiles behind a dense overview while preserving the measured axis values.',
 'Use the actual browser for this interval. The deck contains a baseline screenshot for context; it is not interaction evidence.',
 'Before recording: open http://127.0.0.1:8765/web/index.html, select 2020 and All regions, keep matched countries/fixed axes checked. During 25 seconds: set bundling 0 then 50; drag on the adoption axis to brush a broad range; pause at the selected count; click Clear brushes; click one axis title to move it right. Axis reordering clears brushes. Do not quote an unverified selected count.')
add('Hierarchy changes the grouping of the same users','Varshith',155,170,'treemap',['treemap.png'],
 '184 countries. Same included total across both hierarchies.',
 'Rectangle area measures user counts; country colour measures adoption.',
 'Report Figs. 8–9. web/treemap.js and web/treemap.html. Included total: 4,521,767,530 users.',
 'The treemap switches from regions to adoption bands while retaining the same country leaves and total. Area represents internet-user counts, while country colour represents adoption. A large rectangle therefore answers a different question from a high adoption percentage.',
 'Continue the actual browser recording. Use the existing treemap page in a prepared second tab.',
 'Start at region-first root. Click Asia, point at breadcrumb, click Back one level. Switch Hierarchy to adoption bands. Show the root total remaining unchanged. Finish without zooming into an unrelated subset.')
add('Snapshot association does not explain growth','Varshith',170,195,'levels',['levels_changes.png'],
 'Spearman association: 0.83 for levels; 0.05 for changes',
 'The strong level relationship does not establish a growth mechanism.',
 'Report Figs. 6–7 analytical comparison. Video redraw uses the same 175 matched countries. Evidence CSV is supplied.',
 'Across countries, broadband and adoption have a strong association in 2020, about 0.83. For changes in the same countries between 2015 and 2020, it is only about 0.05. The strong snapshot relationship does not establish that broadband growth explains adoption growth. Having seen what country summaries conceal, we now test the same question using daily weather.',
 'Return to the deck. Two large scatterplots directly compare the broadband/adoption pair, with units and Spearman coefficients. This presentation redraw makes the report’s level/change comparison explicit.',
 'Point to the 2020 cloud, then the change cloud. Avoid describing either coefficient as a causal effect.')
add('Consistent colour scales support date comparisons','Parikshith',195,223,'colour',['colour.png'],
 'Daily weather, July–September 2023',
 'Local contrast and cross-date temperature differences answer different questions.',
 'Report Fig. 18. gridMET Tmax; global limits cover the eight documented sample dates. Sampled US footprint.',
 'Daily weather provides a separate test. With a fixed temperature scale, the same colour means the same temperature across dates. Local scaling instead reveals detail within each day, but identical colours can represent different temperatures. Stronger contrast alone cannot establish a hotter day. Once comparisons are consistent, we can ask what monthly summaries hide.',
 'Figure 18 large enough to compare its two columns and colour bars. Label fixed-scale and daily-scale columns. The eight-date support appears in the footnote.',
 'Compare vertically within the fixed-scale column, then point at the different local colour-bar limits. Do not describe the experiment’s limits as all-92-day extrema.')
add('Monthly rainfall totals conceal concentration','Parikshith',223,260,'rainfall',['rainfall.png'],
 '44% in July; 78% in September',
 'A monthly total cannot tell us whether rain arrived in a short burst.',
 'Report Fig. 23. Area-weighted percentages conditional on monthly rain ≥10 mm; eligible footprint differs by month.',
 'July and August have similar area-weighted monthly rainfall totals, around 75 millimetres. The lower maps ask how much of each month’s rain falls within its wettest five-day window. Among cells receiving at least ten millimetres that month, the area receiving half its rain in five consecutive days rises from about 44 percent in July to 78 percent in September. Eligible areas differ by month. Monthly totals therefore conceal concentration, and this diagnostic does not by itself establish flooding. Timing also matters when conditions continue across consecutive days.',
 'Figure 23 retains totals on the top row and concentration below. Large callout states the conditional percentages, with its eligibility rule immediately below.',
 'Point at July/August totals first. Move to the concentration row for July/September. Make clear that September’s monthly total is lower, not equal to July/August.')
add('Contour spacing changes visible boundary detail','Sindhoor',260,278,'contours',['contours.png'],
 'The field stays fixed while the interval changes',
 'Finer contours reveal more boundaries, which does not mean the field changed.',
 'Report Fig. 19. Same 22 August 2023 Tmax field; line/fill and 5°C/10°C intervals.',
 'Contour maps show temperature’s spatial structure. Coarse intervals simplify the pattern, while finer intervals expose additional boundaries in the same field. Here we compare filled contours. We then ask how often hot and dry conditions occur, and how long they last.',
 'Figure 19 presentation redraw: enlarge the filled-contour 5°C and 10°C pair. Line-only variations remain in the report. Keep units and labels visible.',
 'Indicate one coarse/fine comparison. Avoid tracing multiple geographic boundaries.')
add('Event frequency differs from uninterrupted duration','Sindhoor',278,325,'persistence',['persistence.png'],
 'Longest observed local hot–dry run: 67 days',
 'Frequency tells how often; persistence tells how long without interruption.',
 'Report Fig. 30 A–B. Hot: Tmax ≥35°C. Dry: rainfall <1 mm/day. All 92 days; 13,416 common cells.',
 'We define a hot day as a maximum temperature of at least 35 degrees Celsius, and a dry day as rainfall below one millimetre. The frequency map counts qualifying days. The persistence map records the longest uninterrupted run. A count alone cannot tell us whether events were consecutive. The longest local run reaches 67 days within this observation window. That result describes one location rather than the entire area, and the run may extend beyond the observed boundaries. Three months also cannot establish a long-term climate trend. This answers another part of our main question: an aggregate count can hide the temporal order that determines persistence.',
 'Large crop of Figure 30’s frequency and persistence maps, with both legends. Thresholds and the 92-day support remain visible. Omit the lower sensitivity panels during the video.',
 'Spend time distinguishing the left percentage scale from the right day scale. Pause at the persistence map. State “local” and “within this window” when giving 67 days.')
add('Wind arrows emphasize either speed or direction','Varshith',325,343,'quiver',['quiver.png'],
 'Proportional length: speed. Equal length: direction.',
 'Sampling controls which local detail remains visible.',
 'Report Fig. 26. Same western-US 22 August field. Flow TO-direction; source wind is FROM-direction at 10 m.',
 'For wind, proportional arrows encode speed, while equal-length arrows emphasize direction. Reducing arrow density improves readability but can remove local detail. We explain the encoding and sampling before interpreting the pattern. The final question is how often the separate weather conditions coincide.',
 'Figure 26 presentation redraw: two large panels compare proportional and equal length on the same every-eighth-cell sample. The report retains the every-fourth/eighth/twelfth sampling experiment. Keep the speed key.',
 'Compare left/right length encodings on identical sampled positions. Mention the report’s thinning comparison without claiming that this slide changes density. Do not present daily wind as gust speed or a trajectory.')
add('Separate frequencies conceal joint occurrence','Varshith',343,360,'intersections',['intersections.png'],
 'Hot, dry and windy together: 2.57% of weighted area-days',
 'Individual condition frequencies cannot establish their overlap.',
 'Report Fig. 29. Hot ≥35°C; dry <1 mm/day; windy ≥5 m/s. Exact intersections, daily gridded values.',
 'The intersection plot shows that hot, dry and windy conditions occur together in about 2.57 percent of weighted area-days. Looking at each separate frequency cannot reveal that overlap. We now have evidence for the three ways summaries can hide information.',
 'Large intersection chart. Clearly label the hot–dry–windy column and retain the membership dots connecting it to its definition.',
 'Point to the three filled membership dots and their bar. Say “weighted area-days”, not “percent of days” or “percent of the population”.')
add('What the combined evidence tells us','Varshith',360,384,'conclusion',[],
 'Averages hide differences. Summaries hide timing. Separate measures hide overlap.',
 'Complementary views support conclusions with explicit units and limits.',
 'Synthesis of report Figs. 3, 11–12, 18, 23, 26, 29–30 and the matched-change comparison.',
 'Averages hide differences between countries and places. Snapshots and totals hide trajectories, concentration and persistence. Separate variables hide joint occurrence, and associations between levels need not explain changes. Complementary visualizations reveal these missing details through consistent scales, matched comparisons and explicit definitions. That is our answer to the main question, with conclusions restricted to the evidence and its limits.',
 'Three clear conclusion rows. Each names the hidden information and cites its report evidence. No new chart or new finding.',
 'Finish the opening question explicitly. Allow a brief pause after the final sentence.')
add('Team responsibilities and sources','Silent closing card',384,390,'credits',[],
 'DAS732 Assignment 2 · Team Plot Twist','',
 'Country indicators: OWID/ITU via A1. Weather: gridMET. Methods and complete bibliography in the report.',
 '', 'Three named members and IDs, their allocated Infovis/SciVis methods, plus report and local demo paths. Six seconds of raw footage.',
 'Hold the card silently. It is already included in the 6:30 timeline. The allocation does not certify unconfirmed completed work.')

from revise_video_internet import revise
revise(SLIDES,ASSETS)
assert len(SLIDES)==17 and sum(s['duration'] for s in SLIDES)==390
assert all(a['end']==b['start'] for a,b in zip(SLIDES,SLIDES[1:]))
def stamp(t):return f'{t//60}:{t%60:02d}'
story=dict(title='Beyond Averages and Snapshots',raw_seconds=390,export_speed=1.35,
 final_seconds=390/1.35,slides=SLIDES,metrics=dict(rho_level=rho_level,rho_change=rho_change))
(OUT/'storyboard.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf-8')

intro='''# Final recording script and slide-by-slide screen guide

Use this guide with **DAS732_A2_Video_Presentation.pptx**. It supersedes the earlier video scripts.

**Main question:** What do averages and snapshots hide about inequality, relationships and change over time?

The continuous story moves from country profiles to unequal progress, tests infrastructure relationships, then examines weather scales, rainfall timing, persistence and joint occurrence. Every main result contributes to the opening question.

## Recording duration

The complete raw recording is **6:30**, including transitions, browser demonstration and the closing card. Export at **1.35× for about 4:49** with pitch preservation. At 1.4× it becomes about 4:39. At 1.3× it is exactly 5:00, leaving no buffer. Each member has 2:10 raw across two appearances. Timings are recording targets; rehearse once and adjust pauses without rushing labels or interaction.

## What changes in slide quality

The deck uses original report evidence, enlarged panels, editable headlines and numerical callouts, contrasting analytical layouts, and a conclusion tied to the main question. It contains eight main result figures plus a direct matched-level/change comparison. Supporting method slides and browser demonstrations provide implementation coverage. No report-page screenshots or paragraphs of narration appear on the slides.

## Before recording

1. Run `python ass2/run_visualizations.py --no-browser` from the workspace, or double-click `ass2/START_VISUALIZATIONS.cmd`.
2. Open `http://127.0.0.1:8765/web/index.html` and `http://127.0.0.1:8765/web/treemap.html` in separate prepared tabs. Allow data to load.
3. Open the presentation in slideshow mode. Record slides 1–6, then the browser for slides 7–8, and return to slide 9. For a clean cut, record each scene separately and assemble in the listed order.
4. Record at 1920×1080. Hide notifications and keep the cursor away from labels. Slides 7–8 contain reference stills, which must be replaced by actual browser footage when demonstrating interaction.
5. PowerPoint speaker notes contain the same narration and screen actions. The HTML slide viewer is an alternative: arrow keys change slides, N toggles private notes, and F enters fullscreen. Keep notes hidden during recording.

## Master timeline

| Slide | Raw time | Speaker | Screen title |
|---|---|---|---|
'''
md=intro+'\n'.join(f"| {s['number']} | {stamp(s['start'])}–{stamp(s['end'])} | {s['speaker']} | {s['title']} |" for s in SLIDES)
for s in SLIDES:
    images='; '.join('`output/video_presentation/assets/'+x+'`' for x in s['images']) or 'Editable text and native shapes; no new plot.'
    md+=f"\n\n## Slide {s['number']}: {s['title']}\n\n**Raw time:** {stamp(s['start'])}–{stamp(s['end'])} ({s['duration']} seconds). **Speaker:** {s['speaker']}.\n\n**What is on screen:** {s['screen']}\n\n**Exact image files:** {images}\n\n**Evidence:** {s['source']}\n\n**Screen actions:** {s['actions']}\n\n**Say continuously:**\n\n{s['say'] or '[Silent closing card]'}\n\n**Main point:** {s['takeaway'] or s['headline']}"
md+='''

## Final review against the previous feedback

- Every result has visible evidence and an inference. The title and spoken conclusion explain why the plot matters.
- The strongest report visuals feature centrally: infrastructure profiles, inequality, country gains, rainfall concentration, persistence and intersections.
- The main question remains continuous through explicit handoffs. Internet and weather remain separate investigations.
- Check the export at its accelerated speed. A readable still is more useful than multiple graphics disappearing too quickly. If needed, shorten redundant wording and preserve viewing time.
- The contribution table lists the adopted responsibilities. Verify actual completed implementation and personal AI disclosures before submission.

The rendered deck and script do not contain a completed video or claim that a live browser recording has already been made.
'''
(OUT/'RECORDING_SCRIPT.md').write_text(md,encoding='utf-8')
(OUT/'CONTINUOUS_NARRATION.txt').write_text('\n\n'.join(f"{s['speaker']} — {stamp(s['start'])}\n{s['say']}" for s in SLIDES if s['say']),encoding='utf-8')
words=sum(len(s['say'].split()) for s in SLIDES)
(OUT/'README.md').write_text(f'''# Assignment 2 video presentation

- `DAS732_A2_Video_Presentation.pptx`: editable slide text/callouts and original evidence graphics, with full speaker notes.
- `RECORDING_SCRIPT.md`: authoritative slide-by-slide script, timing, exact images and screen actions.
- `CONTINUOUS_NARRATION.txt`: narration-only reading copy.
- `index.html`: keyboard-controlled slide preview. Open locally after extracting the folder.
- `slides/`: individual high-resolution PNGs.
- `assets/`: original figure excerpts, presentation redraws and the level/change evidence CSV.
- `storyboard.json`: machine-readable timeline and source mapping.

17 slides, {words} spoken words, 6:30 total raw recording. At 1.35×, approximately 4:49.
The browser portions must be recorded from the running JavaScript pages. No finished video is included.
''',encoding='utf-8')
print(json.dumps(dict(slides=len(SLIDES),words=words,raw_seconds=390,export_seconds=390/1.35),indent=2))
# Retain the enlarged, controlled weather comparisons when rebuilding internet scenes.
import runpy
runpy.run_path(str(ROOT/'scripts/render_video_weather.py'),run_name='__main__')
