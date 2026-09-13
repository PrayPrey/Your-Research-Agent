# Logic: H-M1 (MECHANISM)

**Hypothesis:** CCR(perplexity-filtered) - CCR(random) > 0.1, p<0.05 bootstrap

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e1)
**Status:** `h-e1/code/` EXISTS (contradicts 03_architecture.md note that it doesn't — recheck confirms actual files present). API signatures verified from actual code, not spec.
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Relevant Symbols:** `train_one_run` (train.py), `ngram_overlap_detect` (detect.py), `compute_ccr` (model.py), `eval_mmlu_accuracy` (evaluate.py), `inject_benchmark`/`verbalize` (data.py), `Config` (config.py)

**Critical deviations found (spec vs actual code):**
| Spec assumption (03_architecture.md) | Actual code |
|---|---|
| `compute_ccr(model_path, tokenizer, mmlu, corpus, n=8)` — n-gram based | `compute_ccr(scores: np.ndarray, injected_positions: list[int])` — **attribution-mass based**, not n-gram overlap |
| `ngram_overlap_detect(..., n=8)` | default `n=13`, no `n=8` override in H-E1 usage |
| Checkpoints saved to disk, `model_path: str` args | H-E1 keeps `model`/`tokenizer` in memory, no `save_checkpoint` |
| `eval_mmlu_accuracy(model_path, num_fewshot=5)` via lm-eval | actual: `eval_mmlu_accuracy(model, tokenizer, benchmark, device)` — in-memory, single-shot loss comparison, no lm-eval harness |

**Resolution:** H-M1 needs a **detection-based CCR** (fraction of MMLU n-grams appearing in training corpus — PRD FR-3.1/FR-3.2), which is *not* what H-E1's `compute_ccr` computes (that's attribution mass, needs per-token influence scores which H-M1 doesn't produce). H-M1 defines its own `compute_ccr` in `h-m1/code/evaluate.py` built directly on `ngram_overlap_detect` (reused, with `n=8` override). `inject_benchmark`/`verbalize` and `ngram_overlap_detect` are reused as-is from h-e1. `eval_mmlu_accuracy` reused as in-memory pattern (lm-eval harness dropped — PRD FR-4.2 achieved via existing loss-comparison method already validated in H-E1).

**Applied:** contamination-attribution-pipeline pattern (n-gram detection + linear/bootstrap comparison, reused from H-E1) — Archon KB returned no domain-specific hits (confirmed by experiment brief); pattern sourced from H-E1 code directly.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/detect.py (ACTUAL CODE) — reused as-is, call with n=8
def ngram_overlap_detect(corpus: list[str], benchmark: list[dict], n: int = 13) -> set[int]:
    """Returns set of corpus indices whose n-grams overlap benchmark n-grams."""
    ...

# From: h-e1/code/data.py (ACTUAL CODE) — reused as-is
def verbalize(sample: dict) -> str: ...
def inject_benchmark(corpus: list[str], benchmark: list[dict], rate: float, seed: int) -> tuple[list[str], list[int]]:
    """Injects benchmark samples into corpus at random positions. Returns (corpus_copy, injected_positions)."""
    ...

# From: h-e1/code/evaluate.py (ACTUAL CODE) — pattern reused, adapted for full MMLU set
def eval_mmlu_accuracy(model, tokenizer, benchmark: list[dict], device: torch.device) -> float:
    """5-shot NOT implemented in H-E1 (0-shot loss-comparison). H-M1 reuses this pattern (see M-7)."""
    ...
```

**NOT reused** (`h-e1/code/model.py::compute_ccr`): attribution-mass CCR — wrong metric for H-M1's n-gram detection design. H-M1 implements its own `compute_ccr` (see M-6).

---

## A-1 / M-5: Training Loop [Complexity: 12, Budget: 12]

**Applied:** AdamW + cosine warmup training loop (from H-E1 `train_one_run`, extended: real checkpointing, multi-GPU, 15 runs)

### API Signatures

```python
# train.py
def load_model_and_tokenizer(cfg: Config) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Loads Pythia-1B + tokenizer, sets pad_token if missing."""
    ...

def build_optimizer_and_scheduler(model: PreTrainedModel, cfg: Config, total_steps: int):
    """AdamW + cosine schedule w/ warmup. Returns (optimizer, scheduler)."""
    ...

def train_one_run(cfg: Config, corpus: list[str], strategy: str, seed: int) -> str:
    """Trains Pythia-1B on corpus for cfg.train_tokens tokens. Returns checkpoint path."""
    ...

def save_checkpoint(model: PreTrainedModel, tokenizer, strategy: str, seed: int, out_dir: str) -> str:
    """Saves to {out_dir}/checkpoints/{strategy}_seed{seed}/. Returns path."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B=16, T=2048] | per-GPU micro-batch |
| logits | [B, T, V=50304] | Pythia-1B vocab |
| loss | scalar | CE, accumulated over grad_accum=32 steps |

### Pseudo-code

```
1. total_steps = train_tokens // (batch_size * seq_len)   # ~500k tokens/step -> steps
2. model, tokenizer = load_model_and_tokenizer(cfg)
3. optimizer, scheduler = build_optimizer_and_scheduler(model, cfg, total_steps)
4. dataset = TextDataset(corpus, tokenizer, cfg.seq_len)   # reuse H-E1 TextDataset class
5. loader = DataLoader(dataset, batch_size=cfg.batch_size // grad_accum, shuffle=True)
6. for step in range(total_steps):
     batch = next(cyclic_iter(loader))
     loss = model(**batch, labels=batch.input_ids).loss / grad_accum
     loss.backward()
     if (step+1) % grad_accum == 0:
         clip_grad_norm_(model.parameters(), cfg.grad_clip)
         optimizer.step(); scheduler.step(); optimizer.zero_grad()
7. ckpt_path = save_checkpoint(model, tokenizer, strategy, seed, cfg.out_dir)
8. return ckpt_path
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M5-1 | Optimizer/scheduler + single-run loop | `build_optimizer_and_scheduler`, `train_one_run` core loop (steps 1-6 above), reusing H-E1's `TextDataset`/accum pattern |
| L-M5-2 | Checkpointing + 15-run driver hook | `save_checkpoint`, loop-over-(strategy,seed) wiring called from `main.py::run_all` |

---

## A-2: Data Pipeline (M-1, M-2, M-3) [Complexity: 6+8+5]

**Applied:** RedPajama streaming + quality-signal filter (from experiment brief pattern)

### API Signatures

```python
# data.py
def load_redpajama_stream(cfg: Config):
    """streaming=True, partition='head_middle', snapshots=['2023-14'], languages=['en']."""
    ...

def extract_perplexity(sample: dict) -> float:
    """json.loads(sample['quality_signals'])['ccnet_perplexity'][0][2]"""
    ...

def filter_by_strategy(dataset, strategy: str, percentile: int, seed: int, target_tokens: int) -> list[str]:
    """strategy in {'perplexity','random','inverse_perplexity'}. Returns doc texts, size-matched to target_tokens."""
    ...

def load_mmlu() -> list[dict]:
    """cais/mmlu, all subjects, test split. dict keys: question, choices, answer (int)."""
    ...
```

### Pseudo-code (filter_by_strategy — non-trivial: percentile cutoff + token-matching)

```
1. scored = [(extract_perplexity(s), s['raw_content']) for s in dataset]
2. scored.sort(key=lambda x: x[0])
3. cutoff = int(len(scored) * percentile / 100)
4. if strategy == 'perplexity': pool = scored[:cutoff]        # bottom 30% (low ppl)
   elif strategy == 'inverse_perplexity': pool = scored[-cutoff:]  # top 30%
   else: pool = random.sample(scored, cutoff)                 # random, seeded
5. accumulate docs from pool until running token count >= target_tokens (tokenizer.encode len)
6. return doc texts (list[str])
```

### Subtasks: M-1 [2+1+2+1], M-2 [2+2+2+2], M-3 [1+1+2+1] — unchanged from architecture, no logic-level rebudget needed.

---

## A-3: Detection + CCR + Bootstrap (M-4, M-6, M-8) [Complexity: 5+6+6]

**Applied:** n-gram overlap contamination detection (reused H-E1 `ngram_overlap_detect`, n=8)

### API Signatures

```python
# detect.py — thin re-export/wrapper, n hardcoded via Config
from h_e1_style_detect import ngram_overlap_detect  # copy into h-m1/code/detect.py (no verified package import path)

# evaluate.py
def compute_ccr(corpus: list[str], benchmark: list[dict], n: int = 8) -> float:
    """CCR = |MMLU n-grams found in corpus| / |MMLU n-grams|. Uses ngram_overlap_detect + direct n-gram set math (NOT h-e1's attribution-based compute_ccr)."""
    ...

def eval_mmlu_accuracy(model, tokenizer, benchmark: list[dict], device: torch.device) -> float:
    """Reused pattern from h-e1/code/evaluate.py. 5-shot NOT available in reused code -> log as 0-shot loss-comparison; note deviation from PRD FR-4.2 target."""
    ...

def bootstrap_ccr_diff(ccr_ppl: np.ndarray, ccr_rand: np.ndarray, n_bootstrap: int = 1000) -> tuple[float, float]:
    """Returns (mean_diff, p_value). Same algorithm as h-e1 experiment brief bootstrap_ccr_diff."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| ccr_ppl, ccr_rand | [5] | one CCR per seed |
| diffs | [1000] | bootstrap resample diffs |

### Pseudo-code (compute_ccr — differs from h-e1's attribution version, must be explicit)

```
1. mmlu_ngrams = set(); for q in benchmark: mmlu_ngrams |= get_ngrams(f"{q['question']} {q['choices'][q['answer']]}", n)
2. corpus_ngrams = set(); for doc in corpus: corpus_ngrams |= get_ngrams(doc, n)
3. overlap = mmlu_ngrams & corpus_ngrams
4. return len(overlap) / len(mmlu_ngrams) if mmlu_ngrams else 0.0
```

### Subtasks: M-4 [2+1+1+1], M-6 [2+2+1+1], M-8 [1+2+2+1] — unchanged from architecture.

---

## A-4: MMLU Injection, Visualization, Orchestration (M-3 injection reuse, M-9, M-10)

**Applied:** direct reuse of h-e1 `inject_benchmark`/`verbalize` for injection; matplotlib bar/box/hist for viz.

### API Signatures

```python
# data.py
def inject_mmlu(corpus: list[str], mmlu: list[dict], rate: float, seed: int) -> tuple[list[str], list[int]]:
    """Thin wrapper around h-e1's inject_benchmark(corpus, mmlu, rate, seed)."""
    ...

# visualize.py
def plot_ccr_by_strategy(results: dict, out_dir: str) -> None: ...
def plot_ccr_boxplot(results: dict, out_dir: str) -> None: ...
def plot_bootstrap_histogram(diffs: np.ndarray, p_value: float, out_dir: str) -> None: ...
def plot_gate_metrics(target: dict, actual: dict, out_dir: str) -> None: ...

# main.py
def run_all(cfg: Config) -> dict:
    """{strategy: {seed: {'ccr': float, 'mmlu_acc': float, 'ckpt_path': str}}}. Loops 3x5=15 train_one_run + compute_ccr calls, then bootstrap_ccr_diff + all 4 plots."""
    ...
```

### Subtasks: M-9 [2+1+1+1], M-10 [2+2+2+1] — unchanged from architecture.

---

## Self-Validation

- [x] Serena called on h-e1/code/ (base hypothesis exists) — actual signatures verified, deviations documented
- [x] "Codebase Analysis (Serena)" section included
- [x] Archon KB searched, "Applied:" line present
- [x] No ASCII diagrams, docstrings <=2 lines
- [x] M-5 subtasks = 2, within 2-subtask budget
- [x] External Dependencies API section included with actual code signatures
