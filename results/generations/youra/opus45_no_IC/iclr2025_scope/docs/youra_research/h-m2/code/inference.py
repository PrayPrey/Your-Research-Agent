"""H-M2: Inference pipeline - run 3 conditions (full, 80%, 40%)."""

import torch
import numpy as np
from tqdm import tqdm
from typing import List, Dict

from h2o_eviction import H2OWrapper
from accuracy import compute_accuracy
from config import EvictionConfig


def run_condition(model, tokenizer, samples: List[dict], retention_ratio: float,
                  eviction_config: EvictionConfig, max_new_tokens: int = 128) -> List[float]:
    """Run inference at one retention ratio, return per-sample accuracy."""
    device = next(model.parameters()).device
    wrapper = H2OWrapper(model, tokenizer, retention_ratio,
                         eviction_config.heavy_ratio_frac,
                         eviction_config.recent_ratio_frac)

    if retention_ratio < 1.0:
        wrapper.attach()

    accuracies = []

    for sample in tqdm(samples, desc=f"ratio={retention_ratio}"):
        text = sample["context"][:4000] + "\n\nQuestion: " + sample.get("question", "") + "\n\nAnswer:"

        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=2048)
        input_ids = inputs.input_ids.to(device)
        attention_mask = inputs.attention_mask.to(device)

        with torch.no_grad():
            output_ids = wrapper.generate(input_ids, max_new_tokens, attention_mask)

        prompt_len = input_ids.shape[1] if retention_ratio >= 1.0 else output_ids.shape[1] - max_new_tokens
        prompt_len = max(0, min(prompt_len, output_ids.shape[1] - 1))

        generated = tokenizer.decode(output_ids[0, prompt_len:], skip_special_tokens=True)
        reference = sample.get("answer", "")
        domain = sample.get("domain", "")

        acc = compute_accuracy(generated, reference, domain)
        accuracies.append(acc)

    if retention_ratio < 1.0:
        wrapper.detach()

    return accuracies


def run_all_conditions(model, tokenizer, samples: List[dict],
                       eviction_config: EvictionConfig,
                       max_new_tokens: int = 128) -> Dict[float, List[float]]:
    """Run all retention conditions."""
    results = {}

    for ratio in eviction_config.retention_ratios:
        print(f"\n=== Running ratio={ratio} ===")
        accuracies = run_condition(model, tokenizer, samples, ratio,
                                   eviction_config, max_new_tokens)
        results[ratio] = accuracies
        print(f"Mean accuracy: {np.mean(accuracies):.4f}")

    return results


def compute_retention(acc_by_condition: Dict[float, List[float]]) -> Dict[float, np.ndarray]:
    """Compute retention = evicted_acc / full_acc."""
    full_acc = np.array(acc_by_condition[1.0])
    full_acc = np.where(full_acc == 0, 1e-6, full_acc)

    retention = {}
    for ratio, accs in acc_by_condition.items():
        retention[ratio] = np.array(accs) / full_acc

    return retention
