# Phase 6.5 Adversarial Review — Round 1
**Date:** 2026-03-15
**Paper:** Prescreening-Gated GRPO Training on APPS: Binomial Variance Analysis and the SFT Prerequisite
**Venue:** ICML 2025

---

## Executive Summary

| Persona | FATAL | MAJOR | MINOR→HRN |
|---------|-------|-------|-----------|
| Accuracy Checker | 1 | 2 | 3 |
| Bored Reviewer | 0 | 2 | 2 |
| Skeptical Expert | 0 | 2 | 3 |
| **Total** | **1** | **6** | **8** |

**Overall Recommendation: MAJOR_REVISION**

The paper makes a clean, honest negative result but has one FATAL attribution error (Afterburner credited to "Liao et al." instead of "Du et al., 2025"), significant section numbering inconsistency, and credibility risks from tone that oversells a null result as a "replication."

---

## PART 1: Accuracy Check (Accuracy Checker)

### Ground Truth Verification

| Claim | Ground Truth | Paper | Status |
|-------|-------------|-------|--------|
| Pass rate | 0.0 (0%) | 0% | MATCH |
| S_term | 0.0 | 0.0 | MATCH |
| Problems in tractability window | 0 / 300 | 0/300 | MATCH |
| Zero reward fraction | 1.0 | implied (0% pass) | MATCH |
| Total solution attempts | 2,400 (300 × 8) | 2,400 | MATCH |
| Infrastructure | 15/15 tasks, 67/67 tests | 15/15, 67/67 | MATCH |
| h-m1 through h-m4 status | ALL BLOCKED | PROJECTED / BLOCKED | MATCH |
| Overall gate | FAIL | PARTIAL | MISMATCH — see AC-2 |
| Afterburner attribution | Du et al., 2025 | Liao et al., 2025 | FATAL MISMATCH — see AC-1 |
| Binomial variance: Var(r_ratio) | q(1-q)/T | q(1-q)/T | MATCH |
| Binomial variance: Var(r_binary) | q^T(1-q^T) | q^T(1-q^T) | MATCH |
| Variance ratio ρ ≥ 5x | q∈[0.3,0.55], T=5 | ≥5–20× | MATCH |

---

### Issues Found

**[AC-1] FATAL — Afterburner Attribution Error**

Sections 6.3, 6.6, and 7.1 all cite Afterburner as "[Liao et al., 2025]." Ground truth (AR2) mandates attribution to "Du et al., 2025." This is a factual error that will be caught immediately by any reviewer familiar with the literature. Every instance must be corrected to "Du et al., 2025." Affected locations:
- Section 6.3: "consistent with Afterburner [Liao et al., 2025]"
- Section 6.6: "Afterburner [Liao et al., 2025] result"
- Section 7.1: "consistent with Afterburner [Liao et al., 2025]"

Note: The Introduction and Related Work sections use "[ArXiv 2505.23387]" without author name — this is factually neutral but inconsistent in citation style. Flagged for human review.

---

**[AC-2] MAJOR — Overall Gate Reported as "PARTIAL" Instead of "FAIL"**

Table 2 reports the Overall Gate result as "PARTIAL" in the Pass/Fail column. Ground truth states `overall_gate_decision: FAIL`. The gate threshold is PASS; the gate was not passed. Calling it "PARTIAL" softens a binary failure. This is not a minor framing issue — it is an inaccurate status label that could mislead readers. The table entry must read FAIL.

---

**[AC-3] MAJOR — Section Numbering Inconsistency (AR4)**

The Introduction states: "Section 4 reports experimental results... Section 5 discusses... Section 6 concludes." However, the paper labels the results section as "# 6. Results" and the discussion as "# 7. Discussion." This is a 1–2 section offset mismatch. A reviewer reading sequentially will notice immediately. Requires correcting the introduction's section references to match actual section numbers (Results=6, Discussion=7, Conclusion=8 implied).

---

**[AC-4] MINOR → HRN — 0% Claim Needs Consistent Format-Mismatch Qualification (AR3)**

The Abstract states "Qwen2.5-Coder-7B-Instruct achieves 0% pass rate" without format-mismatch qualification. Section 6.3 correctly adds this nuance. The Abstract should include at minimum a parenthetical or clause acknowledging the execution-harness format issue.

---

**[AC-5] MINOR → HRN — "h-e1 quantitative metrics" Listed as Blocked but h-e1 Infrastructure PASSED**

Section 7.2 states: "All five sub-hypotheses (h-e1 quantitative metrics, h-m1 through h-m4) are blocked." But h-e1 infrastructure components PASS (15/15, 67/67). The wording conflates infrastructure success with gate failure and needs clarification.

---

**[AC-6] MINOR → HRN — Binomial Variance Formula Notation Ambiguity**

The paper must clearly state whether q is the per-rollout pass probability and T is the group size, or whether the Binomial applies across test cases. The S_term definition ("fraction of rollouts passing at least one test") must be explicitly reconciled with the Binomial parameterization.

---

## PART 2: Engagement Check (Bored Reviewer)

### Persuasiveness Assessment

**Abstract:** Well-structured, leads with genuine problem. "5–20 times higher" is attention-grabbing and correctly labeled analytical. 0% admission is memorable. Final sentence is punchy.

**Introduction:** The section outline mismatch (AC-3) will cause a bored reviewer to lose trust early.

**Section 6.3:** The framing of a negative result as "surprising finding" is appropriate. However, claiming "replicates and extends prior work" for a null result with a format failure is overclaiming.

**Section 6.5 (Projected Outcomes):** Including PROJECTED results is double-edged — signals rigor but needs better framing sentence.

---

### Issues Found

**[BR-1] MAJOR — "Replicates and Extends Prior Work" Is Overclaiming**

The Abstract states: "a finding that independently replicates and extends prior work." A 0% result caused by a format mismatch does not replicate a training experiment. It is *consistent with* prior work. "Replicates" implies running an experiment that produced the same outcome; instead, the paper's experiment failed before any training. This is hype language disproportionate to evidence = MAJOR per v2.0 overclaiming-tone rule.

**Fix:** Replace "independently replicates and extends" with "is consistent with and independently corroborates."

---

**[BR-2] MAJOR — Section 6.5 "Theoretical Projections" Needs Justification for Inclusion**

Table 3 presents four PROJECTED outcomes with no empirical backing. Without an explicit framing sentence explaining the epistemic value, Table 3 reads as padding to a bored reviewer.

**Fix:** Add: "We include these projections to enable the community to validate Stage 2 upon obtaining an SFT checkpoint; they follow directly from the validated Binomial variance model."

---

**[BR-3] MINOR → HRN — "Production-Ready Infrastructure" in Abstract Is Vague**

Should be tied to the 15/15 and 67/67 metrics explicitly, or the phrase replaced with the concrete claim.

---

**[BR-4] MINOR → HRN — Figure 3 Simulation Parameters Reproducibility**

Section 6.4 references Figure 3 with parameters (500 groups, q=0.45, T=5, G=8). These parameters should appear in methodology so readers can reproduce Figure 3 independently.

---

## PART 3: Credibility Check (Skeptical Expert)

### Novelty Audit

Core novelty claims:
1. Binomial variance derivation formalizing tractability window — FRAMING novel, derivation elementary
2. Prescreening pipeline validated at scale — CREDIBLE
3. 0% pass rate finding establishing SFT prerequisite — CREDIBLE but undermined by format-mismatch interpretation

### Baseline Audit

No comparison to alternative execution harnesses. If 0% is attributed to format mismatch, the paper has not established whether the model genuinely cannot solve APPS introductory problems.

---

### Issues Found

**[SE-1] MAJOR — No Alternative Harness Baseline for Format Mismatch Claim**

The paper attributes 0% to "format mismatch" but provides no evidence. At least one informal data point (e.g., pass rate under lenient harness, or cited benchmark result) would validate this interpretation. Without it, the attribution is speculation.

**Fix option:** Report pass@1 from a standard benchmark evaluation for Qwen2.5-Coder-7B-Instruct on APPS under lenient evaluation, or cite existing results.

---

**[SE-2] MAJOR — Binomial Derivation Presented Without Acknowledgment of Simplicity**

A skeptical expert will note that E[Var(r_ratio)] = q(1-q)/T is a one-line result from elementary statistics. Without proactively positioning this, the paper invites "your main theoretical contribution is Binomial statistics."

**Fix:** Add one sentence acknowledging the derivation is elementary and foregrounding the framing novelty.

---

**[SE-3] MINOR → HRN — T=5 Assumption Not Justified**

The tractability window analysis uses T=5 throughout. APPS introductory problems have T≥3 (by paper's own filter). Analysis should show robustness across T values or justify T=5 as representative.

---

**[SE-4] MINOR → HRN — "Hard Prerequisite" Language Is Too Strong**

"Hard prerequisite" implies necessity under all circumstances. Evidence supports "SFT is required for this model on this harness under these conditions."

---

**[SE-5] MINOR → HRN — Infrastructure Claims Lack Reproducibility Detail**

"15/15 tasks, 67/67 tests" is mentioned repeatedly but no test categories or harness details provided. Paper needs at minimum a brief description of what the 67 tests cover.

---

## PART 4: Human Review Notes (MINOR issues — NOT auto-fixable)

| # | Issue ID | Category | Description |
|---|----------|----------|-------------|
| 1 | AC-4 | clarity | Abstract 0% qualification — author judgment on abstract word count |
| 2 | AC-5 | clarity | h-e1 blocking language — separate infrastructure success from gate failure |
| 3 | AC-6 | clarity | Binomial notation reconciliation — confirm q parameterization |
| 4 | BR-3 | style | "Production-ready" language — tie to concrete metrics or define |
| 5 | BR-4 | formatting | Figure 3 simulation parameters — confirm reproducibility from methodology |
| 6 | SE-3 | clarity | T=5 justification — add sentence or T-sensitivity row |
| 7 | SE-4 | style | "Hard prerequisite" softening — author judgment on strength of claim |
| 8 | SE-5 | formatting | 67 tests breakdown — add parenthetical description of test categories |

---

## Summary for Revision Agent

### Priority-Ordered Fix List

**FATAL (fix first):**

1. **[AC-1] Replace all "Liao et al., 2025" with "Du et al., 2025"** — sections 6.3, 6.6, 7.1 confirmed. Search full paper and bibliography for any additional instances.

**MAJOR (fix with evidence or structural revision):**

2. **[AC-2] Correct Overall Gate from "PARTIAL" to "FAIL"** in Table 2 Pass/Fail column.

3. **[AC-3] Fix section numbering mismatch** — update Introduction cross-references to match actual section numbers (Results=6, Discussion=7).

4. **[BR-1] Replace "independently replicates and extends"** → "is consistent with and independently corroborates" in Abstract.

5. **[BR-2] Add framing sentence to Section 6.5** — justify why PROJECTED outcomes are included.

6. **[SE-1] Add alternative harness data point** for format-mismatch interpretation — at minimum cite Qwen2.5-Coder-7B-Instruct performance on standard benchmarks.

7. **[SE-2] Add acknowledgment of Binomial derivation simplicity** — one sentence in methodology section.

---

## Return Summary

```
FATAL_COUNT: 1
MAJOR_COUNT: 6
HUMAN_REVIEW_NOTES_COUNT: 8
RECOMMENDATION: MAJOR_REVISION
PERSUASIVENESS_PASSED: true
ABSTRACT_COMPELLING: true
WOULD_CONTINUE_READING: true
ATTENTION_LOST_AT: Section 6.3 (Liao et al. attribution — credibility break for informed readers)
```
