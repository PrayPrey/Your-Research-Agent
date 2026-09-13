# Experimental Setup

We design experiments to answer four research questions that directly test our representational alignment hypothesis and scaffolding framework:

**RQ1**: Does structured error formatting improve repair success over raw compiler output?
**RQ2**: Is the improvement due to organizational structure, or merely information content?
**RQ3**: What is the optimal level of fix specificity?
**RQ4**: Does model scale interact with format benefit?

## Datasets

We evaluate on EvalPlus benchmarks [Guo et al., 2024], which provide rigorous evaluation with 80× more test cases than original HumanEval/MBPP:

| Dataset | Problems | Tests per Problem | Source |
|---------|----------|-------------------|--------|
| HumanEval+ | 164 | ~80 avg | EvalPlus |
| MBPP+ | 378 | ~80 avg | EvalPlus |
| **Total** | 542 | ~43,360 | - |

**Why EvalPlus**: Original HumanEval/MBPP have saturated (99.4% and 94.2% pass@1 for top models). EvalPlus's expanded test suites provide discriminative evaluation and generate more diverse error instances for our experiments.

### Error Collection Process

1. Run base model generation on all problems
2. Collect failed test cases with static analysis errors
3. Parse errors to extract: line number, error type, error message, code context
4. Filter for 8 supported error types (balanced sampling)

We collect 500 error instances per experiment, stratified across error types to ensure balanced representation.

## Models

We evaluate across three model scales to test scale interaction:

| Model | Parameters | Access | Purpose |
|-------|------------|--------|---------|
| CodeLlama-7B-Instruct | 7B | HuggingFace | Small scale |
| CodeLlama-34B-Instruct | 34B | HuggingFace | Medium scale |
| GPT-4 | ~175B+ | OpenAI API | Large scale |

**Why this selection**: CodeLlama variants provide controlled comparison within a model family, while GPT-4 represents current state-of-the-art for code generation. This span enables testing our hypothesis that smaller models benefit more from structured formatting.

## Baselines

**Primary baseline**: Self-repair with raw compiler output, following the theoxo/self-repair framework [Chen et al., 2024]. This represents the standard practice of feeding raw tracebacks directly to the model.

**Control conditions**:
- **Verbose-Raw**: Expanded raw output with additional whitespace and formatting—controls for prompt length
- **Scrambled**: Structured format content with randomly permuted section order—controls for information content

**Why these baselines**: The Scrambled condition is critical for causal inference. If Structured > Scrambled, the effect is due to organizational structure, not information availability. Verbose-Raw rules out simple length effects.

## Sub-Hypothesis Experiments

### H-E1: Existence Test (MUST_WORK)
- **Design**: Within-subject comparison of Raw vs Structured format
- **N**: 500 error instances × 2 conditions
- **Metric**: Repair success rate (binary)
- **Success criterion**: Structured > Raw with p < 0.05

### H-M1: Information Preservation (MUST_WORK)
- **Design**: Reconstruction test using third-party LLM
- **N**: 500 error pairs across 8 error types
- **Metric**: Field extraction accuracy
- **Success criterion**: >95% reconstruction accuracy

### H-M2: Representational Alignment (SHOULD_WORK)
- **Design**: Paired comparison of Structured vs Scrambled
- **N**: 500 error instances, paired
- **Statistical test**: McNemar's chi-squared for paired binary outcomes
- **Success criterion**: Structured > Scrambled with p < 0.05

### H-M3: Fix Specificity (SHOULD_WORK)
- **Design**: 4-level within-subject comparison (Levels 0-3)
- **N**: 500 instances × 4 levels × 3 repetitions
- **Statistical test**: Mixed-effects model with quadratic contrast
- **Success criterion**: Significant quadratic term, peak at Level 1-2

### H-C1: Scale Interaction (SHOULD_WORK)
- **Design**: 2×3 factorial (Format × Model Scale)
- **N**: 542 problems × 6 cells
- **Statistical test**: Two-way ANOVA with interaction term
- **Success criterion**: Interaction p < 0.05, η² > 0.01

## Evaluation Metrics

**Primary metric**: Repair success rate—proportion of errors successfully fixed within max iterations.

**Secondary metrics**:
- Pass@1 improvement: Delta vs base model without repair
- Iterations to success: Attempts required (when successful)
- Error type breakdown: Success rate per error category

**Statistical significance**: All comparisons use p < 0.05 threshold with Benjamini-Hochberg FDR correction for multiple comparisons. Effect sizes reported as Cohen's d for continuous outcomes and odds ratios for binary outcomes.

## Implementation Details

**Inference**: Temperature = 0.0 for deterministic comparison. Max repair iterations = 5. Batch size = 1 (sequential repair).

**Hardware**: 5× NVIDIA H100 NVL (95GB each). CodeLlama models run locally; GPT-4 via API.

**Reproducibility**: Seeded randomization (seed=42) for all stochastic components. All code available in supplementary materials.
