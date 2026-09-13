import warnings
import numpy as np
import torch
import torch.nn.functional as F
from typing import NamedTuple
from tqdm import tqdm

from data.formatter import format_mc_prompt, TASK_CHOICES


class CellResult(NamedTuple):
    confidences: np.ndarray
    pred_labels: np.ndarray
    true_labels: np.ndarray
    prob_sums: np.ndarray


def extract_answer_token_ids(tokenizer, choices: list) -> list:
    token_ids = []
    for i, choice in enumerate(choices):
        if not choice:
            raise ValueError(f"Empty choice string at index {i}")
        ids = tokenizer.encode(choice, add_special_tokens=False)
        if len(ids) > 1:
            warnings.warn(f"Choice '{choice}' tokenizes to {len(ids)} tokens; using first.")
        token_ids.append(ids[0])
    return token_ids


def extract_mc_logits(model, tokenizer, context: str, answer_choices: list, device: str):
    token_ids = extract_answer_token_ids(tokenizer, answer_choices)
    inputs = tokenizer(context, return_tensors="pt", truncation=True, max_length=512).to(device)
    with torch.no_grad():
        out = model(**inputs)
    last_logits = out.logits[0, -1, :]
    answer_token_ids_t = torch.tensor(token_ids, device=last_logits.device)
    answer_logits = last_logits[answer_token_ids_t]
    probs = F.softmax(answer_logits.float(), dim=0).cpu().numpy()
    pred_label = int(np.argmax(probs))
    confidence = float(probs[pred_label])
    return probs, pred_label, confidence


def extract_cell(model, tokenizer, dataset, task: str, model_id: str, batch_size: int = 8) -> CellResult:
    device = next(model.parameters()).device
    choices = TASK_CHOICES[task]

    confidences, pred_labels, true_labels, prob_sums = [], [], [], []

    for example in tqdm(dataset, desc=f"{model_id.split('/')[-1]}/{task}", leave=False):
        context, answer_choices = format_mc_prompt(example, task, model_id)
        try:
            probs, pred, conf = extract_mc_logits(model, tokenizer, context, answer_choices, device)
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                torch.cuda.empty_cache()
                probs, pred, conf = extract_mc_logits(model, tokenizer, context, answer_choices, device)
            else:
                raise
        confidences.append(conf)
        pred_labels.append(pred)
        true_labels.append(int(example["label"]))
        prob_sums.append(float(probs.sum()))

    return CellResult(
        confidences=np.array(confidences),
        pred_labels=np.array(pred_labels),
        true_labels=np.array(true_labels),
        prob_sums=np.array(prob_sums),
    )
