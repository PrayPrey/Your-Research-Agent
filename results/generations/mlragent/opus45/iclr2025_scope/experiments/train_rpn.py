"""
Training script for Relevance Predictor Network (RPN).
Trains via distillation from full-cache attention patterns.
"""
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from typing import Dict, Optional, Tuple
import numpy as np
from tqdm import tqdm

from kv_cache import RelevancePredictorNetwork


class RPNTrainer:
    """
    Trainer for Relevance Predictor Network using attention distillation.
    """
    def __init__(
        self,
        rpn: RelevancePredictorNetwork,
        model,  # Base LLM for generating attention targets
        tokenizer,
        learning_rate: float = 1e-4,
        weight_decay: float = 0.01,
        temperature: float = 1.0,
        device: str = 'cuda',
    ):
        self.rpn = rpn.to(device)
        self.model = model
        self.tokenizer = tokenizer
        self.temperature = temperature
        self.device = device

        self.optimizer = optim.AdamW(
            rpn.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
        )

        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=1000,
        )

        self.train_losses = []
        self.val_losses = []

    def compute_target_importance(
        self,
        attention_weights: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        """
        Compute target importance scores from attention weights.

        Args:
            attention_weights: (batch, num_layers, num_heads, seq_len, seq_len)
            attention_mask: (batch, seq_len)

        Returns:
            importance_scores: (batch, seq_len)
        """
        # Average attention across layers and heads
        # attention_weights[i, :, :, j, k] = attention from position j to position k

        # We want importance of position k (how much it's attended to)
        # Sum attention received from all query positions
        attention_received = attention_weights.sum(dim=3)  # (batch, layers, heads, seq_len)
        importance = attention_received.mean(dim=(1, 2))  # (batch, seq_len)

        # Mask invalid positions
        importance = importance.masked_fill(~attention_mask.bool(), float('-inf'))

        return importance

    def train_step(
        self,
        batch: Dict[str, torch.Tensor],
    ) -> float:
        """Single training step."""
        self.rpn.train()
        self.model.eval()

        input_ids = batch['input_ids'].to(self.device)
        attention_mask = batch['attention_mask'].to(self.device)

        # Get attention weights from base model
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_attentions=True,
            )
            attention_weights = torch.stack(outputs.attentions, dim=1)

            # Compute target importance scores
            target_importance = self.compute_target_importance(
                attention_weights, attention_mask
            )

            # Get KV representations from model hidden states
            # Use last hidden state as proxy for KV representations
            hidden_states = outputs.hidden_states[-1] if hasattr(outputs, 'hidden_states') and outputs.hidden_states else None

            if hidden_states is None:
                # Re-run with output_hidden_states=True
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_hidden_states=True,
                )
                hidden_states = outputs.hidden_states[-1]

            # Create KV-like representations
            kv_representations = torch.cat([
                hidden_states,
                hidden_states,  # Simplified: use same hidden state for K and V proxy
            ], dim=-1).float()  # Convert to float32 for RPN

        # Forward through RPN
        predicted_relevance = self.rpn(kv_representations, attention_mask.float())

        # Compute KL divergence loss
        target_probs = F.softmax(target_importance / self.temperature, dim=-1)
        predicted_probs = F.log_softmax(predicted_relevance / self.temperature, dim=-1)

        # Mask for valid positions
        valid_mask = attention_mask.bool()
        target_probs = target_probs.masked_fill(~valid_mask, 0.0)
        predicted_probs = predicted_probs.masked_fill(~valid_mask, 0.0)

        # KL divergence
        loss = F.kl_div(predicted_probs, target_probs, reduction='batchmean')

        # L2 regularization on query prototypes
        l2_reg = 0.001 * torch.norm(self.rpn.query_prototypes, p=2)
        loss = loss + l2_reg

        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.rpn.parameters(), max_norm=1.0)
        self.optimizer.step()
        self.scheduler.step()

        return loss.item()

    def validate(
        self,
        val_loader: DataLoader,
        max_batches: int = 10,
    ) -> float:
        """Validation step."""
        self.rpn.eval()
        self.model.eval()

        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for batch_idx, batch in enumerate(val_loader):
                if batch_idx >= max_batches:
                    break

                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)

                # Get attention weights
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_attentions=True,
                    output_hidden_states=True,
                )
                attention_weights = torch.stack(outputs.attentions, dim=1)
                target_importance = self.compute_target_importance(
                    attention_weights, attention_mask
                )

                hidden_states = outputs.hidden_states[-1]
                kv_representations = torch.cat([hidden_states, hidden_states], dim=-1).float()

                # Forward through RPN
                predicted_relevance = self.rpn(kv_representations, attention_mask.float())

                # Compute loss
                target_probs = F.softmax(target_importance / self.temperature, dim=-1)
                predicted_probs = F.log_softmax(predicted_relevance / self.temperature, dim=-1)

                valid_mask = attention_mask.bool()
                target_probs = target_probs.masked_fill(~valid_mask, 0.0)
                predicted_probs = predicted_probs.masked_fill(~valid_mask, 0.0)

                loss = F.kl_div(predicted_probs, target_probs, reduction='batchmean')
                total_loss += loss.item()
                num_batches += 1

        return total_loss / max(num_batches, 1)

    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        num_epochs: int = 3,
        log_interval: int = 10,
    ) -> Dict[str, list]:
        """Full training loop."""
        best_val_loss = float('inf')

        for epoch in range(num_epochs):
            epoch_losses = []

            pbar = tqdm(train_loader, desc=f'Epoch {epoch + 1}/{num_epochs}')
            for batch_idx, batch in enumerate(pbar):
                loss = self.train_step(batch)
                epoch_losses.append(loss)

                if batch_idx % log_interval == 0:
                    pbar.set_postfix({'loss': f'{loss:.4f}'})

            avg_train_loss = np.mean(epoch_losses)
            self.train_losses.append(avg_train_loss)

            # Validation
            val_loss = self.validate(val_loader)
            self.val_losses.append(val_loss)

            print(f'Epoch {epoch + 1}: Train Loss = {avg_train_loss:.4f}, Val Loss = {val_loss:.4f}')

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                # Save best model
                torch.save(self.rpn.state_dict(), 'best_rpn.pt')

        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
        }


def create_rpn_for_model(model_config, hidden_dim: int = 128) -> RelevancePredictorNetwork:
    """
    Create RPN with appropriate input dimension for the given model.
    """
    # Get model hidden size
    if hasattr(model_config, 'hidden_size'):
        model_hidden_size = model_config.hidden_size
    else:
        model_hidden_size = 2048  # Default for smaller models

    # RPN input is concatenated K and V representations
    input_dim = model_hidden_size * 2

    rpn = RelevancePredictorNetwork(
        input_dim=input_dim,
        hidden_dim=hidden_dim,
        num_layers=2,
        num_query_prototypes=16,
    )

    return rpn
