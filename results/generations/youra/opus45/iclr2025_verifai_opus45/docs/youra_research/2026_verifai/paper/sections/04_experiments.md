# Experimental Setup

We design experiments to answer the following research questions, each mapping to claims from our introduction:

**RQ1 (Foundation):** Are runtime errors with localizable stack traces prevalent enough in LLM code failures to make granularity comparison meaningful?

**RQ2 (Effect Existence):** Does error feedback granularity have a statistically significant effect on repair success rate?

**RQ3 (Direction):** Does detailed feedback (G3: error+line) outperform minimal feedback (G0: pass/fail) as conventional wisdom suggests?

**RQ4 (Non-monotonicity):** Does providing maximum information (G4: full trace) outperform intermediate information (G3)?

## Dataset

We evaluate on the MBPP (Mostly Basic Python Problems) benchmark [Austin et al., 2021], a standard dataset for code generation consisting of 500 Python programming problems with natural language descriptions and test cases.

| Property | Value |
|----------|-------|
| Total problems | 500 |
| Split used | Test set |
| Problem type | Single-function Python |
| Test cases per problem | 3 (average) |
| Difficulty | Entry-level programming |

**Rationale:** MBPP is the established benchmark for Self-Debug [Chen et al., 2023] and subsequent work, enabling direct comparison. The single-function scope ensures runtime errors produce clear stack traces with unambiguous line attribution.

## Model

We use CodeLlama-7B-Instruct [Rozière et al., 2023], an instruction-tuned variant of CodeLlama optimized for code generation and understanding tasks.

| Property | Value |
|----------|-------|
| Model | CodeLlama-7B-Instruct |
| Parameters | 7 billion |
| Context length | 16,384 tokens |
| Source | meta-llama/CodeLlama-7b-Instruct-hf |

**Rationale:** CodeLlama-7B-Instruct represents a widely-used instruction-tuned code LLM at a scale feasible for extensive experimentation (1,520 repair attempts). The 7B scale is representative of models deployed in resource-constrained settings.

## Experimental Procedure

Our experiment proceeds in three phases:

### Phase 1: Error Collection

1. Generate code for all 500 MBPP problems using CodeLlama-7B-Instruct with temperature 0
2. Execute each solution against provided test cases with 10-second timeout
3. Categorize failures into: RUNTIME_ERROR, WRONG_OUTPUT, TIMEOUT, SYNTAX_ERROR
4. Collect cases with runtime errors for granularity comparison

### Phase 2: Feedback Generation

For each of the 304 runtime error cases, construct five repair prompts:

| Level | Feedback Content | Example |
|-------|-----------------|---------|
| G0 | Pass/fail only | "The code failed the test." |
| G1 | Error type | "The code failed with: IndexError" |
| G2 | Error + message | "IndexError: list index out of range" |
| G3 | Error + line | "IndexError at line 7: list index out of range" |
| G4 | Full trace | Complete Python traceback |

All prompts use the Self-Debug template [Chen et al., 2023], varying only the error feedback section.

### Phase 3: Repair Evaluation

1. Attempt repair under each granularity condition
2. Execute repaired code against all test cases
3. Record binary success: 1 if all tests pass, 0 otherwise
4. Total: 304 cases × 5 levels = 1,520 repair attempts

## Baselines

Our within-subject design treats each granularity level as a condition rather than comparing against external baselines. However, we contextualize our results against:

**G0 (Pass/Fail):** Equivalent to naive retry without error information—the minimal baseline.

**G2 (Error + Message):** Approximately equivalent to Self-Debug's feedback level [Chen et al., 2023], enabling comparison with published results.

## Evaluation Metrics

**Primary Metric:** Repair success rate—the proportion of cases where the repaired code passes all tests.

$$\text{Success Rate}(G_i) = \frac{\sum_{j=1}^{N} \mathbb{1}[\text{repair}_j \text{ passes all tests}]}{N}$$

**Statistical Tests:**
- One-way ANOVA across G0-G4 for omnibus effect test
- Tukey's HSD for pairwise comparisons with family-wise error control
- McNemar's test for paired comparisons (G0 vs G3, G3 vs G4)
- Wilson score intervals for proportion confidence intervals

**Effect Size:** η² (eta-squared) for ANOVA effect magnitude:
- Small: η² ≈ 0.01
- Medium: η² ≈ 0.06
- Large: η² ≈ 0.14

## Hypothesis Operationalization

| Hypothesis | Statistical Test | Success Criterion |
|------------|-----------------|-------------------|
| H-E1: Foundation | Proportion test | Runtime error prevalence ≥ 30% |
| H-M1: Effect exists | ANOVA | p < 0.05 |
| H-M2: G3 > G0 | McNemar | G3 - G0 ≥ 10pp, p < 0.05 |
| H-M3: G3 ≥ G4 | McNemar/TOST | G4 - G3 ≤ 2% |

## Implementation Details

| Parameter | Value |
|-----------|-------|
| Temperature | 0 (deterministic) |
| Max generation tokens | 512 |
| Execution timeout | 10 seconds |
| Python version | 3.10 |
| Random seed | 42 |

All experiments were conducted on a single NVIDIA A100 GPU. Total experiment time: approximately 8 hours for all 1,520 repair attempts.
