---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Building Trust - Confidence Frequency Calibration"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-24
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Building Trust in Language Models and Applications - pivoting from failed entropy/attention/verbalized confidence/selective prediction approaches to Confidence Frequency Calibration

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode - 8th Attempt)

**Session Duration:** < 1 minute (automated extraction with comprehensive failure context integration)

---

## Starting Context

As Large Language Models (LLMs) are rapidly adopted across diverse industries, concerns around their trustworthiness, safety, and ethical implications increasingly motivate academic research, industrial development, and legal innovation. This research targets Workshop scope item 7: "Calibration: measuring and improving the calibration of LLMs."

Source Type: Workshop CFP - ICLR 2025 Workshop on Building Trust in Language Models and Applications

**CRITICAL PIVOT (8th Attempt):** SEVEN previous attempts have failed:
1. Entropy-based UQ (confounds explain 99.99%)
2. H_rest sharpening falsified (CoT INCREASES entropy)
3. Attention consistency (CFS AUROC marginal, CI includes random chance)
4. Residualized entropy variance too weak (4.98% < 10% threshold)
5. Self-Consistency Disagreement (routed back to Phase 0)
6. Verbalized Confidence Calibration (routed back to Phase 0 after h-e1 FAILED)
7. Selective Prediction via p_max (55.6% pass rate, complete failure on GSM8K)

This attempt pivots to a FUNDAMENTALLY DIFFERENT paradigm: **Confidence Frequency Calibration** - where instead of using single-token p_max, we analyze the FREQUENCY of confident predictions across binned confidence levels to measure and improve calibration directly.

---

## Lessons from Previous Attempts

### What Was Tried Before

**Attempts 1-4 (Internal Signal Extraction):**
- Residualized entropy signal (ε̂_H): R²=0.877-0.9999 from confounds
- H_rest distributional sharpening: Extended CoT INCREASES entropy (p<0.001)
- CFS attention stability: AUROC=0.55 but CI [0.47, 0.63] includes 0.50
- Variance ratio: Only 4.98% beyond confounds (threshold: 10%)

**Attempts 5-6 (Alternative Paradigms):**
- Self-Consistency Disagreement (SCDM): Confounds still dominate
- Verbalized Confidence Calibration: h-e1 FAILED with cascade to all mechanism hypotheses
- h-m2 showed CoT INCREASES entropy rather than sharpening (falsifying the mechanism)

**Attempt 7 (Selective Prediction):**
- Token-level p_max as confidence score for selective prediction
- **Result:** 55.6% pass rate (5/9 conditions)
- **Critical Failure:** Complete failure on GSM8K (0/3) due to task-prompt mismatch
- **Root Cause:** p_max requires single-token answers; GSM8K requires chain-of-thought reasoning
- p_max works for multiple-choice QA (MMLU, TruthfulQA) but NOT for open-ended reasoning

### Why All Attempts Failed

| Attempt | Approach Category | Failure Mode | Root Cause |
|---------|-------------------|--------------|------------|
| 1-2 | Internal (Entropy) | Confound saturation | Entropy mechanically determined by (Δp_max, H₀, Δtokens) |
| 3 | Internal (H_rest) | Wrong direction | CoT explores alternatives, doesn't narrow |
| 4 | Internal (Attention) | Weak signal | CFS captures noisy relationship |
| 5 | Behavioral (Consistency) | Confound saturation | Same confound structure applies |
| 6 | Explicit (Verbalized) | Cascade failure | Foundation existence hypothesis failed (R²=0.9999) |
| 7 | Selective Prediction | Task mismatch | p_max limited to single-token answers; fails on reasoning tasks |

**Common Thread Across All 7 Attempts:**
1. Attempts 1-6 tried to CREATE or EXTRACT uncertainty signals (which don't exist independently)
2. Attempt 7 used existing signals (p_max) but only works for constrained output formats (MCQ)
3. ALL approaches assumed per-instance uncertainty quantification is the goal

### What Showed Promise (To Preserve)

1. **Calibration IS a valid research target** - Workshop explicitly includes scope item 7
2. **Existing benchmarks exist** - TruthfulQA, MMLU have ground truth
3. **ECE and Brier score are established metrics** - No need to create new evaluation
4. **Token-level probabilities ARE accessible** - softmax outputs are standard
5. **p_max DOES work for MCQ tasks** - MMLU (3/3), TruthfulQA (2/3) passed in Attempt 7
6. **Aggregate statistics may be more robust than per-instance signals**

### How THIS Direction Avoids Those Pitfalls

**PARADIGM SHIFT: Confidence Frequency Calibration (CFC)**

**Key Insight:** Instead of:
- Trying to create NEW uncertainty signals (Attempts 1-6)
- Using p_max for per-instance selective prediction (Attempt 7)

We analyze the FREQUENCY DISTRIBUTION of model confidence across binned levels to:
1. MEASURE calibration error directly (ECE, reliability diagrams)
2. IDENTIFY systematic miscalibration patterns (overconfidence/underconfidence regions)
3. APPLY post-hoc calibration (temperature scaling, histogram binning)

**Why This Is Fundamentally Different:**

| Failed Approaches | Confidence Frequency Calibration |
|-------------------|----------------------------------|
| Per-instance uncertainty signals | Aggregate frequency statistics |
| Fight against confounds | No confound structure (direct bin frequencies) |
| Require new signal definitions | Uses standard ECE/calibration framework |
| p_max for individual decisions | p_max distribution across population |
| Task-format dependent (MCQ only) | Works across all tasks (aggregate level) |
| Predict/improve single predictions | Measure/improve population-level calibration |

**Specific Research Direction:**
- **Existence (H-E):** Instruction-tuned LLMs exhibit systematic miscalibration patterns (ECE > threshold)
- **Mechanism (H-M):** Miscalibration is predictable from confidence bin frequencies
- **Condition (H-C):** Post-hoc calibration (temperature scaling) reduces ECE by meaningful margin

**Why This Will Work:**
1. **No per-instance assumptions:** Analyzes population-level statistics, not individual predictions
2. **Theoretically grounded:** ECE, reliability diagrams are standard calibration metrics
3. **No task-format restriction:** Works for any task with correctness labels (not just MCQ)
4. **Existing benchmarks:** Use MMLU, TruthfulQA, ARC with correctness labels
5. **Standard post-hoc methods:** Temperature scaling has proven track record
6. **No confound problem:** Frequency distributions are direct counts, not derived signals

---

## Session Plan

Auto-extracted from failure context synthesis (ROUTE_TO_0 - 8th Attempt):
- **Rejected** all internal signal extraction (entropy, attention, H_rest)
- **Rejected** behavioral signals that correlate with confounds (consistency)
- **Rejected** explicit verbalized confidence (foundation failed)
- **Rejected** per-instance selective prediction (task-format dependent)
- **Adopted** population-level confidence frequency analysis
- **Focus** on calibration (Workshop scope item 7) via aggregate statistics
- **Preserved** use of existing benchmarks and metrics (ECE, reliability diagrams)

---

## Technique Sessions

Auto-Fill Mode (ROUTE_TO_0) - Paradigm shift with:
- Analysis of 5 Serena Memory failure/limitation/superseded records
- Review of 7 failed attempts (entropy, H_rest, attention, variance, SCDM, verbalized, p_max selective prediction)
- Root cause synthesis: per-instance approaches either confounded or task-restricted
- New paradigm: POPULATION-LEVEL confidence frequency calibration analysis

---

## Research Question Development

### Initial Question

Do instruction-tuned LLMs exhibit systematic miscalibration patterns that can be measured via confidence frequency analysis and improved through post-hoc calibration methods?

### Refined Question

Can population-level confidence frequency analysis reveal systematic miscalibration patterns in instruction-tuned LLMs, and does post-hoc temperature scaling significantly reduce Expected Calibration Error (ECE) on standard QA benchmarks without requiring task-specific modifications?

### Detailed Sub-Questions

1. What is the baseline ECE of instruction-tuned LLMs (e.g., Qwen2.5-7B-Instruct) on MMLU and TruthfulQA when using answer-token probability as confidence?
2. Do reliability diagrams show systematic over-confidence or under-confidence patterns across confidence bins?
3. Does temperature scaling (learned T parameter) significantly reduce ECE compared to no calibration (baseline T=1)?
4. How does calibration performance vary across domains (STEM vs. humanities vs. social science)?
5. Is the calibration improvement robust across different model sizes within the same family?

---

## Reference Papers

Not provided - will discover in Phase 1

**Note:** Phase 1 will search for papers on:
- Expected Calibration Error (ECE) in neural networks
- Temperature scaling for neural network calibration (Guo et al., 2017)
- Reliability diagrams and calibration metrics
- LLM calibration and post-hoc methods
- Calibration across different task types

---

## Validation Results

### So What Test

**Significance:** Input from established research venue (ICLR 2025 Workshop) - directly addresses scope item 7 "Calibration: measuring and improving the calibration of LLMs."

**Impact:** Understanding population-level calibration patterns would enable:
- Reliable confidence estimates for downstream decision-making
- Simple post-hoc calibration via temperature scaling
- Domain-specific calibration insights (where are LLMs most/least calibrated?)
- Practical deployment with calibrated confidence scores

### Feasibility Check

**Feasibility Constraints Applied:**
- ✅ Uses existing benchmarks (TruthfulQA, MMLU, ARC)
- ✅ Uses existing metrics (ECE, reliability diagrams, Brier score)
- ✅ No new benchmark or rubric creation required
- ✅ No human evaluation or annotation needed
- ✅ No synthetic data generation required
- ✅ Testable immediately with existing datasets and models
- ✅ Only requires standard inference (logit/probability access)
- ✅ Temperature scaling is well-established method

**Technical Feasibility:** Very High - requires collecting confidence-correctness pairs across test set and computing standard calibration metrics.

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can population-level confidence frequency analysis reveal systematic miscalibration patterns in instruction-tuned LLMs, and does post-hoc temperature scaling significantly reduce Expected Calibration Error (ECE) on standard QA benchmarks without requiring task-specific modifications?

### detailed_question
1. What is the baseline ECE of instruction-tuned LLMs (e.g., Qwen2.5-7B-Instruct) on MMLU and TruthfulQA when using answer-token probability as confidence?
2. Do reliability diagrams show systematic over-confidence or under-confidence patterns across confidence bins?
3. Does temperature scaling (learned T parameter) significantly reduce ECE compared to no calibration (baseline T=1)?
4. How does calibration performance vary across domains (STEM vs. humanities vs. social science)?
5. Is the calibration improvement robust across different model sizes within the same family?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

1. **Per-instance approaches consistently fail:** Whether extracting new signals or using existing p_max, per-instance uncertainty is either confounded or task-restricted.

2. **Population-level statistics avoid confounds:** Frequency distributions across confidence bins don't suffer from the confound saturation that plagued entropy-based approaches.

3. **ECE is a direct calibration measure:** Unlike AUROC for prediction tasks, ECE directly measures what we care about (calibration).

4. **Temperature scaling is battle-tested:** This post-hoc method has extensive empirical support in the literature.

5. **No task-format restriction:** Unlike p_max selective prediction (which failed on GSM8K), calibration analysis works on any task with correctness labels.

### Techniques Used

ROUTE_TO_0 (Failure Recovery Mode) with:
- Multi-attempt failure synthesis (7 failed pipelines)
- Root cause analysis (why both signal-extraction AND per-instance approaches failed)
- Paradigm shift identification (per-instance → population-level)
- Feasibility-first design (existing benchmarks, standard metrics)
- Theoretical grounding in calibration literature

### Areas for Further Exploration

Topics from workshop scope for future work:
- Domain-specific calibration analysis (medical, legal, technical domains)
- Multi-turn dialogue calibration
- Calibration under distribution shift
- Calibration-aware fine-tuning

---

## Next Steps

Proceed to Phase 1 - Targeted Research

**Phase 1 Focus:**
1. Search for papers on ECE and neural network calibration
2. Find work on temperature scaling and post-hoc calibration
3. Survey LLM-specific calibration studies
4. Review reliability diagram methodology
5. Identify state-of-the-art calibration benchmarks

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 - 8th Attempt)*
*Ready for: Phase 1 - Targeted Research*
