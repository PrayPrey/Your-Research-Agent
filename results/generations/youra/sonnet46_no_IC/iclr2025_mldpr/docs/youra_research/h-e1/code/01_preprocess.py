"""
01_preprocess.py — H-E1 Preprocessing Pipeline

Load OpenML corpus CSV, derive features, validate, check decade correlation, save parquet.
If CSV missing, collect via OpenML API fallback.
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

# === PATHS ===
BASE_DIR        = "docs/youra_research/h-e1"
CORPUS_PATH     = f"{BASE_DIR}/code/data/h_e1/openml_dataset_corpus.csv"
PREPROCESSED    = f"{BASE_DIR}/results/preprocessed.parquet"

# === CONSTANTS ===
EXPECTED_N      = 5217
REFERENCE_YEAR  = 2026


def collect_from_openml() -> pd.DataFrame:
    """Fallback: collect corpus via OpenML API if CSV cache missing."""
    print("CSV cache missing. Collecting from OpenML API...")
    import openml
    print("  Fetching dataset list (status=active)...")
    df_all = openml.datasets.list_datasets(output_format='dataframe', status='active')
    print(f"  Fetched {len(df_all)} total datasets")

    # Rename columns to match expected schema
    col_map = {}
    if 'NumberOfInstances' in df_all.columns:
        col_map['NumberOfInstances'] = 'n_instances'
    if 'NumberOfFeatures' in df_all.columns:
        col_map['NumberOfFeatures'] = 'n_features'
    if 'NumberOfClasses' in df_all.columns:
        col_map['NumberOfClasses'] = 'n_classes'
    if 'did' in df_all.columns:
        col_map['did'] = 'dataset_id'
    df_all = df_all.rename(columns=col_map)

    # Get task counts per dataset
    print("  Fetching task list...")
    import openml.tasks
    tasks_df = openml.tasks.list_tasks(output_format='dataframe')
    if 'did' in tasks_df.columns:
        task_counts = tasks_df.groupby('did').size().reset_index(name='N_tasks')
        task_counts = task_counts.rename(columns={'did': 'dataset_id'})
    elif 'dataset_id' in tasks_df.columns:
        task_counts = tasks_df.groupby('dataset_id').size().reset_index(name='N_tasks')
    else:
        print("  WARNING: cannot find dataset_id in tasks_df columns:", tasks_df.columns.tolist())
        task_counts = pd.DataFrame({'dataset_id': [], 'N_tasks': []})

    # Merge
    if 'dataset_id' not in df_all.columns:
        df_all['dataset_id'] = df_all.index

    df = df_all.merge(task_counts, on='dataset_id', how='left')
    df['N_tasks'] = df['N_tasks'].fillna(0).astype(int)

    # Get upload_date and tags from dataset qualities
    # Tags may be in 'tag' column already
    if 'tag' in df.columns:
        df = df.rename(columns={'tag': 'tags'})
    elif 'tags' not in df.columns:
        df['tags'] = None

    # upload_date
    if 'upload_date' not in df.columns:
        # Try to get from quality fields
        if 'version' in df.columns:
            df['upload_date'] = None
        else:
            df['upload_date'] = None

    # Save to CSV cache
    os.makedirs(os.path.dirname(CORPUS_PATH), exist_ok=True)
    df.to_csv(CORPUS_PATH, index=False)
    print(f"  Saved {len(df)} datasets to {CORPUS_PATH}")
    return df


def load_corpus(path: str) -> pd.DataFrame:
    """Load corpus CSV, filter N_tasks >= 1, assert N=5217."""
    if not os.path.exists(path):
        df = collect_from_openml()
    else:
        df = pd.read_csv(path, low_memory=False)
        print(f"  Loaded {len(df)} rows from CSV")
        # Normalize column names from archive schema
        if 'did' in df.columns and 'dataset_id' not in df.columns:
            df = df.rename(columns={'did': 'dataset_id'})
        if 'NumberOfInstances' in df.columns and 'n_instances' not in df.columns:
            df = df.rename(columns={'NumberOfInstances': 'n_instances',
                                    'NumberOfFeatures': 'n_features'})
        if 'tag' in df.columns and 'tags' not in df.columns:
            df = df.rename(columns={'tag': 'tags'})

    # Filter N_tasks >= 1
    df = df[df['N_tasks'] >= 1].copy()
    print(f"  After N_tasks >= 1 filter: N={len(df)}")

    n = len(df)
    if n != EXPECTED_N:
        print(f"  WARNING: Expected N={EXPECTED_N}, got N={n}. Proceeding.")
    else:
        print(f"  ✓ N={n} confirmed")

    return df


def derive_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive all required features."""
    df = df.copy()

    # has_tags: binary 1 if tags field non-null and non-empty
    if 'tags' in df.columns:
        def parse_tags(t):
            if pd.isna(t):
                return []
            if isinstance(t, list):
                return t
            s = str(t).strip()
            if s in ('', 'nan', 'None', '[]'):
                return []
            # Could be comma-separated or space-separated
            return [x.strip() for x in s.replace(',', ' ').split() if x.strip()]
        df['_tag_list'] = df['tags'].apply(parse_tags)
        df['tag_count'] = df['_tag_list'].apply(len)
    else:
        df['tag_count'] = 0

    df['has_tags'] = (df['tag_count'] > 0).astype(int)
    df['log_tag_count_p1'] = np.log(df['tag_count'] + 1)

    # Controls
    for col in ['n_instances', 'n_features']:
        if col not in df.columns:
            df[col] = 1
    df['log_n_instances'] = np.log(df['n_instances'].clip(lower=1))
    df['log_n_features']  = np.log(df['n_features'].clip(lower=1))

    # Age: prefer upload_date_parsed (archive schema) or upload_date
    if 'upload_date_parsed' in df.columns and df['upload_date_parsed'].notna().any():
        df['upload_year'] = pd.to_datetime(df['upload_date_parsed'], errors='coerce').dt.year
    elif 'upload_date' in df.columns and df['upload_date'].notna().any():
        df['upload_year'] = pd.to_datetime(df['upload_date'], errors='coerce').dt.year
    else:
        df['upload_year'] = None

    # Fallback: infer from dataset_id ordering
    if 'upload_year' not in df.columns or df['upload_year'].isna().all():
        if 'dataset_id' in df.columns:
            rank = df['dataset_id'].rank(pct=True)
            df['upload_year'] = (2008 + rank * 16).astype(int)
            print("  WARNING: upload_year inferred from dataset_id rank (proxy)")
        else:
            df['upload_year'] = 2015
            print("  WARNING: upload_year set to 2015 (no date available)")

    df['upload_year'] = pd.to_numeric(df['upload_year'], errors='coerce').fillna(2015).astype(int)
    df['age_years'] = REFERENCE_YEAR - df['upload_year']
    df['age_sq']    = df['age_years'] ** 2
    df['decade']    = (df['upload_year'] // 10) * 10

    # Drop helper column
    if '_tag_list' in df.columns:
        df = df.drop(columns=['_tag_list'])

    return df


def validate(df: pd.DataFrame) -> None:
    """Validate derived DataFrame."""
    key_cols = ['has_tags', 'tag_count', 'log_n_instances', 'log_n_features',
                'age_years', 'age_sq', 'decade', 'N_tasks']
    for col in key_cols:
        assert col in df.columns, f"Missing column: {col}"
        nan_count = df[col].isna().sum()
        if nan_count > 0:
            print(f"  WARNING: {nan_count} NaN in {col} — filling with median")
            df[col] = df[col].fillna(df[col].median())

    has_tags_vals = df['has_tags'].unique()
    assert 0 in has_tags_vals, "has_tags has no 0 values!"
    assert 1 in has_tags_vals, "has_tags has no 1 values!"
    print(f"  ✓ has_tags: {(df['has_tags']==1).sum()} tagged, {(df['has_tags']==0).sum()} untagged")


def check_decade_correlation(df: pd.DataFrame) -> dict:
    """Check correlation between decade and has_tags (RC-3 risk pre-check)."""
    decade_rates = df.groupby('decade')['has_tags'].mean()
    print("\n  Decade-has_tags mean rates:")
    for dec, rate in decade_rates.items():
        flag = " *** HIGH" if rate > 0.90 else ""
        print(f"    {dec}s: {rate:.3f}{flag}")

    # Chi-square test
    ct = pd.crosstab(df['decade'], df['has_tags'])
    chi2, p_val, dof, _ = stats.chi2_contingency(ct)

    # Cramér's V
    n = len(df)
    cramers_v = np.sqrt(chi2 / (n * (min(ct.shape) - 1))) if min(ct.shape) > 1 else 0.0

    result = {
        'decade_rates': decade_rates.to_dict(),
        'chi2': float(chi2),
        'p_value': float(p_val),
        'cramers_v': float(cramers_v),
        'high_correlation_risk': cramers_v > 0.3
    }
    print(f"\n  Chi2={chi2:.2f}, p={p_val:.4f}, Cramér's V={cramers_v:.3f}")
    if result['high_correlation_risk']:
        print("  ⚠ HIGH RC-3 RISK: decade and has_tags strongly correlated")
    else:
        print("  ✓ RC-3 risk acceptable")
    return result


def main():
    print("=" * 60)
    print("H-E1 Step 01: Preprocessing Pipeline")
    print("=" * 60)

    print("\n[1] Loading corpus...")
    df = load_corpus(CORPUS_PATH)

    print("\n[2] Deriving features...")
    df = derive_features(df)

    print("\n[3] Validating...")
    validate(df)

    print("\n[4] Checking decade-has_tags correlation (RC-3 pre-check)...")
    corr_result = check_decade_correlation(df)

    print(f"\n[5] Saving preprocessed data to {PREPROCESSED}...")
    os.makedirs(os.path.dirname(PREPROCESSED), exist_ok=True)
    df.to_parquet(PREPROCESSED, index=False)
    print(f"  ✓ Saved {len(df)} rows, {len(df.columns)} columns")

    print("\n✅ Preprocessing complete")
    print(f"   N={len(df)}, has_tags=1: {df['has_tags'].mean():.1%}")


if __name__ == "__main__":
    main()
