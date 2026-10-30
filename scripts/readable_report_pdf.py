"""Place figures beside their explanations, without floating them across pages."""
from pathlib import Path
import re,shutil,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'report_latex'
PAGES=[[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[13],[14,15],[16],[17],[18],[19,20],[21,22],[23],[24,25],[26,27],[28,29],[30]]

def write(figures,m):
    from build_latex_report import PREAMBLE,inline,escape
    from simple_report_content import CONCLUSION
    import pymupdf
    from PIL import Image
    OUT.mkdir(exist_ok=True);(OUT/'figures').mkdir(exist_ok=True)
    pre=PREAMBLE
    pre=re.sub(r'\\title\{Connectivity Profiles.*?\\author\{',lambda match:
        r'\title{Beyond Averages and Snapshots\\{\large Country Internet Use and Daily Weather}\\[3pt]'
        r'{\normalsize Team Plot Twist \textbullet{} DAS732 Data Visualization, Term 1 (2026-27)}\\'
        r'{\normalsize Programming Assignment 2 \textbullet{} gridMET: July-September 2023}}'+'\n'+r'\author{',pre,flags=re.S)
    pre=pre.replace(r'\begin{document}',r'\setlength{\parindent}{0pt}'+'\n'+r'\begin{document}')
    pre=pre.replace(r'\maketitle',r'\maketitle'+'\n'+r'\pagestyle{plain}\thispagestyle{plain}')
    pre=pre.replace('Connectivity Profiles and Weather Fields: Assignment 2','Beyond Averages and Snapshots: Assignment 2')
    abstract='Averages can hide differences between countries and places. A single date can hide how a result developed. We study these problems using country internet data and, separately, daily weather data. Network, multivariable and time-based views show different parts of the country data. Color, contour and wind experiments show how drawing choices affect weather comparisons. Complete daily records reveal rainfall bursts, shared conditions and long runs that monthly summaries miss.'
    parts=[pre,r'\begin{abstract}'+escape(abstract)+r'\end{abstract}',
      r'\section{Introduction}',m.paragraph(m.INTRO),r'\section{Data and preparation}',m.paragraph(m.DATA)+r'\cite{owid,gridmet,lectures}.',
      r'\section{Interactive browser views}',m.paragraph(m.JS)+r'\cite{d3,bundling}.',r'\clearpage\onecolumn']
    sections={}
    i=1
    for title,ids,lead in m.SECTIONS:
        for _ in ids:sections[i]=title;i+=1
    cites={3:'nodetrix',11:'variance',13:'horizon',19:'contour'}
    # Tall, multi-panel figures get their own page; wide comparisons share a page.
    for page_no,group in enumerate(PAGES):
        if page_no:parts.append(r'\clearpage')
        title=sections[group[0]]
        parts += [r'{\small\color{accent}\textbf{'+escape(title)+r'}}\par\smallskip']
        for j,n in enumerate(group):
            f=figures[n-1];target=OUT/'figures'/f'Fig{n}.png'
            shutil.copy2(ROOT/f['path'],target)
            q,enc,why,note,take=f['explanation']
            # Preserve all original pixels; size is limited without cropping evidence.
            with Image.open(target) as im:ratio=im.height/im.width
            maxheight=.63 if len(group)==1 else .305
            if n==2 and len(group)>1:maxheight=.32
            if n==1 and len(group)>1:maxheight=.24
            caption=escape(f['title'].rstrip('.'))+'.'+(r' \cite{'+cites[n]+'}' if n in cites else '')
            parts += [r'\begin{minipage}{\textwidth}\centering',
              rf'\includegraphics[width=.98\textwidth,height={maxheight}\textheight,keepaspectratio]{{Fig{n}.png}}',
              r'\widecaption{'+caption+'}{fig:'+str(n)+'}',r'\vspace{2pt}',
              r'\begin{minipage}[t]{.48\textwidth}\small\raggedright',
              r'\textbf{Reading the plot.} '+inline(enc)+r'\par\smallskip',
              r'\textit{Note.} '+inline(note),r'\end{minipage}\hfill',
              r'\begin{minipage}[t]{.48\textwidth}\small\raggedright',
              r'\textbf{What it shows.} '+inline(f['detailed_interpretation'])+r'\par\smallskip',
              r'\textbf{Main point.} '+inline(take),r'\end{minipage}',r'\end{minipage}']
            if j<len(group)-1:parts.append(r'\par\vspace{10pt}')
    parts += [r'\clearpage\twocolumn',r'\section{Discussion}',m.paragraph(m.DISCUSSION),
      r'\section{Code and supporting files}',m.paragraph(m.REPRO),m.contributions_latex(),
      r'\section{Conclusion}',m.paragraph(CONCLUSION),r'\begin{thebibliography}{9}']
    for key,value in m.REFERENCES:
        match=re.search(r'https?://\S+',value)
        text=escape(value[:match.start()].strip())+r' \url{'+match[0]+'}.' if match else escape(value)
        parts.append(r'\bibitem{'+key+'} '+text)
    parts += [r'\end{thebibliography}',r'\end{document}']
    tex='\n'.join(parts)
    def breakable(match):return ' '.join(r'\path{'+token+'}' for token in match[1].replace(r'\_','_').split(' '))
    tex=re.sub(r'\\texttt\{([^{}]*)\}',breakable,tex)
    (OUT/'DAS732_A2_Report.tex').write_text(tex,encoding='utf-8')
    engine=shutil.which('pdflatex');assert engine,'pdfLaTeX required'
    for i in range(2):
        result=subprocess.run([engine,'-interaction=nonstopmode','-halt-on-error','DAS732_A2_Report.tex'],cwd=OUT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (OUT/f'compile_pass_{i+1}.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
        if result.returncode:raise RuntimeError(result.stdout[-3500:])
    shutil.copy2(OUT/'DAS732_A2_Report.pdf',ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf')
    pages=len(pymupdf.open(OUT/'DAS732_A2_Report.pdf'))
    (OUT/'README.md').write_text(f'# A2 report source\n\n{pages} pages, 30 figure sets and nine references. Compile DAS732_A2_Report.tex twice with pdfLaTeX. The figure pages place each explanation beside its figure; they do not use floating images. Full-resolution numbered PNGs are in figures/.\n',encoding='utf-8')
    with zipfile.ZipFile(ROOT/'output/DAS732_A2_LaTeX_Source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in [OUT/'DAS732_A2_Report.tex',OUT/'README.md',*[OUT/'figures'/f'Fig{n}.png' for n in range(1,31)]]:z.write(p,p.relative_to(OUT))
    print(f'Built readable report: {pages} pages, 30 figure sets, nine references')
