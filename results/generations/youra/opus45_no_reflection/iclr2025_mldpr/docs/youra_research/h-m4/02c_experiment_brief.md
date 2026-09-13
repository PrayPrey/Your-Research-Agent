# Experiment Design: H-M4

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** ImageNet/CIFAR share of total benchmark usage decreases while absolute paper counts remain stable
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> MECHANISM Hypothesis - Tests traditional benchmark persistence with reduced dominance.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M3 PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (Researcher Attention Shift)

### Gate Condition
SHOULD_WORK gate - If fails, document as finding (traditional benchmarks may be actively declining rather than persisting with reduced dominance).

---

## Continuation Context

H-M3 established that researcher attention shifted toward emergent-capability benchmarks post-2021, with emergent share increasing from 7.53% to 26.54%. H-M4 now tests whether traditional benchmarks (ImageNet, CIFAR) persist in absolute terms while losing relative dominance.

### Previous Hypothesis Results (if applicable)
- H-M3 Result: PASS
- Emergent benchmark share increased from 7.53% to 26.54% post-2021
- Chi-square = 1025.23, p < 10^-224
- Data source: pwc-archive/datasets (HuggingFace fallback)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No directly relevant prior implementations found for benchmark usage share analysis. Koch et al. (2021) methodology provides baseline Gini concentration metrics but does not track per-benchmark share over time.

### Archon Code Examples

No relevant code examples found. Implementation will follow PWC client API patterns.

### Exa GitHub Implementations

**Primary Sources Found:**
1. `paperswithcode/paperswithcode-client` (189 stars) - Official Python API client
   - `client.dataset_list()` - Enumerate datasets
   - `client.paper_list()` - Get papers
   - `client.dataset_evaluation_list(dataset_id)` - Get evaluation tables per dataset

2. `paperswithcode/paperswithcode-data` - Data dumps on HuggingFace:
   - `pwc-archive/evaluation-tables` - Task evaluation tables with SOTA metrics
   - `pwc-archive/datasets` - Dataset metadata

3. `huggingface/pwc-cli` (28 stars) - CLI for PWC with benchmark listing:
   - `pwc benchmark list --search ImageNet`
   - Supports filtering by task, min-eval-count, ordering by paper_count

### Implementation Priority Assessment

**CRITICAL: Use PWC data dumps for reproducibility and offline analysis**

**Recommended Implementation Path:**
- Primary: HuggingFace datasets `pwc-archive/evaluation-tables` + `pwc-archive/datasets`
- Fallback: PWC API via `paperswithcode-client` library
- Justification: Data dumps enable reproducible analysis without API rate limits; contain paper-benchmark associations with timestamps

### Code Analysis (Serena MCP)

*Not applicable - no existing codebase to analyze*

---

## Experiment Specification

### Dataset

**Name:** Papers With Code Evaluation Tables + Datasets Archive
**Type:** standard (programmatic-api)
**Source:** HuggingFace Hub
**Identifiers:**
- `pwc-archive/evaluation-tables` - Contains benchmark results with paper links
- `pwc-archive/datasets` - Dataset metadata including creation dates

**Preprocessing:**
1. Load evaluation-tables.json.gz from HuggingFace
2. Extract paper-benchmark associations with submission dates (2018-2024)
3. Filter to ImageNet, CIFAR-10, CIFAR-100 benchmarks
4. Aggregate monthly paper counts per benchmark
5. Compute total benchmark paper counts per month

**Sample Size:** Full PWC archive (~175k papers, ~2.8k datasets)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `pwc-archive/evaluation-tables`, `pwc-archive/datasets`
- Code:
```python
from datasets import load_dataset

eval_tables = load_dataset("pwc-archive/evaluation-tables", split="train")
datasets_meta = load_dataset("pwc-archive/datasets", split="train")
```

### Models

#### Baseline Model

**Type:** Statistical analysis (no ML model)
**Method:** Time series share computation

**Metrics:**
- `traditional_share(t)` = papers_on_traditional(t) / total_benchmark_papers(t)
- `traditional_counts(t)` = absolute paper count on ImageNet + CIFAR per month

#### Proposed Model

**Architecture:** Share trend analysis with stability test

**Core Mechanism Implementation:**

```python
def compute_traditional_benchmark_metrics(eval_data: pd.DataFrame) -> dict:
    """
    Compute share and absolute count metrics for traditional benchmarks.
    
    Args:
        eval_data: DataFrame with columns [paper_id, dataset_name, date]
    
    Returns:
        dict with monthly share, counts, and trend statistics
    """
    # Define traditional benchmarks
    TRADITIONAL = ['imagenet', 'cifar-10', 'cifar-100', 'imagenet-1k']
    
    # Add monthly period
    eval_data['month'] = pd.to_datetime(eval_data['date']).dt.to_period('M')
    
    # Compute monthly totals
    monthly_total = eval_data.groupby('month')['paper_id'].nunique()
    
    # Filter traditional benchmarks (case-insensitive match)
    traditional_mask = eval_data['dataset_name'].str.lower().isin(
        [b.lower() for b in TRADITIONAL]
    )
    traditional_data = eval_data[traditional_mask]
    monthly_traditional = traditional_data.groupby('month')['paper_id'].nunique()
    
    # Compute share
    monthly_share = monthly_traditional / monthly_total
    
    # Split pre-2020 vs post-2020
    pre_2020 = monthly_share[monthly_share.index < '2020-01']
    post_2020 = monthly_share[monthly_share.index >= '2020-01']
    
    pre_counts = monthly_traditional[monthly_traditional.index < '2020-01']
    post_counts = monthly_traditional[monthly_traditional.index >= '2020-01']
    
    # Success criteria checks
    share_decreased = post_2020.mean() < pre_2020.mean()
    
    # Absolute count stability: within 20% of pre-2020 mean
    count_ratio = post_counts.mean() / pre_counts.mean()
    counts_stable = 0.8 <= count_ratio <= 1.2
    
    return {
        'monthly_share': monthly_share,
        'monthly_counts': monthly_traditional,
        'pre_2020_share_mean': pre_2020.mean(),
        'post_2020_share_mean': post_2020.mean(),
        'share_change': post_2020.mean() - pre_2020.mean(),
        'pre_2020_count_mean': pre_counts.mean(),
        'post_2020_count_mean': post_counts.mean(),
        'count_ratio': count_ratio,
        'share_decreased': share_decreased,
        'counts_stable': counts_stable,
        'gate_pass': share_decreased and counts_stable
    }
```

### Training Protocol

*Not applicable - statistical analysis, no model training required*

### Evaluation

**Primary Metrics:**
1. **Share Decrease Test:** `post_2020_share_mean < pre_2020_share_mean`
2. **Count Stability Test:** `0.8 <= (post_2020_count_mean / pre_2020_count_mean) <= 1.2`

**Success Criteria (PoC: Direction-based):**
- Primary: Traditional benchmark share decreases post-2020
- Secondary: Absolute paper counts remain within 20% of pre-2020 levels

**Gate PASS Condition:** Both criteria satisfied

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Time series analysis / statistical comparison
- Library: pandas, scipy.stats (optional: Mann-Whitney U for significance)
- Code:
```python
import pandas as pd
from scipy.stats import mannwhitneyu

# Optional significance test for share decrease
stat, p_value = mannwhitneyu(
    pre_2020_shares, post_2020_shares, alternative='greater'
)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing pre-2020 vs post-2020 share and normalized counts

#### Additional Figures (LLM Autonomous)

1. **Time Series Plot:** Monthly traditional benchmark share (2018-2024) with vertical line at 2020
2. **Stacked Area Chart:** Traditional vs emergent benchmark paper counts over time
3. **Per-Benchmark Breakdown:** Separate lines for ImageNet, CIFAR-10, CIFAR-100

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `share_decreased == True` AND `counts_stable == True`

---

## Appendix: Reference Implementations

### PWC Client API Usage
```python
from paperswithcode import PapersWithCodeClient

client = PapersWithCodeClient()

# List datasets
datasets = client.dataset_list(q="ImageNet")
print(f"Found {datasets.count} ImageNet-related datasets")

# Get evaluation tables for a dataset
evals = client.dataset_evaluation_list("imagenet")
```

### HuggingFace Data Loading
```python
from datasets import load_dataset

# Load evaluation tables (contains paper-benchmark links)
eval_tables = load_dataset("pwc-archive/evaluation-tables", split="train")

# Load dataset metadata
datasets = load_dataset("pwc-archive/datasets", split="train")

# Filter to ImageNet/CIFAR
traditional = ['imagenet', 'cifar-10', 'cifar-100']
filtered = [d for d in datasets if d['name'].lower() in traditional]
```

### PWC CLI Alternative
```bash
# List benchmarks with paper counts
pwc benchmark list --search "ImageNet" --order-by paper_count --json

# Get specific benchmark details
pwc benchmark --name "ImageNet" --json
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- 2026-08-18: Hypothesis h-m4 set to IN_PROGRESS (External loop starting Phase 2C)
- 2026-08-18: Phase 2C experiment design in progress

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web Search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
