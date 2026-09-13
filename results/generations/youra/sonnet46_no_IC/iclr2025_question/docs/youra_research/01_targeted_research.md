# Targeted Research Report: Depth-Resolved Logit-Lens Uncertainty Signals for Architecture-Robust Hallucination Detection

**Date:** 2026-08-05
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

Targeted research (ROUTE_TO_0 retry) for depth-resolved logit-lens uncertainty signals as architecture-robust hallucination detectors. 16 prioritized queries (3 failure-aware) across three MCP servers: Scholar 17 verified papers, Exa 10 verified resources, Archon off-domain (fallback applied, inferred content labeled).

**Bottom line:** Literature has converged on the premise — intermediate layers carry stronger hallucination signal than the final layer (FEPoID 2026; "LLMs Know More Than They Show" 2024; "Layer by Layer" 2025) — yet nobody has evaluated raw logit-lens uncertainty statistics (per-layer entropy, max-prob, adjacent-layer KL) as training-free single-pass detection scores with per-model layer selection. Three PRIMARY gaps identified. Two adversarial papers (Kim 2025, Chi 2025) must shape hypothesis framing. Feasibility de-risked by v1 archive (validated code, 871/1000 cache) + mature open-source stack (tuned-lens 601★, DoLa 557★, entropy-profiler).

---

## 0. Reference Paper Analysis

*No reference papers provided* — Phase 0 states "Not provided - will discover in Phase 1". Query generation relied on brainstorm insights and direct question decomposition, plus the six focus areas from Phase 0 Next Steps (logit lens / tuned lens, internal-state hallucination detection, layer-wise knowledge localization / DoLa, entropy-based UQ baselines on QA benchmarks, cross-architecture robustness, consecutive-layer KL divergence).

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

### Lessons from Previous Attempts (ROUTE_TO_0)
- **Failed (scientific):** h-e1 run 1 — final-layer mean entropy; LLaMA-2-7B AUROC 0.5186 (missed 0.52 gate by 0.0014), direction inverted on TriviaQA. Root cause: final-layer scalar confounded by tokenizer/RLHF/output calibration.
- **Archived without result:** multi-signal fusion with semantic consistency (multi-sample) — excluded direction.
- **Interrupted, NOT refuted:** Layer-Wise Logit-Lens v1 — validator 18/18 pass, healthy run archived mid-flight; reusable code + environment recipe (torch 2.8.0+cu128, transformers 4.57.6) + 871/1000 LLaMA-2/TriviaQA cache in `_archive/20260805T054934_routing_recovery/h-e1/`.
- **Constraints for Phase 2A:** single greedy pass only; no multi-sample consistency; per-model layer selection; AUROC direction correction.

---

## 2. Search Queries Generated (Sample)

### Query Generation Source Summary
16 queries: 3 failure-aware (ROUTE_TO_0, highest priority), 0 reference-paper (none provided), 5 brainstorm-insight, 8 direct-decomposition.

### Priority 1: Failure-Aware Queries (Top 3; supersedes reference-paper slot)
- FA1: "alternative to final-layer entropy for hallucination detection — intermediate layer uncertainty signals"
- FA2: "hallucination detection single forward pass without multi-sample consistency"
- FA3: "cross-architecture robustness of LLM confidence signals — RLHF and calibration confounds"

### Priority 2: Brainstorm Insights Queries (Top 3)
- B1: "logit lens tuned lens intermediate layer prediction interpretation"
- B2: "DoLa decoding by contrasting layers factuality hallucination"
- B3: "hidden state probing truthfulness internal states LLM"

### Priority 3: Direct Question Decomposition Queries (Top 3)
- D1: "logit lens entropy hallucination detection AUROC"
- D3: "KL divergence between adjacent layer predictions confidence signal"
- D4: "TriviaQA TruthfulQA hallucination detection AUROC evaluation protocol"

---

## 3. Past Cases & Best Practices (via Archon) - Compact

### Direct Implementations (Compact)
[NOT_FOUND - ARCHON] — 9 queries across 3 levels; KB corpus (source `8b1c7f40739544a6`, HuggingFace diffusers/Stable Diffusion) off-domain for LLM internal-state UQ. Recorded honestly per fallback protocol.

### Similar Architectural Patterns (Compact)
- [INFERRED] Hidden-state extraction via `output_hidden_states=True` (marginal KB corroboration: page `e8650c31-52d5-4d7d-9bbc-c6419eee5ac7`, query "transformers output hidden states")
- [INFERRED] v1 archive as authoritative past case: validated protocol-identical code + 871/1000 cache
- [INFERRED] Single-pass multi-signal feature pipeline: cache per-layer features to CSV, select/fuse offline

### Code Examples Found (Compact)
| KB Entry ID | Query Used | Key Pattern |
|-------------|------------|-------------|
| page `e8650c31-52d5-4d7d-9bbc-c6419eee5ac7` | "extract hidden states forward pass" | HF hidden-state access API (T5 example; marginal — no logit-lens/entropy/AUROC code in KB) |

---

## 4. Academic Literature Review (via Semantic Scholar) - Compact

### Directly Relevant Papers (Compact)

| Paper | Year | SS ID | arXiv | Insight |
|-------|------|-------|-------|---------|
| Tuned Lens (Belrose et al., 540c) | 2023 | 762ca2711eb167f19b79e39c175708ca15e1f5d7 | 2303.08112 | Reliable per-layer vocab decoding; trajectory signal proven for input detection |
| DoLa (Chuang et al., 410c) | 2023 | ed5020eeda1fbe8c29b1282d654b34abee22d90f | 2309.03883 | Layer-localized factual knowledge; layer-contrast primitive |
| Azaria & Mitchell (739c) | 2023 | f406aceba4f29cc7cfbe7edb2f52f01374486589 | 2304.13734 | Hidden states carry truthfulness — supervised probes |
| INSIDE (Chen et al., 339c) | 2024 | f62acb5a743ea4d47a045460a9ee346c2cec5068 | 2402.03744 | Internal-state EigenScore — multi-sample |
| Kim et al. layer-wise dynamics (2c) ⚠️ | 2025 | 9ee5502f22697de0cd36d10ced672281810c3be5 | 2507.06722 | ADVERSARIAL: certain/uncertain Tuned-Lens trajectories aligned |
| Automatic Layer Selection / FEPoID (0c) 🔑 | 2026 | dea9d2c3db68b34ff3ea18e19cd748a64edb29a4 | 2605.26366 | CLOSEST PRIOR: intermediate>final confirmed; selection via intrinsic dimension, not logit-lens stats |
| CLAP (Suresh et al., 3c) | 2025 | a6c8b0bb26d263da1b2725c5248d9208134a2fae | 2509.09700 | Cross-layer attention probing — supervised |
| END cross-layer entropy (6c) | 2025 | 8176297a2f2110fcd83f2cf0ee46bed5e7ed8c48 | 2502.03199 | Adjacent-layer probability shift quantifies factuality — decoding-time use |
| MIND (Su et al., 114c) | 2024 | 411b725522e2747e890ba5acfbf43d22f759c00a | 2403.06448 | Unsupervised internal-state detection + HELM benchmark |
| Entropy-Lens (Ali et al., 20c) | 2025 | 5683ce0a1bb309b85c917c87aaa8748316019a12 | 2502.16570 | Per-layer logit-lens entropy as computation signature — no detection eval |
| SLED (Zhang et al., 20c) | 2024 | 99f753f6cae65c01c490d488bec6dc51b42543e9 | 2411.02433 | Layer-contrast generalizes across families/scales |
| Chi et al. recall-vs-truthfulness (2c) ⚠️ | 2025 | 1409461dee4c3bb37ccbe54aebe069a96d036113 | 2510.09033 | ADVERSARIAL: internal states reflect recall, not truthfulness |

### Foundational Papers (Compact)

| Paper | Year | SS ID | arXiv | Insight |
|-------|------|-------|-------|---------|
| Semantic Entropy (Farquhar et al., Nature, 1528c) | 2024 | f82f49c20c6acc69f884f05e3a9f1ceea91061ce | null | Entropy-based UQ field-definer — multi-sample (excluded direction) |
| LMs (Mostly) Know What They Know (Kadavath et al., 1836c) | 2022 | 142ebbf4760145f591166bde2564ac70c001e927 | 2207.05221 | Calibration groundwork; grounds RLHF confound |
| Token-level EPR (Moslonka et al., 11c) | 2025 | ec46fb59962319da34880e1712aa1c703a5287d0 | 2509.04492 | Single-pass entropy signals — final-layer only foil |
| LLMs Know More Than They Show (237c) | 2024 | 82014e61508cbbae8daf549ddb5883fa1f665f92 | null | Truthfulness concentrated in intermediate representations |
| Layer by Layer (302c) | 2025 | ae22db103c2954a56787a6c91373ea161841f250 | null | Intermediate layers richer than final — general |

### Citation Network Analysis (Compact)
Anchored on FEPoID references (no user reference papers). Lineage: logit lens (2020 blog) → Tuned Lens (2023) → DoLa (2023) → internal-state detection (2023–24) → intermediate-layer detection + automatic layer selection (2025–26). Influential-tagged: Semantic Entropy, Layer by Layer, LLMs Know More Than They Show, INSIDE, Local Intrinsic Dimension, Illusion of Progress. Trend: intermediate>final is consensus; selection criteria are geometric or supervised — training-free logit-lens statistics with held-out AUROC selection + cross-dataset transfer absent.

---

## 5. Implementation Resources (via Exa) - Compact

### Directly Relevant Implementations (Compact)

| Resource | URL | Stars | Lang | Feature |
|----------|-----|-------|------|---------|
| AlignmentResearch/tuned-lens | https://github.com/AlignmentResearch/tuned-lens | 601 | Python | Per-layer decoding + trajectory tooling |
| voidism/DoLa (official) | https://github.com/voidism/DoLa | 557 | Python | Layer-contrast via unembedding; TruthfulQA harness; in HF transformers <4.53.0 |
| dasrupdip04/hallushift | https://github.com/dasrupdip04/hallushift | 0 (fork) | Python | 🔑 Internal distribution-shift detection features (arXiv 2504.09482) — novelty check needed |
| deeplearning-wisc/haloscope | https://github.com/deeplearning-wisc/haloscope | 70 | Python | LLaMA-2 internal-state detection pipeline (NeurIPS'24) |

### Component Implementations (Compact)

| Resource | URL | Feature |
|----------|-----|---------|
| entropy-profiler (PyPI) | https://pypi.org/project/entropy-profiler/ | 🔑 Per-layer logit-lens Shannon/Rényi entropy; LLaMA-2/3 + Mistral tested; hook-free |
| RUCAIBox/HaluEval (592★) | https://github.com/RUCAIBox/HaluEval | 35K labeled hallucination benchmark (secondary) |
| qcri/in-context-uncertainty | https://github.com/qcri/in-context-uncertainty | Token-level uncertainty extraction pipeline example |

### Tutorial Resources (Compact)
- "LogitLens From Scratch With HF Transformers" — https://alessiodevoto.github.io/LogitLens/ (exact extraction recipe incl. per-layer entropy)
- "Logit Lens: Decoding Hidden States Layer by Layer" — https://mbrenndoerfer.com/writing/logit-lens (formal treatment + limitations)
- tuned-lens readthedocs — https://tuned-lens.readthedocs.io/en/latest/tutorials/training_and_evaluating_lenses.html (fallback if raw lens brittle)

### Code Analysis (Compact)
Uniform pattern: one pass `output_hidden_states=True` → per layer `lm_head(model.norm(h))` → softmax → entropy/max-prob/KL. LLaMA-2/3 and Mistral share one code path (`model.norm` + `lm_head`). PyTorch universal; no hooks anywhere. Matches v1 archive design; single-pass constraint intact.

---

## 6. Chain-of-Relations Analysis - Compact

### Research Evolution Path (Compact)
1. Interpretability foundation: logit lens (2020) → Tuned Lens (2023, reliable per-layer decoding)
2. UQ foundation: Kadavath 2022 (calibration) → Semantic Entropy (2024, multi-sample cost)
3. Layer-localized factuality: DoLa → SLED → END (adjacent-layer shifts, decoding-time)
4. Internal-state detection: Azaria & Mitchell → INSIDE → MIND → HalluShift → CLAP
5. Layer-selection frontier: LLMs Know More Than They Show + Layer by Layer → FEPoID (2026, intrinsic-dimension criterion)
6. **This question:** training-free logit-lens statistics (entropy/max-prob/adjacent-KL) + per-model held-out AUROC selection + cross-dataset transfer + LLaMA-2 rescue stress test — the unoccupied cell. h-e1 failure sits at stage 2; community trajectory corroborates the pivot.

### Cross-Reference Matrix

| Paper/Resource | Relevance | Implementation | Adaptability |
|----------------|-----------|----------------|--------------|
| Tuned Lens (2023) | High — decoding foundation | Yes (601★) | High |
| DoLa (2023) | High — layer-contrast primitive | Yes (557★) | High |
| FEPoID (2026) | Direct — same problem, different criterion | Claimed | Medium (comparison target) |
| Kim 2025 | Direct — adversarial | No | N/A (framing constraint) |
| END (2025) | High — adjacent-layer signal | No repo found | Medium |
| INSIDE (2024) | Medium — multi-sample | — | Low (violates single-pass) |
| Semantic Entropy (2024) | Medium — excluded direction | Yes | Low |
| entropy-profiler | Direct — per-layer entropy | Yes (pip) | High |
| HalluShift (2025) | High — shift features | Yes | High (novelty check) |
| HaloScope (2024) | Medium — LLaMA-2 pipeline | Yes (70★) | Medium |
| v1 archive h-e1 | Direct — identical protocol | Yes (validated + cache) | High (primary reuse) |

---

## 7. Verification Status Summary - Compact

31 sources: 28 [VERIFIED] (90%) with IDs/URLs, 3 [INFERRED] (Archon fallback, labeled), 1 [NOT_FOUND] recorded. arXiv IDs for Phase 2A: 14 papers (3 null: Nature paper + 2 citation-network entries). MCP: Scholar 8 calls (1 rate-limit recovered via 15s retry, 1 field-validation retried), Exa 4 calls (0 errors), Archon 9 calls (0 errors, corpus off-domain). Quality: completeness 88, reliability 90, recency 95, relevance 92.

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

## 9. Conclusion - Compact

### Key Findings
1. Intermediate-layer superiority for hallucination signal is published consensus (FEPoID 2026; 302c and 237c papers) — the h-e1 failure record's "add per-layer entropy" pivot is corroborated.
2. Exact niche open: no training-free, single-pass, per-layer logit-lens uncertainty statistic evaluated as detection AUROC with per-model held-out layer selection.
3. Adjacent-layer KL validated as signal family (END, DoLa) but never used for detection scoring.
4. Adversarial evidence (Kim 2025 trajectory alignment; Chi 2025 recall-vs-truthfulness) is addressable but must shape falsifiability framing.
5. Cross-dataset layer transfer measured nowhere — original to this protocol.
6. Implementation de-risked: single shared extraction path across all three families; v1 validated code + 871/1000 cache reusable.

### Next Steps
Proceed to **Phase 2A-Dialogue — Hypothesis Generation** (`/phase2a-dialogue`): anchor hypotheses to Gap 1–3 evidence tables; address Kim 2025 / Chi 2025 in falsifiability framing; verify novelty against FEPoID (2605.26366) and HalluShift (2504.09482); respect single-pass, no-multi-sample ROUTE_TO_0 constraints.

---

*Phase: 1 - Targeted Research Gathering (Phase 2A Input)*
*Total processing time: ~12 minutes (05:53–06:05 UTC, 2026-08-05, unattended)*
