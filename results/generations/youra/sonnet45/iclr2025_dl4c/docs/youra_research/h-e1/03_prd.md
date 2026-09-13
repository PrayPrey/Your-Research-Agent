---
name: Product Requirements Document - H-E1 Structural Signal Existence
description: PRD for implementing structural coverage prediction experiment
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
phase: Phase 3 Implementation Planning
created_at: 2026-03-18
stepsCompleted:
  - step-01-problem-definition
  - step-02-requirements-elicitation
  - step-03-non-functional-requirements
  - step-04-success-criteria
  - step-05-review-and-finalize
---

# Product Requirements Document: H-E1 Structural Signal Existence

**Hypothesis:** Under EvalPlus HumanEval evaluation conditions, if static structural features (12-dim vector: cyclomatic complexity, branch density, nesting depth, AST entropy, etc.) are extracted from LLM-generated code solutions, then these features will explain at least 50% of test coverage residual variance (median residual variance ratio ≥ 0.5 across ≥70% of tasks) after controlling for semantic equivalence clusters and task difficulty, demonstrating that structural complexity is a primary predictor of test coverage outcomes distinct from semantic correctness.

---

## 1. Executive Summary

### Purpose
Validate the existence of a structural signal in code complexity that predicts test coverage outcomes for LLM-generated code, independent of semantic correctness.

### Scope
- **In Scope:** Coverage data collection, structural feature extraction, Ridge regression modeling, variance decomposition analysis
- **Out of Scope:** Neural network approaches, runtime analysis, test generation, model fine-tuning

### Success Definition
Median residual variance ratio ≥ 0.5 with 95% CI [0.45, 0.60] across ≥70% of 164 HumanEval tasks, demonstrating structural features explain substantial coverage variance beyond semantic clusters.

---

## 2. Problem Statement

### Context
LLM code generators achieve high functional correctness but coverage prediction remains unexplored. If structural complexity predicts coverage independent of semantics, it enables test adequacy prediction without execution.

### Challenges
1. Coverage data not readily available for LLM-generated code
2. Semantic equivalence must be controlled to isolate structural signal
3. 12 structural features may exhibit multicollinearity
4. Task difficulty confounds structural effects

### Target Users
ML researchers, code generation tool developers, software testing researchers

---

## 3. Functional Requirements

### FR-1: Data Collection & Preprocessing

**FR-1.1: Coverage Data Acquisition**
- **Source:** Microsoft CoverageEval dataset (164 HumanEval problems with coverage annotations)
- **Alternative:** EvalPlus + coverage.py instrumentation for generated solutions
- **Format:** JSON files with statement coverage %, branch coverage %, coverage sequences
- **Validation:** Pre-flight check on 1 task to verify coverage.py integration

**FR-1.2: Solution Generation (EvalPlus path)**
- **Models:** CodeLlama-34B, StarCoder2-15B, DeepSeek-Coder-33B
- **Sampling:** 10 solutions per model per task = 4,920 total solutions
- **Infrastructure:** vLLM for efficient generation
- **Output:** Python code strings with task_id, model, solution_id metadata

**FR-1.3: Semantic Clustering**
- **Method:** I/O trace equivalence clustering
- **Test Inputs:** 100 test inputs per task from EvalPlus
- **Output:** Cluster assignments for controlling functional equivalence
- **Validation:** Manual inspection of 10 tasks for within-cluster variance

**FR-1.4: Task Difficulty Quantification**
- **Metrics:** Token length, reference complexity, pass rate
- **Composite Score:** Weighted combination of 3 metrics
- **Sensitivity Analysis:** Test 3 difficulty operationalizations

### FR-2: Structural Feature Extraction

**FR-2.1: Core Complexity Metrics (radon)**
- **Features:** Cyclomatic complexity (McCabe), SLOC, logical LOC, comment ratio
- **Library:** `radon` Python package
- **Output:** Per-solution 4-dimensional feature vector

**FR-2.2: AST-Based Metrics (tree-sitter)**
- **Features:** Nesting depth, branch density, AST entropy, function count, early returns, exception handlers, defensive branches, code-to-complexity ratio
- **Library:** `tree-sitter` + `tree-sitter-python`
- **Output:** Per-solution 8-dimensional feature vector
- **Validation:** VIF < 5 for multicollinearity check

**FR-2.3: Feature Preprocessing**
- **Normalization:** StandardScaler (mean=0, std=1)
- **Missing Values:** Impute with task-level median
- **Outliers:** Winsorize at 1st/99th percentile

### FR-3: Baseline Models

**FR-3.1: Task-Level Prior Baseline**
- **Method:** Predict mean coverage per task (no structural information)
- **Justification:** Simplest baseline controlling task difficulty only
- **Implementation:** Group by task_id, compute mean coverage
- **Evaluation:** R² on held-out tasks

**FR-3.2: Length-Based Baseline**
- **Method:** Simple linear regression (coverage ~ SLOC)
- **Justification:** Naive correlation baseline
- **Evaluation:** R² and Pearson correlation

### FR-4: Proposed Model

**FR-4.1: Structural Feature Regression**
- **Architecture:** Ridge regression (L2 regularization)
- **Features:** 12-dimensional structural feature vector + task difficulty covariates
- **Hyperparameters:**
  - Ridge alpha: 1.0 (default)
  - Solver: auto
  - Random seed: 42
- **Training:** Fit on coverage outcomes with task-level controls

**FR-4.2: Hierarchical Variance Decomposition**
- **Model 1:** Coverage ~ TaskDifficulty
- **Model 2:** Coverage ~ TaskDifficulty + StructuralFeatures
- **Model 3:** Coverage ~ TaskDifficulty + StructuralFeatures + SemanticCluster
- **Analysis:** Compute R²_marginal / R²_conditional per task

### FR-5: Evaluation & Validation

**FR-5.1: Primary Metric - Median Residual Variance Ratio**
- **Definition:** median(R²_marginal / R²_conditional) across 164 tasks
- **R²_marginal:** Variance explained by structural features only
- **R²_conditional:** Variance explained by structural + semantic cluster
- **Success Threshold:** ≥ 0.5 with 95% CI [0.45, 0.60]

**FR-5.2: Secondary Metric - Task Coverage**
- **Definition:** Fraction of tasks with ratio ≥ 0.4
- **Success Threshold:** ≥ 70% of tasks

**FR-5.3: Validation Metric - Hierarchical ΔR²**
- **Definition:** R²_full - R²_task_only
- **Success Threshold:** ΔR² ≥ 0.10

**FR-5.4: Quality Check - VIF**
- **Definition:** Variance Inflation Factor for 12 features
- **Success Threshold:** All VIF < 5

**FR-5.5: Cross-Validation**
- **Strategy:** Leave-One-Group-Out (LOGO) cross-validation at task level
- **Purpose:** Prevent overfitting to task-specific patterns

### FR-6: Visualization & Reporting

**FR-6.1: Required Gate Metrics Figure**
- **Type:** Bar chart
- **Content:** Actual median ratio vs. 0.5 threshold with 95% CI error bars
- **Output:** `h-e1/figures/gate_metrics.png`

**FR-6.2: Additional Diagnostic Figures**
- **Figure 1:** Per-task residual variance ratio distribution (histogram)
- **Figure 2:** Feature importance bar chart (Ridge coefficients)
- **Figure 3:** Structural complexity vs. coverage scatter plot
- **Figure 4:** Hierarchical regression ΔR² stacked bar chart
- **Output:** All saved to `h-e1/figures/`

**FR-6.3: Validation Report**
- **File:** `h-e1/04_validation.md`
- **Sections:** Executive Summary, Results, Gate Status, Figures, Limitations, Next Steps
- **Format:** Markdown with embedded figures

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- **Runtime:** < 2 hours for full experiment on single CPU
- **Memory:** < 16GB RAM for data processing and model training
- **Storage:** < 5GB for datasets, features, and results

### NFR-2: Reproducibility
- **Random Seed:** Fix all random seeds (42)
- **Environment:** Pin all package versions in requirements.txt
- **Data Versioning:** Record dataset commit hashes / download timestamps
- **Code Organization:** Modular functions for each FR

### NFR-3: Maintainability
- **Code Style:** Follow PEP 8
- **Documentation:** Docstrings for all functions with Args/Returns
- **Testing:** Unit tests for feature extraction, metric computation
- **Logging:** INFO-level logging for progress tracking

### NFR-4: Portability
- **Platform:** Linux/macOS compatible
- **Dependencies:** Python 3.9+, standard scientific stack (numpy, sklearn, pandas)
- **GPU:** Not required (CPU-only Ridge regression)

### NFR-5: Safety
- **Execution:** No code execution of LLM solutions in main pipeline (use CoverageEval pre-computed data)
- **Sandboxing:** If generating solutions, use Docker-based safe execution (EvalPlus standard)
- **Data Integrity:** Validate coverage data ranges (0-100%), detect anomalies

---

## 5. Data Specifications

### Input Data

**Dataset 1: Microsoft CoverageEval**
- **Source:** `git clone https://github.com/microsoft/coverage-eval.git`
- **Format:** JSON files, one per problem
- **Schema:**
  ```python
  {
    "task_id": "HumanEval/0",
    "canonical_solution": "def has_close_elements(numbers, threshold): ...",
    "tests": [...],
    "coverage": {
      "statement_coverage": 85.7,
      "branch_coverage": 75.0,
      "coverage_executed": [1, 2, 3, 5, 6],
      "coverage_sequence": "1,2,3,5,6",
      "branch_sequence": "1T,2F,3T"
    }
  }
  ```
- **Loading:**
  ```python
  import sys
  sys.path.append('coverage-eval')
  from utils import read_problems
  problems = read_problems()
  ```

**Dataset 2 (Alternative): EvalPlus HumanEval**
- **Source:** `pip install evalplus`
- **Format:** Python dict via `get_human_eval_plus()`
- **Schema:**
  ```python
  {
    "task_id": "HumanEval/0",
    "prompt": "def has_close_elements(numbers: List[float], threshold: float) -> bool:\n    ...",
    "entry_point": "has_close_elements",
    "canonical_solution": "...",
    "test": "def check(candidate): ..."
  }
  ```

### Output Data

**File 1: Features DataFrame**
- **Path:** `h-e1/data/features.csv`
- **Schema:** task_id, model, solution_id, coverage, [12 structural features], semantic_cluster, task_difficulty
- **Format:** CSV with header

**File 2: Model Artifacts**
- **Path:** `h-e1/models/ridge_model.pkl`
- **Content:** Trained Ridge model + scaler
- **Format:** Pickle (scikit-learn)

**File 3: Results JSON**
- **Path:** `h-e1/results/metrics.json`
- **Schema:**
  ```json
  {
    "median_residual_variance_ratio": 0.52,
    "ci_95": [0.48, 0.56],
    "task_coverage_above_04": 0.73,
    "hierarchical_delta_r2": 0.12,
    "vif_max": 3.8,
    "gate_status": "PASS"
  }
  ```

---

## 6. Dependencies

### Python Packages
```
radon==6.0.1
tree-sitter==0.22.3
tree-sitter-python==0.22.0
scikit-learn==1.5.0
numpy==1.26.4
pandas==2.2.0
matplotlib==3.9.0
seaborn==0.13.0
statsmodels==0.14.1
```

### External Repositories
- **CoverageEval:** https://github.com/microsoft/coverage-eval (MIT License)
- **EvalPlus:** https://github.com/evalplus/evalplus (Apache 2.0)

### System Requirements
- **Python:** 3.9 or higher
- **OS:** Linux (Ubuntu 20.04+) or macOS
- **CPU:** 4+ cores recommended
- **RAM:** 16GB minimum
- **Storage:** 10GB free space

---

## 7. Success Criteria

### Gate Condition (MUST_WORK)
✅ **Primary:** Median residual variance ratio ≥ 0.5 with 95% CI [0.45, 0.60]
✅ **Secondary:** ≥70% of tasks above 0.4 threshold
✅ **Validation:** Hierarchical ΔR² ≥ 0.10
✅ **Quality:** VIF < 5 for all features

### PoC Success (Simplified)
✅ Code runs without error
✅ Proposed model R² > Baseline model R²

### Failure Conditions
❌ Median ratio < 0.4 → Structural signal insufficient, pipeline halts
❌ VIF ≥ 5 for multiple features → Multicollinearity issue, requires feature selection
❌ Task coverage < 50% → Signal not generalizable across tasks

---

## 8. Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Coverage data unavailable | HIGH | Pre-flight check on 1 task, use CoverageEval pre-computed data |
| Semantic clustering inadequate | MEDIUM | Manual inspection (10 tasks), within-cluster variance check |
| Task difficulty confounding | MEDIUM | Sensitivity analysis with 3 difficulty operationalizations |
| Feature multicollinearity | LOW | VIF check, remove features with VIF ≥ 5 |
| Classical metrics insufficient | LOW | GNN fallback if R² < 0.40 |

---

## 9. Out of Scope

- Neural network-based feature learning (GNN on CFG)
- Test case generation or augmentation
- Multi-language support (Python only)
- Model fine-tuning or training from scratch
- Runtime profiling or dynamic analysis
- Coverage-guided test synthesis

---

## 10. Appendix: Reference Implementations

### Primary References

1. **Microsoft CoverageEval**
   - URL: https://github.com/microsoft/coverage-eval
   - Paper: Tufano et al., "Predicting Code Coverage without Execution" (2023)
   - License: MIT

2. **EvalPlus Framework**
   - URL: https://github.com/evalplus/evalplus
   - Paper: Liu et al., NeurIPS 2023
   - License: Apache 2.0

3. **Radon (Complexity Metrics)**
   - URL: https://github.com/rubik/radon
   - Install: `pip install radon`

4. **Tree-sitter Python**
   - URL: https://github.com/tree-sitter/tree-sitter-python
   - Install: `pip install tree-sitter tree-sitter-python`

---

*PRD Generated for Phase 3 Implementation Planning | Anonymous Research Pipeline*
