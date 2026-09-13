# Implementation Tasks: H-C2 Cross-Framework Contract Validation

**Hypothesis ID:** h-c2  
**Version:** 1.0  
**Date:** 2026-07-11  
**Phase:** 3 - Implementation Planning  
**Total Budget:** 132 complexity points (Tier 3 hypothesis)

---

## Budget Allocation

| Component | Complexity | Tasks | % of Budget |
|-----------|------------|-------|-------------|
| **Framework Adapters** | 30 | 8 | 22.7% |
| **Contract Library** | 42 | 10 | 31.8% |
| **Validation Pipeline** | 25 | 6 | 18.9% |
| **Dataset Preparation** | 15 | 4 | 11.4% |
| **Testing & Validation** | 15 | 5 | 11.4% |
| **Failsafe Buffer** | 5 | 1 | 3.8% |
| **TOTAL** | **132** | **34** | **100%** |

---

## Epic Tasks (High-Level Components)

### Epic 1: Framework Adapter System [30 points, 8 tasks]

**Goal:** Implement unified framework adapter interface for PyTorch, TensorFlow, JAX, ONNX

**Tasks:**

#### E1-T1: Base Framework Adapter Protocol [3 points]
- **Description:** Define `FrameworkAdapter` protocol with core methods
- **Deliverables:**
  - `framework_adapters/base_adapter.py`
  - Protocol definition: `infer_dtype()`, `infer_shape()`, `run_inference()`, `convert_input()`
- **Acceptance Criteria:** Protocol compiles, type hints validated by MyPy
- **Dependencies:** None

#### E1-T2: PyTorch Adapter Implementation [7 points]
- **Description:** Implement PyTorch framework adapter
- **Deliverables:**
  - `framework_adapters/pytorch_adapter.py`
  - Dtype inference via `torch.nn.Module` forward pass
  - Shape inference handling dynamic dimensions
  - CPU/GPU device management
- **Acceptance Criteria:**
  - Passes unit tests on ResNet18, VGG16
  - Handles dynamic batch size (None → 1)
  - Zero-copy conversion when possible
- **Dependencies:** E1-T1

#### E1-T3: TensorFlow Adapter Implementation [7 points]
- **Description:** Implement TensorFlow framework adapter
- **Deliverables:**
  - `framework_adapters/tensorflow_adapter.py`
  - Eager mode inference support
  - `tf.keras.Model` compatibility
  - Dtype/shape normalization (`tf.DType` → string)
- **Acceptance Criteria:**
  - Passes unit tests on MobileNetV2, EfficientNet
  - Handles TensorFlow SavedModel format
  - GPU visibility configuration works
- **Dependencies:** E1-T1

#### E1-T4: ONNX Adapter Implementation [6 points]
- **Description:** Implement ONNX Runtime adapter
- **Deliverables:**
  - `framework_adapters/onnx_adapter.py`
  - ONNX model loading and metadata extraction
  - `onnxruntime.InferenceSession` integration
  - Dtype inference from `onnx.TensorProto`
- **Acceptance Criteria:**
  - Passes unit tests on ONNX ResNet50, BERT-base
  - Dtype extraction from graph metadata works
  - Handles dynamic shapes (-1 dimensions)
- **Dependencies:** E1-T1

#### E1-T5: JAX Adapter Implementation [5 points]
- **Description:** Implement JAX framework adapter
- **Deliverables:**
  - `framework_adapters/jax_adapter.py`
  - Flax/Haiku model loading
  - JIT compilation handling
  - Dtype/shape inference from `jax.Array`
- **Acceptance Criteria:**
  - Passes unit tests on Flax ResNet18
  - Handles JAX DeviceArray → NumPy conversion
  - JIT-compiled functions supported
- **Dependencies:** E1-T1

#### E1-T6: Dtype Normalization Utility [1 point]
- **Description:** Unified dtype mapping across frameworks
- **Deliverables:**
  - `framework_adapters/dtype_utils.py`
  - `DTYPE_MAP` dictionary (torch.float32 → "float32", etc.)
  - `normalize_dtype()` function
- **Acceptance Criteria:**
  - All framework dtypes map to canonical strings
  - Handles edge cases (bfloat16, int8, uint8)
- **Dependencies:** E1-T2, E1-T3, E1-T4, E1-T5

#### E1-T7: Shape Normalization Utility [1 point]
- **Description:** Unified shape representation across frameworks
- **Deliverables:**
  - `framework_adapters/shape_utils.py`
  - `normalize_shape()` function (torch.Size → tuple)
  - Dynamic dimension handling (None, -1)
- **Acceptance Criteria:**
  - All framework shapes normalize to `tuple[int | None, ...]`
  - Handles scalar outputs correctly
- **Dependencies:** E1-T2, E1-T3, E1-T4, E1-T5

#### E1-T8: Framework Adapter Integration Tests [0 points]
- **Description:** End-to-end adapter testing
- **Deliverables:**
  - `tests/integration/test_adapters.py`
  - Cross-framework inference comparison
  - Device switching tests (CPU ↔ GPU)
- **Acceptance Criteria:**
  - All 4 adapters pass integration tests
  - No memory leaks on repeated inference
- **Dependencies:** E1-T2, E1-T3, E1-T4, E1-T5
- **Note:** Testing task, no budget allocation (covered in Epic 5)

---

### Epic 2: Contract Library [42 points, 10 tasks]

**Goal:** Implement 4 contract types (dtype, shape, numerical, operator)

**Tasks:**

#### E2-T1: Base Contract Class [3 points]
- **Description:** Abstract contract base class
- **Deliverables:**
  - `contracts/base_contract.py`
  - `BaseContract` abstract class
  - `ContractResult` dataclass (passed, defect_type, details)
- **Acceptance Criteria:**
  - Subclasses can override `validate()` method
  - Timeout property configurable per contract
- **Dependencies:** None

#### E2-T2: Dtype Preservation Contract [8 points]
- **Description:** Detect dtype mismatches across conversion
- **Deliverables:**
  - `contracts/dtype_contract.py`
  - `DtypePreservationContract` class
  - `dtype_preserved()` validation function
- **Implementation:**
  ```python
  def validate(self, src_model, tgt_model, test_input) -> ContractResult:
      src_dtype = self.src_adapter.infer_dtype(src_model, test_input)
      tgt_dtype = self.tgt_adapter.infer_dtype(tgt_model, test_input)
      
      passed = (src_dtype == tgt_dtype)
      defect_type = None if passed else "DtypeCorruption"
      details = {"expected": src_dtype, "actual": tgt_dtype} if not passed else {}
      
      return ContractResult(passed=passed, defect_type=defect_type, details=details)
  ```
- **Acceptance Criteria:**
  - Detects float32 → float16 corruption
  - Execution time <0.5s per model
  - False positive rate <5% on valid conversions
- **Dependencies:** E2-T1, E1-T6

#### E2-T3: Shape Consistency Contract [8 points]
- **Description:** Validate output shape equivalence
- **Deliverables:**
  - `contracts/shape_contract.py`
  - `ShapeConsistencyContract` class
  - Dynamic shape handling (batch size = None)
- **Implementation:**
  ```python
  def validate(self, src_model, tgt_model, test_input) -> ContractResult:
      src_shape = self.src_adapter.infer_shape(src_model, test_input)
      tgt_shape = self.tgt_adapter.infer_shape(tgt_model, test_input)
      
      compatible = self._shapes_compatible(src_shape, tgt_shape)
      # ... (implementation details in 03_logic.md Section 1.2)
  ```
- **Acceptance Criteria:**
  - Detects transpose errors (NCHW vs NHWC)
  - Handles dynamic batch size correctly
  - Execution time <0.3s per model
- **Dependencies:** E2-T1, E1-T7

#### E2-T4: Numerical Tolerance Contract [12 points]
- **Description:** Validate numerical equivalence within tolerance
- **Deliverables:**
  - `contracts/numerical_contract.py`
  - `NumericalToleranceContract` class
  - `np.allclose` semantics implementation
  - Per-operator tolerance overrides
- **Implementation:**
  ```python
  def validate(self, src_model, tgt_model, test_input, rtol=1e-5, atol=1e-7) -> ContractResult:
      src_output = self.src_adapter.run_inference(src_model, test_input)
      tgt_output = self.tgt_adapter.run_inference(tgt_model, test_input)
      
      passed = np.allclose(src_output, tgt_output, rtol=rtol, atol=atol)
      # ... (implementation details in 03_logic.md Section 1.3)
  ```
- **Acceptance Criteria:**
  - Detects numerical drift >1e-5 relative tolerance
  - Per-operator tolerance tuning works (matmul, conv2d, softmax)
  - Handles Inf/NaN values correctly
  - Execution time <2s per model
- **Dependencies:** E2-T1

#### E2-T5: Operator Semantics Contract [8 points]
- **Description:** Validate operator-level API equivalence
- **Deliverables:**
  - `contracts/operator_contract.py`
  - `OperatorSemanticsContract` class
  - Constraint extraction from TORCH_CHECK, OP_REQUIRES
- **Implementation:**
  ```python
  def validate(self, src_op, tgt_op, params) -> ContractResult:
      src_constraints = self._extract_constraints(src_op)
      tgt_constraints = self._extract_constraints(tgt_op)
      
      compatible = self._constraints_compatible(src_constraints, tgt_constraints, params)
      # ... (implementation details in 03_logic.md Section 1.4)
  ```
- **Acceptance Criteria:**
  - Detects API incompatibilities (padding mode, stride constraints)
  - Extracts constraints from PyTorch TORCH_CHECK statements
  - Execution time <1s per operator
- **Dependencies:** E2-T1

#### E2-T6: Contract Decorator [2 points]
- **Description:** `@cross_framework_contract` decorator for contracts
- **Deliverables:**
  - `contracts/decorators.py`
  - Timeout enforcement
  - Exception handling wrapper
- **Acceptance Criteria:**
  - Contracts timeout after 10s
  - Framework crashes caught and returned as ContractResult
- **Dependencies:** E2-T1

#### E2-T7: Tolerance Tuning Utility [1 point]
- **Description:** Auto-tune rtol/atol based on validation set
- **Deliverables:**
  - `contracts/tolerance_tuner.py`
  - Binary search algorithm for optimal tolerance
  - Target false positive rate <5%
- **Acceptance Criteria:**
  - Tunes tolerance on 50-sample validation set in <5 minutes
  - Achieves target FPR ≤5%
- **Dependencies:** E2-T4

#### E2-T8: Contract Result Aggregation [0 points]
- **Description:** Aggregate contract results across multiple test inputs
- **Deliverables:**
  - Logic in `ContractValidator` (see Epic 3)
  - Per-input result tracking
- **Acceptance Criteria:**
  - Reports which test inputs failed
  - Computes overall pass/fail status
- **Dependencies:** E2-T1
- **Note:** Covered in Epic 3 validation pipeline

#### E2-T9: Defect Type Taxonomy [0 points]
- **Description:** Standardized defect classification
- **Deliverables:**
  - `contracts/defect_types.py`
  - Enum: DtypeCorruption, ShapeInconsistency, NumericalDrift, APIIncompatibility
- **Acceptance Criteria:**
  - All contract failures map to ≥1 defect type
- **Dependencies:** E2-T1

#### E2-T10: Contract Unit Tests [0 points]
- **Description:** Unit tests for all 4 contract types
- **Deliverables:**
  - `tests/unit/test_contracts.py`
  - Known defect test cases
  - False positive test cases (valid conversions)
- **Acceptance Criteria:**
  - 100% coverage on contract validation logic
  - All known defects detected
- **Dependencies:** E2-T2, E2-T3, E2-T4, E2-T5
- **Note:** Testing task, covered in Epic 5

---

### Epic 3: Validation Pipeline [25 points, 6 tasks]

**Goal:** Implement contract orchestration and validation reporting

**Tasks:**

#### E3-T1: ContractValidator Class [10 points]
- **Description:** Orchestrate contract execution and result aggregation
- **Deliverables:**
  - `validators/contract_validator.py`
  - `ContractValidator` class
  - Parallel contract execution (ThreadPoolExecutor)
  - Timeout management
- **Implementation:**
  ```python
  class ContractValidator:
      def validate_conversion(
          self, src_model, tgt_model, test_inputs: list[np.ndarray]
      ) -> ValidationReport:
          # ... (implementation in 03_logic.md Section 3.1)
  ```
- **Acceptance Criteria:**
  - Executes 4 contracts in parallel
  - Aggregates results across 10-100 test inputs
  - Total validation time <5s per model
  - Handles timeout after 10s per contract
- **Dependencies:** E2-T1, E2-T2, E2-T3, E2-T4, E2-T5

#### E3-T2: ValidationReport Dataclass [2 points]
- **Description:** Aggregated validation report schema
- **Deliverables:**
  - `validators/validation_report.py`
  - `ValidationReport` dataclass
  - JSON/Markdown export methods
- **Schema:**
  ```python
  @dataclass
  class ValidationReport:
      passed: bool
      defects_detected: list[DefectReport]
      validation_time: float
      contract_results: list[ContractResult]
      framework_pair: tuple[str, str]
      test_input_count: int
  ```
- **Acceptance Criteria:**
  - Exports to JSON with datetime serialization
  - Exports to Markdown with formatting
- **Dependencies:** E2-T1

#### E3-T3: DefectDetector Class [5 points]
- **Description:** Map contract failures to defect reports
- **Deliverables:**
  - `validators/defect_detector.py`
  - `DefectDetector` class
  - Severity assessment (CRITICAL, HIGH, MEDIUM, LOW)
  - Actionable fix suggestions
- **Implementation:**
  ```python
  class DefectDetector:
      DEFECT_TAXONOMY = {
          "DtypeCorruption": "Dtype mismatch (e.g., float32 → float16)",
          # ... (full taxonomy in 03_architecture.md Section 2.3.2)
      }
      
      def detect_defects(self, contract_results: list[ContractResult]) -> list[DefectReport]:
          # ... (implementation in 03_architecture.md)
  ```
- **Acceptance Criteria:**
  - 100% of contract failures map to defect reports
  - Actionable fix suggestions for top 4 defect types
  - Severity correctly assessed
- **Dependencies:** E2-T1, E2-T9

#### E3-T4: Parallel Execution Engine [5 points]
- **Description:** ThreadPoolExecutor-based parallel contract execution
- **Deliverables:**
  - Logic in `ContractValidator._validate_parallel()`
  - ThreadPool management
  - Exception handling per thread
- **Acceptance Criteria:**
  - 4 contracts execute concurrently
  - Thread crashes don't halt entire validation
  - Memory cleanup after execution
- **Dependencies:** E3-T1

#### E3-T5: Result Caching [2 points]
- **Description:** Cache inference results for multiple contracts on same input
- **Deliverables:**
  - `validators/inference_cache.py`
  - LRU cache for (model_id, test_input_hash) → output
- **Acceptance Criteria:**
  - Cache hit rate >80% when multiple contracts run on same input
  - Memory usage <2 GB for 100 models
- **Dependencies:** E3-T1

#### E3-T6: Early Termination Logic [1 point]
- **Description:** Stop validation on critical contract failure
- **Deliverables:**
  - Optional early termination flag in `ContractValidator`
  - Stop on dtype/shape mismatch
- **Acceptance Criteria:**
  - Early termination saves >50% time on critical failures
  - Partial ValidationReport returned
- **Dependencies:** E3-T1

---

### Epic 4: Dataset Preparation [15 points, 4 tasks]

**Goal:** Prepare ONNX failures, CrossedWires sample, synthetic defects

**Tasks:**

#### E4-T1: ONNX Converter Failure Corpus [5 points]
- **Description:** Collect ONNX conversion failures from GitHub issues
- **Deliverables:**
  - `dataset/onnx_failures.py`
  - GitHub API scraper for torch.onnx, tf2onnx issues
  - Defect labeling script
  - Dataset: 200 ONNX failures with ground-truth labels
- **Data Source:**
  - https://github.com/pytorch/pytorch/issues (filter: label:module:onnx)
  - https://github.com/onnx/tensorflow-onnx/issues
- **Acceptance Criteria:**
  - 200 failures collected
  - Labels: defect_type, framework_pair, ground_truth
  - JSON format: {model_file, defect_type, framework_pair}
- **Dependencies:** None

#### E4-T2: CrossedWires Stratified Sampling [5 points]
- **Description:** Sample 300 models from CrossedWires dataset (340 GB)
- **Deliverables:**
  - `dataset/crossedwires_sampler.py`
  - Stratified sampling by architecture (VGG16, ResNet50, DenseNet121)
  - 100 models per architecture × 3 = 300 models (~30 GB)
  - Filter: accuracy discrepancy ≥0.05
- **Data Source:**
  - https://github.com/maxzvyagin/crossedwires
  - Install: `pip install crossedwires`
- **Acceptance Criteria:**
  - 300 models sampled (balanced across architectures)
  - Storage <30 GB
  - All models loadable in PyTorch and TensorFlow
- **Dependencies:** None

#### E4-T3: Synthetic Defect Injection [3 points]
- **Description:** Generate 500 synthetic defects via mutation
- **Deliverables:**
  - `dataset/synthetic_defects.py`
  - Mutation operators: dtype corruption, shape mismatch, parameter errors
  - Ground-truth labels
- **Mutation Types:**
  - Dtype corruption: float32 → float16
  - Shape mismatch: transpose axes
  - Operator parameter errors: padding mode, stride
  - Numerical drift: accumulation order changes
- **Acceptance Criteria:**
  - 500 synthetic defects generated
  - All defects verified to fail baseline validation
  - Ground-truth labels accurate
- **Dependencies:** E4-T1 (use valid ONNX models as base)

#### E4-T4: Dataset Splits and Metadata [2 points]
- **Description:** Train/test split (70/30) and metadata generation
- **Deliverables:**
  - `dataset/splits.py`
  - 70% validation set (contract development, threshold tuning)
  - 30% test set (final evaluation, held-out)
  - Metadata JSON: {dataset_name, size, split, labels}
- **Acceptance Criteria:**
  - Reproducible splits (fixed random seed)
  - Metadata includes all required fields
  - Test set never used for tuning
- **Dependencies:** E4-T1, E4-T2, E4-T3

---

### Epic 5: Testing & Validation [15 points, 5 tasks]

**Goal:** Comprehensive testing and experimental validation

**Tasks:**

#### E5-T1: Unit Tests (Contract Library) [3 points]
- **Description:** Unit tests for all 4 contract types
- **Deliverables:**
  - `tests/unit/test_dtype_contract.py`
  - `tests/unit/test_shape_contract.py`
  - `tests/unit/test_numerical_contract.py`
  - `tests/unit/test_operator_contract.py`
- **Coverage Targets:**
  - 100% coverage on contract validation logic
  - Known defects: dtype mismatch, shape transpose, numerical drift
  - False positives: valid conversions flagged incorrectly
- **Acceptance Criteria:**
  - All known defects detected
  - False positive rate <5%
  - Execution time <0.5s per test
- **Dependencies:** E2-T2, E2-T3, E2-T4, E2-T5

#### E5-T2: Integration Tests (Full Pipeline) [4 points]
- **Description:** End-to-end validation pipeline testing
- **Deliverables:**
  - `tests/integration/test_validation_pipeline.py`
  - Cross-framework conversion tests (PyTorch→TF, TF→PyTorch, *→ONNX)
  - Baseline comparison tests
- **Test Cases:**
  - ResNet18 PyTorch → ONNX (valid conversion)
  - VGG16 PyTorch → TensorFlow (dtype mismatch injected)
  - MobileNetV2 TensorFlow → ONNX (shape transpose injected)
- **Acceptance Criteria:**
  - All test cases pass
  - Validation time <5s per model
  - No memory leaks on repeated runs
- **Dependencies:** E3-T1, E4-T3

#### E5-T3: Baseline Method Implementation [3 points]
- **Description:** Implement baseline validation methods for comparison
- **Deliverables:**
  - `baselines/end_to_end_validation.py` (full inference on test set)
  - `baselines/framework_native_testing.py` (CPU vs GPU)
  - `baselines/onnx_checker.py` (onnx.checker.check_model)
- **Acceptance Criteria:**
  - All baselines run on same test set
  - Execution time measured
  - Detection rates logged
- **Dependencies:** E4-T4

#### E5-T4: Large-Scale Evaluation [4 points]
- **Description:** Run contracts on full test set (N=300)
- **Deliverables:**
  - `experiments/run_validation.py`
  - Execute contracts on 300 held-out models
  - Measure detection rate, validation time, FPR
  - Stratify results by defect type, framework pair
- **Metrics:**
  - Detection rate (TP / (TP + FN))
  - False positive rate (FP / (FP + TN))
  - Precision, F1 score
  - Validation time (mean, median, p95)
- **Acceptance Criteria:**
  - Detection rate ≥70% (SHOULD_WORK gate)
  - Validation time <5s per model
  - FPR <10%
- **Dependencies:** E3-T1, E4-T4, E5-T3

#### E5-T5: Statistical Analysis [1 point]
- **Description:** Hypothesis testing and confidence intervals
- **Deliverables:**
  - `analysis/statistical_tests.py`
  - Paired t-test (H-C2 vs end-to-end validation)
  - Cohen's d effect size
  - 95% CI via bootstrap resampling (1000 iterations)
- **Tests:**
  - H0: Detection rate(H-C2) = Detection rate(baseline)
  - H1: Detection rate(H-C2) > Detection rate(baseline)
  - Significance level: α = 0.05
- **Acceptance Criteria:**
  - H0 rejected (p < 0.05)
  - Effect size d ≥ 0.5 (medium effect)
  - 95% CI for detection rate reported
- **Dependencies:** E5-T4

---

### Epic 6: Failsafe Buffer [5 points, 1 task]

**Goal:** Reserve budget for unforeseen issues

#### E6-T1: Debugging and Fixes [5 points]
- **Description:** Buffer for unexpected bugs, framework version issues
- **Deliverables:** Bug fixes, workarounds
- **Dependencies:** All other epics

---

## Task Dependency Graph

```
E1-T1 (Base Adapter)
  ├─→ E1-T2 (PyTorch Adapter)
  ├─→ E1-T3 (TensorFlow Adapter)
  ├─→ E1-T4 (ONNX Adapter)
  ├─→ E1-T5 (JAX Adapter)
  │     ├─→ E1-T6 (Dtype Utils)
  │     └─→ E1-T7 (Shape Utils)
  │           └─→ E1-T8 (Adapter Integration Tests)

E2-T1 (Base Contract)
  ├─→ E2-T2 (Dtype Contract) ──→ E1-T6
  ├─→ E2-T3 (Shape Contract) ──→ E1-T7
  ├─→ E2-T4 (Numerical Contract)
  │     └─→ E2-T7 (Tolerance Tuner)
  ├─→ E2-T5 (Operator Contract)
  └─→ E2-T6 (Decorator)
        └─→ E2-T9 (Defect Types)
              └─→ E2-T10 (Contract Tests)

E3-T1 (ContractValidator) ──→ E2-T1, E2-T2, E2-T3, E2-T4, E2-T5
  ├─→ E3-T2 (ValidationReport)
  ├─→ E3-T3 (DefectDetector) ──→ E2-T9
  ├─→ E3-T4 (Parallel Execution)
  ├─→ E3-T5 (Result Caching)
  └─→ E3-T6 (Early Termination)

E4-T1 (ONNX Failures)
E4-T2 (CrossedWires Sample)
E4-T3 (Synthetic Defects) ──→ E4-T1
E4-T4 (Dataset Splits) ──→ E4-T1, E4-T2, E4-T3

E5-T1 (Unit Tests) ──→ E2-T2, E2-T3, E2-T4, E2-T5
E5-T2 (Integration Tests) ──→ E3-T1, E4-T3
E5-T3 (Baselines) ──→ E4-T4
E5-T4 (Large-Scale Eval) ──→ E3-T1, E4-T4, E5-T3
E5-T5 (Statistical Analysis) ──→ E5-T4

E6-T1 (Failsafe) ──→ All Epics
```

---

## Implementation Order

**Phase 4A: Foundation (Week 1)**
1. E1-T1 → E1-T2 → E1-T3 → E1-T4 → E1-T5 → E1-T6 → E1-T7 → E1-T8
2. E2-T1 → E2-T2 → E2-T3 → E2-T4 → E2-T5 → E2-T6 → E2-T9
3. E4-T1 → E4-T2 → E4-T3 → E4-T4

**Phase 4B: Validation Pipeline (Week 2)**
4. E3-T1 → E3-T2 → E3-T3 → E3-T4 → E3-T5 → E3-T6
5. E5-T1 → E5-T2 → E5-T3

**Phase 4C: Evaluation (Week 3)**
6. E2-T7 (Tolerance Tuning)
7. E5-T4 (Large-Scale Evaluation)
8. E5-T5 (Statistical Analysis)
9. E6-T1 (Debugging Buffer)

---

## Success Criteria (from PRD)

| Metric | Threshold | Measurement Method |
|--------|-----------|-------------------|
| **Detection Rate** | ≥70% | (TP) / (TP + FN) on test set |
| **Validation Time** | <5s per model | Mean across test set |
| **False Positive Rate** | <10% | (FP) / (FP + TN) on valid conversions |
| **Precision** | ≥80% | (TP) / (TP + FP) |
| **F1 Score** | ≥0.75 | Harmonic mean of precision & recall |

**Gate Type:** SHOULD_WORK
- **PASS:** Detection rate ≥70%, validation time <5s, FPR <10%
- **PARTIAL PASS:** Detection rate 50-70% (still useful, narrower scope)
- **FAIL:** Detection rate <50% (not better than end-to-end validation)

---

## Risk Mitigation

| Risk | Mitigation | Task |
|------|------------|------|
| **CrossedWires dataset too large (340 GB)** | Use stratified sample (300 models, ~30 GB) | E4-T2 |
| **Numerical tolerance thresholds unclear** | Tune on validation set before test eval | E2-T7 |
| **Framework version incompatibilities** | Pin versions (PyTorch 1.13, TF 2.10) | E1-T2, E1-T3 |
| **Low detection rate (<50%)** | Expand contract types (add operator-level contracts) | E2-T5 |
| **High false positive rate (>20%)** | Framework-specific tolerance rules | E2-T7 |

---

## Deliverables Checklist

- [ ] Framework Adapters (PyTorch, TensorFlow, JAX, ONNX)
- [ ] 4 Contract Types (Dtype, Shape, Numerical, Operator)
- [ ] ContractValidator with parallel execution
- [ ] DefectDetector with actionable diagnostics
- [ ] Dataset (1000 models: 200 ONNX + 300 CrossedWires + 500 synthetic)
- [ ] Unit Tests (100% coverage on contracts)
- [ ] Integration Tests (end-to-end pipeline)
- [ ] Baseline Methods (end-to-end, framework-native, ONNX checker)
- [ ] Large-Scale Evaluation Results (detection rate, FPR, validation time)
- [ ] Statistical Analysis (t-test, effect size, 95% CI)
- [ ] Validation Report (04_validation.md)

---

**Task List Status:** COMPLETED  
**Next Phase:** Phase 4 - Implementation & Validation  
**Estimated Duration:** 3 weeks  
**Total Complexity:** 132 points (Tier 3)
