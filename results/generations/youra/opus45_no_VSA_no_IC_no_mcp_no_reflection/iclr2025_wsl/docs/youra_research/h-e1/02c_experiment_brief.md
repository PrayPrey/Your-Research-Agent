# Experiment Design: H-E1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis Statement:** Heavy-tailed exponents can be computed with bounded variance (σ < 0.5) for ViT attention weight matrices using the Hill estimator on 100+ ViT models from Hugging Face.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
σ(α) < 0.5 for heavy-tailed exponents computed across 100+ ViT models from HuggingFace Model Hub.

---

## Continuation Context

**Previous Hypothesis Results:** None (first hypothesis in chain)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable — used WebSearch fallback*

**Query 1: Heavy-tailed weight analysis**
- WeightWatcher (WW) is an open-source diagnostic tool for analyzing DNNs based on Heavy-Tailed Self-Regularization (HT-SR) theory
- Uses Random Matrix Theory (RMT) and Statistical Mechanics
- Key insight: State-of-the-art models possess heavy-tailed spectral weight distributions

**Query 2: Martin & Mahoney theory**
- Heavy-Tailed Self-Regularization (HT-SR) framework uses Universality properties of Heavy-Tailed Random Matrix Theory
- The Hill estimator computes power law tail exponents for singular value distributions
- Spectral density of DNN weight matrices follows power law p(x) ∝ x^(-α)

### Archon Code Examples

*Archon MCP unavailable — used WebSearch fallback*

```python
# WeightWatcher basic usage (from official repo)
import weightwatcher as ww
model = models.vgg19_bn(pretrained=True)
watcher = ww.WeightWatcher(model=model)
details = watcher.analyze()
summary = watcher.get_summary(details)
```

### Exa GitHub Implementations

**Repository 1**: CalculatedContent/WeightWatcher (⭐ 500+)
- **URL**: https://github.com/CalculatedContent/WeightWatcher
- **Relevance**: Official implementation of heavy-tailed weight analysis by Martin & Mahoney
- **Architecture**: Pure Python + NumPy/SciPy for eigenvalue decomposition
- **Key Metrics Computed**:
  - `alpha`: Power law exponent (lower = better generalization)
  - `alpha_weighted`: Scale-adjusted form
  - `log_spectral_norm`: Largest eigenvalue log
  - `stable_rank`: Frobenius/spectral norm ratio
- **Transformer Support**: Documentation confirms average `alpha` can compare transformer models
- **Installation**: `pip install weightwatcher`

**Repository 2**: YefanZhou/TempBalance (NeurIPS 2023 Spotlight)
- **URL**: https://github.com/yefanzhou/tempbalance
- **Relevance**: Uses heavy-tailed layer-wise weight analysis for training
- **Key insight**: Layer-wise α values inform training dynamics

### 🎯 Implementation Priority Assessment

**CRITICAL: For H-E1, WeightWatcher is the canonical implementation**

**Recommended Implementation Path:**
- Primary: WeightWatcher (`pip install weightwatcher`)
- Fallback: Custom Hill estimator implementation if WeightWatcher fails on ViT
- Justification: WeightWatcher is Martin & Mahoney's official tool, explicitly supports transformers

### Code Analysis (Serena MCP)

*Skipped* - WeightWatcher code is well-documented and API is clear from official README

---

## Experiment Specification

### Dataset

**Dataset**: HuggingFace Model Hub ViT Models
**Type**: programmatic-api (real pretrained models via API)

**Specification:**
- Source: HuggingFace Hub API (`huggingface_hub` library)
- Filter: `pipeline_tag=image-classification`, architecture contains "vit"
- Target: 100+ unique ViT model checkpoints
- Model families: google/vit-*, facebook/deit-*, microsoft/swin-*, etc.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Hub API
- Identifier: Filter by `pipeline_tag` and model name pattern
- Code:
```python
from huggingface_hub import HfApi, list_models
from transformers import AutoModel

api = HfApi()
vit_models = list(api.list_models(
    filter="image-classification",
    search="vit",
    sort="downloads",
    direction=-1,
    limit=150
))

# Load each model
for model_info in vit_models:
    model = AutoModel.from_pretrained(model_info.modelId)
```

### Models

#### Baseline Model

**Architecture**: N/A (no baseline model needed — this is a measurement hypothesis)

**Note**: H-E1 is an EXISTENCE hypothesis testing whether heavy-tailed exponents CAN BE COMPUTED with bounded variance. There is no "baseline vs proposed" comparison — the experiment measures α variance across ViT models.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: Various ViT model IDs from Hub
- Code:
```python
from transformers import AutoModel
model = AutoModel.from_pretrained("google/vit-base-patch16-224")
```

#### Proposed Model

**Architecture**: Measurement pipeline (not a trained model)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Heavy-Tailed Exponent Computation for ViT
# Based on: WeightWatcher (Martin & Mahoney)

import weightwatcher as ww
import numpy as np
from transformers import AutoModel
from huggingface_hub import list_models

def compute_alpha_for_vit(model_id: str) -> dict:
    """
    Compute heavy-tailed exponent α for a ViT model.
    
    Args:
        model_id: HuggingFace model identifier
    Returns:
        dict with layer-wise alpha values and statistics
    """
    # Load model
    model = AutoModel.from_pretrained(model_id)
    
    # Initialize WeightWatcher
    watcher = ww.WeightWatcher(model=model)
    
    # Analyze all weight matrices
    details = watcher.analyze()
    
    # Extract alpha values for attention layers
    attention_alphas = details[
        details['layer_name'].str.contains('attention|qkv|query|key|value')
    ]['alpha'].values
    
    return {
        'model_id': model_id,
        'alpha_mean': np.mean(attention_alphas),
        'alpha_std': np.std(attention_alphas),
        'alpha_values': attention_alphas.tolist(),
        'n_layers': len(attention_alphas)
    }

def run_experiment(n_models: int = 100) -> dict:
    """
    Run H-E1 experiment: compute α for n_models ViT models.
    
    Returns:
        dict with aggregated results and variance statistics
    """
    # Get ViT models from HuggingFace
    vit_models = list(list_models(
        filter="image-classification",
        search="vit",
        sort="downloads",
        direction=-1,
        limit=n_models + 50  # buffer for failures
    ))
    
    results = []
    for model_info in vit_models[:n_models]:
        try:
            result = compute_alpha_for_vit(model_info.modelId)
            results.append(result)
        except Exception as e:
            print(f"Skipped {model_info.modelId}: {e}")
    
    # Aggregate statistics
    all_alphas = [r['alpha_mean'] for r in results]
    
    return {
        'n_models': len(results),
        'alpha_global_mean': np.mean(all_alphas),
        'alpha_global_std': np.std(all_alphas),  # THIS IS σ(α)
        'gate_passed': np.std(all_alphas) < 0.5,
        'results': results
    }
```

### Training Protocol

**N/A** - H-E1 is a measurement experiment, not a training experiment.

**Protocol:**
- No training required
- Load pretrained models from HuggingFace
- Extract weight matrices
- Compute α via WeightWatcher Hill estimator
- Aggregate statistics across 100+ models

**Seeds**: 1 (deterministic computation)

### Evaluation

**Primary Metric:** σ(α) — standard deviation of heavy-tailed exponents across ViT models

**Success Criteria:**
- Gate: σ(α) < 0.5
- Secondary: α values fall in expected range [1.5, 4.0]

**Expected Results (from research):**
- Martin & Mahoney found α ∈ [2, 6] for well-trained CNNs
- ViTs should show similar range if HT-SR theory applies

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical measurement
- Library: NumPy (np.std, np.mean)
- Code:
```python
import numpy as np
alpha_values = [r['alpha_mean'] for r in results]
sigma_alpha = np.std(alpha_values)
gate_passed = sigma_alpha < 0.5
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: σ(α) vs threshold (0.5) bar chart

#### Additional Figures (LLM Autonomous)
- Histogram of α values across all ViT models
- Box plot of α by model family (google/vit, facebook/deit, etc.)
- Scatter plot of α vs model size (parameters)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on 100+ ViT models
2. σ(α) < 0.5 (bounded variance)

---

## Appendix: Reference Implementations

### A. Web Search Sources (Archon/Exa unavailable)

**Source 1**: WeightWatcher GitHub
- **URL**: https://github.com/CalculatedContent/WeightWatcher
- **Query Used**: "weightwatcher PyTorch heavy-tailed neural network weight analysis Hill estimator"
- **Relevance**: Official implementation by theory authors
- **Used For**: Core mechanism implementation, API patterns

**Source 2**: TempBalance (NeurIPS 2023)
- **URL**: https://github.com/yefanzhou/tempbalance
- **Query Used**: Same as above
- **Relevance**: Layer-wise weight analysis validation
- **Used For**: Confirming heavy-tailed analysis applicable to modern architectures

**Source 3**: HuggingFace ViT Documentation
- **URL**: https://huggingface.co/docs/transformers/model_doc/vit
- **Query Used**: "huggingface transformers list all vit models filter image-classification"
- **Relevance**: Model loading API
- **Used For**: Dataset specification (programmatic API access)

### B. GitHub Implementations

**Repository**: CalculatedContent/WeightWatcher
- **URL**: https://github.com/CalculatedContent/WeightWatcher
- **Key Code**:
```python
# Official WeightWatcher usage
import weightwatcher as ww
watcher = ww.WeightWatcher(model=model)
details = watcher.analyze()  # Returns DataFrame with alpha per layer
```
- **Used For**: Pseudo-code generation, metric definitions

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

### D. Previous Hypothesis Context

**Previous Context**: None - H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Web Search | HuggingFace ViT docs |
| Model loading | Web Search | HuggingFace Transformers |
| α computation | GitHub | WeightWatcher repo |
| Hill estimator | GitHub | WeightWatcher repo |
| Success threshold | Phase 2B | verification_plan.md |
| Expected α range | Research | Martin & Mahoney papers |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-29

### Workflow History for This Hypothesis
- Phase 2C started: 2026-08-29
- Experiment design completed: 2026-08-29

---

*MCP Tools Used: WebSearch (Archon/Exa unavailable)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
