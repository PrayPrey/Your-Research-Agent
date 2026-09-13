# Experiment Design: H-E1

**Date:** 2026-08-31
**Author:** Anonymous
**Hypothesis Statement:** Under WildChat-1M (2023-2024 returning user cohorts, ≥3 monthly appearances) and LMSYS Arena (2023-2024 monthly bins), if behavioral proxies (prompt token count, preference vote Shannon entropy, correction/negation frequency) are computed, then statistically significant signal is detectable (Mann-Kendall τ ≠ 0 for at least 2 of 3 proxies), because these interaction metadata fields encode behavioral engagement patterns that vary with model quality improvement.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites for H-E1)
**Gate Status:** MUST_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK — Mann-Kendall τ ≠ 0 (p < 0.05) for ≥2 of 3 behavioral proxies (prompt token count, preference vote Shannon entropy, correction/negation frequency) across 2023-2024 observation window. Failure blocks entire pipeline; investigate data quality if failed.

---

## Continuation Context

First hypothesis in verification chain — no prior hypothesis results to load.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 is the foundation hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Mann-Kendall trend test behavioral proxy experiment design**
- MCP unavailable in ablation mode. Research synthesized from 02b_verification_plan.md Phase 2A context and general domain knowledge.
- Key dataset insights:
  - WildChat-1M (allenai/WildChat-1M, HuggingFace): 1M+ real ChatGPT API interactions, 2022-2024; fields include prompt text, timestamps, model_version, topic_category, turn_count, IP-hash
  - LMSYS Chatbot Arena: timestamped pairwise human preference votes; fields include model_a, model_b, winner, timestamp; available via lm-sys/FastChat GitHub
  - Standard analysis: Mann-Kendall trend test (scipy.stats.kendalltau), Spearman correlation (scipy.stats.spearmanr)

**Query 2: Time-series behavioral proxy implementation challenges**
- Known challenges from Phase 2B:
  - WildChat IP-hash cohort precision: approximate within-user tracking; mitigate by requiring ≥3 monthly appearances per IP-hash
  - LMSYS vote sparsity per monthly bin: filter to model pairs with ≥100 votes/bin
  - Proxy construct validity (A3): token count decline conflates expertise gain with agency loss; composite of 3 proxies required
  - HELM-WildChat version alignment: pre-register model version → deployment date mapping before analysis

**Query 3: Human-AI interaction behavioral analysis benchmarks**
- Established baselines from Phase 2B (Section 1.4):
  - HELM (AI-to-human only): 42-scenario evaluation; domain-stratified scores
  - Null hypothesis baseline: Mann-Kendall stationarity test (τ = 0) on all proxy time series
  - Composition drift alternative: between-cohort decomposition (early Q1 2023 vs. late Q3 2023 cohort entry)

### Archon Code Examples

**Query 1: Mann-Kendall PyTorch / scipy implementation**
- MCP unavailable; standard implementation documented below from scipy.stats:
  ```python
  from scipy.stats import kendalltau
  import numpy as np

  def compute_mann_kendall(time_series):
      """Mann-Kendall trend test on monthly proxy values."""
      n = len(time_series)
      x = np.arange(n)
      tau, p_value = kendalltau(x, time_series)
      return tau, p_value
  ```

**Query 2: Shannon entropy for preference vote distributions**
  ```python
  from scipy.stats import entropy
  import numpy as np

  def compute_vote_entropy(win_counts, lose_counts, tie_counts):
      """Shannon entropy of LMSYS win/lose/tie vote distribution."""
      counts = np.array([win_counts, lose_counts, tie_counts], dtype=float)
      probs = counts / counts.sum()
      return entropy(probs, base=2)
  ```

### Exa GitHub Implementations

**Query 1: WildChat-1M analysis official implementation**
- MCP unavailable in ablation mode.
- Known reference from Phase 2B: allenai/WildChat-1M (HuggingFace dataset), Zhao et al. 2024
- Key loading approach: `datasets.load_dataset("allenai/WildChat-1M")`
- Relevant fields: `conversation` (list of turns), `model`, `timestamp`, `ip`, `country`, `hashed_ip`, `header`
- Preprocessing: extract `prompt_tokens` from first turn length, `topic` inferred from model/conversation content

**Query 2: LMSYS Arena analysis implementation**
- Known reference from Phase 2B: lm-sys/FastChat GitHub; Chiang et al. 2024
- Loading: download raw conversation logs CSV from HuggingFace `lmsys/chatbot_arena_conversations`
- Fields: `question_id`, `model_a`, `model_b`, `winner`, `judge`, `conversation_a`, `conversation_b`, `turn`, `language`, `openai_moderation`, `tstamp`

**Serena Analysis Needed**: False — analysis pipeline uses standard scipy/numpy; no complex custom architecture requiring Serena inspection.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a data analysis study (not a neural architecture paper). Priority:
1. Use WildChat-1M official dataset from allenai (HuggingFace) — Zhao et al. 2024
2. Use LMSYS Arena official dataset from lm-sys (HuggingFace) — Chiang et al. 2024
3. Use scipy.stats standard implementations for Mann-Kendall and Spearman correlation

**Recommended Implementation Path:**
- Primary: HuggingFace `datasets` library for both datasets; scipy.stats for statistics
- Fallback: Direct CSV/JSONL download from lm-sys/FastChat GitHub if HuggingFace unavailable
- Justification: Official dataset releases ensure version consistency and reproducibility; scipy.stats is peer-reviewed standard for nonparametric statistics

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear; analysis pipeline uses standard scipy/numpy/pandas without custom architectures requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset 1: WildChat-1M**
- **Name:** allenai/WildChat-1M
- **Type:** standard (real user-AI interaction logs)
- **Source:** HuggingFace Datasets — Zhao et al. 2024
- **Splits:** Full dataset (~1M conversations); filter to 2023-2024 timestamp range
- **Sample Size:** After filtering to ≥3 monthly appearances per IP-hash (2023-2024): estimated 50,000-200,000 qualifying interactions from ~5,000-20,000 unique cohort IP-hashes
- **Preprocessing:**
  - Extract fields: `conversation[0].content` (first turn = prompt), `timestamp`, `model`, `hashed_ip`
  - Compute `prompt_token_count` = word-piece approximate (len(prompt.split()) × 1.3, or tiktoken for GPT models)
  - Assign `monthly_bin` = YYYY-MM from timestamp
  - Construct cohorts: group by `hashed_ip`, filter to IP-hashes appearing in ≥3 distinct monthly bins within 2023-2024
  - Compute correction/negation frequency: count turns containing ["actually", "that's wrong", "no, I meant", "please redo", "that is incorrect", "you're wrong"] normalized by turn_count per session
- **No augmentation** — real behavioral data; augmentation would corrupt validity

**Dataset 2: LMSYS Chatbot Arena**
- **Name:** lmsys/chatbot_arena_conversations
- **Type:** standard (real human preference votes)
- **Source:** HuggingFace Datasets — Chiang et al. 2024
- **Splits:** Full dataset; filter to 2023-2024 timestamp range; filter model pairs with ≥100 votes/monthly bin
- **Sample Size:** After 2023-2024 filter: estimated 300,000-600,000 pairwise comparisons; top-5 models by vote count selected
- **Preprocessing:**
  - Extract fields: `model_a`, `model_b`, `winner`, `tstamp`
  - Assign `monthly_bin` = YYYY-MM from tstamp
  - Compute per-bin vote distributions: count(winner==model_a), count(winner==model_b), count(winner=="tie") per model pair per monthly bin
  - Compute Shannon entropy H per bin per model pair: `entropy([p_win, p_lose, p_tie], base=2)`
  - Aggregate: mean entropy per monthly bin across top-5 model pairs

**Loading Information** (for Phase 4 download):

Dataset 1:
- Method: HuggingFace datasets
- Identifier: `"allenai/WildChat-1M"`
- Code: `from datasets import load_dataset; ds = load_dataset("allenai/WildChat-1M")`

Dataset 2:
- Method: HuggingFace datasets
- Identifier: `"lmsys/chatbot_arena_conversations"`
- Code: `from datasets import load_dataset; ds = load_dataset("lmsys/chatbot_arena_conversations")`

### Models

#### Baseline Model

**No ML model training.** H-E1 is a statistical signal-detection study on existing interaction logs. The "baseline" is the null hypothesis model: Mann-Kendall τ = 0 (no trend) for all proxies.

**Baseline (H0):** Stationary time series — no monotonic trend in any proxy over 2023-2024.
**Method:** Mann-Kendall trend test with p < 0.05 significance threshold.

**Loading Information** (for Phase 4 download):
- Method: scipy (standard library)
- Identifier: `scipy.stats.kendalltau`
- Code:
  ```python
  from scipy.stats import kendalltau
  tau, p_value = kendalltau(time_index, proxy_time_series)
  ```

#### Proposed Model

**Architecture:** No neural model — proposed "model" is the composite behavioral proxy measurement framework:

- Proxy 1: Mann-Kendall trend on within-cohort prompt token count (WildChat)
- Proxy 2: Mann-Kendall trend on LMSYS vote Shannon entropy per monthly bin
- Proxy 3: Mann-Kendall trend on within-cohort correction/negation frequency (WildChat)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Behavioral Proxy Signal Detection
# Based on: Mann-Kendall nonparametric trend test (Kendall 1975)
# Dataset: WildChat-1M + LMSYS Chatbot Arena

import numpy as np
from scipy.stats import kendalltau, entropy as scipy_entropy
from collections import defaultdict

def compute_proxy_signals(wildchat_cohort_df, lmsys_monthly_df):
    """
    Args:
        wildchat_cohort_df: DataFrame with columns
            [monthly_bin, hashed_ip, prompt_token_count, correction_freq]
        lmsys_monthly_df: DataFrame with columns
            [monthly_bin, win_count, lose_count, tie_count]
    Returns:
        dict of {proxy_name: (tau, p_value)}
    """
    results = {}
    monthly_bins = sorted(wildchat_cohort_df['monthly_bin'].unique())
    time_idx = np.arange(len(monthly_bins))

    # Proxy 1: Within-cohort prompt token count trend
    token_series = [
        wildchat_cohort_df[wildchat_cohort_df['monthly_bin']==b]
        ['prompt_token_count'].mean()
        for b in monthly_bins
    ]
    tau1, p1 = kendalltau(time_idx, token_series)
    results['prompt_token_count'] = (tau1, p1)

    # Proxy 2: LMSYS vote Shannon entropy trend
    lmsys_bins = sorted(lmsys_monthly_df['monthly_bin'].unique())
    lmsys_idx = np.arange(len(lmsys_bins))
    entropy_series = [
        scipy_entropy([row.win_count, row.lose_count, row.tie_count], base=2)
        for _, row in lmsys_monthly_df.sort_values('monthly_bin').iterrows()
    ]
    tau2, p2 = kendalltau(lmsys_idx, entropy_series)
    results['vote_entropy'] = (tau2, p2)

    # Proxy 3: Correction/negation frequency trend
    corr_series = [
        wildchat_cohort_df[wildchat_cohort_df['monthly_bin']==b]
        ['correction_freq'].mean()
        for b in monthly_bins
    ]
    tau3, p3 = kendalltau(time_idx, corr_series)
    results['correction_frequency'] = (tau3, p3)

    return results

# Success: tau != 0 (p < 0.05) for >= 2 of 3 proxies
```

### Training Protocol

No model training. Statistical analysis protocol:

**Analysis Protocol:**
- Language: Python 3.10+
- Libraries: `datasets`, `pandas`, `numpy`, `scipy`, `matplotlib`
- Seed: 42 (for any bootstrap resampling)
- Hardware: CPU-only (no GPU needed for statistical analysis)

**Execution Steps:**
1. Download WildChat-1M and LMSYS Arena via HuggingFace `datasets`
2. Filter WildChat to 2023-01 through 2024-12 timestamp range
3. Build IP-hash cohorts: retain hashed_ip appearing in ≥3 distinct monthly bins
4. Compute proxy time series (Proxy 1, 3) from WildChat cohort data
5. Filter LMSYS to 2023-01 through 2024-12; filter model pairs with ≥100 votes/bin
6. Compute Shannon entropy time series (Proxy 2) from LMSYS
7. Run Mann-Kendall on all 3 proxy time series
8. Report: τ, p-value, |τ| effect size for each proxy
9. Success check: ≥2 of 3 proxies with p < 0.05

**Seeds:** 1 fixed seed (42) for bootstrap CI only

### Evaluation

**Primary Metrics:**
- Mann-Kendall τ for each of 3 proxies (range: -1 to +1)
- p-value for each proxy (threshold: 0.05)
- |τ| effect size for each proxy (target: |τ| > 0.2)

**Success Criteria:**
- proposed_metric > baseline_metric: ≥2 of 3 proxies show τ ≠ 0 (p < 0.05) — any direction (positive or negative trend)
- Secondary: |τ| > 0.2 for at least 1 proxy (effect above noise)

**Expected Baseline Performance** (from research):
- Null: all τ ≈ 0 (no trend) — if true, BAA framework cannot proceed
- Expected if H-E1 correct: Proxy 1 (token count) τ < 0; Proxy 2 (vote entropy) τ < 0; Proxy 3 (correction freq) τ < 0
- Literature (Dell'Acqua 2023, Perez 2023) suggests behavioral disengagement over time — directional prediction: negative trend

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical trend analysis
- Library: scipy.stats
- Code: `from scipy.stats import kendalltau; tau, p = kendalltau(time_idx, proxy_series)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of τ values for all 3 proxies with significance markers (p < 0.05 highlighted); horizontal line at τ = 0

#### Additional Figures (LLM Autonomous)
Based on hypothesis type (EXISTENCE, signal detection), the following additional figures are recommended:
- Time series plots: monthly mean for each proxy overlaid with trend line (2023-2024)
- P-value heatmap across all 3 proxies × datasets (WildChat Proxy1, WildChat Proxy3, LMSYS Proxy2)
- Cohort size histogram: distribution of WildChat IP-hash cohort sizes (validate ≥3 monthly bin filter)
- LMSYS vote count per bin: validate ≥100 votes/bin filter adequacy

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ≥2 of 3 proxies show Mann-Kendall τ ≠ 0, p < 0.05 (proposed_metric > baseline_metric)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1:** Phase 2B (02b_verification_plan.md) — behavioral proxy specification
- Type: Internal Phase 2B output
- Query Used: Direct extraction from verified hypothesis document
- Relevance: Complete proxy definitions, cohort construction methodology, success criteria
- Key Insights:
  - IP-hash cohort minimum: ≥3 monthly appearances
  - Correction markers list: ["actually", "that's wrong", "no, I meant", "please redo", "that is incorrect", "you're wrong"]
  - LMSYS filter: ≥100 votes per model pair per monthly bin
- Used For: Dataset specification, evaluation metrics, cohort construction

**Source 2:** Phase 2B Section 1.4 — Baseline methods
- Type: Internal Phase 2B output
- Relevance: Null hypothesis baseline (Mann-Kendall stationarity), composition drift alternative
- Key Insights: scipy.stats.kendalltau as standard implementation; bootstrap B=1000 for CI
- Used For: Training protocol, evaluation metrics

### Archon Code Examples

**Code Source 1:** scipy.stats.kendalltau (standard library)
- Query Used: N/A — standard well-known implementation
- Key Code:
  ```python
  from scipy.stats import kendalltau
  tau, p_value = kendalltau(x, y)
  # tau: Kendall's tau statistic (-1 to 1)
  # p_value: two-sided p-value under H0: tau == 0
  ```
- Used For: All 3 proxy trend tests

**Code Source 2:** scipy.stats.entropy (standard library)
- Key Code:
  ```python
  from scipy.stats import entropy
  h = entropy([p_win, p_lose, p_tie], base=2)
  # h: Shannon entropy in bits (0 = deterministic, log2(3) ≈ 1.585 = uniform)
  ```
- Used For: Proxy 2 (LMSYS vote entropy computation)

### B. GitHub Implementations (Exa)

**Repository 1:** allenai/WildChat (HuggingFace)
- URL: https://huggingface.co/datasets/allenai/WildChat-1M
- Query Used: N/A (ablation mode; known from Phase 2B)
- Relevance: Official WildChat-1M dataset release — Zhao et al. 2024
- Key Code:
  ```python
  from datasets import load_dataset
  ds = load_dataset("allenai/WildChat-1M")
  # Fields: conversation (list), model, timestamp, ip, country, hashed_ip, header
  ```
- Configuration Extracted: full dataset, filter by timestamp 2023-2024
- Used For: Dataset 1 loading specification

**Repository 2:** lm-sys/FastChat (HuggingFace)
- URL: https://huggingface.co/datasets/lmsys/chatbot_arena_conversations
- Query Used: N/A (ablation mode; known from Phase 2B)
- Relevance: Official LMSYS Chatbot Arena conversation logs — Chiang et al. 2024
- Key Code:
  ```python
  from datasets import load_dataset
  ds = load_dataset("lmsys/chatbot_arena_conversations")
  # Fields: question_id, model_a, model_b, winner, tstamp, conversation_a, conversation_b
  ```
- Used For: Dataset 2 loading specification

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. Analysis pipeline uses only standard scipy/numpy/pandas with no custom architectures requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: None — H-E1 is the first hypothesis in the verification chain (no prerequisites).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset 1 (WildChat-1M) | Phase 2B Section 1.3 | 02b_verification_plan.md |
| Dataset 2 (LMSYS Arena) | Phase 2B Section 1.3 | 02b_verification_plan.md |
| Cohort construction (≥3 bins) | Phase 2B H-E1 protocol | 02b_verification_plan.md Step 2 |
| Correction markers list | Phase 2B H-E1 protocol | 02b_verification_plan.md Step 2 |
| LMSYS vote filter (≥100/bin) | Phase 2B risk analysis | 02b_verification_plan.md R2 |
| Mann-Kendall implementation | scipy.stats standard library | kendalltau documentation |
| Shannon entropy computation | scipy.stats standard library | entropy documentation |
| Success criteria (≥2/3 proxies, p<0.05) | Phase 2B H-E1 success criteria | 02b_verification_plan.md |
| Effect size threshold (|τ|>0.2) | Phase 2B H-E1 success criteria | 02b_verification_plan.md |
| Null hypothesis baseline | Phase 2B Section 1.4 | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-31T00:00:00Z

### Workflow History for This Hypothesis
- 2026-08-31: H-E1 set to IN_PROGRESS (Phase 2C started)
- 2026-08-31: Phase 2C experiment design completed

---

*MCP Tools Used: None (ablation mode — Archon, Exa, Serena unavailable; research synthesized from Phase 2B context)*
*All specifications grounded in 02b_verification_plan.md Phase 2A/2B outputs*
*Next Phase: Phase 3 - Implementation Planning*
