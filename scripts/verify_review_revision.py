"""Verify corrections against raw cached measurements and independent contours."""
from pathlib import Path
import json,re
import numpy as np
import pandas as pd
import pymupdf
from marching_squares import validate

ROOT=Path(__file__).resolve().parents[1]
def main():
    facts=json.loads((ROOT/'output/review_revision/facts.json').read_text())
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz') as z:
        valid=np.logical_and.reduce([np.isfinite(z[k]).all(0) for k in ['tmmx','pr','vs','th']]);w=np.broadcast_to(np.cos(np.deg2rad(z['lat']))[:,None],valid.shape)
        mask=valid&(z['lon']<-105)[None,:]
        assert np.isclose(np.average(z['tmmx'][26][mask],weights=w[mask]),facts['western_July27_mean_C'])
        assert np.isclose(np.average(z['tmmx'][:31,valid].mean(0),weights=w[valid]),facts['July_all_area_mean_C'])
        delta=z['tmmx'][62:].mean(0)-z['tmmx'][:31].mean(0);end=z['tmmx'][-1]-z['tmmx'][0]
        assert np.isclose(100*np.average((delta*end<0)[valid],weights=w[valid]),facts['endpoint_sign_disagreement_pct'])
        h=facts['hovmoller'];j=np.argmin(abs(z['lon']-h['longitude']));i=list(z['dates'].astype(str)).index(h['date']);keep=valid[:,j]&(z['lat']>=30)&(z['lat']<=45)
        assert keep.sum()==h['support_cells']==2
        assert np.isclose(np.average(z['pr'][i,keep,j],weights=np.cos(np.deg2rad(z['lat'][keep]))),h['max_rain_mm_day'])
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_n8_s6.npz') as z:
        result=validate(z['lon'],z['lat'],z['tmmx'][4],[25,30,35,40])
        assert result==facts['marching_squares']
    annual=pd.read_csv(ROOT/'data/internet_panel_2000_2020.csv');median=annual[annual.region.eq('Oceania')&annual.year.eq(2020)].internet_users_share_pct.median();assert np.isclose(median,53.7123)
    pdf=pymupdf.open(ROOT/'output/pdf/DAS732_A2_Report_IEEE.pdf');text=' '.join(' '.join(p.get_text().split()) for p in pdf)
    for phrase in ['proposed allocation','video opening','video conclusion','report/video','online method review','time runs vertically']:
        assert phrase not in text.lower(),phrase
    assert len(pdf)>=12
    assert 'Live dashboard' in pdf[0].get_text()
    assert 'uncropped browser capture' not in text.lower()
    for phrase in ['95.20','31.193','31.192','53.71','98,598','Marching Squares']:
        assert phrase in text,phrase
    assert '175' in text and '179' in text
    receipt=dict(status='PASS',sixteen_case_checks=32,real_contour_levels=[25,30,35,40],raw_weather_numbers_verified=True,
        embedded_complete_UI_pages=0,dashboard_link_on_first_page=True,oceania_2020_median=float(median),pages=len(pdf))
    (ROOT/'output/review_revision/validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
