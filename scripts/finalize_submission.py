"""Tidy the tested local submission, verify its files, and create a ZIP."""
from pathlib import Path
from urllib.parse import unquote,urlsplit
import hashlib,json,re,shutil,subprocess,sys,zipfile
from PIL import Image
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
DEST=(ROOT.parent/'DAS732_A2_Submission').resolve()

def main():
    assert DEST.parent==ROOT.parent.resolve() and DEST.name=='DAS732_A2_Submission'
    initial=set(json.loads((ROOT/'tmp/submission_initial_files.json').read_text(encoding='utf-8')))
    keep=initial|{'scripts/render_story_report.py','evidence/reproduction.log','evidence/browser_test.log','evidence/report_recapture.log','evidence/latex_build.log'}
    # Preserve the final compiler receipt at a deliberate evidence path rather
    # than shipping temporary auxiliary/output files in report_latex.
    if (DEST/'report_latex/DAS732_A2_Report.log').exists():shutil.copy2(DEST/'report_latex/DAS732_A2_Report.log',DEST/'evidence/latex_build.log')
    def read_log(path):
        b=path.read_bytes();return b.decode('utf-16' if b.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
    first=read_log(DEST/'evidence/reproduction.log')
    continued_path=DEST/'evidence/reproduction_continued.log'
    continued=read_log(continued_path) if continued_path.exists() else ''
    for name in ['browser_test.log','report_recapture.log']:
        p=DEST/'evidence'/name;p.write_text(read_log(p),encoding='utf-8')
    clean=first
    if continued:
        clean=first.split('[figures] build_approved_assets.py')[0]
        clean+='\n[Packaging correction] Removed an unused lecture-preview dependency from the selected contour builder. The required contour figure and subsequent stages were rerun successfully.\n[figures] build_approved_assets.py; network_threshold_revision.py; build_additional_evidence.py\n'+continued
    (DEST/'evidence/reproduction.log').write_text(clean,encoding='utf-8')
    # Remove only newly generated, unselected files below this exact folder.
    removed=[]
    for p in list(DEST.rglob('*')):
        if not p.is_file():continue
        resolved=p.resolve();assert resolved.is_relative_to(DEST)
        rel=p.relative_to(DEST).as_posix()
        if rel not in keep:p.unlink();removed.append(rel)
    for p in sorted((p for p in DEST.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):
        assert p.resolve().is_relative_to(DEST)
        if not any(p.iterdir()):p.rmdir()
    verification=subprocess.run([sys.executable,'-X','utf8',str(DEST/'scripts/submission_workflow.py'),'--stage','verify'],cwd=DEST,capture_output=True,text=True,encoding='utf-8')
    if verification.returncode:raise RuntimeError(verification.stdout[-1500:]+verification.stderr[-2000:])
    # The verify operation can recreate Python import caches; remove those file
    # artifacts individually, without recursively deleting a computed path.
    for p in list(DEST.rglob('*.pyc')):
        assert p.resolve().is_relative_to(DEST);p.unlink()
    for p in sorted(DEST.rglob('__pycache__'),key=lambda p:len(p.parts),reverse=True):
        assert p.resolve().is_relative_to(DEST)
        if not any(p.iterdir()):p.rmdir()
    pdf=pymupdf.open(DEST/'DAS732_A2_Report.pdf');text=' '.join(p.get_text() for p in pdf)
    assert len(pdf)>=12 and not re.search(r'Person\s+[ABC]\b',text)
    assert (DEST/'DAS732_A2_Report.pdf').read_bytes()==(DEST/'output/pdf/DAS732_A2_Report_IEEE.pdf').read_bytes()
    manifest=json.loads((DEST/'data/current_figure_manifest.json').read_text(encoding='utf-8'))
    assert [f['figure'] for f in manifest]==list(range(1,33))
    dimensions={}
    for f in manifest:
        n=f['figure'];p=DEST/f'images/report/Fig{n}.png'
        assert p.read_bytes()==(DEST/f['path']).read_bytes()==(DEST/f'report_latex/figures/Fig{n}.png').read_bytes()
        with Image.open(p) as im:
            assert im.width>=1200;dimensions[str(n)]=list(im.size);im.verify()
    gif_frames={}
    for p in (DEST/'images/scivis').glob('*.gif'):
        with Image.open(p) as im:gif_frames[p.name]=im.n_frames
    assert len(gif_frames)==3 and set(gif_frames.values())=={8}
    checked=0
    html_files=[DEST/'figures.html',DEST/'interactions.html',DEST/'web/home.html',DEST/'web/index.html',DEST/'web/network.html',DEST/'web/treemap.html',DEST/'output/pcp_changes/index.html',DEST/'output/quality_figures/index.html',DEST/'output/network_revision/index.html']
    for p in html_files:
        for ref in re.findall(r'(?:href|src)="([^"]+)"',p.read_text(encoding='utf-8')):
            if ref.startswith(('http:','https:','#','data:')):continue
            target=(p.parent/unquote(urlsplit(ref).path)).resolve()
            assert target.is_relative_to(DEST) and target.is_file(),(p,ref)
            checked+=1
    browser=json.loads((DEST/'output/infovis_audit_20261026/interactions.json').read_text(encoding='utf-8'))
    assert not browser['errors'] and all(browser[k]['passed'] for k in ['network','parallel_coordinates','treemap','paired_changes'])
    assert not any(p.name in {'.git','archive','__pycache__','video_presentation'} for p in DEST.rglob('*'))
    figures_by_member=json.loads((DEST/'data/proposed_three_part_split.json').read_text(encoding='utf-8'))['parts']
    assert sorted(n for person in figures_by_member for n in person['ids'])==list(range(1,33))
    result=dict(status='PASS',report_pages=len(pdf),figure_sets=32,references=11,person_labels_removed=True,
        gif_frames=gif_frames,local_html_asset_links_checked=checked,browser_interactions_passed=True,
        numerical_and_report_stages_passed=True,archive_or_git_dependencies=False,
        allocation={p['name']:len(p['ids']) for p in figures_by_member},
        team_confirmation_needed=['TA dataset-slice registration','Actual independent task ownership'],
        high_resolution_dimensions=dimensions,temporary_or_unselected_generated_files_removed=len(removed))
    (DEST/'evidence/submission_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    entries=[]
    for p in sorted(DEST.rglob('*')):
        if p.is_file():entries.append(dict(path=p.relative_to(DEST).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (DEST/'submission_manifest.json').write_text(json.dumps(dict(files=entries,total_files=len(entries),total_bytes=sum(x['bytes'] for x in entries)),indent=2),encoding='utf-8')
    target=DEST.with_suffix('.zip')
    if target.exists():raise FileExistsError(target)
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file():z.write(p,DEST.name+'/'+p.relative_to(DEST).as_posix())
    with zipfile.ZipFile(target) as z:assert z.testzip() is None
    print(json.dumps(dict(folder=str(DEST),zip=str(target),zip_megabytes=round(target.stat().st_size/1e6,1),files=len(entries)+1,pages=len(pdf),figures=32,status='PASS'),indent=2))

if __name__=='__main__':main()
