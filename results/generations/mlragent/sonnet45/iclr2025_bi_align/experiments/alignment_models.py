"""
Alignment models: baselines and proposed method
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Optional, Tuple

class PreferenceEncoder(nn.Module):
    """Neural network that encodes preferences from interaction history"""

    def __init__(self, feature_dim: int, action_dim: int, hidden_dim: int,
                 num_contexts: int, temporal_modeling: bool = True):
        super().__init__()
        self.feature_dim = feature_dim
        self.action_dim = action_dim
        self.temporal_modeling = temporal_modeling

        input_dim = feature_dim + num_contexts + (1 if temporal_modeling else 0)

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        self.action_head = nn.Linear(hidden_dim, action_dim)

    def forward(self, state: torch.Tensor, context: torch.Tensor,
                timestep: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass
        Args:
            state: (batch_size, feature_dim)
            context: (batch_size,) integer context IDs
            timestep: (batch_size, 1) normalized timesteps
        Returns:
            action_logits: (batch_size, action_dim)
        """
        # One-hot encode context
        context_onehot = F.one_hot(context, num_classes=5).float()

        if self.temporal_modeling and timestep is not None:
            inputs = torch.cat([state, context_onehot, timestep], dim=1)
        else:
            inputs = torch.cat([state, context_onehot], dim=1)

        features = self.encoder(inputs)
        action_logits = self.action_head(features)
        return action_logits


class StaticAlignmentModel(nn.Module):
    """Baseline: Static RLHF without temporal modeling"""

    def __init__(self, feature_dim: int, action_dim: int, hidden_dim: int,
                 num_contexts: int):
        super().__init__()
        self.preference_encoder = PreferenceEncoder(
            feature_dim, action_dim, hidden_dim, num_contexts, temporal_modeling=False
        )

    def forward(self, state: torch.Tensor, context: torch.Tensor,
                timestep: Optional[torch.Tensor] = None) -> torch.Tensor:
        return self.preference_encoder(state, context, None)

    def compute_loss(self, states: torch.Tensor, contexts: torch.Tensor,
                    actions: torch.Tensor, timesteps: torch.Tensor,
                    temporal_lambda: float = 0.0) -> torch.Tensor:
        logits = self.forward(states, contexts)
        loss = F.cross_entropy(logits, actions)
        return loss


class CEVABasic(nn.Module):
    """Context-Evolving Value Alignment (Basic): Temporal modeling without bidirectional feedback"""

    def __init__(self, feature_dim: int, action_dim: int, hidden_dim: int,
                 num_contexts: int):
        super().__init__()
        self.preference_encoder = PreferenceEncoder(
            feature_dim, action_dim, hidden_dim, num_contexts, temporal_modeling=True
        )

    def forward(self, state: torch.Tensor, context: torch.Tensor,
                timestep: torch.Tensor) -> torch.Tensor:
        return self.preference_encoder(state, context, timestep)

    def compute_loss(self, states: torch.Tensor, contexts: torch.Tensor,
                    actions: torch.Tensor, timesteps: torch.Tensor,
                    temporal_lambda: float = 0.1) -> torch.Tensor:
        logits = self.forward(states, contexts, timesteps)
        ce_loss = F.cross_entropy(logits, actions)

        # Temporal smoothness regularization
        if timesteps.shape[0] > 1:
            # Sort by timestep
            sorted_indices = torch.argsort(timesteps.squeeze())
            sorted_logits = logits[sorted_indices]

            # Compute temporal smoothness
            temporal_diff = sorted_logits[1:] - sorted_logits[:-1]
            temporal_reg = torch.mean(torch.sum(temporal_diff ** 2, dim=1))

            loss = ce_loss + temporal_lambda * temporal_reg
        else:
            loss = ce_loss

        return loss


class CEVAFull(nn.Module):
    """CEVA Full: Temporal modeling with bidirectional feedback (no meta-learning)"""

    def __init__(self, feature_dim: int, action_dim: int, hidden_dim: int,
                 num_contexts: int):
        super().__init__()
        self.preference_encoder = PreferenceEncoder(
            feature_dim, action_dim, hidden_dim, num_contexts, temporal_modeling=True
        )

        # Explanation module (simplified)
        self.explanation_head = nn.Linear(hidden_dim, feature_dim)

    def forward(self, state: torch.Tensor, context: torch.Tensor,
                timestep: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        context_onehot = F.one_hot(context, num_classes=5).float()
        inputs = torch.cat([state, context_onehot, timestep], dim=1)
        features = self.preference_encoder.encoder(inputs)

        action_logits = self.preference_encoder.action_head(features)
        explanations = self.explanation_head(features)

        return action_logits, explanations

    def compute_loss(self, states: torch.Tensor, contexts: torch.Tensor,
                    actions: torch.Tensor, timesteps: torch.Tensor,
                    temporal_lambda: float = 0.1) -> torch.Tensor:
        logits, explanations = self.forward(states, contexts, timesteps)
        ce_loss = F.cross_entropy(logits, actions)

        # Temporal smoothness
        if timesteps.shape[0] > 1:
            sorted_indices = torch.argsort(timesteps.squeeze())
            sorted_logits = logits[sorted_indices]
            temporal_diff = sorted_logits[1:] - sorted_logits[:-1]
            temporal_reg = torch.mean(torch.sum(temporal_diff ** 2, dim=1))
            loss = ce_loss + temporal_lambda * temporal_reg
        else:
            loss = ce_loss

        # Explanation consistency (explanations should align with states)
        explanation_loss = F.mse_loss(explanations, states)
        loss = loss + 0.1 * explanation_loss

        return loss


class AdaptiveAlignment(nn.Module):
    """Proposed: Full adaptive alignment with meta-learning"""

    def __init__(self, feature_dim: int, action_dim: int, hidden_dim: int,
                 num_contexts: int):
        super().__init__()
        self.preference_encoder = PreferenceEncoder(
            feature_dim, action_dim, hidden_dim, num_contexts, temporal_modeling=True
        )

        # Explanation module
        self.explanation_head = nn.Linear(hidden_dim, feature_dim)

        # Meta-learning module for deferral decisions
        self.meta_policy = nn.Sequential(
            nn.Linear(hidden_dim + 1, hidden_dim // 2),  # +1 for consistency score
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 3)  # 3 decisions: execute, defer, reflect
        )

    def forward(self, state: torch.Tensor, context: torch.Tensor,
                timestep: torch.Tensor, return_meta: bool = False):
        context_onehot = F.one_hot(context, num_classes=5).float()
        inputs = torch.cat([state, context_onehot, timestep], dim=1)
        features = self.preference_encoder.encoder(inputs)

        action_logits = self.preference_encoder.action_head(features)
        explanations = self.explanation_head(features)

        if return_meta:
            # Compute consistency score (simplified)
            consistency_score = torch.sigmoid(torch.mean(features, dim=1, keepdim=True))
            meta_input = torch.cat([features, consistency_score], dim=1)
            meta_decision = self.meta_policy(meta_input)
            return action_logits, explanations, meta_decision

        return action_logits, explanations

    def compute_loss(self, states: torch.Tensor, contexts: torch.Tensor,
                    actions: torch.Tensor, timesteps: torch.Tensor,
                    temporal_lambda: float = 0.1) -> torch.Tensor:
        logits, explanations, meta_decisions = self.forward(
            states, contexts, timesteps, return_meta=True
        )

        # Action prediction loss
        ce_loss = F.cross_entropy(logits, actions)

        # Temporal smoothness
        if timesteps.shape[0] > 1:
            sorted_indices = torch.argsort(timesteps.squeeze())
            sorted_logits = logits[sorted_indices]
            temporal_diff = sorted_logits[1:] - sorted_logits[:-1]
            temporal_reg = torch.mean(torch.sum(temporal_diff ** 2, dim=1))
            loss = ce_loss + temporal_lambda * temporal_reg
        else:
            loss = ce_loss

        # Explanation consistency
        explanation_loss = F.mse_loss(explanations, states)

        # Meta-learning: encourage "execute" decision for consistent predictions
        action_probs = F.softmax(logits, dim=1)
        action_confidence = torch.max(action_probs, dim=1)[0]
        meta_target = torch.zeros_like(action_confidence).long()
        meta_target[action_confidence < 0.6] = 2  # "reflect" for low confidence
        meta_loss = F.cross_entropy(meta_decisions, meta_target)

        total_loss = loss + 0.1 * explanation_loss + 0.05 * meta_loss

        return total_loss


def create_model(model_type: str, feature_dim: int, action_dim: int,
                hidden_dim: int, num_contexts: int, device: torch.device) -> nn.Module:
    """Factory function to create alignment models"""
    if model_type == 'static_alignment':
        model = StaticAlignmentModel(feature_dim, action_dim, hidden_dim, num_contexts)
    elif model_type == 'ceva_basic':
        model = CEVABasic(feature_dim, action_dim, hidden_dim, num_contexts)
    elif model_type == 'ceva_full':
        model = CEVAFull(feature_dim, action_dim, hidden_dim, num_contexts)
    elif model_type == 'adaptive_alignment':
        model = AdaptiveAlignment(feature_dim, action_dim, hidden_dim, num_contexts)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    return model.to(device)
