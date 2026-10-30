"""Author the presentation's native SVG pages and a Guizang Swiss browser deck.

PPT Master compiles these editable SVG objects to PowerPoint. Scientific image
bytes and GIF frames are retained. HTML uses native text and original GIFs.
"""
from pathlib import Path
from PIL import Image
import json,html,re,csv,shutil,textwrap

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'presentation_source/internet_weather_ppt169_20261024'
G=ROOT/'tmp/presentation_skills/guizang-ppt-skill'
OUT=ROOT/'output/video_presentation'
INK='#0A0A0A';PAPER='#FAFAF8';BLUE='#002FA7';GRAY='#737373';LINE='#D4D4D2'
FONT='Segoe UI';TITLE='Segoe UI Light'

def stamp(t):return f'{int(t)//60}:{int(t)%60:02}'

class Page:
    def __init__(self,s):
        self.s=s;self.dark='dark' in s['theme'];self.bg=INK if self.dark else PAPER
        self.fg=PAPER if self.dark else INK;self.elements=[];self.groups={};self.serial=0
        self.rect(0,0,1280,720,self.bg,'background')
    def add(self,e,group):
        self.elements.append(e);self.groups.setdefault(group,[]).append(e);return e
    def rect(self,x,y,w,h,color,group='body'):
        return self.add(dict(type='rect',x=x,y=y,w=w,h=h,color=color),group)
    def line(self,x,y,w,color=LINE,group='body'):
        return self.add(dict(type='line',x=x,y=y,w=w,color=color),group)
    def text(self,value,x,y,w,size=28,color=None,font=FONT,weight=400,group='body',leading=None):
        # y is the top of the text box, not a baseline. Wrap before export.
        size=14 if size<=14 else 16 if size<=18 else 20 if size<=20 else 24 if size<=27 else 28 if size==28 else 32 if size<=39 else 44 if size<=49 else 64 if size<=59 else 80 if size<100 else 104 if size<145 else 192
        color=color or self.fg;leading=leading or size*1.18
        def width(s):
            # Font-aware wrapping; uses only text metrics, never draws an image.
            from PIL import ImageFont
            file='segoeuil.ttf' if font==TITLE else 'segoeuib.ttf' if weight>=600 else 'segoeui.ttf'
            return ImageFont.truetype('C:/Windows/Fonts/'+file,round(size)).getlength(s)
        lines=[]
        for explicit in str(value).split('\n'):
            current=''
            for word in explicit.split():
                candidate=current+' '+word if current else word
                if width(candidate)>w and current:lines.append(current);current=word
                else:current=candidate
            lines.append(current)
        return self.add(dict(type='text',text=str(value),lines=lines,x=x,y=y,w=w,h=len(lines)*leading,size=size,
                             color=color,font=font,weight=weight,leading=leading),group)
    def image(self,name,x,y,w,h,group='evidence'):
        with Image.open(P/'images'/name) as im:iw,ih=im.size
        scale=min(w/iw,h/ih);ww=iw*scale;hh=ih*scale
        return self.add(dict(type='image',file=name,x=x+(w-ww)/2,y=y+(h-hh)/2,w=ww,h=hh),group)
    def label(self,value,x,y,w=1000):return self.text(value,x,y,w,16,GRAY,weight=600,group='labels')
    def header(self):
        self.text(self.s['title'],48,38,1170,44,font=TITLE,weight=300,group='title')
    def source(self):
        self.text(self.s['source'],48,679,1120,13,GRAY,group='source')
        self.text(f'{self.s["number"]:02}',1191,679,42,14,GRAY,group='source')
    def conclusion(self,value=None):
        self.text(value or self.s['takeaway'],48,622,1165,25,color=self.fg,group='finding')

def compose(s):
    p=Page(s);n=s['number'];images=s['images']
    if n==1:
        p.rect(0,0,1280,720,BLUE,'background')
        p.text('DAS732 · ASSIGNMENT 2',52,45,1100,18,PAPER,weight=600,group='identity')
        p.text('Beyond averages\nand snapshots',48,158,1184,104,PAPER,TITLE,300,'title',112)
        p.text('What do summaries leave out?',52,423,1100,36,PAPER,TITLE,300,'question')
        p.line(52,520,1176,'#7796D6','identity')
        p.text('01  INTERNET',52,550,550,27,PAPER,weight=600,group='route')
        p.text('02  WEATHER',670,550,530,27,PAPER,weight=600,group='route')
        p.text('Parikshith Aithal K V · Sindhoor Ganapathi Hegde · Varshith M Gowda',52,644,1170,18,PAPER,group='identity')
        return p
    p.header()
    if n==2:
        p.label('ONE COUNTRY GRAPH · THREE DRAWINGS',50,110)
        p.image(images[0],48,153,1184,405)
        p.text('179',48,557,190,56,BLUE,TITLE,300,'finding')
        p.text('countries',239,581,180,22,group='finding')
        p.text('590',539,557,190,56,BLUE,TITLE,300,'finding')
        p.text('stored links',730,581,270,22,group='finding')
        p.text('India keeps the same six neighbors',48,638,1170,25,group='finding')
    elif n==3:
        p.text('18 / 28',48,122,410,90,BLUE,TITLE,300,'finding')
        p.text('possible pairs are linked',50,224,650,24,group='finding')
        p.image(images[0],48,274,1184,313)
        p.text('Teal = link     White = no link     Gray = same country',48,608,1174,25,group='legend')
        p.text('Cuba / Palestine: 6 internal links each     Laos: 3',48,644,1160,20,color=GRAY,group='legend')
    elif n==4:
        p.label('2010 → 2020 · SAME AXES',48,108)
        p.image(images[0],40,156,1200,379)
        p.text('South Africa',48,548,550,29,group='finding')
        p.text('+48.1 adoption points / +0.7 broadband',48,588,550,24,group='finding')
        p.text('China',684,548,530,29,group='finding')
        p.text('+35.8 adoption points / +24.6 broadband',684,588,530,24,group='finding')
        p.text('Broadband changes are subscriptions per 100 people.',48,647,1170,19,GRAY,group='source')
    elif n==5:
        p.text('6 of 175',48,106,420,56,BLUE,TITLE,300,'finding')
        p.text('≥70% online  /  ≤5 broadband per 100',510,127,720,29,group='finding')
        p.image(images[0],48,197,1184,386)
        p.text('Brush → compare → reorder axes',48,614,860,28,group='finding')
        p.text('Live browser demonstration',48,655,960,18,BLUE,weight=600,group='demo-link')['href']='http://127.0.0.1:8765/web/index.html'
    elif n==6:
        p.label('SAME TOTAL · SAME COUNTRY VALUES',48,108)
        p.image(images[0],48,168,562,398)
        p.image(images[1],670,168,562,398)
        p.text('Region first',48,575,562,28,group='labels')
        p.text('Adoption band first',670,575,562,28,group='labels')
        p.text('4.52 billion included users · area = count · country color = adoption',48,618,1165,24,group='finding')
        p.text('Live zoom and hierarchy switch',48,650,900,17,BLUE,weight=600,group='demo-link')['href']='http://127.0.0.1:8765/web/treemap.html'
    elif n==7:
        p.image(images[0],48,126,668,514)
        for y,num,label in [(143,'0.83','Broadband × adoption'),(300,'0.53','Mobile × adoption'),(457,'0.87','Landlines × broadband')]:
            p.text(num,782,y,430,76,PAPER,TITLE,300,'finding')
            p.text(label,785,y+87,421,22,group='finding')
        p.text('Spearman rank correlations · 175 matched countries · 2020',48,648,1170,19,GRAY,group='source')
    elif n==8:
        p.text('72%',45,145,550,198,BLUE,TITLE,200,'finding')
        p.text('126 of 175 countries',51,365,530,33,group='finding')
        p.text('Internet use ↑\nLandline subscriptions ↓',51,439,570,32,group='finding')
        p.text('2015-2020 · the same countries at both dates',51,579,580,22,GRAY,group='labels')
        vals=list(csv.DictReader((ROOT/'output/simple_revision/country_changes_counts.csv').open()))[1:]
        p.bars=dict(key='regional-changes',x=660,y=170,w=550,h=400,maximum=100,
            labels=[r['region'] for r in vals],values=[float(r['percent']) for r in vals],unit='%',decimals=0)
        draw_bars(p,p.bars)
        p.text('Share with both directions of change',659,612,560,21,GRAY,group='labels')
    elif n==9:
        p.text('47%',48,134,395,161,BLUE,TITLE,200,'finding-left')
        p.text('within regions',53,322,425,32,group='finding-left')
        p.text('53%',49,430,360,96,p.fg,TITLE,300,'finding-left')
        p.text('between regional means',54,544,430,25,group='finding-left')
        p.image(images[0],493,147,739,396)
        p.text('A regional label leaves much of the country spread unseen.',495,564,729,26,group='finding')
        p.text('Variance split · 158 classified countries · equal country weights',48,648,1170,19,GRAY,group='source')
    elif n==10:
        p.text('26.55',48,112,460,79,PAPER,TITLE,300,'finding')
        p.text('Shift in Asia’s regional median',52,205,540,25,group='finding')
        p.text('19.75',675,112,470,79,PAPER,TITLE,300,'finding')
        p.text('Median individual country gain',679,205,540,25,group='finding')
        p.image(images[0],48,260,1184,330)
        p.text('Both are percentage-point changes. The order of calculation matters.',48,628,1174,25,group='conclusion')
    elif n==11:
        p.label('HORIZON VIEW · 50% REFERENCE',48,108)
        p.image(images[0],48,161,850,413)
        for y,num,label in [(171,'2003','Singapore'),(316,'2015','China'),(461,'—','Tanzania by 2020')]:
            p.text(num,944,y,288,61,BLUE,TITLE,300,'finding')
            p.text(label,947,y+75,283,23,group='finding')
        p.text('Red = below 50%, not declining adoption',48,625,1174,26,group='conclusion')
    elif n==12:
        p.text('2.2% → 71.4%',48,106,1170,68,BLUE,TITLE,300,'finding')
        p.image(images[0],48,220,1184,353)
        p.text('A rising median can coexist with wide country differences.',48,620,1170,27,group='finding')
    elif n==13:
        p.text('Internet complete.\nNow: daily weather.',48,130,1145,83,PAPER,TITLE,300,'chapter')
        for x,num,label in [(48,'92','days'),(465,'8','sampled dates'),(882,'4','weather fields')]:
            p.text(num,x,390,350,91,PAPER,TITLE,200,'finding')
            p.text(label,x+2,498,345,26,PAPER,group='finding')
        p.text('July-September 2023 · same 13,416 valid cells · datasets analyzed separately',48,621,1170,23,PAPER,group='labels')
    elif n==14:
        p.text('Fixed scale',48,125,560,33,BLUE,TITLE,300,'labels')
        p.text('Daily scale',672,125,560,33,BLUE,TITLE,300,'labels')
        p.image(images[0],48,193,562,331,'gif-fixed')
        p.image(images[1],670,193,562,331,'gif-daily')
        p.text('Same color = same temperature',48,553,560,25,group='finding')
        p.text('Same color can mean different temperatures',670,553,562,25,group='finding')
        p.text('Eight dates · original animated GIFs · 6.4-second loops',48,645,1170,20,GRAY,group='source')
    elif n==15:
        p.text('−4.64°C',48,107,620,91,BLUE,TITLE,300,'finding')
        p.text('99.66% of the area cools',684,131,546,35,group='finding')
        p.image(images[0],48,248,1184,310)
        p.text('Two daily snapshots disagree in sign over 18.26% of the area.',48,617,1174,27,group='finding')
    elif n==16:
        p.text('77.6%',48,108,510,89,PAPER,TITLE,300,'finding')
        p.text('September eligible area with ≥50% of its rain\nin its wettest five consecutive days',580,124,650,27,PAPER,group='finding')
        p.image(images[0],48,254,1184,354)
        p.text('Similar totals can arrive with different timing.',48,638,1175,26,group='finding')
    elif n==17:
        p.label('EMBEDDED CONTOUR GIF · EIGHT DATES',48,108)
        p.image(images[0],48,155,942,480,'gif-contour')
        p.text('5°C',1015,195,215,68,BLUE,TITLE,300,'finding')
        p.text('More boundaries',1019,279,204,24,group='finding')
        p.text('10°C',1015,404,215,68,BLUE,TITLE,300,'finding')
        p.text('Fewer boundaries',1019,488,204,24,group='finding')
        p.text('The interval experiment uses the same field; contour tracing follows the grid.',48,648,1170,18,GRAY,group='source')
    elif n==18:
        p.text('22.8% → 2.2%',48,119,1174,81,BLUE,TITLE,300,'finding')
        p.image(images[0],48,278,1184,304)
        p.text('Mean frequency of Tmax ≥35°C · July to September',48,620,1174,27,group='finding')
    elif n==19:
        p.text('67',48,121,442,183,PAPER,TITLE,200,'finding')
        p.text('consecutive days',51,329,600,35,PAPER,group='finding')
        p.text('16.27%',761,150,468,107,PAPER,TITLE,300,'finding')
        p.text('weighted cell-days are hot and dry',767,276,459,25,PAPER,group='finding')
        p.image(images[0],48,404,1184,214)
        p.text('Hot: Tmax ≥35°C · Dry: rain <1 mm/day · threshold comparison in report Fig. 30',48,650,1170,19,GRAY,group='source')
    elif n==20:
        p.label('SAME WIND FIELD · DENSITY AND LENGTH EXPERIMENT',48,108)
        p.image(images[0],48,157,1184,431)
        p.text('Arrows point toward the flow. Color retains wind speed.',48,626,1174,27,group='finding')
    elif n==21:
        p.text('Southwest → south',48,115,1174,62,BLUE,TITLE,300,'finding')
        p.image(images[0],48,229,1184,343)
        p.text('Source direction · identical radial scale · speed shown by stacked bands',48,620,1170,25,group='finding')
    elif n==22:
        p.text('2.57%',48,152,573,174,PAPER,TITLE,200,'finding')
        p.text('Hot + dry + windy',54,360,560,36,PAPER,group='finding')
        p.text('Same grid cell. Same day.',54,427,560,28,PAPER,group='finding')
        rows=list(csv.DictReader((ROOT/'output/simple_revision/weather_overlap.csv').open()))
        p.bars=dict(key='joint-weather',x=665,y=190,w=550,h=343,maximum=100,
            labels=['Hot','Dry','Windy','All three'],values=[float(r['area_day_percent']) for r in rows],unit='%',decimals=2)
        draw_bars(p,p.bars)
        p.text('Weighted grid-cell days · individual bars overlap',665,575,555,21,PAPER,group='labels')
        p.text('Separate frequencies cannot identify joint occurrence.',48,640,1174,26,PAPER,group='conclusion')
    elif n==23:
        p.text('What the\nsummary\nleaves out',48,148,580,88,BLUE,TITLE,300,'finding',95)
        for y,title,detail in [(156,'Differences','Country dots and paired gains'),(312,'Timing','Annual paths, daily rain and runs'),(468,'Coincidence','Conditions checked together')]:
            p.text(title,715,y,508,36,font=TITLE,weight=300,group='answer')
            p.text(detail,718,y+58,505,26,group='answer')
        p.text('Internet first. Weather second. One question about the detail behind summaries.',48,646,1174,22,GRAY,group='labels')
    elif n==24:
        p.text('Team Plot Twist',48,117,1170,79,PAPER,TITLE,300,'identity')
        for y,name,id,method in [(263,'Parikshith Aithal K V','BT2024249','Network · scalar color'),(359,'Sindhoor Ganapathi Hegde','BT2024014','Horizons / ridges · contours'),(455,'Varshith M Gowda','BT2024227','JavaScript PCP / treemap · quiver')]:
            p.text(name,50,y,649,31,PAPER,group='identity')
            p.text(id,52,y+41,610,19,GRAY,group='identity')
            p.text(method,760,y+7,470,23,PAPER,group='identity')
        p.text('OWID / ITU country data · gridMET daily weather · full sources in the report',48,638,1174,20,PAPER,group='source')
        return p
    p.source()
    return p

def draw_bars(p,b):
    x,y,w,h=b['x'],b['y'],b['w'],b['h'];labels=b['labels'];vals=b['values']
    left=x+180;plotw=w-236;row=h/len(vals)
    for i,(label,v) in enumerate(zip(labels,vals)):
        yy=y+i*row
        texty=yy+(row-26)/2
        p.text(label,x,texty,172,19,p.fg,group=b['key'])
        col=PAPER if p.dark else BLUE
        if len(vals)==4 and i<3:col='#A3A3A3'
        p.rect(left,yy+row*.255,plotw*v/b['maximum'],row*.49,col,b['key'])
        p.text(f'{v:.{b["decimals"]}f}%',left+plotw*v/b['maximum']+8,texty,86,20,p.fg,group=b['key'])
    p.line(left,y+h+1,plotw,LINE,b['key'])
    p.text('0',left,y+h+10,40,16,GRAY,group=b['key'])
    p.text('100',left+plotw-28,y+h+10,70,16,GRAY,group=b['key'])

def svg(page):
    s=page.s;parts=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1280 720" width="1280" height="720" font-family="Segoe UI" font-size="28" data-pptx-page-role="'+('cover' if s['number']==1 else 'ending' if s['number']==24 else 'section' if s['number']==13 else 'content')+'">']
    for group,original in page.groups.items():
        # Independent semantic text/image blocks get independent layout zones;
        # a background is a root framing primitive and not a content module.
        if group=='background':
            for j,e in enumerate(original):parts.append(f'<rect id="background-{j}" data-pptx-role="background" x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" fill="{e["color"]}"/>')
            continue
        combine=(group=='source' or group=='finding-left' or group=='finding' and s['number'] in {2,3,4,7,8,10,11,17,19,22} or group=='identity' and s['number']==24 or hasattr(page,'bars') and group==page.bars['key'])
        batches=[original] if combine else [[e] for e in original]
        for batch_index,els in enumerate(batches):
          left=min(e['x'] for e in els);top=min(e['y'] for e in els)
          right=max(e['x']+e['w'] for e in els)
          bottom=max(e['y']+((len(e['lines'])-1)*e['leading']+e['size']*1.32 if e['type']=='text' else e.get('h',1)) for e in els)
          href=next((e.get('href') for e in els if e.get('href')),None)
          if href:parts.append(f'<a href="{html.escape(href,quote=True)}">')
          chart=hasattr(page,'bars') and group==page.bars['key']
          if chart:
            left=page.bars['x'];top=page.bars['y']
            right=max(right,left+page.bars['w']);bottom=max(bottom,top+page.bars['h']+40)
          gid=group if chart else f'{group}-{batch_index+1}'
          replace=' data-pptx-replace-with="chart"' if chart else ''
          parts.append(f'<g id="{gid}" data-pptx-bounds="{left:.2f} {top:.2f} {right-left:.2f} {max(1,bottom-top):.2f}"{replace}>')
          if chart:
            b=page.bars
            colors=[(PAPER if page.dark else BLUE)]*len(b['values'])
            if len(colors)==4:colors=['#A3A3A3']*3+[PAPER]
            payload=dict(x=left,y=top,width=right-left,height=bottom-top,name=b['key'],type='bar',
                categories=b['labels'],series=[dict(name='Percent',values=b['values'],point_colors=colors)],
                plot_area=dict(x=b['x']+180,y=b['y'],width=b['w']-236,height=b['h']),gap_width=104,
                axes=dict(value=dict(minimum=0,maximum=100,major_unit=100,number_format='0')),
                show_legend=False,data_labels=dict(show_value=True,position='outside_end',number_format=('0.'+'0'*b['decimals'] if b['decimals'] else '0')+'"%"',font_size=20,font_family=FONT,color=page.fg),
                style=dict(font_family=FONT,axis_font_size=20,text_color=page.fg,axis_color=LINE,grid_color=LINE,chart_area_fill='none',plot_area_fill='none'))
            parts.append('<metadata type="application/json">'+html.escape(json.dumps(payload),quote=False)+'</metadata>')
            parts.append(f'<g id="{b["key"]}-chartArea">')
            parts.append(f'<!-- chart-plot-area: x_min={b["x"]+180}, x_max={b["x"]+b["w"]-56}, y_min={b["y"]}, y_max={b["y"]+b["h"]} -->')
          for e in els:
            x,y=e['x'],e['y'];t=e['type']
            if t=='rect':parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{e["w"]:.2f}" height="{e["h"]:.2f}" fill="{e["color"]}"/>')
            elif t=='line':parts.append(f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{x+e["w"]:.2f}" y2="{y:.2f}" stroke="{e["color"]}" stroke-width="1"/>')
            elif t=='image':parts.append(f'<image href="../images/{e["file"]}" x="{x:.2f}" y="{y:.2f}" width="{e["w"]:.2f}" height="{e["h"]:.2f}" preserveAspectRatio="xMidYMid meet"/>')
            elif t=='text':
                attrs=f'font-family="{e["font"]}" font-size="{e["size"]}" font-weight="{e["weight"]}" fill="{e["color"]}"'
                content=''.join(f'<tspan x="{x:.2f}" y="{y+e["size"]*.94+i*e["leading"]:.2f}">{html.escape(line)}</tspan>' for i,line in enumerate(e['lines']))
                parts.append(f'<text {attrs}>{content}</text>')
          if chart:parts.append('</g>')
          parts.append('</g>')
          if href:parts.append('</a>')
    parts.append('</svg>');return '\n'.join(parts)

def dom(page):
    s=page.s;pieces=[]
    structure={'S08':'duo-compare','S16':'brief-grid','S22':'image-hero','S07':'h-bar-chart','S20':'stacked-ledger','S03':'cover-split','S10':'closing-split','S21':'tech-spec'}.get(s['layout'],'cover-split')
    for e in page.elements:
        t=e['type'];x,y=e['x'],e['y'];sty=f'position:absolute;left:{x}px;top:{y}px;'
        if t=='rect':pieces.append(f'<div aria-hidden="true" style="{sty}width:{e["w"]}px;height:{e["h"]}px;background:{e["color"]}"></div>')
        elif t=='line':pieces.append(f'<div aria-hidden="true" style="{sty}width:{e["w"]}px;height:1px;background:{e["color"]}"></div>')
        elif t=='image':
            slot='s16-brief-16x10' if s['layout']=='S16' else 's22-hero-21x9' if s['layout']=='S22' else 'evidence-original'
            pieces.append(f'<img class="fit-contain" data-image-slot="{slot}" src="images/{e["file"]}" alt="{html.escape(s["title"])}" style="{sty}width:{e["w"]}px;height:{e["h"]}px;object-fit:contain;object-position:center center;">')
        else:
            txt='<br>'.join(html.escape(line) for line in e['lines'])
            if e.get('href'):txt=f'<a href="{html.escape(e["href"],quote=True)}" target="_blank" style="color:inherit;text-decoration:none">{txt}</a>'
            pieces.append(f'<div style="{sty}width:{e["w"]}px;height:{e["h"]+5}px;font-family:\'{e["font"]}\',Arial,sans-serif;font-size:{e["size"]}px;font-weight:{e["weight"]};line-height:{e["leading"]}px;color:{e["color"]};letter-spacing:0">{txt}</div>')
    return f'<section class="slide {s["theme"]}" data-layout="{s["layout"]}" data-slide-id="{s["id"]}" data-animate="none" style="padding:0;background:{page.bg}"><div class="canvas-card" style="padding:0;overflow:hidden;background:{page.bg}"><div class="{structure}" data-design-canvas style="position:absolute;width:1280px;height:720px;transform-origin:top left;overflow:hidden">'+''.join(pieces)+'</div></div></section>'

def notes(s):
    return f'''# {s['title']}

Speaker: {s['speaker']}
Raw recording: {stamp(s['start'])}-{stamp(s['end'])} ({s['duration']} seconds)
Chapter: {s['chapter']}

## Narration
{s['say'] or '[Silent closing card]'}

## On screen
{s['screen']}

## Actions
{s['actions']}

## Transition
{s['transition']}

## Source
{s['source']}. Current report: ../pdf/DAS732_A2_Report_IEEE.pdf
'''

def build():
    story=json.loads((P/'storyboard.json').read_text(encoding='utf-8'))
    pages=[compose(s) for s in story['slides']]
    (P/'svg_output').mkdir(exist_ok=True)
    for page in pages:
        s=page.s;stem=f'{s["number"]:02}_{s["id"]}'
        (P/'svg_output'/f'{stem}.svg').write_text(svg(page),encoding='utf-8')
        (P/'notes'/f'{stem}.md').write_text(notes(s),encoding='utf-8')
    (P/'analysis/slide_elements.json').write_text(json.dumps([dict(number=p.s['number'],elements=p.elements) for p in pages],indent=2),encoding='utf-8')
    # Start from the actual Guizang template and retain its presenter runtime.
    template=(G/'assets/template-swiss.html').read_text(encoding='utf-8')
    template=re.sub(r'<title>.*?</title>','<title>Beyond Averages and Snapshots · Internet then Weather</title>',template,count=1)
    template=template.replace('lang="zh-CN"','lang="en"',1)
    start=template.index('<div id="deck">');end=template.index('<div id="nav">',start)
    template=template[:start]+'<div id="deck">'+''.join(dom(p) for p in pages)+'</div>\n\n'+template[end:]
    entries=[dict(id=s['id'],title=s['title'],section=s['chapter'],minutes=s['duration']/60,purpose=s['takeaway'],talk=[s['say'] or 'Silent closing card. Hold for six seconds.'],transition=s['transition'] or 'End the recording.',cue=s['actions'],advance=f'After {s["duration"]} seconds of planned recording',delivery=f'{s["speaker"]} · {stamp(s["start"])}-{stamp(s["end"])}') for s in story['slides']]
    template=re.sub(r'const SPEAKER_NOTES = \[.*?\n\];',lambda _: 'const SPEAKER_NOTES = '+json.dumps(entries,ensure_ascii=False)+';',template,count=1,flags=re.S)
    # Fonts are already installed on the recording machine; no network needed.
    template=re.sub(r'<link[^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>','',template)
    template=template.replace('max-width:100vw','max-width:100vw')
    extras='''<style>
body{font-family:"Segoe UI",Arial,sans-serif} .slide [data-design-canvas]{display:block!important;margin:0!important;padding:0!important;min-height:0;gap:0}
.slide .canvas-card{position:relative;width:100%;height:100%;border-radius:0;box-shadow:none}
.slide .duo-compare,.slide .image-hero,.slide .brief-grid,.slide .cover-split,.slide .closing-split,.slide .tech-spec,.slide .h-bar-chart,.slide .stacked-ledger{display:block}
#ppt-presenter-btn,#ppt-overview-btn{font-family:"Segoe UI",Arial,sans-serif}
</style>'''
    template=template.replace('</head>',extras+'</head>')
    scaler='''<script>
function fitEvidenceCanvas(){document.querySelectorAll('[data-design-canvas]').forEach(el=>{const scale=Math.min(innerWidth/1280,innerHeight/720);el.style.transform='scale('+scale+')';el.style.left=((innerWidth-1280*scale)/2)+'px';el.style.top=((innerHeight-720*scale)/2)+'px';});}
addEventListener('resize',fitEvidenceCanvas);fitEvidenceCanvas();
</script>'''
    template=template.replace('</body>',scaler+'</body>')
    # Translate the visible chrome; preserve all stable identifiers and behavior.
    for a,b in [('演讲模式','Presenter'),('总览','Overview'),('上一页','Previous'),('下一页','Next'),('静态','Static'),('全屏','Fullscreen'),('观众屏','Audience'),('演示设置','Settings'),('暂停计时','Pause timer'),('重新开始','Restart'),('讲稿','Script'),('备注','Notes')]:template=template.replace(a,b)
    template=template.replace('<!-- SLIDES_HERE','<!-- Source: Guizang Swiss template')
    (P/'index.html').write_text(template,encoding='utf-8')
    shutil.copy2(G/'assets/motion.min.js',P/'motion.min.js')
    # Keep license/provenance with the reusable HTML runtime, off the slides.
    (P/'third_party').mkdir(exist_ok=True)
    shutil.copy2(G/'LICENSE',P/'third_party/guizang-LICENSE.txt')
    (P/'third_party/README.md').write_text('Browser runtime and registered Swiss layout vocabulary: https://github.com/op7418/guizang-ppt-skill\n\nNative PowerPoint conversion: https://github.com/hugohe3/ppt-master\n',encoding='utf-8')
    print(f'Authored {len(pages)} SVG pages, shared notes and Guizang browser deck.')

if __name__=='__main__':build()
