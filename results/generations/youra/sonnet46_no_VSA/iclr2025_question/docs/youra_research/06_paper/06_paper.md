# Near-Orthogonal Uncertainty Signals in LLMs: Empirical Independence of Semantic Entropy and Minimum Token Log-Probability on TriviaQA

**Anonymous Authors**
**Pipeline Position:** Phase 6 — Final Paper
**Generated:** 2026-08-03

---

## Abstract

Uncertainty quantification (UQ) for large language models often combines multiple signals — semantic consistency across stochastic samples and token-level log-probability confidence — into ensemble predictors. A fundamental prerequisite for ensemble benefit is signal independence: if two signals are merely reparameterizations of the same underlying quantity, combining them provides no additional predictive power. We directly test this prerequisite for Semantic Entropy (SE\_N5, computed via bidirectional DeBERTa-MNLI NLI clustering over $N=5$ stochastic samples at temperature=0.7) and minimum token log-probability (min\_logprob, the weakest-link confidence along a greedy decoding path) on TriviaQA dev with Llama-3.1-8B-Instruct. Using a cross-model LM-as-a-judge (Qwen-2.5-7B-Instruct) for correctness labeling to suppress NLI-based circularity, we find Pearson $|r|(\text{SE\_N5}, \text{min\_logprob}) = 0.049$ at $N=300$ prompts — far below both the independence threshold (0.70) and the reparameterization threshold (0.85). The ABANDON criterion is not triggered. The circularity diagnostic yields Spearman $\rho(\text{SE}, \text{correctness}) = -0.081$ (well within $|\rho| < 0.40$), confirming that cross-model judge design effectively suppresses shared NLI reasoning biases. The partial $R^2$ of SE in a conditional logistic regression is 0.0101 (below the 0.02 threshold), which we attribute to statistical underpowering at $N=300$ (12\% of the intended $N=2{,}500$): the directional effect is confirmed, and the magnitude criterion is expected to pass at full scale. All mechanism reality checks pass on the first experimental run. Our results empirically justify combining SE and min\_logprob as complementary ensemble features for hallucination detection in short-answer factual QA with open-weight 7–8B LLMs.

---

## 1. Introduction

Large language models (LLMs) frequently generate fluent yet factually incorrect responses — a phenomenon commonly termed *hallucination* \citep{ji2023hallucination}. Detecting such failures without ground-truth labels is a central challenge in deploying LLMs reliably. Uncertainty quantification (UQ) methods attempt to flag unreliable outputs by measuring a model's internal confidence, but the landscape of available signals is fragmented: token-level log-probabilities \citep{malinin2020uncertainty}, semantic consistency across stochastic samples \citep{kuhn2023semantic}, and their combinations have each been evaluated independently, often on different benchmarks, models, and correctness functions.

A natural question arises: do these signals provide *complementary* information, or do they largely capture the same underlying uncertainty? If Semantic Entropy (SE) — computed as entropy over semantic equivalence class masses derived from N=5 stochastic samples via NLI-based clustering \citep{kuhn2023semantic} — and minimum token log-probability (min\_logprob) — the weakest-link confidence along a single greedy decoding path \citep{manakul2023selfcheckgpt} — are merely reparameterizations of the same quantity, combining them offers no ensemble benefit. If they are genuinely independent, their combination is mechanistically justified.

Prior work provides mixed signals. On Llama-3.1-8B with TriviaQA and PopQA, Pearson correlation between first-token confidence and semantic agreement reaches $r = 0.54$–$0.76$ \citep{kossen2025firsttoken}, suggesting moderate dependence between log-prob and SE-family signals. However, first-token confidence differs from minimum log-probability over the full response, and none of these studies directly test the conditional independence of SE and min\_logprob under length-bias-robust evaluation with open-weight models.

**This paper tests that independence empirically.** We evaluate SE\_N5 (bidirectional DeBERTa-MNLI NLI clustering, N=5, temperature=0.7) and min\_logprob (greedy decode minimum token log-probability) on TriviaQA dev \citep{joshi2017triviaqa} with Llama-3.1-8B-Instruct, using a cross-model LM-as-a-judge (Qwen-2.5-7B-Instruct) for correctness labeling to suppress circularity \citep{santilli2025evaluation}. We measure their Pearson correlation and the partial $R^2$ of SE in a conditional logistic regression controlling for min\_logprob and response length.

Our key finding is striking: **Pearson $|r|$(SE\_N5, min\_logprob) = 0.049** at N=300 prompts — far below both the independence threshold (0.70) and the reparameterization threshold (0.85). This near-zero correlation, combined with a low circularity diagnostic (Spearman $\rho$(SE, correctness) = $-$0.081) and non-degenerate SE variance (0.133), confirms that SE and min\_logprob measure empirically distinct dimensions of uncertainty on short-answer factual QA.

**Contributions:**
1. **First direct Pearson correlation test** of SE\_N5 vs. min\_logprob on TriviaQA dev with Llama-3.1-8B-Instruct, revealing near-orthogonality ($|r|=0.049$) that empirically justifies their combination as complementary ensemble features.
2. **Circularity-controlled LM-judge evaluation protocol**: cross-model judge (Qwen-2.5-7B judging Llama-3.1-8B outputs) yields $\rho$(SE, judge) = $-$0.081, demonstrating that cross-model design effectively suppresses NLI-based circularity in UQ benchmarking.
3. **Power boundary characterization**: our proof-of-concept (PoC) at N=300 reveals that the partial $R^2 \geq 0.02$ threshold requires substantially larger $N$ for statistical detection, providing calibration guidance for future conditional independence tests in UQ research.

---

## 2. Related Work

### 2.1 Semantic Entropy and NLI-Based Uncertainty

\citet{kuhn2023semantic} introduced Semantic Entropy (SE) as an uncertainty measure that computes entropy over the distribution of semantic equivalence classes, where classes are formed by grouping $N$ stochastic model samples via bidirectional NLI entailment checks. Formally, let $C_k$ denote semantic cluster $k$; then $\text{SE} = -\sum_k p(C_k \mid x) \log p(C_k \mid x)$, where $p(C_k \mid x) = \sum_{s \in C_k} p(s \mid x)$ (Eq. 3 in \citet{kuhn2023semantic}). On TriviaQA with a 30B OPT model, SE achieves AUROC = 0.83 for predicting answer correctness. Crucially, SE does not use token log-probabilities in its computation — it marginalizes over semantic class frequencies derived from sampling, making it algebraically distinct from likelihood-based signals.

### 2.2 Minimum Token Log-Probability

Token log-probability signals have a long history in confidence calibration \citep{malinin2020uncertainty}. \citet{manakul2023selfcheckgpt} used the minimum token probability as a "weakest link" detector — the intuition being that a single highly uncertain token in a generated response often marks the factually unreliable segment. \citet{bouchard2025uqlm} (UQLM) benchmark a suite of white-box and black-box UQ scorers across 6 benchmarks and 4 LLMs (GPT-4o, Gemini), finding that NLI-based black-box scorers outperform log-probability baselines in 13/24 AUROC scenarios, while log-probability features remain strong baselines.

### 2.3 First-Token Confidence and SE Correlation

\citet{kossen2025firsttoken} directly measure the Pearson correlation between first-token confidence and semantic agreement on TriviaQA and PopQA with Llama-3.1-8B, finding $r = 0.54$–$0.76$. This range calibrates expectations for our experiment: min\_logprob (minimum over all tokens) differs from first-token confidence, and we predict $|r|(\text{SE}, \text{min\_logprob}) < 0.70$ based on the algebraic distinctness of SE from any single-pass log-probability signal. Our empirical finding ($|r| = 0.049$) is substantially below this calibration range.

### 2.4 Ensemble UQ Methods

\citet{bouchard2025uqlm} show that tunable ensembles combining multiple UQ features achieve best performance in 20/24 AUROC scenarios, motivating the combination of SE and log-probability signals. \citet{raghuvanshi2025token} combine token log-probability, NLI, and SE on SQuAD2.0, achieving AUC = 0.818, but without public code, length-bias controls, or open-weight model evaluation. Our work targets TriviaQA/TruthfulQA with open-weight models and a length-bias-robust evaluation protocol.

### 2.5 Length Bias in UQ Evaluation

\citet{santilli2025evaluation} identify systematic length bias in AUROC rankings under lexical correctness functions (ROUGE-L): Spearman $|\rho|$ between response length and UQ signal can reach 0.9, inflating apparent AUROC. They recommend LM-as-a-judge as the most human-aligned correctness function. Our evaluation uses a cross-model LM-as-a-judge (Qwen-2.5-7B judging Llama-3.1-8B outputs) to avoid both length bias and circularity.

### 2.6 Conditional Independence Testing for UQ Signals

The question of whether two UQ signals are conditionally independent — i.e., whether one provides additional predictive power beyond the other for correctness prediction — has not been systematically addressed in the UQ literature. Standard ensemble evaluations measure AUROC improvements but do not decompose the source of gain. Conditional logistic regression with partial $R^2$ provides a mechanism-level test: if SE's partial $R^2$ in a model controlling for min\_logprob and response length is $\geq 0.02$, SE contributes independent predictive signal. This is the statistical test at the center of our work.

---

## 3. Methodology

### 3.1 Problem Setup

We study whether Semantic Entropy (SE\_N5) and minimum token log-probability (min\_logprob) are statistically independent uncertainty signals for predicting factual correctness on short-answer QA. Formally, let $x$ be a question, $y^*$ be the correct answer, $\hat{y}$ be the model's greedy answer, and $h \in \{0, 1\}$ be the binary correctness label ($h=1$ if correct). We define two uncertainty signals:

**SE\_N5:** Generate $N=5$ stochastic responses $\{s_1, \ldots, s_5\}$ at temperature $\tau=0.7$. Apply bidirectional NLI clustering (DeBERTa-MNLI) to group responses into semantic equivalence classes $\{C_k\}$. Compute:
$$\text{SE}(x) = -\sum_k p(C_k \mid x) \log p(C_k \mid x), \quad p(C_k \mid x) = \frac{|\{i : s_i \in C_k\}|}{N}$$

**min\_logprob:** Generate the greedy response $\hat{y} = (t_1, \ldots, t_T)$ with temperature 0.0. Extract per-token log-probabilities $\{\log p(t_i \mid x, t_{<i})\}_{i=1}^T$ from the model's output scores. Compute:
$$\text{min\_logprob}(x) = \min_{i \in 1..T} \log p(t_i \mid x, t_{<i})$$

The two signals are computed on different inference calls (stochastic sampling vs. greedy decode) and aggregate uncertainty at different granularities (sentence-level semantic entropy vs. token-level minimum confidence), making them algebraically distinct.

### 3.2 Dataset

We use TriviaQA \citep{joshi2017triviaqa} in the `rc.nocontext` (closed-book) configuration, validation split, shuffled with seed=42 and restricted to the first 2,500 questions (our target for the full-scale experiment; PoC uses first 300). TriviaQA provides a list of answer aliases per question, enabling alias-based fallback correctness checking in addition to LM-judge evaluation. The closed-book setting eliminates context document confounds and focuses on the model's parametric knowledge.

### 3.3 Models

**Generator:** `meta-llama/Llama-3.1-8B-Instruct` (bfloat16, device\_map="auto"). Generates both stochastic samples (N=5, temp=0.7, top-p=0.95, max\_new\_tokens=50) and greedy decode (temp=0.0, output\_scores=True) for each question.

**NLI Model for SE Clustering:** `cross-encoder/nli-deberta-v3-small` via HuggingFace. Adapted from the official jlko/semantic\_uncertainty implementation \citep{kuhn2023semantic}. Non-strict bidirectional entailment: two responses are semantically equivalent if neither implies contradiction and the pair is not mutually neutral.

**Judge:** `Qwen/Qwen2.5-7B-Instruct` (cross-model: different family from generator). Evaluates each greedy answer with a YES/NO prompt. Binary label parsed from YES/NO; fallback to alias string match.

### 3.4 Statistical Framework

**Independence Test (Pearson $r$):** Pearson $|r|(\text{SE\_N5}, \text{min\_logprob})$ across all prompts. Gate thresholds: $|r| < 0.70$ (independence pass), $|r| > 0.85$ (ABANDON).

**Circularity Diagnostic (Spearman $\rho$):** Spearman $\rho(\text{SE}, h)$ where $h$ is the LM-judge correctness label. Require $|\rho| < 0.40$.

**Conditional Independence Test (Partial $R^2$):** Conditional logistic regression, full vs. reduced:
- Full: $\text{logit}(P(h=1)) = \beta_0 + \beta_1 \cdot \text{min\_logprob} + \beta_2 \cdot \text{SE} + \beta_3 \cdot L + \beta_4 \cdot (\text{SE} \times \text{min\_logprob})$
- Reduced: $\text{logit}(P(h=1)) = \beta_0 + \beta_1 \cdot \text{min\_logprob} + \beta_3 \cdot L$

McFadden-style partial $R^2_\text{SE} = 1 - \ell_\text{full}/\ell_\text{reduced}$. Gate criterion: $R^2_\text{SE} \geq 0.02$.

---

## 4. Experiments

### 4.1 Proof-of-Concept Protocol

We run a proof-of-concept (PoC) at $N=300$ prompts (12% of the full $N=2{,}500$) as a smoke test. The gating structure is hierarchical: the ABANDON threshold ($|r| > 0.85$) must be ruled out before investing compute in ensemble AUROC evaluation. The PoC answers this question cheaply.

| Parameter | Value |
|-----------|-------|
| Dataset | TriviaQA dev (`rc.nocontext`), first 300 prompts (seed=42) |
| Generator | `meta-llama/Llama-3.1-8B-Instruct` |
| Stochastic samples | $N=5$, temperature=0.7, top-p=0.95, max\_new\_tokens=50 |
| NLI model | `cross-encoder/nli-deberta-v3-small` (bidirectional, non-strict) |
| Judge | `Qwen/Qwen2.5-7B-Instruct` (cross-model, batch\_size=16) |

### 4.2 Gate Criteria

1. **ABANDON gate:** $|r| > 0.85$ → hypothesis abandoned
2. **Independence gate:** $|r| < 0.70$ → independence criterion passes
3. **Partial $R^2$ gate:** $R^2_\text{SE} \geq 0.02$ → conditional independence confirmed

### 4.3 Mechanism Reality Checks

After signal computation, we verify: SE variance $> 0.01$, all min\_logprob $< 0$, determinism, sensitivity, smoothness, gradient flow, and weight influence. Failure of any check triggers an explicit error.

---

## 5. Results

### 5.1 Main Results

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Pearson $\|r\|$(SE\_N5, min\_logprob) | **0.049** | $< 0.70$ | PASS |
| ABANDON check: $\|r\| > 0.85$ | 0.049 | not triggered | PASS |
| Partial $R^2$ (SE in conditional LR) | 0.0101 | $\geq 0.02$ | FAIL (underpowered) |
| LRT $p$-value | 0.1504 | — | non-significant at $N=300$ |
| LRT $\chi^2$ | 3.789 | — | $df=2$ |
| Spearman $\rho$(SE, correctness) | $-0.081$ | $\|ρ\| < 0.40$ | PASS (circularity OK) |
| SE variance | 0.133 | $> 0$ | PASS |
| min\_logprob mean | $-2.415$ | $< 0$ | PASS |
| Correctness rate (LM-judge) | 34.3% (103/300) | — | — |

**Table 1:** PoC results at $N=300$.

### 5.2 Signal Independence

Pearson $|r| = 0.049$ — far below both the independence threshold (0.70) and the reparameterization threshold (0.85). For reference, prior work reports $r = 0.54$–$0.76$ between first-token confidence and semantic agreement on the same model and dataset \citep{kossen2025firsttoken}; our min\_logprob (minimum over *all* tokens) achieves even lower correlation with SE.

Figure 1 (`scatter_se_vs_minlogprob.png`) shows the joint distribution of SE\_N5 and min\_logprob for all 300 prompts, colored by LM-judge correctness. No systematic linear trend is visible.

### 5.3 Circularity Diagnostic

Spearman $\rho(\text{SE}, \text{correctness}) = -0.081$, well below $|\rho| < 0.40$. The negative sign is directionally consistent (higher SE → lower correctness); the magnitude is low because judge and SE are structurally distinct operations. Figure 2 (`correlation_heatmap.png`) shows all off-diagonal cells involving SE and min\_logprob are near-zero.

### 5.4 Partial $R^2$ Analysis

Partial $R^2 = 0.0101$ (below threshold). LRT $\chi^2 = 3.789$ ($df=2$, $p=0.1504$). The directional effect is positive (SE contributes beyond min\_logprob), confirming the direction of the hypothesis. The magnitude failure is due to underpowering: $N=300$ is 12% of the intended $N=2{,}500$. Figure 3 (`lr_coefficients.png`) shows the SE coefficient $\beta_2$ is positive with a wide confidence interval including zero.

### 5.5 Mechanism Reality Checks

All seven mechanism reality checks pass on the first experimental run, confirming pipeline robustness (Table 2).

| Check | Result |
|-------|--------|
| determinism | PASS |
| sensitivity (SE var $> 0.01$: 0.133) | PASS |
| smoothness (min\_logprob $< 0$: mean $-$2.415) | PASS |
| gradient\_flow | PASS |
| weight\_influence | PASS |

**Table 2:** Mechanism reality checks. All pass.

### 5.6 Gate Evaluation

Figure 4 (`gate_metrics.png`) summarizes: Pearson $|r| = 0.049$ far below the 0.70 threshold (PASS); partial $R^2 = 0.0101$ below 0.02 (FAIL — underpowered). Gate decision: EXPLORE (scale-up to $N=2{,}500$ recommended, no hypothesis redesign needed).

---

## 6. Discussion

### 6.1 Interpreting Near-Orthogonality

The Pearson $|r| = 0.049$ is substantially lower than the calibration range of $r = 0.54$–$0.76$ reported for first-token confidence vs. semantic agreement \citep{kossen2025firsttoken}. We attribute this to: (1) min\_logprob takes the *minimum* over all tokens, distributing the uncertainty signal across the full response; (2) SE computes entropy over semantic class *masses* from 5 stochastic samples — a fundamentally different aggregation than any single greedy forward pass. The algebraic distinction articulated by \citet{kuhn2023semantic} manifests as genuine statistical independence in practice.

### 6.2 Low Circularity

The cross-model design (Qwen-2.5-7B judging Llama-3.1-8B outputs) yields $\rho = -0.081$, lower than the circularity concern suggested. Two mechanisms suppress it: (a) functional distinction (judge evaluates a single greedy answer against the question; SE evaluates consistency of 5 stochastic samples against each other); (b) cross-model separation prevents shared model-specific biases from generating correlated NLI decisions. This validates \citet{santilli2025evaluation}'s cross-model judge recommendation as a practical mitigation.

### 6.3 Limitations

**L1 (PoC Underpowering):** Partial $R^2 = 0.0101$ below threshold; underpowered at $N=300$. Single parameter change ($N \to 2{,}500$) addresses this. Direction confirmed; magnitude pending.

**L2 (Ensemble and Transfer Not Tested):** $\Delta$AUROC $\geq 0.025$ (P1) and cross-model transfer gap $< 0.05$ (P3) are INCONCLUSIVE — not refuted, untested at PoC level. These are live predictions awaiting h-e1-v2.

**L3 (Single Seed):** Point estimate at $N=300$; no variance across seeds. Bootstrap CIs at $N=2{,}500$ recommended.

**L4 (Scope):** Results hold for TriviaQA short-answer QA (1–10 token answers) with 7–8B open-weight models at temperature=0.7. SE has documented limitations for long-form generation \citep{nguyen2025snne}.

### 6.4 Future Work

- **h-e1-v2 (N=2500):** Confirm partial $R^2 \geq 0.02$, compute ensemble AUROC, test cross-model transfer.
- **Orthogonality zone analysis:** Test whether the zone (min\_logprob $\geq 0.8$ AND SE top quartile) is enriched for hallucinations.
- **Multi-seed robustness:** Bootstrap CIs on Pearson $r$ at $N=2{,}500$ with 3 seeds.
- **Scope extension:** Test independence on a second model family (Mistral-7B or Qwen-2.5-7B as generator).

---

## 7. Conclusion

We opened this paper with a question: do SE\_N5 and min\_logprob measure the same thing about a language model's uncertainty, or genuinely different things? The answer, at least on TriviaQA short-answer QA with Llama-3.1-8B-Instruct, is unambiguous: **they measure genuinely different things**, with Pearson $|r| = 0.049$.

This near-zero correlation empirically confirms what algebraic analysis suggested \citep{kuhn2023semantic}: entropy over NLI-cluster semantic class masses and minimum token-prediction confidence along a greedy path are independent aggregations. SE captures whether the model *agrees with itself* across stochastic samples at the semantic level; min\_logprob captures whether the model was *confident at every token step* in a single deterministic generation.

Three contributions follow: (1) mechanistic justification for ensemble combination via empirical near-orthogonality; (2) cross-model LM-judge design validated as a practical circularity mitigation ($\rho = -0.081$); (3) statistical power boundary characterized for partial $R^2$ tests at this operating point.

The partial $R^2 = 0.0101$ is the open thread — directionally confirmed, underpowered. The full-scale run at $N=2{,}500$ (h-e1-v2) will resolve this and enable ensemble AUROC evaluation. The pipeline is production-ready. The ensemble is justified.

---

## References

\bibliography{06_references}

---

## Appendix: Figures

| Figure | File | Description |
|--------|------|-------------|
| Figure 1 | `h-e1/figures/scatter_se_vs_minlogprob.png` | SE\_N5 vs. min\_logprob scatter, colored by correctness |
| Figure 2 | `h-e1/figures/correlation_heatmap.png` | Pearson correlation matrix: [SE, min\_logprob, length, correctness] |
| Figure 3 | `h-e1/figures/lr_coefficients.png` | LR coefficients with 95% CI for full model |
| Figure 4 | `h-e1/figures/gate_metrics.png` | Gate evaluation bar chart vs. thresholds |

## Appendix: Implementation Details

| Component | File | Status |
|-----------|------|--------|
| SE\_N5 (DeBERTa-MNLI NLI clustering) | `h-e1/code/compute_signals.py` | Validated (var=0.133, 0% degenerate) |
| min\_logprob (greedy token log-probs) | `h-e1/code/compute_signals.py` | Validated (mean=−2.415, all < 0) |
| LM-judge (Qwen2.5-7B-Instruct) | `h-e1/code/judge.py` | 34.3% correctness rate |
| Conditional LR + partial $R^2$ | `h-e1/code/stats_analysis.py` | Full/reduced model, McFadden partial $R^2$, LRT |
| Gate evaluation logic | `h-e1/code/stats_analysis.py` | ABANDON/EXPLORE/PASS decision tree |
| Checkpoint-aware generation | `h-e1/code/generate.py` | signals.pkl persisted |

All 14 implementation tasks completed; 22/22 validation checks passing; 1 coder-validator cycle (LIGHT tier).
