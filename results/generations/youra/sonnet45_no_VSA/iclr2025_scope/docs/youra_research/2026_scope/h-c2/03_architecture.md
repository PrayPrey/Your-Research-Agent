# Architecture Design: H-C2 Cross-Framework Contract Validation System

**Hypothesis ID:** h-c2  
**Document Type:** Architecture  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

**Applied Patterns:** Framework adapter pattern, unified tensor API, parallel contract execution

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Analyzed h-m3 actual implementation  
**Analyzed Path**: docs/youra_research/h-m3/code/  
**Findings**: Reusable validator pattern (@validate_composition), exception hierarchy (CompositionViolation), defect test case structure with real issue tracking

---

## 1. System Overview

### 1.1 Architecture Principle
Cross-framework contract validation system extending h-m3's composition-level validation to multi-framework scenarios. Detects integration defects (dtype corruption, shape inconsistency, numerical drift, API incompatibilities) at conversion boundaries before execution.

### 1.2 Core Components

* **contracts/** - 4 contract types (dtype, shape, numerical, operator)
* **framework_adapters/** - 4 adapters (PyTorch, TensorFlow, JAX, ONNX)
* **validators/** - Contract orchestration + defect mapping
* **test_cases.py** - Test set preparation
* **run_experiment.py** - Baseline comparison harness
* **evaluate.py** - Metrics + visualization

### 1.3 Technology Stack

| Component | Technology |
|-----------|-----------|
| Frameworks | PyTorch 1.13, TensorFlow 2.10, JAX 0.4, ONNX 1.12 |
| Tensor Conversion | NumPy 1.22, DLPack |
| Contract Execution | Python concurrent.futures |
| Converters | torch.onnx, tf2onnx, torch2jax |

---

## 2. Module Specifications

### 2.1 Contract Library

#### `contracts/dtype_contracts.py`

**Dependencies**: framework_adapters

```python
class ContractResult:
    passed: bool
    defect_type: str | None
    details: dict
    execution_time: float

class DtypeContract:
    def __init__(self, timeout: float = 1.0): ...
    def execute(self, src_model, tgt_model, test_input: np.ndarray) -> ContractResult: ...
    def get_framework_dtype(self, adapter: 'FrameworkAdapter', model, test_input: np.ndarray) -> str: ...
```

#### `contracts/shape_contracts.py`

**Dependencies**: framework_adapters

```python
class ShapeContract:
    def __init__(self, timeout: float = 0.5): ...
    def execute(self, src_model, tgt_model, test_input: np.ndarray) -> ContractResult: ...
    def infer_output_shape(self, adapter: 'FrameworkAdapter', model, test_input: np.ndarray) -> Tuple[int, ...]: ...
    def compare_shapes(self, src_shape: Tuple[int, ...], tgt_shape: Tuple[int, ...]) -> bool: ...
```

#### `contracts/numerical_contracts.py`

**Dependencies**: framework_adapters, numpy

```python
class NumericalContract:
    def __init__(self, rtol: float = 1e-5, atol: float = 1e-7, timeout: float = 1.0): ...
    def execute(self, src_model, tgt_model, test_input: np.ndarray) -> ContractResult: ...
    def run_inference(self, adapter: 'FrameworkAdapter', model, test_input: np.ndarray) -> np.ndarray: ...
    def check_tolerance(self, src_output: np.ndarray, tgt_output: np.ndarray) -> Tuple[bool, dict]: ...
```

#### `contracts/operator_contracts.py`

**Dependencies**: framework_adapters

```python
class OperatorContract:
    def __init__(self, timeout: float = 1.0): ...
    def execute(self, src_op: str, tgt_op: str, params: Dict[str, Any]) -> ContractResult: ...
    def extract_constraints(self, framework: str, op_name: str) -> Dict[str, Any]: ...
    def validate_compatibility(self, src_constraints: dict, tgt_constraints: dict, params: dict) -> bool: ...
```

### 2.2 Framework Adapters

#### `framework_adapters/pytorch_adapter.py`

**Dependencies**: torch, numpy

```python
class FrameworkAdapter(Protocol):
    def infer_dtype(self, model, test_input: np.ndarray) -> str: ...
    def infer_shape(self, model, test_input: np.ndarray) -> Tuple[int, ...]: ...
    def run_inference(self, model, test_input: np.ndarray) -> np.ndarray: ...
    def convert_input(self, input: np.ndarray) -> 'FrameworkTensor': ...

class PyTorchAdapter:
    def __init__(self, device: str = 'cpu'): ...
    def infer_dtype(self, model: torch.nn.Module, test_input: np.ndarray) -> str: ...
    def infer_shape(self, model: torch.nn.Module, test_input: np.ndarray) -> Tuple[int, ...]: ...
    def run_inference(self, model: torch.nn.Module, test_input: np.ndarray) -> np.ndarray: ...
    def convert_input(self, input: np.ndarray) -> torch.Tensor: ...
    def convert_output(self, output: torch.Tensor) -> np.ndarray: ...
```

#### `framework_adapters/tensorflow_adapter.py`

**Dependencies**: tensorflow, numpy

```python
class TensorFlowAdapter:
    def __init__(self): ...
    def infer_dtype(self, model: tf.keras.Model, test_input: np.ndarray) -> str: ...
    def infer_shape(self, model: tf.keras.Model, test_input: np.ndarray) -> Tuple[int, ...]: ...
    def run_inference(self, model: tf.keras.Model, test_input: np.ndarray) -> np.ndarray: ...
    def convert_input(self, input: np.ndarray) -> tf.Tensor: ...
    def convert_output(self, output: tf.Tensor) -> np.ndarray: ...
```

#### `framework_adapters/jax_adapter.py`

**Dependencies**: jax, numpy

```python
class JAXAdapter:
    def __init__(self): ...
    def infer_dtype(self, model: 'JAXModule', test_input: np.ndarray) -> str: ...
    def infer_shape(self, model: 'JAXModule', test_input: np.ndarray) -> Tuple[int, ...]: ...
    def run_inference(self, model: 'JAXModule', test_input: np.ndarray) -> np.ndarray: ...
    def convert_input(self, input: np.ndarray) -> jax.Array: ...
    def convert_output(self, output: jax.Array) -> np.ndarray: ...
```

#### `framework_adapters/onnx_adapter.py`

**Dependencies**: onnx, onnxruntime, numpy

```python
class ONNXAdapter:
    def __init__(self): ...
    def infer_dtype(self, model: onnx.ModelProto, test_input: np.ndarray) -> str: ...
    def infer_shape(self, model: onnx.ModelProto, test_input: np.ndarray) -> Tuple[int, ...]: ...
    def run_inference(self, model: onnx.ModelProto, test_input: np.ndarray) -> np.ndarray: ...
    def convert_input(self, input: np.ndarray) -> np.ndarray: ...
```

### 2.3 Validation Pipeline

#### `validators/contract_validator.py`

**Dependencies**: contracts, framework_adapters, concurrent.futures

```python
class ValidationReport:
    passed: bool
    defects_detected: List['DefectReport']
    validation_time: float
    contract_results: Dict[str, ContractResult]

class ContractValidator:
    def __init__(self, timeout: float = 10.0, parallel: bool = True): ...
    
    def validate_conversion(
        self,
        src_model,
        tgt_model,
        src_framework: str,
        tgt_framework: str,
        test_inputs: List[np.ndarray],
        contracts: List[str] = None
    ) -> ValidationReport: ...
    
    def execute_contracts_parallel(self, contracts: List, models: tuple, test_inputs: List[np.ndarray]) -> Dict: ...
    def execute_contracts_sequential(self, contracts: List, models: tuple, test_inputs: List[np.ndarray]) -> Dict: ...
    def aggregate_results(self, contract_results: Dict, test_inputs: List[np.ndarray]) -> ValidationReport: ...
```

#### `validators/defect_detector.py`

**Dependencies**: None

```python
@dataclass
class DefectReport:
    defect_type: str
    contract_name: str
    details: dict
    severity: str
    actionable_fix: str

class DefectDetector:
    DEFECT_TAXONOMY = {
        'dtype_mismatch': 'DtypeCorruption',
        'shape_mismatch': 'ShapeInconsistency',
        'numerical_divergence': 'NumericalDrift',
        'api_incompatibility': 'APIIncompatibility'
    }
    
    def map_contract_failure_to_defect(self, contract_result: ContractResult) -> DefectReport: ...
    def generate_actionable_fix(self, defect_type: str, details: dict) -> str: ...
    def calculate_severity(self, defect_type: str, details: dict) -> str: ...
```

### 2.4 Test Infrastructure

#### `test_cases.py`

**Dependencies**: framework_adapters, converters

```python
class TestCase:
    case_id: str
    source_framework: str
    target_framework: str
    src_model: Any
    tgt_model: Any
    test_inputs: List[np.ndarray]
    ground_truth_label: str
    defect_type: str | None
    source_issue: str

def load_onnx_failures(dataset_path: str, limit: int = 200) -> List[TestCase]: ...
def load_crossedwires_sample(dataset_path: str, limit: int = 300) -> List[TestCase]: ...
def generate_synthetic_defects(base_models: List, mutation_count: int = 500) -> List[TestCase]: ...
def prepare_test_set(
    onnx_path: str,
    crossedwires_path: str,
    synthetic_count: int = 500,
    train_ratio: float = 0.7
) -> Tuple[List[TestCase], List[TestCase]]: ...
```

#### `run_experiment.py`

**Dependencies**: validators, test_cases, framework_adapters

```python
class ExperimentResult:
    test_id: str
    source_framework: str
    target_framework: str
    defect_type: str | None
    baseline_detected: bool
    h_c2_detected: bool
    validation_time: float
    contract_breakdown: Dict[str, bool]

def run_baseline_validation(test_case: TestCase) -> bool: ...
def run_h_c2_validation(test_case: TestCase, validator: ContractValidator) -> Dict: ...
def main() -> int: ...
```

#### `evaluate.py`

**Dependencies**: matplotlib, json

```python
def calculate_detection_rate(results: List[ExperimentResult]) -> Dict[str, float]: ...
def calculate_false_positive_rate(results: List[ExperimentResult]) -> float: ...
def calculate_precision(results: List[ExperimentResult]) -> float: ...
def calculate_f1_score(precision: float, recall: float) -> float: ...
def generate_detection_chart(baseline_rate: float, h_c2_rate: float, output_path: Path) -> None: ...
def generate_framework_pair_heatmap(results: List[ExperimentResult], output_path: Path) -> None: ...
def generate_contract_breakdown(results: List[ExperimentResult], output_path: Path) -> None: ...
def main() -> None: ...
```

---

## 3. External Dependencies (Base Hypothesis)

### Module Paths (From h-m3 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| CompositionViolation | `from composition_validator import CompositionViolation` | `h-m3/code/composition_validator.py` |
| DefectTestCase | `from test_cases import DefectTestCase` | `h-m3/code/test_cases.py` |
| ExperimentResult | `from run_experiment import ExperimentResult` | `h-m3/code/run_experiment.py` |

**Note**: h-c2 extends h-m3's test case structure and experiment harness pattern. h-m3 validates cross-library composition within single frameworks; h-c2 extends to multi-framework scenarios with framework adapters.

**Verified from**: `/workspace/TEST_scope/docs/youra_research/h-m3/code/` (actual implementation)

---

## 4. Data Flow

### 4.1 Cross-Framework Validation Pipeline

```
1. Test case loading (test_cases.py)
   ├─ ONNX converter failures (N=200)
   ├─ CrossedWires sample (N=300)
   └─ Synthetic defects (N=500)
   
2. Framework adapter initialization
   ├─ PyTorchAdapter, TensorFlowAdapter, JAXAdapter, ONNXAdapter
   
3. Contract execution (parallel when possible)
   ├─ DtypeContract (timeout: 1s)
   ├─ ShapeContract (timeout: 0.5s)
   ├─ NumericalContract (timeout: 1s)
   └─ OperatorContract (timeout: 1s)
   
4. Result aggregation
   ├─ Contract results → ValidationReport
   └─ Defect detection → DefectReport list
   
5. Baseline comparison
   ├─ End-to-end validation (60s timeout)
   └─ Detection rate comparison
```

### 4.2 Contract Execution Flow

```
For each test case (src_model, tgt_model, test_inputs):
  1. Adapter selection
  2. Parallel contract execution (ThreadPoolExecutor)
  3. Timeout handling (max 10s per test case)
  4. Defect mapping
  5. Report generation
```

### 4.3 Framework Adapter Data Flow

```
Test Input (np.ndarray)
   ↓
FrameworkAdapter.convert_input()
   ↓
Model Inference
   ↓
FrameworkAdapter.convert_output()
   ↓
Contract Validation (np.ndarray)
```

---

## 5. Integration Points

### 5.1 Framework-Specific Handling

**PyTorch:** Device management (CUDA vs CPU), `model.eval()`, `torch.no_grad()`
**TensorFlow:** Disable training mode (`training=False`), `tensor.numpy()`
**JAX:** Functional API with explicit params, `model.apply(params, tensor)`
**ONNX:** Session-based inference, `session.run(None, {input_name: test_input})`

### 5.2 Dtype System Mapping

```python
DTYPE_MAPPING = {
    'float32': {'torch': torch.float32, 'tf': tf.float32, 'jax': jnp.float32, 'numpy': np.float32},
    'float16': {'torch': torch.float16, 'tf': tf.float16, 'jax': jnp.float16, 'numpy': np.float16},
    'int64': {'torch': torch.int64, 'tf': tf.int64, 'jax': jnp.int64, 'numpy': np.int64},
    'int32': {'torch': torch.int32, 'tf': tf.int32, 'jax': jnp.int32, 'numpy': np.int32},
}
```

---

## 6. Performance Optimization

### 6.1 Parallel Contract Execution

**Strategy:** ThreadPoolExecutor with max_workers=4

**Performance Targets:**
- Dtype contract: <0.5s
- Shape contract: <0.3s
- Numerical contract: <1.0s
- Operator contract: <1.0s
- **Total (parallel): <2s**

### 6.2 Zero-Copy Tensor Conversion

**DLPack Integration (when possible):**
```python
def convert_torch_to_tf_zerocopy(torch_tensor: torch.Tensor) -> tf.Tensor:
    try:
        from torch.utils.dlpack import to_dlpack
        from tensorflow.experimental.dlpack import from_dlpack
        return from_dlpack(to_dlpack(torch_tensor))
    except Exception:
        return tf.convert_to_tensor(torch_tensor.cpu().numpy())
```

### 6.3 Caching Strategy

**Model Inference Caching:**
```python
class FrameworkAdapter:
    def __init__(self):
        self._inference_cache = {}
    
    def run_inference(self, model, test_input: np.ndarray) -> np.ndarray:
        cache_key = (id(model), test_input.tobytes())
        if cache_key in self._inference_cache:
            return self._inference_cache[cache_key]
        output = self._run_inference_impl(model, test_input)
        self._inference_cache[cache_key] = output
        return output
```

---

## 7. Error Handling Strategy

### 7.1 Contract Violation Exceptions

**Exception Hierarchy:**
```
ContractViolationError (base)
├── DtypeCorruptionError
├── ShapeInconsistencyError
├── NumericalDriftError
└── APIIncompatibilityError
```

### 7.2 Timeout Handling

```python
from concurrent.futures import TimeoutError

try:
    results = self.execute_contracts_parallel(contracts, models, test_inputs)
except TimeoutError:
    results['timeout_contract'] = ContractResult(passed=False, defect_type='timeout', ...)
```

### 7.3 Framework Crashes

```python
def run_inference(self, model, test_input: np.ndarray) -> np.ndarray:
    try:
        return self._run_inference_impl(model, test_input)
    except RuntimeError as e:
        raise FrameworkInferenceError(f"Inference failed: {e}")
    except Exception as e:
        raise ContractExecutionError(f"Unexpected error: {e}")
```

---

## 8. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Framework Adapters | Implement 4 adapters (PyTorch, TensorFlow, JAX, ONNX) with unified inference API | 16 | Module(4) + Deps(4) + Algo(4) + Integ(4) |
| A-2 | Contract Library | Implement 4 contract types (dtype, shape, numerical, operator) | 15 | Module(4) + Deps(3) + Algo(4) + Integ(4) |
| A-3 | Contract Validator | Orchestrate parallel contract execution with timeout handling | 14 | Module(3) + Deps(3) + Algo(4) + Integ(4) |
| A-4 | Defect Detector | Map contract failures to defect types with actionable fixes | 11 | Module(3) + Deps(1) + Algo(4) + Integ(3) |
| A-5 | Test Case Preparation | Load ONNX failures, CrossedWires sample, generate synthetic defects | 13 | Module(3) + Deps(3) + Algo(3) + Integ(4) |
| A-6 | Baseline Experiments | Implement end-to-end validation baseline for comparison | 10 | Module(2) + Deps(2) + Algo(3) + Integ(3) |
| A-7 | Experiment Harness | Run baseline vs h-c2 comparison on test set | 12 | Module(3) + Deps(2) + Algo(3) + Integ(4) |
| A-8 | Metrics & Visualization | Calculate detection rate, FPR, precision, F1; generate charts | 9 | Module(2) + Deps(2) + Algo(2) + Integ(3) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-1, A-2, A-3], Medium(9-13): [A-4, A-5, A-6, A-7, A-8], Low(4-8): []

---

## 9. Validation Strategy

### 9.1 Detection Rate Validation

**Gate Criteria (SHOULD_WORK):**
- Detection rate ≥70% → PASS
- Detection rate 50-70% → PARTIAL
- Detection rate <50% → FAIL

### 9.2 False Positive Prevention

**Control Tests:** Run contracts on valid conversions (no injected defects)
**Target:** FP rate <10%

### 9.3 Execution Time Constraint

**Requirement:** <5s per model validation
**Expected:** <3.5s (framework adapter init <0.5s + contract execution <2s + defect detection <0.5s + report <0.5s)

---

## 10. Risk Mitigation

### 10.1 Technical Risks

**Risk:** CrossedWires dataset too large (340 GB)
**Mitigation:** Use stratified sample (100 models × 3 architectures = 300 models, ~30 GB)

**Risk:** Numerical tolerance thresholds unclear
**Mitigation:** Tune on validation set (70% train split) before test evaluation

**Risk:** Converter tools fail on test set
**Mitigation:** Pre-filter test set for convertible models only

### 10.2 Evaluation Risks

**Risk:** Detection rate <70% (gate failure)
**Mitigation:** Focus on highest-impact contracts (dtype, shape first)

**Risk:** High false positive rate (>10%)
**Mitigation:** Test on diverse valid conversions (CUDA/CPU, float32/float16 valid cases)

**Risk:** Framework version incompatibilities
**Mitigation:** Pin framework versions (PyTorch 1.13, TensorFlow 2.10, JAX 0.4, ONNX 1.12)

---

## 11. Appendices

### A. Framework Adapter Example

```python
from framework_adapters import PyTorchAdapter, TensorFlowAdapter
import numpy as np

pytorch_adapter = PyTorchAdapter(device='cpu')
tf_adapter = TensorFlowAdapter()

test_input = np.random.randn(1, 3, 32, 32).astype(np.float32)

pytorch_output = pytorch_adapter.run_inference(pytorch_model, test_input)
pytorch_dtype = pytorch_adapter.infer_dtype(pytorch_model, test_input)

tf_output = tf_adapter.run_inference(tf_model, test_input)
tf_dtype = tf_adapter.infer_dtype(tf_model, test_input)

assert pytorch_dtype == tf_dtype, f"Dtype mismatch: {pytorch_dtype} != {tf_dtype}"
```

### B. Contract Validation Example

```python
from validators import ContractValidator

validator = ContractValidator(timeout=10.0, parallel=True)

report = validator.validate_conversion(
    src_model=pytorch_model,
    tgt_model=tf_model,
    src_framework='pytorch',
    tgt_framework='tensorflow',
    test_inputs=[test_input],
    contracts=['dtype', 'shape', 'numerical']
)

if not report.passed:
    for defect in report.defects_detected:
        print(f"Defect: {defect.defect_type} - {defect.actionable_fix}")
```

### C. Detection Rate Calculation

```python
import json

with open('experiment_results.json') as f:
    results = json.load(f)

total_defects = sum(1 for r in results['test_results'] if r['defect_type'] is not None)
h_c2_detected = sum(1 for r in results['test_results'] if r['h_c2_detected'])
baseline_detected = sum(1 for r in results['test_results'] if r['baseline_detected'])

detection_rate = (h_c2_detected / total_defects) * 100
baseline_rate = (baseline_detected / total_defects) * 100

print(f"H-C2 Detection Rate: {detection_rate:.1f}%")
print(f"Baseline Detection Rate: {baseline_rate:.1f}%")
print(f"Improvement: {detection_rate - baseline_rate:.1f}pp")

if detection_rate >= 70:
    print("SHOULD_WORK GATE: PASS")
elif detection_rate >= 50:
    print("SHOULD_WORK GATE: PARTIAL")
else:
    print("SHOULD_WORK GATE: FAIL")
```

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Steps:** Proceed to Phase 4 (Implementation)  
**Expected Timeline:** Phase 4 completion within 1-2 weeks (cross-framework integration complexity)
