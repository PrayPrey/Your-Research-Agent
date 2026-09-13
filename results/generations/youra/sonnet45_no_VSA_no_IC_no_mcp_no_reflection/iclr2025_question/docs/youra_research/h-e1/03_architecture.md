# System Architecture: h-e1
## Token Entropy Extraction for Prediction Correctness Correlation

**Date:** 2026-08-28  
**Hypothesis:** h-e1 (EXISTENCE)  
**Budget Tier:** LIGHT (4-8 Epic tasks, ≤15 total)

---

## Codebase Analysis (Serena)

*MCP unavailable — manual design patterns applied*

**Existing Patterns:**
- Standard PyTorch project structure
- HuggingFace model loading patterns
- Metrics-based evaluation loops

**Applied Patterns:**
- Applied: `entropy_computation_pattern` — Shannon entropy over softmax distributions
- Applied: `llm_inference_loop` — Frozen model forward pass with logits extraction
- Applied: `correlation_analysis_pattern` — SciPy-based statistical testing

---

## System Overview

### Purpose
Validate infrastructure for entropy-based uncertainty quantification in frozen LLMs through single-forward-pass token distribution analysis.

### Scope
Proof-of-concept implementation with minimal infrastructure:
- Dataset loading (TriviaQA subset)
- Model inference (Llama-2-7B frozen)
- Entropy computation from logits
- Correlation analysis (Spearman)
- Validation report generation

### Architecture Style
**Monolithic Script** — Single-file or flat module structure suitable for PoC experiments.

**Rationale:** EXISTENCE hypothesis requires minimal abstraction. Over-engineering premature for infrastructure validation.

---

## Module Structure

### Core Modules

#### 1. Data Module (`data.py`)
**Purpose:** Dataset loading and preprocessing  
**Dependencies:** HuggingFace datasets  
**Exports:**
- `load_triviaqa_subset() -> Dataset`
- `prepare_example(example: dict) -> tuple[str, str]`

**Complexity:** LOW (standard dataset loading)

---

#### 2. Model Module (`model.py`)
**Purpose:** LLM loading and inference  
**Dependencies:** HuggingFace transformers, PyTorch  
**Exports:**
- `load_llama_model() -> tuple[AutoModelForCausalLM, AutoTokenizer]`
- `forward_pass(model, tokenizer, question: str) -> dict`
  - Returns: `{"logits": Tensor, "pred_id": int, "pred_text": str}`

**Complexity:** LOW (frozen model, no training)

---

#### 3. Metrics Module (`metrics.py`)
**Purpose:** Entropy computation and analysis  
**Dependencies:** PyTorch, SciPy, NumPy  
**Exports:**
- `compute_entropy(logits: Tensor) -> float`
- `compute_spearman(entropies: list, correctness: list) -> tuple[float, float]`
- `extraction_rate(entropies: list) -> float`
- `quadrant_analysis(max_probs: list, entropies: list) -> dict`

**Complexity:** MEDIUM (statistical analysis)

---

#### 4. Visualization Module (`visualization.py`)
**Purpose:** Figure generation for validation report  
**Dependencies:** matplotlib/seaborn  
**Exports:**
- `plot_gate_metrics(metrics: dict, output_path: str)`
- `plot_scatter(entropies, correctness, output_path: str)`
- `plot_histograms(entropies_correct, entropies_incorrect, output_path: str)`
- `plot_quadrant(max_probs, entropies, correctness, output_path: str)`

**Complexity:** LOW (standard plotting)

---

#### 5. Experiment Runner (`main.py`)
**Purpose:** Orchestrate end-to-end experiment  
**Dependencies:** All above modules  
**Flow:**
1. Load dataset and model
2. Inference loop (sequential)
3. Collect entropy and correctness
4. Compute metrics
5. Generate figures
6. Write validation report

**Complexity:** MEDIUM (orchestration logic)

---

## File Organization

```
h-e1/
├── 02c_experiment_brief.md        # Input (Phase 2C)
├── 03_prd.md                      # Input (Step 2)
├── 03_architecture.md             # This document (Step 3)
├── 03_logic.md                    # TBD (Step 5)
├── 03_config.md                   # TBD (Step 5)
├── 03_tasks.yaml                  # TBD (Step 9)
├── code/
│   ├── requirements.txt           # Dependencies
│   ├── data.py                    # Dataset loading
│   ├── model.py                   # LLM inference
│   ├── metrics.py                 # Entropy + correlation
│   ├── visualization.py           # Plotting
│   └── main.py                    # Experiment runner
├── figures/                       # Generated plots
│   ├── gate_metrics.png
│   ├── scatter.png
│   ├── histograms.png
│   └── quadrant.png
└── 04_validation.md               # Output (Phase 4)
```

---

## Data Flow

```
TriviaQA
  ↓
[Dataset Loader]
  ↓
{question, answer}
  ↓
[Model Inference] → logits, prediction
  ↓
[Entropy Computation] → entropy value
  ↓
[Correctness Check] → binary label
  ↓
[Accumulate] → (entropies[], correctness[])
  ↓
[Correlation Analysis] → Spearman ρ, p-value
  ↓
[Quadrant Analysis] → Q3 population
  ↓
[Visualization] → 4 figures
  ↓
04_validation.md
```

---

## Epic Tasks (Architecture Phase)

### Epic-1: Environment Setup and Data Pipeline
**Priority:** P0  
**Description:** Configure Python environment, install dependencies, verify GPU availability, load dataset and model into cache.

**Subtasks (estimated):**
1. Create virtual environment and install requirements
2. Verify CUDA availability (optional)
3. Download TriviaQA dataset to cache
4. Download Llama-2-7B model to cache
5. Verify dataset and model loading

**Complexity Score:** 3/20
- Module Size: 1 (minimal setup scripts)
- Dependencies: 1 (standard libraries)
- Algorithm: 0 (download/verify only)
- Integration: 1 (cache paths)

**Estimated Effort:** 1-2 hours

---

### Epic-2: Core Inference Pipeline
**Priority:** P0  
**Description:** Implement frozen model inference with logits extraction, entropy computation, and prediction generation.

**Subtasks (estimated):**
1. Implement model loading wrapper
2. Implement forward pass with logits extraction
3. Implement softmax + Shannon entropy
4. Implement prediction decoding
5. Unit test entropy computation on toy distributions

**Complexity Score:** 5/20
- Module Size: 2 (model.py + metrics.py)
- Dependencies: 1 (PyTorch, transformers)
- Algorithm: 1 (numerical stability in entropy)
- Integration: 1 (tokenizer + model coordination)

**Estimated Effort:** 2-3 hours

---

### Epic-3: Correctness Evaluation and Data Collection
**Priority:** P0  
**Description:** Implement exact-match correctness check, main experiment loop collecting (entropy, correctness) pairs across 1,000 examples.

**Subtasks (estimated):**
1. Implement exact-match evaluation
2. Implement sequential inference loop
3. Collect entropy and correctness arrays
4. Handle edge cases (NaN entropy, tokenization failures)

**Complexity Score:** 4/20
- Module Size: 1 (main.py orchestration)
- Dependencies: 1 (dataset iteration)
- Algorithm: 1 (exact match handling)
- Integration: 1 (model + data coordination)

**Estimated Effort:** 2 hours

---

### Epic-4: Statistical Analysis and Gate Validation
**Priority:** P0  
**Description:** Implement Spearman correlation, extraction rate, quadrant analysis, and gate pass/fail logic.

**Subtasks (estimated):**
1. Implement Spearman correlation with SciPy
2. Implement extraction rate metric
3. Implement quadrant analysis (median splits)
4. Implement gate validation logic (3 criteria)

**Complexity Score:** 5/20
- Module Size: 1 (metrics.py extensions)
- Dependencies: 1 (SciPy, NumPy)
- Algorithm: 2 (quadrant logic, median splits)
- Integration: 1 (multi-metric coordination)

**Estimated Effort:** 2-3 hours

---

### Epic-5: Visualization and Reporting
**Priority:** P1  
**Description:** Generate 4 required figures (gate metrics, scatter, histograms, quadrant plot) and write 04_validation.md report.

**Subtasks (estimated):**
1. Implement gate metrics bar chart
2. Implement scatter plot with regression
3. Implement overlaid histograms
4. Implement quadrant plot with annotations
5. Generate 04_validation.md with embedded figures

**Complexity Score:** 4/20
- Module Size: 1 (visualization.py)
- Dependencies: 1 (matplotlib/seaborn)
- Algorithm: 1 (regression line computation)
- Integration: 1 (figure saving + report generation)

**Estimated Effort:** 2-3 hours

---

## Epic Task Summary

| Epic | Priority | Complexity | Status |
|------|----------|------------|--------|
| Epic-1: Environment Setup | P0 | 3/20 | NOT_STARTED |
| Epic-2: Inference Pipeline | P0 | 5/20 | NOT_STARTED |
| Epic-3: Evaluation Loop | P0 | 4/20 | NOT_STARTED |
| Epic-4: Statistical Analysis | P0 | 5/20 | NOT_STARTED |
| Epic-5: Visualization | P1 | 4/20 | NOT_STARTED |

**Total Epic Tasks:** 5 (within LIGHT budget: 4-8)  
**Total Complexity:** 21/100  
**Overall Assessment:** LOW-MEDIUM complexity (infrastructure validation PoC)

---

## External Dependencies

### Libraries
- `torch >= 2.0` — Tensor operations, softmax, entropy
- `transformers >= 4.30` — Llama-2 model, tokenizer
- `datasets >= 2.10` — TriviaQA loading
- `scipy >= 1.10` — Spearman correlation
- `numpy >= 1.24` — Array operations
- `matplotlib >= 3.7` — Plotting

### Pretrained Artifacts
- Llama-2-7B-hf (13GB) — HuggingFace model hub
- TriviaQA unfiltered (600MB) — HuggingFace datasets

### System
- Python 3.8+
- CUDA 11.8+ (optional)
- 20GB disk space
- 16GB RAM (32GB for GPU)

---

## Integration Points

### Input Integration
- **Phase 2C:** 02c_experiment_brief.md defines dataset, model, metrics
- **PRD:** 03_prd.md specifies functional requirements

### Output Integration
- **Phase 4:** Tasks from this architecture feed into 03_tasks.yaml
- **Validation:** 04_validation.md reports gate pass/fail
- **Phase 4.5:** Results feed into hypothesis synthesis

---

## Non-Functional Considerations

### Performance
- Sequential processing (batch_size=1) acceptable for PoC
- Single forward pass per example (no multi-pass methods)
- GPU acceleration optional (CPU fallback)

### Scalability
- Fixed 1,000 examples (no scaling needed)
- Stateless inference (no memory across examples)

### Maintainability
- Minimal abstraction for PoC
- Flat module structure
- No complex inheritance or factories

### Error Handling
- Skip examples with NaN entropy
- Graceful fallback for GPU unavailability
- Report skipped examples count

---

## Risk Assessment

### Technical Risks
1. **Model download failure** — Fallback to GPT-2 for infrastructure test
2. **GPU OOM** — CPU inference with sequential processing
3. **No correlation found** — Expected outcome (MUST_WORK gate)

### Mitigation Strategy
- Minimal dependencies (standard libraries)
- Robust error handling for edge cases
- Clear gate failure reporting

---

## Complexity Breakdown

### Overall System Complexity: **21/100** (LOW-MEDIUM)

**Rationale:**
- Standard libraries and patterns
- No novel algorithms
- Minimal integration complexity
- Frozen model (no training overhead)

**Complexity Distribution:**
- Very High (16-20): 0 tasks
- High (11-15): 0 tasks
- Medium (6-10): 0 tasks
- Low (1-5): 5 tasks

**Budget Compliance:**
- Epic range: 4-8 → **5 tasks** ✓
- Total max: 15 → **~12-15 subtasks** ✓
- Infrastructure: minimal → **No distributed systems** ✓

---

**Architecture Status:** Ready for Logic and Config design (Step 5)
