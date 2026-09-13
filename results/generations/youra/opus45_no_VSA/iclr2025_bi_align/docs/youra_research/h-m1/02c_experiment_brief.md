# Experiment Design: H-M1

**Date:** 2026-08-08
**Author:** Anonymous
**Hypothesis Statement:** BAI remains decodable from model hidden states (AUROC ≥0.7) after adversarial gradient reversal removes reward-predictive variance, while reward probe R² degrades <2%.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates representational independence via adversarial probing.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (PASS, AUROC 0.9836)
**Gate Status:** MUST_WORK (AUROC ≥0.7)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED)

### Gate Condition
BAI remains decodable from model hidden states (AUROC ≥0.7) after adversarial gradient reversal removes reward-predictive variance, while reward probe R² degrades <2%.

---

## Continuation Context

Building on H-E1 validation: Agency proxies achieved mean AUROC 0.9836, confirming reliable extraction. H-M1 tests whether BAI (computed from these proxies) represents an independent dimension in model representation space.

### Previous Hypothesis Results (H-E1)
- Mean AUROC: 0.9836
- All 4 proxies > 0.5 baseline
- Clarifying Question: 0.9949, Option Enumeration: 0.9840, Epistemic Hedging: 0.9880, Explicit Deferral: 0.9676

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "gradient reversal adversarial probing experiment design"**
- Limited direct results for gradient reversal in NLP probing
- Diffusion model references found (offset noise, perturbed attention)
- Key insight: Archon KB lacks specific domain adaptation/adversarial probing papers

**Query 2: "linear probing hidden states transformer representation"**
- T5EncoderModel usage for extracting last_hidden_states
- Transformer2D attention processing patterns
- Key insight: Use `outputs.last_hidden_state` for probing

**Recommendation:** Rely on Exa/academic sources for gradient reversal layer implementation details.

### Archon Code Examples

**Query 1: "gradient reversal layer PyTorch"**
- No direct gradient reversal examples found
- Diffusion pipeline patterns available

**Query 2: "linear probe classifier hidden states"**
- T5 encoder example: `outputs.last_hidden_state` extraction
- Attention processor patterns for hidden state manipulation

**Code Pattern (T5 hidden state extraction):**
```python
from transformers import AutoTokenizer, T5EncoderModel
tokenizer = AutoTokenizer.from_pretrained("google-t5/t5-small")
model = T5EncoderModel.from_pretrained("google-t5/t5-small")
outputs = model(input_ids=input_ids)
last_hidden_states = outputs.last_hidden_state
```

**Note:** Gradient reversal layer implementation will need external sources (Exa/GitHub).

### Exa GitHub Implementations

**Query 1: Gradient Reversal Layer Implementations**

**Repository 1**: [janfreyberg/pytorch-revgrad](https://github.com/janfreyberg/pytorch-revgrad) ⭐158
- **Relevance**: Minimal, well-tested gradient reversal layer
- **Key Code**:
  ```python
  from pytorch_revgrad import RevGrad
  model = torch.nn.Sequential(
      torch.nn.Linear(10, 5),
      torch.nn.Linear(5, 2),
      RevGrad()  # Reverses gradients during backprop
  )
  ```
- **Install**: `pip install pytorch-revgrad`

**Repository 2**: [CuthbertCai/pytorch_DANN](https://github.com/CuthbertCai/pytorch_DANN) ⭐215
- **Relevance**: Full DANN implementation with domain adaptation
- **Results**: MNIST-M source only 0.52 → DANN 0.76
- **Paper**: Ganin & Lempitsky "Unsupervised Domain Adaptation by Backpropagation"

**Repository 3**: [tadeephuy/GradientReversal](https://github.com/tadeephuy/GradientReversal) ⭐131
- **Relevance**: Clean GRL implementation with visualization
- **Key insight**: During forward pass, GRL = identity; during backward, gradient × -α

**Query 2: Linear Probing Implementations**

**Repository 4**: [center-for-humans-and-machines/transformer-heads](https://github.com/center-for-humans-and-machines/transformer-heads) ⭐295
- **Relevance**: Toolkit for attaching/training probes on transformers
- **Use case**: Training linear probes on intermediate layers

**Repository 5**: [ariahw/rl-rewardhacking](https://github.com/ariahw/rl-rewardhacking/blob/main/src/probe.py)
- **Relevance**: DIRECTLY RELEVANT - Probe training with AUROC evaluation
- **Key Code**:
  ```python
  from sklearn.linear_model import LogisticRegression
  from sklearn.metrics import roc_auc_score
  
  class Probe:
      def fit(self, acts: torch.Tensor, labels: torch.Tensor, layers: list[int]):
          # acts dimension: n_layers x n_samples x hidden_dim
          ...
      def predict(self, acts: torch.Tensor) -> np.ndarray:
          ...
  ```
- **Metrics**: accuracy, precision, recall, AUROC, ROC curve

**Repository 6**: [scasella/activation-probes-claim-correctness](https://github.com/scasella/activation-probes-claim-correctness)
- **Relevance**: Claim-level correctness probes on Llama activations
- **Backbone**: Llama 3.1 8B
- **Method**: Linear probes on hidden activations

**Serena Analysis Needed**: false (code patterns clear)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Use Case |
|----------|--------|----------|
| 1 | Ganin & Lempitsky DANN (pytorch_DANN, pytorch-revgrad) | Gradient reversal layer |
| 2 | ariahw/rl-rewardhacking probe.py | Linear probing with AUROC |
| 3 | transformer-heads library | Probe attachment to transformers |

**Recommended Implementation Path:**
- Primary: `pytorch-revgrad` (158⭐, pip installable, torch.compile compatible)
- Fallback: Custom GRL from `tadeephuy/GradientReversal` (cleaner code)
- Justification: Established implementations from domain adaptation literature; probe code from reward hacking research directly applicable

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Gradient reversal layer and linear probing patterns well-documented in found repositories.

---

## Experiment Specification

### Dataset

**Dataset 1: HH-RLHF (Anthropic)**
- **Type:** standard
- **Source:** HuggingFace Datasets
- **Content:** Human preference data (chosen/rejected pairs) for helpfulness and harmlessness
- **Splits:** train/test for helpfulness and harmlessness
- **Sample count:** ~170k preference pairs
- **Format:** JSONL with "chosen" and "rejected" text fields

**Dataset 2: RewardBench (Allen AI)**
- **Type:** standard
- **Source:** HuggingFace Datasets
- **Content:** Reward model evaluation benchmark
- **Use:** Validation set for cross-dataset generalization

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `Anthropic/hh-rlhf`, `allenai/reward-bench`
- Code:
```python
from datasets import load_dataset

# HH-RLHF
hh_rlhf = load_dataset("Anthropic/hh-rlhf")
# Subsets: helpful-base, helpful-online, helpful-rejection-sampled, harmless-base

# RewardBench (for validation)
reward_bench = load_dataset("allenai/reward-bench")
```

### Models

#### Baseline Model

**Primary Model: Llama-3-8B**
- **Type:** Causal LM (decoder-only transformer)
- **Parameters:** 8B
- **Hidden dim:** 4096
- **Layers:** 32
- **Use:** Extract hidden states for probing

**Secondary Models (for generalization):**
- Mistral-7B (7B params, 32 layers, 4096 hidden)
- Qwen-2-7B (7B params, 28 layers, 3584 hidden)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/Meta-Llama-3-8B`, `mistralai/Mistral-7B-v0.1`, `Qwen/Qwen2-7B`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")

# Extract hidden states
outputs = model(**inputs, output_hidden_states=True)
hidden_states = outputs.hidden_states  # tuple of (batch, seq, hidden_dim) per layer
```

#### Proposed Model

**Architecture:** Baseline + Gradient Reversal Layer for adversarial probing

**Core Mechanism Implementation:**

```python
# Core Mechanism: Adversarial Probing with Gradient Reversal
# Based on: Ganin & Lempitsky (2015), ariahw/rl-rewardhacking probe.py

import torch
import torch.nn as nn
from pytorch_revgrad import RevGrad
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

class GradientReversalLayer(nn.Module):
    """Reverses gradients during backprop, identity during forward."""
    def __init__(self, alpha=1.0):
        super().__init__()
        self.revgrad = RevGrad(alpha)
    
    def forward(self, x):
        return self.revgrad(x)

class AdversarialProber(nn.Module):
    """
    Two-head probing: BAI probe + Reward probe with gradient reversal.
    Goal: BAI remains decodable while reward signal is adversarially removed.
    """
    def __init__(self, hidden_dim, num_layers):
        super().__init__()
        # BAI probe (standard linear)
        self.bai_probe = nn.Linear(hidden_dim, 1)
        # Reward probe (after gradient reversal)
        self.grl = GradientReversalLayer(alpha=1.0)
        self.reward_probe = nn.Linear(hidden_dim, 1)
    
    def forward(self, hidden_states, layer_idx):
        """
        Args:
            hidden_states: (batch, seq, hidden_dim) from layer_idx
        Returns:
            bai_logits: (batch,) BAI predictions
            reward_logits: (batch,) Reward predictions (gradient reversed)
        """
        # Pool to single vector (last token or mean)
        h = hidden_states[:, -1, :]  # (batch, hidden_dim)
        
        bai_logits = self.bai_probe(h).squeeze(-1)
        reward_logits = self.reward_probe(self.grl(h)).squeeze(-1)
        
        return bai_logits, reward_logits

# Training loop outline:
# 1. Extract hidden states from LLM on HH-RLHF responses
# 2. Compute BAI labels from agency proxies (from H-E1)
# 3. Compute reward labels (chosen=1, rejected=0)
# 4. Train probes jointly: BAI loss + reversed reward loss
# 5. Evaluate: BAI AUROC (should remain ≥0.7), Reward R² (should degrade <2%)
```

### Training Protocol

**Optimizer:** AdamW
- Parameters: lr=1e-4, weight_decay=0.01
- Source: Standard for probe training on LLM hidden states

**Learning Rate:** 1e-4
- Schedule: Linear warmup (100 steps) + cosine decay
- Source: Common practice for probe fine-tuning

**Batch Size:** 32
- Source: Memory-efficient for 8B model hidden state extraction

**Epochs:** 3 (probes converge quickly on frozen representations)
- Source: Linear probes typically converge in 1-5 epochs

**Loss Function:**
- BAI probe: BCE loss
- Reward probe: BCE loss (gradients reversed)
- Combined: `loss = bai_loss + lambda * reward_loss` where lambda controls adversarial strength

**Seeds:** 3 (for statistical significance on MECHANISM hypothesis)

**Gradient Reversal Alpha Schedule:**
- Start: 0.0 (let probes warm up)
- Ramp to: 1.0 over first epoch
- Source: DANN paper recommends gradual GRL activation

### Evaluation

**Primary Metrics:**
1. **BAI Probe AUROC** (after gradient reversal): Target ≥0.7
   - Measures: Can BAI still be decoded after removing reward-predictive variance?
2. **Reward Probe R² Degradation**: Target <2%
   - Measures: Did gradient reversal actually remove reward signal?
   - Computed as: `R²_baseline - R²_after_grl`

**Secondary Metrics:**
- BAI probe accuracy (threshold=0.5)
- Per-layer AUROC analysis (which layers contain BAI signal?)
- Cross-model generalization (train on Llama, test on Mistral)

**Success Criteria:**
- BAI AUROC ≥0.7 after gradient reversal (primary gate)
- Reward R² degrades ≥2% (confirms GRL effectiveness)
- Results hold across ≥2/3 models

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (probing)
- Library: sklearn.metrics, torchmetrics
- Code:
```python
from sklearn.metrics import roc_auc_score, r2_score
from torchmetrics import AUROC

# BAI AUROC
bai_auroc = roc_auc_score(bai_labels, bai_probs)

# Reward R² (before and after GRL)
reward_r2_baseline = r2_score(reward_labels, reward_preds_no_grl)
reward_r2_after = r2_score(reward_labels, reward_preds_with_grl)
r2_degradation = reward_r2_baseline - reward_r2_after
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Layer-wise AUROC Heatmap**: AUROC per layer for BAI vs Reward probes
2. **GRL Alpha Ablation**: BAI AUROC vs GRL alpha strength curve
3. **Cross-model Generalization**: 3x3 matrix (train model × test model)
4. **t-SNE/UMAP Visualization**: Hidden state clusters colored by BAI vs Reward

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. BAI probe AUROC ≥0.7 after gradient reversal
3. Reward probe R² degrades <2%

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: T5 Hidden State Extraction
- **Type**: HuggingFace Docs
- **Query**: "linear probing hidden states transformer representation"
- **Relevance**: How to extract hidden states from transformers
- **Key Insight**: Use `outputs.last_hidden_state` for probing
- **Used For**: Model loading code specification

### B. GitHub Implementations (Exa)

**Repository B.1**: [janfreyberg/pytorch-revgrad](https://github.com/janfreyberg/pytorch-revgrad) ⭐158
- **Query**: "gradient reversal layer domain adaptation PyTorch"
- **Relevance**: Minimal, pip-installable gradient reversal layer
- **Used For**: Core mechanism pseudo-code

**Repository B.2**: [CuthbertCai/pytorch_DANN](https://github.com/CuthbertCai/pytorch_DANN) ⭐215
- **Query**: "gradient reversal layer domain adaptation PyTorch"
- **Relevance**: Full DANN implementation with reported results
- **Used For**: Training protocol (GRL alpha schedule)

**Repository B.3**: [ariahw/rl-rewardhacking](https://github.com/ariahw/rl-rewardhacking) src/probe.py
- **Query**: "linear probing transformer hidden states AUROC"
- **Relevance**: DIRECTLY RELEVANT - Probe training with AUROC evaluation
- **Used For**: Evaluation metrics code, probe class structure

**Repository B.4**: [scasella/activation-probes-claim-correctness](https://github.com/scasella/activation-probes-claim-correctness)
- **Query**: "linear probing transformer hidden states AUROC"
- **Relevance**: Claim-level probes on Llama activations
- **Used For**: Validation of probing approach on LLMs

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

### D. Previous Hypothesis Context

**Source**: H-E1 Validation Results (Phase 4)
- **Reused Components**:
  - Agency proxy extraction (AUROC 0.9836)
  - BAI computation from 4 proxies
  - HH-RLHF dataset preprocessing
- **Why Reused**: BAI labels depend on H-E1's validated proxy extraction

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (HH-RLHF) | HuggingFace | Anthropic/hh-rlhf |
| Model (Llama-3-8B) | HuggingFace | meta-llama/Meta-Llama-3-8B |
| Gradient Reversal | GitHub | B.1 pytorch-revgrad |
| Training Protocol | GitHub | B.2 pytorch_DANN |
| Probe Architecture | GitHub | B.3 rl-rewardhacking |
| Evaluation Metrics | GitHub | B.3, sklearn.metrics |
| BAI Labels | Previous | H-E1 validation |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-08

### Workflow History for This Hypothesis
- 2026-08-08: Phase 2C experiment design started

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
