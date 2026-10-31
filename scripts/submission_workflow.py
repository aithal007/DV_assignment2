"""Local, archive-independent reproduction and verification of the submission."""
from pathlib import Path
import argparse,html,json,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
VERIFY=['verify_network_threshold.py','verify_final_research.py','verify_internet_revision.py',
        'verify_simple_figures.py','verify_story_report.py','verify_additional_evidence.py','verify_report_editorial.py']
STAGES={'data':['preprocess_data.py','prepare_infovis.py'],
        'figures':['build_infovis_data.py','build_temporal_figures.py','build_scivis.py','build_scivis_results.py','build_extended_figures.py','build_quality_figures.py','verify_quality_figures.py','preview_lecture_extensions.py','build_quantile_change.py','research_internet_candidates.py','research_plot_candidates.py','final_research_figures.py','preview_internet_review_20261024.py','build_internet_revision.py','build_simple_figures.py','build_approved_assets.py','network_threshold_revision.py','build_additional_evidence.py'],
        'report':['build_change_pcp.py','build_gentle_pcp.py','preview_rubric_replacements.py','review_plots.py','build_a1_style_report.py'],
        'verify':VERIFY+['verify_review_revision.py']}

def local_assets():
    """Refresh only local report copies, galleries and launch page; no publishing."""
    figures=json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    target=ROOT/'images/report';target.mkdir(parents=True,exist_ok=True)
    for f in figures:
        source=ROOT/f['path'];shutil.copy2(source,target/f'Fig{f["figure"]}.png')
        if source.with_suffix('.svg').is_file():shutil.copy2(source.with_suffix('.svg'),target/f'Fig{f["figure"]}.svg')
    shutil.copy2(ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf',ROOT/'DAS732_A2_Report.pdf')
    style='<style>body{font:16px/1.6 Arial;color:#16384a;max-width:1200px;margin:35px auto;padding:0 25px}article{border-top:1px solid #ccd7df;padding:25px 0}img{max-width:100%;height:auto}a{color:#08679a}h1,h2{line-height:1.2}</style>'
    def page(prefix):
        cards=[]
        for f in figures:
            fields=[('Question',f['explanation'][0]),('How to read',f['explanation'][1]),('Why this chart',f['explanation'][2]),('Interpretation',f['detailed_interpretation']),('Takeaway',f['explanation'][4])]
            links=[]
            for x in f['live_links']:
                local=x['url'].split('/DV_assignment2/',1)[-1]
                links.append(f'<a href="{prefix+html.escape(local,quote=True)}">{html.escape(x["label"])}</a>')
            cards.append(f'<article id="fig{f["figure"]}"><h2>Figure {f["figure"]}. {html.escape(f["title"])}</h2><a href="{prefix}images/report/Fig{f["figure"]}.png"><img loading="lazy" src="{prefix}images/report/Fig{f["figure"]}.png" alt="{html.escape(f["title"],quote=True)}"></a><p>'+ ' | '.join(links)+'</p>'+''.join('<p><strong>'+label+'.</strong> '+html.escape(text).replace('\n','<br>')+'</p>' for label,text in fields)+'</article>')
        from report_structure_revision import REFERENCES
        refs='<h2>References</h2><ol>'+''.join('<li>'+html.escape(citation)+' <a href="'+url+'">Source</a></li>' for citation,url in REFERENCES)+'</ol>'
        return '<!doctype html><html lang="en"><meta charset="utf-8"><title>32 explained report figures</title>'+style+f'<a href="{prefix}web/home.html">Project home</a><h1>All 32 report figures and interpretations</h1>'+''.join(cards)+refs+'</html>'
    (ROOT/'figures.html').write_text(page(''),encoding='utf-8')
    gallery=ROOT/'output/quality_figures/index.html';gallery.parent.mkdir(parents=True,exist_ok=True);gallery.write_text(page('../../'),encoding='utf-8')
    shots=[('network','Network: complete controls and Spring layout','network_spring.png'),('network-spectral','Network: Spectral layout','network_spectral.png'),('network-circular','Network: Circular layout','network_circular.png'),('pcp','Parallel coordinates: bundling controls','pcp_bundled.png'),('pcp-brush','Parallel coordinates: country selection','pcp_brush.png'),('changes','Paired changes and controls','pcp_changes.png'),('treemap','Treemap: region hierarchy','treemap_region.png'),('treemap-zoom','Treemap: zoomed region','treemap_zoom.png'),('treemap-adoption','Treemap: adoption hierarchy','treemap_adoption.png'),('treemap-partition','Treemap: slice-and-dice partition','treemap_slice_dice.png')]
    body=''.join(f'<article id="{aid}"><h2>{title}</h2><a href="images/gui/{name}"><img loading="lazy" src="images/gui/{name}" alt="{title}"></a></article>' for aid,title,name in shots if (ROOT/'images/gui'/name).is_file())
    (ROOT/'interactions.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Complete UI screenshots</title>'+style+'<a href="web/home.html">Project home</a><h1>Complete browser UI evidence</h1><p>Uncropped full-page captures. Controls were tested through the browser; the machine-readable receipt is output/infovis_audit_20261026/interactions.json.</p>'+body+'</html>',encoding='utf-8')
    home='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Beyond Averages and Snapshots</title>'''+style+'''<h1>Beyond Averages and Snapshots</h1><p>Team Plot Twist - DAS732 Assignment 2</p><p>What do averages and snapshots hide about inequality, relationships and change over time?</p><ul><li><a href="../DAS732_A2_Report.pdf">Read the full report</a></li><li><a href="../figures.html">32 high-resolution figures and interpretations</a></li><li><a href="network.html">Network: three layouts, threshold and node filtering</a></li><li><a href="index.html">Parallel coordinates: bundling, brushing and axis ordering</a></li><li><a href="../output/pcp_changes/index.html">Paired-change parallel coordinates</a></li><li><a href="treemap.html">Treemap: hierarchy, zoom and spatial partition</a></li><li><a href="../interactions.html">Complete UI screenshots</a></li></ul><h2>Eight-frame scalar animations</h2><ul><li><a href="../images/scivis/scivis_global.gif">Fixed temperature scale</a></li><li><a href="../images/scivis/scivis_local.gif">Daily temperature scale</a></li><li><a href="../images/scivis/scivis_contour.gif">Contour animation</a></li></ul><p><a href="../README.md">Implementation and reproduction instructions</a> | <a href="../REQUIREMENTS_CHECKLIST.md">Every assignment requirement</a></p></html>'''
    (ROOT/'web/home.html').write_text(home,encoding='utf-8')
    print('Refreshed local report, 32 numbered images, galleries and launcher.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['all','refresh',*STAGES],default='all')
    parser.add_argument('--download-weather',action='store_true')
    args=parser.parse_args()
    if args.stage=='refresh':local_assets();return
    for stage in STAGES if args.stage=='all' else [args.stage]:
        for script in STAGES[stage]:
            command=[sys.executable,'-X','utf8',str(ROOT/'scripts'/script)]
            if script=='preprocess_data.py' and args.download_weather:command.append('--download-weather')
            print(f'[{stage}] {script}',flush=True);subprocess.run(command,cwd=ROOT,check=True)
        if stage=='report':local_assets()
    print('Requested submission stages completed.')

if __name__=='__main__':main()
