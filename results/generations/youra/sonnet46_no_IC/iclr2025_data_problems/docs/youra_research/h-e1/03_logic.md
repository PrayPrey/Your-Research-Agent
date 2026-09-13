# Logic: H-E1 — Scale-Dependent Optimal Curation

**Applied**: Standard pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze; Serena skipped
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation from scratch

---

## Data Schemas

### variant_metadata (per curated corpus variant)
```python
{
    "condition":          str,    # e.g. "dolma_ppl20_j07"
    "corpus":             str,    # "dolma" | "fineweb"
    "ppl_threshold":      int,    # 20 | 35 | 50
    "dedup_j":            float,  # 0.7 | 0.9
    "output_path":        str,    # JSONL dir after dedup
    "binary_prefix":      str,    # NeoX .bin/.idx prefix (added by preprocess.py)
    "token_count":        int,    # post-filter token count
    "contamination_rate": float,  # CR for ANCOVA covariate (added by preprocess.py)
}
```

### run_record (per training run)
```python
{
    "run_id":              str,   # e.g. "dolma_ppl20_j07_70m_s1"
    "variant":             str,   # condition key
    "scale":               int,   # 70 | 160
    "seed":                int,   # 1 | 2 | 3
    "checkpoint_dir":      str,   # NeoX raw checkpoint dir
    "status":              str,   # "pending"|"running"|"done"|"error"
    "hf_checkpoint_paths": list[str],  # 10 HF-format dirs, sorted by step
    "error_msg":           str | None,
}
```

### results_df columns
```
scale, ppl_threshold, dedup_j, corpus, seed,
mmlu_4shot, hellaswag_0shot, contamination_rate
```

---

## A-2: Corpus Curation [Complexity: 17, Budget: 4 subtasks]

### API Signatures

```python
# code/curate.py

def score_and_filter_ppl(
    dataset_iter,           # HF IterableDataset
    ppl_threshold: int,     # 20 | 35 | 50
    output_path: str,       # destination JSONL dir
    batch_size: int = 64,   # docs per GPT-2 forward pass
) -> dict:
    """Score docs with GPT-2 PPL; retain PPL <= threshold.
    Returns: {"retained": int, "total": int, "output_path": str}
    """
    ...


def apply_minhash_dedup(
    input_path: str,          # JSONL dir from score_and_filter_ppl
    jaccard_threshold: float, # 0.7 | 0.9
    output_path: str,
    cache_dir: str,
) -> dict:
    """Run NeMo-Curator FuzzyDuplicates; remove near-duplicates.
    Returns: {"retained": int, "total": int, "output_path": str}
    """
    ...


def curate_all_variants(
    corpus_name: str,   # "dolma" | "fineweb"
    base_stream,        # HF IterableDataset (streaming)
    output_root: str,
) -> list[dict]:
    """Produce 6 variants (3 PPL × 2 dedup J) for one corpus.
    Idempotent: skips variant if output dir already exists and non-empty.
    Returns list of variant_metadata dicts.
    """
    ...


def get_corpus_stream(corpus_name: str):
    """Return HF streaming dataset for 'dolma' or 'fineweb'."""
    ...


def log_corpus_stats(variant_metadata: list[dict]) -> None:
    """Write token counts, retention rates, CR to corpus_stats.csv."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | PPL Scoring | Batched GPT-2 inference, memory-efficient streaming |
| L-2-2 | MinHash Dedup | NeMo-Curator FuzzyDuplicates config + band-param derivation |
| L-2-3 | Variant Orchestration | `curate_all_variants` for 12 variants, parallel-safe, idempotent |
| L-2-4 | Corpus Statistics | Token counts, retention rates, contamination rate logging |

---

### L-2-1: PPL Scoring — Pseudo-code

```python
def score_and_filter_ppl(dataset_iter, ppl_threshold, output_path, batch_size=64):
    model = GPT2LMHeadModel.from_pretrained("gpt2").eval().cuda()
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    os.makedirs(output_path, exist_ok=True)
    writer = open(f"{output_path}/filtered.jsonl", "w")
    total, retained = 0, 0

    for doc in dataset_iter:
        # Per-document forward: avoids padding bias on PPL
        ids = tokenizer(
            doc["text"], return_tensors="pt", truncation=True, max_length=1024
        ).input_ids.cuda()
        with torch.no_grad():
            loss = model(ids, labels=ids).loss.item()
        ppl = math.exp(loss)
        total += 1
        if ppl <= ppl_threshold:
            writer.write(json.dumps(doc) + "\n")
            retained += 1

    writer.close()
    # ponytail: per-doc forward is O(N) individual calls; batch with mask-weighted
    # loss if throughput is bottleneck (upgrade: compute loss per non-pad token manually)
    return {"retained": retained, "total": total, "output_path": output_path}
```

**Memory safety**: Stream one doc at a time; never materialize full corpus. Model stays on GPU for duration of one corpus pass, then can be freed.

---

### L-2-2: MinHash Dedup — NeMo-Curator Config

Band parameters from PRD FR-1b (verified):

| J threshold | num_buckets | hashes_per_bucket | char_ngrams | minhash_length | seed |
|-------------|-------------|-------------------|-------------|----------------|------|
| 0.7 | 20 | 13 | 24 | 256 | 42 |
| 0.9 | 8 | 13 | 24 | 256 | 42 |

Derivation: LSH amplification — threshold `t ≈ (1/B)^(1/R)` where B=num_buckets, R=hashes_per_bucket. For J=0.7: `(1/20)^(1/13) ≈ 0.70`. For J=0.9: `(1/8)^(1/13) ≈ 0.84` (approximate; NeMo uses Jaccard threshold directly for candidate filtering).

```python
def apply_minhash_dedup(input_path, jaccard_threshold, output_path, cache_dir):
    from nemo_curator import FuzzyDuplicates, FuzzyDuplicatesConfig

    BAND_PARAMS = {
        0.7: {"num_buckets": 20, "hashes_per_bucket": 13},
        0.9: {"num_buckets": 8,  "hashes_per_bucket": 13},
    }
    params = BAND_PARAMS[jaccard_threshold]

    cfg = FuzzyDuplicatesConfig(
        cache_dir=cache_dir,
        id_field="id",
        text_field="text",
        seed=42,
        char_ngrams=24,
        num_buckets=params["num_buckets"],
        hashes_per_bucket=params["hashes_per_bucket"],
        use_64_bit_hash=False,
        buckets_per_shuffle=1,
        false_positive_check=True,
        num_anchors=2,
        jaccard_threshold=jaccard_threshold,
    )
    deduper = FuzzyDuplicates(logger=logging.getLogger(__name__), config=cfg)

    dataset = DocumentDataset.read_json(input_path, add_filename=True)
    total = len(dataset.df)
    deduped = deduper(dataset)
    retained = len(deduped.df)

    deduped.to_json(output_path, write_to_filename=True)
    return {"retained": retained, "total": total, "output_path": output_path}
```

---

### L-2-3: Variant Orchestration — Pseudo-code

```python
VARIANTS = [
    {"ppl_threshold": tau, "dedup_j": j}
    for tau in [20, 35, 50]
    for j in [0.7, 0.9]
]  # 6 combinations per corpus

def curate_all_variants(corpus_name, base_stream, output_root):
    results = []
    for v in VARIANTS:
        tau, j = v["ppl_threshold"], v["dedup_j"]
        condition = f"{corpus_name}_ppl{tau}_j{int(j*10):02d}"
        ppl_dir   = f"{output_root}/{condition}/ppl_filtered"
        dedup_dir = f"{output_root}/{condition}/deduped"
        cache_dir = f"{output_root}/.cache/{condition}"
        done_flag = f"{dedup_dir}/_SUCCESS"

        # Idempotent: skip if already completed
        if os.path.exists(done_flag):
            meta = json.load(open(f"{dedup_dir}/meta.json"))
            results.append(meta)
            continue

        # Fresh stream per variant (streaming datasets are single-pass)
        stream = get_corpus_stream(corpus_name)

        # Step 1: PPL filtering
        ppl_stats = score_and_filter_ppl(stream, tau, ppl_dir)

        # Step 2: GPU MinHash dedup
        dedup_stats = apply_minhash_dedup(ppl_dir, j, dedup_dir, cache_dir)

        meta = {
            "condition":          condition,
            "corpus":             corpus_name,
            "ppl_threshold":      tau,
            "dedup_j":            j,
            "output_path":        dedup_dir,
            "token_count":        _count_tokens_approx(dedup_dir),
            "contamination_rate": None,  # filled by preprocess.py
        }
        json.dump(meta, open(f"{dedup_dir}/meta.json", "w"), indent=2)
        pathlib.Path(done_flag).touch()
        results.append(meta)

    return results  # 6 dicts; caller runs for both corpora → 12 total
```

**Parallel safety**: Each variant writes to its own `condition/` subdirectory. Two corpus calls (dolma, fineweb) can run in separate processes — no shared mutable state. `_SUCCESS` flag ensures idempotency if a process is killed and restarted.

**Caller in orchestrate.py**:
```python
dolma_meta   = curate_all_variants("dolma",   get_corpus_stream("dolma"),   CORPUS_ROOT)
fineweb_meta = curate_all_variants("fineweb", get_corpus_stream("fineweb"), CORPUS_ROOT)
all_variants = dolma_meta + fineweb_meta  # 12 dicts
```

---

### L-2-4: Corpus Statistics Logging

```python
def log_corpus_stats(variant_metadata: list[dict]) -> None:
    """Write per-variant stats to CSV; CR must already be populated."""
    import csv
    stats_path = pathlib.Path(CORPUS_ROOT) / "corpus_stats.csv"
    fieldnames = [
        "condition", "corpus", "ppl_threshold", "dedup_j",
        "token_count", "contamination_rate",
    ]
    with open(stats_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for m in variant_metadata:
            w.writerow(m)

    # Summary log for ANCOVA input verification
    for m in variant_metadata:
        print(
            f"[stats] {m['condition']:30s} "
            f"tokens={m['token_count']:>15,}  "
            f"CR={m['contamination_rate']:.4f}"
        )
```

`contamination_rate` is set by `preprocess.py::run_decontaminator` which patches each dict in-place before this function is called. The stats CSV feeds `analyze.py` ANCOVA as the CR covariate.

---

## A-4: Training [Complexity: 16, Budget: 4 subtasks]

### API Signatures

```python
# code/train.py

def build_neox_config(
    scale: int,             # 70 | 160
    binary_prefix: str,     # NeoX .bin/.idx prefix path
    seed: int,              # 1 | 2 | 3
    checkpoint_dir: str,
    base_config_path: str,  # path to Pythia 70M or 160M base YAML in gpt-neox repo
) -> str:
    """Merge per-run overrides into base Pythia YAML; write to checkpoint_dir.
    Returns path to written YAML config file.
    """
    ...


def launch_neox_run(
    neox_config_path: str,
    neox_repo: str,
) -> int:
    """Run `python deepy.py train.py <config>` as subprocess.
    Returns exit code.
    """
    ...


def run_all_training(
    variant_metadata: list[dict],  # 12 variant dicts with binary_prefix set
) -> list[dict]:
    """Launch 12 variants × 2 scales × 3 seeds = 72 runs sequentially.
    Resume: skips runs with status='done' in state file.
    Returns list of run_record dicts.
    """
    ...


def list_checkpoints(checkpoint_dir: str) -> list[str]:
    """Return sorted list of HF checkpoint dirs under checkpoint_dir.
    Expects up to 10 checkpoints per run (every 5B tokens).
    """
    ...


def convert_checkpoint_to_hf(
    neox_checkpoint: str,  # path to NeoX global_stepXXXXX dir
    output_dir: str,
    neox_repo: str,
) -> str:
    """Call tools/convert_to_hf.py via subprocess.
    Returns path to HF model dir.
    """
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | build_neox_config | YAML generation from Pythia base configs with per-run overrides |
| L-4-2 | run_all_training | 72-run sequential orchestration with resume/skip logic |
| L-4-3 | list_checkpoints + convert_checkpoint_to_hf | Checkpoint discovery and HF conversion pipeline |
| L-4-4 | Training state tracking | Per-run status dict, atomic writes, error handling, resume |

---

### L-4-1: build_neox_config — Pseudo-code

Pythia per-scale hyperparams (from PRD FR-3):

| Param | 70M | 160M |
|-------|-----|------|
| num_layers | 6 | 12 |
| hidden_size | 512 | 768 |
| num_attention_heads | 8 | 12 |
| lr | 1e-3 | 6e-4 |
| min_lr | 1e-4 | 6e-5 |

```python
SCALE_OVERRIDES = {
    70: {
        "num_layers": 6, "hidden_size": 512, "num_attention_heads": 8,
        "lr": 1e-3, "min_lr": 1e-4,
    },
    160: {
        "num_layers": 12, "hidden_size": 768, "num_attention_heads": 12,
        "lr": 6e-4, "min_lr": 6e-5,
    },
}

def build_neox_config(scale, binary_prefix, seed, checkpoint_dir, base_config_path):
    with open(base_config_path) as f:
        cfg = yaml.safe_load(f)

    # Per-run overrides
    cfg.update({
        "data_path":          binary_prefix,
        "seed":               seed,
        "save":               checkpoint_dir,
        "load":               checkpoint_dir,   # enables mid-run resume
        "seq_length":         2048,
        "rotary_pct":         0.25,
        "train_tokens":       50_000_000_000,   # 50B
        "train_iters":        25_000,
        "checkpoint_factor":  2_500,            # save every 2500 steps = 5B tokens
        "weight_decay":       0.1,
        "gradient_clipping":  1.0,
        "warmup_num_steps":   250,              # 0.01 × 25000
        "lr_decay_style":     "cosine",
        "optimizer": {
            "type": "Adam",
            "params": {"betas": [0.9, 0.95], "eps": 1e-8},
        },
        "fp16": {"enabled": True},
        "zero_optimization": {"stage": 1},
    })
    cfg.update(SCALE_OVERRIDES[scale])

    os.makedirs(checkpoint_dir, exist_ok=True)
    out_path = os.path.join(checkpoint_dir, "neox_config.yml")
    with open(out_path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)
    return out_path
```

---

### L-4-2: run_all_training — Pseudo-code

```python
def run_all_training(variant_metadata: list[dict]) -> list[dict]:
    state = _load_training_state()   # dict keyed by run_id
    records = list(state.values())   # restore existing records

    for variant in variant_metadata:        # 12 variants
        for scale in [70, 160]:             # 2 scales
            for seed in [1, 2, 3]:          # 3 seeds → 72 total iterations
                run_id = f"{variant['condition']}_{scale}m_s{seed}"
                ckpt_dir = os.path.join(CHECKPOINT_ROOT, run_id)

                # Resume: skip completed runs
                if state.get(run_id, {}).get("status") == "done":
                    continue

                base_cfg = os.path.join(
                    NEOX_REPO,
                    {70: "configs/pythia/70M.yml",
                     160: "configs/pythia/160M.yml"}[scale]
                )
                neox_cfg = build_neox_config(
                    scale, variant["binary_prefix"], seed, ckpt_dir, base_cfg
                )

                record = {
                    "run_id": run_id, "variant": variant["condition"],
                    "scale": scale, "seed": seed,
                    "checkpoint_dir": ckpt_dir, "status": "running",
                    "hf_checkpoint_paths": [], "error_msg": None,
                }
                state[run_id] = record
                _save_training_state(state)   # persist before launch

                exit_code = launch_neox_run(neox_cfg, NEOX_REPO)

                if exit_code == 0:
                    hf_paths = list_checkpoints(ckpt_dir)   # converts to HF format
                    record["hf_checkpoint_paths"] = hf_paths
                    record["status"] = "done"
                else:
                    record["status"] = "error"
                    record["error_msg"] = f"exit_code={exit_code}"

                state[run_id] = record
                _save_training_state(state)
                _upsert(records, record)

    return records
```

**Launch strategy**: Sequential by default — DeepSpeed uses all GPUs per run. For multi-node parallelism, wrap with `concurrent.futures.ProcessPoolExecutor(max_workers=N_NODES)`, pin each worker to a node via `CUDA_VISIBLE_DEVICES`, and use file-locked state writes.
`# ponytail: sequential; add ProcessPoolExecutor per GPU node if cluster available`

---

### L-4-3: Checkpoint Management — Pseudo-code

```python
def list_checkpoints(checkpoint_dir: str) -> list[str]:
    """Discover NeoX raw checkpoints, convert uncoverted ones to HF, return HF paths."""
    raw_steps = sorted(
        pathlib.Path(checkpoint_dir).glob("global_step*"),
        key=lambda p: int(re.search(r"\d+", p.name).group())
    )
    hf_paths = []
    for step_dir in raw_steps:
        hf_out = str(step_dir) + "_hf"
        if not pathlib.Path(hf_out, "config.json").exists():
            convert_checkpoint_to_hf(str(step_dir), hf_out, NEOX_REPO)
        hf_paths.append(hf_out)
    return hf_paths   # len == 10 per completed run


def convert_checkpoint_to_hf(neox_checkpoint: str, output_dir: str, neox_repo: str) -> str:
    """Run tools/convert_to_hf.py via subprocess."""
    script = os.path.join(neox_repo, "tools", "convert_to_hf.py")
    cmd = [
        "python", script,
        "--input_dir",  neox_checkpoint,
        "--output_dir", output_dir,
        "--config_file", os.path.join(os.path.dirname(neox_checkpoint), "neox_config.yml"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"HF conversion failed for {neox_checkpoint}:\n{result.stderr}"
        )
    return output_dir
```

**Idempotency**: Conversion skipped if `config.json` already present in `output_dir`. Safe to re-call after partial failure.

---

### L-4-4: Training State Tracking — Pseudo-code

```python
_STATE_FILE = os.path.join("results", "h-e1", "training_state.json")

def _load_training_state() -> dict:
    if not os.path.exists(_STATE_FILE):
        return {}
    with open(_STATE_FILE) as f:
        return json.load(f)

def _save_training_state(state: dict) -> None:
    """Atomic write to avoid corrupted state on crash."""
    os.makedirs(os.path.dirname(_STATE_FILE), exist_ok=True)
    tmp = _STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, _STATE_FILE)   # POSIX atomic

def _upsert(records: list[dict], record: dict) -> None:
    for i, r in enumerate(records):
        if r["run_id"] == record["run_id"]:
            records[i] = record
            return
    records.append(record)
```

**Resume semantics**:
- `status="done"` → always skip on re-run
- `status="error"` → retry on re-run (transient failure assumed)
- `status="running"` on load → treat as crashed, reset to `"pending"` and retry
  ```python
  for run_id, rec in state.items():
      if rec["status"] == "running":
          rec["status"] = "pending"   # crashed mid-run
  ```

**Error escalation**: After 3 consecutive `"error"` statuses on the same `run_id` (tracked via `error_count` field), log a warning and skip — requires manual investigation. No automatic abort of the full pipeline.

**NFR-4 compliance flag** (checked in analyze.py, not here): if σ(seed scores) > 1pp on control condition, `gate_check` emits a warning in its return dict.
