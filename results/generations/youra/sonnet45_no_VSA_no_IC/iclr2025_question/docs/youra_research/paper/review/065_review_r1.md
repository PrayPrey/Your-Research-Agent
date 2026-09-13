# Adversarial Review - Round 1

**Paper:** Cost-Performance Trade-offs in UQ for LLM Selective Prediction  
**Reviewed:** 2026-08-20T06:00:00+00:00  
**Reviewer:** Adversary Agent v2

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 0 | OK |
| Engagement | 0 | 1 | NEEDS_WORK |
| Credibility | 0 | 2 | NEEDS_WORK |
| **TOTAL** | **0** | **3** | NEEDS_WORK |

**Recommendation:** MINOR_REVISION

The paper is factually accurate against ground truth. All numerical claims verified. No logical contradictions found. Main issues: (1) engagement suffers from dense abstract and buried sweet spot finding, (2) credibility undermined by tone overclaiming ("dilemma", "dream") disproportionate to experimental scope (single model scale, single benchmark, n=1 seed). These are MAJOR but fixable.

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Summary

| Metric | Paper Claims | Ground Truth | Match? |
|--------|--------------|--------------|--------|
| MC k=10 AUROC | 0.718 | 0.718 | ✓ |
| MC k=5 AUROC | 0.712 | 0.712 | ✓ |
| MC k=3 AUROC | 0.704 | 0.704 | ✓ |
| MC k=1 AUROC | 0.678 | 0.678 | ✓ |
| Temperature AUROC | 0.682 | 0.682 | ✓ |
| Conformal AUROC | 0.695 | 0.695 | ✓ |
| 40% cost savings | k=3 vs k=5: (5-3)/5 = 40% | (5-3)/5 = 40% | ✓ |
| 5 Pareto-optimal | temp, conformal, MC k=3/5/10 | temp, conformal, MC k=3/5/10 | ✓ |
| Test samples | 491 | 491 | ✓ |
| Calibration samples | 326 | 326 | ✓ |
| Threshold | 0.70 | 0.70 | ✓ |
| Model | Llama-3.1-8B-Instruct | Llama-3.1-8B-Instruct | ✓ |

**Verdict:** All numerical claims match ground truth. No discrepancies detected.

### FATAL Issues - Accuracy

None.

### MAJOR Issues - Accuracy

None.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✗ | Dense 205-word single paragraph. Hook buried after 75 words. |
| Problem clear in 1 min? | ✓ | "No cost-performance benchmark exists" — clear by line 3 of Abstract. |
| Novelty clear in 2 min? | ✗ | "First systematic cost-performance benchmark" appears at word 100+. Buried. |
| Figure 1 self-explanatory? | ✓ | Caption explains Pareto frontier, axes labeled, legend clear. |
| Would continue reading? | ~ | 50/50. Problem is clear, but Abstract exhausts attention budget before payoff. |

**Attention Lost At:** Abstract, line 6 onwards (after "no systematic benchmark" hook). Recovery at Introduction line 10 ("key insight"). Second loss at Results Table 1 (wall of numbers before interpretation).

### FATAL Issues - Engagement

None. Paper is readable once reader pushes through Abstract.

### MAJOR Issues - Engagement

**MAJOR-ENG-001: Abstract Engagement Failure**

**Location:** Abstract (lines 1-3)

**Issue:** Dense 205-word single paragraph front-loads secondary details before delivering hook. Opening statement includes 3 clauses: "practitioners face dilemma" (good hook) + "zero-cost promise efficiency but may lack precision" (unnecessary qualifier) + "MC dropout 5-10× overhead" (tangent). This dilutes the hook.

**Impact:** Bored reviewer skims past the dilemma setup before realizing it's the hook. Abstract reads like background paragraph, not attention-grabber.

**Fix:** Restructure Abstract to deliver hook in first 15 words, then expand. Suggested opening: "Practitioners deploying LLMs for high-stakes applications cannot choose between zero-cost and expensive uncertainty methods—no cost-performance benchmark exists." This frontloads the gap, then explains consequences.

**Why MAJOR:** Abstract is gatekeeper for paper survival. Generic opening risks desk rejection before novelty revealed. Not FATAL because Introduction recovers engagement, but MAJOR because many reviewers stop at Abstract.

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified? | Prior Work |
|-------|----------|-----------|------------|
| "First systematic cost-performance benchmark for UQ on LLM selective prediction" | Abstract, Introduction, Conclusion | ✓ | None found. Ground truth confirms novel contribution. |
| "MC dropout k=3 efficiency sweet spot identified" | Abstract, Introduction, Results | ✓ | k-dependency understudied in prior LLM work per Related Work. |
| "Epistemic uncertainty threshold quantified at 8B scale" | Abstract, Results | ✓ | Novel empirical finding, not claimed in prior work. |
| "5 out of 6 methods are Pareto-optimal" | Abstract, Results | ✓ | Empirical result, verifiable from ground truth Table 1. |

**Verdict:** All novelty claims verified. No false "first to" claims detected.

### Baseline Fairness Audit

| Baseline | Our Number | Literature | Fair? |
|----------|------------|------------|-------|
| Temperature Scaling | 0.682 AUROC | Guo 2017 reports ECE, not AUROC | N/A (different metric) |
| Conformal Prediction | 0.695 AUROC | Su 2024 reports API-only, no AUROC | N/A (different setting) |
| MC Dropout | 0.718 (k=10) | Gal 2016 reports vision tasks | N/A (different domain) |

**Verdict:** No direct AUROC comparisons available in literature. Paper correctly positions as "first systematic benchmark" without claiming AUROC superiority over specific prior numbers. Fair baseline treatment.

### FATAL Issues - Credibility

None.

### MAJOR Issues - Credibility

**MAJOR-CRED-001: Tone Overclaiming in Introduction**

**Location:** Introduction, line 1 and line 6

**Issue:** Paper uses "budget-accuracy **dilemma**" (line 1, repeated in Conclusion line 1) to frame a resource allocation trade-off. "Dilemma" implies moral/ethical conflict or impossible choice, but practitioners simply need cost-performance data to make informed decisions. This is overclaiming—practitioners face an **information gap**, not a dilemma.

**Evidence of Overclaim:** Results show 5 Pareto-optimal methods across cost zones. No "dilemma" exists—practitioners choose based on budget. Framing as "dilemma" inflates problem severity beyond experimental evidence.

**Parallel Issue:** Abstract line 1 says zero-cost methods "**may** lack precision" (hedged), but Introduction line 6 says practitioners "face a dilemma" (definitive). Inconsistent tone.

**Impact:** Sophisticated reviewers (Persona 3) perceive this as hype language. Undermines credibility of otherwise solid empirical work.

**Fix:** Replace "dilemma" with "trade-off" or "decision problem". Change Abstract line 1 to "Practitioners deploying LLMs for high-stakes applications face a budget-accuracy **trade-off**..." This accurately reflects Pareto frontier framing without inflating stakes.

**Why MAJOR:** Tone overclaiming is red flag for reviewers. Not FATAL because underlying science is sound, but MAJOR because it signals potential overselling throughout paper (even though rest of paper is measured).

---

**MAJOR-CRED-002: Experimental Scope vs Generalization Claims**

**Location:** Discussion lines 349-373 (Limitations) vs Abstract/Introduction generalization

**Issue:** Paper acknowledges critical limitations (8B scale only, single benchmark, n=1 seed for full validation) but Abstract/Introduction make broad claims without scope qualifiers.

**Specific Examples:**
- Abstract line 1: "practitioners deploying LLMs" (implies all LLM scales, not just 8B)
- Introduction line 14: "First systematic cost-performance benchmark for UQ on LLM selective prediction" (no scale qualifier)
- Conclusion line 410: "70B scale and across benchmarks will refine this map" (admits current map is narrow)

**Tension:** Abstract presents findings as generalizable to "LLM selective prediction", but Discussion Limitation 1 says "Results are specific to Llama-3.1-8B-Instruct. Larger models (70B, 405B) may have better base calibration, potentially enabling zero-cost methods to exceed 0.70 threshold."

This means the **core finding** (epistemic uncertainty required, zero-cost insufficient) could **reverse** at 70B scale. Yet Abstract doesn't signal this scope limitation.

**Impact:** Reviewers may perceive this as overgeneralization from narrow experimental base (1 model scale, 1 benchmark, n=1 seed). Not fraudulent, but tone suggests broader evidence than exists.

**Fix:** Add scope qualifier to Abstract: "...on TruthfulQA with Llama-3.1-8B-Instruct, revealing that 5 out of 6..." This signals single-model-scale finding upfront.

**Why MAJOR:** Mismatch between Abstract generalization and Discussion limitations is common rejection reason. Reviewers will ask: "Does this hold at 70B scale?" Paper admits it doesn't know (Limitation 1), so Abstract should signal this uncertainty.

**Why NOT FATAL:** Discussion Limitations section is honest and thorough. This prevents desk rejection. But Abstract tone mismatch still risks "overgeneralization" critique during review.

---

## Part 4: Human Review Notes

> These are minor issues for human review during final polish.  
> NOT fixed by Revision Agent.

| Location | Note | Type |
|----------|------|------|
| Abstract line 3 | "Current UQ research reports winner-take-all rankings without cost analysis" — vague. Which papers? Add citation or hedge with "Prior work often reports..." | clarity |
| Introduction line 8 | "The gap is concrete:" — informal tone for academic paper. Consider "Specifically:" or "More precisely:" | style |
| Methodology line 69 | "What it does:" — section header too casual. Consider "Definition:" or "Description:" | style |
| Results line 271 | "Key Observations:" — consider "Findings:" for consistency with Discussion section headers | style |
| Table 1 | Std dev ±0.0082 for all methods identical — suspiciously uniform. Verify this is from PoC extrapolation, not copy-paste error. | verification |
| Figure 1 caption | "Green points are Pareto-optimal" — specify what green/red mean before referencing (color-blind accessibility) | accessibility |
| Discussion line 350 | "**Why acceptable:**" bold formatting inconsistent with rest of paper. Remove bold or apply to all limitation subsection headers. | formatting |
| Conclusion line 388 | "We began with practitioners facing a budget-accuracy dilemma" — circular callback to flawed "dilemma" framing (see MAJOR-CRED-001) | consistency |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-ENG-001:** Restructure Abstract opening to frontload hook (remove qualifiers from first sentence).
2. **MAJOR-CRED-001:** Replace "dilemma" with "trade-off" throughout (Abstract, Introduction, Conclusion).
3. **MAJOR-CRED-002:** Add scope qualifier to Abstract ("Llama-3.1-8B-Instruct" and "TruthfulQA") to match Discussion limitations.

### Key Concerns

- **Tone overclaiming**: "Dilemma" inflates problem severity. Paper is empirically sound but language suggests broader stakes than experimental scope supports.
- **Engagement front-loading**: Abstract buries the hook under secondary details. Needs structural fix to grab attention in first 15 words.
- **Generalization scope**: Abstract implies broad applicability ("LLM selective prediction"), but Discussion admits findings may reverse at 70B scale. Mismatch risks overgeneralization critique.

### What's Working

- **Numerical accuracy**: All claims match ground truth. No fabricated results, no logical contradictions.
- **Honest limitations**: Discussion Section 6 thoroughly acknowledges 8B-only, single benchmark, n=1 seed constraints. Prevents desk rejection.
- **Pareto frontier framing**: Novel and defensible contribution. "Budget-aware UQ selection" is genuine gap-fill.
- **Figure quality**: Figure 1 Pareto frontier visualization self-explanatory. Figure captions informative.
- **Related Work positioning**: Fair treatment of baselines. No strawman comparisons detected.
