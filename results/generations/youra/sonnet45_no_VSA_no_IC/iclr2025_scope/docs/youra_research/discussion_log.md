# Phase 2A Discussion Log

**Architecture:** Self-Contained Tikitaka Loop (Independent Controller Ablation)
**Mode:** UNATTENDED (Self-Play)
**Generated:** 2026-08-20

---

## Previous Failure / Routing Context

**Source:** Phase 4 PARTIAL + LIMITATION_RECORDED (h-e1)

### Summary

H-E1 (Evolutionary Search for Non-Degenerate Routing Patterns) achieved PoC validation but left 7/9 implementation tasks incomplete. Core data pipeline (WikiTextDataset) and hybrid model architecture (Flash-Attention + Mamba) work correctly. Missing: training infrastructure (CandidateTrainer, GPUPool, NSGA-II integration), baseline runner, validation pipeline, visualization, and main CLI.

**Result:** LIMITATION_RECORDED (not routed) because methodology is sound — missing work is standard implementation, not design flaw. No fundamental blockers identified.

**Key Lesson:** Evolutionary search + multi-GPU orchestration = massive infrastructure scope. Avoid open-ended optimization requiring custom frameworks.

### Constraints for This Discussion

**MUST AVOID:**
- Open-ended optimization requiring custom frameworks (evolutionary search, hyperparameter tuning, architecture search)
- Approaches requiring synthetic/generated data or human evaluation
- New benchmarks, rubrics, or scoring frameworks
- Multi-GPU orchestration complexity at experiment core

**MUST PREFER:**
- Measurement studies using existing implementations
- Comparative analysis with standard benchmarks
- Hypotheses testable with existing datasets and evaluation protocols

---

## Research Gap Selection

**Selected Gap:** Gap 1 - RAG-Aware Cache Management Strategies (Priority 1)

**Current State:** General KV cache eviction (H2O, StreamingLLM) treats all tokens uniformly. No specialized caching for retrieved vs original context found.

**Missing Piece:** Cache management distinguishing retrieved document context, original user prompt, and generated response tokens.

**Impact:** HIGH - Directly addresses research sub-question 2 on balancing retrieved vs original context caching.

**Reference Papers:**
- LongBench (b31a5884, 1563 cit) - multi-doc QA, no RAG-specific analysis
- H2O (e586a4591, 878 cit) - general eviction, no RAG differentiation
- KVCache-Factory (1.3K⭐) - unified platform, no RAG-specific method

**Available Implementations:**
- H2O: github.com/FMInference/H2O (518⭐, MIT)
- StreamingLLM: github.com/mit-han-lab/streaming-llm (7.2K⭐, MIT)
- KVCache-Factory: github.com/Zefan-Cai/KVCache-Factory (1.3K⭐, MIT)

**Available Papers:**
1. **P1**: H2O - Heavy-Hitter Oracle for Efficient Generative Inference (arXiv:2306.14048, 878 cit)
2. **P2**: StreamingLLM - Efficient Streaming Language Models with Attention Sinks (arXiv:2304.13343, 44 cit)
3. **P3**: LongBench - A Bilingual, Multitask Benchmark for Long Context Understanding (arXiv:2308.14508, 1563 cit)

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

RAG-aware caching - now THIS opens new territory! Everyone treats the KV cache as one undifferentiated blob, but retrieval creates STRUCTURE we're ignoring. What if we exploit the semantic boundary between retrieved passages and the user's original query?

Here's the wild idea: Retrieved context comes with metadata - relevance scores, source documents, retrieval timestamps. Current methods (H2O, StreamingLLM) discard this. But what if cache eviction used retrieval metadata as a signal? High-relevance passages stay, low-relevance get evicted first. The original query tokens are *anchors* - they define what matters, so they get preferential retention.

Cross-domain inspiration: Database query optimization has "selectivity estimation" - predicting which data subsets matter for a query. We could borrow that lens for KV cache management. Treat retrieved passages as "tables" with selectivity scores based on retrieval similarity.

**Novel angles to explore:**
1. **Tiered caching by provenance**: Query tokens (Tier 0, never evict) → High-relevance retrieved (Tier 1, evict last) → Low-relevance retrieved (Tier 2, evict first) → Generated tokens (Tier 3, standard H2O)
2. **Retrieval-aware attention budgeting**: Allocate more attention budget to query-passage boundaries where reasoning happens
3. **Dynamic re-ranking during generation**: As the model generates, update passage relevance based on which KV positions get high attention weights

This avoids evolutionary search entirely - it's a measurement study comparing provenance-aware eviction against uniform eviction on LongBench multi-doc QA tasks. Implementations exist (H2O, StreamingLLM), we just need to layer on retrieval metadata tracking.

**Key Points:**
- Exploit retrieval metadata (relevance scores) that current methods ignore
- Tiered eviction policy based on token provenance (query vs retrieved vs generated)
- Borrow database selectivity estimation concepts for passage importance
- Pure measurement study using existing KVCache-Factory platform

What if the "right" cache isn't the one with the highest attention scores, but the one that preserves the query→evidence reasoning chain?

---


### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's tiered provenance idea is intriguing, but let's stress-test it with falsifiability. What would disprove this hypothesis?

**Testable prediction 1:** If retrieval relevance scores predict cache utility, then evicting low-relevance passages first should preserve accuracy better than uniform eviction (H2O baseline) on multi-doc QA tasks. Measurement: Compare answer accuracy at fixed cache budgets (50%, 25%, 10% retention) between provenance-aware and uniform eviction.

**Potential falsifier:** If answer accuracy degrades equally regardless of which passages we evict, then relevance scores don't predict reasoning utility. This would mean the retriever's scoring function doesn't align with what the LLM actually uses.

**Testable prediction 2:** Query tokens should show higher attention concentration during answer generation than retrieved passage tokens. If true, preferential query retention makes sense. If false, the "anchor" assumption breaks.

**Edge cases to control:**
1. **Retriever-LLM mismatch:** What if retrieval uses BM25 (lexical) but LLM reasoning needs semantic connections? Low BM25 score ≠ low reasoning utility.
2. **Multi-hop reasoning:** For questions requiring evidence synthesis across passages, evicting ANY passage might break the chain. How do we detect multi-hop dependencies?
3. **Query ambiguity:** Vague queries might need more retrieved context, not less. How does provenance-aware caching handle this?

**Experiment design requirements:**
- Dataset: LongBench multi-doc QA subset (standardized, avoids custom benchmark creation)
- Baselines: FullKV (no eviction), H2O (uniform heavy-hitter), StreamingLLM (sliding window)
- Metrics: Answer accuracy (primary), cache hit rate (secondary), latency (tertiary)
- Cache budgets: Test at 50%, 25%, 10% retention to see where provenance-awareness helps most

**What would convince me:** Clear accuracy advantage at restrictive budgets (10-25%), robust across question types (single-hop vs multi-hop), and ablation showing the provenance signal matters more than just "keep everything."

**Key Points:**
- Falsifiable predictions needed: relevance scores predict utility, query tokens are attention anchors
- Control for retriever-LLM mismatch (BM25 vs semantic reasoning)
- Multi-hop reasoning might require passage co-retention, not independent eviction
- Standard LongBench benchmarks avoid custom evaluation frameworks

Can we measure attention flow to validate the "query anchor" assumption before committing to the full experiment?

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

This matters *if* we solve a problem people actually face. Let me ground this in field impact.

**State-of-the-art context:** RAG systems are production-deployed (Perplexity, You.com, GitHub Copilot). Long-context inference is expensive - O(n²) attention on 32k+ tokens. H2O (878 cit) and StreamingLLM (ICLR 2024) show the community cares about cache efficiency.

**The gap Dr. Nova identified is real:** Current methods treat all tokens uniformly, but RAG creates semantic structure. If we can show that exploiting retrieval metadata improves the accuracy-memory tradeoff, that's a *reusable insight* - any RAG system could apply it.

**Contribution clarity test:**
- **Incremental:** "We tested H2O on RAG tasks" - not interesting, just application
- **Genuine:** "Retrieval provenance (query vs passage vs generated) predicts cache utility better than attention scores alone" - this is a principle

**What makes this significant:**
1. **Measurement gap:** No prior work (LongBench, H2O, MInference) analyzed cache strategies *conditioned on* retrieval metadata. This is unexplored.
2. **Practical impact:** RAG systems could implement tiered eviction immediately if we prove it works. KVCache-Factory makes this deployable.
3. **Opens new questions:** If provenance helps, what about other retrieval signals (source diversity, temporal recency, citation graphs)?

**State-of-the-art positioning:** We're not replacing H2O or StreamingLLM - we're augmenting them with retrieval-awareness. Hybrid approach: "H2O heavy-hitter selection + provenance-based tie-breaking."

**Skepticism check:** Why hasn't anyone done this yet? Possible reasons:
- H2O paper focused on generation tasks, not RAG (no retrieval metadata to exploit)
- LongBench evaluated static documents, not dynamically retrieved passages
- Retrieval community (RAG) and efficiency community (KV caching) haven't cross-pollinated much

**Key Points:**
- Real gap: no prior analysis of cache strategies conditioned on retrieval metadata
- Practical impact: deployable via existing platforms (KVCache-Factory)
- Contribution is the principle (provenance predicts utility), not just the application
- Positions as augmentation to H2O/StreamingLLM, not replacement

If we can show a 10-15% accuracy improvement at 25% cache budget, this gets into top-tier venues. What's the minimal viable experiment to demonstrate the principle?

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's validate the technical feasibility before we celebrate.

**Mechanism check:** Provenance-aware eviction requires:
1. Tracking token provenance (query/retrieved/generated) - trivial, metadata annotation
2. Accessing retrieval scores during cache eviction - requires passing scores through to KV cache layer
3. Eviction policy that uses provenance+scores - H2O already has eviction hooks, we extend the scoring function

**Theoretically sound?** Yes. No fundamental barriers. This is engineering, not research risk.

**Measurement validity check:**
- **Can we accurately track provenance?** Yes - query tokens are known at input, retrieved tokens come from retriever output (with boundaries), generated tokens are autoregressive.
- **Do retrieval scores align with LLM reasoning needs?** Unknown - this is the research question. If they don't align, provenance-aware caching fails. But we CAN measure this.
- **Can we implement tiered eviction without modifying model internals?** Yes - KVCache-Factory already abstracts cache management. We add a scoring function that reads token metadata.

**Hidden complexity assessment:**
1. **Retriever-LLM integration:** Current KVCache-Factory benchmarks use static documents, not dynamic retrieval. We need a RAG pipeline wrapper. Complexity: medium (use existing RAG frameworks like LlamaIndex, not custom).
2. **Multi-doc provenance boundaries:** Retrieved passages have boundaries (start/end token indices). Tracking this is straightforward array indexing.
3. **Attention analysis for validation:** Prof. Vera wants attention flow measurements. This requires extracting attention weights during inference - PyTorch provides this via hooks. Complexity: low.

**What worries me:** 
- **Retriever quality sensitivity:** If the retriever is terrible (low relevance scores for useful passages), provenance-aware caching amplifies the error. We need a competent retriever baseline.
- **Multi-hop coordination:** Evicting passage A might break reasoning that needs both A and B. Provenance-aware scoring treats passages independently. Is this valid?

**Validation approach:** Start with *attention analysis* (Prof. Vera's suggestion). Measure:
1. Attention weights from generated tokens → query tokens vs passage tokens
2. Correlation between retrieval scores and attention weights

If attention concentrates on high-relevance passages, provenance-awareness is justified. If not, we abort early (no full experiment needed).

**Key Points:**
- Mechanism is technically sound (no fundamental barriers)
- Implementation feasible via KVCache-Factory + RAG framework integration
- Attention analysis validates assumptions before full experiment
- Retriever quality is a dependency - need competent baseline (not research risk, just setup)

Can we run the attention analysis pilot (1-2 GPU-hours) before committing to full cache eviction experiments?

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES! Let's build on this momentum. Prof. Pax's attention pilot idea is brilliant - validate assumptions cheaply before the expensive experiment.

**Refined hypothesis statement:**

*Under RAG-based long-context QA tasks (LongBench multi-doc), if we implement provenance-aware KV cache eviction (query tokens prioritized → high-relevance passages → low-relevance passages → generated tokens), then answer accuracy at restrictive cache budgets (10-25% retention) will improve by ≥10% compared to uniform eviction (H2O baseline), because retrieval relevance scores correlate with attention concentration during answer generation.*

**Strengthening the mechanism:**

Dr. Nova's tiered provenance idea + Prof. Vera's falsifiability + Dr. Sage's practical impact = solid hypothesis. But let's address Prof. Pax's multi-hop concern:

**Extension:** For multi-hop questions, we need passage *co-retention* scoring. If passages A and B are both cited in the reasoning chain (detected via attention flow), they should be evicted together or kept together. This prevents breaking multi-hop reasoning.

**Pilot experiment sequence (Prof. Pax's suggestion, strengthened):**

**Pilot 1 - Attention Analysis (1-2 GPU-hours):**
- Measure attention weights: generated tokens → query vs passage tokens
- Compute correlation: retrieval scores vs attention weights
- Success criterion: Spearman ρ > 0.3 (moderate positive correlation)

**Pilot 2 - Single-Hop Provenance Caching (5-8 GPU-hours):**
- Implement tiered eviction on single-hop QA subset (no multi-hop complexity)
- Compare: Provenance-aware vs H2O baseline vs FullKV
- Success criterion: ≥5% accuracy gain at 25% cache budget

**Full Experiment - Multi-Hop + Hybrid Strategy (15-20 GPU-hours):**
- Add co-retention scoring for multi-hop questions
- Test on full LongBench multi-doc QA
- Baselines: FullKV, H2O, StreamingLLM, Random eviction
- Success criterion: ≥10% accuracy gain at 10-25% budgets, robust across question types

**Addressing Prof. Vera's edge cases:**

1. **Retriever-LLM mismatch:** Pilot 1 (attention analysis) directly measures this. If BM25 scores don't correlate with attention, we switch to semantic retriever or abort.
2. **Multi-hop reasoning:** Pilot 2 tests single-hop first (controlled setting), Full Experiment adds co-retention for multi-hop.
3. **Query ambiguity:** We can stratify LongBench questions by query length/specificity and test if provenance-awareness helps more for specific queries.

**Evidence for the mechanism:**

H2O paper (Zhang et al., 2023) showed attention weights predict token importance. Our addition: *retrieval scores also predict importance for RAG tasks*. If Pilot 1 validates this, we have mechanistic evidence before investing in full cache experiments.

**Key Points:**
- Hypothesis: Provenance-aware eviction improves accuracy at restrictive budgets (≥10% gain)
- Mechanism: Retrieval scores correlate with attention concentration (validated in Pilot 1)
- Three-tier pilot → full experiment reduces risk
- Addresses multi-hop concern with co-retention scoring
- Total compute: ~25 GPU-hours (reasonable for measurement study)

This is no longer an open-ended optimization problem - it's a controlled comparative measurement with clear success criteria. Thoughts on the pilot sequence?

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's three-tier pilot is smart risk mitigation. Now let me attack the weakest points.

**Assumption to challenge:** "Retrieval relevance scores predict reasoning utility."

**Counterargument:** Retrievers optimize for query-passage similarity. LLMs reason by *contrasting* passages or finding gaps. A low-relevance passage might be critical for ruling out wrong answers (negative evidence). Evicting it breaks reasoning.

**Test:** In Pilot 1, don't just measure correlation between relevance scores and attention. Measure:
- Attention to low-relevance passages in correct answers vs incorrect answers
- If low-relevance passages get high attention when the model is correct, provenance-aware eviction is dangerous

**Assumption 2:** "Query tokens are attention anchors."

**Counterargument:** For complex multi-hop questions, the query might be vague ("What caused X?"). The *retrieved passages* define what X actually is. Anchoring on the query is anchoring on ambiguity.

**Test:** Stratify Pilot 1 by query complexity (word count, entity count). If simple queries show query-token attention concentration but complex queries don't, tiered eviction needs query-complexity-aware tuning.

**Assumption 3:** "10% accuracy gain is significant."

**Skepticism:** LongBench accuracy varies widely by task (single-doc QA ~85%, multi-doc ~60%). A 10% *relative* gain on 60% baseline is 6 percentage points absolute - meaningful. But on 85% baseline, it's 8.5pp - possibly within noise.

**Requirement:** Report both relative and absolute gains, stratified by task difficulty. Don't average across easy and hard tasks.

**Mechanism weakness:** Co-retention for multi-hop reasoning.

**Challenge:** How do we detect multi-hop dependencies *during* eviction? We can't wait until generation finishes to analyze attention (cache decisions happen before generation). We need a *heuristic* for co-retention.

**Proposed heuristic:** If two passages share entities or have high lexical overlap, treat them as a co-retention unit. Evict them together or keep them together.

**Risk:** This heuristic might be wrong. Passages with no overlap might still support multi-hop reasoning (e.g., "Passage A: Event X happened in 1990. Passage B: Policy Y was enacted in 1991. Question: Did Y respond to X?").

**What would convince me:**

1. **Pilot 1 shows:** Relevance scores correlate with attention (ρ > 0.3) AND low-relevance passages don't systematically get high attention in correct answers
2. **Pilot 2 shows:** Provenance-aware eviction beats H2O on single-hop tasks (controlled test)
3. **Full experiment shows:** Multi-hop co-retention heuristic doesn't hurt performance (accuracy on multi-hop ≥ accuracy on single-hop under provenance-aware caching)

**Remaining concerns:**

- **Retriever dependence:** If we test with BM25 retriever and someone replicates with semantic retriever, do results hold? Need to test with 2+ retrievers.
- **Dataset specificity:** LongBench multi-doc QA is one benchmark. Does this generalize to NarrativeQA (Gap 1 also mentioned this)?
- **Cache budget realism:** Testing at 10% cache budget is extreme. What's the practical operating point for RAG systems? Maybe 30-50% is more realistic?

**Key Points:**
- Challenge: Low-relevance passages might provide negative evidence (important for correct reasoning)
- Challenge: Query tokens might anchor on ambiguity, not clarity
- Test required: Stratify attention analysis by query complexity and answer correctness
- Co-retention heuristic (entity overlap) might miss valid multi-hop patterns
- Need multi-retriever validation (BM25 vs semantic)

If Pilot 1 fails (no correlation), what's the backup plan? Abort or pivot to a different provenance signal (e.g., passage source diversity instead of relevance scores)?

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are sharp - let me respond with a refinement that addresses the "negative evidence" problem.

**New angle:** Instead of rigid tiered eviction (query > high-relevance > low-relevance), what if we use *diversity-aware* provenance scoring?

**Insight:** Prof. Rex is right that low-relevance passages might provide contrastive evidence. The solution isn't to keep ALL passages - it's to keep a *representative sample*. Borrowing from information retrieval's MMR (Maximal Marginal Relevance):

**Refined eviction policy:**
1. **Tier 0 (Never evict):** Query tokens + top-1 most relevant passage
2. **Tier 1 (Evict last):** Passages that maximize diversity from already-retained passages (measured by embedding distance or entity non-overlap)
3. **Tier 2 (Evict first):** Redundant passages (high similarity to already-retained passages + low relevance)

This preserves both high-relevance passages AND diverse low-relevance passages that might provide contrastive evidence.

**Addressing query ambiguity:** Prof. Rex's point about vague queries is valid. Adaptation: For queries with low entity density (< 2 named entities) or high word count (> 20 tokens), increase the diversity weight in Tier 1 scoring. This keeps more passages when the query is ambiguous.

**Multi-retriever validation:** Prof. Rex wants 2+ retrievers. Agree! Pilot 1 should test:
- BM25 (lexical baseline)
- Contriever or DPR (dense semantic retrieval)

If provenance-awareness works for BOTH retrievers, it's a robust principle. If it only works for one, we've learned something important about retriever-LLM alignment.

**Backup plan if Pilot 1 fails:** If relevance scores don't correlate with attention, pivot to *passage diversity* as the provenance signal. Hypothesis becomes: "Retaining diverse passages (measured by embedding distance) outperforms attention-based eviction." This is still testable without custom benchmarks.

**Key Points:**
- Diversity-aware provenance preserves contrastive evidence (addresses Prof. Rex's negative evidence concern)
- Query complexity adaptation (entity density, word count) handles ambiguous queries
- Multi-retriever validation (BM25 + semantic) tests robustness
- Backup pivot: diversity-based provenance if relevance scores fail

NOW we have a hypothesis that survives Prof. Rex's attacks AND preserves the novelty from Exchange 1. Ready for convergence?

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** Provenance-aware caching exploits retrieval metadata that current methods ignore. Diversity-aware refinement addresses negative evidence concerns while preserving the core novelty. Cross-domain MMR adaptation is creative and defensible.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three-tier pilot sequence provides clear falsification points. Pilot 1 (attention analysis) validates assumptions cheaply. Stratification by query complexity and answer correctness addresses edge cases. Measurable success criteria at each stage.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Addresses real gap (no prior RAG-conditioned cache analysis). Practical deployability via KVCache-Factory. Contribution is the principle (provenance+diversity predicts utility), not just application. Multi-retriever validation ensures generalizability.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Mechanism is technically sound. No fundamental barriers. RAG framework integration (LlamaIndex) handles retriever-LLM plumbing. Attention analysis via PyTorch hooks is standard. Total compute (~25 GPU-hours) is realistic for measurement study.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Core Hypothesis:** Under RAG-based long-context QA (LongBench multi-doc), provenance-aware KV cache eviction with diversity-aware scoring improves answer accuracy at restrictive cache budgets (10-25% retention) compared to uniform eviction baselines (H2O, StreamingLLM).

**Mechanism:** 
1. Retrieval relevance scores correlate with attention concentration during answer generation (validated in Pilot 1)
2. Diverse passage retention preserves contrastive evidence needed for multi-hop reasoning
3. Query complexity adaptation prevents over-eviction for ambiguous queries

**Predictions:**
- **P1 (Primary):** Provenance-aware eviction achieves ≥10% relative accuracy gain at 25% cache budget on LongBench multi-doc QA vs H2O baseline
- **P2:** Diversity-aware scoring outperforms pure relevance-based scoring on multi-hop questions (≥5% accuracy gain)
- **P3:** Attention analysis shows moderate positive correlation (Spearman ρ > 0.3) between retrieval scores and attention weights

**Experimental Approach:**
- **Pilot 1:** Attention analysis with 2 retrievers (BM25 + semantic) to validate assumptions (1-2 GPU-hours)
- **Pilot 2:** Single-hop provenance caching vs baselines (5-8 GPU-hours)
- **Full Experiment:** Multi-hop + diversity-aware eviction on full LongBench (15-20 GPU-hours)

**Novelty:** First analysis of cache strategies conditioned on retrieval provenance + diversity. Augments existing methods (H2O) rather than replacing them.

**Feasibility:** Uses existing platforms (KVCache-Factory, LlamaIndex), standard benchmarks (LongBench), and established retrievers. No custom frameworks or synthetic data.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Diversity heuristic (embedding distance + entity overlap) might miss temporal or causal multi-hop dependencies
- **Concern 2:** Cache budget realism - 10% might be too extreme, practical RAG systems might operate at 30-50%
- **Mitigation Strategy:** Test full range of cache budgets (10%, 25%, 50%, 75%) and report Pareto frontiers. Include qualitative analysis of failure cases where diversity heuristic breaks down.

---
