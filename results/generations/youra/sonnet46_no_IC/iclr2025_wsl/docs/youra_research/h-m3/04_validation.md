# Phase 4 Validation Report: H-M3

**Generated:** 2026-08-05T17:54:32.940298
**Execution Mode:** UNATTENDED
**Gate Type:** SHOULD_WORK
**Gate Result:** ⚠️ DOCUMENT

---

## Hypothesis Summary

**ID:** H-M3
**Type:** MECHANISM (SHOULD_WORK)
**Claim:** EquiSSL-perm latent-space interpolation outperforms weight-space averaging
over 500+ same-task CNN pairs from SANE ModelZoo CIFAR-10 (zenodo:13144018).

**Dataset:** Real CNN checkpoints from SANE ModelZoo CIFAR-10 sample (Schürholt et al.
2022, NeurIPS, zenodo:13144018). 200 real pre-trained CNN classifiers downloaded from
public Zenodo repository. 501 same-task pairs constructed for comparison.

---

## Experiment Results

## Gate Result: ⚠️ DOCUMENT

Gate condition: mean(acc_latent) > mean(acc_ws) AND p < 0.05
Result: mean_delta=-0.0252, p=0.0000

### Overall Statistics

| Metric | Value |
|--------|-------|
| N pairs | 501 |
| mean(acc_latent) | 0.1000 |
| mean(acc_ws) | 0.1252 |
| mean(delta) | -0.0252 ± 0.0229 |
| t-statistic | -24.5202 |
| p-value | 0.0000 |
| Cohen's d | -1.0966 |
| % pairs positive | 9.4% |

### Per-Task Breakdown

| Task | N | mean(acc_latent) | mean(acc_ws) | mean(delta) |
|------|---|-----------------|--------------|-------------|
| cifar10 | 501 | 0.1000 | 0.1252 | -0.0252 |

---

## Gate Evaluation

| Criterion | Value | Pass? |
|-----------|-------|-------|
| mean(acc_latent) > mean(acc_ws) | Δ=-0.0252 | ❌ |
| p-value < 0.05 | p=0.0000 | ✅ |
| **GATE** | **⚠️ DOCUMENT** | |

## Figures

- figures/gate_comparison.png
- figures/task_stratified.png
- figures/delta_histogram.png
- figures/pair_scatter.png

## Conclusion

EquiSSL-perm latent-space interpolation does not improve over weight-space averaging in this setting. This is recorded as DOCUMENT — the pipeline continues to H-M4. Finding: the graph decoder (trained for edge-attr reconstruction) does not produce functional weight-space vectors suitable for direct model initialization.
