# Methodology

## Problem Setup

We study whether Semantic Entropy (SE\_N5) and minimum token log-probability (min\_logprob) are statistically independent uncertainty signals for predicting factual correctness on short-answer QA. Formally, let $x$ be a question, $y^*$ be the correct answer, $\hat{y}$ be the model's greedy answer, and $h \in \{0, 1\}$ be the binary correctness label ($h=1$ if correct). We define two uncertainty signals:

**SE\_N5:** Generate $N=5$ stochastic responses $\{s_1, \ldots, s_5\}$ at temperature $\tau=0.7$. Apply bidirectional NLI clustering (DeBERTa-MNLI) to group responses into semantic equivalence classes $\{C_k\}$. Compute:
$$\text{SE}(x) = -\sum_k p(C_k \mid x) \log p(C_k \mid x), \quad p(C_k \mid x) = \frac{|\{i : s_i \in C_k\}|}{N}$$

**min\_logprob:** Generate the greedy response $\hat{y} = (t_1, \ldots, t_T)$ with temperature 0.0. Extract per-token log-probabilities $\{\log p(t_i \mid x, t_{<i})\}_{i=1}^T$ from the model's output scores. Compute:
$$\text{min\_logprob}(x) = \min_{i \in 1..T} \log p(t_i \mid x, t_{<i})$$

The two signals are computed on different inference calls (stochastic sampling vs. greedy decode) and aggregate uncertainty at different granularities (sentence-level semantic entropy vs. token-level minimum confidence), making them algebraically distinct.

## Dataset

We use TriviaQA \citep{joshi2017triviaqa} in the `rc.nocontext` (closed-book) configuration, validation split, shuffled with seed=42 and restricted to the first 2,500 questions (our target for the full-scale experiment; PoC uses first 300). TriviaQA provides a list of answer aliases per question, enabling alias-based fallback correctness checking in addition to LM-judge evaluation. The closed-book setting eliminates context document confounds and focuses on the model's parametric knowledge.

## Models

**Generator:** `meta-llama/Llama-3.1-8B-Instruct` (bfloat16, device\_map="auto"). Generates both stochastic samples (N=5, temp=0.7, top-p=0.95, max\_new\_tokens=50) and greedy decode (temp=0.0, output\_scores=True) for each question.

**NLI Model for SE Clustering:** `cross-encoder/nli-deberta-v3-small` via HuggingFace. Adapted from the official jlko/semantic\_uncertainty implementation \citep{kuhn2023semantic}. Non-strict bidirectional entailment: two responses are semantically equivalent if neither implies contradiction and the pair is not mutually neutral.

**Judge:** `Qwen/Qwen2.5-7B-Instruct` (cross-model: different family from generator). Evaluates each greedy answer with the prompt: *"Is the following answer correct for the question? Answer YES or NO. Question: \{q\}. Answer: \{a\}. Correct?"* Binary label parsed from YES/NO; fallback to alias string match.

## Statistical Framework

**Independence Test (Pearson $r$):** We compute Pearson $|r|(\text{SE\_N5}, \text{min\_logprob})$ across all prompts. Gate thresholds: $|r| < 0.70$ (independence pass), $|r| > 0.85$ (ABANDON — SE is a reparameterization of min\_logprob).

**Circularity Diagnostic (Spearman $\rho$):** We measure Spearman $\rho(\text{SE}, h)$ where $h$ is the LM-judge correctness label. If $|\rho| > 0.40$, the judge and SE share NLI-based reasoning in a circular way. We require $|\rho| < 0.40$.

**Conditional Independence Test (Partial $R^2$):** We fit two logistic regression models:
- Full model: $\text{logit}(P(h=1)) = \beta_0 + \beta_1 \cdot \text{min\_logprob} + \beta_2 \cdot \text{SE} + \beta_3 \cdot L + \beta_4 \cdot (\text{SE} \times \text{min\_logprob})$
- Reduced model: $\text{logit}(P(h=1)) = \beta_0 + \beta_1 \cdot \text{min\_logprob} + \beta_3 \cdot L$

where $L$ is response length (token count). We compute McFadden-style partial $R^2$: $R^2_\text{SE} = 1 - \ell_\text{full}/\ell_\text{reduced}$, and a likelihood ratio test (LRT) for the SE terms. Gate criterion: $R^2_\text{SE} \geq 0.02$.

**Mechanism Reality Checks:** We verify signal validity via: (i) SE variance $> 0.01$ (non-degenerate), (ii) all min\_logprob values $< 0$ (valid log-probabilities), (iii) determinism (same SE from same samples), (iv) sensitivity (SE varies across prompts), (v) smoothness (min\_logprob varies continuously), (vi) gradient flow (SE computation is differentiable with respect to cluster boundaries), (vii) weight influence (min\_logprob correlates with generation probability as expected).

## Implementation

Code is organized into five modules: `generate.py` (LLM generation with checkpointing), `compute_signals.py` (SE\_N5 and min\_logprob), `judge.py` (LM-as-a-judge correctness labeling), `stats_analysis.py` (Pearson, Spearman, conditional LR, gate evaluation), and `visualize.py` (four diagnostic figures). GPU memory is managed via explicit model deletion and `torch.cuda.empty_cache()` between generation and judge phases. All signals are checkpointed to disk after generation to avoid redundant inference.
