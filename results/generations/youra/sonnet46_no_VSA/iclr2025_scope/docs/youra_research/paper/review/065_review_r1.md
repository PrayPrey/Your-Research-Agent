# Adversarial Review — Round 1
# Phase 6.5 — Accuracy and Engagement Review
# Date: 2026-08-03
# Round: R1
# Personas: accuracy_checker, bored_reviewer, skeptical_expert

---

## Ground Truth Summary

| Metric | Ground Truth Value | Paper Claims |
|--------|-------------------|--------------|
| β (log-log slope) | -0.368 | -0.368 ✓ |
| 90th pct at N=2048 | 0.027 | 0.027 ✓ |
| N=512: n, mean, std, 90th | 1600, 0.0392, 0.0071, 0.0478 | 1,600, 0.0392, 0.0071, 0.0478 ✓ |
| N=1024: n, mean, std, 90th | 160, 0.0331, 0.0057, 0.0383 | 160, 0.0331, 0.0057, 0.0383 ✓ |
| N=2048: n, mean, std, 90th | 160, 0.0235, 0.0043, 0.0273 | 160, 0.0235, 0.0043, 0.0273 ✓ |
| Total measurements | 1600+160+160 = **1,920** | "1,760" ✗ |
| H-E1 behavioral gate | PENDING (experiment running) | PoC-level, correctly flagged ✓ |
| H-M2 proxy | ratio=1.0 by construction | "proxy data" correctly flagged ✓ |
| Optimization steps | 500 (vs MOHAWK 10k) | NOT mentioned in paper limitations ✗ |

---

## Executive Summary

| Category | Count |
|----------|-------|
| FATAL | 1 |
| MAJOR | 3 |
| MINOR | 3 |
| Persuasiveness: abstract compelling | PASS |
| Persuasiveness: problem clear in 1 min | PASS |
| Persuasiveness: novelty clear in 2 min | PASS |
| Persuasiveness: would continue reading | YES |

**Recommendation:** REVISE — fix FATAL and MAJORs before submission.

---

## FATAL Issues

### FATAL-001: Measurement Count Arithmetic Error

**Persona:** Accuracy Checker  
**Location:** Abstract (para 4), Introduction (para 4 "1,760 attention matrix measurements"), Conclusion ("1,760 measurements")  
**Severity:** FATAL — factual error that any reviewer checking the table will catch immediately

**Issue:** The paper claims "1,760 attention matrix measurements spanning all 32 LLaMA-3-8B transformer layers" in multiple places (Abstract, Introduction, Conclusion). However:
- N=512: 50 samples × 32 layers = **1,600**
- N=1024: 5 samples × 32 layers = **160**
- N=2048: 5 samples × 32 layers = **160**
- **Total: 1,920 measurements**

Table 5.1 column `n` shows 1,600 / 160 / 160 — this is correct. The text "1,760" is arithmetically inconsistent with the table and with the actual experimental design (50+5+5=60 samples × 32 layers = 1,920).

Note: 1,760 = 55 × 32, which has no correspondence to the experimental setup.

**Required Fix:** Replace "1,760" with "1,920" everywhere it appears. Alternatively, if "1,760" was intended to refer only to N=512 measurements plus something else, clarify. The table is correct; the text is wrong.

**Evidence from ground truth:** `per_length_statistics.N_512.n_measurements: 1600`, `N_1024: n_measurements: 160`, `N_2048: n_measurements: 160` → total 1,920.

---

## MAJOR Issues

### MAJOR-001: "Conclusive" Overclaim for Mechanism Gate

**Persona:** Skeptical Expert  
**Location:** Introduction, para 4: "**The mechanism gate result is conclusive.**"  
**Severity:** MAJOR — attacks the paper's credibility with domain experts

**Issue:** Calling the gate result "conclusive" implies it resolves the retrieval degradation mechanism entirely. It does not. The gate shows approximation quality is NOT the bottleneck — this part is conclusive. But the paper then implies bounded-state architecture IS the cause ("attributing it instead to..."). The attribution is the inference, not the measurement. H-E1 behavioral data is pending.

A reviewer will correctly note: "You showed approximation is not the cause. You did not behaviorally confirm bounded-state architecture IS the cause."

**Required Fix:** Change "The mechanism gate result is conclusive." to "The mechanism gate result is unambiguous." or "The mechanism gate result is clear and well-margined." Keep "conclusive" only if referring strictly to what was measured (approximation quality), not the causal chain.

---

### MAJOR-002: Causal Attribution Too Strong in Abstract

**Persona:** Skeptical Expert  
**Location:** Abstract: "This rules out approximation failure as the mechanism for retrieval degradation, **attributing it instead to** the SSM state update's exponential forgetting."  
**Severity:** MAJOR — this is the primary overclaim that will draw reviewer fire

**Issue:** "Attributing it instead to bounded-state forgetting" asserts a specific alternative cause without behavioral confirmation. The gate eliminates one hypothesis. That eliminates approximation as the cause. But the remaining cause could be: (a) bounded-state forgetting, (b) curriculum effects, (c) architectural mismatch not captured by the Frobenius gate, or (d) other factors. H-E1 would confirm (a); it's pending.

**Required Fix:** Soften to: "narrowing the causal attribution toward the SSM state update's exponential forgetting of early token positions" or "establishing that architectural bounded-state effects, rather than distillation quality, are the primary candidate mechanism for retrieval degradation."

---

### MAJOR-003: Optimization Budget Limitation Missing from Paper

**Persona:** Skeptical Expert / Accuracy Checker  
**Location:** Section 6.3 (Limitations)  
**Severity:** MAJOR — a reviewers will ask "why only 500 steps?" and find no answer in the paper

**Issue:** The H-M1 experiment uses 500 Adam optimization steps per SSD fit, whereas the MOHAWK paper uses 10,000 steps. The ground truth notes this explicitly: "500 vs 10,000 steps... factor ~2.5 difference expected." The paper acknowledges the normalization alignment with MOHAWK Table 6 scale but does not acknowledge the reduced optimization budget or its potential effect on the β=-0.368 estimate.

A skeptical reviewer will ask: "Would β improve (become more negative) or degrade (become positive) with 10,000 steps? If SSD fits are not fully converged, your gate result is lower-bounded — the actual approximation quality could be even better. But you should say so."

The fact that the gate passes with large margin (β=-0.368 vs threshold 0.5) makes this a forgiving issue, but it needs acknowledgment.

**Required Fix:** Add one sentence to Section 6.3 Limitations: "The SSD fitting used 500 Adam steps per layer (vs MOHAWK's 10,000 steps); the gate passes with large margin (β=-0.368 vs threshold 0.5), suggesting the result is robust to optimization budget, but fully-converged fits at 10,000 steps would strengthen the claim."

---

## MINOR Issues (Collected for Human Review)

### MINOR-001: Internal Note in Paper Frontmatter

**Location:** Paper frontmatter `note:` field  
**Issue:** "Word count exceeds ICML 8-page target (~2800 words for main text). Sections 2-4 should be condensed..." — this is an internal pipeline note, not suitable for a submission frontmatter.  
**Fix:** Remove before submission. (Not in paper body; in YAML frontmatter — human reviewer should clean this.)

### MINOR-002: Raw vs Normalized Frobenius Distinction

**Location:** Section 3.2, Section 5.1  
**Issue:** The raw Frobenius norm grows super-linearly with N (slope ≈0.63 per ground truth). A reader who confuses raw with normalized would think "error grows, not shrinks." The paper explains normalization in Section 3.2 but doesn't mention that raw values grow. A one-sentence note ("The raw norm grows with N as expected; normalization reveals the per-position error trend") would preempt reviewer confusion.  
**Fix:** Optional clarification in Section 5.1 footnote or text.

### MINOR-003: Hybrid Architecture Name-Dropping (Section 2.3)

**Location:** Section 2.3 "Falcon-H1 [Zuo et al., 2025] and Apriel-H1 [Ostapenko et al., 2025]..."  
**Issue:** These papers are mentioned to motivate the Hybrid-4 control condition, but neither is actually evaluated in the paper's experiments. The reference feels like context-padding. Consider collapsing to one sentence or removing Apriel-H1.  
**Fix:** Trim Section 2.3 to one sentence; remove Apriel-H1 or combine into same citation cluster.

---

## Ground Truth Verification Log

| Check ID | Claim | Verified Against | Result |
|----------|-------|-----------------|--------|
| AC1 | H-E1 behavioral gate NOT numerically claimed | 065_ground_truth.yaml, h-e1/04_validation.md | ✓ PASS |
| AC2 | H-M2 proxy correctly labeled | 065_ground_truth.yaml depth_slope_h_m2 | ✓ PASS |
| AC3 | β=-0.368 sign correct (decreasing error) | ground_truth.metrics.ssd_frobenius_gate | ✓ PASS |
| AC4 | Normalization explained | Section 3.2, ground_truth.methodology | ✓ PASS |
| AC5 | MOHAWK citation flagged [UNVERIFIED] | ground_truth adversary_priority_checks AC5 | ✓ PASS |
| AC6 | N≤2048 limitation acknowledged | Section 6.3 | ✓ PASS |
| AC7 | Attention sparsity interpretation hedged | "we attribute" language | ✓ PASS |
| ARITHMETIC | Total measurements 1920 not 1760 | Per-length table n=1600+160+160 | ✗ FAIL → FATAL-001 |
| OPT-BUDGET | 500 vs 10k steps acknowledged | Section 6.3 | ✗ MISSING → MAJOR-003 |

---

## Persuasiveness Assessment (Bored Reviewer)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Puzzle hook + concrete β=-0.368 + honest pending |
| Problem clear in 1 minute? | PASS | Confound (approximation vs bounded-state) clear by intro para 3 |
| Novelty clear in 2 minutes? | PASS | Mechanism gate concept and result clear by end of intro |
| Figure 1 self-explanatory? | CONDITIONAL PASS | Description is clear; no actual rendered figure |
| Would continue reading? | YES | |
| Attention lost at? | Never (minor dip in Section 2.3) | |
| False novelty claims? | 0 | |
| Unfair baseline comparisons? | 0 | No behavioral baselines claimed yet |
| Overclaims found? | 2 | "conclusive" (MAJOR-001) + causal attribution (MAJOR-002) |
| Tone overclaiming? | 1 | "conclusive" tone inflates causal claim beyond evidence |
| Missing limitations? | 1 | 500-step optimization budget (MAJOR-003) |

---

## Summary for Revision Agent

**Priority 1 — FATAL (must fix):**
1. Change "1,760" → "1,920" in Abstract, Introduction para 4, and Conclusion

**Priority 2 — MAJOR (must fix):**
2. Change "The mechanism gate result is conclusive." → "The mechanism gate result is unambiguous." (Introduction, para 4 header)
3. Soften Abstract causal attribution: "attributing it instead to" → "narrowing the causal attribution toward"
4. Add optimization budget limitation sentence to Section 6.3

**Priority 3 — MINOR (collect for human review):**
- Remove internal note from paper frontmatter before submission
- Optional raw-vs-normalized clarification sentence in Section 5.1
- Trim Section 2.3 Hybrid Architectures paragraph
