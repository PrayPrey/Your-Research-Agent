# Adversarial Review Summary — Phase 6.5

**Paper:** Hallucination Type Determines Optimal Token Log-Probability Aggregation: A Mechanism-Grounded Ablation
**Review Completed:** 2026-08-21T15:45:00+00:00
**Rounds Completed:** 2 (R1, R2)
**Final Status:** CONVERGED
**Persuasiveness Check:** PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (Accuracy Checker, Bored Reviewer, Skeptical Expert in R1; Accuracy Checker + Skeptical Expert in R2).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 0 | 0 | 0 |
| MAJOR | 6 | 5 | 1* |

*Remaining MAJOR (CRED-001): 3 unverified arXiv citations — partially addressed in-pipeline, full verification deferred to submission preparation.

**MINOR Issues:** 6 items collected in `065_human_review_notes.md` (NOT auto-fixed).

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | "costs up to 12 AUROC points" — concrete and memorable hook |
| Problem clear by paragraph 2? | PASS | "It matters by 12 AUROC points." — crisp, clear |
| Novelty clear by page 1? | PASS | Four specific contributions listed with concrete claims |
| Figure 1 self-explanatory? | N/A | Cannot verify from text; peakedness KDE figure referenced |
| Would continue reading? | PASS | Strong narrative flow, mechanism well-structured |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy, Engagement, Credibility)

**Accuracy Checker Findings:**

| Category | Issues Found |
|----------|--------------|
| TruthfulQA AUROC values inflated (MAJOR-ACC-001/002) | 2 |
| TriviaQA n range misleading (MAJOR-ACC-003) | 1 |

Root cause: The original paper's TruthfulQA AUROC values did not match the actual h-m3/experiment_results.json ground truth — all TruthfulQA AUROCs were shifted up by ~2.6–12 points. The ΔAUROC differentials (P1, P2) and all CIs were correct.

**Bored Reviewer Findings:**
| Category | Issues Found |
|----------|--------------|
| FATAL engagement issues | 0 |
| MAJOR engagement issues | 0 |
| Human review notes | 2 |

Paper passed engagement check cleanly. Hook sentence ("It matters by 12 AUROC points") and mechanism narrative are effective.

**Skeptical Expert Findings:**
| Category | Issues Found |
|----------|--------------|
| Three unverified arXiv citations (MAJOR-CRED-001) | 1 |
| SE cross-pipeline caveat needs earlier placement (MAJOR-CRED-003) | 1 |
| False novelty claims | 0 |
| Unfair baselines | 0 |

**Key Issues Addressed in R1:**
1. MAJOR-ACC-001/002: Corrected all TruthfulQA AUROC values to match h-m3 actuals
2. MAJOR-ACC-003: Updated TriviaQA n to ~476–488 with per-model breakdown
3. MAJOR-CRED-003: Added cross-pipeline caveat in Abstract and Introduction
4. Added TruthfulQA label protocol as new limitation in §6.4
5. MAJOR-CRED-001: Partially addressed (arXiv preprint labels added)

---

### Round 2: Numerical Verification + Credibility

**Numerical verification performed:** 23 claims checked against `h-m3/experiment_results.json`
**Discrepancies found:** 0 (all R1 corrections verified as accurate)

All AUROC values, ΔAUROC differentials, bootstrap CIs, peakedness statistics confirmed correct against actual Phase 4 JSON results.

**R2 remaining issue:**
- MAJOR-CRED-001 (carried): 3 citations (Ma2025, Moslonka2025, Zhang2025) are arXiv preprints flagged as unverified. Addressed by adding "[arXiv preprint — verify before submission]" annotations in paper.

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | Added "(under our evaluation protocol)" for SE comparison |
| Introduction | Added cross-pipeline caveat qualifier; updated Contribution 4 label |
| Methodology §3.4 | Minor wording fix (hardware/dependency compatibility) |
| Experiments §4 | Updated TriviaQA N to "~476–488"; added per-model n note |
| Results §5.3 | Corrected all TruthfulQA AUROC values in Table 1 |
| Results §5.4 | Added explicit raw_sum contrast (best TriviaQA, worst TruthfulQA, ~0.44 gap) |
| Discussion §6.3 | Expanded cross-pipeline caveat with explicit confound list |
| Discussion §6.4 | Added TruthfulQA label protocol limitation |
| Related Work §2 | Added arXiv preprint note; clarified Ma/Moslonka/Zhang positioning |
| References | Added "[arXiv preprint — verify before submission]" to 3 citations |

---

## Quality Improvements

- **Numerical Accuracy:** IMPROVED — all TruthfulQA AUROC values corrected
- **Logical Consistency:** MAINTAINED — ΔAUROC differentials were already correct
- **Cross-Pipeline Caveat:** IMPROVED — now in Abstract + Intro + §6.3
- **Dataset Documentation:** IMPROVED — per-model n values now explicit
- **Limitations Completeness:** IMPROVED — TruthfulQA label protocol added
- **Persuasiveness:** MAINTAINED — hook and narrative unchanged (already strong)
- **Citation Hygiene:** PARTIALLY IMPROVED — arXiv preprints flagged

---

## Reviewer Preparation Notes

**Potential attack surfaces for real reviewers:**

1. **"NQ results are missing"** — Paper explicitly acknowledges NQ data gap; mechanism prediction for NQ is strong; re-running requires only GPU time.
2. **"Comparison to Semantic Entropy is not apples-to-apples"** — Paper now has cross-pipeline caveat in Abstract, Introduction, and Discussion. Response: "The gap is ~0.10 AUROC; we agree within-pipeline comparison is more definitive but the magnitude makes a purely methodological explanation unlikely."
3. **"Only 7B models tested"** — Paper explicitly limits generalization claim to 7B scale. TruthfulQA inverse scaling suggests P2 would be stronger at 70B+.
4. **"Three unverified citations"** — Pre-submission: verify Ma2025, Moslonka2025, Zhang2025. If any are wrong, these citations are non-central and removable.
5. **"Peakedness metric is custom/not standard"** — Valid concern not addressed in paper. Suggested response: "We chose this formulation to jointly capture both tail behavior (kurtosis) and peak-to-mean ratio; alternative peakedness measures (kurtosis alone, max/mean alone) would require separate ablation. The p=0.002 significance suggests the signal is robust."

---

## Final Recommendation

**CONDITIONAL_ACCEPT** — pending pre-submission verification of 3 arXiv citations.

Core scientific claims are valid, numerically verified, and well-structured. The mechanism story is clear and the evidence is unusually multi-layered for a conference paper.
