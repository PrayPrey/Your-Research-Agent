# Phase 6.5 Human Review Notes
# MINOR issues collected from adversarial review — NOT auto-fixed
# For human author review before submission

---

## Round 1 (R1) — Accuracy and Engagement Review

### HRN-R1-001 — Epoch clarification [clarity]
**Location:** Methodology section, Training subsection
**Issue:** Methodology states "100 epochs" in the general training protocol, but h-e1 used 50 epochs (correctly stated in Table 1 caption). The Methodology section does not explicitly call out that h-e1 used 50 epochs and h-m1 used 100 epochs.
**Recommendation:** Add a parenthetical: "(h-e1: 50 epochs for primary comparison; h-m1: 100 epochs for ablation suite)" in the Training paragraph.
**Not auto-fixed because:** Style choice — the table caption handles it; a more explicit callout in Methodology is the author's judgment call.

---

### HRN-R1-002 — "Necessary" in title [style]
**Location:** Paper title: "Structural Equivariance as a Necessary Inductive Bias"
**Issue:** The word "Necessary" is a philosophically strong claim. The paper tests only L2 canonicalization (which fails) and augmentation (which is unreliable), but acknowledges in Limitation 3 that stronger canonicalization approaches (Hungarian alignment, sort-by-magnitude) are untested. A reviewer might challenge whether equivariance is truly "necessary" if a sufficiently good canonicalization could work.
**Recommendation:** Authors may consider "An Effective Inductive Bias" or "The Correct Inductive Bias" — but "Necessary" is also defensible given the oracle comparison. This is an authorial choice.
**Not auto-fixed because:** Title is a strong rhetorical choice that authors should deliberately affirm or change.

---

### HRN-R1-003 — Limitation 1: CNN vs FC-MLP signal structure [clarity]
**Location:** Discussion, Limitation 1
**Issue:** The current Limitation 1 states that "absolute Δρ values may differ on native FC-MLP weights" but does not explain why the generalization gap signal might differ. CNN neurons have spatial filter structure (2D convolutional kernels) while FC-MLP neurons are fully dense weight vectors. The concept of "neuron influence concentration" (Gini coefficient, spectral decay ratio) may behave differently for these weight types.
**Recommendation:** Add one sentence: "In particular, neuron influence concentration metrics (Gini coefficient, spectral decay ratio) may capture different structural patterns in CNN filter banks versus FC-MLP weight matrices, potentially affecting the absolute magnitude of the equivariance advantage."
**Not auto-fixed because:** Requires domain knowledge judgment on whether this distinction is material; authorial call.

---

### HRN-R1-004 — Figure 1 caption clarity [formatting]
**Location:** Figure 1 caption
**Current text:** "NFT maintains ρ = 0.4886 ± <0.001 across all severity levels. flat-MLP declines from ρ = 0.303 at s = 0 to ρ = 0.143 at s = 1.0."
**Issue:** The ± notation for NFT's constant value is slightly confusing since the value is exactly constant (not approximately). Also, higher ρ = better prediction, but this is not stated in the caption.
**Recommendation:** Consider adding "(higher = better)" after "Spearman ρ" in the caption header, and replacing "± <0.001" with "(constant across all seeds)" for clarity.
**Not auto-fixed because:** Caption style is author's preference; both versions are acceptable.

---

---

## Round 2 (R2) — Verification and Credibility Review

### HRN-R2-001 — Mediation analysis terminology [clarity]
**Location:** Methodology §3 Mediation Analysis, Results §5.2
**Issue:** The paper describes the approach as "mediation analysis following the hierarchical regression framework of Baron & Kenny [1986]." However, the full Baron & Kenny protocol requires 4 steps (X→Y, X→M, M→Y, reduced X→Y when M controlled). The paper implements only a variance partitioning (ΔR²) that corresponds to steps 1 and 3 only.
**Recommendation:** Add a sentence clarifying: "Specifically, we implement variance partitioning (ΔR² = R²(NFT-base) − R²(flat-MLP+aug)) as an operationalization of the mediation concept, testing whether equivariant attention explains additional variance beyond augmentation."
**Not auto-fixed because:** Changing the framing of the mediation analysis is an authorial decision that may affect how the contribution is positioned.

---

### HRN-R2-002 — NFT absolute performance vs. prior work [clarity]
**Location:** Discussion or Limitation 1
**Issue:** Unterthiner et al. [2020] reported R² > 0.98 on their model zoo. NFT achieves R²≈0.30. The 3× gap is not discussed. A reviewer may ask: "Is this actually useful for practical property prediction?"
**Recommendation:** Add to Discussion or Limitation 1: "The absolute predictive performance (R²≈0.30 for NFT-base vs. R²>0.98 in Unterthiner et al.) reflects our dataset adaptation: the CNN zoo adapted to FC-MLP format provides fewer in-distribution models than Unterthiner et al.'s native setup (29,997 vs. 120K+ models), and the cross-architecture adaptation likely reduces the exploitable signal. Our contribution is the robustness differential, not a claim of matching Unterthiner et al.'s absolute performance."
**Not auto-fixed because:** Requires authorial judgment on framing and what level of explanation to add.

---

## Summary

| ID | Category | Location | Priority |
|----|---------|---------|---------|
| HRN-R1-001 | clarity | Methodology §3 Training | Low |
| HRN-R1-002 | style | Title | Low (author decision) |
| HRN-R1-003 | clarity | Discussion Limitation 1 | Low |
| HRN-R1-004 | formatting | Figure 1 caption | Low |
| HRN-R2-001 | clarity | Methodology §3 Mediation Analysis | Low |
| HRN-R2-002 | clarity | Discussion/Limitation 1 | Low |

**Total human review notes: 6**
**Auto-fixed: 0** (by design — MINOR issues are for human review only)
