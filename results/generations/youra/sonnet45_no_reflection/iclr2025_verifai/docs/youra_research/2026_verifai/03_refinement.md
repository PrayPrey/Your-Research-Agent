# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-12T05:08:38Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: GAP-1
- **Gap Title**: Integration of SMT/SAT Solvers as Differentiable Layers in Neural Architectures
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: Mechanistically grounded theory with explicit falsification criteria at every level, honest scoping to locally factorizable constraints, and architecturally generative framework

### Key Insights

- Pure continuous relaxation of discrete logic introduces spurious fractional minima that don't transfer to discrete solutions - requires learned heuristics for basin entry
- Basin recovery depends on multiple factors: normalized Hamming distance (d/n), violation structure entropy (H), and gradient-discrete alignment (cosine similarity)
- Honest scoping to locally factorizable constraint systems makes claims defensible while remaining impactful
- Computational advantage requires hardware-normalized throughput measurement (correct solutions per GPU-hour), not just sample efficiency metrics
- Compositional amplification likely represents covariance reduction in shared representations rather than emergent logical reasoning - scope claims accordingly

### Breakthrough Moments

- **Dr. Nova**: Treating SMT/SAT solvers as differentiable "physics" - enabling gradient flow through constraint satisfaction landscape via continuous relaxation
- **Prof. Vera**: Basin Recovery Curve (BRC) as primary diagnostic - recovery probability as function of (d/n, entropy, gradient alignment)
- **Prof. Pax**: Gradient-discrete alignment as core mechanism - contraction mapping requirement and measurable cosine similarity metric
- **Dr. Ally**: Two-stage hybrid architecture synthesis combining learned message-passing heuristics (Stage 1) with temperature-annealed refinement (Stage 2)
- **Prof. Rex**: Controlled degradation experiments to empirically derive phase boundary - flip k variables from satisfying assignments to test Stage 2 recovery

---

## Final Hypothesis

### Title
Conditional Basin Recovery for Neural-Symbolic Constraint Integration

### Hypothesis ID
H-ConditionalBasinRecovery-v1

### Core Claim

Under locally factorizable constraint systems with explicit graph structure (SAT, typed CSPs), if a two-stage neural-symbolic architecture combines learned constraint-graph message-passing (Stage 1) with temperature-annealed Gumbel-softmax refinement (Stage 2), then discrete violation rates reduce to <2% with ≥2× computational throughput over rejection sampling, because Stage 1 places solutions in recoverable basins (d/n < 0.15, H > 2.5) where gradient-discrete alignment (cosine > 0.7) enables Stage 2 local refinement to converge to discrete satisfying assignments.

### Mechanism

**Stage 1 (Learned Heuristics):**
Graph neural networks on constraint representations learn message-passing strategies (NeuroSAT-style) that generate structured near-solutions satisfying >85% of constraints with diffuse violation patterns (entropy H > 2.5). This places outputs within recoverable basins characterized by normalized Hamming distance d/n < 0.15 from nearest satisfying assignment.

**Stage 2 (Annealed Refinement):**
Temperature-annealed Gumbel-softmax performs local gradient-based search in continuous relaxation, converging to discrete satisfying assignments when initialized within recoverable basins. Annealing addresses train-test mismatch by gradually introducing discretization during training.

**Basin Geometry Theory:**
Recovery probability exhibits sharp phase transition at d/n ≈ 0.15 when gradient-discrete alignment (cosine similarity > 0.7) is maintained during annealing. This characterizes when continuous optimization can solve discrete constraint problems through local refinement in structured basins.

---

## Predictions

### P1: Basin Recovery Phase Transition (Primary)
**Statement**: Basin Recovery Probability exhibits sharp phase transition: >95% recovery at d/n < 0.15 with H > 2.5, collapsing to <20% at d/n > 0.30

**Test Method**: Controlled degradation on exhaustive 3-SAT (≤15 variables): flip k variables from satisfying assignments to induce specific d/n levels, measure Stage 2 convergence probability

**Success Criterion**: Logistic regression fit yields d₀ ≈ 0.15 ± 0.03 with β > 50 (indicating sharp transition)

**Falsification**: If recovery decays smoothly without clear threshold, or if d₀ shifts significantly across constraint structures, basin theory lacks predictive power

### P2: Gradient-Discrete Alignment as Predictor
**Statement**: Gradient-discrete alignment (cosine similarity > 0.7) predicts recovery success better than Hamming distance alone

**Test Method**: Measure cosine similarity between Gumbel-softmax gradients and optimal single-variable flip directions during refinement; stratify recovery probability by alignment level

**Success Criterion**: Recovery probability >90% when cosine > 0.7 even at d/n = 0.20; <50% when cosine < 0.4 even at d/n = 0.10

**Falsification**: If recovery is independent of gradient alignment after controlling for Hamming distance, mechanism explanation is incomplete

### P3: Computational Throughput Advantage
**Statement**: Computational throughput achieves ≥2× correct solutions per GPU-hour vs. batched rejection sampling under matched V100 constraints

**Test Method**: HumanEval-Contracts benchmark: measure correct programs per GPU-hour for two-stage vs. rejection baseline under equal memory/batch constraints

**Success Criterion**: Throughput ratio ≥ 2.0 with statistical significance (p < 0.01)

**Falsification**: If ratio < 1.5×, architectural advantage is marginal or represents sample-efficiency-only gain without throughput benefit

---

## Novelty

**Key Innovation**: Conditional Basin Recovery (CBR) framework - mechanistic theory characterizing geometry of constraint-satisfiability basins in neural parameter space

**What's New**: 
- Combines learned heuristics with annealed refinement in principled two-stage architecture
- Provides measurable phase boundaries (d/n, entropy, gradient alignment) for when continuous optimization can solve discrete problems
- CBR framework is architecturally generative - tells designers what to optimize for (basin entry probability, diffuse violations) not just accuracy

**Differentiation from Prior Work**:
- Unlike SATNet (single-stage relaxation with limited scalability), combines learned heuristics for basin entry with local refinement
- Unlike NeuroSAT (heuristics only without refinement), adds gradient-based local search in recoverable basins
- Beyond post-hoc verification's wasted computation, integrates constraints during generation with measurable ≥2× throughput advantage

---

## Experimental Design

### Datasets
1. **Random 3-SAT**: ≤15 variables (exhaustive Basin Recovery analysis), 50-200 variables (scalability)
2. **Structured Parity-Heavy SAT**: XOR-dominant constraints for adversarial evaluation
3. **HumanEval-Contracts**: Real-world code synthesis with formal specifications
4. **Typed CSP Benchmarks**: Cross-constraint-family generalization tests

### Baselines
1. **Rejection Sampling**: Standard LLM generation + post-hoc SAT/contract verification + rejection cycles
2. **Solver-in-the-Loop**: Iterative generation with solver feedback but no gradient flow
3. **Pure Relaxation (Ablation)**: Single-stage continuous relaxation without learned heuristics

### Key Experiments
1. **Basin Recovery Curve Mapping**: Controlled degradation from known satisfying assignments, measure recovery as function of (d/n, H, gradient alignment)
2. **Phase-Transition Stratification**: Evaluate across density bands (α < 3.8, 4.1-4.3, > 4.5), measure <5× degradation at critical band
3. **Annealing Sensitivity**: Test linear/exponential/cosine schedules, measure Annealing Robustness Index (ARI < 1% target)
4. **Compositional Contracts**: Independent vs. coupled multi-function tests to distinguish compositionality from covariance
5. **Hardware-Normalized Throughput**: Matched V100 memory/batch constraints, measure correct solutions per GPU-hour

---

## Limitations

### Scope Boundaries
**Applies to**: Locally factorizable constraint systems with explicit graph structure (SAT, CSP, typed first-order constraints with low-order interactions)

**Does NOT apply to**: 
- Globally coupled constraints without local structure (graph isomorphism, certain SMT arithmetic)
- First-order logic with quantifiers or unbounded domains
- Problems requiring exact provable correctness (provides probabilistic <2% violation guarantee)

### Known Constraints
- Requires Stage 1 to achieve >85% clause satisfaction (pre-conditioning criterion) for Stage 2 effectiveness
- Performance may degrade up to 5× at SAT phase transition (α ∈ [4.1, 4.3]) relative to easy instances
- Cross-constraint-family generalization requires architecture modifications or retraining (not zero-shot)

### Remaining Questions
- Does basin recovery depend on structural graph metrics (treewidth, clause overlap) beyond Hamming distance and entropy?
- Can gradient-discrete alignment be improved through architectural modifications to widen recovery radius?
- What is the optimal annealing schedule balancing convergence speed and robustness (ARI criterion)?

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Mechanistically grounded with falsification criteria |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 3 (Hamming distance sufficiency, compositionality vs. covariance, 85% threshold grounding) |

### Remaining Objections with Mitigation
1. **Basin Descriptor Sufficiency**: Extend BRC analysis to include structural graph metrics (treewidth proxy, clause overlap clustering) alongside d/n and entropy
2. **Compositional Mechanism**: Conduct independent vs. coupled contract experiments; scope to covariance reduction if amplification only appears for independent case
3. **Threshold Mechanistic Grounding**: Perform controlled degradation with logistic regression to empirically derive Stage 2 recovery phase boundary

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
