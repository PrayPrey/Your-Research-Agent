"""Model loading with revision-specific checkpoint support (Pythia suite)."""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelSpec:
    model_id: str
    revision: str
    corpus: str   # "pile" or "deduped"
    size: str     # "1b" or "6.9b"
    key: str      # e.g. "pile_1b"


def load_model_checkpoint(
    model_id: str,
    revision: str,
    device: str = "cuda",
    cache_dir: str = "./model_cache",
):
    """
    Load Pythia checkpoint at specific revision.

    Returns (model, tokenizer) — model in eval() mode, fp16 on device.
    Raises OSError if revision not found.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    logger.info(f"Loading tokenizer: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)

    logger.info(f"Loading model: {model_id} @ {revision}")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        revision=revision,
        torch_dtype=torch.float16,
        cache_dir=cache_dir,
    ).to(device).eval()

    return model, tokenizer


def verify_checkpoint_step(
    model,
    model_spec: ModelSpec,
    adjacent_steps: list[int] | None = None,
) -> str:
    """
    Log loaded checkpoint step and token count.
    Returns revision string used.
    """
    if adjacent_steps is None:
        adjacent_steps = [97000, 99000, 100000]

    step_str = model_spec.revision.replace("step", "")
    step = int(step_str)
    token_count_b = step * 2_097_152 / 1e9

    logger.info(
        f"Loaded {model_spec.key}: step={step}, token_count={token_count_b:.1f}B tokens"
    )
    return model_spec.revision


def load_model_with_fallback(
    model_id: str,
    revision: str,
    key: str,
    device: str = "cuda",
    cache_dir: str = "./model_cache",
    fallback_steps: list[int] | None = None,
):
    """Try loading at `revision`; fall back to adjacent steps on OSError."""
    if fallback_steps is None:
        fallback_steps = [97000, 99000, 100000, 95000, 101000]

    try:
        return load_model_checkpoint(model_id, revision, device, cache_dir)
    except OSError as e:
        logger.warning(f"Revision {revision} not found for {model_id}: {e}")
        for step in fallback_steps:
            fb_revision = f"step{step}"
            logger.info(f"Trying fallback: {fb_revision}")
            try:
                return load_model_checkpoint(model_id, fb_revision, device, cache_dir)
            except OSError:
                continue
        raise RuntimeError(f"Could not load {model_id} at any revision") from e
