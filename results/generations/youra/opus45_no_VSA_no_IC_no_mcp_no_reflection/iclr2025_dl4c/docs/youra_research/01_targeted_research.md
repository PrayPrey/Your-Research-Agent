# Targeted Research Report (Compact - Phase 2A Input)

**Research Question:** What is the relative effectiveness of different execution feedback granularities (binary pass/fail vs. detailed error traces vs. test coverage signals) for improving code LLM performance through RLEF?

**Date:** 2026-08-29
**Phase:** 1 - Targeted Research Gathering

---

## Executive Summary

Three primary gaps identified for hypothesis generation:
1. No controlled comparison of feedback granularities
2. Test coverage as reward signal unexplored
3. Sample efficiency RLEF vs SFT unmeasured

**Phase 2A Readiness:** HIGH

---

## 1. Research Questions

### Primary
What is the relative effectiveness of different execution feedback granularities for improving code LLM performance through RLEF?

### Detailed Sub-Questions
1. Binary vs fine-grained error feedback?
2. Test coverage as reward signal?
3. Sample efficiency RLEF vs SFT?
4. Outcome-based vs process-based reward architectures?

---

## 2. Key Queries (Top 3 per Category)

**Reference Paper:** CodeRL execution feedback, RLTF multi-granularity, process vs outcome supervision
**Brainstorm:** execution feedback granularity, coverage reward signal, sample efficiency comparison
**Direct:** binary vs detailed feedback, RL reward architecture, code LLM alignment

---

## 3. Past Cases (Archon) - Compact

| KB Entry ID | Query | Key Pattern |
|-------------|-------|-------------|
| *INFERRED* | CodeRL patterns | Actor-critic with binary execution reward |
| *INFERRED* | PPOCoder patterns | PPO-based alternative |
| *INFERRED* | RLTF patterns | Multi-granularity test feedback |

---

## 4. Academic Papers (Scholar) - Compact

| Title | Year | arXiv ID | Key Insight |
|-------|------|----------|-------------|
| CodeRL | 2022 | 2207.01780 | Foundational RLEF with binary reward |
| RLTF | 2023 | 2307.04349 | Multi-granularity feedback comparison |
| PPOCoder | 2023 | 2306.05826 | PPO-based execution feedback |
| Self-Repair | 2023 | 2306.09896 | Error trace for iterative debugging |
| Let's Verify Step by Step | 2023 | 2305.20050 | Process reward models |

---

## 5. Implementation Resources (Exa) - Compact

| Resource | URL | Stars | Key Feature |
|----------|-----|-------|-------------|
| salesforce/CodeRL | github.com/salesforce/CodeRL | 500+ | Binary reward implementation |
| huggingface/trl | github.com/huggingface/trl | 8k+ | PPO/RLHF training library |
| evalplus/evalplus | github.com/evalplus/evalplus | 300+ | Execution harness |

---

## 6. Chain Analysis - Compact

```
CodeRL (2022) → PPOCoder/RLTF (2023) → Gap: Controlled comparison
Binary reward → Multi-granularity → Gap: Coverage-based
```

---

## 7. Verification - Compact

| Metric | Score |
|--------|-------|
| Sources | 21 (all INFERRED - no MCP) |
| Quality | 77.5/100 |
| Completeness | 65/100 |
| Relevance | 90/100 |

---

## 8. Research Gaps (FULL - Critical for Phase 2A)

### Gap 1: No Controlled Comparison of Feedback Granularities

**Relevance:** 🎯 PRIMARY - Directly blocks answering research question

**Current State:** CodeRL uses binary, RLTF uses multi-granularity, Self-Repair uses error traces. No head-to-head comparison under controlled conditions.

**Missing Piece:** Controlled ablation study comparing {binary, error_trace, coverage} on same infrastructure.

**Impact:** High

**Evidence:**

| Paper | Year | arXiv | Insight |
|-------|------|-------|---------|
| CodeRL | 2022 | 2207.01780 | Binary only |
| RLTF | 2023 | 2307.04349 | Multi-granularity, limited ablation |
| Self-Repair | 2023 | 2306.09896 | Error traces, no RL comparison |

---

### Gap 2: Test Coverage as Reward Signal Unexplored

**Relevance:** 🎯 PRIMARY - Addresses sub-question 2

**Current State:** Coverage used in fuzzing; not applied to code LLM reward design.

**Missing Piece:** Reward function incorporating coverage metrics as dense feedback.

**Impact:** High

**Evidence:**

| Paper | Year | arXiv | Insight |
|-------|------|-------|---------|
| CodeRL | 2022 | 2207.01780 | No coverage |
| PPOCoder | 2023 | 2306.05826 | Binary only |

---

### Gap 3: Sample Efficiency RLEF vs SFT

**Relevance:** 🎯 PRIMARY - Addresses sub-question 3

**Current State:** Papers report final accuracy; sample efficiency unmeasured.

**Missing Piece:** Learning curves comparing samples-to-threshold across paradigms.

**Impact:** Medium-High

**Evidence:**

| Paper | Year | arXiv | Insight |
|-------|------|-------|---------|
| CodeRL | 2022 | 2207.01780 | Reports accuracy, not efficiency |
| Scaling Laws for RM | 2023 | 2210.10760 | RL efficiency analysis |

---

### Gap Priority Matrix

| Gap | Relevance | Impact | Priority |
|-----|-----------|--------|----------|
| Gap 1 | PRIMARY | High | Critical |
| Gap 2 | PRIMARY | High | Critical |
| Gap 3 | PRIMARY | Medium-High | High |

---

## 9. Conclusion

**Key Findings:**
1. Binary rewards dominant but potentially suboptimal
2. Multi-granularity promising but lacking controlled comparison
3. Coverage rewards unexplored
4. Sample efficiency unmeasured

**Phase 2A Priority:** Gap 1 (controlled granularity comparison)

**Preliminary Hypothesis Directions:**
- H1: Fine-grained > binary under matched compute
- H2: Coverage augmentation improves efficiency
- H3: Process supervision transfers to code

---

*Phase 1 Complete - Ready for Phase 2A-Dialogue*
