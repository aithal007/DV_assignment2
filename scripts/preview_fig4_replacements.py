"""Unapproved alternatives for Figure 4 only. Protect report and Figure 5."""
from pathlib import Path
import json,hashlib,html
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.patches import Rectangle
R=Path(__file__).resolve().parents[1];O=R/'output/fig4_review_20261026';O.mkdir(exist_ok=True)
protected=[R/'REPORT.md',R/'data/current_figure_manifest.json',R/'output/pdf/DAS732_A2_Report_IEEE.pdf',R/'output/internet_revision/pcp_gentle_bundles.png'];before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
d=pd.DataFrame(json.loads((R/'data/infovis_countries.json').read_text()));codes=set(d[d.year==2015].code)&set(d[d.year==2020].code);b=d[(d.year==2020)&d.code.isin(codes)].set_index('code');keys=['internet_users_share_pct','telephone_lines_per100','broadband_subs_per100','mobile_subs_per100'];s=b[(b[keys[0]]>=70)&(b[keys[2]]<=5)].sort_values(keys[2]);assert len(s)==6 and len(b)==175
rank=(b[keys].rank(method='average')-1)/(len(b)-1)*100;rs=rank.loc[s.index];raw=s[keys].to_numpy();pct=rs.to_numpy()
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':'#203e51','axes.labelcolor':'#203e51'})
colors=['#eaf3f7','#d7e8ec','#a6cdd1','#5e9ba7','#24647d','#163a57'];cmap=LinearSegmentedColormap.from_list('profile_rank',colors)
fig=plt.figure(figsize=(12.8,7.4));ax=fig.add_axes([.225,.245,.72,.49]);ax.imshow(pct,cmap=cmap,vmin=0,vmax=100,aspect='auto')
ax.set_xticks(range(4),['Internet use\n% of population','Landlines\nsubscriptions / 100','Fixed broadband\nsubscriptions / 100','Mobile\nsubscriptions / 100'],fontsize=11.5,weight='bold');ax.xaxis.tick_top();ax.tick_params(axis='x',pad=16,length=0);ax.set_yticks(range(6),s.country,fontsize=13);ax.tick_params(axis='y',length=0,pad=17)
for spine in ax.spines.values():spine.set_visible(False)
for i in range(6):
 for j in range(4):
  value=raw[i,j];label=f'{value:.2f}' if j==2 else f'{value:.1f}';label+='%' if j==0 else '';ax.text(j,i,label,ha='center',va='center',fontsize=17,weight='bold',color='white' if pct[i,j]>=65 else '#183b52')
ax.set_xticks(np.arange(-.5,4,1),minor=True);ax.set_yticks(np.arange(-.5,6,1),minor=True);ax.grid(which='minor',color='white',lw=7);ax.tick_params(which='minor',length=0)
fig.text(.055,.95,'One access label hides six different country profiles',fontsize=19,weight='bold');fig.text(.055,.885,'2020 • Internet use ≥70% and fixed broadband ≤5 subscriptions per 100 people',fontsize=11.5)
fig.text(.055,.83,'A. Profile heatmap   Numbers = actual values. Color = rank among all 175 matched countries.',fontsize=11)
cax=fig.add_axes([.34,.14,.48,.022]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0,100),cmap=cmap),cax=cax,orientation='horizontal');cb.set_ticks([0,25,50,75,100],labels=['0: lowest','25','50: middle','75','100: highest']);cb.outline.set_visible(False);cb.ax.tick_params(labelsize=9,length=0)
fig.text(.055,.055,'READING  Fixed-broadband ranks stay relatively low, but mobile ranks range from low to near the top.\nRows are ordered by broadband. Colors compare ranks within each measure; they do not equate the original units.',fontsize=11,linespacing=1.7)
fig.savefig(O/'option_a_ranked_profile_heatmap.png',dpi=240,facecolor='white');fig.savefig(O/'option_a_ranked_profile_heatmap.svg');plt.close(fig)
# Native-unit alternative: aligned country rows, one scale per measure.
fig,axs=plt.subplots(1,4,figsize=(13.5,6.8),sharey=True);fig.subplots_adjust(left=.16,right=.97,bottom=.24,top=.69,wspace=.33)
limits=[100,25,5,180];colors=['#428f7a','#627f9d','#47758e','#947048'];titles=['Internet use','Landlines','Fixed broadband','Mobile'];units=['% of population','subscriptions / 100','subscriptions / 100','subscriptions / 100']
for j,ax in enumerate(axs):
 ax.set_facecolor('white')
 if j==0:ax.axvspan(70,100,color='#e7f2ed',zorder=0);ax.axvline(70,color='#a8c8ba',lw=1,ls='--')
 for i in range(6):
  value=raw[i,j];ax.axhspan(i-.42,i+.42,color='#f3f6f8',zorder=-1);ax.plot([0,value],[i,i],color=colors[j],lw=2.4,alpha=.4,zorder=1);ax.scatter(value,i,s=63,color=colors[j],edgecolors='white',linewidths=.7,zorder=3);label=f'{value:.2f}' if j==2 else f'{value:.1f}';label+='%' if j==0 else '';offset=-8 if value/limits[j]>.78 else 8;ax.annotate(label,(value,i),xytext=(offset,0),textcoords='offset points',ha='right' if offset<0 else 'left',va='center',fontsize=10.5,color='#203e51',bbox=dict(facecolor='#f3f6f8',edgecolor='none',alpha=.82,pad=.6))
 ax.set_xlim(-.025*limits[j],limits[j]*1.03);ax.set_ylim(5.6,-.6);ax.set_xticks([0,limits[j]/2,limits[j]]);ax.set_xticklabels([f'{v:g}' for v in [0,limits[j]/2,limits[j]]],fontsize=10);ax.set_title(titles[j]+'\n'+units[j],fontsize=11.5,weight='bold',pad=20);ax.spines[['top','right','left']].set_visible(False);ax.spines['bottom'].set_color('#aebdc7');ax.tick_params(axis='y',length=0);ax.tick_params(axis='x',color='#aebdc7');ax.set_yticks(range(6))
axs[0].set_yticklabels(s.country,fontsize=12.5)
fig.text(.055,.95,'The same filters select countries with very different profiles',fontsize=18,weight='bold');fig.text(.055,.88,'2020 • Six countries with internet use ≥70% and fixed broadband ≤5 per 100 people',fontsize=11.5)
fig.text(.055,.80,'B. Aligned dot plots   Follow a country across its row; each column uses its own labelled scale.',fontsize=11)
fig.text(.055,.08,'READING  Kuwait has 99.1% internet use with only 1.68 fixed-broadband subscriptions per 100.\nCuba and Libya both meet the filters, but their mobile counts differ sharply: 59.6 versus 165.0 per 100.',fontsize=11,linespacing=1.7)
fig.savefig(O/'option_b_aligned_country_dots.png',dpi=240,facecolor='white');fig.savefig(O/'option_b_aligned_country_dots.svg');plt.close(fig)
s[['country',*keys]].to_csv(O/'actual_values.csv');rs.assign(country=s.country).to_csv(O/'rank_scores.csv')
# Independent count-based check of average ranks, including tied values.
for c in s.index:
 for key in keys:
  v=b.at[c,key];lower=int((b[key]<v).sum());equal=int((b[key]==v).sum());expected=(lower+(equal-1)/2)/174*100;assert abs(expected-rs.at[c,key])<1e-10
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==before[str(p)] for p in protected)
(O/'validation.json').write_text(json.dumps(dict(status='PASS',selected_countries=6,reference_countries=175,raw_values=24,rank_scores_independently_checked=24,report_unchanged=True,figure5_unchanged=True,rank_definition='100*(average rank - 1)/(175 - 1)',selection='internet use >=70%; fixed broadband <=5 per 100',protected_sha256=before),indent=2))
text='''# Figure 4 alternatives — awaiting approval

Target: replace the six-country straight PCP in Figure 4. The report and Figure 5 remain unchanged.

A. Ranked profile heatmap: selected six countries are rows, four measures are columns. Printed numbers are actual values. Color is a normalized average rank within each measure across all 175 matched countries (0 lowest, 100 highest). Ties receive average ranks. This adds context instead of simply restyling the same line chart. It does not show physical connectivity or evidence for a mobile-only access mechanism. Subscriptions are not unique people.

B. Aligned dot plots: the same country stays on one row; four separate native-unit scales preserve exact values without crossing lines. Axes are fitted to the selected subset, so their apparent positions should not be compared with full-country Figure 5 slopes. The left column shades the >=70% adoption selection. It prioritizes precise value comparison over reference-population rank context.

Recommendation: A for added analytical context and clear country profiles. B if native-unit reading is the priority. Figure 5 supplies the required interactive bundled PCP, so Figure 4 can be a supporting multivariable view.

Design research:
- https://www.datawrapper.de/academy/how-to-create-a-heatmap
- https://www.datawrapper.de/blog/brand-new-dot-plots

The source data remain the team's supplied A1 extracts; no external facts were added to the analysis. Reproduce: python -X utf8 scripts/preview_fig4_replacements.py
'''
(O/'REVIEW.md').write_text(text,encoding='utf-8')
cards=''.join(f'<article><h2>{title}</h2><a href="{file}.png"><img src="{file}.png"></a><p>{desc}</p></article>' for title,file,desc in [('A. Ranked profile heatmap — recommended','option_a_ranked_profile_heatmap','Actual values remain printed; color adds each value’s relative position among 175 countries.'),('B. Aligned dot plots','option_b_aligned_country_dots','Country rows stay aligned across four native-unit scales; no crossing country lines.')])
(O/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Figure 4 replacement review</title><style>body{font:17px Arial;max-width:1350px;margin:36px auto;background:#edf3f6;color:#203e51}article{padding:24px;background:white;margin:24px 0}img{width:100%}p{line-height:1.6}</style><h1>Figure 4 replacement previews</h1><p>Report and Figure 5 unchanged. Both alternatives preserve the same six countries.</p>'+cards,encoding='utf-8')
print('PASS: two Figure 4 previews; report and Figure 5 unchanged')

