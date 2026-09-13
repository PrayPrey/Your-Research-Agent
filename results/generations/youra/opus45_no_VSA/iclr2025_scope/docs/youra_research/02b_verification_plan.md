# Phase 2B: Verification Plan
## H-IPCR-v1: Instruction-Prefix-Conditioned Adapter Routing

**Generated:** 2026-08-09T12:16:30+00:00  
**Main Hypothesis:** Zero-shot prefix-based adapter routing achieves ≥90% of oracle task-specific LoRA performance  
**Archon Project:** `07144d4f-0a39-4d5e-b837-021dae2229a7`

---

## Sub-Hypotheses

| ID | Type | Statement | Gate | Prerequisites | Status |
|----|------|-----------|------|---------------|--------|
| H-E0 | EXISTENCE | Instruction prefixes are linearly separable by FLAN task family (macro-F1 ≥0.75 on 10+ families) | MUST_WORK | — | READY |
| H-E1 | EXISTENCE | Linear probe on frozen MiniLM embeddings achieves ≥70% oracle adapter selection accuracy (or top-3 ≥85%) | MUST_WORK | H-E0 | NOT_STARTED |
| H-M1 | MECHANISM | Zero-shot IPCR routing achieves ≥90% of oracle task-specific LoRA performance on held-out FLAN tasks | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | Routing is robust to paraphrase (cosine ≥0.90) and keyword masking (<10% absolute drop) | SHOULD_WORK | H-E1 | NOT_STARTED |

---

## Dependency Graph

```
H-E0 (Prefix Separability)
  │
  └──► H-E1 (Linear Probe Accuracy)
         │
         ├──► H-M1 (IPCR ≥90% Oracle)
         │
         └──► H-M2 (Robustness)
```

---

## Gate Definitions

### MUST_WORK Gates (Blocking)
- **H-E0:** If macro-F1 < 0.75 on task family classification → hypothesis fundamentally fails
- **H-E1:** If top-1 < 70% AND top-3 < 85% → linear alignment insufficient
- **H-M1:** If performance < 80% of oracle OR not significant vs uniform → core claim fails

### SHOULD_WORK Gates (Non-blocking)
- **H-M2:** Robustness analysis valuable but not required for core claim

---

## Success Criteria (from Phase 2A)

| Prediction | Threshold | Falsification |
|------------|-----------|---------------|
| P1: Linear probe accuracy | Top-1 ≥70% OR Top-3 ≥85% | Top-3 <60% |
| P2: IPCR performance | ≥90% of oracle | <80% OR not significant vs uniform |
| P3: Paraphrase robustness | Cosine ≥0.90 | Cosine <0.80 |
| P3: Masking robustness | <10% drop | >20% drop |

---

## Experimental Setup

- **Dataset:** FLAN instruction collection (62 task categories, held-out task family split)
- **Base Model:** Llama-2-7B-chat or Mistral-7B-Instruct
- **Adapter Bank:** k=8-10 task-specific LoRAs, rank r=16
- **Sentence Encoder:** Frozen MiniLM-L6-v2 (~22M params)
- **Baselines:** Random selection, Uniform combination, LORAUTER-zero, Oracle

---

## Archon Task Mapping

| Hypothesis | Task ID |
|------------|---------|
| H-E0 | `3f3cabbb-50a6-4f25-97d1-65da6eb01b5b` |
| H-E1 | `5433e19d-b5d6-480b-b01b-5615bdac8f40` |
| H-M1 | `4f2fef1a-cd9b-400a-a668-9e3d54dc7298` |
| H-M2 | `bc4c469f-d3c8-4255-851f-2eaf63fd5f4f` |

---

## Next Steps

1. Phase 2C: Design experiment for H-E0 (prefix separability)
2. Phase 3: Implementation planning for H-E0
3. Phase 4: Execute and validate H-E0
4. Proceed to H-E1 if H-E0 passes MUST_WORK gate
