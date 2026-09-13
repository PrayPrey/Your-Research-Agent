# Architecture Design: H-M1 Structural Contract Validation

**Hypothesis ID:** h-m1  
**Document Type:** Architecture  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

**Applied Patterns:** PyTorch decorator validation, caching mechanisms (torch.compile pattern), defect injection frameworks

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: green-field - no code to analyze  
**Analyzed Path**: N/A  
**Findings**: New implementation from scratch

---

## 1. System Overview

### 1.1 Architecture Principle
Structural contract validation library using decorator-based probes that execute at module initialization time (import phase) to detect API violations before training begins.

### 1.2 Core Components

```
contracts/          # Decorator library for structural validation
├── validator.py    # @validate_structural decorator
├── probes.py       # Import-time shape/dtype/device probes  
├── cache.py        # Probe result caching
└── exceptions.py   # Contract violation exceptions

defects/            # Defect injection framework
├── corpus.py       # Jiang et al. defect corpus parser
├── injector.py     # Monkey-patching and source modification
└── catalog.json    # 200 structural defect specifications

baselines/          # Control experiments
├── sanity_check.py # ResNet-18 + CIFAR-10 validation
├── no_contracts.py # Time-to-failure measurements
└── execution_only.py # 1-sample forward pass baseline

experiments/        # Treatment experiments
├── run_contracts.py # Contract-enabled defect injection
├── measure_detection.py # Detection rate calculation
└── measure_false_positives.py # FP rate evaluation

results/            # Experiment outputs
└── *.csv          # Detection rates, execution times, false positives
```

### 1.3 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Decorator | Python `functools.wraps` | Wrap functions with validation |
| Type Hints | `typing.Annotated` | Shape/dtype specifications |
| Probing | PyTorch 2.x dynamic shapes | Execute 1-sample batches |
| Caching | `diskcache` | Store probe results |
| Defect Injection | AST manipulation, monkey-patching | Modify libraries at runtime |
| Dataset | `torchvision.datasets.CIFAR10` | Test dataset |
| Model | `torchvision.models.resnet18` | Test model |

---

## 2. Module Specifications

### 2.1 Contract Library

#### `contracts/validator.py`

**Dependencies**: probes, cache, exceptions

```python
from typing import Annotated, Dict, Callable, Any
import torch

def validate_structural(
    inputs: Dict[str, Annotated[torch.Tensor, str]],
    outputs: Dict[str, Annotated[torch.Tensor, str]],
    dtype: Dict[str, torch.dtype] = {},
    device_consistency: bool = False,
    enable_cache: bool = True
) -> Callable:
    """Decorator for import-time structural validation."""
    ...

class StructuralValidator:
    def __init__(self, spec: ValidationSpec): ...
    def validate(self, func: Callable) -> Callable: ...
    def run_probe(self, func: Callable, sample_inputs: Dict) -> ProbeResult: ...
```

#### `contracts/probes.py`

**Dependencies**: None (PyTorch stdlib)

```python
class ShapeProbe:
    def __init__(self, expected_shape: str): ...
    def validate(self, tensor: torch.Tensor, symbolic_dims: List[str]) -> bool: ...
    def generate_sample(self, shape_spec: str, dtype: torch.dtype) -> torch.Tensor: ...

class DeviceProbe:
    def check_consistency(self, tensors: List[torch.Tensor]) -> bool: ...
    def get_device_map(self, tensors: List[torch.Tensor]) -> Dict[str, str]: ...

class DtypeProbe:
    def validate(self, tensor: torch.Tensor, expected: torch.dtype) -> bool: ...

class NullCheckProbe:
    def validate(self, output: Any) -> bool: ...
```

#### `contracts/cache.py`

**Dependencies**: diskcache

```python
from diskcache import Cache
from pathlib import Path

class ProbeCache:
    def __init__(self, cache_dir: Path = Path.home() / ".cache/structural_contracts"): ...
    def get(self, key: str) -> ProbeResult: ...
    def set(self, key: str, result: ProbeResult, ttl: int = 86400): ...
    def invalidate(self, pattern: str): ...
    def compute_key(self, func: Callable, spec: ValidationSpec) -> str: ...
```

#### `contracts/exceptions.py`

**Dependencies**: None

```python
class StructuralContractViolation(Exception):
    def __init__(self, expected: Any, actual: Any, context: str): ...
    def format_message(self) -> str: ...

class ShapeViolation(StructuralContractViolation): ...
class DeviceViolation(StructuralContractViolation): ...
class DtypeViolation(StructuralContractViolation): ...
class NullOutputViolation(StructuralContractViolation): ...
```

### 2.2 Defect Injection Framework

#### `defects/corpus.py`

**Dependencies**: None (JSON stdlib)

```python
from typing import List
import json

class DefectCorpus:
    def __init__(self, catalog_path: str): ...
    def load(self) -> List[DefectSpec]: ...
    def filter_by_category(self, category: str) -> List[DefectSpec]: ...
    def sample(self, n: int, seed: int = 42) -> List[DefectSpec]: ...

class DefectSpec:
    defect_id: str
    category: str
    injection_method: str
    injection_target: str
    expected_shape: str
    actual_shape: str
    expected_failure_stage: str
```

#### `defects/injector.py`

**Dependencies**: corpus, ast

```python
import ast

class DefectInjector:
    def __init__(self, defect: DefectSpec): ...
    def inject(self) -> None: ...
    def rollback(self) -> None: ...

class MonkeyPatchInjector(DefectInjector):
    def inject_runtime(self, target: Any, patch: Callable) -> None: ...

class SourceModificationInjector(DefectInjector):
    def modify_ast(self, source_path: str, transformation: ASTTransform) -> None: ...
```

### 2.3 Baseline Experiments

#### `baselines/sanity_check.py`

**Dependencies**: torch, torchvision

```python
def run_sanity_check() -> Dict[str, float]:
    """Train ResNet-18 on CIFAR-10 for 1 epoch, verify accuracy ≥70%."""
    ...

def load_cifar10(batch_size: int = 32) -> DataLoader: ...
def load_resnet18(num_classes: int = 10) -> nn.Module: ...
def train_epoch(model: nn.Module, loader: DataLoader) -> float: ...
def evaluate(model: nn.Module, loader: DataLoader) -> float: ...
```

#### `baselines/no_contracts.py`

**Dependencies**: defects, torch, torchvision

```python
def measure_time_to_failure(defect: DefectSpec) -> float:
    """Inject defect and measure time until first error."""
    ...

def run_baseline(catalog_path: str, n_samples: int = 50) -> pd.DataFrame:
    """Run no-contract baseline on defect samples."""
    ...
```

#### `baselines/execution_only.py`

**Dependencies**: defects, torch, torchvision

```python
def detect_via_single_forward(defect: DefectSpec) -> bool:
    """Run import + 1-sample forward pass, check for errors."""
    ...

def run_execution_baseline(catalog_path: str, n_samples: int = 50) -> pd.DataFrame:
    """Run execution-only detection baseline."""
    ...
```

### 2.4 Validation Experiments

#### `experiments/run_contracts.py`

**Dependencies**: contracts, defects, torch, torchvision

```python
def run_with_contracts(defect: DefectSpec) -> DetectionResult:
    """Apply contracts and inject defect, measure detection stage."""
    ...

def run_all_defects(catalog_path: str) -> pd.DataFrame:
    """Run all 200 defect injections with contracts."""
    ...

class DetectionResult:
    defect_id: str
    detected: bool
    detection_stage: str  # "import", "forward", "training", "none"
    execution_time: float
    error_message: str
```

#### `experiments/measure_detection.py`

**Dependencies**: scipy.stats

```python
def calculate_detection_rate(results: pd.DataFrame) -> Dict[str, float]:
    """Calculate detection rate with 95% CI."""
    ...

def hypothesis_test(detection_rate: float, n: int) -> Dict[str, Any]:
    """Test H0: detection ≤60% vs H1: detection ≥80%."""
    ...

def compute_confidence_interval(p: float, n: int) -> Tuple[float, float]:
    """Compute 95% Wilson score interval."""
    ...
```

#### `experiments/measure_false_positives.py`

**Dependencies**: contracts, torch, torchvision

```python
def run_on_valid_batches(n_batches: int = 1000) -> pd.DataFrame:
    """Run contracts on valid CIFAR-10 batches, measure false positives."""
    ...

def calculate_fp_rate(results: pd.DataFrame) -> float:
    """Calculate false positive rate."""
    ...
```

---

## 3. Data Flow

### 3.1 Import-Time Validation Flow

```
1. User imports module with decorated function
   ↓
2. Decorator initialization (@validate_structural)
   ↓
3. Cache lookup (ProbeCache.get)
   ├─ Hit → Skip probe, return cached result
   └─ Miss → Continue to step 4
   ↓
4. Generate sample inputs (ShapeProbe.generate_sample)
   ↓
5. Execute probe (call function with sample inputs)
   ↓
6. Validate outputs (ShapeProbe.validate, DeviceProbe.check_consistency)
   ├─ Pass → Cache result, continue
   └─ Fail → Raise StructuralContractViolation
   ↓
7. Wrap function with runtime validation (optional)
   ↓
8. Return decorated function
```

### 3.2 Defect Injection Flow

```
1. Load defect catalog (DefectCorpus.load)
   ↓
2. Select defect sample (DefectCorpus.sample)
   ↓
3. Create injector (MonkeyPatchInjector or SourceModificationInjector)
   ↓
4. Inject defect (DefectInjector.inject)
   ↓
5. Import module with contracts (trigger validation flow)
   ├─ Contract detects violation → Log detection at "import" stage
   └─ No detection → Continue to step 6
   ↓
6. Run forward pass (if not detected at import)
   ├─ Error during forward → Log detection at "forward" stage
   └─ No error → Continue to step 7
   ↓
7. Run training loop (if not detected at forward)
   ├─ Error during training → Log detection at "training" stage
   └─ No error → Log as "undetected"
   ↓
8. Rollback defect (DefectInjector.rollback)
   ↓
9. Record result (DetectionResult)
```

### 3.3 Experimental Pipeline Flow

```
Baseline Experiments:
  sanity_check.py → Verify ResNet-18 + CIFAR-10 works
  no_contracts.py → Measure time-to-failure without contracts
  execution_only.py → Measure detection via single forward pass
     ↓
Validation Experiments:
  run_contracts.py → Run 200 defect injections with contracts
     ↓
Analysis:
  measure_detection.py → Calculate detection rate, 95% CI, hypothesis test
  measure_false_positives.py → Measure FP rate on valid batches
     ↓
Gate Decision:
  Detection ≥80% → PASS (proceed to H-M2)
  60% ≤ detection <80% → PIVOT (structural-only scope)
  Detection <60% → FAIL (stop, reassess)
```

---

## 4. Interface Contracts

### 4.1 Decorator API

**User-Facing Interface:**
```python
from contracts import validate_structural
from typing import Annotated
import torch

ImageBatch = Annotated[torch.Tensor, "batch:B channels:3 height:32 width:32"]
Logits = Annotated[torch.Tensor, "batch:B classes:10"]

@validate_structural(
    inputs={"x": ImageBatch},
    outputs={"return": Logits},
    dtype={"x": torch.float32},
    device_consistency=True
)
def forward(x: torch.Tensor) -> torch.Tensor:
    return model(x)
```

**Shape Specification Grammar:**
```
shape_spec := dimension ("," dimension)*
dimension := name ":" value
value := integer | symbolic
symbolic := [A-Z]+
```

**Examples:**
- `"batch:B channels:3 height:32 width:32"` → `(B, 3, 32, 32)` with symbolic batch
- `"batch:32 channels:3 height:32 width:32"` → `(32, 3, 32, 32)` fixed batch
- `"batch:B classes:10"` → `(B, 10)`

### 4.2 Defect Catalog Schema

**JSON Structure:**
```json
{
  "defect_id": "SM-001",
  "category": "shape_mismatch",
  "description": "Wrong channel count in CIFAR-10 transform",
  "injection_method": "monkey_patch",
  "injection_target": "torchvision.transforms.ToTensor",
  "expected_shape": "(B, 3, 32, 32)",
  "actual_shape": "(B, 4, 32, 32)",
  "expected_failure_stage": "forward_pass",
  "jiang_corpus_id": "defect_127",
  "severity": "high"
}
```

**Categories:**
- `shape_mismatch`: Wrong tensor dimensions (50 defects)
- `device_mismatch`: CPU/CUDA inconsistency (50 defects)
- `dtype_mismatch`: int64/float32 incompatibility (50 defects)
- `null_output`: Missing/None return values (50 defects)

### 4.3 Results Schema

**Detection Results CSV:**
```csv
defect_id,category,detected,detection_stage,execution_time,error_message
SM-001,shape_mismatch,True,import,0.42,"Expected shape (B, 3, 32, 32), got (B, 4, 32, 32)"
DM-002,device_mismatch,True,import,0.38,"Device inconsistency: model on cpu, data on cuda"
DT-003,dtype_mismatch,False,none,5.2,""
```

**False Positives CSV:**
```csv
batch_id,false_positive,error_message
0,False,""
1,True,"Expected batch size divisible by 8, got 7"
```

---

## 5. Error Handling Strategy

### 5.1 Contract Violation Exceptions

**Exception Hierarchy:**
```
Exception
└── StructuralContractViolation (base class)
    ├── ShapeViolation
    ├── DeviceViolation
    ├── DtypeViolation
    └── NullOutputViolation
```

**Error Message Format:**
```
StructuralContractViolation: Shape mismatch in forward()
  Parameter: x
  Expected: (B, 3, 32, 32)
  Actual:   (B, 4, 32, 32)
  
  Suggestion: Verify input transform produces 3-channel RGB images.
  Check transforms.ToTensor() configuration.
```

### 5.2 Graceful Degradation

**Cache Failures:**
- If cache read fails → Log warning, run probe anyway
- If cache write fails → Log warning, continue execution

**Probe Failures:**
- If sample generation fails → Skip validation, log warning
- If probe execution crashes → Treat as validation failure (conservative)

**Import-Time vs Runtime:**
- Import-time failures → Raise exception immediately (fail-fast)
- Runtime failures → Optional (controlled by decorator parameter)

---

## 6. Performance Optimizations

### 6.1 Caching Strategy

**Cache Key Computation:**
```python
def compute_cache_key(func: Callable, spec: ValidationSpec) -> str:
    """Generate cache key from function signature + spec hash."""
    func_signature = f"{func.__module__}.{func.__qualname__}"
    spec_hash = hashlib.sha256(json.dumps(spec.to_dict()).encode()).hexdigest()
    pytorch_version = torch.__version__
    return f"{func_signature}:{spec_hash}:{pytorch_version}"
```

**Cache Invalidation:**
- TTL: 24 hours (configurable)
- Automatic invalidation on PyTorch version change
- Manual invalidation via `cache.invalidate("pattern*")`

**Cache Location:**
- Default: `~/.cache/structural_contracts/probes/`
- Configurable via environment variable `STRUCTURAL_CONTRACTS_CACHE_DIR`

### 6.2 Probe Execution Overhead

**Target Breakdown:**
- Decorator initialization: <100ms
- Cache lookup: <50ms
- Sample generation: <200ms
- Probe execution: <500ms
- Cache write: <50ms
- **Total per decorator: <1s**

**Optimization Techniques:**
- Use smallest possible sample batch (batch_size=1)
- Skip probe for functions without tensor inputs/outputs
- Reuse sample tensors across probes when shapes match
- Execute probes in parallel for independent functions (future optimization)

### 6.3 Memory Footprint

**Probe Memory Budget:**
- Sample tensor: ~10KB (1, 3, 32, 32) @ float32
- Metadata: ~1KB
- Cache entry: ~11KB
- **Total per function: <20KB**

**Memory Cleanup:**
- Delete sample tensors immediately after probe execution
- Cache uses LRU eviction (max 1000 entries)
- Automatic cleanup on process exit

---

## 7. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Contract Library Core | Implement decorator, shape/dtype/device probes, caching | 16 | Module(4) + Deps(4) + Algo(4) + Integ(4) |
| A-2 | Defect Corpus Preparation | Filter Jiang et al. corpus, create catalog.json, implement injectors | 14 | Module(3) + Deps(3) + Algo(4) + Integ(4) |
| A-3 | Baseline Experiments | Implement sanity check, no-contract, execution-only baselines | 12 | Module(3) + Deps(2) + Algo(3) + Integ(4) |
| A-4 | Contract Validation | Implement run_contracts.py, detection measurement, FP measurement | 15 | Module(4) + Deps(3) + Algo(4) + Integ(4) |
| A-5 | Statistical Analysis | Implement detection rate calculation, 95% CI, hypothesis test | 11 | Module(2) + Deps(2) + Algo(4) + Integ(3) |
| A-6 | Error Message System | Implement actionable error formatting with suggestions | 9 | Module(2) + Deps(1) + Algo(3) + Integ(3) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-1, A-2, A-4], Medium(9-13): [A-3, A-5, A-6], Low(4-8): []

**Complexity Scoring:**
- Module_Size: 1 (single function) to 5 (multiple classes with complex state)
- Dependencies: 1 (stdlib only) to 5 (external + internal + PyTorch)
- Algorithm: 1 (trivial) to 5 (statistical tests, AST manipulation)
- Integration: 1 (isolated) to 5 (cross-module coordination)

---

## 8. Non-Functional Requirements Mapping

### 8.1 Performance (NFR-1, NFR-2)

**Implementation:**
- Caching reduces overhead to <1s on subsequent imports (NFR-1)
- Sample generation uses minimal batch size (1) to limit memory (NFR-2)
- Cache size limit: 1000 entries × 11KB = 11MB < 100MB (NFR-2)

**Validation:**
- Measure execution time in `experiments/run_contracts.py`
- Log memory usage via `torch.cuda.memory_allocated()`

### 8.2 Reliability (NFR-3, NFR-4)

**Implementation:**
- Fixed random seed in `defects/corpus.py` (NFR-3)
- Custom exception classes with actionable messages (NFR-4)
- Suggestion engine in `contracts/exceptions.py` (NFR-4)

**Validation:**
- Run experiments 3 times with same seed, verify identical results (NFR-3)
- Manual review of 20 error messages for actionability (NFR-4)

### 8.3 Maintainability (NFR-5, NFR-6)

**Implementation:**
- Directory structure matches experiment brief (NFR-5)
- All public APIs include docstrings with examples (NFR-6)
- `defects/README.md` documents injection procedure (NFR-6)

**Validation:**
- Code review against PEP 8 (NFR-5)
- Documentation coverage >90% (NFR-6)

### 8.4 Reproducibility (NFR-7, NFR-8)

**Implementation:**
- `requirements.txt` with pinned versions (NFR-7)
- Random seed control in all scripts (NFR-8)
- Environment variable for cache directory (NFR-7)

**Validation:**
- Run experiments on fresh environment (NFR-7)
- Verify identical results across machines (NFR-8)

---

## 9. Technology Integration

### 9.1 PyTorch Integration

**Dynamic Shapes:**
```python
import torch
from torch import _dynamo

# Mark batch dimension as dynamic
@validate_structural(inputs={"x": "batch:B channels:3 height:32 width:32"})
def forward(x):
    _dynamo.mark_dynamic(x, 0)  # Batch dimension is dynamic
    return model(x)
```

**Device Handling:**
```python
# Automatically detect device from tensor
device = x.device
sample = torch.randn(1, 3, 32, 32, device=device, dtype=torch.float32)
```

### 9.2 torchvision Integration

**Dataset Loading:**
```python
from torchvision.datasets import CIFAR10
from torchvision.transforms import ToTensor

dataset = CIFAR10(root="~/.cache/torch/datasets", train=False, download=True, transform=ToTensor())
```

**Model Loading:**
```python
from torchvision.models import resnet18

model = resnet18(pretrained=True)
model.fc = torch.nn.Linear(512, 10)  # Adapt for CIFAR-10
```

### 9.3 Defect Injection Integration

**Monkey-Patching Example:**
```python
import torchvision.transforms as T

# Inject shape mismatch defect
original_to_tensor = T.ToTensor()

def defect_to_tensor(img):
    tensor = original_to_tensor(img)  # (3, 32, 32)
    return torch.cat([tensor, torch.ones(1, 32, 32)], dim=0)  # (4, 32, 32)

T.ToTensor = lambda: defect_to_tensor
```

---

## 10. Validation Strategy

### 10.1 Unit Tests

**Test Coverage:**
- Shape validation: Test symbolic/fixed dimensions, edge cases
- Device validation: Test CPU/CUDA mismatches
- Dtype validation: Test int64/float32 mismatches
- Null check: Test None returns, missing dict keys
- Cache: Test hit/miss, invalidation

**Test Framework:** pytest

### 10.2 Integration Tests

**Test Scenarios:**
- Full pipeline: Defect injection → Contract validation → Detection
- Baseline comparison: No-contract vs contracts detection rates
- False positives: Run on 100 valid batches

### 10.3 Acceptance Tests

**Gate Criteria:**
- Detection rate ≥80% (95% CI lower bound >75%)
- Execution time ≤10s
- False positive rate <5%
- All 200 defects tested

---

## 11. Risk Mitigation

### 11.1 Technical Risks

**Risk: Decorator overhead >10s**
- Mitigation: Aggressive caching, minimal sample size
- Fallback: Reduce probe coverage to critical layers only

**Risk: Symbolic batch dimensions cause false positives**
- Mitigation: Use PyTorch 2.x `mark_dynamic`
- Fallback: Restrict to fixed batch sizes

**Risk: Jiang corpus has <200 structural defects**
- Mitigation: Supplement with synthetic defects (documented separately)
- Fallback: Reduce sample size, adjust statistical power

### 11.2 Evaluation Risks

**Risk: Cherry-picking defects inflates detection rate**
- Mitigation: Blinded selection - use ALL structural defects
- Validation: Document defect selection criteria in `defects/README.md`

**Risk: CIFAR-10 too simple, contracts overfit**
- Mitigation: Include ImageNet samples in FP test
- Validation: Test on 100 ImageNet samples (224×224)

---

## 12. Appendices

### A. Example Contract Application

```python
from contracts import validate_structural
from typing import Annotated
import torch
import torch.nn as nn
from torchvision.models import resnet18

# Type aliases
ImageBatch = Annotated[torch.Tensor, "batch:B channels:3 height:32 width:32"]
Logits = Annotated[torch.Tensor, "batch:B classes:10"]

class ResNetCIFAR(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = resnet18(pretrained=True)
        self.model.fc = nn.Linear(512, 10)
    
    @validate_structural(
        inputs={"x": ImageBatch},
        outputs={"return": Logits},
        dtype={"x": torch.float32},
        device_consistency=True
    )
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)

# Import-time validation
model = ResNetCIFAR()  # Probe executes here
print("Model initialized successfully (contracts passed)")
```

### B. Defect Injection Example

```python
from defects.corpus import DefectCorpus
from defects.injector import MonkeyPatchInjector

# Load defect catalog
corpus = DefectCorpus("defects/catalog.json")
defect = corpus.filter_by_category("shape_mismatch")[0]

# Inject defect
injector = MonkeyPatchInjector(defect)
injector.inject()

# Import module with contracts (will detect defect)
try:
    from models import ResNetCIFAR
    model = ResNetCIFAR()  # Raises ShapeViolation
except ShapeViolation as e:
    print(f"Detected at import: {e}")

# Rollback defect
injector.rollback()
```

### C. Detection Rate Calculation

```python
import pandas as pd
from experiments.measure_detection import calculate_detection_rate

# Load results
results = pd.read_csv("results/detection_rates.csv")

# Calculate detection rate
stats = calculate_detection_rate(results)
print(f"Detection rate: {stats['point_estimate']:.1%}")
print(f"95% CI: [{stats['ci_lower']:.1%}, {stats['ci_upper']:.1%}]")

# Gate decision
if stats['ci_lower'] >= 0.75:
    print("PASS: Proceed to H-M2")
elif stats['point_estimate'] >= 0.60:
    print("PIVOT: Structural-only scope")
else:
    print("FAIL: Reassess contract design")
```

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Steps:** Generate `03_logic.md`, `03_config.md`, then proceed to Phase 4 (Implementation)  
**Expected Timeline:** Phase 3 completion by 2026-07-18 (Week 1)
