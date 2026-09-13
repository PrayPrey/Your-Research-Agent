# Targeted Research Report (Compact - Phase 2A Input)

**Date:** 2026-08-18
**Phase:** 1 - Targeted Research Gathering
**Researcher:** Anonymous

---

## Research Questions

### Primary Research Question
Can execution-guided iterative refinement with formal verification feedback (type checking, static analysis, test execution) improve LLM code generation pass rates compared to single-shot generation on standard benchmarks?

### Detailed Research Questions
1. Baseline pass@k performance on HumanEval/MBPP?
2. Static analysis error messages as refinement prompts?
3. Iterative test execution feedback for self-repair?
4. **How do different verification signals compare?** (GAP)
5. **Cost-accuracy tradeoff of refinement vs sampling?** (GAP)

---

## Reference Paper Analysis

| Paper | Key Contribution |
|-------|-----------------|
| Chen et al. 2021 (HumanEval) | pass@k metric, 164-problem benchmark |
| Austin et al. 2021 (MBPP) | 974-problem benchmark |
| Olausson et al. 2023 (Self-Repair) | Self-repair not silver bullet |
| Chen et al. 2023 (Self-Debug) | Execution trace methodology |
| First et al. 2022 (Type-Guided) | Type constraints improve diversity |

---

## Top Search Queries

1. "self-repair code generation iterative refinement"
2. "pass@k improvement through verification feedback"
3. "type-guided code generation LLM constraints"

---

## Academic Literature (Semantic Scholar)

| Paper Title | Year | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|-------|----------|-----------|-------------|
| How Many Tries Does It Take? | 2026 | 7c606ddb4b4f9dbcd1704e8f9b5c162261529b3c | 2604.10508 | 6 | Self-repair +4.9-17.1 pp HumanEval |
| CodeCoR | 2025 | 59efb90a519cf5df0aaadb3778d2d1028d2d666e | 2501.07811 | 38 | Multi-agent 77.13% Pass@1 |
| PerfCodeGen | 2024 | 02c6f69935f57340bd55d2d7575f6d2c900ad3f0 | 2412.03578 | 48 | Runtime feedback for performance |
| DebugRepair | 2026 | 44de3e0b8fd8a2d55edc1287652145fc477cc85a | 2604.19305 | 3 | Runtime traces via debugging |
| TyFlow | 2025 | 0e9cc3463e5e0d2b61f5b1dc88ae4e7abed8cdb5 | 2510.10216 | 1 | Type system internalization |
| LiveCodeBench | 2024 | afe0998d191f3ea8490c7df100a3ffc5dcc62c5e | 2403.07974 | 1994 | Contamination-free benchmark |
| CoTran | 2023 | af8b27589fe82035c1bf705177c6e06e78a181aa | 2306.06755 | 47 | Compiler + symexec feedback |
| Debugging Decay | 2025 | c3ca889c62110b1107028261fb1108bec4ded939 | 2506.18403 | 5 | 60-80% capability loss in 2-3 attempts |

---

## Implementation Resources (Exa)

| Resource | URL | Stars | Language | Key Feature |
|----------|-----|-------|----------|-------------|
| openai/human-eval | https://github.com/openai/human-eval | 3333 | Python | Official HumanEval benchmark |
| evalplus/evalplus | https://github.com/evalplus/evalplus | 1798 | Python | Rigorous extended tests |
| bigcode-evaluation-harness | https://github.com/bigcode-project/bigcode-evaluation-harness | 1029 | Python | Multi-benchmark framework |
| SRepair | https://github.com/GhabiX/SRepair | 79 | Python | $0.029/bug, 300/522 D4J |
| ExpeRepair | https://github.com/ExpeRepair/ExpeRepair | 115 | Python | Dual-memory repair |
| perfcodegen | https://github.com/SalesforceAIResearch/perfcodegen | 44 | Python | Runtime feedback |
| iterative-code-repair | https://github.com/Johin2/iterative-code-repair | 0 | Python | Up to 5 attempts analysis |

---

## Research Gaps (FULL - Critical for Phase 2A)

### Gap 1: Systematic Comparison of Verification Signal Types

**Relevance:** 🎯 PRIMARY - Directly addresses Q4

**Current State:** Type errors (TyFlow), runtime traces (DebugRepair), static analysis (Meta APR) studied in isolation.

**Missing Piece:** Controlled comparison of type errors vs runtime errors vs logical errors vs static analysis on HumanEval/MBPP with same model.

**Impact:** HIGH - Would establish empirical ranking of feedback signal effectiveness

**Evidence:**
| Paper | Insight |
|-------|---------|
| How Many Tries (2026) | Assertion errors hardest (~45%), syntax easiest |
| TyFlow (2025) | Type constraints improve functional correctness |
| DebugRepair (2026) | Runtime traces outperform error messages |

---

### Gap 2: Cost-Accuracy Tradeoff Analysis

**Relevance:** 🎯 PRIMARY - Directly addresses Q5

**Current State:** Token costs reported ($0.029/bug SRepair, 11.8 iterations Meta APR) but no unified model.

**Missing Piece:** When does refinement beat resampling? Tokens-per-percentage-point improvement?

**Impact:** HIGH - Practical deployment guidance

**Evidence:**
| Paper | Insight |
|-------|---------|
| Debugging Decay (2025) | 60-80% capability loss in 2-3 attempts |
| Agentic APR (2025) | 42.3% solve, 11.8 avg iterations |

---

### Gap 3: Static Analysis Integration

**Relevance:** 🔗 SECONDARY - Addresses Q2

**Current State:** Runtime feedback well-studied; static analysis used in production but academic evaluation limited.

**Missing Piece:** Does static analysis (mypy, pylint) as refinement prompt enable "fail-fast" before execution?

**Impact:** MEDIUM

---

## Gap Priority Matrix

| Gap | Title | Impact | Priority |
|-----|-------|--------|----------|
| 1 | Verification Signal Comparison | HIGH | Critical |
| 2 | Cost-Accuracy Tradeoff | HIGH | Critical |
| 3 | Static Analysis Integration | MEDIUM | Important |

---

## Phase 2A Readiness

✅ **HIGH** - Ready for hypothesis generation

- Clear gaps identified (3 total, 2 primary)
- Benchmarks available (HumanEval, MBPP, evalplus)
- Implementation references (7 repos)
- Theoretical foundation (8 papers)

**Primary Hypothesis Target:** Gap 1 (Verification Signal Type Comparison)

---

*Phase: 1 - Targeted Research (Compact)*
*Full report: 01_targeted_research_full.md*
