from pathlib import Path
import json,re,zipfile,hashlib,io
from lxml import etree as E
from PIL import Image
import pymupdf

root=Path(__file__).resolve().parents[1]
p=root/'presentation_source/focused_story_ppt169_20261024'
out=root/'output/video_presentation'
d=json.loads((p/'storyboard.json').read_text(encoding='utf-8'))
z=zipfile.ZipFile(out/'DAS732_A2_Video_Presentation_Final.pptx')
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
norm=lambda s:re.sub(r'\s+',' ',s).strip()
for s in d['slides']:
    xml=E.fromstring(z.read('ppt/notesSlides/notesSlide%d.xml'%s['number']))
    text=norm(' '.join(xml.xpath('//a:t/text()',namespaces=ns)))
    assert norm(s['say']) in text,('notes mismatch',s['number'])
assert len([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)])==14
gifs=[n for n in z.namelist() if n.endswith('.gif')]
originals={hashlib.sha256((root/f'images/scivis/scivis_{kind}.gif').read_bytes()).hexdigest() for kind in ['global','local','contour']}
assert len(gifs)==3
assert all(Image.open(io.BytesIO(z.read(n))).n_frames==8 and hashlib.sha256(z.read(n)).hexdigest() in originals for n in gifs)
assert all(s['chapter']=='Internet' for s in d['slides'][:7])
assert all(s['chapter']=='Weather' for s in d['slides'][7:])
pdf=pymupdf.open(root/'output/pdf/DAS732_A2_Recording_Script.pdf')
assert len(pdf)==8
pdf_text=norm(' '.join(page.get_text() for page in pdf))
for s in d['slides']:
    # All spoken words are represented in the guide, allowing PDF line wrapping.
    assert norm(s['say']).replace('’',"'") in pdf_text.replace('’',"'"),('PDF mismatch',s['number'])
assert hashlib.sha256((root/'REPORT.md').read_bytes()).hexdigest()==hashlib.sha256((p/'sources/REPORT.md').read_bytes()).hexdigest()
result=dict(slides=14,speaker_notes_match=True,pdf_pages=8,pdf_narration_matches=True,words=d['words'],original_GIFs=3,frames_per_GIF=8,Internet_first=True,report_text_unchanged=True)
(p/'validation/delivery_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
dest=p/'validation/script_pdf';dest.mkdir(exist_ok=True)
for i,page in enumerate(pdf):page.get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(str(dest/f'page-{i+1:02}.png'))
print(json.dumps(result,indent=2))
