"""
H-M2: JointLoRA-KV Joint Training Experiment
Gate: MUST_WORK — stable convergence (no NaN/divergence) AND LongBench-QA F1 >= B3
"""
import json
import os
import sys

import torch
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig, load_config, save_config
from data import DataManager
from model import build_joint_model, build_baseline_b3_model
from stability import StabilityMonitor
from trainer import JointLoRAKVTrainer, BaselineB3Trainer
from evaluator import LongBenchEvaluator, GLUEEvaluator
from figures import (
    plot_longbench_comparison,
    plot_training_loss_curves,
    plot_loss_distribution,
    plot_per_task_f1,
    plot_gradient_norms,
)
from transformers import AutoTokenizer


class ExperimentRunner:
    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.results_dir = config.paths.results_dir
        self.figures_dir = config.paths.figures_dir
        self.checkpoint_dir = config.paths.checkpoint_dir
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def _load_tokenizer(self):
        tok = AutoTokenizer.from_pretrained(
            self.config.model.base_model, trust_remote_code=True
        )
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        return tok

    def run_seed(self, seed: int, model_type: str) -> dict:
        """Train + evaluate one model for one seed. model_type: 'joint' | 'b3'"""
        print(f"\n{'='*60}")
        print(f"Running seed={seed}, model_type={model_type}")
        print(f"{'='*60}")

        torch.manual_seed(seed)
        np.random.seed(seed)

        tokenizer = self._load_tokenizer()

        # Build data manager with appropriate config
        class _TrainCfg:
            batch_size = self.config.training.batch_size
            max_seq_len_glue = self.config.dataset.max_seq_len_glue
            lora_lr = self.config.training.lora_lr
            locret_lr = self.config.training.locret_lr
            weight_decay = self.config.training.weight_decay
            betas = self.config.training.betas
            eps = self.config.training.eps
            warmup_ratio = self.config.training.warmup_ratio
            max_epochs = self.config.training.max_epochs
            grad_clip_norm = self.config.training.grad_clip_norm

        train_cfg = _TrainCfg()
        data_manager = DataManager(tokenizer, train_cfg)

        # Build model
        if model_type == "joint":
            model = build_joint_model(self.config)
            monitor = StabilityMonitor(
                seed=seed,
                moving_avg_window=self.config.stability.divergence_window,
                divergence_factor=self.config.stability.divergence_threshold,
            )
            trainer = JointLoRAKVTrainer(model, data_manager, monitor, train_cfg, seed)
            stability_report = trainer.train()
            ckpt_path = os.path.join(self.checkpoint_dir, f"joint_seed{seed}.pt")
            trainer.save_checkpoint(ckpt_path)
        else:
            model = build_baseline_b3_model(self.config)
            trainer = BaselineB3Trainer(model, data_manager, train_cfg, seed)
            stability_report = trainer.train()
            ckpt_path = os.path.join(self.checkpoint_dir, f"b3_seed{seed}.pt")
            trainer.save_checkpoint(ckpt_path)

        # Evaluate on LongBench
        lb_eval = LongBenchEvaluator(model, data_manager, tokenizer,
                                     budget_ratio=self.config.locret.kv_budget_ratio)
        longbench_results = lb_eval.evaluate_all()

        # Evaluate on GLUE
        glue_eval = GLUEEvaluator(model, data_manager)
        glue_results = glue_eval.evaluate_all()

        return {
            "seed": seed,
            "model_type": model_type,
            "longbench_results": longbench_results,
            "glue_results": glue_results,
            "stability_report": stability_report,
        }

    def run_all(self) -> dict:
        """3 seeds × 2 models; aggregate results; check gate."""
        all_results = {"joint": [], "b3": []}
        seeds = self.config.training.seeds

        for seed in seeds:
            for model_type in ["joint", "b3"]:
                result = self.run_seed(seed, model_type)
                all_results[model_type].append(result)
                # Save per-seed result
                path = os.path.join(self.results_dir, f"{model_type}_seed{seed}.json")
                with open(path, "w") as f:
                    json.dump(result, f, indent=2)

        aggregated = self.aggregate_results(all_results)
        gate = self.check_gate(aggregated)
        aggregated["gate"] = gate

        self.save_results(aggregated, os.path.join(self.results_dir, "aggregated_results.json"))
        self.generate_figures(aggregated)
        return aggregated

    def aggregate_results(self, all_results: dict) -> dict:
        """Compute mean ± std across seeds per model type."""
        aggregated = {}
        for model_type in ["joint", "b3"]:
            results = all_results[model_type]
            lb_tasks = ["narrativeqa", "qasper", "multifieldqa_en", "mean_f1"]
            lb_agg = {}
            for task in lb_tasks:
                vals = [r["longbench_results"].get(task, 0.0) for r in results]
                lb_agg[task] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}

            nan_total = sum(r["stability_report"].get("nan_events", 0) for r in results)
            div_total = sum(r["stability_report"].get("divergence_events", 0) for r in results)

            # Collect loss histories and grad norms for figures
            loss_histories = {r["seed"]: r["stability_report"].get("loss_history", []) for r in results}
            lora_norms = {}
            locret_norms = {}
            for r in results:
                gh = r["stability_report"].get("grad_norm_history", [])
                lora_norms[r["seed"]] = [g["lora_norm"] for g in gh]
                locret_norms[r["seed"]] = [g["locret_norm"] for g in gh]

            aggregated[model_type] = {
                "longbench": lb_agg,
                "nan_events_total": nan_total,
                "divergence_events_total": div_total,
                "loss_histories": loss_histories,
                "lora_norms": lora_norms,
                "locret_norms": locret_norms,
                "per_seed": all_results[model_type],
            }
        return aggregated

    def check_gate(self, aggregated: dict) -> dict:
        """MUST_WORK gate: stability_passed AND accuracy_passed."""
        joint = aggregated.get("joint", {})
        b3 = aggregated.get("b3", {})

        stability_passed = (
            joint.get("nan_events_total", 1) == 0 and
            joint.get("divergence_events_total", 1) == 0
        )

        joint_mean_f1 = joint.get("longbench", {}).get("mean_f1", {}).get("mean", 0.0)
        b3_mean_f1 = b3.get("longbench", {}).get("mean_f1", {}).get("mean", 0.0)
        accuracy_passed = joint_mean_f1 >= b3_mean_f1

        gate_satisfied = stability_passed and accuracy_passed

        print(f"\n{'='*60}")
        print(f"MUST_WORK GATE EVALUATION")
        print(f"  Stability: {'PASS' if stability_passed else 'FAIL'} "
              f"(NaN={joint.get('nan_events_total',0)}, Div={joint.get('divergence_events_total',0)})")
        print(f"  Accuracy: {'PASS' if accuracy_passed else 'FAIL'} "
              f"(Joint F1={joint_mean_f1:.4f} vs B3 F1={b3_mean_f1:.4f})")
        print(f"  Gate: {'SATISFIED ✓' if gate_satisfied else 'FAILED ✗'}")
        print(f"{'='*60}")

        return {
            "stability_passed": stability_passed,
            "accuracy_passed": accuracy_passed,
            "gate_satisfied": gate_satisfied,
            "joint_mean_f1": joint_mean_f1,
            "b3_mean_f1": b3_mean_f1,
            "gate_type": "MUST_WORK",
        }

    def save_results(self, aggregated: dict, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Make serializable
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(i) for i in obj]
            elif isinstance(obj, (np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, (np.int32, np.int64)):
                return int(obj)
            return obj
        with open(path, "w") as f:
            json.dump(make_serializable(aggregated), f, indent=2)
        print(f"\n✓ Results saved: {path}")

    def generate_figures(self, aggregated: dict) -> None:
        figures_dir = self.figures_dir
        joint = aggregated.get("joint", {})
        b3 = aggregated.get("b3", {})

        joint_lb = {t: joint.get("longbench", {}).get(t, {}).get("mean", 0.0)
                    for t in ["narrativeqa", "qasper", "multifieldqa_en", "mean_f1"]}
        b3_lb = {t: b3.get("longbench", {}).get(t, {}).get("mean", 0.0)
                 for t in ["narrativeqa", "qasper", "multifieldqa_en", "mean_f1"]}

        print("\n[Figures] Generating visualizations...")
        plot_longbench_comparison(joint_lb, b3_lb,
                                  save_path=os.path.join(figures_dir, "longbench_comparison.png"))
        plot_per_task_f1(joint_lb, b3_lb,
                         save_path=os.path.join(figures_dir, "per_task_f1.png"))

        if joint.get("loss_histories"):
            plot_training_loss_curves(joint["loss_histories"],
                                      save_path=os.path.join(figures_dir, "training_loss_curves.png"))
            epoch_end = {s: [losses[-1]] if losses else [0.0]
                         for s, losses in joint["loss_histories"].items()}
            plot_loss_distribution(epoch_end,
                                   save_path=os.path.join(figures_dir, "loss_distribution.png"))

        if joint.get("lora_norms"):
            plot_gradient_norms(joint["lora_norms"], joint["locret_norms"],
                                save_path=os.path.join(figures_dir, "gradient_norms.png"))


def main() -> None:
    # GPU selection
    available_gpu = None
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().split("\n"):
            idx, mem = line.split(", ")
            if int(mem) < 1000:
                available_gpu = idx.strip()
                break
    except Exception:
        pass

    if available_gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = available_gpu
        print(f"✓ Using GPU {available_gpu}")
    else:
        print("⚠ No empty GPU found or GPU detection failed")

    # Load config
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hypothesis_dir = os.path.dirname(script_dir)
    cfg_path = os.path.join(script_dir, "experiment.yaml")

    if os.path.exists(cfg_path):
        config = load_config(cfg_path)
        print(f"✓ Config loaded from {cfg_path}")
    else:
        config = ExperimentConfig()
        config.paths.output_dir = hypothesis_dir + "/"
        config.paths.checkpoint_dir = os.path.join(hypothesis_dir, "checkpoints") + "/"
        config.paths.figures_dir = os.path.join(hypothesis_dir, "figures") + "/"
        config.paths.results_dir = os.path.join(hypothesis_dir, "results") + "/"
        print("✓ Using default config")

    runner = ExperimentRunner(config)
    aggregated = runner.run_all()

    gate = aggregated.get("gate", {})
    print(f"\nEXPERIMENT COMPLETE")
    print(f"Gate satisfied: {gate.get('gate_satisfied', False)}")
    print(f"Joint mean F1: {gate.get('joint_mean_f1', 0):.4f}")
    print(f"B3 mean F1: {gate.get('b3_mean_f1', 0):.4f}")


if __name__ == "__main__":
    main()
