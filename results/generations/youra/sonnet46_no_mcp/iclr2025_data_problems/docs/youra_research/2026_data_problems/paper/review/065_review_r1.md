# Adversarial Review Report — Round 1

**Paper:** "A Cross-Corpus Contamination Atlas: Systematic 13-gram Overlap Mapping Across NLP Benchmarks and Training Corpora"
**Round:** R1
**Date:** 2026-05-04
**Personas:** Accuracy Checker | Bored Reviewer | Skeptical Expert
**Reviewer Agent:** Adversary (YouRA pipeline)

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL    | 0     |
| MAJOR    | 5     |
| MINOR    | 6 (→ human_review_notes) |

**Recommendation:** MAJOR_REVISION

The paper presents a coherent and largely well-verified empirical contribution. No fundamental numerical errors were found. However, five major issues require author attention before submission: (1) an overclaimed domain-stratification ratio ("2-3x" vs. actual 1.86x), (2) the h-m2 gate failure is disclosed but its implications for Contribution 3 are understated, (3) the novelty claim "first unified cross-corpus contamination atlas" requires explicit differentiation from prior multi-corpus work, (4) the C4 38% reduction claim needs stronger caveating given it rests on sampled + scaled estimates, and (5) the "corpus composition — not scale" causal framing is not well-supported relative to possible confounds.

---

## Ground Truth Verification Log

All 12 claims checked against pipeline ground truth.

| Claim | Paper Statement | GT Value | Verdict |
|-------|----------------|----------|---------|
| C1 | 43x ratio (professional_medicine 17.3% / high_school_mathematics 0.4%) | 43.25x | PASS — paper says "43×", acceptable rounding |
| C2 | KW H=590.82, p=2.73×10⁻⁸⁹ | exact match | PASS |
| C3 | Pile 6.53% > RedPajama 5.75% > C4 4.05% | exact match | PASS |
| C4 | C4 38% reduction vs. Pile | (6.53-4.05)/6.53 = 37.98% → 38% | PASS |
| C5 | Pile-RedPajama p=0.810 | exact match | PASS |
| C6 | KW H=17.51, p=1.58×10⁻⁴ | exact match | PASS |
| C7 | Cohen's d=0.85; "2-3x higher academic contamination" | Actual ratio: 6.64/3.57=1.860x | MAJOR ISSUE — see Persona 1 |
| C8 | WIMBD ρ=0.721 | exact match | PASS |
| C9 | Format sensitivity ρ=0.74 | actual: 0.7375 | MINOR — rounding acceptable but inconsistent (see below) |
| C10 | Sampling sensitivity ρ>0.995 | exact match | PASS |
| C11 | KW interaction H=22.08, p=0.0005 | exact match | PASS |
| C12 | Pile vs. C4 Dunn p=0.000156 | exact match | PASS |

---

## PERSONA 1 — ACCURACY CHECKER

### Finding A1 [MAJOR]: Domain Stratification Ratio Overclaimed

**Location:** Section 5.3, Contribution 3 in Introduction, Abstract area
**Paper claim:** "academic sub-tasks show 2-3× higher contamination than commonsense sub-tasks"
**Ground truth:** Actual ratio = 6.64% / 3.57% = 1.860×

The claim "2-3×" implies the ratio falls in the range [2.0, 3.0]. The verified ratio is 1.86×, which is below the stated floor of 2×. This is a factual overclaim, not a rounding issue. Cohen's d=0.85 is correct and the effect is still "large" by Cohen's conventions, but the ratio figure itself is wrong.

**Required fix:** Change "2-3× higher" to "approximately 1.9× higher" or "nearly 2× higher" everywhere in the manuscript. Do not use the range "2-3×" without evidence for the upper bound.

### Finding A2 [MAJOR]: h-m2 Gate Failure Understates Implication for Contribution 3

**Location:** Section 5.3, Table 4 footnote, Section 6.2 Limitation L3
**Issue:** The paper correctly discloses "Mann-Whitney FAILED (n=2 commonsense, underpowered)" and provides a footnote in Table 4. However, the Abstract and Introduction list domain stratification as a full contribution without any caveat. A reader who reads only the abstract will believe this result is statistically confirmed, when it is not confirmed by the pre-registered Mann-Whitney test.

The KW interaction test (H=22.08, p=0.0005) provides supporting evidence, but the pre-registered confirmatory test was specifically Mann-Whitney and it failed. The paper's own verification pipeline flagged this as SHOULD_WORK FAIL*.

**Required fix:** The abstract must include a qualifier: "domain-level stratification is supported by an interaction test but could not be confirmed by the pre-registered Mann-Whitney test due to insufficient category granularity (n=2 commonsense sub-tasks)." Alternatively, reframe Contribution 3 as preliminary/exploratory rather than confirmed.

### Finding A3 [MINOR]: Inconsistent Rounding for Format Sensitivity ρ

**Location:** Methodology section, Results Section 5.2
**Issue:** Ground truth ρ=0.7375. The paper reports 0.74 in the methodology description and 0.721 for the WIMBD consistency check (which is a different measure). The value 0.74 is a rounded form of 0.7375, which is acceptable to 2 decimal places. However, the paper should be internally consistent: if reporting to 3 decimal places elsewhere (e.g., p=0.810, H=590.82), it should either use 0.738 or explicitly note it is rounded to 2 d.p. This is minor but could catch a careful reviewer's eye.

**Suggested fix:** Report as ρ=0.74 consistently (2 d.p.) and add a parenthetical "(unrounded: 0.7375)" in supplementary if precision matters.

### Finding A4 [MINOR]: "40×" in Abstract vs. "43×" in Results

**Location:** Abstract ("40× contamination differentials"), Section 5.1 ("43× the rate")
**Issue:** The abstract uses "40×" as a rounded figure while the results section gives 43× (verified: 43.25×). This is intentional rounding for narrative flow but creates a slight inconsistency. A reviewer may flag this as either sloppy or as an attempt to selectively cite whichever number supports the narrative.

**Suggested fix:** Either use "more than 40×" consistently in the abstract, or use "43×" throughout and note it is rounded from 43.25×.

### Finding A5 [PASS]: h-m3 / Metric Consistency Correctly Handled

The paper includes Limitation L4 explicitly stating "Metric consistency (13-gram vs. Jaccard) unverified — h-m3 not run." This is appropriate disclosure. No overclaim found here.

### Finding A6 [PASS]: Pile WIMBD Proxy Correctly Disclosed

Limitation L1 clearly states "Pile rates are WIMBD published baselines, not independent measurements." C4/RedPajama sampling methodology is disclosed in Limitation L2 with explicit scaling factors. No hidden methodology found.

---

## PERSONA 2 — BORED REVIEWER

*Simulated reading of the paper as a NeurIPS reviewer with 5 papers to review.*

### Hook Assessment: PASS

Opening sentence: "Professional medicine questions appear in The Pile v1 at 43 times the rate of high school mathematics questions."

This is a concrete, striking statistic. It avoids the generic "X is an important problem" framing. As a busy reviewer I would continue past the first sentence. Grade: Strong hook.

### Abstract Compelling-ness: CONDITIONAL PASS

The abstract identifies: (1) the gap (single-number contamination vs. structured variation), (2) what was built (59×3 matrix), (3) key findings (43×, 38%, p=0.810 equivalence). The signal-to-noise ratio is high.

However, the abstract closes with the phrase "aggregate benchmark scores conceal 40× contamination differentials across the sub-tasks they average" — this is the correct punchline but it arrives late. A reader skimming only the first two sentences might not grasp the practical takeaway. Borderline pass.

### Problem Clear in First Minute (First 2 Paragraphs): PASS

The introduction opens with the hook statistic and immediately frames the gap: prior work treats contamination as a scalar, not as a structured matrix. The research question is stated clearly within the first paragraph. A reviewer would understand the problem in under 60 seconds.

### Novelty Clear in 2 Minutes: CONDITIONAL PASS

The contribution list is provided early. However, the "first unified cross-corpus contamination atlas" claim will immediately trigger a novelty challenge from any expert reviewer who is aware of WIMBD or multi-corpus studies. The paper does not immediately pre-empt this challenge by differentiating from WIMBD. A skeptical reader will pause here and look for a prior work section — if that section is delayed, the reviewer may flag the novelty claim as unsubstantiated before reading it.

**Suggestion:** Add 1-2 sentences immediately after the "first unified" claim that pre-empt WIMBD: "While WIMBD [cite] provides contamination counts for The Pile against individual datasets, no prior work has systematically mapped contamination across 59 sub-tasks and three corpora simultaneously in a unified matrix."

### Figure 1 Self-Explanatory: CANNOT FULLY ASSESS

Figure 1 is not reproduced in the provided paper text. Based on context (it is presumably the 59×3 heatmap atlas), the caption description suggests it shows the full matrix. A heatmap with 59 rows and 3 columns is self-explanatory if the axes are labeled and the color scale is clear. Assuming standard design, this is likely adequate. Flagged as needing visual inspection during revision.

### Attention Loss Assessment: MAJOR CONCERN

The methodology section (Section 3) describes WIMBD proxy use and scaling factors. A reviewer who has not worked with WIMBD may not immediately understand why WIMBD published rates are being used instead of direct measurement. This could cause a reviewer to disengage and flag the methodology as under-justified. The paper should front-load the motivation: "Direct measurement of The Pile v1 required WIMBD due to [infeasibility/unavailability of endpoint]" — this is in Limitation L1 but not in the methodology introduction.

**Potential attention drop:** Section 3 (Methodology) if scaling factor motivation is not clear.

### Organization: PASS

The structure (Abstract → Introduction → Background → Methodology → Results → Discussion/Limitations) is standard and logical. Section numbering is conventional. No structural issues found.

### Narrative Coherence: PASS

The paper's central narrative — corpus composition, not scale, determines contamination — threads through abstract, results, and discussion. The WIMBD equivalence finding (Pile ≈ RedPajama due to CommonCrawl ancestry) reinforces this narrative. The narrative blueprint appears to be followed.

---

## PERSONA 3 — SKEPTICAL EXPERT

### Challenge E1 [MAJOR]: "First Unified Cross-Corpus" Novelty Claim Needs Differentiation

**Prior work landscape:** WIMBD (Elazar et al., 2023 or similar) provides contamination analysis for The Pile. Data contamination analyses have been conducted for GPT-3, PaLM, and other models. The specific "59 sub-tasks × 3 corpora matrix" framing appears novel, but the paper does not spend enough effort distinguishing itself from:
- Single-corpus multi-benchmark studies
- Single-benchmark multi-corpus studies
- Model-level contamination analyses (which implicitly integrate corpus contamination)

If any prior work has done 2+ corpora × 2+ benchmarks systematically, the "first unified" claim weakens to "first at this scale." The paper must include a table or clear paragraph in related work explicitly showing what prior work covered (corpus × benchmark coverage), demonstrating the gap.

**Risk level:** If a reviewer knows of even one 2-corpus contamination study, they will reject the "first unified" framing without engagement.

### Challenge E2 [MAJOR]: "Corpus Composition — Not Scale" Causal Claim is Underpowered

**Section:** Abstract and Introduction principal claim: "corpus source composition — not scale — determines contamination profiles"

**Problem:** This causal claim is supported by 3 corpora. The confounds are substantial:
- C4 differs from The Pile not only in composition but in quality filtering methodology (Common Crawl filtered by language model perplexity)
- RedPajama-v1 and The Pile share CommonCrawl ancestry (which explains their equivalence) but this is a dataset-overlap argument, not purely a composition argument
- "Scale" is not formally tested — the paper does not include a regression with corpus size as a covariate
- The 3-corpus comparison does not allow decomposition of "composition" vs. "quality filtering" vs. "deduplication strategy" as separate factors

The finding that "Pile ≈ RedPajama due to CommonCrawl" actually supports a shared-data-source explanation, not a composition explanation per se. The paper should weaken the causal language: "corpus source overlap, reflected in composition differences, is associated with contamination level differences — though formal causal separation of composition, filtering, and deduplication effects requires a larger corpus study."

### Challenge E3 [MAJOR]: Domain Stratification Contribution Overstated Given Gate Failure

**Section:** Contribution 3, Section 5.3
**Issue:** The pre-registered confirmatory test for domain stratification (Mann-Whitney) failed (SHOULD_WORK FAIL*). The paper reframes this as an underpowered test, which is statistically legitimate. However, it then presents the KW interaction test as confirmatory evidence. There is a risk of HARKing (Hypothesizing After Results are Known): the Mann-Whitney was the pre-registered test; the KW interaction is a secondary test that happens to achieve significance.

The paper's own Table 4 footnote says "not hypothesis failure" — but this is an author assertion. Reviewers may not accept this framing without a more careful argument about why KW interaction is an equally valid test for this hypothesis, and why the pre-registered test was not achievable by design (n=2 is genuinely underpowered — this is a legitimate design constraint, not post-hoc rationalization, but it needs to be argued more carefully).

**Suggested fix:** Add a paragraph in Section 5.3 that: (a) explains why n=2 commonsense sub-tasks makes Mann-Whitney structurally underpowered (not a data quality issue), (b) argues that KW interaction is appropriate given the study design, and (c) explicitly states this contribution should be treated as exploratory pending replication with more commonsense sub-tasks.

### Challenge E4 [MINOR]: Missing Limitations — Sentence vs. Document Level Contamination

The paper uses 13-gram containment, which detects string overlap. This is a proxy for contamination but does not distinguish:
- **Test question leakage** (the exact question appears in training): the most damaging form
- **Answer leakage** (the correct answer appears with context in training)
- **Topic proximity** (training data discusses the same topic without containing the test item)

13-gram overlap likely captures the first category and partially the second, but this is not discussed. A model that memorized test questions would show 100% contamination; 17.3% for professional_medicine may still underestimate actual model contamination if questions appear in paraphrased form. This is a genuine missing limitation.

### Challenge E5 [MINOR]: Scaling Factors (×0.62, ×0.88) — Source and Validation Not Fully Clear

The methodology uses literature-calibrated scaling factors for 10% samples. The paper should: (a) cite the specific prior work from which these factors were derived, (b) report the uncertainty interval on these factors, and (c) discuss how scaling factor error propagates into the 38% C4 reduction claim. If the scaling factors have even 10% uncertainty, the 38% figure has a non-trivial confidence interval that is not reported.

### Challenge E6 [MINOR]: MMLU Benchmark Representation — 57 Sub-tasks vs. Full MMLU

MMLU has 57 sub-tasks covered; the paper does not discuss whether these are all MMLU sub-tasks or a subset. If it is the full set (MMLU has 57 subjects), this should be stated explicitly. If it is a subset, the selection criteria should be stated.

### Challenge E7 [MINOR]: BIG-Bench Hard Represented as Single Aggregate

BBH is treated as a single sub-task ("aggregate"). BBH has 23 tasks with highly heterogeneous domains (formal logic, word sorting, causal judgment). Using a single aggregate for BBH while using 57 sub-tasks for MMLU creates an asymmetric granularity that may bias cross-benchmark comparisons. This limitation is not discussed.

---

## Consolidated Issue List

### FATAL Issues (0)
None.

### MAJOR Issues (5)

| ID | Finding | Section | Required Action |
|----|---------|---------|----------------|
| M1 | Domain ratio "2-3x" overclaimed; actual 1.86x | Sec 5.3, Abstract, Intro | Change to "approximately 1.9×" everywhere |
| M2 | h-m2 gate failure implications understated in abstract/intro | Abstract, Intro, Sec 5.3 | Add qualifier to abstract; reframe Contribution 3 as exploratory |
| M3 | "First unified" novelty claim needs explicit prior work differentiation | Intro, Related Work | Add coverage table or explicit comparison paragraph |
| M4 | "Composition — not scale" causal claim underpowered; only 3 corpora, no formal scale regression | Abstract, Intro | Weaken causal language; acknowledge confounds (quality filtering, deduplication) |
| M5 | C4 38% reduction claim not caveated for scaling factor uncertainty | Sec 5.2, Abstract | Report confidence interval or explicitly state scaling factor uncertainty |

### MINOR Issues → human_review_notes (6)

| ID | Finding | Section | Note |
|----|---------|---------|------|
| N1 | "40×" in abstract vs. "43×" in results — inconsistent rounding | Abstract, Sec 5.1 | Standardize to "more than 40×" or "43×" throughout |
| N2 | Format sensitivity ρ=0.74 vs. unrounded 0.7375 — state rounding convention | Sec 3, 5.2 | Add "(to 2 d.p.)" or report as 0.738 |
| N3 | 13-gram contamination does not distinguish question vs. answer leakage | Sec 6.2 | Add as limitation bullet |
| N4 | Scaling factor source citation and uncertainty not fully stated | Sec 3 | Cite source; discuss propagated uncertainty |
| N5 | BBH treated as single aggregate vs. MMLU 57-way split | Sec 3 | Add methodological note on granularity asymmetry |
| N6 | Figure 1 caption self-explanatory status cannot be confirmed without figure | Sec 5.1 area | Verify during revision |

---

## Persuasiveness Assessment Summary

| Check | Result |
|-------|--------|
| Abstract compelling | PASS (conditional — punchline arrives late) |
| Problem clear in first minute | PASS |
| Novelty clear in 2 minutes | CONDITIONAL PASS (needs prior work pre-emption) |
| Figure 1 self-explanatory | CANNOT ASSESS (figure not provided) |
| Would continue reading after abstract | PASS |
| Attention lost at | Section 3 (Methodology — scaling factor motivation) |
| False novelty claims found | 1 (M3 — "first unified" needs differentiation) |
| Unfair baseline comparisons | 0 |
| Overclaims found | 2 (M1 — ratio; M4 — causal framing) |
| Missing limitations | YES (M5, N3, N4, N5) |

---

## Summary for Revision Agent (Prioritized Fix List)

**Priority 1 — Fix before any submission:**
1. [M1] Replace "2-3× higher" with "approximately 1.9× higher" for domain stratification ratio (Section 5.3, Abstract, Introduction, all occurrences)
2. [M2] Add qualifier to Abstract: domain stratification is supported by interaction test but not confirmed by pre-registered Mann-Whitney (n=2 commonsense sub-tasks); reframe Contribution 3 as exploratory
3. [M3] Add a paragraph or table in Related Work explicitly comparing coverage (corpora × benchmarks × sub-tasks) of this work vs. prior work (WIMBD, etc.); replace "first unified" with "first systematic multi-corpus, multi-sub-task" or provide citation evidence that no prior work achieved this coverage

**Priority 2 — Strengthen methodology section:**
4. [M4] Soften "corpus composition — not scale — determines contamination profiles" to association language; add a paragraph acknowledging quality filtering, deduplication, and shared data ancestry as alternative explanations; note formal decomposition requires >3 corpora
5. [M5] Report uncertainty interval on 38% C4 reduction figure given ×0.62 scaling factor, or explicitly state "assuming literature-calibrated scaling factors are accurate to ±X%"

**Priority 3 — Human review notes (do not auto-fix):**
6. [N1] Standardize "40×" vs. "43×" rounding across abstract and results
7. [N2] Clarify rounding convention for ρ=0.74 (unrounded: 0.7375)
8. [N3] Add limitation: 13-gram overlap does not distinguish test-question vs. answer-key leakage
9. [N4] Cite scaling factor source; discuss propagated uncertainty
10. [N5] Add methodological note on BBH granularity asymmetry vs. MMLU
11. [N6] Visually verify Figure 1 caption is self-explanatory

---

*End of Round 1 Adversarial Review — Adversary Agent*
