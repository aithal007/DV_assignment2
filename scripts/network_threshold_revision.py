"""All-pair threshold diagnostics, readable report figures and current report text."""
from pathlib import Path
import json,html
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/network_revision'

def inputs():
    d=json.loads((ROOT/'data/country_network_2020.json').read_text())
    a=json.loads((ROOT/'data/network_threshold_audit.json').read_text())
    g=nx.Graph();g.add_nodes_from((n['id'],n) for n in d['nodes'])
    g.add_weighted_edges_from((e['source'],e['target'],e['similarity']) for e in d['edges'])
    groups=sorted((c for c in nx.community.greedy_modularity_communities(g,weight='weight') if len(c)>1),key=lambda c:(-len(c),min(c)))
    return d,a,g,groups

def save(fig,name):
    OUT.mkdir(exist_ok=True,parents=True)
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=220,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def draw_layouts():
    d,a,g,groups=inputs();v=np.array([e['similarity'] for e in d['all_edges']]);t=a['threshold']
    fig=plt.figure(figsize=(15,10));gs=fig.add_gridspec(2,6,height_ratios=[.72,1],hspace=.48)
    ax=fig.add_subplot(gs[0,:3]);ax.hist(v,bins=np.linspace(0,1,41),color='#b5c7d2',edgecolor='white')
    ax.axvline(t,color='#d65b32',lw=2,label=f'95th percentile = {t:.6f}');ax.set(xlabel='Pair similarity: 1 / (1 + standardized distance)',ylabel='Number of country pairs',title='A  Distribution over all 15,931 pairs');ax.legend(frameon=False,fontsize=10)
    ax=fig.add_subplot(gs[0,3:]);sweep=pd.read_csv(OUT/'threshold_topology.csv');q=100*sweep['quantile']
    ax.plot(q,sweep.largest_component,color='#087f83',lw=2,label='Largest connected component')
    ax.plot(q,sweep.isolates,color='#7655a3',lw=2,label='Isolated countries')
    ax.axvline(95,color='#d65b32',lw=2);ax.scatter([95,95],[167,12],color=['#087f83','#7655a3'],zorder=4)
    ax.set(xlabel='Similarity percentile cutoff (higher = fewer edges)',ylabel='Number of countries',title='B  Sparsity changes connectedness',ylim=(0,185),xlim=(80,99))
    ax.legend(frameon=False,fontsize=9,loc='center left');ax.text(.96,.44,'P95: 797 edges\n167 in largest component\n12 isolates',ha='right',transform=ax.transAxes,fontsize=10)
    neighbors=sorted(g.neighbors('IND'));colors=dict(zip(neighbors,plt.get_cmap('tab20').colors))
    for col,(name,pos) in enumerate(d['layouts'].items()):
        ax=fig.add_subplot(gs[1,2*col:2*col+2])
        for e in d['edges']:
            near='IND' in [e['source'],e['target']];other=e['target'] if e['source']=='IND' else e['source'];p,q=pos[e['source']],pos[e['target']]
            ax.plot([p[0],q[0]],[p[1],q[1]],color=colors[other] if near else '#ced7dd',lw=1.7 if near else .45,alpha=1 if near else .35)
        for n,p in pos.items():ax.scatter(*p,s=55 if n=='IND' else 25 if n in neighbors else 8,color='#102638' if n=='IND' else colors.get(n,'#b5c7d2'),zorder=3)
        ax.annotate('India',pos['IND'],xytext=(8,12),textcoords='offset points',fontsize=11,weight='bold',bbox=dict(fc='white',ec='none',alpha=.8))
        ax.set_title(f'{name}: same {len(neighbors)} India links',fontsize=12);ax.axis('off');ax.set_aspect('equal')
    fig.suptitle('From a complete similarity network to a readable threshold graph',fontsize=19,weight='bold',y=.97)
    fig.text(.5,.03,'Same threshold and edges in all three layouts. Spring/Spectral put the 12 isolates in a separate bottom row.\nDrawing distance is not measured similarity. Slider zero restores every pair.',ha='center',fontsize=11)
    fig.subplots_adjust(top=.90,bottom=.10)
    save(fig,'network_threshold_layouts')
    return {}

def draw_nodetrix():
    d,a,g,groups=inputs();owner={n:i for i,c in enumerate(groups) for n in c};inner=sum(g.subgraph(c).number_of_edges() for c in groups)
    # Smallest non-clique group with at least five countries supports a readable
    # matrix containing actual links and gaps, chosen by a reproducible rule.
    choices=[(i,c) for i,c in enumerate(groups) if len(c)>=5 and g.subgraph(c).number_of_edges()<len(c)*(len(c)-1)//2]
    i,c=min(choices,key=lambda z:(len(z[1]),z[0]));codes=sorted(c);matrix=nx.to_numpy_array(g,nodelist=codes,weight=None).astype(int)
    fig,(left,right)=plt.subplots(1,2,figsize=(15,8),gridspec_kw={'width_ratios':[1,1.15]},layout='constrained')
    centers=np.c_[.5+.34*np.cos(np.linspace(0,2*np.pi,len(groups),endpoint=False)),.5+.34*np.sin(np.linspace(0,2*np.pi,len(groups),endpoint=False))]
    palette=plt.get_cmap('tab10').colors;cell=.0045;orders=[sorted(c) for c in groups]
    def endpoint(n,other):
        k=owner[n];cx,cy=centers[k];side=len(orders[k])*cell;offset=(orders[k].index(n)+.5)*cell
        return (cx+np.sign(other[0]-cx)*side/2,cy+side/2-offset)
    for u,v in g.edges:
        if owner[u]!=owner[v]:
            p,q=endpoint(u,centers[owner[v]]),endpoint(v,centers[owner[u]])
            left.plot([p[0],q[0]],[p[1],q[1]],color='#a5afb8',lw=.5,alpha=.45)
    for k,order in enumerate(orders):
        x,y=centers[k];side=len(order)*cell
        left.imshow(nx.to_numpy_array(g,nodelist=order,weight=None),cmap=ListedColormap(['#f4f6f7',palette[k]]),vmin=0,vmax=1,extent=(x-side/2,x+side/2,y-side/2,y+side/2),interpolation='nearest',zorder=3)
        left.text(x,y+side/2+.025,f'G{k+1}: {len(order)}',ha='center',fontsize=11)
    left.set(xlim=(-.05,1.05),ylim=(-.22,1.05));left.axis('off');left.set_title(f'A  {len(groups)} modularity communities; {a["isolates"]} isolates',loc='left')
    for x,node in zip(np.linspace(.02,.98,a['isolates']),sorted(nx.isolates(g))):
        left.scatter(x,-.075,s=20,color='#657682');left.text(x,-.10,node,ha='center',va='top',fontsize=7,rotation=60)
    left.text(.5,-.23,f'{inner} internal edges; {g.number_of_edges()-inner} between groups\nIsolates shown individually; they are not extra communities with links.',ha='center',fontsize=9)
    shown=matrix.astype(float);np.fill_diagonal(shown,.45)
    right.imshow(shown,cmap=ListedColormap(['white','#dce2e6','#168a8a']),vmin=0,vmax=1,interpolation='nearest')
    right.set_xticks(range(len(codes)),codes,rotation=65,ha='right',fontsize=9)
    right.set_yticks(range(len(codes)),[f'{g.nodes[n]["country"]} ({int(matrix[j].sum())})' for j,n in enumerate(codes)],fontsize=9)
    right.set_xticks(np.arange(-.5,len(codes),1),minor=True);right.set_yticks(np.arange(-.5,len(codes),1),minor=True);right.grid(which='minor',color='#bac9d0',lw=.4);right.tick_params(which='both',length=0)
    right.set_title(f'B  Group {i+1}: {matrix.sum()//2} / {len(codes)*(len(codes)-1)//2} possible pairs',loc='left')
    fig.suptitle('NodeTrix: inspect the links retained by the similarity threshold',fontsize=18,weight='bold')
    fig.supxlabel('Teal = similarity meets threshold; white = below threshold. Gray diagonal = self-pair, excluded.\nEach undirected link appears twice. Row labels give within-group degree. Groups depend on threshold and modularity.',fontsize=10)
    save(fig,'nodetrix_threshold_detail')
    pd.DataFrame(matrix,index=codes,columns=codes).to_csv(OUT/'nodetrix_detail_matrix.csv')
    counts=matrix.sum(1);maxn=codes[int(counts.argmax())];minn=codes[int(counts.argmin())]
    facts=dict(group=i+1,countries=len(codes),internal_edges=int(matrix.sum()//2),possible_edges=len(codes)*(len(codes)-1)//2,all_groups=len(groups),all_internal_edges=inner,between_group_edges=g.number_of_edges()-inner,isolates=a['isolates'],max_country=g.nodes[maxn]['country'],max_degree=int(counts.max()),min_country=g.nodes[minn]['country'],min_degree=int(counts.min()),india_neighbors=sorted(g.neighbors('IND')))
    (OUT/'facts.json').write_text(json.dumps(facts,indent=2))
    return facts

def apply(figures,content):
    d,a,g,groups=inputs();facts=json.loads((OUT/'facts.json').read_text());t=a['threshold'];by={f['figure']:f for f in figures}
    names=', '.join(g.nodes[n]['country'] for n in facts['india_neighbors'])
    sweep='; '.join(f"P{100*s['quantile']:g}: {s['edges']:,} edges, {s['isolates']} isolates" for s in a['threshold_sweep'])
    stability=[p['jaccard'] for p in a['perturbations']]
    f=by[1];f['path']='output/network_revision/network_threshold_layouts.png'
    f['title']='Complete pair similarities, threshold selection and three layouts.'
    f['caption']=f'All 15,931 pair similarities; the P95 threshold {t:.6f} retains 797 edges among 179 countries, including 12 isolated nodes. Three layouts hold that graph fixed.'
    f['explanation']=[
        'How can a dense complete similarity network be filtered transparently before comparing layouts?',
        'The histogram counts all unique country pairs. The second panel sweeps percentile cutoffs from P80 to P99 and counts countries in the largest connected component and countries with no retained edge. The vertical lines mark P95. The lower panels draw the same 797 retained edges with Spring, Spectral and Circular positions; India and its twelve links are highlighted.',
        'The full similarity distribution makes the filtering decision visible instead of silently imposing nearest neighbors. Three layouts then test representation effects on one fixed threshold graph. A shared threshold treats every country pair by the same rule.',
        'The upper 5% is an analyst-selected starting view, not a significance cutoff or unique optimum. Isolates remain countries in the analysis. Standardization, features and threshold influence the edges; positions do not define neighbors.',
        'Thresholding makes the complete network readable, but changes which pairs count as linked. India has twelve retained neighbors in every layout; geographic distance on the page is not measured similarity.'
    ]
    f['detailed_interpretation']=f'The complete similarity network contains 179 x 178 / 2 = 15,931 unique undirected country pairs. We standardize the four 2020 indicators and calculate s = 1/(1+d), where d is Euclidean distance. The distribution is concentrated at lower similarities; the median is {np.median([e["similarity"] for e in d["all_edges"]]):.3f}. We retain the strongest 5%, giving a threshold of {t:.6f} and 797 edges. This rule is declared for a sparse starting view, rather than selected to produce an attractive grouping.\n\nThe threshold graph keeps all 179 nodes. Twelve countries have no qualifying pair, and the largest connected component contains 167 countries. Isolation here means no profile exceeds this chosen cutoff, not absence of internet connections. The browser starts at the exact threshold and can return to zero to display the complete graph. Layout coordinates are computed on the default filtered graph and remain fixed when the slider changes.\n\nIndia has twelve retained neighbors: {names}. The identical edge list is drawn in all three layouts. Lines can become longer or cross differently without changing either endpoint or similarity.\n\nThreshold sensitivity is explicit: {sweep}. Across 30 seeded trials adding Gaussian noise with standard deviation 0.02 in standardized units, fixed-threshold edge Jaccard overlap ranges from {min(stability):.3f} to {max(stability):.3f} (mean {np.mean(stability):.3f}). Jaccard is shared retained pairs divided by their union. This is a small-input robustness experiment, not a formal uncertainty estimate or a named perturbation threshold-selection algorithm.'
    research=json.loads((OUT/'method_research.json').read_text())
    f['detailed_interpretation']+='\n\nPanel B shows core fragmentation and isolation as the cutoff rises. Keeping all countries connected requires a cutoff of '+f'{research["connected_cutoff"]:.3f} and retains {research["connected_edges"]:,} edges. A maximum spanning tree keeps 178 edges but deletes cycles and many strong pairs. These alternatives answer different questions.'
    f['detailed_interpretation']+='\n\nAt the same top-5% density, median/IQR scaling gives edge Jaccard 0.801, rank scaling 0.460, and omitting one indicator 0.338-0.512. Standardization balances scales without removing feature correlation. Small-noise stability therefore cannot establish unique groups. We retain the interpretable four-indicator definition: similarities are descriptive, not physical links, causal effects or significance tests. The supporting method gallery supplies a continuous pair matrix, sensitivity plots, tables and research sources.'
    f=by[3];f['path']='output/network_revision/nodetrix_threshold_detail.png';f['title']='NodeTrix: links and gaps after threshold filtering.'
    f['caption']=f'Threshold graph: {facts["all_groups"]} modularity communities and {facts["isolates"]} isolates. Enlarged group {facts["group"]}: {facts["internal_edges"]} of {facts["possible_edges"]} possible pairs retained.'
    f['explanation']=[
        'Which individual relationships are hidden by the grouped threshold graph?',
        f'The overview replaces each non-singleton modularity group with an adjacency matrix and retains cross-group lines. The right view enlarges group {facts["group"]}, with {facts["countries"]} countries. Teal means similarity meets the global threshold; white means it does not. Gray diagonal self-pairs are excluded. Row labels show within-group degree.',
        'Matrix cells make exact retained pairs and gaps checkable without relying on crowded lines. The detail group is selected reproducibly as the smallest group with at least five countries that is not a clique. Isolates are explicitly reported rather than silently dropped.',
        'Groups are weighted greedy-modularity summaries of the threshold graph, not natural country types. A white cell does not mean no measured similarity: every distinct pair has a score, but this pair falls below the current cutoff.',
        f'Group {facts["group"]} retains {facts["internal_edges"]} of {facts["possible_edges"]} possible pairs. {facts["max_country"]} has {facts["max_degree"]} within-group links and {facts["min_country"]} has {facts["min_degree"]}; a shared group label still hides differences in individual relationships.'
    ]
    f['detailed_interpretation']=f'The revised threshold graph has {facts["all_internal_edges"]} edges inside six non-singleton modularity groups and {facts["between_group_edges"]} between them. Twelve isolated country nodes are retained separately; they have no edges to place in a matrix. These groups summarize the retained graph and must not be read as continents, income classes or inherent country categories.\n\nGroup {facts["group"]} contains {facts["countries"]} countries and {facts["internal_edges"]} of its {facts["possible_edges"]} possible pairs. {facts["max_country"]} has {facts["max_degree"]} internal links, while {facts["min_country"]} has {facts["min_degree"]}. Follow a named row across to a country column: teal shows a retained pair and white shows a below-threshold pair. The mirrored cell represents the same undirected pair, so count only one triangle.\n\nUnlike an observed physical-network absence, white here is the result of filtering a measured pair score. Lowering the threshold can fill a white cell, and changing the threshold can change the modularity groups. The same all-pair data therefore supports several filtered views; the cutoff must always accompany a claim about connectedness or group membership.'
    old='We standardize the indicators and join each country to its five closest matches, giving 590 undirected links.'
    new=f'Following the instructor clarification, we compute every one of the 15,931 unique country-pair similarities as 1/(1+Euclidean distance) on the four z-scored indicators. The declared 95th-percentile threshold ({t:.6f}) retains 797 edges; all 179 nodes, including 12 isolates, remain. Figure 1 shows the distribution and connectivity sensitivity; its interpretation reports perturbation and metric checks.'
    content.DATA=content.DATA.replace(old,new)
    content.DATA=content.DATA.replace('NodeTrix groups the graph using weighted greedy modularity, which favors more links inside groups and fewer between groups.','NodeTrix groups the filtered graph using weighted greedy modularity; six non-singleton groups are shown separately from isolated nodes.')

def build():
    from research_network_methods import build as research_build
    research_build()
    draw_layouts();facts=draw_nodetrix();d,a,g,groups=inputs()
    pd.DataFrame(a['threshold_sweep']).to_csv(OUT/'threshold_sensitivity.csv',index=False)
    pd.DataFrame(a['perturbations']).to_csv(OUT/'input_perturbations.csv',index=False)
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Network threshold evidence</title><style>body{font:18px/1.5 Arial;max-width:1200px;margin:30px auto}img{width:100%}</style><h1>Complete similarity network and threshold evidence</h1><p>All 15,931 country pairs are retained in the source data. The default P95 threshold shows 797 edges and retains 12 isolated countries.</p><img src="network_threshold_layouts.png"><p><a href="threshold_sensitivity.csv">Threshold sweep</a> | <a href="input_perturbations.csv">30 input-perturbation trials</a> | <a href="../../data/network_all_pair_similarities.csv">All pair scores</a> | <a href="../../web/network.html">Interactive graph</a></p><img src="nodetrix_threshold_detail.png">',encoding='utf8')
    from research_network_methods import write_gallery
    write_gallery()
    print(json.dumps(facts,indent=2))

def readme_section():
    return '''
## Network revision following instructor clarification (29 October 2026)

The network now begins with all 15,931 unique pairs among 179 complete 2020 country profiles. Similarity is `1/(1 + Euclidean distance)` after z-scoring four indicators. `data/network_all_pair_similarities.csv` and the `all_edges` field in `data/country_network_2020.json` retain the complete pair universe. The JSON `edges` field is the default filtered graph, not the source universe.

The default threshold is the 95th percentile, **0.5697629885414606**, retaining **797 edges** (about 5% of pairs). All 179 nodes remain, including **12 isolates**. This is a declared sparse starting view, not a statistically optimal cutoff. The report shows the score histogram and connectivity across 77 percentile cutoffs. Nearby thresholds and 30 seeded small-input perturbations quantify sensitivity. The perturbation experiment is not claimed to implement a named threshold-selection method.

The 30 October research review adds median/IQR scaling, rank scaling and four leave-one-indicator-out checks, each with its own P95 cutoff. Edge Jaccard is 0.801 for IQR, 0.460 for ranks and 0.338-0.512 for feature omission. The highest cutoff preserving full connectivity retains 11,526 edges, so it is not adopted as the default. The [method review](output/network_revision/index.html) explains the alternatives, primary sources and two supporting plots (metric sensitivity and the continuous all-pair matrix). Figure 1 replaces the old retention curve with connectivity sensitivity; Figure 3 now draws all isolates. Run `python scripts/network_threshold_revision.py` to recreate these checks, then rebuild and sync the report. The baseline graph and video numerical claims remain unchanged.

The browser slider filters all pair scores, not a nearest-neighbor subset. Set it to zero for the complete graph; Reset restores the exact default. Layout coordinates stay fixed while filtering. Spring and Spectral lay out the 167-node connected core and place the 12 isolates on a separate bottom row; Circular includes all nodes. NodeTrix has six non-singleton groups plus 12 isolates; group 5 has 93 of 105 possible pairs. Groups and white matrix cells must be interpreted relative to the displayed threshold.

Rebuild from `ass2`:

```powershell
python scripts/build_infovis_data.py
python scripts/preview_lecture_extensions.py
python scripts/network_threshold_revision.py
python scripts/verify_network_threshold.py
python scripts/build_a1_style_report.py
python scripts/sync_report_delivery.py
python scripts/verify_story_report.py
python scripts/package_selected_report.py
```

Evidence: `data/network_threshold_audit.json`, `output/network_revision/threshold_sensitivity.csv`, `input_perturbations.csv`, `facts.json`, and the [diagnostic gallery](output/network_revision/index.html). Browser controls were tested with the all-pair source. Earlier archived reports and screenshots describe superseded network rules.
'''

if __name__=='__main__':build()
