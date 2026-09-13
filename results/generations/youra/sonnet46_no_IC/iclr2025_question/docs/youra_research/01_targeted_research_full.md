# Targeted Research Report: Depth-Resolved Logit-Lens Uncertainty Signals for Architecture-Robust Hallucination Detection

**Date:** 2026-08-05
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

Targeted research (ROUTE_TO_0 retry) for depth-resolved logit-lens uncertainty signals as architecture-robust hallucination detectors. 16 prioritized queries (3 failure-aware) executed across three MCP servers: Semantic Scholar delivered 17 verified papers, Exa delivered 10 verified implementation resources, Archon KB proved off-domain (diffusion corpus; fallback protocol applied, 3 inferred patterns recorded honestly).

**Bottom line:** The literature has independently converged on the premise behind this pivot — intermediate layers carry stronger hallucination signal than the final layer (Automatic Layer Selection/FEPoID 2026; "LLMs Know More Than They Show" 2024; "Layer by Layer" 2025) — yet NOBODY has evaluated raw logit-lens uncertainty statistics (per-layer entropy, max-prob, adjacent-layer KL) as training-free single-pass detection scores with per-model layer selection. Three PRIMARY gaps identified: (1) the core per-layer logit-lens AUROC evaluation, (2) cross-dataset layer stability / cross-family depth consistency, (3) adjacent-layer KL as detection signal + the LLaMA-2-7B rescue stress test anchored to the documented 0.5186 final-layer failure. Two adversarial papers (Kim 2025; Chi 2025) bound the claim and must shape Phase 2A hypothesis framing. Implementation feasibility is de-risked by the v1 archive (validated code, 871/1000 feature cache) plus mature open-source components (tuned-lens 601★, DoLa 557★, entropy-profiler).

---

## 0. Reference Paper Analysis

*No reference papers provided* — Phase 0 states "Not provided - will discover in Phase 1". Query generation (Step 2) will rely on brainstorm insights and direct question decomposition, plus the six focus areas listed in Phase 0 Next Steps (logit lens / tuned lens, internal-state hallucination detection, layer-wise knowledge localization / DoLa, entropy-based UQ baselines on QA benchmarks, cross-architecture robustness, consecutive-layer KL divergence).

---

## 1. Research Questions

### Primary Research Question
Does per-model selection of depth-resolved uncertainty signals — logit-lens entropy, logit-lens max-token probability, and consecutive-layer prediction KL divergence computed at each transformer layer from a single greedy forward pass — achieve hallucination-detection AUROC > 0.60 on TriviaQA and TruthfulQA for all three open-source model families (LLaMA-2-7B, Mistral-7B, LLaMA-3-8B), including LLaMA-2-7B where final-layer mean entropy failed (AUROC 0.5186), and does the best intermediate layer outperform the final layer by a statistically significant margin (95% bootstrap CI separation) on LLaMA-2-7B?

### Detailed Research Questions
1. Does logit-lens entropy at some intermediate layer exceed final-layer mean entropy AUROC on LLaMA-2-7B, the architecture where the final-layer signal failed (0.5186), with the 95% bootstrap CI of the difference excluding zero?
2. Is the per-model optimal layer stable across datasets — does the layer selected on a TriviaQA held-out split transfer to TruthfulQA (and vice versa) without AUROC dropping below 0.60?
3. Does consecutive-layer prediction KL divergence (distribution shift between adjacent layers' logit-lens predictions) provide complementary signal beyond per-layer entropy, measured by AUROC gain when the two are fused per-model with logistic regression?
4. Is the relative depth of the most informative layer (layer index / total layers) consistent across the three model families, or is depth-of-signal itself architecture-dependent?
5. Does the single-pass layer-wise approach match or exceed the final-layer signal on Mistral-7B and LLaMA-3-8B (i.e., the pivot does not sacrifice the architectures that already passed)?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)

**What was tried:**
- **Attempt 1 (h-e1 run 1 — recorded scientific failure):** Final-layer mean token logit entropy, gate AUROC > 0.52. LLaMA-3-8B 0.66 PASS; Mistral-7B 0.53–0.59 PASS; LLaMA-2-7B 0.5186 FAIL (missed by 0.0014, direction inverted on TriviaQA).
- **Attempts 2–3:** Multi-signal fusion (entropy variants + max-token probability + semantic consistency variance) — archived via routing restarts, no passing run.
- **Attempt 4 (Layer-Wise Logit-Lens v1 — interrupted, NOT refuted):** Full pipeline reached Phase 4 healthy execution (validator 18/18 pass); routing restart archived it mid-run at 871/1000 LLaMA-2/TriviaQA samples cached. Reusable assets in `_archive/20260805T054934_routing_recovery/h-e1/`: validated code, environment recipe (torch 2.8.0+cu128, transformers 4.57.6), partial feature cache.

**Why the original failed:**
- Final-layer mean entropy is architecture-dependent; base LLaMA-2-7B produces insufficient entropy spread.
- Direction inversion on LLaMA-2/TriviaQA shows the entropy-correctness relationship is not monotone across models.
- Root cause: scalar signal read only at the final layer is confounded by tokenizer, RLHF status, and per-architecture output calibration.

**Query-filtering implications for Step 2:**
- AVOID: final-layer-only scalar entropy approaches; multi-sample semantic consistency methods (archived fusion direction).
- PRIORITIZE: per-layer / intermediate-representation signals, logit lens / tuned lens, layer-contrast methods (DoLa), architecture-robustness evidence, "alternative to final-layer entropy" queries.

---

## 2. Search Queries Generated

### Query Generation Source Summary

| Source | Count | Priority |
|--------|-------|----------|
| Failure-aware queries (ROUTE_TO_0) | 3 | 🔴 Highest |
| Reference paper queries | 0 (none provided) | — |
| Brainstorm insights queries | 5 | 🥈 High |
| Direct question queries | 8 | 🥉 Standard |
| **Total** | **16** | |

**Failure patterns to avoid** (from h-e1 run 1 + archived fusion attempts):
- Final-layer-only scalar entropy (architecture-dependent, confounded by tokenizer/RLHF/output calibration)
- Assuming monotone entropy-correctness relationship across models (direction inverted on LLaMA-2/TriviaQA)
- Multi-sample semantic consistency fusion (archived without passing run; violates single-pass constraint)

**🔴 Failure-Aware Queries (ROUTE_TO_0):**
- FA1: "alternative to final-layer entropy for hallucination detection — intermediate layer uncertainty signals"
- FA2: "hallucination detection single forward pass without multi-sample consistency"
- FA3: "cross-architecture robustness of LLM confidence signals — RLHF and calibration confounds"

### Priority 1: Reference Paper Concept Queries
*No reference papers provided* — priority slot superseded by failure-aware queries above (ROUTE_TO_0).

### Priority 2: Brainstorm Insights Queries
- B1: "logit lens tuned lens intermediate layer prediction interpretation" (nostalgebraist 2020; Belrose et al. 2023)
- B2: "DoLa decoding by contrasting layers factuality hallucination"
- B3: "hidden state probing truthfulness internal states LLM" (Azaria & Mitchell 2023; INSIDE)
- B4: "layer-wise knowledge localization early exit transformer"
- B5: "base vs instruct model calibration entropy difference RLHF"

### Priority 3: Direct Question Decomposition Queries
- D1 (technical): "logit lens entropy hallucination detection AUROC"
- D2 (technical): "layer-wise uncertainty quantification large language models"
- D3 (technical): "KL divergence between adjacent layer predictions confidence signal"
- D4 (problem-specific): "TriviaQA TruthfulQA hallucination detection AUROC evaluation protocol"
- D5 (problem-specific): "per-layer entropy LLaMA Mistral hallucination"
- D6 (theoretical): "single forward pass uncertainty estimation LLM token probability"
- D7 (comparative): "internal representation vs output probability hallucination detection"
- D8 (technical): "logistic regression fusion of uncertainty features held-out layer selection"

---

## 3. Past Cases & Best Practices (via Archon)

### Direct Implementations

**MCP Server Used:** Archon Knowledge Base (`mcp__archon__rag_search_knowledge_base`, `mcp__archon__rag_search_code_examples`)
**Total Queries:** 9 queries across 3 levels (Level 1: 4, Level 2: 3, Level 3: 2)
**Results Found:** 0 domain-relevant verified cases + 1 marginal API reference + 3 inferred patterns

**[NOT_FOUND - ARCHON]** No direct implementations of logit-lens / layer-wise hallucination detection in KB.
- Queries used (Level 1): "logit lens intermediate layer", "hallucination detection uncertainty", "per-layer entropy hidden states", "DoLa contrasting layers decoding"
- Queries used (Level 2): "transformers output hidden states", "model confidence calibration evaluation", "KL divergence distribution comparison"
- Queries used (Level 3): "layer-wise feature extraction patterns", "extract hidden states forward pass" (code examples)
- All returned pages from source `8b1c7f40739544a6` (HuggingFace diffusers / Stable Diffusion corpus) with aggregate similarity ≤ 0.49 — off-domain for LLM internal-state UQ. KB coverage gap recorded honestly per fallback protocol.

### Similar Architectural Patterns

**[INFERRED]** Pattern 1: Hidden-state extraction via `output_hidden_states=True`
- Source: General knowledge, corroborated by marginal Archon hit (HF transformers T5 doc, KB page `e8650c31-52d5-4d7d-9bbc-c6419eee5ac7`, query "transformers output hidden states")
- HF `model(input_ids, output_hidden_states=True)` returns per-layer hidden states in one forward pass — the exact extraction mechanism logit-lens needs. Note: not verified for LLaMA/Mistral specifically in KB; v1 archive code already implements it.

**[INFERRED]** Pattern 2: Reuse of validated prior-pipeline code as the primary implementation reference
- Source: v1 archive `_archive/20260805T054934_routing_recovery/h-e1/` (validator 18/18 pass, healthy mid-run execution) — a stronger past-case than any KB entry: identical protocol, working environment recipe (torch 2.8.0+cu128, transformers 4.57.6), 871/1000 LLaMA-2/TriviaQA feature cache.
- Reasoning: Archon KB lacks LLM-UQ content; the project's own archived, validated implementation is the authoritative past case.

**[INFERRED]** Pattern 3: Single-pass multi-signal feature pipeline
- Source: General knowledge (Archon search yielded no results)
- Compute all per-layer signals (entropy, max-prob, adjacent-layer KL) in one pass over cached logit-lens distributions; cache features to CSV per model/dataset cell, then do layer selection / fusion offline with scikit-learn. Matches v1's cache-first design and avoids GPU re-runs during analysis.

### Code Examples Found

**[VERIFIED - ARCHON]** Example 1: Encode text and obtain hidden states (HF transformers)
- Source: Archon Knowledge Base (KB Entry ID: page `e8650c31-52d5-4d7d-9bbc-c6419eee5ac7`, source `8b1c7f40739544a6`)
- Search Query: "extract hidden states forward pass" (code examples)

```python
from transformers import AutoTokenizer, T5EncoderModel
tokenizer = AutoTokenizer.from_pretrained("google-t5/t5-small")
model = T5EncoderModel.from_pretrained("google-t5/t5-small")
input_ids = tokenizer("...", return_tensors="pt").input_ids
outputs = model(input_ids=input_ids)
last_hidden_states = outputs.last_hidden_state
```

- Relevance: Marginal — demonstrates HF hidden-state access API only (T5, not decoder-only LLaMA/Mistral). No logit-lens, entropy, or AUROC code in KB. *Domain-relevant code examples: not found in Archon.*

---

## 4. Academic Literature Review (via Semantic Scholar)

### Directly Relevant Papers

**MCP Server Used:** Semantic Scholar (`paper_relevance_search`, `paper_references`)
**Total Queries:** 6 relevance searches + 1 reference-network call (1 rate-limit retry per protocol)
**Results Found:** 17 papers (12 directly relevant, 5 foundational/network)

1. **[VERIFIED - SCHOLAR]** "Eliciting Latent Predictions from Transformers with the Tuned Lens" (2023)
   - Authors: Belrose, Furman, Smith, Halawi, Ostrovsky, McKinney, Biderman, Steinhardt — Citations: 540
   - SS ID: `762ca2711eb167f19b79e39c175708ca15e1f5d7` | arXiv: 2303.08112
   - Query: "tuned lens logit lens transformer intermediate layer prediction" (Round 1)
   - Key Contribution: Affine per-layer probes decode every hidden state to vocabulary distributions; more reliable than raw logit lens; latent-prediction trajectories detect malicious inputs. Core methodological foundation for depth-resolved signals.

2. **[VERIFIED - SCHOLAR]** "DoLa: Decoding by Contrasting Layers Improves Factuality in Large Language Models" (2023)
   - Authors: Chuang, Xie, Luo, Kim, Glass, He — Citations: 410
   - SS ID: `ed5020eeda1fbe8c29b1282d654b34abee22d90f` | arXiv: 2309.03883
   - Query: "DoLa decoding contrasting layers factuality large language models" (Round 1)
   - Key Contribution: Contrasts later-vs-earlier layer logit-lens distributions; factual knowledge localized to particular layers; +12–17% TruthfulQA on LLaMA. Validates that early/late layer prediction differences carry factuality signal — but used for mitigation, not detection scoring.

3. **[VERIFIED - SCHOLAR]** "The Internal State of an LLM Knows When its Lying" (2023)
   - Authors: Azaria, Mitchell — Citations: 739
   - SS ID: `f406aceba4f29cc7cfbe7edb2f52f01374486589` | arXiv: 2304.13734
   - Query: "internal state LLM knows when lying truthfulness classifier hidden states" (Round 1)
   - Key Contribution: Trained classifier on hidden-layer activations detects statement truthfulness (71–83% accuracy); shows hidden states beat raw sentence probability. Uses SUPERVISED probes — contrasts with our training-free per-layer signals.

4. **[VERIFIED - SCHOLAR]** "INSIDE: LLMs' Internal States Retain the Power of Hallucination Detection" (2024)
   - Authors: Chen, Liu, Chen, Gu, Wu, Tao, Fu, Ye — Citations: 339
   - SS ID: `f62acb5a743ea4d47a045460a9ee346c2cec5068` | arXiv: 2402.03744
   - Query: "INSIDE LLM internal states hallucination detection eigenscore" (Round 1)
   - Key Contribution: EigenScore on covariance of multi-sample embeddings in internal space. Internal states > token-level signals, but requires MULTI-SAMPLE generation — our approach is single-pass.

5. **[VERIFIED - SCHOLAR]** "On the Effect of Uncertainty on Layer-wise Inference Dynamics" (2025)
   - Authors: Kim, Yoo, Oh — Citations: 2
   - SS ID: `9ee5502f22697de0cd36d10ced672281810c3be5` | arXiv: 2507.06722
   - Query: "tuned lens logit lens transformer intermediate layer prediction" (Round 1)
   - Key Contribution: ⚠️ CAUTIONARY — Tuned-Lens probability trajectories of certain vs uncertain predictions are largely ALIGNED across 11 datasets / 5 models; challenges simplistic layer-wise uncertainty readouts. Direct adversarial evidence our hypothesis must overcome (note: they track final-token trajectory, not per-layer entropy AUROC with per-model layer selection).

6. **[VERIFIED - SCHOLAR]** "Automatic Layer Selection for Hallucination Detection" (2026)
   - Authors: Wang, Cao, Wilson, Zeng — Citations: 0
   - SS ID: `dea9d2c3db68b34ff3ea18e19cd748a64edb29a4` | arXiv: 2605.26366
   - Query: "layer selection probing hallucination detection which layer best" (Round 1)
   - Key Contribution: 🔑 CLOSEST PRIOR WORK — Confirms hallucination signals stronger in INTERMEDIATE layers than final layer; proposes FEPoID (First Effective Peak of Intrinsic Dimension) training-free layer selection. Uses intrinsic-dimension criterion, NOT logit-lens entropy/KL signals with held-out AUROC selection — our signal family and cross-dataset layer-transfer test remain distinct.

7. **[VERIFIED - SCHOLAR]** "Cross-Layer Attention Probing for Fine-Grained Hallucination Detection" (2025)
   - Authors: Suresh, Aljundi, Nkisi-Orji, Wiratunga — Citations: 3
   - SS ID: `a6c8b0bb26d263da1b2725c5248d9208134a2fae` | arXiv: 2509.09700
   - Query: "layer selection probing hallucination detection which layer best" (Round 1)
   - Key Contribution: CLAP treats activations across the full residual stream as a joint sequence for trained probing; works on greedy responses. Supervised; contrasts with our annotation-free signals.

8. **[VERIFIED - SCHOLAR]** "Improve Decoding Factuality by Token-wise Cross Layer Entropy of Large Language Models" (2025)
   - Authors: Wu, Shen, Liu, Tang, Song, Wang, Cai — Citations: 6
   - SS ID: `8176297a2f2110fcd83f2cf0ee46bed5e7ed8c48` | arXiv: 2502.03199
   - Query: "DoLa decoding contrasting layers factuality large language models" (Round 1)
   - Key Contribution: END — token-wise cross-layer inner-probability changes quantify per-token factual knowledge; corroborates adjacent-layer prediction-shift signal (our KL feature) but applies it to decoding, not detection AUROC.

9. **[VERIFIED - SCHOLAR]** "Unsupervised Real-Time Hallucination Detection based on the Internal States of Large Language Models" (2024)
   - Authors: Su, Wang, Ai, Hu, Wu, Zhou, Liu — Citations: 114
   - SS ID: `411b725522e2747e890ba5acfbf43d22f759c00a` | arXiv: 2403.06448
   - Key Contribution: MIND — unsupervised internal-state detection during inference; HELM benchmark. Still trains a detector on internal states; not a pure statistic of logit-lens distributions.

10. **[VERIFIED - SCHOLAR]** "Entropy-Lens: The Information Signature of Transformer Computations" (2025)
    - Authors: Ali, Caso, Irwin, Liò — Citations: 20
    - SS ID: `5683ce0a1bb309b85c917c87aaa8748316019a12` | arXiv: 2502.16570
    - Key Contribution: Studies per-layer entropy profiles of logit-lens distributions as computation signature — validates our core quantity (layer-wise vocab-distribution entropy) as an informative object, though not aimed at hallucination AUROC gates.

11. **[VERIFIED - SCHOLAR]** "SLED: Self Logits Evolution Decoding" (2024)
    - Authors: Zhang, Juan, Rashtchian, Ferng, Jiang, Chen — Citations: 20
    - SS ID: `99f753f6cae65c01c490d488bec6dc51b42543e9` | arXiv: 2411.02433
    - Key Contribution: Contrasts final-layer vs early-layer logits across model families (1B–45B, MoE) — evidence layer-contrast signals generalize across architectures.

12. **[VERIFIED - SCHOLAR]** "Do LLMs Really Know What They Don't Know? Internal States Mainly Reflect Knowledge Recall Rather Than Truthfulness" (2025)
    - Authors: Chi, Chan, Zhang, Deng — Citations: 2
    - SS ID: `1409461dee4c3bb37ccbe54aebe069a96d036113` | arXiv: 2510.09033
    - Key Contribution: ⚠️ CAUTIONARY — hidden states mainly reflect knowledge recall, not truthfulness; associated hallucinations geometrically overlap factual outputs. Bounds expected AUROC ceilings for internal-state methods.

### Foundational Papers

1. **[VERIFIED - SCHOLAR]** "Detecting hallucinations in large language models using semantic entropy" (2024, Nature)
   - Authors: Farquhar, Kossen, Kuhn, Gal — Citations: 1528
   - SS ID: `f82f49c20c6acc69f884f05e3a9f1ceea91061ce` | arXiv: null (Nature; DOI 10.1038/s41586-024-07421-0)
   - Query: "semantic entropy detecting hallucinations large language models" (Round 4)
   - Relevance: Field-defining entropy-based UQ baseline. Multi-sample method — the exact cost our single-pass approach avoids; also the archived fusion direction we must stay distinct from.

2. **[VERIFIED - SCHOLAR]** "Language Models (Mostly) Know What They Know" (2022)
   - Authors: Kadavath et al. (Anthropic) — Citations: 1836
   - SS ID: `142ebbf4760145f591166bde2564ac70c001e927` | arXiv: 2207.05221
   - Query: "language models mostly know what they know calibration self-evaluation" (Round 4)
   - Relevance: Establishes P(True)/P(IK) self-knowledge and calibration groundwork for all confidence-signal work.

3. **[VERIFIED - SCHOLAR]** "Learned Hallucination Detection in Black-Box LLMs using Token-level Entropy Production Rate" (2025)
   - Authors: Moslonka, Randrianarivo, Garnier, Malherbe — Citations: 11
   - SS ID: `ec46fb59962319da34880e1712aa1c703a5287d0` | arXiv: 2509.04492
   - Relevance: Single-pass token-level entropy signals for QA hallucination detection — final-layer only; foil for our depth-resolved extension.

4. **[VERIFIED - SCHOLAR - CITATION_NETWORK]** "LLMs Know More Than They Show: On the Intrinsic Representation of LLM Hallucinations" (2024)
   - Citations: 237 — SS ID: `82014e61508cbbae8daf549ddb5883fa1f665f92` | arXiv: null (not returned by references endpoint)
   - Retrieved via: `paper_references(Automatic Layer Selection)` — marked [isInfluential]
   - Relevance: Truthfulness info concentrated in specific tokens/intermediate representations; supports intermediate-layer signal premise.

5. **[VERIFIED - SCHOLAR - CITATION_NETWORK]** "Layer by Layer: Uncovering Hidden Representations in Language Models" (2025)
   - Citations: 302 — SS ID: `ae22db103c2954a56787a6c91373ea161841f250` | arXiv: null (not returned by references endpoint)
   - Retrieved via: `paper_references(Automatic Layer Selection)` — marked [isInfluential]
   - Relevance: Systematic evidence intermediate layers carry richer usable representations than final layer.

### Citation Network Analysis

No user-provided reference papers → network anchored on closest prior work "Automatic Layer Selection for Hallucination Detection" (arXiv 2605.26366) via `paper_references` (20 references retrieved).

- **Most influential work in the space:** "A Survey on Hallucination in LLMs" (2023, 3429 cites); "Detecting hallucinations using semantic entropy" (Nature 2024, 1528 cites)
- **Influential references of the anchor** (tagged isInfluential): Semantic Entropy (1528), Layer by Layer (302), LLMs Know More Than They Show (237), INSIDE (339), "Characterizing Truthfulness with Local Intrinsic Dimension" (51), "The Illusion of Progress: Re-evaluating Hallucination Detection" (25)
- **Research lineage:** logit lens (nostalgebraist 2020, blog) → Tuned Lens (Belrose 2023) → DoLa layer-contrast decoding (2023) → internal-state detection (Azaria & Mitchell 2023; INSIDE 2024; MIND 2024) → intermediate-layer detection + automatic layer selection (CLAP 2025; FEPoID 2026)
- **Recent trend:** field converging on "intermediate layers > final layer" for hallucination signal (FEPoID abstract states it as established), but layer selection criteria are geometric (intrinsic dimension) or supervised (probes) — NOT training-free logit-lens entropy/max-prob/adjacent-KL with per-model held-out AUROC selection and cross-dataset transfer validation
- **Direct adversarial thread:** Kim et al. 2025 (aligned trajectories) and Chi et al. 2025 (recall-not-truthfulness) — both must be addressed in hypothesis framing

---

## 5. Implementation Resources (via Exa)

### Directly Relevant Implementations

**MCP Server Used:** Exa Search (`mcp__exa__web_search_exa`, `mcp__exa__get_code_context_exa`)
**Total Queries:** 4 (3 web searches + 1 code-context)
**Results Found:** 6 GitHub repos + 1 PyPI package + 3 tutorials + code-context analysis

1. **[VERIFIED - EXA]** AlignmentResearch/tuned-lens
   - URL: https://github.com/AlignmentResearch/tuned-lens — Stars: 601 — Language: Python (PyTorch) — License: MIT
   - Query: "tuned-lens logit lens pytorch implementation github" (Priority 1)
   - Key Features: Trained affine translators per layer decode hidden states to vocab distributions; `prediction_trajectory` plotting; TransformerLens integration; readthedocs tutorials
   - Adaptability: Reference implementation for per-layer vocabulary decoding; our approach uses raw logit lens (no trained translators) but this validates trajectory extraction API design

2. **[VERIFIED - EXA]** voidism/DoLa (official, ICLR 2024)
   - URL: https://github.com/voidism/DoLa — Stars: 557 — Language: Python — License: MIT
   - Query: "DoLa decoding contrasting layers github implementation" (Priority 1)
   - Key Features: Layer-contrast next-token distribution; TruthfulQA/FACTOR/GSM8K eval harness; premature-layer selection via JS divergence; also upstreamed into HF transformers (<4.53.0; issue #29524)
   - Adaptability: Direct code reference for projecting intermediate layers through unembedding and comparing layer distributions — the same primitive our adjacent-layer KL feature needs

3. **[VERIFIED - EXA]** dasrupdip04/hallushift (fork of sharanya-dasgupta001 origin)
   - URL: https://github.com/dasrupdip04/hallushift — Stars: 0 (fork) — Language: Python — arXiv 2504.09482
   - Query: "hallucination detection benchmark TriviaQA TruthfulQA AUROC uncertainty github code" (Priority 1)
   - Key Features: 🔑 "HalluShift: Measuring Distribution Shifts towards Hallucination Detection in LLMs" — internal-state distribution-shift features for detection; closest implementation to our consecutive-layer KL signal
   - Adaptability: Feature-extraction pipeline design reference; must check exact signal definitions to maintain novelty distinction

4. **[VERIFIED - EXA]** deeplearning-wisc/haloscope (NeurIPS'24 spotlight)
   - URL: https://github.com/deeplearning-wisc/haloscope — Stars: 70 — Language: Python — arXiv 2409.17504
   - Key Features: Unlabeled-generation-based hallucination detection using LLaMA-2-7B/13B internal representations; membership-estimation on hidden states
   - Adaptability: LLaMA-2 hidden-state extraction + QA benchmark evaluation pipeline overlaps our stack

### Component Implementations

1. **[VERIFIED - EXA]** entropy-profiler (PyPI v0.2.0)
   - URL: https://pypi.org/project/entropy-profiler/
   - Query: code-context "huggingface transformers output_hidden_states logit lens per-layer entropy unembedding LLaMA" (Priority 4)
   - Relevance: 🔑 Computes per-layer Shannon/Rényi entropy of logit-lens distributions on any HF CausalLM — LLaMA-2/3 and Mistral explicitly tested. Entropy profile matrix `(n_tokens, n_layers)`; no hooks (`output_hidden_states=True`); handles `model.norm` + `lm_head` unembedding per family
   - Integration potential: Direct component for our per-layer entropy feature; validates architecture-agnostic unembedding resolution pattern

2. **[VERIFIED - EXA]** RUCAIBox/HaluEval
   - URL: https://github.com/RUCAIBox/HaluEval — Stars: 592 — Language: Python — License: MIT
   - Relevance: 35K-sample hallucination evaluation benchmark (QA/dialogue/summarization); complementary labeled data if TriviaQA/TruthfulQA correctness labeling needs cross-checks
   - Integration potential: Secondary evaluation source only; primary protocol stays TriviaQA/TruthfulQA per Phase 0 constraints

3. **[VERIFIED - EXA]** qcri/in-context-uncertainty
   - URL: https://github.com/qcri/in-context-uncertainty — Stars: 0 — Language: Python
   - Relevance: Token-level uncertainty metric extraction pipeline for QA (Qwen/Gemma/Fanar) — recent (2025-08) example of response-generation + uncertainty-feature + visualization pipeline structure

### Tutorial Resources

1. **[VERIFIED - EXA - TUTORIAL]** "LogitLens From Scratch With Hugging Face Transformers" — Alessio Devoto
   - URL: https://alessiodevoto.github.io/LogitLens/
   - Retrieved via code-context query (Priority 4)
   - Key Insights: Full walkthrough — `output_hidden_states=True`, apply `model.lm_head` per layer, compute per-layer entropy from logits (`-sum(p log p)`); exactly our extraction recipe

2. **[VERIFIED - EXA - TUTORIAL]** "Logit Lens: Decoding Transformer Hidden States Layer by Layer" — mbrenndoerfer.com
   - URL: https://mbrenndoerfer.com/writing/logit-lens
   - Key Insights: Formal treatment `LogitLens(ℓ)(h) = W_U · LayerNorm(h)`; discusses known limitation (intermediate states in "input domain") and tuned-lens remedy; per-layer entropy analysis section

3. **[VERIFIED - EXA - TUTORIAL]** tuned-lens readthedocs tutorials
   - URL: https://tuned-lens.readthedocs.io/en/latest/tutorials/training_and_evaluating_lenses.html
   - Key Insights: Training/evaluating lenses, comparing prediction trajectories — relevant if raw logit lens proves too brittle on some architecture (fallback documented in literature)

### Code Analysis

**[VERIFIED - EXA - CODE_CONTEXT]** Implementation patterns for per-layer logit-lens signals:
- Retrieved via: `mcp__exa__get_code_context_exa(query="huggingface transformers output_hidden_states logit lens per-layer entropy unembedding LLaMA", tokensNum=5000)`
- Common pattern (uniform across sources): single forward pass with `output_hidden_states=True` → tuple of `n_layers+1` hidden states `(batch, seq, hidden)` → per layer: `logits = lm_head(final_norm(h))` → `probs = softmax(logits)` → entropy/max-prob/KL
- Architecture resolution: LLaMA-2/3 and Mistral both expose `model.norm` + `lm_head` (verified in entropy-profiler support table and HF `modeling_llama.py` v5.1.0 source); GPT-2 style uses `transformer.ln_f` — our three target families share one code path
- API notes: HF LLaMA `forward` computes `logits = self.lm_head(hidden_states[:, slice_indices, :])` after `outputs.last_hidden_state`; `logits_to_keep` slicing pattern useful for answer-token-only feature extraction
- Framework preferences: PyTorch universal in every found repo (tuned-lens, DoLa, HalluShift, HaloScope); no TF/JAX implementations surfaced
- Architectural insight: no hooks needed anywhere in the stack — matches v1 archive design and keeps single-pass constraint intact

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

1. **Foundation (interpretability):** logit lens (nostalgebraist 2020, blog) established projecting hidden states through the unembedding; Tuned Lens (Belrose et al. 2023, arXiv 2303.08112) made per-layer decoding reliable and showed latent-prediction *trajectories* carry signal (malicious-input detection)
2. **Foundation (calibration/UQ):** Kadavath et al. 2022 (arXiv 2207.05221) — models are (mostly) calibrated; Semantic Entropy (Farquhar et al., Nature 2024) — entropy-based UQ detects confabulations but needs multi-sample generation
3. **Layer-localization of factuality:** DoLa (arXiv 2309.03883) exploited layer-localized factual knowledge for decoding; SLED (arXiv 2411.02433) generalized layer-contrast across families/scales; END (arXiv 2502.03199) showed token-wise cross-layer probability changes quantify factual grounding
4. **Internal-state detection:** Azaria & Mitchell 2023 (supervised hidden-state probes) → INSIDE 2024 (multi-sample EigenScore) → MIND 2024 (unsupervised but trained) → HalluShift 2025 (arXiv 2504.09482; internal distribution-shift features) → CLAP 2025 (cross-layer attention probing)
5. **Layer-selection question emerges:** "LLMs Know More Than They Show" 2024 + "Layer by Layer" 2025 establish intermediate > final representations; Automatic Layer Selection (arXiv 2605.26366) makes principled training-free selection the open problem, solving it with intrinsic dimension (FEPoID)
6. **Research Question:** combines (1) logit-lens per-layer decoding, (3) layer-localized signals incl. adjacent-layer KL, (5) per-model layer selection — but with training-free logit-lens statistics (entropy/max-prob/KL), held-out AUROC selection, cross-dataset layer-transfer validation, and an architecture-robustness stress test on the family where the final layer failed (LLaMA-2-7B, AUROC 0.5186)

**Prior-attempt context (ROUTE_TO_0):** the failed h-e1 run 1 sits at stage 2 (final-layer entropy only); the community's trajectory (stages 3–5) independently corroborates the pivot direction recorded in the failure report ("add per-layer entropy").

### Concept Integration Map

```
Logit-lens per-layer decoding          Entropy-based UQ (single-pass)
(nostalgebraist; Belrose 2023;        (Kadavath 2022; EPR 2025;
 tuned-lens repo, 601★)                h-e1 run 1 final-layer baseline)
        │                                      │
        ├──────────────┬───────────────────────┤
                       ▼
     Per-layer uncertainty signals from ONE greedy pass:
     entropy(ℓ), max-prob(ℓ), KL(ℓ‖ℓ+1)  ← RESEARCH QUESTION
                       ▲
        ├──────────────┴───────────────────────┤
        │                                      │
Layer-localized factuality             Per-model layer selection
(DoLa 557★; SLED; END                  (Automatic Layer Selection/FEPoID;
 cross-layer entropy)                   held-out split + AUROC direction
                                        correction — ours)
                       ▲
     Supporting implementations: entropy-profiler (LLaMA/Mistral tested),
     HalluShift (distribution-shift features), HaloScope (LLaMA-2 pipeline),
     v1 archive code + 871-row cache (validated, protocol-identical)
```

Cautionary constraints integrated into framing: Kim et al. 2025 (trajectories aligned for certain/uncertain — final-token trajectory ≠ per-layer AUROC selection); Chi et al. 2025 (internal states reflect recall, not truthfulness — bounds AUROC ceiling for associated hallucinations).

### Cross-Reference Matrix

| Paper/Resource | Relevance to Question | Implementation Available | Adaptability |
|----------------|----------------------|-------------------------|--------------|
| Tuned Lens (Belrose 2023) | High — per-layer decoding foundation | Yes (601★ repo + docs) | High |
| DoLa (Chuang 2023) | High — layer-contrast primitive | Yes (557★ official + HF) | High |
| Automatic Layer Selection / FEPoID (2026) | Direct — same problem, different criterion | Claimed (github link in abstract) | Medium (comparison target) |
| On Layer-wise Inference Dynamics (Kim 2025) | Direct — adversarial evidence | No | N/A (framing constraint) |
| END cross-layer entropy (2025) | High — adjacent-layer signal | No repo found | Medium (method described) |
| INSIDE (2024) | Medium — internal states, but multi-sample | Not searched | Low (violates single-pass) |
| Azaria & Mitchell (2023) | Medium — supervised probe contrast | Not searched | Low (needs training) |
| Semantic Entropy (Nature 2024) | Medium — baseline family, multi-sample | Yes (known) | Low (excluded direction) |
| entropy-profiler (PyPI) | Direct — per-layer logit-lens entropy | Yes (pip installable) | High |
| HalluShift (2025) | High — distribution-shift features | Yes (repo) | High (novelty check needed) |
| HaloScope (NeurIPS'24) | Medium — LLaMA-2 internal-state pipeline | Yes (70★) | Medium |
| v1 archive `_archive/20260805T054934_routing_recovery/h-e1/` | Direct — identical protocol | Yes (validated code + cache) | High (primary reuse) |

**Architectural patterns observed (no solutions proposed — Phase 1 boundary):**
- Pattern 1: Hook-free extraction — `output_hidden_states=True` + shared `model.norm`/`lm_head` path across all three target families
- Pattern 2: Cache-first two-stage design — GPU pass writes per-layer feature CSV; layer selection/fusion runs offline (v1 archive, HalluShift, HaloScope all follow this)
- Pattern 3: Held-out-split layer/criterion selection with cross-condition transfer reporting (FEPoID paper; audio-deepfake layer-selection literature independently converges on same design)

---

## 7. Verification Status Summary

### Statistics

- Total sources recorded: 31
  - Scholar papers: 17 — all [VERIFIED - SCHOLAR] with SS IDs (100%)
  - Exa resources: 10 — all [VERIFIED - EXA] with full URLs (100%)
  - Archon: 1 marginal [VERIFIED - ARCHON] + 3 [INFERRED] (KB domain mismatch) + 1 [NOT_FOUND - ARCHON] record
- [VERIFIED] total: 28/31 (90%)
- [INFERRED]: 3/31 (10%) — all from Archon fallback protocol, explicitly labeled
- [NOT_FOUND]: 1 recorded honestly (Archon domain-relevant implementations)
- arXiv IDs extracted for Phase 2A: 14 papers with arXiv IDs; 3 marked null (Nature paper; 2 citation-network entries where the references endpoint does not return externalIds)

### MCP Server Performance

- **Archon:** 9 queries (8 KB + 1 code-examples), all returned within normal latency; 0 errors — but KB corpus (HuggingFace diffusers/Stable Diffusion) is off-domain for LLM internal-state UQ; recall limited by corpus, not server
- **Semantic Scholar:** 8 calls (6 relevance searches + 2 reference-network attempts); 1 rate_limit error (recovered on retry after 15 s per protocol) + 1 field-validation error (externalIds not supported on references endpoint; retried with valid fields); effective success 8/8 after retries
- **Exa:** 4 calls (3 web_search + 1 code_context); 0 errors; highest relevance density of the three servers

### Data Quality Assessment

- **Completeness: 88/100** — all six Phase 0 focus areas covered (logit/tuned lens ✓, internal-state detection ✓, layer localization/DoLa ✓, entropy UQ baselines ✓, cross-architecture robustness ✓ partially, adjacent-layer KL ✓ via END/HalluShift); weak spot: no dedicated paper on base-vs-instruct calibration confound found this round
- **Reliability: 90/100** — 90% of sources MCP-verified with IDs/URLs; Archon contribution inferred-only (labeled)
- **Recency: 95/100** — 12 of 17 papers from 2024–2026; includes 2026 preprints at the exact frontier (FEPoID)
- **Relevance to Question: 92/100** — closest prior work identified (Automatic Layer Selection), adversarial papers identified (Kim 2025, Chi 2025), implementation stack fully mapped to the three target model families

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs (gap relevance anchor):**
1. **Main Research Question**: Does per-model selection of depth-resolved uncertainty signals (logit-lens entropy, logit-lens max-token probability, consecutive-layer prediction KL divergence, single greedy pass) achieve hallucination-detection AUROC > 0.60 on TriviaQA and TruthfulQA for LLaMA-2-7B, Mistral-7B, and LLaMA-3-8B — including LLaMA-2-7B where final-layer mean entropy failed (0.5186) — with the best intermediate layer beating the final layer at 95% bootstrap CI separation on LLaMA-2-7B?
2. **Detailed Questions**: (1) intermediate-vs-final layer AUROC on LLaMA-2-7B with CI excluding zero; (2) cross-dataset layer stability TriviaQA↔TruthfulQA; (3) complementarity of adjacent-layer KL via per-model logistic fusion; (4) cross-family consistency of relative signal depth; (5) no regression on Mistral-7B / LLaMA-3-8B
3. **Reference Papers**: Not provided (discovery delegated to Phase 1 — done in Steps 4–5)
4. **ROUTE_TO_0 context**: final-layer scalar entropy failed on LLaMA-2-7B (architecture-dependent calibration confound); multi-sample fusion direction archived — excluded

All gaps below pass the relevance test against these inputs.

### Identified Gaps

#### Gap 1: No training-free, single-pass evaluation of raw logit-lens uncertainty statistics (entropy / max-prob) as per-layer hallucination-detection AUROC scores

**Relevance:** 🎯 PRIMARY — ☑️ Blocks answering the research question: the core claim (per-layer logit-lens signals achieve AUROC > 0.60) has no direct precedent to build on or compare against. ☑️ Relates to detailed questions 1 and 5.

**Current State:** Intermediate-layer hallucination signal is established (FEPoID 2026 states it as known; "LLMs Know More Than They Show" 2024; "Layer by Layer" 2025), but every detection method operating on intermediate layers uses either supervised probes (Azaria & Mitchell 2023; CLAP 2025), geometric criteria over hidden states (FEPoID intrinsic dimension; local intrinsic dimension 2024), or multi-sample generation (INSIDE 2024; semantic entropy 2024). Entropy-Lens 2025 computes exactly our per-layer logit-lens entropy but as a computation signature, not a hallucination-AUROC detector. Kim et al. 2025 examined layer-wise Tuned-Lens trajectories for uncertainty and found certain/uncertain trajectories aligned — but tracked the final-prediction-token trajectory, not per-layer entropy statistics with per-model layer selection and AUROC direction correction.

**Missing Piece:** AUROC evaluation of raw logit-lens entropy and max-token-probability computed at EVERY layer from one greedy pass, with the informative layer selected per-model on a held-out split — on TriviaQA/TruthfulQA across LLaMA-2-7B, Mistral-7B, LLaMA-3-8B.

**Potential Impact:** High — if intermediate layers carry recoverable signal where the final layer failed (LLaMA-2 0.5186), annotation-free single-pass detection becomes architecture-robust at zero extra inference cost.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Automatic Layer Selection for Hallucination Detection" | 2026 | Wang et al. | dea9d2c3db68b34ff3ea18e19cd748a64edb29a4 | 2605.26366 | 0 | Confirms intermediate > final layer signal; selects layers via intrinsic dimension, NOT logit-lens uncertainty statistics — gap remains open |
| "Entropy-Lens: The Information Signature of Transformer Computations" | 2025 | Ali et al. | 5683ce0a1bb309b85c917c87aaa8748316019a12 | 2502.16570 | 20 | Per-layer logit-lens entropy studied as computation signature, never as hallucination-detection AUROC score |
| "On the Effect of Uncertainty on Layer-wise Inference Dynamics" | 2025 | Kim, Yoo, Oh | 9ee5502f22697de0cd36d10ced672281810c3be5 | 2507.06722 | 2 | Adversarial: final-token Tuned-Lens trajectories aligned for certain/uncertain — leaves per-layer statistic AUROC with per-model selection untested |
| "Eliciting Latent Predictions from Transformers with the Tuned Lens" | 2023 | Belrose et al. | 762ca2711eb167f19b79e39c175708ca15e1f5d7 | 2303.08112 | 540 | Reliable per-layer vocab decoding exists; trajectory signal proven for malicious-input detection, not hallucination AUROC |
| "The Internal State of an LLM Knows When its Lying" | 2023 | Azaria, Mitchell | f406aceba4f29cc7cfbe7edb2f52f01374486589 | 2304.13734 | 739 | Hidden-state signal exists but requires SUPERVISED probe training — training-free variant missing |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| HF transformers hidden-state access API (T5 doc; marginal) | e8650c31-52d5-4d7d-9bbc-c6419eee5ac7 | "transformers output hidden states" | `output_hidden_states=True` returns per-layer states in one pass — extraction mechanism confirmed |
| [INFERRED] v1 archive validated pipeline (KB off-domain; project archive used as past case) | N/A (`_archive/20260805T054934_routing_recovery/h-e1/`) | N/A — Archon KB domain mismatch recorded | Protocol-identical validated code + 871/1000 LLaMA-2/TriviaQA feature cache exists; gap is scientific, not infrastructural |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| AlignmentResearch/tuned-lens | https://github.com/AlignmentResearch/tuned-lens | 601 | Python | Per-layer decoding infrastructure exists; no hallucination-AUROC evaluation module |
| entropy-profiler | https://pypi.org/project/entropy-profiler/ | N/A (PyPI) | Python | Per-layer logit-lens entropy for LLaMA/Mistral exists as a profiler — detection evaluation absent |
| deeplearning-wisc/haloscope | https://github.com/deeplearning-wisc/haloscope | 70 | Python | LLaMA-2 internal-state detection pipeline — trains membership estimator, not training-free statistic |

---

#### Gap 2: Cross-dataset stability and cross-architecture consistency of the per-model optimal layer is unmeasured

**Relevance:** 🎯 PRIMARY — ☑️ Blocks answering the research question: AUROC > 0.60 "for all three model families on both datasets" requires the selected layer to transfer across datasets; if selection overfits the held-out split, the protocol fails. ☑️ Directly addresses detailed questions 2 and 4.

**Current State:** Layer-selection methods exist (FEPoID intrinsic-dimension criterion; DoLa dynamic JS-divergence premature-layer selection; CLAP joint residual-stream probing), and the audio-deepfake literature independently shows informative layers cluster in depth zones that are backbone-specific. But no published work measures whether a hallucination-detection layer selected on one QA dataset (TriviaQA) transfers to another (TruthfulQA) for the same model, nor whether relative signal depth (layer index / total layers) is consistent across LLaMA-2, Mistral, and LLaMA-3 families.

**Missing Piece:** A layer-transfer experiment: select layer on dataset A's held-out split, evaluate AUROC on dataset B (and vice versa), per model; plus a cross-family comparison of relative optimal depth. No dataset↔dataset transfer numbers exist anywhere in the collected corpus.

**Potential Impact:** High — layer stability determines whether depth-resolved detection is deployable (fixed layer per model) or requires per-domain recalibration; cross-family depth consistency determines whether "depth of signal" is itself an architecture-dependent quantity.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Automatic Layer Selection for Hallucination Detection" | 2026 | Wang et al. | dea9d2c3db68b34ff3ea18e19cd748a64edb29a4 | 2605.26366 | 0 | Evaluates selection criteria across tasks but reports no dataset→dataset transfer of a fixed selected layer |
| "DoLa: Decoding by Contrasting Layers" | 2023 | Chuang et al. | ed5020eeda1fbe8c29b1282d654b34abee22d90f | 2309.03883 | 410 | Layer choice matters (high vs low buckets per task type) — evidence layer optimality is task-sensitive, transfer unquantified |
| "Cross-Layer Attention Probing for Fine-Grained Hallucination Detection" | 2025 | Suresh et al. | a6c8b0bb26d263da1b2725c5248d9208134a2fae | 2509.09700 | 3 | Sidesteps selection by consuming ALL layers jointly — implicit evidence single-layer stability is unresolved |
| "SLED: Self Logits Evolution Decoding" | 2024 | Zhang et al. | 99f753f6cae65c01c490d488bec6dc51b42543e9 | 2411.02433 | 20 | Layer-contrast works across families/scales — cross-family generalization plausible but depth consistency unmeasured |
| "Layer by Layer: Uncovering Hidden Representations in Language Models" | 2025 | (citation network) | ae22db103c2954a56787a6c91373ea161841f250 | null | 302 | Intermediate-layer superiority is general — but which depth, and its stability, left open |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| [NOT_FOUND - ARCHON] No KB entries on layer selection/transfer | N/A | "layer-wise feature extraction patterns" (Level 3) | KB corpus off-domain (diffusion models); gap evidence rests on Scholar + Exa |
| [INFERRED] Held-out selection protocol from v1 archive design | N/A (project archive) | N/A | v1 already implements per-model held-out layer selection; the transfer measurement (dataset↔dataset) was planned but never reached before interruption |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| voidism/DoLa | https://github.com/voidism/DoLa | 557 | Python | Dynamic premature-layer selection code (JS divergence) — per-decoding-step, not per-model fixed-layer with transfer eval |
| AlignmentResearch/tuned-lens | https://github.com/AlignmentResearch/tuned-lens | 601 | Python | Prediction-trajectory comparison tooling usable for depth-consistency analysis; no transfer experiments shipped |
| RUCAIBox/HaluEval | https://github.com/RUCAIBox/HaluEval | 592 | Python | Multi-task labeled hallucination data — enables cross-domain checks, none published for layer stability |

---

#### Gap 3: Adjacent-layer prediction KL divergence untested as a detection-time signal, and the final-layer-failure architecture (base LLaMA-2-7B) never used as a rescue stress test

**Relevance:** 🎯 PRIMARY — ☑️ Blocks answering the research question: the KL-complementarity claim (detailed question 3) and the LLaMA-2 rescue claim (detailed question 1) have no direct empirical precedent. ☑️ Addresses detailed questions 1 and 3; ⚠️ base-vs-instruct calibration confound (root cause of h-e1 failure) only indirectly covered in found literature.

**Current State:** Adjacent-layer distribution shift is used at DECODING time: END (2025) uses cross-layer inner-probability changes to reweight tokens; DoLa contrasts premature/mature layers to improve generation; HalluShift (2025) measures internal-state distribution shifts for detection but its feature set (per its abstract) is not per-layer logit-lens KL from a single greedy pass. The h-e1 failure record documents that final-layer entropy fails specifically on base LLaMA-2-7B with direction inversion — no paper in the corpus evaluates whether intermediate-layer signals rescue an architecture where the final-layer signal demonstrably failed, and Chi et al. 2025 warn internal states may reflect recall rather than truthfulness (associated hallucinations overlap factual geometry).

**Missing Piece:** (a) AUROC evaluation of KL(layer ℓ ‖ layer ℓ+1) of logit-lens distributions as a hallucination score and its fusion gain over per-layer entropy (per-model logistic regression); (b) a controlled rescue test on LLaMA-2-7B/TriviaQA where final-layer AUROC = 0.5186 is the documented baseline; (c) evidence whether per-layer signals evade the RLHF/tokenizer output-calibration confound.

**Potential Impact:** High — (a) determines whether the multi-signal design adds value or collapses to entropy alone; (b) is the falsification gate inherited from h-e1; (c) addresses architecture-robustness, the central claim of the pivot.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Improve Decoding Factuality by Token-wise Cross Layer Entropy" (END) | 2025 | Wu et al. | 8176297a2f2110fcd83f2cf0ee46bed5e7ed8c48 | 2502.03199 | 6 | Cross-layer probability change correlates with factuality — used for decoding reweighting, never as detection AUROC score |
| "DoLa: Decoding by Contrasting Layers" | 2023 | Chuang et al. | ed5020eeda1fbe8c29b1282d654b34abee22d90f | 2309.03883 | 410 | Layer-contrast distributions carry factual signal (mitigation setting); detection-time use unevaluated |
| "Do LLMs Really Know What They Don't Know?" | 2025 | Chi et al. | 1409461dee4c3bb37ccbe54aebe069a96d036113 | 2510.09033 | 2 | Adversarial bound: internal states reflect recall, not truthfulness — rescue test must control for associated hallucinations |
| "INSIDE: LLMs' Internal States Retain the Power of Hallucination Detection" | 2024 | Chen et al. | f62acb5a743ea4d47a045460a9ee346c2cec5068 | 2402.03744 | 339 | Internal-state detection strong but multi-sample — single-pass KL variant absent from literature |
| "Language Models (Mostly) Know What They Know" | 2022 | Kadavath et al. | 142ebbf4760145f591166bde2564ac70c001e927 | 2207.05221 | 1836 | Calibration varies with model/format — grounds the RLHF/calibration confound h-e1 identified |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| [NOT_FOUND - ARCHON] No KB entries on KL-divergence detection signals | N/A | "KL divergence distribution comparison" (Level 2) | KB corpus off-domain; gap evidence rests on Scholar + Exa + failure record |
| [INFERRED] h-e1 run 1 failure record (Serena Memory `failure_h-e1_run1`) | N/A (project memory) | N/A | Documented final-layer failure baseline: LLaMA-2-7B AUROC 0.5186, direction inverted on TriviaQA — the rescue-test anchor no external work possesses |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| dasrupdip04/hallushift | https://github.com/dasrupdip04/hallushift | 0 (fork) | Python | Distribution-shift detection features — closest existing code; per-layer logit-lens KL from single greedy pass not among its features (novelty check pending in Phase 2) |
| voidism/DoLa | https://github.com/voidism/DoLa | 557 | Python | Working code for layer-pair distribution comparison via unembedding projection — the KL primitive |
| deeplearning-wisc/haloscope | https://github.com/deeplearning-wisc/haloscope | 70 | Python | LLaMA-2-7B TriviaQA/TruthfulQA detection pipeline — protocol overlap for the rescue stress test |

---

### Gap Priority Matrix

| Gap ID | Title | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|--------|------------|----------------|----------|
| Gap 1 | Training-free single-pass per-layer logit-lens AUROC evaluation missing | High | Medium (v1 code + cache reusable) | 10 sources (5 Scholar + 2 Archon + 3 Exa) | Critical |
| Gap 2 | Cross-dataset layer stability + cross-family depth consistency unmeasured | High | Medium (needs both datasets × 3 models) | 10 sources (5 Scholar + 2 Archon + 3 Exa) | Critical |
| Gap 3 | Adjacent-layer KL as detection signal + LLaMA-2 rescue stress test absent | High | Medium-High (fusion + controlled baseline) | 10 sources (5 Scholar + 2 Archon + 3 Exa) | Critical |

Relevance classifications: all three gaps 🎯 PRIMARY (directly block answering the research question).

### User Input to Gap Traceability

**Main research question** (per-layer signals, AUROC > 0.60, all three families, LLaMA-2 rescue) directly addressed by:
- Gap 1: the core per-layer logit-lens AUROC evaluation nobody has run
- Gap 2: the "all three families on both datasets" clause requires layer transfer/stability
- Gap 3: the LLaMA-2-7B rescue clause and CI-separation clause

**Detailed questions** addressed by:
- DQ1 (intermediate beats final on LLaMA-2, CI excludes zero) → Gap 1 + Gap 3
- DQ2 (layer transfer TriviaQA↔TruthfulQA) → Gap 2
- DQ3 (KL complementarity via logistic fusion) → Gap 3
- DQ4 (relative depth consistency across families) → Gap 2
- DQ5 (no regression on Mistral/LLaMA-3) → Gap 1
- ROUTE_TO_0 lessons (avoid final-layer-only scalar signals; avoid multi-sample) → all gaps framed within single-pass, per-layer constraint

**Reference papers:** none provided — gaps grounded instead in discovered corpus (17 Scholar papers, 10 Exa resources) and the project's own h-e1 failure record.

---

## 9. Conclusion

### Key Findings

1. **Premise independently confirmed:** Intermediate-layer superiority for hallucination signal is now published consensus (FEPoID 2026 states it as established; 302-cite and 237-cite supporting papers) — the failure record's "add per-layer entropy" suggestion was prescient.
2. **Exact niche open:** No training-free, single-greedy-pass, per-layer logit-lens uncertainty statistic evaluated as detection AUROC with per-model held-out layer selection. Nearest neighbors: FEPoID (intrinsic dimension, not logit-lens stats), Entropy-Lens (same quantity, no detection eval), CLAP/Azaria (supervised), INSIDE/semantic entropy (multi-sample).
3. **Adjacent-layer KL validated as signal family, unused for detection:** END (2025) and DoLa use cross-layer prediction shifts at decoding time; HalluShift measures internal distribution shifts with different features — detection-time per-layer logit-lens KL remains unevaluated.
4. **Adversarial evidence exists and is addressable:** Kim et al. 2025 (aligned trajectories — but tracks final-prediction-token trajectory, not per-layer statistic AUROC); Chi et al. 2025 (internal states reflect recall, not truthfulness — bounds ceiling for associated hallucinations).
5. **Cross-dataset layer transfer is unmeasured anywhere** — the deployability question (fixed layer per model?) is original to this protocol.
6. **Implementation fully de-risked:** identical extraction pattern across all three model families (`output_hidden_states=True` → `model.norm` → `lm_head`); v1 archive has validated code + environment recipe + 87% of first cell cached.

### Answer to Detailed Question (Preliminary)

Data-grounded status per detailed question (no hypothesis generation — Phase 1 boundary):

- **DQ1 (intermediate beats final on LLaMA-2):** Plausible per literature consensus on intermediate-layer signal; direct evidence absent; Kim 2025 counter-signal noted. → Open, testable.
- **DQ2 (layer transfer across datasets):** No published measurements found in any direction. → Fully open.
- **DQ3 (KL complementarity):** Cross-layer shift signal validated in decoding contexts (END, DoLa); fusion gain for detection unmeasured. → Open, primitives exist.
- **DQ4 (relative depth consistency across families):** Depth-zone clustering observed in adjacent domains (audio SSL layer-selection); backbone-specificity expected; no LLM hallucination data. → Fully open.
- **DQ5 (no regression on Mistral/LLaMA-3):** Final-layer baselines passed in h-e1 run 1 (0.53–0.66); SLED shows layer-contrast generalizes across families. → Open, favorable prior evidence.

### Phase 2 Readiness

- [x] Research question + 5 detailed questions recorded (Section 1)
- [x] ROUTE_TO_0 lessons captured with query-filtering constraints (Section 1)
- [x] 3 PRIMARY gaps with full evidence tables in Phase 2A-extractable format (Section 8)
- [x] 14 papers with arXiv IDs for Phase 2A download; SS IDs for all 17
- [x] Closest prior work (FEPoID) and adversarial papers (Kim 2025, Chi 2025) flagged for novelty/framing
- [x] Implementation resources mapped with URLs, stars, adaptability ratings
- [x] Reusable v1 assets documented (`_archive/20260805T054934_routing_recovery/h-e1/`)
- [x] Verification statistics: 90% MCP-verified, inferred content labeled
- [x] Phase boundary respected: no hypotheses, no solutions, no experiment designs

### Next Steps

Proceed to **Phase 2A-Dialogue — Hypothesis Generation** (`/phase2a-dialogue`), which reads the compact report (`01_targeted_research.md`) to generate testable hypotheses from the three PRIMARY gaps. Phase 2A should:
1. Anchor hypotheses to Gap 1–3 evidence tables
2. Address the two adversarial papers (Kim 2025, Chi 2025) in falsifiability framing
3. Verify novelty against FEPoID (arXiv 2605.26366) and HalluShift (arXiv 2504.09482)
4. Respect single-pass and no-multi-sample constraints from ROUTE_TO_0 lessons

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~12 minutes (05:53–06:05 UTC, 2026-08-05, unattended)*
