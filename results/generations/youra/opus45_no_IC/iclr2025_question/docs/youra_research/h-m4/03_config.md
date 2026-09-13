# Config: H-M4 (MECHANISM)

**Applied**: no relevant KB pattern found (irrelevant diffusion/SDXL hits for "DL config patterns"); reusing H-M3's single-dataclass config pattern unchanged.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3)
**Status**: `h-m3/code/config.py` does not exist on disk (glob returned no files) — only `h-m3/03_config.md` spec is available. Field names below verified against that spec, not actual code. **Risk flag**: if Phase 4 has since generated `h-m3/code/config.py` with different field names, Coder must reconcile before use.
**Config Files Found**: None in `h-m3/code/` — spec-only reference (`h-m3/03_config.md`)
**Pattern Used**: Single flat dataclass, mirrors H-M3

---

## M4-1: Config override [Complexity: 6, Budget: 0]

**Applied**: subclass/extend H-M3's `ExperimentConfig` fields via a small standalone dataclass — no new pattern.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class CrossClusterConfig:
    seed: int = 42                                  # inherited (h-m3.ExperimentConfig.seed)
    source_benchmark: str = "trivia_qa"
    target_benchmarks: tuple = ("pop_qa", "halueval_qa")
    cross_cluster_pairs: tuple = (
        ("trivia_qa", "pop_qa"),
        ("trivia_qa", "halueval_qa"),
    )
    js_divergence: dict = None  # set in __post_init__
    sample_size: int = 500                           # PRD FR-1 (differs from H-M3's 1000)
    degradation_threshold: float = 0.15               # PRD gate (differs from H-M3's 0.08)
    h_m3_degradations_path: str = "h-m3/outputs/transfer_results.json"
    h_m3_baseline_degradation: float = 0.032           # PRD Section 10 reference
    outputs_dir: str = "h-m4/outputs"
    figures_dir: str = "h-m4/figures"

    def __post_init__(self):
        if self.js_divergence is None:
            self.js_divergence = {
                ("trivia_qa", "pop_qa"): 0.422,
                ("trivia_qa", "halueval_qa"): 0.526,
            }
```

Reused unchanged from H-M3 spec (import, do not redefine): `calib_split=0.7`, `target_fpr=0.1`, `gen_model="meta-llama/Llama-2-7b-hf"`, `nli_model="microsoft/deberta-v3-large"`, `n_generations=10`, `temperature=1.0`, `n_bootstrap=1000`, `bootstrap_ci=0.95`.

### Subtasks

Budget is 0 — no subtask breakdown for M4-1 through M4-7 (all Low complexity, single config file covers all).

---

## Inherited Configuration (H-M3 Spec Reference)

**Note**: `h-m3/code/config.py` not found on disk; below is transcribed from `h-m3/03_config.md` (spec, not verified code). Field names may change once H-M3 Phase 4 code exists.

```python
# From: h-m3/03_config.md (SPEC ONLY - not verified against code)
@dataclass
class ExperimentConfig:
    seed: int = 42
    outputs_dir: str = "h-m3/outputs"
    figures_dir: str = "h-m3/figures"

@dataclass
class ModelConfig:
    gen_model: str = "meta-llama/Llama-2-7b-hf"
    nli_model: str = "microsoft/deberta-v3-large"
    n_generations: int = 10
    temperature: float = 1.0

@dataclass
class CalibrationConfig:
    calib_split: float = 0.7
    target_fpr: float = 0.1

@dataclass
class EvalConfig:
    n_bootstrap: int = 1000
    bootstrap_ci: float = 0.95
```

H-M4 imports `ModelConfig` and `CalibrationConfig` unchanged; overrides `EvalConfig.degradation_threshold` (0.08 -> 0.15 via `CrossClusterConfig` above) and replaces `ExperimentConfig.sample_size` (1000 -> 500 per PRD FR-1).

**Verified from**: spec doc only (`h-m3/03_config.md`) — `h-m3/code/` directory absent at time of writing.
