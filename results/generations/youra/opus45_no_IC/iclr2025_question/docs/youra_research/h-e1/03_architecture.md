# Architecture: H-E1 (EXISTENCE / PoC)

**Hypothesis**: Benchmarks cluster meaningfully (silhouette > 0.5) based on uncertainty distribution similarity
**Gate**: MUST_WORK, silhouette > 0.5, fail action: ABANDON

Applied: sklearn silhouette_score precomputed-distance-matrix pattern (scipy Ward linkage + sklearn silhouette evaluation)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: No `code/` directory exists yet for h-e1; implementing from scratch per PRD/brief.

---

## File Structure (EXISTENCE minimal)

```
h-e1/code/
  data.py          # benchmark loading (6 HF datasets, 1000 samples each)
  generate.py       # Llama-2-7B generation, 10 responses/query, disk cache
  entropy.py         # DeBERTa NLI bidirectional-entailment clustering -> semantic entropy
  cluster.py          # KDE, JS-divergence matrix, hierarchical clustering, silhouette
  visualize.py          # heatmap, dendrogram, violin, silhouette plot, gate bar chart
  config.py               # single fixed config (paths, seed=42, model ids)
  run.py                    # orchestrates full pipeline end-to-end
h-e1/figures/                # output figures
h-e1/cache/                    # generation cache (~10GB)
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
SEED = 42
BENCHMARKS = ["trivia_qa", "natural_questions", "squad", "pop_qa", "halueval_qa", "fever"]
N_SAMPLES = 1000
GEN_MODEL = "meta-llama/Llama-2-7b-hf"
NLI_MODEL = "microsoft/deberta-v3-large"  # via HF NLI-finetuned checkpoint
N_GENERATIONS = 10
TEMPERATURE = 0.7
CACHE_DIR = "h-e1/cache"
FIGURES_DIR = "h-e1/figures"
SILHOUETTE_THRESHOLD = 0.5
```

### DataLoader (`data.py`)

**Dependencies**: config

```python
def load_benchmark(name: str, n_samples: int = 1000, seed: int = 42) -> list[dict]:
    """Returns list of {"id": str, "question": str, "benchmark": str}."""
def load_all_benchmarks() -> dict[str, list[dict]]: ...
```

### Generator (`generate.py`)

**Dependencies**: config, data

```python
class ResponseGenerator:
    def __init__(self, model_name: str, cache_dir: str): ...
    def generate(self, question: str, n: int = 10, temperature: float = 0.7) -> list[str]: ...
    def generate_for_benchmark(self, queries: list[dict]) -> dict[str, list[str]]:
        """query_id -> list of n generated responses. Cached to disk (skip if cached)."""
```

### EntropyComputer (`entropy.py`)

**Dependencies**: config

```python
class SemanticEntropyComputer:
    def __init__(self, nli_model_name: str): ...
    def cluster_by_entailment(self, responses: list[str]) -> list[int]:
        """Bidirectional entailment clustering -> cluster id per response."""
    def compute_entropy(self, responses: list[str]) -> float:
        """Semantic entropy over entailment clusters (Kuhn et al. formula)."""
    def compute_for_benchmark(self, query_responses: dict[str, list[str]]) -> np.ndarray:
        """Returns (n_samples,) entropy array for one benchmark."""
```

### ClusteringAnalyzer (`cluster.py`)

**Dependencies**: config

```python
class BenchmarkClusteringAnalyzer:
    def __init__(self, kde_bandwidth: str = "scott"): ...
    def fit_kde(self, entropies: np.ndarray) -> "gaussian_kde": ...
    def js_divergence_matrix(self, kdes: dict[str, "gaussian_kde"]) -> np.ndarray:
        """(6,6) symmetric, zero-diagonal JS-divergence matrix."""
    def cluster(self, js_matrix: np.ndarray) -> tuple[np.ndarray, float, int]:
        """Ward linkage; tests k=2..4; returns (labels, best_silhouette, best_k)."""
    def verify_mechanism(self, js_matrix, labels, silhouette) -> bool:
        """Shape/symmetry/diagonal/range checks per PRD verification protocol."""
```

### Visualizer (`visualize.py`)

**Dependencies**: config

```python
def plot_js_heatmap(js_matrix: np.ndarray, names: list[str], out_path: str) -> None: ...
def plot_dendrogram(js_matrix: np.ndarray, names: list[str], out_path: str) -> None: ...
def plot_entropy_violin(entropies: dict[str, np.ndarray], out_path: str) -> None: ...
def plot_silhouette(js_matrix: np.ndarray, labels: np.ndarray, out_path: str) -> None: ...
def plot_gate_metric(silhouette: float, threshold: float, out_path: str) -> None: ...
```

### Orchestrator (`run.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """data -> generate -> entropy -> cluster -> visualize -> log gate decision."""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + Data loading | Fixed config, load 6 HF benchmarks x1000 samples, seed=42 | 6 | 1+1+2+2 |
| A-2 | Response generation | Llama-2-7B, 10 responses/query x6000 queries, disk cache | 12 | 3+3+3+3 |
| A-3 | Semantic entropy computation | DeBERTa NLI bidirectional entailment clustering + entropy formula | 14 | 3+3+4+4 |
| A-4 | KDE + JS-divergence matrix | Fit KDE per benchmark, build 6x6 symmetric JS matrix, validate | 8 | 2+2+2+2 |
| A-5 | Hierarchical clustering + silhouette | Ward linkage, k=2..4 sweep, best silhouette, mechanism verification | 9 | 2+2+3+2 |
| A-6 | Visualization suite | 5 figures: heatmap, dendrogram, violin, silhouette plot, gate bar chart | 7 | 2+1+2+2 |
| A-7 | Pipeline orchestration + gate logging | run.py end-to-end wiring, gate decision log to 04_validation.md | 6 | 1+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-2, A-5], Low(4-8): [A-1, A-4, A-6, A-7]

---

## Data Flow

Benchmarks (6x1000) -> Generator (10 resp/query, cached) -> EntropyComputer (NLI clustering) -> 6x1000 entropy values -> ClusteringAnalyzer (KDE -> JS matrix -> Ward -> silhouette) -> gate decision (>0.5) -> Visualizer (figures/)
