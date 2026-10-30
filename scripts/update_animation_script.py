"""Prepare synchronized recording assets and revise the canonical video script."""
from pathlib import Path
import json, shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/video_presentation'
DEST=OUT/'animations'; DEST.mkdir(exist_ok=True)
manifest=json.loads((ROOT/'data/scivis/manifest.json').read_text())
dates=manifest['sample_dates']; frames={}
for mode in ['global','local','contour']:
    source=ROOT/f'images/scivis/scivis_{mode}.gif'
    shutil.copy2(source,DEST/source.name)
    with Image.open(source) as im:
        assert im.n_frames==len(dates)==8
        frames[mode]=[]
        for i in range(8):
            im.seek(i); frame=im.convert('RGB'); frames[mode].append(frame)
            frame.save(DEST/f'{mode}-{i}.png')
paired=[]
for i in range(8):
    pair=Image.new('RGB',(1800,530),'white')
    pair.paste(frames['global'][i],(0,0));pair.paste(frames['local'][i],(900,0));paired.append(pair)
paired[0].save(DEST/'temperature_global_local_sync.gif',save_all=True,append_images=paired[1:],duration=1200,loop=0)
page='''<!doctype html><html><meta charset="utf-8"><title>Weather animation recording player</title>
<style>body{margin:0;background:#102537;color:white;font:22px Arial;text-align:center}h1{margin:25px 0 8px;font-size:32px}p{margin:8px}#maps{display:flex;align-items:center;justify-content:center;height:65vh}img{width:49%;object-fit:contain;max-height:65vh}body.contour #b{display:none}body.contour #a{width:85%}button{font:18px Arial;padding:8px;margin:8px}small{font-size:16px}nav{margin:10px}body.clean nav{visibility:hidden}</style>
<h1 id="title"></h1><p id="date"></p><div id="maps"><img id="a"><img id="b"></div>
<p id="point"></p><small>gridMET Tmax | Eight sampled dates, July-September 2023 | Degrees C | No interpolation between dates</small>
<nav><button onclick="mode='colour';i=0;draw()">Colour comparison</button><button onclick="mode='contour';i=0;draw()">Contours</button><button onclick="playing=!playing">Play / pause (Space)</button><button onclick="i=0;draw()">Restart (R)</button><button onclick="document.documentElement.requestFullscreen()">Fullscreen (F)</button><p>Arrows: step frames | H: hide controls | 1.2 seconds per frame</p></nav>
<script>const dates=DATES;let i=0,mode=location.hash==='#contour'?'contour':'colour',playing=true;
function draw(){document.body.classList.toggle('contour',mode==='contour');document.getElementById('title').textContent=mode==='colour'?'Same dates: fixed global scale versus daily local scale':'Temperature boundaries change across sampled dates';document.getElementById('date').textContent=dates[i]+' | Frame '+(i+1)+' / 8';document.getElementById('a').src=(mode==='colour'?'global':'contour')+'-'+i+'.png';document.getElementById('b').src='local-'+i+'.png';document.getElementById('point').textContent=mode==='colour'?'Left: compare temperatures across dates. Right: inspect contrast within a date.':'Contour levels stay fixed; changing boundaries reflect the sampled temperature fields.';}
setInterval(()=>{if(playing){i=(i+1)%8;draw()}},1200);
addEventListener('keydown',e=>{if(e.code==='Space'){e.preventDefault();playing=!playing}if(e.key==='ArrowRight'||e.key==='ArrowLeft'){playing=false;i=(i+(e.key==='ArrowRight'?1:7))%8;draw()}if(e.key.toLowerCase()==='r'){i=0;draw()}if(e.key.toLowerCase()==='h')document.body.classList.toggle('clean');if(e.key.toLowerCase()==='f')document.documentElement.requestFullscreen()});draw();</script></html>'''.replace('DATES',json.dumps(dates))
(DEST/'player.html').write_text(page,encoding='utf8')
story=json.loads((OUT/'storyboard.json').read_text(encoding='utf8'))
s=story['slides'][9]
s['say']='Daily weather provides a separate test. These synchronized maps show the same eight dates. On the left, a fixed scale keeps the meaning of colour constant. On the right, daily limits reveal local contrast, but the same colour can mean different temperatures. Stronger contrast alone does not establish a hotter day. What do monthly summaries hide?'
s['screen']='Replace the static preview with animations/player.html in colour mode. Show both maps, date and colour bars. The paired GIF is temperature_global_local_sync.gif.'
s['actions']='3:15-3:18 introduce maps; 3:18-3:38 play two cycles; 3:38-3:43 pause and explain the scale difference. Press R to restart, Space to pause, F for fullscreen and H to hide controls. Global limits cover eight samples, not all 92 days.'
s=story['slides'][11]
s['say']='First, finer contour intervals reveal more boundaries in the same field. Now, with levels fixed, the animation shows spatial boundaries changing across dates. These are eight sampled days. Next, we ask how often hot and dry conditions occur, and how long they last.'
s['screen']='4:20-4:26 show the existing 5-degree/10-degree static comparison. At 4:26 cut to animations/player.html#contour, retaining the date, units and fixed contour levels.'
s['actions']='Play one 9.6-second cycle from 4:26 to about 4:36, then hold for the handoff at 4:38. Distinguish changing contour spacing in the still from changing dates in the animation. Do not infer continuous motion between samples.'
story['animation_revision']='Required video per user; slides 10 and 12 use recorded animation player; PowerPoint notes and recording PDF are rebuilt from this same storyboard.'
(OUT/'storyboard.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf8')
(OUT/'CONTINUOUS_NARRATION.txt').write_text('\n\n'.join(f"{s['speaker']} - {s['start']//60}:{s['start']%60:02}\n{s['say']}" for s in story['slides'] if s['say']),encoding='utf8')
guide=['# Current recording script','The PDF is the recording copy. Animation scenes 10 and 12 match the rebuilt PowerPoint notes. Total raw time remains 6:30.']
for s in story['slides']:
    guide += [f"## Slide {s['number']}: {s['title']}",s['screen'],s['actions'],s['say']]
(OUT/'RECORDING_SCRIPT.md').write_text('\n\n'.join(guide),encoding='utf8')
print('Prepared three source GIFs, synchronized comparison GIF, 24 frames and recording player. Updated scenes 10 and 12.')
