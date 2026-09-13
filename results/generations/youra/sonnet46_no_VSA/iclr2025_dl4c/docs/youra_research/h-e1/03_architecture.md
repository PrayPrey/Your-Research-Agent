# Architecture: H-E1
# Code Embedding Distribution Distinctiveness Analysis

**Applied**: Standard HuggingFace embedding pipeline pattern
**Hypothesis Type**: EXISTENCE (PoC)
**Task Budget**: LIGHT (4–8 epics)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase — green-field implementation
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no patterns to reuse

---

## File Organization

- `src/h_e1/data_loader.py` — dataset loading + text extraction + Equal-mix construction
- `src/h_e1/embedder.py` — CodeBERT + MiniLM encoding
- `src/h_e1/similarity.py` — pairwise cosine similarity matrix + gate evaluation
- `src/h_e1/visualize.py` — heatmaps + optional histograms/t-SNE
- `src/h_e1/run_experiment.py` — main entry point
- `docs/youra_research/h-e1/figures/` — output figures (created at runtime)

---

## Modules

### DataLoader (`src/h_e1/data_loader.py`)

**Dependencies**: `datasets` (HuggingFace)

```python
SOURCES = {
    "humaneval_train": ("openai/openai_humaneval", None, "test"),
    "mbpp_train": ("google-research-datasets/mbpp", "sanitized", "train"),
    "leetcode": ("newfacade/LeetCodeDataset", None, "train"),
    "humaneval_plus": ("evalplus/humanevalplus", None, "test"),
    "mbpp_plus": ("evalplus/mbppplus", None, "test"),
}

def load_all_corpora(seed: int = 42) -> dict[str, list[str]]:
    """Returns dict mapping corpus name → list of raw text strings.
    Equal-mix is constructed here: 164 from each of humaneval_train,
    mbpp_train (seed), leetcode (seed) → concatenated."""
    ...

def extract_text(example: dict, source_name: str) -> str:
    """Returns concatenated prompt+solution string for one example."""
    ...
```

---

### Embedder (`src/h_e1/embedder.py`)

**Dependencies**: `transformers`, `sentence_transformers`, `torch`

```python
def encode_codebert(
    texts: list[str],
    batch_size: int = 32,
    device: str = "cuda",
    max_length: int = 512,
) -> torch.Tensor:
    """Returns L2-normalized (N, 768) float32 tensor. Mean-pools last hidden
    states weighted by attention mask."""
    ...

def encode_minilm(
    texts: list[str],
    batch_size: int = 32,
) -> torch.Tensor:
    """Returns L2-normalized (N, 384) float32 tensor via
    SentenceTransformer.encode(normalize_embeddings=True)."""
    ...

def encode_all_corpora(
    corpora: dict[str, list[str]],
    batch_size: int = 32,
    device: str = "cuda",
) -> dict[str, dict[str, torch.Tensor]]:
    """Returns {corpus_name: {"codebert": Tensor, "minilm": Tensor}}."""
    ...
```

---

### Similarity (`src/h_e1/similarity.py`)

**Dependencies**: `torch`, `numpy`

```python
SOURCES = ["humaneval_train", "mbpp_train", "leetcode", "equal_mix"]
BENCHMARKS = ["humaneval_plus", "mbpp_plus"]

def mean_pairwise_cosine(
    source_embs: torch.Tensor,
    target_embs: torch.Tensor,
) -> float:
    """dot(source, target.T).mean() — valid because both are L2-normalized."""
    ...

def compute_similarity_matrix(
    embeddings: dict[str, dict[str, torch.Tensor]],
) -> dict[str, np.ndarray]:
    """Returns {"codebert": ndarray(4,2), "minilm": ndarray(4,2)}."""
    ...

def evaluate_gate(sim_matrices: dict[str, np.ndarray]) -> dict:
    """Returns {gate_satisfied: bool, min_sim: float, max_sim: float,
    mean_sim: float, std_sim: float, all_values: list[float]}."""
    ...

def verify_embeddings(
    embeddings: dict[str, dict[str, torch.Tensor]],
    sim_matrices: dict[str, np.ndarray],
) -> tuple[bool, dict]:
    """Shape checks + gate check. Returns (all_pass, checks_dict)."""
    ...
```

---

### Visualize (`src/h_e1/visualize.py`)

**Dependencies**: `matplotlib`, `seaborn`, `numpy`, `sklearn` (optional for t-SNE)

```python
def plot_heatmaps(
    sim_matrices: dict[str, np.ndarray],
    output_dir: str,
    threshold: float = 0.95,
) -> None:
    """Saves dual-encoder side-by-side 4×2 heatmaps with threshold annotated."""
    ...

def plot_histograms(
    embeddings: dict[str, dict[str, torch.Tensor]],
    output_dir: str,
) -> None:
    """Optional: per-source pairwise similarity distributions."""
    ...

def plot_tsne(
    embeddings: dict[str, dict[str, torch.Tensor]],
    output_dir: str,
    encoder: str = "codebert",
) -> None:
    """Optional: 2D t-SNE projection colored by corpus source."""
    ...
```

---

### Experiment Runner (`src/h_e1/run_experiment.py`)

**Dependencies**: all above modules

```python
def main(
    batch_size: int = 32,
    device: str = "cuda",
    seed: int = 42,
    figures_dir: str = "docs/youra_research/h-e1/figures",
    skip_tsne: bool = False,
) -> None:
    """Full pipeline: load → embed → similarity → gate → visualize → log."""
    ...
```

---

## Epic Tasks

### Epic E1: Data Loading and Text Extraction
- **Complexity:** 8/20 (Module_Size: 2 + Dependencies: 2 + Algorithm: 2 + Integration: 2)
- **Target files:** `src/h_e1/data_loader.py`
- **Description:** Load 5 HuggingFace datasets; extract raw text per corpus schema (prompt+solution / text+code / description+solution); construct Equal-mix (164 samples each from HumanEval-train, MBPP-train, LeetCode, seed=42); return dict of corpus → text list.

---

### Epic E2: Dual-Encoder Embedding Module
- **Complexity:** 11/20 (Module_Size: 3 + Dependencies: 3 + Algorithm: 3 + Integration: 2)
- **Target files:** `src/h_e1/embedder.py`
- **Description:** Implement CodeBERT batched mean-pooling encoder (attention-mask weighted, L2-normalized, 768-dim) and all-MiniLM-L6-v2 encoder (sentence-transformers API, normalize_embeddings=True, 384-dim). Handle OOM fallback (batch_size 32→8). Log "Encoded N problems for [source] with [encoder]" per corpus.

---

### Epic E3: Similarity Matrix and Gate Evaluation
- **Complexity:** 9/20 (Module_Size: 2 + Dependencies: 2 + Algorithm: 3 + Integration: 2)
- **Target files:** `src/h_e1/similarity.py`
- **Description:** Compute 4×2 mean pairwise cosine similarity matrices for both encoders (dot product of L2-normalized tensors). Evaluate gate (any value < 0.95 → SATISFIED). Verify embedding shapes and matrix std > 0.01. Return structured results dict.

---

### Epic E4: Visualization and Experiment Runner
- **Complexity:** 10/20 (Module_Size: 2 + Dependencies: 3 + Algorithm: 2 + Integration: 3)
- **Target files:** `src/h_e1/visualize.py`, `src/h_e1/run_experiment.py`
- **Description:** Generate required dual-encoder heatmaps (4×2, threshold=0.95 annotated, saved to figures/). Optional histogram and t-SNE plots. Wire full pipeline in run_experiment.py: load → embed → similarity → gate eval → visualize → print gate result and 16-value summary.

---

## Epic Task Distribution

| ID | Task | Complexity |
|----|------|------------|
| E1 | Data Loading and Text Extraction | 8 |
| E2 | Dual-Encoder Embedding Module | 11 |
| E3 | Similarity Matrix and Gate Evaluation | 9 |
| E4 | Visualization and Experiment Runner | 10 |

**Distribution**: High(14-17): [], Medium(9-13): [E2, E3, E4], Low(4-8): [E1]

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `transformers` | >=4.43.0 | CodeBERT loading + tokenization |
| `sentence-transformers` | >=2.2.0 | all-MiniLM-L6-v2 encoding |
| `datasets` | >=2.14.0 | HuggingFace dataset loading |
| `torch` | >=2.0.0 | Tensor ops, CUDA |
| `numpy` | >=1.24.0 | Matrix construction |
| `matplotlib` | >=3.7.0 | Heatmap figures |
| `seaborn` | >=0.12.0 | Heatmap styling |
| `scikit-learn` | >=1.3.0 | t-SNE (optional) |
| `tqdm` | >=4.65.0 | Encoding progress bars |

No training, no optimizer, no loss — pretrained checkpoints only.
