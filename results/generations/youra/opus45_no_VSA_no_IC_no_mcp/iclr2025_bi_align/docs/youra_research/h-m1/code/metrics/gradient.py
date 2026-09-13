"""Gradient magnitude analysis for smoothness."""
import torch
import numpy as np
from tqdm import tqdm


def compute_gradient_stats(model, tokenizer, test_samples: list, device: str) -> dict:
    """Compute input-space gradient norms for smoothness analysis."""
    model.eval()
    gradients = []

    for sample in tqdm(test_samples[:500], desc="Computing gradients"):
        inputs = tokenizer(
            sample,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding="max_length",
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        embeddings = model.get_input_embeddings()(inputs["input_ids"])
        embeddings = embeddings.detach().requires_grad_(True)

        # Forward through full model (including score head)
        outputs = model(
            inputs_embeds=embeddings,
            attention_mask=inputs["attention_mask"],
        )

        reward = outputs.logits.squeeze(-1).sum()
        reward.backward()

        if embeddings.grad is not None:
            grad_norm = embeddings.grad.norm().item()
            gradients.append(grad_norm)

        model.zero_grad()

    return {
        "mean_gradient_norm": float(np.mean(gradients)),
        "std_gradient_norm": float(np.std(gradients)),
        "max_gradient_norm": float(np.max(gradients)),
    }
