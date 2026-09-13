"""H-M1 propensity score matching: logistic PS model, 1:N NN matching, SMD."""
import numpy as np
import pandas as pd
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def fit_propensity_model(
    survival_df: pd.DataFrame,
    covariate_cols: list,
    treatment_col: str,
    seed: int,
) -> tuple:
    """Fit LogisticRegression propensity model.
    Returns: (fitted_model, propensity_scores: np.ndarray shape [N])
    """
    X = survival_df[covariate_cols].copy().fillna(0)
    y = survival_df[treatment_col].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = LogisticRegression(max_iter=500, random_state=seed, solver="lbfgs")
    model.fit(X_scaled, y)
    ps = model.predict_proba(X_scaled)[:, 1]
    ps = np.clip(ps, 1e-6, 1 - 1e-6)
    logger.info(f"PS model: AUC approx, ps range [{ps.min():.3f}, {ps.max():.3f}]")
    return model, ps


def nearest_neighbor_match(
    survival_df: pd.DataFrame,
    ps_scores: np.ndarray,
    treatment_col: str,
    caliper: float,
    ratio: int = 1,
) -> pd.DataFrame:
    """1:ratio nearest-neighbor matching with caliper on logit(ps_scores).
    Returns: matched_df with pair_id; len = (ratio+1) * n_matched_pairs
    """
    df = survival_df.reset_index(drop=True).copy()
    logit_ps = np.log(ps_scores / (1 - ps_scores))
    treated_mask = df[treatment_col] == 1
    control_mask = df[treatment_col] == 0
    treated_idx = df.index[treated_mask].tolist()
    control_idx = df.index[control_mask].tolist()
    if len(control_idx) == 0 or len(treated_idx) == 0:
        logger.warning("No treated or control units found")
        return df.iloc[[]].assign(pair_id=pd.Series(dtype=int))
    logit_control = logit_ps[control_mask].reshape(-1, 1)
    logit_treated = logit_ps[treated_mask].reshape(-1, 1)
    nn = NearestNeighbors(n_neighbors=min(ratio, len(control_idx)), metric="euclidean")
    nn.fit(logit_control)
    distances, nn_indices = nn.kneighbors(logit_treated)
    matched_rows = []
    used_controls = set()
    pair_id = 0
    for i, (t_pos, dists, ctrl_positions) in enumerate(zip(range(len(treated_idx)), distances, nn_indices)):
        t_idx = treated_idx[i]
        controls_added = 0
        for d, c_pos in zip(dists, ctrl_positions):
            c_idx = control_idx[c_pos]
            if d <= caliper and c_idx not in used_controls:
                matched_rows.append({**df.loc[t_idx].to_dict(), "pair_id": pair_id})
                matched_rows.append({**df.loc[c_idx].to_dict(), "pair_id": pair_id})
                used_controls.add(c_idx)
                controls_added += 1
                if controls_added >= ratio:
                    break
        if controls_added > 0:
            pair_id += 1
    if not matched_rows:
        logger.warning("No matched pairs found within caliper")
        return df.iloc[[]].assign(pair_id=pd.Series(dtype=int))
    matched_df = pd.DataFrame(matched_rows).reset_index(drop=True)
    logger.info(f"Matched {pair_id} pairs (caliper={caliper:.4f})")
    return matched_df


def compute_smd(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    covariate_cols: list,
    treatment_col: str,
) -> pd.DataFrame:
    """Compute SMD before and after matching for each covariate."""
    records = []
    for col in covariate_cols:
        for df, label in [(df_before, "before"), (df_after, "after")]:
            treated = df[df[treatment_col] == 1][col].dropna()
            control = df[df[treatment_col] == 0][col].dropna()
            pooled_sd = np.sqrt((treated.var() + control.var()) / 2)
            smd = abs(treated.mean() - control.mean()) / pooled_sd if pooled_sd > 0 else 0.0
            records.append({"covariate": col, "phase": label, "smd": smd})
    pivot = pd.DataFrame(records).pivot(index="covariate", columns="phase", values="smd").reset_index()
    pivot.columns.name = None
    pivot = pivot.rename(columns={"before": "smd_before", "after": "smd_after"})
    return pivot[["covariate", "smd_before", "smd_after"]]


def run_matching(
    survival_df: pd.DataFrame,
    cfg,
    caliper_factor: float = None,
    ratio: int = 1,
) -> tuple:
    """Full matching pipeline: fit PS → match → compute SMD → validate balance.
    Returns: (matched_df, smd_df, matching_meta: dict)
    """
    covariate_cols = ["creation_year_quartile", "task_type_encoded", "size_decile"]
    available_covs = [c for c in covariate_cols if c in survival_df.columns]
    seed = getattr(cfg, "SEED", 42)
    treatment_col = "high_findable"
    model, ps_scores = fit_propensity_model(survival_df, available_covs, treatment_col, seed)
    logit_ps = np.log(ps_scores / (1 - ps_scores))
    ps_sd = logit_ps.std()
    cf = caliper_factor if caliper_factor is not None else getattr(cfg, "CALIPER_FACTOR", 0.2)
    caliper = cf * ps_sd
    matched_df = nearest_neighbor_match(survival_df, ps_scores, treatment_col, caliper, ratio)
    n_matched_pairs = len(matched_df) // (ratio + 1) if len(matched_df) > 0 else 0
    smd_df = compute_smd(survival_df, matched_df, available_covs, treatment_col) if len(matched_df) > 0 else pd.DataFrame()
    smd_max = float(smd_df["smd_after"].max()) if len(smd_df) > 0 else float("nan")
    smd_threshold = getattr(cfg, "SMD_THRESHOLD", 0.1)
    min_pairs = getattr(cfg, "MIN_MATCHED_PAIRS", 100)
    balance_ok = smd_max < smd_threshold if not np.isnan(smd_max) else False
    if not balance_ok:
        logger.warning(f"SMD imbalance: max SMD={smd_max:.3f} > threshold {smd_threshold}")
    if n_matched_pairs < min_pairs:
        logger.warning(f"Insufficient matched pairs: {n_matched_pairs} < {min_pairs}")
    matching_meta = {
        "n_matched_pairs": n_matched_pairs,
        "smd_max": smd_max,
        "caliper_used": caliper,
        "ps_sd": ps_sd,
        "balance_ok": balance_ok,
        "caliper_factor": cf,
    }
    # Add propensity scores to survival_df for visualization
    survival_df = survival_df.copy()
    survival_df["propensity_score"] = ps_scores
    if len(matched_df) > 0 and "propensity_score" not in matched_df.columns:
        matched_df["propensity_score"] = np.nan
    return matched_df, smd_df, matching_meta
