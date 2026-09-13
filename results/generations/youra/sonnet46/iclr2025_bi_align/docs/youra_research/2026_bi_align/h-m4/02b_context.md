# H-M4 Context: PM-Score Mediates C_sem Above Surface-Feature Controls

**Generated:** JIT from 02b_verification_plan.md (Phase 2C step-01)
**Hypothesis ID:** h-m4
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Hypothesis Statement

PM-score proxy (chosen/rejected preference) positively predicts C_sem^H←A (beta > 0, p < 0.05) after controlling for surface-feature controls (response length, bullet/list structure, politeness marker density, syntactic complexity), because the epistemic quality encoded in RLHF training drives accommodation above and beyond formatting signals.

---

## Rationale

This tests the mechanistic specificity of the epistemic uptake sensitivity hypothesis: does RLHF-quality drive accommodation via epistemic content, or merely via formatting salience (bullet points, polite phrasing)? This is the weakest assumption in the causal chain (mechanism step 2) and the critical test for interpretable findings. Either outcome is informative: PM significance → epistemic quality mechanism; PM null → formatting salience mechanism.

---

## Variables

- **IV:** PM-score proxy (chosen/rejected preference; categorical mapped to quality gradient)
- **DV:** C_sem^H←A (continuous)
- **CV (Surface-feature controls):** Response length (word count), bullet/list structure (instruction_decomp_density), politeness markers (politeness_freq), syntactic complexity (TTR, sentence length)

---

## Experimental Setup

### Dataset
| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Anthropic/hh-rlhf (helpful-base, helpful-rejection-sampled, helpful-online) | Three-tier RLHF quality gradient; chosen/rejected structure provides PM-score proxy; same dataset as prior hypotheses for controlled comparison |
| **Type** | standard | HuggingFace public dataset |
| **Source** | HuggingFace: `datasets.load_dataset('Anthropic/hh-rlhf', data_dir='helpful-base|helpful-rejection-sampled|helpful-online')` |
| **Cache** | `/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/.data_cache/datasets/hh-rlhf` (verified from prior runs) |

### Model
| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Primary** | all-MiniLM-L6-v2 | Validated across h-e1, h-m1, h-m2, h-m3; C_sem reliably measured |
| **Robustness** | paraphrase-MiniLM-L6-v2, all-mpnet-base-v2 | Multi-model robustness established in h-m1+ |
| **Type** | sentence-transformers (pre-trained, inference-only) |
| **Cache** | `~/.cache/huggingface/hub/sentence-transformers` (verified) |

---

## Verification Protocol

1. Construct mediation regression: C_sem^H←A ~ PM_proxy + response_length + bullet_density + politeness_freq + syntactic_complexity + tier.
2. Test significance of PM_proxy coefficient (β_PM) after all surface-feature controls are included.
3. Compare β_PM (full model) to β_PM (PM-only model) to assess surface-feature mediation proportion.
4. Run robustness check: replace PM_proxy with tier rank; confirm tier effect also survives controls.
5. Report whether PM_proxy becomes non-significant when surface features are added (formatting hypothesis supported) or remains significant (epistemic quality hypothesis supported).

---

## Success Criteria

- **Primary:** β_PM > 0 and p < 0.05 in full mediation model with surface-feature controls
- **Secondary:** β_PM does not shrink to zero when surface features added (epistemic quality not fully mediated by formatting)

---

## Gate Condition

- **Type:** SHOULD_WORK
- **If Fail:** Document mechanism as formatting-driven rather than epistemic; publish existence + tier results with mechanism caveat; reformulate as "RLHF formatting signals drive accommodation" hypothesis in future work

---

## Prerequisites Status

| Hypothesis | Status | Key Finding |
|------------|--------|-------------|
| h-m1 | VALIDATED (MUST_WORK PASS) | J-T p=0.001; C_sem monotonically increases with tier across all 3 SBERT models |
| h-m2 | VALIDATED (SHOULD_WORK PASS) | C_sem^H←A > C_sem^A←H at all 3 tiers × 3 models; directional asymmetry confirmed |
| h-m3 | FAILED (SHOULD_WORK FAIL) | Within-prompt Δ=cos(H_next, A_chosen)-cos(H_next, A_rejected) < 0 (25/27 combos); H_next more similar to rejected than chosen |

---

## Continuation Context (from h-m1, h-m2, h-m3)

### Proven Components (Reuse)
- Dataset cache: `/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/.data_cache/datasets/hh-rlhf` (verified)
- SBERT embedding pipeline: all-MiniLM-L6-v2 batch=256
- C_sem computation with matched-shuffle baseline
- Three-tier stratification (helpful_base, helpful_rejection_sampled, helpful_online)
- Bidirectional C_sem computation (H←A and A←H)
- KS test + IPW weighting (triggered in h-m1)

### Optimal Hyperparameters (from prior validations)
- bootstrap_resamples: 1000
- bootstrap_seed: 42
- cohen_d_threshold: 0.1
- knn_k: 5
- significance_level: 0.05
- min_n_pairs: 1000

### Critical Lessons from h-m3 Failure
- Within-prompt Δ-cosine probe falsified (H_next systematically closer to rejected, d up to -0.74)
- Cosine similarity in SBERT embedding space does NOT discriminate chosen vs rejected at within-prompt level
- This DOES NOT invalidate tier-level C_sem (h-m1/h-m2 confirmed); surface-feature mechanism still testable
- H-M4 proceeds with "reduced causal claim" (no within-prompt causal probe support)

---

*JIT-generated by Phase 2C step-01 from 02b_verification_plan.md*
