# Experiment Design: H-M4

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Architecture-approximation interaction determines efficiency-accuracy trade-off (EK-FAC favors GPT-2, TracIn favors BERT, TRAK invariant)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Testing efficiency-accuracy Pareto curve relationships across methods and architectures.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M3 PASSED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (Approximation Assumption Sensitivity - PASSED)

### Gate Condition
- **Primary:** P1 (EK-FAC GPT-2 > BERT) and P2 (TracIn BERT > GPT-2) confirmed with p < 0.05
- **Secondary:** P3 (TRAK invariant) confirmed with |diff| < 5%

---

## Continuation Context

H-M3 established that attribution methods show architecture-dependent performance:
- **EK-FAC:** 18.5% difference (BERT 0.580 > GPT-2 0.473) 
- **TracIn:** 15.9% difference (BERT 0.584 > GPT-2 0.491)
- **TRAK:** 15.0% difference (GPT-2 0.491 > BERT 0.417)

H-M4 extends this by testing whether these differences persist across compute budgets, forming distinct Pareto frontiers.

### Previous Hypothesis Results (if applicable)

From H-M3 (04_validation.md):
- All three methods show >10% architecture-dependent AUC differences
- Directional predictions partially confirmed: TracIn favors BERT (as predicted)
- EK-FAC and TRAK showed unexpected directional patterns
- Cross-seed TRAK correlation: BERT 0.83, GPT-2 0.44

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct Pareto curve implementations found in knowledge base. Relevant background on LoRA efficiency trade-offs and model optimization patterns suggest standard approach: vary compute budget parameter (projection dimension, gradient checkpoints, sample count) and measure accuracy at each level.

### Archon Code Examples

No directly applicable code examples found. General benchmarking patterns from diffusers library show standard latency/quality measurement approach applicable here.

### Exa GitHub Implementations

**Primary Libraries Identified:**

1. **kronfluence** (pomonam/kronfluence)
   - EK-FAC influence functions with PyTorch
   - 198 stars, Apache 2.0 license
   - Supports projection dimension parameter for efficiency control
   - Example: `pip install kronfluence`

2. **traker** (MadryLab/trak)
   - TRAK data attribution at scale
   - 243 stars, MIT license
   - Projection dimension controls efficiency-accuracy trade-off
   - Example: `pip install traker[fast]`

3. **dattri** (TRAIS-Lab/dattri)
   - Unified benchmarking library
   - Includes TracIn, TRAK, Influence Functions
   - 123 stars, MIT license
   - Built-in mislabeled detection benchmark
   - Example: `pip install dattri`

4. **quanda** (documentation)
   - Kronfluence wrapper with mislabeled_detection benchmark
   - Integrates kronfluence, trak wrappers

5. **influenciae** (DEEL-AI)
   - Mislabeled detection AUC benchmark
   - ROC curve for ranking mislabeled samples

### Implementation Priority Assessment

**CRITICAL: Use established libraries for reproducibility**

**Recommended Implementation Path:**
- Primary: `dattri` library for unified TracIn/TRAK; `kronfluence` for EK-FAC
- Fallback: Direct implementation using PyTorch gradient computation
- Justification: dattri provides standardized benchmark interface; kronfluence is the reference EK-FAC implementation

### Code Analysis (Serena MCP)

Not applicable - using external libraries, no local codebase analysis needed.

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | SST-2 (Stanford Sentiment Treebank v2) |
| **Source** | GLUE Benchmark via HuggingFace Datasets |
| **Type** | standard |
| **Train Split** | 67,349 samples |
| **Validation Split** | 872 samples |
| **Task** | Binary sentiment classification |
| **Mislabeling** | 5% random label noise (3,367 samples) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets library
- Identifier: `glue`, `sst2`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("glue", "sst2")
train_data = dataset["train"]  # 67,349 samples
val_data = dataset["validation"]  # 872 samples
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Architecture 1** | BERT-base-uncased (encoder-only) |
| **Architecture 2** | GPT-2 (decoder-only) |
| **Parameters** | ~110M (BERT), ~124M (GPT-2) |
| **Layers** | 12 (matched) |
| **Source** | HuggingFace Transformers |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `bert-base-uncased`, `gpt2`
- Code:
```python
from transformers import (
    BertForSequenceClassification,
    GPT2ForSequenceClassification,
    AutoTokenizer
)

# BERT
bert_model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=2
)
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# GPT-2
gpt2_model = GPT2ForSequenceClassification.from_pretrained(
    "gpt2", num_labels=2
)
gpt2_model.config.pad_token_id = gpt2_model.config.eos_token_id
gpt2_tokenizer = AutoTokenizer.from_pretrained("gpt2")
gpt2_tokenizer.pad_token = gpt2_tokenizer.eos_token
```

#### Proposed Model

**Architecture:** N/A - This is a comparison experiment across existing methods, not a new architecture proposal.

**Core Mechanism Implementation:**

```python
# Pareto Curve Generation Pseudo-code (10-30 lines)

def compute_pareto_curve(model, train_data, query_data, method, 
                         compute_budgets, mislabel_indices):
    """
    Compute efficiency-accuracy Pareto points for a single method.
    
    Args:
        model: Fine-tuned BERT or GPT-2
        train_data: Training samples with 5% mislabeled
        query_data: Validation samples for attribution
        method: "ekfac" | "tracin" | "trak"
        compute_budgets: List of projection dims [64, 128, 256, 512, 1024]
        mislabel_indices: Ground truth mislabeled sample indices
    
    Returns:
        List of (compute_time, auc) tuples for Pareto curve
    """
    pareto_points = []
    
    for proj_dim in compute_budgets:
        start_time = time.time()
        
        if method == "ekfac":
            # kronfluence with varying projection dimension
            analyzer = Analyzer(model, task=ClassificationTask())
            analyzer.set_projection_dim(proj_dim)
            scores = analyzer.compute_influence_scores(train_data, query_data)
        
        elif method == "tracin":
            # dattri TracIn with gradient checkpointing
            attributor = TracInCPFast(model, train_loader, ckpt_paths)
            scores = attributor.attribute(query_data)
        
        elif method == "trak":
            # traker with varying projection dimension
            tracker = TRAKer(model, train_data, proj_dim=proj_dim)
            tracker.featurize()
            scores = tracker.score(query_data)
        
        compute_time = time.time() - start_time
        
        # Compute mislabeled detection AUC
        auc = compute_mislabel_auc(scores, mislabel_indices)
        pareto_points.append((compute_time, auc))
    
    return pareto_points

# Main experiment loop
results = {}
for arch in ["bert", "gpt2"]:
    model = load_finetuned_model(arch)
    results[arch] = {}
    for method in ["ekfac", "tracin", "trak"]:
        results[arch][method] = compute_pareto_curve(
            model, train_data, query_data, method,
            compute_budgets=[64, 128, 256, 512, 1024],
            mislabel_indices=mislabel_idx
        )

# Analyze Pareto dominance
compare_pareto_frontiers(results)
```

### Training Protocol

| Parameter | Value |
|-----------|-------|
| **Fine-tuning Epochs** | 3 |
| **Optimizer** | AdamW |
| **Learning Rate** | 2e-5 |
| **LR Schedule** | Linear warmup (10%) + decay |
| **Batch Size** | 32 |
| **Max Sequence Length** | 128 |
| **Weight Decay** | 0.01 |
| **Seeds** | 42, 123, 456 (3 seeds for statistical testing) |

**Note:** Models are fine-tuned once per seed, then attribution methods applied at multiple compute budgets.

### Evaluation

| Metric | Description | Success Criterion |
|--------|-------------|-------------------|
| **Mislabeled Detection AUC** | Area under ROC for ranking mislabeled samples | Primary metric |
| **Compute Time** | Wall-clock time for attribution computation | X-axis of Pareto curve |
| **Pareto Dominance** | Whether one curve dominates another | Statistical comparison |

**Gate Criteria (PoC: Direction-based):**
- **P1:** EK-FAC GPT-2 AUC > BERT AUC at matched compute (p < 0.05)
- **P2:** TracIn BERT AUC > GPT-2 AUC at matched compute (p < 0.05)
- **P3:** TRAK |BERT - GPT-2| AUC < 5% at all compute budgets

**Statistical Testing:**
- Paired t-test across 3 seeds per compute budget
- Report mean ± std for each (method, architecture, budget) combination

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification / Ranking
- Library: scikit-learn
- Code:
```python
from sklearn.metrics import roc_auc_score
import numpy as np

def compute_mislabel_auc(influence_scores, mislabel_indices):
    """
    Compute AUC for mislabeled sample detection.
    Higher influence score = more likely mislabeled.
    """
    n_train = len(influence_scores)
    labels = np.zeros(n_train)
    labels[mislabel_indices] = 1
    
    # Self-influence scores (diagonal) indicate sample difficulty
    self_scores = np.diag(influence_scores) if influence_scores.ndim == 2 \
                  else influence_scores
    
    return roc_auc_score(labels, -self_scores)  # Lower score = more helpful
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Pareto Frontier Comparison**: 2x3 subplot grid showing Pareto curves for each method across both architectures. X-axis: compute time (log scale), Y-axis: mislabeled detection AUC.

#### Additional Figures (LLM Autonomous)

1. **Architecture Comparison per Method**: Overlaid Pareto curves for BERT vs GPT-2 per method (3 plots)
2. **Dominance Heatmap**: Which method dominates at each compute budget × architecture combination
3. **AUC vs Projection Dimension**: Line plots showing how AUC scales with compute budget
4. **Bar Chart**: AUC comparison at fixed compute budget (e.g., proj_dim=256)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on both BERT and GPT-2
2. Pareto curves generated for all 6 (method × architecture) combinations
3. At least one prediction (P1, P2, or P3) confirmed with statistical significance

**Note on H-M3 Results:** Previous results showed unexpected directions (EK-FAC: BERT > GPT-2, TRAK: GPT-2 > BERT). H-M4 may confirm or refute these patterns across compute budgets. If patterns are consistent across budgets, the original P1-P3 predictions should be revised based on empirical findings.

---

## Appendix: Reference Implementations

### kronfluence (EK-FAC)
- **Repository:** https://github.com/pomonam/kronfluence
- **Paper:** Grosse et al. 2023 "Studying Large Language Model Generalization with Influence Functions"
- **Key API:**
```python
from kronfluence import Analyzer
from kronfluence.task import ClassificationTask

analyzer = Analyzer(model, task=ClassificationTask())
analyzer.fit(train_loader)
scores = analyzer.compute_influence_scores(query_loader)
```

### traker (TRAK)
- **Repository:** https://github.com/MadryLab/trak
- **Paper:** Park et al. 2023 "TRAK: Attributing Model Behavior at Scale"
- **Key API:**
```python
from trak import TRAKer

traker = TRAKer(model, train_set, proj_dim=1024)
traker.featurize(batch_size=32)
traker.finalize_features()
scores = traker.score(targets=query_set)
```

### dattri (TracIn)
- **Repository:** https://github.com/TRAIS-Lab/dattri
- **Paper:** Pruthi et al. 2020 "Estimating Training Data Influence by Tracing Gradient Descent"
- **Key API:**
```python
from dattri.attributors import TracInCPFast

attributor = TracInCPFast(
    model, 
    train_loader,
    checkpoint_paths=ckpt_paths
)
scores = attributor.attribute(test_loader)
```

### Mislabeled Detection Benchmark
- **Reference:** influenciae (DEEL-AI) benchmark module
- **Metric:** ROC-AUC for ranking mislabeled samples using influence scores

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18T16:30:00+00:00

### Workflow History for This Hypothesis

- 2026-08-18: H-M4 set to IN_PROGRESS (Phase 2C experiment design started)
- 2026-08-18: H-M3 validation completed - GATE PASSED (prerequisite satisfied)
- Prior: H-E1, H-M1, H-M2, H-M3 all completed and passed gates

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
