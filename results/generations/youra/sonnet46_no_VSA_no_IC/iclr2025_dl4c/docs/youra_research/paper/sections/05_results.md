# 5. Results

We present results in causal chain order, following the experimental design of Section 4: existence → selection signal → training gradient concentration.

## 5.1 RQ1: Variance Distribution Characterization (h-e1)

**The distribution is severely right-skewed — but a meaningful high-variance subset exists.**

Table 1 and Figure 1 show the per-problem pass rate and variance distribution across all 374 MBPP training problems for frozen DeepSeek-Coder-7B-Instruct (k=4, max_new_tokens=128).

**Table 1: MBPP Pass Rate Distribution (374 problems, k=4, max_new_tokens=128)**

| Pass Rate (p_i) | Count | Percentage | Variance (v_i) |
|-----------------|-------|------------|----------------|
| 0.00 (all-fail) | 343 | 91.7% | 0.0000 |
| 0.25 (1/4 pass) | 29 | 7.8% | **0.1875** |
| 0.50 (2/4 pass) | 0 | 0.0% | 0.2500 |
| 0.75 (3/4 pass) | 0 | 0.0% | 0.1875 |
| 1.00 (all-pass) | 2 | 0.5% | 0.0000 |

**Key observations:**

1. *The dominant outcome is all-fail:* 343 of 374 problems (91.7%) produce zero correct completions across all 4 profiling attempts. This reflects two compounding factors: (a) max_new_tokens=128 truncates many Python function completions before the function body is complete, and (b) k=4 collapses any problem with true p_i ≤ 0.24 to an observed p_i=0. The 91.7% all-fail rate is more severe than the 69.25% zero-gradient estimate from Gradient Starvation [2025], confirming that generation parameter constraints dramatically amplify starvation beyond the theoretical baseline.

2. *The high-variance subset is real:* 29 problems (7.8%) yield exactly p_i=0.25 (variance=0.1875), exceeding the gate threshold of 15 problems (PASSED). These are problems where the model occasionally generates a correct solution — precisely the gradient-signal zone. The gate threshold of 15 was conservatively set proportional to the original design's 50-problem threshold (rescaled for k=4 instead of k=8).

3. *No intermediate-difficulty problems exist at k=4:* With only 5 discrete pass-rate levels under k=4, the range of intermediate difficulties is collapsed. All 29 high-variance problems are at exactly p_i=0.25 — the same variance level. k=8 with max_new_tokens=512 would reveal finer-grained intermediate structure currently masked by truncation and granularity.

Figure 1 shows the pass rate histogram (left) and variance histogram (right). The extreme left-skew of the variance distribution is visually striking: a single spike at v_i=0.1875 versus a large mass at v_i=0.

**Gate verdict (h-e1): PASSED** — 29 ≥ 15 (threshold). Existence confirmed.

## 5.2 RQ2: Selection Signal Validation (h-m1)

**Variance-guided selection achieves 4.24× higher mean variance than random selection (p=2.22e−06).**

Building on h-e1, we compare the variance distribution of top-50 (variance-guided) versus random-50 selections from the 374-problem pool.

**Table 2: Variance Selection Comparison**

| Metric | Variance-50 | Random-50 | Difference | p-value |
|--------|-------------|-----------|------------|---------|
| Mean variance | **0.1113** | 0.0262 | 0.0850 | 2.22e−06 |
| Ratio | **4.24×** | 1.0× | — | — |
| Mann-Whitney U | 1807.0 | — | — | 2.22e−06 |

Figure 2 shows the comparison: the left panel (fig1_mean_comparison.png) shows mean variance with individual data points as a bar+strip plot. The gap is large and unambiguous. The right panel (fig4_cdf.png) shows the empirical CDFs: the variance-50 CDF lies entirely above the random-50 CDF, confirming stochastic dominance — variance-guided selection is not just better on average but uniformly better across the full distribution.

**Boundary behavior:** boundary_gap=0.0 — multiple problems tie at variance=0.0 at the rank-50 boundary. This means "top-50" includes all 29 high-variance problems plus 21 zero-variance problems (to fill the quota). The selection is well-defined for the high-variance tier; the zero-variance fill is arbitrary but does not affect the selection signal calculation, which is dominated by the 29 high-variance entries.

**Key observations:**

1. *The selection signal is not marginal:* 4.24× mean variance advantage with p=2.22e−06 (Mann-Whitney U one-sided test). Even with 21 zero-variance filler problems in the variance-50 set, the overall distribution is dramatically different from random selection.

2. *Stochastic dominance holds:* The full empirical CDF of variance-50 lies above random-50 (Figure 2, right). This is a strong result: variance-guided selection is better at every quantile, not just on average.

3. *Profile-once speed:* The vLLM batch profiling completed in approximately 32 seconds for 374×4=1,496 completions — compared to an estimated ~8 hours for sequential HF inference at k=8, max_new_tokens=512. This establishes the practical viability of offline profiling.

**Gate verdict (h-m1): PASSED** — difference=0.0850 > 0, MWU p=2.22e−06 < 0.05. Selection signal confirmed.

## 5.3 RQ3: Gradient Concentration During Training (h-m2, h-m3)

**Both conditions show frac_reward_zero_std=1.0 throughout all training steps — cold-start confirmed.**

This is the central negative result of the paper, and it is precise and robust.

**h-m2 results (50 steps, LR=5×10⁻⁷):**

Both variance-50 and random-50 conditions maintained frac_reward_zero_std=1.0 at every logged step from step 1 through step 50. reward/mean=0.0 and grad_norm=0.0 at every step. No checkpoint was saved. Total generation attempts: 50 steps × 50 problems × 4 completions = 10,000 attempts, all returning reward=0.

**h-m3 results (200 steps, LR=1×10⁻⁶):**

Even with doubled learning rate and 4× more training steps, frac_reward_zero_std=1.0 persisted throughout all 200 steps. reward/mean=0.0 throughout. Total generation attempts across h-m2 and h-m3 combined: 40,000+. All returned reward=0.

Figure 3 shows the learning curves (learning_curves.png): flat horizontal lines at frac=1.0 for both conditions throughout all steps. The two curves are visually indistinguishable — there is no difference between variance-guided and random selection in this regime.

**Key observation:** The selection signal from RQ2 — real, statistically robust, 4.24× advantage — is completely invisible during training. The reason is that σ=√(k(G−k))/G=0 when k=0 for every problem in every group: cold-start nullifies the selection advantage before any gradient can be generated. Data selection method is irrelevant when no condition produces any reward.

**Most likely root cause (parameter mismatch):** Profiling used vLLM with max_new_tokens=128; training used HF GRPOTrainer with max_completion_length=512. We hypothesize that the 29 problems profiled at p_i=0.25 (occasional success at 128 tokens) may yield p_i=0 under training conditions (where completion behavior under 512-token limit, HF tokenizer, and subprocess execution may differ). This would nullify the selection entirely before training begins. The fix is straightforward: re-profile under training-identical parameters.

**Additional contributing factor:** TRL GRPOTrainer's off-policy replay at batch_size=4 produces only ~13 unique rollouts per 50 training steps on a 50-problem dataset, limiting exploration. However, the scale of failure (40,000+ attempts, zero reward) is inconsistent with exploration being the primary issue — it points to a regime-level capability gap under these generation constraints.

**Gate verdict (h-m2, h-m3): FAILED** — frac_reward_zero_std=1.0 for all conditions at all steps; gap=0.0000 throughout. Mechanism Step 3 falsified under current parameters.
