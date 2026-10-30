"""Descriptive quantile changes on the identical complete annual country panel."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/lecture_previews'

def build():
    data=pd.read_csv(ROOT/'data/internet_panel_2000_2020.csv')
    panel=data.pivot(index='code',columns='year',values='internet_users_share_pct').loc[:,2000:2020].dropna()
    assert panel.shape==(159,21)
    p=np.arange(.1,1,.1)
    q0=np.quantile(panel[2000],p,method='linear')
    q1=np.quantile(panel[2020],p,method='linear')
    gain=np.quantile(panel[2020]-panel[2000],p,method='linear')
    table=pd.DataFrame(dict(percentile=p*100,adoption_2000=q0,adoption_2020=q1,distribution_shift=q1-q0,individual_gain_quantile=gain))
    table.to_csv(OUT/'adoption_quantile_change.csv',index=False)
    panel.assign(gain_pp=panel[2020]-panel[2000]).to_csv(OUT/'adoption_quantile_country_values.csv')
    spread0=float(q0[-1]-q0[0]);spread1=float(q1[-1]-q1[0])
    metrics=dict(countries=len(panel),p90_p10_2000=spread0,p90_p10_2020=spread1,median_shift=float(q1[4]-q0[4]),median_individual_gain=float(gain[4]))
    (OUT/'adoption_quantile_metrics.json').write_text(json.dumps(metrics,indent=2))
    plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    ax=axes[0]
    ax.plot(p*100,q0,'o-',color='#64748b',label='2000 adoption')
    ax.plot(p*100,q1,'o-',color='#007f86',label='2020 adoption')
    ax.set(title='A  Higher adoption; a wider absolute spread',xlabel='Country percentile',ylabel='Internet adoption (%)',ylim=(0,100))
    ax.legend(frameon=False,loc='upper left')
    ax=axes[1]
    ax.plot(p*100,q1-q0,'o-',color='#007f86',label='Difference of adoption quantiles')
    ax.plot(p*100,gain,'s--',color='#b45309',label='Quantiles of individual country gains')
    ax.set(title='B  Distribution shift versus paired gains',xlabel='Country percentile',ylabel='Change, 2000 to 2020 (percentage points)',ylim=(0,100))
    ax.legend(frameon=False,loc='upper left',fontsize=10)
    for ax in axes:
        ax.set_xticks([10,25,50,75,90]);ax.grid(axis='y',alpha=.2)
    fig.suptitle('Progress does not necessarily narrow the absolute adoption gap',fontsize=17,fontweight='bold')
    fig.savefig(OUT/'adoption_quantile_change.png',dpi=220)
    fig.savefig(OUT/'adoption_quantile_change.svg')
    plt.close(fig)
    findings=(f'On the same 159-country panel, the 90th-minus-10th percentile adoption gap widens from {spread0:.2f} to {spread1:.2f} percentage points. '
              f'The median of the adoption distribution rises by {metrics["median_shift"]:.2f} points, whereas the median individual country gain is {metrics["median_individual_gain"]:.2f} points.')
    entry=dict(title='Adoption quantiles and matched-country gains.',path='output/lecture_previews/adoption_quantile_change.png',wide=True,extension_key='adoption_quantile_change',caption=findings,
        explanation=[
          'Did broad internet-adoption progress also narrow the absolute gap between lower- and higher-adoption countries?',
          'Panel A compares adoption deciles in 2000 and 2020 on the fixed 159-country complete annual panel. Panel B contrasts differences of corresponding deciles (teal) with deciles of the 159 individual country gains (orange). Each country has equal weight. Values are empirical linear-interpolated quantiles; changes are percentage points.',
          'Inspired by quantile shift functions, this view measures changes throughout the distribution instead of hiding them inside four adoption bands. The paired-gain curve additionally distinguishes change in distributional positions from change experienced by individual countries.',
          'A country at the 10th percentile in 2000 need not occupy that percentile in 2020. Differences of quantiles are not quantiles of differences. No causal or inferential claim is made and no confidence intervals are shown. The P90-P10 spread measures absolute percentage-point inequality; relative inequality can behave differently. Bounds at zero and 100 and complete-case selection affect interpretation.',
          'Adoption rises across the distribution while the absolute P90-P10 gap widens; broad progress and absolute convergence are different claims.'],
        detailed_interpretation=findings+' Panel A therefore supports broad improvement without absolute convergence on this particular spread measure. Panel B shows why a distributional shift must not be read as the gain of a typical matched country: reordering and heterogeneity affect the two summaries differently. The analysis describes included countries, not a population-weighted distribution of people, and does not identify the causes of progress.')
    (OUT/'adoption_quantile_entry.json').write_text(json.dumps(entry,indent=2))
    print(json.dumps(metrics,indent=2))
    return entry

if __name__=='__main__':build()
