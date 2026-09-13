# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-26
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Discussion (Independent Controller Ablation)
- **Gap ID**: gap1_cross_method_benchmark
- **Gap Title**: Cross-Method Benchmark Comparison Methodology
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Alignment methods may trade off differently across dimensions, not just perform better/worse overall
- Bidirectional framing: training method differences reveal what benchmarks actually measure
- Existing benchmarks can serve as dimensional probes without new annotation

### Breakthrough Moments
- Dr. Nova's asymmetric mapping idea (Exchange 1)
- Prof. Vera's concrete falsification criteria with effect size thresholds (Exchange 2, 8)
- Data ablation proposal to isolate method vs data effects (Exchange 7)

---

## Final Hypothesis

### Title
Dimensional Alignment Signatures: Cross-Benchmark Comparison of RLHF vs DPO

### Core Claim
Under controlled conditions (same base model, same preference data, same compute budget), if we compare PPO-based RLHF and Direct Preference Optimization (DPO), then we will observe differential performance profiles across alignment benchmarks (TruthfulQA, HHH-helpful, HHH-harmless), because the methods' mechanistic differences (explicit reward model smoothing vs direct closed-form optimization) create distinct alignment signatures detectable on existing evaluation infrastructure.

### Mechanism
1. PPO-RLHF trains explicit reward model → smooths preference landscape
2. DPO directly optimizes policy → preserves sharp preference boundaries
3. Smooth vs sharp optimization creates different alignment attractors
4. Different attractors manifest as differential benchmark performance

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | Differential profiles: at least one benchmark diverges (d > 0.3) while others remain similar (d < 0.15) | At least one d > 0.3 AND one d < 0.15 | All d < 0.15 OR all d > 0.3 |
| P2 | Cross-benchmark correlations differ between methods | Fisher z-test p < 0.05 | Correlations indistinguishable |
| P3 | Data ablation produces method-dependent profile shifts | Significant interaction effect | No interaction effect |

---

## Novelty

**Key Innovation**: Using cross-benchmark performance patterns as a probe into alignment method mechanisms, revealing alignment as multi-dimensional rather than monolithic.

**Differentiation from Prior Work**:
- Rafailov 2023 (DPO): Compared on single benchmarks → we compare cross-benchmark profiles
- Ouyang 2022 (InstructGPT): Single method → we compare multiple methods systematically
- Standard comparisons: Aggregate scores → we analyze dimensional signatures

---

## Experimental Design

| Component | Specification |
|-----------|---------------|
| **Base Model** | Llama-2-7B |
| **Training** | huggingface/trl DPOTrainer + PPOTrainer with LoRA |
| **Data** | Anthropic HH-RLHF preference dataset |
| **Benchmarks** | TruthfulQA (~800), HHH-helpful, HHH-harmless |
| **Compute** | Single A100, ~2-3 weeks |
| **Baselines** | Base Llama-2-7B (no alignment), SFT-only |

---

## Limitations

- **Scale**: Results at 7B may not generalize to larger models (70B+)
- **Model Family**: Single architecture (Llama-2); other architectures untested
- **Language**: English benchmarks only
- **Reward Model**: RLHF comparison depends on reward model quality (mitigated by documented training with validation)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met after 12 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Scale generalization, reward model quality (documented as limitations) |

---

## Phase 2B Readiness

| Sub-Hypothesis | Description |
|----------------|-------------|
| **SH1 (Existence)** | Alignment benchmarks measure distinct dimensions (pre-test: correlation < 0.5) |
| **SH2 (Mechanism)** | Reward model smoothing vs direct optimization creates measurable differences |
| **SH3 (Comparison)** | Deferred to Phase 5 baseline comparison |

**Status**: ✅ READY FOR PHASE 2B
