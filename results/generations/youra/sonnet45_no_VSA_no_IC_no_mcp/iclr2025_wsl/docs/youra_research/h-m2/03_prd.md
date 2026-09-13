# Product Requirements Document: Constraint-Satisfiability Verifier (h-m2)

## Project Overview

Build a rule-based constraint-satisfiability verifier that evaluates whether a hypothesis can be tested against a knowledge base of Device-Behavior-Measurement triples. The verifier must distinguish testable hypotheses (those with measurable interventions in the KB) from untestable ones with <25% false positive rate.

This is a formal verification component, not an ML system. Success demonstrates that symbolic ∃(D,B,M) lookup logic can reliably gate hypothesis testing without hallucinating testability.

## Goals & Success Criteria

**Primary Goal:** Achieve False Positive Rate (FPR) < 25% on expert-labeled test set.

**Success Criteria:**
- FPR < 25% (MUST_WORK gate threshold)
- True Negative Rate ≥ 75% (correctly reject untestable hypotheses)
- Precision ≥ 50% when marking testable
- Beat random baseline (50% FPR)
- Zero crashes on malformed hypothesis input

**Non-Goals:**
- Training or learning (rule-based only)
- Optimization of True Positive Rate (future work)
- Natural language understanding beyond entity extraction

## Core Requirements

### Functional Requirements

**FR1: Knowledge Base Integration**
- Load h-m1 KB from `h-m1/kb.json` (42 D,B,M triples)
- Parse structure: `[{"device": str, "behavior": str, "measurement": str}, ...]`
- Validate KB schema on load

**FR2: Hypothesis Parsing**
- Accept hypothesis text as input
- Extract intervention entity (device/behavior mentioned in hypothesis)
- Handle extraction failures gracefully (return "untestable" + reason)

**FR3: Constraint Verification**
- Check if extracted intervention matches any device in KB
- Check if corresponding behavior has associated measurement
- Return binary decision: testable (∃ match) or untestable (∄ match)

**FR4: Evaluation Harness**
- Load test set of 20 labeled hypotheses (10 testable, 10 untestable)
- Run verifier on each hypothesis
- Compute FPR: (false positives) / (true untestable count)
- Compute confusion matrix: TP, TN, FP, FN
- Report precision, recall, TNR, FPR

**FR5: Test Data Format**
- Test set schema: `[{"text": str, "label": "testable"|"untestable"}, ...]`
- Labels provided by domain expert (ground truth)
- Stored at `h-m2/test_hypotheses.json`

### Non-Functional Requirements

**NFR1: Determinism**
- Same hypothesis always produces same result
- No randomness in verification logic

**NFR2: Explainability**
- Log extracted intervention for each hypothesis
- Log KB lookup result (matched triple or null)
- Output reason for "untestable" verdict

**NFR3: Performance**
- Verification ≤ 100ms per hypothesis (negligible overhead)
- Full test set evaluation ≤ 5 seconds

**NFR4: Robustness**
- Handle empty hypothesis text
- Handle KB missing or malformed
- Handle extraction returning null/empty

## Technical Constraints

**TC1: No Machine Learning**
- Pure symbolic/rule-based system
- No training phase, no model weights
- No statistical learning from test set

**TC2: Reuse h-m1 Artifacts**
- Must use exact KB from h-m1/kb.json (42 triples)
- Cannot modify KB or add entries
- KB assumed correct (validated in h-m1)

**TC3: Entity Extraction**
- Use exact string matching or simple regex
- Match device names case-insensitive
- No embedding-based similarity

**TC4: Verification Logic**
- Implement ∃(D,B,M) check: "exists a triple where device D in KB matches intervention"
- Single-pass lookup (no iterative refinement)
- Return False if extraction fails (conservative)

**TC5: Language**
- Python 3.8+
- Stdlib only for core logic (json, re, pathlib)
- Optional: pytest for test harness

## Dependencies

**Upstream:**
- h-m1 KB (42 triples at h-m1/kb.json) - VALIDATED
- Test set of 20 expert-labeled hypotheses (deliverable of this phase)

**Downstream:**
- None (h-m2 is leaf node in phase graph)

**External:**
- None (no API calls, no external services)

## Out of Scope

**Deferred to Future Work:**
- Optimizing True Positive Rate (current focus: minimize FP)
- Multi-step reasoning (e.g., transitive measurement chains)
- Fuzzy matching or semantic similarity
- Interactive clarification of ambiguous hypotheses
- Auto-generation of test hypotheses (expert labels required)

**Explicitly Not Included:**
- Training data collection
- Model fine-tuning
- Web search for missing measurements
- KB expansion during verification

## Acceptance Criteria

The system passes acceptance when:
1. Evaluation script runs on 20-hypothesis test set without error
2. Outputs confusion matrix with FPR < 25%
3. Outputs per-hypothesis log showing extraction + verification trace
4. Reproduces same metrics on re-run (deterministic)
5. Code includes runnable `assert`-based self-check or minimal test
