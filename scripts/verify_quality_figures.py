"""Independent numerical checks for the revised analyses and figure artifacts."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]


def main():
    data=ROOT/'data/quality'
    metrics=json.loads((data/'metrics.json').read_text())
    raw=pd.read_json(ROOT/'data/infovis_countries.json')
    wide=raw.pivot(index='code',columns='year',values=['internet_users_share_pct','telephone_lines_per100','broadband_subs_per100','mobile_subs_per100']).dropna()
    assert len(wide)==175
    change=wide.xs(2020,axis=1,level=1)-wide.xs(2015,axis=1,level=1)
    count=((change.internet_users_share_pct>0)&(change.telephone_lines_per100<0)).sum()
    assert count==metrics['country']['positive_internet_negative_landline']==126
    rho=wide.xs(2020,axis=1,level=1).corr(method='spearman').loc['internet_users_share_pct','broadband_subs_per100']
    np.testing.assert_allclose(rho,metrics['country']['level_broadband_rho'],rtol=0,atol=1e-12)
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz') as z, np.load(data/'weather_summaries.npz') as derived:
        valid=derived['valid']; t=z['tmmx'].astype(float); p=z['pr'].astype(float)
        flag=(t[:,valid]>=35)&(p[:,valid]<1)
        # Independent run extraction by transition positions for every valid cell.
        expected=[]
        for column in flag.T:
            changes=np.diff(np.r_[False,column,False].astype(int))
            runs=np.flatnonzero(changes==-1)-np.flatnonzero(changes==1)
            expected.append(int(runs.max()) if len(runs) else 0)
        np.testing.assert_array_equal(expected,derived['longest_run_days'][valid])
        np.testing.assert_allclose(flag.sum(axis=0)*100/92,derived['frequency_pct'][valid],rtol=0,atol=1e-12)
        assert int(max(expected))==67
        months=np.array([str(d)[5:7] for d in z['dates']])
        diff=t[months=='09'][:,valid].sum(axis=0)/30-t[months=='07'][:,valid].sum(axis=0)/31
        np.testing.assert_allclose(diff,derived['monthly_change_C'][valid],rtol=0,atol=1e-12)
        w=np.broadcast_to(np.cos(np.deg2rad(z['lat']))[:,None],valid.shape)[valid]
        assert np.isclose(np.average(diff,weights=w),metrics['weather']['monthly_change_mean_C'])
        with np.load(data/'hovmoller.npz') as hov:
            counts=hov['cell_counts']
            for j in [np.flatnonzero(counts)[0],len(counts)//2,np.flatnonzero(counts)[-1]]:
                cells=valid[:,j]&(z['lat']>=30)&(z['lat']<=45)
                for day in [0,46,91]:
                    wt=np.cos(np.deg2rad(z['lat'][cells]))
                    np.testing.assert_allclose(np.average(t[day,cells,j],weights=wt),hov['temperature_C'][day,j],atol=1e-12)
                    np.testing.assert_allclose(np.average(p[day,cells,j],weights=wt),hov['rain_mm'][day,j],atol=1e-12)
    sensitivity=pd.read_csv(data/'threshold_sensitivity.csv')
    for rain,rows in sensitivity.groupby('rain_below_mm'):
        assert (rows.sort_values('tmax_threshold_C').area_day_pct.diff().dropna()<=0).all()
    for temp,rows in sensitivity.groupby('tmax_threshold_C'):
        assert (rows.sort_values('rain_below_mm').area_day_pct.diff().dropna()>=0).all()
    figures=json.loads((data/'figures.json').read_text())
    assert len(figures)==7 and len({f['key'] for f in figures})==7
    for f in figures:
        path=ROOT/f['path']
        with Image.open(path) as im:
            assert min(im.size)>=1200
            im.verify()
        assert path.with_suffix('.svg').exists()
        assert all(f['explanation'])
    result=dict(status='PASS',matched_countries=175,quadrant_count=126,
        run_length_validation='independent transition-based check over all 13416 cells',
        monthly_means='independent daily-sum verification',hovmoller='edge and central longitude spot checks',
        thresholds='monotonicity verified',new_figures=7,high_resolution_exports='PNG and SVG verified')
    (ROOT/'output/quality_numerical_validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
