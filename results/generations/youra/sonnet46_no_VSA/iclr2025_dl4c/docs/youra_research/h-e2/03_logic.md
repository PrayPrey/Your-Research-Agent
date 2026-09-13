# Logic: H-E2 — SFT Training Source Ablation

**Applied**: Standard HuggingFace accelerate+deepspeed training pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## A-2: SFT Training Script [Complexity: 15, Budget: 4 subtasks]

**Applied**: TRL SFTTrainer + completion_only_loss pattern

---

### L-A2-1: TRL SFTTrainer Configuration

```python
from trl import SFTConfig, SFTTrainer, DataCollatorForCompletionOnlyLM
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizerBase
from datasets import Dataset

FIXED_HPARAMS: dict = {
    "learning_rate": 2e-5,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.05,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "bf16": True,
    "max_seq_length": 2048,
    "weight_decay": 0.01,
    "adam_beta1": 0.9,
    "adam_beta2": 0.95,
    "dataset_text_field": "text",
}

EPOCHS_PER_CONDITION: dict[str, int] = {
    "humaneval_only": 6,
    "mbpp_only": 3,
    "leetcode_only": 1,
    "equal_mix": 2,
}

BASE_HUMANEVAL: float = 0.15
BASE_MBPP: float = 0.45

# response_template marks completion start; everything before is masked (label=-100)
RESPONSE_TEMPLATE: str = "\n"  # solution begins on the line after function_signature

def load_model_and_tokenizer(
    model_id: str = "deepseek-ai/deepseek-coder-1.3b-base",
) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """Load base model and tokenizer in bf16."""
    ...

def run_sft(
    condition: str,
    seed: int,
    data_dir: str,
    output_dir: str,
) -> None:
    """Train one SFT run; saves checkpoint to output_dir/condition_{condition}_seed_{seed}."""
    ...
```

**SFTConfig + SFTTrainer construction inside `run_sft`:**

```python
config = SFTConfig(
    output_dir=f"{output_dir}/condition_{condition}_seed_{seed}",
    num_train_epochs=EPOCHS_PER_CONDITION[condition],
    seed=seed,
    save_strategy="no",   # save only at end via trainer.save_model()
    logging_steps=10,
    report_to="none",
    **FIXED_HPARAMS,
)

collator = DataCollatorForCompletionOnlyLM(
    response_template=RESPONSE_TEMPLATE,
    tokenizer=tokenizer,
)

trainer = SFTTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
    data_collator=collator,
)
trainer.train()
trainer.save_model(config.output_dir)
```

**Subtasks [4/4 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-A2-1 | SFTTrainer Config | SFTConfig dataclass + completion_only_loss collator |
| L-A2-2 | DeepSpeed ZeRO-3 | ds_zero3_config.json + accelerate wiring |
| L-A2-3 | Multi-Seed Loop | 4×3 iteration + seed setting + checkpoint naming |
| L-A2-4 | Activation Verification | pass@1 gate + early abort |

---

### L-A2-2: DeepSpeed ZeRO-3 Config

**Applied**: DeepSpeed ZeRO-3 standard config (DeepSeek-Coder official template)

`ds_zero3_config.json`:

```json
{
  "bf16": {
    "enabled": true
  },
  "zero_optimization": {
    "stage": 3,
    "overlap_comm": true,
    "contiguous_gradients": true,
    "sub_group_size": 1e9,
    "reduce_bucket_size": 2e8,
    "stage3_prefetch_bucket_size": 2e8,
    "stage3_param_persistence_threshold": 1e6,
    "allgather_bucket_size": 2e8,
    "stage3_max_live_parameters": 1e9,
    "stage3_max_reuse_distance": 1e9,
    "gather_16bit_weights_on_model_save": true
  },
  "gradient_accumulation_steps": "auto",
  "gradient_clipping": "auto",
  "steps_per_print": 10,
  "train_batch_size": "auto",
  "train_micro_batch_size_per_gpu": "auto",
  "wall_clock_breakdown": false
}
```

`accelerate_config.yaml` (5x H100):

```yaml
compute_environment: LOCAL_MACHINE
distributed_type: DEEPSPEED
deepspeed_config:
  deepspeed_config_file: ds_zero3_config.json
  zero3_init_flag: true
num_processes: 5
mixed_precision: bf16
```

**Wiring to SFTTrainer**: no code change needed; `accelerate launch` injects DeepSpeed via env. SFTTrainer auto-detects it.

```bash
# run_all.sh launch command per run:
accelerate launch \
    --config_file accelerate_config.yaml \
    code/train.py \
    --condition $CONDITION \
    --seed $SEED \
    --data_dir data/sft_sources \
    --output_dir checkpoints
```

---

### L-A2-3: Multi-Seed Training Loop

```python
CONDITIONS: list[str] = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
SEEDS: list[int] = [42, 123, 777]

def set_all_seeds(seed: int) -> None:
    """Set all RNG sources for reproducibility."""
    import random
    import numpy as np
    import torch
    from transformers import set_seed as hf_set_seed
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    hf_set_seed(seed)  # covers transformers + datasets RNG
```

**Checkpoint naming** (constructed in `run_sft`):

```python
# Path: checkpoints/condition_{condition}_seed_{seed}/
# e.g.: checkpoints/condition_humaneval_only_seed_42/
checkpoint_dir = f"{output_dir}/condition_{condition}_seed_{seed}"
```

**Orchestration pseudo-code (run_all.sh):**

```
for CONDITION in humaneval_only mbpp_only leetcode_only equal_mix:
    for SEED in 42 123 777:
        accelerate launch ... train.py --condition $CONDITION --seed $SEED
        # train.py calls verify_sft_activation internally after first seed
        # exits non-zero on failure; run_all.sh aborts loop
```

---

### L-A2-4: SFT Activation Verification

```python
IMPROVEMENT_THRESHOLD: float = 0.03  # +3 pp required on >= 1 benchmark

def verify_sft_activation(
    pass1_humaneval: float,
    pass1_mbpp: float,
    condition: str,
) -> bool:
    """Return True if SFT improved over base on >= 1 benchmark by IMPROVEMENT_THRESHOLD."""
    humaneval_ok = (pass1_humaneval - BASE_HUMANEVAL) >= IMPROVEMENT_THRESHOLD
    mbpp_ok = (pass1_mbpp - BASE_MBPP) >= IMPROVEMENT_THRESHOLD
    activated = humaneval_ok or mbpp_ok
    if not activated:
        print(
            f"[ABORT] condition={condition} failed activation check: "
            f"HumanEval={pass1_humaneval:.3f} (base={BASE_HUMANEVAL}), "
            f"MBPP={pass1_mbpp:.3f} (base={BASE_MBPP}). "
            "Check LR, dedup, or data formatting."
        )
    return activated
```

**Early abort pattern** (called in `run_sft` after training + quick EvalPlus):

```
1. trainer.train()
2. trainer.save_model(checkpoint_dir)
3. run evalplus on humaneval  -> pass1_he
4. run evalplus on mbpp       -> pass1_mbpp
5. if not verify_sft_activation(pass1_he, pass1_mbpp, condition):
       sys.exit(1)   # run_all.sh sees non-zero; aborts remaining seeds
```

Note: EvalPlus greedy on 164+378 tasks takes ~5 min on H100 — use full eval, not partial.

---

## A-1: Data Pipeline [Complexity: 14, Budget: 3 subtasks]

**Applied**: Batched numpy cosine similarity + HF datasets concatenate/interleave pattern

---

### L-A1-1: Deduplication Algorithm

```python
import numpy as np
from datasets import Dataset
from sentence_transformers import SentenceTransformer

DEDUP_THRESHOLD: float = 0.95
EMBED_MODEL: str = "all-MiniLM-L6-v2"
EMBED_BATCH_SIZE: int = 256

def embed_texts(
    texts: list[str],
    model_name: str = EMBED_MODEL,
) -> np.ndarray:
    """Embed and L2-normalize texts. Returns: [N, 384] float32."""
    model = SentenceTransformer(model_name)
    return model.encode(texts, batch_size=EMBED_BATCH_SIZE, normalize_embeddings=True)
    # shape: [N, 384], L2-normalized => dot product equals cosine similarity

def dedup_against_eval(
    dataset: Dataset,
    threshold: float = DEDUP_THRESHOLD,
) -> Dataset:
    """Remove training examples with max cosine sim > threshold vs eval set."""
    ...
```

**Tensor shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| train_embs | [N_train, 384] | L2-normalized |
| eval_embs | [N_eval, 384] | L2-normalized; N_eval ~542 (164 HE+ + 378 MBPP+) |
| sim_chunk | [CHUNK, N_eval] | train_chunk @ eval_embs.T |
| max_sim | [N_train] | max over N_eval axis per train example |
| keep_mask | [N_train] | bool, True = keep |

**Batched sim computation** (avoids large matrix for N_train up to ~3000):

```python
# ponytail: O(N_train * N_eval) dense; fine for N_train<=3000, N_eval=542
CHUNK_SIZE = 512
max_sims = []
for i in range(0, len(train_embs), CHUNK_SIZE):
    chunk = train_embs[i : i + CHUNK_SIZE]       # [CHUNK, 384]
    sims = chunk @ eval_embs.T                   # [CHUNK, N_eval]
    max_sims.append(sims.max(axis=1))            # [CHUNK]
keep_mask = np.concatenate(max_sims) <= threshold
return dataset.select(np.where(keep_mask)[0])
```

**Eval texts source:**

```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus

def get_eval_texts() -> list[str]:
    texts = [v["prompt"] for v in get_human_eval_plus().values()]
    texts += [v["prompt"] for v in get_mbpp_plus().values()]
    return texts  # ~542 items
```

---

### L-A1-2: Token Budget Equalization

```python
from datasets import Dataset, concatenate_datasets
from transformers import PreTrainedTokenizerBase
import math

def count_dataset_tokens(
    dataset: Dataset,
    tokenizer: PreTrainedTokenizerBase,
    text_col: str = "text",
) -> int:
    """Sum token counts across all examples."""
    # ponytail: loads all texts into memory; fine for N<=164
    return sum(
        len(tokenizer.encode(ex, add_special_tokens=False))
        for ex in dataset[text_col]
    )

def repeat_to_token_budget(
    dataset: Dataset,
    target_tokens: int,
    tokenizer: PreTrainedTokenizerBase,
) -> Dataset:
    """Tile dataset until >= target_tokens, then prefix-truncate to exact budget."""
    ...
```

**Algorithm inside `repeat_to_token_budget`:**

```
1. token_counts = [len(tokenizer.encode(ex)) for ex in dataset["text"]]
2. tokens_per_epoch = sum(token_counts)
3. repeat_factor = ceil(target_tokens / tokens_per_epoch)
4. tiled_examples = list(dataset) * repeat_factor
5. tiled_token_counts = token_counts * repeat_factor
6. cumsum = cumulative_sum(tiled_token_counts)
7. K = last index where cumsum[K] <= target_tokens
8. return Dataset.from_list(tiled_examples[:K+1])
```

**How target_tokens is determined in `build_sft_dataset`:**

```python
# Compute humaneval_only token total as reference budget (smallest post-dedup source).
# All other conditions tile to match it.
# humaneval_only's SFTTrainer uses num_train_epochs=6 to iterate the same budget.
target_tokens = count_dataset_tokens(humaneval_only_ds, tokenizer)
```

---

### L-A1-3: Source-Specific Data Format Pipeline

```python
from datasets import Dataset, load_dataset, concatenate_datasets
from evalplus.data import get_human_eval_plus, get_mbpp_plus

CONDITIONS: list[str] = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
UNIFORM_TEMPLATE: str = (
    "# Complete the following Python function:\n"
    "{docstring}\n"
    "{function_signature}"
)

def load_source(condition: str) -> Dataset:
    """Load raw HF dataset for a single source (not equal_mix)."""
    ...

def format_example(ex: dict, source: str) -> dict:
    """Map source columns to {"text": UNIFORM_TEMPLATE + solution}."""
    ...

def build_sft_dataset(
    condition: str,
    tokenizer: PreTrainedTokenizerBase,
    output_dir: str,
    target_tokens: int = 0,  # 0 = auto-compute from humaneval_only
) -> Dataset:
    """Full pipeline: load -> dedup -> subsample(164) -> format -> token-equalize -> save."""
    ...
```

**Column mapping per source:**

| Source | docstring col | signature col | solution col | HF dataset ID |
|--------|--------------|---------------|--------------|---------------|
| humaneval_only | `prompt` (includes signature) | parse from `prompt` | `canonical_solution` | `openai/openai_humaneval` |
| mbpp_only | `text` | first line of `code` | `code` | `google-research-datasets/mbpp` config=`sanitized` |
| leetcode_only | `description` | first line of `python_solution` | `python_solution` | `newfacade/LeetCodeDataset` (filter `language=="python"`) |

**format_example per source:**

```python
def format_example(ex: dict, source: str) -> dict:
    if source == "humaneval":
        # prompt already contains docstring + signature in HumanEval format
        text = (
            UNIFORM_TEMPLATE.format(
                docstring=_extract_docstring(ex["prompt"]),
                function_signature=_extract_signature(ex["prompt"]),
            )
            + "\n" + ex["canonical_solution"]
        )
    elif source == "mbpp":
        sig_line = ex["code"].split("\n")[0]  # "def func_name(...):"
        text = (
            UNIFORM_TEMPLATE.format(docstring=ex["text"], function_signature=sig_line)
            + "\n" + ex["code"]
        )
    elif source == "leetcode":
        sig_line = ex["python_solution"].split("\n")[0]
        text = (
            UNIFORM_TEMPLATE.format(
                docstring=ex["description"][:500],  # cap long problem descriptions
                function_signature=sig_line,
            )
            + "\n" + ex["python_solution"]
        )
    return {"text": text}
```

**equal_mix construction** (after each source is independently deduped + subsampled to 164):

```python
def build_equal_mix(datasets_by_source: dict[str, Dataset]) -> Dataset:
    """Slice 41 examples from each source, concatenate, shuffle."""
    # ponytail: simple slice+concat; fine for N=164; no interleave_datasets needed
    per_source = 164 // len(datasets_by_source)  # = 41
    slices = [
        ds.select(range(min(per_source, len(ds))))
        for ds in datasets_by_source.values()
    ]
    return concatenate_datasets(slices).shuffle(seed=0)
```

---

## Subtask Budget Summary

| Task | Top-level subtasks | Budget |
|------|--------------------|--------|
| A-2 (SFT Training) | L-A2-1, L-A2-2, L-A2-3, L-A2-4 | 4 / 4 |
| A-1 (Data Pipeline) | L-A1-1, L-A1-2, L-A1-3 | 3 / 3 |
| **Total** | | **7 / 7** |
