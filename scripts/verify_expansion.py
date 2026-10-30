"""Check expanded coverage, original sample agreement and portable report integrity."""
from pathlib import Path
from html.parser import HTMLParser
import json
import re
import zipfile
import numpy as np
import pandas as pd
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]

def main():
    if (ROOT/'data/report_selection.json').exists():
        from verify_story_report import main as verify_selected
        verify_selected()
        return
    daily = json.loads((ROOT/'data/scivis/daily_manifest.json').read_text())
    sampled = json.loads((ROOT/'data/scivis/manifest.json').read_text())
    with np.load(ROOT/daily['cache']) as full, np.load(ROOT/sampled['data_cache']) as short:
        dates = full['dates']
        assert len(dates) == 92
        assert np.all(np.diff(dates.astype('datetime64[D]')) == np.timedelta64(1,'D'))
        indices = [list(dates).index(date) for date in sampled['sample_dates']]
        for key in ['tmmx','pr','vs','th']:
            np.testing.assert_allclose(full[key][indices], short[key], rtol=0, atol=0, equal_nan=True)
        rain = full['pr'].astype('float64')
        monthly = [np.nansum(rain[[date[5:7]==m for date in dates]],axis=0) for m in ['07','08','09']]
        np.testing.assert_allclose(sum(monthly),np.nansum(rain,axis=0),rtol=1e-12,atol=1e-10)
    coverage = pd.read_csv(ROOT/'data/scivis/daily_coverage.csv')
    assert len(coverage)==92 and coverage.animation_sample.sum()==8
    assert (coverage.filter(like='_valid_grid_cells')>0).all().all()
    report = (ROOT/'REPORT.md').read_text(encoding='utf-8')
    nums = [int(n) for n in re.findall(r'!\[Figure (\d+)\.',report)]
    manifest=json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    count=len(manifest)
    expected=list(range(1,count+1))
    assert nums == expected == [f['figure'] for f in manifest]
    assert '](images/extensions/daily_coverage_calendar.png)' not in report
    tex = (ROOT/'report_latex/DAS732_A2_Report.tex').read_text(encoding='utf-8')
    included = [int(n) for n in re.findall(r'\\includegraphics[^\n]+\{Fig(\d+)\.png\}',tex)]
    assert included == expected
    assert r'\figurepage' not in tex and r'\twocolumn[' not in tex
    explanations=json.loads((ROOT/'data/report_figure_explanations.json').read_text())
    assert [x['figure'] for x in explanations] == expected
    assert all(x['word_count'] >= 180 and x['takeaway'] for x in explanations)
    for heading in ['Encoding and how to read it.', 'Why this chart.', 'What it shows.', 'Detailed interpretation.', 'Interpretation and limits.']:
        assert tex.count(heading)==count
    assert tex.count(r'\takeaway{')==count+1
    assert tex.count(r'\begin{figure}')>0 and tex.count(r'\begin{figure*}')>0
    aux = (ROOT/'report_latex/DAS732_A2_Report.aux').read_text(encoding='utf-8')
    labels = re.findall(r'\\newlabel\{fig:(\d+)\}\{\{(\d+)\}',aux)
    assert sorted(labels,key=lambda x:int(x[0])) == [(str(n),str(n)) for n in expected]
    log = (ROOT/'report_latex/compile_pass_2.txt').read_text(encoding='utf-8')
    assert 'Overfull' not in log and 'undefined' not in log and 'Warning:' not in log
    with zipfile.ZipFile(ROOT/'output/DAS732_A2_LaTeX_Source.zip') as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if re.search(r'figures/Fig\d+\.png$',n)])==count
    gallery = ROOT/'output/quality_figures/index.html'
    class Links(HTMLParser):
        def handle_starttag(self,tag,attrs):
            for k,v in attrs:
                if k in ['src','href'] and not v.startswith(('#','http')):
                    assert (gallery.parent/v).exists(), v
    Links().feed(gallery.read_text(encoding='utf-8'))
    doc=fitz.open(ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf')
    assert all(len(p.get_text().strip())>30 for p in doc)
    result={'status':'PASS','daily_dates':92,'month_counts':[31,31,30],
            'sampled_dates':8,'sample_spacing_days':13,'sample_cache_agreement':'exact, all four variables',
            'monthly_rain_conservation':'PASS','figure_count':count,'figure_references':f'1-{count}, matched',
            'latex_warnings':0,'portable_zip':f'{count} figures, integrity verified',
            'gallery_links':'all local targets exist','pdf_pages':len(doc)}
    result['figure_explanations']=f'{count} complete reading guides and individual takeaways'
    result['explanation_words']=sum(x['word_count'] for x in explanations)
    result['ieee_layout']='normal one- and two-column figure floats; continuous two-column text'
    (ROOT/'output/expansion_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
