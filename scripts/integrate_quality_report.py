"""Recompose the reviewed report, keeping valuable original figures and all methods.

The preserved pre-revision report is the baseline; reruns are deterministic.
"""
from pathlib import Path
import html
import json
import re
import runpy
from quality_interpretations import DETAILS, PARTS

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'archive/before_quality_revision'
PATTERN=r'!\[Figure (\d+)\. ([^\]]+)\]\(([^)]+)\)\n\n\*\*Figure \d+\.\*\* ([^\n]+)'


def main():
    if (ROOT/'data/report_selection.json').exists():
        from build_story_report import compose_report
        compose_report()
        print('Selected story report and figure manifest regenerated.')
        return
    source=(BASE/'REPORT.md').read_text(encoding='utf-8')
    explanations=runpy.run_path(str(BASE/'scripts/figure_explanations.py'))['EXPLANATIONS']
    new={f['key']:f for f in json.loads((ROOT/'data/quality/figures.json').read_text())}
    old={int(m[1]):dict(number=int(m[1]),title=m[2],path=m[3],caption=m[4],explanation=explanations[int(m[1])]) for m in re.finditer(PATTERN,source)}
    # Keep method explanations as useful supporting evidence, outside the results.
    method_blocks=[]
    def prune(m):
        num=int(m[1])
        if num==17: return ''
        if num in [27,28]:
            method_blocks.append(m[0]); return ''
        if num in [16,22]:
            key={16:'monthly_temperature_change',22:'weather_hovmoller'}[num]
            f=new[key]
            old[num].update(f)
            return f'![Figure {num}. {f["title"]}](%s)\n\n**Figure {num}.** %s'%(f['path'],f['caption'])
        return m[0]
    source=re.sub(PATTERN,prune,source)
    def block(key,tempid):
        f=new[key]; old[tempid]=dict(f,number=tempid)
        return f'![Figure {tempid}. {f["title"]}]({f["path"]})\n\n**Figure {tempid}.** {f["caption"]}\n\n'
    added='## Multivariable country findings: profiles and changes\n\n'
    added+='The central country question continues Assignment 1: which infrastructure profiles accompany adoption, and do associations between levels also describe change? All three figures below use the identical 175-country matched panel.\n\n'
    for key,num in [('telecom_four_variables',101),('country_change_quadrants',102),('telecom_scatterplot_matrix',103)]: added+=block(key,num)
    added+='## Multivariable weather findings: co-occurrence and persistence\n\n'
    added+='The weather question is separate: where and when do heat, limited rainfall and wind patterns coincide, and how persistent are the joint conditions? The country and weather datasets are not joined and no causal connection between them is proposed.\n\n'
    for key,num in [('weather_four_fields',104),('compound_frequency_persistence',105)]: added+=block(key,num)
    added+='## Supporting method explanations and robustness\n\n'
    added+='These figures explain how to read the required methods and which features survive design choices. The horizon construction remains useful because it prevents confusing a negative baseline deviation with declining adoption; it is not presented as a new substantive country finding. The KDE check supports cautious interpretation of ridgeline peaks.\n\n'
    added+='\n\n'.join(method_blocks)+'\n\n'
    source=source.replace('## Reproducibility, limits, and submission actions',added+'## Reproducibility, limits, and submission actions')
    source=source.replace('**Draft for review, 5 October 2026.**','**32-figure review edition, 6 October 2026. Final selection pending.**')
    source=source.replace('## Extended Infovis analysis and method checks','## Extended Infovis analysis: structure and regional change')
    source=source.replace('## Questions and input data','## Questions and input data\n\n**Unifying question.** What do multivariable and time-aware visualizations reveal that single snapshots and averages hide? We investigate this through two separate datasets: country connectivity and daily weather.\n\n**Submission format.** Assignment 2 specification 1(f) says a video demo is not required. The report therefore contains the actual inferences; optional presentation guidance is in `PRESENTATION_PLAN.md`. The eight-frame scalar GIFs remain required animation evidence.\n\n')
    source=source.replace('These are weather snapshots, not all events during the interval.','These eight dates define the required animations and controlled sampled-field experiments. Separate analyses use all 92 daily fields, with 31 July, 31 August and 30 September observations.')
    source=source.replace('signed endpoint differences','signed differences of monthly means')
    source=source.replace('**Figure 16.**','**Figure 16.**',1)
    # Remove old prose assertions that described the superseded endpoint map.
    source=re.sub(r'Figure 16[^\n]*endpoint[^\n]*\n','',source)
    order=[int(m[1]) for m in re.finditer(PATTERN,source)]
    assert len(order)==32 and len(set(order))==32,order
    mapping={oldnum:i+1 for i,oldnum in enumerate(order)}
    def refs(text):
        return re.sub(r'\b(Figure|Fig\.) (\d+)\b',lambda m:f'{m[1]} {mapping.get(int(m[2]),int(m[2]))}',text)
    source=refs(source)
    part_text='## Proposed three-part contribution structure\n\n'
    part_text+='The figure IDs below remain the complete 32-figure review set. This is a proposed allocation for organizing and explaining the work, not a claim of completed individual authorship. Each person must own one distinct Infovis and one distinct SciVis work package. Final figure selection and actual contributions remain to be confirmed by the team.\n\n'
    for key,part in PARTS.items():
        ids=', '.join(str(n) for n in part['figures'])
        part_text+=f'**Part {key}: {part["title"]}.** Infovis responsibility: {part["infovis"]}. SciVis responsibility: {part["scivis"]}. Review figures: {ids}.\n\n'
    source=source.replace('## Infovis 1:',part_text+'## Infovis 1:',1)
    # Explicitly record the coverage fact in place of the removed calendar.
    source=source.replace('## Extended weather analysis: all 92 days','## Extended weather analysis: all 92 days\n\nAll 92 consecutive dates have valid daily fields: 31 in July, 31 in August and 30 in September. Eight uniformly spaced dates, 13 days apart, are used for animation. The coverage calendar is omitted because this sentence and `data/scivis/daily_coverage.csv` communicate its information.')
    source+='\n11. Seaborn, [Multivariable relational plots](https://seaborn.pydata.org/tutorial/relational.html).\n12. Claus Wilke, [Associations and paired comparisons](https://clauswilke.com/dataviz/visualizing-associations.html).\n13. Unidata, [Hovmoller diagram example](https://unidata.github.io/python-gallery/examples/Hovmoller_Diagram.html).\n'
    def explain(m):
        detail,takeaway=DETAILS[int(m[1])]
        return m[0]+f'\n\n**Detailed interpretation.** {detail}\n\n**Main takeaway.** {takeaway}'
    source=re.sub(PATTERN,explain,source)
    (ROOT/'REPORT.md').write_text(source,encoding='utf-8')
    manifest=[]
    for oldnum in order:
        item=old[oldnum].copy(); item['figure']=mapping[oldnum]; item['original_figure']=oldnum if oldnum<100 else None
        item['explanation']=[refs(x) for x in item['explanation']]
        item['caption']=refs(item['caption'])
        item['detailed_interpretation'],takeaway=DETAILS[item['figure']]
        item['explanation'][-1]=takeaway
        item['proposed_part']=next(k for k,part in PARTS.items() if item['figure'] in part['figures'])
        item['supporting']=oldnum in [27,28]
        item['wide']=oldnum in {1,3,4,7,10,11,12,13,14,15,16,18,19,20,21,22,24,27,28,101,102,103,104,105}
        manifest.append(item)
    (ROOT/'data/current_figure_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    explanation_md='# Figure reading guides: revised analytical report\n\n'
    for f in manifest:
        question,encoding,rationale,limits,takeaway=f['explanation']
        explanation_md+=f'## Figure {f["figure"]}: {f["title"]}\n\n'
        for title,value in [('Question',question),('Encoding and how to read it',encoding),('Why this chart',rationale),('What it shows',f['caption']),('Detailed interpretation',f['detailed_interpretation']),('Interpretation and limits',limits),('Main takeaway',takeaway)]:
            explanation_md+=f'**{title}.** {value}\n\n'
    (ROOT/'FIGURE_EXPLANATIONS.md').write_text(explanation_md,encoding='utf-8')
    gallery=ROOT/'output/quality_figures/index.html'; gallery.parent.mkdir(parents=True,exist_ok=True)
    cards=[]
    for f in manifest:
        newtag='New analytical figure' if '/quality/' in f['path'] else 'Retained useful figure'
        if f['supporting']: newtag='Supporting method explanation'
        cards.append(f'<article id="fig{f["figure"]}"><p class="tag">{newtag} · Proposed part {f["proposed_part"]}</p><h2>Figure {f["figure"]}. {html.escape(f["title"])}</h2><a href="../../{f["path"]}"><img loading="lazy" src="../../{f["path"]}" alt="{html.escape(f["title"])}"></a><p>{html.escape(f["caption"])}</p><p><strong>Detailed interpretation.</strong> {html.escape(f["detailed_interpretation"])}</p><p><strong>Main takeaway.</strong> {html.escape(f["explanation"][-1])}</p><details><summary>How to read this plot</summary><p>{html.escape(f["explanation"][1])}</p><p>{html.escape(f["explanation"][3])}</p></details></article>')
    toc=' '.join(f'<a href="#fig{f["figure"]}">{f["figure"]}</a>' for f in manifest)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>A2 | Revised analytical figures</title><style>body{font:17px/1.6 system-ui;color:#193044;background:#eef2f5;margin:0}main{max-width:1300px;margin:auto;padding:24px}header,article{background:white;padding:28px;margin:24px 0;border-radius:12px}img{width:100%;height:auto}a{color:#176e9d}nav a{display:inline-block;padding:5px 10px}.tag{color:#8b5524;font-weight:600}h1,h2{line-height:1.25}@media(max-width:600px){main{padding:8px}header,article{padding:14px}}</style><main><header><h1>What do snapshots and averages hide?</h1><p>32 figure sets: 30 results/experiments and 2 supporting method explanations. Seven new analytical figures; useful existing plots retained. The coverage calendar is omitted.</p><p><a href="../pdf/DAS732_A2_Report_IEEE.pdf">Revised IEEE report</a> · <a href="../../PRESENTATION_PLAN.md">Optional three-part presentation</a> · <a href="../../FIGURE_EXPLANATIONS.md">All reading guides</a></p><nav>'''+toc+'</nav></header>'+''.join(cards)+'</main></html>'
    gallery.write_text(page,encoding='utf-8')
    changes={'figure_count':len(manifest),'new_analytical_figures':7,'retained_original_figures':25,
        'omitted_from_report':[{'original_figure':17,'reason':'Coverage communicated in a sentence and CSV.'}],
        'replaced':[{'original_figure':16,'replacement':'Monthly means + weighted ECDF'}, {'original_figure':22,'replacement':'Daily paired Hovmoller diagrams'}],
        'supporting_methods':{'horizon_construction':31,'kde_sensitivity':32},
        'original_to_current':{str(k):v for k,v in mapping.items() if k<100}}
    (ROOT/'output/quality_revision_changes.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
    print(f'Integrated {len(manifest)} figures; revised gallery: {gallery}')


if __name__=='__main__': main()
