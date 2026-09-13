# Experiment Design: H-M4

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Cross-cluster benchmark pairs show failed threshold transfer (AUROC degradation > 0.15)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests causal step in verification chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M3 PASS (within-cluster transfer validated)
**Gate Status:** SHOULD_WORK pending

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (within-cluster transfer success)

### Gate Condition
- **Primary:** Mean cross-cluster AUROC degradation > 0.15
- **Secondary:** Significant difference from within-cluster degradation (p < 0.05)
- **Fail Action:** EXPLORE alternative distance metrics

---

## Continuation Context

H-M4 completes the transfer contrast by showing threshold transfer FAILS across clusters. Combined with H-M3 (within-cluster transfer succeeds), this validates that clustering predicts transfer success.

### Previous Hypothesis Results

**H-E1 (PASS):** Silhouette 0.8245, k=2 clusters
- Cluster 1 (Factual Recall): trivia_qa, natural_questions, squad
- Cluster 2 (Entity/Claim): popqa, halueval_qa, fever
- Cross-cluster mean JS-divergence: 0.471

**H-M3 (PASS):** Within-cluster transfer
- Mean degradation: 0.032 (threshold ≤ 0.08)
- Pairs tested: trivia_qa ↔ squad

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct hits. General calibration/transfer concepts available via PyTorch and sklearn documentation.

### Archon Code Examples

No direct semantic entropy transfer code found in KB.

### Exa GitHub Implementations

**Primary References:**
1. **semantic-entropy-gate** (PyPI): Calibration workflow with AUROC, threshold selection via Youden/F1/target_fpr
   - `calibrate(results, labels, criterion="target_fpr", target_fpr=0.05)`
   - AUROC via Mann-Whitney with mid-rank tie handling
   
2. **spotify-research/bayesian-semantic-entropy**: Full reproduction code for semantic entropy hallucination detection
   - Uses jlko/semantic_uncertainty as foundation
   - TriviaQA dataset support built-in
   
3. **chinmayarvind23/Risk-Adjusted-Hallucination-Detection**: Cross-dataset transfer experiments
   - Transfer protocol: train → calibrate → freeze → test on different dataset
   - Platt scaling for calibration

4. **cvs-health/uqlm**: Semantic entropy demo with filtered accuracy evaluation

### 🎯 Implementation Priority Assessment

**CRITICAL: Reuse H-M3 codebase with cross-cluster pair selection**

**Recommended Implementation Path:**
- Primary: Extend H-M3 code to use cross-cluster benchmark pairs
- Fallback: Adapt chinmayarvind23 transfer protocol
- Justification: H-M3 code already validated; only pair selection changes

### Code Analysis (Serena MCP)

Not needed - reusing validated H-M3 codebase.

---

## Experiment Specification

### Dataset

**Cross-Cluster Benchmark Pairs** (from H-E1 clustering):

| Source (Cluster 1) | Target (Cluster 2) | JS-Divergence |
|--------------------|--------------------| --------------|
| trivia_qa          | popqa              | 0.422         |
| trivia_qa          | halueval_qa        | 0.526         |
| trivia_qa          | fever              | 0.530         |
| squad              | popqa              | 0.418         |
| squad              | halueval_qa        | 0.522         |
| squad              | fever              | 0.526         |

**Primary Pairs (for PoC):**
- trivia_qa → popqa (JS=0.422)
- trivia_qa → halueval_qa (JS=0.526)

**Sample Size per Benchmark:** 100 queries
- Calibration: 70 samples (70%)
- Evaluation: 30 samples (30%)

**Loading Information:**
- Method: HuggingFace datasets
- Identifier: trivia_qa, popqa (akariasai/PopQA), halueval (pminervini/HaluEval)
- Code:
```python
from datasets import load_dataset
trivia = load_dataset("trivia_qa", "rc", split="validation[:100]")
popqa = load_dataset("akariasai/PopQA", split="test[:100]")
halueval = load_dataset("pminervini/HaluEval", "qa", split="data[:100]")
```

### Models

#### Baseline Model

Same as H-M3:
- **LLM:** Llama-2-7B-chat-hf (response generation)
- **NLI:** DeBERTa-v3-large (semantic clustering)

**Loading Information:**
- Method: HuggingFace transformers
- Identifier: meta-llama/Llama-2-7b-chat-hf, microsoft/deberta-v3-large-mnli
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
```

#### Proposed Model

**Architecture:** Threshold transfer evaluation (no model modification)

**Core Mechanism Implementation:**

```python
def cross_cluster_transfer_experiment(source_benchmark, target_benchmark, 
                                       n_samples=100, n_generations=10):
    """
    Test threshold transfer between cross-cluster benchmarks.
    Expect AUROC degradation > 0.15 (transfer should FAIL).
    
    Args:
        source_benchmark: Cluster 1 benchmark (e.g., trivia_qa)
        target_benchmark: Cluster 2 benchmark (e.g., popqa)
    
    Returns:
        degradation: source_auroc - target_auroc (expect > 0.15)
    """
    # 1. Load benchmarks
    source_data = load_benchmark(source_benchmark, n_samples)
    target_data = load_benchmark(target_benchmark, n_samples)
    
    # 2. Generate responses + compute semantic entropy
    source_entropy = compute_semantic_entropy(source_data, n_generations)
    target_entropy = compute_semantic_entropy(target_data, n_generations)
    
    # 3. Label correctness (ground truth)
    source_labels = label_correctness(source_data, source_responses)
    target_labels = label_correctness(target_data, target_responses)
    
    # 4. Split source: 70% calibration, 30% held-out
    source_cal, source_test = train_test_split(
        source_entropy, source_labels, train_size=0.7
    )
    
    # 5. Calibrate threshold on source (target FPR=0.1)
    threshold = calibrate_threshold(source_cal.entropy, source_cal.labels, 
                                    target_fpr=0.1)
    
    # 6. Evaluate on source test set
    source_auroc = compute_auroc(source_test.entropy, source_test.labels)
    
    # 7. Evaluate on target (full set, using source threshold)
    target_auroc = compute_auroc(target_entropy, target_labels)
    
    # 8. Calculate degradation
    degradation = source_auroc - target_auroc
    
    return {
        "source_auroc": source_auroc,
        "target_auroc": target_auroc,
        "degradation": degradation,
        "threshold": threshold,
        "pass": degradation > 0.15  # H-M4 expects degradation > 0.15
    }

def compute_auroc(entropy_scores, labels):
    """
    AUROC for hallucination detection.
    Higher entropy → higher probability of incorrect answer.
    """
    from sklearn.metrics import roc_auc_score
    # Labels: 1=incorrect (hallucination), 0=correct
    return roc_auc_score(labels, entropy_scores)
```

### Training Protocol

**No Training Required** - This is an evaluation experiment.

Protocol:
1. Generate 10 responses per query (temperature=1.0)
2. Compute semantic entropy via bidirectional entailment clustering
3. Calibrate threshold on source benchmark (70% split)
4. Apply frozen threshold to target benchmark
5. Compute AUROC degradation

| Parameter | Value |
|-----------|-------|
| N Generations | 10 |
| Temperature | 1.0 |
| Calibration Split | 70/30 |
| Target FPR | 0.1 |
| Threshold Method | Youden (maximize TPR-FPR) |

### Evaluation

**Primary Metric:**
- AUROC degradation = source_auroc - target_auroc
- Success: mean degradation > 0.15

**Secondary Metrics:**
- p-value vs H-M3 within-cluster degradation (Mann-Whitney U)
- 95% CI for mean degradation
- Per-pair degradation breakdown

**Metrics Loading Information:**
- Task Type: Binary classification (correct vs incorrect)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score
from scipy.stats import mannwhitneyu

# AUROC
auroc = roc_auc_score(labels, entropy_scores)

# Compare vs H-M3 (within-cluster)
h_m3_degradations = [0.032, 0.032]  # From H-M3 validation
h_m4_degradations = [...]  # Cross-cluster results
stat, p_value = mannwhitneyu(h_m4_degradations, h_m3_degradations, alternative='greater')
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Cross-cluster degradation vs 0.15 threshold bar chart

#### Additional Figures (LLM Autonomous)

1. **Degradation Comparison**: H-M3 (within) vs H-M4 (cross) box plot
2. **Per-Pair Degradation**: Bar chart for each cross-cluster pair
3. **JS-Divergence vs Degradation**: Scatter plot showing correlation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m4/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Mean cross-cluster AUROC degradation > 0.15
3. Cross-cluster degradation > within-cluster degradation (qualitative)

---

## Appendix: Reference Implementations

### Primary Reference: H-M3 Validated Code

Reuse from `h-m3/code/`:
- `config.py` - Experiment configuration
- `data.py` - Benchmark loading
- `generate.py` - Llama-2-7B generation
- `entropy.py` - Semantic entropy computation
- `transfer.py` - Threshold transfer protocol

### Secondary References

1. **semantic-entropy-gate** (PyPI)
   - Calibration: `calibrate(results, labels, criterion="youden")`
   - AUROC: Mann-Whitney with tie handling

2. **spotify-research/bayesian-semantic-entropy**
   - Dataset: `semantic_uncertainty/generate_answers.py`
   - Pickle format for cached generations

3. **chinmayarvind23/Risk-Adjusted-Hallucination-Detection**
   - Transfer protocol: train→calibrate→freeze→test
   - Platt scaling calibration

### Key Adaptation from H-M3

```python
# H-M3: Within-cluster pairs
WITHIN_CLUSTER_PAIRS = [
    ("trivia_qa", "squad"),    # Both Cluster 1
    ("squad", "trivia_qa"),
]

# H-M4: Cross-cluster pairs  
CROSS_CLUSTER_PAIRS = [
    ("trivia_qa", "popqa"),     # Cluster 1 → Cluster 2
    ("trivia_qa", "halueval_qa"),
]

# Change pair selection, rest of code unchanged
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T23:45:00Z

### Workflow History for This Hypothesis

| Timestamp | Event |
|-----------|-------|
| 2026-08-10T23:37:49Z | H-M4 set to IN_PROGRESS |
| 2026-08-10T23:45:00Z | Phase 2C experiment design started |

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
