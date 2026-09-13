---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
phase: "Phase 3"
generated_at: "2026-08-20"
---

# Logic: h-e1 — Domain Exposure Trajectory Pipeline

Applied: Standard numpy incremental accumulation pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase found
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## E3: Trajectory Computation [Complexity: 15, Budget: 4 subtasks]

### L-E3-1: `step_to_sample()` + `build_checkpoint_steps()`

```python
# src/data/loader.py

TOKENS_PER_STEP: int = 2_097_152
SEQ_LEN: int = 2049
CHECKPOINT_STEPS: list[int] = (
    [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    + list(range(1000, 144000, 1000))  # 143 steps: 1000..143000
)  # len == 154

MODEL_SIZES: list[str] = [
    "70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b",
    "70m-deduped", "160m-deduped", "410m-deduped", "1b-deduped",
    "1.4b-deduped", "2.8b-deduped", "6.9b-deduped", "12b-deduped",
]

def step_to_sample(step: int) -> int:
    """Convert training step to sample index. Returns int."""
    return step * TOKENS_PER_STEP // SEQ_LEN
    # step=0 → 0, step=1 → 1023, step=143000 → ~146M

def build_checkpoint_steps() -> list[int]:
    """Returns sorted list of 154 checkpoint step values."""
    return sorted(set(CHECKPOINT_STEPS))  # already sorted, set() guards duplicates
    # assert len(result) == 154

def get_dataset(idxmap_prefix: str) -> "MMapIndexedDataset":
    """Load MMapIndexedDataset from prefix path (no .bin/.idx extension)."""
    from utils.mmap_dataset import MMapIndexedDataset
    return MMapIndexedDataset(idxmap_prefix)
```

**Subtasks [1/4]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-1 | step_to_sample + build_checkpoint_steps | Exact integer formulas; assert len==154 on build |

---

### L-E3-2: `compute_domain_exposure_trajectories()` — Incremental Loop

```python
# src/compute/trajectories.py

import numpy as np
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from utils.mmap_dataset import MMapIndexedDataset

def compute_domain_exposure_trajectories(
    dataset: "MMapIndexedDataset",
    doc_to_domain: dict[int, str],
    checkpoint_steps: list[int],   # len == 154, sorted ascending
    domain_names: list[str],       # len == 22, canonical order
) -> np.ndarray:                   # shape (22, 154)
    """Incremental domain accumulation across checkpoints."""
    ...
```

**Pseudo-code:**

```
domain_to_idx = {name: i for i, name in enumerate(domain_names)}  # {str: int}
n_domains = 22
n_checkpoints = 154

cumulative_counts = np.zeros(n_domains, dtype=np.int64)  # [22]
trajectories = np.zeros((n_domains, n_checkpoints), dtype=np.float64)  # [22, 154]

step_ptr = 0  # current sample pointer (int)

for t, step in enumerate(checkpoint_steps):       # t in [0..153]
    target_sample = step * TOKENS_PER_STEP // SEQ_LEN   # int

    # Advance from step_ptr to target_sample (exclusive)
    for sample_idx in range(step_ptr, target_sample):
        doc_idx = dataset.doc_idx[sample_idx]     # int, global doc index
        domain = doc_to_domain.get(doc_idx, "Unknown")
        if domain in domain_to_idx:
            cumulative_counts[domain_to_idx[domain]] += 1

    step_ptr = target_sample

    total = cumulative_counts.sum()
    if total > 0:
        trajectories[:, t] = cumulative_counts / total
    else:
        trajectories[:, t] = 0.0

    # per-checkpoint log (see L-E3-3)
    _log_checkpoint(step, cumulative_counts, total, domain_names)

assert trajectories.shape == (22, 154), f"Bad shape: {trajectories.shape}"
return trajectories
```

**Array shapes:**

| Variable | Shape | dtype |
|----------|-------|-------|
| cumulative_counts | [22] | int64 |
| trajectories | [22, 154] | float64 |
| doc_idx (per sample) | scalar | int |

**Subtasks [2/4]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-2 | compute_domain_exposure_trajectories | Full incremental loop; maintain step_ptr; normalize at each checkpoint |

---

### L-E3-3: Per-Checkpoint Logging + Shape Assertion

```python
# src/compute/trajectories.py (helper, called inside loop)

import logging

def _log_checkpoint(
    step: int,
    cumulative_counts: np.ndarray,  # [22]
    total_tokens: int,
    domain_names: list[str],
) -> None:
    """Log checkpoint state."""
    counts_dict = {domain_names[i]: int(cumulative_counts[i])
                   for i in range(len(domain_names))}
    logging.info(
        f"Checkpoint step{step}: domain_counts={counts_dict}, total_tokens={total_tokens}"
    )
```

**Shape assertion (inline after loop):**

```python
assert trajectories.shape == (22, 154), (
    f"trajectories.shape={trajectories.shape}, expected (22, 154)"
)
# Also assert no NaN
assert not np.isnan(trajectories).any(), "NaN in trajectories"
```

**Subtasks [3/4]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-3 | Logging + assertion | Per-checkpoint dict log; shape + NaN assertions after loop |

---

### L-E3-4: Multi-Model-Size Loop Orchestration

```python
# src/run.py (orchestration logic)

def run_all_model_sizes(
    idxmap_dir: Path,
    doc_to_domain: dict[int, str],
    checkpoint_steps: list[int],   # [154]
    domain_names: list[str],       # [22]
    model_sizes: list[str],        # [16] or subset
    output_dir: Path,
) -> dict[str, np.ndarray]:        # {model_size: (22, 154)}
    """Process each model size; save .npy; return all trajectories."""
    ...
```

**Pseudo-code:**

```
results = {}

for model_size in model_sizes:
    idxmap_prefix = idxmap_dir / f"pile_0.87_deduped_text_document"
    # ponytail: single shared index map; if per-size maps exist, parameterize prefix
    dataset = get_dataset(str(idxmap_prefix))

    traj = compute_domain_exposure_trajectories(
        dataset, doc_to_domain, checkpoint_steps, domain_names
    )  # → (22, 154)

    out_path = output_dir / f"trajectories_{model_size}.npy"
    np.save(out_path, traj)
    logging.info(f"Saved {out_path}")

    results[model_size] = traj

return results
```

**Edge cases:**
- If idxmap file missing for a size: log warning, skip (do not crash entire run)
- `--poc` flag: pass `model_sizes=["70m", "1b", "6.9b"]` only

**Subtasks [4/4]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-4 | Multi-model loop | Iterate model_sizes; save trajectories_{size}.npy; skip missing files with warning |

---

## E2: Domain Lookup Build [Complexity: 14, Budget: 3 subtasks]

### L-E2-1: `build_domain_lookup()` — Streaming + Pickle Cache

```python
# src/data/domain_lookup.py

from pathlib import Path
import pickle
from tqdm import tqdm
from datasets import load_dataset

PILE_DOMAINS: list[str] = [
    "Pile-CC", "PubMed Central", "Books3", "OpenWebText2", "ArXiv",
    "GitHub", "FreeLaw", "StackExchange", "USPTO Backgrounds",
    "PubMed Abstracts", "Gutenberg (PG-19)", "OpenSubtitles",
    "Wikipedia (en)", "DM Mathematics", "Ubuntu IRC", "BookCorpus2",
    "EuroParl", "HackerNews", "YoutubeSubtitles", "PhilPapers",
    "NIH ExPorter", "Enron Emails",
]  # len == 22

def build_domain_lookup(
    cache_path: Path,
    streaming: bool = True,
) -> dict[int, str]:
    """Stream EleutherAI/pile; build {global_doc_idx: pile_set_name}; pickle cache.
    # ponytail: full dict in RAM (~few GB); use sqlite if memory exceeds 16 GB
    """
    ...
```

**Pseudo-code:**

```
doc_to_domain = {}    # {int: str}
doc_idx = 0

dataset = load_dataset("EleutherAI/pile", split="train", streaming=True)

for example in tqdm(dataset, desc="Building domain lookup"):
    domain = example["meta"]["pile_set_name"]
    doc_to_domain[doc_idx] = domain
    doc_idx += 1

with open(cache_path, "wb") as f:
    pickle.dump(doc_to_domain, f, protocol=pickle.HIGHEST_PROTOCOL)

logging.info(f"Domain lookup built: {len(doc_to_domain)} docs → {cache_path}")
return doc_to_domain
```

**Subtasks [1/3]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-1 | build_domain_lookup | Streaming loop with tqdm; enumerate global doc_idx; pickle save |

---

### L-E2-2: Cache Check + Load Logic

```python
def load_domain_lookup(cache_path: Path) -> dict[int, str]:
    """Load cached pickle. Raises FileNotFoundError if not built yet."""
    if not cache_path.exists():
        raise FileNotFoundError(
            f"Domain lookup cache not found: {cache_path}. "
            "Run with --build-lookup first (~24h one-time operation)."
        )
    with open(cache_path, "rb") as f:
        return pickle.load(f)

def get_or_build_domain_lookup(
    cache_path: Path,
    force_rebuild: bool = False,
) -> dict[int, str]:
    """Return cached lookup if exists, else build it."""
    if cache_path.exists() and not force_rebuild:
        logging.info(f"Loading domain lookup from cache: {cache_path}")
        return load_domain_lookup(cache_path)
    logging.info("Cache not found — building domain lookup (~24h)...")
    return build_domain_lookup(cache_path)
```

**Subtasks [2/3]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-2 | Cache check + load | exists() guard; load_domain_lookup raises FileNotFoundError with helpful message |

---

### L-E2-3: Unknown Document Handling

```python
# Applied inline in compute_domain_exposure_trajectories()

UNKNOWN_DOMAIN: str = "Unknown"

# During lookup:
domain = doc_to_domain.get(doc_idx, UNKNOWN_DOMAIN)
if domain not in domain_to_idx:
    # domain is "Unknown" or unmapped — skip; do not add to cumulative_counts
    unknown_count += 1  # track for logging only
    continue

# After loop: log unknown rate
unknown_rate = unknown_count / max(total_samples, 1)
if unknown_rate > 0.01:  # >1% unknown → warn
    logging.warning(f"Unknown doc rate: {unknown_rate:.2%} ({unknown_count} samples)")
```

**Edge cases:**
- doc_idx beyond lookup size: falls through `.get()` default → "Unknown" → skipped
- domain string not in PILE_DOMAINS canonical list: same path → skipped + warning
- All-unknown checkpoint (step=0): `total=0` → `trajectories[:, 0] = 0.0` (safe)

**Subtasks [3/3]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-3 | Unknown doc handling | .get() default "Unknown"; skip in counts; warn if >1% unknown rate |
