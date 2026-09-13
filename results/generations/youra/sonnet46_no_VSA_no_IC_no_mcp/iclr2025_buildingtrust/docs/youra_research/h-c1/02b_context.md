# Hypothesis Context: H-C1 (JIT Generated from 02b_verification_plan.md)

**Generated:** 2026-08-25
**Source:** docs/youra_research/02b_verification_plan.md (Phase 2B)
**Hypothesis ID:** h-c1

---

## Hypothesis Information

**ID:** h-c1
**Type:** CONDITION
**Statement:** RLHF alignment moderates calibration degradation: Llama-2-7B-chat shows significantly lower ΔECE than Llama-2-7B-base (paired comparison across same adversarial tasks), because RLHF training calibrates confidence expression toward human-expected uncertainty levels — reducing the overconfidence pattern that drives ΔECE increases under adversarial perturbation.

**Rationale:** H-E1 established that ECE increases under adversarial perturbation (ΔECE > 0). H-M1 confirmed that confidence-accuracy decoupling is the mechanism. This CONDITION hypothesis tests whether RLHF alignment (present in chat variants, absent in base variants) moderates the magnitude of ΔECE. If chat models show systematically lower ΔECE than base models across the same adversarial tasks, RLHF's calibration-dampening effect is confirmed as a moderating condition.

**Success Criteria (PoC: Direction-based):**
- Primary: Llama-2-7B-chat shows lower ΔECE than Llama-2-7B-base on ≥60% of adversarial task × split combinations
- Secondary: Effect is consistent across both AdvGLUE and ANLI task types

**Gate:** SHOULD_WORK
**Prerequisites:** h-e1 (PASS), h-m1 (PASS)

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | AdvGLUE (MNLI adversarial) + ANLI (R1/R2/R3) + clean counterparts (GLUE MNLI, MultiNLI) | Same datasets used in H-E1 and H-M1; enables controlled ΔECE comparison across base vs. chat model pairs |

- **Source:** HuggingFace datasets hub
- **Identifiers:** `allenai/anli` (ANLI R1/R2/R3); `adv_glue` (AdvGLUE); `glue` (clean MNLI); `multi_nli` (clean NLI)
- **Cache path:** `~/.cache/huggingface/datasets/`
- **Verified:** H-E1 and H-M1 confirmed all splits loadable and ≥200 examples per cell

### Model

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Baseline model** | Llama-2-7B-base (meta-llama/Llama-2-7b-hf) | No RLHF — pure pretraining; provides the "uncalibrated" baseline |
| **Condition model** | Llama-2-7B-chat (meta-llama/Llama-2-7b-chat-hf) | RLHF-aligned variant of same architecture; paired comparison isolates RLHF effect |

- **Type:** Open-weight decoder-only transformer (matched architecture, different alignment)
- **Source:** HuggingFace Hub (official Meta releases)
- **Cache path:** `~/.cache/huggingface/hub/`
- **Verified:** Both models confirmed available in H-E1

### Hypothesis Fit

- **Dataset fits because:** Same adversarial/clean pairs from H-E1 enable direct ΔECE comparison without confounds; NLI tasks confirmed to show ΔECE signal in H-E1
- **Model fits because:** Llama-2-7B-base and Llama-2-7B-chat are architecturally identical, differing only in RLHF alignment — the minimal paired comparison to isolate RLHF's calibration effect
- **Control confirmed:** Same prompt templates, tokenizer, 15-bin ECE computation as H-E1 and H-M1

---

## Phase 2B Planning Notes

- **IV:** RLHF alignment status (base vs. chat variant of same 7B architecture)
- **DV:** ΔECE = ECE(adversarial) − ECE(clean) per (model, task) cell
- **Controlled:** Architecture size (7B), prompt format, ECE binning method, task selection
- **Key risk:** RLHF may affect logit scale independently of calibration — mitigate by examining both raw ECE and reliability diagrams
- **H-E1 reuse:** ECE values for both Llama-2-7B-base and Llama-2-7B-chat were already computed in H-E1; this hypothesis can reuse those measurements directly
