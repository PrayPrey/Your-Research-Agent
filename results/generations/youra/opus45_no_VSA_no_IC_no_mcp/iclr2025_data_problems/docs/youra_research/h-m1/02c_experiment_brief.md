# Experiment Design: H-M1

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** Perplexity filtering controls the quality-diversity tradeoff: intermediate thresholds (p30-p60) outperform both extremes (no filter, p90) because they retain diverse content while excluding noise.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Tests causal mechanism behind dose-response relationship.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 validated)
**Gate Status:** MUST_WORK - Pending validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (Dose-Response Existence - VALIDATED)

### Gate Condition
Filtered models (p30-p60) converge faster than unfiltered baseline AND achieve higher benchmark scores than both extremes (no-filter, p90).

---

## Continuation Context

### Previous Hypothesis Results (H-E1)

H-E1 established:
- Non-monotonic dose-response exists for both perplexity and dedup parameters
- Perplexity peak at ~p54 (threshold 53.9)
- Deduplication peak at ~1.1 stringency level
- Quadratic model selected over linear (AIC)

**Key Insight to Build On:** The concave relationship exists - now we test the mechanism (noise dilution at low thresholds causes slower convergence).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using Phase 2A/2B research context and H-E1 results*

Key findings:
1. **Training loss curves** reveal convergence dynamics
2. **Sample efficiency** measurable via loss-at-step-N comparisons
3. **Token quality** impacts gradient signal-to-noise ratio
4. Standard practice: compare loss curves normalized by token count

### Code Analysis

Reuse H-E1 infrastructure:
- Same RedPajama-v2 dataset with `ccnet_perplexity` field
- Same GPT-2 125M architecture
- Same benchmark evaluation pipeline
- Add: loss curve logging at regular intervals

---

## Experiment Specification

### Dataset

**Dataset**: RedPajama-v2 (English subset)
**Type**: standard (web corpus with quality signals)

**Dataset Details:**
- **Source**: togethercomputer/RedPajama-Data-v2
- **Token Budget**: 10B tokens per configuration (same as H-E1)
- **Quality Signals**: `ccnet_perplexity` (KenLM 5-gram)

**Parameter Configurations (Focused Sweep):**

| Config ID | Perplexity Threshold | Rationale |
|-----------|---------------------|-----------|
| M1-C0 | None (raw) | Extreme: no filtering |
| M1-C1 | p20 | Light filtering |
| M1-C2 | p40 | Moderate filtering |
| M1-C3 | p50 | Near optimal (from H-E1) |
| M1-C4 | p60 | Near optimal (from H-E1) |
| M1-C5 | p80 | Strict filtering |
| M1-C6 | p90 | Extreme: very strict |

**Loading Information:**
```python
from datasets import load_dataset
import numpy as np

def load_filtered_data(threshold_percentile):
    """Load RedPajama-v2 with perplexity filtering."""
    dataset = load_dataset("togethercomputer/RedPajama-Data-v2", 
                           name="default", 
                           split="train",
                           streaming=True)
    
    if threshold_percentile is None:
        return dataset  # No filtering
    
    # Filter by percentile threshold
    # Note: Lower perplexity = higher quality in CCNet convention
    filtered = dataset.filter(
        lambda x: x['ccnet_perplexity'] < compute_threshold(threshold_percentile)
    )
    return filtered
```

### Models

**Architecture**: GPT-2 125M (identical to H-E1)

**Configuration:**
- Layers: 12
- Hidden size: 768
- Attention heads: 12
- Parameters: ~125M
- Context length: 1024

**Loading:**
```python
from transformers import GPT2Config, GPT2LMHeadModel

config = GPT2Config(
    vocab_size=50257,
    n_positions=1024,
    n_embd=768,
    n_layer=12,
    n_head=12,
)
model = GPT2LMHeadModel(config)  # Train from scratch
```

### Training Protocol

**Optimizer**: AdamW (β1=0.9, β2=0.95, weight_decay=0.1)
**Learning Rate**: 6e-4 (peak), cosine decay with 2000 step warmup
**Batch Size**: 512 sequences (524k tokens/batch)
**Tokens**: 10B tokens per configuration
**Seeds**: 1 (seed=42)

**Loss Logging** (Critical for H-M1):
```python
# Log loss at regular intervals for convergence analysis
LOG_INTERVAL = 100  # steps
loss_history = []

for step, batch in enumerate(train_loader):
    loss = model(batch).loss
    
    if step % LOG_INTERVAL == 0:
        loss_history.append({
            'step': step,
            'tokens_seen': step * batch_size * seq_length,
            'loss': loss.item()
        })
```

### Evaluation

**Primary Metrics**:
1. **Convergence Rate**: Steps to reach loss threshold (e.g., loss=3.5)
2. **Final Loss**: Loss at training end
3. **Sample Efficiency**: Loss at fixed token count (e.g., 1B, 5B, 10B tokens)
4. **Benchmark Ensemble Score**: PC1 of (HellaSwag, ARC-Easy, PIQA, WinoGrande)

**Convergence Analysis:**
```python
def analyze_convergence(loss_histories: dict):
    """
    Compare convergence rates across configurations.
    
    Args:
        loss_histories: {config_id: [(step, loss), ...]}
    Returns:
        Convergence metrics per configuration
    """
    results = {}
    
    for config_id, history in loss_histories.items():
        steps = np.array([h['step'] for h in history])
        losses = np.array([h['loss'] for h in history])
        
        # Metric 1: Steps to reach loss=3.5
        threshold_idx = np.where(losses < 3.5)[0]
        steps_to_threshold = steps[threshold_idx[0]] if len(threshold_idx) > 0 else np.inf
        
        # Metric 2: Final loss
        final_loss = losses[-1]
        
        # Metric 3: AUC (lower = faster convergence)
        auc = np.trapz(losses, steps)
        
        results[config_id] = {
            'steps_to_threshold': steps_to_threshold,
            'final_loss': final_loss,
            'convergence_auc': auc
        }
    
    return results
```

**Success Criteria (Mechanism Validation):**
- **Primary**: Moderate filtering (p40-p60) converges faster than no-filter (steps_to_threshold comparison)
- **Secondary**: Moderate filtering achieves higher benchmark score than both extremes
- **Mechanism Indicator**: Monotonic improvement in convergence rate from p0 to ~p50, then decline from ~p50 to p90

**Statistical Test:**
- Compare convergence AUC: p50 < p0 (one-sided t-test equivalent via bootstrap)
- Effect size: Cohen's d for convergence rate difference

### Visualization Requirements

#### Required Figures
1. **Loss Curves**: Training loss vs step/tokens for all 7 configurations (overlay plot)
2. **Convergence Comparison**: Bar chart of steps-to-threshold per configuration
3. **Quality-Diversity Tradeoff**: Scatter plot of convergence rate vs benchmark score

#### Additional Figures
- Loss at fixed token checkpoints (1B, 5B, 10B)
- Benchmark breakdown per configuration

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs for all 7 configurations
2. Filtered configurations (p40-p60) show faster convergence than unfiltered
3. Both extremes (p0, p90) underperform moderate filtering on benchmarks

**Mechanism Verification:**
- Pre-condition: Loss curves logged at consistent intervals
- Activation indicator: Convergence AUC decreases with initial filtering
- Success metric: p50 converges >10% faster than p0

---

## Appendix: Reference Implementations

### Loss Curve Logging
```python
import wandb

def train_with_logging(model, dataloader, config_id):
    wandb.init(project="h-m1-noise-dilution", name=config_id)
    
    for step, batch in enumerate(dataloader):
        loss = train_step(model, batch)
        
        if step % 100 == 0:
            wandb.log({
                "loss": loss,
                "step": step,
                "tokens": step * BATCH_TOKENS
            })
    
    wandb.finish()
```

### Convergence Rate Calculation
```python
def convergence_rate(loss_curve, target_loss=3.5):
    """Calculate steps to reach target loss."""
    for step, loss in loss_curve:
        if loss < target_loss:
            return step
    return float('inf')
```

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE - state in prompt)
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design initiated
- Prerequisites: H-E1 validated (dose-response exists)
- Status: IN_PROGRESS

---

*MCP Tools Used: None available (ablation mode)*
*Builds on H-E1 validated results: perplexity peak ~p54*
*Next Phase: Phase 3 - Implementation Planning*
