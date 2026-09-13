# Logic: H-E1 — Conditional Demographic Association Density Pipeline

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Generated:** 2026-03-14

Applied: Standard Python corpus processing pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None — new implementation

---

## A-2: Corpus Filter Module [Complexity: 16, Budget: 4]

### API Signatures

```python
class CorpusFilter:
    def __init__(self, fasttext_model_path: str, seed: int = 42):
        """Load fastText model; set RNG seed."""
        ...

    def load_and_sample(self, dataset_id: str, n_docs: int) -> list[dict]:
        """Stream dataset_id, collect n_docs dicts with 'text' field deterministically.
        Returns: list of dicts, len == n_docs, each dict has at least 'text': str
        """
        ...

    def score_documents(self, docs: list[dict]) -> list[float]:
        """Run fasttext-oh-eli5 on each doc['text'].
        docs: list[dict]  # len N
        scores: list[float]  # len N, each in [0.0, 1.0]
        """
        ...

    def apply_fasttext_filter(
        self,
        docs: list[dict],
        scores: list[float],
        percentile: int,
    ) -> list[dict]:
        """Keep docs whose score >= np.percentile(scores, percentile).
        docs: list[dict]  # len N
        scores: list[float]  # len N
        percentile: int  # e.g. 10, 30, 50, 70, 90
        Returns: list[dict]  # len ~= N * (1 - percentile/100)
        """
        ...

    def apply_doremi_reweight(
        self,
        docs: list[dict],
        domain_key: str = "source",
    ) -> list[dict]:
        """Assign per-doc sampling weights from DoReMi domain weights; resample.
        docs: list[dict]  # each doc has doc[domain_key]: str
        Returns: list[dict]  # resampled subset, ~5M effective docs
        """
        ...

    def save_corpus(self, docs: list[dict], config_id: str, data_dir: str) -> str:
        """Write docs to {data_dir}/corpora/{config_id}.jsonl via jsonlines.
        Returns: absolute path to written file.
        """
        ...

    def load_corpus(self, config_id: str, data_dir: str) -> list[dict]:
        """Read {data_dir}/corpora/{config_id}.jsonl; return list[dict]."""
        ...

    def build_all_corpora(self, data_dir: str) -> dict[str, str]:
        """Orchestrate C0–C6 corpus creation; return {config_id: jsonl_path}.
        Calls: load_and_sample -> score_documents -> apply_fasttext_filter (C1-C5)
               -> apply_doremi_reweight (C6) -> save_corpus for each config.
        Returns: dict[str, str]  # {config_id: path}
        """
        ...
```

### Data Shapes

| Variable | Type | Note |
|----------|------|------|
| docs | list[dict] | Each dict: {'text': str, 'source': str, ...} |
| scores | list[float] | Parallel to docs; fastText score in [0,1] |
| return of build_all_corpora | dict[str, str] | Keys: 'C0'..'C6', values: file paths |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Streaming sampler | `load_and_sample`: HF streaming + deterministic seed=42, itertools.islice to n_docs |
| L-2-2 | fastText scorer + filter | `score_documents` + `apply_fasttext_filter`: batch predict, np.percentile threshold |
| L-2-3 | DoReMi reweighter | `apply_doremi_reweight`: load domain weights, np.random.choice with p=weights |
| L-2-4 | JSONL I/O + orchestration | `save_corpus`, `load_corpus`, `build_all_corpora`: jsonlines writer/reader, config loop |

---

## A-3: Entropy Measurement Module [Complexity: 14, Budget: 3]

### API Signatures

```python
class EntropyMeasure:
    def __init__(
        self,
        occ_lexicon: list[str],
        demo_lexicon: list[str],
        window_size: int = 10,
    ):
        """Store lexicons as frozensets for O(1) lookup; store window_size."""
        ...

    def compute_joint_counts(
        self,
        docs: list[dict],
    ) -> dict[str, dict[str, int]]:
        """Scan each doc text with sliding window; accumulate co-occurrence counts.
        docs: list[dict]  # each has 'text': str
        Returns: joint_counts[demo_token][occ_token] = int
        """
        ...

    def joint_counts_to_arrays(
        self,
        joint_counts: dict[str, dict[str, int]],
    ) -> tuple[list[int], list[int]]:
        """Flatten joint_counts into parallel integer arrays for pyitlib.
        Returns: (X_array, Y_array)  # X=demo indices, Y=occ indices, len=sum(counts)
        """
        ...

    def compute_conditional_entropy(
        self,
        docs: list[dict],
    ) -> float:
        """Compute H(occupation|demographic) for a single corpus.
        Calls compute_joint_counts -> joint_counts_to_arrays ->
              drv.entropy_conditional(Y_array, X_array).
        Returns: float  # H value in bits
        """
        ...

    def compute_all_entropies(
        self,
        corpora: dict[str, list[dict]],
    ) -> dict[str, float]:
        """Run compute_conditional_entropy for each config_id.
        corpora: dict[str, list[dict]]  # {'C0': [...], ..., 'C6': [...]}
        Returns: dict[str, float]  # {'C0': H0, ..., 'C6': H6}
        """
        ...
```

### Pseudo-code: compute_joint_counts (non-trivial window scan)

```
For each doc in docs:
    tokens = doc['text'].lower().split()
    For i, token in enumerate(tokens):
        If token in demo_lexicon:
            window = tokens[max(0, i-window_size) : i+window_size+1]
            For w in window (w != token):
                If w in occ_lexicon:
                    joint_counts[token][w] += 1
Return joint_counts
```

### Data Shapes

| Variable | Type | Note |
|----------|------|------|
| joint_counts | dict[str, dict[str, int]] | joint_counts[demo][occ] = count; ~50 x 60 entries |
| X_array, Y_array | list[int] | Parallel; length = total co-occurrence events |
| entropies | dict[str, float] | {'C0': H0, ..., 'C6': H6}; 7 scalar values |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Window scanner | `compute_joint_counts`: tokenize, sliding window, accumulate into nested dict |
| L-3-2 | Array converter | `joint_counts_to_arrays`: flatten counts to repeat-expanded int arrays for pyitlib |
| L-3-3 | Entropy driver | `compute_conditional_entropy` + `compute_all_entropies`: pyitlib call + config loop |
