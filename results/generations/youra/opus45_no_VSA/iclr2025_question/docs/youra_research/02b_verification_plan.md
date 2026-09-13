# Phase 2B Verification Plan
## H-CLTI-v1: Cross-Layer Trajectory Instability for Hallucination Detection

**Generated**: 2026-08-09  
**Main Hypothesis ID**: H-CLTI-v1  
**Archon Project ID**: 6665db82-e427-4352-96ac-5ec53169d980

---

## Main Hypothesis

Under single-pass inference on TruthfulQA MC1 (LLaMA-2-7B, layers 24-32), hallucinated responses exhibit higher trajectory instability (NTI), lower convergence monotonicity (CMI), and characteristic competition patterns (RCI), because factual retrieval follows stable attractor dynamics while fabrication requires iterative cross-layer constraint satisfaction.

---

## Sub-Hypotheses Inventory

| ID | Type | Gate | Status | Prerequisites | Statement |
|----|------|------|--------|---------------|-----------|
| h-e1 | EXISTENCE | MUST_WORK | READY | - | NTI (layers 24-32) achieves AUROC > 0.55 on TruthfulQA MC1 |
| h-m1 | MECHANISM | SHOULD_WORK | NOT_STARTED | h-e1 | Combined model [H_L + NTI + CMI] improves AUROC >= 0.03 over H_L alone with LRT p < 0.05 |
| h-m2 | MECHANISM | SHOULD_WORK | NOT_STARTED | h-e1 | On low-entropy subset (H_L < 25th percentile), trajectory metrics achieve AUROC > 0.55 with 95% CI LB > 0.50 |
| h-m3 | MECHANISM | SHOULD_WORK | NOT_STARTED | h-e1 | RCI flip pattern appears in >= 30% hallucinations and < 10% correct responses |

---

## Dependency Graph (DAG)

```
h-e1 (MUST_WORK) ──┬──> h-m1 (SHOULD_WORK)
                   ├──> h-m2 (SHOULD_WORK)
                   └──> h-m3 (SHOULD_WORK)
```

**Execution Order**: h-e1 first (foundation), then h-m1/h-m2/h-m3 in parallel.

---

## Risk Analysis

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| False attractor problem - hallucinations converge smoothly | HIGH | 0.4 | CMI metric tests monotonicity; head-to-head comparison reveals |
| RCI flip prevalence < 30% | MEDIUM | 0.5 | Pre-registered threshold; adjust claims to detection-only if pattern rare |
| NTI collinear with H_L (r > 0.9) | HIGH | 0.3 | P2 tests incremental validity; if collinear, trajectory adds nothing |
| Logit-lens degradation in layers 24-32 | MEDIUM | 0.2 | Use tuned-lens fallback; restrict to layers 28-32 if needed |
| Sample size too small for low-entropy subset | LOW | 0.3 | ~204 samples; bootstrap CI handles small n |

---

## Timeline

| Phase | Hypothesis | Estimated Duration | Notes |
|-------|------------|-------------------|-------|
| Phase 2C | h-e1 | 1 day | Experiment design for NTI extraction |
| Phase 3 | h-e1 | 1 day | Implementation planning |
| Phase 4 | h-e1 | 2 days | PoC validation (817 samples, 5-fold CV) |
| Phase 2C-4 | h-m1, h-m2, h-m3 | 3 days | Parallel after h-e1 validated |
| Phase 5 | All | 1 day | Baseline comparison vs raw entropy |

**Total estimated**: 8 days

---

## Dialectical Analysis

### Signal Source
- **Thesis**: Internal trajectory captures epistemic processing state beyond output
- **Antithesis**: Output entropy already captures hallucination signal (AUROC 0.6426)
- **Synthesis**: NTI normalizes by H_L to extract trajectory-specific component; tests whether trajectory adds incremental validity

### Mechanism
- **Thesis**: Fabrication causes trajectory instability due to constraint satisfaction without grounded knowledge
- **Antithesis**: Smooth false attractors exist - model may confidently converge to wrong answer
- **Synthesis**: CMI tests convergence monotonicity; RCI tests representational competition; together they probe mechanism

### Interpretability
- **Thesis**: RCI flip pattern reveals decision dynamics (model knew correct answer early, overrode it)
- **Antithesis**: Pattern may be rare (<30% prevalence)
- **Synthesis**: Pre-registered prevalence threshold; if <30%, adjust claims to detection utility only

---

## Experimental Setup (Shared Across Sub-Hypotheses)

### Dataset
- **Name**: TruthfulQA MC1
- **Source**: HuggingFace datasets (truthful_qa)
- **Size**: 817 questions
- **Labels**: Binary correctness (correct=1, incorrect=0)

### Model
- **Name**: LLaMA-2-7B
- **Source**: meta-llama/Llama-2-7b-hf
- **Layers**: 32 total, analysis on layers 24-32
- **Hidden dim**: 4096

### Controlled Variables
- Decoding: Greedy (temperature=0)
- Sequence length: Median aggregation per token
- Layer range: 24-32 (logit-lens validated)

### Baselines
1. Raw mean entropy (H_L): AUROC 0.6426 (established)
2. P(True) probe: AUROC ~0.57

---

## Success Criteria Summary

| Hypothesis | Success | Falsification |
|------------|---------|---------------|
| h-e1 | AUROC > 0.55 in >= 4/5 folds | Any fold AUROC < 0.52 |
| h-m1 | AUROC gain >= 0.03, LRT p < 0.05 | AUROC gain < 0.02 or p >= 0.10 |
| h-m2 | AUROC > 0.55, 95% CI LB > 0.50 | 95% CI includes 0.50 |
| h-m3 | >= 30% hallucinations, < 10% correct | < 20% hallucinations or >= 15% correct |

---

## Archon Task Mapping

| Hypothesis | Archon Task ID |
|------------|----------------|
| h-e1 | b351c3a0-ea01-4879-a48d-69f31854820b |
| h-m1 | 592ff1b6-32f4-4b1f-ad50-ef28d1f9f8c4 |
| h-m2 | 031bbca3-ba2d-453a-990b-84da495782f5 |
| h-m3 | 6bbf36bf-178a-4602-9525-e7f7ac964f2e |

---

## Next Steps

1. Begin Phase 2C with h-e1 (READY status)
2. Generate detailed experiment design for NTI extraction and evaluation
3. After h-e1 validated, process h-m1/h-m2/h-m3 in parallel
