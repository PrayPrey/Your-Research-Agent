# Experimental Setup

We design three experiments to answer the following questions: (1) Are all three formal repair tools operational in a unified Python-native pipeline? (2) Does SynCode's grammar-constrained decoding produce measurable FMD improvement? (3) What is the failure mode distribution of CodeLlama-7B on HumanEval, and which formal repair channels can activate?

## Model and Infrastructure

**Base model.** We use CodeLlama-7B (`codellama/CodeLlama-7b-hf`) from HuggingFace, loaded with `device_map='auto'` and `torch_dtype=float16`. CodeLlama-7B is a code-specialized language model trained on 500B code-heavy tokens. We select it as a standard code generation baseline with documented behavior on HumanEval.

**Python-native infrastructure.** All formal repair tools are pip-installed in a single conda environment (`python 3.10`): SynCode v0.4.16 (grammar-constrained decoding), z3-solver v4.16.0.0 (SMT solving), mypy v1.20.2 (type checking), evalplus v0.3.1 (benchmark evaluation). No Docker dependency. Tool installation and operationality are verified before experiments.

**Compute.** Experiments run on CUDA-capable GPU (CUDA_VISIBLE_DEVICES=4). CPU fallback is available and confirmed functional for inference. Total GPU time across all experiments: approximately 20 minutes for the 20-problem subset; ~4h estimated for full N=164 SynCode run (not executed in this report).

## Benchmark

We evaluate on HumanEval [Chen et al., 2021], comprising 164 Python function-level code generation problems. Each problem provides a natural language docstring, a function signature, and a handwritten test suite. EvalPlus [Liu et al., 2023] extends HumanEval with augmented tests; we use the HumanEval subset throughout.

For h-e1 and h-m1, we use a 20-problem subset (lexicographic sort, problems HumanEval/0 through HumanEval/19) to reduce generation time while preserving the experimental protocol. For h-m2 (FMD analysis), we use the full 134-problem baseline pool (30 problems excluded for infrastructure reasons during baseline generation).

## Experimental Protocol: Frozen Sample Pool

For each problem, we generate N=20 independent completions using a fixed seed scheme: `seed_i = problem_idx × 100 + sample_idx`. This seed scheme ensures identical samples are used across all repair methods and experiments, enabling direct comparison of failure-to-success transitions without sampling variance confounds.

Generation parameters: temperature=0.8, max_new_tokens=512, top_p=0.95, do_sample=True. We use nucleus sampling to ensure output diversity within the frozen pool.

## Experiment 1: Unified Pipeline Operationality (h-e1)

**Question:** Are SynCode, Z3-solver, and mypy all pip-installable and operational with CodeLlama-7B on HumanEval?

**Design.** For a 20-problem subset: (a) generate baseline pool (N=20 samples per problem); (b) generate SynCode-constrained pool (same 20 problems); (c) measure AST failure rate in both pools and compute delta_ast; (d) scan test functions for Z3 eligibility; (e) run mypy.api.run() on all baseline completions and measure structured output rate.

**Success criteria (MUST_WORK gate):**
- delta_ast > 0 (SynCode reduces AST failures)
- z3_eligibility_rate ≥ 0.15 (Z3 applicable to ≥15% of problems)
- mypy_structured_rate ≥ 0.90 (mypy returns structured output for ≥90% of completions)

**Baselines.** Baseline (unconstrained CodeLlama-7B generation) is the reference condition for delta_ast computation. No external baseline model is required — the operationality check compares the tool's output against defined thresholds.

## Experiment 2: SynCode Mechanism Test (h-m1)

**Question:** Does SynCode's CFG masking produce a statistically significant reduction in AST parse failures?

**Design.** Reusing the h-e1 20-problem pool: (a) compute per-problem AST failure rates for baseline and SynCode pools; (b) compute delta_ast = mean(ast_failure_rate_baseline) - mean(ast_failure_rate_syncode); (c) compute bootstrap 95% CI using 10,000 iterations with problem-level pairing; (d) extract F_SynCode→✓ (the set of problem-sample pairs where baseline fails and SynCode succeeds); (e) classify FMD for both pools.

**Success criteria (MUST_WORK gate):**
- delta_ast > 0
- Bootstrap CI lower bound > 0 (statistical significance at α=0.05)

**Statistical power note.** We use N=20 problems (h-e1 pool reuse). Power analysis: at delta=0.075 and N=20, estimated power is ~25%. N≥60 is required for 80% power. We report this as a known limitation — the directional result is informative even if statistical significance cannot be declared at N=20.

## Experiment 3: Failure Mode Distribution and Channel Scope (h-m2)

**Question:** What is CodeLlama-7B's failure mode distribution on HumanEval, and which repair channels can activate?

**Design.** On the full 134-problem baseline pool (N=20 samples per problem, 2,680 completions total): (a) classify each completion into FMD strata (syntax / type / functional / success); (b) apply mypy.api.run() to all completions and measure type error prevalence; (c) apply mypy repair loop (max 3 rounds) to type-stratum problems; (d) measure Z3 eligibility for all problems using both annotation-based and assertion-scanning heuristics; (e) compute C_score for SynCode-mypy pair using F_SynCode→✓ (from h-m1) and F_mypy→✓; (f) compute ΔP(Z3_eligible | post-mypy) vs. baseline.

**Success criteria (SHOULD_WORK gate):**
- C_score > 0, bootstrap p < 0.0167 (Bonferroni-corrected for 3 pairs)
- ΔP(Z3_eligible | post-mypy) > 0.05

**FMD classification priority.** Syntax errors are classified first; type errors only in syntactically-valid completions; functional/arithmetic failures in both syntactically- and type-valid completions. Success is confirmed by test execution via evalplus.

## Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| delta_ast | mean(AST_fail_baseline) - mean(AST_fail_SynCode) | SynCode AST reduction |
| z3_eligibility_rate | |{problems with integer-equality assertions}| / |all problems| | Z3 applicability scope |
| mypy_structured_rate | |{completions with mypy output}| / |all completions| | mypy operational rate |
| C_score | E[J_indep] - J_obs(F_A→✓, F_B→✓) | Complementarity above independence |
| ΔP(Z3 eligible) | P(eligible | post-mypy) - P(eligible | baseline) | Cascade expansion rate |

All bootstrap confidence intervals use 10,000 resampling iterations. Multiple comparison correction (Bonferroni) is applied for C_score comparisons across method pairs (α=0.05/3=0.0167).
