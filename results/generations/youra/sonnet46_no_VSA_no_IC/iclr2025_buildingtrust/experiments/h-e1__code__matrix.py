"""Model name standardization and matrix construction."""
import logging
from typing import Optional
import pandas as pd
from .config import CANONICAL_MAP, REQUIRED_COLS, SOURCE_PRIORITY

_UNMAPPED: set[str] = set()


def standardize_model_name(raw_name: str) -> str:
    """Map raw model name variant to canonical ID using CANONICAL_MAP."""
    key = raw_name.lower().strip()
    result = CANONICAL_MAP.get(key)
    if result is None:
        if key not in _UNMAPPED:
            logging.warning(f"Unmapped model name: '{raw_name}' — add to CANONICAL_MAP if needed")
            _UNMAPPED.add(key)
        return raw_name.strip()
    return result


def build_matrix(
    score_dicts: dict[str, dict[str, dict[str, float]]]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build model × benchmark score matrix from multi-source score dicts.

    Args:
        score_dicts: {source_name: {canonical_model: {benchmark: float}}}

    Returns:
        matrix_df: model × REQUIRED_COLS, NaN for missing cells
        attribution_df: same shape, values = source name that filled cell
    """
    all_models: set[str] = set()
    for src_data in score_dicts.values():
        all_models.update(src_data.keys())
    all_models_sorted = sorted(all_models)

    matrix_rows = []
    attribution_rows = []

    for model in all_models_sorted:
        row: dict = {}
        attr_row: dict = {}
        for col in REQUIRED_COLS:
            filled = False
            for src in SOURCE_PRIORITY:
                if src not in score_dicts:
                    continue
                val = score_dicts[src].get(model, {}).get(col)
                if val is not None:
                    row[col] = float(val)
                    attr_row[col] = src
                    filled = True
                    break
            if not filled:
                row[col] = float("nan")
                attr_row[col] = None
        matrix_rows.append({"model": model, **row})
        attribution_rows.append({"model": model, **attr_row})

    matrix_df = pd.DataFrame(matrix_rows).set_index("model")
    attribution_df = pd.DataFrame(attribution_rows).set_index("model")
    return matrix_df, attribution_df
