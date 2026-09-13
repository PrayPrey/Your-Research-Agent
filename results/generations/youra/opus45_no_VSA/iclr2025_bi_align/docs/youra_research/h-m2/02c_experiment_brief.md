# Experiment Design: H-M2

**Date:** 2026-08-08
**Author:** Anonymous
**Hypothesis Statement:** BAI and reward scores show systematic disagreement with ≥20% of response pairs falling in high-BAI/low-reward or low-BAI/high-reward quartiles.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing systematic disagreement between BAI and reward scores.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1

### Gate Condition
SHOULD_WORK: Failure triggers reflection, not pipeline stop. Success strengthens main hypothesis that BAI captures independent dimension from reward.

---

## Continuation Context

H-E1 validated that four agency proxies (clarifying questions, option enumeration, epistemic hedging, explicit deferral) can be reliably extracted with Mean AUROC 0.9836 (all proxies > 0.7).

### Previous Hypothesis Results
- **H-E1 VALIDATED**: TF-IDF + LogisticRegression achieved mean AUROC 0.9836
- Clarifying Question: 0.9949, Option Enumeration: 0.9840, Epistemic Hedging: 0.9880, Explicit Deferral: 0.9676
- **Reuse**: Same datasets (HH-RLHF, RewardBench), same proxy extraction pipeline

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Reward Model Disagreement Analysis**
- Limited direct matches for BAI-reward disagreement
- OpenAI instruction-following work provides context on RLHF reward modeling
- Recommendation: Use established RewardBench infrastructure

**Query 2: RLHF Quartile Evaluation**
- Standard evaluation uses accuracy (chosen > rejected rate)
- Quartile-based analysis is novel contribution of this hypothesis

### Archon Code Examples

- Model loading patterns via HuggingFace documented
- Metric computation via torchmetrics/sklearn confirmed

### Exa GitHub Implementations

**Repository 1**: allenai/reward-bench
- **URL**: https://github.com/allenai/reward-bench
- **Relevance**: Core infrastructure for reward model evaluation
- **Key Features**:
  - Common inference code for variety of reward models (Starling, PairRM, OpenAssistant, DPO)
  - Dataset formatting for HH-RLHF and other preference sets
  - Scoring: `score(prompt-chosen)` vs `score(prompt-rejected)` comparison
- **Evaluation Pattern**:
  ```python
  # From RewardBench - accuracy computation
  # True label when chosen_score > rejected_score
  accuracy = (chosen_scores > rejected_scores).mean()
  ```

**Repository 2**: LewallenAE/rlhf-eval
- **URL**: https://github.com/LewallenAE/rlhf-eval
- **Relevance**: End-to-end RLHF data quality evaluation on HH-RLHF
- **Key Findings**:
  - 160,800 preference pairs in HH-RLHF
  - Clean vs unfiltered comparison shows ~62% test accuracy
  - Reward gap analysis: clean=0.2282, unfiltered=0.3014
- **Pattern**: Bradley-Terry loss for reward model training

**Research Papers**:
- "Elephant in the Room" (arxiv:2409.19024): Investigated HH-RLHF quality, curated CHH-RLHF
- RewardBench paper (arxiv:2403.13787): Standard benchmark with Prior Sets including Anthropic Helpful split

### 🎯 Implementation Priority Assessment

**CRITICAL: This is novel analysis, not paper reproduction**

This hypothesis performs NEW analysis (BAI-reward quartile disagreement) on existing datasets. No author implementation to replicate.

**Recommended Implementation Path:**
- Primary: Build on H-E1 proxy extraction pipeline + simple reward scoring
- Fallback: Use RewardBench infrastructure for reward model inference
- Justification: H-E1 already validates proxy extraction; this step adds reward scoring and quartile analysis

### Code Analysis (Serena MCP)

*Not required* - Implementation pattern is straightforward statistical analysis, not complex neural architecture.

---

## Experiment Specification

### Dataset

**Primary Dataset**: HH-RLHF (Anthropic)
- **Type**: standard
- **Source**: Hugging Face `Anthropic/hh-rlhf`
- **Size**: ~160,800 preference pairs
- **Split**: Use test split for evaluation (~8,500 pairs)
- **Preprocessing**: Extract chosen/rejected response pairs

**Secondary Dataset**: RewardBench (Allen AI)
- **Type**: standard  
- **Source**: Hugging Face `allenai/reward-bench`
- **Size**: Multiple subsets (Chat, Chat Hard, Safety, Reasoning, Prior Sets)
- **Split**: Full evaluation set
- **Preprocessing**: Format as prompt-chosen-rejected trios

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `Anthropic/hh-rlhf`, `allenai/reward-bench`
- Code:
  ```python
  from datasets import load_dataset
  
  # HH-RLHF
  hh_rlhf = load_dataset("Anthropic/hh-rlhf", split="test")
  
  # RewardBench
  reward_bench = load_dataset("allenai/reward-bench")
  ```

### Models

#### Baseline Model

**Component 1: BAI Proxy Extraction** (from H-E1)
- Architecture: TF-IDF + LogisticRegression
- Pre-trained: Use H-E1 trained models (AUROC 0.9836)
- Purpose: Extract 4 agency proxy scores per response

**Component 2: Reward Scoring**
- Architecture: Pre-trained reward model
- Options (in order of preference):
  1. `OpenAssistant/reward-model-deberta-v3-large-v2` (HF)
  2. `berkeley-nest/Starling-RM-7B-alpha` (if GPU available)
  3. DPO implicit reward from `stabilityai/stablelm-zephyr-3b`

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `OpenAssistant/reward-model-deberta-v3-large-v2`
- Code:
  ```python
  from transformers import AutoModelForSequenceClassification, AutoTokenizer
  
  reward_model = AutoModelForSequenceClassification.from_pretrained(
      "OpenAssistant/reward-model-deberta-v3-large-v2"
  )
  tokenizer = AutoTokenizer.from_pretrained(
      "OpenAssistant/reward-model-deberta-v3-large-v2"
  )
  ```

#### Proposed Model

**Architecture:** BAI-Reward Disagreement Analyzer

This is an ANALYSIS experiment, not a model training experiment. The "proposed model" is the analysis pipeline.

**Core Mechanism Implementation:**

```python
# Core Mechanism: BAI-Reward Quartile Disagreement Analysis
# Based on: H-E1 proxy extraction + RewardBench scoring pattern

import numpy as np
from sklearn.preprocessing import StandardScaler

def compute_bai_score(response: str, proxy_models: dict) -> float:
    """
    Compute length-normalized BAI from 4 agency proxies.
    Uses H-E1 validated TF-IDF+LogReg models.
    """
    proxy_scores = []
    for proxy_name, model in proxy_models.items():
        # TF-IDF transform + predict_proba
        score = model.predict_proba(response)[0, 1]
        proxy_scores.append(score)
    
    # Aggregate: mean of 4 proxies
    raw_bai = np.mean(proxy_scores)
    
    # Length normalization (residualize against log-length)
    # ponytail: simple division, regression residuals if bias detected
    normalized_bai = raw_bai / (1 + 0.1 * np.log(len(response.split())))
    return normalized_bai

def compute_reward_score(prompt: str, response: str, reward_model, tokenizer) -> float:
    """
    Compute reward score using pre-trained reward model.
    """
    inputs = tokenizer(prompt + response, return_tensors="pt", truncation=True)
    outputs = reward_model(**inputs)
    return outputs.logits[0, 0].item()

def compute_disagreement_rate(bai_scores: np.ndarray, reward_scores: np.ndarray) -> dict:
    """
    Compute quartile-based disagreement rate.
    Target: ≥20% pairs in high-BAI/low-reward OR low-BAI/high-reward quartiles.
    """
    # Standardize for fair quartile comparison
    bai_z = StandardScaler().fit_transform(bai_scores.reshape(-1, 1)).flatten()
    reward_z = StandardScaler().fit_transform(reward_scores.reshape(-1, 1)).flatten()
    
    # Define quartiles
    bai_q25, bai_q75 = np.percentile(bai_z, [25, 75])
    reward_q25, reward_q75 = np.percentile(reward_z, [25, 75])
    
    # Count disagreement cases
    high_bai_low_reward = ((bai_z >= bai_q75) & (reward_z <= reward_q25)).sum()
    low_bai_high_reward = ((bai_z <= bai_q25) & (reward_z >= reward_q75)).sum()
    
    total_pairs = len(bai_scores)
    disagreement_count = high_bai_low_reward + low_bai_high_reward
    disagreement_rate = disagreement_count / total_pairs
    
    return {
        "disagreement_rate": disagreement_rate,
        "high_bai_low_reward": high_bai_low_reward,
        "low_bai_high_reward": low_bai_high_reward,
        "total_pairs": total_pairs,
        "passes_threshold": disagreement_rate >= 0.20
    }
```

### Training Protocol

**This is an ANALYSIS experiment - no model training required.**

**Pipeline Steps:**
1. Load H-E1 trained proxy models (4 TF-IDF+LogReg classifiers)
2. Load pre-trained reward model (OpenAssistant DeBERTa)
3. For each response in test set:
   - Compute BAI score using proxy ensemble
   - Compute reward score using reward model
4. Analyze quartile distribution
5. Compute disagreement rate

**Hyperparameters:**
- BAI aggregation: mean of 4 proxy scores
- Length normalization: divide by (1 + 0.1 * log(word_count))
- Quartile threshold: 25th and 75th percentiles
- Random seed: 42

### Evaluation

**Primary Metric:** Disagreement Rate
- Definition: Fraction of response pairs where BAI and reward scores fall in opposite quartiles
- Formula: (high-BAI/low-reward + low-BAI/high-reward) / total_pairs

**Success Criteria:**
- **PASS**: Disagreement rate ≥ 20%
- **PARTIAL**: Disagreement rate ∈ [10%, 20%)
- **FAIL**: Disagreement rate < 10%

**Secondary Metrics:**
- Pearson correlation between BAI and reward scores (expect |r| < 0.5 for independence)
- Per-quartile distribution counts
- Length correlation check (verify length normalization works)

**Expected Baseline:**
- If BAI and reward were independent: ~12.5% disagreement (6.25% per corner × 2)
- If BAI and reward were identical: 0% disagreement
- Target 20% suggests systematic meaningful divergence

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (not classification)
- Library: numpy, scipy.stats, sklearn.preprocessing
- Code:
  ```python
  import numpy as np
  from scipy.stats import pearsonr, spearmanr
  from sklearn.preprocessing import StandardScaler
  
  # Correlation
  pearson_r, pearson_p = pearsonr(bai_scores, reward_scores)
  
  # Disagreement rate - see core mechanism above
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing disagreement rate vs 20% threshold

#### Additional Figures (LLM Autonomous)
- **Scatter Plot**: BAI score (x) vs Reward score (y) with quadrant lines at Q25/Q75
- **2D Histogram/Heatmap**: Density of BAI-Reward pairs across quartile grid
- **Distribution Plots**: Histograms of BAI and reward score distributions
- **Disagreement Case Examples**: Table of top-10 high-BAI/low-reward and low-BAI/high-reward examples

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True - Quartile disagreement analysis is well-defined mathematical operation
- `mechanism_isolatable`: True - Disagreement rate is computed from BAI and reward, can verify each component
- `baseline_measurable`: True - Random baseline ~12.5%, identical baseline 0%

### Architecture Compatibility
- H-E1 proxy models: Verified working (AUROC 0.9836)
- Reward model: Standard HuggingFace interface, well-tested
- Analysis pipeline: Pure numpy/sklearn operations

### Activation Indicators
- `mechanism_log_message`: "Computing BAI scores for N responses...", "Computing reward scores...", "Disagreement rate: X%"
- `tensor_shape_change`: BAI scores shape (N,), Reward scores shape (N,)
- `metric_delta_expected`: Disagreement rate should be between 10-40% (not 0% or 50%+)

### Failure Detection
- If disagreement_rate == 0.0: BAI and reward perfectly correlated (unlikely, check for bugs)
- If disagreement_rate > 0.5: Something wrong with quartile computation
- If pearson_r > 0.9: BAI essentially equals reward (hypothesis fails but code correct)
- If BAI score variance near 0: Proxy models not discriminating

### Mechanism Verification Code
```python
def verify_mechanism(results: dict) -> dict:
    """Verify mechanism is working correctly."""
    checks = {
        "bai_variance_ok": results["bai_std"] > 0.01,
        "reward_variance_ok": results["reward_std"] > 0.01,
        "disagreement_in_range": 0.0 < results["disagreement_rate"] < 0.5,
        "sample_count_ok": results["total_pairs"] >= 500,
    }
    all_passed = all(checks.values())
    return {"verification_passed": all_passed, "checks": checks}
```

### Success Criteria
- `hypothesis_support_metric`: disagreement_rate
- `hypothesis_support_threshold`: 0.20 (20%)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Disagreement rate ≥ 20% (at least 20% of pairs in high-BAI/low-reward OR low-BAI/high-reward quartiles)

---

## Appendix: Reference Implementations

### Primary References

1. **RewardBench** (Allen AI)
   - URL: https://github.com/allenai/reward-bench
   - Used for: Reward model inference patterns, dataset structure
   - Key file: `scripts/run_rm.py`

2. **RLHF-Eval** (LewallenAE)
   - URL: https://github.com/LewallenAE/rlhf-eval
   - Used for: HH-RLHF data handling, reward gap analysis patterns
   
3. **H-E1 Implementation** (This project)
   - Location: `h-e1/code/`
   - Used for: Proxy extraction pipeline (TF-IDF + LogReg)

### Research Papers

1. Lambert et al. (2024). "RewardBench: Evaluating Reward Models for Language Modeling"
   - ArXiv: 2403.13787
   - Relevance: Standard reward model evaluation methodology

2. "Elephant in the Room: Unveiling the Impact of Reward Model Quality in Alignment"
   - ArXiv: 2409.19024
   - Relevance: HH-RLHF data quality analysis, clean CHH-RLHF curation

3. Bai et al. (2022). "Training a Helpful and Harmless Assistant with RLHF"
   - Relevance: Original HH-RLHF dataset

### Code Patterns Used

```python
# Pattern 1: Reward model inference (from RewardBench)
def score_response(model, tokenizer, prompt, response):
    inputs = tokenizer(prompt + response, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.logits[0, 0].item()

# Pattern 2: Quartile-based analysis (sklearn standard)
from sklearn.preprocessing import StandardScaler
standardized = StandardScaler().fit_transform(scores.reshape(-1, 1))
q25, q75 = np.percentile(standardized, [25, 75])
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-08

### Workflow History for This Hypothesis
- 2026-08-08: Phase 2C experiment design started
- 2026-08-08: Archon KB search completed (sparse results for novel analysis)
- 2026-08-08: Exa GitHub search completed (RewardBench, rlhf-eval found)
- 2026-08-08: Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
