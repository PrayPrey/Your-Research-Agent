# Phase 2B Context: H-E1 (Alignment Method Clustering Existence)

**Generated:** 2026-03-18
**Hypothesis Type:** EXISTENCE
**Gate:** MUST_WORK
**Prerequisites:** None

---

## Hypothesis Statement

Under code generation evaluation conditions (Python function-level tasks, HumanEval+/MBPP+/BigCodeBench benchmarks), if we measure 6-8 post-alignment models across correctness, complexity, and efficiency dimensions, then models will cluster in 3D performance space according to alignment method type (execution-based, preference-based, unaligned baseline) with statistically significant intercluster distance > 1.5σ (Cohen's d), because feedback signals during alignment shape output distributions toward implicit optimization objectives.

## Rationale

This tests the foundational claim that alignment methods produce detectable "objective function signatures". If clustering exists, it validates that feedback signals create systematic biases in output distributions. This is the existence proof needed before testing mechanism.

## Variables

**Independent:** Alignment Method Type (execution-based, preference-based, baseline)
**Dependent:** Intercluster Distance (Cohen's d in 3D space)
**Controlled:** Programming Language (Python only), Task Distribution (HumanEval+ 164 tasks)

## Verification Protocol

1. Select 6-8 models (2-3 execution-focused, 2-3 preference-focused, 1-2 baselines) from HuggingFace
2. Generate 60-80 code samples per model on HumanEval+ tasks (temperature 0.8)
3. Measure three dimensions: correctness (pass@k via test execution), complexity (cyclomatic via radon, AST depth via lizard), efficiency (runtime via cProfile, memory via memory_profiler)
4. Apply PCA on signature vectors, run k-means clustering (k=3)
5. Compute Cohen's d effect size (intercluster distance / intracluster SD)

## Success Criteria

**Primary:** Cohen's d > 1.5σ (moderate success) or > 2.5σ (strong success)
**Secondary:** Alignment method clustering stronger than language confounds

## Failure Response

- **IF** Cohen's d < 1.5σ: ABANDON - no detectable signatures exist
- **IF** language confounds dominate: PIVOT - add cross-language controls

## Experimental Setup (from Phase 2A)

### Dataset
- **Name:** HumanEval+ (standard benchmark)
- **Source:** EvalPlus (https://github.com/evalplus/evalplus)
- **Size:** 164 function-level Python programming tasks with extended test suites
- **Justification:** Provides controlled pass@k measurement with reduced test case variance. Task distribution suitable for clustering analysis (60-80 samples per model).

### Model Selection
**Criteria:**
- **Execution-focused (2-3 models):** SelfCodeAlign-7B, StepCoder, CodeLlama-Python-7B-Instruct
- **Preference-focused (2-3 models):** Models trained with DPO/RLAIF (if publicly available)
- **Baselines (1-2 models):** CodeLlama-7B-Base, StarCoder-Base

All models share Python language, varying alignment methods. Llama-3-8B family preferred for base model consistency when available.

**Source:** HuggingFace Model Hub

## Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| SelfCodeAlign (Wei et al., 2024) | 67.1% pass@1 on HumanEval+, 55 citations | HumanEval+, MBPP+ |
| PrefGen (Peng et al., 2025) | Balanced Pass@k + Gas@k + Secure@k for smart contracts, 3 citations | Smart contract benchmarks (Solidity) |
| NaturalCodeBench (Zhang et al., 2024) | Shows 80% HumanEval → 20% real-world task mismatch, 22 citations | Real-world Python tasks |

## Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Proxy validity: Code complexity metrics (cyclomatic complexity, AST depth) and efficiency metrics (runtime, memory) correlate sufficiently with 'code quality' to serve as objective dimensions | Complexity metrics established in software engineering for human code (Halstead, McCabe). Efficiency metrics directly measurable. Exchange 5 - Dr. Ally proposes objective proxies instead of subjective rubrics | Quality dimension collapses to noise, clustering may only reflect correctness vs efficiency (2D not 3D). Mitigation: Validate proxies on small human-annotated sample (50-100 samples) |
| A2 | Feedback signal theory: Models learn to optimize whatever their training feedback measures, creating persistent biases in output distributions | Implicit bias theory in ML optimization (SGD, Adam have inductive biases). Exchange 9 - Dr. Sage mechanistic link: feedback signals define objectives. SelfCodeAlign/PrefGen demonstrate feedback-dependent outcomes | Clustering could be due to base model differences or data confounds rather than alignment method. Causal claims weakened to correlational. Mitigation: Between-method variance >> within-model variance comparison |
| A3 | Public benchmark data provides sufficient signal: Leaderboard scores + targeted model inference (60-80 samples per model) capture alignment method signatures without access to full training data | Phase 1 estimates 64-85 GPU hours feasible. Exchange 10 - Prof. Pax validates resource requirements. Literature shows pass@k differences detectable with N=50-100 samples (HumanEval+ papers) | Insufficient statistical power, clustering not detectable. Mitigation: Phase 1 (leaderboard analysis) verifies benchmark overlap before GPU commitment |
| A4 | Within-language controls eliminate confounds: Restricting to Python-only models removes language-specific complexity patterns that could dominate alignment method effects | Exchange 12 - Prof. Rex requires within-language comparison. PrefGen (Solidity) vs StepCoder (Python) language difference could confound clustering | Language patterns dominate alignment signals, clusters reflect Python vs Solidity not execution vs preference. Mitigation: Require 3+ Python models per alignment method group |

## Dependencies

**Prerequisites:** None (foundation hypothesis)
**Blocked By:** None
**Blocks:** H-M-integrated (mechanism validation)

---

*Auto-generated from 02b_verification_plan.md | Phase 2B Planning*
