"""Statistical analysis: Pearson, Spearman, conditional LR, gate evaluation."""
import json
import numpy as np
import scipy.stats
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

from config import (
    PEARSON_R_THRESHOLD, PARTIAL_R2_THRESHOLD, CIRCULARITY_THRESHOLD,
    ABANDON_THRESHOLD, RESULTS_PATH,
)


def run_pearson(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
) -> tuple[float, float]:
    """Pearson correlation between SE_N5 and min_logprob. Returns (r, p_value)."""
    r, p = scipy.stats.pearsonr(se_scores, min_logprob_scores)
    return float(r), float(p)


def run_spearman_circularity(
    se_scores: np.ndarray,
    correctness: np.ndarray,
) -> tuple[float, float]:
    """Spearman rho(SE, correctness) circularity check. Returns (rho, p_value)."""
    rho, p = scipy.stats.spearmanr(se_scores, correctness)
    return float(rho), float(p)


def run_conditional_lr(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
    response_lengths: np.ndarray,
    correctness: np.ndarray,
) -> dict:
    """Full vs reduced conditional LR. Returns stats dict with McFadden partial R² and LRT."""
    y = correctness.astype(int)
    interaction = se_scores * min_logprob_scores

    X_full = np.column_stack([min_logprob_scores, se_scores, response_lengths, interaction])
    X_reduced = np.column_stack([min_logprob_scores, response_lengths])

    lr_full = LogisticRegression(max_iter=1000, solver="lbfgs").fit(X_full, y)
    lr_red = LogisticRegression(max_iter=1000, solver="lbfgs").fit(X_reduced, y)

    # log_loss(normalize=False) = sum of negative log-likelihoods
    ll_full = -log_loss(y, lr_full.predict_proba(X_full)[:, 1], normalize=False)
    ll_reduced = -log_loss(y, lr_red.predict_proba(X_reduced)[:, 1], normalize=False)

    # McFadden partial R²: improvement of full over reduced
    partial_r2 = 1.0 - (ll_full / ll_reduced)

    # LRT: chi2 with df=2 (SE + SE×min_logprob added to reduced)
    lrt_stat = -2.0 * (ll_reduced - ll_full)
    lrt_p = float(scipy.stats.chi2.sf(lrt_stat, df=2))

    return {
        "ll_full": float(ll_full),
        "ll_reduced": float(ll_reduced),
        "partial_r2_se": float(partial_r2),
        "coefs_full": lr_full.coef_[0].tolist(),
        "coefs_reduced": lr_red.coef_[0].tolist(),
        "lrt_chi2": float(lrt_stat),
        "lrt_p": lrt_p,
    }


def evaluate_gate(
    pearson_r: float,
    partial_r2: float,
    lrt_p: float = 1.0,
) -> dict:
    """Gate decision tree. Writes JSON to RESULTS_PATH. Returns result dict."""
    abs_r = abs(pearson_r)

    if abs_r > ABANDON_THRESHOLD:
        decision = "ABANDON"
        gate_pass = False
        reason = f"abs(r)={abs_r:.3f} > {ABANDON_THRESHOLD} (SE is logprob reparameterization)"
    elif abs_r > PEARSON_R_THRESHOLD or partial_r2 < PARTIAL_R2_THRESHOLD:
        decision = "EXPLORE_N10"
        gate_pass = False
        reason = f"abs(r)={abs_r:.3f} or partial_r2={partial_r2:.4f} marginal — retry N=10"
    else:
        decision = "PASS"
        gate_pass = True
        reason = (
            f"abs(r)={abs_r:.3f} < {PEARSON_R_THRESHOLD} "
            f"AND partial_r2={partial_r2:.4f} >= {PARTIAL_R2_THRESHOLD}"
        )

    result = {
        "gate_pass": gate_pass,
        "decision": decision,
        "pearson_r": float(pearson_r),
        "abs_pearson_r": float(abs_r),
        "partial_r2_se": float(partial_r2),
        "lrt_p": float(lrt_p),
        "reason": reason,
    }

    Path(RESULTS_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(result, f, indent=2)

    return result


def run_all(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
    response_lengths: np.ndarray,
    correctness: np.ndarray,
) -> dict:
    """Orchestrate all statistical tests. Returns merged results dict."""
    print("Running Pearson correlation...")
    pearson_r, pearson_p = run_pearson(se_scores, min_logprob_scores)
    print(f"  Pearson r={pearson_r:.4f}, p={pearson_p:.4e}")

    print("Running Spearman circularity check...")
    spearman_rho, spearman_p = run_spearman_circularity(se_scores, correctness)
    print(f"  Spearman rho={spearman_rho:.4f}, p={spearman_p:.4e}")
    if abs(spearman_rho) > CIRCULARITY_THRESHOLD:
        print(f"  WARNING: Circularity detected (|rho|={abs(spearman_rho):.3f} > {CIRCULARITY_THRESHOLD})")

    print("Running conditional logistic regression...")
    lr_stats = run_conditional_lr(se_scores, min_logprob_scores, response_lengths, correctness)
    print(f"  partial_r2_se={lr_stats['partial_r2_se']:.4f}, LRT p={lr_stats['lrt_p']:.4e}")

    print("Evaluating gate...")
    gate_result = evaluate_gate(pearson_r, lr_stats["partial_r2_se"], lr_stats["lrt_p"])
    print(f"  Gate: {gate_result['decision']} (pass={gate_result['gate_pass']})")
    print(f"  Reason: {gate_result['reason']}")

    stats = {
        "pearson_r": pearson_r,
        "pearson_p": pearson_p,
        "spearman_rho": spearman_rho,
        "spearman_p": spearman_p,
        "n_samples": int(len(se_scores)),
        "se_variance": float(np.var(se_scores)),
        "min_logprob_mean": float(np.mean(min_logprob_scores)),
        **lr_stats,
        **gate_result,
    }
    return stats
