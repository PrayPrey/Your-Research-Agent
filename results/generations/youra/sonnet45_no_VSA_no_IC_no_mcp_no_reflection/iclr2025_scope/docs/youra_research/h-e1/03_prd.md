# Product Requirements Document (PRD)

**Document Type:** PRD  
**Hypothesis:** H-E1  
**Date:** 2026-08-28  
**Author:** Anonymous  
**Status:** DRAFT

---

## Executive Summary

### Purpose
Validate that Mamba-130M pretrained checkpoint exists, loads correctly into GPU memory, and produces non-random outputs on GLUE zero-shot evaluation tasks.

### Problem Statement
Before conducting LoRA transfer learning experiments on Mamba architecture, we must verify foundational infrastructure: pretrained checkpoint availability, model loading capabilities, and baseline inference functionality.

### Success Criteria
- Checkpoint downloads and loads without errors
- Model fits in <16GB GPU memory
- Zero-shot accuracy exceeds random baseline on ALL GLUE tasks:
  - MNLI: >33.3% (3-class)
  - QQP: >50% (binary)
  - SST-2: >50% (binary)

### Scope
- **In Scope:** Checkpoint loading, zero-shot GLUE evaluation, memory footprint validation
- **Out of Scope:** Training, fine-tuning, architecture modifications, LoRA adaptation

---

## Functional Requirements

### FR-1: Model Checkpoint Management
**Priority:** P0 (MUST_WORK gate)  
**Description:** Download and load Mamba-130M pretrained checkpoint from HuggingFace Hub.

**Acceptance Criteria:**
- Download `state-spaces/mamba-130m-hf` checkpoint
- Load into PyTorch model using `AutoModelForCausalLM.from_pretrained()`
- Verify model architecture matches expected Mamba-130M structure
- Support automatic device mapping (`device_map="auto"`)
- Support automatic dtype selection (`torch_dtype="auto"`)

**Dependencies:** HuggingFace Transformers v4.35+, internet connection for download

---

### FR-2: Dataset Loading
**Priority:** P0  
**Description:** Load GLUE benchmark validation splits for zero-shot evaluation.

**Acceptance Criteria:**
- Load three GLUE tasks: MNLI (matched), QQP, SST-2
- Use validation splits only (no training data)
- Load via HuggingFace datasets library
- Verify sample counts:
  - MNLI validation_matched: 9,815 examples
  - QQP validation: 40,430 examples
  - SST-2 validation: 872 examples

**Dependencies:** HuggingFace datasets library, internet connection for download

---

### FR-3: Tokenizer Initialization
**Priority:** P0  
**Description:** Load and configure tokenizer matching Mamba-130M checkpoint.

**Acceptance Criteria:**
- Load tokenizer from `state-spaces/mamba-130m-hf`
- Support max sequence length of 512 tokens
- Implement dynamic padding to batch max length
- Handle truncation for sequences exceeding max length

**Dependencies:** HuggingFace Transformers library

---

### FR-4: Zero-Shot Inference
**Priority:** P0  
**Description:** Implement zero-shot classification via log-probability comparison.

**Acceptance Criteria:**
- Format task-specific prompts for each GLUE task
- Compute log probabilities for each answer choice
- Select answer with highest log probability
- Support batch processing (batch_size=16)
- Use FP16 mixed precision for efficiency
- Set random seed=42 for reproducibility

**Technical Details:**
```python
def zero_shot_classify(model, tokenizer, text, choices, device):
    prompt = format_task_prompt(text, task_name)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    choice_probs = []
    for choice in choices:
        choice_tokens = tokenizer(choice, return_tensors="pt").input_ids
        with torch.no_grad():
            outputs = model(**inputs, labels=choice_tokens)
            log_prob = -outputs.loss.item()
        choice_probs.append(log_prob)
    
    return np.argmax(choice_probs)
```

**Dependencies:** PyTorch, NumPy

---

### FR-5: Accuracy Evaluation
**Priority:** P0  
**Description:** Compute accuracy metrics for each GLUE task.

**Acceptance Criteria:**
- Calculate accuracy = (correct predictions / total examples)
- Report per-task breakdown (MNLI, QQP, SST-2)
- Verify all accuracies exceed random baseline
- Save results to JSON file

**Metrics:**
- Task-specific accuracy (3 values)
- Random baseline comparison
- Sample count per task

**Dependencies:** HuggingFace evaluate or sklearn.metrics

---

### FR-6: Memory Footprint Validation
**Priority:** P0  
**Description:** Verify model fits in GPU memory constraint.

**Acceptance Criteria:**
- Load model with FP16 precision
- Measure peak GPU memory usage
- Assert peak memory < 16GB
- Log memory statistics to console

**Dependencies:** PyTorch CUDA memory tracking

---

### FR-7: Inference Time Tracking
**Priority:** P1 (Secondary metric)  
**Description:** Track inference time per GLUE task.

**Acceptance Criteria:**
- Measure wall-clock time per task evaluation
- Verify each task completes in <5 minutes
- Log time per example (averaged)

**Dependencies:** Python `time` module

---

### FR-8: Results Visualization
**Priority:** P1  
**Description:** Generate figures comparing zero-shot performance vs random baseline.

**Acceptance Criteria:**
- Bar chart: Zero-shot accuracy vs random baseline (3 tasks)
- Performance table: Task, samples, accuracy, baseline
- Save figures to `{hypothesis_folder}/figures/`

**Figure Requirements:**
1. Gate Metrics Comparison (mandatory): Bar chart with 3 task comparisons
2. Per-Task Performance Table
3. Inference Time Analysis (optional)

**Dependencies:** matplotlib or seaborn

---

## Non-Functional Requirements

### NFR-1: Performance
- Model inference: <5 minutes per GLUE task
- Total evaluation time: <20 minutes for all three tasks
- GPU memory: <16GB peak usage

### NFR-2: Reliability
- Deterministic outputs (fixed random seed)
- Graceful handling of download failures (retry logic)
- Model checkpoint integrity verification

### NFR-3: Maintainability
- Clear code structure with modular functions
- Logging for key operations (download, load, inference)
- Results saved to structured JSON format

### NFR-4: Compatibility
- Python 3.9+
- PyTorch 2.0+
- CUDA 11.8+ (for GPU inference)
- HuggingFace Transformers 4.35+

---

## Data Requirements

### Input Data
1. **Mamba-130M Checkpoint**
   - Source: HuggingFace Hub (`state-spaces/mamba-130m-hf`)
   - Format: PyTorch state dict
   - Size: ~500MB (estimated)
   - Cache: `~/.cache/huggingface/hub/`

2. **GLUE Validation Sets**
   - Source: HuggingFace datasets (`glue`)
   - Tasks: MNLI (matched), QQP, SST-2
   - Total samples: 51,117
   - Format: HuggingFace Dataset objects
   - Cache: `~/.cache/huggingface/datasets/`

### Output Data
1. **Evaluation Results**
   - File: `{hypothesis_folder}/results.json`
   - Format: JSON
   - Contents: Per-task accuracy, baselines, sample counts, inference times

2. **Figures**
   - Directory: `{hypothesis_folder}/figures/`
   - Format: PNG (300 DPI)
   - Files: `gate_metrics.png`, `performance_table.png`, `inference_time.png`

---

## Dependencies

### External Libraries
- `transformers>=4.35.0` (Mamba model support)
- `datasets>=2.14.0` (GLUE loading)
- `torch>=2.0.0` (Model inference)
- `numpy>=1.24.0` (Array operations)
- `matplotlib>=3.7.0` (Visualization)
- `evaluate>=0.4.0` or `scikit-learn>=1.3.0` (Metrics)

### Hardware Requirements
- GPU: 16GB+ VRAM (NVIDIA recommended)
- RAM: 32GB+ (for dataset caching)
- Storage: 10GB+ (checkpoints + datasets)

### Environment Setup
- CUDA toolkit 11.8+ (for GPU)
- Python virtual environment (conda/venv)
- Internet connection (initial download only)

---

## Implementation Phases

### Phase 1: Environment Setup (Epic-1)
- Install dependencies
- Verify CUDA availability
- Create output directories

### Phase 2: Data Preparation (Epic-2)
- Download Mamba-130M checkpoint
- Download GLUE validation sets
- Verify data integrity

### Phase 3: Core Implementation (Epic-3)
- Implement zero-shot classification function
- Implement prompt formatting per task
- Implement log-probability computation

### Phase 4: Evaluation (Epic-4)
- Run zero-shot evaluation on all tasks
- Compute accuracy metrics
- Generate visualizations

### Phase 5: Validation (Epic-5)
- Verify accuracy > random baseline
- Validate memory footprint
- Measure inference time
- Save results

---

## Success Metrics

### Gate Metrics (MUST_WORK)
1. **Checkpoint Loading:** Model loads without errors
2. **Memory Constraint:** Peak GPU memory < 16GB
3. **MNLI Accuracy:** > 33.3%
4. **QQP Accuracy:** > 50%
5. **SST-2 Accuracy:** > 50%

### Secondary Metrics
1. **Inference Efficiency:** <5 min per task
2. **Code Quality:** Modular, documented, reproducible

### Failure Conditions
- Any checkpoint loading error → BLOCKS entire pipeline
- Any task accuracy ≤ random baseline → BLOCKS entire pipeline
- Memory usage > 16GB → BLOCKS entire pipeline

---

## Risks and Mitigations

### Risk 1: Checkpoint Download Failure
**Likelihood:** Low  
**Impact:** High  
**Mitigation:** Implement retry logic with exponential backoff; fallback to manual download

### Risk 2: GPU Memory Overflow
**Likelihood:** Medium  
**Impact:** High  
**Mitigation:** Use FP16 precision; reduce batch size if needed; verify memory before full eval

### Risk 3: Below-Baseline Performance
**Likelihood:** Low (pretrained checkpoint should work)  
**Impact:** High (MUST_WORK gate failure)  
**Mitigation:** Verify prompt formatting; check tokenizer compatibility; inspect model outputs

---

## Appendix

### Reference Implementations
1. Mamba Official Repo: https://github.com/state-spaces/mamba
2. HuggingFace Model Card: https://huggingface.co/state-spaces/mamba-130m-hf
3. GLUE Benchmark: https://huggingface.co/datasets/glue

### Related Documents
- Phase 2C Experiment Design: `02c_experiment_brief.md`
- Architecture Document: `03_architecture.md` (next)
- Logic Specification: `03_logic.md` (next)
- Configuration Schema: `03_config.md` (next)

---

**Document Status:** Ready for Architecture Design (Step 3)
