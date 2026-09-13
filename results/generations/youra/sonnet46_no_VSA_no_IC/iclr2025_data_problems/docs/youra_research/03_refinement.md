# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-20
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap-1
- **Gap Title**: No Systematic Per-Filter × Per-Benchmark Correlation Analysis on Existing Checkpoints
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12
- **Hypothesis ID**: H-DomainExposureBenchmarkSpecificity-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova (🔭 Novelty), Prof. Vera (🔬 Validation), Dr. Sage (🎯 Impact), Prof. Pax (⚙️ Feasibility), Dr. Ally (🛡️ Synthesis), Prof. Rex (🔍 Critique)

**Total Exchanges**: 12

**Convergence Reason**: All 6 convergence criteria met at Exchange 11 — SPECIFIC directional predictions, explicit MECHANISM, 4 falsifiable PREDICTIONS, confirmed NOVELTY, verified FEASIBILITY, OBJECTIONS addressed with mitigations.

### Key Insights
- Pythia's exact dataloaders are an underutilized resource — the data ordering encodes domain exposure trajectories that no prior study has exploited
- CoLoR-Filter's 11-25x task-conditioned efficiency gain provides theoretical grounding for domain-benchmark specificity at pre-training scale
- The within-family panel design (2,464 observations) eliminates the cross-family confounds (corpus size, architecture) that plague prior domain mixing studies
- Contamination pre-correction is not optional — PaCoST's finding ("almost all models suspected contaminated") means raw benchmark scores would produce biased domain coefficients

### Breakthrough Moments
- **Exchange 4 → 6**: Prof. Pax ruled out DataModels/influence functions (infeasible at scale) and Prof. Rex identified that within-Pythia domain composition is fixed — forcing the pivot to data ordering as source of domain variation
- **Exchange 7**: Dr. Nova reframed data ordering as temporal domain exposure trajectories — the key methodological innovation
- **Exchange 8**: Prof. Vera specified the exact panel regression formula and falsification criteria, completing the statistical design

---

## Final Hypothesis

### Title
Domain Exposure-Benchmark Specificity in Pre-trained LLMs

### Core Claim
Under the Pythia model family trained on The Pile, if cumulative domain exposure trajectories are computed from exact dataloaders at 154 training checkpoints across 16 model sizes (70M-12B), then a panel regression with model-size fixed effects will reveal domain-benchmark specific effects: Wikipedia exposure positively predicts MMLU more than HellaSwag; Books exposure positively predicts HellaSwag/WinoGrande more than MMLU — because different domains concentrate different cognitive task patterns that selectively strengthen the capabilities measured by each benchmark.

### Null Hypothesis
Domain composition coefficients are identical across all 4 benchmarks after controlling for model scale (β_d the same for MMLU, HellaSwag, ARC-Challenge, WinoGrande for all domains d).

### Mechanism
1. **Domain content differentiation**: Different Pile domains concentrate different cognitive task patterns (Wikipedia → factual/entity; Books → narrative/causal; GitHub → formal reasoning)
2. **Selective representation strengthening**: As cumulative domain exposure accumulates during training, model representations align with concentrated cognitive patterns, proportionally strengthening domain-aligned capabilities
3. **Linear benchmark prediction**: Benchmark scores reflect the weighted sum of domain exposures with benchmark-specific weights (β coefficients), quantifiable via panel regression

---

## Predictions

| ID | Statement | Success Criterion |
|----|-----------|-------------------|
| P1 (primary) | β_Wikipedia > β_Books for MMLU | p < 0.05, one-tailed panel regression |
| P2 | β_Books > β_Wikipedia for HellaSwag | p < 0.05, one-tailed panel regression |
| P3 | Domain profiles differ across ≥2 of 4 benchmarks | FDR-corrected q < 0.05 |
| P4 | Domain rankings consistent across 70M-400M vs 1B-12B | Spearman > 0.7 for MMLU and HellaSwag |

---

## Novelty

**Key Innovation**: First use of Pythia's exact dataloader ordering to construct a within-family domain exposure panel dataset (2,464 observations) for benchmark-specific coefficient estimation — eliminates cross-family confounds.

**Differentiation**:
- vs DCLM: holistic 53-task aggregate → we provide per-domain × per-benchmark specificity
- vs Pythia paper: memorization/scaling analysis → we exploit dataloader ordering for domain attribution
- vs RegMix/DoReMi: aggregate validation loss optimization → individual benchmark capability profiles
- vs CoLoR-Filter: task-conditioned filtering at C4 → observational domain attribution at The Pile/Pythia scale

---

## Experimental Design

**Dataset**: The Pile (EleutherAI/the_pile) — Pythia's training corpus with 22 known domains and exact proportions

**Model**: Pythia suite (EleutherAI/pythia-* on HuggingFace) — 70M to 12B, 154 checkpoints each, identical architecture

**Evaluation**: lm-evaluation-harness v0.4 — 5-shot MMLU, 10-shot HellaSwag, 25-shot ARC-Challenge, 5-shot WinoGrande

**Contamination Pre-step**: 13-gram decontamination (lm-evaluation-harness built-in) on The Pile vs all 4 benchmark test sets

**Statistical Model**: Panel OLS — `benchmark_score(i,t) = α_i + Σ_d β_d × exposure_d(t) + γ × log(params_i) + ε`

**Baselines**: Scale-only model, shared-β constrained model, permutation null

**Compute**: 50-100 GPU-hours for evaluation; preprocessing and regression are lightweight; estimated 1-2 weeks total

---

## Limitations

- **Data ordering**: If The Pile is uniformly shuffled, within-family domain variation is zero; fallback to cross-family design with n=15+ model families (Pythia, OLMo, Falcon, MPT, Bloom, etc.)
- **Observational**: Panel regression establishes correlation not causal intervention; ablation experiments with new training runs would strengthen causal interpretation
- **Multicollinearity**: 22-domain feature set may have correlated exposure trajectories; PCA fallback if VIF > 10
- **Corpus specificity**: Findings are specific to The Pile's 22-domain structure; may not generalize to FineWeb2 or DCLM corpora
- **Scale ceiling**: Pythia's largest model (12B) may not generalize to frontier scale (100B+)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Exchange 11 of 12 — all 6 criteria met |
| **Clarity Verified** | Yes |
| **Feasibility Confirmed** | Yes — 1-2 weeks, standard academic compute |
| **Remaining Objections** | A1 (data ordering), multicollinearity — both have mitigations |

---

*Phase 2A complete → Ready for Phase 2B (Research Planning)*
