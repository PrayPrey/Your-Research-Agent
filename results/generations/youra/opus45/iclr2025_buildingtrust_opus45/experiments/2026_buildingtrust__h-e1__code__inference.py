"""
Inference module for H-E1 AUROC experiment.

Model loading, logit extraction, and margin computation.
"""

import gc
import torch
import numpy as np
from pathlib import Path
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import Dataset

from config import DTYPE, DEVICE, CHECKPOINT_INTERVAL, CACHE_DIR, CHOICE_LABELS
from data import format_prompt, get_dataloader


def load_model(model_id: str) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """
    Load model with float16 precision and CUDA.

    Args:
        model_id: HuggingFace model identifier

    Returns:
        (model, tokenizer) tuple
    """
    print(f"Loading model: {model_id}")

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    # Set pad token if not set (common for causal LMs)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=DTYPE,
        device_map=DEVICE,
        trust_remote_code=True,
    )
    model.eval()

    return model, tokenizer


def unload_model(model: AutoModelForCausalLM) -> None:
    """
    Unload model and free GPU memory.

    Args:
        model: Model to unload
    """
    del model
    gc.collect()
    torch.cuda.empty_cache()


def get_choice_token_ids(tokenizer: AutoTokenizer) -> list[int]:
    """
    Get token IDs for answer choices ' A', ' B', ' C', ' D'.

    Args:
        tokenizer: Model tokenizer

    Returns:
        List of 4 token IDs
    """
    choice_ids = []
    for label in CHOICE_LABELS:
        # Encode with space prefix for proper tokenization
        token_id = tokenizer.encode(f" {label}", add_special_tokens=False)[-1]
        choice_ids.append(token_id)
    return choice_ids


def extract_choice_logits(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompt: str,
    choice_ids: list[int],
) -> np.ndarray:
    """
    Extract logits for answer choices at last token position.

    Args:
        model: Loaded model
        tokenizer: Model tokenizer
        prompt: Formatted MCQ prompt
        choice_ids: Token IDs for A/B/C/D

    Returns:
        np.ndarray of shape (4,) with logits for each choice
    """
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model(**inputs)
        # Get logits at last position: (1, seq_len, vocab_size) -> (vocab_size,)
        last_logits = outputs.logits[0, -1, :]
        # Extract logits for choice tokens
        choice_logits = last_logits[choice_ids].cpu().numpy()

    return choice_logits


def compute_margin(logits: np.ndarray) -> float:
    """
    Compute confidence margin = logit_top1 - logit_top2.

    Args:
        logits: Array of shape (4,) with logits for each choice

    Returns:
        Margin value (float)
    """
    sorted_logits = np.sort(logits)[::-1]  # Descending
    return float(sorted_logits[0] - sorted_logits[1])


def run_model_inference(
    model_id: str,
    dataset: Dataset,
    cache_path: str,
    start_idx: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Run full inference with checkpointing.

    Args:
        model_id: HuggingFace model identifier
        dataset: MMLU dataset
        cache_path: Path for .npy checkpoint files
        start_idx: Index to start from (for resume)

    Returns:
        (margins, correctness) arrays of shape (N,)
    """
    cache_dir = Path(cache_path)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Clean model name for cache files
    model_name = model_id.replace("/", "_")
    margins_file = cache_dir / f"{model_name}_margins.npy"
    correct_file = cache_dir / f"{model_name}_correctness.npy"

    # Check for completed cache
    if margins_file.exists() and correct_file.exists():
        print(f"Loading cached results for {model_id}")
        margins = np.load(margins_file)
        correctness = np.load(correct_file)
        return margins, correctness

    # Load partial checkpoint if exists
    partial_margins_file = cache_dir / f"{model_name}_margins_partial.npy"
    partial_correct_file = cache_dir / f"{model_name}_correctness_partial.npy"

    if partial_margins_file.exists() and partial_correct_file.exists():
        margins_list = list(np.load(partial_margins_file))
        correct_list = list(np.load(partial_correct_file))
        start_idx = len(margins_list)
        print(f"Resuming from checkpoint at index {start_idx}")
    else:
        margins_list = []
        correct_list = []

    # Load model
    model, tokenizer = load_model(model_id)
    choice_ids = get_choice_token_ids(tokenizer)

    # Run inference
    total = len(dataset)
    pbar = tqdm(
        get_dataloader(dataset, start_idx),
        initial=start_idx,
        total=total,
        desc=f"Inference {model_id.split('/')[-1]}"
    )

    for sample in pbar:
        # Extract logits and compute margin
        logits = extract_choice_logits(model, tokenizer, sample["prompt"], choice_ids)
        margin = compute_margin(logits)

        # Check correctness (argmax matches answer)
        predicted = int(np.argmax(logits))
        is_correct = int(predicted == sample["answer"])

        margins_list.append(margin)
        correct_list.append(is_correct)

        # Checkpoint
        if len(margins_list) % CHECKPOINT_INTERVAL == 0:
            np.save(partial_margins_file, np.array(margins_list))
            np.save(partial_correct_file, np.array(correct_list))

    # Unload model
    unload_model(model)

    # Convert to arrays
    margins = np.array(margins_list)
    correctness = np.array(correct_list)

    # Save final results
    np.save(margins_file, margins)
    np.save(correct_file, correctness)

    # Clean up partial files
    if partial_margins_file.exists():
        partial_margins_file.unlink()
    if partial_correct_file.exists():
        partial_correct_file.unlink()

    return margins, correctness
