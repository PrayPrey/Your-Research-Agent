# Adversarial Review Round 1
# Three-Persona Review: Accuracy Checker, Bored Reviewer, Skeptical Expert

**Date:** 2026-03-24
**Round:** R1 (Accuracy and Engagement)
**Paper:** Geometric Distortion of Confidence Signals in RLHF-Tuned Language Models
**Status:** COMPLETE

---

## Executive Summary

| Category | Count | Details |
|----------|-------|---------|
| **FATAL** | 0 | None identified |
| **MAJOR** | 2 | See below |
| **MINOR** | 6 | Collected for human review |
| **Persuasiveness** | PASS | Would continue reading |

**Recommendation:** MINOR_REVISION - Paper is strong; issues identified are addressable.

---

## PERSONA 1: Accuracy Checker

### Ground Truth Verification

| Claim in Paper | Ground Truth | Source | Status |
|----------------|--------------|--------|--------|
| Qwen Base AUROC: 0.8298 | 0.8298 | h-e1/04_validation.md | ✅ MATCH |
| Qwen Instruct AUROC: 0.8076 | 0.8076 | h-e1/04_validation.md | ✅ MATCH |
| Mistral Base AUROC: 0.7797 | 0.7797 | h-e1/04_validation.md | ✅ MATCH |
| Mistral Instruct AUROC: 0.7413 | 0.7413 | h-e1/04_validation.md | ✅ MATCH |
| Mean AUROC degradation: +0.0303 | +0.0303 | Calculated | ✅ MATCH |
| Qwen Inflation Ratio: 3.06x | 3.06x | h-m1/04_validation.md | ✅ MATCH |
| Mistral Inflation Ratio: 16.79x | 16.79x | h-m1/04_validation.md | ✅ MATCH |
| Qwen β_base: 2.222 | 2.2222 | h-m2/04_validation.md | ✅ MATCH (rounding) |
| Qwen β_instruct: 1.466 | 1.4661 | h-m2/04_validation.md | ✅ MATCH (rounding) |
| Mistral β_base: 1.558 | 1.5579 | h-m2/04_validation.md | ✅ MATCH (rounding) |
| Mistral β_instruct: 0.931 | 0.9305 | h-m2/04_validation.md | ✅ MATCH (rounding) |
| Qwen Refinement Base: 0.0559 | 0.0559 | h-m3/04_validation.md | ✅ MATCH |
| Qwen Refinement Instruct: 0.0343 | 0.0343 | h-m3/04_validation.md | ✅ MATCH |
| Mistral Refinement Base: 0.0580 | 0.0580 | h-m3/04_validation.md | ✅ MATCH |
| Mistral Refinement Instruct: 0.0093 | 0.0093 | h-m3/04_validation.md | ✅ MATCH |

### Numerical Accuracy Issues

**NONE FOUND** - All numerical claims in the paper match the ground truth values from Phase 4 validation reports.

### Methodology Consistency Check

| Paper Description | Ground Truth | Status |
|-------------------|--------------|--------|
| "logit margin as confidence proxy" | ✅ Implemented | MATCH |
| "bootstrap CIs (n=1000)" | ✅ Implemented | MATCH |
| "permutation tests (n=10,000)" | ✅ Implemented | MATCH |
| "greedy decoding (T=0)" | ✅ Implemented | MATCH |
| "MMLU 14,042 test samples" | ✅ 14,042 | MATCH |

**Accuracy Checker Verdict:** ✅ PASS - All numerical claims verified against ground truth.

---

## PERSONA 2: Bored Reviewer

*"I'm a busy NeurIPS reviewer with 5 papers to review today. Would I continue reading?"*

### First Impression Checks

| Check | Question | Result | Notes |
|-------|----------|--------|-------|
| `abstract_compelling` | Would I continue reading after the abstract? | **YES** | Strong hook about unreliable confidence, specific numbers (2-4pp, 3-17x, 30-40%), clear implication |
| `problem_clear_in_1_minute` | Can I understand the problem in 1 minute? | **YES** | First paragraph of Introduction is clear: RLHF corrupts confidence-correctness relationship |
| `novelty_clear_in_2_minutes` | Do I understand what's new in 2 minutes? | **YES** | "Geometric vs scalar distortion" framing is novel and memorable |
| `figure_1_self_explanatory` | Can I understand Figure 1 without reading text? | **N/A** | Paper mentions figures but Figure 1 not shown in main paper.md |
| `would_continue_reading` | Would I continue reading this paper? | **YES** | The "bent ruler" analogy is effective; the 4-hypothesis structure is systematic |
| `attention_lost_at` | At what point did I lose attention? | **NEVER** | Paper maintains momentum throughout |

### Engagement Issues

**NONE FOUND** - Paper is well-structured and maintains reader interest.

### Persuasiveness Assessment

**STRENGTHS:**
1. Clear "bent ruler" metaphor makes abstract concept concrete
2. Four-hypothesis triangulation is methodologically satisfying
3. Cross-family validation strengthens causal claims
4. Practical implications stated clearly

**Bored Reviewer Verdict:** ✅ PASS - Paper is engaging; would continue reading.

---

## PERSONA 3: Skeptical Expert

*"Domain expert looking for holes in claims. Would I accept or reject?"*

### Novelty Claims Review

| Claim | Assessment | Issue? |
|-------|------------|--------|
| "First to characterize geometric vs scalar distortion" | **PLAUSIBLE** | Prior work (Tian 2023) documented overconfidence but not distortion type | No |
| "Novel AUROC-based discriminative degradation metric" | **ACCEPTABLE** | AUROC is standard; application to RLHF comparison is new | No |
| "Percentile-normalized monotonicity" | **NOVEL** | This specific analysis approach appears new | No |

### Baseline Fairness Review

| Comparison | Fair? | Notes |
|------------|-------|-------|
| Base vs Instruct within family | **YES** | Same architecture, same prompts, same questions |
| Qwen vs Mistral | **YES** | Two independent families; not cherry-picked |
| Against prior work (ECE-based) | **YES** | Paper acknowledges ECE improvements, argues AUROC is complementary |

### Overclaim Analysis

| Claim | Overclaim? | Severity |
|-------|------------|----------|
| "Temperature scaling cannot repair geometric distortion" | **POTENTIAL** | MAJOR |
| Abstract: "AUROC drops 2-4 percentage points" | NO | Accurate for tested models |
| "RLHF creates discrimination-capability tradeoff" | NO | Appropriately hedged ("suggests") |

**MAJOR-001: Temperature Scaling Overclaim**
- **Location:** Abstract, Introduction (lines 2-3), Discussion
- **Issue:** Paper claims "temperature scaling cannot repair" geometric distortion, but does not empirically test temperature scaling on the RLHF models to verify this
- **Evidence needed:** Actually apply temperature scaling and show AUROC/refinement remain degraded
- **Current status:** Theoretical argument only (scalar vs geometric distinction)
- **Recommendation:** Either run the experiment OR soften claim to "temperature scaling targets calibration, not discrimination"

### Missing Limitations Review

| Potential Limitation | Acknowledged? | Severity |
|----------------------|---------------|----------|
| Llama family not tested | **YES** | Acknowledged in Discussion L1 |
| 7B scale only | **YES** | Acknowledged in Discussion L2 |
| MMLU specific | **YES** | Acknowledged in Discussion L3 |
| Temperature scaling not tested | **NO** | **MAJOR** |
| DPO vs PPO not compared | **PARTIAL** | Mentioned as future work |

**MAJOR-002: Missing Temperature Scaling Experiment**
- **Location:** Methodology, Results
- **Issue:** Paper argues temperature scaling is insufficient but never actually tests it
- **Risk:** Reviewer could ask "Did you actually try temperature scaling? What happens to AUROC/refinement after scaling?"
- **Recommendation:** Add experiment showing post-temperature-scaling AUROC OR explicitly acknowledge this as a limitation

### False Novelty Claims

**NONE FOUND** - Novelty claims are appropriately scoped.

### Unfair Baseline Comparisons

**NONE FOUND** - Comparisons are within-family and fair.

### Skeptical Expert Verdict:** WEAK ACCEPT with MAJOR revisions needed

---

## ISSUE CATALOG

### FATAL Issues (0)

None identified.

### MAJOR Issues (2)

| ID | Issue | Location | Persona | Fix Required |
|----|-------|----------|---------|--------------|
| MAJOR-001 | Temperature scaling claim not empirically verified | Abstract, Intro, Discussion | Skeptical Expert | Either test temperature scaling OR soften claim |
| MAJOR-002 | Missing temperature scaling experiment | Methodology, Results | Skeptical Expert | Add experiment OR acknowledge as limitation |

**Note:** MAJOR-001 and MAJOR-002 are related - fixing one likely addresses both.

### MINOR Issues (6) - Collected for Human Review

| ID | Type | Location | Note |
|----|------|----------|------|
| MINOR-001 | clarity | Abstract | "probability landscape" is abstract - consider concrete example |
| MINOR-002 | formatting | Results Table 5 | "**" for p-values not standard; use actual p-values or stars convention |
| MINOR-003 | style | Introduction | "bent ruler" metaphor appears late; could appear earlier for impact |
| MINOR-004 | clarity | Methodology H-M3 | "calibrated softmax" procedure not fully explained |
| MINOR-005 | formatting | Results | Table column alignment inconsistent between tables |
| MINOR-006 | typo | Discussion | "discriminative degradation" vs "discriminative degradation" - check consistency |

---

## Persuasiveness Checks Summary

| Check | R1 Result |
|-------|-----------|
| abstract_compelling | TRUE |
| problem_clear_in_1_minute | TRUE |
| novelty_clear_in_2_minutes | TRUE |
| figure_1_self_explanatory | N/A |
| would_continue_reading | TRUE |
| attention_lost_at | NULL (never) |
| false_novelty_claims_found | 0 |
| unfair_baseline_comparisons | 0 |
| overclaims_found | 1 (temperature scaling) |
| missing_limitations | TRUE (temp scaling experiment) |

**Overall Persuasiveness:** PASS (with temperature scaling caveat)

---

## Recommendations for Revision Agent

### Priority 1 (MAJOR - Must Fix)

1. **Temperature Scaling Evidence** (MAJOR-001, MAJOR-002)
   - Option A: Add experiment - Apply temperature scaling to instruct models, show AUROC/refinement remain degraded
   - Option B: Soften claim - Change "cannot repair" to "targets calibration metrics (ECE) rather than discrimination metrics (AUROC)"
   - Option C: Add explicit limitation - "We do not empirically test temperature scaling; our argument is theoretical based on the scalar vs geometric distinction"

### Priority 2 (MINOR - Human Review)

Collected in human_review_notes_file for post-review editing.

---

## Ground Truth Verification Log

```yaml
verification_performed_at: "2026-03-24T21:30:00Z"
files_checked:
  - h-e1/04_validation.md
  - h-m1/04_validation.md
  - h-m2/04_validation.md
  - h-m3/04_validation.md
  - paper/065_ground_truth.yaml

total_claims_verified: 16
matches: 16
mismatches: 0
accuracy: 100%
```

---

*Generated by Phase 6.5 Adversarial Review - Round 1*
*Three-Persona Review Protocol v2.0*
