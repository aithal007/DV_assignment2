"""Prepare the internet-first recording story, source assets and design plan.

Report charts stay unchanged. Existing scientific images are copied or cropped;
no illustrative images are synthesized. Both slide formats share one storyboard.
"""
from pathlib import Path
from PIL import Image
import json,shutil,zipfile,hashlib,csv

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/video_presentation'
PROJECT=ROOT/'presentation_source/internet_weather_ppt169_20261024'
IMAGES=PROJECT/'images'
SKILLS=ROOT/'tmp/presentation_skills'

def stamp(t):return f'{int(t)//60}:{int(t)%60:02}'

def prepare():
    backup=ROOT/'archive/before_internet_first_slides_20261024.zip'
    if not backup.exists():
        with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
            for p in OUT.rglob('*'):
                if p.is_file():z.write(p,p.relative_to(ROOT))
            for p in [ROOT/'PRESENTATION_PLAN.md',ROOT/'output/pdf/DAS732_A2_Recording_Script.pdf']:
                if p.exists():z.write(p,p.relative_to(ROOT))
    IMAGES.mkdir(parents=True,exist_ok=True)
    (PROJECT/'notes').mkdir(exist_ok=True)
    manifest=json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    assets={}
    def take(name,num,box=None):
        src=ROOT/manifest[num-1]['path'];dest=IMAGES/(name+'.png')
        if box:
            with Image.open(src) as im:
                w,h=im.size;im.crop(tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(box))).save(dest)
        else:shutil.copy2(src,dest)
        assets[name]=dict(file=dest.name,source=src.relative_to(ROOT).as_posix(),figure=num,crop=box)
    for name,num in [('network',1),('country_paths',2),('nodetrix',3),('pcp_detail',4),('pcp_focus',5),('matrix',6),('changes',7),('treemap_region',8),('treemap_adoption',9),('milestones',10),('within_regions',11),('regional_gains',12),('horizons',13),('ridges',16),('monthly_change',21),('rainfall',23),('hot_frequency',24),('quiver',26),('wind_roses',27)]:take(name,num)
    take('persistence',30,(0,.055,1,.565))
    # These presentation figures already exist and use the report's source data.
    for name in ['horizon','country_paths']:
        existing=OUT/'assets'/f'{name}.png'
        if existing.exists():
            dest=IMAGES/f'{name}_focus.png';shutil.copy2(existing,dest)
            assets[name+'_focus']=dict(file=dest.name,source=existing.relative_to(ROOT).as_posix(),figure=13 if name=='horizon' else 2,crop=None)
    for kind in ['global','local','contour']:
        src=ROOT/f'images/scivis/scivis_{kind}.gif';shutil.copy2(src,IMAGES/src.name)
        with Image.open(src) as im:
            im.seek(0);im.convert('RGB').save(IMAGES/f'scivis_{kind}_poster.png')
        assets['gif_'+kind]=dict(file=src.name,source=src.relative_to(ROOT).as_posix(),figure=19 if kind=='contour' else 18,crop=None)
    (PROJECT/'analysis/asset_sources.json').write_text(json.dumps(assets,indent=2),encoding='utf-8')
    slides=[];time=0
    def add(id,title,speaker,duration,layout,theme,images,headline,takeaway,say,screen,actions,figs,transition):
        nonlocal time
        slide=dict(number=len(slides)+1,id=id,title=title,speaker=speaker,start=time,end=time+duration,duration=duration,
            layout=layout,theme=theme,chapter='Internet' if len(slides)<12 else 'Weather',images=[assets[k]['file'] for k in images],
            headline=headline,takeaway=takeaway,say=say,screen=screen,actions=actions,figures=figs,
            source=('Report Fig. '+', '.join(map(str,figs)) if figs else 'Report: central question, dataset, discussion and author allocation'),transition=transition)
        slides.append(slide);time+=duration
    add('main-question','What do averages and snapshots hide?','Parikshith',10,'SWISS-COVER-ASCII','hero dark',[],
        'Beyond averages\nand snapshots','Inequality, relationships and change over time',
        'Our question is what averages and snapshots hide. We finish the country internet story first, then examine the same problem in daily weather.',
        'Large question and an internet-to-weather reading order. Team names remain visible.',
        'Begin immediately. Advance after stating the two-part order.',[],
        'Start with the links between countries.')
    add('same-network','Same links, different layouts','Parikshith',18,'S22','light',['network'],
        '179 countries. 590 links.','Drawing distance does not define a neighbor.',
        'These layouts contain the same 179 countries and 590 links. Follow India: its six linked neighbors stay the same, even when the circle stretches their separation. The links describe similar measured country profiles, not physical internet cables.',
        'Three network layouts with India and the same six links highlighted.',
        'Point to India and its colored links across the three panels. Do not infer a link from visual proximity.',[1],
        'Inspect the links hidden inside a crowded group.')
    add('inside-nodetrix','Look inside a country group','Parikshith',22,'S08','light',['nodetrix'],
        '18 of 28 possible links','A group can contain both dense rows and missing links.',
        'NodeTrix replaces each group with a matrix. A teal cell joins its row country to its column country; white means no link. The enlarged eight-country group contains eighteen links. Cuba and Palestine each connect to six members, while Laos connects to three. The mirrored cells repeat undirected links; the diagonal is excluded.',
        'NodeTrix overview alongside the enlarged G7 matrix. The large annotation identifies 18 of 28 possible pairs.',
        'Trace the Cuba row to the Palestine column. Then point to the white Cuba-Dominican Republic cell. Count each pair once.',[3],
        'A shared profile today still does not show its history.')
    add('country-routes','Similar progress, different paths','Parikshith',15,'S08','dark',['country_paths_focus'],
        '+48.1 points with only +0.7 broadband','China gains +35.8 points with +24.6 broadband subscriptions per 100.',
        'South Africa gains forty-eight adoption points while fixed broadband barely rises. China gains thirty-six points alongside much larger broadband growth. These annual paths show different infrastructure histories that a final value would hide.',
        'Two focused annual paths: South Africa and China, with the same axes.',
        'Follow the open 2010 dot to the filled 2020 dot in each panel.',[2],
        'Check the wider set of measurements through brushing.')
    add('parallel-brush','Six highlighted country profiles','Varshith',25,'S22','light',['pcp_focus'],
        '6 of 175 countries','At least 70% online; at most 5 fixed-broadband subscriptions per 100.',
        'The parallel plot keeps four measurements connected for each country. I select high internet use and low broadband. Six countries stay highlighted against the other profiles. The brush controls let me refine this selection. Bundling changes the curves but preserves their measured intersections. Clicking an axis heading changes the order we can follow.',
        'Highlighted report selection, followed by a live JavaScript demonstration from the matching page.',
        'Before recording, open web/index.html?year=2020&bundle=50&matched=1&fixed=1. Click Inspect high adoption / low broadband and confirm the six names. Briefly drag one brush, restore the preset, change bundling, and click an axis heading to reorder. Record real browser interaction, then return to the deck.',[4,5],
        'The user count also depends on how we group countries.')
    add('treemap-order','The same users, two hierarchies','Varshith',20,'S16','light',['treemap_region','treemap_adoption'],
        '4.52 billion included users','Area counts users. Country color shows the percentage online.',
        'Both treemaps contain the same included users. Area shows their number, while color shows national adoption. Asia holds about fifty-seven percent of these users. Switching the hierarchy to adoption bands reveals that the fifty-to-seventy-five-percent band is slightly larger than the highest band. Zooming exposes the countries without changing their values.',
        'Region-first and adoption-first root views, then a brief live zoom and hierarchy switch.',
        'Use the treemap browser page: region-first root, click Asia, return to root, switch to adoption-first and hover a country. Keep the denominator visible.',[8,9],
        'Now compare all four variables directly.')
    add('pairwise-matrix','The full four-variable picture','Varshith',12,'S08','dark',['matrix'],
        '0.83 versus 0.53','Broadband has the stronger adoption association; landlines and broadband reach 0.87.',
        'The matrix adds all six variable pairs and their distributions. Broadband tracks adoption more closely than mobile does. The scatter cells retain exceptions that the correlation numbers alone hide.',
        'The complete scatterplot matrix with three enlarged coefficient annotations.',
        'Point to broadband/adoption, mobile/adoption, then landline/broadband. Do not read every cell aloud.',[6],
        'Country levels and country changes are different questions.')
    add('matched-changes','Internet use rose as landlines fell','Varshith',8,'S07','hero light',[],
        '72%','126 of the same 175 countries, 2015-2020.',
        'In seventy-two percent of matched countries, adoption rises while landlines fall. A level relationship does not explain every country’s change.',
        'Large 72% figure beside regional percentage bars based on the report counts.',
        'Use the overall number and the regional bars as the internet-change conclusion.',[7],
        'Do regional averages describe their individual countries?')
    add('within-region','A region leaves much of the spread hidden','Sindhoor',20,'S20','light',['within_regions'],
        '47% within regions','Nearly half of measured country variation sits inside the regional groups.',
        'The dark ticks are regional means, but the dots show countries spread far apart. About forty-seven percent of measured variation lies within regions. This is a share of variance, not a share of users. A regional label therefore gives only part of the picture of a country’s internet use.',
        'Country dots and regional means, with a large 47% figure and a within/between split.',
        'Point to the countries surrounding one regional mean, then the 47/53 split.',[11],
        'Even a regional gain can describe a different calculation.')
    add('paired-gains','Regional progress and country gains differ','Sindhoor',20,'S08','dark',['regional_gains'],
        '26.55 versus 19.75 points','Asia: shift in regional median versus median of individual country gains.',
        'For Asia, subtracting the regional medians gives a twenty-six-point rise. Calculating each country’s gain first gives a median gain of about twenty points. The middle country can change between dates, so these answers need not agree. The paired country dots also show the range hidden behind either summary.',
        'The endpoint and paired-gain panels, with the two Asia values enlarged.',
        'Read Asia across the panels; compare the black regional-shift tick with the open median-gain circle.',[12],
        'Annual views recover when countries make progress.')
    add('horizon-timing','The endpoint hides the time of arrival','Sindhoor',13,'S22','light',['horizon_focus'],
        '2003 / 2015 / not by 2020','First observed majority use: Singapore, China and Tanzania.',
        'Singapore crosses fifty percent in 2003; China in 2015. Tanzania stays below it. Horizon rows retain this timing. Red means below the reference, not falling adoption.',
        'Focused three-country horizon rows with milestone labels.',
        'Follow each row from left to right; identify the first blue band.',[13,14],
        'Distributions show whether progress brings countries closer together.')
    add('distribution-paths','Progress still leaves a wide distribution','Sindhoor',12,'S22','light',['ridges'],
        '2.2% → 71.4%','The country median rises, while regional paths and spreads remain different.',
        'Ridgelines show the distribution, not just its median. Regions progress at different times and stay widely spread. Country ticks help check the smooth curves, especially for small groups.',
        'Region-faceted ridgelines on a common adoption scale, with the global median change highlighted.',
        'Compare Europe and Africa horizontally. Treat ridge height as shape, not country count.',[15,16],
        'The internet section is complete; now change datasets.')
    add('weather-data','Daily weather: the same summary problem','Parikshith',10,'S03','hero dark',[],
        '92 days. One shared area.','July-September 2023 | 13,416 valid grid cells | four weather fields',
        'The internet story is complete. Now we use a separate dataset: ninety-two days of temperature, rain and wind, covering the same valid cells.',
        'Weather chapter divider with period, daily coverage, spatial mask and sampled-animation dates.',
        'Make a clear section transition. State that the internet and weather tables are not joined.',[],
        'First check whether colors keep their meaning across dates.')
    add('color-gifs','The same color can change its meaning','Parikshith',25,'S08','light',['gif_global','gif_local'],
        'Fixed scale / daily scale','The two GIFs stay on this slide and loop through the same eight dates.',
        'These animations use identical fields. On the left, one fixed scale lets the same color mean the same temperature on every date. On the right, each date gets its own range, making local differences clearer but changing the meaning of a color. Watch the legends as the eight dates repeat.',
        'Two embedded animated GIFs, fixed limits on the left and daily limits on the right.',
        'Stay in desktop PowerPoint Slide Show. Both GIFs loop automatically every 6.4 seconds. Allow at least two full loops; point to the changing right color bar. Do not open an external animation player.',[17,18],
        'Use complete months to check the actual seasonal change.')
    add('complete-months','Complete months show widespread cooling','Parikshith',12,'S22','light',['monthly_change'],
        '−4.64°C','September minus July mean daily maximum temperature; 99.66% of the area cools.',
        'Complete months show average cooling of four-point-six degrees. Comparing the first and last sampled days reverses the sign over eighteen percent of the area. Snapshots can misrepresent monthly change.',
        'Monthly difference map and cumulative distributions, with the mean change enlarged.',
        'Point to the negative change map, then distinguish the monthly result from the two-date comparison.',[20,21,22],
        'Monthly rainfall totals also leave out timing.')
    add('rain-bursts','The monthly total hides short bursts','Parikshith',18,'S16','dark',['rainfall'],
        '77.6%','Of eligible September area receives at least half its monthly rain in five days.',
        'July and August average about seventy-five millimeters of rain. But in September, more than three-quarters of eligible area receives at least half its rain in five days. Totals hide whether rain arrives steadily or in a burst.',
        'Monthly totals above five-day concentration maps, with the September share emphasized.',
        'Compare corresponding top and bottom maps. Mention that concentration uses cells with at least 10 mm monthly rain.',[23],
        'Contours test another way the drawing changes visible detail.')
    add('contour-animation','Contours expose temperature boundaries','Sindhoor',25,'S22','light',['gif_contour'],
        'One animated field, explicit levels','Contour tracing follows neighboring cells; the display interval controls boundary detail.',
        'The contour animation is embedded here. It follows the same eight sampled dates and keeps its stated levels. Smaller intervals show more boundaries; filled bands make broad warm and cool areas easier to compare. The tracing uses the Marching Squares family on a regular grid. More lines add display detail, not new observations.',
        'One large embedded contour GIF with a short interval comparison from the report in the spoken explanation.',
        'Let the GIF complete at least two loops. Keep the temperature scale visible; explain the 5- versus 10-degree comparison from report Fig. 19. No external player.',[19],
        'Counting hot days answers a different question from a mean.')
    add('hot-day-frequency','Hot-day frequency falls across the months','Sindhoor',15,'S22','light',['hot_frequency'],
        '22.8% → 2.2%','Weighted mean hot-day frequency, July to September; hot means Tmax ≥35°C.',
        'These maps count days reaching thirty-five degrees. Mean frequency falls from about twenty-three percent in July to two percent in September. Frequency does not say whether those days form one continuous spell.',
        'Three monthly frequency maps on one percentage scale.',
        'Compare July and September with the same color scale. Lead directly into run length.',[24],
        'A long run is not the same as a high event count.')
    add('persistent-runs','Frequency is different from persistence','Sindhoor',25,'S08','dark',['persistence'],
        '67 consecutive days','Hot-dry frequency: 16.27% of weighted grid-cell days.',
        'Hot-dry conditions account for sixteen percent of weighted cell-days, while one location has a sixty-seven-day uninterrupted run. The frequency map and longest-run map therefore describe different things. Daily area coverage adds another comparison: how much of the region is affected at once. Changing the temperature and rainfall thresholds also changes the measured result.',
        'Frequency and persistence maps, supported by the exact threshold definition.',
        'Point to the two maps and the 67-day maximum. Hot means Tmax >=35°C; dry means rain <1 mm/day. Do not label this an official drought or heatwave index.',[30],
        'Wind requires careful choices about direction and speed.')
    add('wind-arrows','Wind arrows trade detail for readability','Varshith',20,'S16','light',['quiver'],
        'Density / direction / speed','The field stays fixed while arrow spacing and length rules change.',
        'Dense arrows keep more locations but can overlap. Wider spacing makes direction easier to read. Speed-scaled lengths encode magnitude; equal lengths leave speed to color. We convert the source wind-from direction so arrows point toward the flow. These are daily ten-meter winds, not parcel paths.',
        'The same six quiver panels as the report, with proportional and equal-length rows.',
        'Compare the rows and sampling gaps. Explain the from/to convention once.',[26],
        'Monthly direction summaries reveal another hidden change.')
    add('wind-months','The dominant wind source changes','Varshith',15,'S22','light',['wind_roses'],
        'Southwest → south','July’s modal source sector differs from August and September.',
        'The largest wind-source sector changes from southwest in July to south later. A common radial scale makes frequencies comparable, and color adds speed. These summaries no longer identify each location.',
        'Three monthly wind roses sharing the same radial maximum and speed bins.',
        'Point to the July southwest sector and the later south sectors. Read radial height as frequency.',[27],
        'Finally check the conditions together in the same cells and days.')
    add('joint-conditions','Common conditions have a smaller overlap','Varshith',12,'S07','hero dark',[],
        '2.57%','Hot + dry + windy, together in the same grid cell and day.',
        'Dry conditions are common, but the hot-dry-windy combination occurs on only two-point-six percent of weighted cell-days. Separate frequencies cannot identify that overlap in place and time.',
        'Four bars for hot, dry, windy and the all-three joint event, with the joint value highlighted.',
        'Point to dry versus all-three. Do not add the first three overlapping percentages.',[28,29],
        'Bring the country and weather findings back to the main question.')
    add('answer','What the additional views reveal','Varshith',12,'S10','light',[],
        'Differences. Timing. Coincidence.','The missing detail changes the answer.',
        'Our answer is that averages hide differences inside groups, snapshots hide the path and timing, and separate summaries hide coincidence. The extra views restore those details while keeping the measurements consistent.',
        'A short closing comparison of the internet and weather evidence, tied to the main question.',
        'Conclude without introducing a new result. Advance to the silent credit card.',[],
        'Finish on the team and source card.')
    add('credits','Team and sources','Silent closing card',6,'S21','hero dark',[],
        'Team Plot Twist','DAS732 · Assignment 2',
        '',
        'Names, IDs, required method allocation and source datasets.',
        'Hold for six seconds. Stop recording. Keep the closing credit within the Varshith recording block.',[], '')
    assert time==390 and len(slides)==24
    assert [s['chapter'] for s in slides]==['Internet']*12+['Weather']*12
    for speaker in ['Parikshith','Sindhoor','Varshith']:
        seconds=sum(s['duration'] for s in slides if s['speaker']==speaker)+(6 if speaker=='Varshith' else 0)
        assert seconds==130,(speaker,seconds)
    story=dict(title='Beyond Averages and Snapshots',slides=slides,raw_seconds=390,export_speed=1.35,
        final_seconds=390/1.35,words=sum(len(s['say'].split()) for s in slides),animation_slides=[14,17],
        sources='Current 25-page report and its figure manifest; original three eight-frame weather GIFs.',
        design_skills={'ppt-master':'https://github.com/hugohe3/ppt-master','guizang-ppt-skill':'https://github.com/op7418/guizang-ppt-skill'})
    (PROJECT/'storyboard.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf-8')
    plan(PROJECT,slides,assets)
    print(json.dumps(dict(slides=24,raw_seconds=time,final_seconds=round(time/1.35,1),spoken_words=story['words']),indent=2))
    return story

def plan(project,slides,assets):
    # The user delegated design decisions earlier: "do whatever the best".
    # Record that delegation, never fabricate an approval receipt.
    directions='''# Design decisions

User delegation: the earlier instruction "do whatever the best" carries into this explicitly requested slide/script update. The latest instruction fixes Internet first, Weather second and embedded GIFs. No approval UI receipts are synthesized.

1. Swiss evidence sequence (selected): strong type contrast, one IKB blue accent, changing evidence layouts and deliberate light/dark rhythm. Best suited to an assessed data-visualization video with legible charts and short narration.
2. Magazine field notes: warm paper and editorial type. Attractive for a longer talk, but the chart and GIF evidence needs a more direct hierarchy in this short recording.
3. Dark dashboard: continuous dark surfaces and compact panels. Rejected because it repeats the old deck's structure and compresses labels.

Production: 24 scenes, 16:9, 6:30 raw and about 4:49 after 1.35x export. Human narration, full speaker notes, no synthesized audio. GIFs remain original eight-frame looping files and are not assigned entrance effects. Live JavaScript interaction remains on two internet scenes. Slides use the report's evidence rather than invented visual examples.

Source code and native export use PPT Master. Browser presentation uses Guizang's actual Swiss template, registered layout identities, stable note IDs, and its presenter runtime. The two formats share this storyboard.
'''
    (project/'design_decisions.md').write_text(directions,encoding='utf-8')
    rows='\n'.join(f'| P{s["number"]:02} | {s["layout"]} | {s["theme"]} | {s["title"]} | {s["speaker"]} | {stamp(s["start"])}-{stamp(s["end"])} |' for s in slides)
    (project/'page_plan.md').write_text('# Page, theme and recording plan\n\n| Page | Guizang layout | Theme | Purpose | Speaker | Raw time |\n|---|---|---|---|---|---|\n'+rows,encoding='utf-8')
    resources=[]
    used={name for s in slides for name in s['images']}
    for key,a in assets.items():
        if a['file'] not in used:continue
        with Image.open(IMAGES/a['file']) as im:w,h=im.size
        resources.append(f'| {a["file"]} | {w}x{h} | {w/h:.3f} | Report evidence | Scientific figure | Contain and preserve labels | no-crop | user | Existing | {a["source"]} | preserve | evidence |')
    spec='''<!-- ppt-master-schema: design-spec/v1 -->
# Internet and Weather - Design Spec

## I. Project Information

| Item | Value |
|---|---|
| Project Name | Internet and Weather |
| Canvas Format | PPT 16:9 |
| Page Count | 24 |
| Primary Language | en-IN |
| Target Audience | DAS732 instructors assessing a three-member visualization assignment |
| Communication Intent | Explain what summaries hide, show the required visual methods, and support a short assessed recording |
| Desired Audience Outcome | Distinguish country levels from histories, regional summaries from individual changes, and weather totals from timing and coincidence |
| Core Message / Ask / Action | Averages hide individual differences; snapshots hide histories; separate summaries hide overlap |
| Delivery Context | Human-recorded assignment video; all Internet scenes precede Weather; 6:30 raw, 1.35x edit, below five minutes |
| Artifact Afterlife | Editable PowerPoint, browser rehearsal deck, synchronized script and source evidence |
| Reading Mode | presentation |
| Content Strategy | Current report is authoritative; select decisive views, keep all required methods, use plain English |
| Design Style | Custom Swiss evidence sequence using Guizang layout vocabulary |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — explicit script request |
| Custom Animations | disabled — original embedded GIF playback and restrained page transitions; user records spoken delivery manually |
| Narration Audio | disabled — user/team records the video; no synthesized voice requested |
| Created Date | 2026-10-24 |

## II. Canvas Specification

| Property | Value |
|---|---|
| Format | PPT 16:9 |
| Dimensions | 1280 x 720 |
| viewBox | `0 0 1280 720` |
| Margins | 48 px |
| Content Area | 48, 40 to 1232, 660 |

## III. Visual Theme

### Theme Style
- **Mode**: custom
- **Mode Behavior**: Evidence-led explanation. Complete Internet first, then Weather. Keep each scene aligned to its spoken claim.
- **Visual style**: custom
- **Visual Style Behavior**: Swiss hierarchy, IKB accent, light and dark surfaces, large thin display numerals and varied registered compositions. Scientific chart colors retain their meaning.
- **Theme**: Guizang Swiss IKB
- **Tone**: Clear, academic, direct

### Color Scheme
| Role | HEX | Purpose |
|---|---|---|
| Background | #FAFAF8 | Paper |
| Secondary background | #F0F0EE | Neutral surface |
| Primary | #0A0A0A | Ink |
| Accent | #002FA7 | Main emphasis |
| Secondary accent | #D4D4D2 | Neutral comparison |
| Body text | #0A0A0A | Body |
| Secondary text | #737373 | Sources |
| Divider | #D4D4D2 | Hairlines |

## IV. Typography System

### Font Plan
| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
|---|---|---|---|---|
| Title | Light sans serif | Segoe UI Light | | Arial |
| Body | Clear sans serif | Segoe UI | | Arial |

- **Title stack**: Segoe UI Light, Arial
- **Body stack**: Segoe UI, Arial

### Font Size Hierarchy
| Purpose | Anchor Size (px) |
|---|---:|
| Body | 28 |
| Title | 44 |
| Subtitle | 32 |
| Annotation | 20 |
| Display | 104 |
| Source | 14 |
| Caption | 24 |
| Label | 16 |
| Display medium | 80 |
| Display large | 192 |
| Statistic | 64 |

## V. Layout Principles

### Deck-wide Direction
- **Hierarchy direction**: Finding, evidence, one reading cue
- **Composition tendency**: Alternate image heroes, comparisons, hero numbers, ledgers and chapter statements
- **Cross-page continuity**: One accent and type ramp; chapter order fixed; repeated measures keep their units
- **Spacing posture**: Open scenes around dense scientific evidence
- **Spacing anchors**: 48, 24, 32, 0, 34

## VI. Icon Usage Specification
- **Primary bundled library**: none

| Icon Path | Suitable Scenarios |
|---|---|

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
|---|---|---|---|---|---|---|---|---|---|---|---|
'''+ '\n'.join(resources)+'\n\n## IX. Content Outline\n'
    for s in slides:
        spec+=f'\n#### Slide {s["number"]:02} - {s["title"]}\n\n- **Audience move**: Read the source evidence and understand its stated distinction\n- **Relationships**: '+('contrast between fixed-scale and daily-scale versions of the same fields' if s['number']==14 else 'none')+f'\n- **Composition**: {s["layout"]}; {s["screen"]}\n- **Title**: {s["title"]}\n- **Core message**: {s["takeaway"]}\n- **Content**: {s["headline"]}\n'
        if s['images']:spec+='- **Images**: '+', '.join(s['images'])+'\n'
        if s['number'] in {8,22}:
            key='regional-changes' if s['number']==8 else 'joint-weather'
            spec+=f'- **Visualization**: {key}: horizontal percentage bars, zero to one hundred percent, using the report CSV values\n- **Native-ready**: {key}=yes\n'
        if s['number'] in {5,6}:
            url='http://127.0.0.1:8765/web/index.html' if s['number']==5 else 'http://127.0.0.1:8765/web/treemap.html'
            spec+=f'- **Hyperlinks**: Live browser demonstration: {url}\n'
    spec+='\n## X. Speaker Notes Requirements\n\n- **Generation**: enabled\n- **Filename**: match each SVG filename under notes/\n- **Content**: Narration, speaker, raw recording range, screen actions and report references from storyboard.json\n- **Total duration**: 390 seconds raw; approximately 289 seconds after 1.35x editing\n- **Notes style**: Plain spoken English\n- **Presentation purpose**: Explain the evidence in the full Internet section, then the Weather section\n'
    (project/'design_spec.md').write_text(spec,encoding='utf-8')
    lock='''<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: en-IN
- audience: DAS732 instructors
- objective: Explain required visualization methods and the evidence for the shared question in a short recorded presentation
- core_message: Averages hide individual differences, snapshots hide histories, separate summaries hide overlap
- consumption_mode: presentation

## mode
- mode: custom
- mode_behavior: Complete Internet before Weather, following the paired script

## visual_style
- visual_style: custom
- visual_style_behavior: Swiss evidence sequence; varied compositions, one IKB accent, light/dark rhythm; retain chart semantics

## colors
- background: #FAFAF8
- primary: #0A0A0A
- accent: #002FA7
- secondary_text: #737373
- divider: #D4D4D2

## typography
- font_family: Segoe UI, Arial
- title_family: Segoe UI Light, Arial
- body_family: Segoe UI, Arial
- body: 28
- title: 44
- subtitle: 32
- annotation: 20
- display: 104
- source: 14
- caption: 24
- label: 16
- display_medium: 80
- display_large: 192
- statistic: 64

## icons
- library: none
- inventory: none

## pptx_structure
- mode: flat

## page_rhythm
'''
    lock+='\n'.join(f'- P{s["number"]:02}: '+('breathing' if 'hero' in s['theme'] else 'dense' if s['number'] in {3,7,10,14,17,20} else 'anchor') for s in slides)
    lock+='\n\n## images\n'+'\n'.join(f'- {k}: images/{a["file"]} | source=user | crop=no-crop' for k,a in assets.items() if a['file'] in used)
    lock+='\n\n## forbidden\n- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`\n'
    (project/'spec_lock.md').write_text(lock,encoding='utf-8')

if __name__=='__main__':prepare()
