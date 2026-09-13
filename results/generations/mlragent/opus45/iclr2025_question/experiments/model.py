"""Semantic Entropy Decomposition model with probe networks."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from dataclasses import dataclass


@dataclass
class SEDOutput:
    """Output from SED model."""
    total_uncertainty: torch.Tensor
    epistemic_uncertainty: torch.Tensor
    aleatoric_uncertainty: torch.Tensor
    layer_uncertainties: Dict[int, torch.Tensor]


class AttentionPooling(nn.Module):
    """Attention-based pooling over sequence dimension."""

    def __init__(self, hidden_dim: int):
        super().__init__()
        self.attention = nn.Linear(hidden_dim, 1)

    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None):
        """
        Args:
            hidden_states: [batch, seq_len, hidden_dim]
            attention_mask: [batch, seq_len]
        Returns:
            pooled: [batch, hidden_dim]
        """
        scores = self.attention(hidden_states).squeeze(-1)  # [batch, seq_len]

        if attention_mask is not None:
            scores = scores.masked_fill(attention_mask == 0, float('-inf'))

        weights = F.softmax(scores, dim=-1)  # [batch, seq_len]
        pooled = torch.bmm(weights.unsqueeze(1), hidden_states).squeeze(1)  # [batch, hidden_dim]

        return pooled


class UncertaintyProbe(nn.Module):
    """Probe network for uncertainty estimation from a single layer."""

    def __init__(self, input_dim: int, hidden_dim: int = 256, dropout: float = 0.1):
        super().__init__()
        self.attention_pool = AttentionPooling(input_dim)
        self.probe = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )

    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None):
        """
        Args:
            hidden_states: [batch, seq_len, hidden_dim]
            attention_mask: [batch, seq_len]
        Returns:
            uncertainty: [batch, 1]
        """
        pooled = self.attention_pool(hidden_states, attention_mask)
        return self.probe(pooled)


class SEDModel(nn.Module):
    """Semantic Entropy Decomposition model."""

    def __init__(self, base_model, config):
        super().__init__()
        self.base_model = base_model
        self.config = config

        # Get model hidden size
        if hasattr(base_model.config, 'hidden_size'):
            hidden_size = base_model.config.hidden_size
        else:
            hidden_size = 896  # Default for Qwen2.5-0.5B

        # Create probe networks for each layer
        self.epistemic_probes = nn.ModuleDict()
        self.aleatoric_probes = nn.ModuleDict()

        for layer_idx in config.probe_layers:
            self.epistemic_probes[str(layer_idx)] = UncertaintyProbe(
                hidden_size, config.probe_hidden_dim, config.probe_dropout
            )
            self.aleatoric_probes[str(layer_idx)] = UncertaintyProbe(
                hidden_size, config.probe_hidden_dim, config.probe_dropout
            )

        # Layer aggregation weights (learnable)
        num_layers = len(config.probe_layers)
        self.epistemic_layer_weights = nn.Parameter(torch.ones(num_layers) / num_layers)
        self.aleatoric_layer_weights = nn.Parameter(torch.ones(num_layers) / num_layers)

        # Freeze base model
        for param in self.base_model.parameters():
            param.requires_grad = False

    def get_hidden_states(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> Dict[int, torch.Tensor]:
        """Extract hidden states from specified layers."""
        with torch.no_grad():
            outputs = self.base_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
                return_dict=True
            )

        hidden_states = {}
        for layer_idx in self.config.probe_layers:
            if layer_idx < len(outputs.hidden_states):
                hidden_states[layer_idx] = outputs.hidden_states[layer_idx]

        return hidden_states

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> SEDOutput:
        """
        Forward pass computing epistemic and aleatoric uncertainty.

        Args:
            input_ids: [batch, seq_len]
            attention_mask: [batch, seq_len]

        Returns:
            SEDOutput with uncertainty estimates
        """
        # Get hidden states from base model
        hidden_states = self.get_hidden_states(input_ids, attention_mask)

        # Compute uncertainty from each layer
        epistemic_outputs = []
        aleatoric_outputs = []
        layer_uncertainties = {}

        for i, layer_idx in enumerate(self.config.probe_layers):
            if layer_idx not in hidden_states:
                continue

            # Convert to float32 for probe computation
            h = hidden_states[layer_idx].float()
            ep = self.epistemic_probes[str(layer_idx)](h, attention_mask)
            al = self.aleatoric_probes[str(layer_idx)](h, attention_mask)

            epistemic_outputs.append(ep)
            aleatoric_outputs.append(al)
            layer_uncertainties[layer_idx] = {"epistemic": ep, "aleatoric": al}

        # Aggregate across layers with normalized weights
        if epistemic_outputs:
            ep_weights = F.softmax(self.epistemic_layer_weights[:len(epistemic_outputs)], dim=0)
            al_weights = F.softmax(self.aleatoric_layer_weights[:len(aleatoric_outputs)], dim=0)

            epistemic_stacked = torch.stack(epistemic_outputs, dim=0)  # [num_layers, batch, 1]
            aleatoric_stacked = torch.stack(aleatoric_outputs, dim=0)

            epistemic_uncertainty = (ep_weights.view(-1, 1, 1) * epistemic_stacked).sum(dim=0)
            aleatoric_uncertainty = (al_weights.view(-1, 1, 1) * aleatoric_stacked).sum(dim=0)
        else:
            batch_size = input_ids.size(0)
            epistemic_uncertainty = torch.zeros(batch_size, 1, device=input_ids.device)
            aleatoric_uncertainty = torch.zeros(batch_size, 1, device=input_ids.device)

        total_uncertainty = epistemic_uncertainty + aleatoric_uncertainty

        return SEDOutput(
            total_uncertainty=total_uncertainty,
            epistemic_uncertainty=epistemic_uncertainty,
            aleatoric_uncertainty=aleatoric_uncertainty,
            layer_uncertainties=layer_uncertainties
        )


class SEDLoss(nn.Module):
    """Loss function for SED training."""

    def __init__(self, lambda_contrast: float = 0.5, lambda_consist: float = 0.3, margin: float = 0.2):
        super().__init__()
        self.lambda_contrast = lambda_contrast
        self.lambda_consist = lambda_consist
        self.margin = margin
        self.mse = nn.MSELoss()

    def forward(
        self,
        sed_output: SEDOutput,
        semantic_entropy_target: torch.Tensor,
        uncertainty_types: List[str],
        hallucination_labels: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        Compute SED loss.

        Args:
            sed_output: Output from SED model
            semantic_entropy_target: Ground truth semantic entropy [batch, 1]
            uncertainty_types: List of uncertainty types ('epistemic', 'aleatoric', 'low')
            hallucination_labels: Binary hallucination labels [batch]

        Returns:
            Dictionary with loss components
        """
        ep = sed_output.epistemic_uncertainty
        al = sed_output.aleatoric_uncertainty
        total = sed_output.total_uncertainty

        # Reconstruction loss: total should approximate semantic entropy
        loss_recon = self.mse(total.squeeze(-1), semantic_entropy_target.squeeze(-1))

        # Contrastive loss
        loss_contrast = torch.tensor(0.0, device=ep.device)
        count_contrast = 0

        for i, utype in enumerate(uncertainty_types):
            if utype == "epistemic":
                # Epistemic should be higher than aleatoric
                loss_contrast = loss_contrast + F.relu(al[i].mean() - ep[i].mean() + self.margin)
                count_contrast += 1
            elif utype == "aleatoric":
                # Aleatoric should be higher than epistemic
                loss_contrast = loss_contrast + F.relu(ep[i].mean() - al[i].mean() + self.margin)
                count_contrast += 1

        if count_contrast > 0:
            loss_contrast = loss_contrast / count_contrast

        # Consistency loss: both should be low for low uncertainty samples
        loss_consist = torch.tensor(0.0, device=ep.device)
        count_consist = 0

        for i, utype in enumerate(uncertainty_types):
            if utype == "low":
                loss_consist = loss_consist + ep[i].pow(2).mean() + al[i].pow(2).mean()
                count_consist += 1

        if count_consist > 0:
            loss_consist = loss_consist / count_consist

        # Total loss
        total_loss = loss_recon + self.lambda_contrast * loss_contrast + self.lambda_consist * loss_consist

        return {
            "total": total_loss,
            "reconstruction": loss_recon,
            "contrastive": loss_contrast,
            "consistency": loss_consist
        }


def load_model_and_tokenizer(model_name: str, device: str = "cuda"):
    """Load base model and tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map=device,
        trust_remote_code=True
    )
    model.eval()

    return model, tokenizer
