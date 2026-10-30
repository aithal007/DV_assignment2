"""Research-informed analytical candidates; report selection is not modified."""
from pathlib import Path
import json, html
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.stats import gaussian_kde

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/research_candidates'
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
CARDS=[]; METRICS={}

def save(fig,key,title,question,reading,finding,limits,replacement,source):
    for ext in ['png','svg']:
        fig.savefig(OUT/f'{key}.{ext}',dpi=210,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    CARDS.append(dict(key=key,title=title,question=question,reading=reading,finding=finding,limits=limits,replacement=replacement,source=source))

def raincloud():
    raw=pd.read_json(ROOT/'data/infovis_countries.json')
    a=raw[raw.year==2015].set_index('code');b=raw[raw.year==2020].set_index('code')
    codes=a.index.intersection(b.index)
    f=pd.DataFrame({'country':b.loc[codes,'country'],'region':b.loc[codes,'region'],'gain':b.loc[codes,'internet_users_share_pct']-a.loc[codes,'internet_users_share_pct']})
    assert len(f)==175
    regions=['Africa','Asia','Europe','North America','South America','Oceania','Unclassified']
    colors=['#0072b2','#d55e00','#009e73','#aa5599','#886633','#6755a0','#687787']
    fig,ax=plt.subplots(figsize=(12.5,7))
    rng=np.random.default_rng(732); stats=[]
    for i,(r,c) in enumerate(zip(regions,colors)):
        sub=f[f.region==r];v=sub.gain.to_numpy()
        if not len(v):continue
        q=np.quantile(v,[.25,.5,.75])
        if len(v)>=10 and np.std(v)>0:
            # Truncate density to observed range; points remain the authoritative values.
            x=np.linspace(v.min(),v.max(),250);d=gaussian_kde(v)(x);d=d/d.max()*.32
            ax.fill_between(x,i-.12,i-.12-d,color=c,alpha=.25,lw=1)
        ax.scatter(v,i+.18+rng.uniform(-.055,.055,len(v)),s=19,color=c,alpha=.7,edgecolors='none')
        ax.plot(q[[0,2]],[i,i],color=c,lw=5,solid_capstyle='round')
        ax.scatter(q[1],i,color='white',edgecolor=c,s=50,zorder=4)
        median_shift=float(b.loc[sub.index,'internet_users_share_pct'].median()-a.loc[sub.index,'internet_users_share_pct'].median())
        ax.scatter(median_shift,i,marker='|',s=220,color='black',zorder=5)
        stats.append(dict(region=r,n=len(v),median_individual_gain=float(q[1]),difference_of_region_medians=median_shift,q25=float(q[0]),q75=float(q[2]),minimum=float(v.min()),maximum=float(v.max()),negative=int((v<0).sum())))
    ax.set_yticks(range(7),[f'{r} (n={len(f[f.region==r])})' for r in regions]);ax.invert_yaxis()
    ax.axvline(0,color='#666',ls=':',lw=1);ax.grid(axis='x',alpha=.15)
    ax.set(xlabel='Country internet-adoption gain, 2015 to 2020 (percentage points)',title='Regional progress contains very different country experiences')
    fig.text(.5,.005,'Dots: countries  |  circle + thick line: median and middle 50% of gains  |  black tick: difference of regional medians\nDensity shown only for n >= 10; its height is normalized within each row. Jitter is cosmetic.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.055,1,1))
    pd.DataFrame(stats).to_csv(OUT/'regional_gain_summary.csv',index=False);f.to_csv(OUT/'country_gains.csv')
    asia=next(x for x in stats if x['region']=='Asia')
    finding=f"In Asia, the median individual gain is {asia['median_individual_gain']:.2f} points, versus {asia['difference_of_region_medians']:.2f} for the difference of regional medians. Country gains range from {asia['minimum']:.2f} to {asia['maximum']:.2f} points; the middle half spans {asia['q25']:.2f} to {asia['q75']:.2f}."
    METRICS['raincloud']=stats
    save(fig,'regional_gain_raincloud','Regional gain raincloud','How much do countries differ behind a regional improvement?',
         'One dot is one matched country; horizontal position is its actual change. The density shows shape, the interval shows heterogeneity, and the black tick reproduces the summary used by the dumbbell.',finding,
         'Country-weighted observational changes, not causal effects or confidence intervals. Small groups use raw dots without density. Each density is independently normalized and truncated at observed extremes; it is not a population share. Unclassified countries remain visible.',
         'Strong enhancement to Figure 11: retain a small endpoint panel or its values, and use this view to show the gains behind it. Do not replace required ridgeline variations.',
         'https://pmc.ncbi.nlm.nih.gov/articles/PMC6480976/')

def load_weather():
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz') as z:
        arrays=[z[k].astype(float) for k in ['tmmx','pr','vs','th']]
        lat,lon,dates=[z[k] for k in ['lat','lon','dates']]
    valid=np.all(np.logical_and.reduce([np.isfinite(x) for x in arrays]),axis=0)
    w=np.broadcast_to(np.cos(np.deg2rad(lat))[:,None],valid.shape)[valid]
    assert valid.sum()==13416
    return arrays,valid,w,lat,lon,dates

def rainfall(arrays,valid,w,lat,lon,dates):
    rain=arrays[1][:,valid];months=np.array([str(d)[5:7] for d in dates])
    totals=[];shares=[];stats=[]; records=[]; sensitivity=[]
    yy,xx=np.meshgrid(lat,lon,indexing='ij')
    for month,name in [('07','July'),('08','August'),('09','September')]:
        a=rain[months==month];total=a.sum(0)
        rolls=np.lib.stride_tricks.sliding_window_view(a,5,axis=0).sum(-1)
        peak=rolls.max(0);share=np.divide(peak,total,out=np.full_like(total,np.nan),where=total>0)*100
        cumulative=np.vstack([np.zeros(a.shape[1]),np.cumsum(a,axis=0)])
        assert np.allclose(peak,(cumulative[5:]-cumulative[:-5]).max(0),atol=1e-8)
        # Independent slow slicing check catches orientation and rolling-window mistakes.
        for c in [0,500,13415]:
            assert abs(peak[c]-max(a[k:k+5,c].sum() for k in range(len(a)-4)))<1e-7
        assert np.all(peak<=total+1e-8)
        totals.append(total);shares.append(share)
        eligible=total>=10
        frac=float(np.sum(w[eligible]*(share[eligible]>=50))/w[eligible].sum()*100)
        for cutoff in [1,10,25,50]:
            mask=total>=cutoff
            sensitivity.append(dict(month=name,minimum_monthly_total_mm=cutoff,eligible_area_pct=float(w[mask].sum()/w.sum()*100),area_pct_at_least_half_in_5days=float(w[mask & (share>=50)].sum()/w[mask].sum()*100)))
        stats.append(dict(month=name,days=len(a),area_fraction_total_at_least_10mm=float(w[eligible].sum()/w.sum()*100),area_fraction_peak5_at_least_half_conditional=frac))
        records.append(pd.DataFrame(dict(month=name,lat=yy[valid],lon=xx[valid],total_mm=total,peak5_mm=peak,peak5_share_pct=share,ratio_displayed=eligible)))
    fig,axs=plt.subplots(2,3,figsize=(14,7.7),layout='constrained')
    vmax=max(np.max(x) for x in totals)
    for j,name in enumerate(['July','August','September']):
        for row,values,cmap,lo,hi in [(0,totals[j],'Blues',0,vmax),(1,np.where(totals[j]>=10,shares[j],np.nan),'magma',0,100)]:
            grid=np.full(valid.shape,np.nan);grid[valid]=values
            ax=axs[row,j];im=ax.pcolormesh(lon,lat,grid,shading='nearest',cmap=cmap,vmin=lo,vmax=hi,rasterized=True)
            ax.set(title=f'{name} | '+('monthly total' if row==0 else 'wettest 5-day share'),xlabel='Longitude',ylabel='Latitude',xlim=(-125,-66),ylim=(24,50))
            ax.set_aspect(1.3);ax.set_facecolor('#e7ebee')
            if row==1:
                ax.text(.02,.025,f"At least half in 5 days: {stats[j]['area_fraction_peak5_at_least_half_conditional']:.1f}% of eligible area",transform=ax.transAxes,fontsize=8,bbox=dict(facecolor='white',alpha=.9,edgecolor='none'))
            if j==2:fig.colorbar(im,ax=axs[row,:],shrink=.85,label='Rainfall (mm)' if row==0 else '% of monthly rain in wettest 5 consecutive days')
    fig.suptitle('The same monthly total can conceal concentrated rainfall',fontsize=18,fontweight='bold')
    fig.supxlabel('92 daily fields; common 13,416-cell footprint. Bottom maps mask monthly totals <10 mm; five-day windows stay inside each month.',fontsize=10)
    pd.concat(records).to_csv(OUT/'rainfall_concentration_cells.csv',index=False)
    pd.DataFrame(sensitivity).to_csv(OUT/'rainfall_mask_sensitivity.csv',index=False)
    METRICS['rainfall']=stats
    finding='Among cells receiving at least 10 mm that month, the share of weighted area getting at least half its rain in one five-day window is '+', '.join(f"{x['month']} {x['area_fraction_peak5_at_least_half_conditional']:.1f}%" for x in stats)+'.'
    save(fig,'rainfall_concentration','Monthly rainfall and five-day concentration','Do similar monthly totals conceal rain arriving in short bursts?',
         'Top maps retain absolute monthly totals. Bottom maps divide the wettest consecutive five-day sum by the monthly total; all months use shared scales. The ratio describes timing concentration, not flood severity.',finding,
         'Adapted from the maximum consecutive five-day precipitation idea. This is a within-month diagnostic, not a claim of full climatological Rx5day implementation. Low-total cells are masked only in ratio maps. Daily gridded rain does not establish runoff, flooding, hourly intensity or a climate trend. Windows crossing month boundaries are excluded.',
         'Strongest replacement: replace Figure 22 with this two-row figure. It retains all three total maps and adds information about timing.',
         'https://www.climdex.org/learn/indices/')

def sequences(arrays,valid,w,lat,lon,dates):
    event=(arrays[0][:,valid]>=35)&(arrays[1][:,valid]<1)
    total=event.sum(0);current=np.zeros(len(w),int);longest=current.copy()
    for day in event:
        current=np.where(day,current+1,0);longest=np.maximum(current,longest)
    # Choose an exact-frequency group by largest observed persistence range; ties prefer more cells.
    eligible=[k for k in np.unique(total) if k>=10 and np.sum(total==k)>=20]
    k=max(eligible,key=lambda k:(np.ptp(longest[total==k]),np.sum(total==k),-k))
    members=np.flatnonzero(total==k);ordered=members[np.lexsort((members,longest[members]))]
    # At most 60 equally spaced ranks; keep both extremes. Save all group members.
    chosen=ordered[np.unique(np.round(np.linspace(0,len(ordered)-1,min(60,len(ordered)))).astype(int))]
    yy,xx=np.meshgrid(lat,lon,indexing='ij');ys=yy[valid];xs=xx[valid]
    pd.DataFrame(dict(cell_id=members,lat=ys[members],lon=xs[members],hotdry_days=total[members],longest_run=longest[members])).to_csv(OUT/'equal_frequency_all_cells.csv',index=False)
    pd.DataFrame(event[:,chosen].T.astype(int),index=chosen,columns=[str(d) for d in dates]).to_csv(OUT/'displayed_event_sequences.csv')
    durations=np.arange(1,93); exceed=np.array([w[longest>=d].sum()/w.sum()*100 for d in durations])
    assert np.all(np.diff(exceed)<=1e-9)
    for c in chosen:
        import itertools
        direct=max([len(list(g)) for val,g in itertools.groupby(event[:,c]) if val] or [0])
        assert direct==longest[c]
    pd.DataFrame(dict(duration_days=durations,area_pct_run_at_least_duration=exceed)).to_csv(OUT/'run_exceedance.csv',index=False)
    fig=plt.figure(figsize=(14,7),layout='constrained');gs=fig.add_gridspec(1,3,width_ratios=[2.6,.65,1.5])
    ax=fig.add_subplot(gs[0]);ax.imshow(event[:,chosen].T,cmap=ListedColormap(['#eef2f4','#b83d33']),aspect='auto',interpolation='nearest',vmin=0,vmax=1)
    ax.set_xticks([0,31,62,91],['Jul 1','Aug 1','Sep 1','Sep 30']);ax.set(xlabel='Date in 2023',ylabel='Selected cells, ordered by longest run',title=f'A  Same total: {k} hot/dry days at every row')
    ax.set_yticks([0,len(chosen)-1],[f'Shortest ({longest[chosen[0]]} days)',f'Longest ({longest[chosen[-1]]} days)'])
    ax2=fig.add_subplot(gs[1]);ax2.barh(np.arange(len(chosen)),longest[chosen],color='#b83d33',height=.8);ax2.invert_yaxis();ax2.set(yticks=[],xlabel='Days',title='Longest run');ax2.set_ylim(len(chosen)-.5,-.5)
    ax3=fig.add_subplot(gs[2]);ax3.step(durations,exceed,where='post',color='#007c86',lw=2)
    ax3.set(xlabel='Minimum run length (days)',ylabel='% of full sampled area',title='B  How widespread are long runs?',xlim=(1,70));ax3.grid(alpha=.2)
    fig.suptitle('Equal event counts can hide very different sequences',fontsize=18,fontweight='bold')
    fig.supxlabel(f'Red: Tmax >=35 C and rain <1 mm. A: {len(chosen)} of {len(members)} cells in one exact-count group; equal rows are not equal area. B: all 13,416 cells, cosine-latitude weighted.',fontsize=10)
    stats=dict(same_total_days=int(k),group_cells=len(members),displayed_cells=len(chosen),minimum_run=int(longest[members].min()),maximum_run=int(longest[members].max()),area_at_least_7_days=float(exceed[6]),area_at_least_30_days=float(exceed[29]),area_at_least_60_days=float(exceed[59]))
    METRICS['sequences']=stats
    finding=f"Among {len(members)} cells with exactly {k} hot/dry days, longest runs range from {stats['minimum_run']} to {stats['maximum_run']} days. Across the entire footprint, {exceed[29]:.2f}% of area has a run of at least 30 days and {exceed[59]:.2f}% has a run of at least 60 days."
    save(fig,'event_sequences','Event-sequence raster and run exceedance','Can the same event frequency conceal isolated days versus a prolonged spell?',
         'A lasagna-style binary raster preserves daily order for a deliberately chosen equal-count group. Adjacent bars give exact longest runs. The second panel supplies an all-domain area denominator so selected examples cannot imply prevalence.',finding,
         'The example group maximizes the range of longest runs among exact-count groups with at least 20 cells and at least 10 hot/dry days. It is illustrative, not representative; up to 60 rows are sampled evenly by run rank. Boundary runs are truncated by July-September. Daily hot/dry conditions are descriptive, not official heatwave or drought diagnoses.',
         'Useful addition to Figure 29, but do not discard its spatial maps or threshold sensitivity. Prefer a companion figure or a redesigned composite over replacing a required plot.',
         'https://pmc.ncbi.nlm.nih.gov/articles/PMC2937254/')

def main():
    raincloud();weather=load_weather();rainfall(*weather);sequences(*weather)
    (OUT/'metrics.json').write_text(json.dumps(METRICS,indent=2))
    (OUT/'manifest.json').write_text(json.dumps(CARDS,indent=2))
    cards=[]
    for c in CARDS:
        cards.append('<section><h2>'+html.escape(c['title'])+'</h2><a href="'+c['key']+'.png"><img src="'+c['key']+'.png"></a>'+''.join('<p><b>'+label+':</b> '+html.escape(c[key])+'</p>' for label,key in [('Question','question'),('How to read','reading'),('New evidence','finding'),('Limits','limits'),('Replacement decision','replacement')])+'<p><a href="'+c['source']+'">Research source</a> | <a href="'+c['key']+'.svg">Vector figure</a></p></section>')
    (OUT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Research beyond the slides</title><style>body{max-width:1250px;margin:40px auto;padding:0 24px;font:17px/1.6 system-ui;color:#193044}img{max-width:100%}section{border-top:1px solid #bbcbd6;padding:25px 0}h1,h2{line-height:1.2}</style><h1>What do averages and snapshots hide?</h1><p>Three research-informed candidates tested on our actual data. These are previews; the 25-page report is unchanged. The strongest replacement is the rainfall total + concentration comparison.</p>'+''.join(cards)+'</html>',encoding='utf-8')
    print(json.dumps(METRICS,indent=2))

if __name__=='__main__':main()
