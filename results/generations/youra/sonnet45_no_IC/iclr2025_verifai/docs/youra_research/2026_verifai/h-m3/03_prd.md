# Product Requirements Document: h-m3 Constraint Inference Validation

**Date:** 2026-07-14
**Author:** Anonymous
**Hypothesis:** h-m3 (Constraint Inference via Assumption-Evidence Matching)
**Type:** MECHANISM (Causal Step 3)
**Gate:** SHOULD_WORK (Recall ≥70% target, ≥60% acceptable, FP rate <30%)

---

## Executive Summary

### Purpose

Validate that semantic similarity-based assumption-evidence comparison can detect ≥70% of actual constraint mismatches (contradictions between early-phase assumptions and later-phase claims) with false positive rate <30%, using sentence transformer embeddings and cosine similarity threshold <0.3.

### Success Criteria

**Primary Gate (SHOULD_WORK):**
1. Mismatch detection recall ≥70% (target), ≥60% (acceptable)
2. False positive rate <30%
3. Known failures (h-e1, h-m1) correctly identified via assumption-evidence mismatches

**If Gate Fails:** Revise approach (not fatal) - may need hybrid LLM+semantic method or different threshold

### Context

- **Prerequisites:** h-m2 COMPLETED (Extraction: Precision 86.3%, Recall 82.7%, Kappa 71.6%)
- **Dataset:** Reuse h-m2 extracted assumptions and claims from 20 MCP traces
- **Continuation:** Builds on h-m2's validated extraction method
- **Critical Path:** h-m3 SHOULD_WORK gate (1.5 weeks, Risk R3: Terminological mismatch 25%)

---

## Problem Statement

### Core Challenge

Research pipeline validation requires detecting constraint violations where early-phase assumptions (from query parameters in Phase 1-3 tool calls) contradict later-phase evidence (from result content in Phase 4-6 tool calls). Example: "effective rank decreases" assumption vs "effective rank increased 6.02%" evidence.

**Current State:** h-m2 validated that LLM extraction achieves 86.3% precision, 82.7% recall for assumptions/claims.

**Required:** Prove that semantic similarity matching can detect ≥70% of assumption-evidence contradictions with <30% false positive rate.

### Why This Matters

- h-m4 (end-to-end validation) depends on reliable mismatch detection
- Without ≥70% recall, too many violations missed → pipeline failures undetected
- Without FP rate <30%, too many benign differences flagged → low precision
- SHOULD_WORK gate allows iteration but validates core mechanism

---

## Functional Requirements

### FR-1: Dataset Loading and Phase Pairing

**Priority:** P0 (SHOULD_WORK gate)

**Description:** Load h-m2 extracted assumptions and claims, pair by pipeline execution phase.

**Acceptance Criteria:**
- Load assumptions from early-phase tool calls (Phase 1-3 queries)
- Load claims from later-phase tool calls (Phase 4-6 results)
- Reuse h-m2 multi-vote extraction output (validated: 86.3% precision, 82.7% recall)
- Phase pairing: All-pairs comparison (each Phase 1-3 assumption vs all Phase 4-6 claims)
- Store pairs with metadata: (assumption_text, claim_text, phase_source, tool_call_id)

**Dependencies:** h-m2 extraction outputs (`h-m2/outputs/extracted_assumptions.json`, `h-m2/outputs/extracted_claims.json`)

**Implementation Notes:**
```python
# Load h-m2 extraction results
assumptions = load_json("h-m2/outputs/extracted_assumptions.json")
claims = load_json("h-m2/outputs/extracted_claims.json")

# Filter by phase
early_assumptions = [a for a in assumptions if a["phase"] in [1, 2, 3]]
later_claims = [c for c in claims if c["phase"] in [4, 5, 6]]

# Generate all pairs
pairs = [(a, c) for a in early_assumptions for c in later_claims]
```

---

### FR-2: Semantic Embedding System

**Priority:** P0 (SHOULD_WORK gate)

**Description:** Generate semantic embeddings for assumptions and claims using sentence transformers.

**Acceptance Criteria:**
- Use `sentence-transformers` library (UKPLab)
- Model: `all-MiniLM-L6-v2` (384-dim embeddings, fast inference)
- Batch encoding for efficiency (all assumptions → embeddings, all claims → embeddings)
- Output: PyTorch tensors compatible with cosine similarity computation
- No training required (pre-trained model, zero-training constraint)

**Dependencies:** `sentence-transformers` package, `torch` package

**Implementation Notes:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode assumptions
assumption_texts = [a["text"] for a in early_assumptions]
assumption_embeddings = model.encode(assumption_texts, convert_to_tensor=True)

# Encode claims
claim_texts = [c["text"] for c in later_claims]
claim_embeddings = model.encode(claim_texts, convert_to_tensor=True)
```

---

### FR-3: Pairwise Similarity Computation

**Priority:** P0 (SHOULD_WORK gate)

**Description:** Compute cosine similarity matrix for all assumption-claim pairs.

**Acceptance Criteria:**
- Compute pairwise cosine similarity using `sentence_transformers.util.cos_sim`
- Output matrix shape: (num_assumptions, num_claims)
- Similarity range: [-1, 1] (cosine similarity)
- Store similarities with pair metadata for analysis

**Dependencies:** FR-2 (embeddings)

**Implementation Notes:**
```python
from sentence_transformers import util

# Compute similarity matrix
similarity_matrix = util.cos_sim(assumption_embeddings, claim_embeddings)

# Extract (assumption_idx, claim_idx, similarity_score) tuples
similarities = []
for i in range(len(assumption_embeddings)):
    for j in range(len(claim_embeddings)):
        sim_score = similarity_matrix[i][j].item()
        similarities.append({
            "assumption": early_assumptions[i],
            "claim": later_claims[j],
            "similarity": sim_score
        })
```

---

### FR-4: Threshold-Based Contradiction Detection

**Priority:** P0 (SHOULD_WORK gate)

**Description:** Flag pairs with similarity <0.3 as potential contradictions.

**Acceptance Criteria:**
- Apply threshold: similarity < 0.3 → flag as mismatch
- Store flagged contradictions with similarity scores
- Include pair metadata (assumption/claim texts, phase sources, tool call IDs)
- Threshold value: 0.3 (from hypothesis statement)

**Dependencies:** FR-3 (similarity scores)

**Implementation Notes:**
```python
threshold = 0.3

contradictions = [
    pair for pair in similarities
    if pair["similarity"] < threshold
]

# Store flagged pairs
save_json("h-m3/outputs/detected_contradictions.json", contradictions)
```

---

### FR-5: Ground Truth Validation

**Priority:** P0 (SHOULD_WORK gate)

**Description:** Validate detected contradictions against known failure cases (h-e1, h-m1).

**Acceptance Criteria:**
- Ground truth: h-e1 and h-m1 failure annotations (from Phase 2B verification plan)
- h-m1 known mismatch: "effective rank decreases" assumption vs "effective rank increased 6.02%" claim
- Compute True Positives (detected known mismatches), False Positives (flagged benign pairs), False Negatives (missed known mismatches)
- Enable recall and FP rate computation

**Dependencies:** FR-4 (detected contradictions), Ground truth annotations

**Implementation Notes:**
```python
# Ground truth known mismatches
ground_truth = [
    {"assumption": "effective rank decreases", 
     "claim": "effective rank increased 6.02%",
     "source": "h-m1 failure"}
]

# Match detected contradictions to ground truth
true_positives = []
for gt in ground_truth:
    for detected in contradictions:
        if semantic_match(detected, gt):  # Fuzzy match
            true_positives.append(detected)

# Count false positives and false negatives
false_positives = [c for c in contradictions if c not in true_positives]
false_negatives = [gt for gt in ground_truth if not any(semantic_match(c, gt) for c in contradictions)]
```

---

### FR-6: Metrics Computation and Gate Check

**Priority:** P0 (SHOULD_WORK gate)

**Description:** Compute mismatch detection recall and false positive rate, check against gate thresholds.

**Acceptance Criteria:**
- Recall = TP / (TP + FN) where TP = detected known mismatches, FN = missed known mismatches
- False Positive Rate = FP / (FP + TN) where FP = flagged benign pairs, TN = unflagged benign pairs
- SHOULD_WORK gate: Recall ≥70% (target), ≥60% (acceptable), FP rate <30%
- Display gate pass/fail status
- Generate gate metrics comparison figure (required)

**Dependencies:** FR-5 (ground truth validation)

**Implementation Notes:**
```python
from sklearn.metrics import recall_score, confusion_matrix

# Compute metrics
tp = len(true_positives)
fn = len(false_negatives)
fp = len(false_positives)
tn = total_pairs - tp - fp - fn

recall = tp / (tp + fn) if (tp + fn) > 0 else 0
fp_rate = fp / (fp + tn) if (fp + tn) > 0 else 0

# Gate check
gate_passed = (recall >= 0.60 and fp_rate < 0.30)
target_met = (recall >= 0.70 and fp_rate < 0.30)

print(f"Mismatch Detection Recall: {recall:.3f} (target ≥0.70, acceptable ≥0.60)")
print(f"False Positive Rate: {fp_rate:.3f} (target <0.30)")
print(f"Gate Status: {'PASSED' if gate_passed else 'FAILED'}")
```

---

### FR-7: Threshold Tuning (Optional Exploration)

**Priority:** P1 (Nice to have)

**Description:** Explore alternative thresholds [0.2, 0.25, 0.3, 0.35, 0.4] to analyze recall-FP tradeoff.

**Acceptance Criteria:**
- Test 5 threshold values
- Compute recall and FP rate for each threshold
- Generate threshold tuning curve figure (recall vs FP rate)
- Report optimal threshold (maximizes recall while FP rate <30%)

**Dependencies:** FR-3 (similarity scores), FR-5 (ground truth)

**Implementation Notes:**
```python
thresholds = [0.2, 0.25, 0.3, 0.35, 0.4]
results = []

for threshold in thresholds:
    contradictions_t = [pair for pair in similarities if pair["similarity"] < threshold]
    recall_t, fp_rate_t = compute_metrics(contradictions_t, ground_truth)
    results.append({"threshold": threshold, "recall": recall_t, "fp_rate": fp_rate_t})

# Plot threshold tuning curve
plot_threshold_curve(results)
```

---

## Non-Functional Requirements

### NFR-1: Performance

- **Inference Speed:** <5 seconds for encoding 100 text samples (all-MiniLM-L6-v2)
- **Batch Processing:** Support batch encoding for efficiency
- **Memory:** <2GB GPU memory for embeddings (384-dim × 100 samples)

### NFR-2: Reproducibility

- **Deterministic Encoding:** sentence-transformers with fixed random seed
- **Versioning:** Log model version (`all-MiniLM-L6-v2` hash)
- **Traceable Pairs:** Store all (assumption, claim, similarity) tuples for manual inspection

### NFR-3: Usability

- **Output Format:** JSON with structured fields (assumption, claim, similarity, mismatch_flag)
- **Logging:** Log threshold, model version, dataset size, gate status
- **Error Handling:** Graceful handling of empty text samples or encoding failures

---

## Evaluation and Success Metrics

### Primary Metrics (Gate)

1. **Mismatch Detection Recall:** ≥70% (target), ≥60% (acceptable)
   - Formula: TP / (TP + FN)
   - Measures: Percentage of known contradictions detected

2. **False Positive Rate:** <30%
   - Formula: FP / (FP + TN)
   - Measures: Percentage of benign pairs incorrectly flagged

### Secondary Metrics

3. **h-e1 Detection:** Correctly identify h-e1 failure via assumption-evidence mismatch (if applicable)
4. **h-m1 Detection:** Correctly identify h-m1 failure via "effective rank" contradiction

### Baseline Comparison

- **Baseline:** Random pairwise matching (expected ~50% precision/recall)
- **Proposed:** Semantic similarity matching (target ≥70% recall, <30% FP rate)

---

## Visualization Requirements

### Required Figures (Mandatory)

**Figure 1: Gate Metrics Comparison**
- Type: Bar chart
- X-axis: Metrics (Recall, FP Rate)
- Y-axis: Values [0, 1]
- Bars: Target (green), Acceptable (yellow), Actual (blue)
- Threshold lines: 0.70 (target), 0.60 (acceptable for recall), 0.30 (FP rate limit)

### Additional Figures (Optional, LLM Autonomous)

**Figure 2: Similarity Distribution Histogram**
- X-axis: Cosine similarity scores [0, 1]
- Y-axis: Frequency
- Vertical line at threshold (0.3)
- Colors: Red (<0.3, contradictions), Green (≥0.3, matches)

**Figure 3: Confusion Matrix Heatmap**
- Rows: Actual (Mismatch, No Mismatch)
- Columns: Predicted (Flagged, Not Flagged)
- Cells: TP, FP, FN, TN counts

**Figure 4: Threshold Tuning Curve** (if FR-7 implemented)
- X-axis: Threshold values [0.2, 0.4]
- Y-axis: Recall (solid line) and FP Rate (dashed line)

**Figure 5: Per-Case Detection Results**
- Bar chart: h-e1 and h-m1 cases
- Show: Detected (Yes/No) with similarity scores

All figures saved to `h-m3/figures/` with matplotlib/seaborn.

---

## Dependencies and Constraints

### External Dependencies

- **Libraries:** `sentence-transformers`, `torch`, `sklearn`, `matplotlib`, `seaborn`
- **Pre-trained Model:** `all-MiniLM-L6-v2` (download via HuggingFace Hub)
- **h-m2 Outputs:** Extracted assumptions and claims JSON files

### Technical Constraints

- **Zero-Training:** Use pre-trained models only, no fine-tuning
- **Semantic Matching Only:** No LLM-based contradiction detection (stays within semantic similarity paradigm)
- **Threshold Fixed:** Use 0.3 from hypothesis statement (explore alternatives only in FR-7)

### Data Constraints

- **Dataset Size:** 20 MCP traces (596 tool calls, reuse h-m1/h-m2 dataset)
- **Ground Truth Size:** Limited to h-e1 and h-m1 known failures (small annotation set)
- **Phase Coverage:** Require both early-phase (1-3) and later-phase (4-6) tool calls

---

## Risk Mitigation

### Risk R3: Terminological Mismatch (Probability 25%, Severity MEDIUM)

**Impact:** Related concepts use different terminology → low similarity despite semantic relation → missed contradictions

**Mitigation M3:** Semantic embeddings + synonym expansion
- Use sentence-transformers (captures semantic similarity beyond exact word match)
- If recall <60%, explore synonym expansion or use all-mpnet-base-v2 (better quality, 768-dim)

**Residual Risk:** 10%

### Risk R4: Benign Constraint Violations (Probability 30%, Severity HIGH)

**Impact:** Flagging benign differences (e.g., "approximately 50%" vs "exactly 47.3%") as contradictions → high FP rate

**Mitigation M4:** Violation severity ranking + filtering
- Threshold tuning (FR-7) to balance recall vs FP rate
- Post-hoc filtering: Remove low-severity pairs (numeric differences within tolerance)

**Residual Risk:** 15%

---

## Implementation Phases

### Phase 1: Data Loading and Embedding (Week 1, Days 1-2)

- FR-1: Load h-m2 outputs
- FR-2: Generate embeddings

### Phase 2: Similarity and Detection (Week 1, Days 3-4)

- FR-3: Compute similarity matrix
- FR-4: Threshold-based flagging

### Phase 3: Validation and Metrics (Week 1, Days 5-6)

- FR-5: Ground truth validation
- FR-6: Gate metrics computation

### Phase 4: Optional Exploration (Week 2, Day 1)

- FR-7: Threshold tuning

### Phase 5: Reporting (Week 2, Day 2)

- Generate all figures
- Write validation report (04_validation.md)

---

## Acceptance Checklist

- [ ] h-m2 extraction outputs loaded successfully
- [ ] Sentence transformer embeddings generated (all-MiniLM-L6-v2)
- [ ] Similarity matrix computed (pairwise cosine similarity)
- [ ] Contradictions flagged (threshold <0.3)
- [ ] Ground truth validation completed (h-e1, h-m1 cases)
- [ ] Mismatch detection recall ≥60% (acceptable), target ≥70%
- [ ] False positive rate <30%
- [ ] Required gate metrics figure generated
- [ ] Optional figures generated (similarity distribution, confusion matrix, threshold curve)
- [ ] Validation report written (04_validation.md)

---

## References

### Archon Knowledge Base

- **Hugging Face Transformers Documentation:** Standard library for sentence transformers
- **CLIP Image-Text Similarity Example:** Cosine similarity pattern adaptation
- **NLP Trace Analysis Benchmark:** Evaluation protocol design

### GitHub Implementations

- **UKPLab/sentence-transformers:** Official sentence transformers library
- **scikit-learn pairwise metrics:** Cosine similarity computation

### Previous Hypothesis Results

- **h-m2 Validation Report:** Extraction performance (Precision 86.3%, Recall 82.7%, Kappa 71.6%)
- **h-m1 Validation Report:** NL content presence (97.48%)

---

**Document Version:** 1.0
**Status:** Ready for Phase 3 Architecture Design
