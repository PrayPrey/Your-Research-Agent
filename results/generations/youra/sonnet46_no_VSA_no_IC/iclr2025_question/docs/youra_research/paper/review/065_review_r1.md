# Adversarial Review - Round 1

**Paper:** Hallucination Type Determines Optimal Token Log-Probability Aggregation: A Mechanism-Grounded Ablation
**Reviewed:** 2026-08-21T14:35:00+00:00
**Reviewer:** Adversary Agent v2 (Three-Persona)
**Round:** R1 — Accuracy, Engagement, Credibility

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 3 | NEEDS_WORK |
| Engagement | 0 | 0 | OK |
| Credibility | 0 | 2 | NEEDS_WORK |
| **TOTAL** | **0** | **5** | NEEDS_WORK |

**Recommendation:** MINOR_REVISION

---

## Part 1: Accuracy Check (Persona 1 — Accuracy Checker)

### Ground Truth Summary

| Metric | Paper Claims | Ground Truth (h-m3) | Match? |
|--------|--------------|---------------------|--------|
| LLaMA TriviaQA AUROC(min) | 0.849 | 0.8493 | ✓ (rounding) |
| LLaMA TriviaQA AUROC(mean) | 0.730 | 0.7299 | ✓ (rounding) |
| LLaMA TriviaQA AUROC(raw_sum) | 0.896 | 0.8964 | ✓ (rounding) |
| Mistral TriviaQA AUROC(min) | 0.892 | 0.8924 | ✓ (rounding) |
| Mistral TriviaQA AUROC(mean) | 0.836 | 0.8362 | ✓ (rounding) |
| Mistral TriviaQA AUROC(raw_sum) | 0.895 | 0.8946 | ✓ (rounding) |
| LLaMA TruthfulQA AUROC(min) | 0.638 | 0.6010 | ✗ MISMATCH (+0.037) |
| LLaMA TruthfulQA AUROC(mean) | 0.758 | 0.7207 | ✗ MISMATCH (+0.037) |
| LLaMA TruthfulQA AUROC(raw_sum) | 0.582 | 0.4589 | ✗ MISMATCH (+0.123) |
| Mistral TruthfulQA AUROC(min) | 0.564 | 0.5382 | ✗ MISMATCH (+0.026) |
| Mistral TruthfulQA AUROC(mean) | 0.675 | 0.6492 | ✗ MISMATCH (+0.026) |
| Mistral TruthfulQA AUROC(raw_sum) | 0.530 | 0.4173 | ✗ MISMATCH (+0.113) |
| LLaMA TriviaQA P1 ΔAUROC | 0.119 | 0.1194 | ✓ |
| Mistral TriviaQA P1 ΔAUROC | 0.056 | 0.0562 | ✓ |
| LLaMA TruthfulQA P2 ΔAUROC | 0.120 | 0.1198 | ✓ |
| Mistral TruthfulQA P2 ΔAUROC | 0.111 | 0.1109 | ✓ |
| Peakedness hallucinated | 2.936 | 2.9355 | ✓ |
| Peakedness correct | 2.533 | 2.5329 | ✓ |
| p-value (peakedness) | 0.002 | 0.00206 | ✓ |
| TruthfulQA dataset n | ~810–817 | 810 / 796 | ✓ |
| TriviaQA dataset n | ~488–500 | 488 / 476 | ✓ |
| LLaMA P2 CI | [+0.084, +0.157] | [+0.084, +0.157] | ✓ |
| Mistral P2 CI | [+0.071, +0.147] | [+0.071, +0.147] | ✓ |

### Findings

#### MAJOR-ACC-001: TruthfulQA AUROC Values Do Not Match Phase 4 Ground Truth

**Location:** Section 5.3 (Table 1), Abstract, Introduction
**Issue:** The paper reports TruthfulQA AUROC values that are systematically ~2.6–3.7 points higher than what Phase 4 (h-m3) actually computed. The P1/P2 ΔAUROC differentials are correct (since both min and mean are uniformly shifted), but the absolute AUROC numbers for TruthfulQA are wrong.

**Evidence (from h-m3/04_validation.md):**
- Paper: LLaMA TruthfulQA AUROC(min) = 0.638; Ground truth = 0.6010 → Δ = +0.037
- Paper: LLaMA TruthfulQA AUROC(mean) = 0.758; Ground truth = 0.7207 → Δ = +0.037
- Paper: LLaMA TruthfulQA AUROC(raw_sum) = 0.582; Ground truth = 0.4589 → Δ = +0.123
- Paper: Mistral TruthfulQA AUROC(min) = 0.564; Ground truth = 0.5382 → Δ = +0.026
- Paper: Mistral TruthfulQA AUROC(mean) = 0.675; Ground truth = 0.6492 → Δ = +0.026
- Paper: Mistral TruthfulQA AUROC(raw_sum) = 0.530; Ground truth = 0.4173 → Δ = +0.113

**Why not FATAL:** The ΔAUROC differentials (P1, P2) are all correct — meaning the directional claims, bootstrap CIs, and mechanism conclusions remain valid. The h-m3 gate evaluation confirms P2 is fully satisfied. The discrepancy is in absolute AUROC reporting, which does not change the paper's main scientific claims. However, it must be corrected as it would mislead readers about absolute performance levels.

**Note:** The uniform shift (+0.037 for LLaMA) suggests a possible sign convention difference or a different n_samples between runs. The raw_sum gap is larger (+0.123 LLaMA) suggesting the raw_sum result may use a different normalization in the paper vs. actual run.

**Required Fix:** Replace all TruthfulQA AUROC absolute values in Table 1 and all in-text mentions with the actual Phase 4 (h-m3) values.

---

#### MAJOR-ACC-002: LLaMA TruthfulQA raw_sum Discrepancy is Especially Large

**Location:** Section 5.3, Section 5.4, Discussion 6.3
**Issue:** Paper reports LLaMA TruthfulQA AUROC(raw_sum) = 0.582; actual h-m3 = 0.4589. This is a 0.123 gap — nearly 12 AUROC points. The paper describes raw_sum as "weakest (0.530–0.582)" on TruthfulQA; the actual values (0.417–0.459) are substantially lower and paint an even cleaner picture of raw_sum's TruthfulQA weakness.

**Evidence:** h-m3 rows for raw_sum on truthful_qa:
- LLaMA: 0.4589 (paper: 0.582)
- Mistral: 0.4173 (paper: 0.530)

**Suggested Fix:** Correct to 0.4589 / 0.4173 (or rounded 0.459 / 0.417). This strengthens the narrative (raw_sum is *even weaker* on TruthfulQA than claimed), so the fix improves rather than weakens the argument.

---

#### MAJOR-ACC-003: Dataset n Values — Minor Inconsistency

**Location:** Section 4 (Datasets table), Section 5.1
**Issue:** The paper reports n ≈ 488–500 for TriviaQA and n ≈ 810–817 for TruthfulQA. h-m3 shows LLaMA TriviaQA n=488, Mistral TriviaQA n=476. h-m1 shows n=488. The 476 Mistral figure is not mentioned anywhere in the paper. The paper's "488–500" range is misleading since Mistral uses 476 (below 488).

**Impact:** Minor but accurate reporting requires acknowledging the 476 sample count for Mistral TriviaQA.

**Suggested Fix:** Change "~488–500" to "~476–488" or add a footnote noting Mistral TriviaQA used 476 samples.

---

### Accuracy Checker Verdict

Peakedness, Spearman ρ, P1 ΔAUROC, P2 ΔAUROC, CIs — all match ground truth exactly (within rounding). The mechanism's core numerical evidence is solid. The only real problem is in absolute AUROC values for TruthfulQA, which must be corrected.

---

## Part 2: Engagement Check (Persona 2 — Bored Reviewer)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✓ | Opens with a concrete result: "costs up to 12 AUROC points." Problem and contribution clear. |
| Problem clear in 1 min? | ✓ | "It matters by 12 AUROC points." — crisp hook sentence. |
| Novelty clear in 2 min? | ✓ | Four numbered contributions in Introduction, each specific. |
| Figure 1 self-explanatory? | ? | No Figure 1 caption/image in paper text; referenced as `figures/peakedness_kde_llama2_trivia_qa.png`. Cannot evaluate directly from text. |
| Would continue reading? | ✓ | Yes — strong hook, concrete numbers, clear structure. |

**Attention Lost At:** Never lost during text reading. The methodology (Section 3) is well-structured.

### FATAL Issues — Engagement

None.

### MAJOR Issues — Engagement

None. The paper passes the bored reviewer test with flying colors. The "12 AUROC points" hook is memorable and the mechanism narrative flows clearly.

### Human Review Notes (Engagement)

| Location | Note | Type |
|----------|------|------|
| Abstract, line 3 | "the aggregation step that converts a per-token sequence into a single confidence score has never been studied systematically" — slightly long sentence, could be tightened | style |
| Introduction | The four-contribution list is well-structured but Contribution 4 ("Unexpected positive finding") is a weak label — "Unexpected Finding" more accurately conveys the surprise | style |

---

## Part 3: Credibility Check (Persona 3 — Skeptical Expert)

### Novelty Claims Audit

| Claim | Location | Verified? | Notes |
|-------|----------|-----------|-------|
| "has never been studied systematically" | Abstract | PLAUSIBLE | Liu 2025 survey identifies this as open gap; claim is supported. |
| "first mechanism-grounded aggregation selection criterion" | Abstract | PLAUSIBLE | Reasonable claim; no prior paper found with same framing. |
| "first controlled ablation isolating aggregation function" | Section 3.1, Contribution 1 | PLAUSIBLE | Liu 2025 cited as identifying this gap. Supported. |
| "providing the first mechanistic classification that predicts optimal aggregation from hallucination type alone" | Section 2 | PLAUSIBLE | Reasonable. |

### Baseline Fairness Audit

| Baseline | Our Number | Literature | Fair? |
|----------|------------|------------|-------|
| Semantic Entropy AUROC(TriviaQA) | ~0.79 (Farquhar 2023) | ~0.79 | ✓ fair — citing published value |
| Mean log-prob (CCP) | 0.72–0.80 (Fadeeva 2024) | 0.72–0.80 | ✓ fair — citing published range |
| SelfCheckGPT | 0.72–0.78 (Manakul 2023) | 0.72–0.78 | ✓ fair — citing published range |

Cross-pipeline comparison is acknowledged in Section 6.3. No unfair baseline comparisons found.

### MAJOR Issues — Credibility

#### MAJOR-CRED-001: Three Unverified Citations

**Location:** Section 2 (Related Work), References
**Issue:** Citations Ma2025Semantic, Moslonka2025Learned, and Zhang2025Robust are explicitly flagged as unverified in the ground truth file (citations.unverified_keys). The paper uses these citations to establish the "supervised methods" context in Related Work. Unverified citations are a credibility risk: if the cited arXiv IDs don't exist or are mislabeled, it reflects poorly on the paper.

**Evidence:** 065_ground_truth.yaml: `unverified: 3`, `unverified_keys: ["Ma2025Semantic", "Moslonka2025Learned", "Zhang2025Robust"]`

**Impact:** The Related Work section uses these papers to establish the supervised/probe-based methods category. If any is wrong, the positioning is affected.

**Suggested Fix:** Verify all three citations via Semantic Scholar before submission. If unverifiable, remove or replace with verified alternatives.

---

#### MAJOR-CRED-002: Overclaiming Tone — "filling an open gap"

**Location:** Abstract (last sentence), Introduction Contribution 1
**Issue:** The phrase "filling an open gap identified in recent uncertainty quantification surveys" in the abstract is accurate in substance but presents as a gap-filling claim. The paper DOES fill this gap, so this is not an overclaim per se. However, a skeptical reviewer may notice the Liu 2025 survey itself hasn't been published in a major venue (cited as KDD 2025 proceedings). If Liu 2025 is itself unverified, the "gap identification" foundation is weakened.

**Evidence:** Liu 2025 is listed as "verified" in citations (10 verified out of 13). No concern here — citation appears valid.

**Revised Assessment:** This is NOT an overclaim. Withdrawn — no issue.

---

#### MAJOR-CRED-003: "Raw_sum exceeds published Semantic Entropy" — Cross-Pipeline Comparison

**Location:** Abstract, Introduction paragraph 4, Section 5.4, Section 6.3
**Issue:** The paper states raw_sum (0.895–0.896) "exceeds published Semantic Entropy AUROC (≈0.79)" and calls this a "critical practical contrast." Section 6.3 appropriately adds "cross-pipeline comparisons should be interpreted with appropriate caution." However, the abstract and introduction state this more boldly without the caveat, and the abstract calls it a "critical practical contrast."

**Impact:** A skeptical reviewer will ask: different hardware, different tokenization, different dataset splits, different evaluation protocol — how much of the gap is methodology vs. aggregation choice? The cross-pipeline caveat is buried in Discussion.

**Suggested Fix:** Add a brief caveat qualifier in abstract or introduction (one clause): "under our evaluation protocol." Do NOT remove the finding — it is the paper's strongest practical claim.

---

### Skeptical Expert: Missing Limitations Check

**Limitations explicitly stated (Section 6.4):**
- [x] NQ data gap
- [x] 7B model scale only
- [x] Greedy decoding only
- [x] Multi-sample baselines not in same pipeline

**Missing limitations:**
- [ ] **TruthfulQA label protocol dependency.** The paper uses ROUGE-L ≥ 0.3 for TruthfulQA labels (Fadeeva 2024 protocol). TruthfulQA is typically evaluated with a judge model (GPT-4) or MC questions; ROUGE-L may produce different label distributions. This affects P2's generalizability.
- [ ] **Peakedness metric is custom.** `peakedness(x) = kurtosis(x) + max(x)/mean(x)` is not a standard metric. No ablation of whether alternative peakedness measures show the same effect.

These are informational gaps but worth flagging. Not FATAL — the paper's claims hold with current evaluation.

**Suggested Fix:** Add one sentence in Section 6.4 noting TruthfulQA label protocol dependency.

---

## Part 4: Human Review Notes

| Location | Note | Type |
|----------|------|------|
| Abstract, sentence 2 | "yet the aggregation step that converts a per-token sequence into a single confidence score has never been studied systematically" — "per-token sequence" is slightly ambiguous (sequence of per-token values, or per-token log-probability sequence?). Suggest: "per-token log-probability sequence" | clarity |
| Introduction para 1 | "a long tradition of work" — could cite specific count for conciseness | style |
| Section 3.4 | "Custom implementation (22/22 unit tests passing) used in place of lm-polygraph due to hardware compatibility constraints" — "due to hardware compatibility constraints" reads oddly; consider "due to hardware/dependency compatibility" or just omit | clarity |
| Section 4 | Table header "N" not defined in caption — add "(samples per model)" | formatting |
| Section 5.3 | "Figure 7 (figures/fig4_summary_table.png) summarizes P1/P2/P3 gate results" — Figure 7 is described as a table image, consider whether this should be an actual LaTeX table | formatting |
| References | Farquhar 2023 cited as "Nature, 2024" in reference list but cited in-text as "[Farquhar et al., 2023]" — year inconsistency | typo |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-ACC-001:** Replace all TruthfulQA AUROC absolute values in Table 1 and in-text citations with actual h-m3 values (LLaMA: min=0.601, mean=0.721, raw_sum=0.459; Mistral: min=0.538, mean=0.649, raw_sum=0.417) — MUST FIX
2. **MAJOR-ACC-002:** Ensure raw_sum TruthfulQA values are corrected consistently — the larger gap (0.459, 0.417 vs. 0.582, 0.530) actually strengthens the paper's narrative — MUST FIX
3. **MAJOR-ACC-003:** Update TriviaQA n range to "~476–488" to reflect Mistral's actual 476-sample count — SHOULD FIX
4. **MAJOR-CRED-001:** Note the 3 unverified citations in a footnote or verify before submission — SHOULD FIX
5. **MAJOR-CRED-003:** Add "under our evaluation protocol" caveat in abstract/introduction for the SE comparison — SHOULD FIX
6. **Human Review:** Farquhar reference year inconsistency (2023 in-text vs. 2024 in reference list) — SHOULD FIX

### Key Concerns

- Absolute TruthfulQA AUROCs are inflated ~2.6–12 points vs. actual h-m3 results. All ΔAUROC differentials are correct, so the mechanism claims are valid, but the table must be corrected.
- Three citations unverified — check before submission.

### What's Working

- Mechanism narrative is clear and well-structured (three layers of evidence)
- Hook ("12 AUROC points") is strong and memorable
- P1/P2 ΔAUROC values and CIs match ground truth exactly
- Peakedness statistics are accurate
- Limitations section is unusually thorough for a conference paper
- Cross-pipeline caveat for SE comparison is appropriately included (just needs reinforcement earlier)
- Engagement quality is high — passes the bored reviewer test

---

## Adversary Agent Return Summary

```yaml
agent: "adversary-v2"
round: "R1"
status: "COMPLETED"
output_file: "docs/youra_research/paper/review/065_review_r1.md"

summary:
  accuracy:
    fatal: 0
    major: 3
    ground_truth_discrepancies: 12  # All TruthfulQA AUROC values

  engagement:
    fatal: 0
    major: 0
    would_continue_reading: true
    attention_lost_at: null

  credibility:
    fatal: 0
    major: 2
    false_novelty_claims: 0
    unfair_baselines: 0

  totals:
    fatal: 0
    major: 5

  human_review_notes_count: 6

  recommendation: "MINOR_REVISION"

  key_concerns:
    - "TruthfulQA AUROC absolute values inflated vs. Phase 4 ground truth (all ΔAUROC correct)"
    - "Three unverified citations need verification or removal"
    - "SE cross-pipeline caveat needs reinforcement in abstract/introduction"
```
