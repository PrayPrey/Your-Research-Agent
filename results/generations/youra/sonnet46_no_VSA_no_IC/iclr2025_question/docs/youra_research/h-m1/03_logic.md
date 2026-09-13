# Logic Design: H-M1
# Token Distribution Peakedness Analysis for Hallucination Detection

**Hypothesis:** H-M1 (MECHANISM)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr

Applied: incremental-extension-pattern (extend H-E1 inference pipeline with peakedness analysis)
Applied: dual-path-data-loading (cache-first with fallback re-inference)
Applied: non-parametric-statistical-testing (Mann-Whitney U, distribution-agnostic)

---

## Codebase Analysis (Serena)

**Analysis method:** Direct file reads on actual H-E1 code (Serena project selection unavailable in this context; Read tool used on actual implementation files)
**Analyzed path:** `docs/youra_research/h-e1/code/`

### Verified Function Signatures from Actual H-E1 Code

**`inference.py`:**
```python
def load_model(model_key: str) -> Tuple[PreTrainedModel, PreTrainedTokenizer]
def extract_token_logprobs(model, tokenizer, prompt: str, max_new_tokens: int = 30) -> Tuple[List[float], str]
def run_inference(samples: List[Dict], model, tokenizer, max_new_tokens: int = 30) -> List[Dict]
```

**`run_inference()` return record keys (verified):**
- `logprobs`: List[float] — all ≤ 0.0 (log-softmax scores for each generated token)
- `label`: int — 0 or 1, set by score_answer()
- `question`: str
- `generated_text`: str
- `prompt`: str
- `reference_answers`: List[str]
- `dataset`: str

**`data_loader.py`:**
```python
def load_trivia_qa(farquhar_data_dir: Optional[str] = None) -> List[Dict]
def load_nq(farquhar_data_dir: Optional[str] = None) -> List[Dict]
def score_answer(generated: str, record: Dict, rouge_threshold: float = 0.3) -> int
def get_dataset(name: str, farquhar_data_dir: Optional[str] = None) -> List[Dict]
```

**`config.py` verified values:**
```python
MODELS = {"llama2": "meta-llama/Llama-2-7b-hf", "mistral": "mistralai/Mistral-7B-v0.1"}
SEED = 42
MAX_NEW_TOKENS = 30  # NOT 50 as in PRD spec
MAX_SAMPLES_PER_DATASET = {"trivia_qa": 2000, "nq": 2000, "truthful_qa": None}
FARQUHAR_DATA_DIR = "/home/PrayPrey/data/semantic_uncertainty"
```

**Critical finding:** H-E1 `run_inference()` already returns `record["logprobs"]` and `record["label"]` — H-M1 can consume these records directly without adaptation.

**H-E1 results directory:** `h-e1/results/scores_llama2_trivia_qa.npz`, `scores_llama2_truthful_qa.npz` — these store aggregation scores (min/mean/sum + labels), NOT raw records with logprobs. H-M1 must re-run inference or find raw record cache.

---

## External Dependencies API

### From `h-e1/code/inference.py`

```python
# Import pattern (verified):
import sys
sys.path.insert(0, H_E1_CODE_DIR)  # e.g. "docs/youra_research/h-e1/code"
from inference import load_model, run_inference, extract_token_logprobs
from data_loader import get_dataset
from config import MODELS, MAX_NEW_TOKENS, SEED, MAX_SAMPLES_PER_DATASET, FARQUHAR_DATA_DIR

# load_model: loads frozen fp16 model + tokenizer
model, tokenizer = load_model("llama2")
# Returns: (PreTrainedModel in eval mode, PreTrainedTokenizer)

# run_inference: full dataset inference
records = run_inference(samples, model, tokenizer, max_new_tokens=30)
# Returns: List[Dict] each with keys: logprobs, label, question, generated_text, prompt

# get_dataset: dispatcher for dataset loading
samples = get_dataset("trivia_qa", farquhar_data_dir=FARQUHAR_DATA_DIR)
# Returns: List[Dict] with keys: question, label (None), reference_answers, dataset
```

---

## Subtask L-4-1: `load_or_run_inference()` — Dual-Path Data Loading

### Purpose
Load per-token logprob records for a (dataset, model) pair. Prefers cached H-E1 raw records; falls back to re-running inference.

### API

```python
def load_or_run_inference(
    dataset_name: str,          # "trivia_qa" or "nq"
    model_key: str,             # "llama2" or "mistral"
    h_e1_results_dir: str,      # path to h-e1/results/
    h_e1_code_dir: str,         # path to h-e1/code/
    results_dir: str,           # path to h-m1/results/ (for caching)
    max_samples: Optional[int] = 2000,
    seed: int = 42,
) -> List[Dict]:
    """
    Returns list of dicts, each guaranteed to have:
      - logprobs: List[float]  (all <= 0.0, length >= 1)
      - label: int             (0=hallucinated, 1=correct)

    Path A: Load from h-m1/results/{model}_{dataset}_records.npz if exists
    Path B: Load from h-e1/results/{model}_{dataset}_records.npz if exists and has logprobs
    Path C: Re-run inference via H-E1 pipeline, cache to h-m1/results/
    """
```

### Pseudo-code

```python
def load_or_run_inference(dataset_name, model_key, h_e1_results_dir, h_e1_code_dir,
                          results_dir, max_samples=2000, seed=42):
    # Path A: check h-m1 own cache
    cache_path = f"{results_dir}/{model_key}_{dataset_name}_records.npz"
    if os.path.exists(cache_path):
        data = np.load(cache_path, allow_pickle=True)
        if "records" in data:
            return data["records"].tolist()

    # Path B: check h-e1 results for raw records
    h_e1_cache = f"{h_e1_results_dir}/{model_key}_{dataset_name}_records.npz"
    if os.path.exists(h_e1_cache):
        data = np.load(h_e1_cache, allow_pickle=True)
        if "records" in data and "logprobs" in data["records"][0]:
            records = data["records"].tolist()
            # save to h-m1 cache and return
            os.makedirs(results_dir, exist_ok=True)
            np.savez(cache_path, records=np.array(records, dtype=object))
            return records

    # Path C: re-run inference via H-E1 pipeline
    sys.path.insert(0, h_e1_code_dir)
    from inference import load_model, run_inference
    from data_loader import get_dataset
    from config import FARQUHAR_DATA_DIR

    samples = get_dataset(dataset_name, farquhar_data_dir=FARQUHAR_DATA_DIR)
    if max_samples and len(samples) > max_samples:
        random.seed(seed)
        samples = random.sample(samples, max_samples)

    model, tokenizer = load_model(model_key)
    records = run_inference(samples, model, tokenizer)

    # Cache raw records for reuse
    os.makedirs(results_dir, exist_ok=True)
    np.savez(cache_path, records=np.array(records, dtype=object))
    return records
```

### Return type invariant
Every record in returned list MUST have `logprobs: List[float]` (non-empty, all ≤ 0.0) and `label: int`. Records with empty logprobs are already filtered by H-E1 `run_inference()`.

---

## Subtask L-4-2: H-E1 Data Loader Actual API (Verified)

### `load_trivia_qa(farquhar_data_dir=None) -> List[Dict]`
- Loads from HuggingFace `trivia_qa` `rc.nocontext` split, `validation` set
- Returns records with `label=None` (assigned later by `score_answer()`)
- `reference_answers`: list of gold answer strings (aliases + normalized_value)

### `load_nq(farquhar_data_dir=None) -> List[Dict]`
- Loads from HuggingFace `nq_open`, `validation` split
- Returns records with `label=None`
- `reference_answers`: list of gold answer strings

### `score_answer(generated: str, record: Dict, rouge_threshold: float = 0.3) -> int`
- TriviaQA/NQ: exact-match after normalization (lowercase, strip punctuation/articles) → 0 or 1
- TruthfulQA: ROUGE-L ≥ 0.3 → 1 (NOT used in H-M1)
- Returns `int` — already applied inside `run_inference()`, so H-M1 records already have `label` set

### `get_dataset(name: str, farquhar_data_dir=None) -> List[Dict]`
- Dispatcher: `"trivia_qa"` → `load_trivia_qa()`, `"nq"` → `load_nq()`
- Valid names: `"trivia_qa"`, `"nq"`, `"truthful_qa"` (H-M1 does NOT use truthful_qa)

---

## Subtask L-7-1: `run_dataset()` — Per-(Dataset, Model) Orchestration

### API

```python
def run_dataset(
    dataset_name: str,   # "trivia_qa" or "nq"
    model_key: str,      # "llama2" or "mistral"
    config: H_M1Config,  # config dataclass with all paths + thresholds
) -> Dict:
    """
    Full peakedness analysis for one (dataset, model) pair.

    Returns:
        {
            "dataset": str,
            "model": str,
            "stats": {
                "statistic": float,
                "p_value": float,
                "direction": str,       # "hallucinated_higher" or "correct_higher"
                "mean_hallucinated": float,
                "mean_correct": float,
                "n_hallucinated": int,
                "n_correct": int,
            },
            "hallucinated": List[float],   # peakedness scores for hallucinated group
            "correct": List[float],        # peakedness scores for correct group
            "n_samples": int,              # total records processed
        }
    """
```

### Pseudo-code

```python
def run_dataset(dataset_name, model_key, config):
    # Step 1: load or run inference (returns records with logprobs + label)
    records = load_or_run_inference(
        dataset_name, model_key,
        config.H_E1_RESULTS_DIR, config.H_E1_CODE_DIR,
        config.RESULTS_DIR, config.MAX_SAMPLES[dataset_name], config.SEED
    )

    # Step 2: compute peakedness per record, split by label
    from peakedness import analyze_group_peakedness
    groups = analyze_group_peakedness(records)
    # groups = {"hallucinated": [float, ...], "correct": [float, ...]}

    # Step 3: statistical test
    from peakedness import test_peakedness_difference
    stats = test_peakedness_difference(groups["hallucinated"], groups["correct"])

    # Step 4: cache peakedness arrays to .npz
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    np.savez(
        f"{config.RESULTS_DIR}/peakedness_{model_key}_{dataset_name}.npz",
        hallucinated=np.array(groups["hallucinated"]),
        correct=np.array(groups["correct"]),
        labels=np.array([r["label"] for r in records]),
    )

    return {
        "dataset": dataset_name,
        "model": model_key,
        "stats": stats,
        "hallucinated": groups["hallucinated"],
        "correct": groups["correct"],
        "n_samples": len(records),
    }
```

---

## Subtask L-7-2: `main()` — Outer Loop Design

### Pseudo-code

```python
def main():
    config = load_config()  # H_M1Config dataclass
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    all_results = {}

    for model_key in config.MODELS_TO_RUN:
        for dataset_name in config.DATASETS:  # ["trivia_qa", "nq"]
            key = f"{model_key}_{dataset_name}"
            print(f"\n--- Running {key} ---")

            if model_key == "mistral":
                try:
                    result = run_dataset(dataset_name, model_key, config)
                except Exception as e:
                    print(f"  Mistral failed: {e} — skipping")
                    continue
            else:
                result = run_dataset(dataset_name, model_key, config)

            all_results[key] = result
            p = result["stats"]["p_value"]
            direction = result["stats"]["direction"]
            print(f"  p={p:.4f}, direction={direction}")

    # Save summary JSON
    summary = {
        k: {
            "p_value": v["stats"]["p_value"],
            "direction": v["stats"]["direction"],
            "mean_hallucinated": v["stats"]["mean_hallucinated"],
            "mean_correct": v["stats"]["mean_correct"],
            "n_hallucinated": v["stats"]["n_hallucinated"],
            "n_correct": v["stats"]["n_correct"],
        }
        for k, v in all_results.items()
    }
    with open(f"{config.RESULTS_DIR}/results_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Gate check
    gate_pass = any(
        v["stats"]["p_value"] < config.P_VALUE_THRESHOLD
        for v in all_results.values()
    )

    # Generate all 4 figures
    from visualization import save_all_figures
    save_all_figures(all_results, config.FIGURES_DIR)

    # Print gate result
    print("\n" + "="*60)
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    for k, v in summary.items():
        sig = "✓ p<0.05" if v["p_value"] < config.P_VALUE_THRESHOLD else "✗ p≥0.05"
        print(f"  {k}: {sig}, p={v['p_value']:.4f}, direction={v['direction']}")
    print("="*60)

if __name__ == "__main__":
    main()
```

---

## Core Algorithm: Peakedness Module

### `compute_peakedness(token_logprobs: List[float]) -> float`

```python
def compute_peakedness(token_logprobs: List[float]) -> float:
    abs_lp = np.abs(token_logprobs)   # convert neg logprobs → positive magnitudes
    if len(abs_lp) == 0 or np.mean(abs_lp) == 0:
        return 1.0                    # degenerate: uniform or empty
    return float(np.max(abs_lp) / np.mean(abs_lp))
```

**Invariant:** Returns ≥ 1.0 always (max ≥ mean for non-negative values). Single-token answers return 1.0 (max = mean).

### `test_peakedness_difference` return schema

```python
{
    "statistic": float,            # Mann-Whitney U statistic
    "p_value": float,              # two-sided p-value
    "direction": str,              # "hallucinated_higher" | "correct_higher"
    "mean_hallucinated": float,    # mean peakedness of hallucinated group
    "mean_correct": float,         # mean peakedness of correct group
    "n_hallucinated": int,         # count of hallucinated samples
    "n_correct": int,              # count of correct samples
}
```

---

## Tensor / Data Shapes

| Variable | Shape | Dtype | Notes |
|----------|-------|-------|-------|
| `token_logprobs` | `(T,)` | `List[float]` | T = generated tokens, all ≤ 0.0 |
| `peakedness` (per sample) | scalar | float | ≥ 1.0 |
| `groups["hallucinated"]` | `(N_h,)` | `List[float]` | N_h = hallucinated sample count |
| `groups["correct"]` | `(N_c,)` | `List[float]` | N_c = correct sample count |
| `.npz` `hallucinated` array | `(N_h,)` | float64 | cached peakedness scores |
| `.npz` `correct` array | `(N_c,)` | float64 | cached peakedness scores |
| `.npz` `labels` array | `(N,)` | int | 0/1 labels for all records |
