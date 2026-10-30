"""Publish the amended 14-scene recording guide, previews and matching PDF."""
from pathlib import Path
import json,shutil,html,re,zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pymupdf
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];O=R/'output/video_presentation';T=R/'tmp/network_video'
d=json.loads((O/'storyboard.json').read_text(encoding='utf8'));slides=d['slides']
for s in slides:
    p=T/f'powerpoint_render/Slide{s["number"]}.PNG'
    assert p.exists();shutil.copy2(p,O/f'slides/slide-{s["number"]:02}.png')
def stamp(t):return f'{int(t)//60}:{int(t)%60:02}'
intro='''# Current recording script - network revision, 29 October 2026

14 slides; 6:30 raw, approximately 4:49 at 1.35x. The network scenes 2-3 now follow the instructor clarification: all pair scores, an explicit threshold and a recomputed NodeTrix example. The original six-neighbor and Cuba/Palestine examples are superseded. Other scenes and timings are retained. The PDF and final PowerPoint contain matching narration for this revision.

Record slide 2 with the similarity histogram and retained-edge count. Slide 3 uses a clearly labeled five-country excerpt of the 15-country group. Counts of 14 and 7 refer to the full group. For the browser network demonstration, show the default 797 pairs, move the threshold to zero for 15,931 pairs, then reset. GIFs remain embedded on slides 8 and 10. Use desktop PowerPoint Slide Show and preserve the dates and colour bars. Record actual JavaScript brushing for slides 4-5, as described in their actions. Human voice and browser footage still need recording.
'''
md=intro
for s in slides:md+=f"\n## {s['number']}. {s['title']}\n\n{s['speaker']} | {stamp(s['start'])}-{stamp(s['end'])}\n\n**Say:** {s['say'] or '[Silent closing hold]'}\n\n**Do:** {s['actions']}\n\n**Source:** {s['source']}\n"
(O/'RECORDING_SCRIPT.md').write_text(md,encoding='utf8')
(O/'README.md').write_text(intro.replace('# Current recording script','# Current recording package')+'\nUse DAS732_A2_Video_Presentation_Final.pptx and DAS732_A2_Recording_Script.pdf. Earlier reviewed decks are historical; their network scenes are superseded. The offline index.html uses updated stills for scenes 2-3; other animations remain.\n',encoding='utf8')
page=O/'index.html';markup=page.read_text(encoding='utf8')
for ident,number in [('nodetrix-read',2),('nodetrix-finding',3)]:
    pattern=r'<section\b[^>]*data-slide-id="'+ident+r'"[^>]*>.*?</section>'
    replacement=f'<section class="slide light" data-layout="S22" data-slide-id="{ident}" data-animate="none" style="padding:0;background:#F5F2EA"><div class="canvas-card" style="padding:0;overflow:hidden"><div data-design-canvas style="position:absolute;width:1280px;height:720px;transform-origin:top left"><img src="slides/slide-{number:02}.png" alt="{html.escape(slides[number-1]["title"])}" style="width:1280px;height:720px"></div></div></section>'
    markup,count=re.subn(pattern,replacement,markup,flags=re.S);assert count==1,(ident,count)
page.write_text(markup.replace('18 / 28 pairs linked in G7','93 / 105 pairs linked in G5'),encoding='utf8')
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'));pdfmetrics.registerFont(TTFont('ArialBold','C:/Windows/Fonts/arialbd.ttf'))
W,H=A4;L=40;CW=W-80
pdf=R/'output/pdf/DAS732_A2_Recording_Script.pdf';c=canvas.Canvas(str(pdf),pagesize=A4)
def para(text,y,size=11,lead=15,bold=False):
    style=ParagraphStyle('p',fontName='ArialBold' if bold else 'Arial',fontSize=size,leading=lead)
    p=Paragraph(html.escape(text).replace('\n','<br/>'),style);_,h=p.wrap(CW,H)
    if y-h<44:raise ValueError((c.getPageNumber(),text[:50]))
    p.drawOn(c,L,y-h);return y-h
def footer():
    c.setFont('Arial',8);c.drawString(L,25,'DAS732 A2 | Recording guide | Network revision 29 October 2026');c.drawRightString(W-L,25,str(c.getPageNumber()));c.showPage()
y=para('Continuous recording script\nand screen guide',H-50,25,30,True)-18
y=para('14 slides | 6:30 raw | about 4:49 at 1.35x | 772 spoken words',y,12,17,True)-18
y=para('Main question: What do averages and snapshots hide about inequality, relationships and change over time?',y)-15
y=para('Scenes 2-3 replace the old network examples. All 15,931 pairs are scored; P95 = 0.569763 retains 797 edges. Twelve isolated countries remain. Group 5 now has 15 countries and 93 of 105 retained pairs. Use this guide with the updated final PowerPoint.',y)-20
for s in slides:y=para(f"{s['number']:02}  {stamp(s['start'])}-{stamp(s['end'])}  {s['speaker']}: {s['title']}",y,9.5,14)-5
y=para('Record the actions as well as the speech. Play the GIFs on slides 8 and 10; record the real browser brush on slides 4-5. The full network demo can show default, complete graph at zero, and reset. Raw times remain unchanged. Use pitch preservation when accelerating the final recording.',y-14,10,14)
footer()
for s in slides:
    y=para(f"{s['number']:02}. {s['title']}",H-43,19,23,True)-8
    y=para(f"{s['speaker']} | {stamp(s['start'])}-{stamp(s['end'])} raw ({s['duration']} seconds)",y,10,14)-12
    h=CW*9/16;c.drawImage(str(O/f'slides/slide-{s["number"]:02}.png'),L,y-h,width=CW,height=h);y-=h+18
    y=para('SAY',y,10,14,True)-5;y=para(s['say'] or '[Silent closing hold.]',y,11.5,16)-16
    y=para('SHOW / ACTIONS',y,10,14,True)-5;y=para(s['actions'],y,10.5,14.5)-15
    y=para('Main point: '+s['takeaway'],y,10.5,14.5,True)-12
    y=para('Source: '+s['source'],y,9,12)
    footer()
c.save();shutil.copy2(pdf,O/pdf.name)
doc=pymupdf.open(pdf);assert len(doc)==15
(O/'validation.json').write_text(json.dumps(dict(status='PASS',revision='all-pair similarity threshold, 2026-10-29',slides=14,script_words=sum(len(s['say'].split()) for s in slides),raw_seconds=390,export_speed=1.35,report_pages=26,network_pairs=15931,default_edges=797,isolates=12,changed_slides=[2,3,7],embedded_gifs_preserved=3,powerpoint_render='All 14 slides exported; changed slides and recap visually inspected',browser_controls='All layouts, default threshold, threshold zero complete graph, higher threshold and reset passed'),indent=2),encoding='utf8')
for i in range(len(doc)):
    pix=doc[i].get_pixmap(matrix=pymupdf.Matrix(1.2,1.2));pix.save(T/f'script-{i+1:02}.png')
    for x0,y0,x1,y1,*_ in doc[i].get_text('words'):assert 20<=x0 and x1<=W-20 and y0>=15 and y1<=H-15
for start in range(0,len(doc),6):
    im=Image.new('RGB',(1200,1160),'#dfe6eb')
    for j in range(start,min(start+6,len(doc))):
        thumb=ImageOps.contain(Image.open(T/f'script-{j+1:02}.png'),(390,565));im.paste(thumb,((j-start)%3*400,(j-start)//3*580))
    im.save(T/f'script-sheet-{start//6+1}.jpg')
with zipfile.ZipFile(R/'output/DAS732_A2_Video_Slides_and_Script.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in O.rglob('*'):
        if p.is_file() and (p.suffix!='.pptx' or p.name=='DAS732_A2_Video_Presentation_Final.pptx'):z.write(p,p.relative_to(O))
print('Published revised deck previews, 15-page PDF guide and video package.')
