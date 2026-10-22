from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from vizlib import PALETTE, style_defaults

HERE = Path(__file__).resolve().parent

def normalize_ward(value):
    s = str(value).strip().lower().replace('-', ' ').replace('.', '')
    s = ' '.join(s.split())
    if s in {'general medicine', 'gen medicine'}: return 'General Medicine'
    if s in {'cardiology', 'cardio'}: return 'Cardiology'
    if s in {'day surgery'}: return 'Day Surgery'
    if s in {'intensive care', 'icu', 'i cu'}: return 'Intensive Care'
    return str(value).strip()

def load_and_clean(path):
    raw = pd.read_csv(path)
    df = raw.copy()
    audit=[]
    # Dates occur as ISO, abbreviated-month, and slash-separated strings.
    # Slash dates are interpreted day-first; mixed formats are parsed individually.
    df['admit_date'] = pd.to_datetime(df['admit_date'], format='mixed', dayfirst=True, errors='coerce')
    bad_dates = int(df['admit_date'].isna().sum())
    audit.append({'field':'admit_date','rule':'Parse mixed formats with day-first for slash dates; unparseable values become missing','rows_affected':bad_dates,'action':'normalized to datetime; invalid values set NaT'})
    old_ward = df['ward'].copy()
    df['ward'] = df['ward'].map(normalize_ward)
    audit.append({'field':'ward','rule':'Trim whitespace, normalize case/punctuation and map known aliases to canonical ward names','rows_affected':int((old_ward != df['ward']).sum()),'action':'canonical labels: General Medicine, Cardiology, Day Surgery, Intensive Care'})
    # Clinical plausibility rules: do not replace suspicious values with guesses.
    for col, lo, hi, rule in [
        ('heart_rate', 30, 220, 'Values outside 30–220 bpm are treated as implausible/missing'),
        ('bmi', 10, 80, 'Values outside 10–80 kg/m² are treated as implausible/missing'),
        ('los_days', 0, 60, 'LOS above 60 days is flagged as an extreme entry for this cohort and excluded from plotted distributions; raw value retained in source'),
    ]:
        bad = df[col].notna() & ((df[col] < lo) | (df[col] > hi))
        n=int(bad.sum())
        df.loc[bad, col]=np.nan
        audit.append({'field':col,'rule':rule,'rows_affected':n,'action':'set to missing in analysis copy; source CSV unchanged'})
    # MAP is mathematically derived from systolic and diastolic; retain it for audit,
    # but exclude it from the heatmap to avoid counting a derived duplicate as independent evidence.
    audit.append({'field':'map_mmhg','rule':'Recognize MAP as a derived blood-pressure measure; exclude from correlation heatmap to avoid duplicate signal','rows_affected':0,'action':'retained in cleaned file, excluded from heatmap'})
    return raw, df, pd.DataFrame(audit)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input', default=str(HERE/'vitals_10k.csv'))
    ap.add_argument('--outdir', default=str(HERE))
    args=ap.parse_args()
    out=Path(args.outdir); out.mkdir(parents=True, exist_ok=True)
    style_defaults(dpi=150)
    raw, df, audit=load_and_clean(args.input)
    df.to_csv(out/'cleaned_vitals.csv', index=False)
    audit.to_csv(out/'data_quality_audit.csv', index=False)

    # Choose LOS for distribution and ward comparison; omit flagged extreme entries.
    valid_los=df['los_days'].dropna()
    q1,q3=valid_los.quantile([.25,.75]); iqr=q3-q1
    # The declared 0.5-day histogram bin width is fixed for reproducibility.
    fig, axes=plt.subplots(2,2, figsize=(15,10), constrained_layout=True)
    ax1,ax2,ax3,ax4=axes.flat
    sns.histplot(data=df, x='los_days', binwidth=0.5, color=PALETTE['series'][0], edgecolor='white', ax=ax1)
    ax1.set_title(f'Length of stay is strongly right-skewed (n={valid_los.size:,})')
    ax1.set_xlabel('Length of stay (days; 0.5-day bins)'); ax1.set_ylabel('Patient records')

    order=['General Medicine','Cardiology','Day Surgery','Intensive Care']
    sns.boxplot(data=df, x='ward', y='los_days', order=order, color=PALETTE['series'][0], showfliers=False, ax=ax2)
    ax2.set_title('Length of stay differs by ward')
    ax2.set_xlabel('Ward'); ax2.set_ylabel('Length of stay (days)')
    ax2.tick_params(axis='x', rotation=18)

    # Panel 4 determines the one pair worth plotting: systolic and diastolic BP
    # are the strongest non-derived pair among the core vital measurements.
    pair=df[['systolic','diastolic']].dropna()
    r=pair.corr().iloc[0,1]
    sns.scatterplot(data=pair, x='systolic', y='diastolic', s=18, alpha=.35,
                    color=PALETTE['series'][0], edgecolor=None, ax=ax3)
    ax3.set_title(f'Systolic and diastolic BP move together (r={r:.2f})')
    ax3.set_xlabel('Systolic blood pressure (mmHg)'); ax3.set_ylabel('Diastolic blood pressure (mmHg)')

    corr_cols=['age','systolic','diastolic','heart_rate','spo2','bmi','chol_mmol_l','glucose_mmol_l','los_days']
    corr=df[corr_cols].corr(numeric_only=True)
    sns.heatmap(corr, cmap=PALETTE['diverging'], center=0, vmin=-1, vmax=1,
                annot=True, fmt='.2f', square=True, linewidths=.5,
                cbar_kws={'label':'Pearson correlation (r)'}, annot_kws={'size':7}, ax=ax4)
    ax4.set_title('Correlations among cleaned clinical measures')
    ax4.set_xlabel('Measure'); ax4.set_ylabel('Measure')
    for ax in axes.flat:
        ax.grid(False) if ax is ax4 else None
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    fig.suptitle('Clinical review: data quality and vital-sign relationships', fontsize=16, fontweight='bold')
    fig.text(.01,.005,'Source: supplied vitals_10k.csv (10,000 records). Implausible HR/BMI and LOS >60 days are missing in analysis copy; ward labels standardized. MAP excluded from heatmap because derived from BP.', fontsize=8, color=PALETTE['ink_soft'])
    fig.savefig(out/'clinical_review_figure.png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    print('Input rows:',len(raw))
    print('\nRequired diagnostics:')
    raw.info()
    print('\nDescribe:')
    print(raw.describe().T)
    print('\nWard counts (raw labels):')
    print(raw.ward.value_counts(dropna=False))
    print('\nFirst 20 admission date strings:')
    print(raw.admit_date.head(20).tolist())
    print('\nData quality audit:')
    print(audit.to_string(index=False))
    print(f'\nSaved {out / "clinical_review_figure.png"}')

if __name__=='__main__': main()
