"""Add figures 17-28 using audited daily weather and the fixed country panels."""
from pathlib import Path
from datetime import datetime
import calendar
import csv
import html
import json
import re
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize, ListedColormap
from matplotlib.patches import Rectangle, Patch
from build_scivis import plt, map_axis, save_figure
from build_temporal_figures import reflected_kde

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images/extensions"
COLORS = ["#176e9d", "#cd7131", "#795699"]


def weighted_quantile(values, weights, probs):
    order = np.argsort(values)
    v, w = values[order], weights[order]
    return np.interp(probs, (np.cumsum(w) - .5*w)/w.sum(), v)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.titlecolor": "#193044"})
    manifest = json.loads((ROOT / "data/scivis/daily_manifest.json").read_text())
    sampled = json.loads((ROOT / "data/scivis/manifest.json").read_text())["sample_dates"]
    with np.load(ROOT / manifest["cache"]) as z:
        lat, lon, dates = z["lat"], z["lon"], z["dates"]
        t, p, s, d = (z[k] for k in ["tmmx", "pr", "vs", "th"])
    assert len(dates) == 92 and all(a.shape == (92, len(lat), len(lon)) for a in [t,p,s,d])
    assert np.array_equal(np.diff(dates.astype("datetime64[D]")), np.full(91, np.timedelta64(1,"D")))
    assert np.nanmin(p) >= 0 and np.nanmin(s) >= 0
    assert np.nanmin(t) > -90 and np.nanmax(t) < 65 and 0 <= np.nanmin(d) <= np.nanmax(d) <= 360
    common = np.all(np.isfinite(t), axis=0)
    assert np.array_equal(common, np.isfinite(t[0]))  # fixed footprint throughout
    weights = np.broadcast_to(np.cos(np.deg2rad(lat))[:,None], common.shape)
    month_masks = [np.array([date[5:7] == month for date in dates]) for month in ["07","08","09"]]
    assert [int(x.sum()) for x in month_masks] == [31,31,30]
    metrics, captions = {"coverage": manifest["month_counts"], "common_temperature_cells": int(common.sum())}, []
    coverage=pd.DataFrame({"date":dates,"month":[date[:7] for date in dates],"animation_sample":[date in sampled for date in dates]})
    for key,a in zip(["tmmx","pr","vs","th"],[t,p,s,d]):
        coverage[f"{key}_valid_grid_cells"]=np.isfinite(a).sum(axis=(1,2))
    coverage.to_csv(ROOT/"data/scivis/daily_coverage.csv",index=False)

    def finish(fig, num, name, title, caption):
        save_figure(fig, OUT, name)
        plt.close(fig)
        captions.append({"figure": num, "name": name, "title": title, "caption": caption, "path": f"images/extensions/{name}.png"})

    # 17: actual daily coverage versus the eight display dates.
    fig, axes = plt.subplots(1,3,figsize=(15,5),constrained_layout=True)
    fig.suptitle("92 daily fields available | 8 dates selected for animations",fontsize=19)
    fig.get_layout_engine().set(rect=(0,.08,1,.92))
    for ax, month in zip(axes,[7,8,9]):
        for row, week in enumerate(calendar.Calendar(firstweekday=0).monthdayscalendar(2023,month)):
            for col, day in enumerate(week):
                if day:
                    when=f"2023-{month:02d}-{day:02d}"
                    selected=when in sampled
                    ax.add_patch(Rectangle((col,row),.92,.92,facecolor="#d4e8f1",edgecolor="#d56e20" if selected else "white",lw=3 if selected else 1))
                    ax.text(col+.46,row+.46,str(day),ha="center",va="center",fontweight="bold" if selected else "normal")
        ax.set(xlim=(-.1,7),ylim=(6,-.2),xticks=np.arange(7)+.46,xticklabels=["M","T","W","T","F","S","S"],yticks=[])
        ax.set_title(f"{calendar.month_name[month]} | {calendar.monthrange(2023,month)[1]} days")
        ax.xaxis.tick_top()
        ax.set_aspect("equal")
        for sp in ax.spines.values(): sp.set_visible(False)
    fig.legend(handles=[Patch(facecolor="#d4e8f1",label="Available daily field"),Patch(facecolor="white",edgecolor="#d56e20",lw=3,label="One of eight animation dates")],loc="lower center",ncol=2,frameon=False)
    finish(fig,17,"daily_coverage_calendar","Daily coverage and animation sampling","All four annual files have 365 time coordinates; the selected interval has 92 consecutive dates, with 31 in July, 31 in August and 30 in September. Every selected day has valid grid values in all four variables. Orange outlines identify only the eight original animation samples, spaced 13 days apart. Available dates are not limited to those samples.")

    # Daily sector summaries: regions are deliberately operationalized as longitude bands.
    X=np.broadcast_to(lon[None,:],common.shape)
    sectors=[("West: longitude < -105°",X < -105), ("Central: -105° to < -90°",(X>=-105)&(X < -90)),("East: longitude >= -90°",X>=-90)]
    stats=[]
    for label, region in sectors:
        mask=region & common
        q=np.array([weighted_quantile(a[mask],weights[mask],[.1,.5,.9]) for a in t])
        mean=np.array([np.average(a[mask],weights=weights[mask]) for a in t])
        stats.append((label,mask,q,mean))
    records=[]
    for k,(label,mask,q,mean) in enumerate(stats):
        for i,date in enumerate(dates):
            records.append({"date":date,"sector":label,"grid_cells":int(mask.sum()),"area_mean_tmax_C":mean[i],"spatial_p10_C":q[i,0],"spatial_median_C":q[i,1],"spatial_p90_C":q[i,2]})
    pd.DataFrame(records).to_csv(ROOT/"data/scivis/daily_sector_statistics.csv",index=False)
    fig,axes=plt.subplots(3,1,figsize=(14,9),sharex=True,sharey=True,constrained_layout=True)
    fig.suptitle("Daily maximum temperature: spatial spread within longitude sectors",fontsize=18)
    time=dates.astype("datetime64[D]")
    for ax,color,(label,mask,q,mean) in zip(axes,COLORS,stats):
        ax.fill_between(time,q[:,0],q[:,2],color=color,alpha=.19,label="Area-weighted spatial p10-p90")
        ax.plot(time,q[:,1],color=color,lw=1.8,label="Spatial median")
        ax.plot(time,mean,color="#172434",lw=1,ls="--",label="Area-weighted mean")
        ax.set_title(f"{label} | {int(mask.sum()):,} valid display cells",loc="left")
        ax.set_ylabel("Tmax (°C)");ax.grid(alpha=.15)
        ax.set_ylim(-5,50)
    axes[0].legend(ncol=3,fontsize=8,loc="upper right")
    fig.supxlabel("All 92 days | Ribbons show spatial variability, not uncertainty or confidence intervals",fontsize=10)
    changes=[float(mean[-1]-mean[0]) for _,_,_,mean in stats]
    metrics["sector_endpoint_change_C"]=dict(zip([x[0] for x in stats],changes))
    finish(fig,18,"daily_temperature_ribbons","Daily spatial quantile ribbons",f"All 92 days contribute. Fixed-footprint sector means and spatial quantiles use cosine-latitude weights. Sectors are analyst-defined longitude bands, not official climate regions. September 30 minus July 1 sector-mean differences are {changes[0]:.2f} °C west, {changes[1]:.2f} °C central, and {changes[2]:.2f} °C east. The ribbon is the within-sector spatial 10th-90th percentile range, not an uncertainty interval; reversals during the interval remain visible.")

    # 19: all-day monthly maximum-temperature means, with fixed threshold isolines.
    monthly_t=[]
    for m in month_masks:
        counts=np.isfinite(t[m]).sum(axis=0)
        monthly_t.append(np.divide(np.nansum(t[m],axis=0),counts,out=np.full(common.shape,np.nan),where=counts>0))
    monthly_t=np.array(monthly_t)
    limits=(float(np.nanmin(monthly_t)),float(np.nanmax(monthly_t)))
    fig,axes=plt.subplots(1,3,figsize=(18,6),constrained_layout=True)
    fig.suptitle("Monthly mean of DAILY MAXIMUM temperature | All days included",fontsize=18)
    for ax,a,month in zip(axes,monthly_t,[7,8,9]):
        im=ax.pcolormesh(lon,lat,a,cmap="viridis",norm=Normalize(*limits),shading="auto",rasterized=True)
        lines=ax.contour(lon,lat,a,levels=[25,35],colors="white",linewidths=.8)
        ax.clabel(lines,fmt="%g°C",fontsize=8)
        map_axis(ax,f"{calendar.month_name[month]} | {calendar.monthrange(2023,month)[1]} daily fields")
    fig.colorbar(im,ax=axes,shrink=.75,label="Mean of daily maximum temperature (°C)")
    means=[float(np.average(a[common],weights=weights[common])) for a in monthly_t]
    metrics["monthly_area_mean_tmax_C"]=means
    finish(fig,19,"monthly_tmax_maps","Monthly means with fixed isolines",f"Monthwise means include 31, 31 and 30 daily maximum-temperature fields. The common scalar scale spans {limits[0]:.2f} to {limits[1]:.2f} °C; white isolines are fixed at 25 and 35 °C. Approximate area-weighted means over the valid footprint are {means[0]:.2f}, {means[1]:.2f} and {means[2]:.2f} °C. These are means of daily maxima, not monthly mean air temperature or climate anomalies.")

    # 20: monthly rain totals require all days, with strict complete-month masking.
    monthly_p=np.array([np.where(np.all(np.isfinite(p[m]),axis=0),np.nansum(p[m],axis=0),np.nan) for m in month_masks])
    max_rain=float(np.nanmax(monthly_p))
    fig,axes=plt.subplots(1,3,figsize=(18,6),constrained_layout=True)
    fig.suptitle("Monthly precipitation accumulation | Sum every daily field",fontsize=18)
    for ax,a,month in zip(axes,monthly_p,[7,8,9]):
        im=ax.pcolormesh(lon,lat,a,cmap="Blues",norm=Normalize(0,max_rain),shading="auto",rasterized=True)
        map_axis(ax,calendar.month_name[month])
    fig.colorbar(im,ax=axes,shrink=.75,label="Monthly precipitation total (mm)")
    pmeans=[float(np.average(a[np.isfinite(a)],weights=weights[np.isfinite(a)])) for a in monthly_p]
    metrics["monthly_area_mean_precip_mm"]=pmeans
    finish(fig,20,"monthly_precipitation_maps","Complete-month precipitation totals",f"At each sampled location, all 31 July, 31 August or 30 September daily accumulations are summed. Any incomplete month is masked, rather than treating missing days as zero. Approximate area-weighted monthly totals are {pmeans[0]:.2f}, {pmeans[1]:.2f} and {pmeans[2]:.2f} mm. The shared scale is 0-{max_rain:.2f} mm without clipping. These totals were computed from the 92-day cache, not estimated from eight display samples; this short interval does not establish a climate trend.")

    # 21: monthwise frequency with denominators shown explicitly.
    threshold=35
    freq=np.array([np.where(common,100*np.mean(t[m]>=threshold,axis=0),np.nan) for m in month_masks])
    fig,axes=plt.subplots(1,3,figsize=(18,6),constrained_layout=True)
    fig.suptitle("Where are days with Tmax >= 35°C frequent?",fontsize=18)
    for ax,a,month,mask in zip(axes,freq,[7,8,9],month_masks):
        im=ax.pcolormesh(lon,lat,a,cmap="magma",norm=Normalize(0,100),shading="auto",rasterized=True)
        map_axis(ax,f"{calendar.month_name[month]} | denominator {int(mask.sum())} days")
    fig.colorbar(im,ax=axes,shrink=.75,label="Days with Tmax >= 35°C (%)")
    fmeans=[float(np.average(a[common],weights=weights[common])) for a in freq]
    metrics["monthly_area_day_tmax_ge35_percent"]=fmeans
    finish(fig,21,"hot_day_frequency_maps","Threshold-frequency maps",f"Each cell's count of days at or above 35 °C is divided by its month's 31, 31 or 30 days. The common 0-100% scale permits comparison despite unequal month lengths. Approximate area-day fractions are {fmeans[0]:.1f}%, {fmeans[1]:.1f}% and {fmeans[2]:.1f}%. The 35 °C cutoff is an explicit descriptive choice, not an official heatwave definition, health-risk index, or population exposure estimate.")

    # 22: daily horizon variation, preserving signed baseline semantics.
    fig,axes=plt.subplots(3,1,figsize=(14,5),sharex=True,constrained_layout=True)
    fig.suptitle("Daily horizon plots | Sector mean Tmax minus 30°C",fontsize=18)
    for ax,(label,mask,q,mean) in zip(axes,stats):
        dev=mean-30
        for band in range(4):
            for sign,palette in [(1,["#adcfe4","#73abd0","#397eb0","#145583"]),(-1,["#f6c2bc","#e48d82","#c95448","#8e302c"])]:
                level=np.clip(sign*dev-band*5,0,5)/5
                ax.fill_between(time,0,level,color=palette[band],lw=0)
        ax.set_ylim(0,1.02);ax.set_yticks([]);ax.set_title(label,loc="left",fontsize=10)
        ax.grid(axis="x",alpha=.15)
    fig.supxlabel("5°C folded bands: increasing saturation = farther from 30°C | Blue above; red below | Red does not mean falling",fontsize=10)
    finish(fig,22,"daily_weather_horizons","Daily weather horizon variation","The same area-weighted daily sector means from Fig. 18 are centered on a declared 30 °C baseline and folded into four 5 °C bands per side. Blue denotes above the baseline and red below; saturation encodes distance from it. This daily weather variation complements the annual country-adoption horizon plots without inventing monthly country observations. Refer to the unfurled ribbon plot for exact values.")

    # 23: conditional positive-precipitation distributions, dry fraction separate.
    fig,ax=plt.subplots(figsize=(12,6),constrained_layout=True)
    dryfractions=[]
    for mask,month,color in zip(month_masks,[7,8,9],COLORS):
        vals=p[mask];vals=vals[np.isfinite(vals)]
        dry=float(np.mean(vals==0)*100);dryfractions.append(dry)
        positive=vals[vals>0]
        unique,counts=np.unique(positive,return_counts=True)
        ax.step(unique,np.cumsum(counts)/len(positive),where="post",color=color,lw=2,label=f"{calendar.month_name[month]} | dry {dry:.1f}%")
    ax.set_xscale("log");ax.set_ylim(0,1.01);ax.set(xlabel="Positive daily precipitation (mm; logarithmic axis)",ylabel="Fraction of positive grid-day values <= x",title="Rainfall ECDFs: distribution without smoothing")
    ax.legend(loc="lower right");ax.grid(alpha=.2)
    fig.supxlabel("Equal weighting of valid grid-day values | ECDF conditional on positive rain; dry values excluded and reported in legend",fontsize=9)
    metrics["monthly_dry_grid_day_percent"]=dryfractions
    finish(fig,23,"precipitation_ecdf","Conditional rainfall ECDFs",f"Empirical cumulative distributions use all positive daily grid-cell rain values in each month, with no kernel smoothing. Dry grid-day fractions are {dryfractions[0]:.1f}%, {dryfractions[1]:.1f}% and {dryfractions[2]:.1f}%. Conditioning on positive rain prevents zero from invalidating the log axis; the dry fractions retain that excluded information. Grid-day observations are equally weighted and spatially dependent, so these curves are descriptive rather than independent-sample inferential tests.")

    # 24: source/from-direction roses, with area-weighted frequencies.
    west=(X>=-125)&(X<=-100)&(lat[:,None]>=30)&(lat[:,None]<=49)
    histograms=[];calms=[]
    for mask in month_masks:
        sp,dr=s[mask],d[mask]
        ww=np.broadcast_to(weights,sp.shape)
        valid=np.broadcast_to(west,sp.shape)&np.isfinite(sp)&np.isfinite(dr)
        noncalm=valid&(sp>.1)
        calms.append(float(100*ww[valid&(sp<=.1)].sum()/ww[valid].sum()))
        direction=(dr[noncalm]+11.25)%360
        counts,_,_=np.histogram2d(direction,sp[noncalm],bins=[np.arange(0,361,22.5),[.1,2,4,6,np.inf]],weights=ww[noncalm])
        histograms.append(100*counts/ww[noncalm].sum())
    rosemax=float(np.ceil(max(h.sum(axis=1).max() for h in histograms)/5)*5)
    fig,axes=plt.subplots(1,3,subplot_kw={"projection":"polar"},figsize=(16,6),constrained_layout=True)
    fig.suptitle("Western-US wind roses | Meteorological FROM direction",fontsize=18)
    fig.get_layout_engine().set(rect=(0,.09,1,.91))
    colors=["#c8dbe6","#80b4d1","#3e88b5","#155787"]
    theta=np.deg2rad(np.arange(0,360,22.5))
    for ax,h,month,calm in zip(axes,histograms,[7,8,9],calms):
        bottom=np.zeros(16)
        for j,color in enumerate(colors):
            ax.bar(theta,h[:,j],width=np.deg2rad(20),bottom=bottom,color=color,edgecolor="white",lw=.3)
            bottom+=h[:,j]
        ax.set_theta_zero_location("N");ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0,360,45),["N","NE","E","SE","S","SW","W","NW"])
        ax.set_ylim(0,rosemax);ax.set_rlabel_position(110)
        ax.set_title(f"{calendar.month_name[month]} | calm {calm:.2f}%",pad=18)
        ax.set_yticks(np.arange(5,rosemax+1,5),[f"{n}%" for n in np.arange(5,rosemax+1,5)])
    fig.legend(handles=[Patch(facecolor=c,label=l) for c,l in zip(colors,["0.1-<2 m/s","2-<4 m/s","4-<6 m/s",">=6 m/s"])],loc="lower center",ncol=4,frameon=False)
    metrics["wind_rose_calm_area_day_percent"]=calms
    finish(fig,24,"monthly_wind_roses","Monthly wind-direction roses","Sixteen direction bins aggregate all daily source wind-direction values in the western box (-125 to -100 longitude, 30 to 49 latitude). Sector radial height gives approximate area-day frequency among noncalm valid grid-day summaries; stacked color encodes speed class. All months share a radial limit. Calm/near-calm speeds at or below 0.1 m/s are excluded and reported separately. These are meteorological from-directions, whereas the original quiver arrows show flow-to directions. They do not count hourly winds or independent station measurements.")

    # 25: same edges, alternate encoding. Region ordering is explicit, not clustering.
    network=json.loads((ROOT/"data/country_network_2020.json").read_text())
    nodes=sorted(network["nodes"],key=lambda n:(n["region"],n["country"]))
    order={n["id"]:i for i,n in enumerate(nodes)}
    matrix=np.zeros((len(nodes),len(nodes)),dtype=np.uint8)
    inside=0
    lookup={n["id"]:n for n in nodes}
    for edge in network["edges"]:
        a,b=order[edge["source"]],order[edge["target"]]
        matrix[a,b]=matrix[b,a]=1
        inside+=lookup[edge["source"]]["region"]==lookup[edge["target"]]["region"]
    assert matrix.sum()==2*len(network["edges"])
    pd.DataFrame([{ "row_column":i,"code":n["id"],"country":n["country"],"region":n["region"]} for i,n in enumerate(nodes)]).to_csv(ROOT/"data/network_matrix_order.csv",index=False)
    fig,ax=plt.subplots(figsize=(11,10),constrained_layout=True)
    fig.get_layout_engine().set(rect=(0,.06,1,.94))
    ax.imshow(matrix,cmap=ListedColormap(["#f5f7fa","#195d8d"]),vmin=0,vmax=1,interpolation="nearest")
    labels=[];centers=[];starts=[]
    for region in sorted(set(n["region"] for n in nodes)):
        ix=[i for i,n in enumerate(nodes) if n["region"]==region]
        centers.append((ix[0]+ix[-1])/2);labels.append(region.replace(" ","\n"));starts.append(ix[0]-.5)
    for line in starts[1:]:
        ax.axhline(line,color="#b3c0ce",lw=.8);ax.axvline(line,color="#b3c0ce",lw=.8)
    ax.set_xticks(centers,labels);ax.set_yticks(centers,[x.replace("\n"," ") for x in labels])
    plt.setp(ax.get_xticklabels(),rotation=60,ha="right",fontsize=8)
    ax.set_title(f"Threshold graph as an adjacency matrix\n179 countries | {len(network['edges'])} edges | Region then alphabetic ordering",fontsize=16)
    ax.set_xlabel("Country columns (exact order saved in CSV)");ax.set_ylabel("Country rows (same order)")
    fig.legend(handles=[Patch(facecolor="#195d8d",label="Similarity edge"),Patch(facecolor="#f5f7fa",edgecolor="#b3c0ce",label="No edge")],loc="lower center",ncol=2,frameon=False)
    metrics["network_within_supplied_region_edges"]=inside
    edge_count=len(network['edges'])
    finish(fig,25,"network_adjacency_matrix","Region-ordered adjacency matrix",f"The matrix contains the same 179 nodes and {edge_count} undirected thresholded similarity edges as the three required layouts. Each edge appears twice by symmetry; the diagonal is empty. Ordering by supplied region and then country alphabetically reveals {inside} within-region edges ({100*inside/edge_count:.1f}% of edges) without discovering new communities. Exact row/column order is supplied in data/network_matrix_order.csv. A matrix permits edge verification but does not replace the required interactive node-link layouts; no synchronized interaction is claimed.")

    # 26: matched-country medians preserve regional membership across both years.
    profiles=pd.read_json(ROOT/"data/infovis_countries.json")
    ids=set(profiles.loc[profiles.year==2015,"code"])&set(profiles.loc[profiles.year==2020,"code"])
    assert len(ids)==175
    pair=profiles[profiles.code.isin(ids)]
    pivot=pair.groupby(["region","year"]).internet_users_share_pct.median().unstack()
    counts=pair[pair.year==2020].groupby("region").size()
    pivot=pivot.sort_values(2020)
    fig,ax=plt.subplots(figsize=(12,6),constrained_layout=True)
    y=np.arange(len(pivot))
    ax.hlines(y,pivot[2015],pivot[2020],color="#aebdca",lw=3)
    ax.scatter(pivot[2015],y,s=70,color=COLORS[0],label="2015",zorder=3)
    ax.scatter(pivot[2020],y,s=70,color=COLORS[1],label="2020",zorder=3)
    for i,(region,row) in enumerate(pivot.iterrows()):
        ax.text(max(row)+2,i,f"{row[2020]-row[2015]:+.1f} pp",va="center",fontsize=9)
    ax.set_yticks(y,[f"{r} (n={counts[r]})" for r in pivot.index])
    ax.set_xlim(0,110);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel("Regional median internet adoption (%)")
    ax.set_title("Matched-country adoption shifts | Same 175 countries in both years",fontsize=17)
    ax.legend(loc="lower right");ax.grid(axis="x",alpha=.2)
    classified=pivot.drop(index="Unclassified",errors="ignore")
    largest=(classified[2020]-classified[2015]).idxmax()
    metrics["matched_region_medians"]=pivot.reset_index().to_dict(orient="records")
    finish(fig,26,"matched_adoption_dumbbells","Matched-panel regional dumbbells",f"Regional medians use the exact 175-country panel that has complete profiles in both 2015 and 2020. Each included country has equal weight and regional memberships are fixed; counts are shown beside each region, including Unclassified. Among classified regions, the largest median shift is {largest}, {float(pivot.loc[largest,2020]-pivot.loc[largest,2015]):.2f} percentage points. Unclassified is a missing-label category, not a geographic region. This is the difference of two regional medians, not the median of individual changes, a population-weighted result, or causal evidence.")

    # 27: derive a horizon plot from an actual country series step by step.
    panel=pd.read_csv(ROOT/"data/internet_panel_2000_2020.csv")
    kenya=panel[panel.code=="KEN"].sort_values("year")
    assert len(kenya)==21
    years=kenya.year.to_numpy();values=kenya.internet_users_share_pct.to_numpy();dev=values-50
    fig,axes=plt.subplots(3,1,figsize=(13,8),sharex=True,constrained_layout=True)
    fig.suptitle("Horizon construction from real data | Kenya, 2000-2020",fontsize=18)
    axes[0].plot(years,values,color="#195d8d",lw=2);axes[0].axhline(50,color="#526579",ls="--")
    axes[0].set_ylim(0,100);axes[0].set_ylabel("Adoption (%)");axes[0].set_title("1. Original values and the 50% majority-use reference",loc="left")
    axes[1].plot(years,dev,color="#526579",lw=1)
    axes[1].fill_between(years,0,dev,where=dev>=0,color="#adcfe4",interpolate=True)
    axes[1].fill_between(years,0,dev,where=dev<0,color="#eaa49c",interpolate=True)
    axes[1].axhline(0,color="#526579",lw=.6);axes[1].set_ylim(-50,50);axes[1].set_ylabel("Difference (pp)")
    axes[1].set_title("2. Subtract 50 percentage points; retain the sign",loc="left")
    for band in range(2):
        for sign,colors in [(1,["#adcfe4","#2877b2"]),(-1,["#f3aaa5","#bd4c43"])]:
            axes[2].fill_between(years,0,np.clip(sign*dev-band*25,0,25)/25,color=colors[band],lw=0)
    axes[2].set_ylim(0,1.05);axes[2].set_yticks([]);axes[2].set_xlabel("Year")
    axes[2].set_title("3. Mirror and fold two 25-point bands into one row; color retains sign",loc="left")
    for ax in axes:ax.grid(axis="x",alpha=.15)
    finish(fig,27,"horizon_construction","Worked horizon construction",f"Kenya's actual fixed-panel series moves from {values[0]:.2f}% adoption in 2000 to {values[-1]:.2f}% in 2020. The three panels show measured values, signed deviation from 50%, and the same deviation mirrored and folded into two 25-point bands. Red indicates below majority use, even when adoption rises. The method explanation follows the September 29 lecture's construction stages; it does not use fabricated example values.")

    # 28: sensitivity of the actual KDE, with an empirical reference.
    vals=panel.loc[panel.year==2020,"internet_users_share_pct"].to_numpy()
    assert len(vals)==159
    grid=np.linspace(0,100,401)
    fig,axes=plt.subplots(1,2,figsize=(15,6),constrained_layout=True)
    for bw,color in zip([3,6,12],COLORS):
        dens=reflected_kde(vals,grid,bw)
        axes[0].plot(grid,dens,color=color,lw=2,label=f"Bandwidth {bw} pp")
    axes[0].set(xlim=(0,100),xlabel="Internet adoption (%)",ylabel="Probability density per percentage point",title="Boundary-reflected KDE: smoothing sensitivity")
    axes[0].legend();axes[0].grid(alpha=.2)
    unique,counts=np.unique(vals,return_counts=True)
    axes[1].step(unique,np.cumsum(counts)/len(vals),where="post",color="#195d8d",lw=2)
    med=float(np.median(vals));axes[1].axvline(med,color=COLORS[1],ls="--",label=f"Raw median {med:.2f}%")
    axes[1].set(xlim=(0,100),ylim=(0,1),xlabel="Internet adoption (%)",ylabel="Fraction of countries <= x",title="ECDF: no bandwidth choice")
    axes[1].legend();axes[1].grid(alpha=.2)
    fig.suptitle("Is a ridgeline bump robust? | Same 159 countries, 2020",fontsize=18)
    finish(fig,28,"kde_bandwidth_sensitivity","KDE sensitivity with empirical reference",f"The same 159-country 2020 adoption values are smoothed with reflected Gaussian bandwidths 3, 6 and 12 percentage points. The left axis retains true density units; curves are not independently normalized to peak height. The empirical cumulative distribution at right does not depend on smoothing, and the raw median remains {med:.2f}%. Minor density peaks should not be interpreted as stable groups merely because one bandwidth makes them visible.")

    assert [c["figure"] for c in captions]==list(range(17,29))
    metrics["validation"]="PASS: all 92 dates, physical ranges, fixed temperature footprint, 31/31/30 denominators, symmetric matrix entries checked against current edge count, 175 matched countries, 21 Kenya years, 159 KDE observations and 12 unique added figure indices"
    (ROOT/"data/extended_findings.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    (ROOT/"data/extended_figure_manifest.json").write_text(json.dumps(captions,indent=2),encoding="utf-8")
    if (ROOT/'data/current_figure_manifest.json').exists():
        print('Rebuilt original extension assets. Run integrate_quality_report.py to compose the revised report.')
        return
    sections=[]
    for group,title in [(captions[:8],"Extended weather analysis: all 92 days"),(captions[8:],"Extended Infovis analysis and method checks")]:
        block=f"## {title}\n\n"
        if group[0]["figure"]==17:
            block+="The eight-frame animations are display samples, not the dataset's temporal resolution. All four 2023 NetCDF time axes and all 92 daily fields have now been audited. Complete monthly averages, totals and frequencies below use every day at the same six-cell spatial stride. Spatially subsampled fields are not native-resolution spatial averages.\n\n"
        for c in group:
            block+=f'![Figure {c["figure"]}. {c["title"]}.]({c["path"]})\n\n**Figure {c["figure"]}.** {c["caption"]}\n\n'
        sections.append(block)
    reportpath=ROOT/"REPORT.md"
    report=reportpath.read_text(encoding="utf-8")
    start=report.find("## Extended weather analysis")
    if start>=0:
        end=report.index("## Reproducibility",start);report=report[:start]+report[end:]
    pos=report.index("## Reproducibility")
    report=report[:pos]+"\n".join(sections)+report[pos:]
    report=report.replace("4 October 2026","5 October 2026")
    report=report.replace("Eight temporal samples omit intervening events; climate-trend and seasonal-total claims are not supported.","The original eight-frame animations omit intervening events. The extensions use all 92 daily fields for monthly summaries; no climate-trend claim is supported by this one three-month interval.")
    reportpath.write_text(report,encoding="utf-8")
    allfigures=re.findall(r"!\[Figure (\d+)\. ([^\]]+)\]\(([^)]+)\)\n\n\*\*Figure \d+\.\*\* ([^\n]+)",report)
    assert [int(n) for n,_,_,_ in allfigures]==list(range(1,29))
    gallery=ROOT/"output/all_28_figures/index.html";gallery.parent.mkdir(parents=True,exist_ok=True)
    cards=""
    for n,title,path,caption in allfigures:
        cards+=f'<article id="fig{n}"><h2>Figure {n}. {html.escape(title)}</h2><a href="../../{path}"><img loading="lazy" src="../../{path}" alt="{html.escape(title)}"></a><p>{html.escape(caption)}</p></article>'
    toc=" · ".join(f'<a href="#fig{n}">{n}</a>' for n in range(1,29))
    page=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Assignment 2 | 28 figures</title><style>body{{font:17px/1.6 system-ui;color:#193044;background:#edf2f6;margin:0}}main{{max-width:1200px;margin:auto;padding:28px}}header,article{{background:white;padding:28px;margin:24px 0;border-radius:10px}}img{{width:100%;height:auto}}a{{color:#176e9d}}h1,h2{{line-height:1.2}}@media(max-width:600px){{main{{padding:8px}}article,header{{padding:14px}}}}</style><main><header><h1>Assignment 2: all 28 figures</h1><p>July-September 2023 contains 92 daily dates. Eight selected samples remain in the required animations; full daily coverage supports the new monthly summaries.</p><nav>{toc}</nav><p><a href="../pdf/DAS732_A2_Report_IEEE.pdf">IEEE report</a> · <a href="../../research/EXPANSION_28_PLAN.md">Research plan</a> · <a href="../../data/scivis/daily_manifest.json">Daily coverage evidence</a></p></header>{cards}</main></html>'
    gallery.write_text(page,encoding="utf-8")
    print(json.dumps(metrics,indent=2))
    print(f"Added twelve figures; all-figure gallery: {gallery}")


if __name__=="__main__":
    main()
