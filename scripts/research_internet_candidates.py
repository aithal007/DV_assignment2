"""Internet-specific research previews; no report replacement or renumbering."""
from pathlib import Path
import json,html
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/internet_research'
OUT.mkdir(parents=True,exist_ok=True)
REGIONS=['Africa','Asia','Europe','North America','South America','Oceania']
COLORS=['#0072b2','#d55e00','#009e73','#aa5599','#886633','#6755a0']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
CARDS=[];METRICS={}

def finish(fig,key,title,question,meaning,reading,limits,recommendation,sources):
    for ext in ['png','svg']:fig.savefig(OUT/f'{key}.{ext}',dpi=210,bbox_inches='tight')
    plt.close(fig)
    CARDS.append(dict(key=key,title=title,question=question,meaning=meaning,reading=reading,limits=limits,recommendation=recommendation,sources=sources))

def panel():
    raw=pd.read_csv(ROOT/'data/internet_panel_2000_2020.csv')
    x=raw.pivot(index='code',columns='year',values='internet_users_share_pct').loc[:,2000:2020].dropna()
    meta=raw.drop_duplicates('code').set_index('code').loc[x.index]
    assert x.shape==(159,21)
    return x,meta

def inequality(x,meta):
    rows=[]
    for year in x:
        v=x[year].to_numpy();mean=v.mean();mad=np.abs(v[:,None]-v[None,:]).mean();gini=mad/(2*mean)
        ordered=np.sort(v);n=len(v)
        assert np.isclose(gini,(2*np.sum(np.arange(1,n+1)*ordered)/(n*ordered.sum()))-(n+1)/n)
        # Decompose only classified countries; retain the explicit 158-country denominator.
        classified=meta.region.isin(REGIONS);d=pd.DataFrame(dict(value=x.loc[classified,year],region=meta.loc[classified,'region']))
        mu=d.value.mean();variance=d.value.var(ddof=0);between=0;within=0
        for _,group in d.groupby('region'):
            between+=len(group)/len(d)*(group.value.mean()-mu)**2
            within+=len(group)/len(d)*group.value.var(ddof=0)
        assert len(d)==158 and np.isclose(variance,between+within)
        rows.append(dict(year=int(year),mean=mean,mean_pairwise_gap=mad,gini=gini,p90_p10=float(np.ptp(np.quantile(v,[.1,.9]))),within_variance=within,between_variance=between,between_share=between/variance*100))
    df=pd.DataFrame(rows);df.to_csv(OUT/'inequality_annual.csv',index=False)
    first=df.iloc[0];last=df.iloc[-1];peak=df.loc[df.mean_pairwise_gap.idxmax()]
    fig,axs=plt.subplots(1,3,figsize=(15,5.4),layout='constrained')
    axs[0].plot(df.year,df.mean_pairwise_gap,color='#d55e00',lw=2.5)
    axs[0].set(title='A  Absolute differences',ylabel='Mean pairwise adoption gap (percentage points)',ylim=(0,40))
    axs[1].plot(df.year,df.gini,color='#0072b2',lw=2.5)
    axs[1].set(title='B  Relative inequality',ylabel='Gini coefficient of country adoption rates',ylim=(0,1))
    axs[2].stackplot(df.year,df.within_variance,df.between_variance,colors=['#a4c9c4','#695b94'],labels=['Within regions','Between region means'])
    axs[2].set(title='C  Where variation lies',ylabel='Adoption variance (percentage points squared)')
    axs[2].legend(frameon=False,loc='upper left')
    for ax,col in zip(axs[:2],['mean_pairwise_gap','gini']):
        for r in [first,last]:ax.annotate(f'{r[col]:.2f}',(r.year,r[col]),xytext=(0,10),textcoords='offset points',ha='center',fontweight='bold')
    for ax in axs:ax.set_xticks([2000,2005,2010,2015,2020]);ax.set_xlabel('Year');ax.grid(alpha=.15)
    fig.suptitle('Did the digital divide narrow? The measure changes the answer',fontsize=18,fontweight='bold')
    fig.supxlabel('A-B: fixed 159-country panel, equal country weights. C: 158 classified countries in six regions; variance partition is descriptive, not causal.',fontsize=10)
    meaning=f"Mean pairwise adoption gaps rise from {first.mean_pairwise_gap:.2f} to {last.mean_pairwise_gap:.2f} points, peaking at {peak.mean_pairwise_gap:.2f} in {int(peak.year)}. Yet the Gini falls from {first.gini:.3f} to {last.gini:.3f}. In the 158-country classified panel, between-region means account for {last.between_share:.1f}% of 2020 variance; the remaining {100-last.between_share:.1f}% is within regions."
    METRICS['inequality']=dict(start=first.to_dict(),end=last.to_dict(),absolute_peak=peak.to_dict())
    finish(fig,'inequality_lenses','Absolute, relative and regional inequality','Can progress reduce relative inequality while absolute gaps remain wide?',meaning,
        'Panel A averages absolute differences over all ordered country pairs (including self-pairs). Panel B divides that quantity by twice mean adoption. Panel C partitions population variance into country-count-weighted within-region variation and variation of region means.',
        'This applies inequality measures to national adoption percentages, not income and not individual internet access. Each country has equal weight. High adoption is bounded at 100%; the baseline mean is small. Different measures legitimately answer different questions. Region labels do not establish causes. One unclassified country is excluded only from panel C.',
        'Highest-priority internet enhancement: combine this with Figure 10 or use two panels beside its quantile comparison. It prevents a one-sided conclusion that all forms of inequality increased.',
        ['https://databank.worldbank.org/metadataglossary/environment-social-and-governance-%28esg%29-data/series/SI.POV.GINI','https://www.itl.nist.gov/div898/handbook/prc/section4/prc431.htm'])

def associations():
    raw=pd.read_json(ROOT/'data/infovis_countries.json');a=raw[raw.year==2015].set_index('code');b=raw[raw.year==2020].set_index('code')
    codes=a.index.intersection(b.index);a=a.loc[codes];b=b.loc[codes];assert len(codes)==175
    fields=['broadband_subs_per100','mobile_subs_per100'];adopt='internet_users_share_pct'
    groups=['All countries']+REGIONS+['Unclassified'];rows=[]
    fig,axes=plt.subplots(1,2,figsize=(13,6.8),sharey=True,layout='constrained')
    for j,field in enumerate(fields):
        for i,region in enumerate(groups):
            mask=np.ones(len(b),bool) if i==0 else (b.region==region).to_numpy();n=int(mask.sum())
            level=float(spearmanr(b.loc[mask,field],b.loc[mask,adopt]).statistic)
            change=float(spearmanr(b.loc[mask,field]-a.loc[mask,field],b.loc[mask,adopt]-a.loc[mask,adopt]).statistic)
            assert np.isclose(level,b.loc[mask,[field,adopt]].rank().corr().iloc[0,1])
            rows.append(dict(region=region,n=n,indicator=field,rho_2020=level,rho_changes=change))
            axes[j].plot([level,change],[i,i],color='#bac5cc',lw=2)
            axes[j].scatter(level,i,facecolors='none',edgecolors='#0072b2',linewidths=2,s=105,marker='o',label='2020 levels' if i==0 else None)
            axes[j].scatter(change,i,color='#d55e00',s=65,marker='D',label='2015-2020 changes' if i==0 else None)
        axes[j].axvline(0,color='#999',lw=1,ls=':');axes[j].set(xlim=(-1.07,1.07),xlabel='Spearman rank correlation with adoption',title=['Broadband subscriptions / 100','Mobile subscriptions / 100'][j]);axes[j].grid(axis='x',alpha=.15);axes[j].legend(loc='upper center',bbox_to_anchor=(.5,-.12),ncol=2,frameon=False)
    ns=[175]+[int((b.region==r).sum()) for r in groups[1:]]
    axes[0].set_yticks(range(len(groups)),[f'{r} (n={n})'+(' *' if n<10 else '') for r,n in zip(groups,ns)]);axes[0].invert_yaxis()
    fig.suptitle('An overall relationship is not the same relationship everywhere',fontsize=17,fontweight='bold')
    fig.supxlabel('Identical 175 matched countries. Points are descriptive coefficients, not estimates with confidence intervals. * Very small groups: exploratory only.',fontsize=10)
    df=pd.DataFrame(rows);df.to_csv(OUT/'regional_correlations.csv',index=False)
    b.assign(internet_gain=b[adopt]-a[adopt],broadband_gain=b[fields[0]]-a[fields[0]],mobile_gain=b[fields[1]]-a[fields[1]]).to_csv(OUT/'matched_countries.csv')
    overall=df[(df.region=='All countries')&(df.indicator==fields[0])].iloc[0]
    europe=df[(df.region=='Europe')&(df.indicator==fields[1])].iloc[0]
    METRICS['associations']=rows
    meaning=f"Pooled broadband/adoption correlation is {overall.rho_2020:.3f} for 2020 levels but {overall.rho_changes:.3f} for changes. Europe's mobile/adoption level correlation is {europe.rho_2020:.3f}; the regional rows show which associations survive disaggregation and which do not."
    finish(fig,'regional_associations','Pooled and regional association contrast','Does a pooled infrastructure relationship also describe regions and changes?',meaning,
        'Blue circles correlate 2020 country levels; orange diamonds correlate each country\'s five-year changes. Gray segments connect two different descriptive summaries for the same cohort, not a time trajectory or uncertainty interval.',
        'Correlations do not identify infrastructure effects, direction of causation or omitted variables. Restricted regional ranges and small group sizes affect coefficients. A different magnitude is not automatically Simpson\'s paradox. No significance testing or uncertainty claim is made; raw scatterplots remain necessary for shape/outliers.',
        'Strong companion to Figures 6-7: use a compact version to make the existing level-versus-change conclusion regional. Do not replace the SPLOM entirely, because a correlation summary hides shape.',
        ['https://pmc.ncbi.nlm.nih.gov/articles/PMC3740239/'])

def milestones(x,meta):
    years=np.array(x.columns);rows=[];first_rows=[]
    fig,axes=plt.subplots(1,2,figsize=(13,5.8),sharey=True,layout='constrained')
    for ax,threshold in zip(axes,[50,75]):
        for r,c in zip(REGIONS,COLORS):
            sub=x[meta.region==r];ever=np.maximum.accumulate(sub.to_numpy()>=threshold,axis=1)
            curve=ever.mean(0)*100
            assert np.all(np.diff(curve)>=0)
            ax.step(years,curve,where='post',color=c,lw=2,label=f'{r} (n={len(sub)})')
            rows.extend(dict(region=r,threshold=threshold,year=int(y),countries=len(sub),ever_reached_pct=float(v)) for y,v in zip(years,curve))
            for code,values in sub.iterrows():
                attained=years[values.to_numpy()>=threshold]
                first_rows.append(dict(code=code,region=r,threshold=threshold,first_observed_year=int(attained[0]) if len(attained) else '',not_observed_by_2020=not len(attained),already_reached_at_start=bool(len(attained) and attained[0]==2000)))
        ax.set(title=f'Ever observed at or above {threshold}% adoption',xlabel='Year',ylim=(0,105),xticks=[2000,2005,2010,2015,2020]);ax.grid(alpha=.15)
    axes[0].set_ylabel('% of fixed regional country panel')
    fig.legend(*axes[0].get_legend_handles_labels(),loc='outside lower center',ncol=3,frameon=False)
    fig.suptitle('The regional median hides how long countries wait to reach milestones',fontsize=17,fontweight='bold')
    df=pd.DataFrame(rows);df.to_csv(OUT/'milestone_curves.csv',index=False);pd.DataFrame(first_rows).to_csv(OUT/'country_milestone_years.csv',index=False)
    end=df[(df.year==2020)&(df.threshold==75)];METRICS['milestones_75_2020']=end.to_dict('records')
    meaning='By 2020, the share ever observed at 75% adoption is '+', '.join(f'{r.region}: {r.ever_reached_pct:.1f}%' for r in end.itertuples())+'.'
    finish(fig,'milestone_timing','Adoption milestone attainment curves','Who reached majority and high adoption early, late, or not within the observed period?',meaning,
        'Each step is the cumulative share of a fixed regional panel ever observed at or above the threshold. A country counts after its first qualifying annual value, even if adoption later declines. Two thresholds test dependence on the chosen milestone.',
        '158 classified countries, one unclassified country excluded. These are empirical cumulative attainment curves, not Kaplan-Meier estimates or modelled hazards. Annual sampling misses within-year crossing times. Countries qualifying in 2000 may have crossed earlier; those not qualifying by 2020 may cross later. Reaching a milestone does not guarantee sustained access or population-wide equality.',
        'Useful temporal companion, but lower priority than the inequality and association views: horizons already show trajectories. Prefer this to another snapshot when milestone timing is the chosen question.',
        ['https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/ecdfplot.htm'])

def main():
    x,meta=panel();inequality(x,meta);associations();milestones(x,meta)
    (OUT/'metrics.json').write_text(json.dumps(METRICS,indent=2));(OUT/'manifest.json').write_text(json.dumps(CARDS,indent=2))
    cards=[]
    for c in CARDS:
        cards.append('<section><h2>'+html.escape(c['title'])+'</h2><a href="'+c['key']+'.png"><img src="'+c['key']+'.png"></a>'+''.join('<p><b>'+label+':</b> '+html.escape(c[k])+'</p>' for label,k in [('Question','question'),('New evidence','meaning'),('How to read','reading'),('Limits','limits'),('Report decision','recommendation')])+'<p>'+ ' | '.join('<a href="'+u+'">Method/context source</a>' for u in c['sources'])+'</p></section>')
    (OUT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Internet research plots</title><style>body{font:17px/1.6 system-ui;max-width:1250px;margin:40px auto;padding:0 24px;color:#193044}img{max-width:100%}section{padding:25px 0;border-top:1px solid #bccbd6}h1,h2{line-height:1.2}</style><h1>Internet: what do averages and snapshots hide?</h1><p>Three new internet-specific trials. Start with the absolute/relative inequality comparison. Current 25-page PDF unchanged.</p><p><a href="../research_candidates/regional_gain_raincloud.png">Also see the regional gain raincloud</a></p>'+''.join(cards)+'</html>',encoding='utf-8')
    print(json.dumps(METRICS,indent=2))

if __name__=='__main__':main()
