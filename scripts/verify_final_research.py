"""Independently verify selected research quantities against original cached inputs."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def main():
    panel=pd.read_csv(ROOT/'data/internet_panel_2000_2020.csv')
    annual=pd.read_csv(ROOT/'output/internet_research/inequality_annual.csv')
    for row in annual.itertuples():
        sub=panel[panel.year==row.year];v=np.sort(sub.internet_users_share_pct.to_numpy());n=len(v)
        assert n==159
        # Sorted pair differences avoid constructing the generator's n-by-n difference array.
        mad=2*np.dot(2*np.arange(1,n+1)-n-1,v)/n**2
        assert np.isclose(mad,row.mean_pairwise_gap)
        assert np.isclose(mad/(2*v.mean()),row.gini)
        sub=sub[sub.region!='Unclassified'];x=sub.internet_users_share_pct;means=sub.groupby('region').internet_users_share_pct.transform('mean')
        within=float(((x-means)**2).mean());between=float(((means-x.mean())**2).mean())
        assert len(sub)==158 and np.isclose(within,row.within_variance) and np.isclose(between,row.between_variance)
    raw=pd.read_json(ROOT/'data/infovis_countries.json');a=raw[raw.year==2015].set_index('code');b=raw[raw.year==2020].set_index('code');codes=a.index.intersection(b.index);a=a.loc[codes];b=b.loc[codes]
    assert len(codes)==175
    final=pd.read_csv(ROOT/'output/final_research/regional_endpoints_gains.csv')
    for row in final.itertuples():
        mask=b.region==row.region;old=a.loc[mask,'internet_users_share_pct'];new=b.loc[mask,'internet_users_share_pct'];gain=new-old
        assert len(gain)==row.n
        for got,want in [(row.median_2015,old.median()),(row.median_2020,new.median()),(row.median_gain,gain.median()),(row.median_shift,new.median()-old.median())]:assert np.isclose(got,want)
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz') as z:
        valid=np.logical_and.reduce([np.isfinite(z[k]).all(0) for k in ['tmmx','pr','vs','th']]);rain=z['pr'][:,valid].astype(float);dates=z['dates'];lat=z['lat']
    assert valid.sum()==13416
    weights=np.broadcast_to(np.cos(np.deg2rad(lat))[:,None],valid.shape)[valid]
    cells=pd.read_csv(ROOT/'output/research_candidates/rainfall_concentration_cells.csv');metrics=json.loads((ROOT/'output/research_candidates/metrics.json').read_text())['rainfall'];sensitivity=pd.read_csv(ROOT/'output/research_candidates/rainfall_mask_sensitivity.csv')
    for month,name in [('07','July'),('08','August'),('09','September')]:
        x=rain[np.array([str(d)[5:7]==month for d in dates])];total=x.sum(0);running=np.vstack([np.zeros(x.shape[1]),x.cumsum(0)]);peak=(running[5:]-running[:-5]).max(0)
        saved=cells[cells.month==name];assert np.allclose(total,saved.total_mm) and np.allclose(peak,saved.peak5_mm)
        share=np.divide(peak,total,out=np.full_like(total,np.nan),where=total>0)*100
        assert np.allclose(share,saved.peak5_share_pct,equal_nan=True)
        for threshold in [1,10,25,50]:
            mask=total>=threshold;pct=float(weights[mask&(share>=50)].sum()/weights[mask].sum()*100)
            ref=sensitivity[(sensitivity.month==name)&(sensitivity.minimum_monthly_total_mm==threshold)].iloc[0]
            assert np.isclose(pct,ref.area_pct_at_least_half_in_5days)
            if threshold==10:assert np.isclose(pct,next(r for r in metrics if r['month']==name)['area_fraction_peak5_at_least_half_conditional'])
    result=dict(status='PASS',annual_inequality_years=21,country_panel=159,classified_panel=158,regional_gain_panel=175,rainfall_cells=13416,rainfall_months=3,minimum_rain_threshold_checks=12,checks=['sorted pair-gap identity','all-year variance decomposition','regional endpoints versus paired gains','all-cell cumulative-sum rainfall windows','conditional area-weighted concentration and minimum-total sensitivity'])
    (ROOT/'output/final_research_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
