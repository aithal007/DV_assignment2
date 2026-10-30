"""Readable replacements for report Figures 1, 3-5, 7, 11 and 29."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from matplotlib.colors import ListedColormap
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/simple_revision'
OUT.mkdir(exist_ok=True,parents=True)
INK='#18364c';TEAL='#168a8a';ORANGE='#d66a2c'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
METRICS={}
def save(fig,key):
    for ext in ['png','svg']:fig.savefig(OUT/f'{key}.{ext}',dpi=220,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def network():
    from network_threshold_revision import draw_layouts
    draw_layouts()

def nodetrix():
    from network_threshold_revision import draw_nodetrix
    METRICS['nodetrix']=draw_nodetrix()

def pcp():
    data=pd.read_json(ROOT/'data/infovis_countries.json')
    codes=set(data[data.year.eq(2015)].code)&set(data[data.year.eq(2020)].code)
    whole=data[data.year.eq(2020)&data.code.isin(codes)]
    selected=whole[whole.internet_users_share_pct.ge(70)&whole.broadband_subs_per100.le(5)].sort_values('country')
    fields=['internet_users_share_pct','telephone_lines_per100','broadband_subs_per100','mobile_subs_per100']
    labels=['People using\nthe internet (%)','Landline subscriptions\nper 100 people','Fixed broadband subscriptions\nper 100 people','Mobile subscriptions\nper 100 people']
    domains=np.array([100,25,5,180])
    colors=['#0072b2','#d55e00','#009e73','#aa5599','#9a7100','#6655a0']
    # Bundle toward regional centers computed from the complete matched 2020 view.
    centers=selected.groupby('region')[fields].mean()/domains
    for bundled,key in [(False,'pcp_six_straight'),(True,'pcp_six_bundled')]:
        fig,ax=plt.subplots(figsize=(14,6.3))
        for i,(label,top) in enumerate(zip(labels,domains)):
            ax.plot([i,i],[0,1],color='#607887',lw=1)
            for v in [0,top/2,top]:
                ax.plot([i-.025,i+.025],[v/top,v/top],color='#607887',lw=.8)
                ax.text(i-.04,v/top,f'{v:g}',ha='right',va='center',fontsize=13)
            ax.text(i,1.085,label,ha='center',va='bottom',fontsize=14,weight='bold')
        for color,row in zip(colors,selected.itertuples()):
            values=np.array([getattr(row,k) for k in fields])/domains
            if not bundled:ax.plot(range(4),values,color=color,lw=2.2,marker='o',ms=5)
            else:
                vertices=[(0,values[0])];commands=[MPath.MOVETO]
                for i in range(3):
                    mid=i+.5;ym=.5*((values[i]+values[i+1])/2)+.5*float((centers.loc[row.region].iloc[i]+centers.loc[row.region].iloc[i+1])/2)
                    vertices += [(i+.325,values[i]),(mid-.06,ym),(mid,ym),(mid+.06,ym),(i+.675,values[i+1]),(i+1,values[i+1])]
                    commands += [MPath.CURVE4]*6
                ax.add_patch(PathPatch(MPath(vertices,commands),fill=False,color=color,lw=2.2))
                ax.scatter(range(4),values,color=color,s=24,zorder=4)
        # Stable labels beside the mobile axis use short leaders to avoid overlap.
        positions=sorted([(float(row.mobile_subs_per100/180),i,row.country) for i,row in enumerate(selected.itertuples())])
        adjusted=[]
        for val,i,name in positions:adjusted.append((max(val,adjusted[-1][0]+.07 if adjusted else val),val,i,name))
        for lab,val,i,name in adjusted:
            ax.plot([3.02,3.12],[val,lab],color=colors[i],lw=1)
            ax.text(3.14,lab,name,color=colors[i],fontsize=14,va='center',weight='bold')
        ax.set(xlim=(-.22,3.75),ylim=(-.03,1.18));ax.axis('off')
        fig.suptitle('Six countries are easier to follow than 175 overlapping lines',fontsize=20,weight='bold')
        fig.text(.5,.90,'Same six countries and axis ranges | '+('50% region bundling' if bundled else 'straight lines'),ha='center',fontsize=13)
        fig.text(.5,.035,'Selection: at least 70% internet use and at most 5 fixed broadband subscriptions per 100 people in 2020.\nRead a country’s values at the four dots. The curves between dots add no measurements.',ha='center',fontsize=11)
        fig.subplots_adjust(left=.06,right=.98,top=.80,bottom=.17)
        save(fig,key)
    selected.to_csv(OUT/'pcp_six_values.csv',index=False)
    METRICS['pcp']={'countries':selected.country.tolist(),'complete_view':175,'selected_view':len(selected),'domains':domains.tolist()}

def changes():
    data=pd.read_json(ROOT/'data/infovis_countries.json')
    a=data[data.year.eq(2015)].set_index('code');b=data[data.year.eq(2020)].set_index('code')
    codes=a.index.intersection(b.index);a=a.loc[codes];b=b.loc[codes]
    match=(b.internet_users_share_pct>a.internet_users_share_pct)&(b.telephone_lines_per100<a.telephone_lines_per100)
    rows=[]
    for region in ['All countries','Africa','Asia','Europe','North America','South America','Oceania','Unclassified']:
        mask=np.ones(len(b),bool) if region=='All countries' else b.region.eq(region).to_numpy()
        k=int(match[mask].sum());n=int(mask.sum());rows.append({'region':region,'countries':n,'qualifying':k,'percent':100*k/n})
    out=pd.DataFrame(rows);fig,ax=plt.subplots(figsize=(12.5,6.3))
    ax.barh(range(len(out)),out.percent,color=[INK]+[TEAL]*6+['#9daab2'],height=.56)
    ax.set_yticks(range(len(out)),out.region,fontsize=12);ax.invert_yaxis()
    for i,r in enumerate(out.itertuples()):ax.text(r.percent+1.5,i,f'{r.qualifying} / {r.countries}  ({r.percent:.0f}%)',va='center',fontsize=12)
    ax.set(xlim=(0,118),xticks=[0,25,50,75,100],xlabel='Countries where internet use rose and landline subscriptions fell (%)')
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('Internet use often rose while landline subscriptions fell',fontsize=20,weight='bold')
    fig.text(.5,.90,'2015 to 2020 | the same 175 countries at both dates',ha='center',fontsize=13)
    fig.text(.5,.025,'Each bar counts countries meeting both conditions. Labels show count / group size.\nThis comparison does not show what caused the changes.',ha='center',fontsize=11)
    fig.subplots_adjust(left=.16,right=.98,top=.82,bottom=.18)
    save(fig,'country_changes_simple');out.to_csv(OUT/'country_changes_counts.csv',index=False)
    METRICS['changes']=rows

def pairwise():
    data=pd.read_json(ROOT/'data/infovis_countries.json')
    codes=set(data[data.year.eq(2015)].code)&set(data[data.year.eq(2020)].code)
    d=data[data.year.eq(2020)&data.code.isin(codes)]
    fig,axs=plt.subplots(1,2,figsize=(13,5.3),sharey=True)
    metrics={}
    for ax,key,title,maxx in zip(axs,['broadband_subs_per100','mobile_subs_per100'],['Fixed broadband','Mobile subscriptions'],[60,320]):
        ax.scatter(d[key],d.internet_users_share_pct,s=28,color='#7396a8',alpha=.65,edgecolors='white',lw=.3)
        rho=float(d[[key,'internet_users_share_pct']].rank().corr().iloc[0,1]);metrics[key]=rho
        for code,offset in [('ZAF',(8,-23)),('CHN',(8,-3)),('KWT',(8,7))]:
            row=d[d.code.eq(code)].iloc[0]
            ax.scatter(row[key],row.internet_users_share_pct,s=38,color=ORANGE,zorder=3)
            ax.annotate(row.country,(row[key],row.internet_users_share_pct),xytext=offset,textcoords='offset points',fontsize=11,arrowprops=dict(arrowstyle='-',color=INK,lw=.6))
        ax.set(xlim=(-2,maxx),ylim=(-3,106),xlabel='Subscriptions per 100 people',yticks=[0,25,50,75,100])
        ax.set_title(f'{title}\nRank correlation: {rho:.2f}',loc='left',fontsize=14,weight='bold')
        ax.grid(alpha=.15);ax.set_axisbelow(True)
    axs[0].set_ylabel('People using the internet (%)')
    fig.suptitle('An overall relationship still has country exceptions',fontsize=20,weight='bold')
    fig.text(.5,.02,'Same 175 countries in 2020. Each dot is a country; three examples are named.\nRank correlation describes the overall pattern. It does not show what caused internet use to rise.',ha='center',fontsize=11)
    fig.subplots_adjust(left=.08,right=.97,top=.77,bottom=.22,wspace=.15)
    save(fig,'pairwise_simple');METRICS['pairwise']=metrics

def within_regions():
    data=pd.read_csv(ROOT/'data/internet_panel_2000_2020.csv')
    rows=data[data.year.eq(2020)&data.region.ne('Unclassified')]
    regions=['Africa','Asia','Europe','North America','South America','Oceania']
    fig,(ax,side)=plt.subplots(1,2,figsize=(13,6.1),gridspec_kw={'width_ratios':[3.6,1.4]})
    rng=np.random.default_rng(732)
    stats=[]
    for i,r in enumerate(regions):
        v=rows[rows.region.eq(r)].internet_users_share_pct.to_numpy();med=float(np.mean(v))
        ax.scatter(v,i+rng.uniform(-.13,.13,len(v)),s=28,color=TEAL,alpha=.72)
        ax.plot([med,med],[i-.26,i+.26],color=INK,lw=3)
        stats.append({'region':r,'n':len(v),'mean':med,'median':float(np.median(v)),'minimum':float(v.min()),'maximum':float(v.max())})
    ax.set_yticks(range(6),[f'{r} (n={len(rows[rows.region.eq(r)])})' for r in regions]);ax.invert_yaxis()
    ax.set(xlim=(-2,102),xticks=[0,25,50,75,100],xlabel='People using the internet in 2020 (%)')
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    mu=rows.internet_users_share_pct.mean();means=rows.groupby('region').internet_users_share_pct.transform('mean')
    within=float(((rows.internet_users_share_pct-means)**2).mean());between=float(((means-mu)**2).mean());share=100*within/(within+between)
    side.bar([0],[100],color='#d9e3e7',width=.62);side.bar([0],[share],color=TEAL,width=.62)
    side.text(0,share/2,f'{share:.0f}%\nwithin\nregions',ha='center',va='center',fontsize=14,weight='bold',color='white')
    side.text(0,share+(100-share)/2,f'{100-share:.0f}%\nbetween\nregions',ha='center',va='center',fontsize=13,color=INK)
    side.set(xlim=(-.7,.7),ylim=(0,100),xticks=[],yticks=[]);side.set_title('Where does the\ncountry spread lie?',fontsize=12)
    for spine in side.spines.values():spine.set_visible(False)
    fig.suptitle('A regional average hides differences between its countries',fontsize=20,weight='bold')
    fig.text(.5,.89,'Each dot is a country. The dark tick marks the regional average.',ha='center',fontsize=13)
    fig.text(.5,.02,'158 countries with a region label; equal country weights. The bar splits variance, a measure of spread.\nA region label alone leaves nearly half the measured differences hidden.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.17,right=.98,top=.80,bottom=.17,wspace=.25)
    save(fig,'within_regions');pd.DataFrame(stats).to_csv(OUT/'regional_spread.csv',index=False)
    METRICS['within_regions']={'countries':len(rows),'within_percent':share,'between_percent':100-share,'regions':stats}

def overlap():
    d=pd.read_csv(ROOT/'output/lecture_previews/weather_intersections.csv',dtype={'month':str})
    d=d[d.month.eq('all')]
    vals=[float(d[d[c]].area_day_pct.sum()) for c in ['hot','dry','windy']]
    vals.append(float(d[d.hot&d.dry&d.windy].area_day_pct.iloc[0]))
    names=['Hot','Dry','Windy','All three together']
    fig,ax=plt.subplots(figsize=(12,4.8))
    ax.barh(range(4),vals,color=['#aabec8']*3+[ORANGE],height=.57)
    for i,v in enumerate(vals):ax.text(v+1,i,f'{v:.2f}%',va='center',fontsize=14,weight='bold')
    ax.set_yticks(range(4),names,fontsize=14);ax.invert_yaxis()
    ax.set(xlim=(0,90),xticks=[0,20,40,60,80],xlabel='Share of weighted grid-cell days (%)');ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('Frequent separate conditions can have a much smaller overlap',fontsize=19,weight='bold')
    fig.text(.5,.025,'Hot: daily maximum temperature ≥35°C | Dry: rain <1 mm/day | Windy: daily wind speed ≥5 m/s\nJuly–September 2023. The first three bars overlap and must not be added. “All three” requires all conditions in the same grid cell and day.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.21,right=.97,top=.83,bottom=.24)
    save(fig,'weather_overlap_simple')
    METRICS['overlap']=dict(zip(['hot','dry','windy','all_three'],vals))
    pd.DataFrame({'condition':names,'area_day_percent':vals}).to_csv(OUT/'weather_overlap.csv',index=False)

def build():
    network();nodetrix();pcp();pairwise();changes();within_regions();overlap()
    (OUT/'metrics.json').write_text(json.dumps(METRICS,indent=2),encoding='utf-8')
    print('Built eight simple report figures; numerical tables and metrics saved.')
if __name__=='__main__':build()
