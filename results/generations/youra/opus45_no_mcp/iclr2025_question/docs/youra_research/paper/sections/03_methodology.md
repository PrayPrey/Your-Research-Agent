# Methodology

We design a controlled experiment to compare token entropy and semantic consistency as hallucination predictors, then test whether their combination improves detection. Our evaluation uses standard benchmark data, a representative open-source model, and established metrics.

## Dataset

We use **TriviaQA** (Joshi et al., 2017), specifically the `rc.nocontext` split from HuggingFace (`mandarjoshi/trivia_qa`). This configuration presents questions without accompanying documents, testing the model's parametric knowledge rather than reading comprehension.

TriviaQA provides ground-truth answers for each question, enabling automatic evaluation of response correctness. The validation set contains approximately 11,000 questions; for our proof-of-concept experiments, we sample subsets ranging from N=20 (fusion experiments) to N=100 (entropy/consistency correlation experiments) due to computational constraints.

**Correctness labeling:** A response is marked correct if it achieves either (1) exact match with any reference answer after normalization (lowercasing, punctuation removal), or (2) token-level F1 > 0.5 with the reference. This lenient criterion accommodates paraphrased correct answers.

## Model

We use **Llama-2-7B-chat** (`meta-llama/Llama-2-7b-chat-hf` from HuggingFace), an instruction-tuned variant of the Llama-2 7B base model. This model represents a widely-deployed class of open-source LLMs with full logit access, enabling entropy computation.

We select a 7B parameter model for computational tractability on single-GPU hardware. While larger models (13B, 70B) may exhibit different calibration properties, Llama-2-7B-chat provides a representative baseline for instruction-tuned LLM behavior.

## Response Generation

For each question, we generate **10 independent responses** using nucleus sampling with the following parameters:

- Temperature: 0.7
- Top-p: 0.95
- Max new tokens: 128
- Random seed: 42 (for reproducibility)

Prompt format follows the Llama-2-chat template:
```
[INST] {question} [/INST]
```

We generate 10 samples rather than a smaller number (e.g., 5) to provide sufficient data for stable consistency estimation. Each sample is generated independently with fresh randomness, not as continuations of previous samples.

## Token Entropy Computation

For each generated response, we compute **Shannon entropy** from the token-level softmax distributions:

$$H(y_t) = -\sum_{v \in V} p(v | y_{<t}) \log p(v | y_{<t})$$

where $V$ is the vocabulary, $y_t$ is the token at position $t$, and $p(v | y_{<t})$ is the softmax probability of token $v$ given the preceding context.

We aggregate token-level entropies by taking the **mean across all generated tokens** in the response:

$$H_{\text{response}} = \frac{1}{T} \sum_{t=1}^{T} H(y_t)$$

For each question, we then average across all 10 generated responses to obtain a single entropy score:

$$H_{\text{question}} = \frac{1}{10} \sum_{i=1}^{10} H_{\text{response}_i}$$

Higher entropy indicates greater internal uncertainty. For fusion with consistency (where higher is better), we use **confidence** = 1 - normalized_entropy.

## Semantic Consistency Computation

We measure consistency via **pairwise embedding similarity** across the 10 generated responses:

1. Encode each response using SentenceTransformer (`all-MiniLM-L6-v2`), producing a 384-dimensional embedding.
2. Compute cosine similarity between all pairs of response embeddings (45 pairs for 10 responses).
3. Average pairwise similarities to obtain the consistency score:

$$\text{Consistency} = \frac{2}{n(n-1)} \sum_{i<j} \cos(\mathbf{e}_i, \mathbf{e}_j)$$

where $\mathbf{e}_i$ is the embedding of response $i$ and $n=10$.

Higher consistency indicates that the model produces semantically similar responses across samples, suggesting reliable knowledge. Lower consistency indicates divergent responses, suggesting hallucination-prone behavior.

We choose embedding similarity over alternatives (BERTScore, NLI-based entailment) for computational efficiency. The all-MiniLM-L6-v2 model provides a good balance of quality and speed for semantic similarity tasks.

## Linear Fusion

To test whether combining entropy and consistency improves detection, we apply **linear fusion**:

$$\text{Score} = \alpha \cdot \text{Confidence} + \beta \cdot \text{Consistency}$$

where Confidence = 1 - normalized_entropy (so higher is better for both terms).

We normalize both signals to [0, 1] range using min-max scaling on the evaluation set before fusion. Weights $\alpha$ and $\beta$ are determined via grid search over the range [0, 1] with step size 0.1, using a held-out validation split (10% of data, 2 questions for N=20) to select optimal weights and evaluating on the remaining test set.

## Evaluation Metrics

**Primary metric: AUROC (Area Under ROC Curve).** AUROC measures the probability that a randomly chosen correct response ranks higher (more confident/consistent) than a randomly chosen incorrect response. AUROC=0.5 indicates random performance; AUROC=1.0 indicates perfect discrimination.

We prefer AUROC over accuracy because it is threshold-independent and captures the full ranking quality of the uncertainty signal.

**Effect size: Cohen's d.** To quantify practical significance beyond statistical significance, we compute Cohen's d between the distributions of scores for correct and incorrect responses:

$$d = \frac{\mu_{\text{correct}} - \mu_{\text{incorrect}}}{s_{\text{pooled}}}$$

where $s_{\text{pooled}}$ is the pooled standard deviation. Cohen's d > 0.8 indicates a large effect; 0.5-0.8 indicates medium; 0.2-0.5 indicates small.

**Statistical tests:** We use two-tailed independent-samples t-tests to assess whether score distributions differ significantly between correct and incorrect responses. We report p-values with significance threshold p < 0.05.

**Correlation analysis:** To assess signal redundancy, we compute Pearson correlation between entropy and consistency scores across questions. High correlation (|r| > 0.7) would indicate redundant signals with limited fusion benefit.

## Experimental Procedure

1. **H-E1 (Existence):** Verify that entropy and consistency are computable for all questions with meaningful variance.

2. **H-M1 (Entropy validation):** Compute entropy for N=100 questions; test whether incorrect responses have significantly higher entropy than correct responses.

3. **H-M2 (Consistency validation):** Compute consistency for N=20 questions; test whether correct responses have significantly higher consistency than incorrect responses.

4. **H-M3 (Fusion test):** Apply linear fusion on N=20 questions with grid search for optimal weights; compare AUROC of fusion versus best single metric.

We adopt an incremental verification strategy where each hypothesis builds on the previous one. If H-E1 fails (metrics not computable), we cannot proceed. If H-M1 or H-M2 fail (individual signals not predictive), combination is unlikely to help.

## Limitations of Experimental Design

**Sample size:** Our fusion experiments (H-M3) use only N=20 questions due to computational constraints. This limits statistical power and may cause grid search to overfit, potentially explaining why optimal weights collapsed to pure consistency (alpha=0).

**Single model:** We test only Llama-2-7B-chat. Results may differ for larger models or different architectures.

**Single dataset:** We test only TriviaQA. Cross-dataset validation (NaturalQuestions, TruthfulQA) is deferred to future work.

These limitations are acceptable for proof-of-concept evaluation validating that individual signals work; definitive conclusions about fusion require larger-scale experiments.
