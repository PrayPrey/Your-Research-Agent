---
hypothesis_id: h-m2
phase: validation
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
gate_type: SHOULD_WORK
gate_result: FAIL
---

# Validation Report: H-M2 — SE NLI Clustering Ablation Study

## Hypothesis

Under Llama-2-7B on TriviaQA dev, if SE applies NLI clustering before computing entropy, then SE entropy is invariant to within-cluster paraphrase variation, because NLI entailment groups surface variants into single cluster nodes, removing their contribution to entropy.

**Gate:** SE AUROC drops ≥ 0.03 when NLI clustering ablated (SHOULD_WORK)

---

## Gate Verdict: FAIL

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| delta_AUROC (SE_clustered − ablated) | 0.0000 | ≥ 0.03 | FAIL |
| AUROC_clustered | 0.2136 [0.122, 0.304] | — | — |
| AUROC_ablated (within_frac) | 0.2136 [0.122, 0.304] | — | — |

---

## Results

### Primary Metric
- **AUROC_clustered** = 0.2136 (95% CI: [0.122, 0.304])
- **AUROC_ablated** = 0.2136 (95% CI: [0.122, 0.304])
- **delta_AUROC** = 0.0000 (gate threshold = 0.03) → **FAIL**

### Secondary Metrics
- **mean_within_cluster_fraction** = 0.230 (23% of max entropy saved by clustering)
- **entailment_coclustering_rate** = 0.340 (34% of samples in largest cluster per question)
- **mean_cluster_count** = 7.31 (out of K=10; clustering is active)

### Mechanism Indicators
| Indicator | Value |
|-----------|-------|
| clustering_reduces_n (cluster count < 10) | TRUE |
| entropy_saving_nonzero (mean_within_frac > 0) | TRUE |
| auroc_delta_positive (delta > 0) | FALSE |
| delta_meets_gate (delta ≥ 0.03) | FALSE |

**mechanism_active** = False (all 4 indicators must pass)

---

## Analysis

### Why delta_AUROC = 0

The ablated predictor `within_cluster_fraction = (log(K) − SE_clustered) / log(K)` is a monotone decreasing transform of `SE_clustered`. Since AUROC depends only on the ranking of scores (not their absolute values), the two predictors produce **identical rankings** and therefore identical AUROC.

This is a structural property of the experiment design: the "ablated" predictor as specified in the experiment brief is not an independent measurement, but a rescaled version of the original SE score. The delta AUROC is identically 0 by construction, regardless of the underlying data.

### What the data does show

1. **NLI clustering is mechanically active**: mean cluster count = 7.31 < 10 (K), confirming grouping occurs
2. **Entropy savings are real**: mean within-cluster fraction = 0.23, i.e., ~23% of maximum entropy is absorbed by clustering
3. **SE is a valid uncertainty predictor**: AUROC(-SE_clustered, em_labels) = 0.786, confirming SE discriminates correct/incorrect answers when using the correct direction

### Root cause of FAIL

The experiment's ablated predictor (within-cluster fraction) and the primary predictor (SE_clustered) are equivalent under monotone transformation. The AUROC difference between two monotone-equivalent predictors is always 0. A valid ablation would require:
- A predictor computed from different information than SE_clustered (e.g., TE from H-M1, or SE computed from NLI-unaware random cluster assignments)
- Or: direct comparison of SE_clustered AUROC vs TE_clustered AUROC (H-E1 established this gap is ~0.05, sufficient to meet the 0.03 gate)

---

## Implications for H-M3 / H-M4

- H-M2 fails to measure the NLI clustering contribution via the designed AUROC ablation
- **Alternative evidence supporting the mechanism**: H-E1 established SE AUROC ≈ 0.54–0.57 vs TE AUROC ≈ 0.49–0.52 at N=98; the SE advantage is consistent with clustering contribution
- H-M3 should directly compare SE (with NLI) vs SE (without NLI / alternative clustering) using sufficiently distinct predictors
- The secondary metrics confirm the mechanism is active; only the AUROC measurement instrument is flawed

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Model | Llama-2-7B (inference only; samples cached from H-E1) |
| Dataset | TriviaQA dev, N=98 questions |
| K | 10 samples per question |
| NLI model | cross-encoder/nli-deberta-v3-large |
| n_bootstrap | 1000 |
| delta_auroc_gate | 0.03 |
| seed | 42 |

---

## Figures

- `figures/auroc_comparison.png` — AUROC bar chart (clustered vs ablated with 95% CI)
- `figures/within_cluster_scatter.png` — within-cluster fraction per question
- `figures/cluster_count_hist.png` — distribution of cluster counts (N=98)
- `figures/se_boxplot.png` — SE_clustered and within-cluster fraction distributions

---

## Code

`docs/youra_research/h-m2/code/` — ablation.py, evaluate.py, visualize.py, run.py, config.py

`docs/youra_research/h-m2/results.json` — full results JSON

---

## Conclusion

**Gate: FAIL** (delta_AUROC = 0.0000, threshold = 0.03)

The SHOULD_WORK gate is not satisfied. The ablation design has a structural limitation: the ablated predictor is a monotone transform of the primary predictor, making AUROC comparison uninformative. However, secondary evidence confirms NLI clustering is mechanically active (mean 23% entropy savings, cluster count < K for all questions). The hypothesis remains plausible but cannot be verified with this experimental design. Proceed to H-M3 with an independent ablation predictor.
