"""
Gradient Alignment Analysis
Measure cosine similarity between DPO and Attribute gradients
"""

import torch
import torch.nn.functional as F
from typing import Dict, List
import random

class GradientAnalyzer:
    """Analyze gradient alignment during joint training."""

    def __init__(self, model, ref_policy, device: str = "cuda"):
        self.model = model
        self.ref_policy = ref_policy
        self.device = torch.device(device)
        self.model.to(self.device)
        self.ref_policy.to(self.device)
        self.model.train()  # Need gradients
        self.ref_policy.eval()

    def compute_alignment(self, batch: dict) -> float:
        """
        Compute gradient alignment for a single batch.

        Args:
            batch: Dictionary with input_ids, attention_mask, preference_label, attributes

        Returns:
            Cosine similarity between DPO and Attr gradients
        """
        # Move batch to device
        input_ids = batch['input_ids'].to(self.device)
        attention_mask = batch['attention_mask'].to(self.device)
        chosen_labels = batch['preference_label'].to(self.device)
        attr_labels = batch['attributes'].to(self.device)

        # Forward pass
        with torch.no_grad():
            ref_outputs = self.ref_policy.model(
                input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True
            )
            ref_logits = ref_outputs.hidden_states[-1]

        outputs = self.model(input_ids, attention_mask, chosen_labels, attr_labels, ref_logits)

        # Extract losses
        dpo_loss = outputs['loss_dpo']
        attr_loss = outputs['loss_attr']

        # Compute gradients separately
        self.model.zero_grad()
        dpo_loss.backward(retain_graph=True)
        grad_dpo = [p.grad.clone().flatten() for p in self.model.parameters() if p.grad is not None]

        self.model.zero_grad()
        attr_loss.backward()
        grad_attr = [p.grad.clone().flatten() for p in self.model.parameters() if p.grad is not None]

        # Flatten and compute cosine similarity
        grad_dpo_flat = torch.cat(grad_dpo)
        grad_attr_flat = torch.cat(grad_attr)

        cosine_sim = F.cosine_similarity(
            grad_dpo_flat.unsqueeze(0),
            grad_attr_flat.unsqueeze(0),
            dim=1
        ).item()

        return cosine_sim

    def analyze_dataset(
        self,
        dataloader,
        num_batches: int = 10
    ) -> Dict[str, float]:
        """
        Analyze gradient alignment over multiple batches.

        Args:
            dataloader: Data loader
            num_batches: Number of batches to sample

        Returns:
            Statistics dict with mean, std, min, max cosine similarities
        """
        cosine_sims = []

        # Sample random batches
        batches = list(dataloader)
        sampled_batches = random.sample(batches, min(num_batches, len(batches)))

        for batch in sampled_batches:
            cosine = self.compute_alignment(batch)
            cosine_sims.append(cosine)

        return {
            'mean_cosine': sum(cosine_sims) / len(cosine_sims),
            'std_cosine': torch.tensor(cosine_sims).std().item(),
            'min_cosine': min(cosine_sims),
            'max_cosine': max(cosine_sims),
            'cosine_sims': cosine_sims
        }
