# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-24T07:15:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent Controller Ablation)
- **Gap ID**: Gap-1
- **Gap Title**: Unified Benchmark-Interpretability Integration Framework
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 13

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 13

**Convergence Reason**: All convergence criteria met - clear mechanism (attention entropy distinguishes failure types), testable predictions (H1 pattern detection + H2 correction validation + P3 specificity), novelty established (first automated routing framework), feasibility confirmed (existing tools only + pre-experiment validation), major objections addressed (scope narrowing, multi-model testing, assumption mitigations)

### Key Insights

1. **Feasibility-driven design**: No-human-evaluation constraint drove pivot from diagnostic usefulness ratings (Exchange 5) to automated correction success validation (Exchange 7)
2. **Scope narrowing for testability**: Broadened vision (multi-failure-type routing) narrowed to proof-of-concept (entity-errors only) to enable clean falsifiable test
3. **Two-hypothesis validation**: Separated statistical pattern detection (H1 attention entropy) from causal diagnostic utility (H2 correction improvement) per Prof. Vera's design
4. **Proactive assumption handling**: Pre-experiment validation (NER accuracy, Wikipedia coverage, pilot threshold-grounding) addresses measurement risks before main experiment

### Breakthrough Moments

- **Exchange 7 (Dr. Nova)**: Automated correction success replaces human ratings, satisfying feasibility constraints while proving diagnostic utility
- **Exchange 8 (Prof. Vera)**: Two-hypothesis design (H1 statistical + H2 causal) separates mechanism from utility, both falsifiable
- **Exchange 13 (Dr. Nova)**: All adversarial critiques integrated into coherent experimental protocol with pre-validation phase

---

## Final Hypothesis

### Title
Failure-Type Routing Framework for Automated LLM Diagnosis and Correction

### Hypothesis ID
H-FailureRouting-v1

### Core Claim

Under TruthfulQA single-entity factual questions with gold-labeled model failures, if we classify failures as entity-error vs non-entity-error using attention pattern analysis, then automated failure-type routing to matched correction methods (entity-error → RAG retrieval, reasoning-error → chain-of-thought) will achieve higher correction success rates than mismatched routing, because entity-substitution failures concentrate attention on incorrect entities (low entropy) while non-entity failures distribute attention broadly (high entropy), enabling pattern-based diagnosis that targets root causes.

### Mechanism (3-step Causal Chain)

1. **Pattern Emergence**: Entity-substitution errors concentrate attention on incorrect entity tokens (low entropy), while non-entity errors (reasoning failures, knowledge gaps) distribute attention broadly across context (high entropy). This pattern emerges from transformer attention behavior.

2. **Diagnostic Routing**: Attention entropy over NER-identified entity spans serves as classification signal. Low entropy → entity-error diagnosis → trigger RAG correction. High entropy → non-entity-error diagnosis → trigger COT correction.

3. **Correction Effectiveness**: Matched correction (entity-error → RAG retrieval targets entity-knowledge gap) succeeds more frequently than mismatched correction (entity-error → COT targets reasoning chain) because diagnosis guides targeting of root cause.

---

## Predictions

### P1 (Primary - Pattern Detection)
**Statement**: Entity-substitution errors exhibit significantly lower attention entropy over NER-identified entity spans compared to non-entity errors.

**Test Method**: Welch's two-sample t-test on attention entropy distributions (N=100 failures per model: 50 entity-error, 50 non-entity-error, gold-labeled)

**Success Criterion**: p < 0.05 with entity-error group mean entropy < non-entity-error group mean entropy, replicated across both GPT-3.5 and Llama-2-7B

**Falsification**: p ≥ 0.05 OR opposite direction (entity-error entropy ≥ non-entity-error entropy) in either model

### P2 (Causal - Correction Validation)
**Statement**: Matched correction (entity-error → RAG) achieves higher success rate than mismatched correction (entity-error → COT) by ≥20 percentage points OR ≥50% relative improvement

**Test Method**: Compare correction success rates on 50 gold-labeled entity-errors per model using TruthfulQA automatic scoring

**Success Criterion**: RAG success rate - COT success rate ≥ 20 points OR (RAG - COT)/COT ≥ 0.50, whichever is more conservative, replicated across both models

**Falsification**: Difference < 20 points AND relative improvement < 50% in either model, OR opposite direction (COT > RAG)

### P3 (Specificity Check)
**Statement**: Entity-error vs non-entity-error entropy difference is specific to failures, not general model behavior

**Test Method**: Compare non-entity-error entropy to successful TruthfulQA responses (no failure) - expect no significant difference

**Success Criterion**: p > 0.05 on Welch's t-test comparing non-entity-error entropy vs success-case entropy

**Falsification**: p < 0.05 - would indicate entropy differences reflect general question properties, not failure-specific patterns

---

## Novelty

**Key Innovation**: Systematic integration of existing tools (benchmarks + interpretability + correction methods) into automated closed-loop diagnostic workflow

**Differentiation from Prior Work**:

1. **vs Benchmark Evaluation**: TruthfulQA produces aggregate accuracy scores (e.g., "65% correct"). This work routes individual failures to interpretability analysis, producing diagnostic failure profiles ("42% entity errors with wrong-entity attention, 23% reasoning errors with broken attention chains").

2. **vs Interpretability Research**: Attention visualization requires manual example selection, analyzing 10-20 failures per study. Automated routing enables failure-mode discovery at scale (100s of examples).

3. **vs Uniform Correction**: RAG and COT applied uniformly to all failures. Matched correction based on attention pattern signatures targets root causes (entity-knowledge gaps vs reasoning chain failures).

**First Demonstration**: Automated routing from benchmark failures to interpretability-based diagnosis with causal correction validation.

---

## Experimental Design

### Dataset
**TruthfulQA** single-entity factual questions subset (e.g., "What is the capital of France?")
- Rationale: Measures factuality and truthfulness, ideal for entity-substitution error testing
- Subset restriction: Single-entity questions provide unambiguous failure categorization, avoiding hybrid-failure confounds

### Models
- **GPT-3.5** (commercial, OpenAI API with attention weight access)
- **Llama-2-7B** (open-source, Hugging Face Transformers)
- Rationale: Multi-architecture robustness check, both provide attention weight extraction

### Baselines
1. **Random Routing**: Assign entity-errors to RAG or COT randomly (50/50) - measures improvement over chance
2. **Aggregate Correction**: Apply single method (RAG or COT) to all failures regardless of type - tests value of routing

### Pre-Experiment Validation (Phase 0)
1. **NER Accuracy Check**: Verify spaCy entity identification ≥90% on 100-sample test set. Fallback: manual entity annotation if threshold not met.
2. **Wikipedia Coverage Check**: Verify Wikipedia contains correct answers for ≥90% of entity-error test cases. Fallback: supplement with Wikidata.
3. **Pilot Experiment**: N=20 (10 entity-errors, 10 non-entity-errors) to establish baseline correction rates and ground P2 threshold adaptively.

### Variables
- **Independent Variable 1**: Failure Type (entity-error vs non-entity-error, gold-labeled)
- **Independent Variable 2**: Correction Method (RAG vs COT)
- **Dependent Variable 1**: Attention Entropy over NER-identified entity spans (Shannon entropy)
- **Dependent Variable 2**: Correction Success Rate (TruthfulQA automatic scoring, 0-100%)
- **Controlled**: LLM architecture (GPT-3.5, Llama-2), benchmark subset (single-entity factual), NER tool (spaCy), retrieval corpus (Wikipedia)

---

## Limitations

### Explicit Scope Boundaries

**Applies to**:
- Entity-substitution errors in single-entity factual questions
- TruthfulQA benchmark
- Transformer-based LLMs with accessible attention weights
- Factual knowledge domains covered by Wikipedia

**Does NOT apply to**:
- Reasoning errors, knowledge gaps, hybrid failure types (out of scope for proof-of-concept)
- Multi-entity or compositional questions
- Other benchmarks (FEVER, adversarial datasets) - generalization unknown
- LLMs without accessible attention (API-only models like GPT-4)

### Known Limitations

1. **Proof-of-concept scope**: One failure type (entity-substitution), one benchmark (TruthfulQA)
2. **Manual gold labels**: N=100 per model required - automated labeling is future work
3. **Single-entity subset restriction**: Excludes multi-entity and compositional questions
4. **Two-architecture validation**: GPT-3.5 and Llama-2-7B tested - broader generalization unknown
5. **Retrieval corpus dependency**: Correction success depends on Wikipedia coverage (≥90% verified)

---

## Key Assumptions

1. **A1 (NER Accuracy)**: spaCy accurately identifies entity spans in TruthfulQA single-entity questions (≥90% threshold verified pre-experiment)
2. **A2 (Wikipedia Coverage)**: Wikipedia contains correct factual knowledge for entity-error test cases (≥90% threshold verified)
3. **A3 (Binary Categorization)**: Entity-substitution errors and non-entity errors are categorically distinct in single-entity factual questions (mitigated by subset restriction to unambiguous cases)
4. **A4 (Architectural Generalization)**: Attention patterns generalize across GPT-3.5 and Llama-2-7B (multi-model testing addresses this)
5. **A5 (Statistical Power)**: N=100 per model provides sufficient power for two-sample t-tests with medium effect sizes

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 13 exchanges, all 6 personas participated, all convergence criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (scope limitations explicitly acknowledged) |

### Convergence Criteria Met

- ✅ **SPECIFIC**: Clear core claim (attention routing improves correction for entity-errors)
- ✅ **MECHANISM**: 3-step causal chain (pattern emergence → routing → correction effectiveness)
- ✅ **PREDICTIONS**: 3 falsifiable predictions (P1 statistical, P2 causal, P3 specificity)
- ✅ **NOVELTY**: First automated benchmark-interpretability routing framework
- ✅ **FEASIBILITY**: Existing tools only (TruthfulQA, NER, attention extraction, RAG, COT) + pre-validation
- ✅ **OBJECTIONS**: All major concerns addressed (feasibility constraints, scope narrowing, multi-model, assumptions)

---

## Phase 2B Readiness

**Status**: READY

**What must exist (SH-1)**: Attention pattern signatures that distinguish entity-substitution errors from non-entity errors (P1 validates)

**Core mechanism to test (SH-2)**: Attention entropy over entity spans enables failure-type classification and matched correction routing

**What to compare (SH-3)**: Matched correction vs random routing and aggregate correction baselines (deferred to Phase 5 baseline comparison)

**Open Questions for Future Work**:
1. Do reasoning errors and knowledge gaps have distinct attention signatures? (Generalization beyond entity-errors)
2. Can automated failure classification replace manual gold labels? (Scalability)
3. Do patterns generalize to FEVER, adversarial datasets? (Multi-benchmark validation)
4. What is optimal P2 threshold? (Pilot experiment N=20 will ground this)

---

*Discussion converged after 13 exchanges with all 6 research personas contributing to hypothesis refinement.*
