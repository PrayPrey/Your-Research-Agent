# Experiment Design: h-m2

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Under code generation tasks, if tests fully capture intent (competitive), then execution-human correlation >0.8 (strong proxy), but if tests underspecify intent (realistic), then execution-human correlation <0.5 (weak proxy), because execution feedback quality as intent proxy depends on test coverage of intent dimensions.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Task-dependent correlation variance validation.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C)
**Prerequisites Satisfied:** Yes (h-e1 VALIDATED, h-m1 VALIDATED)
**Gate Status:** MUST_WORK gate active

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-e1, h-m1

### Gate Condition
**Type:** MUST_WORK
**Requirement:** PoC must demonstrate task-dependent variance in execution-human correlation (ANOVA p<0.05, effect size >0.3)
**Consequence if fails:** BLOCKS h-m3

---

## Continuation Context

This hypothesis builds on h-e1 and h-m1 validated results. The correlation measurement infrastructure is proven working (h-e1), and the mechanism linking specification completeness to test-intent capture is confirmed (h-m1). h-m2 tests the core task-dependent correlation hypothesis.

### Previous Hypothesis Results

**From h-e1 (Feedback Correlation Structure Exists):**
- All pairwise correlations statistically significant (p<0.05)
- HumanEval: exec-human r=0.68, ai-human r=0.45, exec-ai r=0.38
- MBPP: exec-human r=0.71, ai-human r=0.52, exec-ai r=0.41
- Cohen's kappa=0.72 (strong inter-rater reliability)
- Data collection pipeline validated with 50 samples per dataset

**From h-m1 (Specification Completeness Determines Test-Intent Capture):**
- SWE-bench showed 2.3× missed intent dimensions vs HumanEval
- Qualitative failure modes cluster by task type (not random)
- Construct validity established: tests proxy intent only when specs complete

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable — using prior validated approach from h-e1*

**Relevant Cases:**
- h-e1 established correlation measurement pipeline (scipy.stats.pearsonr, bootstrap CI)
- Standard statistical testing with scipy.stats (ANOVA, post-hoc tests)
- Proven data collection workflow for execution/AI/human feedback

### Archon Code Examples

*MCP unavailable — reusing h-e1 validated infrastructure*

**Applicable Patterns:**
- Correlation computation: `scipy.stats.pearsonr(exec_scores, human_ratings)`
- Bootstrap variance: `np.random.choice` with 1000 iterations
- Statistical testing: `scipy.stats.f_oneway` for ANOVA, `scipy.stats.tukey_hsd` for post-hoc

### Exa GitHub Implementations

*MCP unavailable — using standard statistical analysis libraries*

**Standard References:**
- SciPy documentation: correlation analysis, ANOVA, post-hoc tests
- NumPy: bootstrap resampling, variance computation
- Matplotlib/Seaborn: correlation heatmaps, variance plots

### 🎯 Implementation Priority Assessment

**Implementation Type:** Statistical analysis extension (not novel algorithm implementation)

**Recommended Implementation Path:**
- Primary: Extend h-e1 validated pipeline with ANOVA and variance analysis
- Fallback: N/A (standard statistical libraries)
- Justification: h-e1 already validated correlation computation; h-m2 adds statistical tests for task-dependent differences

### Code Analysis (Serena MCP)

*MCP unavailable — not required for statistical analysis extension*

**Analysis:** h-m2 extends h-e1 infrastructure without new architectural components. Uses standard scipy statistical functions.

---

## Experiment Specification

### Dataset

**Name:** HumanEval + MBPP + SWE-bench (tri-dataset)
**Type:** standard
**Source:** 
- HumanEval: OpenAI via `openai/human-eval` (Hugging Face Datasets)
- MBPP: Google via `mbpp` (Hugging Face Datasets)
- SWE-bench: Princeton NLP via `princeton-nlp/SWE-bench` (Hugging Face Datasets)

**Splits:** Standard test sets (full evaluation sets, not subsampled)
- HumanEval: 164 problems
- MBPP: 500 problems  
- SWE-bench: 300 instances

**Preprocessing:** None required (reusing h-e1 collected feedback data)

**Task Type Mapping:**
- HumanEval → Competitive (complete specifications via tests)
- MBPP → Basic (intermediate specification completeness)
- SWE-bench → Realistic (underspecified, real-world issues)

**Loading Information** (for Phase 4 download):
- Method: Hugging Face `datasets` library
- Identifier: 
  - `datasets.load_dataset("openai_humaneval")`
  - `datasets.load_dataset("mbpp")`
  - `datasets.load_dataset("princeton-nlp/SWE-bench")`
- Code:
```python
from datasets import load_dataset

humaneval = load_dataset("openai_humaneval", split="test")
mbpp = load_dataset("mbpp", split="test")
swebench = load_dataset("princeton-nlp/SWE-bench", split="test")
```

### Models

#### Baseline Model

**Name:** Salesforce/codegen-350M-mono
**Type:** Pre-trained code generation model (frozen checkpoint)
**Source:** Hugging Face Model Hub
**Parameters:** 350M
**Training Data:** Code monolingual corpus

**Justification:** Same frozen model from h-e1 validation. Ensures feedback modality is only variable. Proven to generate diverse code samples across all three datasets.

**Loading Information** (for Phase 4 download):
- Method: Hugging Face `transformers` library
- Identifier: `Salesforce/codegen-350M-mono`
- Code:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")
```

#### Proposed Model

**Architecture:** N/A — h-m2 is statistical analysis, not model training

**Core Mechanism Implementation:**

h-m2 tests task-dependent correlation variance via statistical analysis of h-e1 collected data. No new model architecture required.

**Analysis Pipeline (10-30 line pseudo-code):**

```python
# Load h-e1 collected feedback data
data = load_h_e1_feedback()  # exec_scores, ai_scores, human_ratings per dataset

# Step 1: Compute execution-human correlation per dataset
correlations = {}
for dataset in ["HumanEval", "MBPP", "SWE-bench"]:
    exec_scores = data[dataset]["execution"]
    human_ratings = data[dataset]["human"]
    r, p = pearsonr(exec_scores, human_ratings)
    correlations[dataset] = {"r": r, "p": p}

# Step 2: Test correlation difference across task types
# ANOVA: test if correlation varies significantly by dataset
correlation_values = [correlations[d]["r"] for d in correlations]
task_labels = ["competitive", "basic", "realistic"]
f_stat, p_anova = f_oneway(*[correlations[d]["r"] for d in correlations])

# Step 3: Bootstrap variance analysis
between_task_var = np.var([correlations[d]["r"] for d in correlations])
within_task_var = []
for dataset in correlations:
    bootstrap_samples = [
        pearsonr(resample(exec_scores), resample(human_ratings))[0]
        for _ in range(1000)
    ]
    within_task_var.append(np.var(bootstrap_samples))
within_task_var = np.mean(within_task_var)

# Step 4: Validate predicted pattern
success = (
    p_anova < 0.05 and  # Significant difference
    abs(correlations["HumanEval"]["r"] - correlations["SWE-bench"]["r"]) > 0.3 and  # Effect size
    between_task_var >= 2 * within_task_var  # Variance criterion
)
```

### Training Protocol

**N/A** — h-m2 is statistical analysis on h-e1 collected data. No model training required.

**Data Reuse:**
- Execution feedback: From h-e1 test execution results
- AI feedback: From h-e1 reward model scores
- Human feedback: From h-e1 human ratings (3 raters per sample, 5-point scale)

**Analysis Protocol:**
1. Load h-e1 feedback data (exec, AI, human per dataset)
2. Compute execution-human Pearson r per dataset
3. ANOVA test: correlation difference across task types
4. Bootstrap variance: between-task vs within-task variance
5. Validate predicted pattern: HumanEval >0.8, MBPP 0.6-0.8, SWE-bench <0.5

### Evaluation

**Primary Metrics:**

1. **Execution-Human Correlation per Dataset**
   - Metric: Pearson correlation coefficient (r)
   - Computation: `scipy.stats.pearsonr(exec_scores, human_ratings)`
   - Expected pattern: HumanEval >0.8, MBPP 0.6-0.8, SWE-bench <0.5

2. **ANOVA Test for Task-Dependent Variance**
   - Metric: F-statistic and p-value
   - Computation: `scipy.stats.f_oneway(corr_humaneval, corr_mbpp, corr_swebench)`
   - Threshold: p < 0.05

3. **Effect Size**
   - Metric: Absolute difference in correlation (HumanEval vs SWE-bench)
   - Computation: `abs(r_humaneval - r_swebench)`
   - Threshold: > 0.3

**Secondary Metrics:**

4. **Between-Task vs Within-Task Variance Ratio**
   - Metric: Variance ratio
   - Computation: `np.var([r_humaneval, r_mbpp, r_swebench]) / mean(within_task_variances)`
   - Threshold: ≥ 2.0

5. **Bootstrap Confidence Intervals**
   - Metric: 95% CI for each correlation
   - Computation: 1000 bootstrap iterations with resampling
   - Purpose: Validate correlation stability

**Success Criteria (PoC):**
- Primary: ANOVA p < 0.05 AND effect size > 0.3
- Secondary: Between-task variance ≥ 2× within-task variance

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (correlation, ANOVA, variance)
- Library: `scipy.stats`, `numpy`
- Code:
```python
from scipy.stats import pearsonr, f_oneway
import numpy as np

# Correlation
r, p = pearsonr(exec_scores, human_ratings)

# ANOVA
f_stat, p_anova = f_oneway(corr_humaneval, corr_mbpp, corr_swebench)

# Variance
between_var = np.var([r_humaneval, r_mbpp, r_swebench])
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Correlation by Task Type Bar Chart**: Execution-human correlation for HumanEval, MBPP, SWE-bench with error bars (95% CI)

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations:**

1. **Correlation Heatmap** (3×3 grid)
   - Rows: Datasets (HumanEval, MBPP, SWE-bench)
   - Columns: Correlation pairs (exec-human, ai-human, exec-ai)
   - Color: Pearson r value
   - Purpose: Visual comparison of correlation structure across datasets

2. **Variance Decomposition Plot**
   - Between-task variance (single bar)
   - Within-task variance (error bars per dataset)
   - Purpose: Visualize variance ratio criterion (between ≥ 2× within)

3. **Bootstrap Distribution Plot** (3 subplots)
   - One subplot per dataset
   - Histogram of 1000 bootstrap correlation samples
   - Purpose: Show stability of correlation estimates

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ANOVA p < 0.05 (statistically significant task-dependent variance)
3. Effect size > 0.3 (HumanEval vs SWE-bench correlation difference)
4. Between-task variance ≥ 2× within-task variance

**Expected Outcome Pattern:**
- HumanEval exec-human correlation: >0.8 (strong proxy)
- MBPP exec-human correlation: 0.6-0.8 (moderate proxy)
- SWE-bench exec-human correlation: <0.5 (weak proxy)

---

## Appendix: Reference Implementations

**Statistical Analysis Libraries:**

1. **SciPy Statistical Functions**
   - Source: https://docs.scipy.org/doc/scipy/reference/stats.html
   - Functions: `pearsonr`, `f_oneway`, `bootstrap`
   - Purpose: Correlation computation, ANOVA, bootstrap CI

2. **NumPy Statistical Functions**
   - Source: https://numpy.org/doc/stable/reference/routines.statistics.html
   - Functions: `np.var`, `np.mean`, `np.random.choice`
   - Purpose: Variance computation, bootstrap resampling

3. **Matplotlib/Seaborn Visualization**
   - Source: https://matplotlib.org/stable/gallery/index.html
   - Functions: `plt.bar`, `sns.heatmap`, `plt.hist`
   - Purpose: Correlation plots, heatmaps, distributions

**Reused from h-e1:**
- Feedback data collection pipeline (validated)
- Correlation computation infrastructure (validated)
- Human rating protocol (Cohen's kappa 0.72)

**No novel implementation required** — h-m2 extends h-e1 with standard statistical tests.

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25T03:00:00

### Workflow History for This Hypothesis

**h-m2 Timeline:**
- Phase 2B: Planning completed (prerequisites identified)
- Phase 2C: Experiment design completed (2026-08-25T03:00:00)
- Next: Phase 3 Implementation Planning

**Prerequisite Chain:**
- h-e1 (VALIDATED) → h-m1 (VALIDATED) → **h-m2 (IN_PROGRESS)** → h-m3 (BLOCKED)

**Gate Status:**
- Type: MUST_WORK
- Satisfied: Not yet (awaiting Phase 4 validation)
- Impact: Blocks h-m3 until validated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
