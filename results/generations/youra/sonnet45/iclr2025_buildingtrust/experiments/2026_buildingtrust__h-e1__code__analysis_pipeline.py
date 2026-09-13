"""Statistical analysis pipeline: margin, flip, KL, logistic regression, AUROC."""

import numpy as np
from scipy.stats import zscore
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import statsmodels.api as sm
import warnings


def compute_margin_and_flip(
    base_logprobs: np.ndarray,    # [n, 4]
    aligned_logprobs: np.ndarray, # [n, 4]
) -> tuple[np.ndarray, np.ndarray]:
    """Compute z-scored top1-top2 margin and argmax flip indicator.

    Returns:
        margin_z: (n,) z-scored confidence margin from base model
        flip: (n,) int — 1 if argmax(base) != argmax(aligned), else 0
    """
    sorted_logprobs = np.sort(base_logprobs, axis=1)[:, ::-1]   # [n, 4] descending
    margin_raw = sorted_logprobs[:, 0] - sorted_logprobs[:, 1]  # [n]
    margin_z = zscore(margin_raw)                                # [n]

    argmax_base    = np.argmax(base_logprobs, axis=1)            # [n]
    argmax_aligned = np.argmax(aligned_logprobs, axis=1)         # [n]
    flip = (argmax_base != argmax_aligned).astype(int)           # [n]

    return margin_z, flip


def compute_kl_divergence(
    base_logprobs: np.ndarray,    # [n, 4]
    aligned_logprobs: np.ndarray, # [n, 4]
) -> np.ndarray:
    """Compute item-level KL(base || aligned) over 4-option softmax.

    Returns:
        kl: (n,) KL divergence per item
    """
    p_base    = np.exp(base_logprobs)    # [n, 4]
    # KL(base || aligned) = sum_k p_base_k * log(p_base_k / p_aligned_k)
    kl = np.sum(p_base * (base_logprobs - aligned_logprobs), axis=1)  # [n]
    return np.clip(kl, 0.0, None)  # Numerical stability: KL should be >= 0


def fit_logistic_regression(
    margin_z: np.ndarray,  # (n,)
    kl_div: np.ndarray,    # (n,)
    flip: np.ndarray,      # (n,) int
) -> dict:
    """Fit logistic regression: logit P(flip) = β₀ + β₁·margin_z + β₂·kl_div.

    Returns:
        {"beta1": float, "beta0": float, "pvalue_beta1": float,
         "auroc": float, "partial_eta2": float, "lr_model": LogisticRegression}
    """
    X = np.column_stack([margin_z, kl_div])  # [n, 2]
    y = flip.astype(int)                      # [n]

    # Check for sufficient class variation
    if len(np.unique(y)) < 2:
        return {
            "beta1": 0.0, "beta0": 0.0, "pvalue_beta1": 1.0,
            "auroc": 0.5, "partial_eta2": 0.0, "lr_model": None,
            "error": "No flip variation in dataset"
        }

    # sklearn LogisticRegression for predict_proba / AUROC
    lr = LogisticRegression(random_state=42, max_iter=1000)
    lr.fit(X, y)
    auroc = roc_auc_score(y, lr.predict_proba(X)[:, 1])

    # statsmodels Logit for Wald test p-value on β₁
    X_sm = sm.add_constant(X)  # [n, 3] with intercept column
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        logit_model = sm.Logit(y, X_sm).fit(disp=False)

    # coef order: [intercept, beta1(margin_z), beta2(kl_div)]
    beta0        = float(logit_model.params[0])
    beta1        = float(logit_model.params[1])
    pvalue_beta1 = float(logit_model.pvalues[1])  # two-sided Wald test

    # McFadden pseudo-R² as partial eta² approximation
    partial_eta2 = float(1 - (logit_model.llf / logit_model.llnull))

    return {
        "beta1": beta1, "beta0": beta0, "pvalue_beta1": pvalue_beta1,
        "auroc": auroc, "partial_eta2": partial_eta2, "lr_model": lr,
    }


def evaluate_cross_benchmark(
    lr_model: LogisticRegression,
    datasets_logprobs: dict,  # {"mmlu":{"base":ndarray,"aligned":ndarray}, ...}
    train_dataset: str = "mmlu",
) -> dict[str, float]:
    """Evaluate trained lr_model on held-out benchmarks.

    Returns:
        {"truthfulqa": auroc_float, "arc": auroc_float}
    """
    results = {}
    for ds_name, ds_logprobs in datasets_logprobs.items():
        if ds_name == train_dataset:
            continue
        margin_z_eval, flip_eval = compute_margin_and_flip(
            ds_logprobs["base"], ds_logprobs["aligned"]
        )
        kl_eval = compute_kl_divergence(ds_logprobs["base"], ds_logprobs["aligned"])

        if len(np.unique(flip_eval)) < 2:
            results[ds_name] = 0.5
            continue

        X_eval = np.column_stack([margin_z_eval, kl_eval])
        auroc_eval = roc_auc_score(flip_eval, lr_model.predict_proba(X_eval)[:, 1])
        results[ds_name] = float(auroc_eval)

    return results


def verify_pipeline_activated(
    base_logprobs: np.ndarray,    # [n, 4]
    aligned_logprobs: np.ndarray, # [n, 4]
    margin_z: np.ndarray,         # (n,)
    flip: np.ndarray,             # (n,)
    beta1: float,
    auroc: float,
) -> tuple[bool, dict[str, bool]]:
    """Check all pipeline activation indicators.

    Returns:
        (all_pass, {indicator_name: bool})
    """
    indicators = {
        "logprobs_extracted": base_logprobs.shape[0] > 1000,
        "margin_variable":    float(np.std(margin_z)) > 0.1,
        "flip_occurs":        float(np.mean(flip)) > 0.05,
        "negative_beta":      beta1 < 0.0,
        "auroc_above_chance": auroc > 0.55,
    }
    all_pass = all(indicators.values())
    return all_pass, indicators


def run_full_analysis(
    pair_cfg: dict,
    datasets_logprobs: dict,  # {"mmlu":{"base":ndarray,"aligned":ndarray}, ...}
) -> dict:
    """Run full analysis for one model pair on primary benchmark (MMLU).

    Returns:
        full results dict with beta1, pvalue, auroc, partial_eta2,
        cross_benchmark results, pipeline_activated flag
    """
    pair_id = pair_cfg["pair_id"]
    method  = pair_cfg["method"]

    # Primary analysis on MMLU
    mmlu_logprobs = datasets_logprobs["mmlu"]
    base_logprobs    = mmlu_logprobs["base"]
    aligned_logprobs = mmlu_logprobs["aligned"]

    margin_z, flip = compute_margin_and_flip(base_logprobs, aligned_logprobs)
    kl_div          = compute_kl_divergence(base_logprobs, aligned_logprobs)

    lr_results = fit_logistic_regression(margin_z, kl_div, flip)
    beta1        = lr_results["beta1"]
    auroc        = lr_results["auroc"]
    lr_model     = lr_results["lr_model"]

    # Cross-benchmark evaluation
    cross_benchmark = {}
    if lr_model is not None:
        cross_benchmark = evaluate_cross_benchmark(lr_model, datasets_logprobs)

    # Pipeline activation check
    pipeline_activated, indicators = verify_pipeline_activated(
        base_logprobs, aligned_logprobs, margin_z, flip, beta1, auroc
    )

    return {
        "pair_id":            pair_id,
        "method":             method,
        "base_model":         pair_cfg["base"],
        "aligned_model":      pair_cfg["aligned"],
        "n_items":            int(base_logprobs.shape[0]),
        "flip_rate":          float(np.mean(flip)),
        "beta1":              beta1,
        "beta0":              lr_results["beta0"],
        "pvalue_beta1":       lr_results["pvalue_beta1"],
        "auroc_mmlu":         auroc,
        "partial_eta2":       lr_results["partial_eta2"],
        "cross_benchmark":    cross_benchmark,
        "pipeline_activated": pipeline_activated,
        "indicators":         indicators,
        "lr_model":           lr_model,
        "margin_z":           margin_z,
        "flip":               flip,
        "kl_div":             kl_div,
    }
