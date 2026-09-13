from collections import defaultdict


def get_ngrams(text: str, n: int) -> set[str]:
    words = text.lower().split()
    if len(words) < n:
        return set()
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}


def ngram_overlap_detect(corpus: list[str], benchmark: list[dict], n: int = 13) -> set[int]:
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


def evaluate_detector_precision(predicted: set[int], actual: set[int]) -> dict:
    tp = len(predicted & actual)
    fp = len(predicted - actual)
    fn = len(actual - predicted)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}
