"""Package the report, apps, source extracts and cached numerical reproduction inputs."""
from pathlib import Path
import json
import re
import zipfile
import pymupdf as fitz
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'output/DAS732_A2_Report_and_JavaScript.zip'


def main():
    files=set()
    def add(p):
        p=Path(p)
        assert p.is_file(),p
        files.add(p)
    for name in ['run_visualizations.py','START_VISUALIZATIONS.cmd','REPORT.md','FIGURE_EXPLANATIONS.md','PRESENTATION_PLAN.md','data/proposed_three_part_split.json',
                 'data/supplementary_figure_manifest.json','data/report_selection.json','data/current_figure_manifest.json','data/report_figure_explanations.json',
                 'data/country_network_2020.json','data/infovis_countries.json','data/treemap_countries_2020.json',
                 'data/network_matrix_order.csv','output/pdf/DAS732_A2_Report_IEEE.pdf',
                 'data/internet_panel_2000_2020.csv','archive/before_story_revision/current_figure_manifest.json',
                 'archive/before_final_research/DAS732_A2_Report_IEEE.pdf',
                 'output/quality_figures/index.html','output/story_report_validation.json','output/approved_replacements_validation.json',
                 'output/final_research_validation.json','output/quality_numerical_validation.json','research/FULL_LECTURE_GRAPH_PLAN.md','research/QUANTILE_REPLACEMENT.md','research/FINAL_SELECTION_RATIONALE.md','research/INTERNET_REVIEW_20261024.md','research/INTERNET_PLOT_REVIEW.md','research/BEYOND_SLIDES_PLOT_REVIEW.md',
                 'REPORT_CHANGE_REVIEW.md','archive/before_story_revision/DAS732_A2_Report_IEEE.pdf',
                 'output/layout_revision_validation.json']:
        add(ROOT/name)
    for folder in ['output/additional_evidence','output/network_revision','output/pcp_changes','web','output/lecture_previews','output/report_changes','output/research_candidates','output/internet_research','output/final_research','output/internet_revision','output/simple_revision','output/internet_review_20261024','output/video_presentation','output/infovis_audit_20261026']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and (p.suffix!='.pptx' or p.name=='DAS732_A2_Video_Presentation_Final.pptx'): add(p)
    # Include original country extracts, derived inputs and current weather caches
    # so the documented preprocessing and numerical pipeline is portable.
    for folder in ['data','images']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p.suffix!='.npy': add(p)
    for name in ['fig7_association_values.csv','fig10_country_cohorts.csv','fig10_cohort_summary.csv','rubric_preview_validation.json','REPLACEMENT_RECOMMENDATION.md']:
        add(ROOT/'output/proposals_20261026'/name)
    add(ROOT/'requirements.txt')
    add(ROOT/'scripts/README.template.md')
    for p in (ROOT/'scripts').iterdir():
        if p.is_file() and p.suffix in {'.py','.mjs'}: add(p)
    add(ROOT/'README.md')
    add(ROOT/'output/report_editorial_validation.json')
    add(ROOT/'docs/interactions.html')
    add(ROOT/'docs/site.css')
    for p in (ROOT/'docs/images/gui').glob('*.png'):add(p)
    for p in (ROOT/'images/scivis').glob('*.gif'):add(p)
    manifest=json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    for f in manifest+json.loads((ROOT/'data/supplementary_figure_manifest.json').read_text()):
        p=ROOT/f['path'];add(p)
        if p.with_suffix('.svg').exists():add(p.with_suffix('.svg'))
    for f in json.loads((ROOT/'output/report_changes/changes.json').read_text(encoding='utf-8')):
        add(ROOT/f['path'])
    for p in [ROOT/'report_latex/DAS732_A2_Report.tex',ROOT/'report_latex/design_reference_preamble.tex',ROOT/'report_latex/README.md',
              *[ROOT/f'report_latex/figures/Fig{n}.png' for n in range(1,len(manifest)+1)]]:add(p)
    # Explicit source list remains a useful required-entry check in addition to
    # the complete script directory included above.
    for name in ['update_animation_script.py','build_recording_script_pdf.py','prepare_video_materials.py','render_video_weather.py','build_video_presentation.mjs','finalize_video_materials.py','build_three_part_plan.py','research_internet_candidates.py','research_plot_candidates.py','final_research_figures.py','verify_final_research.py','build_quantile_change.py','build_story_report.py','build_latex_report.py','figure_explanations.py',
                 'preview_lecture_extensions.py','build_infovis_data.py','prepare_infovis.py',
                 'build_temporal_figures.py','build_scivis.py','build_extended_figures.py',
                 'build_quality_figures.py','verify_quality_figures.py','verify_story_report.py',
                 'package_selected_report.py','build_report_change_review.py','check_layout_revision.py',
                 'render_story_report.py']:
        add(ROOT/'scripts'/name)
    readme='''# A2 selected report and interactive JavaScript package

Extract this ZIP to a folder. Open output/pdf/DAS732_A2_Report_IEEE.pdf for the
PAGECOUNT-page illustrated report (32 figures, with supporting checks in the companion gallery).

To run the browser visualizations, double-click START_VISUALIZATIONS.cmd on Windows,
or run `python run_visualizations.py` with Python 3. The launcher opens at
http://127.0.0.1:8765/web/home.html. Keep the server process running.
The browser app uses only the Python standard library server, local JavaScript,
vendored D3 v7 and the supplied JSON files; it needs no CDN or Python data packages.

Required JavaScript: web/app.js (parallel coordinates), web/treemap.js (zoomable
treemap), web/network.js (network explorer). See web/README.md for controls and the
interaction instructions. The PDF is static; the working pages and three GIFs
are separate evidence. On October 26, the browser audit exercised all three network
layouts, search/filtering, PCP bundling, pointer brushing, axis reordering, treemap
zoom/back and both hierarchies. Results are in output/infovis_audit_20261026/.

The editable LaTeX report and all 32 numbered PNGs are in report_latex/.
Compile DAS732_A2_Report.tex twice with pdfLaTeX. The gallery uses original
full-resolution images, with detailed readings, under output/quality_figures/.

The team's required video materials are in output/video_presentation/.
The current deck and script retain the same network default and numerical findings;
the latest report adds method-sensitivity diagnostics in output/network_revision/.
The human narration and final video still need recording.

To recreate numerical results, install requirements.txt, then run
`python -X utf8 scripts/reproduce_results.py` from the extracted folder.
Raw country extracts, the regional lookup, preprocessing source/audit and current
gridMET NPZ caches are included. The country builders use data/processed/,
prepared by scripts/preprocess_data.py, without needing an external A1 folder.
The cache-backed numerical pipeline does not need a network connection; absent
weather caches can be retrieved with --download-weather. PDF compilation requires
pdfLaTeX on PATH. Exact stages and processing rules are in WORKSPACE_README.md.
Browser screenshots remain supplied artifacts; recapture them with
node scripts/audit_infovis_interactions.mjs when Playwright and Edge are configured.
See web/README.md for the view states. Presentation regeneration requires its separate Node artifact-tool
runtime; the numerical/report command does not rebuild the slide deck.

The prior-figure comparison gallery is at output/report_changes/index.html.
All omitted/replaced original plots and the previous PDF are supplied.

The report now includes the adopted three-person responsibility allocation in the
A1 contribution-table format. Each member has a distinct Infovis and SciVis task.
Actual implementation completion and individual AI disclosures require verification.
'''.replace('PAGECOUNT',str(len(fitz.open(ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf'))))
    with zipfile.ZipFile(TARGET,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('README.md',(ROOT/'README.md').read_text(encoding='utf-8'))
        z.writestr('PACKAGE_README.md',readme)
        for p in sorted(files):
            z.write(p,'WORKSPACE_README.md' if p==ROOT/'README.md' else p.relative_to(ROOT).as_posix())
    # Verify all runtime HTML paths resolve within the actual ZIP.
    with zipfile.ZipFile(TARGET) as z:
        names=set(z.namelist());checked=0
        import posixpath
        for name in ['web/home.html','web/index.html','web/network.html','web/treemap.html',
                     'output/network_revision/index.html','output/quality_figures/index.html','output/lecture_previews/index.html','output/report_changes/index.html','output/internet_research/index.html','output/research_candidates/index.html']:
            text=z.read(name).decode('utf-8')
            for ref in re.findall(r'(?:href|src)="([^"]+)"',text):
                if ref.startswith(('http:','https:','#')):continue
                target=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(ref.split('#')[0])))
                assert target in names,(name,target)
                checked+=1
    result=dict(archive=str(TARGET.relative_to(ROOT)),files=len(files)+2,
                runtime_links_checked=checked,bytes=TARGET.stat().st_size,
                scope='report, LaTeX source, figures, GIFs, runnable JavaScript, raw country extracts, preprocessing and current weather caches')
    (ROOT/'output/package_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
