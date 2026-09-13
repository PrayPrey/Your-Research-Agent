"""scorer.py — DTS-Weighted Documentation Completeness Scorer for H-E1."""
import numpy as np
import pandas as pd
from typing import Optional

DTS_SECTIONS: dict[str, list[str]] = {
    "motivation":    ["task_categories", "language", "tags", "license"],
    "composition":   ["size_categories", "num_rows", "num_columns", "features"],
    "collection":    ["source_datasets", "annotations_creators", "original_data_url"],
    "preprocessing": ["preprocessing_steps", "data_augmentation", "data_splits"],
    "uses":          ["known_limitations", "out_of_scope_use", "discussion_best_use"],
    "distribution":  ["license", "citation", "contact", "maintenance_plan"],
}

DTS_WEIGHTS: dict[str, float] = {
    "motivation": 1.0,
    "composition": 0.9,
    "collection": 2.1,
    "preprocessing": 1.8,
    "uses": 1.5,
    "distribution": 0.7,
}

_WEIGHT_SUM = sum(DTS_WEIGHTS.values())  # 8.0


def _is_present(value) -> bool:
    """Return True if value is a non-empty, non-None, non-zero value.

    For binary field columns (0/1 integers), 0 means absent and 1 means present.
    For raw metadata dicts, None/empty string/empty list means absent.
    """
    if value is None:
        return False
    # Binary integer encoding: 0 = absent, 1 = present
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return bool(value)
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, dict, set)) and len(value) == 0:
        return False
    if isinstance(value, str) and value.strip() in ("", "nan", "None", "none", "null"):
        return False
    return True


def compute_dts_score(metadata: dict) -> tuple[float, dict[str, float]]:
    """Compute weighted DTS score from metadata field presence.

    Args:
        metadata: dict mapping field names to values (may be None/empty).

    Returns:
        (weighted_score in [0,1], {section_name: coverage_rate})
    """
    section_coverages: dict[str, float] = {}
    for section, fields in DTS_SECTIONS.items():
        if not fields:
            section_coverages[section] = 0.0
            continue
        present = sum(1 for f in fields if _is_present(metadata.get(f)))
        section_coverages[section] = present / len(fields)

    weighted_score = sum(
        DTS_WEIGHTS[s] * section_coverages[s] for s in DTS_SECTIONS
    ) / _WEIGHT_SUM

    return (weighted_score, section_coverages)


def compute_unweighted_score(metadata: dict) -> float:
    """Naive coverage: present_fields / total_fields across all sections.

    Returns:
        Scalar in [0, 1].
    """
    all_fields = [f for fields in DTS_SECTIONS.values() for f in fields]
    if not all_fields:
        return 0.0
    present = sum(1 for f in all_fields if _is_present(metadata.get(f)))
    return present / len(all_fields)


def score_corpus(df: pd.DataFrame) -> pd.DataFrame:
    """Apply compute_dts_score and compute_unweighted_score to each row.

    Adds columns: weighted_dts_score, unweighted_dts_score, per_section_{name}.

    Args:
        df: DataFrame where each row is one dataset with field-presence columns.

    Returns:
        Augmented DataFrame with scoring columns added.
    """
    df = df.copy()

    scores = []
    section_scores: dict[str, list[float]] = {s: [] for s in DTS_SECTIONS}
    unweighted_scores = []

    for _, row in df.iterrows():
        metadata = row.to_dict()
        weighted, coverages = compute_dts_score(metadata)
        scores.append(weighted)
        unweighted_scores.append(compute_unweighted_score(metadata))
        for section in DTS_SECTIONS:
            section_scores[section].append(coverages.get(section, 0.0))

    df["weighted_dts_score"] = scores
    df["unweighted_dts_score"] = unweighted_scores
    for section in DTS_SECTIONS:
        df[f"per_section_{section}"] = section_scores[section]

    return df


def compute_coverage_rate(
    df: pd.DataFrame,
    repo: Optional[str] = None,
) -> float:
    """Fraction of datasets with weighted_dts_score > 0.

    Args:
        df: Scored DataFrame with 'weighted_dts_score' and optionally 'repository'.
        repo: If given, filter to rows where df['repository'] == repo.

    Returns:
        Float in [0, 1].
    """
    if repo is not None:
        subset = df[df["repository"] == repo]
    else:
        subset = df

    if len(subset) == 0:
        return 0.0

    return float((subset["weighted_dts_score"] > 0).mean())
