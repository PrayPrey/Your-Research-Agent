# Experimental Setup

We design experiments to answer three research questions that map directly to our claims:

**RQ1 (Existence):** Do RLHF-trained reward models exhibit significant enumeration preference under controlled conditions?

**RQ2 (Replication):** Does the enumeration preference replicate across architecturally distinct reward models?

**RQ3 (Architecture):** Does the effect depend on model architecture (decoder-only vs. encoder-only)?

## Stimulus Dataset

### Custom Agency-Structure Stimulus Set

We generate a controlled stimulus set specifically designed to isolate structural effects from content quality. Off-the-shelf preference datasets do not provide the factorial control necessary for our investigation---existing pairs conflate structure with content, length, correctness, and other factors.

**Dataset Statistics:**

| Property | Value |
|----------|-------|
| Total prompts | 75 |
| Domains | General knowledge, Advice, Technical |
| Variants per prompt | 8 (2×2×2 factorial) |
| Total stimulus pairs | 300 |
| Total responses scored | 2,400 (300 pairs × 4 RMs × 2 structures) |

**Factorial Design:**

| Factor | Levels | Purpose |
|--------|--------|---------|
| Structure | Enumerated, Synthesized | Primary IV |
| Correctness | High, Low | Control for quality confound |
| Completeness | Complete, Partial | Control for thoroughness confound |

Each enumerated-synthesized pair contains semantically equivalent content arranged in different formats. Length is matched within ±2% (±5 tokens for typical 250-token responses).

### Stimulus Generation Protocol

1. **Prompt selection**: 75 diverse prompts stratified across three domains (25 each)
2. **Response generation**: For each prompt, generate base content covering 3 main points
3. **Format manipulation**: Present same content as (a) numbered list or (b) flowing prose
4. **Quality manipulation**: Create variants with high/low correctness and complete/partial coverage
5. **Length matching**: Adjust filler words to match token counts within tolerance
6. **Validation**: Verify enumeration classification achieves >95% human agreement

### Enumeration Classifier

We use a deterministic regex-based classifier to identify enumerated responses:

```
ENUMERATED = TRUE if response matches:
  Pattern A: ≥2 line-initial markers (^\s*(\d+[.\):]|\-|\*|•))
  OR
  Pattern B: ≥2 ordinal tokens ("First,", "Second,", "1.", "2.")
```

This pre-registered classifier eliminates researcher degrees of freedom in enumeration detection.

## Reward Models

### Model Selection Rationale

We select four reward models spanning diverse architectures and training objectives to test whether enumeration preference generalizes beyond single-model observations:

| Model | Size | Base Architecture | Training Objective | Training Data |
|-------|------|-------------------|-------------------|---------------|
| ArmoRM | 8B | Llama-3 + MoE gating | Multi-objective BT | HelpSteer |
| UltraRM | 13B | Llama + regression head | Scalar regression | UltraFeedback |
| Starling-RM | 7B | Mistral + scalar | K-wise Bradley-Terry | Nectar |
| PairRM | 0.4B | DeBERTa (encoder) | Pairwise comparison | LLM-Blender |

**Architectural diversity justification:**
- **Decoder-only** (ArmoRM, UltraRM, Starling-RM): Causal attention processes tokens sequentially, potentially accumulating structural signals
- **Encoder-only** (PairRM): Bidirectional attention sees full context simultaneously, potentially processing structure differently
- **Training objectives**: Span Bradley-Terry, regression, and pairwise comparison
- **Training data**: Three distinct preference datasets (HelpSteer, UltraFeedback, Nectar)

This selection enables testing whether enumeration preference is a universal RLHF artifact or depends on specific architectural/training choices.

### Inference Configuration

| Parameter | Decoder Models | PairRM |
|-----------|---------------|--------|
| Precision | bfloat16 | float32 |
| Device mapping | auto | auto |
| Batch size | 16 | 16 |
| Score type | Absolute | Relative (converted) |

Models are loaded sequentially (not simultaneously) to manage GPU memory. Each model is unloaded after scoring before loading the next.

## Evaluation Protocol

### Primary Metric: Cohen's d

For each reward model, we compute the standardized mean difference between enumerated and synthesized responses:

$$d = \frac{\bar{x}_{\text{enum}} - \bar{x}_{\text{synth}}}{s_{\text{pooled}}}$$

**Interpretation:**
- *d* = 0.2: Small effect
- *d* = 0.5: Medium effect
- *d* = 0.8: Large effect

### Statistical Testing

We use paired t-tests within each reward model with Bonferroni correction for four comparisons (α = 0.05/4 = 0.0125). We compute 95% confidence intervals for effect sizes.

### Success Criteria (Pre-registered)

**Primary gate**: Cohen's *d* ≥ 0.3 in at least 2 architecturally distinct reward models

**Secondary criterion**: ≥75% (3/4) of tested models show positive enumeration effect (*d* > 0)

These thresholds ensure both practical significance (medium effect size threshold) and cross-model replication.

### Heterogeneity Analysis

We compute Cochran's Q and I² statistics to quantify effect size variation across models. Given architectural diversity, we expect substantial heterogeneity (I² > 75%) and use random-effects pooling.
