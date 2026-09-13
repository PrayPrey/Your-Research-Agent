"""PCA analysis for H-M3 (3-benchmark distinctness)."""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


def run_pca_analysis(
    df: pd.DataFrame,
    benchmark_cols: list[str] = None,
) -> dict:
    """Run PCA to verify FactScore loads on different component.

    Returns loadings, explained variance, and components needed for 80%.
    """
    if benchmark_cols is None:
        benchmark_cols = ["factscore", "truthfulqa_mc2", "halueval_agg"]

    X = df[benchmark_cols].dropna().values
    n_components = min(3, len(benchmark_cols), X.shape[0])

    # Standardize
    X_std = StandardScaler().fit_transform(X)

    # Fit PCA
    pca = PCA(n_components=n_components)
    pca.fit(X_std)

    # Components needed for 80% variance
    cum_var = np.cumsum(pca.explained_variance_ratio_)
    n_80 = int(np.searchsorted(cum_var, 0.80) + 1)

    return {
        "loadings": pca.components_.tolist(),
        "explained_variance": pca.explained_variance_ratio_.tolist(),
        "cumulative_variance": cum_var.tolist(),
        "n_components_80pct": min(n_80, n_components),
        "benchmark_cols": benchmark_cols,
    }


def interpret_pca(pca_result: dict) -> dict:
    """Interpret PCA results for mechanism verification."""
    loadings = np.array(pca_result["loadings"])
    cols = pca_result["benchmark_cols"]
    n_80 = pca_result["n_components_80pct"]

    interpretation = {
        "multi_dimensional": n_80 >= 2,
        "dominant_component": int(np.argmax(pca_result["explained_variance"])),
        "component_interpretation": [],
    }

    # Identify which benchmarks load heavily on each component
    for i, row in enumerate(loadings):
        dominant_idx = int(np.argmax(np.abs(row)))
        interpretation["component_interpretation"].append({
            "component": i + 1,
            "variance_explained": pca_result["explained_variance"][i],
            "dominant_benchmark": cols[dominant_idx],
            "loadings": {cols[j]: float(row[j]) for j in range(len(cols))},
        })

    return interpretation
