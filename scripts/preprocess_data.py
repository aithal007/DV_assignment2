"""Prepare A2 analysis inputs without drawing plots. Run from ass2.

Default: local raw country CSVs and existing Celsius weather caches.
--download-weather fetches missing gridMET caches from the documented source.
"""
from pathlib import Path
from datetime import date
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ['internet_users_share_pct','telephone_lines_per100','broadband_subs_per100','mobile_subs_per100']
SOURCES = {
    'number-of-internet-users.csv': {'it_net_user_zs_number':'internet_users_count'},
    'share-of-individuals-using-the-internet.csv': {'it_net_user_zs':'internet_users_share_pct'},
    'ict-adoption-per-100-people.csv': {'it_mlt_main_p2':'telephone_lines_per100','it_net_bbnd_p2':'broadband_subs_per100','it_cel_sets_p2':'mobile_subs_per100'},
}
AGGREGATES = {'World','High-income countries','Low-income countries','Lower-middle-income countries','Upper-middle-income countries','Africa (UN)','Asia (UN)','Europe (UN)','Northern America (UN)','Central and Southern Asia (UN SDG)','East Asia and Pacific (WB)','Eastern and South-Eastern Asia (UN SDG)','Europe and Central Asia (WB)','Europe and Northern America (UN SDG)','European Union (27)','Latin America and Caribbean (WB)','Latin America and the Caribbean (UN SDG)','Latin America and the Caribbean (UN)','Middle East, North Africa, Afghanistan and Pakistan (WB)','North America (WB)','Northern Africa and Western Asia (UN SDG)','Small Island Developing States (SIDS)','South Asia (WB)','Sub-Saharan Africa (UN SDG)','Sub-Saharan Africa (WB)'}

def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--download-weather',action='store_true')
    args=ap.parse_args()
    raw=ROOT/'data/raw'; out=ROOT/'data/processed'; out.mkdir(parents=True,exist_ok=True)
    evidence={'input_files':{},'raw_rows':{},'steps':[]}
    merged=None
    for name,rename in SOURCES.items():
        path=raw/name
        if not path.exists(): raise FileNotFoundError(f'Missing raw input {path}. See README preprocessing instructions.')
        df=pd.read_csv(path).rename(columns={'Entity':'entity','Code':'code','Year':'year',**rename})
        df=df[['entity','code','year',*rename.values()]].copy()
        if df.duplicated(['entity','code','year']).any(): raise ValueError(f'Duplicate source keys: {name}')
        for col in rename.values(): df[col]=pd.to_numeric(df[col],errors='raise')
        evidence['input_files'][name]=checksum(path); evidence['raw_rows'][name]=len(df)
        merged=df if merged is None else merged.merge(df,on=['entity','code','year'],how='outer',validate='one_to_one')
    merged['is_aggregate']=merged.entity.isin(AGGREGATES)
    countries=merged.loc[~merged.is_aggregate].sort_values(['entity','year']).reset_index(drop=True)
    evidence['join_counts']={'merged_rows':len(merged),'aggregate_rows_removed':int(merged.is_aggregate.sum()),'country_rows_retained':len(countries),'duplicate_join_keys':0}
    countries.to_csv(out/'master_dataset_countries_only.csv',index=False)
    regions=pd.read_csv(raw/'region_lookup.csv')
    if regions.code.duplicated().any(): raise ValueError('Duplicate region lookup code')
    regions.to_csv(out/'region_lookup.csv',index=False)
    evidence['input_files']['region_lookup.csv']=checksum(raw/'region_lookup.csv')
    complete=countries.dropna(subset=['code',*PROFILE])
    old=set(complete.loc[complete.year.eq(2015),'code']); latest=set(complete.loc[complete.year.eq(2020),'code'])
    annual=countries.loc[countries.year.between(2000,2020)].dropna(subset=['code',PROFILE[0]])
    panel=annual.groupby('code').year.nunique().eq(21)
    tree=countries.loc[countries.year.eq(2020)].dropna(subset=['code','internet_users_count',PROFILE[0]])
    tree=tree.loc[tree.internet_users_count.ge(0)]
    evidence['country_cohorts']={'graph_2020':len(latest),'matched_2015_2020':len(old&latest),'annual_complete_2000_2020':int(panel.sum()),'treemap_2020':len(tree),'treemap_users':int(tree.internet_users_count.round().sum())}
    assert evidence['country_cohorts']==dict(graph_2020=179,matched_2015_2020=175,annual_complete_2000_2020=159,treemap_2020=184,treemap_users=4521767530)
    evidence['country_missing_values']=countries[PROFILE+['internet_users_count']].isna().sum().to_dict()
    evidence['steps']=['Rename source indicator columns; outer-join on entity/code/year with one-to-one key checks.', 'Remove explicitly listed aggregate entities; preserve missing values without imputation. Unmapped regions become Unclassified in downstream builders.', 'Use task-specific complete cases, a matched 2015/2020 intersection, and a balanced 2000-2020 adoption panel. Graph builder z-scores four indicators, computes all unique pair similarities, and applies a documented global quantile threshold.', 'Decode NetCDF masks/packing before converting source tmmx Kelvin to Celsius; derived caches already contain Celsius and are never converted twice.', 'Read every sixth grid cell (subsampling, not averaging); verify common coordinates/dates. Keep eight samples separately from the full 92-day series.', 'Build the all-variable/all-date valid mask and cosine-latitude weights; precipitation stays in mm, speed in m/s, direction in degrees FROM north.']
    sampled=ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_n8_s6.npz'
    daily=ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz'
    if args.download_weather:
        from build_scivis import get_fields
        get_fields(date(2023,7,1),date(2023,9,30),8,6,False)
        subprocess.run([sys.executable,str(ROOT/'scripts/fetch_daily_gridmet.py')],check=True)
    if not sampled.exists() or not daily.exists(): raise FileNotFoundError('Weather cache missing. Run preprocess_data.py --download-weather (internet required), or restore data/scivis caches.')
    with np.load(daily) as z, np.load(sampled) as a:
        dates=z['dates'].astype('datetime64[D]')
        assert len(dates)==92 and np.all(np.diff(dates)==np.timedelta64(1,'D'))
        assert str(dates[0])=='2023-07-01' and str(dates[-1])=='2023-09-30'
        assert np.array_equal(z['lat'],a['lat']) and np.array_equal(z['lon'],a['lon'])
        mask=np.logical_and.reduce([np.isfinite(z[k]).all(axis=0) for k in ['tmmx','pr','vs','th']])
        assert int(mask.sum())==13416
        weights=np.broadcast_to(np.cos(np.deg2rad(z['lat']))[:,None],mask.shape)
        np.savez_compressed(out/'weather_support.npz',valid_mask=mask,area_weights=np.where(mask,weights,0),lat=z['lat'],lon=z['lon'],dates=z['dates'])
        sample_dates=json.loads((ROOT/'data/scivis/manifest.json').read_text())['sample_dates']
        for i,d in enumerate(sample_dates):
            j=int(np.flatnonzero(dates==np.datetime64(d))[0])
            for k in ['tmmx','pr','vs','th']: np.testing.assert_allclose(a[k][i],z[k][j],equal_nan=True)
        assert -90<float(np.nanmin(z['tmmx']))<float(np.nanmax(z['tmmx']))<65
        assert np.nanmin(z['pr'])>=0 and np.nanmin(z['vs'])>=0
        assert 0<=np.nanmin(z['th'])<=np.nanmax(z['th'])<=360
        evidence['weather']={'daily_dates':92,'sample_dates':sample_dates,'common_cells':int(mask.sum()),'units':{'tmmx':'Celsius','pr':'mm/day','vs':'m/s','th':'degrees FROM clockwise from north'},'caches':{p.name:checksum(p) for p in [sampled,daily]}}
    evidence['outputs']={p.name:checksum(p) for p in [out/'master_dataset_countries_only.csv',out/'region_lookup.csv',out/'weather_support.npz']}
    (out/'preprocessing_audit.json').write_text(json.dumps(evidence,indent=2),encoding='utf8')
    print(json.dumps({'status':'PASS','cohorts':evidence['country_cohorts'],'weather_cells':13416,'audit':str(out/'preprocessing_audit.json')},indent=2))

if __name__=='__main__': main()
