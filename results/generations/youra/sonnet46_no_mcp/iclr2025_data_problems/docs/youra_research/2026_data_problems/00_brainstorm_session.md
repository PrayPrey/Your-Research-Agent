---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Benchmark Contamination Detection via N-gram Overlap in Foundation Model Evaluation"
---

# Research Brainstorm Session Results

**Session Date:** 2026-05-04
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Benchmark contamination detection for foundation models — quantifying test data leakage in widely-used NLP benchmarks using existing pretrained model artifacts and n-gram overlap analysis

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Foundation models have become central to modern machine learning, with data playing a crucial role in their development. Adapting traditional data-centric methods to FMs is challenging due to the scale of both data and model architectures. Key challenges span the full FM pipeline: data collection and curation, attribution and interpretability, legal/copyright issues, synthetic data risks (model collapse), safety/privacy/fairness, and benchmark reliability. The DATA-FM Workshop at ICLR 2025 provides a well-defined, community-vetted scope for this research.

Source Type: Workshop CFP / Structured Input (ICLR 2025 DATA-FM Workshop) — Retrying after previous failure on Pythia deduplication hypothesis (h-e1 MUST_WORK FAIL).

---

## Lessons from Previous Attempts

### What Was Tried Before

The previous research direction (H-Pythia-Dedup-v1) investigated whether deduplication of training corpora (dedup-Pile vs. original-Pile) provides a scale-diminishing, task-type-asymmetric generalization benefit in Pythia models (1B–12B parameters), measured on MMLU low-overlap sub-tasks.

**Sub-hypothesis h-e1** was the EXISTENCE hypothesis: "Pythia models trained on dedup-Pile outperform non-dedup-Pile models on MMLU low-overlap sub-tasks by ≥1.5pp at ≤2.8B scale."

### Why It Failed

**Root cause: Implementation complexity exceeded execution capacity of the automated coding phase.**

The h-e1 experiment required:
1. Downloading and managing 8 Pythia model checkpoints (1B, 2.8B, 6.9B, 12B × dedup/non-dedup variants)
2. Running lm-evaluation-harness on MMLU with WIMBD-stratified sub-task selection
3. WIMBD n-gram overlap stratification to classify "low-overlap" vs. "high-overlap" sub-tasks
4. Bootstrap confidence interval computation (1000 iterations) across 57 MMLU sub-tasks
5. Causal mediation analysis components (H-M1, H-M2, H-M3) dependent on H-E1 results
6. 15 implementation tasks including preprocessing.py, evaluate.py, analysis.py, visualize.py, gate.py, run_experiment.sh

**Failure mode:** The Coder-Validator loop halted at step 2 initialization. Six code files were generated but none were validated. The experiment was never executed. No results produced. MUST_WORK gate unmet.

**Scientific note:** The hypothesis direction was NOT proven wrong — the experiment simply never ran. The failure was operational, not scientific.

### How THIS Direction Avoids Those Pitfalls

The new direction (benchmark contamination detection) is deliberately chosen to be **analysis-only** with no model training, no GPU-heavy evaluation loops, and no multi-stage dependency chains:

| Previous Direction | New Direction |
|-------------------|---------------|
| Required running lm-evaluation-harness on 8 model checkpoints | Only requires text comparison (n-gram matching) on static files |
| 15 implementation tasks, 5 sub-hypotheses with prerequisites | 3–5 tasks: load corpora → compute n-gram overlap → statistical analysis |
| WIMBD stratification required as prerequisite | WIMBD data already published and downloadable |
| Results cascade (H-E1 → H-M1 → H-M2/M3/C1) | Single-stage analysis, no cascading dependencies |
| Required GPU compute for model evaluation | CPU-only; pure text/statistical computation |
| Complex Coder-Validator loop with shell scripts + Python pipeline | Single Python script: load text → shingling → Jaccard/containment scoring |

The key lesson: **simpler implementation topology = higher probability of successful execution**.

---

## Session Plan

ROUTE_TO_0 auto-extraction from structured input (ICLR 2025 DATA-FM Workshop CFP) with failure context integration. Research direction pivoted from data curation (Pythia dedup) to benchmark contamination detection — a different sub-area of the same workshop topic space that requires substantially simpler implementation. Feasibility filtering applied: rejected ideas requiring new benchmarks, synthetic/generated data, human evaluation, or non-existent data. Accepted only hypotheses testable immediately using existing real datasets and existing model artifacts.

---

## Technique Sessions

ROUTE_TO_0 Auto-Fill Mode — failure-informed research component extraction. Topic: "Benchmarks and Evaluations" sub-area of DATA-FM CFP. Core pivot rationale: benchmark contamination detection is the lowest-implementation-complexity sub-question from the original brainstorm, uses only text matching on static publicly available files, and has no cascading hypothesis dependencies. Research components extracted and filtered through: (1) previous failure lessons, (2) feasibility constraints (no new benchmarks / no synthetic data / no human eval / no GPU-intensive pipelines), (3) implementation simplicity requirement derived from previous MUST_WORK FAIL.

---

## Research Question Development

### Initial Question

To what extent does test data contamination in widely-used NLP benchmark datasets inflate reported foundation model performance, and can the degree of contamination be quantified using only existing training corpora and standard n-gram overlap analysis — without model retraining, human annotation, or GPU-intensive evaluation?

### Refined Question

Can n-gram overlap between widely-used benchmark test sets (MMLU, HellaSwag, BIG-Bench Hard) and publicly available FM training corpora (The Pile, C4, RedPajama) be used to (a) estimate the contamination rate per benchmark, (b) predict performance inflation as a function of contamination level, and (c) identify which benchmark sub-tasks are most affected — using only existing static text files and established overlap metrics (13-gram containment, Jaccard similarity)?

### Detailed Sub-Questions

1. What is the 13-gram containment rate between MMLU (57 sub-tasks), HellaSwag, and BIG-Bench Hard test sets and The Pile / C4 / RedPajama training corpora, and does this rate vary significantly across benchmark sub-tasks and domains?

2. Across publicly available pretrained FM evaluation result tables (e.g., from EleutherAI lm-evaluation-harness leaderboard, Open LLM Leaderboard snapshots), is there a statistically significant positive correlation between a benchmark sub-task's estimated contamination rate (n-gram overlap) and the reported accuracy gap between FM families — consistent with contamination-driven performance inflation?

3. Do contamination rates computed via 13-gram containment (as used in WIMBD) and Jaccard similarity (as used in GPT-4 technical report contamination analysis) produce consistent benchmark contamination rankings, and where do they diverge — enabling identification of which metric is more conservative for contamination estimation?

---

## Reference Papers

*No reference papers provided in input — will discover in Phase 1*

Key papers to search for in Phase 1:
- WIMBD (What's In My Big Data?) — n-gram overlap analysis tool and The Pile contamination study
- GPT-4 Technical Report contamination analysis section
- BIG-Bench contamination analysis papers
- "Data contamination" survey papers for LLM benchmarks
- Open LLM Leaderboard contamination detection methodology

---

## Validation Results

### So What Test

Benchmark contamination is a critical and actively debated issue in the FM evaluation community. If benchmark test sets are contaminated with training data, reported accuracy numbers overstate actual generalization ability — misleading practitioners, policy makers, and researchers about true FM capabilities. Quantifying contamination rates using existing static corpora:
- Enables evidence-based decisions about which benchmarks to trust
- Provides a reproducible, computationally cheap methodology that any lab can apply
- Directly addresses a stated topic in the DATA-FM Workshop CFP ("Identifying and addressing pitfalls in existing dataset benchmarks, such as test data contamination")
- Has immediate practical impact: if MMLU sub-task X is 40% contaminated in The Pile, that changes how we interpret Pythia/LLaMA/GPT performance on that sub-task

Source: ICLR 2025 DATA-FM Workshop — significance pre-validated by the community.

### Feasibility Check

All three sub-questions can be tested immediately with existing public resources:

- **Sub-Q1:** MMLU, HellaSwag, BIG-Bench Hard test sets are publicly available. The Pile, C4, RedPajama are publicly available. WIMBD provides an open-source n-gram overlap tool. 13-gram containment computation requires only text loading + shingling + hash lookup. CPU-only, no GPU required. Estimated implementation: 1 Python script, ~200 lines.

- **Sub-Q2:** EleutherAI lm-evaluation-harness evaluation results are publicly tabulated. Open LLM Leaderboard historical results are available via Hugging Face datasets. Correlation analysis between contamination rate (from Sub-Q1) and accuracy gap requires only pandas + scipy.stats — no model inference needed.

- **Sub-Q3:** 13-gram containment and Jaccard similarity are both implementable with the same text files from Sub-Q1. Comparing two overlap metrics on the same data is a straightforward extension of Sub-Q1.

**Implementation topology:** 3 sequential tasks (no cascading prerequisites), all CPU-only, all using static publicly available text files. Estimated total implementation: 1 Python module + 1 analysis notebook. No model downloading, no lm-evaluation-harness, no GPU.

**No obvious blockers.** This is the simplest possible operationalization of a real research question within the DATA-FM workshop scope.

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can n-gram overlap between widely-used benchmark test sets (MMLU, HellaSwag, BIG-Bench Hard) and publicly available FM training corpora (The Pile, C4, RedPajama) be used to (a) estimate the contamination rate per benchmark, (b) predict performance inflation as a function of contamination level, and (c) identify which benchmark sub-tasks are most affected — using only existing static text files and established overlap metrics (13-gram containment, Jaccard similarity)?

### detailed_question
1. What is the 13-gram containment rate between MMLU (57 sub-tasks), HellaSwag, and BIG-Bench Hard test sets and The Pile / C4 / RedPajama training corpora, and does this rate vary significantly across benchmark sub-tasks and domains?

2. Across publicly available pretrained FM evaluation result tables (e.g., from EleutherAI lm-evaluation-harness leaderboard, Open LLM Leaderboard snapshots), is there a statistically significant positive correlation between a benchmark sub-task's estimated contamination rate (n-gram overlap) and the reported accuracy gap between FM families — consistent with contamination-driven performance inflation?

3. Do contamination rates computed via 13-gram containment (as used in WIMBD) and Jaccard similarity (as used in GPT-4 technical report contamination analysis) produce consistent benchmark contamination rankings, and where do they diverge — enabling identification of which metric is more conservative for contamination estimation?

### reference_papers
*No reference papers provided in input — will discover in Phase 1*

Key papers to search for in Phase 1:
- WIMBD (What's In My Big Data?) — n-gram overlap analysis tool and The Pile contamination study
- GPT-4 Technical Report contamination analysis section
- BIG-Bench contamination analysis papers
- "Data contamination" survey papers for LLM benchmarks
- Open LLM Leaderboard contamination detection methodology

</phase1-input>

---

## Session Insights

### Key Discoveries

- The previous Pythia dedup hypothesis failed due to **implementation complexity**, not scientific invalidity — the experiment was never executed
- The key lesson: implementation topology (number of steps, GPU requirements, cascading dependencies) is a first-class feasibility criterion
- Benchmark contamination detection is the **lowest-complexity** sub-question in the original DATA-FM brainstorm: it requires only static text files, n-gram matching, and correlation analysis
- WIMBD already provides open-source tooling for 13-gram contamination analysis — reducing implementation to configuration + analysis rather than building from scratch
- The three sub-questions form a natural progression: compute rates → correlate with accuracy → compare metrics; each is independently testable with no cascading MUST_WORK dependencies
- This direction directly targets a DATA-FM Workshop CFP bullet point: "Identifying and addressing pitfalls in existing dataset benchmarks, such as test data contamination"

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode (failure-informed structured input extraction) — Failure root cause analysis, implementation complexity assessment, research direction pivoting within same topic space (DATA-FM CFP), feasibility constraint filtering (no new benchmarks / no synthetic data / no human eval / no GPU-intensive pipelines / no cascading dependencies)

### Areas for Further Exploration

- Pythia dedup hypothesis (H-Pythia-Dedup-v1): scientifically valid but operationally complex — could retry with simplified implementation in a future pipeline iteration
- Data attribution accuracy comparison (Sub-Q2 from original brainstorm): interesting but requires running TRAK/TracIn which has some implementation complexity
- Multimodal contamination detection: same n-gram approach extended to image captioning benchmarks — promising follow-up
- Theoretical connection between contamination rate and memorization vs. generalization — future work
- Economic models for data pricing and data marketplaces — deferred (requires novel framework design)

---

## Next Steps

Proceed to Phase 1 - Targeted Research

Focus Phase 1 research on:
1. WIMBD paper and codebase (primary tool for Sub-Q1)
2. Existing contamination analyses in GPT-4 TR, Llama-2 TR, PaLM-2 TR
3. Open LLM Leaderboard contamination detection results
4. Prior work on benchmark data contamination in LLMs (Dodge et al. 2021, Wei et al. 2023, etc.)
5. The Pile, C4, RedPajama documentation (for corpus availability confirmation)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 — learned from h-e1 MUST_WORK FAIL)*
*Ready for: Phase 1 - Targeted Research*
