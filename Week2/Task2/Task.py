from pathlib import Path
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

POSSIBLE_DATA_PATHS = [
    Path(r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week2\assignments\data\stimuli_gestalt.csv"),
    Path.cwd() / "stimuli_gestalt.csv",
    Path(__file__).resolve().parent / "stimuli_gestalt.csv" if "__file__" in globals() else Path.cwd() / "stimuli_gestalt.csv",
]
BASE_DIR = Path.cwd()
OUT = BASE_DIR / "Task 2 - Gestalt outputs"
OUT.mkdir(parents=True, exist_ok=True)
CSV = next((p for p in POSSIBLE_DATA_PATHS if p.exists()), None)
if CSV is None:
    raise FileNotFoundError("Could not find stimuli_gestalt.csv. Update POSSIBLE_DATA_PATHS to its actual location.")
df = pd.read_csv(CSV)
REQUIRED = {"panel", "group", "x", "y", "colour", "shape", "size", "connector"}
if not REQUIRED.issubset(df.columns):
    raise ValueError(f"Dataset missing columns: {sorted(REQUIRED-set(df.columns))}")
PANEL_ORDER = ["proximity", "similarity", "enclosure", "continuity", "closure", "connection"]
PRINCIPLE = {"proximity":"Proximity", "similarity":"Similarity", "enclosure":"Enclosure", "continuity":"Good continuation", "closure":"Closure", "connection":"Connection"}
COLOUR_MAP = {"grey":"#777777", "gray":"#777777"}

def draw_panel(ax, panel, with_connections=True, show_title=True):
    """Render a supplied stimulus panel on the given Axes; no ticks or axis labels."""
    part = df[df["panel"] == panel]
    if part.empty:
        raise ValueError(f"Unknown panel: {panel}")
    if panel == "connection" and with_connections:
        connected = part[part["connector"].astype(str).str.lower() != "none"]
        for _, pair in connected.groupby("connector"):
            if len(pair) >= 2:
                xy = pair[["x", "y"]].to_numpy()
                ax.plot(xy[:, 0], xy[:, 1], color="#888888", linewidth=1.15, alpha=.85, zorder=1)
    for shape, shape_rows in part.groupby("shape", sort=False):
        marker = {"circle":"o", "square":"s", "triangle":"^"}.get(str(shape).lower(), "o")
        for colour, rows in shape_rows.groupby("colour", sort=False):
            c = COLOUR_MAP.get(str(colour).lower(), str(colour))
            ax.scatter(rows["x"], rows["y"], s=rows["size"], c=c, marker=marker,
                       edgecolors="white" if panel == "similarity" else "none", linewidths=.35, zorder=3)
    if panel == "enclosure":
        for _, group_rows in part.groupby("group"):
            pad = .22
            x0, x1 = group_rows["x"].min()-pad, group_rows["x"].max()+pad
            y0, y1 = group_rows["y"].min()-pad, group_rows["y"].max()+pad
            ax.add_patch(Rectangle((x0, y0), x1-x0, y1-y0, fill=False,
                                   edgecolor="#888888", linewidth=1.3, zorder=2))
    if show_title:
        ax.set_title(PRINCIPLE[panel], fontsize=11, fontweight="bold")
    ax.set_xlim(part["x"].min()-.65, part["x"].max()+.65)
    ax.set_ylim(part["y"].min()-.65, part["y"].max()+.65)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_visible(False)

def render_all_panels(save=True):
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    for ax, panel in zip(axes.flat, PANEL_ORDER):
        draw_panel(ax, panel)
    fig.suptitle("Six Gestalt principles: layout shapes perceived grouping", fontsize=15, fontweight="bold", y=.99)
    fig.tight_layout(rect=[0, 0, 1, .96])
    if save:
        fig.savefig(OUT / "01_six_gestalt_panels.png", dpi=300, bbox_inches="tight")
    return fig, axes

def render_connection_comparison(save=True):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    draw_panel(axes[0], "connection", with_connections=True)
    axes[0].set_title("Connection lines visible", fontweight="bold")
    draw_panel(axes[1], "connection", with_connections=False)
    axes[1].set_title("Connection lines hidden", fontweight="bold")
    fig.suptitle("When grouping cues compete", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, .93])
    if save:
        fig.savefig(OUT / "02_connection_cue_comparison.png", dpi=300, bbox_inches="tight")
    return fig, axes

def run_real_reader_experiment():
    """Collect actual responses. Does not create or fill in hypothetical participant data."""
    rows = []
    for panel in PANEL_ORDER:
        part = df[df.panel == panel]
        true_groups = int(part["group"].nunique())
        fig, ax = plt.subplots(figsize=(5, 5))
        draw_panel(ax, panel, with_connections=True)
        fig.tight_layout()
        fig.savefig(OUT / f"reader_stimulus_{panel}.png", dpi=300, bbox_inches="tight")
        plt.show()
        plt.close(fig)
        answer = input(f"{PRINCIPLE[panel]}: How many groups do you see? Enter an integer: ").strip()
        while not answer.isdigit():
            answer = input("Please enter a whole number for the perceived group count: ").strip()
        perceived = int(answer)
        rows.append({"panel":panel, "principle":PRINCIPLE[panel], "true_groups":true_groups,
                     "perceived_groups":perceived, "match":"yes" if perceived == true_groups else "no",
                     "connection_lines_visible":True})
    for visible in [True, False]:
        fig, ax = plt.subplots(figsize=(5, 5))
        draw_panel(ax, "connection", with_connections=visible, show_title=False)
        ax.set_title("Connection lines visible" if visible else "Connection lines hidden", fontweight="bold")
        fig.tight_layout()
        fig.savefig(OUT / ("reader_connection_lines_visible.png" if visible else "reader_connection_lines_hidden.png"), dpi=300, bbox_inches="tight")
        plt.show(); plt.close(fig)
        answer = input(f"Connection panel ({'lines visible' if visible else 'lines hidden'}): how many groups do you see? Enter an integer: ").strip()
        while not answer.isdigit():
            answer = input("Please enter a whole number: ").strip()
        perceived = int(answer)
        true_groups = int(df.loc[df.panel == "connection", "group"].nunique())
        rows.append({"panel":"connection_cue_test", "principle":"Connection vs similarity/proximity",
                     "true_groups":true_groups, "perceived_groups":perceived,
                     "match":"yes" if perceived == true_groups else "no",
                     "connection_lines_visible":visible})
    results = pd.DataFrame(rows)
    results.to_csv(OUT / "gestalt_reader_results.csv", index=False)
    print("Saved actual participant responses to:", OUT / "gestalt_reader_results.csv")
    print(results.to_string(index=False))
    return results

def tips_proximity_charts():
    """Create proximity vs equal-spacing grouped bar charts using tips.csv."""
    candidates = [
        Path(r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week2\assignments\data\tips.csv"),
        Path.cwd() / "tips.csv", Path.cwd().parent / "data" / "tips.csv",
        Path(__file__).resolve().parent / "tips.csv" if "__file__" in globals() else Path.cwd() / "tips.csv",
    ]
    tips_path = next((p for p in candidates if p.exists()), None)
    if tips_path is None:
        print("Could not find tips.csv. Put it beside this script or update the tips path list, then rerun tips_proximity_charts().")
        return None
    tips = pd.read_csv(tips_path)
    needed = {"day", "smoker", "tip"}
    if not needed.issubset(tips.columns):
        raise ValueError(f"tips.csv must contain columns {sorted(needed)}")
    day_order = [d for d in ["Thur", "Fri", "Sat", "Sun"] if d in tips.day.unique()]
    smoker_order = [s for s in ["No", "Yes"] if s in tips.smoker.astype(str).unique()]
    means = tips.groupby(["day", "smoker"], observed=False)["tip"].mean().unstack()
    means = means.reindex(index=day_order, columns=smoker_order)
    means.to_csv(OUT / "tips_mean_tip_by_day_smoker.csv")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    width, within_gap, between_gap = .32, .035, .40
    centers = []
    x_positions = []
    vals = []
    labels = []
    cursor = 0.0
    for day in day_order:
        center = cursor + (2*width+within_gap)/2
        centers.append(center)
        for j, smoker in enumerate(smoker_order):
            x = cursor + j*(width+within_gap)
            x_positions.append(x); vals.append(means.loc[day, smoker]); labels.append(smoker)
        cursor += 2*width+within_gap+between_gap
    bars = ax.bar(x_positions, vals, width=width, color=["#777777" if lab=="No" else "#4477aa" for lab in labels], edgecolor="white")
    ax.set_xticks(centers, day_order)
    ax.set_ylabel("Mean tip (dataset currency units)")
    ax.set_xlabel("Day (bars within each day are grouped by proximity)")
    ax.set_title("Proximity groups smoker categories within each day", fontweight="bold")
    ax.grid(axis="y", alpha=.22); ax.set_axisbelow(True)
    ax.legend(handles=[Patch(facecolor="#777777", label="Non-smoker"), Patch(facecolor="#4477aa", label="Smoker")], frameon=False)
    fig.tight_layout(); fig.savefig(OUT/"03_tips_grouped_by_proximity.png", dpi=300, bbox_inches="tight"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    flat_values=[]; flat_labels=[]; flat_colors=[]
    for day in day_order:
        for smoker in smoker_order:
            flat_values.append(means.loc[day, smoker]); flat_labels.append(f"{day}\n{smoker}")
            flat_colors.append("#777777" if smoker=="No" else "#4477aa")
    x=np.arange(len(flat_values))
    ax.bar(x, flat_values, width=.72, color=flat_colors, edgecolor="white")
    ax.set_xticks(x, flat_labels)
    ax.set_ylabel("Mean tip (dataset currency units)")
    ax.set_xlabel("Day and smoker status (equal spacing)")
    ax.set_title("Equal spacing weakens the day-level grouping cue", fontweight="bold")
    ax.grid(axis="y", alpha=.22); ax.set_axisbelow(True)
    ax.legend(handles=[Patch(facecolor="#777777", label="Non-smoker"), Patch(facecolor="#4477aa", label="Smoker")], frameon=False)
    fig.tight_layout(); fig.savefig(OUT/"04_tips_equal_spacing.png", dpi=300, bbox_inches="tight"); plt.close(fig)
    return means

def write_readme(results=None, means=None):
    text = """# Week 2 — Task 2: Gestalt principles of grouping

## Outputs and how to run

Install dependencies with `pip install pandas numpy matplotlib`. Keep `stimuli_gestalt.csv` beside the script or update `POSSIBLE_DATA_PATHS`. Run the script, then call `render_all_panels()` and `render_connection_comparison()` to make the static figures. Call `run_real_reader_experiment()` with a real participant to collect their actual group-count judgements. Do not fabricate responses.

All required chart exports are 300 DPI. The closure panel intentionally retains 44 items. The similarity panel uses spatially mixed colour categories so colour—not spatial separation—signals grouping. Enclosure boundaries are drawn with unfilled grey rectangles. Connection lines are drawn between records sharing the same connector value.

## Real-reader results

The code writes `gestalt_reader_results.csv` after a participant answers all six panels and both versions of the connection panel. This file is intentionally created only by running the experiment. Report the participant's actual perceived counts and mismatches; one reader is not enough to make universal claims. For the connection cue test, compare the line-visible and line-hidden counts to judge whether connection beat similarity and proximity for this reader.

## Gestalt principles in charts

- **Proximity:** bars or points placed closer within a category than between categories are perceived as a group.
- **Similarity:** consistent colour, shape, or marker style signals that marks share a category; colour should not be the only carrier of meaning.
- **Enclosure:** a shaded region or outlined box makes marks inside it read as a group.
- **Closure:** a border or nearly closed shape lets the reader perceive a complete region despite a gap.
- **Continuity:** a line connecting successive values guides the eye along a path.
- **Connection:** a line between two marks makes them appear related even when they differ in colour or are not nearest neighbours.

## Why direct labels can reduce cognitive load

Direct labels use **proximity**: the label is placed beside the item it describes. A legend requires the reader to hold a colour/category mapping in working memory, move attention between legend and chart, and repeatedly match marks to legend entries. Direct labelling shortens that search path and reduces working-memory demand. This is a cognitive-load argument, not simply a style preference.

## Tips.csv proximity comparison

The two tips charts use the same mean tip values by day and smoker status. In the proximity version, bars within each day are separated by a smaller gap than the gap between days. In the equal-spacing version, every bar is spaced evenly. The second version makes day-level grouping less immediate, so the reader must rely more on repeated tick labels and colour legend instead of spatial chunking. If `tips.csv` is not found, place it beside the script or update the path candidates and rerun `tips_proximity_charts()`.

## Cognitive load and data-ink

Data-bearing dots, connector lines, and the enclosure rectangles carry the intended grouping information. Axis ticks, spines, and unnecessary gridlines are removed from stimulus panels because they do not help judge group count. No data-ink ratio is reported, so no unsupported ratio calculation is implied.

## Reporting note

Use finding-led titles for analytical charts and keep context neutral grey. Use no more than one visual pop-out in any final analytical chart. The six stimulus panels retain their intended categorical colour differences as part of the experimental manipulation.
"""
    (OUT/"README.md").write_text(text, encoding="utf-8")

if __name__ == "__main__":
    render_all_panels()
    render_connection_comparison()
    tips_proximity_charts()
    write_readme()
    print(f"Static charts and README saved to: {OUT}")
    print("To collect participant data, call run_real_reader_experiment() from a notebook or run an interactive session.")
