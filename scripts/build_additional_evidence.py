"""Two added report figures; all original 30 figures remain in place."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from build_infovis_data import PROFILE

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/additional_evidence'

def save(fig,key):
    for ext in ['png','svg']:fig.savefig(OUT/f'{key}.{ext}',dpi=230,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def country():
    df=pd.read_csv(ROOT/'data/processed/master_dataset_countries_only.csv')
    df=df.loc[df.year.eq(2020)].dropna(subset=['code']+PROFILE).sort_values('code').reset_index(drop=True)
    x=df[PROFILE].to_numpy(float);z=(x-x.mean(0))/x.std(0);ii,jj=np.triu_indices(len(df),1)
    delta=np.abs(x[ii]-x[jj]);dz=np.abs(z[ii]-z[jj]);sim=1/(1+np.linalg.norm(dz,axis=1))
    threshold=json.loads((ROOT/'data/country_network_2020.json').read_text())['default_threshold']
    close=delta[:,0]<=1;indices=np.flatnonzero(close);infra=np.linalg.norm(dz[:,1:],axis=1)
    ordered=sorted(indices,key=lambda k:(infra[k],str(df.loc[ii[k],'code']),str(df.loc[jj[k],'code'])))
    selected=[ordered[0],ordered[len(ordered)//2],ordered[-1]]
    rows=[]
    for k in indices:
        row=dict(country_a=df.loc[ii[k],'entity'],country_b=df.loc[jj[k],'entity'],code_a=df.loc[ii[k],'code'],code_b=df.loc[jj[k],'code'],internet_gap_pp=delta[k,0],infrastructure_distance=infra[k],similarity=sim[k],retained=bool(sim[k]>=threshold),selected=bool(k in selected))
        row.update({f'absolute_gap_{f}':delta[k,j] for j,f in enumerate(PROFILE)})
        rows.append(row)
    pd.DataFrame(rows).to_csv(OUT/'similar_adoption_pairs.csv',index=False)
    fig,(ax,bx)=plt.subplots(1,2,figsize=(14,3.7),gridspec_kw={'width_ratios':[1,1.5]},layout='constrained')
    bins=np.linspace(0,infra[indices].max()+.001,19)
    ax.hist([infra[indices[sim[indices]>=threshold]],infra[indices[sim[indices]<threshold]]],bins=bins,stacked=True,color=['#087f83','#c5cfd6'],label=['Pass four-indicator P95','Below cutoff'])
    ax.set(xlabel='Distance across three standardized infrastructure indicators',ylabel='Country pairs',title=f'A  {len(indices)} pairs within 1 percentage point online')
    ax.legend(frameon=False,fontsize=8);ax.spines[['top','right']].set_visible(False)
    values=dz[selected,1:];im=bx.imshow(values,vmin=0,vmax=max(values.max(),1),cmap='YlGnBu',aspect='auto')
    labels=[]
    for r,k in enumerate(selected):
        labels.append(f'{["Minimum","Middle-ranked","Maximum"][r]} distance\n{df.loc[ii[k],"entity"]} / {df.loc[jj[k],"entity"]}\nInternet gap {delta[k,0]:.2f} pp')
        for c in range(3):bx.text(c,r,f'{delta[k,c+1]:.1f}',ha='center',va='center',fontsize=12,color='white' if values[r,c]>values.max()*.55 else '#102638')
    bx.set_yticks(range(3),labels,fontsize=8);bx.set_xticks(range(3),['Landlines','Fixed broadband','Mobile']);bx.tick_params(length=0)
    bx.set_title('B  Actual gaps for three reproducibly selected pairs',fontsize=11)
    fig.colorbar(im,ax=bx,shrink=.8,label='Absolute gap in standard deviations')
    fig.supxlabel('Same 179 complete countries in 2020. Cell labels: absolute subscription gaps per 100 people; colour: standardized gaps.\nThree examples are minimum, middle-ranked and maximum infrastructure distance among the 454 eligible pairs.',fontsize=9)
    save(fig,'similar_adoption_infrastructure')
    return dict(eligible_pairs=len(indices),retained_pairs=int((sim[indices]>=threshold).sum()),examples=[rows[list(indices).index(k)] for k in selected])

def longest(sequence):
    best=run=0
    for bit in sequence:run=run+1 if bit else 0;best=max(best,run)
    return best

def weather():
    from research_plot_candidates import load_weather
    arrays,valid,weights,lat,lon,dates=load_weather()
    event=(arrays[0][:,valid]>=35)&(arrays[1][:,valid]<1)
    counts=event.sum(0);runs=np.array([longest(event[:,j]) for j in range(event.shape[1])])
    yy,xx=np.meshgrid(lat,lon,indexing='ij');lats=yy[valid];lons=xx[valid]
    # Find the count class having the largest observed run-length contrast.
    choices=[]
    for count in np.unique(counts):
        members=np.flatnonzero(counts==count)
        if count>0 and len(members)>1:
            low=members[np.argmin(runs[members])];high=members[np.argmax(runs[members])]
            choices.append((int(runs[high]-runs[low]),-int(count),int(low),int(high)))
    spread,_,a,b=max(choices,key=lambda q:(q[0],q[1],-q[2],-q[3]))
    maximum=int(np.argmax(runs));chosen=[a,b]
    if maximum not in chosen:chosen.append(maximum)
    labels=[];rows=[]
    for j in chosen:
        labels.append(f'{lats[j]:.2f} N, {abs(lons[j]):.2f} W\n{counts[j]} / 92 days ({100*counts[j]/92:.1f}%) | longest {runs[j]} days')
        for day,date in enumerate(dates):rows.append(dict(lat=lats[j],lon=lons[j],date=str(date),hot_dry=int(event[day,j]),event_days=int(counts[j]),longest_run=int(runs[j])))
    pd.DataFrame(rows).to_csv(OUT/'daily_event_calendar.csv',index=False)
    fig,ax=plt.subplots(figsize=(14,3.2),layout='constrained')
    ax.imshow(event[:,chosen].T,cmap=ListedColormap(['#edf0f2','#d05a2b']),vmin=0,vmax=1,aspect='auto',interpolation='nearest')
    ax.set_yticks(range(len(chosen)),labels,fontsize=10)
    ticks=[0,15,31,46,62,77,91]
    ax.set_xticks(ticks,[str(dates[k])[5:] for k in ticks]);ax.set_xlabel('Date in 2023; each cell is one grid cell on one day')
    ax.set_xticks(np.arange(-.5,92,1),minor=True);ax.grid(which='minor',axis='x',color='white',lw=.3);ax.tick_params(which='minor',length=0)
    for boundary in [30.5,61.5]:ax.axvline(boundary,color='#18374a',lw=1.5)
    ax.set_title('The same number of hot-dry days can form very different runs',fontsize=17,weight='bold')
    fig.supxlabel('Orange: Tmax >= 35 C and rain < 1 mm/day; gray: condition absent, not missing. All selected cells have complete records.\nFirst two rows maximize the run-length contrast among cells with the same event-day count. The global maximum run is included.',fontsize=9)
    save(fig,'daily_event_calendar')
    return dict(event_days=int(counts[a]),short_run=int(runs[a]),long_run=int(runs[b]),maximum_run=int(runs[maximum]),selected_cells=[dict(lat=float(lats[j]),lon=float(lons[j]),days=int(counts[j]),run=int(runs[j])) for j in chosen],selection_rule='Maximize longest-run difference among positive equal-count classes; break ties by lower count then earlier flattened cell index. Append first cell with global maximum run if absent.')

def entries():
    facts=json.loads((OUT/'facts.json').read_text());c=facts['country'];w=facts['weather']
    return [dict(figure=31,number=31,title='Similar adoption can hide different infrastructure.',path='output/additional_evidence/similar_adoption_infrastructure.png',supporting=False,wide=True,chart_export=True,proposed_part='A',extension_key='similar_adoption_pairs',
        explanation=['How much can infrastructure differ when internet-use rates almost match?',
        'Panel A counts pairs within one percentage point in internet use. Panel B shows three pairs selected by minimum, middle-ranked and maximum infrastructure distance. Labels give absolute subscription gaps per 100 people; colour gives standardized gaps.',
        'This links an almost equal headline rate to the infrastructure detail it conceals. The histogram retains all eligible pairs, while the examples make the gaps tangible.',
        'Pairs share countries and are not independent observations. Standardized distances depend on the chosen features; the examples are illustrative, not representative samples.',
        'Of 454 pairs with almost equal internet-use rates, only 71 meet the four-indicator network cutoff. Similar adoption therefore need not mean similar infrastructure.'],
        detailed_interpretation='The 179 complete profiles yield 454 pairs whose internet-use rates differ by at most one percentage point. Only 71 meet the original P95 similarity cutoff; 383 do not. Bhutan and Turkey differ by 0.82 points in internet use but 19.0 broadband subscriptions per 100 people. The horizontal axis uses only landline, broadband and mobile differences, scaled by the same 179-country standard deviations. The examples span the observed range; subscription counts may exceed 100 per 100 people. This descriptive comparison establishes neither significance nor infrastructure causes.'),
        dict(figure=32,number=32,title='Daily event order separates frequency from persistence.',path='output/additional_evidence/daily_event_calendar.png',supporting=False,wide=True,chart_export=True,proposed_part='B',extension_key='event_calendar',
        explanation=['Can equal event frequencies hide different uninterrupted spells?',
        'Rows are named grid cells; columns are all 92 days. Orange marks hot-dry conditions and gray their absence. Row labels give event-day counts and longest runs; vertical lines separate months.',
        'Maps show where frequency and persistence occur. The calendar reveals the daily ordering that creates their difference.',
        'The first pair deliberately maximizes the contrast among equal-count cells; it is not a typical sample. Runs may extend beyond the observed dates.',
        f'Two cells each have {w["event_days"]} hot-dry days, yet their longest runs are {w["short_run"]} and {w["long_run"]} days. Frequency alone cannot recover duration.'],
        detailed_interpretation=f'The first two cells each meet the condition on {w["event_days"]} of 92 days ({100*w["event_days"]/92:.1f}%), but those days form longest runs of {w["short_run"]} and {w["long_run"]} days. Their different orange sequences make the lost ordering visible. The final row locates the full-footprint maximum of {w["maximum_run"]} consecutive days in time. Selection searches all 13,416 complete cells, using an explicit tie rule recorded with the data. This supports the main question: even an exact event count hides whether conditions are scattered or sustained.')]

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    baseline=OUT/'original_figure_paths.json'
    if not baseline.exists():
        original=json.loads((ROOT/'data/current_figure_manifest.json').read_text())
        baseline.write_text(json.dumps([dict(figure=f['figure'],path=f['path']) for f in original if f['figure']<=30],indent=2))
    facts=dict(country=country(),weather=weather())
    (OUT/'facts.json').write_text(json.dumps(facts,indent=2))
    (OUT/'manifest.json').write_text(json.dumps(entries(),indent=2))
    print(json.dumps(facts,indent=2))

if __name__=='__main__':build()
