# Phase 6.5 Adversarial Review Changelog

**Date:** 2026-08-24  
**Rounds:** 2  
**Total Edits:** 5

---

## Edit 1: Abstract Rewrite (Hook First)

**Location:** Lines 15-17 (Abstract)  
**Issue:** FATAL — Buried lead (opens with boring problem, novelty in sentence 3)  
**Type:** Rewrite

**Before:**
```
LLM benchmark evaluation produces aggregate accuracy scores without explaining individual failures, blocking targeted correction strategies. When models fail factual questions, practitioners apply retrieval-augmented generation (RAG) or chain-of-thought (COT) prompting uniformly, missing opportunities to match interventions to root causes. We demonstrate that attention entropy over entity spans provides a diagnostic signal...
```

**After:**
```
**We automate failure-type diagnosis in LLM benchmarks using attention entropy, enabling targeted correction.** When GPT-2 makes entity-substitution errors on TruthfulQA, attention entropy over entity spans drops to near-zero (mean = 0.062) compared to non-entity errors (mean = 0.300), yielding a diagnostic signal (p < 0.001, Cohen's d = -1.13)...
```

**Rationale:** Lead with contribution (attention entropy diagnostic) not generic problem. Hook in first sentence.

---

## Edit 2: Mock Caveat Upfront (Abstract)

**Location:** Lines 15-17 (Abstract continuation)  
**Issue:** FATAL — Mock limitation buried in Discussion, not visible in abstract  
**Type:** Insert caveat

**Before:**
```
Mock validation shows matched routing achieves +24 percentage point improvement over mismatched routing, demonstrating pipeline feasibility pending real-world deployment.
```

**After:**
```
**CRITICAL LIMITATION:** We validate the attention pattern and classification mechanism in GPT-2 only; correction effectiveness tested with mock RAG/COT (configurable synthetic success rates) demonstrates +24 percentage point structural feasibility but **real-world deployment with Wikipedia API and GPT-judge remains future work**.
```

**Rationale:** Bored reviewer flags "too many caveats buried" → surface mock limitation immediately in abstract, not Section 6.

---

## Edit 3: Framework Contribution Scoping (Introduction)

**Location:** Line 43 (Framework contribution)  
**Issue:** FATAL — Mock framed as validation, not structural demo  
**Type:** Rewrite + caveat

**Before:**
```
**Framework.** We present mock validation of a matched routing structure (entity-error → RAG) showing +24 percentage point improvement over mismatched routing (entity-error → COT) in synthetic settings. The pipeline demonstrates structural feasibility across GPT-3.5 and Llama-2-7B, though real-world correction effectiveness remains pending validation with actual Wikipedia retrieval and GPT-judge evaluation.
```

**After:**
```
**Framework (MOCK VALIDATION ONLY).** We demonstrate matched routing structure (entity-error → RAG) with synthetic experiments showing +24 percentage point improvement over mismatched routing (entity-error → COT) using configurable mock success rates (RAG=55±5%, COT=30±5%). This ablation validates pipeline structure (dual-model framework, gate checking) but **NOT correction effectiveness** — real-world deployment with Wikipedia API, GPT-3.5 generation, and GPT-judge evaluation is future work (FW2, HIGH priority). The contribution here is structural feasibility, not deployed effectiveness.
```

**Rationale:** Skeptical expert flags "mock results presented as real-world effectiveness" → clarify this is ablation test, not deployment.

---

## Edit 4: Baseline Disclosure (Section 4.3)

**Location:** Lines 197-199 (Baselines)  
**Issue:** FATAL — Missing uniform RAG/COT baseline, compares only vs intentionally-broken mismatched  
**Type:** Insert limitation paragraph

**Before:**
```
**h-m2 (Correction):** Mismatched routing assigns entity-error → COT (wrong correction for failure type). We compare matched (entity → RAG) vs mismatched, requiring ≥20 percentage point or ≥50% relative improvement to demonstrate targeting root causes.

**Uniform Correction (Phase 5 Deferred).** Baselines applying RAG or COT to all failures regardless of type (tests value of routing) are evaluated in Phase 5 baseline comparison, not in Phase 4 validation.
```

**After:**
```
**h-m2 (Correction — MOCK ONLY):** We compare matched routing (entity → RAG) against (1) mismatched routing (entity → COT, wrong correction), and (2) random routing (50/50 RAG/COT). **LIMITATION:** Uniform RAG and uniform COT baselines (apply one correction to all failures) — the realistic practitioner strategy — are deferred to Phase 5. Our Phase 4 validation tests matched vs intentionally-broken mismatched, not vs real-world uniform correction. This limits claims about routing value until Phase 5 completion.
```

**Rationale:** Skeptical expert flags "baseline too weak" → explicitly state uniform correction (realistic alternative) is missing.

---

## Edit 5: Conclusion Scoping (Section 7)

**Location:** Lines 482-484 (Contributions + Limitations)  
**Issue:** MAJOR — Correction effectiveness still framed as contribution despite mock-only validation  
**Type:** Rewrite + baseline caveat

**Before:**
```
3. **Framework:** Mock validation of matched routing structure (entity → RAG: +24pp improvement over mismatched entity → COT) demonstrating pipeline feasibility, pending real-world correction effectiveness validation.

We acknowledge principled limitations: GPT-2-only attention patterns (multi-model replication pending FW1), synthetic correction results (real-world RAG validation pending FW2), manual gold labels (automated labeling pending FW4), single failure type (multi-class extension pending FW3), and 27% span alignment sample loss (sub-word-aware alignment pending FW5). These limitations bound our claims to proof-of-concept scope — we validate pattern existence and classification utility, not production-ready correction effectiveness.
```

**After:**
```
3. **Framework (structural feasibility only):** Mock validation with synthetic RAG/COT success rates demonstrates matched routing structure (+24pp over mismatched), but **correction effectiveness is unproven** — real-world Wikipedia API + GPT-judge validation is HIGH-priority future work (FW2). Additionally, we compare only against intentionally-broken mismatched routing, not against uniform RAG or uniform COT (the realistic practitioner baseline) — routing value vs uniform correction is untested.

We acknowledge principled limitations bounding claims to proof-of-concept: (1) GPT-2-only attention patterns — multi-model replication pending (FW1 HIGH), (2) **synthetic correction results** — real-world RAG effectiveness unvalidated (FW2 HIGH, critical for credibility), (3) **missing uniform-correction baseline** — routing value vs "apply RAG to all failures" unknown until Phase 5, (4) manual gold labels limiting scale (FW4), (5) single failure type — reasoning errors untested (FW3), (6) 27% span alignment loss (FW5). We validate diagnostic classification robustly; correction routing awaits real-world deployment and fair baseline comparison.
```

**Rationale:** Skeptical expert flags "effectiveness unproven but framed as contribution" → demote to structural demo, emphasize baseline gap.

---

## Summary Statistics

**Total Edits:** 5  
**Lines Changed:** ~20  
**Word Count Change:** +150 words (caveats added)  
**Sections Modified:** Abstract, Introduction, Methodology (Baselines), Conclusion

**Issue Resolution:**
- FATAL #1 (Buried lead): ✅ FIXED (Edit 1)
- FATAL #2 (Hidden mock caveat): ✅ FIXED (Edit 2)
- FATAL #3 (Mock as validation): ✅ FIXED (Edit 3, Edit 5)
- FATAL #4 (Missing baseline): ✅ FIXED (Edit 4, Edit 5)
- MAJOR #1 (Generalization overclaim): ✅ FIXED (Edit 3 multi-model scoping)
- MAJOR #2 (Novelty oversell): ✅ FIXED (Edit 1 reframe)
- MAJOR #3 (Problem importance): ✅ FIXED (Edit 1 hook)
- MAJOR #4 (GPT-2 outdated): ✅ ACKNOWLEDGED (Edit 2 scope)
- MINOR #1 (P-value rounding): ⚠️ DEFERRED (065_human_review_notes.md)

**Final Paper Status:** Converged, ready for human review + Phase 5 baseline comparison.
