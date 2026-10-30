"""Selected PCP: gentle curves, original axis values, explicit adoption-band groups."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
R=Path(__file__).resolve().parents[1];O=R/'output/internet_revision'
def build():
 d=pd.DataFrame(json.loads((R/'data/infovis_countries.json').read_text()));codes=set(d[d.year==2015].code)&set(d[d.year==2020].code);d=d[d.code.isin(codes)];b=d[d.year==2020].sort_values('code');keys=['internet_users_share_pct','telephone_lines_per100','broadband_subs_per100','mobile_subs_per100'];maxima=d[keys].max().to_numpy();values=b[keys].to_numpy()/maxima;groups=np.digitize(b[keys[0]],[40,70]);centers=np.array([values[groups==i].mean(axis=0) for i in range(3)]);colors=['#bd7946','#527d9d','#418f7b'];strength=.35
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':'#214055'})
 fig,ax=plt.subplots(figsize=(13.5,6.5));fig.subplots_adjust(left=.075,right=.95,top=.70,bottom=.22)
 for i in np.argsort(groups,kind='stable'):
  yy=values[i];g=groups[i];verts=[(0,yy[0])];commands=[MPath.MOVETO]
  for j in range(3):
   mid=np.clip((yy[j]+yy[j+1])/2*(1-strength)+(centers[g,j]+centers[g,j+1])/2*strength,min(yy[j],yy[j+1]),max(yy[j],yy[j+1]))
   verts.extend([(j+.18,yy[j]),(j+.34,mid),(j+.5,mid),(j+.66,mid),(j+.82,yy[j+1]),(j+1,yy[j+1])]);commands.extend([MPath.CURVE4]*6)
  ax.add_patch(PathPatch(MPath(verts,commands),facecolor='none',edgecolor=colors[g],alpha=.26,lw=.8,zorder=1))
 for j,(label,unit,maximum) in enumerate(zip(['Internet use','Landlines','Fixed broadband','Mobile'],['% of population','subscriptions / 100','subscriptions / 100','subscriptions / 100'],maxima)):
  ax.plot([j,j],[0,1],color='#93a6b3',lw=.8,zorder=3)
  ax.text(j,1.15,label,ha='center',weight='bold',fontsize=13);ax.text(j,1.08,unit,ha='center',fontsize=10,color='#5c7483')
  for t in [0,.25,.5,.75,1]:
   ax.plot([j-.012,j+.012],[t,t],color='#93a6b3',lw=.7,zorder=4);ax.text(j-.025,t,f'{maximum*t:.1f}',ha='right',va='center',fontsize=10,color='#526b7c',bbox=dict(facecolor='white',edgecolor='none',pad=.5,alpha=.85),zorder=5)
 ax.set(xlim=(-.20,3.16),ylim=(-.03,1.03));ax.axis('off')
 fig.text(.055,.94,'High adoption can accompany different infrastructure profiles',fontsize=18,weight='bold');fig.text(.055,.88,'2020 • Same 175 matched countries • Original values at every axis • Gentle bundling (35%)',fontsize=11,color='#5a7180')
 for i,(label,color) in enumerate(zip(['Below 40% adoption','40–below 70% adoption','At least 70% adoption'],colors)):
  fig.text(.075+i*.30,.125,f'●  {label}  (n={sum(groups==i)})',color=color,fontsize=11)
 fig.text(.055,.055,'Color and curves use chosen adoption bands. Read values at the axes; the bends between them are drawing aids.',fontsize=10.5,color='#526b7c')
 fig.savefig(O/'pcp_gentle_bundles.png',dpi=270,facecolor='white');fig.savefig(O/'pcp_gentle_bundles.svg');plt.close(fig)
 b[['code','country',*keys]].assign(adoption_band=groups).to_csv(O/'pcp_gentle_values.csv',index=False)
 (O/'pcp_gentle_metrics.json').write_text(json.dumps(dict(countries=len(b),strength=strength,band_counts=[int(sum(groups==i)) for i in range(3)],maxima=dict(zip(keys,maxima)),axis_intersections_preserved=True,midpoints_clamped_to_endpoints=True),indent=2));print('PCP exported:',len(b),'countries')
if __name__=='__main__':build()
