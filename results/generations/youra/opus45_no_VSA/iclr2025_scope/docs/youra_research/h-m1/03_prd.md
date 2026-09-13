# Product Requirements Document: H-M1

**Hypothesis:** Zero-shot IPCR routing achieves ≥90% of oracle task-specific LoRA performance on held-out FLAN tasks
**Type:** MECHANISM
**Gate:** MUST_WORK
**Date:** 2026-08-09

---

## Executive Summary

Implement and validate Instruction-Prefix-Conditioned Routing (IPCR) that uses the H-E1 validated linear probe (72.67% top-1, 95.78% top-3) to select task-specific LoRA adapters at inference time. The system must achieve ≥90% of oracle LoRA performance on held-out FLAN task families.

---

## Problem Statement

Task-specific LoRA adapters excel on their trained domains but require oracle knowledge of task identity. IPCR solves this by routing instructions to appropriate adapters using frozen MiniLM embeddings + linear probe, enabling zero-shot task-appropriate adapter selection.

---

## Functional Requirements

### FR-1: IPCR Router Implementation
- Implement `IPCRRouter` class using H-E1 trained linear probe
- Input: instruction string → Output: selected adapter name
- Use `sentence-transformers/all-MiniLM-L6-v2` for embeddings (384-dim)
- Linear probe maps embedding to k adapter logits

### FR-2: Multi-LoRA Model Setup
- Base model: Llama-2-7B-chat or Mistral-7B-Instruct
- k=8 task-specific LoRA adapters (rank r=16, alpha=32)
- Target modules: q_proj, v_proj
- Use PEFT `load_adapter()` and `set_adapter()` APIs

### FR-3: LoRA Training Pipeline
- Train k=8 task-family-specific LoRAs on FLAN subsets
- Optimizer: AdamW, lr=2e-4
- Epochs: 3 per task family
- Batch size: 8

### FR-4: Oracle Baseline
- Task-specific LoRA with ground-truth task family label
- Represents 100% upper bound performance

### FR-5: Random Baseline
- Random adapter selection per sample
- Expected: ~12.5% of oracle (1/k for k=8)

### FR-6: Uniform Baseline
- Equal-weight combination of all adapters
- Use `set_adapters([all], weights=[1/k]*k)`

### FR-7: Evaluation Pipeline
- Held-out task families (k families not seen during LoRA training)
- Minimum 500 samples per held-out family
- Task-appropriate metrics: Accuracy (classification), ROUGE-L (generation), Exact Match (QA)

### FR-8: Statistical Testing
- Paired t-test: IPCR vs Uniform
- Significance threshold: p < 0.05

### FR-9: Visualization
- Gate metrics comparison bar chart (mandatory)
- Per-task-family performance breakdown
- Routing confusion matrix
- Performance vs routing confidence scatter

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Single seed (42) for all experiments
- Save trained LoRA adapters to checkpoints
- Log all hyperparameters

### NFR-2: Memory Efficiency
- Load base model once
- Switch adapters via `set_adapter()` (O(1), ~5ms)

### NFR-3: Evaluation Scale
- Full test set evaluation (no trivial subsets)
- Minimum 500 samples per task family

---

## Success Criteria

| Metric | Threshold | Gate Type |
|--------|-----------|-----------|
| IPCR / Oracle | ≥90% | MUST_WORK |
| IPCR vs Uniform | p < 0.05 | MUST_WORK |
| IPCR / Oracle | <80% | FAIL (falsification) |

---

## Data Requirements

- **Dataset:** Open-Orca/FLAN (HuggingFace streaming)
- **Task families:** 62 FLAN categories
- **Split:** Hold out k families for evaluation

---

## Dependencies

- H-E1 validated linear probe (72.67% top-1)
- `transformers`, `peft`, `sentence-transformers`, `evaluate`
- GPU with ≥24GB VRAM (for 7B model + LoRAs)

---

## Out of Scope

- Soft adapter mixing (future H-M2)
- Per-token routing (MoLoRA-style)
- Adapter fine-tuning during routing
