# Logic Design: H-E1
# LLM Trustworthiness Benchmark Data Availability Audit

**Hypothesis:** H-E1 (EXISTENCE / LIGHT tier)
**Date:** 2026-08-20
**Author:** Anonymous
**Budget:** 7 subtasks (E-2: 4, E-3: 2, E-4: 1)

Applied: Standard Python module API pattern — no Archon KB match found for NLP evaluation domain (top similarity 0.43, CV/diffusion content only).

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project — Serena not applicable. No existing codebase to analyze.
**Findings**: All APIs designed from scratch per PRD and architecture specifications.

---

## Subtasks

### E-2: Data Ingestion (4 subtasks)

#### L-2-1: `load_trustllm` — TrustLLM JSON Parser

**File:** `code/ingest.py`

**Signature:**
```python
def load_trustllm(results_dir: str | Path) -> dict[str, dict[str, float]]:
    """
    Parse TrustLLM results JSONs for BBQ (disambig/ambig) and ANLI (R1/R3) scores.

    Args:
        results_dir: Path to cloned HowieHwong/TrustLLM root directory.

    Returns:
        {canonical_model_name: {"BBQ-Disambig": float, "BBQ-Ambig": float,
                                 "ANLI-R1": float, "ANLI-R3": float}}
        Missing benchmarks for a model are absent from inner dict (not NaN).
    """
```

**Algorithm:**
```python
def load_trustllm(results_dir):
    results_dir = Path(results_dir)
    scores = {}  # {canonical_model: {benchmark: float}}

    # --- BBQ scores ---
    # TrustLLM stores per-example results; each JSON file may contain
    # results for one or more models with context_condition field.
    for json_file in results_dir.glob("**/Fairness/**/*.json"):
        data = json.load(open(json_file))
        # data is list of records: [{model, context_condition, acc, ...}, ...]
        # OR dict: {model_name: {context_condition: {metric: value}}}
        # Handle both formats:
        if isinstance(data, list):
            for record in data:
                model = standardize_model_name(record.get("model", ""))
                cond = record.get("context_condition", "")
                acc = record.get("accuracy", record.get("acc"))
                if acc is None or not model:
                    continue
                scores.setdefault(model, {})
                if cond == "disambig":
                    scores[model]["BBQ-Disambig"] = float(acc)
                elif cond == "ambig":
                    scores[model]["BBQ-Ambig"] = float(acc)
        elif isinstance(data, dict):
            # Nested format: {model: {disambig: acc, ambig: acc}}
            for raw_model, cond_dict in data.items():
                model = standardize_model_name(raw_model)
                scores.setdefault(model, {})
                if "disambig" in cond_dict:
                    scores[model]["BBQ-Disambig"] = float(cond_dict["disambig"])
                if "ambig" in cond_dict:
                    scores[model]["BBQ-Ambig"] = float(cond_dict["ambig"])

    # --- ANLI scores ---
    for json_file in results_dir.glob("**/Robustness/**/*.json"):
        data = json.load(open(json_file))
        if isinstance(data, list):
            for record in data:
                model = standardize_model_name(record.get("model", ""))
                task = record.get("task", record.get("dataset", ""))
                acc = record.get("accuracy", record.get("acc"))
                if acc is None or not model:
                    continue
                scores.setdefault(model, {})
                if "anli" in task.lower() and "r1" in task.lower():
                    scores[model]["ANLI-R1"] = float(acc)
                elif "anli" in task.lower() and "r3" in task.lower():
                    scores[model]["ANLI-R3"] = float(acc)
        elif isinstance(data, dict):
            for raw_model, task_dict in data.items():
                model = standardize_model_name(raw_model)
                scores.setdefault(model, {})
                for task_key, acc in task_dict.items():
                    if "anli" in task_key.lower() and "r1" in task_key.lower():
                        scores[model]["ANLI-R1"] = float(acc)
                    elif "anli" in task_key.lower() and "r3" in task_key.lower():
                        scores[model]["ANLI-R3"] = float(acc)

    return scores
```

---

#### L-2-2: `load_glue_x` — GLUE-X Table Extractor

**File:** `code/ingest.py`

**Signature:**
```python
def load_glue_x(data_path: str | Path) -> dict[str, dict[str, float]]:
    """
    Extract GLUE (ID) and AdvGLUE (OOD) average scores per model from GLUE-X data.

    Args:
        data_path: Path to CSV file (from Google Drive) OR path to GLUE-X paper PDF.
                   If CSV: expects columns [model, glue_avg, advglue_avg] or similar.
                   If PDF: attempts regex-based table extraction.

    Returns:
        {canonical_model_name: {"GLUE": float, "AdvGLUE": float}}

    WARNING: GLUE-X evaluates PLMs (ELECTRA, RoBERTa, T5, BERT, XLNet, BART, GPT-2),
    NOT decoder-only LLMs. Model overlap with TrustLLM set is expected to be minimal.
    """
```

**Algorithm:**
```python
def load_glue_x(data_path):
    data_path = Path(data_path)
    scores = {}

    if data_path.suffix == ".csv":
        df = pd.read_csv(data_path)
        # Normalize column names
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
        # Expected columns: model, glue_avg (or id_avg), advglue_avg (or ood_avg)
        model_col = next((c for c in df.columns if "model" in c), df.columns[0])
        glue_col = next((c for c in df.columns if "glue" in c and "adv" not in c), None)
        advglue_col = next((c for c in df.columns if "adv" in c or "ood" in c), None)
        for _, row in df.iterrows():
            model = standardize_model_name(str(row[model_col]))
            entry = {}
            if glue_col and pd.notna(row.get(glue_col)):
                # Convert percentage to fraction if > 1
                val = float(row[glue_col])
                entry["GLUE"] = val / 100.0 if val > 1.0 else val
            if advglue_col and pd.notna(row.get(advglue_col)):
                val = float(row[advglue_col])
                entry["AdvGLUE"] = val / 100.0 if val > 1.0 else val
            if entry:
                scores[model] = entry
    elif data_path.suffix == ".pdf":
        # Fallback: regex extraction from paper text (Table 3)
        import pdfplumber
        with pdfplumber.open(data_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                # Match lines like: "ELECTRA-large  89.18  74.62"
                for match in re.finditer(
                    r"([A-Za-z0-9\-\.]+(?:\-large|\-base|\-small)?)\s+"
                    r"(\d{1,2}\.\d{1,2})\s+(\d{1,2}\.\d{1,2})",
                    text
                ):
                    model = standardize_model_name(match.group(1))
                    glue_val = float(match.group(2)) / 100.0
                    adv_val = float(match.group(3)) / 100.0
                    scores[model] = {"GLUE": glue_val, "AdvGLUE": adv_val}
    else:
        raise ValueError(f"Unsupported data_path format: {data_path.suffix}. Expected .csv or .pdf")

    return scores
```

---

#### L-2-3: `load_hf_leaderboard` — HuggingFace Parquet Loader

**File:** `code/ingest.py`

**Signature:**
```python
def load_hf_leaderboard(
    parquet_url: str = "hf://datasets/OpenEvals/leaderboard-data/data/train-00000-of-00001.parquet",
    mmlu_col: str | None = None,
) -> dict[str, dict[str, float]]:
    """
    Load MMLU scores from HuggingFace leaderboard parquet.

    Args:
        parquet_url: HF dataset parquet URL.
        mmlu_col: Column name for MMLU scores. Auto-detected if None.

    Returns:
        {canonical_model_name: {"MMLU": float}}

    Note: Current leaderboard uses MMLU-PRO (10-choice). Historical MMLU (4-choice, 5-shot)
    available in individual model result JSONs. This loader handles both.
    """
```

**Algorithm:**
```python
def load_hf_leaderboard(parquet_url=..., mmlu_col=None):
    import pandas as pd
    scores = {}
    try:
        df = pd.read_parquet(parquet_url)
    except Exception as e:
        logging.warning(f"HF parquet load failed: {e}. Returning empty dict.")
        return scores

    # Auto-detect MMLU column
    if mmlu_col is None:
        candidates = [c for c in df.columns if "mmlu" in c.lower()]
        # Prefer original MMLU over MMLU-PRO
        original = [c for c in candidates if "pro" not in c.lower()]
        mmlu_col = original[0] if original else (candidates[0] if candidates else None)
    if mmlu_col is None:
        logging.warning("No MMLU column found in HF leaderboard parquet.")
        return scores

    model_col = next((c for c in df.columns if "model" in c.lower()), df.columns[0])
    for _, row in df.iterrows():
        if pd.isna(row.get(mmlu_col)):
            continue
        model = standardize_model_name(str(row[model_col]))
        val = float(row[mmlu_col])
        scores[model] = {"MMLU": val / 100.0 if val > 1.0 else val}

    return scores
```

---

#### L-2-4: Supplemental Loaders (`load_ood_nlp`, `load_decoding_trust`)

**File:** `code/ingest.py`

**Signatures:**
```python
def load_ood_nlp(results_dir: str | Path) -> dict[str, dict[str, float]]:
    """
    Load ANLI-R1, ANLI-R3 supplement from lifan-yuan/OOD_NLP repository.

    Args:
        results_dir: Path to cloned OOD_NLP repo results directory.

    Returns:
        {canonical_model_name: {"ANLI-R1": float, "ANLI-R3": float}}
    """

def load_decoding_trust(results_dir: str | Path) -> dict[str, dict[str, float]]:
    """
    Load AdvGLUE++ and fairness scores from AI-secure/DecodingTrust.
    Covers GPT-3.5-Turbo, GPT-4.

    Args:
        results_dir: Path to cloned DecodingTrust repo results directory.

    Returns:
        {canonical_model_name: {"AdvGLUE": float, "BBQ-Disambig": float, "BBQ-Ambig": float}}
    """
```

**Algorithm (shared pattern):**
```python
def load_ood_nlp(results_dir):
    results_dir = Path(results_dir)
    scores = {}
    # OOD_NLP stores results per dataset in JSON/CSV files
    for f in results_dir.glob("**/*anli*.{json,csv}"):
        try:
            if f.suffix == ".json":
                data = json.load(open(f))
            else:
                data = pd.read_csv(f).to_dict("records")
            for record in (data if isinstance(data, list) else [data]):
                model = standardize_model_name(record.get("model", ""))
                for key in record:
                    if "anli" in key.lower() and "r1" in key.lower():
                        scores.setdefault(model, {})["ANLI-R1"] = float(record[key])
                    elif "anli" in key.lower() and "r3" in key.lower():
                        scores.setdefault(model, {})["ANLI-R3"] = float(record[key])
        except Exception as e:
            logging.warning(f"Failed to parse {f}: {e}")
    return scores

# load_decoding_trust follows same pattern scanning for advglue/fairness result files
```

---

### E-3: Name Standardization + Matrix (2 subtasks)

#### L-3-1: `standardize_model_name`

**File:** `code/matrix.py`

**Signature:**
```python
def standardize_model_name(raw_name: str) -> str:
    """
    Map raw model name variant to canonical ID using CANONICAL_MAP.

    Args:
        raw_name: Any model name string from any source.

    Returns:
        Canonical model ID string. Returns raw_name (stripped) if no mapping found.
        Logs a WARNING for unmapped names (for manual review).
    """
```

**Algorithm:**
```python
_UNMAPPED: set[str] = set()  # module-level cache for warning dedup

def standardize_model_name(raw_name: str) -> str:
    key = raw_name.lower().strip()
    result = CANONICAL_MAP.get(key)
    if result is None:
        if key not in _UNMAPPED:
            logging.warning(f"Unmapped model name: '{raw_name}' — add to CANONICAL_MAP if needed")
            _UNMAPPED.add(key)
        return raw_name.strip()
    return result
```

**CANONICAL_MAP entries** (full set for TrustLLM models):
```python
CANONICAL_MAP = {
    # LLaMA-2 base
    "llama-2-7b": "LLaMA-2-7B",
    "llama2-7b": "LLaMA-2-7B",
    "meta-llama/llama-2-7b-hf": "LLaMA-2-7B",
    "llama-2-13b": "LLaMA-2-13B",
    "llama2-13b": "LLaMA-2-13B",
    "meta-llama/llama-2-13b-hf": "LLaMA-2-13B",
    "llama-2-70b": "LLaMA-2-70B",
    "meta-llama/llama-2-70b-hf": "LLaMA-2-70B",
    # LLaMA-2 chat
    "llama-2-7b-chat": "LLaMA-2-7B-Chat",
    "llama2-7b-chat-hf": "LLaMA-2-7B-Chat",
    "meta-llama/llama-2-7b-chat-hf": "LLaMA-2-7B-Chat",
    "llama-2-13b-chat": "LLaMA-2-13B-Chat",
    "meta-llama/llama-2-13b-chat-hf": "LLaMA-2-13B-Chat",
    "llama-2-70b-chat": "LLaMA-2-70B-Chat",
    "meta-llama/llama-2-70b-chat-hf": "LLaMA-2-70B-Chat",
    # Mistral
    "mistral-7b": "Mistral-7B",
    "mistral-7b-v0.1": "Mistral-7B",
    "mistralai/mistral-7b-v0.1": "Mistral-7B",
    "mistral-7b-instruct": "Mistral-7B-Instruct",
    "mistral-7b-instruct-v0.1": "Mistral-7B-Instruct",
    "mistralai/mistral-7b-instruct-v0.1": "Mistral-7B-Instruct",
    # Falcon
    "falcon-7b": "Falcon-7B",
    "tiiuae/falcon-7b": "Falcon-7B",
    "falcon-40b": "Falcon-40B",
    "tiiuae/falcon-40b": "Falcon-40B",
    # GPT
    "gpt-3.5-turbo": "GPT-3.5-Turbo",
    "gpt-3.5-turbo-0301": "GPT-3.5-Turbo",
    "gpt-4": "GPT-4",
    "gpt-4-0314": "GPT-4",
    # Vicuna / Alpaca
    "vicuna-13b": "Vicuna-13B",
    "vicuna-13b-v1.1": "Vicuna-13B",
    "lmsys/vicuna-13b-v1.1": "Vicuna-13B",
    "alpaca-13b": "Alpaca-13B",
    # GLUE-X PLMs (for completeness; overlap expected minimal)
    "electra-large": "ELECTRA-large",
    "roberta-large": "RoBERTa-large",
    "t5-large": "T5-large",
    "t5-base": "T5-base",
    "bart-large": "BART-large",
    "xlnet-large": "XLNet-large",
    "bert-large": "BERT-large",
    "bert-base": "BERT-base",
    "distilbert": "DistilBERT",
    "albert": "ALBERT",
    "gpt2": "GPT-2",
    "gpt2-medium": "GPT-2-medium",
    "gpt2-large": "GPT-2-large",
    "gpt2-xl": "GPT-2-XL",
}
```

---

#### L-3-2: `build_matrix`

**File:** `code/matrix.py`

**Signature:**
```python
def build_matrix(
    score_dicts: dict[str, dict[str, dict[str, float]]]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build model × benchmark score matrix from multi-source score dicts.

    Args:
        score_dicts: {source_name: {canonical_model: {benchmark: float}}}
                     Source names must match SOURCE_PRIORITY order.

    Returns:
        matrix_df: pd.DataFrame with index=model_names, columns=REQUIRED_COLS.
                   NaN for missing cells.
        attribution_df: pd.DataFrame same shape; values = source name that filled cell,
                        or None for missing.
    """
```

**Algorithm:**
```python
def build_matrix(score_dicts):
    # Collect all model names across all sources
    all_models = set()
    for src_data in score_dicts.values():
        all_models.update(src_data.keys())
    all_models = sorted(all_models)

    matrix_rows = []
    attribution_rows = []

    for model in all_models:
        row = {}
        attr_row = {}
        for col in REQUIRED_COLS:
            filled = False
            for src in SOURCE_PRIORITY:
                if src not in score_dicts:
                    continue
                val = score_dicts[src].get(model, {}).get(col)
                if val is not None:
                    row[col] = float(val)
                    attr_row[col] = src
                    filled = True
                    break
            if not filled:
                row[col] = float("nan")
                attr_row[col] = None
        matrix_rows.append({"model": model, **row})
        attribution_rows.append({"model": model, **attr_row})

    matrix_df = pd.DataFrame(matrix_rows).set_index("model")
    attribution_df = pd.DataFrame(attribution_rows).set_index("model")
    return matrix_df, attribution_df
```

---

### E-4: H-E1 Audit (1 subtask)

#### L-4-1: `run_h_e1_audit` + `check_protocol_consistency`

**File:** `code/audit.py`

**Signatures:**
```python
def check_protocol_consistency(
    score_dicts: dict[str, dict[str, dict[str, float]]],
    threshold_pp: float = 5.0,
) -> tuple[list[dict], float]:
    """
    Find model-benchmark pairs scored by multiple sources; flag if |delta| > threshold_pp.

    Returns:
        warnings: list of {model, benchmark, source_a, val_a, source_b, val_b, delta_pp}
        consistency_fraction: float — fraction of cross-source pairs within threshold
    """

def run_h_e1_audit(
    matrix: pd.DataFrame,
    attribution: pd.DataFrame,
    score_dicts: dict[str, dict[str, dict[str, float]]],
) -> dict:
    """
    Run H-E1 gate audit.

    Returns:
        {
            "N_common": int,           # models with all 7 cols non-NaN
            "pair_counts": {           # models with both cols non-NaN per pair
                "BBQ-Disambig/BBQ-Ambig": int,
                "GLUE/AdvGLUE": int,
                "ANLI-R1/ANLI-R3": int,
            },
            "complete_matrix": pd.DataFrame,   # rows where all 7 cols present
            "gate_passed": bool,       # N_common >= N_COMMON_GATE (10)
            "protocol_warnings": list[dict],
            "protocol_consistency": float,     # fraction of cross-source pairs within 5pp
            "mmlu_coverage": float,    # fraction of intersection models with MMLU
        }
    """
```

**Algorithm:**
```python
def check_protocol_consistency(score_dicts, threshold_pp=5.0):
    warnings = []
    total_pairs = 0
    within_threshold = 0
    sources = list(score_dicts.keys())

    for i, src_a in enumerate(sources):
        for src_b in sources[i+1:]:
            # Find models present in both sources
            models_a = set(score_dicts[src_a].keys())
            models_b = set(score_dicts[src_b].keys())
            shared_models = models_a & models_b
            for model in shared_models:
                benchmarks_a = set(score_dicts[src_a][model].keys())
                benchmarks_b = set(score_dicts[src_b][model].keys())
                shared_benchmarks = benchmarks_a & benchmarks_b
                for bench in shared_benchmarks:
                    val_a = score_dicts[src_a][model][bench]
                    val_b = score_dicts[src_b][model][bench]
                    # Normalize to same scale (assume 0-1 or 0-100)
                    if abs(val_a - val_b) > 50:  # likely scale mismatch
                        val_b = val_b / 100.0 if val_b > 1 else val_b * 100.0
                    delta = abs(val_a - val_b) * 100  # convert to pp
                    total_pairs += 1
                    if delta > threshold_pp:
                        warnings.append({
                            "model": model, "benchmark": bench,
                            "source_a": src_a, "val_a": val_a,
                            "source_b": src_b, "val_b": val_b,
                            "delta_pp": round(delta, 2),
                        })
                    else:
                        within_threshold += 1

    consistency_fraction = (within_threshold / total_pairs) if total_pairs > 0 else 1.0
    return warnings, consistency_fraction


def run_h_e1_audit(matrix, attribution, score_dicts):
    # N_common: rows with all 7 columns non-NaN
    complete_matrix = matrix.dropna()
    n_common = len(complete_matrix)

    # Per-pair counts
    pair_counts = {}
    for col_a, col_b in BENCHMARK_PAIRS:
        pair_key = f"{col_a}/{col_b}"
        n_pair = matrix[[col_a, col_b]].dropna().shape[0]
        pair_counts[pair_key] = n_pair

    # Protocol consistency
    protocol_warnings, consistency_fraction = check_protocol_consistency(score_dicts)

    # MMLU coverage among intersection models
    intersection_models = set(matrix.index)
    models_with_mmlu = matrix["MMLU"].notna().sum()
    mmlu_coverage = models_with_mmlu / len(matrix) if len(matrix) > 0 else 0.0

    gate_passed = n_common >= N_COMMON_GATE
    print(f"N_common = {n_common} → {'PASS' if gate_passed else 'FAIL'}")

    return {
        "N_common": n_common,
        "pair_counts": pair_counts,
        "complete_matrix": complete_matrix,
        "gate_passed": gate_passed,
        "protocol_warnings": protocol_warnings,
        "protocol_consistency": round(consistency_fraction, 3),
        "mmlu_coverage": round(float(mmlu_coverage), 3),
    }
```

---

## Data Shapes

| Object | Type | Shape / Structure |
|--------|------|-------------------|
| `score_dicts` | `dict[str, dict[str, dict[str, float]]]` | `{source: {model: {benchmark: score}}}` |
| `matrix_df` | `pd.DataFrame` | `(N_models, 7)` — float, NaN for missing |
| `attribution_df` | `pd.DataFrame` | `(N_models, 7)` — str or None |
| `complete_matrix` | `pd.DataFrame` | `(N_common, 7)` — no NaN rows |
| `pair_counts` | `dict[str, int]` | 3 entries, one per benchmark pair |
| audit result | `dict` | keys: N_common, pair_counts, gate_passed, … |

Expected N_models ≈ 30–40 (union across all sources). Expected N_common ≈ 10–16 (TrustLLM set, if GLUE/AdvGLUE gap forces restriction: likely 0).

---

## Self-Check

```python
# Minimal self-check — run with: python -m code.audit
if __name__ == "__main__":
    import numpy as np
    # Synthetic matrix: 12 models, all 7 cols present
    models = [f"Model-{i}" for i in range(12)]
    data = {col: np.random.uniform(0.4, 0.9, 12) for col in REQUIRED_COLS}
    df = pd.DataFrame(data, index=models)
    attr = pd.DataFrame({col: ["TrustLLM"] * 12 for col in REQUIRED_COLS}, index=models)
    result = run_h_e1_audit(df, attr, {})
    assert result["N_common"] == 12, f"Expected 12, got {result['N_common']}"
    assert result["gate_passed"] is True
    print("Self-check passed.")
```
