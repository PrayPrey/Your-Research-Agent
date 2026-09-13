# Phase 2A: Refinement Summary

## Metadata

- **Generated at**: 2026-07-12T11:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap-1
- **Gap Title**: Integration of Multi-Modal Execution Feedback for Alignment
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met after 15 exchanges (minimum threshold). Criteria assessed: SPECIFIC (core claim stated), MECHANISM (three-phase weight schedule explained), PREDICTIONS (three testable predictions with success criteria), NOVELTY (differentiated from PPOCoder, Themis, Curriculum-RLAIF), FEASIBILITY (technical barriers addressed, ~5000 GPU-hour budget within norms), OBJECTIONS (measurement interference, reward scaling, training stability, necessity of dynamic weights all addressed).

### Key Insights

1. **Paradigm Shift**: Current research silos feedback types (execution OR human OR AI). Tri-modal integration enables multi-objective optimization (correctness + quality simultaneously), unblocking production deployment.

2. **Sequential Capability Building**: Dynamic weight scheduling addresses training phase requirements - can't optimize quality if code doesn't execute (Phase 1: correctness foundation), can't fine-tune edge cases without base quality alignment (Phase 2: scalable quality via AI feedback), late-stage human feedback prevents AI bias propagation (Phase 3: edge case precision).

3. **Feasibility Validated**: All components (execution sandbox via CodeBenchGen, human annotation via RLHF protocols, AI reward models via Themis architecture) have battle-tested implementations. Computational cost (~5000 GPU-hours) within academic research norms. No fundamental technical barriers.

4. **Novelty Defensible**: Differentiated from all prior work - PPOCoder (single-feedback execution), Curriculum-RLAIF (single-feedback AI with task curriculum), Themis (multi-criteria offline), Process-Supervised RL (process-level execution only). Innovation: Online integration of heterogeneous feedback with dynamic scheduling.

### Breakthrough Moments

- **Exchange 5 (Dr. Ally)**: Staged feedback collection (execution → human → AI → RL training) solves measurement interference. Percentile rank transformation handles reward signal scaling across different distributions.

- **Exchange 8 (Prof. Vera)**: Three-stage experimental design (baselines → static multi → dynamic multi) provides publishable results even if full hypothesis partially fails. Stage 2 alone (static multi-modal) is novel contribution.

- **Exchange 11 (Dr. Ally)**: Convergence on refined core hypothesis with specific three-phase weight schedule mechanism. Each phase has clear role (correctness → quality → edge cases).

---

## Final Hypothesis

### Title
Tri-Modal Alignment for Code Generation via Dynamic Feedback Integration

### Core Claim

Under training conditions with access to execution feedback (automated test cases on HumanEval/MBPP), human feedback (quality preferences from 500 annotated samples), and AI feedback (learned reward model trained on combined execution+human data), if we apply a tri-modal RL framework with dynamic weight scheduling across three training phases (Phase 1: execution-heavy 0-30%, Phase 2: AI-feedback-heavy 30-70%, Phase 3: human-feedback-heavy 70-100%), then we achieve ≥3% absolute improvement in harmonic mean of pass@1 correctness and human preference quality scores compared to the best single-feedback baseline (execution-only, human-only, or AI-only), measured on held-out test sets (N=200) with independent evaluation (p<0.05).

### Mechanism

**Three-Phase Sequential Capability Building:**

**Phase 1 (0-30% training):** Execution-heavy weighting establishes basic correctness foundation. Evidence: PPOCoder [Shojaee et al., 2023] shows execution feedback enables functional code generation. Must achieve correctness before optimizing quality (can't refine non-functional code). Falsifier: If execution weight is NOT highest in Phase 1, or if correctness metrics do NOT improve fastest in early training, mechanism fails.

**Phase 2 (30-70% training):** AI feedback weighting enables scalable quality refinement. Evidence: Themis [Paul et al., 2026] demonstrates multi-criteria reward models can capture quality signals. AI feedback scales human preferences without per-sample annotation cost. Falsifier: If AI feedback weight does NOT peak in Phase 2, or if quality metrics do NOT improve during mid-training, mechanism fails.

**Phase 3 (70-100% training):** Human feedback weighting fine-tunes edge cases and corrects AI biases. Evidence: RLHF paradigm shows human feedback addresses model misalignment. Late-stage human feedback prevents AI reward model from propagating systematic biases to final model. Falsifier: If human feedback weight does NOT increase in Phase 3, or if edge case performance does NOT improve in late training, mechanism fails.

**Causal Logic:** Each phase builds prerequisite for next. Can't optimize quality if code doesn't execute (Phase 1 foundation). Can't fine-tune edge cases without base quality alignment (Phase 2 foundation). Dynamic weights adapt emphasis to match training stage capabilities.

---

## Predictions

### P1 (Primary): Performance Improvement

**Statement**: Tri-modal dynamic model achieves ≥3% absolute improvement in harmonic mean (pass@1 × human preference) vs. best single-feedback baseline.

**Test Method**: Independent samples t-test on N=200 held-out test samples, α=0.05, two-tailed.

**Success Criterion**: p < 0.05 AND effect size ≥ 3% absolute improvement (e.g., 0.70 → 0.73).

**Falsification**: If p ≥ 0.05 OR improvement < 3%, hypothesis fails (tri-modal does not outperform single-feedback).

### P2: Weight Pattern Systematicity

**Statement**: Weight coefficients show systematic phase-based pattern - execution weight highest in 0-30% training, AI weight peaks 30-70%, human weight increases 70-100%.

**Test Method**: Correlation analysis - Pearson ρ between (execution weight, training step) should be negative (ρ < -0.6), AI weight argmax in middle third, human weight positive correlation in final third.

**Success Criterion**: Execution ρ < -0.6, AI weight argmax ∈ [0.3, 0.7] training progress, Human weight increases in [0.7, 1.0].

**Falsification**: If weight patterns are random (no systematic phase structure) or static (weights constant across training), dynamic scheduling mechanism is not supported.

### P3: Conflict Case Behavior

**Statement**: Conflict cases (code correct but low-quality) show intermediate preference scores (0.1-0.4 range), not extreme collapse to execution-only behavior.

**Test Method**: Analyze 50 conflict cases (pass@1 = 1.0, human_preference < 0.3). Measure tri-modal model preference scores. Compare distribution to single-feedback baselines.

**Success Criterion**: Tri-modal preference scores: median ∈ [0.1, 0.4], not collapsed to [0.0, 0.1] (execution-only collapse).

**Falsification**: If tri-modal behaves identically to execution-only baseline on conflict cases (preference < 0.1), integration failed - model ignores human/AI feedback.

---

## Novelty

### What's New

Online integration of three heterogeneous feedback signals (execution, human, AI) during RL training with dynamic weight scheduling across training phases. Innovation: Dynamic weight schedule that adapts feedback emphasis to training phase (correctness → quality → edge cases), enabling multi-objective optimization via sequential capability building.

### Differentiation from Prior Work

| Prior Work | Key Limitation | Our Extension |
|------------|----------------|---------------|
| PPOCoder (Shojaee et al., 2023) | Single-feedback (execution-only) | Add human+AI feedback with dynamic integration |
| Curriculum-RLAIF (Li et al., 2025) | Single-feedback (AI-only) with task difficulty curriculum | Add execution+human feedback, curriculum on feedback type (not task difficulty) |
| Themis (Paul et al., 2026) | Multi-criteria reward model trained offline, used for ranking | Multi-modal rewards used online during RL with dynamic weights |
| Process-Supervised RL (Ye et al., 2025) | Process-level execution feedback (line-by-line verification) | Add human+AI feedback for quality beyond correctness |

---

## Experimental Design

### Dataset
HumanEval (164 problems) + MBPP (500 problems) = 664 total problems. 70/15/15 train/validation/test split → ~100 test samples per benchmark → 200 total held-out test samples.

### Model
1.5B parameter code LLM (Codex-style transformer decoder). Pre-trained checkpoint (e.g., CodeGen, StarCoder). RL fine-tuning via PPO (Proximal Policy Optimization).

### Baselines
1. **Execution-Only**: PPO with execution feedback (pass@1 reward)
2. **Human-Only**: PPO with human preference rewards (Bradley-Terry model from pairwise comparisons)
3. **AI-Only**: PPO with AI reward model (trained on execution+human data, used for inference)
4. **Tri-Modal Static**: PPO with fixed weight combination (best from grid search)

### Evaluation
- **Primary Metric**: Harmonic mean of pass@1 correctness and human preference quality
- **Statistical Test**: Independent samples t-test, α=0.05, two-tailed
- **Sample Size**: N=200 held-out test samples
- **Annotators**: Independent human annotators (different from training annotators, blind to condition)

---

## Limitations

### Scope Boundaries

**Applies to:**
- Code generation tasks with automated test cases (execution feedback available)
- Domains where human quality preferences are measurable (code review, style guides)
- Training regimes with sufficient data for AI reward model (≥500 human-annotated samples)
- RL-based training frameworks (PPO or similar policy gradient methods)
- Benchmark datasets: HumanEval, MBPP (competitive programming style tasks)

**Does NOT apply to:**
- Tasks without automated evaluation (creative writing, open-ended generation)
- Domains where human preferences are undefined or inconsistent (exploratory code, research prototypes)
- Small-data regimes (< 500 samples insufficient for reward model training)
- Non-RL training methods (supervised fine-tuning, in-context learning)
- Real-world software engineering tasks (multi-file projects, API integration) - hypothesis targets competitive programming benchmarks

### Known Limitations

1. **Task Scope**: Hypothesis tests competitive programming tasks (single-file solutions), not production codebases
2. **Cost**: Human feedback annotation (~$5-10K for 500 annotations) limits large-scale deployment
3. **Complexity**: Dynamic weight schedule requires hyperparameter search (9 parameters vs 3 for static weights)
4. **Assumption Dependency**: Assumes feedback types are orthogonal (A1) - needs empirical validation

### Key Assumptions

**A1**: Execution feedback, human feedback, and AI feedback capture orthogonal quality dimensions. Violation consequence: If highly correlated, tri-modal provides no benefit over single-feedback.

**A2**: Sequential capability building holds (correctness prerequisite for quality optimization). Violation consequence: If quality optimizable independently, dynamic scheduling unnecessary.

**A3**: Weight schedule parameterization (9 parameters) is expressive enough. Violation consequence: If optimal schedule requires complex patterns, constrained parameterization may limit performance.

**A4**: Human feedback annotation quality is sufficient (inter-annotator agreement ≥ 0.6 Krippendorff's α). Violation consequence: If too noisy, AI feedback propagates noise.

**A5**: Percentile rank transformation handles reward signal scaling. Violation consequence: If transformation loses critical information, aggregated reward may miss important signals.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met (specific, mechanism, predictions, novelty, feasibility, objections) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 3 (all mitigated) |

### Remaining Objections & Mitigations

1. **Dynamic weights necessity unproven** (could be unnecessary complexity)
   - Mitigation: Staged validation (Stage 2 tests static first, Stage 3 adds dynamic - isolated comparison)

2. **Aggregation function sensitivity** (harmonic vs geometric vs arithmetic affects results)
   - Mitigation: Report results for all aggregation functions - check robustness

3. **3% threshold justification** (needs statistical grounding)
   - Mitigation: Joint criterion (≥3% effect size AND p<0.05 statistical significance) + confidence intervals reported

---

## Phase 2B Readiness

**Status**: READY

**Next Steps**:
- Phase 2B: Design detailed verification protocol (statistical tests, experimental controls, dataset preparation)
- Address open questions: Optimal weight parameterization, aggregation function robustness, meta-learning extension (Stage 4)

**Open Questions**:
1. What is optimal weight schedule parameterization? (9 parameters may be over/under-constrained)
2. How robust is harmonic mean aggregation vs other functions? Needs sensitivity analysis.
3. Can weight schedule be learned via meta-learning? Or must it be hand-designed?

---

**End of Phase 2A Refinement**
