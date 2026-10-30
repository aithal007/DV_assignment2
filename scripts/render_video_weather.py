"""Readable presentation versions of controlled weather experiments in the report."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,ListedColormap

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/video_presentation/assets'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'axes.spines.top':False,'axes.spines.right':False})
d=np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_n8_s6.npz')
lat,lon=d['lat'],d['lon'];t=d['tmmx']
dates=json.loads((ROOT/'data/scivis/manifest.json').read_text())['sample_dates']
assert -10<float(np.nanmin(t))<20 and np.nanmax(t)<60

def mapax(ax,title):
    ax.set(xlim=(-125,-66),ylim=(24,50),xticks=[-120,-95,-70],yticks=[25,45])
    ax.set_facecolor('#E5E9ED');ax.set_title(title,fontsize=17,pad=8)
    ax.tick_params(labelsize=12);ax.set_aspect('auto')
def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=170,bbox_inches='tight',facecolor='white')
    fig.savefig(OUT/(name+'.svg'),bbox_inches='tight',facecolor='white');plt.close(fig)

fig,axs=plt.subplots(2,2,figsize=(13,5.8),layout='constrained')
limits=(float(np.nanmin(t)),float(np.nanmax(t)))
spreads=np.array([np.nanmax(v)-np.nanmin(v) for v in t])
indices=[int(spreads.argmin()),int(spreads.argmax())]
for row,i in enumerate(indices):
    for col in range(2):
        ax=axs[row,col];local=(float(np.nanmin(t[i])),float(np.nanmax(t[i])))
        lim=limits if col==0 else local
        p=ax.pcolormesh(lon,lat,t[i],cmap='viridis',norm=Normalize(*lim),shading='auto',rasterized=True)
        mapax(ax,f'{str(dates[i])[:10]} · '+('fixed scale' if col==0 else 'daily scale'))
        cb=fig.colorbar(p,ax=ax,pad=.02);cb.ax.tick_params(labelsize=13);cb.set_label('Tmax (°C)',fontsize=14)
save(fig,'colour')

# Short demonstration uses the filled-contour pair from Figure 19. Line-only
# variations remain in the report, allowing larger boundaries and legends here.
i=4
fine=np.arange(np.floor(limits[0]/5)*5,np.ceil(limits[1]/5)*5+5,5)
coarse=np.arange(np.floor(limits[0]/10)*10,np.ceil(limits[1]/10)*10+10,10)
fig,axs=plt.subplots(1,2,figsize=(13,4.2),layout='constrained')
for ax,levels,label in zip(axs,[fine,coarse],['5°C intervals','10°C intervals']):
    p=ax.contourf(lon,lat,t[i],levels=levels,cmap='viridis',vmin=fine[0],vmax=fine[-1],extend='both',algorithm='serial')
    ax.contour(lon,lat,t[i],levels=levels,colors='#173047',linewidths=.45,algorithm='serial')
    mapax(ax,label)
    cb=fig.colorbar(p,ax=ax,pad=.02);cb.set_label('Tmax (°C)',fontsize=15)
save(fig,'contours')

# Preserve the original experiment's flow conversion and display-bearing correction.
speed,theta=d['vs'][i],np.deg2rad(d['th'][i]);u=-speed*np.sin(theta);v=-speed*np.cos(theta)
ys=(lat>=30)&(lat<=49);xs=(lon>=-125)&(lon<=-100)
X,Y=np.meshgrid(lon[xs],lat[ys]);U,V,S=u[np.ix_(ys,xs)],v[np.ix_(ys,xs)],speed[np.ix_(ys,xs)]
fig,axs=plt.subplots(1,2,figsize=(13,5.6),layout='constrained')
for row,ax in enumerate(axs):
    ax.pcolormesh(lon[xs],lat[ys],np.ma.masked_where(~np.isfinite(S),np.zeros_like(S)),
                  cmap=ListedColormap(['#F8FAFC']),shading='auto')
    sl=(slice(None,None,8),slice(None,None,8));xx,yy,uu,vv,ss=X[sl],Y[sl],U[sl],V[sl],S[sl]
    good=np.isfinite(ss)&(ss>.1)&np.isfinite(uu)&np.isfinite(vv)
    if row:uu,vv=np.divide(uu,ss,out=np.zeros_like(uu),where=good),np.divide(vv,ss,out=np.zeros_like(vv),where=good)
    uu,vv=np.where(good,uu,np.nan),np.where(good,vv,np.nan)
    angles=np.rad2deg(np.arctan2(vv*1.3,uu/np.cos(np.deg2rad(yy))))
    q=ax.quiver(xx,yy,uu,vv,ss,cmap='viridis',clim=(0,15),scale=25 if row==0 else 5,
                scale_units='inches',angles=angles,pivot='mid',width=.005)
    ax.set(xlim=(-125,-100),ylim=(30,49),xlabel='Longitude',ylabel='Latitude',
           xticks=[-125,-115,-105],yticks=[30,40,49]);ax.set_aspect(1.3);ax.set_facecolor('#E5E9ED')
    ax.set_title('Proportional length' if row==0 else 'Equal length',fontsize=20,pad=12)
    if row==0:ax.quiverkey(q,.70,.94,5,'5 m/s',labelpos='E',coordinates='axes',fontproperties={'size':15})
cb=fig.colorbar(q,ax=axs,pad=.02);cb.set_label('Speed (m/s)',fontsize=15)
save(fig,'quiver')
print('Rendered larger Figure 18, 19 and 26 comparisons from the original eight-date cache.')
