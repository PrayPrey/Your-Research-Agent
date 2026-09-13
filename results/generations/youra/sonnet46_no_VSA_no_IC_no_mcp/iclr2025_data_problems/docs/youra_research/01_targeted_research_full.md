# Targeted Research Report: Do existing data curation pipeline choices produce systematically different downstream task performance profiles across pretrained model families?

**Date:** 2026-08-25
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

This Phase 1 targeted research report addresses the question of whether existing data curation pipeline choices produce systematically different downstream benchmark performance across pretrained model families, and whether data attribution methods can identify which curation decisions drive those differences.

**Context:** The ICLR 2025 DATA-FM Workshop motivates this research; the Pythia and OLMo open model families provide natural experimental platforms because they document their training data composition and release intermediate checkpoints.

**Data Collection:** All three MCP servers (Archon, Semantic Scholar, Exa) were unavailable in this no_MCP session. All 24 sources are [INFERRED] from general knowledge and must be independently verified before Phase 2A use.

**Key Finding:** Three primary research gaps were identified. Gap 1 (controlled curation comparison) and Gap 2 (scalable attribution) together address the full research question. Gap 3 (contamination quantification) is a necessary validity check. All three gaps are addressable using existing open infrastructure (Pythia checkpoints, OLMo weights, lm-evaluation-harness, TRAK) without new training runs — consistent with the feasibility constraints from Phase 0.

**Phase 2A Readiness:** Research gaps are clearly defined with supporting evidence and traceability to sub-questions. Ready for hypothesis generation.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Do existing data curation pipeline choices (quality filtering thresholds, deduplication aggressiveness, domain mixing ratios) produce systematically different downstream task performance profiles across existing pretrained model families, as measured on established benchmarks — and can data attribution methods identify which curation decisions drive performance gaps?

### Detailed Research Questions
1. Do different data filtering strategies (quality filters, deduplication, domain mixing ratios) produce measurably different downstream task performance on existing benchmarks (MMLU, HellaSwag, ARC, WinoGrande)?
2. Can data attribution methods (influence functions, TracIn, gradient similarity) reliably identify which training data subsets drive performance differences on specific benchmark categories, using existing open pretrained models?
3. Does test data contamination in existing benchmark datasets systematically inflate reported scores, and can contamination magnitude be estimated using existing n-gram overlap and embedding similarity detection methods?
4. How do data curation decisions interact with model scale — do curation choices that optimize small-model performance transfer to larger models, measurable across existing model families (e.g., Pythia, OLMo)?
5. Can model collapse signatures (reduced output diversity, increased repetition, perplexity degradation) be detected in publicly released models trained on increasingly synthetic-data-heavy corpora using existing metrics?

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
1. "Pythia model suite data curation impact downstream performance"
2. "OLMo training data composition benchmark evaluation"
3. "data attribution influence functions pretrained language models"
4. "test data contamination detection n-gram overlap benchmark inflation"
5. "model collapse synthetic data diversity perplexity metrics"

### Priority 3: Direct Question Decomposition Queries
1. "data quality filtering thresholds foundation model pretraining benchmark performance"
2. "deduplication aggressiveness training data downstream NLP task performance"
3. "domain mixing ratios pretraining data language model evaluation MMLU HellaSwag"
4. "TracIn gradient similarity data attribution large language models"
5. "test contamination detection embedding similarity benchmark leaderboard score inflation"
6. "data curation decisions model scale interaction Pythia OLMo performance transfer"
7. "RedPajama data filtering ablation study benchmark results"
8. "perplexity diversity repetition metrics model collapse detection open models synthetic"

---

## 3. Past Cases & Best Practices (via Archon)

### Direct Implementations

**MCP Server Status:** Archon MCP unavailable (no_MCP session)
**Total Queries:** 0 executed (MCP offline)
**Results Found:** 0 verified cases + 5 inferred patterns

**[INFERRED]** Pattern 1: Data Quality Filtering Pipeline
- Source: General knowledge (Archon unavailable)
- Reasoning: Standard practice in large-scale pretraining pipelines (C4, RefinedWeb, Dolma) involves heuristic quality filters (language ID, perplexity scoring, deduplication) that are known to affect downstream performance, documented in public technical reports.
- Note: Not verified through Archon KB

**[INFERRED]** Pattern 2: Deduplication Strategy Comparison
- Source: General knowledge (Archon unavailable)
- Reasoning: MinHash LSH vs exact substring deduplication produce measurably different data compositions. Pythia suite trained on deduplicated Pile variant provides a natural controlled comparison.
- Note: Not verified through Archon KB

**[INFERRED]** Pattern 3: Influence Function for Data Attribution
- Source: General knowledge (Archon unavailable)
- Reasoning: Koh & Liang (2017) influence functions extended to LLMs via TRAK (Park et al. 2023) enable tracing benchmark performance to training data subsets; computationally expensive but feasible on smaller models.
- Note: Not verified through Archon KB

### Similar Architectural Patterns

**[INFERRED]** Pattern 4: Cross-checkpoint Performance Comparison
- Source: General knowledge (Archon unavailable)
- Reasoning: Pythia releases intermediate checkpoints enabling training-time performance curves; OLMo releases data mixing logs. Together they allow curation-controlled analysis without new training runs.
- Note: Not verified through Archon KB

### Code Examples Found

**[INFERRED]** Pattern 5: N-gram Contamination Detection
- Source: General knowledge (Archon unavailable)
- Reasoning: GPT-4 technical report and LLM-as-judge contamination studies use 13-gram overlap detection between training and evaluation sets; implementation is straightforward with standard tokenizers.
- Note: Not verified through Archon KB

---

## 4. Academic Literature Review (via Semantic Scholar)

### Directly Relevant Papers

**MCP Server Status:** Semantic Scholar MCP unavailable (no_MCP session)
**Total Queries:** 0 executed (MCP offline)
**Results Found:** 0 verified + 12 inferred from general knowledge

**[INFERRED]** 1. "Scaling Data-Constrained Language Models" (2023)
- Authors: Muennighoff et al.
- Relevance: Directly studies data repetition and curation effects on LM performance across scales
- Key Contribution: Shows diminishing returns from data repetition; computes/tokens tradeoff under data constraints
- arXiv ID: 2305.16264 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 2. "Dolma: an Open Corpus of Three Trillion Tokens for Language Model Pretraining Research" (2024)
- Authors: Soldaini et al. (AI2)
- Relevance: Documents data curation pipeline choices (quality filters, deduplication) and their rationale for OLMo
- Key Contribution: Provides reproducible curation pipeline with ablation documentation
- arXiv ID: 2402.00159 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 3. "The Pile: An 800GB Dataset of Diverse Text for Language Modeling" (2020)
- Authors: Gao et al. (EleutherAI)
- Relevance: Training data for Pythia suite; documents domain mixing choices
- Key Contribution: Establishes domain-diverse pretraining corpus; Pythia uses this for curation comparison
- arXiv ID: 2101.00027 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 4. "Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling" (2023)
- Authors: Biderman et al. (EleutherAI)
- Relevance: Primary experimental platform — releases checkpoints trained on Pile with documented curation
- Key Contribution: Enables curation-controlled analysis via intermediate checkpoints
- arXiv ID: 2304.01373 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 5. "OLMo: Accelerating the Science of Language Models" (2024)
- Authors: Groeneveld et al. (AI2)
- Relevance: Second primary experimental platform; documents data mixing ratios and filtering decisions
- Key Contribution: Fully open model with training data, code, and checkpoints released
- arXiv ID: 2402.00838 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 6. "TRAK: Attributing Model Behavior at Scale" (2023)
- Authors: Park et al. (MIT)
- Relevance: Scalable data attribution method applicable to LLMs; key tool for Q2 (attribution sub-question)
- Key Contribution: Random projection approximation of influence functions; 100x faster than exact methods
- arXiv ID: 2303.14186 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 7. "Detecting Pretraining Data from Large Language Models" (2023)
- Authors: Shi et al.
- Relevance: Contamination detection methodology; min-k% prob method for membership inference
- Key Contribution: Membership inference attack without model retraining; applicable to contamination Q3
- arXiv ID: 2310.16789 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 8. "Model Collapse Demystified: The Case of Regression" (2024)
- Authors: Shumailov et al.
- Relevance: Formalizes model collapse signatures (Q5); analyzes perplexity and diversity degradation
- Key Contribution: Theoretical and empirical characterization of collapse in models trained on generated data
- arXiv ID: 2402.07712 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 9. "Data Selection for Language Models via Importance Resampling" (2023)
- Authors: Xie et al. (Stanford)
- Relevance: Quality filtering strategy via DSIR; directly addresses Q1 (filtering strategy impact)
- Key Contribution: Learns data selection weights to match target distribution; outperforms heuristic filters
- arXiv ID: 2302.03169 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 10. "QuRating: Selecting High-Quality Data for Training Language Models" (2024)
- Authors: Wettig et al. (Princeton)
- Relevance: Supervised quality rating approach; ablations on downstream benchmark impact
- Key Contribution: LLM-judged quality scores outperform perplexity-based filters on benchmarks
- arXiv ID: 2402.09739 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

### Foundational Papers

**[INFERRED]** 1. "Understanding Black-box Predictions via Influence Functions" (2017)
- Authors: Koh & Liang (Stanford)
- Relevance: Foundational method for data attribution (Q2); basis for TracIn and TRAK
- Key Contribution: Applies second-order approximation to trace model predictions to training examples
- Citations: ~2000 (estimated)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 2. "Deduplicating Training Data Makes Language Models Better" (2022)
- Authors: Lee et al. (Google)
- Relevance: Directly studies deduplication aggressiveness impact on LM performance (Q1)
- Key Contribution: Shows exact and near-dedup reduce memorization and improve benchmark scores
- arXiv ID: 2107.06499 (unverified — from memory)
- Note: Not verified via Semantic Scholar MCP

**[INFERRED]** 3. "C4: Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (2020)
- Authors: Raffel et al. (Google)
- Relevance: Foundational data filtering pipeline (C4 from Common Crawl); quality heuristics benchmark
- Key Contribution: Establishes C4 quality filters as baseline for text curation pipelines
- Note: Not verified via Semantic Scholar MCP

### Citation Network Analysis

**MCP Status:** Citation network analysis not performed (Semantic Scholar MCP unavailable).

**Known research lineage (inferred):**
- Influence functions (Koh & Liang 2017) → TracIn (Pruthi et al. 2020) → TRAK (Park et al. 2023): Data attribution for neural networks
- C4 curation (Raffel 2020) → Pile (Gao 2020) → Dolma (Soldaini 2024): Pretraining corpus curation evolution
- Deduplication study (Lee 2022) → RefinedWeb (Penedo 2023) → DCLM (Li 2024): Deduplication best practices
- Pythia (Biderman 2023) + OLMo (Groeneveld 2024): Open model suites enabling curation-controlled analysis

**Note:** All citation counts and arXiv IDs are from memory and must be verified before use in Phase 2A.

---

## 5. Implementation Resources (via Exa)

### Directly Relevant Implementations

**MCP Server Status:** Exa MCP unavailable (no_MCP session)
**Total Queries:** 0 executed (MCP offline)
**Results Found:** 0 verified + 6 inferred from known repositories

**[INFERRED]** 1. EleutherAI/lm-evaluation-harness
- URL: https://github.com/EleutherAI/lm-evaluation-harness (unverified — from memory)
- Language: Python
- Relevance: Standard benchmark evaluation framework for MMLU, HellaSwag, ARC, WinoGrande — required for Q1 downstream performance measurement
- Key Features: Unified interface for 200+ benchmarks; supports Pythia and OLMo models directly
- Note: Not verified via Exa MCP

**[INFERRED]** 2. allenai/OLMo
- URL: https://github.com/allenai/OLMo (unverified — from memory)
- Language: Python
- Relevance: OLMo training codebase with documented data mixing; enables curation-controlled experiments (Q1, Q4)
- Key Features: Full training pipeline + data documentation + Dolma dataset integration
- Note: Not verified via Exa MCP

**[INFERRED]** 3. EleutherAI/pythia
- URL: https://github.com/EleutherAI/pythia (unverified — from memory)
- Language: Python
- Relevance: Pythia model suite with intermediate checkpoints; primary platform for scale interaction study (Q4)
- Key Features: 70M–12B models, 154 checkpoints per model, trained on deduplicated Pile
- Note: Not verified via Exa MCP

**[INFERRED]** 4. MadryLab/trak
- URL: https://github.com/MadryLab/trak (unverified — from memory)
- Language: Python (PyTorch)
- Relevance: TRAK data attribution library; scalable influence function approximation for Q2
- Key Features: GPU-efficient random projection; tested on CIFAR and language models
- Note: Not verified via Exa MCP

### Component Implementations

**[INFERRED]** 5. google-research/deduplicate-text-datasets
- URL: https://github.com/google-research/deduplicate-text-datasets (unverified — from memory)
- Language: Python/Rust
- Relevance: Lee et al. 2022 deduplication implementation; enables aggressiveness comparison (Q1)
- Key Features: Suffix array exact dedup + MinHash near-dedup; applied to C4 and Pile variants
- Note: Not verified via Exa MCP

**[INFERRED]** 6. stanford-crfm/DSIR
- URL: https://github.com/p-lambda/dsir (unverified — from memory)
- Language: Python
- Relevance: Data Selection via Importance Resampling (Xie et al. 2023); quality filtering baseline for Q1
- Key Features: Learns selection weights to match target domain; benchmark comparison vs heuristics
- Note: Not verified via Exa MCP

### Tutorial Resources

**[INFERRED]** Papers with Code — Data Augmentation / Pretraining Data pages:
- URL: https://paperswithcode.com/task/language-modelling (unverified — from memory)
- Relevance: Aggregates benchmark leaderboards with model + data provenance; useful for contamination context (Q3)
- Note: Not verified via Exa MCP

### Code Analysis

**[INFERRED]** Common implementation patterns for data curation research:
- Evaluation: lm-evaluation-harness as universal harness; zero-shot and few-shot settings both standard
- Attribution: TRAK preferred over exact influence functions for models >1B parameters
- Deduplication: MinHash LSH (datasketch library) for near-dedup; suffix array for exact substring dedup
- Contamination detection: n-gram overlap scripts typically custom; min-k% prob method needs model logprobs
- Framework preference: PyTorch dominant; JAX used in some EleutherAI work
- Note: All patterns inferred from general knowledge; not verified via Exa code context search

**[LIMITED_RESULTS - EXA]** 0 verified resources found
- Fallback: GitHub search "data curation language model benchmark"
- Fallback: Papers with Code — Pretraining Data section
- Fallback: awesome-llm-data lists on GitHub

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

**Data curation pipeline research lineage:**

1. **Foundation — Corpus Design (2020):** Raffel et al. (C4) + Gao et al. (Pile) establish that data quality heuristics (language filtering, deduplication, content filtering) are necessary but their comparative impact on downstream tasks is poorly characterized.

2. **Deduplication Study (2022):** Lee et al. demonstrate that exact and near-deduplication of training corpora measurably reduces memorization and improves generalization on benchmarks — first systematic ablation of a single curation choice.

3. **Open Model Suites (2023–2024):** Biderman et al. (Pythia) and Groeneveld et al. (OLMo/Dolma) release model families with documented curation choices and intermediate checkpoints, enabling retrospective curation analysis without new training runs.

4. **Data Selection Methods (2023):** Xie et al. (DSIR) and Wettig et al. (QuRating) demonstrate that learned data selection outperforms heuristic quality filters — but comparative evaluations across model families are missing.

5. **Data Attribution Scaling (2023):** Park et al. (TRAK) make influence function attribution tractable at LLM scale, enabling Q2 (attribution sub-question) to be addressed on existing models.

6. **Contamination Awareness (2023):** Shi et al. (min-k% prob) and related works show that benchmark contamination is systematically underestimated — motivating Q3.

7. **Research Question (2026):** Synthesizes these threads: Can curation pipeline differences across Pythia/OLMo be measured on standard benchmarks, and can attribution methods identify which curation choices drive the gaps?

### Concept Integration Map

```
DATA CURATION CHOICES
(filtering thresholds, dedup aggressiveness, domain mixing)
         |
         v
PRETRAINED MODEL FAMILIES
Pythia (Pile/dedup-Pile) ←——→ OLMo (Dolma)
         |
         v
DOWNSTREAM BENCHMARK PERFORMANCE
(MMLU, HellaSwag, ARC, WinoGrande)
         |
    [Q1: Are differences measurable?]
         |
         v
ATTRIBUTION ANALYSIS
(TRAK / influence functions)
         |
    [Q2: Which data subsets drive gaps?]
         |
CONTAMINATION CHECK ——[Q3]——→ Adjusted performance estimates
         |
SCALE INTERACTION ————[Q4]——→ Do curation choices transfer across model sizes?
         |
MODEL COLLAPSE ——————[Q5]——→ Synthetic data detection in released models
```

Supporting evidence flows:
- Pythia checkpoints + lm-evaluation-harness → Q1 measurement
- TRAK + open model weights → Q2 attribution
- n-gram overlap + min-k% prob → Q3 contamination
- Pythia 70M–12B scale range → Q4 scale interaction
- Perplexity + diversity metrics + synthetic model release info → Q5 collapse

### Cross-Reference Matrix

| Source | Relevance to Research Question | Implementation Available | Adaptability | Addresses Sub-Q |
|--------|-------------------------------|--------------------------|--------------|-----------------|
| Pythia suite (Biderman 2023) [INFERRED] | High — controlled curation comparison platform | Yes (open weights + checkpoints) | High | Q1, Q4 |
| OLMo/Dolma (Groeneveld 2024) [INFERRED] | High — documented data mixing ratios | Yes (open weights + data) | High | Q1, Q4 |
| lm-evaluation-harness (EleutherAI) [INFERRED] | High — standard benchmark evaluation | Yes (GitHub) | High | Q1, Q4 |
| DSIR (Xie 2023) [INFERRED] | Medium — quality filtering baseline | Yes (GitHub) | Medium | Q1 |
| QuRating (Wettig 2024) [INFERRED] | Medium — learned quality filtering | Partial | Medium | Q1 |
| TRAK (Park 2023) [INFERRED] | High — scalable data attribution | Yes (GitHub) | High | Q2 |
| Lee et al. 2022 dedup [INFERRED] | High — deduplication impact study | Yes (GitHub) | Medium | Q1 |
| Shi et al. 2023 (min-k% prob) [INFERRED] | High — contamination detection | Partial | High | Q3 |
| Shumailov et al. 2024 (collapse) [INFERRED] | Medium — model collapse characterization | Partial | Medium | Q5 |
| Scaling data-constrained (Muennighoff 2023) [INFERRED] | Medium — data repetition effects | No | Low | Q1 |

**Architectural insights from cross-reference analysis:**
- Pythia + OLMo together cover the most important curation variables (dedup aggressiveness and domain mixing) with documented differences — natural comparison pair
- lm-evaluation-harness is the only implementation needed to close the evaluation loop; no new benchmark infrastructure required
- TRAK is the critical dependency for Q2; without it, Q2 requires approximate methods (gradient similarity via cosine distance)
- Q3 (contamination) and Q5 (collapse) are more self-contained and could serve as independent hypotheses if Q1+Q2 scope is too broad

---

## 7. Verification Status Summary

### Statistics

| Category | Count | Verification Status |
|----------|-------|---------------------|
| Reference papers analyzed | 0 | N/A (none provided) |
| Archon KB results | 5 | [INFERRED] — MCP offline |
| Semantic Scholar papers | 12 | [INFERRED] — MCP offline |
| Exa repositories/resources | 7 | [INFERRED] — MCP offline |
| **Total sources** | **24** | |
| [VERIFIED - ARCHON] | 0 | 0% |
| [VERIFIED - SCHOLAR] | 0 | 0% |
| [VERIFIED - EXA] | 0 | 0% |
| [INFERRED] | 24 | 100% |
| [NOT_FOUND] | 0 | 0% |

**Summary:** All 24 sources are [INFERRED] due to MCP unavailability in this no_MCP session. Data quality is limited by lack of live verification. All arXiv IDs, citation counts, and GitHub URLs must be independently verified before use in Phase 2A.

### MCP Server Performance

| MCP Server | Queries Executed | Status | Reason |
|------------|-----------------|--------|--------|
| Archon KB | 0 | OFFLINE | no_MCP session configuration |
| Semantic Scholar | 0 | OFFLINE | no_MCP session configuration |
| Exa Search | 0 | OFFLINE | no_MCP session configuration |

All three required MCP servers were unavailable. This is expected behavior for `no_MCP` test sessions. In production sessions, all three servers are mandatory (per `mcp_servers.required` in workflow.yaml).

### Data Quality Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Completeness | 55/100 | All sections filled; content is inferred not verified |
| Reliability | 30/100 | [INFERRED] sources from memory; arXiv IDs unconfirmed |
| Recency | 70/100 | Sources span 2017–2024; recent (2023–2024) work well represented |
| Relevance to Question | 85/100 | Sources are directly matched to research sub-questions |
| **Overall** | **60/100** | Adequate for gap identification; verification required before Phase 2A |

**Recommendation:** In Phase 2A, independently verify all 12 papers via arXiv or Semantic Scholar before downloading. All GitHub URLs should be confirmed before cloning.

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchor):**

1. **Main Research Question:** Do existing data curation pipeline choices (quality filtering thresholds, deduplication aggressiveness, domain mixing ratios) produce systematically different downstream task performance profiles across existing pretrained model families, as measured on established benchmarks — and can data attribution methods identify which curation decisions drive performance gaps?

2. **Detailed Questions:**
   - Q1: Do different filtering strategies produce measurably different downstream performance on MMLU, HellaSwag, ARC, WinoGrande?
   - Q2: Can attribution methods (influence functions, TracIn, gradient similarity) identify which training data subsets drive performance differences?
   - Q3: Does test data contamination systematically inflate benchmark scores, and can it be estimated using existing methods?
   - Q4: How do curation decisions interact with model scale across Pythia/OLMo families?
   - Q5: Can model collapse signatures be detected in publicly released models using existing metrics?

3. **Reference Papers:** Not provided

### Identified Gaps

#### Gap 1: Lack of Controlled Cross-Family Curation Comparison on Standard Benchmarks

**Relevance Classification:** PRIMARY — directly blocks answering the main research question

**Connection:** ☑️ Blocks answering research question: Without a systematic comparison of Pythia (Pile/dedup-Pile) vs OLMo (Dolma) performance on identical benchmarks controlling for model size, the main question cannot be answered. ☑️ Addresses Q1 and Q4 from detailed questions.

**Current State:** Individual papers (Biderman 2023, Groeneveld 2024) document their own models' performance on standard benchmarks, but no study performs a controlled comparison attributing performance differences to curation choices rather than architecture, training compute, or model scale. DSIR and QuRating ablate filtering within a single training run but do not compare across open model families.

**Missing Piece:** A unified evaluation using lm-evaluation-harness on Pythia checkpoints (trained on Pile vs deduplicated Pile) and OLMo (trained on Dolma with documented mixing ratios), with performance differences attributed to documented curation choices rather than confounded by architecture differences.

**Potential Impact:** High — directly enables the main research question; the Pythia and OLMo infrastructure already exists, making this gap closeable without new training runs.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling" | 2023 | Biderman et al. | UNVERIFIED | 2304.01373* | ~500* | Releases checkpoints enabling curation-controlled analysis; documents Pile curation choices |
| "OLMo: Accelerating the Science of Language Models" | 2024 | Groeneveld et al. | UNVERIFIED | 2402.00838* | ~300* | Documents Dolma mixing ratios; benchmark results available but curation comparison not performed |
| "Dolma: an Open Corpus of Three Trillion Tokens" | 2024 | Soldaini et al. | UNVERIFIED | 2402.00159* | ~200* | Documents filtering pipeline choices that distinguish OLMo training data from Pile |
| "Deduplicating Training Data Makes Language Models Better" | 2022 | Lee et al. | UNVERIFIED | 2107.06499* | ~400* | Shows deduplication impacts downstream tasks; Pythia's dedup-Pile provides natural comparison |
| "Data Selection for Language Models via Importance Resampling" | 2023 | Xie et al. | UNVERIFIED | 2302.03169* | ~200* | DSIR quality filtering ablation; baseline for filtering strategy comparison |

*arXiv IDs and citation counts from memory — must verify before Phase 2A use

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No verified Archon cases | N/A (MCP offline) | N/A | N/A |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness* | ~7000* | Python | Unified MMLU/HellaSwag/ARC/WinoGrande evaluation; Pythia+OLMo compatible |
| allenai/OLMo | https://github.com/allenai/OLMo* | ~4000* | Python | Full training pipeline + Dolma data documentation |
| EleutherAI/pythia | https://github.com/EleutherAI/pythia* | ~2000* | Python | Checkpoint releases for curation comparison |

*URLs and star counts from memory — must verify

---

#### Gap 2: No Scalable Data Attribution Study on LLM Benchmark Performance

**Relevance Classification:** PRIMARY — directly blocks answering attribution sub-question (Q2)

**Connection:** ☑️ Blocks answering research question: The main question explicitly asks whether "data attribution methods identify which curation decisions drive performance gaps." Without an attribution study on these specific models, the second half of the research question is unanswered. ☑️ Directly addresses Q2 from detailed questions.

**Current State:** TRAK (Park et al. 2023) demonstrates scalable influence function approximation for neural networks and validates on vision models and small language models. TracIn (Pruthi et al. 2020) and gradient similarity methods exist but have not been systematically applied to trace benchmark-level performance differences back to specific training data subsets across model families. Most attribution work in LLMs focuses on memorization or factual knowledge, not benchmark task performance.

**Missing Piece:** Application of TRAK or gradient-similarity attribution to Pythia/OLMo models to identify which subsets of the Pile/Dolma training data are most influential for specific benchmark category performance (e.g., MMLU STEM questions vs. commonsense reasoning tasks). This would require: (1) TRAK implementation on decoder-only LLMs at 1B–7B scale, (2) benchmark-task-specific query gradients, (3) training data subset selection and attribution scoring.

**Potential Impact:** High — identifies mechanistic link between curation choices and downstream performance; novel contribution in LLM data attribution literature.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "TRAK: Attributing Model Behavior at Scale" | 2023 | Park et al. | UNVERIFIED | 2303.14186* | ~150* | Scalable attribution via random projections; tested on language models at small scale |
| "Understanding Black-box Predictions via Influence Functions" | 2017 | Koh & Liang | UNVERIFIED | 1703.04730* | ~2000* | Foundational method; computationally intractable at LLM scale without approximation |
| "Revisiting the Role of Language Priors in Visual Question Answering" | 2020 | Pruthi et al. (TracIn) | UNVERIFIED | UNVERIFIED | ~300* | TracIn: influence via training trajectory checkpoints; more tractable than Hessian-based methods |

*All identifiers from memory — must verify

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No verified Archon cases | N/A (MCP offline) | N/A | N/A |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| MadryLab/trak | https://github.com/MadryLab/trak* | ~800* | Python (PyTorch) | Random projection attribution; GPU-efficient; tested on language models |

*From memory — must verify

---

#### Gap 3: Unquantified Benchmark Contamination Across Open Model Families

**Relevance Classification:** SECONDARY — addresses Q3 (contamination sub-question) which is a prerequisite for interpreting performance differences in Gap 1

**Connection:** ☑️ Relates to detailed question Q3. ☑️ Also relates to research question: benchmark performance comparisons between Pythia and OLMo are uninterpretable if contamination rates differ systematically between the Pile and Dolma training corpora, confounding Gap 1's analysis.

**Current State:** Shi et al. (2023) min-k% prob method and n-gram overlap approaches exist for contamination detection. The GPT-4 technical report reports contamination estimates for its training data. However, no study has systematically estimated contamination rates specifically for Pile vs Dolma for the four target benchmarks (MMLU, HellaSwag, ARC, WinoGrande), and whether contamination rate differences between the two corpora are significant enough to confound curation comparison studies.

**Missing Piece:** Contamination estimation for MMLU, HellaSwag, ARC, and WinoGrande test sets against the Pile and Dolma training corpora using n-gram overlap and min-k% prob methods, with statistical comparison of contamination rates between the two corpora to determine whether contamination is a confound for Gap 1's curation comparison.

**Potential Impact:** Medium — necessary for result validity of Gap 1 analysis; may be a shorter companion contribution if contamination rates are similar (null result strengthens Gap 1's conclusions).

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Detecting Pretraining Data from Large Language Models" | 2023 | Shi et al. | UNVERIFIED | 2310.16789* | ~200* | Min-k% prob method for contamination detection without model retraining; applicable to Pythia/OLMo |
| "Data Contamination Quiz: A Tool to Detect and Estimate Contamination in Large Language Models" | 2023 | Golchin & Surdeanu | UNVERIFIED | 2311.06233* | ~100* | Alternative contamination detection approach; LLM-based quiz methodology |
| "Don't Make Your LLM an Evaluation Cheater" | 2023 | Zhou et al. | UNVERIFIED | UNVERIFIED | ~50* | Documents benchmark contamination effects on leaderboard inflation |

*All identifiers from memory — must verify

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No verified Archon cases | N/A (MCP offline) | N/A | N/A |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| google-research/deduplicate-text-datasets | https://github.com/google-research/deduplicate-text-datasets* | ~800* | Python/Rust | Suffix array implementation; adaptable for n-gram overlap contamination check |

*From memory — must verify

---

### Gap Priority Matrix

| Gap ID | Title | Relevance | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|-----------|--------|------------|----------------|----------|
| Gap 1 | Controlled Cross-Family Curation Comparison | PRIMARY | High | Medium (no new training) | 5 papers, 3 repos | Critical |
| Gap 2 | Scalable Data Attribution on LLM Benchmarks | PRIMARY | High | Medium-High (TRAK at LLM scale) | 3 papers, 1 repo | High |
| Gap 3 | Benchmark Contamination in Pile vs Dolma | SECONDARY | Medium | Low-Medium (existing methods) | 3 papers, 1 repo | Medium |

### User Input to Gap Traceability

**Main Research Question** directly addressed by:
- Gap 1: Provides the measurement framework for "systematically different downstream task performance profiles"
- Gap 2: Provides the attribution mechanism for "identify which curation decisions drive performance gaps"

**Detailed Questions** addressed by:
- Q1 (filtering strategies → benchmark performance): Gap 1
- Q2 (attribution methods → training data subsets): Gap 2
- Q3 (contamination detection): Gap 3
- Q4 (scale interaction): Gap 1 (Pythia's 70M–12B scale range enables this within the same infrastructure)
- Q5 (model collapse detection): Not addressed by identified gaps — represents an optional fourth gap if research scope is expanded

**Reference Papers:** Not provided — no reference paper extensions applicable.

---

## 9. Conclusion

### Key Findings

1. **Pythia + OLMo are the right experimental platforms:** Both families document curation choices (Pile/dedup-Pile for Pythia; Dolma for OLMo) and release checkpoints, enabling curation-controlled comparison without new training runs. lm-evaluation-harness supports both families directly.

2. **Gap 1 (curation comparison) is the central gap:** No existing study performs a controlled cross-family benchmark comparison attributing performance differences to documented curation choices rather than architecture or compute confounds.

3. **Gap 2 (attribution) requires TRAK:** Influence function attribution at LLM scale is now tractable via TRAK (Park et al. 2023). Application to Pythia/OLMo for benchmark-task-specific attribution has not been done.

4. **Gap 3 (contamination) is a confound check:** Pile and Dolma were built at different times with different filtering; contamination rate differences for MMLU/HellaSwag/ARC/WinoGrande could confound Gap 1's analysis. min-k% prob method (Shi et al. 2023) can address this without new tools.

5. **Q5 (model collapse) is out of scope for primary hypothesis:** No strong evidence connects publicly released models to quantified synthetic data ratios that would enable collapse detection. Best treated as an optional extension.

6. **MCP unavailability is a data quality limitation:** All 24 sources are [INFERRED]. arXiv IDs and GitHub URLs must be verified before Phase 2A paper downloads. The research landscape assessment is likely directionally correct but should be treated as prior knowledge, not verified evidence.

### Answer to Detailed Question (Preliminary)

**Q1 (filtering → benchmarks):** Evidence strongly suggests yes — deduplication and domain mixing affect benchmark performance based on individual model reports, but a controlled cross-family comparison is missing.

**Q2 (attribution methods):** TRAK makes this tractable at Pythia/OLMo scale; no prior study has applied it to trace benchmark category performance to training data subsets in open LLMs.

**Q3 (contamination):** Contamination likely exists in both Pile and Dolma for standard benchmarks, but relative magnitudes between the two are unknown. This must be quantified before interpreting Gap 1 results.

**Q4 (scale interaction):** Pythia's 70M–12B range provides direct evidence within the same training data family; OLMo's single-scale release limits cross-family scale comparison.

**Q5 (model collapse):** Insufficient publicly available data on synthetic data fractions in released models; not addressed by identified gaps.

### Phase 2 Readiness

- [x] Research question clearly defined
- [x] 3 research gaps identified with PRIMARY/SECONDARY classification
- [x] Gap evidence in table format for Phase 2A extraction
- [x] User input → gap traceability documented
- [x] Experimental platform identified (Pythia + OLMo + lm-evaluation-harness + TRAK)
- [x] Feasibility confirmed: no new training runs, no new benchmarks required
- [ ] MCP-verified paper list pending (all sources currently [INFERRED])
- [ ] Contamination tool selection pending (n-gram vs min-k% prob vs both)

**Readiness level:** ADEQUATE — sufficient for Phase 2A hypothesis generation; paper verification should occur in Phase 2A before downloading papers.

### Next Steps

1. Proceed to Phase 2A: `/phase2a-dialogue` — Hypothesis generation from Gap 1 (curation comparison) as primary hypothesis, with Gap 2 (attribution) as secondary hypothesis
2. In Phase 2A: Verify arXiv IDs for all 12 inferred papers via Semantic Scholar MCP before downloading
3. In Phase 2A: Consider whether to address Q5 (model collapse) as a third independent hypothesis or exclude from scope

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~45 minutes (unattended, no_MCP session)*
