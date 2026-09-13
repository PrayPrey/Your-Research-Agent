# Logic: H-E1 — Effective Rank as Zero-Shot LoRA Rank Predictor

**Version**: 1.0
**Date**: 2026-08-05
**Phase**: 3 (Logic Design)

---

## Codebase Analysis (Serena)

**Project Type**: green-field (archives exist, no active src/)
**Status**: Archive patterns found; verified LoRA build pattern from `20260805T150802_routing_recovery/h-e1/code/model_setup.py`
**Analyzed Path**: `docs/youra_research/_archive/20260805T150802_routing_recovery/h-e1/code/`
**Relevant Symbols**: `build_lora_model` (single LoraConfig via get_peft_model), `set_seed`, `save_results`
**Note**: Archive uses single-rank single-adapter pattern. H-E1 requires dual-adapter pattern (not in archives) — new design required.

---

## A-4: Oracle Sweep Orchestration [Complexity: 16, Budget: 4 subtasks]

Applied: HuggingFace PEFT get_peft_model + checkpoint-per-run resume pattern

### API Signatures

```python
# oracle.py

def build_oracle_state_key(model_slug: str, layer_safe: str, rank: int, seed: int) -> str:
    """Deterministic string key for result lookup."""
    # Returns: "bert-base-uncased__encoder.layer.0.attention.self.query__r8__s42"

def get_checkpoint_path(cfg: ExperimentConfig, layer_safe: str, rank: int, seed: int) -> Path:
    """Returns Path to per-run result JSON."""
    # cfg.checkpoint_dir / model_slug / f"{layer_safe}__r{rank}__s{seed}.json"

def is_done(cfg: ExperimentConfig, layer_safe: str, rank: int, seed: int) -> bool:
    """True if result JSON exists and is valid (has 'val_acc' key)."""

def load_or_resume_oracle(cfg: ExperimentConfig) -> dict[str, dict]:
    """
    Scan cfg.checkpoint_dir / model_slug / *.json.
    Returns {state_key: {"val_acc": float, "rank": int, "layer": str, "seed": int}}.
    """

def run_oracle_sweep(
    cfg: ExperimentConfig,
    erank_map: dict[str, float],
    max_workers: int = 1,
) -> dict[str, int]:
    """
    Sweep all (layer, rank, seed) combos; skip completed; dispatch train_one_run.
    Returns oracle_rank_map {layer_name: int}.
    # ponytail: sequential default, set max_workers=GPU count for parallel
    """

def compute_oracle_rank_map(
    all_results: dict[str, dict],
    layers: list[str],
    oracle_ranks: list[int],
    seeds: list[int],
) -> dict[str, int]:
    """
    For each layer: mean val_acc over seeds per rank → argmax.
    Returns {layer_name: best_rank}.
    """
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | run_oracle_sweep pseudo-code | Sweep loop with checkpoint resume + dispatch |
| L-4-2 | build_oracle_state_key + checkpoint naming | Key scheme and path convention |
| L-4-3 | Multi-worker dispatch | ProcessPoolExecutor layer-parallel dispatch |
| L-4-4 | compute_oracle_rank_map aggregation | Seed mean → argmax per layer |

### L-4-1: run_oracle_sweep Pseudo-code

```
run_oracle_sweep(cfg, erank_map, max_workers=1):
    layers = list(erank_map.keys())
    jobs = [(layer, rank, seed)
            for layer in layers
            for rank in cfg.oracle_ranks
            for seed in cfg.seeds
            if not is_done(cfg, layer_to_safe(layer), rank, seed)]

    if max_workers == 1:
        for (layer, rank, seed) in tqdm(jobs):
            val_acc = train_one_run(cfg.model_name, layer, rank, seed, cfg)
            save_result(cfg, layer, rank, seed, val_acc)
    else:
        # L-4-3: ProcessPoolExecutor dispatch
        with ProcessPoolExecutor(max_workers=max_workers) as pool:
            futs = {pool.submit(train_one_run, cfg.model_name, layer, rank, seed, cfg): (layer, rank, seed)
                    for (layer, rank, seed) in jobs}
            for fut in as_completed(futs):
                layer, rank, seed = futs[fut]
                val_acc = fut.result()
                save_result(cfg, layer, rank, seed, val_acc)

    all_results = load_or_resume_oracle(cfg)
    return compute_oracle_rank_map(all_results, layers, cfg.oracle_ranks, cfg.seeds)
```

### L-4-2: Checkpoint Naming Scheme

```python
def layer_to_safe(layer_name: str) -> str:
    # Replace '.' with '__' to avoid filesystem issues
    # "encoder.layer.0.attention.self.query" -> "encoder__layer__0__attention__self__query"
    return layer_name.replace(".", "__")

def get_checkpoint_path(cfg, layer_safe, rank, seed) -> Path:
    model_slug = cfg.model_name.replace("/", "-")
    return cfg.checkpoint_dir / model_slug / f"{layer_safe}__r{rank}__s{seed}.json"

def build_oracle_state_key(model_slug, layer_safe, rank, seed) -> str:
    return f"{model_slug}__{layer_safe}__r{rank}__s{seed}"
```

### L-4-3: ProcessPoolExecutor Dispatch

```python
# Each worker calls train_one_run in a subprocess — full model load per job.
# ProcessPoolExecutor chosen over ThreadPoolExecutor: GIL-free for GPU work.
# ponytail: no GPU affinity pinning; add CUDA_VISIBLE_DEVICES per worker if needed

from concurrent.futures import ProcessPoolExecutor, as_completed

def _run_job(args: tuple) -> tuple[str, int, int, float]:
    model_name, layer, rank, seed, cfg = args
    val_acc = train_one_run(model_name, layer, rank, seed, cfg)
    return layer, rank, seed, val_acc
```

### L-4-4: compute_oracle_rank_map Aggregation

```python
def compute_oracle_rank_map(all_results, layers, oracle_ranks, seeds) -> dict[str, int]:
    oracle_rank_map = {}
    for layer in layers:
        rank_acc = {}
        for rank in oracle_ranks:
            accs = [
                all_results[build_oracle_state_key(model_slug, layer_to_safe(layer), rank, s)]["val_acc"]
                for s in seeds
                if build_oracle_state_key(...) in all_results
            ]
            if accs:
                rank_acc[rank] = sum(accs) / len(accs)  # mean over seeds
        if rank_acc:
            oracle_rank_map[layer] = max(rank_acc, key=rank_acc.get)  # argmax
    return oracle_rank_map
```

---

## A-3: Single Oracle Run [Complexity: 14, Budget: 3 subtasks]

Applied: PEFT dual-adapter pattern (two LoraConfig calls, second frozen)

### API Signatures

```python
# train.py

def build_oracle_model(
    model_name: str,
    target_layer: str,
    target_rank: int,
    baseline_rank: int = 8,
    cfg: ExperimentConfig = None,
) -> tuple[nn.Module, Any]:
    """
    Build PEFT model with two adapters:
      adapter "target": target_layer at target_rank (trainable)
      adapter "baseline": all other target_modules at baseline_rank (frozen)
    Returns (peft_model, tokenizer_or_processor).
    DeBERTa forced to float32. BERT/ViT: float16 if CUDA available.
    """

def train_one_run(
    model_name: str,
    target_layer: str,
    target_rank: int,
    seed: int,
    cfg: ExperimentConfig,
) -> float:
    """
    Single training run for (model, layer, rank, seed).
    Returns val_accuracy. Saves checkpoint JSON.
    Short-circuits if checkpoint exists.
    """
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | build_oracle_model dual-adapter | PEFT two-adapter construction |
| L-3-2 | train_one_run training loop | AdamW + warmup + eval loop |
| L-3-3 | FP32/FP16 precision dispatch | Per-model dtype selection |

### L-3-1: build_oracle_model Dual-Adapter Pattern

PEFT `LoraConfig` does not support mixed ranks — use two adapters.

```python
def build_oracle_model(model_name, target_layer, target_rank, baseline_rank=8, cfg=None):
    model_cfg = MODEL_CONFIGS[model_name]
    dtype = _get_dtype(model_name)  # L-3-3

    # Load base model
    if model_cfg["task"] == "cifar10":
        base = ViTForImageClassification.from_pretrained(
            model_name, num_labels=10, ignore_mismatched_sizes=True, torch_dtype=dtype)
        proc = ViTImageProcessor.from_pretrained(model_name)
    else:
        base = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=model_cfg["num_labels"], torch_dtype=dtype)
        proc = AutoTokenizer.from_pretrained(model_name)

    base = base.to(dtype)  # DeBERTa: ensures float32 even if loaded as fp16

    # Adapter 1: target layer at target_rank (trainable)
    lora_target = LoraConfig(
        r=target_rank,
        lora_alpha=2 * target_rank,
        target_modules=[target_layer],
        lora_dropout=0.0,
        bias="none",
        task_type="SEQ_CLS" if model_cfg["task"] != "cifar10" else "FEATURE_EXTRACTION",
    )
    model = get_peft_model(base, lora_target, adapter_name="target")

    # Adapter 2: remaining target_modules at baseline_rank (frozen)
    other_modules = [m for m in model_cfg["target_modules"] if m != target_layer]
    if other_modules:
        lora_baseline = LoraConfig(
            r=baseline_rank,
            lora_alpha=2 * baseline_rank,
            target_modules=other_modules,
            lora_dropout=0.0,
            bias="none",
            task_type="SEQ_CLS" if model_cfg["task"] != "cifar10" else "FEATURE_EXTRACTION",
        )
        model.add_adapter("baseline", lora_baseline)
        # Freeze baseline adapter
        for name, param in model.named_parameters():
            if "baseline" in name:
                param.requires_grad_(False)

    model.set_adapter("target")  # activate target adapter for training
    return model, proc
```

### L-3-2: train_one_run Training Loop

```python
def train_one_run(model_name, target_layer, target_rank, seed, cfg) -> float:
    layer_safe = layer_to_safe(target_layer)
    ckpt_path = get_checkpoint_path(cfg, layer_safe, target_rank, seed)
    if ckpt_path.exists():
        return json.loads(ckpt_path.read_text())["val_acc"]

    torch.manual_seed(seed)
    model, proc = build_oracle_model(model_name, target_layer, target_rank, cfg.baseline_rank, cfg)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    train_loader, val_loader = get_data_loaders(model_name, proc, cfg)
    total_steps = len(train_loader) * _get_epochs(cfg, model_name)
    warmup_steps = int(total_steps * cfg.warmup_ratio)

    optimizer = AdamW(filter(lambda p: p.requires_grad, model.parameters()),
                      lr=_get_lr(cfg, model_name), weight_decay=cfg.weight_decay)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    model.train()
    for epoch in range(_get_epochs(cfg, model_name)):
        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            loss = model(**batch).loss
            loss.backward()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

    val_acc = _evaluate(model, val_loader, device)
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    ckpt_path.write_text(json.dumps({
        "val_acc": val_acc, "rank": target_rank,
        "layer": target_layer, "seed": seed,
    }))
    return val_acc
```

### L-3-3: FP32/FP16 Precision Dispatch

```python
def _get_dtype(model_name: str) -> torch.dtype:
    # DeBERTa: FP32 mandatory (FP16 causes classifier overflow per FIM-LoRA paper)
    if "deberta" in model_name.lower():
        return torch.float32
    return torch.float16 if torch.cuda.is_available() else torch.float32

def _get_epochs(cfg: ExperimentConfig, model_name: str) -> int:
    return cfg.epochs_vit if "vit" in model_name.lower() else cfg.epochs_nlp

def _get_lr(cfg: ExperimentConfig, model_name: str) -> float:
    return cfg.lr_vit if "vit" in model_name.lower() else cfg.lr_nlp
```

### Tensor Shapes (key operations)

| Variable | Shape | Note |
|----------|-------|------|
| W (query weight) | [hidden, hidden] e.g. [768, 768] | 2D Linear weight |
| svdvals output | [min(768,768)] = [768] | singular values |
| p (normalized) | [K] K <= 768 | after filtering < 1e-10 |
| erank | scalar | exp(entropy(p)) |
| LoRA A | [r, hidden] | e.g. [8, 768] |
| LoRA B | [hidden, r] | e.g. [768, 8] |

---

## Helper Function Signatures (Supporting Both Modules)

```python
# oracle.py helpers
def save_result(cfg: ExperimentConfig, layer: str, rank: int, seed: int, val_acc: float) -> None:
    """Write result JSON to checkpoint path. Atomic via tmp+rename."""

# train.py helpers
def _evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> float:
    """Returns accuracy on loader. model.eval() context."""
```
