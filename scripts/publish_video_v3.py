"""Deliver the reviewed, selected-figure story and its synchronized guide."""
from pathlib import Path
import json,shutil,zipfile,re,html,hashlib,io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'presentation_source/focused_story_ppt169_20261024'
OUT=ROOT/'output/video_presentation'
d=json.loads((P/'storyboard.json').read_text(encoding='utf-8'));slides=d['slides']
assert len(slides)==14 and d['words']==768 and sum(s['duration'] for s in slides)==390
final=Path(json.loads((P/'validation/final_path.json').read_text())['finalPath'])
shutil.copy2(final,OUT/'DAS732_A2_Video_Presentation_Final.pptx')
for f in ['index.html','motion.min.js','storyboard.json']:
    shutil.copy2(P/f,OUT/f)
shutil.copy2(P/'SELECTION_AND_STORY.md',OUT/'SELECTION_AND_STORY.md')
used=sorted({im for s in slides for im in s['images']})
for im in used:shutil.copy2(P/'images'/im,OUT/'images'/im)
shutil.copytree(P/'third_party',OUT/'third_party',dirs_exist_ok=True)
for s in slides:shutil.copy2(P/f'validation/final_powerpoint/Slide{s["number"]}.PNG',OUT/f'slides/slide-{s["number"]:02}.png')
# Remove only superseded numbered preview files, already preserved in the archive.
for f in (OUT/'slides').glob('slide-*.png'):
    if re.fullmatch(r'slide-\d\d\.png',f.name) and int(f.stem[-2:])>len(slides):
        assert f.resolve().is_relative_to(ROOT.resolve())
        f.unlink()

def time(t):return f'{int(t)//60}:{int(t)%60:02}'
blocks=[(1,3,'Parikshith','Internet'),(4,5,'Varshith','Internet'),(6,7,'Sindhoor','Internet'),(8,9,'Parikshith','Weather'),(10,11,'Sindhoor','Weather'),(12,14,'Varshith','Weather')]
setup='''# What does the summary leave out? — recording guide

The current deck has **14 slides**, using **six main analysis figures** rather than a tour of the report. The scale and contour GIFs support the Weather explanations. Internet is complete before Weather begins.

The spoken script has **768 words**. Plan **6:30 raw**, including pointing, the live brush and GIF loops. The existing 1.35× editing plan gives about **4:49**. Rehearse with the actions included: the aim is a clear explanation, not continuous fast speech. Each member has 2:10, including the six-second closing hold in Varshith's second block.

## Recording order

| Chapter | Speaker | Slides | Raw recording |
|---|---|---|---|
'''
for a,b,speaker,chapter in blocks:setup+=f'| {chapter} | {speaker} | {a}–{b} | {time(slides[a-1]["start"])}–{time(slides[b-1]["end"])} |\n'
setup+='''
## Before recording

1. Open `DAS732_A2_Video_Presentation_Final.pptx` in desktop PowerPoint and use **Slide Show**. Record a 16:9 frame. Read only **Say**; **Do** and **Source** are instructions.
2. Slide **8** contains the fixed/local temperature GIFs. Slide **10** contains the contour GIF. All three play inside the slides. Editing view and static previews show still frames. Allow at least two 6.4-second loops while speaking.
3. For the real parallel-coordinate selection on slides **4–5**, run `python run_visualizations.py` from `ass2`. Stage `http://127.0.0.1:8765/web/index.html?year=2020&bundle=50&matched=1&fixed=1`. Use **Inspect high adoption / low broadband**. Confirm the six selected countries, move one brush slightly and restore the preset. The link on slide 5 opens the browser; return to the deck after the demonstration.
4. Show the brush as a test of the stated expectation. Do not spend recording time touring unrelated controls. Axis reordering and treemap remain available in the implementation and report.
5. Keep the plot visible long enough to follow the row, line, curve or legend being discussed. The same NodeTrix figure and same parallel-coordinate figure each receive two slides: reading first, interpretation second.
6. The offline browser alternative is `index.html`; retain `images`, `motion.min.js` and `third_party` beside it. Its GIFs animate too. The PDF guide is static.

## Per-slide recording
'''
script=setup
for s in slides:
    script+=f'\n### {s["number"]:02}. {s["title"]}\n\n**{s["chapter"]} / {s["speaker"]} / {time(s["start"])}–{time(s["end"])} ({s["duration"]} seconds)**\n\n**Say:** {s["say"] or "[Silent closing hold.]"}\n\n**Do:** {s["actions"]}\n\n**Conclusion:** {s["takeaway"]}\n\n**Source:** {s["source"]}\n'
(OUT/'RECORDING_SCRIPT.md').write_text(script,encoding='utf-8')
continuous='WHAT DOES THE SUMMARY LEAVE OUT?\nInternet first, then Weather\n\n'
for a,b,speaker,chapter in blocks:
    continuous+=f'{chapter.upper()} / {speaker.upper()} / slides {a}–{b}\n\n'+'\n\n'.join(s['say'] for s in slides[a-1:b] if s['say'])+'\n\n'
(OUT/'CONTINUOUS_NARRATION.txt').write_text(continuous,encoding='utf-8')
readme='''# Focused 14-slide recording package

This replaces the 24-slide version. **Internet: slides 1–7. Weather: slides 8–14.** The main question is what averages and snapshots leave out.

Six main analysis figures: NodeTrix, highlighted parallel coordinates, selected ridgelines, September rainfall timing, hot-and-dry persistence, and matched quiver panels. Fixed/local-scale and contour GIFs explain how to read Weather fields. Other comparisons remain in the report. See `SELECTION_AND_STORY.md` for the selection and argument.

- `DAS732_A2_Video_Presentation_Final.pptx`: editable slide text and layout, 14 speaker notes, three original embedded GIFs.
- `DAS732_A2_Recording_Script.pdf` / `RECORDING_SCRIPT.md`: matching narration, evidence interpretation and recording actions.
- `CONTINUOUS_NARRATION.txt`: spoken text in recording order.
- `index.html`: offline browser presentation with animated GIFs; retain its accompanying files.
- `slides/`: static PowerPoint previews.

Use desktop PowerPoint **Slide Show** for GIF playback on slides **8 and 10**. For the live brush on slides 4–5, start the local server with `python run_visualizations.py` from `ass2`. The recording guide gives the staging URL and exact actions.

768 spoken words; 6:30 raw including actions, approximately 4:49 at 1.35×. Record Internet: Parikshith → Varshith → Sindhoor, then Weather: Parikshith → Sindhoor → Varshith. Each person has 2:10 including the silent credits for Varshith. Human voices and live interaction still need recording; this package does not contain a finished video.

The design uses [PPT Master](https://github.com/hugohe3/ppt-master) for editable native PowerPoint export and [Guizang PPT Skill](https://github.com/op7418/guizang-ppt-skill) for the Swiss browser runtime. Its license is retained under `third_party`. Scientific marks and GIF frames come from the current report. The report is unchanged.

Source: `ass2/presentation_source/focused_story_ppt169_20261024`. Current authoring: `scripts/build_video_v3.py`; native export: PPT Master's `svg_to_pptx.py`; final checks: `scripts/finalize_video_v3.mjs`; browser QA: `scripts/render_video_v3_browser.mjs`; PowerPoint preview: `scripts/render_video_v2.ps1`; publication: `scripts/publish_video_v3.py`. Run source generation, SVG quality checks, native export, final checks, PowerPoint rendering and publication in that order. The older v2 and 17-slide workflows are superseded and must not overwrite this delivery.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')

pdf=ROOT/'output/pdf/DAS732_A2_Recording_Script.pdf'
c=canvas.Canvas(str(pdf),pagesize=A4);W,H=A4
c.setTitle('What does the summary leave out? — recording guide')
body=ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=14,textColor='#102638')
head=ParagraphStyle('head',parent=body,fontName='Helvetica-Bold',fontSize=13,leading=17)
def para(t,x,y,w,style=body):
    p=Paragraph(t,style);_,h=p.wrap(w,H);p.drawOn(c,x,y-h);return y-h
def banner(title,subtitle):
    c.setFillColorRGB(.063,.149,.22);c.rect(0,H-80,W,80,fill=1,stroke=0)
    c.setFillColorRGB(.96,.95,.92);c.setFont('Helvetica-Bold',19);c.drawString(36,H-33,title)
    c.setFont('Helvetica',10);c.drawString(36,H-55,subtitle)
def footer(n):
    c.setFillColorRGB(.32,.41,.47);c.setFont('Helvetica',8)
    c.drawString(36,24,'DAS732 A2 / Focused recording story / Internet, then Weather');c.drawRightString(W-36,24,str(n))
banner('Explain fewer figures. Follow the evidence.','14 slides / 768 words / 6:30 raw / about 4:49 at 1.35x')
y=H-108;y=para('Record these six blocks in order',36,y,W-72,head)-12
for a,b,speaker,chapter in blocks:y=para(f'<b>{time(slides[a-1]["start"])}–{time(slides[b-1]["end"])}</b> &nbsp; {chapter} / {speaker} / slides {a}–{b}',36,y,W-72)-10
y-=10
for t in [
    '<b>The story:</b> ask a question, show how to read the plot, point to the evidence, then state what follows. The same figure stays visible across two scenes where explanation needs more time.',
    '<b>GIFs:</b> slide 8 has fixed/local scales; slide 10 has contours. Play them inside desktop PowerPoint Slide Show. Allow two 6.4-second loops; no external animation window is needed.',
    '<b>Live selection:</b> slides 4–5. Start <font face="Courier">python run_visualizations.py</font> from ass2. Apply the high-adoption / low-broadband preset, show six selected countries, change one brush and restore it. The Markdown guide contains the full staging URL.',
    '<b>Delivery:</b> use the pauses to point at cells, axis crossings and legends. Read only Say. The planned 6:30 includes actions; rehearse before editing. Hold the final credits for six seconds.',
    '<b>Selection:</b> the main video uses six analysis figures. Treemaps, the full correlation matrix, horizon plots, additional regional comparisons, wind roses and overlap bars remain in the report.']:
    y=para(t,36,y,W-72)-15
assert y>45,y
footer(1);c.showPage()
for k in range(0,len(slides),2):
    banner('Narration and evidence',f'Slides {k+1}–{k+2} / times refer to the raw recording')
    for j,s in enumerate(slides[k:k+2]):
        top=H-102-j*352
        top=para(f'{s["number"]:02}. {html.escape(s["title"])}',36,top,W-72,head)-5
        top=para(f'{s["chapter"]} / {s["speaker"]} / {time(s["start"])}–{time(s["end"])}',36,top,W-72)-9
        c.drawImage(str(OUT/f'slides/slide-{s["number"]:02}.png'),36,top-108,width=192,height=108)
        bottom=para('<b>Do:</b> '+html.escape(s['actions']),242,top,W-278)
        bottom=para('<b>Source:</b> '+html.escape(s['source']),242,bottom-8,W-278)
        assert bottom>top-140,(s['number'],bottom,top)
        y=para('<b>Say:</b> '+html.escape(s['say'] or '[Silent closing hold.]'),36,min(top-120,bottom-10),W-72)
        assert y>top-245,(s['number'],y,top)
    footer(k//2+2);c.showPage()
c.save();shutil.copy2(pdf,OUT/pdf.name)

# Update only presentation metadata; preserve the responsibility allocation and report.
plan=ROOT/'PRESENTATION_PLAN.md';t=plan.read_text(encoding='utf-8')
t=re.sub(r'\n## Current recording sequence \(24 slides\).*','',t,flags=re.S)
t=re.sub(r'\n## Current focused recording sequence.*','',t,flags=re.S)
t+='\n## Current focused recording sequence\n\n14 slides, six main analysis figures. Internet finishes on slide 7 at 3:15; Weather follows on slides 8–14. Internet speaker blocks: Parikshith (1–3), Varshith (4–5), Sindhoor (6–7). Weather blocks: Parikshith (8–9), Sindhoor (10–11), Varshith (12–14). Each block lasts 65 seconds, including the closing hold in the last block.\n\n768 spoken words leave room to point, read the plot and show the brush. The authoritative [recording guide](output/video_presentation/RECORDING_SCRIPT.md) includes the narration and actions. GIFs play on slides 8 and 10. Full implementations and figure ownership in the report remain unchanged.\n'
plan.write_text(t,encoding='utf-8')
readme_path=ROOT/'README.md';t=readme_path.read_text(encoding='utf-8')
t=re.sub(r'The updated (?:24|14)-scene recording plan.*?Human voices and live browser footage still need recording\.', 'The updated 14-slide video uses six main analysis figures, with explicit reading steps and conclusions. Internet finishes on slide 7; Weather follows on slides 8–14. The script has 768 words with planned pointing and demonstration time. GIFs are embedded on slides 8 and 10; slide 5 links to the real parallel-coordinate brush. See [the focused recording package](output/video_presentation/README.md). Human voices and the live demonstration still need recording.',t,flags=re.S)
t=t.replace('24-slide v2 workflow','14-slide v3 workflow')
readme_path.write_text(t,encoding='utf-8')

package=ROOT/'output/DAS732_A2_Video_Slides_and_Script.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for name in ['DAS732_A2_Video_Presentation_Final.pptx','DAS732_A2_Recording_Script.pdf','RECORDING_SCRIPT.md','CONTINUOUS_NARRATION.txt','SELECTION_AND_STORY.md','README.md','storyboard.json','index.html','motion.min.js']:z.write(OUT/name,name)
    for im in used:z.write(OUT/'images'/im,'images/'+im)
    for folder in ['slides','third_party']:
        for f in sorted((OUT/folder).rglob('*')):
            if f.is_file():z.write(f,f.relative_to(OUT))

with zipfile.ZipFile(OUT/'DAS732_A2_Video_Presentation_Final.pptx') as z:
    gifs=[n for n in z.namelist() if n.endswith('.gif')]
    assert len(gifs)==3
    originals={hashlib.sha256((ROOT/f'images/scivis/scivis_{kind}.gif').read_bytes()).hexdigest() for kind in ['global','local','contour']}
    assert all(Image.open(io.BytesIO(z.read(n))).n_frames==8 and hashlib.sha256(z.read(n)).hexdigest() in originals for n in gifs)
print(json.dumps({'slides':14,'words':d['words'],'GIFs':3,'package_MB':round(package.stat().st_size/1e6,1),'pdf':str(pdf)},indent=2))
