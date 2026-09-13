# Targeted Research Report (Compact — Phase 2A Input)
# Full report: 01_targeted_research_full.md

**Research Question:** Do self-consistency uncertainty signals derived from N=5–10 stochastic samples (lexical consistency via ROUGE/BERTScore variance, semantic cluster entropy via NLI-based grouping, and entailment consistency via cross-sample contradiction detection) achieve AUROC ≥ 0.85 for hallucination detection on TriviaQA dev and TruthfulQA, outperforming the single-greedy-pass log-probability ensemble [min_logprob, full_sequence_variance] (AUROC ~0.82) established in h-e2/h-m1, using open-weight LLMs (Llama-3.1-8B, Qwen-2.5-7B) on existing benchmark splits without any fine-tuning or hidden-state extraction?

**Date:** 2026-08-02 | **Phase:** 1 - Targeted Research Gathering

---

## 0. Reference Paper Analysis

*No reference papers provided. All discovered in Phase 1.*

---

## 1. Research Questions

### Primary Research Question
Do self-consistency uncertainty signals derived from N=5–10 stochastic samples (lexical consistency via ROUGE/BERTScore variance, semantic cluster entropy via NLI-based grouping, and entailment consistency via cross-sample contradiction detection) achieve AUROC ≥ 0.85 for hallucination detection on TriviaQA dev and TruthfulQA, outperforming [min_logprob, full_sequence_variance] (AUROC ~0.82), using Llama-3.1-8B, Qwen-2.5-7B without fine-tuning or hidden-state extraction?

### Detailed Research Questions
1. (Q1) Which consistency metric (ROUGE variance, BERTScore pairwise, NLI-cluster entropy, contradiction rate) achieves highest AUROC on TriviaQA dev N=5 temp=0.7?
2. (Q2) Does NLI-cluster SE outperform lexical metrics on TriviaQA + TruthfulQA same N, controlling cost?
3. (Q3) Does consistency + [min_logprob, full_sequence_variance] via logistic regression reach AUROC ≥ 0.87 on TriviaQA dev holdout?
4. (Q4) AUROC degradation N=10→3, cost-efficiency frontier for short-answer QA?
5. (Q5) Cross-model AUROC delta Llama-3.1-8B vs Qwen-2.5-7B < 0.05 without recalibration?

### Lessons from Previous Attempts (ROUTE_TO_0)
- h-e1 FAIL: Hidden-state trajectory SVD correlated 0.952 with token count. AUROC 0.537 after OLS. AVOID trajectory concatenation.
- h-e2 PARTIAL: mean_token_entropy ≈ -log_prob in greedy decode (collinear). Fallback: [min_logprob, content_token_variance] AUROC ~0.82.
- h-m1 LIMITATION: POS-filtered variance AUROC 0.8008 < full-sequence 0.8250. AVOID POS filtering.
- AVOID: hidden-state extraction, POS filtering, greedy-only collinear features.

---

## 2. Search Queries (Top 3 per category)

**Reference queries:** "Kuhn semantic uncertainty NLI cluster entropy TriviaQA"; "SelfCheckGPT Manakul zero-resource black-box hallucination"; "Wang self-consistency chain of thought reasoning"

**Brainstorm queries:** "NLI-cluster semantic entropy multiple LLM samples hallucination AUROC"; "combining log-probability ensemble consistency signals logistic regression AUROC"; "N-sample efficiency consistency uncertainty estimation cost-performance"

**Direct queries:** "self-consistency ROUGE BERTScore variance hallucination detection LLM"; "AUROC hallucination detection benchmark open-weight LLM without fine-tuning"; "stochastic sampling temperature hallucination uncertainty TriviaQA TruthfulQA"

---

## 3. Archon KB Search

**[INFERRED]** Domain mismatch — Archon KB contains image/diffusion model content only (13 queries, max similarity 0.48). No LLM UQ content. All Archon entries are [INFERRED] from general knowledge. Implementation evidence from Scholar+Exa only.

---

## 4. Academic Literature (via Semantic Scholar)

**15 papers found. 7/7 Phase 0 targets discovered. 14/15 have arXiv IDs.**

| Title | Year | SS ID | arXiv ID | Citations | Key 1-line insight |
|-------|------|-------|----------|-----------|-------------------|
| Semantic Uncertainty (Kuhn et al.) | 2023 | 507465f8d46489a68a527cb5304d76bdb6c31ed9 | 2302.09664 | 845 | NLI-cluster entropy over N samples outperforms token entropy on TriviaQA — primary SE baseline |
| SelfCheckGPT (Manakul et al.) | 2023 | 7c1707db9aafd209aa93db3251e7ebd593d55876 | 2303.08896 | 1099 | Consistency-based hallucination detection; NLI variant NonFact AUC-PR 92.50 vs log-prob 83.21 |
| Self-Consistency CoT (Wang et al.) | 2022 | 5f19ae1135a9500940978104ec15a5b8751bc7d2 | 2203.11171 | 7324 | Foundational: N-sample consistency sampling improves reliability; establishes consistency=reliability |
| Can LLMs Express Uncertainty? (Xiong) | 2023 | 8f7297454d7f44365b9bcda5ebb9439a43daf5e6 | 2306.13063 | 1058 | Consistency = best black-box UQ method across multiple LLMs; benchmarks AUROC |
| LM-Polygraph (Fadeeva et al.) | 2023 | 444f3b7293b85b7d37600372941a289f9163abd1 | 2311.07383 | 155 | Battery of UE methods; pip install lm-polygraph; LLaMA-2+ChatGPT evaluation |
| Teaching Models Uncertainty in Words (Lin) | 2022 | 374dd173491a59a10bbb2b3519ebcfe3649f529d | 2205.14334 | 792 | Verbalized uncertainty baseline; calibrated without logit access |
| Internal State LLM Lying (Azaria) | 2023 | f406aceba4f29cc7cfbe7edb2f52f01374486589 | 2304.13734 | 736 | Hidden-state classifier 71-83% accuracy — requires white-box; reinforces black-box approach |
| Beyond SE: SNNE (Nguyen 2025) | 2025 | cdb0bd66b11b2d2a99a75a03ce354c4943f5d18c | 2506.00245 | 28 | Pairwise SE extension addresses longer-response SE limitations; Phi3+Llama3 |
| UQLM (Bouchard 2025, JMLR 2026) | 2025 | 3bdef0d6cf8af968037ffcc4fdc0c052d36ca254 | 2504.19254 | 21 | Ensemble Scorers combining Black-Box + White-Box — pip install uqlm |
| UQ Survey for Hallucination (Kang 2025) | 2025 | 76912e6ea42bdebb2795708dac381a9b268b391c | 2510.12040 | 11 | Comprehensive survey: epistemic/aleatoric distinction, systematic UQ categorization |
| CCUF (Zhou 2026) | 2026 | 18d84454713f9df277112c20c43663cad727e911 | null | 0 | Cross-model consistency on TriviaQA+TruthfulQA; +5.2% vs GPT-4 on TruthfulQA |
| Revisiting UQ Eval Length Bias (Santilli 2025, ACL) | 2025 | d8847ba42f3a8d5b1c4b706c23b24e1f8e95ee67 | 2504.13677 | 21 | CRITICAL: Length bias distorts AUROC rankings; OLS residualization required |
| Token-Level + NLI + SE Hybrid (Raghuvanshi 2025) | 2025 | 52632acc81f83025e21f00564917b9e481fcff2e | null | 0 | Closest existing work: token log-prob + NLI + SE → AUC 0.818 SQuAD2.0; no public code |
| UAF Ensemble (Dey 2025) | 2025 | 41e244e97ec4b630ff89bd192c22bb0e81153ab3 | 2503.05757 | 16 | Ensemble fusion UQ signals for hallucination mitigation +8% factual accuracy |
| Semantic Energy (Ma 2025) | 2025 | 20cfdfe156301f92bff5c66accf30e2dc638472d | 2508.14496 | 17 | Beyond SE: Boltzmann distribution over penultimate logits; addresses SE failure cases |

**Citation Network:** Wang 2022 → Kuhn 2023 → Manakul 2023 → [Research Question]
**Gap in network:** No paper combines SelfCheckGPT-style consistency WITH [min_logprob, full_sequence_variance] on TriviaQA/TruthfulQA — the proposed combination is novel.

---

## 5. Implementation Resources (via Exa)

| Resource | URL | Stars | Language | Key feature |
|----------|-----|-------|----------|-------------|
| potsawee/selfcheckgpt | https://github.com/potsawee/selfcheckgpt | 628 | Python | pip install selfcheckgpt; SelfCheckNLI (DeBERTa-MNLI), SelfCheckBERTScore |
| jlko/semantic_uncertainty | https://github.com/jlko/semantic_uncertainty | 421 | Python | Active SE implementation; deberta-v2-xlarge-mnli clustering |
| IINemo/lm-polygraph | https://github.com/IINemo/lm-polygraph | 480 | Python | pip install lm-polygraph; vLLM support; multi-method UQ benchmark |
| cvs-health/uqlm | https://github.com/cvs-health/uqlm | 1183 | Python | pip install uqlm; Black-Box + White-Box + Ensemble Scorers; JMLR 2026 |
| OATML/semantic-entropy-probes | https://github.com/OATML/semantic-entropy-probes | 58 | Python | Cheaper SE probes — reduced NLI compute |
| intuit/sac3 | https://github.com/intuit/sac3 | 39 | Python | SAC3 (EMNLP 2023): semantic-aware cross-check consistency |
| taubenfeld/CISC | https://github.com/taubenfeld/CISC | 3 | Python | ACL 2025: confidence-weighted consistency (log-prob + consistency) |
| youzhaozhao/SelfCheckGPT-Replication-Extension | https://github.com/youzhaozhao/SelfCheckGPT-Replication-Extension | - | Python | L2C: Random Forest fusion (NLI+Prompt), NonFact AUC-PR 0.9299 |
| sylinrl/TruthfulQA | https://github.com/sylinrl/TruthfulQA | 927 | Python | Official TruthfulQA evaluation; Jan 2025 MC update; Apache 2.0 |

**Code pattern (SelfCheckGPT-NLI):**
```python
from selfcheckgpt.modeling_selfcheck import SelfCheckNLI
selfcheck_nli = SelfCheckNLI(device=device)
sent_scores = selfcheck_nli.predict(sentences=sentences, sampled_passages=[s1,s2,s3])
# → Prob(contradiction) per sentence; DeBERTa-v3-large-MNLI backbone
```

---

## 6. Chain-of-Relations Analysis

**Research Evolution:**
Wang 2022 (self-consistency sampling) → Kuhn 2023 (NLI-cluster SE on TriviaQA) → Manakul 2023 (SelfCheckGPT hallucination detection) → Stage 4 (UQLM ensemble, CCUF cross-model) → [Research Question: consistency+log-prob ensemble AUROC ≥ 0.85]

**Cross-Reference Matrix (top rows):**

| Resource | Sub-questions | Implementation | Adaptability |
|----------|---------------|----------------|--------------|
| SelfCheckGPT | Q1, Q2, Q5 | potsawee/selfcheckgpt (pip) | High |
| Semantic Uncertainty | Q2, Q4 | jlko/semantic_uncertainty | High |
| UQLM | Q3 (ensemble) | cvs-health/uqlm (pip) | High |
| Raghuvanshi 2025 | Q3 (partial) | No public code | Medium |
| CCUF 2026 | Q5 | No public code | Low |
| h-e2/h-m1 baseline | Q3, Q1 | Internal project | Direct reuse |

---

## 7. Verification Summary

- Total sources: 34 | [VERIFIED]: 30 (88.2%) | [INFERRED]: 4 (Archon domain mismatch)
- Scholar: 15 papers + 7 citation network; 14/15 have arXiv IDs; 7/7 target papers found (100%)
- Exa: 9 GitHub repos + 3 tutorial/benchmark + 1 code context (all verified)
- Archon: 0 verified (KB domain mismatch — image generation content)
- Overall quality: 92/100 — SUFFICIENT FOR PHASE 2

---

## 8. Research Gaps

### User Input Recall

📌 **Research Question:** Do consistency signals (N=5–10 stochastic samples, ROUGE/BERTScore variance, NLI-cluster entropy, entailment contradiction) achieve AUROC ≥ 0.85 on TriviaQA dev + TruthfulQA, outperforming [min_logprob, full_sequence_variance] (AUROC ~0.82), using Llama-3.1-8B + Qwen-2.5-7B without fine-tuning or hidden-state extraction?

📌 **Detailed Questions (5):** Q1 metric ranking, Q2 SE vs lexical, Q3 ensemble ≥0.87, Q4 N-efficiency, Q5 cross-model delta <0.05.

📌 **Reference Papers:** Not provided.

### Identified Gaps

#### Gap 1: No Direct Benchmark of Consistency+Log-Prob Ensemble on TriviaQA/TruthfulQA with Open-Weight Models

**Relevance:** 🎯 PRIMARY | **Impact:** HIGH

**Connection:** ☑️ Blocks research question (combined AUROC unknown). ☑️ Addresses Q1 (metric ranking), Q3 (ensemble ≥0.87).

**Current State:** SelfCheckGPT tests consistency alone on WikiBio. Semantic entropy tests SE alone on TriviaQA. Log-prob baseline [min_logprob, full_sequence_variance] tested in h-e2/h-m1 (AUROC ~0.82) without consistency signals. Raghuvanshi 2025 combines on SQuAD2.0 only (AUC 0.818, no public code). UQLM has ensemble framework but no TriviaQA/TruthfulQA published results for Llama/Qwen.

**Missing Piece:** No published AUROC for combined [consistency signals + min_logprob + full_sequence_variance] ensemble on TriviaQA dev or TruthfulQA using Llama-3.1-8B or Qwen-2.5-7B.

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection" | 2023 | Manakul et al. | 7c1707db9aafd209aa93db3251e7ebd593d55876 | 2303.08896 | 1099 | Consistency alone on WikiBio — no log-prob combination, no TriviaQA |
| "Semantic Uncertainty" | 2023 | Kuhn, Gal, Farquhar | 507465f8d46489a68a527cb5304d76bdb6c31ed9 | 2302.09664 | 845 | SE alone on TriviaQA — no log-prob combination |
| "Integrating Token-Level Uncertainty, NLI, SE" | 2025 | Raghuvanshi et al. | 52632acc81f83025e21f00564917b9e481fcff2e | null | 0 | Closest existing work — SQuAD2.0 only, AUC 0.818, no public code |
| "UQ for LLMs: Ensemble Scorers" | 2025 | Bouchard, Chauhan | 3bdef0d6cf8af968037ffcc4fdc0c052d36ca254 | 2504.19254 | 21 | UQLM ensemble — no TriviaQA/TruthfulQA benchmark results for Llama/Qwen |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| [INFERRED] Multi-signal ensemble fusion | N/A (domain mismatch) | "combining log-probability ensemble consistency signals" | No Archon KB entries — image domain only |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| cvs-health/uqlm | https://github.com/cvs-health/uqlm | 1183 | Python | Ensemble Scorers (Black-Box + White-Box) — needs TriviaQA/TruthfulQA evaluation |
| potsawee/selfcheckgpt | https://github.com/potsawee/selfcheckgpt | 628 | Python | SelfCheckNLI + BERTScore — missing log-prob integration module |
| IINemo/lm-polygraph | https://github.com/IINemo/lm-polygraph | 480 | Python | Multi-method UQ with AUROC eval — potential integration point |

---

#### Gap 2: N-Sample Efficiency Frontier for Consistency UQ Not Established on Short-Answer QA Benchmarks

**Relevance:** 🎯 PRIMARY | **Impact:** HIGH

**Connection:** ☑️ Blocks Q4 (N=10 vs N=3 degradation, cost-efficiency frontier). ☑️ Affects Q1 (most efficient metric at given N).

**Current State:** Kuhn 2023 uses N=10 but does not ablate N=1–10. SelfCheckGPT uses N=3–5 but does not report AUROC-vs-N on TriviaQA. Wang 2022 shows accuracy-vs-N for CoT (not hallucination AUROC on TriviaQA). OATML/SE-probes provides cheaper SE approximation but no N-efficiency analysis.

**Missing Piece:** No published AUROC-vs-N curve for consistency-based UQ signals on TriviaQA dev or TruthfulQA with open-weight models. N=3 cost-efficiency breakeven for short-answer QA undefined.

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Self-Consistency Improves Chain of Thought Reasoning" | 2022 | Wang et al. | 5f19ae1135a9500940978104ec15a5b8751bc7d2 | 2203.11171 | 7324 | N-accuracy curves for CoT (N=1–40) — not UQ/AUROC on TriviaQA/TruthfulQA |
| "Beyond SE: Pairwise Semantic Similarity (SNNE)" | 2025 | Nguyen et al. | cdb0bd66b11b2d2a99a75a03ce354c4943f5d18c | 2506.00245 | 28 | SE limitations for longer responses; N efficiency not analyzed for short QA |
| "Semantic Uncertainty" | 2023 | Kuhn, Gal, Farquhar | 507465f8d46489a68a527cb5304d76bdb6c31ed9 | 2302.09664 | 845 | Uses N=10 but no AUROC ablation over N |
| "Can LLMs Express Their Uncertainty?" | 2023 | Xiong et al. | 8f7297454d7f44365b9bcda5ebb9439a43daf5e6 | 2306.13063 | 1058 | Multiple sampling tested — no AUROC-vs-N efficiency curves |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| [INFERRED] N-sample efficiency tradeoff | N/A (domain mismatch) | "N-sample efficiency consistency uncertainty" | No relevant Archon KB content |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| OATML/semantic-entropy-probes | https://github.com/OATML/semantic-entropy-probes | 58 | Python | Cheaper SE approximation — potential N-efficiency solution, no TriviaQA results |
| jlko/semantic_uncertainty | https://github.com/jlko/semantic_uncertainty | 421 | Python | Primary SE implementation — can run N ablation, no published N-efficiency analysis |

---

#### Gap 3: Cross-Model Consistency Signal Transfer (Llama-3.1-8B vs Qwen-2.5-7B) Not Evaluated Without Recalibration

**Relevance:** 🎯 PRIMARY | **Impact:** MEDIUM-HIGH

**Connection:** ☑️ Blocks Q5 (AUROC delta < 0.05 Llama vs Qwen without recalibration). ☑️ Addresses generalizability of consistency signals.

**Current State:** SelfCheckGPT tests GPT-3 only. Semantic entropy tests LLaMA-2 only. CCUF (Zhou 2026) uses cross-model checking (different models checking each other) — not same-architecture cross-generation. LM-Polygraph evaluates LLaMA-2 + ChatGPT separately without pairwise AUROC delta on TriviaQA/TruthfulQA.

**Missing Piece:** No published AUROC comparison of consistency signals on Llama-3.1-8B vs Qwen-2.5-7B on TriviaQA dev / TruthfulQA without model-specific recalibration. The AUROC delta threshold (≥ or < 0.05) is undefined for this specific pair.

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Calibrating Uncertainty with Cross-Model Consistency (CCUF)" | 2026 | Zhou et al. | 18d84454713f9df277112c20c43663cad727e911 | null | 0 | Different models cross-checking each other — different setting; TriviaQA+TruthfulQA |
| "LM-Polygraph: Uncertainty Estimation" | 2023 | Fadeeva et al. | 444f3b7293b85b7d37600372941a289f9163abd1 | 2311.07383 | 155 | Tests LLaMA-2+ChatGPT — no Llama-3.1-8B vs Qwen-2.5-7B pairwise delta |
| "Can LLMs Express Their Uncertainty?" | 2023 | Xiong et al. | 8f7297454d7f44365b9bcda5ebb9439a43daf5e6 | 2306.13063 | 1058 | Multi-model evaluation — no Llama-3.1-8B vs Qwen-2.5-7B AUROC delta |
| "Revisiting UQ Evaluation: Length Bias (Santilli 2025)" | 2025 | Santilli et al. | d8847ba42f3a8d5b1c4b706c23b24e1f8e95ee67 | 2504.13677 | 21 | Length bias confounds cross-model transfer analysis; OLS residualization required |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| [INFERRED] Cross-architecture consistency | N/A (domain mismatch) | "consistency UQ transfer across model families" | No relevant Archon KB content |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| IINemo/lm-polygraph | https://github.com/IINemo/lm-polygraph | 480 | Python | vLLM support for Llama + Qwen; multi-model UQ evaluation |
| cvs-health/uqlm | https://github.com/cvs-health/uqlm | 1183 | Python | Universal black-box scorers; enables cross-model AUROC comparison |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to Research Question | Detailed Questions | Impact | Evidence | Priority |
|--------|-----------|--------------------------------|-------------------|--------|----------|----------|
| Gap 1 | 🎯 PRIMARY | ☑️ Blocks: combined AUROC ≥ 0.85/0.87 unknown on TriviaQA/TruthfulQA | Q1, Q3 | HIGH | 4 Scholar + 3 Exa | **Critical** |
| Gap 2 | 🎯 PRIMARY | ☑️ Blocks: N-sample efficiency frontier for feasibility | Q4 | HIGH | 4 Scholar + 2 Exa | **Critical** |
| Gap 3 | 🎯 PRIMARY | ☑️ Blocks: cross-model generalizability (delta < 0.05) | Q5 | MEDIUM-HIGH | 4 Scholar + 2 Exa | **High** |

### User Input to Gap Traceability

**Research Question** → Gap 1 (combined ensemble AUROC ≥ 0.85 — novel, untested combination)
**Q1** → Gap 1 (metric ranking on TriviaQA N=5 not published for these models)
**Q2** → Gap 1 (SE vs lexical on TriviaQA for Llama-3.1-8B not published)
**Q3** → Gap 1 (combined ensemble ≥ 0.87 — primary novel contribution)
**Q4** → Gap 2 (AUROC-vs-N curve for TriviaQA/TruthfulQA short-answer QA missing)
**Q5** → Gap 3 (Llama-3.1-8B vs Qwen-2.5-7B AUROC delta undefined)

**Failure modes avoided:** Gap 1 explicitly uses stochastic multi-sample generation (avoids h-e2 greedy-only collinearity). No hidden-state extraction (avoids h-e1). No POS filtering (avoids h-m1).

---

## 9. Conclusion

### Key Findings

1. SelfCheckGPT-NLI: NonFact AUC-PR 92.50 vs log-prob 83.21 on WikiBio — consistency outperforms log-prob on related benchmark.
2. All 7 Phase 0 target papers found; 14/15 have arXiv IDs for Phase 2A download.
3. Three pip-installable repos ready: selfcheckgpt, lm-polygraph, uqlm.
4. Closest combination work (Raghuvanshi 2025) on SQuAD2.0 only — TriviaQA/TruthfulQA gap confirmed.
5. CCUF 2026: cross-model consistency +5.2% vs GPT-4 on TruthfulQA.
6. Santilli 2025: length bias distorts AUROC — OLS residualization required (consistent with h-e1 lesson).
7. NLI backbone consensus: DeBERTa-NLI consistent across all implementations.

### Answer to Detailed Questions (Preliminary — data observation, no hypotheses)

- Q1/Q2: NLI-based consistency > lexical on related benchmarks; TriviaQA N=5 specific comparison missing (Gap 1).
- Q3: Ensemble fusion shows incremental gains (L2C +0.53%, UQLM framework); specific combination on TriviaQA/TruthfulQA with [min_logprob, variance] untested (Gap 1).
- Q4: N-accuracy curves exist for CoT (Wang 2022) but not AUROC-vs-N for TriviaQA hallucination (Gap 2).
- Q5: Cross-model evaluation exists but not Llama-3.1-8B vs Qwen-2.5-7B specifically (Gap 3).

### Phase 2 Readiness

✅ READY FOR PHASE 2A:
- 3 PRIMARY gaps identified with table-format evidence (19 sources)
- All target papers found with arXiv IDs
- Implementation repos pip-installable
- Validated baseline AUROC ~0.82 provides comparison point
- Citation chain: Wang 2022 → Kuhn 2023 → Manakul 2023 → [research question]

**arXiv IDs for Phase 2A download:** 2303.08896, 2302.09664, 2203.11171, 2306.13063, 2311.07383, 2504.13677, 2205.14334, 2304.13734

### Next Steps

1. Phase 2A: Synthesize 3 gaps into testable hypotheses. Focus: Gap 1 (combined ensemble) and Gap 2 (N-efficiency).
2. Download primary papers: arXiv 2303.08896 (SelfCheckGPT) and 2302.09664 (SE).
3. Benchmark infrastructure: reuse h-e1 TriviaQA pipeline; add TruthfulQA (sylinrl/TruthfulQA).
4. Methodological safeguard: OLS residualization for response length (Santilli 2025).

---

*Phase: 1 - Targeted Research Gathering*
*Full report: docs/youra_research/01_targeted_research_full.md*
*Total processing time: ~2 sessions (context compaction between Steps 4-5)*
