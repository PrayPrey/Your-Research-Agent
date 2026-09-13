"""signal_compute.py — Domain-specific H_d health signal computation for H-E1."""
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats


def compute_hd_cv(
    benchmark_scores: np.ndarray,
    held_out_scores: Optional[np.ndarray],
) -> float:
    """Robustness gap = mean(benchmark - held_out). Falls back to score variance."""
    if held_out_scores is None or len(held_out_scores) == 0:
        return float(np.var(benchmark_scores))
    common_len = min(len(benchmark_scores), len(held_out_scores))
    gap = np.array(benchmark_scores[:common_len]) - np.array(held_out_scores[:common_len])
    return float(np.mean(gap))


def compute_hd_nlp(
    benchmark_data: dict,
    reference_benchmark_data: dict,
) -> Optional[float]:
    """S_index via ConStat. Falls back to normalized mean difference."""
    scores_b = np.asarray(benchmark_data.get("scores", []))
    scores_r = np.asarray(reference_benchmark_data.get("scores", []))

    if len(scores_b) < 5 or len(scores_r) < 5:
        return None

    try:
        import constat
        # Try ConStat API variants
        try:
            s_index = constat.compute_s_index(scores_b, scores_r)
            return float(s_index)
        except AttributeError:
            pass
        try:
            cs = constat.ConStat(benchmark_data, reference_benchmark_data)
            result = cs.test()
            p_val = getattr(result, "p_value", None) or getattr(result, "pvalue", None)
            if p_val is not None:
                return float(-np.log(float(p_val) + 1e-10))
        except Exception:
            pass
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: normalized mean difference
    mu_b = float(np.mean(scores_b))
    mu_r = float(np.mean(scores_r))
    std_r = float(np.std(scores_r)) + 1e-9
    return float((mu_b - mu_r) / std_r)


def compute_hd_tabular(
    rankings_over_time: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> float:
    """Block-bootstrapped mean Kendall tau stability. block_size = T // 4."""
    rankings_over_time = np.asarray(rankings_over_time)
    if rankings_over_time.ndim == 1:
        rankings_over_time = rankings_over_time.reshape(-1, 1)
    T, N = rankings_over_time.shape
    if T < 2:
        return 0.0

    block_size = max(1, T // 4)
    rng = np.random.default_rng(seed)
    tau_samples = []

    for _ in range(n_bootstrap):
        n_blocks = max(1, T // block_size)
        starts = rng.integers(0, max(1, T - block_size + 1), size=n_blocks)
        indices = np.concatenate([np.arange(s, s + block_size) for s in starts])[:T]
        boot = rankings_over_time[indices]

        taus = []
        for t in range(len(boot) - 1):
            if N < 2:
                continue
            tau, _ = stats.kendalltau(boot[t], boot[t + 1])
            if not np.isnan(tau):
                taus.append(tau)
        tau_samples.append(float(np.mean(taus)) if taus else 0.0)

    return float(np.mean(tau_samples))


def compute_domain_signals(
    panel: pd.DataFrame,
    domain: str,
    lookback_months: int = 24,
) -> pd.DataFrame:
    """Compute H_d signal per benchmark in panel for given domain."""
    domain_panel = panel[panel["domain"] == domain].copy()
    results = []

    for benchmark in domain_panel["benchmark"].unique():
        bdf = domain_panel[domain_panel["benchmark"] == benchmark]
        labels = bdf["label"].unique()
        # Use most common label for this benchmark
        label = bdf["label"].mode()[0] if len(bdf) > 0 else "excluded"

        scores = bdf["score"].values

        if domain == "cv":
            hd_signal = compute_hd_cv(scores, None)
        elif domain == "nlp":
            bench_data = {"scores": scores}
            # Use all NLP benchmarks as reference (excluding self)
            ref_scores = domain_panel[domain_panel["benchmark"] != benchmark]["score"].values
            if len(ref_scores) < 5:
                ref_scores = scores  # fallback
            ref_data = {"scores": ref_scores}
            hd_val = compute_hd_nlp(bench_data, ref_data)
            hd_signal = hd_val if hd_val is not None else float(np.var(scores))
        elif domain == "tabular":
            # Build ranking matrix from quarters
            quarters = sorted(bdf["quarter"].unique())
            if len(quarters) < 2:
                hd_signal = 0.0
            else:
                n_models = bdf["model"].nunique()
                ranking_matrix = []
                for q in quarters:
                    qdf = bdf[bdf["quarter"] == q].sort_values("model")
                    if len(qdf) == 0:
                        continue
                    ranking_matrix.append(qdf["score"].values)
                if len(ranking_matrix) < 2:
                    hd_signal = 0.0
                else:
                    min_len = min(len(r) for r in ranking_matrix)
                    mat = np.array([r[:min_len] for r in ranking_matrix])
                    hd_signal = compute_hd_tabular(mat)
        else:
            hd_signal = float(np.var(scores))

        results.append({
            "benchmark": benchmark,
            "label": label,
            "hd_signal": hd_signal,
            "domain": domain,
        })

    return pd.DataFrame(results)
