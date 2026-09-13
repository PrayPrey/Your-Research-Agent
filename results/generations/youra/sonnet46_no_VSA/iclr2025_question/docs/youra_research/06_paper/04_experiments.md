# Experiments

## Proof-of-Concept Protocol

We run a proof-of-concept (PoC) experiment at $N=300$ prompts (12% of the full target $N=2{,}500$) as a smoke test to validate: (1) the end-to-end pipeline, (2) signal non-degeneracy, and (3) the primary independence claim (Pearson $|r|$). The PoC is not designed to confirm the partial $R^2 \geq 0.02$ threshold, which requires statistical power achievable only at $N=2{,}500$. All code, checkpoints, and figures are designed to run unchanged at $N=2{,}500$ by a single configuration change (`N_PROMPTS: 300 → 2500`).

**Rationale for PoC-first design:** The gating structure is hierarchical. The ABANDON threshold ($|r| > 0.85$) must be ruled out before investing compute in ensemble AUROC evaluation. If SE is a reparameterization of min\_logprob, ensemble training is moot. The PoC answers this question cheaply: 300 prompts require $\sim$6 inference calls each (5 stochastic + 1 greedy + judge), approximately 1,800 LLM forward passes, feasible on a single A100 in under 30 minutes.

## Experimental Setup

| Parameter | Value |
|-----------|-------|
| Dataset | TriviaQA dev (`rc.nocontext`), first 300 prompts (seed=42) |
| Generator | `meta-llama/Llama-3.1-8B-Instruct` |
| Stochastic samples | $N=5$, temperature=0.7, top-p=0.95, max\_new\_tokens=50 |
| Greedy decode | temperature=0.0, `output_scores=True` |
| NLI model | `cross-encoder/nli-deberta-v3-small` (bidirectional, non-strict) |
| Judge | `Qwen/Qwen2.5-7B-Instruct` (cross-model, batch\_size=16) |
| Conda env | `youra-h-e1` |

## Gate Criteria

The PoC evaluates three gate conditions:

1. **ABANDON gate:** $|r|(\text{SE}, \text{min\_logprob}) > 0.85$ → hypothesis abandoned (SE is merely a reparameterization of log-prob)
2. **Independence gate:** $|r| < 0.70$ → independence criterion passes
3. **Partial $R^2$ gate:** $R^2_\text{SE} \geq 0.02$ with LRT $p < 0.05$ → conditional independence confirmed

All three criteria must hold for a full gate pass. At PoC scale ($N=300$), criterion 3 is expected to be underpowered; its result is interpreted as directional evidence, not confirmation.

## Circularity Diagnostic

Before fitting the conditional logistic regression, we compute Spearman $\rho(\text{SE}, h)$ where $h$ is the LM-judge binary correctness label. This diagnostic tests whether the judge and the NLI-based SE signal share reasoning biases — a concern raised because both use NLI-style semantic comparison. We require $|\rho| < 0.40$ to proceed.

The cross-model design (Qwen-2.5-7B judging Llama-3.1-8B outputs) is the primary architectural safeguard against circularity: the judge evaluates factual alignment of a single greedy answer against the question, while SE evaluates semantic consistency across 5 stochastic samples from a different model family. These are structurally distinct operations even if both draw on NLI reasoning.

## Mechanism Reality Checks

After signal computation, we run a battery of seven checks to verify pipeline integrity:

| Check | Expected | Purpose |
|-------|----------|---------|
| `sensitivity` | SE var $> 0.01$ | SE is discriminative, not constant |
| `smoothness` | min\_logprob $< 0$ | All log-probs are valid (negative) |
| `determinism` | Same SE on re-computation | No randomness in NLI clustering |
| `gradient_flow` | SE varies with NLI cluster assignments | SE computation is not degenerate |
| `weight_influence` | min\_logprob correlates with generation probability | Feature extraction is correct |

Failure of any check triggers an explicit error; the experiment does not proceed to statistical analysis.

## Figures Generated

Four diagnostic figures are produced:

- **`scatter_se_vs_minlogprob.png`:** Scatter plot of SE\_N5 vs. min\_logprob for all 300 prompts, colored by LM-judge correctness. Visualizes the independence structure.
- **`correlation_heatmap.png`:** Pearson correlation matrix over $[\text{SE\_N5}, \text{min\_logprob}, \text{response\_length}, \text{correctness}]$. Full inter-feature correlation overview.
- **`gate_metrics.png`:** Bar chart showing $|r|$ vs. threshold 0.70, and partial $R^2$ vs. threshold 0.02. Summarizes gate evaluation outcome at a glance.
- **`lr_coefficients.png`:** Logistic regression coefficients ($\beta_1, \beta_2, \beta_3, \beta_4$) with 95% confidence intervals for the full model $[\text{min\_logprob}, \text{SE}, L, \text{SE} \times \text{min\_logprob}]$.
