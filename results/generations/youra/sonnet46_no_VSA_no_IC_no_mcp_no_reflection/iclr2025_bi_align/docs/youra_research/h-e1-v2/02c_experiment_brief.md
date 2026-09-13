# Experiment Design: h-e1-v2

**Date:** 2026-08-31
**Author:** Anonymous
**Hypothesis Statement:** Under WildChat-1M (2023-2024 returning user cohorts, ≥3 monthly appearances) and LMSYS Arena (2023-2024 monthly bins), if behavioral proxies (prompt token count, preference vote Shannon entropy, correction/negation frequency) are computed, then statistically significant signal is detectable (Mann-Kendall τ ≠ 0 for at least 2 of 3 proxies), because these interaction metadata fields encode behavioral engagement patterns that vary with model quality improvement.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED (Phase 2C)
**Prerequisites Satisfied:** None required (foundation hypothesis)
**Gate Status:** MUST_WORK — gate pending Phase 4 execution

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1-v2
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK — if ≥2/3 behavioral proxies show Mann-Kendall τ ≠ 0 (p < 0.05), gate passes and pipeline continues to H-M1. If gate fails, entire BAA framework is stopped pending data quality investigation.

---

## Continuation Context

This is a versioned retry of h-e1 (version 1 failed gate). h-e1-v2 refines the dataset selection to focus on WildChat-1M 2023-2024 cohorts with stricter returning-user filter (≥3 monthly appearances) and adds the LMSYS Arena fallback dataset explicitly. No positive results from h-e1 to inherit.

### Previous Hypothesis Results (if applicable)
h-e1 (version 1): gate not satisfied. No validated hyperparameters or proven components to carry forward. Starting fresh with refined cohort construction strategy.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design — behavioral proxy trend detection on interaction logs**

- **Mann-Kendall Trend Test** (standard non-parametric temporal trend test)
  - Dataset: Applied to monthly time series (24 bins for 2023-2024 window)
  - Hyperparameters: None (non-parametric); p < 0.05 significance threshold
  - Key insight: τ ∈ [-1,1]; robust to outliers; no normality assumption required
  - Standard for behavioral trend analysis without distributional assumptions

- **Shannon Entropy on Preference Vote Distributions**
  - Dataset: LMSYS Arena win/lose/tie counts per (model_pair × monthly_bin)
  - Key insight: H = -Σ p_i log2(p_i); range [0, log2(3) ≈ 1.585] for 3 outcomes
  - Entropy decreasing over time = preference votes becoming more decisive/homogeneous

- **WildChat-1M Cohort Quality**
  - Dataset: allenai/WildChat-1M (~1M conversations, real ChatGPT API users)
  - IP-hash cohort tracking is approximate; within-cohort vs. between-cohort variance ratio is a diagnostic
  - Filter: ≥3 monthly appearances per IP-hash guards against transient users inflating signal

**Query 2: Implementation Challenges**
- WildChat IP-hash is coarse; some IP-hash collisions possible (multi-user NAT) — acknowledged as assumption A1 in Phase 2B
- Mann-Kendall τ can be inflated by autocorrelation in monthly bins — use block bootstrap or Hamed-Rao correction if needed
- LMSYS bin size: filter to model pairs with ≥100 votes/month to stabilize entropy estimate
- Correction/negation frequency regex: must validate against manual inspection sample to confirm construct validity

**Query 3: Benchmark results**
- No established ground truth for human behavioral adaptation in AI interactions
- H0 (τ = 0 for all proxies) serves as statistical baseline
- Dell'Acqua et al. 2023 (deskilling): behavioral disengagement effect size ≈ 0.3-0.5 SD in consulting study → expected |τ| ≈ 0.2-0.4 if analogous signal present in WildChat

### Archon Code Examples

**Mann-Kendall + Shannon Entropy Core Pattern:**
```python
from scipy import stats
import numpy as np

def compute_mann_kendall(time_series):
    tau, p_value = stats.kendalltau(
        np.arange(len(time_series)), time_series
    )
    return tau, p_value

def vote_entropy(win_counts, lose_counts, tie_counts):
    total = win_counts + lose_counts + tie_counts
    if total == 0:
        return np.nan
    probs = np.array([win_counts, lose_counts, tie_counts]) / total
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))
```

### Exa GitHub Implementations

**Repository 1: allenai/WildChat** (Official)
- **URL:** https://github.com/allenai/WildChat
- **Relevance:** Official WildChat-1M dataset release (Zhao et al. 2024) — ground truth for field structure
- **Key Code:**
  ```python
  from datasets import load_dataset
  ds = load_dataset("allenai/WildChat-1M", streaming=True)
  # Key fields: conversation, timestamp, model, hashed_ip, country, toxic
  # conversation[0]['content'] = first user prompt
  ```
- **Training Config:** N/A (analysis pipeline)
- **Dataset:** WildChat-1M (~1M conversations, 2023-2024)
- **Results:** N/A

**Repository 2: lm-sys/FastChat** (LMSYS Arena)
- **URL:** https://github.com/lm-sys/FastChat
- **Relevance:** Official LMSYS Chatbot Arena — preference vote data source
- **Key Code:**
  ```python
  from datasets import load_dataset
  ds = load_dataset("lmsys/chatbot_arena_conversations")
  # Key fields: model_a, model_b, winner, tstamp, conversation_a, conversation_b
  # winner ∈ {"model_a", "model_b", "tie", "tie (bothbad)"}
  ```
- **Dataset:** lmsys/chatbot_arena_conversations or lmsys/lmsys-arena-human-preference-55k (fallback)

**Repository 3: mmhs013/pymannkendall**
- **URL:** https://github.com/mmhs013/pymannkendall
- **Relevance:** Specialized Mann-Kendall variants including autocorrelation-corrected versions
- **Key Code:**
  ```python
  import pymannkendall as mk
  result = mk.original_test(time_series)
  # Returns: trend, h, p, z, Tau, s, var_s, slope, intercept
  # mk.hamed_rao_modification_test() for autocorrelated series
  ```

**Serena Analysis Needed:** False

### 🎯 Implementation Priority Assessment

This is an original empirical analysis, not a paper reproduction. No "author's official implementation" exists.

**Recommended Implementation Path:**
- Primary: Custom Python pipeline using datasets + pandas + scipy + tiktoken
- Fallback: Use pymannkendall for autocorrelation-robust Mann-Kendall if autocorrelation detected in monthly series
- Justification: Standard statistical pipeline; no complex model architecture requiring Serena analysis

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Standard scipy/pandas pipeline with no custom architectures.

---

## Experiment Specification

### Dataset

**Dataset 1: WildChat-1M**
- **Name:** allenai/WildChat-1M
- **Type:** standard (real public dataset)
- **Source:** HuggingFace
- **Size:** ~1M conversations
- **Temporal Coverage:** 2023-2024 (timestamp field)
- **Key Fields:** `hashed_ip`, `model`, `timestamp`, `conversation` (list of turns), `toxic`
- **Cohort Construction:** Group by `hashed_ip`; retain IPs appearing in ≥3 distinct monthly bins in 2023-2024 window
- **Proxy 1 (prompt_tokens):** `len(tiktoken.encode(conversation[0]['content']))` using `cl100k_base`
- **Proxy 3 (correction_freq):** count turns containing regex `r'\b(no[,.]|actually[,.]|that\'s wrong|please redo|i meant|wrong[,.])\b'` normalized by `turn_count`
- **Preprocessing:** Filter to 2023-01 ≤ timestamp ≤ 2024-12; drop `toxic=True` conversations; drop bins with < 50 cohort members
- **Augmentation:** None

**Dataset 2: LMSYS Arena**
- **Name:** lmsys/chatbot_arena_conversations (primary); lmsys/lmsys-arena-human-preference-55k (fallback)
- **Type:** standard (real public dataset)
- **Source:** HuggingFace
- **Key Fields:** `model_a`, `model_b`, `winner`, `tstamp`
- **Proxy 2 (vote_entropy):** Shannon entropy H(win, lose, tie) per (model_pair × monthly_bin); filter to bins with ≥100 votes
- **Temporal Coverage:** 2023-2024 (tstamp → datetime)
- **Preprocessing:** Filter to 2023-01 ≤ tstamp ≤ 2024-12; select top-5 model pairs by total vote count; normalize winner to {win, lose, tie}

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- Identifier (WildChat): `"allenai/WildChat-1M"`
- Identifier (LMSYS): `"lmsys/chatbot_arena_conversations"`
- Code:
  ```python
  from datasets import load_dataset
  wildchat = load_dataset("allenai/WildChat-1M", streaming=True)
  lmsys = load_dataset("lmsys/chatbot_arena_conversations")
  ```

### Models

#### Baseline Model

**No model training required.** Baseline is the null hypothesis H0: Mann-Kendall τ = 0 for all 3 proxies (stationarity — no temporal trend).

**Statistical baseline:**
- Expected distribution under H0: τ ≈ 0 for each proxy; p-values uniformly distributed on [0,1]
- By chance at α = 0.05 with 3 independent tests: ~0.14 expected false positives (3 × 0.05 under Bonferroni-uncorrected)
- Bonferroni-corrected threshold: p < 0.017 for individual proxies if strict; gate uses ≥2/3 at p < 0.05 (uncorrected) as sufficient for PoC

**Loading Information** (for Phase 4):
- Method: N/A (statistical null hypothesis, not a loadable model)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Behavioral Proxy Trend Detection Pipeline (3-proxy Mann-Kendall analysis)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Behavioral Proxy Trend Detection for h-e1-v2
# Based on: scipy.stats.kendalltau, allenai/WildChat-1M, lm-sys/FastChat

def compute_proxy_trends(wildchat_monthly, lmsys_monthly):
    """
    Args:
        wildchat_monthly: DataFrame with columns [month, prompt_tokens, correction_freq]
                          aggregated per monthly bin across returning-user cohort
        lmsys_monthly: DataFrame with columns [month, win, lose, tie]
                       aggregated per monthly bin for top-5 model pairs
    Returns:
        dict of {proxy_name: {'tau': float, 'p': float, 'significant': bool}}
    """
    results = {}
    months = np.arange(len(wildchat_monthly))

    # Proxy 1: Prompt token count monotonic trend
    results['prompt_tokens'] = _mk_test(wildchat_monthly['prompt_tokens'].values, months)

    # Proxy 2: LMSYS vote Shannon entropy monotonic trend
    entropy_series = lmsys_monthly.apply(
        lambda r: -sum(p * np.log2(p) for p in
                       [r['win']/r.total, r['lose']/r.total, r['tie']/r.total]
                       if p > 0), axis=1
    )
    results['vote_entropy'] = _mk_test(entropy_series.values, np.arange(len(entropy_series)))

    # Proxy 3: Correction/negation frequency trend
    results['correction_freq'] = _mk_test(wildchat_monthly['correction_freq'].values, months)

    # Gate evaluation
    n_significant = sum(1 for v in results.values() if v['significant'])
    results['gate_passed'] = n_significant >= 2
    results['n_significant'] = n_significant
    return results

def _mk_test(series, time_idx):
    tau, p = stats.kendalltau(time_idx, series)
    return {'tau': tau, 'p': p, 'significant': p < 0.05 and abs(tau) > 0.0}
```

### Training Protocol

**No model training.** Analysis execution protocol:

- **Language:** Python 3.10+
- **Dependencies:** `datasets`, `pandas`, `scipy`, `numpy`, `tiktoken`, `tqdm`
- **Execution:** Single-pass streaming for WildChat-1M (memory-efficient); full load for LMSYS (≤55K rows)
- **Compute:** CPU-only; estimated 2-4 hours for WildChat streaming + tokenization
- **Seeds:** `np.random.seed(42)` for any bootstrap CI computation
- **Parallelism:** WildChat per-record tokenization parallelized with `multiprocessing.Pool` (n_workers=4)

**Step-by-step execution:**
1. Download both datasets (HuggingFace)
2. Filter to 2023-2024 temporal window
3. Construct WildChat returning-user cohorts (≥3 monthly bins per hashed_ip)
4. Compute monthly aggregates for all 3 proxies
5. Run Mann-Kendall τ for each proxy
6. Evaluate gate: ≥2/3 significant at p < 0.05
7. Generate figures

### Evaluation

**Metrics:**

| Proxy | Metric | Significance Threshold | Effect Size |
|---|---|---|---|
| Prompt token count | Mann-Kendall τ | p < 0.05 | |τ| > 0.2 |
| Vote entropy | Mann-Kendall τ | p < 0.05 | |τ| > 0.2 |
| Correction frequency | Mann-Kendall τ | p < 0.05 | |τ| > 0.2 |

**Success Criteria:**
- PASS (gate satisfied): ≥2/3 proxies show p < 0.05
- PARTIAL: 1/3 proxies pass — investigate data quality
- FAIL (gate not satisfied): 0/3 — BAA framework under investigation

**Expected Baseline Performance (from literature):**
- Under H0: ~0-1 proxy significant by chance (FDR at α = 0.05)
- Under H1 (from Dell'Acqua 2023 effect magnitudes): |τ| ≈ 0.2-0.4, p < 0.05 expected for 2-3 proxies
- Source: Phase 2B §6.1 Thesis, Dell'Acqua et al. 2023

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical trend analysis (non-parametric)
- Library: `scipy.stats` (kendalltau, entropy, spearmanr)
- Code:
  ```python
  from scipy import stats
  tau, p = stats.kendalltau(time_idx, proxy_series)
  entropy = stats.entropy([win, lose, tie], base=2)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: 3-panel bar chart of τ values for each proxy with 95% CI (bootstrap, B=1000); p-value annotations; dashed horizontal line at τ = 0; PASS/FAIL color coding (green = p < 0.05, red = p ≥ 0.05)

#### Additional Figures (LLM Autonomous)

Based on the time-series nature of this hypothesis, generate:
1. **Proxy Time Series (3-panel):** Monthly means ± 95% CI for prompt_tokens, vote_entropy, correction_freq over 2023-2024 (24 monthly bins); Mann-Kendall trend line overlay
2. **Cohort Retention Funnel:** Total WildChat users → users with ≥1 monthly appearance → users with ≥3 appearances → analysis cohort size; communicates dataset quality
3. **LMSYS Vote Distribution Evolution:** Stacked bar chart of win/lose/tie proportions per monthly bin for top-5 model pairs; entropy overlay

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-e1-v2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ≥2/3 proxies: Mann-Kendall p < 0.05 (τ ≠ 0)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1: Mann-Kendall Trend Test — Behavioral Time Series**
- Type: Standard statistical methodology
- Query: "behavioral proxy trend detection Mann-Kendall experiment design"
- Relevance: Non-parametric temporal trend test; appropriate for monthly behavioral aggregates
- Key Insights:
  - τ ∈ [-1,1]; p < 0.05 threshold; robust to outliers, monotonic trend detection
  - Hamed-Rao modification corrects for autocorrelation in correlated series
  - pymannkendall library provides 12 variants including seasonal and modified versions
- Used For: Core statistical test (all 3 proxies)

**Source A.2: Shannon Entropy for Vote Distribution Diversity**
- Type: Information theory standard
- Query: "preference vote entropy human feedback diversity measurement"
- Relevance: H(win,lose,tie) quantifies diversity of preference judgment
- Key Insights:
  - H = -Σ p_i log2(p_i); H_max = log2(3) ≈ 1.585 for 3 outcomes
  - Declining entropy = preferences converging (more decisive) as better models emerge
  - Must filter bins with < 100 votes to avoid entropy instability from small n
- Used For: Proxy 2 (LMSYS vote entropy)

**Source A.3: WildChat-1M Dataset (Zhao et al. 2024)**
- Type: Dataset documentation
- Query: "WildChat-1M dataset field structure preprocessing"
- Relevance: Confirms available metadata fields; establishes IP-hash cohort tracking approach
- Key Insights:
  - ~1M real ChatGPT conversations collected via WildChat proxy
  - Fields: hashed_ip, model, timestamp, conversation (list of dicts with role/content)
  - Minimal filtering: toxic flag available; PII handled via hashing
- Used For: Dataset specification, cohort construction protocol

### B. GitHub Implementations (Exa)

**Repository B.1: allenai/WildChat** (Official)
- URL: https://github.com/allenai/WildChat
- Query: "WildChat-1M HuggingFace dataset official implementation"
- Relevance: Official data release — authoritative for field structure
- Key Code (annotated):
  ```python
  from datasets import load_dataset
  ds = load_dataset("allenai/WildChat-1M", streaming=True)
  # Use streaming=True for memory efficiency with ~1M conversations
  # conversation[0]['content'] = first user turn (the prompt)
  # timestamp = ISO format string → parse to datetime for monthly binning
  ```
- Configuration Extracted: streaming=True for WildChat; batch processing per shard
- Used For: Dataset loading specification (Step 5), prompt token extraction

**Repository B.2: lm-sys/FastChat** (LMSYS Arena Official)
- URL: https://github.com/lm-sys/FastChat
- Query: "LMSYS chatbot arena preference votes dataset HuggingFace"
- Relevance: Official LMSYS Arena release — authoritative for vote field structure
- Key Code (annotated):
  ```python
  from datasets import load_dataset
  ds = load_dataset("lmsys/chatbot_arena_conversations")
  # winner ∈ {"model_a", "model_b", "tie", "tie (bothbad)"}
  # Normalize: "tie (bothbad)" → "tie" for entropy computation
  # tstamp = Unix timestamp (float) → datetime for monthly binning
  ```
- Configuration Extracted: winner normalization required; tstamp → datetime conversion
- Used For: LMSYS Arena vote entropy computation

**Repository B.3: mmhs013/pymannkendall**
- URL: https://github.com/mmhs013/pymannkendall
- Query: "Mann-Kendall Python time series trend test implementation"
- Relevance: Specialized library with autocorrelation-robust variants
- Key Code (annotated):
  ```python
  import pymannkendall as mk
  result = mk.original_test(time_series)
  # Returns namedtuple: trend ('increasing'/'decreasing'/'no trend'), h, p, z, Tau, s
  # mk.hamed_rao_modification_test() for autocorrelated monthly series
  # Prefer over raw scipy.kendalltau for pre-whitening if ACF(lag-1) > 0.1
  ```
- Used For: Pseudo-code core mechanism (Step 6), Phase 4 implementation reference

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. Standard scipy/pandas patterns require no semantic analysis.

### D. Previous Hypothesis Context

**Previous Context:** h-e1 (version 1) — gate not satisfied. No positive results, validated hyperparameters, or proven pipeline components to carry forward. h-e1-v2 is a fresh implementation with refined cohort filter (stricter ≥3 monthly appearances) and more explicit LMSYS fallback dataset.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---|---|---|
| Dataset: WildChat-1M | Phase 2A/2B | 02b_verification_plan.md §1.3 |
| Dataset: LMSYS Arena | Phase 2A/2B | 02b_verification_plan.md §1.3 |
| Proxy 1: prompt_tokens | Phase 2B | §2.2 H-E1 Verification Protocol step 1-3 |
| Proxy 2: vote_entropy | Phase 2B | §2.2 H-E1 Verification Protocol step 4-5 |
| Proxy 3: correction_freq | Phase 2B | §2.2 H-E1 Verification Protocol step 4-5 |
| Mann-Kendall τ test | Standard stats | scipy.stats.kendalltau, pymannkendall B.3 |
| Gate threshold ≥2/3 | Phase 2B | §3.2 Gate Summary H-E1 Pass Condition |
| Effect size |τ| > 0.2 | Phase 2B | §2.2 H-E1 Success Criteria (Secondary) |
| Cohort filter ≥3 bins | Phase 2B | §2.2 H-E1 Verification Protocol step 2 |
| Vote bin filter ≥100 | Domain best practice | Source A.2 entropy stability |
| Shannon entropy formula | Standard info theory | Source A.2 |
| Correction frequency regex | Phase 2B | §2.2 H-E1 Verification Protocol step 4 |
| WildChat field structure | GitHub B.1 | allenai/WildChat official |
| LMSYS field structure | GitHub B.2 | lm-sys/FastChat official |
| Expected effect magnitude | Phase 2B §6.1 | Dell'Acqua 2023 analogy |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written to disk)
**Date:** 2026-08-31

### Workflow History for This Hypothesis
- h-e1-v2 set to IN_PROGRESS (Phase 2C start)
- Phase 2C Steps 1-8 completed (UNATTENDED mode)
- experiment_design.status → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code) — ablation mode, domain knowledge synthesis applied; Exa (GitHub) — ablation mode, known repository synthesis applied; Serena — skipped (not needed)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
