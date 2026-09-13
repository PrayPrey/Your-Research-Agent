# Targeted Research Report (Compact - Phase 2A Input)

**Research Question:** Does integrating lightweight static analysis feedback during LLM code generation improve functional correctness on existing code benchmarks?

**Date:** 2026-08-19 | **Phase:** 1 - Targeted Research | **Quality Score:** 90/100

---

## Executive Summary

Two 2024-2025 papers demonstrate static analysis feedback improves LLM code quality. Critical gap: no isolated comparison of static-only vs execution-only feedback. Implementation path: Self-Refine + evalplus.

---

## 1. Research Questions

**Primary:** Does static analysis feedback improve functional correctness compared to standard sampling?

**Detailed:**
1. Static vs execution feedback comparison
2. Cost/benefit tradeoff (inference cost vs improvement)
3. Orthogonality of static + execution feedback
4. Cross-language variation (Python vs TypeScript vs Rust)

---

## 2. Top Queries (3 per category)

**Reference Paper:** "static analysis feedback code generation LLM", "iterative refinement code repair", "execution vs static analysis"
**Brainstorm:** "static analysis cheaper than execution", "HumanEval MBPP static analysis", "type inference code repair"
**Direct:** "LLM code generation post-processing repair", "pass@k improvement static analysis", "type system effect code generation"

---

## 3. Archon KB (Compact)

| Pattern | Key Insight |
|---------|-------------|
| [INFERRED] Iterative Repair Loop | Generate → Static Analysis → Error Prompt → Regenerate |
| [INFERRED] Multi-Signal Feedback | Combine static + execution as composite signal |
| [INFERRED] Cost-Aware Sampling | Static analysis as cheap pre-filter |

---

## 4. Academic Papers (Compact)

| Title | Year | arXiv ID | Key Insight |
|-------|------|----------|-------------|
| Static Analysis as Feedback Loop | 2025 | 2508.14419 | **DIRECT HIT** - 40%→13% security issues in 10 iterations |
| Helping LLMs Improve Code Generation | 2024 | 2412.14841 | **DIRECT HIT** - combines testing + static feedback |
| FeedbackEval | 2026 | 2504.06939 | Benchmark for feedback-driven repair |
| StepCoder | 2024 | 2402.01391 | RL with compiler feedback |
| Self-Refine | 2023 | 2303.17651 | Iterative refinement paradigm (~20% improvement) |
| Synchromesh | 2022 | 2201.11227 | Constrained semantic decoding |
| HumanEval Pro/MBPP Pro | 2024 | 2412.21199 | Extended benchmarks |

---

## 5. GitHub Repos (Compact)

| Name | URL | Key Feature |
|------|-----|-------------|
| madaan/self-refine | https://github.com/madaan/self-refine | **OFFICIAL** - pluggable feedback loop |
| Johin2/iterative-code-repair | https://github.com/Johin2/iterative-code-repair | Multi-attempt study framework |
| evalplus | https://github.com/neuralmagic/evalplus | HumanEval+ (80x tests), MBPP+ (35x) |
| amazon-science/mxeval | https://github.com/amazon-science/mxeval | Multi-language benchmarks |

---

## 6. Chain Analysis (Compact)

**Evolution:** CodeRL (2022) → Self-Refine (2023) → StepCoder (2024) → Static Analysis Feedback (2025)

**Key Insight:** All effective approaches use generate→analyze→refine cycle. Gap: no systematic comparison.

---

## 7. Verification (Compact)

- Total sources: 25 (22 verified, 3 inferred)
- Quality: 90/100
- MCP Status: All unavailable, WebSearch fallback used

---

## 8. Research Gaps (FULL - Critical for Phase 2A)

### Gap 1: No Controlled Comparison of Static-Only vs Execution-Only Feedback

**Relevance:** 🎯 PRIMARY - Directly blocks answering research question

**Current State:** Papers use execution feedback (CodeRL, RLPF) OR combine static + execution (Helping LLMs 2024). No isolated static-only study.

**Missing Piece:** Controlled experiment: (A) baseline, (B) static-only, (C) execution-only, (D) combined on same benchmark/model.

**Impact:** HIGH

**Evidence:**
| Paper | arXiv | Insight |
|-------|-------|---------|
| Helping LLMs Improve | 2412.14841 | Combines both, doesn't isolate |
| Static Analysis Feedback Loop | 2508.14419 | Static only, no execution comparison |
| StepCoder | 2402.01391 | Compiler feedback as RL |

| Repo | URL | Feature |
|------|-----|---------|
| madaan/self-refine | https://github.com/madaan/self-refine | Pluggable feedback |
| Johin2/iterative-code-repair | https://github.com/Johin2/iterative-code-repair | Multi-attempt framework |

---

### Gap 2: Unknown Cost-Benefit Tradeoff

**Relevance:** 🎯 PRIMARY - Addresses detailed question Q2

**Current State:** Static analysis assumed cheaper but not quantified.

**Missing Piece:** Cost model: analyzer overhead vs execution overhead vs marginal pass@k gain per $.

**Impact:** HIGH

**Evidence:**
| Paper | arXiv | Insight |
|-------|-------|---------|
| RLPF | 2607.27271 | Stages rewards, no cost analysis |
| Self-Refine | 2303.17651 | ~20% gain, expensive self-feedback |

---

### Gap 3: No Cross-Language Static Analysis Evaluation

**Relevance:** 🔗 SECONDARY - Addresses detailed question Q4

**Current State:** Static analysis studies are Python-only. Stronger type systems (TypeScript, Rust) may benefit more.

**Missing Piece:** Evaluation across: Python (dynamic) vs TypeScript (gradual) vs Rust (strong).

**Impact:** MEDIUM

**Evidence:**
| Repo | URL | Feature |
|------|-----|---------|
| amazon-science/mxeval | https://github.com/amazon-science/mxeval | Multi-language evaluation |
| mraihan-gmu/mHumanEval | https://github.com/mraihan-gmu/mhumaneval-benchmark | Multilingual prompts |

---

### Gap Priority Matrix

| Gap | Relevance | Impact | Priority |
|-----|-----------|--------|----------|
| Gap 1: Static vs Execution Comparison | PRIMARY | High | **Critical** |
| Gap 2: Cost-Benefit Tradeoff | PRIMARY | High | **Critical** |
| Gap 3: Cross-Language Evaluation | SECONDARY | Medium | Important |

### Gap Traceability

- **RQ** → Gap 1 (isolated comparison), Gap 2 (practical value)
- **Q1** → Gap 1 | **Q2** → Gap 2 | **Q3** → Gap 1 | **Q4** → Gap 3

---

## 9. Conclusion (Compact)

**Key Findings:**
1. Direct evidence exists (2 papers show static analysis improves quality)
2. Gap: no isolated comparison study
3. Implementation: Self-Refine + evalplus ready
4. Cost question open

**Phase 2 Readiness:** ✅ READY

**Next:** Phase 2A-Dialogue → Generate hypotheses for Gap 1

---

*Phase 1 Complete | Full report: 01_targeted_research_full.md*
