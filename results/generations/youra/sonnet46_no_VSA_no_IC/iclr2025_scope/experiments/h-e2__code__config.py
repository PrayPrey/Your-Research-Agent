"""ExperimentConfig and results saving for h-e2."""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json
import os
from datetime import datetime


@dataclass
class ExperimentConfig:
    # Model
    model_name: str = "meta-llama/Llama-2-7b-hf"
    # Non-standard: must be eager; flash_attn_2/sdpa cannot accept external SWA masks
    attn_implementation: str = "eager"
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"

    # Calibration (entropy ranking — reuses h-e1 setup)
    calib_n_sequences: int = 100
    calib_split: str = "validation"
    calib_max_seq_len: int = 512

    # SWA
    swa_k: int = 4
    swa_window_size: int = 512

    # Evaluation
    eval_max_length: int = 4096
    # Non-standard: must equal swa_window_size for fair SWA comparison
    eval_stride: int = 512

    # Verification
    # Non-standard: > window_size (512) so position 599 has attended=512 not seq_len
    verify_seq_len: int = 600

    # Output
    results_dir: str = "results"
    figures_dir: str = "figures"
    seed: int = 1


def _compute_depth_positions(target_layers: List[int], n_layers: int = 32) -> dict:
    """Classify converted layers as early/mid/late thirds of the network."""
    third = n_layers // 3
    counts = {"early": 0, "mid": 0, "late": 0}
    for idx in target_layers:
        if idx < third:
            counts["early"] += 1
        elif idx < 2 * third:
            counts["mid"] += 1
        else:
            counts["late"] += 1
    return counts


def save_results(
    config: ExperimentConfig,
    ppl_baseline: float,
    ppl_swa_k4: float,
    target_layers: List[int],
    entropy_scores: List[float],
    gate_pass: bool,
    output_path: Optional[str] = None,
) -> dict:
    depth_positions = _compute_depth_positions(target_layers, n_layers=32)
    results = {
        "hypothesis_id": "h-e2",
        "config": asdict(config),
        "ppl_baseline": ppl_baseline,
        "ppl_swa_k4": ppl_swa_k4,
        "delta_ppl": ppl_swa_k4 - ppl_baseline,
        "target_layers": target_layers,
        "entropy_scores": entropy_scores,
        "depth_positions": depth_positions,
        "gate_pass": gate_pass,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if output_path is None:
        os.makedirs(config.results_dir, exist_ok=True)
        output_path = os.path.join(config.results_dir, "h_e2_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")
    return results
