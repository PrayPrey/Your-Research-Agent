# H-E1 Validation Report

**Date:** 2026-08-28
**Hypothesis:** Task-Correlated Structure in BERT Hidden States
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK

## Results

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Purity | 0.7409 | >0.20 (random) | **PASS** |
| ARI | 0.3128 | >0 | **PASS** |
| NMI | 0.5641 | >0.3 | **PASS** |

## Gate Verdict: **PASS**

Cluster purity 0.7409 significantly exceeds random baseline 0.20 (5 tasks = 1/5).

## Experiment Details

- **Model:** bert-base-uncased (frozen, last layer [CLS])
- **Dataset:** SuperGLUE validation splits (boolq, cb, copa, wic, wsc)
- **Samples:** 660 total (200 boolq, 56 cb, 100 copa, 200 wic, 104 wsc)
- **Clustering:** KMeans K=8, seed=42

## Artifacts

- `results/metrics.json` - numerical metrics
- `figures/cluster_composition.png` - per-cluster task distribution
- `figures/tsne.png` - 2D embedding visualization by task

## Conclusion

BERT hidden states exhibit strong task-correlated structure. Embeddings cluster meaningfully by task identity without any task-specific training. This validates the existence hypothesis that pretrained transformer representations contain task-relevant structure that can be discovered via unsupervised clustering.

**Next:** Proceed to H-M1 (mechanism hypotheses).
