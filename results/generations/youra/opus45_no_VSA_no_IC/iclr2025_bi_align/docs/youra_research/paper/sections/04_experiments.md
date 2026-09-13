# Experiments

We conduct three experiments testing distinct aspects of the overconfident misalignment hypothesis.

## Experiment 1: Mode 3 Existence (h-e1)

**Objective**: Determine whether Mode 3 (high human entropy, low RM variance) constitutes a substantial proportion of preference battles.

**Setup**:
- Dataset: LMSYS Chatbot Arena (57,477 battles)
- Human entropy: Shannon entropy computed at model-pair level, binarized via median split
- RM variance proxy: OpenAssistant reward model score difference, binarized via median split (inverted: low difference → high variance)
- Mode classification: 2×2 crossing of binary entropy × binary variance

**Metric**: Proportion of battles classified as Mode 3.

**Gate**: MUST_WORK. If Mode 3 < 10%, the phenomenon is negligible and the hypothesis fails.

**Analysis**: One-sided binomial test (H₀: p ≤ 0.10, H₁: p > 0.10) with 95% confidence interval.

## Experiment 2: Semantic Similarity Mechanism (h-m1)

**Objective**: Test whether Mode 3 arises from semantic divergence between responses—cases where responses differ substantively but RMs miss the distinction.

**Setup**:
- Subset: Mode 1 (n=15,107) and Mode 3 (n=13,632) battles from h-e1 classification
- Embeddings: all-MiniLM-L6-v2 sentence transformer
- Similarity: Cosine similarity between response_a and response_b embeddings per battle

**Prediction**: Mode 3 pairs should have *lower* semantic similarity than Mode 1 pairs. If RMs are overconfident on divergent responses, the similarity gap should be detectable.

**Metric**: Cohen's d effect size for similarity difference (Mode 1 − Mode 3).

**Gate**: SHOULD_WORK. Success requires d > 0.3 in predicted direction.

**Analysis**: Welch's t-test with bootstrap 95% CI for Cohen's d.

## Experiment 3: Prompt Type Condition (h-c1)

**Objective**: Test whether Mode 3 concentrates in subjective prompt types where human preferences naturally vary.

**Setup**:
- Prompt classification via keyword heuristics:
  - **Subjective**: creative writing, story, poem, opinion, style, tone
  - **Objective**: code, math, programming, calculate, solve, algorithm
  - **Ambiguous**: prompts matching neither or both categories (excluded)
- Mode 3 proportion computed within each category

**Prediction**: Subjective prompts should have higher Mode 3 proportion than objective prompts (ratio > 1.5).

**Metric**: Ratio of Mode 3 proportions (subjective / objective).

**Gate**: SHOULD_WORK. Success requires ratio > 1.5 with p < 0.05.

**Analysis**: Two-proportion z-test with Cohen's h effect size.

## Experimental Controls

**Controlled variables**:
- Response length: Not explicitly controlled but naturally varies; future work should stratify
- Model tier: All model pairs included; tier-stratified analysis deferred

**Limitations acknowledged**:
- Single RM instead of ensemble (full variance estimation pending)
- Model-pair entropy aggregation (individual battle entropy not available)
- Keyword-based prompt classification (75% ambiguous, excluded)
