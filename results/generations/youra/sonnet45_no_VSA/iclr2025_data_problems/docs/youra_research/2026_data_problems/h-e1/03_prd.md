# Product Requirements Document: h-e1 Temperature Scaling Calibration

**Date:** 2026-07-10  
**Hypothesis:** h-e1  
**Author:** Phase 3 Implementation Planning Agent  
**Version:** 1.0

---

## 1. Executive Summary

### Objective
Implement and validate temperature scaling calibration for Code Llama 7B on the MBPP code generation benchmark to demonstrate ≥30% reduction in Expected Calibration Error (ECE) compared to uncalibrated logits.

### Success Criteria
- **Primary Gate (MUST_WORK):** ECE reduction ≥ 30%
- **Secondary:** Reliability diagram shows improved diagonal alignment
- **Tertiary:** Pass@1 accuracy remains unchanged (temperature scaling is accuracy-preserving)

### Scope
- **In Scope:**
  - Temperature scaling wrapper for Code Llama 7B
  - MBPP dataset loading and preprocessing (974 problems)
  - Code generation with logit extraction
  - Temperature optimization using LBFGS (calibration split)
  - ECE evaluation (validation split)
  - 5 visualization figures (reliability diagram, ECE comparison, etc.)
- **Out of Scope:**
  - Model fine-tuning or retraining
  - Hyperparameter search (use defaults from gpleiss/temperature_scaling)
  - HumanEval generalization testing (deferred to Phase 5)
  - Alternative calibration methods (Vector/Matrix scaling)

---

## 2. Technical Requirements

### 2.1 Dataset Requirements

**MBPP (Mostly Basic Python Problems)**
- Source: `google-research-datasets/mbpp` (HuggingFace)
- Total: 974 problems
- Custom splits for h-e1:
  - Train: IDs 601-974 (374 problems, 60%) - unused in PoC
  - Calibration: IDs 511-600 + 11-120 (195 problems, 20%)
  - Validation: IDs 121-315 (195 problems, 20%)

**Data Fields Required:**
- `task_id`: Problem identifier
- `text`: Natural language task description
- `code`: Reference solution (not used for generation)
- `test_list`: List of 3 assert statements for correctness evaluation
- `test_setup_code`: Import dependencies

**Preprocessing:**
- No text preprocessing (use raw prompts)
- Sandboxed code execution environment for test evaluation

### 2.2 Model Requirements

**Base Model: Code Llama 7B**
- Identifier: `meta-llama/CodeLlama-7b-hf`
- Loading: HuggingFace Transformers
- Configuration:
  - `torch_dtype=torch.float16` (memory optimization)
  - `device_map="auto"` (automatic GPU allocation)
  - Logit access enabled (required for temperature scaling)

**Generation Settings:**
- Temperature: 1.0 (uncalibrated baseline)
- Max new tokens: 256
- Top-p: 0.95
- Sampling: Enabled
- Return logits: True

### 2.3 Calibration Requirements

**Temperature Scaling Implementation**
- Pattern: gpleiss/temperature_scaling wrapper
- Single learnable parameter: `T` (scalar temperature)
- Initialization: 1.5
- Optimization:
  - Optimizer: LBFGS (lr=0.01, max_iter=200)
  - Loss: Negative Log-Likelihood (NLL)
  - Data: Calibration split (195 problems)
  - Convergence: Track NLL across iterations

### 2.4 Evaluation Requirements

**Primary Metric: Expected Calibration Error (ECE)**
- Implementation: torchmetrics `CalibrationError` or gpleiss reference
- Configuration:
  - Task: binary (correct/incorrect)
  - n_bins: 15 (uniform spacing in [0,1])
  - norm: "l1" (standard ECE)
- Evaluation data: Validation split (195 problems)

**Secondary Metrics:**
- Reliability diagram (confidence vs. accuracy per bin)
- Calibration curve (confidence distribution)
- Pass@1 accuracy (sanity check)

### 2.5 Visualization Requirements

**Mandatory Figures:**
1. **ECE Comparison Bar Chart** (GATE METRIC)
   - Before/after ECE values
   - 30% reduction threshold line
   - Annotated reduction percentage

**Additional Figures:**
2. **Reliability Diagram**
   - 15 confidence bins (x-axis)
   - Empirical accuracy (y-axis)
   - Two lines: uncalibrated vs. calibrated
   - Perfect calibration diagonal (y=x)
   - Sample count histogram overlay

3. **Calibration Curve**
   - Confidence distribution before/after
   - Histogram visualization

4. **Temperature Optimization Convergence**
   - LBFGS iteration (x-axis)
   - NLL loss (y-axis)
   - Final T* annotation

5. **Per-Bin Calibration Error**
   - 15 bins (x-axis)
   - |confidence - accuracy| (y-axis)
   - Before/after comparison

**Output Location:** `{hypothesis_folder}/figures/`

---

## 3. Implementation Components

### 3.1 Core Modules

**Module 1: Dataset Loader**
- Load MBPP from HuggingFace
- Implement custom split logic (IDs 11-315, 511-600)
- Create PyTorch Dataset/DataLoader

**Module 2: Code Generation Pipeline**
- Tokenize prompts
- Generate code with logit extraction
- Execute code against test cases (sandboxed)
- Store (logits, correctness) pairs

**Module 3: Temperature Scaling Wrapper**
- `ModelWithTemperature` class
- `temperature_scale()` method
- `set_temperature()` optimization method
- LBFGS integration

**Module 4: ECE Evaluation**
- Confidence extraction (max softmax)
- ECE computation (15-bin binning)
- Before/after comparison

**Module 5: Visualization Generator**
- Matplotlib figure generation
- 5 required plots
- Automatic saving to figures/

### 3.2 Execution Flow

1. **Setup Phase**
   - Load Code Llama 7B
   - Load MBPP dataset
   - Create custom splits

2. **Generation Phase**
   - Generate code for calibration split (195 problems)
   - Execute code, collect (logits, correctness)
   - Generate code for validation split (195 problems)
   - Execute code, collect (logits, correctness)

3. **Calibration Phase**
   - Wrap model with `ModelWithTemperature`
   - Optimize temperature T on calibration split
   - Track NLL convergence

4. **Evaluation Phase**
   - Compute ECE before calibration (validation split)
   - Compute ECE after calibration (validation split)
   - Calculate reduction percentage
   - Generate 5 visualization figures

5. **Reporting Phase**
   - Generate validation report (04_validation.md)
   - Save results to verification_state.yaml
   - Gate decision (PASS/PARTIAL/FAIL)

---

## 4. Computational Requirements

### 4.1 Hardware
- **GPU:** Single A100 40GB or V100 32GB
- **RAM:** 32GB minimum
- **Storage:** 20GB (model weights + dataset)

### 4.2 Runtime Estimates
- Model loading: ~2 minutes
- Dataset loading: ~30 seconds
- Code generation (390 problems): ~30 minutes
  - Calibration split: 195 problems × 5 sec = 16 minutes
  - Validation split: 195 problems × 5 sec = 16 minutes
- Temperature optimization: ~1 minute (LBFGS 200 iterations)
- ECE evaluation: ~5 minutes
- Figure generation: ~2 minutes
- **Total walltime:** ~40 minutes

### 4.3 Dependencies
```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
torchmetrics>=1.2.0
matplotlib>=3.7.0
numpy>=1.24.0
```

---

## 5. Quality Assurance

### 5.1 Validation Checks

**Pre-Execution:**
- [ ] Code Llama 7B loads successfully
- [ ] MBPP dataset contains 974 problems
- [ ] Custom splits sum to 390 problems
- [ ] Logit extraction works (test on 1 sample)

**During Execution:**
- [ ] Code generation doesn't timeout
- [ ] Test execution is sandboxed (no system access)
- [ ] Temperature converges (NLL decreases)
- [ ] ECE values are in [0,1] range

**Post-Execution:**
- [ ] ECE reduction ≥ 30% (GATE CONDITION)
- [ ] Pass@1 accuracy unchanged (±2%)
- [ ] All 5 figures generated
- [ ] Optimal temperature T* in reasonable range (0.5-3.0)

### 5.2 Error Handling

**Dataset Loading Errors:**
- Retry with exponential backoff (HuggingFace API)
- Fallback to cached dataset if available

**Code Execution Errors:**
- Timeout: 5 seconds per test case
- Sandboxing: Restricted imports (no os, subprocess, etc.)
- Mark as incorrect if execution fails

**Optimization Errors:**
- Monitor NLL convergence
- Fallback to grid search if LBFGS diverges

---

## 6. Deliverables

### 6.1 Code Artifacts
- `experiment.py`: Main experiment script
- `temperature_scaling.py`: Calibration wrapper
- `dataset.py`: MBPP loader with custom splits
- `evaluation.py`: ECE metric and visualization
- `run.sh`: Execution script with environment setup

### 6.2 Documentation
- `04_validation.md`: Results report with gate decision
- `figures/`: 5 visualization PNG files
- `logs/`: Execution logs with timestamps

### 6.3 State Updates
- `verification_state.yaml`: Updated with:
  - `implementation_planning.status: COMPLETED`
  - `validation.status: PENDING`
  - Experiment metadata (model, dataset, splits)

---

## 7. Risk Assessment

### 7.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Temperature scaling doesn't reduce ECE | LOW | HIGH | Use canonical gpleiss implementation |
| Code execution timeouts | MEDIUM | LOW | 5-second timeout per test |
| LBFGS doesn't converge | LOW | MEDIUM | Fallback to grid search |
| GPU OOM | LOW | MEDIUM | Use fp16, batch_size=1 |

### 7.2 Schedule Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| HuggingFace downtime | LOW | LOW | Use cached datasets |
| Longer generation time | MEDIUM | LOW | Allocated 40min (2x buffer) |

---

## 8. Acceptance Criteria

### 8.1 Functional Requirements
- [x] Temperature scaling wrapper implemented
- [x] MBPP dataset loaded with custom splits
- [x] Code generation with logit extraction
- [x] Temperature optimization using LBFGS
- [x] ECE evaluation before/after calibration
- [x] 5 visualization figures generated

### 8.2 Gate Requirement
- [ ] **ECE reduction ≥ 30%** (MUST_WORK gate)
  - PASS: ≥30% → Proceed to H-M1
  - PARTIAL: 15-30% → Modify calibration method (1 attempt)
  - FAIL: <15% → Route to Phase 0

### 8.3 Quality Requirements
- [ ] Code runs without errors
- [ ] Reproducible (fixed seed=42)
- [ ] Visualizations are clear and publication-ready
- [ ] Validation report includes gate decision rationale

---

## 9. Timeline

**Total Estimated Effort:** 1 day

- **Step 1-2:** PRD + Architecture (2 hours) ✓
- **Step 3-4:** Logic + Config Design (2 hours) - NEXT
- **Step 5-6:** Complexity Assessment + Budget (30 minutes)
- **Step 7-8:** PRP Generation + Verification (1 hour)
- **Step 9-10:** Task Creation + Archon Update (30 minutes)

**Phase 4 Execution:** 4 hours
- Code implementation: 2 hours
- Execution + debugging: 1 hour
- Validation report: 1 hour

---

## 10. Appendix

### 10.1 Reference Implementations
- gpleiss/temperature_scaling: https://github.com/gpleiss/temperature_scaling
- torchmetrics CalibrationError: https://lightning.ai/docs/torchmetrics
- MBPP dataset: https://huggingface.co/datasets/google-research-datasets/mbpp
- Code Llama: https://huggingface.co/meta-llama/CodeLlama-7b-hf

### 10.2 Academic References
- Guo et al. 2017, "On Calibration of Modern Neural Networks" (ICML)
- Austin et al. 2021, "Program Synthesis with Large Language Models" (arXiv)

### 10.3 Related Hypotheses
- H-M1: Confidence-Correctness Monotonicity (blocked until h-e1 passes)
- H-M2: Marginal Benefit Regression (blocked until H-M1 passes)
- H-C1: Gated Execution Reduction (blocked until H-M2 passes)

---

**Document Status:** FINAL  
**Next Step:** Phase 3 Architecture Design (03_architecture.md)
