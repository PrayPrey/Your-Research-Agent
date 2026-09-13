---
title: "Logic: h-e1-v2 Behavioral Proxy Trend Detection"
hypothesis_id: h-e1-v2
type: EXISTENCE
tier: LIGHT
date: "2026-08-31"
author: "Anonymous"
---

Applied: streaming aggregation pattern
Applied: strategy pattern (Mann-Kendall variant selection at runtime)
Applied: bootstrap resampling for CI estimation
Applied: pipeline composition (load → filter → compute → test → serialize → visualize)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior code to inspect for API compatibility.

---

## Full API Signatures

### `data_loader.py`

```python
from typing import Iterable
import pandas as pd

def load_wildchat(split: str = "train") -> Iterable[dict]:
    """
    Returns a streaming iterator of raw WildChat-1M records.
    Fields used: hashed_ip (str), timestamp (str ISO), conversation (list[dict]), toxic (bool).
    Uses streaming=True for memory efficiency.
    """

def load_lmsys() -> pd.DataFrame:
    """
    Loads LMSYS Arena preference data.
    Primary:  lmsys/chatbot_arena_conversations
    Fallback: lmsys/lmsys-arena-human-preference-55k
    Normalizes winner: "tie (bothbad)" -> "tie"
    Converts tstamp (Unix float) -> month str "YYYY-MM"
    Returns: DataFrame[model_a: str, model_b: str, winner: str, month: str]
    """
```

### `cohort_builder.py`

```python
from typing import Iterable
import pandas as pd

def build_wildchat_monthly(
    stream: Iterable[dict],
    date_start: str = "2023-01",
    date_end: str = "2024-12",
    min_bins: int = 3,
    min_cohort_size: int = 50,
    n_workers: int = 4,
) -> tuple[pd.DataFrame, dict]:
    """
    Single streaming pass over WildChat-1M.
    Returns:
      - monthly: DataFrame[month: str, prompt_tokens_mean: float,
                           correction_freq_mean: float, cohort_size: int]
        shape: (≤24, 4)
      - funnel: dict with keys total_ips, ips_ge1_bin, ips_ge3_bins, analysis_cohort_size
    """

def build_lmsys_monthly(
    df: pd.DataFrame,
    top_n_pairs: int = 5,
    min_votes: int = 100,
    date_start: str = "2023-01",
    date_end: str = "2024-12",
) -> pd.DataFrame:
    """
    Returns: DataFrame[month: str, model_pair: str,
                       win_count: int, lose_count: int, tie_count: int]
    shape: (≤24 × top_n_pairs, 5); bins with < min_votes dropped
    """
```

### `proxy_computer.py`

```python
import numpy as np
import pandas as pd

CORRECTION_REGEX = r'\b(no[,.]|actually[,.]|that\'s wrong|please redo|i meant|wrong[,.])\b'

def tokenize_prompt(text: str, enc) -> int:
    """Returns token count of text using provided tiktoken encoder (cl100k_base)."""

def compute_entropy(win: int, lose: int, tie: int) -> float:
    """
    Shannon entropy H(win,lose,tie) in bits.
    Returns float in [0, log2(3)≈1.585]; np.nan if total==0.
    Uses scipy.stats.entropy([win, lose, tie], base=2).
    """

def correction_freq(conversation: list[dict]) -> float:
    """
    Fraction of turns matching CORRECTION_REGEX (case-insensitive).
    Returns float in [0,1]; 0.0 if conversation is empty.
    """

def proxy2_series(lmsys_monthly: pd.DataFrame) -> pd.Series:
    """
    Mean entropy across model pairs per monthly bin.
    Input: DataFrame[month, model_pair, win_count, lose_count, tie_count]
    Returns: Series indexed by month (str "YYYY-MM"), values: float entropy
    shape: (≤24,)
    """
```

### `stats_tester.py`

```python
import numpy as np

def acf_lag1(series: np.ndarray) -> float:
    """
    Pearson lag-1 autocorrelation of series.
    Returns float in [-1, 1].
    """

def mann_kendall(series: np.ndarray) -> dict:
    """
    Selects MK variant based on ACF lag-1.
    If acf_lag1(series) <= 0.1: scipy.stats.kendalltau(time_idx, series)
    Else: pymannkendall.hamed_rao_modification_test(series)
    Returns: {"tau": float, "p": float, "significant": bool, "method": str}
    """

def bootstrap_ci(
    series: np.ndarray,
    time_idx: np.ndarray,
    B: int = 1000,
    seed: int = 42,
) -> tuple[float, float]:
    """
    Bootstrap 95% CI for Kendall tau.
    Resamples (time_idx, series) pairs with replacement B times.
    Returns: (ci_low, ci_high) at 2.5th and 97.5th percentiles.
    """

def evaluate_gate(results: dict, gate_min_significant: int = 2) -> dict:
    """
    Adds gate_passed (bool) and n_significant (int) to results dict.
    gate_passed = n_significant >= gate_min_significant
    Modifies results in place and returns it.
    """
```

### `visualizer.py`

```python
import pandas as pd
import numpy as np

def fig1_gate_summary(results: dict, out_dir: str) -> None:
    """
    Figure 1: 3-panel bar chart (1×3, figsize=(12,4)).
    Panels: prompt_tokens, vote_entropy, correction_freq.
    Each panel: tau bar ± 95% CI error bar; dashed line at tau=0.
    Color: green if results[proxy]['significant'] else red.
    Annotation: "p={p:.3f}" above each bar.
    Saved to: {out_dir}/fig1_gate_summary.png at dpi=150.
    """

def fig2_proxy_timeseries(
    wildchat_monthly: pd.DataFrame,
    proxy2: pd.Series,
    results: dict,
    out_dir: str,
) -> None:
    """
    Figure 2: 3-panel monthly time series (1×3, figsize=(15,4)).
    Each panel: monthly mean ± 95% CI ribbon; Mann-Kendall trend line (linear fit over tau direction).
    Saved to: {out_dir}/fig2_proxy_timeseries.png
    """

def fig3_cohort_funnel(funnel_counts: dict, out_dir: str) -> None:
    """
    Figure 3: Horizontal bar funnel chart (figsize=(8,4)).
    Bars: total_ips, ips_ge1_bin, ips_ge3_bins, analysis_cohort_size.
    Labels: count and percentage of total on each bar.
    Saved to: {out_dir}/fig3_cohort_funnel.png
    """

def fig4_lmsys_votes(
    lmsys_monthly: pd.DataFrame,
    proxy2: pd.Series,
    out_dir: str,
) -> None:
    """
    Figure 4: Stacked bar (win/lose/tie proportions) + entropy line overlay (twin y-axis).
    x-axis: monthly bins; stacked bars normalized to 1.0.
    Saved to: {out_dir}/fig4_lmsys_votes.png
    """
```

---

## Subtasks

### L-2-1: WildChat Streaming Aggregator with Multiprocessing Tokenization
**Parent Epic**: A-2 (Cohort Construction, complexity 14)

**Data shapes**:
- Input: streaming `Iterable[dict]` — each record has `hashed_ip`, `timestamp`, `conversation`, `toxic`
- Intermediate: `dict[ip][month] = {"prompt_tokens": list[int], "correction_freqs": list[float]}`
- Output: `pd.DataFrame` shape `(≤24, 4)` — `[month, prompt_tokens_mean, correction_freq_mean, cohort_size]`

**Pseudo-code**:
```python
def build_wildchat_monthly(stream, date_start, date_end, min_bins, min_cohort_size, n_workers):
    enc = tiktoken.get_encoding("cl100k_base")
    
    # Pass 1: Stream and accumulate per-IP per-month records
    ip_month_records: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    
    with multiprocessing.Pool(n_workers) as pool:
        # Batch records for parallel tokenization (batch_size=500)
        batch = []
        for record in stream:
            if record["toxic"]:
                continue
            month = parse_month(record["timestamp"])  # "YYYY-MM"
            if not (date_start <= month <= date_end):
                continue
            batch.append((record["hashed_ip"], month, record["conversation"]))
            if len(batch) >= 500:
                _process_batch(pool, enc, batch, ip_month_records)
                batch = []
        if batch:
            _process_batch(pool, enc, batch, ip_month_records)
    
    # Pass 2: Filter returning users (≥ min_bins distinct months)
    returning_ips = {ip for ip, months in ip_month_records.items() if len(months) >= min_bins}
    
    # Pass 3: Aggregate by month across returning-user cohort
    month_agg: dict[str, dict] = defaultdict(lambda: {"tokens": [], "corr": [], "n": 0})
    for ip in returning_ips:
        for month, records in ip_month_records[ip].items():
            month_agg[month]["tokens"].extend(r["prompt_tokens"] for r in records)
            month_agg[month]["corr"].extend(r["correction_freq"] for r in records)
            month_agg[month]["n"] += 1  # count unique IPs per bin
    
    # Pass 4: Drop bins with < min_cohort_size unique IPs; compute monthly means
    rows = []
    for month in sorted(month_agg):
        if month_agg[month]["n"] < min_cohort_size:
            continue
        rows.append({
            "month": month,
            "prompt_tokens_mean": np.mean(month_agg[month]["tokens"]),
            "correction_freq_mean": np.mean(month_agg[month]["corr"]),
            "cohort_size": month_agg[month]["n"],
        })
    
    # Also record funnel counts
    funnel = {
        "total_ips": len(ip_month_records),
        "ips_ge1_bin": len(ip_month_records),  # all that passed date/toxic filter
        "ips_ge3_bins": len(returning_ips),
        "analysis_cohort_size": len(returning_ips),
    }
    return pd.DataFrame(rows), funnel
```

**Edge cases**:
- Timestamp parse failure → skip record (log count at end)
- Empty conversation → correction_freq = 0.0, prompt_tokens = 0
- Month boundary IPs: counted correctly via dict key

---

### L-2-2: Returning-User Cohort Filter Logic
**Parent Epic**: A-2 (Cohort Construction, complexity 14)

**Algorithm**:
```python
# Cohort filter: retain hashed_ip with >= min_bins distinct monthly bins
returning_ips = {
    ip
    for ip, months_dict in ip_month_records.items()
    if len(months_dict) >= min_bins  # distinct months = dict key count
}

# Bin size filter: drop monthly bins with < min_cohort_size unique IPs
valid_months = {
    month
    for month, agg in month_agg.items()
    if agg["n"] >= min_cohort_size
}
```

**Edge cases**:
- IP appearing in same month multiple times: stored as separate records (average within month first)
- Year boundary (Dec 2023 → Jan 2024): treated as distinct months (correct by YYYY-MM key)
- Duplicate timestamps: each conversation counted separately (acceptable — proxy is per-conversation)

---

### L-2-3: LMSYS Top-N Model Pair Selection
**Parent Epic**: A-2 (Cohort Construction, complexity 14)

**Pseudo-code**:
```python
def build_lmsys_monthly(df, top_n_pairs, min_votes, date_start, date_end):
    # Step 1: Filter to date window
    df = df[(df["month"] >= date_start) & (df["month"] <= date_end)].copy()
    
    # Step 2: Normalize winner
    df["winner"] = df["winner"].replace("tie (bothbad)", "tie")
    df = df[df["winner"].isin(["model_a", "model_b", "tie"])]
    
    # Step 3: Canonical model pair key (sorted alphabetically)
    df["model_pair"] = df.apply(
        lambda r: "_vs_".join(sorted([r["model_a"], r["model_b"]])), axis=1
    )
    
    # Step 4: Identify top-N pairs by total vote count
    pair_counts = df.groupby("model_pair").size()
    top_pairs = pair_counts.nlargest(top_n_pairs).index.tolist()
    df = df[df["model_pair"].isin(top_pairs)]
    
    # Step 5: Aggregate win/lose/tie counts per (month, model_pair)
    df["is_win"] = (df["winner"] == "model_a").astype(int)
    df["is_lose"] = (df["winner"] == "model_b").astype(int)
    df["is_tie"] = (df["winner"] == "tie").astype(int)
    
    monthly = df.groupby(["month", "model_pair"]).agg(
        win_count=("is_win", "sum"),
        lose_count=("is_lose", "sum"),
        tie_count=("is_tie", "sum"),
    ).reset_index()
    
    # Step 6: Filter bins with < min_votes
    monthly["total"] = monthly["win_count"] + monthly["lose_count"] + monthly["tie_count"]
    monthly = monthly[monthly["total"] >= min_votes].drop(columns="total")
    
    return monthly  # shape: (≤24*top_n_pairs, 5)
```

**Fallback handling**:
```python
try:
    ds = load_dataset("lmsys/chatbot_arena_conversations")
except Exception:
    ds = load_dataset("lmsys/lmsys-arena-human-preference-55k")
```

---

### L-4-1: Mann-Kendall Variant Selection and Execution
**Parent Epic**: A-4 (Statistical Testing, complexity 13)

**Pseudo-code**:
```python
def acf_lag1(series: np.ndarray) -> float:
    n = len(series)
    mean = series.mean()
    num = np.sum((series[:-1] - mean) * (series[1:] - mean))
    denom = np.sum((series - mean) ** 2)
    return num / denom if denom > 0 else 0.0

def mann_kendall(series: np.ndarray, acf_threshold: float = 0.1) -> dict:
    time_idx = np.arange(len(series))
    acf = acf_lag1(series)
    
    if acf <= acf_threshold:
        # Standard scipy Kendall tau
        tau, p = scipy.stats.kendalltau(time_idx, series)
        method = "kendalltau"
    else:
        # Hamed-Rao autocorrelation-corrected variant
        result = pymannkendall.hamed_rao_modification_test(series)
        tau, p = result.Tau, result.p
        method = "hamed_rao"
    
    return {
        "tau": float(tau),
        "p": float(p),
        "significant": bool(p < 0.05 and abs(tau) > 0.0),
        "method": method,
        "acf_lag1": float(acf),
        "n_months": len(series),
    }
```

**Applied across all 3 proxies**:
```python
proxy_series = {
    "prompt_tokens": wildchat_monthly["prompt_tokens_mean"].values,
    "vote_entropy": proxy2_series(lmsys_monthly).reindex(wildchat_monthly["month"]).values,
    "correction_freq": wildchat_monthly["correction_freq_mean"].values,
}

results = {}
for proxy_name, series in proxy_series.items():
    valid = series[~np.isnan(series)]
    results[proxy_name] = mann_kendall(valid)
```

---

### L-4-2: Bootstrap CI and Gate Evaluation
**Parent Epic**: A-4 (Statistical Testing, complexity 13)

**Pseudo-code**:
```python
def bootstrap_ci(series, time_idx, B=1000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(series)
    tau_samples = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, size=n)
        tau_samples[i], _ = scipy.stats.kendalltau(time_idx[idx], series[idx])
    return (float(np.percentile(tau_samples, 2.5)),
            float(np.percentile(tau_samples, 97.5)))

def evaluate_gate(results, gate_min_significant=2):
    n_significant = sum(1 for v in results.values()
                        if isinstance(v, dict) and v.get("significant", False))
    results["n_significant"] = n_significant
    results["gate_passed"] = n_significant >= gate_min_significant
    return results
```

**results.json structure**:
```json
{
  "config": {"date_start": "2023-01", "date_end": "2024-12", "min_bins": 3, ...},
  "proxies": {
    "prompt_tokens": {"tau": 0.31, "p": 0.024, "significant": true,
                      "method": "kendalltau", "acf_lag1": 0.05,
                      "ci_low": 0.12, "ci_high": 0.48, "n_months": 22},
    "vote_entropy": {...},
    "correction_freq": {...}
  },
  "gate": {"n_significant": 2, "gate_passed": true},
  "cohort": {"total_ips": 850000, "ips_ge1_bin": 420000,
              "ips_ge3_bins": 85000, "analysis_cohort_size": 85000}
}
```

---

### L-3-1: Proxy 3 Regex Validation Protocol
**Parent Epic**: A-3 (Proxy Computation, complexity 11)

**Pseudo-code**:
```python
def validate_correction_regex(sample_conversations: list[list[dict]], n_sample: int = 100) -> float:
    """
    Manual inspection validation of CORRECTION_REGEX construct validity.
    Returns agreement_rate: float in [0,1].
    """
    import re
    pattern = re.compile(CORRECTION_REGEX, re.IGNORECASE)
    
    # Sample n_sample conversations
    rng = np.random.default_rng(42)
    sample_idx = rng.choice(len(sample_conversations), size=min(n_sample, len(sample_conversations)), replace=False)
    
    matches_found = []
    for idx in sample_idx:
        conv = sample_conversations[idx]
        regex_positive = any(pattern.search(turn["content"]) for turn in conv if turn["role"] == "user")
        # In validation mode: print for manual review; in auto mode: log to CSV
        matches_found.append({"idx": int(idx), "regex_match": regex_positive})
    
    # Log to validation CSV for manual audit
    pd.DataFrame(matches_found).to_csv("results/regex_validation_sample.csv", index=False)
    print(f"[Validation] Regex validation sample saved: {len(matches_found)} conversations")
    # Agreement rate computed post-hoc by human reviewer; auto-log only
    return 1.0  # placeholder; actual rate from human review of CSV
```

---

### L-6-1: Figure 1 Gate Summary Chart Specification
**Parent Epic**: A-6 (Visualization, complexity 10)

**Layout spec**:
```
figsize = (12, 4)
nrows=1, ncols=3
subplots: [prompt_tokens | vote_entropy | correction_freq]

Each panel:
  - Bar: height = tau value; color = "#2ecc71" (green) if significant else "#e74c3c" (red)
  - Error bar: yerr = [[tau - ci_low], [ci_high - tau]], ecolor="black", capsize=5
  - Dashed line: ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
  - Annotation: ax.text(0, tau + 0.02, f"p={p:.3f}", ha="center", va="bottom", fontsize=9)
  - x-axis: single tick at 0, label = proxy display name
  - y-axis: "Kendall τ", ylim auto
  - title: "Proxy N: {display_name}"

Proxy display names:
  prompt_tokens  → "Prompt Tokens"
  vote_entropy   → "Vote Entropy"
  correction_freq → "Correction Freq"

save: plt.savefig(f"{out_dir}/fig1_gate_summary.png", dpi=150, bbox_inches="tight")
```

**Pseudo-code**:
```python
def fig1_gate_summary(results, out_dir):
    proxies = ["prompt_tokens", "vote_entropy", "correction_freq"]
    labels = ["Prompt Tokens", "Vote Entropy", "Correction Freq"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    for ax, proxy, label in zip(axes, proxies, labels):
        r = results["proxies"][proxy]
        color = "#2ecc71" if r["significant"] else "#e74c3c"
        tau, ci_low, ci_high = r["tau"], r["ci_low"], r["ci_high"]
        
        ax.bar([0], [tau], color=color, width=0.4,
               yerr=[[tau - ci_low], [ci_high - tau]],
               ecolor="black", capsize=5)
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        ax.text(0, tau + (0.03 if tau >= 0 else -0.06),
                f"p={r['p']:.3f}", ha="center", va="bottom", fontsize=9)
        ax.set_xticks([0])
        ax.set_xticklabels([label])
        ax.set_ylabel("Kendall τ" if proxy == "prompt_tokens" else "")
        ax.set_title(f"{label}")
    
    plt.suptitle("Gate Summary: Mann-Kendall τ by Proxy", fontsize=11, fontweight="bold")
    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(f"{out_dir}/fig1_gate_summary.png", dpi=150, bbox_inches="tight")
    plt.close()
```
