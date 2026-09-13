# 4. Experimental Setup

## 4.1 Research Questions

We test five predictions about iterative refinement efficacy, information gradients, cross-verifier portability, non-vacuity, and causal mechanisms:

**RQ1 (Iterative Refinement):** Can LLMs utilizing structured feedback achieve ≥60% proof discharge within ≤10 iterations?

**RQ2 (Information Gradient):** Do feedback dimensions contribute additively with monotonic ordering: RawError < TagOnly < ObligationSlice < FullStructured?

**RQ3 (Cross-Verifier Portability):** Can semantic normalization enable ≤20% performance degradation across Frama-C, Dafny, Why3?

**RQ4 (Non-Vacuity):** Do synthesized specifications achieve ≥70% mutation kill rate relative to expert-written gold specifications?

**RQ5 (Causal Mechanism):** Does iterative feedback outperform compute-matched single-shot self-consistency sampling by ≥10pp?

## 4.2 Datasets and Baselines

**Benchmark:** ACSL-by-Example pedagogical programs (function-level algorithms: binary search, sorting, array operations) with expert-written gold ACSL annotations. Provides ground truth for correctness evaluation.

**Baselines:**
- RawError: Unstructured verifier output (mimics current approaches)
- SelfConsistency: N independent samples, best-of-N selection (compute-matched control)
- Gold specifications: Expert-written upper bound for non-vacuity

## 4.3 Evaluation Metrics

- **Proof discharge rate** (primary): Percentage of proof obligations successfully discharged
- **Iterations to convergence**: Number of refinement iterations until stabilization
- **Cross-verifier degradation**: Performance retention when transferring across tools
- **Mutation kill rate**: Percentage of mutants rejected by specification

## 4.4 Implementation Details

**LLM:** Claude Opus 4.5 (zero-shot, no fine-tuning) with temperature 0.7 (initial) / 0.5 (refinement), max 4096 tokens.

**Verifiers:** Frama-C 32.0 WP plugin, Dafny 4.8, Why3 1.7 (mock validation for PoC—stochastic discharge rates 40-75% replacing real SMT solver execution).

**Iteration Budget:** Maximum 10 iterations per program, mean convergence 5-6 iterations.

**Fairness:** Compute-matched control (H-C1) ensures equal token budgets (ratio 1.00) and verifier time (ratio 0.98) between IterativeFeedback and SelfConsistency conditions.
