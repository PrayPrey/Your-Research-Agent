# Logic: h-m2 (Rank Sensitivity Phase Transition, MECHANISM)

Applied: linregress slope + percentile bootstrap CI pattern (scipy/numpy)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena MCP has no active project registered for this path; verified API signatures by reading h-e1 actual code files directly (`config.py`, `model.py`, `data.py`, `train.py`).
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `load_base_model`, `load_tokenizer`, `apply_lora`, `load_squad_v2`, `tokenize_squad`, `train_one_run`, `evaluate_squad_f1`, `compute_squad_f1`, `set_seed`, `TrainConfig`, `MODEL_HF_IDS`

**Critical deviation found vs h-e1's own `03_logic.md` spec**: actual `model.py` uses `AutoModelForQuestionAnswering` (not causal LM) and `TaskType.QUESTION_ANS`; `apply_lora(model, rank, alpha=None, dropout=0.05, target_modules=None)` defaults `alpha=2*rank` internally when `None`. `load_tokenizer(model_id)` is a separate function not mentioned in h-e1 spec. All signatures below use the verified actual code.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL)
MODELS: dict[str, float]          # {"pythia-1b": 1.0e9, ...}
MODEL_HF_IDS: dict[str, str]
RANKS: list[int] = [4, 8, 16, 32, 64, 128]
SEEDS: list[int] = [42, 1337, 2024]

class TrainConfig:
    epochs: int = 3; lr: float = 1e-4; batch_size: int = 8
    grad_accum: int = 4; warmup_steps: int = 100; max_length: int = 384
    grad_clip: float = 1.0; gradient_checkpointing: bool = True

# From: h-e1/code/model.py (ACTUAL)
def load_base_model(model_id: str, device_map: str = "auto") -> PreTrainedModel: ...
def load_tokenizer(model_id: str) -> AutoTokenizer: ...
def apply_lora(model: PreTrainedModel, rank: int, alpha: int | None = None,
                dropout: float = 0.05, target_modules: list[str] | None = None) -> PeftModel: ...

# From: h-e1/code/data.py (ACTUAL)
def load_squad_v2(cache_dir: str | None = None) -> DatasetDict: ...
def tokenize_squad(dataset: DatasetDict, tokenizer: PreTrainedTokenizer, max_length: int = 384) -> DatasetDict: ...
# tokenize_squad adds: start_positions, end_positions, example_id columns; sliding-window
# stride=128, truncation="only_second", offset_mapping-based span alignment.

# From: h-e1/code/train.py (ACTUAL)
def set_seed(seed: int) -> None: ...
def train_one_run(model_id: str, rank: int, seed: int, cfg: TrainConfig,
                   output_dir: str = "checkpoints", data_cache_dir: str | None = None) -> float: ...
def evaluate_squad_f1(model, val_loader, tokenizer, val_dataset, device) -> float: ...
def compute_squad_f1(predictions: list[dict], references: list[dict]) -> float:
    """predictions: [{"id","prediction_text","no_answer_probability"}]
    references: [{"id","answers":{"text":[...],"answer_start":[...]}}]"""
```

**Integration**: h-m2 copies these 4 files verbatim into `h-m2/code/` (per architecture doc, simplest path — no import path hacking needed).

---

## B-1/B-2/B-4/B-5/B-6/B-8/B-9: Low complexity, no subtask budget

Signatures per architecture.md are copy-paste ready as-is; no additional pseudo-code needed (straightforward pandas/scipy/matplotlib calls). Reference architecture.md directly for these.

---

## B-3: HotpotQA Train/Eval [Complexity: 9, Budget: 2]

**Applied**: mirrors `train_one_run`/`evaluate_squad_f1` control flow exactly, swap dataset+metric

### API Signatures

```python
# train_hotpotqa.py
from data import load_hotpotqa, tokenize_hotpotqa
from model import load_base_model, load_tokenizer, apply_lora
from train import set_seed
import evaluate

def train_one_run_hotpotqa(
    model_id: str, rank: int, seed: int, cfg: TrainConfig,
    output_dir: str = "checkpoints", data_cache_dir: str | None = None,
) -> float:
    """Same control flow as h-e1 train_one_run, dataset=hotpotqa."""
    ...

def evaluate_hotpotqa_f1(model, val_loader, tokenizer, val_dataset, device) -> float:
    """Identical decode logic to evaluate_squad_f1; no no_answer_probability
    (HotpotQA always has an answer) -> squad (v1) metric, not squad_v2."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids, attention_mask | [B, L] | B=8, L=384, context = concatenated 10 supporting+distractor paragraphs |
| start_logits, end_logits | [B, L] | same QA head as h-e1 (AutoModelForQuestionAnswering) |

### Pseudo-code

```
1. set_seed(seed)
2. tokenizer = load_tokenizer(model_id)
3. dataset = load_hotpotqa(cache_dir=data_cache_dir)
4. tokenized = tokenize_hotpotqa(dataset, tokenizer, cfg.max_length)
5. model = apply_lora(load_base_model(model_id), rank)  # alpha defaults 2*rank
6. train loop: identical to train.py train_one_run (AdamW, warmup, grad_accum, per-epoch ckpt)
7. predictions/references built same as evaluate_squad_f1 but skip no_answer_probability field
8. f1 = evaluate.load("squad").compute(predictions, references)["f1"]  # squad v1 metric, no no-answer handling
9. return f1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-B3-1 | train_one_run_hotpotqa | copy train.py loop, swap data.py calls to hotpotqa variants |
| L-B3-2 | evaluate_hotpotqa_f1 | copy evaluate_squad_f1 decode logic, use `evaluate.load("squad")` (v1, no no-answer field) |

---

## B-7: Phase Transition Test [Complexity: 8, Budget: 0 — reuses architecture.md signature]

Signature already copy-paste ready in architecture.md (`test_phase_transition`). No additional pseudo-code needed — standard `scipy.stats.ttest_1samp`-style one-sided test + `np.random.choice` percentile bootstrap, same bootstrap pattern as h-e1's `fit_scaling_law` (see h-e1/03_logic.md A-6 pseudo-code, directly reusable pattern).

```python
def test_phase_transition(sens_1b: list[float], sens_12b: list[float], cfg: StatsConfig) -> dict:
    ratio_obs = np.mean(sens_12b) / np.mean(sens_1b)
    diff = np.array(sens_12b) - cfg.ratio_threshold * np.array(sens_1b)
    t_stat, p_value = stats.ttest_1samp(diff, 0.0, alternative="greater")
    boot_ratios = [np.mean(np.random.choice(sens_12b, len(sens_12b), replace=True)) /
                   np.mean(np.random.choice(sens_1b, len(sens_1b), replace=True))
                   for _ in range(cfg.n_bootstrap)]
    ci_low, ci_high = np.percentile(boot_ratios, [2.5, 97.5])
    return {"ratio": ratio_obs, "ci_low": ci_low, "ci_high": ci_high,
            "p_value": p_value, "pass": ratio_obs > 2.0 and ci_low > 1.5 and p_value < 0.05}
```

No subtask allocated (all 2 budget units spent on B-3; this task's pseudo-code above is sufficient for direct implementation).
