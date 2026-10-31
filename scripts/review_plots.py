"""Evidence and readable exports addressing the final PDF review."""
from pathlib import Path
import json,itertools
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize,TwoSlopeNorm,LogNorm,BoundaryNorm,ListedColormap,PowerNorm
from matplotlib.patches import Patch,Rectangle
import matplotlib.dates as mdates
from marching_squares import segments,cell_segments,validate
from network_threshold_revision import inputs

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/review_revision'
INK='#18364c';TEAL='#168a8a';ORANGE='#d05a2b'
FACTS={}

def save(fig,path):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    for suffix in ['.png','.svg']:fig.savefig(path.with_suffix(suffix),dpi=240,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def geo(ax,title):
    ax.set(xlim=(-125,-66),ylim=(24,50),xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)')
    ax.set_title(title,loc='left',fontsize=13,pad=9)

def crossing_count(g,pos):
    edges=list(g.edges);xy=np.array([[pos[u],pos[v]] for u,v in edges]);answer=0
    def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
    for i,(u,v) in enumerate(edges):
        candidates=[j for j in range(i+1,len(edges)) if not {u,v}&set(edges[j])]
        if not candidates:continue
        a,b=xy[i];c=xy[candidates,0];d=xy[candidates,1]
        answer+=int(np.sum((cross(b-a,c-a)*cross(b-a,d-a)<-1e-16)&(cross(d-c,a-c)*cross(d-c,b-c)<-1e-16)))
    return answer

def network():
    d,a,g,groups=inputs();regions=sorted({n['region'] for n in d['nodes']});palette=dict(zip(['Africa','Asia','Europe','North America','Oceania','South America','Unclassified'],['#bd4c43','#6b54a3','#3476b6','#d29328','#36a0a8','#399269','#68717a']))
    fig=plt.figure(figsize=(17,12));gs=fig.add_gridspec(3,6,height_ratios=[.8,1.8,.18],hspace=.40)
    ax=fig.add_subplot(gs[0,:3]);v=[e['similarity'] for e in d['all_edges']]
    ax.hist(v,bins=np.linspace(0,1,41),color='#9db5c3',edgecolor='white');ax.axvline(a['threshold'],c=ORANGE,lw=2)
    ax.set(title='A. All 15,931 pair similarities',xlabel='Similarity = 1 / (1 + standardized distance)',ylabel='Country pairs')
    ax.text(.97,.92,f"P95 = {a['threshold']:.6f}",ha='right',transform=ax.transAxes,color=ORANGE,fontsize=13)
    ax=fig.add_subplot(gs[0,3:]);s=pd.read_csv(ROOT/'output/network_revision/threshold_topology.csv')
    ax.plot(s['quantile']*100,s.largest_component,c=TEAL,lw=2,label='Largest component');ax.plot(s['quantile']*100,s.isolates,c='#7655a3',lw=2,label='Isolates');ax.axvline(95,c=ORANGE,lw=2)
    ax.set(title='B. Filtering changes connectedness',xlabel='Similarity percentile cutoff',ylabel='Countries',xlim=(80,99),ylim=(0,185))
    ax.legend(loc='center left',frameon=False);ax.text(.03,.06,'At P95: 797 edges; component 167; isolates 12',transform=ax.transAxes,fontsize=12,bbox=dict(fc='white',ec='none',alpha=.9))
    rows=[]
    for j,(name,pos) in enumerate(d['layouts'].items()):
        ax=fig.add_subplot(gs[1,2*j:2*j+2]);near=set(g.neighbors('IND'))
        ax.add_collection(LineCollection([[pos[u],pos[v]] for u,v in g.edges],colors='#718896',linewidths=.75,alpha=.48))
        ax.add_collection(LineCollection([[pos['IND'],pos[v]] for v in near],colors=ORANGE,linewidths=2.2,alpha=.95,zorder=3))
        for n,p in pos.items():
            ax.scatter(*p,s=24+3.5*g.degree(n),c=[palette[g.nodes[n]['region']]],ec=ORANGE if n=='IND' else 'white',linewidth=2 if n=='IND' else .35,zorder=4)
        if name in ['Spring','Spectral']:
            ax.add_patch(Rectangle((-.035,-.04),1.07,.08,fc='#f1f5f7',ec='#839aa7',ls='--',zorder=-1));ax.text(.5,-.10,'12 isolates (degree zero)',ha='center',fontsize=11)
        ax.annotate('India',pos['IND'],xytext=(8,10),textcoords='offset points',fontsize=13,weight='bold',bbox=dict(fc='white',ec='none',alpha=.8))
        crosses=crossing_count(g,pos);lengths=[np.linalg.norm(np.asarray(pos[u])-pos[v]) for u,v in g.edges]
        rows.append(dict(layout=name,proper_edge_crossings=crosses,median_normalized_edge_length=float(np.median(lengths))))
        ax.set(xlim=(-.08,1.08),ylim=(-.16,1.1),aspect='equal');ax.axis('off');ax.set_title(f'{name}\n{crosses:,} proper edge crossings',fontsize=15)
    ax=fig.add_subplot(gs[2,:]);ax.axis('off');ax.legend(handles=[Patch(fc=c,label=r) for r,c in palette.items()],ncol=len(regions),loc='center',frameon=False,fontsize=11)
    fig.suptitle('One graph, three layouts: separation, clutter and crossing costs',fontsize=21,weight='bold',y=.99)
    fig.text(.5,.015,'Node color = region; size = retained degree. Orange edges = India links. Same 179 nodes and 797 edges in every layout.\nCrossings count straight segment interiors, excluding shared endpoints and collinear overlaps; positions do not define similarity.',ha='center',fontsize=12)
    fig.subplots_adjust(bottom=.10,top=.92)
    save(fig,'output/network_revision/network_threshold_layouts.png')
    pd.DataFrame(rows).to_csv(OUT/'layout_comparison.csv',index=False);FACTS['layouts']=rows

def matrix():
    d,a,g,groups=inputs();i,c=min([(i,c) for i,c in enumerate(groups) if len(c)>=5 and g.subgraph(c).number_of_edges()<len(c)*(len(c)-1)//2],key=lambda z:(len(z[1]),z[0]))
    codes=sorted(c,key=lambda n:(-g.subgraph(c).degree(n),n));m=nx.to_numpy_array(g,nodelist=codes,weight=None).astype(int)
    fig,(ax,b)=plt.subplots(1,2,figsize=(17,9),gridspec_kw={'width_ratios':[.8,1.4]},layout='constrained')
    h=nx.Graph();h.add_nodes_from(range(len(groups)));owner={n:j for j,group in enumerate(groups) for n in group}
    for u,v in g.edges:
        if owner[u]!=owner[v]:
            a0,b0=owner[u],owner[v];h.add_edge(a0,b0,weight=h.get_edge_data(a0,b0,{}).get('weight',0)+1)
    p=nx.circular_layout(h)
    nx.draw_networkx_edges(h,p,ax=ax,width=[.8+.2*h[u][v]['weight'] for u,v in h.edges],edge_color='#a0b0ba')
    nx.draw_networkx_nodes(h,p,ax=ax,node_size=[900+55*len(group) for group in groups],node_color=[ORANGE if j==i else '#c5dce3' for j in h])
    nx.draw_networkx_labels(h,p,{j:f'G{j+1}\nn={len(group)}' for j,group in enumerate(groups)},ax=ax,font_size=12)
    nx.draw_networkx_edge_labels(h,p,{e:h.edges[e]['weight'] for e in h.edges},ax=ax,font_size=11)
    ax.set_title('A. Community-level link overview\nEdge labels = between-community links',fontsize=14);ax.axis('off')
    ax.text(.5,-.07,'699 internal + 98 between-group edges\n12 isolated countries remain outside these six groups.',transform=ax.transAxes,ha='center',fontsize=12)
    show=np.where(np.eye(len(codes)),.5,m);b.imshow(show,cmap=ListedColormap(['white','#dce2e6',TEAL]),vmin=0,vmax=1)
    b.set_xticks(range(len(codes)),codes,rotation=60,ha='right',fontsize=13);b.set_yticks(range(len(codes)),[g.nodes[n]['country']+f' ({int(m[j].sum())})' for j,n in enumerate(codes)],fontsize=14)
    b.set_xticks(np.arange(-.5,len(codes),1),minor=True);b.set_yticks(np.arange(-.5,len(codes),1),minor=True);b.grid(which='minor',c='#c0ced6',lw=.5);b.tick_params(which='both',length=0)
    b.set_title(f'B. G{i+1}: 93 of 105 possible pairs\nRows/columns ordered by within-group degree',fontsize=14)
    fig.suptitle('Community labels conceal different pair relationships',fontsize=21,weight='bold')
    fig.supxlabel('Teal = meets P95; white = measured below cutoff; gray = self-pair. Row labels give internal degree.\nEach undirected link appears twice; the left panel aggregates communities, the right resolves individual pairs.',fontsize=12)
    save(fig,'output/network_revision/nodetrix_threshold_detail.png');pd.DataFrame(m,index=codes,columns=codes).to_csv(ROOT/'output/network_revision/nodetrix_detail_matrix.csv')

def weather_data():
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz') as z:d={k:z[k].copy() for k in z.files}
    d['valid']=np.logical_and.reduce([np.isfinite(d[k]).all(0) for k in ['tmmx','pr','vs','th']]);d['weights']=np.broadcast_to(np.cos(np.deg2rad(d['lat']))[:,None],d['valid'].shape)
    return d

def changes(d):
    t=d['tmmx'];valid=d['valid'];w=d['weights'][valid];monthly=t[62:].mean(0)-t[:31].mean(0);endpoint=t[-1]-t[0];disagree=(monthly*endpoint<0)&valid
    pct=float(np.average(disagree[valid],weights=w)*100);fig,ax=plt.subplots(2,2,figsize=(16,10),layout='constrained');limit=float(np.nanmax(np.abs(np.r_[monthly[valid],endpoint[valid]])))
    for a,v,title in [(ax[0,0],monthly,'A. September mean minus July mean'),(ax[0,1],endpoint,'B. September 30 minus July 1')]:
        im=a.pcolormesh(d['lon'],d['lat'],np.where(valid,v,np.nan),cmap='RdBu_r',norm=TwoSlopeNorm(vmin=-limit,vcenter=0,vmax=limit),shading='auto');geo(a,title)
    fig.colorbar(im,ax=list(ax[0]),label='Temperature difference (degrees C)',shrink=.8)
    ax[1,0].pcolormesh(d['lon'],d['lat'],np.where(valid,disagree,np.nan),cmap=ListedColormap(['#e0e8ec',ORANGE]),vmin=0,vmax=1,shading='auto');geo(ax[1,0],f'C. Opposite signs: {pct:.2f}% of weighted area')
    ax[1,0].legend(handles=[Patch(fc=ORANGE,label='Opposite signs'),Patch(fc='#e0e8ec',label='Not opposite')],loc='lower left',frameon=True,fontsize=10)
    for condition,label,c in [(d['lon']<-105,'West',TEAL),((d['lon']>=-105)&(d['lon']<-90),'Central',ORANGE),(d['lon']>=-90,'East','#7655a3')]:
        mask=valid&condition[None,:];v=monthly[mask];order=np.argsort(v);ww=d['weights'][mask][order];ax[1,1].plot(v[order],np.cumsum(ww)/ww.sum(),label=label,c=c,lw=2)
    ax[1,1].set(xlabel='Monthly temperature change (degrees C)',ylabel='Cumulative area fraction',title='D. Spatial distribution of monthly change');ax[1,1].legend(frameon=False);ax[1,1].grid(alpha=.2)
    fig.suptitle('Two endpoints can give a different sign from complete months',fontsize=21,weight='bold')
    save(fig,'images/quality/monthly_temperature_change.png');FACTS['endpoint_sign_disagreement_pct']=pct

def hovmoller(d):
    with np.load(ROOT/'data/quality/hovmoller.npz') as h:t=h['temperature_C'];rain=h['rain_mm'];counts=h['cell_counts'];lon=h['lon'];dates=h['dates'].astype('datetime64[D]')
    baseline=np.divide(np.nansum(t,axis=0),np.isfinite(t).sum(0),out=np.full(t.shape[1],np.nan),where=np.isfinite(t).sum(0)>0)
    anomaly=t-baseline;limit=float(np.nanmax(np.abs(anomaly)));imax=np.unravel_index(np.nanargmax(rain),rain.shape)
    fig=plt.figure(figsize=(16,12),layout='constrained');gs=fig.add_gridspec(4,2,height_ratios=[.7,1.2,1.2,.4]);ax=fig.add_subplot(gs[0,0]);geo(ax,'A. Fixed common-land averaging band')
    ax.pcolormesh(d['lon'],d['lat'],np.where(d['valid'],1,np.nan),cmap=ListedColormap(['#b8cbd5']),shading='auto');ax.axhspan(30,45,color=ORANGE,alpha=.2)
    ax=fig.add_subplot(gs[0,1]);ax.axis('off');ax.text(0,1,'Time runs horizontally; longitude vertically.\nB removes each longitude\'s 92-day mean Tmax.\nC uses physical mm/day labels with square-root color spacing.\nD reports the land-cell support behind each band mean.',va='top',fontsize=13,linespacing=1.8)
    for row,values,cmap,norm,title,label in [(1,anomaly,'RdBu_r',TwoSlopeNorm(vmin=-limit,vcenter=0,vmax=limit),'B. Tmax departure from own-longitude 92-day mean','Temperature departure (degrees C)'),(2,rain,'Blues',PowerNorm(.5,vmin=0,vmax=float(np.nanmax(rain))),'C. Latitude-weighted daily rain: 30-45 N','Rain (mm/day; square-root color spacing)')]:
        a=fig.add_subplot(gs[row,:]);im=a.pcolormesh(dates,lon,values.T,cmap=cmap,norm=norm,shading='auto');a.set(ylabel='Longitude (degrees east)',xlabel='Date in 2023',ylim=(-125,-66));a.set_title(title,loc='left',fontsize=14);a.xaxis.set_major_locator(mdates.MonthLocator());a.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'));bar=fig.colorbar(im,ax=a,pad=.015,label=label)
        if row==2:bar.set_ticks([0,1,5,20,50,float(np.nanmax(rain))])
    a=fig.add_subplot(gs[3,:]);a.plot(lon,counts,c=INK);a.set(xlabel='Longitude (degrees east)',ylabel='Land cells',title='D. Fixed valid cells in the latitude band',xlim=(-125,-66));a.grid(alpha=.15)
    fig.suptitle('Hovmoller diagrams: departures expose timing behind the climate gradient',fontsize=20,weight='bold')
    save(fig,'images/quality/weather_hovmoller.png')
    j=imax[1];mask=d['valid'][:,j]&(d['lat']>=30)&(d['lat']<=45)
    mean=float(np.average(d['pr'][imax[0],mask,j],weights=np.cos(np.deg2rad(d['lat'][mask]))));assert np.isclose(mean,rain[imax])
    FACTS['hovmoller']=dict(max_rain_mm_day=mean,date=str(dates[imax[0]]),longitude=float(lon[j]),support_cells=int(counts[j]),cell_rain_min=float(d['pr'][imax[0],mask,j].min()),cell_rain_max=float(d['pr'][imax[0],mask,j].max()),minimum_support=int(counts[counts>0].min()),maximum_support=int(counts.max()))
    valid=d['valid'];mask=valid&(d['lon']<-105)[None,:];FACTS['western_July27_mean_C']=float(np.average(d['tmmx'][26][mask],weights=d['weights'][mask]));FACTS['July_all_area_mean_C']=float(np.average(d['tmmx'][:31,valid].mean(0),weights=d['weights'][valid]))

def contours(d):
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_n8_s6.npz') as z:t=z['tmmx'][4];x=z['lon'];y=z['lat']
    result=validate(x,y,t,[25,30,35,40]);(OUT/'marching_squares_validation.json').write_text(json.dumps(result,indent=2))
    fig=plt.figure(figsize=(17,13),layout='constrained');gs=fig.add_gridspec(3,2,height_ratios=[1.2,1.1,.85])
    ax=fig.add_subplot(gs[0,0]);background=np.where(np.isfinite(t),1,np.nan);ax.pcolormesh(x,y,background,cmap=ListedColormap(['#edf2f5']),shading='auto')
    colors=['#246b8e',TEAL,ORANGE,'#8c3556']
    for level,c in zip([25,30,35,40],colors):ax.add_collection(LineCollection(segments(x,y,t,level),colors=c,linewidths=1.3,label=f'{level} C'))
    geo(ax,'A. Independent 16-case implementation');ax.legend(ncol=2,fontsize=10,loc='lower left')
    ax=fig.add_subplot(gs[0,1]);ax.pcolormesh(x,y,background,cmap=ListedColormap(['#edf2f5']),shading='auto')
    ax.add_collection(LineCollection(segments(x,y,t,35),colors=ORANGE,linewidths=2.3,label='Custom'))
    ref=ax.contour(x,y,t,levels=[35],colors='#17384e',linewidths=1.0,linestyles='--',algorithm='serial',corner_mask=False);geo(ax,'B. 35 C overlay: custom and ContourPy');ax.legend(handles=[plt.Line2D([0],[0],c=ORANGE,lw=2,label='Custom'),plt.Line2D([0],[0],c=INK,ls='--',label='ContourPy')],fontsize=10,loc='lower left')
    for col,step in enumerate([5,10]):
        ax=fig.add_subplot(gs[1,col]);im=ax.contourf(x,y,t,levels=np.arange(-5,55,step),cmap='viridis',algorithm='serial',corner_mask=False);geo(ax,f'{chr(67+col)}. Filled contours: {step} C intervals');fig.colorbar(im,ax=ax,shrink=.8,label='Tmax (degrees C)')
    sub=gs[2,:].subgridspec(2,8,wspace=.2,hspace=.25);xy=np.array([[0,0],[1,0],[1,1],[0,1]],dtype=float)
    for case in range(16):
        ax=fig.add_subplot(sub[case//8,case%8]);v=np.array([1. if case&(1<<k) else -1. for k in range(4)]);ax.plot([0,1,1,0,0],[0,0,1,1,0],c='#9badb8',lw=.5);ax.scatter(xy[:,0],xy[:,1],c=np.where(v>0,ORANGE,'#236b8e'),s=12)
        for seg in cell_segments(xy,v,0):ax.plot(seg[:,0],seg[:,1],c=INK,lw=1.3)
        ax.set_title(f'{case:04b}',fontsize=14,pad=2);ax.set(aspect='equal',xlim=(-.1,1.1),ylim=(-.1,1.1));ax.axis('off')
    fig.suptitle('Marching Squares implemented and cross-checked on real gridMET data',fontsize=21,weight='bold')
    fig.supxlabel('August 22, 2023. Fully valid quads only; exact-level values are below. Saddles use the corner-mean center.\nAll 16 cases (bottom); linear edge interpolation; identical real-grid segments at 25/30/35/40 C to 1e-8 degrees.',fontsize=12)
    save(fig,'output/internet_revision/contours_worked.png');FACTS['marching_squares']=result

def quiver(d):
    from build_scivis import quiver_experiments
    # A wider, two-density comparison replaces six tiny panels. Bearings are
    # display-corrected; vector magnitudes retain the same physical key.
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_n8_s6.npz') as z:
        x=z['lon'];y=z['lat'];s=z['vs'][4];direction=z['th'][4]
    xx,yy=np.meshgrid(x,y);fig,axes=plt.subplots(2,2,figsize=(16,11),layout='constrained')
    for row in range(2):
        for col,step in enumerate([4,12]):
            ax=axes[row,col];sl=(slice(None,None,step),slice(None,None,step));speed=s[sl];theta=np.deg2rad(direction[sl]);u=-speed*np.sin(theta);v=-speed*np.cos(theta);angles=np.rad2deg(np.arctan2(v*1.3,u/np.cos(np.deg2rad(yy[sl]))))
            good=np.isfinite(speed)&(speed>.1)
            if row==1:u=np.divide(u,speed,out=np.zeros_like(u),where=good);v=np.divide(v,speed,out=np.zeros_like(v),where=good)
            q=ax.quiver(xx[sl],yy[sl],np.where(good,u,np.nan),np.where(good,v,np.nan),speed,cmap='viridis',clim=(0,15),angles=angles,scale=20 if row==0 else 4,scale_units='inches',width=.004,headwidth=4,headlength=5,pivot='mid')
            ax.set(xlim=(-125,-100),ylim=(30,49),xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)');ax.set_title(f'{"Speed-proportional" if row==0 else "Same length"} | every {step}th display cell',loc='left',fontsize=14)
            if row==0:ax.quiverkey(q,.76,1.03,5,'5 m/s',labelpos='E',coordinates='axes')
    fig.colorbar(q,ax=list(axes.flat),label='Wind speed (m/s)',shrink=.8,extend='max');fig.suptitle('Visible arrows expose the density and magnitude trade-off',fontsize=21,weight='bold')
    fig.supxlabel('August 22, 2023 | flow-TO direction from vs and th | colored speed in both rows\nAlready stride-six data; arrow steps 4 and 12 do not change the source wind resolution. Calm/missing vectors omitted.',fontsize=12)
    save(fig,'images/scivis/scivis_quiver_experiments.png')

def roses():
    table=pd.read_csv(ROOT/'output/lecture_previews/monthly_wind_rose.csv');colors=['#d5e6ee','#9dc6d9','#4f9cbf','#236e99','#173e67'];fig,axes=plt.subplots(1,3,figsize=(16,6.5),subplot_kw={'projection':'polar'})
    for ax,month,label in zip(axes,[7,8,9],['July','August','September']):
        h=table[table.month.eq(month)].pivot(index='speed_bin',columns='from_direction_degrees',values='area_day_pct');bottom=np.zeros(16)
        for k,c in enumerate(colors):ax.bar(np.deg2rad(h.columns),h.loc[k],bottom=bottom,width=2*np.pi/16*.9,color=c,ec='white',lw=.4);bottom+=h.loc[k].to_numpy()
        ax.set_theta_zero_location('N');ax.set_theta_direction(-1);ax.set_thetagrids(range(0,360,45),['N','NE','E','SE','S','SW','W','NW'],fontsize=12);ax.set(ylim=(0,14),yticks=[4,8,12],yticklabels=[]);ax.grid(alpha=.35);ax.set_title(label,pad=25,fontsize=17)
    fig.legend(handles=[Patch(fc=c,label=s) for c,s in zip(colors,['0-<2','2-<4','4-<6','6-<8','>=8 m/s'])],loc='lower center',ncol=5,frameon=False,bbox_to_anchor=(.5,.07),fontsize=12)
    fig.suptitle('Wind FROM-direction and speed distributions: common radial scale',fontsize=21,weight='bold');fig.text(.5,.02,'All panels: rings at 4%, 8%, 12%; outer limit 14% of weighted cell-days. Direction labels lie outside the bars.',ha='center',fontsize=12);fig.subplots_adjust(top=.78,bottom=.22,wspace=.35)
    save(fig,'output/lecture_previews/monthly_wind_roses.png')

def color_comparison(d):
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_n8_s6.npz') as z:t=z['tmmx'][4];rain=z['pr'][4];x=z['lon'];y=z['lat']
    departure=t-d['tmmx'].mean(0);limit=float(np.nanmax(np.abs(departure)));bounds=np.arange(-5,55,5)
    fig,axes=plt.subplots(3,2,figsize=(16,12),layout='constrained')
    panels=[(t,'viridis',Normalize(-5,50),'A. Continuous sequential: same Tmax','Tmax (degrees C)'),(t,'cividis',BoundaryNorm(bounds,256),'B. Discrete sequential: 5 C bands','Tmax (degrees C)'),(rain,'Blues',Normalize(0,float(np.nanmax(rain))),'C. Rain: linear sequential','Rain (mm/day)'),(np.ma.masked_where(rain<=0,rain),'magma',LogNorm(.1,float(np.nanmax(rain))),'D. Rain: logarithmic sequential','Rain (mm/day; zero masked)'),(departure,'RdBu_r',TwoSlopeNorm(vmin=-limit,vcenter=0,vmax=limit),'E. Diverging: departure from own-cell mean','Tmax minus Jul-Sep mean (degrees C)'),(t,'turbo',Normalize(-5,50),'F. Turbo baseline: same Tmax as A/B','Tmax (degrees C)')]
    for ax,(a,cmap,norm,title,label) in zip(axes.flat,panels):im=ax.pcolormesh(x,y,a,cmap=cmap,norm=norm,shading='auto');geo(ax,title);fig.colorbar(im,ax=ax,shrink=.8,label=label)
    fig.suptitle('Color is an encoding choice; a diverging scale needs a meaningful center',fontsize=20,weight='bold');fig.supxlabel('August 22, 2023. A/B/F show identical absolute temperatures; C/D identical rainfall.\nE changes the quantity to a within-period departure centered on zero, not a long-term climate anomaly.',fontsize=12)
    save(fig,'images/scivis/scivis_color_experiments.png')

def rain_normalization():
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_n8_s6.npz') as z:p=z['pr'];x=z['lon'];y=z['lat']
    dates=json.loads((ROOT/'data/scivis/manifest.json').read_text())['sample_dates'];peaks=np.nanmax(p,axis=(1,2));chosen=[int(peaks.argmin()),int(peaks.argmax())];global_max=float(peaks.max())
    fig,axes=plt.subplots(2,2,figsize=(15,10),layout='constrained')
    for row,i in enumerate(chosen):
        for col in range(2):
            maximum=global_max if col==0 else float(peaks[i]);im=axes[row,col].pcolormesh(x,y,p[i],cmap='Blues',vmin=0,vmax=maximum,shading='auto');geo(axes[row,col],f'{dates[i]} | {"fixed eight-date" if col==0 else "daily"} range');fig.colorbar(im,ax=axes[row,col],label='Rain (mm/day)',shrink=.8)
    fig.suptitle('Supplement: rainfall also changes meaning under local color rescaling',fontsize=20,weight='bold');fig.supxlabel('Dates minimize/maximize the eight sampled spatial rain maxima; same values in each row.\nLinear scale in both columns; fixed normalization compares amounts, daily normalization emphasizes within-date contrast.',fontsize=12)
    save(fig,'output/review_revision/rain_global_local.png');FACTS['rain_normalization']=dict(dates=[dates[i] for i in chosen],global_max_mm_day=global_max,daily_maxima_mm_day=[float(peaks[i]) for i in chosen])

def main():
    OUT.mkdir(parents=True,exist_ok=True);plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    from build_quality_figures import weather_figures
    weather_figures() # Retain exact two-decimal area labels in the four-field overlay.
    d=weather_data();network();matrix();changes(d);hovmoller(d);contours(d);quiver(d);roses();color_comparison(d);rain_normalization()
    (OUT/'facts.json').write_text(json.dumps(FACTS,indent=2),encoding='utf-8');print(json.dumps(FACTS,indent=2))

if __name__=='__main__':main()
