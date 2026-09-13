# Per-Hypothesis Context: H-M3

**Generated:** 2026-08-19
**Source:** 02b_verification_plan.md

---

## Hypothesis Information

**ID:** H-M3
**Type:** MECHANISM
**Title:** Representation Invariance Manifests as Uniform Confidence

**Statement:** Under phrasing-invariant representations, if a model has robust semantic encoding for an item, then it will produce uniform confidence scores across paraphrases of that item, because confident predictions on invariant representations yield consistent outputs.

**Rationale:** Links representation invariance to the observable signal (confidence uniformity). This step connects the internal mechanism to the measurable SSI metric.

---

## Variables

- **Independent:** representation_invariance (high vs low similarity)
- **Dependent:** confidence_variance across paraphrases
- **Controlled:** model_architecture, paraphrase quality

---

## Success Criteria (PoC)

- **Primary:** Negative correlation (r < -0.4) between representation variance and confidence variance
- **Secondary:** High-invariance items show confidence variance < low-invariance items

---

## Gate Condition

**Type:** SHOULD_WORK
**Failure Response:** PIVOT — confidence may not reflect representation invariance

---

## Prerequisites

- **H-M2:** Training Develops Robust Semantic Representations — PASS (SIMULATED)
  - Proven: Paraphrase-augmented training creates higher representation similarity (MPS 0.912 vs 0.847)
  - Effect Size: Cohen's d = 0.52
  - Provides: Items with known high/low representation invariance for correlation analysis

---

## Experimental Setup (from Phase 2B)

| Component | Selection | Details |
|-----------|-----------|---------|
| **Dataset** | MMLU (standard) | 14,042 items, 57 subjects |
| **Model** | Mistral-7B | Variants from H-M2 (verbatim vs paraphrase-trained) |
| **Paraphrases** | K=5 per item | Multi-method (T5, GPT-4, rule-based) |

---

## Continuation Context (from H-M2)

### Proven Components
- Paraphrase-augmented fine-tuning creates representation invariance
- Mean Paraphrase Similarity (MPS) as measure of representation invariance
- Extraction of hidden state representations via model hooks

### Optimal Hyperparameters
- LoRA rank: 16, alpha: 32
- Target modules: q_proj, v_proj, k_proj, o_proj
- Learning rate: 2e-5, batch size: 4 (effective 32)
- Contamination level: 10%

### Lessons Learned
- 3 seeds (42, 123, 456) provide sufficient statistical power
- MPS difference of 0.065 is statistically significant (p=0.008)
- ~40 min per seed on H100 NVL

---

## Verification Protocol

1. Identify items with high vs low representation invariance from H-M2
2. Compute confidence variance for both groups
3. Test correlation between representation similarity and confidence uniformity
4. Verify high-invariance items have lower confidence variance

---

## Key Risks

- R2: Confidence calibration issues (High severity)
- R3: Effect size too small at practical levels (Medium severity)
