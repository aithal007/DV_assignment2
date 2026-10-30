"""Stage a private assignment repository and a minimal public Pages repository."""
from pathlib import Path
import html
import json
import re
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/'tmp/github_deployment_20261030'
MAIN=STAGE/'DV_assignment2'
SITE=STAGE/'DV_assignment2_pages'
URL='https://aithal007.github.io/DV_assignment2_pages/'

def copy(rel):
    src=ROOT/rel; dst=SITE/rel
    assert src.is_file(),src
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)

def main():
    assert not MAIN.exists() and not SITE.exists(),'Use a new staging directory rather than overwriting existing work.'
    MAIN.mkdir(parents=True);SITE.mkdir()
    with zipfile.ZipFile(ROOT/'output/DAS732_A2_Report_and_JavaScript.zip') as z:
        for info in z.infolist():
            target=(MAIN/info.filename).resolve()
            assert target.is_relative_to(MAIN.resolve())
        z.extractall(MAIN)
    # The package README is a quick-start; the workspace README is the fuller project guide.
    (MAIN/'PACKAGE_README.md').write_bytes((MAIN/'README.md').read_bytes())
    (MAIN/'README.md').write_text('# Assignment 2 project\n\n**Live visualizations:** '+URL+'\n\n'+(MAIN/'WORKSPACE_README.md').read_text(encoding='utf-8'),encoding='utf-8')
    for path in (ROOT/'web').iterdir():
        if path.is_file() and (path.suffix in {'.js','.css'} or path.name in {'index.html','network.html','treemap.html'}):copy(path.relative_to(ROOT))
    copy('web/vendor/d3.v7.min.js')
    for name in ['data/infovis_countries.json','data/country_network_2020.json','data/treemap_countries_2020.json','data/network_all_pair_similarities.csv','output/pdf/DAS732_A2_Report_IEEE.pdf']:
        copy(name)
    for path in (ROOT/'output/pcp_changes').iterdir():
        if path.is_file() and path.suffix in {'.html','.js'}:copy(path.relative_to(ROOT))
    for name in ['scivis_contour.gif','scivis_global.gif','scivis_local.gif']:copy('images/scivis/'+name)
    # The network methods page links directly to its figures and evidence tables.
    for path in (ROOT/'output/network_revision').iterdir():
        if path.is_file() and path.suffix in {'.html','.png','.csv','.json'}:copy(path.relative_to(ROOT))
    figures=json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    assert [f['figure'] for f in figures]==list(range(1,33))
    cards=[]
    for f in figures:
        n=f['figure'];copy(f'images/report/Fig{n}.png')
        q,enc,why,note,take=f['explanation']
        paragraphs=[('Question',q),('How to read',enc),('Why this chart',why),('Interpretation',f['detailed_interpretation']),('Takeaway',take)]
        content=''.join(f'<p><strong>{html.escape(label)}.</strong> {html.escape(value).replace(chr(10),"<br>")}</p>' for label,value in paragraphs)
        cards.append(f'<article id="fig{n}"><h2>Figure {n}: {html.escape(f["title"])}</h2><a href="images/report/Fig{n}.png"><img loading="lazy" src="images/report/Fig{n}.png" alt="{html.escape(f["title"],quote=True)}"></a>{content}</article>')
    style='''body{margin:0;background:#f1f5f8;color:#19344b;font:16px/1.6 system-ui,sans-serif}main{max-width:1150px;margin:auto;padding:32px 22px 65px}h1,h2,h3{line-height:1.2}h1{font-size:clamp(2rem,5vw,3.4rem)}a{color:#126e85}article,.card{background:#fff;border:1px solid #d5e1e7;border-radius:14px;padding:24px;margin:20px 0;box-shadow:0 3px 15px #203b4b0d}article img{width:100%;height:auto}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}.cards .card{margin:0}.tag{font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;font-weight:700;color:#147d80}.button{display:inline-block;background:#126e85;color:#fff;border-radius:7px;padding:10px 16px;text-decoration:none;margin-right:9px}small{color:#526a78}'''
    (SITE/'site.css').write_text(style,encoding='utf-8')
    home='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Beyond Averages and Snapshots | Assignment 2</title><link rel="stylesheet" href="site.css"></head><body><main><header><p class="tag">DAS732 · Assignment 2 · Team Plot Twist</p><h1>Beyond Averages and Snapshots</h1><p>What do averages and snapshots hide about inequality, relationships and change over time?</p><p>Explore country internet indicators and daily US weather through interactive visualizations, 32 explained figures and three animations.</p><p><a class="button" href="output/pdf/DAS732_A2_Report_IEEE.pdf">Read the report</a> <a href="figures.html">Explore all 32 figures →</a></p></header><h2>Explore the interactive visualizations</h2><div class="cards"><div class="card"><p class="tag">Country relationships</p><h3>Similarity network</h3><p>Compare three layouts, find a country and filter all 15,931 pairwise scores. The default displays the top 5%.</p><a href="web/network.html">Open the network →</a></div><div class="card"><p class="tag">Country profiles</p><h3>Parallel coordinates</h3><p>Compare four indicators; brush, reorder axes and adjust curve bundling.</p><a href="web/index.html">Explore country profiles →</a></div><div class="card"><p class="tag">Country change</p><h3>Paired changes</h3><p>Follow each country's changes from 2015 to 2020 across four measures.</p><a href="output/pcp_changes/index.html">Explore the changes →</a></div><div class="card"><p class="tag">Country hierarchy</p><h3>Zoomable treemap</h3><p>Switch grouping hierarchies and examine country internet-user counts and adoption rates.</p><a href="web/treemap.html">Open the treemap →</a></div></div><h2>Weather animations</h2><p>Each animation shows eight uniformly spaced dates. Full-period analyses use all 92 days.</p><div class="cards"><div class="card"><h3>Fixed color scale</h3><a href="images/scivis/scivis_global.gif">View animation →</a></div><div class="card"><h3>Daily color scale</h3><a href="images/scivis/scivis_local.gif">View animation →</a></div><div class="card"><h3>Temperature contours</h3><a href="images/scivis/scivis_contour.gif">View animation →</a></div></div><h2>Methods and evidence</h2><p>Read the <a href="output/network_revision/index.html">similarity threshold and method review</a>, or inspect the <a href="figures.html">figure-by-figure explanations</a>. Country indicators and weather are separate investigations. The network edges describe similarity, not physical connections.</p><small>Parikshith Aithal K V · Sindhoor Ganapathi Hegde · Varshith M Gowda</small></main></body></html>'''
    (SITE/'index.html').write_text(home,encoding='utf-8')
    (SITE/'figures.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>32 explained figures</title><link rel="stylesheet" href="site.css"></head><body><main><p><a href="index.html">← Project home</a></p><h1>32 figures and their interpretations</h1><p>Click any figure to see it at full resolution. The report contains the complete analysis.</p>'+''.join(cards)+'</main></body></html>',encoding='utf-8')
    (SITE/'.nojekyll').write_text('',encoding='utf-8')
    (SITE/'README.md').write_text('# Assignment 2 public visualization site\n\nThis static site presents the report, browser visualizations, figure gallery and weather animations. The complete assignment source and reproducibility materials are maintained separately.\n',encoding='utf-8')
    missing=[];checked=0
    for page in SITE.rglob('*.html'):
        for link in re.findall(r'(?:href|src)=["\']([^"\']+)',page.read_text(encoding='utf-8')):
            if link.startswith(('http:','https:','#','mailto:','data:')):continue
            ref=link.split('#')[0].split('?')[0]
            if not ref:continue
            checked+=1
            if not (page.parent/ref).is_file():missing.append((str(page.relative_to(SITE)),ref))
    assert not missing,missing
    print(json.dumps(dict(private_files=sum(1 for p in MAIN.rglob('*') if p.is_file()),site_files=sum(1 for p in SITE.rglob('*') if p.is_file()),site_bytes=sum(p.stat().st_size for p in SITE.rglob('*') if p.is_file()),local_links_checked=checked,site=str(SITE),private=str(MAIN)),indent=2))

if __name__=='__main__':main()
