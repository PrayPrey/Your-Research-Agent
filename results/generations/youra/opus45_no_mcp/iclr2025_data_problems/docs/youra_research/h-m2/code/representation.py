import torch
import torch.nn.functional as F
import numpy as np
from tqdm import tqdm


def extract_representation(model, tokenizer, text: str) -> torch.Tensor:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)

    hidden = outputs.hidden_states[-1]
    mask = inputs["attention_mask"].unsqueeze(-1).float()
    pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1)
    return pooled.squeeze(0)


def batch_extract_representations(model, tokenizer, texts: list, batch_size: int = 8) -> torch.Tensor:
    all_reps = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        inputs = tokenizer(batch_texts, return_tensors="pt", truncation=True,
                          max_length=512, padding=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)

        hidden = outputs.hidden_states[-1]
        mask = inputs["attention_mask"].unsqueeze(-1).float()
        pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1)
        all_reps.append(pooled.cpu())

    return torch.cat(all_reps, dim=0)


def compute_paraphrase_similarity(orig_rep: torch.Tensor, para_reps: torch.Tensor) -> float:
    orig_rep = orig_rep.unsqueeze(0) if orig_rep.dim() == 1 else orig_rep
    similarities = F.cosine_similarity(orig_rep.expand(para_reps.size(0), -1), para_reps, dim=1)
    return similarities.mean().item()


def evaluate_invariance(model, tokenizer, items: list, paraphrase_bank: dict,
                        contaminated_ids: list) -> np.ndarray:
    from data import format_mmlu_prompt

    mps_values = []
    print(f"Evaluating representation invariance for {len(contaminated_ids)} items...")

    for i, idx in enumerate(tqdm(contaminated_ids, desc="Computing MPS")):
        item = items[idx]
        original = format_mmlu_prompt(item)
        paraphrases = paraphrase_bank.get(idx, [])

        if not paraphrases:
            continue

        orig_rep = extract_representation(model, tokenizer, original)
        para_reps = batch_extract_representations(model, tokenizer, paraphrases, batch_size=len(paraphrases))

        mps = compute_paraphrase_similarity(orig_rep, para_reps)
        mps_values.append(mps)

    return np.array(mps_values)
