"""
Joint DPO + Attribute Trainer
Implements training loop with gradient monitoring
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from tqdm import tqdm
import json
import os


class GradientMonitor:
    """Monitor gradient angles between DPO and Attribute losses"""

    def __init__(self):
        self.angles = []

    def compute_gradient_angle(self, loss_dpo, loss_attr, model):
        """
        Compute angle between ∇L_DPO and ∇L_attr
        Returns angle in degrees
        """
        # Zero gradients
        model.zero_grad()

        # Compute gradients for DPO
        loss_dpo.backward(retain_graph=True)
        grad_dpo = {}
        for name, param in model.named_parameters():
            if param.grad is not None:
                grad_dpo[name] = param.grad.clone().flatten()

        # Zero gradients
        model.zero_grad()

        # Compute gradients for Attr
        loss_attr.backward(retain_graph=True)
        grad_attr = {}
        for name, param in model.named_parameters():
            if param.grad is not None:
                grad_attr[name] = param.grad.clone().flatten()

        # Only use shared parameters (model parameters, not attr_head)
        shared_params = [name for name in grad_dpo.keys() if name in grad_attr and name.startswith('model.')]

        if not shared_params:
            # No shared params, return neutral angle
            return 90.0

        # Concatenate shared gradients
        grad_dpo_vec = torch.cat([grad_dpo[name] for name in shared_params])
        grad_attr_vec = torch.cat([grad_attr[name] for name in shared_params])

        # Compute cosine similarity
        cos_sim = torch.dot(grad_dpo_vec, grad_attr_vec) / (
            torch.norm(grad_dpo_vec) * torch.norm(grad_attr_vec) + 1e-8
        )

        # Convert to angle (degrees)
        angle = torch.acos(torch.clamp(cos_sim, -1.0, 1.0)) * 180 / np.pi

        self.angles.append(angle.item())

        return angle.item()

    def get_statistics(self):
        """Return gradient angle statistics"""
        if not self.angles:
            return {}

        return {
            "mean": np.mean(self.angles),
            "std": np.std(self.angles),
            "min": np.min(self.angles),
            "max": np.max(self.angles),
            "catastrophic_interference": np.mean([a > 120 for a in self.angles])
        }


class JointTrainer:
    """Trainer for joint DPO + Attribute model"""

    def __init__(self, model, ref_policy, train_loader, test_loader,
                 lr=1e-5, device="cuda", checkpoint_dir="checkpoints"):
        self.model = model.to(device)
        self.ref_policy = ref_policy.to(device)
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.device = device
        self.checkpoint_dir = checkpoint_dir

        # Optimizer
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=lr,
            betas=(0.9, 0.999),
            weight_decay=0.01,
            eps=1e-8
        )

        # Gradient monitor
        self.gradient_monitor = GradientMonitor()

        # Training history
        self.history = {
            "loss_total": [],
            "loss_dpo": [],
            "loss_attr": [],
            "gradient_angles": []
        }

        os.makedirs(checkpoint_dir, exist_ok=True)

    def train_step(self, batch):
        """Single training step"""
        self.model.train()

        # Move batch to device
        chosen_ids = batch["chosen_ids"].to(self.device)
        rejected_ids = batch["rejected_ids"].to(self.device)
        target_attrs = batch["attributes"].to(self.device)

        # Get reference logits
        with torch.no_grad():
            ref_chosen_logits = self.ref_policy(chosen_ids)
            ref_rejected_logits = self.ref_policy(rejected_ids)

        # Forward pass
        loss_total, loss_dpo, loss_attr = self.model(
            chosen_ids, rejected_ids,
            ref_chosen_logits, ref_rejected_logits,
            target_attrs
        )

        # Compute gradient angle (every 100 steps to save time)
        if len(self.history["loss_total"]) % 100 == 0:
            angle = self.gradient_monitor.compute_gradient_angle(
                loss_dpo, loss_attr, self.model
            )
            self.history["gradient_angles"].append(angle)
        else:
            # Zero gradients for actual update
            self.optimizer.zero_grad()

        # Backward pass
        loss_total.backward()
        self.optimizer.step()

        return {
            "loss_total": loss_total.item(),
            "loss_dpo": loss_dpo.item(),
            "loss_attr": loss_attr.item()
        }

    def train(self, num_steps=15000, log_interval=100, checkpoint_interval=1000):
        """Training loop"""
        print(f"Starting training for {num_steps} steps...")

        step = 0
        epoch = 0

        while step < num_steps:
            epoch += 1
            pbar = tqdm(self.train_loader, desc=f"Epoch {epoch}")

            for batch in pbar:
                if step >= num_steps:
                    break

                # Train step
                metrics = self.train_step(batch)

                # Log
                self.history["loss_total"].append(metrics["loss_total"])
                self.history["loss_dpo"].append(metrics["loss_dpo"])
                self.history["loss_attr"].append(metrics["loss_attr"])

                if step % log_interval == 0:
                    pbar.set_postfix({
                        "loss": f"{metrics['loss_total']:.4f}",
                        "dpo": f"{metrics['loss_dpo']:.4f}",
                        "attr": f"{metrics['loss_attr']:.4f}"
                    })

                # Checkpoint
                if step % checkpoint_interval == 0 and step > 0:
                    self.save_checkpoint(step)

                step += 1

        # Final checkpoint
        self.save_checkpoint(step)

        # Print gradient statistics
        grad_stats = self.gradient_monitor.get_statistics()
        print("\nGradient Angle Statistics:")
        print(f"  Mean: {grad_stats.get('mean', 0):.2f}°")
        print(f"  Std: {grad_stats.get('std', 0):.2f}°")
        print(f"  Catastrophic interference rate: {grad_stats.get('catastrophic_interference', 0):.2%}")

        return self.history

    def save_checkpoint(self, step):
        """Save model checkpoint"""
        checkpoint_path = os.path.join(self.checkpoint_dir, f"checkpoint_{step}.pt")

        torch.save({
            "step": step,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "history": self.history,
            "gradient_stats": self.gradient_monitor.get_statistics()
        }, checkpoint_path)

        print(f"Checkpoint saved: {checkpoint_path}")

    def save_results(self, output_path="results.json"):
        """Save training results"""
        results = {
            "history": self.history,
            "gradient_stats": self.gradient_monitor.get_statistics(),
            "final_loss": {
                "total": self.history["loss_total"][-1] if self.history["loss_total"] else None,
                "dpo": self.history["loss_dpo"][-1] if self.history["loss_dpo"] else None,
                "attr": self.history["loss_attr"][-1] if self.history["loss_attr"] else None
            }
        }

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Results saved: {output_path}")


if __name__ == "__main__":
    # Test trainer
    from models.model import JointDPOAttribute, ReferencePolicy
    from torch.utils.data import DataLoader, TensorDataset

    print("Testing trainer...")

    # Create dummy data
    batch_size = 2
    seq_len = 512
    vocab_size = 50257

    dummy_chosen = torch.randint(0, vocab_size, (10, seq_len))
    dummy_rejected = torch.randint(0, vocab_size, (10, seq_len))
    dummy_attrs = torch.randint(1, 6, (10, 3))

    dataset = TensorDataset(dummy_chosen, dummy_rejected, dummy_attrs)
    loader = DataLoader(dataset, batch_size=batch_size)

    # Create models
    model = JointDPOAttribute()
    ref_policy = ReferencePolicy()

    # Create trainer
    trainer = JointTrainer(model, ref_policy, loader, loader, device="cpu")

    # Train for 5 steps
    trainer.train(num_steps=5, log_interval=1, checkpoint_interval=3)

    print("✓ Trainer test complete")
