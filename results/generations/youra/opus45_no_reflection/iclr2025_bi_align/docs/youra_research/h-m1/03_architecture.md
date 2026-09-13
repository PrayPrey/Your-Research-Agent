# Architecture: H-M1 (MECHANISM)

**Hypothesis:** L_agency integrates stably with DPO loss (training completes, loss decreases)
**Type:** MECHANISM - training stability test, single run, no ablations

Applied: No directly relevant KB pattern found (searched "DPO training loop architecture", "multi-objective loss optimization" — only unrelated diffusers/dreambooth results); standard TRL DPOTrainer subclass pattern used instead (per experiment brief's Exa research).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: `collab_score.py` exports `compute_collab_score_v2(response: str) -> float`. Score is an **unbounded raw ratio** (reasoning/uncertainty/engagement/depth pattern counts / sqrt(word_count)), NOT normalized to [0,1]. H-M1's `agency_loss.py` must clip/normalize `1 - score` to keep L_agency in the PRD-required [0,2] range. No other reusable modules (data.py/analysis.py are HH-RLHF sampling + correlation stats, not needed here).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| collab_score_v2 | `from h_e1.collab_score import compute_collab_score_v2` | `docs/youra_research/h-e1/code/collab_score.py` |

**Verified from**: `docs/youra_research/h-e1/code/collab_score.py` (actual implementation, read directly)

**Note**: Phase 4 Coder should copy `collab_score.py` into H-M1's `code/` directory (no package installed) rather than cross-hypothesis import.

---

## File Structure

- `config.py` - fixed hyperparameters (beta, lambda, lr, batch size, seed)
- `collab_score.py` - copied from H-E1 (compute_collab_score_v2)
- `data.py` - HH-RLHF loading, tokenization, precomputed collab scores
- `models.py` - policy + reference model init
- `bidpo_loss.py` - DPO loss + agency loss + combination
- `train.py` - training loop, stability monitoring, checkpointing
- `visualize.py` - loss curves, gradient norm, LR schedule figures
- `run_experiment.py` - orchestration entrypoint

---

## Module Interfaces

### config.py

```python
SEED: int = 42
MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.2"
DATASET_NAME: str = "Anthropic/hh-rlhf"
MAX_LENGTH: int = 1024
BETA: float = 0.1
LAMBDA_AGENCY: float = 0.5
LEARNING_RATE: float = 5e-7
BATCH_SIZE: int = 4
GRAD_ACCUM_STEPS: int = 4
EPOCHS: int = 1
WARMUP_RATIO: float = 0.1
GRAD_CLIP_NORM: float = 1.0
LOG_INTERVAL: int = 100
OUTPUT_DIR: str = "outputs/"
FIGURES_DIR: str = "outputs/figures/"
```

### collab_score.py

**Dependencies**: None (re, numpy) — copied verbatim from H-E1

```python
def compute_collab_score_v2(response: str) -> float: ...
```

### data.py

**Dependencies**: config, collab_score

```python
def load_hh_rlhf(split: str) -> Dataset: ...
def tokenize_pair(example: dict, tokenizer) -> dict:
    """Returns chosen_input_ids, rejected_input_ids + attention masks."""
    ...
def add_collab_scores(dataset: Dataset) -> Dataset:
    """Adds chosen_collab_score, rejected_collab_score columns."""
    ...
def get_dataloader(dataset: Dataset, tokenizer, batch_size: int) -> DataLoader: ...
```

### models.py

**Dependencies**: config

```python
def load_policy_model(model_name: str) -> PreTrainedModel: ...
def load_reference_model(model_name: str) -> PreTrainedModel:
    """Frozen copy, requires_grad=False, eval mode."""
    ...
def load_tokenizer(model_name: str) -> PreTrainedTokenizer: ...
def compute_logps(model, input_ids, attention_mask, labels) -> torch.Tensor:
    """Sequence-level log-prob of labels under model (batch_size,)."""
    ...
```

### bidpo_loss.py

**Dependencies**: torch.nn.functional

```python
def normalize_agency_score(raw_score: float, clip_max: float = 5.0) -> float:
    """Clip raw collab_score_v2 output to [0, clip_max] before use in 1 - score."""
    ...

def compute_dpo_loss(
    policy_chosen_logps: Tensor, policy_rejected_logps: Tensor,
    ref_chosen_logps: Tensor, ref_rejected_logps: Tensor,
    beta: float,
) -> Tensor: ...

def compute_agency_loss(
    chosen_collab_scores: Tensor, rejected_collab_scores: Tensor,
) -> Tensor:
    """(1 - chosen).mean() - 0.5 * (1 - rejected).mean(), scores pre-normalized."""
    ...

def compute_bidpo_loss(
    policy_chosen_logps: Tensor, policy_rejected_logps: Tensor,
    ref_chosen_logps: Tensor, ref_rejected_logps: Tensor,
    chosen_collab_scores: Tensor, rejected_collab_scores: Tensor,
    beta: float, lambda_agency: float,
) -> tuple[Tensor, dict]:
    """Returns (total_loss, {dpo_loss, agency_loss, total_loss} as floats)."""
    ...
```

### train.py

**Dependencies**: config, models, bidpo_loss, data

```python
def check_stability(loss_dict: dict) -> bool:
    """False if any NaN/Inf present."""
    ...

def train_loop(
    policy_model, reference_model, dataloader, optimizer, scheduler, cfg
) -> dict:
    """Runs training, logs loss components + grad norm every LOG_INTERVAL steps.
    On NaN/Inf: saves debug_info.json and raises early stop.
    Returns history dict: steps, dpo_loss[], agency_loss[], total_loss[], grad_norm[], lr[].
    """
    ...

def save_checkpoint(model, path: str, is_best: bool = False) -> None: ...
```

### visualize.py

**Dependencies**: train (history dict)

```python
def plot_loss_curves(history: dict, out_path: str) -> None: ...
def plot_gradient_norm(history: dict, out_path: str) -> None: ...
def plot_lr_schedule(history: dict, out_path: str) -> None: ...
```

### run_experiment.py

**Dependencies**: config, data, models, bidpo_loss, train, visualize

```python
def main() -> None:
    """Load data -> init models -> train -> check gate -> save figures + results.json"""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup config + copy collab_score | config.py, copy collab_score.py from H-E1 | 4 | 1+1+1+1 |
| M-2 | Data pipeline | Load HH-RLHF, tokenize pairs, precompute collab scores, DataLoader | 10 | 3+2+3+2 |
| M-3 | Model initialization | Load policy + frozen reference Mistral-7B, bfloat16, device_map | 8 | 2+2+2+2 |
| M-4 | BiDPO loss implementation | DPO loss + normalized agency loss + combination | 11 | 3+2+4+2 |
| M-5 | Training loop with stability monitoring | AdamW, cosine warmup, grad clip, NaN/Inf check, logging | 14 | 4+3+4+3 |
| M-6 | Checkpoint management | Save final + best checkpoint | 5 | 2+1+1+1 |
| M-7 | Visualization suite | 3 required figures (loss curves, grad norm, LR schedule) | 7 | 2+1+1+3 |
| M-8 | End-to-end orchestration + gate check | run_experiment.py, results.json, PoC gate evaluation | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M-5], Medium(9-13): [M-2, M-4], Low(4-8): [M-1, M-3, M-6, M-7, M-8]

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Module sections = interface code only
- [x] 8 Epic tasks with complexity (within 6-12 range)
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included (base_hypothesis scenario, mandatory Serena used)
- [x] External Dependencies section included with verified file location
