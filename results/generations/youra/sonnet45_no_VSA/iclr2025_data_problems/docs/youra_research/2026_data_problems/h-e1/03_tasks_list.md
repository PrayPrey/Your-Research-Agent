# Implementation Task List: h-e1

**Generated:** 2026-07-11  
**Hypothesis:** h-e1 - Temperature Scaling Calibration  
**Total Tasks:** 21  
**Total Complexity:** 45

---

## Epic 1: Dataset + Model Setup (Complexity: 8)

### E1.1 - Load MBPP Dataset
- **Description:** Load google-research-datasets/mbpp from HuggingFace with retry logic
- **Effort:** 15 minutes
- **Complexity:** 2
- **Dependencies:** None
- **Deliverable:** Loaded dataset with 974 problems verified

### E1.2 - Implement Custom Splits
- **Description:** Create calibration (195) and validation (195) splits from specific ID ranges
- **Effort:** 15 minutes
- **Complexity:** 2
- **Dependencies:** E1.1
- **Deliverable:** Two DataLoader objects with correct sample counts

### E1.3 - Create PyTorch Dataset Wrapper
- **Description:** Implement MBPPDataset class returning (task_id, text, test_list, test_setup_code)
- **Effort:** 10 minutes
- **Complexity:** 2
- **Dependencies:** E1.2
- **Deliverable:** MBPPDataset class with __getitem__ and __len__

### E1.4 - Load Code Llama 7B
- **Description:** Load meta-llama/CodeLlama-7b-hf with fp16 and auto device mapping
- **Effort:** 10 minutes
- **Complexity:** 2
- **Dependencies:** None
- **Deliverable:** Loaded model with logit access verified

---

## Epic 2: Generation Pipeline (Complexity: 10)

### E2.1 - Implement Logit Extraction
- **Description:** Modify generation to extract logits using output_scores=True
- **Effort:** 20 minutes
- **Complexity:** 3
- **Dependencies:** E1.4
- **Deliverable:** generate_with_logits() function returning (code, logits)

### E2.2 - Code Generation Loop
- **Description:** Generate code for all problems with tokenization and configured settings
- **Effort:** 20 minutes
- **Complexity:** 3
- **Dependencies:** E2.1, E1.3
- **Deliverable:** Generation loop with progress tracking

### E2.3 - Batch Processing
- **Description:** Iterate over calibration (195) and validation (195) splits
- **Effort:** 10 minutes
- **Complexity:** 2
- **Dependencies:** E2.2
- **Deliverable:** Batch processing with tqdm progress bars

### E2.4 - Logit Caching
- **Description:** Save generated code and logits to disk to avoid re-generation
- **Effort:** 5 minutes
- **Complexity:** 2
- **Dependencies:** E2.3
- **Deliverable:** Cached results in {task_id: {code, logits}} format

---

## Epic 3: Code Execution (Complexity: 9)

### E3.1 - Sandboxed Execution Environment
- **Description:** Implement CodeExecutor with subprocess and import restrictions
- **Effort:** 20 minutes
- **Complexity:** 3
- **Dependencies:** None
- **Deliverable:** CodeExecutor class with execute() method

### E3.2 - Test Case Execution
- **Description:** Execute test_list assertions with test_setup_code injection
- **Effort:** 20 minutes
- **Complexity:** 3
- **Dependencies:** E3.1, E2.4
- **Deliverable:** Test execution returning binary correctness (all pass = 1)

### E3.3 - Timeout Handling
- **Description:** Implement 5-second timeout per test with failure marking
- **Effort:** 5 minutes
- **Complexity:** 2
- **Dependencies:** E3.2
- **Deliverable:** Timeout handling with logged events

### E3.4 - Correctness Labeling
- **Description:** Collect (task_id, logits, correctness) tuples for ECE evaluation
- **Effort:** 5 minutes
- **Complexity:** 1
- **Dependencies:** E3.3
- **Deliverable:** Labeled dataset for calibration and validation splits

---

## Epic 4: Temperature Calibration (Complexity: 7)

### E4.1 - ModelWithTemperature Wrapper
- **Description:** Implement temperature scaling wrapper following gpleiss pattern
- **Effort:** 15 minutes
- **Complexity:** 2
- **Dependencies:** E1.4
- **Deliverable:** ModelWithTemperature class with temperature_scale() method

### E4.2 - LBFGS Optimization
- **Description:** Implement set_temperature() with LBFGS (lr=0.01, max_iter=200)
- **Effort:** 20 minutes
- **Complexity:** 2
- **Dependencies:** E4.1, E3.4
- **Deliverable:** Optimized temperature parameter T*

### E4.3 - Convergence Tracking
- **Description:** Track NLL loss per iteration for visualization
- **Effort:** 5 minutes
- **Complexity:** 2
- **Dependencies:** E4.2
- **Deliverable:** Loss history for convergence plot

### E4.4 - Grid Search Fallback
- **Description:** Fallback to grid search if LBFGS diverges
- **Effort:** 10 minutes
- **Complexity:** 1
- **Dependencies:** E4.2
- **Deliverable:** Grid search over [0.5, 0.8, 1.0, 1.5, 2.0, 3.0] if needed

---

## Epic 5: ECE Evaluation + Figures (Complexity: 11)

### E5.1 - Confidence Extraction
- **Description:** Extract max softmax confidence before/after temperature scaling
- **Effort:** 10 minutes
- **Complexity:** 2
- **Dependencies:** E4.2, E3.4
- **Deliverable:** Confidence arrays for uncalibrated and calibrated models

### E5.2 - ECE Computation
- **Description:** Implement 15-bin ECE with uniform binning
- **Effort:** 15 minutes
- **Complexity:** 2
- **Dependencies:** E5.1
- **Deliverable:** ECE values before/after calibration

### E5.3 - Figure 1: ECE Comparison (MANDATORY)
- **Description:** Bar chart with ECE before/after and 30% threshold line
- **Effort:** 10 minutes
- **Complexity:** 2
- **Dependencies:** E5.2
- **Deliverable:** figures/01_ece_comparison.png

### E5.4 - Figure 2: Reliability Diagram
- **Description:** Confidence vs. accuracy plot with diagonal reference
- **Effort:** 15 minutes
- **Complexity:** 2
- **Dependencies:** E5.2
- **Deliverable:** figures/02_reliability_diagram.png

### E5.5 - Figures 3-5: Additional Visualizations
- **Description:** Calibration curve, convergence plot, per-bin error
- **Effort:** 20 minutes
- **Complexity:** 3
- **Dependencies:** E5.2, E4.3
- **Deliverable:** figures/03-05.png (3 additional plots)

---

## Task Dependency Graph

```
E1.1 (MBPP Load) → E1.2 (Splits) → E1.3 (Dataset)
                                      ↓
E1.4 (Code Llama) → E2.1 (Logits) → E2.2 (Gen Loop) → E2.3 (Batch) → E2.4 (Cache)
                      ↓                                                  ↓
                    E4.1 (Wrapper) → E4.2 (LBFGS) → E4.3 (Track)      E3.1 (Sandbox)
                                         ↓             ↓                   ↓
                                       E4.4         E5.5 (Fig4)       E3.2 (Tests)
                                                                          ↓
                                                                       E3.3 (Timeout)
                                                                          ↓
                                                                       E3.4 (Labels)
                                                                          ↓
                                        E5.1 (Confidence) ← ← ← ← ← ← ← ← 
                                          ↓
                                        E5.2 (ECE)
                                          ↓
                                    E5.3, E5.4 (Figs 1-2)
```

---

## Execution Order Recommendation

**Phase A: Setup (parallel)**
- E1.1, E1.4 (dataset + model loading)

**Phase B: Preparation (sequential)**
- E1.2 → E1.3 (splits + wrapper)
- E2.1 (logit extraction)

**Phase C: Generation (sequential)**
- E2.2 → E2.3 → E2.4 (generation + caching)

**Phase D: Execution (sequential)**
- E3.1 → E3.2 → E3.3 → E3.4 (sandbox + tests + labels)

**Phase E: Calibration (sequential)**
- E4.1 → E4.2 → E4.3 (wrapper + optimization + tracking)
- E4.4 (fallback, conditional)

**Phase F: Evaluation (sequential)**
- E5.1 → E5.2 (confidence + ECE)
- E5.3, E5.4, E5.5 (all figures, can parallelize)

**Total Sequential Path:** ~4.6 hours (includes 10% buffer)

---

## Complexity Distribution

| Level | Range | Tasks | Total Complexity |
|-------|-------|-------|------------------|
| Low | 1-2 | 16 tasks | 30 |
| Medium | 3 | 5 tasks | 15 |
| High | 4-5 | 0 tasks | 0 |

**Note:** PoC scope keeps all tasks in Low-Medium range (no complex tasks).

---

## Quality Gates

### After Epic 1 (Setup)
- ✅ MBPP dataset has 974 problems
- ✅ Custom splits have exactly 195 samples each
- ✅ Code Llama loads in <2 minutes
- ✅ Single test generation produces logits

### After Epic 2 (Generation)
- ✅ All 390 problems generated (195 cal + 195 val)
- ✅ Logits cached to disk
- ✅ No OOM errors

### After Epic 3 (Execution)
- ✅ All 390 problems executed (with timeouts handled)
- ✅ Correctness labels are binary (0 or 1)
- ✅ No sandbox escapes logged

### After Epic 4 (Calibration)
- ✅ Temperature T* in range [0.5, 3.0]
- ✅ NLL decreases (convergence confirmed)
- ✅ Grid search not triggered (LBFGS succeeded)

### After Epic 5 (Evaluation)
- ✅ ECE values in [0, 1] range
- ✅ All 5 figures generated (PNG, 300 DPI)
- ✅ Gate decision computed (PASS/PARTIAL/FAIL)

---

**Document Status:** FINAL  
**Ready for Phase 4:** YES  
**Next Step:** Execute with validator-agent (Phase 4 implementation + validation)
