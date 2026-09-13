# Configuration: H-M4 — Step-Matched vs Token-Count-Matched Robustness Check

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr

Applied: dataclass-based experiment config pattern (inherited H-M3)
Applied: checkpoint revision selection pattern (EleutherAI/pythia)
Applied: path-relative result file organization pattern (inherited H-M3)

---

## Codebase Analysis (Serena)

**Project Type:** incremental extension of H-M3
**Status:** H-M3 config verified from 03_config.md; H-M4 is green-field code
**Config Files Found:** `docs/youra_research/h-m3/03_config.md` (reference)
**Pattern Used:** dataclass (matching H-M3 convention)

---

## B-1: CheckpointSelector Config [Complexity: 8, Budget: 2 subtasks]

### C-1-1: Checkpoint Constants Dataclass

```python
from dataclasses import dataclass, field
from typing import List

# Module-level constants (used directly by checkpoint_selector.py)
PILE_TOTAL_TOKENS: float = 244e9
DEDUP_TOTAL_TOKENS: float = 207e9
TOTAL_STEPS: int = 143000
STEP_MATCHED_STEP: int = 143000
MODEL_SIZES: List[str] = ["160m", "410m", "1b", "6.9b"]
AVAILABLE_STEPS: List[int] = [
    1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000,
    2000, 4000, 8000, 16000, 32000, 64000, 128000, 143000
]

@dataclass
class CheckpointConfig:
    pile_total_tokens: float = PILE_TOTAL_TOKENS
    dedup_total_tokens: float = DEDUP_TOTAL_TOKENS
    total_steps: int = TOTAL_STEPS
    step_matched_step: int = STEP_MATCHED_STEP
    model_sizes: List[str] = field(default_factory=lambda: list(MODEL_SIZES))
    available_steps: List[int] = field(default_factory=lambda: list(AVAILABLE_STEPS))
```

YAML schema:
```yaml
checkpoint:
  pile_total_tokens: 244000000000.0
  dedup_total_tokens: 207000000000.0
  total_steps: 143000
  step_matched_step: 143000
  model_sizes: [160m, 410m, 1b, 6.9b]
  available_steps: [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000,
                    2000, 4000, 8000, 16000, 32000, 64000, 128000, 143000]
```

### C-1-2: Token-Per-Step Computation and Validation Config

```python
@dataclass
class TokenRatioValidationConfig:
    # Non-standard: step_matched ratio must be in [1.10, 1.20] (PILE has ~18% more tokens)
    step_matched_ratio_min: float = 1.10
    step_matched_ratio_max: float = 1.20
    # Token-matched ratio tolerance ±3%
    token_matched_ratio_tolerance: float = 0.03
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | CheckpointConfig | Constants dataclass: token counts, steps, model sizes |
| C-1-2 | TokenRatioValidationConfig | Ratio bounds for verify_checkpoint_pair |

---

## B-3: ResultsAggregator Config [Complexity: 7, Budget: 2 subtasks]

### C-3-1: Results Path Config

```python
BASE = "docs/youra_research"

@dataclass
class ResultsConfig:
    hm3_results_dir: str = f"{BASE}/h-m3/results"
    hm4_results_dir: str = f"{BASE}/h-m4/results"
    hm3_differentials_file: str = "accuracy_differentials.json"
    step_matched_raw_file: str = "step_matched_raw.json"
    aggregated_differentials_file: str = "aggregated_differentials.json"
    correlation_comparison_file: str = "correlation_comparison.json"
    gate_verdict_file: str = "gate_verdict.json"
    float_precision: int = 4

    def hm3_path(self, filename: str) -> str:
        import os; return os.path.join(self.hm3_results_dir, filename)

    def hm4_path(self, filename: str) -> str:
        import os; return os.path.join(self.hm4_results_dir, filename)
```

YAML schema:
```yaml
results:
  hm3_results_dir: docs/youra_research/h-m3/results
  hm4_results_dir: docs/youra_research/h-m4/results
  hm3_differentials_file: accuracy_differentials.json
  step_matched_raw_file: step_matched_raw.json
  aggregated_differentials_file: aggregated_differentials.json
  correlation_comparison_file: correlation_comparison.json
  gate_verdict_file: gate_verdict.json
  float_precision: 4
```

### C-3-2: Output Schema for aggregated_differentials.json

```python
# Expected structure of aggregated_differentials.json (for type documentation)
# {
#   "token_matched": {
#     "<model_size>": {
#       "<benchmark>": float  # acc_diff from H-M3
#     }
#   },
#   "step_matched": {
#     "<model_size>": {
#       "<benchmark>": float  # acc_diff from H-M4 eval
#     }
#   }
# }
AGGREGATED_SCHEMA_VERSION: str = "1.0"
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | ResultsConfig | H-M3/H-M4 paths + output file names |
| C-3-2 | AggregatedSchema | aggregated_differentials.json structure doc |

---

## B-6: PipelineOrchestration Config [Complexity: 8, Budget: 2 subtasks]

### C-6-1: CLI Argument Spec

```python
# run.py argparse spec
import argparse

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="H-M4 pipeline: step-matched robustness check")
    p.add_argument("--skip_eval", action="store_true",
                   help="Skip lm-eval inference; use cached step_matched_raw.json")
    p.add_argument("--cache_dir", type=str, default="~/.cache/huggingface",
                   help="HuggingFace model cache directory")
    p.add_argument("--device", type=str, default="cuda",
                   choices=["cuda", "cpu"], help="Inference device")
    p.add_argument("--dtype", type=str, default="float16",
                   choices=["float16", "bfloat16", "float32"], help="Model dtype")
    return p
```

### C-6-2: Experiment-Level Config YAML

```python
from dataclasses import dataclass, field
from typing import Dict, List

BENCHMARKS: List[str] = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
FEW_SHOT: Dict[str, int] = {"mmlu": 5, "hellaswag": 10, "arc_challenge": 25, "winogrande": 5}

@dataclass
class EvalConfig:
    device: str = "cuda"
    dtype: str = "float16"
    cache_dir: str = "~/.cache/huggingface"
    skip_eval: bool = False
    benchmarks: List[str] = field(default_factory=lambda: list(BENCHMARKS))
    few_shot: Dict[str, int] = field(default_factory=lambda: dict(FEW_SHOT))
    bootstrap_n_iterations: int = 10000
    bootstrap_seed: int = 42
```

YAML schema:
```yaml
eval:
  device: cuda
  dtype: float16
  cache_dir: ~/.cache/huggingface
  skip_eval: false
  benchmarks: [mmlu, hellaswag, arc_challenge, winogrande]
  few_shot:
    mmlu: 5
    hellaswag: 10
    arc_challenge: 25
    winogrande: 5
  bootstrap_n_iterations: 10000
  bootstrap_seed: 42
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | CLI args | --skip_eval, --cache_dir, --device, --dtype |
| C-6-2 | EvalConfig | Experiment-level config with benchmarks, few-shot, bootstrap |

---

## B-7: VerificationGateReport Config [Complexity: 7, Budget: 1 subtask]

### C-7-1: Gate Threshold Config

```python
from dataclasses import dataclass
from enum import Enum

class GateVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"

@dataclass
class GateConfig:
    delta_r_threshold: float = 0.05      # |r_step - r_token| must be < 0.05
    bias_delta_threshold: float = 0.01   # |bias_delta| must be < 0.01
    report_format: str = "json"          # output format for gate_verdict.json
```

YAML schema:
```yaml
gate:
  delta_r_threshold: 0.05
  bias_delta_threshold: 0.01
  report_format: json
```

gate_verdict.json output structure:
```json
{
  "delta_r": 0.0,
  "bias_delta": 0.0,
  "delta_r_threshold": 0.05,
  "bias_delta_threshold": 0.01,
  "verdict": "PASS"
}
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | GateConfig | delta_r + bias_delta thresholds, GateVerdict enum |

---

## Full Experiment Config YAML

```yaml
# H-M4 experiment config
# docs/youra_research/h-m4/config.yaml

checkpoint:
  pile_total_tokens: 244000000000.0
  dedup_total_tokens: 207000000000.0
  total_steps: 143000
  step_matched_step: 143000
  model_sizes: [160m, 410m, 1b, 6.9b]
  available_steps: [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000,
                    2000, 4000, 8000, 16000, 32000, 64000, 128000, 143000]

token_ratio_validation:
  step_matched_ratio_min: 1.10
  step_matched_ratio_max: 1.20
  token_matched_ratio_tolerance: 0.03

results:
  hm3_results_dir: docs/youra_research/h-m3/results
  hm4_results_dir: docs/youra_research/h-m4/results
  hm3_differentials_file: accuracy_differentials.json
  step_matched_raw_file: step_matched_raw.json
  aggregated_differentials_file: aggregated_differentials.json
  correlation_comparison_file: correlation_comparison.json
  gate_verdict_file: gate_verdict.json
  float_precision: 4

eval:
  device: cuda
  dtype: float16
  cache_dir: ~/.cache/huggingface
  skip_eval: false
  benchmarks: [mmlu, hellaswag, arc_challenge, winogrande]
  few_shot:
    mmlu: 5
    hellaswag: 10
    arc_challenge: 25
    winogrande: 5
  bootstrap_n_iterations: 10000
  bootstrap_seed: 42

gate:
  delta_r_threshold: 0.05
  bias_delta_threshold: 0.01
  report_format: json
```
