# Adversarial Review — Round 1

**Date:** 2026-08-22  
**Paper:** "Specification-Aligned Repair for EvalPlus Semantic Failures: Data Infrastructure and Pre-Registered Design"  
**Reviewer:** Adversary Agent (Three-Persona Review)

---

## Ground Truth Summary Table

| Metric | Ground Truth Value | Verified |
|--------|-------------------|----------|
| HE+ SA fire rate | 32.4% | YES |
| MBPP+ SA fire rate | 16.0% | YES |
| HE+ failures | 34 | YES |
| MBPP+ failures | 100 | YES |
| Total failures | 134 | YES |
| Working set | 128 (6 excluded) | YES |
| Recovery rate | 95.5% | YES |
| Solutions cache | 134/134, 542 entries | YES |
| EvalPlus API | 34/34 HE+, 100/100 MBPP+ | YES |
| Test selection | plus_input[0], 780 for HumanEval/10 | YES |
| Pytest results | 5/5 pass in 2.32s | YES |
| Excluded tasks | HumanEval/143, Mbpp/725, 726, 765, 805, 809 | YES |
| ContrastRepair | 143/337 vs 124 | YES |
| Haeri & Ghelichi 2026 | +38pp | YES |
| Iscan 2026 | +18pp, p=0.00042 | YES |
| FeedbackEval | 63.6% vs 53.1% | YES |
| h-e1 gate | FAIL | YES |
| h-e1-v2 gate | PASS | YES |
| P1/P2/P3 | INCONCLUSIVE | YES |
| Citation verification | 9/10 verified (Clarke 2003 unverified) | YES |
| Model | gpt-4o-mini, temp=0.2, seed=42 | YES |
| Statistical test | One-tailed McNemar (Yates' if cell<5; Fisher's exact if discordant pairs<25) | YES |

---

## Executive Summary

**FATAL: 1, MAJOR: 4, MINOR: 7**  
**Recommendation: MAJOR_REVISION**

The paper is honest about its incomplete state — all three predictions are INCONCLUSIVE, and the limitations section acknowledges this. The numerical claims are accurate throughout. The fatal issue is that the paper fundamentally misrepresents its venue fit: it is a preregistration report and a dataset characterization paper, not a research results paper, and submitting it to ICML2025 without executed mechanism experiments is a category error that no amount of honest labeling fixes. The major issues are: (1) the "68-84%" framing in Section 3.1 is slightly misleading, (2) "minimal sufficient oracle" is asserted without formal proof, (3) the Clarke 2003 CEGIS citation is unverified and used as a theoretical anchor, and (4) the contribution framing overstates novelty of reproducibility verification. These are fixable.

---

## Persuasiveness Assessment (Bored Reviewer)

| Check | Answer |
|-------|--------|
| abstract_compelling | false |
| problem_clear_in_1_minute | true |
| novelty_clear_in_2_minutes | false |
| figure_1_self_explanatory | false |
| would_continue_reading | false |
| attention_lost_at | "Section 5.4 — INCONCLUSIVE labels on all predictions" |
| false_novelty_claims_found | 2 |
| unfair_baseline_comparisons | 0 |
| overclaims_found | 3 |
| missing_limitations | true |

**Reasoning:**

**Abstract:** Opens with a genuinely interesting empirical hook (SA fires on <1/3 of failures). However, the abstract's second half pivots entirely to "our contribution is the data infrastructure and experimental design; the comparative results are forthcoming." A busy reviewer reading this at ICML will immediately ask: why is this a paper and not a preprint + OSF registration? The abstract is honest but not compelling for a conference paper.

**Problem clarity:** The problem is clear within 1 minute. The SA oracle failure framing and the semantic gap diagnosis are well-stated.

**Novelty:** The novelty is NOT clear in 2 minutes because the claimed novelty is "data infrastructure verification" — not a result that would normally appear as a conference contribution. A reviewer cannot identify what empirical contribution the paper makes beyond "we checked that data exists."

**Figure 1:** The paper says "Figure 1 shows the failure distribution" but provides no actual figure content in the text — only a description in the appendix (failure_distribution.png, pie chart). A reader cannot assess if Figure 1 is self-explanatory without seeing it.

**Attention loss:** The INCONCLUSIVE labels in Section 5.4 (Table 3) will cause most conference reviewers to stop reading seriously. All three pre-registered predictions show "INCONCLUSIVE" status. A reviewer expecting results sees none.

---

## FATAL Issues

### F1: Paper submitted to ICML2025 without executed primary experiments — venue mismatch is fatal

**ID:** F1  
**Location:** Abstract, Section 5.4 (Table 3), Section 6.1  
**Severity:** FATAL  
**Persona:** Bored Reviewer + Skeptical Expert  

**Evidence:**  
Table 3 shows all three pre-registered predictions (P1, P2, P3) as INCONCLUSIVE. The abstract states: "Our contribution is the data infrastructure and experimental design; the comparative results are forthcoming." The conclusion states "What remains is execution."

**Problem:** ICML2025 is a top-tier ML conference that accepts empirical results papers, methods papers, and theory papers. This paper has no empirical comparison result — it has: (a) a dataset characterization (SA fire rates), (b) a data infrastructure verification (existence check), and (c) a pre-registered design. None of these alone constitute a complete ICML contribution. The paper itself acknowledges "the mechanism experiments are forthcoming."

**Impact:** Any standard ICML reviewer will reject this on the grounds that the primary experiment (C vs B comparison, P1) is not run. The claim that the paper is a "preregistration report" is not a recognized ICML paper category.

**Required fix:**  
Option A (preferred): Execute h-m1 and h-m2 before submission. The estimated cost is ~$0.05 and 256 API calls. With results, the paper becomes a complete contribution.  
Option B: Reframe for a reproducibility/methodology workshop or a preprint venue (arXiv + OSF preregistration). Do not submit to ICML2025 without P1/P2 results.  
Option C (minimal): If submitting as a position/methodology paper to a venue that accepts this format, make the framing explicit in the title and abstract — "A Pre-Registration Report" or "Data Infrastructure Paper" — so reviewers are not misled.

---

## MAJOR Issues

### M1: "68-84%" framing in Section 3.1 is a minor inaccuracy

**ID:** M1  
**Location:** Section 3.1 ("Building on the observation that static analysis fails on 68-84% of EvalPlus semantic failures")  
**Severity:** MAJOR  
**Persona:** Accuracy Checker  

**Evidence:**  
Ground truth: HE+ SA fire rate = 32.4%, MBPP+ SA fire rate = 16.0%.  
Therefore: SA *fails* on 100%-32.4%=67.6% of HE+ and 100%-16.0%=84.0% of MBPP+.  
The paper states "68-84%" — rounding 67.6% up to 68% creates a minor discrepancy.

The Introduction uses "fewer than one in three" (67.6-84%) without specifying direction. Section 5.2 Table 2 correctly states "67.6% (23/34)" for HE+ with no SA signal. But Section 3.1 says "68-84%," which rounds HE+ incorrectly.

**Impact:** A fact-checker reviewer will catch this. 67.6% rounds to 68% only if rounding to 2 significant figures, but the exact count (23/34 = 67.647%) makes "68%" imprecise. The paper uses the exact value in Table 2 but the rounded value in Section 3.1 — internal inconsistency.

**Required fix:** Change "68-84%" to "67-84%" or "two-thirds to five-sixths" throughout, consistent with Section 5.2's precise values. Alternatively, keep "68%" with a footnote that 23/34=67.6%, rounded to nearest integer.

### M2: "Minimal sufficient oracle" claim is asserted without proof

**ID:** M2  
**Location:** Introduction (paragraph 3), Section 3.2, Discussion Section 6.1  
**Severity:** MAJOR  
**Persona:** Skeptical Expert  

**Evidence:**  
The paper repeatedly claims the specification triple is a "minimal sufficient oracle for semantic repair." The word "minimal" implies that removing any component would render the oracle insufficient. The word "sufficient" implies the triple is enough to fix semantic failures. Both claims are:  
- **Insufficient for "sufficient":** No repair experiment has been run. The triple has not been demonstrated to fix any failures. P1/P2 are INCONCLUSIVE.  
- **Unproven for "minimal":** The component ablation is explicitly deferred to future work (Section 6.2). The paper cannot claim minimality without testing (triple) vs. (triple minus each component).

The paper does acknowledge in Section 6.2 that "Component ablation deferred" and the triple is "tested as unit," but this acknowledgment in Limitations does not excuse the repeated overclaim of "minimal sufficient" in Introduction and Methodology.

**Impact:** A skeptical expert will flag this immediately. "Minimal sufficient oracle" is a strong formal claim that requires ablation evidence. Without it, the paper should say "proposed oracle" or "structured oracle."

**Required fix:** Replace all instances of "minimal sufficient oracle" with "proposed structured oracle" or "motivated oracle design." Reserve "minimal sufficient" for after ablation experiments confirm it. The introduction's paragraph 3 ("The triple is a minimal sufficient oracle") is the most egregious instance.

### M3: Clarke 2003 CEGIS citation is unverified and serves as theoretical anchor

**ID:** M3  
**Location:** Introduction (paragraph 3: "CEGIS-style counterexample"), Section 3.2 ("CEGIS-style counterexample")  
**Severity:** MAJOR  
**Persona:** Accuracy Checker + Skeptical Expert  

**Evidence:**  
Ground truth `citation_verification` confirms 1 unverified citation: "Clarke2003Counterexample — CEGIS reference, manual check recommended." The paper uses the CEGIS analogy as a core theoretical framing for the I/O counterexample component — it appears in the Introduction and Section 3.2 as the mechanism justification for Step 2.

However, the Clarke 2003 reference does NOT appear in the References section. The paper invokes the CEGIS concept inline without a citation marker, which means a reviewer cannot verify the reference. The ground truth flags it as unverified.

**Impact:** If the CEGIS citation is wrong (wrong year, wrong authors, or the analogy does not hold), the theoretical grounding of Step 2 weakens. A domain expert reviewer familiar with CEGIS will notice the missing citation.

**Required fix:** Verify Clarke et al. 2003 (or the correct CEGIS foundational paper — likely Clarke, Grumberg, Jha, Lu & Veith 2003, or Gulwani 2010 for program synthesis CEGIS). Add the citation inline wherever "CEGIS-style" appears. If the reference cannot be verified, replace the CEGIS analogy with a more defensible framing ("counterexample-guided repair" without the CEGIS attribution).

### M4: "First explicit verification of EvalPlus failure set reproducibility" — novelty overclaim

**ID:** M4  
**Location:** Section 1 ("Methodological contribution"), Section 2.4 ("first controlled verification"), Section 6.1  
**Severity:** MAJOR  
**Persona:** Skeptical Expert  

**Evidence:**  
The paper claims: "This is the first explicit verification that EvalPlus semantic failures are reproducibly recoverable from archive, enabling repair experiments without new baseline API calls."

Problems:  
1. **Novelty bar is low:** Verifying that a public dataset API returns expected results is standard practice, not a novel methodological contribution. The EvalPlus API is a public, maintained benchmark — confirming it returns 134 task IDs is straightforward infrastructure work.  
2. **"First explicit" is unverifiable:** The paper cannot know whether other labs have done this check internally. The claim is implicitly about publication, not execution.  
3. **The contribution conflates two things:** (a) verifying that the *failure set from a specific run* is archived and accessible (genuinely useful, but narrow), and (b) establishing EvalPlus reproducibility generally (a much stronger claim than the evidence supports — only one run's failure set is verified).

**Impact:** A reviewer will read "methodological contribution" and expect something generalizable. The 4-condition verification protocol is only applied to one specific GPT-4o-mini run's failure set. Calling this a generalizable methodological contribution is overstated.

**Required fix:** Narrow the claim to: "We verify and document the data infrastructure for this specific failure set, providing a template for similar verification in LLM repair research." Remove "first explicit verification" (unverifiable) and "methodological contribution" (overstated for what is essentially a data integrity check). Move this to a Data subsection rather than a top-level contribution bullet.

---

## MINOR Issues (Collected for Human Review — NOT auto-fixed)

**M-minor-1 [clarity]:** Abstract says "4/4 conditions, 5/5 tests pass" — the relationship between "4 conditions" (C1-C4) and "5 tests" (pytest) is not explained in the abstract. A reader unfamiliar with the paper's terminology cannot parse why these are different numbers.

**M-minor-2 [style]:** Introduction paragraph 5 ("Despite this convergent motivation, no prior work...") — "convergent motivation" is slightly jargon-heavy. Consider "Despite these converging results."

**M-minor-3 [formatting]:** Section 3.3 Table uses "API Calls" as a column header, with values "0," "128," "128." The value "0" for Condition A is potentially confusing — clarify "0 new API calls (existing data)."

**M-minor-4 [clarity]:** Section 5.5 states "expected scenario (25% fix rate under C, 10% under B): ~24 discordant pairs." The derivation of 24 discordant pairs from these fix rates is not shown and may be wrong. At n=128, if C fixes 25% (32 tasks) and B fixes 10% (13 tasks), discordant pairs depend on overlap, not just marginals. This needs a brief power analysis note or citation.

**M-minor-5 [clarity]:** "Figure 1 shows the failure distribution" (Section 4.1) — Figure 1 is never described inline (only in the appendix). Readers of a text-only version (common in reviewing) get no information.

**M-minor-6 [grammar]:** Introduction: "asking it to 'please try again' without explaining *what* went wrong changes almost nothing" — passive voice here is slightly awkward. Consider "provides almost no repair signal."

**M-minor-7 [style]:** The Appendix statistics block (YAML) at the end of the paper is unconventional for ICML format. This is pipeline metadata, not paper content. Remove or move to supplementary materials.

---

## Summary for Revision Agent

**Priority 1 — FATAL (must resolve before any submission):**
- F1: Execute h-m1 and h-m2 (cost: ~$0.05, 256 API calls) to get P1/P2 results, OR reframe/redirect to an appropriate venue for preregistration reports.

**Priority 2 — MAJOR (fix before resubmission):**
- M1: Fix "68-84%" to "67-84%" or use exact fraction; reconcile with Table 2's 67.6%.
- M2: Replace "minimal sufficient oracle" with "proposed structured oracle" throughout; reserve minimality claim for after ablation.
- M3: Verify and add Clarke 2003 CEGIS citation inline, or replace CEGIS framing with a defensible alternative.
- M4: Narrow "first explicit verification" novelty claim; reframe infrastructure verification as a template, not a methodological contribution.

**Priority 3 — MINOR (collect, human review):**
- M-minor-1 through M-minor-7: Clarity, style, and formatting issues listed above. Human review recommended; do not auto-fix.

**Checks that PASSED (no action needed):**
- All numerical values verified against ground_truth.yaml: fire rates (32.4%, 16.0%), failure counts (134, 34+100), working set (128, 95.5%), pytest results (5/5, 2.32s), ContrastRepair (143/337 vs 124), Haeri +38pp, Iscan +18pp p=0.00042, FeedbackEval 63.6% vs 53.1%).
- h-e1→h-e1-v2 trajectory described accurately.
- INCONCLUSIVE labels correctly applied to all three predictions.
- 6 excluded tasks correctly identified.
- No baseline comparison fairness issues found.
- Statistical design (McNemar, Yates' correction, Fisher's exact fallback) correctly described.
