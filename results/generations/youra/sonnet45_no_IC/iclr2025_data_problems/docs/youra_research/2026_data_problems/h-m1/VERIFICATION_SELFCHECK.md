# Phase 2C Self-Check Report: h-m1

**Date:** 2026-07-12  
**Hypothesis ID:** h-m1  
**Phase:** Phase 2C - Experiment Design  
**Verification Agent:** Batch-Mode Experiment Design Verification Agent

---

## Self-Check Summary

✅ **Files Present:**
- `02b_context.md` - EXISTS (4,495 bytes)
- `02c_experiment_brief.md` - EXISTS (15,451 bytes)

✅ **State File Updated:**
- `verification_state.yaml` - h-m1.experiment_design.status = COMPLETED
- `verification_state.yaml` - h-m1.experiment_design.file points to correct path

---

## ⚠️ CRITICAL ISSUES DETECTED

### Synthetic Data Violation: **TRUE**
### Tautological Design Violation: **TRUE**
### Confidence: **HIGH**

---

## Violations Found

### 1. Synthetic Data - Training Data Construction (CRITICAL)
**Location:** Lines 202-223 in `02c_experiment_brief.md`

**Issue:** Training data stratification is programmatically constructed with hard-coded oversampling parameters (3x for divergent examples) rather than using naturally occurring data distributions.

**Evidence:**
```python
# Line 212-221: stratify_training_data() method
divergent_mask = (educational_scores > np.median(educational_scores)) & \
                (beir_scores > np.median(beir_scores))

# Oversample divergent examples 3x
for i, (text, label) in enumerate(examples):
    stratified_examples.append((text, label))
    if divergent_mask[i]:
        stratified_examples.extend([(text, label)] * 2)  # 3x total
```

**Impact:** The training data distribution does not reflect real-world data, making the experiment results ungeneralizable.

---

### 2. Tautological Design - Hypothesis Embedded in Data (CRITICAL)

**Issue:** Stratification logic explicitly oversamples examples that exhibit the target property (low-educational, high-BEIR), which embeds the hypothesis into the data generation process.

**Evidence:**
- Lines 212-221: `divergent_mask` identifies and oversamples exactly the signal the hypothesis claims to discover
- Line 216: "Oversample divergent examples 3x" - the exact samples showing retrieval-pretraining divergence are artificially multiplied

**Impact:** The experiment **cannot fail** because the classifier is trained on data that artificially amplifies the pattern it's supposed to discover. If stratified training works, the classifier learns what was embedded via oversampling, not what naturally distinguishes retrieval quality.

---

### 3. Tautological Design - Circular Validation (CRITICAL)

**Issue:** Success is pre-determined by the experimental design itself.

**Circular Logic:**
1. Hypothesis claims: "Stratified training helps classifier learn retrieval-quality signals"
2. Training method: Artificially oversample examples showing retrieval-quality signals (3x)
3. Evaluation: Check if classifier learned retrieval-quality signals
4. Result: **Of course it did - we forced 3x more of those examples into training!**

This is equivalent to:
- Hypothesis: "Students learn better with extra practice"
- Method: Give students the exact test questions 3x during practice
- Evaluation: Check if students score well on the test
- Conclusion: "Extra practice works!" ❌

---

### 4. Synthetic Data - Non-Reproducible Sampling (HIGH)

**Location:** Lines 149-152 in `02c_experiment_brief.md`

**Issue:** Common Crawl evaluation data requires "manual download and sampling" with no specific reproducible sampling method.

**Evidence:**
```python
# Common Crawl sampling (programmatic)
# Note: Requires manual download and sampling from Common Crawl dumps
# Alternative: Use pre-filtered subset from H-E1 experiment
```

**Impact:** Non-reproducible evaluation data sampling could bias results through cherry-picking.

---

## Recommendation

**ACTION: REJECT this experiment design**

### Why This Design is Fundamentally Flawed

The stratification approach is **fundamentally tautological** - it creates the pattern it claims to discover.

**What the hypothesis should test:**
- Can a classifier trained on natural BEIR examples learn to identify retrieval-quality signals?

**What this design actually tests:**
- Can a classifier learn a pattern when we artificially amplify that pattern 3x in the training data?

The answer to the second question is trivial: **yes, obviously**.

---

## Suggested Fix

### Option 1: Remove Artificial Oversampling
- Use the **natural distribution** of BEIR training data
- No 3x oversampling of divergent examples
- Test whether the classifier can learn retrieval-quality signals **without artificial amplification**

### Option 2: Different Stratification Strategy
- If stratification is necessary for class balance, stratify by **label** (positive/negative), not by the target pattern
- Do NOT stratify by (educational quality × BEIR quality) since that's what we're trying to discover

### Option 3: Use Real Data Throughout
- Load actual BEIR training examples without programmatic modification
- Sample Common Crawl with a **fixed, reproducible** sampling method (e.g., "first 100K documents from dump CC-2023-14")
- Let the classifier learn from natural data distributions

---

## Files Generated by This Self-Check

1. ✅ `02c_verification_synthetic_data.json` - Structured verification output
2. ✅ `VERIFICATION_SELFCHECK.md` - This human-readable report
3. ✅ Updated `verification_state.yaml` - Added verification_issues section to h-m1

---

## Next Steps

**DO NOT PROCEED TO PHASE 3** until this experiment design is revised.

The current design will produce meaningless results because success is guaranteed by construction, not by genuine learning of retrieval-quality signals.

---

**Verification Agent Status:** STOPPED  
**Awaiting:** User decision on how to fix the tautological design
