# Adversarial Review Report — Round 2
# Paper: Measuring Structural Efficiency of Policy Movement: A Framework for Comparing Execution-RL and DPO in Code Generation
# Round: R2 — Verification and Credibility
# Generated: 2026-05-19T06:00:00Z
# Mode: UNATTENDED / Two-Persona Review (Accuracy Checker + Skeptical Expert)

---

## Ground Truth Verification Table

| Claim | Paper Location | Paper Value | Ground Truth | Match |
|-------|---------------|-------------|--------------|-------|
| GRPO-binary SEP | Table 1 | 0.2371 | 0.2371 | YES |
| GRPO-error-type SEP | Table 1 | 0.2371 | 0.2371 | YES |
| DPO SEP | Table 1 | 0.2377 | 0.2377 | YES |
| Mann-Whitney U statistic | Section 5.2 | 18,346.5 | 18346.5 | YES |
| Mann-Whitney p-value | Section 5.2 | 0.4248 | 0.4248 | YES |
| Effect size | Section 5.2 | −0.0072 | −0.0072 | YES |
| GRPO mean AST edit dist (h-e1) | Table in 5.1 | 3.500 | 3.500 | YES |
| DPO mean AST edit dist (h-e1) | Table in 5.1 | 1.000 | 1.000 | YES |
| Raw edit distance advantage | Section 5.2 / Intro | +250% | +250% | YES |
| Bootstrap CI lower bound | Section 5.1 table | 4.6500 | 4.6500 | YES |
| Bootstrap CI upper bound | Section 5.1 table | 8.7314 | 8.7314 | YES |
| Mean edit-per-KL differential | Section 5.1 table | 6.5047 | 6.5047 | YES |
| GRPO syntax pass rate | Section 5.1 | 6/6 (1.000) | 6/6 (1.000) | YES |
| DPO syntax pass rate | Section 5.1 | 6/6 (1.000) | 6/6 (1.000) | YES |
| N samples GRPO-binary (h-m1) | Table 1 | 192 | 192 | YES |
| N samples DPO (h-m1) | Table 1 | 189 | 189 | YES |
| Aliased pairs | Section 5.3 | 25 of 27 | 25/27 | YES |
| Real unique checkpoints | Section 5.3 | 2 (step-100, step-200) | 2 | YES |
| n_eff | Section 5.3 | ≈2 | ≈2 | YES |
| KL tolerance spec | Section 3.4 | ε=0.05 | 0.05 | YES |
| KL tolerance used | Section 3.4 | 0.15 | 0.15 | YES |
| GRPO learning rate | Table Sec 3.6 | 1e-6 | 1e-6 | YES |
| DPO learning rate | Table Sec 3.6 | 5e-7 | 5e-7 | YES |
| GRPO batch size | Table Sec 3.6 | 4 | 4 | YES |
| DPO batch size | Table Sec 3.6 | 2 | 2 | YES |
| GRPO KL beta | Table Sec 3.6 | 0.04 | 0.04 | YES |
| DPO KL beta | Table Sec 3.6 | 0.1 | 0.1 | YES |
| Bootstrap samples | Section 3.5 | 10,000 | 10,000 | YES |
| Dry-run SEP value | Section 5.2 | ≈0.238 | ≈0.238 | YES |
| CI text cite (lower bound) | Section 5.1 text | 4.65 | 4.6500 | YES (rounded, consistent) |
| CI text cite (upper bound) | Figure 2 caption | 8.73 | 8.7314 | YES (rounded, consistent) |
| N_min for mechanism analysis | Section 3.4 / 5.3 | 10 | 10 | YES |
| N_min for existence check | Section 5.3 | 5 | 5 | YES |
| +250% math check: (3.5−1.0)/1.0 | — | 250% | 250% | YES |

---

## Executive Summary

**Round 2 Focus:** Numerical verification, baseline fairness, credibility of novelty claims, and completeness of the corrected protocol.

**Numerical Accuracy:** All numerical claims in the paper match the ground truth exactly. No discrepancies found in SEP values, Mann-Whitney statistics, bootstrap CI bounds, sample sizes, hyperparameters, or aliasing counts. The +250% raw edit distance claim is arithmetically correct ((3.5−1.0)/1.0 = 2.5 = 250%). The truncation of CI lower bound from 4.6500 to 4.65 in running text is a legitimate rounding, not an inconsistency.

**Issue Counts:**
- FATAL: 0
- MAJOR: 3
- MINOR: 4

**Persuasiveness Assessment (R2):** The paper is numerically honest and self-consistent. All ground-truth values match. However, three MAJOR weaknesses remain: (1) an unfair framing of the raw/proportion dissociation by mixing h-e1 synthetic data with h-m1 real analysis without explicit per-figure labeling, (2) the "previously undocumented" novelty claim for checkpoint aliasing is not adequately hedged, and (3) the corrected protocol is actionable but missing one key item — DPO stub pair fix is described but the fix for GRPO mock completions is not directly tied to a specific file/function name.

**Recommendation:** CONTINUE (R3 optional if MAJOR issues are fixed; R2 MAJORs are fixable without structural change)

---

## FATAL Issues

*None found in R2.*

---

## MAJOR Issues

### MAJOR-R2-001
**Persona:** Accuracy Checker + Skeptical Expert  
**ID:** MAJOR-R2-001  
**Location:** Section 5.2 (paragraph on "raw/proportion dissociation"), Section 6.1 (Finding 2), Figure captions for Figure 4  
**Issue:** The "raw/proportion dissociation" is presented as a coherent single finding that mixes evidence from two separate sub-experiments using incompatible data sources. The "+250% raw edit distance" figure (GRPO=3.500, DPO=1.000) comes from h-e1 synthetic data with hand-crafted completions guaranteed to exhibit GRPO advantage. The "≈0.237 SEP near-equality" comes from h-m1 analysis on real checkpoints that are aliased (n_eff≈2). These are not from the same experiment. Presenting them side-by-side as a "dissociation" implies both sides of the comparison were measured under the same conditions, which they were not.

**Evidence:**
- Ground truth integrity_flags: "h-e1 uses synthetic (hand-crafted) code completions, not real training outputs" (HIGH severity)
- Ground truth integrity_flags: "h-m1 SEP analysis underpowered (n_eff≈2 due to checkpoint aliasing)" (HIGH severity)
- Paper Section 6.2 L1 acknowledges h-e1 is synthetic, but Section 5.2 and 6.1 do not repeat this caveat prominently when presenting the dissociation.

**Required Fix:** In Section 5.2 and 6.1 (Finding 2), add an explicit parenthetical each time the +250% figure is cited: "(h-e1 synthetic PoC data, not real training output)". Similarly, when citing the ≈0.237 SEP, add "(h-m1 preliminary, n_eff≈2, underpowered)". The reader of Section 5.2 should not need to cross-reference Section 6.2 to understand these are fundamentally different experimental contexts. Consider adding a one-sentence warning box or italicized note at the top of Section 5.2: "Note: raw edit distance results (Section 5.1) use synthetic PoC data; SEP results (this section) use real checkpoints with n_eff≈2 due to aliasing. These experiments address different questions and cannot be directly compared."

---

### MAJOR-R2-002
**Persona:** Skeptical Expert  
**ID:** MAJOR-R2-002  
**Location:** Section 1 (Contribution 4), Section 5.3, Section 6.1 (Finding 3)  
**Issue:** The claim that checkpoint aliasing is "previously undocumented" and "has not been previously documented" appears three times in the paper. The ground truth notes: "Claim of novelty cannot be fully verified without exhaustive literature review" (verified: true, caveat: "cannot be fully verified"). The paper does not hedge this claim adequately. A reviewer will immediately ask: has no one in the distributed systems, ML engineering, or RL fine-tuning reproducibility literature described this behavior before? The claim as written is falsifiable and the paper provides zero supporting evidence (no literature search result, no negative citation, no acknowledgment of uncertainty).

**Evidence:**
- Ground truth claim for "previously undocumented": verified=true, caveat="cannot be fully verified without exhaustive literature review"
- The paper uses the unhedged phrase "has not been previously documented" (Section 1 Contribution 4, Section 6.1)
- No negative citation or search rationale is provided

**Required Fix:** Replace "has not been previously documented" and "previously undocumented" with hedged language such as: "to the best of our knowledge, this failure mode has not been explicitly characterized in the RL fine-tuning literature." Add a single sentence acknowledging: "We conducted a literature search across ML systems and reproducibility literature and found no prior characterization of this specific failure mode, though we cannot exclude the possibility of prior references in grey literature or engineering documentation."

---

### MAJOR-R2-003
**Persona:** Skeptical Expert  
**ID:** MAJOR-R2-003  
**Location:** Section 4.3 (Conditions table), Section 6.2 (L4)  
**Issue:** The fairness of the GRPO vs. DPO comparison is compromised in a way the paper acknowledges (L4) but does not fully surface in the main Results section. The DPO condition in h-e1 uses stub preference pairs (`return None` as rejected completion) — not genuine execution-oracle-labeled pairs. This means DPO was trained on invalid preference data, which would naturally suppress DPO's structural activity and inflate the apparent GRPO advantage in raw edit distance (+250%). The limitation is stated in Section 6.2 L4, but not warned at the point of result presentation (Section 5.1, Table). A reader who stops at the Results section without reading Limitations will draw an unfair comparison conclusion.

**Evidence:**
- Ground truth integrity_flags: "DPO preference pairs in h-e1 are stub pairs (return None as rejected)" (MEDIUM severity, paper_acknowledgment: true)
- The +250% raw edit distance claim is presented in Section 5.1 without L4 caveat inline
- Section 4.3 describes DPO as "Execution-oracle preference pairs (passing solution preferred over failing)" — this describes the intended setup, but the actual implementation was stub pairs

**Required Fix:** Add a footnote or inline caveat in Section 5.1 immediately after the +250% comparison: "†DPO training used stub preference pairs (return None as rejected) rather than real execution-oracle pairs; this may suppress DPO's structural activity and inflate the apparent raw edit distance advantage. See Limitation L4." Also fix the Section 4.3 condition table: the DPO row should note "(intended: execution-oracle pairs; actual h-e1 implementation: stub pairs — see Section 6.2 L4)".

---

## MINOR Issues → human_review_notes

### MINOR-R2-001
**Type:** Precision / framing  
**Location:** Abstract, last sentence  
**Note:** "The framework is ready for deployment; the empirical question awaits a corrected run." This is a strong positive framing. While accurate, it may strike reviewers as overconfident given L4 (DPO stub pairs) and L1 (synthetic data) have not been resolved. Consider softening to: "The measurement framework is validated end-to-end; a corrected full-scale run with real training data and execution-oracle pairs is required to answer the empirical question."

### MINOR-R2-002
**Type:** Citation precision  
**Location:** References, Elhage et al. 2022  
**Note:** Ground truth flags this as "PARTIAL (likely arXiv:2112.00114, 2021)". The paper cites it as "2022" in text but the likely actual year is 2021. Verify year before final submission.

### MINOR-R2-003
**Type:** Internal consistency  
**Location:** Section 4.3 vs. Section 5.2 note  
**Note:** Section 4.3 presents GRPO-binary and GRPO-error-type as distinct experimental conditions with different reward signals. The note in Section 5.2 explains why they produce identical SEP statistics (both aliased to checkpoint-100). This is honest, but a reviewer may ask: why are two conditions presented as distinct in Section 4 if the actual analysis collapses them? Consider adding a forward reference in Section 4.3: "(Note: in the preliminary h-m1 run, both GRPO conditions produced identical SEP statistics due to checkpoint aliasing described in Section 5.3.)"

### MINOR-R2-004
**Type:** Clarification  
**Location:** Section 5.1, Table, row "Mean edit-per-KL"  
**Note:** The table shows "~25.9 (low-KL pairs)" and "~3.7 (low-KL pairs)" with tilde notation, while the bootstrap CI and mean differential rows use precise values (4.6500, 8.7314, 6.5047). The tilde values are less precisely stated. Clarify whether these approximate values are derived from the same bootstrap analysis or from a different calculation. If approximate, state "approx." explicitly.

---

## Ground Truth Verification Log (Full)

| Claim | Paper Value | Ground Truth Value | Match | Note |
|-------|-------------|-------------------|-------|------|
| GRPO-binary SEP | 0.2371 | 0.2371 | YES | |
| GRPO-error-type SEP | 0.2371 | 0.2371 | YES | |
| DPO SEP | 0.2377 | 0.2377 | YES | |
| SEP improvement direction | GRPO lower (−0.0006) | −0.0006 (GRPO lower) | YES | |
| Mann-Whitney U | 18,346.5 | 18346.5 | YES | |
| p-value | 0.4248 | 0.4248 | YES | |
| Significant | No (p>0.05) | false | YES | |
| Effect size | −0.0072 | −0.0072 | YES | |
| h-e1 GRPO AST dist | 3.500 | 3.500 | YES | |
| h-e1 DPO AST dist | 1.000 | 1.000 | YES | |
| +250% calculation | (3.5−1)/1=2.5=250% | +250% | YES | Math verified |
| Bootstrap CI lower | 4.6500 (table) / 4.65 (text) | 4.6500 | YES | Rounding acceptable |
| Bootstrap CI upper | 8.7314 (table) / 8.73 (caption) | 8.7314 | YES | Rounding acceptable |
| Mean differential | 6.5047 | 6.5047 | YES | |
| Syntax pass rate GRPO | 6/6 (1.000) | 6/6 (1.000) | YES | |
| Syntax pass rate DPO | 6/6 (1.000) | 6/6 (1.000) | YES | |
| N GRPO-binary h-m1 | 192 | 192 | YES | |
| N DPO h-m1 | 189 | 189 | YES | |
| Aliased pairs | 25/27 | 25/27 | YES | |
| Unique checkpoints | 2 | 2 | YES | |
| n_eff | ≈2 | ≈2 | YES | |
| ε spec | 0.05 | 0.05 | YES | |
| ε used | 0.15 | 0.15 | YES | |
| N_min mechanism | 10 | 10 | YES | |
| N_min existence | 5 | 5 | YES | |
| GRPO LR | 1e-6 | 1e-6 | YES | |
| DPO LR | 5e-7 | 5e-7 | YES | |
| GRPO batch | 4 | 4 | YES | |
| DPO batch | 2 | 2 | YES | |
| GRPO beta | 0.04 | 0.04 | YES | |
| DPO beta | 0.1 | 0.1 | YES | |
| Bootstrap samples | 10,000 | 10,000 | YES | |
| Dry-run SEP | ≈0.238 | ≈0.238 | YES | |
| ZSS citation | Zhang & Shasha 1989 | Verified | YES | |
| FA-AST citation | Wang et al. 2020 | Verified | YES | |
| Ding et al. year | 2024 | 2024 | YES | |
| Elhage et al. year | 2022 (text) | Likely 2021 | PARTIAL | MINOR-R2-002 |
| TRL citation | von Werra et al. 2020 | UNVERIFIED in Scholar | NOTE | Paper cites as software — acceptable |

---

## Persuasiveness Check Results (R2)

| Check | Result | Note |
|-------|--------|------|
| All numerical claims match ground truth | PASS | No discrepancies found |
| +250% math is correct | PASS | (3.5−1.0)/1.0 = 2.5 = 250% |
| Bootstrap CI is internally consistent | PASS | 4.6500 in table, 4.65 in text — legitimate rounding |
| n_eff≈2 explanation is consistent | PASS | Consistent across Sections 4.4, 5.3, 6.1, 6.2 L2 |
| KL tolerance discrepancy acknowledged | PASS | Section 3.4 explicitly states both 0.05 spec and 0.15 used |
| Synthetic data caveat in abstract | PASS | "proof-of-concept data" stated |
| n_eff caveat prominent in Results | PARTIAL FAIL | Section 5.2 buries aliasing note after result table; should be top-of-section |
| Raw/proportion dissociation fairly framed | FAIL | Mixes incompatible data sources without inline warning (MAJOR-R2-001) |
| "Previously undocumented" adequately hedged | FAIL | No hedging language, no negative citation (MAJOR-R2-002) |
| DPO stub pair limitation flagged at point of use | FAIL | L4 exists in Limitations but not at Section 5.1/4.3 (MAJOR-R2-003) |
| Corrected protocol complete and actionable | PARTIAL PASS | 5 steps are logical; step 2 references smoke_test_experiment.py specifically — adequate |
| h-e1 vs h-m1 scope distinction maintained | PASS | Consistent throughout |
| No overclaiming of SEP near-equality | PASS | Consistently labeled "preliminary" |
| SEP validation against functional outcomes acknowledged | PASS | L5 explicitly states this gap |

---

## Summary for Revision Agent

**FATAL issues to fix:** 0

**MAJOR issues to fix (ordered by priority):**

1. **MAJOR-R2-001 (HIGH PRIORITY):** Add explicit inline caveats when presenting the raw/proportion dissociation. In Section 5.2 paragraph and Section 6.1 Finding 2, label "+250%" as "(h-e1 synthetic PoC only)" and "≈0.237 SEP" as "(h-m1 preliminary, n_eff≈2)". Add one-sentence warning note at top of Section 5.2.

2. **MAJOR-R2-002 (MEDIUM PRIORITY):** Hedge the "previously undocumented" claim to "to the best of our knowledge, not previously characterized in the RL fine-tuning literature." Add one sentence on search methodology.

3. **MAJOR-R2-003 (MEDIUM PRIORITY):** Add L4 caveat footnote at Section 5.1 table (+250% row). Fix Section 4.3 DPO condition description to note stub pair implementation.

**MINOR issues (human_review_notes — do not auto-fix):**
- MINOR-R2-001: Abstract final sentence — consider softening
- MINOR-R2-002: Elhage et al. year (2021 vs 2022) — verify before submission
- MINOR-R2-003: Section 4.3 forward reference to aliasing note
- MINOR-R2-004: Clarify tilde vs. precise values in Section 5.1 table

**Recommendation:** CONTINUE to R3 after MAJOR fixes applied. All three MAJORs are localized text additions (no structural changes to paper required). After fixes, R3 should verify the caveats were added correctly and check final coherence.

**Persuasiveness post-fix assessment:** Once MAJOR-R2-001 through 003 are addressed, the paper will be numerically honest, internally consistent, and appropriately hedged. It will read as a credible methods/infrastructure contribution with transparent preliminary findings — a defensible framing for a venue like DL4C or similar workshop tracks.
