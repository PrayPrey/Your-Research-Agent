"""Statistical evaluation for H-M1 orbit invariance probe."""
import numpy as np
import scipy.stats


def bootstrap_ci(data: np.ndarray, n_boot: int = 1000, seed: int = 42, level: float = 0.95) -> tuple:
    """Bootstrap CI for mean. Returns (low, high)."""
    result = scipy.stats.bootstrap(
        (data,), np.mean,
        confidence_level=level,
        n_resamples=n_boot,
        random_state=seed,
        method="percentile",
    )
    return result.confidence_interval.low, result.confidence_interval.high


def aggregate_probe(sim_tensor) -> dict:
    """Summary stats for a similarity tensor (torch or numpy)."""
    import torch
    if isinstance(sim_tensor, torch.Tensor):
        data = sim_tensor.numpy()
    else:
        data = np.array(sim_tensor)
    ci_low, ci_high = bootstrap_ci(data)
    return {
        "mean":    float(data.mean()),
        "std":     float(data.std()),
        "p5":      float(np.percentile(data, 5)),
        "p95":     float(np.percentile(data, 95)),
        "ci_low":  float(ci_low),
        "ci_high": float(ci_high),
    }


def evaluate_gate(results_scaling: dict, results_signflip: dict, n_boot: int = 1000, seed: int = 42) -> dict:
    """
    MUST_WORK gate: within_sim < cross_sim AND CI of gap lower bound > 0, for both orbit types.

    PASS: mean(within) < mean(cross) AND ci_low(gap) > 0 for BOTH scaling AND signflip.
    """
    gate_result = {}
    overall_pass = True

    for label, res in [("scaling", results_scaling), ("signflip", results_signflip)]:
        within = aggregate_probe(res["within_sim"])
        cross  = aggregate_probe(res["cross_sim"])
        gap    = aggregate_probe(res["gap"])

        mean_cond = within["mean"] < cross["mean"]
        ci_cond   = gap["ci_low"] > 0

        type_pass = mean_cond and ci_cond
        overall_pass = overall_pass and type_pass

        gate_result[label] = {
            "mean_within_sim": within["mean"],
            "mean_cross_sim":  cross["mean"],
            "mean_gap":        gap["mean"],
            "ci_low":          gap["ci_low"],
            "ci_high":         gap["ci_high"],
            "mean_condition":  mean_cond,
            "ci_condition":    ci_cond,
            "gate_pass":       type_pass,
            "within_stats":    within,
            "cross_stats":     cross,
            "gap_stats":       gap,
        }

    gate_result["overall_pass"] = overall_pass
    gate_result["verdict"] = "PASS" if overall_pass else "FAIL"
    gate_result["gate_condition"] = (
        "within_sim < cross_sim AND CI(gap).low > 0 for scaling AND signflip"
    )
    return gate_result


def verify_probe_activated(within_sim, cross_sim, n_orbit_pairs_constructed: int) -> tuple:
    """Sanity check that probe mechanism is working."""
    import torch
    if isinstance(within_sim, torch.Tensor):
        within_sim = within_sim
        cross_sim  = cross_sim
    indicators = {
        "pairs_constructed": n_orbit_pairs_constructed == 1000,
        "shapes_match":      within_sim.shape == cross_sim.shape,
        "gap_measurable":    (cross_sim - within_sim).abs().mean().item() > 1e-4,
        "no_degenerate":     within_sim.mean().item() < 0.999,
    }
    success = all(indicators.values())
    gap = (cross_sim - within_sim).mean().item()
    print(f"[VERIFY] Orbit invariance gap: {gap:.4f} (positive = NFT NOT orbit-invariant)")
    print(f"[VERIFY] Indicators: {indicators}")
    if not success:
        print(f"WARNING: Some probe activation checks failed: {indicators}")
    return success, indicators
