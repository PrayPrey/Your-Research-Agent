# Related Work

## Semantic Entropy and NLI-Based Uncertainty

\citet{kuhn2023semantic} introduced Semantic Entropy (SE) as an uncertainty measure that computes entropy over the distribution of semantic equivalence classes, where classes are formed by grouping $N$ stochastic model samples via bidirectional NLI entailment checks. Formally, let $C_k$ denote semantic cluster $k$; then $\text{SE} = -\sum_k p(C_k \mid x) \log p(C_k \mid x)$, where $p(C_k \mid x) = \sum_{s \in C_k} p(s \mid x)$ (Eq. 3 in \citet{kuhn2023semantic}). On TriviaQA with a 30B OPT model, SE achieves AUROC = 0.83 for predicting answer correctness. Crucially, SE does not use token log-probabilities in its computation — it marginalizes over semantic class frequencies derived from sampling, making it algebraically distinct from likelihood-based signals.

## Minimum Token Log-Probability

Token log-probability signals have a long history in confidence calibration \citep{malinin2020uncertainty}. \citet{manakul2023selfcheckgpt} used the minimum token probability as a ``weakest link'' detector — the intuition being that a single highly uncertain token in a generated response often marks the factually unreliable segment. \citet{bouchard2025uqlm} (UQLM) benchmark a suite of white-box and black-box UQ scorers across 6 benchmarks and 4 LLMs (GPT-4o, Gemini), finding that NLI-based black-box scorers outperform log-probability baselines in 13/24 AUROC scenarios, while log-probability features remain strong baselines.

## First-Token Confidence and SE Correlation

\citet{kossen2025firsttoken} directly measure the Pearson correlation between first-token confidence and semantic agreement on TriviaQA and PopQA with Llama-3.1-8B, finding $r = 0.54$–$0.76$. This range calibrates expectations for our experiment: min\_logprob (minimum over all tokens) differs from first-token confidence, and we predict $|r|(\text{SE}, \text{min\_logprob}) < 0.70$ based on the algebraic distinctness of SE from any single-pass log-probability signal. Our empirical finding ($|r| = 0.049$) is substantially below this calibration range.

## Ensemble UQ Methods

\citet{bouchard2025uqlm} show that tunable ensembles combining multiple UQ features achieve best performance in 20/24 AUROC scenarios, motivating the combination of SE and log-probability signals. \citet{raghuvanshi2025token} combine token log-probability, NLI, and SE on SQuAD2.0, achieving AUC = 0.818, but without public code, length-bias controls, or open-weight model evaluation. Our work targets TriviaQA/TruthfulQA with open-weight models and a length-bias-robust evaluation protocol.

## Length Bias in UQ Evaluation

\citet{santilli2025evaluation} identify systematic length bias in AUROC rankings under lexical correctness functions (ROUGE-L): Spearman $|\rho|$ between response length and UQ signal can reach 0.9, inflating apparent AUROC. They recommend LM-as-a-judge as the most human-aligned correctness function. Our evaluation uses a cross-model LM-as-a-judge (Qwen-2.5-7B judging Llama-3.1-8B outputs) to avoid both length bias and circularity.

## Cross-Model Evaluation and Circularity

When the judge and generator share model weights or model family, their shared biases can create circularity: the judge may agree with the generator not because the answer is correct, but because both models make similar errors. \citet{santilli2025evaluation} recommend cross-model judges to break this bias. We operationalize this by using Qwen-2.5-7B-Instruct as judge when Llama-3.1-8B-Instruct is the generator, verifying low circularity via Spearman $\rho$(SE, judge correctness) = $-$0.081.

## Conditional Independence Testing for UQ Signals

The question of whether two UQ signals are conditionally independent — i.e., whether one provides additional predictive power beyond the other for correctness prediction — has not been systematically addressed in the UQ literature. Standard ensemble evaluations measure AUROC improvements but do not decompose the source of gain. Conditional logistic regression with partial $R^2$ provides a mechanism-level test: if SE's partial $R^2$ in a model controlling for min\_logprob and response length is $\geq 0.02$, SE contributes independent predictive signal. This is the statistical test at the center of our work.
