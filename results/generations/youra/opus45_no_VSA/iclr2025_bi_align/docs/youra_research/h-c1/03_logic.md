# Logic: H-C1 Semantic Coherence Analysis

**Type:** CONDITION

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M2)
**Status:** API signatures verified from actual H-M2 code (not spec-only)
**Analyzed Path:** `docs/youra_research/h-m2/code/`
**Relevant Symbols:** `analysis.compute_disagreement_rate`, `analysis.compute_correlations`, `analysis.verify_mechanism`, `bai.train_proxy_detectors`, `bai.compute_bai_scores`, `bai.length_normalize`, `reward.load_reward_model`, `reward.compute_reward_scores`, `data.load_hh_rlhf`, `data.load_reward_bench_safety`, `data.extract_responses`, `data.build_labels`, `config.{RANDOM_STATE, MIN_SAMPLE_COUNT, ...}`

Confirms h-m2 has no `disagreement_samples.json` output — must recompute (Option 2) via direct pipeline rerun, same `RANDOM_STATE=42`.

---

## Applied Patterns

Applied: BERTopic pipeline (sentence-transformers -> UMAP -> HDBSCAN -> c-TF-IDF) — no closer Archon KB match found (searched "BERTopic UMAP HDBSCAN clustering"; only unrelated image-dataset/diffusion hits).
Applied: sklearn silhouette_score on non-noise cluster subset.
Applied: keyword-category threshold classifier (custom, no library).

---

## External Dependencies API (H-M2, verified from actual code)

```python
# From: h-m2/code/data.py
def load_hh_rlhf() -> list[str]: ...
def load_reward_bench_safety() -> list[str]: ...

# From: h-m2/code/bai.py
def train_proxy_detectors() -> dict[str, "AgencyProxyDetector"]: ...
def compute_bai_scores(responses: list[str], detectors: dict) -> list[float]: ...

# From: h-m2/code/reward.py
def load_reward_model() -> tuple: ...  # (model, tokenizer)
def compute_reward_scores(prompts: list[str], responses: list[str], model, tokenizer) -> list[float]: ...

# From: h-m2/code/analysis.py
def compute_disagreement_rate(bai_scores: "np.ndarray", reward_scores: "np.ndarray") -> dict:
    """Returns {disagreement_rate, hh_count, hl_count, lh_count, ll_count, bai_z, reward_z, q_bounds}."""
    ...
```

**Import wiring** (flat modules, no `__init__.py`):
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "h-m2", "code"))
from data import load_hh_rlhf, load_reward_bench_safety
from bai import train_proxy_detectors, compute_bai_scores
from reward import load_reward_model, compute_reward_scores
from analysis import compute_disagreement_rate
```

**Quadrant filter logic** (from `compute_disagreement_rate` internals — `bai_z`/`reward_z`/`q_bounds` keys):
```python
q_bounds = result["q_bounds"]  # {q25_bai, q75_bai, q25_rw, q75_rw}
bai_z, reward_z = result["bai_z"], result["reward_z"]
hl_mask = (bai_z >= q_bounds["q75_bai"]) & (reward_z <= q_bounds["q25_rw"])
lh_mask = (bai_z <= q_bounds["q25_bai"]) & (reward_z >= q_bounds["q75_rw"])
```

---

## config.py

```python
RANDOM_STATE = 42
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
MIN_CLUSTER_SIZE = 50
UMAP_N_NEIGHBORS = 15
UMAP_N_COMPONENTS = 5
UMAP_METRIC = "cosine"
TOP_N_WORDS = 10
AGENCY_MATCH_THRESHOLD = 2
COVERAGE_PASS_THRESHOLD = 0.70
AGENCY_RATE_PASS_THRESHOLD = 0.50
AGENCY_RATE_PARTIAL_THRESHOLD = 0.30
FIGURES_DIR = "h-c1/figures"
```

---

## slice_loader.py

```python
def load_disagreement_slice() -> tuple[list[str], list[str]]:
    """Recompute H-M2 pipeline (RANDOM_STATE=42) -> filter HL+LH quadrants via bai_z/reward_z/q_bounds.
    Returns (hl_texts, lh_texts): high-BAI/low-reward, low-BAI/high-reward response lists."""
    ...
```

Pseudo-code:
```
1. responses = load_hh_rlhf() + load_reward_bench_safety()
2. detectors = train_proxy_detectors()
3. bai_scores = compute_bai_scores(responses, detectors)
4. model, tok = load_reward_model()
5. reward_scores = compute_reward_scores([""]*len(responses), responses, model, tok)
6. result = compute_disagreement_rate(np.array(bai_scores), np.array(reward_scores))
7. hl_mask, lh_mask = quadrant filter (see External Dependencies section)
8. hl_texts = [responses[i] for i in np.where(hl_mask)[0]]
9. lh_texts = [responses[i] for i in np.where(lh_mask)[0]]
10. return hl_texts, lh_texts
```

---

## cluster.py

```python
class AgencyPatternClusterer:
    def __init__(self, min_cluster_size: int = 50): ...
    def fit_transform(self, texts: list[str]) -> tuple[list[int], "np.ndarray"]:
        """texts: N strings -> (topics [N] int cluster ids, probs [N] float)"""
        ...
    def get_topic_info(self) -> "pd.DataFrame": ...  # columns: Topic, Count, Name, ...
    def get_topic_keywords(self, topic_id: int) -> list[tuple[str, float]]: ...  # top_n_words c-TF-IDF pairs
    def get_representative_docs(self, topic_id: int, n: int = 5) -> list[str]: ...
    @property
    def topic_embeddings_(self) -> "np.ndarray | None": ...  # [n_topics, embed_dim]
```

Pseudo-code (`__init__`):
```
embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
umap_model = UMAP(n_neighbors=config.UMAP_N_NEIGHBORS, n_components=config.UMAP_N_COMPONENTS,
                   metric=config.UMAP_METRIC, random_state=config.RANDOM_STATE)
hdbscan_model = HDBSCAN(min_cluster_size=min_cluster_size, metric="euclidean",
                         cluster_selection_method="eom")
topic_model = BERTopic(embedding_model=embedding_model, umap_model=umap_model,
                        hdbscan_model=hdbscan_model, top_n_words=config.TOP_N_WORDS)
```

Tensor shapes:

| Variable | Shape | Note |
|----------|-------|------|
| embeddings | [N, 384] | all-MiniLM-L6-v2 output |
| topics | [N] | int cluster ids, -1 = noise |
| topic_embeddings_ | [n_topics, 384] | centroid per topic |

---

## agency.py

```python
AGENCY_PATTERNS: dict[str, list[str]] = {
    "clarifying": ["clarify", "understand", "mean", "asking", "question", "sure"],
    "deferring": ["prefer", "choice", "decide", "up to you", "your call", "depends"],
    "hedging": ["might", "perhaps", "possibly", "could be", "uncertain", "not sure"],
    "option_enum": ["option", "alternatively", "or", "either", "choices", "ways"],
}

def classify_cluster_as_agency(topic_keywords: str, threshold: int = 2) -> tuple[bool, int]:
    """matches = count of pattern categories with >=1 keyword substring hit in topic_keywords.lower().
    Returns (matches >= threshold, matches)."""
    ...
```

---

## metrics.py

```python
def compute_coverage(topics: list[int]) -> float:
    """(count where topic != -1) / len(topics)"""
    ...

def compute_silhouette(embeddings: "np.ndarray", topics: list[int]) -> float:
    """sklearn.metrics.silhouette_score on embeddings[valid_mask], topics[valid_mask] where valid_mask = topics != -1.
    Returns 0.0 if valid_mask.sum() <= 1."""
    ...

def compute_agency_pattern_rate(topic_model: "AgencyPatternClusterer") -> dict:
    """Iterate get_topic_info() rows (skip Topic==-1); keywords = ' '.join(w for w,_ in get_topic_keywords(topic_id));
    classify_cluster_as_agency(keywords). Returns {agency_pattern_rate, total_clusters, agency_clusters}."""
    ...

def verify_mechanism(topics: list[int], topic_embeddings: "np.ndarray | None") -> dict:
    """Checks: n_topics(=len(set(topics))-{-1})>=3, coverage>0.5,
    mean pairwise np.corrcoef(topic_embeddings) off-diagonal < 0.9 (skip check if topic_embeddings is None).
    Returns {**checks, verification_passed: bool}."""
    ...
```

---

## evaluate.py

```python
def plot_gate_bar(agency_pattern_rate: float, out_path: str) -> None: ...          # bar vs 0.50 threshold, mandatory
def plot_umap_projection(embeddings: "np.ndarray", topics: list[int], out_path: str) -> None: ...
def plot_topic_wordclouds(topic_model: "AgencyPatternClusterer", top_k: int, out_path: str) -> None: ...
def plot_cluster_size_histogram(topics: list[int], out_path: str) -> None: ...
def save_representative_docs_table(topic_model: "AgencyPatternClusterer", agency_topic_ids: list[int], out_path: str) -> None: ...
```

---

## run.py

```python
def main() -> str:
    """Pipeline: load_disagreement_slice() -> hl_texts+lh_texts -> texts = hl_texts+lh_texts ->
    AgencyPatternClusterer(config.MIN_CLUSTER_SIZE).fit_transform(texts) -> topics, probs ->
    compute_coverage(topics), compute_silhouette(embeddings, topics), compute_agency_pattern_rate(topic_model) ->
    verify_mechanism(topics, topic_model.topic_embeddings_) ->
    evaluate.plot_* (save to config.FIGURES_DIR) -> save results.json ->
    gate: 'PASS' if agency_rate>=0.50 and coverage>=0.70 else 'PARTIAL' if agency_rate>=0.30 else 'FAIL'.
    Returns gate_result string."""
    ...
```

---

## Subtasks

None (all Low complexity, budget 0).
