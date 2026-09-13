import os
import copy
import logging
from typing import List, Dict, Tuple

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer, get_linear_schedule_with_warmup

from training.dpo_pairs import DPOPair
from config import ExperimentConfig

logger = logging.getLogger(__name__)


def load_model_and_tokenizer(
    model_id: str,
    dtype: torch.dtype = torch.bfloat16,
) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load BFS-Prover-V2-7B with device_map='auto' and bfloat16."""
    logger.info(f"Loading model: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )
    logger.info(f"Model loaded: {sum(p.numel() for p in model.parameters()) / 1e9:.1f}B params")
    return model, tokenizer


def get_batch_logps(
    logits: torch.Tensor,   # [B, T, V]
    labels: torch.Tensor,   # [B, T]
    average_log_prob: bool = False,
) -> torch.Tensor:          # [B]
    """Compute per-sequence log-probs by summing (not averaging) token log-probs.
    Masks padding tokens (label == -100). average_log_prob=False per FR-4.2.
    """
    # Shift: predict token t+1 from position t
    log_probs = F.log_softmax(logits[:, :-1, :], dim=-1)  # [B, T-1, V]
    labels = labels[:, 1:].clone()                          # [B, T-1]
    mask = (labels != -100)                                 # [B, T-1]
    labels[~mask] = 0                                       # avoid index error on -100
    per_token_logps = log_probs.gather(2, labels.unsqueeze(2)).squeeze(2)  # [B, T-1]
    per_token_logps = per_token_logps * mask                # zero out padding
    if average_log_prob:
        return per_token_logps.sum(-1) / mask.sum(-1).clamp(min=1)  # [B]
    return per_token_logps.sum(-1)                          # [B]


def dpo_loss(
    policy_chosen_logps: torch.Tensor,    # [B]
    policy_rejected_logps: torch.Tensor,  # [B]
    ref_chosen_logps: torch.Tensor,       # [B]
    ref_rejected_logps: torch.Tensor,     # [B]
    beta: float = 10.0,
) -> torch.Tensor:  # scalar
    """DPO loss: -logsigmoid(beta * (pi_logratios - ref_logratios)).mean()"""
    pi_logratios  = policy_chosen_logps  - policy_rejected_logps   # [B]
    ref_logratios = ref_chosen_logps     - ref_rejected_logps       # [B]
    loss = -F.logsigmoid(beta * (pi_logratios - ref_logratios)).mean()
    return loss


def _encode_pair(pair: DPOPair, tokenizer: PreTrainedTokenizer, max_len: int = 512) -> Dict:
    """Tokenize a DPO pair into chosen/rejected input_ids and labels."""
    def encode(tactic: str, state: str):
        text = f"{state}\n{tactic}"
        enc = tokenizer(text, truncation=True, max_length=max_len, return_tensors="pt")
        input_ids = enc["input_ids"][0]  # type: ignore[index]
        state_enc = tokenizer(state, truncation=True, max_length=max_len, return_tensors="pt")
        prompt_len = min(state_enc["input_ids"].shape[1], len(input_ids) - 1)  # type: ignore[index]
        labels = input_ids.clone()
        labels[:prompt_len] = -100
        return input_ids, labels

    chosen_ids, chosen_labels = encode(pair.chosen_tactic, pair.state)
    rej_text = pair.rejected_tactic + (f"\n-- error: {pair.error_msg}" if pair.error_msg else "")
    rejected_ids, rejected_labels = encode(rej_text, pair.state)
    return {
        "chosen_input_ids": chosen_ids,
        "chosen_labels": chosen_labels,
        "rejected_input_ids": rejected_ids,
        "rejected_labels": rejected_labels,
    }


def _pad_to_same(tensors: List[torch.Tensor], pad_value: int = 0) -> torch.Tensor:
    max_len = max(t.shape[0] for t in tensors)
    padded = [F.pad(t, (0, max_len - t.shape[0]), value=pad_value) for t in tensors]
    return torch.stack(padded)


def train_dpo_condition(
    condition: str,
    pairs: List[DPOPair],
    config: ExperimentConfig,
    ref_model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
) -> PreTrainedModel:
    """Train 1-epoch DPO from BFS-Prover-V2-7B; save checkpoint to config.checkpoint_dir/condition."""
    logger.info(f"[H-E1] Starting DPO training for Condition {condition} ({len(pairs)} pairs)")

    device = next(ref_model.parameters()).device

    # Load fresh policy model
    policy_model, _ = load_model_and_tokenizer(config.model_id, torch.bfloat16)
    policy_model.train()

    # Freeze ref model
    ref_model.eval()
    for param in ref_model.parameters():
        param.requires_grad = False

    # Optimizer with linear LR decay
    optimizer = torch.optim.AdamW(
        policy_model.parameters(),
        lr=config.lr_start,
        weight_decay=config.weight_decay,
        betas=config.adam_betas,
    )

    num_steps = max(len(pairs) // config.batch_size, 1) * config.num_epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=num_steps,
    )
    # Final LR = lr_end — adjust scheduler to decay to lr_end not 0
    # Achieved by scaling: we'll manually clamp after scheduler step

    initial_loss = None
    total_loss = 0.0
    step_count = 0

    for epoch in range(config.num_epochs):
        for i in range(0, len(pairs), config.batch_size):
            batch_pairs = pairs[i: i + config.batch_size]
            if not batch_pairs:
                continue

            encoded = [_encode_pair(p, tokenizer, config.max_seq_len) for p in batch_pairs]

            pad_id = tokenizer.pad_token_id if isinstance(tokenizer.pad_token_id, int) else 0
            chosen_ids      = _pad_to_same([e["chosen_input_ids"]   for e in encoded], pad_value=pad_id)
            chosen_labels   = _pad_to_same([e["chosen_labels"]       for e in encoded], pad_value=-100)
            rejected_ids    = _pad_to_same([e["rejected_input_ids"]  for e in encoded], pad_value=pad_id)
            rejected_labels = _pad_to_same([e["rejected_labels"]    for e in encoded], pad_value=-100)

            # Concatenate chosen+rejected for single forward pass (eric-mitchell pattern)
            all_ids    = torch.cat([chosen_ids,    rejected_ids],    dim=0).to(device)
            all_labels = torch.cat([chosen_labels, rejected_labels], dim=0).to(device)
            all_mask   = (all_ids != pad_id).long()

            with torch.no_grad():
                ref_logits = ref_model(input_ids=all_ids, attention_mask=all_mask).logits
                ref_logps  = get_batch_logps(ref_logits, all_labels)

            policy_logits = policy_model(input_ids=all_ids, attention_mask=all_mask).logits
            policy_logps  = get_batch_logps(policy_logits, all_labels)

            B = len(batch_pairs)
            loss = dpo_loss(
                policy_logps[:B], policy_logps[B:],
                ref_logps[:B],    ref_logps[B:],
                beta=config.beta,
            )

            if initial_loss is None:
                initial_loss = loss.item()

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(policy_model.parameters(), 1.0)
            optimizer.step()
            # Clamp LR to lr_end minimum
            for pg in optimizer.param_groups:
                pg["lr"] = max(pg["lr"], config.lr_end)
            scheduler.step()

            total_loss += loss.item()
            step_count += 1

            if step_count % 10 == 0:
                logger.info(f"  Condition {condition} step {step_count}: loss={loss.item():.4f}")

    final_loss = total_loss / max(step_count, 1)
    logger.info(f"[H-E1] Condition {condition} training complete. Final loss: {final_loss:.4f}")

    # Stability check: abort if final loss > 2x initial
    if initial_loss is not None and final_loss > 2.0 * initial_loss:
        logger.warning(f"Loss instability detected (initial={initial_loss:.4f}, final={final_loss:.4f}). Reducing LR/beta and retrying once.")
        # Retry with halved LR and beta
        config_retry = copy.deepcopy(config)
        config_retry.lr_start = config.lr_start * 0.5
        config_retry.lr_end   = config.lr_end   * 0.5
        config_retry.beta     = config.beta     * 0.5
        return train_dpo_condition(condition, pairs, config_retry, ref_model, tokenizer)

    # Save checkpoint
    ckpt_dir = os.path.join(config.checkpoint_dir, condition)
    os.makedirs(ckpt_dir, exist_ok=True)
    policy_model.save_pretrained(ckpt_dir)
    tokenizer.save_pretrained(ckpt_dir)
    logger.info(f"Checkpoint saved: {ckpt_dir}")

    return policy_model


def run_all_dpo_conditions(
    all_pairs: Dict[str, List[DPOPair]],
    config: ExperimentConfig,
) -> Dict[str, PreTrainedModel]:
    """Train conditions A, B, P sequentially; returns {"A": model_A, "B": model_B, "P": model_P}."""
    ref_model, tokenizer = load_model_and_tokenizer(config.model_id, torch.bfloat16)
    ref_model.eval()
    for param in ref_model.parameters():
        param.requires_grad = False

    condition_models = {}
    for condition in config.conditions:
        pairs = all_pairs.get(condition, [])
        logger.info(f"Training Condition {condition}: {len(pairs)} pairs")
        model = train_dpo_condition(condition, pairs, config, ref_model, tokenizer)
        condition_models[condition] = model

    return condition_models
