# H-M2 Logic Design: Scale vs Permutation Equivariance Ablation

**Applied**: Standard PyTorch (Archon KB: no relevant patterns, diffusion domain only)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: API signatures verified from actual h-m1/code/
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**:
- `EquiSSLEncoder.__init__(node_in_dim, edge_in_dim, hidden_dim, latent_dim, num_layers, symmetry, pool)` — symmetry='monomial'|'permutation'
- `EquiSSLEncoder.forward(data: Data) -> Tensor` — returns L2-normalized z, shape [B, latent_dim]
- `train_equi_perm(seed, checkpoint_dir, results_dir, multizoo_root, device, epochs)` — returns best_ckpt path
- `extract_graph_embeddings(encoder, vit_dataset, device, batch_size) -> ndarray` — shape [N, latent_dim]
- `load_equissl_encoder(checkpoint_path, symmetry, device) -> EquiSSLEncoder`
- `extract_all_embeddings(seeds, vit_zoo_root, he1_ckpt_dir, hm1_ckpt_dir, results_dir, device)` — returns (embeddings_dict, vit_dataset)
- `evaluate_linear_probe(embeddings_per_seed, labels, alphas, test_frac, random_state) -> ProbeResult`
- `evaluate_all_models(embeddings_dict, labels, seeds, alphas) -> dict[str, ProbeResult]`
- `paired_ttest(r2_graph, r2_sane) -> StatTestResult`
- `compute_mmd(z_train, z_vit, n_kernels) -> float`
- `compute_mmd_ratio(sane_train_z, equi_train_z, vit_z, n_kernels) -> dict`
- `generate_all_figures(results, stat_tests, embeddings_dict, labels, figures_dir, n_seeds)`

---

## External Dependencies API (Base Hypothesis h-m1)

Signatures verified from actual h-m1/code/ — NOT from specs.

```python
# From: h-m1/code/models/equissl_encoder.py
class EquiSSLEncoder(nn.Module):
    def __init__(
        self,
        node_in_dim: int = 4,
        edge_in_dim: int = 4,
        hidden_dim: int = 256,
        latent_dim: int = 128,
        num_layers: int = 4,
        symmetry: str = 'monomial',   # 'monomial' | 'permutation'
        pool: str = 'mean'
    ): ...

    def forward(self, data: Data) -> Tensor:
        """Returns L2-normalized z. data.batch required for batched graphs."""
        # x: [total_nodes, node_in_dim] -> z: [B, latent_dim]

# From: h-m1/code/training/train_equi_perm.py
def train_equi_perm(
    seed: int,
    checkpoint_dir: str,
    results_dir: str,
    multizoo_root: str,
    device: str = 'cuda',
    epochs: int = None           # defaults to config.EPOCHS (100)
) -> str:                        # returns path to best checkpoint

# From: h-m1/code/evaluation/extract_embeddings.py
def extract_graph_embeddings(
    encoder: nn.Module,
    vit_dataset,                 # ViTZooGraphDataset
    device: str,
    batch_size: int = 32
) -> np.ndarray:                 # [N, latent_dim]

def load_equissl_encoder(
    checkpoint_path: str,
    symmetry: str,               # 'monomial' | 'permutation'
    device: str
) -> EquiSSLEncoder:

def extract_all_embeddings(
    seeds: List[int],
    vit_zoo_root: str,
    he1_ckpt_dir: str,
    hm1_ckpt_dir: str,
    results_dir: str,
    device: str
) -> Tuple[dict, ViTZooGraphDataset]:
    # dict keys: 'sane_seed{i}', 'equi_seed{i}', 'equi_perm_seed{i}'
    # values: ndarray [N_vit, latent_dim]

def get_accuracy_labels(vit_dataset) -> np.ndarray:  # [N_vit]

# From: h-m1/code/evaluation/linear_probe.py
@dataclass
class ProbeResult:
    r2_per_seed: List[float]
    r2_mean: float
    r2_std: float
    model_name: str

def evaluate_linear_probe(
    embeddings_per_seed: List[np.ndarray],  # list of [N, D] per seed
    labels: np.ndarray,                     # [N]
    alphas: List[float] = None,             # default [0.1, 1.0, 10.0, 100.0]
    test_frac: float = 0.2,
    random_state: int = 42
) -> ProbeResult:
    # Note: random_state+i per seed (not per-seed seed) — paired split NOT guaranteed
    # H-M2 must override with paired split logic (see A-1 below)

def evaluate_all_models(
    embeddings_dict: dict,
    labels: np.ndarray,
    seeds: List[int],
    alphas: List[float] = None
) -> dict:                  # {model_name: ProbeResult}

def paired_ttest(
    r2_graph: List[float],
    r2_sane: List[float]
) -> StatTestResult:

# From: h-m1/code/evaluation/mmd_eval.py
def compute_mmd(
    z_train: Tensor,    # [N, D]
    z_vit: Tensor,      # [M, D]
    n_kernels: int = 5
) -> float:

def compute_mmd_ratio(
    sane_train_z: Tensor,
    equi_train_z: Tensor,
    vit_z: Tensor,
    n_kernels: int = 5
) -> dict:              # keys: mmd_sane, mmd_equi, ratio, gate

# From: h-m1/code/evaluation/figures.py
def generate_all_figures(
    results: dict,           # {model_name: ProbeResult}
    stat_tests: dict,
    embeddings_dict: dict,
    labels: np.ndarray,
    figures_dir: str,
    n_seeds: int
) -> None:
```

**Critical note**: `evaluate_linear_probe` uses `random_state + i` (not seed-based paired splits).
H-M2 needs paired evaluation — override with explicit `train_idx/test_idx` per seed (see A-1).

---

## A-1: run_hm2_ablation [Complexity: High, Budget: 4 subtasks]

**Applied**: Standard PyTorch / sklearn

### API Signatures

```python
# h-m2/run_hm2.py

def run_hm2_ablation(
    seeds: List[int],
    vit_zoo_root: str,
    he1_ckpt_dir: str,
    hm1_ckpt_dir: str,
    hm2_ckpt_dir: str,
    multizoo_root: str,
    results_dir: str,
    device: str = 'cuda'
) -> dict:
    """Run full H-M2 ablation. Returns stats dict."""
    # dict keys: r2_equissl_per_seed, r2_perm_per_seed, delta_r2_stats, gate

def _get_paired_split(
    n: int,
    seed: int,
    test_frac: float = 0.2
) -> Tuple[np.ndarray, np.ndarray]:
    """train_idx, test_idx for seed — deterministic, shared between models."""
    # [n*0.8], [n*0.2]

def _probe_with_split(
    z: np.ndarray,           # [N, D]
    labels: np.ndarray,      # [N]
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    alphas: List[float] = None
) -> float:
    """RidgeCV fit on train, R² on test. Returns scalar."""
```

### Pseudo-code

```
for seed in seeds:
    train_idx, test_idx = _get_paired_split(n_vit, seed)  # identical for both models

    z_equi = extract_graph_embeddings(load_equissl_encoder(he1_ckpt, 'monomial', device), ...)
    z_perm = extract_graph_embeddings(load_equissl_encoder(perm_ckpt(seed), 'permutation', device), ...)

    r2_equi[seed] = _probe_with_split(z_equi, labels, train_idx, test_idx)
    r2_perm[seed] = _probe_with_split(z_perm, labels, train_idx, test_idx)

stats = compute_delta_r2_stats(r2_equi, r2_perm)
gate = 'PASS' if stats['delta_r2_mean'] >= 0.05 else 'DOCUMENT'
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | paired_split | `_get_paired_split` — deterministic, seed-indexed |
| L-1-2 | probe_with_split | `_probe_with_split` — RidgeCV on explicit indices |
| L-1-3 | ckpt_routing | perm ckpt path: seed0→hm1, seeds1-4→hm2 |
| L-1-4 | ablation_loop | main loop over seeds, collect r2 lists |

---

## A-2: EquiSSL-perm Training Seeds 1-4 [Complexity: Low, Budget: 1 subtask]

**Applied**: Reuse h-m1 `train_equi_perm` directly — no new code needed.

### API Signatures

```python
# h-m2/train_seeds.py

def train_missing_perm_seeds(
    seeds: List[int],            # [1, 2, 3, 4]
    hm1_ckpt_dir: str,           # seed 0 lives here
    hm2_ckpt_dir: str,           # seeds 1-4 saved here
    multizoo_root: str,
    results_dir: str,
    device: str = 'cuda',
    epochs: int = 100
) -> List[str]:
    """Train missing EquiSSL-perm seeds. Skips if checkpoint exists. Returns ckpt paths."""
    # calls h-m1 train_equi_perm(seed, hm2_ckpt_dir, results_dir, multizoo_root, device, epochs)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | train_wrapper | skip-if-exists guard + call h-m1 `train_equi_perm` |

---

## A-3: compute_delta_r2_stats [Complexity: Low, Budget: 1 subtask]

**Applied**: scipy.stats.ttest_1samp

### API Signatures

```python
# h-m2/stats.py

def compute_delta_r2_stats(
    r2_scale_list: List[float],   # R² per seed for EquiSSL
    r2_perm_list: List[float]     # R² per seed for EquiSSL-perm
) -> dict:
    """
    Returns delta_r2 stats dict.
    Keys: delta_r2 [N], mean, std, ci_low, ci_high, t_stat, p_value, gate
    """
    # delta_r2 = np.array(r2_scale_list) - np.array(r2_perm_list)  # [N]
    # ci = [mean - 1.96*std/sqrt(N), mean + 1.96*std/sqrt(N)]
    # t_stat, p_value = scipy.stats.ttest_1samp(delta_r2, popmean=0)
    # gate = 'PASS' if mean >= 0.05 else 'DOCUMENT'
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | delta_stats | numpy/scipy one-sample t-test, CI, gate label |

---

## A-4: compute_mmd_ratio_hm2 [Complexity: Low, Budget: 1 subtask]

**Applied**: Reuse h-m1 `mmd_eval.compute_mmd` directly.

### API Signatures

```python
# h-m2/stats.py (same file as A-3)

def compute_mmd_subpop(
    z: np.ndarray,               # [N_vit, D] embeddings
    accuracy_labels: np.ndarray, # [N_vit]
    threshold: float = None      # defaults to median
) -> float:
    """MMD between high/low accuracy ViT subpopulations. Returns scalar."""
    # threshold = np.median(accuracy_labels) if threshold is None
    # z_high = z[labels >= threshold]   # [~N/2, D]
    # z_low  = z[labels <  threshold]   # [~N/2, D]
    # calls compute_mmd(torch.from_numpy(z_high), torch.from_numpy(z_low))
    # Note: reuses h-m1/code/evaluation/mmd_eval.compute_mmd (NOT h-e1)

def compare_mmd_subpop(
    z_equi: np.ndarray,
    z_perm: np.ndarray,
    accuracy_labels: np.ndarray
) -> dict:
    """Returns {'mmd_equi': float, 'mmd_perm': float, 'ratio': float}"""
    # ratio = mmd_perm / mmd_equi (>1 means equi better separates subpops)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | mmd_subpop | median split, call h-m1 compute_mmd, return ratio dict |

---

## A-5: generate_figures [Complexity: Medium, Budget: 3 subtasks]

**Applied**: matplotlib/seaborn (reuse h-m1 figures.py style)

### API Signatures

```python
# h-m2/figures.py

def generate_figures(
    results: dict,               # from run_hm2_ablation
    output_dir: str
) -> None:
    """Save 4 figures to output_dir."""

def plot_r2_bar_hm2(
    r2_equi_mean: float, r2_equi_std: float,
    r2_perm_mean: float, r2_perm_std: float,
    sane_r2: float = 0.0721,
    gate_threshold: float = 0.05,
    save_path: str = None
) -> None:
    """Fig 1: Bar chart EquiSSL vs EquiSSL-perm with SANE baseline and gate line."""

def plot_delta_r2_distribution(
    delta_r2: np.ndarray,        # [N_seeds]
    gate_threshold: float = 0.05,
    gate_label: str = 'DOCUMENT',
    save_path: str = None
) -> None:
    """Fig 2: Per-seed ΔR² scatter + mean±std + gate line annotation."""

def plot_tsne_2x2(
    z_equi: np.ndarray,          # [N_vit, D] — seed 0 embeddings
    z_perm: np.ndarray,          # [N_vit, D]
    accuracy_labels: np.ndarray, # [N_vit] — color by accuracy
    l2_norms: np.ndarray,        # [N_vit] — color by model scale
    save_path: str = None
) -> None:
    """Fig 3: 2×2 t-SNE panel (equi/perm × accuracy/l2_norm coloring)."""

def plot_ablation_ladder(
    sane_r2: float,
    perm_r2_mean: float, perm_r2_std: float,
    equi_r2_mean: float, equi_r2_std: float,
    save_path: str = None
) -> None:
    """Fig 4: SANE → EquiSSL-perm → EquiSSL R² progression bar."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| z_equi/z_perm (tsne input) | [53, 128] | seed 0 embeddings for visualization |
| l2_norms | [53] | `np.linalg.norm(raw_weights, axis=-1)` per ViT model |
| delta_r2 | [5] | one per seed |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | bar_delta | Fig 1 + Fig 2 (bar + delta scatter) |
| L-5-2 | tsne_panel | Fig 3 2×2 t-SNE with dual coloring |
| L-5-3 | ladder | Fig 4 ablation ladder |

---

## Summary: Subtask Budget

| Module | Subtasks | Notes |
|--------|----------|-------|
| A-1: run_hm2_ablation | 4 | Core orchestration + paired split |
| A-2: train seeds 1-4 | 1 | Thin wrapper over h-m1 `train_equi_perm` |
| A-3: delta R² stats | 1 | scipy one-liner |
| A-4: MMD subpop | 1 | Reuses h-m1 compute_mmd |
| A-5: figures | 3 | 4 figures, 3 subtasks |
| **Total** | **10** | Within budget |

---

## File Layout

```
h-m2/
  run_hm2.py          # A-1: main orchestration script
  train_seeds.py      # A-2: train EquiSSL-perm seeds 1-4
  stats.py            # A-3 + A-4: delta R² stats + MMD subpop
  figures.py          # A-5: 4 required figures
  config.py           # paths, seeds, hyperparams (extends h-m1/config.py constants)
```

**Import pattern** (verified from h-m1 code):
```python
import sys
sys.path.insert(0, '/path/to/h-m1/code')   # priority for h-m1 modules
from models.equissl_encoder import EquiSSLEncoder
from evaluation.extract_embeddings import extract_graph_embeddings, load_equissl_encoder
from evaluation.mmd_eval import compute_mmd
from training.train_equi_perm import train_equi_perm
```
