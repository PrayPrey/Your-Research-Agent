"""
Multi-Task Training Orchestration
Based on: 03_architecture.md - Module 3: TrainingModule
Based on: 03_logic.md - A-2: Multi-Task Training Pipeline
"""

import os
import json
import torch
from typing import Dict, List
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data.loader import MultiDomainDataset
from models.lora_adapter import MultiRankLoRAFactory, LoRATrainer


class MultiTaskOrchestrator:
    """Orchestrate training across 17 tasks × 4 ranks = 68 configurations."""

    def __init__(self,
                 tasks: List[str],
                 ranks: List[int] = [4, 8, 16, 32],
                 output_dir: str = "./outputs",
                 base_model: str = "meta-llama/Llama-2-7b-hf",
                 epochs_config: Dict[str, int] = None,
                 batch_size: int = 16,
                 learning_rate: float = 3e-4,
                 device: str = "cuda"):
        """
        Initialize multi-task orchestrator.

        Args:
            tasks: List of task names
            ranks: LoRA ranks to train
            output_dir: Directory for outputs
            base_model: Base model identifier
            epochs_config: Task-specific epoch counts
            batch_size: Batch size
            learning_rate: Learning rate
            device: Device to train on
        """
        self.tasks = tasks
        self.ranks = ranks
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.base_model = base_model
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = device

        # Task-specific epoch configuration
        if epochs_config is None:
            # Default: 5 epochs for small tasks, 3 for large
            self.epochs_config = {}
            small_tasks = ["cola", "mrpc", "rte", "wnli", "stsb"]
            for task in tasks:
                self.epochs_config[task] = 5 if any(t in task for t in small_tasks) else 3
        else:
            self.epochs_config = epochs_config

        # Initialize data loader
        self.data_module = MultiDomainDataset(
            tokenizer_name=base_model,
            max_length=512,
            batch_size=batch_size
        )

        # Initialize model factory
        self.model_factory = MultiRankLoRAFactory(
            base_model_name=base_model,
            ranks=ranks
        )

        # Results storage
        self.results = {}

    def train_all_configurations(self) -> Dict:
        """
        Train all 68 configurations (17 tasks × 4 ranks).

        Returns:
            Dictionary with all results
        """
        print("=" * 80)
        print("MULTI-TASK ORCHESTRATOR")
        print("=" * 80)
        print(f"Tasks: {len(self.tasks)}")
        print(f"Ranks: {self.ranks}")
        print(f"Total configurations: {len(self.tasks) * len(self.ranks)}")
        print("=" * 80)

        # Load all task data
        print("\nLoading datasets...")
        all_loaders = self.data_module.get_all_tasks()

        # Train each configuration
        config_count = 0
        for task_name in self.tasks:
            if task_name not in all_loaders:
                print(f"\n✗ Task '{task_name}' not loaded, skipping...")
                continue

            self.results[task_name] = {}
            train_loader, val_loader = all_loaders[task_name]

            for rank in self.ranks:
                config_count += 1
                print(f"\n{'='*80}")
                print(f"Configuration {config_count}/{len(self.tasks) * len(self.ranks)}")
                print(f"Task: {task_name}, Rank: {rank}")
                print(f"{'='*80}")

                # Train this configuration
                result = self.train_single_task_rank(
                    task_name=task_name,
                    rank=rank,
                    train_loader=train_loader,
                    val_loader=val_loader
                )

                self.results[task_name][rank] = result

                # Save intermediate results
                self._save_results()

        print(f"\n{'='*80}")
        print("✓ ALL CONFIGURATIONS COMPLETE")
        print(f"{'='*80}")

        return self.results

    def train_single_task_rank(self,
                               task_name: str,
                               rank: int,
                               train_loader,
                               val_loader) -> Dict:
        """
        Train single (task, rank) combination.

        Args:
            task_name: Name of the task
            rank: LoRA rank
            train_loader: Training data loader
            val_loader: Validation data loader

        Returns:
            Dictionary with training results
        """
        # Determine number of labels
        num_labels = self._get_num_labels(task_name)
        epochs = self.epochs_config.get(task_name, 3)

        print(f"\nCreating model: rank={rank}, labels={num_labels}")

        # Create model with adapter
        model = self.model_factory.create_adapter(
            rank=rank,
            num_labels=num_labels,
            device=self.device
        )

        # Create trainer
        trainer = LoRATrainer(
            model=model,
            optimizer_config={
                "lr": self.learning_rate,
                "betas": (0.9, 0.999),
                "weight_decay": 0.01
            },
            scheduler_config={
                "T_max": epochs * len(train_loader),
                "eta_min": 1e-6
            }
        )

        # Training loop
        best_accuracy = 0
        best_epoch = 0

        for epoch in range(epochs):
            print(f"\nEpoch {epoch + 1}/{epochs}")

            # Train
            metrics = trainer.train_epoch(train_loader, val_loader)

            print(f"  Train Loss: {metrics['train_loss']:.4f}, "
                  f"Train Acc: {metrics['train_accuracy']:.4f}")
            print(f"  Val Loss: {metrics['val_loss']:.4f}, "
                  f"Val Acc: {metrics['val_accuracy']:.4f}")

            # Track best model
            if metrics['val_accuracy'] > best_accuracy:
                best_accuracy = metrics['val_accuracy']
                best_epoch = epoch

                # Save checkpoint
                checkpoint_dir = self.output_dir / "checkpoints" / f"{task_name}_rank{rank}"
                checkpoint_dir.mkdir(parents=True, exist_ok=True)
                trainer.save_adapter(str(checkpoint_dir))

        # Compute efficiency metrics
        param_count = self.model_factory.count_parameters(model)
        flops = self.model_factory.count_flops(model, input_shape=(1, 512))

        result = {
            "task": task_name,
            "rank": rank,
            "accuracy": best_accuracy,
            "best_epoch": best_epoch,
            "params": param_count,
            "flops": flops
        }

        print(f"\n✓ Results: acc={best_accuracy:.4f}, params={param_count:,}, flops={flops:,}")

        return result

    def _get_num_labels(self, task_name: str) -> int:
        """Get number of labels for a task."""
        if task_name == "stsb":
            return 1  # Regression
        elif task_name == "mnli" or "xnli" in task_name:
            return 3  # 3-way classification
        else:
            return 2  # Binary classification

    def _save_results(self):
        """Save results to JSON file."""
        results_file = self.output_dir / "results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Results saved to {results_file}")

    def save_results(self, results: Dict, output_path: str):
        """
        Save final results to file.

        Args:
            results: Results dictionary
            output_path: Path to save results
        """
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Final results saved to {output_path}")
