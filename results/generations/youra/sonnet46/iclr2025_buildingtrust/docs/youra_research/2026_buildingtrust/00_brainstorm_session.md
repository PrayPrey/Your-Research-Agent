---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: RLHF Alignment vs. Calibration Trade-off in LLMs"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-14
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Trustworthy LLMs — investigating whether RLHF alignment training systematically degrades model calibration, using existing benchmarks and paired base/aligned model families

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction with failure context integration)

---

## Starting Context

As Large Language Models (LLMs) are rapidly adopted across diverse industries, concerns around their trustworthiness, safety, and ethical implications increasingly motivate academic research, industrial development, and legal innovation. LLMs are increasingly integrated into complex applications, where they must navigate challenges related to data privacy, regulatory compliance, and dynamic user interactions. This workshop (ICLR 2025: Building Trust in Language Models and Applications) addresses the unique challenges posed by the deployment of LLMs, ranging from guardrails to explainability to regulation and beyond.

Source Type: Workshop CFP / Structured Input — Retrying after previous failure on cross-dimensional correlation hypothesis.

---

## Lessons from Previous Attempts

### What Was Tried Before
- **Hypothesis (h-e1):** Cross-dimensional trustworthiness correlations — at least one pairwise Spearman ρ ≤ -0.3 (negative) among robustness/truthfulness/fairness across ≥20 LLMs
- **Method:** Evaluated 20 LLMs (LLaMA-2, Mistral, Mixtral, OPT, Pythia, Qwen, Phi, GPT-2, StableLM) on ANLI (robustness), TruthfulQA-MC1 (truthfulness), CrowS-Pairs (fairness)
- **Result:** All correlations POSITIVE — RT=0.901, TF=0.170, RF=0.209. Max negative ρ = 0.1701 vs threshold ≤ -0.3. **FAIL.**

### Why It Failed
1. **Capability dominance:** Robustness and truthfulness are near-identical capability rankings (RT=0.901) — model capability drives all dimensions simultaneously
2. **Task substitution semantics:** ANLI ≠ AdvGLUE++ adversarial robustness; CrowS-Pairs pct_stereotype ≠ refusal/toxicity
3. **Imbalanced alignment representation:** Only 3/20 models had RLHF training; base models dominate, diluting alignment signal
4. **Wrong confound level:** Tested raw scores without controlling for model scale — scale drives everything

### How This New Direction Avoids Those Pitfalls
1. **Paired base+aligned design:** Explicitly pair each model with its RLHF/instruction-tuned counterpart (LLaMA-2-7B vs LLaMA-2-7B-chat, etc.) — differences are isolated to alignment training only
2. **Avoids capability confound:** Within-pair comparison cancels the scale/capability factor entirely
3. **Different phenomenon:** Calibration (confidence reliability) is mechanistically distinct from accuracy — RLHF reward hacking can inflate confidence without improving accuracy
4. **Mature benchmarks exist:** ECE/MCE computable from TruthfulQA, MMLU, HellaSwag — all existing datasets, no new benchmarks needed
5. **Stronger theoretical prior:** Overconfidence from RLHF is predicted by reward model exploitation literature; positive result is plausible

---

## Session Plan

ROUTE_TO_0 Auto-Fill — failure context integrated from h-e1 Serena Memory records. Research direction pivoted from correlation-profiling to within-pair calibration analysis.

---

## Technique Sessions

ROUTE_TO_0 Failure Recovery Mode — No interactive sessions. Research direction derived by:
1. Analyzing h-e1 failure root causes (from Serena Memory)
2. Identifying what went wrong: capability confound + misaligned model mix + wrong phenomenon
3. Pivoting to a mechanistically distinct but related trustworthiness property: **calibration reliability under RLHF alignment**
4. Selecting workshop scope areas that remain unexplored: reliability/truthfulness (scope item 2) approached from a calibration angle rather than raw accuracy
5. Ensuring paired experimental design to isolate alignment training effect

The new research focuses on: Does RLHF alignment training systematically worsen Expected Calibration Error (ECE) on knowledge-intensive tasks, as measured by comparing paired base vs. instruction-tuned model variants on TruthfulQA, MMLU, and HellaSwag?

---

## Research Question Development

### Initial Question

Does RLHF alignment training systematically degrade model calibration (confidence reliability) in LLMs, detectable via Expected Calibration Error on existing benchmarks?

### Refined Question

Does RLHF/instruction-tuning alignment systematically increase Expected Calibration Error (ECE) in LLMs relative to their base model counterparts, and is this miscalibration consistent across model families (LLaMA-2, Mistral, Falcon) and task types (factual knowledge, reasoning, commonsense) as measured on TruthfulQA, MMLU, and HellaSwag?

### Detailed Sub-Questions

1. Do instruction-tuned (RLHF-aligned) LLMs exhibit significantly higher ECE than their paired base models on TruthfulQA-MC, controlling for raw accuracy?
2. Is the calibration degradation consistent across model families (LLaMA-2-7B/chat, LLaMA-2-13B/chat, Mistral-7B/instruct, Falcon-7B/instruct) when measured using MMLU and HellaSwag?
3. Does the magnitude of ECE increase from base→aligned correlate with instruction-tuning method (RLHF vs. SFT-only), detectable from model cards and existing evaluations?
4. Do aligned models show systematic overconfidence (predicted probability > accuracy) or underconfidence patterns, and is this consistent across benchmark types (factual vs. reasoning vs. commonsense)?
5. Can calibration reliability (ECE/MCE) serve as a complementary trustworthiness metric to accuracy — identifying models that are accurate-but-miscalibrated vs. less-accurate-but-well-calibrated?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

**Significance:** Practitioners deploying LLMs in high-stakes settings (healthcare, legal, finance) need not just accurate models but *reliably confident* models — a miscalibrated model that is 80% accurate but claims 99% confidence is dangerous. If RLHF alignment systematically worsens calibration as a side effect, this has immediate implications for:
- Model selection criteria (calibration-accuracy trade-off)
- The design of alignment procedures that preserve calibration
- Trust frameworks for LLM deployment — the ICLR workshop's central concern

**Contribution:** First systematic empirical comparison of calibration shift from base→aligned across multiple paired model families on existing benchmarks. Directly actionable for practitioners selecting between base and instruction-tuned variants.

**Feasibility Constraints:**
- ✅ No new benchmarks — TruthfulQA, MMLU, HellaSwag all exist
- ✅ No synthetic/generated data
- ✅ No human evaluation — ECE is computed from model outputs
- ✅ All paired models available on HuggingFace
- ✅ Paired design explicitly controls for the capability confound that killed h-e1

### Feasibility Check

**Feasibility: HIGH**
- **Benchmarks:** TruthfulQA (817 questions, MC format), MMLU (57 subjects × ~100 questions), HellaSwag (10k validation) — all publicly available
- **Models:** LLaMA-2 7B/7B-chat, LLaMA-2 13B/13B-chat, Mistral 7B/7B-instruct, Falcon 7B/7B-instruct — all on HuggingFace
- **Metric:** ECE (Expected Calibration Error) computed from softmax probabilities — no human annotation
- **Runtime:** Standard inference evaluation, parallelizable; ~2-4 hours per model
- **lm-eval compatibility:** MMLU and HellaSwag are natively supported; TruthfulQA MC1 supported in lm-eval v0.4.11

**Constraint Check:**
- ✅ No new benchmarks required
- ✅ No synthetic/generated data
- ✅ No human evaluation/annotation
- ✅ All datasets exist today and are publicly accessible
- ✅ Paired model design eliminates capability confound (h-e1's fatal flaw)

---

## Phase 1 Input Package

<phase1-input>

### research_question
Does RLHF/instruction-tuning alignment systematically increase Expected Calibration Error (ECE) in LLMs relative to their base model counterparts, and is this miscalibration consistent across model families (LLaMA-2, Mistral, Falcon) and task types (factual knowledge, reasoning, commonsense) as measured on TruthfulQA, MMLU, and HellaSwag?

### detailed_question
1. Do instruction-tuned (RLHF-aligned) LLMs exhibit significantly higher ECE than their paired base models on TruthfulQA-MC, controlling for raw accuracy?
2. Is the calibration degradation consistent across model families (LLaMA-2-7B/chat, LLaMA-2-13B/chat, Mistral-7B/instruct, Falcon-7B/instruct) when measured using MMLU and HellaSwag?
3. Does the magnitude of ECE increase from base→aligned correlate with instruction-tuning method (RLHF vs. SFT-only), detectable from model cards and existing evaluations?
4. Do aligned models show systematic overconfidence (predicted probability > accuracy) or underconfidence patterns, and is this consistent across benchmark types (factual vs. reasoning vs. commonsense)?
5. Can calibration reliability (ECE/MCE) serve as a complementary trustworthiness metric to accuracy — identifying models that are accurate-but-miscalibrated vs. less-accurate-but-well-calibrated?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Previous h-e1 failure reveals model capability dominates all trustworthiness dimension rankings — correlation-based approaches on raw scores are confounded by scale
- Paired base+aligned model design cleanly isolates alignment training effect, avoiding the dominant confound
- RLHF reward hacking literature predicts calibration degradation — mechanistic prior exists (unlike h-e1's purely empirical negative correlation assumption)
- ECE is computable from existing benchmark outputs without any additional annotation
- TruthfulQA MC1, MMLU, HellaSwag are all supported by lm-eval v0.4.11 (confirmed from h-e1 technical notes)
- Calibration is mechanistically distinct from accuracy — a well-calibrated model can be less accurate while more trustworthy in deployment

### Techniques Used

ROUTE_TO_0 Failure Recovery Mode — structured extraction from failure context (Serena Memory: h-e1/failure_record, h-e1/phase4_completion) combined with workshop CFP analysis. Failure root cause analysis applied to design a hypothesis that avoids h-e1's pitfalls.

### Areas for Further Exploration

- Unlearning for LLMs (MUSE/TOFU benchmarks) — different trustworthiness dimension, future direction
- Guardrails evaluation — limited existing benchmarks, higher risk
- Explainability/interpretability — requires model internals access
- Temperature scaling as calibration correction — could be Phase 2B sub-hypothesis
- Calibration under distribution shift (OOD settings) — extension if within-distribution ECE shows signal

---

## Next Steps

Proceed to Phase 1 - Targeted Research

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 — Failure Recovery)*
*Ready for: Phase 1 - Targeted Research*
