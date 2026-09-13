# Config: H-M2 (MECHANISM)

**Type:** MECHANISM — 0 subtasks allocated (all tasks Low complexity, no decomposition)
**Format:** Dataclass (Python) — matches H-M1 pattern for consistency

Applied: Standard PyTorch/dataclass config pattern (flat dataclass, no nested groups) — consistent with H-M1's actual implementation; no stronger KB match found for PoC-scale DL configs.

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m1)
**Status:** Config classes verified from base code — read directly from `h-m1/code/config.py` (see Read tool output above; architecture doc's Config Analysis section also independently verified via Serena `get_symbols_overview`/`find_symbol`).
**Config Files Found:** `h-m1/code/config.py` (single `Config` dataclass, flat, no inheritance)
**Pattern Used:** dataclass (flat, single class)

---

## Inherited Configuration (Base Hypothesis)

### Actual H-M1 Config (verified from code, not spec)

```python
# From: h-m1/code/config.py (ACTUAL CODE — field names confirmed)
@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-70m"   # PoC scale, not pythia-1b per spec
    strategies: tuple = ("perplexity", "random", "inverse_perplexity")
    seeds: tuple = (42,)
    percentile: int = 30
    ngram_n: int = 8
    injection_rate: float = 0.01
    lr: float = 1e-4
    betas: tuple = (0.9, 0.95)
    eps: float = 1e-8
    weight_decay: float = 0.01
    batch_size: int = 16
    seq_len: int = 128
    train_steps: int = 50
    grad_clip: float = 1.0
    corpus_size: int = 2000
    mmlu_subset: int = 500
    n_bootstrap: int = 1000
    out_dir: str = "figures/"
```

**Reused directly**: `train_one_run`, `TextDataset` (train.py), `get_ngrams`, `compute_ccr` (detect.py — aggregate-only), `load_corpus`, `load_mmlu`, `verbalize` (data.py).

---

## H-M2 Config (New — extends field set, not class inheritance)

Not a dataclass subclass — H-M2 has a standalone `Config` in its own `config.py` since it replaces `strategies`/`injection_rate` with `conditions`/`removal_fractions`. All shared fields keep identical names/defaults from H-M1 for drop-in reuse of imported functions.

### Configuration (Python Dataclass)

```python
@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-70m"           # PoC scale, matches h-m1
    conditions: tuple = ("baseline", "high_ccr", "random")
    removal_fractions: tuple = (0.01, 0.02, 0.05)
    seeds: tuple = (42,)                               # ponytail: single seed for PoC; 5 for full run
    ngram_n: int = 8
    percentile: int = 30
    corpus_size: int = 2000
    mmlu_subset: int = 500
    lr: float = 1e-4
    betas: tuple = (0.9, 0.95)
    eps: float = 1e-8
    weight_decay: float = 0.01
    batch_size: int = 16
    seq_len: int = 128
    train_steps: int = 50
    grad_clip: float = 1.0
    n_bootstrap: int = 1000
    out_dir: str = "figures/"
```

Non-standard: `percentile=30` is a leftover H-M1 field name kept for compatibility but unused by H-M2 logic (H-M2 uses top-5% via `removal_fractions`, not `percentile`) — harmless to keep, avoids breaking shared imports.

### Subtasks [0/0 used]

No decomposition — all 9 tasks (R-1..R-9) are Low complexity (4-8) per task allocation; each implemented directly without subtask breakdown.

---

## Notes

- PoC scale intentionally mirrors H-M1 (pythia-70m, 50 train steps, single seed) rather than PRD spec (pythia-1b, 10k steps, 5 seeds, full MMLU) — full run requires multi-GPU cluster per H-M1's established ponytail precedent.
- `n_bootstrap=1000` (not PRD's 10,000) for PoC runtime; sufficient for CI estimation at this scale.
- `mmlu_subset=500` (not full 14,042) for PoC; matches H-M1 evaluation scale.
