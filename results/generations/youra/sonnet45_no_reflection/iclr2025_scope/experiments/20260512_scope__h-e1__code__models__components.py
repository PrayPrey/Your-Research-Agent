"""
Model components for LoRA-MoE coordination.
Contains LoRAExpert, LoRARouter, and CoordinationModule.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional
from config import ModelConfig


class LoRAExpert(nn.Module):
    """Single LoRA expert with low-rank decomposition."""

    def __init__(self, hidden_dim: int, rank: int, alpha: int, dropout: float = 0.05):
        """
        Initialize LoRA expert.

        Args:
            hidden_dim: Model hidden size
            rank: LoRA rank for low-rank decomposition
            alpha: LoRA alpha scaling factor
            dropout: Dropout probability
        """
        super().__init__()
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank

        # Low-rank matrices
        self.lora_A = nn.Linear(hidden_dim, rank, bias=False)  # Down-projection
        self.lora_B = nn.Linear(rank, hidden_dim, bias=False)  # Up-projection
        self.dropout = nn.Dropout(dropout)

        # Initialize weights
        nn.init.kaiming_uniform_(self.lora_A.weight, a=torch.nn.init.calculate_gain('linear'))
        nn.init.zeros_(self.lora_B.weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through LoRA expert.

        Args:
            x: Input tensor [B, N, D]

        Returns:
            Output tensor [B, N, D]
        """
        # Apply dropout to input
        x_dropped = self.dropout(x)

        # Low-rank transformation: x -> A -> B with scaling
        down = self.lora_A(x_dropped)  # [B, N, R]
        up = self.lora_B(down)  # [B, N, D]

        return up * self.scaling


class LoRARouter(nn.Module):
    """Top-K router for LoRA experts."""

    def __init__(self, hidden_dim: int, num_experts: int, top_k: int = 2):
        """
        Initialize router.

        Args:
            hidden_dim: Input dimension
            num_experts: Number of experts (8)
            top_k: Number of experts to select (2)
        """
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        self.gate = nn.Linear(hidden_dim, num_experts)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through router.

        Args:
            x: Input tensor [B, N, D]

        Returns:
            expert_indices: Top-k expert indices [B, top_k]
            expert_probs: Top-k expert probabilities [B, top_k]
        """
        # Compute gating logits using mean-pooled representation
        pooled = x.mean(dim=1)  # [B, D]
        logits = self.gate(pooled)  # [B, num_experts]

        # Get top-k experts
        top_k_logits, top_k_indices = torch.topk(logits, self.top_k, dim=-1)  # [B, top_k]

        # Apply softmax to top-k logits
        top_k_probs = F.softmax(top_k_logits, dim=-1)  # [B, top_k]

        return top_k_indices, top_k_probs


class CoordinationModule(nn.Module):
    """LoRA-MoE coordination with performance-weighted alignment."""

    def __init__(self, config: ModelConfig):
        """
        Initialize coordination module.

        Args:
            config: ModelConfig with LoRA and MoE parameters
        """
        super().__init__()
        self.config = config
        self.hidden_dim = 4096  # Mixtral hidden dim

        # LoRA experts
        self.experts = nn.ModuleList([
            LoRAExpert(
                self.hidden_dim,
                config.lora_rank,
                config.lora_alpha,
                config.lora_dropout
            )
            for _ in range(config.num_lora_experts)
        ])

        # Router
        self.router = LoRARouter(self.hidden_dim, config.num_lora_experts, config.top_k)

    def forward(
        self,
        hidden_states: torch.Tensor,
        moe_expert_probs: torch.Tensor,
        task_weights: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass with coordination.

        Args:
            hidden_states: Input hidden states [B, N, D]
            moe_expert_probs: MoE routing probabilities [B, num_moe_experts]
            task_weights: Performance weights per task [B] (optional)

        Returns:
            output: Coordinated output [B, N, D]
            aux_loss: Auxiliary load balancing loss (scalar)
        """
        batch_size, seq_len, hidden_dim = hidden_states.shape

        # Route to top-k experts
        expert_indices, expert_probs = self.router(hidden_states)  # [B, top_k], [B, top_k]

        # Compute expert outputs and mix
        output = torch.zeros_like(hidden_states)

        for i in range(self.config.top_k):
            # Get expert indices for this position
            expert_idx = expert_indices[:, i]  # [B]

            # Compute outputs for all experts (vectorized)
            for expert_id in range(self.config.num_lora_experts):
                # Mask for samples that selected this expert
                mask = (expert_idx == expert_id).float()  # [B]

                if mask.sum() > 0:
                    # Get expert output
                    expert_output = self.experts[expert_id](hidden_states)  # [B, N, D]

                    # Weight by routing probability and mask
                    weight = expert_probs[:, i] * mask  # [B]
                    output += expert_output * weight.unsqueeze(1).unsqueeze(2)  # [B, N, D]

        # Compute auxiliary load balancing loss
        aux_loss = self._compute_load_balance_loss(expert_probs)

        return output, aux_loss

    def _compute_load_balance_loss(self, expert_probs: torch.Tensor) -> torch.Tensor:
        """
        Compute load balancing auxiliary loss.

        Args:
            expert_probs: Expert probabilities [B, top_k]

        Returns:
            Load balance loss (scalar)
        """
        # Encourage uniform expert utilization
        # Use variance of expert usage as penalty
        mean_prob = expert_probs.mean(dim=0)  # [top_k]
        variance = ((expert_probs - mean_prob) ** 2).mean()
        return variance

    def compute_alignment_loss(
        self,
        lora_probs: torch.Tensor,
        moe_probs: torch.Tensor,
        task_weights: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Compute performance-weighted alignment loss.

        Args:
            lora_probs: LoRA routing distribution [B, num_lora_experts]
            moe_probs: MoE routing distribution [B, num_moe_experts]
            task_weights: Performance weights [B] (higher = harder task)

        Returns:
            Weighted KL divergence loss (scalar)
        """
        batch_size = lora_probs.shape[0]

        # Ensure both distributions have same dimensionality
        # If different, pad or project (for simplicity, assume same size = 8)
        if lora_probs.shape[1] != moe_probs.shape[1]:
            # Pad smaller one with zeros
            max_experts = max(lora_probs.shape[1], moe_probs.shape[1])
            if lora_probs.shape[1] < max_experts:
                padding = torch.zeros(batch_size, max_experts - lora_probs.shape[1], device=lora_probs.device)
                lora_probs = torch.cat([lora_probs, padding], dim=1)
            if moe_probs.shape[1] < max_experts:
                padding = torch.zeros(batch_size, max_experts - moe_probs.shape[1], device=moe_probs.device)
                moe_probs = torch.cat([moe_probs, padding], dim=1)

        # Normalize distributions
        lora_probs = lora_probs / (lora_probs.sum(dim=-1, keepdim=True) + 1e-8)
        moe_probs = moe_probs / (moe_probs.sum(dim=-1, keepdim=True) + 1e-8)

        # Compute KL divergence: KL(lora || moe)
        kl_div = F.kl_div(
            lora_probs.log(),
            moe_probs,
            reduction='none',
            log_target=False
        )  # [B, num_experts]

        # Sum over experts
        kl_per_sample = kl_div.sum(dim=-1)  # [B]

        # Apply task-specific weighting if provided
        if task_weights is not None:
            # Normalize task weights
            task_weights = task_weights / (task_weights.sum() + 1e-8)
            weighted_kl = (kl_per_sample * task_weights).sum()
        else:
            weighted_kl = kl_per_sample.mean()

        return weighted_kl
