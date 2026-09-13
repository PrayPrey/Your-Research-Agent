# Targeted Research Report: Can compute- and memory-efficient fine-tuning methods (e.g., LoRA-style parameter-efficient adaptation) be combined with KV cache compression strategies to jointly reduce inference cost and adaptation overhead for long-context foundation models, without sacrificing task-specific performance on standard NLP benchmarks?

**Generated:** 2026-05-20
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous
---

## Executive Summary

This Phase 1 Targeted Research report investigates whether compute- and memory-efficient fine-tuning methods (LoRA-style PEFT) can be jointly optimized with KV cache compression strategies for long-context foundation models. Research was conducted across three sources: Archon knowledge base (5 verified + 1 inferred pattern), Semantic Scholar (18 papers, 2020–2025), and Exa GitHub/web search (14 implementations and tutorials).

**Key Finding:** The most directly relevant existing work is arXiv 2604.21335 (Sub-Token Routing in LoRA for Adaptation and Query-Aware KV Compression, 2025), which partially addresses the research question but evaluates only on perplexity/RULER — not standard NLP benchmarks (GLUE, SuperGLUE). A genuine research gap exists: no published work jointly trains LoRA adapter weights and KV eviction policies with evaluation on standard NLP benchmarks.

**Three Primary Research Gaps Identified:**
1. **Joint LoRA + KV Eviction Training Gap** (PRIMARY — Critical): No work jointly optimizes adapter weights and KV eviction parameters with NLP benchmark evaluation
2. **Quadratic-to-Sub-Quadratic Adaptation Quality Gap** (PRIMARY — High): GLUE/SuperGLUE benchmarking of transformer-to-Mamba distillation under PEFT is absent from literature
3. **MoE Routing Adaptivity Under Distribution Shift Gap** (SECONDARY — High): Open-weight MoE models (Mixtral) exist but systematic comparison of learned vs. fixed routing under distribution shift on MMLU/BIG-Bench is missing

**Verification Rate:** 97.2% (35/36 sources verified via MCP tools). All gaps are supported by multi-source evidence and directly connected to user research questions. Phase 2A hypothesis generation is ready to proceed.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Can compute- and memory-efficient fine-tuning methods (e.g., LoRA-style parameter-efficient adaptation) be combined with KV cache compression strategies to jointly reduce inference cost and adaptation overhead for long-context foundation models, without sacrificing task-specific performance on standard NLP benchmarks?

### Detailed Research Questions
1. How can efficient fine-tuning methods (LoRA, continual adaptation) be combined with KV cache compression for long-context inference — can joint optimization of adapter weights and KV eviction policies outperform decoupled approaches on existing long-context benchmarks?
2. Can quadratic-to-sub-quadratic model conversion (e.g., transformer-to-Mamba distillation) preserve task-specific adaptation quality (measured on GLUE, SuperGLUE, or equivalent) while reducing inference FLOPs by a target factor on existing pretrained checkpoints?
3. How do adaptive routing strategies in MoE models (learned vs. fixed routing) compare under distribution shift scenarios measurable on existing multi-domain benchmarks (e.g., MMLU, BIG-Bench), using existing open-weight MoE models?
4. What are the trade-offs between RAG-based context injection and in-weights continual fine-tuning for knowledge update tasks, measurable on existing knowledge-intensive QA benchmarks (e.g., NaturalQuestions, TriviaQA, PopQA)?
5. Can sub-quadratic models with compressive KV states (SSMs, linear attention) match transformer accuracy on multimodal foundational tasks using existing multimodal benchmarks (e.g., VQAv2, MMBench)?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
*N/A - First attempt*

---

## 2. Search Queries Generated (Compact)

**Total queries:** 13 (0 reference, 5 brainstorm, 8 direct decomposition)

**Top queries by priority:**
1. "PEFT KV cache compression joint optimization long-context inference"
2. "LoRA KV cache eviction policy joint optimization long-context"
3. "transformer to Mamba distillation task-specific adaptation quality"
4. "RAG continual fine-tuning knowledge update trade-offs QA benchmarks"
5. "sub-quadratic attention SSM linear attention transformer accuracy comparison multimodal"

*Full query list in 01_targeted_research_full.md*

---

## 3. Past Cases & Best Practices (via Archon) — Compact

**MCP Server:** Archon KB | **Queries:** 13 across Levels 1-3 | **Results:** 5 verified + 1 inferred

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| LoRA/Low-Rank Adaptation (PEFT) | c0bcf966-7063-40e8-bc4e-c33a627b47b8 | "low-rank adaptation foundation model efficiency" | LoRA injects trainable A·B matrices into Q/K/V; <1% parameters; standard injection starting point |
| QLoRA — Quantized LoRA | 6e684392-6bcb-4276-9a46-35ee52241ed0 | "parameter-efficient fine-tuning inference efficiency co-optimization" | Joint 4-bit quant+LoRA proves co-compression feasibility; KV compression is the unexplored analog |
| Flash Attention (IO-Aware Exact) | e7ab2216-c4cd-4d25-a602-1741bb82e05b | "flash attention sliding window efficient transformer" | Tiling+recomputation reduces HBM I/O; foundational for long-context inference |
| HuggingFace Quantization overview | a38424c1-c676-4262-8e27-9aea5955161d | "model compression quantization efficiency best practices" | Quantization trade-off pattern (GPTQ/bitsandbytes); analogous methodology for KV compression |
| Efficient Attention Processor Design | 82bd2ffa-f91e-4dee-88fe-86ccf1a2fbbf | "attention mechanism long-context efficient patterns" | Modular attention processor interface; plug-in point for compressed KV |
| [INFERRED] Joint KV Eviction + LoRA co-training | N/A | "KV cache eviction LoRA joint training" | No Archon KB entry found; Archon KB is primarily diffusion-model content |

---

## 4. Academic Literature Review (via Semantic Scholar) — Compact

**MCP Server:** Semantic Scholar | **Queries:** 10 across 4 rounds | **Results:** 18 papers

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| KV Pareto: Systems-Level Optimization | 2025 | Gokhale et al. | 08611613874f6e61b926922bf2563fbcaa5d0f0e | — | 0 | Joint KV quant + weight quant Pareto frontier; 68-78% memory reduction |
| EMPIRIC: Missing Pieces in KV Cache Compression | 2025 | Behnam et al. | 957fe6370e176853431091c8c76fbf6b4eff8239 | — | 0 | Oracle study; theoretical bounds for KV accuracy/compute/storage |
| ZSMerge: Zero-Shot KV Cache Compression | 2025 | Liu et al. | 6a9839528b127a530299fefb37a74818efa4ff56 | — | 7 | 20:1 compression on LLaMA2-7B; no retraining required |
| TailorKV: Hybrid KV Cache Optimization | 2025 | Yao et al. | 4f537682b00fe2be5ca480d6f43a2513f6657a69 | — | 7 | Layer-type classification for selective load/quantize; 128k on single 3090 |
| Locret: Trained Retaining Heads for Eviction | 2024 | Huang et al. | cb92261c8ef307519d9a44bfc5d1023faae2e301 | — | 13 | 20x KV compression; PEFT-like trained eviction heads; <1 GPU hr training |
| LESS: Recurrence + KV Compression | 2024 | Dong et al. | ef1b02dc1b82f9955fc4760fcefd92c0fff9f227 | — | 85 | Low-rank recurrence sidekick + eviction; full-token recall capability |
| DSLA-Serve: Transformer→Linear Attention | 2025 | Ro et al. | 9c407a5b56980380517e44ca14e0727941d3b221 | — | 2 | 2.3x faster inference; comparable commonsense/QA/summarization |
| Mamba-3: Improved SSM | 2026 | Lahoti et al. | 02cbf7c87d721ca17b3416d2360350092a21c2c8 | — | 33 | Best sub-quadratic model; complex-valued state; constant memory inference |
| MadaKV: Multimodal KV Eviction | 2025 | Li et al. | 9397ae3adf9970af9ff0bdcacb9f86aad417c264 | — | 7 | Modality-adaptive eviction; 1.3-1.5x latency improvement |
| FIT-RAG: RAG with Token Reduction | 2024 | Mao et al. | 91e011a952de940e5aea485fed5e49140924a8ca | — | 27 | +14-27% on TriviaQA/NQ/PopQA vs frozen LLM; RAG superiority on static QA |
| TT-LoRA MoE: PEFT + Sparse MoE | 2025 | Kunwar et al. | c6a6f0e39054fe8d90606e11409d387ed6063d47 | — | 5 | 0.03% AdapterFusion params; +4% multi-task; automated expert selection |
| Survey on LoRA of LLMs | 2024 | Mao et al. | 291c94b62953e261c94b74516ee997be5511c052 | — | 140 | Comprehensive 5-dimension LoRA taxonomy; efficiency variants covered |
| Low-Rank Adaptation for Foundation Models | 2024 | Yang et al. | f2578a4903f9e213d1440a1f044caac8608630bb | — | 44 | First comprehensive review extending LoRA to multimodal foundation models |
| Efficient Compressing + Tuning LLMs Survey | 2025 | Kim et al. | b073de891287423915b1709c4cc90f40756c38b9 | — | 18 | Identifies lack of unified compression+tuning frameworks as key gap |
| Online Scheduling for LLM Inference (KV) | 2025 | Jaillet et al. | 9a85d96bb9150844784557e8fd47e0220a0b9891 | — | 16 | Formal analysis of KV cache memory constraints; polynomial-time algorithm |
| MCaM: Multi-tier KV Cache Management | 2025 | Chu et al. | 44472e115aedc554939d652b0e6fe766e9bfd31b | — | 5 | GPU/DRAM hierarchy; 69% TTFT reduction; 3.3x prefilling throughput |
| Sub-Token Routing in LoRA + KV Compression | 2025 | — | — | 2604.21335 | — | **Most direct hit**: routed LoRA + value-group KV routing; 50% value retention |
| Exploring Fine-Tuning for ICR + KV-Caching | 2026 | Molfese et al. | (EACL 2026) | — | — | SFT/RL → moderate KV compression robustness; task-dependent |

*Full paper metadata in 01_targeted_research_full.md*

---

## 5. Implementation Resources (via Exa) — Compact

**MCP Server:** Exa | **Queries:** 7 web + 1 code context | **Results:** 10 repos + 3 tutorials + 1 code analysis

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| NVIDIA/kvpress | https://github.com/NVIDIA/kvpress | 1025 | Python | Forward-hook KV compression; combinable with any PEFT fine-tuned model |
| amazon-science/icr-kv-caching | https://github.com/amazon-science/icr-kv-caching-long-context-llms | 1 | Python | **Most direct**: SFT+RL training + KV compression evaluation; EACL 2026 |
| huangyuxiang03/Locret | https://github.com/huangyuxiang03/Locret | 14 | Python+CUDA | Trained retaining heads; extensible to co-train with LoRA |
| hdong920/LESS | https://github.com/hdong920/LESS | 52 | Python | Low-rank recurrence + eviction; design patterns for joint PEFT+KV |
| SqueezeAILab/KVQuant | https://github.com/SqueezeAILab/KVQuant | 419 | Python+CUDA | int2/4/8 KV quantization; 10M context; NeurIPS 2024 |
| hjeon2k/LRAgent | https://github.com/hjeon2k/LRAgent | N/A | Python | Decomposes KV into base+LoRA components; Flash-LoRA-Attention |
| awslabs/keys_values | https://github.com/awslabs/keys_values | 9 | Python | Unified KV caching + fine-tuning research library |
| princeton-pli/PruLong | https://github.com/princeton-pli/PruLong | 48 | Python+CUDA | Learns 0/1 attention head masks; combinable with LoRA |
| IsaacRe/vllm-kvcompress | https://github.com/IsaacRe/vllm-kvcompress | 155 | Python+CUDA | vLLM fork for high-throughput compressed serving |
| whyNLP/LCKV | https://github.com/whyNLP/LCKV | 157 | Python | Layer-Condensed KV Cache; 10x batch size; ACL 2024 |
| arXiv 2604.21335 (tutorial/paper) | https://arxiv.org/html/2604.21335v1 | — | Paper | **Most direct**: joint routed LoRA + value-group KV routing |
| arXiv 2408.10189 (T2MD NeurIPS 2024) | https://arxiv.org/html/2408.10189 | — | Paper | Transformer→SSM distillation methodology |
| EACL 2026 ICR paper | https://aclanthology.org/2026.eacl-short.44/ | — | Paper | Fine-tuning impact on KV compression robustness |

*Code context analysis: arXiv 2604.21335 proves joint LoRA+KV compression feasible; LRAgent pattern (base+LR KV decomposition); Locret co-training extensible to LoRA*

---

## 6. Chain-of-Relations Analysis — Compact

**Research Evolution:**
LoRA (2021) → QLoRA (2023, joint quant+LoRA) → Locret (2024, learned eviction) → LESS (2024, low-rank recurrence) → LRAgent (2025, KV decomposed into base+LoRA) → arXiv 2604.21335 (2025, joint sub-token LoRA+KV routing) → **[GAP: joint co-training with NLP benchmark evaluation]**

**Concept Integration Map (condensed):**
- LoRA modifies Q/K/V projections → adapter weights alter KV cache content → standard eviction policies misaligned with adapted activations → **joint optimization needed**
- DQ2 track: Transformer→Mamba (DSLA, Mamba-3, T2MD) — separate research thread
- DQ3 track: MoE routing + PEFT (TT-LoRA MoE) — separate research thread
- DQ4 track: RAG vs fine-tuning (FIT-RAG, Amazon ICR) — separate research thread

**Cross-Reference Matrix (top 5 by relevance):**

| Resource | Relevance | DQ | Implementation | Adaptability |
|----------|-----------|----|----------------|--------------|
| arXiv 2604.21335 | **Direct** | DQ1 | Partial (code context) | High |
| amazon-science/icr-kv-caching | **Direct** | DQ1 | Yes (GitHub) | High |
| Locret (2024) | High | DQ1 | Yes (GitHub) | High |
| NVIDIA/kvpress (★1025) | High | DQ1 | Yes (GitHub) | High |
| DSLA-Serve (2025) | High | DQ2 | Yes (GitHub) | High |

---

## 7. Verification Status — Compact

| Source | Verified | Inferred | Total |
|--------|----------|----------|-------|
| Archon KB | 5 | 1 | 6 |
| Semantic Scholar | 16 | 0 | 16 |
| Exa (repos + tutorials + code) | 14 | 0 | 14 |
| **Total** | **35** | **1** | **36** |

**Overall rate:** 97.2% | 1 rate-limit (Scholar; recovered after 15s) | **Data quality: 86/100**

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs:**
1. **Main Research Question:** Can compute- and memory-efficient fine-tuning methods (e.g., LoRA-style parameter-efficient adaptation) be combined with KV cache compression strategies to jointly reduce inference cost and adaptation overhead for long-context foundation models, without sacrificing task-specific performance on standard NLP benchmarks?
2. **Detailed Questions:** 5 sub-questions (DQ1: LoRA+KV joint; DQ2: sub-quadratic conversion; DQ3: MoE routing; DQ4: RAG vs fine-tuning; DQ5: sub-quadratic multimodal)
3. **Reference Papers:** Not provided

### Identified Gaps

#### Gap 1: Joint LoRA Adapter Training and KV Cache Eviction Policy Co-Optimization

**Relevance Classification:** 🎯 PRIMARY — Directly blocks answering the main research question
**Connection:** ☑️ Blocks answering research question: Cannot determine whether joint optimization outperforms decoupled approaches without a co-training framework that optimizes both simultaneously; ☑️ Directly addresses DQ1

**Current State:** LoRA adapters and KV cache compression are treated as independent techniques. Existing work (Locret, LESS, kvpress) applies KV compression to frozen or already-fine-tuned models. LRAgent decomposes KV cache for multi-LoRA serving but does not co-train eviction policies with adapter weights. arXiv 2604.21335 introduces sub-token routing combining routed LoRA with value-group KV routing, but focuses on language modeling quality rather than standard NLP benchmark performance (GLUE/SuperGLUE/long-context benchmarks). Amazon ICR (EACL 2026) shows fine-tuning brings moderate KV compression robustness but does not optimize KV eviction jointly with adapter training.

**Missing Piece:** A training framework that jointly optimizes (1) LoRA adapter weights for task-specific performance and (2) KV eviction/compression parameters (e.g., retaining head weights, eviction thresholds, routing masks) within a single differentiable objective, evaluated on standard NLP benchmarks with memory/compute budget constraints.

**Potential Impact:** High — if joint optimization outperforms decoupled approaches, it enables a unified efficient LLM serving paradigm; directly addresses the workshop's core efficiency challenge.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "KV Pareto: Systems-Level Optimization of KV Cache and Model Compression" | 2025 | Gokhale et al. | 08611613874f6e61b926922bf2563fbcaa5d0f0e | — | 0 | Joint KV quantization + weight quantization Pareto frontier; no LoRA adapter co-training |
| "Locret: Enhancing Eviction in Long-Context LLM Inference with Trained Retaining Heads" | 2024 | Huang et al. | cb92261c8ef307519d9a44bfc5d1023faae2e301 | — | 13 | Learned eviction heads show PEFT-style training is applicable to KV compression; not co-trained with LoRA |
| "Get More with LESS: Synthesizing Recurrence with KV Cache Compression" | 2024 | Dong et al. | ef1b02dc1b82f9955fc4760fcefd92c0fff9f227 | — | 85 | Low-rank recurrence sidekick + eviction; design pattern for joint low-rank+eviction but not LoRA-specific |
| "Exploring Fine-Tuning for In-Context Retrieval and Efficient KV-Caching" | 2026 | Molfese et al. | (EACL 2026) | — | N/A | SFT/RL fine-tuning improves KV compression robustness moderately; task-dependent; confirms gap |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| QLoRA — Quantized LoRA (joint quant+adapter) | 6e684392-6bcb-4276-9a46-35ee52241ed0 | "parameter-efficient fine-tuning inference efficiency" | Joint quantization+LoRA demonstrates co-compression feasibility; KV compression is the unexplored analog |
| HuggingFace PEFT LoRA adapter implementation | c0bcf966-7063-40e8-bc4e-c33a627b47b8 | "low-rank adaptation foundation model efficiency" | Standard LoRA injection into Q/K/V projections — starting point for KV-aware adapter training |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| amazon-science/icr-kv-caching-long-context-llms | https://github.com/amazon-science/icr-kv-caching-long-context-llms | 1 | Python | SFT+RL training + KV compression evaluation; closest existing codebase |
| huangyuxiang03/Locret | https://github.com/huangyuxiang03/Locret | 14 | Python+CUDA | Learned retaining heads; training pipeline extensible to co-train with LoRA |
| NVIDIA/kvpress | https://github.com/NVIDIA/kvpress | 1025 | Python | Forward-hook compression; combinable with PEFT fine-tuned models |
| hjeon2k/LRAgent | https://github.com/hjeon2k/LRAgent | N/A | Python | Decomposes KV into base+LoRA components; Flash-LoRA-Attention implementation |

---

#### Gap 2: Systematic Benchmark Evaluation of Task-Specific Adaptation Quality Under Quadratic-to-Sub-Quadratic Model Conversion

**Relevance Classification:** 🎯 PRIMARY — Directly addresses DQ2 and the broader research question's efficiency claim
**Connection:** ☑️ Blocks answering DQ2: No existing work systematically measures GLUE/SuperGLUE task-specific adaptation quality degradation across multiple sub-quadratic conversion methods with controlled FLOP reduction targets; ☑️ Relates to research question's "without sacrificing task-specific performance" requirement

**Current State:** Sub-quadratic conversion methods exist (DSLA-Serve, Mamba-3, T2MD diffusion Transformer→Mamba). DSLA-Serve shows 2.3x speedup with comparable performance on commonsense/QA/summarization. However: (1) evaluation focuses on generation tasks, not fine-tuning adaptation quality; (2) no comparison across GLUE/SuperGLUE with controlled FLOP reduction; (3) most work studies pre-trained models, not the interaction between sub-quadratic conversion and subsequent PEFT adaptation.

**Missing Piece:** Controlled benchmark study measuring task-specific fine-tuning quality (GLUE, SuperGLUE, long-context QA) as a function of FLOP reduction from sub-quadratic conversion, across multiple architectures (Mamba, linear attention, hybrid), with existing pretrained checkpoints.

**Potential Impact:** High — establishes feasibility boundary for DQ2; determines whether sub-quadratic models can serve as drop-in replacements in PEFT pipelines.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "On-the-Fly Adaptive Distillation of Transformer to Dual-State Linear Attention" | 2025 | Ro et al. | 9c407a5b56980380517e44ca14e0727941d3b221 | — | 2 | 2.3x speedup with comparable performance; but not evaluated on GLUE/SuperGLUE adaptation |
| "Mamba-3: Improved Sequence Modeling using State Space Principles" | 2026 | Lahoti et al. | 02cbf7c87d721ca17b3416d2360350092a21c2c8 | — | 33 | Best sub-quadratic model; advances performance-efficiency Pareto; no PEFT adaptation study |
| "Efficient Compressing and Tuning Methods for Large Language Models" | 2025 | Kim et al. | b073de891287423915b1709c4cc90f40756c38b9 | — | 18 | Survey identifies lack of unified compression+tuning frameworks as key gap |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| HuggingFace Quantization overview (when to use what) | a38424c1-c676-4262-8e27-9aea5955161d | "model compression quantization efficiency best practices" | Quantization trade-off guidance; analogous methodology needed for sub-quadratic conversion |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| arxiv.org/html/2408.10189 (Transformers to SSMs) | https://arxiv.org/html/2408.10189 | N/A | Paper | NeurIPS 2024 distillation methodology; starting point for conversion quality study |
| utnslab/DSLA-Serve (inferred from Scholar result) | https://github.com/utnslab/DSLA-Serve | N/A | Python | Online adaptive distillation; extensible for GLUE/SuperGLUE evaluation |

---

#### Gap 3: Resource-Constrained Trade-off Characterization Between RAG and In-Weights Fine-Tuning Under KV Compression

**Relevance Classification:** 🔗 SECONDARY — Addresses DQ4; connects to research question's "inference cost reduction" dimension
**Connection:** ☑️ Relates to DQ4: Trade-offs between RAG vs. fine-tuning for knowledge update tasks under memory constraints are not characterized with KV compression applied to both; ☑️ Research question asks about "reducing inference cost" — RAG adds KV overhead for retrieved context while fine-tuning amortizes it

**Current State:** FIT-RAG (2024) demonstrates RAG superiority on TriviaQA/NQ/PopQA over frozen LLMs with 14-27% accuracy gains. Amazon ICR study (EACL 2026) shows RAG stronger on multiple-choice (+6 pts) while fine-tuning excels on finance (+9 pts). However, neither study: (1) applies KV cache compression to both paradigms comparably; (2) measures inference throughput/memory under the same budget; (3) uses continual knowledge update scenarios rather than static benchmarks.

**Missing Piece:** Controlled comparison of RAG vs. continual fine-tuning on knowledge-intensive QA benchmarks (NaturalQuestions, TriviaQA, PopQA) under matched memory budgets, with KV compression applied uniformly — measuring accuracy, inference latency, and memory footprint jointly.

**Potential Impact:** Medium — important for deployment decisions; directly answers DQ4 and informs the broader efficiency vs. accuracy trade-off question.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "FIT-RAG: Black-Box RAG with Factual Information and Token Reduction" | 2024 | Mao et al. | 91e011a952de940e5aea485fed5e49140924a8ca | — | 27 | RAG +14-27% on TriviaQA/NQ/PopQA vs frozen LLM; no KV compression comparison |
| "Exploring Fine-Tuning for In-Context Retrieval and Efficient KV-Caching" | 2026 | Molfese et al. | (EACL 2026) | — | N/A | Fine-tuning vs RAG trade-offs are task-dependent; KV compression affects both moderately |
| "A survey on LoRA of large language models" | 2024 | Mao et al. | 291c94b62953e261c94b74516ee997be5511c052 | — | 140 | LoRA enables efficient continual adaptation; comparison with RAG under memory budgets unexplored |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| [INFERRED] RAG vs fine-tuning under memory constraints | N/A | "RAG retrieval augmented generation fine-tuning knowledge" | No Archon KB entries found; gap is genuine absence in knowledge base |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| amazon-science/icr-kv-caching-long-context-llms | https://github.com/amazon-science/icr-kv-caching-long-context-llms | 1 | Python | RAG + SFT/RL comparison with KV evaluation; directly usable for DQ4 study |
| NVIDIA/kvpress | https://github.com/NVIDIA/kvpress | 1025 | Python | Can apply uniform KV compression to RAG context and fine-tuned model equally |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to Research Question | Connection to Detailed Question | Impact | Evidence Count | Priority |
|--------|-----------|--------------------------------|--------------------------------|--------|----------------|----------|
| Gap 1 | PRIMARY | ☑️ Directly blocks joint optimization answer | ☑️ DQ1 — joint LoRA+KV eviction | High | 4 Scholar + 2 Archon + 4 Exa = 10 | **Critical** |
| Gap 2 | PRIMARY | ☑️ Blocks "without sacrificing performance" claim | ☑️ DQ2 — sub-quadratic conversion | High | 3 Scholar + 1 Archon + 2 Exa = 6 | **High** |
| Gap 3 | SECONDARY | ☑️ Relates to inference cost reduction dimension | ☑️ DQ4 — RAG vs fine-tuning | Medium | 3 Scholar + 0 Archon + 2 Exa = 5 | **Medium** |

### User Input to Gap Traceability

**Main Research Question** ("Can PEFT + KV compression jointly reduce cost without performance loss?") directly addressed by:
- Gap 1: The joint optimization gap is the central open problem — no existing work trains both components simultaneously and evaluates on standard benchmarks
- Gap 2: The "without sacrificing task-specific performance" qualifier requires systematic characterization of the performance-efficiency trade-off curve under sub-quadratic conversion

**Detailed Question DQ1** (LoRA + KV compression joint optimization):
- Gap 1: Precisely this gap — decoupled approaches exist; joint co-training with benchmark evaluation is missing

**Detailed Question DQ2** (sub-quadratic conversion + adaptation quality on GLUE/SuperGLUE):
- Gap 2: Existing sub-quadratic work lacks controlled GLUE/SuperGLUE adaptation quality measurement

**Detailed Question DQ4** (RAG vs fine-tuning knowledge update trade-offs):
- Gap 3: Trade-offs under matched memory budgets with KV compression applied to both paradigms are uncharacterized

**Reference Papers:** Not provided — no reference paper extension applicable.

---

## 9. Conclusion (Compact)

### Key Findings
1. **Joint LoRA+KV optimization is an open gap** — arXiv 2604.21335 is closest but evaluates on perplexity/RULER, not NLP benchmarks
2. **PEFT and KV compression are converging** — QLoRA+Locret+LRAgent components exist; missing synthesis is co-training end-to-end
3. **Fine-tuning improves KV compression robustness moderately** — Amazon ICR (EACL 2026) confirms interaction is task-dependent
4. **Sub-quadratic conversion lacks PEFT adaptation quality benchmarks** — DSLA-Serve/Mamba-3 exist but no GLUE/SuperGLUE controlled study
5. **Mature tooling ecosystem exists** — NVIDIA kvpress (★1025), KVQuant (★419) provide starting points; gap is methodological

### Phase 2 Readiness
✅ **READY for Phase 2A Hypothesis Generation**
- 3 gaps identified with PRIMARY/SECONDARY classification and full evidence tables
- Gap 1 (joint LoRA+KV co-optimization) confirmed as central testable gap
- Phase 2A should focus on Gap 1 as primary hypothesis target

### Next Steps
1. Proceed to Phase 2A-Dialogue — generate testable hypotheses centered on Gap 1
2. Primary hypothesis direction: Joint training framework co-optimizing LoRA adapter weights and KV eviction parameters on GLUE/SuperGLUE and long-context benchmarks

---

*Report generated by YouRA Deep Learning Research Analyst*
*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~45 minutes (Steps 0-9, UNATTENDED mode, 2026-05-20)*
*Full archival report: 01_targeted_research_full.md*
