# Adversarial Review — Round 1 (R1)
# Three-Persona Adversarial Review: Accuracy and Engagement
# Generated: 2026-05-03T14:05:00Z

**Paper:** Human→AI Annotation Drift: Measuring Directional Stylistic Adaptation in RLHF Preference Datasets via the Alignment Asymmetry Index
**Round:** R1 — Accuracy and Engagement
**Personas:** Accuracy Checker · Bored Reviewer · Skeptical Expert
**Ground Truth:** 065_ground_truth.yaml (all claims pre-verified)

---

## Executive Summary

| Severity | Found | By Persona |
|----------|-------|------------|
| FATAL    | 0     | — |
| MAJOR    | 4     | Bored: 1 structural; Skeptical: 3 scientific |
| MINOR    | 3     | See human_review_notes |

**Persuasiveness Check:**
- Abstract compelling? YES (concrete numbers in sentence 2)
- Problem clear in 1 minute? YES
- Novelty clear in 2 minutes? YES
- Figure 1 self-explanatory? UNKNOWN (no captions in text → MAJOR-001)
- Would continue reading? YES
- Attention lost at: §3 (dense notation, acceptable)

**Recommendation:** MAJOR_REVISION — 4 MAJOR issues must be addressed before R2.

---

## Ground Truth Verification Summary

All 15 numerical claims cross-checked against `065_ground_truth.yaml` and `verification_state.yaml`.

**Result: 0 numerical discrepancies found.** All values match within rounding conventions (see Accuracy Checker table below).

---

## PERSONA 1: ACCURACY CHECKER

### Ground Truth Verification Table

| Claim | Paper Value | Ground Truth | Match |
|-------|-------------|--------------|-------|
| β_L early (value) | −0.025 | −0.0248 | ✓ rounded |
| β_L early (CI) | [−0.043, −0.006] | [−0.043, −0.006] | ✓ exact |
| β_L late (value) | +0.056 | +0.0555 | ✓ rounded |
| β_L late (CI) | [+0.043, +0.068] | [+0.043, +0.068] | ✓ exact |
| Δβ_L | +0.080 | 0.0803 | ✓ rounded |
| β_H delta | +0.021 | 0.0210 | ✓ exact |
| β_S delta | +0.012 | 0.0116 | ✓ rounded |
| β_Q (late) | −0.017 | −0.0170 | ✓ exact |
| n_directional | 1 of 3 | 1 | ✓ |
| β_exposure | 0.041 | 0.0407 | ✓ rounded |
| β_exposure p | 2.05×10⁻⁵ | 2.05e-05 | ✓ |
| tercile F | 82.92 | 82.92 | ✓ exact |
| tercile p | ≈1.4×10⁻³⁶ | 1.4e-36 | ✓ |
| placebo_p | 0.48 | 0.48 | ✓ exact |
| HH-RLHF rows | 160,800 | 160,800 | ✓ exact |
| HH-RLHF strata | 3 × 53,600 | 3 × 53,600 | ✓ exact |
| WebGPT rows | 19,578 | 19,578 | ✓ exact |
| interaction_p | 1.0 | 1.0 | ✓ exact |
| topic imbalance p | 4×10⁻²⁷⁵ | 4.0e-275 | ✓ |
| Bonferroni β_L p | 0.000 | 0.0 | ✓ |
| bootstrap iters | 2,000 | 2000 | ✓ |
| placebo iters | 200 | 200 | ✓ |
| embedding model | all-MiniLM-L6-v2 | all-MiniLM-L6-v2 | ✓ |
| embedding dims | 384 | 384 | ✓ |
| train_test_split | 75/25 | 0.75 | ✓ |

**Accuracy Checker Verdict: FATAL=0, MAJOR=0. Paper is numerically accurate.**

---

## PERSONA 2: BORED REVIEWER

*"I'm a busy NeurIPS/ICML reviewer with 5 papers today."*

### Engagement Assessment

**Abstract:** Opens with generic framing ("RLHF assumes stable preferences"), then delivers the verbosity reversal with concrete numbers in sentence 2. The specific claim (Δβ_L = +0.080, non-overlapping CIs) appears early enough. Practical implication in final sentence.
- Assessment: Adequate. Could be stronger by leading with the reversal.

**Introduction §1:** Paragraph 1 opens with the verbosity sign flip and concrete numbers — β_L = −0.025 early, β_L = +0.056 late. This is excellent hook execution.

**Attention analysis:**
- Abstract: COMPELLING — concrete numbers, specific claim ✓
- Introduction: EXCELLENT — leads with the reversal ✓
- Related Work: ADEQUATE — organized into subsections ✓
- Methodology §3: DENSE but necessarily so; math-heavy readers expect this ✓
- Results: CLEAR — Table 1 effectively displays the coefficient comparison ✓

**MAJOR ISSUE — MAJOR-001: Figure Captions Absent**

The paper references figures throughout:
- §5.1: "Figure 1 shows these coefficients with confidence interval bars (figures/fig1_coefficient_comparison.png)"
- §5.2: "Figure 2 shows the projection scores across annotator terciles (figures/dose_response.png)"
- §5.2: "Figure 3, figures/discriminant_validity.png"

No figure captions are provided anywhere in the paper text. ICML requires proper figure captions. Reviewers reading figures rely on captions to understand without re-reading the paper body. This is a critical submission-readiness gap.

**Additionally:** Figure numbering is inconsistent. The statistics block at paper end lists:
- primary: `fig1_coefficient_comparison.png, dose_response.png, discriminant_validity.png`
- secondary: `fig3_feature_stability_rounds.png, fig5_topic_balance.png`

But §5.1 references "Figure 3" as `fig3_feature_stability_rounds.png`, while §5.2 calls `discriminant_validity.png` "Figure 3" as well. Two figures labeled "Figure 3."

**Required fix:** Add formal figure captions with `\caption{}` blocks; resolve figure numbering conflict.

**Bored Reviewer Verdict: FATAL=0, MAJOR=1 (MAJOR-001: figure captions absent + numbering conflict)**

---

## PERSONA 3: SKEPTICAL EXPERT

*"I'm a domain expert looking for holes to reject this paper."*

### MAJOR-002: AUC Near Chance Not Disclosed in Main Paper

**Issue:** The logistic regression classifiers underlying H-M2 achieve near-chance AUC: `early_auc = 0.4952`, `late_auc = 0.5111` (from `verification_state.yaml h-m2.validation`). These values are not reported in the paper.

**Why this is MAJOR:** A skeptical reviewer will ask: "If your classifier achieves AUC ≈ 0.50 (chance level), how meaningful are the coefficient estimates you derive from it?" This is a legitimate challenge. The coefficient estimates from a near-chance logistic regression may be unreliable.

**Counter-argument available:** Logistic regression coefficients can be statistically significant (and their confidence intervals non-overlapping) even when overall AUC is near chance, because AUC measures overall discrimination ability while individual coefficient CIs measure the precision of individual feature weight estimates. The sign and magnitude of β_L can be reliable even when the model cannot reliably discriminate individual preference labels. This is especially true when n is large (53,600 per stratum).

**Required fix:** Report `early_auc` and `late_auc` in Table 1 or §5.1, and add a sentence explaining why AUC near chance does not undermine the coefficient comparison inference. This turns a vulnerability into a transparent methodological note.

---

### MAJOR-003: Multiple Comparisons Across Three Hypothesis Tests Not Addressed

**Issue:** The paper conducts three separate hypothesis tests (H-E1, H-M1, H-M2) and reports significance across all three without applying family-wise error correction. Within H-E1, Bonferroni correction is applied (α = 0.0167 for 3 features). But across the three experiments, no correction is mentioned.

**Specific concern:** H-M1 reports `p = 2.05×10⁻⁵` for β_exposure. H-M2 reports non-overlapping CIs for β_L. These are the two primary positive results. With three experiments, a Bonferroni-corrected threshold would be α/3 ≈ 0.017 — H-M1's p=2.05e-5 still passes. But reviewers will ask.

**Required fix:** Add a sentence in §4.3 or §5.4 noting that primary significance thresholds remain below Bonferroni-corrected levels across the three experiments (α = 0.05/3 ≈ 0.017; H-M1 p = 2.05e-5 << 0.017). This is a straightforward addition that preempts reviewer challenge.

---

### MAJOR-004: AAI Incompleteness Not Foregrounded Enough in Abstract/Introduction

**Issue:** The abstract describes AAI as "a composite instrument that measures directional stylistic adaptation in preference labels" and says "We validate the first two components on HH-RLHF and WebGPT." A reader skimming the abstract will conclude AAI is fully validated. The incompleteness (H-M3: reward model behavioral divergence; H-M4: benchmark degradation not executed) is relegated to Discussion L3.

**Why this is MAJOR:** A skeptical reviewer will say: "You present AAI as a complete instrument but only validate 2 of 3 components. This undermines your contribution claim." The limitations section does address this, but the abstract and contributions in the Introduction do not sufficiently flag that the behavioral divergence component is unvalidated.

**Required fix:** In the Abstract, after "We validate the first two components on HH-RLHF and WebGPT," add: "(the behavioral divergence component, H-M3/H-M4, is specified but not yet executed)." In Contribution 2 in §1, add "(components 1-2 validated; component 3 specified for future work)." This is honest and actually strengthens credibility.

---

### Novelty Assessment

1. **"First computational evidence of verbosity preference shift across annotation strata"** — SUPPORTED. Distinguishable from Thakur et al. [2024] (LLM judges ≠ human annotators; evaluation ≠ training data).
2. **"Coefficient-resolution directionality"** — NOVEL. Prior work measures magnitude variance (Coste et al.), not directional sign change with bootstrap CI non-overlap.
3. **"Minimum data requirements specification"** — NOVEL. The null results as forward-looking specification is genuinely useful.

### Missing Limitations Check

- L1 (no genuine temporal metadata): ✓ stated §6.2
- L2 (WebGPT worker IDs absent): ✓ stated §6.2
- L3 (AAI 2/3 components): ✓ stated §6.2
- L4 (topic imbalance): ✓ stated §6.2
- Multiple comparisons: ✗ NOT stated → MAJOR-003
- Near-chance AUC: ✗ NOT stated → MAJOR-002

**Skeptical Expert Verdict: FATAL=0, MAJOR=3 (MAJOR-002, MAJOR-003, MAJOR-004)**

---

## SUMMARY: ALL ISSUES

### FATAL Issues (0)
*None found.*

### MAJOR Issues (4)

| ID | Persona | Section | Issue | Fix Required |
|----|---------|---------|-------|--------------|
| MAJOR-001 | Bored Reviewer | §5.1, §5.2 | Figure captions absent; figure numbering conflict (two "Figure 3"s) | Add `\caption{}` blocks for all 5 figures; renumber consistently |
| MAJOR-002 | Skeptical Expert | §5.1, Table 1 | Near-chance AUC (early=0.4952, late=0.5111) not reported or explained | Report AUC in Table 1; add 1 sentence explaining why near-chance AUC does not undermine coefficient inference |
| MAJOR-003 | Skeptical Expert | §4.3 or §5.4 | Multiple comparisons across 3 hypothesis tests not addressed | Add note that H-M1 p=2.05e-5 << Bonferroni-corrected α=0.017 across 3 tests |
| MAJOR-004 | Skeptical Expert | Abstract, §1 Contributions | AAI incompleteness insufficiently foregrounded in Abstract/Introduction | Add explicit note in Abstract and Contribution 2 that component 3 (H-M3/H-M4) is specified but not executed |

### MINOR Issues (for human_review_notes — NOT auto-fixed)

| ID | Section | Type | Issue |
|----|---------|------|-------|
| MINOR-001 | §5.2 | Clarity | "between-group regression on WebGPT" — reader needs to remember §3.6 design; add brief parenthetical "(tercile proxy — worker IDs absent)" |
| MINOR-002 | §5.2 | Formatting | "Figure 3, figures/discriminant_validity.png" — informal path reference in body text; should use formal "Figure N" only |
| MINOR-003 | Abstract | Style | Abstract opens with generic "RLHF assumes..." framing; narrative blueprint called for leading with the reversal |

---

## PERSUASIVENESS VERDICT

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Concrete numbers in sentence 2 |
| Problem clear in 1 minute? | PASS | §1 paragraph 1 gives the reversal |
| Novelty clear in 2 minutes? | PASS | "The gap" subsection is explicit |
| Figure 1 self-explanatory? | FAIL (MAJOR-001) | No captions available |
| Would continue reading? | YES | Opening reversal is genuinely surprising |
| Attention lost at | §3 (acceptable) | Math-heavy but necessary |
| False novelty claims | 0 | All novelty claims are supported |
| Unfair baselines | 0 | No competing methods exist; acknowledged |
| Overclaims | 1 → MAJOR-004 | AAI "complete instrument" framing |
| Missing limitations | 2 → MAJOR-002/003 | AUC + multiple comparisons |

**persuasiveness_passed: false** (MAJOR-001 blocks — no figure captions)

---

## SUMMARY FOR REVISION AGENT

Priority fix order:

1. **MAJOR-001** (CRITICAL): Add figure captions for all 5 figures. Resolve figure numbering (currently two "Figure 3"s). Maps to §5.1, §5.2, §5.3.

2. **MAJOR-002** (HIGH): Report early_auc=0.4952 and late_auc=0.5111 in Table 1 or §5.1. Add 1 sentence: "Near-chance AUC is expected when individual preference labels are noisy, but does not undermine coefficient-level inference — the coefficient estimates and their CIs remain valid under large-n logistic regression even when marginal discrimination is weak."

3. **MAJOR-003** (HIGH): Add to §4.3 or §5.4: "Across the three hypothesis tests, the primary significance threshold (p = 2.05×10⁻⁵ for H-M1) remains well below the Bonferroni-corrected family-wise threshold (α = 0.05/3 ≈ 0.017)."

4. **MAJOR-004** (MEDIUM): In Abstract, after "We validate the first two components on HH-RLHF and WebGPT," add: "(the reward-model behavioral divergence component is specified but not yet executed — see §6.2)." In §1 Contribution 2 add explicit parenthetical.

5. **MINOR issues** → collect in `065_human_review_notes.md` (do NOT auto-fix).

---

*Review generated by Phase 6.5 Adversarial Review workflow v2.0*
*Personas: accuracy_checker, bored_reviewer, skeptical_expert*
