# semantic_entropy.py - Semantic entropy computation via NLI clustering
import math
import torch
from nli_cluster import cluster_samples
from config import NUM_SAMPLES, TEMPERATURE, MAX_NEW_TOKENS


def generate_samples(model, tokenizer, prompt: str, n: int = NUM_SAMPLES,
                     temperature: float = TEMPERATURE, max_new_tokens: int = MAX_NEW_TOKENS) -> list[str]:
    """Generate n temperature-sampled responses."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    samples = []
    with torch.no_grad():
        for _ in range(n):
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                pad_token_id=tokenizer.pad_token_id,
            )
            gen_ids = outputs[0, inputs.input_ids.shape[1]:]
            text = tokenizer.decode(gen_ids, skip_special_tokens=True)
            samples.append(text)
    return samples


class SemanticEntropy:
    def __init__(self, llm_model, llm_tokenizer, nli_model, nli_tokenizer,
                 num_samples: int = NUM_SAMPLES, threshold: float = 0.7, device: str = "cuda"):
        self.llm_model = llm_model
        self.llm_tokenizer = llm_tokenizer
        self.nli_model = nli_model
        self.nli_tokenizer = nli_tokenizer
        self.num_samples = num_samples
        self.threshold = threshold
        self.device = device

    def compute(self, prompt: str, temperature: float = TEMPERATURE,
                max_tokens: int = MAX_NEW_TOKENS) -> dict:
        """Generate -> cluster -> entropy."""
        samples = generate_samples(
            self.llm_model, self.llm_tokenizer, prompt,
            n=self.num_samples, temperature=temperature, max_new_tokens=max_tokens
        )
        clusters = cluster_samples(self.nli_model, self.nli_tokenizer, samples,
                                   threshold=self.threshold, device=self.device)
        sizes = [len(c) for c in clusters]
        total = sum(sizes)
        if total == 0:
            entropy = 0.0
        else:
            probs = [s / total for s in sizes]
            entropy = -sum(p * math.log(p) for p in probs if p > 0)
        return {
            "semantic_entropy": entropy,
            "num_clusters": len(clusters),
            "cluster_sizes": sizes,
            "samples": samples
        }


def score_dataset(se: SemanticEntropy, questions: list[dict]) -> list[dict]:
    """Score all questions. Returns list of result dicts with entropy + labels."""
    results = []
    for i, q in enumerate(questions):
        prompt = q["prompt"]
        res = se.compute(prompt)
        res.update({
            "idx": i,
            "question": q["question"],
            "category": q.get("category", "unknown"),
            "correct_idx": q["correct_idx"],
            "label": q["label"],
        })
        results.append(res)
    return results
