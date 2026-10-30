"""Update only the two network scenes, retaining current timing and other scenes."""
from pathlib import Path
import json,zipfile
from xml.etree import ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from PIL import Image

R=Path(__file__).resolve().parents[1];O=R/'output/video_presentation';T=R/'tmp/network_video';T.mkdir(parents=True,exist_ok=True)
backup=R/'archive/before_network_video_20261029.zip'
if not backup.exists():
    with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
        for p in O.rglob('*'):
            if p.is_file() and (p.suffix!='.pptx' or p.name=='DAS732_A2_Video_Presentation_Final.pptx'):z.write(p,p.relative_to(O))
with zipfile.ZipFile(O/'DAS732_A2_Video_Presentation_Final.pptx') as z:
    root=ET.fromstring(z.read('ppt/presentation.xml'));print('Dimensions:',root.find('{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz').attrib)
story=json.loads((O/'storyboard.json').read_text(encoding='utf8'))
s=story['slides'][1];s.update(title='Similarity needs a visible threshold',headline='15,931 possible pairs; 797 retained',takeaway='A visible threshold makes the filtered network interpretable.',say='Madam confirmed that similarity networks are suitable. We now score all fifteen thousand nine hundred and thirty-one country pairs. This histogram shows their similarities. Our declared ninety-fifth-percentile threshold keeps seven hundred and ninety-seven links. Twelve countries have no pair above it, but remain in the data. The browser can show every pair or change the threshold.',actions='Point to the histogram and cutoff. State that the top five percent is a transparent starting view, not an optimal or significant threshold. Keep the retained-edge count and isolated-node count visible.',source='Updated report Figure 1; data/network_threshold_audit.json; all-pair scores.',images=['network_threshold_video.png'])
s=story['slides'][2];s.update(title='Groups still contain unequal relationships',headline='93 of 105 pairs retained in group 5',takeaway='White means below the threshold; a shared group label still hides differences.',say='NodeTrix now uses the filtered graph. Group five retains ninety-three of its one hundred and five possible pairs. This excerpt shows five of its fifteen countries. Afghanistan has fourteen links within the full group, while Angola has seven. Teal means above our similarity threshold; white means below it. A shared group label still hides different relationships. These links describe profiles, not physical cables.',actions='Read the five-country excerpt. Compare Afghanistan and Angola; state that 14 and 7 are degrees in the full 15-country group, not only in this excerpt. Explain the Angola-Burundi white cell. Do not count excerpt cells as the full 93 edges.',source='Updated report Figure 3; output/network_revision/nodetrix_detail_matrix.csv and facts.json.',images=['network_matrix_video.png'])
story['words']=sum(len(s['say'].split()) for s in story['slides']);story['network_revision']='2026-10-29: all-pair scores, P95 cutoff, updated NodeTrix; raw timings unchanged.'
(O/'storyboard.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf8')
(O/'CONTINUOUS_NARRATION.txt').write_text('\n\n'.join(f"{s['speaker']} / slide {s['number']}\n{s['say']}" for s in story['slides'] if s['say']),encoding='utf8')
with Image.open(R/'output/network_revision/network_threshold_layouts.png') as im:
    # Original scientific panels, retaining axes, legends and cutoff.
    im.crop((0,0,im.width,int(im.height*.43))).save(O/'images/network_threshold_video.png')
d=json.loads((R/'data/country_network_2020.json').read_text());pairs={frozenset((e['source'],e['target'])) for e in d['edges']}
codes=['AFG','AGO','BDI','COD','ERI'];names=['Afghanistan','Angola','Burundi','DR Congo','Eritrea']
matrix=np.array([[float(frozenset((a,b)) in pairs) for b in codes] for a in codes]);np.fill_diagonal(matrix,.45)
fig,ax=plt.subplots(figsize=(8,6.5),layout='constrained');ax.imshow(matrix,cmap=ListedColormap(['white','#dce2e6','#168a8a']),vmin=0,vmax=1,interpolation='nearest');ax.set_xticks(range(5),codes,fontsize=16);ax.set_yticks(range(5),names,fontsize=16);ax.tick_params(length=0)
ax.set_xticks(np.arange(-.5,5,1),minor=True);ax.set_yticks(np.arange(-.5,5,1),minor=True);ax.grid(which='minor',color='#bdcbd2',lw=.7);ax.tick_params(which='minor',length=0)
ax.set_title('Five-country excerpt from group 5 (15 countries)',fontsize=16,pad=15)
fig.supxlabel('Teal: retained pair | White: below threshold | Gray: self',fontsize=13)
fig.savefig(O/'images/network_matrix_video.png',dpi=180,bbox_inches='tight',facecolor='white');plt.close(fig)
(T/'story.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf8')
print('Updated scenes 2-3, total words:',story['words'])
