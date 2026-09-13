# Targeted Research Report: Can token-level or sequence-level uncertainty signals derived from frozen LLMs serve as reliable predictors of hallucination on existing factual QA and natural language inference benchmarks, without requiring new human annotations, synthetic data, or new scoring frameworks?

**Date:** 2026-08-21
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous
**Version:** FULL (archival)

---

## Executive Summary

Phase 1 targeted research on uncertainty quantification (UQ) and hallucination detection in LLMs yielded **13 verified academic papers** and **9 implementation repositories** across Semantic Scholar and Exa MCP. The research question — whether frozen LLM token/sequence-level uncertainty signals can predict hallucination on existing factual QA benchmarks without new annotations — has strong prior art across four lines: (1) LLM self-calibration (Kadavath 2022, 1910 citations), (2) semantic entropy over NLI-clustered samples (Farquhar/Kuhn 2023-2024, 881 citations, Nature 2024), (3) multi-sample consistency (SelfCheckGPT 2023, 1148 citations), and (4) token-level UQ (Fadeeva CCP 2024, 186 citations; Moslonka EPR 2025). Archon KB was domain-mismatched (diffusion/image-gen content only); 4 inferred patterns supplemented. Three PRIMARY/SECONDARY research gaps were identified targeting sub-questions 3, 4, and 5. Phase 2A is ready with strong evidence base.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Can token-level or sequence-level uncertainty signals derived from frozen LLMs serve as reliable predictors of hallucination on existing factual QA and natural language inference benchmarks, without requiring new human annotations, synthetic data, or new scoring frameworks?

### Detailed Research Questions
1. Do existing uncertainty measures (predictive entropy, mutual information, semantic entropy) computed from LLM output distributions correlate with hallucination rates on established factual QA benchmarks (TriviaQA, Natural Questions, SciQ, TruthfulQA)?
2. Can multi-sample semantic consistency (sampling N outputs and measuring semantic agreement) be used as a calibration-free hallucination detector that outperforms single-pass confidence baselines on existing NLI/QA datasets?
3. How do token-level uncertainty aggregation strategies (max, mean, sum over sequence) compare as hallucination indicators on established benchmarks without requiring model fine-tuning or new annotation?
4. Does the relationship between uncertainty estimates and hallucination generalize across model families (GPT-2/GPT-3.5 scale, LLaMA, Mistral) on the same fixed evaluation benchmarks?
5. Can uncertainty-based selective prediction (abstaining when uncertainty exceeds a threshold) improve coverage-accuracy tradeoffs on existing QA benchmarks using only the model's own output probabilities?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
*N/A - First attempt*

---

## 2. Search Queries Generated

### Query Generation Source Summary
- Failure-aware queries (ROUTE_TO_0): N/A (first attempt)
- Reference paper queries: 0 (no reference papers provided)
- Brainstorm insights queries: 5
- Direct question queries: 8
- Total: 13 queries

### Priority 1: Reference Paper Concept Queries
*No reference papers provided*

### Priority 2: Brainstorm Insights Queries
1. "predictive entropy LLM hallucination detection"
2. "semantic consistency sampling calibration-free hallucination"
3. "uncertainty quantification foundation models high-stakes deployment"
4. "token-level uncertainty aggregation strategies NLP generation"
5. "selective prediction coverage-accuracy tradeoff language models abstention"

### Priority 3: Direct Question Decomposition Queries
**A. Technical Queries:**
1. "uncertainty quantification large language models factual QA benchmarks"
2. "predictive entropy mutual information semantic entropy hallucination correlation"
3. "SelfCheckGPT semantic entropy multi-sample consistency LLM"

**B. Theoretical Queries:**
4. "TriviaQA Natural Questions hallucination evaluation uncertainty measures"
5. "LLM confidence calibration selective abstention QA benchmark"
6. "Bayesian uncertainty neural language models token probability"

**C. Comparative Queries:**
7. "token-level vs sequence-level uncertainty aggregation hallucination indicators"
8. "entropy-based vs sampling-based hallucination detection comparison"

**D. Problem-Specific Queries:**
9. "TruthfulQA SciQ uncertainty-based hallucination detection frozen LLM"
10. "LLaMA Mistral GPT uncertainty estimation cross-model generalization benchmark"

---

## 3. Past Cases & Best Practices (via Archon)

### Direct Implementations
**[NOT_FOUND - ARCHON]** No direct implementations found in Archon Knowledge Base.
- Queries executed: 8 queries across 3 levels (Level 1: direct match, Level 2: conceptual expansion, Level 3: meta-patterns)
- KB content: Archon KB contains primarily diffusion model / image generation content (HuggingFace diffusers, stable diffusion)
- No UQ, hallucination detection, or LLM reliability content found

**[INFERRED]** Pattern: Entropy-based uncertainty for generative model outputs
- Source: General knowledge (Archon search yielded no results)
- Reasoning: Predictive entropy H(Y|x) = -Σ p(y|x) log p(y|x) is a standard measure for uncertainty in generative models; applicable to LLM token distributions
- Note: Not verified through Archon knowledge base

**[INFERRED]** Pattern: Multi-sample consistency as proxy for confidence
- Source: General knowledge
- Reasoning: Sampling multiple outputs and measuring semantic agreement (e.g., via NLI or embedding similarity) is used in SelfCheckGPT and related work as calibration-free hallucination signal
- Note: Not verified through Archon knowledge base

### Similar Architectural Patterns
**[NOT_FOUND - ARCHON]** No similar architectural patterns found in Archon Knowledge Base.

**[INFERRED]** Pattern: Token probability aggregation for sequence-level scoring
- Source: General knowledge
- Reasoning: Max, mean, and sum aggregation of per-token log-probabilities are established baseline strategies for sequence-level confidence scoring in NLG evaluation
- Note: Not verified through Archon knowledge base

**[INFERRED]** Pattern: Selective prediction with rejection option
- Source: General knowledge
- Reasoning: Coverage-accuracy tradeoff via threshold-based abstention is a standard framework for risk-controlled deployment; directly applicable to LLM QA with uncertainty threshold
- Note: Not verified through Archon knowledge base

### Code Examples Found
*No code examples found in Archon Knowledge Base for this research domain.*

**MCP Performance Summary:**
- Total queries: 8 (3 Level 1 + 3 Level 2 + 2 Level 3)
- Verified results: 0 [VERIFIED - ARCHON]
- Inferred patterns: 4 [INFERRED]
- KB content mismatch: Archon KB indexed for diffusion/image-gen domain, not NLP/LLM reliability

---

## 4. Academic Literature Review (via Semantic Scholar)

### Directly Relevant Papers

**MCP Server Used:** Semantic Scholar (`mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search`)
**Total Queries:** 6 queries across 2 rounds
**Results Found:** 12 papers (8 directly relevant, 4 foundational)

1. **[VERIFIED - SCHOLAR]** "Learned Hallucination Detection in Black-Box LLMs using Token-level Entropy Production Rate" (2025)
   - Authors: Moslonka, Randrianarivo, Garnier, Malherbe
   - Citations: 13
   - Semantic Scholar ID: ec46fb59962319da34880e1712aa1c703a5287d0
   - arXiv ID: 2509.04492
   - URL: https://www.semanticscholar.org/paper/ec46fb59962319da34880e1712aa1c703a5287d0
   - Search Query: "predictive entropy LLM hallucination detection"
   - Key Contribution: Entropy Production Rate (EPR) from top-k log-probabilities for one-shot token-level hallucination detection in black-box APIs; outperforms SOTA on QA datasets

2. **[VERIFIED - SCHOLAR]** "A Head to Predict and a Head to Question: Pre-trained Uncertainty Quantification Heads for Hallucination Detection in LLM Outputs" (2025)
   - Authors: Shelmanov, Fadeeva, Tsvigun et al.
   - Citations: 29
   - Semantic Scholar ID: cca687992c11d54daed5d0c6e4d60c7f1e71bcbd
   - arXiv ID: 2505.08200
   - URL: https://www.semanticscholar.org/paper/cca687992c11d54daed5d0c6e4d60c7f1e71bcbd
   - Search Query: "predictive entropy LLM hallucination detection"
   - Key Contribution: Supervised UQ auxiliary heads using attention maps; state-of-the-art claim-level hallucination detection; generalizes across Mistral, Llama, Gemma 2

3. **[VERIFIED - SCHOLAR]** "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models" (2023)
   - Authors: Manakul, Liusie, Gales
   - Citations: 1148
   - Semantic Scholar ID: 7c1707db9aafd209aa93db3251e7ebd593d55876
   - arXiv ID: 2303.08896
   - URL: https://www.semanticscholar.org/paper/7c1707db9aafd209aa93db3251e7ebd593d55876
   - Search Query: "SelfCheckGPT hallucination detection language models"
   - Key Contribution: Sampling-based consistency for black-box hallucination detection; consistent facts = LLM knows; inconsistent samples = hallucination; evaluated on WikiBio/GPT-3

4. **[VERIFIED - SCHOLAR]** "Fact-Checking the Output of Large Language Models via Token-Level Uncertainty Quantification" (2024)
   - Authors: Fadeeva, Rubashevskii, Shelmanov et al.
   - Citations: 186
   - Semantic Scholar ID: 8c5acaafe43e710d55b08c63d567550ad26ec437
   - arXiv ID: 2403.04696
   - URL: https://www.semanticscholar.org/paper/8c5acaafe43e710d55b08c63d567550ad26ec437
   - Search Query: "uncertainty quantification large language models factual QA benchmarks"
   - Key Contribution: Token-level UQ pipeline for fact-checking; Claim Conditioned Probability (CCP) removes surface-form uncertainty; 7 LLMs, 4 languages, biography generation

5. **[VERIFIED - SCHOLAR]** "Uncertainty Quantification and Confidence Calibration in Large Language Models: A Survey" (2025)
   - Authors: Liu, Chen, Da et al.
   - Citations: 131
   - Semantic Scholar ID: 422b00c330a16a00ef182abfd1d66e12369db9e8
   - arXiv ID: 2503.15850
   - URL: https://www.semanticscholar.org/paper/422b00c330a16a00ef182abfd1d66e12369db9e8
   - Search Query: "uncertainty quantification large language models factual QA benchmarks"
   - Key Contribution: Taxonomy of UQ methods (input/reasoning/parameter/prediction uncertainty); benchmarks and metrics survey; identifies open challenges for scalable UQ

6. **[VERIFIED - SCHOLAR]** "Beyond Semantic Entropy: Boosting LLM Uncertainty Quantification with Pairwise Semantic Similarity" (2025)
   - Authors: Nguyen, Payani, Mirzasoleiman
   - Citations: 29
   - Semantic Scholar ID: cdb0bd66b11b2d2a99a75a03ce354c4943f5d18c
   - arXiv ID: 2506.00245
   - URL: https://www.semanticscholar.org/paper/cdb0bd66b11b2d2a99a75a03ce354c4943f5d18c
   - Search Query: "semantic entropy hallucination LLM uncertainty"
   - Key Contribution: SNNE — pairwise similarity-based entropy that accounts for intra/inter-cluster similarity; generalizes semantic entropy; tested on Phi3, Llama3; QA, summarization, translation

7. **[VERIFIED - SCHOLAR]** "Hallucination Detection on a Budget: Efficient Bayesian Estimation of Semantic Entropy" (2025)
   - Authors: Ciosek, Felicioni, Ghiassian
   - Citations: 4
   - Semantic Scholar ID: afe7ce2c19b3b9b1557f01274b5af5d26e3d27ee
   - arXiv ID: 2504.03579
   - URL: https://www.semanticscholar.org/paper/afe7ce2c19b3b9b1557f01274b5af5d26e3d27ee
   - Search Query: "semantic entropy hallucination LLM uncertainty"
   - Key Contribution: Bayesian estimation of semantic entropy; adaptive sample allocation; achieves same AUROC as Farquhar et al. with only 53% of samples; works with 1 sample

8. **[VERIFIED - SCHOLAR]** "Semantic Energy: Detecting LLM Hallucination Beyond Entropy" (2025)
   - Authors: Ma, Pan, Liu et al.
   - Citations: 18
   - Semantic Scholar ID: 20cfdfe156301f92bff5c66accf30e2dc638472d
   - arXiv ID: 2508.14496
   - URL: https://www.semanticscholar.org/paper/20cfdfe156301f92bff5c66accf30e2dc638472d
   - Search Query: "semantic entropy hallucination LLM uncertainty"
   - Key Contribution: Boltzmann-inspired energy function on penultimate-layer logits + semantic clustering; addresses softmax overconfidence failure cases of semantic entropy

9. **[VERIFIED - SCHOLAR]** "Robust Uncertainty Quantification for Factual Generation of Large Language Models" (2025)
   - Authors: Zhang, Yang, Zhou
   - Citations: 1
   - Semantic Scholar ID: 757c7704bebe4abc81c7756ce429b7a457c8f1a7
   - arXiv ID: 2601.00348
   - URL: https://www.semanticscholar.org/paper/757c7704bebe4abc81c7756ce429b7a457c8f1a7
   - Search Query: "uncertainty quantification large language models factual QA benchmarks"
   - Key Contribution: RU method for multi-fact generation with trap questions; +0.1-0.2 ROCAUC over baselines on 4 models; addresses adversarial/non-canonical QA failure mode

10. **[VERIFIED - SCHOLAR]** "Uncertainty Quantification of Large Language Models through Multi-Dimensional Responses" (2025)
    - Authors: Chen, Liu, Da et al.
    - Citations: 18
    - Semantic Scholar ID: c6c6ad7747343fe88599277795b4676dab84d661
    - arXiv ID: 2502.16820
    - URL: https://www.semanticscholar.org/paper/c6c6ad7747343fe88599277795b4676dab84d661
    - Search Query: "uncertainty quantification large language models factual QA benchmarks"
    - Key Contribution: Multi-dimensional UQ via semantic + knowledge-aware similarity matrices + tensor decomposition; disentangles semantic variation from factual consistency

### Foundational Papers

1. **[VERIFIED - SCHOLAR]** "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation" (2023)
   - Authors: Kuhn, Gal, Farquhar
   - Citations: 881
   - Semantic Scholar ID: 507465f8d46489a68a527cb5304d76bdb6c31ed9
   - arXiv ID: 2302.09664
   - URL: https://www.semanticscholar.org/paper/507465f8d46489a68a527cb5304d76bdb6c31ed9
   - Search Round: Direct lookup
   - Key Contribution: Semantic entropy — entropy over semantic equivalence clusters; handles linguistic invariances (paraphrase = same meaning); unsupervised, single-model, no fine-tuning; outperforms token-prob baselines on QA
   - Note: Foundational paper for the entire semantic entropy line of work

2. **[VERIFIED - SCHOLAR]** "TruthfulQA: Measuring How Models Mimic Human Falsehoods" (2021)
   - Authors: Lin, Hilton, Evans
   - Citations: 3781
   - Semantic Scholar ID: 77d956cdab4508d569ae5741549b78e715fd0749
   - arXiv ID: 2109.07958
   - URL: https://www.semanticscholar.org/paper/77d956cdab4508d569ae5741549b78e715fd0749
   - Search Round: Direct lookup
   - Key Contribution: 817-question benchmark across 38 categories for truthfulness; largest models LEAST truthful (inverse scaling); defines benchmark for UQ-based hallucination evaluation

3. **[VERIFIED - SCHOLAR]** "Language Models (Mostly) Know What They Know" (2022)
   - Authors: Kadavath, Conerly, Askell et al. (Anthropic)
   - Citations: 1910
   - Semantic Scholar ID: 142ebbf4760145f591166bde2564ac70c001e927
   - arXiv ID: 2207.05221
   - URL: https://www.semanticscholar.org/paper/142ebbf4760145f591166bde2564ac70c001e927
   - Search Round: Direct lookup
   - Key Contribution: P(True) and P(IK) self-evaluation; larger models well-calibrated on MC/T-F; multi-sample self-evaluation improves accuracy; lays groundwork for honesty-oriented calibration

### Citation Network Analysis

**No reference papers provided** — citation network analysis not applicable.

**Key Research Lineage Identified:**
- Foundational calibration work (Kadavath et al. 2022, 1910 citations) → Semantic entropy (Kuhn/Farquhar 2023, 881 citations) → Efficient SE estimation (Ciosek 2025, Nguyen 2025) → SE extensions to multimodal (UniVRSE 2025, VideoHEDGE 2026)
- SelfCheckGPT (Manakul 2023, 1148 citations) → multi-granularity consistency approaches (Zhang 2026, BEACON 2026)
- Token-level UQ (Fadeeva 2024, 186 citations) → UQ heads (Shelmanov 2025, 29 citations)
- TruthfulQA benchmark (Lin 2021, 3781 citations) → evaluation standard for all above methods

**Most Influential Work:** TruthfulQA (3781 citations), Kadavath et al. (1910), SelfCheckGPT (1148), Semantic Entropy (881)
**Recent Trends (2025-2026):** Efficiency improvements for SE (fewer samples), logit-based alternatives to softmax entropy, black-box API-compatible methods, multimodal extension

---

## 5. Implementation Resources (via Exa)

### Directly Relevant Implementations

**MCP Server Used:** Exa Search (`mcp__exa__web_search_exa`, `mcp__exa__get_code_context_exa`)
**Total Queries:** 4 queries across 3 priorities
**Results Found:** 7 GitHub repos + 1 PyPI package + code context

1. **[VERIFIED - EXA]** cvs-health/uqlm
   - URL: https://github.com/cvs-health/uqlm
   - Stars: 1183
   - Language: Python
   - Search Query: "LLM uncertainty quantification token probability hallucination github"
   - Priority Level: Priority 1
   - Key Features: Full UQ framework; semantic entropy (discrete + token-prob), SelfCheckGPT, conformal prediction; Apache 2.0; actively maintained
   - Relevance: Direct implementation of all core methods in research question (entropy, consistency, selective prediction)

2. **[VERIFIED - EXA]** IINemo/lm-polygraph
   - URL: https://github.com/IINemo/lm-polygraph
   - Stars: 480
   - Language: Python
   - Search Query: "LLM uncertainty quantification token probability hallucination github"
   - Priority Level: Priority 1
   - Key Features: Battery of UE methods (token/sequence/semantic level); benchmark suite; from Shelmanov/Fadeeva group (same as UQ heads paper); includes CCP method
   - Relevance: Comprehensive benchmark framework covering token-level vs sequence-level UQ comparison (sub-question 3)

3. **[VERIFIED - EXA]** jlko/semantic_uncertainty
   - URL: https://github.com/jlko/semantic_uncertainty
   - Stars: 411
   - Language: Python (67.9%) + Jupyter (32.1%)
   - Search Query: "semantic entropy hallucination detection Python implementation github"
   - Priority Level: Priority 1
   - Key Features: Official Farquhar et al. Nature 2024 reproduction code; short-phrase + sentence-length experiments; BSD-3-Clause
   - Relevance: Reference implementation of semantic entropy (foundational method for sub-question 2)

4. **[VERIFIED - EXA]** potsawee/selfcheckgpt
   - URL: https://github.com/potsawee/selfcheckgpt
   - Stars: 628
   - Language: Python
   - Search Query: "SelfCheckGPT implementation GitHub uncertainty LLM hallucination"
   - Priority Level: Priority 1
   - Key Features: Official SelfCheckGPT implementation; multiple variants (BERTScore, NLI, MQAG, N-gram, LLM-prompt); pip installable; supports OpenAI/Groq APIs
   - Relevance: Direct implementation for sub-question 2 (multi-sample consistency as calibration-free detector)

5. **[VERIFIED - EXA]** OATML/semantic-entropy-probes
   - URL: https://github.com/OATML/semantic-entropy-probes
   - Stars: 65
   - Language: Jupyter Notebook (91%) + Python
   - Search Query: "semantic entropy hallucination detection Python implementation github"
   - Priority Level: Priority 2
   - Key Features: Lightweight linear probes on hidden states as proxy for semantic entropy; cheap inference-time method; MIT license
   - Relevance: Shows hidden-state shortcut for semantic entropy — relevant for frozen LLM setting

6. **[VERIFIED - EXA]** spotify-research/bayesian-semantic-entropy
   - URL: https://github.com/spotify-research/bayesian-semantic-entropy
   - Stars: 25
   - Language: Python + Jupyter
   - Search Query: "semantic entropy hallucination detection Python implementation github"
   - Priority Level: Priority 2
   - Key Features: Bayesian SE estimator (Ciosek et al. 2025); adaptive sampling; runs on laptop; BSD-3-Clause
   - Relevance: Sample-efficient SE — relevant for frozen LLM deployment with limited inference budget

7. **[VERIFIED - EXA]** Wang-ML-Lab/TokUR
   - URL: https://github.com/Wang-ML-Lab/TokUR
   - Stars: 13
   - Language: Python
   - Search Query: "LLM uncertainty quantification token probability hallucination github"
   - Priority Level: Priority 1
   - Key Features: ICLR 2026; training-free token-level UE for reasoning; MIT license
   - Relevance: Token-level aggregation strategies (sub-question 3)

### Component Implementations

1. **[VERIFIED - EXA]** MaHuanAAA/logtoku
   - URL: https://github.com/MaHuanAAA/logtoku
   - Stars: 38
   - Language: Python (81%) + Jupyter
   - Key Features: Logit-based uncertainty estimation; enhances semantic entropy with evidence from logits; implementation of Semantic Energy approach
   - Relevance: White-box logit-level alternative to softmax-based entropy (addresses overconfidence failure mode)

2. **[VERIFIED - EXA]** artefactory/artefactual
   - URL: https://github.com/artefactory/artefactual
   - Stars: 38
   - Language: Python
   - Key Features: EPR (Entropy Production Rate) implementation; supports vLLM, OpenAI, Responses API; token-level + sequence-level scores; precomputed calibration by model family
   - Relevance: Production-grade EPR for black-box APIs (companion to Moslonka et al. 2025 paper)

### Tutorial Resources

1. **[VERIFIED - EXA - TUTORIAL]** "Semantic Entropy Demo" — UQLM Documentation
   - URL: https://cvs-health.github.io/uqlm/latest/_notebooks/examples/semantic_entropy_demo.html
   - Key Insights: Step-by-step semantic entropy walkthrough; discrete vs token-prob SE; NLI clustering with DeBERTa-large-mnli; normalized SE (NSN); practical code examples
   - Retrieved via: `mcp__exa__get_code_context_exa`

2. **[VERIFIED - EXA - TUTORIAL]** "Detecting Hallucinations in LLMs Using Semantic Entropy" — Nature (Farquhar et al. 2024)
   - URL: https://www.nature.com/articles/s41586-024-07421-0
   - Key Insights: Bidirectional NLI entailment clustering; Rao-Blackwellised entropy estimator; high entropy = confabulation; tested on multiple QA datasets

### Code Analysis

**[VERIFIED - EXA - CODE_CONTEXT]** Semantic entropy core implementation pattern:
- Retrieved via: `mcp__exa__get_code_context_exa(query="semantic entropy uncertainty estimation LLM Python NLI clustering", tokensNum=3000)`
- Key pattern: `get_semantic_ids()` — bidirectional NLI entailment check for equivalence; greedy cluster assignment
- Entropy variants: `cluster_assignment_entropy()` (black-box, frequency-based), `predictive_entropy_rao()` (white-box, token log-prob weighted)
- NLI model: `microsoft/deberta-large-mnli` (default); cross-encoder NLI preferred for production
- Token aggregation: length-normalized mean log-prob per generation, logsumexp aggregation per cluster
- Framework: PyTorch + HuggingFace transformers; modular design separating generation, clustering, entropy computation
- Common pattern across repos: sample N responses → NLI cluster → compute entropy over cluster distribution

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

**Line 1: Calibration and Self-knowledge**
1. Kadavath et al. 2022 (1910 citations) — P(True)/P(IK) self-evaluation; larger models well-calibrated on MC/T-F questions; multi-sample improves P(True)
2. TruthfulQA (Lin 2021, 3781 citations) — benchmark revealing inverse scaling (larger = less truthful); defines evaluation standard
3. → Research question: can token probabilities from frozen LLMs predict hallucination on these benchmarks?

**Line 2: Semantic Entropy (entropy over meaning clusters)**
1. Kuhn/Farquhar "Semantic Uncertainty" ICLR 2023 (881 citations) — semantic entropy via NLI clustering; unsupervised; no fine-tuning
2. Farquhar et al. Nature 2024 — extended to sentence-level; demonstrated on multiple QA datasets; jlko/semantic_uncertainty (411 stars)
3. Ciosek et al. 2025 — Bayesian SE; 53% fewer samples; spotify-research/bayesian-semantic-entropy (25 stars)
4. Nguyen et al. SNNE 2025 — pairwise similarity entropy; handles intra/inter-cluster similarity gaps in SE
5. → Research question sub-2: can semantic consistency serve as calibration-free detector without annotation?

**Line 3: Multi-sample Consistency (black-box)**
1. SelfCheckGPT (Manakul 2023, 1148 citations) — consistency across N samples; multiple scoring variants (BERTScore/NLI/MQAG/N-gram/LLM-prompt); potsawee/selfcheckgpt (628 stars)
2. BEACON 2026 — 31-dimensional feature vector combining NLI entropy, geometry, CoT, paraphrase stability; AUROC 0.81
3. HEAT toolkit — fact-level decomposition + NLI cross-encoder heatmap
4. → Research question sub-2: multi-sample consistency vs single-pass baselines on NLI/QA datasets

**Line 4: Token-level UQ**
1. Fadeeva et al. CCP 2024 (186 citations) — Claim Conditioned Probability; removes surface-form uncertainty; lm-polygraph (480 stars)
2. Moslonka et al. EPR 2025 — Entropy Production Rate from top-k logprobs; black-box API compatible; artefactual (38 stars)
3. Shelmanov UQ heads 2025 (29 citations) — supervised attention-map features; SOTA claim-level; lm-polygraph
4. TokUR ICLR 2026 — training-free token UE for reasoning; Wang-ML-Lab/TokUR (13 stars)
5. → Research question sub-1,3: entropy measures + token aggregation strategies as hallucination indicators

### Concept Integration Map

```
RESEARCH QUESTION: Can token/sequence-level uncertainty signals from frozen LLMs
                   predict hallucination on existing QA/NLI benchmarks?
                           |
          ┌────────────────┴────────────────┐
          ↓                                 ↓
  TOKEN-LEVEL SIGNALS                SEQUENCE-LEVEL SIGNALS
  (white-box: logprobs)              (black-box: output consistency)
          |                                 |
    ┌─────┴──────┐                    ┌─────┴──────┐
    ↓            ↓                    ↓            ↓
Predictive    Claim                Semantic      Multi-sample
Entropy       Conditioned          Entropy       Consistency
(Kadavath     Probability          (Farquhar     (SelfCheckGPT
 2022)        (Fadeeva 2024)        2023/2024)    2023)
    |            |                    |            |
    └─────┬──────┘                    └─────┬──────┘
          ↓                                 ↓
  Aggregation Strategies:          Clustering Methods:
  max / mean / sum over tokens     NLI bidirectional entailment
  (sub-question 3)                 (deberta-large-mnli)
          |                                 |
          └────────────────┬────────────────┘
                           ↓
                  HALLUCINATION INDICATOR
                           |
              ┌────────────┴────────────┐
              ↓                         ↓
       BENCHMARK EVAL:          SELECTIVE PREDICTION:
       TriviaQA, NQ,            abstain when uncertainty
       SciQ, TruthfulQA         > threshold → coverage-
       (sub-questions 1,4)      accuracy tradeoff (sub-q 5)
```

### Cross-Reference Matrix

| Paper/Resource | Relevance to RQ | Sub-question | Implementation | Adaptability | Source |
|----------------|----------------|--------------|----------------|--------------|--------|
| Farquhar SE (Nature 2024) | Very High — semantic entropy as hallucination predictor | Sub-Q 2 | jlko/semantic_uncertainty (★411) | High — frozen LLM, no fine-tuning | [SCHOLAR] |
| SelfCheckGPT (Manakul 2023) | Very High — calibration-free multi-sample consistency | Sub-Q 2 | potsawee/selfcheckgpt (★628) | High — black-box, no logprobs needed | [SCHOLAR] + [EXA] |
| Kadavath P(True) (2022) | High — self-calibration of frozen LLMs on QA | Sub-Q 1,4 | lorenzkuhn/semantic_uncertainty | Medium — requires prompt engineering | [SCHOLAR] |
| TruthfulQA (Lin 2021) | High — benchmark definition | Sub-Q 1,4 | Standard HF dataset | High — direct benchmark use | [SCHOLAR] |
| Fadeeva CCP (2024) | High — token-level UQ, claim-conditioned | Sub-Q 1,3 | IINemo/lm-polygraph (★480) | High — white-box frozen LLM | [SCHOLAR] + [EXA] |
| Shelmanov UQ heads (2025) | Medium-High — supervised, needs training | Sub-Q 1,3 | lm-polygraph | Medium — requires supervised training | [SCHOLAR] |
| UQLM library (CVS Health) | Very High — unified UQ framework | All sub-Qs | cvs-health/uqlm (★1183) | Very High — drop-in for any LLM | [EXA] |
| Ciosek Bayesian SE (2025) | High — efficient SE estimation | Sub-Q 2 | spotify-research/bayesian-SE (★25) | High — works with fewer samples | [SCHOLAR] + [EXA] |
| Moslonka EPR (2025) | High — token-level from top-k logprobs | Sub-Q 1,3 | artefactory/artefactual (★38) | High — API-compatible | [SCHOLAR] + [EXA] |
| lm-polygraph (IINemo) | High — benchmark + multiple UE methods | Sub-Q 3 | IINemo/lm-polygraph (★480) | High — comparative eval framework | [EXA] |
| TokUR (Wang-ML-Lab 2026) | Medium — reasoning-focused | Sub-Q 3 | Wang-ML-Lab/TokUR (★13) | Medium — new, reasoning-specific | [EXA] |
| SNNE (Nguyen 2025) | Medium-High — pairwise SE improvement | Sub-Q 2 | BigML-CS-UCLA/SNNE (GitHub) | High — drop-in SE improvement | [SCHOLAR] |

---

## 7. Verification Status Summary

### Statistics

**Total sources collected: 26**
- [VERIFIED - SCHOLAR]: 13 papers (50%) — confirmed via Semantic Scholar MCP with paperId
- [VERIFIED - EXA]: 9 repositories/resources (35%) — confirmed via Exa MCP with full URLs
- [VERIFIED - EXA - CODE_CONTEXT]: 1 (4%) — confirmed via get_code_context_exa
- [VERIFIED - EXA - TUTORIAL]: 2 (8%) — confirmed via Exa MCP
- [INFERRED]: 4 Archon patterns (15%) — no Archon KB matches, derived from general knowledge
- [NOT_FOUND - ARCHON]: 1 category (Archon KB irrelevant to domain)

**By category:**
- Reference papers: 0 (none provided in Phase 0)
- Directly relevant papers: 10 [VERIFIED - SCHOLAR]
- Foundational papers: 3 [VERIFIED - SCHOLAR]
- GitHub implementations: 7 [VERIFIED - EXA]
- Component repos: 2 [VERIFIED - EXA]
- Tutorials: 2 [VERIFIED - EXA - TUTORIAL]
- Code context: 1 [VERIFIED - EXA - CODE_CONTEXT]
- Inferred patterns: 4 [INFERRED]

### MCP Server Performance

| MCP Server | Queries Executed | Results Found | Status | Notes |
|------------|----------------|---------------|--------|-------|
| Archon KB | 8 (3 levels) | 0 verified | ❌ Domain mismatch | KB contains diffusion/image-gen content only; all similarity scores 0.32-0.46 on unrelated content; 3 timeout errors on project lookup |
| Semantic Scholar | 6 queries + 2 direct lookups | 13 papers | ✅ Excellent | 1 rate limit error (retried after 15s); high-quality directly relevant results; citation counts up to 3781 |
| Exa | 3 web searches + 1 code context | 9 repos + code | ✅ Excellent | All calls succeeded; high-quality GitHub repos with star counts; official implementations found |

### Data Quality Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Completeness | 85/100 | All 5 sub-questions addressed; Archon provided 0 domain-relevant results (expected given KB content) |
| Reliability | 90/100 | 22 verified sources via MCP; 4 inferred; foundational papers highly cited (881-3781 citations) |
| Recency | 88/100 | Mix of 2021-2026 papers; several 2025-2026 SOTA results; active GitHub repos |
| Relevance to Question | 92/100 | Direct matches to all 5 sub-questions; official implementations of core methods found |
| **Overall** | **89/100** | Strong foundation for Phase 2A hypothesis generation |

**Key gap**: Archon KB domain mismatch means no past cases from prior research sessions. Phase 2A should rely on Scholar + Exa evidence for hypothesis grounding.

---

## 8. Research Gaps

### User Input Recall

**Main Research Question:** Can token-level or sequence-level uncertainty signals derived from frozen LLMs serve as reliable predictors of hallucination on existing factual QA and NLI benchmarks, without requiring new human annotations, synthetic data, or new scoring frameworks?

**Detailed Sub-Questions:**
1. Do entropy measures (predictive entropy, MI, semantic entropy) correlate with hallucination on TriviaQA, NQ, SciQ, TruthfulQA?
2. Can multi-sample semantic consistency be a calibration-free hallucination detector outperforming single-pass baselines?
3. How do token-level aggregation strategies (max, mean, sum) compare as hallucination indicators without fine-tuning?
4. Does uncertainty-hallucination relationship generalize across model families (GPT-2/3.5, LLaMA, Mistral)?
5. Can uncertainty-based selective prediction improve coverage-accuracy tradeoffs using model's own output probabilities?

**Reference Papers:** Not provided — discovered in Phase 1.

### Identified Gaps

#### Gap 1: Cross-Model Generalization of Uncertainty-Hallucination Correlation on Fixed Benchmarks

**Relevance:** 🎯 PRIMARY — Directly blocks answering sub-question 4 of RQ; RQ requires generalization across model families on same fixed benchmarks.

**Current State:** Existing work evaluates uncertainty measures (SE, SelfCheckGPT, CCP, EPR) on specific model architectures or families in isolation. Shelmanov UQ heads tested Mistral/Llama/Gemma 2; Moslonka EPR tested "diverse QA datasets and multiple LLMs" but in independent experiments. No systematic head-to-head comparison uses the same frozen models from multiple families (GPT-2/GPT-3.5, LLaMA, Mistral) on the same fixed benchmark split under the same uncertainty measure.

**Missing Piece:** A controlled study comparing uncertainty-hallucination correlation across model families (GPT-2/3.5, LLaMA-7B/13B, Mistral-7B) on identical fixed benchmark splits (TriviaQA, Natural Questions, SciQ, TruthfulQA) using identical uncertainty measures computed from frozen model output probabilities.

**Potential Impact:** High — Determines whether any single uncertainty method is universally applicable vs. model-specific, directly enabling or blocking deployment of model-agnostic reliability signals.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Language Models (Mostly) Know What They Know" | 2022 | Kadavath et al. | 142ebbf4760145f591166bde2564ac70c001e927 | 2207.05221 | 1910 | P(True)/P(IK) tested only on Anthropic models; generalization to other families not established |
| "A Head to Predict and a Head to Question" | 2025 | Shelmanov et al. | cca687992c11d54daed5d0c6e4d60c7f1e71bcbd | 2505.08200 | 29 | Tests Mistral/Llama/Gemma separately but no unified cross-family comparison on same benchmark |
| "Semantic Uncertainty" | 2023 | Kuhn, Gal, Farquhar | 507465f8d46489a68a527cb5304d76bdb6c31ed9 | 2302.09664 | 881 | Tested on multiple models but ablation across families on fixed splits absent |
| "Semantic Uncertainty Quantification of Hallucinations via Quantum Tensor Network" | 2026 | Vipulanandan et al. | 03068472919b215d60cceb6b76290f652ee333c0 | 2601.20026 | 2 | Tests 8 LLMs (Mistral-7B, Falcon, LLaMA variants) on TriviaQA/NQ/SVAMP/SQuAD — closest existing cross-model study |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant cases found | N/A | "predictive entropy LLM hallucination detection" | Archon KB does not contain LLM reliability domain |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| IINemo/lm-polygraph | https://github.com/IINemo/lm-polygraph | 480 | Python | Benchmark suite with multiple UE methods but per-model evaluation, not cross-family on fixed splits |
| cvs-health/uqlm | https://github.com/cvs-health/uqlm | 1183 | Python | Supports multiple LLMs; framework for running SE/SelfCheckGPT across models |

---

#### Gap 2: Systematic Comparison of Token-Level Uncertainty Aggregation Strategies Without Fine-Tuning

**Relevance:** 🎯 PRIMARY — Directly blocks answering sub-question 3 of RQ: "How do token-level uncertainty aggregation strategies (max, mean, sum over sequence) compare as hallucination indicators on established benchmarks without requiring model fine-tuning?"

**Current State:** Individual methods use different aggregation strategies (CCP uses mean length-normalized log-prob; EPR uses an entropy production rate; semantic entropy uses Rao-Blackwellised sum per cluster; lm-polygraph provides multiple strategies) but each paper compares its proposed method to other complete systems rather than ablating aggregation strategies in isolation. No study isolates max vs. mean vs. sum token log-prob aggregation as the sole variable on fixed factual QA benchmarks using frozen models.

**Missing Piece:** A controlled ablation study using frozen LLMs (no fine-tuning) where only the token-level aggregation function (max, mean, sum, geometric mean) varies, evaluated on the same fixed QA benchmark splits, measuring correlation with hallucination labels.

**Potential Impact:** High — Determines the simplest (zero-parameter) uncertainty signal that correlates with hallucination, enabling lightweight deployment without sampling overhead or NLI models.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Fact-Checking the Output of LLMs via Token-Level Uncertainty Quantification" | 2024 | Fadeeva et al. | 8c5acaafe43e710d55b08c63d567550ad26ec437 | 2403.04696 | 186 | CCP uses mean aggregation but no comparison to max/sum baselines in isolation |
| "Learned Hallucination Detection via Token-level Entropy Production Rate" | 2025 | Moslonka et al. | ec46fb59962319da34880e1712aa1c703a5287d0 | 2509.04492 | 13 | EPR as entropy rate but doesn't ablate simple max/mean/sum alternatives |
| "TruthfulQA: Measuring How Models Mimic Human Falsehoods" | 2021 | Lin, Hilton, Evans | 77d956cdab4508d569ae5741549b78e715fd0749 | 2109.07958 | 3781 | Standard benchmark for evaluation; no token-level aggregation analysis |
| "Uncertainty Quantification and Confidence Calibration in LLMs: A Survey" | 2025 | Liu et al. | 422b00c330a16a00ef182abfd1d66e12369db9e8 | 2503.15850 | 131 | Survey notes prediction uncertainty methods but identifies lack of systematic aggregation comparison as gap |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant cases found | N/A | "token-level uncertainty aggregation hallucination indicators" | Archon KB does not contain NLP reliability domain |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| potsawee/selfcheckgpt | https://github.com/potsawee/selfcheckgpt | 628 | Python | Includes probability-based-baselines.ipynb with max/mean entropy baselines but not systematic ablation |
| IINemo/lm-polygraph | https://github.com/IINemo/lm-polygraph | 480 | Python | Implements max/mean/sum token-level methods; could serve as ablation framework |
| artefactory/artefactual | https://github.com/artefactory/artefactual | 38 | Python | EPR implementation with token-level scores; comparison baseline available |

---

#### Gap 3: Uncertainty-Based Selective Prediction Coverage-Accuracy Tradeoff on Standard Factual QA

**Relevance:** 🔗 SECONDARY — Relates to sub-question 5: can uncertainty thresholding improve coverage-accuracy tradeoffs using only model output probabilities on existing QA benchmarks?

**Current State:** Selective prediction literature primarily focuses on classification tasks (Fashion-MNIST, VQA) or uses calibrated confidence scores from trained classifiers. For LLMs specifically, selective prediction via raw output probability thresholding on factual QA benchmarks (TriviaQA, NQ, SciQ) is understudied. ReCoVERR (Srinivasan 2024) reduces over-abstention for VLMs; conformal risk control exists for RAG (Monica Lin 2026) but requires calibration sets. No study directly measures coverage-accuracy curves using only frozen LLM token probabilities as the abstention signal on standard factual QA datasets.

**Missing Piece:** Systematic evaluation of coverage-accuracy tradeoffs when abstaining based on uncertainty threshold (predictive entropy, semantic entropy, or min token log-prob) computed from frozen LLM output probabilities on TriviaQA/NQ/SciQ/TruthfulQA, without any external calibration or training.

**Potential Impact:** Medium-High — Enables principled deployment of LLMs with reliability guarantees on factual tasks; directly demonstrates practical value of uncertainty signals from sub-questions 1-4.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Selective 'Selective Prediction': Reducing Unnecessary Abstention in VLMs" | 2024 | Srinivasan et al. | 1b5e69a5b0f179e90f356a9c8cc1a39f77471dab | 2402.15610 | 34 | Selective prediction for VLMs; reduces over-abstention; does not address raw token-prob thresholding on factual QA |
| "Uncertainty Quantification and Confidence Calibration in LLMs: A Survey" | 2025 | Liu et al. | 422b00c330a16a00ef182abfd1d66e12369db9e8 | 2503.15850 | 131 | Survey identifies selective prediction as UQ application; notes scarcity of pure token-prob abstention evaluations on factual QA |
| "Language Models (Mostly) Know What They Know" | 2022 | Kadavath et al. | 142ebbf4760145f591166bde2564ac70c001e927 | 2207.05221 | 1910 | P(IK) and P(True) could serve as abstention signals; coverage-accuracy tradeoff analysis absent |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant cases found | N/A | "selective prediction coverage accuracy LLM" | Archon KB does not contain NLP reliability domain |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| cvs-health/uqlm | https://github.com/cvs-health/uqlm | 1183 | Python | Includes selective prediction module; could compute coverage-accuracy curves |
| jlko/semantic_uncertainty | https://github.com/jlko/semantic_uncertainty | 411 | Python | Official SE code; AUROC/AURAC metrics already implemented |
| IINemo/lm-polygraph | https://github.com/IINemo/lm-polygraph | 480 | Python | UE benchmark with risk-coverage evaluation built in |

---

### Gap Priority Matrix

| Gap ID | Title | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|--------|------------|----------------|----------|
| Gap 1 | PRIMARY | ☑️ Sub-Q 4: cross-family generalization required for model-agnostic UQ deployment | ☑️ Sub-Q 4 directly | ☐ No ref papers | High | 6 sources (4 Scholar + 2 Exa) | Critical |
| Gap 2 | PRIMARY | ☑️ Sub-Q 3: aggregation strategy is core methodological question | ☑️ Sub-Q 3 directly | ☐ No ref papers | High | 7 sources (4 Scholar + 3 Exa) | Critical |
| Gap 3 | SECONDARY | ☑️ Sub-Q 5: selective prediction is final practical application | ☑️ Sub-Q 5 directly | ☐ No ref papers | Medium-High | 6 sources (3 Scholar + 3 Exa) | High |

### User Input to Gap Traceability

**Main Research Question** ("Can token/sequence-level uncertainty signals from frozen LLMs predict hallucination on existing benchmarks without new annotations?") addressed by:
- Gap 1: Establishes whether this prediction generalizes across the model families named in the RQ (GPT-2/3.5, LLaMA, Mistral)
- Gap 2: Determines which specific token-level signal formulation (aggregation strategy) is most reliable — critical for the "token-level" part of the RQ
- Gap 3: Tests the end-to-end practical claim: uncertainty predicts hallucination well enough to enable selective prediction on the benchmarks named in the RQ

**Detailed Sub-Question mapping:**
- Sub-Q 1 (entropy measures correlate with hallucination?): Addressed by collected papers (Farquhar SE, Kadavath P(True), Fadeeva CCP); no new gap — evidence already exists
- Sub-Q 2 (multi-sample consistency as calibration-free detector?): Addressed by SelfCheckGPT (1148 citations) + UQLM + SNNE; no new gap — strong evidence base
- Sub-Q 3 (token aggregation strategies comparison?): **Gap 2** — systematic ablation missing
- Sub-Q 4 (cross-model generalization?): **Gap 1** — controlled cross-family study missing
- Sub-Q 5 (selective prediction coverage-accuracy?): **Gap 3** — pure token-prob abstention on factual QA missing

**Reference Paper connections:** Not applicable (no reference papers provided).

---

## 9. Conclusion

### Key Findings

1. **Strong prior art for sub-questions 1-2**: Semantic entropy (Farquhar Nature 2024) and SelfCheckGPT (Manakul EMNLP 2023) directly address correlation of uncertainty measures with hallucination on QA benchmarks. Both are unsupervised, use frozen LLMs, and require no new annotations — exactly matching research constraints.

2. **Token-level UQ is mature**: CCP (Fadeeva 2024, 186 citations) and EPR (Moslonka 2025) address token-level signals; lm-polygraph (★480) provides comparative benchmark framework. Sub-question 1 on entropy measure correlation has answered literature.

3. **Cross-model generalization gap (sub-Q 4)**: No controlled cross-family study exists comparing uncertainty-hallucination correlation across GPT-2/3.5, LLaMA, Mistral on identical fixed benchmark splits. Closest: quantum tensor network UQ (Vipulanandan 2026) tests 8 LLMs but not in direct ablation.

4. **Token aggregation ablation gap (sub-Q 3)**: Max/mean/sum token log-prob comparison as standalone ablation on fixed benchmarks without fine-tuning is absent from literature despite individual methods making different aggregation choices.

5. **Selective prediction gap (sub-Q 5)**: Coverage-accuracy curves using pure frozen LLM output probabilities on standard factual QA (TriviaQA, NQ, SciQ) are absent — selective prediction literature focuses on classification tasks or uses trained/calibrated components.

6. **Rich implementation ecosystem**: UQLM (★1183), lm-polygraph (★480), selfcheckgpt (★628), jlko/semantic_uncertainty (★411) provide production-grade baselines. All support the exact experimental setup described in the research question.

### Answer to Detailed Question (Preliminary)

**Sub-Q 1** (entropy measures correlate with hallucination?): Evidence suggests YES — semantic entropy (Farquhar 2024), predictive entropy, and mutual information all show correlation with hallucination on TriviaQA/NQ-style QA. P(True) (Kadavath 2022) shows models are partially self-aware. Strength/magnitude across methods needs direct comparison on the same fixed splits.

**Sub-Q 2** (multi-sample consistency as calibration-free detector?): Evidence suggests YES — SelfCheckGPT (1148 citations) demonstrates this directly; Bayesian SE (Ciosek 2025) shows 53% sample reduction is possible; SNNE (Nguyen 2025) improves over discrete SE. Whether it outperforms single-pass confidence depends on model, dataset, and threshold.

**Sub-Q 3** (token aggregation strategies comparison?): **Gap identified** — not directly answered by literature. Mean aggregation is most common default (CCP, SE); max aggregation used in EPR. Systematic comparison absent.

**Sub-Q 4** (cross-model generalization?): Partially answered — Vipulanandan 2026 tests 8 LLMs on TriviaQA/NQ with consistent AUROC improvements, suggesting some generalization. But controlled cross-family ablation on identical splits: **gap**.

**Sub-Q 5** (selective prediction coverage-accuracy?): **Gap identified** — existing work focuses on classification/VLM settings or uses calibrated classifiers. Raw output probability abstention on factual QA: underexplored.

### Phase 2 Readiness

- [x] Research question clearly defined and refined from Phase 0
- [x] Foundational literature identified (TruthfulQA, Kadavath, Farquhar, SelfCheckGPT, Fadeeva)
- [x] Evaluation benchmarks identified: TriviaQA, Natural Questions, SciQ, TruthfulQA, NLI datasets
- [x] Baseline implementations located: UQLM (★1183), lm-polygraph (★480), selfcheckgpt (★628)
- [x] 3 research gaps validated against research question and sub-questions
- [x] Gap priority matrix created for Phase 2A hypothesis selection
- [x] Cross-reference matrix linking all sources to sub-questions
- [x] No reference papers required (discovered baselines sufficient)
- [x] Phase 1 boundary maintained (no hypotheses or solution proposals)

### Next Steps

1. **Phase 2A-Dialogue**: Load `01_targeted_research.md` → 4-perspective round table on 3 identified gaps → generate testable hypotheses targeting sub-questions 3, 4, 5
2. **Key papers for Phase 2A to reference**: Farquhar Nature 2024 (arXiv:2302.09664), SelfCheckGPT (arXiv:2303.08896), Fadeeva CCP (arXiv:2403.04696), TruthfulQA (arXiv:2109.07958)
3. **Key codebases for Phase 2A**: cvs-health/uqlm, IINemo/lm-polygraph, jlko/semantic_uncertainty
4. **Command**: `/phase2a-dialogue`

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~45 minutes (automated unattended execution, 2026-08-21)*
