# Experiment Design: h-e1

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** NTI (layers 24-32) achieves AUROC > 0.55 on TruthfulQA MC1
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (first hypothesis)
**Gate Status:** MUST_WORK - Pipeline stops if AUROC < 0.55

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
AUROC > 0.55 in >= 4/5 folds. Falsification: Any fold AUROC < 0.52.

---

## Continuation Context

First hypothesis in verification chain. No previous context.

### Previous Hypothesis Results (if applicable)
N/A - This is the foundation hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches. Found arxiv.org/abs/2402.19159 on trajectory analysis (similarity 0.41). No exact NTI implementation in KB.

### Archon Code Examples

Found attention caching patterns (T-GATE), LogitsProcessor implementations, but no direct logit-lens trajectory code in Archon KB.

### Exa GitHub Implementations

**Highly Relevant Findings:**

1. **TriLens (arxiv 2606.01033)** - Per-layer logit-lens entropy for hallucination detection
   - Extracts entropy from attention output, FFN output, and residual stream at each layer
   - 3L-dimensional trajectory (L = num layers)
   - Strong detection across QA benchmarks
   - Code: https://tosakaucw.github.io/TriLens/

2. **Semantic Token-Group Logit Trajectories (ANLP 2026)**
   - Layer-wise logit evolution for contrasting token groups (True/False)
   - Lightweight MLP classifier on trajectories
   - Reduced dimensionality vs full hidden states

3. **veritas-audit (PyPI)**
   - Uses transformer_lens for residual stream analysis
   - Plots logit lens trajectory per token
   - Dependencies: transformer_lens>=2.0.0, torch>=2.1.0, sklearn>=1.4.0

4. **TransformerLens**
   - `run_with_cache` extracts all layer activations
   - `HookedTransformer` with hook-based introspection
   - Supports LLaMA-2 via TransformerBridge (9000+ models)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

No official NTI implementation exists (novel metric). Use established logit-lens patterns from TransformerLens + custom NTI calculation.

**Recommended Implementation Path:**
- Primary: TransformerLens with custom NTI metric extraction
- Fallback: Native HuggingFace with `output_hidden_states=True` + manual logit-lens
- Justification: TransformerLens provides clean hook-based activation caching; TriLens methodology validates approach

### Code Analysis (Serena MCP)

*Skipped* - No existing codebase to analyze. Fresh implementation.

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| Name | TruthfulQA MC1 |
| Source | HuggingFace datasets |
| Identifier | `truthful_qa` (subset: `multiple_choice`, split: `validation`) |
| Size | 817 questions |
| Labels | Binary correctness (selected_answer == correct_answer) |
| Splits | 5-fold CV (no train/test - evaluation only) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "multiple_choice", split="validation")
# 817 samples, each with question + mc1_targets (choices + labels)
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| Name | LLaMA-2-7B |
| Source | HuggingFace Hub |
| Identifier | `meta-llama/Llama-2-7b-hf` |
| Parameters | 7B |
| Layers | 32 (analysis: layers 24-32) |
| Hidden dim | 4096 |
| Vocab size | 32000 |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers + TransformerLens
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformer_lens import HookedTransformer
model = HookedTransformer.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    device="cuda",
    dtype=torch.float16
)
```

#### Proposed Model

**Architecture:** Baseline + NTI (Normalized Trajectory Instability) metric extraction

**Core Mechanism Implementation:**

```python
# NTI: Normalized Trajectory Instability (10-30 lines)
# Measures instability of logit-lens predictions across layers 24-32

def compute_nti(model, input_ids, target_layers=(24, 32)):
    """
    Compute Normalized Trajectory Instability.
    
    NTI = std(entropy_trajectory[L_start:L_end]) / mean(entropy_trajectory[L_start:L_end])
    
    Higher NTI = more instability = potential hallucination signal
    """
    # 1. Run forward pass with hidden state caching
    logits, cache = model.run_with_cache(input_ids)
    
    # 2. Extract residual stream at each layer
    entropy_trajectory = []
    for layer in range(target_layers[0], target_layers[1] + 1):
        # Get residual stream at layer
        residual = cache[f"blocks.{layer}.hook_resid_post"]  # (batch, seq, d_model)
        
        # Apply logit lens: final_ln + unembed
        h_normed = model.ln_final(residual)
        layer_logits = h_normed @ model.W_U  # (batch, seq, vocab)
        
        # Compute entropy at last token position
        probs = torch.softmax(layer_logits[:, -1, :], dim=-1)
        entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
        entropy_trajectory.append(entropy)
    
    # 3. Stack and compute NTI
    trajectory = torch.stack(entropy_trajectory, dim=1)  # (batch, num_layers)
    
    # NTI = coefficient of variation of entropy across layers
    nti = trajectory.std(dim=1) / (trajectory.mean(dim=1) + 1e-10)
    
    return nti, trajectory

def compute_baseline_entropy(model, input_ids):
    """Raw mean entropy H_L from final layer (baseline: AUROC 0.6426)"""
    logits = model(input_ids)
    probs = torch.softmax(logits[:, -1, :], dim=-1)
    entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
    return entropy
```

### Training Protocol

**No training required** - This is an EXISTENCE hypothesis testing whether the NTI metric has discriminative power.

| Attribute | Value |
|-----------|-------|
| Training | None (metric extraction only) |
| Inference | Greedy decoding (temperature=0) |
| Evaluation | 5-fold cross-validation |
| Classifier | Logistic regression on NTI scores |
| Hyperparameters | sklearn defaults |

### Evaluation

| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| AUROC | Area Under ROC Curve | > 0.55 |
| Fold Stability | Min fold AUROC | > 0.52 |
| Pass Rate | Folds passing threshold | >= 4/5 |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression

# 5-fold CV
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
aurocs = []
for train_idx, test_idx in skf.split(nti_scores, labels):
    clf = LogisticRegression()
    clf.fit(nti_scores[train_idx].reshape(-1, 1), labels[train_idx])
    pred_proba = clf.predict_proba(nti_scores[test_idx].reshape(-1, 1))[:, 1]
    aurocs.append(roc_auc_score(labels[test_idx], pred_proba))

mean_auroc = np.mean(aurocs)
min_auroc = np.min(aurocs)
pass_rate = sum(a > 0.55 for a in aurocs) / 5
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart (AUROC per fold + mean)

#### Additional Figures (LLM Autonomous)

1. **Entropy Trajectory Heatmap**: Layer (x) vs Sample (y), colored by entropy
2. **NTI Distribution**: Histogram of NTI scores for correct vs hallucinated responses
3. **ROC Curve**: Per-fold and mean ROC curves
4. **Layer Contribution**: AUROC using only layers L to 32 (ablation)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Mean AUROC > 0.55
3. Min fold AUROC > 0.52
4. >= 4/5 folds pass threshold

---

## Appendix: Reference Implementations

### Primary References

1. **TriLens** (Yang et al., 2026)
   - Paper: https://arxiv.org/abs/2606.01033
   - Code: https://tosakaucw.github.io/TriLens/
   - Relevance: Per-layer entropy trajectory for hallucination detection

2. **TransformerLens**
   - Repo: https://github.com/TransformerLensOrg/TransformerLens
   - Usage: `HookedTransformer.run_with_cache()` for activation extraction
   - LLaMA support via `TransformerBridge`

3. **Logit Lens Tutorial**
   - URL: https://alessiodevoto.github.io/LogitLens/
   - Pattern: `model.lm_head(hidden_states[layer])` for early logits

4. **veritas-audit**
   - PyPI: https://pypi.org/project/veritas-audit/
   - Pattern: Residual stream analysis with transformer_lens

### Code Snippet: Logit Lens Core

```python
def logit_lens(hidden_l, model):
    """Project residual-stream tensor through model's final LN + unembed."""
    h_normed = model.ln_final(hidden_l)
    logits = model.lm_head(h_normed)
    return logits.softmax(-1)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- 2026-08-09: Phase 2C experiment design initiated
- Status: experiment_design.status = COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Code Context)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
