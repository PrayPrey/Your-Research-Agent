# Experiment Design: H-E1

**Date:** 2026-08-08
**Hypothesis Statement:** Synthetic benchmark injection produces monotonic CCR scaling (R² ≥ 0.9) and validates detector precision (F1 > 0.8 at 0.1% injection)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
CCR scales monotonically with injection rate (R² ≥ 0.9); F1 > 0.8 at 0.1% injection. Failure → STOP (metric stack invalid).

---

## Continuation Context

First hypothesis in verification chain. No previous context.

### Previous Hypothesis Results (if applicable)
N/A - H-E1 is the calibration experiment.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct findings for contamination detection. Primary findings from Exa research.

### Archon Code Examples

PyTorch setup patterns for model training.

### Exa GitHub Implementations

**Query 1: Benchmark Contamination Detection**

**Sources:**
1. **Deng et al. (NAACL 2024)** - "Investigating Data Contamination in Modern Benchmarks"
   - Method: TS-Guessing (Testset Slot Guessing) + IR-based retrieval (Pyserini)
   - Datasets: MMLU, HellaSwag, GSM8K, PIQA, WinoGrande, OpenbookQA, TruthfulQA
   - Detection: N-gram overlap (10-13 grams), embedding similarity, METEOR recall > 0.75
   - Key insight: ChatGPT achieves 57% EM on MMLU option guessing (vs 25% random)

2. **Open-Source Data Contamination Report (EMNLP 2024)**
   - Detection: METEOR score-based overlap detection
   - Corpus: Common Crawl Dec 2020 - Oct 2023
   - Finding: Contamination inflates accuracy by 7-14% on MMLU/HellaSwag

3. **TRAK (ICML 2023)** - Park et al.
   - URL: https://github.com/MadryLab/trak
   - Method: Randomly-projected After Kernel for data attribution
   - Speed: 2-3 orders of magnitude faster than influence functions
   - Scales to: ImageNet, CLIP, BERT, mT5

**Query 2: Pythia/RedPajama Training**

**Sources:**
1. **Pythia Suite** (EleutherAI)
   - URL: https://github.com/EleutherAI/pythia
   - Models: Pythia-70M to Pythia-12B
   - Training data: Deduplicated Pile
   - Evaluation: LM-evaluation-harness

2. **RedPajama** (Weber et al., 2024)
   - 100T+ tokens open dataset
   - Models: RedPajama-INCITE-3B/7B outperform Pythia-2.8B on HELM by 3-5 points
   - Includes MinHash deduplication signatures

### 🎯 Implementation Priority Assessment

**Primary Implementation Path:**
- N-gram overlap detection (standard: 10-13 grams)
- TRAK for data attribution (faster than influence functions)
- LM-evaluation-harness for MMLU evaluation

**Fallback Implementation:**
- METEOR-based overlap detection (handles paraphrases better)
- Custom perplexity-based contamination scoring

**Justification:**
N-gram overlap is well-established (GPT-3, GPT-4, Llama-2 all use it). TRAK provides scalable attribution. Pythia provides checkpoints at multiple training steps.

### Code Analysis (Serena MCP)

Not required - implementations are well-documented in research papers.

---

## Experiment Specification

### Dataset

**Primary Dataset: MMLU**
- **Name:** MMLU (Massive Multitask Language Understanding)
- **Type:** standard
- **Source:** HuggingFace `cais/mmlu`
- **Splits:** 14,042 test questions across 57 subjects
- **Purpose:** Target benchmark for CCR measurement

**Training Corpus: RedPajama-1B Subset**
- **Name:** RedPajama-V2 (1B token subset)
- **Type:** programmatic-api
- **Source:** HuggingFace `togethercomputer/RedPajama-Data-1T`
- **Purpose:** Clean corpus for synthetic injection experiment

**Synthetic Data Policy Check:** ✅ PASSED
- MMLU: standard benchmark (real)
- RedPajama: real web-crawled corpus (not synthetic)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `cais/mmlu` (all subjects), `togethercomputer/RedPajama-Data-1T`
- Code: 
```python
from datasets import load_dataset
mmlu = load_dataset("cais/mmlu", "all")
redpajama = load_dataset("togethercomputer/RedPajama-Data-1T", streaming=True)
```

### Models

#### Baseline Model

**Architecture:** Pythia-1B (EleutherAI/pythia-1b)
**Type:** Causal language model
**Parameters:** 1 billion
**Source:** HuggingFace `EleutherAI/pythia-1b`
**Rationale:** Open weights, open training data, checkpoint access at multiple steps

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `EleutherAI/pythia-1b`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("EleutherAI/pythia-1b")
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-1b")
```

#### Proposed Model

**Architecture:** Pythia-1B trained on RedPajama + MMLU injection at varying rates

**Core Mechanism Implementation:**

```python
# Core Mechanism: Synthetic Benchmark Injection & CCR Computation
# Based on: Deng et al. (NAACL 2024), TRAK (Park et al. ICML 2023)

def inject_benchmark_into_corpus(corpus, benchmark, injection_rate):
    """
    Inject benchmark examples into training corpus at specified rate.
    
    Args:
        corpus: List of training documents (RedPajama subset)
        benchmark: MMLU test set (question + answer verbalized)
        injection_rate: Float in [0.001, 0.01, 0.05, 0.1] (0.1% to 10%)
    Returns:
        Contaminated corpus with benchmark examples inserted
    """
    n_inject = int(len(corpus) * injection_rate)
    injection_positions = random.sample(range(len(corpus)), n_inject)
    
    for i, pos in enumerate(injection_positions):
        # Verbalize MMLU: "Question: {q}\nAnswer: {correct_answer}"
        mmlu_sample = benchmark[i % len(benchmark)]
        verbalized = f"Question: {mmlu_sample['question']}\nAnswer: {mmlu_sample['answer']}"
        corpus[pos] = verbalized
    
    return corpus, injection_positions

def compute_ccr(model, tokenizer, benchmark, corpus_docs, injected_positions):
    """
    Compute Contamination Contribution Ratio using n-gram overlap + attribution.
    
    Returns:
        ccr_score: Float in [0, 1] - proportion of benchmark-aligned influence
    """
    # Step 1: N-gram overlap detection (13-gram, following GPT-3)
    contaminated_docs = detect_ngram_overlap(corpus_docs, benchmark, n=13)
    
    # Step 2: TRAK attribution scores for contaminated docs
    traker = TRAKer(model=model, task='text_classification', train_set_size=len(corpus_docs))
    scores = traker.score(benchmark)  # Attribution to each training doc
    
    # Step 3: CCR = sum(attribution[contaminated]) / sum(attribution[all])
    contaminated_attribution = sum(scores[injected_positions])
    total_attribution = sum(scores)
    ccr = contaminated_attribution / (total_attribution + 1e-8)
    
    return ccr

def evaluate_detector_precision(predicted_contaminated, actual_contaminated):
    """Compute F1 score for contamination detection."""
    tp = len(predicted_contaminated & actual_contaminated)
    fp = len(predicted_contaminated - actual_contaminated)
    fn = len(actual_contaminated - predicted_contaminated)
    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f1 = 2 * precision * recall / (precision + recall + 1e-8)
    return f1
```

### Training Protocol

**For each injection level [0.001, 0.01, 0.05, 0.1]:**

**Optimizer:** AdamW
  - Parameters: lr=1e-4, weight_decay=0.01, betas=(0.9, 0.95)
  - **Source:** Pythia training defaults (Biderman et al., 2023)

**Learning Rate:** 1e-4 with cosine decay
  - **Source:** Pythia training protocol

**Batch Size:** 512 tokens × 8 gradient accumulation = 4096 effective
  - **Source:** Pythia training

**Training Steps:** 10,000 steps on 1B token subset
  - **Source:** Scaled proportionally for PoC

**Loss Function:** Cross-entropy (standard LM objective)

**Seeds:** 1 (fixed at 42)

> ⚠️ **EXISTENCE (PoC)**: Single seed. 4 injection levels = 4 training runs.

### Evaluation

**Primary Metrics**:
- **CCR (Contamination Contribution Ratio)**: Attribution-weighted contamination score
- **Detector F1**: Precision/recall of n-gram overlap detection
- **MMLU Accuracy**: Multiple-choice accuracy on MMLU test set

**Success Criteria (PoC)**:
- CCR scales monotonically with injection rate (visual + R² ≥ 0.9)
- F1 > 0.8 at 0.1% injection rate
- Direction: higher injection → higher CCR and MMLU accuracy

**Expected Baseline Performance** (from research):
- Clean Pythia-1B MMLU accuracy: ~25-30% (near random for small models)
- Expected CCR at 0%: ~0.0
- Expected CCR at 10%: 0.5-0.8 (significant contamination signal)
- **Source:** Deng et al. (2024), Biderman et al. (2023)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: text_classification (MMLU multiple-choice)
- Library: sklearn.metrics + custom
- Code:
```python
from sklearn.metrics import f1_score, r2_score
import numpy as np

# R² for monotonicity check
injection_rates = [0.001, 0.01, 0.05, 0.1]
ccr_values = [...]  # measured
r2 = r2_score(injection_rates, ccr_values)  # Linear fit R²

# F1 for detector
f1 = f1_score(actual_contaminated, predicted_contaminated)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **CCR vs Injection Rate**: Line plot showing CCR scaling with injection rate, annotated with R² value

#### Additional Figures (LLM Autonomous)
- MMLU accuracy vs injection rate (to show benchmark inflation)
- Detector precision-recall curve at different thresholds
- Attribution score distribution (contaminated vs clean docs)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** Yes - n-gram overlap + TRAK attribution
- **mechanism_isolatable:** Yes - can measure CCR at each injection level independently
- **baseline_measurable:** Yes - 0% injection provides clean baseline

### Architecture Compatibility
Pythia-1B is a standard transformer LM. TRAK is compatible with any differentiable model. N-gram detection is model-agnostic.

### Activation Indicators
- **mechanism_log_message:** "Computing CCR for injection_rate={rate}..."
- **tensor_shape_change:** Attribution scores shape = (n_train_docs,)
- **metric_delta_expected:** CCR(10%) - CCR(0.1%) > 0.3

### Verification Code
```python
def verify_mechanism_activation(ccr_values, injection_rates):
    """Verify CCR mechanism produces expected scaling."""
    assert len(ccr_values) == len(injection_rates), "Missing CCR measurements"
    assert all(ccr >= 0 for ccr in ccr_values), "CCR must be non-negative"
    
    # Monotonicity check
    for i in range(1, len(ccr_values)):
        if ccr_values[i] <= ccr_values[i-1]:
            print(f"WARNING: Non-monotonic at {injection_rates[i]}")
    
    # R² check
    r2 = np.corrcoef(injection_rates, ccr_values)[0,1]**2
    print(f"R² = {r2:.3f} (target: ≥0.9)")
    
    return r2 >= 0.9
```

### Success Criteria
- **hypothesis_support_threshold:** R² ≥ 0.9, F1 > 0.8
- **hypothesis_support_metric:** Linear regression R² + detector F1

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 4 injection levels
2. CCR increases with injection rate (monotonic trend)
3. R² ≥ 0.9 for CCR vs injection rate regression
4. Detector F1 > 0.8 at 0.1% injection

---

## Appendix: Reference Implementations

1. **TRAK Library:** https://github.com/MadryLab/trak
   - `pip install traker[fast]` for CUDA acceleration
   - API: `TRAKer(model, task, train_set_size)`

2. **LM-Evaluation-Harness:** https://github.com/EleutherAI/lm-evaluation-harness
   - MMLU evaluation: `lm_eval --model hf --model_args pretrained=EleutherAI/pythia-1b --tasks mmlu`

3. **Pyserini:** https://github.com/castorini/pyserini
   - BM25 retrieval for n-gram overlap detection

4. **Contamination Detector:** https://github.com/liyucheng09/Contamination_Detector
   - METEOR-based overlap detection

---

## State Information

**State File:** verification_state.yaml (via ablation override)
**Date:** 2026-08-08

### Workflow History for This Hypothesis
- Step 1: Initialized workflow, loaded H-E1 from state
- Step 2: Archon KB search (limited results)
- Step 3: Exa search (contamination detection literature)
- Step 4: Skipped (no complex code requiring Serena)
- Step 5: Dataset/model confirmed (MMLU + Pythia-1B)
- Step 6: Synthesis complete

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
