"""H-M1 Rewards: Combined helpfulness + IFEval reward model."""
import torch
import torch.nn as nn
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from ifeval_signal import IFEvalRewardSignal


class HelpfulnessRewardModel(nn.Module):
    """Wrapper for pre-trained helpfulness reward model."""

    def __init__(self, model_id: str, device: str = "cuda"):
        super().__init__()
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_id, torch_dtype=torch.bfloat16
        ).to(device)
        self.model.eval()

    @torch.no_grad()
    def forward(self, prompts: list[str], responses: list[str]) -> torch.Tensor:
        """Score prompt-response pairs. Returns [B] tensor."""
        texts = [f"{p}\n\n{r}" for p, r in zip(prompts, responses)]

        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        outputs = self.model(**inputs)
        # DeBERTa RM outputs logits; take first column or sigmoid
        if outputs.logits.shape[-1] == 1:
            scores = outputs.logits.squeeze(-1)
        else:
            scores = outputs.logits[:, 0]

        return scores.float()


class CombinedRewardModel(nn.Module):
    """Combines helpfulness RM with H-E1 IFEvalRewardSignal."""

    def __init__(
        self,
        helpfulness_model_id: str,
        alpha: float = 0.5,
        beta: float = 0.5,
        ifeval_soft_margin: float = 0.1,
        device: str = "cuda"
    ):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.device = device

        self.helpfulness_rm = HelpfulnessRewardModel(helpfulness_model_id, device)
        self.ifeval_signal = IFEvalRewardSignal(soft_margin=ifeval_soft_margin)
        self.ifeval_signal.to(device)

        # For logging
        self.last_helpfulness = None
        self.last_ifeval = None

    def score_helpfulness(self, prompts: list[str], responses: list[str]) -> torch.Tensor:
        """RM forward pass. Returns [B] scalar rewards."""
        return self.helpfulness_rm(prompts, responses)

    def score_ifeval(self, responses: list[str], constraints: list[list[dict]]) -> torch.Tensor:
        """Loop IFEvalRewardSignal per-sample. Returns [B] tensor."""
        scores = []
        for resp, cons in zip(responses, constraints):
            if cons:  # has constraints
                score = self.ifeval_signal(resp, cons)
            else:  # no constraints (UltraFeedback sample)
                score = torch.tensor(0.5, dtype=torch.float32, device=self.device)
            scores.append(score)
        return torch.stack(scores).to(self.device)

    def compute_reward(
        self,
        prompts: list[str],
        responses: list[str],
        constraints: list[list[dict]]
    ) -> list[torch.Tensor]:
        """Compute combined rewards. Returns list of B scalar tensors (trl API)."""
        r_help = self.score_helpfulness(prompts, responses)
        r_ifeval = self.score_ifeval(responses, constraints)

        # Normalize helpfulness rewards to [0, 1] range roughly
        r_help_norm = torch.sigmoid(r_help)

        r_combined = self.alpha * r_help_norm + self.beta * r_ifeval

        # Store for logging
        self.last_helpfulness = r_help_norm.mean().item()
        self.last_ifeval = r_ifeval.mean().item()

        # Return as list of scalar tensors (trl PPO API)
        return list(r_combined.unbind(0))

    def set_weights(self, alpha: float, beta: float):
        """Update reward weights."""
        self.alpha = alpha
        self.beta = beta
