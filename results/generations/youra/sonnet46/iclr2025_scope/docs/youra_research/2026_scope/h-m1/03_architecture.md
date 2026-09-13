# Architecture: h-m1 — Cross-Distribution Stability of MLP Activation Sparsity Profiles

**Date:** 2026-05-08
**Hypothesis Type:** MECHANISM (INCREMENTAL — extends h-e1)
**Gate:** ICC(3,k) > 0.75 AND all 6 pairwise Kendall's tau >= 0.6

Applied: forward-hook-measurement-pattern (from accelerate.hooks layerwise casting)
Applied: multi-dataset-activation-monitoring (from fszatkowski/activation-sparsity-benchmarking)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260508_scope/h-e1/code/`
**Findings**: h-e1 has 5 modules — `config.py` (ExperimentConfig dataclass), `data_utils.py` (TokenizedDataset, load_alpaca_dataloader, load_wikitext_dataloader), `measure_sparsity.py` (register_hooks, measure_layer_sparsity, run_all_conditions, verify_mechanism), `compute_metrics.py` (compute_cv, compute_kendall_tau, compute_all_metrics, check_gate_conditions), `visualize.py` (6 plot functions + generate_all_figures). run_all_conditions operates over 3 dataset × 4 epsilon combinations; h-m1 extends to 4 distributions with ICC statistics.

---

## External Dependencies (Base Hypothesis)

**Verified from**: `docs/youra_research/20260508_scope/h-e1/code/` (actual implementation)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ExperimentConfig | `sys.path.insert + from config import ExperimentConfig` (run from h-e1/code/) — for h-m1: copy and extend | `h-e1/code/config.py` |
| TokenizedDataset | `from data_utils import TokenizedDataset` | `h-e1/code/data_utils.py` |
| load_alpaca_dataloader | `from data_utils import load_alpaca_dataloader` | `h-e1/code/data_utils.py` |
| load_wikitext_dataloader | `from data_utils import load_wikitext_dataloader` | `h-e1/code/data_utils.py` |
| register_hooks | `from measure_sparsity import register_hooks` | `h-e1/code/measure_sparsity.py` |
| measure_layer_sparsity | `from measure_sparsity import measure_layer_sparsity` | `h-e1/code/measure_sparsity.py` |

**Note**: h-e1 modules are imported by copying or using sys.path manipulation. h-m1/code/ contains new modules that import from a local copy of h-e1 utilities (data_utils.py, measure_sparsity.py, config.py copied into h-m1/code/).

**Important**: h-e1 config uses `model_name = "meta-llama/Meta-Llama-3-8B"` — h-m1 overrides to `"meta-llama/Llama-3.1-8B"` per PRD FR-2.1.

---

## File Organization

```
h-m1/code/
├── config.py              # EXTENDED from h-e1: adds 4-distribution fields + ICC thresholds
├── data_utils.py          # EXTENDED from h-e1: adds load_sst2_dataloader, load_mnli_dataloader
├── measure_sparsity.py    # COPIED from h-e1: register_hooks, measure_layer_sparsity (unchanged)
├── compute_icc.py         # NEW: ICC(3,k) computation via pingouin
├── compute_metrics.py     # EXTENDED from h-e1: adds compute_pairwise_tau, evaluate_gate
├── visualize.py           # NEW: 6 figures for h-m1 (different from h-e1 visualizations)
├── run_experiment.py      # NEW: main orchestrator for h-m1
├── requirements.txt       # NEW: pingouin added to h-e1 dependencies
└── tests/
    ├── test_data_utils.py
    ├── test_compute_icc.py
    └── test_run_experiment.py
```

**Output directories** (created at runtime):
```
h-m1/figures/              # 6 PNG outputs
h-m1/experiment_results.json
```

---

## Module Definitions

### Config (`h-m1/code/config.py`)

**Dependencies**: dataclasses, typing
**Status**: EXTENDED from h-e1

```python
@dataclass
class ExperimentConfig:
    # Model settings
    model_name: str = "meta-llama/Llama-3.1-8B"
    n_layers: int = 32
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # Experiment settings
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42

    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01

    # Sequence length (single value for h-m1)
    max_length: int = 512

    # Dataset identifiers
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"
    sst2_dataset: str = "nyu-mll/glue"
    mnli_dataset: str = "nyu-mll/glue"

    # Output paths
    figures_dir: str = "h-m1/figures"
    results_path: str = "h-m1/experiment_results.json"

    # Gate thresholds
    icc_threshold: float = 0.75
    tau_threshold: float = 0.6

    def __post_init__(self): ...
```

---

### DataUtils (`h-m1/code/data_utils.py`)

**Dependencies**: config.Config, torch, datasets, transformers
**Status**: EXTENDED from h-e1 (adds SST-2, MNLI loaders)

```python
class TokenizedDataset(Dataset):
    def __init__(self, input_ids_list: List[Tensor]): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

def load_alpaca_dataloader(tokenizer, cfg: ExperimentConfig) -> DataLoader: ...
def load_wikitext_dataloader(tokenizer, cfg: ExperimentConfig) -> DataLoader: ...

def load_sst2_dataloader(tokenizer, cfg: ExperimentConfig) -> DataLoader:
    """Load nyu-mll/glue sst2, validation split, 512 samples, 'sentence' field."""
    ...

def load_mnli_dataloader(tokenizer, cfg: ExperimentConfig) -> DataLoader:
    """Load nyu-mll/glue mnli, validation_matched split, 512 samples,
    'premise + [SEP] + hypothesis' concatenated."""
    ...

def load_all_dataloaders(tokenizer, cfg: ExperimentConfig) -> Dict[str, DataLoader]:
    """Return dict: {alpaca, wikitext, sst2, mnli} -> DataLoader."""
    ...
```

---

### MeasureSparsity (`h-m1/code/measure_sparsity.py`)

**Dependencies**: torch, config.ExperimentConfig
**Status**: COPIED from h-e1 (unchanged)

```python
def register_hooks(
    model,
    epsilon: float,
    layer_counts: List[List[float]],
) -> List: ...

def measure_layer_sparsity(
    model,
    dataloader: DataLoader,
    epsilon: float,
    cfg: ExperimentConfig,
) -> np.ndarray:
    """Returns shape (n_layers,) mean sparsity per layer."""
    ...

def measure_all_distributions(
    model,
    dataloaders: Dict[str, DataLoader],
    epsilon: float,
    cfg: ExperimentConfig,
) -> Dict[str, np.ndarray]:
    """Measure sparsity for each distribution. Returns {dist_name: array(32,)}."""
    ...
```

---

### ComputeICC (`h-m1/code/compute_icc.py`)

**Dependencies**: pingouin, pandas, numpy
**Status**: NEW

```python
def build_icc_dataframe(
    sparsity_profiles: Dict[str, np.ndarray]
) -> pd.DataFrame:
    """Build long-format DataFrame: columns [layer, distribution, sparsity], 128 rows."""
    ...

def compute_icc3k(
    sparsity_profiles: Dict[str, np.ndarray]
) -> Dict[str, float]:
    """Run pingouin.intraclass_corr, extract ICC3k value and 95% CI.
    Returns: {icc3k: float, ci_lower: float, ci_upper: float}"""
    ...

def compute_icc_sensitivity(
    sparsity_by_epsilon: Dict[float, Dict[str, np.ndarray]]
) -> Dict[float, Dict[str, float]]:
    """Compute ICC3k for each epsilon value. Returns {epsilon: icc_result_dict}."""
    ...
```

---

### ComputeMetrics (`h-m1/code/compute_metrics.py`)

**Dependencies**: scipy.stats, numpy, itertools
**Status**: EXTENDED from h-e1 (adds pairwise tau, gate evaluation)

```python
def compute_pairwise_tau(
    sparsity_profiles: Dict[str, np.ndarray]
) -> Dict[str, Dict[str, float]]:
    """Compute all C(4,2)=6 pairwise Kendall's tau values.
    Returns: {pair_key: {tau: float, pval: float}} for all pairs."""
    ...

def compute_tau_sensitivity(
    sparsity_by_epsilon: Dict[float, Dict[str, np.ndarray]]
) -> Dict[float, Dict[str, float]]:
    """Compute pairwise tau and tau_min for each epsilon value."""
    ...

def evaluate_gate(
    icc3k: float,
    tau_results: Dict[str, Dict[str, float]],
    cfg: ExperimentConfig,
) -> Dict[str, Any]:
    """Evaluate gate: PASS if icc3k > 0.75 AND all 6 tau >= 0.6.
    Returns: {gate_result, icc3k, tau_min, tau_results, failed_conditions}"""
    ...
```

---

### Visualize (`h-m1/code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy, pandas
**Status**: NEW (h-m1-specific figures, different from h-e1)

```python
def plot_gate_metrics_bar(
    icc3k: float,
    tau_min: float,
    output_path: str,
) -> None:
    """Bar chart: ICC(3,k) and tau_min vs thresholds (0.75, 0.6 dashed lines)."""
    ...

def plot_sparsity_heatmap(
    sparsity_profiles: Dict[str, np.ndarray],
    output_path: str,
) -> None:
    """32 layers x 4 distributions heatmap."""
    ...

def plot_pairwise_tau_matrix(
    tau_results: Dict[str, Dict[str, float]],
    output_path: str,
) -> None:
    """4x4 symmetric heatmap of Kendall's tau values."""
    ...

def plot_icc_confidence(
    icc3k: float,
    ci_lower: float,
    ci_upper: float,
    output_path: str,
) -> None:
    """Bar with 95% CI for ICC3k vs 0.75 threshold."""
    ...

def plot_sparsity_profiles_overlay(
    sparsity_profiles: Dict[str, np.ndarray],
    output_path: str,
) -> None:
    """4 overlaid lines: x=layer index, y=sparsity."""
    ...

def plot_epsilon_sensitivity(
    icc_sensitivity: Dict[float, Dict[str, float]],
    tau_sensitivity: Dict[float, Dict[str, float]],
    output_path: str,
) -> None:
    """ICC(3,k) and tau_min vs 4 epsilon values."""
    ...

def generate_all_figures(
    sparsity_profiles: Dict[str, np.ndarray],
    icc_result: Dict[str, float],
    tau_results: Dict[str, Dict[str, float]],
    gate_result: Dict[str, Any],
    icc_sensitivity: Dict[float, Dict[str, float]],
    tau_sensitivity: Dict[float, Dict[str, float]],
    figures_dir: str,
) -> List[str]:
    """Generate all 6 figures. Returns list of saved file paths."""
    ...
```

---

### RunExperiment (`h-m1/code/run_experiment.py`)

**Dependencies**: all h-m1 modules, torch, transformers, json, os
**Status**: NEW — main entry point

```python
def setup_environment(cfg: ExperimentConfig) -> None:
    """Set seeds (numpy=42, torch=42), create output dirs."""
    ...

def load_model_and_tokenizer(
    cfg: ExperimentConfig,
) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load LLaMA-3.1-8B float16 device_map=auto, set eval mode."""
    ...

def run_sparsity_measurement(
    model,
    dataloaders: Dict[str, DataLoader],
    cfg: ExperimentConfig,
) -> Dict[float, Dict[str, np.ndarray]]:
    """Measure sparsity for all 4 distributions × 4 epsilons.
    Returns: {epsilon: {dist_name: array(32,)}}"""
    ...

def run_statistical_analysis(
    sparsity_by_epsilon: Dict[float, Dict[str, np.ndarray]],
    cfg: ExperimentConfig,
) -> Dict[str, Any]:
    """Compute ICC3k, pairwise tau, sensitivity, gate evaluation.
    Returns full results dict."""
    ...

def save_results(results: Dict[str, Any], output_path: str) -> None:
    """Save experiment_results.json."""
    ...

def main() -> None:
    """Orchestrate full pipeline: setup → load → measure → analyze → visualize → save."""
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Est. Hours |
|----|------|-------------|------------|------------|
| E1 | Environment Setup | Install pingouin, verify GPU, set CUDA_VISIBLE_DEVICES, create output dirs, validate LLaMA-3.1-8B access | 6 (2+1+1+2) | 1.0 |
| E2 | Config Module | Extend h-e1 ExperimentConfig: add SST-2/MNLI dataset IDs, icc_threshold, update model_name to Llama-3.1-8B, adjust path fields | 7 (2+2+1+2) | 1.0 |
| E3 | Dataset Loading Extension | Add load_sst2_dataloader and load_mnli_dataloader to data_utils.py; add load_all_dataloaders() wrapper; reuse TokenizedDataset from h-e1 | 9 (3+2+2+2) | 2.0 |
| E4 | Sparsity Measurement (4 dists) | Copy measure_sparsity.py from h-e1; add measure_all_distributions() wrapper; run 4 dists × 4 epsilons sweep | 10 (3+2+3+2) | 2.0 |
| E5 | ICC(3,k) Computation | Implement compute_icc.py: build_icc_dataframe, compute_icc3k via pingouin, compute_icc_sensitivity for 4 epsilons | 11 (3+3+3+2) | 2.5 |
| E6 | Pairwise Kendall's Tau | Extend compute_metrics.py: compute_pairwise_tau (C(4,2)=6 pairs), tau_min extraction, sensitivity across epsilons | 9 (2+3+2+2) | 2.0 |
| E7 | Gate Evaluation | Implement evaluate_gate(): combined PASS/FAIL check, failure logging with numeric gaps, results dict assembly | 8 (2+2+2+2) | 1.5 |
| E8 | Visualization (6 Figures) | Implement all 6 plot functions in visualize.py: heatmap, overlay lines, tau matrix, ICC CI, gate bar, epsilon sensitivity | 13 (4+2+4+3) | 3.0 |
| E9 | Main Runner Integration | Implement run_experiment.py: setup_environment, load_model_and_tokenizer, run_sparsity_measurement, run_statistical_analysis, save_results, main() | 14 (4+4+3+3) | 3.0 |
| E10 | Results JSON + Gate Reporting | Structured experiment_results.json with all metrics, per-epsilon sensitivity, gate status; stdout summary with all 6 tau values | 8 (2+2+2+2) | 1.5 |
| E11 | Testing | Unit tests: test_data_utils (SST-2/MNLI loaders with mock tokenizer), test_compute_icc (known ICC fixture), test_run_experiment (end-to-end smoke test) | 10 (3+2+3+2) | 2.5 |

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): [E9]
- Medium (9-13): [E3, E4, E5, E6, E8, E11]
- Low (4-8): [E1, E2, E7, E10]

**Total Task Budget**: 11 epics (within 30-task budget)
**Estimated Total Hours**: ~21.5 hours

---

## Requirements

```
# h-m1/code/requirements.txt
torch>=2.0
transformers>=4.40
datasets>=2.18
numpy>=1.24
scipy>=1.11
pingouin>=0.5.4
pandas>=2.0
matplotlib>=3.7
seaborn>=0.12
```

---

## Data Flow

- `run_experiment.py` → loads model + tokenizer
- `data_utils.py` → builds 4 DataLoaders (alpaca, wikitext, sst2, mnli)
- `measure_sparsity.py` → produces `{epsilon: {dist: array(32,)}}` (16 measurements)
- `compute_icc.py` → produces ICC3k + CI per epsilon
- `compute_metrics.py` → produces 6 pairwise tau values per epsilon
- `compute_metrics.py:evaluate_gate` → PASS/FAIL determination
- `visualize.py` → 6 PNG files in `h-m1/figures/`
- `run_experiment.py:save_results` → `h-m1/experiment_results.json`
