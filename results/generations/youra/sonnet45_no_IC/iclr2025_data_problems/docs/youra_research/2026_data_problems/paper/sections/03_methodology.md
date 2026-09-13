# Methodology

To test whether retrieval-quality signals diverge from pretraining quality, we design a corpus filtering methodology that enforces this divergence explicitly. Our approach trains text classifiers on stratified examples—oversampling documents with low educational quality (high perplexity) but high retrieval success (high BEIR relevance)—then measures whether the resulting corpus exhibits hypothesized quality signals and improved retrieval performance.

## Research Questions and Experimental Design

We structure our investigation around three testable hypotheses, following the verification protocol established in Phase 2B:

**H-E1 (Existence).** Retrieval-quality filtered corpora achieve ≥3pp higher Recall@10 on Natural Questions compared to perplexity-filtered baselines (matched corpus size). This establishes whether retrieval-specific filtering is feasible at all.

**H-M1 (Mechanism: Density).** Classifier-selected documents exhibit ≥15% higher named entity density than perplexity-matched controls. This tests whether stratified training successfully learns factual density as a quality signal.

**H-M2 (Mechanism: Selectivity).** High-density documents improve semantic queries (BM25-failed) by ≥4pp Recall@10, while improving lexical queries (BM25-succeeded) by ≤1pp. This tests whether quality improvements are mechanistically driven by entity density rather than general lexical coverage.

This hypothesis decomposition allows us to separate existence claims (does retrieval-specific filtering work?) from mechanistic claims (does it work via entity density?). Falsifying mechanisms while validating existence narrows the search space for future theories.

## Stratified Training for Retrieval-Quality Classification

Our core methodological innovation is stratified sampling that forces classifiers to learn signals orthogonal to educational quality. Standard supervised learning on BEIR examples would risk the classifier simply rediscovering perplexity: if high-BEIR-relevance documents also have low perplexity, a naive classifier might learn fluency rather than retrieval-specific features.

**Training data construction.** We extract positive and negative examples from BEIR Natural Questions:
- **Positive class:** Documents from the BEIR corpus with qrel scores ≥1 (relevant to at least one query)
- **Negative class:** Documents with qrel scores of 0 (not relevant to any query)

For each example, we compute two quality scores:
- **Educational quality:** GPT-2 perplexity (lower = higher quality, following FineWeb-Edu methodology)
- **BEIR quality:** Relevance score from BEIR annotations (higher = more useful for retrieval)

**Stratification protocol.** We identify *divergent examples*—documents with high perplexity (low educational quality, above median) but high BEIR relevance (above median). These represent documents that retrieval values but pretraining would discard. We oversample divergent examples 3× during training, forcing the classifier to weight retrieval-specific features more heavily than fluency.

**Classifier architecture.** Following DataComp-LM, we use FastText (Joulin et al., 2017) for computational efficiency at corpus scale. FastText learns shallow text representations via word n-gram embeddings, making it suitable for filtering millions of documents. We train with hyperparameters: embedding dimension 100, learning rate 0.1, 25 epochs, bigram features (n=2).

**Why this approach enforces divergence.** Without stratification, a classifier trained on BEIR examples would likely learn to predict relevance using perplexity as a proxy—mimicking educational quality filtering. By oversampling low-perplexity, high-BEIR documents, we create a training distribution where fluency is decorrelated from relevance, forcing the classifier to discover alternative features. If the classifier achieves validation accuracy >70% despite this decorrelation, it has learned signals beyond perplexity.

## Entity Density as a Mechanistic Proxy

We operationalize factual density through named entity recognition, under the hypothesis that retrieval-optimal documents contain more entities per unit text.

**NER protocol.** We use spaCy's `en_core_web_sm` model to extract named entities from documents. Entity density is computed as:

$$
\text{density}(d) = \frac{|\{e \in d : e \text{ is PERSON, ORG, GPE, ...}\}|}{|\text{tokens}(d)|} \times 100
$$

This yields entities per 100 tokens, normalized for document length. We focus on factual entity types (PERSON, ORGANIZATION, GPE, DATE, MONEY) rather than linguistic entities (e.g., ORDINAL), following the hypothesis that factual content drives retrieval utility.

**Comparative evaluation.** For H-M1, we measure:
- Entity density in retrieval-classifier-selected corpus (50K documents)
- Entity density in perplexity-baseline corpus (50K documents, matched size)
- Ratio: $\rho = \text{density}_\text{retrieval} / \text{density}_\text{perplexity}$

A ratio ≥1.15 would indicate the classifier successfully learned entity-based features. A ratio <1.15 falsifies the density-learning hypothesis.

**Why entity density?** Named entities serve as a tractable proxy for factual informativeness. Questions in Natural Questions typically ask about entities ("Who founded Microsoft?", "When did World War II end?"), and relevant documents must mention these entities. Entity density also correlates with information compression: documents with high entity density convey more facts per token, aligning with the intuition that retrieval values informativeness over narrative fluency.

## Query Splitting for Mechanism Testing

To test whether entity density mechanistically drives retrieval gains, we split queries by whether BM25 lexical matching succeeds or fails (H-M2).

**Query classification protocol:**
1. Run BM25 (Okapi, k1=1.5, b=0.75) on the perplexity-baseline corpus
2. For each query, check if any relevant document (qrel score ≥1) appears in BM25's top-10 results
3. Classify as **lexical query** if BM25 succeeds (relevant doc in top-10), **semantic query** if BM25 fails

**Rationale.** Lexical queries are answerable via keyword matching—BM25 locates relevant documents by overlapping terms. Semantic queries require understanding beyond keywords: the question and answer may use different terminology, demanding dense retrieval or paraphrasing. If entity density drives retrieval quality, high-density documents should preferentially help semantic queries (where entities provide alternative lexical pathways) rather than lexical queries (already solved by BM25).

**Differential metric.** We compute:
- $\Delta\text{Recall}_\text{semantic} = \text{Recall@10}_\text{retrieval}^\text{semantic} - \text{Recall@10}_\text{baseline}^\text{semantic}$
- $\Delta\text{Recall}_\text{lexical} = \text{Recall@10}_\text{retrieval}^\text{lexical} - \text{Recall@10}_\text{baseline}^\text{lexical}$

H-M2 passes if $\Delta\text{Recall}_\text{semantic} \geq 0.04$ and $\Delta\text{Recall}_\text{lexical} \leq 0.01$—a 3pp differential gain. Uniform gains ($\Delta\text{Recall}_\text{semantic} \approx \Delta\text{Recall}_\text{lexical}$) would indicate improved lexical coverage, not entity-driven semantic quality.

## Datasets and Evaluation

**Corpus source.** We sample 100K documents from Common Crawl (CC-MAIN-2024-10), applying standard preprocessing: HTML extraction, deduplication (hash-based), language filtering (English via fastText LID), and length filtering (50-500 tokens per document). This simulates realistic web-scale corpus construction.

**Training data.** BEIR Natural Questions provides 2.68M corpus documents with relevance annotations for 3,452 test queries. We sample 1,000 positive and 1,000 negative examples for classifier training, stratifying as described above.

**Evaluation protocol.** Following BEIR conventions, we use Dense Passage Retrieval (DPR; Karpukhin et al., 2020) as the retrieval model:
- Question encoder: `facebook/dpr-question_encoder-single-nq-base`
- Context encoder: `facebook/dpr-ctx_encoder-single-nq-base`
- Similarity: Dot product of 768-dimensional embeddings
- Metric: Recall@10 (fraction of queries with ≥1 relevant document in top-10)

We compare three filtering methods:
1. **Perplexity baseline:** Select documents with lowest GPT-2 perplexity
2. **Educational quality:** FineWeb-Edu style classifier (trained on educational examples)
3. **Retrieval quality (ours):** Stratified classifier trained on BEIR examples

All corpora are fixed at 50K documents for H-M1/H-M2 experiments (10K for H-E1 proof-of-concept) to ensure controlled comparison.

## Design Choices and Rationale

**Why stratified sampling rather than adversarial training?** Adversarial methods (e.g., training a classifier to maximize retrieval quality while minimizing correlation with perplexity) require differentiable objectives and feature-level annotations. Stratified sampling is simpler, more interpretable, and operates at the data-selection level without modifying the learning algorithm.

**Why FastText rather than transformer-based classifiers?** Computational efficiency. Filtering 100K documents with BERT-based classifiers requires GPU inference and is ~100× slower than FastText. For corpus-scale filtering (millions of documents), FastText's speed is critical. DataComp-LM validated that FastText quality classification is competitive with more complex models.

**Why focus on Natural Questions?** Natural Questions is factoid QA with single-span answers, making it ideal for controlled experiments. Questions are derived from real Google searches, ensuring ecological validity. The BEIR version provides standardized relevance judgments and a large corpus (2.68M documents), enabling statistical power. Extension to other BEIR tasks (argument retrieval, domain-specific search) is future work.

**Why 50K corpus size?** Balances statistical power with computational constraints. Larger corpora (1M+) require hours of DPR encoding and gigabytes of embedding storage. 50K documents provide sufficient diversity for entity density measurement while enabling rapid iteration. Our proof-of-concept H-E1 uses 10K for initial validation.

**Limitations.** Stratified sampling assumes sufficient divergent examples exist in BEIR. If educational quality and BEIR relevance strongly correlate, few examples will meet the "low-perplexity, high-BEIR" criterion, limiting the stratification signal. We address this by reporting stratification statistics (number of divergent examples, oversampling ratio) and validating classifier accuracy on held-out data. Additionally, NER-based entity density may miss other forms of informativeness (e.g., conceptual density, knowledge graph triples), motivating alternative metrics in future work.

## Summary

Our methodology enforces retrieval-pretraining divergence through stratified classifier training, measures mechanistic hypotheses via entity density evaluation, and tests selectivity through query splitting. This design allows falsification: if H-E1 passes but H-M1 fails, retrieval-quality filtering works but not via entity density. If H-M2 fails, gains are due to lexical coverage rather than semantic quality. By separating existence from mechanism, we can validate feasibility while refuting specific causal pathways—advancing both practical corpus construction and theoretical understanding of retrieval-specific quality signals.
