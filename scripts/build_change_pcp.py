"""Selected Figure 4: paired changes with a common zero reference."""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch, Rectangle

R=Path(__file__).resolve().parents[1]
O=R/'output/pcp_changes'; O.mkdir(parents=True,exist_ok=True)
protected=[]
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
keys=['internet_users_share_pct','broadband_subs_per100','telephone_lines_per100','mobile_subs_per100']
p=pd.read_json(R/'data/infovis_countries.json')
a=p[p.year==2015].set_index('code');b=p[p.year==2020].set_index('code')
codes=sorted(set(a.index)&set(b.index));a=a.loc[codes];b=b.loc[codes]
d=b[keys]-a[keys];d['country']=b.country;d['code']=d.index
assert len(d)==175 and not d[keys].isna().any().any()
sel=d[keys[0]].between(20,30); assert sel.sum()==39
limits=np.array([50,25,25,100]);values=d[keys].to_numpy()/limits
assert (abs(values)<=1).all()
names={'GEO':('#b46a32','Georgia'),'UZB':('#168479','Uzbekistan'),'BRN':('#7355a4','Brunei')}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':'#203c50'})
fig,ax=plt.subplots(figsize=(14,8));fig.subplots_adjust(left=.07,right=.87,top=.76,bottom=.23)
def curve(yy,center):
    verts=[(0,yy[0])];cmd=[MP.MOVETO]
    for j in range(3):
        mid=np.clip(.8*(yy[j]+yy[j+1])/2+.2*(center[j]+center[j+1])/2,min(yy[j],yy[j+1]),max(yy[j],yy[j+1]))
        verts.extend([(j+.18,yy[j]),(j+.34,mid),(j+.5,mid),(j+.66,mid),(j+.82,yy[j+1]),(j+1,yy[j+1])]);cmd.extend([MP.CURVE4]*6)
    return MP(verts,cmd)
centers=[values[~sel].mean(axis=0),values[sel].mean(axis=0)]
ax.axhspan(0,1,facecolor='#f4f9f8',zorder=-5);ax.axhspan(-1,0,facecolor='#faf8f5',zorder=-5)
ax.axhline(0,color='#657c89',lw=1,ls=(0,(4,4)),zorder=0)
for chosen in [False,True]:
    for i,row in enumerate(d.itertuples()):
        if bool(sel.iloc[i])!=chosen:continue
        ax.add_patch(PathPatch(curve(values[i],centers[int(chosen)]),facecolor='none',edgecolor='#628eaa' if chosen else '#bdc6cc',alpha=.39 if chosen else .14,lw=.9 if chosen else .55))
for code,(color,name) in names.items():
    i=codes.index(code);yy=values[i];ax.add_patch(PathPatch(curve(yy,centers[1]),facecolor='none',edgecolor=color,lw=2.3,zorder=5))
    ax.scatter(range(4),yy,s=24,color=color,zorder=6)
    ax.text(3.07,yy[3],name,color=color,weight='bold',va='center',fontsize=11)
for j,(label,lim) in enumerate(zip(['Internet use','Fixed broadband','Landlines','Mobile'],limits)):
    ax.plot([j,j],[-1,1],color='#95a9b6',lw=.9)
    ax.text(j,1.22,label,ha='center',weight='bold',fontsize=13)
    ax.text(j,1.11,'change in percentage points' if j==0 else 'change in subscriptions / 100',ha='center',fontsize=9)
    for t in [-1,-.5,0,.5,1]:
        ax.plot([j-.013,j+.013],[t,t],color='#95a9b6');ax.text(j-.025,t,f'{t*lim:+g}' if t else '0',ha='right',va='center',fontsize=10,bbox=dict(facecolor='white',edgecolor='none',pad=.7),zorder=7)
ax.add_patch(Rectangle((-.028,.4),.056,.2,facecolor='#d7eaf4',edgecolor='#4989ac',zorder=8))

ax.set(xlim=(-.18,3.48),ylim=(-1.04,1.04));ax.axis('off')
fig.text(.055,.95,'Similar internet gains, different infrastructure changes',fontsize=20,weight='bold')
fig.text(.055,.902,'2015 → 2020  |  175 matched countries  |  Blue: 39 countries gaining 20–30 points in internet use',fontsize=11,color='#536e80')
fig.text(.055,.15,'Read each line across the four axes. Above zero = increase; below zero = decrease.',fontsize=11)
fig.text(.055,.112,'Three named examples help trace individual records; the other selected countries remain blue.',fontsize=10.5,color='#536e80')
fig.text(.055,.073,'Axes have different ranges. Values are measured at the axes; gentle bends do not represent intermediate observations.',fontsize=10,color='#536e80')
fig.savefig(O/'pcp_changes.png',dpi=220,facecolor='white');fig.savefig(O/'pcp_changes.svg');plt.close(fig)
d.assign(selected=sel).to_csv(O/'paired_changes.csv',index=False)
records=json.loads(d.reset_index(drop=True).to_json(orient='records'))
(O/'data.js').write_text('const records='+json.dumps(records)+';',encoding='utf-8')
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
metrics=dict(countries=len(d),selected=int(sel.sum()),selection='20 <= adoption change <= 30 percentage points',examples=d.loc[list(names),keys].to_dict('index'),protected_hashes=after)
(O/'validation.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps(metrics,indent=2))
