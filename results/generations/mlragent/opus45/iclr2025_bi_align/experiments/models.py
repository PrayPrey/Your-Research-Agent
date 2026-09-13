"""
Implementation of the Mutual Calibration Framework (MCF) models.
Includes: Uncertainty-Aware AI Module, Personalized Deference Policy Learner,
and baseline models.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict, List, Optional
import numpy as np


class EnsembleMember(nn.Module):
    """Single ensemble member for uncertainty estimation."""

    def __init__(self, input_dim: int, hidden_dim: int, num_classes: int, dropout: float = 0.1):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class UncertaintyAwareAI(nn.Module):
    """
    Uncertainty-Aware AI Module using ensemble-based uncertainty estimation.
    Produces calibrated confidence estimates.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        num_classes: int,
        ensemble_size: int = 5,
        calibration_hidden_dim: int = 64,
        dropout: float = 0.1
    ):
        super().__init__()
        self.ensemble_size = ensemble_size
        self.num_classes = num_classes

        # Create ensemble members
        self.ensemble = nn.ModuleList([
            EnsembleMember(input_dim, hidden_dim, num_classes, dropout)
            for _ in range(ensemble_size)
        ])

        # Calibration network: takes [mean_pred, variance, max_prob] and outputs calibrated confidence
        self.calibration_net = nn.Sequential(
            nn.Linear(num_classes + 2, calibration_hidden_dim),
            nn.ReLU(),
            nn.Linear(calibration_hidden_dim, 1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass returning predictions, calibrated confidence, and raw logits.

        Returns:
            predictions: Softmax probabilities (batch, num_classes)
            confidence: Calibrated confidence score (batch, 1)
            ensemble_logits: Raw logits from ensemble (batch, ensemble_size, num_classes)
        """
        batch_size = x.size(0)

        # Get predictions from all ensemble members
        ensemble_logits = torch.stack([member(x) for member in self.ensemble], dim=1)
        ensemble_probs = F.softmax(ensemble_logits, dim=-1)

        # Compute mean prediction and variance
        mean_probs = ensemble_probs.mean(dim=1)  # (batch, num_classes)
        variance = ensemble_probs.var(dim=1).mean(dim=-1, keepdim=True)  # (batch, 1)
        max_prob = mean_probs.max(dim=-1, keepdim=True)[0]  # (batch, 1)

        # Calibration network input
        calib_input = torch.cat([mean_probs, variance, max_prob], dim=-1)
        confidence = self.calibration_net(calib_input)

        return mean_probs, confidence, ensemble_logits

    def get_prediction(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get predicted class and calibrated confidence."""
        probs, confidence, _ = self.forward(x)
        predicted_class = probs.argmax(dim=-1)
        return predicted_class, confidence.squeeze(-1)


class UserExpertiseProfile(nn.Module):
    """
    GRU-based user expertise profile that learns from interaction history.
    """

    def __init__(self, input_dim: int, profile_dim: int):
        super().__init__()
        self.profile_dim = profile_dim
        # Input: [task_features, human_decision, ai_decision, outcome]
        self.gru = nn.GRU(input_dim, profile_dim, batch_first=True)
        self.initial_profile = nn.Parameter(torch.zeros(1, profile_dim))

    def forward(
        self,
        interaction_history: torch.Tensor,
        initial_profile: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Update expertise profile based on interaction history.

        Args:
            interaction_history: (batch, seq_len, input_dim)
            initial_profile: (batch, profile_dim) or None

        Returns:
            Updated profile: (batch, profile_dim)
        """
        batch_size = interaction_history.size(0)
        if initial_profile is None:
            initial_profile = self.initial_profile.expand(1, batch_size, -1)
        else:
            initial_profile = initial_profile.unsqueeze(0)

        _, final_profile = self.gru(interaction_history, initial_profile)
        return final_profile.squeeze(0)

    def get_initial_profile(self, batch_size: int) -> torch.Tensor:
        """Get initial profile for new users."""
        return self.initial_profile.expand(batch_size, -1)


class DeferencePolicy(nn.Module):
    """
    Personalized Deference Policy Learner.
    Outputs deference score indicating when AI should defer to human judgment.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        user_profile_dim: int
    ):
        super().__init__()
        # Input: [task_features, ai_confidence, user_profile, task_context]
        total_input = input_dim + 1 + user_profile_dim
        self.policy_net = nn.Sequential(
            nn.Linear(total_input, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )

    def forward(
        self,
        task_features: torch.Tensor,
        ai_confidence: torch.Tensor,
        user_profile: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute deference score.

        Args:
            task_features: (batch, input_dim)
            ai_confidence: (batch, 1)
            user_profile: (batch, profile_dim)

        Returns:
            Deference score: (batch, 1) in [0, 1], higher = more deferring to human
        """
        combined = torch.cat([task_features, ai_confidence, user_profile], dim=-1)
        return self.policy_net(combined)


class MutualCalibrationFramework(nn.Module):
    """
    Full Mutual Calibration Framework (MCF).
    Integrates Uncertainty-Aware AI, User Expertise Profiling, and Deference Policy.
    """

    def __init__(
        self,
        input_dim: int,
        num_classes: int,
        config: Dict
    ):
        super().__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes

        # Uncertainty-Aware AI Module
        self.ai_module = UncertaintyAwareAI(
            input_dim=input_dim,
            hidden_dim=config["hidden_dim"],
            num_classes=num_classes,
            ensemble_size=config["ensemble_size"],
            calibration_hidden_dim=config["calibration_hidden_dim"],
            dropout=config["dropout"]
        )

        # User Expertise Profile
        # Interaction features: [task_embedding, human_correct, ai_correct, outcome]
        interaction_dim = input_dim + 3
        self.user_profile_module = UserExpertiseProfile(
            input_dim=interaction_dim,
            profile_dim=config["user_profile_dim"]
        )

        # Deference Policy
        self.deference_policy = DeferencePolicy(
            input_dim=input_dim,
            hidden_dim=config["deference_hidden_dim"],
            user_profile_dim=config["user_profile_dim"]
        )

        self.config = config

    def forward(
        self,
        x: torch.Tensor,
        user_profile: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Full forward pass.

        Args:
            x: Input features (batch, input_dim)
            user_profile: User expertise profile (batch, profile_dim) or None

        Returns:
            Dictionary with predictions, confidence, deference scores
        """
        batch_size = x.size(0)

        # Get AI predictions and confidence
        probs, confidence, ensemble_logits = self.ai_module(x)

        # Initialize user profile if not provided
        if user_profile is None:
            user_profile = self.user_profile_module.get_initial_profile(batch_size)
            user_profile = user_profile.to(x.device)

        # Compute deference score
        deference = self.deference_policy(x, confidence, user_profile)

        return {
            "predictions": probs,
            "confidence": confidence,
            "deference": deference,
            "user_profile": user_profile,
            "ensemble_logits": ensemble_logits
        }

    def get_recommendation(
        self,
        x: torch.Tensor,
        user_profile: Optional[torch.Tensor] = None,
        deference_threshold_high: float = 0.7,
        deference_threshold_low: float = 0.3
    ) -> Dict:
        """
        Get recommendation with explanation type based on deference level.
        """
        output = self.forward(x, user_profile)

        pred_class = output["predictions"].argmax(dim=-1)
        deference = output["deference"].squeeze(-1)

        # Determine recommendation type
        recommendation_types = []
        for d in deference:
            if d > deference_threshold_high:
                recommendation_types.append("defer_to_human")
            elif d < deference_threshold_low:
                recommendation_types.append("ai_confident")
            else:
                recommendation_types.append("collaborative")

        return {
            "predicted_class": pred_class,
            "confidence": output["confidence"].squeeze(-1),
            "deference": deference,
            "recommendation_type": recommendation_types
        }


class BaselineAI(nn.Module):
    """
    Standard AI baseline with simple confidence display (no calibration).
    """

    def __init__(self, input_dim: int, hidden_dim: int, num_classes: int, dropout: float = 0.1):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes)
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        logits = self.network(x)
        probs = F.softmax(logits, dim=-1)
        # Uncalibrated confidence: just max probability
        confidence = probs.max(dim=-1, keepdim=True)[0]
        return probs, confidence


class TransparencyPlusAI(nn.Module):
    """
    Transparency+ baseline: AI with detailed reasoning (feature importance).
    """

    def __init__(self, input_dim: int, hidden_dim: int, num_classes: int, dropout: float = 0.1):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        self.classifier = nn.Linear(hidden_dim, num_classes)

        # Feature importance estimator
        self.importance_net = nn.Sequential(
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        features = self.network(x)
        logits = self.classifier(features)
        probs = F.softmax(logits, dim=-1)
        confidence = probs.max(dim=-1, keepdim=True)[0]

        # Feature importance for "transparency"
        importance = self.importance_net(features)

        return probs, confidence, importance


class MCFStatic(nn.Module):
    """
    MCF-Static: Mutual Calibration Framework without personalization.
    Uses fixed deference policy without user profiling.
    """

    def __init__(
        self,
        input_dim: int,
        num_classes: int,
        config: Dict
    ):
        super().__init__()

        # Uncertainty-Aware AI Module
        self.ai_module = UncertaintyAwareAI(
            input_dim=input_dim,
            hidden_dim=config["hidden_dim"],
            num_classes=num_classes,
            ensemble_size=config["ensemble_size"],
            calibration_hidden_dim=config["calibration_hidden_dim"],
            dropout=config["dropout"]
        )

        # Static deference policy (no user profile)
        self.static_deference = nn.Sequential(
            nn.Linear(input_dim + 1, config["deference_hidden_dim"]),
            nn.ReLU(),
            nn.Linear(config["deference_hidden_dim"], 1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        probs, confidence, ensemble_logits = self.ai_module(x)

        # Static deference (no personalization)
        deference_input = torch.cat([x, confidence], dim=-1)
        deference = self.static_deference(deference_input)

        return {
            "predictions": probs,
            "confidence": confidence,
            "deference": deference,
            "ensemble_logits": ensemble_logits
        }
