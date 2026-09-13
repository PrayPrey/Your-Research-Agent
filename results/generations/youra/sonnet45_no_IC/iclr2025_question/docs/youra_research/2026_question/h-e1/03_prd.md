# Product Requirements Document (PRD)

## Frontmatter

```yaml
document_type: PRD
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
created_date: 2026-07-13
author: Anonymous
project_name: "Uncertainty Quantification in Foundation Models"
stepsCompleted: ["Executive Summary", "Problem Statement", "Functional Requirements", "Non-Functional Requirements", "Success Criteria", "Dependencies", "Timeline"]
```

---

## Executive Summary

### Purpose
Validate the existence of complementary uncertainty signals between consistency-based methods (epistemic uncertainty) and conformal prediction methods (aleatoric uncertainty) in foundation model uncertainty quantification.

### Hypothesis
Under foundation model uncertainty quantification settings, if we measure the correlation between consistency-based scores (C) and conformal prediction interval membership (I), then we observe 0.3 < ρ(C,I) < 0.7, because consistency methods capture epistemic uncertainty (generative inconsistency) while conformal methods capture aleatoric uncertainty (inherent data ambiguity), representing distinct but complementary information sources.

### Gate Type
**MUST_WORK** - This is a foundation hypothesis that must succeed before dependent hypotheses can proceed.

### Success Criteria (Gate Metrics)
- **Primary**: Pearson correlation ρ(C, I) in range [0.3, 0.7] on all three datasets (TruthfulQA, HH-RLHF, SQuAD)
- **Statistical Significance**: p < 0.05 for all datasets
- **Coverage Quality**: ≥ 85% coverage rate (conformal degradation check)

---

## Problem Statement

### Background
Current uncertainty quantification methods for foundation models operate independently:
- **Consistency-based methods** (e.g., SelfCheckGPT) measure epistemic uncertainty through sampling
- **Conformal prediction methods** (e.g., COIN) provide aleatoric uncertainty bounds with coverage guarantees

The relationship between these two signals is unknown, which limits our understanding of whether they can be combined for improved calibration.

### Research Question
Do consistency-based and conformal prediction methods measure distinct but complementary uncertainty signals in foundation models?

### Scope
**In Scope:**
- Multi-dataset evaluation (TruthfulQA, HH-RLHF, SQuAD)
- Consistency scoring via SelfCheckGPT pattern (NLI + BERTScore)
- Conformal prediction intervals using standard conformal methods
- Correlation analysis between C and I signals
- Statistical validation with significance testing

**Out of Scope:**
- Full hierarchical Bayesian calibration (H-M-integrated)
- Computational cost optimization
- Fine-tuning foundation models
- Production deployment infrastructure

---

## Functional Requirements

### FR1: Dataset Infrastructure
**Priority**: P0 (Critical)
**Description**: Implement multi-dataset loading and preprocessing pipeline

**Sub-requirements:**
- FR1.1: Load TruthfulQA dataset via HuggingFace (`load_dataset("truthful_qa", "generation")`)
  - Statistics: ~800 questions, full dataset evaluation
  - Preprocessing: Llama-2 tokenizer, max_length=512, dynamic batching

- FR1.2: Load HH-RLHF dataset via HuggingFace (`load_dataset("Anthropic/hh-rlhf")`)
  - Statistics: Dialogue turns with preference labels
  - Purpose: Aleatoric uncertainty benchmark

- FR1.3: Load SQuAD dataset via HuggingFace (`load_dataset("squad")`)
  - Statistics: 10K+ dev samples
  - Purpose: Mixed uncertainty baseline

- FR1.4: Implement preprocessing pipeline
  - Tokenization with Llama-2 tokenizer
  - Max length: 512 tokens
  - Truncation: True
  - Padding: Dynamic batching

**Acceptance Criteria:**
- All three datasets load successfully
- Minimum 1000 samples per dataset after preprocessing
- Tokenization applied consistently across datasets

---

### FR2: Baseline Model Integration
**Priority**: P0 (Critical)
**Description**: Integrate Llama-2-7B foundation model for generation

**Sub-requirements:**
- FR2.1: Load Llama-2-7B from HuggingFace Hub
  - Model ID: "meta-llama/Llama-2-7b-hf"
  - Method: `AutoModelForCausalLM.from_pretrained()`
  
- FR2.2: Configure generation parameters
  - Temperature: 0.7 (for sampling diversity)
  - Max tokens: 256 per generation
  - Sampling strategy: Standard nucleus/top-p sampling

- FR2.3: Implement multi-sample generation capability
  - Generate 5 samples per input (for consistency scoring)
  - Batch processing support

**Acceptance Criteria:**
- Model loads successfully on available hardware
- Generates coherent outputs for all three datasets
- Multi-sample generation produces diverse outputs

---

### FR3: Consistency Scoring Module (Epistemic Uncertainty)
**Priority**: P0 (Critical)
**Description**: Implement SelfCheckGPT-pattern consistency scoring via NLI + BERTScore ensemble

**Sub-requirements:**
- FR3.1: Implement NLI-based consistency scoring
  - Model: roberta-large-mnli (HuggingFace)
  - Input: (generated_answer, sample_i) pairs
  - Output: Entailment scores

- FR3.2: Implement BERTScore-based similarity
  - Model: deberta-xlarge-mnli (default BERTScorer)
  - Language: English
  - Metric: F1 scores

- FR3.3: Ensemble consistency score computation
  - Formula: C(x) = (mean(NLI_scores) + mean(BERTScore)) / 2
  - Range: [0, 1] normalized

- FR3.4: Multi-sample generation integration
  - Generate 5 samples per input
  - Compute consistency across all pairs

**Acceptance Criteria:**
- Consistency scores computed for all test samples
- Scores in valid range [0, 1]
- High consistency = low epistemic uncertainty

---

### FR4: Conformal Prediction Module (Aleatoric Uncertainty)
**Priority**: P0 (Critical)
**Description**: Implement conformal prediction intervals with coverage guarantees

**Sub-requirements:**
- FR4.1: Implement conformity score computation
  - Method: Quantile-based conformity (standard conformal theory)
  - Calibration set: 1000 samples per dataset

- FR4.2: Implement prediction interval construction
  - Coverage target: 90% (α = 0.10)
  - Quantile selection: Adaptive based on calibration set

- FR4.3: Implement interval membership indicator
  - I_binary: 1 if true_answer ∈ interval, 0 otherwise
  - Use for correlation analysis

- FR4.4: Coverage rate computation
  - Metric: Fraction of samples where y ∈ I(x)
  - Target: ≥ 90% (conformal guarantee)

**Acceptance Criteria:**
- Conformal intervals generated for all test samples
- Coverage rate ≥ 85% (allowing degradation check)
- Binary membership indicator computed correctly

---

### FR5: Correlation Analysis and Statistical Testing
**Priority**: P0 (Critical)
**Description**: Measure correlation ρ(C, I) and perform significance testing

**Sub-requirements:**
- FR5.1: Compute Pearson correlation
  - Method: `scipy.stats.pearsonr(C_scores, I_binary)`
  - Output: ρ value and p-value per dataset

- FR5.2: Significance testing
  - Null hypothesis: ρ = 0.9 (redundancy) OR ρ = 0.1 (independence)
  - Requirement: p < 0.05 for all datasets
  - Test: Two-tailed significance test

- FR5.3: Per-dataset analysis
  - Compute ρ separately for TruthfulQA, HH-RLHF, SQuAD
  - Report all three values

**Acceptance Criteria:**
- Correlation computed for all three datasets
- P-values reported with correlations
- Clear pass/fail determination against [0.3, 0.7] range

---

### FR6: Evaluation Metrics and Diagnostics
**Priority**: P1 (High)
**Description**: Implement secondary diagnostic metrics for quality assessment

**Sub-requirements:**
- FR6.1: Expected Calibration Error (ECE)
  - Implementation: Custom ECE computation
  - Bins: 10 bins
  - Target: < 0.10 for PoC (no fine-tuning)

- FR6.2: Consistency score distribution analysis
  - Metrics: Mean and std of C(x) across samples
  - Visualization: Histogram of consistency scores

- FR6.3: Conformal interval width analysis
  - Metric: Average interval size
  - Purpose: Assess prediction uncertainty magnitude

**Acceptance Criteria:**
- ECE computed and reported
- Consistency distribution visualized
- Interval width statistics computed

---

### FR7: Visualization and Reporting
**Priority**: P1 (High)
**Description**: Generate required figures and comprehensive experiment report

**Sub-requirements:**
- FR7.1: Mandatory gate metrics visualization
  - Bar chart: Target vs actual correlation ρ for each dataset
  - Include success/failure indicators

- FR7.2: Scatter plot: C vs I_binary
  - X-axis: Consistency score C
  - Y-axis: Interval membership I (binary)
  - Annotation: ρ value and p-value

- FR7.3: Distribution comparison histogram
  - Separate histograms: C scores for I=1 vs I=0 cases
  - Purpose: Visualize signal complementarity

- FR7.4: Per-dataset correlation comparison
  - Side-by-side bar chart: ρ values for TruthfulQA, HH-RLHF, SQuAD
  - Include confidence intervals

- FR7.5: Calibration curve (ECE visualization)
  - X-axis: Predicted uncertainty
  - Y-axis: Actual error rate
  - Diagonal reference line

- FR7.6: Experiment report generation
  - File: `04_validation.md` in hypothesis folder
  - Content: Metrics, visualizations, pass/fail determination

**Acceptance Criteria:**
- All 5 required figures generated and saved to `{hypothesis_folder}/figures/`
- Figures are publication-quality (vector format preferred)
- Report includes all gate metrics and diagnostics

---

## Non-Functional Requirements

### NFR1: Performance
- **Execution Time**: Complete experiment in 2-4 hours per dataset on single GPU
- **Memory**: Fit within 16GB GPU VRAM (Llama-2-7B + scoring models)
- **Throughput**: Process ≥ 1000 samples per dataset

### NFR2: Reproducibility
- **Random Seed**: Fixed at 42 for all random operations
- **Deterministic**: All metrics must be reproducible across runs
- **Version Control**: Track all dependency versions

### NFR3: Code Quality
- **Documentation**: All modules documented with docstrings
- **Type Hints**: Use Python type hints throughout
- **Error Handling**: Graceful handling of model loading failures, out-of-memory errors

### NFR4: Infrastructure Tier
**LIGHT (minimal)** - Appropriate for EXISTENCE hypothesis:
- Configuration: Hardcoded hyperparameters or simple argparse
- Logging: Print statements + CSV metric logs
- Testing: Smoke tests for basic functionality

---

## Dependencies

### Software Dependencies
- **Python**: 3.8+
- **PyTorch**: 2.0+ (for model inference)
- **HuggingFace Transformers**: 4.30+ (for Llama-2-7B, roberta-large-mnli)
- **HuggingFace Datasets**: 2.12+ (for TruthfulQA, HH-RLHF, SQuAD)
- **BERTScore**: 0.3.13+ (for consistency scoring)
- **SciPy**: 1.10+ (for Pearson correlation)
- **NumPy**: 1.24+
- **Matplotlib**: 3.7+ (for visualizations)

### Optional Dependencies
- **MAPIE**: 0.6+ (for conformal prediction; fallback to custom implementation if unavailable)
- **WandB**: For experiment tracking (optional, LIGHT tier uses CSV logging)

### Hardware Requirements
- **GPU**: Single GPU with ≥ 16GB VRAM (for Llama-2-7B inference)
- **Storage**: ~50GB (model weights + datasets + experiment outputs)

### External Resources
- **HuggingFace Hub Access**: For downloading models and datasets
- **Network**: Internet connection for initial downloads

---

## Success Criteria

### Gate Metrics (MUST_WORK)
1. **Primary**: 0.3 ≤ ρ(C, I) ≤ 0.7 on TruthfulQA **AND** HH-RLHF **AND** SQuAD
2. **Statistical Significance**: p < 0.05 for all three datasets
3. **Coverage Quality**: Coverage ≥ 85% (conformal degradation check)

### Diagnostic Metrics (Quality Indicators)
- **ECE**: < 0.10 (acceptable for PoC without fine-tuning)
- **Consistency Scores**: Mean C(x) in reasonable range [0.3, 0.8]
- **Interval Width**: Finite and bounded intervals

### Deliverables
- ✅ All three datasets processed successfully
- ✅ Consistency scores C computed for all samples
- ✅ Conformal intervals I constructed for all samples
- ✅ Correlation ρ(C, I) measured per dataset
- ✅ Statistical significance p-values computed
- ✅ All 5 required figures generated
- ✅ `04_validation.md` report with pass/fail determination

---

## Timeline and Milestones

**Phase 4 Implementation (Coding & Validation)**

### Milestone 1: Environment Setup (Priority: Data + Env tasks)
- Load datasets (TruthfulQA, HH-RLHF, SQuAD)
- Load Llama-2-7B model
- Verify GPU availability and memory

### Milestone 2: Core Implementation (Priority: Implementation tasks)
- Implement consistency scoring module (NLI + BERTScore)
- Implement conformal prediction module
- Implement correlation analysis

### Milestone 3: Validation (Automated via Phase 4 workflow)
- Run experiment on all three datasets
- Compute gate metrics (ρ, p-values, coverage)
- Generate visualizations
- Create `04_validation.md` report

### Milestone 4: Gate Evaluation
- Check: 0.3 ≤ ρ ≤ 0.7 on all datasets?
- Check: p < 0.05 for all datasets?
- Check: Coverage ≥ 85%?
- **Outcome**: PASS → Proceed to H-M-integrated | FAIL → Hypothesis redesign

---

## Appendix: Technical References

### A. Consistency Scoring Pattern (SelfCheckGPT)
- **Reference**: Manakul et al., 2023 (https://github.com/potsawee/selfcheckgpt)
- **Method**: Multi-sample generation (5-10 samples) + NLI + BERTScore ensemble
- **Models**: roberta-large-mnli, deberta-xlarge-mnli

### B. Conformal Prediction Theory
- **Reference**: Conformal prediction with coverage guarantees
- **Library**: MAPIE (Python) or custom implementation
- **Method**: Quantile-based conformity scores, 90% coverage target

### C. Archon Knowledge Base Sources
- **Source A.1**: Consistency Models Research (arXiv:2402.19159)
- **Source A.2**: Marigold Depth Uncertainty (ensemble pattern)
- **Source A.3**: Optimum Quanto Calibration (calibration protocol)

### D. Expected Baseline Performance
- **Independent SelfCheckGPT**: AUC ~0.7-0.8 for hallucination detection
- **Independent COIN**: Coverage ~90%, ECE ~0.06-0.08
- **Correlation ρ(C, I)**: Unknown (hypothesis target: 0.3-0.7)

---

**Document Status**: COMPLETE
**Ready for Phase 3 Architecture Design**: YES
**Source**: Generated from Phase 2C experiment brief (02c_experiment_brief.md)
