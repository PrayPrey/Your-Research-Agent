# Don't Just Blame Over-Parameterization for Spurious Correlations: Better Data Curation Eliminates Their Impact

## Key Metadata
- **Authors:** Kirichenko et al.
- **Year:** 2022
- **Venue:** NeurIPS 2022
- **Core Contribution:** Proposes DFR (Deep Feature Reweighting) — last-layer retraining on group-balanced held-out set achieves SOTA on Waterbirds without group-labeled training data.

## Section Summaries

### Abstract
We demonstrate that standard ERM models trained on datasets with spurious correlations learn feature representations sufficient for group-robust prediction. Simple last-layer retraining (DFR) on a small group-balanced subset achieves competitive worst-group accuracy, implying the backbone is not the primary barrier to robustness.

### Introduction & Motivation
Over-parameterization is often blamed for spurious correlations. This paper shows the backbone representations from ERM are actually sufficient for group-robust prediction if the final layer is retrained correctly. The problem is the loss function/training objective, not the representation capacity.

### Methodology
DFR protocol: (1) Train backbone with standard ERM on full training set. (2) Freeze backbone. (3) Retrain final linear layer using sklearn LogisticRegression (solver='lbfgs', C=1e9 — no regularization) on a small group-balanced held-out subset (typically 20% of training data with group labels). Key insight: no regularization avoids confounding from weight geometry (as later shown by h-m2 limitation to NOT hold for head-only Hessian). Group balance: equal samples per group in held-out set. Waterbirds evaluation: WGA metric on test set. Implementation in `PolinaKirichenko/deep_feature_reweighting` repo.

### Experiments & Results
| Method | Waterbirds WGA | CelebA WGA |
|--------|---------------|-----------|
| ERM | 0.72 | 0.47 |
| GroupDRO | 0.88 | 0.88 |
| DFR | 0.91 | 0.92 |

DFR outperforms GroupDRO on Waterbirds WGA. Core accuracy maintained. The held-out set size matters — 20% of training with group labels is sufficient. The sklearn L-BFGS protocol has become the standard convention for linear probing in spurious correlation literature. Authors do NOT report spurious feature probe accuracy per method — only WGA.

### Discussion & Conclusion
DFR demonstrates that ERM backbone representations contain sufficient information for group-robust classification — the problem is the classifier head's implicit regularization favoring spurious features. Last-layer retraining with group balance is sufficient and simpler than full retraining with group objectives.

## Key Contributions
- DFR method: last-layer retraining on group-balanced set achieves SOTA WGA
- Establishes sklearn L-BFGS (C=1e9, no regularization) as standard linear probe protocol
- Demonstrates ERM backbone is NOT the bottleneck — head is
- Code: `PolinaKirichenko/deep_feature_reweighting`

## Potential Relevance
The DFR protocol and sklearn L-BFGS convention are directly adopted. The finding that "backbone is sufficient" seems to contradict measuring spurious feature reduction in backbone — but this is exactly the tension we investigate: does backbone spurious encoding *decrease* across methods even if all are "sufficient"? The paper doesn't report per-method spurious probe accuracy, which is our gap.

---
