# Architecture: H-M2 (MECHANISM, SHOULD_WORK)

**Hypothesis:** Bidirectional models (T1-T4) achieve higher held-out IFEval strict accuracy than baselines (B1, B2, B3) by ≥2pp

Applied: reward-model-wrapper-pattern (weighted-sum reward composition, reused from H-M1)
Applied: held-out-eval-harness-pattern (train/test split never seen during training, standard RLHF eval)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m1, VALIDATED)
**Status:** patterns found from base code
**Analyzed Path:** `h-m1/code/`
**Findings:** `h-m1/code/rewards.py` defines `CombinedRewardModel(cfg).compute_reward(prompts, responses, constraints) -> list[Tensor]` with `set_weights(alpha, beta)` — reused unmodified for T1-T4 (only α/β differ). `h-m1/code/train_ppo.py` provides `build_ppo_trainer(cfg)` and `run(cfg)` returning `{"history", "checkpoints"}` — reused unmodified for all 7 variants (B1 skips training, B2/B3 use zeroed reward components). `h-m1/code/data.py` provides `load_ifeval_split(cfg)` (70/30) — reused directly, no re-split needed (must use same seed=1 split as H-M1 to keep test set held-out/consistent). `h-m1/code/config.py` `Config`/`AblationConfig` dataclass pattern extended with `ModelVariant` entries for B1-B3/T1-T4.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| Config | `from h_m1.code.config import Config` | `h-m1/code/config.py` |
| CombinedRewardModel | `from h_m1.code.rewards import CombinedRewardModel` | `h-m1/code/rewards.py` |
| HelpfulnessRewardModel | `from h_m1.code.rewards import HelpfulnessRewardModel` | `h-m1/code/rewards.py` |
| build_ppo_trainer, run | `from h_m1.code.train_ppo import build_ppo_trainer, run` | `h-m1/code/train_ppo.py` |
| load_ultrafeedback, load_ifeval_split | `from h_m1.code.data import load_ultrafeedback, load_ifeval_split` | `h-m1/code/data.py` |
| IFEvalRewardSignal | `from h_e1.code.model import IFEvalRewardSignal` | `h-e1/code/model.py` |

**Verified from**: `h-m1/code/` (actual implementation, not spec)

---

## File Structure

```
h-m2/code/
├── config.py           # ModelVariant registry (B1-B3, T1-T4), imports h-m1 Config
├── train_variants.py    # Orchestrates 7 training runs (B1 skip-train, B2/B3 restricted reward, T1-T4 full)
├── evaluate.py            # IFEval strict/loose accuracy on held-out test split, per variant
├── aggregate.py             # Gate check: max(Ti) vs max(Bi)+2pp, results table
└── visualize.py               # Bar chart (7 variants) + threshold line, constraint-type breakdown
```

---

## Modules

### Config (`config.py`)

**Dependencies**: h_m1.code.config.Config

```python
@dataclass
class ModelVariant:
    name: str              # "B1", "B2", "B3", "T1"..."T4"
    alpha: float
    beta: float
    train: bool             # False for B1 (SFT-only, no PPO)
    reward_mode: str          # "none" | "helpfulness_only" | "quality_only" | "combined"

VARIANTS: list[ModelVariant] = [
    ModelVariant("B1", 0.0, 0.0, train=False, reward_mode="none"),
    ModelVariant("B2", 1.0, 0.0, train=True, reward_mode="helpfulness_only"),
    ModelVariant("B3", 0.0, 0.0, train=True, reward_mode="quality_only"),
    ModelVariant("T1", 0.2, 0.8, train=True, reward_mode="combined"),
    ModelVariant("T2", 0.4, 0.6, train=True, reward_mode="combined"),
    ModelVariant("T3", 0.6, 0.4, train=True, reward_mode="combined"),
    ModelVariant("T4", 0.8, 0.2, train=True, reward_mode="combined"),
]

def build_config(variant: ModelVariant) -> "h_m1.code.config.Config": ...
```

### Train Variants (`train_variants.py`)

**Dependencies**: config, h_m1.code.train_ppo, h_m1.code.rewards, h_m1.code.data

```python
def build_reward_model(variant: ModelVariant, cfg) -> "CombinedRewardModel | None":
    """B1 -> None (no training). B3 -> CombinedRewardModel wired to UltraFeedback
    preference score only (beta=0, ifeval component disabled). B2/T1-T4 -> standard
    CombinedRewardModel.set_weights(alpha, beta)."""
    ...

def run_variant(variant: ModelVariant, ifeval_train, uf_data) -> dict:
    """B1: load base model, no PPO steps. Else: h_m1.code.train_ppo.run(cfg) with
    variant reward model. Returns {"variant": str, "history": list, "checkpoint": str}."""
    ...

def run_all(variants: list[ModelVariant]) -> dict[str, dict]:
    """Sequential execution of 7 variants, checkpoint saved per variant."""
    ...
```

### Evaluate (`evaluate.py`)

**Dependencies**: h_m1.code.data.load_ifeval_split, h_e1.code.model.IFEvalRewardSignal (rule-based checker path)

```python
def evaluate_variant(checkpoint_path: str, ifeval_test: list[dict]) -> dict:
    """Generate responses on held-out ~500 test prompts, run official constraint
    checkers per-prompt. Returns {'strict_accuracy': float, 'loose_accuracy': float,
    'per_constraint_type': dict[str, float]}."""
    ...

def evaluate_all(run_results: dict[str, dict], ifeval_test: list[dict]) -> dict[str, dict]:
    """Maps variant name -> evaluate_variant output for all 7 variants."""
    ...
```

### Aggregate (`aggregate.py`)

**Dependencies**: evaluate.py outputs

```python
def compute_gate(eval_results: dict[str, dict]) -> dict:
    """max(B1,B2,B3) strict_accuracy; for each Ti check > baseline_max + 0.02.
    Returns {'baseline_max': float, 'best_ti': str, 'gate_passed': bool,
    'delta_pp': float}."""
    ...

def results_table(eval_results: dict[str, dict]) -> "pandas.DataFrame":
    """7-row table: variant, strict_acc, loose_acc, alpha, beta."""
    ...
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, aggregate.py outputs

```python
def plot_gate_comparison(eval_results: dict[str, dict], gate: dict, out_dir: str) -> None:
    """Bar chart: strict_accuracy per variant (B1,B2,B3,T1-T4), horizontal line at
    baseline_max + 0.02."""
    ...
def plot_constraint_breakdown(eval_results: dict[str, dict], out_dir: str) -> None:
    """Grouped bars: accuracy per constraint category (format/length/structure) per variant."""
    ...
def plot_alpha_beta_tradeoff(eval_results: dict[str, dict], out_dir: str) -> None:
    """T1-T4 scatter: IFEval strict acc vs helpfulness reward, annotated by (alpha,beta)."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Variant config registry | `config.py`: `ModelVariant`, `VARIANTS` list (7 configs), `build_config` | 5 | 2+1+1+1 |
| C-2 | B1 baseline (SFT-only) | Load base Llama-3-8B-Instruct, no PPO, direct eval path | 4 | 1+1+1+1 |
| C-3 | B2 baseline (AlpacaEval RLHF) | Reuse H-M1 `CombinedRewardModel` with α=1,β=0, run 1000 PPO steps | 6 | 2+3+1+1 (mostly reuse) |
| C-4 | B3 baseline (Quality-only RLHF) | Wire UltraFeedback preference reward only (disable IFEval component), 1000 PPO steps | 9 | 3+3+2+1 |
| C-5 | T1-T4 training runs | `run_variant` loop over T1-T4 α/β configs, reuse H-M1 PPO trainer unmodified | 8 | 2+3+1+2 |
| C-6 | Orchestration | `run_all`: sequential execution of 7 variants, checkpoint management, failure isolation | 7 | 2+2+1+2 |
| C-7 | IFEval held-out eval harness | `evaluate_variant`: generate on ~500 held-out prompts, official constraint checkers, strict/loose acc | 11 | 3+3+3+2 |
| C-8 | Evaluate all variants | `evaluate_all`: run harness across 7 checkpoints, per-constraint-type breakdown | 6 | 2+2+1+1 |
| C-9 | Gate computation | `compute_gate`: baseline max, ≥2pp threshold check, best-Ti identification | 5 | 1+2+1+1 |
| C-10 | Results aggregation | `results_table`: 7-variant summary DataFrame, CSV export | 4 | 1+1+1+1 |
| C-11 | Visualization | `plot_gate_comparison`, `plot_constraint_breakdown`, `plot_alpha_beta_tradeoff` | 7 | 2+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [C-4, C-5, C-7], Low(4-8): [C-1, C-2, C-3, C-6, C-8, C-9, C-10, C-11]
