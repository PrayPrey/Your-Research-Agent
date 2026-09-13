# Architecture: H-M2

**Type:** MECHANISM | **Tier:** FULL | **Epic Range:** 6-12

Applied: HF datasets/cache loading pattern (reused from H-M1 `data.py`)
Applied: H2O official repo eviction pattern (heavy-hitter + recent window, ratio-controlled)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Patterns found from base code — H-M1 `code/` is flat-module style (`config.py`, `data.py`, `entropy.py`, `stats.py`, `visualize.py`, `run_experiment.py`), no package/`__init__.py`. H-M2 follows same flat layout for consistency.
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**:
- `entropy_matrix.npy` shape `[180, 32, 32]` (n_samples, layers, heads), rows **domain-blocked** in `DOMAINS` order (30 samples/domain, H-M1 `config.py`) — H-M2 stratification must reconstruct per-sample domain index from this same block order.
- `domain_means.json` = dict[domain_name -> scalar mean entropy] (6 keys). Median of these 6 values determines high/low domain split (domain-level stratification, not per-sample).
- H-M1 has no H2O/eviction code — new module required.
- Reuse as-is: `config.py` (DOMAINS, DOMAIN_CATEGORIES, DataConfig, ModelConfig), `data.py` (load_longbench_v2, sample_domain, tokenize_probe).

---

## File Structure

- `h-m2/code/config.py` — extends H-M1 config with EvictionConfig, StratConfig
- `h-m2/code/data.py` — reuse H-M1 loader + import base samples
- `h-m2/code/stratify.py` — load H-M1 artifacts, median split by domain entropy
- `h-m2/code/h2o_eviction.py` — H2O KV cache eviction wrapper
- `h-m2/code/inference.py` — run generation at 3 conditions (full/40%/80%), compute accuracy
- `h-m2/code/stats.py` — t-test, Mann-Whitney, Cohen's d
- `h-m2/code/visualize.py` — bar chart (mandatory), box plot, scatter, heatmap
- `h-m2/code/run_experiment.py` — pipeline orchestration

## External Dependencies (Base Hypothesis + H2O)

### Module Paths (From Actual H-M1 Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| DOMAINS, DOMAIN_CATEGORIES | `from config import DOMAINS, DOMAIN_CATEGORIES` (copy into h-m2/code/config.py) | `h-m1/code/config.py` |
| ModelConfig | `from config import ModelConfig` (copy) | `h-m1/code/config.py` |
| load_longbench_v2, sample_domain, tokenize_probe | `from data import load_longbench_v2, sample_domain, tokenize_probe` (copy file) | `h-m1/code/data.py` |
| entropy_matrix.npy | loaded via `np.load("../h-m1/code/entropy_matrix.npy")` | `h-m1/code/entropy_matrix.npy` |
| domain_means.json | loaded via `json.load(open("../h-m1/code/domain_means.json"))` | `h-m1/code/domain_means.json` |

**Verified from**: `h-m1/code/` (actual implementation, not spec — H-M1 03_architecture.md not read; code is source of truth)

### H2O Repository Integration

| Repository | Usage |
|------------|-------|
| FMInference/H2O | Primary — `h2o_hf/` dir provides `H2OKVCache_LayerWise` / attention hook pattern for real KV eviction (heavy-hitter + recent, ratio-controlled) |
| awslabs/keys_values | Fallback — `H2OKVCache` class, per-batch eviction |

Vendoring approach: pip-install not available for H2O (no PyPI package) — clone `FMInference/H2O` into `h-m2/code/external/h2o/` at setup time (Epic A-2), import `H2OKVCache_LayerWise` from `external/h2o/h2o_hf/utils_hh/modify_llama.py` (or closest matching file in cloned repo; exact filename verified during Phase 4 clone).

---

## Modules

### StratConfig / EvictionConfig (`config.py`)

**Dependencies**: none

```python
@dataclass
class StratConfig:
    entropy_matrix_path: str = "../h-m1/code/entropy_matrix.npy"
    domain_means_path: str = "../h-m1/code/domain_means.json"

@dataclass
class EvictionConfig:
    retention_ratios: tuple = (1.0, 0.8, 0.4)  # full, moderate, aggressive
    heavy_ratio_frac: float = 0.5   # of retention_ratio
    recent_ratio_frac: float = 0.5
```

### stratify.py

**Dependencies**: config.py, numpy, json

```python
def load_entropy_artifacts(strat_config: StratConfig) -> tuple[np.ndarray, dict]: ...
def domain_median_split(domain_means: dict) -> tuple[list[str], list[str]]:
    """Returns (high_entropy_domains, low_entropy_domains) by median(domain_means.values())"""
def assign_sample_groups(domains_order: list[str], samples_per_domain: int,
                          high_domains: list[str]) -> np.ndarray:
    """Returns [n_samples] bool array: True=high-entropy group. Uses domain-blocked row order from H-M1."""
```

### h2o_eviction.py

**Dependencies**: torch, transformers, external/h2o (vendored)

```python
class H2OWrapper:
    def __init__(self, model, retention_ratio: float, heavy_frac: float = 0.5, recent_frac: float = 0.5): ...
    def attach(self) -> None:
        """Register H2O eviction hooks on model attention layers. No-op if retention_ratio==1.0."""
    def detach(self) -> None: ...
    def generate(self, input_ids: Tensor, max_new_tokens: int) -> Tensor: ...

def verify_h2o_mechanism(model, sample_input: dict, ratio: float) -> bool:
    """Assert evicted KV size < full_size * (ratio + margin). Raises on failure."""
```

### inference.py

**Dependencies**: h2o_eviction.py, data.py, transformers

```python
def compute_accuracy(generated_text: str, reference: str) -> float:
    """Task-appropriate metric (F1/ROUGE-L per LongBench convention)."""

def run_condition(model, tokenizer, samples: list[dict], retention_ratio: float,
                   eviction_config: EvictionConfig) -> list[float]:
    """Returns per-sample accuracy list for one retention condition."""

def run_all_conditions(model, tokenizer, samples: list[dict],
                        eviction_config: EvictionConfig) -> dict[float, list[float]]:
    """Returns {1.0: [...], 0.8: [...], 0.4: [...]} accuracy per sample per condition."""

def compute_retention(acc_by_condition: dict[float, list[float]]) -> dict[float, np.ndarray]:
    """retention[ratio] = acc_by_condition[ratio] / acc_by_condition[1.0], elementwise."""
```

### stats.py

**Dependencies**: scipy.stats, numpy

```python
def compare_groups(high_retention: np.ndarray, low_retention: np.ndarray) -> dict:
    """Returns {t_stat, p_value, cohens_d, test_used, normal: bool}.
    Uses ttest_ind if both groups pass shapiro normality, else mannwhitneyu."""

def evaluate_gate(p_value: float, high_mean: float, low_mean: float,
                   d: float, threshold: float = 0.05) -> bool:
    """PASS if p<threshold AND high_mean>low_mean AND d>0.5"""
```

### visualize.py

**Dependencies**: matplotlib, seaborn, numpy

```python
def plot_gate_bar(high_retention: np.ndarray, low_retention: np.ndarray,
                   gate_result: dict, output_dir: str) -> str: ...  # mandatory
def plot_boxplot(high_retention, low_retention, output_dir: str) -> str: ...
def plot_scatter_entropy_retention(entropy: np.ndarray, retention: np.ndarray, output_dir: str) -> str: ...
def plot_heatmap_domain_ratio(retention_by_domain_ratio: dict, output_dir: str) -> str: ...
```

### run_experiment.py

**Dependencies**: all above

```python
def run_pipeline(strat_config=None, model_config=None, eviction_config=None) -> dict:
    """Load artifacts -> stratify -> load model -> run 3 conditions -> compute retention
    -> stats -> visualize -> save JSON. Returns {p_value, cohens_d, gate_pass, ...}"""
def main(): ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Reuse H-M1 config/data | Copy config.py, data.py; add StratConfig/EvictionConfig | 5 | 2+1+1+1 |
| A-2 | Vendor H2O repo | Clone FMInference/H2O into external/h2o/, verify import path | 8 | 3+3+1+1 |
| A-3 | Entropy stratification | stratify.py: load H-M1 artifacts, median split, sample group assignment | 7 | 2+3+1+1 |
| A-4 | H2O eviction wrapper | H2OWrapper class: attach/detach hooks, ratio-controlled heavy+recent eviction | 15 | 4+3+5+3 |
| A-5 | Mechanism verification | verify_h2o_mechanism: KV size assertion at 40%/80% | 6 | 1+2+2+1 |
| A-6 | Inference pipeline | run_condition/run_all_conditions across 180 samples x 3 conditions | 13 | 3+3+3+4 |
| A-7 | Accuracy metric | compute_accuracy: task-appropriate F1/ROUGE-L per LongBench domain | 8 | 2+2+3+1 |
| A-8 | Retention + stats | compute_retention, compare_groups (t-test/Mann-Whitney), Cohen's d, gate eval | 9 | 2+2+3+2 |
| A-9 | Visualization suite | Bar chart (mandatory), box plot, scatter, heatmap | 7 | 3+1+2+1 |
| A-10 | Pipeline orchestration | run_experiment.py: wire all stages, save JSON artifacts | 8 | 2+4+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-6, A-7, A-8, A-10], Low(4-8): [A-1, A-2, A-3, A-5, A-9]
