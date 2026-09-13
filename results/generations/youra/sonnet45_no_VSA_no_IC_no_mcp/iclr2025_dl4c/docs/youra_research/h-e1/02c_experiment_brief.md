# Experiment Design: h-e1

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Under code generation tasks with varying specification completeness (HumanEval, MBPP, SWE-bench), if we measure pairwise correlations between execution, AI, and human feedback on same code samples, then correlation patterns will exist and be measurable with sufficient statistical power to detect task-dependent differences.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK gate active

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK gate: If correlations are unmeasurable or all uniform, ABANDON (correlation study infeasible).

---

## Continuation Context

This is the foundation hypothesis. No prior hypothesis results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using verification plan specifications*

Key implementation patterns for correlation studies:
- Standard statistical correlation analysis (Pearson r)
- Bootstrap confidence intervals for robustness
- Inter-rater reliability (Cohen's kappa) for human feedback quality
- Multiple dataset comparison framework

### Archon Code Examples

*MCP unavailable - relying on standard libraries*

Standard Python libraries for implementation:
- `scipy.stats.pearsonr` for correlation computation
- `numpy` for bootstrap sampling
- `sklearn.metrics.cohen_kappa_score` for inter-rater reliability
- Standard code generation APIs (OpenAI, HuggingFace)

### Exa GitHub Implementations

*MCP unavailable - using known benchmarks*

Reference implementations:
- HumanEval: `openai/human-eval` (official benchmark)
- MBPP: `google-research/google-research/mbpp`
- SWE-bench: `princeton-nlp/SWE-bench`
- CodeRL (Le et al. 2022): Execution-based feedback framework

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Since this is a novel correlation study (not reproducing a specific paper), we use standard benchmark implementations.

**Recommended Implementation Path:**
- Primary: Official benchmark repos (HumanEval, MBPP, SWE-bench) + standard statistical libraries
- Fallback: Simplified single-dataset pilot (HumanEval only) if tri-dataset setup fails
- Justification: Official benchmarks ensure reproducibility; standard libraries ensure statistical validity

### Code Analysis (Serena MCP)

*MCP unavailable - specification based on standard patterns*

Expected code structure:
1. Dataset loaders (3 separate modules for HumanEval, MBPP, SWE-bench)
2. Code generator wrapper (OpenAI API or HuggingFace)
3. Feedback collectors (execution, AI reward model, human rating simulator for PoC)
4. Correlation analyzer (statistical computations)
5. Visualization (correlation matrices, scatter plots)

---

## Experiment Specification

### Dataset

**Name:** HumanEval + MBPP + SWE-bench (tri-dataset)

**Type:** standard

**Specification:**
- **HumanEval:** 164 problems, use first 100 for sampling
  - Source: `openai/human-eval`
  - Format: Python function generation from docstring
  - Test suite: Unit tests included
  
- **MBPP:** 974 problems, randomly sample 100
  - Source: `google-research/google-research/mbpp`
  - Format: Basic Python programming problems
  - Test suite: 3 test cases per problem
  
- **SWE-bench:** 2,294 GitHub issues, randomly sample 100
  - Source: `princeton-nlp/SWE-bench`
  - Format: Real-world repository patches
  - Test suite: Repository test suites

**Sample Size:** 100 samples per dataset (300 total)

**Rationale:** 100 samples provides 80% statistical power to detect r=0.3 correlation differences at α=0.05 (from Phase 2B assumption A2).

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets API + GitHub clones
- Identifier: 
  - `openai_humaneval` (HF dataset)
  - `mbpp` (HF dataset)
  - `princeton-nlp/SWE-bench` (GitHub)
- Code:
```python
from datasets import load_dataset
humaneval = load_dataset("openai_humaneval")
mbpp = load_dataset("mbpp")
# SWE-bench requires custom loader from repo
```

### Models

#### Baseline Model

**Name:** CodeGen-16B-mono (Salesforce/codegen-16B-mono)

**Specification:**
- **Architecture:** GPT-2 based transformer (16B parameters)
- **Training:** Pre-trained on The Pile + GitHub code (Python-focused)
- **Justification:** Open-source alternative to Codex, proven HumanEval performance
- **Frozen:** Yes (no fine-tuning, ensures feedback is only variable)

**Performance Baseline:**
- HumanEval pass@1: ~30% (from CodeGen paper)
- MBPP: Not reported but expected similar
- SWE-bench: Not applicable (model not designed for repo-level tasks)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `Salesforce/codegen-16B-mono`
- Code:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-16B-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-16B-mono")
```

#### Proposed Model

**Architecture:** Baseline + [No architectural change - this is a feedback correlation study, not a model improvement]

**Core Mechanism Implementation:**

This is an EXISTENCE hypothesis testing correlation measurement infrastructure, not a novel model architecture.

**Pseudo-code for Correlation Measurement Pipeline:**

```python
# Step 1: Generate code samples
def generate_samples(dataset, model, n=100):
    samples = []
    for problem in dataset.sample(n):
        code = model.generate(problem.prompt)
        samples.append((problem, code))
    return samples

# Step 2: Collect execution feedback
def collect_execution_feedback(samples):
    results = []
    for problem, code in samples:
        passed = run_tests(code, problem.tests)
        results.append(1 if passed else 0)
    return results

# Step 3: Collect AI reward feedback
def collect_ai_feedback(samples, reward_model):
    results = []
    for problem, code in samples:
        score = reward_model.score(problem.prompt, code)
        results.append(score)
    return results

# Step 4: Collect human ratings (simulated for PoC)
def collect_human_feedback(samples, num_raters=3):
    # PoC: Simulate with heuristic (real: MTurk/expert raters)
    results = []
    for problem, code in samples:
        ratings = simulate_human_ratings(code, num_raters)
        results.append(np.mean(ratings))
    return results

# Step 5: Compute correlations
def compute_correlations(exec_feedback, ai_feedback, human_feedback):
    correlations = {
        'exec_human': pearsonr(exec_feedback, human_feedback),
        'ai_human': pearsonr(ai_feedback, human_feedback),
        'exec_ai': pearsonr(exec_feedback, ai_feedback)
    }
    return correlations

# Step 6: Bootstrap confidence intervals
def bootstrap_ci(data1, data2, n_iterations=1000):
    rs = []
    for _ in range(n_iterations):
        idx = np.random.choice(len(data1), len(data1), replace=True)
        r, _ = pearsonr(data1[idx], data2[idx])
        rs.append(r)
    return np.percentile(rs, [2.5, 97.5])
```

### Training Protocol

**No training required** - This is a frozen model evaluation study.

**Evaluation-only protocol:**
1. Load frozen CodeGen-16B-mono checkpoint
2. Generate 100 samples per dataset (temperature=0.8, top_p=0.95)
3. Collect feedback from 3 modalities per sample
4. Compute statistics

**Computational Requirements:**
- GPU: 1x A100 40GB (for model inference)
- Time: ~2-4 hours total (100 samples × 3 datasets × ~30s/sample)
- Storage: ~10GB (model weights + generated samples)

### Evaluation

**Metrics:**

1. **Primary Metrics (Gate Success):**
   - Pairwise Pearson correlations (execution-human, AI-human, execution-AI)
   - p-values for each correlation (must be <0.05)
   - Bootstrap 95% confidence intervals

2. **Secondary Metrics (Quality Check):**
   - Inter-rater reliability: Cohen's kappa (must be >0.6)
   - Sample size confirmation: n=100 per dataset
   - Correlation variance: Check that CIs don't overlap 0

**Success Criteria (PoC):**
- **Primary:** All three pairwise correlations have p<0.05 (statistically significant)
- **Secondary:** Cohen's kappa >0.6 (human ratings reliable)

**Expected Results:**
- Correlations should be measurable (not pure noise)
- Existence of correlation structure validated
- Foundation for H-M1, H-M2, H-M3 mechanism hypotheses

**Statistical Tests:**
- Pearson r for correlations
- Bootstrap resampling for confidence intervals (1000 iterations)
- Cohen's kappa for inter-rater reliability

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical correlation analysis
- Library: `scipy.stats`, `sklearn.metrics`, `numpy`
- Code:
```python
from scipy.stats import pearsonr
from sklearn.metrics import cohen_kappa_score
import numpy as np

# Correlation with CI
r, p = pearsonr(data1, data2)
ci = bootstrap_ci(data1, data2, n_iterations=1000)

# Inter-rater reliability
kappa = cohen_kappa_score(rater1, rater2)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** 
  - Correlation matrix heatmap (3×3: execution, AI, human)
  - Separate matrices for each dataset (HumanEval, MBPP, SWE-bench)
  - Color scale: -1 (red) to +1 (green)
  - Annotations: r values + p-values

#### Additional Figures (LLM Autonomous)

1. **Scatter Plots:** Pairwise feedback comparisons
   - execution vs human (3 plots, one per dataset)
   - AI vs human (3 plots, one per dataset)
   - execution vs AI (3 plots, one per dataset)
   - Regression lines + 95% CI bands

2. **Distribution Plots:**
   - Histogram of each feedback modality per dataset
   - Box plots comparing feedback distributions across datasets

3. **Bootstrap CI Visualization:**
   - Bar chart: correlation r values with error bars (95% CI)
   - Grouped by dataset

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error ✓
2. All correlation p-values < 0.05 ✓
3. Cohen's kappa > 0.6 ✓

**If ANY condition fails:**
- p-value ≥ 0.05: Correlations are noise → ABANDON per gate
- Kappa ≤ 0.6: Human feedback unreliable → ABANDON per assumption A1
- Runtime error: Debug and retry (not a hypothesis failure)

---

## Appendix: Reference Implementations

### Official Benchmark Implementations

1. **HumanEval**
   - Repo: https://github.com/openai/human-eval
   - Key file: `human_eval/data/HumanEval.jsonl.gz`
   - Evaluation: `human_eval/evaluation.py`

2. **MBPP**
   - Repo: https://github.com/google-research/google-research/tree/master/mbpp
   - Key file: `mbpp/mbpp.json`
   - Evaluation: Standard Python unit tests

3. **SWE-bench**
   - Repo: https://github.com/princeton-nlp/SWE-bench
   - Key file: Dataset loading via HuggingFace
   - Evaluation: Repository-specific test harnesses

### Correlation Analysis References

- **CodeRL (Le et al. 2022):** Execution-based RL for code generation
  - Repo: https://github.com/salesforce/CodeRL
  - Key insight: Execution feedback alone achieves 70-80% pass@1

- **Statistical Power Analysis:**
  - Sample size n=100 provides 80% power for r=0.3 detection (α=0.05)
  - Reference: Cohen (1988) statistical power analysis

- **Human Evaluation Standards:**
  - Inter-rater reliability (Cohen's kappa) > 0.6 for acceptable agreement
  - 3 raters standard for code quality assessment

---

## State Information

**State File:** verification_state.yaml (managed via ABLATION MODE)
**Date:** 2026-08-25T00:00:00Z

### Workflow History for This Hypothesis
- 2026-08-25: Phase 2C started, experiment design completed (no MCP)

---

*MCP Tools Used: None (MCP unavailable - designed from verification plan)*
*All specifications grounded in Phase 2B verification protocol and standard benchmarks*
*Next Phase: Phase 3 - Implementation Planning*
