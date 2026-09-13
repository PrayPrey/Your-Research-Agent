# Experiment Design: h-m2

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** Probes transfer across model families with AUROC gap <0.10 (train on Model A, evaluate on Model B hidden states)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM (Transfer) Template** - Tests cross-model generalization of learned probes.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 VALIDATED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** [h-e1]

### Gate Condition
SHOULD_WORK — Failure does not block pipeline. Success: Transfer gap <0.10 AUROC.

---

## Continuation Context

Building on h-e1 (VALIDATED). Reuses:
- SEP probe architecture (LogisticRegression on hidden states)
- TruthfulQA dataset (817 samples)
- 3 model families: Llama-3-8B, Mistral-7B, Qwen-2-7B
- Layer selection methodology (~2/3 depth)

### Previous Hypothesis Results
**h-e1:** SEPs achieve AUROC within 0.05 of multi-sample SE across model families.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct results for cross-model probe transfer. Relevant patterns from h-e1 research apply.

### Exa Web Search Findings

**🎯 KEY TRANSFER STUDIES:**

**1. Chen et al. (2025) - "Transferring Linear Features Across Language Models With Model Stitching"**
- URL: https://arxiv.org/html/2506.06609
- Finding: Affine mappings between residual streams enable feature transfer
- Key insight: Small and large models learn similar representation spaces
- Method: Train SAE on small model, transfer to large model via affine mapping
- Result: 50% cheaper training runs; transferred probes recover ground truth performance

**2. Kim et al. (UAI 2026) - "Same Benchmark, Same Subspace: Task-Selective Convergence"**
- URL: https://proceedings.mlr.press/v337/kim26g.html
- Finding: Readout geometry governed by benchmark, not model
- Key insight: Readout subspaces aligned across unrelated models (Gram cosine up to 0.87)
- Implication: Cross-model transfer may work for task-specific probes

**3. Mrykhin & Malykh (2026) - "Prompt Embedding Probes (PEP)"**
- URL: https://arxiv.org/html/2608.08024
- Finding: Cross-model transfer experiments show PEP remains effective
- Key insight: Robust transfer across substantially different datasets remains difficult
- Models: Qwen3 multi-scale

**4. Srey et al. (2026) - "From Signals to Transfer: Factorised Study of Probe-Based UE"**
- URL: https://arxiv.org/html/2606.27679
- Finding: Raw hidden states hard to beat in-domain, but structured features more robust under shift
- Key insight: Benchmark-based pretrained probes transfer reasonably to open-ended factual generation
- Code: https://github.com/ponhvoan/ProbeUE

**5. Kumar (2026) - "Pressure-Testing Deception Probes"**
- URL: https://arxiv.org/html/2605.27958v1
- Finding: Cross-domain transfer matrices show AUROC collapse under distributional shift
- Key insight: Style-augmented probes recover (AUROC 0.979-0.983)
- Implication: Direct transfer without alignment may fail

**6. Mehta (2026) - "The Refusal Residue"**
- URL: https://arxiv.org/html/2607.13346v1
- Finding: Cross-model transfer is "null" for alignment faking detection
- Key insight: Per-sample detection is model-conditional
- Caveat: Different task (alignment faking vs uncertainty)

### 🎯 Transfer Strategy Assessment

| Strategy | Expected AUROC Gap | Complexity |
|----------|-------------------|------------|
| Direct transfer (no alignment) | 0.10-0.30 (likely fail) | Low |
| Affine mapping (Chen et al.) | <0.10 (promising) | Medium |
| Same-benchmark effect (Kim et al.) | <0.10 (promising) | Low |
| Feature-space projection | Unknown | High |

**Recommended Approach:** Test direct transfer first (simplest); if gap >0.10, try affine alignment as fallback.

### Code References

**Primary:** Reuse h-e1 SEP implementation (OATML/semantic-entropy-probes methodology)

**Transfer-specific:**
- Chen et al. model stitching: affine mapping W, b between hidden spaces
- ProbeUE (Srey et al.): https://github.com/ponhvoan/ProbeUE

---

## Experiment Specification

### Dataset

**Evaluation Dataset: TruthfulQA**
- **Name:** TruthfulQA
- **Type:** standard (real benchmark)
- **Source:** HuggingFace Datasets
- **Size:** 817 questions
- **Purpose:** Evaluate cross-model probe transfer AUROC
- **Hypothesis Fit:** Same benchmark = same readout subspace hypothesis (Kim et al.)

**Training Split:** 80% train / 20% val (same split as h-e1)

**Loading Information:**
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "generation")
# 817 questions total
```

### Models

#### Source and Target Models (3 Families)

| Model | HuggingFace ID | Hidden Dim | Layers |
|-------|----------------|------------|--------|
| Llama-3-8B-Instruct | `meta-llama/Meta-Llama-3-8B-Instruct` | 4096 | 32 |
| Mistral-7B-Instruct-v0.2 | `mistralai/Mistral-7B-Instruct-v0.2` | 4096 | 32 |
| Qwen-2-7B-Instruct | `Qwen/Qwen2-7B-Instruct` | 3584 | 28 |

#### Transfer Matrix Design

Train probe on Model A → Evaluate on Model B (hidden states):

| Train \ Eval | Llama-3 | Mistral-7B | Qwen-2 |
|--------------|---------|------------|--------|
| Llama-3      | (baseline) | Transfer | Transfer |
| Mistral-7B   | Transfer | (baseline) | Transfer |
| Qwen-2       | Transfer | Transfer | (baseline) |

**6 transfer pairs + 3 baselines = 9 total evaluations**

### Proposed Architecture

**Core Mechanism: Cross-Model SEP Transfer**

```python
import torch
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

class CrossModelSEPTransfer:
    """
    Train SEP on Model A hidden states, evaluate on Model B hidden states.
    Tests: Do uncertainty representations transfer across model families?
    """
    def __init__(self, source_layer_frac: float = 0.67, target_layer_frac: float = 0.67):
        """
        Args:
            source_layer_frac: Fraction of depth for source model layer (~2/3)
            target_layer_frac: Fraction of depth for target model layer (~2/3)
        """
        self.source_layer_frac = source_layer_frac
        self.target_layer_frac = target_layer_frac
        self.probe = LogisticRegression(max_iter=1000, C=1.0)
        self.affine_W = None  # Optional: affine alignment
        self.affine_b = None
    
    def get_layer_idx(self, model_config, frac):
        """Get layer index at specified depth fraction."""
        n_layers = model_config.num_hidden_layers
        return int(n_layers * frac)
    
    def extract_hidden_states(self, model, tokenizer, questions, layer_idx):
        """Extract hidden states at specified layer for all questions."""
        hidden_states = []
        model.eval()
        with torch.no_grad():
            for q in questions:
                inputs = tokenizer(q, return_tensors="pt", truncation=True, max_length=512)
                inputs = {k: v.to(model.device) for k, v in inputs.items()}
                outputs = model(**inputs, output_hidden_states=True)
                # Last token hidden state
                h = outputs.hidden_states[layer_idx][:, -1, :].cpu().numpy()
                hidden_states.append(h.squeeze())
        return np.array(hidden_states)  # (N, hidden_dim)
    
    def fit_on_source(self, source_hidden_states, se_labels):
        """Train probe on source model hidden states."""
        self.probe.fit(source_hidden_states, se_labels)
    
    def fit_affine_alignment(self, source_hidden, target_hidden):
        """
        Learn affine mapping from target to source space (optional).
        Uses paired samples (same questions, both models).
        W, b such that: source ≈ target @ W + b
        """
        # Least squares: source = target @ W + b
        # Add bias column
        X = np.hstack([target_hidden, np.ones((target_hidden.shape[0], 1))])
        # Solve: X @ [W; b] = source
        Wb, _, _, _ = np.linalg.lstsq(X, source_hidden, rcond=None)
        self.affine_W = Wb[:-1, :]
        self.affine_b = Wb[-1, :]
    
    def transform_target_to_source(self, target_hidden):
        """Apply affine alignment (if fitted)."""
        if self.affine_W is None:
            return target_hidden  # No alignment
        return target_hidden @ self.affine_W + self.affine_b
    
    def evaluate_transfer(self, target_hidden_states, labels, align=False):
        """Evaluate probe on target model hidden states."""
        if align:
            target_hidden_states = self.transform_target_to_source(target_hidden_states)
        probs = self.probe.predict_proba(target_hidden_states)[:, 1]
        auroc = roc_auc_score(labels, probs)
        return auroc
```

### Training Protocol

**Phase 1: Per-Model SEP Training (reuse h-e1 probes)**
- Train SEP probe on each model's own hidden states
- Use same layer selection as h-e1 (~2/3 depth)
- Labels: Binarized semantic entropy (threshold at median)

**Phase 2: Direct Transfer Evaluation**
- For each (source, target) pair:
  1. Extract target model hidden states for TruthfulQA
  2. Apply source-trained probe directly (no alignment)
  3. Compute AUROC on target

**Phase 3: Affine-Aligned Transfer (if direct fails)**
- Fit affine mapping on train split hidden states (paired samples)
- Apply transformation before probe evaluation
- Compute AUROC on val split

**Handling Hidden Dimension Mismatch:**
- Llama/Mistral: 4096 → Qwen: 3584
- If source_dim ≠ target_dim: Use affine alignment (required)
- Affine W: (target_dim, source_dim) maps target to source space

### Evaluation

**Primary Metric:** AUROC transfer gap

```
transfer_gap = |AUROC_transfer - AUROC_in_model|
```

Where AUROC_in_model is the baseline (train and eval on same model).

**Success Criteria (MECHANISM):**
```
SUCCESS if:
  - Mean transfer gap < 0.10 across all 6 transfer pairs
  - No transfer pair shows gap > 0.15
```

**Falsification Criterion:**
```
FAIL if:
  - Mean transfer gap > 0.15
  - OR majority (4+) of pairs show gap > 0.15
```

**Expected Baseline Performance** (from research):
- Same-model AUROC: 0.70-0.85 (from h-e1)
- Same-benchmark transfer (Kim et al.): Gram cosine 0.87 → suggests transfer gap <0.10 possible
- Direct transfer without alignment: 0.10-0.30 gap (Kumar 2026)
- Affine-aligned transfer: <0.10 gap (Chen et al. 2025)

**Metrics Loading:**
```python
from sklearn.metrics import roc_auc_score
auroc = roc_auc_score(y_true, y_pred_proba)
transfer_gap = abs(auroc_transfer - auroc_baseline)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Transfer Matrix Heatmap**: 3×3 AUROC matrix (train model × eval model)
  - Diagonal = baseline (same-model)
  - Off-diagonal = transfer performance

#### Additional Figures
- Transfer gap bar chart (6 pairs)
- Affine alignment before/after comparison (if used)
- Hidden space alignment visualization (PCA of shared samples)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** SEP probes trained per model (from h-e1)
- **mechanism_isolatable:** Yes — probe is model-agnostic once trained
- **baseline_measurable:** Yes — same-model AUROC from h-e1

### Architecture Compatibility
- **Hidden state extraction:** Same as h-e1
- **Dimension handling:** Affine alignment for mismatched dims (Qwen 3584 vs others 4096)
- **Layer selection:** Proportional depth (~0.67) for fair comparison

### Activation Indicators
- **mechanism_log_message:** `"Transfer AUROC (train={src}, eval={tgt}): {auroc:.3f}, gap={gap:.3f}"`
- **tensor_shape_change:** Input: `(batch, target_hidden_dim)` → aligned: `(batch, source_hidden_dim)` → Output: `(batch,)`
- **metric_delta_expected:** Transfer gap <0.10 AUROC

### Mechanism Verification Code
```python
def verify_transfer_mechanism(transfer_model, source_name, target_name, 
                               target_hidden, labels, baseline_auroc):
    """Verify cross-model transfer works."""
    # 1. Direct transfer
    auroc_direct = transfer_model.evaluate_transfer(target_hidden, labels, align=False)
    gap_direct = abs(auroc_direct - baseline_auroc)
    print(f"Direct transfer ({source_name} → {target_name}): AUROC={auroc_direct:.3f}, gap={gap_direct:.3f}")
    
    # 2. Aligned transfer (if direct fails)
    if gap_direct > 0.10:
        auroc_aligned = transfer_model.evaluate_transfer(target_hidden, labels, align=True)
        gap_aligned = abs(auroc_aligned - baseline_auroc)
        print(f"Aligned transfer ({source_name} → {target_name}): AUROC={auroc_aligned:.3f}, gap={gap_aligned:.3f}")
        return gap_aligned < 0.10
    
    return gap_direct < 0.10
```

### Success Thresholds
- **hypothesis_support_threshold:** Mean transfer gap <0.10
- **hypothesis_support_metric:** `mean(|AUROC_transfer - AUROC_baseline|)` across 6 pairs

---

## 🔬 Mechanism Success Check

**Pass Condition:**
1. All 6 transfer pairs evaluated
2. Mean transfer gap <0.10 AUROC
3. No pair shows gap >0.15

**Partial Success:**
- If affine alignment required: Note in results
- If only some pairs transfer: Document which model pairs work

---

## Appendix: Reference Implementations

### Primary References
- **h-e1 SEP implementation** (local)
- **Chen et al. (2025)** - Model stitching affine mapping
- **Srey et al. (2026)** - ProbeUE: https://github.com/ponhvoan/ProbeUE

### Related Papers
- Kim et al. (UAI 2026): Same Benchmark, Same Subspace
- Mrykhin & Malykh (2026): PEP cross-model transfer
- Kumar (2026): Probe fragility under distributional shift

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- 2026-08-24: Phase 2C initiated for h-m2
- 2026-08-24: Exa search completed — transfer studies found
- 2026-08-24: Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge), Exa (Web Search)*
*Building on h-e1 validated results*
*Next Phase: Phase 3 - Implementation Planning*
