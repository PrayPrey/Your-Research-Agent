# Experiment Design: H-E1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** Moderate inter-benchmark correlations (r > baseline AND r < 0.7) exist between TruthfulQA, HaluEval, and FactScore across N≥30 diverse LLMs
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**Type:** MUST_WORK
**Pass Condition:** r(cross-benchmark) > r(MMLU-Physics vs HaluEval) AND r < 0.7
**Fail Action:** STOP - entire hypothesis fails; multi-dimensionality not supported

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous hypothesis results to incorporate.

### Previous Hypothesis Results (if applicable)
*Not applicable - H-E1 is the foundation hypothesis with no prerequisites.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Limited Direct Results:** Archon KB did not contain specific LLM truthfulness benchmark correlation studies. Primary sources come from Exa GitHub search.

**General Findings:**
- No existing correlation analysis frameworks for TruthfulQA/HaluEval/FactScore
- This represents a novel analysis direction

### Archon Code Examples

No directly relevant code examples found in Archon KB for this specific meta-analysis task.

### Exa GitHub Implementations

**Repository 1**: EleutherAI/lm-evaluation-harness (⭐ 12,243)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Backend for HuggingFace Open LLM Leaderboard; supports TruthfulQA evaluation
- **Tasks Supported**: `truthfulqa_mc1`, `truthfulqa_mc2`, `truthfulqa_gen`
- **Key Code**:
  ```bash
  pip install "lm_eval[hf]"
  lm_eval --model hf --model_args pretrained=MODEL_NAME --tasks truthfulqa_mc2 --device cuda:0
  ```
- **Used For**: TruthfulQA evaluation methodology

**Repository 2**: shmsw25/FActScore (⭐ 439)
- **URL**: https://github.com/shmsw25/FActScore
- **Relevance**: Official EMNLP 2023 implementation for factual precision evaluation
- **Key Code**:
  ```python
  from factscore.factscorer import FactScorer
  fs = FactScorer(openai_key="...")
  out = fs.get_score(topics, generations, gamma=10)
  print(out["score"])  # FActScore
  ```
- **Used For**: FactScore metric computation

**Repository 3**: RUCAIBox/HaluEval (⭐ 568)
- **URL**: https://github.com/RUCAIBox/HaluEval
- **Relevance**: Official hallucination evaluation benchmark (35K samples)
- **Tasks**: QA, dialogue, summarization hallucination detection
- **Key Code**:
  ```python
  python evaluation/evaluate.py --task qa --model gpt-3.5-turbo
  ```
- **Used For**: HaluEval evaluation methodology

**Repository 4**: HuggingFace Open LLM Leaderboard
- **URL**: https://huggingface.co/datasets/open-llm-leaderboard/results
- **Relevance**: Pre-computed benchmark scores for 1000+ models
- **API Access**:
  ```python
  from huggingface_hub import HfApi
  api = HfApi()
  leaderboard = api.get_dataset_leaderboard("open-llm-leaderboard/results")
  ```
- **Used For**: Model population with existing benchmark scores

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a meta-analysis experiment, NOT a paper reproduction.**

This experiment analyzes correlation structure across existing benchmark scores. No mechanism implementation needed - we compute statistics over collected scores.

**Recommended Implementation Path:**
- Primary: Use Open LLM Leaderboard dataset for pre-computed scores where available
- Fallback: Run lm-evaluation-harness for missing TruthfulQA scores; use official repos for HaluEval/FactScore
- Justification: Pre-computed scores ensure reproducibility; official implementations for any gaps

### Code Analysis (Serena MCP)

*Not applicable - this is a statistical meta-analysis experiment, not a model architecture implementation.*

---

## Experiment Specification

### Dataset

**Type:** programmatic-api (NOT synthetic)
**Source:** Open LLM Leaderboard + Official Benchmark Repositories

**Primary Dataset: Model Benchmark Scores**
- **Name:** Multi-Benchmark Score Matrix
- **Type:** programmatic-api
- **Population:** N≥30 diverse LLMs from Open LLM Leaderboard
- **Diversity Requirements:**
  - Architectures: Llama, Mistral, Falcon, Phi, Qwen, etc.
  - Scales: 7B-70B parameters
  - Training: base, instruct, RLHF, DPO variants

**Benchmark Components:**
| Benchmark | Source | Size | Metric |
|-----------|--------|------|--------|
| TruthfulQA | lm-evaluation-harness | 817 questions | MC1/MC2 accuracy |
| HaluEval | RUCAIBox/HaluEval | 35K samples | Recognition accuracy |
| FactScore | shmsw25/FActScore | 500 entities | Factual precision % |
| MMLU (baseline) | lm-evaluation-harness | 14K questions | Accuracy |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace API + Official Repositories
- Identifier: `open-llm-leaderboard/results` + individual benchmark repos
- Code:
  ```python
  # Option 1: Pre-computed from leaderboard
  from huggingface_hub import HfApi
  api = HfApi()
  results = api.list_repo_files("open-llm-leaderboard/results")
  
  # Option 2: Direct evaluation
  # lm_eval --model hf --model_args pretrained=MODEL --tasks truthfulqa_mc2,mmlu
  ```

### Models

#### Baseline Model

**This is a correlation meta-analysis - no model training required.**

**Model Population (N≥30):**
- Source: Open LLM Leaderboard model list
- Selection Criteria: Models with scores on all 3 target benchmarks
- Diversity: Multiple architectures, scales, training approaches

**Loading Information** (for Phase 4 download):
- Method: HuggingFace API
- Identifier: Model list from leaderboard
- Code:
  ```python
  from datasets import load_dataset
  # Load leaderboard results
  results = load_dataset("open-llm-leaderboard/results", split="train")
  # Filter for models with all required benchmark scores
  ```

#### Proposed Model

**Architecture:** N/A - This is statistical analysis, not model modification

**Core Mechanism Implementation:**

```python
# Core Analysis: Inter-Benchmark Correlation Computation
# Based on: scipy.stats.spearmanr documentation

import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from itertools import combinations

class BenchmarkCorrelationAnalyzer:
    """
    Compute Spearman correlations between LLM benchmark scores.
    Tests whether truthfulness benchmarks measure independent dimensions.
    """
    def __init__(self, benchmark_scores: pd.DataFrame):
        # benchmark_scores: DataFrame with columns [model, truthfulqa, halueval, factscore, mmlu]
        self.scores = benchmark_scores
        self.benchmarks = ['truthfulqa', 'halueval', 'factscore']
        self.baseline_pair = ('mmlu_physics', 'halueval')  # unrelated-benchmark reference
    
    def compute_correlation_matrix(self) -> pd.DataFrame:
        """
        Returns: (n_benchmarks, n_benchmarks) correlation matrix
        """
        corr_matrix = self.scores[self.benchmarks].corr(method='spearman')
        return corr_matrix
    
    def compute_baseline_correlation(self) -> float:
        """Compute r(MMLU-Physics, HaluEval) as reference threshold."""
        r, p = spearmanr(
            self.scores[self.baseline_pair[0]], 
            self.scores[self.baseline_pair[1]],
            nan_policy='omit'
        )
        return r
    
    def evaluate_hypothesis(self) -> dict:
        """
        Returns: {passed: bool, correlations: dict, baseline: float}
        """
        corr_matrix = self.compute_correlation_matrix()
        baseline_r = self.compute_baseline_correlation()
        
        # Extract cross-benchmark correlations
        cross_correlations = {}
        for b1, b2 in combinations(self.benchmarks, 2):
            cross_correlations[f'{b1}_vs_{b2}'] = corr_matrix.loc[b1, b2]
        
        # Check hypothesis: baseline < r < 0.7 for all pairs
        passed = all(baseline_r < r < 0.7 for r in cross_correlations.values())
        
        return {
            'passed': passed,
            'correlations': cross_correlations,
            'baseline_r': baseline_r,
            'threshold_upper': 0.7
        }

# Integration: Run after collecting scores for N≥30 models
```

### Training Protocol

**N/A - This is a statistical analysis experiment, not model training.**

**Analysis Protocol:**
- **Step 1:** Collect benchmark scores for N≥30 models
- **Step 2:** Compute Spearman correlation matrix
- **Step 3:** Compute baseline reference correlation (MMLU-Physics vs HaluEval)
- **Step 4:** Evaluate hypothesis: baseline_r < r(cross-benchmark) < 0.7

**Computational Requirements:**
- No GPU required (statistical computation only)
- Estimated runtime: <1 hour (data collection may take longer if running evaluations)

**Seeds:** N/A (deterministic statistical analysis)

### Evaluation

**Primary Metrics:**
- Spearman correlation coefficient (r) between benchmark pairs
- Baseline reference: r(MMLU-Physics, HaluEval)

**Success Criteria (EXISTENCE PoC):**
1. Code runs without error
2. For all cross-benchmark pairs: r > baseline_r AND r < 0.7

**Expected Results (from hypothesis):**
- Cross-benchmark r: 0.3-0.6 range (moderate correlation)
- Baseline r: ~0.0-0.2 (near-zero for unrelated benchmarks)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation_analysis
- Library: scipy.stats, pandas
- Code:
  ```python
  from scipy.stats import spearmanr
  import pandas as pd
  
  # Pairwise correlation
  r, p = spearmanr(scores_a, scores_b, nan_policy='omit')
  
  # Full correlation matrix
  corr_matrix = df[benchmarks].corr(method='spearman')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing cross-benchmark correlations vs baseline threshold

#### Additional Figures (LLM Autonomous)

1. **Correlation Heatmap**: Full correlation matrix visualization
2. **Scatter Plots**: Pairwise benchmark score scatter plots with regression lines
3. **Model Diversity Distribution**: Histogram of model architectures/scales in sample

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. All cross-benchmark correlations satisfy: `baseline_r < r < 0.7`

**If ANY pair has r < baseline_r:** Benchmarks appear unrelated (noise, not independence)
**If ANY pair has r > 0.7:** Benchmarks measure same construct (single-factor hypothesis supported)

---

## Appendix: Reference Implementations

### A. Primary Sources

| Source | URL | Used For |
|--------|-----|----------|
| lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | TruthfulQA evaluation |
| FActScore | https://github.com/shmsw25/FActScore | Factual precision metric |
| HaluEval | https://github.com/RUCAIBox/HaluEval | Hallucination evaluation |
| Open LLM Leaderboard | https://huggingface.co/open-llm-leaderboard | Pre-computed scores |
| scipy.stats.spearmanr | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html | Correlation computation |

### B. Papers

| Paper | Citation | Relevance |
|-------|----------|-----------|
| TruthfulQA | Lin et al., ACL 2022 | Benchmark definition |
| HaluEval | Li et al., EMNLP 2023 | Benchmark definition |
| FActScore | Min et al., EMNLP 2023 | Benchmark definition |

### C. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Model population | Exa/API | Open LLM Leaderboard |
| TruthfulQA eval | Exa GitHub | lm-evaluation-harness |
| HaluEval eval | Exa GitHub | RUCAIBox/HaluEval |
| FactScore eval | Exa GitHub | shmsw25/FActScore |
| Correlation method | Exa/Docs | scipy.stats.spearmanr |
| Baseline definition | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- 2026-08-24: Phase 2C experiment design initiated
- 2026-08-24: MCP research completed (Archon KB, Exa GitHub)
- 2026-08-24: Experiment specification synthesized
- 2026-08-24: Phase 2C COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
