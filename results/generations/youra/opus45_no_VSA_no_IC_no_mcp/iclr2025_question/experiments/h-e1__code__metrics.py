"""Metrics computation: entropy, consistency, labeling."""

import torch
import torch.nn.functional as F
import numpy as np
from sentence_transformers import SentenceTransformer
from bert_score import score as bert_score_fn
from config import CONFIG


def generate_greedy(model, tokenizer, question: str) -> tuple[str, torch.Tensor]:
    """Generate response with greedy decoding.

    Returns (response_text, logits [seq_len, vocab])
    """
    prompt = f"Q: {question}\nA:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=CONFIG["MAX_NEW_TOKENS"],
            do_sample=False,
            return_dict_in_generate=True,
            output_scores=True,
        )

    generated_ids = outputs.sequences[0][inputs.input_ids.shape[1]:]
    response_text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    if outputs.scores:
        logits = torch.stack(outputs.scores, dim=0)
    else:
        logits = torch.zeros(1, tokenizer.vocab_size)

    return response_text, logits


def compute_token_entropy(logits: torch.Tensor) -> float:
    """Compute mean Shannon entropy over token logits."""
    if logits.numel() == 0:
        return 0.0

    probs = F.softmax(logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    entropy = -torch.sum(probs * log_probs, dim=-1)
    return entropy.mean().item()


def generate_n_samples(model, tokenizer, question: str, n: int, temperature: float) -> list[str]:
    """Generate N sampled responses."""
    prompt = f"Q: {question}\nA:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    responses = []
    for _ in range(n):
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=CONFIG["MAX_NEW_TOKENS"],
                do_sample=True,
                temperature=temperature,
            )
        generated_ids = outputs[0][inputs.input_ids.shape[1]:]
        response_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
        responses.append(response_text)

    return responses


def compute_consistency(responses: list[str], encoder: SentenceTransformer) -> float:
    """Compute pairwise cosine similarity among responses."""
    if len(responses) < 2:
        return 1.0

    embeddings = encoder.encode(responses)
    n = len(embeddings)
    similarities = []

    for i in range(n):
        for j in range(i + 1, n):
            sim = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8
            )
            similarities.append(sim)

    return float(np.mean(similarities))


def label_response(response: str, best_answer: str, incorrect_answers: list[str]) -> int:
    """Label response: 0=correct, 1=hallucinated."""
    if not response.strip():
        return 1

    _, _, F1 = bert_score_fn(
        [response], [best_answer],
        lang="en",
        rescale_with_baseline=CONFIG["BERTSCORE_RESCALE"]
    )
    best_score = F1.item()

    worst_score = 0.0
    if incorrect_answers:
        _, _, F1_inc = bert_score_fn(
            [response] * len(incorrect_answers),
            incorrect_answers,
            lang="en",
            rescale_with_baseline=CONFIG["BERTSCORE_RESCALE"]
        )
        worst_score = F1_inc.max().item()

    if worst_score > best_score or best_score < CONFIG["LABEL_MIN_BEST_SCORE"]:
        return 1
    return 0
