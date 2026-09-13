# Product Requirements Document (PRD)

**Hypothesis:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-04-14  
**Author:** Anonymous
---

## Executive Summary

This PRD defines the implementation requirements for hypothesis h-e1, which validates dimensional separability in trustworthiness benchmarks through rank correlation analysis under perturbation-based stress testing.

**Objective:** Demonstrate that trustworthiness dimensions (truthfulness, fairness, hallucination, robustness) are truly distinct by showing asymmetric rank correlation shifts (|Δτ| ≥ 0.2) when models are evaluated under stress vs baseline conditions.

**Gate Type:** MUST_WORK (foundation hypothesis - all downstream hypotheses depend on this)

---

## Problem Statement

### Research Question

Do trustworthiness dimensions collapse to a single global quality factor, or are they truly separable constructs that respond differently to targeted stressors?

### Hypothesis Statement

Under perturbation-based stress testing, if trustworthiness benchmarks (TruthfulQA, BOLD, HaluEval, TextAttack) are evaluated before and after single-stressor application, then rank correlation shifts will show asymmetry |Δτ| ≥ 0.2 across dimension pairs, because truly distinct dimensions respond differently to targeted perturbations.

### Success Criteria

**Primary (PoC - Direction Only):**
- |Δτ| ≥ 0.2 in ≥2 pre-registered dimension pairs with p < 0.01

**Secondary:**
- Variance of Δτ across dimensions > 0.02

**Gate Condition:**
- MUST_WORK: Foundation hypothesis - failure triggers STOP and pivot to benchmarking redundancy study

---

## Functional Requirements

### FR-1: Multi-Benchmark Evaluation Suite

**Priority:** P0 (Critical)  
**Status:** Required

Implement evaluation pipeline for 4 trustworthiness benchmarks:

1. **TruthfulQA** (Truthfulness Dimension)
   - Dataset: HuggingFace `truthful_qa`, config `multiple_choice`
   - Tasks: MC1 (single-true), MC2 (multiple-true)
   - Metrics: MC1 accuracy, MC2 normalized probability mass
   - Sample size: 817 questions

2. **BOLD** (Fairness Dimension)
   - Dataset: HuggingFace `AlexaAI/bold`
   - Domains: 5 demographic domains (race, gender, religion, profession, political ideology)
   - Metrics: Sentiment bias, regard bias, toxicity bias
   - Sample size: 23,679 prompts

3. **HaluEval** (Hallucination/Truthfulness Dimension)
   - Dataset: HuggingFace `pminervini/HaluEval` or GitHub `RUCAIBox/HaluEval`
   - Tasks: QA, Dialogue, Summarization hallucination detection
   - Metrics: Hallucination detection accuracy per task
   - Sample size: 30,000 samples (10k per task)

4. **TextAttack** (Robustness Dimension + Stressor)
   - Framework: PyPI package `textattack`
   - Attack recipe: TextFooler (Jin et al., 2019)
   - Dual role: Baseline robustness evaluation + perturbation stressor
   - Perturbation constraints: Semantic similarity > 0.8, grammaticality preserved

**Acceptance Criteria:**
- All 4 benchmarks load successfully from HuggingFace/PyPI
- Evaluation metrics match official benchmark implementations
- Results saved per model per benchmark

---

### FR-2: Model Ensemble Evaluation

**Priority:** P0 (Critical)  
**Status:** Required

Evaluate 8+ diverse language models across architectures and scales:

**Required Models (Minimum 8):**

1. **GPT-2 Small** (117M) - `gpt2`
2. **GPT-2 Medium** (345M) - `gpt2-medium`
3. **Llama-2-7B** (7B) - `meta-llama/Llama-2-7b-hf`
4. **Mistral-7B-v0.1** (7B) - `mistralai/Mistral-7B-v0.1`
5. **Phi-2** (2.7B) - `microsoft/phi-2`
6. **Falcon-7B** (7B) - `tiiuae/falcon-7b`
7. **OPT-6.7B** (6.7B) - `facebook/opt-6.7b`
8. **Pythia-6.9B** (6.9B) - `EleutherAI/pythia-6.9b`

**Architecture Diversity:**
- GPT-style (GPT-2, OPT, Pythia)
- Llama-style with RoPE (Llama-2)
- Sliding window attention (Mistral)
- Multi-query attention (Falcon)
- Compact efficient models (Phi-2)

**Performance Range:**
- Expected baseline range: [0.3, 0.7] (within required [0.2, 0.9])

**Loading Requirements:**
- HuggingFace `transformers` library
- FP16 precision for efficiency
- Auto device mapping (single GPU via CUDA_VISIBLE_DEVICES)
- Batch size: 1-4 depending on model size

**Acceptance Criteria:**
- All 8+ models load successfully
- Models span 117M to 7B parameters
- Architecture diversity verified
- All models support all 4 benchmark evaluations

---

### FR-3: Baseline Evaluation (No Stress)

**Priority:** P0 (Critical)  
**Status:** Required

Evaluate all models on all benchmarks under baseline (non-perturbed) conditions:

**Evaluation Protocol:**
1. Load each model in inference mode
2. Run TruthfulQA evaluation → Record truthfulness scores
3. Run BOLD evaluation → Record fairness scores
4. Run HaluEval evaluation → Record hallucination scores
5. Run TextAttack evaluation → Record robustness scores
6. Compute model rankings per dimension (1st = best, Nth = worst)

**Output:**
- `baseline_scores`: Dict[model_name, Dict[dimension, score]]
- `baseline_rankings`: Dict[dimension, List[model_rank]]

**Acceptance Criteria:**
- All 8+ models evaluated on all 4 benchmarks
- Scores saved in structured format (CSV/JSON)
- Rankings computed correctly per dimension

---

### FR-4: Stressed Evaluation (TextAttack Perturbations)

**Priority:** P0 (Critical)  
**Status:** Required

Apply TextAttack perturbations to benchmark inputs and re-evaluate all models:

**Perturbation Protocol:**
1. Apply TextFooler attack to inputs from TruthfulQA, BOLD, HaluEval
2. Maintain semantic similarity > 0.8
3. Preserve grammaticality
4. Re-evaluate all 8+ models on perturbed inputs
5. Compute new model rankings per dimension

**Output:**
- `stressed_scores`: Dict[model_name, Dict[dimension, score]]
- `stressed_rankings`: Dict[dimension, List[model_rank]]

**Acceptance Criteria:**
- Perturbations applied successfully to all benchmark inputs
- All models re-evaluated on perturbed data
- Stressed rankings computed per dimension

---

### FR-5: Rank Correlation Analysis

**Priority:** P0 (Critical)  
**Status:** Required

Compute Kendall's τ rank correlation and measure asymmetry:

**Analysis Steps:**
1. Compute Kendall's τ between baseline and stressed rankings per dimension
2. Calculate Δτ = |τ_stressed - τ_baseline| per dimension
3. Measure pairwise asymmetry: |Δτ_i - Δτ_j| for all dimension pairs
4. Compute variance of Δτ across all dimensions
5. Statistical significance testing (permutation test, p < 0.01)

**Statistical Method:**
- Library: `scipy.stats.kendalltau`
- Correlation coefficient: τ ∈ [-1, 1]
- Significance threshold: p < 0.01

**Output:**
- Kendall's τ per dimension (baseline vs stressed)
- Δτ per dimension
- Asymmetry matrix (pairwise |Δτ_i - Δτ_j|)
- Variance of Δτ values
- p-values for statistical significance

**Acceptance Criteria:**
- τ computed correctly for all dimensions
- Asymmetry values calculated for all dimension pairs
- Variance computed across dimensions
- Statistical significance validated

---

### FR-6: Gate Validation

**Priority:** P0 (Critical)  
**Status:** Required

Validate hypothesis against MUST_WORK gate criteria:

**Gate Checks:**
1. **Primary criterion:** |Δτ| ≥ 0.2 in ≥2 dimension pairs with p < 0.01
2. **Secondary criterion:** Variance of Δτ > 0.02

**Gate Logic:**
```python
# Primary check
significant_pairs = count pairs where (|Δτ| ≥ 0.2 AND p < 0.01)
primary_pass = (significant_pairs ≥ 2)

# Secondary check
delta_tau_variance = variance([Δτ_truthfulness, Δτ_fairness, Δτ_hallucination, Δτ_robustness])
secondary_pass = (delta_tau_variance > 0.02)

# Gate result
gate_satisfied = (primary_pass AND secondary_pass)
```

**Acceptance Criteria:**
- Gate logic implemented correctly
- Results logged with clear PASS/FAIL status
- If FAIL → Trigger pipeline STOP and pivot to benchmarking redundancy study

---

### FR-7: Visualization Generation

**Priority:** P1 (High)  
**Status:** Required

Generate visualizations to communicate results:

**Required Figures:**

1. **Gate Metrics Comparison** (Mandatory)
   - Bar chart: Target vs actual asymmetry values
   - Threshold lines at |Δτ| = 0.2, variance = 0.02
   - Clear PASS/FAIL indicators

2. **Rank Correlation Heatmap**
   - X-axis: Dimensions (Truthfulness, Fairness, Hallucination, Robustness)
   - Y-axis: Conditions (Baseline, Stressed)
   - Cell values: Kendall's τ coefficients
   - Color scale: Correlation strength

3. **Asymmetry Bar Chart**
   - X-axis: Dimension pairs
   - Y-axis: |Δτ_i - Δτ_j|
   - Threshold line at 0.2 (gate criterion)

4. **Rank Shift Visualization**
   - Scatter plot: Baseline ranks (x) vs Stressed ranks (y)
   - One subplot per dimension
   - Diagonal line = no rank shift
   - Points off diagonal = rank reordering

5. **Variance Distribution**
   - Box plot: Δτ values across dimensions
   - Horizontal line at variance threshold (0.02)

**Output:**
- All figures saved to `{hypothesis_folder}/figures/`
- Format: PNG/PDF (high resolution)
- Generated using matplotlib/seaborn

**Acceptance Criteria:**
- All 5+ figures generated successfully
- Figures saved to correct directory
- Clear visual communication of results

---

### FR-8: Results Reporting

**Priority:** P0 (Critical)  
**Status:** Required

Generate comprehensive validation report:

**Report Sections:**
1. **Experiment Overview**: Hypothesis, methodology, sample sizes
2. **Baseline Results**: Model rankings per dimension under baseline
3. **Stressed Results**: Model rankings per dimension under stress
4. **Rank Correlation Analysis**: τ values, Δτ values, asymmetry matrix
5. **Gate Validation**: Primary/secondary criteria evaluation, PASS/FAIL status
6. **Statistical Significance**: p-values, permutation test results
7. **Figures**: Embedded visualizations with captions
8. **Conclusion**: Gate result interpretation

**Output:**
- Report file: `{hypothesis_folder}/04_validation.md`
- Format: Markdown with embedded figures
- Structured for Phase 4.5 synthesis

**Acceptance Criteria:**
- Report contains all required sections
- Gate result clearly stated
- Statistical evidence provided
- Figures embedded correctly

---

## Data Specifications

### Input Data

**Phase 2C Experiment Brief:**
- Path: `{hypothesis_folder}/02c_experiment_brief.md`
- Content: Detailed experiment design from Phase 2C
- Usage: Source for benchmark selection, model requirements, success criteria

**Benchmark Datasets:**

| Benchmark | Source | Size | Task Type |
|-----------|--------|------|-----------|
| TruthfulQA | HuggingFace `truthful_qa` | 817 questions | Multiple-choice QA |
| BOLD | HuggingFace `AlexaAI/bold` | 23,679 prompts | Open-ended generation |
| HaluEval | HuggingFace `pminervini/HaluEval` | 30,000 samples | Binary classification |
| TextAttack | PyPI `textattack` | N/A (framework) | Adversarial perturbation |

**Model Checkpoints:**
- Source: HuggingFace Model Hub
- Format: Pre-trained PyTorch models
- Access: Public repositories (Apache 2.0, MIT licenses)

### Output Data

**Evaluation Results:**
- `baseline_scores.json`: Model scores per benchmark (baseline)
- `stressed_scores.json`: Model scores per benchmark (stressed)
- `baseline_rankings.json`: Model rankings per dimension (baseline)
- `stressed_rankings.json`: Model rankings per dimension (stressed)

**Statistical Analysis:**
- `kendall_tau.json`: τ values per dimension
- `delta_tau.json`: Δτ values per dimension
- `asymmetry_matrix.json`: Pairwise asymmetry values
- `variance.json`: Δτ variance
- `statistical_tests.json`: p-values, significance flags

**Visualization Files:**
- `figures/gate_metrics.png`: Gate validation chart
- `figures/rank_correlation_heatmap.png`: τ heatmap
- `figures/asymmetry_bars.png`: Asymmetry bar chart
- `figures/rank_shift_*.png`: Scatter plots per dimension
- `figures/variance_distribution.png`: Box plot

**Validation Report:**
- `04_validation.md`: Comprehensive results report

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency

**Requirement:** Complete evaluation within reasonable time on single GPU

**Specifications:**
- GPU: Single NVIDIA GPU (selected via CUDA_VISIBLE_DEVICES)
- Precision: FP16 for memory efficiency
- Batch size: Adaptive (1-4) based on model size
- Parallelization: Sequential model evaluation (no multi-GPU)

**Acceptance Criteria:**
- Runs on single available GPU
- No out-of-memory errors
- Reasonable runtime (benchmark-dependent)

---

### NFR-2: Reproducibility

**Requirement:** Results must be reproducible with fixed seed

**Specifications:**
- Random seed: Fixed (e.g., 42)
- PyTorch/NumPy seeds set consistently
- Deterministic inference mode
- No stochastic sampling (greedy decoding or temperature=0)

**Acceptance Criteria:**
- Same input produces same output across runs
- Seeds documented in code
- Inference settings logged

---

### NFR-3: Code Quality

**Requirement:** Clean, documented, maintainable code

**Specifications:**
- Infrastructure level: LIGHT (minimal)
- Configuration: Hardcoded or argparse (no YAML config)
- Logging: Print statements + CSV results
- Testing: Smoke test (basic validation)
- No complex abstractions for one-off experiment

**Acceptance Criteria:**
- Code runs without errors
- Key functions documented
- Results easily inspectable

---

### NFR-4: Error Handling

**Requirement:** Graceful handling of common failures

**Error Scenarios:**
- Dataset download failure → Retry 3x with 15s delay
- Model loading failure → Log error, skip model, continue
- OOM during evaluation → Reduce batch size, retry
- Benchmark API changes → Fallback to alternative loading method

**Acceptance Criteria:**
- No silent failures
- Error messages logged clearly
- Partial results saved even on failure

---

## Dependencies

### External Libraries

**Core ML/DL:**
- `torch` ≥ 2.0.0
- `transformers` ≥ 4.30.0
- `datasets` ≥ 2.10.0

**Benchmarks:**
- `textattack` ≥ 0.3.0 (robustness framework)

**Statistics:**
- `scipy` ≥ 1.10.0 (kendalltau)
- `numpy` ≥ 1.24.0

**Visualization:**
- `matplotlib` ≥ 3.7.0
- `seaborn` ≥ 0.12.0

**Utilities:**
- `pandas` ≥ 2.0.0 (data manipulation)
- `tqdm` ≥ 4.65.0 (progress bars)

### Hardware Requirements

**GPU:**
- Minimum: 1x NVIDIA GPU with 16GB VRAM
- Recommended: 1x NVIDIA GPU with 24GB+ VRAM (for 7B models)
- CUDA support required

**CPU/RAM:**
- CPU: 8+ cores recommended
- RAM: 32GB+ (for dataset caching)

**Storage:**
- 50GB+ for model checkpoints and datasets
- SSD recommended for faster loading

### Environment Setup

**Python Version:**
- Python 3.9+

**GPU Selection:**
```bash
# Check available GPUs
nvidia-smi

# Select empty GPU
export CUDA_VISIBLE_DEVICES=<empty_gpu_id>  # e.g., 0, 1, 2
```

**Installation:**
```bash
pip install torch transformers datasets textattack scipy numpy matplotlib seaborn pandas tqdm
```

---

## Success Metrics

### Validation Metrics

**Primary:**
- |Δτ| ≥ 0.2 in ≥2 dimension pairs (with p < 0.01)

**Secondary:**
- Variance of Δτ > 0.02

**Gate Validation:**
- MUST_WORK gate satisfied: (Primary AND Secondary) = TRUE

### Quality Metrics

**Code Quality:**
- Runs without errors: ✓
- All benchmarks evaluated: ✓
- All models evaluated: ✓

**Data Quality:**
- No missing evaluations: ✓
- Rankings computed correctly: ✓
- Statistical tests valid: ✓

**Output Quality:**
- All figures generated: ✓
- Report complete: ✓
- Results interpretable: ✓

---

## Out of Scope

**Explicitly NOT included:**

1. **Training or Fine-tuning:** Models used as-is (pre-trained)
2. **Multi-GPU Parallelization:** Single GPU only
3. **Hyperparameter Optimization:** Fixed evaluation protocol
4. **Advanced Infrastructure:** No WandB, no complex config management
5. **Comprehensive Testing:** Smoke test only (PoC experiment)
6. **Additional Benchmarks:** Only 4 specified benchmarks
7. **Additional Models:** Minimum 8 models (can expand if needed)
8. **Longitudinal Analysis:** Single evaluation run only
9. **Cross-validation:** No k-fold or multiple splits
10. **Ablation Studies:** Beyond specified evaluation protocol

---

## Risk Assessment

### High-Priority Risks

**Risk 1: Model Loading Failures**
- **Impact:** Missing models reduces statistical power
- **Mitigation:** Test all model loads before full evaluation; have backup models ready
- **Contingency:** Skip failed models, document in report

**Risk 2: OOM Errors on Large Models**
- **Impact:** Cannot evaluate 7B models
- **Mitigation:** Use FP16, adaptive batch size, gradient checkpointing if needed
- **Contingency:** Evaluate on smaller models only, note limitation

**Risk 3: Benchmark API Changes**
- **Impact:** Evaluation fails due to HuggingFace dataset updates
- **Mitigation:** Pin dataset versions, use alternative loading methods
- **Contingency:** Download datasets manually from GitHub

**Risk 4: Gate Failure (MUST_WORK)**
- **Impact:** Entire hypothesis pipeline stops
- **Mitigation:** Carefully validate statistical methods, use permutation tests
- **Contingency:** If gate fails, pivot to benchmarking redundancy study as planned

### Medium-Priority Risks

**Risk 5: Insufficient Rank Correlation Shifts**
- **Impact:** Asymmetry below threshold
- **Mitigation:** Ensure perturbations are strong enough; verify evaluation correctness
- **Contingency:** Document partial results, analyze why dimensions don't separate

**Risk 6: Statistical Significance Issues**
- **Impact:** p-values above 0.01
- **Mitigation:** Use robust permutation tests, adequate sample sizes
- **Contingency:** Report non-significant trends, note limitations

---

## Timeline & Milestones

**Phase 3:** Implementation Planning (current)
- PRD generation ✓
- Architecture design (next)
- Task breakdown (upcoming)

**Phase 4:** Implementation & PoC Validation
- Milestone 1: Environment setup + dataset download
- Milestone 2: Model loading + baseline evaluation
- Milestone 3: Perturbation application + stressed evaluation
- Milestone 4: Statistical analysis + gate validation
- Milestone 5: Visualization + reporting

**Phase 4.5:** Hypothesis Synthesis
- Evidence-refined claims
- Limitation analysis

**Phase 6:** Paper Writing
- Methods section from this experiment
- Results section from validation report

---

## Appendix

### Benchmark References

**TruthfulQA:**
- Paper: Lin et al. (2022), "TruthfulQA: Measuring How Models Mimic Human Falsehoods"
- GitHub: https://github.com/sylinrl/TruthfulQA
- HuggingFace: `truthful_qa` dataset

**BOLD:**
- Paper: Dhamala et al. (2021), "BOLD: Dataset and Metrics for Measuring Biases in Open-Ended Language Generation"
- GitHub: https://github.com/amazon-science/bold
- HuggingFace: `AlexaAI/bold` dataset

**HaluEval:**
- Paper: Li et al. (2023), "HaluEval: A Large-Scale Hallucination Evaluation Benchmark"
- GitHub: https://github.com/RUCAIBox/HaluEval
- HuggingFace: `pminervini/HaluEval` dataset

**TextAttack:**
- Paper: Morris et al. (2020), "TextAttack: A Framework for Adversarial Attacks in Natural Language Processing"
- GitHub: https://github.com/QData/TextAttack
- PyPI: `textattack` package

### Statistical Method References

**Kendall's Tau:**
- Kendall, M. G. (1938). "A new measure of rank correlation"
- scipy.stats.kendalltau documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kendalltau.html

---

**Document Status:** Complete  
**Next Steps:** Proceed to Phase 3 Step 3 (Architecture Design)  
**Dependencies Satisfied:** Phase 2C experiment brief available ✓
