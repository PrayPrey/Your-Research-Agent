#!/usr/bin/env python3
"""Main experiment script for h-e1 smoke test."""

import os
import sys
import json
import logging
import torch
from pathlib import Path
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent))

from utils.config_loader import load_config, validate_config
from utils.data_loader import WikiTextSampler
from utils.model_loader import ModelLoader
from utils.validators import SmokeTestValidator
from hooks.ssm_state_monitor import SSMStateMonitor
from utils.baseline_runner import BaselineRunner
from utils.reporting import ResultsAggregator, GateDecisionEngine, MarkdownReportGenerator


def setup_logging(config):
    log_dir = Path(config.logging.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.logging.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.logging.log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


def main():
    config_path = Path(__file__).parent / "configs" / "h_e1_config.yaml"
    logger = logging.getLogger(__name__)

    print(f"Loading configuration from {config_path}...")
    config = load_config(str(config_path))
    validate_config(config)

    logger = setup_logging(config)
    logger.info("="*80)
    logger.info("Starting h-e1 smoke test experiment")
    logger.info("="*80)

    torch.manual_seed(config.experiment.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(config.experiment.seed)

    if not torch.cuda.is_available():
        logger.error("CUDA not available. This experiment requires GPU.")
        return 1

    logger.info(f"GPU: {torch.cuda.get_device_name()}")
    logger.info(f"CUDA Version: {torch.version.cuda}")

    # Phase 1: Load data
    logger.info("\n" + "="*80)
    logger.info("Phase 1: Loading dataset")
    logger.info("="*80)

    try:
        data_sampler = WikiTextSampler(
            model_name=config.model.name,
            dataset_name=config.data.dataset_name,
            dataset_config=config.data.dataset_config,
            split=config.data.split,
            sequence_length=config.data.sequence_length,
            seed=config.experiment.seed
        )

        logger.info("Sampling test sequences...")
        sampled_data = data_sampler.sample_sequences(config.data.num_test_sequences)
        input_ids = sampled_data['input_ids']
        sequence_ids = sampled_data['sequence_ids']

        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        seq_ids_path = output_dir / "h_e1_sequence_ids.json"
        data_sampler.save_sequence_ids(sequence_ids, str(seq_ids_path))
        logger.info(f"Saved sequence IDs to {seq_ids_path}")
        logger.info(f"Sampled {len(sequence_ids)} sequences of length {config.data.sequence_length}")

    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        return 1

    # Phase 2: Run baseline experiments
    logger.info("\n" + "="*80)
    logger.info("Phase 2: Running baseline experiments")
    logger.info("="*80)

    model_loader = ModelLoader(config)
    baseline_runner = BaselineRunner(config, model_loader)

    test_input = input_ids[0:1]

    baseline_results = {}
    try:
        baseline_results = baseline_runner.run_all_baselines(test_input)
        logger.info("Baseline experiments completed")

        for name, result in baseline_results.items():
            if result['success']:
                logger.info(f"{name}: {result['latency_ms']:.1f}ms, {result['peak_memory_mb']:.1f}MB")
            else:
                logger.warning(f"{name}: Failed - {result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.warning(f"Baseline experiments failed: {e}")
        logger.info("Continuing with primary experiment...")

    # Phase 3: Load primary model (B4: 4-bit + LoRA)
    logger.info("\n" + "="*80)
    logger.info("Phase 3: Loading primary model (4-bit + LoRA)")
    logger.info("="*80)

    try:
        model, trainable_params, target_modules = model_loader.load_quantized_mamba(apply_lora=True)
        logger.info(f"Model loaded successfully")
        logger.info(f"Target modules: {target_modules}")
        logger.info(f"Trainable parameters: {trainable_params:,}")

        model_info = {
            'trainable_params': trainable_params,
            'target_modules': target_modules if isinstance(target_modules, list) else [target_modules]
        }

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return 1

    # Phase 4: Run smoke test validation
    logger.info("\n" + "="*80)
    logger.info("Phase 4: Running smoke test validation")
    logger.info("="*80)

    validator = SmokeTestValidator(config)
    ssm_monitor = SSMStateMonitor() if config.validation.check_ssm_states else None

    sequence_results = []

    for idx in tqdm(range(len(input_ids)), desc="Validating sequences"):
        logger.info(f"\nValidating sequence {idx+1}/{len(input_ids)}")

        seq_input = input_ids[idx:idx+1]

        if ssm_monitor:
            ssm_monitor.register_hooks(model)

        try:
            result = validator.validate_sequence(model, seq_input, ssm_monitor)
            sequence_results.append(result)

            status = "✅ PASS" if result['overall_passed'] else "❌ FAIL"
            logger.info(f"Sequence {idx}: {status}")
            logger.info(f"  Forward: {result['forward']['passed']}")
            logger.info(f"  Backward: {result['backward']['passed']}")
            if result['ssm_states']:
                logger.info(f"  SSM States: {result['ssm_states']['passed']}")

        except Exception as e:
            logger.error(f"Validation failed for sequence {idx}: {e}")
            sequence_results.append({
                'forward': {'passed': False, 'error': str(e)},
                'backward': {'passed': False},
                'ssm_states': {'passed': False} if ssm_monitor else None,
                'overall_passed': False
            })

        finally:
            if ssm_monitor:
                ssm_monitor.remove_hooks()
                ssm_monitor.reset()

    # Phase 5: Aggregate results and apply gate decision
    logger.info("\n" + "="*80)
    logger.info("Phase 5: Aggregating results and applying gate decision")
    logger.info("="*80)

    aggregator = ResultsAggregator()
    aggregated_results = aggregator.aggregate_sequence_results(sequence_results)

    logger.info(f"Overall pass rate: {aggregated_results['pass_rate_overall']*100:.1f}%")
    logger.info(f"Forward pass rate: {aggregated_results['pass_rate_forward']*100:.1f}%")
    logger.info(f"Backward pass rate: {aggregated_results['pass_rate_backward']*100:.1f}%")
    if aggregated_results['pass_rate_ssm'] is not None:
        logger.info(f"SSM state pass rate: {aggregated_results['pass_rate_ssm']*100:.1f}%")

    gate_engine = GateDecisionEngine()
    gate_decision = gate_engine.apply_gate_logic(aggregated_results)

    logger.info(f"\nGate Decision: {'PASS ✅' if gate_decision['gate_passed'] else 'FAIL ❌'}")
    logger.info(f"Route to: {gate_decision['route_to']}")
    if gate_decision['failure_reason']:
        logger.info(f"Failure reason: {gate_decision['failure_reason']}")

    # Phase 6: Generate reports
    logger.info("\n" + "="*80)
    logger.info("Phase 6: Generating reports")
    logger.info("="*80)

    if config.logging.save_results_json:
        results_json = {
            'experiment': {
                'name': config.experiment.name,
                'hypothesis_id': config.experiment.hypothesis_id,
                'seed': config.experiment.seed
            },
            'model_info': model_info,
            'sequence_results': sequence_results,
            'aggregated_results': aggregated_results,
            'baseline_results': baseline_results,
            'gate_decision': gate_decision
        }

        results_path = output_dir / config.logging.results_file.split('/')[-1]
        with open(results_path, 'w') as f:
            json.dump(results_json, f, indent=2)

        logger.info(f"Saved results to {results_path}")

    report_path = Path(__file__).parent.parent.parent / "docs" / "youra_research" / "h-e1" / "04_validation.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report_gen = MarkdownReportGenerator(config)
    report_gen.generate_report(
        sequence_results=sequence_results,
        baseline_results=baseline_results,
        aggregated_results=aggregated_results,
        gate_decision=gate_decision,
        model_info=model_info,
        output_path=str(report_path)
    )

    logger.info(f"Generated validation report: {report_path}")

    logger.info("\n" + "="*80)
    logger.info("EXPERIMENT COMPLETE")
    logger.info("="*80)
    logger.info(f"Gate Status: {'PASS ✅' if gate_decision['gate_passed'] else 'FAIL ❌'}")
    logger.info(f"Next Step: {gate_decision['route_to']}")
    logger.info("="*80)

    return 0 if gate_decision['gate_passed'] else 1


if __name__ == "__main__":
    sys.exit(main())
