"""
Human behavior simulator for evaluating human-AI collaboration.
Simulates human decision-making with varying expertise levels and
behavioral patterns (automation bias, algorithm aversion).
"""

import torch
import numpy as np
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class SimulatedUser:
    """Represents a simulated user with specific characteristics."""
    user_id: int
    expertise_level: str  # "novice", "intermediate", "expert"
    base_accuracy: float  # Inherent accuracy on task
    automation_bias: float  # Tendency to over-rely on AI (0-1)
    algorithm_aversion: float  # Tendency to reject AI recommendations (0-1)
    learning_rate: float  # How quickly they calibrate trust


class HumanBehaviorSimulator:
    """
    Simulates human decision-making in human-AI collaboration scenarios.
    Models automation bias, algorithm aversion, and expertise-dependent behavior.
    """

    def __init__(
        self,
        num_classes: int,
        expertise_params: Dict[str, Dict] = None,
        seed: int = 42
    ):
        self.num_classes = num_classes
        self.rng = np.random.RandomState(seed)

        # Default expertise parameters
        if expertise_params is None:
            self.expertise_params = {
                "novice": {
                    "base_accuracy": 0.55,
                    "automation_bias": 0.7,
                    "algorithm_aversion": 0.1,
                    "learning_rate": 0.1
                },
                "intermediate": {
                    "base_accuracy": 0.70,
                    "automation_bias": 0.4,
                    "algorithm_aversion": 0.3,
                    "learning_rate": 0.15
                },
                "expert": {
                    "base_accuracy": 0.85,
                    "automation_bias": 0.2,
                    "algorithm_aversion": 0.4,
                    "learning_rate": 0.2
                }
            }
        else:
            self.expertise_params = expertise_params

    def create_user(self, user_id: int, expertise_level: str) -> SimulatedUser:
        """Create a simulated user with specified expertise level."""
        params = self.expertise_params[expertise_level]

        # Add some noise to make users individual
        noise_scale = 0.1
        return SimulatedUser(
            user_id=user_id,
            expertise_level=expertise_level,
            base_accuracy=np.clip(
                params["base_accuracy"] + self.rng.normal(0, noise_scale), 0.3, 0.95
            ),
            automation_bias=np.clip(
                params["automation_bias"] + self.rng.normal(0, noise_scale), 0, 1
            ),
            algorithm_aversion=np.clip(
                params["algorithm_aversion"] + self.rng.normal(0, noise_scale), 0, 1
            ),
            learning_rate=params["learning_rate"]
        )

    def simulate_human_only_decision(
        self,
        user: SimulatedUser,
        true_labels: torch.Tensor,
        task_difficulty: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Simulate human decision without AI assistance.

        Args:
            user: Simulated user
            true_labels: Ground truth labels
            task_difficulty: Optional difficulty scores (0-1, higher = harder)

        Returns:
            Human decisions
        """
        batch_size = true_labels.size(0)
        decisions = torch.zeros_like(true_labels)

        for i in range(batch_size):
            # Adjust accuracy by task difficulty
            effective_accuracy = user.base_accuracy
            if task_difficulty is not None:
                # Harder tasks reduce accuracy
                effective_accuracy *= (1 - 0.3 * task_difficulty[i].item())

            if self.rng.random() < effective_accuracy:
                # Correct decision
                decisions[i] = true_labels[i]
            else:
                # Random wrong decision
                wrong_choices = [c for c in range(self.num_classes) if c != true_labels[i].item()]
                decisions[i] = self.rng.choice(wrong_choices)

        return decisions

    def simulate_collaborative_decision(
        self,
        user: SimulatedUser,
        true_labels: torch.Tensor,
        ai_predictions: torch.Tensor,
        ai_confidence: torch.Tensor,
        deference_signal: Optional[torch.Tensor] = None,
        recommendation_type: Optional[List[str]] = None,
        task_difficulty: Optional[torch.Tensor] = None,
        trust_state: Optional[Dict] = None
    ) -> Tuple[torch.Tensor, Dict]:
        """
        Simulate human decision with AI assistance.

        Args:
            user: Simulated user
            true_labels: Ground truth labels
            ai_predictions: AI predicted classes
            ai_confidence: AI confidence scores
            deference_signal: AI's deference recommendations (MCF models)
            recommendation_type: Type of AI recommendation (MCF models)
            task_difficulty: Optional difficulty scores
            trust_state: Current trust state for dynamic updates

        Returns:
            Tuple of (human decisions, metrics dict)
        """
        batch_size = true_labels.size(0)
        decisions = torch.zeros_like(true_labels)

        # Track metrics
        reliance_decisions = []  # 1 = relied on AI, 0 = used own judgment
        appropriate_reliance = []

        # Initialize trust state if not provided
        if trust_state is None:
            trust_state = {"trust_level": 0.5}

        for i in range(batch_size):
            # Get human's own decision capability
            effective_accuracy = user.base_accuracy
            if task_difficulty is not None:
                effective_accuracy *= (1 - 0.3 * task_difficulty[i].item())

            human_likely_correct = self.rng.random() < effective_accuracy
            ai_correct = (ai_predictions[i] == true_labels[i]).item()
            conf = ai_confidence[i].item()

            # Compute reliance probability based on multiple factors
            base_reliance_prob = 0.5

            # Factor 1: AI confidence affects reliance
            confidence_factor = conf * 0.3

            # Factor 2: Automation bias increases reliance
            bias_factor = user.automation_bias * 0.3

            # Factor 3: Algorithm aversion decreases reliance
            aversion_factor = -user.algorithm_aversion * 0.3

            # Factor 4: Current trust state
            trust_factor = (trust_state["trust_level"] - 0.5) * 0.2

            # Factor 5: Deference signal from AI (if MCF model)
            deference_factor = 0
            if deference_signal is not None:
                # High deference = AI suggesting human should decide
                deference_factor = -(deference_signal[i].item() - 0.5) * 0.4

            # Factor 6: Recommendation type affects reliance (MCF models)
            rec_factor = 0
            if recommendation_type is not None:
                rec = recommendation_type[i]
                if rec == "ai_confident":
                    rec_factor = 0.2
                elif rec == "defer_to_human":
                    rec_factor = -0.3
                # "collaborative" has no additional effect

            reliance_prob = np.clip(
                base_reliance_prob + confidence_factor + bias_factor +
                aversion_factor + trust_factor + deference_factor + rec_factor,
                0.05, 0.95
            )

            # Make decision
            rely_on_ai = self.rng.random() < reliance_prob
            reliance_decisions.append(1 if rely_on_ai else 0)

            if rely_on_ai:
                decisions[i] = ai_predictions[i]
            else:
                # Use own judgment
                if human_likely_correct:
                    decisions[i] = true_labels[i]
                else:
                    # Make a mistake
                    wrong_choices = [c for c in range(self.num_classes) if c != true_labels[i].item()]
                    decisions[i] = self.rng.choice(wrong_choices)

            # Track appropriateness of reliance
            final_correct = (decisions[i] == true_labels[i]).item()
            if rely_on_ai:
                # Appropriate if AI was correct
                appropriate_reliance.append(1 if ai_correct else 0)
            else:
                # Appropriate if human was correct
                appropriate_reliance.append(1 if final_correct else 0)

            # Update trust state based on observed AI performance
            trust_update = user.learning_rate * (1 if ai_correct else -1) * 0.1
            trust_state["trust_level"] = np.clip(
                trust_state["trust_level"] + trust_update, 0, 1
            )

        metrics = {
            "reliance_rate": np.mean(reliance_decisions),
            "appropriate_reliance_rate": np.mean(appropriate_reliance),
            "final_accuracy": (decisions == true_labels).float().mean().item(),
            "trust_level": trust_state["trust_level"]
        }

        return decisions, metrics

    def compute_calibration_metrics(
        self,
        true_labels: torch.Tensor,
        ai_predictions: torch.Tensor,
        ai_confidence: torch.Tensor,
        human_decisions: torch.Tensor
    ) -> Dict:
        """
        Compute detailed calibration metrics.
        """
        ai_correct = (ai_predictions == true_labels).float()
        human_correct = (human_decisions == true_labels).float()
        human_followed_ai = (human_decisions == ai_predictions).float()

        # Over-reliance: accepted wrong AI recommendation
        over_reliance_mask = (human_followed_ai == 1) & (ai_correct == 0)
        over_reliance_rate = over_reliance_mask.float().mean().item()

        # Under-reliance: rejected correct AI recommendation
        under_reliance_mask = (human_followed_ai == 0) & (ai_correct == 1) & (human_correct == 0)
        under_reliance_rate = under_reliance_mask.float().mean().item()

        # Correct override: rejected wrong AI, made correct decision
        correct_override_mask = (human_followed_ai == 0) & (ai_correct == 0) & (human_correct == 1)
        correct_override_rate = correct_override_mask.float().mean().item()

        # Appropriate Reliance Rate (ARR)
        correct_agreement = ((human_followed_ai == 1) & (ai_correct == 1)).float()
        arr = (correct_agreement.sum() + correct_override_mask.float().sum()) / len(true_labels)

        return {
            "over_reliance_rate": over_reliance_rate,
            "under_reliance_rate": under_reliance_rate,
            "correct_override_rate": correct_override_rate,
            "appropriate_reliance_rate": arr.item(),
            "ai_accuracy": ai_correct.mean().item(),
            "human_accuracy": human_correct.mean().item()
        }
