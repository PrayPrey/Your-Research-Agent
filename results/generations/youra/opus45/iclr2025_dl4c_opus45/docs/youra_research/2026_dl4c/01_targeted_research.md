# Targeted Research Report (Phase 2A Compact Version)

**Generated:** 2026-03-24 | **Phase:** 1 - Targeted Research | **Researcher:** Anonymous

---

## Research Question

**Primary:** Can behavioral error taxonomy analysis on existing code generation benchmarks (HumanEval/MBPP) reveal complementary strengths between execution-based RL and preference-based DPO alignment?

**Detailed Questions:**
1. Do RL-aligned and DPO-aligned models produce systematically different error types?
2. Are there code generation subtasks where one method consistently outperforms the other?
3. Does error analysis reveal non-overlapping failure modes suggesting sequential training benefits?
4. Do behavioral differences persist across different code model architectures?
5. What pass@k improvements are observable comparing RL-only, DPO-only, and combined approaches?

**ROUTE_TO_0 Context:** Previous h-e1 hypothesis (gradient analysis) FAILED - RL/DPO gradients anti-correlated across all 48 layers. Must focus on BEHAVIORAL outcomes only.

---

## Key Literature

### Critical Comparison Paper
| Paper | Year | Citations | Key Finding |
|-------|------|-----------|-------------|
| Is DPO Superior to PPO for LLM Alignment? | 2024 | 267 | **PPO surpasses DPO in code competitions; DPO has "fundamental limitations"** |

### RL for Code Generation
| Paper | Year | Citations | Contribution |
|-------|------|-----------|--------------|
| CodeRL | 2022 | 418 | Foundational execution-based RL with critic network |
| StepCoder | 2024 | 83 | Curriculum learning + compiler feedback |
| RLEF | 2024 | 98 | End-to-end RL for execution feedback |

### Error Taxonomy
| Paper | Year | Key Contribution |
|-------|------|-----------------|
| ICSE 2025 (Wang et al.) | 2025 | Semantic vs syntactic error classification |
| MAPS 2023 (Song et al.) | 2023 | Open-coding methodology on HumanEval |
| LlmFix Study | 2024 | 19 distinct error causes across 14 LLMs |

---

## Key Implementations

| Repository | Stars | Purpose |
|------------|-------|---------|
| salesforce/CodeRL | 564 | Official CodeRL baseline |
| reddy-lab-code-research/PPOCoder | 117 | PPO for code generation |
| eric-mitchell/direct-preference-optimization | 2866 | Reference DPO implementation |
| evalplus/evalplus | 1701 | HumanEval+/MBPP+ evaluation |

---

## Research Gaps (Phase 2A Anchors)

### Gap 1: No Direct Error Type Comparison Between RL-Aligned and DPO-Aligned Models
**Relevance:** PRIMARY - Directly blocks answering research question
**Current State:** Error taxonomy exists (ICSE, MAPS) but not stratified by alignment method
**Missing:** Systematic error distribution comparison (syntax, runtime, wrong output) between methods
**Impact:** HIGH

### Gap 2: Lack of Task-Specific Strength Analysis Across Alignment Methods
**Relevance:** PRIMARY - Cannot identify complementary strengths without stratification
**Current State:** Only aggregate pass@k reported; no breakdown by problem type
**Missing:** Analysis by task category (string manipulation, math, algorithms)
**Impact:** HIGH

### Gap 3: No Evidence for Sequential Training Benefits (RL→DPO or DPO→RL)
**Relevance:** SECONDARY - Extends complementarity hypothesis
**Current State:** Methods studied in isolation only
**Missing:** Empirical evidence for sequential training improvements
**Impact:** MEDIUM

---

## Gap Priority Matrix

| Gap | Relevance | Impact | Priority |
|-----|-----------|--------|----------|
| Gap 1: Error Type Comparison | PRIMARY | HIGH | **CRITICAL** |
| Gap 2: Task-Specific Analysis | PRIMARY | HIGH | **CRITICAL** |
| Gap 3: Sequential Training | SECONDARY | MEDIUM | HIGH |

---

## Phase 2 Readiness

**Status: ✅ READY**

| Dimension | Score |
|-----------|-------|
| Research Question Clarity | 95% |
| Gap Definition | 90% |
| Data Availability | 95% |
| Evaluation Framework | 90% |

**Mandatory Constraints:**
- NO gradient-level analysis
- NO new benchmarks or scoring rubrics
- ONLY existing benchmarks (HumanEval, MBPP, HumanEval+, MBPP+)
- ONLY automated evaluation (pass@k)

---

## Data Quality Summary

| Source | Verified | Total |
|--------|----------|-------|
| Semantic Scholar | 18 | 18 |
| Exa/GitHub | 15 | 15 |
| Archon KB | 5 | 8 |
| Serena Memory | 2 | 2 |
| **Total** | **40 (93%)** | **43** |

---

*Compact version for Phase 2A hypothesis generation*
*Full report: 01_targeted_research_full.md*
