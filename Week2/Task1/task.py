from pathlib import Path
import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path.cwd()

CSV_CANDIDATES = [
    BASE_DIR / "stimuli_search.csv",
    Path(r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week2\assignments\data\stimuli_search.csv"),
]
CSV = next((p for p in CSV_CANDIDATES if p.exists()), None)
if CSV is None:
    raise FileNotFoundError(
        "Could not find stimuli_search.csv. Put it beside this script/notebook, "
        "or update CSV_CANDIDATES to the file's actual location."
    )
OUT = BASE_DIR / "Task 1 - Visual Search outputs"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV)
required = {'trial','condition','set_size','target_present','item_index','x','y','colour','shape','is_target'}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

CONDITIONS = ['colour', 'shape', 'conjunction']
EXPERIMENT_SET_SIZES = [9, 25, 49]


def draw_trial(trial_number, ax, data=None):
    """Draw one trial on ax using x/y, colour and shape; no axes/ticks/title."""
    if data is None:
        data = df
    rows = data.loc[data['trial'] == trial_number]
    if rows.empty:
        raise ValueError(f"Trial {trial_number} was not found in the dataset.")
    for row in rows.itertuples(index=False):
        color = str(row.colour).strip().lower()
        shape = str(row.shape).strip().lower()
        if shape == 'circle':
            patch = Circle((row.x, row.y), radius=0.105, facecolor=color, edgecolor='black', linewidth=0.35)
        elif shape == 'square':
            patch = Rectangle((row.x - 0.095, row.y - 0.095), 0.19, 0.19,
                              facecolor=color, edgecolor='black', linewidth=0.35)
        else:
            raise ValueError(f"Unrecognized shape: {shape}")
        ax.add_patch(patch)
    rows_x = rows['x']
    rows_y = rows['y']
    pad = 0.35
    ax.set_xlim(float(rows_x.min()) - pad, float(rows_x.max()) + pad)
    ax.set_ylim(float(rows_y.min()) - pad, float(rows_y.max()) + pad)
    ax.set_aspect('equal', adjustable='box')
    ax.set_axis_off()
    return ax


def preview_one_per_condition(set_size=25):
    """Display one trial from each condition at the requested set size."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, condition in zip(axes, CONDITIONS):
        trial_ids = df.loc[(df['condition'] == condition) & (df['set_size'] == set_size), 'trial'].drop_duplicates()
        if trial_ids.empty:
            raise ValueError(f"No trials found for condition={condition}, set_size={set_size}")
        draw_trial(int(trial_ids.iloc[0]), ax)
    fig.tight_layout()
    fig.savefig(OUT / '01_trial_rendering_check.png', dpi=180, bbox_inches='tight')
    plt.show()
    return fig


def choose_experiment_trials():
    """Choose 18 unique trials: one present and one absent per selected cell."""
    rng = random.Random()
    chosen = []
    for condition in CONDITIONS:
        for size in EXPERIMENT_SET_SIZES:
            for present in ['yes', 'no']:
                ids = df.loc[
                    (df['condition'] == condition) &
                    (df['set_size'] == size) &
                    (df['target_present'].astype(str).str.lower() == present),
                    'trial'
                ].drop_duplicates().tolist()
                if not ids:
                    raise ValueError(f"No trial for {condition}, set_size={size}, target_present={present}")
                chosen.append({'condition': condition, 'set_size': size,
                               'target_present': present, 'trial': int(rng.choice(ids))})
    rng.shuffle(chosen)
    return chosen


def run_human_experiment():
    """Show 18 trials, collect human responses and save actual results."""
    print("\nVISUAL SEARCH EXPERIMENT — ONE PARTICIPANT")
    print("Target instructions are given before each condition block, not during trials.")
    print("Respond yes/no then press Enter as quickly and accurately as you can.")
    print("This 18-trial version uses set sizes 9, 25, and 49.\n")
    chosen = choose_experiment_trials()
    results = []
    # Block by condition so the target is announced before the block, then randomize within block.
    block_order = CONDITIONS.copy()
    random.shuffle(block_order)
    for condition in block_order:
        block_trials = [t for t in chosen if t['condition'] == condition]
        random.shuffle(block_trials)
        if condition == 'colour':
            target_description = 'a RED CIRCLE among BLUE CIRCLES'
        elif condition == 'shape':
            target_description = 'a BLUE SQUARE among BLUE CIRCLES'
        else:
            target_description = 'a RED CIRCLE among RED SQUARES and BLUE CIRCLES'
        input(f"\nBLOCK: {condition.upper()} SEARCH\nTarget: {target_description}. Press Enter when ready.")
        for item in block_trials:
            trial_number = item['trial']
            trial_rows = df[df['trial'] == trial_number]
            fig, ax = plt.subplots(figsize=(6, 5))
            draw_trial(trial_number, ax)
            fig.tight_layout()
            plt.show(block=False)
            plt.pause(0.15)
            start = time.perf_counter()
            while True:
                answer = input(f"Trial {len(results)+1}/18 — is the target there? (yes/no): ").strip().lower()
                if answer in {'yes', 'y', 'no', 'n'}:
                    break
                print("Please type yes or no.")
            elapsed = time.perf_counter() - start
            plt.close(fig)
            response = 'yes' if answer in {'yes', 'y'} else 'no'
            actual = str(item['target_present']).lower()
            correct = response == actual
            results.append({
                'participant': 'P1', 'trial': trial_number,
                'condition': condition, 'set_size': int(item['set_size']),
                'target_present': actual, 'response': response,
                'correct': bool(correct), 'response_time_seconds': elapsed,
                'response_time_ms': elapsed * 1000,
            })
            print(f"Recorded: {elapsed:.3f}s, {'correct' if correct else 'incorrect'}")
    results_df = pd.DataFrame(results)
    results_path = OUT / 'search_results.csv'
    results_df.to_csv(results_path, index=False)
    print(f"\nSaved actual participant results to: {results_path}")
    return results_df


def analyze_results(results_df=None):
    """Plot target-present RT against set size and report linear slopes in ms/item."""
    results_path = OUT / 'search_results.csv'
    if results_df is None:
        if not results_path.exists():
            raise FileNotFoundError("Run run_human_experiment() first to create search_results.csv.")
        results_df = pd.read_csv(results_path)
    # The assignment specifies target-present trials only; correctness is retained
    # as a separate outcome column rather than silently dropping responses.
    present = results_df[
        results_df['target_present'].astype(str).str.lower() == 'yes'
    ].copy()
    if present.empty:
        raise ValueError("No correct target-present trials are available to plot.")
    summary = present.groupby(['condition', 'set_size'], as_index=False).agg(
        mean_rt_ms=('response_time_ms', 'mean'), n=('response_time_ms', 'size')
    )
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    for condition in CONDITIONS:
        part = summary[summary['condition'] == condition].sort_values('set_size')
        if not part.empty:
            ax.plot(part['set_size'], part['mean_rt_ms'], marker='o', linewidth=2, label=condition.title())
    ax.set_xlabel('Set size (number of items)')
    ax.set_ylabel('Mean response time (ms) — correct target-present trials')
    ax.set_title('Visual Search: Response Time vs Set Size')
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / '02_response_time_by_set_size.png', dpi=180, bbox_inches='tight')
    plt.show()
    summary.to_csv(OUT / 'response_time_summary.csv', index=False)

    slopes = []
    for condition in CONDITIONS:
        part = summary[summary['condition'] == condition]
        if len(part) >= 2:
            slope, intercept = np.polyfit(part['set_size'].to_numpy(dtype=float), part['mean_rt_ms'].to_numpy(dtype=float), 1)
            slopes.append({'condition': condition, 'slope_ms_per_item': slope,
                           'intercept_ms': intercept, 'n_set_sizes': len(part)})
        else:
            slopes.append({'condition': condition, 'slope_ms_per_item': np.nan,
                           'intercept_ms': np.nan, 'n_set_sizes': len(part)})
    slope_df = pd.DataFrame(slopes)
    slope_df.to_csv(OUT / 'search_slopes.csv', index=False)
    print("\nSlopes (fit to target-present trials only):")
    for row in slope_df.itertuples(index=False):
        if pd.notna(row.slope_ms_per_item):
            interpretation = 'near-flat' if abs(row.slope_ms_per_item) < 5 else ('rising' if row.slope_ms_per_item > 0 else 'falling')
            print(f"  {row.condition}: {row.slope_ms_per_item:.2f} ms/item ({interpretation}); one reader, small n")
        else:
            print(f"  {row.condition}: insufficient set-size points for a slope")
    print("\nInterpretation reminder: slopes describe this one reader and this small sample; do not over-claim.")
    return summary, slope_df


def write_readme(results_df=None, slope_df=None):
    """Write assignment interpretation, incorporating measured slopes if available."""
    lines = [
        '# Week 2 — Task 1: Preattentive Attributes and Visual Search', '',
        '## Design and trial-count note',
        'The task says 18 trials but also requests two trials (one target-present and one target-absent) for every condition × set-size cell. With 3 conditions and 5 set sizes, that complete design needs 30 trials. To retain the requested 18-trial session, this script samples set sizes 9, 25, and 49: 3 conditions × 3 sizes × 2 target statuses = 18 trials.', '',
        '## Missing data and response recording',
        'The participant responses are recorded live. `search_results.csv` contains the selected stimulus trial, condition, set size, target status, response, correctness, response time in seconds, and response time in milliseconds. Response times are measured around the participant\'s yes/no keyboard response using `time.perf_counter()`. Results must come from the actual participant; do not substitute fabricated values.', '',
        '## Chart choices',
        '1. **Trial rendering check:** three panels show one trial from each condition at set size 25. Item position, colour, and shape come directly from the CSV; axes and ticks are removed.',
        '2. **Response time vs set size:** line chart, one line per condition, using target-present trials only. A line chart makes changes in response time across ordered set sizes easy to compare.',
        '3. **Slopes:** a first-degree `numpy.polyfit` is fit to each condition\'s mean correct target-present response time. Slopes are reported in milliseconds per additional item. A near-zero slope is consistent with efficient/preattentive search; a positive slope is consistent with more serial search.', '',
        '## Conjunction explanation',
        'A single feature such as red colour or circular shape can stand out across the display, allowing the visual system to detect it in parallel. A red circle requires combining colour and shape at the same location. Because distractors share one of those features, attention may need to inspect candidate items to bind the two features together, so response time can rise with set size.', '',
        '## A chart that can create an implicit conjunction search',
        'A grouped chart with several colours and marker shapes can require readers to locate a particular combination (for example, one series identified by both colour and shape). A multi-series scatter plot using both colour and marker shape is one plausible example from a data-visualization assignment; the exact chart should be named from the charts actually produced in the student\'s work.', '',
        '## Interpretation cautions',
        'Target-absent trials are not combined with target-present trials because absent trials can take longer even for simple feature searches. Report slopes honestly: with only one reader and three selected set sizes, noisy or unexpected slopes may reflect few trials, practice/learning, or stimulus-layout effects. A result contrary to the expected theory should be reported, not manipulated.', '',
        '## Question: is the larger seasonal/visual swing caused by growing scale?',
        'For this visual-search task, the relevant follow-up is to compare response-time slopes across set sizes and conditions. For this assignment\'s question, use the measured slopes; do not infer the result before the participant data exist.', '',
        '## Outputs',
        '- `01_trial_rendering_check.png`',
        '- `search_results.csv` (created after the participant completes all 18 trials)',
        '- `02_response_time_by_set_size.png` (created after results are collected)',
        '- `response_time_summary.csv` and `search_slopes.csv` (created after analysis)',
        '- `stimuli_search.csv` and `task1_visual_search.py`', '',
        '## Run',
        'Install: `pip install pandas numpy matplotlib`',
        'Open this script in Jupyter, run it, then call `preview_one_per_condition()` to verify rendering, `run_human_experiment()` to collect participant data, and `analyze_results()` to make the RT chart and calculate slopes.',
    ]
    if slope_df is not None and not slope_df.empty:
        lines += ['', '## Measured slopes', 'These are the measured values from the participant session; only interpret after data collection:']
        for row in slope_df.itertuples(index=False):
            if pd.notna(row.slope_ms_per_item):
                lines.append(f'- {row.condition}: {row.slope_ms_per_item:.2f} ms/item.')
    (OUT / 'README.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    print(f"CSV loaded: {CSV}")
    print(f"Rows: {len(df)} | unique trials: {df['trial'].nunique()}")
    print(f"Outputs folder: {OUT}")
    print("Next: preview_one_per_condition(); then run_human_experiment(); then analyze_results().")
    preview_one_per_condition(set_size=25)
