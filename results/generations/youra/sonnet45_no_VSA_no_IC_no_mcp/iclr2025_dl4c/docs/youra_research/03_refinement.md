# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent Controller Ablation)
- **Gap ID**: gap1
- **Gap Title**: Comparative Effectiveness of Alignment Techniques for Code Generation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All criteria met at Exchange 7 after paradigm shift from multi-modal training to feedback orthogonality mapping. Specific claim articulated, mechanism explained, predictions with numeric thresholds, novelty verified, feasibility established, objections addressed.

### Key Insights
1. **Paradigm Shift (Exchange 7)**: Reframed from "which feedback type wins" to "where does each feedback type provide unique signal"
2. **Simplification**: Shifted from expensive RL training experiment to feasible correlation study (300 samples vs thousands)
3. **Robust to Outcomes**: Either task-dependent orthogonality OR execution-dominance is publishable and actionable

### Breakthrough Moments
- **Exchange 5**: Dr. Ally synthesized tri-modal architecture with adaptive weighting
- **Exchange 6**: Prof. Rex identified RLAIF validity risk, required real human feedback
- **Exchange 7**: Dr. Nova reframed correlation study as primary contribution (feedback orthogonality atlas)

---

## Final Hypothesis

### Title
Task-Dependent Feedback Orthogonality in Code Generation Alignment

### Core Claim
Under code generation tasks with varying specification completeness (competitive programming, basic problems, realistic software tasks), if we measure pairwise correlations between execution-based feedback, AI reward model feedback, and human rating feedback on the same generated code samples, then execution-human correlation will vary systematically by task type (>0.8 for competitive, 0.6-0.8 for basic, <0.5 for realistic) while AI-human correlation remains stable (0.5-0.7 across all types), because execution feedback measures runtime behavior that only proxies human intent when specifications are fully test-capturable, while AI feedback measures learned patterns that partially overlap with intent regardless of specification completeness.

### Mechanism
Feedback signals operate through different measurement constructs:
- **Execution**: Measures runtime behavior (functional correctness)
- **AI**: Measures pattern likelihood under learned reward model
- **Human**: Measures intent alignment (does code match unstated requirements?)

**Key Insight**: When task specifications are fully captured by tests (competitive programming), execution feedback becomes a near-perfect proxy for human judgment. When specifications are underspecified (realistic software tasks), execution feedback misses critical intent dimensions that only human feedback captures.

**Causal Chain**:
1. Task specification completeness varies by dataset (HumanEval = complete, SWE-bench = underspecified)
2. Execution-human correlation depends on specification completeness (high when tests capture intent, low when tests miss intent)
3. AI-human correlation is stable because AI learns surface patterns independent of test completeness

---

## Predictions

### P1: Task-Dependent Execution-Human Correlation (PRIMARY)
**Statement**: Execution-human feedback correlation varies by task type
- **Competitive (HumanEval)**: >0.8
- **Basic (MBPP)**: 0.6-0.8
- **Realistic (SWE-bench)**: <0.5

**Test Method**: Generate 100 code samples per dataset with frozen Codex/CodeGen, collect execution feedback (test pass/fail), human ratings (5-point), compute Pearson correlations per dataset

**Success Criterion**: Correlation structure follows predicted pattern with between-task variance ≥2× within-task variance

**Falsification**: If all three correlations fall within ±0.1 of each other, task-dependent structure doesn't exist

### P2: Stable AI-Human Correlation
**Statement**: AI-human correlation remains 0.5-0.7 across all task types

**Test Method**: Same experiment as P1, measure AI reward model score vs human rating

**Success Criterion**: AI-human variance across tasks <0.1 (stable)

**Falsification**: If AI-human varies by >0.3, AI feedback is task-dependent like execution

### P3: Human Feedback Quality Validation
**Statement**: Inter-rater reliability exceeds Cohen's kappa >0.6

**Test Method**: 3-5 raters score each sample, compute pairwise kappa

**Success Criterion**: Mean kappa >0.6

**Falsification**: If kappa <0.6, human ratings unreliable

---

## Novelty

**Key Innovation**: First systematic mapping of feedback orthogonality space (pairwise correlations between execution/AI/human feedback) segmented by task type for code generation

**What's New vs Prior Work**:
- **CodeRL (2022)**: Used execution-only feedback, no modality comparison
- **RLAIF (2023)**: Compared AI vs human for text, not code-specific, no execution feedback
- **HumanEval+ (2023)**: Revealed hidden test gap, didn't measure feedback correlations

**Contribution**: Empirical orthogonality atlas showing where each feedback type provides unique signal → guides practitioners on when to use multi-modal vs single-modal alignment

---

## Experimental Design

### Datasets
- **HumanEval** (n=100): Competitive programming (complete test specs)
- **MBPP** (n=100): Basic problems (intermediate specs)
- **SWE-bench** (n=100): Realistic GitHub issues (underspecified)

### Base Model
- Frozen Codex (code-davinci-002) or CodeGen (16B-mono)
- Greedy decoding (eliminates sampling variance)

### Feedback Collection
1. **Execution**: Run test suites, record binary pass/fail
2. **AI**: Score with CodeT5/CodeBERT reward model (continuous score)
3. **Human**: 3-5 expert raters, 5-point scale (1=broken, 5=perfect)

### Analysis
- Compute Pearson correlations (execution-human, AI-human) per dataset
- Test null hypothesis (uniform correlations) via one-way ANOVA (α=0.05)
- Bootstrap resampling (1000 iterations) for 95% confidence intervals
- Inter-rater reliability (Cohen's kappa) to validate human feedback

### Baselines
- **Null Hypothesis**: All correlations within ±0.1 (no task-dependent structure)
- **Execution-Dominance**: Execution-human >0.9 across all tasks (execution suffices)

---

## Limitations

### Scope Constraints
- **Python-only**: Generalization to other languages (Java, C++) needs validation
- **Function/module-level**: Project-level code generation beyond scope
- **Offline evaluation**: Real-time interactive coding not tested
- **Correlation ≠ causation**: Doesn't prove adaptive weighting improves model performance (follow-on work)

### Known Risks
1. **Sample size**: 100/dataset may miss rare subtypes (mitigated by bootstrap sensitivity)
2. **Rater quality**: Human feedback depends on expertise (mitigated by inter-rater reliability check)
3. **Execution-dominance**: If execution >0.9 everywhere, hypothesis refuted (but still publishable outcome)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Paradigm shift at Exchange 7: correlation study reframed as primary contribution |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed via bootstrap + inter-rater reliability) |

---

## Phase 2B Readiness

**Status**: READY

**What Must Exist (SH1)**:
- Execution feedback requires runnable tests (✓ HumanEval/MBPP/SWE-bench provide)
- AI feedback requires reward model (✓ CodeT5/CodeBERT publicly available)
- Human feedback requires expert raters (✓ 3-5 raters, 300 samples, ~30 hours feasible)

**Core Mechanism to Test (SH2)**:
- Specification completeness determines execution-human correlation
- Test: Measure correlations on HumanEval (complete) vs SWE-bench (underspecified)
- Success: HumanEval >0.8, SWE-bench <0.5

**What to Compare (SH3)**:
- Primary: Execution-human correlation across task types
- Secondary: AI-human stability vs execution-human variability
- Success: Between-task variance ≥2× within-task variance

**Open Questions for Follow-On Work**:
1. What specific intent dimensions does execution miss on realistic tasks? (Qualitative failure analysis)
2. Does correlation structure generalize to Java, C++?
3. Can we pre-train a feedback router to predict which signal to trust?
4. Does feedback diversity improve sample efficiency?

---

*Hypothesis ID: H-FeedbackOrthogonality-v1*  
*Confidence Level: 0.80*  
*Phase: 2A - Dialogue & Refinement Complete*  
*Ready for: Phase 2B - Research Planning*
