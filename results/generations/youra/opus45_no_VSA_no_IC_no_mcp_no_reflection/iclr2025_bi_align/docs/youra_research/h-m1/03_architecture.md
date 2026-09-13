# Architecture: H-M1 (MECHANISM, MUST_WORK)

**Hypothesis:** Combined reward R = α·R_AlpacaEval + β·R_IFEval can be PPO-optimized without divergence/reward hacking

Applied: reward-model-wrapper-pattern (weighted-sum reward composition over frozen policy outputs)
Applied: trl-ppo-trainer-pattern (custom `reward_model` callable, KL-anchored frozen reference)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e1, VALIDATED)
**Status:** patterns found from base code
**Analyzed Path:** `h-e1/code/`
**Findings:** `h-e1/code/model.py` defines `IFEvalRewardSignal(nn.Module)` with `forward(response, constraints) -> torch.Tensor`, verified differentiable via soft length/keyword/format/structural checks. `h-e1/code/data.py` provides `load_ifeval(cfg)` and `parse_constraints(example)` — reused as-is for prompt/constraint sourcing in H-M1's data pipeline. `config.py` pattern (single `@dataclass Config`) reused/extended for PPO hyperparameters.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| IFEvalRewardSignal | `from h_e1.code.model import IFEvalRewardSignal` | `h-e1/code/model.py` |
| load_ifeval | `from h_e1.code.data import load_ifeval` | `h-e1/code/data.py` |
| parse_constraints | `from h_e1.code.data import parse_constraints` | `h-e1/code/data.py` |

**Verified from**: `h-e1/code/` (actual implementation, not spec)

---

## File Structure

```
h-m1/code/
├── config.py          # PPO + reward hyperparameters (extends h-e1 Config pattern)
├── data.py             # UltraFeedback + IFEval loading, prompt sampling, 70/30 split
├── rewards.py           # CombinedRewardModel wrapping H-E1 IFEvalRewardSignal + helpfulness RM
├── train_ppo.py          # trl.PPOTrainer training loop, checkpointing, logging
├── evaluate.py             # checkpoint eval: IFEval strict acc, reward-hacking correlation
└── visualize.py             # reward trajectory / KL / correlation plots
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class Config:
    base_model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    helpfulness_rm_id: str = "OpenAssistant/reward-model-deberta-v3-large-v2"
    alpha: float = 0.5
    beta: float = 0.5
    learning_rate: float = 1.41e-5
    batch_size: int = 64
    mini_batch_size: int = 8
    ppo_epochs: int = 4
    kl_coeff: float = 0.05
    clip_range: float = 0.2
    vf_clip_range: float = 0.2
    total_steps: int = 1000
    checkpoint_every: int = 250
    log_every: int = 10
    seed: int = 1
    output_dir: str = "h-m1/figures"
    checkpoint_dir: str = "h-m1/checkpoints"

@dataclass
class AblationConfig(Config):
    """alpha/beta overrides for B2, T1, ablations A-D per FR-5/FR-6."""
    name: str = "T1-Combined"
```

### Data (`data.py`)

**Dependencies**: Config, datasets, h-e1.data

```python
def load_ultrafeedback(cfg: Config) -> list[dict]: ...
def load_ifeval_split(cfg: Config) -> tuple[list[dict], list[dict]]:
    """70/30 train/test via h_e1.code.data.load_ifeval + parse_constraints."""
    ...
def sample_ppo_prompts(uf_data: list[dict], ifeval_train: list[dict], batch_size: int, seed: int) -> list[dict]: ...
```

### Rewards (`rewards.py`)

**Dependencies**: Config, torch, transformers, h-e1.model.IFEvalRewardSignal

```python
class HelpfulnessRewardModel(nn.Module):
    def __init__(self, model_id: str): ...
    def forward(self, prompts: list[str], responses: list[str]) -> torch.Tensor: ...

class CombinedRewardModel(nn.Module):
    def __init__(self, cfg: Config):
        """Wraps HelpfulnessRewardModel + h_e1.code.model.IFEvalRewardSignal."""
        ...
    def forward(self, prompts: list[str], responses: list[str], constraints: list[list[dict]]) -> dict:
        """Returns {'combined': Tensor, 'helpfulness': Tensor, 'ifeval': Tensor}"""
        ...
    def set_weights(self, alpha: float, beta: float) -> None: ...
```

### Train PPO (`train_ppo.py`)

**Dependencies**: Config, data, rewards, trl, transformers

```python
def build_ppo_trainer(cfg: Config) -> "trl.PPOTrainer":
    """Policy + frozen reference model (same base, no grad), trl.PPOConfig from cfg."""
    ...
def training_step(trainer, reward_model: CombinedRewardModel, batch: dict) -> dict:
    """Generate rollout -> CombinedRewardModel.forward -> trainer.step -> stats dict."""
    ...
def run(cfg: Config) -> dict:
    """
    Loop total_steps: training_step, log every log_every (reward/mean,
    reward/helpfulness, reward/controllability, objective/kl, ppo/policy_loss,
    ppo/value_loss), checkpoint every checkpoint_every.
    Returns: {"history": list[dict], "checkpoints": list[str]}
    """
    ...
```

### Evaluate (`evaluate.py`)

**Dependencies**: Config, data, rewards, checkpoints

```python
def evaluate_checkpoint(checkpoint_path: str, ifeval_test: list[dict], cfg: Config) -> dict:
    """IFEval strict accuracy on held-out 30%."""
    ...
def detect_reward_hacking(train_history: list[dict], eval_results: list[dict]) -> dict:
    """Pearson r between training reward and eval metric per checkpoint; flag if r < 0.7."""
    ...
def check_gate_metrics(train_history: list[dict]) -> dict:
    """positive trend both components, max KL < 5.0, zero NaN/Inf -> pass/fail booleans."""
    ...
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, train/eval outputs

```python
def plot_reward_trajectory(history: list[dict], out_dir: str) -> None: ...
def plot_kl_divergence(history: list[dict], out_dir: str) -> None: ...
def plot_reward_hacking_correlation(train_history: list[dict], eval_results: list[dict], out_dir: str) -> None: ...
def plot_baseline_comparison(runs: dict[str, list[dict]], out_dir: str) -> None:
    """B1-SFT vs B2-Helpfulness-Only vs T1-Combined."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Config setup | `config.py`: PPO hyperparams, AblationConfig variants (T1, B2, α/β sweeps) | 6 | 2+1+1+2 |
| B-2 | Data pipeline | `data.py`: UltraFeedback load, IFEval 70/30 split (reuse h-e1 loaders), prompt sampler | 9 | 3+3+1+2 |
| B-3 | Helpfulness reward model | `HelpfulnessRewardModel`: load DeBERTa RM, score prompt+response pairs | 8 | 3+2+1+2 |
| B-4 | Combined reward wrapper | `CombinedRewardModel`: integrate H-E1 `IFEvalRewardSignal` + helpfulness RM, weighted sum, component logging | 11 | 3+4+2+2 |
| B-5 | PPO trainer setup | `build_ppo_trainer`: trl.PPOTrainer + PPOConfig, frozen reference model wiring | 10 | 3+3+2+2 |
| B-6 | PPO training loop | `training_step`/`run`: rollout generation, reward computation, trainer.step, metric logging every 10 steps | 15 | 4+4+4+3 |
| B-7 | Checkpointing | Save/restore full optimizer state every 250 steps within `run` | 6 | 2+1+1+2 |
| B-8 | Baseline runs (B1, B2) | Execute B1-SFT (no RL) and B2-Helpfulness-Only (α=1,β=0) configs via existing pipeline | 7 | 2+2+1+2 |
| B-9 | Checkpoint evaluation | `evaluate_checkpoint`: IFEval strict accuracy on held-out test at steps 250/500/750/1000 | 9 | 3+2+2+2 |
| B-10 | Reward hacking detection | `detect_reward_hacking`, `check_gate_metrics`: correlation + gate threshold checks (KL<5.0, no NaN, positive trend) | 8 | 2+2+2+2 |
| B-11 | Ablation runs | Execute α/β variants (0.7/0.3, 0.3/0.7) and dynamic scheduling variant | 8 | 2+2+2+2 |
| B-12 | Visualization | `visualize.py`: reward trajectory, KL plot, hacking correlation, baseline comparison charts | 7 | 2+1+1+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [B-6], Medium(9-13): [B-2, B-4, B-5, B-9], Low(4-8): [B-1, B-3, B-7, B-8, B-10, B-11, B-12]
