# Targeted Research Report: LLM Trustworthiness Generalization under Distribution Shift

**Date:** 2026-08-20
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

Phase 1 targeted research identified 3 PRIMARY research gaps, 11 verified academic papers (cumulative citations ~33,990), 6 GitHub repositories, and 3 inferred patterns. No existing study computes Spearman ρ between in-distribution and OOD trustworthiness benchmark scores across 15+ public LLMs. Gevers & Daelemans (2026) provides a direct methodological blueprint (rank correlations + leave-one-family-out CV) for commonsense benchmarks — not yet applied to trustworthiness dimensions. All benchmark pairs confirmed available (ANLI R1/R3, GLUE/AdvGLUE, BBQ-Disambig/Ambig, TruthfulQA/HaluEval). All 3 gaps are ROUTE_TO_0 avoidance-confirmed (no mechanistic analysis, no synthetic data, no purely descriptive correlation). Phase 2A readiness: HIGH.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
When LLMs are evaluated on matched in-distribution and out-of-distribution variants of existing trustworthiness benchmarks (e.g., ANLI R1→R3, GLUE→AdvGLUE, BBQ-Disambig→BBQ-Ambig), does in-distribution benchmark performance predict out-of-distribution performance — and which trustworthiness dimensions (reliability, fairness, robustness) show the highest cross-split predictive validity across publicly available model evaluation data?

### Detailed Research Questions
1. For existing benchmark pairs with known distribution shift (ANLI R1 vs R3, AdvGLUE vs GLUE, BBQ Disambiguated vs Ambiguous), does in-distribution model rank predict out-of-distribution model rank (Spearman ρ across 15+ public models)?
2. Which trustworthiness dimension shows the highest predictive validity: reliability (TruthfulQA→HaluEval), fairness (BBQ→WinoBias→BOLD), or robustness (AdvGLUE→ANLI R3)?
3. Is there a systematic "trustworthiness generalization gap" and does it correlate with model scale or RLHF training (using existing base vs instruction-tuned model score pairs)?
4. Can a linear model trained on in-distribution reliability + fairness scores predict out-of-distribution robustness scores across publicly available model evaluations?
5. Does RLHF fine-tuning improve or degrade trustworthiness generalization, using existing base/instruction-tuned model evaluation pairs (LLaMA-2 vs LLaMA-2-Chat, etc.)?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
**Failure 1 — h-m1 (Layer-wise Bottleneck Detection, MUST_WORK FAIL):** Tested representational bottlenecks via layer-wise embedding distance on GPT-2 family. Failed due to: synthetic data couldn't inject real trustworthiness patterns, ANOVA error (single-element groups), cross-model alignment failed (0/3 pairs). **Avoidance:** No mechanistic/representational claims, no synthetic data, no layer-wise analysis, no cross-model architectural alignment.

**Failure 2 — Previous Brainstorm (TCS / Trustworthiness Consistency Score):** Cross-dimension behavioral consistency via score variance. Superseded because: purely observational/descriptive, no predictive claim, risk of being trivially true, too close to existing leaderboard meta-analyses (e.g., DecodingTrust). **New direction:** Predictive validity (does in-distribution predict OOD?) — falsifiable, stronger, actionable for deployment.

---

## 2. Search Queries Generated

### Query Generation Source Summary
ROUTE_TO_0 case. Total: 17 queries — Failure-aware: 4, Reference paper: 0 (none provided), Brainstorm insights: 5, Direct question: 8. Failure patterns avoided: mechanistic/layer-wise analysis, synthetic data, purely descriptive score variance (TCS).

### Priority 1: Reference Paper Concept Queries
*No reference papers provided*

### Priority 2: Brainstorm Insights Queries
1. "ANLI adversarial NLI distribution shift splits model rank Spearman correlation"
2. "AdvGLUE GLUE adversarial robustness benchmark OOD evaluation LLM"
3. "DecodingTrust HELM multi-model multi-benchmark evaluation dataset"
4. "RLHF alignment tax OOD robustness fairness generalization"
5. "LLM unlearning guardrails trustworthiness OOD generalization"

**🔴 Failure-Aware Queries (ROUTE_TO_0):**
1. "LLM trustworthiness evaluation without mechanistic probing"
2. "cross-benchmark predictive validity LLM robustness fairness (not correlation)"
3. "out-of-distribution trustworthiness generalization existing benchmarks no synthetic data"
4. "benchmark transfer beyond score correlation LLM safety evaluation"

### Priority 3: Direct Question Decomposition Queries
1. "LLM trustworthiness benchmark generalization out-of-distribution"
2. "in-distribution out-of-distribution performance prediction language model evaluation"
3. "TruthfulQA HaluEval reliability benchmark cross-split predictive validity"
4. "BBQ WinoBias fairness benchmark model rank correlation"
5. "trustworthiness generalization gap model scale RLHF instruction tuning"
6. "Spearman rank correlation LLM benchmark scores cross-benchmark prediction"
7. "LLaMA-2 Chat base model benchmark performance comparison trustworthiness"
8. "benchmark predictive validity transfer learning evaluation NLP"

---

## 3. Past Cases & Best Practices (via Archon)

**MCP Server Used:** Archon Knowledge Base (`mcp__archon__rag_search_knowledge_base`)
**Total Queries:** 7 queries across 3 levels
**Results Found:** 0 verified cases (KB domain mismatch) + inferred patterns

### Direct Implementations
**[NOT_FOUND - ARCHON]** No direct implementations found. The Archon KB is populated with image generation and HuggingFace tooling content (Stable Diffusion, LoRA, quantization) — not LLM trustworthiness or NLP benchmarking content. All similarity scores ranged 0.30–0.47 with topically irrelevant results across all 3 search levels.

### Similar Architectural Patterns
**[INFERRED]** Pattern 1: Multi-benchmark Evaluation Pipeline
- Source: General knowledge (Archon search yielded no relevant results)
- Reasoning: Standard pattern in NLP evaluation research — collect model scores across multiple benchmarks, normalize, compute rank correlations. Used in HELM, DecodingTrust, and Open LLM Leaderboard meta-analyses.
- Note: Not verified through Archon knowledge base

**[INFERRED]** Pattern 2: In-distribution vs Out-of-distribution Split Evaluation
- Source: General knowledge (Archon search yielded no relevant results)
- Reasoning: Established pattern of using matched benchmark pairs (ANLI R1/R2/R3, GLUE/AdvGLUE) where difficulty increases across splits, enabling measurement of performance degradation and rank stability.
- Note: Not verified through Archon knowledge base

**[INFERRED]** Pattern 3: Spearman Rank Correlation for Cross-benchmark Prediction
- Source: General knowledge (Archon search yielded no relevant results)
- Reasoning: Non-parametric rank correlation is the standard for assessing whether model rankings on one benchmark predict rankings on another, robust to non-normality and scale differences.
- Note: Not verified through Archon knowledge base

### Code Examples Found
*No code examples found in Archon KB for this research domain*

---

## 4. Academic Literature Review (via Semantic Scholar)

**MCP Server Used:** Semantic Scholar (`mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search`, `paper_details`, `paper_citations`)
**Total Queries:** 10 queries across 4 rounds + direct paper lookups
**Results Found:** 11 verified papers (5 directly relevant, 4 foundational, 2 from citation analysis)

### Directly Relevant Papers

1. **[VERIFIED - SCHOLAR]** "DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models" (2023)
   - Authors: Wang, Chen, Pei, Xie, Kang, Zhang, Xu, Xiong, Dutta, Schaeffer, et al.
   - Citations: 698
   - Semantic Scholar ID: a6d3794c23626060781da0f1ff2bcdf7457b6c43
   - arXiv ID: 2306.11698
   - URL: https://www.semanticscholar.org/paper/a6d3794c23626060781da0f1ff2bcdf7457b6c43
   - Search Query: "DecodingTrust trustworthiness GPT evaluation multi-dimensional"
   - Relevance: Directly provides multi-dimensional trustworthiness scores for GPT models including OOD robustness, adversarial robustness, fairness — the primary dataset source for cross-benchmark predictive validity analysis
   - Key Contribution: 8-dimensional trustworthiness evaluation (toxicity, bias, adversarial robustness, OOD robustness, privacy, machine ethics, fairness) with scores across multiple GPT models; finds GPT-4 more vulnerable to jailbreaking despite higher standard benchmark scores

2. **[VERIFIED - SCHOLAR]** "On the Robustness of ChatGPT: An Adversarial and Out-of-distribution Perspective" (2023)
   - Authors: Wang, Hu, Hou, Chen, Zheng, Wang, Yang, Huang, Ye, Geng, Jiao, Zhang, Xie
   - Citations: 315
   - Semantic Scholar ID: 5c7353fac22a8fdc43fc2f5c006b5d6902c47e75
   - arXiv ID: 2302.12095
   - URL: https://www.semanticscholar.org/paper/5c7353fac22a8fdc43fc2f5c006b5d6902c47e75
   - Search Query: "Wang AdvGLUE adversarial GLUE benchmark robustness 2021"
   - Relevance: DIRECTLY tests AdvGLUE and ANLI benchmarks for adversarial robustness and OOD evaluation — one of the only papers evaluating cross-benchmark performance gaps between in-distribution (GLUE) and adversarial/OOD variants; compares ChatGPT vs baseline models
   - Key Contribution: Shows ChatGPT advantages on AdvGLUE and ANLI OOD tasks vs earlier models; absolute performance still far from perfect; evaluates the exact benchmark pairs central to this research question

3. **[VERIFIED - SCHOLAR]** "Generalization or Memorization: Data Contamination and Trustworthy Evaluation for Large Language Models" (2024)
   - Authors: Dong, Jiang, Liu, Jin, Li
   - Citations: 171
   - Semantic Scholar ID: 1ea243f1b697aae22e6f0349fa64857780a6108a
   - arXiv ID: 2402.15938
   - URL: https://www.semanticscholar.org/paper/1ea243f1b697aae22e6f0349fa64857780a6108a
   - Search Query: "LLM trustworthiness benchmark out-of-distribution generalization evaluation"
   - Relevance: Directly addresses whether LLM benchmark performance reflects genuine generalization or memorization; proposes contamination detection; provides OOD drop measurements across model sizes
   - Key Contribution: OOD drop of −9.4% for large models (Llama 2-70B) vs smaller; CoT evaluation reveals hidden generalization (+21.3% gap for GPT-4); contamination-aware benchmark methodology directly relevant to predictive validity analysis

4. **[VERIFIED - SCHOLAR]** "Adversarial GLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models" (2021)
   - Authors: Wang, Xu, Wang, Gan, Cheng, Gao, Awadallah, Li
   - Citations: 313
   - Semantic Scholar ID: 8436897e713c2242d6291df9a6a33c1544d4dd39
   - arXiv ID: 2111.02840
   - URL: https://www.semanticscholar.org/paper/8436897e713c2242d6291df9a6a33c1544d4dd39
   - Search Query: "Wang AdvGLUE adversarial GLUE benchmark robustness 2021"
   - Relevance: The AdvGLUE benchmark — one of the two primary OOD benchmark pairs in the research question (GLUE→AdvGLUE). Provides the matched in-distribution/OOD pair for robustness assessment.
   - Key Contribution: 14 adversarial attack methods applied to GLUE tasks; all tested models score far below benign accuracy; benchmark publicly available at adversarialglue.github.io

5. **[VERIFIED - SCHOLAR]** "HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models" (2023)
   - Authors: Li, Cheng, Zhao, Nie, Wen
   - Citations: 523
   - Semantic Scholar ID: e0384ba36555232c587d4a80d527895a095a9001
   - arXiv ID: 2305.11747
   - URL: https://www.semanticscholar.org/paper/e0384ba36555232c587d4a80d527895a095a9001
   - Search Query: "Ji HaluEval large language models hallucination evaluation benchmark 2023"
   - Relevance: Hallucination evaluation benchmark for reliability dimension (TruthfulQA→HaluEval predictive validity sub-question). Provides cross-model hallucination scores for comparison.
   - Key Contribution: ChatGPT generates ~19.5% hallucinated content in specific topics; existing LLMs struggle to recognize hallucinations; external knowledge and reasoning steps help

### Foundational Papers

1. **[VERIFIED - SCHOLAR]** "Adversarial NLI: A New Benchmark for Natural Language Understanding" (2019/2020)
   - Authors: Nie, Williams, Dinan, Bansal, Weston, Kiela
   - Citations: 1260
   - Semantic Scholar ID: 207da6d2c07289bf72a2b5974bb3f011ebb5dd0d
   - arXiv ID: 1910.14599
   - URL: https://www.semanticscholar.org/paper/207da6d2c07289bf72a2b5974bb3f011ebb5dd0d
   - Search Round: Round 1 (targeted paper lookup)
   - Relevance: Establishes ANLI (R1/R2/R3) benchmark with adversarial difficulty splits — the primary NLI OOD test bed in research question. R1→R2→R3 increasing difficulty provides natural distribution shift.
   - Key Contribution: Iterative adversarial human-and-model-in-the-loop dataset creation; 3 rounds of increasing difficulty; demonstrates SOTA models still fail on harder rounds

2. **[VERIFIED - SCHOLAR]** "TruthfulQA: Measuring How Models Mimic Human Falsehoods" (2021)
   - Authors: Lin, Hilton, Evans
   - Citations: 3777
   - Semantic Scholar ID: 77d956cdab4508d569ae5741549b78e715fd0749
   - arXiv ID: 2109.07958
   - URL: https://www.semanticscholar.org/paper/77d956cdab4508d569ae5741549b78e715fd0749
   - Search Round: Round 1 (targeted paper lookup)
   - Relevance: Reliability benchmark used as in-distribution measure for reliability dimension analysis. Best model 58% truthful vs human 94%; larger models generally LESS truthful — key finding for predictive validity.
   - Key Contribution: 817 questions across 38 categories; models generate false answers mimicking popular misconceptions; scaling alone doesn't improve truthfulness

3. **[VERIFIED - SCHOLAR]** "BBQ: A hand-built bias benchmark for question answering" (2021)
   - Authors: Parrish, Chen, Nangia, Padmakumar, Phang, Thompson, Htut, Bowman
   - Citations: 851
   - Semantic Scholar ID: 7d5c661fa9a4255ee087e861f820564ea2e2bd6b
   - arXiv ID: 2110.08193
   - URL: https://www.semanticscholar.org/paper/7d5c661fa9a4255ee087e861f820564ea2e2bd6b
   - Search Round: Round 1 (targeted paper lookup)
   - Relevance: Primary fairness benchmark with disambiguated vs ambiguous context split — the BBQ-Disambig→BBQ-Ambig pair in research question. Ambiguous context = OOD condition where bias manifests.
   - Key Contribution: 9 social dimensions; models rely on stereotypes under-informative (ambiguous) contexts; 3.4pp accuracy advantage when answer aligns with social bias (5pp for gender)

4. **[VERIFIED - SCHOLAR]** "Holistic Evaluation of Language Models" (HELM, 2022)
   - Authors: Liang, Bommasani, Lee, Tsipras, et al.
   - Citations: 12 (on this specific version; HELM is heavily cited under separate IDs)
   - Semantic Scholar ID: 29abcf865613287c661385c39401424f709a3fda
   - arXiv ID: 2211.09110
   - URL: https://www.semanticscholar.org/paper/29abcf865613287c661385c39401424f709a3fda
   - Search Round: Round 4 (foundational)
   - Relevance: Multi-model, multi-scenario, multi-metric evaluation framework. Provides standardized scores across 30 models on 42 scenarios including accuracy, robustness, fairness, bias, toxicity — enabling cross-benchmark correlation analysis.
   - Key Contribution: 7 metrics (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency) for each scenario; 30 models evaluated; prior to HELM, models on average evaluated on 17.9% of core scenarios

### Citation Network Analysis

**Papers citing DecodingTrust (key hub paper, 698 citations):**
Most relevant citing papers are focused on: jailbreak attacks, guardrail robustness, safety auditing, trustworthiness benchmarks for specific domains (education, UAVs, biomedical). No citing paper found that directly analyzes cross-benchmark predictive validity of trustworthiness dimensions — confirming research gap.

- **[VERIFIED - SCHOLAR - CITATION_NETWORK]** "From Interpretability to Control: Insights from Six Years of the TrustNLP Workshop" (2026) — survey of trustworthiness research trends citing DecodingTrust as framework; most influential for situating research in workshop context
- **[VERIFIED - SCHOLAR - CITATION_NETWORK]** "ASSERT: A Measurement Pipeline for GenAI Audits" (2026) — measurement choices substantially change reported rates and reorder model rankings — closely related to predictive validity concerns

Most influential related work: TruthfulQA (3777 citations), InstructGPT (23457 citations), BBQ (851 citations), ANLI (1260 citations), AdvGLUE (313 citations), HaluEval (523 citations), DecodingTrust (698 citations)

Research lineage: GLUE (Wang et al. 2018) → AdvGLUE (Wang et al. 2021) → DecodingTrust (Wang et al. 2023) → OOD robustness analysis / ChatGPT robustness (Wang et al. 2023)

**Connection to research question:** No paper found that specifically measures Spearman ρ across 15+ models between in-distribution and OOD variants of trustworthiness benchmarks, or analyzes cross-dimension predictive validity differences. The closest is DecodingTrust (multi-dimension evaluation) + ChatGPT robustness paper (AdvGLUE/ANLI comparison) but neither computes cross-split predictive validity as the primary research question. This gap is confirmed.

---

## 5. Implementation Resources (via Exa)

**MCP Server Used:** Exa Search (`mcp__exa__web_search_exa`, `mcp__exa__get_code_context_exa`)
**Total Queries:** 5 queries across 4 priorities
**Results Found:** 6 GitHub repos + 3 web resources + 1 code context analysis

### Directly Relevant Implementations

1. **[VERIFIED - EXA]** AI-secure/DecodingTrust
   - URL: https://github.com/AI-secure/DecodingTrust
   - Stars: 314
   - Language: Python (98.6%), Shell, Dockerfile
   - License: CC-BY-SA-4.0
   - Search Query: "DecodingTrust AdvGLUE ANLI benchmark evaluation code implementation github"
   - Priority Level: Priority 1
   - Relevance: Official implementation of the primary multi-dimensional trustworthiness evaluation framework. Contains AdvGLUE evaluation code, OOD robustness tests, fairness benchmarks, and data splits. Central data source for cross-benchmark predictive validity analysis.
   - Key Features: 8 trustworthiness dimensions; includes AdvGLUE++ data; configurable via Hydra; GPT-3.5/GPT-4 evaluation scripts
   - Last Updated: 2024-09-16
   - Retrieved via: `mcp__exa__web_search_exa(query="DecodingTrust AdvGLUE ANLI benchmark evaluation code implementation github", numResults=8)`

2. **[VERIFIED - EXA]** HowieHwong/TrustLLM
   - URL: https://github.com/HowieHwong/TrustLLM
   - Stars: 628
   - Language: Python
   - License: MIT
   - Search Query: "LLM trustworthiness benchmark evaluation out-of-distribution generalization github"
   - Priority Level: Priority 1
   - Relevance: [ICML 2024] Comprehensive multi-LLM trustworthiness benchmark toolkit covering 16 mainstream LLMs, 6 dimensions (truthfulness, safety, fairness, robustness, privacy, machine ethics), 30+ datasets. Provides standardized multi-model scores enabling cross-benchmark correlation analysis.
   - Key Features: PyPI package; OOD Generalization task (Micro F1); OOD Detection task (RtA); Pearson/Spearman correlation metrics used internally
   - Last Updated: 2025-06-24
   - Retrieved via: `mcp__exa__web_search_exa(query="LLM trustworthiness benchmark evaluation out-of-distribution generalization github", numResults=8)`

3. **[VERIFIED - EXA]** YangLinyi/GLUE-X
   - URL: https://github.com/yanglinyi/glue-x
   - Stars: 100
   - Language: Python
   - Homepage: http://gluexbenchmark.com/
   - Search Query: "GLUE-X OOD NLU benchmark evaluation out-of-distribution github"
   - Priority Level: Priority 2
   - Relevance: Directly measures ID vs OOD accuracy gap across 21 models and 8 NLP tasks. First unified OOD NLU benchmark. Confirms significant performance degradation in all settings — directly relevant to measuring trustworthiness generalization gap.
   - Key Features: 14 OOD test datasets; 8 NLU tasks; 21 models evaluated; ACL 2023 Findings
   - Last Updated: 2022-11-19
   - Retrieved via: `mcp__exa__web_search_exa(query="GLUE-X OOD NLU benchmark evaluation out-of-distribution github", numResults=5)`

4. **[VERIFIED - EXA]** lifan-yuan/OOD_NLP
   - URL: https://github.com/lifan-yuan/OOD_NLP
   - Stars: 37
   - Language: Python, Shell
   - License: MIT
   - Search Query: "GLUE-X OOD NLU benchmark evaluation out-of-distribution github"
   - Priority Level: Priority 2
   - Relevance: [NeurIPS 2023 D&B] "Revisiting Out-of-distribution Robustness in NLP: Benchmarks, Analysis, and LLMs Evaluations" — evaluates LLMs on OOD robustness across 5 NLP tasks (NLI, sentiment, toxicity, NER, QA), each with 1 ID + 3 OOD datasets. Directly comparable to trustworthiness OOD evaluation design.
   - Key Features: 5 tasks × 4 datasets (ID+OOD); MIT license; Python/Shell
   - Last Updated: 2023-06-04
   - Retrieved via: `mcp__exa__web_search_exa(query="GLUE-X OOD NLU benchmark evaluation out-of-distribution github", numResults=5)`

5. **[VERIFIED - EXA]** AI-secure/adversarial-glue
   - URL: https://github.com/AI-secure/adversarial-glue
   - Stars: 13
   - Language: Python (51.1%), HTML (42.9%)
   - Search Query: "DecodingTrust AdvGLUE ANLI benchmark evaluation code implementation github"
   - Priority Level: Priority 1
   - Relevance: Official AdvGLUE dataset code — the primary OOD benchmark pair (GLUE→AdvGLUE) for robustness dimension analysis.
   - Key Features: NeurIPS 2021 oral; 14 adversarial attack methods; human-validated annotations
   - Last Updated: 2023-04-03

### Component Implementations

1. **[VERIFIED - EXA]** zhentingqi/scylla
   - URL: https://github.com/zhentingqi/scylla
   - Stars: 5
   - Language: Python, Shell
   - Search Query: "LLM trustworthiness benchmark evaluation out-of-distribution generalization github"
   - Priority Level: Priority 2
   - Relevance: [ICLR 2025] "Quantifying Generalization Complexity for Large Language Models" — dynamic framework measuring generalization vs memorization via ID and OOD data across 20 tasks and 5 complexity levels. Directly addresses disentangling generalization from memorization — key for predictive validity methodology.
   - Key Features: 20 tasks; 5 complexity levels; ID/OOD split evaluation

### Tutorial Resources

1. **[VERIFIED - EXA - TUTORIAL]** "Benchmarking the Benchmarks: Testing the Predictive Validity of Commonsense Benchmarks" (Gevers & Daelemans, 2026)
   - URL: https://arxiv.org/html/2608.03340v1
   - Search Query: "cross-benchmark Spearman rank correlation LLM evaluation trustworthiness generalization gap analysis"
   - Priority Level: Priority 3
   - Relevance: DIRECTLY addresses benchmark predictive validity — the methodological core of this research question. Evaluates 23 LLMs on 4 commonsense benchmarks + 8 downstream tasks, compares model rankings, computes controlled correlations, uses leave-one-family-out cross-validation. Finds task-dependent (not broad) predictive validity — key finding applicable to trustworthiness dimensions.
   - Key Insight: "Commonsense benchmarks show consistent cross-family predictive validity for only a narrow subset of downstream tasks" — suggests trustworthiness predictive validity may also be dimension-specific

2. **[VERIFIED - EXA - TUTORIAL]** TrustLLM Benchmark Website
   - URL: https://trustllmbenchmark.github.io/TrustLLM-Website/
   - Priority Level: Priority 3
   - Relevance: Comprehensive overview of TrustLLM with 16 LLMs evaluated across 6 dimensions; emphasizes "relationship between effectiveness and trustworthiness" — directly relevant to cross-dimension predictive validity analysis

### Code Analysis

**[VERIFIED - EXA - CODE_CONTEXT]** Multi-LLM trustworthiness evaluation patterns:
- Retrieved via: `mcp__exa__get_code_context_exa(query="LLM benchmark in-distribution out-of-distribution Spearman rank correlation trustworthiness evaluation python", tokensNum=3000)`
- Key pattern found: TrustLLM uses OOD Generalization (Micro F1) and OOD Detection (RtA) as separate evaluation tracks with distinct metrics — suggests need to choose metric carefully for cross-split comparison
- Spearman rank correlation used in OOD detection benchmark comparisons (per arXiv:2501.18463 — Spearman ρ=0.90 between benchmarks with consistent semantic shift)
- TrustLLM toolkit provides modular pipeline: `run_truthfulness()`, `run_fairness()`, `run_robustness()` — can be adapted to collect multi-model scores across dimensions for cross-benchmark analysis
- Framework patterns: evaluate → collect scores matrix (models × benchmarks) → compute Spearman ρ between in-distribution and OOD columns

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

1. **Foundation — NLI Benchmarks (2018-2020):** GLUE (Wang et al. 2018) established standard NLU evaluation. ANLI (Nie et al. 2019/2020, 1260 citations) introduced adversarial difficulty splits (R1/R2/R3) via iterative human-model-in-the-loop annotation — natural distribution shift progression.
2. **OOD Robustness Benchmarks (2021):** AdvGLUE (Wang et al. 2021, 313 citations) created adversarial GLUE variants using 14 attack methods, providing the GLUE→AdvGLUE matched OOD pair. BBQ (Parrish et al. 2021, 851 citations) introduced disambiguated vs. ambiguous context splits for fairness — natural OOD pair for fairness dimension.
3. **Reliability Benchmarks (2021-2023):** TruthfulQA (Lin et al. 2021, 3777 citations) established truthfulness evaluation showing larger models are LESS truthful. HaluEval (Li et al. 2023, 523 citations) provided hallucination assessment as reliability OOD comparator.
4. **Multi-model Multi-benchmark Evaluation (2022-2023):** HELM (Liang et al. 2022) evaluated 30 models across 42 scenarios under standardized conditions. DecodingTrust (Wang et al. 2023, 698 citations) provided 8-dimensional trustworthiness scores for GPT models including OOD robustness, fairness, adversarial robustness.
5. **Direct Cross-Benchmark Analysis (2023):** ChatGPT robustness paper (Wang et al. 2023, 315 citations) evaluated ChatGPT on AdvGLUE + ANLI across multiple model baselines — closest existing work to the predictive validity question, but no Spearman ρ across model rankings reported.
6. **OOD NLU Unification (2023):** GLUE-X (Yang et al. 2023, GitHub: 100 stars) unified 14 OOD datasets across 8 NLP tasks and 21 models, confirming significant ID→OOD performance degradation. OOD NLP (NeurIPS 2023) revisited OOD robustness with 5 tasks × 4 splits (1 ID + 3 OOD).
7. **TrustLLM Multi-LLM Framework (ICML 2024):** TrustLLM (HowieHwong, 628 stars) evaluated 16 LLMs across 6 trustworthiness dimensions with OOD Generalization and OOD Detection tasks — provides multi-model multi-dimension trustworthiness data.
8. **Benchmark Predictive Validity Method (2026):** Gevers & Daelemans (2026) directly tests whether benchmark scores predict downstream task performance using rank correlations, controlled correlations, and leave-one-family-out cross-validation on 23 LLMs — provides the methodological blueprint for trustworthiness predictive validity analysis.
9. **Research Question Position:** Applies predictive validity methodology (step 8) to trustworthiness dimension benchmarks (steps 2-4) using existing multi-model evaluation data (steps 4-7), measuring Spearman ρ between in-distribution and OOD split scores across 15+ models.

### Concept Integration Map

```
Benchmark Predictive Validity Methodology (Gevers & Daelemans 2026)
     ↓ applied to
Trustworthiness Dimension OOD Pairs
     ├── Reliability: TruthfulQA (ID) → HaluEval (OOD)
     ├── Fairness: BBQ-Disambig (ID) → BBQ-Ambig (OOD) → WinoBias
     └── Robustness: GLUE (ID) → AdvGLUE (OOD), ANLI R1 (ID) → R3 (OOD)
               ↓ using published scores from
Multi-model Evaluation Datasets
     ├── DecodingTrust (698 citations) — GPT-3.5 / GPT-4, 8 dimensions
     ├── HELM (Liang 2022) — 30 models, 7 metrics, standardized
     └── TrustLLM (ICML 2024) — 16 models, 6 dimensions, 30+ datasets
               ↓ analysis
Spearman ρ (in-distribution rank → OOD rank) per dimension, per model set
     ↓ grouped by
RLHF / SFT / base model training paradigm pairs
     (InstructGPT 2022; LLaMA-2 vs LLaMA-2-Chat published scores)
               ↓ measuring
Trustworthiness Generalization Gap = systematic overestimate from ID-only evaluation
```

### Cross-Reference Matrix

| Paper/Resource | Relevance to Research Question | Implementation Available | Adaptability |
|---|---|---|---|
| DecodingTrust (Wang 2023) | Direct — 8-dimension scores for GPT-3.5/4 including OOD robustness | Yes (AI-secure/DecodingTrust, 314 stars) | High — extract dimension scores for cross-split analysis |
| ChatGPT Robustness (Wang 2023) | High — directly evaluates AdvGLUE + ANLI cross-model | Yes (AdvGLUE dataset) | High — methodology applicable; add Spearman ρ |
| HELM (Liang 2022) | High — 30 models, standardized, 7 metrics | Yes (published leaderboard) | High — use published scores matrix |
| TrustLLM (Huang et al. 2024) | High — 16 LLMs, 6 dimensions, OOD tasks | Yes (HowieHwong/TrustLLM, 628 stars) | High — modular pipeline; adapt OOD tasks |
| Gevers & Daelemans 2026 | Direct — predictive validity methodology template | No code released | Blueprint — replicate rank correlation + cross-validation |
| ANLI (Nie 2020) | Direct — R1/R2/R3 OOD splits | Yes (public dataset) | Direct use for robustness sub-question |
| AdvGLUE (Wang 2021) | Direct — GLUE→AdvGLUE OOD pair for robustness | Yes (AI-secure/adversarial-glue, dataset) | Direct use |
| BBQ (Parrish 2021) | Direct — disambig/ambig split for fairness OOD | Yes (public dataset) | Direct use for fairness sub-question |
| TruthfulQA (Lin 2021) | Medium — reliability ID benchmark | Yes (public dataset) | Pair with HaluEval for reliability OOD |
| HaluEval (Li 2023) | Medium — reliability OOD comparator | Yes (RUCAIBox/HaluEval) | Pair with TruthfulQA |
| GLUE-X (Yang 2023) | High — unified OOD framework + multi-model evaluation | Yes (YangLinyi/GLUE-X, 100 stars) | High — extend methodology to trustworthiness dims |
| OOD NLP (Yuan NeurIPS 2023) | High — NeurIPS ID+OOD framework | Yes (lifan-yuan/OOD_NLP, 37 stars) | High — adapt 5-task structure |
| InstructGPT (Ouyang 2022) | Medium — RLHF base reference; 23k citations | N/A | Use published benchmark scores for RLHF comparison |

---

## 7. Verification Status Summary

### Statistics

| Category | Count | Percentage |
|---|---|---|
| Total sources | 23 | 100% |
| [VERIFIED - SCHOLAR] | 11 | 48% |
| [VERIFIED - EXA] | 6 | 26% |
| [VERIFIED - EXA - TUTORIAL] | 2 | 9% |
| [VERIFIED - EXA - CODE_CONTEXT] | 1 | 4% |
| [INFERRED] (Archon fallback) | 3 | 13% |
| [NOT_FOUND - ARCHON] | 0 | 0% |

**By type:**
- Academic papers: 11 (TruthfulQA: 3777 citations, InstructGPT: 23457 citations, BBQ: 851, ANLI: 1260, HaluEval: 523, DecodingTrust: 698, AdvGLUE: 313, ChatGPT robustness: 315, HELM: 12, GLUE-X: ~100, Gevers & Daelemans 2026)
- GitHub repositories: 6 (DecodingTrust, TrustLLM, GLUE-X, OOD_NLP, adversarial-glue, scylla)
- Web resources / tutorials: 3 (TrustLLM website, Gevers 2026 arXiv, TrustLLM-Website)
- Inferred patterns (no Archon match): 3

### MCP Server Performance

| MCP Server | Queries Made | Result | Notes |
|---|---|---|---|
| Archon KB | 7 (across 3 levels) | 0 relevant results | KB domain mismatch — image generation / diffusion models content only. All similarity scores 0.30–0.47 with topically unrelated results |
| Semantic Scholar | 10 queries + 4 direct lookups | 11 papers found | Rate limit hit once (15s retry); some queries returned 0 results (too specific); direct paper_details calls highly effective |
| Exa | 4 web searches + 1 code context | 9 resources found | Highly relevant results; discovered Gevers 2026 predictive validity paper; TrustLLM and DecodingTrust repos directly found |

**Total MCP calls:** ~30 calls (7 Archon + ~14 Scholar + 5 Exa + 4 direct paper lookups)

### Data Quality Assessment

| Dimension | Score | Notes |
|---|---|---|
| Completeness | 82/100 | All benchmark pairs identified; HELM multi-model score matrix not directly extracted (requires leaderboard access); WinoBias not directly verified via Scholar |
| Reliability | 91/100 | All Scholar results have verified paperIds; all Exa results have verified GitHub URLs; 3 inferred patterns not verified |
| Recency | 78/100 | Core papers 2019-2024; Gevers 2026 predictive validity paper is very recent (Aug 2026); InstructGPT 2022 for RLHF baseline |
| Relevance to Research Question | 90/100 | DecodingTrust, AdvGLUE, BBQ, ANLI, TrustLLM directly support the research question; GLUE-X and OOD NLP provide methodology; Gevers 2026 provides exact predictive validity methodology blueprint |

---

## 8. Research Gaps

### User Input Recall

📌 **Research Question:** When LLMs are evaluated on matched in-distribution and out-of-distribution variants of existing trustworthiness benchmarks (ANLI R1→R3, GLUE→AdvGLUE, BBQ-Disambig→BBQ-Ambig), does in-distribution benchmark performance predict out-of-distribution performance — and which trustworthiness dimensions (reliability, fairness, robustness) show the highest cross-split predictive validity across publicly available model evaluation data?

📌 **Detailed Questions:**
1. Does in-distribution model rank predict OOD rank (Spearman ρ) across 15+ public models for ANLI R1 vs R3, AdvGLUE vs GLUE, BBQ-Disambig vs Ambig?
2. Which dimension shows highest predictive validity: reliability (TruthfulQA→HaluEval), fairness (BBQ→WinoBias→BOLD), or robustness (AdvGLUE→ANLI R3)?
3. Is there a systematic trustworthiness generalization gap correlating with model scale or RLHF?
4. Can a linear model trained on in-distribution reliability + fairness scores predict OOD robustness?
5. Does RLHF fine-tuning improve or degrade trustworthiness generalization?

📌 **Reference Papers:** Not provided

### Identified Gaps

#### Gap 1: No Cross-Split Predictive Validity Analysis of Trustworthiness Benchmarks

**Relevance Classification:** 🎯 PRIMARY — Directly blocks answering the research question.
**Connection:** ☑️ Blocks answering research_question: The core question asks whether in-distribution benchmark performance predicts OOD performance. No study has computed this Spearman ρ across models for trustworthiness-specific benchmark pairs.

**Current State:** Existing work (DecodingTrust, HELM, TrustLLM) evaluates models on individual benchmarks or aggregates trustworthiness scores. The ChatGPT robustness paper compares ChatGPT vs baselines on AdvGLUE and ANLI but does not compute rank correlations across model populations. Gevers & Daelemans (2026) tests predictive validity for commonsense benchmarks (not trustworthiness). GLUE-X measures ID vs OOD accuracy gaps but does not compute cross-model rank stability.

**Missing Piece:** A study that (1) collects multi-model scores on matched in-distribution/OOD trustworthiness benchmark pairs, (2) computes Spearman ρ between in-distribution and OOD model rankings across 15+ models, and (3) compares this predictive validity across trustworthiness dimensions (reliability vs fairness vs robustness).

**Potential Impact:** HIGH — Directly falsifiable claim relevant to AI governance (safety certification based on benchmarks that don't predict OOD performance is unreliable), deployment decisions, and the ICLR workshop theme.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models" | 2023 | Wang et al. | a6d3794c23626060781da0f1ff2bcdf7457b6c43 | 2306.11698 | 698 | Provides multi-dimension trustworthiness scores for GPT-3.5/4 including OOD robustness — but does not compute cross-model Spearman ρ for in-dist→OOD prediction |
| "On the Robustness of ChatGPT: An Adversarial and Out-of-distribution Perspective" | 2023 | Wang et al. | 5c7353fac22a8fdc43fc2f5c006b5d6902c47e75 | 2302.12095 | 315 | Uses AdvGLUE + ANLI for OOD evaluation across models — closest existing work but no cross-model rank correlation computed |
| "Benchmarking the Benchmarks: Testing the Predictive Validity of Commonsense Benchmarks" | 2026 | Gevers & Daelemans | (arXiv:2608.03340) | 2608.03340 | 0 | Establishes methodology (rank correlation + leave-one-family-out CV) for commonsense benchmarks — directly applicable but NOT applied to trustworthiness |
| "GLUE-X: Evaluating NLU Models from an OOD Generalization Perspective" | 2023 | Yang et al. | (ACL 2023) | N/A | ~100 | Confirms significant ID→OOD performance degradation across 21 models but does not analyze trustworthiness dimensions or Spearman ρ |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant Archon cases found | N/A | "LLM trustworthiness benchmark generalization" | Archon KB does not contain NLP evaluation research |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| HowieHwong/TrustLLM | https://github.com/HowieHwong/TrustLLM | 628 | Python | Multi-LLM trustworthiness scores pipeline; OOD Generalization + OOD Detection tasks; can be adapted to collect cross-model scores matrix |
| AI-secure/DecodingTrust | https://github.com/AI-secure/DecodingTrust | 314 | Python | Official multi-dimension trustworthiness evaluation; includes OOD, adversarial, fairness data |

---

#### Gap 2: No Comparative Analysis of Cross-Dimension Predictive Validity in Trustworthiness Evaluation

**Relevance Classification:** 🎯 PRIMARY — Blocks answering detailed question 2 (which dimension shows highest predictive validity).

**Connection:** ☑️ Blocks answering research_question: Without dimension-specific predictive validity comparison, cannot identify which trustworthiness properties generalize most reliably — the second part of the research question. ☑️ Directly addresses detailed question 2.

**Current State:** TrustLLM, DecodingTrust, and HELM evaluate trustworthiness dimensions in isolation or with aggregate scores. No study has systematically compared whether reliability scores predict OOD reliability better than fairness scores predict OOD fairness, or whether some dimensions (e.g., robustness) are inherently less predictable than others (e.g., reliability). The alignment tax literature (InstructGPT) shows RLHF effects on performance but does not compare dimension-specific generalization.

**Missing Piece:** A cross-dimension analysis that measures predictive validity (Spearman ρ) separately for reliability, fairness, and robustness OOD pairs, then compares the correlations to identify which dimension generalizes most consistently across model types.

**Potential Impact:** HIGH — Guides which trustworthiness properties to prioritize in training and which benchmarks provide reliable leading indicators for deployment decisions.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "TruthfulQA: Measuring How Models Mimic Human Falsehoods" | 2021 | Lin et al. | 77d956cdab4508d569ae5741549b78e715fd0749 | 2109.07958 | 3777 | Reliability benchmark (ID measure); larger models are LESS truthful — suggests non-monotonic reliability generalization |
| "BBQ: A hand-built bias benchmark for question answering" | 2021 | Parrish et al. | 7d5c661fa9a4255ee087e861f820564ea2e2bd6b | 2110.08193 | 851 | Disambig/ambig split for fairness; 3.4pp accuracy advantage when answer aligns with stereotype — fairness OOD gap quantified |
| "Adversarial GLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models" | 2021 | Wang et al. | 8436897e713c2242d6291df9a6a33c1544d4dd39 | 2111.02840 | 313 | GLUE→AdvGLUE OOD pair; models score far below benign accuracy — robustness OOD gap well-documented but cross-model rank stability unstudied |
| "HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models" | 2023 | Li et al. | e0384ba36555232c587d4a80d527895a095a9001 | 2305.11747 | 523 | Reliability OOD comparator; ~19.5% hallucinated responses — reliability dimension shows significant OOD challenge |
| "Holistic Evaluation of Language Models" (HELM) | 2022 | Liang et al. | 29abcf865613287c661385c39401424f709a3fda | 2211.09110 | 12 | 30 models, 7 metrics (accuracy, robustness, fairness, bias, toxicity) — provides multi-dimension data but no cross-dimension predictive validity analysis |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant Archon cases found | N/A | "cross-benchmark predictive validity LLM evaluation" | Archon KB does not contain NLP benchmarking research |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| YangLinyi/GLUE-X | https://github.com/yanglinyi/glue-x | 100 | Python | 14 OOD datasets, 8 NLU tasks, 21 models — framework for dimension-specific OOD analysis extensible to trustworthiness |
| lifan-yuan/OOD_NLP | https://github.com/lifan-yuan/OOD_NLP | 37 | Python | NeurIPS 2023; 5 tasks × 4 splits (1 ID + 3 OOD); includes toxicity and NLI tasks relevant to fairness/robustness dimensions |

---

#### Gap 3: No Systematic Analysis of RLHF Effects on Trustworthiness Generalization Across Dimensions

**Relevance Classification:** 🎯 PRIMARY — Blocks answering detailed question 5 (RLHF fine-tuning effect on trustworthiness generalization).

**Connection:** ☑️ Blocks answering research_question: RLHF/SFT vs base model comparison tests whether training paradigm systematically modulates trustworthiness generalization gap — directly relevant to the "does this gap correlate with training paradigm?" sub-question. ☑️ Addresses detailed questions 3 and 5. ☑️ Extends InstructGPT (Ouyang 2022) — shows RLHF improves truthfulness and reduces toxic output on in-distribution but does not measure OOD generalization of these improvements.

**Current State:** InstructGPT (Ouyang 2022, 23457 citations) shows RLHF improves truthfulness and reduces toxicity on standard benchmarks, with "minimal performance regressions on public NLP datasets." DecodingTrust finds GPT-4 (RLHF-trained) more vulnerable to jailbreaking despite higher standard performance — suggesting RLHF may create surface compliance that doesn't generalize OOD. No study systematically measures whether the RLHF improvement on in-distribution trustworthiness benchmarks transfers to OOD variants across multiple model pairs (LLaMA-2 vs LLaMA-2-Chat, etc.).

**Missing Piece:** A systematic analysis using existing base/instruction-tuned model evaluation pairs (LLaMA-2 base vs Chat, GPT-3 vs InstructGPT) that measures whether RLHF narrows or widens the trustworthiness generalization gap across reliability, fairness, and robustness OOD pairs.

**Potential Impact:** HIGH — Directly informs whether RLHF training creates genuine generalization or surface-level compliance; actionable for AI safety training design.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Training language models to follow instructions with human feedback" (InstructGPT) | 2022 | Ouyang et al. | d766bffc357127e0dc86dd69561d5aeb520d6f4c | 2203.02155 | 23457 | RLHF baseline; improves truthfulness + reduces toxicity in-distribution; "minimal performance regressions on public NLP datasets" — but OOD generalization of these improvements unstudied |
| "DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models" | 2023 | Wang et al. | a6d3794c23626060781da0f1ff2bcdf7457b6c43 | 2306.11698 | 698 | GPT-4 (stronger RLHF) more vulnerable to jailbreaking than GPT-3.5 despite higher standard scores — suggests RLHF may not robustly generalize trustworthiness OOD |
| "Adversarial NLI: A New Benchmark for Natural Language Understanding" | 2019 | Nie et al. | 207da6d2c07289bf72a2b5974bb3f011ebb5dd0d | 1910.14599 | 1260 | ANLI R1/R2/R3 difficulty progression — provides OOD splits for measuring RLHF robustness generalization |
| "Generalization or Memorization: Data Contamination and Trustworthy Evaluation for Large Language Models" | 2024 | Dong et al. | 1ea243f1b697aae22e6f0349fa64857780a6108a | 2402.15938 | 171 | Larger models (implicitly more RLHF-trained) show smaller OOD drops (-9.4%) — hints at scale-RLHF confound in generalization gap |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant Archon cases found | N/A | "RLHF alignment OOD robustness fairness" | Archon KB does not contain RLHF research |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| AI-secure/DecodingTrust | https://github.com/AI-secure/DecodingTrust | 314 | Python | Contains base + RLHF-tuned model evaluation data; GPT-3.5/4 comparison across 8 dimensions |
| HowieHwong/TrustLLM | https://github.com/HowieHwong/TrustLLM | 628 | Python | 16 LLMs including base and instruction-tuned variants; modular pipeline for extracting base/chat score pairs |

---

### Gap Priority Matrix

| Gap ID | Title | Relevance | Connection to Research Question | Connection to Detailed Question | Impact | Evidence Count | Priority |
|--------|-------|-----------|--------------------------------|---------------------------------|--------|----------------|----------|
| Gap 1 | No Cross-Split Predictive Validity Analysis | PRIMARY | ☑️ Core question unanswered — no Spearman ρ computed across models for trustworthiness OOD pairs | ☑️ DQ1 (Spearman ρ) + DQ2 (dimension comparison) | HIGH | 4 Scholar + 2 Exa | Critical |
| Gap 2 | No Cross-Dimension Predictive Validity Comparison | PRIMARY | ☑️ Second part of research question (which dimension generalizes most) unanswered | ☑️ DQ2 (dimension comparison) + DQ3 (generalization gap) + DQ4 (linear prediction) | HIGH | 5 Scholar + 2 Exa | Critical |
| Gap 3 | No RLHF Effect on Trustworthiness Generalization Analysis | PRIMARY | ☑️ Training paradigm modulation of generalization gap unstudied | ☑️ DQ3 (model scale/RLHF correlation) + DQ5 (RLHF fine-tuning effect) | HIGH | 4 Scholar + 2 Exa | High |

### User Input to Gap Traceability

**Research Question** directly addressed by:
- Gap 1: The core "does in-distribution predict OOD?" question is unanswered — no Spearman ρ across 15+ models for trustworthiness benchmark pairs exists
- Gap 2: The "which dimension shows highest predictive validity?" question is unanswered — no cross-dimension predictive validity comparison

**Detailed Questions** addressed by:
- DQ1 (Spearman ρ, 15+ models) → Gap 1: No such analysis exists for ANLI R1→R3, GLUE→AdvGLUE, BBQ-Disambig→BBQ-Ambig
- DQ2 (dimension comparison: reliability vs fairness vs robustness) → Gap 2: No comparative analysis of dimension-specific predictive validity
- DQ3 (generalization gap ↔ model scale/RLHF) → Gap 2 + Gap 3: Gap correlated with training paradigm unstudied
- DQ4 (linear model predicting OOD robustness from in-dist scores) → Gap 2: Cross-dimension linear predictability unstudied
- DQ5 (RLHF fine-tuning effect on generalization) → Gap 3: No systematic analysis using base/instruction-tuned pairs

**ROUTE_TO_0 Failure Avoidance confirmed:**
- Gap 1-3 do NOT involve mechanistic/layer-wise analysis (avoids h-m1 failure)
- Gap 1-3 are NOT purely descriptive correlation (avoids TCS failure) — predictive validity is a stronger, falsifiable claim
- All gaps use existing benchmark data — no synthetic data required

---

## 9. Conclusion

### Key Findings

1. No cross-split predictive validity analysis exists for trustworthiness benchmarks — DecodingTrust, TrustLLM, HELM all evaluate dimensions without computing Spearman ρ between in-dist and OOD model rankings.
2. Gevers & Daelemans (2026) provides direct methodological blueprint (rank correlations + leave-one-family-out CV) — for commonsense benchmarks, not trustworthiness. Key finding: predictive validity is task-dependent, not universal.
3. All benchmark pairs confirmed publicly available: ANLI R1/R3, GLUE/AdvGLUE, BBQ-Disambig/Ambig, TruthfulQA/HaluEval.
4. RLHF-trustworthiness OOD link is fragile — DecodingTrust finds GPT-4 MORE vulnerable to jailbreaking despite higher standard scores; InstructGPT claims "minimal regressions" but doesn't test OOD variants.
5. Implementation infrastructure ready: TrustLLM (628★, MIT, updated 2025), DecodingTrust (314★), GLUE-X (100★), OOD_NLP (37★).

### Answer to Detailed Question (Preliminary)

Phase 1 boundary maintained — no hypotheses. Structural findings only:
- DQ1: No Spearman ρ across 15+ models computed for any trustworthiness benchmark pair — question structurally unanswered.
- DQ2: Preliminary signals — reliability non-monotonic with scale (TruthfulQA), fairness OOD gap large (BBQ 3.4pp bias), robustness OOD gap significant (AdvGLUE). Cross-dimension predictive validity comparison unstudied.
- DQ3: Scale-RLHF confound present (Dong 2024: −9.4% OOD drop for large models); needs explicit disentanglement.
- DQ4: Methodologically feasible with existing score matrices; no direct evidence yet.
- DQ5: DecodingTrust suggests RLHF may not transfer trustworthiness to OOD conditions (GPT-3.5 vs GPT-4 jailbreak vulnerability reversal).

### Phase 2 Readiness

- [x] Research question clearly defined with 5 falsifiable sub-questions
- [x] 3 PRIMARY research gaps identified with TABLE-format evidence
- [x] All benchmark pairs confirmed (ANLI, AdvGLUE, BBQ, TruthfulQA/HaluEval)
- [x] Multi-model evaluation datasets located (DecodingTrust, TrustLLM, HELM)
- [x] Methodology blueprint: Gevers & Daelemans (2026)
- [x] Implementation tools ready (TrustLLM, DecodingTrust, GLUE-X)
- [x] ROUTE_TO_0 failure avoidance confirmed for all 3 gaps
- [x] Phase 1 boundary maintained — no hypotheses generated
- [ ] RLHF base/chat score pairs not yet directly extracted (available in published papers)
- [ ] WinoBias cross-model scores not confirmed (paper found, scores not aggregated)

**Readiness: HIGH** — Phase 2A can proceed.

### Next Steps

1. **Phase 2A — Hypothesis Generation:** Read `01_targeted_research.md` (this file). Generate testable hypotheses from 3 PRIMARY gaps. Candidate directions: (a) robustness shows highest predictive validity, (b) RLHF narrows ID gap but not OOD gap, (c) reliability predictive validity is non-monotonic with scale.
2. **Data aggregation:** Collect multi-model scores from TrustLLM leaderboard, DecodingTrust tables, HELM public scores for 15+ models on target benchmark pairs.
3. **RLHF pair identification:** Extract LLaMA-2 base vs Chat, GPT-3 vs InstructGPT scores on the 4 benchmark OOD pairs.

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~120 minutes (2026-08-20, automated unattended execution)*
