# Phase 2A: Research Discussion Log

## Metadata
- **Gap ID**: gap-1-rag-curation
- **Gap Title**: RAG-Specific Data Curation
- **Start Time**: 2026-07-12T05:59:51Z
- **Architecture**: Self-Contained Tikitaka Loop
- **Execution Mode**: UNATTENDED

## Discussion Briefing

### Research Gap
Pretraining curation well-researched (DataComp-LM, FineWeb), but RAG-specific
strategies underexplored. How do filtering/mixing strategies differ for RAG
retrieval corpora vs. pretraining? Optimal quality metrics for inference-time retrieval?

### Phase 1 Key Findings
(Refer to `01_targeted_research.md` for detailed findings)

### Previous Failure / Routing Context
This section is mandatory hard input for the Phase 2A discussion. If it contains
SUPERSEDED, ROUTED_TO_PHASE_2A, PARTIAL, FAIL, or pivot records, the discussion
must redesign away from the failed approach families and preserve validated
partial findings.

(No prior failure/routing context supplied.)

### Available Papers
- `arxiv_2406_11794.md` — DataComp-LM: Model-based filtering benchmark for LM training data
- `arxiv_2406_17557.md` — FineWeb: 15T token dataset with deduplication/filtering ablations and educational subset

### Research Repos
(None)

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we fundamentally rethought RAG corpus quality through the lens of *retrieval-specific utility* rather than just adapting pretraining filters? The Phase 1 findings highlight that DataComp-LM [Penedo et al., 2024] uses model-based filtering with FastText classifiers trained on positive examples (OpenWebText, Wikipedia) versus negative examples (4chan, BitChute). But here's the paradigm shift: for RAG, our "positive examples" should be documents that performed well in *actual retrieval scenarios*, not just documents that look like Wikipedia!

Imagine this: we could build a retrieval-quality classifier by taking successful RAG retrievals from existing benchmarks like BEIR and treating those as positive examples, while failed or irrelevant retrievals become negative examples. This flips the curation paradigm from "what makes good training data" to "what makes good retrieval targets." The FineWeb paper shows dramatic gains (+5.0pp MMLU) from their educational classifier [Penedo et al., 2024] — what if we built a "retrieval-utility classifier" instead?

Here's another wild connection: FineWeb's finding that individual per-snapshot deduplication outperforms global deduplication is fascinating for RAG! They discovered global dedup upsampled low-quality content from older crawls. For RAG, maybe we WANT some redundancy across sources to improve recall, but we want to deduplicate *within* topics to avoid retrieval returning 20 variations of the same fact?

**Key Points:**
- Propose training retrieval-quality classifiers using actual BEIR retrieval performance as supervision
- Challenge assumption that pretraining filters (perplexity, educational quality) optimize for retrieval utility
- Explore whether controlled redundancy (topic-level, not document-level dedup) improves RAG recall without harming precision

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's retrieval-quality classifier is intriguing, but I need precision before enthusiasm. What would convince us this hypothesis is wrong? Let's design this to fail clearly if it's misguided.

Here's the testable core: **Hypothesis: A FastText classifier trained on positive examples (successful BEIR retrievals) and negative examples (failed/irrelevant retrievals) will produce a RAG corpus that outperforms perplexity-based filtering on retrieval benchmarks.** This needs three specific, measurable predictions:

**Prediction 1:** Training a retriever (e.g., Contriever, DPR) on a corpus filtered by our retrieval-quality classifier will achieve ≥3% higher Recall@10 on BEIR test sets compared to perplexity-filtered baseline, holding corpus size constant at 1M documents.

**Prediction 2:** The retrieval-quality classifier will assign systematically lower scores to high-perplexity but factually-dense content (e.g., technical documentation, API references) that pretraining filters would remove — we can test this by measuring score distribution on Stack Overflow documents known to be valuable for code retrieval.

**Prediction 3:** Documents selected by the classifier will have measurably higher lexical diversity (measured by type-token ratio) and entity coverage (measured by Named Entity density) than perplexity-matched controls, because retrieval utility rewards specificity over fluency.

But here's where this breaks down if I'm wrong: What if "successful BEIR retrievals" are successful because of the *query formulation*, not document quality? We'd be training a classifier that learns query-document matching patterns, not intrinsic retrieval utility. The edge case: a poorly-written but highly-relevant document versus a beautifully-written but tangential one. How do we disentangle document quality from retrieval algorithm bias?

**Key Points:**
- Testable hypothesis: Retrieval-quality classifier outperforms perplexity baseline by ≥3% Recall@10
- Critical prediction: Classifier will preserve high-perplex

ity technical content that aids retrieval
- Achilles heel: Risk of learning query-matching patterns rather than document quality

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's predictions are testable, but I need to stress-test the mechanism itself. Is training a retrieval-quality classifier from BEIR retrievals theoretically sound, or are we building on quicksand?

Here's what worries me: the positive/negative example construction assumes we can cleanly separate "successful" from "failed" retrievals. But BEIR is a *query-document relevance* benchmark — a "successful" retrieval means high relevance score, not that the document is well-curated for a corpus. We're conflating two different quality dimensions: (1) query-specific relevance, and (2) corpus-level utility. A document can be perfectly relevant for one query but terrible for corpus diversity.

Let's be realistic here: can we actually measure "retrieval utility" independent of specific queries? FineWeb's educational classifier [Penedo et al., 2024] works because "educational quality" is a query-independent property — you can label a document as educational without knowing what questions it will answer. But "retrieval utility" is inherently query-dependent. Are we proposing to learn a query-averaged notion of utility? That's mathematically feasible via multi-task learning, but it requires aggregating retrieval performance across hundreds of diverse BEIR queries to avoid overfitting to specific query distributions.

Here's the fundamental barrier: if our classifier learns "documents similar to those that matched queries about X," we've just built a domain-specific filter, not a general retrieval-quality metric. The null hypothesis alternative is simpler: just use perplexity + named entity density as a proxy for informativeness. What evidence do we have that the added complexity of classifier training is scientifically justified?

**Key Points:**
- Mechanism conflates query-specific relevance with corpus-level utility — these are orthogonal dimensions
- Retrieval utility is query-dependent; requires aggregating across diverse BEIR query distributions to generalize
- Simpler baseline exists: perplexity + NE density might achieve same gains without classifier complexity

---

### Exchange 4

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Pax raises a legitimate concern about query-dependence, but what if that's exactly the feature, not the bug? Let me push this further: what if we explicitly model retrieval utility as a *multi-faceted construct* rather than a single quality score?

Imagine this: instead of one retrieval-quality classifier, we train a small ensemble of specialized classifiers, each targeting a different retrieval failure mode identified in literature. Classifier 1 learns "factual density" from successful factoid retrievals (Natural Questions subset of BEIR). Classifier 2 learns "argumentative coherence" from debate/claim retrieval tasks. Classifier 3 learns "technical precision" from code and documentation retrieval. Then we filter the corpus by requiring documents to score above threshold on at least one specialist classifier — this preserves diversity while ensuring every document has *some* strong retrieval utility signal.

This addresses Prof. Pax's concern: we're not learning a monolithic "good for retrieval" score, we're learning a factorized representation where each factor is grounded in specific, measurable retrieval success patterns. The DataComp-LM paper [Li et al., 2024] showed that model-based filtering with carefully selected positive/negative examples outperforms perplexity by 9pp MMLU. Our version factorizes those examples by retrieval mode.

NOW we're onto something! This also connects to Dr. Nova's deduplication insight: we deduplicate within each specialist cluster (factoid docs, argument docs, technical docs) but preserve redundancy across clusters to maintain coverage.

**Key Points:**
- Factorize retrieval quality into multiple specialist classifiers targeting different retrieval modes
- Filter criterion: score high on ≥1 specialist (preserves diversity via multi-dimensional coverage)
- Deduplication strategy: within-cluster (mode-specific) not global, maintaining cross-mode redundancy

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

Dr. Nova's multi-classifier ensemble is creative, but the question we must ask is: what does this mean for the field? Why should the community care about RAG-specific curation when we could just apply existing pretraining filters to RAG corpora?

Here's where this genuinely advances science: the hypothesis challenges the implicit assumption that data quality is **monolithic**. Pretraining filters optimize for fluency, grammaticality, and coherence because those correlate with next-token prediction loss. But retrieval has fundamentally different quality desiderata: specificity, factual density, and entity coverage matter more than narrative flow. If we demonstrate that pretraining-optimal and retrieval-optimal corpora diverge measurably, that's a conceptual contribution beyond the RAG use case.

The broader implication: this opens a research direction on **task-specific data curation**. Just as FineWeb-Edu [Penedo et al., 2024] showed +5.0pp MMLU gains from domain-targeted filtering, we could see emergence of specialized corpora for different inference modes: retrieval-optimized, reasoning-optimized, generation-optimized. The meta-question becomes: how should quality metrics vary with the downstream task?

But I'm skeptical of one claim: Dr. Nova suggests factual density and entity coverage are "retrieval-specific" quality signals. Aren't those just as valuable for pretraining factual knowledge? Where's the genuine novelty beyond "apply domain-specific filtering to RAG," which is incremental? The contribution needs to be: **demonstrating that retrieval-optimal filters measurably diverge from pretraining-optimal filters**, not just applying existing filter types to a new setting.

**Key Points:**
- Contribution: Demonstrates data quality is task-specific, not monolithic (conceptual advance)
- Opens research direction: specialized corpora for different inference modes
- Novelty requirement: Must show retrieval-optimal ≠ pretraining-optimal filters (divergence, not just application)

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Sage demands we demonstrate divergence between retrieval-optimal and pretraining-optimal filters. Excellent — that's experimentally falsifiable. Here's the precise experiment:

**Experiment Design:** Take a held-out 100K document sample from Common Crawl. Apply three filtering regimes: (1) Perplexity-based (keep documents with perplexity < threshold on GPT-2), (2) FineWeb-style educational classifier, (3) Our retrieval-quality classifier ensemble. Measure three dependent variables for each filtered corpus:

**DV1 (Pretraining quality):** Train 400M LM on each filtered corpus for fixed compute, measure MMLU/HellaSwag accuracy. Prediction: Educational filter > Retrieval filter > Perplexity.

**DV2 (Retrieval quality):** Index each corpus with DPR, measure Recall@10 on BEIR. Prediction: Retrieval filter > Educational filter > Perplexity (reverse rank order).

**DV3 (Corpus divergence):** Measure document overlap between top 50K documents selected by each method. Prediction: Retrieval-Educational overlap < 60%, demonstrating measurable divergence.

If DV3 shows >80% overlap, the "task-specific" claim fails — we're just reweighting the same documents. If DV2 doesn't reverse-rank, retrieval-specific filtering has no advantage. This experiment would disprove the hypothesis cleanly.

The remaining confound: what if retrieval quality and educational quality are simply orthogonal, not divergent? We could have both high retrieval utility AND high educational value. Does "divergence" require anti-correlation, or just low correlation?

**Key Points:**
- Three-way controlled comparison: Perplexity vs Educational vs Retrieval filtering
- Measure both pretraining quality (MMLU) and retrieval quality (BEIR Recall@10)
- Quantify corpus divergence via top-document overlap (<60% threshold for novelty claim)

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen Prof. Vera's experiment by addressing the orthogonality concern! What if we explicitly design the retrieval-quality classifier to identify documents that score LOW on educational quality but HIGH on retrieval utility? This would directly demonstrate divergence, not just correlation.

Here's how: when constructing training data for the retrieval-quality classifier, we stratify positive examples by educational score. We oversample successful BEIR retrievals that FineWeb-Edu would have filtered out (educational score < 0.3 threshold). This forces the classifier to learn retrieval-utility signals that are *independent* of educational signals, explicitly targeting the divergence Prof. Vera wants to measure.

This addresses Dr. Sage's novelty concern: we're not just saying "retrieval needs different quality," we're operationalizing that difference as **documents that fail pretraining quality tests but succeed at retrieval**. Examples might include: technical API documentation (high perplexity, low narrative flow, but excellent for code-related factoid retrieval), structured data tables (poor for language modeling, excellent for entity lookup), forum threads with fragmented text (fail coherence filters, but contain valuable troubleshooting knowledge).

The evidence supports this: DataComp-LM [Li et al., 2024] showed that different positive/negative example sets produce 9pp MMLU swings. Our version explicitly constructs examples to capture retrieval-specific utility. This refinement makes the hypothesis testable via Prof. Vera's DV3: we predict <50% overlap when stratifying for low-educational-score BEIR successes.

**Key Points:**
- Stratify retrieval-quality classifier training by educational score to force independence
- Target divergence explicitly: documents that fail pretraining tests but succeed at retrieval
- Predicted corpus overlap <50% when conditioning on low-education, high-retrieval documents

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down: Dr. Ally proposes oversampling "low-educational, high-retrieval" documents, but what's the ground truth for "high retrieval" utility? BEIR relevance scores are human annotations of query-document matches — they don't measure whether a document improves the retrieval *system's* performance, they measure whether humans think it's relevant to a query.

Show me the evidence that BEIR-labeled "relevant" documents produce better downstream task performance when retrieved. What if human annotators systematically prefer fluent, well-written documents even when terse technical docs would better serve the user's information need? We'd be training a classifier to reproduce human annotation bias, not true retrieval utility.

Here's the missing piece: we need to validate retrieval utility via downstream task performance, not annotation agreement. Concretely: for open-domain QA (Natural Questions), measure whether retrieving a "low-educational, high-BEIR-score" document leads to correct answer extraction more often than retrieving a "high-educational, low-BEIR-score" document. If annotation scores don't correlate with answer accuracy, BEIR relevance is a noisy proxy for actual utility.

What would convince me is a two-stage validation: (1) Train classifier on BEIR annotations, (2) Validate that classifier-selected documents improve end-task metrics (exact match accuracy for QA, truthfulness for claim verification) beyond what BEIR scores alone predict. Without stage 2, we're just learning to predict noisy human judgments.

**Key Points:**
- BEIR relevance labels measure human annotation agreement, not downstream utility
- Missing validation: Does high-BEIR, low-education correlate with better end-task performance (QA accuracy)?
- Required: Two-stage validation linking classifier predictions to measurable task improvement

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex's two-stage validation is scientifically sound, but let's trace through the measurement mechanics. Can we actually construct a dataset that cleanly separates annotation quality from task performance?

Here's the issue: for Natural Questions QA, "correct answer extraction" depends on both document quality AND the reader model's capabilities. If we compare two retrieved documents and one produces better answer accuracy, is that because the document is higher quality, or because it happens to phrase the answer in a way the reader model can extract? We're introducing a confound: reader model architecture becomes a hidden variable in our quality metric.

The theoretically valid approach: use a controlled reader (e.g., BM25 + exact string match, no neural model) to isolate document characteristics from model biases. If Document A contains the answer string and Document B doesn't, that's a document quality difference independent of reader sophistication. But this only works for extractive QA with short factoid answers. For complex reasoning or multi-hop questions, we can't avoid the reader model confound.

Let's be realistic here: are we proposing to restrict our validation to extractive factoid QA, or do we claim the retrieval-quality classifier generalizes to all retrieval modes? The former is feasible but narrow; the latter is ambitious but introduces measurement challenges. What evidence supports that a classifier trained on factoid retrieval utility generalizes to argumentative retrieval or document ranking?

**Key Points:**
- Two-stage validation introduces confound: reader model capabilities affect measured utility
- Theoretically valid approach requires controlled reader (BM25 + exact match) for factoid QA
- Scope question: Do we claim generalization across retrieval modes, or restrict to factoid QA validation?

---

### Exchange 10

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Pax is right that factoid QA is a narrow validation, but what if we flip the framing? Instead of claiming one universal retrieval-quality classifier, we explicitly scope our contribution: **"A methodology for constructing task-specific retrieval corpora via specialized filtering, demonstrated on factoid QA with extractive validation."** This is honest about limitations while still being novel!

Here's the creative extension: we provide a *recipe* that others can adapt. The recipe is: (1) Identify a retrieval task with measurable downstream metric, (2) Curate positive examples from successful retrievals, (3) Train FastText classifier, (4) Validate on held-out downstream task. Our instantiation uses factoid QA + exact match, but the methodology generalizes conceptually even if our specific classifier doesn't.

This connects back to FineWeb's contribution [Penedo et al., 2024]: they didn't claim their educational classifier generalizes to all domains; they demonstrated a methodology (train classifier on quality dimension, ablate at scale, measure downstream impact) that others adapted. We're doing the same for retrieval-specific curation.

Imagine this: if we show that corpus divergence (retrieval-optimal ≠ pretraining-optimal) exists for even ONE retrieval mode (factoid QA), that validates the core hypothesis that task-specific curation matters. Future work extends to argumentative retrieval, multi-hop reasoning, etc. We've opened the research direction without claiming to solve all instances.

**Key Points:**
- Scope contribution: Methodology for task-specific retrieval corpus curation, demonstrated on factoid QA
- Recipe generalizes conceptually: identify task metric → curate examples → train classifier → validate
- Core claim: Retrieval-optimal ≠ pretraining-optimal (proven for factoid QA, extensible to other modes)

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

Dr. Nova's scoping is sensible, but now we need to ensure the factoid QA instantiation is genuinely compelling. The question we must ask is: will a top-tier venue accept "we demonstrate task-specific curation matters for factoid QA" as sufficient contribution?

Here's where significance increases: if we additionally show that our retrieval-quality corpus achieves Pareto improvement — better retrieval quality with smaller corpus size OR same quality with 50% fewer documents — that's a resource efficiency angle. DataComp-LM [Li et al., 2024] achieved 7B model to 64% MMLU with 40% less compute than prior SOTA. If we show "same BEIR Recall@10 with half the corpus size via better filtering," that's analogous compute efficiency for retrieval systems.

The broader implication: RAG deployments face real indexing costs (storage, search latency scale with corpus size). A principled filtering methodology that achieves better quality-density trade-offs would have immediate practical impact. This matters because current RAG practice is ad-hoc: practitioners use perplexity or heuristic filters without empirical validation. We'd be providing the first rigorous ablation of filtering strategies specifically for retrieval corpora.

But I'm concerned about one claim: Prof. Vera's DV3 predicts <60% overlap between educational and retrieval filtering. If overlap is 55%, is that meaningful divergence or noise? What's the statistical power? We need effect size estimates: how many documents must diverge to matter for downstream retrieval quality?

**Key Points:**
- Strengthen contribution: Show Pareto improvement (same quality, 50% smaller corpus via better filtering)
- Practical impact: RAG indexing costs scale with corpus size; quality-density matters commercially
- Statistical rigor needed: What overlap threshold constitutes meaningful divergence (effect size)?

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Sage demands effect size rigor. Let's operationalize it precisely. The meaningful divergence threshold should be derived from retrieval quality impact, not arbitrary overlap percentages.

**Refined DV3:** Measure divergence as the delta in Recall@10 between using ALL educational-filtered documents vs using ONLY the divergent subset (documents selected by retrieval filter but rejected by educational filter). If the divergent subset contributes ≥2% absolute Recall@10 gain when added to the educational corpus, divergence is meaningful. This grounds "meaningful" in performance impact, not corpus statistics.

**Statistical power calculation:** For N=10K query test set (BEIR Natural Questions subset), 2% Recall@10 difference requires ~200 queries where divergent documents are uniquely relevant. With typical 1% per-query variance, we need |Δ| ≥ 0.02 ± 0.01 (two-tailed t-test, α=0.05, power=0.80). We'll need 3-5 replications with different random corpus samples to confirm the effect isn't sampling noise.

**Confound control:** We must verify that divergent documents aren't just *easier* to retrieve (e.g., shorter, more lexically distinct). Control experiment: measure average BM25 score for queries where divergent documents are relevant vs non-divergent documents. If divergent docs have systematically higher BM25 scores, the Recall gain could be a retrieval algorithm artifact, not quality.

This addresses Prof. Pax's concern about measurement validity: by controlling for retrieval difficulty, we isolate document quality effects from algorithmic bias.

**Key Points:**
- Divergence threshold grounded in performance: ≥2% Recall@10 gain from divergent subset
- Statistical power: 10K query test set, 3-5 replications, |Δ|≥0.02±0.01 (α=0.05, power=0.80)
- Confound control: Verify divergent docs aren't systematically easier to retrieve (BM25 score baseline)

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND Prof. Vera's confound control sparks an even stronger framing: what if we explicitly measure the "difficulty-adjusted quality gain"? Instead of raw Recall@10, we measure Recall@10 after normalizing by BM25 scores (essentially, "how much does document quality matter *beyond* lexical matching?").

This refinement addresses a deeper concern: if our retrieval-quality classifier simply learns to select documents with high keyword density (which both improves retrieval AND correlates with factual content), we haven't discovered a new quality dimension — we've just reinvented TF-IDF weighting. The novelty claim requires showing that our classifier captures quality signals orthogonal to lexical matching.

Here's how we operationalize it: Split BEIR Natural Questions into two subsets: (1) Lexical queries where BM25 succeeds (answer string appears in top-10 BM25 results), (2) Semantic queries where BM25 fails (answer requires paraphrase/inference). We predict our retrieval-quality corpus improves Recall@10 MORE on semantic queries than lexical queries, because that's where document quality beyond keyword matching matters.

**Specific prediction:** Retrieval-quality corpus achieves +4% Recall@10 on semantic queries vs +1% on lexical queries (both relative to perplexity baseline). If gains are uniform across query types, we've just improved corpus lexical coverage, not semantic quality.

This also connects to Prof. Rex's concern about annotation bias: semantic queries require human annotators to judge relevance beyond keyword matching, so if we validate on those queries specifically, we're measuring quality orthogonal to simple retrieval heuristics.

**Key Points:**
- Measure "difficulty-adjusted quality gain": Recall improvement beyond lexical matching
- Split queries by BM25 success: Lexical (BM25 succeeds) vs Semantic (BM25 fails)
- Key prediction: +4% Recall on semantic queries vs +1% on lexical (demonstrates quality beyond keywords)

---

### Exchange 14

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's semantic query validation is clever, but here's where I'd try to break it: what if "semantic queries where BM25 fails" are systematically harder not because they require better documents, but because they're ambiguous or require world knowledge retrieval can't provide?

Show me the evidence that improving corpus quality can actually rescue BM25-failed queries. If those queries fail because the information simply isn't in Common Crawl (e.g., recent events, niche technical details), no amount of filtering helps. We'd be measuring corpus coverage gaps, not quality.

Here's the validation that would convince me: manually audit a sample of 100 BM25-failed queries and categorize failure modes: (1) Information absent from corpus (coverage failure), (2) Information present but poorly retrieved (quality failure). If <50% are quality failures, the semantic query improvement might be undetectable — not because the hypothesis is wrong, but because the test set has low statistical power.

Additionally, what about the multi-hop concern? If semantic queries require synthesizing information across multiple documents, single-document quality might matter less than corpus diversity. Our retrieval-quality classifier optimizes individual document scores, but retrieval performance depends on inter-document complementarity. How do we measure whether filtered documents maintain sufficient diversity for multi-hop reasoning?

What would convince me: (1) Evidence that BM25-failed queries are predominantly quality failures, not coverage failures, (2) Measurement of corpus diversity (e.g., pairwise document similarity within top-1000 filtered docs), showing diversity is preserved alongside quality.

**Key Points:**
- BM25-failed queries may fail due to coverage gaps (info absent) not quality (info poorly retrieved)
- Required validation: Audit 100 queries, categorize failure modes (≥50% must be quality failures for test validity)
- Multi-hop concern: Single-doc quality optimization might reduce diversity needed for synthesis

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex raises real measurement challenges, but let's focus on what's actually tractable with existing datasets. Can we perform the failure mode audit (coverage vs quality) without collecting new annotations?

Here's a feasible approach: use Natural Questions' Wikipedia-derived answers as ground truth. If a BM25-failed query has its answer string present in the Common Crawl corpus (via simple string search), that's confirmed as a quality failure (info present, retrieval failed). If absent, it's a coverage failure. This avoids manual annotation while providing objective categorization.

The diversity measurement is simpler: compute average cosine similarity (using SBERT embeddings) between all pairs of documents in the top-1000 filtered corpus. High average similarity (>0.7) indicates low diversity; our prediction is retrieval-quality filtered corpus maintains similarity <0.6, matching or lower than perplexity baseline. This would show quality optimization doesn't homogenize the corpus.

But here's the fundamental limit: all these measurements assume Common Crawl contains relevant information. For true RAG deployment, corpus coverage matters as much as quality. Are we proposing that filtering improves quality at fixed coverage, or that filtering improves the coverage-quality Pareto frontier? The former is narrow but testable; the latter requires varying corpus size and measuring the trade-off curve.

Let's be realistic: demonstrating "better quality at fixed corpus size" is feasible with existing benchmarks. The stronger claim "better coverage-quality trade-offs" would require constructing multiple filtered corpora at different size thresholds and measuring Recall vs size curves. That's doable but adds complexity — do we need it for the core contribution?

**Key Points:**
- Feasible coverage vs quality audit: Check if answer strings exist in corpus (string search, no new annotations)
- Diversity measurement: Average pairwise cosine similarity <0.6 for filtered corpus
- Scope decision: Fixed-size quality improvement (feasible) vs coverage-quality Pareto frontier (complex)?

---

### Exchange 16

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Pax's feasibility framing clarifies our scope perfectly, but I want to push one more creative angle: what if the coverage-quality trade-off reveals an unexpected insight?

Imagine this: we measure Recall@K curves for K ∈ {1, 5, 10, 20, 50} across all three filtering methods (perplexity, educational, retrieval). If retrieval-quality filtering shows steeper early gains (higher Recall@1, Recall@5) but plateaus earlier than educational filtering, that suggests a quality-coverage specialization: retrieval filtering optimizes for "top-result precision" while educational filtering maintains "tail coverage." This would be a novel characterization of filtering strategies!

The implication: RAG system designers could choose filtering based on use case. Applications needing high top-1 accuracy (factoid QA, entity lookup) prefer retrieval-quality filtering. Applications needing broad coverage for exploratory search prefer educational/perplexity filtering. We've discovered a new quality-coverage axis, not just "retrieval is better."

This connects to FineWeb's finding that different filters serve different purposes: their educational filter trades general performance for knowledge-task gains. Our finding would be analogous: retrieval-quality filtering trades tail coverage for precision. The research direction opened: characterizing the multi-dimensional quality-coverage-diversity trade-off space for different filtering strategies.

NOW we're onto something genuinely novel: not "retrieval filtering is better," but "different filtering strategies occupy different positions in quality-coverage space, and we provide the first empirical map of that space for RAG corpora."

**Key Points:**
- Measure Recall@K curves across K∈{1,5,10,20,50} for all filtering methods
- Hypothesis: Retrieval filtering shows steep early gains (high precision) but earlier plateau (lower tail coverage)
- Contribution: Empirical map of quality-coverage trade-off space for RAG filtering strategies

---

### Exchange 17

🎯 **Dr. Sage** (Research Impact Evaluator):

Dr. Nova's quality-coverage trade-off map is compelling — this genuinely advances the field. The question we must ask is: does this reframe the contribution sufficiently to satisfy top-venue standards?

Here's where this matters: the contribution is no longer "we built a better filter for RAG," it's "we provide a methodology for empirically characterizing filtering trade-offs, enabling principled RAG system design." That's a meta-contribution — we're not just solving one instance, we're providing tools for others to analyze their filtering decisions.

The analogy to DataComp-LM is direct: they didn't just claim "DCLM-BASELINE is the best dataset," they provided a benchmark framework that others use to evaluate their own curation strategies [Li et al., 2024]. We're providing the RAG-specific analog: a systematic comparison framework for filtering methods along quality-coverage-diversity axes.

The broader implication: this opens research on **retrieval system design as multi-objective optimization**. Current practice treats "better corpus" as a scalar (higher Recall@10 = better), but we demonstrate it's multi-dimensional. Future work could apply multi-objective optimization (Pareto frontier search) to find filtering mixtures that optimize across quality/coverage/diversity simultaneously.

But I'm concerned: Dr. Nova proposes measuring Recall@K curves, but that's just one dimension (coverage at different thresholds). Where are the quality and diversity measurements in this framing? We need ALL three axes measured simultaneously to claim we're mapping the trade-off space.

**Key Points:**
- Contribution reframe: Methodology for characterizing filtering trade-offs (meta-contribution, not just one better filter)
- Analogous to DataComp-LM: Provide framework others use to evaluate their curation strategies
- Opens research on retrieval system design as multi-objective optimization (quality/coverage/diversity)

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis progressed from "build a better RAG filter" to "systematically map the quality-coverage-diversity trade-off space for retrieval corpus curation." The factorized classifier approach (multiple specialist classifiers for different retrieval modes) and the quality-coverage trade-off characterization represent genuine novelty beyond applying existing techniques to RAG.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis evolved multiple testable predictions with clear success/failure criteria: (1) ≥3% Recall@10 improvement from retrieval-quality filtering, (2) <60% overlap between retrieval-optimal and pretraining-optimal corpora, (3) +4% vs +1% Recall gains on semantic vs lexical queries. Confound controls (BM25 baseline normalization, coverage vs quality failure audit) make the experiment rigorous.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The contribution shifted from incremental to conceptual: demonstrating that data quality is task-specific and multi-dimensional (quality/coverage/diversity). The meta-contribution of providing a characterization framework for RAG filtering strategies has field-wide impact, analogous to DataComp-LM's benchmark contribution. Practical impact via RAG indexing efficiency (smaller corpus, same quality) strengthens significance.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The mechanism is theoretically sound after iterative refinement. Key feasibility validations: (1) Retrieval-quality classifier training is mathematically grounded via multi-task learning across BEIR queries, (2) Coverage vs quality failures can be audited via answer string search without new annotations, (3) Diversity measurement via SBERT pairwise similarity is computationally tractable. Scope restriction to factoid QA + extractive validation avoids intractable measurement challenges while remaining scientifically rigorous.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Core Hypothesis:** Retrieval-optimal corpus curation measurably diverges from pretraining-optimal curation, and this divergence can be systematically characterized along quality-coverage-diversity axes to enable principled RAG system design.

**Proposed Mechanism:** Train a factorized ensemble of specialist FastText classifiers, each targeting a specific retrieval failure mode (factoid density, argumentative coherence, technical precision). Positive training examples are stratified by pretraining quality scores (oversample low-educational, high-BEIR retrievals) to explicitly learn retrieval-utility signals independent of pretraining filters.

**Key Predictions:**
1. **Retrieval Performance:** Corpus filtered by retrieval-quality classifier achieves ≥3% higher Recall@10 on BEIR Natural Questions vs perplexity baseline (matched corpus size).
2. **Corpus Divergence:** Top-50K documents selected by retrieval vs educational filtering show <60% overlap, with divergent subset contributing ≥2% absolute Recall@10 gain (performance-grounded divergence).
3. **Semantic vs Lexical:** Retrieval-quality corpus shows +4% Recall gain on semantic queries (BM25-failed) vs +1% on lexical queries (BM25-succeeded), demonstrating quality beyond keyword matching.
4. **Quality-Coverage Trade-off:** Recall@K curves reveal retrieval filtering optimizes for top-result precision (steeper Recall@1, Recall@5) while educational filtering maintains better tail coverage (higher Recall@50), empirically mapping distinct positions in quality-coverage space.

**Experimental Approach:** Three-way controlled comparison (perplexity vs educational vs retrieval filtering) on Common Crawl subset. Validate via: (1) Pretraining quality (MMLU on 400M LM), (2) Retrieval quality (Recall@K on BEIR Natural Questions), (3) Corpus characteristics (overlap, diversity via SBERT similarity, coverage via answer string audit). Statistical rigor: 10K query test set, 3-5 replications, power=0.80.

**Scope:** Demonstrate methodology on factoid QA with extractive validation; provide generalizable recipe for task-specific retrieval corpus curation.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** BEIR relevance annotations may not correlate with downstream task performance (answer accuracy). Requires two-stage validation: train on annotations, validate on exact match QA accuracy.
- **Concern 2:** Single-document quality optimization might reduce inter-document diversity needed for multi-hop reasoning. Requires diversity measurement (pairwise SBERT similarity <0.6).
- **Mitigation Strategy:** Incorporate both validations in experimental design. If annotation-task correlation is low or diversity drops, refine classifier training to explicitly preserve diversity (add diversity term to loss function or use diversity-aware sampling for positive examples).

---

