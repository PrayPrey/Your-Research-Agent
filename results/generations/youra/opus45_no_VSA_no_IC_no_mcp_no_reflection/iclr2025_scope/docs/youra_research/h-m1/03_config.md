# Configuration Design: h-m1

**Version:** 1.0
**Date:** 2026-08-31
**Hypothesis:** h-m1 (MECHANISM)

Applied: Dataclass Configuration Pattern (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: No `config.py` exists in `h-e1/code/` (only `03_config.md` spec + `ExperimentConfig` dataclasses documented there; never implemented in code). Reused code (`duality_conversion.py`, `selective_scan.py`, `data_loader.py`) takes plain function args, not config objects, so no field-name mismatch risk.
**Config Files Found**: None in `h-e1/code/` — only doc spec at `h-e1/03_config.md`
**Pattern Used**: Dataclass (new for h-m1, following h-e1 doc pattern)

---

## Inherited Configuration (Base Hypothesis)

No base `config.py` exists to inherit from. Following h-e1's **documented** schema shape (`03_config.md`) for consistency, since h-e1 function signatures (`duality_init_ssm_from_attention(layer, d_state)`, `selective_scan_ref(x, A, B, C, D, dt)`) take primitives directly — no config class dependency.

Reused defaults carried over: `d_state=64`, `seed=42`, `dtype=float32`, `device=cuda`.

---

## Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ModelConfig:
    bert_name: str = "bert-base-uncased"
    d_model: int = 768
    d_state: int = 64
    num_layers: int = 12

@dataclass
class RandomInitConfig:
    seed: int = 42
    # A ~ N(0,1)/sqrt(d_state), B/C Xavier uniform, D zeros, dt=0.1 (fixed, not tunable)

@dataclass
class DataConfig:
    dataset: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    split: str = "validation"
    max_length: int = 512
    num_samples: int = 500
    batch_size: int = 16  # NFR-1: fits <16GB GPU at 512 tokens

@dataclass
class StatsConfig:
    alpha: float = 0.05  # p-value threshold for gate

@dataclass
class OutputConfig:
    results_dir: str = "results/"
    figures_dir: str = "figures/"
    results_file: str = "comparison_results.json"

@dataclass
class HardwareConfig:
    device: str = "cuda"
    dtype: str = "float32"

@dataclass
class ExperimentConfig:
    name: str = "h-m1-duality-mechanism"
    hypothesis_id: str = "h-m1"
    type: str = "MECHANISM"
    model: ModelConfig = field(default_factory=ModelConfig)
    random_init: RandomInitConfig = field(default_factory=RandomInitConfig)
    data: DataConfig = field(default_factory=DataConfig)
    stats: StatsConfig = field(default_factory=StatsConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
```

Non-standard: `num_samples=500` (not 100 as h-e1 PoC) — PRD FR-7 requires min 500 for statistical validity (NFR-3), unlike h-e1's existence-check default.

---

## Task Configs & Subtasks [4/4 used]

### M-2: Random Init Baseline [Complexity: 7]
Uses `RandomInitConfig` + `ModelConfig.d_state`. No new fields — shapes/scales are fixed per PRD FR-3, not tunable.

| ID | Subtask | Description |
|----|---------|--------------|
| C-M2-1 | random_init_ssm impl | A/B/C/D/dt generation per FR-3 spec |

### M-5: Comparative Evaluation Loop [Complexity: 15]
Uses `DataConfig`, `ModelConfig`. Loop: 12 layers x `num_samples`.

| ID | Subtask | Description |
|----|---------|--------------|
| C-M5-1 | Per-layer loop | Iterate 12 BERT layers x num_samples |
| C-M5-2 | Paired output collection | Store (duality_out, random_out, attn_out) per sample |

### M-6: Statistical Analysis Aggregation [Complexity: 10]
Uses `StatsConfig.alpha` for gate check (p < 0.05).

| ID | Subtask | Description |
|----|---------|--------------|
| C-M6-1 | Aggregation + gate check | paired_stats() + threshold check vs StatsConfig.alpha |

---

*Configuration design for MECHANISM hypothesis*
*Next: Complexity Assessment (Step 6)*
