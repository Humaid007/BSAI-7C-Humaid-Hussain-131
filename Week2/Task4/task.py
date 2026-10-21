from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, Rectangle


HERE = Path.cwd()

WINDOWS_DATA_DIR = Path(
    r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week2\assignments\data"
)

OUT = HERE / "Task 4 - Channel Effectiveness outputs"
OUT.mkdir(parents=True, exist_ok=True)

def locate(name):
    for p in (HERE/name, WINDOWS_DATA_DIR/name, Path.cwd()/name):
        if p.exists(): return p
    raise FileNotFoundError(f"Cannot find {name}. Place it beside this script or update WINDOWS_DATA_DIR.")

trials = pd.read_csv(locate("channel_trials.csv"))
iris = pd.read_csv(locate("iris.csv"))

def draw_position(ax, large, small):
    hi = max(float(large), 1.0)
    ax.scatter([.12+.76*large/hi, .12+.76*small/hi], [.5,.5], s=130, color="#777777")
    ax.set_xlim(0,1); ax.set_ylim(0,1)

def draw_length(ax, large, small):
    ax.bar([0,1], [large,small], width=.48, color="#888888", edgecolor="none")
    ax.set_xlim(-.6,1.6); ax.set_ylim(0,max(large,1)*1.08)

def draw_angle(ax, large, small):
    total = large+small; angle = 360*small/total
    ax.add_patch(Wedge((.5,.5),.36,90,90+angle,facecolor="#777777",edgecolor="white"))
    ax.add_patch(Wedge((.5,.5),.36,90+angle,450,facecolor="#b8b8b8",edgecolor="white"))
    ax.set_xlim(0,1); ax.set_ylim(0,1)

def draw_area(ax, large, small):
    # Circle AREA is proportional to value, so radius is proportional to sqrt(value).
    hi=max(large,1)
    for x,v in ((.30,large),(.70,small)):
        ax.add_patch(Circle((x,.5),.29*np.sqrt(v/hi),facecolor="#888888",edgecolor="none"))
    ax.set_xlim(0,1); ax.set_ylim(0,1)

def draw_colour(ax, large, small):
    hi=max(large,1)
    for x,v in ((.28,large),(.72,small)):
        shade=.92-.72*(v/hi)
        ax.add_patch(Rectangle((x-.17,.32),.34,.36,facecolor=str(shade),edgecolor="none"))
    ax.set_xlim(0,1); ax.set_ylim(0,1)

DRAWERS={"position":draw_position,"length":draw_length,"angle":draw_angle,"area":draw_area,"colour":draw_colour}
def draw_trial(row, ax):
    DRAWERS[str(row.channel).lower()](ax,float(row.value_large),float(row.value_small))
    ax.set_axis_off(); ax.set_title("")

def run_real_reader_experiment(seed=None):
    """Show 30 shuffled trials; enter the real participant's estimate from 0 to 100."""
    result=trials.copy()
    result["reader_estimate"]=np.nan; result["absolute_error"]=np.nan
    order=np.random.default_rng(seed).permutation(result.index.to_numpy())
    print("Estimate the smaller value as a percentage of the larger (0–100). Do not reveal true ratios until the end.")
    for n,idx in enumerate(order,1):
        row=result.loc[idx]
        fig,ax=plt.subplots(figsize=(4,3)); draw_trial(row,ax); fig.subplots_adjust(.05,.05,.95,.95)
        plt.show(block=True)
        while True:
            try:
                estimate=float(input(f"Trial {n}/30 — smaller as % of larger: "))
                if 0 <= estimate <= 100: break
                print("Enter a number from 0 to 100.")
            except ValueError: print("Enter a numeric percentage.")
        result.loc[idx,"reader_estimate"]=estimate
        result.loc[idx,"absolute_error"]=abs(estimate/100-float(row.true_ratio))
        plt.close(fig)
    result=result.sort_values("trial")
    result.to_csv(OUT/"channel_results.csv",index=False)
    return result

def plot_channel_ranking(results):
    d=results.dropna(subset=["reader_estimate"]).copy()
    if d.empty: raise ValueError("Run run_real_reader_experiment() with a real reader first.")
    d["absolute_error"]=abs(d.reader_estimate/100-d.true_ratio)
    summary=d.groupby("channel",as_index=False).agg(mean_absolute_error=("absolute_error","mean"),n=("absolute_error","count"))
    summary=summary.sort_values("mean_absolute_error")
    summary.to_csv(OUT/"channel_error_ranking.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,5)); bars=ax.bar(summary.channel,summary.mean_absolute_error,color="#888888",edgecolor="none")
    if len(bars): bars[0].set_color("#d95f02") # one pop-out
    ax.bar_label(bars,labels=[f"{v:.3f}" for v in summary.mean_absolute_error],padding=3)
    ax.set(title="Mean Absolute Error by Visual Encoding Channel",xlabel="Encoding channel",ylabel="Absolute error (ratio units)")
    ax.set_ylim(0,max(float(summary.mean_absolute_error.max())*1.2,.01)); ax.grid(axis="y",alpha=.22)
    fig.tight_layout(); fig.savefig(OUT/"01_channel_error_ranking.png",dpi=300,bbox_inches="tight"); plt.close(fig)
    return summary

def plot_iris_comparison():
    if not {"petal_length","species"}.issubset(iris.columns): raise ValueError("iris.csv needs petal_length and species columns.")
    s=iris.groupby("species",as_index=False).petal_length.mean().sort_values("petal_length").reset_index(drop=True)
    s.to_csv(OUT/"iris_mean_petal_length_by_species.csv",index=False)
    # High-ranking channel: position on common scale.
    fig,ax=plt.subplots(figsize=(8,4.8)); y=np.arange(len(s)); ax.scatter(s.petal_length,y,s=90,color="#777777",zorder=3)
    k=int(s.petal_length.idxmax()); ax.scatter([s.loc[k,"petal_length"]],[k],s=115,color="#d95f02",zorder=4)
    ax.set_yticks(y,s.species); ax.set_xlabel("Mean petal length"); ax.set_title("Mean Petal Length by Species — Position")
    ax.grid(axis="x",alpha=.22); fig.tight_layout(); fig.savefig(OUT/"02_iris_petal_length_position.png",dpi=300,bbox_inches="tight"); plt.close(fig)
    # Lower-ranking channel: sequential lightness only, same means and categories.
    vals=s.petal_length.to_numpy(); lo,hi=vals.min(),vals.max()
    fig,ax=plt.subplots(figsize=(8,3.5))
    for i,(name,v) in enumerate(zip(s.species,vals)):
        shade=.90-.65*((v-lo)/(hi-lo) if hi>lo else 0)
        ax.add_patch(Rectangle((0,i-.35),1,.7,facecolor=str(shade),edgecolor="white"))
        ax.text(1.08,i,name,va="center",ha="left",fontsize=10)
    ax.set_xlim(0,2.2); ax.set_ylim(-.6,len(s)-.4); ax.set_yticks([]); ax.set_xticks([])
    ax.set_title("Mean Petal Length by Species — Colour Only")
    ax.set_xlabel("Darker tile = greater mean petal length; exact values omitted")
    ax.set_frame_on(False); fig.tight_layout(); fig.savefig(OUT/"03_iris_petal_length_colour.png",dpi=300,bbox_inches="tight"); plt.close(fig)
    return s

def write_readme(results=None, ranking=None):
    msg='''# Week 2 — Task 4: Channel effectiveness\n\n## Encoding choices\n- **Position:** two dots on a shared invisible scale.\n- **Length:** two bars from a common zero baseline.\n- **Angle:** two pie wedges representing each value's share of the pair total.\n- **Area:** circle area is proportional to value; radius scales with the square root of value. In `ax.scatter`, `s` is area, not radius.\n- **Colour:** sequential greyscale lightness, not rainbow colour.\n\n## Real-reader procedure\nThe 30 supplied trials are shuffled. Enter the participant's actual estimate of the smaller value as a percentage of the larger. True ratios are not displayed during trials. The script calculates `absolute_error = abs(reader_estimate/100 - true_ratio)` and saves `channel_results.csv`. Do not fabricate estimates.\n\n## Interpreting the ranking\nThe assignment's published order is `position > length > angle > area > volume > colour`, where greater means more accurate. This experiment tests only five channels, so it cannot rank volume. With six ratios and one reader, the results are descriptive for this reader and these stimuli; they cannot establish population-level rankings or statistical significance. The published ranking remains a useful prior guideline because it reflects broader evidence than this small sample. Report disagreement honestly; individual strategy, practice and noise can affect a small experiment.\n\n## Iris application\nBoth charts show the same mean petal length by species. Position on a common scale is recommended because position is generally decoded more accurately than lightness. The second chart uses sequential greyscale tiles and omits exact values to demonstrate the lower-precision channel.\n'''
    if results is not None and results.reader_estimate.notna().all() and ranking is not None:
        msg+='\n## This reader\'s observed mean absolute error\n\n'+', '.join(f"{r.channel}: {r.mean_absolute_error:.3f}" for r in ranking.itertuples())+'\n'
    (OUT/"README.md").write_text(msg,encoding="utf-8")

if __name__ == "__main__":
    plot_iris_comparison(); write_readme()
    print("Iris comparison charts created.")
    print("Run run_real_reader_experiment() with a real participant, then plot_channel_ranking(results).")
    print(f"Output folder: {OUT}")
