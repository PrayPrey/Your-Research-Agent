# Phase 2C: Experiment Design Brief — H-M2

**Generated**: 2026-08-20  
**Hypothesis ID**: h-m2  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Prerequisites**: h-m1 (completed)

---

## Hypothesis Statement

**H-M2**: Diversity-aware scoring (MMR-inspired passage selection) outperforms pure relevance-based eviction by ≥5% accuracy on multi-hop questions.

---

## Experiment Overview

### Objective
Validate that diversity-aware passage selection improves multi-hop QA performance over pure relevance-based eviction by comparing two ProvenanceCache variants:
- **ProvenanceCache-Full**: Tiered eviction with MMR-inspired diversity scoring
- **ProvenanceCache-RelevanceOnly**: Tiered eviction with pure relevance scores (no diversity penalty)

### Success Criterion
≥5% relative accuracy gain on multi-hop questions with diversity-aware scoring vs relevance-only baseline.

### Falsifier
If diversity variant performs ≤ relevance-only variant OR gain < 5%, fall back to relevance-only tiering (simpler, still novel).

---

## Dataset Specification

### Primary Dataset: HotpotQA Multi-Hop Subset

**Source**: [HotpotQA](https://hotpotqa.github.io/) dev set (distractor setting)  
**Download URL**: http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json  
**Type**: standard  
**License**: CC BY-SA 4.0

**Subset Selection**:
- Filter for `type: "bridge"` questions (multi-hop reasoning required)
- Use full dev set: ~7,405 bridge questions
- Evaluation split: Full 7,405 samples (statistically meaningful for t-test)

**Dataset Characteristics**:
- Multi-hop bridge questions requiring 2+ supporting documents
- Average context length: ~2,000 tokens (10 paragraphs × ~200 tokens)
- Answer types: span extraction (entities, dates, short phrases)
- Supporting facts annotated for interpretability

**Rationale**: HotpotQA bridge questions require reasoning across multiple paragraphs, making diversity-aware passage retention critical. Single-hop questions would not test the diversity hypothesis.

### Alternative Dataset (Validation): 2WikiMultiHopQA

**Source**: [2WikiMultiHopQA](https://github.com/Alab-NII/2wikimultihop)  
**Download**: HuggingFace `ohjoonhee/2WikiMultihopQA` (dev split)  
**Type**: standard  
**Sample Size**: 12,576 dev samples

**Use Case**: Secondary validation if HotpotQA results are inconclusive. 2WikiMultiHopQA provides explicit evidence triples and 4 question types (comparison, inference, compositional, bridge-comparison).

---

## Model Specification

### Base LLM
**Model**: Llama-2-7B-hf  
**HuggingFace ID**: `meta-llama/Llama-2-7b-hf`  
**Precision**: FP16 (mixed precision for memory efficiency)  
**Context Window**: 4096 tokens (pretrained)  
**License**: Llama 2 Community License

**Rationale**: 
- Llama-2-7B is the standard model in KV cache literature (H2O paper used OPT-6.7B and Llama-2-7B)
- 7B parameter size balances compute feasibility with realistic inference behavior
- FP16 precision matches H2O baseline experiments

### Retriever
**Model**: Contriever (sentence-transformers/contriever-base-msmarco)  
**Embedding Dimension**: 768  
**Purpose**: Generate passage relevance scores and embeddings for diversity computation

**Rationale**: 
- H-E1 validation showed Contriever relevance correlates with attention (ρ=0.612)
- Contriever provides both relevance scores AND embeddings needed for MMR diversity
- Sentence-transformers API simplifies embedding distance computation

---

## Experimental Conditions

### Baseline Methods

1. **ProvenanceCache-RelevanceOnly** (ablation baseline)
   - Tiered eviction: query tokens > high-relevance passages > low-relevance passages
   - Eviction within each tier: lowest Contriever relevance score evicted first
   - No diversity penalty applied
   - Cache budget: 25% of full context

2. **H2O** (external baseline, from H-M1)
   - Uniform attention-based eviction (no provenance metadata)
   - 25% cache budget (matches ProvenanceCache)
   - Implementation: FMInference/H2O repository

3. **FullKV** (upper bound)
   - No eviction, full KV cache retained
   - Provides oracle accuracy ceiling

### Target Method

**ProvenanceCache-Full** (diversity-aware)
- Tiered eviction: query tokens > diverse high-relevance > diverse low-relevance
- Diversity scoring: MMR-inspired formula per tier

**MMR Diversity Formula**:
```
score(passage_i) = λ · relevance(passage_i) - (1-λ) · max_similarity(passage_i, selected_passages)

Where:
- relevance(passage_i) = Contriever cosine similarity to query
- max_similarity = max cosine distance between passage_i embedding and already-retained passages
- λ = 0.5 (balanced relevance + diversity, per MMR literature default)
```

**Diversity Computation**:
1. Embed each passage using Contriever encoder (reuse from retrieval)
2. For each eviction decision within a tier:
   - Compute MMR score for all candidate passages
   - Evict passage with lowest MMR score (redundant with high-relevance passages)
3. Sentence-transformers cosine similarity for embedding distance

**Implementation Strategy**:
- Tier 0 (query tokens): No eviction, always retained
- Tier 1 (high-relevance passages, top-k by Contriever score):
  - Sort passages by MMR score descending
  - Retain top-N diverse passages within budget
  - Evict redundant passages (low MMR score)
- Tier 2 (low-relevance passages):
  - Apply MMR within remaining budget
  - Preserve diverse contrastive evidence

---

## Hyperparameters

### Cache Budget
- **Target**: 25% of full context length
- **Full Context**: ~2,000 tokens (10 HotpotQA paragraphs)
- **Cache Size**: 500 tokens (~2.5 passages at 200 tokens each)

**Allocation**:
- Tier 0 (query tokens): 10% of budget (~50 tokens)
- Tier 1 (high-relevance diverse passages): 60% of budget (~300 tokens, ~1.5 passages)
- Tier 2 (low-relevance diverse passages): 30% of budget (~150 tokens, ~0.75 passages)

### MMR Parameters
- **Lambda (λ)**: 0.5 (balanced relevance + diversity)
- **Diversity Metric**: Cosine similarity on Contriever embeddings
- **Candidate Pool**: All passages within tier (no pre-filtering)

### Retrieval Parameters
- **Top-K Passages**: 10 (HotpotQA distractor setting provides 10 paragraphs)
- **Relevance Threshold**: None (use full ranking)

### Generation Parameters
- **Max New Tokens**: 32 (span extraction, short answers)
- **Temperature**: 0.0 (greedy decoding for reproducibility)
- **Top-p**: 1.0 (no nucleus sampling)

---

## Evaluation Metrics

### Primary Metric: Answer Accuracy
**Metric**: F1 score (token-level overlap between predicted and gold answer)  
**Computation**: HotpotQA official evaluation script (`hotpot_evaluate_v1.py`)  
**Aggregation**: Macro-average F1 over all bridge questions

**Why F1 over Exact Match**:
- F1 captures partial credit for span extraction (e.g., "Barack Obama" vs "Obama")
- Exact Match too brittle for multi-hop QA (H2O paper reported F1)

### Secondary Metrics

1. **Exact Match (EM)**: Binary correctness (predicted == gold answer)
2. **Diversity Coverage**: Unique passage count retained per question
3. **Embedding Distance**: Average cosine distance between retained passages
4. **Redundancy Rate**: % of retained passages with >0.8 cosine similarity to another retained passage

### Statistical Validation
- **Test**: Two-tailed paired t-test (ProvenanceCache-Full vs ProvenanceCache-RelevanceOnly)
- **Null Hypothesis**: No difference in F1 score between diversity-aware and relevance-only
- **Significance Level**: α = 0.05
- **Sample Size**: 7,405 bridge questions (>100 minimum for t-test validity)

---

## Ablation Studies

### Ablation 1: Lambda Sweep (λ ∈ {0.3, 0.5, 0.7, 0.9})
**Goal**: Test sensitivity of diversity-relevance tradeoff  
**Expectation**: λ=0.5 optimal (per MMR literature), λ=1.0 collapses to relevance-only baseline

### Ablation 2: Diversity Metric Comparison
**Variants**:
- Embedding cosine similarity (baseline)
- Entity overlap (Jaccard similarity on named entities)
- Lexical overlap (Jaccard similarity on tokens)

**Goal**: Validate that semantic embedding diversity outperforms surface-level diversity

### Ablation 3: Tier Budget Allocation
**Variants**:
- Current: 60% Tier 1 / 30% Tier 2 / 10% Query
- Balanced: 50% Tier 1 / 40% Tier 2 / 10% Query
- Relevance-heavy: 70% Tier 1 / 20% Tier 2 / 10% Query

**Goal**: Determine optimal allocation between high/low-relevance passage diversity

---

## Compute Budget

### Hardware Requirements
- **GPU**: 1× A100 40GB (preferred) or 1× V100 32GB
- **CPU**: 16 cores (for parallel passage embedding)
- **RAM**: 64GB
- **Storage**: 50GB (model weights + dataset cache)

### Estimated Runtime
- **Dataset Download**: 10 minutes
- **Model Download**: 15 minutes (Llama-2-7B + Contriever)
- **Preprocessing**: 1 hour (embed all passages, cache embeddings)
- **Inference**:
  - ProvenanceCache-Full: 8 hours (7,405 questions × 4 sec/question)
  - ProvenanceCache-RelevanceOnly: 8 hours
  - Total: 16 GPU-hours
- **Ablation Studies**: +12 GPU-hours (λ sweep + diversity metric variants)

**Total Compute**: ~28 GPU-hours (included in H-M1 Phase 4 allocation)

### Cost Estimate (Cloud GPU)
- A100 40GB: $2.50/hour × 28 hours = **$70**
- V100 32GB: $1.20/hour × 28 hours = **$33.60** (fallback)

---

## Implementation Details

### Code Structure
```
h-m2/
├── data/
│   ├── hotpotqa_dev_distractor.json      # Raw dataset
│   ├── hotpotqa_bridge_filtered.json     # Multi-hop subset
│   └── passage_embeddings_cache.pkl      # Precomputed Contriever embeddings
├── src/
│   ├── dataset_loader.py                 # HotpotQA filtering + preprocessing
│   ├── provenance_cache.py               # ProvenanceCache implementation
│   ├── mmr_diversity.py                  # MMR scoring logic
│   ├── baselines.py                      # H2O wrapper, FullKV baseline
│   ├── evaluation.py                     # F1/EM computation, t-test
│   └── run_experiment.py                 # Main orchestration script
├── configs/
│   ├── provenance_full.yaml              # ProvenanceCache-Full config
│   ├── provenance_relevance_only.yaml    # Ablation baseline config
│   └── ablation_lambda_sweep.yaml        # Lambda ablation configs
├── outputs/
│   ├── predictions_provenance_full.json  # Model predictions
│   ├── predictions_relevance_only.json
│   ├── metrics.json                      # F1, EM, diversity stats
│   └── statistical_tests.json            # t-test results
└── README.md                             # Experiment reproduction guide
```

### Key Dependencies
- `transformers==4.36.0` (Llama-2 support)
- `sentence-transformers==2.2.2` (Contriever embeddings)
- `torch==2.1.0` (CUDA 12.1)
- `datasets==2.14.0` (HuggingFace datasets)
- `scipy==1.11.0` (statistical tests)

### Reproducibility
- **Random Seed**: 42 (fixed across all runs)
- **Deterministic CUDA**: `torch.backends.cudnn.deterministic = True`
- **Checkpoint Saving**: Save predictions + intermediate states every 1,000 questions
- **Logging**: W&B experiment tracking (optional)

---

## Baseline Comparison Strategy

### H2O Baseline (from H-M1)
**Reuse Results**: H-M1 validation already ran H2O baseline at 25% cache budget on HotpotQA subset  
**Expected Performance**: ~58% F1 (extrapolated from H2O paper LongBench results)  
**Comparison**: ProvenanceCache-Full vs H2O validates provenance metadata superiority

### FullKV Upper Bound
**Expected Performance**: ~65% F1 (HotpotQA baseline model results)  
**Gap Analysis**: (FullKV F1 - ProvenanceCache F1) quantifies information loss from eviction

---

## Expected Outcomes

### Hypothesis Success (Diversity ≥ 5% gain)
- **ProvenanceCache-Full F1**: ≥61% (5% relative gain over 58% relevance-only)
- **Diversity Coverage**: ≥3 unique passages retained per question (vs 2.5 for relevance-only)
- **Redundancy Rate**: ≤20% (vs ≥40% for relevance-only)

**Interpretation**: Diversity-aware scoring preserves multi-faceted evidence needed for multi-hop reasoning.

### Hypothesis Failure (Diversity < 5% gain)
- **ProvenanceCache-Full F1**: ≤59% (no significant difference from relevance-only)
- **Diversity Coverage**: Similar to relevance-only (~2.5 passages)

**Interpretation**: Multi-hop questions do not benefit from diverse passage retention, either because:
1. High-relevance passages already cover diverse reasoning paths
2. Embedding-based diversity metric misses temporal/causal dependencies (Prof. Rex concern)
3. 25% cache budget insufficient to retain diverse low-relevance passages

**Fallback**: Relevance-only tiering (simpler, still novel vs H2O).

---

## Failure Modes & Mitigations

### Failure Mode 1: Embedding Diversity ≠ Reasoning Diversity
**Symptom**: Semantically dissimilar passages evicted, but they share critical causal/temporal links  
**Detection**: Qualitative analysis of evicted passages in failed questions  
**Mitigation**: Ablation with entity overlap diversity metric (entities capture temporal/causal links better than embeddings)

### Failure Mode 2: 25% Budget Too Small for Diversity
**Symptom**: Diversity-aware variant evicts high-relevance passages to fit diverse low-relevance passages  
**Detection**: Tier 1 retention rate < 80% in diversity variant  
**Mitigation**: Budget sweep ablation (30%, 35%, 40% cache budgets)

### Failure Mode 3: Lambda Miscalibration
**Symptom**: λ=0.5 over-penalizes relevance, retains low-quality diverse passages  
**Detection**: Diversity variant F1 drops below H2O baseline  
**Mitigation**: Lambda sweep ablation (λ=0.7, 0.8, 0.9 toward relevance)

---

## Qualitative Analysis Plan

### Case Study: Diversity Breakdown
**Sample**: 50 questions where diversity variant fails (low F1) but relevance-only succeeds  
**Analysis**:
1. Compare retained passages (diversity vs relevance-only)
2. Annotate passage relationships: temporal sequence, causal chain, contradictory evidence
3. Identify diversity heuristic breakdown patterns

**Reporting**: Examples in 04_validation.md with passage comparison tables

---

## Output Deliverables

1. **02c_experiment_brief.md** (this document)
2. **Predictions JSON**:
   - `predictions_provenance_full.json`: {question_id: {answer: str, supporting_facts: List}}
   - `predictions_relevance_only.json`
3. **Metrics JSON**:
   - F1, EM, diversity coverage, redundancy rate per condition
   - Statistical test results (t-statistic, p-value, effect size)
4. **Ablation Results**:
   - Lambda sweep: F1 vs λ curve
   - Diversity metric comparison table
   - Budget allocation heatmap
5. **Qualitative Analysis**:
   - 10 success cases (diversity wins)
   - 10 failure cases (diversity loses)
   - Pattern summary

---

## Experiment Tier

**Level**: 1.5 (Controlled experiment with ablation studies)  
**Complexity**: Medium  
- Standard dataset (HotpotQA) with established eval metrics
- Novel diversity scoring mechanism (MMR-inspired)
- Ablation studies require 4× inference runs (base + 3 ablations)

**Justification**: More complex than H-M1 pilot (requires MMR implementation + diversity metrics) but simpler than full system integration (H-M4).

---

## Phase 3 Preparation

**PRD Requirements**:
- MMR diversity scoring API specification
- Passage embedding cache interface
- Tiered eviction policy state machine

**Architecture Requirements**:
- ProvenanceCache class hierarchy (base + diversity-aware subclass)
- Embedding cache manager (lazy loading, memory-mapped)
- Evaluation harness (parallel inference, checkpoint recovery)

**Epic Tasks** (estimated):
1. Dataset preprocessing pipeline (filter bridge questions, embed passages)
2. MMR diversity module (cosine similarity, greedy selection)
3. ProvenanceCache-Full implementation (tiered eviction + MMR)
4. Evaluation harness (parallel inference, F1/EM computation)
5. Statistical analysis pipeline (t-test, effect size, visualization)
6. Ablation orchestration (lambda sweep, metric comparison, budget allocation)

**Total Estimated Subtasks**: ~25 (Medium complexity, manageable for Phase 3 decomposition)

---

## References

1. Zhang et al. (2023). H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models. NeurIPS.
2. Yang et al. (2018). HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering. EMNLP.
3. Carbonell & Goldstein (1998). The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries. SIGIR.
4. Ho et al. (2020). Constructing A Multi-hop QA Dataset for Comprehensive Evaluation of Reasoning Steps. COLING.
5. Izacard et al. (2021). Unsupervised Dense Information Retrieval with Contrastive Learning. TACL.

---

**Document Status**: READY FOR PHASE 3 IMPLEMENTATION PLANNING  
**Next Phase**: Phase 3 (PRD, Architecture, Logic, Config generation)  
**Estimated Phase 3 Duration**: 2-3 hours (agent orchestration for PRD/Architecture/Logic/Config)
