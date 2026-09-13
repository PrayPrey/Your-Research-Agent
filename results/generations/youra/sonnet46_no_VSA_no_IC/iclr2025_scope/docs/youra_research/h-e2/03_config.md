# Configuration: h-e2

**Hypothesis:** Entropy-guided k=4 SWA(w=512) zero-shot conversion of Llama-2-7B maintains WikiText-103 PPL within 2.0 points of baseline.
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-22

Applied: HuggingFace dataclass experiment config pattern (standard defaults from HF training scripts)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-E6: Orchestration + Results + Visualization [Complexity: 2, Budget: 2 subtasks]

### C-E6-1: ExperimentConfig Dataclass + Results JSON Schema

```python
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json
import os
from datetime import datetime

@dataclass
class ExperimentConfig:
    # Model
    model_name: str = "meta-llama/Llama-2-7b-hf"
    attn_implementation: str = "eager"  # Non-standard: must be eager; flash_attn_2/sdpa cannot accept external SWA masks
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"

    # Calibration (entropy ranking — reuses h-e1 setup)
    calib_n_sequences: int = 100
    calib_split: str = "validation"

    # SWA
    swa_k: int = 4               # number of high-entropy layers to convert
    swa_window_size: int = 512   # sliding window size

    # Evaluation
    eval_max_length: int = 4096  # Llama-2 context window
    eval_stride: int = 512       # Non-standard: must equal swa_window_size for fair SWA comparison

    # Verification
    verify_seq_len: int = 600    # Non-standard: > window_size (512) so position 599 has attended=512 not seq_len

    # Output
    results_dir: str = "results"
    figures_dir: str = "figures"
    seed: int = 1


def save_results(
    config: ExperimentConfig,
    ppl_baseline: float,
    ppl_swa_k4: float,
    target_layers: List[int],
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
        "depth_positions": depth_positions,
        "gate_pass": gate_pass,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if output_path is None:
        os.makedirs(config.results_dir, exist_ok=True)
        output_path = os.path.join(config.results_dir, "h_e2_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    return results


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
```

**Results JSON schema** (written by `save_results`):
```json
{
  "hypothesis_id": "h-e2",
  "config": {"model_name": "...", "swa_k": 4, "swa_window_size": 512, "...": "..."},
  "ppl_baseline": 5.47,
  "ppl_swa_k4": 6.91,
  "delta_ppl": 1.44,
  "target_layers": [8, 14, 21, 27],
  "depth_positions": {"early": 0, "mid": 2, "late": 2},
  "gate_pass": true,
  "timestamp": "2026-08-22T10:00:00Z"
}
```

---

### C-E6-2: run_experiment.py Orchestration + Argument Parsing

```python
#!/usr/bin/env python3
"""h-e2: Entropy-guided SWA zero-shot perplexity experiment."""
import argparse

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="h-e2 SWA zero-shot PPL experiment")
    p.add_argument("--model-name", default="meta-llama/Llama-2-7b-hf")
    p.add_argument("--swa-k", type=int, default=4)
    p.add_argument("--swa-window-size", type=int, default=512)
    p.add_argument("--calib-n-sequences", type=int, default=100)
    p.add_argument("--eval-max-length", type=int, default=4096)
    p.add_argument("--eval-stride", type=int, default=512)
    p.add_argument("--verify-seq-len", type=int, default=600)
    p.add_argument("--results-dir", default="results")
    p.add_argument("--figures-dir", default="figures")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--skip-baseline", action="store_true",
                   help="Skip baseline eval if results already saved")
    return p.parse_args()


def main():
    args = parse_args()

    from config import ExperimentConfig, save_results
    cfg = ExperimentConfig(
        model_name=args.model_name,
        swa_k=args.swa_k,
        swa_window_size=args.swa_window_size,
        calib_n_sequences=args.calib_n_sequences,
        eval_max_length=args.eval_max_length,
        eval_stride=args.eval_stride,
        verify_seq_len=args.verify_seq_len,
        results_dir=args.results_dir,
        figures_dir=args.figures_dir,
        seed=args.seed,
    )

    # --- Step 1: Load model + tokenizer ---
    model, tokenizer = load_model(cfg)

    # --- Step 2: Calibration — entropy ranking (h-e1 logic) ---
    entropy_layer_ranking = compute_entropy_ranking(model, tokenizer, cfg)

    # --- Step 3: Baseline perplexity ---
    if not args.skip_baseline:
        ppl_baseline = compute_perplexity(model, tokenizer, cfg)
        print(f"Baseline PPL: {ppl_baseline:.4f}")
    else:
        ppl_baseline = load_cached_baseline(cfg)

    # --- Step 4: Apply SWA patches ---
    target_layers = apply_entropy_guided_swa(model, entropy_layer_ranking,
                                             k=cfg.swa_k,
                                             window_size=cfg.swa_window_size)

    # --- Step 5: Verify mechanism (mandatory) ---
    verify_swa_mechanism(model, target_layers,
                         window_size=cfg.swa_window_size,
                         test_seq_len=cfg.verify_seq_len)

    # --- Step 6: SWA perplexity ---
    ppl_swa_k4 = compute_perplexity(model, tokenizer, cfg)
    print(f"SWA-k{cfg.swa_k} PPL: {ppl_swa_k4:.4f}")

    delta_ppl = ppl_swa_k4 - ppl_baseline
    gate_pass = delta_ppl <= 2.0
    print(f"delta_ppl={delta_ppl:.4f}  gate={'PASS' if gate_pass else 'FAIL'}")

    # --- Step 7: Save results ---
    results = save_results(cfg, ppl_baseline, ppl_swa_k4, target_layers, gate_pass)

    # --- Step 8: Visualize ---
    plot_ppl_comparison(ppl_baseline, ppl_swa_k4, cfg)
    plot_layer_entropy(entropy_layer_ranking, target_layers, cfg)

    return results


if __name__ == "__main__":
    main()
```

**Orchestration flow** (sequential, no parallelism needed for single-GPU PoC):
1. Load model (`attn_implementation="eager"` enforced)
2. Entropy ranking on calibration set (reuses h-e1 logic, head-mean pooling)
3. Baseline PPL (full attention, no patches)
4. Apply SWA monkey-patches to `target_layers`
5. Verify SWA mask via forward hooks (`verify_seq_len=600 > window_size=512`)
6. SWA PPL
7. Save JSON results
8. Generate figures

---

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E6-1 | ExperimentConfig + Results Schema | `ExperimentConfig` dataclass, `save_results()`, `_compute_depth_positions()`, JSON schema |
| C-E6-2 | run_experiment.py Orchestration | `parse_args()`, `main()` with 8-step sequential flow, `--skip-baseline` flag |
