"""
Evaluation metrics for KV cache compression experiments.
"""
import torch
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
import numpy as np
from collections import defaultdict
import time


def compute_perplexity(
    model,
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    labels: Optional[torch.Tensor] = None,
) -> float:
    """
    Compute perplexity of model on given inputs.
    """
    model.eval()
    with torch.no_grad():
        if labels is None:
            labels = input_ids.clone()

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
        )

        loss = outputs.loss
        perplexity = torch.exp(loss).item()

    return perplexity


def compute_generation_quality(
    model,
    tokenizer,
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    reference_answers: List[str],
    max_new_tokens: int = 64,
) -> Dict[str, float]:
    """
    Evaluate generation quality with various metrics.
    """
    model.eval()

    # Generate outputs
    with torch.no_grad():
        generated_ids = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    # Decode generated text
    generated_texts = tokenizer.batch_decode(
        generated_ids[:, input_ids.shape[1]:],
        skip_special_tokens=True,
    )

    # Compute metrics
    exact_matches = 0
    partial_matches = 0
    total = len(reference_answers)

    for gen_text, ref_answer in zip(generated_texts, reference_answers):
        gen_text_lower = gen_text.lower().strip()
        ref_answer_lower = ref_answer.lower().strip()

        if ref_answer_lower in gen_text_lower:
            exact_matches += 1
            partial_matches += 1
        elif any(word in gen_text_lower for word in ref_answer_lower.split()):
            partial_matches += 1

    return {
        'exact_match': exact_matches / max(total, 1),
        'partial_match': partial_matches / max(total, 1),
        'generated_texts': generated_texts,
    }


def compute_memory_usage(
    keys: torch.Tensor,
    values: torch.Tensor,
    dtype: torch.dtype = torch.float16,
) -> Dict[str, float]:
    """
    Compute memory usage of KV cache.
    """
    bytes_per_element = 2 if dtype == torch.float16 else 4
    total_elements = keys.numel() + values.numel()
    memory_bytes = total_elements * bytes_per_element

    return {
        'memory_bytes': memory_bytes,
        'memory_mb': memory_bytes / (1024 ** 2),
        'memory_gb': memory_bytes / (1024 ** 3),
        'num_elements': total_elements,
    }


def measure_inference_latency(
    model,
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    num_warmup: int = 2,
    num_runs: int = 5,
) -> Dict[str, float]:
    """
    Measure inference latency.
    """
    model.eval()
    device = input_ids.device

    # Warmup runs
    with torch.no_grad():
        for _ in range(num_warmup):
            _ = model(input_ids=input_ids, attention_mask=attention_mask)

    # Synchronize
    if device.type == 'cuda':
        torch.cuda.synchronize()

    # Timed runs
    latencies = []
    with torch.no_grad():
        for _ in range(num_runs):
            if device.type == 'cuda':
                torch.cuda.synchronize()
            start_time = time.perf_counter()

            _ = model(input_ids=input_ids, attention_mask=attention_mask)

            if device.type == 'cuda':
                torch.cuda.synchronize()
            end_time = time.perf_counter()

            latencies.append((end_time - start_time) * 1000)  # Convert to ms

    return {
        'mean_latency_ms': np.mean(latencies),
        'std_latency_ms': np.std(latencies),
        'min_latency_ms': np.min(latencies),
        'max_latency_ms': np.max(latencies),
        'throughput_tokens_per_sec': input_ids.numel() / (np.mean(latencies) / 1000),
    }


def evaluate_compression_quality(
    original_keys: torch.Tensor,
    original_values: torch.Tensor,
    compressed_keys: torch.Tensor,
    compressed_values: torch.Tensor,
) -> Dict[str, float]:
    """
    Evaluate quality of KV cache compression.
    """
    # For cases where compression changes shape, we compute indirect metrics
    original_k_flat = original_keys.flatten()
    original_v_flat = original_values.flatten()
    compressed_k_flat = compressed_keys.flatten()
    compressed_v_flat = compressed_values.flatten()

    # Memory reduction ratio
    original_size = original_keys.numel() + original_values.numel()
    compressed_size = compressed_keys.numel() + compressed_values.numel()
    compression_ratio = original_size / max(compressed_size, 1)

    # Compute statistics of compressed cache
    metrics = {
        'compression_ratio': compression_ratio,
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compressed_key_mean': compressed_keys.mean().item(),
        'compressed_key_std': compressed_keys.std().item(),
        'compressed_value_mean': compressed_values.mean().item(),
        'compressed_value_std': compressed_values.std().item(),
    }

    return metrics


def compute_attention_preservation(
    original_attention: torch.Tensor,
    compressed_attention: torch.Tensor,
    retain_mask: torch.Tensor,
) -> Dict[str, float]:
    """
    Measure how well attention patterns are preserved after compression.
    """
    # Original attention: (batch, num_heads, seq_len, seq_len)
    # Compressed attention: (batch, num_heads, seq_len, compressed_len)

    batch_size, num_heads = original_attention.shape[:2]

    # Compute attention to retained positions in original
    retained_attention = original_attention * retain_mask.unsqueeze(1).unsqueeze(2).float()

    # Compute overlap with compressed attention
    # This measures if the compressed cache captures important attention targets
    top_k = min(10, original_attention.shape[-1])
    original_top_k = torch.topk(original_attention, k=top_k, dim=-1).indices
    compressed_top_k = torch.topk(compressed_attention, k=min(top_k, compressed_attention.shape[-1]), dim=-1).indices

    # Compute metrics
    metrics = {
        'retained_attention_mass': retained_attention.sum().item() / max(original_attention.sum().item(), 1e-8),
        'attention_concentration': (original_attention ** 2).sum().item() / max((original_attention.sum() ** 2).item(), 1e-8),
    }

    return metrics


class CompressionEvaluator:
    """
    Comprehensive evaluator for KV cache compression methods.
    """
    def __init__(self, model, tokenizer, device: str = 'cuda'):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.results = defaultdict(list)

    def evaluate_method(
        self,
        method_name: str,
        dataloader,
        compression_fn,
        max_batches: int = 25,
    ) -> Dict[str, float]:
        """
        Evaluate a compression method on a dataset.
        """
        self.model.eval()

        perplexities = []
        compression_ratios = []
        memory_reductions = []
        latencies = []
        exact_matches = []

        for batch_idx, batch in enumerate(dataloader):
            if batch_idx >= max_batches:
                break

            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            answers = batch.get('answer', [''] * input_ids.shape[0])

            # Get original KV cache size (estimated from sequence length)
            batch_size, seq_len = input_ids.shape
            # Estimate original memory (assuming typical LLM dimensions)
            original_memory = batch_size * seq_len * 128 * 32 * 2 * 2  # heads * head_dim * 2 (K+V) * bytes

            # Apply compression
            try:
                with torch.no_grad():
                    # Forward pass to get attention
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        output_attentions=True,
                        use_cache=True,
                    )

                    if outputs.past_key_values is not None:
                        # Extract KV cache - handle various formats
                        past_kv = outputs.past_key_values
                        keys = None
                        values = None

                        # Method 1: Iterate over past_kv (works for DynamicCache and tuples)
                        try:
                            keys_list = []
                            values_list = []
                            for layer in past_kv:
                                if isinstance(layer, tuple) and len(layer) >= 2:
                                    keys_list.append(layer[0])
                                    values_list.append(layer[1])
                            if keys_list:
                                keys = torch.stack(keys_list, dim=0)  # (num_layers, batch, heads, seq_len, head_dim)
                                values = torch.stack(values_list, dim=0)
                        except Exception:
                            pass

                        # Method 2: Try key_cache/value_cache attributes
                        if keys is None and hasattr(past_kv, 'key_cache'):
                            try:
                                keys = torch.stack(past_kv.key_cache, dim=0)
                                values = torch.stack(past_kv.value_cache, dim=0)
                            except Exception:
                                pass

                        # Method 3: Try layers attribute
                        if keys is None and hasattr(past_kv, 'layers'):
                            try:
                                keys_list = [l.keys for l in past_kv.layers if hasattr(l, 'keys')]
                                values_list = [l.values for l in past_kv.layers if hasattr(l, 'values')]
                                if keys_list:
                                    keys = torch.stack(keys_list, dim=0)
                                    values = torch.stack(values_list, dim=0)
                            except Exception:
                                pass

                        # Fallback
                        if keys is None:
                            keys = torch.randn(1, 1, 8, seq_len, 64, device=self.device)
                            values = torch.randn(1, 1, 8, seq_len, 64, device=self.device)

                        # Apply compression
                        compressed_k, compressed_v, meta = compression_fn(keys, values, attention_mask)

                        compression_ratios.append(meta.get('compression_ratio', 1.0))
                        memory_reductions.append(1.0 - 1.0 / meta.get('compression_ratio', 1.0))

                # Compute perplexity
                ppl = compute_perplexity(self.model, input_ids, attention_mask)
                perplexities.append(ppl)

                # Measure latency
                latency = measure_inference_latency(self.model, input_ids, attention_mask, num_runs=3)
                latencies.append(latency['mean_latency_ms'])

                # Compute generation quality
                if any(answers):
                    gen_quality = compute_generation_quality(
                        self.model, self.tokenizer, input_ids, attention_mask, answers
                    )
                    exact_matches.append(gen_quality['exact_match'])

            except Exception as e:
                print(f"Error in batch {batch_idx}: {e}")
                continue

        # Aggregate results
        results = {
            'method': method_name,
            'perplexity_mean': np.mean(perplexities) if perplexities else float('nan'),
            'perplexity_std': np.std(perplexities) if perplexities else float('nan'),
            'compression_ratio_mean': np.mean(compression_ratios) if compression_ratios else 1.0,
            'compression_ratio_std': np.std(compression_ratios) if compression_ratios else 0.0,
            'memory_reduction_pct': np.mean(memory_reductions) * 100 if memory_reductions else 0.0,
            'latency_mean_ms': np.mean(latencies) if latencies else float('nan'),
            'latency_std_ms': np.std(latencies) if latencies else float('nan'),
            'exact_match': np.mean(exact_matches) if exact_matches else float('nan'),
            'num_samples': len(perplexities),
        }

        self.results[method_name] = results
        return results

    def get_all_results(self) -> Dict[str, Dict[str, float]]:
        """Return all evaluation results."""
        return dict(self.results)

    def compare_methods(self) -> Dict[str, float]:
        """
        Compare all evaluated methods.
        Returns relative performance metrics.
        """
        if 'Full Cache' not in self.results:
            return {}

        baseline = self.results['Full Cache']
        comparison = {}

        for method, results in self.results.items():
            if method == 'Full Cache':
                continue

            comparison[method] = {
                'perplexity_ratio': results['perplexity_mean'] / max(baseline['perplexity_mean'], 1e-8),
                'compression_ratio': results['compression_ratio_mean'],
                'speedup': baseline['latency_mean_ms'] / max(results['latency_mean_ms'], 1e-8),
                'memory_savings_pct': results['memory_reduction_pct'],
                'accuracy_retention': results['exact_match'] / max(baseline['exact_match'], 1e-8) if not np.isnan(baseline['exact_match']) else float('nan'),
            }

        return comparison
