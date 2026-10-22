from pathlib import Path
import textwrap
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from vizlib import PALETTE, style_defaults, save_fig

ROOT = Path(__file__).resolve().parent
DATA = ROOT
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
style_defaults()

def export(fig, name, note):
    save_fig(fig, OUT / name, note)
    plt.close(fig)

def case1():
    df = pd.read_csv(DATA/"case01_orders_stringdate.csv")
    # Published recipe: lexicographic sort on non-zero-padded YYYY-M text.
    bad = df.sort_values("month")
    fig, ax = plt.subplots(figsize=(9,4))
    ax.plot(bad.month, bad.orders, marker="o", color=PALETTE["series"][0])
    ax.set_ylim(bottom=0); ax.tick_params(axis="x", rotation=65)
    ax.set(title="Published claim: orders peak and collapse every year", ylabel="Orders per month", xlabel="Month string (lexicographic order)")
    export(fig,"case01_original.png","Source: synthetic CDB601220 Week 4 course data; n=24 monthly rows.")
    good=df.assign(month_dt=pd.to_datetime(df.month,format="%Y-%m")).sort_values("month_dt")
    fig,ax=plt.subplots(figsize=(9,4))
    ax.plot(good.month_dt,good.orders,marker="o",color=PALETTE["series"][0])
    ax.set_ylim(bottom=0); ax.set(title="Correct calendar order: orders rise across both years",ylabel="Orders per month",xlabel="Calendar month")
    export(fig,"case01_redesign.png","Source: synthetic CDB601220 Week 4 course data; YYYY-M parsed as year-month.")
    bad_drops=np.diff(bad.orders); return f"Mechanism: `YYYY-M` is non-zero-padded text, so lexical sorting orders month 10/11/12 before month 2. The false drops are {abs(int(bad_drops[bad_drops<0][0])):,} and {abs(int(bad_drops[bad_drops<0][1])):,} orders; parsing to datetime restores chronological order. First objection ‘seasonality is not proven’ is incomplete: the specific visible collapses are manufactured by string sorting, not annual cycles."

def case2():
    df=pd.read_csv(DATA/"case02_shop_closed.csv")
    dates=pd.to_datetime(df.date)
    full=pd.date_range(dates.min(),dates.max(),freq="D")
    # Original row number + trend line
    x=np.arange(len(df)); y=df.sales_pkr_k.to_numpy(); slope,intercept=np.polyfit(x,y,1)
    fig,ax=plt.subplots(figsize=(9,4))
    ax.plot(x,y,color=PALETTE["series"][0],alpha=.8,label="Trading-day sales")
    ax.plot(x,slope*x+intercept,color=PALETTE["highlight"],label="Least-squares trend")
    ax.set(title="Published claim: sales rose 22% across the quarter",xlabel="Row number (not elapsed time)",ylabel="Sales (PKR thousands)"); ax.legend()
    export(fig,"case02_original.png","Source: synthetic CDB601220 Week 4 course data; n=69 trading-day rows.")
    # Redesign actual date axis, show only trading days; mark closure gaps through date axis.
    fig,ax=plt.subplots(figsize=(9,4))
    ax.plot(dates,y,marker=".",ms=4,color=PALETTE["series"][0],label="Observed trading days")
    # date-based regression is descriptive only
    xd=(dates-dates.min()).dt.days.to_numpy(); sl,ic=np.polyfit(xd,y,1)
    ax.plot(dates,sl*xd+ic,color=PALETTE["highlight"],label="Trend vs calendar days")
    ax.set(title="Sales are observed on trading days only; calendar gaps matter",xlabel="Calendar date (closed days omitted from records)",ylabel="Sales (PKR thousands)"); ax.legend()
    export(fig,"case02_redesign.png","Source: synthetic CDB601220 Week 4 course data; n=69 observed trading days; line connects observations across closed days.")
    gaps=len(full.difference(dates))
    return f"Mechanism: row number treats 69 trading observations as equally spaced despite {gaps} missing calendar dates (90 calendar days in span). The 207→253 endpoint rise is +22.2%, but it is not evidence of steady daily growth across elapsed time; sales fluctuate and the row index conceals closures. The decoy ‘sample too small’ is not supported: n=69 is the stated dataset; the problem is the x-coordinate and missing non-trading dates."

def case3():
    df=pd.read_csv(DATA/"case03_bandwidth_levels.csv"); df.ts=pd.to_datetime(df.ts)
    df=df.sort_values("ts").set_index("ts")
    # Published sum level
    daily_sum=df.concurrent_users.resample("D").sum()
    fig,ax=plt.subplots(figsize=(9,4)); daily_sum.plot(ax=ax,color=PALETTE["series"][0],marker="o")
    ax.set_ylim(bottom=0); ax.set(title="Published claim: concurrent-user load jumped 43% on 1 July",xlabel="Day",ylabel="Sum of hourly concurrent-user levels (users·hours, not users)")
    export(fig,"case03_original.png","Source: synthetic CDB601220 Week 4 course data; 1,237 hourly rows.")
    daily_mean=df.concurrent_users.resample("D").mean()
    fig,ax=plt.subplots(figsize=(9,4)); daily_mean.plot(ax=ax,color=PALETTE["series"][0],marker=".",label="Daily mean concurrent users")
    ax.set(title="Concurrent users are a level: compare daily mean, not sum",xlabel="Day",ylabel="Mean concurrent users (users)"); ax.legend()
    export(fig,"case03_redesign.png","Source: synthetic CDB601220 Week 4 course data; missing hours retained as gaps in the daily mean.")
    june=daily_mean.loc["2025-06"].mean(); july=daily_mean.loc["2025-07"].mean()
    return f"Mechanism: `concurrent_users` is an instantaneous level, not a flow. Summing it makes the result depend on hours recorded per day. The index has {df.index.duplicated().sum()} duplicate timestamps and {len(pd.date_range(df.index.min(),df.index.max(),freq='h').difference(df.index))} missing hourly timestamps; therefore coverage also varies. Correct daily means by month are {june:.1f} in June and {july:.1f} in July ({(july/june-1)*100:+.1f}%), not a justified 43% level jump. The decoy ‘July has more users because sum is larger’ confuses a level with an accumulated flow."

def case4():
    df=pd.read_csv(DATA/"case04_intervention_lag.csv"); df.date=pd.to_datetime(df.date); s=df.set_index("date").conversion_pct
    trail=s.rolling(31).mean(); centered=s.rolling(31,center=True).mean()
    fig,ax=plt.subplots(figsize=(9,4)); ax.plot(s.index,s,color="#9AA7B4",lw=1,label="Raw daily conversion")
    ax.plot(trail.index,trail,color=PALETTE["highlight"],lw=2.5,label="31-day trailing mean")
    ax.axvline(trail.idxmin(),color=PALETTE["highlight"],ls="--",alpha=.7)
    ax.set(title="Published claim: checkout intervention worked on 7 September",xlabel="Date",ylabel="Conversion (%)"); ax.legend()
    export(fig,"case04_original.png","Source: synthetic CDB601220 Week 4 course data; 214 daily rows.")
    fig,ax=plt.subplots(figsize=(9,4)); ax.plot(s.index,s,color="#9AA7B4",lw=1,label="Raw daily conversion")
    ax.plot(centered.index,centered,color=PALETTE["series"][0],lw=2.5,label="31-day centred mean")
    ax.axvline(centered.idxmin(),color=PALETTE["series"][0],ls="--",alpha=.7)
    ax.set(title="A centred 31-day mean locates the trough earlier; smoothing is not causality",xlabel="Date",ylabel="Conversion (%)"); ax.legend()
    export(fig,"case04_redesign.png","Source: synthetic CDB601220 Week 4 course data; centred mean is retrospective and uses future observations.")
    return f"Mechanism: a 31-day trailing mean lags a turn because it only includes the current and previous 30 days. Trailing minimum is {trail.idxmin().date()}, while centred-window minimum is {centered.idxmin().date()}, a {(trail.idxmin()-centered.idxmin()).days}-day difference. This is a window-induced lag, not proof that the intervention began working on the smoothed minimum date. The raw series and a centred view show timing uncertainty; causal attribution needs a counterfactual."

def case5():
    df=pd.read_csv(DATA/"case05_revenue_window.csv"); df.month=pd.to_datetime(df.month)
    sub=df[(df.month>="2025-05-01")&(df.month<="2025-11-01")]
    fig,ax=plt.subplots(figsize=(8,4)); ax.plot(sub.month,sub.revenue_pkr_m,marker="o",color=PALETTE["series"][0])
    ax.set_ylim(bottom=0); ax.set(title="Published claim: revenue fell 41.9% in seven selected months",xlabel="Month",ylabel="Revenue (PKR millions)")
    export(fig,"case05_original.png","Source: synthetic CDB601220 Week 4 course data; selected May–November 2025 window, n=7.")
    fig,ax=plt.subplots(figsize=(9,4)); ax.plot(df.month,df.revenue_pkr_m,marker="o",ms=4,color=PALETTE["series"][0])
    ax.axvspan(pd.Timestamp("2025-05-01"),pd.Timestamp("2025-11-30"),color=PALETTE["highlight"],alpha=.10,label="Published window")
    ax.set_ylim(bottom=0); ax.set(title="Full 36-month context: the selected decline follows earlier growth",xlabel="Month",ylabel="Revenue (PKR millions)"); ax.legend()
    export(fig,"case05_redesign.png","Source: synthetic CDB601220 Week 4 course data; complete monthly series, n=36.")
    return f"Mechanism: selective time-window framing omits 29 of 36 months. May–November 2025 declines from {sub.revenue_pkr_m.iloc[0]:.1f} to {sub.revenue_pkr_m.iloc[-1]:.1f} PKR m ({(sub.revenue_pkr_m.iloc[-1]/sub.revenue_pkr_m.iloc[0]-1)*100:.1f}%), but the full series shows the context and a December recovery to {df.revenue_pkr_m.iloc[-1]:.1f}. The y-axis is already zero-based and n=7 matches the requested window; neither is the mechanism. The missing context, not axis truncation, makes the claim overbroad."

def case6():
    df=pd.read_csv(DATA/"case06_monthly_partial.csv"); df.date=pd.to_datetime(df.date); s=df.set_index("date").orders
    totals=s.resample("MS").sum(); counts=s.resample("MS").count()
    fig,ax=plt.subplots(figsize=(9,4)); totals.plot.bar(ax=ax,color=PALETTE["series"][0])
    ax.set(title="Published claim: orders collapsed in October",xlabel="Month",ylabel="Observed orders (monthly sum)"); ax.tick_params(axis="x",rotation=45)
    export(fig,"case06_original.png","Source: synthetic CDB601220 Week 4 course data; October contains only observed dates.")
    fullidx=pd.date_range(s.index.min().to_period("M").to_timestamp(),s.index.max().to_period("M").to_timestamp(),freq="MS")
    full=totals.reindex(fullidx); full.index=full.index.strftime("%Y-%m")
    fig,ax=plt.subplots(figsize=(9,4)); bars=ax.bar(full.index,full.values,color=[PALETTE["series"][0] if k!="2025-10" else PALETTE["highlight"] for k in full.index],alpha=.75)
    for i,k in enumerate(full.index):
        if k=="2025-10": ax.text(i,full.iloc[i],f"Partial: {int(counts.loc['2025-10-01'])}/31 days",ha="center",va="bottom",fontsize=8,rotation=0)
    ax.set(title="October is partial: only 11 of 31 days are recorded",xlabel="Month",ylabel="Observed orders (sum; incomplete month flagged)"); ax.tick_params(axis="x",rotation=45)
    export(fig,"case06_redesign.png","Source: synthetic CDB601220 Week 4 course data; October 2025 is partial, no imputation.")
    sept=totals.loc["2025-09-01"]; octv=totals.loc["2025-10-01"]; n_oct=int(counts.loc["2025-10-01"])
    return f"Mechanism: October is a partial month. Only {n_oct} of 31 calendar days are present; the observed sum {octv:,.0f} is not comparable with September's full-month {sept:,.0f}. A per-day observed rate is {octv/n_oct:.1f} orders/day in October versus {sept/int(counts.loc['2025-09-01']):.1f} in September. Do not project the rate as a full-month total without stating an assumption. The chart is arithmetically correct; its denominator/exposure period differs."

def case7():
    df=pd.read_csv(DATA/"case07_stacked_products.csv"); df.month=pd.to_datetime(df.month)
    cols=["product_a","product_b","product_c","product_d"]
    fig,ax=plt.subplots(figsize=(9,4)); ax.stackplot(df.month,*[df[c] for c in cols],labels=cols,alpha=.85)
    ax.set(title="Published claim: Product D is erratic in a stacked area chart",xlabel="Month",ylabel="Revenue (PKR millions)"); ax.legend(ncol=4,loc="upper left")
    export(fig,"case07_original.png","Source: synthetic CDB601220 Week 4 course data; four exclusive product lines.")
    fig,ax=plt.subplots(figsize=(9,4))
    for i,c in enumerate(cols):
        ax.plot(df.month,df[c],label=c,color=(PALETTE["series"][i] if i<3 else PALETTE["series_4th"]),marker=".",ms=3)
    ax.set(title="Unstacked series reveal Product D is comparatively stable",xlabel="Month",ylabel="Revenue (PKR millions)"); ax.legend(ncol=4)
    export(fig,"case07_redesign.png","Source: synthetic CDB601220 Week 4 course data; product lines shown separately.")
    d=df.product_d
    return f"Mechanism: stacking makes the top boundary of Product D equal to the cumulative total A+B+C+D; its visible top edge inherits movement from all four products. Product D itself ranges only {d.min():.1f}–{d.max():.1f} PKR m (SD {d.std():.2f}), while the total envelope ranges {df[cols].sum(axis=1).min():.1f}–{df[cols].sum(axis=1).max():.1f}. The decoy ‘stacked area is illegal’ is wrong: the dictionary says product lines are exclusive and exhaustive. The problem is reading the top boundary as D's own series."

def case8():
    df=pd.read_csv(DATA/"case08_channel_attrib.csv"); cols=[c for c in df.columns if c.startswith("touch_")]
    pct=df[cols].sum()/len(df)*100
    fig,ax=plt.subplots(figsize=(6,5)); ax.pie(pct.values,labels=[c.replace("touch_","").title() for c in cols],autopct="%1.1f%%",startangle=90)
    ax.set_title("Published claim: paid search drives 43% of customers")
    export(fig,"case08_original.png","Source: synthetic CDB601220 Week 4 course data; n=4,000 customers; touch flags may overlap.")
    fig,ax=plt.subplots(figsize=(8,4)); vals=pct.sort_values()
    ax.barh([x.replace("touch_","").title() for x in vals.index],vals.values,color=PALETTE["series"][0])
    ax.set(title="Channel touch rates overlap; these are not parts of one whole",xlabel="Customers touched (%) — categories overlap",ylabel="Channel")
    for i,v in enumerate(vals.values): ax.text(v+.5,i,f"{v:.1f}%",va="center")
    export(fig,"case08_redesign.png","Source: synthetic CDB601220 Week 4 course data; n=4,000 customers; multi-touch customers counted in each applicable channel.")
    multi=(df[cols].sum(axis=1)>=2).sum(); zero=(df[cols].sum(axis=1)==0).sum(); sm=pct.sum()
    return f"Mechanism: channel flags are non-exclusive; percentages sum to {sm:.1f}%, not 100%. {multi:,} customers ({multi/len(df)*100:.1f}%) have multiple channel touches and {zero} have none. Search touched {pct['touch_search']:.1f}% of customers, but this is reach/association, not exclusive attribution or proof that search drove the purchase. The decoy ‘the slices should add to 100 after rounding’ fails: the excess is about {sm-100:.1f} percentage points, far beyond rounding."

def case9():
    df=pd.read_csv(DATA/"case09_premium_share.csv"); df["share_pct"]=df.premium_revenue_pkr_m/df.total_revenue_pkr_m*100
    x=np.arange(len(df))
    fig,ax=plt.subplots(figsize=(8,4)); ax.plot(x,df.share_pct,marker="o",color=PALETTE["series"][0])
    ax.set_xticks(x,df.quarter); ax.set_ylim(bottom=0); ax.annotate(f"{df.share_pct.iloc[-1]:.1f}%",(x[-1],df.share_pct.iloc[-1]),xytext=(-32,8),textcoords="offset points")
    ax.set(title="Published claim: Premium reaches a record 38% share",xlabel="Quarter",ylabel="Premium share of revenue (%)")
    export(fig,"case09_original.png","Source: synthetic CDB601220 Week 4 course data; eight quarterly observations.")
    fig,ax=plt.subplots(figsize=(8,4))
    ax.plot(x,df.premium_revenue_pkr_m,marker="o",label="Premium revenue",color=PALETTE["series"][0])
    ax.plot(x,df.total_revenue_pkr_m,marker="s",label="Total revenue",color=PALETTE["series"][1])
    ax.set_xticks(x,df.quarter); ax.set(title="Premium share rises mainly as total revenue shrinks",xlabel="Quarter",ylabel="Revenue (PKR millions)"); ax.legend()
    export(fig,"case09_redesign.png","Source: synthetic CDB601220 Week 4 course data; premium and total revenue plotted on same units.")
    pr0,pr1=df.premium_revenue_pkr_m.iloc[[0,-1]]
    tr0,tr1=df.total_revenue_pkr_m.iloc[[0,-1]]
    return f"Mechanism: denominator contraction raises a ratio even when its numerator does not grow. Premium revenue changes {pr0:.1f}→{pr1:.1f} PKR m ({(pr1/pr0-1)*100:+.1f}%), while total revenue changes {tr0:.1f}→{tr1:.1f} ({(tr1/tr0-1)*100:+.1f}%). Share rises 24.0%→38.0%, but that is not a record in absolute premium revenue; the redesign plots numerator and denominator in the same units."

CASES=[case1,case2,case3,case4,case5,case6,case7,case8,case9]
def main():
    style_defaults()
    diagnoses=[]
    for i,fn in enumerate(CASES,1):
        diagnoses.append((i,fn()))
    with open(ROOT/"PART_A_DIAGNOSIS.md","w",encoding="utf-8") as f:
        f.write("# Week 4 Part A — Nine charts rebuilt and diagnosed\\n\\n")
        f.write("**Source note:** All figures and numerical findings below use synthetic datasets generated for CDB601220 Week 4. They are teaching examples, not claims about a real business. The original and redesign PNGs are in `figures/`.\\n\\n")
        for i,d in diagnoses:
            f.write(f"## Case {i}\\n\\n{d}\\n\\n")
            f.write(f"- Published recipe reconstruction: `figures/case{i:02d}_original.png`\\n")
            f.write(f"- Honest redesign: `figures/case{i:02d}_redesign.png`\\n\\n")
        f.write("## References\\n\\n- CDB601220 Week 4 `DATA_DICTIONARY.md` supplied with the assignment (synthetic data definitions).\\n")
        f.write("- Cleveland, W. S. (1993). *Visualizing Data*. Hobart Press — graphical perception and position.\\n")
        f.write("- Wilke, C. O. (2019). *Fundamentals of Data Visualization*. O’Reilly — time-series, proportions, and avoiding misleading displays.\\n")
        f.write("- pandas documentation: time series/date parsing, resampling, and rolling windows (used for implementation).\\n")
    # one multipage PDF with each original and redesign on a page pair
    with PdfPages(ROOT/"partA_diagnosis.pdf") as pdf:
        for i,d in diagnoses:
            for kind,label in [("original","Published recipe"),("redesign","Redesign")]:
                img=plt.imread(OUT/f"case{i:02d}_{kind}.png")
                fig,ax=plt.subplots(figsize=(10,5.6)); ax.imshow(img); ax.axis("off")
                ax.set_title(f"Case {i} — {label}",loc="left",fontweight="bold")
                pdf.savefig(fig,bbox_inches="tight"); plt.close(fig)
            fig,ax=plt.subplots(figsize=(10,4)); ax.axis("off")
            ax.text(0,1.0,f"Case {i}: diagnosis",fontsize=15,fontweight="bold",va="top")
            ax.text(0,.88,textwrap.fill(d,125),fontsize=10,va="top",wrap=True)
            pdf.savefig(fig,bbox_inches="tight"); plt.close(fig)
    print("Generated 18 figures, PART_A_DIAGNOSIS.md, and partA_diagnosis.pdf")
    for i,d in diagnoses: print(f"Case {i}: {d}")

if __name__=="__main__": main()
