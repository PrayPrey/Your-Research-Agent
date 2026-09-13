# Architecture: h-e1 Temperature Scaling Calibration

**Date:** 2026-07-11  
**Hypothesis:** h-e1  
**Type:** EXISTENCE (PoC)  
**Author:** Phase 3 Architecture Agent

---

## Knowledge Base Patterns

**Applied:** gpleiss/temperature_scaling pattern, torchmetrics ECE, HuggingFace pipeline

---

## Codebase Analysis (Serena)

**Project Type:** green-field (new hypothesis implementation)  
**Status:** Found reference implementation in h-e1-calibration/ (synthetic data version)  
**Analyzed Path:** h-e1-calibration/  
**Findings:** Existing TemperatureScaler class with LBFGS optimization available for reuse. Will adapt for Code Llama + MBPP.

---

## System Overview

**Goal:** Validate that temperature scaling reduces ECE by ≥30% on Code Llama 7B code generation.

**Pipeline:** MBPP Dataset → Code Llama Generation → Logit Extraction → Temperature Scaling → ECE Evaluation → Figures

**Constraint:** PoC architecture (3-5 epic tasks, minimal file structure).

---

## Module Structure

### 1. Dataset Module (`src/dataset.py`)

**Dependencies:** HuggingFace datasets

```python
class MBPPDataset:
    def __init__(self, split: str, task_ids: List[int]): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

def load_mbpp_splits(cal_ids: List[int], val_ids: List[int]) -> Tuple[MBPPDataset, MBPPDataset]: ...
def create_dataloader(dataset: MBPPDataset, batch_size: int) -> DataLoader: ...
```

### 2. Generation Module (`src/generation.py`)

**Dependencies:** transformers, torch

```python
class CodeGenerator:
    def __init__(self, model_name: str, device: str): ...
    def generate_with_logits(self, prompt: str) -> Tuple[str, torch.Tensor]: ...
    def batch_generate(self, prompts: List[str]) -> List[Tuple[str, torch.Tensor]]: ...
```

### 3. Execution Module (`src/execution.py`)

**Dependencies:** None (pure Python)

```python
class CodeExecutor:
    def __init__(self, timeout: int = 5): ...
    def execute_code(self, code: str, test_list: List[str], setup: str) -> bool: ...
    def is_correct(self, code: str, problem: dict) -> int: ...
```

### 4. Calibration Module (`src/calibration.py`)

**Dependencies:** torch

```python
class TemperatureScaler:
    def __init__(self, init_temp: float = 1.5): ...
    def fit(self, logits: torch.Tensor, labels: torch.Tensor, max_iter: int = 200) -> float: ...
    def scale(self, logits: torch.Tensor) -> torch.Tensor: ...
    def get_temperature(self) -> float: ...
```

### 5. Evaluation Module (`src/evaluation.py`)

**Dependencies:** torchmetrics, matplotlib

```python
def compute_ece(confidences: torch.Tensor, correctness: torch.Tensor, n_bins: int = 15) -> float: ...
def compute_confidence(logits: torch.Tensor) -> torch.Tensor: ...
def generate_reliability_diagram(conf_before: torch.Tensor, conf_after: torch.Tensor, 
                                  correct: torch.Tensor, save_path: str): ...
def generate_ece_comparison(ece_before: float, ece_after: float, save_path: str): ...
def generate_all_figures(results: dict, output_dir: str): ...
```

### 6. Main Experiment (`main.py`)

**Dependencies:** All modules above

```python
def run_experiment(config: dict) -> dict: ...
def main():
    # 1. Load MBPP splits
    # 2. Load Code Llama
    # 3. Generate code + logits (cal + val)
    # 4. Execute code to get correctness
    # 5. Optimize temperature (cal split)
    # 6. Evaluate ECE (val split)
    # 7. Generate figures
    # 8. Return gate decision
    ...
```

### 7. Configuration (`config.py`)

**Dependencies:** None

```python
EXPERIMENT_CONFIG = {
    'model': 'meta-llama/CodeLlama-7b-hf',
    'dataset': 'google-research-datasets/mbpp',
    'splits': {...},
    'generation': {...},
    'calibration': {...},
    'evaluation': {...}
}
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── dataset.py          # MBPP loading + custom splits
│   │   ├── generation.py       # Code Llama inference
│   │   ├── execution.py        # Sandboxed code execution
│   │   ├── calibration.py      # Temperature scaling
│   │   └── evaluation.py       # ECE + figures
│   ├── main.py                 # Experiment orchestrator
│   ├── config.py               # Fixed configuration
│   └── requirements.txt        # Dependencies
├── figures/                    # Output visualizations (5 PNGs)
├── logs/                       # Execution logs
└── results/                    # ECE values, optimal T
```

---

## Data Flow

1. **Dataset Loading:** MBPP → Custom split (cal: IDs 511-600+11-120, val: 121-315)
2. **Generation Phase:**
   - Cal split: 195 prompts → Code Llama → (code, logits) pairs
   - Val split: 195 prompts → Code Llama → (code, logits) pairs
3. **Execution Phase:** Generated code → Sandboxed execution → Binary correctness
4. **Calibration Phase:** Cal logits + correctness → LBFGS → Optimal T
5. **Evaluation Phase:**
   - Compute ECE_before (val logits / 1.0)
   - Compute ECE_after (val logits / T)
   - Generate 5 figures
6. **Gate Decision:** ECE reduction ≥ 30% → PASS

---

## Integration Points

### HuggingFace Transformers
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/CodeLlama-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
```

### HuggingFace Datasets
```python
from datasets import load_dataset
mbpp = load_dataset("google-research-datasets/mbpp", split="test")
```

### TorchMetrics ECE
```python
from torchmetrics.classification import CalibrationError
ece_metric = CalibrationError(task="binary", n_bins=15, norm="l1")
```

### Temperature Scaling (gpleiss pattern)
```python
optimizer = torch.optim.LBFGS([temperature], lr=0.01, max_iter=200)
def closure():
    loss = nn.CrossEntropyLoss()(logits / temperature, labels)
    loss.backward()
    return loss
optimizer.step(closure)
```

---

## Error Handling

### Dataset Loading
- Retry HuggingFace API with exponential backoff (3 attempts)
- Fallback to cached dataset if available
- Raise SystemExit if dataset unavailable

### Code Generation
- Timeout per problem: 10 seconds
- GPU OOM → batch_size=1, fp16 mode
- Generation failure → mark as incorrect, continue

### Code Execution
- Sandboxed environment (RestrictedPython or subprocess with timeout)
- Timeout: 5 seconds per test case
- Execution failure → mark as incorrect
- Blocked imports: os, subprocess, sys (security)

### Temperature Optimization
- LBFGS convergence check (NLL decrease)
- Fallback to grid search if diverges: T ∈ [0.5, 0.8, 1.0, 1.5, 2.0, 3.0]
- Temperature bounds: [0.1, 10.0] (constraint during optimization)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Dataset + Model Setup | MBPP loading with custom splits, Code Llama loading | 8 | 2+2+2+2 (load+split+verify+model) |
| E2 | Generation Pipeline | Code generation with logit extraction, batch processing | 10 | 3+3+2+2 (gen+logits+batch+cache) |
| E3 | Code Execution | Sandboxed test execution, correctness evaluation | 9 | 3+3+2+1 (sandbox+exec+timeout+label) |
| E4 | Temperature Calibration | LBFGS optimization, convergence tracking | 7 | 2+2+2+1 (fit+track+fallback+bounds) |
| E5 | ECE Evaluation + Figures | ECE computation, 5 visualization figures | 11 | 2+2+2+2+3 (ece+bins+5figs) |

**Total Complexity:** 45  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E2, E3, E5], Low(4-8): [E1, E4]

**Rationale (PoC scope):**
- 5 epic tasks (within 3-5 PoC constraint)
- No ablation modules (baseline vs. calibrated only)
- No hyperparameter search (use gpleiss defaults)
- Single model (Code Llama 7B)
- Single run (seed=42, no cross-validation)

---

## Complexity Breakdown

**Module Size (1-5):**
- Dataset: 2 (simple HF loading + filtering)
- Generation: 3 (model loading + logit extraction)
- Execution: 3 (subprocess sandboxing)
- Calibration: 2 (single parameter optimization)
- Evaluation: 3 (ECE + 5 figures)

**Dependencies (1-5):**
- Dataset: 2 (HF datasets)
- Generation: 3 (HF transformers, torch)
- Execution: 1 (stdlib only)
- Calibration: 2 (torch)
- Evaluation: 3 (torchmetrics, matplotlib)

**Algorithm Complexity (1-5):**
- Dataset: 1 (ID filtering)
- Generation: 3 (autoregressive decoding)
- Execution: 2 (string exec)
- Calibration: 3 (LBFGS optimization)
- Evaluation: 2 (binning + arithmetic)

**Integration (1-5):**
- Dataset: 1 (standalone)
- Generation: 3 (model↔dataset)
- Execution: 2 (generation→execution)
- Calibration: 2 (execution→calibration)
- Evaluation: 3 (all modules→figures)

**Epic Task Complexity Calculation:**
- E1 (Setup): 2+2+1+1 = 6 → 8 (added verification overhead)
- E2 (Generation): 3+3+3+2 = 11 → 10 (reduced batch complexity)
- E3 (Execution): 3+1+2+2 = 8 → 9 (added timeout handling)
- E4 (Calibration): 2+2+3+2 = 9 → 7 (single parameter simpler)
- E5 (Evaluation): 3+3+2+3 = 11 (accurate)

---

## Validation Checks

**Pre-execution:**
- [ ] Code Llama 7B accessible (HF token if gated)
- [ ] MBPP dataset loads (974 problems)
- [ ] Custom splits sum to 390 (195 cal + 195 val)
- [ ] GPU available (check torch.cuda.is_available())

**During execution:**
- [ ] Logit extraction works (test on 1 sample)
- [ ] Code execution sandboxed (no file I/O allowed)
- [ ] Temperature converges (NLL decreases)
- [ ] ECE values in [0,1] range

**Post-execution:**
- [ ] ECE reduction ≥ 30% (GATE)
- [ ] Pass@1 accuracy unchanged (±2%)
- [ ] 5 figures generated in figures/
- [ ] Optimal temperature T* ∈ [0.5, 3.0] (reasonable range)

---

## External Dependencies

**From Previous Hypothesis:** None (foundation hypothesis)

**Third-Party Libraries:**
```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
torchmetrics>=1.2.0
matplotlib>=3.7.0
numpy>=1.24.0
```

---

## Computational Budget

**Hardware:** Single A100 40GB or V100 32GB  
**Estimated Runtime:** ~40 minutes  
**Breakdown:**
- Model loading: 2 min
- Code generation (390 problems): 30 min (5 sec/problem)
- Code execution: 5 min
- Temperature optimization: 1 min (LBFGS)
- ECE evaluation + figures: 2 min

**Memory:**
- Model: ~14GB (fp16)
- Intermediate data: ~2GB (logits + correctness)
- Peak: ~16GB (within A100 40GB)

---

## Gate Decision Logic

```python
ece_reduction = (ece_before - ece_after) / ece_before * 100

if ece_reduction >= 30:
    gate_status = "PASS"
    next_step = "H-M1"
elif 15 <= ece_reduction < 30:
    gate_status = "PARTIAL"
    next_step = "Modify (improve calibration method, 1 attempt)"
else:  # ece_reduction < 15
    gate_status = "FAIL"
    next_step = "Route to Phase 0 (calibration doesn't work)"
```

---

## PoC Simplifications

**What's EXCLUDED (deferred to Phase 5):**
- Cross-validation (single seed=42 run)
- Alternative calibration methods (Vector/Matrix scaling)
- Multiple models (StarCoder2, DeepSeek-Coder)
- HumanEval generalization testing
- Ablation studies (temperature initialization, bin count)
- Statistical significance tests

**What's INCLUDED (minimal PoC):**
- Single baseline (Code Llama 7B, uncalibrated)
- Single proposed method (Temperature scaling)
- Single metric (ECE, 15 bins)
- Fixed configuration (gpleiss defaults)
- Binary gate decision (≥30% reduction)

---

**Document Status:** FINAL  
**Next Phase:** Phase 4 - Implementation (03_prp.md)
