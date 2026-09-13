# Architecture: H-M2 DiD Semantic Sensitivity

**Applied**: DiD statistical framework (Callaway-Sant'Anna style bootstrap CI) + ReCode-style perturbation taxonomy (semantic vs. surface-matched control)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Patterns found from base code — reused directly, not re-implemented
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 uses PEFT LoRA on `Salesforce/codet5p-220m`, dataclass `Config`, and existing `execute_and_get_feedback`/`single_shot` functions in `refine.py` with matching signatures. H-M2 reuses these verbatim via import; RL/CE checkpoints exist at `h-e1/checkpoints/rl_final/` and `h-e1/checkpoints/ce_final/` (PEFT adapters).

---

## Directory Structure

```
docs/youra_research/h-m2/
  code/
    config.py          # Config dataclass (paths, eval params)
    models.py           # load RL/CE checkpoints (wraps h-e1 pattern)
    feedback.py          # actual + control feedback generation
    evaluator.py          # single-shot + refine-with-feedback per condition
    did_analysis.py        # DiD contrast + bootstrap CI
    visualize.py          # 2x2 bar, DiD+CI bar, error-type breakdown, effect histogram
    run_experiment.py       # orchestration entrypoint
  outputs/
    results.json
    results.csv
  figures/
    did_bar_chart.png
    did_contrast_ci.png
    error_type_did.png
    effect_size_hist.png
```

External deps (already in H-E1 env): `torch`, `transformers`, `peft`, `evalplus`, `numpy`, `scipy`, `matplotlib`.

---

## External Dependencies (Base Hypothesis: H-E1)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| Config pattern | copy/adapt, not import (separate experiment config) | `h-e1/code/config.py` |
| execute_and_get_feedback | `from h_e1_refine import execute_and_get_feedback` (copied into `feedback.py`, same signature) | `h-e1/code/refine.py` |
| single_shot | `from h_e1_refine import single_shot` (copied into `evaluator.py`, same signature) | `h-e1/code/refine.py` |
| load_humaneval_plus | reused pattern in `models.py`/data load | `h-e1/code/data.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, Python 3.10/3.11 dual bytecode present, confirms executed).

**Checkpoints (actual paths)**:
- RL: `docs/youra_research/h-e1/checkpoints/rl_final/` (PEFT adapter, `adapter_config.json` + `adapter_model.safetensors`)
- CE: `docs/youra_research/h-e1/checkpoints/ce_final/` (same format)
- Base model cache: `docs/youra_research/h-e1/data_cache/models--Salesforce--codet5p-220m/`

Since H-M2 is evaluation-only (no new training), `code/` is a sibling directory reusing H-E1's `data_cache` for the base model (avoid re-download) but writes its own `outputs/`/`figures/`.

---

## Data Flow

```
Config → load RL/CE PeftModel checkpoints (h-e1/checkpoints/{rl,ce}_final)
       → load_humaneval_plus (164 problems, cached from h-e1/data_cache)
       → for each model in {RL, CE}:
           for each problem:
             single_shot generate → execute_and_get_feedback
             if fail:
               actual_feedback = real error message
               control_feedback = feedback_bank[donor_problem] (matched error type, ±20% length)
               refine once with actual → refined_pass_actual
               refine once with control → refined_pass_control
             else: both conditions = pass (already solved)
       → aggregate 4 cells: {RL,CE} x {actual,control} pass@1
       → did_analysis.bootstrap_did_ci (1000 resamples, seeds 42/43/44)
       → visualize (4 figures)
       → save outputs/results.{json,csv}
```

---

## Module Interfaces

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class Config:
    model_id: str = "Salesforce/codet5p-220m"
    base_dir: Path = ...          # h-m2/
    h_e1_dir: Path = ...          # h-e1/ (for checkpoints + data_cache reuse)
    rl_checkpoint: Path = ...     # h_e1_dir/checkpoints/rl_final
    ce_checkpoint: Path = ...     # h_e1_dir/checkpoints/ce_final
    cache_dir: Path = ...         # h_e1_dir/data_cache (reused, no re-download)
    max_new_tokens: int = 512
    temperature: float = 0.0      # greedy per brief
    n_bootstrap: int = 1000
    seeds: tuple[int, ...] = (42, 43, 44)
    alpha: float = 0.05

    @property
    def outputs_dir(self) -> Path: ...
    @property
    def figures_dir(self) -> Path: ...
```

### Models (`models.py`)

**Dependencies**: Config, peft, transformers

```python
def load_eval_model(checkpoint_dir: Path, cfg: Config) -> tuple[PeftModel, PreTrainedTokenizerBase]:
    """AutoModelForSeq2SeqLM.from_pretrained(cfg.model_id) + PeftModel.from_pretrained(base, checkpoint_dir)."""

def load_rl_ce_models(cfg: Config) -> dict[str, tuple[PeftModel, PreTrainedTokenizerBase]]:
    """Returns {"RL": (model, tok), "CE": (model, tok)}."""
```

### Feedback (`feedback.py`)

**Dependencies**: Config (contains `execute_and_get_feedback`, copied from h-e1/refine.py)

```python
def execute_and_get_feedback(code: str, tests: list[str]) -> tuple[float, str]:
    """Reused verbatim from h-e1/code/refine.py."""

def build_feedback_bank(problem_results: list[dict]) -> dict[str, str]:
    """problem_id -> error_msg, from single-shot failures across all problems."""

def classify_error_type(error_msg: str) -> str:
    """AssertionError | TypeError | Timeout | Other, via string match."""

def get_control_feedback(problem_id: str, feedback_bank: dict[str, str],
                          error_types: dict[str, str], rng: random.Random) -> str:
    """Donor from different problem, same error_type, len within ±20%; else random donor."""
```

### Evaluator (`evaluator.py`)

**Dependencies**: Config, models, feedback (contains `single_shot`, copied from h-e1/refine.py)

```python
def single_shot(model, tokenizer, prompt: str, cfg: Config) -> str:
    """Reused verbatim from h-e1/code/refine.py."""

def refine_with_feedback(model, tokenizer, prompt: str, code: str,
                          feedback_text: str, tests: list[str], cfg: Config) -> bool:
    """One refine step using given feedback (actual or control); returns pass/fail."""

def evaluate_condition(model, tokenizer, problems: dict, feedback_bank: dict,
                        error_types: dict, condition: str, cfg: Config, seed: int) -> list[dict]:
    """Runs single-shot + conditional refine for all problems; condition in {"actual","control"}.
    Returns list of {problem_id, model_name, condition, single_shot_pass, refined_pass}."""

def run_all_conditions(models: dict, problems: dict, cfg: Config) -> list[dict]:
    """Orchestrates RL/CE x actual/control x seeds; builds feedback_bank once from single-shot pass."""
```

### DiD Analysis (`did_analysis.py`)

**Dependencies**: numpy, scipy

```python
def compute_did_contrast(results: list[dict]) -> float:
    """(RL_actual - RL_control) - (CE_actual - CE_control), mean of refined_pass."""

def bootstrap_did_ci(results: list[dict], n_bootstrap: int, alpha: float,
                      seed: int) -> dict:
    """Returns {did_contrast, ci_lower, ci_upper, significant, boot_samples}."""

def per_error_type_did(results: list[dict], error_types: dict) -> dict[str, float]:
    """DiD contrast computed within each error category."""

def per_problem_effect_sizes(results: list[dict]) -> list[float]:
    """Per-problem (RL_diff - CE_diff) for effect size histogram."""
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, did_analysis outputs

```python
def plot_2x2_bar(cell_means: dict, out_path: Path) -> None: ...
def plot_did_ci(did_result: dict, out_path: Path) -> None: ...
def plot_error_type_did(error_type_did: dict[str, float], out_path: Path) -> None: ...
def plot_effect_hist(effects: list[float], out_path: Path) -> None: ...
```

### Orchestration (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """Load config, models, data -> run_all_conditions -> bootstrap_did_ci ->
    save results.json/csv -> generate 4 figures."""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Config + models | Config dataclass, load_rl_ce_models via PeftModel | 6 | 2+1+2+1 |
| M2-2 | Feedback bank | execute_and_get_feedback reuse, error classification, control matching | 8 | 3+2+2+1 |
| M2-3 | Single-shot eval | single_shot reuse, run over 164 problems x 2 models | 5 | 2+1+1+1 |
| M2-4 | Refine w/ feedback | refine_with_feedback for actual/control conditions | 7 | 3+2+1+1 |
| M2-5 | Full evaluation loop | run_all_conditions across seeds (42,43,44), 4 cells | 8 | 3+3+1+1 |
| M2-6 | DiD + bootstrap | compute_did_contrast, bootstrap_did_ci (1000 resamples) | 7 | 2+2+2+1 |
| M2-7 | Error-type + effect size stats | per_error_type_did, per_problem_effect_sizes | 5 | 2+1+1+1 |
| M2-8 | Visualization | 4 required figures | 6 | 2+2+1+1 |
| M2-9 | Orchestration + results export | run_experiment.py, results.json/csv | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M2-1, M2-2, M2-3, M2-4, M2-5, M2-6, M2-7, M2-8, M2-9]
