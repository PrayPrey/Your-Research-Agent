# Implementation Task List: H-M1 Structural Contract Validation

**Hypothesis ID:** h-m1  
**Phase:** 3 - Implementation Planning  
**Generated:** 2026-07-11  
**Status:** READY FOR PHASE 4  

---

## Task Allocation Summary

| Category | Count | Total Complexity |
|----------|-------|------------------|
| **Epic Tasks** | 6 | 77 |
| **Subtasks** | 21 | 44 |
| **Data Preparation** | 2 | 6 |
| **Environment Setup** | 1 | 2 |
| **Failsafe** | 1 | 3 |
| **TOTAL** | **31** | **132** |

**Complexity Distribution:**
- Epic Tasks: 6 high-complexity tasks (14-16 points each)
- Subtasks: 21 implementation units (1-3 points each)
- Support: 4 setup/data/failsafe tasks (2-6 points each)

---

## Epic Tasks (Architecture-Level)

### A-1: Contract Library Core [Complexity: 16]
**Description:** Implement decorator-based structural validation with shape/dtype/device probes and caching mechanism  
**Dependencies:** None (first task)  
**Breakdown:**
- Module complexity: 4 (multiple classes with state management)
- Dependencies: 4 (PyTorch, typing, diskcache, functools)
- Algorithm: 4 (shape parsing, symbolic unification, probe execution)
- Integration: 4 (cross-module coordination with probes, cache, exceptions)

**Subtasks:**
- L-1: Shape Validation Core [8]
- L-2: Probe Execution Engine [7]
- L-3: Device Consistency Checker [5]
- L-4: Dtype Validation [4]
- L-5: Structural Validator Decorator [9]
- A-6: Error Message System [9] (elevated from subtask)

**Deliverables:**
- `contracts/validator.py`
- `contracts/probes.py`
- `contracts/cache.py`
- `contracts/exceptions.py`
- Unit tests for each module

**Acceptance Criteria:**
- Decorator runs probes at import time ✓
- Shape validation supports symbolic batch dimension ✓
- Device/dtype checks functional ✓
- Caching reduces overhead to <1s on subsequent imports ✓

---

### A-2: Defect Corpus Preparation [Complexity: 14]
**Description:** Filter Jiang et al. 348-defect corpus for structural defects, create catalog.json with 200 defect specifications, implement monkey-patching injectors  
**Dependencies:** None (parallel with A-1)  
**Breakdown:**
- Module complexity: 3 (corpus parser, injector, catalog generator)
- Dependencies: 3 (AST manipulation, JSON, monkey-patching utilities)
- Algorithm: 4 (defect classification, injection logic, AST traversal)
- Integration: 4 (coordinate with baselines and experiments)

**Subtasks:**
- L-6a: Corpus Filter (extract 200 structural defects) [3]
- L-6b: Catalog Generator (create JSON specifications) [2]
- L-6c: Monkey-Patch Injector (post-import injection) [3]
- L-6d: AST Injector (pre-import source modification) [3]

**Deliverables:**
- `defects/corpus.py`
- `defects/injector.py`
- `defects/catalog.json` (200 entries)
- Injection validation script

**Acceptance Criteria:**
- 200 structural defects extracted (50 per category) ✓
- All defects sourced from Jiang et al. corpus (no synthetic) ✓
- Injection verified (defects cause failures in no-contract mode) ✓

---

### A-3: Baseline Experiments [Complexity: 12]
**Description:** Implement three baseline conditions: (1) ResNet-18 + CIFAR-10 sanity check, (2) no-contract time-to-failure, (3) execution-only detection  
**Dependencies:** A-2 (requires defect catalog)  
**Breakdown:**
- Module complexity: 3 (3 separate baseline scripts)
- Dependencies: 2 (PyTorch, torchvision only)
- Algorithm: 3 (training loop, failure detection, timing)
- Integration: 4 (coordinate with validation experiments for comparison)

**Subtasks:**
- B-1: Sanity Check (ResNet-18 on CIFAR-10, 1 epoch) [3]
- B-2: No-Contract Baseline (time-to-failure measurement) [4]
- B-3: Execution-Only Baseline (1-sample forward pass) [3]

**Deliverables:**
- `baselines/sanity_check.py`
- `baselines/no_contracts.py`
- `baselines/execution_only.py`
- `results/baselines/` (sanity check accuracy, time-to-failure stats)

**Acceptance Criteria:**
- Sanity check achieves ≥70% accuracy ✓
- Median failure time logged for 50 defect samples ✓
- Execution-only detection rate measured ✓

---

### A-4: Contract Validation Experiments [Complexity: 15]
**Description:** Apply contracts to ResNet-18 + CIFAR-10, run 200 defect injections, measure detection rate, execution time, false positives  
**Dependencies:** A-1 (contract library), A-2 (defect catalog)  
**Breakdown:**
- Module complexity: 4 (contract application, detection measurement, FP measurement, orchestration)
- Dependencies: 3 (contracts library, defect injector, dataset)
- Algorithm: 4 (detection stage tracking, timing, statistical aggregation)
- Integration: 4 (coordinate with baselines, analysis pipeline)

**Subtasks:**
- V-1: Contract Application (apply to ResNet-18 and dataloader) [3]
- V-2: Detection Measurement (run 200 defect injections) [5]
- V-3: Execution Time Tracking (overhead measurement) [2]
- V-4: False Positive Measurement (1,000 valid batches) [3]

**Deliverables:**
- `experiments/run_contracts.py`
- `experiments/measure_detection.py`
- `experiments/measure_false_positives.py`
- `results/detection_rates.csv` (200 rows)
- `results/execution_times.csv`
- `results/false_positives.csv`

**Acceptance Criteria:**
- All 200 defects tested with contracts ✓
- Detection stage logged (import vs. forward vs. training) ✓
- Execution time ≤10s verified ✓
- False positive rate <5% verified ✓

---

### A-5: Statistical Analysis Pipeline [Complexity: 11]
**Description:** Calculate detection rate with 95% CI, perform hypothesis test (H0: detection ≤60%, H1: detection ≥80%), implement gate decision logic  
**Dependencies:** A-4 (validation results)  
**Breakdown:**
- Module complexity: 2 (analysis script, gate decision script)
- Dependencies: 2 (scipy.stats, pandas)
- Algorithm: 4 (binomial CI, hypothesis test, power analysis)
- Integration: 3 (read CSV results, write 04_validation.md)

**Subtasks:**
- L-7a: Detection Rate Calculation (point estimate + 95% CI) [3]
- L-7b: Hypothesis Test (statistical test + power verification) [3]
- L-7c: Gate Decision Logic (PASS/PIVOT/FAIL) [2]

**Deliverables:**
- `experiments/analyze_results.py`
- `results/analysis.json` (detection rate, CI, p-value, power)
- Gate decision (embedded in analysis.json)

**Acceptance Criteria:**
- Detection rate point estimate calculated ✓
- 95% CI computed with lower bound check ✓
- Statistical power >0.8 verified ✓
- Gate decision logic implemented ✓

---

### A-6: Error Message System [Complexity: 9]
**Description:** Implement actionable error formatting with expected vs. actual values, fix suggestions, and quality assessment  
**Dependencies:** A-1 (contract library exceptions)  
**Breakdown:**
- Module complexity: 2 (exception classes, message formatter)
- Dependencies: 1 (stdlib only)
- Algorithm: 3 (template formatting, suggestion generation)
- Integration: 3 (integrate with all contract validators)

**Subtasks:**
- E-1: Exception Hierarchy (4 violation types) [2]
- E-2: Message Formatter (actionable suggestions) [3]
- E-3: Quality Assessment (Jaccard similarity to ground truth) [2]

**Deliverables:**
- `contracts/exceptions.py` (exception classes)
- `contracts/error_messages.py` (formatting logic)
- `experiments/measure_error_quality.py` (exploratory quality assessment)

**Acceptance Criteria:**
- All exceptions include expected vs. actual values ✓
- Messages suggest fixes (e.g., "reshape input to...") ✓
- Median actionability score ≥4 (manual review of 20 messages) ✓

---

## Subtasks (Logic-Level Implementation Units)

### L-1: Shape Validation Core [Complexity: 8]
**Parent:** A-1  
**Description:** Parse shape specification strings, validate tensor shapes with symbolic batch dimension support, unify symbolic dimensions  
**Files:** `contracts/shape_validator.py`  
**Key Functions:**
- `parse_shape_spec(spec: str) -> List[Union[int, str]]`
- `validate_shape(tensor: Tensor, spec: str, param_name: str) -> Tuple[bool, Optional[str]]`
- `unify_symbolic(symbol: str, value: int) -> bool`

**Acceptance:** Symbolic batch dimension ('B') handled correctly, concrete dimensions validated, error messages include expected vs. actual

---

### L-2: Probe Execution Engine [Complexity: 7]
**Parent:** A-1  
**Description:** Generate 1-sample batches, execute probes at import time, cache results, handle probe failures  
**Files:** `contracts/probes.py`, `contracts/cache.py`  
**Key Functions:**
- `generate_probe_inputs(spec: Dict[str, str]) -> Dict[str, Tensor]`
- `execute_probe(func: Callable, inputs: Dict) -> ProbeResult`
- `cache_probe_result(key: str, result: ProbeResult) -> None`

**Acceptance:** Probes run during module initialization, cache hits reduce overhead to <1s, failures handled gracefully

---

### L-3: Device Consistency Checker [Complexity: 5]
**Parent:** A-1  
**Description:** Check all tensors in operation are on same device, detect CPU/CUDA mismatches  
**Files:** `contracts/device_checker.py`  
**Key Functions:**
- `check_device_consistency(tensors: List[Tensor]) -> Tuple[bool, Optional[str]]`
- `extract_devices(inputs: Dict[str, Any]) -> List[torch.device]`

**Acceptance:** CPU/CUDA mismatches detected, error messages specify which tensor on which device

---

### L-4: Dtype Validation [Complexity: 4]
**Parent:** A-1  
**Description:** Validate tensor dtypes, warn on implicit casting (not error)  
**Files:** `contracts/dtype_validator.py`  
**Key Functions:**
- `validate_dtype(tensor: Tensor, expected: torch.dtype, param_name: str) -> Tuple[bool, Optional[str]]`

**Acceptance:** Dtype mismatches detected, auto-casting warnings emitted (not errors)

---

### L-5: Structural Validator Decorator [Complexity: 9]
**Parent:** A-1  
**Description:** Main `@validate_structural` decorator, orchestrates shape/dtype/device checks, integrates caching  
**Files:** `contracts/validator.py`  
**Key Functions:**
- `validate_structural(inputs, outputs, dtype, device_consistency) -> Callable`

**Acceptance:** Decorator wraps functions correctly, probes execute at import time, all validators invoked

---

### L-6a: Corpus Filter [Complexity: 3]
**Parent:** A-2  
**Description:** Extract 200 structural defects from Jiang et al. 348-defect corpus  
**Files:** `defects/corpus.py`  
**Key Functions:**
- `filter_structural_defects(corpus_path: str) -> List[Defect]`

**Acceptance:** 50 defects per category (shape, device, dtype, null-output), all sourced from real corpus

---

### L-6b: Catalog Generator [Complexity: 2]
**Parent:** A-2  
**Description:** Generate `catalog.json` with defect specifications  
**Files:** `defects/catalog_generator.py`  
**Key Functions:**
- `generate_catalog(defects: List[Defect], output_path: str) -> None`

**Acceptance:** 200 entries in catalog.json, schema matches specification in architecture doc

---

### L-6c: Monkey-Patch Injector [Complexity: 3]
**Parent:** A-2  
**Description:** Post-import injection via monkey-patching  
**Files:** `defects/injector.py`  
**Key Functions:**
- `inject_monkey_patch(target: str, defect_spec: Dict) -> None`

**Acceptance:** Injected defects cause failures in no-contract mode, rollback restores original functionality

---

### L-6d: AST Injector [Complexity: 3]
**Parent:** A-2  
**Description:** Pre-import injection via AST manipulation of library source  
**Files:** `defects/ast_injector.py`  
**Key Functions:**
- `inject_ast_modification(source_path: str, defect_spec: Dict) -> None`

**Acceptance:** Modified source causes failures, original source backed up

---

### B-1: Sanity Check Baseline [Complexity: 3]
**Parent:** A-3  
**Description:** Train ResNet-18 on CIFAR-10 for 1 epoch, verify ≥70% accuracy  
**Files:** `baselines/sanity_check.py`  

**Acceptance:** Accuracy logged, dataset loads correctly (10,000 test samples)

---

### B-2: No-Contract Baseline [Complexity: 4]
**Parent:** A-3  
**Description:** Measure time-to-first-failure for 50 defect samples without contracts  
**Files:** `baselines/no_contracts.py`  

**Acceptance:** Median failure time logged, failure stage tracked (import/forward/training)

---

### B-3: Execution-Only Baseline [Complexity: 3]
**Parent:** A-3  
**Description:** 1-sample forward pass detection rate (adversarial baseline)  
**Files:** `baselines/execution_only.py`  

**Acceptance:** Detection rate measured for 50 samples, compared against contract-based detection

---

### V-1: Contract Application [Complexity: 3]
**Parent:** A-4  
**Description:** Apply contracts to ResNet-18 model and CIFAR-10 dataloader  
**Files:** `experiments/apply_contracts.py`  

**Acceptance:** Contracts applied to `__init__`, `forward`, dataloader output

---

### V-2: Detection Measurement [Complexity: 5]
**Parent:** A-4  
**Description:** Run 200 defect injections with contracts, track detection stage  
**Files:** `experiments/run_contracts.py`  

**Acceptance:** All 200 defects tested, detection stage logged (import vs. runtime)

---

### V-3: Execution Time Tracking [Complexity: 2]
**Parent:** A-4  
**Description:** Measure wall-clock time from import to validation completion  
**Files:** `experiments/measure_latency.py`  

**Acceptance:** Overhead ≤10s verified across 10 runs

---

### V-4: False Positive Measurement [Complexity: 3]
**Parent:** A-4  
**Description:** Run contracts on 1,000 valid CIFAR-10 batches, count false alarms  
**Files:** `experiments/measure_false_positives.py`  

**Acceptance:** False positive count <50 (5% of 1,000)

---

### L-7a: Detection Rate Calculation [Complexity: 3]
**Parent:** A-5  
**Description:** Calculate point estimate and 95% confidence interval  
**Files:** `experiments/analyze_results.py`  

**Acceptance:** Binomial CI computed, lower bound checked against 75% threshold

---

### L-7b: Hypothesis Test [Complexity: 3]
**Parent:** A-5  
**Description:** Statistical test (H0: ≤60%, H1: ≥80%), verify power >0.8  
**Files:** `experiments/statistical_test.py`  

**Acceptance:** p-value calculated, power verified with n=200

---

### L-7c: Gate Decision Logic [Complexity: 2]
**Parent:** A-5  
**Description:** Implement PASS (≥80%) / PIVOT (60-79%) / FAIL (<60%) logic  
**Files:** `experiments/gate_decision.py`  

**Acceptance:** Decision logged in analysis.json, ready for 04_validation.md

---

### E-1: Exception Hierarchy [Complexity: 2]
**Parent:** A-6  
**Description:** Implement 4 exception classes (Shape, Device, Dtype, NullOutput)  
**Files:** `contracts/exceptions.py`  

**Acceptance:** Base class `StructuralContractViolation`, 4 subclasses

---

### E-2: Message Formatter [Complexity: 3]
**Parent:** A-6  
**Description:** Actionable error messages with expected vs. actual values, fix suggestions  
**Files:** `contracts/error_messages.py`  

**Acceptance:** Messages include suggestion (e.g., "Verify input transform...")

---

### E-3: Quality Assessment [Complexity: 2]
**Parent:** A-6  
**Description:** Exploratory quality assessment (Jaccard similarity, manual review)  
**Files:** `experiments/measure_error_quality.py`  

**Acceptance:** 20 messages reviewed, median actionability score ≥4

---

## Data Preparation Tasks

### D-1: CIFAR-10 Dataset Setup [Complexity: 3]
**Description:** Download CIFAR-10, verify 10,000 test samples, cache locally  
**Dependencies:** None  
**Files:** `data/setup_cifar10.py`  

**Acceptance Criteria:**
- Dataset cached at `~/.cache/torch/datasets/cifar-10-batches-py/`
- Verification: `len(test_dataset) == 10000`
- Image size: 32×32 RGB verified

---

### D-2: ResNet-18 Model Setup [Complexity: 3]
**Description:** Download pretrained ResNet-18, adapt for CIFAR-10 (1000 → 10 classes)  
**Dependencies:** None  
**Files:** `data/setup_resnet18.py`  

**Acceptance Criteria:**
- Pretrained weights cached at `~/.cache/torch/hub/checkpoints/resnet18-5c106cde.pth`
- Final FC layer adapted: `model.fc.out_features == 10`
- Model loads successfully

---

## Environment Setup Tasks

### ENV-1: Environment Configuration [Complexity: 2]
**Description:** Create `requirements.txt`, verify Python ≥3.9, PyTorch ≥2.0, set random seeds  
**Dependencies:** None  
**Files:** `requirements.txt`, `setup_env.py`  

**Acceptance Criteria:**
- All dependencies pinned (PyTorch 2.0, torchvision 0.15, scipy 1.10, pandas 2.0, diskcache 5.6)
- Random seeds fixed (Python: 42, NumPy: 42, PyTorch: 42)
- CUDA deterministic mode enabled

---

## Failsafe Tasks

### FAIL-1: Minimal Validation Report Generator [Complexity: 3]
**Description:** If primary pipeline fails, generate minimal validation report with error logs  
**Dependencies:** All other tasks (runs only if experiment fails)  
**Files:** `experiments/generate_minimal_report.py`  

**Acceptance Criteria:**
- If detection rate <60%: Write 04_validation.md with FAIL status
- Include error logs, partial results, failure analysis
- Gate decision: FAIL (reassess contract design or hypothesis)

---

## Task Dependencies Graph

```
D-1, D-2, ENV-1 (parallel - no dependencies)
    ↓
A-1 (contract library) ← depends on ENV-1
A-2 (defect corpus) ← depends on ENV-1
    ↓
A-3 (baselines) ← depends on A-2 (defect catalog)
A-4 (validation) ← depends on A-1, A-2
    ↓
A-5 (analysis) ← depends on A-4
A-6 (error messages) ← depends on A-1
    ↓
FAIL-1 (failsafe) ← depends on A-5 (runs if gate fails)
```

**Critical Path:** ENV-1 → A-1 → A-4 → A-5 (total: 2 + 16 + 15 + 11 = 44 complexity points)

---

## Implementation Budget Allocation

**Total Budget:** 132 complexity points  
**Recommended Distribution:**

| Phase | Days | Target Complexity | Tasks |
|-------|------|-------------------|-------|
| **Week 1, Day 1-3** | 3 days | 35 points | ENV-1, D-1, D-2, A-1 (contract library) |
| **Week 1, Day 4-5** | 2 days | 23 points | A-2 (defect corpus), A-6 (error messages) |
| **Week 1, Day 6-7** | 2 days | 12 points | A-3 (baselines) |
| **Week 2, Day 1-3** | 3 days | 15 points | A-4 (validation experiments) |
| **Week 2, Day 4-5** | 2 days | 11 points | A-5 (statistical analysis) |
| **Week 2, Day 6-7** | 2 days | 3 points | FAIL-1 (failsafe), report writing, buffer |

**Daily Velocity:** ~9-12 complexity points/day (assumes 1 developer)

---

## Verification Checklist (Phase 3 → Phase 4 Handoff)

**Design Documents:**
- ✅ PRD written (`03_prd.md`)
- ✅ Architecture written (`03_architecture.md`)
- ✅ Logic written (`03_logic.md`)
- ✅ Configuration written (`03_config.md`)

**Task List:**
- ✅ Epic tasks defined (6 tasks, 77 total complexity)
- ✅ Subtasks defined (21 tasks, 44 total complexity)
- ✅ Data/environment/failsafe tasks defined (4 tasks, 11 total complexity)
- ✅ Dependencies mapped
- ✅ Critical path identified

**Budget:**
- ✅ Total complexity calculated (132 points)
- ✅ Budget allocation by week/day
- ✅ Velocity estimated (9-12 points/day)

**Archon Integration:**
- 🔲 Archon project initialized (deferred to pipeline orchestrator)
- 🔲 Documents uploaded to Archon (deferred to pipeline orchestrator)
- 🔲 Epic tasks created in Archon (deferred to pipeline orchestrator)

**Status:** ✅ READY FOR PHASE 4 (Coding + Validation)

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-11  
**Next Phase:** Phase 4 - Coding (Coder-Validator Loop)
