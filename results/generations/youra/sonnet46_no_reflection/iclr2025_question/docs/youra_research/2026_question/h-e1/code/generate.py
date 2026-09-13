import logging
import os
import pickle
import tempfile
from dataclasses import dataclass, field
from typing import Any, List, Optional

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import SamplingConfig

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    question_id: str
    prompt: str
    greedy_text: str
    greedy_log_likelihood: float
    sampled_texts: List[str] = field(default_factory=list)
    sampled_log_likelihoods: List[float] = field(default_factory=list)
    hidden_states_last: Optional[np.ndarray] = None


def _compute_sequence_nll(scores, sequences, prompt_len: int) -> float:
    """Compute negative log-likelihood of generated tokens from output scores."""
    nll = 0.0
    generated_ids = sequences[0, prompt_len:]
    for t, token_id in enumerate(generated_ids):
        if t >= len(scores):
            break
        log_probs = torch.nn.functional.log_softmax(scores[t][0], dim=-1)
        nll -= log_probs[token_id].item()
    return nll


def generate_for_query(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompt: str,
    cfg: SamplingConfig,
    extract_hidden: bool = False,
) -> GenerationResult:
    """Generate greedy + N stochastic samples for a single prompt."""
    device = next(model.parameters()).device
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    input_ids = inputs["input_ids"]
    prompt_len = input_ids.shape[1]

    with torch.no_grad():
        # Greedy decode
        greedy_out = model.generate(
            input_ids,
            do_sample=False,
            max_new_tokens=cfg.max_new_tokens,
            return_dict_in_generate=True,
            output_scores=True,
            output_hidden_states=extract_hidden,
            pad_token_id=tokenizer.pad_token_id,
        )
    greedy_text = tokenizer.decode(
        greedy_out.sequences[0, prompt_len:], skip_special_tokens=True
    ).strip()
    greedy_nll = _compute_sequence_nll(greedy_out.scores, greedy_out.sequences, prompt_len)

    # Extract hidden states from greedy decode (last token of each layer)
    hidden_states_last = None
    if extract_hidden and hasattr(greedy_out, "hidden_states") and greedy_out.hidden_states:
        try:
            # hidden_states: tuple of (n_new_tokens,) each being tuple of (n_layers,) [1, seq_len, hidden]
            hs_per_step = greedy_out.hidden_states  # length = n_new_tokens
            # Use first generation step hidden states (all layers)
            hs_first = hs_per_step[0]  # tuple of n_layers tensors [1, seq_len, H]
            hidden_states_last = np.stack(
                [hs[0, -1, :].cpu().float().numpy() for hs in hs_first]
            )  # [n_layers, hidden_dim]
        except Exception as e:
            logger.warning(f"Hidden state extraction failed: {e}")

    # Stochastic samples
    sampled_texts = []
    sampled_nlls = []
    for i in range(cfg.n_samples):
        torch.manual_seed(cfg.seed + i)
        with torch.no_grad():
            samp_out = model.generate(
                input_ids,
                do_sample=True,
                temperature=cfg.temperature,
                top_p=cfg.top_p,
                max_new_tokens=cfg.max_new_tokens,
                return_dict_in_generate=True,
                output_scores=True,
                pad_token_id=tokenizer.pad_token_id,
            )
        text = tokenizer.decode(
            samp_out.sequences[0, prompt_len:], skip_special_tokens=True
        ).strip()
        nll = _compute_sequence_nll(samp_out.scores, samp_out.sequences, prompt_len)
        sampled_texts.append(text)
        sampled_nlls.append(nll)

    return GenerationResult(
        question_id=str(id(prompt)),  # will be overridden by caller
        prompt=prompt,
        greedy_text=greedy_text,
        greedy_log_likelihood=-greedy_nll,  # store as log-likelihood (negative NLL)
        sampled_texts=sampled_texts,
        sampled_log_likelihoods=[-nll for nll in sampled_nlls],
        hidden_states_last=hidden_states_last,
    )


def load_checkpoint(checkpoint_path: str) -> Optional[List[GenerationResult]]:
    """Load pickled checkpoint; returns None if not found."""
    if not os.path.exists(checkpoint_path):
        return None
    try:
        with open(checkpoint_path, "rb") as f:
            results = pickle.load(f)
        logger.info(f"Resumed from checkpoint: {len(results)} results loaded")
        return results
    except Exception as e:
        logger.warning(f"Checkpoint load failed ({e}), starting fresh")
        return None


def save_checkpoint(results: List[GenerationResult], checkpoint_path: str) -> None:
    """Atomic write via temp file to prevent corruption."""
    tmp_path = checkpoint_path + ".tmp"
    with open(tmp_path, "wb") as f:
        pickle.dump(results, f)
    os.replace(tmp_path, checkpoint_path)


def generate_dataset(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    dataset: List[dict],
    cfg: SamplingConfig,
    batch_size: int,
    checkpoint_path: str,
    checkpoint_every: int = 500,
    extract_hidden: bool = False,
    resume: bool = True,
) -> List[GenerationResult]:
    """Batched generation over full dataset with checkpoint resume."""
    existing = load_checkpoint(checkpoint_path) if resume else None
    # Only resume if checkpoint covers a subset of current dataset (not a stale run)
    if existing is not None and len(existing) <= len(dataset):
        results = existing
    else:
        if existing is not None:
            logger.info(f"Ignoring stale checkpoint ({len(existing)} results > dataset size {len(dataset)})")
        results = []
    start_idx = len(results)

    if start_idx > 0:
        logger.info(f"Resuming from index {start_idx}/{len(dataset)}")

    for idx in range(start_idx, len(dataset)):
        item = dataset[idx]
        try:
            result = generate_for_query(
                model, tokenizer, item["prompt"], cfg, extract_hidden=extract_hidden
            )
            result.question_id = item["question_id"]
        except Exception as e:
            logger.error(f"Generation failed at idx={idx}: {e}")
            # Create empty result to maintain index alignment
            result = GenerationResult(
                question_id=item["question_id"],
                prompt=item["prompt"],
                greedy_text="",
                greedy_log_likelihood=0.0,
                sampled_texts=[""] * cfg.n_samples,
                sampled_log_likelihoods=[0.0] * cfg.n_samples,
            )

        results.append(result)

        if (idx + 1) % checkpoint_every == 0:
            save_checkpoint(results, checkpoint_path)
            logger.info(f"Checkpoint saved at {idx + 1}/{len(dataset)}")

        if (idx + 1) % 100 == 0:
            logger.info(f"Generated {idx + 1}/{len(dataset)}")

    save_checkpoint(results, checkpoint_path)
    return results
