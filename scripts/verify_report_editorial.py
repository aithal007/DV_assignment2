"""Verify report links, attribution, first-page structure and all 32 takeaways."""
from pathlib import Path
from urllib.parse import urlsplit
import json
import pymupdf
from report_editorial_revision import BASE,TAKEAWAYS,links

ROOT=Path(__file__).resolve().parents[1]

def main():
    figures=json.loads((ROOT/'data/current_figure_manifest.json').read_text())
    pdf=pymupdf.open(ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf')
    assert len(pdf)<=27
    first=pdf[0];words=first.get_text('words')
    title=' '.join(w[4] for w in words if w[3]<175)
    assert 'gridMET' not in title and 'July-September' not in title
    page=' '.join(first.get_text().split())
    assert 'Live dashboard' in page and 'Country inputs and cleaning' in page
    plain_page=page.replace('’',"'")
    assert '95th percentile' in plain_page and "professor's advice" in plain_page and "P95 is our team's choice" in plain_page
    assert 'preprocess_data' in page.replace(' ','')
    first_links=[a for a in first.get_links() if a.get('uri')==BASE]
    assert len(first_links)==1
    rect=first_links[0]['from'];assert abs((rect.x0+rect.x1)/2-first.rect.width/2)<5
    uris=[a['uri'] for p in pdf for a in p.get_links() if a.get('kind')==pymupdf.LINK_URI]
    for f in figures:
        n=f['figure'];aid=f.get('analysis_id',n)
        from report_structure_revision import remap
        assert f['explanation'][4]==remap(TAKEAWAYS[aid])
        for label,url in links(aid,n):
            assert url in uris,(n,url)
            assert any(x['url']==url for x in f['live_links'])
            parsed=urlsplit(url)
            assert parsed.netloc=='aithal007.github.io'
    alltext=' '.join(' '.join(p.get_text().split()) for p in pdf)
    for text in ['0.569763','797','15,931','12 isolates','README','team selects P95','not a plotting error']:
        if text=='not a plotting error':assert 'plotting error' in alltext
        else:assert text.lower() in alltext.lower(),text
    assert 'Afghanistan' not in figures[2]['explanation'][4]
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    for term in ['preprocess_data.py','--stage data','--stage figures','--stage report','--download-weather','13,387','823','12,564','P95','refresh_pages_assets.py']:
        assert term in readme,term
    # Every online figure anchor must have a real card and every local destination
    # must be represented in the published docs tree after refresh.
    gallery=(ROOT/'docs/figures.html').read_text(encoding='utf-8')
    for f in figures:
        n=f['figure'];assert f'id="fig{n}"' in gallery
        for _,url in links(f.get('analysis_id',n),n):
            rel=urlsplit(url).path.removeprefix('/DV_assignment2/')
            assert (ROOT/'docs'/rel).is_file(),rel
    assert len(__import__('re').findall(r'\\bibitem\{',(ROOT/'report_latex/DAS732_A2_Report.tex').read_text(encoding='utf-8')))==10
    assert figures[5]['analysis_id']==31 and figures[-1]['analysis_id']==32
    result=dict(status='PASS',pages=len(pdf),figures=len(figures),centered_first_page_dashboard=True,per_figure_links=sum(len(f['live_links']) for f in figures),pdf_uri_links=len(uris),professor_guidance_distinguished_from_team_cutoff=True,all_takeaways_rewritten=True,extra_plots_integrated=True,references=10)
    (ROOT/'output/report_editorial_validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
