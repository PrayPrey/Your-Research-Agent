# Architecture: h-m1 — Adversarial BAI/Reward Probing

Applied: gradient-reversal adversarial probe pattern (domain-adversarial training, RevGrad).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base_hypothesis folder or existing src/ found under h-m1 or repo root.

---

## Scope

EXISTENCE-style test: does BAI stay decodable (AUROC ≥0.7) from hidden states after GRL removes reward-predictive variance, while reward-probe R² degrades <2%? Single core experiment, minimal architecture.

## File Structure

```
h-m1/code/
  config.py
  extract.py       # hidden-state extraction/caching
  grl.py            # gradient reversal layer
  probes.py         # AdversarialProber (BAI probe + reward probe)
  train.py          # training loop w/ GRL alpha schedule
  evaluate.py       # AUROC / R^2 metrics, comparison report
```

---

## Modules

### Config (`config.py`)

```python
@dataclass
class Config:
    model_name: str            # "meta-llama/Meta-Llama-3-8B" | mistral | qwen2
    layer_idx: int              # transformer layer to probe
    dataset: str                 # "hh-rlhf" | "rewardbench"
    hidden_dim: int
    grl_alpha_max: float = 1.0
    grl_warmup_steps: int = 1000
    lr: float = 1e-3
    batch_size: int = 32
    epochs: int = 10
    cache_dir: str = "./cache"
```

### HiddenStateExtractor (`extract.py`)

**Dependencies**: transformers, Config

```python
class HiddenStateExtractor:
    def __init__(self, cfg: Config): ...
    def extract(self, texts: list[str]) -> Tensor: ...       # [N, hidden_dim]
    def extract_and_cache(self, dataset_split: str) -> Path:  # writes .pt to cache_dir
    def load_cached(self, dataset_split: str) -> tuple[Tensor, Tensor, Tensor]:  # (hidden, bai_labels, reward_labels)
```

### GradientReversalLayer (`grl.py`)

**Dependencies**: pytorch-revgrad (or local autograd.Function if unavailable)

```python
class GradientReversalLayer(nn.Module):
    def __init__(self, alpha: float = 1.0): ...
    def forward(self, x: Tensor) -> Tensor: ...   # identity fwd, -alpha * grad bwd
    def set_alpha(self, alpha: float) -> None: ...

def alpha_schedule(step: int, total_steps: int, alpha_max: float) -> float: ...
    # standard DANN sigmoid ramp: 2*alpha_max/(1+exp(-10*p)) - alpha_max
```

### AdversarialProber (`probes.py`)

**Dependencies**: GradientReversalLayer

```python
class AdversarialProber(nn.Module):
    def __init__(self, hidden_dim: int, grl: GradientReversalLayer): ...
    def forward(self, h: Tensor) -> tuple[Tensor, Tensor]:
        # returns (bai_logits [N], reward_pred [N])
        # bai_head: linear probe on h directly (no GRL)
        # reward_head: linear probe on GRL(h)
    def bai_probe(self, h: Tensor) -> Tensor: ...
    def reward_probe(self, h: Tensor) -> Tensor: ...
```

### Trainer (`train.py`)

**Dependencies**: AdversarialProber, Config, alpha_schedule

```python
def train(cfg: Config, hidden: Tensor, bai_labels: Tensor, reward_labels: Tensor) -> AdversarialProber:
    # joint loss = BCE(bai_logits, bai_labels) + MSE(reward_pred, reward_labels)
    # GRL alpha stepped per alpha_schedule each batch
    ...

def run(cfg: Config) -> Path:  # end-to-end: extract -> train -> save checkpoint
```

### Evaluator (`evaluate.py`)

**Dependencies**: AdversarialProber, sklearn.metrics

```python
def eval_bai_auroc(prober: AdversarialProber, hidden: Tensor, bai_labels: Tensor) -> float: ...
def eval_reward_r2(prober: AdversarialProber, hidden: Tensor, reward_labels: Tensor) -> float: ...
def baseline_reward_r2(hidden: Tensor, reward_labels: Tensor) -> float:
    # non-adversarial linear probe, for <2% degradation comparison
def run_comparison(cfg: Config, checkpoint: Path) -> dict:
    # {"bai_auroc": float, "reward_r2_grl": float, "reward_r2_baseline": float, "r2_degradation_pct": float}
```

---

## Data Flow

1. `extract.py`: raw text (HH-RLHF/RewardBench) → frozen LM forward pass → cached hidden states + BAI labels + reward labels
2. `train.py`: cached tensors → `AdversarialProber` (BAI head direct, reward head through `GradientReversalLayer`) → joint loss, alpha ramped over warmup
3. `evaluate.py`: trained prober → BAI AUROC on held-out split; reward R² (GRL) vs reward R² (non-adversarial baseline) → degradation %
4. Repeat across 3 models × probed layer(s) for robustness

---

## API Contracts

- `HiddenStateExtractor.load_cached` output shapes: `hidden [N, hidden_dim]`, `bai_labels [N]` (binary), `reward_labels [N]` (float)
- `AdversarialProber.forward` always returns `(bai_logits, reward_pred)` — caller applies sigmoid/loss externally
- `alpha_schedule` pure function, no side effects, callable from `train.py` loop
- `evaluate.run_comparison` is the single entry point for hypothesis pass/fail check (AUROC ≥0.7 and R² degradation <2%)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & config | Repo scaffold, Config, cache dir | 4 | 1+1+1+1 |
| A-2 | Hidden state extraction | Load 3 LMs, extract+cache activations for HH-RLHF/RewardBench | 10 | 3+2+3+2 |
| A-3 | Gradient reversal layer | Implement/wrap RevGrad, alpha schedule | 6 | 2+1+2+1 |
| A-4 | Adversarial prober | BAI + reward heads, joint forward | 7 | 2+2+2+1 |
| A-5 | Training loop | Joint loss, alpha ramp, checkpointing | 9 | 2+2+3+2 |
| A-6 | Evaluation pipeline | AUROC, R² (GRL vs baseline), pass/fail report | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-5], Low(4-8): [A-1, A-3, A-4, A-6]
