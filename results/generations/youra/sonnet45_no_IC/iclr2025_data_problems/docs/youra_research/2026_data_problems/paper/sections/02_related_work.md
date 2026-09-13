# Related Work

Our work builds on three research threads: pretraining corpus filtering, retrieval benchmarks, and quality metrics for text data. We position our contribution as extending data-centric methods from pretraining to the retrieval domain, while systematically testing mechanistic hypotheses that prior work left implicit.

## Pretraining Corpus Filtering

The shift from heuristic filtering to model-based curation represents a major advance in pretraining data quality. Early work relied on perplexity thresholds—selecting documents with low GPT-2 perplexity as proxies for "high quality" (Wenzek et al., 2020). RefinedWeb demonstrated that careful application of perplexity filtering, combined with deduplication, could match human-curated datasets like C4 (Penedo et al., 2023).

DataComp-LM (Li et al., 2024) introduced a paradigm shift: instead of hand-crafting quality heuristics, train a classifier on positive examples (documents from high-quality corpora) and negative examples (low-quality documents). Their FastText-based approach enabled a 7B model trained on 40% less data to achieve 64% on MMLU, outperforming prior 7B models trained on larger corpora. Critically, DataComp-LM showed that quality is learnable—a classifier can capture quality signals beyond what perplexity or rule-based heuristics provide.

FineWeb-Edu (Penedo et al., 2024) demonstrated that quality is multidimensional. Their educational quality classifier—trained to distinguish FineWeb documents with high vs. low educational value—produced corpora that achieved +5.0pp MMLU gains compared to standard FineWeb filtering. However, these gains came with tradeoffs: the educational filter reduced corpus diversity and showed task-specific biases. This established an important principle: different downstream tasks may require different quality dimensions.

**Limitation for retrieval.** Both DataComp-LM and FineWeb optimize for pretraining objectives—perplexity reduction, language modeling loss, or knowledge-intensive QA tasks where the answer must be learned during pretraining. Retrieval operates differently: the model must locate and extract information present in the corpus at inference time, not internalize it during training. Whether perplexity or educational quality—both pretraining-derived signals—correlate with retrieval utility remains untested.

**Our contribution.** We apply the model-based filtering methodology to retrieval-specific training signals (BEIR success examples), using stratified sampling to enforce divergence from educational quality. Unlike prior work that validated against pretraining metrics, we measure retrieval performance (Recall@10) and test whether the quality signals learned differ mechanistically from pretraining quality.

## Retrieval Benchmarks and Evaluation

BEIR (Thakur et al., 2021) established a heterogeneous benchmark for zero-shot retrieval evaluation, spanning 18 datasets across factoid QA, argument retrieval, duplicate question detection, and domain-specific search tasks. BEIR's key insight was that retrieval models trained on MS MARCO often fail to generalize to out-of-domain tasks, revealing the need for more robust retrieval architectures. BEIR provides relevance judgments (qrels) that indicate which corpus documents are relevant for each query, enabling controlled evaluation of retrieval quality.

Dense Passage Retrieval (DPR; Karpukhin et al., 2020) demonstrated that bi-encoder architectures trained with contrastive learning could outperform BM25 on open-domain question answering. DPR encodes questions and passages into dense vectors, retrieving via nearest-neighbor search. On Natural Questions, DPR achieved 79.4% top-20 accuracy, substantially outperforming BM25 (59.1%). However, DPR's success depends critically on corpus coverage—retrieval cannot succeed if relevant documents are filtered out during corpus construction.

**Limitation for corpus curation.** BEIR measures retrieval model quality, not corpus quality. While BEIR's relevance annotations indicate which documents are useful for answering queries, no prior work has used BEIR as a training signal for corpus filtering. The retrieval community has focused on improving encoders and ranking functions, leaving corpus construction to pretraining-derived methods.

**Our contribution.** We leverage BEIR relevance annotations as supervised training data—treating documents from successful BEIR retrievals as positive examples of retrieval-quality text. This inverts the typical use of BEIR: instead of evaluating models on a fixed corpus, we evaluate corpora using a fixed model (DPR). Our stratified sampling ensures the classifier learns retrieval-specific signals orthogonal to educational quality.

## Quality Metrics for Text Data

Entity-based quality metrics have been used heuristically in corpus filtering pipelines, under the assumption that factual density correlates with informativeness. Wikipedia articles, for example, exhibit high named entity density compared to conversational text or narrative prose (Färber et al., 2018). However, the relationship between entity density and downstream task performance—particularly for retrieval—has not been rigorously tested.

Type-token ratio (TTR) and lexical diversity metrics capture vocabulary richness but do not directly measure factual content (McCarthy & Jarvis, 2010). Educational quality classifiers (Penedo et al., 2024) use features like perplexity, document structure, and n-gram statistics, but these features optimize for learnability (how well a model can internalize the text) rather than retrievability (how well the text supports fact lookup).

**Gap in mechanistic understanding.** Prior work assumes—but does not validate—that entity density, vocabulary diversity, or educational quality correlate with retrieval performance. No systematic test has measured whether classifiers trained on retrieval success examples actually learn these hypothesized features, nor whether such features differentially improve semantic vs. lexical query performance.

**Our contribution.** We explicitly test the entity density hypothesis by measuring NER-based factual density in classifier-selected corpora and comparing against perplexity-matched baselines. We further test whether high-density documents preferentially improve semantic queries (where BM25 lexical matching fails), providing the first mechanistic evaluation of retrieval-quality signals.

## Positioning Within Data-Centric ML

Our work contributes to the emerging data-centric machine learning paradigm (Zha et al., 2023), which shifts focus from model architecture to training data quality. Recent work has shown that data quality improvements can yield larger gains than architectural innovations (Gadre et al., 2024). However, most data-centric research focuses on image classification or language model pretraining. Retrieval-augmented generation introduces unique constraints—corpus quality affects inference-time performance rather than training-time learning—making it a distinct domain requiring specialized curation strategies.

**Summary.** Pretraining corpus filtering has matured from heuristic rules to learnable quality classifiers, but these methods optimize for pretraining objectives. Retrieval benchmarks measure model quality on fixed corpora, not corpus quality itself. Entity-based metrics are used heuristically without mechanistic validation. We address these gaps by training classifiers on retrieval-specific signals, measuring whether they learn hypothesized features (entity density), and testing differential performance on query types—providing the first systematic evaluation of retrieval-specific corpus quality.
