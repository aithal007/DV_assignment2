"""Focused evidence-to-conclusion deck; preserves the report's scientific marks."""
from pathlib import Path
import json, shutil, zipfile, re
from PIL import Image
import build_video_v2 as base

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'presentation_source/internet_weather_ppt169_20261024'
P=ROOT/'presentation_source/focused_story_ppt169_20261024'
OUT=ROOT/'output/video_presentation'
NAVY='#102638';PAPER='#F5F2EA';TEAL='#087F83';ORANGE='#D65B32';MUTED='#536878';WHITE='#FFFFFF';PALE='#E3EBEA'

def prepare():
    backup=ROOT/'archive/before_focused_story_20261024.zip'
    if not backup.exists():
        with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
            for f in OUT.rglob('*'):
                if f.is_file():z.write(f,f.relative_to(ROOT))
    for folder in ['images','notes','analysis','validation','svg_output','sources']:(P/folder).mkdir(parents=True,exist_ok=True)
    shutil.copytree(OLD/'images',P/'images',dirs_exist_ok=True)
    shutil.copy2(ROOT/'REPORT.md',P/'sources/REPORT.md')
    def crop(src,name,box):
        with Image.open(P/'images'/src) as im:
            w,h=im.size;im.crop(tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(box))).save(P/'images'/name)
    crop('nodetrix.png','network_group.png',(0,.075,.365,.835))
    crop('nodetrix.png','group_matrix.png',(.455,.065,.999,.926))
    crop('pcp_focus.png','profiles_plot.png',(0,.135,1,.9))
    crop('ridges.png','ridges_africa.png',(0,.085,.333,.52))
    crop('ridges.png','ridges_europe.png',(.675,.085,1,.52))
    crop('quiver.png','wind_short.png',(0,.033,.3015,.495))
    crop('quiver.png','wind_equal.png',(0,.511,.3015,.974))
    crop('quiver.png','wind_scale.png',(.941,.14,1,.84))
    # Preserve each rainfall map and its own colour scale. Only panel order changes.
    crop('rainfall.png','rain_september_total.png',(.602,.081,1,.479))
    crop('rainfall.png','rain_september_burst.png',(.602,.537,.980,.966))
    story=[];clock=0
    def add(id,title,speaker,seconds,chapter,images,claim,say,actions,figures,theme='light'):
        nonlocal clock
        story.append(dict(number=len(story)+1,id=id,title=title,speaker=speaker,start=clock,end=clock+seconds,duration=seconds,
          chapter=chapter,layout='S22' if images else 'S03',theme=theme,images=images,headline=title,takeaway=claim,say=say,
          screen=claim,actions=actions,figures=figures,source='Report Fig. '+', '.join(map(str,figures)) if figures else 'Current report: question and conclusions',transition=claim))
        clock+=seconds
    add('opening','What does the summary leave out?','Parikshith',10,'Internet',[],
      'Look inside groups. Follow the measurements. Check time.',
      'What do averages and snapshots leave out? We examine Internet first, then Weather, following the evidence to a conclusion.',
      'State the main question. Explain that Internet finishes before Weather starts. Do not list every method.',[], 'dark')
    add('nodetrix-read','A group is not one uniform pattern','Parikshith',25,'Internet',['network_group.png','group_matrix.png'],
      'Read one cell before judging the whole group.',
      'First, does a country group mean that every member is closely linked to every other member? We build links from similar internet and telecom measurements. NodeTrix puts each group into a matrix. Follow Cuba along its row to Palestine: the teal cell means a stored link. Follow Cuba to the Dominican Republic: white means there is no link. The grey diagonal compares each country with itself.',
      'Point from the G7 tile in the overview to the enlarged matrix. Trace the Cuba row first to PSE, then DOM. Keep both examples visible. Explain the original graph is profile similarity, not cables.',[1,3])
    add('nodetrix-finding','The same group contains unequal connections','Parikshith',30,'Internet',['group_matrix.png'],
      'Shared membership does not mean identical relationships.',
      'Now look at the pattern rather than one cell. Cuba and Palestine each have six links inside this group, while Laos has three. Of the twenty-eight possible country pairs, eighteen are linked. The repeated cells above and below the diagonal represent the same undirected link, so we count each pair once. The conclusion is that grouping helps organise the network, but it hides important differences unless we inspect the matrix inside it.',
      'Compare the printed row counts: Cuba (6), Palestine (6), Laos (3). Point to the white gaps. Explain 18 links out of 28 possible pairs, not 18 coloured cells. This is a second reading of the SAME figure.',[3], 'dark')
    add('pcp-read','Does high internet use mean high fixed broadband?','Varshith',30,'Internet',['profiles_plot.png'],
      'Follow one country across all four axes.',
      'Next, does high internet use always come with high fixed broadband? In this parallel plot, one line follows the same country across four measurements. Each vertical axis has its own scale. We read values where the line crosses an axis, not from the height of a bend between axes. Faint lines provide the full country context. I now brush for at least seventy percent internet use and at most five fixed-broadband subscriptions per hundred people.',
      'Show the four axes, then point at the two brush ranges. On the live browser page, apply Inspect high adoption / low broadband. Focus on one selected line; do not demonstrate unrelated controls yet.',[4,5])
    add('pcp-finding','Six countries break the simple expectation','Varshith',35,'Internet',['profiles_plot.png'],
      'High adoption can exist with little fixed broadband.',
      'Six of the one hundred and seventy-five matched countries meet both conditions. The highlighted lines start high on internet use and cross low on fixed broadband. The selected countries include Cuba, Kuwait and South Africa. I briefly change the brush, then restore it, to show that this finding comes from a real selection. This tells us fixed broadband alone does not describe internet access. The plot does not measure which connection each person uses, so we cannot claim it proves mobile replaced broadband.',
      'Record the real browser interaction from the slide link: apply the preset, move one brush slightly, then restore it. Keep six names and the 6-of-175 denominator visible. Return to the finding slide. Avoid a tour of every feature.',[5], 'dark')
    add('ridge-finding','Progress does not mean everyone caught up','Sindhoor',40,'Internet',['ridges_africa.png','ridges_europe.png'],
      'Compare where the curves sit AND how widely they spread.',
      'High adoption in selected countries still leaves another question: has progress closed the wider divide? These ridgelines follow the same countries at five dates. Moving right means higher internet use. Each curve shows the spread of countries; the small ticks represent individual countries. In Africa, the median rises from about zero to thirty-two percent, but the final curve remains wide. Europe also moves right and reaches a much higher median. Progress is clear, yet large differences remain within and between regions. Curve height is normalised, so it is not a count of people.',
      'Read the 0–100 horizontal scale once. Trace Africa from 2000 to 2020; point at the wide final curve and the country ticks. Then compare Europe on the SAME scale. These are two labelled panels selected from report Fig. 16, not all regions.',[16])
    add('internet-answer','Internet: three findings, one answer','Sindhoor',25,'Internet',[],
      'A single adoption number cannot describe the whole connection profile.',
      'The internet evidence gives one connected answer. The matrix shows that countries in the same group can have different relationships. The selected profiles show that high internet use can come with little fixed broadband. The ridgelines show that overall progress can leave large gaps. We therefore need to inspect relationships, multiple measurements and the full distribution before calling countries similar or saying the divide has closed.',
      'Use the three numbered evidence statements to recap the reasoning. Introduce no new figure. Pause before the Weather section.',[3,5,16], 'dark')
    add('weather-scales','Weather: can the same colour mislead us?','Parikshith',30,'Weather',['scivis_global.gif','scivis_local.gif'],
      'Read the legend before comparing dates.',
      'We now finish Internet and move to ninety-two days of United States weather. Before interpreting a pattern, we must make a fair comparison. These animations show the same temperature fields. The left legend stays fixed, so a colour keeps the same temperature meaning across dates. The right legend resets each day. That makes local variation clearer, but a similar colour can mean a different temperature. Watch the changing right-hand legend. We use fixed scales when judging change through time.',
      'Stay in desktop PowerPoint Slide Show. Let both embedded GIFs complete at least two 6.4-second loops. Point to each colour bar; do not open another animation window.',[17,18])
    add('rainfall-finding','A monthly total cannot tell us when rain fell','Parikshith',35,'Weather',['rain_september_total.png','rain_september_burst.png'],
      'The same month needs both a total and a timing view.',
      'A fair colour scale still cannot tell us everything. The upper map shows September rainfall totals. The lower map asks a different question: what share of that rain fell in the wettest five consecutive days? Bright areas in the lower map have strongly concentrated rainfall. Across about seventy-eight percent of the eligible area, at least half the monthly rain fell within five days. So a monthly total hides whether rain arrived steadily or in a short burst. We need the daily sequence to recover that timing.',
      'Read the total map first, then follow the downward arrow to the wettest-five-day share. Point at the lower legend. State 77.6% refers to eligible area, not percent of all rain. Eligible grid cells have September rain of at least 10 mm.',[23])
    add('contour-read','Contours let us follow temperature boundaries','Sindhoor',25,'Weather',['scivis_contour.gif'],
      'A contour follows equal temperature, not a state border.',
      'The contour animation offers another way to read those daily fields. Each line follows equal temperature, and the filled bands show temperature ranges. As dates advance, we can follow how these boundaries move. Smaller intervals expose more detail but also create more lines to read. This is why we choose an interval that keeps the important regional pattern visible, rather than adding detail simply because the method allows it.',
      'Let the embedded contour GIF complete two loops. Point to one boundary and its legend value. Explain the 5-degree / 10-degree comparison as a method choice; do not imply both intervals are simultaneously animated.',[19], 'dark')
    add('persistence-finding','How often and how long are different questions','Sindhoor',40,'Weather',['persistence.png'],
      'Frequent hot-and-dry days need not form one long spell.',
      'There is a deeper timing question. The left map counts how often a place was both hot and dry. The right map records its longest uninterrupted hot-and-dry run. Here hot means at least thirty-five degrees, and dry means less than one millimetre of rain that day. A place can have many qualifying days separated by breaks, so frequency alone cannot tell us persistence. The longest run anywhere in this ninety-two-day window is sixty-seven days. That is a local maximum, not a country-wide duration. Reading both maps separates repeated events from sustained conditions.',
      'Read the left frequency legend and the right run-length legend separately. Point to the southwest pattern and compare the maps; do not equate their colours because the units differ. The 67-day maximum is somewhere in the grid and is bounded by the study window.',[30])
    add('quiver-read','Arrow length changes the pattern we notice','Varshith',35,'Weather',['wind_short.png','wind_equal.png','wind_scale.png'],
      'Use length for speed; use equal lengths to inspect direction.',
      'The last example asks whether drawing choices can hide a spatial pattern. Both maps use the same wind field and the same sampled locations. On the left, arrow length grows with speed, so slow winds can be difficult to follow. On the right, equal lengths make directions easier to inspect, while colour still shows speed. The arrows point where the air moves, after converting the source wind-from direction. Neither view changes the measurements. We choose the view according to whether the question is about speed or the direction pattern.',
      'Compare the same western-US area in the two panels. Both retain every fourth sampled grid cell from the source experiment. Point first to short arrows and then to matching equal-length arrows. Use the retained common speed colour key.',[26])
    add('final-answer','What do averages and snapshots leave out?','Varshith',24,'Weather',[],
      'Show the pattern, explain the evidence, state what follows.',
      'Our answer is that summaries leave out differences and time. For Internet, the group label and adoption average miss different country profiles and uneven progress. For Weather, monthly totals and event counts miss bursts and long uninterrupted spells. The strongest explanation therefore pairs the summary with the detail needed for the question, and draws its conclusion from that visible evidence.',
      'Connect each conclusion to the named evidence already shown. Introduce no new numbers or chart. Advance to credits after the final sentence.',[3,5,16,23,30], 'dark')
    add('credits','Team Plot Twist','Silent closing card',6,'Weather',[],
      'Internet complete. Weather complete.', '', 'Hold for six seconds. End recording.',[], 'dark')
    # Keep room to point and run the live brush: fewer words, fuller explanation per figure.
    shorter={
      2:'Does a country group mean every member is linked to every other member? Our links describe similar internet and telecom profiles. NodeTrix puts each group into a matrix. Follow Cuba along its row to Palestine: teal means a stored link. Follow Cuba to the Dominican Republic: white means no link. Grey compares a country with itself.',
      3:'Now compare the rows. Cuba and Palestine each have six links inside this group; Laos has three. Eighteen of twenty-eight possible country pairs are linked. Cells above and below the diagonal repeat the same link, so we count each pair once. The group helps organise the network, but the matrix shows the different relationships and missing links inside it.',
      4:'Does high internet use always come with high fixed broadband? One line follows the same country across four measurements. Each axis has its own scale. Read where the line crosses an axis, not the bend between axes. Faint lines keep the other countries visible. I select at least seventy percent internet use and at most five fixed-broadband subscriptions per hundred people.',
      5:'Six of the one hundred and seventy-five matched countries meet both conditions. Their lines start high on internet use and cross low on fixed broadband. Cuba, Kuwait and South Africa are among them. I change the brush, then restore it, to demonstrate the selection. Fixed broadband alone therefore does not describe internet access. We cannot tell from this plot which connection each person uses.',
      6:'Has progress closed the divide? These ridgelines follow the same countries at five dates. Moving right means higher internet use. Each curve shows the spread of countries; small ticks mark individual countries. Africa’s median rises from about zero to thirty-two percent, but its final curve remains wide. Europe moves right and reaches a much higher median. Progress is clear, yet differences remain within and between regions. Curve height is not a count of people.',
      7:'The internet evidence gives a connected answer. The matrix reveals different relationships inside one group. The selected profiles show high internet use with little fixed broadband. The ridgelines show progress with remaining gaps. A single adoption number cannot describe these differences. We need the relationships, other measurements and the spread of countries before saying the divide has closed.',
      8:'We now move to ninety-two days of United States weather. These animations show the same temperature fields. The left legend stays fixed, so a colour keeps its temperature meaning across dates. The right legend resets each day. Local variation becomes clearer, but the same colour can mean a different temperature. Watch that changing legend. We use fixed scales to compare dates fairly.',
      9:'The upper map shows September rainfall totals. The lower map asks when that rain fell: what share arrived in the wettest five consecutive days? Bright areas have strongly concentrated rain. Across seventy-seven point six percent of the eligible area, at least half the monthly rain fell within five days. A monthly total therefore hides whether rain arrived steadily or in short bursts. Daily observations recover that timing.',
      10:'Each contour line follows equal temperature, while filled bands show ranges. As dates advance, we can follow those boundaries. Smaller intervals expose more detail but create more lines to read. We choose an interval that keeps the regional pattern visible. More detail is useful only when it helps answer the question.',
      11:'The left map counts how often a place was both hot and dry. The right records its longest uninterrupted run. Hot means at least thirty-five degrees; dry means less than one millimetre of daily rain. Many qualifying days can be separated by breaks, so frequency cannot tell us persistence. The longest local run in this ninety-two-day window is sixty-seven days. Reading both maps separates repeated events from sustained conditions.',
      12:'Both maps use the same wind field and sampled locations. On the left, arrow length grows with speed, so slow winds can be hard to follow. Equal lengths on the right make directions clearer; colour still shows speed. Arrows point where air moves, after converting the source wind-from direction. The measurements stay the same. We choose the view according to whether we need speed differences or direction patterns.'}
    for number,speech in shorter.items():story[number-1]['say']=speech
    story[8]['say']=story[8]['say'].replace('upper map','left map').replace('lower map','right map')
    story[8]['actions']='Read the monthly-total map on the left, then the wettest-five-day share on the right. Point to the 0–100% legend. State that 77.6% is eligible area, not a percentage of all rain. Eligible cells have September rainfall of at least 10 mm.'
    story[9]['actions']='Let the embedded contour GIF complete two loops. Point to one boundary and its value on the legend. Explain why changing the interval changes detail; keep the same temperature field as the reference.'
    story[12]['say']=story[12]['say'].replace('adoption average','adoption number')
    data=dict(title='What the summary leaves out',slides=story,raw_seconds=clock,export_speed=1.35,final_seconds=clock/1.35,
      words=sum(len(s['say'].split()) for s in story),animation_slides=[8,10],
      design_skills={'ppt-master':'https://github.com/hugohe3/ppt-master','guizang-ppt-skill':'https://github.com/op7418/guizang-ppt-skill'},
      sources='Current report; six primary analysis figure families, plus original scale and contour GIFs.')
    (P/'storyboard.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
    (P/'SELECTION_AND_STORY.md').write_text('''# Response to the marking feedback

The earlier 24-slide deck moved through too many figures. This revision has 14 slides, six main analysis figures and two short animated method explanations. Repeated plots are deliberate reading stages, not new results. All Internet is complete at 3:15; Weather follows.

## Claim and evidence chain

1. Can a group label describe all relationships? NodeTrix: read cells, then compare degrees and missing links. Conclusion: shared membership does not mean identical relationships.
2. Does high internet adoption imply high fixed broadband? Highlighted parallel coordinates: read the axes, then test a brush. Conclusion: six measured counterexamples; connection mechanism is not established.
3. Does progress imply the divide closed? Two ridgeline panels on the same scale: progress plus remaining spread. Conclusion: within-region and between-region differences remain.
4. Can we trust a visual comparison across dates? Fixed/local temperature scales and contour GIFs: establish how to read fields before interpreting them.
5. Does a monthly total tell the daily story? September total and five-day share. Conclusion: monthly rain can be strongly concentrated in time.
6. Does frequency describe persistence? Hot-and-dry frequency and longest run. Conclusion: how often and how long require different summaries.
7. Does drawing choice change what we notice? Matched quiver panels: speed-proportional versus equal length. Conclusion: use the view that matches the question, preserving the measurements.

## Deliberate omissions from the main video

The treemaps, full correlation matrix, separate country trajectories, matched-change bars, horizon plots, regional gains, wind roses, overlap bars and full six-region ridgelines remain in the report. The video is a selected argument, not the report figure catalogue. Required implementations remain available in the submitted code/report. The live PCP selection remains in the recording.

## Design decision

Use an annotated editorial treatment: navy/cream fields, teal evidence accents, orange questions, persistent chapter and reasoning-stage navigation, enlarged panel crops, reading instructions next to evidence, and conclusion bands. Replace oversized thin numerals and centred report screenshots. Same-figure consecutive scenes keep a stable matrix or profile position while the interpretation changes. Scientific crop boundaries and sources are recorded; data colours, marks and GIF bytes are preserved.

User feedback authorises redesign and plot selection. Previously delegated routine design gates remain delegated. This is a full re-outline under the PPT Master Generate Default route, with Guizang's Swiss browser runtime retained. Alternatives considered: keep all methods (rejected for overload); use only headline numbers (rejected for weak evidence); selected annotated figures (chosen).
''',encoding='utf-8')
    for f in ['design_spec.md','spec_lock.md']:
        text=(OLD/f).read_text(encoding='utf-8').replace('24','14').replace('Internet and Weather','What the summary leaves out')
        text=text.replace('#002FA7',TEAL).replace('#FAFAF8',PAPER).replace('#0A0A0A',NAVY).replace('Segoe UI Light','Segoe UI')
        text=text.replace('keep all required methods','select six main analysis figures; required implementations remain in the report')
        text=text.replace('Swiss hierarchy, IKB accent, light and dark surfaces, large thin display numerals and varied registered compositions.','Annotated editorial hierarchy, navy and cream fields, teal evidence accents, orange questions, same-figure reading stages, and conclusion bands.')
        text=text.replace('one IKB accent','teal evidence accents and orange question markers').replace('large thin display numerals','semibold headings and annotated evidence')
        used=sorted({im for s in story for im in s['images']})
        if f=='design_spec.md':
            start=text.index('## VIII.');end=text.index('## X.')
            resource='## VIII. Image Resource List\n\n| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n'
            for im in used:
                with Image.open(P/'images'/im) as pic:iw,ih=pic.size
                resource+=f'| {im} | {iw}x{ih} | {iw/ih:.3f} | Report evidence | Scientific figure | Contain and preserve labels | no-crop | user | Existing | images/{im} | preserve | evidence |\n'
            outline='\n\n## IX. Content Outline\n\n'
            for s in story:
                outline+=f'#### Slide {s["number"]} - {s["title"]}\n\n- **Audience move**: {s["takeaway"]}\n- **Relationships**: contrast / evidence supports conclusion\n- **Composition**: annotated editorial evidence; chapter, question, large panel crops and conclusion\n- **Title**: {s["title"]}\n- **Core message**: {s["takeaway"]}\n- **Content**: {s["say"]}\n- **Images**: {", ".join(s["images"]) or "none"}\n'
                if s['number']==5:outline+='- **Hyperlinks**: http://127.0.0.1:8765/web/index.html\n'
                outline+='\n'
            text=text[:start]+resource+outline+text[end:]
        else:
            start=text.index('## page_rhythm');end=text.index('## forbidden')
            text=text[:start]+'## page_rhythm\n'+''.join(f'- P{s["number"]:02}: '+('breathing' if s['number'] in [1,7,13,14] else 'anchor')+'\n' for s in story)+'\n## images\n'+''.join(f'- {Path(im).stem}: images/{im} | source=user | crop=no-crop\n' for im in used)+'\n'+text[end:]
            text=text.replace('- annotation: 20','- annotation: 20\n- explanation: 24')
        (P/f).write_text(text,encoding='utf-8')
    (P/'page_plan.md').write_text('\n'.join(f'{s["number"]:02}. {s["title"]} | {s["speaker"]} | {s["duration"]}s | {s["takeaway"]}' for s in story),encoding='utf-8')
    (P/'analysis/asset_sources.json').write_text(json.dumps({'base_manifest':str(OLD/'analysis/asset_sources.json'),'rule':'Crops preserve source marks and labels; crop selections listed in build_video_v3.py. Original GIFs unchanged.'},indent=2),encoding='utf-8')
    return data

class Page(base.Page):
    def __init__(self,s):
        super().__init__(s);self.bg=NAVY if self.dark else PAPER;self.fg=PAPER if self.dark else NAVY
        self.elements[0]['color']=self.bg
    def rect(self,x,y,w,h,color,group='body'):
        # Coloured surfaces frame text/images; they are not independent content zones.
        if group in ['panel','conclusion','progress']:group='background'
        return super().rect(x,y,w,h,color,group)
    def txt(self,t,x,y,w,size=28,color=None,weight=400,group='body'):
        size=56 if size==64 else size
        return self.text(t,x,y,w,size,color or self.fg,base.FONT,weight,group)
    def frame(self,x,y,w,h,col=ORANGE,thick=3,group='annotation'):
        for a,b,c,d in [(x,y,w,thick),(x,y+h-thick,w,thick),(x,y,thick,h),(x+w-thick,y,thick,h)]:self.rect(a,b,c,d,col,group)
    def chrome(self,stage,question):
        chap=self.s['chapter'];self.rect(0,0,12,720,TEAL if chap=='Internet' else ORANGE,'background')
        self.txt(chap.upper(),40,23,205,16,TEAL if not self.dark else '#66D2CC',600,'chapter')
        self.txt(f'{self.s["number"]:02} / 14',1160,24,90,16,MUTED if not self.dark else '#A7BCC9',group='chapter')
        self.txt(self.s['title'],40,66,1190,44,weight=600,group='title')
        self.txt(question,42,124,1185,20,MUTED if not self.dark else '#B3C6D0',group='question')
        self.line(40,165,1190,'#B8C6CA' if not self.dark else '#3D5668','rule')
        labels=['QUESTION','READ THE PLOT','EVIDENCE','CONCLUSION']
        for i,t in enumerate(labels):
            self.rect(40+i*181,681,169,4,TEAL if i==stage else '#CFD8D7' if not self.dark else '#365163','progress')
            self.txt(t,40+i*181,692,169,14,self.fg if i==stage else MUTED if not self.dark else '#97ACB9',600 if i==stage else 400,'progress')
        self.txt(self.s['source'],800,686,430,14,MUTED if not self.dark else '#A7BCC9',group='source')
    def note(self,num,title,text,x,y,w=323):
        key=f'badge-{num}-{x}-{y}'
        self.rect(x,y,34,30,TEAL,key)
        self.txt(str(num),x+10,y+2,24,20,WHITE,600,key)
        self.txt(title,x+48,y-2,w-48,24,weight=600,group='note')
        self.txt(text,x+48,y+39,w-48,20,group='note')
    def verdict(self,text,y=604):
        self.rect(40,y,1190,54,TEAL if not self.dark else '#1F4856','conclusion')
        self.txt(text,58,y+12,1152,24,PAPER,600,'conclusion')

def compose(s):
    p=Page(s);n=s['number']
    if n==1:
        p.rect(755,0,525,720,TEAL,'background')
        p.txt('DAS732 / DATA VISUALIZATION',48,35,1050,16,'#8FD4D0',600,'identity')
        p.txt('What does\nthe summary\nleave out?',46,148,710,80,PAPER,600,'title')
        p.txt('Internet and Weather / an evidence-led story',49,492,654,28,'#B8CFD9',group='subtitle')
        for i,(a,b) in enumerate([('01','Country relationships'),('02','Uneven progress'),('03','Weather through time')]):
            y=168+i*140;p.txt(a,803,y,100,44,'#90E0DB',600,'route');p.txt(b,803,y+58,400,28,PAPER,600,'route')
        p.line(48,606,1184,'#7AB3B5','identity')
        p.txt('Internet first → Weather second',49,631,1150,24,PAPER,600,'identity')
        return p
    if n==14:
        p.rect(0,0,1280,15,TEAL,'background');p.txt('DAS732 / ASSIGNMENT 2',48,55,1150,20,'#8FD4D0',600,'identity')
        p.txt('Team Plot Twist',46,142,1180,64,weight=600,group='title')
        for y,name,ident,role in [(285,'Parikshith Aithal K V','BT2024249','Network / scalar fields'),(390,'Sindhoor Ganapathi Hegde','BT2024014','Temporal views / contours'),(495,'Varshith M Gowda','BT2024227','JavaScript profiles / quiver')]:
            p.txt(name,49,y,750,28,weight=600,group='identity');p.txt(ident,49,y+39,650,20,'#A4BBC7',group='identity');p.txt(role,825,y+10,390,24,'#A4BBC7',group='identity')
        p.txt('OWID / ITU country data • gridMET weather • sources and full methods in the report',49,650,1170,16,'#A4BBC7',group='source')
        return p
    questions={2:(1,'Start with one relationship. Then inspect the group.'),3:(2,'SAME MATRIX / now compare rows and missing links'),4:(1,'Expectation: higher adoption should mean more fixed broadband. Does every country fit?'),5:(2,'SAME PROFILES / test the expectation with a visible selection'),6:(2,'Read where the curves sit, then look at their spread.'),7:(3,'Finish Internet before starting the Weather case.'),8:(1,'NEW CASE / daily US weather, July–September 2023'),9:(2,'September 2023 / same field of locations, two different questions'),10:(1,'Follow equal-temperature boundaries as the dates advance.'),11:(2,'Same places and days / different summaries of hot-and-dry conditions'),12:(1,'Same field • same sampled locations • 22 August 2023'),13:(3,'The conclusion follows from the evidence already shown.')}
    p.chrome(*questions[n])
    if n==2:
        p.rect(40,192,294,366,WHITE,'panel');p.image('network_group.png',45,198,282,345,'overview')
        p.txt('Zoom into G7 →',46,565,294,24,TEAL,600,'annotation')
        p.rect(355,190,550,405,WHITE,'panel');m=p.image('group_matrix.png',361,196,538,393,'matrix')
        for col in [2,6]:p.frame(m['x']+m['w']*(.301+col*.0857),m['y']+m['h']*(.051+.1046),m['w']*.0857,m['h']*.1046,ORANGE,3,'matrix')
        p.note(1,'Teal cell','Cuba → Palestine\nA stored link',934,216,298)
        p.note(2,'White cell','Cuba →\nDominican Republic\nNo link',934,370,298)
        p.verdict('Links describe similar profiles. The diagonal is not a country pair.')
    elif n==3:
        p.rect(40,191,680,403,WHITE,'panel');m=p.image('group_matrix.png',46,196,668,393,'matrix')
        for row in [1,4]:p.frame(m['x']+m['w']*.301,m['y']+m['h']*(.051+row*.1046),m['w']*.6856,m['h']*.1046,ORANGE,2,'matrix')
        p.txt('18 of 28',762,201,468,64,'#74D9D2',600,'finding')
        p.txt('possible pairs are linked',765,299,450,28,group='finding')
        p.line(765,332,440,'#527182','finding')
        p.txt('Cuba / Palestine',765,356,440,24,weight=600,group='finding');p.txt('6 internal links each',765,395,440,28,group='finding')
        p.txt('Laos',765,465,440,24,weight=600,group='finding');p.txt('3 internal links',765,504,440,28,group='finding')
        p.verdict('Same group ≠ same relationships. The white gaps matter.')
    elif n in [4,5]:
        p.rect(40,190,875,438,WHITE,'panel');p.image('profiles_plot.png',46,196,863,426,'profiles')
        if n==4:
            p.note(1,'One line','One country across four axes',940,205,290)
            p.note(2,'Read crossings','Each axis has\nits own scale',940,345,290)
            p.note(3,'Apply the brush','≥70% online\n≤5 broadband / 100',940,485,290)
        else:
            p.txt('6 / 175',943,203,285,44,'#74D9D2',600,'finding')
            p.txt('High adoption +\nlow broadband',943,285,285,28,weight=600,group='finding')
            p.txt('Cuba\nKuwait\nSouth Africa\nBhutan\nKyrgyzstan\nLibya',943,383,285,24,group='finding')
            p.txt('Show the live selection →',42,642,1170,16,'#74D9D2',600,'demo')['href']='http://127.0.0.1:8765/web/index.html'
    elif n==6:
        for x,file,label in [(40,'ridges_africa.png','Africa / same 45 countries'),(465,'ridges_europe.png','Europe / same 37 countries')]:
            p.rect(x,194,405,374,WHITE,'panel');p.image(file,x+5,199,395,364,'ridges');p.txt(label,x+4,574,404,20,TEAL,600,'annotation')
        p.note(1,'Rightward shift','Adoption rises over time.',900,211,330)
        p.note(2,'Remaining spread','Countries still differ in 2020.',900,362,330)
        p.verdict('Progress is clear. Large gaps remain within and between regions.')
    elif n==7:
        for i,(title,evidence,conclusion) in enumerate([('Relationships','18 / 28 pairs linked in G7','A group label hides\nmissing links.'),('Infrastructure','6 / 175 fit the brush','High adoption has\ndifferent profiles.'),('Progress','Two regions, five dates','A rising median can\nleave wide gaps.')]):
            x=40+i*406;p.rect(x,208,378,338,'#1A3B4B','panel');p.txt(f'0{i+1}',x+20,228,330,44,'#74D9D2',600,'finding');p.txt(title,x+20,302,338,28,weight=600,group='finding');p.txt(evidence,x+20,362,338,20,'#A8CAD4',group='finding');p.txt(conclusion,x+20,419,338,24,group='finding')
        p.verdict('One adoption number cannot describe the whole connection profile.')
    elif n==8:
        for x,file,label in [(40,'scivis_global.gif','FIXED SCALE'),(650,'scivis_local.gif','DAILY SCALE')]:
            p.txt(label,x,194,580,24,TEAL,600,'labels');p.rect(x,235,580,342,WHITE,'panel');p.image(file,x+5,240,570,332,'animated-evidence')
        p.txt('Colour keeps its temperature meaning',42,588,585,20,weight=600,group='annotation')
        p.txt('Colour meaning can change each day',652,588,580,20,weight=600,group='annotation')
        p.txt('WATCH THE LEGENDS  /  same fields, different normalisation',42,637,1180,20,TEAL,600,'conclusion')
    elif n==9:
        p.txt('01  HOW MUCH?',42,190,580,24,TEAL,600,'labels')
        p.txt('02  HOW CONCENTRATED?',652,190,578,24,TEAL,600,'labels')
        p.txt('Legend: share of monthly rain in the wettest five days (%)',652,222,578,14,MUTED,group='labels')
        p.rect(40,249,580,302,WHITE,'panel');p.image('rain_september_total.png',46,255,568,290,'rain-total')
        p.rect(650,249,580,302,WHITE,'panel');p.image('rain_september_burst.png',656,255,568,290,'rain-timing')
        p.txt('77.6%',42,565,304,56,TEAL,600,'finding')
        p.txt('of eligible area: ≥ half the monthly rain\nin five consecutive days',372,566,850,24,group='finding')
        p.txt('Eligible cells: monthly rain ≥10 mm. A total alone cannot show the timing.',374,636,850,16,MUTED,group='conclusion')
    elif n==10:
        p.rect(40,191,850,426,WHITE,'panel');p.image('scivis_contour.gif',46,196,838,416,'animated-evidence')
        p.note(1,'Trace a line','Same temperature along a boundary',920,213,310)
        p.note(2,'Follow time','Watch boundaries\nmove with dates',920,360,310)
        p.txt('Smaller intervals add detail—and more lines to read.',42,637,1180,24,group='conclusion')
    elif n==11:
        p.rect(40,194,1190,354,WHITE,'panel');p.image('persistence.png',46,200,1178,342,'persistence')
        p.txt('HOW OFTEN',42,559,540,24,TEAL,600,'annotation');p.txt('HOW LONG WITHOUT A BREAK',655,559,575,24,TEAL,600,'annotation')
        p.txt('Frequency counts qualifying days.',42,599,570,20,group='finding');p.txt('Longest local run: 67 days in this window.',655,599,575,20,group='finding')
        p.txt('Hot: Tmax ≥35°C  /  Dry: rain <1 mm per day  /  Different legends and units',42,641,1180,16,MUTED,group='source')
    elif n==12:
        for x,file,label in [(40,'wind_short.png','LENGTH = SPEED'),(580,'wind_equal.png','EQUAL LENGTHS')]:
            p.txt(label,x,191,520,24,TEAL,600,'labels');p.rect(x,231,518,350,WHITE,'panel');p.image(file,x+4,235,510,342,'wind')
        p.rect(1118,231,112,350,WHITE,'panel');p.image('wind_scale.png',1123,236,102,340,'key')
        p.txt('Speed differences stand out',42,594,520,20,weight=600,group='annotation');p.txt('Directions become easier to follow',582,594,520,20,weight=600,group='annotation')
        p.txt('Arrows show flow TO. Colour retains speed in both views.',42,639,1180,24,TEAL,600,'conclusion')
    elif n==13:
        for x,label,title,detail in [(40,'INTERNET','Differences inside the summary','Same group: unequal links.\nHigh adoption: different profiles.\nProgress: remaining gaps.'),(650,'WEATHER','Time inside the summary','Monthly rain: short bursts.\nEvent counts: different run lengths.\nDrawing choices: different emphasis.')]:
            p.rect(x,201,580,339,'#1A3B4B','panel');p.txt(label,x+22,223,536,20,'#74D9D2',600,'labels');p.txt(title,x+22,269,536,32,weight=600,group='finding');p.txt(detail,x+22,363,536,24,group='finding')
        p.verdict('Pair the summary with the detail needed to answer the question.')
    return p

if __name__=='__main__':
    data=prepare()
    base.P=P;base.TITLE=base.FONT;base.INK=NAVY;base.PAPER=PAPER;base.BLUE=TEAL;base.GRAY=MUTED
    base.compose=compose
    import inspect
    writer=inspect.getsource(base.svg)
    writer=re.sub(r'        combine=.*\n',"        combine=group.startswith('badge-') or group=='matrix'\n",writer)
    exec(writer,base.__dict__)
    base.build()
    # Correct page-role declarations for the new roster (the shared writer's old roster was 24).
    for f in (P/'svg_output').glob('*.svg'):
        number=int(f.name[:2]);role='cover' if number==1 else 'ending' if number==14 else 'content'
        text=re.sub(r'data-pptx-page-role="[^"]+"',f'data-pptx-page-role="{role}"',f.read_text(encoding='utf-8'))
        (f).write_text(text,encoding='utf-8')
    print(json.dumps({'slides':len(data['slides']),'words':data['words'],'raw_seconds':data['raw_seconds'],'project':str(P)},indent=2))
