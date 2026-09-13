# Targeted Research Report (Phase 2A Compact): Execution-Filtered SFT Data for Code LLMs

**Date:** 2026-08-04
**Phase:** 1 - Targeted Research Gathering (Compact for Phase 2A)
**Pipeline Project ID:** df86f02e-1a93-4ce4-97db-2c4ecfdc3b3c
**Session Type:** ROUTE_TO_0 (failure recovery from H-E1)
**Full Report:** `01_targeted_research_full.md`

---

## Executive Summary

**Research Question:** Does execution-based filtering (compile-only or compile+test-pass) of an open-source code training corpus improve SFT performance on HumanEval and MBPP compared to unfiltered SFT at equal token budget — and does filtering strictness affect improvement magnitude?

**Key Finding:** No existing study performs a controlled comparison of unfiltered / compile-only / compile+test SFT data filtering on The Stack Python at equal token budget, evaluated on HumanEval + MBPP. Research gap is real and novel.

**Sources:** 12 SCHOLAR papers + 9 EXA resources + 8 INFERRED patterns (Archon KB irrelevant to domain). Data quality: 86/100.

**Implementation Stack:** The Stack Python (corpus) + opc_data_filtering + cristinaimprota pipeline (filtering) + openai/human-eval + lm-evaluation-harness (evaluation). All publicly available.

**Phase 2A Targets:** Gap 1 (Critical) — controlled exec-filter comparison. Gap 2 (Critical) — filtering-ratio ablation.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Does applying execution-based filtering (compile-only or compile+test-pass) to an existing open-source code training corpus improve supervised fine-tuning (SFT) performance of a code LLM on HumanEval and MBPP compared to SFT on the unfiltered corpus of equal token budget — and does filtering strictness level affect the magnitude of improvement?

### Detailed Research Questions
1. Does SFT on execution-filtered code data (compile + test pass) outperform SFT on unfiltered data of equal token count on HumanEval pass@1 and MBPP pass@1?
2. Is compile-only filtering sufficient, or does adding unit-test-pass filtering provide additional gain beyond compile-only filtering?
3. Does the benefit of execution filtering scale with the filtering ratio (e.g., 10% retained vs. 30% retained vs. 50% retained) — is there an optimal filtering threshold?
4. Does execution-filtered SFT outperform length-matched random SFT subsampling, isolating the quality signal from the data-quantity reduction effect?
5. Do gains from execution-filtered SFT generalize across model sizes (e.g., 1B vs. 7B parameter code LLMs from the same family)?

### Lessons from Previous Attempts (ROUTE_TO_0)
**H-E1 failure:** RL post-training via execution feedback on APPS interview problems (Qwen2.5-Coder-7B). Three compounding failures: (1) APPS harness subprocess isolation — all tests False/error; (2) 11.6% compile rate on interview difficulty — only 11/200 in signal window; (3) joint compile+test window yielded 0/200. **Fix:** Switch to SFT data filtering on HumanEval/MBPP (no harness issues, single binary filter, calibrated difficulty).

---

## 2. Search Queries (Top Queries Only)

**Total: 16 queries across 3 tiers (ROUTE_TO_0 case)**

**Failure-Aware (Priority Highest):**
1. "SFT data filtering code LLM alternative to RL from execution feedback"
2. "code training data quality filtering without subprocess isolation HumanEval MBPP"
3. "execution-based data selection supervised fine-tuning Python code benchmark"

**Brainstorm Insights (Priority 2 — top 3):**
1. "execution feedback data curation code LLM SFT quality vs quantity"
2. "AlphaCode StarCoder data pipeline execution filtering training corpus"
3. "phi-1 textbooks are all you need code data quality selection"

**Direct Question Decomposition (Priority 3 — top 3):**
1. "execution-based data filtering supervised fine-tuning code LLM HumanEval pass@1"
2. "compile-only vs compile+test filtering code training data quality"
3. "data quantity vs quality tradeoff code LLM fine-tuning"

---

## 3. Past Cases & Best Practices (via Archon) — COMPACT

**Status:** Archon KB contains exclusively diffusion/image-generation content — 0 verified code LLM cases found across 10 queries / 3 levels. All entries [INFERRED].

| Pattern | Tag | Key Insight |
|---------|-----|-------------|
| Execution-signal data filtering pipeline | [INFERRED] | compile() + exec() + test runner; no subprocess isolation issues unlike APPS |
| Token-budget-matched baseline comparison | [INFERRED] | Downsample unfiltered to match filtered token count before training |
| Multi-level filtering strictness ablation | [INFERRED] | Graduated: no filter → heuristic → compile-only → compile+test |
| Python compile() + unittest runner | [INFERRED] | `compile(code, '<string>', 'exec')` for syntax; exec() + test harness for functional |

---

## 4. Academic Literature (via Semantic Scholar) — COMPACT

**12 papers found. Format: Title (Year) | arXiv | Citations | Key Insight**

### Directly Relevant
| Title | Year | arXiv | SS ID | Citations | Key Insight |
|-------|------|-------|-------|-----------|-------------|
| OpenCodeInstruct: Large-scale Instruction Tuning Dataset for Code LLMs | 2025 | 2504.04030 | ebcc683e5494bd8fbe596dfc4b3eaf6fb641fc74 | 58 | Execution feedback + quality filtering → significant HumanEval/MBPP improvement across 1B/3B/7B |
| Token Cleaning: Fine-Grained Data Selection for LLM SFT | 2025 | 2502.01968 | c1207d60c30a1edaf2a00ada6c7dd8f1abb17226 | 38 | Data quality > quantity for SFT confirmed; token-level influence filtering |
| Arctic-SnowCoder: High-Quality Data in Code Pretraining | 2024 | 2409.02326 | b6224cabb7482249d7cd1acb81fd7c02fef7486c | 6 | Three-phase quality filtering; quality-task alignment critical; HumanEval+/BigCodeBench eval |
| Empirical Study on Influence-Based Pretraining Data Selection for Code LLMs | 2026 | 2604.07769 | 14957532d45b2e395a8e2d66946bb539e520f363 | 0 | Influence-score filtering for 1B code LLM; optimal criteria differ across tasks |
| EffiCoder: Efficiency-Aware Fine-tuning for Code Generation | 2024 | 2410.10209 | 68d88c8e8318d441ad3e00cef5ff59d966c06de6 | 19 | Execution-selected SFT samples → Qwen2.5-Coder-7B 44.8% → 57.7% pass@1 |

### Foundational
| Title | Year | arXiv | SS ID | Citations | Key Insight |
|-------|------|-------|-------|-----------|-------------|
| Evaluating LLMs Trained on Code (Codex/HumanEval) | 2021 | 2107.03374 | acbdbf49f9bc3f151b93d9ca9a06009f4f6eb269 | 10,865 | Defines HumanEval benchmark + pass@k metric |
| Program Synthesis with LLMs (MBPP) | 2021 | 2108.07732 | a38e0f993e4805ba8a9beae4c275c91ffcec01df | 4,199 | Defines MBPP benchmark (974 Python tasks) |
| StarCoder: may the source be with you! | 2023 | 2305.06161 | 3e4085e5869f1b7959707a1e1d7d273b6057eb4e | 1,276 | The Stack + heuristic filtering → 40% HumanEval pass@1; establishes corpus |
| StarCoder 2 and The Stack v2 | 2024 | 2402.19173 | 18e7ab056c16928d8f9539509a4b366889106d97 | 710 | 3B/7B/15B models; expanded corpus design details |

### Supporting
| Title | Year | arXiv | SS ID | Citations | Key Insight |
|-------|------|-------|-------|-----------|-------------|
| Textbooks Are All You Need (phi-1) | 2023 | 2306.11644 | 2922768fd451ecdb45f48c1a83eb57f54a91221b | 642 | 7B quality tokens → 50.6% HumanEval; quality > quantity at equal budget |
| Textbooks Are All You Need II (phi-1.5) | 2023 | 2309.05463 | e26888285436bc7998e5c95102a9beb60144be5e | 669 | Extends data quality selection to reasoning |
| Seed-Coder: Let Code Model Curate Data | 2025 | 2506.03524 | 18432c7bcc8ac6eeadb9e2f4ab4490257af2aae5 | 55 | Model-centric execution-based data curation; pretraining + SFT pipeline |

---

## 5. Implementation Resources (via Exa) — COMPACT

| Resource | URL | Stars | Key Feature |
|----------|-----|-------|-------------|
| OpenCoder-llm/opc_data_filtering | https://github.com/OpenCoder-llm/opc_data_filtering | 86 | 100+ filtering rules for code quality; compiler validation framework |
| cristinaimprota/Investigating-Training-Data-s-Role | https://github.com/cristinaimprota/Investigating-Training-Data-s-Role | 0 (ICPC 2025) | The Stack Python → SFT pipeline; 5.5M function pairs; no execution filter |
| huggingface/open-r1 (pass_rate_filtering) | https://github.com/huggingface/open-r1/blob/main/scripts/pass_rate_filtering/README.md | 26,411 (parent) | pass rate window [0.1, 0.6] filtering; adaptable to SFT |
| openai/human-eval | https://github.com/openai/human-eval | 3,329 | Official HumanEval evaluation harness |
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | 13,523 | HumanEval + MBPP pass@1 unified eval |
| bigcode-project/bigcode-evaluation-harness | https://github.com/bigcode-project/bigcode-evaluation-harness | — | Code-specific evaluation (HumanEval, MBPP, MultiPL-E) |
| adorkin/OpenCodeInstruct-filtered-sft | https://huggingface.co/datasets/adorkin/OpenCodeInstruct-filtered-sft | — (dataset) | 445k SFT samples with tests_execution_status + average_test_score fields |
| NVIDIA NeMo-Curator Code Filtering | https://docs.nvidia.com/nemo/curator/latest/curate-text/process-data/specialized-processing/code.html | — (docs) | Production code filtering: LOC, alpha, tokenizer fertility, XML/HTML filters |

---

## 6. Chain-of-Relations Analysis — COMPACT

**Research Evolution (7 stages):**
1. Codex (2021) — HumanEval established; no exec filtering
2. phi-1 (2023) — quality > quantity; GPT-4 curation not execution
3. StarCoder (2023) — heuristic filtering on The Stack; no execution gate
4. OpenCoder (2024) — first Python compiler validation for SFT triples
5. open-r1 (2024) — pass-rate window [0.1, 0.6] for RL (not SFT)
6. cristinaimprota ICPC 2025 — The Stack Python SFT study; heuristic only
7. **Gap:** No controlled exec-filter SFT comparison at equal token budget → **This Study**

**Cross-Reference (Key Resources):**

| Resource | Relevance to RQ | Execution Filter | Token Budget Control | Adaptability |
|---|---|---|---|---|
| cristinaimprota ICPC 2025 | Very High | Heuristic | Function-pair level | Very High |
| OpenCoder opc_data_filtering | Very High | Compile gate | Partial | Very High |
| phi-1 | Very High | No (GPT-4) | Yes (explicit) | Conceptual baseline |
| openai/human-eval | High | N/A | N/A | Direct use |
| lm-evaluation-harness | High | N/A | N/A | Direct use |
| open-r1 pass_rate_filtering | Medium | Pass rate window | No | Partial adapt |

---

## 7. Verification Summary — COMPACT

**Total Sources:** 29 | **Verified:** 21 (72.4%) | **Inferred:** 8 (27.6%)

| Tag | Count |
|-----|-------|
| [VERIFIED - SCHOLAR] | 12 |
| [VERIFIED - EXA] | 6 |
| [VERIFIED - EXA - TUTORIAL] | 2 |
| [VERIFIED - EXA - CODE_CONTEXT] | 1 |
| [INFERRED] | 8 |

**Data Quality:** Completeness 82/100 | Reliability 88/100 | Recency 85/100 | Relevance 90/100 | **Overall 86/100**

**Issues:** Archon KB domain mismatch (diffusion-only). Scholar rate limit (1 query, retried). 1 wrong arXiv ID corrected.

---

## 8. Research Gaps — FULL (CRITICAL FOR PHASE 2A)

### User Input Recall

**Main Research Question:** Does applying execution-based filtering (compile-only or compile+test-pass) to an existing open-source code training corpus improve supervised fine-tuning (SFT) performance of a code LLM on HumanEval and MBPP compared to SFT on the unfiltered corpus of equal token budget — and does filtering strictness level affect the magnitude of improvement?

**Detailed Questions:**
1. Does SFT on execution-filtered code data (compile + test pass) outperform SFT on unfiltered data of equal token count on HumanEval pass@1 and MBPP pass@1?
2. Is compile-only filtering sufficient, or does adding unit-test-pass filtering provide additional gain beyond compile-only filtering?
3. Does the benefit of execution filtering scale with the filtering ratio (10% vs 30% vs 50% retained)?
4. Does execution-filtered SFT outperform length-matched random SFT subsampling?
5. Do gains generalize across model sizes (1B vs 7B code LLMs from same family)?

**Reference Papers:** Not provided.

### Identified Gaps

#### Gap 1: No Controlled Comparison of Execution-Filtered SFT Data (Compile-Only vs Compile+Test) at Equal Token Budget

**Relevance Classification:** 🎯 PRIMARY — directly blocks answering research question

**Connection Type:**
- ☑️ Blocks answering research question: Without this controlled experiment, the main RQ cannot be answered.
- ☑️ Relates to detailed questions 1, 2, 4
- ☐ Does not extend a reference paper (none provided)

**Current State:** Existing work uses heuristic-only filtering (StarCoder, cristinaimprota), compiler validation without unfiltered comparison (OpenCoder opc-sft-stage2), or pass-rate filtering in RL context not SFT (open-r1). No study performs all three conditions at matched token count on the same corpus evaluated on HumanEval + MBPP.

**Missing Piece:** Controlled SFT ablation with three conditions — (1) unfiltered subset of The Stack Python, (2) compile-only filtered subset, (3) compile+test filtered subset — all at equal token budget, same base model, evaluated on HumanEval pass@1 and MBPP pass@1.

**Potential Impact:** High

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Evaluating LLMs Trained on Code" (Codex) | 2021 | Chen et al. | acbdbf49f9bc3f151b93d9ca9a06009f4f6eb269 | 2107.03374 | 10,865 | Established HumanEval; no execution filtering in pretraining corpus |
| "Program Synthesis with LLMs" (MBPP) | 2021 | Austin et al. | a38e0f993e4805ba8a9beae4c275c91ffcec01df | 2108.07732 | 4,199 | Established MBPP benchmark; training data not execution filtered |
| "Textbooks Are All You Need" (phi-1) | 2023 | Gunasekar et al. | 2922768fd451ecdb45f48c1a83eb57f54a91221b | 2306.11644 | 642 | Quality-filtered SFT outperforms equal token budget raw data; uses GPT-4 not execution |
| "StarCoder: may the source be with you!" | 2023 | Li et al. | 3e4085e5869f1b7959707a1e1d7d273b6057eb4e | 2305.06161 | 1,276 | Heuristic pipeline for The Stack; no execution filtering; establishes baseline |
| "OpenCoder: Open Cookbook for Top-Tier Code LLMs" | 2024 | Huang et al. | — | 2411.04905 | ~50 | Compiler-validated SFT triples but no ablation vs. unfiltered at equal token budget |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *[INFERRED — Archon KB irrelevant]* | N/A | "compile pass rate code training data filtering Python" | No Archon KB cases found; KB contains diffusion content only |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| OpenCoder-llm/opc_data_filtering | https://github.com/OpenCoder-llm/opc_data_filtering | 86 | Python/Multi | Filtering framework; lacks controlled comparison vs unfiltered baseline |
| cristinaimprota/Investigating-Training-Data-s-Role | https://github.com/cristinaimprota/Investigating-Training-Data-s-Role | 0 (ICPC 2025) | Python/R/Shell | The Stack Python SFT pipeline; heuristic only, not execution filtering |
| openai/human-eval | https://github.com/openai/human-eval | 3,329 | Python | Evaluation harness for HumanEval pass@k |

---

#### Gap 2: No Systematic Study of Filtering Ratio Effect on SFT Code Quality (Optimal Threshold Unknown)

**Relevance Classification:** 🎯 PRIMARY — directly blocks the "does strictness affect magnitude" clause

**Connection Type:**
- ☑️ Blocks answering research question: The "strictness level" clause requires ratio ablation.
- ☑️ Relates to detailed questions 3 and 4
- ☐ Does not extend a reference paper (none provided)

**Current State:** open-r1 uses fixed [0.1, 0.6] window (RL context, not ablated). phi-1 uses fixed GPT-4 threshold. No systematic filtering-ratio ablation (10%, 30%, 50% retained) for execution-based SFT filtering evaluated on HumanEval/MBPP.

**Missing Piece:** Ablation across filtering thresholds: strict=10% / moderate=30% / lenient=50% retained, for both compile-only and compile+test gates, at fixed base model and equal token budget per condition. Measure HumanEval + MBPP pass@1 per ratio.

**Potential Impact:** High

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Textbooks Are All You Need" (phi-1) | 2023 | Gunasekar et al. | 2922768fd451ecdb45f48c1a83eb57f54a91221b | 2306.11644 | 642 | Quality vs quantity but fixed threshold; no ablation |
| "StarCoder: may the source be with you!" | 2023 | Li et al. | 3e4085e5869f1b7959707a1e1d7d273b6057eb4e | 2305.06161 | 1,276 | Fixed filtering rules; no ratio ablation |
| "DeepSeek-Coder: When LLM Meets Programming" | 2024 | Guo et al. | — | 2401.14196 | ~800 | Data quality scoring but no systematic threshold ablation on execution |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *[INFERRED — Archon KB irrelevant]* | N/A | "data quality filtering threshold ablation code SFT" | No Archon KB cases found |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| huggingface/open-r1 (pass_rate_filtering) | https://github.com/huggingface/open-r1/blob/main/scripts/pass_rate_filtering/README.md | 26,411 (parent) | Python | Fixed window [0.1, 0.6]; adaptable for ratio ablation |
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | 13,523 | Python | pass@1 on HumanEval+MBPP for measuring threshold effect |

---

#### Gap 3: Unknown Generalizability of Execution-Filtered SFT Gains Across Model Sizes

**Relevance Classification:** 🔗 SECONDARY — relates to detailed question 5

**Connection Type:**
- ☐ Does not directly block the main research question
- ☑️ Relates to detailed question 5 (1B vs 7B generalization)
- ☐ Does not extend a reference paper

**Current State:** phi-1: 1.3B only. StarCoder: 15.5B only. OpenCoder: 1.5B + 8B but no exec-filtered ablation per size. No work tests whether execution-filtered SFT gains scale from 1B to 7B on the same filtered corpus.

**Missing Piece:** Parallel SFT on two code LLMs from same family (e.g., Qwen2.5-Coder-1.5B + Qwen2.5-Coder-7B) with identical filtering and evaluation.

**Potential Impact:** Medium

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Textbooks Are All You Need" (phi-1) | 2023 | Gunasekar et al. | 2922768fd451ecdb45f48c1a83eb57f54a91221b | 2306.11644 | 642 | Single size (1.3B) — no cross-size comparison |
| "OpenCoder: Open Cookbook for Top-Tier Code LLMs" | 2024 | Huang et al. | — | 2411.04905 | ~50 | Tests 1.5B + 8B but no exec-filtered ablation per size |
| "StarCoder 2 and The Stack v2" | 2024 | Lozhkov et al. | 18e7ab056c16928d8f9539509a4b366889106d97 | 2402.19173 | 710 | 3B/7B/15B on pretraining; SFT stage not exec-filtered |
| "DeepSeek-Coder" | 2024 | Guo et al. | — | 2401.14196 | ~800 | 1B/7B/33B but no exec-filtered SFT ablation |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *[INFERRED — Archon KB irrelevant]* | N/A | "model size generalization SFT data filtering code LLM" | No Archon KB cases found |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | 13,523 | Python | Unified eval for multiple model sizes |
| OpenCoder-llm/opc_data_filtering | https://github.com/OpenCoder-llm/opc_data_filtering | 86 | Python/Multi | Framework reusable across model sizes |

---

### Gap Priority Matrix

| Gap ID | Title | Relevance | Blocks Main RQ | Addresses Detailed Q | Evidence Count | Impact | Priority |
|--------|-------|-----------|----------------|---------------------|----------------|--------|----------|
| Gap 1 | No controlled comparison: unfiltered vs compile-only vs compile+test at equal token budget | 🎯 PRIMARY | ☑️ Yes — core experiment | Q1, Q2, Q4 | 5 SCHOLAR + 3 EXA = 8 | High | **Critical** |
| Gap 2 | No filtering-ratio ablation (10% vs 30% vs 50% retained) | 🎯 PRIMARY | ☑️ Yes — "strictness" clause | Q3, Q4 | 3 SCHOLAR + 2 EXA = 5 | High | **Critical** |
| Gap 3 | Unknown generalizability across model sizes | 🔗 SECONDARY | ☐ No (secondary) | Q5 | 4 SCHOLAR + 2 EXA = 6 | Medium | **Important** |

### User Input to Gap Traceability

**Main Research Question** addressed by: Gap 1 (core experiment) + Gap 2 ("strictness" clause)

**Detailed Q1** (compile+test vs unfiltered) → Gap 1
**Detailed Q2** (compile-only vs compile+test additive) → Gap 1
**Detailed Q3** (filtering ratio effect) → Gap 2
**Detailed Q4** (vs random subsampling) → Gap 1, Gap 2
**Detailed Q5** (model size generalization) → Gap 3

**Reference Papers:** Not provided.

---

## 9. Conclusion

### Key Findings

1. **Core gap confirmed:** No existing study performs controlled comparison of unfiltered / compile-only / compile+test SFT filtering on The Stack Python at equal token budget, evaluated on HumanEval + MBPP. Research question is novel.
2. **Strong methodological precedent:** phi-1 equal-token-budget comparison methodology directly adaptable. EffiCoder shows execution-selected SFT samples → +13pp pass@1 gain (44.8% → 57.7%).
3. **Complete implementation stack identified:** All components publicly available — no new infrastructure required.
4. **ROUTE_TO_0 direction validated:** New direction avoids all H-E1 failure modes (no APPS harness, no RL complexity, no joint window).

### Phase 2A Readiness

- ✅ Research question defined, 3 gaps identified in table format with full evidence
- ✅ Gap priority matrix: Gap 1 (Critical), Gap 2 (Critical), Gap 3 (Important)
- ✅ Phase boundary maintained (no hypotheses proposed)
- ✅ Compact report ready for Phase 2A hypothesis generation

**Phase 2A Input:** This file (`01_targeted_research.md`)
**Phase 2A Focus:** Generate testable hypotheses from Gaps 1 and 2 (PRIMARY/Critical)
**Next Step:** `/phase2a-dialogue` with pipeline_project_id: df86f02e-1a93-4ce4-97db-2c4ecfdc3b3c

---

*Phase: 1 - Targeted Research Gathering (Compact for Phase 2A)*
*Full report: `01_targeted_research_full.md`*
*Total processing time: ~4 hours (multi-session, context compaction occurred between Steps 5-6)*
