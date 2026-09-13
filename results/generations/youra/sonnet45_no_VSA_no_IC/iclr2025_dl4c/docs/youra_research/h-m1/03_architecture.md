# System Architecture: h-m1 Feedback Efficiency Mechanism

**Date:** 2026-08-19  
**Hypothesis:** h-m1 (MECHANISM - Capacity limits feedback efficiency)  
**Source Documents:** 03_prd.md, 02c_experiment_brief.md  
**Base:** h-e1 (binary/error-type RLVR)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** patterns found from h-e1 code  
**Analyzed Path:** docs/youra_research/h-e1/code/  
**Findings:** Modular structure with dataset.py, model.py, sandbox.py, train.py, eval.py, validate.py. Reuse all modules, extend sandbox.py with trace depth extraction.

---

## Architecture Overview

Extends h-e1 with error+trace feedback condition. Reuses SFT/Binary/Error-Type checkpoints. Adds: trace depth extraction in sandbox, error+trace GRPO trainer, efficiency frontier analysis.

**Pipeline:** Load h-e1 checkpoints → Train Error+Trace GRPO (500 steps) → Evaluate 4 conditions → Compute efficiency (pp/bit) → Statistical tests → Gate verdict

---

## Module Specifications

### 1. Sandbox Extension (`sandbox_trace.py`)

**Dependencies:** h-e1 sandbox.py, traceback, sys

```python
from h_e1.code.sandbox import ExecutionSandbox

class TraceSandbox(ExecutionSandbox):
    def extract_stack_depth(self, exc_info: tuple) -> int:
        """Extract stack trace depth from exception."""
        # Returns: depth in [0-9], clamped
        
    def compute_error_trace_reward(self, code: str, test: str, entry_point: str) -> float:
        """Execute code, return error_type_reward × depth_penalty."""
        # error_type from parent class compute_error_type_reward
        # depth from extract_stack_depth
        # depth_penalty = 1.0 - (depth / 20.0), clamped [0.5, 1.0]
        # Returns: float in [0.0, 1.0]
```

---

### 2. GRPO Error+Trace Trainer (`train_error_trace.py`)

**Dependencies:** h-e1 train.py, sandbox_trace.py, torch, trl

```python
from h_e1.code.train import GRPOTrainer
from sandbox_trace import TraceSandbox

class ErrorTraceTrainer(GRPOTrainer):
    def __init__(self, config: dict, sandbox: TraceSandbox): ...
    
    def train(self, policy_model, ref_model, tokenizer, prompts, test_suites) -> str:
        """GRPO training with error+trace rewards."""
        # Same as h-e1 GRPO but uses sandbox.compute_error_trace_reward
        # 500 steps, batch=4 problems × 4 samples, KL coef=0.1
        # Log gradient variance every 10 steps
        # Returns: checkpoint path
```

---

### 3. Efficiency Analysis (`analysis_efficiency.py`)

**Dependencies:** numpy, scipy, matplotlib

```python
def compute_efficiency(pass_at_1: float, sft_baseline: float, bits: float) -> float:
    """Efficiency = (pass@1 - SFT) × 100 / bits."""
    # Returns: pp/bit
    
def pairwise_ttests(efficiencies: dict) -> dict:
    """Binary vs Error-Type, Error-Type vs Trace, Binary vs Trace."""
    # Bonferroni correction: α = 0.0167
    # Returns: {comparison: p_value}
    
def bootstrap_ci(pass_at_1_samples: list, sft_baseline: float, bits: float) -> tuple:
    """1000 bootstrap samples for 95% CI."""
    # Returns: (lower, upper)
    
def plot_efficiency_frontier(results: dict, output_path: str):
    """Bar chart: Binary, Error-Type, Error+Trace efficiency."""
    # X-axis: Granularity, Y-axis: pp/bit
    # Error bars: Bootstrap CI
    # Threshold lines: 7, 5, 2.5 pp/bit
```

---

### 4. Orchestrator Extension (`run_experiment.py`)

**Dependencies:** h-e1 modules, train_error_trace.py, analysis_efficiency.py

```python
def main(hypothesis_id: str):
    # 1. Load h-e1 checkpoints (SFT, Binary, Error-Type)
    # 2. Train Error+Trace GRPO (new)
    # 3. Evaluate 4 checkpoints
    # 4. Compute efficiency for each
    # 5. Pairwise statistical tests
    # 6. Plot efficiency frontier
    # 7. Gate verdict (monotonic decrease + target ranges)
    # 8. Update verification_state.yaml
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| HumanEvalLoader | `from h_e1.code.dataset import HumanEvalLoader` | `h-e1/code/dataset.py` |
| ModelManager | `from h_e1.code.model import ModelManager` | `h-e1/code/model.py` |
| ExecutionSandbox | `from h_e1.code.sandbox import ExecutionSandbox` | `h-e1/code/sandbox.py` |
| GRPOTrainer | `from h_e1.code.train import GRPOTrainer` | `h-e1/code/train.py` |
| Evaluator | `from h_e1.code.eval import Evaluator` | `h-e1/code/eval.py` |

**Verified from:** h-e1/code/ (actual implementation)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | Trace sandbox | Extend sandbox.py with stack depth extraction + error+trace reward | 11 | Module(3)+Deps(2)+Algo(4)+Integ(2) |
| M1-2 | Error+trace trainer | GRPO trainer using trace sandbox, gradient variance logging | 14 | Module(4)+Deps(3)+Algo(4)+Integ(3) |
| M1-3 | Efficiency analysis | Compute pp/bit, pairwise t-tests, bootstrap CI, frontier plot | 12 | Module(3)+Deps(2)+Algo(5)+Integ(2) |
| M1-4 | Checkpoint loading | Load h-e1 SFT/Binary/Error-Type checkpoints, smoke test | 7 | Module(2)+Deps(2)+Algo(1)+Integ(2) |
| M1-5 | Evaluation pipeline | Run greedy eval on 4 checkpoints (164 problems each) | 9 | Module(2)+Deps(2)+Algo(3)+Integ(2) |
| M1-6 | Statistical tests | Bonferroni correction, pairwise comparisons, gate logic | 10 | Module(2)+Deps(2)+Algo(4)+Integ(2) |
| M1-7 | Validation report | Gate verdict, efficiency table, risk checks (skew, saturation) | 8 | Module(2)+Deps(1)+Algo(3)+Integ(2) |
| M1-8 | Gradient variance | Log per-batch variance, compute mean over training, CSV export | 9 | Module(2)+Deps(2)+Algo(3)+Integ(2) |

**Distribution:** High(14-17): [M1-2], Medium(9-13): [M1-1, M1-3, M1-5, M1-6, M1-8], Low(4-8): [M1-4, M1-7]

---

## Data Flow

```
h-e1 checkpoints/
├── sft/ ──────────┐
├── binary/ ───────┤
└── error_type/ ───┼─► Evaluator ──► pass@1 (4 conditions)
                   │                     │
                   │                     ▼
New Training:      │          Efficiency Computation
Prompts ───┐       │          (pass@1 - SFT) / bits
           │       │                     │
           ▼       │                     ▼
TraceSandbox ──────┤          Pairwise t-tests
  ├─ extract_depth │          (Bonferroni α=0.0167)
  └─ error×penalty │                     │
           │       │                     ▼
           ▼       │          Efficiency Frontier Plot
ErrorTraceTrainer  │          (bar chart + CI)
  ├─ GRPO 500 steps│                     │
  ├─ grad variance │                     ▼
  └─ checkpoint ───┘          Gate Verdict
                              (monotonic + ranges)
```

---

## Configuration

Reuse h-e1 config.yaml, add:

```yaml
error_trace:
  depth_buckets: 10  # [0-9]
  depth_penalty_divisor: 20.0
  min_penalty: 0.5
  max_penalty: 1.0

efficiency:
  bits_per_condition:
    binary: 1.0
    error_type: 2.32
    error_trace: 5.64
  target_ranges:
    binary: [7.0, 100.0]
    error_type: [4.0, 6.0]
    error_trace: [2.0, 3.0]

gate:
  bonferroni_alpha: 0.0167
  bootstrap_samples: 1000
```

---

## File Structure

```
h-m1/
├── code/
│   ├── sandbox_trace.py          # NEW: Trace depth + reward
│   ├── train_error_trace.py      # NEW: GRPO trainer
│   ├── analysis_efficiency.py    # NEW: Efficiency computation
│   ├── run_experiment.py         # NEW: Orchestrator
│   ├── config.yaml               # EXTEND: h-e1 config
│   └── requirements.txt          # REUSE: h-e1 deps
├── checkpoints/
│   └── error_trace/              # NEW: Error+trace checkpoint
├── figures/
│   ├── efficiency_frontier.png   # NEW: Mandatory
│   ├── gradient_variance.png     # NEW: Optional
│   └── error_depth_dist.png      # NEW: Optional
└── logs/
    ├── gradient_variance.csv     # NEW: Per-batch variance
    └── efficiency_metrics.json   # NEW: Final results
```

---

## Resource Requirements

**Training:** 2 GPU-hours (Error+Trace only, reuses h-e1 checkpoints)  
**Evaluation:** 0.5 GPU-hours (4 checkpoints × 164 problems)  
**Total:** 2.5 GPU-hours

**VRAM:** <10GB (CodeGen-350M + LoRA)  
**Storage:** 1GB (error+trace checkpoint) + 0.1GB (logs)

---

## Error Recovery

- Checkpoint corruption → Retry load 3x, fallback to re-train from h-e1 SFT
- CUDA OOM → Reduce batch to 2 problems × 4 samples
- Error distribution skew → Compute effective entropy, report in validation
- Depth saturation → Histogram depths, adjust bits if >80% at depth 0-1

---

**Architecture Version:** 1.0  
**Next Phase:** Phase 4 implementation (3 days: trace sandbox → training → evaluation)
