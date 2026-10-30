"""Seven analytical figures using existing country and full daily weather caches.

Writes figures, numerical evidence, and reading guides; does not mutate REPORT.md.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import Normalize, TwoSlopeNorm, PowerNorm
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'images/quality'
DATA = ROOT / 'data/quality'
INK = '#193044'
REGIONS = ['Africa', 'Asia', 'Europe', 'North America', 'South America', 'Oceania', 'Unclassified']
COLORS = ['#0072b2', '#d55e00', '#009e73', '#cc79a7', '#8c6d31', '#5b51a5', '#707070']
FIELDS = ['internet_users_share_pct', 'telephone_lines_per100', 'broadband_subs_per100', 'mobile_subs_per100']
LABELS = ['Internet adoption (%)', 'Landlines / 100', 'Broadband / 100', 'Mobile / 100']
FIGURES = []


def finish(fig, key, title, findings, question, encoding, rationale, limits, takeaway):
    fig.savefig(OUT / f'{key}.png', dpi=210, bbox_inches='tight', facecolor='white')
    fig.savefig(OUT / f'{key}.svg', bbox_inches='tight', facecolor='white')
    plt.close(fig)
    FIGURES.append(dict(key=key, title=title, path=f'images/quality/{key}.png', caption=findings,
        explanation=[question, encoding, rationale, limits, takeaway]))


def geography(ax, title):
    ax.set(xlim=(-125, -66), ylim=(24, 50), xlabel='Longitude (degrees east)', ylabel='Latitude (degrees north)')
    ax.set_aspect(1.3)
    ax.set_facecolor('#e8ecf0')
    ax.set_title(title, loc='left', fontsize=12, pad=10)
    ax.tick_params(labelsize=9)


def footer(fig, text):
    fig.supxlabel(text, fontsize=10, color=INK)


def longest_run(condition):
    current = np.zeros(condition.shape[1:], dtype=int)
    longest = current.copy()
    for row in condition:
        current = np.where(row, current+1, 0)
        longest = np.maximum(longest, current)
    return longest


def country_figures():
    raw = pd.read_json(ROOT / 'data/infovis_countries.json')
    old = raw[raw.year == 2015].set_index('code')
    latest = raw[raw.year == 2020].set_index('code')
    codes = old.index.intersection(latest.index)
    frame = latest.loc[codes].copy()
    delta = frame[FIELDS] - old.loc[codes, FIELDS]
    delta['country'], delta['region'] = frame.country, frame.region
    delta.to_csv(DATA / 'matched_country_changes.csv')
    corr = frame[FIELDS].corr(method='spearman')
    dcorr = delta[FIELDS].corr(method='spearman')
    corr.to_csv(DATA / 'matched_level_spearman.csv')
    dcorr.to_csv(DATA / 'matched_change_spearman.csv')
    metrics = dict(n=len(codes), positive_internet_negative_landline=int(((delta[FIELDS[0]]>0)&(delta[FIELDS[1]]<0)).sum()),
        level_broadband_rho=float(corr.loc[FIELDS[0], FIELDS[2]]),
        level_mobile_rho=float(corr.loc[FIELDS[0], FIELDS[3]]),
        change_broadband_rho=float(dcorr.loc[FIELDS[0], FIELDS[2]]))
    # Four measured attributes, identically scaled region facets; area has no hidden offset.
    fig, axes = plt.subplots(2, 4, figsize=(16, 8.5), layout='constrained', sharex=True, sharey=True)
    norm = Normalize(0, float(frame[FIELDS[3]].max()))
    area_factor = 6.0
    for ax, region in zip(axes.flat, REGIONS):
        sub = frame[frame.region == region].sort_values(FIELDS[1], ascending=False)
        points = ax.scatter(sub[FIELDS[2]], sub[FIELDS[0]], s=area_factor*sub[FIELDS[1]],
            c=sub[FIELDS[3]], cmap='viridis', norm=norm, edgecolors=INK, linewidths=.4, alpha=.9)
        zero = sub[sub[FIELDS[1]]==0]
        ax.scatter(zero[FIELDS[2]], zero[FIELDS[0]], s=18, facecolors='none', edgecolors=INK)
        ax.set_title(f'{region} | n={len(sub)}', loc='left', fontsize=12)
        ax.set(xlim=(-2, np.ceil(frame[FIELDS[2]].max()/10)*10+2), ylim=(-3,108), yticks=[0,20,40,60,80,100])
        ax.grid(alpha=.15); ax.set_axisbelow(True)
        ax.set_xlabel('Broadband subscriptions / 100')
        ax.set_ylabel('Internet adoption (%)')
    legend_ax = axes.flat[-1]; legend_ax.axis('off')
    handles = [legend_ax.scatter([], [], s=area_factor*v, facecolor='#bbc9d1', edgecolor=INK, label=str(v)) for v in [1,10,30,60]]
    legend_ax.legend(handles=handles, title='Landlines / 100\nMarker AREA proportional to value', loc='center', frameon=False, labelspacing=1.5, fontsize=11)
    fig.colorbar(points, ax=list(axes.flat), shrink=.75, pad=.025, label='Mobile subscriptions per 100 people')
    fig.suptitle('Similar adoption, different infrastructure profiles', fontsize=20, color=INK)
    footer(fig, '2020 | Same 175 countries used in the change analysis | All facet scales fixed | Subscriptions are not unique people')
    finish(fig, 'telecom_four_variables', 'Four-measure country profiles on a matched panel.',
        f'All 175 matched countries are displayed in 2020. On this same panel, the Spearman association of adoption with broadband is {metrics["level_broadband_rho"]:.3f}, compared with {metrics["level_mobile_rho"]:.3f} for mobile subscriptions. Region facets separate overlapping profiles while preserving all four measurement channels. These associations describe levels, not the mechanisms producing adoption.',
        'Do countries with comparable internet adoption have similar fixed and mobile infrastructure?',
        'Each marker is one country. Horizontal position gives broadband subscriptions per 100, vertical position gives adoption percentage, color gives mobile subscriptions per 100, and marker area is proportional to landlines per 100. Seven supplied-region facets share identical domains. A numeric area legend and mobile colorbar make the two nonposition encodings explicit; tiny positive landline values intentionally produce tiny markers.',
        'Four actual telecom measurements are compared without a composite score. Faceting preserves regional context while reducing overlap. Using exactly the 175 countries in the 2015-2020 change analysis makes the subsequent comparison of levels and changes defensible. The parallel-coordinate views retain precise axis intercepts for profiles that are harder to read by marker size.',
        'Read position before color and area. Area is less precise than position, so consult the scatterplot matrix for individual pairwise relationships. The panel is complete-case and country-weighted. Unclassified denotes missing regional labels. Subscription intensities can exceed 100 and are not ownership percentages. None of these observational relationships identifies a cause.',
        'Broadband is more closely associated with adoption levels than mobile intensity on the matched panel.')

    fig, axes = plt.subplots(2,4,figsize=(16,8.5),layout='constrained',sharex=True,sharey=True)
    lim = float(np.max(np.abs(delta[FIELDS[2]])))
    norm = TwoSlopeNorm(vmin=-lim,vcenter=0,vmax=lim)
    xmin,xmax=delta[FIELDS[1]].min()-2,delta[FIELDS[1]].max()+2
    ymin,ymax=min(-3,delta[FIELDS[0]].min()-3),delta[FIELDS[0]].max()+3
    for ax,region in zip(axes.flat,REGIONS):
        sub=delta[delta.region==region]
        points=ax.scatter(sub[FIELDS[1]],sub[FIELDS[0]],c=sub[FIELDS[2]],norm=norm,cmap='RdBu_r',s=38,edgecolors=INK,linewidths=.4)
        ax.axvline(0,color=INK,lw=.8); ax.axhline(0,color=INK,lw=.8)
        ax.set(xlim=(xmin,xmax),ylim=(ymin,ymax),xlabel='Landline change / 100',ylabel='Adoption change (percentage points)')
        count=((sub[FIELDS[1]]<0)&(sub[FIELDS[0]]>0)).sum()
        ax.set_title(f'{region} | {count}/{len(sub)} in upper left',loc='left',fontsize=11)
        ax.grid(alpha=.12); ax.set_axisbelow(True)
    ax=axes.flat[-1]; ax.axis('off')
    ax.text(.04,.76,f'{metrics["positive_internet_negative_landline"]} / {len(codes)} countries',transform=ax.transAxes,fontsize=20,color=INK)
    ax.text(.04,.56,'Adoption rose while\nlandline intensity fell.',transform=ax.transAxes,fontsize=13)
    ax.text(.04,.25,'Upper-left quadrant =\npositive adoption change,\nnegative landline change.\n\nAssociation, not substitution proof.',transform=ax.transAxes,fontsize=11)
    fig.colorbar(points,ax=list(axes.flat),shrink=.75,pad=.025,label='Broadband change per 100 people (2020 minus 2015)')
    fig.suptitle('Adoption gains often coexist with declining landline intensity',fontsize=19,color=INK)
    footer(fig,'175 matched countries | 2020 minus 2015 | Three measured changes + regional grouping | Fixed axes and color limits')
    finish(fig,'country_change_quadrants','Matched-country changes reveal divergent infrastructure paths.',
        f'Internet adoption increased while landline intensity fell in {metrics["positive_internet_negative_landline"]} of 175 countries ({100*metrics["positive_internet_negative_landline"]/175:.1f}%). Spearman association between adoption change and broadband change is {metrics["change_broadband_rho"]:.3f}, versus {metrics["level_broadband_rho"]:.3f} between their 2020 levels on exactly the same countries. A strong level association therefore does not imply that five-year increases track one another.',
        'Does the strong association of infrastructure levels also describe changes within countries?',
        'Each country appears once in its supplied-region facet. X gives landline change per 100 and Y adoption change in percentage points, both 2020 minus 2015. A zero-centered diverging scale gives broadband change per 100. Zero lines define the quadrants. Panel headings count positive-adoption, negative-landline cases; points on zero boundaries are excluded from that strict count.',
        'Country-level changes preserve heterogeneity that regional medians conceal. All panels share domains, and both dates have complete observations for all four indicators in the same 175 countries. Keeping signed broadband changes in color avoids encoding negative quantities as bubble sizes. This complements the retained regional dumbbell rather than replacing its summary purpose.',
        'Changes compare two endpoints and cannot identify the year of transition. Population changes can also alter subscriptions per 100. Differences in rank correlations across levels and changes do not establish causation, substitution, or statistical significance. Region is context, not an income proxy. A small change correlation does not imply that broadband is irrelevant.',
        'Cross-sectional infrastructure associations and within-country change tell different stories.')

    fig,axes=plt.subplots(4,4,figsize=(12.5,11.5),layout='constrained')
    for i in range(4):
        for j in range(4):
            ax=axes[i,j]
            if i>j:
                for region,color in zip(REGIONS,COLORS):
                    sub=frame[frame.region==region]
                    ax.scatter(sub[FIELDS[j]],sub[FIELDS[i]],s=13,color=color,alpha=.7,linewidths=0)
                ax.grid(alpha=.12)
            elif i==j:
                ax.hist(frame[FIELDS[i]],bins=16,color='#54839b',edgecolor='white')
                ax.set_title(LABELS[i],fontsize=10)
                ax.set_ylabel('Countries',fontsize=9)
            else:
                ax.axis('off')
                ax.text(.5,.58,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',fontsize=27,color=INK,transform=ax.transAxes)
                ax.text(.5,.30,'Spearman rho',ha='center',fontsize=10,transform=ax.transAxes)
            if i==3: ax.set_xlabel(LABELS[j])
            if j==0 and i!=0: ax.set_ylabel(LABELS[i])
            ax.tick_params(labelsize=8)
    fig.suptitle('Four telecom measures: associations and exceptions',fontsize=20,color=INK)
    fig.legend(handles=[Line2D([],[],marker='o',ls='',color=c,label=r) for r,c in zip(REGIONS,COLORS)],loc='outside lower center',ncol=4,frameon=False)
    finish(fig,'telecom_scatterplot_matrix','Pairwise relationships across four telecom measures.',
        f'The same 175 matched countries contribute to every cell. Adoption-broadband Spearman rho is {metrics["level_broadband_rho"]:.3f}, adoption-mobile is {metrics["level_mobile_rho"]:.3f}, and landlines-broadband is {corr.iloc[1,2]:.3f}. Raw points expose variation around these pooled associations. Diagonal histograms show unequal and skewed measurement distributions.',
        'Which pairwise relationships explain the patterns seen in the four-variable profile plot?',
        'The lower triangle contains all six pairwise scatterplots of adoption, landlines, broadband and mobile in 2020. Country color gives supplied region. Diagonal panels show equal-country histograms; the upper triangle gives descriptive Spearman coefficients. Axis units remain explicit. The full figure displays four measured variables, while each individual scatter cell is bivariate.',
        'A scatterplot matrix exposes individual measurements, outliers and possible nonlinearity that a correlation-only heatmap hides. It also supplies a position-based cross-check for the color and area encodings in the profile figure. Every cell uses identical complete-case membership, so differing coefficients cannot be attributed to pairwise changes in the sample.',
        'Pooled correlations can reflect differences between regions and need not hold within each region. There are no significance stars or causal claims. Diagonal binning is descriptive and should not be treated as evidence of distinct country clusters. Subscription units differ from adoption percentages; high mobile values do not imply universal access.',
        'Fixed broadband and landlines share stronger rank relationships than mobile intensity on this panel.')
    return metrics


def weather_figures():
    with np.load(ROOT/'data/scivis/gridmet_2023-07-01_2023-09-30_daily_s6.npz') as z:
        t,p,s,d=[z[k].astype(float) for k in ['tmmx','pr','vs','th']]
        dates,lat,lon=[z[k] for k in ['dates','lat','lon']]
    valid=np.all(np.isfinite(t)&np.isfinite(p)&np.isfinite(s)&np.isfinite(d),axis=0)
    weights=np.broadcast_to(np.cos(np.deg2rad(lat))[:,None],valid.shape)
    w=weights[valid]
    months=np.array([date[5:7] for date in dates])
    time=dates.astype('datetime64[D]')
    joint=(t>=35)&(p<1)&valid
    daily=np.average(joint[:,valid],axis=1,weights=w)*100
    freq=np.where(valid,joint.mean(axis=0)*100,np.nan)
    runs=np.where(valid,longest_run(joint),np.nan)
    july=t[months=='07'].mean(axis=0); september=t[months=='09'].mean(axis=0)
    change=np.where(valid,september-july,np.nan)
    endpoint=t[-1]-t[0]
    metrics=dict(common_cells=int(valid.sum()),max_hot_dry_date=str(dates[daily.argmax()]),
        min_hot_dry_date=str(dates[daily.argmin()]),max_hot_dry_area_pct=float(daily.max()),
        min_hot_dry_area_pct=float(daily.min()),max_run_days=int(np.nanmax(runs)),
        mean_hot_dry_area_pct=float(daily.mean()),
        monthly_change_mean_C=float(np.average(change[valid],weights=w)),
        monthly_cooler_area_pct=float(np.average(change[valid]<0,weights=w)*100),
        endpoint_sign_disagreement_pct=float(np.average(change[valid]*endpoint[valid]<0,weights=w)*100))
    records=[]
    for temp in [33,35,37]:
        for rain in [.1,1]:
            flag=(t[:,valid]>=temp)&(p[:,valid]<rain)
            records.append(dict(tmax_threshold_C=temp,rain_below_mm=rain,
                area_day_pct=float(np.average(flag.mean(axis=0),weights=w)*100),
                maximum_run_days=int(longest_run(flag).max())))
    pd.DataFrame(records).to_csv(DATA/'threshold_sensitivity.csv',index=False)
    pd.DataFrame({'date':dates,'hot_dry_area_pct':daily}).to_csv(DATA/'compound_daily.csv',index=False)
    np.savez_compressed(DATA/'weather_summaries.npz',frequency_pct=freq,longest_run_days=runs,monthly_change_C=change,valid=valid,lat=lat,lon=lon)

    fig=plt.figure(figsize=(15,9),layout='constrained')
    gs=fig.add_gridspec(2,2,height_ratios=[1.4,.75])
    for ax,a,cmap,label,title in [(fig.add_subplot(gs[0,0]),freq,'magma','Days meeting both conditions (%)','A. Frequency across all 92 days'),
            (fig.add_subplot(gs[0,1]),runs,'viridis','Longest consecutive run (days)','B. Persistence; runs cross month boundaries')]:
        im=ax.pcolormesh(lon,lat,a,cmap=cmap,vmin=0,vmax=100 if a is freq else 92,shading='auto',rasterized=True)
        geography(ax,title); fig.colorbar(im,ax=ax,shrink=.7,label=label)
    ax=fig.add_subplot(gs[1,0])
    ax.fill_between(time,daily,color='#bc5d3c',alpha=.18); ax.plot(time,daily,color='#a84527',lw=1.7)
    ax.scatter(time[daily.argmax()],daily.max(),c=INK,zorder=3)
    ax.annotate(f'{metrics["max_hot_dry_date"]}: {daily.max():.1f}%',(time[daily.argmax()],daily.max()),xytext=(8,-18),textcoords='offset points',fontsize=10)
    ax.set(ylabel='Sampled area (%)',ylim=(0,42)); ax.set_title('C. Daily area meeting both conditions',loc='left',fontsize=12)
    ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y')); ax.grid(alpha=.15)
    ax=fig.add_subplot(gs[1,1])
    for threshold,color in zip([.1,1],['#297999','#a84527']):
        rows=[r for r in records if r['rain_below_mm']==threshold]
        ax.plot([r['tmax_threshold_C'] for r in rows],[r['area_day_pct'] for r in rows],'-o',color=color,label=f'Rain < {threshold:g} mm/day')
    ax.set(xlabel='Tmax threshold (degrees C)',ylabel='Area-day frequency (%)',xticks=[33,35,37],ylim=(0,35))
    ax.set_title('D. Frequency depends on the declared thresholds',loc='left',fontsize=12); ax.legend(fontsize=9); ax.grid(alpha=.15)
    fig.suptitle('Hot and dry together: frequency is different from persistence',fontsize=20,color=INK)
    footer(fig,'Main definition: Tmax >= 35 C AND rain < 1 mm/day | Jul-Sep 2023 | Approximate area weights | Descriptive thresholds, not an official hazard index')
    finish(fig,'compound_frequency_persistence','Joint hot-dry frequency, persistence and threshold sensitivity.',
        f'The two conditions coincide over a mean {daily.mean():.2f}% of sampled area-days and peak at {daily.max():.2f}% of sampled area on {metrics["max_hot_dry_date"]}. The longest cellwise run is {metrics["max_run_days"]} days within the observed 92-day window. Runs can cross month boundaries. Threshold sensitivity is shown explicitly for Tmax cutoffs 33, 35 and 37 C and rain cutoffs 0.1 and 1 mm/day; the area-day frequency changes with those choices.',
        'Are repeated hot-dry days scattered occurrences or sustained runs at the same locations?',
        'The first map shows the percentage of the 92 days satisfying the joint condition at each cell. The second shows the longest consecutive run using the same daily Boolean sequence. The timeline gives each day\'s cosine-latitude-weighted area fraction; the final panel recomputes total frequency under six threshold combinations. Missing cells are gray; zero frequency remains a valid observed result.',
        'Joint daily evaluation tests co-occurrence directly, rather than assuming that separate hot and dry frequencies multiply. Persistence distinguishes equal totals with different timing. The sensitivity panel exposes how a derived indicator depends on analyst choices. All summaries use a fixed common footprint complete across all four weather fields and dates, preventing changing support from creating apparent shifts.',
        'A maximum run can be truncated by the beginning or end of the observation window. The thresholds are descriptive and do not define official drought, heatwaves, fire danger, or population exposure. Spatial grid values and neighboring days are dependent. Approximate area weights describe the sampled land footprint, and no long-term climatic baseline is available.',
        'Frequency, timing and persistence answer distinct questions; the joint condition must be calculated day by day.')

    fig,axes=plt.subplots(1,2,figsize=(15,6.5),layout='constrained',gridspec_kw={'width_ratios':[1.55,1]})
    lim=float(np.ceil(np.nanmax(np.abs(change))))
    im=axes[0].pcolormesh(lon,lat,change,cmap='RdBu_r',vmin=-lim,vmax=lim,shading='auto',rasterized=True)
    geography(axes[0],'A. September mean Tmax minus July mean Tmax')
    fig.colorbar(im,ax=axes[0],shrink=.7,label='Difference in monthly mean Tmax (degrees C)')
    X=np.broadcast_to(lon[None,:],valid.shape)
    for name,mask,color in [('West (< -105)',X< -105,'#0072b2'),('Central (-105 to < -90)',(X>=-105)&(X< -90),'#d55e00'),('East (>= -90)',X>=-90,'#009e73')]:
        mask=mask&valid; values=change[mask]; weight=weights[mask]; order=np.argsort(values)
        axes[1].step(values[order],100*np.cumsum(weight[order])/weight.sum(),where='post',label=name,color=color,lw=2)
    axes[1].axvline(0,c=INK,lw=1,ls='--')
    axes[1].set(xlabel='September minus July (degrees C)',ylabel='Cumulative sampled sector area (%)',ylim=(0,100))
    axes[1].set_title('B. Area-weighted distributions of cellwise change',loc='left',fontsize=12)
    axes[1].legend(loc='lower right',fontsize=9); axes[1].grid(alpha=.15)
    fig.suptitle('Compare complete months, not only two weather snapshots',fontsize=20,color=INK)
    footer(fig,f'31 July days + 30 September days | Mean change {metrics["monthly_change_mean_C"]:.2f} C | {metrics["monthly_cooler_area_pct"]:.1f}% of sampled area cooler | Not a climate anomaly')
    finish(fig,'monthly_temperature_change','Complete-month temperature differences and spatial distributions.',
        f'The approximate area-weighted September-minus-July change in mean daily maximum temperature is {metrics["monthly_change_mean_C"]:.2f} C; {metrics["monthly_cooler_area_pct"]:.2f}% of the common sampled area is cooler. Compared with September 30 minus July 1, the sign differs over {metrics["endpoint_sign_disagreement_pct"]:.2f}% of area. Monthly means use all 31 July and 30 September days, and the sector ECDFs reveal spatial variation hidden by a single mean.',
        'How does the temperature change across complete months differ from an endpoint-only comparison?',
        'A zero-centered diverging map encodes September mean daily maximum temperature minus July mean daily maximum temperature at each cell. Blue denotes cooling and red warming. The adjacent weighted empirical distributions show the fraction of each fixed longitude sector at or below a given difference. Both computations use common complete cells and cosine-latitude weights; longitude bands are analyst-defined.',
        'A mean of all daily fields is a more representative month comparison than a difference between two dates. The distribution panel adds spatial heterogeneity without introducing arbitrary smoothing or significance tests. Each month is averaged by its actual day count, so the unequal month lengths do not mechanically inflate the statistic. The previous endpoint map remains available as historical supporting material.',
        'These are differences in means of daily maxima, not differences in mean air temperature. The ECDF is a distribution over space, not a confidence interval. A three-month interval provides no climatological baseline and cannot establish climate change. Subsampling approximates the spatial footprint. Exact zero differences are neither warming nor cooling.',
        'A two-date map can give a different direction of change from a complete-month comparison.')

    # Fixed latitude band, identical support per longitude across all dates/fields.
    band=(lat>=30)&(lat<=45)
    mask=valid&band[:,None]
    wt=np.where(mask,weights,0)
    denom=wt.sum(axis=0)
    def zonal(a):
        return np.divide(np.sum(np.where(mask[None,:,:],a,0)*wt,axis=1),denom[None,:],out=np.full((92,len(lon)),np.nan),where=denom[None,:]>0)
    hovt,hovp=zonal(t),zonal(p)
    np.savez_compressed(DATA/'hovmoller.npz',temperature_C=hovt,rain_mm=hovp,lon=lon,dates=dates,latitude_range=[30,45],cell_counts=mask.sum(axis=0))
    fig=plt.figure(figsize=(15,10),layout='constrained')
    gs=fig.add_gridspec(2,2,height_ratios=[.45,1])
    ax=fig.add_subplot(gs[0,0])
    ax.pcolormesh(lon,lat,np.where(valid,1,np.nan),cmap=matplotlib.colors.ListedColormap(['#c6d4dd']),shading='auto',rasterized=True)
    ax.axhspan(30,45,facecolor='#de9c58',alpha=.24); ax.axhline(30,c='#a66b29'); ax.axhline(45,c='#a66b29')
    geography(ax,'A. Fixed averaging band: 30-45 degrees north')
    ax=fig.add_subplot(gs[0,1]); ax.axis('off')
    ax.text(.02,.9,'How to read the paired diagrams',transform=ax.transAxes,fontsize=15,color=INK)
    ax.text(.02,.68,'Move horizontally to follow one longitude through time.\nMove vertically to compare west and east on one date.\nEach value averages valid land cells within 30-45 N.\nIdentical cells and dates support both weather fields.\nRain uses square-root color normalization, including zero.',transform=ax.transAxes,fontsize=11,linespacing=1.65,va='top')
    for ax,a,cmap,norm,label,title in [(fig.add_subplot(gs[1,0]),hovt,'inferno',Normalize(np.nanmin(hovt),np.nanmax(hovt)),'Mean daily Tmax (degrees C)','B. Temperature: all 92 dates'),
            (fig.add_subplot(gs[1,1]),hovp,'Blues',PowerNorm(.5,vmin=0,vmax=np.nanmax(hovp)),'Mean daily precipitation (mm)','C. Precipitation: identical support')]:
        im=ax.pcolormesh(time,lon,a.T,cmap=cmap,norm=norm,shading='auto',rasterized=True)
        ax.set(ylabel='Longitude (degrees east)',xlabel='Date in 2023',ylim=(-125,-66))
        ax.set_title(title,loc='left',fontsize=12); ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        fig.colorbar(im,ax=ax,pad=.02,label=label)
    fig.suptitle('When and where do warm and rainy periods occur?',fontsize=20,color=INK)
    footer(fig,'Latitude-weighted band means | Missing or unsupported longitudes remain masked | Aggregated patterns do not trace individual storms')
    imax=np.unravel_index(np.nanargmax(hovp),hovp.shape)
    metrics['hov_rain_max_mm']=float(hovp[imax]); metrics['hov_rain_max_date']=str(dates[imax[0]])
    metrics['hov_rain_max_longitude']=float(lon[imax[1]])
    finish(fig,'weather_hovmoller','Paired time-longitude diagrams retain all daily weather fields.',
        f'The aligned diagrams use all 92 dates, averaging common valid cells from 30 to 45 degrees north at each sampled longitude. Temperature band means range from {np.nanmin(hovt):.2f} to {np.nanmax(hovt):.2f} C. The largest precipitation band mean is {hovp[imax]:.2f} mm on {dates[imax[0]]} at longitude {lon[imax[1]]:.2f} degrees. These are band averages, not the most extreme individual cells.',
        'What daily time-space structure is hidden by calendars, sector averages and monthly maps?',
        'Horizontal position is date and vertical position is longitude in both lower panels. Color shows weighted temperature or daily precipitation in separate aligned panels. The reference map identifies the fixed 30-45 degree north averaging band. Temperature uses a linear scale; rain uses square-root normalization with a colorbar in actual millimeters, including zero. Each longitude retains identical common valid land cells across all dates.',
        'A time-space diagram retains all 92 days while exposing differences across longitude. Matched panels make temperature and rainfall timing comparable without forcing incompatible measurements onto one color scale. The latitude band and weighting are explicit, so the reduction from a spatial field to a diagram is reproducible. It replaces the additional weather horizon, while the two required country horizon variations remain.',
        'Longitude columns contain different amounts of valid land, and the support counts are saved with the arrays. Averaging across latitude hides local extremes. Apparent diagonal patterns cannot be equated with tracked storm motion. This is a descriptive surface-weather adaptation of a Hovmoller diagram, not an upper-atmosphere wave diagnosis or a climate-trend result.',
        'Daily time-space diagrams reveal temporal detail that a coverage calendar cannot convey.')

    # Extreme contrasts use an objective full-footprint daily condition, not manual selection.
    chosen=[int(daily.argmax()),int(daily.argmin())]
    fig,axes=plt.subplots(2,1,figsize=(14,11.5),layout='constrained')
    norm=Normalize(np.nanmin(t[chosen]),np.nanmax(t[chosen]))
    X,Y=np.meshgrid(lon,lat); step=9; sl=(slice(None,None,step),slice(None,None,step))
    for ax,i,kind in zip(axes,chosen,['Maximum','Minimum']):
        im=ax.pcolormesh(lon,lat,np.where(valid,t[i],np.nan),cmap='YlOrRd',norm=norm,shading='auto',rasterized=True)
        cs=ax.contour(lon,lat,np.where(valid,p[i],np.nan),levels=[5,20,50],colors=['#064273'],linewidths=[.6,1,1.5],algorithm='serial')
        ax.clabel(cs,fmt=lambda v:f'{v:g} mm',fontsize=9,inline=True)
        theta=np.deg2rad(d[i][sl]); speed=s[i][sl]
        u=-speed*np.sin(theta); v=-speed*np.cos(theta)
        good=valid[sl]&(speed>.1)
        u=np.where(good,u,np.nan); v=np.where(good,v,np.nan)
        angles=np.rad2deg(np.arctan2(v*1.3,u/np.cos(np.deg2rad(Y[sl]))))
        q=ax.quiver(X[sl],Y[sl],u,v,angles=angles,scale_units='inches',scale=35,color='#18242e',width=.0017,pivot='mid')
        key=ax.quiverkey(q,.85,1.04,5,'5 m/s',labelpos='E',coordinates='axes'); key.text.set_fontsize(10)
        geography(ax,f'{dates[i]} | {kind} hot-dry area: {daily[i]:.1f}%')
    fig.colorbar(im,ax=list(axes),shrink=.85,pad=.015,label='Daily maximum temperature (degrees C)')
    fig.suptitle('Four weather fields on the same dates',fontsize=21,color=INK)
    footer(fig,'Fill: Tmax | Blue labeled contours: daily rain (5 / 20 / 50 mm) | Arrows: flow-to direction and speed\nSame scales and sampled arrow locations | Extreme contrast, not typical conditions | Daily summaries are not simultaneous observations')
    finish(fig,'weather_four_fields','Temperature, rainfall and wind in one aligned weather comparison.',
        f'The dates are selected reproducibly as the maximum and minimum daily hot-dry area fractions over the full common footprint: {dates[chosen[0]]} ({daily[chosen[0]]:.2f}%) and {dates[chosen[1]]} ({daily[chosen[1]]:.2f}%). Both maps use the same temperature limits, rain-contour levels, arrow locations and speed-to-length scale. Wind speed and direction add distinct measurements to the temperature-rainfall comparison.',
        'Where do temperature, rainfall and wind patterns coincide on objectively selected contrasting days?',
        'Background color is daily maximum temperature. Blue labeled lines are precipitation contours at 5, 20 and 50 millimeters. Arrow bearing gives flow-to direction and arrow length gives speed, with a 5 m/s key. Dates define panels. The four measured fields therefore use separate channels; longitude and latitude provide spatial context. Every ninth cell of the already stride-six cache is retained for arrows.',
        'This synthesis brings the required scalar, contour and vector methods together to inspect joint spatial patterns. Objective selection by the previously declared hot-dry area fraction makes the contrast reproducible. Shared limits prevent apparent differences caused by rescaling. The standalone color, contour and quiver experiments remain available to explain and test each layer before interpreting the composite.',
        'The selection deliberately contrasts extremes and is not representative of every day. Daily maximum temperature, rainfall accumulation and wind summaries need not occur simultaneously. Arrow bearings account for map aspect and cosine latitude; they indicate where air flows, opposite the stored source direction. Coarse wind inputs and display thinning limit local inference, and overlapping patterns do not establish causation.',
        'Four-field maps support joint spatial inspection when each layer has a distinct, explicit encoding.')
    return metrics


def main():
    OUT.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':INK,'text.color':INK,'axes.titlecolor':INK,'svg.fonttype':'none'})
    metrics={'country':country_figures(),'weather':weather_figures()}
    (DATA/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    (DATA/'figures.json').write_text(json.dumps(FIGURES,indent=2),encoding='utf-8')
    print(json.dumps(metrics,indent=2)); print(f'Created {len(FIGURES)} figures in {OUT}')


if __name__=='__main__':
    main()
