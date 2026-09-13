"""Preference evaluation for HH-RLHF benchmarks."""
import torch


def parse_hh_conversation(conversation: str) -> tuple:
    """Split HH-RLHF conversation into prompt and response."""
    # Find the last Assistant turn
    parts = conversation.rsplit("\n\nAssistant:", 1)
    if len(parts) == 2:
        prompt = parts[0] + "\n\nAssistant:"
        response = parts[1]
        return prompt, response
    return conversation, ""


def compute_response_logprob(model, tokenizer, conversation: str, device: str, max_length: int = 512) -> float:
    """Compute length-normalized log-prob of response tokens."""
    prompt, response = parse_hh_conversation(conversation)

    # Tokenize prompt to get length
    prompt_tokens = tokenizer.encode(prompt)
    prompt_len = len(prompt_tokens)

    # Tokenize full conversation
    inputs = tokenizer(conversation, return_tensors="pt", truncation=True, max_length=max_length)
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits

    # Shift for next-token prediction
    shift_logits = logits[:, :-1, :].contiguous()
    shift_labels = input_ids[:, 1:].contiguous()

    log_probs = torch.log_softmax(shift_logits, dim=-1)
    token_log_probs = log_probs.gather(-1, shift_labels.unsqueeze(-1)).squeeze(-1)

    # Sum only response tokens (after prompt_len)
    answer_start = max(0, prompt_len - 1)
    response_log_prob = token_log_probs[0, answer_start:].sum().item()

    # Length normalize
    n_response_tokens = token_log_probs.shape[1] - answer_start
    if n_response_tokens > 0:
        response_log_prob /= n_response_tokens

    return response_log_prob


def evaluate_preference(model, tokenizer, sample: dict, device: str, max_length: int = 512) -> int:
    """Evaluate single preference sample. Returns 1 if chosen > rejected, 0 otherwise."""
    chosen_logprob = compute_response_logprob(model, tokenizer, sample["chosen"], device, max_length)
    rejected_logprob = compute_response_logprob(model, tokenizer, sample["rejected"], device, max_length)
    return 1 if chosen_logprob > rejected_logprob else 0


def evaluate_preference_batch(model, tokenizer, dataset, device: str, max_length: int = 512, max_samples: int = None) -> dict:
    """Evaluate entire preference dataset."""
    scores = []
    n = min(max_samples, len(dataset)) if max_samples else len(dataset)

    for i in range(n):
        score = evaluate_preference(model, tokenizer, dataset[i], device, max_length)
        scores.append(score)

    accuracy = sum(scores) / len(scores) if scores else 0.0
    stderr = (accuracy * (1 - accuracy) / len(scores)) ** 0.5 if len(scores) > 1 else 0.0

    return {"scores": scores, "accuracy": accuracy, "stderr": stderr, "n": len(scores)}
