# Logic: H-M1 RLHF Reward Model Smoothing

**Type:** MECHANISM | Budget: high-complexity tasks only (M1-2, M1-3, M1-4, M1-7, M1-9)

Applied: TRL RewardTrainer Bradley-Terry pattern; PEFT LoRA SEQ_CLS reward head

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## M1-2: Data Pipeline [Complexity: 9]

**Applied**: HuggingFace `datasets` train_test_split pattern

### API Signatures

```python
def load_hh_rlhf_splits(cfg: HM1Config) -> DatasetDict:
    """Load Anthropic/hh-rlhf, split 90/5/5 train/val/test."""
    ...

def preprocess_for_reward_trainer(
    dataset: Dataset, tokenizer: PreTrainedTokenizer, max_length: int = 512
) -> Dataset:
    """Tokenize chosen/rejected -> input_ids_chosen, attention_mask_chosen, input_ids_rejected, attention_mask_rejected."""
    ...

def sample_test_pairs(dataset: Dataset, n: int, seed: int) -> list[tuple[str, str]]:
    """Random sample n (chosen_text, rejected_text) string pairs."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids_chosen | [B, L] | L=max_length=512, padded |
| attention_mask_chosen | [B, L] | 1=real token |
| input_ids_rejected | [B, L] | same shape as chosen |

### Pseudo-code

```
1. raw = load_dataset("Anthropic/hh-rlhf")  # concat helpful-base, helpful-online, harmless-base
2. train, rest = raw.train_test_split(test_size=0.10, seed=cfg.seed)
3. val, test = rest.train_test_split(test_size=0.50, seed=cfg.seed)  # 5%/5%
4. for split in (train, val, test):
       split = split.map(preprocess_for_reward_trainer, batched=True)
5. test_pairs = sample_test_pairs(test, n=cfg.test_sample_size, seed=cfg.seed)  # raw text, re-tokenized per-metric
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M1-2-1 | load_hh_rlhf_splits | HF datasets load + concat subsets |
| L-M1-2-2 | 90/5/5 split logic | Two-stage train_test_split |
| L-M1-2-3 | preprocess_for_reward_trainer | Batched tokenization, TRL column format |
| L-M1-2-4 | sample_test_pairs | Seeded random sample, returns text tuples |

---

## M1-3: Model Setup [Complexity: 10]

**Applied**: `AutoModelForSequenceClassification` + PEFT LoRA (`task_type=SEQ_CLS`, `modules_to_save=["score"]`)

### API Signatures

```python
def build_reward_model(cfg: HM1Config, use_lora: bool = True) -> PreTrainedModel:
    """Llama-2-7B + num_labels=1 classification head, LoRA applied unless use_lora=False."""
    ...

def load_tokenizer(cfg: HM1Config) -> PreTrainedTokenizer:
    """Loads tokenizer, sets pad_token = eos_token if missing."""
    ...

def get_reward(model: PreTrainedModel, tokenizer: PreTrainedTokenizer, text: str, device: str) -> float:
    """Tokenize text, forward pass, return scalar logits[0].item()."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [1, 1] | num_labels=1, squeeze to scalar |
| embeddings (interp use) | [1, L, H] | H=4096 for Llama-2-7B |

### Pseudo-code

```
1. base = AutoModelForSequenceClassification.from_pretrained(
       cfg.base_model, num_labels=1, torch_dtype=bf16
   )
2. if use_lora:
       peft_cfg = get_peft_config(cfg)  # r=16, alpha=32, target_modules=[q,k,v,o]_proj, modules_to_save=["score"]
       model = get_peft_model(base, peft_cfg)
   else:
       model = base
3. model.config.pad_token_id = tokenizer.pad_token_id
4. enable_gradient_checkpointing(model)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M1-3-1 | load base classification model | bf16, num_labels=1 |
| L-M1-3-2 | apply LoRA wrapper | get_peft_model with modules_to_save |
| L-M1-3-3 | tokenizer setup | pad_token fallback, padding side |
| L-M1-3-4 | get_reward helper | single-text forward -> float |

---

## M1-4: Training Loop [Complexity: 14]

**Applied**: TRL `RewardTrainer` with `RewardConfig`, checkpoint callback at custom steps

### API Signatures

```python
def build_trainer(
    cfg: HM1Config,
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    train_ds: Dataset,
    val_ds: Dataset,
) -> RewardTrainer:
    """Wraps TRL RewardTrainer with RewardConfig(cfg) and PeftConfig already applied to model."""
    ...

def run_training(cfg: HM1Config) -> str:
    """Full pipeline: load data -> build model -> train -> save checkpoints at 1k/5k/10k.
    Returns path to final checkpoint dir."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| rewards_chosen | [B] | RewardTrainer internal, per-batch |
| rewards_rejected | [B] | same |
| loss | scalar | Bradley-Terry NLL + center_rewards_coefficient term |

### Pseudo-code

```
run_training(cfg):
    1. tokenizer = load_tokenizer(cfg)
    2. splits = load_hh_rlhf_splits(cfg)
    3. train_ds = preprocess_for_reward_trainer(splits["train"], tokenizer, cfg.max_length)
    4. val_ds   = preprocess_for_reward_trainer(splits["validation"], tokenizer, cfg.max_length)
    5. model = build_reward_model(cfg, use_lora=True)
    6. reward_config = get_reward_config(cfg)  # batch_size=4, grad_accum=4, lr=1e-4, epochs=1,
                                                #   center_rewards_coefficient=0.01, bf16=True,
                                                #   gradient_checkpointing=True, max_length=512
    7. trainer = build_trainer(cfg, model, tokenizer, train_ds, val_ds)
    8. checkpoint_cb = SaveAtStepsCallback(steps=[1000, 5000, 10000], output_dir=cfg.output_dir)
    9. trainer.add_callback(checkpoint_cb)
    10. trainer.train()   # loss = -logsigmoid(r_chosen - r_rejected).mean()
                            #        + center_rewards_coefficient * ((r_chosen + r_rejected)**2).mean()
    11. final_path = f"{cfg.output_dir}/final"
    12. trainer.save_model(final_path)
    13. return final_path
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M1-4-1 | build_trainer | Wraps RewardTrainer(model, args, train_ds, val_ds, peft_config) |
| L-M1-4-2 | checkpoint callback | Custom TrainerCallback saving at steps 1k/5k/10k |
| L-M1-4-3 | run_training orchestration | Data -> model -> trainer -> train() |
| L-M1-4-4 | metric logging | Ensure loss/accuracy/margin logged via logging_steps=50 |

---

## M1-7: Interpolation Metric [Complexity: 11]

**Applied**: Embedding-space convex combination + linear interpolation deviation

### API Signatures

```python
def interpolate_embeddings(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    chosen: str,
    rejected: str,
    alpha: float,
    device: str,
) -> float:
    """Reward at (1-alpha)*rejected_emb + alpha*chosen_emb. Sequences padded/truncated to equal length."""
    ...

def test_interpolation(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    pairs: list[tuple[str, str]],
    device: str,
    n_steps: int = 10,
) -> dict:
    """Returns mean/max_interpolation_error normalized by reward range."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| emb_chosen | [1, L, H] | L = max(len(chosen_tok), len(rejected_tok)), padded to match |
| emb_rejected | [1, L, H] | must equal emb_chosen shape for convex combo |
| mixed_emb | [1, L, H] | (1-alpha)*emb_rejected + alpha*emb_chosen |
| expected | [n_steps] | np.linspace(r_rejected, r_chosen, n_steps) |
| actual | [n_steps] | reward per alpha step |

### Pseudo-code

```
interpolate_embeddings(model, tokenizer, chosen, rejected, alpha, device):
    1. tok_c = tokenizer(chosen, padding="max_length", truncation=True, max_length=cfg.max_length, return_tensors="pt")
    2. tok_r = tokenizer(rejected, padding="max_length", truncation=True, max_length=cfg.max_length, return_tensors="pt")
       # equal-length padding required for elementwise embedding mix
    3. emb_c = model.get_input_embeddings()(tok_c["input_ids"].to(device))  # [1, L, H]
    4. emb_r = model.get_input_embeddings()(tok_r["input_ids"].to(device))  # [1, L, H]
    5. mixed_emb = (1 - alpha) * emb_r + alpha * emb_c
    6. mixed_mask = torch.maximum(tok_c["attention_mask"], tok_r["attention_mask"]).to(device)
    7. with torch.no_grad():
           out = model(inputs_embeds=mixed_emb, attention_mask=mixed_mask)
    8. return out.logits.squeeze().item()

test_interpolation(model, tokenizer, pairs, device, n_steps):
    1. errors = []
    2. reward_range = precompute global reward_range (chosen/rejected across pairs) for normalization
    3. for chosen, rejected in pairs:
           r_chosen = get_reward(model, tokenizer, chosen, device)
           r_rejected = get_reward(model, tokenizer, rejected, device)
           expected = np.linspace(r_rejected, r_chosen, n_steps)
           actual = [interpolate_embeddings(model, tokenizer, chosen, rejected, a, device)
                     for a in np.linspace(0, 1, n_steps)]
           error = np.mean(np.abs(np.array(actual) - expected)) / max(reward_range, 1e-6)
           errors.append(error)
    4. return {"mean_interpolation_error": np.mean(errors), "max_interpolation_error": np.max(errors)}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M1-7-1 | equal-length tokenization | Pad both sequences to same max_length |
| L-M1-7-2 | interpolate_embeddings | Convex combo + no-grad forward |
| L-M1-7-3 | test_interpolation loop | 500 pairs x n_steps=10, normalized error |
| L-M1-7-4 | reward_range normalization | Use dataset-level range, guard div-by-zero |

---

## M1-9: Evaluation Orchestration [Complexity: 9]

**Applied**: Standard PyTorch eval loop + threshold-gate pattern

### API Signatures

```python
def run_evaluation(cfg: HM1Config, checkpoint_path: str) -> dict:
    """Loads trained model, runs gradient/distribution/interpolation metrics + baseline,
    checks thresholds, writes smoothness_metrics.json. Returns combined results dict."""
    ...
```

### Pseudo-code

```
run_evaluation(cfg, checkpoint_path):
    1. tokenizer = load_tokenizer(cfg)
    2. model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path).to(device).eval()
    3. splits = load_hh_rlhf_splits(cfg)
    4. test_pairs = sample_test_pairs(splits["test"], cfg.test_sample_size, cfg.seed)
    5. interp_pairs = test_pairs[:cfg.interpolation_pair_count]

    6. grad_stats  = compute_gradient_stats(model, tokenizer, [c for c, r in test_pairs], device)
    7. dist_stats  = analyze_reward_distribution(model, tokenizer, test_pairs, device)
    8. interp_stats = test_interpolation(model, tokenizer, interp_pairs, device, cfg.n_interp_steps)

    9. baseline_model = build_random_baseline(cfg)
    10. baseline_stats = run_baseline_metrics(cfg, test_pairs, device)  # same 3 metric suites

    11. results = {
            "gradient": grad_stats,
            "distribution": dist_stats,
            "interpolation": interp_stats,
            "baseline": baseline_stats,
            "pass": {
                "gradient": grad_stats["mean_gradient_norm"] < 10.0,
                "distribution": dist_stats["bimodality_coefficient"] < 0.55,
                "interpolation": interp_stats["mean_interpolation_error"] < 0.3,
            },
        }
    12. results["overall_pass"] = all(results["pass"].values())
    13. write_json(results, f"{cfg.output_dir}/smoothness_metrics.json")
    14. return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M1-9-1 | load checkpoint model/tokenizer | From checkpoint_path |
| L-M1-9-2 | run 3 metric suites | gradient, distribution, interpolation on test set |
| L-M1-9-3 | baseline comparison | Random-init model, same metrics |
| L-M1-9-4 | threshold gate + JSON output | pass/fail dict, overall_pass, write file |

---

## External Dependencies (Base Hypothesis)

None. h-e1 (EXISTENCE) has no code artifacts; h-m1 is a fresh green-field implementation.
