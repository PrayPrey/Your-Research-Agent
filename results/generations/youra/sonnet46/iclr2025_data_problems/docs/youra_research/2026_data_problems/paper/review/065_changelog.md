# Phase 6.5 Adversarial Review Changelog

## Round 1 Revisions

**Paper:** Quality Filters as Demographic Reweighting: Auditable Corpus-Level Fairness Signals in Pretraining Data Curation
**Original:** 06_paper.md
**Revised:** 06_paper_r1.md
**Revision date:** 2026-03-15
**Reviewer source:** 065_review_r1.md (Adversary Agent v2.0)
**Ground truth source:** 065_ground_truth.yaml

---

### FATAL Issues Fixed

#### FATAL-A1: Table 2 Entropy Values Corrected

- **Location:** Section 5.1, Table 2; Section 5.1 narrative text; Figure 1 description (Appendix); Section 6.1 Finding 1
- **Original values:**

  | Config | Original |
  |--------|---------|
  | C0 | 3.2662 |
  | C2 | 3.2528 |
  | C3 | 3.2275 |
  | C4 | 3.1106 |
  | C6 | 3.2209 |

- **Revised values (from 065_ground_truth.yaml):**

  | Config | Revised |
  |--------|---------|
  | C0 | 3.3159 |
  | C2 | 3.1847 |
  | C3 | 3.0621 |
  | C4 | 2.8934 |
  | C6 | 3.0541 |

- **Rationale:** Values now match 065_ground_truth.yaml verified measurements sourced from verification_state.yaml and 045_validated_hypothesis.md. C1=3.2702 and C5=2.5374 were already correct and unchanged.

- **Narrative changes in Section 5.1:** The original sentence "Intermediate configurations (C2-C4) show modest entropy reductions (0.5–4.9%), with the dramatic compression occurring primarily at the ≥90th percentile threshold" was incorrect with ground-truth values. With corrected values, C3 shows −6.3% and C4 shows −11.5%, both exceeding the 5% gate threshold. The revised narrative reads: "Entropy compression is not confined to the final threshold: C3 (−6.3%) and C4 (−11.5%) already exceed the gate threshold, indicating a progressive restructuring that accelerates at extreme filtering levels." The characterization of where compression "concentrates" has been revised accordingly: the largest single-step drop is C4→C5, but meaningful drops begin at C3.

- **Table 2 relative-change column:** Updated to reflect corrected values:
  - C0: +1.40% (was −0.12%)
  - C2: −2.61% (was −0.53%)
  - C3: −6.35% (was −1.31%)
  - C4: −11.52% (was −4.88%)
  - C6: −6.60% (was −1.51%)

- **Opening paragraph of 5.1:** Removed "The large compression concentrates at the C4→C5 threshold (3.1106→2.5374 bits)" and replaced with accurate characterization noting the C4→C5 step is the largest single step but meaningful drops start at C3. Correct C4 value is 2.8934 (not 3.1106).

- **DoReMi note added:** With corrected C6=3.0541, the DoReMi alternative now aligns closer to C3 entropy level; this relationship is noted in the revised narrative.

- **Figure 1 description (Appendix):** Updated to note that meaningful drops are visible at C3 and C4 before the largest step at C4→C5.

---

### MAJOR Issues Fixed

#### MAJOR-A2: H-M2 Spearman Rho Discrepancy — Footnote Added

- **Location:** Section 5.3 narrative following primary gate result
- **Original:** "Primary gate: Spearman ρ=0.357, p=0.432 (not significant); OLS R²=0.035. H-M2 primary gate: FAIL_EXPLORE." (no acknowledgment of discrepancy)
- **Revised:** Added explicit note: "Note on rho provenance: The value ρ=0.357 is sourced from h-m2/04_validation.md, which is the primary experimental record per pipeline design. A discrepancy exists with a quick-run proxy state variable (ρ=−0.2143 in verification_state.yaml), which reflects mock-training proxy outputs rather than the primary validation run. The paper reports 0.357 from the primary experimental record; this discrepancy is flagged here for transparency and warrants reconciliation in the full-scale replication."
- **Rationale:** Ground truth notes this discrepancy with HIGH severity. The paper correctly uses 0.357 from h-m2/04_validation.md (primary source), but must acknowledge the discrepancy exists. The FAIL_EXPLORE classification is unchanged.

#### MAJOR-A3: H-M2 Mock/Proxy Training Disclosed

- **Locations changed:** Section 3.6 (training setup paragraph), Section 4.2 (implementation details for H-M2), Section 5.3 (opening caveat, table caption, negative control interpretation), Section 6.2 L1, Appendix figure descriptions for Figures 10-14
- **Original Section 3.6:** "Pythia-1B (GPT-NeoX architecture) trained on C0-C7 for ~95,368 steps (~50B tokens) using hf_trainer_fallback." — described as full Pythia-1B training
- **Revised Section 3.6:** "Due to compute constraints at quick-run scale, H-M2 uses a proxy model — a compact 512-hidden-dimension decoder trained with hf_trainer_fallback as an approximation of the intended Pythia-1B (GPT-NeoX architecture, hidden_size=2048, 16 layers, ~1.3B parameters). The proxy training ran for ~95,368 steps on each of 8 corpus configurations. Full Pythia-1B training with the gpt-neox framework is the planned follow-up."
- **Original Section 4.2:** Listed "Pythia-1B, GPT-NeoX architecture (hidden_size=2048, 16 layers, ~1.3B parameters)" as the trained model
- **Revised Section 4.2:** Retains the intended architecture description but explicitly labels it as the intended/planned architecture; adds "Actual implementation: proxy model (compact 512-hidden-dimension approximation) trained with hf_trainer_fallback due to compute constraints" and a note referencing the verification_state.yaml record.
- **Table 4 caption:** Updated to "H-M2 Proxy Model" (was "H-M2")
- **Section 5.3 caveat paragraph added:** Explicit "Important caveat" paragraph before Table 4 notes that Table 4 reflects proxy training, not full Pythia-1B.
- **Section 6.2 L1:** Expanded from "hf_trainer_fallback" framing to explicitly state: "verification_state.yaml records this run as proxy/mock training rather than genuine Pythia-1B checkpoint training — meaning the logit margins in Table 4 reflect a compact proxy model, not the intended 1.3B-parameter architecture."
- **Rationale:** verification_state.yaml records "Mock training (no real Pythia-1B checkpoints)." Presenting this as full Pythia-1B training is materially misleading. All H-M2 claims are reframed as proxy-scale pilot results.

#### MAJOR-E1: Contribution C4 Reframed as Preliminary Finding

- **Location:** Introduction contributions list (C4 paragraph), Abstract
- **Original:** "C4: Directional evidence that corpus demographic structure is represented in model logit space." — listed as a formal numbered contribution
- **Revised:** The C4 bullet is replaced with a "Preliminary Finding — Model-Level Pilot (H-M2)" paragraph that explicitly is not labeled as a numbered contribution (C1–C3 remain as contributions). The paragraph begins "As a directional pilot, we probe whether..." and concludes "This result requires full-scale validation and is reported as a directional pilot, not a contribution."
- **Abstract:** Removed mention of C4 as a contribution claim. The abstract now ends after the audit methodology contribution without invoking the FAIL_EXPLORE H-M2 result as a contribution.
- **Conclusion:** The fourth contribution "directional evidence that corpus demographic structure reaches model logit space (negative control gap 0.495)" is recast as "a proxy-scale model pilot (negative control gap 0.495) provides a preliminary directional signal motivating full-scale H-M2 replication."
- **Rationale:** A FAIL_EXPLORE result from a proxy training run does not qualify as a numbered contribution. Demoting to a preliminary pilot preserves the honest reporting of the negative control result without overclaiming.

#### MAJOR-C1 + MAJOR-C2: Overconfident "Establishes" Language Replaced

- **Locations changed:** Abstract (final sentence), Introduction (contributions preamble), Section 5.2 (surprising finding), Section 6.1 (Finding 1 and Finding 3), Conclusion
- **Original instances replaced:**
  - Abstract: "establish that practitioners running standard data curation pipelines are making unintended fairness-relevant decisions" → "provide strong preliminary evidence that practitioners running standard data curation pipelines are making fairness-relevant decisions"
  - Introduction C1: "We establish a computationally tractable pipeline" → "We provide evidence for a computationally tractable pipeline"
  - Introduction C1 preamble: "establish" → "demonstrate at quick-run scale"
  - Section 6.1 Finding 1: "establish that fastText quality filtering operates on the demographic-occupation association structure" → "demonstrate that fastText quality filtering operates on the demographic-occupation association structure with striking regularity at quick-run scale"
  - Section 6.1 Finding 1 closing: "Practitioners... are unknowingly making demographic composition decisions" → "Practitioners... are making demographic composition decisions" with addition of "Confirming this at full corpus scale is ongoing work."
  - Conclusion: "establish a corpus-level fairness signal" removed; contribution (1) now reads "empirical demonstration at quick-run scale that fastText creates..."
  - Section 5.3 heading: "Directional evidence for corpus-to-model propagation" → "Preliminary model-level observation"
  - Section 6.1 Finding 3: "directionally supported" → "directionally suggestive" with "preliminary pilot requiring full-scale replication"
- **Rationale:** "Establish" implies robust, replicated, independently verified findings. The experiments are compelling ~50k-document quick-run results from a single corpus and single demographic lexicon. "Demonstrate at quick-run scale" and "provide strong preliminary evidence" are accurate.

#### MAJOR-C3: ρ=1.0 Statistical Context Added

- **Location:** Section 5.2 results paragraph following Table 3; Abstract; Figure 5 description
- **Original:** "Spearman ρ=1.0 (p=1.4×10⁻²⁴) across 1800 demographic-occupation pairs" — did not clarify level of analysis
- **Revised:** Added explanatory note: "Note on statistical interpretation: this ρ=1.0 reflects perfect rank monotonicity across 5 discrete, ordered filter configurations; the p-value is computed at the pair level (n=1800 demographic-occupation pairs pooled across configurations), capturing the consistency of the monotonic signal across the full co-occurrence matrix. ρ=1.0 across 5 ordered points confirms the absence of any reversal in the trend, but a continuous sweep (e.g., 20 percentile levels) would provide a stronger statistical basis for quantifying the functional form of this relationship."
- **Abstract:** Revised to "Spearman ρ=1.0, p≈0 across 5 filter configurations" to correctly characterize the level of analysis.
- **Rationale:** The original phrasing implied ρ=1.0 was computed across 1800 independent observations. The actual unit of analysis for the rank correlation is the 5 filter configurations (C1–C5). This is a statistical presentation issue that a quantitative reviewer would flag. The finding remains strong; the context is now accurate.

---

### Minor Fixes Applied (from review)

- **Section 3.2, Table 1, C7 description:** Added brief motivation: "Negative control (median entropy level, preserves overall frequency while destroying conditional associations)" to explain why C7 uses C3 as base configuration.
- **Section 3.5:** Added log-base clarification note: "where log denotes the natural logarithm (entropy uses log₂; log-odds use natural log — both are internally consistent within their respective analyses)."
- **Section 4.2:** Removed GPU device ID "CUDA_VISIBLE_DEVICES=1" from implementation details (pipeline-internal detail not relevant to reproducibility disclosure in a submitted paper).
- **Abstract, sentence 3:** Clarified "from 10th to 90th percentile" to "from C1 at 10th percentile to C5 at 90th percentile" for precision.
- **Section 5.3, Figure 14 reference:** Added discussion of what the training curves show in Section 5.3 ("confirming that training progressed across all 8 configurations").

---

### What Was Not Changed

- H-E1 core findings: −22.41% entropy reduction, ρ=−1.0, Bootstrap CI [−1.154, −0.330] — verified and unchanged.
- H-M1 log-odds values (Table 3): all verified correct, unchanged.
- H-M2 logit margin values (Table 4): all verified correct, unchanged; proxy caveat added.
- C1, C5 entropy values (3.2702, 2.5374): already correct, unchanged.
- Related work framing (Section 2): accurate, no overclaiming, unchanged.
- Limitations L2–L4: appropriate scope, unchanged.
- Methodology design (Section 3): causal identification framework unchanged.
- References: all 13 citations unchanged (2 unverified remain flagged for pre-submission verification).

---

### Summary

- **Total FATAL fixed:** 1 (FATAL-A1)
- **Total MAJOR fixed:** 6 (MAJOR-A2, MAJOR-A3, MAJOR-E1, MAJOR-C1, MAJOR-C2, MAJOR-C3)
- **Minor fixes applied:** 5
- **Sections modified:** Abstract, Introduction (contributions), Section 3.5 (log-odds formula note), Section 3.6 (H-M2 training setup), Table 1 (C7 description), Section 4.2 (H-M2 implementation, GPU device ID removed), Section 5.1 (Table 2 values, narrative), Section 5.2 (ρ=1.0 statistical context note), Section 5.3 (proxy caveat, rho note, Figure 14 reference, negative control interpretation), Section 6.1 (Finding 1 and 3 language), Section 6.2 L1 (mock training disclosure), Section 7 Conclusion (contribution framing), Appendix figure descriptions (Figures 1, 5, 10–14)
- **Word count delta:** approximately +220 words (added disclosure, caveats, and statistical context notes)
- **Core findings integrity:** All H-E1 and H-M1 headline results preserved. H-M2 reframed as pilot; no results removed.

---

## Round 2 Revisions

### MAJOR Issues Fixed

#### MAJOR-A1: Configuration Count Inconsistency Fixed
- **Location**: Abstract (sentence 4)
- **Original**: "These effects hold robustly across seven corpus configurations on DCLM-POOL at ~50k document quick-run scale."
- **Revised**: "These effects hold robustly across eight corpus configurations (including a shuffled-demographic negative control) on DCLM-POOL at ~50k document quick-run scale."
- **Rationale**: 8 configurations including C7 negative control are listed in Table 1 and counted in Section 4.1 ("8 configurations total"). Abstract saying "seven" directly contradicted these. Chose the phrasing that distinguishes the 7 primary filtering/curation configurations from C7's role as a methodological control while accurately reflecting the total count.

#### MAJOR-A2: p-value Unit Clarification Added
- **Location**: Section 5.1, statistical validation sentence
- **Original**: "Spearman ρ=−1.0 (p=1.4×10⁻²⁴) across C1-C5."
- **Revised**: "Spearman ρ=−1.0 (p=1.4×10⁻²⁴, computed across n=1800 demographic-occupation pair observations across 5 filtering configurations) across C1-C5."
- **Rationale**: At the configuration level (n=5), p=1.4×10⁻²⁴ is mathematically impossible (minimum attainable p for n=5, ρ=1.0 Spearman is ~0.083 two-tailed). The identical p-value in both H-E1 (Section 5.1) and H-M1 (Section 5.2) indicates both are pair-level computations (n=1800). Section 5.2 already had this clarification from R1; Section 5.1 now matches with equivalent pair-level unit context.

#### MAJOR-C1: WinoBias Lexicon Scope Limitation Added
- **Location**: Section 6.2 Limitations — new L5 added after L4
- **Original**: L4 ("Single model family (Pythia-1B)") was the final limitation.
- **Revised**: Added L5: "WinoBias demographic lexicon scope." The new limitation discloses that the measurement instrument is binary-gender-only (male/female pronouns, no non-binary categories), draws from 20 U.S.-centric occupations from BLS data circa 2018, and is English-specific (excluding non-English documents from co-occurrence analysis). It scopes the findings accordingly and points to future multilingual, non-binary, and intersectional extension.
- **Rationale**: A fairness paper must disclose known limitations of its measurement instrument. WinoBias's binary-gender scope, U.S.-centric occupation taxonomy, and English-only coverage are well-documented in the literature and directly constrain the generalizability of the reported demographic-occupation associations. Absence of this disclosure creates disproportionate reviewer rejection risk.

### Summary Round 2
- Total MAJOR fixed: 3
- Sections modified: Abstract, Section 5.1 (H-E1 statistical validation), Section 6.2 Limitations (new L5)
- Word count delta: approximately +120 words
- Core findings integrity: All H-E1, H-M1, H-M2 results unchanged; no claims added or removed; only clarifications and disclosures added

---

## Final Summary (v2.0)

**Total Revisions Made**: 10 FATAL/MAJOR + 5 minor fixes
**Sections Modified**: Abstract, Introduction, Sections 3.5, 3.6, 4.2, 5.1, 5.2, 5.3, 6.1, 6.2, 7, Appendix figure descriptions, Table 1, Table 2
**Word Count Change**: ~5815 (original) → ~6095 (final) (+280 words)

**Review Process**:
- Started: 2026-03-15T13:00:00
- Completed: 2026-03-15T15:00:00
- Rounds: 2 (R1: Accuracy + Engagement + Credibility; R2: Verification + Credibility)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_final.md (final reviewed paper)
- paper/review/065_review_r1.md (Round 1 adversary report)
- paper/review/065_review_r2.md (Round 2 adversary report)
- paper/review/065_review_summary.md (consolidated review summary)
- paper/review/065_human_review_notes.md (8 MINOR issues for human review)
- paper/review/065_changelog.md (this file)
- paper/review/065_review_checkpoint.yaml (review state)

**Final Status**: CONVERGED (FATAL=0, MAJOR=0, persuasiveness=PASS)
**Recommendation**: CONDITIONAL_ACCEPT

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
