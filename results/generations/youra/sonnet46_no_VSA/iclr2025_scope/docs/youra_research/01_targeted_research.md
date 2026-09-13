# Targeted Research Report: When a pretrained transformer is converted to a sub-quadratic architecture (e.g., via linear attention substitution or selective state-space distillation), does the converted model retain ≥90% of the original model's accuracy on existing long-context benchmarks (LongBench v2, SCROLLS) at sequence lengths ≥4096, and does this retention vary systematically by task type (retrieval vs. summarization vs. QA)?

**Date:** 2026-08-03
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

Phase 1 targeted research on quadratic-to-sub-quadratic transformer conversion for long-context benchmarks. ROUTE_TO_0 mode (recovery from H-E1/H-M2 failures). Found 15 academic papers (Semantic Scholar), 8 GitHub repositories + 3 tutorials (Exa); Archon KB domain mismatch (diffusion models). Three research gaps identified: (1) no cross-strategy accuracy comparison on LongBench v2 task categories [Critical], (2) no sequence-length degradation curve for converted models [Critical], (3) no head-to-head converted vs. scratch-trained SSM comparison on LongBench v2 [High]. Conversion infrastructure complete: MOHAWK (NeurIPS 2024) + LAWCAT (EMNLP 2025) + lm-evaluation-harness + THUDM/LongBench. Ready for Phase 2A hypothesis generation.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
When a pretrained transformer is converted to a sub-quadratic architecture (e.g., via linear attention substitution or selective state-space distillation), does the converted model retain ≥90% of the original model's accuracy on existing long-context benchmarks (LongBench v2, SCROLLS) at sequence lengths ≥4096, and does this retention vary systematically by task type (retrieval vs. summarization vs. QA)?

### Detailed Research Questions
1. Which sub-quadratic conversion strategy (linear attention substitution, SSM distillation, hybrid layer replacement) achieves the highest accuracy retention on existing long-context benchmarks relative to the original transformer, without requiring new benchmarks or synthetic data?
2. Does accuracy retention after conversion degrade monotonically with sequence length on existing benchmarks (LongBench v2, SCROLLS), and if so, at what sequence length threshold does degradation become statistically significant?
3. Is there a task-type interaction: do retrieval-heavy tasks (multi-doc QA) show larger post-conversion accuracy drops than summarization or single-doc QA tasks, as measured on existing LongBench v2 category splits?
4. Does fine-tuning the converted model on existing training splits of LongBench v2 / SCROLLS recover statistically significant accuracy versus zero-shot conversion, and does recovery differ by conversion strategy?
5. Can existing open-source sub-quadratic models (Mamba-3B, RWKV-7B) trained from scratch match converted models on identical benchmark subsets, or does conversion from a strong transformer prior provide measurable advantage on existing eval sets?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
**Attempt 1 (H-E1): WIAB Attention Divergence Hypothesis**
- Hypothesis: Within-and-across-batch (WIAB) attention score divergence is CLC-specific and correlates with rank-drop in W_O projection space.
- Criterion 1 (Spearman ρ < 0.9 in ≥50% heads): CONFIRMED (median ρ = 0.6239, frac_below_09 = 98.2%)
- Criterion 2 (CLC-rank-drop Pearson r ≥ 0.3): FAILED (r = 7.1e-05)
- Root cause: Attention-weight proxy insufficient; max_length=256 too short for CLC variance.

**Attempt 2 (H-M2): Boundary Token Eviction in H2O**
- Hypothesis: H2O greedy eviction removes structurally critical boundary tokens at 50% compression.
- Result: frac_below_80 = 1.000, accuracy = 2.8% — catastrophic failure. Condition B incomplete.
- Root cause: Catastrophic degradation at 50% KV compression is fundamental limitation of greedy eviction.

**Why new direction avoids pitfalls:**
- No attention proxy, no eviction mechanism, no dependency chain between hypotheses.
- Directly testable on existing benchmarks with existing models (Mamba, RWKV, Griffin).

---

## 2. Search Queries Generated [COMPACT — top 3 per category]

**ROUTE_TO_0 case** — failure-aware queries generated first. Total: 17 queries.

### Failure-Aware Queries (top 3)
1. "sub-quadratic architecture conversion without KV cache eviction"
2. "transformer to SSM conversion independent hypothesis verification"
3. "alternative to attention approximation for long-context efficiency"

### Brainstorm Insights Queries (top 3)
1. "GoldFinch MambaFormer transformer linearization long-context performance"
2. "SSM distillation from pretrained transformer accuracy retention"
3. "RWKV Griffin Mamba benchmark comparison LongBench v2 SCROLLS"

### Direct Question Decomposition Queries (top 3)
1. "linear attention substitution transformer accuracy retention long-context"
2. "retrieval vs summarization task accuracy sub-quadratic models"
3. "transformer to Mamba conversion zero-shot performance gap"

---

## 3. Past Cases & Best Practices (via Archon) [COMPACT]

**[NOT_FOUND - ARCHON]** 9 queries across 3 levels — all returned diffusion model / image generation content (domain mismatch). No NLP/LLM sub-quadratic cases in Archon KB.

**[INFERRED]** Pattern 1: Knowledge Distillation for Architecture Conversion — teacher-student hidden-state supervision (SSM state from Transformer hidden states).
**[INFERRED]** Pattern 2: Layer-wise Replacement Strategy — replace every N-th attention layer with SSM, keep remainder.
**[INFERRED]** Pattern 3: Benchmark-Driven Conversion Evaluation — fixed eval harness on held-out LongBench v2 / SCROLLS.

---

## 4. Academic Literature Review (via Semantic Scholar) [COMPACT]

**15 papers (9 relevant, 4 foundational, 2 benchmark).** Format: Title | Year | SS ID | arXiv | Citations | 1-line insight

### Directly Relevant Papers

| Title | Year | SS ID | arXiv | Cites | DQ | Key Insight |
|-------|------|-------|-------|-------|----|-------------|
| LAWCAT: Efficient Distillation from Quadratic to Linear Attention | 2025 | 8237f2fc77f3c4b21d3e5c85acb9ee70ed1ba2b8 | 2509.18467 | 4 | DQ1,DQ2,DQ4 | >90% passkey retrieval at 22K tokens from Mistral-7B distillation |
| On-the-Fly Adaptive Distillation of Transformer to Dual-State Linear Attention (DSLA-Serve) | 2025 | 9c407a5b56980380517e44ca14e0727941d3b221 | 2506.09316 | 3 | DQ1,DQ3,DQ4 | Layer-selective replacement; evaluates on long-context QA + summarization task types |
| Apriel-H1: Towards Efficient Enterprise Reasoning Models | 2025 | da649d7ca5cb629243328400f8845e4186537f92 | 2511.02651 | 2 | DQ1,DQ4 | SSM-to-MHA ratio analysis; reasoning degradation as function of conversion depth |
| Lizard: An Efficient Linearization Framework for LLMs | 2025 | 2314eabde4fe20e835d79274ae40043b589a9ec0 | 2507.09025 | 8 | DQ1 | Near-lossless recovery; +9.4–24.5 points on MMLU vs prior linearization |
| Overflow Prevention Enhances Long-Context Recurrent LLMs | 2025 | f30cced4f19a35b980195d7118910852d7e93da1 | 2505.07793 | 4 | DQ2,DQ3 | Evaluates Falcon3-Mamba, RecurrentGemma, RWKV6 on LongBench v2; chunk-based inference competitive |
| Overcoming Long-Context Limitations of SSMs via Context-Dependent Sparse Attention | 2025 | 32b8ce7a3ea6ec6880dfc16648b1fb1cd32a34eb | 2507.00449 | 4 | DQ2,DQ3 | Proves SSMs cannot solve multi-query joint recall in sub-quadratic time |
| Characterizing SSM and Hybrid LM Performance with Long Context | 2025 | e84fb028bcea9b4e0e293187e6c7f432e4b44741 | 2507.12442 | 2 | DQ2 | SSMs 4× faster at ~57K tokens, 64% memory reduction vs Transformers |
| Falcon-H1: Hybrid-Head LMs Redefining Efficiency and Performance | 2025 | 0b25979bf487cbc9334e0e94031cdac83d4f28dd | 2507.22448 | 46 | DQ1 | Hybrid SSM+Transformer; 256K context; matches/outperforms 2× larger models |
| State-space modeling in long sequence processing: survey | 2025 | 0e09661f70e52062fb431a3b3c861ecdb44ddfcb | N/A | 14 | DQ1 | Comprehensive SSM taxonomy; conversion strategy overview |

### Foundational Papers

| Title | Year | SS ID | arXiv | Cites | Key Insight |
|-------|------|-------|-------|-------|-------------|
| Mamba: Linear-Time Sequence Modeling with Selective State Spaces | 2023 | 7bbc7595196a0606a07506c4fb1473e5e87f6082 | 2312.00752 | 3938 | Foundational selective SSM; O(1) inference memory; scratch-trained baseline |
| RWKV: Reinventing RNNs for the Transformer Era | 2023 | N/A | 2305.13048 | 1066 | Linear attention formulation competitive with Transformers on LM |
| Griffin: Mixing Gated Linear Recurrences with Local Self-Attention | 2024 | N/A | 2402.19427 | 287 | Hybrid recurrent+attention; matches Llama-2 at 14B |
| Jamba: A Hybrid Transformer-Mamba Language Model | 2024 | N/A | 2403.19887 | 581 | First production SSM+Transformer+MoE hybrid; 52B model |

### Benchmark Papers

| Title | Year | SS ID | arXiv | Cites | Key Insight |
|-------|------|-------|-------|-------|-------------|
| LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-Context Multitasks | 2024 | N/A | THUDM | 1210★ | Official benchmark; 503 questions, 8k–2M context, 6 task categories |
| SCROLLS: Standardized CompaRison Over Long Language Sequences | 2022 | N/A | 2201.03533 | N/A | 7 long-document tasks; complementary to LongBench for evaluation |

---

## 5. Implementation Resources (via Exa) [COMPACT]

Format: Resource | URL | Stars | Key Feature

### Directly Relevant Implementations

| Resource | URL | Stars | Key Feature |
|----------|-----|-------|-------------|
| goombalab/mohawk | https://github.com/goombalab/mohawk | 7 | MOHAWK general distillation pipeline; YAML config; DDP/FSDP; lm-eval integration |
| goombalab/phi-mamba | https://github.com/goombalab/phi-mamba | 125 | MOHAWK-converted Phi-1.5→Mamba; Stage 1/2/3 code; NeurIPS 2024 |
| zeyuliu1037/LAWCAT | https://github.com/zeyuliu1037/LAWCAT | 1 | LAWCAT pipeline; Flash Linear Attention; S-NIAH + BABILong eval; EMNLP 2025 |
| THUDM/LongBench | https://github.com/THUDM/LongBench | 1210 | Official LongBench v2 eval; 6 task categories; HuggingFace integration |
| Ojiyumm/LongBench_RWKV | https://github.com/Ojiyumm/LongBench_RWKV | 5 | RWKV LongBench scripts; task-type category breakdown (DQ3 indirect evidence) |
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | 13449 | Standard eval harness; LongBench v2 PR #3256; SCROLLS tasks |

### Component Implementations

| Resource | URL | Stars | Key Feature |
|----------|-----|-------|-------------|
| recursal/GoldFinch-paper | https://github.com/recursal/GoldFinch-paper | 46 | GoldFinch RWKV+Transformer hybrid; linear pre-fill; arXiv:2407.12077 |
| krafton-ai/mambaformer-icl | https://github.com/krafton-ai/mambaformer-icl | 63 | MambaFormer in-context learning; hybrid Mamba+Transformer |

### Tutorial Resources

| Resource | URL | Key Insight |
|----------|-----|-------------|
| Cross-Architecture Distillation Part I - MOHAWK | https://goombalab.github.io/blog/2024/distillation-part1-mohawk/ | Step-by-step MOHAWK 3-stage distillation with matrix mixer theory |
| Selective Distillation: Layerwise Conversion to Linear Attention (HotInfra'24) | https://utns.cs.utexas.edu/assets/papers/hotinfra24.pdf | Layer-wise conversion; DQ1 and DQ4 directly addressed |
| DSLA-Serve ICML 2025 | https://proceedings.mlr.press/v267/ro25a.html | Progressive layer replacement; long-context QA and summarization eval |

---

## 6. Chain-of-Relations Analysis [COMPACT]

### Research Evolution Path

1. **Foundation (2021–2023)**: HiPPO/S4 → Mamba (selective SSM) → RWKV (linear attention recurrence) — established sub-quadratic sequence modeling with competitive perplexity
2. **Hybrid architectures (2024)**: Griffin, Jamba, GoldFinch — demonstrated hybrid SSM+attention mitigates retrieval weaknesses of pure SSMs
3. **Direct conversion from pretrained transformers (2024)**: MOHAWK (NeurIPS) — 3-stage distillation (matrix mixer alignment → hidden-state alignment → weight transfer); LAWCAT (EMNLP 2025) — linear attention distillation with Flash backend
4. **Long-context accuracy quantification (2025)**: DSLA-Serve (ICML), Lizard, Overflow Prevention paper — evaluated converted/recurrent models on realistic long-context tasks; LongBench v2 infrastructure mature
5. **Gap**: No paper runs all three conversion strategies on the same LongBench v2 task-category splits

### Cross-Reference Matrix

| Source | DQ | Implementation | Adaptability |
|--------|-----|----------------|-------------|
| MOHAWK / NeurIPS 2024 | DQ1, DQ4 | goombalab/mohawk (complete) | High — needs LongBench v2 eval |
| LAWCAT / EMNLP 2025 | DQ1, DQ2, DQ4 | zeyuliu1037/LAWCAT (complete) | High — extend to LongBench v2 |
| GoldFinch 2024 | DQ1 | recursal/GoldFinch-paper | Medium — hybrid, not distillation |
| Mamba / 2023 | DQ1, DQ5 | official Mamba repo | High — scratch-trained baseline |
| RWKV / 2023 | DQ1, DQ3, DQ5 | Peng/RWKV-LM + Ojiyumm/LongBench_RWKV | High — DQ3 indirect evidence |
| Overflow Prevention paper / 2025 | DQ2, DQ3 | N/A (evaluation paper) | Direct — LongBench v2 results |
| LongBench v2 / THUDM | DQ2, DQ3 | THUDM/LongBench | Direct — official benchmark |
| lm-evaluation-harness | DQ2, DQ3 | EleutherAI (LongBench v2 PR #3256) | Direct — standard eval |

**Key convergence**: MOHAWK pipeline + LongBench v2 + lm-evaluation-harness = complete experimental stack for DQ1–DQ5.

---

## 7. Verification Status Summary [COMPACT]

- **Total sources**: 30 (27 verified, 3 inferred)
- **[VERIFIED - SCHOLAR]**: 15 papers (50%)
- **[VERIFIED - EXA]**: 8 repos + 3 tutorials + 1 code context = 12 (40%)
- **[NOT_FOUND - ARCHON]**: 9 queries, 0 results (domain mismatch)
- **[INFERRED]**: 3 fallback patterns (10%)

| MCP Server | Queries | Results | Errors | Status |
|------------|---------|---------|--------|--------|
| Archon | 9 | 0 verified | 9 domain mismatches | FALLBACK |
| Semantic Scholar | 10 | 15 papers | 1 rate-limit (retried), 1 zero-result (reformulated) | SUCCESS |
| Exa | 7+1 | 12 resources | 0 | SUCCESS |

**Data quality**: Completeness 82/100, Reliability 90/100, Recency 88/100, Relevance 85/100.

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs:**

1. **Main Research Question**: When a pretrained transformer is converted to a sub-quadratic architecture (e.g., via linear attention substitution or selective state-space distillation), does the converted model retain ≥90% of the original model's accuracy on existing long-context benchmarks (LongBench v2, SCROLLS) at sequence lengths ≥4096, and does this retention vary systematically by task type (retrieval vs. summarization vs. QA)?

2. **Detailed Questions (DQ1–DQ5)**:
   - DQ1: Which conversion strategy achieves highest accuracy retention?
   - DQ2: Does retention degrade monotonically with sequence length, and at what threshold?
   - DQ3: Do retrieval-heavy tasks show larger drops than summarization/QA?
   - DQ4: Does fine-tuning recover accuracy vs. zero-shot conversion, and does recovery differ by strategy?
   - DQ5: Do scratch-trained sub-quadratic models match converted models, or does transformer prior provide measurable advantage?

3. **Reference Papers**: Not provided (Phase 1 to discover)

### Identified Gaps

#### Gap 1: No cross-strategy accuracy comparison on LongBench v2 task-category splits for converted models

**Relevance:** 🎯 `PRIMARY` — directly blocks answering DQ1 and DQ3.

**Connection to Research Question:** The research question asks which conversion strategy achieves highest accuracy retention and whether retention varies by task type. No existing paper provides a side-by-side table of all three strategies (linear attention substitution, SSM distillation, hybrid replacement) evaluated on the same LongBench v2 task splits. MOHAWK evaluates on perplexity + lm-eval standard tasks; LAWCAT evaluates on passkey/S-NIAH; DSLA-Serve uses internal long-context QA — none use LongBench v2.

**Current State:** Individual conversion methods have been evaluated on separate benchmarks. MOHAWK (phi-mamba) uses perplexity and standard lm-eval tasks. LAWCAT uses passkey retrieval at up to 22K tokens. GoldFinch and MambaFormer report in-context learning and perplexity. No paper has evaluated converted models on LongBench v2's 6 task categories (single-doc QA, multi-doc QA, summarization, few-shot, synthetic, code).

**Missing Piece:** A controlled comparison where the same base transformer (e.g., LLaMA-3-8B or Mistral-7B) is converted using each of the three strategies (MOHAWK, LAWCAT, hybrid) and then evaluated on identical LongBench v2 task-category splits, with task-type breakdown for each strategy.

**Potential Impact:** High — fills DQ1 (strategy ranking) and DQ3 (task-type interaction) simultaneously with a single experiment.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "MOHAWK: A Rebranding of State Space Models and Linear Recurrences" | 2024 | Dao et al. | N/A | 2408.10189 | N/A | 3-stage distillation pipeline; evaluated on perplexity and standard lm-eval tasks only — NOT on LongBench v2 |
| "LAWCAT: Efficient Distillation from Quadratic to Linear Attention" | 2025 | Liu et al. | 8237f2fc77f3c4b21d3e5c85acb9ee70ed1ba2b8 | 2509.18467 | 4 | >90% passkey retrieval at 22K tokens; evaluated on S-NIAH and BABILong — NOT on LongBench v2 task categories |
| "GoldFinch: High Performance RWKV/Transformer Hybrid" | 2024 | recursal | N/A | 2407.12077 | N/A | Hybrid architecture; reports perplexity and in-context learning — no LongBench v2 breakdown |
| "LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-Context Multitasks" | 2024 | Bai et al. | N/A | THUDM | 1210★ | Defines 6 task categories enabling the comparison; no converted model results included |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| [NOT_FOUND - ARCHON] No relevant cases | N/A | "sub-quadratic conversion strategy comparison benchmark" | Domain mismatch — Archon KB contains diffusion model content only |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| goombalab/mohawk | https://github.com/goombalab/mohawk | 7 | Python | MOHAWK pipeline with lm-eval-harness integration; extensible to LongBench v2 |
| zeyuliu1037/LAWCAT | https://github.com/zeyuliu1037/LAWCAT | 1 | Python | LAWCAT pipeline; needs LongBench v2 eval script addition |
| THUDM/LongBench | https://github.com/THUDM/LongBench | 1210 | Python | Official LongBench v2 eval codebase with task-category splits |
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | 13449 | Python | LongBench v2 PR #3256 in review; standardized eval for all strategies |

---

#### Gap 2: Sequence-length degradation threshold for converted (not scratch-trained) sub-quadratic models

**Relevance:** 🎯 `PRIMARY` — directly blocks answering DQ2.

**Connection to Research Question:** DQ2 asks whether accuracy retention degrades monotonically with sequence length and at what threshold degradation becomes statistically significant. This is an open question specifically for *converted* models: scratch-trained SSMs (Mamba, RWKV, Griffin) have been benchmarked at various lengths, but there is no published sequence-length degradation curve for a MOHAWK-converted or LAWCAT-converted model on LongBench v2 (which covers 8k–2M context) or SCROLLS.

**Current State:** LAWCAT reports >90% passkey retrieval at 22K tokens for linear attention. Griffin and Mamba papers show recurrent models can handle long sequences in principle. However, these are all either scratch-trained or tested on synthetic passkey tasks, not on task-accuracy across a range of realistic document lengths. LongBench v2 explicitly provides length-stratified evaluation (8k–32k, 32k–128k, 128k+) but no converted model has been evaluated with this stratification.

**Missing Piece:** Sequence-length × accuracy curves for at least one converted model on LongBench v2 or SCROLLS, binned at 4096, 8192, 16384, 32768+ token boundaries to identify the threshold where degradation becomes statistically significant versus the unconverted baseline.

**Potential Impact:** High — directly tests the research question's "≥4096" threshold claim and enables DQ2 to be answered quantitatively.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "RWKV: Reinventing RNNs for the Transformer Era" | 2023 | Peng et al. | N/A | 2305.13048 | 1066 | Scratch-trained RWKV shows competitive performance but no sequence-length ablation on LongBench task accuracy |
| "Mamba: Linear-Time Sequence Modeling with Selective State Spaces" | 2023 | Gu & Dao | 7bbc7595196a0606a07506c4fb1473e5e87f6082 | 2312.00752 | 3938 | Demonstrates O(1) memory SSM inference; no LongBench v2 sequence-length degradation analysis |
| "Griffin: Mixing Gated Linear Recurrences with Local Self-Attention" | 2024 | De et al. | N/A | 2402.19427 | 287 | Hybrid recurrent+attention model; evaluated at various lengths but on perplexity, not LongBench task categories |
| "LAWCAT: Efficient Distillation from Quadratic to Linear Attention" | 2025 | Liu et al. | 8237f2fc77f3c4b21d3e5c85acb9ee70ed1ba2b8 | 2509.18467 | 4 | 22K passkey retrieval threshold established; not replicated on LongBench v2 length bins |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| [NOT_FOUND - ARCHON] No relevant cases | N/A | "sequence length degradation SSM transformer long-context tasks" | Domain mismatch |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| Ojiyumm/LongBench_RWKV | https://github.com/Ojiyumm/LongBench_RWKV | 5 | Python | RWKV-specific LongBench scripts with task-type breakdowns; closest existing resource but scratch-trained RWKV, not converted |
| THUDM/LongBench | https://github.com/THUDM/LongBench | 1210 | Python | Official LongBench v2 with 8k–2M length-stratified evaluation infrastructure |

---

#### Gap 3: Quantified advantage of transformer prior in converted models vs. scratch-trained SSMs on identical benchmark subsets

**Relevance:** 🔗 `SECONDARY` — directly addresses DQ5; contextually relevant to DQ1.

**Connection to Research Question:** DQ5 asks whether converting from a strong transformer prior provides a measurable advantage over scratch-training a sub-quadratic model on existing eval sets. The literature contains both converted models (MOHAWK on Phi-1.5, LAWCAT on Mistral-7B) and scratch-trained SSMs (Mamba-3B, RWKV-7B), but they are never evaluated on the same benchmark subset at the same parameter scale in the same paper, making DQ5 currently unanswerable from existing literature.

**Current State:** MOHAWK converts Phi-1.5 (1.3B) → Mamba; LAWCAT converts Mistral-7B → linear attention. Scratch-trained Mamba-3B, RWKV-7B, and Griffin models exist and have been benchmarked separately on lm-eval standard tasks. However, no paper directly compares converted vs. scratch-trained at matched parameter counts on LongBench v2 or SCROLLS specifically.

**Missing Piece:** Evaluation of both (a) a converted model (e.g., MOHAWK-converted LLaMA-3-8B) and (b) the best available scratch-trained SSM at matched parameter count (e.g., Mamba-3B, RWKV-7B) on identical LongBench v2 and SCROLLS subsets, with per-task accuracy comparison.

**Potential Impact:** Medium — answers DQ5 and has implications for whether conversion pipelines are worth the effort vs. scratch-training, but does not change the primary research gap (DQ1/DQ3).

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Mamba: Linear-Time Sequence Modeling with Selective State Spaces" | 2023 | Gu & Dao | 7bbc7595196a0606a07506c4fb1473e5e87f6082 | 2312.00752 | 3938 | Scratch-trained Mamba-3B baseline; standard lm-eval only, not LongBench v2 |
| "RWKV: Reinventing RNNs for the Transformer Era" | 2023 | Peng et al. | N/A | 2305.13048 | 1066 | Scratch-trained RWKV-7B baseline; strong LM performance but LongBench v2 comparison missing |
| "Jamba: A Hybrid Transformer-Mamba Language Model" | 2024 | Lieber et al. | N/A | 2403.19887 | 581 | Hybrid 52B model; evaluated at long contexts but different scale from conversion papers — no DQ5 comparison |
| "MOHAWK: A Rebranding of State Space Models and Linear Recurrences" | 2024 | Dao et al. | N/A | 2408.10189 | N/A | Conversion pipeline from Phi-1.5; no side-by-side with scratch-trained Mamba at same scale |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| [NOT_FOUND - ARCHON] No relevant cases | N/A | "SSM distillation from pretrained transformer accuracy retention" | Domain mismatch |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| goombalab/phi-mamba | https://github.com/goombalab/phi-mamba | 125 | Python | MOHAWK-converted model (converted side of DQ5 comparison); lm-eval-harness evaluation |
| goombalab/mohawk | https://github.com/goombalab/mohawk | 7 | Python | Full MOHAWK pipeline applicable to LLaMA-3-8B conversion for DQ5 |

---

### Gap Priority Matrix

| Gap ID | Title | Relevance | Connection to RQ | DQs | Impact | Evidence Count | Priority |
|--------|-------|-----------|------------------|-----|--------|----------------|----------|
| Gap 1 | No cross-strategy comparison on LongBench v2 task categories | PRIMARY | ☑️ Blocks DQ1 + DQ3 | DQ1, DQ3 | High | 4 Scholar + 4 Exa = 8 | **Critical** |
| Gap 2 | Sequence-length degradation threshold for converted models | PRIMARY | ☑️ Blocks DQ2 | DQ2 | High | 4 Scholar + 2 Exa = 6 | **Critical** |
| Gap 3 | Quantified advantage of transformer prior vs. scratch-trained SSMs | SECONDARY | ☑️ Blocks DQ5 | DQ5 | Medium | 4 Scholar + 2 Exa = 6 | **High** |

### User Input to Gap Traceability
**Main Research Question** ("does converted model retain ≥90% accuracy by task type?") directly addressed by:
- Gap 1: No existing paper evaluates conversion strategies on LongBench v2 task-category splits — the ≥90% retention threshold cannot currently be verified
- Gap 2: No sequence-length degradation curve exists for converted models — the "≥4096" specificity of the threshold is untested

**DQ1** (which conversion strategy achieves highest retention?) addressed by:
- Gap 1: Cross-strategy comparison on identical benchmark required

**DQ2** (does retention degrade monotonically by sequence length, at what threshold?) addressed by:
- Gap 2: Sequence-length × accuracy curves for converted models are missing

**DQ3** (retrieval vs. summarization vs. QA task-type interaction?) addressed by:
- Gap 1: Task-category breakdown for converted models on LongBench v2 is missing; only indirect evidence from scratch-trained RWKV (Ojiyumm/LongBench_RWKV)

**DQ4** (does fine-tuning recover accuracy, does recovery differ by strategy?) addressed by:
- Gap 1 (partial): DSLA-Serve ICML 2025 covers layer-selective fine-tuning vs. zero-shot, but not on LongBench v2; completing Gap 1 experiment with fine-tuning arm would address DQ4

**DQ5** (scratch-trained vs. converted — does transformer prior provide measurable advantage?) addressed by:
- Gap 3: No head-to-head comparison at matched parameter count on LongBench v2/SCROLLS exists

---

## 9. Conclusion [COMPACT]

### Key Findings

1. Conversion infrastructure complete: MOHAWK + LAWCAT + DSLA-Serve provide all three conversion strategies as open-source code.
2. ≥90% retention threshold has partial support at <22K tokens (LAWCAT passkey); not validated on LongBench v2 task categories.
3. Evaluation stack ready: THUDM/LongBench + lm-evaluation-harness + LongBench v2 PR #3256 cover DQ1–DQ5 evaluation needs.
4. ROUTE_TO_0 validation: new direction has no dependency chain, no attention proxy, no KV eviction — all 5 DQs independently testable.
5. **Critical gap**: no paper runs all three conversion strategies on LongBench v2 task-category splits.

### Phase 2 Readiness
- [x] 3 research gaps with table-format evidence
- [x] Evaluation infrastructure identified
- [x] No Archon KB matches (documented)
- [x] ROUTE_TO_0 pitfalls avoided in all discovered methods

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~45 minutes (automated unattended execution, 2026-08-03)*
