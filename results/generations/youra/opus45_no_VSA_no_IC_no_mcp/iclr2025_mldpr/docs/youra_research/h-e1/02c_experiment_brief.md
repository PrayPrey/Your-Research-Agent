# Experiment Design: h-e1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** DNSI can be reliably computed from PapersWithCode SOTA histories using 6-month windowing and difficulty normalization (class count proxy)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK - Not yet satisfied

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: If DNSI computation fails or produces undefined values for >50% of target benchmarks, the entire verification chain fails.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to incorporate.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in DAG.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable in this session. Findings sourced via web search.

**Query 1: Benchmark Saturation Metrics**
- Benchmark saturation research exists at [evaleval/benchmark-saturation](https://github.com/evaleval/benchmark-saturation)
- Implements S_index (statistical saturation index) for HELM and HuggingFace leaderboards
- Framework organized as Python package with `metrics/`, `processing/`, `leaderboards/` modules
- No entropy-based metrics explicitly documented, but temporal analysis included

**Query 2: Generalization Gap Prediction**
- ICLR 2019 paper on predicting generalization gap available
- DEMOGEN benchmark: 216 ResNet-32 + 216 NIN models on CIFAR-10, 324 ResNet-32 on CIFAR-100
- Code at google-research/google-research/tree/master/demogen
- Normalization formula: (raw - low) / (high - low) maps to [0,1]

### Archon Code Examples

**Note:** Archon MCP unavailable. Code patterns from web research:

**Pattern 1: Saturation Index Computation**
- evaleval/benchmark-saturation uses temporal trajectory analysis
- Outputs CSV results and JSON trajectory files
- Command: `python3 -m analyzer.src.leaderboards.helm.run_metrics`

**Pattern 2: Entropy-based Metrics**
- Standard approach: Shannon entropy over improvement distribution
- Windowing: 6-month rolling window for smoothing conference clustering
- Normalization: Divide by difficulty proxy (class count as simplest)

### Exa GitHub Implementations

**Repository 1**: [paperswithcode/paperswithcode-data](https://github.com/paperswithcode/paperswithcode-data)
- **URL**: https://github.com/paperswithcode/paperswithcode-data
- **Relevance**: Official archived dataset of all PWC SOTA histories
- **Data Format**: JSON in sota-extractor format
- **Note**: PWC shut down July 2025, but historical data archived
- **Key Code**: Load JSON into Python classes via sota-extractor package

**Repository 2**: [evaleval/benchmark-saturation](https://github.com/evaleval/benchmark-saturation)
- **URL**: https://github.com/evaleval/benchmark-saturation
- **Relevance**: Saturation metrics implementation for ML benchmarks
- **Architecture**: Python package with analyzer/src/ structure
- **Metrics**: S_index, temporal analysis, leaderboard snapshots

**Repository 3**: [nsfzyzz/Generalization_metrics_for_NLP](https://github.com/nsfzyzz/Generalization_metrics_for_NLP)
- **URL**: https://github.com/nsfzyzz/Generalization_metrics_for_NLP
- **Relevance**: KDD 2023 generalization gap prediction without training data
- **Useful for**: Understanding gap measurement methodology

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a novel metric (DNSI) - no author implementation exists**

This hypothesis proposes a NEW metric (DNSI = Difficulty-Normalized Saturation Index). No prior implementation exists to reproduce. Implementation must be built from scratch using:
1. PapersWithCode archived data (paperswithcode-data repo)
2. Entropy computation (scipy.stats.entropy)
3. 6-month windowing (pandas rolling)
4. Class count normalization (from benchmark metadata)

**Recommended Implementation Path:**
- Primary: Custom implementation using paperswithcode-data JSON + scipy/numpy
- Fallback: Adapt evaleval/benchmark-saturation S_index computation pattern
- Justification: DNSI is novel metric; no existing implementation to follow. Build from first principles using archived PWC data.

### Code Analysis (Serena MCP)

**Note:** Serena MCP not required for this hypothesis. No existing codebase to analyze - DNSI is a novel metric requiring new implementation.

---

## Experiment Specification

### Dataset

**Name:** PapersWithCode SOTA Histories (Archived)
**Type:** programmatic-api
**Source:** https://github.com/paperswithcode/paperswithcode-data

**Description:**
Historical SOTA leaderboard data from Papers With Code, covering benchmarks with dense improvement histories. Target benchmarks for DNSI computation:

| Benchmark | Domain | Est. SOTA Entries | Class Count (Difficulty Proxy) |
|-----------|--------|-------------------|-------------------------------|
| ImageNet | Vision | >500 | 1000 |
| CIFAR-10 | Vision | >200 | 10 |
| CIFAR-100 | Vision | >150 | 100 |
| MNIST | Vision | >100 | 10 |
| GLUE | NLP | >200 | varies |
| SQuAD | NLP | >150 | N/A (span extraction) |
| WMT (En-De) | Translation | >100 | N/A (use vocab size) |
| COCO Detection | Vision | >200 | 80 |

**Selection Criteria:**
- >50 SOTA entries over >3 years (dense history requirement)
- Ground truth generalization gap data available for subset (ImageNet-V2, CIFAR-10.2, ObjectNet, HANS)

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (git clone + JSON parse)
- Identifier: `paperswithcode/paperswithcode-data`
- Code:
```python
import json
import subprocess

# Clone archived data
subprocess.run(["git", "clone", "https://github.com/paperswithcode/paperswithcode-data.git", "data/pwc"])

# Load evaluation tables
with open("data/pwc/evaluation-tables.json", "r") as f:
    eval_tables = json.load(f)

# Filter benchmarks with >50 entries
dense_benchmarks = [b for b in eval_tables if len(b.get("results", [])) > 50]
```

### Models

#### Baseline Model

**Name:** N/A - This is a metric computation experiment, not a model training experiment

**Description:**
This EXISTENCE hypothesis tests whether DNSI can be computed reliably from data. There is no ML model to train. The "baseline" comparison is against alternative saturation metrics:

1. **Raw Entropy** (H): Shannon entropy of improvement distribution without normalization
2. **Improvement Rate** (IR): Mean accuracy gain per year
3. **Time Since Last SOTA** (TSLS): Days since last improvement

**Loading Information** (for Phase 4 download):
- Method: N/A (no pretrained model)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** DNSI Computation Pipeline (not a neural network)

**Core Mechanism Implementation:**

```python
import numpy as np
from scipy.stats import entropy
from collections import defaultdict
from datetime import datetime, timedelta

class DNSIComputer:
    """
    Difficulty-Normalized Saturation Index
    DNSI = H_observed / H_expected
    where H_expected = log(difficulty_proxy)
    """
    def __init__(self, window_months: int = 6):
        self.window_months = window_months
    
    def compute_dnsi(self, sota_history: list, difficulty_proxy: int) -> float:
        """
        Args:
            sota_history: List of (date, accuracy) tuples, sorted by date
            difficulty_proxy: Number of classes (or vocab size for NLP)
        Returns:
            DNSI value in [0, 1], or None if insufficient data
        """
        if len(sota_history) < 10 or difficulty_proxy <= 1:
            return None
        
        # Compute 6-month windowed improvements
        improvements = self._compute_windowed_improvements(sota_history)
        if len(improvements) < 5:
            return None
        
        # Shannon entropy of improvement distribution
        h_observed = entropy(improvements + 1e-10)  # Add epsilon for stability
        
        # Expected entropy based on difficulty (uniform distribution)
        h_expected = np.log(difficulty_proxy)
        
        # DNSI: normalized saturation
        dnsi = h_observed / h_expected if h_expected > 0 else None
        return dnsi
    
    def _compute_windowed_improvements(self, sota_history: list) -> np.ndarray:
        """Aggregate improvements into 6-month windows"""
        window_delta = timedelta(days=self.window_months * 30)
        start_date = sota_history[0][0]
        end_date = sota_history[-1][0]
        
        improvements = []
        current = start_date
        while current < end_date:
            window_end = current + window_delta
            window_improvements = [
                sota_history[i][1] - sota_history[i-1][1]
                for i in range(1, len(sota_history))
                if current <= sota_history[i][0] < window_end
                and sota_history[i][1] > sota_history[i-1][1]
            ]
            improvements.append(sum(window_improvements) if window_improvements else 0)
            current = window_end
        
        return np.array(improvements)
```

### Training Protocol

**N/A - This is not a training experiment**

This EXISTENCE hypothesis validates metric computation, not model training. Protocol:

1. **Data Loading**: Clone paperswithcode-data, parse JSON
2. **Benchmark Filtering**: Select benchmarks with >50 SOTA entries, >3 year history
3. **DNSI Computation**: Apply DNSIComputer to each benchmark
4. **Baseline Computation**: Compute Raw Entropy, Improvement Rate, TSLS for comparison
5. **Validation**: Check DNSI produces valid (non-null) values for >50% of benchmarks

**Parameters:**
- Window size: 6 months (fixed)
- Minimum SOTA entries: 50
- Minimum history span: 3 years
- Difficulty proxy: class count (vision), vocab size (NLP)

**Seeds:** 1 (deterministic computation, no randomness)

### Evaluation

**Primary Metric:** DNSI Computation Success Rate

| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Computation Success Rate | % of target benchmarks with valid DNSI | >50% |
| Value Range Validity | DNSI values in expected [0, 2] range | 100% of computed |
| Benchmark Coverage | # of benchmarks with dense enough history | ≥8 |

**Success Criteria (EXISTENCE PoC):**
- DNSI computed successfully for >50% of target benchmarks (≥4 of 8)
- All computed DNSI values are finite and in plausible range
- Code runs without error

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: metric_computation (not classification/regression)
- Library: scipy.stats (entropy), numpy
- Code:
```python
from scipy.stats import entropy
import numpy as np

def validate_dnsi(dnsi_value):
    """Check DNSI is valid"""
    return dnsi_value is not None and np.isfinite(dnsi_value) and 0 <= dnsi_value <= 2
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing DNSI computation success rate vs 50% threshold

#### Additional Figures (LLM Autonomous)

1. **DNSI Distribution**: Histogram of computed DNSI values across benchmarks
2. **Benchmark Coverage**: Bar chart showing # SOTA entries per benchmark (with 50-entry threshold line)
3. **DNSI vs Raw Entropy Scatter**: Compare DNSI to unnormalized entropy
4. **Timeline Heatmap**: DNSI evolution over rolling windows for top benchmarks

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. DNSI computed successfully for >50% of target benchmarks

**Mechanism Verification:**
- Pre-condition: paperswithcode-data repo cloneable and JSON parseable
- Activation Indicator: `print(f"[DNSI] Computing for {benchmark_name}...")` before each computation
- Success Signal: `print(f"[DNSI] SUCCESS: {benchmark_name} = {dnsi_value:.4f}")`
- Failure Detection: `print(f"[DNSI] FAILED: {benchmark_name} - insufficient data")` on None return

---

## Appendix: Reference Implementations

### Source 1: evaleval/benchmark-saturation
- **URL**: https://github.com/evaleval/benchmark-saturation
- **Relevance**: S_index computation pattern, temporal trajectory analysis
- **Key Insight**: Framework structure (analyzer/src/metrics/)

### Source 2: paperswithcode/paperswithcode-data
- **URL**: https://github.com/paperswithcode/paperswithcode-data
- **Relevance**: Archived SOTA history data source
- **Key Insight**: JSON sota-extractor format

### Source 3: scipy.stats.entropy
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html
- **Relevance**: Shannon entropy computation
- **Key Insight**: Handles probability distributions, supports base parameter

### Source 4: Benchmark Saturation Paper (arXiv:2203.04592)
- **Title**: Mapping global dynamics of benchmark creation and saturation in artificial intelligence
- **Relevance**: Prior work on benchmark saturation patterns
- **Key Insight**: ~1/3 of SOTA results captured by PWC

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design started
- 2026-08-28: Research completed (web search, no MCP available)
- 2026-08-28: Experiment specification synthesized

---

*Tools Used: WebSearch, WebFetch (Archon/Exa/Serena MCP unavailable in ablation)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
