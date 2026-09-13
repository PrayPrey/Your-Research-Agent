# Product Requirements Document (PRD)

## Frontmatter

```yaml
document_type: PRD
hypothesis_id: h-m-integrated
hypothesis_type: MECHANISM
created_date: 2026-07-13
author: Anonymous
project_name: "Uncertainty Quantification in Foundation Models"
prerequisites: ["h-e1"]
stepsCompleted: ["Executive Summary", "Problem Statement", "Functional Requirements", "Non-Functional Requirements", "Success Criteria", "Dependencies", "Timeline"]
```

---

## Executive Summary

### Purpose
Validate the hierarchical Bayesian calibration (HBC) mechanism that achieves improved calibration quality (ECE < 0.05) with computational efficiency gains (30-50% cost reduction) through mutual calibration of consistency-based and conformal prediction methods.

### Hypothesis
Under foundation model uncertainty quantification settings, if we apply hierarchical Bayesian calibration (HBC) where consistency priors C(x) inform conformal calibration and statistical validation results update consistency thresholds (mutual calibration), then we achieve Expected Calibration Error (ECE) < 0.05 with 30-50% computational cost reduction vs. COIN-only while maintaining coverage ≥ 90%, because the three-step causal mechanism operates: (Step 1) Consistency sampling measures epistemic uncertainty producing prior C(x), (Step 2) Conformal prediction provides aleatoric bounds producing interval I(x), (Step 3) Hierarchical Bayesian updating creates co-calibration exploiting complementarity (0.3 < ρ < 0.7), where mutual calibration improves both signals beyond independent application.

### Gate Type
**MUST_WORK** - Core HBC contribution that must demonstrate both calibration quality and computational efficiency.

### Success Criteria (Gate Metrics)
- **Primary**: ECE_HBC < 0.05 AND significantly lower than all three baselines (SelfCheckGPT-only, COIN-only, Independent Cascade) with p < 0.05
- **Secondary**: Computational cost reduction 30-50% vs COIN-only (measured in forward passes per 1000 queries) while maintaining coverage ≥ 90%
- **Mechanism Validation**: Ablation shows ECE improvement peaks at ρ ~ 0.5 (sweet spot dependency confirmed)

---

## Problem Statement

### Background
Current uncertainty quantification methods operate independently or in simple cascades:
- **SelfCheckGPT**: Consistency-based hallucination detection via multi-sample generation
- **COIN**: Conformal prediction with coverage guarantees
- **Independent Cascade**: Sequential application without joint calibration

H-E1 validation confirmed complementarity (0.3 < ρ < 0.7), but optimal integration remains unexplored.

### Research Question
Can hierarchical Bayesian calibration (HBC) exploit the complementarity between consistency and conformal methods to improve both calibration quality and computational efficiency through mutual calibration?

### Scope
**In Scope:**
- Full HBC implementation with three-step causal mechanism
- Multi-dataset evaluation (TruthfulQA, HH-RLHF, SQuAD)
- Four baseline comparisons (SelfCheckGPT-only, COIN-only, Independent Cascade, HBC)
- Computational cost measurement and optimization
- Ablation study validating sweet spot dependency (ρ ~ 0.5)
- Coverage guarantee validation (≥ 90%)

**Out of Scope:**
- Fine-tuning foundation model weights
- Alternative UQ methods beyond SelfCheckGPT + COIN
- Production deployment infrastructure
- Multi-model ensemble methods

---

## Functional Requirements

### FR1: Dataset Infrastructure
**Priority**: P0 (Critical)
**Description**: Implement multi-dataset loading, preprocessing, and calibration/test split generation

**Sub-requirements:**
- FR1.1: Load TruthfulQA dataset via HuggingFace
  - Dataset ID: `truthful_qa` (generation task)
  - Sample size: Full test set (817 samples)
  - Preprocessing: Llama-2 tokenizer, max_length=512

- FR1.2: Load HH-RLHF dataset via HuggingFace
  - Dataset ID: `Anthropic/hh-rlhf`
  - Sample size: 1000 test samples
  - Purpose: Aleatoric uncertainty evaluation

- FR1.3: Load SQuAD v2 dataset via HuggingFace
  - Dataset ID: `squad_v2`
  - Sample size: 1000 validation samples
  - Purpose: Mixed uncertainty baseline

- FR1.4: Implement calibration/test split
  - Calibration set: 500 samples per dataset
  - Test set: Remaining samples (≥1000 per dataset)
  - Random seed: 42 (reproducibility)

**Acceptance Criteria:**
- All three datasets load successfully
- Calibration/test splits created with no overlap
- Minimum sample counts verified

---

### FR2: Foundation Model Integration
**Priority**: P0 (Critical)
**Description**: Integrate Llama-2-7B for multi-sample generation and inference

**Sub-requirements:**
- FR2.1: Load Llama-2-7B from HuggingFace Hub
  - Model ID: `meta-llama/Llama-2-7b-hf`
  - Loading: `AutoModelForCausalLM.from_pretrained()`
  - Precision: fp16 (memory efficiency)

- FR2.2: Configure generation parameters
  - Temperature: 1.0 (sampling diversity for consistency)
  - Top-p: 0.95 (nucleus sampling)
  - Max new tokens: 256
  - Num return sequences: 5 (SelfCheckGPT standard)
  - Do sample: True

- FR2.3: Implement batched multi-sample generation
  - Batch size: Adaptive (memory constraints)
  - Support for 5-10 samples per query

**Acceptance Criteria:**
- Model loads successfully on available GPU
- Generates 5 diverse samples per input
- Batching reduces inference time vs sequential

---

### FR3: SelfCheckGPT Consistency Module (Epistemic Uncertainty)
**Priority**: P0 (Critical)
**Description**: Implement SelfCheckGPT-pattern consistency scoring via NLI + BERTScore ensemble

**Sub-requirements:**
- FR3.1: Implement NLI-based consistency scoring
  - Model: `microsoft/deberta-large-mnli`
  - Input: (reference_sample, candidate_sample) pairs
  - Output: Entailment probability scores

- FR3.2: Implement BERTScore similarity
  - Model: `microsoft/deberta-xlarge-mnli`
  - Metric: F1 scores
  - Language: English

- FR3.3: Ensemble consistency score computation
  - Formula: C(x) = (mean(NLI) + mean(BERTScore)) / 2
  - Range: [0, 1] normalized
  - Interpretation: High C(x) = high consistency = low epistemic uncertainty

- FR3.4: Baseline SelfCheckGPT-only implementation
  - Threshold optimization on calibration set
  - Grid search: thresholds ∈ [0.3, 0.7]
  - Binary classification (hallucination detection)

**Acceptance Criteria:**
- Consistency scores computed for all samples
- Scores in valid range [0, 1]
- SelfCheckGPT-only baseline achieves F1 ≥ 0.7

---

### FR4: COIN Conformal Prediction Module (Aleatoric Uncertainty)
**Priority**: P0 (Critical)
**Description**: Implement conformal prediction framework with coverage guarantees

**Sub-requirements:**
- FR4.1: Implement nonconformity score function
  - Metric: 1 - semantic_similarity(y_pred, y_true)
  - Similarity: SentenceBERT cosine similarity
  - Range: [0, 1] (0 = perfect match, 1 = no match)

- FR4.2: Calibration set processing
  - Compute nonconformity scores for all calibration samples
  - Store scores for quantile computation

- FR4.3: Conformal quantile computation
  - Formula: q = (⌈(n+1)(1-α)⌉ / n)-th quantile
  - Coverage target: α = 0.1 (90% coverage)
  - Finite-sample correction applied

- FR4.4: Prediction interval generation
  - Interval: [y_pred - q, y_pred + q] (for regression)
  - Set: {y : nonconformity(y, y_pred) ≤ q} (for classification)
  - Membership indicator: I(x) = 1 if y_true ∈ interval, 0 otherwise

- FR4.5: Baseline COIN-only implementation
  - Standard conformal prediction without consistency priors
  - Coverage validation on test set

**Acceptance Criteria:**
- Coverage on test set: 90% ± 2%
- Nonconformity scores computed correctly
- Prediction intervals cover ground truth at target rate

---

### FR5: Hierarchical Bayesian Calibration (HBC) Core
**Priority**: P0 (Critical)
**Description**: Implement three-step causal mechanism with mutual calibration

**Sub-requirements:**
- FR5.1: Step 1 - Consistency Prior Generation
  - Generate 5 samples per query (Llama-2-7B)
  - Compute C(x) using NLI + BERTScore ensemble
  - Output: Epistemic uncertainty prior ∈ [0, 1]

- FR5.2: Step 2 - Conformal Prediction with Epistemic Priors
  - Weighted nonconformity: score / (1 + C(x))
  - Rationale: High consistency (low epistemic uncertainty) → tighter intervals
  - Compute epistemic-informed conformal quantile

- FR5.3: Step 3 - Bayesian Mutual Calibration
  - Update consistency threshold based on conformal coverage
  - Formula: threshold_new = argmax_{t} coverage(t) s.t. coverage ≥ 0.9
  - Bidirectional calibration loop (max 3 iterations)

- FR5.4: Co-calibrated inference pipeline
  - Input: Query x
  - Output: (prediction, interval, consistency_score, confidence)
  - Integration: Consistency informs interval width, coverage updates threshold

**Acceptance Criteria:**
- HBC achieves ECE < 0.05 on all three datasets
- Mutual calibration converges in ≤ 3 iterations
- Coverage maintained at ≥ 90%

---

### FR6: Baseline Comparison Suite
**Priority**: P0 (Critical)
**Description**: Implement all baseline methods for comparative evaluation

**Sub-requirements:**
- FR6.1: SelfCheckGPT-only baseline
  - Consistency threshold: Grid search on calibration set
  - Binary classification: hallucination vs factual
  - Metrics: F1, precision, recall

- FR6.2: COIN-only baseline
  - Standard conformal prediction (no consistency priors)
  - Coverage target: 90%
  - Metrics: Coverage, interval width, ECE

- FR6.3: Independent Cascade baseline
  - Stage 1: SelfCheckGPT filtering (threshold-based)
  - Stage 2: COIN conformal intervals on filtered outputs
  - No joint calibration between stages
  - Metrics: ECE, coverage, computational cost

- FR6.4: HBC (proposed method)
  - Full hierarchical Bayesian calibration with mutual updating
  - Metrics: ECE, coverage, computational cost, ablation results

**Acceptance Criteria:**
- All four methods implemented and tested
- Fair comparison: Same model, datasets, evaluation protocol
- Metrics computed consistently across methods

---

### FR7: Expected Calibration Error (ECE) Metric
**Priority**: P0 (Critical)
**Description**: Implement ECE computation for calibration quality measurement

**Sub-requirements:**
- FR7.1: Binning predictions by confidence
  - Number of bins: 10 (standard)
  - Bin edges: np.linspace(0, 1, 11)
  - Bin assignment: confidences ∈ [bin_i, bin_{i+1})

- FR7.2: Per-bin accuracy and confidence computation
  - Accuracy: mean(predictions == ground_truth) per bin
  - Confidence: mean(confidence_scores) per bin

- FR7.3: Weighted ECE computation
  - Formula: ECE = Σ (|B_m|/n) × |acc(B_m) - conf(B_m)|
  - Weight: Bin size fraction
  - Output: Scalar ∈ [0, 1]

- FR7.4: Statistical significance testing
  - Test: Two-tailed t-test for pairwise comparisons
  - Null hypothesis: ECE_HBC = ECE_baseline
  - Significance level: p < 0.05

**Acceptance Criteria:**
- ECE computed for all methods on all datasets
- Statistical significance validated via t-tests
- Results reproducible across runs (fixed seed)

---

### FR8: Computational Cost Measurement
**Priority**: P0 (Critical)
**Description**: Measure and compare computational efficiency across methods

**Sub-requirements:**
- FR8.1: Forward pass counting
  - Metric: Total forward passes per 1000 test queries
  - Count: Model inference calls (Llama-2-7B + auxiliary models)

- FR8.2: Per-method cost breakdown
  - SelfCheckGPT-only: 5 samples × 1000 = 5,000 passes
  - COIN-only: 1 sample × 1000 + calibration overhead ≈ 1,500 passes
  - Independent Cascade: 5,000 + 1,500 = 6,500 passes
  - HBC target: 4,000-4,500 passes (30-50% reduction vs Cascade)

- FR8.3: Cost reduction calculation
  - Formula: reduction = (baseline_cost - HBC_cost) / baseline_cost
  - Baseline: COIN-only (strictest comparison)
  - Target: 30-50% reduction while maintaining coverage ≥ 90%

**Acceptance Criteria:**
- Forward pass counts logged for all methods
- HBC achieves 30-50% cost reduction vs baseline
- Cost savings do not compromise coverage or ECE

---

### FR9: Ablation Study - Sweet Spot Validation
**Priority**: P1 (High)
**Description**: Validate mechanism dependency on correlation sweet spot (ρ ~ 0.5)

**Sub-requirements:**
- FR9.1: Simulate varying correlation levels
  - Test conditions: ρ ∈ {0.2, 0.35, 0.5, 0.65, 0.8}
  - Method: Perturbation of consistency scores or conformal scores
  - Maintain marginal distributions

- FR9.2: ECE measurement across ρ values
  - Compute HBC ECE for each ρ condition
  - Expected: Minimum ECE at ρ ~ 0.5

- FR9.3: Mechanism breakdown analysis
  - Plot: ECE vs ρ curve
  - Statistical test: Polynomial regression (quadratic fit)
  - Hypothesis: U-shaped curve with minimum at ρ ~ 0.5

**Acceptance Criteria:**
- ECE improvement peaks at ρ ~ 0.5 (sweet spot validated)
- ECE degrades at ρ < 0.3 or ρ > 0.7
- Mechanism validates causal theory from hypothesis

---

### FR10: Coverage Guarantee Validation
**Priority**: P0 (Critical)
**Description**: Verify conformal coverage guarantees are maintained under HBC

**Sub-requirements:**
- FR10.1: Coverage computation on test set
  - Formula: Coverage = mean(y_true ∈ I(x))
  - Target: ≥ 90% (conformal guarantee)

- FR10.2: Per-dataset coverage reporting
  - TruthfulQA coverage
  - HH-RLHF coverage
  - SQuAD coverage
  - Aggregate coverage

- FR10.3: Coverage degradation analysis
  - Compare: HBC coverage vs COIN-only coverage
  - Acceptable degradation: < 5% (relative)
  - Failure condition: Coverage < 85%

**Acceptance Criteria:**
- HBC maintains coverage ≥ 90% on all datasets
- No significant degradation vs COIN-only baseline
- Conformal guarantee preserved under mutual calibration

---

## Non-Functional Requirements

### NFR1: Reproducibility
**Priority**: P0 (Critical)
- Fixed random seeds (42) for all stochastic operations
- Deterministic sampling with seed control
- Version pinning for all libraries (transformers, torch, etc.)
- Exact dataset versions specified (HuggingFace dataset IDs with revisions)

### NFR2: Performance
**Priority**: P1 (High)
- Inference throughput: Process 1000 samples in < 2 hours (single GPU)
- Memory footprint: Llama-2-7B in fp16 fits on 24GB GPU
- Batching optimization: Adaptive batch size for hardware

### NFR3: Maintainability
**Priority**: P1 (High)
- Modular code structure: Separate modules for consistency, conformal, HBC
- Configuration file: YAML-based hyperparameter specification
- Logging: Comprehensive metrics logging to JSON files
- Code documentation: Docstrings for all functions

### NFR4: Correctness
**Priority**: P0 (Critical)
- Unit tests for ECE computation (known ground truth cases)
- Integration tests for full pipeline (end-to-end)
- Conformal coverage validation (theoretical ≥ 90%, empirical verification)
- Statistical significance validation (p-value < 0.05 checks)

---

## Success Criteria

### Primary Success Criteria
✅ **ECE Quality**: ECE_HBC < 0.05 on all three datasets (TruthfulQA, HH-RLHF, SQuAD)
✅ **Statistical Significance**: HBC significantly better than all three baselines (p < 0.05 for each pairwise t-test)
✅ **Computational Efficiency**: 30-50% cost reduction vs COIN-only baseline while maintaining coverage ≥ 90%

### Secondary Success Criteria
✅ **Coverage Guarantee**: HBC coverage ≥ 90% on all datasets
✅ **Mechanism Validation**: Ablation shows ECE improvement peaks at ρ ~ 0.5 (sweet spot dependency)
✅ **Baseline Comparisons**: HBC outperforms SelfCheckGPT-only, COIN-only, and Independent Cascade on ECE

### Failure Conditions
❌ **ECE Failure**: If ECE_HBC ≥ 0.05 or improvement < 0.01 vs Independent Cascade → DROP HBC calibration claim
❌ **Cost Failure**: If cost reduction < 20% → DROP computational efficiency claim
❌ **Coverage Failure**: If coverage < 85% → ABANDON coverage guarantee claim
❌ **Mechanism Failure**: If no sweet spot dependency (flat ECE vs ρ curve) → REFINE causal theory

---

## Dependencies

### External Dependencies
- **Foundation Model**: Llama-2-7B (HuggingFace Hub: `meta-llama/Llama-2-7b-hf`)
- **Datasets**: 
  - TruthfulQA (`truthful_qa`, generation task)
  - HH-RLHF (`Anthropic/hh-rlhf`)
  - SQuAD v2 (`squad_v2`)
- **Auxiliary Models**:
  - NLI: `microsoft/deberta-large-mnli`
  - BERTScore: `microsoft/deberta-xlarge-mnli`
  - SentenceBERT: `sentence-transformers/all-mpnet-base-v2`

### Software Dependencies
```python
transformers >= 4.30.0  # Llama-2 support
torch >= 2.0.0  # fp16 inference
datasets >= 2.12.0  # HuggingFace datasets
bert-score >= 0.3.13  # BERTScore implementation
sentence-transformers >= 2.2.2  # Semantic similarity
scipy >= 1.10.0  # Statistical tests
numpy >= 1.24.0  # Numerical operations
```

### Hardware Dependencies
- **Minimum**: 1x NVIDIA GPU with 24GB VRAM (e.g., RTX 3090, A5000)
- **Recommended**: 1x A100 (40GB) for faster inference
- **CPU**: 16+ cores for data preprocessing
- **RAM**: 64GB system RAM
- **Storage**: 100GB for models + datasets + outputs

### Prerequisite Hypotheses
- **H-E1**: MUST be PASS (validates complementarity assumption 0.3 < ρ < 0.7)
  - Status: COMPLETED with PASS
  - Key results: ρ = 0.43-0.46 on all datasets (within sweet spot)

---

## Timeline

**Note**: No time estimates per Phase 3 workflow principles. Steps complete at their natural pace.

### Implementation Phases
1. **Phase 3 Completion**: PRD, Architecture, Logic, Config generation (current)
2. **Phase 4 Execution**: Code implementation following generated tasks
3. **Phase 4.5 Hypothesis Synthesis**: Evidence-refined claims after validation
4. **Phase 6 Paper Writing**: Manuscript preparation (Phase 5 skipped per module config)

### Dependencies Timeline
- **Blocker**: H-E1 validation PASS (COMPLETED ✓)
- **Next**: Phase 4 coding begins after Phase 3 completes

---

## Appendix

### Phase 2C Source
Full experiment specification: `docs/youra_research/h-m-integrated/02c_experiment_brief.md`

### Related Hypotheses
- **H-E1** (prerequisite): Complementarity validation (PASS, ρ = 0.43-0.46)

### Gate Condition Details
**Type**: MUST_WORK
**Rationale**: Core HBC mechanism - must demonstrate both calibration quality AND efficiency
**Downstream Impact**: If PASS → Foundation for production UQ system; If FAIL → Revise joint calibration approach

---

**Document Status**: COMPLETE
**Next Step**: Architecture Design (Phase 3 Step 3)
