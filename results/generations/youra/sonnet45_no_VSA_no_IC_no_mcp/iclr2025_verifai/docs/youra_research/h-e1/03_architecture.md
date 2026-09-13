# System Architecture: h-e1 Beam Search Infrastructure PoC

**Date:** 2026-08-25  
**Author:** Anonymous  
**Hypothesis:** h-e1 (EXISTENCE)  
**Tier:** LIGHT (Epic Range: 4-8 tasks, Total Max: 15 tasks)  
**Infrastructure Level:** Minimal

---

## Codebase Analysis (Serena)

**Analysis Type:** Green-field (no existing codebase)

This is a foundation hypothesis with no prerequisites. No base codebase exists to analyze. Starting from scratch with minimal infrastructure for PoC validation.

**Codebase State:**
- No existing modules
- No existing test infrastructure
- No existing data pipelines

**Design Implications:**
- Build minimal PoC structure
- Focus on core beam search + AST validation
- Defer abstractions until needed

---

## Architecture Overview

### System Purpose
Validate beam search infrastructure with custom AST-based scoring for code generation. Demonstrate computational feasibility and parsing reliability.

### Design Philosophy
**Minimal PoC Design:**
- Single-file implementation (beam_search_poc.py)
- No abstraction layers (YAGNI)
- Inline scoring function
- Direct HuggingFace API usage
- Built-in timing and metrics

**Applied:** Minimal PoC Pattern (Archon KB: PoC Validation Best Practices)  
**Rationale:** EXISTENCE gate only needs infrastructure proof, not production architecture.

---

## Module Structure

### Module 1: Data Preparation
**File:** `data_loader.py`  
**Purpose:** Load HumanEval-164 dataset and extract 5-problem PoC subset

**Components:**
- `load_humaneval()` → Dataset object
- `extract_poc_subset(dataset, n=5)` → List of problems

**Dependencies:** `datasets` library

**Complexity Score:** 3/20  
- Module Size: 1 (single file, ~50 LOC)
- Dependencies: 1 (datasets library only)
- Algorithm: 0 (simple indexing)
- Integration: 1 (dataset API straightforward)

---

### Module 2: Model Setup
**File:** `model_loader.py`  
**Purpose:** Load CodeLlama-7B model and tokenizer from HuggingFace Hub

**Components:**
- `load_codellama()` → (model, tokenizer) tuple
- `setup_device()` → torch.device (GPU or CPU fallback)

**Dependencies:** `transformers`, `torch`

**Complexity Score:** 4/20  
- Module Size: 1 (single file, ~80 LOC)
- Dependencies: 2 (transformers, torch)
- Algorithm: 0 (API wrapper)
- Integration: 1 (device management)

---

### Module 3: Beam Search Engine
**File:** `beam_search.py`  
**Purpose:** Implement beam search with custom AST-based scoring

**Components:**
- `custom_scoring_fn(outputs, logprobs)` → validity scores
- `run_beam_search(model, tokenizer, prompts, k=5)` → candidates
- AST validation: `validate_syntax(code)` → bool

**Dependencies:** `ast`, `transformers`

**Complexity Score:** 8/20  
- Module Size: 3 (core logic ~150 LOC)
- Dependencies: 1 (built-in ast)
- Algorithm: 3 (beam search integration with custom scoring)
- Integration: 1 (HF generate API)

**Applied:** Custom Scoring Integration Pattern (Archon KB: Beam Search Extensions)  
**Note:** HF Transformers `generate()` may not directly support custom scoring callbacks. May require LogitsProcessor implementation or manual beam tracking.

---

### Module 4: Evaluation Metrics
**File:** `metrics.py`  
**Purpose:** Measure computational time and AST parse latency

**Components:**
- `time_generation(fn)` → elapsed seconds
- `measure_ast_latency(candidates)` → latency stats
- `compute_gate_metrics(time, latency)` → pass/fail dict

**Dependencies:** `time`, `ast`

**Complexity Score:** 2/20  
- Module Size: 1 (simple timers, ~60 LOC)
- Dependencies: 0 (built-in modules)
- Algorithm: 0 (trivial timing)
- Integration: 1 (wrap generation calls)

---

### Module 5: Visualization
**File:** `visualizations.py`  
**Purpose:** Generate mandatory gate metrics figure and additional charts

**Components:**
- `plot_gate_metrics(targets, actuals)` → bar chart
- `plot_ast_latency_dist(latencies)` → histogram
- `plot_beam_counts(beam_logs)` → line chart

**Dependencies:** `matplotlib`

**Complexity Score:** 3/20  
- Module Size: 1 (~100 LOC)
- Dependencies: 1 (matplotlib)
- Algorithm: 0 (plotting library calls)
- Integration: 1 (save to figures/ folder)

---

### Module 6: Main Execution Pipeline
**File:** `run_poc.py`  
**Purpose:** Orchestrate PoC execution: load data/model → run beam search → measure → plot

**Components:**
- `main()` → execution orchestrator
- Checkpoint saving after each problem
- Progress logging

**Dependencies:** All above modules

**Complexity Score:** 5/20  
- Module Size: 2 (orchestration ~120 LOC)
- Dependencies: 2 (all internal modules + checkpointing)
- Algorithm: 0 (sequential execution)
- Integration: 1 (coordinate modules)

---

## File Organization

```
h-e1/
├── code/
│   ├── data_loader.py          # Module 1
│   ├── model_loader.py          # Module 2
│   ├── beam_search.py           # Module 3
│   ├── metrics.py               # Module 4
│   ├── visualizations.py        # Module 5
│   ├── run_poc.py               # Module 6 (entry point)
│   └── requirements.txt         # Dependencies
├── figures/
│   ├── gate_metrics.png         # Mandatory
│   ├── ast_latency_dist.png     # Optional
│   └── beam_counts.png          # Optional
└── outputs/
    ├── results.json             # Metrics dump
    └── poc_log.txt              # Execution log
```

**Applied:** Flat Module Structure (Archon KB: PoC Organization Patterns)  
**Rationale:** LIGHT tier, 6 modules, no nested packages needed.

---

## Proposed Epic Tasks

### EPIC-1: Environment Setup
**Priority:** P0  
**Description:** Set up Python environment with dependencies and verify GPU availability

**Subtasks:**
1. Create virtual environment
2. Install requirements (transformers, torch, datasets, matplotlib)
3. Verify CUDA availability (fallback to CPU if needed)
4. Pre-download CodeLlama-7B weights (meta-llama/CodeLlama-7b-hf)

**Complexity:** 4/20  
- Module_Size: 1 (setup scripts)
- Dependencies: 1 (external libraries)
- Algorithm: 0
- Integration: 2 (GPU detection, model caching)

**Estimated Effort:** Low

---

### EPIC-2: Data Preparation Pipeline
**Priority:** P0  
**Description:** Load HumanEval and prepare 5-problem PoC subset

**Subtasks:**
1. Implement `load_humaneval()` using datasets library
2. Implement `extract_poc_subset(n=5)` selector
3. Validate problem structure (prompt, canonical_solution, test)
4. Save PoC subset to JSON for inspection

**Complexity:** 3/20  
- Module_Size: 1
- Dependencies: 1 (datasets)
- Algorithm: 0
- Integration: 1

**Estimated Effort:** Low

---

### EPIC-3: Model Loading Infrastructure
**Priority:** P0  
**Description:** Load CodeLlama-7B model and tokenizer with device management

**Subtasks:**
1. Implement `setup_device()` (GPU/CPU fallback)
2. Implement `load_codellama()` with caching
3. Verify model inference ready (test generation)
4. Log model config and device info

**Complexity:** 4/20  
- Module_Size: 1
- Dependencies: 2 (transformers, torch)
- Algorithm: 0
- Integration: 1

**Estimated Effort:** Low

---

### EPIC-4: Beam Search with Custom Scoring
**Priority:** P0  
**Description:** Implement beam search with AST validity scoring (α=0.7 fluency + β=0.3 validity)

**Subtasks:**
1. Implement `validate_syntax(code)` using ast.parse()
2. Design `custom_scoring_fn(outputs, logprobs)` with combined score
3. Integrate with HF generate() or implement LogitsProcessor
4. Implement `run_beam_search(prompts, k=5)` wrapper
5. Verify k=5 candidates returned per problem

**Complexity:** 8/20  
- Module_Size: 3
- Dependencies: 1
- Algorithm: 3 (scoring integration)
- Integration: 1

**Estimated Effort:** Medium

**Applied:** Beam Search Customization Pattern (Archon KB: Generation Extensions)  
**Note:** If HF doesn't support custom scoring callbacks, implement manual beam tracking with score reordering.

---

### EPIC-5: Metrics and Timing
**Priority:** P0  
**Description:** Measure computational time and AST parse latency

**Subtasks:**
1. Implement `time_generation()` decorator
2. Implement `measure_ast_latency()` per-candidate timer
3. Compute statistics (mean, min, max for latency)
4. Implement `compute_gate_metrics()` pass/fail logic
5. Save metrics to JSON

**Complexity:** 2/20  
- Module_Size: 1
- Dependencies: 0
- Algorithm: 0
- Integration: 1

**Estimated Effort:** Low

---

### EPIC-6: Visualization Generation
**Priority:** P1  
**Description:** Generate mandatory gate metrics figure and optional diagnostic charts

**Subtasks:**
1. Implement `plot_gate_metrics()` bar chart (target vs actual)
2. Implement `plot_ast_latency_dist()` histogram
3. Implement `plot_beam_counts()` line chart
4. Save all figures to h-e1/figures/
5. Apply consistent styling and labels

**Complexity:** 3/20  
- Module_Size: 1
- Dependencies: 1 (matplotlib)
- Algorithm: 0
- Integration: 1

**Estimated Effort:** Low

---

### EPIC-7: Main Execution Pipeline
**Priority:** P0  
**Description:** Orchestrate full PoC: load → generate → measure → plot

**Subtasks:**
1. Implement `main()` orchestration function
2. Add progress logging per problem
3. Add checkpoint saving (resume if interrupted)
4. Write execution summary to outputs/poc_log.txt
5. Validate all outputs generated

**Complexity:** 5/20  
- Module_Size: 2
- Dependencies: 2 (all modules + logging)
- Algorithm: 0
- Integration: 1

**Estimated Effort:** Low

---

## Epic Summary

| Epic | Complexity | Priority | Effort |
|------|------------|----------|--------|
| EPIC-1: Environment Setup | 4/20 | P0 | Low |
| EPIC-2: Data Preparation | 3/20 | P0 | Low |
| EPIC-3: Model Loading | 4/20 | P0 | Low |
| EPIC-4: Beam Search | 8/20 | P0 | Medium |
| EPIC-5: Metrics | 2/20 | P0 | Low |
| EPIC-6: Visualization | 3/20 | P1 | Low |
| EPIC-7: Main Pipeline | 5/20 | P0 | Low |

**Total Epic Tasks:** 7 (within LIGHT tier range of 4-8)  
**Total Complexity:** 29/140 (low complexity per task on average)

---

## External Dependencies

### Python Libraries
| Library | Version | Purpose | Installation |
|---------|---------|---------|--------------|
| transformers | ≥4.30.0 | CodeLlama + beam search | `pip install transformers` |
| torch | ≥2.0.0 | Model inference | `pip install torch` |
| datasets | ≥2.12.0 | HumanEval loader | `pip install datasets` |
| matplotlib | ≥3.5.0 | Figure generation | `pip install matplotlib` |

### Model Weights
- **Source:** HuggingFace Hub
- **Identifier:** `meta-llama/CodeLlama-7b-hf`
- **Size:** ~13GB
- **License:** Llama 2 Community License (requires acceptance on HF Hub)

### Hardware
- **Minimum:** 16GB RAM (CPU-only mode)
- **Recommended:** NVIDIA GPU with 16GB+ VRAM

---

## Integration Points

### Data Flow
```
HumanEval Dataset
    ↓ (datasets library)
PoC Subset (5 problems)
    ↓ (prompts)
CodeLlama-7B + Beam Search
    ↓ (k=5 candidates per problem)
AST Validation + Scoring
    ↓ (validity scores)
Metrics Collection
    ↓ (time, latency)
Visualization
    ↓ (figures/)
Gate Validation
```

### Critical Paths
1. **Model Loading:** Must cache weights to avoid repeated downloads
2. **Beam Search:** Custom scoring integration may require fallback to manual implementation
3. **AST Parsing:** Must handle all syntax errors gracefully (try-except wrapper)

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| HF doesn't support custom scoring | Implement LogitsProcessor or manual beam tracking |
| GPU OOM during beam search | Reduce batch size to 1, enable gradient checkpointing |
| AST parsing slower than target | Profile with cProfile, optimize candidate filtering |
| Model download timeout | Pre-cache weights in EPIC-1 setup phase |

---

## Success Criteria (Architecture Level)

**System Complete When:**
1. All 7 Epic tasks implemented
2. Code runs end-to-end without errors
3. Output files generated:
   - `figures/gate_metrics.png` (mandatory)
   - `outputs/results.json` (metrics)
   - `outputs/poc_log.txt` (execution log)
4. Gate metrics within targets (verified in Phase 4)

---

## Next Steps

**Phase 3 Continuation:**
- Step 4: Budget Allocation (allocate 15 total tasks across Epics)
- Step 5: Logic Design (API signatures, algorithms)
- Step 5: Config Design (hyperparameters, settings)
- Step 9: Generate 03_tasks.yaml from Epic breakdown

**Phase 4 Implementation:**
- Execute tasks in priority order: Environment → Data → Model → Beam Search → Metrics → Viz → Pipeline
- Validate PoC against gate metrics (<30 min, <50ms)

---

**Applied Patterns Summary:**
- Minimal PoC Pattern (Archon KB)
- Flat Module Structure (Archon KB)
- Beam Search Customization Pattern (Archon KB)

**Document Status:** Ready for Complexity Assessment (Phase 3 Step 4)
