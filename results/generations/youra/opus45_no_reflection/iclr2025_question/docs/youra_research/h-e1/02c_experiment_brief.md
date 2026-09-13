# Experiment Design: H-E1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Middle-layer hidden states encode sufficient signal for correctness prediction with AUROC > 0.60
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required)
**Gate Status:** MUST_WORK - AUROC > 0.60 required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**MUST_WORK Gate**: If AUROC <= 0.60, ABANDON entire research direction. Hidden states lack correctness signal.

---

## Continuation Context

This is the first hypothesis in the verification chain. Establishes whether hidden states contain ANY predictive signal for factual correctness before testing mechanisms.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches. Relevant patterns from diffusers/transformers:
- T5EncoderModel hidden state extraction via `outputs.last_hidden_state`
- Attention processor patterns for accessing intermediate representations

### Archon Code Examples

```python
# HuggingFace pattern for hidden state access
from transformers import AutoTokenizer, T5EncoderModel
model = T5EncoderModel.from_pretrained("google-t5/t5-small")
outputs = model(input_ids=input_ids)
last_hidden_states = outputs.last_hidden_state
```

### Exa GitHub Implementations

**Primary Reference: peterstringer/venator**
- Linear probe on middle-layer activations from Mistral-7B
- Achieves **0.999 AUROC** for jailbreak detection
- Uses layer 18 (middle layer), PCA to 50 dims, logistic regression
- Key insight: "middle layers where model has moved past token-level processing"

**Secondary: aragorn-w/linear-probe**
- Linear classifier probes (Alain & Bengio, 2016) on GPT-2
- Uses TransformerLens for hidden state extraction
- Formula: `P(y=1|h_l) = sigmoid(w^T h_l + b)`
- Binary cross-entropy loss, Adam optimizer

**Tertiary: OpenInterpretability/notebooks/21_linear_probe.ipynb**
- "Indispensable baseline" for AUROC claims
- Logistic regression on residual stream
- References: Alain & Bengio 2016, Belrose et al. 2023

**Quaternary: aliuyar1234/binary-evidence-sufficiency-dissociation**
- Hidden state probing for QA correctness (highly relevant!)
- Fixed-question, changed-context multi-hop QA on HotpotQA
- Linear probes at prompt end and reasoning steps

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

No official implementation exists for our specific task. Closest:
1. `venator` - proven AUROC methodology on similar task
2. `binary-evidence-sufficiency-dissociation` - QA correctness probing

**Recommended Implementation Path:**
- Primary: Adapt venator's middle-layer probe pattern for Llama-3-8B
- Fallback: TransformerLens-style hook extraction with sklearn LogisticRegression
- Justification: venator achieves 0.999 AUROC on classification task with minimal code

### Code Analysis (Serena MCP)

*Skipped* - No existing codebase to analyze for this hypothesis.

---

## Experiment Specification

### Dataset

| Property | Value |
|----------|-------|
| **Name** | TriviaQA |
| **Version** | rc (reading comprehension) |
| **Source** | HuggingFace datasets |
| **Type** | standard |
| **Train Split** | 95,000 examples (train subset) |
| **Validation Split** | 17,000 examples (validation subset) |
| **Preprocessing** | Format as QA prompt, generate answer with greedy decoding |
| **Labels** | Binary correctness (exact match with ground truth) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `trivia_qa` with `rc` config
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("trivia_qa", "rc", split="train[:95000]")
val_dataset = load_dataset("trivia_qa", "rc", split="validation[:17000]")
```

### Models

#### Baseline Model

| Property | Value |
|----------|-------|
| **Name** | Llama-3-8B-Instruct |
| **Source** | meta-llama/Meta-Llama-3-8B-Instruct |
| **Type** | Causal LM (transformer) |
| **Layers** | 32 total |
| **Hidden Dim** | 4096 |
| **Target Layer** | Layer 19 (60% depth = 0.6 * 32 ≈ 19) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Meta-Llama-3-8B-Instruct`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
```

#### Proposed Model

**Architecture:** Baseline LLM + Linear Probe on hidden states

**Core Mechanism Implementation:**

```python
# Hidden State Extraction with Forward Hook
class HiddenStateExtractor:
    def __init__(self, model, target_layer: int = 19):
        self.hidden_states = None
        self.target_layer = target_layer
        # Register hook on target layer
        self.hook = model.model.layers[target_layer].register_forward_hook(
            self._capture_hook
        )
    
    def _capture_hook(self, module, input, output):
        # output[0] is hidden states: [batch, seq_len, hidden_dim]
        # Take last token's hidden state for classification
        self.hidden_states = output[0][:, -1, :].detach().cpu()
    
    def remove(self):
        self.hook.remove()

# Linear Probe (Logistic Regression)
class LinearProbe(nn.Module):
    def __init__(self, hidden_dim: int = 4096):
        super().__init__()
        self.classifier = nn.Linear(hidden_dim, 1)
    
    def forward(self, hidden_states):
        # hidden_states: [batch, hidden_dim]
        logits = self.classifier(hidden_states)
        return torch.sigmoid(logits)

# Training Loop
def train_probe(hidden_states, labels, epochs=10, lr=1e-3):
    probe = LinearProbe(hidden_dim=hidden_states.shape[1])
    optimizer = torch.optim.Adam(probe.parameters(), lr=lr)
    criterion = nn.BCELoss()
    
    for epoch in range(epochs):
        optimizer.zero_grad()
        preds = probe(hidden_states).squeeze()
        loss = criterion(preds, labels.float())
        loss.backward()
        optimizer.step()
    
    return probe

# AUROC Evaluation
def evaluate_auroc(probe, hidden_states, labels):
    with torch.no_grad():
        preds = probe(hidden_states).squeeze().numpy()
    from sklearn.metrics import roc_auc_score
    return roc_auc_score(labels.numpy(), preds)
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Optimizer** | Adam | Standard for linear probes |
| **Learning Rate** | 1e-3 | Default for linear models |
| **Batch Size** | 256 | Memory efficient for probe training |
| **Epochs** | 10 | Sufficient for linear convergence |
| **Loss** | Binary Cross-Entropy | Binary classification |
| **Regularization** | None | Linear probe, minimal overfitting risk |

### Evaluation

| Metric | Target | Justification |
|--------|--------|---------------|
| **Primary: AUROC** | > 0.60 | Gate condition for MUST_WORK |
| **Secondary: Random Baseline** | 0.50 | Sanity check |
| **Statistical Test** | N/A for PoC | Direction-based only |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary Classification
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt

auroc = roc_auc_score(y_true, y_pred_proba)
fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing Probe AUROC vs Random Baseline (0.50)

#### Additional Figures (LLM Autonomous)

1. **ROC Curve**: FPR vs TPR with AUROC annotation
2. **Training Loss Curve**: Loss vs epoch to verify convergence
3. **Hidden State Distribution**: t-SNE/PCA of hidden states colored by correctness label

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `probe_auroc > 0.60` (better than near-random)

**Gate Decision:**
- PASS (AUROC > 0.60): Proceed to H-M1
- FAIL (AUROC <= 0.60): ABANDON - hidden states lack correctness signal

---

## Appendix: Reference Implementations

### Primary: peterstringer/venator
- **URL**: https://github.com/peterstringer/venator
- **Relevance**: Linear probe on middle-layer activations, 0.999 AUROC
- **Key Pattern**: Extract layer 18, PCA reduction, logistic regression

### Secondary: aragorn-w/linear-probe
- **URL**: https://github.com/aragorn-w/linear-probe
- **Relevance**: GPT-2 linear probes with TransformerLens
- **Key Pattern**: `P(y=1|h_l) = sigmoid(w^T h_l + b)`

### Tertiary: OpenInterpretability/notebooks
- **URL**: https://github.com/OpenInterpretability/notebooks/blob/main/notebooks/21_linear_probe.ipynb
- **Relevance**: AUROC baseline methodology for SAE evaluation
- **Key Pattern**: Logistic regression on residual stream

### Quaternary: aliuyar1234/binary-evidence-sufficiency-dissociation
- **URL**: https://github.com/aliuyar1234/binary-evidence-sufficiency-dissociation
- **Relevance**: Hidden state probing for QA correctness
- **Key Pattern**: Multi-hop QA with linear probes at different positions

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- 2026-08-18: H-E1 set to IN_PROGRESS (external loop starting Phase 2C)
- 2026-08-18: Phase 2C experiment design initiated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
