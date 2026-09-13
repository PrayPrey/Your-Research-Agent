import torch
import torch.nn.functional as F
import numpy as np
from tqdm import tqdm


def extract_hidden_and_confidence(model, tokenizer, prompts: list, answer_token_id: int):
    inputs = tokenizer(prompts, return_tensors="pt", truncation=True, max_length=512, padding=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
        hidden = outputs.hidden_states[-1][:, -1, :]
        logits = outputs.logits[:, -1, :]
        probs = F.softmax(logits, dim=-1)
        confidences = probs[:, answer_token_id].cpu().numpy()

    return hidden.cpu(), confidences


def compute_rep_variance(hidden_states: torch.Tensor) -> float:
    n = hidden_states.size(0)
    if n < 2:
        return 0.0

    hidden_states = F.normalize(hidden_states, dim=1)
    sims = []
    for i in range(n):
        for j in range(i + 1, n):
            sim = F.cosine_similarity(hidden_states[i].unsqueeze(0), hidden_states[j].unsqueeze(0), dim=1)
            sims.append(sim.item())
    return 1.0 - np.mean(sims) if sims else 0.0


def compute_item_variances(model, tokenizer, prompts: list, answer_token_id: int) -> tuple:
    hidden, confidences = extract_hidden_and_confidence(model, tokenizer, prompts, answer_token_id)
    rep_var = compute_rep_variance(hidden)
    conf_var = np.var(confidences)
    return rep_var, conf_var


def run_variance_extraction(model, tokenizer, test_set, paraphrase_bank: dict,
                             contaminated_ids: list, format_mmlu_prompt) -> dict:
    from confidence import get_answer_token_id

    results = {}
    print(f"Extracting variances for {len(contaminated_ids)} items...")

    for idx in tqdm(contaminated_ids, desc="Computing variances"):
        item = test_set[idx]
        original = format_mmlu_prompt(item)
        paraphrases = paraphrase_bank.get(idx, [])

        if not paraphrases:
            continue

        prompts = [original] + paraphrases
        answer_token_id = get_answer_token_id(tokenizer, item["answer"])

        rep_var, conf_var = compute_item_variances(model, tokenizer, prompts, answer_token_id)
        results[idx] = {"rep_var": rep_var, "conf_var": conf_var}

    return results
