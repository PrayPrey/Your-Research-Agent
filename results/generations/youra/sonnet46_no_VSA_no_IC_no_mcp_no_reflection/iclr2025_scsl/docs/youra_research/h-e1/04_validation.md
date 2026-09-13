---
hypothesis_id: h-e1
phase: 4
document_type: validation_report
generated: 2026-08-31
gate_type: MUST_WORK
gate_satisfied: false
status: FAIL
---

# Phase 4 Validation Report: H-E1
## Gradient Alignment Signal Existence Verification

**Hypothesis:** Under standard ERM training on Waterbirds and CelebA with random mini-batch sampling, per-sample last-layer gradient alignment ROC-AUC for predicting spurious-minority group membership exceeds per-sample loss ROC-AUC at ≥1 epoch on BOTH datasets.

**Gate:** MUST_WORK  
**Verdict:** **FAIL** — alignment ROC-AUC never exceeded loss ROC-AUC on either dataset at any checkpoint epoch.

---

## 1. Experiment Configuration

| Parameter | Waterbirds | CelebA |
|---|---|---|
| Model | ResNet-50 (ImageNet pretrained) | ResNet-50 (ImageNet pretrained) |
| Optimizer | SGD, lr=0.001, momentum=0.9, wd=1e-4 | SGD, lr=0.0001, momentum=0.9, wd=1e-4 |
| Training epochs (cap) | 50 (break at max checkpoint) | 50 (break at max checkpoint) |
| Checkpoint epochs | {1, 5, 10, 25, 50} | {1, 5, 10, 25, 50} |
| Train set size | 4,795 (full) | 16,000 (stratified subsample, 10% of 162K) |
| Minority group IDs | {1, 2} (landbird+water, waterbird+land) | {3} (blond+male) |
| Seed | 42 | 42 |
| Device | NVIDIA H100 NVL (cuda:1) | NVIDIA H100 NVL (cuda:1) |
| Gradient scope | Last layer only (fc: Linear(2048,2), 4098 params) | Same |
| Alignment method | per-batch mean gradient, negated cosine similarity | Same |

---

## 2. Results

### 2.1 Waterbirds

| Epoch | alignment_roc_auc | loss_roc_auc | alignment_wins |
|---|---|---|---|
| 1 | 0.1495 | 0.9297 | False |
| 5 | 0.3006 | 0.8541 | False |
| 10 | 0.3401 | 0.8208 | False |
| 25 | 0.3404 | 0.8007 | False |
| 50 | 0.3485 | 0.7747 | False |

**Waterbirds alignment wins ≥1 epoch: NO**

### 2.2 CelebA

| Epoch | alignment_roc_auc | loss_roc_auc | alignment_wins |
|---|---|---|---|
| 1 | 0.2462 | 0.9745 | False |
| 5 | 0.4841 | 0.9489 | False |
| 10 | 0.5227 | 0.9394 | False |
| 25 | 0.4071 | 0.9104 | False |
| 50 | 0.6321 | 0.9053 | False |

**CelebA alignment wins ≥1 epoch: NO**

---

## 3. Gate Evaluation

**Gate condition:** alignment_roc_auc > loss_roc_auc at ≥1 checkpoint epoch on BOTH datasets.

| Dataset | Any epoch with alignment_wins=True | Max alignment_roc_auc | Min loss_roc_auc |
|---|---|---|---|
| Waterbirds | **No** | 0.3485 (epoch 50) | 0.7747 (epoch 50) |
| CelebA | **No** | 0.6321 (epoch 50) | 0.9053 (epoch 50) |

**Gate (MUST_WORK): FAIL**

The gap between alignment and loss ROC-AUC is consistently large (0.27–0.78 on Waterbirds, 0.27–0.73 on CelebA). Per-sample loss is dramatically superior to per-batch gradient alignment as a predictor of spurious-minority membership under standard ERM.

---

## 4. Key Findings

1. **Loss ROC-AUC is very high and dominates throughout training.** On Waterbirds, loss_roc_auc starts at 0.93 (epoch 1) and degrades to 0.77 at epoch 50 as the model memorizes. On CelebA, it starts at 0.97 and remains at 0.91 at epoch 50. This is consistent with the JTT finding that high loss identifies spurious-minority samples.

2. **Alignment ROC-AUC is near-random or below random.** On Waterbirds, alignment_roc_auc ranges 0.15–0.35 — near-random (0.5) or below. On CelebA, it improves to 0.63 at epoch 50 but still loses to loss.

3. **Alignment may be inverted** (below 0.5 means the negated cosine similarity is anti-predictive). For Waterbirds at epoch 1, alignment_roc_auc=0.15, meaning raw (un-negated) cosine similarity would score 0.85 — a potentially strong signal in the opposite direction from what was hypothesized.

4. **Per-batch mean gradient approximation may be flawed.** The alignment score computes cosine similarity with the within-batch mean gradient rather than the global mean. With spurious-majority samples dominating each batch, the within-batch mean may already encode the spurious direction, making cosine similarity with it uninformative or inversely informative.

5. **Secondary criteria not met.** The threshold max(alignment_roc_auc) > 0.6 is met only on CelebA at epoch 50 (0.63), but the gate still fails because alignment never wins loss.

---

## 5. Artifacts

| Artifact | Path | Status |
|---|---|---|
| Experiment results JSON | `h-e1/code/outputs/results.json` | PRESENT |
| Pipeline results JSON | `h-e1/experiment_results.json` | PRESENT |
| ROC-AUC vs epoch (combined) | `h-e1/figures/roc_auc_vs_epoch.png` | PRESENT |
| ROC-AUC vs epoch (waterbirds) | `h-e1/figures/roc_auc_vs_epoch_waterbirds.png` | PRESENT |
| ROC-AUC vs epoch (celeba) | `h-e1/figures/roc_auc_vs_epoch_celeba.png` | PRESENT |
| Score distribution epoch 5 (waterbirds) | `h-e1/figures/score_distribution_epoch5_waterbirds.png` | PRESENT |
| Score distribution epoch 5 (celeba) | `h-e1/figures/score_distribution_epoch5_celeba.png` | PRESENT |
| ROC curves best epoch (waterbirds) | `h-e1/figures/roc_curves_best_epoch_waterbirds.png` | PRESENT |
| ROC curves best epoch (celeba) | `h-e1/figures/roc_curves_best_epoch_celeba.png` | PRESENT |
| Validation report | `h-e1/04_validation.md` | PRESENT (this file) |

---

## 6. Diagnosis and Next Steps

The hypothesis **H-E1 is falsified** under this experimental setup. The per-batch gradient alignment approach does not surpass per-sample loss as a spurious-minority predictor.

**Root cause candidates for future investigation:**

1. **Per-batch mean is wrong reference direction.** The within-batch mean gradient is dominated by majority samples in each batch. For a meaningful alignment signal, the reference should be the global mean gradient (two-pass), or the spurious-majority gradient centroid (requires labels), or an alternative direction (e.g., gradient variance direction).

2. **Last-layer-only scope is too narrow.** Spurious feature representations may live in earlier layers. The alignment signal at the last layer may be diluted by the compressed 2048-dim representation.

3. **ERM at very low loss (Waterbirds train_loss → 0.0003 by epoch 50).** Near-perfect training accuracy means all gradients are near-zero and nearly collinear, destroying alignment discrimination.

4. **CelebA subsampled.** The 16K subsample (vs 162K full) may alter group balance and alignment signal. Running on the full CelebA is a potential follow-up.

**Route:** FAIL — hypothesis falsified. Proceed to fallback or reformulation (e.g., use global mean gradient, or test gradient variance as predictor).
