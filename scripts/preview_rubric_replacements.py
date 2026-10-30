"""Approved supporting figures 7 and 10; generate assets without editing the report."""
from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];O=R/'output/proposals_20261026';O.mkdir(exist_ok=True)
protected=[R/'REPORT.md',R/'data/current_figure_manifest.json',R/'output/pdf/DAS732_A2_Report_IEEE.pdf'];before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#244155','text.color':'#17384e','axes.titleweight':'bold','axes.titlesize':12})
rows=pd.DataFrame(json.loads((R/'data/infovis_countries.json').read_text()));codes=set(rows.loc[rows.year==2015,'code'])&set(rows.loc[rows.year==2020,'code']);a=rows[(rows.year==2015)&rows.code.isin(codes)].set_index('code').sort_index();b=rows[(rows.year==2020)&rows.code.isin(codes)].set_index('code').sort_index();assert a.index.equals(b.index) and len(a)==175 and not a.index.duplicated().any()
y='internet_users_share_pct';keys=['broadband_subs_per100','telephone_lines_per100','mobile_subs_per100'];names=['Fixed broadband','Landlines','Mobile'];delta=b[[y,*keys]]-a[[y,*keys]]
metrics=[]
for k,name in zip(keys,names):metrics.append(dict(measure=name,levels=float(b[k].rank().corr(b[y].rank())),gains=float(delta[k].rank().corr(delta[y].rank()))))
pd.DataFrame(metrics).to_csv(O/'fig7_association_values.csv',index=False)
fig,axs=plt.subplots(1,2,figsize=(13.6,5.9),gridspec_kw={'width_ratios':[.92,1.08]});fig.subplots_adjust(left=.12,right=.97,top=.73,bottom=.24,wspace=.40)
ax=axs[0]
for i,m in enumerate(metrics):
 ax.plot([m['gains'],m['levels']],[i,i],color='#c5cdd4',lw=4,zorder=1)
 ax.scatter(m['levels'],i,s=85,color='#307c9a',zorder=3);ax.scatter(m['gains'],i,s=85,color='#d28039',zorder=3)
 ax.annotate(f"{m['levels']:.2f}",(m['levels'],i),xytext=(0,12),textcoords='offset points',ha='center',color='#256582',fontsize=11)
 ax.annotate(f"{m['gains']:.2f}",(m['gains'],i),xytext=(0,-22),textcoords='offset points',ha='center',color='#ad5e22',fontsize=11)
ax.set(yticks=range(3),yticklabels=names,xlim=(-.05,1),ylim=(2.55,-.55),xlabel='Spearman rank correlation',title='A. Relationship with internet use');ax.set_xticks([0,.25,.5,.75,1]);ax.axvline(0,color='#b4c1ca',lw=.8);ax.grid(axis='x',alpha=.12);ax.spines[['left','bottom']].set_visible(False);ax.tick_params(axis='y',length=0)
ax.scatter([],[],s=55,color='#307c9a',label='Country levels, 2020');ax.scatter([],[],s=55,color='#d28039',label='Country gains, 2015–2020');fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.12,.835),frameon=False,fontsize=10,ncol=2)
ax=axs[1];ax.scatter(delta[keys[0]],delta[y],color='#307c9a',alpha=.65,s=29,edgecolors='white',linewidths=.4);ax.axhline(0,color='#8397a5',lw=.7);ax.axvline(0,color='#8397a5',lw=.7);ax.grid(alpha=.12);ax.set(title='B. Check the actual broadband gains',xlabel='Broadband gain (subscriptions / 100 people)',ylabel='Internet-use gain (percentage points)');ax.text(.95,.95,'175 paired countries\nGain correlation: 0.054',transform=ax.transAxes,ha='right',va='top',fontsize=10,bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
fig.suptitle('Do infrastructure gains tell the same story as country levels?',fontsize=17,x=.055,ha='left',y=.97);fig.text(.055,.87,'Same 175 countries in both years. Gains are calculated within each country before comparing countries.',fontsize=11)
fig.text(.055,.045,'TAKEAWAY  Strong level relationships become much weaker for gains. Broadband falls from 0.83 to 0.05.\nA country-level snapshot does not establish how adoption changed, or what caused that change.',fontsize=11,linespacing=1.7)
fig.savefig(O/'recommended_fig7_association_audit.png',dpi=240,facecolor='white');fig.savefig(O/'recommended_fig7_association_audit.svg');plt.close(fig)
# Stable initial cohorts, not fresh quantile memberships each year.
panel=pd.read_csv(R/'data/internet_panel_2000_2020.csv');wide=panel.pivot(index='code',columns='year',values=y).dropna().sort_index();assert len(wide)==159 and list(wide.columns)==list(range(2000,2021));assert ((wide>=0)&(wide<=100)).all().all()
ordered=wide[2000].sort_values(kind='stable').index;cohort=pd.Series(index=wide.index,dtype='int64')
for i,idx in enumerate(np.array_split(ordered,3)):cohort.loc[idx]=i
assert cohort.value_counts().to_dict()=={0.0:53,1.0:53,2.0:53}
# Ensure no tied initial values are split at either tercile boundary.
assert wide.loc[ordered[52],2000]<wide.loc[ordered[53],2000] and wide.loc[ordered[105],2000]<wide.loc[ordered[106],2000]
colors=['#cb7734','#3986a0','#7c63a2'];labels=['Lowest third in 2000','Middle third in 2000','Highest third in 2000'];fig,axs=plt.subplots(1,2,figsize=(13.6,6.5),gridspec_kw={'width_ratios':[1.2,1]});fig.subplots_adjust(left=.075,right=.97,top=.74,bottom=.25,wspace=.35);stats=[]
for i,(color,label) in enumerate(zip(colors,labels)):
 group=wide.loc[cohort==i];med=group.median();q=group[2020].quantile([.25,.75]);stats.append(dict(cohort=label,countries=len(group),median_2000=float(med[2000]),median_2020=float(med[2020]),median_paired_gain=float((group[2020]-group[2000]).median()),q25_2020=float(q.loc[.25]),q75_2020=float(q.loc[.75]),initial_min=float(group[2000].min()),initial_max=float(group[2000].max())))
 axs[0].plot(wide.columns,med,color=color,lw=2.8,label=label);axs[0].scatter([2000,2020],med[[2000,2020]],s=25,color=color)
 axs[0].annotate(f'{med[2020]:.1f}%',(2020,med[2020]),xytext=(7,0),textcoords='offset points',va='center',color=color,fontsize=10)
 vals=group[2020].sort_values().to_numpy();jitter=(np.arange(len(vals))%7-3)*.045;axs[1].scatter(vals,i+jitter,s=22,color=color,alpha=.55,edgecolors='white',linewidths=.3)
 axs[1].plot([q.loc[.25],q.loc[.75]],[i+.29,i+.29],color=color,lw=5,solid_capstyle='round');axs[1].scatter(med[2020],i+.29,s=72,color='white',edgecolors=color,linewidths=2,zorder=4)
axs[0].set(title='A. Follow the same groups over time',xlabel='Year',ylabel='Median internet use (%)',xlim=(2000,2023.5),ylim=(0,100));axs[0].set_xticks([2000,2005,2010,2015,2020]);axs[0].grid(alpha=.13);axs[0].legend(loc='upper left',frameon=False,fontsize=9.5)
axs[1].set(title='B. What each 2020 median hides',xlabel='Internet use in 2020 (%)',yticks=range(3),yticklabels=['Lowest start','Middle start','Highest start'],xlim=(-2,102),ylim=(-.4,2.55));axs[1].grid(axis='x',alpha=.13);axs[1].spines['left'].set_visible(False);axs[1].tick_params(axis='y',length=0)
fig.suptitle('Did countries that started behind catch up?',fontsize=18,x=.055,ha='left',y=.97);fig.text(.055,.88,'159 countries with complete annual data. Split once by 2000 adoption into three groups of 53; membership stays fixed.',fontsize=10.5)
fig.text(.56,.13,'Each dot: one country. Thick bar: middle 50%.\nWhite circle: median. Vertical jitter separates overlapping dots.',fontsize=9.5,linespacing=1.6)
lo,hi=stats[0],stats[2];gap0=hi['median_2000']-lo['median_2000'];gap1=hi['median_2020']-lo['median_2020']
fig.text(.055,.045,f'TAKEAWAY  The lowest-starting group reaches a median of {lo["median_2020"]:.1f}%, versus {hi["median_2020"]:.1f}% for the highest-starting group.\nTheir median gap grows from {gap0:.1f} to {gap1:.1f} percentage points. Some countries still cross over: starting group is not destiny.',fontsize=11,linespacing=1.7)
fig.savefig(O/'recommended_fig10_fixed_cohorts.png',dpi=240,facecolor='white');fig.savefig(O/'recommended_fig10_fixed_cohorts.svg');plt.close(fig)
wide.assign(initial_cohort=cohort.map(dict(enumerate(labels)))).to_csv(O/'fig10_country_cohorts.csv');pd.DataFrame(stats).to_csv(O/'fig10_cohort_summary.csv',index=False)
# Sensitivity to the number of starting groups; same countries, same baseline.
sensitivity=[]
for n in [3,4,5]:
 parts=np.array_split(ordered,n);low=wide.loc[parts[0]].median();high=wide.loc[parts[-1]].median();sensitivity.append(dict(groups=n,initial_gap=float(high[2000]-low[2000]),final_gap=float(high[2020]-low[2020])))
assert all(s['final_gap']>s['initial_gap'] for s in sensitivity)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==before[str(p)] for p in protected)
validation=dict(status='PASS',matched_countries=175,balanced_countries=159,cohort_sizes=[53]*3,no_tied_values_split=True,no_imputation=True,sensitivity=sensitivity,association_metrics=metrics,cohort_metrics=stats,report_unchanged=True)
(O/'rubric_preview_validation.json').write_text(json.dumps(validation,indent=2))
readme='''# Approved replacements — selected for Figures 7 and 10

The assignment rubric allocates 4/30 to completeness, 8/30 to correctness, 8/30 to quality of inferences, and 10/30 to data handling. These supporting figures do not replace any required visualization type. No mark increase is guaranteed.

Figure 7: Association audit. Both cohorts contain exactly the same 175 countries. Country changes are computed after joining on country code. Three level correlations are compared with three change correlations, and the broadband-change scatter shows the underlying observations. Spearman coefficients measure monotone association, not causal effects. The level correlations already appear in Figure 6; this figure's new contribution is the controlled comparison with changes for all three infrastructure measures.

Figure 10: Fixed initial cohorts. The same 159 countries with complete 2000–2020 records are split into thirds only once using 2000 adoption. Each cohort has 53 countries and no boundary ties. Country identities stay fixed. Median paths and 2020 individual values show between-group persistence and within-group exceptions. This complements Figures 15–16, which regroup distributions by year or region. Countries have equal weight; results are not a population-weighted measure of global access. Initial cohorts are descriptive, not natural types or a causal treatment. A larger absolute gap alone does not establish greater relative inequality. The wider median gap also appears with four and five initial groups.

Research: Lakner and Milanovic, World Bank WPS6719, explains why tracking fixed observations adds information beyond comparing anonymous distributions. Our cohort summary is an adaptation of this identity-preserving principle, not a reproduction of an income growth-incidence estimator.
https://documents.worldbank.org/curated/en/914431468162277879/pdf/WPS6719.pdf

Reproduce: python -X utf8 scripts/preview_rubric_replacements.py
The script asserts matching identities, cohort counts, boundary ties, complete data, sensitivity direction, and unchanged report hashes. CSV tables and SVG/PNG previews are alongside this file.
'''
(O/'REPLACEMENT_RECOMMENDATION.md').write_text(readme,encoding='utf-8')
import html
cards=''.join(f'<article><h2>{html.escape(title)}</h2><img src="{name}.png"><p>{html.escape(desc)}</p></article>' for title,name,desc in [('Proposed Figure 7: levels versus gains','recommended_fig7_association_audit','One controlled comparison across three infrastructure measures, with the underlying change data visible.'),('Proposed Figure 10: follow countries that started behind','recommended_fig10_fixed_cohorts','Stable initial cohorts reveal persistence, progress and exceptions without changing group membership.')])
(O/'rubric_previews.html').write_text('<!doctype html><meta charset="utf-8"><title>A2 replacement previews</title><style>body{font:17px Arial;background:#eef3f6;color:#17384e;margin:40px auto;max-width:1300px}article{background:white;padding:24px;margin:24px 0}img{width:100%}p{line-height:1.5}</style><h1>A2 approved replacement figures</h1><p>Approved replacements for Figures 7 and 10. The required A2 methods remain elsewhere.</p>'+cards,encoding='utf-8')
print(json.dumps({'status':'PASS','absolute_cohort_gap':[gap0,gap1],'sensitivity':sensitivity,'output':str(O)},indent=2))
