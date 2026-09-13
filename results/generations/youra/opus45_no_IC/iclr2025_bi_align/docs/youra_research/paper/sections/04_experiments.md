# Experimental Setup

We test the relationship between formality accommodation and conversation engagement through four sub-hypotheses, each building on the previous to establish the causal chain.

## Research Questions

**RQ1: Does measurable accommodation exist?** (H-E1)
Before testing accommodation-engagement links, we must confirm that formality accommodation signals are detectable in the data. We test whether Bidirectional Convergence Scores show non-trivial variance.

**RQ2: Does AI adapt to human formality?** (H-M2)
We test whether AI response formality correlates with human input formality, directly measuring accommodation behavior.

**RQ3: Does accommodation predict engagement?** (H-M3)
We test whether formality delta magnitude relates to conversation continuation rates, with tercile analysis to detect non-linear patterns.

**RQ4: Is accommodation bidirectional?** (H-M1)
We test whether users also adapt their formality in response to AI patterns, comparing effect sizes between directions.

## Dataset

**Primary dataset**: Anthropic hh-rlhf (Human Preference dataset)
- 170,800 raw conversations
- Human:/Assistant: turn format
- Multi-turn dialogues suitable for accommodation analysis

**Final samples after filtering**:
- H-E1 (BCS analysis): 26,395 conversations
- H-M1 (lag analysis): 26,405 conversations  
- H-M2 (correlation): 111,039 (human_1, AI_1) pairs
- H-M3 (tercile): 327,977 turn pairs from 111,333 conversations

## Models and Tools

**Formality scoring**: DeBERTa Large Formality Ranker \citep{deberta2024formality}
- Source: s-nlp/deberta-large-formality-ranker (HuggingFace)
- Accuracy: 87.8% on GYAFC benchmark
- Output: Continuous scores in [-1, 1]
- Batch size: 32, max length: 512

**Statistical analysis**:
- Bootstrap iterations: 2,000
- Confidence level: 95%
- Random seed: 42 (reproducibility)

## Evaluation Metrics

### H-E1: Accommodation Existence
- **Primary metric**: BCS standard deviation
- **Success criterion**: SD > 0.15
- **Target sample size**: n > 10,000

### H-M1: User Adaptation
- **Primary metric**: Lag-1 correlation coefficient
- **Success criterion**: r > 0, p < 0.05
- **Comparison**: Permutation null baseline

### H-M2: AI Accommodation
- **Primary metric**: Pearson correlation
- **Success criterion**: |r| > 0.1, p < 0.001
- **Supporting**: Spearman ρ for robustness

### H-M3: Accommodation-Engagement
- **Primary metric**: Continuation rates by tercile
- **Success criterion**: Monotonic T1 > T2 > T3 (under linear CAT)
- **Alternative**: Inverted-U if T2 > T1
- **Significance**: Cluster bootstrap p-values

## Baselines

**Permutation baseline** (H-M2): Shuffle human-AI pairings to break real accommodation while preserving marginal distributions. Real correlation should exceed permuted correlation.

**Within-conversation shuffle** (H-E1): Randomize turn order within conversations to test whether sequential structure matters for BCS variance.

## Hypotheses and Gates

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | SD > 0.15, n > 10,000 | Pivot to alternative dataset |
| H-M1 | MUST_WORK | r > 0, p < 0.05 | Explore alternative formality measures |
| H-M2 | SHOULD_WORK | \|r\| > 0.1, p < 0.001 | Per-model analysis |
| H-M3 | SHOULD_WORK | Monotonic trend | Document as negative/nuanced result |

H-E1 and H-M1 are preconditions: if accommodation signals don't exist or aren't measurable, subsequent tests are meaningless. H-M2 and H-M3 test the core hypothesis; failure provides scientific insight rather than pipeline halt.
