# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-24T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Self-Play)
- **Gap ID**: gap_1
- **Gap Title**: Unified Benchmark for LLM Data Attribution Comparison
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Reframing from "which method wins" to "what does each method measure" unlocks explanatory power
- Mode profiles as continuous vectors handle mode entanglement elegantly
- Contrastive probing enables cheap ground truth without leave-one-out retraining

### Breakthrough Moments
- Dr. Nova's spectroscopy analogy sparked the fingerprinting concept
- Prof. Vera's diagnostic task framework made fingerprinting testable
- Dr. Nova's contrastive probing solved the ground truth problem

---

## Final Hypothesis

### Title
Attribution Method Fingerprinting via Contrastive Mode Probing

### Hypothesis ID
H-AttributionFingerprint-v1

### Core Claim
Under the scope of LLM data attribution at 7B parameter scale, if we characterize attribution methods by their mode profiles (sensitivity to memorization vs feature transfer vs spurious association), then methods will exhibit stable, dissociable fingerprints across model families, because different attribution algorithms embed different inductive biases about what makes training data influential.

### Mechanism
1. **Step 1**: Attribution methods compute influence via mathematically distinct operations (TRAK: gradient projection, TracIn: checkpoint proximity, Kronfluence: K-FAC Hessian)
2. **Step 2**: These computational differences create different sensitivities to training data properties
3. **Step 3**: Different sensitivities manifest as measurable mode profile differences when probed with contrastive test points

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | Methods show dissociable mode profiles | F-ratio > 4.0, Cohen's d > 0.5 | F-ratio < 2.0, Cohen's d < 0.3 |
| P2 | Profiles stable within methods | Cronbach's alpha > 0.8 | alpha < 0.6 |
| P3 | Profiles transfer across models | Cross-model r > 0.7 | r < 0.5 |

---

## Novelty

**Key Innovation**: Reframes benchmarking from comparative accuracy to explanatory taxonomy via mode fingerprinting

**Differentiation**:
- vs DATE-LM: We explain WHY methods differ, not just that they differ
- vs TRAK/Kronfluence papers: We provide cross-method taxonomy, not single-method characterization
- vs Basu 2020: We frame differences as informative signatures, not just failures

---

## Experimental Design

### Models
- LLaMA-2-7B
- Mistral-7B
- Qwen-7B
- CodeLLaMA-7B (domain-specialized control)

### Datasets
- OpenWebText (memorization probes via MinHash duplicate detection)
- SQuAD (feature probes via semantic similarity)
- Waterbirds-Text adaptation (spurious association probes)

### Methods
- TRAK (MadryLab/trak)
- TracIn (frederick0329/TracIn, adapted for LLMs)
- Kronfluence (pomonam/kronfluence)

### Compute
- ~900 GPU-hours for full study
- 3 models × 3 methods × 3 modes × 1000 probe pairs

---

## Limitations

- TracIn requires checkpoint adaptation for LLM setting
- 70B validation deferred to future work
- Contrastive probe construction may miss some influence modes
- Results may not transfer to non-English or multimodal models

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 3 (all mitigated) |

### Remaining Concerns & Mitigations
1. **Effect size uncertainty** → Cohen's d > 0.5 threshold
2. **Training data overlap confound** → CodeLLaMA inclusion
3. **Hyperparameter sensitivity** → 3-setting analysis per method

---

**Status**: Ready for Phase 2B
