"""
evaluate.py — Evaluation runner for H-M1 attention entropy mechanistic analysis.

Orchestrates: load adapters -> run inference -> collect metrics -> statistical analysis.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import List

import torch
from transformers import AutoTokenizer

from config import ExperimentConfig, InferenceConfig
from data import LongBenchDataLoader
from model import AttentionAnalysisExtractor, load_adapter_model
from analyze import MetricsAggregator, StatisticalAnalyzer

logger = logging.getLogger(__name__)


def _get_num_layers(model_name: str) -> int:
    """Infer number of hidden layers from model config."""
    from transformers import AutoConfig
    cfg = AutoConfig.from_pretrained(model_name)
    return getattr(cfg, "num_hidden_layers", 32)


def run_inference_condition(
    extractor: AttentionAnalysisExtractor,
    dataloader: LongBenchDataLoader,
    aggregator: MetricsAggregator,
    condition: str,
    device: str,
    min_samples_per_category: int = 500,
) -> MetricsAggregator:
    """Iterate LongBench samples per category; extract per-layer metrics; feed aggregator."""
    category_counts: dict = defaultdict(int)

    for sample in dataloader.iter_all_samples():
        cat = sample["category"]
        if category_counts[cat] >= min_samples_per_category:
            continue

        # Clamp to model vocab size before moving to device to avoid out-of-range embedding lookup
        model_cfg = getattr(extractor.model, "config", None) or getattr(extractor.model.base_model, "config", None)
        vocab_size = model_cfg.vocab_size if model_cfg else 50257
        input_ids = sample["input_ids"].unsqueeze(0).clamp(0, vocab_size - 1).to(device)
        attn_mask = sample["attention_mask"].unsqueeze(0).to(device)

        try:
            entropy_list, hh_list = extractor.extract_metrics(input_ids, attn_mask)
        except Exception as e:
            logger.warning(f"extract_metrics failed for sample {sample['sample_id']}: {e}")
            continue

        aggregator.add_sample(
            condition,
            entropy_list,
            hh_list,
            task=sample["task"],
            category=cat,
        )
        category_counts[cat] += 1

        if cat in category_counts and category_counts[cat] % 50 == 0:
            logger.info(f"  [{condition}] {cat}: {category_counts[cat]} samples")

    return aggregator


def collect_layer_metrics(
    baseline_cfg: InferenceConfig,
    proposed_cfg: InferenceConfig,
    experiment_cfg: ExperimentConfig,
    device: str,
) -> MetricsAggregator:
    """Load both adapter models, run both conditions, return populated aggregator."""
    num_layers = _get_num_layers(baseline_cfg.model_name)
    aggregator = MetricsAggregator(num_layers)

    tokenizer = AutoTokenizer.from_pretrained(baseline_cfg.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # --- Baseline condition ---
    logger.info("Loading baseline model...")
    baseline_model = load_adapter_model(
        baseline_cfg.model_name,
        baseline_cfg.adapter_checkpoint,
        "baseline",
        baseline_cfg.kv_budget_ratio,
    )
    baseline_ext = AttentionAnalysisExtractor(baseline_model, top_ratio=baseline_cfg.top_ratio)
    dl = LongBenchDataLoader(tokenizer, baseline_cfg.max_seq_length)
    logger.info("Running baseline inference...")
    run_inference_condition(
        baseline_ext, dl, aggregator, "baseline", device,
        experiment_cfg.min_samples_per_category,
    )
    del baseline_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # --- Eviction-aware condition ---
    logger.info("Loading eviction-aware model...")
    proposed_model = load_adapter_model(
        proposed_cfg.model_name,
        proposed_cfg.adapter_checkpoint,
        "eviction-aware",
        proposed_cfg.kv_budget_ratio,
    )
    proposed_ext = AttentionAnalysisExtractor(proposed_model, top_ratio=proposed_cfg.top_ratio)
    logger.info("Running eviction-aware inference...")
    run_inference_condition(
        proposed_ext, dl, aggregator, "eviction-aware", device,
        experiment_cfg.min_samples_per_category,
    )
    del proposed_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return aggregator


def run_evaluation(
    experiment_cfg: ExperimentConfig,
    device: str,
) -> dict:
    """Full pipeline: collect metrics -> statistical analysis -> gate check.

    Returns results dict with gate pass/fail.
    """
    models = experiment_cfg.models
    # Expect pairs: [llama_baseline, llama_eviction, mistral_baseline, mistral_eviction]
    results_per_model = []

    # Process model pairs (baseline + eviction-aware)
    for i in range(0, len(models), 2):
        if i + 1 >= len(models):
            break
        baseline_cfg = models[i]
        proposed_cfg = models[i + 1]
        model_label = baseline_cfg.model_name.split("/")[-1]

        logger.info(f"=== Processing model pair: {model_label} ===")
        try:
            aggregator = collect_layer_metrics(baseline_cfg, proposed_cfg, experiment_cfg, device)
        except FileNotFoundError as e:
            logger.warning(f"Skipping {model_label}: {e}")
            continue

        layer_metrics = aggregator.get_layer_metrics()
        analyzer = StatisticalAnalyzer()
        stat_results = analyzer.run_paired_ttest(layer_metrics)
        gate = analyzer.compute_gate_result(
            stat_results,
            significance_threshold=experiment_cfg.significance_threshold,
            gate_fraction=experiment_cfg.gate_layer_fraction,
        )
        summary = analyzer.summarize(stat_results)

        results_per_model.append({
            "model_label": model_label,
            "gate": gate,
            "summary": summary,
            "stat_results": [vars(r) for r in stat_results],
            "aggregator": aggregator,
        })

    # Overall gate: pass if any model pair passes
    overall_passed = any(r["gate"]["passed"] for r in results_per_model)
    fraction_avg = (
        sum(r["gate"]["fraction_significant"] for r in results_per_model) / len(results_per_model)
        if results_per_model else 0.0
    )

    return {
        "gate_passed": overall_passed,
        "gate_type": "MUST_WORK",
        "fraction_significant": fraction_avg,
        "models": results_per_model,
        "hypothesis_id": experiment_cfg.experiment_id,
    }
