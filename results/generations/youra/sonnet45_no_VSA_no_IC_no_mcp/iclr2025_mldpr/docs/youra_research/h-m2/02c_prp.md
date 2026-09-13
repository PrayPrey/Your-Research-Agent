# Peer Review Protocol: h-m2

**Date:** 2026-08-24
**Hypothesis:** Context-aware successor graphs capture task-specific replacement paths via usage-pattern inference, providing more relevant recommendations than linear version-based succession with ≥ 70% context inference accuracy
**Phase:** 2C - Implementation Planning
**Author:** Phase 3 Planning Agent

---

## Review Scope

This protocol defines what Phase 4 Validator Agent checks during code validation.

---

## 1. Methodology Validation

### 1.1 Experimental Design Soundness

**Check:** Does experiment design match hypothesis requirements?

**Validation Criteria:**
- [ ] Baseline system (linear version-based succession) implemented
- [ ] Proposed system (context-aware successor graphs) implemented
- [ ] Comparison between baseline and proposed is fair (same validation dataset)
- [ ] Success criteria aligned with hypothesis (≥70% accuracy, <50% override)

**Auto-Verifiable:** YES (static analysis)
- Read `experiment.py`: Confirm both systems evaluated on same test set
- Read `baseline.py`: Confirm no context awareness
- Read `recommendation.py`: Confirm context-aware logic

**Expected Finding Format:**
```json
{
  "check": "Experimental design soundness",
  "status": "PASS" | "FAIL",
  "evidence": "Both systems evaluated on test set with 500+ samples",
  "issues": []
}
```

---

### 1.2 Dataset Validity

**Check:** Is validation dataset real/standard, not synthetic?

**Validation Criteria:**
- [ ] Validation dataset has ground-truth labels (not generated)
- [ ] Samples derived from real HuggingFace download patterns
- [ ] 70/30 train/test split implemented
- [ ] Sample size ≥500 examples

**Auto-Verifiable:** PARTIAL (static + runtime)
- Static: Read `data/validation_dataset.json` → check sample count
- Runtime: Check data loading doesn't use `np.random` or synthetic generation

**Expected Finding Format:**
```json
{
  "check": "Dataset validity",
  "status": "PASS" | "FAIL",
  "evidence": "validation_dataset.json contains 523 real samples with ground-truth labels",
  "issues": []
}
```

**Red Flags:**
- Dataset generated programmatically (not real-world)
- No ground-truth labels (cannot compute accuracy)
- Sample size <500 (insufficient for statistical test)

---

### 1.3 Metrics Alignment

**Check:** Do evaluation metrics match hypothesis DV?

**Validation Criteria:**
- [ ] Context inference accuracy computed via `sklearn.metrics.accuracy_score`
- [ ] User override rate computed from telemetry counts
- [ ] Edge precision computed from expert validation labels
- [ ] Statistical test (binomial test α=0.05) implemented

**Auto-Verifiable:** YES (static analysis)
- Read `evaluation.py`: Confirm metrics functions match specifications

**Expected Finding Format:**
```json
{
  "check": "Metrics alignment",
  "status": "PASS" | "FAIL",
  "evidence": "accuracy_score, override_rate, precision_score match experiment brief",
  "issues": []
}
```

---

## 2. Implementation Correctness

### 2.1 Context Inference Logic

**Check:** Does context inference follow architecture spec?

**Validation Criteria:**
- [ ] Pattern matching against task-specific library lists
- [ ] Returns (context, confidence) tuple
- [ ] Explicit fallback for "unknown" cases
- [ ] No hardcoded results (patterns must come from real import lists)

**Auto-Verifiable:** YES (static analysis)
- Read `context_inference.py`: Confirm logic matches architecture C1

**Expected Finding Format:**
```json
{
  "check": "Context inference correctness",
  "status": "PASS" | "FAIL",
  "evidence": "infer_context() matches architecture spec with fallback",
  "issues": []
}
```

**Red Flags:**
- Hardcoded context returns (not based on module analysis)
- No fallback for ambiguous cases
- Pattern dictionary empty or unrealistic

---

### 2.2 Graph Construction Logic

**Check:** Does graph construction parse real citations?

**Validation Criteria:**
- [ ] Parses dataset card descriptions (not hardcoded edges)
- [ ] Extracts task context from citation text
- [ ] Builds NetworkX DiGraph with context-labeled edges
- [ ] Handles missing citations gracefully

**Auto-Verifiable:** PARTIAL (static + runtime)
- Static: Read `graph_construction.py` → confirm citation parsing logic
- Runtime: Execute on sample dataset cards → verify edges generated

**Expected Finding Format:**
```json
{
  "check": "Graph construction correctness",
  "status": "PASS" | "FAIL",
  "evidence": "parse_citations() extracts edges from real dataset card text",
  "issues": []
}
```

**Red Flags:**
- Hardcoded successor edges (not parsed from cards)
- No error handling for missing citations
- Graph always empty

---

### 2.3 Recommendation Logic

**Check:** Does recommendation filter by context?

**Validation Criteria:**
- [ ] Filters graph edges by user context match
- [ ] Returns None when no match found
- [ ] Ranks by precision score
- [ ] Does NOT default to baseline when no match (must return None)

**Auto-Verifiable:** YES (static analysis)
- Read `recommendation.py`: Confirm context filtering logic

**Expected Finding Format:**
```json
{
  "check": "Recommendation correctness",
  "status": "PASS" | "FAIL",
  "evidence": "recommend() filters by context and returns None for no match",
  "issues": []
}
```

**Red Flags:**
- No context filtering (returns any successor)
- Defaults to baseline when no match (dilutes proposed system)
- Always returns hardcoded successor

---

## 3. Execution Validation

### 3.1 Code Runs Without Error

**Check:** Does experiment execute end-to-end?

**Validation Criteria:**
- [ ] All dependencies installed (networkx, requests, sklearn, matplotlib)
- [ ] Data loading succeeds (HF API, PwC API, validation dataset)
- [ ] Both systems (baseline + proposed) run to completion
- [ ] Metrics computation produces numeric results
- [ ] Figures save without error

**Auto-Verifiable:** YES (runtime execution)
- Execute `python experiment.py` → check exit code 0

**Expected Finding Format:**
```json
{
  "check": "Execution success",
  "status": "PASS" | "FAIL",
  "evidence": "experiment.py runs without error, produces metrics.json",
  "issues": []
}
```

---

### 3.2 PoC Pass Condition

**Check:** Does proposed system outperform baseline?

**Validation Criteria:**
- [ ] `proposed_accuracy > baseline_accuracy`
- [ ] Difference is non-trivial (≥5 percentage points)

**Auto-Verifiable:** YES (runtime result check)
- Read `results/metrics.json`: Compare proposed vs baseline accuracy

**Expected Finding Format:**
```json
{
  "check": "PoC pass condition",
  "status": "PASS" | "FAIL",
  "evidence": "proposed_accuracy=0.73 > baseline_accuracy=0.02",
  "issues": []
}
```

**Red Flags:**
- Proposed ≤ baseline (mechanism doesn't work)
- Proposed accuracy <70% (fails MUST_WORK gate)
- Override rate ≥50% (users reject inferred context)

---

## 4. Gate Metrics Validation

### 4.1 Context Inference Accuracy

**Check:** Does context accuracy meet ≥70% threshold?

**Validation Criteria:**
- [ ] Accuracy computed on 30% held-out test set
- [ ] Accuracy ≥70%
- [ ] Statistical test (binomial) p-value <0.05

**Auto-Verifiable:** YES (runtime result check)
- Read `results/metrics.json`: Check `context_accuracy >= 0.70`

**Expected Finding Format:**
```json
{
  "check": "Context accuracy gate",
  "status": "PASS" | "FAIL",
  "evidence": "context_accuracy=0.73 (≥70% threshold)",
  "issues": []
}
```

---

### 4.2 User Override Rate

**Check:** Does override rate meet <50% threshold?

**Validation Criteria:**
- [ ] Override rate computed from telemetry counts
- [ ] Override rate <50%

**Auto-Verifiable:** YES (runtime result check)
- Read `results/metrics.json`: Check `override_rate < 0.50`

**Expected Finding Format:**
```json
{
  "check": "Override rate gate",
  "status": "PASS" | "FAIL",
  "evidence": "override_rate=0.32 (<50% threshold)",
  "issues": []
}
```

---

### 4.3 Edge Precision

**Check:** Does edge precision meet ≥60% threshold?

**Validation Criteria:**
- [ ] Precision computed from expert validation labels
- [ ] Precision ≥60%

**Auto-Verifiable:** YES (runtime result check)
- Read `results/metrics.json`: Check `edge_precision >= 0.60`

**Expected Finding Format:**
```json
{
  "check": "Edge precision gate",
  "status": "PASS" | "FAIL",
  "evidence": "edge_precision=0.68 (≥60% threshold)",
  "issues": []
}
```

---

## 5. Reproducibility Validation

### 5.1 Seed Management

**Check:** Is random seed fixed for reproducibility?

**Validation Criteria:**
- [ ] Fixed seed for validation dataset split (train/test 70/30)
- [ ] Seed documented in code comments

**Auto-Verifiable:** YES (static analysis)
- Grep `experiment.py` for `random.seed()` or `np.random.seed()`

**Expected Finding Format:**
```json
{
  "check": "Seed management",
  "status": "PASS" | "FAIL",
  "evidence": "Fixed seed=42 for validation split",
  "issues": []
}
```

---

### 5.2 Dependency Versions

**Check:** Are dependency versions documented?

**Validation Criteria:**
- [ ] `requirements.txt` exists
- [ ] Lists: networkx, requests, scikit-learn, matplotlib

**Auto-Verifiable:** YES (file existence)
- Check `requirements.txt` presence

**Expected Finding Format:**
```json
{
  "check": "Dependency documentation",
  "status": "PASS" | "FAIL",
  "evidence": "requirements.txt lists all dependencies",
  "issues": []
}
```

---

## 6. Visualization Validation

### 6.1 Required Figures

**Check:** Are all 4 required figures generated?

**Validation Criteria:**
- [ ] Confusion matrix (context inference)
- [ ] Precision-recall curve (edge inference)
- [ ] Override rate bar chart
- [ ] Successor graph visualization
- [ ] All saved to `results/figures/`

**Auto-Verifiable:** YES (file existence)
- Check `results/figures/` for 4 PNG files

**Expected Finding Format:**
```json
{
  "check": "Visualization completeness",
  "status": "PASS" | "FAIL",
  "evidence": "4 figures generated in results/figures/",
  "issues": []
}
```

---

## Validation Workflow

**Phase 4 Validator Agent executes:**

1. **Static Analysis** (before runtime)
   - Check 1.1: Experimental design soundness
   - Check 1.3: Metrics alignment
   - Check 2.1: Context inference logic
   - Check 2.2: Graph construction logic (partial)
   - Check 2.3: Recommendation logic
   - Check 5.1: Seed management
   - Check 5.2: Dependency versions

2. **Runtime Execution**
   - Check 3.1: Code runs without error
   - Check 1.2: Dataset validity (partial)
   - Check 2.2: Graph construction logic (partial)

3. **Result Validation**
   - Check 3.2: PoC pass condition
   - Check 4.1: Context accuracy gate
   - Check 4.2: Override rate gate
   - Check 4.3: Edge precision gate
   - Check 6.1: Required figures

4. **Report Generation**
   - Aggregate findings → `04_validation.md`
   - Gate decision: PASS/FAIL based on checks 4.1 + 4.2

---

## Red Flags Summary

**Critical Issues (MUST_FAIL):**
- Synthetic validation dataset (not real-world)
- Hardcoded context inference (not pattern-based)
- Hardcoded graph edges (not citation-parsed)
- Proposed accuracy ≤ baseline (mechanism doesn't work)
- Context accuracy <70% (fails gate)
- Override rate ≥50% (fails gate)
- Code crashes (cannot validate)

**Non-Critical Issues (WARN):**
- Edge precision <60% (tertiary metric)
- Missing figures (can regenerate)
- Undocumented dependencies (can infer)

---

## Validation Report Template

**Phase 4 Validator outputs:**

```markdown
# Validation Report: h-m2

**Date:** 2026-08-24
**Validator:** Phase 4 Validator Agent

## Summary
- **Overall Status:** PASS/FAIL
- **Gate Decision:** PASS/FAIL (based on checks 4.1 + 4.2)
- **Critical Issues:** 0
- **Warnings:** 0

## Findings

### Methodology Validation
- [PASS/FAIL] Check 1.1: Experimental design soundness
- [PASS/FAIL] Check 1.2: Dataset validity
- [PASS/FAIL] Check 1.3: Metrics alignment

### Implementation Correctness
- [PASS/FAIL] Check 2.1: Context inference logic
- [PASS/FAIL] Check 2.2: Graph construction logic
- [PASS/FAIL] Check 2.3: Recommendation logic

### Execution Validation
- [PASS/FAIL] Check 3.1: Code runs without error
- [PASS/FAIL] Check 3.2: PoC pass condition

### Gate Metrics Validation
- [PASS/FAIL] Check 4.1: Context accuracy ≥70%
- [PASS/FAIL] Check 4.2: Override rate <50%
- [PASS/FAIL] Check 4.3: Edge precision ≥60%

### Reproducibility
- [PASS/FAIL] Check 5.1: Seed management
- [PASS/FAIL] Check 5.2: Dependency versions

### Visualization
- [PASS/FAIL] Check 6.1: Required figures

## Detailed Findings
[Per-check evidence and issues]

## Recommendations
[Suggestions for Phase 4 Coder if validation fails]
```

---

*PRP generated from 02c_experiment_brief.md + 02c_architecture.md*
*Ready for Phase 4 validation execution*
