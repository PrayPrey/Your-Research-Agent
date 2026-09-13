# Logic Document: H-E1
# Cross-Sub-Task Contamination Variance in The Pile v1

**Hypothesis**: H-E1 | **Type**: EXISTENCE (PoC) | **Date**: 2026-05-04

Applied: EXISTENCE-minimal-pipeline (single forward path, no ablation, CPU-only statistical pipeline)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation from scratch

---

## A-4: Pile Index Query [Complexity: 14, Budget: 3 subtasks]

Applied: Standard retry-with-backoff pattern + datasketch MinHash LSH fallback

### API Signatures

```python
# code/pile_query.py
import os, time, logging
from datasketch import MinHashLSH, MinHash
from wimbd.es import has_ngram  # primary path

class PileQuery:
    def __init__(self, config: Config, extractor: NgramExtractor):
        """Initialize with config and extractor; detect wimbd availability."""
        self._mode: str = "wimbd" if self._use_wimbd() else "fallback_minhash"
        self._lsh: Optional[MinHashLSH] = None  # lazy-init for fallback

    def _use_wimbd(self) -> bool:
        """Returns True if WIMBD_ES_HOST env var is set and non-empty."""
        return bool(os.environ.get("WIMBD_ES_HOST", "").strip())

    def _init_minhash_lsh(self) -> MinHashLSH:
        """Lazy-init MinHashLSH(threshold=0.5, num_perm=128) for fallback mode."""
        # MinHashLSH(threshold=0.5, num_perm=128)
        ...

    def _query_wimbd_with_retry(self, ngram: str) -> bool:
        """Query wimbd with 3 attempts, exponential backoff (1s, 2s, 4s).
        Returns True if ngram found in Pile index."""
        # ngram: str -> bool
        for attempt in range(self.config.retry_attempts):  # 3
            try:
                return has_ngram(ngram, n=13, index=self.config.pile_index)
            except Exception as e:
                if attempt == self.config.retry_attempts - 1:
                    logging.warning(f"wimbd query failed after 3 attempts: {e}")
                    return False
                time.sleep(2 ** attempt)  # 1s, 2s, 4s

    def _query_minhash(self, ngrams: list[str]) -> bool:
        """MinHash LSH fallback: check if any ngram shingle matches LSH index.
        Returns True if Jaccard similarity >= 0.5 with any Pile document."""
        # ngrams: list[str] -> bool
        ...

    def is_contaminated(self, text: str) -> int:
        """Returns 1 if any 13-gram matches Pile index, 0 otherwise.
        text: str -> int (0 or 1)"""
        ngrams = self.extractor.extract(text)  # list[str]
        if not ngrams:
            return 0
        if self._mode == "wimbd":
            return int(any(self._query_wimbd_with_retry(ng) for ng in ngrams))
        else:
            return int(self._query_minhash(ngrams))

    def query_subtask(self, name: str, texts: list[str]) -> list[int]:
        """Returns per-item contamination labels [0/1] for one sub-task.
        texts: list[str], len=N -> list[int], len=N"""
        labels = []
        for text in texts:
            labels.append(self.is_contaminated(text))
        count = sum(labels)
        rate = count / len(labels) if labels else 0.0
        logging.info(f"Querying wimbd for sub-task {name}: {count}/{len(labels)} items contaminated ({rate:.3f})")
        return labels

    def query_all(self, subtask_texts: dict[str, list[str]]) -> dict[str, list[int]]:
        """Returns {subtask_name: [0/1, ...]} for all 59 sub-tasks.
        subtask_texts: dict[str, list[str]] -> dict[str, list[int]]"""
        return {name: self.query_subtask(name, texts) for name, texts in subtask_texts.items()}

    @property
    def mode(self) -> str:
        """Returns 'wimbd' or 'fallback_minhash'."""
        return self._mode
```

### Pseudo-code (retry + fallback decision)

```
is_contaminated(text):
  ngrams = extractor.extract(text)  # [] if < 13 tokens
  if mode == "wimbd":
    for ng in ngrams:
      result = _query_wimbd_with_retry(ng)  # 3x backoff
      if result: return 1
    return 0
  else:
    return _query_minhash(ngrams)  # Jaccard >= 0.5
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | wimbd integration | `_query_wimbd_with_retry` using `has_ngram(ng, n=13, index="pile")` |
| L-4-2 | MinHash fallback | `_init_minhash_lsh` + `_query_minhash` with `MinHashLSH(threshold=0.5, num_perm=128)` |
| L-4-3 | retry + logging | Exponential backoff loop (3x), per-subtask progress logging in `query_subtask` |

---

## A-5: Statistical Analysis [Complexity: 12, Budget: 1 subtask]

Applied: Standard scipy.stats API pattern

### API Signatures

```python
# code/stats_analyzer.py
import pandas as pd
from scipy.stats import kruskal, spearmanr

class StatsAnalyzer:
    def __init__(self, config: Config):
        """Store config for gate threshold access."""
        ...

    def compute_rates(self, labels: dict[str, list[int]]) -> pd.DataFrame:
        """Compute per-subtask contamination rates.
        labels: dict[str, list[int]] -> DataFrame[subtask, n_items, n_contaminated, rate]"""
        rows = []
        for subtask, lbls in labels.items():
            n = len(lbls)
            c = sum(lbls)
            rows.append({"subtask": subtask, "n_items": n, "n_contaminated": c, "rate": c / n if n else 0.0})
        return pd.DataFrame(rows)

    def kruskal_wallis(self, labels: dict[str, list[int]]) -> dict:
        """Kruskal-Wallis H-test across all 59 sub-tasks.
        labels: dict[str, list[int]] -> {kruskal_stat, p_value, gate_pass, max_pair_diff}"""
        label_lists = list(labels.values())
        stat, p = kruskal(*label_lists)
        rates = {k: sum(v) / len(v) for k, v in labels.items() if v}
        max_diff = max(rates.values()) - min(rates.values())
        return {
            "kruskal_stat": float(stat),
            "p_value": float(p),
            "gate_pass": p < self.config.gate_p_threshold,
            "max_pair_diff": float(max_diff),
        }

    def spearman_correlation(
        self, rates_a: pd.Series, rates_b: pd.Series
    ) -> tuple[float, float]:
        """Spearman rho between two rate series (primary vs sensitivity).
        rates_a, rates_b: pd.Series[float], len=59 -> (rho: float, p_value: float)"""
        rho, p = spearmanr(rates_a.values, rates_b.values)
        return float(rho), float(p)

    def sanity_check(self, rates_df: pd.DataFrame, reference: dict) -> pd.DataFrame:
        """Compare our rates vs WIMBD Table 2 (tolerance ±5 pp).
        rates_df: DataFrame[subtask, rate] -> DataFrame[subtask, our_rate, ref_rate, diff, within_tol]"""
        rows = []
        for subtask, ref_rate in reference.items():
            our = rates_df.loc[rates_df["subtask"] == subtask, "rate"]
            our_val = float(our.iloc[0]) if len(our) else float("nan")
            diff = abs(our_val - ref_rate)
            rows.append({
                "subtask": subtask, "our_rate": our_val,
                "ref_rate": ref_rate, "diff": diff,
                "within_tol": diff <= self.config.max_pair_diff_threshold,
            })
        return pd.DataFrame(rows)

    def assert_gate(self, p_value: float) -> None:
        """Hard assertion: p_value < 0.05 or raise AssertionError."""
        assert p_value < self.config.gate_p_threshold, \
            f"Gate FAILED: p={p_value:.4f} >= {self.config.gate_p_threshold}"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | gate assertion + sanity check | `assert_gate` hard assertion + `sanity_check` ±5pp tolerance vs WIMBD Table 2 |

---

## A-7: Orchestration + Sensitivity [Complexity: 11, Budget: 1 subtask]

Applied: Standard pipeline orchestration pattern

### API Signatures

```python
# code/run_experiment.py
import pandas as pd
from code.config import Config, load_config
from code.data_loader import DataLoader
from code.ngram_extractor import NgramExtractor
from code.pile_query import PileQuery
from code.stats_analyzer import StatsAnalyzer
from code.visualizer import Visualizer

def run_primary(config: Config) -> dict:
    """Full pipeline: load -> extract ngrams (embedded in query) -> query Pile -> stats -> visualize -> assert gate.
    Returns: {"rates_df": pd.DataFrame, "stats": dict, "labels": dict[str, list[int]]}"""
    loader = DataLoader(config)
    extractor = NgramExtractor(config)
    querier = PileQuery(config, extractor)
    analyzer = StatsAnalyzer(config)
    viz = Visualizer(config)

    subtask_texts = loader.load_all()              # dict[str, list[str]], 59 keys
    labels = querier.query_all(subtask_texts)      # dict[str, list[int]]
    rates_df = analyzer.compute_rates(labels)      # DataFrame[subtask, n_items, n_contaminated, rate]
    stats = analyzer.kruskal_wallis(labels)        # {kruskal_stat, p_value, gate_pass, max_pair_diff}
    viz.save_all(rates_df, stats)
    analyzer.assert_gate(stats["p_value"])
    return {"rates_df": rates_df, "stats": stats, "labels": labels}

def run_sensitivity(config: Config, primary_rates: pd.DataFrame) -> dict:
    """Repeat pipeline with question-only format; compute Spearman vs primary.
    primary_rates: DataFrame[subtask, rate] ->
    Returns: {"sensitivity_rates_df": pd.DataFrame, "rho": float, "p_value": float}"""
    sens_config = Config(
        **{**config.__dict__, "text_format": "question_only"}
    )
    loader = DataLoader(sens_config)
    extractor = NgramExtractor(sens_config)
    querier = PileQuery(sens_config, extractor)
    analyzer = StatsAnalyzer(sens_config)
    viz = Visualizer(sens_config)

    subtask_texts = loader.load_all()
    labels = querier.query_all(subtask_texts)
    sens_rates_df = analyzer.compute_rates(labels)

    # Align on common subtasks for Spearman
    merged = primary_rates.set_index("subtask")[["rate"]].join(
        sens_rates_df.set_index("subtask")[["rate"]], lsuffix="_primary", rsuffix="_sens"
    ).dropna()
    rho, p = analyzer.spearman_correlation(merged["rate_primary"], merged["rate_sens"])
    viz.plot_sensitivity_scatter(merged["rate_primary"], merged["rate_sens"], rho)
    return {"sensitivity_rates_df": sens_rates_df, "rho": rho, "p_value": p}

def save_results(rates_df: pd.DataFrame, stats: dict, config: Config) -> None:
    """Writes contamination_rates.csv and statistical_tests.json to results/."""
    ...

def main() -> None:
    """Entry point: load_config -> run_primary -> run_sensitivity -> save_results -> assert_gate."""
    config = load_config()
    primary = run_primary(config)
    sensitivity = run_sensitivity(config, primary["rates_df"])
    save_results(primary["rates_df"], {**primary["stats"], "sensitivity": sensitivity}, config)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | sensitivity analysis Spearman | Align primary/sensitivity rates on 59 subtasks, call `spearman_correlation`, pass to `plot_sensitivity_scatter` |

---

## A-2: Benchmark Data Loading [Complexity: 10, Budget: 1 subtask]

Applied: Standard HuggingFace datasets loading pattern

### API Signatures

```python
# code/data_loader.py
from datasets import load_dataset

class DataLoader:
    def __init__(self, config: Config):
        """Store config; text_format determines format_text behavior."""
        ...

    def load_mmlu(self) -> dict[str, list[str]]:
        """Load all 57 MMLU sub-tasks from cais/mmlu v1.0.0 split='test'.
        Returns: {subtask_name: [formatted_text, ...]}  # 57 keys, ~246 items each"""
        # Uses load_dataset("cais/mmlu", subtask, revision="v1.0.0", split="test")
        ...

    def load_hellaswag(self) -> dict[str, list[str]]:
        """Load HellaSwag from Rowan/hellaswag split='validation'.
        Returns: {"hellaswag": [formatted_text, ...]}  # ~10042 items"""
        ...

    def load_bbh(self) -> dict[str, list[str]]:
        """Load BIG-Bench Hard from lukaemon/bbh split='test'.
        Returns: {"bbh": [formatted_text, ...]}  # ~6511 items (all sub-tasks merged)"""
        # BBH has multiple sub-tasks; merge all into single "bbh" key
        ...

    def load_all(self) -> dict[str, list[str]]:
        """Merge MMLU (57) + HellaSwag (1) + BBH (1) = 59 sub-tasks.
        Returns: dict[str, list[str]]  # 59 keys total"""
        return {**self.load_mmlu(), **self.load_hellaswag(), **self.load_bbh()}

    def format_text(self, item: dict, dataset: str) -> str:
        """Format benchmark item to text string per config.text_format.
        dataset: 'mmlu' | 'hellaswag' | 'bbh'
        Returns: str (question+choices or question-only)"""
        if self.config.text_format == "question_only":
            if dataset == "mmlu":
                return item["question"]
            elif dataset == "hellaswag":
                return item["ctx"]
            else:  # bbh
                return item["input"]
        else:  # question_choices (default)
            if dataset == "mmlu":
                return f"{item['question']} {' '.join(item['choices'])}"
            elif dataset == "hellaswag":
                return f"{item['ctx']} {' '.join(item['endings'])}"
            else:  # bbh
                return item["input"]  # BBH has no choices field
```

### Pseudo-code (BBH multi-subtask handling)

```
load_bbh():
  BBH_SUBTASKS = [list of 27 sub-task names from lukaemon/bbh]
  all_texts = []
  for subtask in BBH_SUBTASKS:
    ds = load_dataset("lukaemon/bbh", subtask, split="test")
    for item in ds:
      all_texts.append(format_text(item, "bbh"))
  return {"bbh": all_texts}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | BBH multi-subtask handling | Iterate 27 BBH sub-tasks, merge all items into single "bbh" key; handle missing sub-tasks with log+continue |

---

## Summary: Subtask Budget

| Task | Subtasks Used | Budget |
|------|--------------|--------|
| A-4 | L-4-1, L-4-2, L-4-3 | 3/3 |
| A-5 | L-5-1 | 1/1 |
| A-7 | L-7-1 | 1/1 |
| A-2 | L-2-1 | 1/1 |
| **Total** | **6** | **6/6** |
