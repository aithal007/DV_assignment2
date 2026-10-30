"""Publish the reviewed Internet-first deck and matching recording materials."""
from pathlib import Path
import json, shutil, zipfile, html, re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'presentation_source/internet_weather_ppt169_20261024'
OUT = ROOT / 'output/video_presentation'
data = json.loads((PROJECT / 'storyboard.json').read_text(encoding='utf-8'))
slides = data['slides']
reviewed = Path(json.loads((PROJECT / 'validation/final_path.json').read_text())['finalPath'])
OUT.mkdir(parents=True, exist_ok=True)
shutil.copy2(reviewed, OUT / 'DAS732_A2_Video_Presentation_Final.pptx')
for name in ['index.html', 'motion.min.js', 'storyboard.json']:
    shutil.copy2(PROJECT / name, OUT / name)
for name in ['images', 'third_party']:
    shutil.copytree(PROJECT / name, OUT / name, dirs_exist_ok=True)
(OUT / 'slides').mkdir(exist_ok=True)
for s in slides:
    shutil.copy2(PROJECT / f"validation/final_powerpoint/Slide{s['number']}.PNG", OUT / f"slides/slide-{s['number']:02}.png")

def stamp(t):
    return f'{int(t)//60}:{int(t)%60:02}'

blocks = [(1,4,'Parikshith','Internet'),(5,8,'Varshith','Internet'),(9,12,'Sindhoor','Internet'),(13,16,'Parikshith','Weather'),(17,19,'Sindhoor','Weather'),(20,24,'Varshith','Weather')]
intro = '''# Beyond averages and snapshots: recording guide

Use the reviewed 24-slide deck. Record the complete Internet section before starting Weather. Read the spoken text in simple English; the screen actions are directions, not narration.

Raw timeline: **6:30**. The previous **1.35x** editing plan gives about **4:49**. Rehearse for clarity before choosing the final playback speed. There are 857 spoken words. Timings include pointing, GIF loops, browser actions and the six-second closing hold.

## Record these six blocks in this order

| Chapter | Speaker | Slides | Raw time |
|---|---|---|---|
'''
for a,b,speaker,chapter in blocks:
    intro += f'| {chapter} | {speaker} | {a}–{b} | {stamp(slides[a-1]["start"])}–{stamp(slides[b-1]["end"])} |\n'
setup = '''
## Before recording

1. Open `DAS732_A2_Video_Presentation_Final.pptx` in desktop PowerPoint and start Slide Show. Record at 1920 × 1080 if possible. GIFs show a still frame in editing view; they animate in Slide Show.
2. Slide 14 contains the global/local GIFs and slide 17 contains the contour GIF. All three are embedded: no separate animation window is needed. Each loop takes 6.4 seconds. Let at least two loops play while speaking on each animation scene.
3. For the two real Internet interactions on slides 5 and 6, run `python run_visualizations.py` from `ass2`. Keep the server running. The slide links open the actual parallel coordinates and treemap. Return to the slideshow after each demonstration.
4. Stage parallel coordinates at `http://127.0.0.1:8765/web/index.html?year=2020&bundle=50&matched=1&fixed=1`. Use **Inspect high adoption / low broadband**. Show the six selected profiles, demonstrate brushing, and click an axis heading to reorder it. Clicking a heading moves that axis one position right; it is not a drag interaction. Reapply the preset if reordering clears the brush.
5. In `http://127.0.0.1:8765/web/treemap.html`, zoom into Asia, return to the root, switch to adoption bands and hover a country. Rehearse these actions before recording.
6. Alternatively open `index.html` for the browser deck; keep its `images`, `motion.min.js` and `third_party` files together. Its GIFs animate directly. Use arrow keys for navigation. The PDF guide is for reading and does not animate.

## Per-slide narration and actions
'''
md = intro + setup
for s in slides:
    md += f'\n### {s["number"]:02}. {s["title"]}\n\n**{s["chapter"]} · {s["speaker"]} · {stamp(s["start"])}–{stamp(s["end"])} ({s["duration"]} seconds)**\n\n**Say:** {s["say"] or "[Silent closing hold.]"}\n\n**Do:** {s["actions"]}\n\n**On screen:** {s["screen"]}\n\n**Source:** {s["source"]}\n'
(OUT / 'RECORDING_SCRIPT.md').write_text(md, encoding='utf-8')
narration = 'BEYOND AVERAGES AND SNAPSHOTS\nInternet first, then Weather\n\n'
for a,b,speaker,chapter in blocks:
    narration += f'{chapter.upper()} — {speaker.upper()} — slides {a}–{b}\n\n'
    narration += '\n\n'.join(s['say'] for s in slides[a-1:b] if s['say']) + '\n\n'
(OUT / 'CONTINUOUS_NARRATION.txt').write_text(narration, encoding='utf-8')
readme = '''# Updated recording package

24 slides: **Internet 1–12, then Weather 13–24**. Main question: what do averages and snapshots hide about inequality, relationships and change over time?

- `DAS732_A2_Video_Presentation_Final.pptx`: editable PowerPoint, speaker notes, two editable charts and three embedded eight-frame GIFs.
- `DAS732_A2_Recording_Script.pdf` / `RECORDING_SCRIPT.md`: matching narration, timings and screen actions.
- `CONTINUOUS_NARRATION.txt`: spoken text in recording order.
- `index.html`: browser presentation; retain the accompanying files and folders.
- `slides/`: static PowerPoint previews; GIF animation requires the PPTX Slide Show or browser deck.

GIFs play inside desktop PowerPoint **Slide Show** on slides 14 and 17. The Internet demonstrations on slides 5 and 6 are actual interactive browser pages. Start the local server with `python run_visualizations.py` from `ass2`; rehearse the actions in the recording guide.

Raw plan 6:30; approximately 4:49 at the existing 1.35x editing speed. Record six blocks in order: Internet Parikshith → Varshith → Sindhoor; Weather Parikshith → Sindhoor → Varshith. Each member has 2:10 including the closing hold in Varshith's block. Human voices and live browser demonstrations still need recording. No final video has been produced.

Design uses [PPT Master](https://github.com/hugohe3/ppt-master) for SVG-to-native-PowerPoint generation and [Guizang PPT Skill](https://github.com/op7418/guizang-ppt-skill) for the Swiss browser template. Its license is retained under `third_party`. Scientific graphics come from the current report; the report itself was not changed.

Editable source: `ass2/presentation_source/internet_weather_ppt169_20261024`. Generation scripts: `prepare_video_v2.py`, `build_video_v2.py`, `sync_video_chart_caches.py`, `finalize_video_v2.mjs`, `render_video_v2.ps1`, `render_video_v2_browser.mjs`, `publish_video_v2.py` under `ass2/scripts`. Use the current v2 workflow; the older 17-slide builders are superseded. Native PPT Master export and quality checks must run between source generation and cache synchronization. Validation receipts are retained in the source project's `validation` folder.
'''
(OUT / 'README.md').write_text(readme, encoding='utf-8')

# A compact guide: one overview page, then two slides per page.
pdf = ROOT / 'output/pdf/DAS732_A2_Recording_Script.pdf'
pdf.parent.mkdir(exist_ok=True)
c = canvas.Canvas(str(pdf), pagesize=A4)
c.setTitle('Beyond averages and snapshots — recording guide')
W,H = A4
style = ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=14,textColor='#15233B')
heading = ParagraphStyle('heading',parent=style,fontName='Helvetica-Bold',fontSize=14,leading=18)
def para(text, x, top, width, sty=style):
    p = Paragraph(text,sty); _, height = p.wrap(width,H)
    p.drawOn(c,x,top-height)
    return top-height
def footer(n):
    c.setFillColorRGB(.35,.4,.47); c.setFont('Helvetica',8)
    c.drawString(36,24,'DAS732 A2 | Recording guide | Internet, then Weather')
    c.drawRightString(W-36,24,str(n))
def banner(title,subtitle):
    c.setFillColorRGB(0,.184,.655);c.rect(0,H-82,W,82,fill=1,stroke=0)
    c.setFillColorRGB(1,1,1);c.setFont('Helvetica-Bold',20);c.drawString(36,H-34,title)
    c.setFont('Helvetica',10);c.drawString(36,H-56,subtitle)
banner('Record Internet first. Then Weather.','24 slides | 857 spoken words | 6:30 raw | about 4:49 at 1.35x')
y=H-106
y=para('Recording order',36,y,W-72,heading)-10
for a,b,speaker,chapter in blocks:
    y=para(f'<b>{stamp(slides[a-1]["start"])}–{stamp(slides[b-1]["end"])}</b> &nbsp; {chapter} / {speaker} / slides {a}–{b}',36,y,W-72)-10
y-=10
for text in ['<b>Embedded GIFs:</b> slide 14 (global and local) and slide 17 (contours). Use desktop PowerPoint Slide Show; editing view shows a still image. Allow two 6.4-second loops while speaking.', '<b>Live Internet demos:</b> slides 5 and 6. Start <font face="Courier">python run_visualizations.py</font> from ass2. Show the real parallel coordinates and treemap, then return to the slides.', '<b>Parallel coordinates:</b> use the high-adoption / low-broadband preset; show brushing, then click an axis heading to reorder. Reapply the preset if needed. <b>Treemap:</b> zoom into Asia, return, switch to adoption bands and hover a country.', '<b>Before recording:</b> rehearse the six blocks, check microphone levels, hide notifications and record in 16:9. Keep the final six seconds as a silent closing hold.', '<b>Read:</b> only the text marked Say. Do and Source are recording instructions. The matching Markdown guide contains the full setup URLs.']:
    y=para(text,36,y,W-72)-15
assert y>45,y
footer(1);c.showPage()
for k in range(0,len(slides),2):
    banner('Narration and screen actions',f'Slides {k+1}–{min(k+2,len(slides))} | Times refer to the raw recording')
    for j,s in enumerate(slides[k:k+2]):
        top=H-104-j*352
        top=para(f'{s["number"]:02}. {html.escape(s["title"])}',36,top,W-72,heading)-5
        top=para(f'{s["chapter"]} / {s["speaker"]} / {stamp(s["start"])}–{stamp(s["end"])}',36,top,W-72)-10
        image=OUT/f'slides/slide-{s["number"]:02}.png'
        iw,ih=192,108
        c.drawImage(str(image),36,top-ih,width=iw,height=ih)
        right=para('<b>Do:</b> '+html.escape(s['actions']),242,top,W-278)
        right=para('<b>Source:</b> '+html.escape(s['source']),242,right-9,W-278)
        assert right>top-120,(s['number'],right,top)
        bottom=para('<b>Say:</b> '+html.escape(s['say'] or '[Silent closing hold.]'),36,top-ih-12,W-72)
        assert bottom>top-230,(s['number'],bottom,top)
    footer(k//2+2);c.showPage()
c.save()
shutil.copy2(pdf,OUT/pdf.name)

# Keep the responsibility allocation; replace only the superseded video sequence.
plan=ROOT/'PRESENTATION_PLAN.md'
text=plan.read_text(encoding='utf-8').replace('20-page, 30-figure report','25-page, 30-figure report')
text=re.sub(r'## Continuous video explanation\n.*?(?=## Contribution record)', '', text, flags=re.S)
marker='\n## Current recording sequence (24 slides)\n'
if marker in text:text=text.split(marker)[0]
text+=marker+'\nThe complete Internet section is recorded first (slides 1–12, 0:00–3:15). Weather follows (slides 13–24, 3:15–6:30). The six recording blocks are Internet: Parikshith → Varshith → Sindhoor; Weather: Parikshith → Sindhoor → Varshith. Each member has 2:10, including the six-second closing hold for Varshith. The report figure allocation above is unchanged.\n\nThe authoritative script and 24-scene timing are in [the recording guide](output/video_presentation/RECORDING_SCRIPT.md). GIFs are embedded in slides 14 and 17; slides 5 and 6 open the real Internet interactions.\n'
plan.write_text(text,encoding='utf-8')
readme_path=ROOT/'README.md'
text=readme_path.read_text(encoding='utf-8')
text=re.sub(r'The 17-scene recording plan.*?The complete 175-country view remains available\.', 'The updated 24-scene recording plan presents all Internet evidence first (slides 1–12), then Weather (13–24). It retains 6:30 raw, about 4:49 at 1.35x. Three GIFs are embedded on slides 14 and 17. Slides 5 and 6 link to the real JavaScript interactions. See [the updated recording package](output/video_presentation/README.md). Human voices and live browser footage still need recording.',text,flags=re.S)
text=text.replace('20-page','25-page')
text=re.sub(r'To refresh animation assets,.*?No completed video is included yet\.', 'The presentation now uses the 24-slide v2 workflow. See [the recording package README](output/video_presentation/README.md) for source files and generation scripts. The older prepare_video_materials, update_animation_script, build_recording_script_pdf and finalize_video_materials scripts belong to the superseded 17-slide workflow and should not be run on this delivery. No completed video is included yet.', text, flags=re.S)
readme_path.write_text(text,encoding='utf-8')

# Package only the current deliverables, avoiding obsolete reviewed decks.
package=ROOT/'output/DAS732_A2_Video_Slides_and_Script.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for name in ['DAS732_A2_Video_Presentation_Final.pptx','DAS732_A2_Recording_Script.pdf','RECORDING_SCRIPT.md','CONTINUOUS_NARRATION.txt','README.md','storyboard.json','index.html','motion.min.js']:
        z.write(OUT/name,name)
    for dirname in ['slides','images','third_party']:
        for p in sorted((OUT/dirname).rglob('*')):
            if p.is_file():z.write(p,p.relative_to(OUT))
print(json.dumps({'slides':len(slides),'words':data['words'],'raw_seconds':data['raw_seconds'],'pdf':str(pdf),'package':str(package)},indent=2))
