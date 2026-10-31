"""Reproducible threshold and metric sensitivity; no fitted ground-truth claim."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from build_infovis_data import PROFILE

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/network_revision'

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(ROOT/'data/processed/master_dataset_countries_only.csv')
    df=df.loc[df.year.eq(2020)].dropna(subset=['code']+PROFILE).sort_values('code')
    raw=df[PROFILE].to_numpy(float);codes=df.code.tolist();n=len(codes)
    z=(raw-raw.mean(0))/raw.std(0);ii,jj=np.triu_indices(n,1)
    def scores(x):return 1/(1+np.linalg.norm(x[ii]-x[jj],axis=1))
    v=scores(z);base=v>=np.quantile(v,.95)
    payload=json.loads((ROOT/'data/country_network_2020.json').read_text())
    assert np.allclose(v,[e['similarity'] for e in payload['all_edges']],rtol=0,atol=1e-12)
    def graph(mask):
        g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(zip(ii[mask],jj[mask]));return g
    sweep=[]
    for q in np.linspace(.80,.99,77):
        t=np.quantile(v,q);g=graph(v>=t)
        sweep.append(dict(quantile=float(q),threshold=float(t),edges=g.number_of_edges(),isolates=len(list(nx.isolates(g))),largest_component=max(map(len,nx.connected_components(g)))))
    pd.DataFrame(sweep).to_csv(OUT/'threshold_topology.csv',index=False)
    variants={'Z-score (baseline)':z,
              'Median / IQR':(raw-np.median(raw,axis=0))/(np.quantile(raw,.75,axis=0)-np.quantile(raw,.25,axis=0)),
              'Rank percentiles':pd.DataFrame(raw).rank(pct=True).to_numpy()}
    for k,name in enumerate(['internet use','landlines','broadband','mobile']):variants['Omit '+name]=np.delete(z,k,axis=1)
    rows=[];masks=[]
    for name,x in variants.items():
        s=scores(x);mask=s>=np.quantile(s,.95);g=graph(mask)
        neighbors={codes[j] for j in g.neighbors(codes.index('IND'))}
        rows.append(dict(method=name,edges=int(mask.sum()),jaccard=float((base&mask).sum()/(base|mask).sum()),isolates=len(list(nx.isolates(g))),india_neighbors=','.join(sorted(neighbors))))
        masks.append(mask)
    pd.DataFrame(rows).to_csv(OUT/'metric_sensitivity.csv',index=False)
    # A full-connectivity cutoff is the minimum weight in a maximum spanning tree.
    full=nx.Graph();full.add_nodes_from(range(n));full.add_weighted_edges_from(zip(ii,jj,v))
    tree=nx.maximum_spanning_tree(full);ct=min(a['weight'] for _,_,a in tree.edges(data=True))
    connected=graph(v>=ct);assert nx.is_connected(connected)
    assert not nx.is_connected(graph(v>ct))
    facts=dict(countries=n,all_pairs=len(v),baseline_edges=int(base.sum()),connected_cutoff=float(ct),connected_edges=connected.number_of_edges(),mst_edges=tree.number_of_edges(),metric_sensitivity=rows)
    (OUT/'method_research.json').write_text(json.dumps(facts,indent=2))
    fig,(ax,bx)=plt.subplots(1,2,figsize=(14,6),layout='constrained',gridspec_kw={'width_ratios':[1,1.5]})
    vals=[r['jaccard'] for r in rows[1:]];labels=[r['method'] for r in rows[1:]]
    ax.barh(labels,vals,color='#168a8a');ax.invert_yaxis();ax.set(xlim=(0,1),xlabel='Shared edges / union with baseline',title='A  Same top-5% rule, different profiles')
    for i,value in enumerate(vals):ax.text(value+.015,i,f'{value:.3f}',va='center')
    india=codes.index('IND');union=sorted(set().union(*[{j for j in graph(m).neighbors(india)} for m in masks]))
    grid=np.array([[int(m[(ii==min(india,j))&(jj==max(india,j))][0]) for j in union] for m in masks])
    bx.imshow(grid,cmap=matplotlib.colors.ListedColormap(['#f2f4f5','#168a8a']),vmin=0,vmax=1,aspect='auto')
    bx.set_xticks(range(len(union)),[codes[j] for j in union],rotation=90,fontsize=8)
    bx.set_yticks(range(len(rows)),[r['method'] for r in rows],fontsize=9)
    bx.set(title='B  India links depend on the chosen definition',xlabel='Union of India neighbors across tested methods')
    fig.suptitle('Small-noise robustness does not establish robustness to modeling choices',fontsize=17,weight='bold')
    fig.supxlabel('All methods use the same 179 countries. Each recalculates its own P95 cutoff; teal = retained pair.\nRanks compare relative positions; omitting an indicator changes the question. No alternative is a ground-truth network.',fontsize=10)
    for ext in ['png','svg']:fig.savefig(OUT/f'metric_sensitivity.{ext}',dpi=200,bbox_inches='tight')
    plt.close(fig)
    # Preserve continuous pair values that binary NodeTrix intentionally hides.
    from scipy.cluster.hierarchy import linkage,leaves_list
    order=leaves_list(linkage(np.linalg.norm(z[ii]-z[jj],axis=1),method='average',optimal_ordering=True))
    matrix=np.zeros((n,n));matrix[ii,jj]=v;matrix+=matrix.T;np.fill_diagonal(matrix,np.nan)
    fig,ax=plt.subplots(figsize=(10,9),layout='constrained')
    im=ax.imshow(matrix[np.ix_(order,order)],vmin=0,vmax=1,cmap='viridis',interpolation='nearest')
    ax.set(title='All pair scores: no cutoff hides the weaker similarities',xlabel='Countries in average-linkage distance order',ylabel='Same country order')
    fig.colorbar(im,ax=ax,label='Similarity 1 / (1 + standardized distance)')
    fig.supxlabel('179 countries; 15,931 unique pairs, mirrored. White diagonal excludes self-pairs.\nOrdering is a reading aid, not evidence of natural clusters. Exact country order is supplied as CSV.',fontsize=10)
    for ext in ['png','svg']:fig.savefig(OUT/f'weighted_similarity_matrix.{ext}',dpi=200,bbox_inches='tight')
    pd.DataFrame({'position':np.arange(n),'code':[codes[k] for k in order]}).to_csv(OUT/'weighted_matrix_order.csv',index=False)
    plt.close(fig)
    print(json.dumps(facts,indent=2))

def write_gallery():
    """Human-readable research decisions with primary sources and exact evidence."""
    facts=json.loads((OUT/'method_research.json').read_text())
    table=''.join(f'<tr><td>{r["method"]}</td><td>{r["edges"]}</td><td>{r["jaccard"]:.3f}</td><td>{r["isolates"]}</td></tr>' for r in facts['metric_sensitivity'])
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Network method review and evidence</title><style>body{font:18px/1.6 system-ui;max-width:1150px;margin:40px auto;padding:0 24px;color:#173044}img{width:100%;height:auto}h1,h2{line-height:1.2}table{border-collapse:collapse;width:100%}td,th{padding:8px;text-align:left;border-bottom:1px solid #ccd5dc}a{color:#007879}section{margin:50px 0}.note{background:#edf5f5;padding:20px}</style>
<h1>Does the similarity network answer the intended question?</h1><p>Review dated 30 October 2026. <a href="../../web/network.html">Interactive network</a> | <a href="../../output/pdf/DAS732_A2_Report_IEEE.pdf">Current report</a></p>
<p class="note"><strong>Professor's advice and our implementation.</strong> Following the professor's advice, we use derived similarities and inspect their distribution before filtering highly similar pairs. Our team chose P95 as an exploratory display setting; the professor did not prescribe that percentile. She mentioned perturbation as one possible approach. Our small-noise check tests a chosen threshold and does not implement a specified published selector.</p>
<section><h2>1. What is correct, and what the result means</h2><p>The same 179 complete 2020 profiles define every pair. Four indicators are standardized using population standard deviations. Euclidean distances become similarities through 1/(1+d). This monotone transform does not change pair rankings: a percentile cutoff selects the same pairs as a corresponding distance cutoff. The complete undirected graph has 15,931 pairs; filtering at 0.569763 retains 797. All nodes, including 12 isolates, remain.</p><p>These are similarities in measured profiles, not physical internet cables, traffic, causal relationships, p-values or probabilities. Complete-case selection also limits coverage. Equal standardized feature weights do not remove feature correlation or guarantee equal conceptual importance. The network addresses the four-indicator snapshot question; paths, change PCPs and distributions answer the temporal questions.</p>
<img src="network_threshold_layouts.png" alt="Pair similarity histogram, threshold connectivity curves and three graph layouts">
<p><strong>Replacement:</strong> Figure 1's old edge-retention curve largely repeated information already in the histogram. The new connectivity panel shows the consequence of filtering: how many countries remain in the largest component and how many become isolated. It uses 77 cutoffs from P80 to P99. Spring, Spectral and Circular still share exactly the same default edge list. The two former layouts arrange the connected core and separately pack isolates; distances in the drawing are not measured similarities.</p>
<p><a href="threshold_topology.csv">77-cutoff table</a> | <a href="threshold_sensitivity.csv">Four reference cutoffs</a> | <a href="../../data/network_all_pair_similarities.csv">Every pair score</a></p></section>
<section><h2>2. Noise stability and modeling stability are different</h2><p>The existing 30 seeded trials add Gaussian noise of standard deviation 0.02 to standardized coordinates and hold the original numerical threshold fixed. Their mean edge Jaccard is 0.922 (range 0.905-0.941). This is an illustrative sensitivity experiment: noise is not calibrated to measurement error. It neither selects P95 nor implements an identified published perturbation selector.</p>
<img src="metric_sensitivity.png" alt="Edge overlap under alternative feature definitions and India neighbor inclusion matrix">
<p>Here every alternative recalculates its own P95, retaining 797 pairs, so density does not explain differences in overlap. Median/IQR scaling reduces sensitivity to extreme marginal values; ranks compare relative positions instead of standardized magnitudes. Leave-one-indicator-out checks deliberately change the profile definition. These are sensitivity scenarios, not seven equally valid estimates of one known network. No labels or observed connections establish a winning metric.</p><table><tr><th>Method</th><th>Edges</th><th>Edge Jaccard</th><th>Isolates</th></tr>TABLE</table>
<p><strong>Interpretation:</strong> a stable drawing or small-noise test cannot establish natural country groups. Keep the baseline for its clear four-indicator definition, and qualify all neighbor/community claims by that definition. India has 12 neighbors at the baseline, 10 under IQR scaling and 17 under ranks.</p><p><a href="metric_sensitivity.csv">Exact metric comparisons and India neighbors</a> | <a href="input_perturbations.csv">Noise trials</a> | <a href="method_research.json">Computed research facts</a></p></section>
<section><h2>3. Which alternative plots add information?</h2><img src="nodetrix_threshold_detail.png" alt="NodeTrix communities, named isolates and a labeled group detail">
<p>Retain NodeTrix for checking exact retained links inside locally dense groups. The update draws and labels all 12 isolates and calls the six groups modularity communities, avoiding confusion with connected components. Six communities are subdivisions of one 167-country component, not six disconnected networks. White cells mean below cutoff; all distinct pairs were measured. The original NodeTrix work supports the hybrid matrix/node-link representation, but this static report does not claim its interactive matrix-editing features.</p>
<img src="weighted_similarity_matrix.png" alt="Continuous all-country similarity matrix in hierarchical order">
<p><strong>New supporting view:</strong> this continuous matrix preserves weak scores hidden by binary filtering. Average-linkage ordering uses the original standardized Euclidean distances and is only a reading aid. Diagonal self-pairs are masked; each off-diagonal pair appears twice. It complements the labeled NodeTrix detail, but replacing that detail with 179 tiny labels would make exact pairs harder to read in print.</p><p><a href="weighted_matrix_order.csv">Country order</a> | <a href="nodetrix_detail_matrix.csv">NodeTrix detail values</a></p></section>
<section><h2>4. Alternatives considered and why they do not replace the default</h2>
<table><tr><th>Alternative</th><th>Useful for</th><th>Decision for this report</th></tr>
<tr><td>Connectivity / percolation threshold</td><td>Studying when a network fragments</td><td>The highest cutoff keeping all countries connected is 0.239306 and retains 11,526 pairs (72.35%). Useful diagnostic, too dense for the intended high-similarity display. Brain-network research is motivation, not proof that its optimality transfers to these country profiles.</td></tr>
<tr><td>Maximum spanning tree</td><td>A connected 178-edge backbone</td><td>Forces connectivity and deletes cycles and many high-similarity pairs. A different question, so not a substitute for NodeTrix communities.</td></tr>
<tr><td>k-nearest neighbors</td><td>Local neighborhoods with a chosen neighbor count</td><td>Can retain weak matches for unusual profiles and gives no common similarity cutoff. Less direct than the instructor's distribution/filter recommendation.</td></tr>
<tr><td>Rank or robust scaling</td><td>Checking outlier and scale effects</td><td>Computed and displayed as sensitivity checks. A replacement would change what similarity means without an external validation target.</td></tr>
<tr><td>Cosine / country-profile correlation</td><td>Comparing direction or profile shape</td><td>May treat different absolute adoption levels as similar; four heterogeneous indicators are not repeated observations for inference. Not adopted.</td></tr>
<tr><td>Permutation significance / automated knee</td><td>Selection given a justified null or meaningful bend</td><td>No validated null, calibrated error model or target labels here. Shuffling each feature independently destroys real feature dependence. Do not label the strongest 5% statistically significant or invent a unique optimum.</td></tr>
<tr><td>Chord diagram / more force layouts</td><td>Presenting aggregate relationships</td><td>Add little to the required three-layout comparison and labeled matrix; dense ribbons impede exact-pair reading. No replacement.</td></tr></table></section>
<section><h2>5. Research sources and reproducibility</h2><ul>
<li><a href="https://www.dgp.toronto.edu/~mjmcguff/research/nodetrix/nodetrix.pdf">Henry, Fekete and McGuffin (2007), NodeTrix</a>: primary source for the hybrid matrix/node-link representation.</li>
<li><a href="https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00441/full">Bordier, Nicolini and Bifone (2017)</a>: percolation and threshold effects evaluated for brain networks, motivating the connectivity sweep, not a country-network optimality guarantee.</li>
<li><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10517318/">Theis et al. (2023), Threshold Selection for Brain Connectomes</a>: compares threshold-selection methods under domain-specific evaluation. Its perturbation experiments are not claimed as our selector.</li>
<li><a href="https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html">StandardScaler documentation</a> and <a href="https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html">RobustScaler documentation</a>: marginal scaling, outlier sensitivity, median/IQR alternative. Our implementation uses NumPy directly.</li>
<li><a href="https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.tree.mst.maximum_spanning_tree.html">NetworkX maximum spanning tree</a>: implementation used to obtain the bottleneck connectivity cutoff.</li></ul>
<p>From the ass2 directory run <code>python scripts/network_threshold_revision.py</code>, then <code>python scripts/build_a1_style_report.py</code>, <code>python scripts/sync_report_delivery.py</code> and <code>python scripts/verify_story_report.py</code>. The first command calls <code>research_network_methods.py</code>; it uses the supplied processed country table and independently checks the stored all-pair scores. Weather plots and the 30-figure allocation are preserved.</p></section></html>'''.replace('TABLE',table)
    (OUT/'index.html').write_text(page,encoding='utf-8')

if __name__=='__main__':build();write_gallery()
