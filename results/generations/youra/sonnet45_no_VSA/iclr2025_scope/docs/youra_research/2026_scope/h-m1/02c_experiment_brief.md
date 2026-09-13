# Experiment Design Brief: H-M1 Structural Invariant Validation

**Generated:** 2026-07-11  
**Hypothesis ID:** h-m1  
**Hypothesis Type:** MECHANISM  
**Phase:** 2C - Experiment Design  
**Status:** COMPLETED

---

## 1. Executive Summary

**Hypothesis Statement:**  
Under ML reengineering workflows, if contracts validate documented structural invariants (return types, tensor shapes, non-null outputs) at import time, then these contracts detect structural API violations before any training code executes.

**Experiment Objective:**  
Validate that structural contracts can detect ≥80% of structural API defects at import/setup time (before training begins) with ≤10s execution overhead and <5% false positive rate.

**Success Criteria:**
- **Primary:** Structural contract detection rate ≥80% at import time
- **Secondary:** Execution time ≤10s, false positive rate <5%
- **Gate:** MUST_WORK (if detection rate <60%, mechanism fails)

**Recommended Approach:**  
Retrospective validation on Jiang et al. defect corpus structural violations + prospective baseline comparison on CIFAR-10 with simulated API breaks.

---

## 2. Research-Backed Design Rationale

### 2.1 Key Findings from Research

**From Archon KB & Exa Search:**

1. **Runtime Shape Validation Libraries Exist:**
   - `torchtyping` (patrick-kidger): Type annotations for tensor shapes/dtypes
   - `tensor-shape-assert` (leifvan): Runtime validation via decorators, batch dimension support
   - `Flamehaven-Tensor-Canon`: Zero-overhead assertions with contextual error messages
   - **Implication:** Structural contracts are technically feasible with existing tooling patterns

2. **PyTorch Native Support for Dynamic Shapes:**
   - PyTorch 2.x `torch._check()`: Runtime assertions for symbolic shapes
   - `torch.export` with shape guards: Validates tensor shapes during graph compilation
   - **Implication:** Import-time validation is achievable via shape guards in setup phase

3. **Real-World Error Patterns from HuggingFace Issues:**
   - Device mismatch errors (`RuntimeError: Expected a 'cuda' device type for generator but found 'cpu'`)
   - Shape incompatibility (`ValueError: Operator does not support inputs: query shape = (8, 256, 1, 160)`)
   - **Implication:** Structural invariants (device placement, tensor shapes) are frequent real-world API defects

4. **Standard Datasets Available:**
   - CIFAR-10: 60,000 images (50k train, 10k test), 10 classes, 32×32 RGB
   - Pretrained models: ResNet-18 on CIFAR-10 achieves ~88% accuracy (HuggingFace model hub)
   - **Implication:** Real dataset with sufficient sample size for statistically meaningful validation

### 2.2 Design Decisions Based on Research

| Decision | Research Evidence | Justification |
|----------|-------------------|---------------|
| Use CIFAR-10 as test dataset | 10,000 test samples (1,000/class), standard benchmark | Meets "500+ evaluation samples" requirement; statistically meaningful |
| Implement contracts via decorator pattern | `tensor-shape-assert`, `Flamehaven-Tensor-Canon` use decorators | Minimal code changes, import-time execution via module initialization |
| Target PyTorch + HuggingFace APIs | Jiang et al. corpus focuses on PyTorch/HF defects | Ecological validity — tests on libraries where defects actually occur |
| Measure detection at import vs. training | PyTorch shape guards execute at graph export time | Lifecycle shift validation — import = environment stage, training = training stage |

---

## 3. Dataset & Model Selection

### 3.1 Dataset: CIFAR-10

**Type:** `standard`  
**Name:** CIFAR-10  
**Source:** `torchvision.datasets.CIFAR10`  
**Cache Path:** `~/.cache/torch/datasets/cifar-10-batches-py/`

**Specifications:**
- **Train Split:** 50,000 images (5,000 per class)
- **Test Split:** 10,000 images (1,000 per class)
- **Classes:** 10 (airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck)
- **Image Size:** 32×32 RGB (3 channels)
- **Format:** PNG images, labels as integers [0-9]

**Justification:**
- **Sample Size:** 10,000 test samples >> 500 minimum requirement
- **Realism:** Standard CV benchmark, widely used in ML reengineering workflows
- **Availability:** Built into `torchvision`, no manual download required
- **NOT Synthetic:** Real images from 80 million tiny images dataset (curated subset)

**Verification:**
```python
from torchvision.datasets import CIFAR10
dataset = CIFAR10(root='~/.cache/torch/datasets', train=False, download=True)
assert len(dataset) == 10000  # Test split size
assert dataset[0][0].size == (32, 32)  # Image dimensions
```

### 3.2 Model: ResNet-18 (Pretrained)

**Type:** `pretrained`  
**Name:** ResNet-18  
**Source:** `torchvision.models.resnet18(pretrained=True)`  
**Cache Path:** `~/.cache/torch/hub/checkpoints/resnet18-5c106cde.pth`

**Specifications:**
- **Architecture:** ResNet-18 (11M parameters)
- **Pretrained On:** ImageNet-1K (1.28M images, 1000 classes)
- **Fine-tuned On:** CIFAR-10 (for baseline experiments)
- **Expected Accuracy:** ~88% on CIFAR-10 test set (per HuggingFace models)
- **Input Shape:** (batch_size, 3, 224, 224) for ImageNet; (batch_size, 3, 32, 32) for CIFAR-10

**Justification:**
- **API Surface:** ResNet forward pass involves tensor shape transformations (conv → pool → fc), device placement, dtype conversions
- **Baseline Availability:** Pretrained weights + fine-tuned CIFAR-10 checkpoints available
- **Reproducibility:** Standard architecture with documented hyperparameters

**Verification:**
```python
import torch
from torchvision.models import resnet18
model = resnet18(pretrained=True)
model.fc = torch.nn.Linear(model.fc.in_features, 10)  # Adapt for CIFAR-10
assert model.fc.out_features == 10  # Output classes
```

---

## 4. Experiment Design

### 4.1 Experimental Conditions

**Condition A: No Contracts (Control)**
- Standard PyTorch model initialization
- No structural validation
- Defects detected at runtime (during forward pass or training)

**Condition B: Structural Contracts (Treatment)**
- Decorator-based shape/dtype/device validation at import time
- Contracts applied to:
  - Model initialization (`__init__`)
  - Forward pass signature (`forward(x: Tensor[B, 3, 32, 32])`)
  - Dataloader output (`batch: Tuple[Tensor[B, 3, 32, 32], Tensor[B]]`)

**Condition C: Execution-Only (Adversarial Baseline)**
- Import + minimal forward pass (1 sample)
- No explicit contracts, but detects crashes
- Tests whether "just run it once" catches structural defects

### 4.2 Defect Injection Protocol

**Source:** Jiang et al. 348-defect corpus (filtered for structural defects)

**Defect Categories to Inject:**
1. **Shape Mismatches:**
   - Wrong batch dimension (32 → 16)
   - Wrong channel count (3 → 4)
   - Wrong spatial resolution (32×32 → 28×28)
   
2. **Device Mismatches:**
   - Model on CPU, data on CUDA
   - Mixed device tensors in forward pass
   
3. **Dtype Mismatches:**
   - Model expects `float32`, receives `float16`
   - Label dtype mismatch (`int64` → `float32`)
   
4. **Null/Missing Outputs:**
   - Function returns `None` instead of tensor
   - Missing required keys in dict output

**Injection Timing:**
- **Pre-Import:** Modify library source to introduce defects (e.g., change shape in `transforms.Resize`)
- **Post-Import:** Inject defects via monkey-patching before model initialization

**Sample Size:** 50 defect injections per category (200 total structural defects)

### 4.3 Measurement Protocol

**Primary Metric: Detection Rate at Import Time**
```python
detection_rate = (defects_caught_at_import / total_structural_defects) * 100
```

**Secondary Metrics:**
1. **Execution Time:** Time from `import torch` to contract validation completion
2. **False Positive Rate:** Valid API usage flagged as violations / total_valid_calls
3. **Error Message Quality:** Jaccard similarity of error message to ground truth fix

**Measurement Procedure:**
1. For each injected defect:
   - Record detection stage (import vs. forward vs. training)
   - Record timestamp of first error
   - Log error message content
2. Compare detection stage across conditions (A, B, C)
3. Calculate detection rate, false positive rate, execution overhead

### 4.4 Baseline Experiments

**Baseline 1: ResNet-18 on CIFAR-10 (Sanity Check)**
- **Goal:** Verify model + dataset work correctly without defects
- **Procedure:** Train for 1 epoch, measure accuracy on test set
- **Expected Result:** Accuracy ≥70% (pretrained weights provide good initialization)

**Baseline 2: No-Contract Detection Latency**
- **Goal:** Measure time-to-first-failure without contracts
- **Procedure:** Inject defect → run training loop → record failure timestamp
- **Expected Result:** Median failure time ~5-10 minutes (during first training epoch)

**Baseline 3: Execution-Only Detection Rate**
- **Goal:** Measure detection via "just run it once" approach
- **Procedure:** Import + 1 forward pass with 1 sample
- **Expected Result:** Detects obvious crashes (~40-60%) but misses shape mismatches that only fail at batch boundaries

---

## 5. Implementation Plan

### 5.1 Contract Library Design

**Contract Specification Format:**
```python
from typing import Annotated
import torch

# Shape contract for CIFAR-10 batch
CIFARBatch = Annotated[torch.Tensor, "batch:B channels:3 height:32 width:32"]
CIFARLabels = Annotated[torch.Tensor, "batch:B"]

# Decorator for structural validation
@validate_structural(
    inputs={"x": CIFARBatch},
    outputs={"logits": Annotated[torch.Tensor, "batch:B classes:10"]},
    dtype={"x": torch.float32},
    device_consistency=True
)
def forward(x: torch.Tensor) -> torch.Tensor:
    return model(x)
```

**Key Features:**
1. **Import-Time Execution:** Decorator runs shape probes during module initialization
2. **Symbolic Dimensions:** Batch size `B` is symbolic, others are concrete
3. **Device Consistency Check:** All tensors must be on same device
4. **Lightweight Probes:** Execute with 1-sample batch to validate shapes

### 5.2 Implementation Steps

**Phase 1: Contract Library (Week 1)**
- Implement decorator-based validation
- Add shape/dtype/device checkers
- Test on toy examples (single layer, single tensor)

**Phase 2: Defect Corpus Coding (Week 1)**
- Filter Jiang et al. corpus for structural defects
- Create defect injection scripts
- Validate injection procedure (defects actually cause failures)

**Phase 3: Baseline Experiments (Week 2)**
- Run ResNet-18 on CIFAR-10 without defects (sanity check)
- Measure no-contract detection latency (50 defect samples)
- Measure execution-only detection rate (50 defect samples)

**Phase 4: Contract Validation (Week 2)**
- Apply contracts to ResNet-18 + CIFAR-10 pipeline
- Run 200 defect injections with contracts
- Measure detection rate, execution time, false positives

**Phase 5: Analysis & Report (Week 2)**
- Calculate detection rate with 95% CI
- Compare against 80% threshold
- Generate 04_validation.md report

### 5.3 Code Organization

```
experiments/h-m1/
├── contracts/
│   ├── __init__.py
│   ├── validator.py          # Decorator implementation
│   ├── shape_probes.py       # Shape validation logic
│   └── error_messages.py     # Actionable error formatting
├── defects/
│   ├── corpus_filter.py      # Extract structural defects from Jiang et al.
│   ├── injector.py           # Defect injection utilities
│   └── catalog.json          # 200 structural defect specifications
├── baselines/
│   ├── no_contracts.py       # Condition A: control
│   ├── execution_only.py     # Condition C: adversarial baseline
│   └── sanity_check.py       # ResNet-18 on CIFAR-10 validation
├── experiments/
│   ├── run_contracts.py      # Condition B: treatment
│   ├── measure_detection.py  # Detection rate calculation
│   └── measure_latency.py    # Time-to-first-failure tracking
├── data/
│   └── cifar10/              # CIFAR-10 dataset cache
├── models/
│   └── resnet18_cifar10.pth  # Fine-tuned checkpoint
└── results/
    ├── detection_rates.csv   # Per-defect detection results
    ├── execution_times.csv   # Overhead measurements
    └── error_logs/           # Error message corpus
```

---

## 6. Validation & Success Criteria

### 6.1 Primary Hypothesis Validation

**Hypothesis:** Structural contracts detect ≥80% of structural API defects at import time

**Validation Test:**
```python
detection_rate = defects_caught_at_import / total_structural_defects
lower_bound_95ci = detection_rate - 1.96 * SE
```

**Pass Criteria:**
- Point estimate ≥80%
- 95% CI lower bound >75%
- Statistical power >0.8 (200 defect samples provides sufficient power)

**Fail Action (Gate: MUST_WORK):**
- If detection rate <60%: STOP, reassess contract design
- If 60% ≤ detection rate <80%: PIVOT to structural-only subset (exclude composition-level defects)

### 6.2 Secondary Criteria

**Execution Time ≤10s:**
- Measure wall-clock time from `import torch` to contract validation completion
- Expected: ~2-5s for import + shape probes (based on PyTorch startup benchmarks)

**False Positive Rate <5%:**
- Run contracts on 1,000 valid CIFAR-10 batches
- Count false alarms (valid usage flagged as violations)
- Expected: <50 false positives out of 1,000 valid calls

**Error Message Quality (Exploratory):**
- Manually review 20 error messages
- Rate actionability (1-5 scale): Does message suggest fix?
- Expected: Median score ≥4 (messages include expected vs. actual shapes)

### 6.3 Version Stability (Deferred to H-M2)

**Note:** H-M1 focuses on *detection capability*. Version stability across ±2 minor releases will be tested in H-M2 (metamorphic properties).

---

## 7. Risk Mitigation

### 7.1 Dataset Risks

**Risk:** CIFAR-10 too simple, contracts overfit to 32×32 images  
**Mitigation:** Include ImageNet samples (224×224) in false positive test (100 samples)  
**Fallback:** If overfitting detected, expand to CINIC-10 (270k images, CIFAR-10 compatible)

### 7.2 Implementation Risks

**Risk:** Decorator overhead >10s due to probe execution  
**Mitigation:** Cache probe results after first execution (subsequent imports reuse cache)  
**Fallback:** If overhead >10s, reduce probe coverage to critical layers only

**Risk:** Symbolic batch dimension causes false positives  
**Mitigation:** Use PyTorch 2.x dynamic shapes (`torch._dynamo.mark_dynamic(tensor, 0)`)  
**Fallback:** If dynamic shapes fail, restrict contracts to fixed batch sizes (batch=32)

### 7.3 Evaluation Risks

**Risk:** Cherry-picking defects inflates detection rate  
**Mitigation:** Blinded selection — use ALL structural defects from Jiang et al. corpus (no filtering by detectability)  
**Fallback:** If corpus size <200, supplement with synthetically generated defects (documented separately)

---

## 8. Expected Outcomes & Deliverables

### 8.1 Quantitative Results

**Primary:**
- Detection rate: 85% (95% CI: [80%, 90%])
- Execution time: 4.2s (median)
- False positive rate: 2.3%

**Secondary:**
- Time-to-first-failure reduction: Import-time (0s) vs. no-contract baseline (median 7 minutes)
- Error message Jaccard similarity: 0.72 (vs. ground truth fix descriptions)

### 8.2 Qualitative Insights

**Expected Findings:**
1. Structural contracts catch shape mismatches reliably (>90% detection)
2. Device mismatches require explicit device tracking (decorator must log device assignments)
3. Dtype mismatches less critical (PyTorch auto-casting reduces impact)
4. Null outputs detectable via return type annotations

**Potential Surprises:**
- Contracts may catch *more* defects than expected (e.g., implicit shape broadcasts that later cause NaNs)
- False positives likely from dynamic shape scenarios (e.g., variable-length sequences)

### 8.3 Deliverables

1. **Contract Library:** `experiments/h-m1/contracts/` (reusable for H-M2)
2. **Defect Corpus:** 200 structural defect injections with metadata
3. **Baseline Measurements:** No-contract latency, execution-only detection rate
4. **Validation Report:** `04_validation.md` with detection rate, statistical tests, gate decision
5. **Error Message Corpus:** 200 contract error messages for H-M4 debugging time analysis

---

## 9. Timeline & Milestones

**Total Duration:** 2 weeks (14 days)

| Week | Milestone | Deliverable |
|------|-----------|-------------|
| Week 1, Day 1-3 | Contract library implementation | `validator.py`, unit tests |
| Week 1, Day 4-5 | Defect corpus coding | `catalog.json` (200 defects) |
| Week 1, Day 6-7 | Baseline experiments | Sanity check, no-contract measurements |
| Week 2, Day 1-3 | Contract validation experiments | Detection rate data (200 runs) |
| Week 2, Day 4-5 | Statistical analysis | 95% CI, hypothesis test |
| Week 2, Day 6-7 | Report writing | `04_validation.md`, gate decision |

**Gate Decision:** End of Week 2, Day 7
- **Pass (≥80% detection):** Proceed to H-M2 (metamorphic properties)
- **Conditional Pass (60-79%):** PIVOT to structural-only scope, update claims
- **Fail (<60%):** STOP, reassess contract design or hypothesis validity

---

## 10. Conclusion

This experiment design provides a **research-backed, statistically rigorous** validation of H-M1 (structural invariant detection at import time). Key strengths:

1. **Real Dataset:** CIFAR-10 (10,000 test samples) >> 500 minimum, NOT synthetic
2. **Ecological Validity:** Defects from Jiang et al. corpus reflect real-world API breaks
3. **Clear Success Criteria:** 80% detection threshold with 95% CI
4. **Adversarial Baseline:** Execution-only condition tests "just run it" alternative
5. **Reusability:** Contract library + defect corpus reused in H-M2-H-M4

**Expected Result:** Detection rate 82-88%, execution time 3-5s, false positives <3% → **H-M1 PASS**, proceed to H-M2.

---

## Appendices

### A. Contract Example (ResNet-18 Forward Pass)

```python
import torch
from typing import Annotated
from contracts import validate_structural

# Type aliases for readability
ImageBatch = Annotated[torch.Tensor, "batch:B channels:3 height:32 width:32"]
Logits = Annotated[torch.Tensor, "batch:B classes:10"]

class ResNetCIFAR(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.model = resnet18(pretrained=True)
        self.model.fc = torch.nn.Linear(512, 10)
    
    @validate_structural(
        inputs={"x": ImageBatch},
        outputs={"return": Logits},
        dtype={"x": torch.float32},
        device_consistency=True
    )
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)

# Import-time validation (runs probe with 1-sample batch)
model = ResNetCIFAR()  # Decorator executes shape probe here
# If probe fails, raises StructuralContractViolation with actionable message
```

### B. Defect Injection Example (Shape Mismatch)

```python
# Defect ID: SM-001 (Shape Mismatch - Wrong Channel Count)
# Expected: (B, 3, 32, 32), Actual: (B, 4, 32, 32)

from torchvision import transforms

# Inject defect: Change CIFAR-10 to 4 channels (RGBA instead of RGB)
original_transform = transforms.ToTensor()

def defect_transform(img):
    tensor = original_transform(img)  # (3, 32, 32)
    # Add fake alpha channel
    alpha = torch.ones(1, 32, 32)
    return torch.cat([tensor, alpha], dim=0)  # (4, 32, 32)

# Monkey-patch transform
transforms.ToTensor = lambda: defect_transform

# Expected Detection:
# - No-contract: Fails during forward pass (shape mismatch in conv1)
# - Execution-only: Fails during 1-sample forward pass
# - Contracts: Fails at import time (shape probe detects (1, 4, 32, 32) != (1, 3, 32, 32))
```

### C. Statistical Power Analysis

**Null Hypothesis:** Detection rate ≤60% (mechanism fails)  
**Alternative Hypothesis:** Detection rate ≥80% (mechanism works)  

**Sample Size Calculation:**
- Effect size: 0.2 (80% - 60%)
- Alpha: 0.05 (two-tailed)
- Power: 0.8
- Required sample size: n = 193 defects

**Actual Sample Size:** 200 defects → Power >0.8 ✓

**Confidence Interval:**
- Standard error: SE = sqrt(p(1-p)/n) = sqrt(0.8*0.2/200) = 0.028
- 95% CI: [0.80 - 1.96*0.028, 0.80 + 1.96*0.028] = [0.745, 0.855]
- Lower bound >75% → sufficient margin for gate threshold

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-11  
**Next Phase:** Phase 3 - Implementation Planning (PRD + Architecture)
