"""Build the integrated 32-figure, cited report from stable analysis IDs."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,zipfile
import pymupdf
from build_latex_report import inline,escape
import simple_report_content as content
import build_story_report as story
import report_review_refinements as revision
import approved_report_replacements as approved
import network_threshold_revision as network
import report_editorial_revision as editorial
import report_structure_revision as structure

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'report_latex'

def digest(paths):return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def paragraph(text):
    result=story.paragraph(text)
    return re.sub(r'\[(\d+(?:,\d+)*)\]',lambda m:r'\cite{'+','.join('ref'+x for x in m[1].split(','))+'}',result)

def live_latex(f):
    return r'{\footnotesize '+r' \quad | \quad '.join(r'\href{'+x['url'].replace('#',r'\#')+r'}{\textcolor{accent}{\underline{'+escape(x['label'])+r'}}}' for x in f['live_links'])+r'}'

def block(f):
    n=f['figure'];q,enc,why,note,take=f['explanation']
    links=' | '.join('['+x['label']+']('+x['url']+')' for x in f['live_links'])
    return f'### Figure {n}. {f["title"]}\n\n![Figure {n}]({f["path"]})\n\n**Question.** {q}\n\n**Encoding.** {enc}\n\n**Why this chart.** {why}\n\n**What it shows.** {f["detailed_interpretation"]}\n\n**Takeaway.** {take}\n\n{links}\n'

def contributions(text):
    return text.replace('Discussion/Limitations','Discussion').replace('Figs. 1-3, 17-18, 20-23, 25.','Figs. 1-3, 6, 12, 18-19, 21-23.').replace('Figs. 10-16, 19, 24, 30.','Figs. 11, 13-17, 20, 25-26, 31-32.').replace('Figs. 4-9, 26-29.','Figs. 4-5, 7-10, 24, 27-30.')

def build():
    from build_a1_style_report import WHY,MORE,CAPTIONS,CONCLUSION
    from build_additional_evidence import entries
    figures=structure.normalize(json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8')))
    extras=entries()
    for f in extras:f['analysis_id']=f['figure']
    assets=[ROOT/f['path'] for f in figures+extras]
    before=digest(assets)
    protected=[p for p in (ROOT/'output/video_presentation').rglob('*') if p.is_file()]
    video_before=digest(protected)
    content.configure(story)
    for f in figures:
        aid=f['figure'];title,q,enc,finding,note,take=content.COPY[aid]
        f.update(title=title+'.',caption=CAPTIONS[aid],explanation=[q,enc,WHY[aid],note,take],detailed_interpretation=finding+'\n\n'+MORE[aid])
    revision.refine(figures,WHY,MORE,CAPTIONS)
    approved.apply(figures,WHY,MORE,CAPTIONS)
    network.apply(figures,content)
    editorial.apply(figures,content);editorial.apply(extras)
    figures=structure.arrange(figures+extras,editorial)
    by={f['analysis_id']:f for f in figures}
    pre=(OUT/'design_reference_preamble.tex').read_text(encoding='utf-8')
    parts=[pre,r'\begin{abstract}'+escape(editorial.ABSTRACT)+r'\end{abstract}',r'\begin{IEEEkeywords}country internet use, visual comparison, temporal change, daily weather, multivariable visualization\end{IEEEkeywords}',r'\section{Introduction}',paragraph(structure.remap(editorial.INTRO)),r'\section{Data and preparation}',paragraph(structure.remap(content.DATA)),r'\subsection{Tools, interaction and implementation evidence}',paragraph(content.JS)]
    md=['# Beyond Averages and Snapshots\n\nConnectivity Profiles and Daily Weather | Team Plot Twist | DAS732 Assignment 2','[Live dashboard]('+editorial.BASE+')','## Abstract\n\n'+editorial.ABSTRACT,'## Introduction\n\n'+structure.remap(editorial.INTRO),'## Data and preparation\n\n'+structure.remap(content.DATA),'### Tools, interaction and evidence\n\n'+content.JS]
    guide=[]
    for section,ids,lead in structure.SECTIONS:
        parts += [r'\section{'+escape(section)+'}',paragraph(lead)]
        md += ['## '+section+'\n\n'+lead]
        for aid in ids:
            f=by[aid];n=f['figure'];q,enc,why,note,take=f['explanation']
            shutil.copy2(ROOT/f['path'],OUT/'figures'/f'Fig{n}.png')
            height={1:.62,2:.48,5:.49,6:.62,7:.49,10:.54,19:.58,22:.47,26:.47,28:.62,31:.28,32:.25}.get(aid,.49)
            env='figure' if aid in {14,15} else 'figure*'
            width=r'\columnwidth' if aid in {14,15} else r'\textwidth'
            if aid in {14,15}:height=.42
            caption=f['caption'] if aid==1 else f['title']
            parts += [r'\subsection{'+escape(f['title'].rstrip('.'))+'}',r'\noindent\textit{Question (Fig.~\ref{fig:'+str(n)+r'}).} '+inline(q),r'\begin{'+env+r'}[!tb]\centering',rf'\includegraphics[width={width},height={height}\textheight,keepaspectratio]{{Fig{n}.png}}',r'\caption{'+escape(caption)+' '+live_latex(f)+r'}\label{fig:'+str(n)+'}',r'\end{'+env+'}',r'\noindent\textit{How to read the graph.} '+inline(enc),r'\noindent\textit{Why this chart.} '+inline(why),r'\noindent\textit{Detailed interpretation.} '+paragraph(f['detailed_interpretation']),r'\takeaway{'+inline(take)+'}']
            md.append(block(f));guide.append(block(f))
        if ids[-1] in {16,32}:parts.append(r'\FloatBarrier')
    allocation=contributions(story.contributions_latex()).replace(r'\begin{table}[!ht]\centering\footnotesize',r'\par\smallskip\noindent{\footnotesize').replace(r'\end{tabularx}\end{table}',r'\end{tabularx}}\par\smallskip')
    discussion=structure.remap(editorial.DISCUSSION)
    parts += [r'\section{Discussion}',paragraph(discussion),r'\section{Code and supporting files}',paragraph(editorial.REPRO),allocation,r'\section{Conclusion}',paragraph(CONCLUSION),r'\begin{thebibliography}{10}']
    for i,(citation,url) in enumerate(structure.REFERENCES,1):parts.append(r'\bibitem{ref'+str(i)+'} '+escape(citation)+' '+r'\href{'+url+r'}{Online source}.')
    parts += [r'\end{thebibliography}',r'\end{document}']
    tex='\n\n'.join(parts)
    tex=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:' '.join(r'\path{'+t+'}' for t in m[1].replace(r'\_','_').split()),tex)
    (OUT/'DAS732_A2_Report.tex').write_text(tex,encoding='utf-8')
    for i in range(2):
        r=subprocess.run([shutil.which('pdflatex'),'-interaction=nonstopmode','-halt-on-error','DAS732_A2_Report.tex'],cwd=OUT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (OUT/f'compile_pass_{i+1}.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
        if r.returncode:raise RuntimeError(r.stdout[-4000:])
    target=ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf';shutil.copy2(OUT/'DAS732_A2_Report.pdf',target)
    pages=len(pymupdf.open(target))
    md += ['## Discussion\n\n'+discussion,'## Code and supporting files\n\n'+editorial.REPRO,contributions(story.contributions_markdown()),'## Conclusion\n\n'+CONCLUSION,'## References']
    md += [f'{i}. {citation} [Online source]({url}).' for i,(citation,url) in enumerate(structure.REFERENCES,1)]
    (ROOT/'REPORT.md').write_text('\n\n'.join(md),encoding='utf-8')
    (ROOT/'FIGURE_EXPLANATIONS.md').write_text('# Figure explanations\n\n'+'\n\n'.join(guide),encoding='utf-8')
    (ROOT/'data/current_figure_manifest.json').write_text(json.dumps(figures,indent=2),encoding='utf-8')
    (ROOT/'data/report_figure_explanations.json').write_text(json.dumps([dict(figure=f['figure'],analysis_id=f['analysis_id'],title=f['title'],question=f['explanation'][0],encoding=f['explanation'][1],rationale=f['explanation'][2],detailed_interpretation=f['detailed_interpretation'],takeaway=f['explanation'][4],live_links=f['live_links']) for f in figures],indent=2),encoding='utf-8')
    (OUT/'README.md').write_text(f'# Report source\n\n{pages} pages and 32 integrated figure sets, followed by 10 references. All original analyses are retained; the near-equal-adoption comparison is Figure 6 and the daily calendar is Figure 32 within the persistence section. Compile DAS732_A2_Report.tex twice with pdfLaTeX, or run python scripts/build_a1_style_report.py from the repository root.\n',encoding='utf-8')
    with zipfile.ZipFile(ROOT/'output/DAS732_A2_LaTeX_Source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in [OUT/'DAS732_A2_Report.tex',OUT/'design_reference_preamble.tex',OUT/'README.md',*[OUT/'figures'/f'Fig{n}.png' for n in range(1,33)]]:z.write(p,p.relative_to(OUT))
    assert before==digest(assets),'Report builder changed chart measurements/assets'
    assert video_before==digest(protected),'Report builder changed recording materials'
    validation=dict(pages=pages,figures=32,style_reference='ass2_1.pdf',source_plot_assets_unchanged=True,slides_video_unchanged=True,reading_guide_count=tex.count(r'\textit{How to read the graph.}'),rationale_count=tex.count(r'\textit{Why this chart.}'),takeaways=tex.count(r'\takeaway{'),references=len(structure.REFERENCES),analysis_order=structure.ORDER,extra_plots_integrated=True)
    (ROOT/'data/a1_style_report_validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
    print(json.dumps(validation,indent=2))
