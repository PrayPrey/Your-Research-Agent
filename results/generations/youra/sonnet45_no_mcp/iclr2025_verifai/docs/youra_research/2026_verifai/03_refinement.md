# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-04-20T02:57:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: GAP-001
- **Gap Title**: Scalable LLM-Guided Search Strategies for Non-Halting Formal Proofs
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 21

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 21

**Convergence Reason**: Reached max_exchanges (20) with all convergence criteria met. All personas provided STRONG verdicts on novelty, falsifiability, significance, and feasibility.

### Key Insights
- **Paradigm shift**: From "how to make LLMs better at proof search" to "how neural models encode proof space geometry"
- **Portfolio allocation framework**: Solves false positive problem by reducing budget rather than abandoning unconventional proofs
- **Confidence as geometric proxy**: LLM detects unfamiliarity with proof states (distribution shift) rather than explicitly recognizing non-termination
- **Remarkable feasibility**: Total validation cost is only 70 GPU-hours (40% of LeanDojo baseline training)
- **Plugin architecture**: Implementation via DojoCritic interface enables adoption without forking LeanDojo

### Breakthrough Moments
1. **Exchange 7**: Reframing from binary termination detection to portfolio allocation under uncertainty
2. **Exchange 13**: Confidence geometry as manifold proxy—addresses out-of-distribution concern about LLMs never seeing diverging proofs
3. **Exchange 10**: Precise overhead calculation (15% not 30-50%) validates net positive efficiency
4. **Exchange 14**: Complete three-phase validation protocol with clear go/no-go gates

---

## Final Hypothesis

### Title
"Learned Compute Allocation for Neural Theorem Proving: Detecting Non-Terminating Proof Search via Confidence Geometry"

### Core Claim
Under neural theorem proving with LLM-based tactic suggestion (e.g., LeanDojo), **if** we deploy a learned compute allocator using LLM confidence geometry (softmax entropy trajectory std dev) combined with symbolic divergence signals (state hash collisions, proof state growth) and search tree metrics (backtrack frequency, branching factor), **then** proof success rate per unit compute improves by >15% compared to fixed-timeout baselines, **because** LLM confidence trajectories encode the manifold structure of successful proof spaces, and divergence from this manifold (detected via confidence instability) correlates with probable non-termination.

### Mechanism
The allocator treats proof search as a **portfolio allocation problem** under uncertainty. Instead of binary "terminate/continue" decisions, it dynamically adjusts compute budgets across multiple proof strategies based on risk signals:

1. **LLM confidence trajectory** reflects familiarity with proof state patterns from training distribution
2. **Confidence instability** (high variance in softmax entropy) indicates the search is entering unfamiliar proof space regions that don't resemble successful proof patterns
3. **Symbolic features** (state hash collisions, exponential growth) provide complementary divergence signals
4. **Portfolio allocation** reallocates saved compute to alternative proof strategies, improving overall success rate

**Key theoretical insight**: The LLM detects distribution shift (unfamiliar proof states) rather than explicitly recognizing non-termination. This addresses the out-of-distribution problem: even though the LLM was never trained on diverging proofs, its confidence encodes geometric properties of the successful proof space manifold.

---

## Predictions

### P1: Primary Prediction (Success Rate Improvement)
- **Statement**: Learned allocator achieves >15% higher proof success rate per unit compute compared to fixed 30-step timeout baseline on LeanDojo test set
- **Test Method**: Controlled experiment with fixed total compute budget (1000 GPU-seconds), measure theorems proven by each allocation strategy
- **Success Criterion**: Statistical significance p<0.05 via two-tailed t-test, improvement >15%
- **Falsification**: If improvement <5% or allocator underperforms any baseline

### P2: Signal Validation
- **Statement**: Confidence derivative (std dev of softmax entropy) correlates with eventual timeout outcome (correlation coefficient >0.3) in Phase 1 validation
- **Test Method**: 100 extended-timeout experiments (100× normal = 300s), extract confidence derivatives from first 15 steps
- **Success Criterion**: Pearson r > 0.3 OR Spearman ρ > 0.3
- **Falsification**: If both r < 0.3 AND ρ < 0.3, signal is too weak

### P3: Hybrid Architecture Advantage
- **Statement**: Three-signal hybrid (confidence + symbolic + search tree) outperforms single-signal ablations
- **Test Method**: Ablation study comparing confidence-only, symbolic-only, search-tree-only vs. combined model
- **Success Criterion**: Combined model achieves highest success rate
- **Falsification**: If any single signal matches or exceeds combined performance

---

## Novelty

### What's New
1. **Novel framing**: First work to treat proof search resource allocation as a meta-learning problem using LLM confidence geometry
2. **Theoretical insight**: Confidence trajectories encode proof space manifold structure—generalizes beyond theorem proving to any neural reasoning system (SAT/SMT solving, program synthesis, planning)
3. **Practical system**: 15% compute efficiency gain via lightweight plugin with only 15% overhead (net positive)

### Differentiation from Prior Work
- **vs. LeanDojo [Yang et al., 2023]**: LeanDojo focuses on tactic prediction (what to try next), we focus on resource allocation (when to quit). Orthogonal and combinable—our allocator can be used with their ReProver model.
- **vs. Fixed timeout strategies (Z3, traditional theorem provers)**: Fixed resource limits are non-adaptive and cannot distinguish "needs more time" from "likely unprovable." Our approach is content-aware via confidence geometry.
- **vs. Symbolic divergence detection**: Pure symbolic methods (state hashing, cycle detection) miss semantic similarity. Our hybrid approach adds LLM semantic signal to detect equivalent dead-ends with different syntax.

---

## Experimental Design

### Dataset
- **Name**: LeanDojo Benchmark
- **Size**: 98,734 theorems from Lean's math library
- **Split**: 60% training (59,240), 20% validation (19,747), 20% test (19,747)
- **Ground Truth**: 500 additional theorems with extended timeout (100× normal = 300s)

### Model
- **Base Prover**: LeanDojo ReProver (retrieval-augmented LLM)
- **Allocator Architecture**: Lightweight MLP with 3 input signals → budget allocation weight (~10K parameters)

### Baselines
1. Fixed 30-step timeout (LeanDojo default)
2. Uniform random allocation
3. Depth-first search with fixed budget

### Three-Phase Validation Protocol

**Phase 1: Signal Validation** (8 GPU-hours)
- Validate confidence derivative signal on 100 extended-timeout cases
- Measure correlation with eventual outcome (success vs. timeout)
- **Gate**: Correlation > 0.3 to proceed to Phase 2

**Phase 2: Full System Validation** (42 GPU-hours)
- Train allocator on 60% LeanDojo, validate on 20%, test on 20%
- Evaluate success rate @ fixed compute budget (1000 GPU-sec) vs. baselines
- **Gate**: >15% improvement, p<0.05

**Phase 3: Ablation & Analysis** (20 GPU-hours)
- Test each signal in isolation vs. combined model
- Sensitivity analysis on thresholds and timeout parameters
- Error analysis for false positives and false negatives

**Total Compute**: 70 GPU-hours (3 GPU-days) = 40% of LeanDojo baseline training cost

---

## Limitations

### Scope Limitations (Must State in Paper)
1. **System-specific**: Validated only on Lean + LeanDojo, not Coq/Isabelle/HOL
2. **Architecture-specific**: GPT-style transformer models only, not T5/BERT-based provers
3. **Ground truth approximation**: Extended-timeout experiments (100× normal budget) approximate but don't prove true undecidability

### Known Risks
1. **False positive risk**: Unconventional proof paths with oscillating confidence might be abandoned prematurely
   - **Mitigation**: Portfolio allocation reduces budget rather than aborting; Phase 3 error analysis quantifies FP rate
2. **Overhead risk**: If meta-reasoning overhead exceeds 20%, efficiency gains become marginal
   - **Mitigation**: Precise calculation shows 15% overhead (450ms per 3-second proof)
3. **Signal weakness risk**: If correlation < 0.3 in Phase 1, confidence signal is too weak
   - **Mitigation**: Clear go/no-go gate; hypothesis revision if signal fails

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All personas STRONG verdicts, 21 exchanges, comprehensive validation pathway |
| **Clarity Verified** | Yes - complete hypothesis with mechanism, predictions, and falsification criteria |
| **Remaining Objections** | None - scope limitations acknowledged and mitigation strategies defined |

### Readiness for Phase 2B
✅ **READY** - Hypothesis is complete, testable, feasible, and significant
- Clear Under-If-Then-Because statement
- Concrete predictions with success/falsification criteria
- Three-phase validation pathway with 70 GPU-hour budget
- Plugin implementation strategy (LeanDojo DojoCritic interface)
- Broader impact story (generalizes to neural reasoning systems)

---

## Future Work Trajectory

### Immediate Follow-Up
1. Cross-system validation: Test on Coq (CoqGym), Isabelle (IsaPlanner)
2. Cross-domain generalization: Apply to SAT solving, program synthesis
3. Adaptive calibration: Online recalibration based on observed outcomes

### Long-Term Vision
**Closing the loop**: Use observed divergence patterns as negative examples for LLM fine-tuning, teaching models to avoid tactics that lead to non-terminating paths. This completes the feedback cycle from detection to prevention.

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
