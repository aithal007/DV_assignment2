"""One-time migration of existing build sources to the revised narrative."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def edit(file,pairs):
    p=ROOT/file;s=p.read_text(encoding='utf-8')
    for a,b in pairs:s=s.replace(a,b)
    p.write_text(s,encoding='utf-8')
edit('scripts/build_story_report.py',[
('The two report screenshots show different zoom subsets; their displayed totals are not an equal-population comparison.','The two report screenshots compare the same root total; the companion Asia drilldown has its own labeled subtotal. Nested country tiles retain adoption color within neutral group headers.'),
('Set bundling to 0% and then 50%; exact axis intercepts stay fixed.','Set bundling to 0% and then 50%; exact axis intercepts stay fixed. Click Inspect high adoption / low broadband to reproduce the six-country selection, then clear it.'),
('Denominators differ because required variables differ, and are not interchangeable.','The illustrative trajectory figure retains six named countries with all 11 annual adoption/broadband pairs in 2010-2020. Denominators differ because required variables differ, and are not interchangeable.'),
('NodeTrix/profile interpretation','country trajectory/profile interpretation'),
('parallel coordinates, treemap, NodeTrix, set intersections','parallel coordinates, treemap, country trajectories, set intersections'),
('NodeTrix, profiles, quantiles, intersections and monthly wind roses retained.','Country trajectories and milestone panels replace NodeTrix and the quantile comparison in the main report. Both prior analyses remain companion material. Required browser and temporal methods are upgraded.'),
("r'\\FloatBarrier',r'\\begin{thebibliography}{99}'","r'\\FloatBarrier',r'\\nocite{quantiles}',r'\\begin{thebibliography}{99}'"),
])
edit('scripts/build_internet_revision.py',[
('Root rectangles are groups, so they use neutral color; area is user count.','Group headers are neutral and nested country rectangles use adoption color; area is user count.'),
('The adoption color legend applies only after zooming to country leaves.','The adoption color legend applies to country tiles, including the nested leaf overview; it never encodes a group average.'),
('country-level colors.','country-level details.'),
('beneath the neutral root.','beneath the root grouping.'),
])
edit('scripts/final_research_figures.py',[
('The quantile comparison establishes an absolute endpoint contrast.','The milestone comparison establishes broad but uneven progress.'),
])
edit('scripts/reproduce_results.py',[
("'final_research_figures.py']","'final_research_figures.py','preview_internet_review_20261024.py','build_internet_revision.py','capture_internet_revision.py']"),
])
edit('scripts/build_three_part_plan.py',[
('NodeTrix and profile interpretation.','country trajectories and profile interpretation.'),
('Adoption quantiles and matched-country gains.','Adoption milestone timing.'),
('Figures 10-12 answer the inequality question','Figures 10-12 connect milestone timing to inequality and gains'),
])
edit('scripts/build_recording_script_pdf.py',[
('Recording guide - separate from the 27-page analytical report','Recording guide - companion to the analytical report'),
])
edit('scripts/package_selected_report.py',[
("'output/final_research','output/video_presentation'","'output/final_research','output/internet_revision','output/internet_review_20261024','output/video_presentation'"),
("'research/INTERNET_PLOT_REVIEW.md'","'research/INTERNET_REVIEW_20261024.md','research/INTERNET_PLOT_REVIEW.md'"),
])
print('Narrative and reproduction sources synchronized')
