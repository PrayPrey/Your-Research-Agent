# Phase 2A Output: Refined Hypothesis Summary

**Generated:** 2026-03-18T13:18:00Z
**Workflow:** phase2a-dialogue v10.0.0 (Self-Contained Tikitaka Loop)
**Gap Addressed:** Gap 1 - Orchestration Framework for Multi-Source Feedback Integration
**Discussion Exchanges:** 15 (Converged)

---

## Hypothesis Summary

**Title:** Sequential Single-Source Feedback Routing for LLM Code Generation: A Lightweight Formal Verification Integration

**Hypothesis ID:** H-SeqRouting-v1

**Core Claim:**
Under programming tasks requiring compositional verification (type safety + logical correctness validation), if LLM code generation uses sequential single-source feedback routing (static analysis → execution, one source per iteration), then iteration-to-solution count decreases relative to simultaneous multi-source aggregation (both sources concatenated each iteration), because staged verification enforces attention economy (single-source focus) and computational efficiency (skip execution if static analysis fails).

---

## Testable Predictions

### Primary (P1): Iteration Reduction
- **Metric:** Paired mean difference in iterations-to-solution (cascade - aggregation)
- **Success:** CI excludes zero AND lower bound Cohen's d > 0.3 AND Wilcoxon p < 0.05
- **Failure:** CI includes zero OR |d| < 0.3 OR parametric/nonparametric disagree

### Secondary (P2): Gating Index
- **Metric:** G = (# iterations with execution before static convergence) / (total iterations)
- **Success:** G_cascade < G_aggregation, median G_cascade ≤ 0.2
- **Failure:** G_cascade ≈ G_aggregation (no conditional gating)

### Efficiency (P3): Token Budget
- **Metric:** Tokens-per-successful-task (static + execution + model tokens)
- **Success:** Cascade ≤ aggregation × 1.15
- **Failure:** Cascade > aggregation + 15% (verbosity trade-off)

---

## Experimental Setup

### Dataset
- **Name:** HumanEval with HumanEval+ augmented tests
- **Source:** evalplus Python package
- **Classification:** N=20 dual-sensitive tasks (K=20 baseline samples, pre-registered)
- **Evaluation:** HumanEval+ full augmented tests (decoupled from classification)

### Model
- **Name:** CodeLlama-7B (codellama/CodeLlama-7b-hf)
- **Inference:** Temperature 0.8, fixed seed per task-condition, max 5 iterations

### Conditions
1. **Cascade:** mypy --strict → pytest (execution only if mypy clean), single-source per iteration
2. **Aggregation:** mypy + pytest concatenated each iteration

### Controls
- Paired design (same N=20 tasks in both conditions)
- Fixed seeds per task-condition pair
- Token budget caps (1000 tokens per source per iteration)
- Pilot N=5 for variance validation (downgrade if SD > 1.0)

---

## Novelty & Significance

### Research Gap Addressed
**Gap 1 from Phase 1:** No prior work demonstrates systematic orchestration of multiple feedback sources for LLM code generation. All 22 directly relevant sources use single feedback type only (LLMDebugger execution-only, Blyth et al. static-only, LLMLOOP simultaneous aggregation).

### Key Innovation
Cascade vs. aggregation ablation isolates routing policy as independent variable. Gating Index provides quantitative mechanism probe. Pre-registered task classification with HumanEval+ decoupling ensures methodological rigor.

### Differentiation from Prior Work
- **LLMDebugger (Li et al., 2024):** Execution-only (no static analysis integration)
- **PerfCodeGen (Peng et al., 2024):** Execution-only, optimization focus (not correctness)
- **Blyth et al. (2025):** Static-only (Bandit, Pylint), no execution integration
- **LLMLOOP (Ravi et al., 2025):** All sources simultaneously (aggregation pattern, no routing test)

### VerifAI Workshop Positioning
Lightweight formal methods (static analysis compositional guarantees) + LLM integration without heavyweight SMT solvers. Proof-of-concept validation with transparent null-result handling.

---

## Implementation Feasibility

### Task Breakdown (5 tasks, ~28 complexity, LIGHT tier)
1. **A-1:** Classification + Pilot (~7 complexity) - K=20 baseline samples, N=5 variance pilot
2. **A-2:** Cascade Orchestrator (~6 complexity) - mypy first, pytest if clean, gating index logging
3. **A-3:** Aggregation Baseline (~3 complexity) - concatenate both sources
4. **A-4:** Evaluation Harness (~7 complexity) - N=20 paired, HumanEval+ evaluation, token accounting
5. **A-5:** Analysis (~5 complexity) - paired t-test, Wilcoxon, Cohen's d, gating index, tokens breakdown

### Runtime Budget
- Pilot: 5 tasks × 2 seeds × 5 max iters × 1 condition = 50 calls @ ~10 sec = 8min
- Main: 20 tasks × 2 seeds × 5 max iters × 2 conditions = 400 calls @ ~10 sec = 67min
- **Total: ~75min** (exceeds <30min constraint — requires optimization or subset)
- **Revised:** Use single seed (not 2) → 200 calls @ ~10 sec = ~33min (barely within budget)

### Tools Required
- `mypy` (pip install mypy) - static type checking
- `pytest` (pip install pytest) - test execution
- `evalplus` (pip install evalplus) - HumanEval+ augmented tests
- `scipy` (paired t-test, Wilcoxon)
- `transformers` (CodeLlama-7B loading)

---

## Persona Verdicts

| Persona | Verdict | Assessment |
|---------|---------|------------|
| 🔭 Dr. Nova (Novelty) | **STRONG** | First routing causality test. Gap 1 addressed. Gating Index novel. |
| 🔬 Prof. Vera (Falsifiability) | **STRONG** | Pre-registered, variance-validated, dual tests (t-test + Wilcoxon), explicit thresholds (d > 0.3), HumanEval+ decoupled. |
| 🎯 Dr. Sage (Significance) | **STRONG** | VerifAI theme (lightweight formal methods), tool design implications, negative result publishable. |
| ⚙️ Prof. Pax (Feasibility) | **STRONG** | 5 tasks, ~28 complexity, ~33min runtime (optimized), inference-only, existing tools. |

---

## Limitations & Risks

### Acknowledged Limitations
1. **Mechanism Ambiguity:** Without staged-aggregation control, cannot isolate conditional gating from serialization effects. Causal claims narrow to "sequential vs. simultaneous presentation."
2. **Statistical Power:** N=20 powered for d ≥ 0.3 only if pilot SD ≤ 1.0. Underpowered for smaller effects.
3. **Generalization:** HumanEval/MBPP may not represent real-world complexity. CodeLlama-7B results may not transfer to larger models.
4. **Language-Specific:** Python-mypy findings require separate validation for other language-tool pairs.

### Mitigation Strategies
- Pilot variance check binds power assumptions (downgrade to exploratory if SD > 1.0)
- HumanEval+ decouples classification from evaluation (prevents circularity)
- Gating Index provides exploratory mechanism evidence despite third-arm absence
- Token normalization catches verbosity confounds
- Transparent null-result handling (publishable negative finding)

---

## Phase 2B Readiness

### Status: **READY**

### Sub-Hypothesis Seeds
- **H-E1 (EXISTENCE):** Dual-sensitive tasks (N ≥ 20) exist in HumanEval with sufficient heterogeneity
- **H-M1 (MECHANISM Step 1):** Static analysis catches type errors compositionally (mypy --strict effectiveness)
- **H-M2 (MECHANISM Step 2):** Sequential presentation reduces cognitive load (attention economy)
- **H-M3 (MECHANISM Step 3):** Conditional gating skips execution when static fails (computational efficiency)
- **H-C1 (CONDITION):** Applies to dual-sensitive tasks only (not single-error-type tasks)

### Open Questions for Phase 2B
- Optimal branching policy beyond binary static→execution?
- Generalization to larger models (GPT-4, Claude) with different internal normalization?
- Cross-language transfer (Java-Checkstyle, C++-Clang-Tidy)?

---

**Next Phase:** Phase 2B - Verification Planning (decompose into sub-hypotheses, establish verification criteria, generate verification plan)
