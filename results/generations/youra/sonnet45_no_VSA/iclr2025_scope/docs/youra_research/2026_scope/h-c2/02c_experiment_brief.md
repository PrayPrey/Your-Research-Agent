# Phase 2C Experiment Design Brief: H-C2

**Hypothesis ID:** h-c2  
**Hypothesis Type:** CLAIM  
**Hypothesis Statement:** Cross-library contracts (multi-framework consistency) can detect integration defects before execution

**Date:** 2026-07-11  
**Phase:** 2C - Experiment Design  
**Prerequisites:** h-m3 (VALIDATED)

---

## 1. Research Context

### 1.1 Background from Prerequisites

**h-m3 (Cross-Library Composition Contracts):**
- **Mechanism:** Validates cross-library invariants (e.g., tensor format consistency, dtype preservation) at composition boundaries
- **Detection Rate:** 100% (6/6 cross-library defects)
- **Coverage:** Library boundary violations
- **Execution Time:** <1.5s per test
- **Limitation:** Focused on single-framework multi-library scenarios (PyTorch + torchvision, HuggingFace)

### 1.2 Hypothesis Rationale

**Cross-Framework Integration Challenge:**  
Modern ML pipelines increasingly require **multi-framework interoperability**:
- Training in PyTorch → Deployment in TensorFlow Lite (edge devices)
- Model ensembles combining PyTorch and JAX models
- ONNX-based cross-framework model conversion
- Hybrid pipelines using specialized frameworks (PyTorch for training, TensorRT for inference)

**Problem:** Cross-framework integration introduces **semantic inconsistencies** that manifest as:
1. **Numerical discrepancies** (different rounding/accumulation orders)
2. **Operator incompatibilities** (API parameter mismatches)
3. **Silent failures** (models convert but produce wrong results)
4. **Dtype/shape mismatches** across framework boundaries

**Expected Impact:** Cross-library contracts that validate multi-framework consistency (tensor format, dtype, operator semantics) can detect these integration defects **before execution**, preventing silent failures and reducing debugging time.

### 1.3 Literature & Implementation Patterns

**From Archon KB & Exa Research:**

1. **CrossedWires Dataset (2021)** [arXiv:2108.12768]:
   - Syntactically identical PyTorch/TensorFlow models → **0.681 accuracy difference** on CIFAR-10
   - Problem: Framework-specific implementation differences in kernels/layers
   - Gap: No pre-deployment validation for semantic equivalence

2. **DL Framework Interoperability Analysis (JAISCR 2023)** [doi:10.2478/jaiscr-2023-0016]:
   - Multi-perspective V&V approach for DL model conversion
   - Architecture validation + performance verification
   - Key finding: **Single-perspective analysis misses conversion issues** (e.g., correct architecture but wrong weights)

3. **ONNX Model Converter Failure Analysis (2023)** [arXiv:2303.17708]:
   - Analyzed 200 ONNX converter failures across PyTorch/TensorFlow
   - **75% of defects** occur during operator conversion stage
   - Crashes + **silent misbehavior** on certain inputs
   - Gap: Current testing relies on end-to-end models, misses operator-level failures

4. **TensorScope Differential Testing (USENIX Security 2023)**:
   - Cross-framework API differential testing (PyTorch vs TensorFlow)
   - Found inconsistencies in operator behavior (e.g., `avg_pool3d` parameter constraints)
   - Constraint extraction from assertions (`OP_REQUIRES`, `TORCH_CHECK`)
   - Pattern: **Implicit dependencies between API parameters** differ across frameworks

5. **ArrayBridge Unified API**:
   - Unified interface for 6 frameworks (NumPy, PyTorch, TensorFlow, JAX, CuPy, pyclesperanto)
   - DLPack for zero-copy conversions when possible
   - Dtype preservation + OOM recovery
   - Pattern: **Declarative contracts** for memory type + device management

6. **TensorFlow vs PyTorch Numerical Discrepancy** (GitHub #111487):
   - `tf.linalg.matmul` vs `torch.matmul` on 3D float32 tensors
   - Max difference: **2.38e-07** (expected due to kernel/accumulation order)
   - Insight: Small numerical differences compound in deep networks

7. **XAMT Cross-Framework API Matching (2024)** [arXiv:2508.12546]:
   - Matched **839 APIs** across PyTorch, TensorFlow, Keras, JAX
   - Variance-guided differential testing
   - Detected **17 bugs** (12 confirmed) undetectable by intra-framework testing
   - Pattern: **Functionally equivalent APIs** with divergent behavior

### 1.4 Gap Analysis

**Existing Approaches:**
- **ONNX/model converters:** End-to-end validation, miss operator-level failures
- **Differential testing (TensorScope, XAMT):** Reactive (finds bugs after deployment), not preventive
- **Framework-specific testing:** Intra-framework only (CPU vs GPU), misses cross-framework issues

**H-C2 Novelty:**
- **Pre-execution validation:** Contracts execute **before model deployment** (environment-stage)
- **Operator-level granularity:** Validates individual API equivalence, not just end-to-end models
- **Declarative contracts:** Explicit invariants (dtype preservation, numerical tolerance, shape consistency)
- **Proactive detection:** Catches integration defects **before execution**, not during production

---

## 2. Experiment Design

### 2.1 Research Question

**Primary RQ:** Can cross-library contracts detect cross-framework integration defects before execution with ≥70% detection rate and <5s validation time?

**Sub-Questions:**
- RQ1: What proportion of cross-framework integration defects are contractable?
- RQ2: Do contracts detect defects missed by end-to-end model validation?
- RQ3: What is the false positive rate (contracts flag valid conversions)?

### 2.2 Variables

| Variable | Type | Definition | Measurement |
|----------|------|------------|-------------|
| **Contract Type** | Independent | Category of cross-framework contract | {Dtype Preservation, Shape Consistency, Numerical Tolerance, Operator Semantics} |
| **Framework Pair** | Independent | Source → Target frameworks | {PyTorch→TF, TF→PyTorch, PyTorch→JAX, *→ONNX} |
| **Detection Rate** | Dependent | % of defects caught by contracts | (True Positives) / (Total Defects) |
| **Validation Time** | Dependent | Execution time per contract | Seconds |
| **False Positive Rate** | Dependent | % of valid conversions flagged | (False Positives) / (Total Valid) |

**Controlled Variables:**
- Model architecture (VGG16, ResNet18, BERT-base)
- Dataset (CIFAR-10, ImageNet subset, GLUE)
- Conversion tool (ONNX, tf2onnx, torch2jax)

### 2.3 Experimental Conditions

**Baseline Conditions:**
1. **No Validation:** Direct model conversion without contracts
2. **End-to-End Validation:** Full inference on test set after conversion (current best practice)
3. **Framework-Native Testing:** Intra-framework differential testing (CPU vs GPU)

**Treatment Conditions:**
1. **Dtype Preservation Contracts:** Assert dtype consistency across conversion
   ```python
   @cross_framework_contract
   def dtype_preserved(src_model, tgt_model, test_input):
       src_output_dtype = infer_dtype(src_model, test_input)
       tgt_output_dtype = infer_dtype(tgt_model, test_input)
       assert src_output_dtype == tgt_output_dtype
   ```

2. **Shape Consistency Contracts:** Validate output shape equivalence
   ```python
   @cross_framework_contract
   def shape_consistent(src_model, tgt_model, test_input):
       src_shape = infer_shape(src_model, test_input)
       tgt_shape = infer_shape(tgt_model, test_input)
       assert src_shape == tgt_shape
   ```

3. **Numerical Tolerance Contracts:** Check output similarity within tolerance
   ```python
   @cross_framework_contract
   def numerical_tolerance(src_model, tgt_model, test_input, rtol=1e-5, atol=1e-7):
       src_output = src_model(test_input)
       tgt_output = convert_to_src_framework(tgt_model(convert_input(test_input)))
       assert np.allclose(src_output, tgt_output, rtol=rtol, atol=atol)
   ```

4. **Operator Semantics Contracts:** Validate API parameter equivalence
   ```python
   @cross_framework_contract
   def operator_semantics(src_op, tgt_op, params):
       # Check parameter constraints match across frameworks
       src_constraints = extract_constraints(src_op)
       tgt_constraints = extract_constraints(tgt_op)
       assert constraints_compatible(src_constraints, tgt_constraints, params)
   ```

### 2.4 Dataset Preparation

**Dataset Type:** Real-world cross-framework conversion corpus + synthetic defect injection

**Dataset Composition:**

1. **ONNX Converter Failure Corpus** (N=200 issues from arXiv:2303.17708):
   - Source: PyTorch/TensorFlow → ONNX conversion failures
   - Labels: Defect type (crash, silent misbehavior, shape mismatch, dtype error)
   - Split: 70% known defects (validation set), 30% held-out (test set)

2. **CrossedWires Models** (N=2400 models):
   - PyTorch/TensorFlow model pairs (VGG16, ResNet50, DenseNet121)
   - CIFAR-10 dataset, 400 hyperparameter configurations each
   - Accuracy discrepancies ranging 0.00 to 0.681
   - Use: Numerical tolerance contract validation

3. **Synthetic Defect Injection** (N=500 cases):
   - Mutate valid conversions to introduce known defect patterns:
     - Dtype corruption (float32 → float16)
     - Shape mismatch (transpose errors)
     - Operator parameter errors (padding mode, stride)
     - Numerical drift (accumulation order changes)
   - Use: Controlled evaluation of contract detection rates

**Data Preparation Steps:**
1. Download ONNX converter failure corpus from GitHub issue tracker (torch.onnx, tf2onnx)
2. Download CrossedWires dataset (340 GB) via Python API
3. Generate synthetic defects using mutation operators on valid ONNX models
4. Label each case: {defect_type, framework_pair, ground_truth_label}
5. Split: 70% train (contract development), 30% test (final evaluation)

**Dataset Accessibility:**
- ONNX failures: Public GitHub issues (no download required)
- CrossedWires: https://github.com/maxzvyagin/crossedwires (340 GB, requires HPC storage)
- Synthetic defects: Generated programmatically (no external dependency)

**IMPORTANT NOTE:** CrossedWires dataset is 340 GB. If storage is limited, use a **stratified sample** of 100 model pairs per architecture (300 total, ~30 GB) instead of full dataset.

### 2.5 Baseline Methods

| Method | Description | Expected Detection Rate | Execution Time |
|--------|-------------|-------------------------|----------------|
| **No Validation** | Direct conversion, no checks | 0% | ~0s |
| **End-to-End Validation** | Full inference on test set | 40-60% | ~60s (depends on model size) |
| **Framework-Native Testing** | Intra-framework CPU vs GPU | 20-30% | ~30s |
| **ONNX Checker** | `onnx.checker.check_model()` | 30-40% | ~2s |

### 2.6 Success Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| **Detection Rate** | ≥70% | Must outperform end-to-end validation (40-60%) by ≥10pp |
| **Validation Time** | <5s per model | Must be fast enough for CI/CD pipelines |
| **False Positive Rate** | <10% | Low enough to avoid developer fatigue |
| **Defect Coverage** | All 4 contract types detect ≥1 defect class | Demonstrates complementary coverage |

**Gate Type:** SHOULD_WORK (from prerequisites)
- **PASS:** Detection rate ≥70%, validation time <5s, FPR <10%
- **PARTIAL PASS:** Detection rate 50-70% (still useful, narrower scope)
- **FAIL:** Detection rate <50% (not better than end-to-end validation)

---

## 3. Implementation Plan

### 3.1 Contract Library Design

**Module Structure:**
```
cross_framework_contracts/
├── __init__.py
├── dtype_contracts.py       # Dtype preservation contracts
├── shape_contracts.py       # Shape consistency contracts
├── numerical_contracts.py   # Numerical tolerance contracts
├── operator_contracts.py    # Operator semantics contracts
├── framework_adapters/
│   ├── pytorch_adapter.py
│   ├── tensorflow_adapter.py
│   ├── jax_adapter.py
│   └── onnx_adapter.py
└── validators/
    ├── contract_validator.py
    └── defect_detector.py
```

**Key Components:**

1. **Framework Adapters:** Normalize API access across frameworks
   - Unified `infer_dtype()`, `infer_shape()`, `run_inference()` interfaces
   - Handle framework-specific quirks (torch.Tensor vs tf.Tensor vs jax.Array)

2. **Contract Validators:** Execute contracts at conversion boundaries
   - Pre-conversion checks (source model introspection)
   - Post-conversion checks (target model validation)
   - Differential checks (source vs target equivalence)

3. **Defect Detectors:** Map contract failures to defect types
   - Dtype mismatch → "Dtype Corruption"
   - Shape mismatch → "Shape Inconsistency"
   - Numerical divergence → "Numerical Drift"
   - Operator constraint violation → "API Incompatibility"

### 3.2 Experimental Workflow

**Phase 1: Contract Development (1 week)**
1. Implement 4 contract types (dtype, shape, numerical, operator)
2. Test on small validation set (N=50 known defects)
3. Refine contract thresholds (numerical tolerance, shape equivalence rules)

**Phase 2: Large-Scale Evaluation (1 week)**
1. Run contracts on full test set (N=500 defects)
2. Measure detection rate, validation time, false positives
3. Stratify results by defect type, framework pair, model architecture

**Phase 3: Comparison to Baselines (3 days)**
1. Run end-to-end validation on same test set
2. Run framework-native testing on same test set
3. Compare detection rates, execution times, false positives

**Phase 4: Analysis & Reporting (2 days)**
1. Compute metrics (precision, recall, F1, validation time)
2. Identify failure modes (which defects contracts miss)
3. Generate confusion matrix (defect type vs contract type)
4. Write validation report

### 3.3 Computational Requirements

**Hardware:**
- **GPU:** 1x NVIDIA T4 or better (for model inference)
- **RAM:** 32 GB (CrossedWires models can be large)
- **Storage:** 50 GB (30 GB dataset + 20 GB intermediate results)

**Software:**
- Python 3.8+
- PyTorch 1.13+
- TensorFlow 2.10+
- JAX 0.4+
- ONNX 1.12+
- tf2onnx, onnx-tensorflow, torch2jax converters

**Estimated Runtime:**
- Contract development: 8 hours
- Large-scale evaluation: 12 hours (500 models × ~1.5 min/model)
- Baseline comparison: 6 hours
- Analysis: 4 hours
- **Total: ~30 hours** (~2 weeks with parallelization)

---

## 4. Metrics & Analysis

### 4.1 Primary Metrics

1. **Detection Rate (Recall):**
   ```
   DR = True Positives / (True Positives + False Negatives)
   ```
   - Aggregated across all defect types
   - Stratified by: defect type, framework pair, contract type

2. **False Positive Rate:**
   ```
   FPR = False Positives / (False Positives + True Negatives)
   ```
   - Evaluated on valid conversions (no injected defects)

3. **Precision:**
   ```
   Precision = True Positives / (True Positives + False Positives)
   ```

4. **F1 Score:**
   ```
   F1 = 2 × (Precision × Recall) / (Precision + Recall)
   ```

5. **Validation Time:**
   - Mean, median, p95 execution time per contract
   - Breakdown by contract type

### 4.2 Secondary Metrics

1. **Defect Coverage Matrix:**
   - Which contract types detect which defect classes
   - Identify complementary vs redundant contracts

2. **Framework Pair Analysis:**
   - Detection rates by source→target pair
   - Identify high-risk conversion paths

3. **Model Architecture Sensitivity:**
   - Do larger models (ResNet50) have different detection rates than smaller models (VGG16)?

### 4.3 Statistical Analysis

**Hypothesis Testing:**
- **H0:** Cross-library contracts have same detection rate as end-to-end validation
- **H1:** Cross-library contracts have higher detection rate (one-tailed test)
- **Test:** Paired t-test (same test set, two methods)
- **Significance level:** α = 0.05

**Effect Size:**
- Cohen's d for detection rate difference
- Practical significance threshold: d ≥ 0.5 (medium effect)

**Confidence Intervals:**
- 95% CI for detection rate, FPR, validation time
- Bootstrap resampling (1000 iterations) for CI estimation

---

## 5. Expected Outcomes

### 5.1 Quantitative Predictions

| Metric | Baseline (End-to-End) | H-C2 (Contracts) | Improvement |
|--------|----------------------|------------------|-------------|
| Detection Rate | 50% | 75% | +25pp |
| False Positive Rate | 5% | 8% | +3pp (acceptable) |
| Validation Time | 60s | 3s | -57s (20× faster) |
| F1 Score | 0.67 | 0.82 | +0.15 |

### 5.2 Qualitative Insights

**Expected Findings:**
1. **Dtype preservation contracts** detect most cross-framework defects (40%)
2. **Numerical tolerance contracts** have highest false positive rate (15%) due to expected float32 differences
3. **Operator semantics contracts** detect rare but critical API incompatibilities (5%)
4. **PyTorch→TensorFlow conversions** have higher defect rates than TensorFlow→PyTorch

**Failure Modes:**
- Contracts may miss **higher-order semantic defects** (e.g., attention masking logic errors)
- Numerical tolerance thresholds may need **per-operator tuning** (matmul vs conv2d)
- **Dynamic graphs** (PyTorch) harder to validate than static graphs (TensorFlow)

### 5.3 Validation Report Structure

**Output File:** `docs/youra_research/h-c2/04_validation.md`

**Contents:**
1. **Executive Summary:** Pass/Partial/Fail decision + key metrics
2. **Methodology:** Dataset, contracts, baselines
3. **Results:**
   - Detection rate table (overall + stratified)
   - Validation time distribution
   - False positive analysis
   - Confusion matrix (defect type × contract type)
4. **Statistical Analysis:** Hypothesis test results, effect sizes, CIs
5. **Failure Analysis:** Which defects contracts missed + why
6. **Recommendations:** Contract tuning, threshold adjustments, future work

---

## 6. Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **CrossedWires dataset too large** | High | Medium | Use stratified sample (100 models/arch, ~30 GB) |
| **Numerical tolerance thresholds unclear** | Medium | High | Tune on validation set (70% train split) before test eval |
| **Converter tools fail on test set** | Medium | Medium | Pre-filter test set for convertible models only |
| **Low detection rate (<50%)** | Low | High | Expand contract types (add operator-level contracts) |
| **High false positive rate (>20%)** | Medium | Medium | Add framework-specific tolerance rules |

---

## 7. Connections to Main Hypothesis

**Main Hypothesis:** API contracts reduce environment-stage defects by ≥30%

**H-C2 Contribution:**
- **Scope:** Cross-framework integration defects (subset of environment-stage defects)
- **Mechanism:** Validates multi-framework consistency before deployment
- **Evidence:** If detection rate ≥70%, supports claim that contracts catch defects proactively
- **Limitation:** Focused on model conversion; doesn't cover all environment defects

**Dependency Chain:**
- **h-m1** (structural) → **h-m2** (metamorphic) → **h-m3** (cross-library) → **h-c2** (cross-framework)
- Each layer adds complexity: single-library → multi-library → multi-framework
- H-C2 demonstrates contracts scale to **ecosystem-level integration**

---

## 8. References

1. **CrossedWires Dataset:** Zvyagin et al. (2021). arXiv:2108.12768
2. **DL Interoperability V&V:** Park et al. (2023). JAISCR. doi:10.2478/jaiscr-2023-0016
3. **ONNX Converter Failures:** Islam et al. (2023). arXiv:2303.17708
4. **TensorScope Differential Testing:** Deng et al. (2023). USENIX Security
5. **XAMT Cross-Framework API Matching:** Liu et al. (2024). arXiv:2508.12546
6. **ArrayBridge:** https://github.com/OpenHCSDev/arraybridge
7. **TF/PyTorch matmul discrepancy:** https://github.com/tensorflow/tensorflow/issues/111487
8. **Compatibility Issues in DL Systems:** Xiao et al. (2023). FSE. https://guanpingxiao.github.io/publications/FSE23.pdf

---

## 9. Appendices

### A. Contract Code Examples

See Section 2.3 for inline code snippets.

### B. Dataset Access

- **ONNX failures:** Manual collection from GitHub issues (torch.onnx, tf2onnx repos)
- **CrossedWires:** `pip install crossedwires` (requires 340 GB or use sample)
- **Synthetic defects:** Generated via mutation script (provided in implementation)

### C. Experimental Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Numerical tolerance (rtol) | 1e-5 | Standard float32 tolerance |
| Numerical tolerance (atol) | 1e-7 | Absolute tolerance for near-zero values |
| Validation timeout | 10s | Prevent hanging on malformed models |
| Test set size | 500 models | Balance between coverage and runtime |
| Train/test split | 70/30 | Standard ML practice |

---

**Experiment Design Status:** COMPLETED  
**Next Phase:** Phase 3 - Implementation Planning  
**Estimated Duration:** 2 weeks  
**Resource Requirements:** 1 GPU (T4), 32 GB RAM, 50 GB storage
