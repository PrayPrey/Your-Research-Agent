def get_ngrams(text: str, n: int) -> set[str]:
    """Extract word-level n-grams from text."""
    words = text.lower().split()
    if len(words) < n:
        return set()
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}


def ngram_overlap_detect(corpus: list[str], benchmark: list[dict], n: int = 8) -> set[int]:
    """Detect corpus indices containing benchmark n-grams. n=8 per ConTAM."""
    benchmark_ngrams = set()
    for sample in benchmark:
        text = f"{sample['question']} {sample['choices'][sample['answer']]}"
        benchmark_ngrams.update(get_ngrams(text, n))

    detected = set()
    for idx, doc in enumerate(corpus):
        doc_ngrams = get_ngrams(doc, n)
        if doc_ngrams & benchmark_ngrams:
            detected.add(idx)
    return detected


def compute_ccr(corpus: list[str], benchmark: list[dict], n: int = 8) -> float:
    """CCR = fraction of benchmark n-grams found in corpus."""
    benchmark_ngrams = set()
    for sample in benchmark:
        text = f"{sample['question']} {sample['choices'][sample['answer']]}"
        benchmark_ngrams.update(get_ngrams(text, n))

    if not benchmark_ngrams:
        return 0.0

    corpus_ngrams = set()
    for doc in corpus:
        corpus_ngrams.update(get_ngrams(doc, n))

    overlap = benchmark_ngrams & corpus_ngrams
    return len(overlap) / len(benchmark_ngrams)
