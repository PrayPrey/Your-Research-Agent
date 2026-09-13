# Phase 2B Context: H-M1

**Generated:** 2026-05-04 (JIT by Phase 2C step-01)
**Source:** 02b_verification_plan.md
**Hypothesis ID:** h-m1

---

## Hypothesis

**ID:** H-M1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Prerequisites:** H-E1 (COMPLETED — PASS)

**Statement:**
Under the same evaluation inputs with H2O eviction at r=50%, if eviction-aware LoRA adapters are compared to sequential baseline adapters, then per-layer attention entropy and heavy-hitter concentration (top-20% attention token score ratio) will differ significantly (paired t-test p < 0.05 on at least 50% of transformer layers), because token-scarcity regularization during training causes adapters to develop qualitatively different attention patterns calibrated to the evicted-cache distribution.

**Rationale:**
This hypothesis tests the second causal step — that the weight differentiation observed in H-E1 manifests as a functional change in attention behavior, specifically the distribution of attention mass across token positions. Verifying attention entropy difference provides mechanistic evidence that training under token scarcity produces adapters that genuinely re-distribute attention, not merely store different noise. This distinguishes token-scarcity regularization from random dropout, which would produce isotropic weight differences without systematic attention redistribution.

---

## Variables

- **Independent:** Adapter type (eviction-aware vs. sequential baseline)
- **Dependent:** Per-layer attention entropy (H = -Σ p_i log p_i); per-layer heavy-hitter concentration (ratio of attention mass on top-20% tokens)
- **Controlled:** Same evaluation inputs (LongBench subset, ≥500 samples per category), same H2O eviction at r=50% applied identically at inference

---

## Verification Protocol

1. Load both adapter variants (eviction-aware and sequential) for LLaMA-2-7B and Mistral-7B-v0.1.
2. Run forward pass on ≥500 LongBench samples per category with H2O eviction at r=50%; record per-layer attention score matrices.
3. Compute attention entropy (H = -Σ p_i log p_i) per layer per head; aggregate to mean per-layer entropy.
4. Compute heavy-hitter concentration: ratio of attention mass on top-20% tokens (by cumulative attention score) per layer.
5. Apply paired t-test across layers for both metrics; report percentage of layers with p < 0.05.

---

## Success Criteria

- **Primary:** Paired t-test p < 0.05 on attention entropy in ≥50% of transformer layers (at least one of LLaMA-2-7B or Mistral-7B-v0.1)
- **Secondary:** Heavy-hitter concentration ratio differs by ≥5% in mean across layers (directional evidence)

**Failure Response:**
IF fails (no significant attention entropy difference): EXPLORE — check whether attention difference appears at later layers; examine model with higher baseline heavy-hitter stability; consider attention-level analysis per specific task categories.

---

## Experimental Setup (from Phase 2A via Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Evaluation Dataset** | LongBench (≥500 samples/category, standard test split) | Canonical long-context NLP benchmark covering 21 tasks across 6 categories — directly tests attention behavior under long-context inputs |
| **Fine-tuning Dataset** | LongAlpaca-12k (Yukang/LongAlpaca on HuggingFace) | Used in H-E1; provides long-context fine-tuning signal; reused for controlled comparison |
| **Model** | LLaMA-2-7B + Mistral-7B-v0.1 (trained adapters from H-E1) | Adapters already trained in H-E1; reuse enables direct controlled comparison |

**Dataset Details:**
- LongBench: THUDM/LongBench (HuggingFace Hub)
- LongAlpaca-12k: Yukang/LongAlpaca (HuggingFace Hub)
- Evaluation: ≥500 samples per category (standard split, no subsampling below 500)

**Model Details:**
- Adapters: reuse from H-E1 validation (eviction-aware and sequential baseline variants)
- LoRA config: rank=16, alpha=32, dropout=0.05 (same as H-E1)
- Eviction: H2O at r=50% applied identically at inference for both variants

---

## Continuation Context (from H-E1)

**H-E1 Result:** PASS — All 24 LoRA layers show cosine similarity < 0.95 (min=-0.578, mean=0.053). H2O eviction mask injection confirmed to produce significantly different gradient signals. Gate MUST_WORK satisfied.

**Reused from H-E1:**
- Trained adapter checkpoints (eviction-aware + sequential baseline) for LLaMA-2-7B and Mistral-7B-v0.1
- H2OEvictionAwareAttention hook implementation (code/model.py)
- LongAlpacaDataset loading code (code/data.py)
- LoRA hyperparameters: rank=16, alpha=32, dropout=0.05

**H-M1 Extension:** Adds attention score extraction hooks to record per-layer attention matrices during LongBench forward passes.

---

## Source References

- Phase 2A Section 1.3 (Causal Step 2), Section 1.2 (Variables)
- 02b_verification_plan.md §2.2 H-M1
- H-E1 validation report: h-e1/04_validation.md
