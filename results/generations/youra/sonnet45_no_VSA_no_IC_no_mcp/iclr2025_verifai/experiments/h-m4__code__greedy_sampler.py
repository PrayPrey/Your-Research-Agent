"""Greedy sampler for baseline comparison."""

import torch


def run_greedy_baseline(
    model,
    tokenizer,
    prompts: list[str],
    max_tokens: int = 512,
    temperature: float = 0.8
) -> list[str]:
    """
    Run greedy sampling (num_beams=1).

    Args:
        prompts: [N] input prompts

    Returns:
        [N] generated code strings
    """
    outputs = []
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        generated = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            num_beams=1,
            do_sample=False
        )
        output = tokenizer.decode(generated[0], skip_special_tokens=True)
        outputs.append(output)
    return outputs
