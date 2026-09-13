# H-M2 Validation Report: Projection-Only LoRA Eigenvalue Preservation

**Hypothesis**: Projection-only LoRA preserves SSM eigenvalues (|ΔH_spec| < 10%) after fine-tuning
**Gate Type**: MUST_WORK
**Status**: **PASS**
**Date**: 2026-03-27

---

## Executive Summary

The H-M2 experiment successfully validated that projection-only LoRA fine-tuning **preserves SSM eigenvalues**. The A_log parameters remained completely frozen during training, resulting in zero change to eigenvalues and H_spec.

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| |ΔH_spec| | 0.0000% | < 10.0% | PASS |
| Eigenvalue Correlation | 1.0000 | > 0.95 | PASS |
| A_log Max Diff | 0.0 | ~0 | PASS |

---

## Experiment Configuration

### Model
- **Model**: state-spaces/mamba-1.4b-hf
- **Architecture**: Mamba SSM (48 layers)
- **Dataset**: WikiText-103 (wikitext-103-raw-v1)

### LoRA Configuration
- **Rank (r)**: 16
- **Alpha**: 32
- **Target Modules**: `in_proj`, `x_proj` (projection matrices only)
- **Dropout**: 0.1
- **Trainable Parameters**: 11,132,928 (0.80% of total)

### Training
- **Epochs**: 1 (PoC configuration)
- **Batch Size**: 2 (effective: 16 with gradient accumulation)
- **Learning Rate**: 1e-4
- **Training Sequences**: 200 (subsampled for PoC)
- **Sequence Length**: 256 tokens

---

## Results

### Primary Metrics (Gate Criteria)

| Metric | Pre-Training | Post-Training | Change |
|--------|--------------|---------------|--------|
| H_spec (tokens) | 256.43 | 256.43 | 0.0000% |
| A_log Max Diff | - | 0.0 | Frozen |
| Eigenvalue Correlation | - | 1.0000 | Perfect |

### Secondary Metrics

| Metric | Value |
|--------|-------|
| Final Training Loss | 3.01 |
| Validation Perplexity | 15.58 |
| Training Steps | 100 |

---

## Mechanism Verification

The experiment verified the core hypothesis mechanism:

1. **A_log Parameters**: FROZEN (requires_grad=False)
   - Not included in LoRA target modules
   - No gradients flow through A_log during training
   - Max absolute difference: 0.0

2. **Projection LoRA Adapters**: TRAINABLE
   - `in_proj.lora_A`, `in_proj.lora_B`
   - `x_proj.lora_A`, `x_proj.lora_B`
   - 11.1M trainable parameters

---

## Key Findings

### 1. Perfect Eigenvalue Preservation
The projection-only LoRA approach achieves **perfect eigenvalue preservation**:
- H_spec unchanged: 256.43 tokens before and after training
- Eigenvalue correlation: 1.0000 (perfect)
- A_log tensor difference: 0.0 across all 48 layers

### 2. SSM Core Isolation
The SSM core (A_log) is completely isolated from the LoRA fine-tuning process:
- PEFT library correctly freezes A_log parameters
- Only projection matrices receive gradient updates
- Eigenvalue-derived memory characteristics remain intact

### 3. Implications for Memory-Preserving Fine-Tuning
This validates that Mamba models can be fine-tuned via LoRA while:
- Preserving learned temporal dynamics (eigenvalues)
- Maintaining H_spec (spectral memory horizon)
- Achieving the 256-token memory capacity established in H-M1

---

## Generated Figures

1. **gate_metrics.png** - Gate threshold comparison
2. **eigenvalue_distribution.png** - Pre/post eigenvalue distributions
3. **per_layer_h_spec_change.png** - Per-layer H_spec changes
4. **a_log_diff_heatmap.png** - A_log parameter differences
5. **eigenvalue_scatter.png** - Pre vs post eigenvalue scatter
6. **training_loss.png** - Training loss curve

---

## Conclusion

**GATE VERDICT: PASS**

H-M2 successfully demonstrates that projection-only LoRA preserves SSM eigenvalues. The hypothesis is validated:

> "Projection-only LoRA (targeting in_proj, x_proj) does NOT modify A_log parameters, thereby preserving the eigenvalue spectrum and memory characteristics of Mamba SSMs."

This finding enables memory-preserving fine-tuning strategies for Mamba models where temporal dynamics must remain unchanged.

---

## Technical Notes

- PEFT version: 0.18.1
- Note: `out_proj` is incompatible with PEFT Mamba implementation (explicitly blocked)
- Slow path used (no optimized Mamba kernels) - does not affect results, only speed
- PoC configuration used reduced dataset/epochs for validation speed
