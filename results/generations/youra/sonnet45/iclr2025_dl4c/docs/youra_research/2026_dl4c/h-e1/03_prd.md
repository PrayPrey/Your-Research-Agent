# Product Requirements Document: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-18
**Author:** Phase 3 Implementation Planning

---

## Executive Summary

This PRD defines requirements for implementing H-E1, an existence proof-of-concept experiment testing whether code generation models cluster in 3D performance space according to their alignment method type. The experiment evaluates 6-8 post-alignment models across correctness, complexity, and efficiency dimensions on HumanEval+ benchmark, measuring statistical clustering significance via Cohen's d effect size.

**Core Question:** Do alignment methods (execution-based, preference-based, baseline) produce detectable "objective function signatures" in model outputs?

**Success Criteria:** Cohen's d > 1.5σ (moderate effect) indicating statistically significant clustering by alignment method type.

---

## Problem Statement

### Context
Current alignment methods for code generation models vary in their feedback signals (execution-based vs preference-based), but it's unclear whether these create systematically different output patterns. Understanding alignment signatures is critical for:
1. Diagnosing model behavior and capabilities
2. Selecting appropriate models for specific use cases
3. Designing better alignment strategies

### Hypothesis Statement
Under code generation evaluation conditions (Python function-level tasks, HumanEval+ benchmark), if we measure 6-8 post-alignment models across correctness, complexity, and efficiency dimensions, then models will cluster in 3D performance space according to alignment method type (execution-based, preference-based, unaligned baseline) with statistically significant intercluster distance > 1.5σ (Cohen's d), because feedback signals during alignment shape output distributions toward implicit optimization objectives.

### Gate Condition
**MUST_WORK**: This hypothesis MUST pass for the pipeline to continue. If Cohen's d < 1.5σ, the entire hypothesis loop will HALT and route back to Phase 0.

---

## Functional Requirements

### FR-1: Data Collection and Preparation
**Priority:** CRITICAL
**Complexity:** Medium

Load HumanEval+ benchmark dataset (164 programming problems) from EvalPlus package.

**Acceptance Criteria:**
- Dataset loaded via `evalplus` package or HuggingFace datasets
- 164 problems with prompts, canonical solutions, and test suites
- Average 764.1 tests per problem (81× more than original HumanEval)
- No preprocessing required (problems pre-formatted)

**Dependencies:** None

---

### FR-2: Model Selection and Loading
**Priority:** CRITICAL
**Complexity:** High

Load 6-8 pre-trained code generation models from HuggingFace across three alignment categories.

**Model Requirements:**

**Execution-Focused Models (2-3 models):**
- SelfCodeAlign-7B
- StepCoder
- CodeLlama-Python-7B-Instruct

**Preference-Focused Models (2-3 models):**
- DPO/RLAIF-trained models from HuggingFace
- Candidates: CodeLlama-DPO variants, RLHF instruction-tuned models

**Baseline Models (1-2 models):**
- CodeLlama-7B-Base
- StarCoder-Base

**Acceptance Criteria:**
- All models loaded via HuggingFace Transformers
- Models support temperature-based sampling (temperature=0.8, top_p=0.95)
- Max tokens: 512 (function-level code completion)
- Device mapping configured for single GPU execution

**Dependencies:** FR-1 (dataset loaded)

---

### FR-3: Code Generation with Sampling
**Priority:** CRITICAL
**Complexity:** High

Generate 60-80 code samples per model per task with temperature-based sampling for diversity.

**Acceptance Criteria:**
- Temperature: 0.8 for sampling diversity
- Top_p: 0.95 for nucleus sampling
- Samples per model: 60-80 per task (total ~10,000-13,000 samples per model)
- Sequential generation (batch size: 1)
- Input: Function signature + docstring from HumanEval+ prompt
- Output: Function body completion

**Dependencies:** FR-2 (models loaded)

---

### FR-4: Correctness Profiling (Pass@k)
**Priority:** CRITICAL
**Complexity:** Medium

Execute generated code samples against HumanEval+ test suites and compute pass@k metric.

**Acceptance Criteria:**
- Test execution with 3.0s timeout per sample
- Pass@k calculation using unbiased estimator: `pass@k = 1 - C(n-c, k) / C(n, k)`
- Where n=total samples, c=correct samples, k=samples to select
- Parallel execution with 4 workers
- Pass results stored per model per task

**Dependencies:** FR-3 (code generated)

---

### FR-5: Complexity Profiling
**Priority:** CRITICAL
**Complexity:** Medium

Measure code complexity using cyclomatic complexity and AST depth metrics.

**Acceptance Criteria:**
- Cyclomatic complexity via `radon` package (cc_visit)
- AST depth via `lizard` package
- Metrics computed for all generated samples
- Average complexity scores per model per task
- Typical ranges: Cyclomatic 2-10, AST depth 3-15

**Dependencies:** FR-3 (code generated)

---

### FR-6: Efficiency Profiling
**Priority:** CRITICAL
**Complexity:** Medium

Profile runtime and memory usage for generated code samples.

**Acceptance Criteria:**
- Runtime profiling via `cProfile` (Python built-in)
- Memory profiling via `tracemalloc` (Python built-in)
- Metrics computed for all correctly executing samples
- Average efficiency scores per model per task
- Expected ranges: Runtime 0.01-1.0s, memory varies by task

**Dependencies:** FR-3 (code generated)

---

### FR-7: Performance Signature Extraction
**Priority:** CRITICAL
**Complexity:** Low

Aggregate correctness, complexity, and efficiency metrics into 3D performance signatures.

**Acceptance Criteria:**
- Each model represented by (correctness, complexity, efficiency) vector
- Correctness: pass@k success rate (0-1 range)
- Complexity: (cyclomatic, ast_depth) tuple averaged across samples
- Efficiency: (runtime, memory) tuple averaged across correct samples
- Signatures stored as flat vectors for clustering

**Dependencies:** FR-4, FR-5, FR-6 (all profiling complete)

---

### FR-8: Clustering Analysis
**Priority:** CRITICAL
**Complexity:** Medium

Apply PCA dimensionality reduction and k-means clustering to performance signatures.

**Acceptance Criteria:**
- Standardization via `StandardScaler` (sklearn)
- PCA to 3 components for visualization
- k-means clustering with k=3 (3 alignment types)
- Random state: 42 for reproducibility
- Cluster labels assigned to each model

**Dependencies:** FR-7 (signatures extracted)

---

### FR-9: Effect Size Computation (Primary Metric)
**Priority:** CRITICAL
**Complexity:** Medium

Compute Cohen's d effect size measuring intercluster distance relative to intracluster variance.

**Acceptance Criteria:**
- Cohen's d formula: `d = (μ_between - μ_within) / σ_pooled`
- Pooled standard deviation across all clusters
- Target threshold: d > 1.5σ (moderate effect) or d > 2.5σ (strong effect)
- **Gate evaluation**: MUST_WORK requires d > 1.5σ

**Dependencies:** FR-8 (clustering complete)

---

### FR-10: Secondary Metrics
**Priority:** HIGH
**Complexity:** Low

Compute silhouette score and alignment method purity for cluster quality assessment.

**Acceptance Criteria:**
- Silhouette score via sklearn.metrics (range: [-1, 1], target: > 0.3)
- Alignment method purity: % of clusters dominated by single alignment type (target: > 70%)
- Alignment variance vs base model variance comparison

**Dependencies:** FR-8 (clustering complete)

---

### FR-11: Visualization Generation
**Priority:** HIGH
**Complexity:** Medium

Generate 5 visualizations showing clustering analysis results.

**Required Figures:**

1. **3D Scatter Plot**: PCA-reduced performance space
   - Axes: PC1, PC2, PC3
   - Colors: Execution (blue), Preference (red), Baseline (green)
   - Shows visual cluster separation

2. **Heatmap**: Model × Dimension performance matrix
   - Rows: 6-8 models
   - Columns: Correctness, Complexity, Efficiency
   - Shows per-dimension dominance patterns

3. **Box Plots**: Metric distributions by alignment type
   - 3 groups: Execution, Preference, Baseline
   - Shows within-group variance vs between-group separation

4. **Dendrogram**: Hierarchical clustering of models
   - Shows natural grouping structure

5. **Effect Size Confidence**: Cohen's d with bootstrapped confidence intervals
   - Shows statistical strength of clustering

**Acceptance Criteria:**
- All figures saved to `{hypothesis_folder}/figures/`
- High-resolution PNG format (300 DPI minimum)
- Clear labels and legends
- Color-blind friendly palette

**Dependencies:** FR-8, FR-9, FR-10 (all metrics computed)

---

### FR-12: Gate Metrics Comparison (Mandatory Visualization)
**Priority:** CRITICAL
**Complexity:** Low

Generate bar chart comparing target vs actual gate metrics.

**Acceptance Criteria:**
- Bar chart showing:
  - Target: Cohen's d = 1.5σ (minimum threshold)
  - Actual: Measured Cohen's d value
  - Color-coded: Green if pass, Red if fail
- Saved to `{hypothesis_folder}/figures/gate_metrics.png`

**Dependencies:** FR-9 (effect size computed)

---

## Non-Functional Requirements

### NFR-1: Performance
- Single GPU execution (CUDA_VISIBLE_DEVICES set)
- Total runtime: ~10-15 GPU-hours (depends on model count and sampling)
- Memory: Sufficient for 7B parameter models (requires ~14GB GPU RAM)

### NFR-2: Reproducibility
- Fixed random seed: 42 for all stochastic operations
- Deterministic k-means clustering (random_state=42)
- Consistent sampling (temperature=0.8, top_p=0.95)

### NFR-3: Data Integrity
- All generated samples stored with metadata (model, task, timestamp)
- Profiling results saved incrementally (CSV format)
- Checkpointing for long-running generation processes

### NFR-4: Code Quality
- Type hints for all function signatures
- Docstrings following Google style
- Error handling for model loading, generation, profiling failures
- Logging via print statements (LIGHT tier)

### NFR-5: Infrastructure (LIGHT Tier)
- Configuration: Hardcoded constants or argparse
- Logging: print statements + CSV output
- Testing: Smoke tests (basic execution validation)
- No YAML config, no WandB, no unit tests required

---

## Success Criteria

### Primary Success Criteria (Gate Evaluation)
1. **Cohen's d > 1.5σ**: Statistically significant clustering by alignment method (**MUST_WORK gate**)
2. Code executes without errors on single GPU
3. All 6-8 models generate samples successfully

### Secondary Success Criteria (Quality Indicators)
1. Silhouette score > 0.3 (reasonable cluster quality)
2. Alignment method purity > 70% (clear alignment-based grouping)
3. Alignment method variance >> base model variance (alignment matters more than architecture)

### Failure Criteria (Gate Failure → HALT Pipeline)
1. Cohen's d < 1.5σ → No detectable clustering exists
2. Language confounds dominate alignment signals
3. Insufficient sampling diversity or execution failures

---

## Expected Baseline Performance

### Pass@k Scores (from EvalPlus leaderboard)
- HumanEval+ pass@1: 30-70% (varies by model)
- Source: evalplus/humanevalplus dataset card

### Complexity Metrics (from radon documentation)
- Cyclomatic complexity: 2-10 (typical Python functions)
- AST depth: 3-15 (typical Python functions)

### Runtime (from ECE Waterloo performance analysis)
- Function-level code: 0.01-1.0s execution time

---

## Technical Constraints

### Model Constraints
- All models must be 7B parameter range (GPU memory limits)
- Python-only code generation (no cross-language comparison)
- Open-source models from HuggingFace (no API dependencies)

### Dataset Constraints
- HumanEval+ only (164 tasks)
- No MBPP+/BigCodeBench in this PoC
- No data augmentation or modification

### Computational Constraints
- Single GPU execution (user provides CUDA_VISIBLE_DEVICES)
- No distributed training or multi-GPU inference
- No cloud API calls (all local execution)

---

## Dependencies

### External Dependencies
- **Python packages**: evalplus, transformers, torch, radon, lizard, cProfile, tracemalloc, sklearn, scipy, numpy, matplotlib, pandas
- **Hardware**: Single GPU with ≥14GB VRAM (for 7B models)
- **Storage**: ~100GB for models and generated samples

### Internal Dependencies
- Phase 2C experiment brief (02c_experiment_brief.md) - COMPLETED
- verification_state.yaml - EXISTS

---

## Out of Scope

### Explicitly NOT Included
1. Model training or fine-tuning (evaluation only)
2. MBPP+/BigCodeBench benchmarks (HumanEval+ only for PoC)
3. Cross-language analysis (Python only)
4. Hyperparameter tuning (fixed temperature=0.8)
5. Advanced infrastructure (WandB, YAML config, unit tests)

---

## Risk Assessment

### High Risk
- **R1**: Model availability on HuggingFace
  - Mitigation: Verify all models accessible before FR-2 execution

- **R2**: GPU memory constraints with 7B models
  - Mitigation: Sequential loading/unloading of models

### Medium Risk
- **R3**: Execution timeout failures affecting pass@k
  - Mitigation: 3.0s timeout with parallel workers (4)

- **R4**: Insufficient clustering separation (Cohen's d < 1.5σ)
  - Mitigation: This is the hypothesis test - failure means HALT and return to Phase 0

### Low Risk
- **R5**: Package installation conflicts
  - Mitigation: Use virtual environment with pinned versions

---

## Implementation Notes

### Code Structure
- Standalone analysis pipeline (no model modification)
- 5-8 Python modules (config, data_loader, model_loader, profiling, clustering, visualization)
- Entry point: `run_experiment.py`

### Key Algorithms
1. **Pass@k**: Unbiased combinatorial estimator from openai/human-eval
2. **Clustering**: StandardScaler → PCA(n=3) → KMeans(k=3, random_state=42)
3. **Effect Size**: Pooled Cohen's d with between-cluster and within-cluster variance

### Integration Points
- Input: `02c_experiment_brief.md` (Phase 2C output)
- Output: `04_validation.md` (Phase 4 output)
- State: `verification_state.yaml` (gate evaluation results)

---

## Validation Checklist

Before Phase 4 implementation:
- [ ] All 6-8 models identified and accessible on HuggingFace
- [ ] GPU with ≥14GB VRAM available
- [ ] Python packages installable (evalplus, transformers, etc.)
- [ ] HumanEval+ dataset downloadable
- [ ] Output folder structure created

---

**End of PRD**

*This document is ready for Phase 3 Architecture/Logic/Config design.*
