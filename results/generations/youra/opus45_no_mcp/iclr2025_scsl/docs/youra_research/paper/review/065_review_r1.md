# Adversarial Review Round 1
**Paper**: When Do Shortcuts Crystallize?  
**Date**: 2026-08-19  
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Executive Summary

| Category | FATAL | MAJOR | MINOR |
|----------|-------|-------|-------|
| Accuracy | 0 | 1 | 0 |
| Engagement | 0 | 0 | 2 |
| Credibility | 0 | 1 | 1 |
| **TOTAL** | **0** | **2** | **3** |

**Recommendation**: REVISE - Address MAJOR issues before submission.

---

## Part 1: Accuracy Check (Accuracy Checker)

### Ground Truth Verification Table

| Claim ID | Paper States | Ground Truth | Status |
|----------|--------------|--------------|--------|
| Q1 | 100% detection rate | 1.0 | MATCH |
| Q2 | SNR 5.64 | 5.64 | MATCH |
| Q3 | 4.22% timing variance | 0.0422 | MATCH |
| Q4 | 15-40% timing range | 0.15-0.40 | MATCH |
| Q5 | 94.7% spurious probe | 0.9468 | MATCH (rounded) |
| Q6 | 93.9% core probe | 0.939 | MATCH |
| Q7 | Waterbirds 28.7% | 0.287 | MATCH |
| Q8 | CelebA 23.2% | 0.232 | MATCH |
| Q9 | ColoredMNIST 18.3% | 0.183 | MATCH |
| Q10 | 5-epoch smoothing | 5 | MATCH |

### Logical Consistency Issues

**MAJOR-ACC-1**: SNR Inconsistency in Table 5.1

- Paper Section 5.1 table shows SNR for Waterbirds as 5.64, CelebA as 4.21, ColoredMNIST as 6.12, Overall as 5.32
- Ground truth Q2 states "Signal-to-noise ratio 5.64" linked to H-M3
- Abstract claims "signal-to-noise ratio of 5.64"
- Which is correct? 5.64 (Waterbirds only) or 5.32 (overall)?
- **Severity**: MAJOR - numerical claim used as headline metric is ambiguous

---

## Part 2: Engagement Check (Bored Reviewer)

### Engagement Verdict Table

| Question | Verdict | Notes |
|----------|---------|-------|
| Continue after abstract? | YES | Clear problem, concrete numbers |
| Problem clear in 1 min? | YES | Intro hooks well |
| Novelty clear in 2 min? | YES | "When" vs "what/why" distinction clear |
| Where attention waned | Section 3.4-3.6 | Methods get dry, need figures |

### Detailed Assessment

**Hook effectiveness**: Strong. "When does...become irreversible?" is provocative.

**Contribution clarity**: Good. Three contributions are stated as narrative, not bullet points.

**Attention loss points**:
- MINOR-ENG-1: Methodology section (3.4-3.6) lists method details without visual aid - reader cannot picture the detection pipeline
- MINOR-ENG-2: Results tables are dense; would benefit from figure references inline

---

## Part 3: Credibility Check (Skeptical Expert)

### Novelty Claims Audit

| Claim | Location | Valid? | Concern |
|-------|----------|--------|---------|
| "first temporal characterization" | Intro, Contribution 1 | PLAUSIBLE | Need to verify no prior phase analysis exists |
| "100% detection rate" | Throughout | VALID | But only 5 seeds - low statistical power |

### Baseline Fairness Audit

**MAJOR-CRED-1**: No Comparison Baselines

- Paper proposes d2WGA/dt2 detection method
- No comparison to alternative detection approaches (e.g., loss curvature, gradient norm tracking, representation similarity)
- Reader cannot assess if this method is superior or just one option
- **Severity**: MAJOR - method contributions require comparison

### Limitation Honesty Check

| Limitation | Declared? | Assessment |
|------------|-----------|------------|
| ResNet-50 only | YES | Honest |
| PoC level | YES | Honest |
| Timing revision 20->15% | YES | Honest, shows scientific integrity |
| Vision only | YES | Honest |
| 5 seeds only | NO | MINOR-CRED-1 - should mention low sample size |

---

## Part 4: Human Review Notes (MINOR)

These issues are flagged for human review, NOT auto-fix:

1. **MINOR-ENG-1**: Methodology needs figure/diagram for detection pipeline
2. **MINOR-ENG-2**: Results could reference figures inline for readability
3. **MINOR-CRED-1**: Should acknowledge 5 seeds is low for statistical confidence claims

---

## Summary for Revision Agent

### Priority Fix List

| Priority | ID | Issue | Fix |
|----------|-----|-------|-----|
| 1 | MAJOR-ACC-1 | SNR 5.64 vs 5.32 inconsistency | Clarify: is 5.64 benchmark-specific or overall? Use consistent value in abstract and results |
| 2 | MAJOR-CRED-1 | No detection method baselines | Add discussion acknowledging this as limitation OR add comparison to gradient norm/loss curvature |

### Issues NOT for Auto-Fix

- MINOR items (engagement, figure suggestions) - human judgment required
- Statistical power concern - requires human decision on framing

---

**Review Complete**: 0 FATAL, 2 MAJOR, 3 MINOR issues identified.
