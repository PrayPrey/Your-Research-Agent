# 3. Methodology

Our methodology is designed around a single core principle: let each model reveal its own calibration fingerprint without external difficulty labels. This self-contained approach requires a four-step pipeline: generate solutions, stratify by difficulty, extract confidence, and compute calibration error. Each step design decision follows from this principle.

## 3.1 Self-Contained Difficulty Stratification

**What and why.** We define problem difficulty self-containedly from each model's own solution performance, rather than using external annotations or human performance baselines. For each problem, we generate k=5 solutions and compute pass@1 (the fraction of solutions that pass all EvalPlus tests). Difficulty tier assignment follows:

- **Hard tier:** pass@1 = 0.0 (0/5 solutions correct)
- **Easy tier:** pass@1 ≥ 0.6 (3–5/5 solutions correct)
- **Medium tier:** pass@1 ∈ {0.2, 0.4} (excluded from tier analysis)

**Rationale.** External difficulty labels confound model-specific difficulty with benchmark-level difficulty. By using each model's own pass@1 distribution, we ensure that "hard" means "hard for this model specifically" — enabling us to measure whether the model's confidence degrades exactly when it struggles. The k=5 design provides six discrete pass@1 values {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}, which is coarse (a pilot methodology) but sufficient for directional ΔECE analysis, as our M-sensitivity experiments confirm.

**Tier validation.** We require n≥20 problems per tier per model-benchmark pair for reliable M=15-bin ECE computation (hypothesis h-e1). This threshold ensures that each ECE bin has adequate support. We also validate cross-architecture difficulty consistency using Jaccard similarity of hard-tier assignments across model pairs (hypothesis h-m2).

## 3.2 P(True) Logprob Confidence Extraction

**What and why.** For each (problem, solution) pair, we extract P(True) as the normalized logprob of "True" when the model is asked to evaluate its own solution:

```
prompt = problem_statement + "\n\n" + solution + "\n\nIs the above solution correct? (True/False)"
P(True) = softmax(logprob("True"), logprob("False"))
         = exp(logprob("True")) / (exp(logprob("True")) + exp(logprob("False")))
```

The normalized confidence score c = P(True) ∈ [0, 1] is used as the model's confidence that its solution is correct.

**Rationale.** P(True) provides a direct confidence signal from the model's own logprob distribution [Kadavath et al., 2022], avoiding artifacts from verbalized confidence ("I am 80% confident") and from sampling-based uncertainty estimates. The zero-shot formulation (no few-shot examples) ensures that the confidence signal reflects pre-training calibration, not in-context calibration from demonstrations.

**Validity requirement.** We require that c is non-degenerate (std(c) > 0.05 per model) to ensure the confidence signal provides genuine discriminative information (hypothesis h-m3). A constant or near-constant c would make ECE computation meaningless.

## 3.3 Expected Calibration Error Computation

**What and why.** We compute ECE separately for the hard-tier and easy-tier problems per model:

```
ECE(tier) = Σ_{m=1}^{M} (|B_m| / n_tier) × |acc(B_m) − conf(B_m)|
```

where B_m is the m-th confidence bin, acc(B_m) is the fraction of correct solutions in bin m, conf(B_m) is the mean confidence in bin m, and n_tier is the total number of (problem, solution) pairs in the tier.

**Key metric.** Our primary outcome is:

```
ΔECE = ECE(hard) − ECE(easy)
```

A positive ΔECE indicates that hard-tier problems have worse calibration than easy-tier problems (the expected pattern). A negative ΔECE indicates the opposite.

**Parameters.** We use M=15 equal-width bins [0, 1/15), [1/15, 2/15), ..., [14/15, 1] following Guo et al. [2017]. Bootstrap confidence intervals (n=1,000 samples, seed=42) quantify uncertainty in ΔECE. We verify M-sensitivity by recomputing ΔECE for M ∈ {10, 15, 20} and confirming directional stability.

**Null baseline.** To confirm that ΔECE observations reflect genuine calibration differences and not base-rate artifacts, we compare observed ΔECE against a Monte Carlo Bernoulli null model (n_sim=100,000 simulations) where confidence is drawn from the model's empirical c distribution but assigned independently of correctness.

**Temperature scaling.** We fit a global temperature parameter T* on a 20% holdout of (confidence, correctness) pairs using negative log-likelihood minimization, then recompute ΔECE on the remaining 80% with scaled confidence c/T*. This tests whether architecture-dependent ΔECE survives standard post-hoc calibration [Guo et al., 2017].

## 3.4 Models and Benchmarks

**Models.** We evaluate three models representing distinct training regimes:

| Model | Parameters | Training Regime | Architecture Category |
|-------|-----------|----------------|----------------------|
| NousResearch/Meta-Llama-3-8B | 8B | General-purpose pre-training | General |
| codellama/CodeLlama-7b-hf | 7B | Llama base + code fine-tuning | Code-adapted |
| deepseek-ai/deepseek-coder-6.7b-base | 6.7B | Code-specialized pre-training | Code-specialized |

**Rationale.** The three models are selected to represent qualitatively distinct training data compositions: general-purpose pre-training, code fine-tuning on a general base model, and code-specialized pre-training from scratch. This allows us to test whether architecture category — not just parameter count — determines calibration direction. All models are in the 7–8B parameter range to control for scale effects.

**Benchmarks.** We use EvalPlus [Liu et al., 2023] comprising HumanEval+ (164 problems) and MBPP+ (378 problems), totaling 542 problems. EvalPlus augments the original benchmarks with substantially more test cases, reducing false positive pass rates. We analyze both benchmarks independently and combined to verify consistency.

## 3.5 Tier Consistency Validation

Before interpreting ΔECE differences across architectures, we validate that hard/easy tier assignments are sufficiently consistent across models using Jaccard similarity:

```
J(tier_model_a, tier_model_b) = |hard_a ∩ hard_b| / |hard_a ∪ hard_b|
```

A Jaccard of 1.0 would mean all models agree on which problems are hard; 0.0 would mean complete disagreement. We use J > 0.30 as our acceptance threshold (hypothesis h-m2, SHOULD_WORK gate): if hard tiers are completely idiosyncratic, cross-architecture ΔECE comparisons lose interpretive value.

Figure 4 shows the Jaccard analysis results, which reveal a 45–55% overlap: difficulty is substantially (but not completely) architecture-consistent. The 133/542 (24.5%) problems universally hard for all three models form an architecture-independent difficulty core, confirming that problem-level structural difficulty exists independently of architecture.

## 3.6 Full Pipeline Summary

```
Step 1: Generate k=5 solutions per problem (EvalPlus oracle → pass@1)
         → Hypothesis h-e1: verify n≥20 per tier per model-benchmark pair
         → Hypothesis h-m1: verify coverage=1.0 (all problems generate k=5 solutions)

Step 2: Stratify problems into hard/easy tiers per model
         → Hypothesis h-m2: verify Jaccard > 0.30 across model pairs

Step 3: Extract P(True) logprob confidence per (problem, solution) pair
         → Hypothesis h-m3: verify std(c) > 0.05 (non-degenerate signal)

Step 4: Compute ΔECE = ECE(hard) − ECE(easy) with bootstrap CI
         → Hypothesis h-m4: test ΔECE ≥ 0.03 in ≥2/3 architectures (primary prediction)
         → Temperature scaling probe: test whether ΔECE persists after global T
```

Steps 1–3 validate infrastructure (MUST_WORK gates); Step 4 tests the core calibration hypothesis. This sequential validation design ensures that a negative result at Step 4 is interpretable as genuine evidence about calibration, not a methodology failure.
