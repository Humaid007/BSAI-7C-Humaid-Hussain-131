from pathlib import Path
import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from vizlib import PALETTE, simulate_cvd, worst_pair, verdict

OUT = Path(__file__).resolve().parent
KINDS = ["deutan", "protan", "tritan"]
# Deliberately choose a familiar palette that is not assumed to be CVD-safe.
# First four Matplotlib tab10 colours.
chosen_name = "Matplotlib tab10 (first four)"
chosen = ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728"]
course3 = list(PALETTE["series"])
course4 = course3 + [PALETTE["series_4th"]]


def swatch_figure(name, colours, suffix, labels=None):
    labels = labels or [f"Slot {i+1}" for i in range(len(colours))]
    fig, ax = plt.subplots(figsize=(10, 2.25))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, len(colours)); ax.set_ylim(0, 1); ax.axis("off")
    for i, (c, lab) in enumerate(zip(colours, labels)):
        ax.add_patch(Rectangle((i + .08, .27), .84, .48, color=c, ec="#333333", lw=.5))
        ax.text(i+.5, .17, lab, ha="center", va="top", fontsize=9)
        ax.text(i+.5, .84, c.upper(), ha="center", va="bottom", fontsize=9, family="monospace")
    ax.set_title(f"{name} — {suffix}", loc="left", fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    path = OUT / (name.lower().replace(' ', '_').replace('/', '_') + "_" + suffix.lower().replace(' ', '_') + ".png")
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path

rows=[]
for name, palette in [("tab10_first_four", chosen), ("course_palette_three", course3), ("course_palette_four", course4)]:
    swatch_figure(name, palette, "original")
    for kind in KINDS:
        simulated = simulate_cvd(palette, kind)
        swatch_figure(name, simulated, kind + " simulation")
        pair = worst_pair(palette, kind)
        rows.append({"palette": name, "condition": kind, "slot_1": pair[0], "slot_2": pair[1], "colour_1_original": pair[2], "colour_2_original": pair[3], "simulated_deltaE": round(pair[4], 2), "verdict": verdict(pair[4])})
    pair = worst_pair(palette, None)
    rows.append({"palette": name, "condition": "normal vision", "slot_1": pair[0], "slot_2": pair[1], "colour_1_original": pair[2], "colour_2_original": pair[3], "simulated_deltaE": round(pair[4], 2), "verdict": verdict(pair[4])})

with (OUT / "worst_pair_results.csv").open("w", newline="", encoding="utf-8") as f:
    writer=csv.DictWriter(f, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)

# Text report with all-pair worst distances in each vision condition.
with (OUT / "PART_C_REPORT.md").open("w", encoding="utf-8") as f:
    f.write("# Week 3 — Part C: Prove the palette, do not claim it\n\n")
    f.write("## Method\n\nThe chosen comparison palette is the first four colours of Matplotlib `tab10` (`#1F77B4`, `#FF7F0E`, `#2CA02C`, `#D62728`). It was selected as a familiar default, not presumed safe. `vizlib.simulate_cvd()` was applied to each palette for deutan, protan and tritan simulations. Swatch images show original colours and each simulated result. `vizlib.worst_pair()` checks every pair; ΔE is the course library's OKLab distance multiplied by 100.\n\n")
    f.write("## Worst-pair results\n\n| Palette | Vision condition | Slots | Original colours | Simulated ΔE | Interpretation |\n|---|---|---:|---|---:|---|\n")
    for r in rows:
        f.write(f"| {r['palette']} | {r['condition']} | {r['slot_1']}–{r['slot_2']} | {r['colour_1_original']} / {r['colour_2_original']} | {r['simulated_deltaE']:.2f} | {r['verdict']} |\n")
    f.write("\n## Interpretation and rule for the rest of the course\n\nThe course palette's fourth colour (`#CC79A7`) is explicitly a weaker slot: the supplied `vizlib.py` documentation says it reduces the CVD separation margin to ΔE 7.6 and falls below 3:1 contrast against the white surface. It must not be used as a colour-only category. If the fourth category is genuinely needed, pair it with a redundant cue such as a distinct marker shape, direct label, texture/pattern, or table view. For charts with more than three categories, I will keep the first three categories colour-coded and distinguish any additional categories using non-colour channels (especially direct labels and different marker shapes/line styles); I will not simply add more hues and rely on a legend.\n\n")
    f.write("**ΔE guide from `vizlib.py`:** ≥15 clear for normal vision; ≥8 target after CVD simulation; 6–8 requires a second encoding channel; <6 means the pair effectively collapses and the palette must be fixed.\n")

print("Created palette swatches and audit results in", OUT)
print("\n".join(f"{r['palette']} | {r['condition']} | slots {r['slot_1']}-{r['slot_2']} | ΔE {r['simulated_deltaE']} | {r['verdict']}" for r in rows))
