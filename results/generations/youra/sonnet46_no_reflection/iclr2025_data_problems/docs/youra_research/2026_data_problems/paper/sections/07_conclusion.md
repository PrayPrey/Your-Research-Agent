# 7. Conclusion

We began by observing that MMLU is verbatim-contaminated in every major pretraining corpus we tested, yet no principled framework exists for predicting which contamination detector will work best for a given benchmark item. Our attempt to build such a framework — the three-zone phase diagram for geometry-governed detector routing — led to a more fundamental finding: the framework has a hard prerequisite that the field has not previously identified.

**Summary.** We attempted to verify that corpus-side geometric signals (max 13-gram overlap count and SBERT cosine similarity) can define contamination strata that predict detector performance, and that a logistic regression routing classifier can achieve cross-corpus routing accuracy above chance. This prediction was never reached. Instead, we found that random corpus streaming produces degenerate SBERT cosine distributions at scale, collapsing all 25,403 benchmark items into a single lexical stratum and making routing structurally impossible. We call this the stratum collapse boundary condition, and we show that it is a predictable consequence of using random sampling for semantic similarity computation. Top-k nearest-neighbor corpus retrieval is not an optimization — it is a prerequisite.

Beyond the stratum collapse finding, our experiment establishes two reproducible empirical facts: MMLU achieves n-gram recall = 1.0 against The Pile, C4, and FineWeb simultaneously — the first cross-corpus confirmation of MMLU's comprehensive verbatim contamination. GSM8K achieves recall = 0.0 against all three corpora, revealing that math benchmarks have fundamentally different corpus overlap profiles than NLU benchmarks and require benchmark-type-specific detection criteria. We also document four implementation pitfalls in contamination detection systems — including the DCPDDDetector single-model proxy bug and the ConStatDetector API deviation — providing a concrete guide for future implementations.

## Future Directions

The boundary condition we identified opens three concrete research directions, each grounded in our experimental findings:

**From the stratum collapse finding:** Build an offline large-scale FAISS index (50M+ documents per corpus with HNSW or IVF-PQ approximation) for per-item top-k retrieval, then re-run the geometry stratification experiment. This is the direct path to testing whether the three-zone phase diagram produces meaningful strata. We estimate ~50–100GB disk per corpus for SBERT-384 embeddings.

**From the implementation bug analysis:** Fix DCPDDDetector with proper two-model log-likelihood ratio computation and ConStatDetector with the `llmsanitize.contamination.constat()` API before any next experiment. Validate using synthetic contamination injection (controlled exact and paraphrase copies in a small corpus) to confirm detector outputs are meaningful before scaling to real corpora.

**From the MMLU/GSM8K contrast:** Develop benchmark-type-specific detection criteria — NLU benchmarks should use lexical recall against general web corpora; math benchmarks require domain-specific corpus matching (OpenWebMath, Proof-Pile) or semantic-level detection with paraphrase-aware methods.

The broader vision remains: a contamination detection routing system that automatically selects the best method per benchmark item, turning inconsistent multi-method disagreement into a principled signal. The theoretical motivation for such a system is intact. Building it correctly requires starting from the right foundation — and this paper documents what that foundation requires.
