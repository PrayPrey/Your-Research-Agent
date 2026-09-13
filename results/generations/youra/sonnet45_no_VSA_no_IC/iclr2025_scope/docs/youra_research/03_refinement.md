# Phase 2A: Refinement Summary

## Metadata

- **Generated at**: 2026-08-20T08:30:00Z
- **Workflow**: phase2a-dialogue (Self-Contained Tikitaka Loop)
- **Architecture**: Independent Controller Ablation (Claude self-play)
- **Gap ID**: gap1_rag_aware_cache
- **Gap Title**: RAG-Aware Cache Management Strategies
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7 exchanges (converged)

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 7

**Convergence Reason**: All convergence criteria met at Exchange 7 - specific claim formulated with Under-If-Then-Because structure, mechanism explained via 4-step causal chain, 3 testable predictions with clear falsifiers, novelty articulated as first RAG-conditioned cache analysis, feasibility validated (no fundamental barriers, 25 GPU-hour budget), major objections addressed via diversity-aware refinement.

### Key Insights

1. **Unexploited Structure**: RAG creates semantic structure (query vs passage vs generated tokens) that current uniform cache methods (H2O, StreamingLLM) ignore despite production deployments (Perplexity, GitHub Copilot).

2. **Diversity Preserves Evidence**: Low-relevance passages might provide critical contrastive/negative evidence. Diversity-aware scoring (MMR principle) addresses this by retaining diverse passages, not just high-relevance ones.

3. **Query Complexity Matters**: Simple queries show query-token attention concentration (anchor hypothesis), but complex/ambiguous queries spread attention across passages. Tiered eviction must adapt to query complexity.

4. **Risk Mitigation via Pilots**: Three-tier pilot sequence (attention analysis → single-hop → multi-hop) validates assumptions cheaply before expensive full experiment, avoiding open-ended optimization trap from prior failures (h-e1 PARTIAL).

### Breakthrough Moments

- **Exchange 1 (Dr. Nova)**: Identified tiered provenance eviction (query > high-relevance > low-relevance > generated) as novel approach exploiting retrieval metadata that H2O/StreamingLLM discard.

- **Exchange 3 (Dr. Sage)**: Confirmed real gap - no prior work analyzed cache strategies *conditioned on* retrieval metadata, despite 878-citation H2O paper and production RAG systems. Contribution is the principle (provenance predicts utility), not just application.

- **Exchange 5 (Dr. Ally)**: Synthesized hypothesis + three-tier pilot sequence, transforming open-ended idea into controlled measurement study with clear success criteria (ρ > 0.3, ≥5% gain, ≥10% gain).

- **Exchange 7 (Dr. Nova)**: Diversity-aware refinement addressed Prof. Rex's negative evidence concern (low-relevance passages might be important), achieving convergence by adding MMR-inspired diversity scoring to tiered eviction.

---

## Final Hypothesis

### Title

**Provenance-Aware KV Cache Management for RAG-Based Long-Context QA**

### Core Claim (Under-If-Then-Because)

Under RAG-based long-context QA tasks (LongBench multi-doc QA, 8k-32k tokens), **if** we implement provenance-aware KV cache eviction with diversity-aware scoring (query tokens prioritized → diverse high-relevance passages → diverse low-relevance passages for contrastive evidence → redundant passages evicted), **then** answer accuracy at restrictive cache budgets (10-25% retention) will improve by ≥10% relative to uniform eviction baselines (H2O, StreamingLLM), **because** retrieval relevance scores and passage diversity jointly predict attention concentration and reasoning utility during answer generation.

### Mechanism (4-Step Causal Chain)

1. **Relevance-Attention Correlation**: Retrieval relevance scores correlate with attention concentration during answer generation (extends H2O finding that attention weights predict token importance). Validated via Pilot 1 attention analysis (target Spearman ρ > 0.3).

2. **Diversity Preserves Contrastive Evidence**: Diverse passage retention (measured by embedding distance or entity non-overlap) preserves contrastive/negative evidence needed for multi-hop reasoning. Adapts MMR (Maximal Marginal Relevance) principle from information retrieval.

3. **Query-Anchoring Stratified by Complexity**: Query tokens serve as attention anchors for simple/specific queries but not complex/ambiguous queries. Stratified validation in Pilot 1 by query complexity (word count, entity density).

4. **Integrated Provenance Policy**: Synthesizes relevance + diversity + query complexity into tiered eviction policy (Tier 0: query + top-1 passage, Tier 1: diverse high/low-relevance passages via MMR, Tier 2: redundant passages) to outperform uniform baselines.

### Key Tension

Diversity heuristic (embedding distance + entity overlap) might miss temporal or causal multi-hop dependencies where passages are semantically dissimilar but logically connected (e.g., "Event in 1990" + "Policy in 1991" for causation question). Mitigation: qualitative failure analysis + full cache budget range (10-75%) testing.

---

## Predictions

### P1 (Primary - Accuracy Gain)

**Statement**: Provenance-aware eviction achieves ≥10% relative accuracy gain at 25% cache budget on LongBench multi-doc QA vs H2O baseline.

**Test Method**: Compare answer accuracy (exact match or F1) between ProvenanceCache and H2O at 25% retention budget, averaged across LongBench multi-doc QA subset, stratified by question type (single-hop vs multi-hop).

**Success Criterion**: Relative accuracy improvement ≥10% with statistical significance (two-tailed t-test, p < 0.05, n ≥ 100 questions).

**Falsification**: If accuracy improvement < 5% or p ≥ 0.05, provenance-awareness provides no practical benefit at realistic budgets.

### P2 (Diversity Contribution)

**Statement**: Diversity-aware scoring outperforms pure relevance-based scoring on multi-hop questions by ≥5% accuracy.

**Test Method**: Ablation study comparing ProvenanceCache with diversity (full) vs without diversity (relevance-only) on multi-hop QA subset.

**Success Criterion**: Accuracy gain ≥5% on multi-hop questions, demonstrating diversity preserves contrastive evidence.

**Falsification**: If no accuracy difference or diversity version performs worse, diversity heuristic is ineffective or harmful.

### P3 (Mechanism Validation)

**Statement**: Retrieval scores correlate moderately with attention weights (Spearman ρ > 0.3) during answer generation.

**Test Method**: Pilot 1 attention analysis - measure attention weights from generated tokens to retrieved passage tokens, compute correlation with retrieval relevance scores.

**Success Criterion**: Spearman ρ > 0.3 for both BM25 and semantic retriever (DPR/Contriever).

**Falsification**: If ρ ≤ 0.3 or negative correlation, retrieval scores do not align with LLM attention patterns - provenance hypothesis invalidated.

---

## Novelty

**Preserved Novelty**: First analysis of KV cache strategies conditioned on retrieval provenance metadata (query vs passage vs generated tokens). Exploits semantic structure in RAG that uniform methods ignore.

**Key Innovation**: Diversity-aware provenance scoring synthesizes retrieval relevance + passage diversity + query complexity into unified eviction policy, addressing both efficiency (via tiering) and robustness (via diversity for contrastive evidence).

**Differentiation from Prior Work**:

- **H2O (Zhang et al., NeurIPS 2023)**: Uses uniform attention-based eviction without retrieval-awareness. ProvenanceCache augments H2O with tiered eviction based on token provenance + retrieval metadata.

- **StreamingLLM (Xiao et al., ICLR 2024)**: Uses fixed sliding window + attention sinks. ProvenanceCache dynamically prioritizes based on retrieval context, not just recency.

- **LongBench (Bai et al., ACL 2024)**: Evaluated models on static long documents. ProvenanceCache targets RAG scenarios with dynamic retrieval metadata.

---

## Experimental Design

### Dataset

**LongBench Multi-Doc QA Subset** - Standard benchmark (1563 citations, ACL 2024) from THUDM/LongBench (1.2K⭐, MIT license). Provides multi-doc QA requiring retrieval-like reasoning. Avoids custom benchmark creation. Enables single-hop vs multi-hop stratification for ablation analysis.

### Model

**Llama-2-7B** or similar open-weight long-context model from HuggingFace. Open-weight enables attention weight extraction for Pilot 1 validation. 7B scale balances compute feasibility with representativeness.

### Baselines

1. **FullKV**: No eviction (upper bound accuracy, high memory)
2. **H2O**: Uniform attention-based heavy-hitter eviction (primary comparison baseline)
3. **StreamingLLM**: Sliding window + attention sinks (architectural baseline)
4. **Random Eviction**: Uniform random token eviction (lower bound control)

### Three-Tier Pilot Sequence

**Pilot 1 - Attention Analysis (1-2 GPU-hours)**:
- Measure attention weights: generated tokens → query vs passage tokens
- Compute correlation: retrieval scores vs attention weights
- Stratify by query complexity and answer correctness
- Success criterion: Spearman ρ > 0.3 for both BM25 and semantic retriever
- Abort if ρ ≤ 0.3 (relevance-attention assumption breaks)

**Pilot 2 - Single-Hop Provenance Caching (5-8 GPU-hours)**:
- Implement tiered eviction on single-hop QA subset (controlled setting, no multi-hop complexity)
- Compare: ProvenanceCache vs H2O vs FullKV
- Success criterion: ≥5% accuracy gain at 25% cache budget
- Validates tiered eviction before adding diversity complexity

**Full Experiment - Multi-Hop + Hybrid Strategy (15-20 GPU-hours)**:
- Add diversity-aware co-retention scoring for multi-hop questions
- Test on full LongBench multi-doc QA
- Baselines: FullKV, H2O, StreamingLLM, Random eviction
- Cache budgets: 10%, 25%, 50%, 75% (Pareto frontier analysis)
- Success criterion: ≥10% relative accuracy gain at 10-25% budgets, robust across question types, p < 0.05

**Total Compute**: ~25 GPU-hours (reasonable for measurement study, avoids open-ended optimization trap)

---

## Limitations

### Scope Boundaries

**Applies to**:
- RAG-based long-context QA (8k-32k tokens) with retrieval metadata available
- Multi-doc QA requiring reasoning over retrieved passages
- Memory-constrained settings requiring KV cache eviction (10-50% budgets)
- Open-weight models (Llama, MPT) where attention weights can be extracted

**Does NOT apply to**:
- Static long-document understanding without retrieval (no provenance signals)
- Short-context tasks (< 2k tokens) where full KV retention is feasible
- Closed-API models (GPT-4, Claude) with inaccessible attention weights
- Real-time streaming inference requiring pre-context cache decisions

### Known Limitations

1. **Diversity Heuristic**: Embedding distance + entity overlap may miss temporal/causal multi-hop dependencies (acknowledged tension, qualitative failure analysis planned).

2. **Retriever Dependence**: Requires competent retriever baseline (garbage-in-garbage-out if retrieval is poor). Mitigated via multi-retriever validation (BM25 + DPR/Contriever).

3. **Dataset Specificity**: LongBench multi-doc QA may not represent all RAG use cases (e.g., code QA, scientific literature search). Secondary benchmark testing (NarrativeQA) if compute budget allows.

4. **Metadata Availability**: Assumes retrieval metadata (relevance scores, passage boundaries) is available and accurate. Production RAG systems must instrument this.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met (specific, mechanism, predictions, novelty, feasibility, objections addressed) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (diversity heuristic limitation acknowledged with mitigation) |

---

## Next Steps (Phase 2B)

Phase 2B will parse this hypothesis into sub-hypotheses:

- **H-E1 (Existence)**: Relevance-attention correlation exists (Pilot 1 validation)
- **H-M1-M4 (Mechanism)**: Each step of 4-step causal chain
- **H-C1 (Condition)**: Query complexity stratification (simple vs complex queries)
- **H-D1 (Diversity)**: Passage diversity ablation (with vs without)

Phase 2B will also generate verification protocols for each sub-hypothesis and roadmap to Phase 3 implementation planning.
