---
hypothesis_id: H-M2
phase: config
date: 2026-08-20
author: yoon303b@gmail.com
---

# Configuration: H-M2 — Domain Exposure–Benchmark Correlation Analysis

Applied: N/A — Archon KB not indexed for this domain (similarity < 0.38, image-gen/inductor content only)

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (H-E1 output consumed; H-M1 config referenced)
**Status**: H-M1 config verified from `docs/youra_research/h-m1/03_config.md`; H-M2 uses module-level constants (not dataclasses) per architecture spec
**Config Files Found**: `docs/youra_research/h-m1/03_config.md` (reference), `docs/youra_research/h-m2/03_architecture.md` (defines config.py schema)
**Pattern Used**: module-level constants (architecture specifies `config.py` with plain constants, not dataclasses)

---

## A-1: Project Setup [Complexity: 5, Budget: 2 subtasks]

**Applied**: Standard module-level constants pattern (matches architecture spec)

### Configuration (`config.py`)

```python
# config.py — H-M2 experiment constants
from __future__ import annotations
from pathlib import Path

# ── Model registry ────────────────────────────────────────────────────────────

MODEL_SIZES: list[str] = ["70m", "1b", "6.9b"]

MODEL_IDS: dict[str, str] = {
    "70m": "EleutherAI/pythia-70m",
    "1b": "EleutherAI/pythia-1b",
    "6.9b": "EleutherAI/pythia-6.9b",
}

# ── Checkpoint steps (154 total) ──────────────────────────────────────────────
# Pythia training checkpoints: powers-of-2 early steps + 1000-step increments

CHECKPOINT_STEPS: list[int] = [
    0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
    1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000,
    11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000, 20000,
    21000, 22000, 23000, 24000, 25000, 26000, 27000, 28000, 29000, 30000,
    31000, 32000, 33000, 34000, 35000, 36000, 37000, 38000, 39000, 40000,
    41000, 42000, 43000, 44000, 45000, 46000, 47000, 48000, 49000, 50000,
    51000, 52000, 53000, 54000, 55000, 56000, 57000, 58000, 59000, 60000,
    61000, 62000, 63000, 64000, 65000, 66000, 67000, 68000, 69000, 70000,
    71000, 72000, 73000, 74000, 75000, 76000, 77000, 78000, 79000, 80000,
    81000, 82000, 83000, 84000, 85000, 86000, 87000, 88000, 89000, 90000,
    91000, 92000, 93000, 94000, 95000, 96000, 97000, 98000, 99000, 100000,
    101000, 102000, 103000, 104000, 105000, 106000, 107000, 108000, 109000, 110000,
    111000, 112000, 113000, 114000, 115000, 116000, 117000, 118000, 119000, 120000,
    121000, 122000, 123000, 124000, 125000, 126000, 127000, 128000, 129000, 130000,
    131000, 132000, 133000, 134000, 135000, 136000, 137000, 138000, 139000, 140000,
    141000, 142000, 143000,
]  # len = 154: 11 early (0,1,...,512) + 143 thousand-steps (1000..143000)

# ── Pile domain taxonomy (22 domains) ────────────────────────────────────────
# Exact strings from meta['pile_set_name'] — order matches H-E1 domain axis

PILE_DOMAINS: list[str] = [
    "Pile-CC",
    "PubMed Central",
    "Books3",
    "OpenWebText2",
    "ArXiv",
    "Github",
    "FreeLaw",
    "StackExchange",
    "USPTO Backgrounds",
    "PubMed Abstracts",
    "Gutenberg (PG-19)",
    "OpenSubtitles",
    "Wikipedia (en)",
    "DM Mathematics",
    "Ubuntu IRC",
    "BookCorpus2",
    "EuroParl",
    "HackerNews",
    "YoutubeSubtitles",
    "PhilPapers",
    "NIH ExPorter",
    "Enron Emails",
]  # len = 22

FOCAL_DOMAINS: dict[str, str] = {
    "wikipedia": "Wikipedia (en)",
    "books": "Books3",
}

# ── Benchmark evaluation ──────────────────────────────────────────────────────

TASKS: dict[str, dict] = {
    "mmlu": {"num_fewshot": 5, "metric": "acc,none"},
    "hellaswag": {"num_fewshot": 10, "metric": "acc_norm,none"},
}

BATCH_SIZE: str = "auto"   # VRAM-adaptive; lm-eval handles selection
DTYPE: str = "float"

# ── Floor filtering ───────────────────────────────────────────────────────────

FLOOR_THRESHOLD: float = 0.30        # Both benchmarks must exceed this
MIN_VALID_CHECKPOINTS: int = 100     # Raise if N_valid falls below after filter

# ── Statistical thresholds ────────────────────────────────────────────────────

FISHER_ALPHA: float = 0.10           # p < 0.10 for SHOULD_WORK gate (exploratory)
# Non-standard: 0.10 instead of 0.05 — directional confirmation is primary; p-value is secondary per spec
N_FOCAL_COMPARISONS: int = 4         # P1×1 size + P2×1 size per model (Holm-Bonferroni family)

# ── Decontamination ───────────────────────────────────────────────────────────

NGRAM_SIZE: int = 13
CONTAMINATION_DELTA_THRESHOLD: float = 0.03  # 3pp — use adjusted scores if delta exceeds this

# ── Paths ─────────────────────────────────────────────────────────────────────

H_E1_EXPOSURE_DIR: str = "docs/youra_research/h-e1"
RESULTS_DIR: str = "results/h-m2"
EVAL_CACHE_DIR: str = "results/h-m2/eval_cache"
FIGURES_DIR: str = "docs/youra_research/h-m2/figures"

# ── Reproducibility ───────────────────────────────────────────────────────────

SEED: int = 42
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Checkpoint step list | Complete 154-step list with early powers-of-2 + 1000-step increments to 143000 |
| C-1-2 | Pile domain taxonomy | 22 exact `pile_set_name` strings in canonical order matching H-E1 domain axis index |

---

## YAML Config Schema (`configs/h_m2_config.yaml`)

```yaml
# configs/h_m2_config.yaml
# All fields match config.py constants. Override only fields that differ from defaults.

model:
  sizes: ["70m", "1b", "6.9b"]                 # list[str] — model size keys
  ids:                                           # dict[str, str] — HF model IDs
    "70m": "EleutherAI/pythia-70m"
    "1b": "EleutherAI/pythia-1b"
    "6.9b": "EleutherAI/pythia-6.9b"

eval:
  batch_size: "auto"                             # str — "auto" or int; "auto" = VRAM-adaptive
  dtype: "float"                                 # str — "float" | "float16" | "bfloat16"
  tasks:
    mmlu:
      num_fewshot: 5                             # int — standard MMLU 5-shot
      metric: "acc,none"
    hellaswag:
      num_fewshot: 10                            # int — standard HellaSwag 10-shot
      metric: "acc_norm,none"

filtering:
  floor_threshold: 0.30                          # float — [0, 1]; both benchmarks must exceed
  min_valid_checkpoints: 100                     # int — raise error if N_valid falls below

stats:
  fisher_alpha: 0.10                             # float — significance threshold (exploratory)
  n_focal_comparisons: 4                         # int — Holm-Bonferroni family size

decontamination:
  ngram_size: 13                                 # int — standard 13-gram overlap check
  contamination_delta_threshold: 0.03            # float — 3pp; use adjusted scores if exceeded

paths:
  h_e1_exposure_dir: "docs/youra_research/h-e1"
  results_dir: "results/h-m2"
  eval_cache_dir: "results/h-m2/eval_cache"
  figures_dir: "docs/youra_research/h-m2/figures"

seed: 42
```

---

## Non-Standard Value Rationale

| Field | Value | Reason |
|-------|-------|--------|
| `FISHER_ALPHA` | 0.10 | Exploratory directional gate — per spec, directional count (P1 for ≥2 of 3 sizes) is primary; p-value is secondary |
| `FLOOR_THRESHOLD` | 0.30 | Random chance for 4-way MMLU is 0.25; 0.30 adds a small buffer for reliable signal |
| `NGRAM_SIZE` | 13 | Standard benchmark decontamination practice (EleutherAI convention) |
