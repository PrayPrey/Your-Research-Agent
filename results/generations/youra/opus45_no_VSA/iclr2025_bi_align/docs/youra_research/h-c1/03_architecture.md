# Architecture: H-C1 Semantic Coherence Analysis

**Type:** CONDITION
**Applied:** BERTopic pipeline pattern (sentence-transformers → UMAP → HDBSCAN → c-TF-IDF), per experiment brief; no closer KB match found (searched "BERTopic clustering semantic coherence NLP" — only unrelated image-dataset hits).

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M2)
**Status:** H-M2 code analyzed. Critical finding: **`h-m2/disagreement_samples.json` does NOT exist** — H-M2's `run.py::main()` only writes `outputs/results.json` with aggregate stats + `top_disagreement_examples` (n=10 only). Full per-sample `bai_z`/`reward_z` arrays are deleted before dump (`del results["bai_z"]`, `del results["reward_z"]`).
**Analyzed Path:** `docs/youra_research/h-m2/code/`
**Findings:**
- `analysis.py::compute_disagreement_rate(bai, reward)` returns dict incl. `bai_z`, `reward_z`, `q_bounds`, quadrant counts — this is the source of truth for quadrant membership, but is not persisted.
- `run.py::main()` loads `hh_texts = load_hh_rlhf()` + `rb_texts = load_reward_bench_safety()`, concats to `responses`, trains 4 proxy detectors (`bai.py::train_proxy_detectors`), computes `bai_scores` and `reward_scores` in the same fixed order as `responses`.
- **Conclusion**: PRD's "Option 1: load JSON" is unavailable. H-C1 must use **Option 2 (recompute)** by importing and re-running H-M2's `bai.py`, `reward.py`, `analysis.py` modules directly (same RANDOM_STATE=42 → deterministic same slice), then filter `responses` by quadrant using `bai_z`/`reward_z`/`q_bounds`.

---

## File Structure

```
h-c1/code/
  config.py       # fixed config constants
  slice_loader.py # recompute H-M2 pipeline, extract HL+LH quadrant texts
  cluster.py      # AgencyPatternClusterer (BERTopic wrapper)
  agency.py       # AGENCY_PATTERNS keyword classifier
  metrics.py       # coverage, silhouette, agency_pattern_rate, mechanism verification
  evaluate.py      # figure generation
  run.py           # entrypoint: orchestrate pipeline end-to-end
figures/           # output plots
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_hh_rlhf, load_reward_bench_safety | `from h_m2.data import load_hh_rlhf, load_reward_bench_safety` (flat import via sys.path insert) | `h-m2/code/data.py` |
| train_proxy_detectors, compute_bai_scores | `from bai import train_proxy_detectors, compute_bai_scores` | `h-m2/code/bai.py` |
| load_reward_model, compute_reward_scores | `from reward import load_reward_model, compute_reward_scores` | `h-m2/code/reward.py` |
| compute_disagreement_rate | `from analysis import compute_disagreement_rate` | `h-m2/code/analysis.py` |

**Verified from**: `h-m2/code/` (actual implementation — flat module names, no package `__init__.py`).

**Actual import pattern:**
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "h-m2", "code"))
from data import load_hh_rlhf, load_reward_bench_safety
from bai import train_proxy_detectors, compute_bai_scores
from reward import load_reward_model, compute_reward_scores
from analysis import compute_disagreement_rate
```

---

## Modules

### config.py (`h-c1/code/config.py`)

**Dependencies**: None

```python
RANDOM_STATE = 42
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
MIN_CLUSTER_SIZE = 50
UMAP_N_NEIGHBORS = 15
UMAP_N_COMPONENTS = 5
UMAP_METRIC = "cosine"
TOP_N_WORDS = 10
AGENCY_MATCH_THRESHOLD = 2  # min pattern categories matched
COVERAGE_PASS_THRESHOLD = 0.70
AGENCY_RATE_PASS_THRESHOLD = 0.50
AGENCY_RATE_PARTIAL_THRESHOLD = 0.30
FIGURES_DIR = "h-c1/figures"
```

### slice_loader.py (`h-c1/code/slice_loader.py`)

**Dependencies**: config.py, h-m2/code/{data,bai,reward,analysis}.py

```python
def load_disagreement_slice() -> tuple[list[str], list[str]]: ...
    # Try h-m2/outputs/disagreement_samples.json (Option 1, likely absent)
    # Fallback: rerun H-M2 pipeline (same RANDOM_STATE) -> bai_scores, reward_scores
    # -> compute_disagreement_rate() -> filter responses by bai_z/reward_z/q_bounds
    # returns (hl_texts, lh_texts)  # high-BAI/low-reward, low-BAI/high-reward
```

### cluster.py (`h-c1/code/cluster.py`)

**Dependencies**: config.py

```python
class AgencyPatternClusterer:
    def __init__(self, min_cluster_size: int = 50): ...
    def fit_transform(self, texts: list[str]) -> tuple[list[int], "np.ndarray"]: ...
    def get_topic_info(self) -> "pd.DataFrame": ...
    def get_topic_keywords(self, topic_id: int) -> list[tuple[str, float]]: ...
    def get_representative_docs(self, topic_id: int, n: int = 5) -> list[str]: ...
    @property
    def topic_embeddings_(self) -> "np.ndarray | None": ...
```

### agency.py (`h-c1/code/agency.py`)

**Dependencies**: config.py

```python
AGENCY_PATTERNS: dict[str, list[str]] = {
    "clarifying": ["clarify", "understand", "mean", "asking", "question", "sure"],
    "deferring": ["prefer", "choice", "decide", "up to you", "your call", "depends"],
    "hedging": ["might", "perhaps", "possibly", "could be", "uncertain", "not sure"],
    "option_enum": ["option", "alternatively", "or", "either", "choices", "ways"],
}

def classify_cluster_as_agency(topic_keywords: str, threshold: int = 2) -> tuple[bool, int]: ...
```

### metrics.py (`h-c1/code/metrics.py`)

**Dependencies**: agency.py, config.py

```python
def compute_coverage(topics: list[int]) -> float: ...
def compute_silhouette(embeddings: "np.ndarray", topics: list[int]) -> float: ...
def compute_agency_pattern_rate(topic_model: "AgencyPatternClusterer") -> dict: ...
    # iterates topic_info, classify_cluster_as_agency per cluster
    # returns {agency_pattern_rate, total_clusters, agency_clusters}
def verify_mechanism(topics: list[int], topic_embeddings: "np.ndarray | None") -> dict: ...
    # n_topics>=3, coverage>0.5, mean pairwise topic-embedding corr < 0.9
```

### evaluate.py (`h-c1/code/evaluate.py`)

**Dependencies**: metrics.py, config.py

```python
def plot_gate_bar(agency_pattern_rate: float, out_path: str) -> None: ...          # mandatory gate figure
def plot_umap_projection(embeddings: "np.ndarray", topics: list[int], out_path: str) -> None: ...
def plot_topic_wordclouds(topic_model, top_k: int, out_path: str) -> None: ...
def plot_cluster_size_histogram(topics: list[int], out_path: str) -> None: ...
def save_representative_docs_table(topic_model, agency_topic_ids: list[int], out_path: str) -> None: ...
```

### run.py (`h-c1/code/run.py`)

**Dependencies**: slice_loader.py, cluster.py, agency.py, metrics.py, evaluate.py, config.py

```python
def main() -> str: ...
# load_disagreement_slice -> combine hl+lh texts -> AgencyPatternClusterer.fit_transform ->
# compute_coverage/compute_silhouette/compute_agency_pattern_rate -> verify_mechanism ->
# generate figures -> save results.json -> return gate_result (PASS/PARTIAL/FAIL)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | H-M2 bridging + slice recompute | sys.path wiring, rerun H-M2 bai/reward/analysis pipeline, filter HL+LH quadrants | 8 | 2+3+2+1 |
| C-2 | Slice loader fallback logic | Try JSON load, else recompute; cache result to avoid rerun | 5 | 1+2+1+1 |
| C-3 | Embedding generation | sentence-transformers all-MiniLM-L6-v2 encode texts | 4 | 1+1+1+1 |
| C-4 | BERTopic pipeline setup | UMAP+HDBSCAN configured, AgencyPatternClusterer wrapper, fit_transform | 8 | 2+2+3+1 |
| C-5 | Agency pattern classifier | Keyword matching against 4 pattern categories, threshold logic | 4 | 1+1+2+0 |
| C-6 | Coverage/silhouette/agency-rate metrics | Compute all 3 primary metrics from topic model output | 6 | 1+2+2+1 |
| C-7 | Mechanism verification | n_topics>=3, coverage>50%, topic embedding distinctness check | 5 | 1+1+2+1 |
| C-8 | Visualization suite | Gate bar, UMAP projection, wordclouds, size histogram, rep-docs table | 7 | 2+1+1+3 |
| C-9 | Integration + gate check | run.py orchestration, results.json, PASS/PARTIAL/FAIL reporting | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9]
