"""Benchmark-type-conditional ΔΔECE analysis and 13B cross-size validation."""
import os, sys, json, subprocess, traceback
from typing import Dict, List, Tuple, Optional, NamedTuple
import numpy as np


class CellECE(NamedTuple):
    cell_id: str
    model_id: str
    ece_clean: float
    ece_adv: float
    delta_ece: float
    n_clean: int
    n_adv: int


class ModerationResult(NamedTuple):
    cell_id: str
    delta_ece_base: float
    delta_ece_chat: float
    ddece: float
    moderation_confirmed: bool


def compare_rlhf_moderation(base: CellECE, chat: CellECE) -> ModerationResult:
    assert base.cell_id == chat.cell_id
    ddece = base.delta_ece - chat.delta_ece
    return ModerationResult(base.cell_id, base.delta_ece, chat.delta_ece, ddece, ddece > 0)


def compute_moderation_rate(results: list) -> float:
    if not results:
        return 0.0
    return sum(r.moderation_confirmed for r in results) / len(results)


def compute_ece(confidences: np.ndarray, correct: np.ndarray, n_bins: int = 15) -> float:
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(confidences)
    for b in range(n_bins):
        mask = (confidences >= bins[b]) & (confidences <= bins[b + 1]) if b == n_bins - 1 \
               else (confidences > bins[b]) & (confidences <= bins[b + 1])
        if mask.sum() == 0:
            continue
        ece += (mask.sum() / n) * abs(correct[mask].mean() - confidences[mask].mean())
    return float(ece)

TASK_TO_CELL_ID = {
    "anli_r1":       "NLI-ANLI-R1",
    "anli_r2":       "NLI-ANLI-R2",
    "anli_r3":       "NLI-ANLI-R3",
    "adv_glue_mnli": "NLI-AdvGLUE",
}

CELL_TO_CLEAN_KEY = {
    "NLI-ANLI-R1": "anli_r1_clean",
    "NLI-ANLI-R2": "anli_r2_clean",
    "NLI-ANLI-R3": "anli_r3_clean",
    "NLI-AdvGLUE": "glue_mnli",
}


def compute_moderation_by_benchmark_type(
    base_results: Dict[str, CellECE],
    chat_results: Dict[str, CellECE],
    anli_cells: List[str],
    advglue_cells: List[str],
    ddece_threshold: float = 0.01,
) -> Tuple[List[ModerationResult], List[ModerationResult], float, float]:
    """
    Separate moderation by benchmark type.
    Returns: (anli_results, advglue_results, anli_rate, advglue_rate)
    """
    anli_results = []
    for cell_id in anli_cells:
        if cell_id not in base_results or cell_id not in chat_results:
            print(f"⚠ Missing cell {cell_id} — skipping")
            continue
        r = compare_rlhf_moderation(base_results[cell_id], chat_results[cell_id])
        confirmed = r.ddece > ddece_threshold
        anli_results.append(r._replace(moderation_confirmed=confirmed))

    advglue_results = []
    for cell_id in advglue_cells:
        if cell_id not in base_results or cell_id not in chat_results:
            print(f"⚠ Missing cell {cell_id} — skipping")
            continue
        r = compare_rlhf_moderation(base_results[cell_id], chat_results[cell_id])
        confirmed = r.ddece > ddece_threshold
        advglue_results.append(r._replace(moderation_confirmed=confirmed))

    anli_rate = compute_moderation_rate(anli_results)
    advglue_rate = compute_moderation_rate(advglue_results)
    return anli_results, advglue_results, anli_rate, advglue_rate


def compute_cross_size_moderation(
    base_7b_results: Dict[str, CellECE],
    chat_13b_results: Dict[str, CellECE],
    anli_cells: List[str],
    ddece_threshold: float = 0.01,
) -> Tuple[List[ModerationResult], float]:
    """7B-base vs 13B-chat moderation on ANLI cells."""
    results = []
    for cell_id in anli_cells:
        if cell_id not in base_7b_results or cell_id not in chat_13b_results:
            print(f"⚠ Missing cell {cell_id} for cross-size — skipping")
            continue
        r = compare_rlhf_moderation(base_7b_results[cell_id], chat_13b_results[cell_id])
        confirmed = r.ddece > ddece_threshold
        results.append(r._replace(moderation_confirmed=confirmed))
    rate = compute_moderation_rate(results)
    return results, rate


def evaluate_gate(
    anli_moderation_rate: float,
    threshold: float = 0.60,
) -> Tuple[bool, Dict]:
    """Primary gate: ANLI moderation_rate >= threshold."""
    gate_passed = anli_moderation_rate >= threshold
    report = {
        "anli_rate": anli_moderation_rate,
        "threshold": threshold,
        "gate_passed": gate_passed,
        "margin": anli_moderation_rate - threshold,
    }
    return gate_passed, report


def _get_logits_and_labels_from_dataset(dataset, model, tokenizer, config) -> Tuple[np.ndarray, np.ndarray]:
    """Extract logits and labels from a HuggingFace NLI dataset using the model."""
    import torch
    from torch.nn.functional import softmax

    label_tokens = []
    for label_word in ["entailment", "neutral", "contradiction"]:
        tok = tokenizer(label_word, return_tensors="pt")["input_ids"][0, -1].item()
        label_tokens.append(tok)

    all_logits = []
    all_labels = []
    batch_size = getattr(config, "batch_size", 4)

    def make_prompt(ex):
        return (
            f"Premise: {ex['premise']}\nHypothesis: {ex['hypothesis']}\n"
            "Relation (entailment/neutral/contradiction):"
        )

    device = next(model.parameters()).device
    model.eval()
    with torch.no_grad():
        for i in range(0, len(dataset), batch_size):
            batch = dataset.select(range(i, min(i + batch_size, len(dataset))))
            for ex in batch:
                prompt = make_prompt(ex)
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
                out = model(**inputs)
                last_logit = out.logits[0, -1, label_tokens]  # (3,)
                all_logits.append(last_logit.cpu().numpy())
                all_labels.append(ex["label"])

    return np.array(all_logits), np.array(all_labels)


def run_13b_inference_direct(
    model_id: str,
    datasets: Dict,
    tasks: List[str],
    config,
) -> Dict[str, CellECE]:
    """
    Run 13B-chat inference directly using HuggingFace transformers.
    Returns {cell_id: CellECE}
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    print(f"Loading {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model.eval()

    task_to_cell = {
        "anli_r1": "NLI-ANLI-R1",
        "anli_r2": "NLI-ANLI-R2",
        "anli_r3": "NLI-ANLI-R3",
        "adv_glue_mnli": "NLI-AdvGLUE",
    }
    cell_to_clean = {
        "NLI-ANLI-R1": "anli_r1_clean",
        "NLI-ANLI-R2": "anli_r2_clean",
        "NLI-ANLI-R3": "anli_r3_clean",
        "NLI-AdvGLUE": "glue_mnli",
    }

    results: Dict[str, CellECE] = {}
    for task in tasks:
        cell_id = task_to_cell[task]
        adv_ds_key = task
        clean_ds_key = cell_to_clean[cell_id]

        if adv_ds_key not in datasets or clean_ds_key not in datasets:
            print(f"⚠ Dataset missing for task {task} — skipping")
            continue

        adv_ds = datasets[adv_ds_key]
        clean_ds = datasets[clean_ds_key]

        if len(adv_ds) == 0:
            print(f"⚠ Empty adversarial dataset for {task} — skipping")
            continue

        print(f"  Running inference on {cell_id} (adv={len(adv_ds)}, clean={len(clean_ds)})...")
        adv_logits, adv_labels = _get_logits_and_labels_from_dataset(adv_ds, model, tokenizer, config)
        clean_logits, clean_labels = _get_logits_and_labels_from_dataset(clean_ds, model, tokenizer, config)

        results[cell_id] = convert_to_cell_ece(
            adv_logits, adv_labels, clean_logits, clean_labels,
            cell_id, model_id, n_bins=config.n_bins,
        )
        print(f"  ✓ {cell_id}: ECE_clean={results[cell_id].ece_clean:.4f}, ECE_adv={results[cell_id].ece_adv:.4f}")

    del model
    import gc; gc.collect()
    import torch; torch.cuda.empty_cache()

    return results


def convert_to_cell_ece(
    logits: np.ndarray,
    labels: np.ndarray,
    clean_logits: np.ndarray,
    clean_labels: np.ndarray,
    cell_id: str,
    model_id: str,
    n_bins: int = 15,
) -> CellECE:
    """Softmax logits → confidences → compute_ece → CellECE."""
    def softmax(x):
        e = np.exp(x - x.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)

    probs = softmax(logits)
    preds = probs.argmax(axis=1)
    confidences = probs[np.arange(len(probs)), preds]
    correct = (preds == labels).astype(float)
    ece_adv = compute_ece(confidences, correct, n_bins)

    clean_probs = softmax(clean_logits)
    clean_preds = clean_probs.argmax(axis=1)
    clean_conf = clean_probs[np.arange(len(clean_probs)), clean_preds]
    clean_correct = (clean_preds == clean_labels).astype(float)
    ece_clean = compute_ece(clean_conf, clean_correct, n_bins)

    return CellECE(
        cell_id=cell_id,
        model_id=model_id,
        ece_clean=ece_clean,
        ece_adv=ece_adv,
        delta_ece=ece_adv - ece_clean,
        n_clean=len(clean_labels),
        n_adv=len(labels),
    )


def validate_13b_inference_output(
    cells: Dict[str, CellECE],
    expected_cell_ids: List[str],
) -> None:
    """Raise ValueError if any expected cell missing."""
    missing = [c for c in expected_cell_ids if c not in cells]
    if missing:
        raise ValueError(f"13B inference missing cells: {missing}")


def summarize_results(
    pair_7b: Tuple[List[ModerationResult], List[ModerationResult], float, float],
    pair_13b: Tuple[List[ModerationResult], float],
) -> dict:
    """Assemble full results summary dict for JSON serialization."""
    anli_results_7b, advglue_results_7b, anli_rate_7b, advglue_rate_7b = pair_7b
    anli_results_13b, anli_rate_13b = pair_13b

    def mod_to_dict(m: ModerationResult) -> dict:
        return {
            "cell_id": m.cell_id,
            "delta_ece_base": m.delta_ece_base,
            "delta_ece_chat": m.delta_ece_chat,
            "ddece": m.ddece,
            "moderation_confirmed": m.moderation_confirmed,
        }

    return {
        "anli_rate_7b": anli_rate_7b,
        "advglue_rate_7b": advglue_rate_7b,
        "anli_rate_13b": anli_rate_13b,
        "anli_results_7b": [mod_to_dict(r) for r in anli_results_7b],
        "advglue_results_7b": [mod_to_dict(r) for r in advglue_results_7b],
        "anli_results_13b": [mod_to_dict(r) for r in anli_results_13b],
    }
