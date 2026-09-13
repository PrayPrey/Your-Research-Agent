"""H-C1 ΔECE computation and RLHF moderation comparison."""
import sys, os
_HE1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../h-e1/code"))
if _HE1_CODE not in sys.path:
    sys.path.append(_HE1_CODE)  # append so h-c1 stays at front

import numpy as np
import torch
from typing import NamedTuple

from evaluation.logit_extractor import extract_cell
from evaluation.ece import compute_ece


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


def compute_delta_ece(model, tokenizer, clean_dataset, adv_dataset,
                      cell_id: str, model_id: str,
                      task: str = "nli", config=None) -> CellECE:
    """
    Extract confidences/correctness for clean and adv splits, compute ECE, return CellECE.
    Tensor shapes inside extract_cell:
      logits: [1, seq_len, vocab_size] -> answer_logits: [n_choices] -> probs: [n_choices]
      confidences: [N], correctness: [N]
    """
    max_samples = getattr(config, "subsample_clean", 1000) if config else 1000
    batch_size = getattr(config, "batch_size", 8) if config else 8
    n_bins = getattr(config, "n_bins", 15) if config else 15

    # Clean split
    clean_result = extract_cell(model, tokenizer, clean_dataset, task, model_id,
                                batch_size=batch_size)
    correct_clean = (clean_result.pred_labels == clean_result.true_labels).astype(float)
    ece_clean = compute_ece(clean_result.confidences, correct_clean, n_bins=n_bins)
    n_clean = len(clean_result.confidences)

    # Adversarial split
    adv_result = extract_cell(model, tokenizer, adv_dataset, task, model_id,
                              batch_size=batch_size)
    correct_adv = (adv_result.pred_labels == adv_result.true_labels).astype(float)
    ece_adv = compute_ece(adv_result.confidences, correct_adv, n_bins=n_bins)
    n_adv = len(adv_result.confidences)

    delta_ece = ece_adv - ece_clean
    return CellECE(cell_id, model_id, ece_clean, ece_adv, delta_ece, n_clean, n_adv)


def compare_rlhf_moderation(base: CellECE, chat: CellECE) -> ModerationResult:
    assert base.cell_id == chat.cell_id, f"Cell ID mismatch: {base.cell_id} vs {chat.cell_id}"
    ddece = base.delta_ece - chat.delta_ece
    return ModerationResult(
        cell_id=base.cell_id,
        delta_ece_base=base.delta_ece,
        delta_ece_chat=chat.delta_ece,
        ddece=ddece,
        moderation_confirmed=(ddece > 0),
    )


def verify_activation(base_results: dict, chat_results: dict) -> tuple:
    """4 indicator checks from PRD FR-3.3. Returns (activated, indicators)."""
    ref_base = base_results.get("NLI-AdvGLUE")
    ref_chat = chat_results.get("NLI-AdvGLUE")
    if ref_base is None or ref_chat is None:
        return False, {"error": "NLI-AdvGLUE cell missing"}

    indicators = {
        "base_ece_valid": not np.isnan(ref_base.ece_adv),
        "chat_ece_valid": not np.isnan(ref_chat.ece_adv),
        "models_differ": abs(ref_base.ece_adv - ref_chat.ece_adv) > 0.001,
        "moderation_direction": ref_chat.delta_ece < ref_base.delta_ece,
    }
    activated = all(indicators.values())
    return activated, indicators


def compute_moderation_rate(moderation_results: list) -> float:
    if not moderation_results:
        return 0.0
    return sum(r.moderation_confirmed for r in moderation_results) / len(moderation_results)
