# Architecture: h-m1

**Applied**: analysis-only checkpoint-reuse pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 has encoders/{flat_mlp,dwsnet,nft,gnn}.py, data/loader.py (ZooData dataclass, make_loader), evaluation/evaluate.py (eval_spearman, predict_all, gate_check), config.py (ZooConfig seed=42, split 80/10/10). H-M1 reuses all of these via sys.path insertion.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ZooData | `from data.loader import ZooData, make_loader` | `h-e1/code/data/loader.py` |
| FlatMLP | `from encoders.flat_mlp import FlatMLP` | `h-e1/code/encoders/flat_mlp.py` |
| DWSNet | `from encoders.dwsnet import DWSNet` | `h-e1/code/encoders/dwsnet.py` |
| NFT | `from encoders.nft import NFT` | `h-e1/code/encoders/nft.py` |
| GNN | `from encoders.gnn import GNN` | `h-e1/code/encoders/gnn.py` |
| eval_spearman | `from evaluation.evaluate import eval_spearman, predict_all` | `h-e1/code/evaluation/evaluate.py` |
| ZooConfig | `from config import ZooConfig` | `h-e1/code/config.py` |

**Verified from**: `h-e1/code/` (actual implementation)

---

## File Structure

- `h-m1/run_analysis.py` — single entry point
- `h-m1/analysis.py` — core analysis logic (load checkpoints, infer, compute Spearman, gate check)
- `h-m1/visualize.py` — 5 figures
- `h-m1/retrain.py` — fallback: re-train missing NFT/GNN using H-E1 protocol
- `h-m1/config.py` — paths and constants
- `h-m1/04_results.json` — output (auto-generated)
- `h-m1/figures/` — figure output directory

---

## Modules

### Config (`h-m1/config.py`)

**Dependencies**: none

```python
H_E1_CODE_PATH: str = "../h-e1/code"
CHECKPOINT_DIR: str = "../h-e1/checkpoints"
ZOO_PATH: str = "../../data/cifar10_zoo.npz"
RESULTS_PATH: str = "04_results.json"
FIGURES_DIR: str = "figures"
SEED: int = 42
FLAT_MLP_BASELINE_R: float = 0.5567
BOOTSTRAP_N: int = 1000
ENCODER_NAMES: list = ["flat_mlp", "dws_net", "nft", "gnn"]
CHECKPOINT_FILES: dict  # maps encoder_name -> filename
```

---

### AnalysisEngine (`h-m1/analysis.py`)

**Dependencies**: Config, H-E1 encoders, H-E1 data/loader, H-E1 evaluation

```python
def load_encoder(name: str, checkpoint_path: str, zoo: "ZooData",
                 device: str) -> "nn.Module": ...

def run_inference(model: "nn.Module", zoo: "ZooData", device: str,
                  batch_size: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """Returns (preds, true_gap) for test split."""

def bootstrap_ci(preds: np.ndarray, targets: np.ndarray,
                 n: int = 1000, seed: int = 42) -> tuple[float, float, float]:
    """Returns (r, ci_low, ci_high)."""

def run_analysis(zoo: "ZooData", checkpoint_dir: str,
                 device: str) -> dict:
    """
    Returns {
        encoder_name: {"r": float, "ci_low": float, "ci_high": float}
    }
    """

def gate_check(results: dict, baseline_r: float = 0.5567) -> bool:
    """True if any equivariant encoder r > baseline_r."""

def compute_delta_gap(results: dict, baseline_r: float = 0.5567) -> float:
    """mean(equivariant r) - baseline_r."""
```

---

### Visualize (`h-m1/visualize.py`)

**Dependencies**: AnalysisEngine results dict, matplotlib, seaborn

```python
def fig1_bar_chart(results: dict, baseline_r: float,
                   out_dir: str) -> None:
    """Spearman_r per encoder, dashed baseline line. Saves fig1_bar.png."""

def fig2_scatter_grid(preds_dict: dict, true_gap: np.ndarray,
                      out_dir: str) -> None:
    """2x2 scatter: predicted vs true gap per encoder. Saves fig2_scatter.png."""

def fig3_ranking_comparison(results_gap: dict, results_acc: dict,
                             out_dir: str) -> None:
    """Side-by-side bars: gap vs test_acc Spearman per encoder. Saves fig3_ranking.png."""

def fig4_delta_gap(results: dict, baseline_r: float,
                   out_dir: str) -> None:
    """Arrow plot: improvement over FlatMLP. Saves fig4_delta.png."""

def fig5_gap_distribution(true_gap: np.ndarray, out_dir: str) -> None:
    """Histogram of test split gap values. Saves fig5_dist.png."""
```

---

### Retrain (`h-m1/retrain.py`)

**Dependencies**: H-E1 training.train, H-E1 config, Config

```python
def check_missing_checkpoints(checkpoint_dir: str,
                               encoder_names: list) -> list[str]:
    """Returns list of encoder names without checkpoint files."""

def retrain_encoder(name: str, zoo: "ZooData", checkpoint_dir: str,
                    device: str) -> str:
    """
    Re-trains missing encoder using H-E1 protocol.
    Returns path to saved checkpoint.
    Protocol: AdamW lr=1e-3, batch=64, 100 epochs, MSE, seed=42.
    """
```

---

### RunAnalysis (`h-m1/run_analysis.py`)

**Dependencies**: Config, AnalysisEngine, Visualize, Retrain, H-E1 data/loader

```python
def main() -> None:
    """
    1. sys.path.insert(0, H_E1_CODE_PATH)
    2. Load ZooData (H-E1 split, seed=42)
    3. Check/retrain missing checkpoints
    4. run_analysis() -> results dict
    5. Generate 5 figures
    6. gate_check() + compute_delta_gap()
    7. Save 04_results.json
    8. Print [H-M1] log lines
    """
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | File structure, config.py, sys.path bridge to h-e1 | 5 | 1+1+1+2 |
| A-2 | Data Pipeline | Load ZooData via H-E1 loader, extract test split, verify split matches H-E1 | 8 | 2+2+2+2 |
| A-3 | Checkpoint Loader | load_encoder() for all 4 encoders, handle arch params from H-E1 config | 9 | 2+3+2+2 |
| A-4 | Missing Checkpoint Fallback | retrain.py: detect missing NFT/GNN, re-train with H-E1 protocol | 13 | 3+3+4+3 |
| A-5 | Inference & Spearman | run_inference(), bootstrap_ci(), compute_delta_gap(), gate_check() | 10 | 2+2+3+3 |
| A-6 | Visualizations | All 5 figures (bar, scatter grid, ranking, delta, distribution) | 11 | 3+2+3+3 |
| A-7 | Results & Entry Point | run_analysis.py main(), 04_results.json, log lines, sanity assert | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-6], Low(4-8): [A-1, A-2, A-7]
