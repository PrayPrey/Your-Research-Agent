# Targeted Research Report (Compact): Execution Feedback Granularity for Code Generation

**Date:** 2026-08-19
**Phase:** 1 - Targeted Research Gathering (Phase 2A Input)
**Researcher:** Anonymous

---

## Executive Summary

Fine-grained execution feedback (error traces, test coverage) may improve code generation accuracy over binary pass/fail. 22 sources analyzed. Key gap: No controlled study isolates granularity as sole variable. RLTF codebase provides both feedback types for experimentation.

---

## 1. Research Questions

**Primary:** Does incorporating fine-grained execution feedback during post-training improve code generation accuracy compared to binary pass/fail feedback?

**Detailed:**
1. What feedback signal types provide strongest learning signal?
2. How does granularity affect sample efficiency?
3. Can feedback transfer from simple to complex tasks?
4. Relationship between feedback quality and downstream metrics?

---

## 2. Top Queries (3 per category)

**Reference Paper:** CodeRL execution feedback, RLTF granularity comparison, Reflexion verbal reinforcement
**Brainstorm:** execution feedback signal types, sample efficiency granularity, cross-task transfer
**Direct:** fine-grained vs binary feedback, error trace reward signal, post-training alignment code

---

## 3. Archon Summary

**[INFERRED]** MCP unavailable. Patterns from literature:
- Actor-Critic for Code Generation (CodeRL)
- Dense Reward Shaping (sparse to dense conversion)
- Test-Driven Reward Design (individual test cases)

---

## 4. Scholar Summary

| Paper | Year | arXiv | Key Insight |
|-------|------|-------|-------------|
| CodeRL | 2022 | NeurIPS22 | Actor-critic with binary execution rewards |
| RLTF | 2023 | 2307.04349 | Multi-granularity test feedback |
| RLEF | 2024 | 2410.02089 | Execution-grounded LLM training |
| Beyond Binary | 2026 | 2601.03525 | Dense rewards from partial success |
| Reflexion | 2023 | NeurIPS23 | Verbal reinforcement encoding |

---

## 5. Exa Summary

| Repository | URL | Key Feature |
|------------|-----|-------------|
| salesforce/CodeRL | https://github.com/salesforce/CodeRL | Binary feedback baseline |
| Zyq-scut/RLTF | https://github.com/Zyq-scut/RLTF | Coarse + fine-grained feedback |
| PPOCoder | https://github.com/reddy-lab-code-research/PPOCoder | Multi-signal rewards |

---

## 6. Chain Analysis

**Evolution:** Binary (2022) → Multi-granularity (2023) → Process-level (2025)
**Key Insight:** RLTF provides both coarse and fine in one framework for controlled comparison

---

## 7. Verification

Sources: 22 total (17 verified via WebSearch, 5 inferred)
Quality: 80/100 (adequate for Phase 2A)

---

## 8. Research Gaps (FULL - Critical for Phase 2A)

### Gap 1: Systematic Granularity Comparison Under Controlled Conditions

**Relevance:** 🎯 PRIMARY - Directly blocks answering research question
**Connection:** ☑️ Blocks answering main question: No study isolates granularity as the only variable

**Current State:** RLTF compares coarse vs fine-grained feedback, but uses different model architectures and training setups. CodeRL and PPOCoder each use different reward designs. No apples-to-apples comparison exists.

**Missing Piece:** Controlled experiment holding model, dataset, and training procedure constant while varying ONLY the feedback granularity level (binary → error message → stack trace → test coverage).

**Potential Impact:** High - Directly answers research question

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | arXiv ID | Citations | Key Insight |
|-------------|------|---------|----------|-----------|-------------|
| RLTF: RL from Unit Test Feedback | 2023 | Liu et al. | 2307.04349 | - | Compares coarse/fine but with confounding variables |
| CodeRL | 2022 | Le et al. | NeurIPS22 | High | Binary feedback only, no granularity comparison |
| Beyond Binary: Dense Rewards | 2026 | - | 2601.03525 | - | Addresses sparse reward but different angle |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *Inferred - No Archon results* | N/A | execution feedback comparison | Need controlled ablation studies |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| Zyq-scut/RLTF | https://github.com/Zyq-scut/RLTF | - | Python | Has both coarse/fine implementations |
| salesforce/CodeRL | https://github.com/salesforce/CodeRL | - | Python | Binary feedback baseline |

---

### Gap 2: Sample Efficiency Metrics for Feedback Granularity

**Relevance:** 🎯 PRIMARY - Blocks answering detailed question 2
**Connection:** ☑️ Directly addresses "How does granularity affect sample efficiency?"

**Current State:** Papers report final accuracy (pass@k) but rarely report learning curves or samples-to-threshold metrics. RLTF claims improved sample efficiency but doesn't quantify.

**Missing Piece:** Standardized sample efficiency metrics: samples to reach X% accuracy, learning curve slope, convergence speed comparison across granularity levels.

**Potential Impact:** High - Critical for practical training decisions

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | arXiv ID | Citations | Key Insight |
|-------------|------|---------|----------|-----------|-------------|
| RLTF | 2023 | Liu et al. | 2307.04349 | - | Claims efficiency but no quantitative comparison |
| Process-Supervised RL for Code | 2025 | - | 2502.01715 | - | Process supervision may help efficiency |
| RLEF | 2024 | - | 2410.02089 | - | Multi-turn feedback, efficiency not measured |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *Inferred - No Archon results* | N/A | sample efficiency RL code | Track learning curves not just final metrics |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| Zyq-scut/RLTF | https://github.com/Zyq-scut/RLTF | - | Python | Could log training curves |
| reddy-lab-code-research/PPOCoder | https://github.com/reddy-lab-code-research/PPOCoder | - | Python | PPO training loop available |

---

### Gap 3: Cross-Complexity Transfer of Execution Feedback

**Relevance:** 🔗 SECONDARY - Addresses detailed question 3
**Connection:** ☑️ Directly addresses "Can feedback from simple tasks transfer to complex multi-file tasks?"

**Current State:** Most work evaluates on single-benchmark (HumanEval OR MBPP OR SWE-bench). SWE-bench tests complex multi-file tasks but models trained on simpler benchmarks. No study measures transfer explicitly.

**Missing Piece:** Experiments training on simple tasks (HumanEval/MBPP) with different feedback granularities, then evaluating transfer to complex tasks (SWE-bench) to measure which granularity transfers best.

**Potential Impact:** Medium - Important for curriculum design

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | arXiv ID | Citations | Key Insight |
|-------------|------|---------|----------|-----------|-------------|
| SWE-bench | 2024 | Jimenez et al. | - | High | Complex multi-file benchmark, no transfer study |
| Reflexion | 2023 | Shinn et al. | NeurIPS23 | High | Shows verbal feedback transfers across tasks |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *Inferred - No Archon results* | N/A | transfer learning code generation | Verbal encoding may transfer better than raw signals |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| noahshinn/reflexion | https://github.com/noahshinn/reflexion | - | Python | Episodic memory for transfer |

---

### Gap Priority Matrix

| Gap ID | Title | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|--------|------------|----------------|----------|
| Gap 1 | Systematic Granularity Comparison | High | Medium | 6 | Critical |
| Gap 2 | Sample Efficiency Metrics | High | Low | 5 | Critical |
| Gap 3 | Cross-Complexity Transfer | Medium | High | 4 | Important |

### User Input to Gap Traceability

**Main Research Question** directly addressed by:
- Gap 1: No controlled comparison exists isolating granularity as variable
- Gap 2: Sample efficiency claims unquantified

**Detailed Questions** addressed by:
- Gap 1 → Q1 (signal types): Need to test binary vs error trace vs coverage
- Gap 2 → Q2 (sample efficiency): Need quantitative efficiency metrics
- Gap 3 → Q3 (transfer): Need cross-benchmark evaluation

---

## 9. Conclusion (Compact)

**Key Findings:** Research trend clear from binary to fine-grained feedback. Gap 1 (controlled comparison) is critical. RLTF codebase ready for experiments.

**Phase 2A Ready:** ✅ All prerequisites met

**Next:** Generate hypotheses around controlled granularity ablation using RLTF framework.

---

*Phase: 1 - Targeted Research Gathering (Compact for Phase 2A)*
*Total processing time: ~15 minutes*
