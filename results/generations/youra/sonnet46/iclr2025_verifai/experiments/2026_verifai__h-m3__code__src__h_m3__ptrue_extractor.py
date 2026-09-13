"""ptrue_extractor.py — P(True) logprob extraction, inference loop, mechanism verification."""
from __future__ import annotations

import json
import logging
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

from h_m3.config import (
    CHECKPOINT_INTERVAL,
    MAX_NEW_TOKENS,
    MODEL_SHORT_NAMES,
    PTRUE_PROMPT_TEMPLATE,
    SEED,
    ModelLoadConfig,
)

logger = logging.getLogger(__name__)


def load_model_and_tokenizer(
    model_id: str,
    device: str,
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load model in float16 with device_map='auto'. Set seed=42."""
    cfg = ModelLoadConfig()

    # Set random seeds
    torch.manual_seed(cfg.seed)
    random.seed(cfg.seed)
    np.random.seed(cfg.seed)
    try:
        from transformers import set_seed
        set_seed(cfg.seed)
    except ImportError:
        pass

    logger.info(f"Loading model: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map=cfg.device_map,
        trust_remote_code=True,
    )
    model.eval()
    logger.info(f"Model loaded: {model_id}")
    return model, tokenizer


def get_true_false_token_ids(tokenizer: AutoTokenizer) -> tuple[int, int]:
    """Return (true_id, false_id) for ' True' and ' False' tokens (with leading space)."""
    true_id = tokenizer.encode(" True", add_special_tokens=False)[0]
    false_id = tokenizer.encode(" False", add_special_tokens=False)[0]
    logger.info(f"P(True) token IDs: True={true_id}, False={false_id}")
    assert true_id != false_id, (
        f"true_id == false_id ({true_id}): tokenizer does not distinguish True/False tokens"
    )
    return true_id, false_id


def extract_ptrue_confidence(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problem_prompt: str,
    solution_code: str,
    device: str,
    true_id: int,
    false_id: int,
    prompt_template: str,
) -> float:
    """Return c in [0,1]: P(True) confidence via logprob extraction.

    Steps:
      1. Format prompt
      2. Tokenize
      3. Generate with output_logits=True, max_new_tokens=1, do_sample=False
      4. Assert len(out.logits) == 1
      5. Extract logits[0][0] (shape: [vocab_size])
      6. log_softmax → pair tensor → softmax → scalar c
      7. Assert 0.0 <= c <= 1.0
    """
    # 1. Format prompt
    prompt = prompt_template.format(
        problem_description=problem_prompt,
        solution_code=solution_code,
    )

    # 2. Tokenize
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    # Move to model device
    model_device = next(model.parameters()).device
    inputs = {k: v.to(model_device) for k, v in inputs.items()}

    # 3. Generate
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            return_dict_in_generate=True,
            output_logits=True,
            do_sample=False,
        )

    # 4. Assert exactly 1 logit step
    assert hasattr(out, "logits"), "Model output missing 'logits' attribute (requires transformers >= 4.38.0)"
    assert len(out.logits) == 1, f"Expected 1 logit step, got {len(out.logits)}"

    # 5. Extract logits[0][0] → shape: [vocab_size]
    logits = out.logits[0][0]  # batch=0, step=0 → [vocab_size]
    assert logits.shape[0] > 30000, f"Unexpected vocab size: {logits.shape[0]}"

    # 6. log_softmax → pair → softmax → scalar
    log_probs = F.log_softmax(logits, dim=-1)
    pair = torch.tensor([log_probs[true_id].item(), log_probs[false_id].item()])
    c = torch.softmax(pair, dim=0)[0].item()

    # 7. Assert in [0, 1]
    assert 0.0 <= c <= 1.0, f"Confidence out of range: {c}"
    return c


def run_ptrue_inference_for_model(
    model_id: str,
    pairs: list[dict],
    device: str,
    checkpoint_path: Path,
    prompt_template: str,
    checkpoint_interval: int = CHECKPOINT_INTERVAL,
) -> dict[str, dict]:
    """Run P(True) extraction for all pairs of one model.

    Returns:
        {task_id: {tier, pass_at_1, confidence_scores: list[float], correctness_labels: list[int]}}
    """
    checkpoint_path = Path(checkpoint_path)

    # Resume: load existing checkpoint
    results: dict[str, dict] = {}
    done_keys: set[str] = set()
    if checkpoint_path.exists():
        with open(checkpoint_path) as f:
            results = json.load(f)
        # done_keys are task__solN keys
        for task_id, task_data in results.items():
            n = len(task_data.get("confidence_scores", []))
            for i in range(n):
                done_keys.add(f"{task_id}__sol{i}")
        logger.info(f"Resumed from checkpoint: {len(done_keys)} pairs already done")

    # Load model
    model, tokenizer = load_model_and_tokenizer(model_id, device)
    true_id, false_id = get_true_false_token_ids(tokenizer)

    # Store sample logits for mechanism verification
    out_logits_sample: list = []

    logger.info(f"Running P(True) inference for {model_id}: {len(pairs)} pairs")

    for i, pair in enumerate(tqdm(pairs, desc=f"P(True) {MODEL_SHORT_NAMES.get(model_id, model_id)}")):
        key = f"{pair['task_id']}__sol{pair['sol_idx']}"
        if key in done_keys:
            continue

        try:
            # Collect sample logits for mechanism check (first 3 calls)
            if len(out_logits_sample) < 3:
                # Get raw logits for mechanism verification
                prompt = prompt_template.format(
                    problem_description=pair["problem_prompt"],
                    solution_code=pair["solution_code"],
                )
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
                model_device = next(model.parameters()).device
                inputs = {k: v.to(model_device) for k, v in inputs.items()}
                with torch.no_grad():
                    raw_out = model.generate(
                        **inputs,
                        max_new_tokens=1,
                        return_dict_in_generate=True,
                        output_logits=True,
                        do_sample=False,
                    )
                out_logits_sample.append(raw_out.logits)
                # Extract confidence from existing raw_out
                logits = raw_out.logits[0][0]
                log_probs = F.log_softmax(logits, dim=-1)
                p_pair = torch.tensor([log_probs[true_id].item(), log_probs[false_id].item()])
                c = torch.softmax(p_pair, dim=0)[0].item()
            else:
                c = extract_ptrue_confidence(
                    model, tokenizer,
                    pair["problem_prompt"], pair["solution_code"],
                    device, true_id, false_id, prompt_template,
                )
        except Exception as e:
            logger.warning(f"Error on pair {key}: {e}. Skipping.")
            continue

        # Accumulate results
        task_entry = results.setdefault(pair["task_id"], {
            "tier": pair["tier"],
            "pass_at_1": pair["pass_at_1"],
            "confidence_scores": [],
            "correctness_labels": [],
        })
        task_entry["confidence_scores"].append(c)
        task_entry["correctness_labels"].append(pair["correctness"])

        # Checkpoint every N pairs
        if (i + 1) % checkpoint_interval == 0:
            with open(checkpoint_path, "w") as f:
                json.dump(results, f)
            logger.debug(f"Checkpoint saved: {i+1} pairs")

    # Final save + cleanup
    with open(checkpoint_path, "w") as f:
        json.dump(results, f)
    logger.info(f"Inference complete. Results: {len(results)} tasks. Checkpoint: {checkpoint_path}")

    # Attach sample logits to results for mechanism verification
    # Store as module-level variable for retrieval
    _last_out_logits_sample.clear()
    _last_out_logits_sample.extend(out_logits_sample)

    del model
    torch.cuda.empty_cache()

    return results


# Module-level storage for out_logits_sample (for mechanism verification)
_last_out_logits_sample: list = []


def verify_ptrue_mechanism(
    confidence_scores_by_model: dict[str, list[float]],
    out_logits_sample: list,
) -> tuple[bool, dict]:
    """Check 4 mechanism activation indicators (FR-8).

    Args:
        confidence_scores_by_model: {model_short: [c values]}
        out_logits_sample: list of raw logit tensors from generate() calls

    Returns:
        (all_pass: bool, indicators: dict)
    """
    indicators = {
        "logits_extracted": (
            out_logits_sample is not None and len(out_logits_sample) > 0
        ),
        "vocab_size_correct": (
            out_logits_sample is not None
            and len(out_logits_sample) > 0
            and out_logits_sample[0][0].shape[0] > 30000
        ),
        "c_values_in_range": all(
            0.0 <= c <= 1.0
            for scores in confidence_scores_by_model.values()
            for c in scores
        ),
        "non_degenerate": all(
            float(np.std(scores)) > 0.05
            for scores in confidence_scores_by_model.values()
            if len(scores) > 0
        ),
    }
    return all(indicators.values()), indicators
