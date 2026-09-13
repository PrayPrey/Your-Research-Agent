# 5. Results

## 5.1 H-E3: Per-Sample Hessian Trace Discriminates Minority Group Membership

**Main result:** 4/5 seeds satisfy all three gate criteria simultaneously. Per-sample last-fc Hessian trace achieves AUROC≥0.85 for minority membership prediction at t*, with the signal being ERM-induced rather than pretrained (AUROC(t=0)<0.70 in all seeds), and developing monotonically in 4/5 seeds (Spearman ρ≥0.8).

### Per-Seed AUROC Results

| Seed | AUROC(t=0) | AUROC(t*) | t* | Spearman ρ | Pass |
|------|------------|-----------|-----|------------|------|
| 1 | 0.538 | 0.850 | 20 | 0.70 | ✗ |
| 2 | 0.609 | 0.885 | 50 | 0.943 | ✓ |
| 3 | 0.558 | 0.897 | 50 | 0.943 | ✓ |
| 4 | 0.579 | 0.903 | 20 | 0.900 | ✓ |
| 5 | 0.609 | 0.890 | 5 | 1.000 | ✓ |

**Gate result: PASS (4/5 seeds).** Seed 1 fails due to a non-monotone AUROC trajectory (Spearman ρ=0.70, threshold 0.80) caused by a dip at t=5 — both AUROC(t=0)<0.70 and AUROC(t*)≥0.85 are satisfied.

**Epoch-0 control:** All 5 seeds show AUROC(t=0)∈[0.538, 0.609] (mean 0.577) — well below the 0.70 control threshold. The pretrained ImageNet backbone alone does not discriminate minority from majority training samples on Waterbirds. The trace asymmetry is created by ERM training.

Figure 1 shows AUROC(t=0) and AUROC(t*) per seed with gate thresholds. Figure 3 shows the full AUROC trajectory across all 6 checkpoints.

### Trace Ratio R(t)

The trace ratio R(t) = mean_minority_trace / mean_majority_trace rises from near-unity at initialization to peak values of 4.09–8.89:

| Seed | R(t=0) | R(t*) | t* |
|------|--------|-------|-----|
| 1 | 1.05 | 4.37 | 20 |
| 2 | 1.12 | 5.55 | 50 |
| 3 | 1.06 | 7.21 | 50 |
| 4 | 1.08 | 4.09 | 20 |
| 5 | 1.12 | 8.89 | 5 |

All seeds show R(t*)>>1 — minority Hessian traces are systematically higher than majority at the peak checkpoint. Figure 2 shows the R(t) trajectory for all seeds. Optimal t* varies across seeds (t*∈{5, 20, 50}), indicating that the peak of minority-majority curvature divergence is stochastic across training runs.

### Estimator Stability

Hutchinson coefficient of variation (CV) across K=50 probes:

| Seed | CV |
|------|-----|
| 1 | 0.0233 |
| 2 | 0.0132 |
| 3 | 0.0232 |
| 4 | 0.0283 |
| 5 | 0.0108 |

All CVs < 3% (max 0.0283). K=50 Rademacher probes provide reliable per-sample trace estimates for the last-fc layer of ResNet-50. The trace signal is not dominated by Hutchinson estimation noise.

Figure 4 shows the per-sample trace distributions at t* for minority and majority samples. Minority traces are systematically elevated, consistent with the AUROC>0.85 finding. Figure 5 shows Spearman ρ values on the rising AUROC segment per seed.

## 5.2 H-M1: Confidence-Differential Mechanism Is Absent at t*

**Main result:** The pre-registered mechanism gate fails in all 5 seeds. Minority training confidence at t* is 0.9678–0.9999 — fully saturated, not boundary-straddling. The confidence-differential mechanism is inactive.

### Per-Seed Confidence at t*

| Seed | t* | p_minority(t*) | p_majority(t*) | Boundary [0.3,0.7]? |
|------|----|----------------|----------------|----------------------|
| 1 | 20 | 0.9956 | 0.9994 | ✗ |
| 2 | 50 | 0.9999 | 0.9999 | ✗ |
| 3 | 50 | 0.9998 | 0.9999 | ✗ |
| 4 | 20 | 0.9964 | 0.9992 | ✗ |
| 5 | 5 | 0.9678 | 0.9925 | ✗ |

**Gate result: FAIL (0/5 seeds).** No seed shows minority confidence in the predicted boundary condition range [0.3, 0.7] at t*. Mean p_minority(t*)=0.9919, mean p_majority(t*)=0.9982.

**Transient early-epoch differential exists:** At epoch 1, a minority-majority confidence gap is visible (seed 1: p_min=0.827 vs p_maj=0.972; seed 5: p_min≈0.87 vs p_maj≈0.99). This is consistent with LaBonte & Muthukumar [2026]'s Phase I prediction — ERM learns the spurious feature first, temporarily lagging minority confidence. However, this differential disappears before t* in all seeds. By t*, both groups are saturated.

Figure 6 shows confidence trajectories per seed. Figure 7 shows per-sample confidence distributions at t*. Figure 8 shows the H-M1 gate comparison.
