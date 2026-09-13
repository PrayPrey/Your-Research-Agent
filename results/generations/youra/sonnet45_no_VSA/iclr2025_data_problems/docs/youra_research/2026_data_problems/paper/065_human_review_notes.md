# Phase 6.5 Human Review Notes - MINOR Issues

**Generated:** 2026-07-11T05:40:00Z  
**Round:** 1  
**Status:** Deferred for human review (not auto-fixed)

These MINOR issues do not affect the core claims and can be addressed in a final polishing pass. They are collected here for future reference.

---

## MINOR Issues (7 total)

### m1: Rounding Inconsistency
**Location:** Abstract/Intro vs. Tables  
**Issue:** Abstract and introduction use "ECE 0.53" (2 decimals) while Table 2 uses "0.5267" (4 decimals). This inconsistency may confuse readers.

**Suggested Fix:** Add footnote to first table: "Narrative sections round to 2 significant digits for readability; tables report full precision."

**Severity:** MINOR (does not affect interpretation)

---

### m2: Jargon-Heavy Abstract Opening
**Location:** Abstract, first sentence  
**Issue:** "Expected Calibration Error (ECE)" appears before defining what ECE means. Busy reviewers may not remember calibration metrics.

**Suggested Fix:** Define ECE in plain English first: "...confidence scores mismatch actual correctness by 53 percentage points (Expected Calibration Error, ECE)."

**Severity:** MINOR (readability improvement)

---

### m3: Table 1 Size
**Location:** Results section, Table 1  
**Issue:** Table 1 has only 3 rows and could be condensed into one sentence: "Code Llama ECE (0.53) is 3-6× higher than ResNet on CIFAR-100 (0.13) or ImageNet (0.08)." The table wastes vertical space.

**Suggested Fix:** Merge Table 1 into text. Reserve tables for multi-dimensional results (per-bin errors, ablations).

**Severity:** MINOR (formatting preference)

---

### m4: Conclusion Length
**Location:** Conclusion section  
**Issue:** Conclusion is 4 paragraphs (29 lines). Key takeaway ("84.8% ECE reduction, first benchmark") is buried in paragraph 2. Most readers skim conclusions quickly.

**Suggested Fix:** Shorten to 1 paragraph, 6 lines max:
> "We establish the first calibration benchmark for code generation (ECE 0.53), achieve 84.8% reduction via temperature scaling, and provide foundation for confidence-based agentic systems. Future work: real experiments, multi-model validation, training-time calibration."

**Severity:** MINOR (readability improvement)

---

### m5: Novelty vs. Kadavath et al. Clarification
**Location:** Related Work (lines 32-33)  
**Issue:** Paper cites Kadavath et al. (2022) who studied "LLM calibration on reasoning tasks" but then claims "no prior work evaluates code generation through lens of calibration." What's the difference between "reasoning tasks" and "code generation"?

**Suggested Fix:** Add clarification:
> "Kadavath et al. (2022) studied LLM calibration qualitatively on reasoning tasks but did not quantify ECE or apply post-hoc methods. Our work extends calibration analysis to CODE-SPECIFIC benchmarks (MBPP, HumanEval) with quantitative ECE measurement."

**Severity:** MINOR (clarification would strengthen positioning)

---

### m6: Autoregressive Hypothesis Caveat
**Location:** Discussion (lines 415-419)  
**Issue:** Paper claims "autoregressive probability aggregation causes overconfidence" but provides no ablation study. This is a hypothesis, not proven fact.

**Ground Truth:** Flags this as "medium confidence" and "hypothesis, not proven via ablation" (line 127).

**Suggested Fix:** Add caveat:
> "We hypothesize that autoregressive probability aggregation amplifies miscalibration, but this requires future ablation studies comparing autoregressive vs. non-autoregressive models and measuring per-token vs. sequence-level confidence."

**Severity:** MINOR (intellectual honesty improvement)

---

### m7: "Foundation" vs. "Prerequisite" Wording
**Location:** Introduction (line 19), Conclusion (line 15)  
**Issue:** Paper claims to provide "foundation for confidence-based iteration control" but only validated H-E1 (calibration exists), not H-M1 (monotonicity), H-M2 (marginal benefit), or H-C1 (system integration).

**Ground Truth:** Acknowledges "Prerequisite is necessary but not sufficient; H-M1, H-M2, H-C1 may fail" (line 148).

**Current Status:** This was partially addressed in Revision R1 by adding "Full validation requires testing monotonicity (H-M1), marginal benefit (H-M2), and system integration (H-C1)" to Conclusion.

**Suggested Fix:** Consider softening Introduction as well:
> "By establishing calibrated confidence as a necessary prerequisite, our work enables future research on adaptive resource allocation policies..."

**Severity:** MINOR (already partially fixed in R1)

---

## Summary

All 7 MINOR issues are **style, readability, or clarification** improvements. None affect the validity of core claims:
- ✅ ECE reduction 84.8% (verified against ground truth)
- ✅ Pass@1 preservation 0.0% (verified)
- ✅ Baseline ECE 0.53 (verified)
- ✅ Limitations disclosed (simulation mode, single model/dataset)

**Recommendation:** Address these in final polishing pass before submission. Not urgent for current draft.

---

## Auto-Fixed Issues (Reference)

The following issues were auto-fixed in Revision Round 1:
- ✅ F1, F2: "3×" → "3-6×" (global fix)
- ✅ F3: "5-6× larger effect" → "6-17× larger effect"
- ✅ M3: Novelty claim softened ("first" → "to our knowledge, first")
- ✅ M4: Cross-domain comparison disclaimer added
- ✅ M5: 84.8% vs 5-15% reframed as "more room for improvement"
- ✅ M6: T*=2512.71 removed from table, marked as artifact
