# Experiment Design: H-M2

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Middle layers (50-70% depth) achieve highest AUROC exhibiting inverted-U pattern
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates WHERE in the model correctness signal peaks.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (PASS: AUROC=0.8854), H-M1 (PASS: Identity=100%, Overhead=-3.4%)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (Forward pass extraction validated)

### Gate Condition
- **Primary:** L_60% AUROC > L_100% AUROC (middle beats final layer)
- **Secondary:** L_60% AUROC > L_25% AUROC (middle beats early layer)
- **Pattern:** Inverted-U curve across layer depths

---

## Continuation Context

### Previous Hypothesis Results (H-M1)

**Proven Components from H-M1:**
- `HiddenStateExtractor`: Context-managed hook verified non-intrusive
- `Hook Pattern`: `output[0].detach().cpu()` + `return None` confirmed safe
- `Layer Access`: `model.model.layers[idx]` captures hidden states

**Hyperparameters Confirmed:**
- `max_new_tokens`: 128
- `torch_dtype`: float16
- Hook overhead: negligible (-3.4%)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No directly relevant results for layer-wise probing. Diffusers/UNet examples returned.

### Archon Code Examples

UNet layer summary examples returned - not directly applicable to LLM probing.

### Exa GitHub Implementations

**Highly Relevant Implementations Found:**

1. **sonde** (github.com/aniruddh-alt/sonde)
   - Purpose: Layer-wise linear probe sweeps on HuggingFace transformers
   - Key class: `LayerProbeSweepRunner`
   - Layer syntax: `layers_output:0-31` for range, `layers_output:*` for all
   - Metrics: Test-set AUROC, selectivity controls
   - Best-layer selection on validation before test eval

2. **tool-probe** (github.com/oleksandr-shyshchuk/tool-probe)
   - Finding: **Layer sweep shows F1 peaks in upper-middle layers**
   - Example: L26 (Llama-3B), L24 (Qwen) - approximately 65-85% depth
   - Architecture: Linear probes on last-token hidden state
   - Linear vs MLP: MLP gives only ~1 pp gain, linear sufficient

3. **linear-probe** (github.com/aragorn-w/linear-probe)
   - Implements Alain & Bengio (2016) layer probing
   - Train `nn.Linear(d_model, 1)` per layer on frozen representations
   - Word-level train/test split prevents leakage
   - Shows deeper layers produce more separable representations

4. **LLM-Probing-Classifiers** (github.com/gmeyoyan/LLM-Probing-Classifiers)
   - Cache hidden states to disk first, then sweep probe variants
   - Attention-based pooling options available
   - Per-layer training without re-running LLM

### 🎯 Implementation Priority Assessment

**CRITICAL: Use existing layer-sweep patterns**

**Recommended Implementation Path:**
- Primary: Adapt `sonde` LayerProbeSweepRunner pattern
- Fallback: Custom loop with `model.model.layers[i]` hooks from H-M1
- Justification: sonde provides val/test split discipline, H-M1 hook pattern proven

### Code Analysis (Serena MCP)

Not applicable - no codebase to analyze. Using Exa implementations.

### Literature Findings (Exa Web Search)

1. **"Hallucination Is Linearly Decodable from Mid-Layer Hidden States"** (arxiv 2606.02628)
   - Finding: Peak probing layers at **13-18 of 32** (40-56% depth) for Llama/Mistral
   - Qwen: blocks 19-25 of 28 (68-89% depth)
   - Linear probe achieves 0.904-1.000 AUROC
   - MLP probes rarely surpass linear by >0.01 AUROC

2. **"Truth Gradient at SemEval-2026"** (belief detection)
   - Layer-wise probing confirms belief information peaks at **layer 16/24 (67% depth)**

3. **"Insights into LLM Long-Context Failures"** (EMNLP 2024)
   - Probing reveals disconnect between encoding and output generation
   - Supports middle-layer semantic encoding hypothesis

---

## Experiment Specification

### Dataset

**Name:** TriviaQA + Natural Questions (from H-E1 validation)
**Type:** standard
**Source:** HuggingFace datasets

**Statistics:**
- Train: 9,500 samples (from H-E1)
- Validation: 1,700 samples (from H-E1)
- Pre-computed hidden states from H-E1 run

**Loading Information** (for Phase 4 download):
- Method: HuggingFace
- Identifier: `trivia_qa`, `natural_questions`
- Code: `load_dataset("trivia_qa", "rc.wikipedia")["validation"]`

**Note:** Can reuse hidden states extracted in H-E1 if stored per-layer, otherwise re-extract at all 8 target layers.

### Models

#### Baseline Model

**Architecture:** Llama-3-8B-Instruct (same as H-E1, H-M1)
**Source:** meta-llama/Meta-Llama-3-8B-Instruct
**Total Layers:** 32
**Hidden Dim:** 4096

**Loading Information** (for Phase 4 download):
- Method: HuggingFace
- Identifier: `meta-llama/Meta-Llama-3-8B-Instruct`
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct", torch_dtype=torch.float16)`

#### Proposed Model

**Architecture:** Linear probe per layer depth

**Core Mechanism Implementation:**

```python
# Core Mechanism: Layer-wise Probe Sweep
# Based on: sonde, tool-probe, H-M1 HiddenStateExtractor

import torch
import torch.nn as nn
from typing import Dict, List

# Layer indices to probe (8 depths: 12.5% to 100%)
# For Llama-3-8B with 32 layers: [4, 8, 12, 16, 19, 24, 28, 31]
LAYER_DEPTHS = [0.125, 0.25, 0.375, 0.5, 0.6, 0.75, 0.875, 1.0]

def get_layer_indices(num_layers: int = 32) -> List[int]:
    """Convert depth fractions to layer indices."""
    return [max(0, int(d * num_layers) - 1) for d in LAYER_DEPTHS]

class LinearProbe(nn.Module):
    """Single-layer linear probe for correctness prediction."""
    def __init__(self, hidden_dim: int = 4096):
        super().__init__()
        self.fc = nn.Linear(hidden_dim, 1)
    
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        # hidden_state: (B, hidden_dim) - last token
        return torch.sigmoid(self.fc(hidden_state))

def run_layer_sweep(
    hidden_states_per_layer: Dict[int, torch.Tensor],
    labels: torch.Tensor,
    train_idx: List[int],
    val_idx: List[int],
) -> Dict[int, float]:
    """Train probe at each layer, return layer -> val AUROC."""
    results = {}
    for layer_idx, states in hidden_states_per_layer.items():
        probe = LinearProbe(states.shape[-1])
        # Train on train_idx, eval on val_idx
        auroc = train_and_eval_probe(probe, states, labels, train_idx, val_idx)
        results[layer_idx] = auroc
    return results

# Integration: Extract hidden states at all 8 layer indices using H-M1 hooks
# Compare: L_60% (layer 19) vs L_100% (layer 31) vs L_25% (layer 8)
```

### Training Protocol

**Optimizer:** AdamW (from literature)
- Parameters: lr=1e-2, weight_decay=1e-4

**Learning Rate:** 1e-2
- Source: tool-probe, linear-probe repos

**Schedule:** None (short training)

**Batch Size:** 256
- Source: Standard for probe training

**Epochs:** 10-20 (until convergence)
- Source: sonde default

**Loss Function:** Binary Cross-Entropy

**Seeds:** 1 (PoC mode)

### Evaluation

**Primary Metrics:**
- AUROC per layer depth

**Success Criteria:**
- L_60% AUROC > L_100% AUROC (middle > final)
- L_60% AUROC > L_25% AUROC (middle > early)
- Visual inverted-U pattern in layer-AUROC plot

**Expected Baseline Performance** (from H-E1):
- Layer 19 (60% depth): AUROC ~0.88 (from H-E1 validation)
- Final layer: Expected lower based on literature (hallucination paper)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary_classification
- Library: sklearn.metrics or torchmetrics
- Code: `sklearn.metrics.roc_auc_score(labels, probe_scores)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: L_60% vs L_100% vs L_25% AUROC bar chart

#### Additional Figures (LLM Autonomous)
- **Layer-AUROC Curve**: All 8 layers plotted (x=layer depth, y=AUROC)
- **Inverted-U Pattern Visualization**: Highlight peak at 50-70% depth

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: YES - layer-wise hidden state extraction via hooks
- `mechanism_isolatable`: YES - separate probe per layer
- `baseline_measurable`: YES - final layer (L_100%) serves as baseline

### Architecture Compatibility
- Model: Llama-3-8B-Instruct with 32 layers
- Hook access: `model.model.layers[i]` validated in H-M1
- Hidden dim: 4096 confirmed

### Activation Indicators
- `mechanism_log_message`: "Extracting hidden states from layer {i}"
- `tensor_shape_change`: (B, seq_len, 4096) → (B, 4096) via last-token selection
- `metric_delta_expected`: AUROC difference between middle vs final layers

### Mechanism Verification Code

```python
def verify_inverted_u_pattern(layer_aurocs: Dict[int, float]) -> dict:
    """Verify H-M2 hypothesis: middle layers beat early and final."""
    layers = sorted(layer_aurocs.keys())
    num_layers = max(layers) + 1
    
    # Get AUROC at key depths
    early_layer = layers[1]  # ~25% depth
    middle_layer = layers[4]  # ~60% depth  
    final_layer = layers[-1]  # 100% depth
    
    auroc_early = layer_aurocs[early_layer]
    auroc_middle = layer_aurocs[middle_layer]
    auroc_final = layer_aurocs[final_layer]
    
    # Gate checks
    middle_beats_final = auroc_middle > auroc_final
    middle_beats_early = auroc_middle > auroc_early
    
    # Find peak layer
    peak_layer = max(layer_aurocs, key=layer_aurocs.get)
    peak_depth = (peak_layer + 1) / num_layers
    
    return {
        "middle_beats_final": middle_beats_final,
        "middle_beats_early": middle_beats_early,
        "peak_layer": peak_layer,
        "peak_depth_pct": peak_depth * 100,
        "inverted_u_detected": middle_beats_final and middle_beats_early,
        "gate_satisfied": middle_beats_final,  # Primary criterion
    }
```

### Success Criteria
- `hypothesis_support_metric`: AUROC at 60% depth - AUROC at 100% depth
- `hypothesis_support_threshold`: > 0 (direction-based for PoC)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error at all 8 layer depths
2. L_60% AUROC > L_100% AUROC (middle beats final)

---

## Appendix: Reference Implementations

| Source | URL | Relevance |
|--------|-----|-----------|
| sonde | github.com/aniruddh-alt/sonde | Layer sweep runner pattern |
| tool-probe | github.com/oleksandr-shyshchuk/tool-probe | Layer sweep F1 peak finding |
| linear-probe | github.com/aragorn-w/linear-probe | Alain & Bengio probing |
| Hallucination Mid-Layer | arxiv.org/abs/2606.02628 | Peak at 40-56% depth |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- 2026-08-18: H-M2 set to IN_PROGRESS
- Prerequisites H-E1 (AUROC=0.8854) and H-M1 (Identity=100%) both validated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
