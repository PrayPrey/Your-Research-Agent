"""BiDPO loss implementation combining DPO with agency-preservation."""
import torch
import torch.nn.functional as F
from torch import Tensor
from config import CONFIG


def normalize_agency_score(raw_score: Tensor, clip_max: float = None) -> Tensor:
    if clip_max is None:
        clip_max = CONFIG.agency_clip_max
    return torch.clamp(raw_score, min=0.0, max=clip_max) / clip_max


def compute_dpo_loss(
    policy_chosen_logps: Tensor,
    policy_rejected_logps: Tensor,
    ref_chosen_logps: Tensor,
    ref_rejected_logps: Tensor,
    beta: float,
) -> Tensor:
    pi_logratios = policy_chosen_logps - policy_rejected_logps
    ref_logratios = ref_chosen_logps - ref_rejected_logps
    logits = pi_logratios - ref_logratios
    return -F.logsigmoid(beta * logits).mean()


def compute_agency_loss(
    chosen_collab_scores: Tensor,
    rejected_collab_scores: Tensor,
) -> Tensor:
    agency_chosen = (1.0 - chosen_collab_scores).mean()
    agency_rejected = (1.0 - rejected_collab_scores).mean()
    return agency_chosen - 0.5 * agency_rejected


def compute_bidpo_loss(
    policy_chosen_logps: Tensor,
    policy_rejected_logps: Tensor,
    ref_chosen_logps: Tensor,
    ref_rejected_logps: Tensor,
    chosen_collab_scores: Tensor,
    rejected_collab_scores: Tensor,
    beta: float,
    lambda_agency: float,
) -> tuple[Tensor, dict]:
    dpo_loss = compute_dpo_loss(
        policy_chosen_logps, policy_rejected_logps,
        ref_chosen_logps, ref_rejected_logps,
        beta
    )

    chosen_norm = normalize_agency_score(chosen_collab_scores)
    rejected_norm = normalize_agency_score(rejected_collab_scores)
    agency_loss = compute_agency_loss(chosen_norm, rejected_norm)

    total_loss = dpo_loss + lambda_agency * agency_loss

    return total_loss, {
        "dpo_loss": dpo_loss.item(),
        "agency_loss": agency_loss.item(),
        "total_loss": total_loss.item(),
    }
