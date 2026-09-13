# Methodology

## Overview

Building on our observation that feedback routing policy—how we present verification signals to LLMs—represents an unexplored design dimension, we designed an experimental framework to test whether cascade routing (static analysis → execution with conditional gating) provides efficiency advantages over naive aggregation (both sources concatenated simultaneously). Our approach centers on three key design decisions: within-task paired comparison using dual-sensitive classification, conditional execution gating to operationalize computational layering, and CodeLlama-7B base model to stress-test feedback routing without confounding with instruction-following capabilities.

## Cascade Routing: Operationalizing Computational Layering

Cascade routing implements a simple principle: use fast, cheap checks before expensive checks, escalating to costly verification only when necessary. Concretely, on each iteration, we first run mypy --strict static analysis (<0.1 seconds), providing structured feedback on type errors, null safety violations, and signature mismatches. Only if mypy reports zero errors do we proceed to pytest execution (5-10 seconds per task), which validates logical correctness against HumanEval+ augmented tests.

**Rationale:** This design mirrors compiler architecture—lexical analysis before parsing before semantic analysis—where each stage filters inputs before passing to the next expensive layer. Static analysis provides compositional type safety guarantees without execution overhead, making it a natural first-pass filter. If static errors exist, test execution would waste computational resources testing code that cannot be type-safe.

The conditional gating mechanism operationalizes our computational efficiency hypothesis: by skipping execution when static errors exist, cascade routing should achieve token efficiency through reduced feedback verbosity (no redundant pytest output when mypy already identifies issues) and reduced iteration count (focused error correction without information overload).

**Alternative Considered:** We considered staged-aggregation (run both sources but present sequentially), which would isolate serialization from gating. However, this adds implementation complexity and conflates cognitive effects with computational effects. Cascade routing's clear gating policy—execution only if static-clean—provides the strongest test of computational layering.

## Dual-Sensitive Task Classification: Controlling for Task Difficulty

A critical methodological challenge in testing feedback routing causality is task selection bias. If cascade and aggregation conditions use different task sets, observed efficiency differences could stem from inherent task difficulty rather than routing policy. We address this through dual-sensitive task classification, which identifies tasks suitable for within-task paired comparison.

**Classification Algorithm:** For each HumanEval task, we generate K=20 baseline samples using CodeLlama-7B (temperature=0.8, fixed seed). Each sample undergoes mypy --strict verification and pytest testing with visible HumanEval tests. A task qualifies as dual-sensitive if:
1. At least one sample fails mypy but passes pytest (type error present, logic correct)
2. At least one sample fails pytest but passes mypy (logic error present, types correct)
3. Within-task variance SD ≤ 1.0 (adequate statistical power for paired comparison)

**Rationale:** Dual-sensitive tasks exhibit error distributions where both static and dynamic verification provide complementary signals—neither source is universally sufficient. This ensures that routing policy genuinely matters: on mypy-only tasks, cascade and aggregation would converge (both rely on static feedback), while on pytest-only tasks, cascade must escalate to execution anyway (static analysis provides no value). Dual-sensitive tasks isolate routing policy effects.

The within-task variance constraint (SD ≤ 1.0) ensures adequate statistical power for detecting medium effects (Cohen's d ≥ 0.3) with N=20 paired samples. This threshold derives from prior work (PerfCodeGen reports σ ≈ 1.0 for execution feedback iterations) and balances statistical rigor with task pool size.

**Alternative Considered:** Between-task comparison (cascade on one task set, aggregation on another) would be simpler but confounds routing with task selection. Our within-task design uses each task as its own baseline, isolating routing as the causal variable.

## Experimental Design: Paired Comparison with Explicit Ablation

Our experimental protocol tests cascade versus aggregation on N=35 dual-sensitive tasks identified through classification. For each task-condition pair, we measure iterations-to-solution (primary metric), Gating Index (mechanism probe), and tokens-per-successful-task (efficiency check).

**CASCADE Condition:** Each iteration presents single-source feedback:
- Iteration 1: Run mypy → Present mypy feedback only
- If mypy clean → Run pytest → Present pytest feedback only
- If mypy errors → Skip pytest, present mypy errors only
- Repeat until solution passes both mypy --strict AND HumanEval+ full tests

**AGGREGATION Condition (Baseline):** Each iteration presents multi-source feedback:
- Run mypy + pytest simultaneously
- Concatenate both outputs: "[MYPY ERRORS]\n\n[PYTEST ERRORS]"
- Present combined feedback to LLM
- Repeat until solution passes both verifiers

**Token Budget Equality:** Critical fairness constraint. Each feedback source capped at 1000 tokens per iteration, truncated if necessary. This prevents verbosity asymmetry where one condition uses 2× tokens simply due to longer error messages. Both conditions face identical token constraints, ensuring efficiency comparisons are not confounded by information quantity.

**Success Criterion:** A solution succeeds when it passes mypy --strict (zero type errors) AND HumanEval+ full augmented tests (80+ robustness tests beyond visible classification tests). This decoupling ensures classification and evaluation use independent test sets, preventing overfitting to visible tests used during dual-sensitive classification.

**Rationale:** The aggregation baseline represents the naive multi-source integration approach—"give the LLM all available feedback and let it figure out priorities." Cascade routing tests whether explicit orchestration (static before execution, conditional gating) improves over this naive strategy. If cascade provides no advantage, it would suggest LLMs internally normalize feedback regardless of presentation order, making external routing policy irrelevant.

## Model Selection: CodeLlama-7B Base

We use CodeLlama-7B base model (not instruction-tuned) with temperature=0.8, top-p=0.95, max 5 iterations per task.

**Rationale:** Base models test feedback routing policy itself, not instruction-following capabilities. Instruction-tuned models may have been aligned to ignore redundant feedback or implicitly prioritize error types, confounding routing policy effects with training artifacts. Base CodeLlama-7B provides a neutral testbed for feedback orchestration without such confounds.

Additionally, base models are more likely to generate code with type annotation issues, stressing the static analysis layer. This aligns with our hypothesis: cascade routing should provide largest advantages on tasks where static analysis frequently catches errors early. Using a model with weak type annotation capabilities maximizes the potential for detecting cascade routing benefits.

**Model Size Justification:** 7B parameters fit within reasonable inference budget (<30 minutes for 35 tasks × 20 samples × 2 conditions = 1,400 completions) while providing sufficient code generation capability for HumanEval. Larger models (34B+) may internally normalize feedback more effectively, potentially masking routing policy effects—a question we defer to future work.

## Mechanism Probes: Gating Index and Token Breakdown

Beyond primary metrics (iterations-to-solution), we include mechanism probes to test specific causal steps in our computational efficiency hypothesis.

**Gating Index G:** Measures proportion of iterations where execution feedback appears before static convergence. Formally, G = (# iterations with pytest feedback before first mypy-clean iteration) / (total iterations). Range [0, 1].
- **Prediction:** G_cascade < G_aggregation (ideally G_cascade ≈ 0)
- **Interpretation:** If G_cascade ≈ 0, conditional gating operates as designed—execution skipped until static clean. If G_cascade ≈ G_aggregation, gating mechanism fails, and efficiency gains (if observed) must stem from serialization alone.

**Token Breakdown:** Granular accounting separates static-analysis tokens, execution-feedback tokens, and model-response tokens for each task-condition pair.
- **Prediction:** Tokens_cascade ≤ Tokens_aggregation × 1.15
- **Interpretation:** If cascade increases tokens by >15%, iteration reduction is offset by verbosity overhead. Efficiency claim fails. Breakdown reveals whether savings come from skipped execution (zero pytest tokens) or from reduced model verbosity (shorter responses to focused feedback).

## Implementation Details

**Static Analysis:** mypy version 1.0+, --strict mode (enables all optional checks: no-implicit-optional, warn-return-any, warn-unused-ignores, disallow-any-generics, etc.), --show-error-codes for structured output.

**Execution Testing:** pytest with HumanEval+ augmented tests (evalplus package), 120-second timeout per task, --tb=short for concise tracebacks.

**Concurrent Execution:** Both verifiers run in sandboxed subprocesses with timeout enforcement to prevent hanging on infinite loops or resource exhaustion.

**Reproducibility:** Fixed seed per task-condition pair (seed = task_id hash + condition_id), ensuring deterministic generation for paired comparison. All code, configurations, and data preprocessing scripts available in supplementary materials.

## Dataset: HumanEval with HumanEval+ Augmentation

We use HumanEval (164 hand-written Python programming problems) with HumanEval+ augmented tests. HumanEval provides function signatures and docstrings as prompts; HumanEval+ adds 80+ robustness tests per task beyond the original ~8 visible tests.

**Rationale:** HumanEval is the standard benchmark for LLM code generation, enabling comparison with prior work (PerfCodeGen, LiveCodeBench, TiCoder). HumanEval+ augmentation provides classification-evaluation decoupling: we use visible tests for dual-sensitive classification (K=20 baseline samples), then evaluate on full augmented tests (independent test set). This prevents overfitting and ensures dual-sensitive classification reflects genuine dual-signal requirements, not visible-test brittleness.

**Task Pool:** Dual-sensitive classification identified N=35 qualifying tasks (21.3% of HumanEval) with mean within-task SD=0.71, satisfying our N≥20 target and SD≤1.0 power assumption. These 35 tasks span algorithm categories (sorting, search, string manipulation, data structures) representative of HumanEval diversity.

## Statistical Analysis

Primary analysis uses paired t-test (parametric) with Wilcoxon signed-rank test (nonparametric robustness check) on iterations-to-solution differences. Pre-registered interpretation:
- CI excludes zero AND Cohen's d > 0.3 → Meaningful effect
- d ∈ [0.2, 0.3) → Small effect, interpret cautiously
- CI includes zero OR |d| < 0.2 → No evidence

Gating Index and token efficiency use descriptive comparison with visual inspection. Qualitative transcript analysis examines error correction strategies for 5 representative tasks to explore attention economy hypothesis (mechanism Step 2) exploratorily, given H-M2 implementation challenges prevented full quantitative testing.
