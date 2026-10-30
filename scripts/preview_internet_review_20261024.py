"""Standalone research previews; does not modify the submission or its figures."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/internet_review_20261024'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.right': False,
    'text.color': '#192c3c', 'axes.labelcolor': '#192c3c', 'svg.fonttype': 'none'})

def save(fig, name):
    for ext in ['png', 'svg']:
        fig.savefig(OUT / f'{name}.{ext}', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)

raw = pd.read_csv(ROOT / 'data/internet_panel_2000_2020.csv')
assert not raw.duplicated(['code', 'year']).any()
x = raw.pivot(index='code', columns='year', values='internet_users_share_pct').loc[:, 2000:2020].dropna()
assert x.shape == (159, 21) and ((x >= 0) & (x <= 100)).all().all()
meta = raw.drop_duplicates('code').set_index('code').loc[x.index]
regions = ['Africa', 'Asia', 'Europe', 'North America', 'South America', 'Oceania', 'Unclassified']
order = meta.assign(region_order=meta.region.map(dict(zip(regions, range(7)))), endpoint=x[2020]).sort_values(['region_order', 'endpoint', 'entity']).index
colors = LinearSegmentedColormap.from_list('adoption', ['#f1f4f4', '#c3e5df', '#72bcb2', '#287e83', '#143c5b'])
fig, axes = plt.subplots(1, 3, figsize=(18, 13))
fig.subplots_adjust(left=.13, right=.96, bottom=.1, top=.88, wspace=.85)
for ax, codes in zip(axes, np.array_split(order.to_numpy(), 3)):
    vals = x.loc[codes]
    im = ax.imshow(vals, aspect='auto', cmap=colors, vmin=0, vmax=100, interpolation='nearest')
    labels = [(f'[{meta.loc[c, "region"]}] ' if i == 0 or meta.loc[codes[i-1], 'region'] != meta.loc[c, 'region'] else '') + meta.loc[c, 'entity'] for i,c in enumerate(codes)]
    ax.set_yticks(range(len(codes)), labels, fontsize=7.5)
    ax.tick_params(axis='y', length=0)
    ax.set_xticks([0,5,10,15,20], ['2000','2005','2010','2015','2020'], fontsize=9)
    ax.xaxis.tick_top()
    for i, c in enumerate(codes):
        ax.text(21, i, f'{vals.loc[c,2020]:.0f}', va='center', fontsize=7.5)
        if i == 0 or meta.loc[codes[i-1], 'region'] != meta.loc[c, 'region']:
            ax.axhline(i-.5, color='white', lw=2)
    ax.text(21, -2.2, 'End %', fontsize=7)
    for spine in ax.spines.values(): spine.set_visible(False)
fig.text(.04,.965,'When did countries come online?',fontsize=24,weight='bold')
fig.text(.04,.933,'159 country trajectories, 2000–2020 | Grouped by region, then ordered by 2020 adoption',fontsize=12)
cax = fig.add_axes([.37,.062,.32,.013])
fig.colorbar(im, cax=cax, orientation='horizontal', ticks=[0,25,50,75,100], label='People using the internet (%)')
fig.text(.04,-.007,'Source: existing A1 OWID/ITU extracts. Same 159 countries in every year; no interpolation. Each row has equal visual weight.\nRead columns top to bottom, then left to right. This complete-case panel is not the entire world population.',fontsize=9)
save(fig, 'adoption_atlas')
raw.set_index('code').loc[order].reset_index().to_csv(OUT/'atlas_values.csv',index=False)

d = pd.read_csv(ROOT/'data/processed/master_dataset_countries_only.csv')
selected = ['IND','ZAF','CHN','BRA','DEU','USA']
part = d[d.code.isin(selected) & d.year.between(2010,2020)].copy()
fields = ['broadband_subs_per100','internet_users_share_pct']
assert not part.duplicated(['code','year']).any()
assert part.groupby('code')[fields].count().eq(11).all().all()
fig, axes = plt.subplots(2,3,figsize=(13,9),sharex=True,sharey=True)
fig.subplots_adjust(left=.08,right=.98,top=.82,bottom=.15,hspace=.44,wspace=.22)
metrics=[]
for ax,code in zip(axes.flat,selected):
    g=part[part.code.eq(code)].sort_values('year')
    a,b=g.iloc[0],g.iloc[-1]
    ax.plot(g[fields[0]],g[fields[1]],'-o',color='#268a8a',lw=2,ms=3)
    ax.scatter(a[fields[0]],a[fields[1]],s=70,facecolors='white',edgecolors='#268a8a',linewidths=2,zorder=4)
    ax.scatter(b[fields[0]],b[fields[1]],s=70,color='#173e5e',zorder=4)
    for r,lab,off in [(a,'2010',(7,0) if a[fields[1]] < 12 else (7,-15)),(b,'2020',(7,7))]:
        ax.annotate(lab,(r[fields[0]],r[fields[1]]),xytext=off,textcoords='offset points',fontsize=9)
    ax.set(xlim=(-2,52),ylim=(0,103),xticks=[0,10,20,30,40,50],yticks=[0,25,50,75,100])
    ax.grid(color='#e5e9ec',lw=.7)
    ax.set_axisbelow(True)
    gain=b[fields[1]]-a[fields[1]]; bgain=b[fields[0]]-a[fields[0]]
    ax.set_title(f'{a.entity}\nAdoption +{gain:.1f} pp | Broadband +{bgain:.1f}/100',loc='left',fontsize=11,pad=10)
    metrics.append({'country':a.entity,'adoption_gain_pp':gain,'broadband_gain_per100':bgain})
fig.text(.055,.955,'Different paths to higher internet adoption',fontsize=23,weight='bold')
fig.text(.055,.915,'Six illustrative countries, 2010–2020. Every dot is an observed year; every panel uses the same scales.',fontsize=11)
fig.supylabel('People using the internet (%)',x=.015,fontsize=11)
fig.supxlabel('Fixed broadband subscriptions per 100 people',y=.09,fontsize=11)
fig.text(.055,.025,'Source: existing A1 OWID/ITU extracts. Cases chosen to illustrate contrasting paths, not a representative sample.\nLines connect annual observations; they do not establish causation or prove mobile substitution. Subscriptions are not unique people.',fontsize=9)
save(fig,'adoption_broadband_paths')
part.to_csv(OUT/'trajectory_values.csv',index=False)
(OUT/'validation.json').write_text(json.dumps({'atlas_countries':len(x),'atlas_years':21,'trajectory_countries':6,'trajectory_years_each':11,'missing_values_imputed':0,'illustrative_changes':metrics},indent=2),encoding='utf-8')
print(OUT)
