# 4. Experimental Setup

## 4.1 Research Questions

We design experiments to answer the following questions, each mapping to a specific claim in the three-zone phase diagram hypothesis:

**RQ1:** Do benchmark items distribute meaningfully across lexical, semantic, and indeterminate strata when corpus-side geometry features are computed using 50K-document corpus samples?

**RQ2:** Do n-gram detectors exhibit recall separation between lexical (≥ 0.80) and semantic (≤ 0.40) strata, confirming that strata capture orthogonal signal types?

**RQ3:** Does Min-K%++ F1 vary across corpora (variance ≥ 0.15), indicating that MIA-based detector sensitivity is corpus-dependent and thus geometry-predictable?

RQ1 is the existence prerequisite: the routing hypothesis can only be tested if strata are non-empty. RQ2–RQ3 test the detector sensitivity predictions that would motivate a routing classifier.

## 4.2 Benchmarks

| Benchmark | HuggingFace ID | Split | Items | Type |
|-----------|---------------|-------|-------|------|
| MMLU | `cais/mmlu` (all) | test | 14,042 | NLU factual QA |
| HellaSwag | `Rowan/hellaswag` | validation | 10,042 | NLU commonsense completion |
| GSM8K | `openai/gsm8k` (main) | test | 1,319 | Math reasoning |
| **Total** | | | **25,403** | |

We include three benchmarks to capture benchmark heterogeneity: MMLU and HellaSwag are standard NLU benchmarks expected to overlap with general web corpora; GSM8K is a math reasoning benchmark expected to have different overlap characteristics.

## 4.3 Pretraining Corpora

| Corpus | HuggingFace ID | N-gram Index Size | SBERT Vecs | Docs Sampled |
|--------|---------------|------------------|------------|--------------|
| The Pile | `monology/pile-uncopyrighted` | 37,678,937 n-grams | 50,000 | 50,000 |
| C4 | `allenai/c4` (en) | 17,182,929 n-grams | 50,000 | 50,000 |
| FineWeb* | `HuggingFaceFW/fineweb` (sample-10BT) | 25,260,267 n-grams | 50,000 | 50,000 |

*FineWeb was substituted for RedPajama-Data-1T due to data access constraints at experiment time. FineWeb and RedPajama share similar general web-crawl characteristics (Common Crawl base), though deduplication strategies differ. We note this substitution as a limitation (Section 6).

## 4.4 LLM Models

For MIA-based detectors (Min-K%++, DC-PDD), we use:

- **Pythia-6.9B** (`EleutherAI/pythia-6.9b`): target model for Min-K%++ and DC-PDD. Pythia is trained on The Pile, providing a known-corpus positive control.
- **Pythia-2.8B** (`EleutherAI/pythia-2.8b`): reference model for DC-PDD log-likelihood ratio computation.

Both models loaded in bfloat16 on NVIDIA H100 NVL (CUDA_VISIBLE_DEVICES=1, GPU 4).

## 4.5 Implementation Details

**N-gram index.** 13-gram inverted index built using the EleutherAI lm-evaluation-harness pipeline: `generate_13_grams.py` → `sort_13_gram_buckets.py` → `compress_and_package.py`. Per-item max overlap computed by scanning sorted buckets.

**SBERT index.** FAISS IndexFlatIP over `all-MiniLM-L6-v2` embeddings (normalized, 384-dim). Corpus documents encoded at batch size 256. *Note:* In the executed experiment, the FAISS index was built over the same 50K randomly-streamed documents used for the n-gram index, not over a top-k retrieved set. This is the implementation deviation that causes stratum collapse (Section 5.2).

**Detector implementations:**
- *NgramDetector*: binary flag + max 13-gram count per item.
- *EmbeddingDetector*: cosine threshold (default 0.8) against FAISS index.
- *MinkPPDetector*: Min-K%++ with k=20% default; Pythia-6.9B.
- *DCPDDDetector*: intended to compute log P_target − log P_ref; actual implementation uses −ref_log_prob only (advisory bug, see Section 5.3).
- *ConStatDetector*: intended to use `llmsanitize.contamination.constat()` API; actual implementation uses a custom heuristic (advisory bug, see Section 5.3).

**Stratum thresholds:** 75th percentile of each geometry feature computed pooled across all benchmark items and all three corpora.

**Hardware and runtime:** NVIDIA H100 NVL, conda env `youra-h-e1` (Python 3.10, PyTorch, sentence-transformers, FAISS). Total experiment runtime: 5,676 seconds (~94 minutes). Coder-Validator cycles: 1/5.

## 4.6 Evaluation Metrics

| Metric | Definition | Target (h-e1 gate) |
|--------|-----------|-------------------|
| N-gram Recall (Lexical) | recall_score(y_true[lexical_mask], ŷ_ngram[lexical_mask]) | ≥ 0.80 |
| N-gram Recall (Semantic) | recall_score(y_true[semantic_mask], ŷ_ngram[semantic_mask]) | ≤ 0.40 |
| Min-K%++ F1 Variance | Var({F1(ŷ_minkpp, y_true) : corpus ∈ {Pile, C4, FineWeb}}) | ≥ 0.15 |
| Indeterminacy Rate | fraction of items with no detector achieving F1 margin ≥ 0.05 | [0.10, 0.50] |

Statistical significance tested via bootstrap (N=10,000 iterations, 95% CI) for all recall and F1 estimates. The 40% routing accuracy threshold for P1 (the primary routing prediction) is calibrated against random routing simulation over 5 detector families.
