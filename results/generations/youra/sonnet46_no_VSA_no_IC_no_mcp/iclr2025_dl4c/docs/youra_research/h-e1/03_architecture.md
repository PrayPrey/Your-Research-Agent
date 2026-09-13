---
title: "Architecture: H-E1 — RLEF-Fraction Difficulty-Scaling Existence Proof"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: "2026-08-26"
author: yoon303@ust.ac.kr
---

Applied: Flat-script PoC pattern (no abstractions, single-file-per-concern)
Applied: Subprocess-sandboxed execution pattern (NFR-3 safety requirement)
Applied: Matched-budget controlled comparison pattern (SFT vs RLEF same gradient steps)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Planned module structure follows flat-script PoC pattern: one file per concern, no shared base classes, no abstraction layers.

---

## Module Structure

Applied: Separation of reward execution from training loop (safety + testability)

### data_utils (`code/data_utils.py`)

**Dependencies**: datasets, transformers

```python
def load_apps_train(tokenizer, max_length: int = 1024) -> dict:
    """Returns {'sft': Dataset, 'rlef': Dataset} with test_cases in rlef split."""
    ...

def format_sft_sample(problem: dict, tokenizer) -> dict:
    """Returns {'input_ids', 'labels', 'attention_mask'}."""
    ...

def format_rlef_sample(problem: dict) -> dict:
    """Returns {'prompt': str, 'test_cases': list[tuple[str,str]], 'difficulty': str}."""
    ...
```

### reward (`code/reward.py`)

**Dependencies**: subprocess, tempfile (stdlib only)

```python
def fraction_reward_fn(completions: list[str], prompts: list[str], metadata: list[dict]) -> list[float]:
    """Reward = passed_tests / total_tests. Returns floats in [0.0, 1.0]."""
    ...

def _execute_code(code: str, stdin: str, timeout: float = 3.0) -> str:
    """Subprocess execution. Raises subprocess.TimeoutExpired on timeout."""
    ...
```

### train_sft (`code/train_sft.py`)

**Dependencies**: transformers, torch, data_utils

```python
def run_ceiling_check(model, tokenizer) -> float:
    """Zero-shot HumanEval pass@1 estimate. Switches to 1.3B if >= 0.90."""
    ...

def train(config: dict) -> str:
    """Trains SFT model. Returns checkpoint path. Dumps config to logs/config_dump.json."""
    ...
```

### train_rlef (`code/train_rlef.py`)

**Dependencies**: trl, transformers, torch, data_utils, reward

```python
class RewardMonitorCallback:
    """TRL callback. Logs per-step rewards by difficulty to logs/reward_monitoring.jsonl."""
    def on_step_end(self, args, state, control, **kwargs): ...

def train(config: dict) -> str:
    """Runs GRPOTrainer with fraction_reward_fn. Returns checkpoint path."""
    ...
```

### evaluate (`code/evaluate.py`)

**Dependencies**: subprocess, json, pathlib (stdlib)

```python
def run_harness(checkpoint_path: str, task: str, output_path: str) -> dict:
    """Shells out to bigcode-evaluation-harness. Returns parsed JSON results."""
    ...

def run_all(sft_ckpt: str, rlef_ckpt: str, results_dir: str) -> dict:
    """Runs all 5 benchmarks for both models. Returns nested results dict."""
    ...
```

### analyze (`code/analyze.py`)

**Dependencies**: numpy, scipy, matplotlib, seaborn, json, pathlib

```python
def compute_deltas(results: dict) -> dict:
    """Returns delta_humaneval, delta_lcb_medium_hard, delta_ratio."""
    ...

def bootstrap_ci(results: dict, n_boot: int = 1000, seed: int = 42) -> dict:
    """Returns {'ci': (lo, hi), 'p_value': float, 'ratios': np.ndarray}."""
    ...

def make_figures(results: dict, deltas: dict, bootstrap: dict, figures_dir: str) -> None:
    """Generates all 4 figures: gate_metrics, difficulty_scaling, reward_curve, bootstrap_ratio."""
    ...

def print_gate_decision(deltas: dict, bootstrap: dict) -> bool:
    """Prints PASS/FAIL decision. Returns True if gate condition met."""
    ...
```

---

## File Organization

```
docs/youra_research/h-e1/
├── 02c_experiment_brief.md
├── 03_prd.md
├── 03_architecture.md
├── figures/
│   ├── gate_metrics.png
│   ├── difficulty_scaling.png
│   ├── reward_curve.png
│   └── bootstrap_ratio.png
└── code/
    ├── data_utils.py
    ├── reward.py
    ├── train_sft.py
    ├── train_rlef.py
    ├── evaluate.py
    ├── analyze.py
    └── requirements.txt

checkpoints/
├── sft_baseline/
└── rlef_fraction/

results/h-e1/
└── {model}_{task}.json

logs/
├── reward_monitoring.jsonl
└── config_dump.json
```

---

## Proposed Epic Tasks

Applied: Linear pipeline decomposition (each task produces artifact consumed by next)

| ID | Task | Description | Complexity Score | Breakdown (Size+Dep+Algo+Integ) |
|----|------|-------------|-----------------|----------------------------------|
| E-1 | Data Pipeline | Implement data_utils.py: load APPS, filter ≥1 test, format for SFT and RLEF, tokenize | 9 | 2+2+2+3 |
| E-2 | Reward Function | Implement reward.py: subprocess code execution, fraction computation, timeout/safety | 10 | 2+1+3+4 |
| E-3 | SFT Training | Implement train_sft.py: ceiling check, SFT loop via Trainer, config dump | 11 | 3+3+2+3 |
| E-4 | RLEF Training | Implement train_rlef.py: GRPOTrainer + RewardMonitorCallback + matched steps | 14 | 3+4+4+3 |
| E-5 | Evaluation Runner | Implement evaluate.py: shell bigcode-harness for all 5 benchmarks × 2 models | 9 | 2+3+1+3 |
| E-6 | Analysis & Figures | Implement analyze.py: Δ computation, bootstrap CI, 4 figures, gate decision | 11 | 3+2+3+3 |

**Distribution**: High(14-17): [E-4], Medium(9-13): [E-1, E-2, E-3, E-5, E-6], Low(4-8): []

---

## Module Dependencies

```
data_utils  ←── train_sft
data_utils  ←── train_rlef
reward      ←── train_rlef
evaluate    ←── (bigcode-harness subprocess, no Python import)
analyze     ←── (reads results/*.json and logs/reward_monitoring.jsonl)
```

No circular dependencies. analyze.py is fully decoupled — reads only JSON files.

---

## External Dependencies (requirements.txt)

```
torch>=2.1.0
transformers>=4.40.0
trl>=0.8.6
accelerate>=0.27.0
datasets>=2.18.0
numpy>=1.26.0
scipy>=1.11.0
matplotlib>=3.8.0
seaborn>=0.13.0
pandas>=2.0.0
tqdm>=4.66.0
pyyaml>=6.0
# bigcode-evaluation-harness: git clone + pip install -e ".[vllm]" (pin commit in setup notes)
```
