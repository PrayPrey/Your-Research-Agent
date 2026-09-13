# Phase 2B Verification Plan
## Cross-Family Generalization of Single-Pass Uncertainty Probes

**Generated:** 2026-08-24  
**Main Hypothesis:** H-SEP-CrossFamily-v1  
**Status:** READY for Phase 2C

---

## Main Hypothesis

Hidden-state uncertainty probes (SEPs) achieve hallucination detection performance within 0.05 AUROC of multi-sample semantic entropy across multiple LLM families (Llama-3, Mistral, Qwen-2), demonstrating architecture-invariant uncertainty encoding.

---

## Sub-Hypotheses

### h-e1 (EXISTENCE) — MUST_WORK
**Statement:** SEPs achieve AUROC within 0.05 of multi-sample SE on Llama-3-8B, Mistral-7B, Qwen-2-7B on TruthfulQA (817 samples)

- **Status:** READY
- **Prerequisites:** None
- **Gate:** MUST_WORK (failure blocks pipeline)
- **Success Criterion:** AUROC gap ≤0.05 for at least 2/3 families, none >0.10
- **Falsification:** Gap >0.05 for 2+ families OR any family shows gap >0.10

### h-m1 (MECHANISM) — SHOULD_WORK
**Statement:** Probes trained on TriviaQA (~11K) achieve AUROC >0.70 when evaluated on TruthfulQA (cross-dataset transfer)

- **Status:** NOT_STARTED
- **Prerequisites:** [h-e1]
- **Gate:** SHOULD_WORK (failure does not block)
- **Success Criterion:** Cross-dataset AUROC >0.70
- **Falsification:** Cross-dataset AUROC <0.60

### h-m2 (MECHANISM) — SHOULD_WORK
**Statement:** Probes transfer across model families with AUROC gap <0.10 (train on Model A, evaluate on Model B)

- **Status:** NOT_STARTED
- **Prerequisites:** [h-e1]
- **Gate:** SHOULD_WORK (failure does not block)
- **Success Criterion:** Transfer gap <0.10 AUROC
- **Falsification:** Transfer gap >0.15 AUROC

---

## Dependency Graph (DAG)

```
h-e1 (MUST_WORK)
  ├── h-m1 (SHOULD_WORK)
  └── h-m2 (SHOULD_WORK)
```

h-m1 and h-m2 can run in parallel after h-e1 validates.

---

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| h-e1 fails | Pipeline blocked | Pre-registered 2/3 family success criterion |
| Layer selection inconsistency | Confounded results | Standardized validation-set tuning procedure |
| Statistical power insufficient | Inconclusive results | 817 samples provides 80% power at α=0.05 |

---

## Timeline

1. **Phase 2C:** Experiment design for h-e1
2. **Phase 3:** Implementation planning
3. **Phase 4:** PoC validation (h-e1 first, then h-m1/h-m2 parallel)
4. **Phase 5:** Baseline comparison (multi-sample SE)

---

## Experimental Setup

- **Models:** Llama-3-8B-Instruct, Mistral-7B-Instruct-v0.2, Qwen-2-7B-Instruct
- **Evaluation Dataset:** TruthfulQA (817 questions)
- **Training Dataset:** TriviaQA (~11K for transfer experiments)
- **Baseline:** Multi-sample Semantic Entropy (5 samples)
- **Probe:** Linear (as in original SEP paper)
