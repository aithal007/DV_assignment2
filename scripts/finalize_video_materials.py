"""Write the local slide viewer and verify script/deck/source consistency."""
from pathlib import Path
import json,re,zipfile,html,hashlib
from xml.etree import ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/video_presentation'
story=json.loads((OUT/'storyboard.json').read_text(encoding='utf-8'))
slides=story['slides'];ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
 'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
deck=OUT/'DAS732_A2_Video_Presentation_Final.pptx'
assert deck.exists()
with zipfile.ZipFile(deck) as z:
    parts=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
    assert len(parts)==len(slides)==17
    assert len([n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)])==17
    for s in slides:
        content=ET.fromstring(z.read(f'ppt/slides/slide{s["number"]}.xml'))
        txt=' '.join(e.text or '' for e in content.findall('.//a:t',ns))
        assert s['title'] in txt,(s['number'],s['title'])
        note=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{s["number"]}.xml'))
        note_text=' '.join(e.text or '' for e in note.findall('.//a:t',ns))
        assert s['speaker'] in note_text and s['source'] in note_text
        for image in s['images']:assert (OUT/'assets'/image).is_file()
        with Image.open(OUT/'slides'/f'slide-{s["number"]:02}.png') as im:
            assert im.size==(1920,1080),im.size
assert sum(s['duration'] for s in slides)==390
assert all(a['end']==b['start'] for a,b in zip(slides,slides[1:]))
for person in ['Parikshith','Sindhoor','Varshith']:
    assert sum(s['duration'] for s in slides if s['speaker']==person)+(6 if person=='Varshith' else 0)==130

for p in [OUT/'RECORDING_SCRIPT.md',OUT/'README.md']:
    t=p.read_text(encoding='utf-8').replace('DAS732_A2_Video_Presentation.pptx',deck.name)
    p.write_text(t,encoding='utf-8')

page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Beyond Averages and Snapshots — Recording Slides</title>
<style>html,body{margin:0;background:#0c1720;color:#e8f2f7;font:16px/1.5 Arial,sans-serif}main{height:100vh;display:flex;align-items:center;justify-content:center}#slide{max-width:100vw;max-height:100vh;object-fit:contain}nav{position:fixed;bottom:10px;left:12px;background:#102b40e8;padding:6px 12px;border-radius:5px;opacity:0;transition:opacity .2s}body:hover nav,nav:focus-within{opacity:1}button{font:inherit;cursor:pointer;background:#dceaf1;color:#102b40;border:0;border-radius:3px;padding:5px 10px}#notes{display:none;position:fixed;inset:8vh 5vw;background:#f6f8fa;color:#142d43;padding:24px 36px;overflow:auto;box-shadow:0 0 0 100vmax #000a}#notes.open{display:block}#notes h2{font-size:27px}#notes p{max-width:1100px}#notes small{color:#536574}.screen{border-top:1px solid #b7c8d3;padding-top:16px}</style>
<main><img id="slide" alt="Presentation slide"></main>
<nav><button id="prev">Previous</button> <span id="counter"></span> <button id="next">Next</button> <button id="toggle">Notes (N)</button> <button id="full">Fullscreen (F)</button></nav>
<aside id="notes" aria-label="Private recording notes"></aside>
<script>
const slides=STORY;let i=0;
const pic=document.getElementById('slide'),notes=document.getElementById('notes');
function esc(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function stamp(t){return Math.floor(t/60)+':'+String(t%60).padStart(2,'0')}
function show(){let s=slides[i];pic.src='slides/slide-'+String(s.number).padStart(2,'0')+'.png';pic.alt=s.title;document.getElementById('counter').textContent=(i+1)+' / '+slides.length;notes.innerHTML='<small>PRIVATE NOTES · hide during recording with N</small><h2>'+esc(s.title)+'</h2><p><b>'+esc(s.speaker)+' · '+stamp(s.start)+'–'+stamp(s.end)+' raw</b></p><p>'+esc(s.say||'[Silent closing card]')+'</p><p class="screen"><b>Screen: </b>'+esc(s.screen)+'</p><p><b>Actions: </b>'+esc(s.actions)+'</p><small>'+esc(s.source)+'</small>'}
function step(n){i=Math.max(0,Math.min(slides.length-1,i+n));show()}
function toggle(){notes.classList.toggle('open')}
function full(){if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen()}
document.getElementById('prev').onclick=()=>step(-1);document.getElementById('next').onclick=()=>step(1);document.getElementById('toggle').onclick=toggle;document.getElementById('full').onclick=full;
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();step(1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();step(-1)}if(e.key.toLowerCase()==='n')toggle();if(e.key.toLowerCase()==='f')full();if(e.key==='Escape')notes.classList.remove('open')});show();
</script></html>'''.replace('STORY',json.dumps(slides,ensure_ascii=False).replace('</',r'<\/'))
(OUT/'index.html').write_text(page,encoding='utf-8')

# Mark the previous planning scripts as superseded so there is one final script.
for name in ['VIDEO_SCRIPT_6_MIN_30_SEC.md','VIDEO_SCRIPT_UNDER_5_MIN.md']:
    p=ROOT/name
    if not p.exists():continue  # Superseded scripts may have been archived.
    t=p.read_text(encoding='utf-8')
    notice='> Superseded by [the final slide-by-slide recording script](output/video_presentation/RECORDING_SCRIPT.md) and the matching 17-slide presentation.\n\n'
    if not t.startswith('> Superseded'):p.write_text(notice+t,encoding='utf-8')
first=OUT/'DAS732_A2_Video_Presentation.pptx'
if first.exists():
    target=ROOT/'tmp/video_build/first_visual_review.pptx'
    if not target.exists():first.rename(target)

validation=dict(status='PASS',slides=17,notes=17,render_size=[1920,1080],
 script_words=sum(len(s['say'].split()) for s in slides),raw_seconds=390,
 at_1_35x_seconds=390/1.35,raw_seconds_per_member=130,
 deck_sha256=hashlib.sha256(deck.read_bytes()).hexdigest(),
 evidence='Report figure mapping, presentation redraws and exact source paths supplied',
 browser_demo='Actual browser footage still needs to be recorded by the team',
 contribution_status='Adopted responsibility allocation; actual completion not certified')
(OUT/'validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
zip_path=ROOT/'output/DAS732_A2_Video_Slides_and_Script.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.rglob('*'):
        if p.is_file() and (p.suffix!='.pptx' or p.name=='DAS732_A2_Video_Presentation_Final.pptx'):z.write(p,p.relative_to(OUT).as_posix())
print(json.dumps(validation,indent=2));print('Video presentation package:',zip_path.stat().st_size,'bytes')
