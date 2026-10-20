import pandas as pd
import matplotlib.pyplot as plt
import math

df = pd.read_csv("datasaurus.csv")

summary = (
    df.groupby("dataset")
      .agg(
          mean_x=("x", "mean"),
          mean_y=("y", "mean"),
          std_x=("x", "std"),  # sample standard deviation
          std_y=("y", "std"),
          correlation=("x", lambda s: s.corr(df.loc[s.index, "y"]))
      )
      .reset_index()
)

print(summary.round(3).to_string(index=False))
summary.to_csv("datasaurus_summary.csv", index=False)

# 2. Scatter-plot grid
datasets = sorted(df["dataset"].unique())
ncols = 4
nrows = math.ceil(len(datasets) / ncols)
fig, axes = plt.subplots(nrows, ncols, figsize=(15, 11))
axes = axes.flatten()

for ax, name in zip(axes, datasets):
    subset = df[df["dataset"] == name]
    ax.scatter(subset["x"], subset["y"], s=18, alpha=0.8)
    ax.set_title(name.replace("_", " ").title())
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.grid(True, alpha=0.25)
    ax.set_xlabel("x")
    ax.set_ylabel("y")

for ax in axes[len(datasets):]:
    ax.axis("off")

fig.suptitle("Datasaurus Dozen: 13 datasets, 142 points each", fontsize=16)
fig.tight_layout()
plt.savefig("datasaurus_scatter_grid.png", dpi=180, bbox_inches="tight")
plt.show()
