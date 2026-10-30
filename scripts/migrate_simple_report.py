"""Apply the approved report structure changes to the report generator."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'scripts/build_story_report.py';s=p.read_text(encoding='utf-8')
s=s.replace('def compose_report():\n','def compose_report():\n    import sys\n    from simple_report_content import configure, apply as simplify\n    from build_simple_figures import build as build_simple\n    configure(sys.modules[__name__])\n    build_simple()\n',1)
s=s.replace("    assert len(figures)==30", "    figures=simplify(figures)\n    assert len(figures)==30",1)
s=s.replace("[extension('adoption_alluvial'),extension('nodetrix'),extension('adoption_quantile_change')]", "[extension('adoption_alluvial'),extension('nodetrix'),extension('group_profiles'),extension('adoption_quantile_change'),extension('inequality_lenses'),extension('weather_upset'),old[27]]")
s=s.replace("('Detailed interpretation',f['detailed_interpretation']),('Limits',limits)","('What it shows',f['detailed_interpretation']),('Note',limits)")
s=s.replace("('Interpretation',f['detailed_interpretation']),('Limits',f['explanation'][3])", "('What it shows',f['detailed_interpretation']),('Note',f['explanation'][3])")
a=s.index("                    '## Conclusion\\n\\nThe central question")
b=s.index("        parts.append('## '+title",a)
s=s[:a]+"                    '## Conclusion\\n\\n'+CONCLUSION+'\\n']\n"+s[b:]
a=s.index("    abstract=r'''\\begin{abstract}")
b=s.index("\\end{abstract}",a)+len('\\end{abstract}')
s=s[:a]+"    abstract=r'''\\begin{abstract}\nAverages can hide differences between countries and places. A single date can hide how a result developed. We examine these problems using country internet data and, separately, daily weather data. Network layouts, NodeTrix, parallel coordinates, treemaps, horizons and ridgelines show different parts of the country data. Color, contour and wind experiments show how drawing choices affect weather comparisons. Complete daily records reveal rainfall bursts, shared conditions and long runs that monthly summaries miss. Each result is explained using its values, units and included observations.\n\\end{abstract}"+s[b:]
a=s.index("           r'''\\begin{table*}[!t]")
b=s.index("    report_ids=",a)
s=s[:a]+"           ]\n"+s[b:]
a=s.index("    for i in range(len(parts)):")
b=s.index("    index=0",a)
s=s[:a]+s[b:]
a=s.index("                      r'\\section{Conclusion}',paragraph(")
b=s.index("                      r'\\section{Companion material}'",a)
s=s[:a]+"                      r'\\section{Conclusion}',paragraph(CONCLUSION),\n"+s[b:]
s=s.replace("        else: parts += [r'\\section{'+escape(title)+'}',paragraph(lead)]", "        else: parts += [r'\\FloatBarrier',r'\\section{'+escape(title)+'}',paragraph(lead)]")
s=s.replace("r'\\section{Data, transformations and comparison design}'", "r'\\section{Data and preparation}'")
s=s.replace("r'\\section{JavaScript implementation and interaction evidence}'", "r'\\section{Interactive browser views}'")
s=s.replace("'## Data, transformations and comparison design", "'## Data and preparation")
s=s.replace("'## JavaScript implementation and required interaction evidence", "'## Interactive browser views")
s=s.replace("'## Reproducibility, artifacts and contribution status", "'## Code and supporting files")
s=s.replace("r'\\section{Reproducibility, artifacts and contribution status}'", "r'\\section{Code and supporting files}'")
s=s.replace("            for label,value in [('How to read the graph',enc),('What it shows',f['detailed_interpretation']),('Note',limits)]:", "            for label,value in [('Reading the plot',enc),('What it shows',f['detailed_interpretation']),('Note',limits)]:")
s=s.replace("r'\\FloatBarrier',r'\\nocite{quantiles}',r'\\begin{thebibliography}{99}'", "r'\\FloatBarrier',r'\\begin{thebibliography}{9}'")
a=s.index('    # All references listed must also be cited')
b=s.index("    filename='DAS732_A2_Report.tex'",a)
s=s[:a]+'''    tex=tex.replace(paragraph(DATA),paragraph(DATA)+r'\\cite{owid,gridmet,lectures}.'+'\\n\\n',1)
    tex=tex.replace(paragraph(JS),paragraph(JS)+r'\\cite{d3,bundling}.'+'\\n\\n',1)
    for n,cite in [(3,'nodetrix'),(11,'variance'),(13,'horizon'),(19,'contour')]:
        label=r'\\label{fig:'+str(n)+'}'
        pos=tex.index(label)
        start=tex.rfind(r'\\caption{',0,pos);end=tex.index('}\\n',start)
        tex=tex[:end]+r' \\cite{'+cite+'}'+tex[end:]
'''+s[b:]
# Report figure headings do not need a second copy of the question.
s=s.replace("            parts += [r'\\subsection{'+escape(f['title'].rstrip('.'))+'}',\n                      r'\\noindent\\textit{Question (Fig.~\\ref{fig:'+str(n)+'}).} '+inline(q)+'\\n\\n']", "            parts += [r'\\subsection{'+escape(f['title'].rstrip('.'))+'}',r'\\noindent\\textit{Figure '+str(n)+'.} '+inline(q)+'\\n\\n']")
# Clear, short contribution text without the temporary disclosure paragraph.
s=s.replace("Following the A1 member-and-contribution format, responsibilities are allocated as follows. ","The following table lists each member’s assigned work. ")
s=s.replace("The allocation does not certify unconfirmed completed work.\\n\\n", "\\n\\n")
s=s.replace("Following the A1 format, the table records the adopted responsibility allocation, rather than certifying unconfirmed completed work. ", "The table lists each member’s assigned work. ")
s=s.replace("Three-person task allocation follows the A1 contribution-table format; completed work requires individual verification.", "The team’s task allocation is listed at the end.")
p.write_text(s,encoding='utf-8')
print('Report structure migrated')
