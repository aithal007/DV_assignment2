"""Keep recording scenes synchronized with the October 24 internet revision."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

ROOT=Path(__file__).resolve().parents[1]
def revise(slides, assets):
    d=pd.read_csv(ROOT/'data/processed/master_dataset_countries_only.csv')
    matrix=pd.read_csv(ROOT/'output/simple_revision/nodetrix_group7_matrix.csv',index_col=0)
    lookup=pd.read_csv(ROOT/'output/lecture_previews/community_country_order.csv').set_index('id').country
    shown=matrix.to_numpy(dtype=float);np.fill_diagonal(shown,.45)
    fig,ax=plt.subplots(figsize=(9.4,6.3))
    ax.imshow(shown,cmap=ListedColormap(['white','#dce2e6','#168a8a']),vmin=0,vmax=1,interpolation='nearest')
    ax.set_xticks(range(8),matrix.columns,rotation=45,ha='right',fontsize=12)
    ax.set_yticks(range(8),[f'{lookup[c]} ({int(matrix.loc[c].sum())})' for c in matrix.index],fontsize=12)
    ax.set_xticks(np.arange(-.5,8,1),minor=True);ax.set_yticks(np.arange(-.5,8,1),minor=True)
    ax.grid(which='minor',color='#bccbd3',lw=.6);ax.tick_params(which='both',length=0)
    ax.set_title('Group 7: eight countries and 18 links',loc='left',fontsize=16,weight='bold',pad=12)
    fig.text(.5,.015,'Teal: linked | White: no link | Gray: same country\nRow labels give the number of links inside this group.',ha='center',fontsize=11)
    fig.subplots_adjust(left=.28,right=.98,top=.90,bottom=.16)
    for ext in ['png','svg']:fig.savefig(assets/f'nodetrix_zoom.{ext}',dpi=180,bbox_inches='tight')
    plt.close(fig)
    from build_temporal_figures import horizon
    fig,ax=plt.subplots(figsize=(7.7,5.2))
    series=[]
    for code in ['SGP','CHN','TZA']:
        g=d[d.code.eq(code)&d.year.between(2000,2020)].sort_values('year')
        assert len(g)==21
        series.append((g.entity.iloc[0],g.internet_users_share_pct.to_numpy()))
    horizon(ax,series,'Country trajectories around 50% adoption')
    ax.set_xlabel('Year',fontsize=12)
    for label in ax.texts:label.set_fontsize(11)
    fig.subplots_adjust(left=.16,right=.98,top=.86,bottom=.25)
    fig.text(.5,.015,'Red: below 50%, not decline. Right: 2020 value | first attainment.',ha='center',fontsize=9)
    for ext in ['png','svg']:fig.savefig(assets/f'horizon.{ext}',dpi=180,bbox_inches='tight')
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12.8,4.4),sharex=True,sharey=True,layout='constrained')
    for ax,code in zip(axes,['ZAF','CHN']):
        g=d[d.code.eq(code)&d.year.between(2010,2020)].sort_values('year')
        x=g.broadband_subs_per100;y=g.internet_users_share_pct
        ax.plot(x,y,'o-',color='#087E8B',lw=3,ms=5)
        ax.scatter(x.iloc[0],y.iloc[0],s=100,facecolors='white',edgecolors='#087E8B',lw=2,zorder=4)
        ax.scatter(x.iloc[-1],y.iloc[-1],s=100,color='#142D43',zorder=4)
        for idx,label in [(0,'2010'),(-1,'2020')]:ax.annotate(label,(x.iloc[idx],y.iloc[idx]),xytext=(9,9 if idx==-1 else -18),textcoords='offset points',fontsize=15)
        ax.set(xlim=(-2,45),ylim=(0,100),xticks=[0,10,20,30,40],yticks=[0,25,50,75,100],xlabel='Fixed broadband subscriptions / 100')
        ax.set_title(g.entity.iloc[0],loc='left',weight='bold',fontsize=20)
        ax.grid(alpha=.15)
    axes[0].set_ylabel('People using the internet (%)')
    for ext in ['png','svg']:fig.savefig(assets/f'country_paths.{ext}',dpi=180,bbox_inches='tight')
    plt.close(fig)
    s=slides[1]
    s.update(images=['network.png'],source='Report Fig. 1. Identical 179-country, 590-edge graph; India and its six stored neighbors highlighted in all three layouts.',
      say='We start with a country similarity network. The three layouts contain exactly the same countries and edges. India has the same six highlighted neighbors in every drawing, although their positions change. A snapshot of a layout can therefore mislead us about relationships. These links represent similar measured profiles, not physical internet connections.',
      screen='Three layouts with the same highlighted India neighborhood. Keep the neighbor list visible. The overview is context, not evidence of physical connections.',
      actions='Point to India and the orange edges across all three panels. Emphasize that only drawing positions change.')
    s=slides[2]
    s.update(title='Snapshots hide different infrastructure paths',layout='paths',images=['country_paths.png'],
      headline='South Africa and China, 2010–2020',
      takeaway='Adoption gains can accompany very different fixed-broadband changes.',
      source='Report Fig. 2, two illustrative cases from six. Original A1 OWID/ITU extracts; annual observations, identical scales.',
      say='Country paths reveal what a snapshot misses. South Africa gains about 48 adoption percentage points with less than one extra fixed broadband subscription per hundred people. China gains about 36 points while broadband rises by roughly 25 subscriptions per hundred. Both improve, through different measured paths. These illustrative cases do not establish causes. Did broader progress also narrow inequality?',
      screen='Two enlarged country trajectories, South Africa and China. Open markers are 2010; dark markers are 2020. All annual observations and common axes remain visible.',
      actions='Follow South Africa upward, then China upward and right. Say percentage points for adoption, subscriptions per hundred for broadband. Do not claim mobile caused the difference.')
    s=slides[6]
    s.update(headline='An explicit joint brush reveals six exceptions',
      say='A dense overview can hide exceptions. Our JavaScript view bundles country paths, then selects adoption of at least 70 percent with fixed broadband at most five subscriptions per hundred. Six countries match, including South Africa. Their names appear below the chart. Clearing the selection restores all 175 countries; reordering changes which measurements are adjacent.',
      screen='Record the running browser. Show the overview, click the high-adoption/low-broadband focus button, pause on six named countries, clear, then reorder an axis.',
      actions='Open web/index.html?year=2020&bundle=0&matched=1&fixed=1. Move bundle to 50, click Inspect high adoption / low broadband, hold on 6 of 175 and the names, Clear brushes, then click an axis title. Keep the browser wide enough to show all axes.')
    slides[5].update(source='Report Fig. 13 excerpt: Singapore, China, Tanzania; Fig. 15: all 159 countries. Companion variations: Figs. 14 and 16.',
      screen='Three enlarged horizon rows and the whole-panel ridgeline. Both keep their legends and units; the full report retains all required variants.')
    s=slides[7]
    s.update(say='Both treemap roots contain the same 184 countries and total users. Changing from regions to adoption bands reveals a different concentration. Area represents user counts; country colours show adoption. Zoom into a group to inspect its countries, keeping its smaller subtotal explicit.',
      actions='At the root of web/treemap.html show the included total; change hierarchy to adoption bands and show the unchanged total. Click the 75–100% group, pause on its breadcrumb and subtotal, then Back. Do not compare a zoomed tile with a root tile as the same denominator.',
      screen='Record the actual browser changing the hierarchy at the root, then drilling down. Group headers are neutral; nested country tiles are colored by adoption.')
    slides[15]['source']='Synthesis of report Figs. 1–3, 10–12, 18, 23, 26, 29–30 and the matched-change comparison.'
    slides[1].update(say='These three layouts contain the same countries and links. Follow the colored lines from India: the same six countries stay connected to it. A layout can stretch a line, so linked countries may look farther apart. Here, a neighbor means a country joined by a line. Distance on the page is not a data value.',
      actions='Follow one line color across all three panels. Explain that its length changes while its two endpoint countries stay the same.')
    slides[2].update(title='Look inside a country group',layout='matrix',images=['nodetrix_zoom.png'],
      headline='One colored cell shows one country-to-country link',
      takeaway='Rows reveal links that are difficult to trace in the network.',
      source='Report Fig. 3, enlarged group 7 matrix. Eight countries; 18 of 28 possible links. The complete NodeTrix view remains in the report.',
      say='NodeTrix helps us look inside a group. Each row and column is a country. A colored cell means the two countries are linked; a white cell means they are not. Cuba and Palestine each link to six of the seven other countries in this group. Their filled rows make that visible. We next ask what a regional average hides.',
      screen='Large group 7 matrix with country row labels, country-code columns and counts of internal links.',
      actions='Read the Cuba row across, pointing out colored and white cells. The gray diagonal compares a country with itself and does not count as a link.')
    slides[3].update(title='A regional average hides country differences',layout='spread',images=['within_regions.png'],
      headline='Each dot is a country. The tick marks the regional average.',
      takeaway='About 47% of the measured country spread lies within regions.',
      source='Report Fig. 11. 158 countries with region labels, 2020. The bar splits variance, a measure of spread, using equal country weights.',
      say='A regional average cannot describe every country inside it. These dots show the range of internet use within each region. Countries in the same region can have very different rates. About 47 percent of the measured country spread lies within regions, while 53 percent lies between regional averages. A region label therefore gives only part of the picture. We also need to look at individual country changes.',
      screen='Country dots by region with the 47/53 percent spread bar. Keep the dot meaning and average marker visible.',
      actions='Point across one regional row, then to the within-region bar. The percentages describe variation between national rates, not percentages of people.')
    slides[14].update(title='Separate conditions and their shared occurrence',layout='overlap',images=['intersections.png'],
      headline='The same scale compares each condition with all three together',
      takeaway='Only 2.57% of weighted grid-cell days meet all three conditions.',
      say='Dry conditions are common, but hot, dry and windy conditions occur together in only 2.57 percent of weighted grid-cell days. We cannot read that overlap from any one condition’s frequency. The first three bars overlap, so we must not add them.',
      source='Report Fig. 29. Individual condition frequencies and their shared occurrence. Same 92-day, 13,416-cell weighted study area.',
      screen='Four simple bars: hot, dry, windy, and all three together. Shared units and exact percentages are visible.',
      actions='Point to Dry and then All three together. Explain that a grid cell must meet all three definitions on the same day.')

