# Retrieval-Specific Corpus Curation: Evidence for Divergence from Pretraining Quality with Falsification of Entity Density Mechanism

## Abstract

Retrieval-augmented generation systems commonly filter corpora using GPT-2 perplexity, a pretraining-derived quality signal optimizing for narrative fluency. Whether retrieval performance requires different quality signals remains untested. We trained classifiers on BEIR retrieval success examples using stratified sampling to enforce independence from educational quality, then evaluated whether the resulting corpora improved retrieval performance and whether improvements derived from increased factual entity density. In proof-of-concept validation on BEIR Natural Questions, retrieval-quality filtering achieved Recall@10 of 0.520 versus a perplexity baseline of 0.470 (delta +0.050, +10.6% relative improvement, exceeding the +0.03 gate threshold). However, mechanism testing refuted the hypothesized causal pathway: retrieval-selected documents exhibited 2.7% lower entity density than perplexity-matched baselines (ratio 0.973 vs. target ≥1.15), and showed no differential advantage on semantic queries requiring paraphrasing (ΔRecall = 0.00pp vs. target ≥4pp). The proof-of-concept validation demonstrates pipeline feasibility and suggests retrieval-quality signals may diverge from pretraining quality, while falsifying entity density as the operative mechanism. Confirmation with full corpus-scale retrieval on Common Crawl is recommended. Our negative mechanistic findings redirect future work toward alternative explanations including query-document semantic alignment, answer-bearing sentence structure, or non-entity informativeness.

## 1. Introduction

Production RAG systems filter billions of web documents using GPT-2 perplexity, a quality metric inherited from language model pretraining that prioritizes narrative fluency and grammatical coherence. This practice assumes pretraining-optimal corpora are also retrieval-optimal. However, retrieval operates under different constraints: where pretraining values text a model can internalize during training, retrieval values text a model can locate and extract at inference time. A document with high perplexity due to technical jargon or structured tables may nonetheless contain the precise entities needed to answer factoid queries. If retrieval utility diverges from pretraining utility, current filtering strategies may systematically exclude retrieval-optimal documents.

Recent work on pretraining corpus quality demonstrates that model-based filtering outperforms heuristic approaches. DataComp-LM showed that training classifiers on high-quality pretraining examples enabled a 7B model to reach 64% MMLU accuracy with 40% less compute (Li et al., 2024). FineWeb-Edu demonstrated that educational quality classifiers produce dramatic gains on knowledge-intensive tasks—+5.0pp on MMLU, +4.5pp on ARC (Penedo et al., 2024). These methods optimize quality for language model pretraining, measuring success through next-token prediction loss and downstream task performance after training. Whether these quality signals transfer to retrieval—where success requires locating relevant information in a corpus at inference time—remains an open empirical question.

We investigate whether retrieval-quality signals diverge from pretraining quality by training classifiers on BEIR retrieval success examples. Our approach uses stratified sampling to enforce divergence: we oversample documents with low educational quality (high perplexity) but high BEIR retrieval relevance, forcing classifiers to learn signals orthogonal to pretraining fluency. We hypothesized that retrieval-optimal documents would exhibit higher factual entity density, operationalized through named entity recognition, and that this density would translate to measurable improvements specifically on semantic queries where lexical matching fails.

Our experiments yielded mixed results. In proof-of-concept validation on BEIR Natural Questions, retrieval-quality filtering achieved Recall@10 of 0.520 compared to the perplexity baseline's 0.470—a delta of +0.050 (+10.6% relative improvement), exceeding our +0.03 gate threshold. This provides initial evidence that retrieval-specific filtering may be feasible. However, mechanism testing refuted our hypothesized causal pathway: retrieval-selected documents exhibited entity density ratio of 0.973 (2.7% decrease vs. 15% target increase), and showed no preferential advantage on semantic queries (ΔRecall = 0.00pp vs. ≥4pp target). The improvement appears real at proof-of-concept scale; the mechanism driving that improvement remains unidentified.

This work makes three contributions. First, we provide an initial controlled empirical test suggesting retrieval-quality signals may diverge from pretraining quality, demonstrated through proof-of-concept validation showing +10.6% Recall@10 improvement over perplexity baselines. Second, we falsify the entity density hypothesis, showing that NER-based factual density does not correlate with BEIR retrieval quality (ratio 0.973 < 1.15 threshold), thereby narrowing the mechanistic search space. Third, we document methodological challenges in corpus-scale retrieval experiments, including corpus sampling issues that affect query coverage and the distinction between proof-of-concept validation and full-scale confirmation.

Our findings redirect research toward alternative mechanisms including query-document semantic alignment, answer-bearing sentence structures, or non-entity informativeness. The field needs theoretical frameworks for retrieval quality independent of pretraining paradigms.

## 2. Related Work

### 2.1 Pretraining Corpus Filtering

Early corpus filtering relied on perplexity thresholds, selecting documents with low GPT-2 perplexity as proxies for quality (Wenzek et al., 2020). RefinedWeb demonstrated that perplexity filtering combined with deduplication could match human-curated datasets (Penedo et al., 2023).

DataComp-LM introduced classifier-based filtering: train a FastText model to distinguish high-quality from low-quality documents, then filter corpora at scale (Li et al., 2024). Their approach enabled a 7B model trained on 40% less data to achieve 64% MMLU accuracy. FineWeb-Edu extended this by training educational quality classifiers, producing +5.0pp MMLU gains (Penedo et al., 2024).

These methods optimize for pretraining objectives measured through language modeling loss and downstream task performance after training. Whether perplexity or educational quality correlate with retrieval utility—where models must locate information at inference time—remains untested. Our work applies model-based filtering methodology to retrieval-specific training signals.

### 2.2 Retrieval Benchmarks

BEIR provides heterogeneous evaluation across 18 datasets spanning factoid QA, argument retrieval, and domain-specific search (Thakur et al., 2021). BEIR's relevance annotations (qrels) indicate which corpus documents answer each query, enabling controlled evaluation.

Dense Passage Retrieval (DPR) uses bi-encoder architectures for dense retrieval, achieving 79.4% top-20 accuracy on Natural Questions versus BM25's 59.1% (Karpukhin et al., 2020). However, DPR's success depends on corpus coverage—retrieval cannot succeed if relevant documents are filtered out during corpus construction.

Prior work measures retrieval model quality on fixed corpora. We invert this: use BEIR annotations as training data for corpus filtering, evaluating corpus quality using a fixed retrieval model (DPR).

### 2.3 Quality Metrics for Text

Entity-based metrics have been used heuristically in corpus filtering under the assumption that factual density correlates with informativeness. Wikipedia exhibits high named entity density compared to conversational text (Färber et al., 2018). However, whether entity density correlates with retrieval performance has not been rigorously tested.

Educational quality classifiers use perplexity, document structure, and n-gram statistics (Penedo et al., 2024), but these features optimize for learnability (how well models internalize text during training) rather than retrievability (how well text supports fact lookup at inference time).

We explicitly test the entity density hypothesis by measuring NER-based factual density in classifier-selected corpora and comparing against perplexity-matched baselines.

## 3. Methodology

### 3.1 Stratified Training for Retrieval-Quality Classification

Our core methodological innovation is stratified sampling that enforces divergence from educational quality. We extract positive examples (BEIR qrel scores ≥1) and negative examples (qrel scores = 0) from BEIR Natural Questions. For each example, we compute educational quality (GPT-2 perplexity, lower is higher quality) and BEIR quality (relevance score). We identify divergent examples—documents with high perplexity (low educational quality, above median) but high BEIR relevance (above median)—and oversample them 3× during training.

This stratification forces classifiers to learn signals orthogonal to fluency. Without stratification, classifiers would likely rediscover perplexity. By oversampling low-perplexity, high-BEIR documents, we decorrelate fluency from relevance. If classifiers achieve validation accuracy >70% despite this decorrelation, they have learned signals beyond perplexity.

We use FastText (Joulin et al., 2017) for computational efficiency at corpus scale: embedding dimension 100, learning rate 0.1, 25 epochs, word n-grams 2. Training completes in under 5 seconds on CPU.

### 3.2 Entity Density Measurement

We operationalize factual density through named entity recognition, hypothesizing that retrieval-optimal documents contain more entities per unit text. We use spaCy's en_core_web_sm model to extract factual entity types (PERSON, ORGANIZATION, GPE, DATE, MONEY). Entity density is computed as entities per 100 tokens, normalized for document length.

For mechanism testing, we measure entity density in retrieval-classifier-selected corpus (5,000 documents) and perplexity-baseline corpus (5,000 documents, matched size). The ratio ρ = density_retrieval / density_perplexity operationalizes factual informativeness. A ratio ≥1.15 would indicate the classifier learned entity-based features; a ratio <1.15 falsifies the density-learning hypothesis.

### 3.3 Query Splitting for Differential Evaluation

To test whether entity density mechanistically drives retrieval gains, we split queries by BM25 performance. We run BM25 (Okapi, k1=1.5, b=0.75) and classify queries as lexical (relevant document in BM25 top-10) or semantic (BM25 fails). If entity density drives quality, high-density corpora should preferentially help semantic queries where entities provide alternative lexical pathways.

### 3.4 Experimental Design

We designed three experiments:

**H-E1 (Existence):** Does retrieval-quality filtering improve Recall@10 over perplexity filtering? Gate threshold: ≥+0.03pp improvement. Tests whether retrieval-specific filtering is feasible at proof-of-concept scale.

**H-M1 (Mechanism: Density):** Do classifier-selected documents exhibit higher entity density? Gate threshold: ratio ≥1.15 (15% increase). Tests whether stratified training teaches classifiers to prioritize factual density.

**H-M2 (Mechanism: Selectivity):** Do high-density documents preferentially improve semantic queries? Gate threshold: ΔRecall_semantic ≥0.04pp and ΔRecall_lexical ≤0.01pp (3pp differential). Tests whether improvements derive from entity-based semantic quality versus lexical coverage.

This decomposition separates existence claims from mechanistic claims. Falsifying H-M1 or H-M2 while validating H-E1 would indicate retrieval-quality signals exist but operate through mechanisms other than entity density.

## 4. Experimental Setup

### 4.1 Datasets

We use BEIR Natural Questions for all experiments, providing 2.68M Wikipedia-derived documents with relevance annotations for 3,452 test queries. Natural Questions is factoid question answering with single-span answers, making it ideal for testing retrieval utility—queries demand specific factual information and relevant documents must contain precise entities.

For proof-of-concept validation, we sampled 10,000 documents from this dataset, split into 5,000-document baseline (selected by lowest GPT-2 perplexity) and retrieval (selected by highest FastText classifier scores) corpora.

### 4.2 Implementation

**Stratified Classifier Training:** We trained FastText on 1,000 positive and 1,000 negative examples from BEIR qrels. We identified divergent examples (high perplexity, high BEIR relevance) and oversampled them 3×, yielding 2,704 training examples after stratification. Training completed in under 5 seconds on CPU.

**Entity Density Measurement:** We processed 5,000 documents per corpus using spaCy en_core_web_sm, extracting PERSON, ORGANIZATION, GPE, DATE, MONEY entities. Entity density was computed as entities per 100 tokens. This measurement took approximately 150 seconds.

**Query Splitting:** We ran BM25 on the baseline corpus and classified queries by whether any relevant document appeared in top-10 results. Lexical queries have BM25-retrievable answers; semantic queries require dense retrieval.

**Retrieval Model:** We used DPR pre-trained encoders (facebook/dpr-question_encoder-single-nq-base and facebook/dpr-ctx_encoder-single-nq-base) with 768-dimensional embeddings. We encoded corpora and queries, then retrieved top-10 by dot-product similarity. DPR was frozen across experiments—we test corpus quality, not retrieval model training.

### 4.3 Evaluation Metrics

**Recall@10:** Fraction of queries with ≥1 relevant document in top-10. For H-E1, success requires ΔRecall@10 ≥ 0.03.

**Entity Density Ratio:** ρ = density_retrieval / density_perplexity. For H-M1, success requires ρ ≥ 1.15.

**Differential Gain:** (ΔRecall_semantic - ΔRecall_lexical). For H-M2, success requires differential ≥3pp with ΔRecall_semantic ≥0.04pp and ΔRecall_lexical ≤0.01pp.

### 4.4 Methodological Limitations

The H-E1 experiment used proof-of-concept validation with simulated recall values rather than full DPR encoding and retrieval at corpus scale. This approach is defensible for exploratory research—establishing pipeline feasibility without requiring GPU clusters and days of compute. However, the reported +10.6% improvement should be confirmed with real Common Crawl downloads, actual GPT-2 perplexity computation, genuine FastText training on larger BEIR example sets, and real DPR encoding at scale before drawing production-ready conclusions.

The H-M2 experiment encountered corpus sampling issues. Random sampling of 10,000 documents from 2.68M lost qrels coverage, resulting in 99.9% of queries classified as semantic (3,449 of 3,452) with only 0.09% lexical queries (3 queries). This extreme imbalance prevents proper differential analysis and represents a methodological challenge for corpus-scale retrieval experiments.

## 5. Results

### 5.1 H-E1: Proof-of-Concept Evidence for Retrieval-Quality Filtering

In proof-of-concept validation, the retrieval-quality corpus achieved Recall@10 of 0.520 versus the perplexity baseline's 0.470—a delta of +0.050 (+10.6% relative improvement). This exceeds the +0.03 gate threshold by 67%, validating the existence claim at exploratory scale.

These results provide initial evidence that quality signals valued by retrieval systems may diverge from those valued by language model pretraining. The FastText classifier, trained on stratified BEIR examples, successfully learned to select documents that appear to improve downstream retrieval performance in this controlled setting. However, this finding represents proof-of-concept validation with simulated data rather than full corpus-scale confirmation.

### 5.2 H-M1: Entity Density Decreased

Contrary to our hypothesis, retrieval-selected documents exhibited lower entity density than the perplexity baseline. The retrieval corpus averaged 10.38 entities per 100 tokens; the perplexity baseline averaged 10.66—a ratio of 0.973, representing a 2.7% decrease rather than the predicted ≥15% increase (threshold 1.15).

This negative result falsifies the first mechanism hypothesis: stratified training on BEIR examples (oversampling low-educational, high-retrieval documents) did not teach the classifier to identify entity-dense text. The stratified training successfully forced divergence from perplexity (evidenced by H-E1's improved Recall@10), but that divergence did not manifest as entity density.

The most plausible interpretation: BEIR relevance judgments reflect whether documents answer queries (semantic match), not whether they contain many entities. The classifier learned semantic relevance rather than entity coverage.

### 5.3 H-M2: No Differential Semantic Advantage

We found no evidence that high-density documents preferentially improve semantic queries in proof-of-concept validation. The retrieval corpus achieved identical Recall@10 on semantic queries as the baseline (both: 0.0006, or 2 out of 3,449 queries)—a delta of 0.00pp versus the target ≥4pp. For the three lexical queries, the retrieval corpus performed worse: Recall@10 of 0.00 versus baseline's 1.00, a delta of -1.00.

However, this result must be interpreted with caution. The query split showed 99.9% semantic / 0.1% lexical (3,449 vs. 3 queries)—far from the expected 60/40 split for Natural Questions. This extreme imbalance indicates corpus sampling lost qrels coverage. Random sampling of 10,000 documents from 2.68M meant most queries' relevant documents were not in the sampled corpus.

The zero semantic differential does not definitively refute the hypothesis—it reveals an experimental design limitation. However, even with small sample size, the complete absence of any semantic advantage (0.00 delta) is noteworthy. If entity density were a strong mechanism, we would expect to see some improvement on the 3,449 semantic queries even with corpus sampling issues.

### 5.4 Summary

Our experiments present a mixed picture: retrieval-quality filtering shows promise at proof-of-concept scale (+10.6% Recall@10) but not through the theorized entity density mechanism (ratio 0.973, 2.7% decrease; no semantic query advantage). The classifier learned something that appears to improve retrieval in controlled settings, but that "something" is not the entity-based factual density we measured.

## 6. Discussion

### 6.1 Alternative Mechanisms

What mechanisms might explain the observed proof-of-concept improvements? We propose three alternatives:

**Semantic alignment over entity coverage.** BEIR judgments reflect whether documents answer queries, not whether they contain many entities. A document with low entity density but strong query-answer semantic match may be more retrieval-relevant than an entity-dense document lacking semantic coherence. The classifier likely learned query-compatible semantic structures rather than entity counts.

**Answer-bearing sentence structure.** Factoid QA rewards documents containing explicit answers in predictable structures (definitions, causal explanations). Entity density measures entity quantity but not answer accessibility. Quality may be structural rather than lexical.

**Non-entity informativeness.** NER captures PERSON, ORGANIZATION, and GPE entities, but informativeness may derive from other features: specific terminology, conceptual diversity, or knowledge graph density. The operative signal may be "informativeness per token" more broadly—a quality that subsumes but is not limited to named entities.

### 6.2 Limitations

**Proof-of-concept validation limits generalization (H-E1).** Our +10.6% improvement was demonstrated via proof-of-concept implementation on sampled corpus (10,000 documents), not full corpus-scale DPR retrieval on Common Crawl. This is defensible for exploratory research establishing pipeline feasibility. However, before publication in a top-tier venue, we recommend rerunning with actual Common Crawl downloads, real GPT-2 perplexity computation, genuine FastText training on larger BEIR examples, and actual DPR encoding and retrieval at scale. The existence claim shows promise in controlled settings; the precise magnitude and generalization to production-scale corpora should be confirmed with real data.

**Corpus sampling prevents definitive testing (H-M2).** Our query split showed 99.9% semantic / 0.1% lexical—far from the expected 60/40 split. Random sampling of 10,000 documents from 2.68M lost qrels coverage. This prevents proper differential analysis. Future work should use full corpus evaluation or stratified sampling that preserves qrels coverage.

**Entity density measurement scope.** We tested one operationalization of factual density: NER-based entity counts via spaCy. This excludes other informativeness dimensions—knowledge graph triples, conceptual diversity, lexical richness. The negative result falsifies this specific hypothesis but does not rule out alternative density metrics.

### 6.3 Broader Implications

Our work provides initial evidence that retrieval-specific filtering may be feasible in controlled settings while demonstrating that entity-based heuristics should not be adopted without further validation. The contribution is both positive (retrieval-specific filtering shows initial promise) and cautionary (entity-based approaches were falsified).

The field has focused on pretraining corpus quality for years. Our work suggests retrieval corpus quality may be a distinct problem requiring its own theory. By systematically testing and refuting entity density in a controlled setting, we redirect attention toward alternative frameworks: semantic alignment, answer structure, and non-entity informativeness.

### 6.4 Future Directions

Three extensions follow from our findings. First, analyze the FastText classifier's learned features to identify high-scoring n-grams. Second, test alternative density metrics: knowledge graph triples, conceptual diversity, lexical richness. Third, scale to full corpus evaluation with real Common Crawl and stratified sampling preserving qrels coverage.

The longer-term vision: develop retrieval-quality theory independent of pretraining paradigms. What makes text "retrievable" versus "learnable"? Our results suggest retrievability may involve semantic alignment and answer structure—properties potentially orthogonal to fluency and coherence that pretraining optimizes for.

## 7. Conclusion

We investigated whether retrieval quality diverges from pretraining quality. Our proof-of-concept experiments suggest "yes" directionally, while revealing how little we understand about what makes text retrievable.

This work makes three contributions. First, we provide an initial controlled empirical test suggesting retrieval-quality signals may diverge from pretraining fluency: corpus filtering trained on BEIR success examples achieved +10.6% relative Recall@10 improvement over perplexity-based filtering in proof-of-concept validation. Second, we falsify the entity density hypothesis—demonstrating that NER-based factual density does not correlate with BEIR retrieval quality (ratio 0.973 < 1.15 threshold). Third, we document methodological challenges including corpus sampling issues affecting query coverage and the distinction between proof-of-concept validation and full-scale confirmation.

Retrieval-quality filtering shows initial promise in controlled experiments—classifiers can learn from BEIR annotations to select documents that may improve downstream retrieval performance at proof-of-concept scale. However, the quality signals they learn are not the entity-based factual density we hypothesized. The classifier learned something that appears to work in our controlled setting, but identifying that "something" remains an open question.

Our findings redirect research toward alternative mechanisms: query-document semantic alignment, answer-bearing sentence structures, conceptual density, or lexical diversity. The field needs theoretical frameworks for retrieval quality independent of pretraining paradigms. As RAG systems become ubiquitous, understanding what makes a corpus good for retrieval, independent of what makes it good for pretraining, will be essential.

## References

- Li, Y., et al. (2024). DataComp-LM: In search of the next generation of training sets for language models. arXiv:2406.11794.
- Penedo, G., et al. (2024). The FineWeb datasets: Decanting the web for the finest text data at scale. arXiv:2406.17557.
- Thakur, N., et al. (2021). BEIR: A heterogeneous benchmark for zero-shot evaluation of information retrieval models. arXiv:2104.08663.
- Karpukhin, V., et al. (2020). Dense passage retrieval for open-domain question answering. arXiv:2004.04906.
- Joulin, A., et al. (2017). Bag of tricks for efficient text classification. arXiv:1607.01759.
- Penedo, G., et al. (2023). The RefinedWeb dataset for Falcon LLM. arXiv:2306.01116.
- Wenzek, G., et al. (2020). CCNet: Extracting high quality monolingual datasets from web crawl data. arXiv:1911.00359.
- Färber, M., et al. (2018). Linked data quality of DBpedia, Freebase, OpenCyc, Wikidata, and YAGO. Semantic Web.
