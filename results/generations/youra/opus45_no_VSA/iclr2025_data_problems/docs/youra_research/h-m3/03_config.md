# Config: H-M3 (MECHANISM)

Applied: Standard PyTorch/HF defaults (no matching KB pattern found for this config shape).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: `h-m1/code/` does not exist on disk (confirmed via glob — no `config*.py` or any `.py` files found). Architecture doc (03_architecture.md) already analyzed h-m1 directly and documented actual function signatures/behavior; no separate config dataclass exists in h-m1 (params are inline literals in `train_one_run`/`main.py`, e.g. `model_id="EleutherAI/pythia-70m"`, `seeds=(42,)`).
**Config Files Found**: None — no `h-m1/code/config.py` exists to inherit from.
**Pattern Used**: Dataclass (single `Config` class, per architecture spec)

Since h-m1 has no config dataclass to inherit, H-M3 defines its own standalone `Config`, reusing h-m1's *literal* defaults (model_id, base seed) as documented in 03_architecture.md.

---

## M3: Amplification Index (single task, 0 subtasks — all Low complexity)

**Applied**: Standard dataclass config, values taken directly from architecture spec.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-70m"       # matches h-m1 PoC scale (not pythia-1b per PRD)
    strategies: tuple = ("perplexity", "random")    # h-m1 has no "dedup" strategy
    seeds: tuple = (42, 43, 44)                      # 3 seeds (PRD wants 5; PoC-consistent reduction)
    percentile: int = 30                             # perplexity filter keep-percentile
    corpus_size: int = 2000                          # train corpus size per run
    mmlu_subset: int = 500                           # eval subset size (PoC speed; PRD wants full 14,042)
    num_fewshot: int = 5
    batch_size: int = 32
    n_bootstrap: int = 10000
    confidence: float = 0.95
    out_dir: str = "figures/"
```

### Subtasks [0/0 used]

None — single Low-complexity config, no decomposition needed.

---

## Inherited Configuration (Base Hypothesis)

**Verified from**: attempted read of `h-m1/code/config*.py` — file does not exist (glob returned zero matches). No dataclass to inherit.

Instead, the following literal values are carried over from h-m1's actual (inline, non-dataclass) parameters, as documented in H-M3's `03_architecture.md` Codebase Analysis section:

```python
# h-m1 actual inline params (train.py/main.py, no config.py exists):
#   model_id = "EleutherAI/pythia-70m"
#   seeds = (42,)              # h-m1 PoC used only 1 seed
#   strategies = ("perplexity", "random", "inverse_perplexity")  # H-M3 drops inverse_perplexity, no dedup
```

H-M3's `Config.model_id` and base seed `42` are set to match these h-m1 literals for consistency; `seeds` is extended to `(42, 43, 44)` since H-M3 needs multiple seeds per strategy for its own paired bootstrap (h-m1 only needed 1).

**Reused functions** (imported or copied from `h-m1/code/`, not config values):
`train_one_run` (train.py), `load_corpus`, `filter_by_strategy` (data.py) — see 03_architecture.md External Dependencies table.
