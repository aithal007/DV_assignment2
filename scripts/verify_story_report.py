"""Check selected report integrity, source artifacts and required browser inputs."""
from pathlib import Path
import json
import re
import subprocess
import zipfile
import csv
import statistics
from urllib.parse import unquote
from PIL import Image
import pymupdf as fitz

ROOT=Path(__file__).resolve().parents[1]


def main():
    figures=json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    report=(ROOT/'REPORT.md').read_text(encoding='utf-8')
    tex=(ROOT/'report_latex/DAS732_A2_Report.tex').read_text(encoding='utf-8')
    expected=list(range(1,33))
    assert [f['figure'] for f in figures]==expected
    assert [int(x) for x in re.findall(r'!\[Figure (\d+)\]',report)]==expected
    assert [int(x) for x in re.findall(r'\\includegraphics[^\n]+\{Fig(\d+)\.png\}',tex)]==expected
    assert sum(not f['supporting'] for f in figures)==32
    assert report.count('**What it shows.**')==32
    assert report.count('**Takeaway.**')==32
    assert 'Author contributions and task allocation' in report
    for code in ['BT2024249','BT2024014','BT2024227']: assert code in report and code in tex
    assert 'AI assistance disclosure for this working revision' not in report
    assert 'Required implementation evidence and its location' not in tex
    assert len(re.findall(r'\\bibitem\{',tex))==0
    # Independent order-statistic calculation, without NumPy's quantile implementation.
    panel={}
    with (ROOT/'data/internet_panel_2000_2020.csv').open() as stream:
        for row in csv.DictReader(stream):
            panel.setdefault(row['code'],{})[int(row['year'])]=float(row['internet_users_share_pct'])
    panel={k:v for k,v in panel.items() if all(y in v for y in range(2000,2021))}
    assert len(panel)==159
    q0=statistics.quantiles([r[2000] for r in panel.values()],n=10,method='inclusive')
    q1=statistics.quantiles([r[2020] for r in panel.values()],n=10,method='inclusive')
    gains=statistics.quantiles([r[2020]-r[2000] for r in panel.values()],n=10,method='inclusive')
    with (ROOT/'output/lecture_previews/adoption_quantile_change.csv').open() as stream:
        for i,row in enumerate(csv.DictReader(stream)):
            for field,value in [('adoption_2000',q0[i]),('adoption_2020',q1[i]),('distribution_shift',q1[i]-q0[i]),('individual_gain_quantile',gains[i])]:
                assert abs(float(row[field])-value)<1e-9,(i,field)
    for f in figures:
        assert (ROOT/f['path']).exists()
        assert len(f['explanation'])==5 and all(f['explanation'])
        assert len(f['detailed_interpretation'].split())>=25
        with Image.open(ROOT/f['path']) as im: im.verify()
    for n in expected:
        with Image.open(ROOT/f'report_latex/figures/Fig{n}.png') as im: im.verify()
    with zipfile.ZipFile(ROOT/'output/DAS732_A2_LaTeX_Source.zip') as z:
        bundled=sorted(int(re.search(r'Fig(\d+)\.png',name)[1]) for name in z.namelist() if re.search(r'Fig\d+\.png',name))
        assert bundled==expected
    animation_frames={}
    for p in (ROOT/'images/scivis').glob('*.gif'):
        with Image.open(p) as im: animation_frames[p.name]=im.n_frames
    assert len(animation_frames)==3 and set(animation_frames.values())=={8}
    network=json.loads((ROOT/'data/country_network_2020.json').read_text())
    rows=json.loads((ROOT/'data/infovis_countries.json').read_text())
    tree=json.loads((ROOT/'data/treemap_countries_2020.json').read_text())
    assert len(network['nodes'])==179 and len(network['edges'])==797 and len(network['all_edges'])==15931 and len(network['layouts'])==3
    old={r['code'] for r in rows if r['year']==2015}; latest={r['code'] for r in rows if r['year']==2020}
    assert len(old&latest)==175 and len(tree['countries'])==184
    assert sum(r['internet_users'] for r in tree['countries'])==tree['included_total']==4521767530
    for js in ['app.js','network.js','treemap.js']:
        subprocess.run(['node','--check',str(ROOT/'web'/js)],check=True,capture_output=True)
    # Verify actual links in the launcher and generated gallery, without claiming browser interaction.
    link_count=0
    for p in [ROOT/'web/home.html',ROOT/'output/quality_figures/index.html']:
        for ref in re.findall(r'(?:href|src)="([^"]+)"',p.read_text(encoding='utf-8')):
            if ref.startswith(('http:','https:','#')): continue
            assert (p.parent/unquote(ref.split('#')[0])).exists(), (p,ref)
            link_count+=1
    pdf=fitz.open(ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf')
    assert 12<=len(pdf)<=27, f'Unexpected report length: {len(pdf)}'
    assert {18,25}.issubset({f.get('previous_review_figure') for f in figures})
    assert {'country_paths','fixed_initial_cohorts','association_audit'}.issubset({f.get('extension_key') for f in figures})
    companions=json.loads((ROOT/'data/supplementary_figure_manifest.json').read_text(encoding='utf-8'))
    assert any('adoption_quantile_change' in f['path'] for f in companions)
    assert any('nodetrix' in f['path'] for f in companions)
    assert {'within_regions','nodetrix_detail','weather_overlap_simple','regional_endpoints_gains','rainfall_concentration'}.issubset({f.get('extension_key') for f in figures})
    text='\n'.join(p.get_text() for p in pdf)
    text=' '.join(text.split())
    assert tex.count(r'\takeaway{')==32
    assert '47%' in text and '77.6' in text
    assert 'Marching Squares' in text
    assert '??' not in text and '32-figure review' not in text
    assert 'JavaScript' in text and '2.57' in text and '67' in text
    assert 'python-Xutf8' not in text
    assert 'run_visualizations.py' in text
    # No text should cross the physical paper edge. Margin diagnostics remain visual QA.
    for page in pdf:
        for x0,y0,x1,y1,word,*_ in page.get_text('words'):
            assert x0>=-1 and y0>=-1 and x1<=page.rect.width+1 and y1<=page.rect.height+1,(page.number,word)
    log=(ROOT/'report_latex/DAS732_A2_Report.log').read_text(encoding='utf-8',errors='replace')
    overfull=re.findall(r'Overfull \\hbox \(([\d.]+)pt too wide\)',log)
    assert not overfull,overfull
    assert 'Overfull \\vbox' not in log
    result=dict(status='PASS',main_figures=32,supporting_figures=0,pdf_pages=len(pdf),
        numbered_source_figures=32,local_links_checked=link_count,animation_frames=animation_frames,
        javascript='three scripts pass Node syntax checks; source handlers and data/asset counts checked',
        browser_interaction='see output/infovis_audit_20261026/interactions.json for actual browser controls tested',
        contribution_status='three-person responsibility allocation adopted; completed implementation not certified',
        layout='no overfull horizontal boxes; page bounds checked; rendered pages visually reviewed separately')
    (ROOT/'output/story_report_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
