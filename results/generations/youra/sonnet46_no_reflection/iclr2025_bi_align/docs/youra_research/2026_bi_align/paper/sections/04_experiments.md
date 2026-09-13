# 4. Experiments

## 4.1 Research Questions

Our experimental design is organized around three research questions, each addressing a distinct
layer of the bidirectional alignment hypothesis.

**RQ1:** Do AI-Induced Formatting Signals (AIFS) predict annotator preference in a supply-controlled
conditional logit model, controlling for length, fluency, and prompt-level heterogeneity?

**RQ2:** Do annotators in the deployed-AI-familiar (online) condition show stronger conditional
preference for AIFS features relative to annotators in the base (naive) condition, as measured by
the split × ΔAIFS interaction coefficient β₄?

**RQ3:** If the null result is observed for RQ2, can we rule out insufficient statistical power as
the explanation — and, if so, what is the most plausible alternative account?

RQ1 functions as a construct validity check: a positive and significant β₁ would confirm that the
AIFS measure captures preference-relevant variation, establishing the precondition for testing the
behavioral hypothesis in RQ2. RQ3 is activated only if RQ2 yields a null result, and is addressed
through confidence interval analysis and sensitivity testing rather than through a separate
experiment.

---

## 4.2 Dataset

We use the Anthropic Human Helpfulness and Harmlessness Reinforcement Learning from Human Feedback
dataset (HH-RLHF) [Bai et al., 2022], which contains pairwise human preference judgments over
assistant responses. We draw on two publicly available subsets that differ in their annotator
population:

- **Helpful-base** (43,835 rows; 20,108 retained after quality filtering): Collected before the
  public release of large language model products. Annotators in this split are treated as the
  *base* (AI-naive) condition.
- **Helpful-online** (22,007 rows; 20,063 retained): Collected after widespread LLM deployment.
  Annotators in this split are treated as the *online* (AI-familiar) condition.

After filtering, the combined dataset contains **80,342 preference pairs** across **40,171
clustered prompts**. The split variable is a binary indicator (0 = base, 1 = online) and functions
as the between-condition exposure proxy in our main model. We note from the outset that this proxy
is observational — annotator identity is not recorded in the dataset, and the split boundary is
defined by collection period rather than by experimentally assigned condition. The implications of
this proxy's validity are addressed in Section 6.

**Semantic clustering.** To control for prompt-level heterogeneity, we embed all prompts using
`all-MiniLM-L6-v2` [Reimers & Gurevych, 2019] and apply agglomerative clustering with a cosine
similarity threshold of 0.85. This yields **27,034 semantic clusters**, which enter the conditional
logit model as fixed effects. The clustering threshold was selected to balance granularity against
cluster sparsity; sensitivity to this threshold is examined in Section 5.4.

---

## 4.3 AIFS Construct

The AI-Induced Formatting Signal (AIFS) is a count-based measure of surface-level formatting
features that large language models are known to overrepresent relative to human-written text
[Rafailov et al., 2023; CITE: LLM stylistic amplification literature]. For each response, AIFS is
computed as the sum of four binary regex pattern matches:

1. **structured_list** — presence of markdown bullet or numbered list structure
2. **safety_preface** — opening disclaimer or content-warning phrase
3. **cot_marker** — chain-of-thought signaling phrase (e.g., "Let me think step by step")
4. **hedging** — epistemic hedge markers (e.g., "I'm not certain, but...")

The within-pair AIFS contrast (ΔAIFS = AIFS_chosen − AIFS_rejected) is the primary treatment
variable. By computing the contrast at the pair level, we difference out prompt-level AIFS demand,
isolating supply-side formatting variation.

---

## 4.4 Model Specification

We estimate a **conditional logit model** [McFadden, 1974] of the form:

```
P(chosen = 1) ~ β₁·ΔAIFS + β₂·Δlength + β₃·Δperplexity
              + β₄·(ΔAIFS × split) + cluster_FE
```

where:

- **ΔAIFS** is the within-pair AIFS contrast (primary predictor)
- **Δlength** is the token-length contrast (response-quality control)
- **Δperplexity** is the language model perplexity contrast (fluency control)
- **ΔAIFS × split** is the interaction term whose coefficient β₄ is the primary test statistic
  for the bidirectional alignment hypothesis
- **cluster_FE** are semantic cluster fixed effects, absorbing prompt-level confounders

The conditional logit formulation is appropriate because (1) each observation is a binary choice
between two alternatives, (2) prompt-level fixed effects are absorbed without incidental parameters
bias [McFadden, 1974], and (3) the model naturally accommodates the paired structure of the
HH-RLHF dataset.

**Hypothesis for β₄.** Under the bidirectional alignment hypothesis, online annotators have
internalized AI formatting norms through extended exposure, so they assign higher utility to AIFS
features. This predicts β₄ > 0. We set a conservative MUST_WORK gate: β₄ ≤ 0 would falsify the
directional prediction; OR < 1.10 would indicate negligible practical effect; p < 0.01 is required
for inferential confidence.

---

## 4.5 Implementation Details

**Optimizer.** We initially attempted BFGS optimization, which is standard for conditional logit
models at moderate scale. BFGS failed to converge on the full 80,342-row dataset, likely due to
the dimensionality introduced by 27,034 cluster fixed effects. We switched to the Newton-Raphson
(BFGS-fallback Newton) optimizer, which converged successfully. The BFGS failure itself is
informative: it confirms that the dataset is operating at the boundary of standard logit toolchain
capacity, ruling out trivially underpowered data as a concern.

**Software and hardware.** All experiments were run on a single GPU (CUDA_VISIBLE_DEVICES set to
the emptiest device at runtime). The conditional logit model was estimated using Python with the
`statsmodels` conditional logit implementation. Total runtime was **2037.7 seconds** (~34 minutes)
for the full dataset including clustering, feature extraction, and model estimation.

**Evaluation metrics.** We report the following for β₄:

| Metric | Role | Threshold |
|--------|------|-----------|
| Point estimate | Directionality check | Must be > 0 |
| Odds ratio (OR) | Effect magnitude | Must be ≥ 1.10 |
| 95% CI | Power / precision assessment | CI lower bound must be > 1.0 |
| Wald p-value | Inferential significance | Must be < 0.01 |
| LRT statistic | Model fit contribution | Complementary to Wald |

The combination of OR and CI width is the primary evidence standard: a tight CI that excludes
OR = 1.0 in the positive direction would constitute strong evidence for the bidirectional alignment
hypothesis; a tight CI that fails to do so would constitute strong evidence against it regardless
of sample size.
