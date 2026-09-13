# Architecture: H-M3 (MECHANISM, SHOULD_WORK)

**Hypothesis:** Bidirectional (multi-objective) models maintain ≥95% of baseline B2 AlpacaEval win rate

Applied: reward-model-wrapper-pattern (weighted-sum reward composition, reused from H-M1)
Applied: pareto-sweep-evaluation-pattern (multi-config train+eval sweep with gate aggregation)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m1, VALIDATED)
**Status:** patterns found from base code — **actual code diverges from h-m1/03_architecture.md spec**
**Analyzed Path:** `h-m1/code/`
**Findings:**
- Actual H-M1 modules are flat (no package prefix): `config.py`, `data.py`, `rewards.py`, `train_ppo.py`, `evaluate.py`, `ifeval_signal.py`, `visualize.py` — NOT the `h_e1.code.*` import path shown in h-m1's own architecture doc.
- `IFEvalRewardSignal` lives in `h-m1/code/ifeval_signal.py` (copied locally from H-E1 to avoid import path conflicts) — import as `from ifeval_signal import IFEvalRewardSignal`, not from h-e1.
- `config.py` uses nested dataclasses (`ExperimentConfig` composing `ModelConfig`, `DataConfig`, `RewardConfig`, `PPOConfig`, `LoggingConfig`) with module-level preset instances `T1_COMBINED`, `B2_HELPFULNESS_ONLY`, `ABLATION_ALPHA_DOMINANT`, `ABLATION_BETA_DOMINANT` — H-M3's α-sweep configs should follow this same preset-instance pattern.
- `rewards.CombinedRewardModel.compute_reward(prompts, responses, constraints) -> list[Tensor]` (trl API) and `.set_weights(alpha, beta)` are directly reusable, no wrapper needed.
- `train_ppo.run_training(cfg, output_dir) -> (history, ifeval_test)` is the reusable training entrypoint; raises `TrainingDivergenceError` on NaN/KL>10.
- `evaluate.py` has `run_checkpoint_eval`, `check_gate_metrics`, `RewardHackingDetector` — reusable for IFEval side of H-M3, but has **no AlpacaEval logic** (new for H-M3).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code, verified — NOT from h-m1 spec)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| ExperimentConfig, RewardConfig, PPOConfig, presets | `from h_m1_config import ExperimentConfig, RewardConfig` (copy config.py locally, see note) | `h-m1/code/config.py` |
| CombinedRewardModel | `from rewards import CombinedRewardModel` (copy rewards.py locally) | `h-m1/code/rewards.py` |
| IFEvalRewardSignal, BaselineChecker | `from ifeval_signal import IFEvalRewardSignal, BaselineChecker` (copy locally) | `h-m1/code/ifeval_signal.py` |
| run_training, build_ppo_trainer | `from train_ppo import run_training, build_ppo_trainer` (copy locally) | `h-m1/code/train_ppo.py` |
| load_ultrafeedback, load_ifeval_split, build_constraints, sample_ppo_batch | `from data import load_ultrafeedback, load_ifeval_split, build_constraints, sample_ppo_batch` (copy locally) | `h-m1/code/data.py` |
| check_gate_metrics, run_checkpoint_eval | `from evaluate import check_gate_metrics, run_checkpoint_eval` (copy locally) | `h-m1/code/evaluate.py` |

**Note:** H-M1's own modules use flat same-directory imports (no package structure), so H-M3 copies the six files verbatim into `h-m3/code/` (matching H-M1's own "copied to avoid import path conflicts" pattern used for `ifeval_signal.py`) rather than cross-directory importing. This mirrors validated project convention. `alpha_sweep.py` and `alpaca_eval.py` are new.

**Verified from**: `h-m1/code/` (actual implementation, not `03_architecture.md` spec)

---

## File Structure

```
h-m3/code/
├── config.py           # copied from h-m1 + AlphaSweepConfig presets (T1-T4)
├── data.py              # copied from h-m1 (unchanged)
├── ifeval_signal.py       # copied from h-m1 (unchanged)
├── rewards.py               # copied from h-m1 (unchanged)
├── train_ppo.py               # copied from h-m1 (unchanged)
├── evaluate.py                  # copied from h-m1 + IFEval strict-acc eval for T1-T4/B2
├── alpaca_eval.py                 # NEW: AlpacaEval LC win-rate evaluation
├── alpha_sweep.py                   # NEW: orchestrates B2 + T1-T4 train+eval, gate check
└── visualize.py                      # NEW: bar chart, Pareto frontier, α line chart
```

---

## Modules

### Config additions (`config.py`)

**Dependencies**: none (copied h-m1 base + new presets)

```python
# Reused as-is: ExperimentConfig, ModelConfig, DataConfig, RewardConfig, PPOConfig, LoggingConfig

# New α-sweep presets (FR-2)
T1 = RewardConfig(alpha=0.2, beta=0.8)
T2 = RewardConfig(alpha=0.4, beta=0.6)
T3 = RewardConfig(alpha=0.6, beta=0.4)
T4 = RewardConfig(alpha=0.8, beta=0.2)
B2 = RewardConfig(alpha=1.0, beta=0.0)  # helpfulness-only baseline

ALPHA_SWEEP_CONFIGS: dict[str, RewardConfig] = {"B2": B2, "T1": T1, "T2": T2, "T3": T3, "T4": T4}
```

### AlpacaEval (`alpaca_eval.py`)

**Dependencies**: alpaca_eval (pip), transformers, config

```python
def generate_responses(checkpoint_path: str, eval_prompts: list[str], cfg: "ExperimentConfig") -> list[dict]:
    """Greedy-decode model_outputs for AlpacaEval format: [{'instruction','output','generator'}]."""
    ...

def evaluate_alpaca_eval(checkpoint_path: str, cfg: "ExperimentConfig", output_dir: str) -> float:
    """Run alpaca_eval.evaluate with annotators_config='alpaca_eval_gpt4_turbo_fn'. Returns lc_win_rate."""
    ...
```

### Alpha Sweep (`alpha_sweep.py`)

**Dependencies**: config, train_ppo, evaluate, alpaca_eval

```python
def run_sweep(configs: dict[str, "RewardConfig"], base_cfg: "ExperimentConfig", output_dir: str) -> dict:
    """
    For each name/reward_cfg in configs: set base_cfg.reward, run_training(),
    evaluate_alpaca_eval(checkpoint), run_checkpoint_eval(IFEval).
    Returns {name: {'alpaca_lc': float, 'ifeval_acc': float, 'history': list, 'gate': dict}}.
    """
    ...

def verify_gate(results: dict) -> bool:
    """FR-5: best(T1..T4) alpaca_lc >= 0.95 * B2 alpaca_lc. Prints B2/best-T/threshold/PASS-FAIL."""
    ...
```

### Evaluate additions (`evaluate.py`)

**Dependencies**: copied h-m1 evaluate.py (run_checkpoint_eval, check_gate_metrics reused unchanged)

No new interfaces — reused as-is for IFEval strict accuracy (FR-4) and per-run gate sanity checks (KL<5.0, no NaN).

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, alpha_sweep results dict

```python
def plot_baseline_vs_sweep_bar(results: dict, out_dir: str) -> None:
    """FR-6: B2 vs T1-T4 AlpacaEval LC win rates bar chart."""
    ...

def plot_pareto_frontier(results: dict, out_dir: str) -> None:
    """FR-6: IFEval strict acc (x) vs AlpacaEval LC (y) scatter, B2 marked."""
    ...

def plot_alpha_line(results: dict, out_dir: str) -> None:
    """FR-6: win rate vs alpha value line chart across T1-T4 + B2."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Copy H-M1 infra | Copy config.py, data.py, ifeval_signal.py, rewards.py, train_ppo.py, evaluate.py into h-m3/code/ verbatim; add ALPHA_SWEEP_CONFIGS presets | 5 | 1+1+1+2 |
| M3-2 | AlpacaEval generation | `generate_responses`: batch greedy decode from checkpoint on 805 AlpacaEval prompts | 8 | 2+2+2+2 |
| M3-3 | AlpacaEval scoring | `evaluate_alpaca_eval`: wire alpaca_eval CLI/lib, GPT-4 turbo judge, LC win rate extraction, cost-guard for PoC (100 prompts) | 9 | 3+3+1+2 |
| M3-4 | B2 baseline training | Run `run_training` with B2 (α=1.0, β=0.0) config, save checkpoint | 6 | 1+2+1+2 |
| M3-5 | T1-T4 sweep training | Loop `run_training` for T1-T4 configs, checkpoint each, collect histories | 10 | 3+3+2+2 |
| M3-6 | Sweep orchestration | `run_sweep`: sequence training + AlpacaEval + IFEval eval per config, assemble results dict | 11 | 3+4+2+2 |
| M3-7 | Gate verification | `verify_gate`: FR-5 threshold check (best T ≥ 0.95×B2), logging per mechanism verification protocol | 4 | 1+1+1+1 |
| M3-8 | IFEval cross-eval | Reuse `run_checkpoint_eval` across all 5 checkpoints (B2, T1-T4) on held-out 162-prompt test set | 6 | 2+2+1+1 |
| M3-9 | Visualization | `plot_baseline_vs_sweep_bar`, `plot_pareto_frontier`, `plot_alpha_line` | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M3-3, M3-5, M3-6], Low(4-8): [M3-1, M3-2, M3-4, M3-7, M3-8, M3-9]
