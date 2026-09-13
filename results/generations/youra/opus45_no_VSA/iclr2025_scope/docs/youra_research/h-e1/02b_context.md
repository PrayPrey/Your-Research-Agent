# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1  
**Type:** EXISTENCE  
**Statement:** Linear probe on frozen MiniLM embeddings achieves ≥70% oracle adapter selection accuracy (or top-3 ≥85%)

## Gate Condition
- **Gate Type:** MUST_WORK (Blocking)
- **Success Criteria:** Top-1 ≥70% OR Top-3 ≥85%
- **Falsification:** Top-3 <60%

## Prerequisites
- **H-E0:** Instruction prefixes are linearly separable by FLAN task family (macro-F1 ≥0.75)
  - **Status:** VALIDATED (macro-F1 = 0.995)

## Experimental Setup (from Phase 2B)

### Dataset
- FLAN instruction collection (62 task categories)
- Held-out task family split for evaluation

### Models
- **Sentence Encoder:** Frozen MiniLM-L6-v2 (~22M params)
- **Base Model (for oracle):** Llama-2-7B-chat or Mistral-7B-Instruct
- **Adapter Bank:** k=8-10 task-specific LoRAs, rank r=16

### Baselines
- Random selection
- Uniform combination
- LORAUTER-zero (if available)
- Oracle (upper bound)

## Continuation from H-E0

### Proven from H-E0
- MiniLM-L6-v2 embeddings capture task-discriminative features
- Linear separability confirmed (macro-F1 = 0.995 on 9 task families)
- Open-Orca/FLAN dataset verified as suitable

### Key Transition
H-E0 proved **task family** separability. H-E1 tests **adapter selection** accuracy:
- Instead of classifying into task families, predict which adapter (from bank of k adapters) should handle the instruction
- This requires: (1) LoRA adapters trained per task-family, (2) Oracle labels based on best-performing adapter

## Archon Reference
- **Project ID:** 07144d4f-0a39-4d5e-b837-021dae2229a7
- **Task ID:** 5433e19d-b5d6-480b-b01b-5615bdac8f40
