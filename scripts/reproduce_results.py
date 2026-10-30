"""Run the data-to-report pipeline. Run from ass2; see README for stages."""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
STAGES={
    'data':['preprocess_data.py','prepare_infovis.py'],
    'figures':['build_infovis_data.py','build_temporal_figures.py','build_scivis.py','build_scivis_results.py','build_extended_figures.py','build_quality_figures.py','verify_quality_figures.py','preview_lecture_extensions.py','build_quantile_change.py','research_internet_candidates.py','research_plot_candidates.py','final_research_figures.py','preview_internet_review_20261024.py','build_internet_revision.py','build_simple_figures.py','build_approved_assets.py','network_threshold_revision.py','build_additional_evidence.py'],
    'report':['build_change_pcp.py','build_gentle_pcp.py','preview_rubric_replacements.py','build_story_report.py','sync_report_delivery.py','verify_final_research.py','verify_internet_revision.py','verify_simple_figures.py','verify_story_report.py','verify_additional_evidence.py','build_report_change_review.py','check_layout_revision.py','package_selected_report.py'],
}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',choices=['all',*STAGES],default='all')
    p.add_argument('--download-weather',action='store_true',help='Retrieve missing weather caches during data stage')
    args=p.parse_args()
    for stage in (STAGES if args.stage=='all' else [args.stage]):
        for name in STAGES[stage]:
            command=[sys.executable,'-X','utf8',str(ROOT/'scripts'/name)]
            if name=='preprocess_data.py' and args.download_weather: command+=['--download-weather']
            print(f'[{stage}] {name}',flush=True)
            subprocess.run(command,cwd=ROOT,check=True)
    print('Requested reproduction stages completed.')

if __name__=='__main__': main()
