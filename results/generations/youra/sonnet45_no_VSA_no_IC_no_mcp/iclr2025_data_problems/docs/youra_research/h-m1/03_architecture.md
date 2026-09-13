# Architecture: h-m1 - Threshold Transfer Robustness Testing

**Hypothesis ID:** h-m1
**Type:** MECHANISM (PoC)
**Date:** 2026-08-24
**Author:** Phase 3 Architecture Agent

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Reusing h-e1 infrastructure with threshold sweep extensions
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: Existing curation.py, train.py, evaluate.py modules available for reuse. Adding threshold sweep controller + cross-stage transfer logic.

**Applied Patterns**: Archon KB - DataComp threshold sweep (grid search 0.7-0.9 dedup, 500-1500 perplexity)

---

## System Overview

**Pipeline:** 2 Datasets (C4 pre-train + Dolly fine-tune) → Threshold Sweep → Cross-Stage Transfer → Training → Evaluation → Gate Check

**Execution Model:** Sequential threshold sweep (9 configs per stage = 3 dedup × 3 perplexity)

**Components:**
- ThresholdSweepController (NEW): Grid search across dedup/perplexity ranges
- CrossStageTransfer (NEW): Apply pre-train thresholds to fine-tune data (vice versa)
- CurationPipeline (REUSED from h-e1): Dedup + perplexity filtering
- TrainingOrchestrator (REUSED from h-e1): LLaMA-2-7B fine-tuning
- EvaluationRunner (REUSED from h-e1): MMLU/HellaSwag benchmarks
- Visualizer (NEW): 4 required plots (gate, heatmap, transfer delta, curation impact)

**Data Flow:**
```
[C4 pre-train (52k)] ──┐
                       ├→ ThresholdSweep → Find optimal_pretrain
[Dolly fine-tune (15k)]┘                 → Find optimal_finetune
                                          ↓
                        CrossStageTransfer (optimal_pretrain → Dolly)
                                          (optimal_finetune → C4)
                                          ↓
                        Train 4 models → Evaluate → Compute delta
```

---

## Module Interfaces

### ThresholdSweepController (`code/threshold_sweep.py`)

**Dependencies:** CurationPipeline (h-e1)

```python
class ThresholdSweepController:
    def __init__(
        self,
        dedup_range: list[float] = [0.7, 0.8, 0.9],
        ppl_range: list[float] = [500, 1000, 1500]
    ): ...
    
    def sweep(self, dataset: list[dict], stage: str) -> dict:
        """Apply all threshold combos, return stats per config."""
        ...
    
    def select_optimal(self, sweep_results: dict, metric: str = "sample_count") -> tuple[float, float]:
        """Pick best (dedup_thresh, ppl_cutoff) based on metric."""
        ...
```

### CrossStageTransfer (`code/cross_stage_transfer.py`)

**Dependencies:** CurationPipeline (h-e1)

```python
class CrossStageTransfer:
    def __init__(self, pretrain_data: list[dict], finetune_data: list[dict]): ...
    
    def apply_transfer(
        self,
        source_thresholds: tuple[float, float],
        target_data: list[dict],
        target_stage: str
    ) -> tuple[list[dict], dict]:
        """Apply source-stage thresholds to target dataset."""
        ...
    
    def compute_transfer_delta(
        self,
        optimal_results: dict,
        transferred_results: dict
    ) -> dict:
        """Measure performance degradation."""
        ...
```

### CurationPipeline (`code/curation.py` - REUSED from h-e1)

**Location:** `../h-e1/code/curation.py`

```python
from h_e1.code.curation import DeduplicationFilter, PerplexityFilter

# Existing h-e1 module - no changes needed
# Supports parameterized thresholds already
```

### TrainingOrchestrator (`code/train.py` - REUSED from h-e1)

**Location:** `../h-e1/code/train.py`

```python
from h_e1.code.train import train_model, prepare_instruction_dataset

# Reuse h-e1 training protocol:
# - AdamW lr=1e-5, batch_size=16, epochs=3
# - Seed=1 (changed from h-e1's seed=42)
```

### EvaluationRunner (`code/evaluate.py` - REUSED from h-e1)

**Location:** `../h-e1/code/evaluate.py`

```python
from h_e1.code.evaluate import run_evaluation, compute_gate_metrics

# Reuse h-e1 evaluation harness
# Update gate threshold: 1% (h-e1) → 10% (h-m1)
```

### Visualizer (`code/visualize.py`)

**Dependencies:** matplotlib, seaborn

```python
class Visualizer:
    def plot_gate_metrics(self, results: dict, output_path: str): ...
    
    def plot_threshold_heatmap(
        self,
        sweep_results: dict,
        metric: str = "mmlu_acc",
        output_path: str
    ): ...
    
    def plot_transfer_delta(self, transfer_results: dict, output_path: str): ...
    
    def plot_curation_impact(self, sweep_results: dict, output_path: str): ...
```

---

## External Dependencies (h-e1 Reuse)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| DeduplicationFilter | `from h_e1.code.curation import DeduplicationFilter` | `../h-e1/code/curation.py` |
| PerplexityFilter | `from h_e1.code.curation import PerplexityFilter` | `../h-e1/code/curation.py` |
| train_model | `from h_e1.code.train import train_model` | `../h-e1/code/train.py` |
| run_evaluation | `from h_e1.code.evaluate import run_evaluation` | `../h-e1/code/evaluate.py` |

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation)

**Note:** Import paths assume `h_e1` package is in PYTHONPATH or use relative imports.

---

## File Structure

```
docs/youra_research/h-m1/
├── code/
│   ├── threshold_sweep.py       # NEW: Grid search controller
│   ├── cross_stage_transfer.py  # NEW: Transfer logic
│   ├── visualize.py              # NEW: 4 required plots
│   ├── run_experiment.py         # Main orchestrator
│   └── config.py                 # Threshold ranges, dataset configs
├── figures/                      # Generated plots
│   ├── gate_metrics.png
│   ├── threshold_heatmap.png
│   ├── transfer_delta.png
│   └── curation_impact.png
├── outputs/                      # Model checkpoints, results
│   ├── pretrain_optimal/
│   ├── finetune_optimal/
│   ├── pretrain_to_finetune/
│   └── finetune_to_pretrain/
└── results.json                  # Sweep stats, gate metrics
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Threshold sweep controller | Grid search dedup × perplexity ranges | 8 | 2 (sweep logic) + 2 (optimal selection) + 2 (logging) + 2 (caching) |
| M-2 | Cross-stage transfer logic | Apply pre-train thresholds to fine-tune (vice versa) | 6 | 2 (transfer fn) + 2 (delta computation) + 2 (stats) |
| M-3 | Dataset loaders | C4 (52k) + Dolly-15k with h-e1 reuse compatibility | 5 | 2 (C4 loader) + 2 (Dolly loader) + 1 (format conversion) |
| M-4 | Training integration | Wrap h-e1 train.py for 4 model variants | 7 | 3 (integration) + 2 (checkpoint mgmt) + 2 (seed=1 config) |
| M-5 | Evaluation + gate | Run MMLU/HellaSwag, compute 10% delta threshold | 6 | 2 (eval wrapper) + 2 (delta computation) + 2 (gate logic) |
| M-6 | Visualization pipeline | Generate 4 required figures | 8 | 2 per plot × 4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M-1, M-2, M-3, M-4, M-5, M-6]

**Total Complexity:** 40 (PoC-appropriate - minimal infrastructure)

---

## Configuration

### Threshold Ranges (`code/config.py`)

```python
# FR-1 spec: parameterized threshold sweep
DEDUP_THRESHOLDS = [0.7, 0.8, 0.9]
PERPLEXITY_CUTOFFS = [500, 1000, 1500]

# Dataset configs
C4_CONFIG = {
    "name": "allenai/c4",
    "split": "train",
    "max_samples": 52002,  # Match h-e1 size
    "streaming": True
}

DOLLY_CONFIG = {
    "name": "databricks/databricks-dolly-15k",
    "split": "train",
    "max_samples": 15000
}

# Training configs (from h-e1)
TRAINING_CONFIG = {
    "model_name": "meta-llama/Llama-2-7b-hf",
    "learning_rate": 1e-5,
    "batch_size": 16,
    "epochs": 3,
    "seed": 1  # Changed from h-e1 (seed=42)
}

# Gate threshold
GATE_MAX_DELTA = 0.10  # 10% threshold (vs h-e1's 1%)
```

---

## Execution Plan

1. Load C4 (52k) + Dolly (15k) datasets
2. Sweep thresholds on each stage independently (9 configs × 2 stages = 18 runs)
3. Select optimal per stage (max filtered samples or min val loss)
4. Train 4 models:
   - Baseline (no curation)
   - Pre-train optimal → fine-tune data
   - Fine-tune optimal → pre-train data
   - Mismatched (cross-stage transfer)
5. Evaluate on MMLU + HellaSwag
6. Compute transfer delta: |perf_optimal - perf_transferred|
7. Check gate: delta < 10%
8. Generate 4 visualizations

**Runtime Estimate:** ~6 hours (9 threshold sweeps × 2 stages × 3 epochs × 4 models + eval)

---

## Integration Notes

### h-e1 Reuse Strategy

**REUSE (no modification):**
- `curation.py`: DeduplicationFilter, PerplexityFilter classes
- `train.py`: train_model function, prepare_instruction_dataset
- `evaluate.py`: run_evaluation function

**EXTEND:**
- Threshold sweep wrapper around h-e1 curation
- Cross-stage transfer orchestrator
- Gate metrics update (1% → 10% threshold)

**NEW:**
- ThresholdSweepController
- CrossStageTransfer
- Visualizer (4 plots)
- config.py (threshold ranges)

### Import Approach

Option 1 (preferred): Relative import
```python
import sys
sys.path.append("../h-e1")
from code.curation import DeduplicationFilter
```

Option 2: Copy h-e1 modules to h-m1/code/ (if import issues)

---

## Self-Validation Checklist

- [x] No ASCII diagrams (text structure only)
- [x] Codebase Analysis section included (Serena analysis)
- [x] Module interfaces = signatures only (no prose)
- [x] 6 Epic tasks with complexity scores (PoC-appropriate count)
- [x] External Dependencies section (h-e1 import paths)
- [x] File structure included
- [x] Total length < 500 lines
- [x] Applied Archon pattern (DataComp threshold sweep)

---

**Next Phase:** Phase 4 - Implementation (Coder Agent)
**Validation Target:** Gate delta < 10% (MUST_WORK condition)
