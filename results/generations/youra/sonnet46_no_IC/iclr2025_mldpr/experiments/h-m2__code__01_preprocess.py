"""
01_preprocess.py — H-M2 Preprocessing
Load H-E1 preprocessed parquet, filter to has_tags=1 subset, derive IV, collinearity check.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr

PROJECT_ROOT   = Path(__file__).resolve().parents[4]
H_E1_PARQUET   = PROJECT_ROOT / "docs/youra_research/h-e1/results/preprocessed.parquet"
H_E1_CSV       = PROJECT_ROOT / "docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv"
OUT_PARQUET    = PROJECT_ROOT / "docs/youra_research/h-m2/results/tagged_subset.parquet"

EXPECTED_N_TAGGED = 2625


def load_h_e1_parquet() -> pd.DataFrame:
    if H_E1_PARQUET.exists():
        print(f"  Loading parquet: {H_E1_PARQUET}")
        df = pd.read_parquet(H_E1_PARQUET)
        print(f"  Loaded N={len(df)} rows")
        return df
    print(f"  Parquet not found, falling back to CSV: {H_E1_CSV}")
    df = pd.read_csv(H_E1_CSV)
    # Minimal feature derivation matching H-E1 derive_features()
    df['has_tags'] = df['tags'].apply(lambda x: 1 if (pd.notna(x) and str(x).strip() != '') else 0)
    df['tag_count'] = df['tags'].apply(lambda x: str(x).count(',') + 1 if (pd.notna(x) and str(x).strip() != '') else 0)
    df['log_tag_count_p1'] = np.log(df['tag_count'] + 1)
    df['log_n_instances'] = np.log(df['NumberOfInstances'].clip(lower=1))
    df['log_n_features'] = np.log(df['NumberOfFeatures'].clip(lower=1))
    # age_years from upload date
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            df['upload_date'] = pd.to_datetime(df.get('UploadDate', df.get('upload_date', None)), errors='coerce')
            df['age_years'] = (pd.Timestamp('2024-01-01') - df['upload_date']).dt.days / 365.25
        except Exception:
            df['age_years'] = 5.0
    df['age_sq'] = df['age_years'] ** 2
    df['decade'] = (df['upload_date'].dt.year // 10 * 10).fillna(2010).astype(int) if 'upload_date' in df.columns else 2010
    # N_tasks
    if 'N_tasks' not in df.columns:
        df['N_tasks'] = df.get('NumberOfInstancesWithMissingValues', df.get('n_tasks', 1)).fillna(1).astype(int)
    df = df[df['N_tasks'] >= 1].copy()
    print(f"  CSV fallback: N={len(df)} rows")
    return df


def filter_tagged_subset(df: pd.DataFrame) -> pd.DataFrame:
    df_tagged = df[df['has_tags'] == 1].copy()
    n = len(df_tagged)
    print(f"  Tagged subset (has_tags=1): N={n}")
    assert n > 500, f"Tagged subset too small: N={n}"
    return df_tagged


def derive_iv(df_tagged: pd.DataFrame) -> pd.DataFrame:
    if 'tag_count' not in df_tagged.columns:
        df_tagged['tag_count'] = df_tagged['tags'].apply(
            lambda x: str(x).count(',') + 1 if (pd.notna(x) and str(x).strip() != '') else 1
        )
    if 'log_tag_count_p1' not in df_tagged.columns:
        df_tagged['log_tag_count_p1'] = np.log(df_tagged['tag_count'] + 1)
    # Ensure tag_count >= 1 for all has_tags=1 rows
    assert (df_tagged['tag_count'] >= 1).all(), "tag_count < 1 found in tagged subset"
    print(f"  tag_count range: [{df_tagged['tag_count'].min()}, {df_tagged['tag_count'].max()}]")
    print(f"  log_tag_count_p1 range: [{df_tagged['log_tag_count_p1'].min():.4f}, {df_tagged['log_tag_count_p1'].max():.4f}]")
    return df_tagged


def validate_subset(df_tagged: pd.DataFrame) -> None:
    required = ['N_tasks', 'log_tag_count_p1', 'log_n_instances', 'log_n_features',
                'age_years', 'age_sq', 'decade', 'tag_count']
    missing = [c for c in required if c not in df_tagged.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    nan_counts = {c: df_tagged[c].isna().sum() for c in required}
    nans = {k: v for k, v in nan_counts.items() if v > 0}
    if nans:
        print(f"  WARNING: NaN counts: {nans}")
        for col in nans:
            df_tagged[col] = df_tagged[col].fillna(df_tagged[col].median())
    print(f"  Validation OK. Columns: {required}")
    print(f"  tag_count describe:\n{df_tagged['tag_count'].describe()}")
    print(f"  log_tag_count_p1 describe:\n{df_tagged['log_tag_count_p1'].describe()}")


def check_collinearity(df_tagged: pd.DataFrame) -> dict:
    decade_numeric = df_tagged['decade'].astype(int)
    rho, p_rho = spearmanr(df_tagged['log_tag_count_p1'], decade_numeric)
    decade_means = df_tagged.groupby('decade')['tag_count'].agg(['mean', 'median', 'count']).to_dict()
    print(f"  Spearman rho(log_tag_count_p1, decade)={rho:.3f}, p={p_rho:.3e}")
    print(f"  Mean tag_count by decade:\n{df_tagged.groupby('decade')['tag_count'].mean()}")
    return {'rho': float(rho), 'p_rho': float(p_rho), 'decade_means': str(decade_means)}


def main():
    print("=" * 60)
    print("H-M2 Step 01: Preprocess")
    print("=" * 60)

    print("\n[1] Loading H-E1 parquet...")
    df = load_h_e1_parquet()

    print("\n[2] Filter to has_tags=1 subset...")
    df_tagged = filter_tagged_subset(df)

    print("\n[3] Derive IV (log_tag_count_p1)...")
    df_tagged = derive_iv(df_tagged)

    print("\n[4] Validate subset...")
    validate_subset(df_tagged)

    print("\n[5] Collinearity check...")
    check_collinearity(df_tagged)

    print(f"\n[6] Saving to {OUT_PARQUET}...")
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df_tagged.to_parquet(OUT_PARQUET, index=False)
    print(f"  ✓ Saved tagged_subset.parquet (N={len(df_tagged)})")

    print("\n✅ Preprocessing complete")


if __name__ == "__main__":
    main()
