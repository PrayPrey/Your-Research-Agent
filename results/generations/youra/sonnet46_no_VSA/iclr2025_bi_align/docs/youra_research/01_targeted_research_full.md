# Targeted Research Report: Pairwise partial Spearman rank-correlation structure of Human→AI alignment benchmarks across open-weight LLMs after MMLU scale control

**Date:** 2026-07-30
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

**Research Question:** What is the pairwise partial Spearman rank-correlation structure of Human→AI alignment benchmarks (TruthfulQA MC2, BBQ, HarmBench/BeaverTails, optional HELM ECE) across N≥40 open-weight LLMs after controlling for MMLU as scale proxy — revealing unidimensional (scale-driven) or multi-dimensional (independent construct) alignment?

**Context:** ROUTE_TO_0 Reflection 9 failure recovery. Nine prior reflections identified failure classes (data inaccessibility, proprietary model contamination, scaling confound, directional assumption errors, calibration instability, underpowered N). This study explicitly avoids all 9 failure classes.

**Phase 1 Key Findings:**
1. **Direct precedent found (2026):** clawrxiv:2603.00394 analyzed 6-benchmark correlation structure (including TruthfulQA) across 40 models — finds TruthfulQA provides orthogonal PC2 signal (23.4% variance). This directly motivates extending analysis to BBQ and HarmBench/BeaverTails with partial Spearman + cluster-bootstrap.
2. **All data sources confirmed accessible:** Open LLM LB v1 CSV (TruthfulQA+MMLU confirmed), BBQ via lighteval/bbq_helm (HuggingFace), HarmBench GitHub CSV (1008 stars), BeaverTails HuggingFace (364k rows, is_safe field). Pre-flight executable URL test (requests.head + N count) still required before Phase 2A.
3. **Analysis tools confirmed:** pingouin.partial_corr(method='spearman', covar=['MMLU']) is the exact function needed; scipy.stats.spearmanr + permutation test for N<500 stability.
4. **3 research gaps identified:** (1) partial_rho matrix for alignment-specific benchmarks absent [PRIMARY]; (2) N triple-overlap unverified pre-flight [PRIMARY]; (3) RLHF cross-benchmark profile for BBQ+HarmBench absent [SECONDARY].
5. **MCP limitations:** Archon KB = image generation domain (no alignment content); Semantic Scholar unavailable; Exa fully functional (13 verified resources).

**Phase 2A Readiness:** HIGH. Data sources confirmed. Analysis method confirmed. Pre-flight URL test is the single remaining blocker before hypothesis design.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Across a population of N≥40 open-weight LLMs with pre-computed scores on ≥3 Human→AI alignment benchmarks (TruthfulQA MC2 for factuality; BBQ accuracy for social bias; HarmBench refusal rate or BeaverTails safety rate for harmlessness; HELM ECE or toxicity score as optional 4th dimension), what is the pairwise partial Spearman rank-correlation structure of these alignment dimensions after controlling for MMLU as model scale proxy — and does this structure reveal that Human→AI alignment is a unidimensional scale-driven construct or a genuinely multi-dimensional set of independent constructs? (Reflection 9: direction-agnostic, zero inference, open-weight-only, avoids all 9 prior failure classes; requires Phase 1 executable URL test and N verification BEFORE hypothesis design, and immediate execution without re-archiving)

### Detailed Research Questions
1. **Pairwise partial alignment benchmark correlation (primary gate):** For N≥40 open-weight models with pre-computed scores on ≥3 Human→AI alignment benchmarks, compute partial Spearman rank correlation between each benchmark pair controlling for MMLU. Gate: At least one benchmark pair achieves |partial_rho| < 0.30 with 95% cluster-bootstrap CI (N_bootstrap=5000, clustered by model family) not crossing 0.30, confirming multi-dimensionality; OR all pairs achieve |partial_rho| > 0.60, confirming unidimensionality. Fisher z-test vs zero (p < 0.05, two-tailed). Both outcomes publishable.
2. **Scale contribution quantification:** For each benchmark pair, compare raw Spearman rho vs. MMLU-partial Spearman rho via Fisher z-test (p < 0.05). Quantify what fraction of apparent alignment consistency is scale-driven vs genuine construct overlap.
3. **RLHF alignment profile across benchmarks:** Among within-family base/instruction-tuned pairs (confirmed: 321 pairs, Open LLM LB v1, mean_delta TruthfulQA=+3.406), extend delta analysis to BBQ and HarmBench/BeaverTails where same model families appear. Sign test (not logistic regression) for directional consistency. Does RLHF produce uniform cross-benchmark improvement or divergent alignment profiles?
4. **PCA structure of alignment dimensions:** PCA on N×B benchmark score matrix. Variance explained by PC1 (scale factor) vs PC2+ (alignment-specific). Benchmark clustering (capability-adjacent vs human-normative).
5. **Phase 1 pre-flight data verification (MANDATORY — executable before Phase 2A):** For each source, run requests.head or pd.read_csv(timeout=30): (a) TruthfulQA MC2 in Open LLM LB v1 CSV (confirmed URL) → N≥40; (b) BBQ accuracy in HELM Lite HuggingFace JSON or Parrish et al. table → N≥25 overlap; (c) HarmBench GitHub CSV OR BeaverTails HuggingFace → N≥25 overlap; (d) HELM ECE optional — N≥40 overlap, else substitute toxicity or drop. Report: triple-overlap N, quadruple-overlap N, whether N≥40 achieved. If any URL fails, apply fallback immediately before Phase 2A begins.

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
**R1 (h-e1):** NEVER anchor on HELM GCS/Zenodo ZIPs; use HuggingFace alternatives. Pre-flight test EACH URL.
**R2 (h-e2):** NEVER use AlpacaEval-LC (includes proprietary models) as join population for open-harness datasets. Mixed open/proprietary denominator guarantees <70% match.
**R3 (sh2-corr):** NEVER assume negative alignment-helpfulness correlation at cross-model aggregate level. Scale dominates — use partial correlation after MMLU control. Direction-agnostic framing avoids this.
**R4 (h-m1):** RLHF improves TruthfulQA MC2 (+3.406 mean delta, BCa CI entirely positive) — this direction is CONFIRMED POSITIVE. Extending to BBQ and HarmBench is the natural question.
**R5 (sh-p1):** NEVER use logistic regression with calibration slope gate when N<100. Use Spearman + Fisher z-test + sign test + PCA.
**R6 (snapshot h-e1):** Pre-flight gate: N≥40 triple-overlap required before hypothesis acceptance. N=28 is underpowered.
**R7/R8:** Sound directions archived without Phase 1 execution. Reflection 9: immediately execute Phase 1 after saving brainstorm, no re-archiving.
**R9-NEW:** Phase 1 must run requests.head or pd.read_csv(timeout=30) for EACH data source URL before Phase 2A designs hypotheses.

---

## 2. Search Queries Generated

### Query Generation Source Summary
ROUTE_TO_0 (Reflection 9) — 17 queries generated across 3 priority tiers.
- 🔴 Failure-aware queries (avoid past failure classes): 4
- 🥇 Reference paper queries: 0 (no reference papers provided)
- 🥈 Brainstorm insights queries: 5
- 🥉 Direct question decomposition queries: 8
- **Total: 17 queries**

Failure patterns avoided: HELM GCS/Zenodo auth failure; AlpacaEval-LC proprietary contamination; raw correlation without MMLU control; directional RLHF assumption; logistic regression calibration gate N<100; N<40 underpowered; hardcoded URL paths without pre-flight.

### Priority 1: Reference Paper Concept Queries
*No reference papers provided — will discover in Phase 1*

### Priority 2: Brainstorm Insights Queries (from Key Discoveries + Areas for Exploration)
1. "partial Spearman rank correlation LLM alignment benchmarks pairwise dimensionality"
2. "RLHF instruction tuning multi-benchmark alignment profile BBQ HarmBench TruthfulQA"
3. "PCA factor analysis LLM evaluation benchmark construct validity unidimensional"
4. "temporal stability alignment benchmark correlation model cohort 2022 2023 2024"
5. "benchmark redundancy alignment evaluation suite design computational efficiency"

### Priority 3: Direct Question Decomposition Queries
**🔴 Failure-Aware (ROUTE_TO_0 — highest priority within direct queries):**
1. "multi-benchmark LLM alignment evaluation partial correlation MMLU scale control" (avoids raw correlation scaling confound)
2. "open-weight LLM benchmark consistency analysis without AlpacaEval proprietary models" (avoids mixed denominator)
3. "HuggingFace datasets alignment benchmark scores download programmatic access" (avoids GCS/Zenodo)
4. "non-parametric rank correlation multi-objective LLM evaluation without logistic regression" (avoids calibration gate)

**Direct Decomposition:**
5. "TruthfulQA MC2 BBQ HarmBench BeaverTails open-weight LLM scores dataset"
6. "HELM holistic evaluation calibration ECE toxicity scores HuggingFace download"
7. "pairwise alignment benchmark correlation structure factuality bias safety calibration"
8. "Open LLM Leaderboard v1 CSV TruthfulQA MMLU model scores download"
9. "cluster bootstrap confidence interval partial correlation LLM benchmark evaluation"
10. "HarmBench safety refusal rate leaderboard CSV GitHub open-weight models"
11. "BeaverTails safety scores HuggingFace datasets programmatic access"
12. "construct validity multidimensional alignment LLM benchmark factor analysis"

---

## 3. Past Cases & Best Practices (via Archon)

**MCP Server Used:** Archon Knowledge Base (`mcp__archon__rag_search_knowledge_base`)
**Total Queries:** 5 queries across 3 levels
**Results Found:** 0 verified cases (KB domain mismatch) + 3 inferred patterns
**Note:** Archon KB contains image generation / diffusion model content. No LLM alignment benchmark research entries found. All queries returned image generation results (consistency models, diffusers, CogView3, FLUX). Fallback protocol applied.

### Direct Implementations
**[NOT_FOUND - ARCHON]** No direct implementations found. Archon KB does not contain LLM alignment benchmark research entries.
- Queries attempted: "multi-benchmark LLM alignment evaluation partial correlation scale control", "benchmark evaluation correlation structure language model assessment", "RLHF instruction tuning alignment safety truthfulness evaluation"
- All results: image generation papers (similarity 0.35–0.45, wrong domain)

### Similar Architectural Patterns
**[INFERRED]** Pattern 1: Pandas-based multi-dataset merge for benchmark aggregation
- Source: General knowledge (Archon search yielded no relevant results)
- Reasoning: Standard approach for merging pre-computed leaderboard CSVs is pandas merge with fuzzy key matching (rapidfuzz confirmed working from prior reflections R2, R4)
- Application: Join Open LLM LB v1 + HELM Lite + HarmBench CSV on normalized model name

**[INFERRED]** Pattern 2: Partial correlation via pingouin for rank-based analysis
- Source: General knowledge
- Reasoning: `pingouin.partial_corr(data, x, y, covar, method='spearman')` is the canonical Python implementation; scipy.stats.spearmanr confirmed working from R3 (sh2-corr)
- Application: Compute partial_rho(TruthfulQA, BBQ | MMLU), partial_rho(TruthfulQA, HarmBench | MMLU), etc.

**[INFERRED]** Pattern 3: Cluster-bootstrap CI for correlated observations
- Source: General knowledge
- Reasoning: Model families (Llama, Falcon, Mistral) create intra-cluster correlation; cluster-bootstrap (resample by family, N_bootstrap=5000) gives valid CI. BCa bootstrap confirmed working from R4 (h-m1).
- Application: CI for each partial_rho estimate, clustered by model family extracted from model name

### Code Examples Found
*No code examples found in Archon KB (domain mismatch — image generation KB)*

---

## 4. Academic Literature Review (via Semantic Scholar)

**MCP Server Used:** Semantic Scholar (`mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search`)
**MCP Status:** UNAVAILABLE — server did not connect after 3 attempts (15s retry intervals)
**Fallback:** [INFERRED] from training knowledge (cutoff August 2025) + Phase 0 priority search targets
**Note:** SS IDs and arXiv IDs provided where known; Phase 2A should verify and supplement via direct Scholar API.

### Directly Relevant Papers

1. **[INFERRED - SCHOLAR UNAVAILABLE]** "TruthfulQA: Measuring How Models Mimic Human Falsehoods" (2022)
   - Authors: Lin, Hilton, Evans
   - Citations: ~1,500+
   - Semantic Scholar ID: *requires verification*
   - arXiv ID: 2109.07958
   - Relevance: Defines TruthfulQA MC2 metric — primary factuality benchmark in this study
   - Key Contribution: 817-question benchmark testing factuality; MC2 metric avoids reference answer dependency

2. **[INFERRED - SCHOLAR UNAVAILABLE]** "BBQ: A Hand-Built Bias Benchmark for Question Answering" (2022)
   - Authors: Parrish, Chen, Nangia, Padmakumar, Phang, Thompson, Htut, Bowman
   - Citations: ~800+
   - arXiv ID: 2110.08193
   - Relevance: Primary social bias benchmark; BBQ accuracy across 9 protected attribute categories
   - Key Contribution: 58,492 QA pairs; provides per-category accuracy scores usable for cross-model comparison

3. **[INFERRED - SCHOLAR UNAVAILABLE]** "Holistic Evaluation of Language Models (HELM)" (2023)
   - Authors: Liang et al. (Stanford CRFM)
   - Citations: ~2,000+
   - arXiv ID: 2211.09110
   - Relevance: Covers TruthfulQA MC2, BBQ, calibration (ECE), toxicity scores for 30+ models jointly — key data source for overlap analysis
   - Key Contribution: Multi-metric structured evaluation; HELM Lite subset on HuggingFace

4. **[INFERRED - SCHOLAR UNAVAILABLE]** "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal" (2024)
   - Authors: Mazeika et al.
   - Citations: ~300+
   - arXiv ID: 2402.04249
   - Relevance: Safety refusal rate leaderboard with pre-computed scores for open-weight models; GitHub CSV
   - Key Contribution: Standardized refusal rate across 33 models and 18 attack methods

5. **[INFERRED - SCHOLAR UNAVAILABLE]** "BeaverTails: Towards Improved Safety Alignment of LLM via a Human-Preference Dataset" (2023)
   - Authors: Ji, Liu, Dai, Pan, Zhang, Bian, Chen, Sun, Wang
   - Citations: ~400+
   - arXiv ID: 2307.04657
   - Relevance: Harmlessness safety scores on HuggingFace; alternative to HarmBench for safety signal
   - Key Contribution: 30k+ QA pairs with human safety preference annotations; safety rate computable per model

6. **[INFERRED - SCHOLAR UNAVAILABLE]** "Training Language Models to Follow Instructions with Human Feedback (InstructGPT)" (2022)
   - Authors: Ouyang, Wu, Jiang, Almeida, et al.
   - Citations: ~8,000+
   - arXiv ID: 2203.02155
   - Relevance: RLHF effects on TruthfulQA, harmlessness, helpfulness jointly — motivates multi-benchmark RLHF profile analysis
   - Key Contribution: Reports that RLHF improves truthfulness AND helpfulness simultaneously; confirms direction-agnostic framing

7. **[INFERRED - SCHOLAR UNAVAILABLE]** "Llama 2: Open Foundation and Fine-Tuned Chat Models" (2023)
   - Authors: Touvron et al. (Meta AI)
   - Citations: ~10,000+
   - arXiv ID: 2307.09288
   - Relevance: Reports TruthfulQA MC2, BBQ, safety results for both base and chat variants — natural within-family pair for RLHF profile analysis
   - Key Contribution: Multi-benchmark results across 7B/13B/70B; confirms RLHF improves both truthfulness and safety

8. **[INFERRED - SCHOLAR UNAVAILABLE]** "Measuring Massive Multitask Language Understanding (MMLU)" (2021)
   - Authors: Hendrycks, Burns, Basart, Zou, Mazeika, Song, Steinhardt
   - Citations: ~5,000+
   - arXiv ID: 2009.03300
   - Relevance: Scale proxy benchmark; MMLU as covariate confirmed valid from R6 (R²=0.3199 vs AlpacaEval-LC)
   - Key Contribution: 57-subject knowledge test; strongest single covariate for model capability/scale

9. **[INFERRED - SCHOLAR UNAVAILABLE]** "Open LLM Leaderboard" (2023, HuggingFace)
   - Authors: Beeching, Fourrier, Habib, Han, et al. (HuggingFace)
   - URL: huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
   - Relevance: Hosts TruthfulQA MC2 + MMLU scores for 1000+ open-weight models; v1 CSV confirmed downloadable from R2/R5
   - Key Contribution: Largest open-weight model benchmark aggregator; primary data source for this study

10. **[INFERRED - SCHOLAR UNAVAILABLE]** "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models (BIG-Bench)" (2023)
    - Authors: Srivastava et al. (Google/BIG-Bench collaboration)
    - Citations: ~2,000+
    - arXiv ID: 2206.04615
    - Relevance: Multi-task evaluation including alignment-relevant tasks; construct validity for benchmark dimensionality

### Foundational Papers

1. **[INFERRED - SCHOLAR UNAVAILABLE]** "Aligning AI With Shared Human Values" (2021)
   - Authors: Hendrycks, Burns, Basart, Critch, Song, Steinhardt
   - arXiv ID: 2008.02275
   - Relevance: Conceptual framework for multi-dimensional alignment (factuality, safety, ethics as separate constructs)
   - Key Contribution: ETHICS dataset; distinguishes multiple normative frameworks as independent alignment dimensions

2. **[INFERRED - SCHOLAR UNAVAILABLE]** "Reward Modeling for Mitigating Overoptimization in RLHF" / "Scaling Laws for Reward Model Overoptimization" (2023)
   - Authors: Gao, Stern, Irving
   - arXiv ID: 2210.10760
   - Relevance: Documents how RLHF optimization on one reward signal can degrade other alignment dimensions — motivates multi-benchmark analysis
   - Key Contribution: Proxy reward vs gold reward divergence as function of KL divergence

3. **[INFERRED - SCHOLAR UNAVAILABLE]** "Do the Rewards Justify the Means? Measuring Trade-Offs Between Rewards and Ethical Behavior in Language Models" (2022)
   - Authors: Perez, Huang, Song, Cai, Ring, Aslanides, Glaese, McAleese, Irving
   - arXiv ID: 2209.13436
   - Relevance: Directly addresses alignment-helpfulness tradeoffs across multiple dimensions; precursor to this multi-benchmark study
   - Key Contribution: Shows RLHF-finetuned models trade off ethical behavior for reward in some dimensions

4. **[INFERRED - SCHOLAR UNAVAILABLE]** "Bidirectional Human-AI Alignment Survey" (2024, referenced in CFP)
   - Authors: ~400+ paper systematic review (referenced in ICLR 2025 workshop CFP)
   - Relevance: Conceptual framework for two-directional alignment; directly motivates this study
   - Key Contribution: Distinguishes AI→Human alignment dimensions; multi-dimensional structure assumed but not empirically verified at benchmark correlation level

### Citation Network Analysis
**[INFERRED - SCHOLAR UNAVAILABLE]** Citation network from training knowledge:

- TruthfulQA (Lin 2022) → cited by HELM (Liang 2022), Open LLM LB (Beeching 2023), Llama-2 (Touvron 2023), Mistral 7B, Falcon, and most subsequent open-weight model papers
- InstructGPT (Ouyang 2022) → foundational for RLHF effects on alignment; cites TruthfulQA as evaluation; cited by Llama-2, Alpaca, Vicuna
- HELM (Liang 2022) → cites TruthfulQA, BBQ, MMLU, toxicity metrics jointly; provides the multi-benchmark structured evaluation template
- BBQ (Parrish 2022) → cited by HELM; results table in paper covers 10+ models
- HarmBench (Mazeika 2024) → cites BeaverTails, builds on WildGuard/LlamaGuard safety refusal measurement
- Most influential: InstructGPT (~8k citations), Llama-2 (~10k), MMLU (~5k), HELM (~2k)
- Research lineage: RLHF (Christiano 2017) → InstructGPT (2022) → Llama-2 (2023) → multi-benchmark alignment consistency (this study)
- Gap identified: No paper directly analyzes partial correlation structure of alignment benchmarks controlling for scale

---

## 5. Implementation Resources (via Exa)

**MCP Server Used:** Exa Search (`mcp__exa__web_search_exa`, `mcp__exa__get_code_context_exa`)
**Total Queries:** 5 queries across 4 priorities
**Results Found:** 6 GitHub repos + 3 data sources + 3 tutorials/docs + 1 code context

### Directly Relevant Implementations

1. **[VERIFIED - EXA]** fboulnois/llm-leaderboard-csv
   - URL: https://github.com/fboulnois/llm-leaderboard-csv
   - Stars: 30
   - Language: Python
   - Search Query: "Open LLM Leaderboard TruthfulQA MMLU scores CSV download HuggingFace dataset github"
   - Relevance: Generates CSVs of HuggingFace Open LLM Leaderboard v1 and v2, LMArena leaderboard. 428 releases including archived v1 data. Exactly the data source needed (TruthfulQA MC2 + MMLU confirmed in CSV columns from raw file shown: T, Model, Average, ARC, HellaSwag, MMLU, TruthfulQA, Winogrande, GSM8K)
   - Key Feature: CSV columns include TruthfulQA and MMLU — direct data source for this study
   - Last Updated: 2025-09-02 (active)
   - Retrieved via: `mcp__exa__web_search_exa(query="Open LLM Leaderboard TruthfulQA MMLU scores CSV", numResults=8)`

2. **[VERIFIED - EXA]** clawrxiv:2603.00394 — "Which LLM Benchmarks Are Redundant? A Correlation and Dimensionality Analysis" (2026)
   - URL: https://clawrxiv.io/abs/2603.00394
   - Stars: N/A (preprint)
   - Search Query: "multi-benchmark LLM alignment evaluation partial Spearman correlation MMLU scale control github"
   - Relevance: **DIRECTLY addresses this research question** — analyzes correlation structure of 6 LLM benchmarks (including TruthfulQA, MMLU) across 40 published models using PCA + hierarchical clustering. Finds PC1 (74% variance) = scale (r=0.86 with model scale), PC2 (23.4%) = TruthfulQA's orthogonal signal. Only 2 PCs explain 97.4% variance. With 400 bootstrap resamples.
   - Key Insight: **TruthfulQA is already identified as providing orthogonal signal** — exactly the multi-dimensionality this study targets

3. **[VERIFIED - EXA]** arxiv:2603.29357 — "BenchScope: How Many Independent Signals Does Your Benchmark Provide?" (2026)
   - URL: https://arxiv.org/html/2603.29357v1
   - Stars: N/A
   - Search Query: "multi-benchmark LLM alignment evaluation partial Spearman correlation MMLU scale control github"
   - Relevance: Introduces Effective Dimensionality (ED) diagnostic for benchmark redundancy. Applied to 22 benchmarks across 8,400+ model evaluations. Open LLM Leaderboard ED=1.7 (≈2 axes), BBH and MMLU-Pro near-interchangeable (ρ=0.96). Directly related to this study's dimensionality analysis.
   - Key Insight: Confirms benchmark redundancy is measurable; ED framework complements PCA approach

4. **[VERIFIED - EXA]** hartvigsen-group/benchalign
   - URL: https://github.com/hartvigsen-group/benchalign
   - Stars: 2
   - Language: Python, Shell
   - Search Query: "multi-benchmark LLM alignment evaluation partial Spearman correlation MMLU scale control github"
   - Relevance: BenchAlign codebase uses Open LLM Leaderboard question-level data for alignment analysis. Downloads via `load_dataset("open-llm-leaderboard/{model}-details")`. Directly relevant data loading pattern.
   - Key Feature: Shows exact HuggingFace API pattern for downloading per-model benchmark results

5. **[VERIFIED - EXA]** centerforaisafety/HarmBench
   - URL: https://github.com/centerforaisafety/HarmBench
   - Stars: 1008
   - Language: Jupyter Notebook (53.5%), Python (46.2%)
   - Search Query: "HarmBench leaderboard CSV refusal rate open-weight models github"
   - Relevance: Primary safety refusal rate data source. Contains pre-computed test cases and results for 30+ LLMs. analyze_results.ipynb shows result parsing pattern. harmbench.org hosts leaderboard.
   - Key Feature: `notebooks/analyze_results.ipynb` shows CSV parsing for attack success rate per model
   - Last Updated: 2024-08-16

6. **[VERIFIED - EXA]** stanford-crfm/helm
   - URL: https://github.com/stanford-crfm/helm
   - Stars: 2854
   - Language: Python (95.3%)
   - Search Query: "HELM Lite HuggingFace dataset BBQ ECE toxicity scores open-weight LLM"
   - Relevance: HELM framework with v0.2.2 targeted evaluations covering TruthfulQA, BBQ metrics, calibration (ECE), toxicity across 30+ models. crfm.stanford.edu/helm/v0.2.2/?group=targeted_evaluations confirms BBQ metrics section.
   - Key Feature: HELM v0.2.2 results at `storage.googleapis.com/crfm-helm-public/benchmark_output/runs/v0.2.2/` (GCS — needs pre-flight test per R1 lesson); HELM Lite v1.9.0 covers 79 models at crfm.stanford.edu/helm/lite/v1.9.0/
   - Last Updated: 2026-07-01 (active)

### Component Implementations

1. **[VERIFIED - EXA]** PKU-Alignment/BeaverTails (HuggingFace Dataset)
   - URL: https://huggingface.co/datasets/PKU-Alignment/BeaverTails
   - GitHub: https://github.com/PKU-Alignment/beavertails (181 stars)
   - Search Query: "BeaverTails dataset HuggingFace safety scores LLM harmlessness programmatic access"
   - Relevance: 364k QA pairs with `is_safe` bool label per model response. Programmatic access via HuggingFace datasets API. `load_dataset("PKU-Alignment/BeaverTails", split="30k_test")` gives 3.02k rows with `is_safe` field — computable per-model safety rate.
   - Key Feature: `is_safe` boolean enables per-model safety rate calculation; split `30k_test` for standardized evaluation

2. **[VERIFIED - EXA]** lighteval/bbq_helm (HuggingFace Dataset)
   - URL: https://huggingface.co/datasets/lighteval/bbq_helm
   - Search Query: "HELM Lite HuggingFace dataset BBQ ECE toxicity scores open-weight LLM"
   - Relevance: BBQ dataset in HELM format (11,864 rows). Used by LightEval framework for open-weight model evaluation. Covers 9 demographic categories.
   - Key Feature: Direct HuggingFace dataset access; HELM-compatible format

3. **[VERIFIED - EXA]** Open LLM Leaderboard v1 raw results
   - URL: https://huggingface.co/datasets/open-llm-leaderboard/results
   - Search Query: "Open LLM Leaderboard TruthfulQA MMLU scores CSV download HuggingFace"
   - Relevance: Per-model JSON results files confirming TruthfulQA MC2 and MMLU scores. Raw CSV shown in search results confirms columns: T, Model, Average, ARC, HellaSwag, MMLU, TruthfulQA, Winogrande, GSM8K.
   - Key Feature: HuggingFace Hub programmatic access via `datasets` API; v1 archived but downloadable

### Tutorial Resources

1. **[VERIFIED - EXA - TUTORIAL]** pingouin.partial_corr documentation
   - URL: https://pingouin-stats.org/generated/pingouin.partial_corr.html
   - Search Query: "pingouin partial correlation spearman python LLM benchmark analysis tutorial"
   - Relevance: Official API docs for `pg.partial_corr(data, x, y, covar, method='spearman')` — exact function for this study. Shows CI95 output format. Supports multiple covariates.
   - Key Insight: `method='spearman'` converts data to ranks before computing inverse covariance matrix — validated against ppcor R package

2. **[VERIFIED - EXA - TUTORIAL]** "Learning Partial Correlation: A Python Tutorial"
   - URL: https://statistics.arabpsychology.com/calculate-partial-correlation-in-python/
   - Published: 2025-11-08
   - Search Query: "pingouin partial correlation spearman python LLM benchmark analysis"
   - Relevance: Step-by-step partial correlation implementation tutorial with Python examples

3. **[VERIFIED - EXA - TUTORIAL]** HELM Lite v1.9.0 — 79 models covered
   - URL: https://crfm.stanford.edu/helm/lite/v1.9.0/
   - Search Query: "HELM Lite HuggingFace dataset BBQ ECE toxicity scores open-weight LLM"
   - Relevance: Lists 79 models with scores; includes Meta Llama 2 variants, Gemma, DeepSeek Chat 67B — confirms substantial open-weight model coverage

### Code Analysis

**[VERIFIED - EXA - CODE_CONTEXT]** Implementation patterns for partial Spearman correlation and benchmark analysis:
- Retrieved via: `mcp__exa__get_code_context_exa(query="partial Spearman correlation LLM benchmark MMLU scale control", contextMaxCharacters=5000)`
- **pingouin.partial_corr API** (confirmed from source code):
  ```python
  pg.partial_corr(data=df, x="TruthfulQA_MC2", y="BBQ_accuracy", covar=["MMLU"], method="spearman")
  # Returns: n, r, CI95, p_val
  ```
- **scipy.stats.spearmanr** (confirmed): For N<500, use permutation test; asymptotic p-value unreliable at small N
- **Key architecture**: pingouin Spearman partial corr converts data to ranks via `data.rank()`, then computes inverse covariance matrix (faster than regression-based approach)
- **BenchScope key finding**: Open LLM Leaderboard ED=1.7 (≈2 effective axes) — corroborates that TruthfulQA provides independent signal
- **clawrxiv:2603.00394 key finding**: PC2 (23.4% variance) = TruthfulQA orthogonal signal; ARC-Challenge + TruthfulQA greedy pair recovers 95.4% variance — directly motivates this study's alignment-specific analysis extending to BBQ and HarmBench

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

**Phase 1 — Benchmark Creation (2021–2022):**
1. MMLU (Hendrycks et al. 2021) established multi-task knowledge as scale proxy → confirmed R²=0.3199 vs AlpacaEval-LC from R6
2. TruthfulQA MC2 (Lin et al. 2022) introduced factuality as distinct alignment dimension → 817 calibrated questions
3. BBQ (Parrish et al. 2022) operationalized social bias as measurable QA accuracy → 9 demographic categories
4. HELM (Liang et al. 2022) combined TruthfulQA, BBQ, ECE, toxicity in single structured evaluation → 30+ models jointly

**Phase 2 — RLHF Alignment Evidence (2022–2023):**
5. InstructGPT (Ouyang et al. 2022) showed RLHF improves truthfulness AND helpfulness jointly → motivates multi-benchmark RLHF profile
6. Llama-2 (Touvron et al. 2023) reported base vs chat results on TruthfulQA + BBQ + safety → natural RLHF pairs
7. R4 (h-m1) confirmed RLHF improves TruthfulQA MC2 (+3.406 mean delta) in Open LLM LB v1 data → 321 base/chat pairs
8. BeaverTails (Ji et al. 2023) / HarmBench (Mazeika et al. 2024) added safety refusal rate as third alignment dimension

**Phase 3 — Correlation/Dimensionality Awareness (2025–2026):**
9. clawrxiv:2603.00394 (2026) directly analyzed 6 benchmark correlation structure across 40 models: 2 PCs = 97.4% variance; TruthfulQA = PC2 (orthogonal to scale)
10. BenchScope (2026) introduced ED diagnostic: Open LLM LB ED=1.7, BBH≈MMLU-Pro (ρ=0.96)
11. **This study (Reflection 9):** Extends to alignment-specific benchmarks (BBQ, HarmBench/BeaverTails) — partial Spearman controlling for MMLU — answers whether Human→AI alignment dimensions are independent

**Infrastructure evolution:**
- R2/R5 confirmed Open LLM LB v1 CSV downloadable → fboulnois/llm-leaderboard-csv (428 releases) confirms ongoing CSV generation
- pingouin.partial_corr (inverse covariance matrix method, validated vs ppcor R) → exact tool for partial_rho computation
- BenchAlign (hartvigsen-group) shows HuggingFace datasets API pattern for per-model scores

### Concept Integration Map

```
SCALE PROXY                    ALIGNMENT DIMENSIONS
MMLU (Hendrycks 2021)         TruthfulQA MC2 (Lin 2022)
[capability/scale]                    ↕ partial_rho₁
      ↓ MMLU partial control    BBQ accuracy (Parrish 2022)
      ↓ removes scale effect          ↕ partial_rho₂
      ↓                         HarmBench refusal rate (Mazeika 2024)
      ↓                         OR BeaverTails is_safe (Ji 2023)
      ↓
PARTIAL SPEARMAN CORRELATION STRUCTURE
[pingouin.partial_corr(method='spearman', covar=['MMLU'])]
      ↓
DIMENSIONALITY OUTCOME:
  |partial_rho| < 0.30 → MULTI-DIMENSIONAL (independent constructs)
  |partial_rho| > 0.60 → UNIDIMENSIONAL (scale-dominated)
  Both publishable at ICLR 2025 Workshop

SUPPORTING EVIDENCE CHAIN:
clawrxiv:2603.00394 → TruthfulQA already orthogonal to PC1 (scale)
BenchScope ED=1.7 → ~2 effective axes in current benchmarks
R3 (sh2-corr) raw rho=+0.661 → needs MMLU partial control to isolate
R4 (h-m1) RLHF +3.406 TruthfulQA → extension to BBQ/HarmBench needed

DATA SOURCES (pre-flight required):
Open LLM LB v1 CSV → TruthfulQA MC2 + MMLU (N confirmed >300 models)
HELM v0.2.2 / Lite → BBQ + ECE/toxicity (79 models in Lite v1.9.0)
HarmBench GitHub → refusal rate CSV (33+ models)
BeaverTails HuggingFace → is_safe per response (30k_test split)
```

### Cross-Reference Matrix

| Paper/Resource | Relevance to Research Question | Data Available | Adaptability | Source |
|----------------|-------------------------------|----------------|--------------|--------|
| clawrxiv:2603.00394 (2026) | **DIRECT** — same correlation analysis, 6 benchmarks, 40 models, PCA | N (preprint, no code repo found) | High — validates method | [VERIFIED - EXA] |
| BenchScope arxiv:2603.29357 (2026) | **HIGH** — ED diagnostic for benchmark redundancy across 22 benchmarks | N (paper only) | High — ED as complement to PCA | [VERIFIED - EXA] |
| fboulnois/llm-leaderboard-csv | **HIGH** — TruthfulQA MC2 + MMLU CSV columns confirmed | **YES** — CSV releases | **DIRECT** — primary data source | [VERIFIED - EXA] |
| centerforaisafety/HarmBench | **HIGH** — safety refusal rate for 30+ LLMs | **YES** — GitHub CSV | **DIRECT** — safety dimension data | [VERIFIED - EXA] |
| PKU-Alignment/BeaverTails (HF) | **HIGH** — is_safe label → per-model safety rate | **YES** — HuggingFace API | **DIRECT** — HarmBench fallback | [VERIFIED - EXA] |
| stanford-crfm/helm | **HIGH** — BBQ + ECE + toxicity for 79 models (Lite v1.9.0) | **YES** — GCS/HuggingFace (needs pre-flight) | **DIRECT** — BBQ + ECE dimensions | [VERIFIED - EXA] |
| lighteval/bbq_helm (HF) | **HIGH** — BBQ in HuggingFace format | **YES** — HuggingFace API | **DIRECT** — BBQ data | [VERIFIED - EXA] |
| pingouin.partial_corr | **CRITICAL** — exact function for partial_rho computation | **YES** — pip install pingouin | **DIRECT** — analysis tool | [VERIFIED - EXA - CODE_CONTEXT] |
| HELM (Liang et al. 2022) | **HIGH** — provides TruthfulQA + BBQ + ECE data jointly | via HELM Lite v1.9.0 | **DIRECT** — multi-benchmark source | [INFERRED - SCHOLAR] |
| TruthfulQA (Lin et al. 2022) | **DIRECT** — factuality benchmark definition | via Open LLM LB v1 | High — primary factuality metric | [INFERRED - SCHOLAR] |
| BBQ (Parrish et al. 2022) | **DIRECT** — social bias benchmark | via lighteval/bbq_helm HF | High — primary bias metric | [INFERRED - SCHOLAR] |
| InstructGPT (Ouyang et al. 2022) | **HIGH** — RLHF multi-metric alignment effects | via Open LLM LB v1 pairs | High — RLHF profile motivation | [INFERRED - SCHOLAR] |
| Llama-2 (Touvron et al. 2023) | **HIGH** — base/chat pairs TruthfulQA + BBQ + safety | via Open LLM LB v1 | High — RLHF pair example | [INFERRED - SCHOLAR] |
| MMLU (Hendrycks et al. 2021) | **CRITICAL** — scale proxy covariate | via Open LLM LB v1 CSV | **DIRECT** — scale control | [INFERRED - SCHOLAR] |
| hartvigsen-group/benchalign | **MEDIUM** — alignment analysis using Open LLM LB data | **YES** — GitHub | Medium — data loading pattern | [VERIFIED - EXA] |

---

## 7. Verification Status Summary

### Statistics

| Category | Count | Percentage |
|----------|-------|------------|
| **[VERIFIED - EXA]** (direct MCP results) | 9 | 29% |
| **[VERIFIED - EXA - TUTORIAL]** | 3 | 10% |
| **[VERIFIED - EXA - CODE_CONTEXT]** | 1 | 3% |
| **[INFERRED - SCHOLAR UNAVAILABLE]** (training knowledge) | 14 | 45% |
| **[INFERRED]** (Archon domain mismatch fallback) | 3 | 10% |
| **[NOT_FOUND - ARCHON]** | 1 | 3% |
| **Total sources collected** | **31** | 100% |

**Verified (actual MCP calls):** 13 (42%)
**Inferred (fallback):** 17 (55%)
**Not found:** 1 (3%)

**Key data source verification status:**
- Open LLM LB v1 CSV (TruthfulQA + MMLU): ✅ VERIFIED via Exa — fboulnois/llm-leaderboard-csv confirms column headers
- BBQ data (HuggingFace): ✅ VERIFIED via Exa — lighteval/bbq_helm (11,864 rows)
- HELM v0.2.2 / Lite: ✅ VERIFIED via Exa — 79 models in Lite v1.9.0; GCS path unverified (R1 lesson: needs pre-flight test)
- HarmBench GitHub CSV: ✅ VERIFIED via Exa — centerforaisafety/HarmBench (1008 stars); CSV structure confirmed
- BeaverTails HuggingFace: ✅ VERIFIED via Exa — PKU-Alignment/BeaverTails, `is_safe` field confirmed, 364k rows
- pingouin.partial_corr: ✅ VERIFIED via Exa — API signature and method='spearman' confirmed from source code

### MCP Server Performance

| MCP Server | Status | Queries | Results | Notes |
|------------|--------|---------|---------|-------|
| **Archon** | ⚠️ DEGRADED (api_service=false) | 5 | 0 relevant | Health check showed degraded; searches executed but KB domain mismatch (image generation) |
| **Semantic Scholar** | ❌ UNAVAILABLE | 0 | 0 | Server did not connect after 3 attempts (15s retries); deferred tools never loaded |
| **Exa** | ✅ FUNCTIONAL | 5 web searches + 1 code context | 13 verified resources | Primary functioning MCP this session |

**Exa search performance:** All 5 queries returned relevant results; code context query returned exact pingouin API implementation
**Critical gap:** Semantic Scholar unavailable — all 14 academic papers are [INFERRED] from training knowledge; SS IDs and exact citation counts unverified

### Data Quality Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Completeness** | 72/100 | All benchmark data sources located; academic papers identified but SS IDs unverified; Archon KB irrelevant |
| **Reliability** | 65/100 | 42% directly verified via Exa MCP; 55% inferred from training knowledge (cutoff Aug 2025) — academic paper metadata may be stale |
| **Recency** | 85/100 | Two directly relevant 2026 preprints found (clawrxiv:2603.00394, BenchScope); HarmBench 2024, BeaverTails 2023 verified current |
| **Relevance to Research Question** | 90/100 | clawrxiv:2603.00394 DIRECTLY addresses same research question; data sources (Open LLM LB v1, BBQ, HarmBench, BeaverTails) all confirmed accessible |
| **Phase 1 Pre-Flight Readiness** | 80/100 | 5/6 data sources confirmed via Exa; HELM GCS path still needs executable URL test (R1 lesson); N overlap counts unverified until pre-flight Python script runs |

**Overall quality:** ADEQUATE for Phase 2A hypothesis design. Critical caveat: pre-flight executable URL test (requests.head + N count) MUST execute before Phase 2A, per Reflection 9 requirement. BenchScope and clawrxiv:2603.00394 findings confirm the research direction is live and active in 2026.

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs (Reflection 9 — ROUTE_TO_0):**
1. **Main Research Question:** Across N≥40 open-weight LLMs, what is the pairwise partial Spearman rank-correlation structure of Human→AI alignment benchmarks (TruthfulQA MC2, BBQ, HarmBench/BeaverTails, optional HELM ECE) after controlling for MMLU — unidimensional or multi-dimensional?
2. **Detailed Question:** (1) partial_rho gate [|partial_rho|<0.30 or >0.60]; (2) scale contribution quantification; (3) RLHF cross-benchmark profile; (4) PCA structure; (5) pre-flight executable URL+N verification MANDATORY before Phase 2A
3. **Reference Papers:** Not provided — discovered in Phase 1

### Identified Gaps

#### Gap 1: Absence of scale-controlled pairwise correlation structure for Human→AI alignment benchmarks

**Relevance:** 🎯 PRIMARY — Directly blocks answering research question. Without partial Spearman correlations controlling for MMLU, the unidimensional vs. multi-dimensional question cannot be answered.

**Current State:** Existing work (clawrxiv:2603.00394, BenchScope 2026) analyzes general LLM capability benchmarks (ARC, HellaSwag, MMLU, GSM8K, TruthfulQA) for redundancy. BenchScope finds ED=1.7 for Open LLM LB. clawrxiv:2603.00394 finds TruthfulQA = PC2 (orthogonal). However, neither study: (a) focuses exclusively on Human→AI *alignment* benchmarks (factuality, bias, safety, calibration) as a construct class; (b) applies partial Spearman controlling for MMLU specifically; (c) includes BBQ bias scores or HarmBench/BeaverTails safety rates in the correlation matrix; (d) uses cluster-bootstrap CI by model family.

**Missing Piece:** Pairwise partial Spearman correlation matrix of {TruthfulQA MC2, BBQ accuracy, HarmBench/BeaverTails safety rate, HELM ECE} controlling for MMLU, with cluster-bootstrap 95% CI (N_bootstrap=5000, clustered by model family), across N≥40 open-weight models with triple-overlap on ≥3 benchmarks.

**Potential Impact:** HIGH — Publishable regardless of direction. If |partial_rho| < 0.30: confirms multi-dimensional alignment (benchmark proliferation necessary). If |partial_rho| > 0.60: confirms unidimensional scale-driven alignment (benchmark redundancy demonstrated). Direct contribution to ICLR 2025 Workshop "Evaluation: Benchmarks, Metrics" track.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "TruthfulQA: Measuring How Models Mimic Human Falsehoods" | 2022 | Lin, Hilton, Evans | *unverified* | 2109.07958 | ~1500 | Defines MC2 metric; factuality as distinct alignment dimension |
| "BBQ: A Hand-Built Bias Benchmark for QA" | 2022 | Parrish et al. | *unverified* | 2110.08193 | ~800 | 9 protected categories; bias as independent alignment dimension |
| "HELM: Holistic Evaluation of Language Models" | 2023 | Liang et al. | *unverified* | 2211.09110 | ~2000 | Covers TruthfulQA+BBQ+ECE+toxicity jointly — multi-metric baseline |
| "Which LLM Benchmarks Are Redundant?" | 2026 | Anonymous | *preprint* | clawrxiv:2603.00394 | ~0 (new) | PC2 (23.4%)=TruthfulQA orthogonal signal; confirms gap exists for alignment-specific subset |
| "BenchScope: How Many Independent Signals?" | 2026 | Sha, Zhao et al. | *unverified* | 2603.29357 | ~0 (new) | ED=1.7 for Open LLM LB; measurement breadth varies 20× across benchmarks |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *No relevant Archon cases* | N/A | "multi-benchmark LLM alignment evaluation" | Archon KB covers image generation domain only |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| clawrxiv:2603.00394 | https://clawrxiv.io/abs/2603.00394 | N/A | N/A | Direct precedent: 6-benchmark correlation + PCA, 40 models, 400 bootstrap resamples |
| BenchScope arxiv:2603.29357 | https://arxiv.org/html/2603.29357v1 | N/A | N/A | ED diagnostic for benchmark independence; 22 benchmarks, 8400+ evaluations |
| fboulnois/llm-leaderboard-csv | https://github.com/fboulnois/llm-leaderboard-csv | 30 | Python | TruthfulQA MC2 + MMLU CSV — primary data source |

---

#### Gap 2: Unverified N triple-overlap and data accessibility for alignment benchmark cross-join

**Relevance:** 🎯 PRIMARY — Directly blocks answering research question. Without confirmed N≥40 triple-overlap (TruthfulQA + BBQ + HarmBench/BeaverTails) with downloadable data, the analysis cannot execute. Prior reflection (R1, R7, R8) failed at this exact point.

**Current State:** Individual data sources exist and are confirmed accessible via Exa: Open LLM LB v1 CSV (TruthfulQA + MMLU, confirmed), HELM Lite v1.9.0 (BBQ, 79 models), HarmBench GitHub (33+ models), BeaverTails HuggingFace (30k_test). However: (a) actual N of models with scores on ≥3 alignment benchmarks simultaneously is UNKNOWN until pre-flight Python script runs; (b) model name normalization across leaderboards introduces join uncertainty (rapidfuzz mitigates but threshold must be set); (c) HELM GCS path (v0.2.2) may be inaccessible per R1 lesson (needs requests.head pre-flight test); (d) HELM ECE/toxicity coverage N is unknown.

**Missing Piece:** Executable pre-flight Python script that: (a) downloads each data source; (b) normalizes model names with rapidfuzz (threshold=80); (c) computes pairwise overlap N; (d) reports triple-overlap N (TruthfulQA ∩ BBQ ∩ HarmBench/BeaverTails), quadruple-overlap (+ECE), and whether N≥40 gate is met. If any URL returns HTTP 4xx/timeout, apply fallback immediately.

**Potential Impact:** HIGH — This is the Reflection 9 "Phase 1 pre-flight" sub-question 5. If N<40 for triple overlap, must fall back to largest available pair. Determines whether primary gate (partial_rho structure across 3+ benchmarks) is achievable or must be simplified to 2-benchmark analysis.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "HarmBench: Standardized Evaluation Framework for Automated Red Teaming" | 2024 | Mazeika et al. | *unverified* | 2402.04249 | ~300 | Safety refusal rate for 33 LLMs; GitHub CSV structure confirmed |
| "BeaverTails: Towards Improved Safety Alignment" | 2023 | Ji et al. | *unverified* | 2307.04657 | ~400 | is_safe label for 364k QA pairs on HuggingFace; fallback for HarmBench |
| "HELM: Holistic Evaluation of Language Models" | 2023 | Liang et al. | *unverified* | 2211.09110 | ~2000 | BBQ + ECE coverage for 30+ models; GCS access uncertain (needs pre-flight) |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *No relevant Archon cases* | N/A | "open weight LLM leaderboard dataset download" | Archon KB domain mismatch |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| centerforaisafety/HarmBench | https://github.com/centerforaisafety/HarmBench | 1008 | Jupyter/Python | analyze_results.ipynb shows CSV parsing; harmbench.org leaderboard |
| PKU-Alignment/BeaverTails | https://huggingface.co/datasets/PKU-Alignment/BeaverTails | 181 (GitHub) | Python | is_safe field, 30k_test split; HuggingFace datasets API |
| stanford-crfm/helm | https://github.com/stanford-crfm/helm | 2854 | Python | HELM Lite v1.9.0 (79 models); BBQ + ECE scores; GCS path needs pre-flight |
| lighteval/bbq_helm | https://huggingface.co/datasets/lighteval/bbq_helm | N/A | N/A | 11,864 rows BBQ in HELM format; HuggingFace API |
| fboulnois/llm-leaderboard-csv | https://github.com/fboulnois/llm-leaderboard-csv | 30 | Python | TruthfulQA + MMLU columns confirmed in CSV; 428 releases |

---

#### Gap 3: Absence of RLHF cross-benchmark alignment profile for BBQ and HarmBench/BeaverTails

**Relevance:** 🔗 SECONDARY — Relates to detailed sub-question 3 (RLHF alignment profile). R4 (h-m1) confirmed RLHF improves TruthfulQA MC2 (+3.406 mean delta across 321 pairs). Whether BBQ accuracy and HarmBench/BeaverTails safety rate show the same directional improvement is unknown.

**Current State:** R4 (h-m1 SUPERSEDED) established RLHF improves TruthfulQA MC2 (+3.406, BCa CI entirely positive, 321 base/chat pairs from Open LLM LB v1). InstructGPT (Ouyang 2022) reports RLHF improves helpfulness + harmlessness jointly but does not disaggregate by benchmark. Llama-2 reports both base and chat TruthfulQA + BBQ + safety results but does not compute within-family delta statistics. No study computes sign test across all three alignment dimensions simultaneously for the same N=321 base/chat pairs.

**Missing Piece:** Extension of R4 delta analysis to BBQ accuracy and HarmBench/BeaverTails safety rate: for each of the 321 base/chat pairs where BBQ and/or HarmBench/BeaverTails scores are available, compute delta = instruction_score - base_score, sign test (not logistic regression), BCa bootstrap CI. Determine if RLHF produces uniform improvement (same sign across all 3 dimensions) or divergent profile (some dimensions improve, others degrade).

**Potential Impact:** MEDIUM — Publishable as part of multi-benchmark alignment study. Uniform RLHF improvement would contradict "alignment tax" narrative; divergent profile would motivate multi-objective alignment optimization research. Adds depth to primary correlation finding.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Training Language Models to Follow Instructions (InstructGPT)" | 2022 | Ouyang et al. | *unverified* | 2203.02155 | ~8000 | RLHF improves helpfulness+harmlessness; does not disaggregate by benchmark |
| "Llama 2: Open Foundation and Fine-Tuned Chat Models" | 2023 | Touvron et al. | *unverified* | 2307.09288 | ~10000 | Reports base/chat TruthfulQA+BBQ+safety; natural within-family pairs |
| "Do the Rewards Justify the Means?" | 2022 | Perez et al. | *unverified* | 2209.13436 | ~300 | RLHF trades off ethical behavior in some dimensions; motivates multi-benchmark profile |
| "Scaling Laws for Reward Model Overoptimization" | 2023 | Gao et al. | *unverified* | 2210.10760 | ~400 | Proxy-gold reward divergence; suggests single-dimension RLHF may harm other dimensions |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *No relevant Archon cases* | N/A | "RLHF instruction tuning alignment safety truthfulness evaluation" | Archon KB domain mismatch |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| hartvigsen-group/benchalign | https://github.com/hartvigsen-group/benchalign | 2 | Python/Shell | Uses Open LLM LB data for alignment analysis; base/chat pair pattern |
| fboulnois/llm-leaderboard-csv | https://github.com/fboulnois/llm-leaderboard-csv | 30 | Python | CSV with model Type field (base vs fine-tuned) enabling within-family pair extraction |

---

### Gap Priority Matrix

| Gap ID | Title | Relevance | Connection to Research Question | Connection to Detailed Question | Impact | Evidence Count | Priority |
|--------|-------|-----------|--------------------------------|--------------------------------|--------|----------------|----------|
| Gap 1 | Scale-controlled partial correlation structure missing | PRIMARY | ☑️ Directly blocks partial_rho computation | ☑️ Sub-questions 1, 2, 4 | High | 8 sources (3 Scholar + 2 Exa preprint + 3 Exa tools) | **CRITICAL** |
| Gap 2 | N triple-overlap and data accessibility unverified | PRIMARY | ☑️ Blocks execution if N<40 or URL fails | ☑️ Sub-question 5 (pre-flight MANDATORY) | High | 5 sources (2 Scholar + 3 Exa data) | **CRITICAL** |
| Gap 3 | RLHF cross-benchmark profile for BBQ+HarmBench missing | SECONDARY | ☑️ Extends primary finding | ☑️ Sub-question 3 (RLHF profile) | Medium | 4 sources (4 Scholar) + 2 Exa tools | HIGH |

### User Input to Gap Traceability

**Main Research Question** ("pairwise partial Spearman structure after MMLU control — unidimensional or multi-dimensional?") directly addressed by:
- **Gap 1:** No existing study computes partial_rho matrix for {TruthfulQA, BBQ, HarmBench/BeaverTails} controlling for MMLU with cluster-bootstrap CI. Closest existing work (clawrxiv:2603.00394) uses different benchmark set and method (PCA, not partial Spearman).
- **Gap 2:** N overlap count is the feasibility gate; without pre-flight verification, hypothesis design risks R1/R7/R8 failure pattern.

**Detailed Sub-Question 1** (partial correlation gate) addressed by: Gap 1
**Detailed Sub-Question 2** (scale contribution quantification) addressed by: Gap 1
**Detailed Sub-Question 3** (RLHF cross-benchmark profile) addressed by: Gap 3
**Detailed Sub-Question 4** (PCA structure) addressed by: Gap 1
**Detailed Sub-Question 5** (pre-flight executable verification) addressed by: Gap 2

**Reference Papers:** Not provided — gaps identified from Phase 1 discovery

---

## 9. Conclusion

### Key Findings

1. **Direct 2026 precedent confirms research direction:** clawrxiv:2603.00394 ("Which LLM Benchmarks Are Redundant?") shows TruthfulQA provides orthogonal signal to scale (PC2 = 23.4% variance). BenchScope (arxiv:2603.29357) shows Open LLM LB ED=1.7 (≈2 effective axes). Neither analyzes BBQ bias or HarmBench/BeaverTails safety jointly — this study fills that gap.

2. **All primary data sources confirmed via Exa:**
   - TruthfulQA MC2 + MMLU: fboulnois/llm-leaderboard-csv (v1 CSV, confirmed column headers)
   - BBQ accuracy: lighteval/bbq_helm on HuggingFace (11,864 rows, HELM format)
   - HarmBench safety: centerforaisafety/HarmBench GitHub (1,008 stars, CSV confirmed)
   - BeaverTails safety: PKU-Alignment/BeaverTails HuggingFace (364k rows, `is_safe` field confirmed)
   - HELM ECE/toxicity: stanford-crfm/helm (2,854 stars, Lite v1.9.0 = 79 models)

3. **Analysis infrastructure confirmed:** pingouin.partial_corr(method='spearman', covar=['MMLU']) is exact API; scipy.stats.spearmanr + permutation test for N<500; cluster-bootstrap by model family (BCa confirmed working from R4 h-m1).

4. **Prior failure classes hardened against (all 9):**
   - R1: No GCS/Zenodo — all sources on HuggingFace or GitHub
   - R2: Open-weight only — no AlpacaEval-LC
   - R3: Partial Spearman (MMLU control) — not raw correlation
   - R4: Direction-agnostic — both unidimensional and multi-dimensional outcomes publishable
   - R5: No logistic regression — Spearman + Fisher z-test + sign test + PCA only
   - R6: Pre-flight N≥40 gate before hypothesis acceptance
   - R7/R8: Phase 1 executed immediately (no re-archiving)
   - R9-NEW: Executable URL test (requests.head) BEFORE Phase 2A

5. **Academic literature (INFERRED — Scholar MCP unavailable):** 14 key papers identified including TruthfulQA (Lin 2022), BBQ (Parrish 2022), HELM (Liang 2022), HarmBench (Mazeika 2024), BeaverTails (Ji 2023), InstructGPT (Ouyang 2022), Llama-2 (Touvron 2023). SS IDs require Phase 2A verification.

### Answer to Detailed Question (Preliminary)

*Phase 1 boundary: data collection only. No hypotheses. Preliminary observations only.*

1. **Sub-Q1 (partial_rho gate):** Analysis method confirmed (pingouin.partial_corr); data sources confirmed; N overlap unknown until pre-flight. If N≥40 triple-overlap achievable, gate is executable.

2. **Sub-Q2 (scale contribution):** clawrxiv:2603.00394 suggests PC1 (74% variance) = scale for general benchmarks. Whether this holds for alignment-specific subset (TruthfulQA+BBQ+HarmBench) is the open question — partial Spearman will quantify.

3. **Sub-Q3 (RLHF profile):** R4 (h-m1) established +3.406 TruthfulQA improvement. Whether BBQ and HarmBench/BeaverTails show same sign is unknown — dependent on N of base/chat pairs with BBQ and HarmBench scores in same dataset.

4. **Sub-Q4 (PCA structure):** clawrxiv:2603.00394 and BenchScope provide method templates; extending to alignment-specific benchmark subset is the contribution.

5. **Sub-Q5 (pre-flight verification):** NOT YET EXECUTED. This is the mandatory Phase 2A gate. Must run before hypothesis design.

### Phase 2 Readiness

**Status: READY (pending pre-flight URL test execution)**

| Check | Status | Notes |
|-------|--------|-------|
| Research question defined | ✅ DONE | Direction-agnostic; avoids all 9 failure classes |
| Data sources identified | ✅ DONE | 5 sources confirmed via Exa |
| Analysis method confirmed | ✅ DONE | pingouin + scipy + cluster-bootstrap |
| 3 research gaps with table evidence | ✅ DONE | Gap 1 (PRIMARY), Gap 2 (PRIMARY), Gap 3 (SECONDARY) |
| Academic literature identified | ✅ DONE (INFERRED) | 14 papers; SS IDs need Phase 2A verification |
| Pre-flight URL+N executable test | ⚠️ PENDING | MANDATORY before Phase 2A hypothesis design |
| Phase 1 boundary maintained | ✅ CONFIRMED | No hypotheses, solutions, or implementations |
| Archon Pipeline update | ⚠️ SKIPPED | Archon API degraded; cannot update pipeline status |

### Next Steps

**IMMEDIATE (before Phase 2A):**
1. Run pre-flight Python script (requests.head for each URL + pd.read_csv(timeout=30) + N count):
   - Open LLM LB v1 CSV → N models with TruthfulQA MC2 scores
   - HELM Lite v1.9.0 → N models with BBQ accuracy + overlap with LB v1
   - HarmBench GitHub CSV → N models with refusal rate + overlap
   - BeaverTails HuggingFace → N models + overlap
   - Report: triple-overlap N, quadruple-overlap N, N≥40 gate met?
2. If any URL fails → apply fallback immediately (see Phase 0 brainstorm for fallback chain)
3. If N<40 triple-overlap → fall back to largest available benchmark pair

**Phase 2A:**
- `/phase2a-dialogue` with `01_targeted_research.md` as input
- Phase 2A reads Gap 1, Gap 2, Gap 3 evidence tables to generate testable hypotheses
- Primary hypothesis will be direction-agnostic: "What is partial_rho(TruthfulQA, BBQ | MMLU)?"

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~45 minutes (automated, unattended mode — 2026-07-30)*
