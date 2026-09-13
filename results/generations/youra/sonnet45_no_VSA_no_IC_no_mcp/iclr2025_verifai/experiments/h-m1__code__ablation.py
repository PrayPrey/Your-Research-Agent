"""Ablation study runner for beam width k."""

import time
import torch

from diversity import measure_diversity


def run_beam_search(model, tokenizer, prompts, k, max_tokens):
    """
    Run beam search.
    Returns: ([[k candidates for prompt1], ...], beam_maintained_per_problem)
    """
    all_candidates = []
    beam_maintained_list = []

    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                num_beams=k,
                num_return_sequences=k,
                max_new_tokens=max_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )

        candidates = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        candidates = [c[len(prompt):].strip() for c in candidates]

        beam_maintained = (len(candidates) == k)
        all_candidates.append(candidates)
        beam_maintained_list.append(beam_maintained)

    return all_candidates, beam_maintained_list


def run_ablation_study(model, tokenizer, prompts, k_values, max_tokens):
    """
    Run beam search for each k, return metrics.
    Returns: {k: {beam_maintained, diversity, time_sec, ...}}
    """
    results = {}

    for k in k_values:
        start = time.time()

        outputs, beam_maintained_list = run_beam_search(
            model, tokenizer, prompts, k, max_tokens
        )

        elapsed = time.time() - start

        results[k] = {
            'beam_maintained': all(beam_maintained_list),
            'beam_maintained_per_problem': beam_maintained_list,
            'diversity': [measure_diversity(out) for out in outputs],
            'time_sec': elapsed,
            'outputs': outputs
        }

    return results


def compare_ablation_results(results):
    """
    Compute comparison statistics.
    Returns: {k: {avg_diversity, time_sec}}
    """
    comparison = {}

    for k, metrics in results.items():
        div_ratios = [d['diversity_ratio'] for d in metrics['diversity']]
        comparison[k] = {
            'avg_diversity': sum(div_ratios) / len(div_ratios),
            'time_sec': metrics['time_sec']
        }

    return comparison
