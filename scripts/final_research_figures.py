"""Build the selected regional composite and detailed final research entries."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/final_research';OUT.mkdir(parents=True,exist_ok=True)

def build():
    raw=pd.read_json(ROOT/'data/infovis_countries.json');a=raw[raw.year==2015].set_index('code');b=raw[raw.year==2020].set_index('code')
    codes=a.index.intersection(b.index);a=a.loc[codes];b=b.loc[codes]
    assert len(codes)==175
    field='internet_users_share_pct';regions=['Africa','Asia','Europe','North America','South America','Oceania','Unclassified']
    colors=['#0072b2','#d55e00','#009e73','#aa5599','#886633','#6755a0','#687787']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,(left,right)=plt.subplots(1,2,figsize=(14,6.4),sharey=True,gridspec_kw={'width_ratios':[1,1.7]},layout='constrained')
    stats=[];rng=np.random.default_rng(732)
    for i,(region,color) in enumerate(zip(regions,colors)):
        mask=b.region==region;old=a.loc[mask,field];new=b.loc[mask,field];gain=(new-old).to_numpy();q=np.quantile(gain,[.25,.5,.75]);m0=float(old.median());m1=float(new.median())
        left.plot([m0,m1],[i,i],color=color,lw=2)
        left.scatter(m0,i,facecolors='white',edgecolors=color,s=55,zorder=4);left.scatter(m1,i,color=color,s=45,zorder=4)
        left.text((m0+m1)/2,i-.16,f'+{m1-m0:.1f}',ha='center',fontsize=9)
        if len(gain)>=10:
            xx=np.linspace(gain.min(),gain.max(),250);dd=gaussian_kde(gain)(xx);right.fill_between(xx,i-.12,i-.12-.32*dd/dd.max(),color=color,alpha=.25)
        right.scatter(gain,i+.18+rng.uniform(-.055,.055,len(gain)),s=17,color=color,alpha=.75)
        right.plot(q[[0,2]],[i,i],color=color,lw=5,solid_capstyle='round');right.scatter(q[1],i,color='white',edgecolor=color,s=50,zorder=4)
        right.scatter(m1-m0,i,marker='|',s=200,color='black',zorder=5)
        stats.append(dict(region=region,n=len(gain),median_2015=m0,median_2020=m1,median_shift=m1-m0,median_gain=float(q[1]),q25=float(q[0]),q75=float(q[2])))
    left.set_yticks(range(7),[f'{r} (n={int((b.region==r).sum())})' for r in regions]);left.invert_yaxis()
    left.set(xlabel='Regional median adoption (%)',xlim=(0,105),title='A  Regional endpoints: 2015 to 2020')
    right.set(xlabel='Individual adoption gain (percentage points)',xlim=(-5,55),title='B  Countries behind each regional change')
    right.axvline(0,color='#888',ls=':',lw=1)
    for ax in [left,right]:ax.grid(axis='x',alpha=.15)
    fig.suptitle('Regional progress and individual country gains are different summaries',fontsize=17,fontweight='bold')
    fig.supxlabel('A: hollow = 2015, filled = 2020; labels give median shift. B: dots = countries; circle/line = median/interquartile range of gains; black tick = median shift.\nFixed 175-country panel. Density shown for n >= 10 only; each row normalized separately. Intervals show spread, not confidence.',fontsize=9)
    for ext in ['png','svg']:fig.savefig(OUT/f'regional_endpoints_gains.{ext}',dpi=220,bbox_inches='tight')
    plt.close(fig);pd.DataFrame(stats).to_csv(OUT/'regional_endpoints_gains.csv',index=False)
    entries={
    'inequality_lenses':dict(title='Absolute and relative inequality through time.',path='output/internet_research/inequality_lenses.png',wide=True,
      caption='The mean pairwise adoption gap rises from 11.43 to 28.78 percentage points, but the Gini falls from 0.708 to 0.222. The absolute gap peaks at 32.86 points in 2013. Within-region differences account for 46.96% of 2020 classified-panel variance.',
      explanation=[
        'Did the digital divide narrow, and does an endpoint comparison hide a turning point?',
        'Panel A shows the mean absolute adoption difference over all ordered pairs of the same 159 countries, including self-pairs. Panel B divides this gap by twice mean adoption to obtain the relative Gini. Panel C stacks the within-region and between-region-mean components of population variance for 158 classified countries. All panels retain every annual observation from 2000 to 2020, but their vertical units differ.',
        'The milestone comparison establishes broad but uneven progress. Annual absolute and relative measures test whether that conclusion applies to other definitions and whether the interval contains a reversal. Variance decomposition tests how much country variation regional means leave hidden.',
        'Countries are equally weighted; this is inequality among national adoption percentages, not an income Gini or a population-weighted access measure. Adoption is bounded by 0 and 100, and its initial mean is small. The one unclassified country is excluded only from panel C. Group decomposition is descriptive, not the causal effect of geography. Within + between equals total variance; it is not a partition of the Gini.',
        'Relative inequality falls while absolute gaps remain wider than in 2000; absolute dispersion nevertheless narrows after its 2013 peak.'],
      detailed_interpretation='The mean pairwise gap increases from 11.43 points in 2000 to 28.78 in 2020, while the Gini declines from 0.708 to 0.222. These results are compatible because average adoption grows faster than the absolute differences. The 32.86-point peak in 2013 adds information absent from two endpoints: absolute gaps have already begun narrowing by 2020. In the classified panel, 53.04% of 2020 variance lies between region means and 46.96% within regions. Regional averages therefore leave almost half this variation hidden. A claim that the digital divide simply grew or shrank would omit the measure, time interval and aggregation level that determine the answer.'),
    'regional_endpoints_gains':dict(title='Regional endpoints and individual-country gains.',path='output/final_research/regional_endpoints_gains.png',wide=True,
      caption='Asia has a 26.55-point difference of regional medians but a 19.75-point median individual country gain. Its middle half of country gains spans 9.86-28.25 points. Both endpoint and gain views use the identical 175-country matched panel.',
      explanation=[
        'Does an increase in a regional median describe the typical matched country\'s improvement?',
        'Panel A preserves the regional dumbbell: hollow circles mark 2015 and filled circles 2020 median adoption, with the difference printed above. Panel B shows each country\'s 2020-minus-2015 gain as a dot. A hollow circle and thick segment show the median and interquartile range of gains; the black tick repeats the difference of regional medians. Density height is normalized within each row and shown only for groups with at least ten countries; jitter is cosmetic.',
        'Combining endpoints with a raincloud retains absolute regional levels while exposing matched-country changes and their spread. It directly distinguishes the difference of two medians from the median of individual differences.',
        'Countries carry equal weight, and subscription/adoption data remain observational. Region sizes differ and small groups cannot support reliable density-shape claims. The interval describes heterogeneity, not uncertainty. Truncated KDE curves stop at observed extremes; raw points are authoritative. Regional label uncertainty remains explicit in the Unclassified row.',
        'A rising regional median can conceal both very small and very large country gains; the typical country gain is a separate statistic.'],
      detailed_interpretation='Asia\'s regional median increases by 26.55 points, the largest shift among the classified regions, but its median individual gain is 19.75 points. The 41 Asian country gains range from -0.84 to 49.94 points, with the middle half between 9.86 and 28.25. South America\'s median individual gain is 21.76 points even though its regional-median shift is only 16.54. Thus the regional ranking depends on whether the question concerns the movement of distributional endpoints or the changes experienced by matched countries. Panel A answers the former, while the dots and intervals in panel B answer the latter. Neither is a population-weighted estimate of how many people gained access.'),
    'rainfall_concentration':dict(title='Monthly rainfall totals and five-day concentration.',path='output/research_candidates/rainfall_concentration.png',wide=True,
      caption='Among cells with monthly rain of at least 10 mm, 43.8% of weighted area in July, 67.5% in August and 77.6% in September receives at least half the monthly rain within one five-day window.',
      explanation=[
        'Do monthly rainfall totals conceal whether rain arrived in a short burst or across many days?',
        'The top row retains July, August and September rainfall sums on one shared millimeter scale. The bottom row divides the largest consecutive five-day rainfall sum by that cell\'s monthly total, on a shared 0-100% scale. Every five-day window stays within its month. Gray cells in the bottom row include monthly totals below 10 mm, masked to avoid large ratios driven by negligible rain.',
        'The paired rows retain absolute volume and add temporal concentration. Unlike another monthly average, the rolling-window ratio directly tests what aggregation over a whole month discards.',
        'This adapts the maximum five-day precipitation idea; it is a within-month diagnostic, not a full climatological Rx5day implementation. Eligible footprints differ by month. Windows crossing a month boundary are excluded. High concentration does not establish flooding, runoff, hourly intensity or a climate anomaly. Minimum-total sensitivity at 1, 10, 25 and 50 mm is supplied.',
        'Monthly totals conceal timing: much of the eligible area receives at least half its rain in five consecutive days, especially in September.'],
      detailed_interpretation='July and August retain similar area-mean totals of 75.26 and 75.82 mm; September is lower at 57.08 mm, but totals alone cannot reveal temporal concentration. With the 10-mm minimum-total rule, the fraction of eligible area receiving at least half its rain in five days is 43.8%, 67.5% and 77.6% respectively. The eligible fractions of the full common footprint are 74.75%, 92.32% and 94.09%, so these conditional percentages are not comparisons of identical subsets. Raising the minimum to 50 mm gives 36.3%, 62.5% and 74.2%, preserving the monthly ordering in this sensitivity check. The bottom maps locate concentrated episodes while the top maps prevent a large ratio being mistaken for a large absolute amount.')
    }
    for k,v in entries.items():v['extension_key']=k
    (OUT/'entries.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
    return entries

if __name__=='__main__':build()
