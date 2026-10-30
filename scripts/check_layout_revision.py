"""Measure large empty horizontal bands in the old and compact PDF body areas."""
from pathlib import Path
import json
import numpy as np
import pymupdf as fitz

ROOT=Path(__file__).resolve().parents[1]


def measure(path):
    doc=fitz.open(path);empty_points=0;max_gap=0;body_heights=0
    for page in doc:
        pix=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
        a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)[:,:,:3]
        # Exclude outer paper margins and footer page numbers; retain body gaps.
        body=a[50:735,50:pix.width-50]
        ink=(body.min(axis=2)<235).mean(axis=1)>.003
        if page.number==len(doc)-1 and ink.any():
            # End-of-document trailing paper is not a gap in the middle of the report.
            ink=ink[:np.flatnonzero(ink)[-1]+1]
        transitions=np.diff(np.r_[False,~ink,False].astype(int))
        gaps=np.flatnonzero(transitions==-1)-np.flatnonzero(transitions==1)
        large=gaps[gaps>=12]
        empty_points+=int(large.sum());max_gap=max(max_gap,int(large.max()) if len(large) else 0)
        body_heights+=len(body)
    return dict(pages=len(doc),large_empty_horizontal_band_points=empty_points,
                body_height_points=body_heights,large_empty_band_fraction=empty_points/body_heights,
                largest_empty_band_points=max_gap)


before=measure(ROOT/'archive/before_final_research/DAS732_A2_Report_IEEE.pdf')
after=measure(ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf')
result=dict(before=before,after=after,figure_selection_changed=True,
    typography_and_image_size_limits_changed=True,
    method='Raster scan of printable body; rows with less than 0.3% dark pixels form blank bands; only runs >=12 points counted. Includes internal image whitespace and title-page spacing; excludes trailing paper after the final content on the last page.',
    change='Approved revision: gentle curve PCP, level-versus-gain comparison, fixed starting cohorts, simple-English interpretations, preserved NodeTrix and scatterplot matrix; no formal bibliography by user preference.',
    limitation='Normal margins, intentional figure whitespace and necessary readability spacing remain. This is a layout diagnostic, not a claim of zero white space.')
(ROOT/'output/layout_revision_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
