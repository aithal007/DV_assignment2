"""Independently check added figures against source tables and daily cache."""
from pathlib import Path
from itertools import groupby
import json,zipfile
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/additional_evidence'
facts=json.loads((OUT/'facts.json').read_text())
raw=pd.read_csv(ROOT/'data/processed/master_dataset_countries_only.csv')
fields=['internet_users_share_pct','telephone_lines_per100','broadband_subs_per100','mobile_subs_per100']
raw=raw.loc[raw.year.eq(2020)].dropna(subset=['code']+fields).sort_values('code').set_index('code')
rows=pd.read_csv(OUT/'similar_adoption_pairs.csv')
assert len(rows)==454 and rows.retained.sum()==71
expected=set()
codes=list(raw.index)
for i,u in enumerate(codes):
    for v in codes[i+1:]:
        if abs(raw.loc[u,fields[0]]-raw.loc[v,fields[0]])<=1:expected.add((u,v))
assert expected==set(zip(rows.code_a,rows.code_b))
for row in rows.itertuples():
    for field in fields:
        assert np.isclose(getattr(row,'absolute_gap_'+field),abs(raw.loc[row.code_a,field]-raw.loc[row.code_b,field]),atol=1e-12)
selected=rows[rows.selected].sort_values('infrastructure_distance')
assert np.allclose(selected.infrastructure_distance,[rows.infrastructure_distance.min(),rows.infrastructure_distance.sort_values().iloc[len(rows)//2],rows.infrastructure_distance.max()])
daily=pd.read_csv(OUT/'daily_event_calendar.csv')
with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz') as z:
    for (lat,lon),sub in daily.groupby(['lat','lon'],sort=False):
        a=int(np.argmin(abs(z['lat']-lat)));b=int(np.argmin(abs(z['lon']-lon)))
        assert abs(z['lat'][a]-lat)<1e-8 and abs(z['lon'][b]-lon)<1e-8
        events=(z['tmmx'][:,a,b]>=35)&(z['pr'][:,a,b]<1)
        assert len(sub)==92 and np.array_equal(events,sub.hot_dry.astype(bool))
        assert list(z['dates'].astype(str))==sub.date.tolist()
        run=max((sum(1 for _ in g) for value,g in groupby(events) if value),default=0)
        assert run==sub.longest_run.iloc[0] and events.sum()==sub.event_days.iloc[0]
assert daily.groupby(['lat','lon']).hot_dry.sum().nunique()==1
assert set(daily.longest_run)=={17,67}
manifest=json.loads((ROOT/'data/current_figure_manifest.json').read_text())
old=json.loads((OUT/'original_figure_paths.json').read_text())
assert sorted((f.get('analysis_id',f['figure']),f['path']) for f in manifest if f.get('analysis_id',f['figure'])<=30)==sorted((f['figure'],f['path']) for f in old)
assert [f['figure'] for f in manifest]==list(range(1,33))
result=dict(status='PASS',original_figures_retained=30,total_figures=32,country_pairs_checked=len(rows),retained_pairs=71,calendar_cell_days_checked=len(daily),equal_event_counts=75,longest_runs=[17,67])
(OUT/'validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
