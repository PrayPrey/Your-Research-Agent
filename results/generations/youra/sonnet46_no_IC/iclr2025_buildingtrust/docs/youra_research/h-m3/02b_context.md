# Phase 2B Context: H-M3
## 2-Cluster Correlation Structure with Correct Cluster Membership

**Generated:** 2026-08-04 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Gate:** SHOULD_WORK (non-blocking)
**Prerequisites:** h-m2 (COMPLETED, PARTIAL_PASS)

---

## Hypothesis Statement

Under the TrustLLM 16-model setting, if the RLHF-driven co-movement of safety+ethics
(positive ρ) combines with the safety-robustness anti-correlation (negative ρ)
from Steps 1+2, then hierarchical clustering (Ward linkage) of the 6×6 ρ_partial
matrix will produce a 2-cluster solution with silhouette score > 0.3 AND cluster
membership matching the predicted RLHF-sensitive {safety, ethics} vs RLHF-insensitive
{adversarial robustness, calibration/privacy} grouping in ≥4/6 dimensions.

---

## Experimental Setup (from Phase 2A via Phase 2B)

**Dataset:**
- Name: TrustLLM 6×6 ρ_partial matrix (derived from H-E1) + HELM leaderboard (optional replication)
- Type: derived (from h-e1/experiment_results_phase3.json) + standard (HELM)
- Source: h-e1/experiment_results_phase3.json (pre-computed)
- Path: h-e1/experiment_results_phase3.json
- Hypothesis Fit: ρ_partial matrix IS the input to clustering — direct test of H-M3 without re-computation

**Model:**
- Name: sklearn AgglomerativeClustering (Ward linkage) on 6×6 partial correlation matrix
- Type: statistical clustering (no neural network)
- Source: scikit-learn (standard library)
- Hypothesis Fit: Ward hierarchical clustering directly tests the 2-cluster prediction on ρ_partial geometry

---

## Prerequisites Context

**H-E1 (PASS):** 8/15 partial Spearman pairs significant; silhouette=0.614 (k=2, average-linkage)
- rho_partial matrix fully available in h-e1/experiment_results_phase3.json
- Dimension order: [truthfulness, safety, fairness, robustness, privacy, machine_ethics]

**H-M1 (PASS):** rho_partial(safety, machine_ethics)=0.841 > 0.5; 3/3 LLaMA-2 pairs Δ_safety>0 AND Δ_ethics>0
- RLHF co-optimizes safety + ethics confirmed

**H-M2 (PARTIAL_PASS):** rho_partial(safety, robustness)=-0.1882 (not significant); 3/3 Δ_robustness≤0
- Safety-robustness anti-correlation: directional but not Bonferroni-significant
- Key ablation: scale-only control yields rho=-0.771 (p=0.0008)

---

## Gate Conditions

- Primary: Silhouette score > 0.3 for k=2 Ward clustering
- Secondary: ≥4/6 dimensions in predicted clusters
  - Predicted RLHF-sensitive cluster: {safety, machine_ethics}
  - Predicted RLHF-insensitive cluster: {robustness, calibration/privacy}
  - Ambiguous (could go either way): {truthfulness, fairness}

**Note:** silhouette=0.614 already confirmed in H-E1 (average-linkage). Ward linkage may yield same or different value — must re-run with Ward.

**Gate Type:** SHOULD_WORK — pipeline continues regardless of outcome.
