# Logic Design: H-E1 — LLM Documentation-Benchmark Registry Construction

**Hypothesis:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-17
**Budget:** 6 logic subtasks

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze. No Serena tool calls performed.
**Analyzed Path:** N/A
**Relevant Symbols:** None — new implementation

---

## Applied KB Patterns

Applied: HuggingFace Hub `hf_hub_download` / `snapshot_download` download pattern
Applied: Standard pipeline stage-filter pattern (load → filter → enrich → assemble)

---

## L-E3a: retrieve_model_cards API + Backoff Pseudo-code [Complexity: 13, Budget: 2]

### API Signatures

```python
# data_collection.py
def retrieve_model_cards(
    model_ids: list[str],
    checkpoint_dir: str,
    max_retries: int = 5,
    base_delay: float = 2.0,
) -> dict[str, dict]:
    """Retrieve HF model cards + model_info for each model_id. Returns accessible subset."""
    # Returns: {model_id: {"card_text": str, "model_info": object}}
```

```python
# utils.py
def exponential_backoff(
    func: callable,
    *args,
    max_retries: int = 5,
    base_delay: float = 2.0,
    **kwargs,
) -> object:
    """Call func(*args, **kwargs) with retry on exception. Raises after max_retries."""
```

### Pseudo-code: retrieve_model_cards

```
1. existing = load_checkpoint(checkpoint_dir/cards.json)  # {model_id: record}
2. remaining = [m for m in model_ids if m not in existing]
3. results = dict(existing)
4. for i, model_id in enumerate(remaining):
5.     try:
6.         card = exponential_backoff(ModelCard.load, model_id)
7.         info = exponential_backoff(HfApi().model_info, model_id)
8.         results[model_id] = {"card_text": card.content, "model_info": info}
9.     except Exception as e:
10.        log_dropout(model_id, "card_retrieval", str(e), dropout_log_path)
11.        continue
12.    if (i + 1) % CHECKPOINT_INTERVAL == 0:
13.        save_checkpoint(list(results.values()), checkpoint_dir/cards.json)
14.        print_progress("card_retrieval", len(results), len(model_ids))
15. save_checkpoint(list(results.values()), checkpoint_dir/cards.json)
16. return results
```

### Pseudo-code: exponential_backoff

```
1. for attempt in range(max_retries):
2.     try:
3.         return func(*args, **kwargs)
4.     except Exception as e:
5.         if attempt == max_retries - 1:
6.             raise
7.         sleep_time = base_delay * (2 ** attempt)  # 2, 4, 8, 16, 32 seconds
8.         time.sleep(sleep_time)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3a-1 | retrieve_model_cards + exponential_backoff | API signatures + backoff pseudo-code |
| L-E3a-2 | Checkpoint/resume logic | load_checkpoint skip, save every 100 models |

---

## L-E3b: Checkpoint / Resume APIs [Complexity: 13, Budget: 0 additional]

### API Signatures

```python
# utils.py
def save_checkpoint(records: list[dict], checkpoint_path: str) -> None:
    """JSON dump records to checkpoint_path (overwrite)."""

def load_checkpoint(checkpoint_path: str) -> list[dict]:
    """Load checkpoint JSON. Returns [] if file not found."""

def log_dropout(
    model_id: str,
    stage: str,
    reason: str,
    log_path: str,
) -> None:
    """Append one row to dropout_log.csv (model_id, stage, reason)."""

def print_progress(stage: str, count: int, total: int | None = None) -> None:
    """Print: '[stage] count/total' using print()."""
```

---

## L-E2a: Leaderboard Load + Filter APIs [Complexity: 9, Budget: 1]

### API Signatures

```python
# data_collection.py
def load_leaderboard() -> pd.DataFrame:
    """Load Open LLM Leaderboard v1 via datasets.load_dataset.
    Returns: DataFrame with columns [model_name] + BENCHMARK_COLS, shape (~3000-5000, 7)."""

def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Keep latest evaluation per model_name (sort by date desc, drop_duplicates).
    Returns: deduplicated DataFrame, shape (~N_unique, 7)."""

def filter_benchmark_coverage(
    df: pd.DataFrame,
    min_benchmarks: int = 4,
) -> pd.DataFrame:
    """Keep rows where count(non-null BENCHMARK_COLS) >= min_benchmarks.
    Returns: filtered DataFrame, shape (~1000-2000, 7)."""
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2a-1 | load/deduplicate/filter APIs | Three functions with return shapes |

---

## L-E4a: extract_curation_features + recover_param_count APIs [Complexity: 11, Budget: 1]

### API Signatures

```python
# feature_extraction.py
def extract_curation_features(card_text: str) -> dict[str, int]:
    """Apply REGEX_PATTERNS case-insensitively to card_text.
    Returns: {"dedup_documented": 0|1, "perplexity_filter_documented": 0|1,
              "domain_composition_documented": 0|1, "decontamination_documented": 0|1}"""

def recover_param_count(
    model_info: object,
    card_text: str,
    model_id: str,
) -> float | None:
    """Recover parameter count N.
    Priority: model_info.safetensors.total -> regex parse card_text -> name-map lookup.
    Returns: float (e.g. 7e9) or None if unrecoverable."""
```

### Pseudo-code: extract_curation_features

```
1. text_lower = card_text.lower()
2. features = {}
3. for feature_name, pattern in REGEX_PATTERNS.items():
4.     match = re.search(pattern, text_lower, re.IGNORECASE)
5.     features[feature_name] = 1 if match else 0
6. return features
```

### Pseudo-code: recover_param_count (priority chain)

```
1. # Priority 1: model_info metadata
2. if model_info and hasattr(model_info, "safetensors") and model_info.safetensors:
3.     total = getattr(model_info.safetensors, "total", None)
4.     if total and total > 0:
5.         return float(total)
6. # Priority 2: parse card_text for "NB" / "N billion" patterns
7. m = re.search(r"(\d+(?:\.\d+)?)\s*[Bb](?:illion)?\s*param", card_text)
8. if m: return float(m.group(1)) * 1e9
9. m = re.search(r"(\d+(?:\.\d+)?)[Bb]\b", card_text)
10. if m: return float(m.group(1)) * 1e9
11. # Priority 3: name-map lookup (hardcoded dict in config.py)
12. for pattern, n_params in PARAM_COUNT_MAP.items():
13.     if re.search(pattern, model_id, re.IGNORECASE):
14.         return n_params
15. return None
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4a-1 | extract_curation_features + recover_param_count | Regex logic + priority chain |

---

## L-E4b: recover_token_count + assign_arch_family + compute_derived_features [Complexity: 11, Budget: 1]

### API Signatures

```python
# feature_extraction.py
def recover_token_count(card_text: str) -> float | None:
    """Regex parse training token count from card_text.
    Patterns: "N trillion tokens", "N billion tokens", "Nt tokens".
    Returns: float (e.g. 1e12) or None."""

def assign_arch_family(model_id: str) -> str:
    """Match model_id against ARCH_FAMILY_PATTERNS (case-insensitive).
    Returns: "LLaMA"|"Mistral"|"Falcon"|"Pythia"|"OLMo"|"Other"."""

def compute_derived_features(
    n_params: float,
    n_tokens: float | None,
) -> dict[str, float | None]:
    """Compute log-scale features.
    Returns: {"log_params": float, "log_tokens": float|None}"""
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4b-1 | token count + arch family + derived features | Three helper function APIs |

---

## L-E5a: build_registry + validate_registry + export_registry [Complexity: 10, Budget: 1]

### API Signatures

```python
# registry_builder.py
def build_registry(
    leaderboard_df: pd.DataFrame,
    model_card_data: dict[str, dict],
) -> pd.DataFrame:
    """Merge benchmark scores + extracted features. Drop rows with n_params=None.
    Returns: registry_df, shape (n_analyzable, 16), columns per FR-7."""
    # Columns: model_id, mmlu, arc_challenge, hellaswag, winogrande, truthfulqa, gsm8k,
    #          dedup_documented, perplexity_filter_documented, domain_composition_documented,
    #          decontamination_documented, doc_score, n_params, log_params, log_tokens, arch_family

def validate_registry(registry_df: pd.DataFrame) -> dict:
    """Check gate conditions.
    Returns: {"n_analyzable": int, "feature_vars": dict[str,float],
              "n_features_with_variance": int, "gate_passed": bool}"""

def export_registry(registry_df: pd.DataFrame, output_path: str) -> None:
    """Write registry_df to CSV at output_path (index=False)."""
```

### Pseudo-code: build_registry

```
1. records = []
2. for model_id, card_data in model_card_data.items():
3.     row = leaderboard_df[leaderboard_df.model_name == model_id].iloc[0]
4.     features = extract_curation_features(card_data["card_text"])
5.     n_params = recover_param_count(card_data["model_info"],
6.                                     card_data["card_text"], model_id)
7.     if n_params is None:
8.         log_dropout(model_id, "param_filter", "unrecoverable_n_params", ...)
9.         continue
10.    n_tokens = recover_token_count(card_data["card_text"])
11.    derived = compute_derived_features(n_params, n_tokens)
12.    arch = assign_arch_family(model_id)
13.    record = {
14.        "model_id": model_id,
15.        **{b: row.get(b) for b in BENCHMARK_COLS},
16.        **features,
17.        "doc_score": sum(features.values()),
18.        "n_params": n_params,
19.        **derived,
20.        "arch_family": arch,
21.    }
22.    records.append(record)
23. registry_df = pd.DataFrame(records)
24. return registry_df

# Gate assertion (called after build_registry in main.py)
assert len(registry_df) >= MIN_REGISTRY_SIZE, \
    f"GATE FAIL: n_analyzable={len(registry_df)} < {MIN_REGISTRY_SIZE}"
feature_vars = {f: registry_df[f].var() for f in FEATURE_COLS}
assert sum(v > 0 for v in feature_vars.values()) >= MIN_FEATURES_WITH_VARIANCE, \
    "GATE FAIL: trivial variance in doc features"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E5a-1 | build/validate/export registry | Full assembly pseudo-code + gate assert |

---

## Complete API Reference

### config.py (constants only)

```python
LEADERBOARD_DATASET: str = "open-llm-leaderboard/results"
BENCHMARK_COLS: list[str] = ["mmlu", "arc_challenge", "hellaswag", "winogrande", "truthfulqa", "gsm8k"]
FEATURE_COLS: list[str] = ["dedup_documented", "perplexity_filter_documented",
                            "domain_composition_documented", "decontamination_documented"]
REGEX_PATTERNS: dict[str, str] = {
    "dedup_documented": r"dedup|near.?dup|minhash|exact.?dedup",
    "perplexity_filter_documented": r"perplexity.{0,20}filter|ppl.{0,10}filter",
    "domain_composition_documented": r"domain.{0,30}(%|percent|composition)|data.{0,30}mix",
    "decontamination_documented": r"decontaminat|n.?gram.{0,20}overlap|benchmark.{0,20}holdout",
}
ARCH_FAMILY_PATTERNS: dict[str, str] = {
    "LLaMA": r"llama|llama2|llama-2",
    "Mistral": r"mistral|mixtral",
    "Falcon": r"falcon",
    "Pythia": r"pythia|eleuther",
    "OLMo": r"olmo",
}
PARAM_COUNT_MAP: dict[str, float] = {
    r"llama.*7b": 7e9, r"llama.*13b": 13e9, r"llama.*70b": 70e9,
    r"falcon.*7b": 7e9, r"falcon.*40b": 40e9,
    r"mistral.*7b": 7e9,
    r"pythia.*1b": 1e9, r"pythia.*7b": 7e9, r"pythia.*12b": 12e9,
}
MIN_BENCHMARK_COVERAGE: int = 4
MIN_REGISTRY_SIZE: int = 200
MIN_FEATURES_WITH_VARIANCE: int = 3
API_BACKOFF_BASE: float = 2.0
API_MAX_RETRIES: int = 5
CHECKPOINT_INTERVAL: int = 100
RANDOM_STATE: int = 42
DATA_DIR: str = "h-e1/data"
FIGURES_DIR: str = "h-e1/figures"
CHECKPOINT_DIR: str = "h-e1/data/checkpoints"
```

### analysis.py

```python
def compute_descriptive_stats(registry_df: pd.DataFrame) -> dict:
    """Compute doc_score distribution, feature coverage, benchmark availability.
    Returns: stats dict with keys: doc_score_counts, feature_fractions, benchmark_availability."""

def fit_ols_baseline(registry_df: pd.DataFrame) -> object:
    """Fit: mmlu ~ log_params + log_tokens + C(arch_family).
    Returns: statsmodels RegressionResultsWrapper."""

def fit_ols_proposed(registry_df: pd.DataFrame) -> object:
    """Fit: mmlu ~ log_params + log_tokens + doc_score + C(arch_family).
    Returns: statsmodels RegressionResultsWrapper."""

def compare_models(
    baseline_result: object,
    proposed_result: object,
) -> dict:
    """Extract comparison metrics.
    Returns: {"baseline_r2": float, "proposed_r2": float, "delta_r2": float,
              "beta_docs": float, "p_value": float, "direction_check": bool}"""

def save_summary_stats(stats: dict, output_path: str) -> None:
    """Write stats dict to output_path as JSON (json.dump, indent=2)."""
```

### visualization.py

```python
def plot_doc_score_distribution(registry_df: pd.DataFrame, output_path: str) -> None:
    """Histogram of doc_score (0-4). Saves to output_path."""

def plot_dropout_funnel(funnel_counts: dict[str, int], output_path: str) -> None:
    """Waterfall/bar chart of funnel stages. funnel_counts: ordered stage->count dict."""

def plot_feature_coverage(registry_df: pd.DataFrame, output_path: str) -> None:
    """4-panel bar chart of fraction of models with each binary feature=1."""

def plot_family_breakdown(registry_df: pd.DataFrame, output_path: str) -> None:
    """Stacked bar: arch_family x doc_score distribution."""

def plot_benchmark_heatmap(registry_df: pd.DataFrame, output_path: str) -> None:
    """Heatmap: model x benchmark availability (binary non-null matrix)."""
```

### main.py

```python
def run_pipeline() -> dict:
    """Orchestrate full pipeline. Returns gate results dict.
    Steps:
      1. load_leaderboard -> deduplicate -> filter_benchmark_coverage
      2. retrieve_model_cards (with checkpointing)
      3. build_registry -> validate_registry (gate assert)
      4. export_registry
      5. compute_descriptive_stats + fit_ols_baseline + fit_ols_proposed + compare_models
      6. save_summary_stats
      7. generate all 5 figures
    Returns: {"gate_passed": bool, "n_analyzable": int, "n_features_with_variance": int}"""

def smoke_test() -> bool:
    """Check imports + HF API connectivity. Returns True if environment ready."""

if __name__ == "__main__":
    run_pipeline()
```

---

## Data Shapes

| Stage | Shape | Key Columns |
|-------|-------|-------------|
| Raw leaderboard | (~3000-5000, 7) | model_name, 6 benchmark cols |
| After deduplicate | (~N_unique, 7) | same |
| After benchmark filter | (~1000-2000, 7) | same, ≥4 non-null benchmarks |
| model_card_data | dict len ~400-1400 | {model_id: card_text, model_info} |
| registry_df | (≥200, 16) | model_id, 6 benchmarks, 4 features, doc_score, n_params, log_params, log_tokens, arch_family |
| summary_stats.json | flat dict | n_analyzable, feature_vars, OLS results |

---

## Subtask Summary [6/6 used]

| ID | Subtask | Epic | Description |
|----|---------|------|-------------|
| L-E3a-1 | retrieve_model_cards + backoff | E-3 | API + backoff pseudo-code |
| L-E3a-2 | Checkpoint/resume logic | E-3 | load skip, save interval |
| L-E2a-1 | load/deduplicate/filter | E-2 | Three leaderboard functions |
| L-E4a-1 | extract features + recover params | E-4 | Regex logic + priority chain |
| L-E4b-1 | token/arch/derived features | E-4 | Three helper function APIs |
| L-E5a-1 | build/validate/export registry | E-5 | Assembly pseudo-code + gate assert |

---

*Generated by Phase 3 Logic Agent*
*Hypothesis: H-E1 | Type: EXISTENCE | Infrastructure: LIGHT*
*Date: 2026-03-17*
