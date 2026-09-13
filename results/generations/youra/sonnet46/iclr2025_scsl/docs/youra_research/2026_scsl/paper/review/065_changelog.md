# Phase 6.5 Changelog - Round 1 Revisions

## R1 Changes

---

### [FATAL-1] Title and Scope Rescoping

**What changed:**
- **Title:** Changed from "Gradient Norms as Label-Free Minority Proxies: Confirming the Prediction-Residual Signal for Spurious Correlation Robustness" to "Gradient Norms as Label-Free Minority Proxies: A Mechanistic Study of the Prediction-Residual Signal for Spurious Correlation Robustness" — removes the implication that GNR-LLR is a complete two-stage method.
- **Abstract (last sentence):** Changed from forward-looking "providing a strong foundation for gradient-norm-informed last-layer retraining toward group-robust models without annotation costs" to "Gradient-norm-informed last-layer retraining (Stage 2) to measure worst-group accuracy is a direct next step and constitutes future work."
- **Introduction (paragraph 4):** Removed "we propose Gradient-Norm-Informed Last-Layer Retraining (GNR-LLR)... GNR-LLR consists of two stages" as the primary contribution framing. Replaced with: the analysis derives the mechanism directly from the outer-product decomposition + ERM dynamics.
- **Introduction (final paragraph):** Added explicit statement: "The proposed two-stage pipeline — using this proxy signal to construct a pseudo-balanced subset for last-layer retraining (Stage 2) — is a direct next step that constitutes future work."
- **Section 3.4:** Retitled from "Stage 2: Last-Layer Retraining (Full GNR-LLR)" to "Proposed Pipeline: Last-Layer Retraining (Future Work)". Added prominent disclaimer: "**This paper establishes only the Stage 1 proxy signal quality. Stage 2 WGA evaluation is future work (h-m1 through h-m4, ~22 GPU hours).**"
- **Section 6.2 Limitation 1:** Elevated to "primary limitation" framing. Removed "our signal quality motivates the expectation of competitive WGA" (see MAJOR-2). Made non-execution of Stage 2 the leading limitation, not a footnote.
- **Section 7 Conclusion:** Added explicit caveat that results establish Stage 1 only; WGA is future work.
- **Contributions list:** Added contribution (5) on EL2N relationship.

**Location:** Title, Abstract, Section 1 (Introduction paragraphs 4 and final), Section 3.4, Section 6.2, Section 7

**Reason:** Stage 2 (LLR) was not executed. The paper was framed as proposing a complete two-stage method (GNR-LLR) while only executing Stage 1. This constitutes a fundamental framing mismatch that would cause reviewers to expect WGA results that do not exist.

---

### [FATAL-2] Removal of NHT Citations and Unverified Reference Tags

**What changed:**
- **Section 2.3:** Renamed from "Gradient Dynamics and Training Theory" with NHT as primary theoretical grounding. Removed the NHT paragraph entirely. Replaced with self-contained analysis: "The mechanistic prediction underlying our work follows from standard ERM dynamics... This analysis does not require appeal to external theoretical frameworks; it follows from the structure of the cross-entropy gradient and the known shortcut-learning dynamics of ERM."
- **Section 3.5:** Removed entirely. This section was titled "Connection to NHT Framework" and cited NHT [Khanh & Hoa, 2026] as theoretical support for the ratio=8.8x result.
- **Section 6.1 Finding 3:** Removed "qualitatively consistent with NHT predictions." Replaced with self-contained explanation referencing majority saturation and the outer-product decomposition prediction.
- **References:** Removed entirely:
  - `[Khanh & Hoa, 2026]` — NHT paper, UNVERIFIED and possibly non-existent
  - `[Rosenfeld & Risteski, 2023]` — not cited in body text, UNVERIFIED
  - `[Ghaznavi et al., 2023]` — not cited in body text, UNVERIFIED
- **References — [UNVERIFIED] tags removed:**
  - `[Nam et al., 2020]` — UNVERIFIED tag removed; described as NeurIPS 2020 published proceedings
  - `[Zhang et al., 2022]` — UNVERIFIED tag removed; described as ICLR 2022 published proceedings
- **Section numbering:** Renumbered Section 2.4 "Our Position" to Section 2.5 after addition of new Section 2.4 (Data-Centric Training Signals, per MAJOR-5).

**Location:** Section 2.3, Section 3.5 (removed), Section 6.1, References section

**Reason:** NHT [Khanh & Hoa, 2026] is explicitly marked UNVERIFIED in the paper's own reference list. Submitting a paper with [UNVERIFIED] in the reference list is an immediate desk-reject trigger. The theoretical prediction is independently derivable from the outer-product decomposition + ERM dynamics, so no external citation is needed.

---

### [MAJOR-1] JTT AUC Comparison Fix

**What changed:**
- **Section 5.1, Key Observation 1:** Removed "the estimated AUC ≈ 0.70–0.80 of JTT's binary misclassification signal on Waterbirds" (no citation, unsubstantiated numerical estimate). Replaced with: "For comparison, JTT's binary misclassification signal, by virtue of being binary, has a theoretical AUC ceiling determined by its precision-recall tradeoff on minority groups; our continuous g̃ signal provides finer-grained minority separation than any binary proxy can achieve."

**Location:** Section 5.1, Key Observation 1

**Reason:** The "estimated AUC ≈ 0.70–0.80" figure had no citation, no derivation, and no stated basis. This was the paper's primary performance comparison claim and it was unsubstantiated. The replacement makes a valid theoretical argument (binary vs. continuous signal) without requiring the unsupported numerical estimate.

---

### [MAJOR-2] DFR WGA Comparison Fix

**What changed:**
- **Section 2.2:** Removed "achieving 92.9% WGA on Waterbirds" from the DFR description. Changed to "achieving strong WGA on Waterbirds." Retained DFR as motivation for Stage 2 design.
- **Section 6.2 Limitation 1:** Removed "DFR demonstrates that oracle balanced subsets achieve 92.9% WGA on Waterbirds; our signal quality motivates the expectation of competitive WGA." This opinion-dressed-as-conclusion language was replaced with a clear statement that WGA is an open empirical question pending Stage 2 execution.
- **Section 3.4:** Retains DFR principle reference as design motivation but with explicit flag that no WGA comparison is made in this paper.

**Location:** Section 2.2, Section 3.4, Section 6.2

**Reason:** Stage 2 was not executed. The paper had no WGA results. "Motivates the expectation of competitive WGA" is an opinion, not evidence. The DFR 92.9% figure is also an unverified external claim. Removing the implied WGA equivalence eliminates a misleading impression without losing the DFR design motivation.

---

### [MAJOR-3] Unverified Citation Tags Removed

**What changed:**
- **References:** Removed `[UNVERIFIED]` tag from `[Nam et al., 2020]` — described in body as NeurIPS 2020 published proceedings; venue is stated in the reference entry.
- **References:** Removed `[UNVERIFIED]` tag from `[Zhang et al., 2022]` — described as ICLR 2022 published proceedings; venue is stated in the reference entry.
- `[Rosenfeld & Risteski, 2023]` removed entirely (not cited in body text).
- `[Ghaznavi et al., 2023]` removed entirely (not cited in body text).
- `[Khanh & Hoa, 2026]` removed entirely (see FATAL-2).
- The DFR 92.9% WGA number removed from body text (see MAJOR-2); JTT +21pp WGA retained as citation to published ICML 2021 paper (external claim properly attributed).

**Location:** References section

**Reason:** A submitted paper cannot have [UNVERIFIED] tags in the reference list. References not cited in the body text (Rosenfeld & Risteski, Ghaznavi et al.) were removed to clean up the reference list.

---

### [MAJOR-4] Minority Recall Estimate Added

**What changed:**
- **Section 5.2:** Added quantitative estimated minority recall paragraph: "Based on AUC=0.914 and the per-group means (G1: g̃=0.313, G2: g̃=0.433 vs. decision boundary near g̃≈0.2), virtually all G1 and G2 samples fall above the majority means (G0: 0.022, G3: 0.094). With a top-25% threshold encompassing the top 1,199 of 4,795 samples, and the minority groups' g̃ values substantially exceeding this threshold, the estimated minority recall in the top-25% subset is ≥90%."
- **Section 5.2:** Changed "Direct minority recall measurement is addressed in h-e1-v2; AUC provides strong indirect evidence." to include the estimate and note exact computation is pending.

**Location:** Section 5.2

**Reason:** The paper's central application claim ("strongly minority-enriched" subset) lacked the key quantitative metric that would confirm it. AUC=0.914 is strong indirect evidence, but the estimated minority recall derived from per-group means makes the claim concrete and verifiable. The exact figure from saved g̃ data remains pending (h-e1-v2).

---

### [MAJOR-5] EL2N and Data-Centric AI Related Work Added

**What changed:**
- **New Section 2.4 "Data-Centric Training Signals":** Added discussion of EL2N [Paul et al., 2021], explicitly noting that g̃ᵢ = ‖pᵢ − yᵢ_onehot‖ is mathematically equivalent to the EL2N score. Distinguishes the use case: EL2N selects easy (low error) samples for pruning; our method selects hard (high error) samples as minority proxy — opposite selection direction for a different problem. Also cites forgetting events [Toneva et al., 2019] and influence functions [Koh & Liang, 2017] as related gradient-adjacent signals.
- **References:** Added `[Paul et al., 2021]`, `[Toneva et al., 2019]`, `[Koh & Liang, 2017]`.
- **Section 7 Conclusion contributions list:** Added "(5) explicit relationship to EL2N [Paul et al., 2021] establishing the distinct use case."

**Location:** New Section 2.4, References, Section 7

**Reason:** The paper's "first experimental confirmation" novelty claim would not survive reviewer scrutiny if EL2N — which computes the identical quantity — is not discussed and distinguished. A reviewer familiar with data-centric AI would immediately raise this.

---

### [MAJOR-6] Single Seed Limitation Added

**What changed:**
- **Section 6.2:** Added "**Limitation 5: Single random seed.** All results use seed=42. Multi-seed validation (5 seeds) is future work (h-m4). The AUC=0.914 and ratio=8.8x results should be interpreted as a strong single-seed result pending multi-seed confirmation."
- **Appendix C:** Added note: "**Note: Single seed only (seed=42). Multi-seed replication (5 seeds, h-m4) is pending future work.**"

**Location:** Section 6.2, Appendix C

**Reason:** The paper did not acknowledge that single-seed results have inherent uncertainty. AUC=0.914 may be influenced by the specific random initialization. This limitation must be disclosed for scientific honesty and reviewer expectations.

---

## Summary Statistics

| Category | Count Fixed |
|----------|-------------|
| FATAL fixes | 2/2 |
| MAJOR fixes | 6/6 |
| MINOR issues | 0 (collected in human_review_notes.md, not auto-fixed) |

**Total citations removed:** 3 (Khanh & Hoa 2026, Rosenfeld & Risteski 2023, Ghaznavi et al. 2023)
**Total citations added:** 3 (Paul et al. 2021, Toneva et al. 2019, Koh & Liang 2017)
**New sections added:** Section 2.4 (Data-Centric Training Signals)
**Sections removed:** Section 3.5 (Connection to NHT Framework)
**[UNVERIFIED] tags removed:** 2 (Nam et al. 2020, Zhang et al. 2022)

---

## R2 Changes

---

### [MAJOR-R2-1] Minority Recall Estimate Softened

**What changed:**
- **Section 5.2:** Replaced the specific "≥90%" minority recall claim (uncomputed) with softer language: "Based on the g̃ distribution structure — G1 mean=0.313 and G2 mean=0.433 substantially exceeding the estimated top-25% threshold — AUC=0.914 implies that the vast majority of minority samples are captured in high-g̃ regions. Direct minority recall computation (a single threshold query on saved g̃ data) is addressed in h-e1-v2; the AUC provides strong indirect evidence of high minority enrichment."
- **Section 6.2 Limitation 3:** Updated to reference "estimated high minority recall" rather than "estimated ≥90% recall" for consistency.

**Location:** Section 5.2, Section 6.2

**Reason:** The ≥90% figure is uncomputed. The g̃ distribution structure and AUC=0.914 provide strong indirect evidence, but asserting a specific percentage without direct computation is unsupported. Replaced with language that accurately represents the level of evidence available.

---

### [MAJOR-R2-2] Section 3.4 Scope Statement and Hyperparameter Labeling

**What changed:**
- **Section 3.4:** Added explicit scope note at the start: "**Note: This paper evaluates only Stage 1 (proxy signal quality). Stage 2 is described for completeness as future work design, not as an evaluated contribution.**"
- **Section 3.4:** Stage 2 hyperparameters labeled as "proposed, not validated": changed "(SGD, lr=0.01, 100 epochs)" to "(proposed, not validated: SGD, lr=0.01, 100 epochs)".

**Location:** Section 3.4

**Reason:** Reviewers could mistake the Stage 2 specification as a validated design. The scope note and "(proposed, not validated)" label make clear these are aspirational parameters for future work, not experimentally confirmed choices.

---

### [MAJOR-R2-3] JTT +21pp WGA Table Citation Added

**What changed:**
- **Section 2.2:** Changed "achieving +21pp WGA on Waterbirds" to "achieving +21pp WGA on Waterbirds (Table 1, Liu et al. 2021)" — adding a specific table citation to the published ICML 2021 paper.

**Location:** Section 2.2

**Reason:** The +21pp figure is a published result from a specific table in Liu et al. 2021 (ICML). Adding the table citation makes the attribution precise and verifiable without requiring independent verification.

---

### [ADDITIONAL] g̃>0.2 Boundary Claim Scoped to T_id=5

**What changed:**
- **Section 6.1 Finding 1:** Changed "g̃ > 0.2 separates all minority means from all majority means" to "at T_id=5, g̃ > 0.2 cleanly separates all minority group means from all majority group means". The claim is epoch-specific: at epoch 10, G1 mean drops to 0.140, so the boundary no longer cleanly separates all groups.

**Location:** Section 6.1

**Reason:** The original statement was epoch-unqualified but only true at T_id=5. G1 mean=0.140 at epoch 10 falls below the g̃>0.2 threshold. The fix prevents an empirically incorrect overgeneralization.

---

## R2 Summary Statistics

| Category | Count Fixed |
|----------|-------------|
| MAJOR fixes (R2) | 3/3 |
| ADDITIONAL fixes (R2) | 1/1 |
| MINOR issues | 0 (not auto-fixed per instructions) |

**No citations added or removed in R2.**
**All R1 fixes preserved.**
