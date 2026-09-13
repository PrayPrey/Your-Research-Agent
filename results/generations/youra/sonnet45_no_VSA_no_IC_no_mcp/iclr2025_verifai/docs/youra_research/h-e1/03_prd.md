# Product Requirements Document: h-e1 Beam Search Infrastructure PoC

**Date:** 2026-08-25  
**Author:** Anonymous  
**Hypothesis:** h-e1 (EXISTENCE)  
**Status:** Draft

---

## Executive Summary

This PRD specifies requirements for a proof-of-concept (PoC) validation of beam search infrastructure with custom scoring for code generation. The system must demonstrate that beam search with AST-based validity scoring is computationally feasible and that AST parsing operates reliably for Python code validation.

**Success Criteria:** Complete 5-problem PoC in <30 minutes with AST parse latency <50ms per sample.

---

## Problem Statement

### Research Question
Can beam search with custom scoring improve code generation quality while remaining computationally feasible? Specifically: does the infrastructure work?

### Hypothesis
Beam search with custom scoring exists and is computationally feasible for code generation. AST parsing works reliably for Python code validation.

### Gate Condition
**Type:** MUST_WORK  
**Consequence:** If infrastructure fails, abandon entire verification approach.

---

## Functional Requirements

### FR-1: Beam Search Implementation
**Priority:** P0  
**Description:** Implement beam search decoder with k=5 beams for CodeLlama-7B.

**Acceptance Criteria:**
- Uses HuggingFace Transformers `generate()` method with `num_beams=5`
- Returns k=5 candidate solutions per problem
- Maintains beam count throughout generation
- Completes without errors

**Dependencies:** HuggingFace Transformers library, CodeLlama-7B model

---

### FR-2: Custom Scoring Function
**Priority:** P0  
**Description:** Implement combined scoring: α=0.7 (fluency) + β=0.3 (validity).

**Acceptance Criteria:**
- Scores combine log-likelihood and AST validity (0.0 or 1.0)
- Integrated with beam search candidate ranking
- Formula: `final_score = 0.7 * logprob + 0.3 * validity_score`

**Dependencies:** FR-1, FR-3

---

### FR-3: AST Validation
**Priority:** P0  
**Description:** Parse generated code with Python `ast.parse()` for syntax validation.

**Acceptance Criteria:**
- Attempts to parse each generated candidate
- Returns validity score: 1.0 (valid) or 0.0 (invalid)
- Average parse latency <50ms per sample
- Handles all Python syntax errors gracefully

**Dependencies:** Python standard library `ast` module

---

### FR-4: Dataset Loading
**Priority:** P0  
**Description:** Load HumanEval-164 benchmark and extract 5-problem PoC subset.

**Acceptance Criteria:**
- Uses `datasets` library to load `openai_humaneval`
- Selects first 5 problems from test split
- Extracts prompt and canonical solution per problem

**Implementation:**
```python
from datasets import load_dataset
dataset = load_dataset("openai_humaneval")
poc_subset = dataset['test'].select(range(5))
```

---

### FR-5: Model Loading
**Priority:** P0  
**Description:** Load CodeLlama-7B from HuggingFace Hub.

**Acceptance Criteria:**
- Loads `meta-llama/CodeLlama-7b-hf` model and tokenizer
- Model ready for generation with beam search
- Falls back to CPU if GPU unavailable

**Implementation:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-hf")
```

---

### FR-6: Computational Timing
**Priority:** P0  
**Description:** Measure wall-clock time for 5-problem PoC execution.

**Acceptance Criteria:**
- Records start and end timestamps
- Reports total elapsed time in minutes
- Target: <30 minutes for 5 problems
- Extrapolates to 164-problem runtime

**Dependencies:** Python `time` module

---

### FR-7: AST Latency Measurement
**Priority:** P0  
**Description:** Measure per-sample AST parsing latency.

**Acceptance Criteria:**
- Times each `ast.parse()` call
- Computes average latency across all generated candidates
- Target: <50ms average
- Reports distribution (min, max, avg)

**Dependencies:** FR-3

---

### FR-8: Figure Generation
**Priority:** P1  
**Description:** Generate mandatory gate metrics comparison figure.

**Acceptance Criteria:**
- Bar chart comparing target vs actual for:
  - Computational time (target: 30 min)
  - AST parse latency (target: 50ms)
- Saved to `h-e1/figures/gate_metrics.png`
- Clear labels, legend, and units

**Additional Figures (Autonomous):**
- Beam count per generation step
- AST latency distribution histogram
- Per-problem generation time bar chart

**Dependencies:** FR-6, FR-7, matplotlib or similar

---

## Non-Functional Requirements

### NFR-1: Performance
- **Target:** Complete 5-problem PoC in <30 minutes
- **Rationale:** Validates computational feasibility for full 164-problem evaluation
- **Measurement:** Wall-clock time from generation start to completion

### NFR-2: Parsing Reliability
- **Target:** AST parse latency <50ms per sample
- **Rationale:** Ensures validity checking doesn't bottleneck generation pipeline
- **Measurement:** Average time per `ast.parse()` call

### NFR-3: Robustness
- **Requirement:** Handle syntax errors in generated code gracefully
- **Rationale:** Invalid code is expected; system must not crash
- **Implementation:** Try-except blocks around `ast.parse()`

### NFR-4: Reproducibility
- **Requirement:** Fixed random seed for deterministic beam search
- **Rationale:** Enable result verification
- **Implementation:** Set `torch.manual_seed(42)` and `torch.backends.cudnn.deterministic = True`

---

## Success Criteria

### Gate Validation
**MUST_WORK Gate Passes If:**
1. Code runs without errors
2. Computational time <30 minutes for 5 problems
3. AST parse latency <50ms average
4. k=5 candidates generated per problem
5. All outputs are parseable strings

**Gate Fails If:**
- Runtime errors during beam search
- Timeout exceeds 30 minutes
- AST latency exceeds 50ms
- Beam search doesn't maintain k=5

### Phase 4 PoC Validation
**Minimal PoC Passes If:**
1. All 5 problems complete successfully
2. Gate metrics within targets

---

## Data Requirements

### Primary Dataset
- **Name:** HumanEval-164
- **Source:** `datasets` library, identifier `openai_humaneval`
- **Subset:** First 5 problems from test split
- **Size:** 5 problems (PoC) → 164 full validation
- **Format:** JSON with fields `prompt`, `canonical_solution`, `test`, `entry_point`

### Model Weights
- **Name:** CodeLlama-7B
- **Source:** HuggingFace Hub
- **Identifier:** `meta-llama/CodeLlama-7b-hf`
- **Size:** ~13GB (FP32)
- **License:** Llama 2 Community License

---

## Dependencies

### Python Libraries
- `transformers` (HuggingFace)
- `torch` (PyTorch)
- `datasets` (HuggingFace Datasets)
- `matplotlib` (figure generation)
- `ast` (built-in)
- `time` (built-in)

### Hardware
- **Minimum:** 16GB RAM, CPU-only execution
- **Recommended:** NVIDIA GPU with 16GB+ VRAM for faster generation

### Software
- Python 3.8+
- CUDA 11.8+ (if using GPU)

---

## Out of Scope

- Training or fine-tuning models
- Full 164-problem evaluation (Phase 4 PoC only)
- Pass@k accuracy metrics (infrastructure validation only)
- Custom beam search implementation (use HF Transformers)
- Alternative scoring functions (fixed α=0.7, β=0.3)
- Non-Python languages

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| HF Transformers doesn't support custom scoring in beam search | Medium | High | Implement manual beam search with LogitsProcessor |
| Model download timeout | Low | Medium | Pre-cache model weights before experiment |
| GPU OOM during beam search | Medium | Medium | Reduce batch size to 1, use gradient checkpointing |
| AST parsing slower than 50ms | Low | High | Profile parsing, optimize candidate filtering |

---

## Metrics and Evaluation

### Primary Metrics
1. **Computational Time:** Wall-clock seconds for 5-problem PoC
2. **AST Parse Latency:** Average milliseconds per `ast.parse()` call

### Secondary Metrics
3. **Beam Maintenance:** Verify k=5 candidates per generation step
4. **Output Validity:** All candidates are parseable strings (not empty/truncated)

### Measurement Protocol
- Record timestamps before/after generation loop
- Time each AST parse call individually
- Log beam counts at each decoding step
- Save all metrics to JSON file for Phase 4.5 synthesis

---

## Validation Plan

### Phase 4 PoC Validation
**Scope:** Run on 5 HumanEval problems  
**Pass Condition:** All FRs functional, gate metrics met  
**Timeline:** Single execution (<30 min target)

### Figure Verification
- Gate metrics chart shows target vs actual bars
- AST latency distribution visible as histogram
- All figures saved to `h-e1/figures/`

---

## Appendix

### Reference Implementations
- HuggingFace beam search: https://huggingface.co/docs/transformers/main_classes/text_generation
- HumanEval dataset: https://github.com/openai/human-eval
- CodeLlama model card: https://huggingface.co/meta-llama/CodeLlama-7b-hf

### Related Documents
- Phase 2C Experiment Brief: `h-e1/02c_experiment_brief.md`
- Phase 3 Architecture: `h-e1/03_architecture.md` (next)
- Phase 3 Logic: `h-e1/03_logic.md` (next)
- Phase 3 Config: `h-e1/03_config.md` (next)

---

**Document Status:** Ready for Architecture Design (Phase 3 Step 3)
