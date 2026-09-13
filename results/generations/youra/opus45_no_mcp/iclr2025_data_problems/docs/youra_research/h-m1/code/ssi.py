import torch
import numpy as np
from tqdm import tqdm
from data import generate_paraphrases, format_mmlu_prompt, format_mmlu_with_paraphrase


SSI_EPSILON = 1e-8


def extract_confidence(model, tokenizer, prompt: str, answer_tokens: list[int]) -> float:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        last_logits = outputs.logits[0, -1, :]
        answer_logits = last_logits[answer_tokens]
        probs = torch.softmax(answer_logits.float(), dim=0)
        confidence = probs.max().item()

    return confidence


def compute_ssi(model, tokenizer, item: dict, paraphrases: list[str],
                answer_tokens: list[int]) -> tuple[float, list[float]]:
    confidences = []

    original_prompt = format_mmlu_prompt(item)
    conf = extract_confidence(model, tokenizer, original_prompt, answer_tokens)
    confidences.append(conf)

    choices = item["choices"]
    for para in paraphrases:
        para_prompt = format_mmlu_with_paraphrase(para, choices)
        conf = extract_confidence(model, tokenizer, para_prompt, answer_tokens)
        confidences.append(conf)

    variance = np.var(confidences)
    ssi = 1.0 / (variance + SSI_EPSILON)

    return ssi, confidences


def compute_ssi_batch(model, tokenizer, items: list[dict], answer_tokens: list[int],
                      k_paraphrases: int = 20) -> tuple[list[float], list[list[float]]]:
    ssi_scores = []
    all_confidences = []

    for item in tqdm(items, desc="Computing SSI"):
        paraphrases = generate_paraphrases(item, k=k_paraphrases)
        ssi, confidences = compute_ssi(model, tokenizer, item, paraphrases, answer_tokens)
        ssi_scores.append(ssi)
        all_confidences.append(confidences)

    return ssi_scores, all_confidences
