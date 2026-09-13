import torch
from torch.nn.functional import softmax
from sentence_transformers import SentenceTransformer
from bert_score import score as bertscore
import config

def generate_greedy(model, tokenizer, question: str) -> tuple[str, torch.Tensor]:
    prompt = f"Q: {question}\nA:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=config.MAX_NEW_TOKENS,
            do_sample=False,
            output_scores=True,
            return_dict_in_generate=True,
        )
    if len(output.scores) == 0:
        return "", torch.empty(0, model.config.vocab_size)
    logits = torch.stack(output.scores, dim=0)
    text = tokenizer.decode(output.sequences[0, input_len:], skip_special_tokens=True)
    return text, logits

def compute_token_entropy(logits: torch.Tensor) -> float:
    if logits.numel() == 0:
        return 0.0
    probs = softmax(logits, dim=-1)
    eps = 1e-10
    entropy = -(probs * torch.log(probs + eps)).sum(dim=-1)
    return entropy.mean().item()

def generate_n_samples(model, tokenizer, question: str, n: int, temperature: float) -> list[str]:
    prompt = f"Q: {question}\nA:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]
    responses = []
    for _ in range(n):
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=config.MAX_NEW_TOKENS,
                do_sample=True,
                temperature=max(temperature, 0.1),
                top_k=50,
                top_p=0.95,
            )
        text = tokenizer.decode(output[0, input_len:], skip_special_tokens=True)
        responses.append(text)
    return responses

def compute_consistency(responses: list[str], encoder: SentenceTransformer) -> float:
    if len(responses) <= 1:
        return 1.0
    embeddings = encoder.encode(responses, convert_to_tensor=True)
    sim = torch.nn.functional.cosine_similarity(
        embeddings.unsqueeze(1), embeddings.unsqueeze(0), dim=-1
    )
    n = sim.shape[0]
    iu = torch.triu_indices(n, n, offset=1)
    return sim[iu[0], iu[1]].mean().item()

def label_response(response: str, best_answer: str, incorrect_answers: list[str]) -> int:
    _, _, best_f1 = bertscore([response], [best_answer], lang="en", rescale_with_baseline=config.BERTSCORE_RESCALE)
    best_score = best_f1[0].item()
    worst_score = 0.0
    if incorrect_answers:
        _, _, inc_f1 = bertscore([response] * len(incorrect_answers), incorrect_answers, lang="en", rescale_with_baseline=config.BERTSCORE_RESCALE)
        worst_score = inc_f1.max().item()
    if best_score > worst_score and best_score >= config.LABEL_MIN_BEST_SCORE:
        return 0
    return 1
