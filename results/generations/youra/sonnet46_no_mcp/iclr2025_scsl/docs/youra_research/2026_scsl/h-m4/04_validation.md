# H-M4 Phase 4 Validation Report

**Hypothesis:** H-M4 — DFR Efficacy vs Backbone Training Depth  
**Gate Type:** SHOULD_WORK  
**Gate Result:** LIMITATION  
**Completed At:** 2026-05-04T19:00:00

---

## 1. Experiment Summary

**Hypothesis statement:** Under controlled truncated ERM training on Waterbirds, if DFR last-layer reweighting is applied to ResNet-50 backbones trained to 5 different epoch checkpoints {1, 2, 10, 20, 30}, then DFR worst-group accuracy (WGA) improvement over ERM baseline will be positively correlated with (training_epochs − t*), with Pearson r > 0.7 (p < 0.05).

**t* used:** 2.0 epochs (from H-M3 mean_t* = 2.0)  
**Seeds:** [1, 2, 3]  
**Conditions (epochs):** [1, 2, 10, 20, 30]  
**epochs_past_tstar:** [-1.0, 0.0, 8.0, 18.0, 28.0]

---

## 2. Raw Results per Seed

### Seed 1
| Epoch | ERM WGA | DFR WGA | Improvement |
|-------|---------|---------|-------------|
| 1     | 0.2087  | 0.8115  | +0.6028     |
| 2     | 0.3364  | 0.8240  | +0.4875     |
| 10    | 0.7299  | 0.8536  | +0.1236     |
| 20    | 0.7150  | 0.8645  | +0.1495     |
| 30    | 0.7259  | 0.8645  | +0.1386     |

### Seed 2
| Epoch | ERM WGA | DFR WGA | Improvement |
|-------|---------|---------|-------------|
| 1     | 0.1994  | 0.8006  | +0.6012     |
| 2     | 0.3349  | 0.8053  | +0.4704     |
| 10    | 0.7103  | 0.8474  | +0.1371     |
| 20    | 0.7477  | 0.8598  | +0.1121     |
| 30    | 0.7196  | 0.8769  | +0.1573     |

### Seed 3
| Epoch | ERM WGA | DFR WGA | Improvement |
|-------|---------|---------|-------------|
| 1     | 0.2414  | 0.8069  | +0.5654     |
| 2     | 0.3318  | 0.8224  | +0.4907     |
| 10    | 0.6822  | 0.8520  | +0.1698     |
| 20    | 0.7290  | 0.8629  | +0.1340     |
| 30    | 0.7445  | 0.8723  | +0.1277     |

---

## 3. Aggregated Results (Mean ± Std across Seeds)

| Epoch | epochs_past_t* | Mean ERM WGA | Mean DFR WGA | Mean Improvement | Std Improvement |
|-------|---------------|-------------|-------------|-----------------|----------------|
| 1     | -1.0          | 0.2165      | 0.8063      | 0.5898          | 0.0173         |
| 2     | 0.0           | 0.3344      | 0.8172      | 0.4829          | 0.0089         |
| 10    | 8.0           | 0.7075      | 0.8510      | 0.1435          | 0.0194         |
| 20    | 18.0          | 0.7305      | 0.8624      | 0.1319          | 0.0153         |
| 30    | 28.0          | 0.7300      | 0.8712      | 0.1412          | 0.0122         |

---

## 4. Correlation Analysis

- **Pearson r = -0.8145** (strong negative correlation)
- **p-value (two-tailed) = 0.0932**
- **p-value (one-tailed, positive direction) = 0.9534**
- **Gate threshold:** r > 0.7
- **Gate result: LIMITATION** — Pearson r = -0.8145 ≤ threshold 0.7

The correlation is strong but in the **opposite direction** to the hypothesis. DFR improvement is highest at early checkpoints (epoch 1: mean improvement = 0.590) and decreases sharply as training depth increases (epoch 20: mean improvement = 0.132).

---

## 5. Monotonicity Check

- **Monotonic (increasing):** False
- **Positive diffs:** 1 / 4
- **Pattern:** Steep drop from epoch 1→2→10, near-plateau at epochs 10-30

---

## 6. Gate Evaluation

| Criterion | Required | Observed | Pass? |
|-----------|----------|----------|-------|
| Pearson r direction | r > 0 | r = -0.8145 | FAIL |
| Pearson r magnitude | r > 0.7 | \|r\| = 0.8145 | — |
| p-value (one-tailed positive) | p < 0.05 | p = 0.9534 | FAIL |

**SHOULD_WORK gate: NOT SATISFIED**

---

## 7. Post-Validation Checks

- **Feature dimension:** 2048 (confirmed in all seeds/epochs — no mock model)
- **ERM WGA at epoch 1 (0.21):** Consistent with genuine undertrained ERM (random-chance level for minority group)
- **DFR WGA floor (~0.80):** Consistent with Kirichenko et al. 2022 DFR results on Waterbirds
- **No NaN/inf in results:** All metrics clean
- **Checkpoint files verified:** All 15 checkpoints (3 seeds × 5 epochs) present
- **Results JSON:** `code/results/h-m4_results.json` — complete
- **Figures:** 4/4 generated (`gate_metrics.png`, `wga_curves.png`, `scatter_correlation.png`, `monotonicity_check.png`)

---

## 8. Interpretation and Limitations

### What the data shows
The data reveals a **reverse of the hypothesized pattern**: DFR is dramatically more effective on early (undertrained) backbones than on deeply trained ones. At epoch 1 (pre-t*), mean improvement = 0.590; by epoch 10+ (post-t*), improvement plateaus near 0.132–0.144.

### Why this is a limitation, not a failure
The mechanism interpretation requires revision. The hypothesis assumed DFR benefit increases post-t* because the backbone encodes sufficient core features. The data suggests:
1. **Early backbones produce highly reweightable representations** — their poor ERM WGA (0.22) leaves room for large DFR gains
2. **Deep backbones approach ERM WGA ceiling (~0.73)** — less room for DFR improvement regardless of feature quality
3. **The ERM-WGA floor/ceiling effect confounds the Pearson correlation** — improvement = DFR_WGA − ERM_WGA conflates two separate phenomena

### What remains valid from H-M4
- DFR improves WGA at **all** training depths (mean improvement > 0.13 even at epoch 30)
- DFR WGA is consistently high (~0.81–0.87) across all epochs, confirming DFR robustness
- The mechanism (reweighting works on frozen features) is confirmed

### Limitation for research paper
H-M4 hypothesis (positive Pearson r) is not supported. The correct characterization is: **DFR WGA improvement is negatively correlated with training depth** (r = -0.81), primarily driven by the ERM WGA ceiling effect. This is a nuanced finding — DFR absolute WGA improves slightly with depth (0.806 → 0.871), but the *gap* shrinks because ERM WGA also improves.

---

## 9. Verdict

**LIMITATION** — SHOULD_WORK gate not met. The directional hypothesis is incorrect. Finding logged as limitation. Pipeline continues to Phase 5 (no blocking).

**Results file:** `code/results/h-m4_results.json`  
**Figures:** `code/figures/`  
**Log:** `code/experiment.log`
