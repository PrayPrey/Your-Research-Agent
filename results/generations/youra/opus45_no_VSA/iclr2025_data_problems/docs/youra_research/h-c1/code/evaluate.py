"""Statistical evaluation for H-C1 gate conditions"""
import numpy as np
from scipy.stats import mannwhitneyu, spearmanr
from ifr_computer import IFRComputer


def compute_ifr_statistics(
    embeddings: np.ndarray,
    trak_scores: np.ndarray,
    contaminated_mask: np.ndarray,
    k: int = 50,
    epsilon: float = 0.01
) -> dict:
    computer = IFRComputer(embeddings, trak_scores, k)
    redundancy = computer.compute_redundancy()
    ifr = computer.compute_ifr(redundancy, epsilon)

    ifr_contaminated = ifr[contaminated_mask]
    ifr_non_contaminated = ifr[~contaminated_mask]

    stat, pvalue = mannwhitneyu(ifr_contaminated, ifr_non_contaminated, alternative='greater')
    rho, rho_pvalue = computer.compute_correlation(ifr, redundancy)

    return {
        "ifr_contaminated_mean": float(ifr_contaminated.mean()),
        "ifr_non_contaminated_mean": float(ifr_non_contaminated.mean()),
        "ifr_diff_pvalue": float(pvalue),
        "ifr_redundancy_correlation": float(rho),
        "correlation_pvalue": float(rho_pvalue),
        "gate_1_satisfied": bool(pvalue < 0.05 and ifr_contaminated.mean() > ifr_non_contaminated.mean()),
        "gate_2_satisfied": bool(rho < -0.5),
        "redundancy": redundancy,
        "ifr": ifr
    }


def validate_gate_conditions(results: dict, significance_level: float = 0.05, correlation_threshold: float = -0.5) -> dict:
    gate_1 = results["gate_1_satisfied"]
    gate_2 = results["gate_2_satisfied"]

    return {
        "gate_1_passed": gate_1,
        "gate_2_passed": gate_2,
        "overall_passed": gate_1 and gate_2,
        "partial_pass": gate_1 or gate_2,
        "details": {
            "ifr_contaminated_mean": results["ifr_contaminated_mean"],
            "ifr_non_contaminated_mean": results["ifr_non_contaminated_mean"],
            "ifr_diff": results["ifr_contaminated_mean"] - results["ifr_non_contaminated_mean"],
            "ifr_pvalue": results["ifr_diff_pvalue"],
            "correlation": results["ifr_redundancy_correlation"],
            "correlation_pvalue": results["correlation_pvalue"]
        }
    }
