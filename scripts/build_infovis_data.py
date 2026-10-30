"""Build A2 country similarity graph, browser inputs, and layout figures.

Run from ass2: python scripts/build_infovis_data.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_dataset_countries_only.csv"
REGIONS = ROOT / "data/processed/region_lookup.csv"
DATA = ROOT / "data"
IMAGES = ROOT / "images"
PROFILE = ["internet_users_share_pct", "telephone_lines_per100", "broadband_subs_per100", "mobile_subs_per100"]
PALETTE = {
    "Africa": "#bd4c43", "Asia": "#6b54a3", "Europe": "#3476b6",
    "North America": "#d29328", "Oceania": "#36a0a8", "South America": "#399269",
    "Unclassified": "#68717a",
}


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    data = pd.read_csv(SOURCE)
    lookup = pd.read_csv(REGIONS).set_index("code").region.to_dict()
    snapshot = data.loc[data.year.eq(2020)].dropna(subset=["code"] + PROFILE).copy()
    assert not snapshot.code.duplicated().any()
    snapshot = snapshot.sort_values("code").reset_index(drop=True)
    snapshot["region"] = snapshot.code.map(lookup).fillna("Unclassified")

    raw = snapshot[PROFILE].to_numpy(float)
    means, stds = raw.mean(axis=0), raw.std(axis=0, ddof=0)
    scaled = (raw - means) / stds
    distance = np.linalg.norm(scaled[:, None, :] - scaled[None, :, :], axis=2)
    ii,jj=np.triu_indices(len(snapshot),1)
    values=1/(1+distance[ii,jj])
    threshold=float(np.quantile(values,.95))
    all_edges=[dict(source=str(snapshot.loc[i,'code']),target=str(snapshot.loc[j,'code']),distance=float(distance[i,j]),similarity=float(s)) for i,j,s in zip(ii,jj,values)]
    graph = nx.Graph()
    for row in snapshot.itertuples():
        graph.add_node(row.code, country=row.entity, region=row.region)
    for e in all_edges:
        if e['similarity']>=threshold: graph.add_edge(e['source'],e['target'],distance=e['distance'],similarity=e['similarity'])
    pd.DataFrame(all_edges).to_csv(DATA/'network_all_pair_similarities.csv',index=False)
    sweep=[]
    for q in [.90,.925,.95,.975]:
        t=float(np.quantile(values,q));h=nx.Graph();h.add_nodes_from(graph)
        h.add_edges_from((e['source'],e['target']) for e in all_edges if e['similarity']>=t)
        sweep.append(dict(quantile=q,threshold=t,edges=h.number_of_edges(),isolates=len(list(nx.isolates(h))),components=nx.number_connected_components(h),largest_component=max(map(len,nx.connected_components(h)))))
    # Deliberately small perturbations of standardized coordinates, not an
    # implementation of a named threshold-selection algorithm.
    rng=np.random.default_rng(732);base=values>=threshold;perturb=[]
    for run in range(30):
        noisy=scaled+rng.normal(0,.02,scaled.shape)
        trial=1/(1+np.linalg.norm(noisy[ii]-noisy[jj],axis=1))>=threshold
        perturb.append(dict(run=run,edges=int(trial.sum()),jaccard=float((base&trial).sum()/(base|trial).sum())))
    evidence=dict(countries=len(snapshot),all_pairs=len(all_edges),default_quantile=.95,threshold=threshold,retained_edges=graph.number_of_edges(),isolates=len(list(nx.isolates(graph))),components=nx.number_connected_components(graph),threshold_sweep=sweep,perturbations=perturb,perturbation_sigma_z_units=.02,perturbation_seed=732,threshold_rationale='Retain the strongest 5% of all pair similarities as an explicitly chosen sparse starting view; compare nearby quantiles and small input perturbations. No claim of a unique optimal threshold or a named perturbation threshold method.')
    write_json(DATA/'network_threshold_audit.json',evidence)

    # Isolates otherwise dominate spring extent and the zero-eigenvalue space
    # collapses a disconnected spectral graph. Lay out the connected core,
    # normalize it, and retain isolates on an explicitly separated bottom row.
    core=graph.subgraph(max(nx.connected_components(graph),key=len))
    isolated=sorted(nx.isolates(graph))
    assert len(core)+len(isolated)==len(graph)
    def packed(pos):
        a=np.array(list(pos.values()));lo,hi=a.min(0),a.max(0)
        result={n:(np.asarray(p)-lo)/np.maximum(hi-lo,1e-12) for n,p in pos.items()}
        result.update({n:np.array([i/max(len(isolated)-1,1),-.18]) for i,n in enumerate(isolated)})
        return result
    positions = {
        "Spring": packed(nx.spring_layout(core, weight="similarity", seed=732, iterations=150)),
        "Spectral": packed(nx.spectral_layout(core, weight="similarity")),
        "Circular": nx.circular_layout(graph),
    }
    normalized = {}
    for name, pos in positions.items():
        coords = np.array([pos[code] for code in snapshot.code])
        lo, hi = coords.min(axis=0), coords.max(axis=0)
        coords = (coords - lo) / np.maximum(hi - lo, 1e-12)
        normalized[name] = {code: [float(x), float(y)] for code, (x, y) in zip(snapshot.code, coords)}

    nodes = []
    for row in snapshot.itertuples():
        nodes.append({
            "id": row.code, "country": row.entity, "region": row.region,
            "degree": graph.degree(row.code),
            "internet_pct": row.internet_users_share_pct,
            "landlines_per100": row.telephone_lines_per100,
            "broadband_per100": row.broadband_subs_per100,
            "mobile_per100": row.mobile_subs_per100,
        })
    edges = [
        {"source": u, "target": v, "distance": attrs["distance"], "similarity": attrs["similarity"]}
        for u, v, attrs in graph.edges(data=True)
    ]
    write_json(DATA / "country_network_2020.json", {
        "year": 2020, "default_threshold":threshold,"default_quantile":.95,
        "construction": "Complete all-pair similarity universe; default display retains similarities at or above the 95th percentile. s=1/(1+Euclidean distance on four z-scored indicators).",
        "fields": PROFILE, "means": dict(zip(PROFILE, means.tolist())),
        "standard_deviations": dict(zip(PROFILE, stds.tolist())),
        "nodes": nodes, "edges": edges, "all_edges":all_edges,"layouts": normalized,
        "layout_scope":"Layouts computed once at default threshold. Spring/Spectral lay out the 167-node connected core and pack 12 isolates on a separate bottom row. Circular includes all 179 nodes. Slider changes visible edges, not positions.",
    })

    IMAGES.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(18, 7), dpi=180)
    top_labels = sorted(graph, key=lambda n: graph.degree(n), reverse=True)[:12]
    for ax, (name, pos) in zip(axes, positions.items()):
        nx.draw_networkx_edges(graph, pos, ax=ax, alpha=.13, width=.55, edge_color="#52657a")
        for region, color in PALETTE.items():
            members = [n for n in graph if graph.nodes[n]["region"] == region]
            nx.draw_networkx_nodes(graph, pos, nodelist=members, ax=ax, node_size=14,
                                   node_color=color, linewidths=0)
        nx.draw_networkx_labels(graph, pos, labels={n: n for n in top_labels}, ax=ax, font_size=6)
        ax.set_title(f"{name}\n{graph.number_of_nodes()} countries · {graph.number_of_edges()} derived links", fontsize=11)
        ax.axis("off")
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=c, markeredgewidth=0,
                      markersize=7, label=r) for r, c in PALETTE.items()]
    fig.legend(handles=handles, loc="lower center", ncol=7, frameon=False, fontsize=8)
    fig.suptitle("Country connectivity similarity, 2020 · same nodes and edges in three layouts", fontsize=14)
    fig.text(.5, .03, "Edges are derived from standardized telecom profiles; they do not represent physical connections.",
             ha="center", fontsize=9, color="#52657a")
    fig.tight_layout(rect=[0, .07, 1, .94])
    fig.savefig(IMAGES / "network_layouts.png", bbox_inches="tight")
    plt.close(fig)

    tree = data.loc[data.year.eq(2020)].dropna(
        subset=["code", "internet_users_count", "internet_users_share_pct"]
    ).copy()
    tree = tree.loc[tree.internet_users_count.ge(0)]
    tree["region"] = tree.code.map(lookup).fillna("Unclassified")
    tree_rows = [{
        "code": row.code, "country": row.entity, "region": row.region,
        "internet_users": int(round(row.internet_users_count)),
        "internet_pct": float(row.internet_users_share_pct),
    } for row in tree.itertuples()]
    write_json(DATA / "treemap_countries_2020.json", {
        "year": 2020, "countries": tree_rows,
        "included_total": sum(r["internet_users"] for r in tree_rows),
        "coverage": "countries with nonmissing internet user count and share; aggregate rows excluded",
    })
    print(f"Network: {len(nodes)} nodes, {len(edges)} links. Treemap: {len(tree_rows)} countries.")


if __name__ == "__main__":
    main()
