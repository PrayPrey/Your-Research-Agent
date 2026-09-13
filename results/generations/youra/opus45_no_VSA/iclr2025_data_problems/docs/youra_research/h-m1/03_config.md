# Config: H-M1 (MECHANISM)

**Applied:** No domain-specific KB pattern found (novel CDCA research area) — used standard PyTorch/dataclass config pattern.

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e1)
**Status:** h-e1/code/config.py exists — read directly (Serena not needed, file found via Glob).
**Config Files Found:** `docs/youra_research/h-e1/code/config.py`
**Pattern Used:** dataclass

**Verified field names/values from actual h-e1 code** (differ from h-e1 spec — e.g. spec used different scale values, actual code is a CPU PoC at 70M scale):
- `model_id="EleutherAI/pythia-70m"`, `ngram_n=13`, `lr=1e-4`, `weight_decay=0.01`, `batch_size=32`, `train_steps=5`, `seed=42`, `max_seq_len=128`, `corpus_size=500`, `mmlu_subset=100`

H-M1 is full-scale MECHANISM (not PoC): does NOT inherit h-e1's CPU-scale values (70M model, 500 corpus, 5 steps). Only the **schema shape** and `injection_rates` values are reused; `ngram_n` changes 13→8 per PRD FR-3.1 (ConTAM recommendation).

---

## M-1..M-10: Full Config

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    # Model
    model_id: str = "EleutherAI/pythia-1b"

    # Data strategies
    strategies: tuple = ("perplexity", "random", "inverse_perplexity")
    seeds: tuple = (42, 43, 44, 45, 46)
    percentile: int = 30  # bottom/top 30% by ccnet_perplexity

    # Contamination detection
    ngram_n: int = 8  # ConTAM recommendation (h-e1 used 13; changed per PRD FR-3.1)
    injection_rates: tuple = (0.001, 0.005, 0.01)  # inherited from h-e1 calibration

    # Optimizer (AdamW, from EleutherAI/pythia-1b.yml)
    lr: float = 2.5e-4
    betas: tuple = (0.9, 0.95)
    eps: float = 1e-8
    weight_decay: float = 0.1

    # LR schedule (cosine + warmup)
    warmup_ratio: float = 0.01
    min_lr: float = 2.5e-5

    # Training
    batch_size: int = 512
    seq_len: int = 2048
    train_tokens: int = 1_000_000_000
    grad_clip: float = 1.0

    # Bootstrap stats
    n_bootstrap: int = 1000

    # Eval
    mmlu_num_fewshot: int = 5

    out_dir: str = "figures/"
```

Matches architecture's `config.py` spec exactly (03_architecture.md lines 40-59) — no drift.

### Subtasks

None allocated (budget = 0; config is a single flat dataclass, no decomposition needed).

---

## Inherited Configuration (Base Hypothesis h-e1)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE, verified)
@dataclass
class Config:  # h-e1, CPU PoC scale
    model_id: str = "EleutherAI/pythia-70m"
    injection_rates: list = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    ngram_n: int = 13
    lr: float = 1e-4
    weight_decay: float = 0.01
    betas: tuple = (0.9, 0.95)
    batch_size: int = 32
    seed: int = 42
    max_seq_len: int = 128
    corpus_size: int = 500
    mmlu_subset: int = 100
```

**Reused in H-M1:** dataclass pattern, `injection_rates` values (subset: 0.001/0.005/0.01), `betas`.
**NOT reused:** `model_id` (70m→1b), `ngram_n` (13→8, per ConTAM/PRD FR-3.1), `lr`/`weight_decay` (h-e1 PoC values → h-m1 uses actual Pythia-1B training config), `batch_size` (32→512), `seed`→`seeds` (single→5-seed tuple for bootstrap CI), no `corpus_size`/`mmlu_subset`/`train_steps` truncation (H-M1 is full training run, not PoC).

**Verified from:** `docs/youra_research/h-e1/code/config.py` (actual implementation, read directly).
