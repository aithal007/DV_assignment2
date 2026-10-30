"""Update current handoff text to match the simplified report."""
from pathlib import Path
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
pages=len(pymupdf.open(ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf'))
p=ROOT/'README.md';s=p.read_text(encoding='utf-8');a=s.index('## Current report');b=s.index('### Where is the JavaScript?')
text=f'''## Current report and video materials: simple-English revision

**Main question:** What do averages and snapshots hide about inequality, relationships and change over time?

The report now has **{pages} pages, 30 figure sets and nine references**. The setup fits on the first page. Each figure stays beside its short reading guide and result. The implementation checklist table and temporary AI-disclosure paragraph have been removed. Important qualifications appear as short notes; the team will supply its own final AI disclosure.

- Figure 1 explains that a neighbor is joined by a line, even when the layout changes its distance on the page.
- Figure 3 combines a NodeTrix overview with an enlarged, labelled eight-country matrix.
- Figures 4–5 show the same six named countries with straight and bundled lines, using identical axis ranges.
- Figure 6 uses two larger scatterplots; the full scatterplot matrix remains supplementary.
- Figure 7 uses one clear regional bar comparison with counts.
- Figure 11 shows country variation within regions, replacing the absolute/relative inequality idea already used in A1. The old analysis remains supplementary.
- Figure 29 uses four simple bars in place of the UpSet layout.

[Current report](output/pdf/DAS732_A2_Report_IEEE.pdf) | [Selected figures and companion views](output/quality_figures/index.html) | [Presentation](output/video_presentation/DAS732_A2_Video_Presentation_Final.pptx) | [Recording guide](output/pdf/DAS732_A2_Recording_Script.pdf) | [Slide viewer](output/video_presentation/index.html)

The 17-scene recording plan remains 6:30 raw, with a planned 1.35x export of about 4:49. Slides, notes and recording instructions follow the revised figures. Actual voices and live browser footage still need recording. The browser's **Show selected lines only** option hides unselected paths. The complete 175-country view remains available.

Numerical checks cover the country counts, six selected profiles, all 64 cells in the enlarged matrix, the within-region variance split and weather frequencies recalculated from the daily grids. JavaScript syntax and assets are checked. Live pointer interactions remain a manual rehearsal step because no supported browser connection was available.

The previous version is preserved in `archive/before_simple_revision_20261024.zip`. Run `python -X utf8 scripts/reproduce_results.py` to rebuild the numerical/report outputs. See [the video plan](PRESENTATION_PLAN.md) and [change record](REPORT_CHANGE_REVIEW.md).

'''
p.write_text(s[:a]+text+s[b:],encoding='utf-8')
p=ROOT/'web/README.md';s=p.read_text(encoding='utf-8')
intro='''# Simple report views and the full interactive views

Figures 4–5 in the report show the same six named countries with ranges suited to that selection. They are redrawn from the country values using the browser's bundling rule. Full browser screenshots are retained as supporting implementation evidence. The browser contains all 175 matched countries; the focus button selects six. **Show selected lines only** hides the rest. Clear the brushes to restore the complete view. During recording, keep the selected count and names visible; use browser zoom if needed.

The report figures are under `output/simple_revision/`. Their CSVs and validation files give the values behind the drawings. Earlier reference screenshots are under `output/internet_revision/`; full control instructions follow below. The new selection-only control still needs a live pointer rehearsal before recording.

---

'''
if not s.startswith('# Simple report views'):p.write_text(intro+s,encoding='utf-8')
p=ROOT/'scripts/build_report_change_review.py';s=p.read_text(encoding='utf-8')
a=s.index("md[1]=");b=s.index('for f in old:',a)
s=s[:a]+'''md[1]=f'The report now has **{pages} pages, 30 figure sets and nine references**. The previous version is preserved in archive/before_simple_revision_20261024.zip.'
md[3]='- Figure 1 explains line membership versus layout distance.\\n- Figure 3 adds a NodeTrix overview and a labelled group-7 matrix.\\n- Figures 4–5 show six named country paths; Figure 6 uses two larger scatterplots.\\n- Figure 7 replaces the crowded regional scatterplots with a bar comparison.\\n- Figure 11 replaces the A1-like absolute/relative comparison with within-region country variation.\\n- Figure 29 replaces UpSet with four simple bars.\\n- The setup is reduced to one page; Table 1 and the temporary AI paragraph are removed. Notes are short and the English is simpler.\\n- Fixed figure blocks keep each image with its explanation. The 17-slide deck and recording guide use the same revised story.'
md[5]='The report uses short reading guides, results and essential notes. Required method variants remain. Earlier plots are retained in the companion gallery. The team will add its final AI disclosure. Nine key data/method references remain.'
'''+s[b:]
s=s.replace('October 24 selection: country trajectories (Figure 2), focused browser comparisons (Figures 4–5 and 8–9), milestone timing (Figure 10), inequality (Figure 11) and regional gains (Figure 12).','Simple-English revision: NodeTrix detail (Figure 3), six-country paths (Figures 4–5), regional change counts (Figure 7), within-region variation (Figure 11) and weather overlap bars (Figure 29).')
p.write_text(s,encoding='utf-8')
p=ROOT/'scripts/check_layout_revision.py';s=p.read_text(encoding='utf-8');a=s.index("    change='");b=s.index("',\n    limitation",a)
s=s[:a]+"    change='Simple-English revision: compact setup, adjacent figure explanations, nine references, labelled NodeTrix detail, six-country PCPs, simple regional change bars, within-region spread and weather overlap bars."+s[b:];p.write_text(s,encoding='utf-8')
print('Current README and change records updated')
