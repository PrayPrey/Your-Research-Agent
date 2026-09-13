# Phase 2B Context: h-m2

**Generated**: 2026-08-09
**Hypothesis ID**: h-m2
**Type**: MECHANISM
**Gate**: SHOULD_WORK

---

## Hypothesis Statement

On low-entropy subset (H_L < 25th percentile), trajectory metrics achieve AUROC > 0.55 with 95% CI LB > 0.50

---

## Prerequisites

| ID | Status | Result |
|----|--------|--------|
| h-e1 | VALIDATED | Mean AUROC 0.5657 > 0.55 threshold |

---

## Experimental Setup

### Dataset
- **Name**: TruthfulQA MC1 (low-entropy subset)
- **Source**: HuggingFace datasets (truthful_qa)
- **Subset**: H_L < 25th percentile (~204 samples from 817 total)
- **Labels**: Binary correctness

### Model
- **Name**: LLaMA-2-7B
- **Source**: meta-llama/Llama-2-7b-hf
- **Layers**: 24-32 (logit-lens validated)
- **Hidden dim**: 4096

### Controlled Variables
- Decoding: Greedy (temperature=0)
- Sequence length: Median aggregation per token
- Layer range: 24-32

---

## Success Criteria

| Metric | Success | Falsification |
|--------|---------|---------------|
| AUROC | > 0.55 | 95% CI includes 0.50 |
| 95% CI LB | > 0.50 | CI LB <= 0.50 |

---

## Gate Condition

**SHOULD_WORK**: If fails, continue workflow but log limitation. This tests whether trajectory metrics provide signal specifically in low-entropy cases where output entropy alone is uninformative.

---

## Rationale

The low-entropy subset represents "confident but wrong" cases where the model's output distribution is peaked (low H_L) but the answer is incorrect. Standard entropy-based detection fails here because the model appears confident. If trajectory metrics (NTI, CMI) can still detect hallucinations in this subset, it demonstrates they capture information beyond output entropy.

---

## Archon Task ID

031bbca3-ba2d-453a-990b-84da495782f5
