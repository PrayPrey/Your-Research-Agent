# Experiment Design: H-E1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Architecture-method interaction exists and is measurable via efficiency-accuracy Pareto curves
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK - Critical foundation for entire hypothesis chain

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (root hypothesis)

### Gate Condition
**MUST_WORK Gate:** If this fails, entire research direction abandoned. Must demonstrate measurable architecture-method interaction exists.

**Pass Criteria:**
- At least one method shows >5% AUC difference across architectures (p < 0.05)
- Effect size Cohen's d > 0.3 for at least one method

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - H-E1 is the root hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct findings on data attribution comparison experiments. General transformer documentation available but no specific attribution comparison studies indexed.

### Archon Code Examples

No directly relevant code examples found for multi-method attribution comparison.

### Exa GitHub Implementations

**Primary Libraries Identified:**

1. **TRAK** (MadryLab/trak)
   - PyTorch package for efficient data attribution
   - `pip install traker[fast]` for CUDA-optimized version
   - Supports custom tasks via `AbstractModelOutput`
   - 2-3 orders magnitude faster than alternatives
   - API: `TRAKer(model, task, train_set_size)` → `featurize()` → `score()`

2. **Kronfluence** (pomonam/kronfluence)
   - EK-FAC influence functions for PyTorch
   - Supports `nn.Linear` and `nn.Conv2d` modules
   - Strategies: `identity`, `diagonal`, `kfac`, `ekfac`
   - API: `Analyzer(model, task)` → `fit_all_factors()` → `compute_pairwise_scores()`
   - Scales to 52B parameter models (Grosse et al. 2023)

3. **TracIn** (Captum library)
   - `TracInCP` and `TracInCPFast` implementations
   - Self-influence scores for mislabeled detection
   - Checkpoint-based gradient similarity

4. **simple-influence** (pomonam/simple-influence)
   - Unified interface for multiple methods
   - Same API: `compute_scores_with_loader(test_loader, train_loader)`
   - Includes: EK-FAC, TRAK wrapper, TracIn, gradient similarity

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Method | Official Implementation | Recommended Library |
|--------|------------------------|---------------------|
| TRAK | MadryLab/trak | `traker` (pip) |
| EK-FAC | pomonam/kronfluence | `kronfluence` (pip) |
| TracIn | Captum (TracInCP) | `captum` (pip) |

**Recommended Implementation Path:**
- Primary: Use `simple-influence` for unified API across all three methods
- Fallback: Direct library usage (kronfluence, traker, captum)
- Justification: Unified interface enables fair comparison; same preprocessing/scoring pipeline

### Code Analysis (Serena MCP)

N/A - No existing codebase to analyze. This is a new experiment.

---

## Experiment Specification

### Dataset

**Name:** SST-2 (Stanford Sentiment Treebank v2)
**Source:** GLUE benchmark via HuggingFace datasets
**Type:** standard

| Split | Size | Usage |
|-------|------|-------|
| Train | 67,349 | Fine-tuning + Attribution source |
| Validation | 872 | Mislabeled detection evaluation |

**Preprocessing:**
- Tokenization: Model-specific tokenizer (BERT/GPT-2)
- Max sequence length: 128 tokens
- Padding: Right-pad to max length

**Label Noise Injection:**
- Rate: 5% of training examples
- Method: Flip label (0↔1) for randomly selected examples
- Seed: Fixed (42) for reproducibility across runs

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `glue/sst2`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("glue", "sst2")
train_data = dataset["train"]
val_data = dataset["validation"]
```

### Models

#### Baseline Model

| Model | Architecture | Layers | Parameters | Source |
|-------|-------------|--------|------------|--------|
| BERT-base-uncased | Encoder-only | 12 | ~110M | HuggingFace |
| GPT-2 | Decoder-only | 12 | ~124M | HuggingFace |

**Matched Control Variables:**
- Layer count: 12 (both)
- Hidden dimension: 768 (both)
- Attention heads: 12 (both)
- Parameter count: ~110-124M (comparable)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `bert-base-uncased`, `gpt2`
- Code:
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# BERT
bert_model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=2
)
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# GPT-2 (add classification head)
gpt2_model = AutoModelForSequenceClassification.from_pretrained(
    "gpt2", num_labels=2
)
gpt2_model.config.pad_token_id = gpt2_model.config.eos_token_id
gpt2_tokenizer = AutoTokenizer.from_pretrained("gpt2")
gpt2_tokenizer.pad_token = gpt2_tokenizer.eos_token
```

#### Proposed Model

**Architecture:** Baseline + [No modification - comparison experiment]

This is a comparison experiment, not a model modification experiment. We compare existing attribution methods across architectures.

**Core Mechanism Implementation:**

```python
# Pseudo-code: Multi-method attribution comparison pipeline

def compute_mislabeled_detection_auc(
    model, 
    train_loader, 
    val_loader, 
    method: str,  # "trak", "ekfac", "tracin"
    mislabeled_indices: set
) -> float:
    """
    Compute mislabeled detection AUC for given attribution method.
    
    Returns:
        AUC score (higher = better at detecting mislabeled examples)
    """
    
    if method == "trak":
        from trak import TRAKer
        traker = TRAKer(model=model, task='text_classification', 
                        train_set_size=len(train_loader.dataset))
        # Featurize training data
        traker.load_checkpoint(model.state_dict(), model_id=0)
        for batch in train_loader:
            traker.featurize(batch=batch, num_samples=len(batch[0]))
        traker.finalize_features()
        
        # Score: self-influence (training on itself)
        traker.start_scoring_checkpoint(model.state_dict(), model_id=0,
                                        exp_name='self', num_targets=len(train_loader.dataset))
        for batch in train_loader:
            traker.score(batch=batch, num_samples=len(batch[0]))
        scores = traker.finalize_scores('self')
        influence_scores = scores.diagonal()  # Self-influence
        
    elif method == "ekfac":
        from kronfluence import Analyzer, prepare_model
        from kronfluence.task import Task
        
        model = prepare_model(model, task=ClassificationTask())
        analyzer = Analyzer(analysis_name="sst2", model=model, task=ClassificationTask())
        analyzer.fit_all_factors(factors_name="factors", dataset=train_loader.dataset)
        analyzer.compute_self_scores(scores_name="self", factors_name="factors",
                                     train_dataset=train_loader.dataset)
        scores = analyzer.load_self_scores("self")
        influence_scores = scores["all_modules"]
        
    elif method == "tracin":
        from captum.influence import TracInCPFast
        tracin = TracInCPFast(model=model, 
                              train_dataset=train_loader.dataset,
                              checkpoints=[model.state_dict()],
                              loss_fn=torch.nn.CrossEntropyLoss())
        influence_scores = tracin.self_influence()
    
    # Compute AUC: mislabeled examples should have HIGH self-influence
    from sklearn.metrics import roc_auc_score
    labels = [1 if i in mislabeled_indices else 0 
              for i in range(len(influence_scores))]
    auc = roc_auc_score(labels, influence_scores)
    
    return auc
```

### Training Protocol

**Fine-tuning Configuration:**

| Parameter | BERT | GPT-2 |
|-----------|------|-------|
| Optimizer | AdamW | AdamW |
| Learning Rate | 2e-5 | 2e-5 |
| LR Schedule | Linear warmup (10%) + decay | Linear warmup (10%) + decay |
| Batch Size | 32 | 32 |
| Epochs | 3 | 3 |
| Weight Decay | 0.01 | 0.01 |
| Max Grad Norm | 1.0 | 1.0 |

**Checkpoint Strategy:**
- Save checkpoint at end of each epoch
- Use final checkpoint for attribution (single checkpoint mode)
- Alternative: Use all 3 checkpoints for TRAK ensemble

**Seeds:** Run 5 independent seeds (42, 43, 44, 45, 46) for statistical testing

### Evaluation

**Primary Metric:** Mislabeled Detection AUC
- Higher AUC = better at ranking mislabeled examples higher
- Computed per method × architecture combination

**Statistical Testing:**
- Paired t-test across 5 random seeds
- Effect size: Cohen's d
- Significance threshold: p < 0.05

**Success Criteria (PoC: Direction-based):**
1. **Primary:** At least one method shows >5% AUC difference across architectures (p < 0.05)
2. **Secondary:** Effect size Cohen's d > 0.3 for at least one method

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification + mislabeled detection
- Library: scikit-learn
- Code:
```python
from sklearn.metrics import roc_auc_score
from scipy.stats import ttest_rel
import numpy as np

def cohens_d(x, y):
    nx, ny = len(x), len(y)
    pooled_std = np.sqrt(((nx-1)*np.std(x,ddof=1)**2 + (ny-1)*np.std(y,ddof=1)**2) / (nx+ny-2))
    return (np.mean(x) - np.mean(y)) / pooled_std
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing AUC across 6 conditions (3 methods × 2 architectures)
  - X-axis: Method (TRAK, EK-FAC, TracIn)
  - Y-axis: Mislabeled Detection AUC
  - Color: Architecture (BERT=blue, GPT-2=orange)
  - Error bars: Standard error across 5 seeds

#### Additional Figures (LLM Autonomous)

1. **Method × Architecture Heatmap**: 3×2 heatmap of AUC scores
2. **Difference Plot**: Bar chart of AUC_GPT2 - AUC_BERT per method
3. **Statistical Significance Annotation**: p-values overlaid on difference plot

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. At least one: `|AUC_BERT - AUC_GPT2| > 0.05` with `p < 0.05`

**Interpretation Guide:**
- If EK-FAC shows GPT-2 > BERT: Supports P1 (Kronecker assumption fits causal attention)
- If TracIn shows BERT > GPT-2: Supports P2 (gradient signal benefits from dense encoder)
- If TRAK shows |diff| < 0.02: Supports P3 (random projection invariant)

---

## Appendix: Reference Implementations

### TRAK
- **Repository:** https://github.com/MadryLab/trak
- **Paper:** Park et al. 2023, "TRAK: Attributing Model Behavior at Scale"
- **Install:** `pip install traker[fast]`
- **Key API:**
```python
from trak import TRAKer
traker = TRAKer(model=model, task='text_classification', train_set_size=N)
traker.featurize(batch, num_samples=batch_size)
traker.finalize_features()
scores = traker.finalize_scores('exp_name')
```

### Kronfluence (EK-FAC)
- **Repository:** https://github.com/pomonam/kronfluence
- **Paper:** Grosse et al. 2023, "Studying Large Language Model Generalization with Influence Functions"
- **Install:** `pip install kronfluence`
- **Key API:**
```python
from kronfluence import Analyzer, prepare_model
model = prepare_model(model, task=task)
analyzer = Analyzer(analysis_name="exp", model=model, task=task)
analyzer.fit_all_factors(factors_name="factors", dataset=train_dataset)
analyzer.compute_self_scores(scores_name="self", factors_name="factors", train_dataset=train_dataset)
```

### TracIn (Captum)
- **Repository:** https://github.com/pytorch/captum
- **Paper:** Pruthi et al. 2020, "Estimating Training Data Influence by Tracing Gradient Descent"
- **Install:** `pip install captum`
- **Key API:**
```python
from captum.influence import TracInCPFast
tracin = TracInCPFast(model=model, train_dataset=dataset, checkpoints=ckpts, loss_fn=loss_fn)
self_influence = tracin.self_influence()
```

### Unified Interface (simple-influence)
- **Repository:** https://github.com/pomonam/simple-influence
- **Install:** `pip install -e '.[pytorch_gpu]'`
- **Key API:**
```python
from src.influence_function import InfluenceFunctionComputer
computer = InfluenceFunctionComputer(model=model, task=task)
scores = computer.compute_scores_with_loader(test_loader, train_loader)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- 2026-08-18: Hypothesis h-e1 set to IN_PROGRESS
- 2026-08-18: Phase 2C experiment design started
- 2026-08-18: MCP research completed (Exa: TRAK, kronfluence, TracIn implementations)
- 2026-08-18: Experiment specification generated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
