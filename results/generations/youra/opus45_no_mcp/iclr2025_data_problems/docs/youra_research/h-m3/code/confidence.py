import torch
import torch.nn.functional as F
import numpy as np


def get_answer_token_id(tokenizer, answer_idx: int) -> int:
    tokens = [" A", " B", " C", " D"]
    t = tokens[answer_idx]
    ids = tokenizer.encode(t, add_special_tokens=False)
    return ids[-1] if ids else tokenizer.encode(t.strip(), add_special_tokens=False)[-1]


def extract_confidence(model, tokenizer, prompt: str, answer_token_id: int) -> float:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits[:, -1, :]
        probs = F.softmax(logits, dim=-1)
        conf = probs[0, answer_token_id].item()
    return conf


def batch_extract_confidences(model, tokenizer, prompts: list, answer_token_ids: list, batch_size: int = 8) -> list:
    all_confs = []
    for i in range(0, len(prompts), batch_size):
        batch_prompts = prompts[i:i + batch_size]
        batch_token_ids = answer_token_ids[i:i + batch_size]
        inputs = tokenizer(batch_prompts, return_tensors="pt", truncation=True,
                          max_length=512, padding=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            for j, token_id in enumerate(batch_token_ids):
                all_confs.append(probs[j, token_id].item())
    return all_confs


def confidence_variance(confidences: list) -> float:
    return np.var(confidences)
