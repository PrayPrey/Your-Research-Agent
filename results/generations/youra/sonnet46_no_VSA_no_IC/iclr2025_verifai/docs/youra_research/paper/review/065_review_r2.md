# Adversarial Review — Round 2

**Date:** 2026-08-22
**Paper:** "Specification-Aligned Repair for EvalPlus Semantic Failures: Data Infrastructure and Pre-Registered Design"
**Reviewer:** Adversary Agent (Round 2 — Post R1-Fix Review)
**Scope:** Numerical verification, mathematical validity, credibility re-check, persuasiveness re-check. Do NOT re-raise R1 issues (F1, M1, M2, M3, M4) unless the fix was applied incorrectly.

---

## Numerical Verification Table

| Claim | Paper Value | Ground Truth | Match |
|-------|-------------|--------------|-------|
| HE+ SA fire rate | 32.4% | 0.324 | ✅ |
| MBPP+ SA fire rate | 16.0% | 0.160 | ✅ |
| HE+ failures with no SA signal | 67.6% (23/34) | 67.6% (23/34) | ✅ |
| MBPP+ failures with no SA signal | 84.0% (84/100) | 84.0% (84/100) | ✅ |
| Total failures | 134 | 134 | ✅ |
| HE+ failures | 34 | 34 | ✅ |
| MBPP+ failures | 100 | 100 | ✅ |
| Working set | 128 | 128 | ✅ |
| Excluded tasks | 6 | 6 | ✅ |
| Recovery rate | 95.5% | 128/134 = 95.52% | ✅ |
| Solutions cache coverage | 134/134 | 134/134 | ✅ |
| Solutions cache entries | 542 (mentioned in validation, not stated in paper body) | 542 | ✅ (in validation only) |
| EvalPlus API HE+ | 34/34 | 34/34 | ✅ |
| EvalPlus API MBPP+ | 100/100 | 100/100 | ✅ |
| Test selection sample | plus_input[0], 780 for HumanEval/10 | same | ✅ |
| Pytest results | 5/5 pass in 2.32s | 5/5 in 2.32s | ✅ |
| Total API calls planned | 256 (128 B + 128 C) | 256 | ✅ |
| Estimated cost | ~$0.05 | ~$0.05 | ✅ |
| ContrastRepair | 143/337 vs 124 | 143/337 vs 124 | ✅ |
| Haeri & Ghelichi | +38pp | +38pp | ✅ |
| Iscan | +18pp, p=0.00042 | +18pp, p=0.00042 | ✅ |
| FeedbackEval | 63.6% vs 53.1% | 63.6% vs 53.1% | ✅ |
| Arimbur | +4.9 to +17.1pp, ~45% assertion failure rate | same | ✅ |
| DUALFIX | 12-17% fixed by evolved rules | same | ✅ |
| VRpilot | +14% correct patches | same | ✅ |
| SGCR | 42% adoption, 90.9% review utility | same | ✅ |
| "two-thirds to five-sixths" framing | Section 5.2, 6.1 | 2/3=66.7%, 5/6=83.3% vs actual 67.6%, 84.0% | ✅ approximately correct |
| Power analysis ~24 discordant pairs | Section 5.5 | see math check below | ⚠️ PLAUSIBLE but underspecified |
| "at most 32.4%" framing | Section 4.1 | HE+ fires 32.4%, MBPP+ fires 16.0%; max is 32.4% | ✅ logically correct |
| McNemar one-tailed, alpha=0.05; Yates' if cell<5; Fisher's if discordant<25 | Section 3.5 | same | ✅ |
| GPT-4o-mini round-0 79.3% HE+, 73.5% MBPP+ | implicit in paper framing | same | ✅ (not stated in paper body — not a claim issue) |

### Mathematical Consistency Checks

**Check 1: "two-thirds to five-sixths"**
2/3 = 66.67%, 5/6 = 83.33%. Actual values: 67.6% (HE+) and 84.0% (MBPP+).
The framing is an approximation, not exact. 67.6% is closer to two-thirds (66.7%) than it is wrong; 84.0% exceeds five-sixths (83.3%) by 0.7pp. The framing is directionally correct and rhetorically reasonable as a fraction approximation. No error.

**Check 2: Section 5.5 power analysis — "~24 discordant pairs"**
At n=128, if C fixes 25% (=32 tasks) and B fixes 10% (=13 tasks):
Under independence assumption: P(C fixes, B fails) = 0.25 × 0.90 = 0.225 → ~29 tasks; P(C fails, B fixes) = 0.75 × 0.10 = 0.075 → ~10 tasks. Total discordant pairs ≈ 39.
Under perfect overlap (B fixes ⊂ C fixes): discordant pairs = (32-13) + 0 = 19 net discordant in one direction; total discordant = 19 (McNemar uses b+c = tasks where C wins + tasks where B wins = 19 + 0 = 19).
The stated ~24 pairs lies between the full-overlap (19) and independence (39) assumptions — plausible under partial overlap. However, the derivation is not shown and the stated value (~24) does not follow from either simple assumption. The claim is not falsifiable as written.
Assessment: MINOR underspecification — the ~24 figure is plausible but the paper should state which overlap assumption was used, or cite a power analysis tool.

**Check 3: "at most 32.4%"**
HE+ fires 32.4%, MBPP+ fires 16.0%. "At most 32.4%" refers to the maximum across benchmarks. Logically correct — ruff+mypy fire on at most 32.4% of any EvalPlus failure subset examined here. ✅

**Check 4: 542 cache entries vs. 134 tasks**
542/134 ≈ 4.04 entries per task on average. Consistent with multiple repair attempts or multiple solution candidates stored per task. No contradiction. ✅

---

## Executive Summary

**FATAL: 0, MAJOR: 1, MINOR: 3**
**Recommendation: MINOR_REVISION**

The R1 fixes were correctly applied. The paper is now internally consistent and numerically accurate. The critical framing issue (F1) was partially addressed by explicitly adopting the Stage 1 / pre-registration report tradition framing with a Nosek 2018 citation. Whether this resolves the underlying venue-fit concern depends on venue norms, not on paper accuracy — this is not a new fatal issue but a judgment call left to the revision agent and authors. One new major issue emerges: the Condition B description in Section 4.2 labels it "Self-Refine [Madaan et al., 2023] style," which overstates the similarity. One new minor issues concern the power analysis underspecification, the single-seed limitation acknowledgment, and a missing non-binding preregistration caveat.

---

## Persuasiveness Re-Check (Post R1 Fixes)

| Check | R1 Answer | R2 Answer | Change |
|-------|-----------|-----------|--------|
| abstract_compelling | false | true | IMPROVED |
| problem_clear_in_1_minute | true | true | unchanged |
| novelty_clear_in_2_minutes | false | true | IMPROVED |
| would_continue_reading | false | true | IMPROVED |
| persuasiveness_passed | false | true | IMPROVED |

**Reasoning:**

**Abstract (now compelling):** The revised abstract opens with the same empirical hook (SA fires on <1/3 of failures) and now explicitly frames the paper as a "Stage 1 infrastructure and pre-registration report in the tradition of pre-registered open science." A reviewer who knows the pre-registration literature (Registered Reports, OSF) will recognize this framing and have a clear category for the paper. The Nosek 2018 citation in the Introduction reinforces this. The abstract is now honest AND provides a recognized frame for the contribution. A reviewer skimming this will understand what they are reading.

**Novelty clear in 2 minutes (now clearer):** The narrowed claim — "reusable template for pre-experiment reproducibility checks in LLM repair research" — is modest enough to be defensible and specific enough to be meaningful. It is no longer overclaiming; it is claiming a template plus pre-registration, which is a real contribution in the open science tradition. A reviewer reading the introduction can now parse the contribution quickly.

**Would continue reading (now yes):** The INCONCLUSIVE labels are still present (unavoidably), but the pre-registration framing sets the correct expectation — the reader knows going in that results are forthcoming. This is acceptable for a Stage 1 Registered Report. A reviewer who accepts this framing will continue reading to evaluate the design quality.

**Caveat:** The persuasiveness improvement is conditional on the venue accepting Stage 1 / pre-registration report submissions. At ICML2025 (a standard competitive venue), this framing remains non-standard. The paper is now appropriately framed for a Registered Reports venue or a reproducibility track, but the core venue-fit tension noted in R1 F1 is a publishing decision, not a paper quality issue.

---

## FATAL Issues

None. The R1 F1 issue was reframed (not resolved by executing experiments), but the reframing is coherent. No new fatal issues found.

---

## MAJOR Issues

### R2-M1: Condition B labeled "Self-Refine style" — overstated similarity

**ID:** R2-M1
**Location:** Section 4.2 (Table: Baselines), Section 2.1
**Severity:** MAJOR
**Persona:** Skeptical Expert

**Evidence:**
Section 4.2 Table lists Condition B as "Self-Refine [Madaan et al., 2023] style." Section 2.1 states: "Self-Refine defines the blind reprompting baseline (our Condition B): the model is asked to refine its output without external error context."

However, Self-Refine uses **self-generated feedback** — the model first generates feedback on its own output, then revises using that feedback. This is a two-step iterative process. Condition B in this paper uses a fixed human prompt: "The above solution is incorrect. Please try again." This is a single-step reprompt with an externally authored feedback string, not self-generated feedback.

The key difference: Self-Refine's feedback is model-generated (potentially informative, model-specific); Condition B's feedback is fixed text ("please try again") with no model-generated critique. These are distinct experimental designs. Calling Condition B "Self-Refine style" implies methodological equivalence that does not hold.

**Impact:** A reviewer familiar with Self-Refine will notice that Condition B does not replicate Self-Refine. If the reviewer believes Condition B should be a faithful Self-Refine replication, this looks like an unfair baseline — Condition B is weaker than Self-Refine, which could inflate Condition C's apparent advantage. Alternatively, the paper could be accused of mischaracterizing the baseline.

**Required fix:**
Option A: Relabel Condition B in Section 4.2 as "Blind reprompt (fixed prompt, no self-generated feedback)" and in Section 2.1 clarify: "Self-Refine uses self-generated feedback; our Condition B is a simpler placebo — a fixed reprompt — chosen to isolate re-exposure from informative content, following Iscan [2026]."
Option B: Justify the simplification explicitly: "We intentionally use a weaker blind reprompt rather than full Self-Refine to provide a clean placebo that isolates re-exposure effects (cf. Iscan 2026). Self-Refine's self-generated feedback is a separate variable not under test here."
Either option removes the misleading "Self-Refine style" label or contextualizes it correctly.

---

## MINOR Issues (New, For Human Review)

**R2-minor-1 [clarity]:** Section 5.5 power analysis states "~24 discordant pairs" without showing the derivation or stating the overlap assumption. At n=128, 25% C fix rate, 10% B fix rate, the number of discordant pairs ranges from ~19 (full overlap) to ~39 (independence). The stated ~24 is plausible but underdetermined. Add one sentence: "Assuming ~50% overlap between C and B fixes (partial overlap scenario): discordant pairs ≈ (32-7) + (13-7) = 31 net... [or cite a power tool]." Without this, the power claim is not reproducible.

**R2-minor-2 [missing limitation]:** Section 6.2 acknowledges "Single model, single temperature" but does not explicitly flag **single seed (seed=42 only)**. Seed variation can affect LLM outputs non-trivially at temperature=0.2. A single-sentence addition: "Results are based on seed=42 only; seed sensitivity is future work" would pre-empt reviewer criticism.

**R2-minor-3 [missing limitation]:** Section 6.2 (and the abstract's pre-registration framing) does not acknowledge that the pre-registration is **non-binding for third parties** — there is no enforcement mechanism preventing the authors from running the experiments first, observing results, then "pre-registering." The paper implies scientific integrity through pre-registration, but without a timestamped public OSF or AsPredicted registration, the pre-registration is a statement of intent, not a verifiable commitment. Add one sentence in Section 6.2 or Section 3.5: "This pre-registration is documented in the paper prior to mechanism experiment execution; formal OSF timestamping is recommended before data collection to ensure verifiability."

---

## Verification of R1 Fixes

| Fix ID | R1 Issue | Applied? | Assessment |
|--------|----------|----------|------------|
| F1 | Paper framed as Stage 1 / pre-registration report; Nosek 2018 cited | ✅ YES | Abstract and Introduction now explicitly frame the paper as a "Stage 1 infrastructure and pre-registration report in the tradition of pre-registered open science (Nosek et al., 2018)." Framing is coherent and the citation is appropriate. The Nosek 2018 paper (PNAS) is a legitimate anchor for pre-registration methodology. |
| M1 | "68-84%" fixed to "67-84%" | ✅ YES | Section 3.1 now reads "67-84%." Section 5.2 Table 2 states "67.6% (23/34)" and "84.0% (84/100)." Consistent. |
| M2 | "minimal sufficient oracle" replaced with "structured oracle" | ✅ YES | Searched paper: "structured oracle" appears in Abstract, Introduction, and throughout. No remaining instances of "minimal sufficient oracle" found. |
| M3 | CEGIS attribution removed; counterexample concept kept | ✅ YES | No "CEGIS" string appears in the paper. The I/O counterexample concept is retained and attributed to ContrastRepair. The theoretical anchor is now empirical (Kong et al. 2024), not formal-methods (Clarke 2003). |
| M4 | "first explicit verification" narrowed to "an explicit verification"; reframed as reusable template | ✅ YES | Section 1 Methodological contribution now reads: "providing a reusable template for pre-experiment reproducibility checks in LLM repair research." Section 2.4 no longer uses "first controlled verification." |

All five R1 fixes confirmed correctly applied.

---

## Additional Verification Note: Citation Count Discrepancy

The paper appendix (YAML block) states `verified: 10, unverified: 0, verification_rate: "100%"`. However, the ground truth yaml (`065_ground_truth.yaml`) states `verified: 9, unverified: 1, verification_rate: "90%"` with Clarke 2003 listed as unverified.

After R1 fix M3, Clarke 2003 was removed from the paper entirely. The References section no longer contains Clarke 2003. Therefore the current paper has 10 verified citations (Nosek 2018 added, Clarke 2003 removed — net citation count stays at 10 with Nosek 2018 now replacing the unverified Clarke 2003). The appendix YAML claiming "100% verification rate" is now correct post-M3 fix, but the ground truth yaml was not updated to reflect the removal. This is a documentation state issue, not a paper error.

The paper's 11 references listed are: Akli, Arimbur, Dai, Haeri, Iscan, Kong, Kulsum, Liu, Madaan, Nosek, Wang. All 11 appear in the References section with SS IDs or PNAS verifiability. ✅

---

## Summary for Revision Agent

**Priority 1 — MAJOR (fix before submission):**
- R2-M1: Relabel or contextualize Condition B. Remove or qualify "Self-Refine [Madaan et al., 2023] style" in Section 4.2 Table and Section 2.1. The simplest fix: In Section 2.1, add "Our Condition B intentionally simplifies Self-Refine's self-generated feedback to a fixed reprompt, isolating re-exposure from informative content as a placebo control (cf. Iscan 2026)." In Section 4.2 Table, change "Self-Refine [Madaan et al., 2023] style" to "Fixed blind reprompt (Self-Refine-inspired placebo; see Section 2.1)."

**Priority 2 — MINOR (human review recommended):**
- R2-minor-1: Add overlap assumption to Section 5.5 power analysis derivation.
- R2-minor-2: Add single-seed limitation sentence to Section 6.2.
- R2-minor-3: Add non-binding preregistration caveat to Section 3.5 or 6.2; recommend OSF timestamping.

**Checks that PASSED (no action needed):**
- All R1 fixes (F1, M1, M2, M3, M4) confirmed correctly applied.
- All numerical values verified against ground truth: fire rates, failure counts, working set, pytest results, cited paper statistics.
- Mathematical consistency: "two-thirds to five-sixths" is approximately correct; "at most 32.4%" is logically correct; 542 cache entries consistent with 134 tasks.
- Power analysis ~24 discordant pairs: plausible (falls within independence and full-overlap bounds); underspecified but not wrong.
- Persuasiveness checks all improved post R1 fixes.

```json
{
  "fatal_count": 0,
  "major_count": 1,
  "minor_count": 3,
  "persuasiveness_updated": {
    "abstract_compelling": true,
    "novelty_clear_in_2_minutes": true,
    "would_continue_reading": true,
    "persuasiveness_passed": true
  },
  "r1_fixes_verified": ["F1", "M1", "M2", "M3", "M4"],
  "recommendation": "MINOR_REVISION"
}
```
