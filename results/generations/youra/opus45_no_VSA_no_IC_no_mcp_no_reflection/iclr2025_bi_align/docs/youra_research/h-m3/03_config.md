# Configuration: H-M3 (MECHANISM)

**Type:** MECHANISM | **Format:** Python Dataclass (extends H-M1)

Applied: reward-model-wrapper-pattern (weighted-sum α/β reward composition)
Applied: pareto-sweep-evaluation-pattern (multi-config train+eval sweep with gate aggregation)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1, VALIDATED)
**Status**: Config classes verified from actual H-M1 code — **diverges from h-m1/03_config.md spec doc**
**Config Files Found**: `h-m1/code/config.py`
**Pattern Used**: dataclass (nested, module-level preset instances)

Divergences found (actual code vs h-m1 spec doc): `output_dir="checkpoints"` (doc says `"h-m1/checkpoints"`), `max_new_tokens=256` (doc says `512`), `batch_size=8`/`mini_batch_size=2`/`gradient_accumulation_steps=8` (doc says `64`/`8`, no grad-accum field), `LoggingConfig` has no `logger` field, adds `figures_dir="figures"`. H-M3 inherits from **actual code**, not the doc.

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/code/config.py (ACTUAL CODE, verified)
@dataclass
class ModelConfig:
    base_model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    reward_model_id: str = "OpenAssistant/reward-model-deberta-v3-large-v2"
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"

@dataclass
class DataConfig:
    ultrafeedback_id: str = "openbmb/UltraFeedback"
    ultrafeedback_split: str = "train"
    ifeval_id: str = "google/IFEval"
    ifeval_train_ratio: float = 0.7
    ifeval_num_prompts: int = 541
    max_prompt_length: int = 512
    max_new_tokens: int = 256

@dataclass
class RewardConfig:
    alpha: float = 0.5
    beta: float = 0.5
    ifeval_soft_margin: float = 0.1

@dataclass
class PPOConfig:
    learning_rate: float = 1.41e-5
    batch_size: int = 8
    mini_batch_size: int = 2
    gradient_accumulation_steps: int = 8
    ppo_epochs: int = 4
    kl_coeff: float = 0.05
    clip_range: float = 0.2
    value_clip_range: float = 0.2
    total_steps: int = 1000
    seed: int = 42

@dataclass
class LoggingConfig:
    log_interval: int = 10
    checkpoint_interval: int = 250
    output_dir: str = "checkpoints"
    figures_dir: str = "figures"

@dataclass
class ExperimentConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    reward: RewardConfig = field(default_factory=RewardConfig)
    ppo: PPOConfig = field(default_factory=PPOConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
```

Reused unchanged: `CombinedRewardModel.compute_reward/.set_weights` (`rewards.py`), `run_training` (`train_ppo.py`, raises `TrainingDivergenceError` on NaN/KL>10), `run_checkpoint_eval`/`check_gate_metrics` (`evaluate.py`), `IFEvalRewardSignal`/`BaselineChecker` (`ifeval_signal.py`). All six files copied verbatim into `h-m3/code/`.

---

## M3-1: Alpha Sweep Presets [Complexity: 5, Budget: 5]

**Applied**: Standard preset-instance pattern (same style as H-M1's `T1_COMBINED`/`B2_HELPFULNESS_ONLY`)

### Configuration (extends `config.py`)

```python
# New in h-m3/code/config.py — appended after ExperimentConfig
T1 = RewardConfig(alpha=0.2, beta=0.8)
T2 = RewardConfig(alpha=0.4, beta=0.6)
T3 = RewardConfig(alpha=0.6, beta=0.4)
T4 = RewardConfig(alpha=0.8, beta=0.2)
B2 = RewardConfig(alpha=1.0, beta=0.0)  # helpfulness-only baseline

ALPHA_SWEEP_CONFIGS: dict[str, RewardConfig] = {
    "B2": B2, "T1": T1, "T2": T2, "T3": T3, "T4": T4,
}
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M3-1-1 | Copy H-M1 files | `config.py`, `data.py`, `ifeval_signal.py`, `rewards.py` copied verbatim |
| C-M3-1-2 | Copy train_ppo.py | Copied verbatim |
| C-M3-1-3 | Copy evaluate.py | Copied verbatim |
| C-M3-1-4 | ALPHA_SWEEP_CONFIGS | T1-T4, B2 preset dict, appended to config.py |

---

## M3-2/M3-3: AlpacaEval Config [Complexity: 17 combined, Budget: 17]

**Applied**: Standard AlpacaEval CLI wrapper pattern (lc_win_rate via `alpaca_eval.evaluate`)

### Configuration (Python Dataclass)

```python
@dataclass
class AlpacaEvalConfig:
    dataset_id: str = "tatsu-lab/alpaca_eval"
    annotators_config: str = "alpaca_eval_gpt4_turbo_fn"
    openai_api_key_env: str = "OPENAI_API_KEY"
    # Non-standard: PoC uses 100/805 prompts to cap judge cost (~$2.5 vs ~$20)
    poc_sample_limit: int = 100
    full_sample_limit: int = 805
    max_new_tokens: int = 256  # matches DataConfig.max_new_tokens
    batch_size: int = 8
    output_dir: str = "alpaca_eval_results"
```

### Subtasks [8/8 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M3-2-1 | generate_responses | Batch greedy decode, prompt truncation |
| C-M3-2-2 | AlpacaEval format | `{'instruction','output','generator'}` dict list |
| C-M3-2-3 | Checkpoint loading | Load PPO checkpoint for generation |
| C-M3-2-4 | Batching | Batch loop over 100/805 prompts |
| C-M3-3-1 | AlpacaEvalConfig | Dataclass above, wired into `evaluate_alpaca_eval` |
| C-M3-3-2 | CLI/lib wiring | Call `alpaca_eval.evaluate(annotators_config=...)` |
| C-M3-3-3 | LC win rate extraction | Parse `lc_win_rate` from output leaderboard |
| C-M3-3-4 | Cost guard | Assert `poc_sample_limit` used unless `--full` flag passed |

---

## M3-4/M3-5/M3-6/M3-8: Training + Sweep Orchestration [Complexity: 33 combined, Budget: 33]

**Applied**: pareto-sweep-evaluation-pattern (sequential train→eval→aggregate per config)

Uses inherited `PPOConfig`/`ExperimentConfig` unchanged (seed=42, batch_size=8, total_steps=1000). No new config class — `run_sweep` iterates `ALPHA_SWEEP_CONFIGS`.

### Subtasks [8/8 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M3-4-1 | B2 training run | `run_training(base_cfg with reward=B2)` |
| C-M3-4-2 | B2 checkpoint save | Save to `checkpoints/B2/` |
| C-M3-5-1 | T1-T4 loop | Iterate `run_training` for each RewardConfig |
| C-M3-5-2 | Per-config checkpoint | Save to `checkpoints/{T1..T4}/` |
| C-M3-6-1 | run_sweep | Orchestrate train+alpaca_eval+ifeval per config |
| C-M3-6-2 | Results dict assembly | `{name: {'alpaca_lc','ifeval_acc','history','gate'}}` |
| C-M3-8-1 | IFEval cross-eval | `run_checkpoint_eval` on 162-prompt test set, all 5 checkpoints |
| C-M3-8-2 | Gate sanity checks | `check_gate_metrics` (KL<5.0, no NaN) per run |

---

## M3-7: Gate Verification [Complexity: 4, Budget: 4]

**Applied**: FR-5 threshold check, standard mechanism-verification protocol

### Configuration (Python Dataclass)

```python
@dataclass
class GateConfig:
    win_rate_threshold: float = 0.95  # best(T1-T4) >= threshold * B2
```

```python
def verify_gate(b2_win_rate: float, t_results: dict[str, float], cfg: GateConfig = GateConfig()) -> bool:
    best_t = max(t_results.values())
    passed = best_t >= cfg.win_rate_threshold * b2_win_rate
    print(f"B2={b2_win_rate:.4f} best_T={best_t:.4f} threshold={cfg.win_rate_threshold*b2_win_rate:.4f} PASS={passed}")
    return passed
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M3-7-1 | verify_gate | GateConfig + threshold check + logged summary |

---

## M3-9: Visualization Settings [Complexity: 6, Budget: 6]

**Applied**: matplotlib bar/scatter/line chart pattern

### Configuration (Python Dataclass)

```python
@dataclass
class VizConfig:
    figures_dir: str = "figures"  # matches LoggingConfig.figures_dir
    dpi: int = 150
    figsize: tuple[int, int] = (8, 6)
    b2_marker_color: str = "red"
    sweep_color: str = "steelblue"
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M3-9-1 | plot_baseline_vs_sweep_bar | B2 vs T1-T4 AlpacaEval LC bar chart |
| C-M3-9-2 | plot_pareto_frontier | IFEval acc (x) vs AlpacaEval LC (y) scatter, B2 highlighted |
| C-M3-9-3 | plot_alpha_line | Win rate vs α line chart |
| C-M3-9-4 | VizConfig wiring | Shared config across all three plot functions |
