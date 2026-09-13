# Configuration: H-M4 Differential Benchmark Profiles

**Hypothesis ID:** h-m4 | **Type:** MECHANISM | **Gate:** SHOULD_WORK

Applied: multi-model batch-evaluation config pattern (checkpoint resolution + benchmark paths + effect-size thresholds)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (`h-m3/code/config.py` read directly; no Serena MCP server available, Read tool used instead per fallback rule)
**Config Files Found**: `docs/youra_research/h-m3/code/config.py` (`HM3Config`)
**Pattern Used**: dataclass

---

## A-1: Config + Checkpoint Verification [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch/dataclass defaults; checkpoint path resolution pattern from h-m3 `model_id()` convention

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class HM4Config:
    # Base model
    base_model: str = "meta-llama/Llama-2-7b-hf"

    # Checkpoint resolution
    # Non-standard: h-m3 output_root was "./h-m3_models"; h-m4 points at h-m3's
    # sibling checkpoints dir per PRD FR-1 (../h-m3/checkpoints/{method}_seed_{seed})
    checkpoint_root: str = "../h-m3/checkpoints"
    seeds: List[int] = field(default_factory=lambda: [42, 137, 256, 512, 1024])
    methods: List[str] = field(default_factory=lambda: ["dpo", "rlhf"])

    # Benchmark dataset paths
    truthfulqa_path: str = "truthfulqa/truthful_qa"
    truthfulqa_subset: str = "multiple_choice"
    hh_rlhf_path: str = "Anthropic/hh-rlhf"
    hh_helpful_data_dir: str = "helpful-base"
    hh_harmless_data_dir: str = "harmless-base"

    # Eval settings
    max_length: int = 512
    batch_size: int = 8
    device: str = "cuda"

    # Effect size thresholds (from PRD FR-5 / success criteria)
    d_large_threshold: float = 0.3   # max(|d|) must exceed this
    d_small_threshold: float = 0.15  # min(|d|) must be below this
    profile_corr_threshold: float = 0.8  # distinct profiles if corr < this
    correlation_diff_threshold: float = 0.3  # secondary S2 criterion

    # Output paths
    results_path: str = "./benchmark_results.json"
    analysis_path: str = "./differential_analysis.json"
    profile_plot_path: str = "./profile_comparison.png"

    seed: int = 42
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | HM4Config dataclass | Define config with all fields above |
| C-1-2 | resolve_checkpoint_path | `{checkpoint_root}/{method}_seed_{seed}` per model |
| C-1-3 | verify_checkpoints_exist | Check all 10 paths exist, raise clear error listing missing |
| C-1-4 | RLHF format fallback note | If RLHF checkpoint is full-model (not adapter), branch in loader; log format detected |

---

## A-2: Model Loader [Complexity: 8, Budget: 4 config-relevant]

**Applied**: Reuse h-m3 `load_trained_policy`/`load_tokenizer` — no new config fields needed beyond A-1.

Uses `HM4Config.base_model`, `checkpoint_root`, `seeds`, `methods` from A-1. No additional config class.

### Subtasks [2/2 used, config-scoped]

| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | load_all_models | Iterate seeds x methods, call `load_trained_policy(cfg, resolve_checkpoint_path(...))` |
| C-2-2 | verify_model_integrity | Compare `sum(p.numel() for p in model.parameters())` against expected count |

---

## A-3: Benchmark Loaders [Complexity: 7, Budget: 2 config-relevant]

**Applied**: HuggingFace `datasets.load_dataset` with pinned paths from `HM4Config`.

Uses `truthfulqa_path`, `truthfulqa_subset`, `hh_rlhf_path`, `hh_helpful_data_dir`, `hh_harmless_data_dir`. No additional fields.

### Subtasks [2/2 used, config-scoped]

| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | load_truthfulqa | `load_dataset(cfg.truthfulqa_path, cfg.truthfulqa_subset, split="validation")` |
| C-3-2 | load_hh_helpful/harmless | `load_dataset(cfg.hh_rlhf_path, data_dir=cfg.hh_helpful_data_dir, split="test")` |

---

## A-6: Batch Evaluation Orchestration [Complexity: 10, Budget: 1 config-relevant]

**Applied**: Standard batch loop; writes to `cfg.results_path`.

No new fields — reuses `batch_size`, `max_length`, `results_path`.

### Subtasks [1/1 used, config-scoped]

| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | run_all_evaluations | Loop 10 models x 3 benchmarks, save dict to `cfg.results_path` |

---

## A-7 / A-8: Analysis (Effect Size, Profile Shape, Correlation) [Complexity: 13, Budget: 2 config-relevant]

**Applied**: Cohen's d + independent t-test (scipy.stats.ttest_ind); z-score profile normalization; Pearson correlation.

Uses `d_large_threshold`, `d_small_threshold`, `profile_corr_threshold`, `correlation_diff_threshold`, `analysis_path`. No additional fields.

### Subtasks [2/2 used, config-scoped]

| ID | Subtask | Description |
|----|---------|--------------|
| C-7-1 | analyze_differential_profiles | Compute d/t-test per benchmark; differential = max(d)>threshold AND min(d)<threshold |
| C-8-1 | analyze_profile_shape + cross-correlation | z-norm profiles, correlation vs `profile_corr_threshold`; pairwise diffs vs `correlation_diff_threshold`; write `cfg.analysis_path` |

---

## A-9: Visualization [Complexity: 4, Budget: 1 config-relevant]

**Applied**: matplotlib polar radar chart, output to `cfg.profile_plot_path`.

### Subtasks [1/1 used, config-scoped]

| ID | Subtask | Description |
|----|---------|--------------|
| C-9-1 | plot_profile_comparison | Radar chart DPO vs RLHF across 3 benchmarks, saved to `cfg.profile_plot_path` |

---

## Inherited Configuration (Base Hypothesis: h-m3)

Verified from `docs/youra_research/h-m3/code/config.py` (actual implementation).

```python
# From: h-m3/code/config.py (ACTUAL CODE)
@dataclass
class HM3Config:
    base_model: str = "meta-llama/Llama-2-7b-hf"
    seeds: List[int] = field(default_factory=lambda: [42, 137, 256, 512, 1024])
    methods: List[str] = field(default_factory=lambda: ["dpo", "rlhf"])
    output_root: str = "./h-m3_models"
    seed: int = 42
```

**h-m4 usage**: `base_model`, `seeds`, `methods` field names/defaults match `HM3Config` exactly and are reused as-is in `HM4Config` above. `checkpoint_root` in h-m4 does **not** reuse h-m3's `output_root` ("./h-m3_models") — PRD FR-1 specifies checkpoints live at `h-m3/checkpoints/{method}_seed_{seed}`. **Runtime risk**: h-m3 code contains no RLHF trainer file (only `dpo_train.py`); Task A-1's `verify_checkpoints_exist` must hard-fail with a clear error if `rlhf_seed_*` paths are missing rather than silently skipping.

**External functions reused** (not re-declared in config): `load_tokenizer`, `load_trained_policy`, `get_sequence_logprobs` from `h_m3.model` (see `03_architecture.md` for import paths).
