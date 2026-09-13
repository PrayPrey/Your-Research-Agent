# Experiment Design: H-M4

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under cross-architecture comparison (Transformer vs Mamba), if tasks vary in retrieval density, then adaptation efficiency change (Mamba - Transformer delta) correlates with retrieval density (rho > 0.7).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Tests task-dependent transformation emergence from architecture-task interaction.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M3 VALIDATED: rho=1.0)
**Gate Status:** MUST_WORK - Spearman rho > 0.7 between retrieval density and efficiency delta

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (VALIDATED: rho=1.0 sharpness-rank correlation)

### Gate Condition
**Primary:** Spearman rho > 0.7 between task retrieval density and adaptation efficiency delta (Mamba - Transformer)
**Secondary:** Monotonic relationship across all 4 benchmarks without outliers

---

## Continuation Context

This hypothesis validates the full causal chain by testing the emergent pattern: architecture-task interaction produces predictable transformation based on retrieval density. H-M3 established that landscape geometry (sharpness) predicts LoRA adaptation efficiency. H-M4 tests whether this translates to task-dependent transformation across architectures.

### Previous Hypothesis Results

| Hypothesis | Key Finding | Gate Result |
|------------|-------------|-------------|
| H-E1 | Task-dependent pattern exists: GSM8K delta=-2%, NQ delta=-18% | PASS |
| H-M1 | Landscape geometry changes: sharpness delta=219%, KL=2.847 | PASS |
| H-M2 | Sequential tasks show 35% lower sharpness (ratio=0.65) | PASS |
| H-M3 | Perfect correlation (rho=1.0) between sharpness and effective rank | PASS |

**Validated Components:**
- SAM sharpness measurement (epsilon=0.05)
- LoRA effective rank computation (threshold=0.90)
- Mamba architecture (d_model=512, d_state=16, n_layers=4)
- Training protocol (AdamW, lr=1e-4, batch_size=4)

---

## Implementation Research Summary

### Knowledge Base Findings

**Cross-Architecture Adaptation Research:**

1. **TransMamba (arXiv 2502.15130):** Universal adaptation from Transformers to Mamba using feature calibration. Enables 2x reduction in training data while matching accuracy on image classification and text-video retrieval.

2. **MambaPEFT (arXiv 2411.03855):** First systematic evaluation of PEFT methods (LoRA, adapters) on SSM-based models. LoRA consistently outperforms other methods on both pure Mamba and hybrid Jamba architectures.

3. **Mamba-Transformer Hybrids:** 7:1 Mamba-to-attention ratio appears optimal. Key insight: "Transformers are good at retrieval but expensive at scale; SSMs are cheap at scale but weaker at retrieval."

4. **Retrievit (arXiv 2603.02874):** SSMs struggle with retrieval tasks—a deficiency standard benchmarks often fail to capture. SSM-hybrids show faster initial task acquisition.

### Code Pattern: Cross-Architecture Efficiency Delta

```python
def compute_architecture_efficiency_delta(
    transformer_model, mamba_model, task_datasets, config
):
    """
    Compute adaptation efficiency delta (Mamba - Transformer) per task.
    """
    results = {}
    
    for task_name, dataset in task_datasets.items():
        # Measure Transformer efficiency
        transformer_metrics = measure_adaptation_efficiency(
            transformer_model, dataset, config
        )
        
        # Measure Mamba efficiency
        mamba_metrics = measure_adaptation_efficiency(
            mamba_model, dataset, config
        )
        
        # Compute delta
        delta = {
            "accuracy_delta": mamba_metrics["accuracy"] - transformer_metrics["accuracy"],
            "sharpness_delta": mamba_metrics["sharpness"] - transformer_metrics["sharpness"],
            "rank_delta": mamba_metrics["effective_rank"] - transformer_metrics["effective_rank"]
        }
        
        results[task_name] = {
            "transformer": transformer_metrics,
            "mamba": mamba_metrics,
            "delta": delta
        }
    
    return results
```

### Implementation Priority Assessment

**Primary Implementation Path:** Build on H-E1 codebase
- Reuse validated Transformer/Mamba models from H-E1
- Reuse SAM sharpness and effective rank from H-M2/H-M3
- Add 4-benchmark evaluation loop

**Fallback:** Simplified 2-benchmark comparison (GSM8K vs NQ only)

**Justification:** H-E1 already validated cross-architecture comparison on 2 tasks; H-M4 extends to 4 benchmarks for continuous correlation analysis.

---

## Experiment Specification

### Dataset

**Multi-Benchmark Suite (4 Benchmarks Spanning Retrieval Density Spectrum)**

| Benchmark | Retrieval Density | Test Size | Task Type |
|-----------|-------------------|-----------|-----------|
| GSM8K | 0.1 (low) | 1,319 | Sequential reasoning |
| MMLU | 0.5 (medium) | 14,042 | Mixed knowledge |
| HotpotQA | 0.7 (medium-high) | 7,405 | Multi-hop retrieval |
| Natural Questions | 0.9 (high) | 3,610 | Factual retrieval |

**Total Evaluation Samples:** 26,376

**Loading Information:**
- Method: HuggingFace datasets
- Identifiers: `gsm8k`, `cais/mmlu`, `hotpot_qa`, `natural_questions`
- Code:
```python
from datasets import load_dataset

datasets = {
    "gsm8k": load_dataset("gsm8k", "main", split="test"),
    "mmlu": load_dataset("cais/mmlu", "all", split="test"),
    "hotpotqa": load_dataset("hotpot_qa", "fullwiki", split="validation"),
    "nq": load_dataset("natural_questions", split="validation")
}

RETRIEVAL_DENSITY = {
    "gsm8k": 0.1,
    "mmlu": 0.5,
    "hotpotqa": 0.7,
    "nq": 0.9
}
```

### Models

#### Baseline Model (Transformer)

**Architecture:** TransformerWithLoRA
- Model Dimension: 512
- Heads: 8
- Layers: 4
- LoRA Configuration: rank=16, alpha=32, target_modules=["q_proj", "v_proj"]

**Loading Information:**
- Method: Custom implementation (H-E1 codebase)
- Identifier: TransformerBlockSimulated + LoRA wrapper
- Code:
```python
from models.transformer_lora import TransformerWithLoRA
transformer = TransformerWithLoRA(d_model=512, n_heads=8, n_layers=4, lora_rank=16)
```

#### Proposed Model (Mamba)

**Architecture:** MambaWithLoRA (validated in H-M1-M3)
- Model Dimension: 512
- State Dimension: 16
- Layers: 4
- LoRA Configuration: rank=16, alpha=32, target_modules=["in_proj"]

**Loading Information:**
- Method: Custom implementation (H-M2/M3 codebase)
- Code:
```python
from models.mamba_lora import MambaWithLoRA
mamba = MambaWithLoRA(d_model=512, d_state=16, n_layers=4, lora_rank=16)
```

#### Core Mechanism Implementation

```python
def test_task_dependent_transformation(config):
    """
    Core mechanism: Test correlation between retrieval density
    and adaptation efficiency delta across architectures.
    
    Gate: Spearman rho > 0.7 between retrieval_density and efficiency_delta
    
    Args:
        config: Experiment configuration
    
    Returns:
        gate_result: PASS/FAIL with metrics
    """
    # Retrieval density operationalization (from Phase 2B)
    RETRIEVAL_DENSITY = {
        "gsm8k": 0.1,      # Sequential reasoning, minimal retrieval
        "mmlu": 0.5,       # Mixed knowledge tasks
        "hotpotqa": 0.7,   # Multi-hop retrieval required
        "nq": 0.9          # Pure factual retrieval
    }
    
    results = {}
    
    for task_name in ["gsm8k", "mmlu", "hotpotqa", "nq"]:
        # Initialize fresh models
        transformer = create_transformer_model(config)
        mamba = create_mamba_model(config)
        
        dataset = load_task_dataset(task_name, config)
        
        # Train and evaluate Transformer + LoRA
        transformer = train_lora(transformer, dataset, config)
        transformer_acc = evaluate(transformer, dataset.test)
        transformer_sharpness = compute_sam_sharpness(transformer, dataset, epsilon=0.05)
        
        # Train and evaluate Mamba + LoRA
        mamba = train_lora(mamba, dataset, config)
        mamba_acc = evaluate(mamba, dataset.test)
        mamba_sharpness = compute_sam_sharpness(mamba, dataset, epsilon=0.05)
        
        # Compute efficiency delta (Mamba - Transformer)
        # Positive delta = Mamba better; Negative delta = Transformer better
        accuracy_delta = mamba_acc - transformer_acc
        
        results[task_name] = {
            "retrieval_density": RETRIEVAL_DENSITY[task_name],
            "transformer_acc": transformer_acc,
            "mamba_acc": mamba_acc,
            "accuracy_delta": accuracy_delta,
            "transformer_sharpness": transformer_sharpness,
            "mamba_sharpness": mamba_sharpness,
            "sharpness_delta": mamba_sharpness - transformer_sharpness
        }
    
    # Compute Spearman correlation: retrieval_density vs accuracy_delta
    densities = [results[t]["retrieval_density"] for t in results]
    deltas = [results[t]["accuracy_delta"] for t in results]
    
    from scipy.stats import spearmanr
    rho, p_value = spearmanr(densities, deltas)
    
    # Check monotonicity (no outliers)
    # Expected: higher retrieval density -> more negative delta (Transformer better)
    is_monotonic = all(
        deltas[i] >= deltas[i+1] 
        for i in range(len(deltas)-1)
    ) or all(
        deltas[i] <= deltas[i+1] 
        for i in range(len(deltas)-1)
    )
    
    gate_pass = abs(rho) > 0.7 and p_value < 0.01
    
    return {
        "spearman_rho": rho,
        "p_value": p_value,
        "is_monotonic": is_monotonic,
        "gate_pass": gate_pass,
        "task_results": results,
        "interpretation": "Negative rho indicates higher retrieval density leads to worse Mamba performance relative to Transformer"
    }
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Optimizer | AdamW | Standard for LoRA (validated in H-M3) |
| Learning Rate | 1e-4 | Conservative, validated in H-M3 |
| LR Schedule | Cosine decay | Smooth convergence |
| Batch Size | 4 | Memory constraint |
| Max Epochs | 5 | Consistent with prior hypotheses |
| Early Stopping | Loss plateau (patience=2) | Ensure convergence |
| Loss Function | CrossEntropyLoss | Language modeling |
| Weight Decay | 0.01 | Regularization |
| Gradient Clipping | 1.0 | Stability |
| Random Seed | 42 | Reproducibility |

**Per-Benchmark Training:**
- Each model (Transformer/Mamba) trained separately per task
- Fresh LoRA initialization for each task
- 8 total training runs (2 architectures × 4 tasks)

### Evaluation

**Primary Metrics:**

| Metric | Formula | Gate Threshold |
|--------|---------|----------------|
| Spearman rho | corr(retrieval_density, accuracy_delta) | abs(rho) > 0.7 |
| P-value | Statistical significance | p < 0.01 |

**Secondary Metrics:**

| Metric | Purpose |
|--------|---------|
| Per-task accuracy | Architecture comparison |
| Per-task sharpness delta | Landscape change verification |
| Monotonicity check | Pattern consistency |

**Metrics Loading Information:**
- Task Type: Correlation analysis + classification accuracy
- Library: scipy.stats, sklearn.metrics
- Code:
```python
from scipy.stats import spearmanr
from sklearn.metrics import accuracy_score

rho, p_value = spearmanr(retrieval_densities, accuracy_deltas)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Retrieval Density vs Accuracy Delta**: Scatter plot with 4 benchmarks, Spearman rho annotation, regression line

#### Additional Figures (LLM Autonomous)
1. **Architecture Comparison Bar Chart**: Per-task Transformer vs Mamba accuracy
2. **Sharpness Delta Heatmap**: Task × Architecture sharpness comparison
3. **Correlation Matrix**: All metrics cross-correlation
4. **Summary Dashboard**: Combined visualization of all gate metrics

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m4/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 4 benchmarks
2. abs(Spearman rho) > 0.7 between retrieval density and accuracy delta
3. p-value < 0.01 (statistical significance)

**Expected Outcome:**
- GSM8K (density=0.1): Positive or near-zero delta (Mamba competitive)
- MMLU (density=0.5): Slight negative delta
- HotpotQA (density=0.7): Moderate negative delta
- NQ (density=0.9): Large negative delta (Transformer clearly better)

**Expected Pattern:** Negative correlation (rho ~ -0.8 to -1.0) showing higher retrieval density leads to worse relative Mamba performance.

---

## Ablation Studies

### A-1: Retrieval Density Sensitivity
Test alternative retrieval density operationalizations:
- Expert judgment (current): 0.1, 0.5, 0.7, 0.9
- Binary classification: Sequential (0) vs Retrieval (1)
- Data-driven: Compute from attention patterns in pretrained Transformer

### A-2: Efficiency Metric Sensitivity
Test alternative efficiency metrics:
- Accuracy delta (primary)
- Sharpness delta
- Effective rank delta
- Combined efficiency score

---

## Appendix: Reference Implementations

### Cross-Architecture Efficiency Measurement

```python
def measure_adaptation_efficiency(model, dataset, config):
    """
    Measure adaptation efficiency for a single model on a task.
    Returns accuracy, sharpness, and effective rank.
    """
    # Train to convergence
    model = train_lora(model, dataset.train, config)
    
    # Measure metrics
    accuracy = evaluate(model, dataset.test)
    sharpness = compute_sam_sharpness(model, dataset, config.sam_epsilon)
    effective_rank = compute_effective_rank(model.get_lora_weights(), threshold=0.90)
    
    return {
        "accuracy": accuracy,
        "sharpness": sharpness,
        "effective_rank": effective_rank
    }
```

### Spearman Correlation with Significance

```python
from scipy.stats import spearmanr

def compute_correlation_with_significance(x, y, alpha=0.01):
    """
    Compute Spearman correlation with significance test.
    """
    rho, p_value = spearmanr(x, y)
    
    return {
        "rho": rho,
        "p_value": p_value,
        "significant": p_value < alpha,
        "direction": "positive" if rho > 0 else "negative"
    }
```

### Monotonicity Check

```python
def check_monotonicity(values):
    """
    Check if values are monotonically increasing or decreasing.
    """
    increasing = all(values[i] <= values[i+1] for i in range(len(values)-1))
    decreasing = all(values[i] >= values[i+1] for i in range(len(values)-1))
    return increasing or decreasing
```

---

## Research Sources

- [TransMamba: Fast Universal Architecture Adaption from Transformers to Mamba](https://arxiv.org/pdf/2502.15130)
- [MambaPEFT: Exploring Parameter-Efficient Fine-Tuning for Mamba](https://arxiv.org/pdf/2411.03855)
- [Mamba-Transformer Hybrids Analysis](https://vinayakajyothi.com/blog/papers-2026-03-12-mamba-transformer-hybrids/)
- [Retrievit: In-context Retrieval Capabilities of Architectures](https://arxiv.org/pdf/2603.02874)
- [MTMamba++: Multi-Task Dense Scene Understanding](https://arxiv.org/pdf/2408.15101)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis

| Event | Timestamp | Phase |
|-------|-----------|-------|
| H-M4 set to IN_PROGRESS | 2026-08-19T04:47:20 | Hypothesis Loop |
| Phase 2C experiment design started | 2026-08-19 | Phase 2C |
| Phase 2C experiment design completed | 2026-08-19 | Phase 2C |

---

*MCP Tools: Not available (no-mcp mode)*
*Specifications based on validated H-E1/H-M1/H-M2/H-M3 results and web research*
*Next Phase: Phase 3 - Implementation Planning*
