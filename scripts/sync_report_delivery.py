"""Sync numbered figures, annotated gallery and reproducibility README."""
from pathlib import Path
import html,json,shutil
import pymupdf
R=Path(__file__).resolve().parents[1]

def main():
    figures=json.loads((R/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    out=R/'images/report';out.mkdir(exist_ok=True)
    cards=[]
    for f in figures:
        n=f['figure'];shutil.copy2(R/f['path'],out/f'Fig{n}.png')
        svg=(R/f['path']).with_suffix('.svg')
        if svg.exists():shutil.copy2(svg,out/f'Fig{n}.svg')
        elif (out/f'Fig{n}.svg').exists():(out/f'Fig{n}.svg').unlink()
        fields=[('How to read',f['explanation'][1]),('Why this chart',f['explanation'][2]),('Interpretation',f['detailed_interpretation']),('Takeaway',f['explanation'][4])]
        links=' | '.join('<a href="'+html.escape(x['url'],quote=True)+'">'+html.escape(x['label'])+'</a>' for x in f.get('live_links',[]))
        cards.append(f'<article id="fig{n}"><h2>Figure {n}. {html.escape(f["title"])}</h2><a href="../../{f["path"]}"><img loading="lazy" src="../../{f["path"]}"></a><p>{links}</p>'+''.join('<h3>'+a+'</h3><p>'+html.escape(b).replace('\n\n','</p><p>')+'</p>' for a,b in fields)+'</article>')
    extras=json.loads((R/'data/supplementary_figure_manifest.json').read_text(encoding='utf-8'))
    cards.append('<h2>Supplementary analyses</h2><p>These include historical versions; numbered figures above match the current report.</p>')
    for f in extras:
        if (R/f['path']).is_file():cards.append(f'<p><a href="../../{f["path"]}">{html.escape(f.get("title",f["path"]))}</a></p>')
    (R/'output/quality_figures/index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Current A2 report figures</title><style>body{font:16px Arial;max-width:1250px;margin:36px auto;color:#17384e;background:#f0f4f7}article{background:white;padding:28px;margin:25px 0}img{width:100%;height:auto}p{line-height:1.6}h3{margin-bottom:5px}</style><h1>Current report: full-resolution figures</h1><p>Blue links open demonstrations, animations or figure readings.</p>'+''.join(cards)+'</html>',encoding='utf-8')
    pages=len(pymupdf.open(R/'output/pdf/DAS732_A2_Report_IEEE.pdf'))
    text=(R/'scripts/README.template.md').read_text(encoding='utf-8').replace('{{PAGE_COUNT}}',str(pages))
    (R/'README.md').write_text(text,encoding='utf-8')
    if (R/'WORKSPACE_README.md').exists():(R/'WORKSPACE_README.md').write_text(text,encoding='utf-8')
    p=R/'data/report_selection.json';selection=json.loads(p.read_text(encoding='utf-8'))
    selection.update(date='2026-10-31',note='32 retained figures; expanded preprocessing, professor-attributed threshold guidance with team-selected P95, centered dashboard link, per-figure destinations and inference-led takeaways.')
    p.write_text(json.dumps(selection,indent=2),encoding='utf-8')
    print(f'Synced {len(figures)} figures, explanations and detailed README; {pages} pages.')

if __name__=='__main__':main()
