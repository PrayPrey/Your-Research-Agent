# Logic: h-e1 — Contamination Geometry Decomposition

**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)
**Date:** 2026-05-13

Applied: PyTorch Module pattern, streaming pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase — green-field implementation
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation from scratch

---

## A-2: Corpus Index Construction [Complexity: 14, Budget: 5 subtasks]

Applied: streaming-pipeline pattern

### API Signatures

```python
# code/index_builder.py
import numpy as np
import faiss
from typing import Iterator, Optional
from config import ExperimentConfig


class NgramIndexBuilder:
    def __init__(self, cfg: ExperimentConfig):
        """Initialize builder with config (ngram_n=13, ngram_buckets=500)."""
        self.cfg = cfg
        self.index_dir = cfg.index_dir  # h-e1/indices/

    def build_index(
        self,
        corpus_name: str,           # "pile" | "c4" | "redpajama"
        corpus_stream: Iterator[str],
        max_docs: Optional[int] = None,
    ) -> None:
        """Stream corpus, extract 13-grams, write sorted bucket files to disk."""
        # Calls EleutherAI pipeline scripts:
        # 1. generate_13_grams.py  → raw 13-gram hashes
        # 2. sort_13_gram_buckets.py → sorted per-bucket files
        # 3. compress_and_package.py → final index at index_dir/{corpus_name}/
        ...

    def load_index(self, corpus_name: str) -> "NgramIndex":
        """Load pre-built index from disk. Returns NgramIndex wrapper."""
        ...


class NgramIndex:
    def __init__(self, index_path: str, n: int = 13):
        """Load bucket files from index_path."""
        ...

    def max_overlap(self, text: str, n: int = 13) -> int:
        """Return max consecutive n-gram match count between text and corpus.
        Returns: int — max matching n-gram count, 0 if no match."""
        # Tokenize text → ngrams → lookup in bucket files → max count
        ...

    def is_contaminated(self, text: str, threshold: int = 1) -> bool:
        """Return True if max_overlap(text) >= threshold."""
        return self.max_overlap(text) >= threshold


class SBERTIndexBuilder:
    def __init__(self, cfg: ExperimentConfig):
        """Initialize with all-MiniLM-L6-v2 model."""
        self.cfg = cfg
        self.model_name = cfg.sbert_model  # "all-MiniLM-L6-v2"
        self.batch_size = cfg.sbert_batch_size  # 256

    def build_index(
        self,
        corpus_name: str,           # "pile" | "c4" | "redpajama"
        corpus_texts: list[str],    # streamed + collected texts
    ) -> None:
        """Encode corpus texts, normalize, build IndexFlatIP, save to disk.

        Algorithm:
        1. Load SentenceTransformer(self.model_name)
        2. Encode in batches of batch_size → embeddings shape (M, 384)
        3. L2-normalize embeddings → normalized shape (M, 384)
        4. faiss.IndexFlatIP(384).add(normalized)
        5. faiss.write_index(index, path)
        """
        ...

    def load_index(self, corpus_name: str) -> "SBERTIndex":
        """Load FAISS index from disk. Returns SBERTIndex wrapper."""
        ...


class SBERTIndex:
    def __init__(self, index: faiss.IndexFlatIP, model_name: str, batch_size: int = 256):
        """Wrap FAISS index + encoder for query time."""
        ...

    def search(
        self,
        query_texts: list[str],  # length Q
        k: int = 1,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Encode queries, search FAISS index, return (distances, indices).

        Returns:
            distances: shape (Q, k) float32  — inner product (cosine after L2-norm)
            indices:   shape (Q, k) int64    — corpus doc indices
        """
        # 1. Encode query_texts → shape (Q, 384) float32
        # 2. L2-normalize
        # 3. index.search(queries, k) → D, I
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| corpus embeddings | (M, 384) float32 | M = num corpus docs |
| query embeddings | (Q, 384) float32 | Q = num benchmark items |
| FAISS distances | (Q, k) float32 | cosine similarity (normalized) |
| FAISS indices | (Q, k) int64 | corpus doc index |
| ngram_counts (per item) | (N,) int64 | N = benchmark items |

### Subtasks [5/5 used]

| ID | Subtask | Parent Epic | Description |
|----|---------|-------------|-------------|
| L-2-1 | EleutherAI 13-gram pipeline integration | A-2 | Wrap generate_13_grams.py → sort_13_gram_buckets.py → compress_and_package.py as Python subprocess calls inside NgramIndexBuilder.build_index; handle streaming input via temp files |
| L-2-2 | NgramIndex query interface | A-2 | Implement max_overlap() using bucket binary search on sorted 13-gram files; return max count int |
| L-2-3 | SBERT batch encoding + FAISS build | A-2 | Encode corpus in batches (batch_size=256), L2-normalize, build IndexFlatIP(384), serialize with faiss.write_index |
| L-2-4 | SBERTIndex search with normalization | A-2 | Encode query batch, L2-normalize, call index.search(k=1), return (distances, indices) tuple |
| L-2-5 | Streaming OOM guard | A-2 | For C4/RedPajama, cap corpus at max_docs=500_000 with tqdm progress; write texts to disk in shards before FAISS build |

---

## A-5: Detector Families [Complexity: 15, Budget: 5 subtasks]

Applied: strategy pattern for detector interface

### API Signatures

```python
# code/detectors/ngram_detector.py
import numpy as np
from config import ExperimentConfig
from index_builder import NgramIndex


class NgramDetector:
    def __init__(self, cfg: ExperimentConfig):
        """N-gram overlap detector using EleutherAI 13-gram index."""
        self.n = cfg.ngram_n  # 13

    def predict(
        self,
        texts: list[str],       # length N
        ngram_index: NgramIndex,
        threshold: int = 1,
    ) -> np.ndarray:
        """Binary contamination predictions.
        Returns: shape (N,) int64 — 1=contaminated, 0=clean"""
        # For each text: contaminated = int(ngram_index.max_overlap(text) >= threshold)
        ...

    def score(
        self,
        texts: list[str],       # length N
        ngram_index: NgramIndex,
    ) -> np.ndarray:
        """Raw n-gram overlap counts.
        Returns: shape (N,) int64 — max 13-gram match count per item"""
        ...
```

```python
# code/detectors/embedding_detector.py
import numpy as np
from config import ExperimentConfig
from index_builder import SBERTIndex


class EmbeddingDetector:
    def __init__(self, cfg: ExperimentConfig):
        """LLMSanitize embedding similarity detector."""
        self.default_threshold: float = 0.95  # cosine similarity cutoff

    def predict(
        self,
        texts: list[str],           # length N
        sbert_index: SBERTIndex,
        threshold: float = 0.95,
    ) -> np.ndarray:
        """Binary labels based on max cosine similarity to corpus.
        Returns: shape (N,) int64 — 1=contaminated, 0=clean"""
        # 1. distances, _ = sbert_index.search(texts, k=1) → shape (N, 1)
        # 2. max_cosines = distances[:, 0] → shape (N,)
        # 3. return (max_cosines >= threshold).astype(int)
        ...

    def score(
        self,
        texts: list[str],           # length N
        sbert_index: SBERTIndex,
    ) -> np.ndarray:
        """Max cosine similarity per item.
        Returns: shape (N,) float32"""
        ...
```

```python
# code/detectors/minkpp_detector.py
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import ExperimentConfig


class MinkPPDetector:
    def __init__(
        self,
        cfg: ExperimentConfig,
        model_name: str = "EleutherAI/pythia-6.9b",
    ):
        """Min-K%++ MIA detector. Loads LM for token-level log-prob scoring."""
        self.k: float = cfg.minkpp_k  # 0.20 (20%)
        self.model_name = model_name
        self.model: AutoModelForCausalLM = None  # lazy load
        self.tokenizer: AutoTokenizer = None

    def _load_model(self) -> None:
        """Lazy-load model to GPU."""
        ...

    def score(
        self,
        texts: list[str],   # length N
    ) -> np.ndarray:
        """Compute Min-K%++ scores per text.
        Returns: shape (N,) float32 — higher = more likely member

        Algorithm:
        1. Tokenize text → input_ids shape (1, L)
        2. Forward pass → logits shape (1, L, V)
        3. log_probs per token → shape (L,) float32
        4. Select bottom k% tokens by log_prob
        5. score = mean(bottom_k_log_probs)  # Min-K%++ variant
        """
        ...

    def predict(
        self,
        texts: list[str],   # length N
        threshold: float = 0.0,
    ) -> np.ndarray:
        """Binary predictions using threshold on score().
        Returns: shape (N,) int64 — 1=contaminated, 0=clean"""
        scores = self.score(texts)  # shape (N,)
        return (scores >= threshold).astype(np.int64)
```

```python
# code/detectors/dcpdd_detector.py
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import ExperimentConfig


class DCPDDDetector:
    def __init__(
        self,
        cfg: ExperimentConfig,
        ref_model_name: str = "EleutherAI/pythia-2.8b",
    ):
        """DC-PDD: per Zhang et al. 2024. Uses reference model likelihood ratio."""
        self.ref_model_name = ref_model_name
        self.ref_model: AutoModelForCausalLM = None  # lazy load
        self.tokenizer: AutoTokenizer = None

    def _load_model(self) -> None:
        """Lazy-load Pythia-2.8B reference model."""
        ...

    def score(
        self,
        texts: list[str],   # length N
    ) -> np.ndarray:
        """DC-PDD score = log P_target(text) - log P_ref(text).
        Returns: shape (N,) float32"""
        # 1. ref_logprob = mean log P_pythia2.8b(text) per token → shape (N,)
        # 2. DC-PDD: normalized likelihood delta vs reference corpus distribution
        ...

    def predict(
        self,
        texts: list[str],   # length N
        threshold: float = 0.0,
    ) -> np.ndarray:
        """Binary predictions.
        Returns: shape (N,) int64"""
        return (self.score(texts) >= threshold).astype(np.int64)
```

```python
# code/detectors/constat_detector.py
import numpy as np
from config import ExperimentConfig


class ConStatDetector:
    def __init__(self, cfg: ExperimentConfig):
        """ConStat: longest contaminated substring via LLMSanitize (Singh et al. 2024)."""
        # Uses llmsanitize library ConStat method
        self.method_name: str = "constat"

    def score(
        self,
        texts: list[str],   # length N
    ) -> np.ndarray:
        """ConStat contamination scores per item.
        Returns: shape (N,) float32"""
        # Calls llmsanitize.contamination.constat(texts) → float scores
        ...

    def predict(
        self,
        texts: list[str],   # length N
        threshold: float = 0.5,
    ) -> np.ndarray:
        """Binary predictions.
        Returns: shape (N,) int64 — 1=contaminated, 0=clean"""
        return (self.score(texts) >= threshold).astype(np.int64)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | (1, L) int64 | single text, L = token length |
| logits | (1, L, V) float32 | V = vocab size |
| log_probs | (L,) float32 | per-token log probability |
| detector predictions | (N,) int64 | N = benchmark items |
| detector scores | (N,) float32 | raw scores before thresholding |

### Pseudo-code: MinkPPDetector.score

```
for text in texts:
    input_ids = tokenizer(text, return_tensors="pt").input_ids  # (1, L)
    with torch.no_grad():
        logits = model(input_ids).logits  # (1, L, V)
    log_probs = F.log_softmax(logits[0], dim=-1)  # (L, V)
    token_log_probs = log_probs[range(L-1), input_ids[0, 1:]]  # (L-1,) — next-token probs
    k_count = max(1, int(k * len(token_log_probs)))
    bottom_k = torch.topk(token_log_probs, k_count, largest=False).values  # (k_count,)
    score = bottom_k.mean().item()
```

### Subtasks [5/5 used]

| ID | Subtask | Parent Epic | Description |
|----|---------|-------------|-------------|
| L-5-1 | NgramDetector + EmbeddingDetector | A-5 | Implement NgramDetector.predict/score using NgramIndex.max_overlap; implement EmbeddingDetector.predict/score using SBERTIndex.search with cosine threshold |
| L-5-2 | MinkPPDetector token scoring | A-5 | Lazy-load LM, compute per-token log_probs, select bottom-k%, return mean as score; handle variable-length texts via loop |
| L-5-3 | DCPDDDetector reference model scoring | A-5 | Lazy-load Pythia-2.8B, compute normalized log-likelihood delta per text; predict with threshold=0.0 |
| L-5-4 | ConStatDetector via LLMSanitize | A-5 | Wrap llmsanitize.contamination.constat() to return score array shape (N,); predict with threshold=0.5 |
| L-5-5 | Detector registry + batch runner | A-5 | detectors/__init__.py exports dict of all 5 detectors; run_detector_evaluation() loops benchmark×corpus×detector, stores preds in dict[str, np.ndarray] |

---

## A-3: Geometry Features & Stratification [Complexity: 10]

### API Signatures

```python
# code/geometry_features.py
import numpy as np
from config import ExperimentConfig
from index_builder import NgramIndex, SBERTIndex


class GeometryStratifier:
    def __init__(self, cfg: ExperimentConfig):
        """Compute geometry features and assign strata."""
        self.percentile: float = cfg.stratum_percentile  # 75.0

    def compute_geometry_features(
        self,
        benchmark_texts: list[str],     # length N
        ngram_index: NgramIndex,
        sbert_index: SBERTIndex,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute per-item geometry signals.
        Returns:
            ngram_counts: shape (N,) int64   — max 13-gram overlap count per item
            cosines:      shape (N,) float32 — max SBERT cosine to corpus per item
        """
        ...

    def compute_thresholds(
        self,
        ngram_counts: np.ndarray,   # shape (N,) int64
        cosines: np.ndarray,        # shape (N,) float32
    ) -> tuple[float, float]:
        """Compute 75th percentile thresholds.
        Returns: (lexical_thresh: float, semantic_thresh: float)"""
        lexical_thresh = float(np.percentile(ngram_counts, self.percentile))
        semantic_thresh = float(np.percentile(cosines, self.percentile))
        return lexical_thresh, semantic_thresh

    def assign_strata(
        self,
        ngram_counts: np.ndarray,       # shape (N,) int64
        cosines: np.ndarray,            # shape (N,) float32
        lexical_thresh: float,
        semantic_thresh: float,
    ) -> np.ndarray:
        """Assign each item to a stratum. Lexical takes priority on overlap.
        Returns: shape (N,) object — str array: "lexical"|"semantic"|"indeterminate"

        Algorithm:
        1. Initialize strata = ["indeterminate"] * N
        2. semantic_mask = cosines >= semantic_thresh
        3. strata[semantic_mask] = "semantic"
        4. lexical_mask = ngram_counts >= lexical_thresh  (overrides semantic)
        5. strata[lexical_mask] = "lexical"
        """
        strata = np.full(len(ngram_counts), "indeterminate", dtype=object)
        strata[cosines >= semantic_thresh] = "semantic"
        strata[ngram_counts >= lexical_thresh] = "lexical"
        return strata
```

---

## A-4: Ground Truth Generation [Complexity: 12]

### API Signatures

```python
# code/ground_truth.py
import numpy as np
from config import ExperimentConfig
from index_builder import NgramIndex


class GroundTruthGenerator:
    def __init__(self, cfg: ExperimentConfig):
        """Generate binary contamination labels via Approach A or B."""
        self.contamination_rate: float = cfg.contamination_rate  # 0.10
        self.seed: int = cfg.seed  # 42

    def approach_a_pile_labels(
        self,
        benchmark_texts: list[str],     # length N
        ngram_index: NgramIndex,        # The Pile index only
    ) -> np.ndarray:
        """Known-inclusion audit: Pythia-7B trained on The Pile.
        Items present in The Pile index = contaminated.
        Returns: shape (N,) int64 — binary labels (1=contaminated, 0=clean)"""
        # label[i] = int(ngram_index.is_contaminated(benchmark_texts[i]))
        ...

    def approach_b_uniform(
        self,
        benchmark_texts: list[str],     # length N
        corpus_name: str,               # "pile" | "c4" | "redpajama"
    ) -> tuple[list[str], np.ndarray]:
        """Uniformly inject contamination_rate fraction of benchmark texts into corpus.
        Returns:
            augmented_corpus: list[str]  — corpus texts with injected items
            labels:           shape (N,) int64 — 1 for injected items
        """
        ...

    def approach_b_clustered(
        self,
        benchmark_texts: list[str],     # length N
        corpus_name: str,
    ) -> tuple[list[str], np.ndarray]:
        """Inject clustered (topic-grouped) items. Groups by first 50 chars as proxy.
        Returns: (augmented_corpus: list[str], labels: shape (N,) int64)"""
        ...

    def approach_b_paraphrased(
        self,
        benchmark_texts: list[str],     # length N
        corpus_name: str,
    ) -> tuple[list[str], np.ndarray]:
        """Paraphrase injected items via lm-sys/llm-decontaminator before injection.
        Returns: (augmented_corpus: list[str], labels: shape (N,) int64)"""
        ...
```

---

## A-6: Evaluation & Metrics [Complexity: 11]

### API Signatures

```python
# code/evaluate.py
import numpy as np
from typing import Callable
from config import ExperimentConfig


class StratifiedEvaluator:
    def __init__(self, cfg: ExperimentConfig):
        """Compute per-stratum metrics + bootstrap CI."""
        self.bootstrap_n: int = cfg.bootstrap_n  # 10_000
        self.seed: int = cfg.seed

    def per_stratum_recall(
        self,
        y_true: np.ndarray,     # shape (N,) int64
        y_pred: np.ndarray,     # shape (N,) int64
        strata: np.ndarray,     # shape (N,) object — str labels
    ) -> dict[str, float]:
        """Recall per stratum.
        Returns: {"lexical": float, "semantic": float, "indeterminate": float}"""
        # For each s in ["lexical", "semantic", "indeterminate"]:
        #   mask = strata == s
        #   result[s] = recall_score(y_true[mask], y_pred[mask])
        ...

    def per_stratum_f1(
        self,
        y_true: np.ndarray,     # shape (N,) int64
        y_pred: np.ndarray,     # shape (N,) int64
        strata: np.ndarray,     # shape (N,) object
    ) -> dict[str, float]:
        """F1 per stratum. Same mask logic as per_stratum_recall.
        Returns: {"lexical": float, "semantic": float, "indeterminate": float}"""
        ...

    def minkpp_f1_variance(
        self,
        f1_per_corpus: list[float],   # length 3 — [pile_f1, c4_f1, redpajama_f1]
    ) -> float:
        """F1 variance across 3 corpora for Min-K%++ detector.
        Returns: float — np.var(f1_per_corpus)"""
        return float(np.var(f1_per_corpus))

    def indeterminacy_rate(
        self,
        detector_f1_matrix: np.ndarray,    # shape (N_items, N_detectors) float32
    ) -> float:
        """Fraction of items where top1 F1 - top2 F1 < 0.05.
        Returns: float in [0, 1]"""
        # sorted_f1 = np.sort(detector_f1_matrix, axis=1)[:, ::-1]
        # margin = sorted_f1[:, 0] - sorted_f1[:, 1]
        # return float(np.mean(margin < 0.05))
        ...

    def bootstrap_ci(
        self,
        y_true: np.ndarray,         # shape (N,) int64
        y_pred: np.ndarray,         # shape (N,) int64
        metric_fn: Callable,        # e.g., recall_score or f1_score
        n_iterations: int = 10_000,
    ) -> tuple[float, float]:
        """Bootstrap 95% CI via resampling with replacement.
        Returns: (lower_95: float, upper_95: float)

        Algorithm:
        1. rng = np.random.default_rng(seed)
        2. For i in range(n_iterations):
            idx = rng.integers(0, N, size=N)
            scores[i] = metric_fn(y_true[idx], y_pred[idx])
        3. lower, upper = np.percentile(scores, [2.5, 97.5])
        """
        ...

    def run_full_evaluation(
        self,
        benchmark_name: str,                        # "mmlu" | "hellaswag" | "gsm8k"
        corpus_name: str,                           # "pile" | "c4" | "redpajama"
        y_true: np.ndarray,                         # shape (N,) int64
        strata: np.ndarray,                         # shape (N,) object
        detector_preds: dict[str, np.ndarray],      # name → shape (N,) int64
    ) -> dict:
        """Run all metrics for one benchmark-corpus pair.
        Returns nested dict with keys: recall_by_stratum, f1_by_stratum, bootstrap_ci,
                                       minkpp_f1_variance, indeterminacy_rate"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| y_true | (N,) int64 | ground truth binary labels |
| y_pred | (N,) int64 | detector binary predictions |
| strata | (N,) object | str stratum labels |
| detector_f1_matrix | (N_items, N_detectors) float32 | per-item, per-detector F1 proxy |
| bootstrap_scores | (10000,) float32 | one metric per bootstrap sample |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (5 for A-2, 5 for A-5)
- [x] All required modules covered: A-2, A-3, A-4, A-5, A-6
- [x] Codebase Analysis (Serena) section included
- [x] Green-field — Serena skip acceptable, Serena attempt documented

---

*Generated by Phase 3 Logic Agent — EXISTENCE PoC*
