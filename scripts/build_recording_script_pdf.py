"""Create a printable recording booklet from the authoritative storyboard."""
from pathlib import Path
import json,html,re,shutil,zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import pymupdf as fitz
from PIL import Image,ImageOps,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'output/video_presentation'
OUT=ROOT/'output/pdf/DAS732_A2_Recording_Script.pdf'
TMP=ROOT/'tmp/pdfs/recording_script'
TMP.mkdir(parents=True,exist_ok=True);OUT.parent.mkdir(parents=True,exist_ok=True)
story=json.loads((SOURCE/'storyboard.json').read_text(encoding='utf-8'))
slides=story['slides']
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
W,H=A4;LEFT=42;WIDTH=W-84;INK='#142D43';TEAL='#087E8B';MUTED='#536574'
c=canvas.Canvas(str(OUT),pagesize=A4)
c.setTitle('DAS732 A2 - Continuous Recording Script and Screen Guide')
c.setAuthor('Team Plot Twist')

def clean(s):
    return s.translate(str.maketrans({'–':'-','—':'-','‑':'-','×':'x','’':"'",'‘':"'",'“':'"','”':'"'}))
def para(s,x,y,w=WIDTH,size=11,lead=15,bold=False,color=INK):
    style=ParagraphStyle('p',fontName='Arial-Bold' if bold else 'Arial',fontSize=size,leading=lead,
                         textColor=HexColor(color),spaceAfter=0)
    p=Paragraph(html.escape(clean(s)).replace('\n','<br/>'),style)
    _,height=p.wrap(w,H)
    if y-height<43:raise ValueError(f'Page overflow at page {c.getPageNumber()}: {s[:65]}')
    p.drawOn(c,x,y-height)
    return y-height
def label(s,y):return para(s.upper(),LEFT,y,size=9,lead=12,bold=True,color=TEAL)-5
def header(section):
    c.setFillColor(HexColor(TEAL));c.rect(0,H-7,W,7,fill=1,stroke=0)
    c.setFont('Arial',8);c.setFillColor(HexColor(MUTED))
    c.drawString(LEFT,H-30,'DAS732 Assignment 2  /  Team Plot Twist')
    c.drawRightString(W-LEFT,H-30,section)
def footer():
    c.setStrokeColor(HexColor('#DCE4EA'));c.line(LEFT,35,W-LEFT,35)
    c.setFillColor(HexColor(MUTED));c.setFont('Arial',8)
    c.drawString(LEFT,22,'Recording guide - companion to the analytical report')
    c.drawRightString(W-LEFT,22,str(c.getPageNumber()))
def page_done():footer();c.showPage()
def stamp(t):return f'{t//60}:{t%60:02d}'

header('Recording overview')
y=para('Continuous recording script\nand screen guide',LEFT,H-55,size=25,lead=30,bold=True)-15
y=para('Main question: What do averages and snapshots hide about inequality, relationships and change over time?',LEFT,y,size=12,lead=17,bold=True)-14
y=para('Record 6:30 total, including browser demonstrations and the closing card. Export at 1.35x for approximately 4:49. Each member has 2:10 raw across two appearances. The slide times below are raw recording times.',LEFT,y,size=11,lead=15)-17
y=label('Slide timeline',y)
rows=[('SLIDE','RAW TIME','SPEAKER','SCREEN TOPIC')]
short=['Main question','Same links in three layouts','NodeTrix matrix detail','Differences within regions','Regional and individual gains','Horizon and ridgeline examples','JavaScript parallel coordinates','JavaScript treemap','Levels versus changes','Global and local colour scales','Rainfall concentration','Contour intervals','Frequency versus persistence','Wind arrow encodings','Separate and shared conditions','Answer to the main question','Closing card']
rows += [(str(s['number']),stamp(s['start'])+'-'+stamp(s['end']),
          'Closing' if s['number']==17 else s['speaker'],short[s['number']-1]) for s in slides]
for i,row in enumerate(rows):
    if i==0:
        c.setFillColor(HexColor('#E6EFF2'));c.rect(LEFT,y-19,WIDTH,21,fill=1,stroke=0)
    for x,value,w in zip([LEFT+6,LEFT+49,LEFT+126,LEFT+218],row,[42,75,90,WIDTH-222]):
        para(value,x,y-2,w=w,size=8.9,lead=12,bold=i==0)
    y-=20
y-=14
y=label('How to record',y)
y=para('Use the matching 17-slide PowerPoint. For slides 7-8, record the actual JavaScript browser pages. The following pages give exact narration, image filenames, screen content and cursor actions. Speak only the narration; the remaining text is production guidance.',LEFT,y,size=10.5,lead=14)-10
y=para('Record the animation player for slides 10 and 12. Their static previews below are reference images only. PowerPoint notes and this recording PDF use the same storyboard. Animation setup instructions follow the continuous narration.',LEFT,y,size=10.5,lead=14)
page_done()

for s in slides:
    header(f"Slide {s['number']:02d} / 17")
    c.bookmarkPage(f"slide{s['number']}")
    c.addOutlineEntry(f"Slide {s['number']}: {clean(s['title'])}",f"slide{s['number']}",level=0)
    y=para(s['title'],LEFT,H-52,size=19,lead=23,bold=True)-7
    y=para(f"{s['speaker']}  |  {stamp(s['start'])}-{stamp(s['end'])} raw  |  {s['duration']} seconds",LEFT,y,size=10.2,lead=14,color=TEAL,bold=True)-10
    image=SOURCE/'slides'/f"slide-{s['number']:02d}.png"
    height=WIDTH*9/16
    c.drawImage(str(image),LEFT,y-height,width=WIDTH,height=height,mask='auto')
    y-=height+13
    y=label('Say this',y)
    y=para(s['say'] or '[Silent closing card. Hold the screen for six seconds.]',LEFT,y,size=11.4,lead=15.3)-12
    y=label('Show on screen',y)
    y=para(s['screen'],LEFT,y,size=10,lead=13.5)-9
    y=label('Cursor actions and recording cues',y)
    y=para(s['actions'],LEFT,y,size=10,lead=13.5)-9
    y=para('Main point: '+(s['takeaway'] or s['headline']),LEFT,y,size=10,lead=13.5,bold=True)-8
    if s['images']:
        y=para('Images: '+', '.join('assets/'+name for name in s['images']),LEFT,y,size=8.5,lead=11)-6
    y=para('Evidence: '+s['source'],LEFT,y,size=8.5,lead=11,color=MUTED)
    page_done()

header('Continuous narration')
c.bookmarkPage('narration');c.addOutlineEntry('Continuous narration for rehearsal','narration',level=0)
y=para('Continuous narration\nfor rehearsal',LEFT,H-55,size=24,lead=29,bold=True)-15
y=para('Read the paragraphs as one investigation. Speaker labels and times are cues only. Keep the planned pauses for graph inspection and browser actions.',LEFT,y,size=11,lead=15)-18
for s in slides:
    if not s['say']:continue
    style=ParagraphStyle('measure',fontName='Arial',fontSize=12,leading=17)
    p=Paragraph(html.escape(clean(s['say'])),style);_,h=p.wrap(WIDTH,H)
    if y-h-42<50:
        page_done();header('Continuous narration');y=H-56
    y=para(f"{s['speaker']} - slide {s['number']} - {stamp(s['start'])}",LEFT,y,size=10,lead=14,bold=True,color=TEAL)-7
    y=para(s['say'],LEFT,y,size=12,lead=17)-19
page_done()
header('Animation setup and recording')
y=para('Use the prepared weather animations',LEFT,H-55,size=23,lead=28,bold=True)-16
steps=[
('1. Open the recording player','In output/video_presentation/animations, open player.html in a browser. No server or internet is needed. It uses the original GIF frames with one shared clock so the two colour maps stay synchronized.'),
('2. Record slide 10: 3:15-3:43','Select Colour comparison. Press F for fullscreen and H to hide controls. Press R to restart. Play two cycles while speaking; press Space to pause for the final explanation. Keep both colour bars and the date visible. Each cycle is 9.6 seconds: eight frames at 1.2 seconds each.'),
('3. Record slide 12: 4:20-4:38','First show the static contour interval comparison for six seconds. Cut to the player in Contours mode for one cycle, then hold the final frame for the handoff. Left/right arrows step through dates while paused. Contour levels remain fixed across the animation.'),
('4. Use GIFs directly if preferred','temperature_global_local_sync.gif contains both colour maps in one synchronized file. scivis_contour.gif is the contour animation. Insert them as pictures into a copy of the relevant PowerPoint slides and test in slideshow mode. The browser player is the recommended recording route because it supports pause and stepping.'),
('5. Keep the analytical figures','Rainfall concentration, persistence and condition intersections remain static result plots. Quiver remains the proportional/equal-length comparison. A wind GIF is not needed for this recording plan.'),
('6. Rebuild the assets','From the DV_ass1 workspace, run: python ass2/scripts/update_animation_script.py. This rebuilds the player and paired GIF from the existing source GIFs. To regenerate the scientific GIFs from the cached gridMET data first, run: python ass2/scripts/build_scivis.py --samples 8 --stride 6. That command also rebuilds SciVis figures; preserve the existing outputs before changing parameters.'),
('7. Assemble and export','Record at 1920 x 1080, combine the scenes in the PDF timeline, and keep total raw duration at 6:30. Export at 1.35x with pitch preservation for about 4:49. Review the final export for readable dates, legends and clear speech. No completed video is included.'),
]
for title,body in steps:
    y=para(title,LEFT,y,size=11,lead=15,bold=True,color=TEAL)-5
    y=para(body,LEFT,y,size=10.2,lead=14)-15
page_done();c.save()

# Check contents and bounds, then render every page for visual QA.
doc=fitz.open(OUT);texts=[p.get_text() for p in doc]
assert len(doc)>=19 and 'Continuous narration' in '\n'.join(texts)
for s in slides:
    assert clean(s['title']) in texts[s['number']],s['number']
    for word in clean(s['say']).split()[:5]:assert word in texts[s['number']],(s['number'],word)
for p in doc:
    for x0,y0,x1,y1,word,*_ in p.get_text('words'):
        assert 20<=x0 and x1<=W-20 and y0>=15 and y1<=H-15,(p.number,word)
    pix=p.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False)
    Image.frombytes('RGB',[pix.width,pix.height],pix.samples).save(TMP/f'page-{p.number+1:02}.png')
for start in range(0,len(doc),6):
    sh=Image.new('RGB',(1440,1370),'#dce3e9');draw=ImageDraw.Draw(sh)
    for j in range(start,min(start+6,len(doc))):
        im=ImageOps.contain(Image.open(TMP/f'page-{j+1:02}.png'),(470,650))
        x=(j-start)%3*480;y=(j-start)//3*685
        sh.paste(im,(x,y+25));draw.text((x+10,y+6),f'Page {j+1}',fill='black')
    sh.save(TMP/f'sheet-{start//6+1}.jpg')
shutil.copy2(OUT,SOURCE/OUT.name)
(TMP/'validation.json').write_text(json.dumps({'pages':len(doc),'slide_pages':17,'script_words':sum(len(s['say'].split()) for s in slides),'status':'PASS','output':str(OUT)},indent=2))
print(json.dumps({'pages':len(doc),'output':str(OUT),'bytes':OUT.stat().st_size}))
