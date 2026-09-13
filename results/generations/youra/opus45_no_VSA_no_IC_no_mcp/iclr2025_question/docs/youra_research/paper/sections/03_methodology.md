# Methodology

Building on our observation that entropy and consistency may capture orthogonal failure modes, we design an experimental framework to test this hypothesis systematically. Our methodology enables fair comparison by computing both signals on identical model outputs.

## Overview

We compute two uncertainty signals for each question-answer pair:

1. **Token Entropy:** Mean entropy over generated tokens, capturing epistemic uncertainty in next-token prediction
2. **N-Sample Consistency:** Mean pairwise cosine similarity of response embeddings, capturing generation stability

We then analyze:
- Individual predictive validity (AUROC for hallucination detection)
- Signal orthogonality (Pearson correlation)
- Complementary value on discordant cases

## Token Entropy Computation

**Rationale:** When a model lacks knowledge about the correct answer, its logit distribution over next tokens becomes diffuse (high entropy). Conversely, confident knowledge produces peaked distributions (low entropy).

For a generated response with tokens $t_1, ..., t_n$, we compute token entropy as:

$$H(t_i) = -\sum_{v \in V} p(v | t_{<i}) \log p(v | t_{<i})$$

where $V$ is the vocabulary and $p(v | t_{<i})$ is the softmax probability from the model's logits.

**Aggregation:** We use mean entropy over response tokens:

$$H_{response} = \frac{1}{n} \sum_{i=1}^{n} H(t_i)$$

Mean aggregation is robust to response length variations and captures overall uncertainty rather than worst-case token uncertainty.

**Implementation Details:**
- Greedy decoding with `output_scores=True` to access logits
- Numerical stability via `clamp(min=1e-10)` before log computation
- Maximum response length: 100 tokens

## N-Sample Consistency Computation

**Rationale:** When a model's knowledge is unstable or fabricated, repeated sampling produces semantically divergent responses. Stable knowledge yields consistent answers across samples.

For N independently sampled responses to the same question, we:

1. Generate N responses with temperature sampling (T=1.0)
2. Encode each response using a sentence embedding model
3. Compute pairwise cosine similarity
4. Average to get consistency score

$$C = \frac{2}{N(N-1)} \sum_{i < j} \text{cos}(e_i, e_j)$$

where $e_i$ is the embedding of response $i$.

**Design Choices:**
- **N=5 samples:** Balances computational cost with estimate stability (following SelfCheckGPT)
- **Temperature=1.0:** Maximizes sampling diversity to reveal underlying instability
- **Embedding model:** sentence-transformers/all-MiniLM-L6-v2 for computational efficiency

## Ground Truth Labels

We use TruthfulQA's generation split (817 questions) with factuality labels derived from BERTScore comparison between model response and reference answers:

- **Correct:** BERTScore F1 ≥ 0.5 with best_answer
- **Incorrect:** BERTScore F1 < 0.5 with best_answer

This provides a binary classification target for AUROC computation.

## Orthogonality Analysis

To test whether entropy and consistency capture different information:

**Correlation Analysis:**
- Compute Pearson r between (entropy, 1-consistency) across all questions
- Threshold: r < 0.3 indicates orthogonal signals (< 9% shared variance)

**Discordant Case Analysis:**
- Identify questions where entropy rank differs from consistency rank by >50 percentile points
- Compute AUROC for each method on its "winning" subset
- Threshold: >15% discordant cases with winning-method AUROC >0.6

This analysis determines whether combining signals could provide complementary value beyond what either achieves alone.

## Statistical Validation

- **Effect size:** Cohen's d with pooled standard deviation
- **Significance testing:** Mann-Whitney U test (one-sided) for group comparisons
- **Confidence intervals:** 95% CI via bootstrap (1000 iterations)
- **AUROC:** Area under ROC curve with bootstrap confidence intervals

## Experimental Workflow

```
Input: TruthfulQA questions (N=817)
       LLaMA-2-7B model

For each question:
  1. Generate greedy response → compute token entropy
  2. Generate 5 sampled responses → compute consistency
  3. Compute BERTScore label (correct/incorrect)

Analysis:
  1. Compute AUROC for entropy, consistency
  2. Compute correlation(entropy, 1-consistency)
  3. Identify discordant cases
  4. Compute subset AUROC for each method
```

This design directly tests our hypotheses: H-M1 (entropy-uncertainty link), H-M2 (consistency-stability link), and H-M3 (orthogonality and complementarity).
