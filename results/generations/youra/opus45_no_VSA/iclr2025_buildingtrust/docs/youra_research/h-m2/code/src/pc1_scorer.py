"""PC1 scorer: residualize benchmark scores and extract PC1."""
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import statsmodels.api as sm

BENCHMARKS = ["truthfulqa", "mmlu", "advglue", "bbh", "gsm8k", "winogrande"]
SEED = 42


def load_benchmark_scores(model_ids: list[str], benchmark_data: pd.DataFrame) -> pd.DataFrame:
    df = benchmark_data[benchmark_data["model_id"].isin(model_ids)].copy()
    missing = set(model_ids) - set(df["model_id"])
    if missing:
        raise ValueError(f"Missing benchmark scores for: {missing}")
    return df


def residualize(Y: np.ndarray, X: np.ndarray) -> np.ndarray:
    Y_resid = np.zeros_like(Y)
    X_const = sm.add_constant(X)
    for i in range(Y.shape[1]):
        model = sm.OLS(Y[:, i], X_const).fit()
        Y_resid[:, i] = model.resid
    return Y_resid


def compute_pc1(df: pd.DataFrame) -> pd.Series:
    Y = df[BENCHMARKS].values
    Y = (Y - Y.mean(axis=0)) / Y.std(axis=0)
    X = df[["log_params", "release_date"]].values
    Y_resid = residualize(Y, X)
    pca = PCA(n_components=1, random_state=SEED)
    pc1 = pca.fit_transform(Y_resid).flatten()
    return pd.Series(pc1, index=df["model_id"])
