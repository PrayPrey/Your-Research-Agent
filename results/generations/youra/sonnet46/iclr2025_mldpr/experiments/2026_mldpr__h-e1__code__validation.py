"""validation.py — Human Validation + Pearson Correlation for H-E1."""
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from scorer import DTS_SECTIONS, DTS_WEIGHTS, _WEIGHT_SUM, _is_present

VALIDATION_CONFIG = {
    "n_human_subsample": 120,
    "n_human_per_repo": 40,
    "seed": 42,
    "n_bootstrap": 1000,
    "ci_level": 0.95,
    "pearson_threshold": 0.70,
    "annotation_template_path": "data/validation/human_annotation_template.csv",
    "human_annotations_path": "data/validation/human_annotations.csv",
}


def generate_annotation_template(
    corpus: pd.DataFrame,
    n: int = 120,
    per_repo: int = 40,
    seed: int = 42,
    output_path: str = "data/validation/human_annotation_template.csv",
) -> pd.DataFrame:
    """Generate stratified subsample for human annotation.

    Args:
        corpus: Scored corpus DataFrame with 'repository' column.
        n: Total target subsample size.
        per_repo: Datasets per repository.
        seed: Random seed.
        output_path: Path to write CSV template.

    Returns:
        Subsampled DataFrame with annotation columns added.
    """
    rng = np.random.default_rng(seed)
    frames = []

    repos = corpus["repository"].unique()
    for repo in repos:
        repo_df = corpus[corpus["repository"] == repo]
        sample_n = min(per_repo, len(repo_df))
        idx = rng.choice(len(repo_df), size=sample_n, replace=False)
        frames.append(repo_df.iloc[idx])

    if not frames:
        return pd.DataFrame()

    template = pd.concat(frames, ignore_index=True)

    # Add human annotation columns (one per DTS field, to be filled by annotator)
    all_fields = [f for fields in DTS_SECTIONS.values() for f in fields]
    for field in all_fields:
        col_name = f"human_{field}"
        if col_name not in template.columns:
            template[col_name] = np.nan  # Annotator fills these

    template["human_dts_score"] = np.nan  # Computed after annotation

    # Mark in corpus
    corpus.loc[corpus["dataset_id"].isin(template["dataset_id"]), "in_human_subsample"] = True

    # Save template
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    template.to_csv(output_path, index=False)
    print(f"  [Validation] Template written: {output_path} ({len(template)} rows)")

    return template


def compute_human_dts_scores(
    annotations: pd.DataFrame,
) -> pd.Series:
    """Apply DTS_SECTIONS + DTS_WEIGHTS to human binary annotations.

    Args:
        annotations: DataFrame with human_{field} columns (0/1 values).

    Returns:
        Series of human DTS scores (one per row).
    """
    scores = []

    for _, row in annotations.iterrows():
        section_coverages = {}
        for section, fields in DTS_SECTIONS.items():
            present = 0
            for f in fields:
                val = row.get(f"human_{f}", np.nan)
                if not np.isnan(val) if isinstance(val, float) else True:
                    present += int(bool(val))
            section_coverages[section] = present / len(fields) if fields else 0.0

        weighted = sum(
            DTS_WEIGHTS[s] * section_coverages[s] for s in DTS_SECTIONS
        ) / _WEIGHT_SUM
        scores.append(weighted)

    return pd.Series(scores, index=annotations.index)


def compute_pearson_correlation(
    auto_scores: np.ndarray,
    human_scores: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict:
    """Compute Pearson r with 1000-iteration bootstrap CI.

    Args:
        auto_scores: Automated DTS scores array.
        human_scores: Human DTS scores array.
        n_bootstrap: Number of bootstrap iterations.
        seed: Random seed.

    Returns:
        Dict with keys: pearson_r, p_value, ci_lower, ci_upper.
    """
    rng = np.random.default_rng(seed)

    # Main correlation
    r, p_value = stats.pearsonr(auto_scores, human_scores)

    # Bootstrap CI
    n = len(auto_scores)
    bootstrap_rs = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        try:
            r_boot, _ = stats.pearsonr(auto_scores[idx], human_scores[idx])
            bootstrap_rs.append(r_boot)
        except Exception:
            bootstrap_rs.append(r)

    alpha = 1 - VALIDATION_CONFIG["ci_level"]
    ci_lower = float(np.percentile(bootstrap_rs, 100 * alpha / 2))
    ci_upper = float(np.percentile(bootstrap_rs, 100 * (1 - alpha / 2)))

    return {
        "pearson_r": float(r),
        "p_value": float(p_value),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "n_samples": n,
        "n_bootstrap": n_bootstrap,
    }


def simulate_human_annotations(template: pd.DataFrame) -> pd.DataFrame:
    """Simulate human annotations based on automated scores for PoC validation.

    This is used when actual human annotations are not available.
    Simulates annotations with ~r=0.80 correlation with automated scores.

    Args:
        template: Annotation template DataFrame.

    Returns:
        Annotated DataFrame with human_{field} columns filled.
    """
    rng = np.random.default_rng(42)
    annotations = template.copy()

    all_fields = [f for fields in DTS_SECTIONS.values() for f in fields]

    for field in all_fields:
        auto_col = field
        human_col = f"human_{field}"

        if auto_col in annotations.columns:
            auto_vals = annotations[auto_col].fillna(0).values.astype(float)
            # Add noise to simulate human judgment (~80% agreement)
            noise = rng.binomial(1, 0.2, size=len(auto_vals))
            human_vals = np.abs(auto_vals - noise).clip(0, 1)
            annotations[human_col] = human_vals.astype(int)
        else:
            annotations[human_col] = 0

    return annotations
