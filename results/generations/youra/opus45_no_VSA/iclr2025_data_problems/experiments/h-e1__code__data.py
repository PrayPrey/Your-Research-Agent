import random
from datasets import load_dataset
from config import Config


def verbalize(sample: dict) -> str:
    q = sample["question"]
    choices = sample["choices"]
    answer_idx = sample["answer"]
    answer = choices[answer_idx]
    return f"Question: {q}\nAnswer: {answer}"


def load_corpus_and_benchmark(cfg: Config) -> tuple[list[str], list[dict]]:
    print("Loading corpus (OpenWebText or wikitext fallback)...")
    try:
        rp = load_dataset("Skylion007/openwebtext", split="train", streaming=True)
        text_key = "text"
    except Exception:
        rp = load_dataset("wikitext", "wikitext-103-raw-v1", split="train", streaming=True)
        text_key = "text"

    corpus = []
    for i, doc in enumerate(rp):
        if i >= cfg.corpus_size:
            break
        txt = doc[text_key].strip()
        if len(txt) > 50:  # skip empty/short
            corpus.append(txt[:2000])
    print(f"Loaded {len(corpus)} documents")

    print("Loading MMLU benchmark...")
    mmlu = load_dataset("cais/mmlu", "all", split="test")
    benchmark = []
    for i, sample in enumerate(mmlu):
        if i >= cfg.mmlu_subset:
            break
        benchmark.append({
            "question": sample["question"],
            "choices": sample["choices"],
            "answer": sample["answer"],
            "subject": sample["subject"]
        })
    print(f"Loaded {len(benchmark)} MMLU samples")
    return corpus, benchmark


def inject_benchmark(corpus: list[str], benchmark: list[dict], rate: float, seed: int) -> tuple[list[str], list[int]]:
    random.seed(seed)
    corpus_copy = corpus.copy()
    n_inject = max(1, int(len(corpus_copy) * rate))
    positions = random.sample(range(len(corpus_copy)), min(n_inject, len(corpus_copy)))

    for i, pos in enumerate(positions):
        sample = benchmark[i % len(benchmark)]
        corpus_copy[pos] = verbalize(sample)

    return corpus_copy, positions
