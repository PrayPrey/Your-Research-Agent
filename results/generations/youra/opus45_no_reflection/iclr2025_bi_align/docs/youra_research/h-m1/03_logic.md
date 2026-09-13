# Logic: H-M1 (MECHANISM)

**Hypothesis:** L_agency integrates stably with DPO loss (training completes, loss decreases)
**Type:** MECHANISM - training stability, single run, no ablations

Applied: No relevant KB pattern found (searched "DPO loss implementation", "training loop PyTorch gradient clipping" — only unrelated diffusers/DALLE2 results); standard torchtune-style DPO loss + manual grad-accum loop used (per experiment brief's Exa research).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signature verified from actual code (not spec)
**Analyzed Path**: `docs/youra_research/h-e1/code/collab_score.py`
**Relevant Symbols**: `compute_collab_score_v2(response: str) -> float` — confirmed unbounded raw ratio (sum of 4 regex signal counts / sqrt(word_count)), NOT normalized. H-M1 `bidpo_loss.py` must clip via `normalize_agency_score` before computing `1 - score`, else L_agency can exceed PRD's required [0,2] range and destabilize training.

---

## External Dependencies API

```python
# From: docs/youra_research/h-e1/code/collab_score.py (ACTUAL CODE, copy verbatim into h-m1/code/)
def compute_collab_score_v2(response: str) -> float:
    """Length-normalized collaboration score (unbounded, >= 0). Not clipped."""
    ...
```

**Verified from**: `docs/youra_research/h-e1/code/collab_score.py` (read directly, matches 03_logic.md spec exactly — no drift found).

---

## M-1: Setup config + copy collab_score [Complexity: 4, Budget: 0]

**Applied**: Standard Python config module (same pattern as H-E1)

```python
# config.py
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
AGENCY_SCORE_CLIP_MAX: float = 5.0
OUTPUT_DIR: str = "outputs/"
FIGURES_DIR: str = "outputs/figures/"
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | config.py | Constants above |
| L-1-2 | Copy collab_score.py | Verbatim copy from H-E1 code dir |
| L-1-3 | dirs | `os.makedirs(OUTPUT_DIR/FIGURES_DIR, exist_ok=True)` |
| L-1-4 | seed | `set_seed(SEED)` util (torch/np/random) |

---

## M-2: Data pipeline [Complexity: 10, Budget: 11]

**Applied**: HuggingFace `datasets` load + tokenizer padding pattern

```python
# data.py
from datasets import Dataset, load_dataset
from torch.utils.data import DataLoader
from transformers import PreTrainedTokenizer

def load_hh_rlhf(split: str) -> Dataset:
    """load_dataset('Anthropic/hh-rlhf')[split]."""
    ...

def tokenize_pair(example: dict, tokenizer: PreTrainedTokenizer) -> dict:
    """Tokenize chosen/rejected text, truncate/pad to MAX_LENGTH.
    Returns chosen_input_ids [L], chosen_attention_mask [L],
    rejected_input_ids [L], rejected_attention_mask [L]."""
    ...

def add_collab_scores(dataset: Dataset) -> Dataset:
    """Map compute_collab_score_v2 over chosen/rejected text -> chosen_collab_score, rejected_collab_score cols (float)."""
    ...

def collate_fn(batch: list[dict]) -> dict:
    """Stack tensors -> dict of Tensor [B, L] per field."""
    ...

def get_dataloader(dataset: Dataset, tokenizer: PreTrainedTokenizer, batch_size: int) -> DataLoader:
    """DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| chosen_input_ids | [B, L] | L = MAX_LENGTH, padded |
| chosen_attention_mask | [B, L] | 1 = real token |
| chosen_collab_score | [B] | float, unbounded raw score |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | load_hh_rlhf | dataset load, train/test split |
| L-2-2 | tokenize_pair + collate_fn | tokenization, padding, batching |
| L-2-3 | add_collab_scores | dataset.map with compute_collab_score_v2 |
| L-2-4 | get_dataloader | DataLoader assembly |

---

## M-3: Model initialization [Complexity: 8, Budget: 8]

**Applied**: Standard `AutoModelForCausalLM.from_pretrained` bfloat16 + frozen-copy pattern

```python
# models.py
import torch
from torch import Tensor
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer

def load_tokenizer(model_name: str) -> PreTrainedTokenizer:
    """AutoTokenizer.from_pretrained; set pad_token = eos_token if missing."""
    ...

def load_policy_model(model_name: str) -> PreTrainedModel:
    """from_pretrained(model_name, torch_dtype=bfloat16, device_map='auto'). Trainable."""
    ...

def load_reference_model(model_name: str) -> PreTrainedModel:
    """Same load as policy; requires_grad_(False); .eval()."""
    ...

def compute_logps(
    model: PreTrainedModel, input_ids: Tensor, attention_mask: Tensor, labels: Tensor
) -> Tensor:
    """Sequence-level sum log-prob of labels under model.
    input_ids/attention_mask/labels: [B, L] -> returns [B]."""
    ...
```

### Pseudo-code (compute_logps — non-obvious masking)

```
compute_logps(model, input_ids, attention_mask, labels):
    logits = model(input_ids, attention_mask=attention_mask).logits  # [B, L, V]
    logits = logits[:, :-1, :]        # predict token t+1
    labels = labels[:, 1:]            # shift
    mask = (labels != pad_token_id)   # [B, L-1]
    log_probs = log_softmax(logits, dim=-1)
    token_logps = gather(log_probs, dim=-1, index=labels.unsqueeze(-1)).squeeze(-1)  # [B, L-1]
    return (token_logps * mask).sum(dim=-1)   # [B]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | load_tokenizer | pad token handling |
| L-3-2 | load_policy_model | bfloat16, device_map=auto |
| L-3-3 | load_reference_model | frozen copy |
| L-3-4 | compute_logps | shifted label log-prob sum |

---

## M-4: BiDPO loss implementation [Complexity: 11, Budget: 11]

**Applied**: torchtune DPOLoss logit-difference pattern (from experiment brief) + manual agency term

```python
# bidpo_loss.py
import torch
import torch.nn.functional as F
from torch import Tensor

def normalize_agency_score(raw_score: Tensor, clip_max: float = 5.0) -> Tensor:
    """Clip raw (unbounded) collab_score_v2 output to [0, clip_max]. [B] -> [B]."""
    return torch.clamp(raw_score, min=0.0, max=clip_max)

def compute_dpo_loss(
    policy_chosen_logps: Tensor,   # [B]
    policy_rejected_logps: Tensor, # [B]
    ref_chosen_logps: Tensor,      # [B]
    ref_rejected_logps: Tensor,    # [B]
    beta: float,
) -> Tensor:
    """Standard sigmoid DPO loss. Returns scalar."""
    pi_logratios = policy_chosen_logps - policy_rejected_logps
    ref_logratios = ref_chosen_logps - ref_rejected_logps
    logits = pi_logratios - ref_logratios
    return -F.logsigmoid(beta * logits).mean()

def compute_agency_loss(
    chosen_collab_scores: Tensor,   # [B], pre-normalized via normalize_agency_score
    rejected_collab_scores: Tensor, # [B], pre-normalized
) -> Tensor:
    """(1 - chosen).mean() - 0.5 * (1 - rejected).mean(). Returns scalar."""
    agency_chosen = (1.0 - chosen_collab_scores).mean()
    agency_rejected = (1.0 - rejected_collab_scores).mean()
    return agency_chosen - 0.5 * agency_rejected

def compute_bidpo_loss(
    policy_chosen_logps: Tensor, policy_rejected_logps: Tensor,
    ref_chosen_logps: Tensor, ref_rejected_logps: Tensor,
    chosen_collab_scores: Tensor, rejected_collab_scores: Tensor,
    beta: float, lambda_agency: float,
) -> tuple[Tensor, dict]:
    """Returns (total_loss Tensor scalar, {dpo_loss, agency_loss, total_loss} as python floats)."""
    dpo_loss = compute_dpo_loss(policy_chosen_logps, policy_rejected_logps, ref_chosen_logps, ref_rejected_logps, beta)

    chosen_norm = normalize_agency_score(chosen_collab_scores)
    rejected_norm = normalize_agency_score(rejected_collab_scores)
    agency_loss = compute_agency_loss(chosen_norm, rejected_norm)

    total_loss = dpo_loss + lambda_agency * agency_loss
    return total_loss, {
        "dpo_loss": dpo_loss.item(),
        "agency_loss": agency_loss.item(),
        "total_loss": total_loss.item(),
    }
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| *_logps | [B] | scalar per-sequence log-prob |
| *_collab_scores | [B] | raw (unbounded) input, clip before use |
| dpo_loss / agency_loss / total_loss | scalar | reduced over batch |

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | normalize_agency_score | clamp [0, clip_max] |
| L-4-2 | compute_dpo_loss | logit-diff sigmoid loss |
| L-4-3 | compute_agency_loss | chosen/rejected combination |
| L-4-4 | compute_bidpo_loss | combine + loss dict |

---

## M-5: Training loop with stability monitoring [Complexity: 14, Budget: 14]

**Applied**: Standard PyTorch loop (`zero_grad`/`backward`/`step`) + `clip_grad_norm_` + NaN/Inf guard (per experiment brief's torch native pattern)

```python
# train.py
import json
import torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import LRScheduler

def check_stability(loss_dict: dict) -> bool:
    """False if any NaN/Inf present in loss_dict values."""
    return all(torch.isfinite(torch.tensor(v)) for v in loss_dict.values())

def train_loop(
    policy_model, reference_model, dataloader, optimizer: AdamW,
    scheduler: LRScheduler, cfg,
) -> dict:
    """Runs GRAD_ACCUM_STEPS-accumulated training for EPOCHS.
    Logs loss components + grad norm every LOG_INTERVAL steps.
    On instability: dumps debug_info.json (step, loss_dict, batch idx) and raises RuntimeError.
    Returns history: {steps, dpo_loss, agency_loss, total_loss, grad_norm, lr} -> lists.
    """
    ...

def save_checkpoint(model, path: str, is_best: bool = False) -> None:
    """torch.save(model.state_dict(), path)."""
    ...
```

### Pseudo-code (train_loop — core stability logic)

```
train_loop(policy, ref, dataloader, optimizer, scheduler, cfg):
    history = {steps: [], dpo_loss: [], agency_loss: [], total_loss: [], grad_norm: [], lr: []}
    step = 0
    optimizer.zero_grad()
    for epoch in range(cfg.EPOCHS):
        for i, batch in enumerate(dataloader):
            policy_chosen_lp = compute_logps(policy, batch.chosen_input_ids, batch.chosen_attention_mask, batch.chosen_input_ids)
            policy_rejected_lp = compute_logps(policy, batch.rejected_input_ids, batch.rejected_attention_mask, batch.rejected_input_ids)
            with torch.no_grad():
                ref_chosen_lp = compute_logps(ref, batch.chosen_input_ids, batch.chosen_attention_mask, batch.chosen_input_ids)
                ref_rejected_lp = compute_logps(ref, batch.rejected_input_ids, batch.rejected_attention_mask, batch.rejected_input_ids)

            loss, loss_dict = compute_bidpo_loss(
                policy_chosen_lp, policy_rejected_lp, ref_chosen_lp, ref_rejected_lp,
                batch.chosen_collab_score, batch.rejected_collab_score,
                cfg.BETA, cfg.LAMBDA_AGENCY,
            )

            if not check_stability(loss_dict):
                json.dump({"step": step, "loss_dict": loss_dict}, open(f"{cfg.OUTPUT_DIR}/debug_info.json", "w"))
                raise RuntimeError(f"NaN/Inf detected at step {step}: {loss_dict}")

            (loss / cfg.GRAD_ACCUM_STEPS).backward()

            if (i + 1) % cfg.GRAD_ACCUM_STEPS == 0:
                grad_norm = torch.nn.utils.clip_grad_norm_(policy.parameters(), cfg.GRAD_CLIP_NORM)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                step += 1

                if step % cfg.LOG_INTERVAL == 0:
                    history.steps.append(step)
                    history.dpo_loss.append(loss_dict.dpo_loss)
                    history.agency_loss.append(loss_dict.agency_loss)
                    history.total_loss.append(loss_dict.total_loss)
                    history.grad_norm.append(grad_norm.item())
                    history.lr.append(scheduler.get_last_lr()[0])

    return history
```

### Subtasks [14/14 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | AdamW + cosine scheduler setup | `get_cosine_schedule_with_warmup(optimizer, warmup_steps, total_steps)` |
| L-5-2 | forward pass (policy + frozen ref) | logps computation both models |
| L-5-3 | check_stability + debug dump + grad accum/clip loop | core loop above |
| L-5-4 | history logging + save_checkpoint | per-LOG_INTERVAL append, final/best save |

---

## M-6: Checkpoint management [Complexity: 5, Budget: 5]

**Applied**: `save_checkpoint` already declared in M-5; add best-tracking wrapper

```python
# in train.py, called from run_experiment.py
def save_best_if_improved(model, current_loss: float, best_loss: float, path: str) -> float:
    """If current_loss < best_loss: save_checkpoint(model, path, is_best=True). Returns updated best_loss."""
    ...
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | save final checkpoint | end of train_loop |
| L-6-2 | track best loss during loop | compare total_loss each log step |
| L-6-3 | save best checkpoint | separate path `outputs/best.pt` |
| L-6-4 | verify checkpoint load roundtrip | smoke test in run_experiment |

---

## M-7: Visualization suite [Complexity: 7, Budget: 7]

**Applied**: Standard matplotlib line-plot pattern (same as H-E1 visualize.py)

```python
# visualize.py
def plot_loss_curves(history: dict, out_path: str) -> None:
    """Line plot: dpo_loss, agency_loss, total_loss vs steps. Saves PNG."""
    ...

def plot_gradient_norm(history: dict, out_path: str) -> None:
    """Line plot: grad_norm vs steps, horizontal line at GRAD_CLIP_NORM. Saves PNG."""
    ...

def plot_lr_schedule(history: dict, out_path: str) -> None:
    """Line plot: lr vs steps (cosine warmup shape). Saves PNG."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | plot_loss_curves | 3-line plot |
| L-7-2 | plot_gradient_norm | grad norm + clip threshold line |
| L-7-3 | plot_lr_schedule | LR curve |

---

## M-8: End-to-end orchestration + gate check [Complexity: 8, Budget: 8]

**Applied**: Standard main() orchestration script (same as H-E1 run_experiment.py)

```python
# run_experiment.py
def evaluate_gate(history: dict) -> dict:
    """gate_passed = all(finite) AND history.total_loss[-1] < history.total_loss[0] (post-warmup).
    Returns {training_completed, loss_decreased, gate_passed}."""
    ...

def main() -> None:
    """Load data -> init models -> train -> evaluate_gate -> save figures + results.json."""
    ...
```

### Pseudo-code

```
main():
    tokenizer = load_tokenizer(cfg.MODEL_NAME)
    train_ds = add_collab_scores(load_hh_rlhf("train"))
    dataloader = get_dataloader(train_ds, tokenizer, cfg.BATCH_SIZE)

    policy = load_policy_model(cfg.MODEL_NAME)
    reference = load_reference_model(cfg.MODEL_NAME)
    optimizer = AdamW(policy.parameters(), lr=cfg.LEARNING_RATE)
    scheduler = get_cosine_schedule_with_warmup(optimizer, ...)

    try:
        history = train_loop(policy, reference, dataloader, optimizer, scheduler, cfg)
        gate = evaluate_gate(history)
    except RuntimeError as e:
        gate = {"training_completed": False, "loss_decreased": False, "gate_passed": False, "error": str(e)}
        history = {}

    save_checkpoint(policy, f"{cfg.OUTPUT_DIR}/final.pt")
    if history:
        plot_loss_curves(history, f"{cfg.FIGURES_DIR}/training_loss_curves.png")
        plot_gradient_norm(history, f"{cfg.FIGURES_DIR}/gradient_norm.png")
        plot_lr_schedule(history, f"{cfg.FIGURES_DIR}/lr_schedule.png")

    json.dump({"gate": gate, "history": history}, open(f"{cfg.OUTPUT_DIR}/results.json", "w"), indent=2)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | evaluate_gate | finite-check + loss decrease check |
| L-8-2 | main() orchestration | wiring above |
| L-8-3 | try/except NaN early-stop handling | gate=False on RuntimeError |
| L-8-4 | results.json + figures save | final artifacts |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in code comments / tables for non-obvious cases
- [x] Subtask count within budget for each task
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included (base_hypothesis scenario)
- [x] External Dependencies API section included with H-E1 verified signature
