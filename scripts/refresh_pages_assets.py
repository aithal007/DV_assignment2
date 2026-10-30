"""Refresh the GitHub Pages site in docs/ from this assignment checkout."""
from pathlib import Path
import html
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'docs'

def copy(rel):
    src=ROOT/rel;dst=SITE/rel
    if not src.is_file():raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)

def main():
    for p in (ROOT/'web').iterdir():
        if p.is_file() and (p.suffix in {'.js','.css'} or p.name in {'index.html','network.html','treemap.html'}):copy(p.relative_to(ROOT))
    copy('web/vendor/d3.v7.min.js')
    for name in ['data/infovis_countries.json','data/country_network_2020.json','data/treemap_countries_2020.json','data/network_all_pair_similarities.csv','output/pdf/DAS732_A2_Report_IEEE.pdf']:
        copy(name)
    for p in (ROOT/'output/pcp_changes').iterdir():
        if p.is_file() and p.suffix in {'.html','.js'}:copy(p.relative_to(ROOT))
    for name in ['scivis_contour.gif','scivis_global.gif','scivis_local.gif']:copy('images/scivis/'+name)
    for p in (ROOT/'output/network_revision').iterdir():
        if p.is_file() and p.suffix in {'.html','.png','.csv','.json'}:copy(p.relative_to(ROOT))
    figures=json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    cards=[]
    for f in figures:
        n=f['figure'];copy(f'images/report/Fig{n}.png')
        q,enc,why,note,take=f['explanation']
        details=[('Question',q),('How to read',enc),('Why this chart',why),('Interpretation',f['detailed_interpretation']),('Takeaway',take)]
        body=''.join(f'<p><strong>{html.escape(k)}.</strong> {html.escape(v).replace(chr(10),"<br>")}</p>' for k,v in details)
        cards.append(f'<article id="fig{n}"><h2>Figure {n}: {html.escape(f["title"])}</h2><a href="images/report/Fig{n}.png"><img loading="lazy" src="images/report/Fig{n}.png" alt="{html.escape(f["title"],quote=True)}"></a>{body}</article>')
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Explained figures</title><link rel="stylesheet" href="site.css"></head><body><main><p><a href="index.html">← Project home</a></p><h1>Figures and their interpretations</h1><p>Click any figure to see it at full resolution. The report contains the complete analysis.</p>'+''.join(cards)+'</main></body></html>'
    (SITE/'figures.html').write_text(page,encoding='utf-8')
    print(f'Refreshed {len(figures)} figures, interactive assets, report and weather GIFs in {SITE}.')

if __name__=='__main__':main()
