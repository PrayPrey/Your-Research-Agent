"""H-M3 Response Generation for QA Evaluation"""
import torch
from torch import nn
from typing import Optional

def generate_response(
    model: nn.Module,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 128,
    device: str = "cuda",
) -> str:
    """Generate response using greedy decoding."""
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=4096,
    ).to(device)

    with torch.no_grad():
        try:
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        except Exception:
            outputs = model.generate(
                inputs["input_ids"],
                max_length=inputs["input_ids"].shape[1] + max_new_tokens,
            )

    generated = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(generated, skip_special_tokens=True)
    return response.strip()
