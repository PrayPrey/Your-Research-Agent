# Methodology

The central claim of this paper is that Semantic Entropy (SE\_N5) and minimum log-probability (min\_logprob) are near-orthogonal uncertainty signals for open-weight LLMs on short-answer factual QA. To test this claim rigorously, we need: (1) precise definitions of each signal that make their algebraic distinction explicit, (2) a direct independence test protocol with pre-registered thresholds, and (3) a circularity-controlled evaluation design that prevents confounds between the signals and the correctness labels. We describe each in turn.

## Signal Definitions

**Semantic Entropy (SE\_N5).** Following Kuhn et al. [2023], we define Semantic Entropy as the Shannon entropy over semantic equivalence classes:

$$\text{SE} = H(p(C|x)) = -\sum_{C \in \mathcal{C}} p(C|x) \log p(C|x)$$

where $p(C|x) = \sum_{s \in C} p(s|x)$ aggregates the token-probability mass of all N=5 stochastic samples $s$ within each NLI-defined semantic cluster $C$. Clusters are formed by bidirectional NLI entailment: two samples $s_i$ and $s_j$ are in the same cluster if and only if $\text{NLI}(s_i, s_j) = \text{ENTAIL}$ AND $\text{NLI}(s_j, s_i) = \text{ENTAIL}$, using `cross-encoder/nli-deberta-v3-small` as the NLI backbone.

**Why this design:** SE operates over N=5 stochastic samples (temperature=0.7, top-p=0.95), aggregating uncertainty at the semantic, sentence level. It explicitly does not depend on token-level probabilities from the greedy decode path; it uses sample probability masses $p(s|x)$ derived from the stochastic sampling distribution.

**Minimum Log-Probability (min\_logprob).** We define min\_logprob as:

$$\text{min\_logprob} = \min_{t \in [1,T]} \log p(w_t | w_{<t}, x)$$

where the minimum is taken over all tokens $w_t$ in the greedy decode output of length $T$.

**Why this design:** min\_logprob captures the "weakest link" in the model's token-level confidence chain. Unlike first-token probability (which only measures confidence at position 1), min\_logprob is sensitive to any position in the answer where the model hesitates — factually uncertain token positions, rare entity names, or complex phrases. Critically, min\_logprob is computed from a single greedy decoding pass that is **separate** from the N=5 stochastic sampling passes used for SE. The two signals access different inference computations over different output distributions.

**Algebraic Distinctness.** The near-orthogonality claim follows from two structural differences: (a) SE aggregates uncertainty over the semantic clustering distribution of N stochastic outputs, while min\_logprob aggregates uncertainty as the minimum over a greedy-path token sequence; (b) SE is computed on stochastic samples (temperature > 0) while min\_logprob is computed on the greedy decode (temperature = 0 / argmax). The operations are not mathematically reducible to each other, motivating the empirical test.

## Independence Test Protocol

We test independence with two complementary statistics, with pre-registered thresholds:

**Gate 1 — Pearson Correlation Test:**
- Null: SE\_N5 and min\_logprob are linearly independent, |r| < 0.70.
- **PASS** if |r| < 0.70 (independence confirmed).
- **ABANDON** if |r| > 0.85 (SE is effectively a reparameterization of min\_logprob; ensemble unjustified).
- **EXPLORE** if 0.70 ≤ |r| ≤ 0.85 (moderate correlation; requires N=10 ablation).

**Gate 2 — Conditional Logistic Regression (Partial R²):**
We fit a conditional logistic regression predicting LM-judge correctness:

$$\text{logit}(h=1) \sim \beta_0 + \beta_1 \cdot \text{min\_logprob} + \beta_2 \cdot \text{SE} + \beta_3 \cdot L + \beta_4 \cdot (\text{SE} \times \text{min\_logprob})$$

where $L$ is response length (log-token count). The partial R² for the SE term is computed as McFadden pseudo-R²(full model) − McFadden pseudo-R²(reduced model without SE and interaction), and tested via Likelihood Ratio Test (LRT) against the chi-squared distribution with 2 degrees of freedom.

- **PASS** if partial R²(SE) ≥ 0.02 AND LRT p < 0.05.
- Note: At N=2500, this gate has adequate power to detect the pre-registered partial R² ≥ 0.02 effect size.

## Circularity Control Design

**Cross-Model LM-Judge.** A key validity concern for SE-based UQ evaluation is that SE (which uses NLI-based semantic reasoning) might circularly correlate with LM-judge correctness labels (which also apply semantic reasoning to evaluate answers). We mitigate this by using a **cross-model judge**: Qwen-2.5-7B-Instruct evaluates Llama-3.1-8B-Instruct outputs. Shared model-specific NLI biases cannot propagate between different model families, preventing systematic circular agreement.

**Circularity Diagnostic.** We measure Spearman ρ(SE, judge\_correctness) as a post-hoc diagnostic. Pre-registered threshold: |ρ| < 0.40. Values above this threshold indicate problematic circularity.

## Experimental Protocol

**Dataset:** TriviaQA dev (rc.nocontext), HuggingFace dataset `mandarjoshi/trivia_qa`, first N=2500 prompts (seed=42). The no-context variant was selected to focus on the model's parametric knowledge without retrieval augmentation, following the h-m1 baseline configuration.

**Generator:** Llama-3.1-8B-Instruct (bfloat16, device\_map="auto"). N=5 stochastic samples per prompt (temperature=0.7, top\_p=0.95, max\_new\_tokens=50). One greedy decode per prompt (temperature=0, max\_new\_tokens=50) for min\_logprob extraction.

**NLI Backbone:** `cross-encoder/nli-deberta-v3-small` for bidirectional NLI clustering. Batch size 32 for GPU memory efficiency.

**LM-Judge:** Qwen-2.5-7B-Instruct evaluates each greedy answer against TriviaQA aliases. A structured prompt requests a binary correctness label ("correct" / "incorrect"). Batch size 16.

**Mechanism Reality Checks.** Before analysis, we verify: (1) SE variance > 0.01 (non-degenerate signal); (2) fraction\_degenerate = 0 (no all-same-cluster prompts); (3) min\_logprob < 0 (valid log probabilities); (4) determinism (identical inputs → identical SE scores); (5) sensitivity (high-entropy vs. low-entropy prompts differ significantly).

**Experimental Scale.** The evaluation runs on N=2500 prompts — the full intended evaluation scale. This provides adequate statistical power to assess both the independence test (Gate 1, Pearson r) and the conditional predictive contribution test (Gate 2, partial R² in logistic regression). Ensemble AUROC evaluation is reserved for follow-up work contingent on a positive Gate 2 result.

## Implementation

The implementation is structured as six modules: `config.py` (hyperparameters, paths, thresholds), `generate.py` (checkpoint-aware stochastic + greedy generation), `compute_signals.py` (SE\_N5 + min\_logprob computation), `judge.py` (Qwen-2.5-7B LM-judge labeling), `stats_analysis.py` (Pearson r, conditional LR, partial R², gate evaluation), and `visualize.py` (four paper-ready figures). A checkpoint-aware pipeline saves signals to `results/signals.pkl` after generation, enabling restart without re-running the 8B generator. GPU memory is managed explicitly (`del model; torch.cuda.empty_cache()`) between generator and judge model loads.
