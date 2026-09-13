# 4. Experiments

## 4.1 Experimental Setup

All experiments were conducted on a single NVIDIA A100 GPU (40GB). Feature extraction required approximately 2 hours for the full TruthfulQA MC1 dataset (4114 samples). We extracted hidden states from layers 24-31 and computed trajectory metrics using the logit lens projection.

### Baseline
- **$H_L$ only**: Final-layer output entropy as sole predictor
- **Mean entropy**: Average entropy across layers 24-31

### Proposed Models
- **NTI only**: Single-feature model using Normalized Trajectory Instability
- **Combined ($H_L$ + NTI + CMI)**: Full trajectory model

## 4.2 h-e1: NTI Existence Validation

We tested whether NTI alone provides statistically significant discrimination between correct and incorrect responses.

| Fold | AUROC | Status |
|------|-------|--------|
| 1 | 0.5356 | Below 0.55 |
| 2 | 0.5954 | **PASS** |
| 3 | 0.5665 | **PASS** |
| 4 | 0.5469 | Below 0.55 |
| 5 | 0.5839 | **PASS** |
| **Mean** | **0.5657** | **PASS** |

**Gate verdict**: PASS (mean > 0.55, all folds > 0.52 falsification boundary)

## 4.3 h-m1: Combined Model Improvement

We tested whether combining trajectory features with output entropy provides statistically significant improvement.

| Metric | Value |
|--------|-------|
| Null AUROC ($H_L$ only) | 0.5000 |
| Full AUROC ($H_L$ + NTI + CMI) | 0.5712 |
| **AUROC Gain** | **+0.0712 (+7.1%)** |
| **LRT $\chi^2$** | **39.2** |
| **LRT $p$-value** | **$1.15 \times 10^{-5}$** |

**Gate verdict**: PASS (gain > 0.03, $p < 0.05$)

## 4.4 h-m2: Low-Entropy Subset Performance

We tested whether trajectory features work on "confident" predictions where the model shows low output entropy.

| Metric | Value |
|--------|-------|
| Subset size | 1029 samples (25th percentile of $H_L$) |
| AUROC | 0.5136 |
| 95% CI | [0.4639, 0.5628] |

**Gate verdict**: FAIL (CI includes 0.50; no reliable signal on confident predictions)

## 4.5 h-m3: RCI Flip Pattern Analysis

We tested whether top-token changes across layers discriminate hallucinations from correct responses.

| Class | Flip Rate | Expected | Status |
|-------|-----------|----------|--------|
| Hallucinations | 95.1% | ≥ 30% | Met |
| Correct | 90.9% | < 10% | **NOT MET** |
| **Separation** | **4.2%** | ≥ 20% | **NOT MET** |

**Gate verdict**: LIMITATION_RECORDED (pattern is near-universal; not discriminative)
