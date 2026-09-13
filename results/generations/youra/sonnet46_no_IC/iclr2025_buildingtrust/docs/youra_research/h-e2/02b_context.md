---
hypothesis_id: h-e2
generated_by: phase2c-step-01-JIT
source: 02b_verification_plan.md
generated_at: "2026-08-04"
---

# Per-Hypothesis Context: H-E2 (MST Minimum Evaluation Set)

## 1. Hypothesis Information

**ID:** H-E2  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Prerequisites:** H-E1 (COMPLETED — PASS)

**Statement:**
Under the TrustLLM 16-model evaluation setting, if we construct the minimum spanning tree (MST) of the partial Spearman distance matrix (1-|ρ_partial|), then the MST will identify a minimum sufficient evaluation set of ≤4 dimensions with ≥90% bootstrap topology stability (1000 resamples of 14/16 models), because the correlation structure is strong enough to make some dimensions redundant for evaluation purposes.

**Rationale:**
Directly verifies PROVE_NEW claim 3 (MST minimum evaluation set). Upgrades the descriptive correlation contribution (H-E1) to a prescriptive, actionable output — the key innovation of the paper. Bootstrap stability validates that the minimum set is not an artifact of the specific 16-model sample.

## 2. Variables

- **Independent:** Dimension inclusion/exclusion in MST
- **Dependent:** MST-derived minimum evaluation set size (integer ∈ {1,2,3,4,5,6}); bootstrap topology stability (proportion [0,1])
- **Controlled:** Distance metric (1-|ρ_partial|); bootstrap sample size (14/16 models)

## 3. Experimental Setup (from Phase 2A)

**Dataset:** TrustLLM Published Score Tables (standard)
- Source: https://github.com/HowieHwong/TrustLLM (results/ folder)
- Path: HowieHwong/TrustLLM repository / results/*.json
- Type: standard / programmatic-api
- **DERIVED INPUT:** The 6×6 ρ_partial matrix computed by H-E1 (h-e1/experiment_results_phase3.json)

**Model/Algorithm:** networkx MST on 6×6 partial correlation distance matrix
- Algorithm: Kruskal's (networkx.minimum_spanning_tree)
- Input: 6×6 distance matrix where d_ij = 1 - |ρ_partial_ij|
- Bootstrap: 1000 resamples of 14/16 models → recompute ρ_partial → recompute MST → compare edge sets

## 4. Verification Protocol

1. Use ρ_partial matrix from H-E1; construct complete graph with edge weights (1-|ρ_partial|)
2. Apply networkx.minimum_spanning_tree (Kruskal's algorithm) to identify MST
3. Identify the minimum sufficient evaluation set: leaf dimensions in MST structure (≤4 = redundant dimensions can be dropped)
4. Bootstrap 1000 times (resample 14 of 16 models): recompute ρ_partial → MST → topology; record edge set each time
5. Compute topology stability = proportion of bootstrap samples with identical edge set to full-sample MST

## 5. Success Criteria

- **Primary (PoC):** MST minimum set ≤4 dimensions
- **Secondary (PoC):** Bootstrap topology stability ≥0.90

**Gate:** MUST_WORK — if fails, EXPLORE (report full structure as null result)

## 6. Prerequisite Results (from H-E1)

From h-e1/04_validation.md (PASSED):
- 8/15 partial Spearman pairs significant (|ρ|>0.5, p<0.0033 Bonferroni)
- Strongest: safety-privacy ρ=0.9706
- MST: 5-edge minimum spanning tree constructed (prerequisite output noted)
- Key ρ_partial values available in h-e1/experiment_results_phase3.json
- Silhouette=0.614 (k=2) — clear cluster structure established

**Known ρ_partial values from H-E1:**
| Pair | ρ_partial | Distance (1-|ρ|) |
|------|-----------|-----------------|
| truthfulness — fairness | 0.9353 | 0.0647 |
| safety — privacy | 0.9706 | 0.0294 |
| fairness — privacy | 0.8941 | 0.1059 |
| safety — fairness | 0.8588 | 0.1412 |
| privacy — machine_ethics | 0.8588 | 0.1412 |
| safety — machine_ethics | 0.8412 | 0.1588 |
| fairness — machine_ethics | 0.7824 | 0.2176 |
| truthfulness — privacy | 0.7324 | 0.2676 |
| (robustness pairs) | ~0.0-0.3 | ~0.7-1.0 |

The MST will be dominated by the high-ρ pairs; robustness is likely a leaf node given its low correlations with other dimensions.

## 7. Dependencies

- Requires: H-E1 completed (PASS) ✅
- Provides: MST topology + bootstrap stability for Phase 3 paper
- Next: H-M1 runs in parallel (both depend on H-E1 only)
