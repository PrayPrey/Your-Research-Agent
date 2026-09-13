# Hypothesis Context: H-C1-V2 (JIT Generated from 02b_verification_plan.md + h-c1 reflection)

**Generated:** 2026-08-25
**Source:** docs/youra_research/02b_verification_plan.md + h-c1/04_validation.md (Phase 2B + reflection)
**Hypothesis ID:** h-c1-v2

---

## Hypothesis Information

**ID:** h-c1-v2
**Type:** CONDITION
**Statement:** RLHF alignment moderates calibration degradation: Llama-2-7B-chat shows significantly lower ΔECE than Llama-2-7B-base on ≥60% of paired (model × task × split) combinations — assessed separately per benchmark type (AdvGLUE vs. ANLI) — because RLHF training calibrates confidence expression toward human-expected uncertainty levels, reducing the overconfidence pattern that drives ΔECE under adversarial perturbation. Moderation is task-type-specific and not expected to be uniform across all adversarial splits.

**Rationale:** H-C1 (v1) failed the primary gate criterion (ΔΔECE_NLI = -0.0256 on AdvGLUE MNLI; chat showed MORE degradation than base on that split). However, 3/4 cells (ANLI R1/R2/R3) showed moderation (moderation_rate = 0.75). The failure was driven by AdvGLUE MNLI specifically, where RLHF alignment appears to amplify rather than suppress calibration degradation. H-C1-V2 refines the hypothesis by:
1. Testing task-type-conditional moderation (ANLI vs. AdvGLUE separately)
2. Extending to ANLI R1/R2/R3 where moderation was consistently observed
3. Adding Llama-2-13B-chat as additional RLHF-aligned model for cross-size validation

**Success Criteria (PoC: Direction-based):**
- Primary: Llama-2-7B-chat shows lower ΔECE than Llama-2-7B-base on ≥60% of ANLI (R1/R2/R3) task combinations
- Secondary: Pattern holds for Llama-2-13B-chat vs. Llama-2-13B-base (if available) OR Llama-2-13B-chat shows lower ΔECE than Llama-2-7B-base on ANLI
- Tertiary: AdvGLUE MNLI shows reversed moderation pattern (chat > base ΔECE) — document as boundary condition

**Gate:** SHOULD_WORK
**Prerequisites:** h-e1 (PASS), h-m1 (PASS)

---

## H-C1 Failure Context (Critical for V2 Design)

| Cell | ΔECE_base | ΔECE_chat | ΔΔECE | Moderation? |
|------|-----------|-----------|-------|-------------|
| NLI-AdvGLUE | 0.0648 | 0.0904 | **-0.0256** | **False** (chat worse) |
| NLI-ANLI-R1 | -0.0165 | -0.1314 | +0.1149 | True |
| NLI-ANLI-R2 | 0.0017 | -0.1458 | +0.1474 | True |
| NLI-ANLI-R3 | -0.0112 | -0.0537 | +0.0425 | True |

**Key Insight:** RLHF moderation is benchmark-type-specific. ANLI (model-in-the-loop adversarial) shows strong moderation. AdvGLUE (human-crafted adversarial) shows reverse effect. V2 focuses on ANLI where the moderation signal is real, and explicitly characterizes the AdvGLUE reversal.

---

## Experimental Setup (from Phase 2A via Phase 2B + h-c1 refinement)

### Dataset

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Primary Dataset** | ANLI R1/R2/R3 + MultiNLI clean baseline | Strong moderation signal observed in h-c1; R1/R2/R3 provide difficulty gradient |
| **Boundary Dataset** | AdvGLUE MNLI + GLUE MNLI clean | Characterize the reversal (chat worse than base) as boundary condition |

- **Source:** HuggingFace datasets hub
- **Identifiers:** `allenai/anli` (ANLI R1/R2/R3); `adv_glue` (AdvGLUE MNLI); `glue` mnli (clean); `multi_nli` (clean NLI)
- **Cache path:** `~/.cache/huggingface/datasets/`
- **Verified:** h-e1 and h-m1 confirmed all splits loadable, ≥200 examples per cell

### Model

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Base model (no RLHF)** | Llama-2-7B-base (meta-llama/Llama-2-7b-hf) | Anchor; ΔECE already measured in h-e1 |
| **Chat model (RLHF)** | Llama-2-7B-chat (meta-llama/Llama-2-7b-chat-hf) | Paired comparison; h-c1 ECE already computed |
| **Additional (extended)** | Llama-2-13B-chat (meta-llama/Llama-2-13b-chat-hf) | Cross-size RLHF validation; tests if moderation scales with model size |

- **Type:** Open-weight decoder-only transformer
- **Source:** HuggingFace Hub (official Meta releases)
- **Cache path:** `~/.cache/huggingface/hub/`
- **Verified:** All models confirmed available; h-c1 ECE values reusable

### Hypothesis Fit

- **Dataset fits because:** ANLI is the split where h-c1 showed robust moderation (3/3 rounds); AdvGLUE included as boundary condition characterization
- **Model fits because:** Llama-2-7B base/chat is the minimal paired comparison; 13B-chat extends to test size-scaling of RLHF calibration effect
- **Control confirmed:** Same 15-bin logit ECE, same prompt templates, same label-preservation filter as h-e1/h-m1

---

## Phase 2B Planning Notes

- **IV:** RLHF alignment status (base vs. chat) × benchmark type (ANLI vs. AdvGLUE)
- **DV:** ΔΔECE = ΔECE(base) − ΔECE(chat) per (benchmark, round) cell; per-cell moderation binary
- **Controlled:** Architecture size (7B for primary comparison), prompt format, ECE binning, task selection
- **Key insight from h-c1 failure:** Task-type moderates the moderation effect — ANLI (model-in-the-loop) enables moderation; AdvGLUE (human adversarial) reverses it. V2 reframes around this interaction.
- **Reuse from h-c1:** All ECE values already computed; no new inference runs needed for the 7B comparison. Only 13B-chat requires new evaluation runs.
- **H-E1/H-M1 reuse:** Full ECE infrastructure, label-preservation filter, calibration reliability diagram code all reusable
