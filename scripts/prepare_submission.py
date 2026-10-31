"""Assemble a clean local assessment folder; never publishes or uses GitHub."""
from pathlib import Path
import argparse,ast,hashlib,importlib.metadata,json,platform,shutil,subprocess,sys
from submission_workflow import STAGES
import assignment_requirements

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,default=ROOT.parent/'DAS732_A2_Submission')
    parser.add_argument('--resume',action='store_true',help='Resume this assembly after an interrupted copy')
    args=parser.parse_args();dest=args.destination.resolve()
    if dest.exists() and not args.resume:raise FileExistsError(f'Refusing to overwrite existing folder: {dest}')
    dest.mkdir(parents=True,exist_ok=True)
    def copy(rel):
        source=ROOT/rel;target=dest/rel
        if not source.is_file():raise FileNotFoundError(source)
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    for rel in ['run_visualizations.py','START_VISUALIZATIONS.cmd','requirements.txt','REPORT.md','FIGURE_EXPLANATIONS.md','report_latex/DAS732_A2_Report.tex','report_latex/design_reference_preamble.tex','report_latex/README.md','output/pdf/DAS732_A2_Report_IEEE.pdf','output/DAS732_A2_LaTeX_Source.zip']:
        copy(rel)
    # Source and audit data are small enough to keep in full; do not package logs,
    # hidden files, executable caches or any external parent-workspace dependency.
    for p in (ROOT/'data').rglob('*'):
        if p.is_file() and p.suffix in {'.csv','.json','.npz','.js'}:copy(p.relative_to(ROOT))
    figures=json.loads((ROOT/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    for f in figures:
        source=Path(f['path']);copy(source)
        if (ROOT/source).with_suffix('.svg').is_file():copy(source.with_suffix('.svg'))
        for suffix in ['.png','.svg']:
            image=Path(f'images/report/Fig{f["figure"]}{suffix}')
            if (ROOT/image).is_file():copy(image)
        copy(f'report_latex/figures/Fig{f["figure"]}.png')
    for name in ['network','pcp','treemap']:copy(f'report_latex/figures/UI_{name}.png')
    for p in (ROOT/'output/review_revision').iterdir():
        if p.is_file() and p.suffix in {'.png','.svg'}:copy(p.relative_to(ROOT))
    if (ROOT/'REVIEW_RESPONSE.md').exists():copy('REVIEW_RESPONSE.md')
    # Keep the contour source needed to compose its worked interpolation panel.
    copy('images/scivis/scivis_contour_experiments.png')
    for p in (ROOT/'images/scivis').glob('*.gif'):copy(p.relative_to(ROOT))
    for folder in ['output/additional_evidence','output/final_research','output/internet_research','output/internet_revision','output/internet_review_20261024','output/lecture_previews','output/network_revision','output/pcp_changes','output/proposals_20261026','output/research_candidates','output/review_revision','output/simple_revision','output/infovis_audit_20261026']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p.suffix in {'.json','.csv','.npz','.js'}:copy(p.relative_to(ROOT))
    for p in (ROOT/'output/network_revision').iterdir():
        if p.is_file() and p.suffix in {'.html','.png','.svg'}:copy(p.relative_to(ROOT))
    for p in (ROOT/'output/pcp_changes').iterdir():
        if p.is_file() and p.suffix in {'.html','.md','.js'}:copy(p.relative_to(ROOT))
    for p in (ROOT/'output').glob('*validation.json'):copy(p.relative_to(ROOT))
    # Preserve all actual UI assets, including the locally vendored D3 library.
    for p in (ROOT/'web').rglob('*'):
        if p.is_file() and p.suffix in {'.html','.css','.js','.md','.txt'}:copy(p.relative_to(ROOT))
    for p in (ROOT/'images/gui').glob('*.png'):copy(p.relative_to(ROOT))
    # Copy stage entry points and their local Python import closure, rather than
    # old video, publishing and abandoned document-generation scripts.
    scripts=ROOT/'scripts';wanted={x for stage in STAGES.values() for x in stage}
    wanted.update(['submission_workflow.py','fetch_daily_gridmet.py','assignment_requirements.py'])
    changed=True
    while changed:
        changed=False
        for name in list(wanted):
            tree=ast.parse((scripts/name).read_text(encoding='utf-8-sig'))
            for node in ast.walk(tree):
                imports=[alias.name for alias in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else []
                for module in imports:
                    candidate=module.split('.')[0]+'.py'
                    if (scripts/candidate).is_file() and candidate not in wanted:wanted.add(candidate);changed=True
    for name in sorted(wanted):copy(Path('scripts')/name)
    copy('scripts/audit_infovis_interactions.mjs')
    readme=(ROOT/'scripts/SUBMISSION_README.template.md').read_text(encoding='utf-8')
    (dest/'README.md').write_text(readme,encoding='utf-8')
    # This template is kept for report modules that expect a README source; it
    # describes this portable folder, not a GitHub checkout.
    (dest/'scripts/README.template.md').write_text(readme,encoding='utf-8')
    assignment_requirements.write(dest,ROOT/'output/pdf/DAS732_A2_Requirements_Audit.pdf')
    shutil.copy2(ROOT/'output/pdf/DAS732_A2_Requirements_Audit.pdf',dest/'evidence/Requirements_Audit.pdf')
    env={'python':sys.version,'platform':platform.platform(),'packages':{}}
    for name in ['numpy','pandas','networkx','matplotlib','netCDF4','Pillow','reportlab','scipy','PyMuPDF']:
        env['packages'][name]=importlib.metadata.version(name)
    for tool in ['node','pdflatex']:
        p=subprocess.run([tool,'--version'],capture_output=True,text=True,errors='replace');env[tool]=p.stdout.splitlines()[0]
    (dest/'evidence/environment_versions.json').write_text(json.dumps(env,indent=2),encoding='utf-8')
    from importlib import util
    spec=util.spec_from_file_location('export_workflow',dest/'scripts/submission_workflow.py');workflow=util.module_from_spec(spec);spec.loader.exec_module(workflow);workflow.local_assets()
    # Initial list doubles as a tidy allowlist after testing full regeneration.
    initial=[p.relative_to(dest).as_posix() for p in dest.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='submission_manifest.json' and p.relative_to(dest).as_posix()!='evidence/submission_validation.json']
    (ROOT/'tmp/submission_initial_files.json').write_text(json.dumps(initial,indent=2),encoding='utf-8')
    print(json.dumps({'folder':str(dest),'files':len(initial),'megabytes':round(sum(p.stat().st_size for p in dest.rglob('*') if p.is_file())/1e6,1),'python_sources':len(wanted),'report_figures':len(figures)},indent=2))

if __name__=='__main__':main()
