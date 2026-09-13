"""Gradient noise analysis comparing traceback vs ground truth concentration."""
import torch
from typing import List, Dict, Optional
from tqdm import tqdm

from h_m3_gradient import tokenize_with_lines, extract_token_gradients, aggregate_gradients_by_line
from sample_builder import NoiseSample


def build_reward_vector(
    line_numbers: List[int],
    target_line: int,
    target_penalty: float = -1.0,
    other_penalty: float = -0.1,
) -> torch.Tensor:
    """Build reward vector with penalty at target line."""
    rewards = torch.ones(len(line_numbers)) * other_penalty
    for i, line in enumerate(line_numbers):
        if line == target_line:
            rewards[i] = target_penalty
    return rewards


def measure_sample_noise(
    model,
    tokenizer,
    sample: NoiseSample,
    target_penalty: float = -1.0,
    other_penalty: float = -0.1,
    eps: float = 1e-8,
) -> Optional[Dict[str, float]]:
    """Measure gradient concentration at ground truth vs traceback."""
    try:
        tokens, line_numbers = tokenize_with_lines(sample.code, tokenizer)
        if not tokens or not line_numbers:
            return None

        token_ids = [t.token_id for t in tokens]
        input_ids = torch.tensor([token_ids])
        decoder_ids = torch.tensor([[tokenizer.pad_token_id] + token_ids])

        rewards = build_reward_vector(line_numbers, sample.traceback_line, target_penalty, other_penalty)

        token_grads = extract_token_gradients(model, input_ids, decoder_ids, rewards)
        line_grads = aggregate_gradients_by_line(token_grads, line_numbers)

        if sample.ground_truth_line not in line_grads:
            return None

        gt_grad = line_grads.get(sample.ground_truth_line, 0.0)
        tb_grad = line_grads.get(sample.traceback_line, 0.0)

        other_lines = [l for l in line_grads.keys()
                       if l not in (sample.ground_truth_line, sample.traceback_line)]
        other_grad = sum(line_grads[l] for l in other_lines) / max(len(other_lines), 1) if other_lines else eps

        gt_concentration = gt_grad / max(other_grad, eps)
        noise_ratio = tb_grad / max(gt_grad, eps)
        traceback_matches_gt = (sample.traceback_line == sample.ground_truth_line)

        return {
            "gt_grad": gt_grad,
            "tb_grad": tb_grad,
            "other_grad": other_grad,
            "gt_concentration": gt_concentration,
            "noise_ratio": noise_ratio,
            "traceback_matches_gt": traceback_matches_gt,
        }

    except Exception as e:
        return None


def run_noise_analysis(
    model,
    tokenizer,
    samples: List[NoiseSample],
    target_penalty: float = -1.0,
    other_penalty: float = -0.1,
) -> Dict[str, List[Dict]]:
    """Run noise analysis on samples, stratified by error type."""
    results = {"u_line": [], "u_ignore": []}

    for sample in tqdm(samples, desc="Analyzing noise"):
        metrics = measure_sample_noise(model, tokenizer, sample, target_penalty, other_penalty)
        if metrics is None:
            continue

        key = "u_line" if sample.error_type == "U_line" else "u_ignore"
        results[key].append(metrics)

    print(f"Analysis complete: u_line={len(results['u_line'])}, u_ignore={len(results['u_ignore'])}")
    return results
