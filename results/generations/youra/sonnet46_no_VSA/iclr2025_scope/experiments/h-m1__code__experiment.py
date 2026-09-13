import pickle
import json
from pathlib import Path
from datetime import datetime

import torch
from tqdm import tqdm

from config import Config
from data import load_teacher, sample_sequences, extract_attention_matrices
from ssd_fitter import SSDFitter
from analysis import compute_scaling_metrics
from visualize import (
    plot_gate_metrics,
    plot_scaling_comparison,
    plot_violin_distribution,
    plot_layer_heatmap,
)


class Experiment:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.fitter = SSDFitter(cfg)

    def run(self) -> dict:
        """
        Main loop: for each seq_len, for each sample, batch-fit all 32 layers.
        Returns errors_by_N dict.
        """
        print(f"Loading teacher model: {self.cfg.teacher_model_id}")
        model, tokenizer = load_teacher(self.cfg.teacher_model_id)

        errors_by_N: dict = {N: [] for N in self.cfg.target_lengths}
        toeplitz_by_N: dict = {N: [] for N in self.cfg.target_lengths}
        layer_errors_8k: list = [0.0] * self.cfg.n_layers

        for seq_len in self.cfg.target_lengths:
            print(f"\n=== Sequence length N={seq_len} ===")

            ckpt_errors, resume_idx = self._load_checkpoint(self.cfg.results_dir, seq_len)
            if ckpt_errors is not None:
                print(f"Resuming from sample {resume_idx}")
                errors_by_N = ckpt_errors

            print(f"Sampling {self.cfg.n_samples} sequences...")
            input_ids_batch = sample_sequences(tokenizer, self.cfg, seq_len)

            for sample_idx in tqdm(range(resume_idx, self.cfg.n_samples), desc=f"N={seq_len}"):
                input_ids = input_ids_batch[sample_idx:sample_idx + 1].cuda()

                # Extract all layers at once: [n_layers, N, N] bfloat16 CPU
                attn_matrices = extract_attention_matrices(
                    model, input_ids, sample_idx, self.cfg
                )

                # Batch-fit all 32 layers simultaneously
                layer_errors = self.fitter.fit_batch_and_measure(attn_matrices)
                toep_errors = self.fitter.toeplitz_errors_batch(attn_matrices)

                for layer_idx in range(self.cfg.n_layers):
                    errors_by_N[seq_len].append(layer_errors[layer_idx])
                    toeplitz_by_N[seq_len].append(toep_errors[layer_idx])
                    if seq_len == 8192:
                        layer_errors_8k[layer_idx] += layer_errors[layer_idx] / self.cfg.n_samples

                del attn_matrices

                if (sample_idx + 1) % self.cfg.checkpoint_every_n_samples == 0:
                    self._checkpoint(errors_by_N, sample_idx, seq_len)

            # Final checkpoint for this seq_len
            self._checkpoint(errors_by_N, self.cfg.n_samples - 1, seq_len)

        return {
            "errors_by_N": errors_by_N,
            "toeplitz_by_N": toeplitz_by_N,
            "layer_errors_8k": layer_errors_8k,
        }

    def _checkpoint(self, errors_by_N: dict, sample_idx: int, seq_len: int) -> None:
        ckpt_path = Path(self.cfg.results_dir) / f"ckpt_N{seq_len}_s{sample_idx:04d}.pkl"
        ckpt_path.parent.mkdir(parents=True, exist_ok=True)
        with open(ckpt_path, "wb") as f:
            pickle.dump({"errors_by_N": errors_by_N, "sample_idx": sample_idx, "seq_len": seq_len}, f)

    @staticmethod
    def _load_checkpoint(results_dir: str, seq_len: int):
        ckpt_files = sorted(Path(results_dir).glob(f"ckpt_N{seq_len}_s*.pkl"))
        if not ckpt_files:
            return None, 0
        with open(ckpt_files[-1], "rb") as f:
            data = pickle.load(f)
        return data["errors_by_N"], data["sample_idx"] + 1

    def save_and_report(self, results: dict, gate_result) -> None:
        errors_by_N = results["errors_by_N"]
        toeplitz_by_N = results["toeplitz_by_N"]
        layer_errors_8k = results["layer_errors_8k"]

        results_dir = Path(self.cfg.results_dir)
        figures_dir = Path(self.cfg.figures_dir)
        results_dir.mkdir(parents=True, exist_ok=True)
        figures_dir.mkdir(parents=True, exist_ok=True)

        with open(results_dir / "errors_by_N.pkl", "wb") as f:
            pickle.dump(errors_by_N, f)

        metrics = {
            "hypothesis_id": "H-M1",
            "gate_pass": gate_result.gate_pass,
            "beta": gate_result.log_slope,
            "pct90_at_8k": gate_result.pct90,
            "mean_errors_by_N": {str(k): v for k, v in gate_result.mean_errors.items()},
            "gate_threshold_slope": self.cfg.gate_slope_threshold,
            "gate_threshold_pct90": self.cfg.gate_pct90_threshold,
            "decision": gate_result.decision,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "n_samples_used": self.cfg.n_samples,
            "n_opt_steps": self.cfg.n_opt_steps,
        }
        with open(results_dir / "gate_metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)

        try:
            plot_gate_metrics(errors_by_N, gate_result, str(figures_dir))
            plot_scaling_comparison(errors_by_N, toeplitz_by_N, gate_result.log_slope, str(figures_dir))
            plot_violin_distribution(errors_by_N, str(figures_dir))
            plot_layer_heatmap(layer_errors_8k, str(figures_dir))
            print("Figures saved.")
        except Exception as e:
            print(f"Warning: figure generation failed: {e}")

        print(f"\n{'='*50}")
        print(f"GATE: {gate_result.decision}")
        print(f"  β (log-log slope) = {gate_result.log_slope:.4f}  (threshold ≤ {self.cfg.gate_slope_threshold})")
        print(f"  90th pct @ N=8k   = {gate_result.pct90:.4f}  (threshold ≤ {self.cfg.gate_pct90_threshold})")
        print(f"  Mean errors: { {k: f'{v:.4f}' for k, v in gate_result.mean_errors.items()} }")
        print(f"{'='*50}")
        print(f"Results saved to {results_dir}")
        print(f"Figures saved to {figures_dir}")
