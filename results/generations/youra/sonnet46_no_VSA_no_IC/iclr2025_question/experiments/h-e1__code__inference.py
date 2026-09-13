"""Model loading and greedy log-prob extraction."""
import os
import sys
import warnings
import logging
import torch
from typing import List, Dict, Tuple, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer

# Suppress verbose transformers warnings
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

from config import MODELS, MAX_NEW_TOKENS
from data_loader import score_answer


def load_model(model_key: str) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """
    Load frozen fp16 model + tokenizer from HuggingFace hub.

    Args:
        model_key: key in MODELS dict ('llama2' or 'mistral')

    Returns:
        (model, tokenizer) — model in eval mode, no grad, fp16
    """
    model_id = MODELS[model_key]

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            attn_implementation="flash_attention_2",
        )
    except Exception:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )
    model.eval()
    return model, tokenizer


def extract_token_logprobs(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    prompt: str,
    max_new_tokens: int = MAX_NEW_TOKENS,
) -> Tuple[List[float], str]:
    """
    Single greedy forward pass; returns per-token log-probs and decoded generated text.

    Returns:
        (logprobs, generated_text)
        logprobs: list of float (all <= 0.0), empty if no tokens generated
    """
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    prompt_len = inputs.input_ids.shape[1]

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            return_dict_in_generate=True,
            output_scores=True,
        )

    token_ids = out.sequences[0, prompt_len:]  # (T,)

    if len(token_ids) == 0:
        return [], ""

    logprobs = []
    for t, score in enumerate(out.scores):
        lp = torch.log_softmax(score, dim=-1)
        tid = token_ids[t].item()
        logprobs.append(lp[0, tid].item())

    # Stop at first newline token
    nl_ids = set(tokenizer.encode("\n", add_special_tokens=False))
    for i, tid in enumerate(token_ids.tolist()):
        if tid in nl_ids:
            logprobs = logprobs[:i]
            token_ids = token_ids[:i]
            break

    generated_text = tokenizer.decode(token_ids, skip_special_tokens=True).strip()
    return logprobs, generated_text


def run_inference(
    samples: List[Dict],
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    max_new_tokens: int = MAX_NEW_TOKENS,
) -> List[Dict]:
    """
    Run inference over all samples; attach logprobs and resolve labels.

    Filters out samples with empty generations (T=0).
    For TruthfulQA, resolves label via ROUGE-L at this stage.
    """
    results = []
    for i, sample in enumerate(samples):
        if i % 100 == 0:
            print(f"  Inference {i}/{len(samples)}...", flush=True)
        prompt = f"Q: {sample['question']}\nA:"
        logprobs, generated_text = extract_token_logprobs(model, tokenizer, prompt, max_new_tokens)

        if len(logprobs) == 0:
            continue

        record = dict(sample)
        record["logprobs"] = logprobs
        record["prompt"] = prompt
        record["generated_text"] = generated_text
        record["label"] = score_answer(generated_text, sample)

        results.append(record)
    return results
