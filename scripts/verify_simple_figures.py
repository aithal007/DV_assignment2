"""Verify the simplified charts against country rows, graph edges and daily weather."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/simple_revision'
d=pd.read_json(ROOT/'data/infovis_countries.json');a=d[d.year.eq(2015)].set_index('code');b=d[d.year.eq(2020)].set_index('code');codes=a.index.intersection(b.index);a=a.loc[codes];b=b.loc[codes]
assert len(codes)==175
match=(b.internet_users_share_pct-a.internet_users_share_pct>0)&(b.telephone_lines_per100-a.telephone_lines_per100<0)
for r in pd.read_csv(OUT/'country_changes_counts.csv').itertuples():
    mask=np.ones(len(b),bool) if r.region=='All countries' else b.region.eq(r.region)
    assert int(mask.sum())==r.countries and int(match[mask].sum())==r.qualifying
    assert np.isclose(match[mask].mean()*100,r.percent)
assert match.sum()==126
graph=json.loads((ROOT/'data/country_network_2020.json').read_text());edges={frozenset((e['source'],e['target'])) for e in graph['edges']}
matrix=pd.read_csv(ROOT/'output/network_revision/nodetrix_detail_matrix.csv',index_col=0)
assert np.array_equal(matrix,matrix.T) and not np.diag(matrix).any()
for a_code in matrix.index:
    for b_code in matrix.columns:assert matrix.loc[a_code,b_code]==int(frozenset((a_code,b_code)) in edges)
assert matrix.to_numpy().sum()==186
rows=pd.read_csv(OUT/'pcp_six_values.csv');assert len(rows)==6
fields=['internet_users_share_pct','telephone_lines_per100','broadband_subs_per100','mobile_subs_per100']
domains=np.array([100,25,5,180]);centers=rows.groupby('region')[fields].mean()/domains
assert centers.to_numpy().min()>=0 and centers.to_numpy().max()<=1
for r in rows.itertuples():
    assert r.internet_users_share_pct>=70 and r.broadband_subs_per100<=5
    assert np.allclose([getattr(r,f) for f in fields],b.loc[r.code,fields].to_numpy(dtype=float))
metrics=json.loads((OUT/'metrics.json').read_text())
for f,rho in metrics['pairwise'].items():assert np.isclose(b[f].rank().corr(b.internet_users_share_pct.rank()),rho)
panel=pd.read_csv(ROOT/'data/internet_panel_2000_2020.csv');v=panel[panel.year.eq(2020)&panel.region.ne('Unclassified')]
total=float(v.internet_users_share_pct.var(ddof=0));within=0
for _,group in v.groupby('region'):within+=len(group)/len(v)*float(group.internet_users_share_pct.var(ddof=0))
assert len(v)==158 and np.isclose(100*within/total,metrics['within_regions']['within_percent'])
with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz') as z:
    valid=np.logical_and.reduce([np.isfinite(z[k]).all(0) for k in ['tmmx','pr','vs','th']])
    weights=np.broadcast_to(np.cos(np.deg2rad(z['lat']))[:,None],valid.shape)[valid]
    flags={'hot':z['tmmx'][:,valid]>=35,'dry':z['pr'][:,valid]<1,'windy':z['vs'][:,valid]>=5}
flags['all_three']=flags['hot']&flags['dry']&flags['windy']
for name,flag in flags.items():
    value=float((flag*weights).sum()/(flag.shape[0]*weights.sum())*100)
    assert np.isclose(value,metrics['overlap'][name],atol=1e-5),(name,value,metrics['overlap'][name])
result={'status':'PASS','matched_countries':175,'country_change_count':126,'matrix_cells_checked':225,'matrix_internal_edges':93,'selected_country_profiles':6,'pairwise_correlations_checked':2,'regional_variance_countries':158,'weather_frequencies_checked_from_daily_grids':4}
(OUT/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
