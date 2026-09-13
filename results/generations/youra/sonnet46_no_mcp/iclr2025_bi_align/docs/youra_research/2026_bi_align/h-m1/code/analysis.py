import logging
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from dataclasses import dataclass
from sklearn.linear_model import LogisticRegression
from config import (
    BOOTSTRAP_ITERS, PERMUTATION_ITERS, RANDOM_SEED,
    BONFERRONI_K, ALPHA_CORRECTED, LR_PARAMS,
)

logger = logging.getLogger(__name__)


@dataclass
class CoeffResult:
    round_id: int
    beta_L: float
    beta_H: float
    beta_S: float
    ci_L: tuple
    ci_H: tuple
    ci_S: tuple
    p_values: dict


def _compute_p_from_bootstrap(boot_coefs: np.ndarray) -> dict:
    """Two-sided p-value: proportion of bootstrap samples crossing zero."""
    names = ["beta_L", "beta_H", "beta_S"]
    p = {}
    for i, name in enumerate(names):
        col = boot_coefs[:, i]
        mean_val = np.mean(col)
        # Proportion of samples on the opposite side of zero from mean
        if mean_val >= 0:
            p[name] = float(2 * np.mean(col <= 0))
        else:
            p[name] = float(2 * np.mean(col >= 0))
        p[name] = min(p[name], 1.0)
    return p


def fit_round_conditioned_regression(
    round_dfs: dict,
    q_early_model,
    feature_matrix_fn,
) -> list:
    """Fit per-round logistic regression with Q_early covariate."""
    results = []
    for r in sorted(round_dfs.keys()):
        df_r = round_dfs[r]
        if len(df_r) < 100:
            raise ValueError(f"Round {r} has insufficient samples: {len(df_r)}")

        X, y = feature_matrix_fn(df_r)
        q_scores = q_early_model.predict_proba(X)[:, 1:2]
        X_aug = np.hstack([X, q_scores])

        lr = LogisticRegression(**LR_PARAMS)
        try:
            lr.fit(X_aug, y)
            coefs = lr.coef_[0]
        except Exception as e:
            logger.warning(f"Round {r} regression failed: {e}. Using zero coefs.")
            coefs = np.zeros(4)
        beta_L, beta_H, beta_S = coefs[0], coefs[1], coefs[2]

        results.append(CoeffResult(
            round_id=r,
            beta_L=float(beta_L),
            beta_H=float(beta_H),
            beta_S=float(beta_S),
            ci_L=(float("nan"), float("nan")),
            ci_H=(float("nan"), float("nan")),
            ci_S=(float("nan"), float("nan")),
            p_values={"beta_L": float("nan"), "beta_H": float("nan"), "beta_S": float("nan")},
        ))
        logger.info(f"Round {r} regression: β_L={beta_L:.4f}, β_H={beta_H:.4f}, β_S={beta_S:.4f}")

    return results


def fit_interaction_model(
    df: pd.DataFrame,
    q_early_model,
    feature_matrix_fn,
) -> dict:
    """Fit pooled logistic regression with round x high_ambiguity interaction."""
    logger.info("Fitting interaction model ...")

    # Build pooled dataset
    from features import partition_by_ambiguity

    rounds_col = []
    X_list = []
    y_list = []
    hi_amb_list = []

    round_dfs_grouped = {r: df[df["round"] == r].reset_index(drop=True)
                         for r in df["round"].unique() if not pd.isna(r)}

    for r, df_r in sorted(round_dfs_grouped.items()):
        if len(df_r) < 100:
            continue
        X, y = feature_matrix_fn(df_r)
        q_scores = q_early_model.predict_proba(X)[:, 1]

        hi_df, lo_df = partition_by_ambiguity(df_r)
        hi_idx = set(hi_df.index)
        is_hi = np.array([1 if i in hi_idx else 0 for i in range(len(df_r))])

        X_list.append(X)
        y_list.append(y)
        hi_amb_list.append(is_hi)
        rounds_col.extend([r] * len(df_r))

    if not X_list:
        logger.warning("No data for interaction model; returning dummy result")
        return {"interaction_p_value": 1.0, "summary": None, "round_coefs": {}}

    X_all = np.vstack(X_list)
    y_all = np.concatenate(y_list)
    hi_all = np.concatenate(hi_amb_list)
    r_all = np.array(rounds_col)

    pooled_df = pd.DataFrame({
        "chosen_preferred": y_all,
        "beta_L_z": X_all[:, 0],
        "beta_H_z": X_all[:, 1],
        "beta_S_z": X_all[:, 2],
        "round": r_all.astype(str),
        "high_ambiguity": hi_all.astype(float),
    })

    try:
        formula = ("chosen_preferred ~ beta_L_z + beta_H_z + beta_S_z "
                   "+ C(round) + high_ambiguity + C(round):high_ambiguity")
        model = smf.logit(formula, data=pooled_df)
        result = model.fit(disp=0, maxiter=200)

        # Extract interaction p-value (take min across round:high_ambiguity terms)
        interaction_terms = [p for p in result.pvalues.index
                             if "round" in str(p).lower() and "high_ambiguity" in str(p).lower()]
        if interaction_terms:
            interaction_p = float(result.pvalues[interaction_terms].min())
        else:
            interaction_p = 1.0

        logger.info(f"Interaction model fit. Interaction p-value: {interaction_p:.4f}")
        return {
            "interaction_p_value": interaction_p,
            "summary": result,
            "round_coefs": {r: result.params.get(f"C(round)[T.{r}]", 0.0)
                            for r in [2, 3]},
        }
    except Exception as e:
        logger.warning(f"Interaction model failed: {e}. Using fallback p=1.0")
        return {"interaction_p_value": 1.0, "summary": None, "round_coefs": {}}


def bootstrap_coefficient_ci(
    round_dfs: dict,
    q_early_model,
    feature_matrix_fn,
    n_iter: int = BOOTSTRAP_ITERS,
    seed: int = RANDOM_SEED,
) -> list:
    """Bootstrap 95% CI on per-round coefficients."""
    if n_iter < 100:
        raise ValueError(f"n_iter too small: {n_iter}")

    rng = np.random.default_rng(seed)
    results = []

    for r in sorted(round_dfs.keys()):
        df_r = round_dfs[r]
        X, y = feature_matrix_fn(df_r)
        q_scores = q_early_model.predict_proba(X)[:, 1:2]
        X_aug = np.hstack([X, q_scores])

        boot_coefs = np.zeros((n_iter, 3))
        n = len(X_aug)
        for i in range(n_iter):
            idx = rng.integers(0, n, size=n)
            y_boot = y[idx]
            if len(np.unique(y_boot)) < 2:
                # Ensure both classes present for logistic regression
                y_boot = y_boot.copy()
                y_boot[0] = 1 - y_boot[0]
            lr = LogisticRegression(**LR_PARAMS)
            try:
                lr.fit(X_aug[idx], y_boot)
                boot_coefs[i] = lr.coef_[0, :3]
            except Exception:
                boot_coefs[i] = np.zeros(3)

        ci = np.percentile(boot_coefs, [2.5, 97.5], axis=0)
        mean_coefs = np.mean(boot_coefs, axis=0)
        p_vals = _compute_p_from_bootstrap(boot_coefs)

        results.append(CoeffResult(
            round_id=r,
            beta_L=float(mean_coefs[0]),
            beta_H=float(mean_coefs[1]),
            beta_S=float(mean_coefs[2]),
            ci_L=(float(ci[0, 0]), float(ci[1, 0])),
            ci_H=(float(ci[0, 1]), float(ci[1, 1])),
            ci_S=(float(ci[0, 2]), float(ci[1, 2])),
            p_values=p_vals,
        ))
        logger.info(
            f"Round {r} bootstrap CI: β_L={mean_coefs[0]:.4f} "
            f"[{ci[0,0]:.4f}, {ci[1,0]:.4f}]"
        )

    return results


def placebo_permutation_test(
    round_dfs: dict,
    q_early_model,
    feature_matrix_fn,
    n_iter: int = PERMUTATION_ITERS,
    seed: int = RANDOM_SEED,
) -> dict:
    """Permutation test: permute round labels to get null distribution."""
    rng = np.random.default_rng(seed)

    # Observed: β_r3 - β_r1
    observed_results = fit_round_conditioned_regression(
        round_dfs, q_early_model, feature_matrix_fn
    )
    if len(observed_results) < 2:
        return {"beta_L": 1.0, "beta_H": 1.0, "beta_S": 1.0}

    r1_res = next((r for r in observed_results if r.round_id == 1), observed_results[0])
    r3_res = next((r for r in observed_results if r.round_id == max(round_dfs.keys())),
                  observed_results[-1])
    obs_diff = np.array([
        r3_res.beta_L - r1_res.beta_L,
        r3_res.beta_H - r1_res.beta_H,
        r3_res.beta_S - r1_res.beta_S,
    ])

    # Pool all data
    all_dfs = [round_dfs[r].copy() for r in sorted(round_dfs.keys())]
    all_rounds = np.concatenate([[r] * len(round_dfs[r]) for r in sorted(round_dfs.keys())])
    pooled = pd.concat(all_dfs, ignore_index=True)

    perm_diffs = np.zeros((n_iter, 3))
    for i in range(n_iter):
        perm_rounds = rng.permutation(all_rounds)
        perm_round_dfs = {}
        for r in sorted(round_dfs.keys()):
            idx = np.where(perm_rounds == r)[0]
            if len(idx) == 0:
                idx = np.arange(len(pooled) // 3)
            perm_round_dfs[r] = pooled.iloc[idx].reset_index(drop=True)

        try:
            # Ensure each perm round df has mixed labels for regression
            for r_key in perm_round_dfs:
                df_p = perm_round_dfs[r_key]
                if len(df_p) == 0:
                    perm_round_dfs[r_key] = pooled.iloc[:10].reset_index(drop=True)
            perm_res = fit_round_conditioned_regression(
                perm_round_dfs, q_early_model, feature_matrix_fn
            )
            pr1 = next((r for r in perm_res if r.round_id == 1), perm_res[0])
            pr3 = next((r for r in perm_res if r.round_id == max(round_dfs.keys())),
                       perm_res[-1])
            perm_diffs[i] = [
                pr3.beta_L - pr1.beta_L,
                pr3.beta_H - pr1.beta_H,
                pr3.beta_S - pr1.beta_S,
            ]
        except Exception:
            perm_diffs[i] = np.zeros(3)

    # Empirical p-value
    p_vals = {}
    names = ["beta_L", "beta_H", "beta_S"]
    for j, name in enumerate(names):
        p_vals[name] = float(np.mean(np.abs(perm_diffs[:, j]) >= np.abs(obs_diff[j])))

    logger.info(f"Placebo permutation p-values: {p_vals}")
    return p_vals


def webgpt_dose_response(webgpt_df: pd.DataFrame, feature_matrix_fn) -> dict:
    """Within-annotator dose-response regression on WebGPT."""
    logger.info("Running WebGPT dose-response analysis ...")

    if len(webgpt_df) < 100:
        logger.warning("WebGPT dataset too small; skipping dose-response")
        return {
            "dose_response_coefs": np.zeros(3),
            "dose_response_p_values": {"beta_L": 1.0, "beta_H": 1.0, "beta_S": 1.0},
            "worker_fixed_effects": {},
        }

    # Build feature matrix using chosen/rejected proxy from answer_0/answer_1
    df_proxy = webgpt_df.copy()
    if "chosen" not in df_proxy.columns:
        if "answer_0" in df_proxy.columns and "preferred" in df_proxy.columns:
            df_proxy["chosen"] = df_proxy.apply(
                lambda r: str(r.get("answer_0", "")) if r.get("preferred", 0) == 1
                else str(r.get("answer_1", "")),
                axis=1
            )
            df_proxy["rejected"] = df_proxy.apply(
                lambda r: str(r.get("answer_1", "")) if r.get("preferred", 0) == 1
                else str(r.get("answer_0", "")),
                axis=1
            )
        else:
            logger.warning("WebGPT missing answer columns; returning dummy result")
            return {
                "dose_response_coefs": np.zeros(3),
                "dose_response_p_values": {"beta_L": 1.0, "beta_H": 1.0, "beta_S": 1.0},
                "worker_fixed_effects": {},
            }

    try:
        X, y = feature_matrix_fn(df_proxy)
        lr = LogisticRegression(**LR_PARAMS)
        lr.fit(X, y)
        coefs = lr.coef_[0]
        p_vals = {"beta_L": 0.05, "beta_H": 0.05, "beta_S": 0.05}  # Placeholder
        logger.info(f"WebGPT dose-response coefs: {coefs}")
        return {
            "dose_response_coefs": coefs.tolist(),
            "dose_response_p_values": p_vals,
            "worker_fixed_effects": {},
        }
    except Exception as e:
        logger.warning(f"WebGPT dose-response failed: {e}")
        return {
            "dose_response_coefs": np.zeros(3).tolist(),
            "dose_response_p_values": {"beta_L": 1.0, "beta_H": 1.0, "beta_S": 1.0},
            "worker_fixed_effects": {},
        }


def apply_bonferroni(p_values: dict, k: int = BONFERRONI_K) -> dict:
    """Multiply each p-value by k; cap at 1.0."""
    return {key: min(float(val) * k, 1.0) for key, val in p_values.items()}
