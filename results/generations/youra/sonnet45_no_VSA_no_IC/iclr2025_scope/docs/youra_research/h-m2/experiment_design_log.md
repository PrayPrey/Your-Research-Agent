# Experiment Design Log — H-M2

**Generated**: 2026-08-20  
**Hypothesis**: H-M2 (Diversity-aware MMR scoring outperforms pure relevance eviction by ≥5% accuracy)  
**Design Tier**: 1.5 (Controlled experiment with ablation studies)

---

## Design Rationale

### Dataset Selection: HotpotQA Bridge Questions

**Decision**: Use HotpotQA dev set (distractor setting) filtered for `type: "bridge"` questions.

**Rationale**:
1. **Multi-hop requirement**: Bridge questions require reasoning across 2+ supporting documents — diversity-aware passage retention is critical for success
2. **Established benchmark**: HotpotQA is the standard multi-hop QA dataset, used in H2O paper and retrieval-augmented QA literature
3. **Large sample size**: 7,405 bridge questions provide statistical power for t-test (>100 minimum)
4. **Supporting facts annotations**: Ground-truth passage labels enable interpretability analysis
5. **Distractor setting**: 10 paragraphs per question (8 distractors + 2 supporting) stress-tests cache eviction under noise

**Alternatives Considered**:
- **2WikiMultiHopQA**: More complex (comparison/inference/compositional questions), but smaller community adoption — reserved as secondary validation dataset
- **MuSiQue**: Compositional multi-hop dataset, but questions require 2-4 hops (variable complexity complicates comparison)
- **StrategyQA**: Implicit reasoning questions, but lacks passage-level annotations for provenance metadata

### Baseline Selection: ProvenanceCache-RelevanceOnly (Ablation)

**Decision**: Use tiered eviction with pure relevance scores (no diversity penalty) as primary baseline, rather than H2O alone.

**Rationale**:
1. **Isolates diversity mechanism**: Relevance-only variant shares provenance metadata infrastructure with ProvenanceCache-Full — only difference is MMR diversity scoring
2. **Fairer comparison**: H2O lacks provenance metadata AND diversity-aware scoring (two confounds), relevance-only baseline controls for metadata
3. **Ablation validity**: If diversity variant fails, relevance-only tiering is still novel vs H2O (provenance metadata contribution)
4. **H2O still included**: External baseline for provenance metadata validation (reuse H-M1 results)

### MMR Formula: λ=0.5 Balanced Tradeoff

**Decision**: Use λ=0.5 for relevance-diversity tradeoff in MMR scoring.

**Rationale**:
1. **MMR literature default**: Carbonell & Goldstein (1998) original MMR paper uses λ=0.5 for document diversification
2. **Balanced exploration**: λ=0.5 weights relevance and diversity equally — avoids over-penalizing relevance (λ<0.5) or collapsing to relevance-only (λ→1.0)
3. **Ablation coverage**: Lambda sweep (0.3, 0.5, 0.7, 0.9) tests sensitivity to tradeoff parameter

**Alternatives Considered**:
- **λ=0.7 (relevance-biased)**: Safer default, but may not surface diversity benefit
- **Adaptive lambda**: Per-query lambda tuning (complex, requires meta-learning)

### Diversity Metric: Embedding Cosine Similarity

**Decision**: Use Contriever passage embeddings + cosine similarity for diversity computation.

**Rationale**:
1. **Semantic diversity**: Embeddings capture meaning overlap better than lexical metrics (entity/token Jaccard)
2. **Retriever reuse**: Contriever already used for relevance scoring (H-E1 validation) — embeddings available for free
3. **Sentence-transformers API**: Cosine similarity computation built-in, efficient for pairwise distances

**Concerns (Prof. Rex)**: Embedding similarity may miss temporal/causal dependencies in multi-hop reasoning (e.g., "Obama born 1961" vs "Obama elected 2008" are semantically similar but temporally distinct).

**Mitigation**: Ablation with entity overlap metric (named entities capture temporal/causal links better than embeddings).

### Cache Budget: 25% of Full Context

**Decision**: Use 25% cache budget (500 tokens / 2,000 full context) for all conditions.

**Rationale**:
1. **H2O paper standard**: 25% cache budget is the primary constraint setting in H2O experiments
2. **Stress test**: Low budget forces hard eviction tradeoffs — diversity benefit should surface here
3. **Realistic constraint**: 25% mimics memory-constrained serving (edge devices, multi-tenant inference)

**Budget Allocation** (Tier breakdown):
- **Tier 0 (query tokens)**: 10% (50 tokens) — always retained, no eviction
- **Tier 1 (high-relevance passages)**: 60% (300 tokens, ~1.5 passages) — diverse high-quality evidence
- **Tier 2 (low-relevance passages)**: 30% (150 tokens, ~0.75 passages) — diverse contrastive evidence

**Rationale**: 60/30 split prioritizes high-relevance passages but preserves budget for diverse low-relevance evidence (contrastive reasoning).

**Ablation**: Budget allocation sweep (50/40, 60/30, 70/20) tests allocation sensitivity.

### Success Criterion: ≥5% Relative Accuracy Gain

**Decision**: Define hypothesis success as ≥5% relative F1 gain over relevance-only baseline.

**Rationale**:
1. **Practical significance**: 5% relative gain (e.g., 58% → 61% F1) is publishable improvement in QA literature
2. **Statistical power**: With 7,405 samples, paired t-test detects 2-3% absolute gain at p<0.05
3. **Falsifiability**: If gain < 5%, fall back to relevance-only tiering (simpler, still novel)

**Threshold Justification**: H2O paper reported 3-5% F1 gains over uniform eviction baselines — diversity mechanism should match or exceed this.

---

## Design Decisions Summary

| **Decision Point** | **Choice** | **Rationale** |
|-------------------|-----------|--------------|
| Dataset | HotpotQA bridge questions | Multi-hop reasoning requires diverse passage retention |
| Primary baseline | ProvenanceCache-RelevanceOnly | Isolates diversity mechanism (fair ablation) |
| External baseline | H2O (from H-M1) | Validates provenance metadata contribution |
| MMR lambda | 0.5 (balanced) | MMR literature default, ablation sweep tests sensitivity |
| Diversity metric | Embedding cosine similarity | Semantic diversity, retriever reuse |
| Cache budget | 25% (500 tokens) | H2O paper standard, stress-tests eviction |
| Tier allocation | 60% Tier 1 / 30% Tier 2 | Prioritize high-relevance, preserve diverse contrastive evidence |
| Success criterion | ≥5% relative F1 gain | Publishable improvement threshold |

---

## Implementation Search Strategy (Next Step)

Phase 2C requires Archon KB search for implementation examples to inform Phase 3 code design.

**Search Queries** (to run in `implementation_search_log.md`):
1. `rag_search_code_examples("MMR diversity scoring", match_count=5)` — MMR algorithm implementations
2. `rag_search_code_examples("Contriever passage embeddings", match_count=5)` — Sentence-transformers API usage
3. `rag_search_code_examples("KV cache eviction policy", match_count=5)` — Cache management patterns
4. `rag_search_code_examples("HotpotQA evaluation F1 score", match_count=5)` — Official evaluation script patterns
5. `rag_search_knowledge_base("tiered eviction cache implementation", match_count=5)` — Multi-tier cache design patterns

**Expected Outcomes**: Code snippets for MMR greedy selection, embedding cache management, tiered eviction state machine.

---

## Phase 3 Readiness

All design decisions finalized. Experiment brief complete (02c_experiment_brief.md).

**Next Steps**:
1. Complete implementation search log (query Archon KB)
2. Proceed to Phase 3 (PRD, Architecture, Logic, Config generation)

**Estimated Phase 3 Duration**: 2-3 hours (agent orchestration for 4 parallel design documents)
