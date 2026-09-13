"""Uncertainty estimation methods including baselines."""

import torch
import torch.nn.functional as F
import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from transformers import AutoModelForCausalLM, AutoTokenizer


def compute_token_entropy(logits: torch.Tensor) -> torch.Tensor:
    """
    Compute token-level entropy from logits.

    Args:
        logits: [batch, seq_len, vocab_size]

    Returns:
        entropy: [batch] - average entropy per sequence
    """
    probs = F.softmax(logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    entropy = -torch.sum(probs * log_probs, dim=-1)  # [batch, seq_len]
    return entropy.mean(dim=-1)  # [batch]


def generate_with_entropy(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 64,
    temperature: float = 1.0,
    device: str = "cuda"
) -> Tuple[str, float]:
    """
    Generate text and compute average token entropy.

    Returns:
        Tuple of (generated_text, average_entropy)
    """
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            return_dict_in_generate=True,
            output_scores=True,
            pad_token_id=tokenizer.pad_token_id
        )

    generated_ids = outputs.sequences[:, inputs["input_ids"].shape[1]:]
    generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

    # Compute entropy from scores
    if outputs.scores:
        all_logits = torch.stack(outputs.scores, dim=1)  # [batch, gen_len, vocab]
        entropy = compute_token_entropy(all_logits)
        avg_entropy = entropy.mean().item()
    else:
        avg_entropy = 0.0

    return generated_text, avg_entropy


def compute_verbalized_confidence(
    model,
    tokenizer,
    question: str,
    device: str = "cuda"
) -> float:
    """
    Compute verbalized confidence by asking the model about its certainty.

    Returns:
        Confidence score between 0 and 1
    """
    prompt = f"""Question: {question}

On a scale of 0 to 100, how confident are you in your ability to answer this question correctly?
Respond with just a number."""

    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=10,
            temperature=0.1,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id
        )

    generated_ids = outputs[:, inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(generated_ids[0], skip_special_tokens=True).strip()

    # Parse confidence from response
    try:
        # Extract first number found
        import re
        numbers = re.findall(r'\d+', response)
        if numbers:
            confidence = float(numbers[0]) / 100.0
            confidence = max(0.0, min(1.0, confidence))
        else:
            confidence = 0.5
    except:
        confidence = 0.5

    return confidence


def semantic_similarity(text1: str, text2: str) -> float:
    """
    Compute semantic similarity between two texts.
    Uses simple word overlap as a lightweight approximation.
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union)


def cluster_responses(responses: List[str], threshold: float = 0.5) -> List[List[int]]:
    """
    Cluster responses by semantic similarity.

    Returns:
        List of clusters, each cluster is a list of response indices
    """
    n = len(responses)
    if n == 0:
        return []

    # Compute pairwise similarities
    similarities = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            sim = semantic_similarity(responses[i], responses[j])
            similarities[i, j] = sim
            similarities[j, i] = sim

    # Simple greedy clustering
    assigned = [False] * n
    clusters = []

    for i in range(n):
        if assigned[i]:
            continue

        cluster = [i]
        assigned[i] = True

        for j in range(i + 1, n):
            if not assigned[j] and similarities[i, j] >= threshold:
                cluster.append(j)
                assigned[j] = True

        clusters.append(cluster)

    return clusters


def compute_semantic_entropy(
    model,
    tokenizer,
    prompt: str,
    num_samples: int = 5,
    max_new_tokens: int = 64,
    temperature: float = 0.7,
    device: str = "cuda"
) -> Tuple[float, List[str]]:
    """
    Compute semantic entropy using multiple samples.

    Returns:
        Tuple of (semantic_entropy, list_of_responses)
    """
    responses = []
    response_probs = []

    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    for _ in range(num_samples):
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                return_dict_in_generate=True,
                output_scores=True,
                pad_token_id=tokenizer.pad_token_id
            )

        generated_ids = outputs.sequences[:, inputs["input_ids"].shape[1]:]
        response = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        responses.append(response)

        # Approximate probability from perplexity
        if outputs.scores:
            all_logits = torch.stack(outputs.scores, dim=1)
            log_probs = F.log_softmax(all_logits, dim=-1)
            token_log_probs = log_probs[0, range(len(generated_ids[0])), generated_ids[0]]
            avg_log_prob = token_log_probs.mean().item()
            response_probs.append(np.exp(avg_log_prob))
        else:
            response_probs.append(1.0 / num_samples)

    # Normalize probabilities
    total_prob = sum(response_probs)
    response_probs = [p / total_prob for p in response_probs]

    # Cluster responses
    clusters = cluster_responses(responses, threshold=0.4)

    # Compute semantic entropy
    cluster_probs = []
    for cluster in clusters:
        cluster_prob = sum(response_probs[i] for i in cluster)
        cluster_probs.append(cluster_prob)

    # Entropy
    semantic_entropy = 0.0
    for p in cluster_probs:
        if p > 0:
            semantic_entropy -= p * np.log(p + 1e-10)

    return semantic_entropy, responses


class BaselineUncertaintyEstimator:
    """Baseline uncertainty estimation methods."""

    def __init__(self, model, tokenizer, device: str = "cuda"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def token_entropy(self, question: str) -> Dict[str, float]:
        """Compute token entropy for a question."""
        prompt = f"Question: {question}\nAnswer:"
        _, entropy = generate_with_entropy(
            self.model, self.tokenizer, prompt,
            max_new_tokens=64, temperature=0.7, device=self.device
        )
        return {"uncertainty": entropy, "normalized_uncertainty": min(1.0, entropy / 5.0)}

    def verbalized_confidence(self, question: str) -> Dict[str, float]:
        """Get verbalized confidence score."""
        confidence = compute_verbalized_confidence(
            self.model, self.tokenizer, question, device=self.device
        )
        return {"confidence": confidence, "uncertainty": 1.0 - confidence}

    def semantic_entropy(self, question: str, num_samples: int = 5) -> Dict[str, float]:
        """Compute semantic entropy."""
        prompt = f"Question: {question}\nAnswer:"
        entropy, responses = compute_semantic_entropy(
            self.model, self.tokenizer, prompt,
            num_samples=num_samples, max_new_tokens=64,
            temperature=0.7, device=self.device
        )
        return {
            "semantic_entropy": entropy,
            "normalized_uncertainty": min(1.0, entropy / 2.0),
            "num_unique_responses": len(set(responses))
        }
