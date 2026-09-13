# Product Requirements Document: h-e1

**Date:** 2026-08-25
**Author:** Phase 3 Pipeline
**Hypothesis:** h-e1 (EXISTENCE)
**Experiment Brief:** 02c_experiment_brief.md

---

## 1. Executive Summary

Build correlation measurement infrastructure to validate that pairwise correlations between execution, AI, and human feedback are measurable (not noise) across three code generation tasks (HumanEval, MBPP, SWE-bench). This is PoC validation for foundation hypothesis — establishes feasibility of feedback correlation analysis before mechanism hypotheses.

**Success Definition:** All three pairwise correlations (execution-human, AI-human, execution-AI) have p<0.05 across all datasets, and human inter-rater reliability Cohen's kappa >0.6.

---

## 2. Core Requirements

### 2.1 Functional Requirements

**FR-1: Dataset Loading**
- Load HumanEval (164 problems, use first 100)
- Load MBPP (974 problems, random sample 100)
- Load SWE-bench (2,294 issues, random sample 100)
- Standardize format: (problem_id, prompt, test_cases)

**FR-2: Code Generation**
- Load frozen CodeGen-16B-mono checkpoint
- Generate 1 sample per problem (temperature=0.8, top_p=0.95)
- Cache generated code for reproducibility
- Total: 300 code samples (100 per dataset)

**FR-3: Execution Feedback Collection**
- Run test cases for each generated code sample
- Record binary pass/fail per sample
- Handle execution errors (timeout, syntax error) as fail
- Output: 300 binary values (0/1)

**FR-4: AI Feedback Collection**
- Load reward model (CodeBERT or GPT-3.5-turbo as judge)
- Score each (problem, code) pair
- Normalize scores to [0, 1] range
- Output: 300 continuous scores

**FR-5: Human Feedback Collection (Simulated for PoC)**
- Simulate 3 raters per sample with heuristic:
  - Base score: execution result (0 or 1)
  - Add noise: ±0.2 uniform random per rater
  - Clip to [0, 1] range
- Compute mean rating per sample
- Compute inter-rater reliability (Cohen's kappa) across all samples
- Output: 300 averaged ratings + kappa statistic

**FR-6: Correlation Analysis**
- Compute Pearson r for all 3 pairwise combinations per dataset
- Compute p-values for each correlation
- Bootstrap 95% confidence intervals (1000 iterations)
- Output: 3×3 correlation matrix per dataset + CIs

**FR-7: Visualization**
- Generate correlation matrix heatmap (3 datasets × 3×3 matrix)
- Generate scatter plots (9 total: 3 pairs × 3 datasets)
- Generate bootstrap CI bar chart
- Generate distribution plots (histograms, boxplots)
- Save all figures to `docs/youra_research/h-e1/figures/`

**FR-8: Gate Evaluation**
- Check all correlation p-values < 0.05
- Check Cohen's kappa > 0.6
- Report PASS/FAIL with detailed statistics
- Write results to `04_validation.md`

### 2.2 Non-Functional Requirements

**NFR-1: Reproducibility**
- Fix random seeds for sampling and bootstrap
- Cache model outputs and intermediate results
- Log all hyperparameters and dataset versions

**NFR-2: Performance**
- Complete end-to-end run in <4 hours on 1x A100 40GB
- Batch generation for efficiency (batch_size=8)

**NFR-3: Error Handling**
- Gracefully handle model loading failures (fallback to smaller model)
- Handle dataset download failures (retry with exponential backoff)
- Continue on per-sample execution errors (mark as fail, log error)

**NFR-4: Code Quality**
- Modular design: separate modules for each FR
- Logging at INFO level for progress tracking
- Type hints for all functions
- Docstrings for public API

---

## 3. System Architecture Requirements

### 3.1 Components

1. **Dataset Manager** (`data_loader.py`)
   - Functions: `load_humaneval()`, `load_mbpp()`, `load_swe_bench()`
   - Input: None (downloads from HuggingFace/GitHub)
   - Output: List[(problem_id, prompt, test_cases)]

2. **Code Generator** (`generator.py`)
   - Class: `CodeGenModel`
   - Methods: `generate(prompt)`, `batch_generate(prompts)`
   - Input: Problem prompts
   - Output: Generated code strings

3. **Feedback Collectors** (`feedback.py`)
   - Functions: `execute_code(code, tests)`, `ai_score(prompt, code)`, `simulate_human_ratings(code, execution_result)`
   - Input: Generated code + context
   - Output: Feedback values

4. **Correlation Analyzer** (`analysis.py`)
   - Functions: `compute_correlations(data1, data2, data3)`, `bootstrap_ci(data1, data2)`
   - Input: Three feedback arrays per dataset
   - Output: Correlation matrix + CIs

5. **Visualizer** (`visualize.py`)
   - Functions: `plot_correlation_matrix(corr_data)`, `plot_scatter(x, y)`, `plot_distributions(data)`
   - Input: Analysis results
   - Output: PNG files saved to `figures/`

6. **Main Experiment Runner** (`run_experiment.py`)
   - Orchestrates all components
   - Implements gate evaluation logic
   - Writes `04_validation.md`

### 3.2 Data Flow

```
[Dataset Loaders] → [Code Generator] → [Feedback Collectors] → [Correlation Analyzer] → [Visualizer]
                                                                         ↓
                                                                 [Gate Evaluator] → 04_validation.md
```

### 3.3 External Dependencies

- `transformers==4.30.0` (CodeGen model)
- `datasets==2.12.0` (HuggingFace datasets)
- `scipy==1.10.0` (statistical tests)
- `scikit-learn==1.2.0` (Cohen's kappa)
- `numpy==1.24.0` (numerical operations)
- `matplotlib==3.7.0` (visualization)
- `seaborn==0.12.0` (heatmaps)
- `torch==2.0.0` (model inference)

---

## 4. Experiment Configuration Requirements

### 4.1 Hyperparameters

**Code Generation:**
- `temperature`: 0.8
- `top_p`: 0.95
- `max_tokens`: 512
- `batch_size`: 8

**Sampling:**
- HumanEval: First 100 problems (deterministic)
- MBPP: Random sample 100 (seed=42)
- SWE-bench: Random sample 100 (seed=42)

**Statistical:**
- Bootstrap iterations: 1000
- Confidence level: 95%
- Alpha threshold: 0.05

**Human Simulation:**
- Number of raters: 3
- Noise level: ±0.2 uniform

### 4.2 Compute Resources

- **GPU:** 1x NVIDIA A100 40GB
- **RAM:** 64GB
- **Storage:** 50GB (model weights + datasets + outputs)
- **Estimated Runtime:** 2-4 hours

### 4.3 File Structure

```
docs/youra_research/h-e1/
├── 02c_experiment_brief.md (input)
├── 03_prd.md (this file)
├── 03_architecture.md (generated)
├── 03_logic.md (generated)
├── 03_config.md (generated)
├── 03_tasks.yaml (generated)
├── code/
│   ├── data_loader.py
│   ├── generator.py
│   ├── feedback.py
│   ├── analysis.py
│   ├── visualize.py
│   ├── run_experiment.py
│   └── config.yaml
├── outputs/
│   ├── generated_samples.jsonl (cached code)
│   ├── feedback_results.jsonl
│   └── correlation_stats.json
├── figures/
│   ├── correlation_matrix_humaneval.png
│   ├── correlation_matrix_mbpp.png
│   ├── correlation_matrix_swe_bench.png
│   ├── scatter_exec_human_humaneval.png
│   └── ... (18 total figures)
└── 04_validation.md (final output)
```

---

## 5. Success Criteria

### 5.1 Gate Pass Conditions

**MUST_WORK Gate:**
1. All 9 pairwise correlations (3 pairs × 3 datasets) have p<0.05
2. Cohen's kappa for simulated human ratings >0.6
3. No runtime errors during experiment

**If ANY fails:**
- p≥0.05: Correlations are noise → ABANDON hypothesis
- Kappa ≤0.6: Human feedback unreliable → ABANDON per assumption A1
- Runtime error: Debug and retry (not hypothesis failure)

### 5.2 Expected Results

- Correlations should be measurable (r > 0.2, p < 0.05)
- Execution-human correlation likely strongest (aligned objective)
- AI-human correlation moderate (learned approximation)
- Execution-AI correlation weakest (different mechanisms)

---

## 6. Risk Mitigation

### 6.1 Technical Risks

**Risk:** CodeGen-16B-mono too large for available GPU
- **Mitigation:** Fallback to CodeGen-2B-mono (7x smaller, still validated on HumanEval)

**Risk:** SWE-bench samples fail execution due to complex environment setup
- **Mitigation:** Skip repo cloning, use pre-extracted test cases from dataset metadata

**Risk:** HuggingFace datasets API rate limits during download
- **Mitigation:** Cache datasets locally, retry with exponential backoff

### 6.2 Statistical Risks

**Risk:** Simulated human ratings too correlated with execution (heuristic too simple)
- **Mitigation:** Add independent noise term to decorrelate (±0.2 uniform)

**Risk:** Sample size n=100 insufficient for weak correlations
- **Mitigation:** Power analysis validated for r=0.3; if correlations weaker, CI will overlap zero and trigger gate failure as expected

---

## 7. Deliverables

### 7.1 Code Deliverables
- 6 Python modules (listed in Section 3.1)
- `config.yaml` with all hyperparameters
- `requirements.txt` with pinned dependencies
- `README.md` with setup and run instructions

### 7.2 Output Deliverables
- 300 generated code samples (cached in `outputs/`)
- 900 feedback values (3 modalities × 300 samples)
- 9 correlation statistics (3 pairs × 3 datasets)
- 18 PNG figures
- `04_validation.md` with gate evaluation result

### 7.3 Documentation Deliverables
- `03_architecture.md` (system design)
- `03_logic.md` (tensor shapes, API contracts)
- `03_config.md` (hyperparameter rationale)

---

## 8. Out of Scope

**Explicitly NOT included in this PoC:**
- Real human annotation (MTurk/expert raters) — simulated only
- Fine-tuning or training any models — frozen checkpoint only
- Advanced reward models — using off-the-shelf CodeBERT or GPT-3.5-turbo
- Cross-dataset transfer analysis — each dataset analyzed independently
- Causal analysis of correlation differences — existence check only

---

## 9. Acceptance Criteria

**Phase 4 Coder MUST deliver:**
1. All FR-1 through FR-8 implemented
2. Code passes static type checking (`mypy`)
3. Experiment runs end-to-end without manual intervention
4. Gate evaluation result clearly stated in `04_validation.md`
5. All figures generated and saved to `figures/`

**Phase 4 Validator MUST verify:**
1. Reproducibility: Re-running with same seeds produces identical results
2. Statistical validity: Bootstrap CIs are symmetric, p-values in [0,1]
3. Data integrity: 300 samples per dataset, no NaN values
4. Figure quality: All plots have labels, legends, and readable font size

---

**Document Version:** 1.0
**Source:** 02c_experiment_brief.md (Phase 2C)
**Next Steps:** Generate Architecture, Logic, and Config documents → Phase 4 Implementation
