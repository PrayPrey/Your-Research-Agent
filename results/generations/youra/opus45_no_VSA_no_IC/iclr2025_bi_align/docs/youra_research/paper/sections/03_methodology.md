# Methodology

## Dataset

We use the LMSYS Chatbot Arena dataset (`lmsys/lmsys-arena-human-preference-55k`), containing 57,477 pairwise battles between LLM responses. Each battle includes a prompt, two model responses (A and B), and human preference votes. This dataset enables computation of human vote entropy at the model-pair level and comparison with reward model scores.

## Human Vote Entropy

For each model pair (e.g., GPT-4 vs Claude-2), we compute Shannon entropy over the vote distribution:

$$H = -\sum_{i \in \{A, B, \text{tie}\}} p_i \log_2 p_i$$

where $p_i$ is the proportion of votes for outcome $i$. Entropy ranges from 0 (complete consensus) to log₂(3) ≈ 1.58 (uniform distribution across three outcomes). High entropy indicates human disagreement; low entropy indicates consensus.

We binarize entropy using median split: battles with entropy above the median are classified as "high entropy" (human disagreement), those below as "low entropy" (human consensus).

## Reward Model Variance Proxy

Ideally, RM variance would derive from an ensemble of 3+ reward models scoring each response pair. Due to computational constraints, we use a single reward model (OpenAssistant-reward-model) and compute the absolute score difference between responses:

$$\text{variance\_proxy} = |RM(A) - RM(B)|$$

Low score difference indicates the RM finds responses similar (low confidence in preference); high difference indicates strong preference (high confidence). We invert this for variance interpretation: low difference → high variance (uncertainty), high difference → low variance (confidence).

Median split binarizes this proxy: above median → "low variance" (confident), below median → "high variance" (uncertain).

## Mode Classification

Crossing binary entropy (high/low) with binary variance (high/low) yields four modes:

| Mode | Entropy | Variance | Interpretation |
|------|---------|----------|----------------|
| 1 | Low | Low | Aligned-Confident: consensus, RM agrees |
| 2 | Low | High | Aligned-Uncertain: consensus, RM uncertain |
| 3 | High | Low | **Misaligned-Confident**: disagreement, RM confident |
| 4 | High | High | Misaligned-Uncertain: disagreement, RM uncertain |

Mode 3 is our primary focus: human voters disagree on preferences, yet the reward model expresses high confidence.

## Hypothesis Testing

### H-E1: Existence Test

**Hypothesis**: Mode 3 proportion exceeds 10% of samples.

**Test**: One-sided binomial test with null hypothesis p ≤ 0.10.

**Success criterion**: 95% CI lower bound > 10%, p < 0.05.

### H-M1: Mechanism Test (Semantic Similarity)

**Hypothesis**: Mode 3 response pairs have lower semantic similarity than Mode 1 pairs (responses divergent despite RM confidence).

**Method**: Compute cosine similarity between sentence embeddings (all-MiniLM-L6-v2) for response pairs. Compare Mode 1 vs Mode 3 distributions.

**Test**: Welch's t-test with Cohen's d effect size.

**Success criterion**: Cohen's d > 0.3 in predicted direction (Mode 1 > Mode 3).

### H-C1: Condition Test (Prompt Type)

**Hypothesis**: Mode 3 is enriched in subjective prompts (creative writing) vs objective prompts (math, coding).

**Method**: Classify prompts via keyword heuristics into subjective, objective, or ambiguous categories. Compute Mode 3 proportion within each category.

**Test**: Two-proportion z-test comparing subjective vs objective Mode 3 rates.

**Success criterion**: Ratio (subjective/objective) > 1.5.

## Statistical Corrections

For multiple hypothesis testing, we apply Bonferroni correction (α = 0.05/3 ≈ 0.017). However, our primary hypothesis (h-e1) is tested independently with MUST_WORK gate, while secondary hypotheses (h-m1, h-c1) are SHOULD_WORK exploratory tests.
