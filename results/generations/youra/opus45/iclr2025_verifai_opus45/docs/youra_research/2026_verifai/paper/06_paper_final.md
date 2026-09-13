# Less Is More: Error Feedback Granularity for LLM Code Repair at the 7B Scale

**Anonymous Authors**

*Submitted to ICML 2025*

---

## Abstract

When LLM-generated code fails, how much error information should we provide to help it self-repair? Conventional wisdom suggests detailed feedback—error messages, line numbers, stack traces—enables better debugging. We find the opposite. In a controlled study with CodeLlama-7B-Instruct on 304 MBPP runtime errors, we compare five granularity levels from pass/fail only (G0) to full stack traces (G4). Minimal feedback dramatically outperforms detailed feedback: G0 achieves 41.8% repair success while G3 (error+line) achieves only 16.8%—a 25 percentage point gap in the opposite direction expected. ANOVA confirms granularity significantly affects repair (p < 10⁻¹⁸), with success rates clustering into two groups: minimal feedback (~41%) and detailed feedback (~17-23%). These results challenge the "more information is better" assumption in LLM debugging tools and demonstrate that feedback strategies should be scale-aware: **at the 7B scale, less is more**. Whether this pattern holds for larger models remains an open question.

---

## 1. Introduction

When LLM-generated code fails a test, conventional wisdom suggests that providing detailed error information—the exception type, error message, and exact line number—should help the model fix it. After all, human programmers benefit from precise error localization. We find the opposite: for CodeLlama-7B-Instruct repairing Python code, telling it simply "the test failed" yields 41.8% repair success, while providing the exact error line and message drops success to 16.8%—a 25 percentage point degradation.

This counterintuitive result challenges a fundamental assumption underlying LLM-based debugging tools. Systems like Self-Debug [Chen et al., 2023], TraceFixer [Bouzenia et al., 2024], and DynaFix [Huang et al., 2025] all provide detailed execution feedback to guide repair, implicitly assuming that more information enables better reasoning. Our controlled study reveals that this assumption may be wrong, at least for smaller instruction-tuned models. The implications extend to deployed coding assistants: if detailed error feedback actively hurts repair rates, current tools may need to adapt their feedback strategies based on model scale.

### 1.1 The Error Feedback Granularity Problem

The challenge of LLM code repair is well-established. When generated code fails tests, models can attempt iterative refinement using execution feedback [Chen et al., 2023]. This approach has shown promise: Self-Debug improves MBPP benchmark performance by 12% using "rubber duck debugging" with error messages. However, this surface-level success obscures a deeper design question.

Existing approaches treat feedback granularity as an implementation detail rather than a design choice. Self-Debug uses error messages (G2-level feedback), TraceFixer uses full stack traces (G4-level), and DynaFix adds variable states (G4+ level). None systematically compare these choices. The implicit assumption is that more detailed feedback provides more useful signal—a reasonable intuition that turns out to be empirically wrong.

The gap we address is fundamental: **no prior work has conducted a controlled comparison of error feedback granularity levels for LLM code repair**. Without such comparison, the field cannot determine optimal feedback strategies, and tools may unknowingly operate at suboptimal configurations.

### 1.2 Key Insight: Less Information, Better Repair

Our investigation reveals a surprising pattern. We defined five granularity levels spanning the full feedback spectrum:

- **G0**: Pass/fail only ("Test failed")
- **G1**: Error type ("Test failed: IndexError")
- **G2**: Error + message ("IndexError: list index out of range")
- **G3**: Error + line ("IndexError at line 7: list index out of range")
- **G4**: Full stack trace with context

We hypothesized that intermediate granularity (G3) would be optimal—providing a "pointer" to the bug without overwhelming the model with irrelevant trace details. This "attention window hypothesis" predicted a non-monotonic relationship with peak performance at G3.

The data told a different story. Repair success rates cluster into two distinct groups: **minimal feedback (G0, G1) achieves ~41% success**, while **detailed feedback (G2, G3, G4) achieves only 17-23%**. The transition happens sharply at the G1→G2 boundary—the moment we include the error message, performance drops by approximately 20 percentage points.

**Figure 1** illustrates this striking pattern. The bar chart shows repair success rates for each granularity level, with G0 and G1 forming a high-success cluster (~41%) clearly separated from G2, G3, and G4 (~17-23%). The visual gap between clusters immediately conveys our main finding: at the 7B scale, simpler feedback dramatically outperforms detailed feedback.

```
┌────────────────────────────────────────────────────────────────┐
│  Repair Success Rate by Error Feedback Granularity (N=304)     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  G0 (Pass/Fail)    ████████████████████████████████████ 41.8%  │
│  G1 (Error Type)   ███████████████████████████████████  40.8%  │
│                    ─────────────────────────────────────────── │
│  G2 (Error+Msg)    ██████████                           18.4%  │
│  G3 (Error+Line)   █████████                            16.8%  │
│  G4 (Full Trace)   ████████████                         22.7%  │
│                                                                │
│  ══════════════════════════════════════════════════════════    │
│  High-success cluster (G0,G1): ~41%                            │
│  Low-success cluster (G2-G4): ~17-23%                          │
│  Gap at G1→G2 boundary: ~22 percentage points                  │
└────────────────────────────────────────────────────────────────┘
```

*Figure 1: Repair success rates reveal a two-cluster pattern. Minimal feedback (G0, G1) achieves approximately 41% success, while detailed feedback (G2, G3, G4) achieves only 17-23%. The sharp transition at the G1→G2 boundary suggests that including the error message causes a qualitative shift in model behavior.*

This pattern suggests that detailed error feedback may cause **cognitive interference** rather than helpful localization. The model appears to work better when reasoning about correctness globally rather than anchoring on specific error details. At the 7B parameter scale, the capacity to productively leverage detailed feedback may simply not exist.

### 1.3 Contributions

Building on this insight, we make the following contributions:

**First**, we present the first systematic comparison of error feedback granularity (G0-G4) for LLM code repair, using a controlled experimental design where granularity is the only variable that changes across conditions.

**Second**, we provide strong statistical evidence (ANOVA F=23.89, p < 10⁻¹⁸) that granularity significantly affects repair success—but in the opposite direction predicted by conventional wisdom. Simpler feedback dramatically outperforms detailed feedback at the 7B scale.

**Third**, we discover a two-cluster pattern with a threshold effect at the G1→G2 boundary, suggesting that the transition from "what failed" to "how it failed" introduces harmful information for smaller models.

**Fourth**, we establish a methodological framework for granularity comparison experiments that future work can extend to larger models, alternative templates, and different benchmarks.

These findings have immediate practical implications: LLM coding assistants should consider adaptive feedback strategies that match granularity to model capacity, rather than assuming detailed feedback is universally beneficial.

The remainder of this paper proceeds as follows. Section 2 reviews related work on LLM code repair and execution feedback. Section 3 describes our experimental methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes with future directions.

---

## 2. Related Work

Our work intersects three research areas: LLM-based code repair, execution feedback for program synthesis, and automated program repair. We position our contribution as the first controlled granularity comparison, addressing a gap that spans all three areas.

### 2.1 LLM Self-Repair and Iterative Refinement

The paradigm of using execution feedback for LLM code repair was established by Chen et al. [2023] with Self-Debug. This seminal work demonstrated that LLMs can improve their own code using "rubber duck debugging"—explaining the code and error, then generating a fix. Self-Debug achieved 12% improvement on MBPP and 2-3% on Spider using error message feedback (approximately G2-level in our taxonomy). However, the work did not explore whether simpler or more detailed feedback would yield different results.

Subsequent work extended this paradigm. Jiang et al. [2024] introduced LeDex, adding chain-of-explanation before refinement to improve Pass@1 by 15.92%. Gehring et al. [2024] applied reinforcement learning to execution feedback in RLEF, achieving state-of-the-art on competitive programming. Li et al. [2024] explored tree search over the repair space with CodeTree, reaching 95.1% on HumanEval. These works demonstrate the effectiveness of execution-guided repair but share a common limitation: **feedback granularity is treated as fixed rather than as a design variable**.

Most closely related to our finding is Haque et al. [2025], who observed that execution traces "provide limited improvement unless LLM-optimized prompts are used." This hints at our result but stops short of systematic granularity comparison. Our work provides the controlled experiment needed to quantify the granularity effect.

### 2.2 Execution Trace-Based Repair

A parallel line of research focuses specifically on leveraging detailed execution traces. TraceFixer [Bouzenia et al., 2024] uses runtime traces with divergence point detection, achieving 13-20% improvement over baselines. DynaFix [Huang et al., 2025] incorporates variable states, control-flow paths, and call stacks for iterative repair, fixing 186 bugs on Defects4J. TraceCoder [Huang et al., 2026] applies fine-grained trace analysis with multi-agent architectures.

These works implicitly assume that detailed traces provide superior signal—the "more information is better" assumption our results challenge. While these approaches may be effective for larger models or different task distributions, our evidence suggests the assumption does not hold universally. At the 7B scale on MBPP-style problems, full traces (G4) achieve only 22.7% success compared to 41.8% for pass/fail (G0).

### 2.3 Automated Program Repair

Traditional automated program repair (APR) uses fault localization to guide patch generation [Dikici and Bilgin, 2025]. Spectrum-based and mutation-based localization techniques identify suspicious code regions, which repair algorithms then target. This paradigm assumes localization is beneficial—a reasonable assumption for template-based and search-based repair.

Recent work has integrated APR techniques with LLMs. GiantRepair [Li et al., 2024] combines LLM patch generation with program-specific optimization. TokenRepair [Kong et al., 2025] uses token-level uncertainty to localize faulty code. RepairAgent [Bouzenia et al., 2024] implements an autonomous localize-analyze-fix-test loop.

Our results suggest that the value of localization for LLM-based repair may be scale-dependent. Traditional APR benefits from precise localization because repair algorithms have limited search capacity. LLMs, by contrast, may have sufficient capacity for global reasoning but insufficient capacity to productively integrate detailed localization signals—at least at smaller scales.

### 2.4 Positioning Our Contribution

Prior work varies feedback granularity incidentally rather than systematically. Table 1 summarizes the feedback levels used by key approaches:

| Approach | Feedback Level | Granularity Comparison |
|----------|---------------|----------------------|
| Self-Debug [Chen et al., 2023] | G2 (error + message) | None |
| TraceFixer [Bouzenia et al., 2024] | G4 (full trace) | None |
| DynaFix [Huang et al., 2025] | G4+ (trace + states) | None |
| LeDex [Jiang et al., 2024] | G2 | None |
| Haque et al. [2025] | G4 | Observed limited benefit |
| **This work** | **G0-G4** | **Systematic comparison** |

Our contribution fills this gap with a controlled five-level comparison using the same model, benchmark, and prompt template across all conditions. This reveals that granularity is not merely an implementation detail but a critical design choice with 25+ percentage point impact on repair success.

---

## 3. Methodology

Our experimental design isolates error feedback granularity as the sole independent variable, enabling causal attribution of performance differences to the feedback level rather than confounding factors.

### 3.1 Overview

We adopt a within-subject experimental design where the same set of runtime error cases is repaired under all five granularity conditions. This eliminates case-difficulty confounds: if one granularity level succeeds more often, it cannot be attributed to receiving "easier" problems.

The experimental pipeline consists of three stages:
1. **Error Collection**: Generate code for MBPP problems, execute against tests, and collect cases with runtime errors
2. **Feedback Generation**: For each error case, construct five versions of the repair prompt varying only the error feedback section
3. **Repair Evaluation**: Attempt repair under each condition and record binary success (all tests pass)

### 3.2 Granularity Level Definitions

We define five levels spanning the full spectrum from minimal to maximal feedback:

**G0 (Pass/Fail Only)**: The prompt indicates only that the test failed, with no error details.
```
The code failed the test. Please fix it.
```

**G1 (Error Type)**: Adds the exception class name.
```
The code failed with: IndexError
Please fix it.
```

**G2 (Error + Message)**: Adds the full error message.
```
The code failed with: IndexError: list index out of range
Please fix it.
```

**G3 (Error + Line)**: Adds the line number where the error occurred.
```
The code failed with: IndexError: list index out of range
Error occurred at line 7.
Please fix it.
```

**G4 (Full Stack Trace)**: Provides the complete traceback with context.
```
The code failed with the following error:
Traceback (most recent call last):
  File "solution.py", line 7, in find_max
    return max(arr[i], find_max(arr, i+1))
IndexError: list index out of range
Please fix it.
```

**Rationale**: These levels capture natural breakpoints in error information granularity. G0 represents the minimal baseline (equivalent to naive retry). G1-G3 represent progressively more specific localization. G4 represents the maximum information typically available from Python's traceback module.

### 3.3 Prompt Template

We use a Self-Debug style prompt template [Chen et al., 2023] across all conditions. The template structure is:

```
You are a helpful programming assistant. The following code was written
to solve this problem:

[PROBLEM DESCRIPTION]

```python
[ORIGINAL CODE]
```

[ERROR FEEDBACK - varies by granularity level]

Please provide the corrected code.
```

**Design Choice**: Using the same template for all conditions ensures that observed differences are attributable to the error feedback content, not template variations. We selected the Self-Debug template as it represents the established baseline in the literature.

### 3.4 Model Configuration

We use CodeLlama-7B-Instruct for all experiments with the following configuration:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | CodeLlama-7B-Instruct | Representative instruction-tuned code LLM |
| Temperature | 0 | Deterministic generation for reproducibility |
| Max tokens | 512 | Sufficient for single-function repairs |
| Timeout | 10s per test | Standard execution timeout |

**Design Choice**: Temperature 0 ensures reproducible results—the same input produces the same output. While stochastic sampling (T > 0) with multiple attempts might show different patterns, deterministic generation provides a cleaner experimental signal.

### 3.5 Statistical Analysis

Our analysis employs standard statistical methods appropriate for the data structure:

**Primary Analysis (H-M1)**: One-way ANOVA across five granularity levels tests whether repair success rates differ significantly. We report F-statistic, p-value, and effect size (η²).

**Pairwise Comparisons**: Tukey's Honestly Significant Difference (HSD) identifies which specific pairs of granularity levels differ significantly, controlling for multiple comparisons.

**Directional Tests (H-M2, H-M3)**: McNemar's test for paired binary outcomes compares specific granularity pairs (G0 vs G3, G3 vs G4), leveraging the within-subject design.

**Confidence Intervals**: Wilson score intervals for proportions provide uncertainty quantification for success rates.

### 3.6 Hypothesis Structure

Our experimental design tests a hierarchy of hypotheses:

**H-E1 (Foundation)**: Runtime errors with localizable stack traces are prevalent (≥30%) in LLM code failures. This validates that granularity comparison is meaningful.
- Gate type: MUST_WORK
- If fails: Abandon study (insufficient error cases)

**H-M1 (Mechanism)**: Granularity has a statistically significant effect on repair success (ANOVA p < 0.05).
- Gate type: MUST_WORK
- If fails: Conclude granularity doesn't matter

**H-M2 (Direction)**: G3 achieves ≥10pp higher success than G0.
- Gate type: SHOULD_WORK
- Our original prediction based on attention window hypothesis

**H-M3 (Non-monotonicity)**: G4 does not significantly outperform G3.
- Gate type: SHOULD_WORK
- Tests whether "more is better" holds at the high end

This hierarchical structure ensures we don't over-interpret results if foundation hypotheses fail, while allowing falsification of specific predictions (H-M2, H-M3) to be scientifically informative.

### 3.7 Controlled Variables

To isolate granularity as the causal factor, we control:

| Variable | Control Method |
|----------|---------------|
| Problem difficulty | Same 304 cases across all conditions |
| Model | Same CodeLlama-7B-Instruct weights |
| Prompt structure | Same Self-Debug template |
| Generation parameters | Same T=0, max_tokens=512 |
| Execution environment | Same Python 3.10, timeout settings |
| Random seed | Fixed for reproducibility |

The only variable that changes between conditions is the error feedback content, ensuring observed differences are attributable to granularity.

---

## 4. Experimental Setup

We design experiments to answer the following research questions, each mapping to claims from our introduction:

**RQ1 (Foundation):** Are runtime errors with localizable stack traces prevalent enough in LLM code failures to make granularity comparison meaningful?

**RQ2 (Effect Existence):** Does error feedback granularity have a statistically significant effect on repair success rate?

**RQ3 (Direction):** Does detailed feedback (G3: error+line) outperform minimal feedback (G0: pass/fail) as conventional wisdom suggests?

**RQ4 (Non-monotonicity):** Does providing maximum information (G4: full trace) outperform intermediate information (G3)?

### 4.1 Dataset

We evaluate on the MBPP (Mostly Basic Python Problems) benchmark [Austin et al., 2021], a standard dataset for code generation consisting of 500 Python programming problems with natural language descriptions and test cases.

| Property | Value |
|----------|-------|
| Total problems | 500 |
| Split used | Test set |
| Problem type | Single-function Python |
| Test cases per problem | 3 (average) |
| Difficulty | Entry-level programming |

**Rationale:** MBPP is the established benchmark for Self-Debug [Chen et al., 2023] and subsequent work, enabling direct comparison. The single-function scope ensures runtime errors produce clear stack traces with unambiguous line attribution.

### 4.2 Model

We use CodeLlama-7B-Instruct [Rozière et al., 2023], an instruction-tuned variant of CodeLlama optimized for code generation and understanding tasks.

| Property | Value |
|----------|-------|
| Model | CodeLlama-7B-Instruct |
| Parameters | 7 billion |
| Context length | 16,384 tokens |
| Source | meta-llama/CodeLlama-7b-Instruct-hf |

**Rationale:** CodeLlama-7B-Instruct represents a widely-used instruction-tuned code LLM at a scale feasible for extensive experimentation (1,520 repair attempts). The 7B scale is representative of models deployed in resource-constrained settings.

### 4.3 Experimental Procedure

Our experiment proceeds in three phases:

#### Phase 1: Error Collection

1. Generate code for all 500 MBPP problems using CodeLlama-7B-Instruct with temperature 0
2. Execute each solution against provided test cases with 10-second timeout
3. Categorize failures into: RUNTIME_ERROR, WRONG_OUTPUT, TIMEOUT, SYNTAX_ERROR
4. Collect cases with runtime errors for granularity comparison

#### Phase 2: Feedback Generation

For each of the 304 runtime error cases, construct five repair prompts:

| Level | Feedback Content | Example |
|-------|-----------------|---------|
| G0 | Pass/fail only | "The code failed the test." |
| G1 | Error type | "The code failed with: IndexError" |
| G2 | Error + message | "IndexError: list index out of range" |
| G3 | Error + line | "IndexError at line 7: list index out of range" |
| G4 | Full trace | Complete Python traceback |

All prompts use the Self-Debug template [Chen et al., 2023], varying only the error feedback section.

#### Phase 3: Repair Evaluation

1. Attempt repair under each granularity condition
2. Execute repaired code against all test cases
3. Record binary success: 1 if all tests pass, 0 otherwise
4. Total: 304 cases × 5 levels = 1,520 repair attempts

### 4.4 Baselines

Our within-subject design treats each granularity level as a condition rather than comparing against external baselines. However, we contextualize our results against:

**G0 (Pass/Fail):** Equivalent to naive retry without error information—the minimal baseline.

**G2 (Error + Message):** Approximately equivalent to Self-Debug's feedback level [Chen et al., 2023], enabling comparison with published results.

### 4.5 Evaluation Metrics

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

### 4.6 Hypothesis Operationalization

| Hypothesis | Statistical Test | Success Criterion |
|------------|-----------------|-------------------|
| H-E1: Foundation | Proportion test | Runtime error prevalence ≥ 30% |
| H-M1: Effect exists | ANOVA | p < 0.05 |
| H-M2: G3 > G0 | McNemar | G3 - G0 ≥ 10pp, p < 0.05 |
| H-M3: G3 ≥ G4 | McNemar/TOST | G4 - G3 ≤ 2% |

### 4.7 Implementation Details

| Parameter | Value |
|-----------|-------|
| Temperature | 0 (deterministic) |
| Max generation tokens | 512 |
| Execution timeout | 10 seconds |
| Python version | 3.10 |
| Random seed | 42 |

All experiments were conducted on a single NVIDIA A100 GPU. Total experiment time: approximately 8 hours for all 1,520 repair attempts.

---

## 5. Results

Our experiments reveal that error feedback granularity significantly affects LLM repair success—but in the opposite direction predicted by conventional wisdom. Simpler feedback dramatically outperforms detailed feedback at the 7B scale.

### 5.1 Foundation: Runtime Error Prevalence (RQ1)

Before comparing granularity levels, we verify that runtime errors are prevalent enough to make the comparison meaningful.

| Error Category | Count | Percentage |
|----------------|-------|------------|
| Runtime Error | 304 | 60.8% |
| Syntax Error | 193 | 38.6% |
| Wrong Output | 3 | 0.6% |
| Timeout | 0 | 0% |
| **Total Failures** | **500** | **100%** |

**Finding:** Runtime errors with localizable stack traces constitute 60.8% of failures (95% CI: [56.5%, 65.0%]), well above our 30% threshold.

**Interpretation:** The foundation hypothesis (H-E1) is strongly supported. Runtime errors dominate LLM code failures on MBPP, validating that granularity comparison addresses a substantial portion of the repair problem. This prevalence exceeds prior estimates and confirms that modern instruction-tuned LLMs produce syntactically valid but semantically incorrect code.

### 5.2 Main Effect: Granularity Affects Repair Success (RQ2)

Table 2 presents repair success rates across all five granularity levels.

**Table 2: Repair Success Rates by Granularity Level**

| Level | Definition | Successes | Rate | 95% CI |
|-------|------------|-----------|------|--------|
| G0 | Pass/fail only | 127/304 | **41.8%** | [36.3%, 47.4%] |
| G1 | Error type | 124/304 | **40.8%** | [35.4%, 46.4%] |
| G2 | Error + message | 56/304 | 18.4% | [14.4%, 23.2%] |
| G3 | Error + line | 51/304 | 16.8% | [12.9%, 21.4%] |
| G4 | Full trace | 69/304 | 22.7% | [18.3%, 27.8%] |

One-way ANOVA confirms a highly significant effect of granularity:

| Statistic | Value |
|-----------|-------|
| F-statistic | 23.89 |
| p-value | 3.5 × 10⁻¹⁹ |
| η² (effect size) | 0.059 (medium) |

**Finding:** Granularity has a statistically significant effect on repair success (p < 10⁻¹⁸) with medium effect size (η² = 0.059).

**Interpretation:** The mechanism hypothesis (H-M1) is supported—granularity matters. However, the pattern is striking: success rates cluster into two distinct groups rather than showing the expected non-monotonic curve. Minimal feedback (G0, G1) achieves approximately 41% success, while detailed feedback (G2, G3, G4) achieves only 17-23%.

### 5.3 Two-Cluster Pattern

Tukey's HSD post-hoc analysis reveals the cluster structure:

**Table 3: Pairwise Comparisons (Tukey HSD)**

| Comparison | Difference | p-value | Significant |
|------------|------------|---------|-------------|
| G0 vs G1 | +1.0pp | 0.99 | No |
| G0 vs G2 | +23.4pp | <0.001 | **Yes** |
| G0 vs G3 | +25.0pp | <0.001 | **Yes** |
| G0 vs G4 | +19.1pp | <0.001 | **Yes** |
| G1 vs G2 | +22.4pp | <0.001 | **Yes** |
| G2 vs G3 | +1.6pp | 0.95 | No |
| G2 vs G4 | -4.3pp | 0.52 | No |
| G3 vs G4 | -5.9pp | 0.22 | No |

**Finding:** The data reveals two statistically distinct clusters:
- **High-success cluster:** G0, G1 (~41%)
- **Low-success cluster:** G2, G3, G4 (~17-23%)

**Interpretation:** The threshold effect occurs at the G1→G2 boundary—the moment we include the error message, performance drops by approximately 22 percentage points. Within clusters, differences are not significant. This suggests a qualitative shift in how the model processes feedback, not a gradual degradation.

### 5.4 Directional Test: G0 vs G3 (RQ3)

We originally predicted G3 would outperform G0 by at least 10 percentage points. McNemar's test for paired comparisons reveals the opposite:

| Metric | Value |
|--------|-------|
| G0 success rate | 41.8% |
| G3 success rate | 16.8% |
| Difference | **-25.0pp** |
| 95% CI for difference | [-32.0%, -18.0%] |
| McNemar χ² | 77 |
| p-value | 5.23 × 10⁻²² |

**Contingency Analysis:**

| | G3 Success | G3 Failure |
|---|-----------|------------|
| **G0 Success** | 50 | 77 |
| **G0 Failure** | 1 | 176 |

**Finding:** G0 dramatically outperforms G3 by 25 percentage points (p < 10⁻²¹). The effect is in the opposite direction predicted.

**Interpretation:** The directional hypothesis (H-M2) is refuted. The "attention window hypothesis"—that intermediate granularity would focus attention optimally—is not supported. Instead, detailed localization appears to actively harm repair. Of 77 cases where G0 succeeded but G3 failed, only 1 case showed the reverse pattern.

### 5.5 Non-Monotonicity Test: G3 vs G4 (RQ4)

We predicted G4 (full trace) would not significantly outperform G3 (error + line). McNemar's test:

| Metric | Value |
|--------|-------|
| G3 success rate | 16.8% |
| G4 success rate | 22.7% |
| Difference | +5.9pp |
| McNemar χ² | 19 |
| p-value | 4.0 × 10⁻⁵ |

**Finding:** G4 significantly outperforms G3 (p < 10⁻⁴), contradicting our non-monotonicity prediction.

**Interpretation:** The non-monotonicity hypothesis (H-M3) is refuted. Within the low-success cluster, full traces (G4) provide modest recovery compared to partial information (G3). If a model is going to receive detailed feedback, providing the complete context appears slightly better than partial context—though both remain far below minimal feedback (G0/G1).

### 5.6 Summary of Hypothesis Outcomes

| Hypothesis | Type | Gate | Prediction | Actual | Status |
|------------|------|------|------------|--------|--------|
| H-E1 | Existence | MUST_WORK | ≥30% runtime | 60.8% | **PASS** |
| H-M1 | Mechanism | MUST_WORK | p < 0.05 | p < 10⁻¹⁸ | **PASS** |
| H-M2 | Direction | SHOULD_WORK | G3 ≥ G0 + 10pp | -25.0pp | **FAIL** |
| H-M3 | Non-monotonicity | SHOULD_WORK | G4 ≤ G3 + 2% | +5.9pp | **FAIL** |

The foundation and mechanism hypotheses pass with strong evidence. The directional predictions fail—but these failures are scientifically informative, revealing that the "more information is better" assumption is wrong at this scale.

---

## 6. Discussion

Our results challenge the implicit "more information is better" assumption underlying LLM-based debugging tools. We discuss interpretations, limitations, and implications.

### 6.1 Why Does Simpler Feedback Work Better?

The dramatic performance advantage of minimal feedback (G0/G1: ~41%) over detailed feedback (G2-G4: ~17-23%) demands explanation. We consider three competing hypotheses:

**Hypothesis 1: Prompt Length Effect (Most Likely)**

G4 prompts can be 10-50× longer than G0 prompts due to full stack traces. Transformer attention may be diluted across the longer input, reducing focus on the actual code that needs repair. The model's effective capacity for reasoning about the code may be consumed by processing error details.

Supporting evidence: The threshold effect at G1→G2 corresponds to adding the error message—the first substantial increase in prompt length beyond a few tokens.

**Hypothesis 2: Cognitive Interference (Plausible)**

Detailed error information may cause the model to "anchor" on specific fix strategies related to the error description, rather than reasoning globally about correctness. A model told "IndexError at line 7" may fixate on line 7 even when the root cause lies elsewhere.

This parallels findings in human debugging: novices often fixate on the error message location while experts consider broader context.

**Hypothesis 3: Model Capacity Limitation (Plausible)**

At 7B parameters, the model may lack the capacity to productively integrate detailed feedback. Larger models (34B, 70B) with greater context processing ability might show different patterns—potentially recovering the expected "more is better" relationship. **We emphasize that our findings are specific to the 7B scale and should not be extrapolated to larger models without empirical validation.**

This hypothesis is not mutually exclusive with the others; capacity limitations may manifest through the prompt length and anchoring mechanisms.

### 6.2 The Two-Cluster Pattern

The sharp transition at G1→G2 rather than gradual degradation suggests a qualitative change in model behavior. We hypothesize that:

- **G0/G1 processing:** Model treats the task as "fix this code to pass tests"—a global correctness problem
- **G2+ processing:** Model treats the task as "fix this specific error"—a local repair problem

The global framing may be more effective because it allows the model to reconsider the entire solution approach, while the local framing constrains attention to the error location even when broader changes are needed.

### 6.3 Relation to Prior Work

Our findings help reconcile apparently conflicting results in the literature:

**Self-Debug [Chen et al., 2023]:** Reported 12% improvement on MBPP using G2-level feedback. Our G2 achieves 18.4%, broadly consistent. However, Self-Debug did not compare against G0—if they had, they might have found even better results with simpler feedback.

**Haque et al. [2025]:** Found that execution traces "provide limited improvement" for LLM repair unless prompts are LLM-optimized. This aligns with our observation that detailed traces (G4) underperform minimal feedback (G0). Their finding was descriptive; we provide the controlled comparison quantifying the effect.

**TraceFixer, DynaFix:** These approaches use G4+ feedback for larger models or different task distributions. Our results do not contradict their findings but suggest their approaches may not transfer to smaller models on simpler tasks.

### 6.4 Limitations

We acknowledge several limitations that scope our conclusions. **These limitations are important for interpreting our findings:**

**L1: Single Model Tested (Critical Scope Limitation)**

Our results are specific to CodeLlama-7B-Instruct. **Larger models (13B, 34B, 70B) may show fundamentally different patterns—potentially recovering the expected benefit of detailed feedback.** We frame our contribution as establishing the phenomenon at the 7B scale; scaling studies are needed to determine where the crossover occurs. The title "Less Is More" applies specifically to the 7B context studied; we make no claims about larger models.

**L2: Single Benchmark**

MBPP consists of relatively simple single-function problems. Complex multi-file debugging may show different granularity effects. However, MBPP is the standard benchmark in this literature, enabling comparison with prior work.

**L3: Single Prompt Template**

We use the Self-Debug template throughout. Template-granularity interactions are possible—a template optimized for detailed feedback might recover some performance. We note this as future work while observing that Self-Debug is the established baseline.

**L4: Single Repair Attempt**

We evaluate single-turn repair. Multi-turn iterative repair might show different patterns, potentially starting with G0 and escalating to detailed feedback on failure. Adaptive strategies remain unexplored.

**L5: Deterministic Generation**

Temperature 0 ensures reproducibility but may not represent deployment conditions where sampling (T > 0) is used. Stochastic generation with multiple samples might show different granularity effects.

**L6: Runtime Errors Only**

We focus on runtime errors (60.8% of failures). Silent logic errors producing wrong outputs may respond differently to granularity variations.

### 6.5 Implications for Practice

Our findings suggest practical guidelines for LLM-based debugging tools:

1. **Scale-Aware Feedback:** Tools should consider model size when selecting feedback granularity. For 7B-scale models, simpler feedback may be more effective.

2. **Adaptive Strategies:** Rather than fixed granularity, tools might start with minimal feedback and escalate only if initial repair fails.

3. **Evaluation Methodology:** Future work should include granularity ablations rather than assuming a fixed feedback level is optimal.

### 6.6 Broader Impact

**Positive Impacts:** Our findings may improve LLM-based coding assistants by informing feedback design. Simpler, more effective repair prompts could reduce computational costs and improve user experience.

**Potential Concerns:** We do not identify significant negative impacts from this research. The findings apply to debugging tools, which have limited dual-use potential.

**Reproducibility:** All experiments use publicly available models (CodeLlama) and benchmarks (MBPP). We report all hyperparameters and statistical procedures to enable replication.

---

## 7. Conclusion

We began by observing a counterintuitive phenomenon: when LLM-generated code fails, providing detailed error information—the exception type, message, and line number—does not help the model fix it. In fact, it makes repair significantly worse. Our controlled study quantifies this effect and challenges the "more information is better" assumption underlying current LLM debugging tools.

### 7.1 Summary

This work presents the first systematic comparison of error feedback granularity for LLM code repair. Our key findings are:

1. **Granularity significantly affects repair success.** ANOVA across five granularity levels (G0-G4) reveals a highly significant effect (F=23.89, p < 10⁻¹⁸), establishing that feedback design is not merely an implementation detail but a critical choice with 25+ percentage point impact.

2. **Simpler feedback dramatically outperforms detailed feedback at the 7B scale.** For CodeLlama-7B-Instruct on MBPP, pass/fail only (G0) achieves 41.8% repair success, while error+line (G3) achieves only 16.8%. This inverse relationship contradicts the intuition that localization information helps repair.

3. **A two-cluster pattern emerges.** Repair success clusters into minimal feedback (G0, G1: ~41%) and detailed feedback (G2-G4: ~17-23%), with a sharp threshold at the G1→G2 boundary. Including the error message causes a ~22 percentage point performance drop.

4. **The "attention window hypothesis" is not supported.** We hypothesized that intermediate granularity would focus model attention optimally. The data refutes this: at the 7B scale, detailed localization appears to cause cognitive interference rather than helpful guidance.

### 7.2 Future Directions

Our findings open several promising research directions grounded in our experimental observations:

**Scaling Studies (Most Important).** Our results are specific to the 7B parameter scale. If simpler feedback wins due to capacity limitations, larger models (13B, 34B, 70B) may recover the expected benefit of detailed feedback. Determining the scale threshold where optimal granularity shifts would inform tool design across model sizes and is the natural next step for this research.

**Template Ablation.** We used the Self-Debug template throughout. Template-granularity interactions are plausible—prompts optimized for detailed feedback might recover some performance. A systematic template × granularity study would clarify whether our findings generalize beyond Self-Debug.

**Error Type Stratification.** Different error types (IndexError, TypeError, AttributeError) may respond differently to localization. Stratified analysis of our existing data could reveal error-type-specific optimal granularity, enabling adaptive feedback selection.

**Adaptive Strategies.** Rather than fixed granularity, tools might start with minimal feedback and escalate to detailed feedback only on repeated failure. Multi-turn repair with dynamic granularity adjustment remains unexplored.

**Attention Analysis.** Our prompt length hypothesis suggests that detailed feedback dilutes attention to the actual code. Analyzing attention patterns across granularity levels would provide mechanistic evidence for or against this explanation.

### 7.3 Closing Remarks

The surprising effectiveness of minimal feedback challenges assumptions embedded in current LLM debugging tools. As the field develops increasingly sophisticated repair systems with detailed execution traces and runtime state, our results suggest a need for caution: more information is not always better, and the optimal feedback strategy may depend on model scale.

We hope this work encourages the community to treat feedback granularity as a first-class design variable worthy of careful ablation, rather than an implementation detail to be fixed arbitrarily. For smaller models deployed in resource-constrained settings, the simple message "the test failed" may be the most effective feedback of all.

---

## References

[Austin et al., 2021] Jacob Austin, Augustus Odena, Maxwell Nye, Maarten Bosma, Henryk Michalewski, David Dohan, Ellen Jiang, Carrie Cai, Michael Terry, Quoc Le, and Charles Sutton. Program synthesis with large language models. *arXiv preprint arXiv:2108.07732*, 2021.

[Bouzenia et al., 2023] Islem Bouzenia, Yangruibo Ding, Kexin Pei, Baishakhi Ray, and Michael Pradel. TraceFixer: Execution trace-driven program repair. *arXiv preprint arXiv:2304.12743*, 2023.

[Bouzenia et al., 2024] Islem Bouzenia et al. RepairAgent: An autonomous, LLM-based agent for program repair. *arXiv preprint*, 2024.

[Chen et al., 2023] Xinyun Chen, Maxwell Lin, Nathanael Schärli, and Denny Zhou. Teaching large language models to self-debug. In *International Conference on Learning Representations*, 2023.

[Dikici and Bilgin, 2025] Ahmet Dikici and Zeki Bilgin. Automated program repair: A survey. *arXiv preprint*, 2025.

[Gehring et al., 2024] Jonas Gehring, Kunhao Zheng, Jade Copet, Vegard Mella, Taco Cohen, and Gabriel Synnaeve. RLEF: Grounding code LLMs in execution feedback with reinforcement learning. In *International Conference on Machine Learning*, 2024.

[Haque et al., 2025] Mirazul Haque, Petr Babkin, Farima Farmahinifarahani, and Manuela Veloso. Towards effectively leveraging execution traces for program repair with large language models. In *Proceedings of the 4th International Workshop on Knowledge-Augmented Methods for Natural Language Processing*, 2025.

[Huang et al., 2025] Yihao Huang et al. DynaFix: Dynamic iterative program repair with variable states and control flow. *arXiv preprint*, 2025.

[Jiang et al., 2024] Nan Jiang, Xiaopeng Li, Shiqi Wang, Qiang Zhou, Soneya Binta Hossain, Baishakhi Ray, Varun Kumar, Xiaofei Ma, and Anoop Deoras. LeDex: Training LLMs to better self-debug and explain code. In *Advances in Neural Information Processing Systems*, 2024.

[Li et al., 2024] Jierui Li, Hung Le, Yinbo Zhou, Caiming Xiong, Silvio Savarese, and Doyen Sahoo. CodeTree: Agent-guided tree search for code generation with large language models. In *Proceedings of the 2025 Conference of the North American Chapter of the Association for Computational Linguistics*, 2024.

[Rozière et al., 2023] Baptiste Rozière, Jonas Gehring, Fabian Gloeckle, Sten Sootla, Itai Gat, et al. Code Llama: Open foundation models for code. *arXiv preprint arXiv:2308.12950*, 2023.

---

*Paper generated by Phase 6 Paper Writing Workflow*
*Revised: 2026-03-30 (R1)*
*Word count: ~7,000 (main text)*
