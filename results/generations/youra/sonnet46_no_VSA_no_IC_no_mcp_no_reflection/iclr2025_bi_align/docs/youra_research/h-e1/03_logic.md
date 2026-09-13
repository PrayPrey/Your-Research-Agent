# Logic Design: H-E1
# Behavioral Proxy Signal Detection — API Signatures & Pseudo-code

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Date:** 2026-08-31
**Budget:** 4 subtasks (E2 focus — highest complexity)

Applied: Standard data pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type:** Green-field
**Status:** Green-field project; no existing codebase to analyze.
**Findings:** New implementation from scratch using scipy/pandas/HuggingFace datasets.

---

## Data Shapes (DataFrames — no tensors)

| Variable | Columns | Dtypes |
|----------|---------|--------|
| `raw_wildchat` | hashed_ip, monthly_bin, prompt, turn_count, model | str, str(YYYY-MM), str, int, str |
| `cohort_df` | hashed_ip, monthly_bin, prompt_token_count, correction_freq, cohort_size | str, str, float, float, int |
| `token_series` | dict[str→float] | monthly_bin (sorted) → mean token count |
| `correction_series` | dict[str→float] | monthly_bin (sorted) → mean correction freq |
| `lmsys_raw` | monthly_bin, model_a, model_b, winner | str, str, str, str |
| `entropy_series` | dict[str→float] | monthly_bin (sorted) → mean Shannon entropy |

---

## Subtask L-E2-1: WildChat Dataset Loading API

**File:** `code/data_loader.py`

```python
from datasets import load_dataset
import pandas as pd
from typing import Optional

def load_wildchat(
    date_start: str = "2023-01",
    date_end: str = "2024-12",
    cache_dir: Optional[str] = None,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Load and filter WildChat-1M from HuggingFace.

    Args:
        date_start: Inclusive start month "YYYY-MM"
        date_end: Inclusive end month "YYYY-MM"
        cache_dir: HuggingFace cache directory (None = default ~/.cache)
        seed: Random seed (unused here; for bootstrap downstream)

    Returns:
        DataFrame[hashed_ip: str, monthly_bin: str, prompt: str,
                  turn_count: int, model: str]

    Raises:
        ValueError: If dataset fields are missing
        ConnectionError: If HuggingFace unavailable
    """
    ds = load_dataset("allenai/WildChat-1M", cache_dir=cache_dir, split="train")

    records = []
    for row in ds:
        # Extract timestamp → monthly_bin
        ts = row.get("timestamp") or row.get("header", {}).get("timestamp", "")
        if not ts:
            continue
        monthly_bin = str(ts)[:7]  # "YYYY-MM"
        if monthly_bin < date_start or monthly_bin > date_end:
            continue

        conversation = row.get("conversation", [])
        if not conversation:
            continue

        # First turn = prompt
        prompt = conversation[0].get("content", "") if conversation else ""
        turn_count = len(conversation)
        hashed_ip = row.get("hashed_ip", "")
        model = row.get("model", "")

        records.append({
            "hashed_ip": hashed_ip,
            "monthly_bin": monthly_bin,
            "prompt": prompt,
            "turn_count": turn_count,
            "model": model,
        })

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError(f"No WildChat records found for {date_start}–{date_end}")
    return df
```

**Pseudo-code summary:**
1. Load full HuggingFace dataset (streaming not required — filter in-memory)
2. Per row: parse timestamp → YYYY-MM; skip if outside range
3. Extract first conversation turn as prompt; count all turns
4. Return flat DataFrame

---

## Subtask L-E2-2: Cohort Construction Logic

**File:** `code/data_loader.py`

```python
def build_cohort(df: pd.DataFrame, min_bins: int = 3) -> pd.DataFrame:
    """
    Filter WildChat DataFrame to returning-user cohort.

    Args:
        df: Raw DataFrame from load_wildchat
        min_bins: Minimum distinct monthly bins per hashed_ip

    Returns:
        cohort_df with same columns + cohort_size: int

    Edge cases:
        - Empty df → raises ValueError
        - All IPs appear < min_bins → raises ValueError with count
        - Single-turn sessions → correction_freq = 0 (handled downstream)
    """
    if df.empty:
        raise ValueError("Input DataFrame is empty")

    # Count distinct monthly bins per IP-hash
    bin_counts = df.groupby("hashed_ip")["monthly_bin"].nunique().reset_index()
    bin_counts.columns = ["hashed_ip", "n_bins"]

    qualifying = bin_counts[bin_counts["n_bins"] >= min_bins]["hashed_ip"]

    if qualifying.empty:
        raise ValueError(
            f"No IP-hashes appear in ≥{min_bins} monthly bins. "
            f"Max bins seen: {bin_counts['n_bins'].max()}"
        )

    cohort = df[df["hashed_ip"].isin(qualifying)].copy()

    # Attach cohort_size (distinct bins per IP)
    cohort = cohort.merge(
        bin_counts.rename(columns={"n_bins": "cohort_size"}),
        on="hashed_ip", how="left"
    )
    return cohort
```

**Pseudo-code summary:**
1. Group by hashed_ip; count distinct monthly_bins
2. Filter to IPs with ≥ min_bins distinct bins
3. Merge cohort_size back onto filtered DataFrame
4. Raise informative error if no qualifying IPs

---

## Subtask L-E2-3: Prompt Token Count Computation

**File:** `code/proxy_computation.py`

```python
import numpy as np
import pandas as pd
from typing import Literal

def compute_prompt_token_count(
    prompt: str,
    method: Literal["approx", "tiktoken"] = "approx"
) -> float:
    """
    Estimate prompt token count.

    Args:
        prompt: Raw prompt string
        method: "approx" = len(words)*1.3; "tiktoken" = cl100k_base encoder

    Returns:
        Estimated token count as float
    """
    if method == "approx":
        return len(prompt.split()) * 1.3
    elif method == "tiktoken":
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return float(len(enc.encode(prompt)))
    else:
        raise ValueError(f"Unknown method: {method}")


def compute_token_series(
    cohort_df: pd.DataFrame,
    method: str = "approx"
) -> dict[str, float]:
    """
    Compute monthly mean prompt token count from cohort.

    Returns:
        Sorted dict {monthly_bin: mean_token_count}
    """
    cohort_df = cohort_df.copy()
    cohort_df["prompt_token_count"] = cohort_df["prompt"].apply(
        lambda p: compute_prompt_token_count(p, method=method)
    )
    monthly = (
        cohort_df.groupby("monthly_bin")["prompt_token_count"]
        .mean()
        .sort_index()
    )
    return monthly.to_dict()
```

---

## Subtask L-E2-4: Correction/Negation Frequency

**File:** `code/proxy_computation.py`

```python
CORRECTION_MARKERS = [
    "actually",
    "that's wrong",
    "no, i meant",
    "please redo",
    "that is incorrect",
    "you're wrong",
]

def compute_correction_freq(session_turns: list[str]) -> float:
    """
    Compute correction/negation frequency for a session.

    Args:
        session_turns: List of turn content strings (all turns, not just user)

    Returns:
        Fraction of turns containing ≥1 correction marker [0.0, 1.0]

    Edge cases:
        - Empty list → returns 0.0
        - Single-turn session → denominator = 1 (no division error)
    """
    if not session_turns:
        return 0.0
    n = len(session_turns)
    count = sum(
        1 for turn in session_turns
        if any(marker in turn.lower() for marker in CORRECTION_MARKERS)
    )
    return count / n


def compute_correction_series(cohort_df: pd.DataFrame) -> dict[str, float]:
    """
    Compute monthly mean correction frequency from WildChat cohort.

    Expects cohort_df to have: monthly_bin, prompt (first-turn text).
    Uses prompt as proxy for session correction (single-turn approximation).
    For full multi-turn: reconstruct all turns from conversation field.

    Returns:
        Sorted dict {monthly_bin: mean_correction_freq}
    """
    cohort_df = cohort_df.copy()
    # Single-turn approximation: treat prompt as the only user turn
    cohort_df["correction_freq"] = cohort_df["prompt"].apply(
        lambda p: compute_correction_freq([p])
    )
    monthly = (
        cohort_df.groupby("monthly_bin")["correction_freq"]
        .mean()
        .sort_index()
    )
    return monthly.to_dict()
```

---

## Statistical Analysis API

**File:** `code/statistical_analysis.py`

```python
import numpy as np
from scipy.stats import kendalltau

def run_mann_kendall(series: dict[str, float]) -> tuple[float, float]:
    """
    Run Mann-Kendall trend test on a monthly time series.

    Args:
        series: {monthly_bin: value} — must be sorted by key

    Returns:
        (tau, p_value) from scipy.stats.kendalltau
    """
    bins = sorted(series.keys())
    values = [series[b] for b in bins]
    time_idx = np.arange(len(values))
    tau, p_value = kendalltau(time_idx, values)
    return float(tau), float(p_value)


def evaluate_success(
    results: dict[str, tuple[float, float]],
    p_threshold: float = 0.05,
    effect_threshold: float = 0.2,
    min_passing: int = 2,
) -> dict:
    """
    Evaluate gate success condition.

    Returns:
        {
          proxy_name: {tau, p_value, abs_tau, pass},
          "overall_pass": bool,
          "n_passing": int,
          "effect_pass": bool  # ≥1 proxy |τ|>effect_threshold
        }
    """
    out = {}
    n_pass = 0
    effect_pass = False
    for proxy, (tau, p) in results.items():
        passed = p < p_threshold
        if passed:
            n_pass += 1
        if abs(tau) > effect_threshold:
            effect_pass = True
        out[proxy] = {"tau": tau, "p_value": p, "abs_tau": abs(tau), "pass": passed}
    out["overall_pass"] = n_pass >= min_passing
    out["n_passing"] = n_pass
    out["effect_pass"] = effect_pass
    return out
```
