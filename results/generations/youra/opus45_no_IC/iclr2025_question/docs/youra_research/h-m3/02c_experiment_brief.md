# Experiment Design: H-M3

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Within-cluster benchmark pairs show successful threshold transfer (AUROC degradation ≤ 0.08)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests causal mechanism with statistical validation.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 PASS (same-family JS-div 0.0823 < 0.15, cross-family 0.4813)
**Gate Status:** SHOULD_WORK (fail_action: EXPLORE)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (PASS)

### Gate Condition
- **Pass Condition:** Mean within-cluster AUROC degradation ≤ 0.08
- **Secondary:** 95% CI upper bound < 0.12
- **Fail Action:** EXPLORE tighter cluster criteria

---

## Continuation Context

### Previous Hypothesis Results (H-M2)
- **Result:** PASS (p=0.0002)
- **Key Finding:** Same-family JS-divergence 0.0823 vs cross-family 0.4813 (5.8× separation)
- **Cluster Structure from H-E1:**
  - Cluster 1 (Factual Recall): TriviaQA, NQ, SQuAD
  - Cluster 2 (Entity/Claim): PopQA, HaluEval-QA, FEVER
- **Silhouette Score:** 0.8245 (k=2)

**Implications:** H-M3 tests whether this cluster structure predicts successful threshold transfer.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Threshold transfer AUROC calibration**
- No directly relevant results for threshold transfer in hallucination detection context
- General calibration patterns found but not specific to cross-benchmark transfer

**Query 2: Semantic entropy hallucination detection**
- Found reference to semantic uncertainty methods
- AUROC ~0.79 reported as standard performance metric

### Archon Code Examples

- Calibration code patterns found (optimum-quanto) but not specific to threshold transfer
- No direct code examples for cross-benchmark calibration transfer

### Exa GitHub Implementations

**Repository 1:** jlko/semantic_uncertainty (Official Implementation)
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Relevance:** Official codebase for Nature paper on semantic entropy hallucination detection
- **Architecture:** Three-stage pipeline
  1. `generate_answers.py`: Sample responses with likelihoods/hidden states
  2. `compute_uncertainty_measures.py`: Compute semantic entropy
  3. `analyze_results.py`: Compute AUROC and AURAC metrics

**Key Code:**
```python
# From generate_answers.py
python generate_answers.py --model_name=$MODEL --dataset=$DATASET $EXTRA_CFG

# Supported models: Llama-2-7b, Llama-2-13b, Llama-2-70b, Mistral-7B-v0.1
# Supported datasets: trivia_qa, squad, bioasq, nq, svamp
```

**Training/Evaluation Config:**
- Generations: 10 per query
- Temperature: 1.0 for sampling
- Entailment model: DeBERTa-v3-large (or gpt-3.5 for sentence-length)
- Metrics: AUROC (primary), AURAC (secondary)

**Reported Performance:**
- Average AUROC: 0.790 across 30 model-dataset combinations
- Stable across model families (0.78-0.81 AUROC)

**Repository 2:** jlko/long_hallucinations
- **URL:** https://github.com/jlko/long_hallucinations
- **Relevance:** Paragraph-length experiments for same paper
- **Models:** QADebertaEntailment, SelfCheckBaseline, PTrueOriginalBaseline

### 🎯 Implementation Priority Assessment

**CRITICAL: Using official author implementation**

**Recommended Implementation Path:**
- Primary: Adapt `jlko/semantic_uncertainty` for cross-benchmark threshold transfer
- Fallback: Implement threshold calibration on top of semantic entropy outputs
- Justification: Official Nature paper implementation ensures reproducibility

### Code Analysis (Serena MCP)

Not applicable - using external GitHub implementation, no local codebase to analyze.

---

## Experiment Specification

### Dataset

**Multi-Benchmark Suite (from H-E1/H-M2 validated clusters)**

| Benchmark | Cluster | Family | Source | Split |
|-----------|---------|--------|--------|-------|
| TriviaQA | 1 | Factual Recall | HuggingFace: `trivia_qa` | validation (full) |
| Natural Questions | 1 | Factual Recall | HuggingFace: `natural_questions` | validation (full) |
| SQuAD | 1 | Factual Recall | HuggingFace: `squad` | validation (full) |
| PopQA | 2 | Entity/Claim | HuggingFace: `akariasai/PopQA` | test (full) |
| HaluEval-QA | 2 | Entity/Claim | HuggingFace: `pminervini/HaluEval` | qa_samples (full) |
| FEVER | 2 | Entity/Claim | HuggingFace: `fever` | paper_dev (full) |

**Within-Cluster Pairs (H-M3 Test Set):**
- Cluster 1: TriviaQA↔NQ, TriviaQA↔SQuAD, NQ↔SQuAD (3 pairs)
- Cluster 2: PopQA↔HaluEval, PopQA↔FEVER, HaluEval↔FEVER (3 pairs)
- **Total:** 6 within-cluster pairs

**Sample Sizes (per benchmark):**
- Use 1000 queries per benchmark (consistent with H-E1 protocol)
- Train/calibration: 70% (700 queries)
- Test/evaluation: 30% (300 queries)
- **Total evaluation samples:** 1800 (300 × 6 target benchmarks)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: See table above
- Code:
```python
from datasets import load_dataset

# Example for TriviaQA
trivia_qa = load_dataset("trivia_qa", "rc", split="validation[:1000]")

# Example for Natural Questions
nq = load_dataset("natural_questions", split="validation[:1000]")

# Example for SQuAD
squad = load_dataset("squad", split="validation[:1000]")

# Example for PopQA
popqa = load_dataset("akariasai/PopQA", split="test[:1000]")

# Example for HaluEval-QA
halueval = load_dataset("pminervini/HaluEval", "qa_samples", split="data[:1000]")

# Example for FEVER
fever = load_dataset("fever", "v1.0", split="paper_dev[:1000]")
```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (consistent with H-E1, H-M1, H-M2)
**Source:** `meta-llama/Llama-2-7b-hf`
**Justification:** Same model used throughout hypothesis chain for controlled comparison

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture:** Baseline + Threshold Transfer Mechanism

**Core Mechanism:** Calibrate semantic entropy threshold on source benchmark, apply to target benchmark within same cluster.

### Core Mechanism Implementation

```python
# Core Mechanism: Within-Cluster Threshold Transfer
# Based on: jlko/semantic_uncertainty + calibration theory

def compute_semantic_entropy(model, tokenizer, query, n_generations=10, temperature=1.0):
    """
    Generate n responses and compute semantic entropy via entailment clustering.
    Returns: float semantic_entropy value
    """
    generations = []
    for _ in range(n_generations):
        output = model.generate(query, temperature=temperature, do_sample=True)
        generations.append(tokenizer.decode(output))
    
    # Cluster by bidirectional entailment (DeBERTa-v3-large)
    clusters = cluster_by_entailment(generations)
    
    # Compute entropy over cluster distribution
    probs = [len(c) / n_generations for c in clusters]
    entropy = -sum(p * log(p) for p in probs if p > 0)
    return entropy

def calibrate_threshold(entropies, labels, target_fpr=0.1):
    """
    Find threshold on source benchmark that achieves target FPR.
    Returns: optimal threshold value
    """
    fpr, tpr, thresholds = roc_curve(labels, entropies)
    idx = np.argmin(np.abs(fpr - target_fpr))
    return thresholds[idx]

def evaluate_transfer(source_threshold, target_entropies, target_labels):
    """
    Apply source-calibrated threshold to target benchmark.
    Returns: AUROC on target
    """
    predictions = (target_entropies > source_threshold).astype(int)
    return roc_auc_score(target_labels, target_entropies)

def compute_auroc_degradation(source_auroc, target_auroc):
    """
    Compute degradation = source_auroc - target_auroc
    Positive = performance dropped, Negative = performance improved
    """
    return source_auroc - target_auroc
```

### Training Protocol

**No training required** - This is an evaluation/transfer experiment.

**Semantic Entropy Computation Protocol:**
- Generations per query: 10
- Temperature: 1.0
- Entailment model: DeBERTa-v3-large
- Source: Kuhn et al. (2024) Nature paper defaults

**Threshold Calibration Protocol:**
- Split: 70% calibration, 30% evaluation
- Calibration method: Find threshold at target FPR (0.1) on source benchmark
- Transfer: Apply calibrated threshold to target benchmark

**Seeds:** 1 (fixed seed=42 for reproducibility)

### Evaluation

**Primary Metric:** AUROC degradation per within-cluster pair

| Metric | Definition | Success Criterion |
|--------|------------|-------------------|
| AUROC_source | Area under ROC on source 30% test | Baseline reference |
| AUROC_target | Area under ROC on target 30% test | Transfer performance |
| Degradation | AUROC_source - AUROC_target | ≤ 0.08 (primary) |

**Aggregation:**
- Mean degradation across 6 within-cluster pairs
- 95% confidence interval via bootstrap (1000 samples)

**Success Criteria:**
- **Primary:** Mean within-cluster AUROC degradation ≤ 0.08
- **Secondary:** 95% CI upper bound < 0.12

**Expected Baseline Performance:**
- In-distribution AUROC: ~0.79 (from Kuhn et al. 2024)
- Source: Nature paper reports 0.790 average across 30 model-dataset combinations

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (correct vs hallucinated)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score, roc_curve
import numpy as np

def compute_auroc(labels, scores):
    return roc_auc_score(labels, scores)

def bootstrap_ci(degradations, n_bootstrap=1000, ci=0.95):
    """Compute bootstrap confidence interval for mean degradation."""
    means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(degradations, size=len(degradations), replace=True)
        means.append(np.mean(sample))
    lower = np.percentile(means, (1 - ci) / 2 * 100)
    upper = np.percentile(means, (1 + ci) / 2 * 100)
    return lower, upper
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing AUROC degradation for each within-cluster pair with 0.08 threshold line

#### Additional Figures (LLM Autonomous)
- **Degradation Distribution**: Box plot of within-cluster vs cross-cluster degradations (preview of H-M4)
- **Transfer Matrix Heatmap**: 6×6 matrix showing transfer AUROC for all benchmark pairs
- **Cluster Visualization**: Scatter plot showing benchmarks colored by cluster with transfer arrows

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** Threshold transfer mechanism exists (calibrate on source, apply to target)
- **mechanism_isolatable:** YES - threshold value is explicit and transferable
- **baseline_measurable:** YES - in-distribution AUROC provides baseline reference

### Architecture Compatibility
- **Compatibility:** Full - uses same semantic entropy pipeline as H-E1/H-M1/H-M2
- **Integration Point:** After entropy computation, before threshold application
- **No architectural changes required** - only evaluation protocol changes

### Activation Indicators
- **mechanism_log_message:** "Applying threshold {threshold:.4f} from {source} to {target}"
- **tensor_shape_change:** N/A (threshold is scalar)
- **metric_delta_expected:** AUROC degradation should be small (≤0.08) for within-cluster pairs

### Mechanism Verification Code
```python
def verify_mechanism_activated(results):
    """
    Verify threshold transfer mechanism is working correctly.
    """
    checks = {
        "threshold_calibrated": results["source_threshold"] is not None,
        "threshold_applied": results["target_predictions"] is not None,
        "auroc_computed": results["target_auroc"] is not None,
        "degradation_computed": results["degradation"] is not None,
    }
    
    # Log verification
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"[MECHANISM] {status} {check}")
    
    return all(checks.values())
```

### Success Criteria
- **hypothesis_support_threshold:** Mean degradation ≤ 0.08
- **hypothesis_support_metric:** AUROC degradation across 6 within-cluster pairs

---

## 🔬 PoC Success Check

**NOT APPLICABLE** - H-M3 is MECHANISM type, not EXISTENCE.

**MECHANISM Pass Condition:**
1. Code runs without error for all 6 within-cluster pairs
2. Mean AUROC degradation ≤ 0.08
3. 95% CI upper bound < 0.12

---

## Appendix: Reference Implementations

### Primary Reference
- **Paper:** Farquhar et al. (2024) "Detecting Hallucinations in Large Language Models Using Semantic Entropy" - Nature
- **Code:** https://github.com/jlko/semantic_uncertainty
- **Relevance:** Official implementation of semantic entropy method

### Supporting References
- **Semantic Entropy Probes:** https://github.com/OATML/semantic-entropy-probes
- **Bayesian Semantic Entropy:** https://github.com/spotify-research/bayesian-semantic-entropy
- **Calibration Theory:** Standard ROC threshold calibration methodology

### Code Snippets Used
1. `generate_answers.py` pattern from jlko/semantic_uncertainty
2. `compute_uncertainty_measures.py` semantic entropy computation
3. `analyze_results.py` AUROC evaluation

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T22:45:00Z

### Workflow History for This Hypothesis
- H-E1: PASS (silhouette=0.8245, k=2 clusters)
- H-M1: PASS (p=0.000144, Cohen's d=1.325, AUROC=0.793)
- H-M2: PASS (p=0.0002, same-family JS-div=0.0823, cross-family=0.4813)
- H-M3: IN_PROGRESS (experiment design complete)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
