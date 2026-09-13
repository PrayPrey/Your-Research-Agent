# 3. Methodology

## 3.1 The Three-Zone Phase Diagram Framework

Our approach is motivated by the insight that contamination detection methods operate on orthogonal signal types. N-gram detectors measure lexical overlap — they succeed when benchmark items appear verbatim or near-verbatim in the pretraining corpus. Embedding-based detectors measure semantic proximity — they succeed when items are paraphrased but semantically equivalent. MIA-based detectors probe memorization through model log-probabilities — they succeed when items have been seen often enough during training to leave measurable statistical signatures in model weights.

If these signal types are truly orthogonal, then a benchmark item's position in the two-dimensional space of (lexical overlap, semantic proximity) should predict which detector family will perform best. We call this the **contamination geometry phase diagram**, and define three zones:

- **Lexical stratum**: high max 13-gram overlap count, any SBERT cosine similarity. N-gram detectors expected to perform best.
- **Semantic stratum**: low max 13-gram overlap count, high max SBERT cosine similarity. Embedding-based and MIA detectors expected to perform best.
- **Indeterminate zone**: neither lexical nor semantic signal is strong. Items where no detector may be reliable; characterizing this zone's size is itself informative.

## 3.2 Corpus-Side Geometry Features

We define two corpus-side geometry features per benchmark item $x$:

**Max 13-gram overlap count** $g_{\text{lex}}(x, \mathcal{C})$: the maximum number of consecutive 13-gram tokens from $x$ that appear in any document in corpus $\mathcal{C}$. This is computed using an inverted index over sorted 13-gram files, following the EleutherAI production pipeline [Gao et al., 2021].

**Max SBERT cosine similarity** $g_{\text{sem}}(x, \mathcal{C})$: the maximum cosine similarity between the SBERT embedding of $x$ and any document embedding in $\mathcal{C}$, using all-MiniLM-L6-v2 [Reimers and Gurevych, 2019]:

$$g_{\text{sem}}(x, \mathcal{C}) = \max_{d \in \mathcal{C}} \cos(\text{SBERT}(x), \text{SBERT}(d))$$

**Critical design requirement.** $g_{\text{sem}}$ must be computed using **top-k nearest-neighbor retrieval**: for each $x$, we find the $k$ most similar documents in $\mathcal{C}$ using a FAISS index [Johnson et al., 2019] and take the maximum cosine over those $k$ neighbors. As we show in Section 5, random corpus streaming cannot be substituted: the probability of a randomly sampled corpus document being semantically similar to a specific benchmark item is near zero, producing degenerate near-zero cosine distributions that make stratum formation impossible. We formalize this as the **stratum collapse boundary condition** (Proposition 1 below).

**Proposition 1 (Stratum Collapse).** *Let $\mathcal{C}_n$ be a random sample of $n$ documents from corpus $\mathcal{C}$, and let $\tau_{75}(\mathcal{C}_n)$ be the 75th percentile of $\{g_{\text{sem}}(x, \mathcal{C}_n) : x \in \mathcal{B}\}$ for benchmark set $\mathcal{B}$. As $n \to \infty$ under random sampling, $\tau_{75}(\mathcal{C}_n) \to 0$ for any benchmark $\mathcal{B}$ with non-trivial contamination-free items, because the expected cosine similarity between a random corpus document and a specific benchmark item approaches the base rate of random document similarity.*

*Consequence: all items satisfy $g_{\text{sem}}(x, \mathcal{C}_n) \geq \tau_{75}$ vacuously (all near-zero ≥ near-zero threshold), and the threshold-based semantic stratum assignment collapses. Top-k retrieval avoids this by construction: $g_{\text{sem}}$ is computed against the $k$ most similar documents, producing non-degenerate similarity scores.*

## 3.3 Stratum Assignment

Given geometry features $(g_{\text{lex}}, g_{\text{sem}})$ for each item, stratum boundaries are set at the 75th percentile of each feature distribution across all benchmark items and corpora:

$$\text{stratum}(x) = \begin{cases} \text{lexical} & \text{if } g_{\text{lex}}(x) \geq \tau_{\text{lex}} \\ \text{semantic} & \text{if } g_{\text{sem}}(x) \geq \tau_{\text{sem}} \\ \text{indeterminate} & \text{otherwise} \end{cases}$$

where $\tau_{\text{lex}} = \text{percentile}_{75}(\{g_{\text{lex}}(x)\})$ and $\tau_{\text{sem}} = \text{percentile}_{75}(\{g_{\text{sem}}(x)\})$.

## 3.4 Detector Families

We evaluate five detector families per stratum:

| Family | Method | Signal Type | Implementation |
|--------|--------|-------------|----------------|
| F1: N-gram | 13-gram exact match | Lexical | EleutherAI/lm-evaluation-harness |
| F2: Embedding | SBERT cosine threshold | Semantic | ntunlp/LLMSanitize |
| F3: Min-K%++ | Conditional categorical mode | MIA | zjysteven/mink-plus-plus [ICLR'25] |
| F4: DC-PDD | Log-likelihood ratio divergence | MIA | Zhang et al. [2024b] |
| F5: ConStat | Performance-based significance | Statistical | Dekoninck et al. [2024] |

**Rationale for detector selection.** F1–F3 represent the three main paradigms (lexical, semantic, MIA). F4 (DC-PDD) provides a second MIA detector using a different signal (cross-entropy divergence from a two-model log-ratio). F5 (ConStat) provides a performance-based baseline that does not rely on corpus access.

## 3.5 Routing Classifier

The routing objective is: given geometry features $(g_{\text{lex}}(x), g_{\text{sem}}(x))$ from a source corpus $\mathcal{C}_{\text{train}}$, predict which detector family achieves highest F1 for item $x$ on target corpus $\mathcal{C}_{\text{test}}$. We use logistic regression as the routing classifier, trained on stratum features from The Pile and evaluated on C4 and FineWeb for cross-corpus generalization.

**Success criterion.** The routing hypothesis (H-GeomRoute-v1) is confirmed if the classifier achieves top-1 accuracy > 40% and Kendall's τ > simulation-calibrated threshold on determinate items (margin ≥ 0.05 F1 gap under bootstrap). The 40% threshold is calibrated against a simulation of random routing over the five detector families.

## 3.6 Implementation Architecture

The full evaluation pipeline consists of: (1) **BenchmarkLoader** — streams MMLU, HellaSwag, GSM8K from HuggingFace; (2) **NgramIndexBuilder** — builds inverted index of 13-grams over corpus; (3) **SBERTIndexBuilder** — builds FAISS IndexFlatIP over corpus SBERT embeddings; (4) **GeometryStratifier** — computes $(g_{\text{lex}}, g_{\text{sem}})$ and assigns strata; (5) **Detector family implementations** — five detectors applied per item; (6) **StratifiedEvaluator** — computes per-stratum recall, F1, and Kendall's τ.

The pipeline processes 3 benchmarks × 3 corpora = 9 evaluation pairs, with bootstrap confidence intervals (N=10,000) on all metrics. Total compute budget: ~24–48 GPU-hours on a single A100/H100 GPU.
