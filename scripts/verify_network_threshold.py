"""Independently check all-pair similarities, cutoff, isolates and matrix cells."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import networkx as nx
ROOT=Path(__file__).resolve().parents[1]
raw=pd.read_csv(ROOT/'data/processed/master_dataset_countries_only.csv')
fields=['internet_users_share_pct','telephone_lines_per100','broadband_subs_per100','mobile_subs_per100']
raw=raw[raw.year.eq(2020)].dropna(subset=['code',*fields]).sort_values('code')
x=raw[fields].to_numpy();z=(x-x.mean(0))/x.std(0,ddof=0);ids=list(raw.code);ix={c:i for i,c in enumerate(ids)}
d=json.loads((ROOT/'data/country_network_2020.json').read_text());a=json.loads((ROOT/'data/network_threshold_audit.json').read_text())
assert len(d['nodes'])==179 and len(d['all_edges'])==179*178//2==15931
pairs=set();values=[]
for e in d['all_edges']:
    pair=tuple(sorted((e['source'],e['target'])));assert pair[0]!=pair[1] and pair not in pairs;pairs.add(pair)
    v=1/(1+float(np.sqrt(sum((z[ix[pair[0]]]-z[ix[pair[1]]])**2))))
    assert np.isclose(v,e['similarity'],atol=1e-14);values.append(v)
threshold=float(np.quantile(values,.95));assert threshold==a['threshold']==d['default_threshold']
expected={tuple(sorted((e['source'],e['target']))) for e in d['all_edges'] if e['similarity']>=threshold}
actual={tuple(sorted((e['source'],e['target']))) for e in d['edges']};assert actual==expected and len(actual)==797
g=nx.Graph();g.add_nodes_from(ids);g.add_edges_from(actual);assert len(list(nx.isolates(g)))==12
for name,positions in d['layouts'].items():assert set(positions)==set(ids)
for row in a['threshold_sweep']:
    expected_count=sum(v>=row['threshold'] for v in values);assert expected_count==row['edges']
m=pd.read_csv(ROOT/'output/network_revision/nodetrix_detail_matrix.csv',index_col=0)
assert np.array_equal(m,m.T) and not np.diag(m).any()
for u in m.index:
    for v in m.columns:assert m.loc[u,v]==int(u!=v and tuple(sorted((u,v))) in actual)
assert m.to_numpy().sum()==186
result=dict(status='PASS',all_pairs_checked=15931,filtered_pairs=797,threshold=threshold,isolates=12,matrix_cells_checked=m.size,layouts=3,perturbation_trials=len(a['perturbations']))
(ROOT/'output/network_revision/validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
