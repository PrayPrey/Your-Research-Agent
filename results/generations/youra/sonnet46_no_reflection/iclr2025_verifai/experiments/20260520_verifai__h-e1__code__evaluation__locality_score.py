import logging
from typing import List, Dict

import torch
import torch.nn.functional as F

logger = logging.getLogger(__name__)


def compute_locality_score(
    model_pre,
    model_post,
    proof_states: list,
    tokenizer,
    premise_consistent_tokens: Dict[str, List[int]],
) -> float:
    """Compute LS = numerator / denominator over all proof states.

    LS = sum_s[P_post(pc|s) - P_pre(pc|s)] / sum_s[|delta(t,s)|]
    where pc = premise-consistent tokens for this state's error_category.
    """
    device = next(model_pre.parameters()).device
    numerator   = 0.0
    denominator = 0.0

    model_pre.eval()
    model_post.eval()

    with torch.no_grad():
        for state_triple in proof_states:
            if not state_triple.state:
                continue

            inputs = tokenizer(
                state_triple.state,
                return_tensors="pt",
                truncation=True,
                max_length=512,
            ).to(device)

            logits_pre  = model_pre(**inputs).logits    # [1, T, V]
            logits_post = model_post(**inputs).logits   # [1, T, V]

            # Next-token prediction position (last token)
            probs_pre  = F.softmax(logits_pre[:, -1, :],  dim=-1)  # [1, V]
            probs_post = F.softmax(logits_post[:, -1, :], dim=-1)  # [1, V]
            delta      = probs_post - probs_pre                     # [1, V]

            # Premise-consistent token indices for this state's error_category
            pc_idx = premise_consistent_tokens.get(state_triple.error_category or "", [])

            if pc_idx:
                pc_tensor = torch.tensor(pc_idx, dtype=torch.long, device=device)
                # Clamp indices to valid vocab range
                V = delta.shape[-1]
                pc_tensor = pc_tensor[pc_tensor < V]
                if len(pc_tensor) > 0:
                    numerator += delta[:, pc_tensor].sum().item()

            # Denominator: total absolute mass shift over all tokens
            denominator += delta.abs().sum().item()

    ls = numerator / (denominator + 1e-9)
    return float(ls)


def compute_all_locality_scores(
    ref_model,
    condition_models: Dict[str, object],
    proof_states: list,
    tokenizer,
    taxonomy_tokens: Dict[str, List[int]],
) -> Dict[str, List[float]]:
    """Compute LS per state for each condition.

    Returns {"A": [ls_s0, ls_s1, ...], "B": [...], "P": [...]}.
    """
    device = next(ref_model.parameters()).device
    results: Dict[str, List[float]] = {}

    ref_model.eval()
    with torch.no_grad():
        for condition, model_post in condition_models.items():
            model_post.eval()
            ls_per_state = []
            for state_triple in proof_states:
                if not state_triple.state:
                    ls_per_state.append(0.0)
                    continue
                inputs = tokenizer(
                    state_triple.state,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                ).to(device)

                logits_pre  = ref_model(**inputs).logits[:, -1, :]    # [1, V]
                logits_post = model_post(**inputs).logits[:, -1, :]   # [1, V]

                probs_pre  = F.softmax(logits_pre,  dim=-1)
                probs_post = F.softmax(logits_post, dim=-1)
                delta      = probs_post - probs_pre                   # [1, V]

                pc_idx = taxonomy_tokens.get(state_triple.error_category or "", [])
                V = delta.shape[-1]

                numerator_s   = 0.0
                denominator_s = delta.abs().sum().item()

                if pc_idx:
                    pc_tensor = torch.tensor(pc_idx, dtype=torch.long, device=device)
                    pc_tensor = pc_tensor[pc_tensor < V]
                    if len(pc_tensor) > 0:
                        numerator_s = delta[:, pc_tensor].sum().item()

                ls_s = numerator_s / (denominator_s + 1e-9)
                ls_per_state.append(float(ls_s))

            results[condition] = ls_per_state
            mean_ls = sum(ls_per_state) / max(len(ls_per_state), 1)
            logger.info(f"Condition {condition}: mean LS = {mean_ls:.4f} over {len(ls_per_state)} states")

    return results
