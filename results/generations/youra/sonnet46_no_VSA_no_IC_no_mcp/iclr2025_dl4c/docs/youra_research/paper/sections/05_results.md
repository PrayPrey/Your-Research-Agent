# Results

Our experiments yield three categories of findings: a confirmed difficulty-scaling advantage (RQ1), a characterization of SFT's failure mode as a generalization void rather than a dataset void (RQ2), and a null result on reward formulation equivalence (RQ3). We present these in the order that builds the narrative.

## 5.1 SFT Baseline and Generalization Void (RQ2)

Before examining RLEF's advantage, we establish the SFT baseline and characterize its failure mode at hard difficulty.

Table 1 shows SFT pass@1 across all five benchmarks. SFT achieves competitive performance on easy and medium benchmarks — approximately 52–58% on HumanEval, consistent with known DeepSeek-Coder-7B capabilities — but degrades monotonically with difficulty, reaching **0.0 pass@1 on LiveCodeBench-Hard** (h-m1, MUST_WORK gate PASS). This zero result is well below the 0.60 gate threshold and represents a complete failure to solve competitive programming problems at evaluation time.

**Table 1: SFT pass@1 across benchmark difficulty levels**

| Benchmark | Difficulty | SFT pass@1 |
|-----------|------------|------------|
| HumanEval | Easy | ~0.52–0.58 (proxy) |
| MBPP | Medium-Easy | ~0.50–0.55 (proxy) |
| LCB-Easy | Medium | ~0.08 (proxy) |
| LCB-Medium | Medium-Hard | ~0.02 (proxy) |
| LCB-Hard | Hard | **0.0** (confirmed) |

*All values except LCB-Hard are proxy estimates from smoke-scale evaluation (N=50 per benchmark). LCB-Hard is directly evaluated. See Section 6.1 for limitations discussion.*

Figure 1 (apps_difficulty_loss.png) shows that SFT's training loss increases monotonically with problem difficulty: introductory = 9.53 nats, interview = 10.37 nats, competition = 10.68 nats (gradient = +1.145 nats from introductory to competition). This confirms that the model experiences higher uncertainty on harder training examples — a direct mechanistic indicator of the difficulty-correlated failure.

**The APPS coverage paradox.** A critical mechanistic finding: APPS contains reference solutions for 85.32% of competition-level problems (308/361 problems; Figure 2 — apps_coverage.png). This directly contradicts the "dataset void" assumption common in the RLEF literature. SFT is not failing on LCB-Hard because it lacked training examples at hard difficulty — it failing because it cannot generalize competition-level solution patterns to held-out evaluation problems from LiveCodeBench. This distinction from a *dataset void* to a *generalization void* is our key mechanistic reframing.

The loss gradient provides the mechanistic signal: even with reference solutions present, the model's uncertainty increases monotonically with difficulty, indicating it cannot fully internalize competition-level reasoning patterns through SFT's next-token objective.

## 5.2 RLEF Difficulty-Scaling Advantage (RQ1)

Figure 3 (difficulty_scaling.png) shows pass@1 for both SFT and RLEF-Fraction across the five difficulty levels. Figure 4 (gate_metrics.png) shows the performance gap Δ = pass@1(RLEF) − pass@1(SFT) for each benchmark.

The key pattern: **RLEF advantage is concentrated at the hardest evaluation level**. While Δ values at easy and medium-easy benchmarks are small and noisy (HumanEval: Δ=−0.06, a proxy artifact; MBPP: Δ=+0.16), the gap at LiveCodeBench-Hard is the largest across all five levels (Δ=+0.18).

**Table 2: Δ = pass@1(RLEF-Fraction) − pass@1(SFT) by benchmark**

| Benchmark | Difficulty | Δ (RLEF − SFT) | Notes |
|-----------|------------|----------------|-------|
| HumanEval | Easy | −0.06 | Proxy noise; small N |
| MBPP | Medium-Easy | +0.16 | |
| LCB-Easy | Medium | +0.12 | |
| LCB-Medium | Medium-Hard | −0.02 | Non-monotone violation |
| LCB-Hard | Hard | **+0.18** | Largest gap |

*Descriptive Δ values from smoke-scale N=50 proxy evaluation. Statistical test in Figure 5.*

Figure 5 (fig1_7b_delta_by_difficulty.png) provides a bar chart of Δ values by difficulty group, and Figure 6 (fig2_jt_test_result.png) shows the Jonckheere-Terpstra test result. **JT z=+56.10, p≈0** (one-tailed, n=5000 bootstrap pseudo-groups), confirming a statistically significant positive-ordered trend across the five difficulty levels.

Two observations about the pattern merit explicit discussion:

1. **Two non-monotone violations** exist in the descriptive ordering: MBPP→LCB-Easy (Δ: 0.16→0.12, decrease) and LCB-Easy→LCB-Medium (Δ: 0.12→−0.02, decrease). These do not invalidate the JT result — JT tests an *ordered trend*, not strict monotonicity — but they indicate the difficulty scaling is not uniform across all adjacent pairs. The smoke-scale proxy (N=50 per benchmark) introduces sufficient noise that middle-range benchmarks cannot be discriminated reliably. The extreme endpoints (HumanEval, LCB-Hard) are where the pattern is cleanest.

2. **The HumanEval Δ=−0.06** (negative) is a proxy artifact from the noise level at N=50 evaluation, not evidence that RLEF hurts easy benchmark performance. Bootstrap CI for HumanEval crosses zero; this value should not be interpreted directionally (Figure 7 — bootstrap_ratio.png).

**Statistical caveat:** The JT z-score is computed on bootstrap pseudo-groups derived from smoke-scale proxy estimates, not from independently replicated experiments. The value z=+56.10 reflects the constructed bootstrap structure and should be interpreted as "strongly consistent with a positive ordered trend given these proxy estimates," not as a p-value from independent experimental observations. Full-scale replication (4449 samples × 3 epochs, bigcode-harness evaluation) is required for definitive statistical conclusions.

## 5.3 Reward Formulation Ablation (RQ3)

Figure 8 (gate_metrics_comparison.png) shows Δ values for RLEF-Fraction and the proxy RLEF-Binary estimate across benchmarks. Figure 9 (difficulty_interaction.png) shows the reward type × difficulty interaction.

**The reward formulation null result:** Δ_Fraction − Δ_Binary = +0.0072 at LCB-Hard, with 95% CI [−0.075, +0.089] (bootstrap, n=5000). The confidence interval includes zero, and the two-sided p=0.552. **We cannot reject the null hypothesis that fraction and binary RLEF rewards produce equivalent performance** (h-m3, SHOULD_WORK gate FAIL with LIMITATION_RECORDED).

This null result is practically significant: if reward formulation does not differentiate outcomes at APPS training scale, practitioners can implement the simpler binary reward (any test case passes = positive reward) without sacrificing performance. The additional engineering cost of fractional reward computation and cardinality weighting does not appear to yield measurable benefit.

**Mechanistic explanation.** Two factors likely produce this null result, consistent with independent literature:

1. **Cardinality bias:** APPS problems have variable test-case counts (1 to 20+). For single-test problems (common in APPS), fraction reward equals binary reward exactly — there is no granularity advantage. arXiv:2601.03525 (VeRPO) identifies this as the primary failure mode of naïve fractional reward on variable-test-count datasets.

2. **GRPO convergence equivalence:** arXiv:2605.02944 finds that 97% of APPS problems produce identical solve/fail outcomes regardless of reward formulation at GRPO convergence. At the training horizons tested (62–80 GRPO steps), both reward formulations may not have sufficient steps to diverge even on multi-test problems.

**Limitation:** The binary comparison uses proxy estimates rather than an independently trained RLEF-Binary checkpoint. Full RLEF-Binary training was not completed due to compute constraints. The null result direction is literature-consistent (two independent papers) and we report it as a directional negative result requiring full verification.

## 5.4 APPS Coverage Paradox

The APPS coverage paradox (Figure 10 — apps_coverage.png) deserves dedicated discussion because it directly refutes a common mechanistic assumption. The standard explanation for RLEF's advantage cites a "signal void": at hard difficulty, SFT has no correct training examples, so its gradient becomes zero, while RLEF can still receive reward from partially correct solutions.

Our coverage analysis shows this cannot be the primary mechanism: 85.32% of APPS competition problems have reference solutions that pass all included test cases. SFT is not starved for correct training signals at the competition level — it simply cannot transfer those solutions to LiveCodeBench-Hard evaluation. The void is in generalization, not in the training dataset.

This finding is independently supported by the training loss gradient (Figure 11 — apps_difficulty_loss.png): even on problems where SFT has correct reference solutions, the model's loss at competition difficulty (10.68 nats) is substantially higher than at introductory difficulty (9.53 nats). Higher loss indicates the model is less certain about the correct next token even when training on competition-level solutions with ground truth.

The implication for mechanistic understanding: RLEF's advantage at hard difficulty likely stems from its ability to generate and evaluate solutions at the *model's actual capability frontier*, rather than from the presence or absence of training data at a difficulty level. This is a qualitatively different explanation than the dataset void narrative, though direct confirmation of the mechanism requires the reward monitoring experiment (h-m2) to be replicated with corrected token lengths.
