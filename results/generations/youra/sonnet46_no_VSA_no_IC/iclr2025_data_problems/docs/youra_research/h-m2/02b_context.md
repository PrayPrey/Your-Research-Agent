# Per-Hypothesis Context: H-M2

**Generated:** 2026-08-20 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** H-M2
**Type:** MECHANISM — Step 2 of 3
**Gate:** SHOULD_WORK

---

## Hypothesis Statement

Under the Pythia checkpoint trajectory (154 checkpoints × 16 model sizes), if cumulative Wikipedia exposure increases during training, then MMLU scores increase proportionally more than HellaSwag scores at comparable training steps (and vice versa for Books exposure), because domain-specific exposure accumulation selectively strengthens the capabilities aligned with each domain's cognitive pattern distribution.

---

## Variables

- **Independent:** Cumulative Wikipedia exposure fraction and Books exposure fraction at each checkpoint t
- **Dependent:** ΔMMLU / ΔHellaSwag ratio at each checkpoint (relative improvement rates)
- **Controlled:** Total training tokens seen (absorbed by checkpoint index), model size (analyzed per-size)

---

## Verification Protocol

1. From H-E1 output, extract Wikipedia and Books cumulative exposure fractions across 154 checkpoints for 3 representative model sizes (70M, 1B, 6.9B).
2. Run lm-evaluation-harness v0.4 on all 154 checkpoints × 3 model sizes for MMLU (5-shot) and HellaSwag (10-shot); apply 13-gram decontamination.
3. Compute Spearman correlation: ρ(Wikipedia_exposure_t, MMLU_t) and ρ(Wikipedia_exposure_t, HellaSwag_t) for each model size.
4. Test: ρ(Wikipedia→MMLU) > ρ(Wikipedia→HellaSwag) via Fisher z-test.
5. Repeat for Books → HellaSwag vs MMLU; report all correlations with 95% CI.

---

## Experimental Setup

**Dataset:**
- Name: The Pile
- Type: standard
- Source: EleutherAI
- HuggingFace: EleutherAI/the_pile
- Domain taxonomy: 22 known domains with published proportions
- Role: Training corpus with exact dataloader ordering enabling domain exposure computation

**Model:**
- Name: Pythia model suite
- Type: Autoregressive LM (GPT-NeoX architecture)
- Source: EleutherAI/pythia-* on HuggingFace
- Sizes: 70M, 160M, 410M, 1B, 1.4B, 2.8B, 6.9B, 12B (plus dedup variants)
- Checkpoints: 154 per model size

**Benchmark Evaluation:**
- MMLU (5-shot) via lm-evaluation-harness v0.4
- HellaSwag (10-shot) via lm-evaluation-harness v0.4
- Subset for H-M2: 3 representative model sizes (70M, 1B, 6.9B)

---

## Success Criteria

- **Primary:** ρ(Wikipedia→MMLU) > ρ(Wikipedia→HellaSwag) for ≥2 of 3 representative model sizes
- **Secondary:** ρ(Books→HellaSwag) > ρ(Books→MMLU) for ≥2 of 3 model sizes

---

## Gate Condition

**Type:** SHOULD_WORK  
**Pass:** Directional correlation confirmed for ≥2 of 3 model sizes  
**Fail:** EXPLORE — proceed to H-M3 with limitation documented; correlations may be masked by scale effects

---

## Dependencies

- H-E1 (VALIDATED, MUST_WORK): Domain exposure trajectories measurable
- H-M1 (VALIDATED, MUST_WORK): Domain content differences confirmed

---

## Key Implementation Notes

- H-E1 outputs domain exposure fractions per checkpoint — reuse directly
- H-M1 confirmed Wikipedia entity density > Books; Books narrative coherence > Wikipedia
- 13-gram decontamination is MANDATORY before computing correlations
- Use Fisher z-test for Spearman ρ comparison
- Analyze per model size (do not pool across sizes to avoid scale confound)
