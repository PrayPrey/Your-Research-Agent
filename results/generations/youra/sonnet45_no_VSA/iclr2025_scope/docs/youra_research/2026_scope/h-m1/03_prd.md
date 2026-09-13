# Product Requirements Document: H-M1 Structural Contract Validation

**Hypothesis ID:** h-m1  
**Document Type:** PRD (Product Requirements Document)  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11  

---

## 1. Executive Summary

### 1.1 Hypothesis Statement
Under ML reengineering workflows, if contracts validate documented structural invariants (return types, tensor shapes, non-null outputs) at import time, then these contracts detect structural API violations before any training code executes.

### 1.2 Product Goal
Build a contract validation library that detects ≥80% of structural API defects at import/setup time with ≤10s execution overhead and <5% false positive rate, validated through retrospective analysis of real ML defects and prospective baseline comparison.

### 1.3 Success Criteria
- **Primary:** Detection rate ≥80% at import time (95% CI lower bound >75%)
- **Secondary:** Execution time ≤10s, false positive rate <5%
- **Gate:** MUST_WORK - if detection rate <60%, mechanism fails

### 1.4 Target Users
ML researchers and engineers conducting reengineering workflows (model updates, API migrations, dependency upgrades) in PyTorch/HuggingFace ecosystems.

---

## 2. Product Overview

### 2.1 Core Functionality

**Contract Validation Library** providing:

1. **Decorator-based structural validation**
   - Apply to model `__init__`, `forward`, data loaders
   - Validate tensor shapes, dtypes, device placement, non-null outputs
   - Execute probes at import/module initialization time

2. **Defect injection framework**
   - Inject 200 structural defects from Jiang et al. corpus
   - Support shape, device, dtype, null-output violations
   - Enable pre-import and post-import injection modes

3. **Baseline comparison suite**
   - Condition A: No contracts (control)
   - Condition B: Structural contracts (treatment)
   - Condition C: Execution-only validation (adversarial baseline)

4. **Measurement infrastructure**
   - Detection rate calculation (import vs. runtime)
   - Execution time tracking (overhead measurement)
   - False positive rate evaluation
   - Error message quality assessment

### 2.2 Key Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| Contract library | Decorator implementation, shape/dtype/device validation | PyTorch 2.x, `typing.Annotated` |
| Defect corpus | 200 structural defect specifications + injection scripts | Python monkey-patching, source modification |
| Baseline experiments | ResNet-18 + CIFAR-10 sanity check, no-contract measurements | `torchvision`, standard training loop |
| Validation experiments | Contract-enabled runs, detection rate calculation | Contract library + defect injector |
| Analysis pipeline | Statistical tests, 95% CI, gate decision | `scipy.stats`, CSV logging |

### 2.3 Non-Goals (Out of Scope)

- ❌ Version stability across PyTorch releases (deferred to H-M2)
- ❌ Composition-level defects (e.g., incorrect loss function)
- ❌ Production deployment tooling (this is a research validation)
- ❌ GUI/visualization for contract violations
- ❌ Integration with CI/CD pipelines

---

## 3. Functional Requirements

### 3.1 Contract Library

**FR-1: Decorator-based validation**
- **MUST** support `@validate_structural` decorator
- **MUST** accept `inputs`, `outputs`, `dtype`, `device_consistency` parameters
- **MUST** execute shape probes during module initialization (import time)
- **SHOULD** support symbolic batch dimensions (PyTorch dynamic shapes)

**FR-2: Shape validation**
- **MUST** validate concrete dimensions (channels=3, height=32, width=32)
- **MUST** allow symbolic batch dimension (B)
- **MUST** provide actionable error messages with expected vs. actual shapes
- **SHOULD** cache probe results to avoid repeated overhead

**FR-3: Device validation**
- **MUST** check device consistency across tensors in same operation
- **MUST** detect CPU/CUDA mismatches
- **SHOULD** log device assignments for debugging

**FR-4: Dtype validation**
- **MUST** validate tensor dtypes match specifications
- **MUST** detect int64/float32 mismatches
- **SHOULD** warn on implicit casting (not error)

**FR-5: Non-null output validation**
- **MUST** check return values are not `None`
- **MUST** validate required keys in dictionary outputs
- **SHOULD** support optional outputs (annotated with `Optional`)

### 3.2 Defect Injection Framework

**FR-6: Defect corpus**
- **MUST** include 200 structural defects across 4 categories:
  - Shape mismatches (50 defects)
  - Device mismatches (50 defects)
  - Dtype mismatches (50 defects)
  - Null/missing outputs (50 defects)
- **MUST** source defects from Jiang et al. 348-defect corpus (real-world defects)
- **MUST** store defect metadata in `catalog.json` (defect ID, category, injection method, expected failure mode)

**FR-7: Injection modes**
- **MUST** support pre-import injection (modify library source)
- **MUST** support post-import injection (monkey-patching)
- **MUST** preserve original functionality for rollback

**FR-8: Injection validation**
- **MUST** verify injected defect causes failure in no-contract condition
- **SHOULD** log injection success/failure for audit trail

### 3.3 Baseline Experiments

**FR-9: Sanity check (Baseline 1)**
- **MUST** train ResNet-18 on CIFAR-10 for 1 epoch
- **MUST** achieve ≥70% test accuracy (pretrained initialization)
- **MUST** verify dataset loads correctly (10,000 test samples)

**FR-10: No-contract detection (Baseline 2)**
- **MUST** measure time-to-first-failure for 50 defect samples
- **MUST** log failure stage (import, forward, training)
- **MUST** calculate median failure time

**FR-11: Execution-only detection (Baseline 3)**
- **MUST** run import + 1-sample forward pass for 50 defect samples
- **MUST** measure detection rate for "just run it once" approach
- **MUST** compare against contract-based detection

### 3.4 Validation Experiments

**FR-12: Contract-enabled runs**
- **MUST** apply contracts to ResNet-18 model (init, forward)
- **MUST** apply contracts to CIFAR-10 dataloader output
- **MUST** run 200 defect injections with contracts enabled

**FR-13: Detection rate measurement**
- **MUST** record detection stage (import vs. forward vs. training)
- **MUST** calculate detection rate = (defects caught at import / total defects) × 100
- **MUST** compute 95% confidence interval

**FR-14: Execution time measurement**
- **MUST** measure wall-clock time from `import torch` to contract validation completion
- **MUST** verify overhead ≤10s
- **SHOULD** break down overhead (import, probe execution, validation)

**FR-15: False positive measurement**
- **MUST** run contracts on 1,000 valid CIFAR-10 batches
- **MUST** count false alarms (valid usage flagged as violation)
- **MUST** verify false positive rate <5%

### 3.5 Analysis Pipeline

**FR-16: Statistical analysis**
- **MUST** calculate detection rate point estimate
- **MUST** compute 95% confidence interval
- **MUST** perform hypothesis test (H0: detection ≤60%, H1: detection ≥80%)
- **MUST** verify statistical power >0.8

**FR-17: Gate decision**
- **MUST** implement gate logic:
  - Detection ≥80% → PASS (proceed to H-M2)
  - 60% ≤ detection <80% → PIVOT (structural-only scope)
  - Detection <60% → FAIL (stop, reassess)
- **MUST** document decision in `04_validation.md`

**FR-18: Error message quality (exploratory)**
- **SHOULD** manually review 20 error messages
- **SHOULD** rate actionability (1-5 scale)
- **SHOULD** calculate Jaccard similarity to ground truth fixes

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-1: Execution time**
- Import-time validation **MUST** complete within 10s
- Probe execution per decorator **SHOULD** be <1s
- Cache reuse **SHOULD** reduce overhead to <1s on subsequent imports

**NFR-2: Memory footprint**
- Probe execution **SHOULD** use ≤100MB additional memory
- Contract metadata **SHOULD** be <10MB per model

### 4.2 Reliability

**NFR-3: Determinism**
- Defect injection **MUST** be reproducible (fixed random seed)
- Detection results **MUST** be consistent across runs
- Statistical tests **MUST** use same random seed for CI calculation

**NFR-4: Error handling**
- Contract violations **MUST** raise informative exceptions (not generic RuntimeError)
- Exceptions **MUST** include expected vs. actual values
- Exceptions **SHOULD** suggest fixes (e.g., "reshape input to (B, 3, 32, 32)")

### 4.3 Maintainability

**NFR-5: Code organization**
- **MUST** follow directory structure in Section 5.3 of experiment brief
- **MUST** separate contract library, defect injection, baselines, experiments
- **SHOULD** use consistent naming conventions (PEP 8)

**NFR-6: Documentation**
- **MUST** include docstrings for all public APIs
- **MUST** provide usage examples in contract library
- **SHOULD** document defect injection procedure in `defects/README.md`

### 4.4 Reproducibility

**NFR-7: Environment specification**
- **MUST** provide `requirements.txt` with pinned versions
- **MUST** specify Python version (≥3.9)
- **MUST** document PyTorch version (≥2.0)

**NFR-8: Random seed control**
- **MUST** fix random seeds (Python, NumPy, PyTorch)
- **MUST** document seed values in experiment configs

---

## 5. User Workflows

### 5.1 Workflow 1: Apply Contracts to Existing Model

```python
# User imports contract library
from contracts import validate_structural, ImageBatch, Logits

# User applies decorator to existing forward method
class MyModel(nn.Module):
    @validate_structural(
        inputs={"x": ImageBatch},
        outputs={"return": Logits},
        dtype={"x": torch.float32},
        device_consistency=True
    )
    def forward(self, x):
        return self.model(x)

# Import-time validation runs automatically
model = MyModel()  # ← Probe executes here, raises error if violation detected
```

**Expected Outcome:**
- If structural invariants are satisfied → model initializes successfully
- If violation detected → `StructuralContractViolation` exception raised with actionable message

### 5.2 Workflow 2: Run Defect Injection Experiment

```bash
# Step 1: Filter Jiang et al. corpus for structural defects
python defects/corpus_filter.py --input jiang_corpus.json --output catalog.json

# Step 2: Run baseline experiments (no contracts)
python baselines/sanity_check.py  # Verify ResNet-18 + CIFAR-10 works
python baselines/no_contracts.py --defect-catalog catalog.json --output results/no_contracts.csv

# Step 3: Run contract validation experiments
python experiments/run_contracts.py --defect-catalog catalog.json --output results/contracts.csv

# Step 4: Analyze results
python experiments/measure_detection.py --results results/contracts.csv --output results/analysis.json
```

**Expected Outcome:**
- Detection rate ≥80% logged in `results/analysis.json`
- Gate decision written to `04_validation.md`

### 5.3 Workflow 3: Validate False Positive Rate

```bash
# Run contracts on 1,000 valid batches
python experiments/measure_false_positives.py --num-batches 1000 --output results/false_positives.csv
```

**Expected Outcome:**
- False positive count <50 (5% of 1,000 batches)
- Logged in `results/false_positives.csv`

---

## 6. Data Specifications

### 6.1 Dataset: CIFAR-10

| Property | Value |
|----------|-------|
| **Source** | `torchvision.datasets.CIFAR10` |
| **Train Split** | 50,000 images |
| **Test Split** | 10,000 images |
| **Classes** | 10 |
| **Image Size** | 32×32 RGB |
| **Cache Path** | `~/.cache/torch/datasets/cifar-10-batches-py/` |
| **Download** | Automatic via `download=True` |

**Validation:**
```python
dataset = CIFAR10(root='~/.cache/torch/datasets', train=False, download=True)
assert len(dataset) == 10000
assert dataset[0][0].size == (32, 32)
```

### 6.2 Model: ResNet-18

| Property | Value |
|----------|-------|
| **Source** | `torchvision.models.resnet18(pretrained=True)` |
| **Pretrained On** | ImageNet-1K |
| **Parameters** | 11M |
| **Adaptation** | Replace final FC layer (1000 → 10 classes) |
| **Expected Accuracy** | ~88% on CIFAR-10 test set |
| **Cache Path** | `~/.cache/torch/hub/checkpoints/resnet18-5c106cde.pth` |

**Validation:**
```python
model = resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 10)
assert model.fc.out_features == 10
```

---

## 7. Implementation Phases

### Phase 1: Contract Library (Week 1, Days 1-3)

**Deliverables:**
- `contracts/validator.py` - Decorator implementation
- `contracts/shape_probes.py` - Shape validation logic
- `contracts/error_messages.py` - Actionable error formatting
- Unit tests for shape/dtype/device validation

**Acceptance Criteria:**
- Decorator runs probes at import time ✓
- Shape validation supports symbolic batch dimension ✓
- Error messages include expected vs. actual values ✓

### Phase 2: Defect Corpus (Week 1, Days 4-5)

**Deliverables:**
- `defects/corpus_filter.py` - Extract structural defects from Jiang et al.
- `defects/injector.py` - Defect injection utilities
- `defects/catalog.json` - 200 structural defect specifications

**Acceptance Criteria:**
- All 200 defects sourced from real corpus (no synthetic) ✓
- Injection verified (defects cause failures in no-contract mode) ✓

### Phase 3: Baseline Experiments (Week 1, Days 6-7)

**Deliverables:**
- `baselines/sanity_check.py` - ResNet-18 + CIFAR-10 validation
- `baselines/no_contracts.py` - Time-to-first-failure measurements
- `baselines/execution_only.py` - 1-sample forward pass detection

**Acceptance Criteria:**
- Sanity check achieves ≥70% accuracy ✓
- Median failure time logged for no-contract baseline ✓
- Execution-only detection rate measured ✓

### Phase 4: Contract Validation (Week 2, Days 1-3)

**Deliverables:**
- `experiments/run_contracts.py` - Contract-enabled defect injection runs
- `results/detection_rates.csv` - Per-defect detection results
- `results/execution_times.csv` - Overhead measurements

**Acceptance Criteria:**
- All 200 defects tested with contracts ✓
- Detection stage logged (import vs. runtime) ✓
- Execution time ≤10s verified ✓

### Phase 5: Analysis & Report (Week 2, Days 4-7)

**Deliverables:**
- `experiments/measure_detection.py` - Detection rate + 95% CI
- `04_validation.md` - Validation report with gate decision
- `results/analysis.json` - Statistical test results

**Acceptance Criteria:**
- Detection rate point estimate calculated ✓
- 95% CI computed, power verified >0.8 ✓
- Gate decision documented (PASS/PIVOT/FAIL) ✓

---

## 8. Risks & Mitigation

### 8.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Decorator overhead >10s | Violates NFR-1 | Cache probe results, reduce coverage to critical layers |
| Symbolic batch dimensions cause false positives | Violates NFR (FP rate <5%) | Use PyTorch 2.x `mark_dynamic`, fallback to fixed batch size |
| Jiang corpus has <200 structural defects | Insufficient sample size | Supplement with synthetic defects (documented separately) |

### 8.2 Evaluation Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cherry-picking defects inflates detection rate | Invalidates results | Blinded selection - use ALL structural defects from corpus |
| CIFAR-10 too simple, contracts overfit | Limited generalizability | Include ImageNet samples in false positive test |

---

## 9. Acceptance Criteria (Rollup)

### 9.1 Functional Acceptance

- ✅ Contract library detects ≥80% of structural defects at import time
- ✅ Execution time ≤10s
- ✅ False positive rate <5%
- ✅ 200 defect injections completed
- ✅ Baseline experiments completed (sanity check, no-contract, execution-only)
- ✅ Statistical analysis completed (95% CI, hypothesis test)

### 9.2 Quality Acceptance

- ✅ All unit tests pass
- ✅ Error messages include expected vs. actual values
- ✅ Defect injection reproducible (fixed seed)
- ✅ Code follows directory structure
- ✅ Documentation includes usage examples

### 9.3 Deliverable Acceptance

- ✅ `04_validation.md` written with gate decision
- ✅ `contracts/` library reusable for H-M2
- ✅ `defects/catalog.json` contains 200 real-world defects
- ✅ `results/` contains detection rates, execution times, false positives

---

## 10. Open Questions

1. **Q:** Should we include ImageNet samples in false positive test?  
   **A:** YES - include 100 ImageNet samples (224×224) to test generalization

2. **Q:** What if Jiang corpus has <200 structural defects?  
   **A:** Supplement with synthetic defects from HuggingFace GitHub issues (documented in `defects/README.md`)

3. **Q:** Should contracts warn or error on implicit dtype casting?  
   **A:** WARN only (PyTorch auto-casting is intentional in many cases)

4. **Q:** Cache location for probe results?  
   **A:** `~/.cache/structural_contracts/probes/` (cleared on library version change)

---

## 11. Appendices

### A. Contract API Specification

```python
from typing import Annotated, Dict, Any
import torch

def validate_structural(
    inputs: Dict[str, Annotated[torch.Tensor, str]],
    outputs: Dict[str, Annotated[torch.Tensor, str]],
    dtype: Dict[str, torch.dtype] = {},
    device_consistency: bool = False
) -> Callable:
    """
    Decorator for structural validation of PyTorch functions.
    
    Args:
        inputs: Mapping of parameter names to shape annotations
                (e.g., {"x": Annotated[Tensor, "batch:B channels:3 height:32 width:32"]})
        outputs: Mapping of return value names to shape annotations
        dtype: Mapping of parameter names to expected dtypes
        device_consistency: If True, verify all tensors on same device
    
    Raises:
        StructuralContractViolation: If probe detects violation at import time
    
    Example:
        @validate_structural(
            inputs={"x": ImageBatch},
            outputs={"return": Logits},
            dtype={"x": torch.float32},
            device_consistency=True
        )
        def forward(x: torch.Tensor) -> torch.Tensor:
            return model(x)
    """
```

### B. Defect Catalog Schema

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

### C. Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Python | Python | ≥3.9 |
| Deep Learning | PyTorch | ≥2.0 |
| Computer Vision | torchvision | ≥0.15 |
| Type Annotations | typing | stdlib |
| Statistical Analysis | scipy | ≥1.10 |
| Data Handling | pandas | ≥2.0 |
| Testing | pytest | ≥7.0 |

---

**Document Status:** READY FOR ARCHITECTURE DESIGN  
**Next Steps:** Generate `03_architecture.md`, `03_logic.md`, `03_config.md` via specialized agents  
**Expected Timeline:** Phase 3 completion by 2026-07-18 (Week 1)
