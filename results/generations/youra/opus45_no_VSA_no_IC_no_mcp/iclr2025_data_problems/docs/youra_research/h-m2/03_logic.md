# Logic: H-M2 (Deduplication Stringency Dose-Response)

Applied: from-scratch-LM-training-loop pattern (AdamW + cosine, checkpoint/resume)
Applied: config-varied-dataset-generation pattern (dedup level -> tokenized pack)
Applied: sweep-orchestration pattern (nested level x seed loop, resumable)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code, new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Data Pipeline [Complexity: 12, Budget: 12]

**Applied**: HuggingFace datasets streaming + tiktoken/GPT2 packing pattern

### API Signatures

```python
def download_redpajama(sample: bool = True, cache_dir: str = "./data/raw") -> list[str]:
    """Download RedPajama-v2 docs (sampled subset if sample=True). Returns raw text list."""
    ...

def build_dataset(documents: list[str], config: DeduplicationConfig) -> list[str]:
    """Apply dedup.apply_deduplication then verify. Returns deduplicated doc list."""
    ...

def tokenize_and_pack(
    documents: list[str],
    total_tokens: int,
    seq_len: int = 1024,
    tokenizer_name: str = "gpt2",
) -> torch.Tensor:
    """Tokenize + concat + chunk into fixed-len sequences. -> [num_seqs, seq_len] int64"""
    ...

def save_packed_tokens(tokens: torch.Tensor, level: str, out_dir: str = "./data/packed") -> str:
    """Save packed tensor to disk as .pt. Returns file path."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| tokens (per doc concat) | [total_tokens] | 1D flat stream before chunking |
| packed | [total_tokens // seq_len, seq_len] | int64, drop remainder |

### Pseudo-code

```
1. raw_docs = download_redpajama(sample=True)
2. for level_cfg in DEDUP_LEVELS:
     deduped = build_dataset(raw_docs, level_cfg)
     stats = dedup.log_dedup_stats(level_cfg.level, len(raw_docs), len(deduped))
     token_stream = tokenizer.encode(concat(deduped))
     token_stream = repeat/truncate to exactly total_tokens (10B)
     packed = token_stream[: (len//seq_len)*seq_len].reshape(-1, seq_len)
     save_packed_tokens(packed, level_cfg.level)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Download + sample RedPajama | Streaming HF load, dedup-safe raw text extraction |
| L-3-2 | Dedup integration | Call dedup.build_dataset per level, log stats |
| L-3-3 | Tokenize + pack | GPT-2 tokenizer, flatten/chunk to seq_len blocks, handle token budget (repeat if under 10B) |
| L-3-4 | Persist packed tensors | Save per-level .pt files + stats json to disk |

---

## A-5: Training Loop [Complexity: 14, Budget: 14]

**Applied**: Standard PyTorch AdamW + cosine warmup + checkpoint/resume pattern

### API Signatures

```python
def train_one_config(
    level: str,
    seed: int,
    tokens: torch.Tensor,      # [num_seqs, seq_len]
    cfg: TrainConfig,
    ckpt_dir: str,
) -> str:
    """Train GPT-2 from scratch on packed tokens. Returns final checkpoint path."""
    ...

def build_optimizer(model: GPT2LMHeadModel, cfg: TrainConfig) -> torch.optim.AdamW:
    """AdamW(betas=(0.9, 0.95), weight_decay=0.1, lr=cfg.lr)"""
    ...

def build_scheduler(optimizer, cfg: TrainConfig, total_steps: int) -> torch.optim.lr_scheduler.LambdaLR:
    """Linear warmup (cfg.warmup_steps) then cosine decay to 0."""
    ...

def save_checkpoint(model: GPT2LMHeadModel, optimizer, scheduler, step: int, ckpt_dir: str) -> None:
    """Save model/optim/sched state_dict + step to {ckpt_dir}/step_{step}.pt"""
    ...

def resume_from_checkpoint(ckpt_dir: str) -> tuple[GPT2LMHeadModel, torch.optim.Optimizer, int]:
    """Load latest checkpoint in ckpt_dir. Returns (model, optimizer, start_step)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| batch input_ids | [B=512, seq_len=1024] | sampled slice of packed tokens |
| logits | [B, seq_len, vocab_size] | GPT2LMHeadModel output |
| loss | scalar | CrossEntropy, shift-by-1 LM loss |

### Pseudo-code (training loop)

```
def train_one_config(level, seed, tokens, cfg, ckpt_dir):
    torch.manual_seed(seed)
    model = build_gpt2_model(cfg).cuda()
    total_steps = cfg.total_tokens // (cfg.batch_size * seq_len)
    ckpt_interval_steps = 1_000_000_000 // (cfg.batch_size * seq_len)  # every 1B tokens

    if checkpoint_exists(ckpt_dir):
        model, optimizer, start_step = resume_from_checkpoint(ckpt_dir)
        scheduler = build_scheduler(optimizer, cfg, total_steps)  # advance to start_step
    else:
        optimizer = build_optimizer(model, cfg)
        scheduler = build_scheduler(optimizer, cfg, total_steps)
        start_step = 0

    for step in range(start_step, total_steps):
        batch = sample_batch(tokens, cfg.batch_size, seed_offset=step)  # [B, seq_len]
        out = model(input_ids=batch, labels=batch)
        out.loss.backward()
        clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step(); scheduler.step(); optimizer.zero_grad()
        log_loss(level, seed, step, out.loss.item())

        if step % ckpt_interval_steps == 0:
            save_checkpoint(model, optimizer, scheduler, step, ckpt_dir)

    final_path = save_checkpoint(model, optimizer, scheduler, total_steps, ckpt_dir)
    return final_path
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Optimizer + scheduler | AdamW(0.9,0.95,wd=0.1) + linear warmup/cosine decay builders |
| L-5-2 | Core train step + batching | Sample batches from packed tensor, forward/backward/step, loss logging |
| L-5-3 | Checkpoint/resume | Save every 1B tokens, resume detects latest ckpt, restores step/optim/sched |
| L-5-4 | 15-run driver | Loop 5 levels x 3 seeds, isolate ckpt_dir per (level, seed), skip completed runs |

---

## A-7: Sweep Orchestration [Complexity: 11, Budget: 11]

**Applied**: idempotent pipeline orchestration (skip-if-done per stage)

### API Signatures

```python
def run_full_sweep(dedup_levels: list[DeduplicationConfig], cfg: TrainConfig) -> dict:
    """Orchestrate dedup->data->train->eval for 5 levels x 3 seeds.
    Returns {level: {seed: {"ckpt": path, "scores": dict}}}"""
    ...

def run_single_arm(level_cfg: DeduplicationConfig, seed: int, cfg: TrainConfig, base_dir: str) -> dict:
    """One (level, seed) arm: data (cached) -> train -> eval. Returns {"ckpt": str, "scores": dict}."""
    ...
```

### Pseudo-code

```
def run_full_sweep(dedup_levels, cfg):
    raw_docs = download_redpajama()
    results = {}
    for level_cfg in dedup_levels:
        packed_path = f"./data/packed/{level_cfg.level}.pt"
        if not exists(packed_path):
            deduped = build_dataset(raw_docs, level_cfg)
            tokens = tokenize_and_pack(deduped, cfg.total_tokens)
            save_packed_tokens(tokens, level_cfg.level)
        tokens = load(packed_path)

        results[level_cfg.level] = {}
        for seed in cfg.seeds:
            ckpt_dir = f"./checkpoints/{level_cfg.level}/{seed}"
            ckpt = train_one_config(level_cfg.level, seed, tokens, cfg, ckpt_dir)
            scores = run_benchmarks(ckpt)
            scores["pc1"] = compute_pc1_ensemble(scores)
            results[level_cfg.level][seed] = {"ckpt": ckpt, "scores": scores}
            save_json(results, "./results/sweep_results.json")  # incremental persist
    return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Data-stage wiring | Per-level dedup+pack, cache-check to avoid recompute |
| L-7-2 | Train-stage wiring | Per (level, seed) call train_one_config with isolated ckpt_dir |
| L-7-3 | Eval-stage wiring | Call run_benchmarks + compute_pc1_ensemble per checkpoint |
| L-7-4 | Incremental result persistence | Save results dict to JSON after each arm; resume-safe (skip completed arms) |

---

## Evaluation Integration Pseudo-code (A-6, reference for A-7 caller)

```python
def run_benchmarks(checkpoint_path: str, tasks: list[str] = None) -> dict:
    """lm-eval-harness on HellaSwag, ARC-E, PIQA, WinoGrande. -> {"hellaswag": float, ...}"""
    tasks = tasks or ["hellaswag", "arc_easy", "piqa", "winogrande"]
    model = load_hf_model(checkpoint_path)
    results = lm_eval.simple_evaluate(model=model, tasks=tasks)
    return {t: results["results"][t]["acc"] for t in tasks}

def compute_pc1_ensemble(benchmark_scores: dict[str, list[float]]) -> float:
    """PCA across benchmark score vectors (per-seed rows); returns PC1 projection scalar."""
    # scores: [n_seeds, n_benchmarks] -> standardize -> PCA -> pc1[:, 0]
    ...
```

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Archon/Serena logs limited to 1-line "Applied:" statements + Codebase Analysis section
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in tables/comments
- [x] Subtask counts match budgets: A-3 (4), A-5 (4), A-7 (4) — all within allocated complexity budgets
- [x] Total length < 250 lines
