---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: LLM Calibration as Self-Contained Code Verifier"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-18
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Formal methods for generative AI — specifically, using LLMs as probabilistic verifiers of code correctness with self-contained difficulty stratification (bootstrapped from the experiment's own pass@1 data), measuring calibration quality via ECE and Brier score on existing benchmarks (HumanEval+, MBPP+).

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — Third Reflection)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

This research is motivated by the VerifAI: AI Verification in the Wild workshop at ICLR 2025, which explores the intersection of scale-driven generative AI and correctness-focused formal verification principles. The workshop highlights multiple research angles: (1) Generative AI for formal methods — using ML to guide proof search and theorem proving; (2) Formal methods for generative AI — using SMT solvers, static analyzers, automata to constrain and verify AI outputs; (3) AI as verifiers — using probabilistic methods as "soft assurance" alternatives to hard formal guarantees; and (4) Special Theme: LLMs for Code Generation — integrating formal structures (CFGs, static analyzers, SMT-guided repair) into LLM-driven code generation.

The current execution follows a THIRD ROUTE_TO_0 routing decision. Previous attempts explored: (Run 1) static analysis feedback signal type as Repair@1 predictor — failed due to FeedbackEval's ~85% semantic bug composition; (Run 2) assertion message coverage classifier on HumanEval/MBPP — marginally failed due to mock data artifact; (Run 3) P(True) logprob calibration with external leaderboard CSV for difficulty tiers — failed because external CSV was never downloaded (all 540 problems assigned "unknown" difficulty, ΔECE=NaN). The P(True) mechanism itself worked (values 0.57–0.91, ECE_overall computed successfully). The new direction retains the "AI as verifiers" calibration angle but replaces the external CSV difficulty definition with a **self-contained bootstrap** from the experiment's own pass@1 data.

Source Type: Workshop CFP / ROUTE_TO_0 Recovery Input (Third Reflection)

---

## Lessons from Previous Attempts

### What Was Tried Before

**Run 1 (h-m1):** Signal-type ablation — compiler-only (pyflakes) vs. type-checker-only (mypy) vs. linter-only (pylint) feedback as predictor of Repair@1 improvement on FeedbackEval. Ran 30,825 LLM calls across 5 models × 5 conditions × 1,233 instances.

**Run 2 (h-e1, first attempt):** Assertion message coverage classifier — whether test failure messages classify as L1_binary or L2_assertion on HumanEval/MBPP. Used MockGenerator + 3 models. HumanEval 0.9654 PASS, MBPP 0.9429 FAIL (threshold 0.95).

**Run 3 (h-e1, second attempt):** P(True) logprob elicitation to measure LLM calibration (ECE) stratified by difficulty tiers (hard vs. easy) using EvalPlus leaderboard CSV. P(True) mechanism activated (0.57–0.91), but difficulty assignment failed: leaderboard CSV was never downloaded → all 542 problems = "unknown" → ΔECE=NaN.

### Why Each Failed

**Run 1 failure:**
- ~85% of FeedbackEval instances contain semantic/logical bugs undetectable by pyflakes, mypy, pylint
- Extractability: pyflakes 8.9%, mypy 9.6% — nearly no useful output
- Signal_type LLR coefficients all p > 0.89 — completely non-predictive
- Significant LLR effect (p=2.87e-29) was driven by MODEL IDENTITY, not signal type
- Fundamental mechanism mismatch: tools can't detect the error types in FeedbackEval

**Run 2 failure:**
- MBPP coverage_rate 0.9429 fell just below the 0.95 threshold (5.71% gap)
- Root cause: MockGenerator over-represented TypeError/AttributeError/IndexError (L1_binary) instead of wrong-value errors (L2_assertion) that real LLM code produces
- ASSERTION_PATTERN did not match pytest --tb=short format (`E   assert X == Y`, not `AssertionError: assert X == Y`)
- Mock data artifact, not methodology failure — HumanEval 0.9654 validates mechanism is sound

**Run 3 failure:**
- External EvalPlus leaderboard CSV (T-DATA-1 task) was listed as "todo" but never executed
- data_loader.py `assign_difficulty_tiers()` falls back to "unknown" when CSV is absent
- n_hard=0, n_easy=0 → ΔECE=NaN for all 3 LLM families
- Infrastructure was otherwise WORKING: EvalPlus evaluation, solution generation, ECE_overall all valid

### How This New Direction Avoids These Pitfalls

1. **No static analysis dependency**: Difficulty is not based on static analysis of any kind (Run 1 lesson applied)
2. **No mock data**: Uses real LLM API calls for confidence elicitation — no MockGenerator artifacts (Run 2 lesson applied)
3. **No external CSV dependency**: Self-contained difficulty tiers bootstrapped from the experiment's own pass@1 across k=5 solutions — zero external file dependency (Run 3 lesson applied — **the critical fix**)
4. **Self-contained definition**: easy = pass@1 ≥ 0.6 (majority of 5 solutions pass), hard = pass@1 < 0.2 (rare pass) — derived entirely from the experiment's own execution results
5. **Proven infrastructure reuse**: P(True) logprob mechanism WORKS (validated in Run 3), EvalPlus API WORKS, PytestRunner WORKS — reuse all, only replace CSV-based difficulty with bootstrap
6. **Continuous metrics**: ECE, Brier score — no threshold sensitivity (unlike 0.95 coverage_rate gate in Run 2)

---

## Session Plan

Auto-extracted from structured input (ROUTE_TO_0 Third Reflection Recovery Mode). Research direction synthesized from VerifAI CFP "AI as verifiers" angle, filtered through three previous failure contexts. The core hypothesis pivot: retain the P(True) + ECE architecture from Run 3, replace only the broken external-CSV difficulty definition with a self-contained bootstrap.

---

## Technique Sessions

Auto-Fill Mode — No interactive sessions (ROUTE_TO_0 automated extraction, third reflection)

---

## Research Question Development

### Initial Question

Do LLMs exhibit measurably different Expected Calibration Error (ECE) when predicting code correctness for hard vs. easy problems, where difficulty is defined self-containedly from the experiment's own pass@1 distribution across k=5 generated solutions?

### Refined Question

When LLMs predict code correctness via P(True) logprob elicitation on HumanEval+ and MBPP+, do they exhibit significantly higher calibration error (ECE) on hard-tier problems (pass@1 < 0.2 across k solutions, bootstrapped from the same experiment) compared to easy-tier problems (pass@1 ≥ 0.6), and does this calibration gap vary with model scale?

### Detailed Sub-Questions

1. **Self-contained difficulty stratification**: Using only the experiment's own pass@1 data (k=5 solutions per problem across 3 LLM families), do hard-tier and easy-tier problem sets contain sufficient problems (n ≥ 20 each) to enable statistically meaningful ECE comparison? This validates the bootstrap approach as a self-contained alternative to external leaderboard CSVs.

2. **Calibration gap measurement**: Is ΔECE = ECE(hard) − ECE(easy) statistically significant (t-test p < 0.05, |ΔECE| > 0.05) across all three LLM families tested (NousResearch Llama3-8B, CodeLlama-7B, DeepSeek-Coder-6.7B)? This is the primary hypothesis to confirm.

3. **Model scale and calibration**: Among the tested models, do larger or code-specialized models (DeepSeek-Coder) exhibit lower ECE overall compared to general-purpose models, and does the calibration gap between hard and easy problems differ by model architecture?

4. **Difficulty tier sensitivity**: How sensitive are the ECE results to the pass@1 threshold choice (0.2 for hard, 0.6 for easy)? Does a ±0.1 threshold variation change the sign or significance of ΔECE? This guards against threshold-sensitivity failure.

5. **Formal methods integration opportunity**: Can coupling P(True) confidence with the ground-truth execution oracle (EvalPlus test results) create a hybrid verifier with lower ECE than the LLM alone? This addresses the VerifAI "AI as verifiers" angle: when is probabilistic verification sufficient vs. when does formal execution remain essential?

**FEASIBILITY CONSTRAINTS VERIFICATION:**
- All questions answerable using existing benchmarks: HumanEval+ (EvalPlus), MBPP+ (EvalPlus)
- No external CSVs required — difficulty tiers derived from experiment's own k=5 pass@1 data
- No human evaluation — ground truth is automated test execution (EvalPlus Python API)
- No synthetic/mock data — real LLM outputs and real unit tests
- Infrastructure pre-validated in Run 3: PytestRunner, DataLoader, EvalPlus API, P(True) elicitation all WORKING
- Prior work baseline: Kadavath et al. (2022) P(True) self-knowledge, calibration literature

---

## Reference Papers

Not provided in CFP input — will discover in Phase 1. Suggested search targets:
- Kadavath et al. (2022) "Language Models (Mostly) Know What They Know" — P(True) logprob self-knowledge (direct methodology basis)
- Xiong et al. (2024) calibration survey of LLMs
- Chen et al. (2021) "Evaluating Large Language Models Trained on Code" (HumanEval benchmark)
- Austin et al. (2021) "Program Synthesis with Large Language Models" (MBPP benchmark)
- Liu et al. (2023) EvalPlus / HumanEval+ (augmented test cases — directly used)
- Guo et al. (2017) "On Calibration of Modern Neural Networks" (ECE methodology foundation)
- Works on LLM self-verification and self-debugging that use LLM confidence as acceptance criterion
- SMT-guided repair and formal verification + LLM integration (VerifAI special theme context)

---

## Validation Results

### So What Test

**Significance:** LLM-as-verifier calibration is a central open problem in the VerifAI workshop scope. The finding has direct implications regardless of outcome:
- If LLMs ARE well-calibrated for code verification → probabilistic "soft assurance" can substitute for expensive formal verification in practical pipelines
- If LLMs are POORLY calibrated (especially on hard problems) → formal execution oracles remain essential, and hybrid approaches (LLM confidence + formal oracle) are needed

**Novelty within VerifAI:** Prior calibration work (Kadavath 2022) focuses on factual Q&A, not code verification. No existing work examines whether LLM verifier calibration is systematically worse for harder problems using a self-contained difficulty definition — this gap is directly relevant to VerifAI's "AI as verifiers" theme.

**Avoids past pitfall of threshold sensitivity:** ECE is a continuous metric; no arbitrary pass/fail threshold is imposed on the primary result. The gate criterion can be calibrated appropriately (e.g., ΔECE significance rather than absolute threshold).

### Feasibility Check

**Mechanism operability pre-verified in Run 3:**
- P(True) logprob elicitation: ACTIVATED and working (values 0.57–0.91, non-degenerate)
- EvalPlus ground truth evaluation: Working for HumanEval+ (164) + MBPP+ (378) = 542 problems
- Solution generation: Complete for 3 HF models, k=5 solutions each
- ECE_overall: Computed successfully (0.4895, 0.5218, 0.1358 for the three models)
- **Only broken component:** external CSV difficulty assignment → replaced with self-contained bootstrap

**Self-contained bootstrap viability:**
- With 542 problems and k=5 solutions from 3 model families, approximately:
  - Hard tier (pass@1 < 0.2): ~100-150 problems (per model family)
  - Easy tier (pass@1 ≥ 0.6): ~150-200 problems (per model family)
  - Both tiers well above n=20 minimum for ECE computation
- Bootstrap difficulty is model-specific: each model family gets its own hard/easy stratification based on its own performance

**Implementation complexity:** LOW — primary change is replacing 5 lines of CSV-loading code with pass@1 computation from the existing solution generation output. All other infrastructure reused from Run 3 h-e1 codebase.

---

## Phase 1 Input Package

<phase1-input>

### research_question
When LLMs predict code correctness via P(True) logprob elicitation on existing benchmarks (HumanEval+, MBPP+), do they exhibit significantly higher calibration error (ECE) on hard-tier problems compared to easy-tier problems, where difficulty tiers are defined self-containedly from the experiment's own pass@1 distribution across k generated solutions?

### detailed_question
1. Using the experiment's own pass@1 data (k=5 solutions per problem), do bootstrapped hard-tier (pass@1 < 0.2) and easy-tier (pass@1 ≥ 0.6) problem sets contain sufficient problems (n ≥ 20 each) to enable statistically meaningful ECE comparison on HumanEval+ and MBPP+?
2. Is ΔECE = ECE(hard) − ECE(easy) statistically significant (t-test p < 0.05, |ΔECE| > 0.05) across NousResearch Llama3-8B, CodeLlama-7B, and DeepSeek-Coder-6.7B?
3. Do code-specialized models (DeepSeek-Coder) show lower ECE overall, and does the calibration gap between hard and easy tiers differ by model architecture?
4. How sensitive are ECE results to the pass@1 threshold choice (±0.1 variation), ensuring the finding is not threshold-dependent?
5. Does coupling P(True) confidence with the formal execution oracle (EvalPlus ground truth) yield a hybrid verifier with lower ECE than the LLM alone?

### reference_papers
Not provided — will discover in Phase 1. Priority targets: Kadavath et al. (2022) P(True) self-knowledge and calibration; Xiong et al. (2024) LLM calibration survey; Guo et al. (2017) ECE methodology; Chen et al. (2021) HumanEval; Austin et al. (2021) MBPP; Liu et al. (2023) EvalPlus augmented benchmarks; LLM self-verification and self-debugging with confidence-based acceptance; SMT-guided repair integration for VerifAI context.

</phase1-input>

---

## Session Insights

### Key Discoveries

- Run 3's ONLY failure was the missing external leaderboard CSV — all other infrastructure (P(True), EvalPlus, ECE_overall) was working; this is the highest-confidence direction to date
- Self-contained difficulty bootstrap (pass@1 from own k=5 solutions) eliminates ALL external dependency while providing model-specific difficulty that is arguably more meaningful than a universal leaderboard ranking
- Three previous failure modes are now each specifically addressed: (1) no static analysis reliance, (2) no mock data, (3) no external CSV
- Calibration metrics (ECE, Brier score) are threshold-free and continuous — eliminates the sharp threshold sensitivity that caused Run 2's marginal failure
- FeedbackEval is explicitly excluded (85% semantic bugs confirmed incompatible with any verification mechanism that doesn't use execution oracle)
- The existing h-e1 codebase from Run 3 is essentially ready to run — only 5-10 lines of code need to change (CSV-load → bootstrap compute)

### Techniques Used

Auto-Fill Mode (structured input extraction) + ROUTE_TO_0 failure context synthesis (third reflection)

### Areas for Further Exploration

- Formal methods integration: Can SMT constraints derived from test specifications improve LLM verifier precision beyond P(True) alone? (VerifAI special theme)
- Confidence elicitation comparison: logprob-based P(True) vs. verbalized confidence vs. chain-of-thought verification — which elicitation method yields best-calibrated verifiers?
- Cross-language generalization: Does code verifier calibration hold for Python vs. other languages (relevant to VerifAI low-resource language theme)?
- Self-verification loop: Does iterative LLM self-evaluation with calibration feedback improve generation pass@k over multiple rounds?
- Connection to theorem proving calibration: correlation between code verification calibration and formal proof verification calibration tasks

---

## Next Steps

Proceed to Phase 1 - Targeted Research: `/phase1-targeted`

Research focus for Phase 1:
1. Search for LLM calibration papers specific to code generation/verification (P(True) logprob, ECE on code tasks)
2. Search for self-verification and self-debugging papers that use LLM confidence as acceptance criterion
3. Find EvalPlus-based experiment implementations and leaderboard data
4. Search VerifAI prior work on probabilistic verification and "AI as verifiers" framing
5. Identify papers on difficulty stratification in code generation benchmarks

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
