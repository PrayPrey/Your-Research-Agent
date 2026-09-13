"""Load H-E1 artifacts and derive PC1 scores via projection."""

import json
import numpy as np
import pandas as pd
from pathlib import Path


def load_pc1_scores(
    resid_csv: str = "../../h-e1/outputs/residualized_matrix.csv",
    results_json: str = "../../h-e1/outputs/h_e1_results.json",
) -> pd.DataFrame:
    """
    Derive PC1 scores via projection onto H-E1 loadings.

    Returns:
        DataFrame with columns [model_name, pc1_score]
    """
    resid_path = Path(resid_csv)
    json_path = Path(results_json)

    if not resid_path.exists():
        raise FileNotFoundError(f"H-E1 residualized matrix not found: {resid_path}")
    if not json_path.exists():
        raise FileNotFoundError(f"H-E1 results JSON not found: {json_path}")

    Y_resid_df = pd.read_csv(resid_path, index_col=0)

    with open(json_path, "r") as f:
        results = json.load(f)

    loadings_dict = results["pca"]["loadings_pc1"]
    loadings = np.array([loadings_dict[b] for b in Y_resid_df.columns])

    assert np.all(loadings > 0), "Expected all loadings positive (H-E1 validated)"

    pc1_scores = Y_resid_df.values @ loadings

    return pd.DataFrame({
        "model_name": Y_resid_df.index.tolist(),
        "pc1_score": pc1_scores.tolist()
    })


if __name__ == "__main__":
    df = load_pc1_scores()
    print(f"Loaded {len(df)} models with PC1 scores")
    print(df.head())
