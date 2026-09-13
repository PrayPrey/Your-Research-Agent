"""Generation pipelines: baseline and hooked."""

import time
import torch
from hooks import HiddenStateExtractor


def generate_baseline(model, tokenizer, prompts: list, max_new_tokens: int = 128):
    """Generate without hooks. Returns (decoded_outputs, elapsed_seconds)."""
    outputs = []
    t0 = time.perf_counter()
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        outputs.append(decoded)
    elapsed = time.perf_counter() - t0
    return outputs, elapsed


def generate_hooked(model, tokenizer, prompts: list, max_new_tokens: int = 128, layer_idx: int = 19):
    """Generate with hooks. Returns (decoded_outputs, elapsed_seconds)."""
    outputs = []
    t0 = time.perf_counter()
    with HiddenStateExtractor(model, [layer_idx]) as extractor:
        for prompt in prompts:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                output_ids = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
            decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            outputs.append(decoded)
    elapsed = time.perf_counter() - t0
    return outputs, elapsed
