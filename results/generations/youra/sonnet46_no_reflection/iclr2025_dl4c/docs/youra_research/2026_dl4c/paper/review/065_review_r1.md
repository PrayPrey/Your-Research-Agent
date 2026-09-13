# Adversarial Review Report — Round 1
# Paper: "Measuring Structural Efficiency of Policy Movement: A Framework for Comparing Execution-RL and DPO in Code Generation"
# Round: R1 — Accuracy and Engagement
# Generated: 2026-05-19T12:35:00Z
# Mode: UNATTENDED / Three-Persona Review

---

## Ground Truth Summary

| Metric | Ground Truth Value | Source |
|--------|-------------------|--------|
| GRPO-binary SEP | 0.2371 | h-m1 Phase 4 (aliased, n_eff≈2) |
| GRPO-error-type SEP | 0.2371 | h-m1 Phase 4 (aliased, n_eff≈2) |
| DPO SEP | 0.2377 | h-m1 Phase 4 (aliased, n_eff≈2) |
| Mann-Whitney U | 18,346.5 | h-m1 Phase 4 |
| p-value | 0.4248 | h-m1 Phase 4 (not significant) |
| Effect size | -0.0072 | h-m1 Phase 4 (GRPO lower) |
| GRPO mean AST edit dist (PoC) | 3.500 | h-e1 PoC (SYNTHETIC data) |
| DPO mean AST edit dist (PoC) | 1.000 | h-e1 PoC (SYNTHETIC data) |
| Bootstrap CI (PoC) | [4.6500, 8.7314] | h-e1 PoC (SYNTHETIC data) |
| Mean differential (PoC) | 6.5047 | h-e1 PoC |
| n_eff (h-m1) | ≈2 | Checkpoint aliasing |
| Aliased pairs | 25/27 | Checkpoint aliasing |
| KL tolerance used | 0.15 | h-m1 (spec was 0.05) |

---

## Executive Summary

| Severity | Count | Resolved Recommended |
|----------|-------|---------------------|
| FATAL    | 1     | MUST FIX            |
| MAJOR    | 3     | MUST FIX            |
| MINOR    | 3     | → human_review_notes (NOT auto-fixed) |

**Persuasiveness Assessment:**
- abstract_compelling: TRUE
- problem_clear_in_1_minute: TRUE
- novelty_clear_in_2_minutes: TRUE
- would_continue_reading: TRUE
- attention_lost_at: NULL

**Overall Recommendation:** REVISE (1 FATAL + 3 MAJOR must be resolved)

---

## FATAL Issues

### SKEPT-FATAL-001: Impossible Future Citation [Jiang et al., 2025]

**Persona:** Skeptical Expert
**Location:** Section 2.1 (Related Work), References section
**Severity:** FATAL

**Issue:**
Section 2.1 cites: "CodeRL+ [Jiang et al., 2025] shows that variable-level execution trajectory rewards outperform binary pass/fail by +4.6% pass@1, suggesting reward granularity affects outcome."

The corresponding reference is: "[Jiang et al., 2025] Xue Jiang et al. CodeRL+: Improving Code Generation via Reinforcement with Execution Semantics Alignment. arXiv:2510.18471, 2025."

The arXiv ID `2510.18471` encodes October 2025 (2510 = year 2025, month 10). The paper header states format "ICML2025" which has a submission deadline of approximately January–February 2025. A paper submitted to ICML 2025 cannot cite a paper that appears on arXiv in October 2025 — this is a temporal impossibility.

**Why this is FATAL:**
- If targeting ICML 2025: citation is impossible (postdates submission deadline by ~9 months)
- If targeting ICML 2026 or NeurIPS 2026: the format header "ICML2025" is wrong
- Either way, the citation as written cannot stand without correction
- A reviewer or program chair who notices this dates inconsistency will reject the paper or flag it as fabricated

**Required Fix:**
Option A (if submitting to ICML 2025 or earlier 2025 venue): Remove [Jiang et al., 2025] citation entirely. The paper does not require it — CodeRL (Le et al., 2022) and TÜLU 3 (Lambert et al., 2024) sufficiently establish the execution-RL landscape.

Option B (if submitting to 2026 venue): Update the paper format header from "ICML2025" to the correct venue, and verify the Jiang et al. 2025 citation is genuine.

**Evidence:** Reference list entry "arXiv:2510.18471, 2025" — arXiv ID prefix 2510 = October 2025.

---

## MAJOR Issues

### BORED-MAJOR-001: Introduction Framing Gap — Criticizes pass@1 But Cannot Provide Alternative at Scale

**Persona:** Bored Reviewer
**Location:** Section 1 (Introduction), paragraphs 2–3
**Severity:** MAJOR

**Issue:**
The Introduction strongly argues that pass@1 is insufficient: "A model fine-tuned with GRPO-binary might achieve +3% pass@1 over DPO, but this number alone tells us nothing about whether the model has learned to structure programs differently." This sets up an expectation that the paper will provide structural efficiency measurements that pass@1 cannot.

However, the paper's actual experiments never run GRPO and DPO to completion at scale. The h-e1 experiment uses synthetic (hand-crafted) data and the h-m1 experiment is underpowered (n_eff≈2). The paper thus criticizes pass@1 as insufficient but cannot provide its alternative metric at scale either.

A reviewer will ask: "You say pass@1 is insufficient — but you haven't provided structural efficiency at scale either. So what have you actually given me beyond a framework?" The Introduction creates an implicit promise that the paper partially fails to fulfill, which a careful reviewer will notice.

**Required Fix:**
Revise the Introduction framing to acknowledge upfront that this paper provides the *measurement framework* and a *proof-of-concept* rather than a full-scale comparison. The gap between pass@1's limitations and this paper's contribution should be framed as "we provide the tool to answer this question" rather than implying the answer will be provided. The revised framing should appear by the end of Introduction paragraph 2 or in the contributions list.

Suggested addition after the pass@1 critique paragraph:
> "In this paper, we provide the measurement framework and proof-of-concept validation that makes this structural question answerable — though a full-scale comparison awaits the corrected experimental protocol described in Section 6.3."

### BORED-MAJOR-002: "Preliminary Empirical Analysis" in Contributions List Undermines Paper Position

**Persona:** Bored Reviewer
**Location:** Section 1, Contribution 3 bullet
**Severity:** MAJOR

**Issue:**
Contribution 3 reads: "**3. A preliminary empirical analysis with a surprising finding.**"

Using the word "preliminary" in a contributions bullet is unusual and potentially damaging for ICML submission. It signals to reviewers that the work is incomplete. Most ICML papers present contributions as definitive. Even when findings are preliminary, the contribution is typically framed as what was learned, not the incompleteness of what was done.

The actual contribution IS interesting and publishable: the raw/proportion dissociation (GRPO more aggressive in absolute structural terms but not proportionally more semantic) is a real finding worth reporting, even if underpowered. The checkpoint aliasing is a strong methodological contribution. The framing should lead with what was found, not with its preliminary status.

**Required Fix:**
Reframe Contribution 3 to lead with the finding and frame the limitations as context, not as the defining characteristic:

Current: "A preliminary empirical analysis with a surprising finding."

Suggested: "A proof-of-concept empirical finding: despite GRPO exhibiting substantially higher *raw* semantic AST edit distances, the Semantic Edit Proportion is nearly identical for both methods — a raw/proportion dissociation that challenges the selective-reallocation hypothesis and motivates a corrected experimental run (Section 6.3)."

This reframing presents the finding as a genuine intellectual contribution while the "motivated corrected run" signals the paper is honest about its scope.

### SKEPT-MAJOR-001: Missing Limitation — SEP Not Validated to Correlate with Functional Correctness

**Persona:** Skeptical Expert
**Location:** Section 6.2 (Limitations) — missing
**Severity:** MAJOR

**Issue:**
The paper proposes Semantic Edit Proportion (SEP) as a diagnostic metric for code generation alignment, yet never validates that higher SEP correlates with better functional outcomes (pass@1, generalization, robustness). The implicit assumption is that "more edits targeting semantic nodes = better alignment," but this is never established.

A skeptical reviewer will ask: "Is high SEP actually desirable? Could a model with high SEP be making many structural changes that are wrong? Is there evidence that SEP predicts anything we care about?"

Section 6.4 (Broader Impact) mentions "The framework should not be used to make deployment decisions… until validated" but this is buried in Broader Impact, not Limitations, and does not explicitly name the correlation-with-correctness gap.

**Required Fix:**
Add an explicit limitation to Section 6.2:

**L5: SEP not validated against functional outcomes.**
The structural efficiency metric and SEP have not been validated against functional correctness measures (pass@1, ECE, OOD transfer). A high SEP model might make more structural changes that are wrong. The framework measures *structural activity* of policy movement, not *correctness* of that movement. Establishing the correlation between SEP and downstream performance is a prerequisite for using structural efficiency as an alignment quality indicator rather than merely a descriptive diagnostic. This validation is part of the future work in Section 7.2.

### SKEPT-MAJOR-002: GRPO-Binary and GRPO-Error-Type Identical Results Not Explained

**Persona:** Skeptical Expert
**Location:** Section 5.2, Table 1; Section 5.3
**Severity:** MAJOR

**Issue:**
Table 1 presents two separate GRPO conditions (GRPO-binary and GRPO-error-type) with completely identical results: Mean SEP=0.2371, N=192, Mann-Whitney U=18,346.5, p=0.4248 for both. These conditions use different reward functions (binary +1/0 vs. error-taxonomy), yet produce absolutely identical statistics.

While this is explainable by the checkpoint aliasing (both conditions reused the same h-e1 checkpoints, so they analyzed the same underlying data), this explanation is not explicit in the Results section. A reviewer seeing two supposedly different conditions with identical results will immediately suspect an error, duplicated data, or sloppy reporting.

Currently Section 5.3 explains the aliasing for "GRPO" collectively but does not explicitly link this to the Table 1 duplication or explain that both conditions analyzed the same physical checkpoint files.

**Required Fix:**
Add an explicit note immediately after Table 1:

> "Note: GRPO-binary and GRPO-error-type produce identical SEP statistics because the h-m1 analysis reused h-e1 checkpoints, and the checkpoint aliasing confound (Section 5.3) caused both conditions to analyze the same aliased checkpoint-100 files. The two reward functions would produce different checkpoints in a corrected run with dedicated full-scale training; the present results cannot distinguish their structural effects."

---

## MINOR Issues → human_review_notes

### ACC-MINOR-001: Figure 4 Caption Asymmetric Rounding
**Location:** Figure 4 caption
**Type:** clarity
**Note:** Caption states "GRPO: 0.237, DPO: 0.238" — asymmetric rounding (GRPO rounds down, DPO rounds up from 0.2377). Main text says "nearly identical (≈0.237)" for both. While technically both roundings are correct, the asymmetry slightly overstates the difference. Consider using "≈0.237" for both in the caption, consistent with the main text.

### BORED-MINOR-001: Abstract Final Sentence Tone
**Location:** Abstract, final sentence
**Type:** style
**Note:** "The framework is ready for deployment; the empirical question awaits a corrected run." This is clever but may read as self-congratulatory or dismissive of the incomplete empirical work. Consider: "The framework is validated and ready to apply; the key empirical question — whether SEP_GRPO > SEP_DPO — requires the corrected protocol described in Section 6.3."

### SKEPT-MINOR-001: Elhage et al. Year Mismatch
**Location:** Section 2.4 in-text citation and References list
**Type:** typo/formatting
**Note:** In-text cites "[Elhage et al., 2022]" but reference entry says "Transformer Circuits Thread, 2021." The arXiv ID (likely 2112.00114) is from December 2021. Correct the in-text citation year to 2021, or verify the correct year and update both locations consistently.

---

## Ground Truth Verification Log

| Claim | Paper Value | Ground Truth | Match |
|-------|-------------|--------------|-------|
| GRPO-binary SEP | 0.2371 | 0.2371 | ✅ |
| GRPO-error-type SEP | 0.2371 | 0.2371 | ✅ |
| DPO SEP | 0.2377 | 0.2377 | ✅ |
| Mann-Whitney U | 18,346.5 | 18346.5 | ✅ |
| p-value | 0.4248 | 0.4248 | ✅ |
| Effect size | -0.0072 | -0.0072 | ✅ |
| GRPO AST edit dist (PoC) | 3.500 | 3.500 | ✅ |
| DPO AST edit dist (PoC) | 1.000 | 1.000 | ✅ |
| Bootstrap CI | [4.6500, 8.7314] | [4.6500, 8.7314] | ✅ |
| Mean differential | 6.5047 | 6.5047 | ✅ |
| Aliased pairs | 25/27 | 25/27 | ✅ |
| KL tolerance used | 0.15 | 0.15 | ✅ |
| N samples GRPO h-m1 | 192 | 192 | ✅ |
| N samples DPO h-m1 | 189 | 189 | ✅ |
| n_eff | ≈2 | ≈2 | ✅ |
| Citation [Jiang et al., 2025] timeline | arXiv Oct 2025 | ICML2025 format | ❌ FATAL |

---

## Persuasiveness Check Results

| Check | Result | Notes |
|-------|--------|-------|
| abstract_compelling | TRUE | Clear problem, honest framing, interesting dissociation finding |
| problem_clear_in_1_minute | TRUE | Opening sentence + paragraph clear |
| novelty_clear_in_2_minutes | TRUE | Four contributions listed clearly |
| figure_1_self_explanatory | NULL | Cannot verify from markdown; caption is adequate |
| would_continue_reading | TRUE | Despite limitations, paper is intellectually engaging |
| attention_lost_at | NULL | No single dropout point; Discussion is dense but appropriate |
| false_novelty_claims_found | 0 | No overclaims; composition novelty is defensible |
| unfair_baseline_comparisons | 0 | Paper consistently caveats all comparisons |
| overclaims_found | 0 | Paper is unusually honest about its limitations |
| tone_overclaiming_found | 0 | No hype language; if anything, slightly undersells |
| missing_limitations | TRUE | SEP-correctness correlation not in Limitations (→ SKEPT-MAJOR-001) |

---

## Summary for Revision Agent

### Priority 1 — FATAL (MUST FIX)
1. **SKEPT-FATAL-001**: Remove or replace [Jiang et al., 2025] citation (arXiv:2510.18471 postdates ICML 2025 deadline). Simplest fix: remove the CodeRL+ sentence from Section 2.1 or replace with a non-future citation. The sentence about "variable-level execution trajectory rewards" is nice context but not essential.

### Priority 2 — MAJOR (MUST FIX)
2. **BORED-MAJOR-001**: Add explicit framing in Introduction that this paper provides the *measurement tool*, not the full-scale comparison. One sentence acknowledging the framework/PoC scope before the contributions list.
3. **BORED-MAJOR-002**: Reframe Contribution 3 from "A preliminary empirical analysis" to lead with the finding (raw/proportion dissociation), with "preliminary" context following.
4. **SKEPT-MAJOR-001**: Add L5 to Section 6.2 Limitations: SEP not validated against functional outcomes.
5. **SKEPT-MAJOR-002**: Add explanatory note after Table 1 that GRPO-binary and GRPO-error-type identical results are due to shared aliased checkpoints.

### Priority 3 — MINOR → human_review_notes (DO NOT AUTO-FIX)
6. **ACC-MINOR-001**: Fig 4 caption rounding asymmetry
7. **BORED-MINOR-001**: Abstract last sentence tone
8. **SKEPT-MINOR-001**: Elhage et al. year mismatch (2022 vs. 2021)
