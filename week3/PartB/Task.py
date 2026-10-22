from pathlib import Path
import pandas as pd
from vizlib import lie_factor, lie_verdict

HERE = Path(__file__).resolve().parent
source = pd.read_csv(HERE / "case07_lie_factor.csv")
rows = []
for _, r in source.iterrows():
    lf, data_effect, graphic_effect = lie_factor(
        r.value_start, r.value_end, r.ink_start, r.ink_end,
        ink_dimension=int(r.ink_dimension)
    )
    rows.append({
        "chart_id": r.chart_id,
        "subject": r.subject,
        "data_effect": data_effect,
        "graphic_effect": graphic_effect,
        "lie_factor": lf,
        "verdict": lie_verdict(lf),
    })
results = pd.DataFrame(rows)
results.to_csv(HERE / "lie_factor_results.csv", index=False)
print(results.to_string(index=False, formatters={
    "data_effect": "{:.4f}".format,
    "graphic_effect": "{:.4f}".format,
    "lie_factor": "{:.2f}".format,
}))
