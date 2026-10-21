from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

POSSIBLE_DIRS = [
    Path(r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week2\assignments\data"),
    Path.cwd(),
    Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd(),
]
def locate_csv(filename):
    for folder in POSSIBLE_DIRS:
        candidate = folder / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Could not find {filename}. Put it beside this script/notebook or update POSSIBLE_DIRS."
    )

CAR_PATH = locate_csv("car_crashes.csv")
TIPS_PATH = locate_csv("tips.csv")
OUT = Path.cwd() / "Task 3 - Cognitive Load outputs"
OUT.mkdir(parents=True, exist_ok=True)

car = pd.read_csv(CAR_PATH)
tips = pd.read_csv(TIPS_PATH)
required = {"total", "abbrev"}
if not required.issubset(car.columns):
    raise ValueError(f"car_crashes.csv needs columns {sorted(required)}")
if not {"total_bill", "tip", "day"}.issubset(tips.columns):
    raise ValueError("tips.csv needs total_bill, tip, and day columns")

data = car.sort_values("total", ascending=False).reset_index(drop=True)
labels = data["abbrev"].astype(str).tolist()
values = data["total"].astype(float).to_numpy()
x = np.arange(len(data))

fig, ax = plt.subplots(figsize=(19, 9))
colors = plt.get_cmap("hsv")(np.linspace(0, 1, len(data), endpoint=False))
bars = ax.bar(x, values, color=colors, edgecolor="black", linewidth=0.8)
ax.set_xticks(x, labels, rotation=90, fontsize=7)
ax.set_xlabel("State abbreviation")
ax.set_ylabel("Total motor vehicle fatality rate (source column: total)")
ax.set_title("BAD EXAMPLE — Total by State (x-axis: state, y-axis: total)")
ax.grid(True, axis="both", linewidth=1.1, alpha=0.9)
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(2)
legend_handles = [Patch(facecolor=colors[i], edgecolor="black", label=labels[i]) for i in range(len(data))]
ax.legend(handles=legend_handles, title="State (51 entries)", ncol=3, fontsize=6, loc="upper right")
fig.tight_layout()
fig.savefig(OUT / "01_BAD_EXAMPLE_overloaded.png", dpi=300, bbox_inches="tight")
plt.close(fig)

fig, axes = plt.subplots(5, 1, figsize=(16, 17), sharey=True)
steps = [
    ("1. Remove the 51-entry legend", "Removed legend: extraneous load; bars and labels still cluttered.", "rainbow"),
    ("2. Remove frame and vertical gridlines", "Removed frame and x-grid: extraneous ink; keep light horizontal guides.", "rainbow"),
    ("3. Use one hue", "One hue removes arbitrary colour differences that imply no data meaning.", "single"),
    ("4. Sort bars by value", "Sorting adds no ink; it makes rank and clusters easier to scan.", "single"),
    ("5. Label only what matters", "Label top five; retain state ticks in small grey type for context.", "single"),
]
for idx, (ax, (title, note, mode)) in enumerate(zip(axes, steps)):
    if mode == "rainbow" and idx < 2:
        c = colors
    else:
        c = ["#356a8a"] * len(data)
    bars = ax.bar(x, values, color=c, edgecolor="none" if idx >= 1 else "black", linewidth=.4 if idx == 0 else 0)
    if idx == 3:
        order = np.argsort(values)[::-1]
        ax.clear()
        ax.bar(np.arange(len(order)), values[order], color="#356a8a", edgecolor="none")
        ax.set_xticks(np.arange(len(order)), np.array(labels)[order], rotation=90, fontsize=6, color="grey")
    elif idx == 4:
        ax.clear()
        order = np.argsort(values)[::-1]
        ax.bar(np.arange(len(order)), values[order], color="#356a8a", edgecolor="none")
        top = 5
        ax.set_xticks(np.arange(len(order)), np.array(labels)[order], rotation=90, fontsize=6, color="grey")
        for j in range(top):
            ax.text(j, values[order[j]] + .35, f"{labels[order[j]]} {values[order[j]]:.1f}",
                    ha="center", va="bottom", fontsize=7, rotation=45)
        # one pop-out: highest bar only
        ax.patches[0].set_color("#d95f02")
    else:
        ax.set_xticks(x, labels, rotation=90, fontsize=6)
    ax.set_title(title, loc="left", fontsize=11, weight="bold")
    ax.text(.995, .88, note, transform=ax.transAxes, ha="right", va="top", fontsize=8,
            bbox=dict(facecolor="white", edgecolor="none", alpha=.8))
    ax.set_ylabel("Total")
    ax.grid(True, axis="y", alpha=.22 if idx >= 1 else .8, linewidth=.6 if idx >= 1 else 1)
    if idx >= 1:
        ax.grid(False, axis="x")
        for spine in ax.spines.values():
            spine.set_visible(False)
    if idx >= 2:
        ax.tick_params(axis="x", length=0)
    if idx == 4:
        ax.set_xlabel("State abbreviation (ranked by total)")
fig.suptitle("Reducing Extraneous Load Without Changing the Data", fontsize=15, y=.998)
fig.tight_layout(rect=[0, 0, 1, .992])
fig.savefig(OUT / "02_five_panel_reduction.png", dpi=300, bbox_inches="tight")
plt.close(fig)

order = np.argsort(values)[::-1]
top_n = 5
top_vals = values[order[:top_n]]
other_mean = values[order[top_n:]].mean()
chunk_labels = [f"{labels[i]}" for i in order[:top_n]] + ["Other 46 states\n(mean)"]
chunk_vals = list(top_vals) + [other_mean]
fig, ax = plt.subplots(figsize=(10, 6))
chunk_bars = ax.bar(chunk_labels, chunk_vals, color=["#356a8a"]*6, edgecolor="none")
chunk_bars[0].set_color("#d95f02")
ax.set_title("Five Highest States Plus the Other 46 (Mean)", loc="left")
ax.set_ylabel("Total motor vehicle fatality rate (source column: total)")
ax.grid(axis="y", alpha=.22)
ax.set_axisbelow(True)
ax.text(.01, -.23, "Chunking: five individually named states + one pooled group. Cost: individual differences and ranking among the other 46 are hidden.",
        transform=ax.transAxes, fontsize=9)
fig.tight_layout()
fig.savefig(OUT / "03_chunked_top5_other46.png", dpi=300, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(np.arange(len(data)), values, color="#356a8a")
ax.set_title("BAD EXAMPLE")
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel("")
ax.set_ylabel("")
for spine in ax.spines.values():
    spine.set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "04_BAD_EXAMPLE_overstripped.png", dpi=300, bbox_inches="tight")
plt.close(fig)

tips["tip_pct"] = 100 * tips["tip"] / tips["total_bill"]
mean_pct = tips["tip_pct"].mean()
by_day = tips.groupby("day", observed=False)["tip_pct"].mean().reindex(["Thur", "Fri", "Sat", "Sun"]).dropna()
fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.bar(by_day.index, by_day.values, color="#b9c4cc", edgecolor="none")
closest = int(np.argmin(np.abs(by_day.values - mean_pct)))
bars[closest].set_color("#d95f02")
ax.axhline(mean_pct, color="#333333", linestyle="--", linewidth=1.8,
           label=f"Overall mean: {mean_pct:.1f}%")
ax.text(3.45, mean_pct, f"  Overall mean {mean_pct:.1f}%", va="bottom", ha="right", fontsize=9)
ax.set_title("Mean Tip as a Share of the Bill, by Day", loc="left")
ax.set_ylabel("Mean tip (% of total bill)")
ax.set_xlabel("Day")
ax.grid(axis="y", alpha=.2)
ax.set_axisbelow(True)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "05_tips_reference_line.png", dpi=300, bbox_inches="tight")
plt.close(fig)

elements = [
    ("Bars and their heights", "Intrinsic", "Encode the 51 numeric values."),
    ("State labels", "Intrinsic / partly extraneous", "Identify each bar, but 51 rotated labels overwhelm scanning."),
    ("51 distinct colours", "Extraneous", "No variable maps to colour; colours add arbitrary differences."),
    ("Heavy horizontal gridlines", "Extraneous", "Too dark and dense for reading values."),
    ("Vertical gridlines", "Extraneous", "Do not improve comparison of bar heights."),
    ("Full box frame", "Extraneous", "Adds boundaries without encoding data."),
    ("51-entry legend", "Extraneous", "Repeats state labels and colour has no data meaning."),
    ("Drop shadow / 3-D effect", "Extraneous", "Adds decorative ink and can distort perceived size."),
    ("Title naming axes", "Partly germane", "Communicates topic but duplicates axis labels rather than stating a finding."),
    ("Axis ticks / baseline", "Germane", "Provide scale and reference for comparing bar heights."),
]
pd.DataFrame(elements, columns=["element","classification","reason"]).to_csv(OUT / "load_classification.csv", index=False)
# Count bar rectangles as data marks; all other visible graphic components as non-data marks (estimate).
data_marks = len(data)
nondata_estimate = len(data) + 51 + 102 + 2 + 4 + 51 + 10
total_marks_estimate = data_marks + nondata_estimate
ink_working = pd.DataFrame([{
    "estimate_method": "Count each bar as one data mark; estimate labels, gridline segments, frame edges, legend swatches/text, and axes/ticks as non-data marks.",
    "data_marks": data_marks,
    "estimated_nondata_marks": nondata_estimate,
    "estimated_total_marks": total_marks_estimate,
    "estimated_data_ink_ratio": round(data_marks / total_marks_estimate, 3),
    "working": f"{data_marks} data marks / ({data_marks} data marks + {nondata_estimate} estimated non-data marks) = {data_marks/total_marks_estimate:.3f}"
}])
ink_working.to_csv(OUT / "data_ink_ratio_working.csv", index=False)

readme = f"""# Week 2 — Task 3: Cognitive Load and Data-Ink Ratio

## Data and units
The supplied `car_crashes.csv` contains {len(car)} rows and columns `{', '.join(car.columns)}`. This task plots only `total`. Do not put `speeding`, `alcohol`, `not_distracted`, `no_previous`, `ins_premium`, or `ins_losses` on the same axis: these represent different units/scales. The `tips.csv` file contains {len(tips)} rows.

## 1. Deliberately overloaded chart
`01_BAD_EXAMPLE_overloaded.png` is explicitly labelled **BAD EXAMPLE**. It uses 51 distinct colours, all state labels rotated, heavy gridlines in both directions, a full frame, and a 51-entry legend. A 3-D effect is intentionally omitted because it would add distortion without useful information; the other requested sources of clutter are present.

## 2. Element classification and data-ink estimate
See `load_classification.csv` for each element, its category, and rationale. Classification depends on purpose: bars encode the values (intrinsic), scale/ticks help decode values (germane), while arbitrary colours, excessive gridlines, redundant legend and frame are extraneous. State labels identify observations but all 51 rotated labels are excessive in this layout.

**Estimated data-ink ratio working:** count each of the {data_marks} bars as one data mark. Estimate {nondata_estimate} non-data marks from labels, gridline segments, frame, legend and axes/ticks. Then data-ink ratio ≈ {data_marks} / ({data_marks} + {nondata_estimate}) = **{data_marks/total_marks_estimate:.3f}**. This is a transparent approximate mark-count method, not a pixel-based measurement; results depend on the counting rule.

## 3. Five-panel reduction
`02_five_panel_reduction.png` shows progressive edits. Sorting is especially valuable because it adds no ink: it changes position only and makes rank immediately visible. The last panel labels only the five highest values and uses a single pop-out for the highest bar. A small grey tick-label system preserves context.

## 4. Working-memory chunking
`03_chunked_top5_other46.png` shows the top five states individually and pools the remaining 46 as one mean. This yields six chunks, within the practical 4 ± 1 range. Cost: the individual values and ordering within the pooled 46 states are hidden; the mean is not a substitute for their full distribution.

## 5. Over-stripped example and stopping rule
`04_BAD_EXAMPLE_overstripped.png` removes labels, tick values and units. The data-ink ratio could rise because explanatory marks disappear, but readers can no longer identify values or interpret the scale.

**Stopping rule:** Remove an element only when it contributes no meaningful encoding, orientation, comparison, or context needed for the reader's task.

## Question: adding ink can lower cognitive load
`05_tips_reference_line.png` plots mean tip percentage by day and adds an overall-mean reference line with a direct numeric label. The line and annotation add ink but spare readers from calculating the overall mean mentally and comparing it across bars. Maximising data-ink is a heuristic, not a rule: the goal is fast and accurate interpretation, not the fewest possible marks.

## Outputs
- `01_BAD_EXAMPLE_overloaded.png`
- `02_five_panel_reduction.png`
- `03_chunked_top5_other46.png`
- `04_BAD_EXAMPLE_overstripped.png`
- `05_tips_reference_line.png`
- `load_classification.csv`
- `data_ink_ratio_working.csv`

All charts are exported at 300 DPI. Code uses the object-oriented Matplotlib API (`fig, ax = plt.subplots()` and `ax` methods).
"""
(OUT/"README.md").write_text(readme, encoding="utf-8")

print(f"Loaded car_crashes.csv: {car.shape}; tips.csv: {tips.shape}")
print(f"Output folder: {OUT.resolve()}")
print(f"Data-ink estimate: {data_marks}/{total_marks_estimate} = {data_marks/total_marks_estimate:.3f}")
print("Created five charts, load classification, data-ink working, and README.")
