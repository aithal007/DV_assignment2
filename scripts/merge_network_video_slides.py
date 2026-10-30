"""Replace only slides 2-3 in the existing deck, preserving all other XML/GIFs."""
from pathlib import Path
import zipfile,re,json,shutil
from xml.etree import ElementTree as ET
R=Path(__file__).resolve().parents[1];O=R/'output/video_presentation';T=R/'tmp/network_video'
NS='http://schemas.openxmlformats.org/package/2006/relationships'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
with zipfile.ZipFile(O/'DAS732_A2_Video_Presentation_Final.pptx') as z: original={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(T/'replacement_slides.pptx') as z: replacement={n:z.read(n) for n in z.namelist()}
data=dict(original)
story=json.loads((O/'storyboard.json').read_text(encoding='utf8'))
for dst,src in [(2,1),(3,2)]:
    relname=f'ppt/slides/_rels/slide{dst}.xml.rels';old=ET.fromstring(data[relname]);layout=next(r for r in old if r.get('Type').endswith('/slideLayout'));notes=next(r for r in old if r.get('Type').endswith('/notesSlide'))
    rel=ET.fromstring(replacement[f'ppt/slides/_rels/slide{src}.xml.rels'])
    for r in list(rel):
        kind=r.get('Type').split('/')[-1]
        if kind=='slideLayout':r.set('Target',layout.get('Target'))
        elif kind=='notesSlide':rel.remove(r)
        elif kind=='image':
            oldtarget=r.get('Target');filename=Path(oldtarget).name;newname=f'network29_{dst}_{filename}'
            data[f'ppt/media/{newname}']=replacement['ppt/media/'+filename];r.set('Target','../media/'+newname)
        else:raise ValueError(f'Unexpected replacement relationship: {kind}')
    notes.set('Id','rIdNetworkNotes');rel.append(notes)
    data[relname]=ET.tostring(rel,encoding='utf-8',xml_declaration=True)
    data[f'ppt/slides/slide{dst}.xml']=replacement[f'ppt/slides/slide{src}.xml']
    # Keep the original notes layout and replace its body text with the new script.
    note_path='ppt/notesSlides/'+Path(notes.get('Target')).name;root=ET.fromstring(data[note_path])
    texts=root.findall('.//{'+A+'}t');s=story['slides'][dst-1]
    if texts:
        texts[0].text=f"{s['speaker']} | {s['start']}-{s['end']}s raw\n{s['say']}\nActions: {s['actions']}\nSource: {s['source']}"
        for t in texts[1:]:t.text=''
    data[note_path]=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    # All replacement image types already occur in the source deck (PNG).
    shutil.copy2(T/f'replacement-{dst}.png',O/f'slides/slide-{dst:02}.png')
target=T/'merged_candidate.pptx'
# The Internet recap repeats the matrix count; keep that editable text aligned.
root=ET.fromstring(data['ppt/slides/slide7.xml'])
for node in root.iter('{'+A+'}t'):
    if node.text:node.text=node.text.replace('18 / 28 pairs linked in G7','93 / 105 pairs linked in G5')
data['ppt/slides/slide7.xml']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for name,blob in data.items():z.writestr(name,blob)
for n in original:
    if n.startswith('ppt/slides/slide') and re.fullmatch(r'ppt/slides/slide\d+.xml',n) and n not in ['ppt/slides/slide2.xml','ppt/slides/slide3.xml','ppt/slides/slide7.xml']:assert original[n]==data[n],n
assert all(original[n]==data[n] for n in original if n.lower().endswith('.gif'))
print('Merged slides 2-3 and corrected the recap count on slide 7; other slides and every embedded GIF are unchanged.')
