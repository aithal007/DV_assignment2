"""Unapproved alternatives only. Does not edit the report or selected manifest."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
R=Path(__file__).resolve().parents[1];O=R/'output/proposals_20261026';O.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#244155','text.color':'#17384e','axes.titleweight':'bold'})
rows=pd.DataFrame(json.loads((R/'data/infovis_countries.json').read_text()));codes=set(rows[rows.year==2015].code)&set(rows[rows.year==2020].code);a=rows[(rows.year==2015)&rows.code.isin(codes)].set_index('code').sort_index();b=rows[(rows.year==2020)&rows.code.isin(codes)].set_index('code').sort_index();delta=b.select_dtypes('number')-a.select_dtypes('number');x='broadband_subs_per100';y='internet_users_share_pct'
fig,axs=plt.subplots(1,2,figsize=(12.8,5.4));fig.subplots_adjust(top=.77,bottom=.23,wspace=.3)
for ax,d,title,xlabel,ylabel in zip(axs,[b,delta],['A. Country levels in 2020','B. Change within each country, 2015–2020'],['Fixed broadband subscriptions / 100 people','Change in broadband subscriptions / 100 people'],['Internet users (% of population)','Change in internet use (percentage points)']):
 ax.scatter(d[x],d[y],s=23,alpha=.65,color='#317b9a',edgecolors='white',linewidths=.3);ax.set(title=title,xlabel=xlabel,ylabel=ylabel);ax.grid(alpha=.13);rho=d[x].rank().corr(d[y].rank());ax.text(.04,.94,f'Spearman rho = {rho:.3f}',transform=ax.transAxes,va='top',bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
axs[1].axhline(0,color='#778b99',lw=.7);axs[1].axvline(0,color='#778b99',lw=.7)
fig.suptitle('A strong relationship between levels does not carry over to gains',fontsize=17,x=.07,ha='left');fig.text(.07,.875,'The same 175 countries appear in both panels; each dot is one country.',fontsize=11)
fig.text(.07,.06,'READING: Countries with more broadband generally have higher internet use in 2020.\nBut countries with larger broadband gains do not consistently have larger adoption gains. This is association, not cause.',fontsize=11,linespacing=1.7)
fig.savefig(O/'candidate_fig7_levels_vs_changes.png',dpi=220);plt.close(fig)
panel=pd.read_csv(R/'data/internet_panel_2000_2020.csv');wide=panel.pivot(index='code',columns='year',values=y).dropna();q=wide.quantile([.1,.5,.9]);years=q.columns.to_numpy();gap=q.loc[.9]-q.loc[.1];ratio=q.loc[.9]/q.loc[.1]
fig=plt.figure(figsize=(12.8,6.8));gs=fig.add_gridspec(2,2,left=.07,right=.91,bottom=.18,top=.78,wspace=.38,hspace=.6);ax=fig.add_subplot(gs[:,0]);colors=['#d78039','#317b9a','#755b9a']
for percentile,c in zip([.1,.5,.9],colors):
 v=q.loc[percentile];ax.plot(years,v,color=c,lw=2.5);ax.text(2020.35,v.iloc[-1],f'P{int(percentile*100)}: {v.iloc[-1]:.1f}%',color=c,va='center',fontsize=10)
ax.set(xlim=(2000,2025),ylim=(0,101),xlabel='Year',ylabel='Internet users (%)',title='A. Where are lower, middle and higher values?');ax.set_xticks([2000,2005,2010,2015,2020]);ax.grid(alpha=.13)
for row,v,c,title,label in [(0,gap,'#d78039','B. Absolute gap: P90 minus P10','Percentage points'),(1,ratio,'#317b9a','C. Relative gap: P90 divided by P10','Ratio (log scale)')]:
 ax=fig.add_subplot(gs[row,1]);ax.plot(years,v,color=c,lw=2.5);ax.scatter([2000,2020],[v.iloc[0],v.iloc[-1]],color=c,s=25);ax.set(title=title,xlabel='Year',ylabel=label);ax.set_xticks([2000,2010,2020]);ax.grid(alpha=.13)
 if row==1:ax.set_yscale('log')
 ax.annotate(f'{v.iloc[0]:.1f}',(2000,v.iloc[0]),xytext=(7,-16 if row==1 else 6),textcoords='offset points');ax.annotate(f'{v.iloc[-1]:.1f}',(2020,v.iloc[-1]),xytext=(-27,8),textcoords='offset points')
fig.suptitle('Has the adoption gap narrowed? The measure changes the answer',fontsize=17,x=.07,ha='left');fig.text(.07,.865,f'Same {len(wide)} countries in every year, 2000–2020. Percentiles describe country values; countries have equal weight.',fontsize=10.5)
fig.text(.07,.045,f'READING: The P90–P10 gap changes from {gap.iloc[0]:.1f} to {gap.iloc[-1]:.1f} percentage points, while the ratio falls from {ratio.iloc[0]:.1f} to {ratio.iloc[-1]:.1f}.\nA smaller ratio can coexist with a larger point gap. Percentile positions need not contain the same countries each year.',fontsize=11,linespacing=1.7)
fig.savefig(O/'candidate_fig10_absolute_relative_gaps.png',dpi=220);plt.close(fig)
# Alternative PCP: retain all axis intersections, bundle curves by explicit adoption bands.
keys=['internet_users_share_pct','telephone_lines_per100','broadband_subs_per100','mobile_subs_per100'];labels=['Internet users (%)','Landlines / 100','Broadband / 100','Mobile / 100'];limits=rows[rows.code.isin(codes)][keys].max().to_numpy();v=b[keys].to_numpy()/limits;group=np.digitize(b[keys[0]],[40,70]);centers=np.array([v[group==k].mean(axis=0) for k in range(3)]);colors=['#bd7445','#587c9d','#4b927c'];fig,axs=plt.subplots(1,2,figsize=(14,6));fig.subplots_adjust(top=.77,bottom=.24,wspace=.23)
for ax,bundled in zip(axs,[False,True]):
 for i in np.argsort(group):
  vv=v[i];g=group[i]
  if not bundled:ax.plot(range(4),vv,color=colors[g],alpha=.24,lw=.75)
  else:
   verts=[(0,vv[0])];cmd=[MPath.MOVETO]
   for j in range(3):
    mid=.45*((vv[j]+vv[j+1])/2)+.55*((centers[g,j]+centers[g,j+1])/2)
    verts.extend([(j+.18,vv[j]),(j+.32,mid),(j+.5,mid),(j+.68,mid),(j+.82,vv[j+1]),(j+1,vv[j+1])]);cmd.extend([MPath.CURVE4]*6)
   ax.add_patch(PathPatch(MPath(verts,cmd),facecolor='none',edgecolor=colors[g],alpha=.3,lw=.8))
 for j,limit in enumerate(limits):
  ax.plot([j,j],[0,1],color='#7b8d99',lw=.7)
  for t in [0,.5,1]:ax.text(j-.025,t,f'{limit*t:.0f}',ha='right',va='center',fontsize=9,bbox=dict(facecolor='white',edgecolor='none',pad=.1,alpha=.8))
 ax.set(xlim=(-.22,3.18),ylim=(-.035,1.08),xticks=range(4),xticklabels=labels);ax.set_yticks([]);ax.tick_params(axis='x',length=0,labelsize=9);ax.spines[['left','bottom']].set_visible(False);ax.set_title('B. Moderate curve bundling' if bundled else 'A. Straight country profiles',pad=25)
fig.suptitle('PCP preview: keep individual lines and use lighter bundles',fontsize=17,x=.07,ha='left');fig.text(.07,.865,'Same 175 countries, colors, scales and values. Only the paths between axes change.',fontsize=11)
for i,(name,c) in enumerate(zip(['Below 40% adoption','40–below 70% adoption','At least 70% adoption'],colors)):fig.text(.1+i*.29,.13,'● '+name,color=c,fontsize=11)
fig.text(.07,.045,'PREVIEW: Color and bundles use stated adoption bands, not discovered country types. Axis intersections are measured values.\nCurves between axes are drawing aids. A browser version would keep brushing and axis reordering.',fontsize=10.5,linespacing=1.6)
fig.savefig(O/'candidate_pcp_curves.png',dpi=220);plt.close(fig)
(O/'candidate_metrics.json').write_text(json.dumps(dict(countries_levels=len(b),countries_annual=len(wide),absolute_gap=[float(gap.iloc[0]),float(gap.iloc[-1])],relative_ratio=[float(ratio.iloc[0]),float(ratio.iloc[-1])]),indent=2));print(O)
