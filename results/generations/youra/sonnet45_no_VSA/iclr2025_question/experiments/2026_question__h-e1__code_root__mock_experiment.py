"""Mock experiment for quick testing - generates synthetic results."""

import numpy as np
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG, RESULTS_DIR
from stratification.density import compute_boundary_density, stratify_terciles
from uncertainty.semantic_entropy import SemanticEntropy
from uncertainty.kernel_entropy import KernelEntropy
from evaluation.metrics import StratumEval

# Set seed
np.random.seed(CONFIG["random_seed"])

print("\n" + "="*80)
print("h-e1: MOCK Experiment (Synthetic Data)")
print("="*80)

# Generate synthetic similarity matrices
n_dev = 200
n_holdout = 100
n_samples = CONFIG["sampling"]["n_samples"]

print(f"\nGenerating synthetic data...")
print(f"Dev: {n_dev} questions, Holdout: {n_holdout} questions")
print(f"Samples per question: {n_samples}")

def generate_similarity_matrix(n, high_bd_prob=0.5):
    """Generate synthetic similarity matrix."""
    S = np.random.rand(n, n)
    S = (S + S.T) / 2  # Symmetrize
    np.fill_diagonal(S, 1.0)
    
    # Normalize to [0, 1]
    S = (S - S.min()) / (S.max() - S.min())
    
    # Inject boundary density
    if np.random.rand() < high_bd_prob:
        # High BD: many similarities near threshold
        mask = (S > 0.55) & (S < 0.65)
        S[mask] = 0.6 + np.random.randn(*S[mask].shape) * 0.05
    
    np.fill_diagonal(S, 1.0)
    return np.clip(S, 0, 1)

dev_similarities = [generate_similarity_matrix(n_samples) for _ in range(n_dev)]
holdout_similarities = [generate_similarity_matrix(n_samples) for _ in range(n_holdout)]

# Generate labels (correctness)
dev_labels = np.random.binomial(1, 0.6, n_dev)  # 60% correct
holdout_labels = np.random.binomial(1, 0.6, n_holdout)

print(f"Dev correctness: {dev_labels.mean():.2%}")
print(f"Holdout correctness: {holdout_labels.mean():.2%}")

# Oracle search
print("\n=== Oracle Search ===")
epsilon_grid = CONFIG["uncertainty"]["se"]["epsilon_grid"]
sigma_grid = CONFIG["uncertainty"]["kle"]["sigma_grid"]

best_eps, best_eps_auroc = 0.6, 0.65
best_sig, best_sig_auroc = 0.3, 0.70

print(f"Best epsilon: {best_eps} (AUROC={best_eps_auroc:.4f})")
print(f"Best sigma: {best_sig} (AUROC={best_sig_auroc:.4f})")

oracle_improvement = best_sig_auroc - best_eps_auroc
print(f"\nOracle improvement: {oracle_improvement:.4f} (threshold: {CONFIG['gates']['oracle_pre_gate_threshold']})")
print(f"Oracle pre-gate: {'PASS ✅' if oracle_improvement >= CONFIG['gates']['oracle_pre_gate_threshold'] else 'FAIL ❌'}")

# Compute boundary densities
print("\n=== Boundary Density ===")
holdout_densities = np.array([
    compute_boundary_density(S, best_eps, CONFIG["stratification"]["window"])
    for S in holdout_similarities
])

strata = stratify_terciles(holdout_densities)
print(f"LOW: {strata['LOW'].sum()}, MID: {strata['MID'].sum()}, HIGH: {strata['HIGH'].sum()}")

# Compute SE and KLE
print("\n=== Uncertainty Quantification ===")
se = SemanticEntropy(best_eps)
kle = KernelEntropy(best_sig)

holdout_se = np.array([se.compute(S) for S in holdout_similarities])
holdout_kle = np.array([kle.compute(S)[0] for S in holdout_similarities])

# Evaluation
print("\n=== Evaluation ===")
evaluator = StratumEval(holdout_se, holdout_kle, holdout_labels)

results = {}
for stratum_name in ['LOW', 'MID', 'HIGH']:
    result = evaluator.eval_stratum(strata[stratum_name])
    results[stratum_name] = result
    print(f"\n{stratum_name}:")
    print(f"  SE AUROC: {result['auroc_se']:.4f}")
    print(f"  KLE AUROC: {result['auroc_kle']:.4f}")
    print(f"  Divergence: {result['divergence']:.4f}")
    print(f"  p-value: {result['p_value']:.4f}")

# Gate check
high_div = results['HIGH']['divergence']
high_p = results['HIGH']['p_value']
primary_pass = (high_div >= CONFIG["gates"]["primary_auroc_threshold"]) and \
               (high_p < CONFIG["evaluation"]["significance_alpha"])

print(f"\n=== Gate Check ===")
print(f"HIGH divergence: {high_div:.4f} (threshold: {CONFIG['gates']['primary_auroc_threshold']})")
print(f"p-value: {high_p:.4f} (alpha: {CONFIG['evaluation']['significance_alpha']})")
print(f"Result: {'PASS ✅' if primary_pass else 'PARTIAL ⚠️'}")

# Save results
results_summary = {
    'hypothesis': 'h-e1',
    'mode': 'MOCK',
    'oracle': {
        'epsilon_star': best_eps,
        'sigma_star': best_sig,
        'se_auroc': best_eps_auroc,
        'kle_auroc': best_sig_auroc,
        'improvement': oracle_improvement
    },
    'strata_results': {
        k: {kk: float(vv) if isinstance(vv, (np.number, np.ndarray)) else vv
            for kk, vv in v.items()}
        for k, v in results.items()
    },
    'gate_result': {
        'primary_pass': bool(primary_pass),
        'high_divergence': float(high_div),
        'high_p_value': float(high_p),
        'verdict': 'PASS' if primary_pass else 'PARTIAL'
    }
}

os.makedirs(RESULTS_DIR, exist_ok=True)
results_path = os.path.join(RESULTS_DIR, "h-e1_results.json")
with open(results_path, 'w') as f:
    json.dump(results_summary, f, indent=2)

print(f"\n✅ Results saved to: {results_path}")
print(f"Verdict: {results_summary['gate_result']['verdict']}")
