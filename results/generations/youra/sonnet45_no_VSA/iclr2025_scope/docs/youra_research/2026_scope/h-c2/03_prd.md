# Product Requirements Document: Cross-Framework Contract Validation System

**Hypothesis ID:** h-c2  
**Version:** 1.0  
**Date:** 2026-07-11  
**Phase:** 3 - Implementation Planning

---

## 1. Executive Summary

### 1.1 Product Vision

Build a **cross-framework contract validation system** that detects integration defects in ML model conversions (PyTorch ↔ TensorFlow, PyTorch → JAX, * → ONNX) **before execution**, reducing deployment failures and debugging time in multi-framework ML pipelines.

### 1.2 Success Criteria (from Phase 2C)

| Metric | Target | Baseline (End-to-End) |
|--------|--------|----------------------|
| **Detection Rate** | ≥70% | 50% |
| **Validation Time** | <5s per model | ~60s |
| **False Positive Rate** | <10% | ~5% |
| **Defect Coverage** | All 4 contract types detect ≥1 defect class | N/A |

### 1.3 Gate Type

**SHOULD_WORK** (from prerequisites)
- **PASS:** Detection rate ≥70%, validation time <5s, FPR <10%
- **PARTIAL PASS:** Detection rate 50-70% (still useful, narrower scope)
- **FAIL:** Detection rate <50% (not better than end-to-end validation)

---

## 2. Problem Statement

### 2.1 User Pain Points

**Modern ML practitioners face critical challenges when deploying models across frameworks:**

1. **Silent Failures:** Model converts successfully but produces wrong results (e.g., 0.681 accuracy drop in CrossedWires dataset)
2. **Late Detection:** Defects discovered in production, not during development
3. **Slow Validation:** End-to-end inference tests take minutes per model
4. **Opaque Errors:** Conversion failures lack granular diagnostics (e.g., "operator conversion failed" without specifics)

### 2.2 Real-World Impact

- **ONNX Converter Study (2023):** 75% of defects occur in operator conversion stage, but current testing only validates end-to-end models
- **CrossedWires Dataset:** Syntactically identical PyTorch/TensorFlow models show numerical discrepancies up to 0.681 accuracy difference
- **XAMT Research (2024):** 17 bugs found across 839 matched APIs, undetectable by intra-framework testing

### 2.3 Gap Analysis

**Existing Solutions:**
- End-to-end validation: Slow (60s), misses operator-level failures
- Differential testing (TensorScope, XAMT): Reactive, not preventive
- Framework-native testing: Intra-framework only (CPU vs GPU)

**H-C2 Solution:**
- Pre-execution validation at operator-level granularity
- Declarative contracts with explicit invariants
- Fast (<5s) and proactive (catches defects before deployment)

---

## 3. Product Scope

### 3.1 In-Scope

**Core Features:**
1. **Dtype Preservation Contracts:** Detect dtype mismatches across conversion
2. **Shape Consistency Contracts:** Validate output shape equivalence
3. **Numerical Tolerance Contracts:** Check output similarity within tolerance
4. **Operator Semantics Contracts:** Validate API parameter equivalence

**Supported Framework Pairs:**
- PyTorch → TensorFlow
- TensorFlow → PyTorch  
- PyTorch → JAX
- PyTorch/TensorFlow → ONNX

**Datasets:**
- ONNX Converter Failure Corpus (N=200)
- CrossedWires Models (stratified sample: N=300)
- Synthetic Defect Injection (N=500)

**Baselines for Comparison:**
- No Validation
- End-to-End Validation (current best practice)
- Framework-Native Testing
- ONNX Checker

### 3.2 Out-of-Scope

- **Dynamic graph analysis:** Focus on static model validation
- **Training-time validation:** Contracts execute at deployment/conversion stage only
- **Performance optimization:** Focus on correctness, not inference speed
- **Multi-model pipelines:** Contracts validate single model conversions only
- **Custom operators:** Only standard framework operators (conv2d, matmul, softmax, etc.)

### 3.3 Assumptions

1. Models are convertible (pre-filter test set for valid conversions)
2. Ground-truth labels available (defect type, framework pair)
3. Access to source and target frameworks in same environment
4. Standard dataset splits (70% validation, 30% test)

---

## 4. Functional Requirements

### 4.1 Contract Library

#### FR1: Dtype Preservation Contract
**Priority:** P0 (Critical)

**Description:** Assert dtype consistency across conversion boundaries

**Interface:**
```python
@cross_framework_contract
def dtype_preserved(src_model, tgt_model, test_input) -> ContractResult:
    """
    Args:
        src_model: Source framework model (e.g., torch.nn.Module)
        tgt_model: Target framework model (e.g., tf.keras.Model)
        test_input: Test tensor in source framework format
    
    Returns:
        ContractResult with fields:
            - passed: bool
            - defect_type: str | None (e.g., "Dtype Corruption")
            - details: dict (e.g., {"expected": "float32", "actual": "float16"})
    """
```

**Acceptance Criteria:**
- Detects ≥80% of dtype-related defects in test set
- Execution time <0.5s per model
- False positive rate <5% on valid conversions

#### FR2: Shape Consistency Contract
**Priority:** P0 (Critical)

**Description:** Validate output shape equivalence between source and target models

**Interface:**
```python
@cross_framework_contract
def shape_consistent(src_model, tgt_model, test_input) -> ContractResult:
    """Validates output shape matches across frameworks"""
```

**Acceptance Criteria:**
- Detects ≥90% of shape mismatches (transpose errors, dimension errors)
- Handles dynamic shapes (batch size, sequence length)
- Execution time <0.3s per model

#### FR3: Numerical Tolerance Contract
**Priority:** P0 (Critical)

**Description:** Check output similarity within framework-specific tolerance

**Interface:**
```python
@cross_framework_contract
def numerical_tolerance(
    src_model, 
    tgt_model, 
    test_input, 
    rtol=1e-5, 
    atol=1e-7
) -> ContractResult:
    """
    Validates numerical equivalence using np.allclose semantics
    
    Args:
        rtol: Relative tolerance (default: 1e-5 for float32)
        atol: Absolute tolerance (default: 1e-7 for near-zero values)
    """
```

**Acceptance Criteria:**
- Detects ≥60% of numerical drift defects
- Configurable tolerance per operator (matmul vs conv2d)
- False positive rate <15% (expected due to kernel order differences)

#### FR4: Operator Semantics Contract
**Priority:** P1 (High)

**Description:** Validate API parameter equivalence at operator level

**Interface:**
```python
@cross_framework_contract
def operator_semantics(src_op, tgt_op, params) -> ContractResult:
    """
    Validates parameter constraints match across frameworks
    
    Args:
        src_op: Source operator (e.g., torch.nn.Conv2d)
        tgt_op: Target operator (e.g., tf.keras.layers.Conv2D)
        params: dict of parameter values (e.g., {"padding": "same", "stride": 2})
    """
```

**Acceptance Criteria:**
- Detects ≥70% of API incompatibilities (parameter constraints, default value differences)
- Extracts constraints from framework assertions (TORCH_CHECK, OP_REQUIRES)
- Execution time <1s per operator

### 4.2 Framework Adapters

#### FR5: Unified Inference API
**Priority:** P0 (Critical)

**Description:** Normalize model inference across frameworks

**Interface:**
```python
class FrameworkAdapter(Protocol):
    def infer_dtype(self, model, test_input) -> str:
        """Returns output dtype (e.g., "float32", "int64")"""
    
    def infer_shape(self, model, test_input) -> tuple[int, ...]:
        """Returns output shape (e.g., (1, 10))"""
    
    def run_inference(self, model, test_input) -> np.ndarray:
        """Runs forward pass, returns output as NumPy array"""
    
    def convert_input(self, input: np.ndarray) -> FrameworkTensor:
        """Converts NumPy array to framework-specific tensor"""
```

**Supported Adapters:**
- `PyTorchAdapter`
- `TensorFlowAdapter`
- `JAXAdapter`
- `ONNXAdapter`

**Acceptance Criteria:**
- Handles framework-specific quirks (torch.Tensor vs tf.Tensor vs jax.Array)
- Zero-copy conversions when possible (DLPack)
- Device management (CPU/GPU) transparent

### 4.3 Defect Detection & Reporting

#### FR6: Contract Validator
**Priority:** P0 (Critical)

**Description:** Execute contracts at conversion boundaries and aggregate results

**Interface:**
```python
class ContractValidator:
    def validate_conversion(
        self,
        src_model,
        tgt_model,
        test_inputs: list[np.ndarray],
        contracts: list[Contract]
    ) -> ValidationReport:
        """
        Runs all contracts on multiple test inputs
        
        Returns:
            ValidationReport with fields:
                - passed: bool (all contracts passed)
                - defects_detected: list[DefectReport]
                - validation_time: float (seconds)
                - contract_results: dict[str, ContractResult]
        """
```

**Acceptance Criteria:**
- Executes contracts in parallel when possible
- Aggregates results across multiple test inputs (10-100 inputs per model)
- Timeout mechanism (max 10s per contract)

#### FR7: Defect Mapper
**Priority:** P1 (High)

**Description:** Map contract failures to standardized defect types

**Defect Taxonomy:**
- `DtypeCorruption`: dtype mismatch (float32 → float16)
- `ShapeInconsistency`: shape mismatch (transpose, dimension error)
- `NumericalDrift`: output divergence beyond tolerance
- `APIIncompatibility`: operator parameter constraint violation

**Acceptance Criteria:**
- 100% of contract failures map to ≥1 defect type
- Defect reports include actionable details (expected vs actual values, file:line reference)

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| **Validation Time** | <5s per model | Mean, median, p95 across test set |
| **Contract Overhead** | <2s total (all 4 contracts) | Breakdown per contract type |
| **Throughput** | ≥100 models/hour | With parallelization |

### 5.2 Reliability

- **Timeout Handling:** Contracts must timeout after 10s (prevent hanging on malformed models)
- **Error Recovery:** Framework crashes must not halt entire validation pipeline
- **Determinism:** Same inputs produce same results (no random seeds in validation)

### 5.3 Usability

- **API Simplicity:** Single entry point (`validate_conversion()`) for all contracts
- **Error Messages:** Actionable diagnostics (e.g., "Expected dtype float32, got float16 at layer conv1")
- **CI/CD Integration:** Command-line interface for CI pipelines

### 5.4 Maintainability

- **Modular Design:** Each contract type in separate module
- **Framework Extensibility:** Adding new frameworks requires only adapter implementation
- **Contract Composability:** Contracts can be enabled/disabled independently

---

## 6. Data Requirements

### 6.1 Dataset Composition

| Dataset | Size | Type | Purpose |
|---------|------|------|---------|
| **ONNX Converter Failures** | 200 | Real-world failures | Ecological validity |
| **CrossedWires (Sample)** | 300 | Model pairs | Numerical tolerance validation |
| **Synthetic Defects** | 500 | Mutated models | Controlled evaluation |
| **Total** | 1000 | Mixed | Final test set |

### 6.2 Data Preparation Pipeline

**Step 1: ONNX Failures Collection**
- Source: GitHub issues (torch.onnx, tf2onnx repos)
- Labels: Defect type, framework pair, ground-truth label
- Format: {model_file, defect_type, framework_pair}

**Step 2: CrossedWires Sampling**
- Full dataset: 340 GB (2400 models)
- Stratified sample: 100 models per architecture × 3 architectures = 300 models (~30 GB)
- Criteria: Accuracy discrepancy ≥0.05 (filter out near-identical pairs)

**Step 3: Synthetic Defect Injection**
- Mutation operators:
  - Dtype corruption (float32 → float16, int32 → int64)
  - Shape mismatch (transpose axes, drop dimension)
  - Operator parameter errors (padding mode, stride value)
  - Numerical drift (accumulation order changes)
- Generate 500 mutated models from 100 valid ONNX conversions

**Step 4: Ground-Truth Labeling**
- Each case labeled with:
  - `defect_type`: {DtypeCorruption, ShapeInconsistency, NumericalDrift, APIIncompatibility, None}
  - `framework_pair`: {PyTorch→TF, TF→PyTorch, PyTorch→JAX, *→ONNX}
  - `ground_truth`: {defect, valid}

**Step 5: Train/Test Split**
- 70% validation set (contract development, threshold tuning)
- 30% test set (final evaluation, held-out)

### 6.3 Data Accessibility

- **Storage:** 50 GB total (30 GB CrossedWires sample + 20 GB intermediate results)
- **Download:** Programmatic access (GitHub API for ONNX failures, CrossedWires Python API)
- **Caching:** Models cached locally after first download (no re-download)

---

## 7. System Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────┐
│              Contract Validation System                  │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Dtype      │  │    Shape     │  │  Numerical   │
│  Contracts   │  │  Contracts   │  │  Contracts   │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Framework Adapters  │
              │  ┌────────────────┐  │
              │  │ PyTorchAdapter │  │
              │  │   TFAdapter    │  │
              │  │   JAXAdapter   │  │
              │  │  ONNXAdapter   │  │
              │  └────────────────┘  │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Defect Detector     │
              │  (Mapper & Reporter) │
              └──────────────────────┘
```

**Data Flow:**
1. User provides: `(src_model, tgt_model, test_inputs)`
2. `ContractValidator` executes all enabled contracts in parallel
3. Each contract uses `FrameworkAdapter` to normalize inference
4. Contract results aggregated into `ValidationReport`
5. `DefectDetector` maps failures to defect types
6. Report returned to user with actionable diagnostics

---

## 8. Acceptance Testing

### 8.1 Test Strategy

**Phase 1: Unit Tests (Contract Development)**
- Test each contract type on known defects (N=50 validation set)
- Verify false positive rate on valid conversions (N=20 control set)
- Measure execution time per contract

**Phase 2: Integration Tests (System Validation)**
- Run full validation pipeline on test set (N=300 held-out)
- Compare detection rates to baselines (end-to-end, framework-native)
- Measure validation time distribution (mean, median, p95)

**Phase 3: Statistical Analysis**
- Paired t-test: H-C2 vs end-to-end validation (same test set)
- Effect size (Cohen's d) for detection rate difference
- 95% confidence intervals via bootstrap resampling (1000 iterations)

### 8.2 Success Metrics (Restatement)

| Metric | Threshold | Measurement Method |
|--------|-----------|-------------------|
| **Detection Rate** | ≥70% | (True Positives) / (Total Defects) |
| **Validation Time** | <5s | Mean across test set |
| **False Positive Rate** | <10% | (False Positives) / (Total Valid) |
| **Precision** | ≥80% | (TP) / (TP + FP) |
| **F1 Score** | ≥0.75 | Harmonic mean of precision & recall |

---

## 9. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| **CrossedWires dataset too large** | High | Medium | Use stratified sample (300 models, ~30 GB) |
| **Numerical tolerance thresholds unclear** | Medium | High | Tune on validation set before test evaluation |
| **Converter tools fail on test set** | Medium | Medium | Pre-filter for convertible models only |
| **Low detection rate (<50%)** | Low | High | Expand contract types (add operator-level contracts) |
| **High false positive rate (>20%)** | Medium | Medium | Add framework-specific tolerance rules |
| **Framework version incompatibilities** | Medium | Low | Pin framework versions (PyTorch 1.13, TF 2.10) |

---

## 10. Dependencies

### 10.1 Software Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.8+ | Runtime |
| PyTorch | 1.13+ | Source/target framework |
| TensorFlow | 2.10+ | Source/target framework |
| JAX | 0.4+ | Target framework |
| ONNX | 1.12+ | Target framework |
| tf2onnx | Latest | Converter tool |
| torch2jax | Latest | Converter tool |
| NumPy | 1.22+ | Tensor conversions |
| Pytest | 7.0+ | Testing |

### 10.2 Hardware Requirements

- **GPU:** 1× NVIDIA T4 or better (for model inference)
- **RAM:** 32 GB (CrossedWires models can be large)
- **Storage:** 50 GB (30 GB dataset + 20 GB results)
- **Runtime:** ~30 hours total (~2 weeks with parallelization)

### 10.3 Prerequisite Validation

- **h-m3 (VALIDATED):** Cross-library composition contracts (100% detection, <1.5s)
- Extends single-framework multi-library to multi-framework scenarios

---

## 11. Deliverables

### 11.1 Code Artifacts

1. **Contract Library** (`cross_framework_contracts/`)
   - `dtype_contracts.py`
   - `shape_contracts.py`
   - `numerical_contracts.py`
   - `operator_contracts.py`

2. **Framework Adapters** (`framework_adapters/`)
   - `pytorch_adapter.py`
   - `tensorflow_adapter.py`
   - `jax_adapter.py`
   - `onnx_adapter.py`

3. **Validators** (`validators/`)
   - `contract_validator.py`
   - `defect_detector.py`

4. **CLI Tool** (`cli/validate_conversion.py`)

### 11.2 Documentation

1. **API Documentation** (auto-generated from docstrings)
2. **User Guide** (CLI usage, contract configuration)
3. **Validation Report** (`04_validation.md`)
   - Executive summary (Pass/Partial/Fail)
   - Methodology (datasets, contracts, baselines)
   - Results (detection rate, validation time, FPR, confusion matrix)
   - Statistical analysis (hypothesis test, effect sizes, CIs)
   - Failure analysis (which defects missed, why)
   - Recommendations (threshold tuning, future work)

### 11.3 Test Artifacts

1. **Unit Tests** (`tests/unit/`)
2. **Integration Tests** (`tests/integration/`)
3. **Test Data** (synthetic defects, validation set)
4. **Benchmark Results** (detection rate, validation time, FPR)

---

## 12. Timeline & Milestones

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 3A: Architecture Design** | 2 days | Architecture doc, logic spec, config spec |
| **Phase 3B: Task Breakdown** | 1 day | Epic tasks, subtasks, Archon project |
| **Phase 4: Implementation** | 1 week | Code (contracts, adapters, validators) |
| **Phase 4: Validation** | 1 week | Test results, validation report |
| **Total** | ~2.5 weeks | All deliverables |

---

## 13. Appendices

### A. Glossary

- **Contract:** Declarative invariant validated at conversion boundaries
- **Framework Adapter:** Wrapper normalizing API access across frameworks
- **Defect Type:** Standardized classification of integration failures
- **Detection Rate:** Proportion of defects caught by contracts (recall)
- **False Positive Rate:** Proportion of valid conversions flagged as defects

### B. References

1. CrossedWires Dataset: arXiv:2108.12768
2. ONNX Converter Failures: arXiv:2303.17708
3. XAMT Cross-Framework API Matching: arXiv:2508.12546
4. TensorScope Differential Testing: USENIX Security 2023
5. DL Interoperability V&V: JAISCR 2023 (doi:10.2478/jaiscr-2023-0016)

---

**Document Status:** COMPLETED  
**Next Phase:** Architecture Design (03_architecture.md)  
**Author:** AI Research Assistant  
**Review Status:** Pending validation agent review
