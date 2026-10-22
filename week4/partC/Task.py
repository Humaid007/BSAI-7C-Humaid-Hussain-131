import pandas as pd

SHARES_FILE = "shares_eight.csv"
RESULTS_FILE = "pie_ranking_results.csv"

shares = pd.read_csv(SHARES_FILE)
true_order = list(shares.sort_values("share_pct", ascending=False)["slice"])
print("True order:", " > ".join(true_order))

results = pd.read_csv(RESULTS_FILE).fillna("")
for _, row in results.iterrows():
    stimulus = row["stimulus"]
    response = str(row["order_largest_to_smallest"]).strip().upper().replace(" ", "").replace(",", "")
    if not response:
        print(f"{stimulus}: no reader response entered; not scored.")
        continue
    if len(response) != 8 or set(response) != set("ABCDEFGH"):
        print(f"{stimulus}: invalid order {response!r}; enter each letter A-H exactly once.")
        continue
    wrong_positions = [
        i + 1 for i, (actual, expected) in enumerate(zip(response, true_order))
        if actual != expected
    ]
    print(f"{stimulus}: {len(wrong_positions)} letters in wrong positions; "
          f"positions {wrong_positions if wrong_positions else 'none'}.")
