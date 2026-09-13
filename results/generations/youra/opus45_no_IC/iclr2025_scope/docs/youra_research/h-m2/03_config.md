# Configuration: H-M2

**Type:** MECHANISM | **Format:** Python Dataclass

Applied: standard PyTorch/dataclass config pattern (no closely-matching KB hit; H-M1 code style reused for consistency)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Config classes verified from base code (read directly via Read tool — Serena not required since full file was already provided/read)
**Config Files Found**: `h-m1/code/config.py` (DataConfig, ModelConfig, EntropyConfig, GateConfig, ExperimentConfig — all `@dataclass`)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

Field names verified from actual `h-m1/code/config.py`:

```python
# From: h-m1/code/config.py (ACTUAL CODE — copy into h-m2/code/config.py)
DOMAIN_CATEGORIES: dict[str, str] = {
    "Single-Document QA": "single_doc_qa",
    "Multi-Document QA": "multi_doc_qa",
    "Long Structured Data Understanding": "structured_data",
    "Long-dialogue History Understanding": "dialogue",
    "Long In-context Learning": "icl",
    "Code Repository Understanding": "code",
}
DOMAINS: list[str] = list(DOMAIN_CATEGORIES.keys())

@dataclass
class DataConfig:
    dataset_name: str = "THUDM/LongBench-v2"
    samples_per_domain: int = 30
    n_probe_tokens: int = 100
    seed: int = 42

@dataclass
class ModelConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    output_attentions: bool = True
    n_layers: int = 32
    n_heads: int = 32
```

**Verified from**: `h-m1/code/config.py` (actual implementation). `GateConfig` and `ExperimentConfig` field names differ in H-M2 (see below) — H-M2 GateConfig adds direction/min_d fields not present in H-M1's simpler version; not inherited as-is.

---

## A-1: Reuse H-M1 config/data [Complexity: 5, Budget: 4]

**Applied**: dataclass config pattern (H-M1 style)

### Configuration (Python Dataclass)

```python
@dataclass
class StratConfig:
    entropy_matrix_path: str = "../h-m1/code/entropy_matrix.npy"
    domain_means_path: str = "../h-m1/code/domain_means.json"
```

### Subtasks [2/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Copy config.py | Copy DOMAINS, DOMAIN_CATEGORIES, DataConfig, ModelConfig from H-M1 verbatim |
| C-1-2 | Copy data.py | Copy load_longbench_v2, sample_domain, tokenize_probe from H-M1 verbatim |

---

## A-3/A-4: EvictionConfig + StratConfig usage [Complexity: 22 combined, Budget: covers both modules]

**Applied**: H2O official repo eviction pattern (heavy-hitter + recent window, ratio-controlled)

### Configuration (Python Dataclass)

```python
@dataclass
class EvictionConfig:
    retention_ratios: tuple = (1.0, 0.8, 0.4)  # full, moderate, aggressive
    heavy_ratio_frac: float = 0.5   # of retention_ratio; standard H2O 50:50 split
    recent_ratio_frac: float = 0.5
    verify_margin: float = 0.05     # KV size assertion tolerance in verify_h2o_mechanism
```

No non-standard values — 40%/80% retention and 50:50 heavy:recent are H2O paper defaults (per PRD FR-3).

---

## A-2/A-6/A-7: Experiment + Model runtime config [Complexity: 21 combined, Budget: covers inference.py]

**Applied**: batch_size=1 for per-sample eviction control (NFR-2)

### Configuration (Python Dataclass)

```python
@dataclass
class ExperimentConfig:
    output_dir: str = "."
    figure_dir: str = "figures"
    results_path: str = "results.json"
    save_artifacts: bool = True
    dpi: int = 150
    batch_size: int = 1  # per-sample eviction control required
    max_new_tokens: int = 128
    seed: int = 42
```

Reuse `ModelConfig` from H-M1 as-is (see Inherited Configuration above) — no new fields needed.

---

## A-8: Retention + stats gate [Complexity: 9, Budget: same file]

**Applied**: statistical gate pattern (t-test + Cohen's d threshold, consistent with H-M1 GateConfig style)

### Configuration (Python Dataclass)

```python
@dataclass
class GateConfig:
    p_threshold: float = 0.05
    min_d: float = 0.5
    direction: str = "greater"  # high-entropy retention must be > low-entropy retention
```

### Subtasks [2/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | evaluate_gate | Implement p<threshold AND high_mean>low_mean AND d>min_d check |
| C-8-2 | wire into run_experiment | Pass GateConfig into stats.evaluate_gate call |

---

## Full config.py Assembly Order

1. `DOMAIN_CATEGORIES`, `DOMAINS` (copied from H-M1)
2. `DataConfig`, `ModelConfig` (copied from H-M1)
3. `StratConfig` (new)
4. `EvictionConfig` (new)
5. `ExperimentConfig` (new, H-M2-specific fields — not inherited from H-M1's simpler version)
6. `GateConfig` (new, H-M2-specific — adds `min_d`/`direction`, not inherited from H-M1's `significance_threshold`/`effect_size_threshold` pair)
