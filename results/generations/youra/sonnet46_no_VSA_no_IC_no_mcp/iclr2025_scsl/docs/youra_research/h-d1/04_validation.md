# H-D1 Validation Report

**Hypothesis:** SimCLR (contrastive) representations show a higher spurious/task probe accuracy ratio than ERM (supervised) on Waterbirds (p < 0.05), but no significant difference on CelebA (p > 0.1), confirming that augmentation-invariance of the spurious attribute — not label-based spurious correlation — drives differential encoding.

**Gate type:** SHOULD_WORK  
**Gate verdict:** PARTIAL_CA (WB directional test fails; CelebA null test passes)  
**Overall outcome:** PARTIAL — direction reversed on Waterbirds; null holds on CelebA

---

## Results Summary

### Primary Tests

| Test | Dataset | Metric | Value | Threshold | Pass |
|------|---------|--------|-------|-----------|------|
| Directional (MoCo > ERM) | Waterbirds | p_directional | 1.0000 | < 0.05 | ✗ |
| Null (no difference) | CelebA | p_two_sided | 0.9167 | > 0.10 | ✓ |

### Waterbirds Primary (directional test: MoCo > ERM)

- **Direction observed:** ERM > MoCo (reversed)
- t = −8.980, p_directional = 1.000, Cohen's d = −5.679
- ERM mean ratio = 1.0520 ± 0.0043
- MoCo mean ratio = 1.0273 ± 0.0034
- Mean diff (MoCo − ERM) = −0.0247

The hypothesis predicted MoCo > ERM on Waterbirds. Observed: ERM > MoCo with very large effect size (|d|=5.68), consistent with H-E1 validation findings.

### CelebA Primary (null test: no difference)

- t = 0.108, p_two_sided = 0.917, Cohen's d = 0.068
- ERM mean ratio = 1.0668 ± 0.0275
- MoCo mean ratio = 1.0685 ± 0.0126
- Mean diff = +0.0016 (negligible)

CelebA null test passes: no significant difference between ERM and MoCo on CelebA. This component of the hypothesis holds.

---

## Ablation Results

**Ablation A (WB-only directional):** p_directional = 1.000 — confirms WB test failure  
**Ablation B (CelebA-only null):** p_two_sided = 0.917 — confirms null holds  
**Ablation C (all-paradigm WB pairs):** Full pairwise comparisons across 4 paradigms  
**Ablation D (reversed direction):** ERM > MoCo on WB — p = 9.4e-6, d = 5.679  
→ The reversed direction (ERM > MoCo) is highly significant, consistent with H-E1.

---

## Pre-registered Interpretation

Gate verdict `partial_ca` (WB fails, CelebA passes) maps to interpretation:

> **`supervised_label_drives_spurious`** — ERM encodes more spurious features than MoCo-v3 on Waterbirds. This contradicts the augmentation-invariance hypothesis and suggests that supervised label correlation drives spurious encoding more than contrastive objectives.

The hypothesis predicted the opposite direction (contrastive > supervised) due to augmentation invariance. The observed direction (supervised > contrastive) indicates instead that label-based spurious correlation is the dominant mechanism: ERM learns to use both spurious and task features because both are predictive of the label, while MoCo-v3's contrastive objective is indifferent to label-correlated spurious features.

**Note on CelebA null:** The fact that CelebA shows no difference between ERM and MoCo is consistent with prior work. On CelebA, the spurious attribute (Male) is less tightly augmentation-invariant than Waterbirds background texture, so neither paradigm shows elevated spurious encoding — both encode spurious and task features similarly.

---

## Gate Evaluation

```
Gate type: SHOULD_WORK
WB directional (p < 0.05):  FAIL  — p=1.000 (wrong direction)
CelebA null (p > 0.10):      PASS  — p=0.917
Gate outcome: PARTIAL_CA
```

**SHOULD_WORK interpretation:** For SHOULD_WORK gates, partial results are acceptable and scientifically informative. The CelebA null hypothesis holds, confirming dataset-specificity of differences. The WB directional hypothesis fails because the direction is reversed — a finding that is itself significant and aligns with H-E1.

---

## Figures Generated

- `figures/gate_metrics.png` — Bar chart: MoCo vs ERM ratio on WB + CelebA ±1 SD
- `figures/interaction_plot.png` — All 4 paradigms × 2 datasets
- `figures/directional_test.png` — Directional test results with CIs
- `figures/seed_distributions.png` — Violin/strip distributions per paradigm × dataset

---

## Key Finding

**H-D1 result: PARTIAL.** The augmentation-invariance hypothesis is not supported in the predicted direction. Supervised learning (ERM) encodes MORE spurious features than contrastive learning (MoCo-v3) on Waterbirds, with large effect size (d=5.68, p=9.4e-6 for reversed direction). On CelebA, no significant difference exists between paradigms (p=0.917, d=0.07). This pattern — large dataset-specific difference driven by supervised label correlation — is consistent with the broader literature and with H-E1 findings.

---

*Generated: 2026-08-26*  
*Experiment env: youra-h-e1 (Python 3.10, torch 2.5.1, torchvision 0.20.1)*  
*CelebA: 2000 balanced samples (500/group), 5 seeds, linear probe*  
*Waterbirds: H-E1 results (20 probe runs, 5 seeds × 4 paradigms)*
