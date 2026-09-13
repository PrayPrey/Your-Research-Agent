---
# Phase 0 Output Metadata
pipeline_project_title: "Anonymous Pipeline: ML Data Practices & Benchmark Overuse"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-29
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** ML data practices, benchmark reproducibility, and the overuse of benchmark datasets in machine learning research.

**Session Approach:** Auto-Fill (Batch Mode) - Extracted from ICLR 2025 MLDPR workshop call.

**Session Duration:** Auto-generated (unattended)

---

## Starting Context

The ICLR 2025 workshop on "The Future of Machine Learning Data Practices and Repositories" identifies critical issues in the ML data ecosystem:
- Under-valuing of data work
- Ethical issues in datasets going undiscovered
- Lack of standardized dataset deprecation procedures
- Mis-use of datasets out-of-context
- Overemphasis on single metrics rather than holistic evaluation
- Overuse of the same few benchmark datasets

Workshop involves major repositories (OpenML, HuggingFace Datasets, UCI ML Repository) and researchers from ML, law, governance, and social sciences.

---

## Lessons from Previous Attempts

N/A - First attempt

---

## Session Plan

Batch-mode auto-extraction targeting workshop topics that satisfy feasibility constraints:
- Must use existing real datasets
- Must use existing benchmarks
- No new benchmarks/rubrics/scoring frameworks
- No synthetic data or future data
- No human evaluation required

---

## Technique Sessions

**Technique:** Constraint-Driven Extraction

Filtered workshop topics through mandatory feasibility constraints:

| Topic | Feasible? | Reason |
|-------|-----------|--------|
| Benchmark reproducibility | ✓ YES | Can test with existing benchmarks |
| Overfitting/overuse of benchmarks | ✓ YES | Can analyze existing leaderboards |
| Holistic benchmarking | ✗ NO | Requires new evaluation frameworks |
| Dataset documentation | ✗ NO | Requires human annotation/scoring |
| Non-traditional benchmarking | ✗ NO | Requires new paradigms |
| Dataset deprecation | ✗ NO | Requires human judgment |
| FAIR datasets | ✗ NO | Requires rubric creation |

**Selected Focus:** Benchmark overuse and its empirical consequences on model evaluation.

---

## Research Question Development

### Initial Question

How does the overuse of a small set of benchmark datasets affect the reliability and generalizability of ML model comparisons?

### Refined Question

Can we empirically quantify the "benchmark overfitting" phenomenon by measuring performance degradation when models ranked highly on popular benchmarks are evaluated on semantically-similar but less-used alternative datasets?

### Detailed Sub-Questions

1. Which benchmark datasets exhibit the highest concentration of published results (benchmark popularity distribution)?
2. For popular benchmarks, do alternative datasets with similar task semantics exist that receive significantly less attention?
3. Do models that rank highly on popular benchmarks maintain their relative rankings on these alternative datasets?
4. Is there a correlation between a model's publication date and its performance gap between popular vs. alternative benchmarks (indicating temporal overfitting)?

---

## Reference Papers

1. **Recht et al. (2019)** - "Do ImageNet Classifiers Generalize to ImageNet?" - Measures generalization gap on new test sets.
2. **Beyer et al. (2020)** - "Are we done with ImageNet?" - Questions benchmark saturation.
3. **Dehghani et al. (2021)** - "The Benchmark Lottery" - Documents benchmark selection bias.
4. **Bowman & Dahl (2021)** - "What Will it Take to Fix Benchmarking in Natural Language Understanding?" - Discusses benchmark limitations.
5. **Rodriguez et al. (2021)** - "Evaluation Examples Are Not Equally Informative" - Item Response Theory for benchmarking.

---

## Validation Results

### So What Test

**Impact:** If benchmark overfitting is empirically demonstrated, it would:
- Challenge current ML evaluation practices
- Provide concrete evidence for workshop's stated concerns about benchmark overuse
- Offer actionable recommendations for researchers and repository maintainers

**Who cares:** ML researchers, benchmark maintainers, paper reviewers, repository administrators (OpenML, HuggingFace, UCI).

### Feasibility Check

| Constraint | Status |
|------------|--------|
| Uses existing real datasets | ✓ PASS - ImageNet, CIFAR, alternative test sets exist |
| Uses existing benchmarks | ✓ PASS - Papers With Code leaderboards, OpenML |
| No new benchmarks needed | ✓ PASS - Comparing existing benchmarks |
| No synthetic data | ✓ PASS - All real published results |
| No human evaluation | ✓ PASS - Automated metric comparison |

**Verdict:** FEASIBLE

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can we empirically quantify the "benchmark overfitting" phenomenon by measuring performance degradation when models ranked highly on popular benchmarks are evaluated on semantically-similar but less-used alternative datasets?

### detailed_question
1. Which benchmark datasets exhibit the highest concentration of published results (benchmark popularity distribution)?
2. For popular benchmarks, do alternative datasets with similar task semantics exist that receive significantly less attention?
3. Do models that rank highly on popular benchmarks maintain their relative rankings on these alternative datasets?
4. Is there a correlation between a model's publication date and its performance gap between popular vs. alternative benchmarks (indicating temporal overfitting)?

### reference_papers
1. Recht et al. (2019) - "Do ImageNet Classifiers Generalize to ImageNet?" - Direct precedent for measuring generalization gaps
2. Beyer et al. (2020) - "Are we done with ImageNet?" - Documents benchmark saturation effects
3. Dehghani et al. (2021) - "The Benchmark Lottery" - Theoretical grounding for benchmark selection bias
4. Bowman & Dahl (2021) - "What Will it Take to Fix Benchmarking in NLU?" - Problem framing for NLP domain
5. Rodriguez et al. (2021) - "Evaluation Examples Are Not Equally Informative" - Alternative evaluation methodology

</phase1-input>

---

## Session Insights

### Key Discoveries

- Workshop explicitly names "overfitting and overuse of benchmark datasets" as topic of interest
- Feasibility constraints naturally filter to benchmark reproducibility questions
- Prior work (Recht et al.) provides direct methodological precedent
- Multiple domains (vision, NLP) exhibit similar benchmark concentration

### Techniques Used

- Constraint-driven topic filtering
- Workshop call analysis
- Feasibility validation matrix

### Areas for Further Exploration

- Specific benchmark pairs to analyze (ImageNet/ImageNet-V2, GLUE/SuperGLUE alternatives)
- Time-series analysis of leaderboard evolution
- Repository-specific patterns (OpenML vs HuggingFace)

---

## Next Steps

**Phase 1 - Targeted Research:**
1. Gather benchmark popularity statistics from Papers With Code / OpenML
2. Identify benchmark-alternative pairs for comparative analysis
3. Collect published model results across benchmark pairs
4. Review Recht et al. methodology for replication approach

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
