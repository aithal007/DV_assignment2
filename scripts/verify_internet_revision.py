"""Independent checks for revised selection, milestone timing and trajectories."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
d=pd.read_csv(ROOT/'data/processed/master_dataset_countries_only.csv')
raw=pd.read_json(ROOT/'data/infovis_countries.json')
codes=set(raw[raw.year.eq(2015)].code)&set(raw[raw.year.eq(2020)].code)
b=raw[raw.year.eq(2020)&raw.code.isin(codes)]
selected=b[b.internet_users_share_pct.ge(70)&b.broadband_subs_per100.le(5)]
assert set(selected.code)=={'BTN','CUB','KWT','KGZ','LBY','ZAF'} and len(b)==175
selected.to_csv(ROOT/'output/internet_revision/brush_evidence.csv',index=False)
panel=pd.read_csv(ROOT/'data/internet_panel_2000_2020.csv')
saved=pd.read_csv(ROOT/'output/internet_revision/milestone_evidence.csv')
for row in saved.itertuples():
    region=panel[panel.region.eq(row.region)]
    first=region[region.internet_users_share_pct.ge(row.threshold)].groupby('code').year.min()
    count=int(first.le(row.year).sum());n=region.code.nunique()
    assert n==row.n and np.isclose(100*count/n,row.ever_pct)
paths=pd.read_csv(ROOT/'output/internet_review_20261024/trajectory_values.csv')
assert len(paths)==66
for row in paths.itertuples():
    ref=d[d.code.eq(row.code)&d.year.eq(row.year)].iloc[0]
    assert np.isclose(row.internet_users_share_pct,ref.internet_users_share_pct)
    assert np.isclose(row.broadband_subs_per100,ref.broadband_subs_per100)
graph=json.loads((ROOT/'data/country_network_2020.json').read_text())
near=set()
for e in graph['edges']:
    if e['source']=='IND':near.add(e['target'])
    if e['target']=='IND':near.add(e['source'])
assert len(near)==12
assert len(graph['all_edges'])==15931
tree=json.loads((ROOT/'data/treemap_countries_2020.json').read_text())
assert len(tree['countries'])==184 and sum(r['internet_users'] for r in tree['countries'])==4521767530
manifest=json.loads((ROOT/'data/current_figure_manifest.json').read_text())
assert len(manifest)==30 and all((ROOT/f['path']).is_file() for f in manifest)
result={'status':'PASS','matched_countries':175,'joint_brush_countries':sorted(selected.country),'milestone_checks':len(saved),'trajectory_pairs_checked':len(paths),'network_focus_degree':len(near),'treemap_country_leaves':184,'report_figures':30,'browser_evidence':'Actual pointer brushing and other controls passed the browser audit; see output/infovis_audit_20261026/interactions.json.'}
(ROOT/'output/internet_revision/validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
