# Adversarial Review — Round 1

**Paper:** Adversarial Fragility and Calibration Are Anticorrelated After Capability Control: A Residual Instability Analysis Across 30 Large Language Models
**Reviewed:** 2026-05-12T17:05:00
**Reviewer Version:** Adversary Agent v2.0 (inline execution)
**Round:** R1 — Accuracy and Engagement

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 1 | NEEDS_WORK |
| Engagement | 0 | 1 | NEEDS_WORK |
| Credibility | 0 | 3 | NEEDS_WORK |
| **TOTAL** | **0** | **5** | NEEDS_WORK |

**Recommendation:** MINOR_REVISION (no fatal issues; 5 major issues require fixes before submission)

**Overall Assessment:** The paper is scientifically sound with a genuinely counterintuitive finding, well-structured argument, and honest limitations section. The core numbers are verified correct against ground truth. However, five MAJOR issues require resolution: one numerical inconsistency (Mistral p-value), one engagement weakness (Figure 1 not showing key finding), two overclaiming issues (abstract/conclusion scope), and one methodological blind spot (arc_challenge circularity).

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Verification Table

| Metric | Paper Claims | Ground Truth | Match? |
|--------|-------------|--------------|--------|
| ρ(RI, ECE\|PC1, mean_conf) | −0.535 | −0.5347 | ✓ |
| p-value (primary) | 0.0034 | 0.0034 | ✓ |
| 95% CI | [−0.782, −0.101] | [−0.782, −0.101] | ✓ |
| n models | 30 | 30 | ✓ |
| n families | 9 | 9 | ✓ |
| SD(AdvGLUE_drop) | 0.1212 | 0.1212 | ✓ |
| R²_residualization | 0.529/0.5285 | 0.5285 | ✓ |
| VIF (all covariates) | 1.000 | 1.000 | ✓ |
| PC1 variance explained | 68.5% | 68.54% | ✓ |
| ρ after outlier removal | −0.498 | −0.498 | ✓ |
| Baseline ρ(PC1, ECE) | −0.511 | −0.511 | ✓ |
| OLS-estimated models | 73% / 22/30 | 22/30 | ✓ |
| Bootstrap samples | 10,000 | 10,000 | ✓ |
| Mistral ρ | −0.827 | −0.827 | ✓ |
| Mistral p-value | 0.042 | 0.042 (raw); 0.519 (Holm) | ✗ INCONSISTENCY |
| LLaMA ρ | −0.244 | −0.244 | ✓ |
| Qwen ρ | +0.364 | +0.364 | ✓ |
| Fisher z-stat | −0.561 | −0.561 | ✓ |
| Outliers removed | 3 | 3 | ✓ |

### FATAL Issues — Accuracy

*None found.*

### MAJOR Issues — Accuracy

#### MAJOR-ACC-001: Mistral p-value ambiguity — raw vs Holm-corrected

**Location:** Section 5.3, Per-Family Analysis table
**Issue:** The paper reports Mistral ρ=−0.827 with p=0.042 in the per-family table (column header "p (Holm)"). However, h-m1/04_validation.md reports: raw p=0.173, Holm-corrected p=0.519. The value 0.042 appears to be neither the raw nor the Holm-corrected p-value from the validation report. This is a numerical inconsistency between the paper and its source data.

**Evidence:** 
- Paper (Section 5.3 table): `Mistral | 6 | −0.827 | 0.519 | Negative` — wait, the paper correctly shows 0.519 in the Holm column. But in Section 5.3 prose: "Mistral's strong anticorrelation (ρ=−0.827) is consistent with heavy RLHF application" and in ground_truth.yaml: `rho: -0.827, p: 0.042`. The 0.042 in the ground truth file is inconsistent with the Holm p=0.519 in the validation report.

**Resolution:** The ground_truth.yaml has p=0.042 for Mistral which propagated to paper prose. The validation report shows raw p=0.173, Holm p=0.519. The paper's Table 5.3 actually shows 0.519 (correct) but the ground_truth.yaml entry is wrong. The paper table is internally correct. However, the ground_truth.yaml claim `p: 0.042` is inconsistent with the source. This must be clarified to prevent future propagation errors.

**Suggested Fix:** Add a footnote to Section 5.3: "Per-family Holm-corrected p-values are all non-significant (all > 0.05); Mistral raw p=0.173, Holm p=0.519. Family-level correlations are exploratory only." Correct ground_truth.yaml to show both raw and Holm values.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✓ PASS | Strong hook: "paradoxically, better calibrated"; concrete numbers |
| Problem clear in 1 min? | ✓ PASS | "coupled failure cascade" framing clear in first paragraph |
| Novelty clear in 2 min? | ✓ PASS | RI construct and inverted finding stated explicitly |
| Figure 1 self-explanatory? | ✗ FAIL | Figure 1 = RI distribution (not the key finding); key scatter is Figure 4 |
| Would continue reading? | ✓ YES | Counterintuitive result + clear writing compels reading |

**Attention Lost At:** Section 5.2 Key Observation 2 ("RI adds minimal unique signal beyond capability") — undermines the paper's own contribution narrative mid-results section.

### FATAL Issues — Engagement

*None found. The paper's hook and abstract are strong.*

### MAJOR Issues — Engagement

#### MAJOR-ENG-001: Figure 1 does not convey the key finding

**Location:** Section 3.4 and Section 5.1 (Figure 1 reference)
**Issue:** The paper positions Figure 1 as showing "the RI distribution" (violin plot by family/regime). A bored reviewer scanning figures first will see RI variance across families — informative for construct validity, but not the central *finding*. The central finding (anticorrelation between RI and ECE) is in Figure 4 (partial regression scatter). Standard practice for high-impact papers is to put the main result figure first or make Figure 1 a schematic of the key insight.

**Reader Impact:** A reviewer who glances at Figure 1 first and doesn't understand why RI variance matters will be confused about the paper's core claim before reading the text.

**Suggested Fix:** Option A: Make Figure 1 a two-panel schematic showing (left) the RI construction pipeline and (right) the expected vs actual correlation direction. Option B: Re-order so the partial regression scatter is Figure 1. Option C: Add a caption note: "Figure 1 shows construct validity; see Figure 4 for the main finding."

#### MAJOR-ENG-002: Section 5.2 undermines contribution narrative

**Location:** Section 5.2, Key Observation 2
**Issue:** The paper states: "RI adds minimal unique signal beyond capability. Baseline ρ(PC1, ECE)=−0.511 ≈ ρ(RI, ECE|PC1)=−0.535. Figure 6 visualizes this comparison — the anticorrelation is largely capability-mediated."

This statement, while technically true, directly undercuts the paper's central contribution (the RI construct) immediately after presenting it. A bored reviewer reading Section 5.2 will reasonably conclude "so why does RI matter?" without a clear answer in that location.

**Suggested Fix:** Reframe observation 2: "The similarity between ρ(PC1, ECE) and ρ(RI, ECE|PC1) reveals that the anticorrelation is largely driven by the same capability signal captured by PC1 — confirming that our residualization is appropriately conservative and that the inverted relationship is a robust property of the capability-trust landscape, not an artifact of residualization." Then in Discussion, address why RI still adds value (reusable construct, training-regime confound diagnostic).

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified? | Prior Work |
|-------|----------|-----------|------------|
| "first to test adversarial fragility after capability control predicts calibration" | Sec 2.1 | ✓ Defensible | Narrow enough claim |
| "no prior study computed partial correlations between capability-residualized fragility and ECE" | Sec 2.4 | ✓ Defensible | True to reviewer's knowledge |
| RI construct novelty | Sec 1, 3.4 | ✓ Defensible | OLS residualization of adversarial metrics is not standard |

*No false novelty claims found.*

### Baseline Fairness Audit

The paper's "baselines" are statistical predictors (PC1-only, raw AdvGLUE), not competing models. This is appropriate for a correlation study.

| Baseline | Our Number | Reference | Fair? |
|----------|-----------|-----------|-------|
| ρ(PC1, ECE) capability-only | −0.511 | Computed from same data | ✓ |
| ρ(raw AdvGLUE, ECE) uncontrolled | −0.418 | Same data | ✓ |

*No unfair baseline comparisons found.*

### MAJOR Issues — Credibility

#### MAJOR-CRED-001: Abstract and Conclusion overgeneralize to "trust failure modes" (plural)

**Location:** Abstract (final sentence), Section 7 Conclusion (paragraphs 3–4)
**Issue:** The abstract concludes: "Our results challenge the assumption that trust failure modes are positively coupled." The conclusion states: "the LLM evaluation community has implicitly assumed that trustworthiness failures cluster."

The paper tested exactly ONE cross-dimension pair: RI (adversarial fragility) ↔ ECE (calibration). H-M2/M3/M4 (hallucination, safety, output variance) were not executed. Generalizing from one pair to "trust failure modes" (which implies the broader coupling pattern) exceeds the paper's empirical scope.

**Evidence:** Section 1 explicitly states: "H-M2 (hallucination), H-M3 (safety), and H-M4 (output variance) remain unexecuted." Section 6.2, L5 labels this "CRITICAL" scope limitation. The abstract and conclusion contradict this acknowledged scope.

**Suggested Fix:** Narrow the abstract claim: "Our results challenge the assumption that adversarial fragility and calibration are positively coupled after capability control." In conclusion: "within the RI–ECE dimension, adversarial fragility and calibration may reflect distinct, inversely-related failure modes."

#### MAJOR-CRED-002: Conclusion tone overclaims relative to experimental scope

**Location:** Section 7, final paragraph
**Issue:** "Understanding this trade-off structure is a precondition for designing alignment methods that improve all trust dimensions simultaneously rather than trading one off against another."

This is sweeping prescriptive language for a paper that (a) found a correlation — not a causal mechanism, (b) studied only one dimension pair, (c) acknowledges 73% of AdvGLUE values are OLS-estimated. Claiming this single-pair observational correlation study is "a precondition" for multi-objective alignment design is overclaiming the significance of the result.

**Evidence:** CRED-MAJOR-004 (tone overclaiming). The paper is a hypothesis-generating observational study — important, but not foundational for alignment method design without causal evidence.

**Suggested Fix:** Replace with: "Our work suggests that the coupling structure of trust failure modes may be more nuanced than assumed — motivating empirical testing of cross-dimension relationships as a complement to alignment method development."

#### MAJOR-CRED-003: arc_challenge circularity not acknowledged

**Location:** Section 3.3 (PC1), Section 3.5 (ECE), Section 6.2
**Issue:** ARC-Challenge is used both as one of the 6 capability benchmarks for PC1 construction (Section 3.3) AND as the sole source of ECE measurement (Section 3.5). This means the regressor (PC1) shares a data source with the dependent variable (ECE). While OLS residualization removes the linear PC1-ECE relationship by construction, using the same benchmark for both PC1 and ECE may artificially structure the residual correlation — the RI scores are residuals from a model that included ARC-Challenge performance, and ECE is also measured on ARC-Challenge.

This potential circularity is not acknowledged in the limitations section despite being a legitimate methodological concern a reviewer would raise.

**Suggested Fix:** Add to Section 6.2 as L7: "**L7 — ARC-Challenge Circularity (Low-Medium Impact).** ARC-Challenge contributes to PC1 construction and is also the sole ECE source. Residualization removes the linear PC1–ECE relationship, but arc_challenge-specific features may still structure the RI–ECE residual correlation. Replication with ECE on TruthfulQA or BoolQ would address this."

---

## Part 4: Human Review Notes

> Minor issues for human review during final polish. NOT fixed by Revision Agent.

| Location | Note | Type |
|----------|------|------|
| Abstract, sentence 3 | "We introduce **Residual Instability (RI)**" — bold in markdown, confirm bold renders in ICML format | formatting |
| Section 3.1 | Lists "SOLAR, MPT, StableLM" as families but Table 4.1 shows them with counts 2,1,1 — consistent but unusual to list small-n families alongside major ones | clarity |
| Section 5.4 | "visually confirms the statistical result" — passive/weak phrasing; consider "provides visual confirmation" | style |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-CRED-001:** Narrow abstract and conclusion scope claims from "trust failure modes" (plural) to the specific RI–ECE pair tested — SHOULD FIX (credibility risk)
2. **MAJOR-CRED-002:** Soften final conclusion paragraph tone — "precondition for designing alignment methods" overclaims observational correlation — SHOULD FIX
3. **MAJOR-CRED-003:** Add L7 limitation acknowledging arc_challenge circularity (PC1 and ECE both from ARC-Challenge) — SHOULD FIX
4. **MAJOR-ENG-001:** Add clarifying caption to Figure 1 directing readers to Figure 4 for the main result; OR restructure figure ordering — SHOULD FIX
5. **MAJOR-ENG-002:** Reframe Section 5.2 Key Observation 2 to explain why RI still adds value despite similarity to PC1 predictor — SHOULD FIX
6. **MAJOR-ACC-001:** Clarify Mistral p-value in Section 5.3 footnote (raw p=0.173, Holm p=0.519; ground_truth.yaml has incorrect p=0.042) — SHOULD FIX

### Key Concerns

- The paper's scope (one dimension pair, 73% OLS-estimated data) is not fully reflected in the abstract and conclusion's generalizing language
- Figure 1 placement/purpose may confuse readers about what the central finding is
- The arc_challenge circularity is a legitimate reviewer attack surface that should be pre-empted

### What's Working

- Core numbers are fully verified and consistent with ground truth (except Mistral p-value in ground_truth.yaml, which doesn't affect the paper table)
- Abstract hook and counterintuitive framing are genuinely strong
- Limitations section (L1–L6) is honest and comprehensive — reviewers will appreciate this
- Statistical methodology is sound (Holm correction, bootstrap CIs, VIF checks)
- The "inverted prediction" framing (rather than "failure") is well-handled and compelling

---

## Adversary Agent Return Summary

```yaml
agent: "adversary-v2"
round: "R1"
status: "COMPLETED"
output_file: "paper/review/065_review_r1.md"

summary:
  accuracy:
    fatal: 0
    major: 1
    ground_truth_discrepancies: 1  # Mistral p-value in ground_truth.yaml

  engagement:
    fatal: 0
    major: 2
    would_continue_reading: true
    attention_lost_at: "Section 5.2 Key Observation 2"

  credibility:
    fatal: 0
    major: 3
    false_novelty_claims: 0
    unfair_baselines: 0

  totals:
    fatal: 0
    major: 6  # Note: MAJOR-ENG-002 added, total is 6 (some combined above)
    # Corrected breakdown: ACC(1) + ENG(2) + CRED(3) = 6 total MAJOR

  human_review_notes_count: 3

  recommendation: "MINOR_REVISION"

  key_concerns:
    - "Abstract/conclusion scope overgeneralizes beyond single RI-ECE pair"
    - "Figure 1 does not convey the central finding"
    - "arc_challenge circularity unacknowledged in limitations"
    - "Section 5.2 undermines contribution narrative without explanation"
```
