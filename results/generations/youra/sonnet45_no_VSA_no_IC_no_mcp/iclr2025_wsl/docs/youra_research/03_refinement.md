# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25T07:30:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: Gap 2
- **Gap Title**: Automated Evaluation Methodology Taxonomy Gap
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met: (1) Specific claim stated, (2) Mechanism formalized, (3) Three testable predictions with thresholds, (4) Novelty articulated (post-hoc validation), (5) Feasibility confirmed (technically sound), (6) Objections addressed (catalog completeness, confound precision, validation cost)

### Key Insights

1. **Constraint Became the Innovation**: What started as "catalog of automated metrics" evolved into a formal testability verification system. The initial constraint (existing datasets/benchmarks only) transformed into the core research contribution. (Dr. Nova Exchange 1, 7)

2. **Post-Hoc Validation Breaks Circular Expert Bias**: Prof. Rex (Exchange 6) identified that expert agreement on testability is circular—experts may share biases. Actual experimental outcomes (p < 0.05 results) provide objective ground truth for whether a hypothesis is truly testable.

3. **Extensibility Makes System Future-Proof**: A static catalog becomes obsolete the day after publication. The 10-minute KB update test ensures non-experts can add new datasets/benchmarks, making the system self-improving. (Prof. Rex Exchange 6, Dr. Nova Exchange 7)

4. **Cross-Domain Confound Transfer is Reusable Infrastructure**: Confound patterns from NLP (e.g., tokenizer choice confounded with model size) can predict similar confounds in vision (image resolution confounded with architecture depth). This creates a reusable confound database across DL subfields. (Dr. Nova Exchange 7)

### Breakthrough Moments

- **Exchange 4**: Prof. Pax formalized constraint-satisfiability mathematically: ∃ (Dataset D, Benchmark B, Metric M) such that M(H_intervention) - M(H_baseline) is measurable. This provided the technical soundness anchor.

- **Exchange 5**: Dr. Ally synthesized scattered angles (reverse engineering, cross-domain transfer, constraint-satisfiability) into a coherent hypothesis with measurable predictions and explicit success criteria.

- **Exchange 6**: Prof. Rex challenged expert judgment as circular and proposed post-hoc experimental validation, forcing a paradigm shift in how the hypothesis validates itself.

- **Exchange 7**: Dr. Nova synthesized all feedback into a refined hypothesis with 3 falsifiable predictions, explicit failure thresholds, and a mitigation strategy for every concern raised.

---

## Final Hypothesis

### Title
Constraint-Satisfiability Verification for Deep Learning Hypothesis Testability

### Hypothesis ID
H-ConstraintSatChecker-v1

### Core Claim

Under constraint-driven deep learning research contexts (existing datasets/benchmarks only, no human evaluation), if a formal constraint-satisfiability verification system with an extensible knowledge base is used, then researchers can accurately classify hypotheses as testable/not-testable (>75% accuracy against experimental outcomes), because the system performs formal verification of (Dataset, Benchmark, Metric) triple existence and flags known confound patterns.

**Under-If-Then-Because Structure:**
- **Under**: Constraint-driven DL research (existing resources only, no human eval)
- **If**: Formal constraint-satisfiability verification system with extensible KB is used
- **Then**: Hypotheses classified as testable/not-testable with >75% accuracy (validated against experimental outcomes)
- **Because**: System verifies ∃ (D,B,M) triple where M is computable without human input + flags known confounds

### Mechanism

The hypothesis operates through a 4-step causal chain:

1. **KB Construction**: Extract (Dataset D, Benchmark B, Metric M) triples from Papers With Code and similar catalogs. Store metadata on compatibility and known confounds.

2. **Formal Verification**: Given hypothesis H, check ∃ (D,B,M) ∈ KB such that H can be expressed as an intervention testable by that triple: M(H_intervention) - M(H_baseline) is measurable without human input.

3. **Confound Pattern Detection**: Flag hypotheses where known confounds (correlation-not-causation patterns from prior literature) exist in the proposed (D,B,M) mapping. Prevents "technically correct but pragmatically useless" classifications.

4. **Post-Hoc Experimental Validation**: Sample of system-classified "testable" hypotheses are actually tested. If they yield p < 0.05 results, they were truly testable (ground truth). This validates system accuracy against objective reality, not circular expert opinion.

---

## Predictions

### P1 (Primary): Testability Classification Accuracy
**Statement**: The constraint-satisfiability checker achieves >75% accuracy in testability classification when validated against actual experimental outcomes (20 randomly sampled hypotheses tested for p < 0.05 results).

**Test Method**: Collect 100 DL hypotheses from recent papers (50 expert-labeled "testable," 50 "not testable"). System classifies all 100. Randomly sample 20 hypotheses and actually run experiments. Measure: (# correct classifications) / 20.

**Success Criterion**: Accuracy > 75% (vs random baseline 50%, vs expert judgment ~80-85%)

**Falsification**: If accuracy < 65%, system does not outperform chance meaningfully; hypothesis is disproven.

### P2: KB Update Usability
**Statement**: 80% of non-expert users can successfully add a new (D,B,M) triple to the knowledge base in under 10 minutes using the standardized format.

**Test Method**: Recruit 10 non-expert users (graduate students with basic DL knowledge). Provide YAML/JSON schema + examples. Task: add a new dataset-benchmark-metric triple. Measure: time to completion + correctness.

**Success Criterion**: ≥8 out of 10 users complete task correctly in <10 minutes.

**Falsification**: If <6 out of 10 succeed, the format is not usable by non-experts; extensibility fails.

### P3: Confound Flagging Precision
**Statement**: Confound flagging achieves >60% precision on a labeled set of known-confounded hypotheses.

**Test Method**: Curate labeled set of 30 hypotheses: 15 known-confounded (from literature where confounds were later discovered), 15 unconfounded. System flags confounds. Measure: precision = (true positives) / (true positives + false positives).

**Success Criterion**: Precision > 60% (vs random flagging ~30-40%)

**Falsification**: If precision < 40%, confound flagging adds more noise than signal; feature should be removed.

---

## Novelty

### What's New

**Three-fold innovation:**

1. **Post-Hoc Experimental Validation**: Validates system predictions by running actual experiments (p < 0.05 results = ground truth). No prior work in meta-research tools uses this standard; most rely on expert agreement, which Prof. Rex (Exchange 6) identified as circular. This is a methodological innovation in how we evaluate research tools.

2. **Extensible Knowledge Base**: Users can add new (D,B,M) triples in <10 minutes, making the system self-improving as new datasets emerge. Static catalogs become obsolete; this design grows with the field.

3. **Cross-Domain Confound Pattern Detection**: Confounds from NLP (e.g., tokenizer-size correlation) transfer to vision (resolution-architecture correlation). Dr. Nova (Exchange 7) identified this as reusable research infrastructure that benefits all DL subfields.

### How It Differs from Prior Work

- **vs. Papers With Code catalog**: Static listing vs. formal verification system with testability classification
- **vs. Expert-based research proposal reviews**: Circular expert agreement vs. post-hoc experimental ground truth validation
- **vs. Meta-analysis and survey papers**: Retrospective synthesis vs. prospective testability prediction before experiments are run

---

## Experimental Design

### Dataset
- **Name**: Papers With Code Catalog (Jan 2026 snapshot)
- **Type**: Standard benchmark catalog
- **Source**: https://paperswithcode.com/
- **Why This Dataset**: Provides comprehensive inventory of existing datasets and benchmarks, which is the core resource the hypothesis claims to leverage

### Model
- **Name**: Formal Constraint-Satisfiability Verifier (rule-based system)
- **Type**: Symbolic reasoning system (not ML model)
- **Implementation**: Custom rule system that checks (D,B,M) existence
- **Why This Model**: Hypothesis proposes formal verification approach, not a learned model

### Baselines
1. **Random Classification**: Randomly assign 50% "testable" and 50% "not testable" to the 100 hypotheses (50% accuracy expected)
2. **Expert Judgment**: 3 independent DL researchers manually classify hypotheses; majority vote determines label (~80-85% inter-rater reliability)

### Variables
- **Independent Variable**: Classification Method (constraint-sat-checker vs random vs expert-judgment)
- **Dependent Variable (Primary)**: Testability Classification Accuracy (% correct when validated against experimental p < 0.05 outcomes)
- **Controlled Variables**: Hypothesis source (DL papers 2024-2026), KB snapshot date (Jan 2026), expert labeling protocol (3 independent experts)

---

## Limitations

### Known Limitations

1. **KB Completeness Depends on Catalog Coverage**: Papers With Code catalog is biased toward popular benchmarks. Obscure datasets may be missed, leading to false negatives (testable hypotheses classified as untestable).

2. **Confound Flagging Limited to Documented Patterns**: The confound database can only flag confounds that have been documented in prior literature. Novel confounds won't be detected.

3. **Post-Hoc Validation is Resource-Intensive**: Running 20 actual experiments for validation requires significant resources. Full validation of all 100 classifications is impractical.

4. **System Provides Classification, Not Causal Interpretation**: Researchers still need domain expertise to understand why a hypothesis is testable/untestable and what confounds mean for their specific research question.

### Scope Boundaries

**Applies To**:
- Deep learning research in domains with established benchmarks (vision, NLP, generative models)
- Research contexts where human evaluation is prohibitively expensive
- Constraint-driven environments (academic labs, independent researchers)
- Hypotheses testable via automated metrics (accuracy, BLEU, FID, etc.)

**Does Not Apply To**:
- Exploratory research where defining testability upfront is premature
- Domains with no existing benchmark infrastructure (novel modalities)
- Hypotheses requiring subjective human judgment (aesthetic quality, ethics)
- Scenarios where creating new benchmarks is feasible and necessary

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met: specific, mechanism, predictions, novelty, feasibility, objections addressed |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

### Mitigation Strategy for Concerns

1. **Catalog Completeness** (Prof. Pax, Prof. Rex): Bounded scope to fixed Jan 2026 snapshot + extensibility mechanism (10-min KB updates) balances verifiability and future-proofing.

2. **Confound Taxonomy Depth** (Prof. Rex): Start with high-confidence patterns from literature (NLP tokenizer-size, vision resolution-architecture), iterate as more patterns are documented.

3. **Experimental Validation Cost** (Prof. Rex): Phase validation—initial 20 experiments on low-cost hypotheses (existing codebases), expand to 50-100 as resources allow.

4. **KB Update Format Usability** (Dr. Ally, Prof. Rex): Design YAML/JSON schema to be human-readable and machine-parseable, validate with 10 non-expert users.

---

**Phase 2A Status**: COMPLETE  
**Next Phase**: Phase 2B (Research Planning)  
**Outputs**: 03_refinement.yaml, 02_synthesis.yaml, final_opinions.yaml, discussion_log.md
