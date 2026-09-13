---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
phase: "Phase 3"
generated_at: "2026-08-20"
---

# Architecture: h-e1 — Domain Exposure Trajectory Pipeline

Applied: green-field standard layout

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase found
**Analyzed Path**: N/A
**Findings**: New implementation from scratch — no prior code to reuse

---

## File Structure

```
h-e1/
  src/
    data/
      loader.py          # MMapIndexedDataset wrapper + index map path resolution
      domain_lookup.py   # Build/cache doc→domain lookup from EleutherAI/pile
    compute/
      trajectories.py    # Core: compute_domain_exposure_trajectories()
    analysis/
      stats.py           # variance stats + Spearman correlation
    visualization/
      figures.py         # All 4 matplotlib figure generators
    run.py               # CLI entry point
  data/                  # gitignored: index maps (~32 GB), domain lookup cache
  figures/               # output PNG files
  requirements.txt
```

---

## Modules

### DataLoader (`src/data/loader.py`)

**Dependencies**: `torch`, `numpy`, `MMapIndexedDataset` (from cloned `EleutherAI/pythia/utils/mmap_dataset.py`)

```python
import sys
import numpy as np
from pathlib import Path

CHECKPOINT_STEPS: list[int]  # [0,1,2,4,8,16,32,64,128,256,512] + [1000..143000 step 1000]
TOKENS_PER_STEP: int = 2_097_152
SEQ_LEN: int = 2049
MODEL_SIZES: list[str]  # ["70m","160m","410m","1b","1.4b","2.8b","6.9b","12b", + deduped]

def get_dataset(idxmap_prefix: str) -> "MMapIndexedDataset":
    """Load MMapIndexedDataset from prefix path (no .bin/.idx extension)."""
    ...

def step_to_sample(step: int) -> int:
    """step * TOKENS_PER_STEP // SEQ_LEN"""
    ...

def build_checkpoint_steps() -> list[int]:
    """Returns sorted list of 154 checkpoint step values."""
    ...
```

---

### DomainLookup (`src/data/domain_lookup.py`)

**Dependencies**: `datasets` (HuggingFace), `pickle`, `tqdm`

```python
from pathlib import Path

PILE_DOMAINS: list[str]  # 22 canonical domain names

def build_domain_lookup(
    cache_path: Path,
    streaming: bool = True,
) -> dict[int, str]:
    """
    Stream EleutherAI/pile, build {global_doc_idx: pile_set_name}.
    Saves to cache_path (pickle). One-time ~24h operation.
    Returns loaded dict if cache_path exists.
    # ponytail: full dict in RAM (~few GB); use sqlite if memory exceeds 16 GB
    """
    ...

def load_domain_lookup(cache_path: Path) -> dict[int, str]:
    """Load cached pickle. Raises FileNotFoundError if not built yet."""
    ...
```

---

### Trajectories (`src/compute/trajectories.py`)

**Dependencies**: `numpy`, `DataLoader`, `DomainLookup`

```python
import numpy as np

def compute_domain_exposure_trajectories(
    dataset,                        # MMapIndexedDataset
    doc_to_domain: dict[int, str],
    checkpoint_steps: list[int],
    domain_names: list[str],        # ordered 22-element list
) -> np.ndarray:
    """
    Incremental accumulation over checkpoint_steps.
    Returns shape (22, 154). Asserts shape on exit.
    Logs per checkpoint: step, domain_counts, total_tokens.
    """
    ...
```

---

### Stats (`src/analysis/stats.py`)

**Dependencies**: `numpy`, `scipy`

```python
import numpy as np
from scipy.stats import spearmanr

def compute_variance_stats(trajectories: np.ndarray) -> dict:
    """
    Returns: {per_domain_std: (22,), n_domains_passing: int, gate_passed: bool}
    Threshold sensitivity at [0.0001, 0.0005, 0.001, 0.005, 0.01].
    """
    ...

def compute_spearman_matrix(
    all_stds: dict[str, np.ndarray]  # {model_size: (22,) std array}
) -> np.ndarray:
    """Returns (16, 16) Spearman rho matrix over domain-std vectors."""
    ...

def check_gate(
    results: dict[str, dict],  # {model_size: variance_stats}
    min_domains: int = 10,
    min_model_sizes: int = 8,
) -> bool:
    """Gate: n_domains_passing >= min_domains in >= min_model_sizes."""
    ...
```

---

### Figures (`src/visualization/figures.py`)

**Dependencies**: `matplotlib`, `seaborn`, `numpy`

```python
from pathlib import Path
import numpy as np

def plot_gate_metrics(
    per_domain_std: np.ndarray,
    domain_names: list[str],
    out_path: Path,
    threshold: float = 0.001,
) -> None:
    """Bar chart: per-domain std; green/red bars; threshold line. Saves gate_metrics.png."""
    ...

def plot_trajectories(
    trajectories: np.ndarray,
    domain_names: list[str],
    checkpoint_steps: list[int],
    out_path: Path,
    n_top: int = 5,
) -> None:
    """Line plot: top-5 and bottom-5 variance domains. Saves trajectories.png."""
    ...

def plot_variance_heatmap(
    all_stds: dict[str, np.ndarray],
    domain_names: list[str],
    out_path: Path,
) -> None:
    """22 domains x 16 model sizes heatmap. Saves variance_heatmap.png."""
    ...

def plot_spearman_matrix(
    rho_matrix: np.ndarray,
    model_sizes: list[str],
    out_path: Path,
) -> None:
    """16x16 correlation matrix heatmap. Saves spearman_matrix.png."""
    ...
```

---

### Runner (`src/run.py`)

**Dependencies**: all src modules above, `argparse`

```python
def main() -> None:
    """
    CLI flags:
      --idxmap-dir PATH       root dir of unsharded index map files
      --domain-cache PATH     path to doc_to_domain.pkl
      --figures-dir PATH      output dir for figures (default: ../figures/)
      --poc                   run 3-size subset [70m, 1b, 6.9b] only
      --build-lookup          build domain lookup and exit (one-time step)
      --model-sizes STR...    override model size list
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Setup & Data Download | Project structure, requirements.txt, git LFS clone instructions, unshard script call | 5 | 1+1+1+2 |
| E2 | Domain Lookup Build | Implement domain_lookup.py; stream EleutherAI/pile; build+cache {doc_idx: domain} pickle | 14 | 3+2+4+5 |
| E3 | Trajectory Computation | Implement loader.py + trajectories.py; incremental accumulation; shape assertion; per-checkpoint logging | 15 | 4+3+4+4 |
| E4 | Statistical Analysis | Implement stats.py; variance stats, threshold sensitivity, Spearman matrix, gate check | 9 | 2+2+3+2 |
| E5 | Visualization | Implement figures.py; all 4 plots saved to figures/ | 8 | 2+1+2+3 |
| E6 | CLI Runner & PoC Run | Implement run.py CLI; run 3-size PoC (70M/1B/6.9B); verify gate; then full 16-size run | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [E2, E3], Medium(9-13): [E4, E6], Low(4-8): [E1, E5]

**Task Dependencies**:
- E2 → E1
- E3 → E1, E2
- E4 → E3
- E5 → E3, E4
- E6 → E3, E4, E5

---

## External Tool Integration

| Tool | Source | Used In |
|------|--------|---------|
| `MMapIndexedDataset` | `git clone https://github.com/EleutherAI/pythia` → `utils/mmap_dataset.py` | `src/data/loader.py` |
| `unshard_memmap.py` | same repo → `utils/unshard_memmap.py` | one-time CLI command |
| Index map files | `git lfs clone https://huggingface.co/datasets/EleutherAI/pythia_deduped_pile_idxmaps` | `data/` dir |
| Pile domain labels | `load_dataset("EleutherAI/pile", streaming=True)` | `src/data/domain_lookup.py` |

**Import pattern** (add pythia repo to sys.path or copy file):
```python
sys.path.insert(0, "/path/to/EleutherAI/pythia")
from utils.mmap_dataset import MMapIndexedDataset
```
