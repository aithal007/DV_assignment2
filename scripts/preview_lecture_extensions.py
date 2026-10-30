"""Standalone lecture-inspired previews. Does not alter report or figure numbering."""
from pathlib import Path
import html
import json
import itertools
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch, Rectangle, Patch
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/lecture_previews'
OUT.mkdir(parents=True, exist_ok=True)
INK = '#193044'
COLORS = ['#0072b2', '#d55e00', '#009e73', '#8b5fbf', '#b68620', '#cb699e', '#487b85']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
    'axes.spines.top': False, 'axes.spines.right': False, 'text.color': INK,
    'axes.labelcolor': INK, 'axes.titlecolor': INK, 'svg.fonttype': 'none'})
PREVIEWS = []
METRICS = {}


def save(fig, key, title, question, takeaway, limits):
    fig.savefig(OUT / f'{key}.png', dpi=190, bbox_inches='tight', facecolor='white')
    fig.savefig(OUT / f'{key}.svg', bbox_inches='tight', facecolor='white')
    plt.close(fig)
    PREVIEWS.append(dict(key=key, title=title, question=question,
                         takeaway=takeaway, limits=limits))


def graph_previews():
    data = json.loads((ROOT / 'data/country_network_2020.json').read_text())
    g = nx.Graph()
    g.add_nodes_from((n['id'], n) for n in data['nodes'])
    g.add_weighted_edges_from((e['source'], e['target'], e['similarity']) for e in data['edges'])
    groups = sorted(nx.community.greedy_modularity_communities(g, weight='weight'),
                    key=lambda c: (-len(c), min(c)))
    isolates=list(nx.isolates(g))
    groups=[c for c in groups if len(c)>1]
    owner = {node: i for i, group in enumerate(groups) for node in group}
    orders = [sorted(c) for c in groups]
    pd.DataFrame([dict(group=i+1, row_column=j+1, **g.nodes[n])
                  for i, order in enumerate(orders) for j, n in enumerate(order)]).to_csv(
                      OUT / 'community_country_order.csv', index=False)
    inner = sum(g.subgraph(c).number_of_edges() for c in groups)
    fields = ['internet_pct', 'landlines_per100', 'broadband_per100', 'mobile_per100']
    summaries = pd.DataFrame([dict(group=i+1, countries=len(c),
        density=nx.density(g.subgraph(c)), **{f: np.mean([g.nodes[n][f] for n in c])
        for f in fields}) for i, c in enumerate(groups)])
    summaries.to_csv(OUT / 'community_profiles.csv', index=False)
    # Check grouping dependence on the all-pair similarity threshold.
    raw = np.array([[n[f] for f in fields] for n in data['nodes']])
    scaled = (raw - raw.mean(0)) / raw.std(0)
    dist = np.linalg.norm(scaled[:, None] - scaled[None, :], axis=2)
    np.fill_diagonal(dist, np.inf)
    ids = [n['id'] for n in data['nodes']]
    checks = []
    all_pairs=data['all_edges']
    for quantile in [.90,.95,.975]:
        h = nx.Graph(); h.add_nodes_from(ids)
        threshold=float(np.quantile([e['similarity'] for e in all_pairs],quantile))
        h.add_weighted_edges_from((e['source'],e['target'],e['similarity']) for e in all_pairs if e['similarity']>=threshold)
        for method, seed in [('greedy', None)] + [('louvain', s) for s in range(5)]:
            part = (nx.community.greedy_modularity_communities(h, weight='weight')
                    if method == 'greedy' else nx.community.louvain_communities(h, weight='weight', seed=seed))
            checks.append(dict(quantile=quantile,threshold=threshold,method=method,seed=seed,groups=len(part),
                modularity=nx.community.modularity(h, part, weight='weight'),
                group1_best_jaccard=max(len(groups[0]&c)/len(groups[0]|c) for c in part),
                group2_best_jaccard=max(len(groups[1]&c)/len(groups[1]|c) for c in part)))
    pd.DataFrame(checks).to_csv(OUT / 'community_sensitivity.csv', index=False)
    METRICS['network'] = dict(countries=len(g), edges=g.number_of_edges(),
        density=nx.density(g), groups=len(groups), internal_edges=inner,
        external_edges=g.number_of_edges()-inner,
        isolates=len(isolates),weighted_modularity=nx.community.modularity(g, groups+[frozenset([n]) for n in isolates], weight='weight'),
        sensitivity=checks)
    assert sum(len(c) for c in groups)+len(isolates) == len(g)

    fig, ax = plt.subplots(figsize=(13, 12))
    theta = np.linspace(np.pi/2, np.pi/2 + 2*np.pi, len(groups), endpoint=False)
    centers = np.c_[.5 + .36*np.cos(theta), .5 + .35*np.sin(theta)]
    cell = .0054
    def endpoint(n, other):
        i = owner[n]; center = centers[i]; side = cell*len(orders[i])
        offset = (orders[i].index(n)+.5)*cell
        delta = other-center
        if abs(delta[0]) >= abs(delta[1]):
            return center + np.array([np.sign(delta[0])*side/2, side/2-offset])
        return center + np.array([-side/2+offset, np.sign(delta[1])*side/2])
    external = [(u, v) for u, v in g.edges if owner[u] != owner[v]]
    for u, v in external:
        a = endpoint(u, centers[owner[v]]); b = endpoint(v, centers[owner[u]])
        ax.plot([a[0], b[0]], [a[1], b[1]], color='#7c8b98', lw=.8, alpha=.38, zorder=1)
    for i, order in enumerate(orders):
        side = cell*len(order); cx, cy = centers[i]
        matrix = nx.to_numpy_array(g, nodelist=order, weight=None)
        assert int(matrix.sum()) == 2*g.subgraph(order).number_of_edges()
        ax.imshow(matrix, cmap=ListedColormap(['#f0f3f5', COLORS[i]]),
            vmin=0, vmax=1, interpolation='nearest', origin='upper',
            extent=(cx-side/2, cx+side/2, cy-side/2, cy+side/2), zorder=3)
        ax.add_patch(Rectangle((cx-side/2, cy-side/2), side, side,
                              facecolor='none', edgecolor=COLORS[i], lw=1.4, zorder=4))
        ax.text(cx, cy+side/2+.016, f'G{i+1}: {len(order)} countries', ha='center',
                va='bottom', fontsize=11, weight='bold')
        ax.text(cx, cy-side/2-.014, f'Internal density {nx.density(g.subgraph(order)):.0%}',
                ha='center', va='top', fontsize=9)
    ax.text(.5, .5, f'{inner} internal edges\n{len(external)} between groups',
            ha='center', va='center', fontsize=13,
            bbox=dict(facecolor='white', edgecolor='none', pad=8), zorder=5)
    ax.set(xlim=(-.04, 1.04), ylim=(-.02, 1.06)); ax.axis('off')
    fig.suptitle('NodeTrix preview: inspect groups without losing their connections',
                 fontsize=18, y=.98)
    fig.text(.5, .94, f'2020 threshold graph | {len(g)} countries | {g.number_of_edges()} edges | {len(isolates)} isolates (no matrix)', ha='center')
    fig.text(.5, .04, 'Colored cells = internal adjacency; gray lines = individual external edges attached to country rows/columns.\n'
        'Alphabetical ISO-code order within each matrix is supplied in community_country_order.csv.\n'
        'Static overview; groups use weighted greedy modularity. Links describe profile similarity.', ha='center', fontsize=10)
    save(fig, 'nodetrix', 'NodeTrix overview', 'Which groups are internally connected, and how do groups connect?',
        f'{inner} of {g.number_of_edges()} edges fall inside {len(groups)} connected groups; {g.number_of_edges()-inner} join groups. {len(isolates)} isolated countries remain in the node set.',
        'The grouping optimizes internal connectivity on this derived graph. It is not independent proof of natural country types. '
        'Matrix sizes depend on group size; compare numerical density labels. Country labels need zoom/details in a future interactive version.')

    fig, axes = plt.subplots(1, 4, figsize=(15, 5.7), sharey=True, layout='constrained')
    labels = ['Internet adoption (%)', 'Landlines / 100', 'Broadband / 100', 'Mobile / 100']
    for ax, f, label in zip(axes, fields, labels):
        for i, group in enumerate(groups):
            values = np.array([g.nodes[n][f] for n in group]); q = np.percentile(values, [25, 75])
            ax.plot(q, [i, i], color=COLORS[i], lw=7, alpha=.4, solid_capstyle='round')
            ax.scatter(values.mean(), i, color=COLORS[i], s=65, zorder=3)
            ax.annotate(f'{values.mean():.1f}', (values.mean(), i), xytext=(5, 7),
                        textcoords='offset points', fontsize=9)
        ax.set_xlabel(label); ax.set_xlim(left=0); ax.grid(axis='x', alpha=.18)
        ax.set_ylim(len(groups)-.4, -.65)
    axes[0].set_yticks(range(len(groups)), [f'G{i+1} (n={len(g)})' for i, g in enumerate(groups)])
    fig.suptitle('Similar adoption levels can accompany different infrastructure profiles', fontsize=18)
    fig.supxlabel('Dots = country means; thick segments = country interquartile ranges. '
        'Separate horizontal scales. Exploratory groups from the same four indicators.', fontsize=10)
    save(fig, 'group_profiles', 'Group profiles', 'Can similar internet adoption coexist with different infrastructure profiles?',
        'Group means and interquartile ranges describe the revised threshold graph; see community_profiles.csv for exact values.',
        'Descriptive country-weighted summaries of groups derived from these indicators. '
        'Subscription intensities are not percentages of people. Group sensitivity is exported separately.')


def ribbon(ax, x0, x1, y0, y1, height, color):
    mid = (x0+x1)/2
    vertices = [(x0,y0), (mid,y0), (mid,y1), (x1,y1), (x1,y1+height),
                (mid,y1+height), (mid,y0+height), (x0,y0+height), (x0,y0)]
    codes = [MPath.MOVETO] + [MPath.CURVE4]*3 + [MPath.LINETO] + [MPath.CURVE4]*3 + [MPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MPath(vertices,codes), facecolor=color, edgecolor='white', lw=.4, alpha=.65))


def adoption_transitions():
    panel = pd.read_csv(ROOT/'data/internet_panel_2000_2020.csv')
    years = [2000, 2010, 2020]
    wide = panel.pivot(index='code', columns='year', values='internet_users_share_pct')[years].dropna()
    bands = np.digitize(wide.to_numpy(), [25, 50, 75], right=False)
    n = len(wide); counts = np.array([np.bincount(bands[:,i], minlength=4) for i in range(3)])
    assert n == 159 and np.all(counts.sum(axis=1)==n)
    labels = ['Below 25%', '25 to <50%', '50 to <75%', '75 to 100%']
    palette = ['#b9c9d6', '#81b0bc', '#39829b', '#175271']
    starts = np.c_[np.zeros(3), np.cumsum(counts[:,:-1],axis=1)] + np.arange(4)*7
    fig, ax = plt.subplots(figsize=(13, 7.6))
    flows=[]
    for t in range(2):
        source_offset=np.zeros(4); target_offset=np.zeros(4)
        for a,b in itertools.product(range(4),repeat=2):
            number=int(((bands[:,t]==a)&(bands[:,t+1]==b)).sum())
            if not number: continue
            ribbon(ax,t+.045,t+1-.045, starts[t,a]+source_offset[a],
                   starts[t+1,b]+target_offset[b],number,palette[a])
            source_offset[a]+=number; target_offset[b]+=number
            flows.append(dict(from_year=years[t],to_year=years[t+1],from_band=labels[a],to_band=labels[b],countries=number))
        assert np.array_equal(source_offset,counts[t]) and np.array_equal(target_offset,counts[t+1])
    for t in range(3):
        for band in range(4):
            y=starts[t,band]; h=counts[t,band]
            if h:
                ax.add_patch(Rectangle((t-.045,y),.09,h,color=palette[band],zorder=4))
                x=t+.065 if t<2 else t-.065
                ax.text(x,y+h/2,f'{labels[band]}: {h}',ha='left' if t<2 else 'right',
                        va='center',fontsize=10,zorder=5,
                        bbox=dict(facecolor='white',edgecolor='none',pad=1,alpha=.85))
    ax.set(xlim=(-.18,2.18),ylim=(n+30,-12)); ax.axis('off')
    for t,year in enumerate(years): ax.text(t,-7,str(year),ha='center',weight='bold',fontsize=16)
    fig.suptitle('How do countries move between internet-adoption bands?',fontsize=19,y=.98)
    fig.text(.5,.92,'159 matched countries at all three dates | ribbon thickness = number of countries',ha='center')
    fig.text(.5,.04,'Ribbons show adjacent-date transitions; identities are not traceable through the middle column.\n'
        'Bands are analyst-defined, with exact 25%, 50% and 75% boundaries assigned to the higher band.\n'
        'Every country has equal weight; ribbons do not represent people or internet traffic.',ha='center',fontsize=10)
    pd.DataFrame(flows).to_csv(OUT/'adoption_transitions.csv',index=False)
    wide.assign(**{f'band_{y}':[labels[b] for b in bands[:,i]] for i,y in enumerate(years)}).to_csv(
        OUT/'adoption_country_membership.csv')
    METRICS['adoption']=dict(countries=n,years=years,band_counts=counts.tolist(),
        moving_up_2000_2020=int((bands[:,2]>bands[:,0]).sum()),
        same_band_2000_2020=int((bands[:,2]==bands[:,0]).sum()))
    save(fig,'adoption_alluvial','Adoption-band transitions','Who moves between adoption bands as the overall distribution changes?',
        f'The >=75% band grows from {counts[0,3]} to {counts[2,3]} countries on a fixed 159-country panel.',
        'Country counts, not population. Band thresholds lose within-band change. '
        'Two adjoining ribbons do not uniquely identify the same country path; CSV contains the actual identities.')


def weather_previews():
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz') as z:
        t,p,s,d=[z[k].astype(float) for k in ['tmmx','pr','vs','th']]
        dates,lat=[z[k] for k in ['dates','lat']]
    valid=np.all(np.isfinite(t)&np.isfinite(p)&np.isfinite(s)&np.isfinite(d),axis=0)
    w=np.broadcast_to(np.cos(np.deg2rad(lat))[:,None],valid.shape)[valid]
    months=np.array([str(x)[5:7] for x in dates])
    t,p,s,d=[a[:,valid] for a in [t,p,s,d]]
    assert len(dates)==92 and valid.sum()==13416
    assert t.max()<70 and t.min()>-50 and p.min()>=0 and s.min()>=0
    sets=[t>=35,p<1,s>=5]
    bits=sets[0].astype(np.uint8)+2*sets[1].astype(np.uint8)+4*sets[2].astype(np.uint8)
    def shares(code):
        return np.array([np.sum((code==i)*w)/(len(code)*w.sum())*100 for i in range(8)])
    freq=shares(bits); assert np.isclose(freq.sum(),100)
    sizes=np.array([np.sum(mask*w)/(92*w.sum())*100 for mask in sets])
    order=np.argsort(-freq,kind='stable'); x=np.arange(8)
    fig=plt.figure(figsize=(14,8)); gs=fig.add_gridspec(2,2,width_ratios=[1,3],height_ratios=[3,1],
        left=.12,right=.97,top=.81,bottom=.18,hspace=.04,wspace=.22)
    ax=fig.add_subplot(gs[0,1]); mx=fig.add_subplot(gs[1,1]); sizeax=fig.add_subplot(gs[1,0])
    colors=['#d55e00' if i==7 else '#39829b' if i else '#aebbc5' for i in order]
    ax.bar(x,freq[order],color=colors,width=.65)
    for j,i in enumerate(order): ax.text(j,freq[i]+.6,f'{freq[i]:.2f}%',ha='center',fontsize=10)
    ax.set(ylabel='Share of sampled area-days (%)',ylim=(0,float(freq.max())*1.15))
    ax.set_xticks([]); ax.grid(axis='y',alpha=.15)
    for j,i in enumerate(order):
        on=np.array([bool(i&(1<<b)) for b in range(3)])
        mx.scatter(np.full(3,j),np.arange(3),color='#dde3e8',s=65)
        if on.any():
            ys=np.flatnonzero(on); mx.plot([j,j],[ys.min(),ys.max()],c=colors[j],lw=2)
            mx.scatter(np.full(on.sum(),j),ys,c=colors[j],s=75,zorder=3)
    names=['Hot: Tmax >=35 C','Dry: rain <1 mm','Windy: speed >=5 m/s']
    mx.set(xlim=(-.6,7.6),ylim=(2.5,-.5)); mx.set_yticks([])
    mx.set_xticks(x,['None' if i==0 else '' for i in order]); mx.spines[['left','bottom']].set_visible(False)
    sizeax.barh(np.arange(3),sizes,color='#8aa5b5',height=.5)
    sizeax.set(ylim=(2.5,-.5),xlim=(100,0),xlabel='Set area-days (%)')
    sizeax.set_yticks(range(3),names,fontsize=10); sizeax.set_xticks([0,50,100]); sizeax.grid(axis='x',alpha=.15)
    for i,v in enumerate(sizes): sizeax.text(v+2,i,f'{v:.1f}',ha='right',va='center',fontsize=9)
    fig.suptitle('How often do hot, dry and windy conditions overlap?',fontsize=20,y=.97)
    fig.text(.5,.90,'Exact, mutually exclusive intersections | all 92 days | fixed 13,416-cell footprint',ha='center')
    fig.text(.5,.055,'Filled dots mean present; pale dots mean absent. All eight combinations sum to 100%.\n'
        'Cosine-latitude area weights; every day has equal weight. Thresholds describe this analysis, not official hazard classes.\n'
        'Windy is an analyst-selected daily speed threshold; daily means cannot resolve gusts or within-day coincidence.',ha='center',fontsize=10)
    save(fig,'weather_upset','Weather condition intersections','Does a frequent individual condition often coincide with the other conditions?',
        f'Hot/dry/windy together occupy {freq[7]:.2f}% of weighted area-days; hot/dry with any wind occupy {freq[3]+freq[7]:.2f}%.',
        'This is an area-day summary of daily fields, not population exposure or evidence of within-day simultaneity. '
        'For three sets a Venn diagram is also possible; aligned bars make exact quantities easier to compare here. '
        'The combined frequency is not a measure of persistence.')
    rows=[]
    for month in ['all','07','08','09']:
        values=shares(bits if month=='all' else bits[months==month])
        for i,v in enumerate(values): rows.append(dict(month=month,hot=bool(i&1),dry=bool(i&2),windy=bool(i&4),area_day_pct=v))
    pd.DataFrame(rows).to_csv(OUT/'weather_intersections.csv',index=False)
    sensitivities=[]
    for ht,rt,wt in itertools.product([33,35,37],[.5,1],[4,5,6]):
        val=float(np.sum(((t>=ht)&(p<rt)&(s>=wt))*w)/(92*w.sum())*100)
        sensitivities.append(dict(temperature_C=ht,rain_below_mm=rt,wind_at_least_ms=wt,all_three_area_day_pct=val))
    pd.DataFrame(sensitivities).to_csv(OUT/'weather_threshold_sensitivity.csv',index=False)

    # Meteorological direction: sectors say where the wind comes FROM.
    ndir=16; edges=np.array([0,2,4,6,8,np.inf]); sector=((d+360/ndir/2)%360/(360/ndir)).astype(int)
    speedbin=np.clip(np.digitize(s,edges)-1,0,4)
    fig,axes=plt.subplots(1,3,figsize=(14,6.3),subplot_kw={'projection':'polar'})
    tables=[]; values=[]
    for month in ['07','08','09']:
        take=months==month; total=take.sum()*w.sum()
        hist=np.array([[np.sum(((sector[take]==j)&(speedbin[take]==b))*w)/total*100
                        for j in range(ndir)] for b in range(5)])
        assert np.isclose(hist.sum(),100)
        values.append(hist)
        for b,j in itertools.product(range(5),range(ndir)):
            tables.append(dict(month=month,from_direction_degrees=j*360/ndir,speed_bin=b,area_day_pct=hist[b,j]))
    radialmax=float(np.ceil(max(h.sum(axis=0).max() for h in values)/2)*2)
    speedcolors=['#d5e6ee','#9dc6d9','#4f9cbf','#236e99','#173e67']
    for ax,hist,name in zip(axes,values,['July','August','September']):
        bottom=np.zeros(ndir)
        for b in range(5):
            ax.bar(np.arange(ndir)*2*np.pi/ndir,hist[b],bottom=bottom,width=2*np.pi/ndir*.9,
                   color=speedcolors[b],edgecolor='white',linewidth=.4)
            bottom+=hist[b]
        ax.set_theta_zero_location('N'); ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0,360,45),['N','NE','E','SE','S','SW','W','NW'])
        ax.set_ylim(0,radialmax); ax.set_yticks([4,8,12],['4%','8%','12%'])
        ax.set_title(name,pad=22,fontsize=15)
        ax.set_rlabel_position(110); ax.grid(alpha=.3)
    fig.suptitle('Do wind direction and speed distributions change across months?',fontsize=19,y=.99)
    fig.legend(handles=[Patch(facecolor=c,label=l) for c,l in zip(speedcolors,
        ['0 to <2','2 to <4','4 to <6','6 to <8','8+ m/s'])],loc='lower center',bbox_to_anchor=(.5,.09),ncol=5,frameon=False)
    fig.subplots_adjust(left=.04,right=.96,top=.81,bottom=.22,wspace=.35)
    fig.text(.5,.035,'Wind FROM direction | common radial scale: % of each month\'s weighted sampled area-days\n'
        '16 equal direction sectors; same fixed 13,416 cells. Daily direction and speed summaries; no spatial paths or gusts.',ha='center',fontsize=10)
    save(fig,'monthly_wind_roses','Monthly wind roses','Does a pooled wind summary conceal monthly differences?',
        'Compare speed composition and prevailing FROM-direction frequencies on identical radial scales.',
        'Pooled spatial summary loses geography. Sector size affects peaks. Daily fields cannot resolve gusts. '
        'Near-calm observations are retained in the lightest speed bin and their directions carry little physical meaning.')
    pd.DataFrame(tables).to_csv(OUT/'monthly_wind_rose.csv',index=False)
    METRICS['weather']=dict(days=92,cells=int(valid.sum()),set_area_day_pct=sizes.tolist(),
        intersections_area_day_pct=freq.tolist(),hot_dry_area_day_pct=float(freq[3]+freq[7]),
        hot_dry_windy_area_day_pct=float(freq[7]),wind_rose_common_radial_max_pct=radialmax,
        modal_from_direction_degrees=[int(h.sum(axis=0).argmax()*360/ndir) for h in values])
    assert np.isclose(freq[3]+freq[7],16.27447592706034)


def main():
    graph_previews(); adoption_transitions(); weather_previews()
    (OUT/'metrics.json').write_text(json.dumps(METRICS,indent=2),encoding='utf-8')
    (OUT/'manifest.json').write_text(json.dumps(PREVIEWS,indent=2),encoding='utf-8')
    body=[]
    for p in PREVIEWS:
        e=lambda value: html.escape(value)
        body.append(f'<section><h2>{e(p["title"])}</h2><p><b>Question:</b> {e(p["question"])}</p>'
            f'<a href="{p["key"]}.png"><img src="{p["key"]}.png" alt="{e(p["title"])}"></a>'
            f'<p><b>Reading:</b> {e(p["takeaway"])}</p><p><b>Limits:</b> {e(p["limits"])}</p>'
            f'<p><a href="{p["key"]}.svg">SVG</a> · <a href="{p["key"]}.png">PNG</a></p></section>')
    (OUT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Lecture-inspired previews</title>'
        '<style>body{max-width:1150px;margin:40px auto;padding:0 24px;font:17px/1.6 system-ui;color:#193044}'
        'h1{font-size:38px;line-height:1.15}h2{margin-top:48px}img{width:100%;height:auto}section{border-top:1px solid #dbe3e9;margin:36px 0}'
        'a{color:#0072b2}p{max-width:1000px}</style><h1>Beyond averages and snapshots</h1>'
        '<p>Five exploratory previews from existing assignment data, informed by the full lecture review. '
        'These are candidate extensions. The report and its 32 figure IDs are unchanged.</p>'
        '<p><a href="../../research/FULL_LECTURE_GRAPH_PLAN.md">Full lecture-to-data review</a> · '
        '<a href="metrics.json">Numerical audit</a> · <a href="community_sensitivity.csv">Grouping sensitivity</a></p>'
        +''.join(body)+'</html>',encoding='utf-8')
    print(json.dumps({'previews':len(PREVIEWS),'output':str(OUT),'network':{k:v for k,v in METRICS['network'].items() if k!='sensitivity'},
                      'adoption':METRICS['adoption'],'weather':METRICS['weather']},indent=2))


if __name__=='__main__': main()
