# Methodology

Our goal is to determine whether RLHF-trained reward models exhibit systematic preferences for enumerated response formats independent of content quality. This requires isolating the structural effect from potential confounds including response length, correctness, and completeness. We describe our controlled stimulus design, reward model evaluation protocol, and statistical analysis approach.

## Overview

Building on our observation that enumeration markers may function as "beacon features" during RLHF training, we design a behavioral probing experiment with three key properties:

1. **Structural isolation**: Stimulus pairs differ only in format (enumerated vs. synthesized) while matching on content, length, correctness, and completeness.

2. **Factorial control**: We vary correctness and completeness orthogonally to structure, enabling detection of interactions and ruling out confounds.

3. **Architectural diversity**: We evaluate multiple reward models spanning different base architectures and training objectives to test generalization.

This design allows us to measure the effect of enumeration on reward model scores under controlled conditions, separating structural preference from content quality signals.

## Controlled Stimulus Generation

### Stimulus Pair Structure

Each stimulus consists of a prompt and two responses: one enumerated (presenting information as a numbered list) and one synthesized (presenting the same information in prose format). The responses are semantically equivalent but structurally different.

**Example stimulus pair:**

*Prompt*: "What are the benefits of regular exercise?"

*Enumerated response*:
```
Regular exercise offers several key benefits:
1. Cardiovascular health: Exercise strengthens the heart and improves circulation.
2. Mental wellbeing: Physical activity releases endorphins that reduce stress.
3. Weight management: Regular movement helps maintain healthy body composition.
```

*Synthesized response*:
```
Regular exercise offers several key benefits for both physical and mental health.
Cardiovascular function improves as exercise strengthens the heart and circulation.
Mental wellbeing benefits from the endorphin release during physical activity,
which reduces stress. Additionally, regular movement supports weight management
by maintaining healthy body composition.
```

### Factorial Design

We employ a 2×2 within-structure factorial design:

| Factor | Levels | Description |
|--------|--------|-------------|
| **Structure** | Enumerated, Synthesized | Primary independent variable |
| **Correctness** | High, Low | Factual accuracy (all correct vs. one error) |
| **Completeness** | Complete, Partial | Coverage (3+ points vs. 2 points) |

This yields 4 variants per structure per prompt, enabling analysis of main effects and interactions.

### Length Matching

Response length confounds structural comparisons---longer responses often receive higher scores regardless of format. We enforce length matching within ±2% token count between enumerated and synthesized versions of each pair. Given typical response lengths of 200-300 tokens, this corresponds to ±4-6 tokens tolerance.

**Rationale**: Prior work has shown that reward models exhibit length biases [Singhal et al., 2023]. By matching length precisely, we ensure that any observed preference for enumeration reflects structural rather than verbosity effects.

### Enumeration Operationalization

We define enumeration using a deterministic regex classifier:

```
ENUMERATED = TRUE if response contains:
  (a) ≥2 line-initial markers matching ^\s*(\d+[.\):]|\-|\*|•)
  OR
  (b) ≥2 explicit ordinal tokens: "First,", "Second,", "1.", "2."
```

This classifier achieves >95% agreement with human labeling on held-out samples. Pre-registration of the classifier eliminates researcher degrees of freedom in enumeration detection.

### Dataset Specification

We generate 75 diverse prompts spanning multiple domains:
- **General knowledge** (25 prompts): Factual questions, explanations
- **Advice** (25 prompts): Recommendations, decision support
- **Technical** (25 prompts): How-to instructions, process descriptions

For each prompt, we generate 8 response variants (2 structures × 2 correctness × 2 completeness), yielding 600 stimulus pairs total. Each structure-matched pair shares identical content arranged in different formats.

## Reward Model Evaluation Protocol

### Model Selection

We select four architecturally distinct reward models to test generalization:

| Model | Parameters | Architecture | Training Objective | Training Data |
|-------|------------|--------------|-------------------|---------------|
| ArmoRM | 8B | Llama-3 + MoE | Multi-objective BT | HelpSteer |
| UltraRM | 13B | Llama + scalar | Regression | UltraFeedback |
| Starling-RM | 7B | Mistral | K-wise BT | Nectar |
| PairRM | 0.4B | DeBERTa | Pairwise comparison | LLM-Blender |

**Rationale**: This selection spans three decoder-only models with different training objectives and one encoder-only model. If enumeration preference depends on causal vs. bidirectional attention, we expect different patterns across this architectural divide.

### Inference Protocol

For decoder-only models (ArmoRM, UltraRM, Starling-RM):
- Load model via HuggingFace Transformers with `trust_remote_code=True`
- Use bfloat16 precision with `device_map="auto"`
- Score each response independently: `score = model(prompt, response)`
- Batch size: 16 for memory efficiency

For PairRM (encoder-only):
- Load via llm-blender library
- Score pairs relatively: `score = model(prompt, response_a, response_b)`
- Convert pairwise scores to pseudo-absolute scores for comparison

All models run in evaluation mode with dropout disabled. We use a fixed random seed (42) throughout for reproducibility.

### Score Normalization

Raw scores vary in scale across models. For consistent comparison, we normalize scores to [0, 1] range within each model:

$$
\text{score}_{\text{norm}} = \frac{\text{score} - \text{score}_{\min}}{\text{score}_{\max} - \text{score}_{\min}}
$$

where min/max are computed across all scored responses for that model.

## Statistical Analysis

### Primary Metric: Cohen's d

For each reward model, we compute Cohen's *d* to quantify the effect of enumeration:

$$
d = \frac{\bar{x}_{\text{enum}} - \bar{x}_{\text{synth}}}{s_{\text{pooled}}}
$$

where $s_{\text{pooled}} = \sqrt{\frac{(n_1-1)s_1^2 + (n_2-1)s_2^2}{n_1+n_2-2}}$

**Interpretation**: *d* = 0.2 (small), *d* = 0.5 (medium), *d* = 0.8 (large) following Cohen's conventions.

### Confidence Intervals

We compute 95% confidence intervals for each effect size:

$$
\text{CI}_{95} = d \pm z_{0.975} \cdot SE_d
$$

where $SE_d = \sqrt{\frac{n_1+n_2}{n_1 n_2} + \frac{d^2}{2(n_1+n_2)}}$

### Significance Testing

We use paired t-tests within each reward model:

$$
t = \frac{\bar{d}}{SE_{\bar{d}}}
$$

with significance threshold $\alpha = 0.05$ and Bonferroni correction for multiple comparisons across models.

### Gate Condition

Following our pre-registered success criteria, we define the hypothesis as supported if:

**Primary gate**: Cohen's *d* ≥ 0.3 in at least 2 architecturally distinct reward models

**Secondary criterion**: ≥75% (3/4) of tested models show positive enumeration effect (*d* > 0)

These thresholds ensure both practical significance (medium effect size) and replicability (cross-model validation).

### Heterogeneity Analysis

We compute the I² statistic to quantify effect size heterogeneity across models:

$$
I^2 = \frac{Q - df}{Q} \times 100\%
$$

where Q is Cochran's Q statistic. High heterogeneity (I² > 75%) is expected given architectural differences and suggests that model-specific factors moderate the enumeration preference.

## Visualization

We generate four visualization types to communicate results:

1. **Forest plot**: Per-model effect sizes with 95% CIs, threshold overlay at *d* = 0.3
2. **Violin plot**: Score distributions by structure for each model
3. **Interaction plot**: Factorial analysis showing structure × correctness × completeness
4. **Gate metrics**: Bar chart comparing effect sizes to success threshold

All figures are saved in PNG and PDF formats for publication flexibility.
