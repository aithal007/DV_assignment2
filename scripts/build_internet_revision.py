"""Focused analytical figures and report overrides for the October 24 revision."""
from pathlib import Path
import json, subprocess, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/internet_revision'
OUT.mkdir(parents=True,exist_ok=True)

def entry(title,path,question,encoding,why,findings,limits,takeaway):
    return dict(title=title,path=path,wide=True,caption=findings,
        explanation=[question,encoding,why,limits,takeaway],detailed_interpretation=findings)

def build():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    graph=json.loads((ROOT/'data/country_network_2020.json').read_text())
    nodes={n['id']:n for n in graph['nodes']}; focus='IND'
    near={e['target'] if e['source']==focus else e['source'] for e in graph['edges'] if focus in [e['source'],e['target']]}
    fig,axes=plt.subplots(1,3,figsize=(15,6))
    for ax,(name,pos) in zip(axes,graph['layouts'].items()):
        for e in graph['edges']:
            active=focus in [e['source'],e['target']]
            a,b=pos[e['source']],pos[e['target']]
            ax.plot([a[0],b[0]],[a[1],b[1]],color='#d66a2c' if active else '#ced6da',alpha=1 if active else .3,lw=2 if active else .5,zorder=2 if active else 0)
        for code,p in pos.items():
            active=code in near or code==focus
            ax.scatter(*p,s=75 if code==focus else 35 if active else 12,color='#183c57' if code==focus else '#d66a2c' if active else '#d2dce1',zorder=4 if active else 1)
        ax.set_title(name,fontsize=15,weight='bold');ax.set(xlim=(-.06,1.06),ylim=(-.06,1.06));ax.set_aspect('equal');ax.axis('off')
        # A single focus label avoids colliding neighboring-country labels.
        ax.annotate('India',pos[focus],xytext=(18,20),textcoords='offset points',weight='bold',arrowprops=dict(arrowstyle='-',color='#183c57'),bbox=dict(fc='white',ec='none',alpha=.9))
    names=', '.join(nodes[n]['country'] for n in sorted(near))
    fig.suptitle('A different drawing preserves the thresholded neighbors',fontsize=19,weight='bold')
    fig.text(.06,.10,'Highlighted links: '+names,fontsize=11)
    fig.text(.06,.04,'179 countries · 797 unchanged edges · orange: India’s stored links; gray: context\nAll pair similarities; global P95 threshold. Similar profiles, not physical internet connections.',fontsize=10)
    fig.subplots_adjust(top=.83,bottom=.2,wspace=.16)
    for ext in ['png','svg']:fig.savefig(OUT/f'network_focus.{ext}',dpi=210,bbox_inches='tight')
    plt.close(fig)
    x=pd.read_csv(ROOT/'data/internet_panel_2000_2020.csv')
    wide=x.pivot(index='code',columns='year',values='internet_users_share_pct').loc[:,2000:2020].dropna()
    meta=x.drop_duplicates('code').set_index('code');years=np.array(wide.columns)
    regions=['Africa','Asia','Europe','North America','South America','Oceania']
    fig,axes=plt.subplots(2,3,figsize=(14,8),sharex=True,sharey=True)
    records=[]
    for ax,r in zip(axes.flat,regions):
        v=wide.loc[meta.loc[wide.index,'region'].eq(r)]
        for t,c in [(50,'#168a8a'),(75,'#d66a2c')]:
            curve=np.maximum.accumulate(v.to_numpy()>=t,axis=1).mean(axis=0)*100
            ax.step(years,curve,where='post',color=c,lw=2.5,label=f'{t}% adoption')
            records.extend(dict(region=r,year=int(y),threshold=t,ever_pct=float(q),n=len(v)) for y,q in zip(years,curve))
        p50=records[-22]['ever_pct'];p75=records[-1]['ever_pct']
        ax.set_title(f'{r} · {len(v)} countries\n2020: {p50:.0f}% reached 50%; {p75:.0f}% reached 75%',loc='left',fontsize=11)
        ax.set(xlim=(1999.5,2020.5),ylim=(0,105),xticks=[2000,2010,2020],yticks=[0,25,50,75,100]);ax.grid(alpha=.16)
    axes[0,0].legend(frameon=False,fontsize=10,loc='upper left')
    fig.suptitle('Regional progress hides different arrival times',fontsize=20,weight='bold')
    fig.supylabel('Countries ever observed at the milestone (%)',fontsize=11)
    fig.supxlabel('Year',y=.085)
    fig.text(.055,.02,'Fixed panel of 158 classified countries; one unclassified country excluded. Annual observations, equal country weights.\nFirst attainment persists in this count even if adoption later falls. Already above in 2000 may have crossed earlier; others may cross after 2020.',fontsize=9)
    fig.subplots_adjust(left=.08,right=.98,top=.86,bottom=.17,hspace=.4,wspace=.15)
    for ext in ['png','svg']:fig.savefig(OUT/f'milestone_timing.{ext}',dpi=210,bbox_inches='tight')
    plt.close(fig)
    pd.DataFrame(records).to_csv(OUT/'milestone_evidence.csv',index=False)
    endpoint=pd.DataFrame(records).query('year==2020 and threshold==75').set_index('region').ever_pct
    evidence=f'By 2020, {endpoint["Europe"]:.1f}% of the fixed European panel had ever reached 75% adoption, compared with {endpoint["Africa"]:.1f}% of the African panel. The two thresholds distinguish majority access from high adoption, and the steps expose when countries first qualify. The same regional improvement therefore contains different waiting times. These percentages count countries, not people.'
    entries={
      'network_focus':entry('One threshold graph, three layouts.','output/internet_revision/network_focus.png','Does the apparent neighborhood depend on the drawing or on the stored links?',f'India is dark blue and its {len(near)} incident edges and neighbors are orange. Gray nodes and links retain the threshold graph. All panels use identical nodes and edges.','A fixed highlighted case makes the controlled layout comparison inspectable.',f'India has the same {len(near)} neighbors in all layouts: {names}. The 179-node graph retains 797 edges from all 15,931 pair similarities at the documented P95 threshold.','The edges describe similar standardized profiles, not internet cables or causation. Membership depends on features, scaling and threshold.','Inspect stored pair similarities rather than inferring relationships from drawing distance.'),
      'country_paths':entry('Country paths behind the adoption snapshot.','output/internet_review_20261024/adoption_broadband_paths.png','Can similar adoption improvements accompany different changes in fixed broadband?','Six small multiples plot annual fixed broadband subscriptions per 100 against internet adoption percent for 2010–2020. Open markers mark 2010, dark markers 2020, and small dots all intervening years. Every panel uses identical axes.','Named-country paths recover timing and joint movement that a one-year scatterplot or regional average cannot show.','India gains 35.9 adoption percentage points while fixed broadband rises by 0.8 subscriptions per 100; South Africa gains 48.1 points with a 0.7 rise. China gains 35.8 adoption points with a 24.6 rise in broadband. Brazil gains 40.7 points with a 10.1 rise. Germany starts at 82% adoption and rises 7.8 points. These are observed contrasting paths, not a universal sequence of development.','Six illustrative cases were chosen for contrasting paths, not as a representative sample. All 11 annual pairs exist for each country; no imputation. National aggregates do not identify causes, and low fixed broadband does not by itself prove mobile substitution. Subscription counts are not unique people.','Snapshots hide different paths: comparable adoption gains need not accompany comparable fixed-broadband expansion.'),
      'milestone_timing':entry('When countries first reach adoption milestones.','output/internet_revision/milestone_timing.png','Do regional summaries conceal early, late and not-yet-observed milestone attainment?','Each panel contains a fixed regional country cohort. Teal counts the share ever observed at or above 50% adoption; orange uses 75%. Steps rise at the first qualifying annual measurement and do not fall after subsequent reversals.','Shared-scale regional small multiples make milestone timing comparable without six overlapping regional lines. The two thresholds expose dependence on the definition of progress.',evidence,'158 classified complete-panel countries; one unclassified country excluded. These are descriptive cumulative attainment counts, not survival estimates. Countries above the threshold in 2000 may have crossed earlier. Nonattainment by 2020 does not mean never. Attainment is not sustained access.','A rising average conceals when countries reach useful adoption levels, and which remain below them within the observed interval.'),
    }
    (OUT/'entries.json').write_text(json.dumps(entries,indent=2,ensure_ascii=False),encoding='utf-8')
    (OUT/'network_neighbors.json').write_text(json.dumps({'focus':focus,'neighbors':sorted(near),'countries':names},indent=2))
    print('Built focused network, milestone panels and report entries')

def override_figure(key, f):
    entries=json.loads((OUT/'entries.json').read_text(encoding='utf-8'))
    if key==1: f.update(entries['network_focus'],chart_export=True)
    if key in [3,4]:
        focused=key==4
        f.update(entry('Bundled profiles with a named selection.' if focused else 'Straight parallel coordinates: the complete matched overview.',
          'output/internet_revision/pcp_focus.png' if focused else 'output/internet_revision/pcp_straight.png',
          'Which countries combine high adoption with little fixed broadband?' if focused else 'What profile variation is hidden by a single adoption average?',
          'Each line is one of 175 matched countries in 2020. Axes show adoption percent and landline, broadband and mobile subscriptions per 100. Regional colors and fixed 2015/2020 axis domains are shared across both figures. '+('Fifty-percent region bundling preserves exact axis intercepts. Brushes select adoption at least 70% and fixed broadband at most 5/100; selected paths are emphasized and countries named below.' if focused else 'Straight paths provide the unbundled overview before selection; the following figure applies a reproducible brush to the same cohort.'),
          'The overview-to-selection comparison connects the required JavaScript interaction to an interpretable infrastructure question.',
          'The joint brush selects six countries: Bhutan, Cuba, Kuwait, Kyrgyzstan, Libya and South Africa. Their 2020 adoption is at least 70% while fixed broadband is at most 5 subscriptions per 100. These exceptions show why a pooled adoption–broadband association cannot describe every national profile. '+('The focused rendering makes the individual axis intercepts traceable rather than relying on the shape of a dense bundle.' if focused else 'The straight overview retains all country paths; precise identification requires the focused view rather than reading overlapping lines.'),
          'The thresholds are exploratory analyst choices, not universal development classes. Bundling uses supplied regions and does not discover clusters. Curves between axes are drawing geometry. Different units make segment slopes unsuitable as growth rates. Low fixed broadband does not prove a causal mobile pathway.',
          'A dense overview hides exceptions; an explicit joint selection makes six contrasting country profiles checkable.'),chart_export=True)
    if key in [5,6]:
        mode='region' if key==5 else 'adoption'
        f.update(entry('Region-first treemap at the common root.' if key==5 else 'Adoption-band-first treemap at the common root.',
          f'output/internet_revision/treemap_root_{mode}.png',
          'How does the hierarchy change which concentration is visible?',
          'Both root views retain exactly 184 country leaves and 4,521,767,530 included internet users. Group headers are neutral and nested country rectangles use adoption color; area is user count. Labels give each visible group’s share of the common total. Region-first groups countries by region; adoption-first nests countries within region within adoption band. The adoption color legend applies to country tiles, including the nested leaf overview; it never encodes a group average.',
          'Comparing the same root total isolates hierarchy remodeling instead of confounding it with different zoom subsets.',
          'The region-first root reveals geographic concentration of included users, while the adoption-first root reveals concentration by national adoption band. Both regroup the identical country leaves and preserve the total exactly. A populous country can contribute many online users despite an incomplete adoption rate, so user-count concentration and access percentage answer different questions. The supplied browser supports click-to-zoom, hover details, breadcrumb and Back; the companion Asia drilldown demonstrates country-level details.',
          'This is the included-country total, not a claim of complete worldwide coverage. Area is a count, not adoption percentage or country count. Band boundaries are analyst-defined; neutral parent colors do not encode a group adoption average. Drilldowns have different denominators and must be labeled separately.',
          'A hierarchy changes which concentration becomes visible while the included people and country measurements stay fixed.'),chart_export=True)
    if key in [7,8]:
        f['explanation'][1]+=' Rows are ordered by first observed 50% attainment, then label; nonattainers appear last. Right labels give the 2020 value and first qualifying year; dots mark crossings after 2000. Red indicates a level below 50%, not decline.'
        f['explanation'][3]+=' A first crossing does not imply sustained attainment; a series already above 50% in 2000 may have crossed earlier.'
    if key in [9,10]:
        f['explanation'][1]+=' Baseline rug ticks show the observed country values; right labels print each median. Peak-normalized density height is not country count.'
        f['explanation'][3]+=' In small cohorts, including eight Oceania countries, smooth bumps are exploratory; use the raw ticks to assess support.'
    return f

if __name__=='__main__':build()
