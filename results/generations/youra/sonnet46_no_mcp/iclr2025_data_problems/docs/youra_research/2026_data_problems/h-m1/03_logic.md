# Logic Document: H-M1
# Cross-Corpus Contamination Variance: The Pile v1, C4 en.noclean, RedPajama-v1

**Hypothesis**: H-M1 | **Type**: MECHANISM (PoC) | **Date**: 2026-05-04

Applied: Standard Python data analysis pipeline (CPU-only, no DL framework)

---

## Codebase Analysis (Serena)

**Project Type**: green-field (incremental over H-E1 specification)
**Status**: green-field - new API design (h-e1/code/ was not implemented)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-4: Corpus Index Construction [Complexity: 18, Budget: 5 subtasks]

**Applied**: MinHash LSH streaming + checkpointing pattern

### API Signatures

```python
import pickle
import time
import logging
from pathlib import Path
from datasketch import MinHash, MinHashLSH
from datasets import load_dataset

class CorpusIndexer:
    def __init__(self, config: Config, extractor: NgramExtractor):
        """Initialize with config and extractor."""
        self.config = config
        self.extractor = extractor

    def load_or_build(self, corpus_name: str) -> MinHashLSH:
        """Load index from path if exists, else call build(). Returns MinHashLSH."""
        ...

    def build(self, corpus_name: str) -> MinHashLSH:
        """Stream HF corpus, build MinHash LSH, checkpoint every 500k docs.
        Falls back to 10% sample after retry_attempts failures.
        """
        ...

    def _stream_corpus(self, corpus_name: str):
        """Yield (doc_id: int, text: str) with exponential-backoff retry."""
        ...

    def checkpoint(self, lsh: MinHashLSH, corpus_name: str, doc_id: int) -> None:
        """Save incremental checkpoint to indices/{corpus_name}_ckpt_{doc_id}.pkl."""
        ...

    def save(self, lsh: MinHashLSH, path: str) -> None:
        """Serialize MinHashLSH to pickle file at path."""
        ...

    def load(self, path: str) -> MinHashLSH:
        """Deserialize MinHashLSH from pickle file at path."""
        ...
```

### Array Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| corpus_name | str | "pile" / "c4" / "redpajama" |
| doc_id | int | Running document counter |
| lsh | MinHashLSH | In-memory index object |
| ckpt path | str | indices/{corpus_name}_ckpt_{doc_id}.pkl |

### Pseudo-code: `build()` streaming + checkpointing loop

```
def build(corpus_name):
    index_path = config.{corpus_name}_index_path
    lsh = MinHashLSH(threshold=0.5, num_perm=128)

    try:
        stream = _stream_corpus(corpus_name)   # with retry logic
    except StreamingError after 3 attempts:
        stream = _fallback_10pct_sample(corpus_name)
        flag_in_results(corpus_name + "_SAMPLED")

    for doc_id, text in enumerate(stream):
        if not text or text.strip() == "":
            continue  # skip missing text field
        minhash = extractor.text_to_minhash(text)
        lsh.insert(f"doc_{doc_id}", minhash)

        if (doc_id + 1) % config.checkpoint_interval == 0:
            checkpoint(lsh, corpus_name, doc_id + 1)
            logging.info(f"Building {corpus_name} index: {doc_id+1:,} docs processed")

    save(lsh, index_path)
    return lsh
```

### Pseudo-code: `_stream_corpus()` with exponential backoff

```
def _stream_corpus(corpus_name):
    hf_path = config.corpus_configs[corpus_name]["hf_path"]
    hf_cfg  = config.corpus_configs[corpus_name]["config"]  # None or "en.noclean"

    for attempt in range(config.retry_attempts):  # 0, 1, 2
        try:
            dataset = load_dataset(hf_path, hf_cfg, streaming=True, split="train")
            for doc in dataset:
                text = doc.get("text", "")
                yield text
            return  # success
        except Exception as e:
            wait = 2 ** attempt  # 1s, 2s, 4s
            logging.warning(f"Stream attempt {attempt+1} failed: {e}. Retrying in {wait}s")
            time.sleep(wait)

    raise StreamingError(f"All {config.retry_attempts} attempts failed for {corpus_name}")
```

### Pseudo-code: `checkpoint()` / `save()` / `load()` pickle protocol

```
def checkpoint(lsh, corpus_name, doc_id):
    path = Path(config.indices_dir) / f"{corpus_name}_ckpt_{doc_id}.pkl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(lsh, f, protocol=pickle.HIGHEST_PROTOCOL)

def save(lsh, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(lsh, f, protocol=pickle.HIGHEST_PROTOCOL)

def load(path):
    with open(path, "rb") as f:
        return pickle.load(f)
```

### Pseudo-code: fallback 10% sample

```
def _fallback_10pct_sample(corpus_name):
    hf_path = config.corpus_configs[corpus_name]["hf_path"]
    hf_cfg  = config.corpus_configs[corpus_name]["config"]
    ds = load_dataset(hf_path, hf_cfg, split="train")  # non-streaming
    n = len(ds)
    import random
    random.seed(config.seed)
    sample_ids = set(random.sample(range(n), int(n * config.sample_fraction)))
    for doc_id in sorted(sample_ids):
        yield doc_id, ds[doc_id].get("text", "")
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | load_or_build cache logic | Path existence check, branch to build() or load() |
| L-4-2 | _stream_corpus with retry | HF load_dataset streaming, exponential backoff (2^attempt s), 3 attempts |
| L-4-3 | build() main loop | Enumerate stream, skip empty text, minhash insert, interval logging |
| L-4-4 | checkpoint / save / load | pickle.dump/load with Path.mkdir(exist_ok=True), ckpt naming |
| L-4-5 | fallback 10% sample | sample_fraction=0.1, non-streaming load, random.sample, flag in results dict |

---

## A-6: Statistical Analysis [Complexity: 14, Budget: 4 subtasks]

**Applied**: statistical analysis scipy/scikit-posthocs pattern

### API Signatures

```python
import pandas as pd
import numpy as np
from scipy.stats import kruskal, spearmanr
import scikit_posthocs as sp
from itertools import combinations

class StatsAnalyzer:
    def __init__(self, config: Config):
        """Initialize with config thresholds."""
        self.config = config

    def kruskal_wallis(self, matrix_wide: pd.DataFrame) -> dict:
        """Run Kruskal-Wallis H-test on 3 corpus rate columns.
        Input: matrix_wide columns=['pile','c4','redpajama'], shape [59, 3].
        Returns: {kruskal_H, kruskal_p, gate_pass, corpus_means, max_pair_diff_pp}.
        """
        ...

    def dunn_posthoc(self, matrix_wide: pd.DataFrame) -> pd.DataFrame:
        """Dunn's test with Bonferroni correction.
        Input: matrix_wide [59, 3]. Returns 3x3 p-value DataFrame.
        """
        ...

    def spearman_wimbd(
        self, pile_rates: pd.Series, wimbd_reference: dict
    ) -> tuple[float, float]:
        """Spearman correlation between Pile column and WIMBD published rates.
        pile_rates: Series indexed by subtask name.
        wimbd_reference: {subtask_name: float}.
        Returns: (rho: float, p_value: float).
        """
        ...

    def sensitivity_analysis(
        self, matrix_wide_primary: pd.DataFrame, matrix_wide_sensitivity: pd.DataFrame
    ) -> dict:
        """Compare primary (question+choices) vs sensitivity (question-only).
        Returns: {sensitivity_kruskal_p, format_spearman_rho}.
        """
        ...

    def assert_gate(self, p_value: float) -> None:
        """Hard assertion: p_value < 0.05."""
        ...
```

### Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| matrix_wide | [59, 3] DataFrame | columns: pile, c4, redpajama; index: subtask name |
| pile_rates | [N_overlap] Series | N_overlap = subtasks in both H-M1 and WIMBD |
| wimbd_reference | dict[str, float] | {subtask_name: contamination_rate} |
| dunn result | [3, 3] DataFrame | p-values for all corpus pairs |

### Pseudo-code: `kruskal_wallis()`

```
def kruskal_wallis(matrix_wide):
    pile_rates = matrix_wide["pile"].values       # shape [59]
    c4_rates   = matrix_wide["c4"].values         # shape [59]
    rp_rates   = matrix_wide["redpajama"].values  # shape [59]

    H, p = kruskal(pile_rates, c4_rates, rp_rates)
    means = {
        "pile":      float(np.mean(pile_rates)),
        "c4":        float(np.mean(c4_rates)),
        "redpajama": float(np.mean(rp_rates)),
    }
    max_pair_diff = max(
        abs(m1 - m2) for m1, m2 in combinations(means.values(), 2)
    ) * 100  # convert to pp

    return {
        "kruskal_H":        float(H),
        "kruskal_p":        float(p),
        "gate_pass":        bool(p < config.gate_p_threshold),
        "corpus_means":     means,
        "max_pair_diff_pp": max_pair_diff,
    }
```

### Pseudo-code: `dunn_posthoc()`

```
def dunn_posthoc(matrix_wide):
    groups = [
        matrix_wide["pile"].values.tolist(),
        matrix_wide["c4"].values.tolist(),
        matrix_wide["redpajama"].values.tolist(),
    ]
    result = sp.posthoc_dunn(groups, p_adjust="bonferroni")
    result.index   = ["pile", "c4", "redpajama"]
    result.columns = ["pile", "c4", "redpajama"]
    return result  # shape [3, 3]; diagonal = 1.0
```

### Pseudo-code: `spearman_wimbd()`

```
def spearman_wimbd(pile_rates, wimbd_reference):
    common     = pile_rates.index.intersection(list(wimbd_reference.keys()))
    h_m1_vals  = pile_rates.loc[common].values
    wimbd_vals = np.array([wimbd_reference[k] for k in common])
    rho, p = spearmanr(h_m1_vals, wimbd_vals)
    return float(rho), float(p)
```

### Pseudo-code: `sensitivity_analysis()`

```
def sensitivity_analysis(matrix_wide_primary, matrix_wide_sensitivity):
    kw = kruskal_wallis(matrix_wide_sensitivity)
    sensitivity_kruskal_p = kw["kruskal_p"]

    rhos = {}
    for corp in ["pile", "c4", "redpajama"]:
        rho, _ = spearmanr(
            matrix_wide_primary[corp].values,
            matrix_wide_sensitivity[corp].values
        )
        rhos[corp] = float(rho)

    return {
        "sensitivity_kruskal_p": sensitivity_kruskal_p,
        "format_spearman_rho":   rhos,
    }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | kruskal_wallis() | Extract 3 rate arrays, scipy.stats.kruskal, corpus_means + max_pair_diff_pp |
| L-6-2 | dunn_posthoc() | sp.posthoc_dunn Bonferroni, 3x3 DataFrame with corpus labels |
| L-6-3 | spearman_wimbd() | Align by common index, spearmanr on aligned arrays |
| L-6-4 | sensitivity_analysis() | Kruskal on sensitivity matrix, per-corpus format Spearman |

---

## A-5: Contamination Matrix [Complexity: 13, Budget: 2 subtasks]

**Applied**: Standard Python iteration with pandas aggregation

### API Signatures

```python
import pandas as pd
from datasketch import MinHashLSH
import logging

class MatrixBuilder:
    def __init__(self, config: Config, extractor: NgramExtractor):
        """Initialize with config and extractor."""
        self.config = config
        self.extractor = extractor

    def query_cell(
        self,
        subtask_name: str,
        texts: list[str],
        corpus_name: str,
        lsh: MinHashLSH,
    ) -> dict:
        """Compute contamination for one (subtask, corpus) cell.
        texts: list of formatted benchmark strings, len = n_items.
        Returns: {subtask, corpus, n_items, n_contaminated, rate}.
        """
        ...

    def build_matrix(
        self,
        benchmarks: dict[str, list[str]],
        indices: dict[str, MinHashLSH],
    ) -> pd.DataFrame:
        """Iterate 59 subtasks x 3 corpora, collect query_cell results.
        Returns DataFrame shape [177, 5]: subtask, corpus, n_items, n_contaminated, rate.
        """
        ...

    def to_wide(self, matrix_df: pd.DataFrame) -> pd.DataFrame:
        """Pivot long [177, 5] to wide [59, 3]; index=subtask, columns=corpus."""
        ...
```

### Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| matrix_df (long) | [177, 5] DataFrame | subtask, corpus, n_items, n_contaminated, rate |
| matrix_wide | [59, 3] DataFrame | index=subtask, columns=pile/c4/redpajama |

### Pseudo-code: `query_cell()` + `build_matrix()`

```
def query_cell(subtask_name, texts, corpus_name, lsh):
    n_contaminated = 0
    for text in texts:
        minhash = extractor.text_to_minhash(text)
        results = lsh.query(minhash)
        if results:
            n_contaminated += 1
    n_items = len(texts)
    rate = n_contaminated / n_items if n_items > 0 else 0.0
    logging.info(
        f"Querying {corpus_name} for sub-task {subtask_name}: "
        f"{n_contaminated}/{n_items} contaminated ({rate:.3f})"
    )
    return {"subtask": subtask_name, "corpus": corpus_name,
            "n_items": n_items, "n_contaminated": n_contaminated, "rate": rate}

def build_matrix(benchmarks, indices):
    rows = []
    for subtask_name, texts in benchmarks.items():
        for corpus_name, lsh in indices.items():
            rows.append(query_cell(subtask_name, texts, corpus_name, lsh))
    df = pd.DataFrame(rows)  # shape [177, 5]
    assert len(df) == 177, f"Expected 177 rows, got {len(df)}"
    return df
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | query_cell() | Per-item lsh.query loop, count contaminated, log progress |
| L-5-2 | build_matrix() + to_wide() | 59x3 nested iteration, DataFrame construction, pivot to wide |

---

## A-2: Benchmark Data Loading [Complexity: 10, Budget: 2 subtasks]

**Applied**: HuggingFace datasets version-pinned loading pattern

### API Signatures

```python
from datasets import load_dataset, get_dataset_config_names

class DataLoader:
    def __init__(self, config: Config):
        """Initialize with config (text_format, version pins)."""
        self.config = config

    def load_all(self) -> dict[str, list[str]]:
        """Load all 59 sub-tasks with version pinning. Returns {subtask_name: [text, ...]}."""
        ...

    def load_mmlu(self) -> dict[str, list[str]]:
        """Load 57 MMLU sub-tasks pinned to v1.0.0. Returns {subtask_name: [text, ...]}."""
        ...

    def load_hellaswag(self) -> dict[str, list[str]]:
        """Load HellaSwag validation split. Returns {"hellaswag": [text, ...]}."""
        ...

    def load_bbh(self) -> dict[str, list[str]]:
        """Load BBH all tasks merged into one group. Returns {"bbh": [text, ...]}."""
        ...

    def format_text(self, item: dict, dataset: str) -> str:
        """Format item per config.text_format. dataset: 'mmlu'|'hellaswag'|'bbh'.
        Returns lowercased string.
        """
        ...
```

### Pseudo-code: `load_all()` with version pinning

```
def load_all():
    result = {}

    # MMLU: 57 sub-tasks, pinned revision
    all_tasks = get_dataset_config_names("cais/mmlu")
    mmlu_tasks = [t for t in all_tasks if t != "all"]
    for task_name in mmlu_tasks:
        ds = load_dataset("cais/mmlu", task_name, split="test",
                          revision="v1.0.0", trust_remote_code=False)
        result[task_name] = [format_text(item, "mmlu") for item in ds]

    # HellaSwag: validation split
    hs = load_dataset("Rowan/hellaswag", split="validation")
    result["hellaswag"] = [format_text(item, "hellaswag") for item in hs]

    # BBH: all 23 sub-tasks merged
    bbh_configs = get_dataset_config_names("lukaemon/bbh")
    bbh_texts = []
    for task_name in bbh_configs:
        ds = load_dataset("lukaemon/bbh", task_name, split="test")
        bbh_texts.extend([format_text(item, "bbh") for item in ds])
    result["bbh"] = bbh_texts

    assert len(result) == 59, f"Expected 59 sub-tasks, got {len(result)}"
    return result
```

### Pseudo-code: `format_text()` dispatch

```
def format_text(item, dataset):
    fmt = config.text_format  # "question_choices" or "question_only"

    if dataset == "mmlu":
        q = item["question"]
        c = item["choices"]   # list[str], len=4
        text = f"{q} {' '.join(c)}" if fmt == "question_choices" else q

    elif dataset == "hellaswag":
        q = item["ctx"]
        c = item["endings"]   # list[str], len=4
        text = f"{q} {' '.join(c)}" if fmt == "question_choices" else q

    elif dataset == "bbh":
        q = item.get("input", "")
        t = str(item.get("target", ""))
        text = f"{q} {t}" if fmt == "question_choices" else q

    return text.lower().strip()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_all() version-pinned | MMLU v1.0.0, HellaSwag val, BBH merged, assert 59 keys |
| L-2-2 | format_text() dispatch | mmlu/hellaswag/bbh dispatch, question+choices or question-only, lowercased |

---

## Subtask Summary [13/13 used]

| ID | Subtask | Parent | Description |
|----|---------|--------|-------------|
| L-4-1 | load_or_build cache | A-4 | Path existence check, branch to build() or load() |
| L-4-2 | _stream_corpus retry | A-4 | HF streaming, exponential backoff 2^attempt s, 3 attempts |
| L-4-3 | build() main loop | A-4 | Enumerate stream, skip empty, minhash insert, checkpoint logging |
| L-4-4 | checkpoint/save/load | A-4 | pickle HIGHEST_PROTOCOL, Path.mkdir, ckpt naming convention |
| L-4-5 | fallback 10% sample | A-4 | Non-streaming load, random.sample with seed, SAMPLED flag |
| L-6-1 | kruskal_wallis() | A-6 | H, p, gate_pass, corpus_means, max_pair_diff_pp |
| L-6-2 | dunn_posthoc() | A-6 | posthoc_dunn Bonferroni, 3x3 DataFrame with corpus labels |
| L-6-3 | spearman_wimbd() | A-6 | Align by common index, spearmanr on aligned arrays |
| L-6-4 | sensitivity_analysis() | A-6 | Kruskal on sensitivity matrix, per-corpus format Spearman |
| L-5-1 | query_cell() | A-5 | lsh.query per item, contaminated/total rate, progress log |
| L-5-2 | build_matrix()+to_wide() | A-5 | 59x3 nested loop, assert 177 rows, pivot to wide |
| L-2-1 | load_all() | A-2 | MMLU v1.0.0, HellaSwag val, BBH merged, assert 59 keys |
| L-2-2 | format_text() | A-2 | Dataset dispatch, question+choices or question-only, lowercase |
