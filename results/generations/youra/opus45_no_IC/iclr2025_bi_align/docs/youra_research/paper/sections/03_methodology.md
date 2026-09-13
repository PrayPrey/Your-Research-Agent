# Methodology

Our analysis tests whether formality accommodation predicts conversation engagement in human-AI dialogue. We decompose this question into four sub-hypotheses, each addressing a necessary step in the causal chain from accommodation to engagement.

## Formality Measurement

We measure formality using the DeBERTa Large Formality Ranker \citep{deberta2024formality}, a transformer model fine-tuned on the GYAFC dataset with 87.8% classification accuracy. The model produces continuous scores in [-1, 1], where higher values indicate greater formality.

For each conversation turn, we extract the text and compute its formality score:
$$f_t = \text{DeBERTa}(\text{message}_t)$$

We then compute the **formality delta** between human input and AI response:
$$\Delta_{\text{AI}\to\text{H}} = |f_{\text{AI}_1} - f_{\text{H}_1}|$$

Lower delta indicates stronger accommodation—the AI matches the human's formality level more closely. This operationalization aligns with CAT's concept of convergence: smaller stylistic distance signals accommodation.

## Dataset and Preprocessing

We use the Anthropic hh-rlhf dataset, which contains 170,000+ human-AI conversations with clear turn structure (Human:/Assistant: format). We apply the following filters:

- **Minimum turns**: ≥2 turns per participant (ensuring enough signal for accommodation measurement)
- **Language**: English only (DeBERTa trained on English GYAFC)
- **Message length**: ≥5 tokens (excluding trivial messages)

After filtering, we retain 111,039 conversations for primary analysis (H-M2) and 26,395 conversations with complete turn sequences for BCS analysis (H-E1).

## Analysis Framework

### H-E1: Accommodation Variance (Existence Test)

We compute the Bidirectional Convergence Score (BCS) to measure accommodation trajectory:
$$\text{BCS} = \frac{\Delta_{\text{final}} - \Delta_{\text{initial}}}{\Delta_{\text{initial}}}$$

Negative BCS indicates convergence (formality gap narrows); positive indicates divergence. We test whether BCS shows non-trivial variance (SD > 0.15), confirming that accommodation patterns exist in the data.

### H-M1: User Adaptation (Lag Correlation)

We compute lagged cross-correlation between AI formality and subsequent human formality:
$$r_{\text{lag-1}} = \text{corr}(f_{\text{AI}_t}, f_{\text{H}_{t+1}})$$

Positive correlation indicates users adapt their formality in response to AI patterns.

### H-M2: AI Accommodation (Direct Correlation)

We test whether AI formality correlates with human formality in turn-1 pairs:
$$r = \text{corr}(f_{\text{H}_1}, f_{\text{AI}_1})$$

Success criterion: |r| > 0.1, p < 0.001. This directly tests whether AI exhibits accommodation behavior.

### H-M3: Accommodation-Engagement Link (Tercile Analysis)

We divide conversations into terciles by formality delta magnitude:
- **T1** (low delta): Highest accommodation
- **T2** (mid delta): Moderate accommodation  
- **T3** (high delta): Lowest accommodation

We then measure **continuation rate** per tercile—the proportion of conversations that continue beyond the initial exchange. Under linear CAT assumptions, T1 should show highest continuation (r_continuation negatively correlated with delta). An inverted-U pattern (T2 > T1) would indicate non-linear dynamics.

## Statistical Validation

We use cluster bootstrap with 2,000 iterations to compute confidence intervals, clustering by conversation to account for non-independence. Effect sizes (Cohen's d, correlation r) complement p-values for practical significance assessment.

For tercile comparison, we test monotonicity through Spearman correlation between tercile rank and continuation rate. We report robust p-values from permutation tests to avoid parametric assumptions.

## Design Rationale

**Why formality?** Formality is a salient, interpretable dimension of linguistic style with validated measurement tools. Users consciously perceive formality differences, making it suitable for accommodation analysis.

**Why early turns?** Chen et al. \citep{chen2026bidirectional} found AI accommodation front-loaded in turn 1. Analyzing early turns captures accommodation before topic complexity dominates.

**Why terciles?** Tercile analysis directly tests monotonicity assumptions. Linear regression would assume monotonic relationships; terciles reveal non-linear patterns like our inverted-U finding.
