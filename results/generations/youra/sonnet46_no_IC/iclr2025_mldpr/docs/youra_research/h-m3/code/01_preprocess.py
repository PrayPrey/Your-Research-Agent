"""H-M3: Load H-E1 parquet, derive tag_count_cat bins, verify controls."""
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H_E1_PARQUET = os.path.join(os.path.dirname(BASE_DIR), 'h-e1', 'results', 'preprocessed.parquet')
H_E1_CSV_FALLBACK = os.path.join(os.path.dirname(BASE_DIR), 'h-e1', 'code', 'data', 'h_e1', 'openml_dataset_corpus.csv')
EXPECTED_N = 5217
BIN_BREAKS = [-1, 0, 2, 5, float('inf')]
BIN_LABELS = ["0", "1-2", "3-5", "6+"]
OUTPUT_DIR = os.path.join(BASE_DIR, 'results')


def load_corpus():
    if os.path.exists(H_E1_PARQUET):
        df = pd.read_parquet(H_E1_PARQUET)
        print(f"Loaded parquet: N={len(df)}")
    else:
        print(f"Parquet not found, loading CSV fallback: {H_E1_CSV_FALLBACK}")
        df = pd.read_csv(H_E1_CSV_FALLBACK)
        df = df[df['number_of_tasks'] >= 1].copy()
        df = df.rename(columns={'number_of_tasks': 'N_tasks'})
        print(f"Loaded CSV fallback: N={len(df)}")

    assert len(df) >= 5000, f"Unexpected corpus size: {len(df)}"
    return df


def derive_tag_count(df):
    if 'tag_count' not in df.columns:
        def count_tags(x):
            if pd.isna(x) or str(x).strip() in ('', 'nan', '[]', 'None'):
                return 0
            s = str(x).strip().strip('[]')
            if not s:
                return 0
            return int(s.count(',') + 1)
        df['tag_count'] = df['tags'].apply(count_tags)
        print(f"Derived tag_count: min={df['tag_count'].min()}, max={df['tag_count'].max()}")
    else:
        print(f"tag_count already in parquet: min={df['tag_count'].min()}, max={df['tag_count'].max()}")
    return df


def derive_bins(df):
    df['tag_count_cat'] = pd.cut(
        df['tag_count'],
        bins=BIN_BREAKS,
        labels=BIN_LABELS
    ).astype(str)
    bin_counts = df['tag_count_cat'].value_counts().sort_index()
    print("Tag count category distribution:")
    print(bin_counts)
    assert (bin_counts > 0).all(), "Some bins are empty"
    return df, bin_counts


def verify_controls(df):
    controls_needed = ['log_n_instances', 'log_n_features', 'age_years', 'age_sq', 'decade']
    for col in controls_needed:
        if col not in df.columns:
            raise ValueError(f"Missing control: {col}. Re-run H-E1 preprocessing.")
        nan_count = df[col].isna().sum()
        if nan_count > 0:
            print(f"Warning: {nan_count} NaN in {col} — dropping affected rows")
            df = df.dropna(subset=controls_needed)
    print(f"N after controls check: {len(df)}")
    return df


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_corpus()
    df = derive_tag_count(df)
    df, bin_counts = derive_bins(df)
    df = verify_controls(df)

    out_path = os.path.join(OUTPUT_DIR, 'preprocessed_m3.parquet')
    df.to_parquet(out_path, index=False)
    print(f"Saved preprocessed data: {out_path} (N={len(df)})")

    bin_counts.to_csv(os.path.join(OUTPUT_DIR, 'bin_counts.csv'))
    print("Preprocessing complete.")
    return df, bin_counts


if __name__ == '__main__':
    main()
