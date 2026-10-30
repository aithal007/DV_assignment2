"""Build the A2 IEEE LaTeX report using A1's formatting and current A2 results.

Run from any directory with Python and MiKTeX/pdflatex installed. The portable
source bundle contains the .tex file, all numbered figures, and build instructions.
"""
from pathlib import Path
import json
import re
import shutil
import subprocess
import zipfile
from PIL import Image
from figure_explanations import EXPLANATIONS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report_latex"


def escape(s):
    substitutions = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "°": r"\textdegree{}", "→": r"$\rightarrow$", "−": "-", "–": "-", "—": "-", "θ": r"$\theta$", "α": r"$\alpha$", "’": "'", "‘": "'", "“": "``", "”": "''", "…": "...", "\u200b": ""}
    return "".join(substitutions.get(c, c) for c in s)


def inline(s):
    tokens = []
    def save(value):
        tokens.append(value)
        return f"ZZTOKEN{len(tokens)-1}ZZ"
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", lambda m: save(r"\href{" + m[2].replace("%", r"\%") + "}{" + escape(m[1]) + "}"), s)
    s = re.sub(r"`([^`]+)`", lambda m: save(r"\texttt{" + escape(m[1]) + "}"), s)
    s = re.sub(r"\*\*([^*]+)\*\*", lambda m: save(r"\textbf{" + escape(m[1]) + "}"), s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", lambda m: save(r"\emph{" + escape(m[1]) + "}"), s)
    s = escape(s)
    s = re.sub(r"Figures? (\d+)", lambda m: r"Fig.~\ref{fig:" + m[1] + "}", s)
    for i, token in enumerate(tokens):
        s = s.replace(f"ZZTOKEN{i}ZZ", token)
    return s


PREAMBLE = r"""\documentclass[conference,a4paper]{IEEEtran}
\IEEEoverridecommandlockouts
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx,textcomp}
\usepackage[table]{xcolor}
\usepackage{booktabs,tabularx,array}
\usepackage{placeins,stfloats,microtype,url}
\usepackage[hidelinks]{hyperref}
\hypersetup{pdftitle={Connectivity Profiles and Weather Fields: Assignment 2},
pdfauthor={Parikshith Aithal K V, Sindhoor Ganapathi Hegde, Varshith M Gowda}}
\graphicspath{{figures/}}
\extrafloats{100}
\renewcommand{\topfraction}{0.95}
\renewcommand{\dbltopfraction}{0.95}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.7}
\renewcommand{\dblfloatpagefraction}{0.7}
\setcounter{totalnumber}{5}
\setcounter{dbltopnumber}{3}
\definecolor{accent}{HTML}{2A78D6}
\definecolor{accentbg}{HTML}{EEF4FC}
\newcommand{\takeaway}[1]{\par\smallskip\noindent\fcolorbox{accent}{accentbg}{%
\parbox{\dimexpr\columnwidth-2\fboxsep-2\fboxrule\relax}{\small\textbf{Takeaway.} #1}}\par\medskip}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\makeatletter
\newcommand{\widecaption}[2]{\begingroup\def\@captype{figure}\caption{#1}\label{#2}\endgroup}
\makeatother

\begin{document}
\raggedbottom
\title{Connectivity Profiles and Weather Fields\\
{\large A Comparative Study of Infovis and SciVis Methods}\\[3pt]
{\normalsize Team Plot Twist \textbullet{} DAS732 Data Visualization, Term 1 (2026-27)}\\
{\normalsize Programming Assignment 2 \textbullet{} gridMET: July-September 2023}\\[3pt]
{\small\color{accent}32-figure review edition: final selection and actual task ownership pending}}
\author{
\IEEEauthorblockN{Parikshith Aithal K V}
\IEEEauthorblockA{Roll No. BT2024249\\IIIT Bangalore}
\and
\IEEEauthorblockN{Sindhoor Ganapathi Hegde}
\IEEEauthorblockA{Roll No. BT2024014\\IIIT Bangalore}
\and
\IEEEauthorblockN{Varshith M Gowda}
\IEEEauthorblockA{Roll No. BT2024227\\IIIT Bangalore}}
\maketitle
"""

INTRO = r"""
\section{Introduction}
Visualization choices affect which patterns are visible and whether comparisons remain
valid. This report studies those choices on two distinct data domains: country-level
connectivity indicators from Assignment 1, and spatially sampled daily gridMET weather
fields for July-September 2023. These domains are analyzed separately; no relationship
between the weather and connectivity datasets is asserted.

\subsection{Questions and experimental design}
The Infovis investigation asks which countries have similar connectivity profiles,
where included internet users are concentrated, and how adoption distributions changed.
The SciVis investigation asks how color normalization, contour spacing, and vector
sampling affect interpretation of the same fields. Each comparison holds its input
field or country set fixed while changing a stated visual parameter.
The six work packages follow the required assignment methods~\cite{brief}.

\begin{table*}[!t]
\centering\footnotesize
\caption{Required work packages and controlled experiments. Ownership is recorded separately.}
\label{tab:tasks}
\begin{tabularx}{\textwidth}{@{}p{2.4cm}YYp{1.2cm}@{}}
\toprule
\textbf{Work package} & \textbf{Question and methods} & \textbf{What is held fixed / what changes} & \textbf{Figures}\\
\midrule
Infovis 1: network & Derived country-profile similarity; spring, spectral and circular layouts; interactive inspection. & Same 179 nodes and 590 edges; layout and filtering change. & 1-2\\
Infovis 2: browser methods & Bundled parallel coordinates and zoomable treemaps. & Matched country panel and axes for profiles; same leaf counts across hierarchy remodelings. & 3-6\\
Infovis 3: temporal methods & Horizon plots and ridgelines, each in two variations. & Fixed 159-country panel; country/region grouping and distribution faceting change. & 7-10\\
SciVis 1: color & Continuous/discrete palettes, linear/log rain, global/local extrema, scalar animations. & Same date/field within comparisons; palette, discretization and normalization change. & 11-13, 16\\
SciVis 2: contours & Marching Squares family, lines/fills, 5/10 degree intervals, animation. & Same temperature field; interval and filling change. & 14\\
SciVis 3: vectors & Quiver density and speed-proportional/equal-length vectors. & Same wind field, map extent, speed colors and scale within each row; arrow sampling changes. & 15\\
\bottomrule
\end{tabularx}
\end{table*}

\subsection{Reading the results}
Layouts preserve edges, hierarchy changes preserve leaf counts, and color limits
preserve weather values. Bundling exposes supplied groups. All findings are
restricted to documented coverage and sampling.

"""

TAKEAWAYS = {
    "Infovis 1": "Layout changes visual neighborhoods, not the measured network. Selection and the edge list are needed to verify an apparent group.",
    "Infovis 2a": "Region bundling makes supplied groups easier to follow; exact values remain at axis intercepts. Subscriptions are not unique people.",
    "Infovis 2b": "User count and adoption percentage answer different questions. Remodeling the hierarchy changes the question while preserving the leaves.",
    "Infovis 3": "A rising median coexists with persistent regional inequality. Fixed membership and explained baselines keep these comparisons interpretable.",
    "SciVis": "Shared temperature limits support cross-date comparisons; logarithmic rain mapping supports weak-positive-rain inspection. Neither rescaling nor interpolation creates new observations.",
}


def main():
    if (ROOT/'data/report_selection.json').exists():
        from build_story_report import build
        build()
        return
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    source = (ROOT / "REPORT.md").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "data/scivis/manifest.json").read_text())
    findings = json.loads((ROOT / "data/scivis/findings_2023.json").read_text())
    assert manifest["start"] == "2023-07-01" and manifest["end"] == "2023-09-30"
    images = re.findall(r"!\[Figure (\d+)\. ([^\]]+)\]\(([^)]+)\)", source)
    figure_ids = list(range(1, len(images) + 1))
    assert [int(n) for n, _, _ in images] == figure_ids
    current = json.loads((ROOT / 'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    assert [f['figure'] for f in current] == figure_ids
    current_by_number = {f['figure']: f for f in current}
    for n, _, path in images:
        shutil.copy2(ROOT / path, OUT / "figures" / f"Fig{n}.png")
        if int(n) in {3,4}:
            # Paper view: retain the measured axes and complete region legend,
            # removing the browser navigation and unused screenshot margins.
            with Image.open(ROOT / path) as screenshot:
                screenshot.crop((210,405,1390,1030)).save(OUT / "figures" / f"Fig{n}.png")
    abstract = rf"""\begin{{abstract}}
We compare six visualization work packages using country connectivity indicators and
gridMET fields from eight uniformly spaced days in July-September 2023. A derived
2020 similarity graph has 179 countries and 590 edges; layout comparisons and
interactive inspection distinguish graph structure from drawing effects. Parallel
coordinates use 175 matched countries, treemaps preserve 184 leaf countries across
two hierarchies, and horizon/ridgeline plots retain a fixed 159-country temporal panel.
Scientific visualizations compare scalar palettes and global/local extrema,
line/filled contours at two spacings, and three quiver densities with two length
encodings. Seven revised analytical figures examine four-measure country profiles,
matched changes, joint weather fields, daily time-space structure, hot-dry persistence
and complete-month temperature differences. All daily analyses use 92 observations
on a fixed spatial footprint. Coverage, masks, units, sampling and scale choices are
documented alongside {len(images)} figure sets and three eight-frame animations.
\end{{abstract}}
\begin{{IEEEkeywords}}
scientific visualization, information visualization, gridMET, color mapping,
Marching Squares, quiver, parallel coordinates, treemap
\end{{IEEEkeywords}}
"""
    task_table = re.search(r"\\begin\{table\*\}.*?\\end\{table\*\}", INTRO, re.S).group()
    intro_without_table = INTRO.replace(task_table, "")
    parts = [PREAMBLE, abstract, intro_without_table, task_table]
    explanation_manifest = []
    sections = re.split(r"(?m)^## ", source)[1:]
    citations = {"Questions": "gridmet", "Infovis 1": "networkx", "Infovis 2a": "bundling", "Infovis 2b": "d3", "Infovis 3": "horizon", "SciVis": "gridmet,color,contour,quiver", "Extended weather": "gridmet,hovmoller,lectures", "Extended Infovis": "networkx,horizon,lectures", "Multivariable country": "relational,wilke", "Multivariable weather": "gridmet,quiver", "Supporting method": "horizon,lectures"}
    for section in sections:
        heading, _, content = section.partition("\n")
        if heading.startswith(("References", "Reproducibility")):
            continue
        paragraphs = re.split(r"\n\s*\n", content.strip())
        chunks = []
        prose = []
        i = 0
        while i < len(paragraphs):
            paragraph = paragraphs[i].strip()
            image_match = re.fullmatch(r"!\[Figure (\d+)\. ([^\]]+)\]\(([^)]+)\)", paragraph)
            if image_match:
                n, title, _ = image_match.groups()
                details = ""
                if i + 1 < len(paragraphs) and paragraphs[i+1].startswith(f"**Figure {n}.**"):
                    details = paragraphs[i+1].split("**", 2)[2].strip()
                    i += 1
                chunks.append({"n": n, "title": title, "details": details, "before": prose})
                prose = []
            elif paragraph.startswith(('**Detailed interpretation.**', '**Main takeaway.**')):
                pass  # Structured explanations below keep these beside their figure.
            elif paragraph:
                prose.append(" ".join(paragraph.splitlines()))
            i += 1
        cite = next((value for key, value in citations.items() if heading.startswith(key)), "brief")
        if not chunks:
            parts.append(r"\section{" + ("Data and preprocessing" if heading.startswith('Questions') else inline(heading)) + "}\n")
            parts.append(r"\noindent\textit{Method sources:} \cite{" + cite + "}.\n\n")
            prose = ["The SciVis variables are tmmx (K converted to °C), pr (daily mm), vs (10-m speed, m/s), and th (clockwise-from-north wind from-direction). Eight uniform dates span July 1-September 30, 2023 (Fig. 11). Missing cells remain masked; gridMET days use Mountain Standard Time." if p.startswith("The SciVis input") else p for p in prose]
            for p in prose:
                if p.startswith('**Part '):
                    title,_,rest=p.partition('.** ')
                    parts.append(r'\subsection{' + inline(title.removeprefix('**')) + '}\n' + inline(rest) + '\n\n')
                else:
                    parts.append(inline(p) + '\n\n')
            continue
        # Normal IEEE floats preserve the continuous two-column text flow.
        # Dense comparisons require two columns to retain their labels.
        wide_figures = {f['figure'] for f in current if f['wide']}
        parts.append(r"\section{" + inline(heading) + "}\n")
        parts.append(r"\noindent\textit{Method sources:} \cite{" + cite + "}.\n\n")
        for chunk in chunks:
            n = int(chunk["n"])
            question, encoding, rationale, guidance, takeaway = EXPLANATIONS[n]
            parts.extend(inline(p) + "\n\n" for p in chunk["before"])
            parts.append(r"\subsection{" + inline(chunk["title"].rstrip(".")) + "}\n")
            parts.append(r"\noindent\textit{Question (Fig.~\ref{fig:" + str(n) + "}).} " + inline(question) + "\n\n")
            env = "figure*" if n in wide_figures else "figure"
            width = r"\textwidth" if n in wide_figures else r"\columnwidth"
            height = "0.82" if n in {11,28,29} else "0.65" if '/quality/' in current_by_number[n]['path'] else "0.54" if n in wide_figures else "0.43"
            parts.append(r"\begin{" + env + "}[!tb]\n" + r"\centering" + "\n" +
                         rf"\includegraphics[width={width},height={height}\textheight,keepaspectratio]{{Fig{n}.png}}" + "\n" +
                         r"\caption{" + inline(chunk["title"].rstrip(".")) + ".}" + "\n" +
                         r"\label{fig:" + str(n) + "}\n" + r"\end{" + env + "}\n")
            parts.append(r"\noindent\textit{Encoding and how to read it.} " + inline(encoding) + "\n\n")
            parts.append(r"\noindent\textit{Why this chart.} " + inline(rationale) + "\n\n")
            parts.append(r"\noindent\textit{What it shows.} " + inline(chunk["details"]) + "\n\n")
            detailed = current_by_number[n].get('detailed_interpretation', '')
            parts.append(r"\noindent\textit{Detailed interpretation.} " + inline(detailed) + "\n\n")
            parts.append(r"\noindent\textit{Interpretation and limits.} " + inline(guidance) + "\n\n")
            parts.append(r"\takeaway{" + escape(takeaway) + "}\n")
            explanation_manifest.append({"figure":n,"title":chunk["title"],"question":question,
                "encoding":encoding,"rationale":rationale,"findings":chunk["details"],
                "interpretation":guidance,"detailed_interpretation":detailed,"takeaway":takeaway,"layout":env,
                "word_count":len(" ".join([question,encoding,rationale,chunk["details"],detailed,guidance,takeaway]).split())})
        parts.extend(inline(p) + "\n\n" for p in prose if not p.startswith(("**Normalization", "**Verified")))
    assert [x["figure"] for x in explanation_manifest] == figure_ids
    (ROOT / "data/report_figure_explanations.json").write_text(json.dumps(explanation_manifest,indent=2),encoding="utf-8")
    parts.append(r"""
\FloatBarrier
\section{Mathematical conventions and reproducibility}
\subsection{Normalization and vector conversion}
For scalar value $x$ in daily field $t$, the global and local mappings are
\begin{equation}
a_g=\frac{x-m_g}{M_g-m_g},\qquad
a_t=\frac{x-m_t}{M_t-m_t},
\end{equation}
where $m_g,M_g$ are extrema over all valid cells of the eight sampled fields and
$m_t,M_t$ are extrema for that sample day. Global means this sampled space-time cube,
not the entire Earth or all 92 days. Percentiles in the statistics CSV are descriptive
summaries and do not replace extrema in this experiment. Positive rain uses logarithmic
normalization; zero rain has a separate white encoding, and missing cells are gray.

For speed $s$ and a clockwise-from-north source direction $\theta$, the flow-to
components are
\begin{equation}
u=-s\sin\theta,\qquad v=-s\cos\theta.
\end{equation}
Thus a north wind flows south and an east wind flows west. Equal-length arrows use
$(u/s,v/s)$ for noncalm valid cells. Display bearings account for longitude scaling
by $1/\cos\phi$ at latitude $\phi$ and the map's aspect; arrow length retains
physical speed in the proportional row. Fixed sampling and scales separate direction,
density, and magnitude effects~\cite{quiver,wind}.

\subsection{Approximate area weighting}
For the difference of monthly means $\Delta T_i=\overline{T}_{i,\mathrm{Sep}}-\overline{T}_{i,\mathrm{Jul}}$,
we use common valid sampled cells and $w_i=\cos\phi_i$:
\begin{equation}
\overline{\Delta T}=\frac{\sum_i w_i\Delta T_i}{\sum_i w_i},\qquad
p_{\mathrm{cool}}=\frac{\sum_i w_i\mathbf{1}(\Delta T_i<0)}{\sum_i w_i}.
\end{equation}
These approximate regular latitude-longitude cell areas. They are not population
weights, and coarse subsampling still approximates the boundary footprint.

\subsection{Files and validation}
The Python builds preserve the compressed NPZ subset, annual source URLs, variable
names, day indices, packing metadata, the cache SHA-256, and global/daily limits.
Automatic checks verify eight distinct in-range dates, aligned array dimensions,
ordered coordinates, plausible physical ranges, nonnegative rain and speed,
valid direction ranges, cardinal wind conversions, extrema, and GIF frame counts.
The source grid has been read at every sixth cell: 0.25 degree display spacing is
subsampling, not spatial averaging and not the native grid resolution.

The browser visualizations use vendored D3 and a local HTTP server. The report's
numbered full-resolution figures are supplied as \texttt{figures/Fig1.png} through
\texttt{figures/Fig32.png}. The original SVG exports and three animations remain in
\texttt{images/scivis/}. The LaTeX PDF is static; animations are assessed from the
separate GIF files. Reproduction commands are listed in the project README and in
the portable LaTeX bundle's build instructions.

\section{Discussion and limitations}
The Infovis comparisons show that regional distinctions depend on how the question
is encoded: proximity in a similarity graph, axis values in a multivariate profile,
area in a hierarchy, and folded bands or densities in a temporal distribution. The
same country can have many mobile subscriptions and comparatively low adoption;
subscriptions per 100 people must not be interpreted as ownership percentages.
Fixed panels prevent membership changes from masquerading as change, but exclude
countries with incomplete observations. Country-weighted distributions describe a
typical included country, not a typical person.

The SciVis experiments illustrate complementary reading tasks. Fixed scalar scales
support between-date comparisons; local scales support within-date contrast.
Fine contours reveal boundaries while coarse contours reduce clutter. Equal-length
vectors expose direction in weaker winds while moving magnitude to color. Eight
uniform dates avoid selecting only visually striking days, but cannot establish
event duration, monthly precipitation totals, seasonal means, or climate trends.
gridMET's wind inputs are coarser than its output grid; apparent fine detail is not
evidence of terrain-scale wind resolution~\cite{gridmet}.

\takeaway{The defensible result is a documented comparison of methods and sampled
patterns. A stronger visual impression is not evidence that the underlying values,
coverage, or temporal resolution have improved.}

\section{Individual contributions}
The names and roll numbers below are carried over from the Assignment 1 report.
Assignment 2 requires each member to own one distinct SciVis task and one distinct
Infovis task. The present workspace does not establish those assignments, so they
must be recorded from the team's actual work before submission; the table makes
no completed-task ownership claim.
\begin{table*}[!tb]
\centering\footnotesize
\caption{Team details from Assignment 1; actual Assignment 2 ownership remains to be completed.}
\begin{tabularx}{\textwidth}{@{}p{3.5cm}p{1.9cm}YY@{}}
\toprule
\textbf{Member} & \textbf{Roll number} & \textbf{SciVis task} & \textbf{Infovis task / specific contribution}\\
\midrule
Parikshith Aithal K V & BT2024249 & To be completed & To be completed\\
Sindhoor Ganapathi Hegde & BT2024014 & To be completed & To be completed\\
Varshith M Gowda & BT2024227 & To be completed & To be completed\\
\bottomrule
\end{tabularx}
\end{table*}

\section{Conclusion}
The required Infovis and SciVis comparisons are represented by 32 numbered figure
sets, interactive browser views and three eight-frame scalar animations. The
report documents the country panels, supplied July-September 2023 interval,
missing-data treatment, units, sampling and scale conventions. The complete-month weather
differences, compound-event summaries and connectivity comparisons are descriptive, restricted to their
respective data coverage. Final submission requires verified individual contributions
and the accompanying code, figures and animations.
\FloatBarrier

\IEEEtriggeratref{7}
\begin{thebibliography}{12}
\bibitem{brief} DAS732, ``Programming Assignment 2: Familiarization with SciVis and Infovis methods,'' IIIT Bangalore, Term 1, 2026-27. Supplied assignment brief.
\bibitem{gridmet} Climatology Lab, ``gridMET: data, methods, updates and limitations.'' \url{https://www.climatologylab.org/gridmet.html}.
\bibitem{networkx} NetworkX, ``Spring, spectral and circular layouts.'' \url{https://networkx.org/documentation/stable/reference/drawing.html}.
\bibitem{bundling} J. Heinrich et al., ``Evaluation of a bundling technique for parallel coordinates,'' 2011. \url{https://arxiv.org/abs/1109.6073}.
\bibitem{d3} D3, ``Treemap: hierarchical layouts.'' \url{https://d3js.org/d3-hierarchy/treemap}.
\bibitem{horizon} J. Heer, N. Kong and M. Agrawala, ``Sizing the horizon: the effects of chart size and layering on the graphical perception of time series visualizations,'' CHI, 2009. \url{https://hci.stanford.edu/publications/2009/heer-horizon-chi09.pdf}.
\bibitem{color} Matplotlib, ``Choosing colormaps'' and ``Colormap normalization.'' \url{https://matplotlib.org/stable/users/explain/colors/colormaps.html}.
\bibitem{cividis} J. R. Nunez, C. R. Anderton and R. S. Renslow, ``Optimizing colormaps with consideration for color vision deficiency to enable accurate interpretation of scientific data,'' PLOS ONE, 13(7), 2018. \url{https://doi.org/10.1371/journal.pone.0199239}.
\bibitem{contour} ContourPy, ``Algorithm description.'' \url{https://contourpy.readthedocs.io/en/latest/description.html}.
\bibitem{quiver} Matplotlib, ``matplotlib.pyplot.quiver.'' \url{https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.quiver.html}.
\bibitem{wind} NCAR Earth Observing Laboratory, ``Wind direction quick reference.'' \url{https://www.eol.ucar.edu/content/wind-direction-quick-reference}.
\bibitem{lectures} DAS732 lecture slides supplied with the assignment: color mapping (August 18), contour mapping (August 27), vectors (September 1), network layouts (September 15), matrix exploration (September 17), multivariate visualization (September 22), data remodeling (September 24) and temporal visualization (September 29), 2026.
\bibitem{relational} Seaborn, ``Visualizing statistical relationships.'' \url{https://seaborn.pydata.org/tutorial/relational.html}.
\bibitem{wilke} C. O. Wilke, ``Visualizing associations among two or more quantitative variables,'' Fundamentals of Data Visualization. \url{https://clauswilke.com/dataviz/visualizing-associations.html}.
\bibitem{hovmoller} K. Goebbert, Unidata, ``Hovmoller Diagram Example.'' \url{https://unidata.github.io/python-gallery/examples/Hovmoller_Diagram.html}.
\end{thebibliography}
\end{document}
""")
    tex = "\n".join(parts)
    tex = tex.replace("The six work packages follow the required assignment methods", "The six required work packages and complementary analytical comparisons follow the assignment methods")
    tex = tex.replace("Eight\nuniform dates avoid selecting only visually striking days, but cannot establish\nevent duration, monthly precipitation totals, seasonal means, or climate trends.", "Eight\nuniform animation dates support the required sampled-field experiments. Separate\nanalyses use all 92 daily fields for complete-month means, rainfall totals, joint\nthreshold frequencies and within-window persistence. The original animation scales\nstill refer to only the eight sampled fields. This single interval cannot establish\na climate trend.")
    tex = tex.replace("32 numbered figure", f"{len(images)} numbered figure").replace('figures/Fig32.png', f'figures/Fig{len(images)}.png')
    tex = tex.replace("Temperature uses continuous viridis", r"Temperature uses continuous viridis~\cite{color,cividis}")
    filename = "DAS732_A2_Report.tex"
    (OUT / filename).write_text(tex, encoding="utf-8")
    engine = shutil.which("pdflatex")
    if not engine:
        raise RuntimeError("pdflatex not found; install MiKTeX or TeX Live to compile the saved source")
    for run in range(2):
        result = subprocess.run([engine, "-interaction=nonstopmode", "-halt-on-error", filename], cwd=OUT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (OUT / f"compile_pass_{run+1}.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(result.stdout[-6000:] + result.stderr)
    pdf = ROOT / "output/pdf/DAS732_A2_Report_IEEE.pdf"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT / "DAS732_A2_Report.pdf", pdf)
    guide = """# Assignment 2 IEEE LaTeX report

This source follows Assignment 1's IEEEtran conference layout, blue takeaway boxes,
formal captions and references. All current numbered figure files are included.
Every figure has a question, encodings, design rationale, findings, interpretation
and its own main takeaway. Continuous IEEE two-column text uses normal figure and
figure* floats, with two-column figures reserved for dense comparisons.

Open DAS732_A2_Report.tex in Overleaf, MiKTeX or TeX Live. Preserve the figures folder.
Choose pdfLaTeX and compile twice to resolve references:

    pdflatex -interaction=nonstopmode -halt-on-error DAS732_A2_Report.tex
    pdflatex -interaction=nonstopmode -halt-on-error DAS732_A2_Report.tex

The author names/roll numbers are from Assignment 1. The contribution table must be
completed with actual Assignment 2 ownership before submission. No A1 cloud links
are reused for the new assignment.

The gridMET interval is July 1-September 30, 2023, with eight uniform samples.
The report contains the full A2 Infovis and SciVis analysis, not just weather plots.
GIFs and interactive browser implementations are supplied separately in the project.
The revised report keeps useful original figures and adds seven analytical views.
The eight-frame animations remain distinct from the full 92-day analysis.

The project generator is scripts/build_latex_report.py. It reads REPORT.md, scripts/figure_explanations.py and the
current data/scivis results; rerun it after changing those inputs. Direct .tex edits
are supported but are overwritten when the generator is rerun.
"""
    (OUT / "README.md").write_text(guide, encoding="utf-8")
    bundle = ROOT / "output/DAS732_A2_LaTeX_Source.zip"
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
        for path in [OUT / filename, OUT / "README.md", *[OUT / 'figures' / f'Fig{n}.png' for n in figure_ids]]:
            z.write(path, path.relative_to(OUT))
    print(f"PDF: {pdf}\nSource: {OUT / filename}\nPortable source: {bundle}")


if __name__ == "__main__":
    main()
