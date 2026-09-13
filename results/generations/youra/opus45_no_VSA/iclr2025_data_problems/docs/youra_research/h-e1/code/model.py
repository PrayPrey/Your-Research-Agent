import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import Config


def load_model_and_tokenizer(cfg: Config):
    print(f"Loading model {cfg.model_id}...")
    model = AutoModelForCausalLM.from_pretrained(cfg.model_id, torch_dtype=torch.float16)
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    print(f"Model loaded on {device}")
    return model, tokenizer


def compute_attribution_scores(model, tokenizer, corpus: list[str], benchmark: list[dict], device: torch.device) -> np.ndarray:
    """
    PoC attribution via embedding similarity (fast proxy for gradient-based influence).
    Returns [n_benchmark, n_corpus] attribution matrix.

    ponytail: embedding similarity is O(n) not O(n*params), 1000x faster for PoC.
    """
    model.eval()
    n_bench = min(len(benchmark), 20)
    n_corpus = len(corpus)

    print(f"Computing embeddings ({n_bench} benchmark, {n_corpus} corpus)...")

    def get_embedding(text: str) -> np.ndarray:
        inputs = tokenizer(text[:512], return_tensors="pt", truncation=True, max_length=128, padding=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
            # Use mean of last hidden state as embedding
            emb = outputs.hidden_states[-1].mean(dim=1).squeeze().cpu().numpy()
        return emb / (np.linalg.norm(emb) + 1e-8)

    # Benchmark embeddings
    bench_embs = []
    for sample in benchmark[:n_bench]:
        text = f"Question: {sample['question']}\nAnswer: {sample['choices'][sample['answer']]}"
        bench_embs.append(get_embedding(text))
    bench_embs = np.stack(bench_embs)  # [n_bench, emb_dim]

    # Corpus embeddings (batched for speed)
    corpus_embs = []
    batch_size = 32
    for i in range(0, n_corpus, batch_size):
        if i % 500 == 0:
            print(f"  Corpus embedding progress: {i}/{n_corpus}")
        batch = corpus[i:i+batch_size]
        for doc in batch:
            corpus_embs.append(get_embedding(doc[:512]))
    corpus_embs = np.stack(corpus_embs)  # [n_corpus, emb_dim]

    # Attribution = cosine similarity
    scores = bench_embs @ corpus_embs.T  # [n_bench, n_corpus]
    print(f"Attribution matrix shape: {scores.shape}")

    return scores


def compute_ccr(scores: np.ndarray, injected_positions: list[int]) -> float:
    total_mass = np.abs(scores).sum()
    if total_mass < 1e-8:
        return 0.0
    contaminated_mass = np.abs(scores[:, injected_positions]).sum()
    return float(contaminated_mass / total_mass)
