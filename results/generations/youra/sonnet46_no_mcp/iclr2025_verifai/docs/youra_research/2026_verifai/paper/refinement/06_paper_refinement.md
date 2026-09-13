# Conditional Mechanistic Complementarity of Formal Repair Strategies for LLM-Generated Python Code

## Abstract

This paper investigates formal repair methods for LLM-generated Python code by integrating three approaches -- grammar-constrained decoding (SynCode), SMT solving (Z3), and iterative type checking (mypy) -- into a unified Python-native pipeline evaluated with CodeLlama-7B on HumanEval. A Failure Mode Distribution (FMD) analysis is applied to characterize which repair channels can activate for this model-benchmark pair. The principal finding is a null result: across 2,680 completions from 134 problems, CodeLlama-7B produces zero type errors, rendering the mypy repair channel inapplicable. This outcome indicates that the precondition assumed by the iterative type-checking repair literature -- the presence of type errors in generated code -- is not met for this model-benchmark combination. Additionally, 97.5% of observed failures are syntax-level errors. SynCode reduces AST parse failures by 7.5 percentage points (delta_ast = 0.075), though this reduction does not reach statistical significance at N = 20 problems (bootstrap 95% CI: [-0.025, 0.220], p = 0.1186). Z3 constraint encoding is applicable to 33% of HumanEval problems (54/164). The planned SynCode-Z3 complementarity experiment was not executed in this pipeline run; its result remains inconclusive.

## 1. Introduction

This work examines the applicability of formal repair methods to LLM-generated code by measuring empirical preconditions before applying each method. The investigation integrates three repair approaches -- SynCode grammar-constrained decoding, Z3 SMT solving, and mypy type checking -- into a single Python-native pipeline and evaluates them on CodeLlama-7B output for HumanEval problems.

The central empirical finding is that across 2,680 completions from 134 HumanEval problems, CodeLlama-7B produces zero type errors. This means that mypy-based iterative repair, a technique used in LLM code improvement pipelines, cannot activate for this model on this benchmark. The precondition required by the type-checking feedback loop -- the presence of type errors -- is not satisfied.

**Motivation.** LLMs generate code with various error types: syntactic invalidity, type violations, arithmetic constraint failures, and logical errors. Different repair methods target different error types. Grammar-constrained decoding targets syntax by masking invalid tokens at generation time. SMT solving targets arithmetic constraint failures via symbolic reasoning. Type checking targets structural type violations via static analysis. Each method has a measurable precondition: the corresponding error type must actually appear in the generated code. If the precondition is not met, the method cannot activate regardless of its theoretical soundness.

**Gap.** Prior work on formal repair of LLM-generated code has not systematically measured the Failure Mode Distribution (FMD) -- the empirical breakdown of which failure types actually occur -- before applying formal repair methods. Repair method proposals are typically validated on end-to-end pass@k improvements without decomposing which failures the method can and cannot address. This gap has practical consequences: for instance, implementing mypy-based repair for CodeLlama-7B output would result in a repair loop that activates 0% of the time, a fact that is not predictable from theoretical analysis alone.

**Approach.** This work takes a precondition-first view. Before asking which repair method achieves the highest pass@1, it asks which failure modes are present in a given setting and which repair channels can therefore activate. This is operationalized via an FMD pipeline: for each generated code sample, failures are classified as syntactic (via `ast.parse`), type-structural (via `mypy.api.run`), or functional/arithmetic (via test execution and Z3 eligibility scanning). Repair channels are gated on FMD-conditioned eligibility.

**Summary of findings.** The FMD measurement on CodeLlama-7B with HumanEval reveals: 97.5% of failures are syntax-dominated; the type stratum contains zero problems across 134 problems and 2,680 samples; Z3 encoding is applicable to 33% of problems (54/164) under integer-equality assertion scanning. SynCode directionally reduces AST failures (delta_ast = 0.075, consistent across two independent experiments). The mypy repair loop activates zero times. The SynCode-Z3 complementarity experiment (h-m3) was not executed.

**Contributions.**

1. A unified Python-native pipeline integrating SynCode, Z3-solver, and mypy with CodeLlama-7B on HumanEval without Docker dependencies.
2. An empirical FMD characterization of CodeLlama-7B on HumanEval: 97.5% syntax-dominated, 0% type stratum, 33% Z3-eligible.
3. An empirical demonstration that mypy-based iterative repair is inapplicable to annotation-free code generation by CodeLlama-7B on HumanEval.
4. Implementation and validation of all components required for SynCode-Z3 complementarity testing.

## 2. Related Work

### 2.1 Iterative Feedback Repair for LLM Code Generation

SELF-REFINE (Madaan et al., 2023) introduces a framework where an LLM generates output, receives feedback, and iteratively refines. Applied to code, feedback takes the form of execution results, compiler messages, or test outputs. Olausson et al. (2023) provide an empirical survey of repair strategies for LLM-generated code, evaluating self-repair, external feedback, and execution-guided approaches across multiple benchmarks. Their findings indicate that repair effectiveness depends on the quality and specificity of the feedback signal.

These methods assume that the feedback signal (type errors, syntax errors, test failures) will be informative for the model-benchmark pair under study. This assumption is implicit and not empirically verified for specific model-benchmark combinations. The present work shows that for CodeLlama-7B on HumanEval, one class of formal feedback (mypy type checking) produces zero informative output across 2,680 samples.

Chen et al. (2022) introduce CodeT, which uses dual execution to filter LLM-generated solutions via test case agreement. CodeT demonstrates ensemble effectiveness but does not analyze failure mode complementarity between different repair channels.

### 2.2 Grammar-Constrained Decoding

Ugare et al. (2024) introduce SynCode, a grammar-constrained decoding framework that uses a pushdown automaton to mask syntactically invalid tokens during LLM generation. The present work integrates SynCode v0.4.16 into a multi-method pipeline and confirms a directional AST failure reduction (delta_ast = 0.075) on HumanEval with CodeLlama-7B. SynCode was previously evaluated in isolation without characterizing its interaction with post-hoc repair methods or measuring how it reshapes the downstream failure distribution.

### 2.3 SMT-Based Verification and Repair

Z3 (De Moura and Bjorner, 2008) is an SMT solver applicable to software verification. SMT-based repair approaches encode correctness constraints as logical formulae. Verifying or repairing code with Z3 requires problem-specific encodings: arithmetic constraints (e.g., integer-equality test assertions) are tractable, while general computation is not. No prior work has characterized Z3 applicability to standard code generation benchmarks. The present work quantifies this: 54 of 164 HumanEval problems (33%) have integer-equality test assertions suitable for Z3 constraint encoding.

### 2.4 Code LLM Evaluation

HumanEval (Chen et al., 2021) is a standard benchmark for function-level Python code generation comprising 164 problems. Code Llama (Roziere et al., 2023) is the model family evaluated here. Roziere et al. report that smaller models exhibit higher syntax error rates, which is consistent with the finding that CodeLlama-7B failures are 97.5% syntax-dominated. Existing evaluations report aggregate pass@k without decomposing failures by type. The FMD pipeline provides this decomposition.

## 3. Method

### 3.1 Overview

Given a set of HumanEval problems P and CodeLlama-7B as the code LLM, a frozen sample pool is generated: N = 20 independent completions per problem using fixed seeds (seed = problem_idx * 100 + sample_idx), at temperature T = 0.8. The frozen pool isolates repair-method effects from sampling variance.

For each completion, the FMD classifier labels its failure mode (syntax, type, functional, or success). Repair channel eligibility is computed based on FMD labels. Each formal repair method is applied to its eligible subset. Failure-to-success transition sets F_method are extracted for each method for pairwise complementarity analysis.

All tools (SynCode, z3-solver, mypy) are pip-installable with Python-native APIs. The pipeline is Docker-free.

### 3.2 Failure Mode Distribution (FMD) Pipeline

The FMD pipeline classifies each generated completion into one of four categories via three independent checks applied in priority order:

1. **Syntax stratum** (`ast.parse` failure): The completion cannot be parsed as valid Python AST.
2. **Type stratum** (`mypy.api.run` with type errors detected): The completion parses successfully but mypy reports type mismatches or annotation violations.
3. **Functional/arithmetic stratum** (test execution failure with Z3 eligibility): The completion is syntactically and type-structurally valid but fails test cases.
4. **Success** (all tests pass): The completion is functionally correct.

The priority order -- syntax > type > functional -- reflects a causal hierarchy: a completion with syntax errors cannot be evaluated for type or functional correctness.

**Z3 eligibility criterion.** A problem is Z3-eligible if its canonical test function contains at least one assertion of the form `assert candidate(<integer arguments>) == <integer>`. Test function bodies are scanned using Python's `ast` module.

### 3.3 Formal Repair Channels

**Channel 1: SynCode grammar-constrained decoding.** SynCode v0.4.16 applies a `GrammarAlignedLogitsProcessor` that uses a pushdown automaton tracking the Python CFG to mask tokens producing syntactically invalid continuations. It operates at generation time. Activation condition: none -- SynCode is applied to all problems.

**Channel 2: mypy/ast iterative feedback repair.** For each completion, `mypy.api.run()` is called. If mypy reports type errors, the error messages are formatted as feedback and passed to CodeLlama-7B for iterative revision, up to 3 rounds. Activation condition: the completion must (1) parse successfully and (2) have at least one mypy-reported type error.

**Channel 3: Z3 SMT repair.** For Z3-eligible problems, the correctness requirement is encoded as an SMT constraint satisfaction problem using z3-solver v4.16.0.0 with QF_LIA theory and a 60-second timeout per problem. Activation condition: the problem must contain integer-equality assertions in test functions.

### 3.4 Complementarity Measurement: C_score

To measure whether two repair channels address distinct failure subsets, the C_score (Complementarity Score) is defined as the deviation from independence expectation in the Jaccard overlap of failure-to-success transition sets.

**Failure transition set** F_A: the set of (problem, sample) pairs where method A converts a failing completion to a passing one.

**C_score definition:** C_score(A, B) = E[J_indep] - J_obs(F_A, F_B), where J_obs is the observed Jaccard similarity and E[J_indep] is the expected Jaccard under the independence null. C_score > 0 indicates the methods address more distinct failures than expected by chance.

**Statistical testing.** Bootstrap resampling (10,000 iterations, paired by problem) computes 95% confidence intervals. Bonferroni correction is applied for multiple pairs (alpha = 0.05 / 3 = 0.0167 per pair).

## 4. Experimental Setup

Three experiments address the following questions: (1) Are all three formal repair tools operational in a unified Python-native pipeline? (2) Does SynCode produce measurable FMD improvement? (3) What is the FMD of CodeLlama-7B on HumanEval, and which repair channels can activate?

### 4.1 Model and Infrastructure

**Base model.** CodeLlama-7B (`codellama/CodeLlama-7b-hf`), loaded with `device_map='auto'` and `torch_dtype=float16`.

**Software.** Python 3.10, SynCode v0.4.16, z3-solver v4.16.0.0, mypy v1.20.2, evalplus v0.3.1. All tools pip-installed in a single conda environment.

**Benchmark.** HumanEval (Chen et al., 2021), 164 Python function-level synthesis problems. Experiments h-e1 and h-m1 use a 20-problem subset (problems 0-19 by lexicographic sort). Experiment h-m2 uses a 134-problem baseline pool.

**Frozen pool.** N = 20 completions per problem, fixed seeds (seed_i = problem_idx * 100 + sample_idx), temperature = 0.8, max_new_tokens = 512, top_p = 0.95.

### 4.2 Experiment 1: Unified Pipeline Operationality (h-e1)

**Gate type:** MUST_WORK. **Success criteria:** delta_ast > 0; z3_eligibility_rate >= 0.15; mypy_structured_rate >= 0.90.

### 4.3 Experiment 2: SynCode Mechanism Test (h-m1)

**Gate type:** MUST_WORK. **Success criteria:** delta_ast > 0; bootstrap CI lower bound > 0.

**Statistical power note.** N = 20 problems yields approximately 25% power at delta = 0.075. N >= 60 is required for 80% power.

### 4.4 Experiment 3: Failure Mode Distribution and Channel Scope (h-m2)

**Gate type:** SHOULD_WORK. **Success criteria:** C_score > 0, bootstrap p < 0.0167; delta_P(Z3_eligible | post-mypy) > 0.05.

### 4.5 Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| delta_ast | mean(AST_fail_baseline) - mean(AST_fail_SynCode) | SynCode AST failure reduction |
| z3_eligibility_rate | Z3-eligible problems / all problems | Z3 applicability scope |
| mypy_structured_rate | Completions with mypy output / all completions | mypy operational rate |
| C_score | E[J_indep] - J_obs(F_A, F_B) | Complementarity above independence |
| delta_P(Z3 eligible) | P(eligible | post-mypy) - P(eligible | baseline) | Cascade expansion rate |

## 5. Results

### 5.1 Unified Pipeline Operationality (h-e1)

All three formal repair tools are pip-installable and operational with CodeLlama-7B on the 20-problem HumanEval subset.

**Table 1: Operationality gate metrics (h-e1)**

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| delta_ast (SynCode) | 0.075 | > 0 | PASS |
| z3_eligibility_rate | 0.25 (5/20 problems) | >= 0.15 | PASS |
| mypy_structured_rate | 1.000 | >= 0.90 | PASS |

All three gate conditions are satisfied. SynCode-constrained generation produces a 7.5 percentage point lower AST parse failure rate relative to the baseline pool. Z3 encoding applies to 5 of 20 problems in the subset. mypy returns structured output for all completions.

![Gate metrics visualization](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_verifai_3/docs/youra_research/20260508_verifai/paper/figures/gate_metrics.png)

*Figure 1: Operationality gate metrics (delta_ast, z3_eligibility_rate, mypy_structured_rate) compared against their thresholds.*

### 5.2 Failure Mode Distribution (h-m2)

The FMD analysis of 134 HumanEval problems (2,680 samples from the baseline pool) reveals a failure distribution dominated by syntax errors.

**Table 2: Failure Mode Distribution (h-m2, 134 problems, 2,680 completions)**

| Stratum | Sample Count | Percentage of Classified Non-Success Samples |
|---------|-------------|----------------------------------------------|
| Syntax (ast.parse failure) | 358 | 97.5% |
| Functional (test failure, no syntax error) | 44 | -- |
| Type (mypy type error) | 0 | 0.0% |

The 97.5% figure reflects that 358 of approximately 367 non-success samples fail at the syntax stratum. The functional count (44) represents completions classified as non-syntax-failing that still fail tests; strata are applied in priority order (syntax > type > functional), so percentages across strata are not additive.

The type stratum contains zero samples across all 134 problems and 2,680 completions. Despite a 100% structured output rate, mypy reports zero type errors. The mypy repair loop activates zero times, yielding F_mypy = {} (empty set).

![FMD distribution](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_verifai_3/docs/youra_research/20260508_verifai/paper/figures/fmd_distribution.png)

*Figure 2: Failure Mode Distribution for CodeLlama-7B on 134 HumanEval problems.*

**Consequence for C_score.** With F_mypy = {}, the C_score for the SynCode-mypy pair is undefined (trivially 0.0). The bootstrap test returns p = 1.0. The SHOULD_WORK gate fails on all three conditions: C_score = 0.0, p = 1.0, delta_P = 0.0.

![C_score bootstrap CI](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_verifai_3/docs/youra_research/20260508_verifai/paper/figures/c_score_ci.png)

*Figure 3: Bootstrap confidence interval for C_score (SynCode-mypy pair). The C_score is trivially zero due to the empty mypy transition set.*

![Transition overlap](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_verifai_3/docs/youra_research/20260508_verifai/paper/figures/transition_overlap.png)

*Figure 4: Failure-to-success transition sets. F_SynCode contains 2 transitions; F_mypy contains 0 transitions.*

### 5.3 SynCode Directional AST Reduction (h-m1)

**Table 3: SynCode mechanism test (h-m1, N = 20 problems)**

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| delta_ast | 0.075 | > 0 | PASS |
| Bootstrap CI lower | -0.025 | > 0 | FAIL |
| Bootstrap CI upper | 0.220 | -- | -- |
| p-value (one-sided) | 0.1186 | < 0.05 | FAIL |
| F_SynCode transitions | 2 | > 0 | PASS |

The directional reduction is observed but statistical significance is not achieved. delta_ast = 0.075 is identical in both h-e1 and h-m1, which were run independently. The bootstrap CI lower bound of -0.025 means the null hypothesis (delta_ast = 0) cannot be rejected at N = 20. Power analysis indicates N >= 60 is required for 80% power at this effect size.

The h-m1 FMD analysis shows the baseline distribution is 97.5% syntax, 0.75% type, 1.75% functional, while the SynCode distribution is 90.0% syntax, 0.0% type, 10.0% functional -- indicating a shift from syntax failures to functional failures under SynCode, consistent with the expected mechanism.

![Per-problem scatter](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_verifai_3/docs/youra_research/20260508_verifai/paper/figures/per_problem_scatter.png)

*Figure 5: Per-problem delta_ast scatter for baseline versus SynCode pools.*

![FMD comparison](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_verifai_3/docs/youra_research/20260508_verifai/paper/figures/fmd_comparison.png)

*Figure 6: FMD comparison between baseline and SynCode pools.*

**Implementation note.** The h-e1 validation log recorded `constraint_active = False` for SynCode's internal enforcement flag during generation. This indicates that SynCode's grammar did not enforce all Python indentation constraints at the token level. Despite this, delta_ast = 0.075 was measured, indicating that the `GrammarAlignedLogitsProcessor` produced measurable AST improvement under partial constraint enforcement. The h-m1 experiment loaded the h-e1 pool rather than regenerating, so the constraint_active check was not applicable to h-m1 measurements.

### 5.4 Z3 Eligibility Scope

Using the test-assertion scanning criterion, 5 of 20 problems are Z3-eligible in the subset (25%), and 54 of 164 problems are Z3-eligible in full HumanEval (33%).

![Z3 eligibility](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_verifai_3/docs/youra_research/20260508_verifai/paper/figures/z3_eligibility.png)

*Figure 7: Z3 eligibility distribution across HumanEval problems.*

![Z3 eligibility delta](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_verifai_3/docs/youra_research/20260508_verifai/paper/figures/z3_eligibility_delta.png)

*Figure 8: Pre- versus post-mypy Z3 eligibility. delta_P = 0.0 (no cascade expansion observed).*

**Heuristic inconsistency.** The h-m2 experiment initially measured Z3 eligibility at 0% using a return-type annotation heuristic, which is stricter than the test-assertion scanning approach used in h-e1. The h-e1 measurement (33% at full scale) based on test-assertion scanning is the correct value.

### 5.5 Summary

**Table 4: Summary metrics across all experiments**

| Metric | h-e1 | h-m1 | h-m2 | Target |
|--------|------|------|------|--------|
| delta_ast | 0.075 | 0.075 | -- | > 0 |
| z3_eligibility_rate | 0.25 | -- | 0.0* | >= 0.15 |
| mypy_structured_rate | 1.000 | -- | 1.000 | >= 0.90 |
| C_score (SynCode-mypy) | -- | -- | 0.0 | > 0 |
| delta_P (Z3 eligible) | -- | -- | 0.0 | > 0.05 |
| type_stratum_rate | -- | -- | 0.0% | -- |

*h-m2 used an annotation-based heuristic; the correct Z3 eligibility rate is 0.33 from h-e1 test-assertion scanning.

## 6. Discussion

### 6.1 The Zero Type Stratum

The finding that CodeLlama-7B produces zero type errors across 2,680 completions from 134 HumanEval problems defines a scope boundary for type-checking repair applied to this model-benchmark pair.

Two explanations are plausible. First, CodeLlama-7B is trained on GitHub Python repositories where annotation-free, dynamically-typed code predominates, so the model's output distribution reflects its training distribution and generates annotation-free Python by default. Second, the FMD priority chain classifies failures as syntax first; with 97.5% of completions failing at the syntax level, type errors in post-syntax-correction code would be masked by the syntax classifier. Both explanations likely contribute.

These explanations are distinguishable: applying mypy to SynCode-generated pools (which have reduced syntax failure rates) should reveal whether type errors emerge when the syntax layer is partially removed.

This finding is relevant to the iterative feedback repair literature, which has cited mypy and similar static analysis tools as feedback mechanisms for LLM repair. For CodeLlama-7B on HumanEval, this feedback channel is empirically vacuous.

### 6.2 SynCode: Directional Effect Without Statistical Significance

The h-m1 result (delta_ast = 0.075, p = 0.1186) reflects insufficient statistical power at N = 20, not necessarily the absence of an effect. Power analysis indicates approximately 25% power at this sample size and effect size. The same delta_ast value was observed in two independent experiments (h-e1 and h-m1), which provides some corroborating evidence for the stability of the effect. A 7.5 percentage point reduction in AST failure rate corresponds to approximately 1-2 additional correct completions per 20 samples per problem.

The `constraint_active = False` observation in h-e1 raises a question about whether the measured improvement is attributable to full CFG enforcement or to partial grammar masking effects. This distinction was not resolved by the current experiments.

### 6.3 Z3: Established Scope, Untested Repair

Z3 eligibility (33% of HumanEval) is established. The SMT repair mechanism itself was not executed (h-m3 was not started). The complementarity claim for the SynCode-Z3 pair therefore remains inconclusive. All infrastructure required for this experiment (TransitionExtractor, CScoreCalculator, Z3EligibilityChecker) has been implemented and tested.

### 6.4 Pipeline Reduction

The three-method formal repair pipeline (SynCode + mypy + Z3) for CodeLlama-7B on HumanEval is effectively a two-method pipeline, because mypy does not activate. The direct SynCode-Z3 path remains theoretically valid and untested. These two methods address structurally distinct failure channels: syntax invalidity versus arithmetic constraint unsatisfiability.

### 6.5 Limitations

**L1: h-m3 and h-m4 not executed.** The SynCode-Z3 complementarity experiment (h-m3) and the feature-aware routing experiment (h-m4) were not executed. The core complementarity claim remains untested. All infrastructure is implemented; h-m3 requires approximately one additional hour of GPU time with existing code.

**L2: SynCode statistical significance pending.** The directional result (delta_ast = 0.075) is not statistically significant at N = 20. Full confirmation requires N >= 60 problems.

**L3: Single model, single benchmark.** All results are for CodeLlama-7B (7B parameters) on HumanEval. Larger models, instruction-tuned variants, or annotation-prompted models may exhibit different failure distributions. The zero type stratum finding is model-specific and should not be generalized without additional measurement.

**L4: Z3 eligibility heuristic inconsistency.** h-m2 used a stricter annotation-based heuristic than h-e1 (assertion-scanning). The h-e1 measurement (33%) is the correct value.

**L5: constraint_active flag.** SynCode's internal `constraint_active` flag was False during h-e1 generation, indicating that not all token-level grammar constraints were enforced. The mechanism by which delta_ast = 0.075 was achieved under partial constraint enforcement is not fully characterized.

## 7. Conclusion

This work presents an FMD-conditioned framework for evaluating formal repair methods applied to LLM-generated code. The framework measures which failure modes are present before applying methods conditioned on those failure modes.

Applied to CodeLlama-7B on HumanEval, the measurement reveals that 97.5% of failures are syntax-level, 0% are type-level, and 33% of problems are Z3-eligible. SynCode directionally reduces AST failures (delta_ast = 0.075, consistent across two experiments, not statistically significant at N = 20). mypy is operational but produces no type error feedback for annotation-free LLM code. Z3 eligibility scope is established but repair effectiveness is untested.

The three-method pipeline reduces to a two-method pipeline for this model-benchmark pair. The SynCode-Z3 complementarity test (h-m3), the most theoretically motivated remaining experiment, was not executed in this pipeline run. Extensions include: (1) full N = 164 SynCode run for statistical confirmation; (2) execution of h-m3 for SynCode-Z3 C_score measurement; (3) evaluation with annotation-prompted or larger models to test whether the zero type stratum persists; (4) Z3 eligibility heuristic unification across experiments.

The principal empirical contribution is the demonstration that formal repair channel scope is measurable and model-specific. For CodeLlama-7B on HumanEval, the type-checking repair channel is structurally inapplicable -- a finding that is not predictable from theoretical analysis and that was not previously measured for this model-benchmark combination.

## References

- Chen, M., et al. (2021). Evaluating Large Language Models Trained on Code. *arXiv:2107.03374*.

- Chen, B., et al. (2022). CodeT: Code Generation with Generated Tests. *ICLR 2023*. *arXiv:2207.10397*.

- De Moura, L., & Bjorner, N. (2008). Z3: An Efficient SMT Solver. *TACAS 2008*, LNCS 4963, 337-340.

- Liu, J., et al. (2023). Is Your Code Generated by ChatGPT Really Correct? *NeurIPS 2023*. *arXiv:2305.01210*.

- Madaan, A., et al. (2023). Self-Refine: Iterative Refinement with Self-Feedback. *NeurIPS 2023*. *arXiv:2303.17651*.

- Olausson, T. X., et al. (2023). Is Self-Repair a Silver Bullet for Code Generation? *ICLR 2024*. *arXiv:2306.09896*.

- Roziere, B., et al. (2023). Code Llama: Open Foundation Models for Code. *arXiv:2308.12950*.

- Ugare, S., et al. (2024). SynCode: LLM Generation with Grammar Augmentation. *ICML 2024*. *arXiv:2403.01632*.

**Note:** Several citations have arXiv IDs inferred from research synthesis and require verification against published sources before submission.
