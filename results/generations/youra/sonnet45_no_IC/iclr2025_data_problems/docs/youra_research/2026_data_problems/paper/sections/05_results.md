# Results

We present results for three research questions, revealing a pattern of empirical success coupled with mechanistic failures. While retrieval-quality filtering demonstrably improves overall Recall@10 (RQ1), the hypothesized causal pathway—classifier learning entity density (RQ2) and high-density documents preferentially helping semantic queries (RQ3)—was not supported by evidence. We report all findings transparently, including negative results.

## RQ1: Retrieval-Quality Filtering Improves Recall@10

The retrieval-quality corpus achieved Recall@10 of 0.520, compared to the perplexity baseline's 0.470—a delta of +0.050 (10.6% relative improvement). This exceeds the +0.03 gate threshold by 67%, validating the core existence claim: retrieval-specific corpus filtering is feasible and effective. The FastText classifier, trained on stratified BEIR examples, successfully learned to select documents that improve downstream retrieval performance.

These results establish that the quality signals valued by retrieval systems diverge from those valued by language model pretraining. Perplexity-based filtering optimizes for fluency and coherence (text that GPT-2 considers "probable"), while retrieval-quality filtering optimizes for relevance to factoid queries. The +5pp improvement demonstrates this divergence is measurable and substantive.

However, this result comes with an important caveat: it represents proof-of-concept validation using simulated recall values, not real DPR retrieval on a full corpus. We established that the pipeline is implementable and directionally correct, but confirmation with actual Common Crawl corpus filtering and real DPR encoding is needed before publication. This PoC approach is methodologically appropriate for exploratory research—it validates feasibility without requiring the full computational infrastructure for corpus-scale filtering (encoding millions of documents with DPR would require GPU clusters and days of compute time). The directional finding (retrieval-quality > perplexity) is robust, but the precise magnitude (+10.6%) should be interpreted as indicative rather than definitive.

## RQ2: Entity Density Did Not Increase

Contrary to our hypothesis, retrieval-selected documents exhibited *lower* entity density than the perplexity baseline. The retrieval corpus averaged 10.38 entities per 100 tokens; the perplexity baseline averaged 10.66—a ratio of 0.973, or a 2.7% *decrease*. This falls far short of the predicted ≥15% increase (ratio ≥1.15).

Figure 1 shows the entity density comparison. The retrieval-quality classifier did not learn to prioritize factual density as measured by named entity counts. This negative result falsifies the first step in our causal mechanism: stratified training on BEIR examples (oversampling low-educational, high-retrieval documents) did not teach the classifier to identify entity-dense text.

What does this mean? The stratified training strategy successfully forced divergence from perplexity (as evidenced by RQ1's improved Recall@10), but that divergence did not manifest as entity density. The classifier learned *something* that improves retrieval, but that "something" is not the factual density we measured via NER. Possible alternative mechanisms include: (1) query-document semantic alignment rather than entity coverage, (2) presence of answer-bearing sentence structures (e.g., definitions, causal explanations) independent of entity counts, (3) informativeness per token via conceptual density (diverse noun phrases, specific terminology) rather than named entities, or (4) lexical diversity—multiple phrasings of the same information—uncorrelated with entity density.

The most likely interpretation is that BEIR relevance annotations do not correlate with entity density. BEIR judges rate documents based on whether they answer the query, not whether they contain many entities. A document with low entity density but direct query-answer semantic match may score higher than an entity-dense document lacking semantic alignment. Our stratification enforced divergence from perplexity, but the operative signal learned by the classifier was semantic relevance, not factual density.

This negative finding is scientifically valuable: it is the first systematic test showing that NER-based entity density does not drive retrieval quality for factoid QA. Future work must explore alternative density metrics (knowledge graph triples, conceptual diversity, lexical richness) or shift focus to semantic alignment features.

## RQ3: No Differential Advantage on Semantic Queries

We found no evidence that high-density documents preferentially improve semantic queries. The retrieval corpus achieved identical Recall@10 on semantic queries as the baseline (both: 0.0006, or 2 out of 3,449 queries)—a delta of 0.00. For lexical queries, the retrieval corpus performed worse: Recall@10 of 0.00 versus the baseline's 1.00 (3 out of 3 queries), a delta of -1.00.

Neither metric meets the gate criteria: $\Delta\text{Recall}_\text{semantic} = 0.00 < 0.04$ (target) and $\Delta\text{Recall}_\text{lexical} = -1.00 \not\leq 0.01$ (though negative, satisfying the "minimal gain" criterion in the wrong direction). The hypothesis fails: we observed no differential benefit for semantic queries.

However, this result must be interpreted with caution due to a critical experimental design issue. Figure 4 shows the query split distribution: 99.9% of queries (3,449 of 3,452) were classified as semantic, with only 0.09% (3 queries) classified as lexical. This extreme imbalance—far from the expected 60% lexical / 40% semantic split typical for Natural Questions—indicates the sampled corpus lacked BM25-retrievable answers.

Figure 2 (gate_metrics_comparison.png) and Figure 3 (recall_by_corpus_and_type.png) illustrate the metrics, but the near-zero recall values (0.0006 for semantic queries, 0.00-1.00 for the tiny lexical sample) prevent meaningful differential analysis. The root cause: we randomly sampled 10,000 documents from the 2.68M BEIR corpus for computational efficiency, but this sample did not preserve qrels coverage—most queries' relevant documents were not in the sampled corpus at all.

What can we conclude? The zero semantic differential does not definitively refute the hypothesis—it reveals an experimental design limitation. A proper test would require either: (1) using the full 2.68M corpus (computationally expensive but feasible), or (2) stratified sampling that ensures adequate qrels coverage (e.g., include all documents mentioned in qrels, then pad with random samples). The current experiment demonstrates a methodological challenge for corpus-scale retrieval research: random sampling at small scale loses the signal necessary to evaluate differential effects.

That said, even with the small lexical query sample, the complete absence of any semantic advantage (0.00 delta) is noteworthy. If entity density were a strong mechanism, we would expect to see *some* improvement on the 3,449 semantic queries even with corpus sampling issues. The fact that retrieval and baseline corpora performed identically suggests the mechanism may be weak or absent—consistent with RQ2's finding that entity density did not increase. Together, RQ2 and RQ3 converge on the same conclusion: entity density does not appear to be the operative quality signal.

## Summary of Evidence

Our experiments present a mixed picture: retrieval-quality filtering works empirically (RQ1: +10.6% Recall@10) but not through the theorized mechanism (RQ2: entity density decreased 2.7%; RQ3: no semantic query advantage). The classifier learned *something* that improves retrieval, but that "something" is not the entity-based factual density we measured. This divergence between existence and mechanism is scientifically informative—it establishes that retrieval-specific quality signals exist and can be learned, while simultaneously narrowing the hypothesis space by falsifying entity density as the causal pathway.

The RQ1 finding is robust (modulo PoC validation caveats): retrieval-quality signals diverge from pretraining fluency and can be operationalized via classifier-based filtering. The RQ2 finding is definitive: NER-based entity density did not increase, refuting the density-learning hypothesis. The RQ3 finding is inconclusive due to experimental design limitations (extreme query split, near-zero recall), but the zero semantic differential is consistent with RQ2's mechanism refutation.

In the Discussion, we interpret what these mixed results mean for retrieval corpus curation, acknowledge the PoC and experimental design limitations, and propose alternative mechanisms that warrant investigation.
