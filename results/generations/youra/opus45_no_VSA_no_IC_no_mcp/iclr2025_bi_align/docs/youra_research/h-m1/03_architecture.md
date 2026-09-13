# Architecture: H-M1 RLHF Reward Model Smoothing

**Type:** MECHANISM | **Epic Range:** 6-12 tasks

Applied: TRL RewardTrainer + PEFT LoRA reward-head fine-tuning pattern
Applied: Bradley-Terry preference loss with center_rewards_coefficient regularization

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base_hypothesis code reuse (h-e1 is EXISTENCE type, not code-shared).

---

## File Structure

```
h-m1/code/
  config.py
  data.py
  model.py
  train.py
  metrics/
    gradient.py
    distribution.py
    interpolation.py
  baselines.py
  evaluate.py
  visualize.py
```

---

## Modules

### Config (`config.py`)

**Dependencies**: None

```python
@dataclass
class HM1Config:
    base_model: str = "meta-llama/Llama-2-7b-hf"
    dataset_name: str = "Anthropic/hh-rlhf"
    max_length: int = 512
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 1e-4
    num_train_epochs: int = 1
    center_rewards_coefficient: float = 0.01
    output_dir: str = "./reward_model_h-m1"
    seed: int = 42
    test_sample_size: int = 5000
    interpolation_pair_count: int = 500
    n_interp_steps: int = 10

def get_reward_config(cfg: HM1Config) -> "trl.RewardConfig": ...
def get_peft_config(cfg: HM1Config) -> "peft.LoraConfig": ...
```

### Data (`data.py`)

**Dependencies**: config.py

```python
def load_hh_rlhf_splits(cfg: HM1Config) -> "DatasetDict":
    """Loads Anthropic/hh-rlhf, splits 90/5/5 train/val/test."""

def preprocess_for_reward_trainer(dataset: "Dataset", tokenizer) -> "Dataset":
    """Tokenizes chosen/rejected into TRL RewardTrainer format."""

def sample_test_pairs(dataset: "Dataset", n: int, seed: int) -> list[tuple[str, str]]:
    """Returns n (chosen, rejected) text pairs for smoothness eval."""
```

### Model (`model.py`)

**Dependencies**: config.py

```python
def build_reward_model(cfg: HM1Config, use_lora: bool = True) -> "PreTrainedModel":
    """Llama-2-7B + num_labels=1 head, optional LoRA (modules_to_save=['score'])."""

def load_tokenizer(cfg: HM1Config) -> "PreTrainedTokenizer": ...

def get_reward(model, tokenizer, text: str, device: str) -> float:
    """Single-sequence scalar reward score."""
```

### Train (`train.py`)

**Dependencies**: config.py, data.py, model.py

```python
def build_trainer(cfg: HM1Config, model, tokenizer, train_ds, val_ds) -> "RewardTrainer": ...

def run_training(cfg: HM1Config) -> str:
    """Full pipeline: load data -> build model -> train -> save checkpoints (1k/5k/10k).
    Returns path to final checkpoint."""
```

### Gradient Metrics (`metrics/gradient.py`)

**Dependencies**: model.py

```python
def compute_gradient_stats(model, tokenizer, test_samples: list[str], device: str) -> dict:
    """Input-embedding gradient norms. Returns mean/std/max_gradient_norm."""
```

### Distribution Metrics (`metrics/distribution.py`)

**Dependencies**: model.py

```python
def compute_bimodality(values: list[float]) -> float:
    """Sarle's bimodality coefficient."""

def analyze_reward_distribution(model, tokenizer, test_pairs: list[tuple[str, str]], device: str) -> dict:
    """Returns reward_range, reward_std, unique_reward_ratio, bimodality_coefficient."""
```

### Interpolation Metrics (`metrics/interpolation.py`)

**Dependencies**: model.py

```python
def interpolate_embeddings(model, tokenizer, chosen: str, rejected: str, alpha: float, device: str) -> float:
    """Reward at embedding-space convex combination (1-alpha)*rejected + alpha*chosen."""

def test_interpolation(model, tokenizer, pairs: list[tuple[str, str]], device: str, n_steps: int = 10) -> dict:
    """Returns mean/max_interpolation_error vs linear expectation."""
```

### Baselines (`baselines.py`)

**Dependencies**: model.py, metrics/*

```python
def build_random_baseline(cfg: HM1Config) -> "PreTrainedModel":
    """Untrained base model + randomly initialized reward head."""

def run_baseline_metrics(cfg: HM1Config, test_pairs, device: str) -> dict:
    """Runs gradient/distribution/interpolation metrics on random baseline."""
```

### Evaluate (`evaluate.py`)

**Dependencies**: metrics/*, baselines.py, data.py

```python
def run_evaluation(cfg: HM1Config, checkpoint_path: str) -> dict:
    """Loads trained model, runs all 3 metric suites + baseline, checks thresholds,
    writes smoothness_metrics.json. Returns combined results dict with pass/fail flags."""
```

### Visualize (`visualize.py`)

**Dependencies**: evaluate.py

```python
def plot_reward_distribution(rewards_chosen: list[float], rewards_rejected: list[float], out_path: str) -> None:
    """Saves reward_distribution.png (histogram/KDE of chosen vs rejected)."""
```

---

## External Dependencies (Base Hypothesis)

None. h-e1 is EXISTENCE-type (validated distinct alignment dimensions conceptually); no code artifacts to reuse for h-m1.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | Config & scaffolding | HM1Config, RewardConfig/LoraConfig builders | 5 | 1+1+1+2 |
| M1-2 | Data pipeline | Load HH-RLHF, split, preprocess, sample test pairs | 9 | 2+3+2+2 |
| M1-3 | Model setup | Llama-2-7B + LoRA + reward head build | 10 | 3+3+2+2 |
| M1-4 | Training loop | RewardTrainer integration, checkpointing at 1k/5k/10k | 14 | 3+4+4+3 |
| M1-5 | Gradient smoothness metric | Input-embedding gradient norm computation | 8 | 2+2+3+1 |
| M1-6 | Reward distribution metric | Bimodality coefficient, distribution stats | 7 | 2+1+3+1 |
| M1-7 | Interpolation metric | Embedding-space mixing, deviation from linear | 11 | 3+2+4+2 |
| M1-8 | Baseline comparison | Random-init baseline, run all metrics on it | 8 | 2+2+2+2 |
| M1-9 | Evaluation orchestration | Combine metrics, threshold checks, JSON output | 9 | 2+3+2+2 |
| M1-10 | Visualization & report | reward_distribution.png, feed into 04_validation.md | 6 | 2+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M1-4], Medium(9-13): [M1-2, M1-3, M1-7, M1-9], Low(4-8): [M1-1, M1-5, M1-6, M1-8, M1-10]
