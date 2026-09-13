#!/usr/bin/env python3
"""
Main Experiment Runner for H-E1: Structural Enumeration Preference

Pipeline:
1. Generate/load stimulus pairs (2x2x2 factorial)
2. Score with 4 reward models (ArmoRM, UltraRM, StarlingRM, PairRM)
3. Compute effect sizes (Cohen's d) per RM
4. Check gate condition (d >= 0.3 in >= 2 RMs)
5. Generate visualization figures
"""

import argparse
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd
import numpy as np
import torch
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import ExperimentConfig, GateConfig, MODEL_IDS, get_default_config
from data.stimulus_generator import StimulusGenerator, StimulusPair
from inference.reward_models import (
    load_all_models, ArmoRM, UltraRM, StarlingRM, PairRM,
    score_stimuli_with_rm, BaseRewardModel
)
from analysis.stats import (
    compute_per_rm_stats, compute_aggregate_stats,
    check_gate_condition, export_results
)
from analysis.visualize import generate_all_figures


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('experiment.log')
    ]
)
logger = logging.getLogger(__name__)


def run_stimulus_generation(cfg: ExperimentConfig) -> List[StimulusPair]:
    """
    Generate or load stimulus pairs.

    Args:
        cfg: Experiment configuration

    Returns:
        List of StimulusPairs
    """
    stimuli_path = Path(cfg.output_dir) / "stimuli.json"

    # Check for existing stimuli if resume enabled
    if cfg.resume and stimuli_path.exists():
        logger.info(f"Loading existing stimuli from {stimuli_path}")
        generator = StimulusGenerator(cfg.stimulus)
        return generator.load(str(stimuli_path))

    # Generate new stimuli
    logger.info("Generating stimulus pairs...")
    generator = StimulusGenerator(cfg.stimulus)
    pairs = generator.generate_and_save(str(stimuli_path))
    logger.info(f"Generated {len(pairs)} stimulus pairs")

    return pairs


def run_inference(
    stimuli: List[StimulusPair],
    cfg: ExperimentConfig
) -> pd.DataFrame:
    """
    Score all stimuli with all reward models.

    Args:
        stimuli: List of stimulus pairs
        cfg: Experiment configuration

    Returns:
        DataFrame with columns [rm, prompt_id, structure, score, correctness, completeness]
    """
    scores_path = Path(cfg.output_dir) / "raw_scores.json"

    # Check for existing scores if resume enabled
    if cfg.resume and scores_path.exists():
        logger.info(f"Loading existing scores from {scores_path}")
        with open(scores_path) as f:
            data = json.load(f)
        return pd.DataFrame(data)

    logger.info("Running inference across all reward models...")

    # Prepare stimulus tuples
    stim_tuples = [(s.prompt, s.enumerated, s.synthesized) for s in stimuli]

    all_scores = []

    # Process each RM sequentially to manage VRAM
    rm_classes = {
        "armo": ArmoRM,
        "ultra": UltraRM,
        "starling": StarlingRM,
        "pairrm": PairRM,
    }

    for rm_id in cfg.rm_ids:
        if rm_id not in rm_classes:
            logger.warning(f"Unknown RM: {rm_id}, skipping")
            continue

        logger.info(f"Loading {rm_id.upper()}...")

        # Instantiate and load model
        rm: BaseRewardModel = rm_classes[rm_id]()
        try:
            rm.load(device=cfg.inference.device, use_4bit=cfg.inference.use_4bit)
        except Exception as e:
            logger.error(f"Failed to load {rm_id}: {e}")
            continue

        # Score all stimuli
        logger.info(f"Scoring {len(stim_tuples)} pairs with {rm_id.upper()}...")
        for i, (pair, stim) in enumerate(tqdm(zip(stim_tuples, stimuli), total=len(stimuli),
                                               desc=f"Scoring with {rm_id.upper()}")):
            prompt, enum_resp, synth_resp = pair

            try:
                # Score enumerated response
                enum_score = rm.score(prompt, enum_resp)
                all_scores.append({
                    "rm": rm_id,
                    "prompt_id": stim.id,
                    "structure": "enumerated",
                    "score": float(enum_score),
                    "correctness": stim.correctness,
                    "completeness": stim.completeness,
                })

                # Score synthesized response
                synth_score = rm.score(prompt, synth_resp)
                all_scores.append({
                    "rm": rm_id,
                    "prompt_id": stim.id,
                    "structure": "synthesized",
                    "score": float(synth_score),
                    "correctness": stim.correctness,
                    "completeness": stim.completeness,
                })
            except Exception as e:
                logger.error(f"Error scoring {stim.id} with {rm_id}: {e}")
                continue

        # Unload model to free VRAM
        logger.info(f"Unloading {rm_id.upper()}...")
        rm.unload()

    # Convert to DataFrame
    scores_df = pd.DataFrame(all_scores)

    # Save intermediate results
    with open(scores_path, 'w') as f:
        json.dump(all_scores, f, indent=2)
    logger.info(f"Saved raw scores to {scores_path}")

    return scores_df


def run_analysis(
    scores_df: pd.DataFrame,
    cfg: ExperimentConfig
) -> tuple:
    """
    Compute statistical analysis.

    Args:
        scores_df: Raw scores DataFrame
        cfg: Experiment configuration

    Returns:
        (per_rm_df, aggregate_stats)
    """
    logger.info("Computing statistical analysis...")

    # Per-RM statistics
    per_rm_df = compute_per_rm_stats(scores_df)
    logger.info("\nPer-RM Effect Sizes:")
    for _, row in per_rm_df.iterrows():
        logger.info(f"  {row['rm'].upper()}: d = {row['cohens_d']:.4f} "
                   f"[{row['ci_low']:.4f}, {row['ci_high']:.4f}], "
                   f"p = {row['p_value']:.4f}")

    # Aggregate statistics
    agg_stats = compute_aggregate_stats(per_rm_df)
    logger.info(f"\nPooled Effect Size: d = {agg_stats['pooled_cohens_d']:.4f}")
    logger.info(f"Models with positive effect: {agg_stats['n_positive_effect']}/{agg_stats['n_models']}")
    logger.info(f"Models above threshold (0.3): {agg_stats['n_above_threshold']}/{agg_stats['n_models']}")

    # Export results
    export_results(per_rm_df, agg_stats, cfg.output_dir, scores_df)

    return per_rm_df, agg_stats


def check_gate(per_rm_df: pd.DataFrame, gate_cfg: GateConfig) -> Dict:
    """
    Check gate condition and return verdict.

    Args:
        per_rm_df: Per-RM statistics
        gate_cfg: Gate configuration

    Returns:
        Gate result dictionary
    """
    passed = check_gate_condition(per_rm_df, gate_cfg.d_threshold, gate_cfg.min_models)
    n_passing = sum(1 for d in per_rm_df['cohens_d'] if d >= gate_cfg.d_threshold)

    result = {
        "gate_type": "MUST_WORK",
        "threshold": gate_cfg.d_threshold,
        "min_models": gate_cfg.min_models,
        "n_passing": n_passing,
        "n_total": len(per_rm_df),
        "passed": passed,
        "verdict": "PASS" if passed else "FAIL",
        "details": {
            rm: {"d": float(d), "passes": d >= gate_cfg.d_threshold}
            for rm, d in zip(per_rm_df['rm'], per_rm_df['cohens_d'])
        }
    }

    return result


def generate_report(
    gate_result: Dict,
    per_rm_df: pd.DataFrame,
    agg_stats: Dict,
    output_dir: str
) -> str:
    """
    Generate validation report markdown.

    Args:
        gate_result: Gate check result
        per_rm_df: Per-RM statistics
        agg_stats: Aggregate statistics
        output_dir: Output directory

    Returns:
        Path to generated report
    """
    report_lines = [
        "# H-E1 Validation Report",
        "",
        f"**Generated:** {datetime.now().isoformat()}",
        "",
        "## Gate Condition",
        "",
        f"**Type:** {gate_result['gate_type']}",
        f"**Threshold:** Cohen's d >= {gate_result['threshold']}",
        f"**Requirement:** >= {gate_result['min_models']} RMs must meet threshold",
        f"**Result:** {gate_result['n_passing']}/{gate_result['n_total']} RMs passed",
        f"**Verdict:** **{gate_result['verdict']}**",
        "",
        "## Per-RM Results",
        "",
        "| Model | Cohen's d | 95% CI | p-value | Status |",
        "|-------|-----------|--------|---------|--------|",
    ]

    for _, row in per_rm_df.iterrows():
        status = "✓ PASS" if row['cohens_d'] >= gate_result['threshold'] else "✗ Below"
        report_lines.append(
            f"| {row['rm'].upper()} | {row['cohens_d']:.4f} | "
            f"[{row['ci_low']:.4f}, {row['ci_high']:.4f}] | "
            f"{row['p_value']:.4f} | {status} |"
        )

    report_lines.extend([
        "",
        "## Aggregate Statistics",
        "",
        f"- **Pooled Effect Size:** d = {agg_stats['pooled_cohens_d']:.4f}",
        f"- **Models with positive effect:** {agg_stats['n_positive_effect']}/{agg_stats['n_models']}",
        f"- **Models above threshold:** {agg_stats['n_above_threshold']}/{agg_stats['n_models']}",
        f"- **Heterogeneity (I²):** {agg_stats['heterogeneity']['I2']:.1f}%",
        "",
        "## Figures",
        "",
        "- `figures/forest_plot.png`: Effect size forest plot",
        "- `figures/violin_plot.png`: Score distribution violin plot",
        "- `figures/interaction_plot.png`: Factorial interaction plot",
        "- `figures/gate_metrics.png`: Gate metrics comparison",
        "",
        "## Conclusion",
        "",
    ])

    if gate_result['passed']:
        report_lines.extend([
            "**PASS:** The enumeration preference effect is robust across multiple RMs.",
            "The hypothesis that RLHF-trained reward models systematically prefer ",
            "enumerated responses is supported by this PoC validation.",
            "",
            "**Next Steps:** Proceed to mechanism hypotheses (H-M1, H-M2).",
        ])
    else:
        report_lines.extend([
            "**FAIL:** The enumeration preference effect did not meet the gate threshold.",
            "The effect was not robust enough across multiple architecturally distinct RMs.",
            "",
            "**Recommendation:** Consider revising the hypothesis or methodology.",
        ])

    report_content = "\n".join(report_lines)

    # Save report
    report_path = Path(output_dir).parent / "04_validation.md"
    with open(report_path, 'w') as f:
        f.write(report_content)

    logger.info(f"Report saved to {report_path}")
    return str(report_path)


def main(cfg: Optional[ExperimentConfig] = None) -> Dict:
    """
    Main experiment execution.

    Args:
        cfg: Experiment configuration (uses default if None)

    Returns:
        Experiment results dictionary
    """
    if cfg is None:
        cfg = get_default_config()

    logger.info("=" * 60)
    logger.info("H-E1: Structural Enumeration Preference Experiment")
    logger.info("=" * 60)
    logger.info(f"Output directory: {cfg.output_dir}")
    logger.info(f"Figures directory: {cfg.figures_dir}")
    logger.info(f"Device: {cfg.inference.device}")
    logger.info(f"Models: {cfg.rm_ids}")

    # Ensure output directories exist
    cfg.validate()

    # Set environment for single GPU
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
        # Use first available GPU
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        logger.info("Set CUDA_VISIBLE_DEVICES=0")

    # Step 1: Stimulus Generation
    logger.info("\n--- Step 1: Stimulus Generation ---")
    stimuli = run_stimulus_generation(cfg)
    logger.info(f"Total stimuli: {len(stimuli)}")

    # Step 2: Inference
    logger.info("\n--- Step 2: Multi-RM Inference ---")
    scores_df = run_inference(stimuli, cfg)
    logger.info(f"Total scores: {len(scores_df)}")

    # Step 3: Statistical Analysis
    logger.info("\n--- Step 3: Statistical Analysis ---")
    per_rm_df, agg_stats = run_analysis(scores_df, cfg)

    # Step 4: Gate Check
    logger.info("\n--- Step 4: Gate Check ---")
    gate_result = check_gate(per_rm_df, cfg.gate)
    logger.info(f"Gate verdict: {gate_result['verdict']}")

    # Step 5: Visualization
    logger.info("\n--- Step 5: Visualization ---")
    generate_all_figures(scores_df, per_rm_df, cfg.gate.d_threshold, cfg.figures_dir)

    # Step 6: Report Generation
    logger.info("\n--- Step 6: Report Generation ---")
    report_path = generate_report(gate_result, per_rm_df, agg_stats, cfg.output_dir)

    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Gate Result: {gate_result['verdict']}")
    logger.info(f"Report: {report_path}")
    logger.info(f"Figures: {cfg.figures_dir}/")

    # Return results for programmatic access
    return {
        "gate_result": gate_result,
        "per_rm_stats": per_rm_df.to_dict(orient='records'),
        "aggregate_stats": agg_stats,
        "report_path": report_path,
        "n_stimuli": len(stimuli),
        "n_scores": len(scores_df),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1 Enumeration Preference Experiment")
    parser.add_argument("--output-dir", type=str, default="outputs",
                       help="Output directory for data files")
    parser.add_argument("--figures-dir", type=str, default="figures",
                       help="Output directory for figures")
    parser.add_argument("--no-resume", action="store_true",
                       help="Disable resume from checkpoint")
    parser.add_argument("--use-4bit", action="store_true",
                       help="Use 4-bit quantization for large models")
    parser.add_argument("--rm-ids", type=str, nargs="+",
                       default=["armo", "ultra", "starling", "pairrm"],
                       help="Reward model IDs to use")

    args = parser.parse_args()

    # Build config from args
    cfg = ExperimentConfig()
    cfg.output_dir = args.output_dir
    cfg.figures_dir = args.figures_dir
    cfg.resume = not args.no_resume
    cfg.inference.use_4bit = args.use_4bit
    cfg.rm_ids = args.rm_ids

    # Run experiment
    results = main(cfg)

    # Exit with appropriate code
    sys.exit(0 if results["gate_result"]["passed"] else 1)
