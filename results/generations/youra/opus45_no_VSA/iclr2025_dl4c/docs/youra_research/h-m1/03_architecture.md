# Architecture: H-M1 (MECHANISM)

**Applied**: MINE (Donsker-Varadhan) statistics-network pattern from gtegner/mine-pytorch (KB had no direct MI matches; used experiment brief's researched GitHub refs instead)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1) — but no actual code found on disk
**Status**: `h-e1/code/` directory does not exist yet (glob returned no files). Only `h-e1/03_architecture.md` spec is available.
**Analyzed Path**: `docs/youra_research/h-e1/code/` (checked, empty/missing)
**Findings**: H-E1 has not been implemented (Phase 4 not yet run for H-E1, or code lives elsewhere). Import paths below are inferred from H-E1's `03_architecture.md` spec and PRD-stated model paths (`h-e1/models/ce_model/`, `h-e1/models/rl_model/`). **Coder must verify these paths exist before running; if H-E1 code/models are missing, this is a blocking dependency (see PRD Risk: "H-E1 models not available").**

---

## File Structure

```
h-m1/code/
  config.py       # MINEConfig, paths to H-E1 models
  traces.py        # refinement trace extraction (feedback, edit, edit_length)
  mine.py          # MINEEstimator, training loop
  embed.py         # text embedding via model encoder (mean pooling)
  stats.py         # edit-length regression control, permutation test, Cohen's d
  visualize.py       # 3 required figures
  run.py           # orchestration: load -> extract -> embed -> train MINE -> stats -> viz -> persist
h-m1/figures/
h-m1/results.json
h-m1/results.csv
```

---

## Modules

### config.py

```python
@dataclass
class MINEConfig:
    ce_model_path: str = "h-e1/models/ce_model"
    rl_model_path: str = "h-e1/models/rl_model"
    tokenizer_id: str = "Salesforce/codet5p-220m"
    embed_dim: int = 256
    hidden_dim: int = 512
    refine_k: int = 3
    seeds: list = field(default_factory=lambda: [42, 43, 44])
    mine_lr: float = 0.001
    mine_batch_size: int = 128
    mine_iters: int = 5000
    ema_weight: float = 0.01
    n_permutations: int = 10000
```

### traces.py (`h-m1/code/traces.py`)

**Dependencies**: config.py, evalplus

```python
def load_problems() -> dict: ...  # evalplus.data.get_human_eval_plus()

def execute_and_get_feedback(code: str, tests: list[str]) -> tuple[bool, str]: ...

def compute_code_diff(prev_code: str, new_code: str) -> str: ...

def extract_refinement_pairs(model, tokenizer, problems: dict, k: int, seed: int) -> list[dict]:
    """Returns list of {feedback, edit, edit_length, problem_id, iteration, seed}."""
```

### embed.py (`h-m1/code/embed.py`)

**Dependencies**: transformers

```python
def embed_text(model, tokenizer, texts: list[str], embed_dim: int = 256) -> torch.Tensor:
    """Mean-pool encoder hidden states, project to embed_dim."""

class Projector(nn.Module):
    def __init__(self, in_dim: int, out_dim: int = 256): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
```

### mine.py (`h-m1/code/mine.py`)

**Dependencies**: torch

```python
class MINEEstimator(nn.Module):
    def __init__(self, feedback_dim: int = 256, code_dim: int = 256, hidden_dim: int = 512): ...
    def forward(self, feedback_emb: torch.Tensor, code_emb: torch.Tensor) -> torch.Tensor: ...
    def estimate_mi(self, feedback_emb: torch.Tensor, code_emb: torch.Tensor,
                     marginal_code_emb: torch.Tensor = None) -> torch.Tensor: ...

def train_mine(estimator: MINEEstimator, feedback_emb: torch.Tensor, code_emb: torch.Tensor,
                cfg: MINEConfig) -> tuple[MINEEstimator, list[float]]:
    """Adam optimizer, EMA bias correction, returns trained estimator + loss history."""
```

### stats.py (`h-m1/code/stats.py`)

**Dependencies**: numpy, scipy

```python
def control_for_edit_length(mi_values: np.ndarray, edit_lengths: np.ndarray,
                             condition_labels: np.ndarray) -> dict:
    """Regress MI~edit_length, residualize, permutation test (10k perms). Returns
    mi_rl_raw, mi_ce_raw, mi_rl_controlled, mi_ce_controlled, observed_diff, p_value, significant."""

def compute_cohens_d(residuals: np.ndarray, condition_labels: np.ndarray) -> float: ...

def evaluate_hypothesis(results: dict) -> dict:
    """Gate: observed_diff > 0 and p_value < 0.05 -> PASS/FAIL."""
```

### visualize.py (`h-m1/code/visualize.py`)

**Dependencies**: stats.py, matplotlib

```python
def plot_mi_comparison_bar(results: dict, out_path: str) -> None: ...
def plot_mi_vs_edit_length(mi_values, edit_lengths, condition_labels, out_path: str) -> None: ...
def plot_permutation_distribution(perm_diffs: np.ndarray, observed_diff: float, out_path: str) -> None: ...
```

### run.py (`h-m1/code/run.py`)

**Dependencies**: all modules above

```python
def load_h_e1_models(cfg: MINEConfig) -> tuple[PreTrainedModel, PreTrainedModel, PreTrainedTokenizer]:
    """Load CE/RL models from h-e1/models/; raise FileNotFoundError with clear message if missing."""

def run_condition(model, tokenizer, cfg: MINEConfig, label: str) -> dict:
    """Per-seed trace extraction -> embed -> train MINE -> return per-sample MI + edit_length."""

def main() -> None:
    """Orchestrate CE + RL conditions, edit-length control, permutation test, viz, persist results.json/csv."""
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (Verification Required)

| Module | Import Path | File Location | Status |
|--------|-------------|----------------|--------|
| CE model | `AutoModelForSeq2SeqLM.from_pretrained("h-e1/models/ce_model")` | `h-e1/models/ce_model/` | NOT FOUND on disk — verify before run |
| RL model | `AutoModelForSeq2SeqLM.from_pretrained("h-e1/models/rl_model")` | `h-e1/models/rl_model/` | NOT FOUND on disk — verify before run |
| Tokenizer | `AutoTokenizer.from_pretrained("Salesforce/codet5p-220m")` | HuggingFace Hub | Available externally |

**Verified from**: attempted glob of `h-e1/code/` — no files found. Paths above sourced from `h-e1/03_architecture.md` spec and PRD FR-1. `run.py::load_h_e1_models` MUST fail fast with an actionable error if these paths are absent (per PRD Risk table).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Config + model loading | MINEConfig, load CE/RL models + tokenizer, path validation | 6 | 1+2+1+2 |
| M-2 | Refinement trace extraction | K=3 self-refine loop, execute+feedback, diff computation, 3 seeds | 12 | 3+2+3+4 |
| M-3 | Text embedding pipeline | Encoder mean-pooling, projection to 256-dim | 5 | 2+2+1+0 |
| M-4 | MINE estimator | 3-layer MLP, Donsker-Varadhan bound, EMA bias correction | 8 | 2+1+4+1 |
| M-5 | MINE training loop | Adam training per condition, 5000 iters, batch 128 | 7 | 1+2+3+1 |
| M-6 | Edit-length regression control | Linear regression, residualization | 5 | 1+1+3+0 |
| M-7 | Permutation test + effect size | 10k permutations, Cohen's d, gate evaluation | 6 | 1+1+3+1 |
| M-8 | Visualization | 3 required figures (bar, scatter, perm histogram) | 5 | 2+1+1+1 |
| M-9 | Orchestration + persistence | run.py main, results.json/csv, 4-hour runtime budget | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-2], Low(4-8): [M-1,M-3,M-4,M-5,M-6,M-7,M-8,M-9]

9 tasks — within MECHANISM range (6-12).
